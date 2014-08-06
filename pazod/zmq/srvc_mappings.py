__author__ = 'outcastgeek'

import pazod
import venusian

RECREATE_INDEX = 'recreate_index'
INDEX_ONE = 'index_one'
REINDEX_ONE = 'reindex_one'
BULK_INDEX_NEW = 'bulk_index_new'
INDEX_ALL = 'index_all'
GEN_TEST_DATA = 'gen_test_data'
GEN_TEST_DATA_TASK = 'gen_test_data_task'
DROP_TEST_DATA = 'drop_test_data'
DROP_TEST_DATA_TASK = 'drop_test_data_task'

SRVC_MAP = {}

class zmq_service(object):
    def __init__(self, **settings):
        self.__dict__.update(settings)

    def __call__(self, wrapped):
        settings = self.__dict__.copy()

        def callback(context, name, ob):

            srvc_name = settings.get('srvc_name')
            SRVC_MAP.update({srvc_name:ob})

        venusian.attach(wrapped, callback, category='zmq_services')
        return wrapped

class Registry(object):
    def __init__(self):
        self.registered = []

    def add(self, name, ob):
        self.registered.append((name, ob))

registry = Registry()

def scan_for_zmq_services():
    scanner = venusian.Scanner(registry=registry)
    scanner.scan(pazod, categories=('zmq_services',))

