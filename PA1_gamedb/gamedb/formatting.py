"Formatting helper functions"

import sys
from tabulate import tabulate
from typing import Iterable, Sequence


def row_counter(rows: Sequence) -> Iterable[int]:
    "Returns an iterator of row numbers, for pretty tables."
    return range(1, len(rows) + 1)


def generate_numbered_table(rows, headers: Sequence[str] = ()) -> str:
    "Adds a number column to the table and returns the tabulate output"
    new_headers = ["#"]
    new_headers.extend(headers)
    return tabulate(rows, headers=new_headers, showindex=row_counter(rows))


def print_err(err: str) -> None:
    "Central error formatting"
    print("ERROR:", err, file=sys.stderr)


def get_initials(inputstr: str) -> str:
    """
    Returns the first character of each whitespace-seperated word in inputstr,
    with the form A.B.C.
    """
    initials = (w[0].upper() for w in inputstr.split())
    return "".join("%c." % c for c in initials)
