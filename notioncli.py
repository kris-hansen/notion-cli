import os
import argparse

from termcolor import colored, cprint

from notion.client import NotionClient
from notion.block import TodoBlock

client = NotionClient(token_v2=os.environ['NOTION_TOKEN'])

page = client.get_block(os.environ['NOTION_PAGE'])

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
                
        except:
            pass #not a task 
    cprint('{} removed.'.format(taskn), 'white', attrs=['bold'])