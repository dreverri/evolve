import unittest
import evolve

class TestEvolveBranch(unittest.TestCase):
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
		
		
class TestEvolveCommit(unittest.TestCase):
		def setUp(self):
			self.repo = evolve.Repository()
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
			
		def test_getAncestors(self):
			branch = self.repo.checkout('master')
			commit = branch.parent
			a = commit.getAncestors()
			self.assertTrue('root' in a)
			self.assertTrue(branch.parent.commit_id in a)
			
		def test_rollback(self):
			branch = self.repo.checkout('master')
			commit = branch.parent
			revlog = commit.rollback('root')
			self.assertEqual(len(revlog),1)
			self.assertTrue(revlog[0]['change'] == 'drop')
			
		def test_reverse_create(self):
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
			branch = self.repo.checkout('master')
			commit = branch.parent
			reverse_change = commit.reverse(change)
			self.assertTrue(reverse_change['change'] == 'drop')
			
		def test_reverse_drop(self):
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
			branch = self.repo.branch('reverse_drop','master')
			commit = branch.parent
			change1 = commit.reverse(change)
			branch.add(change1)
			branch.commit('drop table')
			commit = branch.parent
			change2 = commit.reverse(change1)
			self.assertTrue(change2['change'] == 'create')
			
		def test_reverse_alter_add(self):
			branch = self.repo.branch('reverse_alter_add','master')
			change = {
				'change':'alter.add',
				'schema':{
					"id":"person",
					"type":"object",
					"properties":{
						"name":{"type":"string"}
					}
				}
			}
			branch.add(change)
			branch.commit('reverse_alter_add')
			commit = branch.parent
			c2 = commit.reverse(change)
			self.assertTrue(c2['change'] == 'alter.drop')
		
		def test_reverse_alter_modify(self):
			branch = self.repo.branch('reverse_alter_modify','master')
			c1 = {
				'change':'alter.add',
				'schema':{
					"id":"person",
					"type":"object",
					"properties":{
						"name":{"type":"string"}
					}
				}
			}
			c2 = {
				'change':'alter.modify',
				'schema':{
					"id":"person",
					"type":"object",
					"properties":{
						"name":{"type":"string","maxLength":50}
					}
				}
			}
			branch.add(c1)
			branch.add(c2)
			branch.commit('reverse_alter_modify')
			commit = branch.parent
			c3 = commit.reverse(c2)
			self.assertTrue(c3['change'] == 'alter.modify')
			self.assertFalse('maxLength' in c3['schema']['properties']['name'])
			
class TestEvolveCommit(unittest.TestCase):
	def setUp(self):
		self.repo = evolve.Repository()
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