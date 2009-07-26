from sqlalchemy.orm import mapper
from evolve.db import Database


class EvolvedModel(object):
    pass


class Models(object):
    def __init__(self, dbstring, schema):
        self.database = Database(dbstring)
        self.schema = schema
        self.models = {}
        
    def build(self):
        """Build models from schema"""
        for modelname, modelschema in self.schema.items():
            table_name = modelschema["id"]
            table = self.database.table(table_name)
            dct = {"schema": modelschema}
            model = type(modelname, (EvolvedModel, ), dct)
            mapper(model, table)
            self.models[modelname] = model