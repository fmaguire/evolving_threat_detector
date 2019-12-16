"""
Tests for `etd` module.
"""
import pytest
import shutil
from etd import etd
import os.path


class TestEtd(object):

    @classmethod
    def setup_class(cls):
        cls.args = lambda: None
        cls.args.input_genome = 'test/data/test_toy_salmonella.fna'
        cls.args.database_dir = 'test/data/references'
        cls.args.mash_distance = 0.5
        cls.args.num_threads = 1
        cls.args.output_dir = 'run_test'
        cls.args.debug = False
        cls.args.verbose = False

    def test_check_data(self):
        if os.path.exists(self.args.input_genome):
            return True
        else:
            return False


    def test_whole_function(self):
        etd.run(self.args)


    @classmethod
    def teardown_class(cls):
        os.remove('run_test.log')
        shutil.rmtree('run_test')
