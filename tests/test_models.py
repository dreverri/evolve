import unittest
from evolve.models import Models
from evolve.db import Database
import os
from sqlalchemy import *


class TestModels(unittest.TestCase):
    def setUp(self):
        self.schema = {
            "person":{
                "id":"person",
                "type":"object",
                "properties":{
                    "id":{"type": "string", 
                            "maxLength": 40, 
                            "identity": True
                            },
                    "name":{"type": "string", "maxLength": 255}
                }
            }
        }
        self.models = Models('sqlite:///test_database.db', self.schema)
        table = self.models.database.table('person')
        table.append_column(Column('id', Unicode(40), primary_key=True))
        table.append_column(Column('name', Unicode(255)))
        table.create()
        
    def tearDown(self):
        if os.path.exists('test_database.db'):
            os.remove('test_database.db')
            
    def build_person(self):
        self.models.build()
        person = self.models.models['person']
        return person
        
    def test_build_with_person(self):
        self.models.build()
        self.assertTrue('person' in self.models.models.keys())
        
    def test_person_has_schema(self):
        person = self.build_person()
        self.assertTrue(hasattr(person, 'schema'))
        
    def test_person_schema_is_correct(self):
        person = self.build_person()
        self.assertEqual(person.schema, self.schema["person"])
        
    def test_person_has_id(self):
        person = self.build_person()
        self.assertTrue(hasattr(person, 'id'))
        
    def test_person_has_name(self):
        person = self.build_person()
        self.assertTrue(hasattr(person, 'name'))
        
    def test_person_does_not_have_other(self):
        person = self.build_person()
        self.assertFalse(hasattr(person, 'other'))


if __name__ == '__main__':
    unittest.main()