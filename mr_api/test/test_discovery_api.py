import os
import json
import unittest
import requests
from uuid import uuid4
from time import sleep
from ocio_utilities.configuration import configure
from ocio_sciencelogic.client import Client
from nose.tools import assert_in, assert_equal, assert_is_none, nottest, \
    assert_is_instance
from mr_utilities.mr_db import AutoStart, Prediscovery, mr

from datetime import datetime

from pprint import pprint

CONF = configure(__file__)
EM7 = CONF['services']['sciencelogic']
CAN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'canonicals')
URL = 'http://127.0.0.1:5000'

# TODO: Add tests for POSTing bad prediscovery results.


@nottest
def get_json_canonical(name):

    canonical_file = os.path.join(CAN, '%s.json' % name)
    return json.loads(open(canonical_file).read())


class TestMrApi(unittest.TestCase):

    prediscovery = '%s/prediscovery' % URL
    em7 = Client(EM7['user'], EM7['pass'], EM7['uri'])
    db = mr()


    def test_001_GET_prediscovery(self):

        params = {'collector_ip': '128.149.3.169'}
        res = requests.get(self.prediscovery, params=params)
        assert_equal(res.status_code, 200)
        res = res.json()
        assert_equal(len(res), 2)
        assert_in('137.78.110.99', res)
        assert_in('128.149.122.16', res)
        db = self.db()
        autos = [x for x in db.query(AutoStart).all()]
        assert_equal(len(autos), 2)

        zero = autos[0]
        assert_equal(zero.device, None)
        assert_equal(zero.failure_description, None)
        assert_equal(zero.id, 1)
        assert_equal(zero.ip, '128.149.122.16')
        assert_equal(zero.network, 'JPL')
        assert_equal(zero.session, None)
        assert_equal(zero.startmonitor_id, 1)
        assert_equal(zero.status, 'prediscovery')

        one = autos[1]
        assert_equal(one.device, None)
        assert_equal(one.failure_description, None)
        assert_equal(one.id, 2)
        assert_equal(one.ip, '137.78.110.99')
        assert_equal(one.network, 'JPL')
        assert_equal(one.session, None)
        assert_equal(one.startmonitor_id, 2)

        db.close()


    def test_002_GET_prediscovery_bad_collector_ip(self):

        ip = str(uuid4())
        res = requests.get(self.prediscovery, params={'collector_ip': ip})
        assert_equal(res.status_code, 404)
        j = res.json()
        assert_in('message', j)
        assert_in('Invalid collector IP address: %s' % ip, j['message'])

    def test_003_GET_prediscovery_unknown_collector_ip(self):

        params = {'collector_ip': '123.45.678.90'}
        res = requests.get(self.prediscovery, params=params)
        assert_equal(res.status_code, 404)
        j = res.json()
        assert_in('message', j)
        assert_in('No collector found at IP: 123.45.678.90', j['message'])

    def test_004_POST_prediscovery(self):

        """
        # !!! For testing make sure that the discover() method is commented out
        # in post to prediscovery in mr_api !!!
        """

        prediscovery_canonicals = get_json_canonical(
            'test_004_POST_prediscovery_prediscovery'
        )
        assert_equal(len(prediscovery_canonicals), 2)
        res = requests.post(self.prediscovery,
                            data=json.dumps(prediscovery_canonicals))
        assert_equal(res.status_code, 200)
        sleep(1)

        db = self.db()
        prediscoveries = db.query(Prediscovery).all()
        for i in range(len(prediscovery_canonicals)):
            prediscovery_canonical = prediscovery_canonicals[i]
            prediscovery = prediscoveries[i].__dict__
            for column in prediscovery_canonical:
                if column == 'log':
                    if not prediscovery_canonical[column]:
                        assert_is_none(prediscovery[column])
                elif prediscovery_canonical[column] == '':
                    assert_is_none(prediscovery[column])
                else:
                    assert_equal(prediscovery_canonical[column],
                                 prediscovery[column])
        db.close()
        sleep(60)
        db = self.db()
        autos = [x for x in db.query(AutoStart).all()]
        assert_equal(len(autos), 2)

        zero = autos[0]
        assert_is_instance(zero.created, datetime)
        assert_is_instance(zero.device, int)
        assert_equal(zero.failure_description, None)
        assert_equal(zero.id, 1)
        assert_equal(zero.ip, '128.149.122.16')
        assert_equal(zero.network, 'JPL')
        assert_is_instance(zero.session, int)
        assert_equal(zero.startmonitor_id, 1)
        assert_equal(zero.status, 'success')
        assert_is_instance(zero.updated, datetime)

        one = autos[1]
        assert_is_instance(one.created, datetime)
        assert_equal(one.device, None)
        assert_equal(one.failure_description,
                     '["MM Watch - unknown error", "CPU Load error"]')
        assert_equal(one.id, 2)
        assert_equal(one.ip, '137.78.110.99')
        assert_equal(one.network, 'JPL')
        assert_equal(one.session, None)
        assert_equal(one.startmonitor_id, 2)
        assert_equal(one.status, 'recheck')
        assert_is_instance(one.updated, datetime)

        db.close()
