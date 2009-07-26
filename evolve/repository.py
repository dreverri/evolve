from evolve.commit import Commit
from evolve.branch import Branch


class BranchNotFound(Exception):
    pass


class BranchAlreadyExists(Exception):
    pass


class NoCommonParent(Exception):
    pass


class Repository(object):
    def __init__(self):
        self.commits = {'root': {'changelog': [], 'msg': 'root'}}
        self.branches = {}
        self.checkouts = {}
        
    def branch(self, branch_name, parent_branch_name=None):
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
        
    def checkout(self, branch_name):
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
            
        branch = Branch(self, branch_name, commit)
        return branch
        
    def find_common_parent(self, commit_one, commit_two):
        """Find the common parent between the two commits if one exists"""
        one = Commit(self)
        one.checkout(commit_one)
        two = Commit(self)
        two.checkout(commit_two)
        listone = one.getAncestors()
        listtwo = two.getAncestors()
        def compare(a, b):
            common = None
            for index in range(len(a)):
                if a[index] is not b[index]:
                    return common
                common = a[index]
            return common
                
        if len(listone) < len(listtwo):
            common = compare(listone, listtwo)
        else:
            common = compare(listtwo, listone)
        
        if not common:
            raise NoCommonParent("The commits %s and %s do not share a common parent" % (commit_one, commit_two))
            
        return common
        
    def migrate(self, commit_one, commit_two):
        """Migrate from one commit to another"""
        parent = self.find_common_parent(commit_one, commit_two)
        c1 = Commit(self)
        c1.checkout(commit_one)
        c2 = Commit(self)
        c2.checkout(commit_two)
        log = c1.rollback(parent)
        log.extend(c2.rollforward(parent))
        return log