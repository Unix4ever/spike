import unittest
import json

from hamcrest import *
from worker import config

class TestConfig(unittest.TestCase):

    def test_multiple_files(self):
        """
        Test how several config files are merged in one
        """
        res = config.read_config("test/resources/*.json")

        def expect(field, condition):
            assert_that(config.get(field), condition)

        expect("folder.tmp", equal_to("/tmp2"))
        expect("folder.subdirs.dir2", equal_to("<_<"))
        expect("folder.subdirs.dir1", equal_to("/o_o"))
        expect("new_one", equal_to("three"))

        assert_that(config.get("not_existing", "default"), equal_to("default"))
        
