import unittest
import json
import os
import time

from hamcrest import *
from worker.script_manager import ScriptFileDB

class TestSpikeWorker(unittest.TestCase):

    def setUp(self):
        self.db = ScriptFileDB()

    def test_file_db(self):
        self.db.add_script_file("1", "scripts/flow.py")
        assert_that(self.db.get_script_file("1"), equal_to("scripts/flow.py"))
        assert_that(self.db.get_script_file("2"), none())

    def test_file_ttl(self):
        self.db.add_script_file("2", "scripts/flow2.py", cache=True,
                ttd=time.time() - 10)
        assert_that(self.db.get_script_file("2"), none())

    def tearDown(self):
        os.remove(self.db.db_file)
