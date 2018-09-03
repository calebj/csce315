# GameDB

## Installation:
The project is a standard Python package, and can be installed with `python3.6 -m pip install .` or `python3.6 setup.py install`. To install only the requirements, use `python3.6 -m pip install -r requirements.txt`.

## Usage:
Invoke the entrypoint with `gamedb` once installed, or the module with `python3.6 -m gamedb`.
The latter command works even without having installed the package.

## Components:
- [`data/init.sql1](gamedb/data/init.sql) - DDL for the data tables and views
- [`__init__.py`](gamedb/__init__.py) - includes top-level imports for the package
- [`__main__.py`](gamedb/__main__.py) - invoked with `python -m gamedb`, calls `command.main()`
- [`command.py`](gamedb/command.py) - contains the interactive prompt loop and error display
- [`formatting.py`](gamedb/formatting.py) - simple formatting utilities for exceptions, tabulation, etc.
- [`gamedb.py`](gamedb/gamedb.py) - the main application class, connects the parser and db
- [`parser_base.py`](gamedb/parser_base.py) - base class for the command parser, help and decorator machinery
- [`parser_gamedb.py`](gamedb/parser_gamedb.py) - gamedb token + command definitions, logic and SQL queries
