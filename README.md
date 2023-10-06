# Building

This project uses the (Poetry)[https://python-poetry.org/] packaging system for building and managing dependecies. To get the dependencies:

1. Install Poetry `pip install poetry`
2. Create a virtual environment `python -m venv .venv`
3. Activate the virtual environment
  - For bash: `. .venv/bin/activate`
4. Install the dependencies `poetry install`

You can then build the pip distribution by running `poetry build`
