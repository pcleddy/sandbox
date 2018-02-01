from time import strftime, localtime, sleep
from ocio_sciencelogic.client import Client
from ocio_utilities.configuration import configure
from mr_utilities.mr_db import StartMonitor, construct, deconstruct, mr, User, \
    populate_local


CONF = configure(__file__)
NAMESERVER = CONF['services']['nameserver']
sciencelogic = CONF['services']['sciencelogic']
EM7 = Client(sciencelogic['user'], sciencelogic['pass'], sciencelogic['uri'])
DB = mr()
TEST_IPS = ('137.78.110.99', '128.149.122.16')
TEST_SESSIONS = ['128.149.122.16 (auto)', 'MR-PR1 (128.149.122.16)']


def insert():

    cr = strftime('%Y-%m-%d %H:%M', localtime())
    db = DB()
    user = User(username='sabaker', type='LDAP')
    db.add(user)
    db.commit()
    inserts = []
    for fqdn in ('jplis-sa-wfe.jpl.nasa.gov', '137.78.110.99'):
        i = {'fqdn': fqdn,
             'status': 'in progress',
             'userID': user.id,
             'osID': 3,
             'createTime': cr,
             'org': 'OCIO-SA'}
        inserts.append(StartMonitor(**i))
    if inserts:
        db.bulk_save_objects(inserts)
        db.commit()
        db.close()


def setup():

    deconstruct()
    construct()
    populate_local()
    insert()
    EM7.cleanup_discovery_sessions(TEST_SESSIONS)


def teardown():

    """if testing celery route comment 'pass' and uncomment everything else
    this will teardown the db and cleanup the em7 test sessions and if the
    sleep statement is removed all of that stuff will happen while the celery
    task is running and it will die a miserable death"""

    # pass
    sleep(60)   # let mr_tasks do it's thing
    deconstruct()   # destroy test db
    # wipeout EM7 test sessions and devices
    EM7.cleanup_discovery_sessions(TEST_SESSIONS)
