import sys
import os
from evolve.file_repository import FileRepository
from evolve.database_repository import DatabaseRepository
from evolve.exceptions import RepositoryAlreadyExists
from sqlalchemy import exc


def usage():
    print("Usage: evolve init [dburl]")
    
def init_file():
    try:
        repo = FileRepository()
        repo.initialize('.')
    except RepositoryAlreadyExists:
        print("Error: Repository already exists at the current location")
        usage()

def init_db(target):
    try:
        repo = DatabaseRepository(target)
        repo.initialize()
    except exc.ArgumentError:
        print("Error: The provided database URL is not valid (%s)" % target)
        usage()
    except RepositoryAlreadyExists:
        print("Error: Repository already exists in the specified datbase")
        usage()

def run():
    try:
        target = sys.argv[2]
        init_db(target)
    except IndexError:
        init_file()
    