*Notion CLI*

It's a CLI.

For Notion.so

In the tune of taskbook (https://github.com/klaussinani/taskbook) which is an npm package that I started using and really enjoyed; but I wanted something that was more portable across my devices and that I could also shared (i.e., it needed a back end)

I started looking at Notion for this, but wanted to stay in CLI land vs. having to task back to bright colours to check my code to do's

Thus, this mini project was born

Installing: 

- Requirements - Python3 and pip install the requirements.txt dependencies 

Installation - you can run it directly with:

`$ python notioncli.py `

or

build it into an executable with:

`pyinstaller --onefile notioncli.py`

and then cp the binary from the ./dist folder to somewhere in your path

#Notes
- The pyinstaller packager does not work with conda/miniconda
- PY3.5 tested

#Future to-dos
- I think it needs to be faster, I have considered rewriting in go; not sure how much of the delay is related to runtime (pyinstaller packaging efficiency)
vs network/Notion 'API' delays
- Multiple pages, one per project

