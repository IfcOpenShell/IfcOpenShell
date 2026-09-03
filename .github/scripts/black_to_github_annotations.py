from __future__ import annotations

import json
import os
import sys
from typing import TypedDict

import github_action_utils as gha_utils


class Entry(TypedDict):
    location: Location


class Location(TypedDict):
    path: str
    lines: Lines


class Lines(TypedDict):
    begin: int
    end: int


json_data: list[Entry] = json.load(sys.stdin)

if os.getenv("RUNNER_DEBUG"):
    print("Debug: Black formatting JSON data:")
    print(json.dumps(json_data, indent=2))

for change in json_data:
    location = change["location"]
    path = location["path"]
    lines = location["lines"]
    gha_utils.error(
        f"Black formatting issue in {path}",
        title="Black Format Issue",
        file=path,
        line=lines["begin"],
        end_line=lines["end"],
    )
