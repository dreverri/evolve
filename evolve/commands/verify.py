import sys
import os
from evolve.file_repository import FileRepository


def usage():
    print("Usage: evolve verify branch_name changes.json")

def verify_changes(branch_name, changes):
    path = os.path.dirname(changes)
    repo = os.path.join(path, 'evolve.json')
    # load repo from file
    # checkout branch
    # verify changes

def run():
    try:
        branch_name = sys.argv[2]
        changes = sys.argv[3]
        verify_changes(branch_name, changes)
    except IndexError:
        usage()
