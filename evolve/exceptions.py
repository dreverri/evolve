class RepositoryAlreadyExists(Exception):
    pass


class BranchNotFound(Exception):
    pass


class BranchAlreadyExists(Exception):
    pass


class NoCommonParent(Exception):
    pass



class CommitNotFound(Exception):
    pass


class InvalidChange(Exception):
    pass