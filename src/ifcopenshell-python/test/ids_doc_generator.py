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

class spec_generator:
    cases = []

    def __call__(self, name, *, facet, inst, expected):
        if not name:
            return

        fail_or_pass = "pass" if expected is True else "fail"

        # Create an IFC file with the instance in `inst` passed to us
        # based on an IFC file template with project and units.
        f = template.create()
        instances = [f.add(inst)]
        for nm in inst.wrapped_data.get_inverse_attribute_names():
            for v in getattr(inst, nm):
                instances.append(f.add(v))

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
                raise Exception("About to emit invalid example data")

        ifc_text = "\n".join(
            map(str, {inst: None for inst in itertools.chain.from_iterable(map(f.traverse, instances))}.keys())
        )

        basename = f"{fail_or_pass}-" + re.sub("[^0-9a-zA-Z]", "_", name.lower())

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

        self.cases.append({
            "name": name, "ids": xml_text, "ifc": ifc_text, "basename": basename, "result": fail_or_pass
        })

        assert bool(facet(inst)) is expected


test_ids.case = spec_generator()

suite = unittest.TestLoader().discover('.', pattern='test_ids.py')
result = unittest.TextTestRunner(verbosity=2).run(suite)

with open(os.path.join(outdir, "spec.md"), "w") as f:
    for c in test_ids.case.cases:
        write = functools.partial(print, file=f)
        write(f"## [{c['result'].upper()}] {c['name']}")
        write()
        write("~~~xml")
        write(c['ids'])
        write("~~~")
        write()
        write("~~~lua")
        write(c['ifc'])
        write("~~~")
        write()
        write(f"[Sample IDS]({c['basename']}.ids) - [Sample IFC]({c['basename']}.ifc)")
        write()
