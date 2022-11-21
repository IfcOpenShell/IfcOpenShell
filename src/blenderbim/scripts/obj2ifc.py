# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.


# This can be packaged with `pyinstaller --onefile --hidden-import numpy --collect-all ifcopenshell --clean obj2ifc.py`
import argparse
import pywavefront
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.owner.settings
from pathlib import Path

import numpy as np

class Obj2Ifc:
    def __init__(self, path):
        self.path = path

    def execute(self, version="IFC4"):
        self.basename = Path(self.path).stem
        self.create_ifc_file(version)
        self.scene = pywavefront.Wavefront(self.path, create_materials=True, collect_faces=True)
        for mesh in self.scene.mesh_list:
            
            faces = mesh.faces
            ifc_faces = np.zeros([len(faces)], dtype=object)
            for i, face in enumerate(faces):
                ifc_faces[i] = (
                    self.file.createIfcFace(
                        [
                            self.file.createIfcFaceOuterBound(
                                self.file.createIfcPolyLoop(
                                    [self.file.createIfcCartesianPoint(self.scene.vertices[index]) for index in face]
                                ),
                                True,
                            )
                        ]
                    )
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
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "Name": mesh.name or self.basename,
                    "ObjectPlacement": self.placement,
                    "Representation": representation,
                }
            )
            ifcopenshell.api.run("spatial.assign_container", self.file, product=product, relating_structure=self.storey)
        self.file.write(self.path.replace(".obj", ".ifc"))

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
        lengthunit = ifcopenshell.api.run("unit.add_si_unit", self.file, unit_type="LENGTHUNIT", name="METRE")
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
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=site, relating_object=project)
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=building, relating_object=site)
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=self.storey, relating_object=building)

        self.origin = self.file.createIfcAxis2Placement3D(
            self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
            self.file.createIfcDirection((0.0, 0.0, 1.0)),
            self.file.createIfcDirection((1.0, 0.0, 0.0)),
        )
        self.placement = self.file.createIfcLocalPlacement(None, self.origin)
        self.history = ifcopenshell.api.run("owner.create_owner_history", self.file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Converts an OBJ to an IFC")
    parser.add_argument("obj", type=str, help="The OBJ file")
    args = parser.parse_args()

    obj2ifc = Obj2Ifc(args.obj)
    obj2ifc.execute()
