# IfcTester - IDS based model auditing
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcTester.
#
# IfcTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcTester.  If not, see <http://www.gnu.org/licenses/>.


import os
import time
import ifctester
import ifctester.reporter
import ifcopenshell
from flask import Flask, request, send_from_directory

app = Flask(__name__)


class Ifc:
    ifc = None
    filepath = None

    @classmethod
    def get(cls, filepath=None):
        if filepath is None or filepath == cls.filepath:
            return cls.ifc
        cls.filepath = filepath
        cls.ifc = ifcopenshell.open(filepath)
        return cls.ifc


@app.route("/")
def index():
    with open("www/index.html") as template:
        return template.read()


@app.route("/<path:asset>.<string:ext>")
def get_asset(asset, ext):
    if ext in ("js", "css"):
        return send_from_directory("www", asset + "." + ext)


@app.route("/audit", methods=["POST"])
def audit():
    filename = ifcopenshell.guid.new()
    ids_filepath = os.path.join("uploads", filename + ".ids")
    ifc_filepath = os.path.join("uploads", filename + ".ifc")
    request.files.get("ids").save(ids_filepath)
    request.files.get("ifc").save(ifc_filepath)

    start = time.time()
    specs = ifctester.open(ids_filepath)
    ifc = Ifc.get(ifc_filepath)
    print("Finished loading:", time.time() - start)
    start = time.time()
    specs.validate(ifc)
    print("Finished validating:", time.time() - start)
    start = time.time()

    os.remove(ids_filepath)
    os.remove(ifc_filepath)

    engine = ifctester.reporter.Json(specs)
    engine.report()
    return engine.to_string()
