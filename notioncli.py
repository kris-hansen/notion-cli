import os
import notion
import argparse

from termcolor import colored, cprint

from notion.client import NotionClient

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
        cprint('  {}  {}.'.format(check, child.title), 'green')
    cprint('\n{} total tasks'.format(n), 'white', attrs=['bold'])

def add(task):
    newchild = page.children.add_new(TodoBlock, title=task)
    newchild.checked = False

