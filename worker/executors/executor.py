import logging
import time

try:
    from statsd import statsd
    statsd_installed = True
except:
    statsd_installed = False

from worker import executors
from common import config

log = logging.getLogger(__name__)


def bind(t):
    def f(cls):
        executors.bindings[t] = cls
        return cls

    return f


class Executor(object):

    def __init__(self):
        self.script_file = None
        self.stats_connected = False
        self.host = config.get("stats.host", "localhost")
        self.port = config.get("stats.port", 8125)

    def prepare(self, script_file):
        self.script_file = script_file

    def run(self, task):
        if not self.script_file:
            log.error("Failed to run executor, script is not set")
            return

        start = time.time()
        res = self.execute(task)
        elapsed = time.time() - start
        self.report("gauge", elapsed, scenario=task.scenario_id)
        return res

    def execute(self, task):
        raise NotImplementedError()

    def report(self, metric_type, value, **kwargs):
        if not statsd_installed:
            return

        if not self.stats_connected:
            statsd.connect(self.host, self.port)
            self.stats_connected = True
        key = "spike.test"
        tags = ["%s:%s" % (k, v) for k, v in kwargs.iteritems()]
        if "postfix" in kwargs:
            key = ".".join([key, kwargs["postfix"]])
            del kwargs["postfix"]

        if metric_type == "counter":
            statsd.increment(key, value, tags=tags)
        elif metric_type == "gauge":
            statsd.gauge(key, value, tags=tags)
