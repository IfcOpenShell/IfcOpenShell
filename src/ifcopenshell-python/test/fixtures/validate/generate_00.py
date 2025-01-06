import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.owner
from pathlib import Path


guid1 = "3pdqyORIn8KBHZAhhtJ72T"
guid2 = "1sEzC8v31DshmvW5t5P631"

for schema in ("ifc2x3", "ifc4", "ifc4x3"):
    for status in ("fail", "pass"):
        f = ifcopenshell.file(schema=schema)

        # setup IfcOwnerHistory
        if schema == "ifc2x3":
            ifcopenshell.api.owner.add_application(f)
            person = ifcopenshell.api.owner.add_person(f)
            organization = ifcopenshell.api.owner.add_organisation(f)
            ifcopenshell.api.owner.add_person_and_organisation(f, person=person, organisation=organization)

        wall1 = ifcopenshell.api.root.create_entity(f)
        wall2 = ifcopenshell.api.root.create_entity(f)
        wall1.GlobalId = guid1
        wall2.GlobalId = guid1 if status == "fail" else guid2

        filename = f"{status}-{'not-' if status == 'pass' else ''}duplicated-guids-{schema}.ifc"
        f.write(Path(__file__).parent / filename)
