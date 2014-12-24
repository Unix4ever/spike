import unittest
import json

import SimpleHTTPServer
import SocketServer

from flexmock import flexmock
from hamcrest import *
from worker import config
from worker.spike_worker import SpikeWorker
from worker.executors.factory import ExecutorFactory
from worker.executors import ExecutorPrepareError

class TestSpikeWorker(unittest.TestCase):

    PORT = 12039

    def setUp(self):
        flexmock(config) \
                .should_call("get")

        flexmock(config) \
                .should_receive("get") \
                .with_args("script.folder", "scripts") \
                .and_return("./test/resources/scripts")

        self.instance = SpikeWorker(ExecutorFactory())

    def tearDown(self):
        self.instance.clean_cache()        

    def test_non_existing_script(self):
        """
        Test non existing script execution attempt
        Should receive an exception
        """
        message = \
        {
                "scenario": 
                {
                    "id": "not_existing",
                    "type": "python"
                },
                "id": 1
        }
        try:
            self.instance.process(message)
        except ExecutorPrepareError:
            pass
        else:
            self.fail("No exception for non-existing script execution attempt")

    def test_local_file_flow(self):
        """
        Test local file retrival
        """
        message = \
        {
                "scenario": 
                {
                    "id": "test_local_script",
                    "type": "python"
                },
                "id": 1
        }
        res = self.instance.process(message)
        assert_that(res, not_none())
        assert_that(res.get("result"), equal_to("success"))

"""
    def test_remote_file_flow(self):
        Download file and run
        flexmock(self.instance.executor_factory.script_manager) \
                .should_receive("master_host") \
                .and_return("http://localhost:%s" % TestSpikeWorker.PORT)

        message = \
        {
                "scenario": 
                {
                    "id": "remote",
                    "type": "python"
                },
                "id": 1
        }

        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(("", TestSpikeWorker.PORT), Handler)
        httpd.handle_request()
        
        self.instance.process(message)
"""
