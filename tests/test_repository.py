import unittest
from evolve.repository import *


class TestEvolveRepository(unittest.TestCase):
    def setUp(self):
        self.repo = Repository()
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
        branch.commit('create person table')
        
    def test_find_common_parent(self):
        master = self.repo.checkout('master')
        b1 = self.repo.branch('b1','master')
        change = {
            "change":"alter.add",
            "schema":{
                "id":"person",
                "type":"object",
                "properties":{
                    "name":{"type":"string"}
                }
            }
        }
        b1.add(change)
        b1.commit('added name field')
        b2 = self.repo.branch('b2','master')
        change2 = {
            "change":"alter.add",
            "schema":{
                "id":"person",
                "type":"object",
                "properties":{
                    "last_name":{"type":"string"}
                }
            }
        }
        b2.add(change2)
        b2.commit('added last name field')
        common = self.repo.find_common_parent(b1.parent.commit_id,b2.parent.commit_id)
        self.assertTrue(master.parent.commit_id == common)
        
    def test_migrate(self):
        master = self.repo.checkout('master')
        b3 = self.repo.branch('b3','master')
        change = {
            "change":"alter.add",
            "schema":{
                "id":"person",
                "type":"object",
                "properties":{
                    "name":{"type":"string"}
                }
            }
        }
        b3.add(change)
        b3.commit('added name field')
        b4 = self.repo.branch('b4','master')
        change2 = {
            "change":"alter.add",
            "schema":{
                "id":"person",
                "type":"object",
                "properties":{
                    "last_name":{"type":"string"}
                }
            }
        }
        b4.add(change2)
        b4.commit('added last name field')
        migration = self.repo.migrate(b3.parent.commit_id,b4.parent.commit_id)
        self.assertTrue(migration[0]['change'] == 'alter.drop')
        self.assertTrue('name' in migration[0]['schema']['properties'])
        self.assertTrue(migration[1]['change'] == 'alter.add')
        self.assertTrue('last_name' in migration[1]['schema']['properties'])
    
        
if __name__ == '__main__':
    unittest.main()