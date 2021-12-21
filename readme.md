# *Notion CLI*

It's a CLI to track your tasks.

In a Notion.so page

![](https://github.com/kris-hansen/notion-cli/blob/master/notionclilist.gif)

In the tune of taskbook (https://github.com/klaussinani/taskbook) which is an npm package that I started using and really enjoyed; but I wanted something that was more portable across my devices and that I could also shared (i.e., it needed a back end).

I started looking at Notion for this, but wanted to stay in CLI land vs. having to task back to bright colours to check my code to do's.

Thus, this mini project was born!

![](https://github.com/kris-hansen/notion-cli/blob/master/notioncliadd.gif)

Uses the Python library [notion-py](https://github.com/jamalex/notion-py) to access to the Notion 'API'.

## Install

### pip

You can install from git with pip:

```sh
pip install --user git+https://github.com/kris-hansen/notion-cli@latest
```

### git + virtualenv

First, make sure you have a recent Python 3 in your path. Ubuntu and other Linux
distributions should already have it installed. On MacOS, you can run
`brew install python`. For Windows, you're on your own - though note that
building the pyinstaller bundle isn't supported on Conda.

To set up the virtualenv, run `make setup`.

To source the virtualenv after it's built, run `source ./venv/bin/activate` in
bash.

### pyinstaller bundle

Once you have the git/virtualenv install set up, you may generate a portable
single-file bin via pyinstaller by running `make build`. Note that the
pyinstaller build is quite slow to boot!

## Configuration

In order to run this tool, you need to define two environment variables:

- `NOTION_TOKEN` - This is the API token for the API client
- `NOTION_PAGE` - This is the URL for the page (ex: https://notion.so/my-page)

To get the `NOTION_TOKEN`, you'll need to:

- Log into notion in your web browser
- Crack open the dev console
- Dig through your browser cookies
- Copy-paste it on out

See the notion-py documentation for more details.

For convenience, this project includes an example env file that you can use as
a template:

```bash
cp dev-env.source.sample .env
${EDITOR} .env  # Fill in the fields
```

## Run

To run the tool, ensure that the virtualenv is set up and the env file is
loaded:

```bash
source ./venv/bin/activate
source .env

notion --help
```

For convenience, you may want to put a shim in your path:

```bash
#!/usr/bin/env bash

source ${HOME}/notion-cli/venv/bin/activate
source ${HOME]/.config/notion/notion.env

exec notion "$@"
```

A good location for this script may be `~/.local/bin/notion`.

```bash
$ notion --help
usage: notion [-h] [--env [ENV]] [--list [LIST]] [--add ADD]
                 [--remove REMOVE] [--check CHECK] [--uncheck UNCHECK]

A Notion.so CLI focused on simple task management

optional arguments:
  -h, --help         show this help message and exit
  --env [ENV]        Print current relevant environment variables
  --list [LIST]      List tasks
  --add ADD          Usage: --add [str] Add a new task
  --remove REMOVE    Usage: --remove [n or 'n,n,n' Remove task n or tasks 'n,n,n' from the task list
  --check CHECK      Usage: --check [n or 'n,n,n'] check off task n or tasks 'n,n,n' 
  --uncheck UNCHECK  Usage: --uncheck [n or 'n,n,n'] uncheck task n or tasks 'n,n,n' 
```

## Known Issues

- The pyinstaller build's boot time is very long. The workaround is to install from pip; an alternate solution may be a go rewrite.
- The tool only supports one page right now.
