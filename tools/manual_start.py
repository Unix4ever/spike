import argparse
import pika
import uuid
import json
import os
import sys

from pika import credentials as pika_credentials

path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(path, '..')))
from worker import config

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Add tasks to queue manually")
    parser.add_argument("-amqp", "--amqp-server", dest="amqp_server", help="AMQP server address to publish to")
    parser.add_argument("-s", "--scenario", dest="scenario", help="Scenario to run")
    parser.add_argument("-c", "--count", dest="count", help="Task count", default=1)
    parser.add_argument("-d", "--drain", dest="drain", action="store_true", help="Drain all previous messages")
    config.read_config()

    opts = parser.parse_args()

    amqp_server = opts.amqp_server if opts.amqp_server else config.get("main.amqp_server")
    amqp_user = config.get("main.amqp_user", "guest")
    amqp_pass = config.get("main.amqp_pass", "guest")
    queue = config.get("main.input_queue", "spikeTasks")
    if not amqp_server:
        print "FATAL: amqp server is not defined"
        exit(1)


    connection = pika.BlockingConnection(pika.ConnectionParameters(host=str(amqp_server),
            credentials=pika_credentials.PlainCredentials(amqp_user, amqp_pass)))
    channel = connection.channel()
    count = 0
    if opts.drain:
        print "Draining all messages from queue"
        message = True
        while message:
            method, _, message = channel.basic_get(queue)
            channel.basic_ack(method.delivery_tag)
            count += 1
            sys.stdout.write("Got %s messages\r" % count)
            sys.stdout.flush()

    if not opts.scenario:
        print "FATAL: scenario is not defined"
        exit(2)

    print "Going to publish %s tasks to launch %s scenario" % (opts.count, opts.scenario)
    for i in xrange(int(opts.count)):
        msg = {"scenario": {"id": opts.scenario, "type": "python"}, "id": uuid.uuid4().hex}
        channel.basic_publish(exchange='', routing_key=queue, body=json.dumps(msg))
