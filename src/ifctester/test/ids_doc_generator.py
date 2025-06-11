# IfcTester - IDS based model auditing
# Copyright (C) 2021-2022 Thomas Krijnen <thomas@aecgeeks.com>, Dion Moult <dion@thinkmoult.com>
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
import re
import uuid
import pytest
import functools
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.type
import ifcopenshell.api.unit
import ifcopenshell.guid
import ifctester
import test_facet
import test_ids
import numpy as np
from pathlib import Path
from xml.dom.minidom import parseString
from ifctester import ids
from ifcopenshell import validate

outdir = "build"


# Just for aesthetics so we don't keep on getting brand new GlobalIds on each generation
def regenerate_guids(ifc):
    ns = uuid.UUID("b59aa156-82a4-4b4c-a6e5-3d04a0236af9")
    for element in ifc.by_type("IfcRoot"):
        element.GlobalId = ifcopenshell.guid.compress(uuid.uuid5(ns, str(element.id())).hex)


class FacetDocGenerator:
    def __init__(self):
        self.facet = None
        self.testcases = {}

    def __call__(self, name, *, facet, inst, expected):
        if not name:
            return

        result = "pass" if expected is True else "fail"

        ifc = inst.wrapped_data.file
        if "GlobalId" not in name:
            regenerate_guids(ifc)

        # Validate the file created and loop over the issues, fixing them one by one.
        l = validate.json_logger()
        validate.validate(ifc, l)
        for issue in l.statements:
            if "GlobalId" in issue["message"]:
                issue["instance"].GlobalId = ifcopenshell.guid.new()
            elif "PredefinedType" in issue["message"]:
                ty = re.findall("\\(.+?\\)", issue["message"])[0][1:-1].split(", ")[0]
                issue["instance"].PredefinedType = ty
            elif "IfcMaterialList" in issue["message"]:
                issue["instance"].Materials = [ifc.createIfcMaterial("Concrete", None, "CONCRETE")]
            else:
                raise Exception("About to emit invalid example data:", issue)

        # ifc_text = "\n".join([f"{e} /* Testcase */" if e == inst else str(e) for e in f])
        lines = ifc.wrapped_data.to_string().split("\n")[7:-3]
        ifc_text = "\n".join([f"{l} /* Testcase */" if f"#{inst.id()}=" in l else l for l in lines])
        basename = f"{result}-" + re.sub("[^0-9a-zA-Z]", "_", name.lower())

        # Write IFC to disk
        ifc.write(os.path.join(outdir, "testcases", self.facet, f"{basename}.ifc"))

        # Create an IDS with the applicability selecting exactly
        # the entity type passed to us in `inst`.
        specs = ids.Ids(title=name)

        # todo: to resume IFC2X3 we need to ensure that entities and attributes are consistent with that schema in order to pass audit
        spec = ids.Specification(name=name, minOccurs=1, ifcVersion=["IFC4"])
        spec.applicability.append(ids.Entity(name=inst.is_a().upper()))
        spec.requirements.append(facet)
        specs.specifications.append(spec)

        # Write IDS to disk
        with open(os.path.join(outdir, "testcases", self.facet, f"{basename}.ids"), "w", encoding="utf-8") as ids_file:
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


class IdsDocGenerator:
    def __init__(self):
        self.testcases = []

    def __call__(self, name, ids, ifc, expected, applicable_entities=None, failed_entities=None):
        ids.validate(ifc)
        all_applicable = set()
        all_failures = set()
        if not applicable_entities:
            applicable_entities = []
        if not failed_entities:
            failed_entities = []
        for spec in ids.specifications:
            assert spec.status is expected
            all_applicable.update(spec.applicable_entities)
            for requirement in spec.requirements:
                if requirement.status is False:
                    all_failures.update(requirement.failed_entities)
        assert set(all_applicable) == set(applicable_entities)
        assert set(all_failures) == set(failed_entities)

        result = "pass" if expected is True else "fail"

        regenerate_guids(ifc)

        l = validate.json_logger()
        validate.validate(ifc, l)
        for issue in l.statements:
            raise Exception("About to emit invalid example data:", issue)

        lines = ifc.wrapped_data.to_string().split("\n")[7:-3]
        ifc_text = ""
        for i, line in enumerate(lines):
            step_id = int(line[1 : line.index("=")])
            element = ifc.by_id(step_id)
            newline = "" if i == 0 else "\n"
            if element in applicable_entities:
                pass_or_fail = "FAIL" if element in failed_entities else "PASS"
                ifc_text += f"{newline}[{pass_or_fail}] {line}"
            else:
                ifc_text += f"{newline}       {line}"
        basename = f"{result}-" + re.sub("[^0-9a-zA-Z]", "_", name.lower())

        # Write IFC to disk
        ifc.write(os.path.join(outdir, "testcases", "ids", f"{basename}.ifc"))

        # Write IDS to disk
        with open(os.path.join(outdir, "testcases", "ids", f"{basename}.ids"), "w", encoding="utf-8") as ids_file:
            ids_file.write(ids.to_string())

        reports = []
        for spec in ids.specifications:
            report = {"applicability": [], "requirements": [], "usage": spec.get_usage(), "status": spec.status}
            for facet in spec.applicability:
                report["applicability"].append(facet.to_string("applicability"))
            for facet in spec.requirements:
                report["requirements"].append(
                    {"status": facet.status, "text": facet.to_string("requirement"), "usage": facet.get_usage()}
                )
            reports.append(report)

        xml_text = "\n".join([l[4:] for l in ids.to_string().split("\n")[4:-1]]).replace("\t", "  ")

        self.testcases.append(
            {"name": name, "ids": xml_text, "ifc": ifc_text, "basename": basename, "result": result, "reports": reports}
        )


test_facet.run = FacetDocGenerator()
test_facet.set_facet = test_facet.run.set_facet
test_ids.run = IdsDocGenerator()

pytest.main(["-p", "no:pytest-blender"])

for facet, testcases in test_facet.run.testcases.items():
    with open(os.path.join(outdir, f"testcases-{facet}.md"), "w", encoding="utf-8") as f:
        write = functools.partial(print, file=f)
        write(f"# {facet.capitalize()} testcases")
        write()
        write(
            "These testcases are designed to help describe behaviour in edge cases and ambiguities. All valid IDS implementations must demonstrate identical behaviour to these test cases."
        )
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
            write(
                f"[Sample IDS](testcases/{facet}/{testcase['basename']}.ids) - [Sample IFC: {testcase['id']}](testcases/{facet}/{testcase['basename']}.ifc)"
            )
            write()

with open(os.path.join(outdir, f"testcases-ids.md"), "w", encoding="utf-8") as f:
    write = functools.partial(print, file=f)
    write(f"# IDS integration testcases")
    write()
    write(
        "These testcases are designed to help describe behaviour in edge cases and ambiguities. All valid IDS implementations must demonstrate identical behaviour to these test cases."
    )
    write()
    for testcase in test_ids.run.testcases:
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
        for report in testcase["reports"]:
            write("```")
            icon = "✔️" if report["status"] else "❌"
            write(f"# {icon} Specification ({report['usage']})")
            write("Applies to:")
            for facet in report["applicability"]:
                write(f" - {facet}")
            write("Requirements:")
            for facet in report["requirements"]:
                icon = "✔️" if facet["status"] else "❌"
                write(f" - {icon} {facet['text']} ({facet['usage']})")
            write("```")
            write()
        write(
            f"[Sample IDS](testcases/ids/{testcase['basename']}.ids) - [Sample IFC](testcases/ids/{testcase['basename']}.ifc)"
        )
        write()

specs = ifctester.ids.Ids(
    title="buildingSMART Sample IDS",
    copyright="buildingSMART",
    version="1.0.0",
    description="These are example specifications for those learning how to use IDS",
    author="foo@bar.com",
    date="2022-01-01",
    purpose="Contractual requirements",
)

spec = ifctester.ids.Specification(
    name="Project naming",
    ifcVersion=["IFC4"],
    description="Projects shall be named correctly for the purposes of identification, project archival, and model federation.",
    instructions="Each discipline is responsible for naming their own project.",
)
specs.specifications.append(spec)
spec.applicability.append(ifctester.ids.Entity(name="IFCPROJECT"))
spec.requirements.append(
    ifctester.ids.Attribute(
        name="Name",
        value="TEST",
        instructions="The project manager shall confirm the short project code with the client based on their real estate portfolio naming scheme.",
    )
)

spec = ifctester.ids.Specification(
    name="Fire rating",
    ifcVersion=["IFC4"],
    description="All objects must have a fire rating for building compliance checks and to know the protection strategies needed for any penetrations.",
    instructions="The architect is responsible for including this data.",
)
specs.specifications.append(spec)
spec.applicability.append(ifctester.ids.Entity(name="IFCWALLTYPE"))
restriction = ifctester.ids.Restriction(options={"pattern": "(-|[0-9]{2,3})\/(-|[0-9]{2,3})\/(-|[0-9]{2,3})"})
spec.requirements.append(
    ifctester.ids.Property(
        propertySet="Pset_WallCommon",
        name="FireRating",
        datatype="IfcLabel",
        value=restriction,
        instructions="Fire rating is specified using the Fire Resistance Level as defined in the Australian National Construction Code (NCC) 2019. Valid examples include -/-/-, -/120/120, and 60/60/60",
    )
)

ids_path = Path(outdir) / "library" / "sample.ids"
if not ids_path.parent.exists():
    ids_path.parent.mkdir()
specs.to_xml(str(ids_path))

# Create sample model
model = ifcopenshell.file()

project = ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject", name="My Project")
project.Name = "TEST"
ifcopenshell.api.unit.assign_unit(model)

context = ifcopenshell.api.context.add_context(model, context_type="Model")
body = ifcopenshell.api.context.add_context(
    model,
    context_type="Model",
    context_identifier="Body",
    target_view="MODEL_VIEW",
    parent=context,
)

site = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSite", name="My Site")
building = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuilding", name="Building A")
storey = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey", name="Ground Floor")

ifcopenshell.api.aggregate.assign_object(model, relating_object=project, products=[site])
ifcopenshell.api.aggregate.assign_object(model, relating_object=site, products=[building])
ifcopenshell.api.aggregate.assign_object(model, relating_object=building, products=[storey])

wall_types = []
for i in range(0, 4):
    wall_type = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWallType", name=f"DEMO{i + 1}")
    wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall", name=f"WALL {i + 1}")
    ifcopenshell.api.type.assign_type(model, related_objects=[wall], relating_type=wall_type)
    representation = ifcopenshell.api.geometry.add_wall_representation(
        model, context=body, length=5, height=3, thickness=(i + 1) * 0.05
    )
    if i == 0:
        pass
    elif i == 1:
        pset = ifcopenshell.api.pset.add_pset(model, product=wall_type, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(model, pset=pset, properties={"FireRating": "-/-/-"})
    elif i == 2:
        pset = ifcopenshell.api.pset.add_pset(model, product=wall_type, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(model, pset=pset, properties={"FireRating": "120/120/120"})
    elif i == 3:
        pset = ifcopenshell.api.pset.add_pset(model, product=wall_type, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(model, pset=pset, properties={"FireRating": "FOOBAR"})
    ifcopenshell.api.geometry.assign_representation(model, product=wall, representation=representation)
    location = np.eye(4)
    location[1][3] += i * 1
    ifcopenshell.api.geometry.edit_object_placement(model, product=wall, matrix=location)
    ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[wall])

model.write(os.path.join(outdir, "library", "sample.ifc"))
