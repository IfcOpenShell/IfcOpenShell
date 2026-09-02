# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 IfcOpenShell contributors
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

# This file was generated with the assistance of an AI coding tool.

# Exercises IfcConvert's XML serializer support for
# IfcRelAssociatesClassification / IfcClassification / IfcClassificationReference
# (see https://github.com/IfcOpenShell/IfcOpenShell/issues/556): every product's
# classification association should show up as a per-product xlink:href, and a
# top-level ifc.classifications section should contain each referenced
# IfcClassification(Reference) exactly once, with IFC4's hierarchical
# ReferencedSource chain walked and deduplicated.

import shutil
import subprocess
import xml.etree.ElementTree as ET

import pytest

import ifcopenshell
import ifcopenshell.guid

XLINK_HREF = "{http://www.w3.org/1999/xlink}href"

requires_ifcconvert = pytest.mark.skipif(shutil.which("IfcConvert") is None, reason="Requires IfcConvert in path")


def build_minimal_project(schema):
    f = ifcopenshell.file(schema=schema)

    # IfcPerson's identification attribute was renamed Id -> Identification in IFC4.
    person_id_attr = "Id" if schema == "IFC2X3" else "Identification"
    person = f.create_entity("IfcPerson", **{person_id_attr: "P1", "FamilyName": "Doe"})
    org = f.create_entity("IfcOrganization", Name="Acme")
    person_org = f.create_entity("IfcPersonAndOrganization", ThePerson=person, TheOrganization=org)
    app = f.create_entity(
        "IfcApplication",
        ApplicationDeveloper=org,
        Version="1.0",
        ApplicationFullName="Test",
        ApplicationIdentifier="Test",
    )
    owner_history = f.create_entity(
        "IfcOwnerHistory", OwningUser=person_org, OwningApplication=app, ChangeAction="ADDED", CreationDate=0
    )

    length_unit = f.create_entity("IfcSIUnit", UnitType="LENGTHUNIT", Name="METRE")
    unit_assignment = f.create_entity("IfcUnitAssignment", Units=[length_unit])

    context = f.create_entity(
        "IfcGeometricRepresentationContext",
        ContextType="Model",
        CoordinateSpaceDimension=3,
        Precision=1e-5,
        WorldCoordinateSystem=f.create_entity(
            "IfcAxis2Placement3D", Location=f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
        ),
    )

    project = f.create_entity(
        "IfcProject",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=owner_history,
        Name="Test Project",
        UnitsInContext=unit_assignment,
        RepresentationContexts=[context],
    )
    site = f.create_entity("IfcSite", GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner_history, Name="Site")
    building = f.create_entity(
        "IfcBuilding", GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner_history, Name="Building"
    )
    storey = f.create_entity(
        "IfcBuildingStorey", GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner_history, Name="Storey"
    )

    f.create_entity(
        "IfcRelAggregates",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=owner_history,
        RelatingObject=project,
        RelatedObjects=[site],
    )
    f.create_entity(
        "IfcRelAggregates",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=owner_history,
        RelatingObject=site,
        RelatedObjects=[building],
    )
    f.create_entity(
        "IfcRelAggregates",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=owner_history,
        RelatingObject=building,
        RelatedObjects=[storey],
    )

    return f, owner_history, storey


def contain_in_storey(f, owner_history, storey, elements):
    f.create_entity(
        "IfcRelContainedInSpatialStructure",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=owner_history,
        RelatedElements=elements,
        RelatingStructure=storey,
    )


def convert_to_xml(tmp_path, f, name):
    ifc_fn = tmp_path / f"{name}.ifc"
    xml_fn = tmp_path / f"{name}.xml"
    f.write(str(ifc_fn))
    subprocess.run(
        [shutil.which("IfcConvert") or "IfcConvert", "-y", str(ifc_fn), str(xml_fn)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return ET.parse(str(xml_fn)).getroot()


def assert_all_xlinks_resolve(root):
    ids = {el.attrib["id"] for el in root.iter() if "id" in el.attrib}
    hrefs = [el.attrib[XLINK_HREF] for el in root.iter() if XLINK_HREF in el.attrib]
    assert hrefs, "expected at least one xlink:href in the output"
    for href in hrefs:
        assert href.lstrip("#") in ids, f"unresolved xlink:href {href!r}"


class TestXmlClassificationSerialization:
    @requires_ifcconvert
    def test_ifc4_referenced_source_chain_is_walked_and_deduplicated(self, tmp_path):
        f, owner_history, storey = build_minimal_project("IFC4")

        wall1 = f.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner_history, Name="Wall-1")
        wall2 = f.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner_history, Name="Wall-2")
        contain_in_storey(f, owner_history, storey, [wall1, wall2])

        # Full/hierarchical classification: IfcClassification -> level1 -> level2 -> level3.
        classification = f.create_entity(
            "IfcClassification", Source="acme.example", Edition="2024", Name="Acme Classification System"
        )
        level1 = f.create_entity(
            "IfcClassificationReference", Identification="L1", Name="Level 1", ReferencedSource=classification
        )
        level2 = f.create_entity(
            "IfcClassificationReference", Identification="L1.2", Name="Level 2", ReferencedSource=level1
        )
        level3 = f.create_entity(
            "IfcClassificationReference", Identification="L1.2.3", Name="Level 3 (deepest)", ReferencedSource=level2
        )

        # wall1 is classified at the deepest level: walking ReferencedSource has
        # to visit level3 -> level2 -> level1 -> classification.
        f.create_entity(
            "IfcRelAssociatesClassification",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=owner_history,
            RelatedObjects=[wall1],
            RelatingClassification=level3,
        )
        # wall2 is classified directly at level2, which shares the level1 ->
        # classification tail with wall1's chain: this exercises dedup so that
        # level1/classification (and level2 itself) aren't emitted twice.
        f.create_entity(
            "IfcRelAssociatesClassification",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=owner_history,
            RelatedObjects=[wall2],
            RelatingClassification=level2,
        )

        root = convert_to_xml(tmp_path, f, "ifc4_classification_chain")
        assert_all_xlinks_resolve(root)

        classifications = root.find("classifications")
        assert classifications is not None

        # Exactly one node per unique classification entity: level1, level2,
        # level3 and the root classification - no duplicates despite two
        # associations both walking through level1/classification.
        emitted_ids = [el.attrib["id"] for el in classifications]
        assert len(emitted_ids) == len(set(emitted_ids)) == 4

        references_by_identification = {
            el.attrib.get("Identification"): el.attrib["id"]
            for el in classifications
            if el.tag == "IfcClassificationReference"
        }
        assert set(references_by_identification) == {"L1", "L1.2", "L1.2.3"}
        classification_ids = [el.attrib["id"] for el in classifications if el.tag == "IfcClassification"]
        assert len(classification_ids) == 1

        # Per-product references point at the specific node each product was
        # actually associated with, not just any classification node.
        def hrefs_for(product_name):
            product = root.find(f".//IfcWall[@Name='{product_name}']")
            assert product is not None
            return {
                child.attrib[XLINK_HREF].lstrip("#")
                for child in product
                if child.tag == "IfcClassificationReference" and XLINK_HREF in child.attrib
            }

        assert hrefs_for("Wall-1") == {references_by_identification["L1.2.3"]}
        assert hrefs_for("Wall-2") == {references_by_identification["L1.2"]}

    @requires_ifcconvert
    def test_ifc2x3_classification_reference_is_not_chained(self, tmp_path):
        # In IFC2X3, IfcClassificationReference.ReferencedSource can only point
        # directly to an IfcClassification (no reference-to-reference
        # chaining), unlike IFC4's IfcClassificationReferenceSelect.
        f, owner_history, storey = build_minimal_project("IFC2X3")

        wall = f.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner_history, Name="Wall-1")
        contain_in_storey(f, owner_history, storey, [wall])

        classification = f.create_entity(
            "IfcClassification", Source="acme.example", Edition="2024", Name="Acme Classification System"
        )
        reference = f.create_entity(
            "IfcClassificationReference", Name="Top-level reference", ReferencedSource=classification
        )
        f.create_entity(
            "IfcRelAssociatesClassification",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=owner_history,
            RelatedObjects=[wall],
            RelatingClassification=reference,
        )

        root = convert_to_xml(tmp_path, f, "ifc2x3_classification_direct")
        assert_all_xlinks_resolve(root)

        classifications = root.find("classifications")
        assert classifications is not None
        # Exactly the reference and the classification it points to - no
        # chaining is possible in IFC2X3, so no extra nodes are produced.
        assert len(list(classifications)) == 2
        tags = sorted(el.tag for el in classifications)
        assert tags == ["IfcClassification", "IfcClassificationReference"]

        product = root.find(".//IfcWall[@Name='Wall-1']")
        assert product is not None
        product_hrefs = {
            child.attrib[XLINK_HREF].lstrip("#")
            for child in product
            if child.tag == "IfcClassificationReference" and XLINK_HREF in child.attrib
        }
        reference_id = next(el.attrib["id"] for el in classifications if el.tag == "IfcClassificationReference")
        assert product_hrefs == {reference_id}


if __name__ == "__main__":
    pytest.main(["-x", __file__])
