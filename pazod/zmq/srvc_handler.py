__author__ = 'outcastgeek'

import logging
import sys
import umsgpack

from zmq import green as zmq

from ..zmq.srvc_mappings import SRVC_MAP

log = logging.getLogger('oasysusa')

def resolve_handler(msg):
    srvc_name = msg.get('srvc')
    log.debug('Resolved Service: %s', srvc_name)
    return SRVC_MAP.get(srvc_name)

def process_msg(raw_msg, **kwargs):
    msg = umsgpack.unpackb(raw_msg)
    srvc_func = resolve_handler(msg)
    return srvc_func(msg, kwargs)


def handle_msg(context, _id, raw_msg, **kwargs):
    """
    RequestHandler
    :param context: ZeroMQ context
    :param id: Requires the identity frame to include in the reply so that it will be properly routed
    :param msg: Message payload for the worker to process
    """
    # Worker will process the task and then send the reply back to the DEALER backend socket via inproc
    response = None
    try:
        worker = context.socket(zmq.DEALER)
        worker.connect('inproc://backend')
        response = process_msg(raw_msg, **kwargs)
    except:
        e = sys.exc_info()[0]
        log.error("Error: %s" % e)
        response = "Error"

    worker.send(_id, zmq.SNDMORE)
    worker.send(response)

    del raw_msg

    log.debug('Request handler quitting.\n')
    worker.close()



