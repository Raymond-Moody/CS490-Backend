from django.test.runner import DiscoverRunner
from django import db

class SakilaTestRunner(DiscoverRunner):
    #use live mysql test database instead of creating one because creating one didn't work
    def setup_databases(self, **kwargs):
        connection = db.connections['default']
        db_conf = connection.settings_dict
        db_conf['NAME'] = db_conf['TEST']['NAME']
        connection.connect()

    def teardown_databases(self, old_config, **kwargs):
        pass
