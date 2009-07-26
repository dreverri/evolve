from evolve.exceptions import RepositoryAlreadyExists
from evolve.db import Database


class DatabaseRepository(object):
    def __init__(self, dbstring):
        self.database = Database(dbstring)
        
    def initialize(self):
        props = {
            "type": {"type": "string", "maxLength": 40},
            "key": {"type": "string", "maxLength": 40},
            "value": {"type": "string"},
        }
        table = self.database.table('_evolve')
        if table.exists():
            raise RepositoryAlreadyExists()
        else:
            for name, prop in props.items():
                column = self.get_column(name, prop)
                table.append_column(column)
            table.create()
    
    def deploy(self, change):
        if change["change"] == "create":
            self.deploy_create(change["schema"])
        if change["change"] == "drop":
            self.deploy_drop(change["schema"])
        if change["change"] == "alter.add":
            self.deploy_alter_add(change["schema"])
        if change["change"] == "alter.rename":
            self.deploy_alter_rename(change["schema"])
        if change["change"] == "alter.modify":
            self.deploy_alter_modify(change["schema"])
        if change["change"] == "alter.drop":
            self.deploy_alter_drop(change["schema"])
            
    def deploy_create(self, schema):
        table = self.get_table(schema)
        for name, prop in schema["properties"].items():
            column = self.get_column(name, prop)
            table.append_column(column)
        table.create()
        
    def deploy_drop(self, schema):
        table = self.get_table(schema)
        table.drop()
        
    def deploy_alter_add(self, schema):
        table = self.get_table(schema)
        for name, prop in schema["properties"].items():
            column = self.get_column(name, prop)
            column.create(table)
            
    def deploy_alter_drop(self, schema):
        table = self.get_table(schema)
        for name, prop in schema["properties"].items():
            column = table.c[name]
            column.drop()
            
    def deploy_alter_rename(self, schema):
        table = self.get_table(schema)
        for oldname, newname in schema["properties"].items():
            column = table.c[oldname]
            column.alter(name=newname)
            
    def deploy_alter_modify(self, schema):
        table = self.get_table(schema)
        for name, prop in schema["properties"].items():
            newcolumn = get_column(name, prop)
            oldcolumn = table.c[name]
            oldcolumn.alter(newcolumn)
        
    def get_table(self, schema):
        return self.database.table(schema["id"])
        
    def get_column(self, name, prop):
        return self.database.column(name, prop)