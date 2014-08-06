from __future__ import with_statement

__author__ = 'outcastgeek'

import contextlib
import logging
import sys

from gevent.coros import Semaphore
from gevent.socket import wait_read, wait_write

from psycopg2 import extensions, OperationalError, connect

from sqlalchemy.pool import QueuePool

log = logging.getLogger('pazod')

def gevent_wait_callback(conn, timeout=None):
    """A wait callback useful to allow gevent to work with Psycopg."""
    while 1:
        state = conn.poll()
        if state == extensions.POLL_OK:
            break
        elif state == extensions.POLL_READ:
            wait_read(conn.fileno(), timeout=timeout)
        elif state == extensions.POLL_WRITE:
            wait_write(conn.fileno(), timeout=timeout)
        else:
            raise OperationalError(
                "Bad result from poll: %r" % state)


def make_green(engine):
    """
    Set up psycopg2 & SQLAlchemy to be greenlet-friendly.
    Note: psycogreen does not really monkey patch psycopg2 in the
    manner that gevent monkey patches socket.
    """
    log.warn('Making the system green...')

    extensions.set_wait_callback(gevent_wait_callback)

    # Assuming that gevent monkey patched the builtin
    # threading library, we're likely good to use
    # SQLAlchemy's QueuePool, which is the default
    # pool class.  However, we need to make it use
    # threadlocal connections
    #
    #
    engine.pool._use_threadlocal = True


class GreenQueuePool(QueuePool):

    def __init__(self, *args, **kwargs):
        super(GreenQueuePool, self).__init__(*args, **kwargs)
        if self._overflow_lock is not None:
            self._overflow_lock = Semaphore()





