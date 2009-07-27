import sys
import os
from evolve.file_repository import FileRepository
from evolve.database_repository import DatabaseRepository


def usage():
    print("Usage: evolve init [dbstring|path]")

def init_target(target):
    if os.path.isdir(target):
        repo = FileRepository()
        repo.initialize(target)
    else:
        repo = DatabaseRepository(target)
        repo.initialize()

def run():
    try:
        target = sys.argv[2]
        init_target(target)
    except IndexError:
        usage()
    