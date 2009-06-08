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

class Repository:
	def __init__(self):
		self.commits = {'root':{'changelog':[],'msg':'root'}}
		self.branches = {}
		self.checkouts = {}
		
	def branch(self,branch_name,parent_branch_name=None):
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
		
	def rollback(self,commit):
		pass
		
	def find_common_parent(self,start_commit,end_commit):
		pass

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
			del tables[table]

		if action == 'alter.add' or action == 'alter.modify':
			for field in fields:
				tables[table]['properties'][field] = fields[field]

		if action == 'alter.rename':
			for field in fields:
				newname = fields[field]
				tables[table]['properties'][newname] = tables[table]['properties'][field]
				del tables[table]['properties'][field]

		if action == 'alter.drop':
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
			self.changelog.append(change)
			self.schema.add(change)
		else:
			raise InvalidChange

	def commit(self,msg):
		commit = Commit(self.repository)
		commit.parent = self.parent
		commit.changelog = self.changelog
		commit.schema = self.schema
		commit.msg = msg
		commit.commit_id = hashlib.sha1(json.dumps(commit.toDict()))
		commit.checkedout = True
		self.repository.commits[commit.commit_id] = commit.toDict()
		self.repository.checkouts[commit.commit_id] = commit
		self.repository.branches[self.name] = commit.commit_id
		self.parent = commit
		self.reset()
		
	def reset(self):
		self.schema = copy.deepcopy(self.parent.schema)
		self.changelog = []
