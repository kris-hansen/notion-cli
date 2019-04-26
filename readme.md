# *Notion CLI*

It's a CLI to track your tasks.

In a Notion.so page

![](https://github.com/kris-hansen/notion-cli/blob/master/notionclilist.gif)

In the tune of taskbook (https://github.com/klaussinani/taskbook) which is an npm package that I started using and really enjoyed; but I wanted something that was more portable across my devices and that I could also shared (i.e., it needed a back end)

I started looking at Notion for this, but wanted to stay in CLI land vs. having to task back to bright colours to check my code to do's

Thus, this mini project was born

![](https://github.com/kris-hansen/notion-cli/blob/master/notioncliadd.gif)

Uses the Python library notion-py (https://github.com/jamalex/notion-py) to access to the Notion 'API'

## Install

- Requirements - Python3 and pip install the requirements.txt dependencies 
- Edit dev-env.source.sample and enter your page and token (you can find the token in your browser cookies after a successful Notion login)

## Run

you can run it directly with:

`$ python notioncli.py`

or

build it into an executable with:

`pyinstaller --onefile notioncli.py`

and then cp the binary from the ./dist folder to somewhere in your path

```$ notioncli --help
usage: notioncli [-h] [--env [ENV]] [--list [LIST]] [--add ADD]
                 [--remove REMOVE] [--check CHECK] [--uncheck UNCHECK]

A Notion.so CLI focused on simple task management

optional arguments:
  -h, --help         show this help message and exit
  --env [ENV]        Print current relevant environment variables
  --list [LIST]      List tasks
  --add ADD          Usage: --add [str] Add a new task
  --remove REMOVE    Usage: --remove [n] Remove task n from the task list
  --check CHECK      Usage: --check [n] check off task n
  --uncheck UNCHECK  Usage: --segment : Update the OWL / KOHO link for the
                     current segmentid (and other environments defined by the
                     current set of environment variables)
```

## Notes

- The pyinstaller packager does not work with conda/miniconda
- PY3.5 tested

## Future to-dos

- I think it needs to be faster, I have considered rewriting in go; not sure how much of the delay is related to runtime (pyinstaller packaging efficiency)
vs network/Notion 'API' delays
- Multiple pages, one per project