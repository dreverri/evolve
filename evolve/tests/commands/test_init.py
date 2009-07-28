import unittest
import os
import shutil
from evolve.commands.init import *
from sqlalchemy import *

class InitFileTests(unittest.TestCase):        
    def setUp(self):
        self.old_path = os.getcwd()
        self.test_path = 'test_init_file'
        os.mkdir(self.test_path)
        os.chdir(self.test_path)
        
    def test_init_file(self):
        init_file()
        self.assertTrue(os.path.exists('evolve.json'))
        self.assertTrue(os.path.exists('changes.json'))
        
    def tearDown(self):
        os.chdir(self.old_path)
        if os.path.exists(self.test_path):
            shutil.rmtree(self.test_path)


class InitDbTests(unittest.TestCase):
    def setUp(self):
        self.valid_target = 'sqlite:///test.db'
        self.invalid_target = 'not a database URL'

    def tearDown(self):
        if os.path.exists('test.db'):
            os.remove('test.db')

    def setup_table(self, dbstring, table_name):
        engine = create_engine(dbstring)
        metadata = MetaData()
        metadata.bind = engine
        table = Table(table_name, metadata)
        return table

    def test_init_db(self):
        target = self.valid_target
        init_db(target)
        self.assertTrue(os.path.exists('test.db'))
        table = self.setup_table(target, '_evolve')
        self.assertTrue(table.exists())

    def test_init_db_bad_target(self):
        target = self.invalid_target
        init_db(target)


if __name__ == '__main__':
    unittest.main()