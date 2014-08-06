__author__ = 'outcastgeek'

import logging
import os
import signal
import sys

from beaker import cache
from beaker.util import coerce_cache_params
from gevent.pool import Pool
from gevent.threadpool import ThreadPool
from zmq import green as zmq

from pyramid.paster import (
    get_appsettings,
    setup_logging
    )

from sqlalchemy import engine_from_config

from pazod.models import (
    DBSession,
    Base,
    )

from pazod.zmq.psycopg2_pool import (
    make_green,
    GreenQueuePool
    )

from pazod.zmq.srvc_handler import (
    handle_msg,
    process_msg
    )

from pazod.zmq.srvc_mappings import scan_for_zmq_services

log = logging.getLogger('pazod')

def detectCPUs():
    """
     Detects the number of CPUs on a system. Cribbed from pp.
     """
    # Linux, Unix and MacOS:
    if hasattr(os, "sysconf"):
        if os.sysconf_names.has_key("SC_NPROCESSORS_ONLN"):
            # Linux & Unix:
            ncpus = os.sysconf("SC_NPROCESSORS_ONLN")
            if isinstance(ncpus, int) and ncpus > 0:
                return ncpus
            else: # OSX:
                return int(os.popen2("sysctl -n hw.ncpu")[1].read())
    # Windows:
    if os.environ.has_key("NUMBER_OF_PROCESSORS"):
       ncpus = int(os.environ["NUMBER_OF_PROCESSORS"]);
       if ncpus > 0:
           return ncpus
    return 1 # Default

def poolSIZE():
    procs = detectCPUs()
    if procs > 0:
        return procs * 2 + 1
    else:
        return 3

# Set the maximum pool size for the request handlers
POOL_SIZE = 40000
TPOOL_SIZE = poolSIZE()

class Server(object):
    def __init__(self, settings):
        self.settings = settings
        self.address = settings.get('services_tcp_address')
        self.work_address = settings.get('workers_tcp_address')
        self.pool = Pool(POOL_SIZE)
        self.tpool = ThreadPool(TPOOL_SIZE)
        self.dead=False

    def stopped(self):
        return self.dead

    def run(self):
        # Scan for Zmq Service Handlers
        scan_for_zmq_services()

        context = zmq.Context()
        frontend = context.socket(zmq.ROUTER)
        frontend.bind(self.address)

        backend = context.socket(zmq.DEALER)
        backend.bind('inproc://backend')

        worker = context.socket(zmq.PULL)
        worker.bind(self.work_address)

        poll = zmq.Poller()
        poll.register(frontend, zmq.POLLIN)
        poll.register(backend, zmq.POLLIN)
        poll.register(worker, zmq.POLLIN)

        while not self.stopped():
            sockets = dict(poll.poll(1000))
            if frontend in sockets:
                if sockets[frontend] == zmq.POLLIN:
                    _id = frontend.recv()
                    msg = frontend.recv()
                    log.debug('Server received message from: %s\n' % _id)
                    self.pool.wait_available()
                    self.pool.spawn(handle_msg, context, _id, msg, **self.settings)

            if backend in sockets:
                if sockets[backend] == zmq.POLLIN:
                    _id = backend.recv()
                    msg = backend.recv()
                    log.debug('Server sending to frontend: %s\n' % _id)
                    frontend.send(_id, zmq.SNDMORE)
                    frontend.send(msg)

            if worker in sockets:
                if sockets[worker] == zmq.POLLIN:
                    msg = worker.recv()
                    log.debug('Dispatching work')
                    self.tpool.spawn(process_msg, msg, **self.settings)
                    # self.pool.wait_available()
                    # log.debug('Dispatching work')
                    # self.pool.spawn(process_msg, msg, **self.settings)

        frontend.close()
        backend.close()
        worker.close()
        context.term()

        # signal handler
    def sig_handler(self, sig, frame):
        log.warning("Caught Signal: %s", sig)
        self.pool.kill()
        self.dead=True

def configure_database(settings):
    engine = engine_from_config(settings, 'sqlalchemy.', echo_pool=True, poolclass=GreenQueuePool, pool_size=40000, max_overflow=0)
    # make_green(engine) # Make the system green!!!!

    DBSession.configure(bind=engine)
    Base.metadata.bind = engine


# Got it from here: https://github.com/Pylons/pyramid_beaker/blob/master/pyramid_beaker/__init__.py
def set_cache_regions_from_settings(settings):
    """
    The ``settings`` passed to the configurator are used to setup
    the cache options. Cache options in the settings should start
    with either 'beaker.cache.' or 'cache.'.
    """
    cache_settings = {'regions':None}
    for key in settings.keys():
        for prefix in ['beaker.cache.', 'cache.']:
            if key.startswith(prefix):
                name = key.split(prefix)[1].strip()
                cache_settings[name] = settings[key].strip()
    coerce_cache_params(cache_settings)

    if 'enabled' not in cache_settings:
        cache_settings['enabled'] = True

    regions = cache_settings['regions']
    if regions:
        for region in regions:
            if not region: continue
            region_settings = {
                'data_dir': cache_settings.get('data_dir'),
                'lock_dir': cache_settings.get('lock_dir'),
                'expire': cache_settings.get('expire', 60),
                'enabled': cache_settings['enabled'],
                'key_length': cache_settings.get('key_length', 250),
                'type': cache_settings.get('type'),
                'url': cache_settings.get('url'),
                }
            region_prefix = '%s.' % region
            region_len = len(region_prefix)
            for key in list(cache_settings.keys()):
                if key.startswith(region_prefix):
                    region_settings[key[region_len:]] = cache_settings.pop(key)
            coerce_cache_params(region_settings)
            cache.cache_regions[region] = region_settings


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    print "Config location: %s" % config_uri
    settings = get_appsettings(config_uri)

    configure_database(settings)

    set_cache_regions_from_settings(settings)

    # logging.config.dictConfig(settings) # TODO: Figure this out!!!!

    # Start the server that will handle incoming requests
    server = Server(settings)
    # signal register
    signal.signal(signal.SIGINT, server.sig_handler)
    signal.signal(signal.SIGTERM, server.sig_handler)
    server.run()

if __name__ == "__main__":
    main()

