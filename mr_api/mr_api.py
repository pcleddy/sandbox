import json
import re
import mr_api_logging
import logging
from flask import Flask, jsonify, request
from flask_restful import Resource, Api, abort, reqparse
from ocio_utilities.configuration import configure
from ocio_utilities.device import Device
from ocio_sciencelogic.client import Client as EM7
from ocio_sciencelogic.ocio import get_collector_in_group
from mr_utilities.mr_db import Prediscovery, AutoStart, StartMonitor, mr
from mr_tasks.discovery_tasks import discover


CONF = configure(__file__)
SCIENCELOGIC = CONF['services']['sciencelogic']
# sql alchemy foo
# flask foo
app = Flask(__name__)
# flask-restful foo
api = Api(app)

NAMESERVER = CONF['services']['nameserver']


class PreDiscovery(Resource):

    session = mr()
    device = Device(NAMESERVER)
    ip_regex = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    em7 = EM7(SCIENCELOGIC['user'], SCIENCELOGIC['pass'], SCIENCELOGIC['uri'])
    parser = reqparse.RequestParser()

    def vet(self, collector_ip):

        if not self.ip_regex.match(collector_ip):
            abort(404,
                  message='Invalid collector IP address: %s' % collector_ip)
        params = {'filter.ip': collector_ip,
                  'filter.class_type/description': 'EM7 Data Collector'}
        collector = self.em7.query('device', params=params)
        if not collector:
            abort(404, message='No collector found at IP: %s' % collector_ip)
        collector_group = self.device.group(collector_ip)
        if not collector_group:
            m = 'No network group found for collector IP: %s' % collector_ip
            abort(404, message=m)
        return collector_group

    def get(self):

        if not request.args or 'collector_ip' not in request.args:
            m = '"collector_ip" parameter required in prediscovery GET queries.'
            abort(404, message=m)

        collector_group = self.vet(request.args.get('collector_ip'))
        session = self.session()

        # create any autostart records that need to be created
        additions = self._update_autostart(session)
        for addition in additions:
            # if there should be a failure at this early stage, fail to manual
            if addition.status == 'fail':
                self._fail(addition)

        new = [x for x in session.query(AutoStart).
            filter(AutoStart.status.in_(['new', 'recheck'])).
            filter(AutoStart.network == collector_group).
            with_entities(AutoStart.id, AutoStart.ip)]
        self._change_state([n[0] for n in new], 'prediscovery', session)
        session.commit()
        session.close()
        return jsonify([n.ip for n in new])

    def post(self):

        session = self.session()
        if request.data:

            results = json.loads(request.data.decode('utf-8'))
            for result in results:
                collector_uri = get_collector_in_group(result['ip_address'])
                result['collector_uri'] = collector_uri
            for result in results:
                ip, status, prediscovery = \
                    self._process_prediscovery_result(result, session)
                if status == 'discovery':
                    # pass
                    discover.delay(collector_uri, ip)
                else:
                    self._kickback_prediscovery_failure(prediscovery)
        else:
            abort(404, message='prediscovery result(s) required for POST')
        session.commit()
        session.close()

    def _change_state(self, ids, status, db):

        db.query(AutoStart).\
            filter(AutoStart.id.in_(ids)).\
            update({'status': status}, synchronize_session=False)

    def _process_prediscovery_result(self, result, db):

        ip = result['ip_address']
        status = 'discovery' if result['status'] else 'recheck'

        for k, v in result.items():
            result[k] = True if v == 1 else False if v == 0 \
                else None if v in ('', 2, []) \
                else json.dumps(v) if k == 'log' \
                else v
        if 'collector_uri' in result:
            del result['collector_uri']
        prediscovery = Prediscovery(**result)
        db.add(prediscovery)
        db.commit()  # do we need this commit?
        auto_start = db.query(AutoStart).\
            filter(AutoStart.ip == ip).\
            filter(AutoStart.status == 'prediscovery').with_for_update().one()
        auto_start.status = status
        auto_start.failure_description = prediscovery.log
        auto_start.prediscoveries.append(prediscovery)
        db.commit()
        if status == 'recheck':
            self._kickback_prediscovery_failure(auto_start)
        return ip, status, prediscovery

    def _kickback_prediscovery_failure(self, auto_start):

        pass

    def _update_autostart(self, db):

        device = Device(NAMESERVER)
        autos = [x for x in db.query(AutoStart.startmonitor_id).
            filter(AutoStart.status not in ('success', 'fail'))]
        starts = [x for x in db.query(StartMonitor).
                  filter(StartMonitor.status == 'in progress').
                  filter(StartMonitor.id not in autos).
                  with_entities(StartMonitor.id, StartMonitor.fqdn)]

        additions = []
        for start in starts:
            ip = device.ip(start[1])
            failure_description = None
            status = 'new'

            if not ip:
                failure_description = 'no ip'
                status = 'fail'
            elif len(ip) > 1:
                failure_description = 'multiple ips'
                status = 'fail'
            else:
                ip = ip[0]
                group = device.group(ip)

                if not group:
                    status = 'fail'
                    failure_description = 'unknown group'
            addition = {'startmonitor_id': start[0],
                        'ip': ip,
                        'network': group,
                        'status': status,
                        'failure_description': failure_description}
            additions.append(AutoStart(**addition))

        for addition in additions:
            db.add(addition)
        db.flush()
        db.commit()

        return additions

    def _fail(self, auto, db):

        start = db.query(StartMonitor).filter(
            StartMonitor.id == auto.startmonitor_id
        )



api.add_resource(PreDiscovery, '/prediscovery')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
