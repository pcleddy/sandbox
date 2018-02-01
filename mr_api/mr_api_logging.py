import os
import logging
from logging.handlers import TimedRotatingFileHandler

mr_log = 'mr_api.log'
sqlalchemy_log = 'sqlalchemy.log'
werkzeug_log = 'werkzeug.log'

directory = os.path.dirname(os.path.abspath(__file__))
level = logging.DEBUG
log_path = os.path.join(directory, mr_log)

format_str = '%(asctime)s %(levelname)s %(module)s: %(message)s'
formatter = logging.Formatter(format_str)

# mr_api logging
logger = logging.getLogger('mr_api')
logger.setLevel(level)
kwargs = {'when': 'W0', 'backupCount': 12}
handler = TimedRotatingFileHandler(filename=log_path, **kwargs)
handler.setFormatter(formatter)
logger.addHandler(handler)

# sqlalchemy logging
sqlalchemy_path = os.path.join(directory, sqlalchemy_log)
sqlalchemy_logger = logging.getLogger('sqlalchemy')
sqlalchemy_logger.setLevel(level)
sqlalchemy_handler = TimedRotatingFileHandler(filename=sqlalchemy_path,
                                              **kwargs)
sqlalchemy_handler.setFormatter(formatter)
sqlalchemy_logger.addHandler(sqlalchemy_handler)

# werkzeug (development server) logging
werkzeug_path = os.path.join(directory, werkzeug_log)
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(level)
werkzeug_handler = TimedRotatingFileHandler(filename=werkzeug_path, **kwargs)
werkzeug_handler.setFormatter(formatter)
werkzeug_logger.addHandler(werkzeug_handler)
