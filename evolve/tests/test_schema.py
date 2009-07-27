import unittest
from evolve.schema import *
from evolve.tests import non_reversible_changes
from evolve.tests import reversible_changes


class EvolveSchemaTestCase(unittest.TestCase):
    def setUp(self):
        self.schema = Schema()
        
    def setup_schema_for_alter_add(self):
        self.schema.tables['person'] = {
            "id":"person",
            "type":"object",
            "properties":{
                "id": {"type":"string"}
            }
        }
        
    def setup_schema_for_drop(self):
        self.schema.tables['person'] = {
            "id":"person",
            "type":"object",
            "properties":{
                "id": {"type":"string"},
            }
        }
        
    def setup_schema_for_alter_drop_alter_modify_alter_rename(self):
        self.schema.tables['person'] = {
            "id":"person",
            "type":"object",
            "properties":{
                "id": {"type":"string"},
                "name": {"type":"string"}
            }
        }


class EvolveSchemaMakeChangesReversible(EvolveSchemaTestCase):
    def test_create(self):
        rev = reversible_changes.create
        non_rev = non_reversible_changes.create
        result = self.schema.make_change_reversible(non_rev)
        self.assertEqual(result, rev)
        
    def test_drop(self):
        self.setup_schema_for_drop()
        rev = reversible_changes.drop
        non_rev = non_reversible_changes.drop
        result = self.schema.make_change_reversible(non_rev)
        self.assertEqual(result, rev)
        
    def test_alter_add(self):
        self.setup_schema_for_alter_add()
        rev = reversible_changes.alter_add
        non_rev = non_reversible_changes.alter_add
        result = self.schema.make_change_reversible(non_rev)
        self.assertEqual(result, rev)
        
    def test_alter_drop(self):
        self.setup_schema_for_alter_drop_alter_modify_alter_rename()
        rev = reversible_changes.alter_drop
        non_rev = non_reversible_changes.alter_drop
        result = self.schema.make_change_reversible(non_rev)
        self.assertEqual(result, rev)
        
    def test_alter_modify(self):
        self.setup_schema_for_alter_drop_alter_modify_alter_rename()
        rev = reversible_changes.alter_modify
        non_rev = non_reversible_changes.alter_modify
        result = self.schema.make_change_reversible(non_rev)
        self.assertEqual(result, rev)
        
    def test_alter_rename(self):
        self.setup_schema_for_alter_drop_alter_modify_alter_rename()
        rev = reversible_changes.alter_rename
        non_rev = non_reversible_changes.alter_rename
        result = self.schema.make_change_reversible(non_rev)
        self.assertEqual(result, rev)