from sqlalchemy import *
from migrate import *
from evolve.json2sql import JSONSchemaTypeToSQLColumnType


class Database(object):
    def __init__(self, dbstring):
        self.dbstring = dbstring
        self.engine = create_engine(dbstring)
        self.metadata = MetaData(self.engine)
        
    def table(self, table_name):
        metadata = self.metadata
        table = Table(table_name, metadata)
        return table

    def column(self, name, prop):
        _type = self.column_type(prop)
        if "identity" in prop and prop["identity"]:
            primary_key = True
        else:
            primary_key = False
        
        column = Column(name, _type, primary_key=primary_key)
        return column

    def column_type(self, prop):
        return JSONSchemaTypeToSQLColumnType(prop).get_column_type()