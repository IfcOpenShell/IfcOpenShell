# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell
import ifcopenshell.guid
import ezdxf


class Dxf2Ifc:
    def execute(self):
        self.create_ifc_file()
        doc = ezdxf.readfile("input.dxf")
        model = doc.modelspace()
        products = []
        for entity in model:
            print(entity)
            if entity.get_mode() == "AcDbPolyFaceMesh":
                ifc_faces = []
                for face in entity.faces():
                    ifc_faces.append(
                        self.file.createIfcFace(
                            [
                                self.file.createIfcFaceOuterBound(
                                    self.file.createIfcPolyLoop(
                                        [
                                            self.file.createIfcCartesianPoint((face[index].dxf.location))
                                            for index in range(len(face) - 1)
                                        ]
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
                            self.subcontext,
                            "Body",
                            "Brep",
                            [self.file.createIfcFacetedBrep(self.file.createIfcClosedShell(ifc_faces))],
                        )
                    ],
                )
                products.append(
                    self.file.create_entity(
                        "IfcBuildingElementProxy",
                        **{
                            "GlobalId": ifcopenshell.guid.new(),
                            "Name": entity.dxf.layer,
                            "ObjectPlacement": self.placement,
                            "Representation": representation,
                        }
                    )
                )
            else:
                print("Not yet implemented")
        self.file.createIfcRelContainedInSpatialStructure(
            ifcopenshell.guid.new(), None, None, None, products, self.site
        )
        self.file.write("test.ifc")

    def create_ifc_file(self):
        self.file = ifcopenshell.file()
        units = self.file.createIfcUnitAssignment([self.file.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")])
        self.origin = self.file.createIfcAxis2Placement3D(
            self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
            self.file.createIfcDirection((0.0, 0.0, 1.0)),
            self.file.createIfcDirection((1.0, 0.0, 0.0)),
        )
        self.placement = self.file.createIfcLocalPlacement(None, self.origin)
        self.context = self.file.createIfcGeometricRepresentationContext(None, "Model", 3, 1.0e-05, self.origin)
        self.subcontext = self.file.createIfcGeometricRepresentationSubcontext(
            "Body", "Model", None, None, None, None, self.context, None, "MODEL_VIEW", None
        )
        self.project = self.file.create_entity(
            "IfcProject",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "Name": "DXF Conversion",
                "RepresentationContexts": [self.context],
                "UnitsInContext": units,
            }
        )
        self.site = self.file.create_entity(
            "IfcSite",
            **{"GlobalId": ifcopenshell.guid.new(), "Name": "DXF Conversion Site", "ObjectPlacement": self.placement}
        )
        self.file.createIfcRelAggregates(ifcopenshell.guid.new(), None, None, None, self.project, [self.site])


dxf2ifc = Dxf2Ifc()
dxf2ifc.execute()
