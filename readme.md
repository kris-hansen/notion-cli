# *Notion CLI*

If you like this project, you might also like my other version of this [notion-cli-go] (https://github.com/kris-hansen/notion-cli-go) which is sort of the same but written in go for easier compilation and portability.

It's a CLI to track your tasks.

In a Notion page


In the tune of taskbook (https://github.com/klaussinani/taskbook) which is an npm package that I started using and really enjoyed; but I wanted something that was more portable across my devices and that I could also shared (i.e., it needed a back end).

I started looking at Notion for this, but wanted to stay in CLI land vs. having to task back to bright colours to check my code to do's.

Thus, this mini project was born!


Now uses the official Notion API!  [notion](https://developers.notion.com/) to access to the Notion page with the tasks. Previous versions used the unofficial API prior to the official API being released. This version is a rewrite to use the official API.

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

### Testing

To run the tests, run `make test`.

## Configuration

In order to run this tool, you need to define three environment variables:

- `NOTION_API_KEY` - This is the API token for the API client *make sure to share your Notion page with your integration*
- `NOTION_PAGE_ID` - This is the URL for the page (ex: https://notion.so/my-page/{pageID}) Here are some [tips] (https://developers.notion.com/docs/working-with-page-content#:~:text=Open%20the%20page%20in%20Notion,ends%20in%20a%20page%20ID.) for finding your page ID

To get a `NOTION_API_KEY` and make your task page available, you'll need to:

- Sign into Notion
- Visit [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
- Create a new integration
- Share your task page with the integration

See the Notion documentation for more details.

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
usage: notion [-h] {help,add_todo,list_todos,mark_checked,del_todo} ...

Manage ToDo blocks using the Notion API in your CLI.

positional arguments:
  {help,add_todo,list_todos,mark_checked,del_todo}
    help                Show this help message and exit
    add_todo            Add a new to-do item to the specified to-do block
    list_todos          List all to-do items in a to-do block
    mark_checked        Mark a to-do item as complete
    del_todo            Remove a to-do item from a to-do block

optional arguments:
  -h, --help            show this help message and exit
```

## Known Limitations

- The tool only supports one Notion page right now.
