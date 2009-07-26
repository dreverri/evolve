import unittest
from evolve.repository import *
from evolve.branch import *


class TestEvolveBranch(unittest.TestCase):
    def setUp(self):
        self.repo = Repository()
        
    def test_branch(self):
        branch = self.repo.branch('master')
        self.assertEqual(branch.name,'master')
        self.assertEqual(branch.parent.commit_id,'root')
        
    def test_branch_from_branch(self):
        master = self.repo.branch('master')
        exp = self.repo.branch('exp','master')
        self.assertEqual(exp.name,'exp')
        self.assertEqual(exp.parent.commit_id,'root')
        
    def test_verify(self):
        change = {
            "change":"create",
            "schema":{
                "id":"person",
                "type":"object",
                "properties":{
                    "id":{"type":"string"}
                }
            }
        }
        branch = self.repo.branch('master')
        branch.verify(change)
        
    def test_add(self):
        change = {
            "change":"create",
            "schema":{
                "id":"person",
                "type":"object",
                "properties":{
                    "id":{"type":"string"}
                }
            }
        }
        branch = self.repo.branch('master')
        branch.add(change)
        self.assertTrue('person' in branch.schema.tables)
        
    def test_commit(self):
        change = {
            "change":"create",
            "schema":{
                "id":"person",
                "type":"object",
                "properties":{
                    "id":{"type":"string"}
                }
            }
        }
        branch = self.repo.branch('master')
        branch.add(change)
        branch.commit('test commit')
        self.assertFalse(branch.parent.commit_id is 'root')
        
    def test_change_drop(self):
        create = {
            "change":"create",
            "schema":{
                "id":"person",
                "type":"object",
                "properties":{
                    "id":{"type":"string"}
                }
            }
        }
        branch = self.repo.branch('change_drop')
        branch.add(create)
        branch.commit('create person')
        drop = {
            "change":"drop",
            "schema":{
                "id":"person",
                "type":"object",
                "properties":{}
            }
        }
        branch.add(drop)
        # check to see if properties were inheritted from previous schema
        self.assertTrue('id' in drop['old_schema']['properties'])


if __name__ == '__main__':
    unittest.main()