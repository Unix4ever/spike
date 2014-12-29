import os
import sys
import logging
import json
import pika
import threading
import argparse

from pika import credentials as pika_credentials

from logging import handlers

from Queue import Queue

path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(path, '..')))

from common import config

from worker.executors import ExecutorPrepareError
from worker.spike_worker import SpikeWorker
from worker.spike_worker import ProcessingError
from worker.executors.factory import ExecutorFactory

class Spike(object):

    def __init__(self):
        self.workers_count = config.getint("main.workers_count", 1)
        self.amqp_address = config.get("main.amqp_server")
        self.amqp_user = config.get("main.amqp_user", "guest")
        self.amqp_pass = config.get("main.amqp_pass", "guest")

        self.input_queue = config.get("main.input_queue", "spikeTasks")
        self.output_queue = config.get("main.output_queue")

        self.running = True
        self.threads = []
        self.worker = SpikeWorker(ExecutorFactory())

    def run(self):
        if not self.amqp_address:
            raise Exception("Failed to run Spike, amqp host not set")

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=str(self.amqp_address),
            socket_timeout=10,
            credentials=pika_credentials.PlainCredentials(self.amqp_user, self.amqp_pass)))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.input_queue)
        self.channel.basic_qos(prefetch_count=self.workers_count * 5)

        local_queue = Queue()

        if self.output_queue:
            self.channel.queue_declare(queue=self.output_queue)

        stop_event = threading.Event()

        def process(queue, cfg):
            config.config = cfg
            while not stop_event.is_set():
                task = queue.get()
                if not task:
                    break

                task, callback = task

                logging.info("Starting process message %r" % task)
                self.worker.process(task)
                callback()
                queue.task_done()
                logging.info("Finished processing message %r" % task)

        for i in xrange(self.workers_count):
            t = threading.Thread(target=process, args=(local_queue,
                config.config))
            t.daemon = True
            self.threads.append(t)
            t.start()

        def on_message(channel, method_frame, header_frame, body):
            try:
                message = json.loads(body)
            except ValueError:
                logging.exception("Failed to process amqp message %r", message)
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                return

            logging.info("Got AMQP message %s", body)
            try:
                local_queue.put((self.worker.create_task(message), lambda: channel.basic_ack(delivery_tag=method_frame.delivery_tag)))
            except ProcessingError:
                logging.exception("Failed to process amqp message %r", message)
            except ExecutorPrepareError:
                logging.exception("Failed to process task %r", message)
            except Exception:
                logging.exception("Unhandler error")
                raise

        self.channel.basic_consume(on_message, self.input_queue)
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            stop_event.set()

            logging.info("Waiting for all threads to stop")

            for _ in self.threads:
                local_queue.put(None)

            for t in self.threads:
                t.join(timeout=20)
        self.connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spike load test utility")
    parser.add_argument("-c", "--config", dest="config", help="Configuration file")
    parser.add_argument("-l", "--logfile", dest="log_file", help="Log file")
    parser.add_argument("-p", "--pidfile", dest="pid_file", help="Pid file")
    options = parser.parse_args()
    pid = str(os.getpid())

    if options.pid_file:
        if os.path.isfile(options.pid_file):
            logging.error("%s already exists, exiting" % options.pid_file)
            sys.exit()
        else:
            file(options.pid_file, 'w').write(pid)
    
    files = []
    if options.config:
        files.append(options.config)

    if options.log_file:
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s][%(process)d] %(message)s')
        log_file = handlers.RotatingFileHandler(options.log_file)
        log_file.setLevel(logging.INFO)
        log_file.setFormatter(formatter)
        root.addHandler(log_file)
    else:
        logging.basicConfig(level=logging.INFO)
                
    config.read_config(*files)

    try:
        spike = Spike()
        spike.run()
    finally:
        if options.pid_file and os.path.isfile(options.pid_file):
            os.unlink(options.pid_file)
