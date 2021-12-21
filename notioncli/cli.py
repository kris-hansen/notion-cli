import argparse
from contextlib import contextmanager
from contextlib import redirect_stdout
from io import StringIO
import os
import sys

from notion.block import TodoBlock
from notion.client import NotionClient
from termcolor import colored
from termcolor import cprint


@contextmanager
def capture_stdout(output):
    stdout = sys.stdout
    sys.stdout = output
    try:
        yield
    finally:
        sys.stdout = stdout


class ConfigurationError(Exception):
    pass


def connect():
    try:
        client = NotionClient(token_v2=os.environ["NOTION_TOKEN"], monitor=False)
    except:
        raise ConfigurationError("Invalid or expired NOTION_TOKEN")

    return client


def get_page(client):
    if "NOTION_PAGE" not in os.environ:
        raise ConfigurationError("Missing NOTION_PAGE")
    return client.get_block(os.environ["NOTION_PAGE"])


def parse_task(taskn):
    taskn = str(taskn)
    if "," in string:
        taskn = string.split(",")
    return taskn


def check_env():
    has_token = "NOTION_TOKEN" in os.environ
    has_page = "NOTION_PAGE" in os.environ

    if not has_token:
        if has_page:
            raise ConfigurationError("Missing NOTION_TOKEN")
        else:
            raise ConfigurationError("Missing NOTION_TOKEN and NOTION_PAGE")


def list_tasks(page):
    n = 0
    cprint("\n\n{}\n".format(page.title), "white", attrs=["bold"])
    cprint("  # Status Description", "white", attrs=["underline"])
    for child in page.children:
        if child.type == "sub_header":
            cprint("[{}]".format(child.title), "green")
        elif child.type == "to_do":
            n += 1
            if child.checked:
                check = "[*]"
            else:
                check = "[ ]"
            cprint("  {}  {}  {}.".format(n, check, child.title), "green")
        else:
            pass

    cprint("\n{} total tasks".format(n), "white", attrs=["bold"])


def check_task(page, taskn):
    n = 0
    for child in page.children:
        if child.type == "to_do":
            n += 1
            for task in taskn:
                if n == int(task):
                    child.checked = True
        else:
            pass  # not a task
    cprint("{} marked as completed".format(taskn), "white", attrs=["bold"])


def uncheck_task(page, taskn):
    if isinstance(taskn, int):
        taskn = str(taskn)
    else:
        if "," in taskn:
            taskn = taskn.split(",")
    n = 0
    for child in page.children:
        n += 1
        try:
            for task in taskn:
                if n == int(task):
                    child.checked = False
        except:
            pass  # not a task
    cprint("{} marked as incomplete".format(taskn), "white", attrs=["bold"])


def add_task(page, task):
    newchild = page.children.add_new(TodoBlock, title=task)
    newchild.checked = False
    cprint("{} added as a new task".format(task))


def remove_task(page, taskn):

    if isinstance(taskn, int):
        taskn = str(taskn)
    else:
        if "," in taskn:
            taskn = taskn.split(",")
    n = 0
    for child in page.children:
        if child.type == "to_do":
            n += 1
            for task in taskn:
                if n == int(task):
                    child.remove()
        else:
            pass  # not a task
    cprint("{} removed.".format(taskn), "white", attrs=["bold"])


def main():
    parser = argparse.ArgumentParser(
        description="A Notion.so CLI \
    focused on simple task management"
    )
    parser.add_argument(
        "--env",
        nargs="?",
        const=True,
        default=False,
        help="Print current relevant environment variables",
    )
    parser.add_argument(
        "--list", nargs="?", const=True, default=False, help="List tasks"
    )
    parser.add_argument(
        "--add", default=False, type=str, help="Usage: --add [str] Add a new task"
    )
    parser.add_argument(
        "--remove",
        default=False,
        type=parse_task,
        help="Usage: --remove [n] (or n,n) remove task n from the task list",
    )
    parser.add_argument(
        "--check",
        default=False,
        type=parse_task,
        help="Usage: --check [n] (or n,n) mark n as completed",
    )
    parser.add_argument(
        "--uncheck",
        default=False,
        type=parse_task,
        help="Usage: --uncheck[n] (or n,n) to mark as incomplete",
    )

    args = parser.parse_args()

    try:

        check_env()

        page = get_page(connect())

        if args.env:
            cprint("\n Environment variables: \n", "white", attrs=["underline"])
            cprint(
                "    Notion.so token: {}\n".format(os.environ["NOTION_TOKEN"]), "green"
            )
            cprint(
                "    Notion.so page: {}\n".format(os.environ["NOTION_PAGE"]), "green"
            )
        if args.list:
            list_tasks(page)
        if args.add:
            add_task(page, str(args.add))
        if args.check:
            check_task(page, args.check)
        if args.uncheck:
            uncheck_task(args.uncheck)
        if args.remove:
            remove_task(args.remove)
    except Exception as exc:
        cprint(f"Flagrant error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
