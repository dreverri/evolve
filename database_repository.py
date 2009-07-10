"""Useful link for setting up MySQLdb on OS X:
http://trentm.com/blog/archives/2009/05/26/mysql-python-on-mac-os-x/
"""

import unittest
from sqlalchemy import *
import os
import os.path

class RepositoryAlreadyExists(Exception):
    pass
    
    
class DatabaseRepository:
    def initialize(self, dbstring):
        engine = create_engine(dbstring)
        metadata = MetaData()
        metadata.bind = engine
        table = Table('_evolve', metadata,
            Column('type', Unicode(40)),
            Column('key', Unicode(40)),
            Column('value', UnicodeText())
        )
        if table.exists():
            raise RepositoryAlreadyExists()
        else:
            table.create()
    
    
class TestDatabaseRepository(unittest.TestCase):
    def setUp(self):
        self.dbstring = 'sqlite:///test.db'
        
    def tearDown(self):
        if os.path.exists('test.db'):
            os.remove('test.db')
        
    def test_initialize_database(self):
        """The table _evolve should be created"""
        dbstring = self.dbstring
        repository = DatabaseRepository()
        repository.initialize(dbstring)
        
    def test_already_initialized_database_failure(self):
        """raise RepositoryAlreadyExists"""
        dbstring = self.dbstring
        repository = DatabaseRepository()
        repository.initialize(dbstring)
        self.assertRaises(RepositoryAlreadyExists, 
            getattr(repository, 'initialize'), dbstring)
        
    
if __name__ == '__main__':
    unittest.main()