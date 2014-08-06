__author__ = 'outcastgeek'

import collections
import functools
import logging
import umsgpack

from zmq import green as zmq

log = logging.getLogger('pazod')

# Got it from here: https://wiki.python.org/moin/PythonDecoratorLibrary
class memoized(object):
    '''Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    '''
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value
    def __repr__(self):
        '''Return the function's docstring.'''
        return self.func.__doc__
    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return functools.partial(self.__call__, obj)


@memoized
def setup_ask_socket(address, identity):
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    socket.setsockopt(zmq.IDENTITY, identity)
    socket.connect(address)
    return context, socket


def srvc_ask(identity, address, message):
    identity = '{}{}'.format('id_', identity)
    address = address
    pack_msg = umsgpack.packb(message)
    context, socket = setup_ask_socket(address, identity)
    log.debug('Client %s started\n' % identity)
    poll = zmq.Poller()
    poll.register(socket, zmq.POLLIN)

    socket.send(pack_msg)
    log.debug('Req from client %s sent.\n' % identity)

    response = None
    received_reply = False
    while not received_reply:
        sockets = dict(poll.poll(1000))
        if socket in sockets:
            if sockets[socket] == zmq.POLLIN:
                response = socket.recv()
                log.debug('Client %s received reply: %s\n' % (identity, response))
                received_reply = True

    socket.close()
    context.term()
    return response


@memoized
def setup_tell_socket(address):
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect(address)
    return socket

def srvc_tell(address, message):
    address = address
    pack_msg = umsgpack.packb(message)
    # context = zmq.Context()
    # socket = context.socket(zmq.PUSH)
    # socket.connect(address)
    socket = setup_tell_socket(address)
    socket.send(pack_msg)




