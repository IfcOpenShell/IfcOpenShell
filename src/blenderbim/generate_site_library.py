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

import bpy
import ifcopenshell
import ifcopenshell.api


class LibraryGenerator:
    def generate(self):
        ifcopenshell.api.pre_listeners = {}
        ifcopenshell.api.post_listeners = {}

        self.file = ifcopenshell.api.run("project.create_file")
        self.project = ifcopenshell.api.run(
            "root.create_entity", self.file, ifc_class="IfcProject", name="BlenderBIM Demo"
        )
        self.library = ifcopenshell.api.run(
            "root.create_entity", self.file, ifc_class="IfcProjectLibrary", name="BlenderBIM Demo Library"
        )
        ifcopenshell.api.run(
            "project.assign_declaration", self.file, definition=self.library, relating_context=self.library
        )
        ifcopenshell.api.run("unit.assign_unit", self.file, length={"is_metric": True, "raw": "METERS"})
        ifcopenshell.api.run("context.add_context", self.file, context="Model")
        self.representations = {
            "body": ifcopenshell.api.run(
                "context.add_context", self.file, context="Model", subcontext="Body", target_view="MODEL_VIEW"
            ),
            "clearance": ifcopenshell.api.run(
                "context.add_context", self.file, context="Model", subcontext="Clearance", target_view="MODEL_VIEW"
            ),
        }
        ifcopenshell.api.run("context.add_context", self.file, context="Plan")
        self.annotation = ifcopenshell.api.run(
            "context.add_context", self.file, context="Model", subcontext="Annotation", target_view="PLAN_VIEW"
        )

        self.create_type("IfcBuildingElementProxyType", "Site Shed 3x6m", {"body": "Site Shed 3x6m"})
        self.create_type("IfcBuildingElementProxyType", "Site Shed 3x12m", {"body": "Site Shed 3x12m"})
        self.create_type(
            "IfcBuildingElementProxyType",
            "Mobile Crane 50T",
            {"body": "Mobile Crane 50T", "clearance": "Mobile Crane 50T - Clearance"},
        )

        self.file.write("blenderbim-site-library.ifc")

    def create_type(self, ifc_class, name, representations):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class, name=name)
        for rep_name, obj_name in representations.items():
            obj = bpy.data.objects.get(obj_name)
            representation = ifcopenshell.api.run(
                "geometry.add_representation",
                self.file,
                context=self.representations[rep_name],
                blender_object=obj,
                geometry=obj.data,
                total_items=max(1, len(obj.material_slots)),
            )
            ifcopenshell.api.run(
                "style.assign_representation_styles",
                self.file,
                **{
                    "shape_representation": representation,
                    "styles": [
                        ifcopenshell.api.run("style.add_style", self.file, **self.get_style_settings(s.material))
                        for s in obj.material_slots
                    ],
                },
            )
            ifcopenshell.api.run(
                "geometry.assign_representation", self.file, product=element, representation=representation
            )
        ifcopenshell.api.run("project.assign_declaration", self.file, definition=element, relating_context=self.library)

    def get_style_settings(self, material):
        transparency = material.diffuse_color[3]
        diffuse_colour = material.diffuse_color
        if (
            material.use_nodes
            and hasattr(material.node_tree, "nodes")
            and "Principled BSDF" in material.node_tree.nodes
        ):
            bsdf = material.node_tree.nodes["Principled BSDF"]
            transparency = bsdf.inputs["Alpha"].default_value
            diffuse_colour = bsdf.inputs["Base Color"].default_value
        transparency = 1 - transparency
        return {
            "name": material.name,
            "external_definition": None,
            "surface_colour": tuple(material.diffuse_color),
            "transparency": transparency,
            "diffuse_colour": tuple(diffuse_colour),
        }


LibraryGenerator().generate()
