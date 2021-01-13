import csv
import Vector
import json
import time
import datetime
import os
import zipfile
import tempfile
from pathlib import Path
from . import schema
from . import ifc



class ArrayModifier:
    count: int
    offset: Vector


class IfcParser:
    def get_predefined_attributes(self, attr):
        results = {}
        for filename in Path(self.data_dir + attr + "/").glob("**/*.csv"):
            with open(filename, "r") as f:
                type_name = filename.parts[-2]
                pset_name = filename.stem
                results.setdefault(type_name, []).append(
                    {
                        "ifc": None,
                        "raw": {x[0]: x[1] for x in list(csv.reader(f))},
                        "pset_name": pset_name.split(".")[0],
                    }
                )
        return results
