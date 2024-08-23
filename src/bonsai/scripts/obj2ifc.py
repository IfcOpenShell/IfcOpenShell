# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.


# This can be packaged with `pyinstaller --onefile --hidden-import numpy --collect-all ifcopenshell --clean obj2ifc.py`
import argparse
import pywavefront
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.owner.settings
import ifcopenshell.guid
from pathlib import Path

import numpy as np


class Obj2Ifc:
    def __init__(self, paths, outfile):
        self.paths = paths
        self.outfile = outfile
        self.basename = Path(outfile).stem

    def execute(self, version="IFC4"):
        self.create_ifc_file(version)
        for path in self.paths:
            self.path = path
            self._execute()

    def _execute(self):

        self.scene = pywavefront.Wavefront(self.path, create_materials=True, collect_faces=True)
        for mesh in self.scene.mesh_list:

            faces = mesh.faces
            ifc_faces = np.zeros([len(faces)], dtype=object)
            for i, face in enumerate(faces):
                ifc_faces[i] = self.file.createIfcFace(
                    [
                        self.file.createIfcFaceOuterBound(
                            self.file.createIfcPolyLoop(
                                [
                                    self.file.createIfcCartesianPoint(self.get_coordinates(self.scene.vertices[index]))
                                    for index in face
                                ]
                            ),
                            True,
                        )
                    ]
                )
            representation = self.file.createIfcProductDefinitionShape(
                None,
                None,
                [
                    self.file.createIfcShapeRepresentation(
                        self.context,
                        "Body",
                        "Brep",
                        [self.file.createIfcFacetedBrep(self.file.createIfcClosedShell(ifc_faces.tolist()))],
                    )
                ],
            )
            product = self.file.create_entity(
                "IfcBuildingElementProxy",
                GlobalId=ifcopenshell.guid.new(),
                Name=mesh.name or self.basename,
                Representation=representation,
            )
            ifcopenshell.api.run(
                "spatial.assign_container", self.file, products=[product], relating_structure=self.storey
            )
            product.ObjectPlacement = self.placement

        self.file.write(self.outfile)

    def get_coordinates(self, coordinates):
        # OBJ swaps Y and Z axis
        return [coordinates[0], -coordinates[2], coordinates[1]]

    def create_ifc_file(self, version):
        self.file = ifcopenshell.api.run("project.create_file", version=version)
        person = ifcopenshell.api.run("owner.add_person", self.file)
        person[0] = person.GivenName = None
        person.FamilyName = "user"
        org = ifcopenshell.api.run("owner.add_organisation", self.file)
        org[0] = None
        org.Name = "template"
        user = ifcopenshell.api.run("owner.add_person_and_organisation", self.file, person=person, organisation=org)
        application = ifcopenshell.api.run("owner.add_application", self.file)
        ifcopenshell.api.owner.settings.get_user = lambda ifc: user
        ifcopenshell.api.owner.settings.get_application = lambda ifc: application

        project = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject", name=self.basename)
        lengthunit = ifcopenshell.api.run("unit.add_si_unit", self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.run("unit.assign_unit", self.file, units=[lengthunit])
        model = ifcopenshell.api.run("context.add_context", self.file, context_type="Model")
        self.context = ifcopenshell.api.run(
            "context.add_context",
            self.file,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model,
        )
        site = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSite", name="My Site")
        building = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding", name="My Building")
        self.storey = ifcopenshell.api.run(
            "root.create_entity", self.file, ifc_class="IfcBuildingStorey", name="My Storey"
        )
        ifcopenshell.api.run("aggregate.assign_object", self.file, products=[site], relating_object=project)
        ifcopenshell.api.run("aggregate.assign_object", self.file, products=[building], relating_object=site)
        ifcopenshell.api.run("aggregate.assign_object", self.file, products=[self.storey], relating_object=building)

        ifcopenshell.api.run("geometry.edit_object_placement", self.file, product=site)
        ifcopenshell.api.run("geometry.edit_object_placement", self.file, product=building)
        ifcopenshell.api.run("geometry.edit_object_placement", self.file, product=self.storey)

        self.origin = self.file.createIfcAxis2Placement3D(
            self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
            self.file.createIfcDirection((0.0, 0.0, 1.0)),
            self.file.createIfcDirection((1.0, 0.0, 0.0)),
        )
        self.placement = self.file.createIfcLocalPlacement(self.storey.ObjectPlacement, self.origin)
        self.history = ifcopenshell.api.run("owner.create_owner_history", self.file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Converts an OBJ to an IFC")
    parser.add_argument("obj", type=str, nargs="+", help="One or more OBJ files")
    parser.add_argument("-o", "--output", type=str, help="The output file to save the patched IFC", default="out.ifc")
    args = parser.parse_args()

    obj2ifc = Obj2Ifc(args.obj, args.output)
    obj2ifc.execute()
