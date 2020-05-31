import re
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.backends import utils as backend_utils

try:
    import MySQLdb as Database
    import sqlalchemy.pool as pool
    from sqlalchemy.pool import QueuePool
    from sqlalchemy.exc import TimeoutError
    import types
except ImportError as err:
    raise ImproperlyConfigured(
        'Error loading MySQLdb module.\n'
        'Did you install mysqlclient and SQLAlchemy?'
    ) from err

from MySQLdb.constants import CLIENT, FIELD_TYPE  # isort:skip
from MySQLdb.converters import conversions

# Some of these import MySQLdb, so import them after checking if it's installed.
from django.db.backends.mysql.client import DatabaseClient  # isort:skip
from django.db.backends.mysql.creation import DatabaseCreation  # isort:skip
from django.db.backends.mysql.features import DatabaseFeatures  # isort:skip
from django.db.backends.mysql.introspection import DatabaseIntrospection  # isort:skip
from django.db.backends.mysql.operations import DatabaseOperations  # isort:skip
from django.db.backends.mysql.schema import DatabaseSchemaEditor  # isort:skip
from django.db.backends.mysql.validation import DatabaseValidation  # isort:skip

version = Database.version_info
if version < (1, 3, 3):
    raise ImproperlyConfigured("mysqlclient 1.3.3 or newer is required; you have %s" % Database.__version__)

# MySQLdb returns TIME columns as timedelta -- they are more like timedelta in
# terms of actual behavior as they are signed and include days -- and Django
# expects time.
django_conversions = conversions.copy()
django_conversions.update({
    FIELD_TYPE.TIME: backend_utils.typecast_time,
})

# This should match the numerical portion of the version numbers (we can treat
# versions like 5.0.24 and 5.0.24a as the same).
server_version_re = re.compile(r'(\d{1,2})\.(\d{1,2})\.(\d{1,2})')

from django.db.backends.mysql.base import CursorWrapper
from django.db.backends.mysql.base import DatabaseWrapper as _DatabaseWrapper

server_pools = {}


class MySQLConnections:
    def __init__(self, conn_params, conn_settings):
        options = conn_settings.get('OPTIONS') or {}
        self.host = conn_settings['HOST']
        self.port = int(conn_settings['PORT'])
        self.user = conn_settings['USER']
        self.db = conn_settings['NAME']
        self.passwd = conn_settings['PASSWORD']
        self.use_unicode = True,
        self.charset = options.get('charset') or 'utf8mb4'
        self.client_flag = conn_params['client_flag']
        self.sql_mode = options.get('sql_mode') or 'STRICT_TRANS_TABLES'

    def get_conn(self):
        return Database.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            db=self.db,
            passwd=self.passwd,
            use_unicode=True,
            charset=self.charset,
            client_flag=self.client_flag,
            sql_mode=self.sql_mode,
        )


class DatabaseWrapper(_DatabaseWrapper):

    def get_new_connection(self, conn_params):
        # return a mysql connection
        alias = self._get_alias_by_params(conn_params)
        conn_settings = settings.DATABASES[alias]
        if not hasattr(server_pools, alias):
            server_pools[alias] = self._get_connection_pool(conn_params=conn_params, conn_settings=conn_settings)
        return server_pools[alias].connect()

    def _get_alias_by_params(self, conn_params):
        target_str = ''.join([str(conn_params[_]) for _ in ['host', 'port', 'db', 'user', 'passwd']])
        for k, v in settings.DATABASES.items():
            _str = ''.join([str(v[_]) for _ in ['HOST', 'PORT', 'NAME', 'USER', 'PASSWORD']])
            if _str == target_str:
                return k
        return 'default'

    def _get_connection_pool(self, conn_params, conn_settings):
        queue_pool = conn_settings['QUEUE_POOL']
        pool_size = queue_pool['pool_size']
        max_overflow = queue_pool['max_overflow']
        timeout = queue_pool['timeout']
        recycle = queue_pool['recycle']
        mysql_connections = MySQLConnections(conn_params=conn_params, conn_settings=conn_settings)
        return pool.QueuePool(mysql_connections.get_conn, pool_size=pool_size,
                              max_overflow=max_overflow, timeout=timeout,
                              recycle=recycle)
