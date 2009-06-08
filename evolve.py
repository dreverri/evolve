import copy, hashlib

try:
	import json
except ImportError:
	import simplejson as json

class BranchNotFound(Exception):
	pass
	
class CommitNotFound(Exception):
	pass
	
class InvalidChange(Exception):
	pass
	
class BranchAlreadyExists(Exception):
	pass

class NoCommonParent(Exception):
	pass

class Repository:
	def __init__(self):
		self.commits = {'root':{'changelog':[],'msg':'root'}}
		self.branches = {}
		self.checkouts = {}
		
	def branch(self,branch_name,parent_branch_name=None):
		if branch_name in self.branches:
			raise BranchAlreadyExists("The branch %s already exists, use checkout()" % branch_name)
			
		if parent_branch_name:
			try:
				self.branches[branch_name] = self.branches[parent_branch_name]
			except KeyError:
				raise BranchNotFound("Could not find the %s branch" % parent_branch_name)
		else:
			self.branches[branch_name] = 'root'
		return self.checkout(branch_name)
		
	def checkout(self,branch_name):
		try:
			commit_id = self.branches[branch_name]
		except KeyError:
			raise BranchNotFound("Could not find the %s branch" % branch_name)
		
		try:
			commit = self.checkouts[commit_id]
		except KeyError:
			commit = Commit(self)
			commit.checkout(commit_id)
			self.checkouts[commit_id] = commit
			
		branch = Branch(self,branch_name,commit)
		return branch
		
	def find_common_parent(self,commit_one,commit_two):
		"""Find the common parent between the two commits if one exists"""
		one = Commit(self)
		one.checkout(commit_one)
		two = Commit(self)
		two.checkout(commit_two)
		listone = one.getAncestors()
		listtwo = two.getAncestors()
		def compare(a,b):
			common = None
			for index in range(len(a)):
				if a[index] is not b[index]:
					return common
				common = a[index]
			return common
				
		if len(listone) < len(listtwo):
			common = compare(listone,listtwo)
		else:
			common = compare(listtwo,listone)
		
		if not common:
			raise NoCommonParent("The commits %s and %s do not share a common parent" % (commit_one,commit_two))
			
		return common
		
	def migrate(self,commit_one,commit_two):
		"""Migrate from one commit to another"""
		parent = self.find_common_parent(commit_one,commit_two)
		c1 = Commit(self)
		c1.checkout(commit_one)
		c2 = Commit(self)
		c2.checkout(commit_two)
		log = c1.rollback(parent)
		log.extend(c2.rollforward(parent))
		return log		

class Schema:
	def __init__(self):
		self.tables = {}
		
	def verify(self,change):
		"""Verify change against the working schema"""
		tables = self.tables
		action = change['change']
		schema = change['schema']
		table = schema['id']
		fields = schema['properties']
	
		if action == 'create':
			return table not in tables
		
		if action == 'drop':
			return table in tables
		
		if action == 'alter.add' or action == 'alter.rename':
			if table not in tables:
				return False
			for field in fields:
				if field in tables[table]['properties']:
					return False
			return True
		
		if action == 'alter.modify':
			if table not in tables:
				return False
			for field in fields:
				if field not in tables[table]['properties']:
					return False
			return True

	def add(self,change):
		"""Add change to the working changelog, indexed per table, and working schema"""
		tables = self.tables
		action = change['change']
		schema = change['schema']
		table = change['schema']['id']
		fields = change['schema']['properties']

		if action == 'create':
			tables[table] = schema

		if action == 'drop':
			change['old_schema'] = copy.deepcopy(tables[table])
			del tables[table]

		if action == 'alter.add' or action == 'alter.modify':
			if action == 'alter.modify':
				change['old_schema'] = copy.deepcopy(tables[table])
			for field in fields:
				tables[table]['properties'][field] = fields[field]

		if action == 'alter.rename':
			for field in fields:
				newname = fields[field]
				tables[table]['properties'][newname] = tables[table]['properties'][field]
				del tables[table]['properties'][field]

		if action == 'alter.drop':
			change['old_schema'] = copy.deepcopy(tables[table])
			for field in fields:
				del tables[table]['properties'][field]
		
class Commit:
	def __init__(self,repository):
		self.repository = repository
		self.parent = None
		self.changelog = None
		self.schema = None
		self.commit_id = None
		self.msg = None
		self.checkedout = False
		
	def checkout(self,commit_id):
		if self.checkedout:
			return
		
		try:
			commit_dict = self.repository.commits[commit_id]
		except KeyError:
			raise CommitNotFound("Could not find the commit %s" % commit_id)
		
		self.commit_id = commit_id
		self.msg = commit_dict['msg']
		
		if 'parent' in commit_dict:
			self.parent = Commit(self.repository)
			self.parent.checkout(commit_dict['parent'])
			self.schema = copy.deepcopy(self.parent.schema)
		else:
			self.parent = None
			self.schema = Schema()
		
		self.changelog = commit_dict['changelog']
			
		for change in self.changelog:
			self.schema.add(change)
			
		self.checkedout = True
		
	def toDict(self):
		d = {
			'changelog':self.changelog,
			'msg':self.msg
		}
		
		if self.parent:
			d['parent'] = self.parent.commit_id
			
		return d	
	
	def getAncestors(self):
		if self.parent:
			parents = self.parent.getAncestors()
			parents.append(self.commit_id)
			return parents
		else:
			return [self.commit_id]
	
	def rollback(self,to_commit=None):
		"""Returns a changelog that will rollback the current commit to the given commit_id.
		
		If to_commit is None than only this commit will be rolled back in the changelog."""
		if to_commit is self.commit_id:
			raise InvalidChange("Can't rollback to self")
			
		if not to_commit:
			to_commit = self.parent.commit_id
			
		ancestors = self.getAncestors()
		if to_commit not in ancestors:
			raise CommitNotFound("Did not find %s in the list of ancestors of %s" % (to_commit, self.commit_id))
			
		revlog = [self.reverse(change) for change in self.changelog]
		revlog.reverse()
			
		if self.parent.commit_id is not to_commit:
			parentlog = self.parent.rollback(to_commit)
			revlog.extend(parentlog)
		
		return revlog
		
	def rollforward(self,from_commit=None):
		"""Return changelog from given commit to current commit"""
		if from_commit is self.commit_id:
			raise InvalidChange("Can't rollback to self")
			
		if not from_commit:
			from_commit = self.parent.commit_id
			
		ancestors = self.getAncestors()
		if from_commit not in ancestors:
			raise CommitNotFound("Did not find %s in the list of ancestors of %s" % (from_commit, self.commit_id))

		log = copy.deepcopy(self.changelog)

		if self.parent.commit_id is not from_commit:
			parentlog = self.parent.rollforward(from_commit)
			parentlog.extend(log)
			log = parentlog

		return log
		
	def reverse(self,change):
		action = change['change']
		table = change['schema']['id']
		fields = change['schema']['properties']
		new_change = copy.deepcopy(change)
		if 'old_schema' in new_change:
			del new_change['old_schema']
		
		if action == 'create':
			new_change['change'] = 'drop'
			
		if action == 'drop':
			new_change['change'] = 'create'
			new_change['schema'] = change['old_schema']
			
		if action == 'alter.add':
			new_change['change'] = 'alter.drop'

		if action == 'alter.modify':
			for field in fields:
				old = change['old_schema']['properties'][field]
				new_change['schema']['properties'][field] = old
			
		if action == 'alter.rename':
			for field in fields:
				newname = fields[field]
				new_change['schema']['properties'][newname] = field
				del new_change['schema']['properties'][field]
			
		if action == 'alter.drop':
			new_change['change'] = 'alter.add'
			for field in fields:
				old = change['old_schema']['properties'][field]
				new_change['schema']['properties'][field] = old
				
		return new_change
							
class Branch:
	def __init__(self,repository,name,parent):
		self.repository = repository
		self.name = name
		self.parent = parent
		self.reset()
		
	def verify(self,change):
		return self.schema.verify(change)

	def add(self,change):
		if self.verify(change):
			self.schema.add(change)
			self.changelog.append(change)
		else:
			raise InvalidChange

	def commit(self,msg):
		commit = Commit(self.repository)
		commit.parent = self.parent
		commit.changelog = self.changelog
		commit.schema = self.schema
		commit.msg = msg
		commit.commit_id = hashlib.sha1(json.dumps(commit.toDict())).hexdigest()
		commit.checkedout = True
		self.repository.commits[commit.commit_id] = commit.toDict()
		self.repository.checkouts[commit.commit_id] = commit
		self.repository.branches[self.name] = commit.commit_id
		self.parent = commit
		self.reset()
		
	def reset(self):
		self.schema = copy.deepcopy(self.parent.schema)
		self.changelog = []
