import os
import sys


commands = []
script_path = os.path.dirname(__file__)
for f in os.listdir(script_path):
    file_path = os.path.join(script_path, f)
    if os.path.isfile(file_path):
        parts = f.split('.')
        command = parts[0]
        extension = parts[1]
        if extension == 'py' and command != '__init__':
            commands.append(command)


def usage():
    print("Available commands:")
    for command in commands:
        print(command)

def run_cmd(command):
    if command in commands:
        _mod = __import__("evolve.commands.%s" % command, fromlist=['run'])
        _mod.run()
    else:
        usage()


def run():
    try:
        command = sys.argv[1]
        run_cmd(command)
    except IndexError:
        usage()