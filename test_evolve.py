import unittest
import evolve

class TestEvolve(unittest.TestCase):
	def setUp(self):
		self.repo = evolve.Repository()
		
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
		self.assertTrue(branch.parent.commit_id is not 'root')
		
		
if __name__ == '__main__':
    unittest.main()