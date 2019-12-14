"""
Tests for `etd` module.
"""
import pytest
from etd import etd
import os.path


class TestEtd(object):

    @classmethod
    def setup_class(cls):
        cls.test_genome = 'test/data/test_salmonella.fna'
        cls.args = lambda: None
        cls.args.input = cls.test_genome

    def test_check_data(self):
        if os.path.exists(self.test_genome):
            return True
        else:
            return False


    def test_runner(self):
        #etd.run(self.args)
        pass

    @classmethod
    def teardown_class(cls):
        pass
