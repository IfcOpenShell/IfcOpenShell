import ifcopenshell
import ifcopenshell.api.owner
import ifcopenshell.api.root

from ...fixture_generate import normalize_header, pass_if, write_fixture

guid1 = "3pdqyORIn8KBHZAhhtJ72T"
guid2 = "1sEzC8v31DshmvW5t5P631"

for schema in ("IFC2X3", "IFC4", "IFC4X3"):
    for status in ("fail", "pass"):
        f = ifcopenshell.file(schema=schema)

        # setup IfcOwnerHistory
        if schema == "IFC2X3":
            ifcopenshell.api.owner.add_application(f)
            person = ifcopenshell.api.owner.add_person(f)
            organization = ifcopenshell.api.owner.add_organisation(f)
            ifcopenshell.api.owner.add_person_and_organisation(f, person=person, organisation=organization)

        wall1 = ifcopenshell.api.root.create_entity(f)
        wall2 = ifcopenshell.api.root.create_entity(f)
        wall1.GlobalId = guid1
        wall2.GlobalId = guid1 if status == "fail" else guid2

        normalize_header(f)
        write_fixture(f, __file__, pass_if(status == "pass"), f"duplicated-guids-{schema.lower()}")
