# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import os
import json
import ifcopenshell
import ifcopenshell.util.pset
import bpy
from pathlib import Path

cwd = os.path.dirname(os.path.realpath(__file__))


class IfcSchema:
    def __init__(self):
        self.schema_dir = Path(cwd).joinpath("schema")
        self.data_dir = Path(cwd).joinpath("data")
        # TODO: Make it less troublesome
        self.products = [
            "IfcElement",
            "IfcSpatialElement",
            "IfcGroup",
            "IfcStructural",
            "IfcPositioningElement",
            "IfcMaterialDefinition",
            "IfcParameterizedProfileDef",
            "IfcBoundaryCondition",
            "IfcElementType",
            "IfcAnnotation",
        ]
        self.elements = {}
        self.classification_files = {}
        self.classifications = {}
        self.load_pset_templates()
        self.load()

    def load_pset_templates(self):
        property_paths = self.data_dir.joinpath("pset").glob("*.ifc")
        # TODO: add IFC2X3 PsetQto template support
        self.psetqto = ifcopenshell.util.pset.get_template("IFC4")
        # Keep only the first template, which is the official buildingSMART one
        self.psetqto.templates = self.psetqto.templates[0:1]
        self.psetqto.get_applicable.cache_clear()
        self.psetqto.get_applicable_names.cache_clear()
        self.psetqto.get_by_name.cache_clear()
        for path in property_paths:
            self.psetqto.templates.append(ifcopenshell.open(path))

    def load(self):
        for product in self.products:
            with open(os.path.join(self.schema_dir, f"{product}_IFC4.json")) as f:
                setattr(self, product, json.load(f))
                self.elements.update(getattr(self, product))

    def load_classification(self, name, classification_index=None):
        if name not in self.classifications:
            if classification_index is not None:
                self.classification_files[name] = ifcopenshell.file.from_string(
                    bpy.context.scene.BIMProperties.classifications[classification_index].data
                )
            else:
                classification_path = os.path.join(self.schema_dir, "classifications", "{}.ifc".format(name))
                self.classification_files[name] = ifcopenshell.open(classification_path)
            self.classifications[name] = self.classification_files[name].by_type("IfcClassification")[0]
        classification = self.classifications[name]
        bpy.context.scene.BIMProperties.active_classification_name = self.classifications[name].Name
        return {"name": "", "description": "", "children": self.get_classification_references(classification)}

    def get_classification_references(self, classification):
        references = {}
        if not hasattr(classification, "HasReferences") or not classification.HasReferences:
            return references
        for reference in classification.HasReferences:
            references[reference.Identification] = {
                "location": reference.Location,
                "identification": reference.Identification,
                "name": reference.Name,
                "description": reference.Description,
                "children": self.get_classification_references(reference),
            }
        return references


ifc = IfcSchema()


def reload():
    global ifc
    ifc = IfcSchema()
