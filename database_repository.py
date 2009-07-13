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
    def __init__(self, dbstring):
        self.dbstring = dbstring
        self.engine = create_engine(dbstring)
        self.metadata = MetaData(self.engine)
        
    def initialize(self):
        metadata = self.metadata
        table = Table('_evolve', metadata,
            Column('type', Unicode(40)),
            Column('key', Unicode(40)),
            Column('value', UnicodeText()),
            useexisting = True
        )
        if table.exists():
            raise RepositoryAlreadyExists()
        else:
            table.create()
    
    def deploy(self, change):
        if change["change"] == "create":
            self.deploy_create(change["schema"])
            
    def deploy_create(self, schema):
        metadata = self.metadata
        table_name = schema["id"]
        table = Table(table_name, metadata)
        for name, prop in schema["properties"].items():
            column = self.get_column(name, prop)
            table.append_column(column)
        table.create()
            
    def get_column(self, name, prop):
        type_ = self.get_column_type(prop)
        column = Column(name, type_)
        return column
        
    def get_column_type(self, prop):
        if "type" in prop and prop["type"] == "string":
            if "format" in prop and prop["format"] == "date":
                pass
            else:
                if "maxLength" in prop and prop["maxLength"]:
                    return Unicode(length = prop["maxLength"])
                else:
                    return UnicodeText()
        
            
    
class TestDatabaseRepository(unittest.TestCase):
    def setUp(self):
        self.dbstring = 'sqlite:///test.db'
        
    def tearDown(self):
        if os.path.exists('test.db'):
            os.remove('test.db')
            
    def setup_table(self, dbstring, table_name):
        engine = create_engine(dbstring)
        metadata = MetaData()
        metadata.bind = engine
        table = Table(table_name, metadata)
        return table
            
    def assertTableExists(self, dbstring, table_name):
        table = self.setup_table(dbstring, table_name)
        self.assertTrue(table.exists())
        
    def assertTableDoesNotExist(self, dbstring, table_name):
        table = self.setup_table(dbstring, table_name)
        self.assertFalse(table.exists())
        
    def test_initialize_database(self):
        """The table _evolve should be created"""
        dbstring = self.dbstring
        repository = DatabaseRepository(dbstring)
        repository.initialize()
        self.assertTableExists(dbstring, '_evolve')
        
    def test_already_initialized_database_failure(self):
        """raise RepositoryAlreadyExists"""
        dbstring = self.dbstring
        repository = DatabaseRepository(dbstring)
        repository.initialize()
        self.assertRaises(RepositoryAlreadyExists, 
            getattr(repository, 'initialize'))
            
    def test_deploy_create(self):
        """Create a table based on a JSON schema"""
        dbstring = self.dbstring
        repository = DatabaseRepository(dbstring)
        repository.initialize()
        change = {
            "change":"create",
            "schema":{
                "id":"test",
                "type":"object",
                "properties":{
                    "text_column":{"type":"string"}
                }
            }
        }
        repository.deploy(change)
        self.assertTableExists(dbstring, "test")
		
		
if __name__ == '__main__':
    unittest.main()