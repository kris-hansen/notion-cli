import os
import argparse

from termcolor import colored, cprint

from notion.client import NotionClient
from notion.block import TodoBlock

from contextlib import redirect_stdout
from contextlib import contextmanager
from io import StringIO

@contextmanager
def captureStdOut(output): 
    stdout = sys.stdout
    sys.stdout = output
    try:
        yield
    finally:
        sys.stdout = stdout

client = NotionClient(token_v2=os.environ['NOTION_TOKEN'])

page = client.get_block(os.environ['NOTION_PAGE'])

parser = argparse.ArgumentParser(description='A Notion.so CLI \
focused on simple task management')
parser.add_argument('--env', nargs='?', const=True, default=False, help='Print current relevant environment variables')
parser.add_argument('--list', nargs='?', const=True, default=False, help='List tasks')
parser.add_argument('--add', default=False, type=str, help='Usage: --add [str] Add a new task')
parser.add_argument('--remove', default=False, type=int, help='Usage: --remove [n] Remove task n from the task list')
parser.add_argument('--check', default=False, type=int, help='Usage: --check [n] check off task n')
parser.add_argument('--uncheck', default=False, type=int, help='Usage: --segment : Update the OWL / KOHO link \
for the current segmentid (and other environments defined by the current set of environment variables)')

args = parser.parse_args()

def list():
    n = 0 
    cprint('{}\n'.format(page.title), 'white', attrs=['underline'])
    for child in page.children:
        n += 1
        try:
            if child.checked:
                check = '[*]'
            else:
                check = '[ ]'
        except:
            pass #not a task    
        cprint('  {}  {}  {}.'.format(n, check, child.title), 'green')
    cprint('\n{} total tasks'.format(n), 'white', attrs=['bold'])

def check(taskn):
    n = 0
    for child in page.children:
        n += 1
        try:
            if n == taskn:
                child.checked = True
        except:
            pass #not a task 
    cprint('{} marked as completed'.format(taskn), 'white', attrs=['bold'])

def uncheck(taskn):
    n = 0
    for child in page.children:
        n += 1
        try:
            if n == taskn:
                child.checked = False
        except:
            pass #not a task 
    cprint('{} marked as incomplete'.format(taskn), 'white', attrs=['bold'])

def add(task):
    newchild = page.children.add_new(TodoBlock, title=task)
    newchild.checked = False
    cprint('{} added as a new task'.format(task))

def remove(taskn):
    n = 0
    for child in page.children:
        n += 1
        try:
            if n == taskn:
                child.remove()      
        except:
            pass #not a task 
    cprint('{} removed.'.format(taskn), 'white', attrs=['bold'])

if args.env:
    cprint('\n Environment variables: \n', 'white', attrs=['underline'])
    cprint('    Notion.so token: {}\n'.format(os.environ['NOTION_TOKEN']), 'green')
    cprint('    Notion.so page: {}\n'.format(os.environ['NOTION_PAGE']), 'green')

if args.list:
    list()

if args.add:
    add(str(args.add))

if args.check:
    if isinstance(args.check, int):
        check(args.check)
    else:
        cprint('Check requires an int argument for task number','white', attrs=['bold'])

if args.uncheck:
    if isinstance(args.uncheck, int):
        uncheck(args.uncheck)
    else:
        cprint('Uncheck requires an int argument for task number','white', attrs=['bold'])


if args.remove:
    if isinstance(args.remove, int):
        remove(args.remove)
    else:
        cprint('Remove requires an int argument for task number','white', attrs=['bold'])
   