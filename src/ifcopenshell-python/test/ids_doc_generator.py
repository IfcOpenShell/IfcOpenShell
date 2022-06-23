# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import unittest
import functools
import itertools
import ifcopenshell
import test_ids
from xml.dom.minidom import parseString
from ifcopenshell import ids, template, validate

outdir = "build"


class DocGenerator:
    def __init__(self):
        self.facet = None
        self.testcases = {}

    def __call__(self, name, *, facet, inst, expected):
        if not name:
            return

        result = "pass" if expected is True else "fail"

        f = inst.wrapped_data.file
        instances = list(f)

        # Validate the file created and loop over the issues, fixing them
        # one by one.
        l = validate.json_logger()
        validate.validate(f, l)
        for issue in l.statements:
            if "GlobalId" in issue["message"]:
                issue["instance"].GlobalId = ifcopenshell.guid.new()

            elif "PredefinedType" in issue["message"]:
                ty = re.findall("\\(.+?\\)", issue["message"])[0][1:-1].split(", ")[0]
                issue["instance"].PredefinedType = ty
            elif "IfcMaterialList" in issue["message"]:
                issue["instance"].Materials = [f.createIfcMaterial("Concrete", None, "CONCRETE")]
            else:
                raise Exception("About to emit invalid example data:", issue)

        ifc_text = "\n".join([f"{e} /* Testcase */" if e == inst else str(e) for e in f])
        basename = f"{result}-" + re.sub("[^0-9a-zA-Z]", "_", name.lower())

        # Write IFC to disk
        f.write(os.path.join(outdir, f"{basename}.ifc"))

        # Create an IDS with the applicability selecting exactly
        # the entity type passed to us in `inst`.
        specs = ids.ids(title=name)
        spec = ids.specification(name=name)
        spec.add_applicability(ids.entity.create(name=inst.is_a()))
        spec.add_requirement(facet)
        specs.specifications.append(spec)

        # Write IDS to disk
        with open(os.path.join(outdir, f"{basename}.ids"), "w", encoding="utf-8") as ids_file:
            ids_file.write(specs.to_string())

        xml_text = "\n".join(
            l
            for l in parseString(specs.to_string())
            .getElementsByTagName("requirements")[0]
            .childNodes[1]
            .toprettyxml()
            .split("\n")
            if l.strip()
        ).replace("\t", "  ")

        self.testcases.setdefault(self.facet, []).append(
            {"name": name, "ids": xml_text, "ifc": ifc_text, "basename": basename, "result": result, "id": inst.id()}
        )

        assert bool(facet(inst)) is expected

    def set_facet(self, facet):
        self.facet = facet


test_ids.run = DocGenerator()
test_ids.set_facet = test_ids.run.set_facet

suite = unittest.TestLoader().discover(".", pattern="test_ids.py")
result = unittest.TextTestRunner(verbosity=2).run(suite)

for facet, testcases in test_ids.run.testcases.items():
    with open(os.path.join(outdir, f"testcases-{facet}.md"), "w") as f:
        write = functools.partial(print, file=f)
        write(f"# {facet.capitalize()} testcases")
        write()
        write("These testcases are designed to help describe behaviour in edge cases and ambiguities. All valid IDS implementations must demonstrate identical behaviour to these test cases.")
        write()
        for testcase in testcases:
            write(f"## [{testcase['result'].upper()}] {testcase['name']}")
            write()
            write("~~~xml")
            write(testcase["ids"])
            write("~~~")
            write()
            write("~~~lua")
            write(testcase["ifc"])
            write("~~~")
            write()
            write(f"[Sample IDS]({testcase['basename']}.ids) - [Sample IFC: {testcase['id']}]({testcase['basename']}.ifc)")
            write()
