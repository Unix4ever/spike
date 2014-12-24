import os
import sys
import logging
import json
import pika
import threading
import argparse

from Queue import Queue

os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
sys.path.append("./")

import config

from worker.spike_worker import SpikeWorker
from worker.executors.factory import ExecutorFactory

class Spike(object):

    def __init__(self):
        self.workers_count = config.getint("main.workers_count", 1)
        self.amqp_address = config.get("main.amqp_server")

        self.input_queue = config.get("main.input_queue", "spikeTasks")
        self.output_queue = config.get("main.output_queue")

        self.running = True
        self.threads = []
        self.worker = SpikeWorker(ExecutorFactory())

    def run(self):
        if not self.amqp_address:
            raise Exception("Failed to run Spike, amqp host not set")

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=str(self.amqp_address)))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.input_queue)
        self.channel.basic_qos(prefetch_count=self.workers_count)

        local_queue = Queue()

        if self.output_queue:
            self.channel.queue_declare(queue=self.output_queue)

        stop_event = threading.Event()

        def process(queue):
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
            t = threading.Thread(target=process, args=(local_queue,))
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
    parser = argparse.ArgumentParser(description="Replicate data from one dc to another")
    parser.add_argument("-config", "--config", dest="config", help="Configuration file")
    options = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    files = []
    if options.config:
        files.append(options.config)
                
    config.read_config(*files)

    spike = Spike()
    spike.run()
