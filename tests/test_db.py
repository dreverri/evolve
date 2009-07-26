import unittest
from evolve.db import Database
import os
from sqlalchemy import *


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database('sqlite:///test_database.db')
        
    def create_table(self):
        Table('table', self.db.metadata, Column('col1', String(40)))
        self.db.metadata.create_all()
        
    def tearDown(self):
        if os.path.exists('test_database.db'):
            os.remove('test_database.db')
        
    def test_table_with_name(self):
        """Test table with just a name. Table does not exist"""
        table = self.db.table('test')
        
    def test_table_with_existing_table(self):
        """Test table with table that exists"""
        self.create_table()
        table = self.db.table('table')
        self.assertEqual(['col1'], table.columns.keys())


if __name__ == '__main__':
    unittest.main()