# TODO
# Convert JSON to Column
# Convert JSON to Table
# What to do with existing schema on legacy DB?

# Usage:
# evolve init db://user:pass@host:port
# evolve clone db://user:pass@host:port
# add changes to changes.json
# evolve verify changes.json
# evolve commit changes.json
# evolve push db://user:pass@host:port master
# evolve deploy db://user:pass@host:port master
# evolve deploy . master

# How to access the data from python?
# need to build python classes that map to the database
# deploy a static python file?
# load the models dynamically from the database?
# loading dynamically is not a good idea
# deploy a static file
# should it be python or json?
# json would have to be reloaded to build the pyhton models
# deploy a static python file with the same name as the branch
# file would have to declare the dbstring and commit_id
# commit_id would ensure that the file is up to date with the database
# deploy statis python files to models folder


import unittest
from sqlalchemy import *
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker

dbstring = "sqlite:///:memory:"
engine = create_engine(dbstring)
metadata = MetaData(engine)

schema = {
    "person":{
        "id":"person",
    	"type":"object",
    	"properties":{
    		"id":{"type":"string", "identity": True}
    	},
    },
    "address":{
        "id":"address",
    	"type":"object",
    	"properties":{
    		"id":{"type":"string", "identity": True}
    	},
    }
}

class Models(object):
    pass

class EvolvedModel:
    pass
    
def get_column_type(prop):
    if "type" in prop and prop["type"] == "string":
        if "format" in prop and prop["format"] == "date":
            pass
        else:
            if "maxLength" in prop and prop["maxLength"]:
                return Unicode(length = prop["maxLength"])
            else:
                return UnicodeText()
                
def get_column(name, prop):
    type_ = get_column_type(prop)
    column = Column(name, type_)
    if "primary_key" in prop and prop["primary_key"]:
        column.primary_key = True
    return column
    
def build_table(props):
    table_name = props["id"]
    table = Table(table_name, metadata)
    for name, prop in props["properties"].items():
        column = get_column(name, prop)
        table.append_column(column)
    return table

for name, props in schema.items():
    table = build_table(props)
    table.create()
    model = type(name, (object, EvolvedModel), {})
    mapper(model, table)
    setattr(Models, name, model)

Session = sessionmaker(bind=engine)
session = Session()

person = Models.person()
person.id = u'1'
session.add(person)
print(session.query(Models.person).all())

class EvolvedModelsTest(unittest.TestCase):
    def test_object_creation(self):
        pass
        
    def test_column_creation(self):
        pass
        
    def test_table_creation(self):
        pass
        
    def test_object_table_mapper(self):
        pass
        
    def test_query_all(self):
        pass
        
    def test_query_by_id(self):
        pass
        
    def test_save_record(self):
        pass
    
    def test_update_record(self):
        pass
        
    def test_delete_record(self):
        pass
        

if __name__ == "__main__":
    unittest.main()