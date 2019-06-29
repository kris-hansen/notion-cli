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

try:
    client = NotionClient(token_v2=os.environ['NOTION_TOKEN'], monitor=False)
    page = client.get_block(os.environ['NOTION_PAGE'])
except:
    cprint('NOTION_TOKEN / NOTION_PAGE environment variables not set.\n', 'red')
    
def parse_task(string):
    taskn = string
    if isinstance(string, int):
        taskn = str(taskn)
    else:
        if ',' in string:
            taskn = string.split(',')
    value = taskn
    return value


parser = argparse.ArgumentParser(description='A Notion.so CLI \
focused on simple task management')
parser.add_argument('--env', nargs='?', const=True, default=False, help='Print current relevant environment variables')
parser.add_argument('--list', nargs='?', const=True, default=False, help='List tasks')
parser.add_argument('--add', default=False, type=str, help='Usage: --add [str] Add a new task')
parser.add_argument('--remove', default=False, type=parse_task, help='Usage: --remove [n] Remove task n from the task list')
parser.add_argument('--check', default=False, type=parse_task, help='Usage: --check [n] check off task n')
parser.add_argument('--uncheck', default=False, type=parse_task, help='Usage: --segment : Update the OWL / KOHO link \
for the current segmentid (and other environments defined by the current set of environment variables)')

args = parser.parse_args()

def checkEnv():
    try:
        os.environ['NOTION_TOKEN']
        os.environ['NOTION_PAGE']
    except KeyError:
        cprint('Environment variables not set', 'white')
        exit

def list():
    checkEnv()
    n = 0 
    cprint('\n\n{}\n'.format(page.title), 'white', attrs=['bold'])
    cprint('#  Status Description','white',attrs=['underline'])
    for child in page.children:
        n += 1
        try:
            if child.checked:
                check = '[*]'
            else:
                check = '[ ]'
        except:
            pass #not a task
        if len(str(n)) <= 1:
            cprint('  {}   {}  {}.'.format(n, check, child.title), 'green')
        if len(str(n)) > 1:
            cprint('  {}  {}  {}.'.format(n, check, child.title), 'green')

    cprint('\n{} total tasks'.format(n), 'white', attrs=['bold'])

def check(taskn):
    n = 0
    for child in page.children:
        n += 1
        try:
            for task in taskn:
                if n == int(task):
                    child.checked = True
        except:
            pass #not a task 
    cprint('{} marked as completed'.format(taskn), 'white', attrs=['bold'])

def uncheck(taskn):
    if isinstance(taskn, int):
        taskn = str(taskn)
    else:
        if ',' in taskn:
            taskn = taskn.split(',')
    n = 0
    for child in page.children:
        n += 1
        try:
            for task in taskn:
                if n == int(task):
                    child.checked = False
        except:
            pass #not a task 
    cprint('{} marked as incomplete'.format(taskn), 'white', attrs=['bold'])

def add(task):
    newchild = page.children.add_new(TodoBlock, title=task)
    newchild.checked = False
    cprint('{} added as a new task'.format(task))

def remove(taskn):
    if isinstance(taskn, int):
        taskn = str(taskn)
    else:
        if ',' in taskn:
            taskn = taskn.split(',')
    n = 0
    for child in page.children:
        n += 1
        try:
            for task in taskn:
                if n == int(task):
                    child.remove()      
        except:
            pass #not a task 
    cprint('{} removed.'.format(taskn), 'white', attrs=['bold'])

if args.env:
    cprint('\n Environment variables: \n', 'white', attrs=['underline'])
    cprint('    Notion.so token: {}\n'.format(os.environ['NOTION_TOKEN']), 'green')
    cprint('    Notion.so page: {}\n'.format(os.environ['NOTION_PAGE']), 'green')

if args.list:
    checkEnv()
    list()

if args.add:
    add(str(args.add))

if args.check:
    check(args.check)

if args.uncheck:
    uncheck(args.uncheck)

if args.remove:
    remove(args.remove)

   
