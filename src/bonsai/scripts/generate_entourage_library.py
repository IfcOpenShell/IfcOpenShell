# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2024 Dion Moult <dion@thinkmoult.com>
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

import os
import bpy
import ifcopenshell
import ifcopenshell.api
import bonsai.tool as tool
from pathlib import Path


# When run from Blender
BLEND_DIR = os.path.dirname(bpy.data.filepath)
OUT_PATH = os.path.join(BLEND_DIR, "..", "bonsai", "bim", "data", "libraries", "IFC4 Entourage Library.ifc")


class LibraryGenerator:
    def generate(self, library_name, output_filename):
        ifcopenshell.api.pre_listeners = {}
        ifcopenshell.api.post_listeners = {}

        self.materials = {}

        self.file = ifcopenshell.api.run("project.create_file")
        self.project = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject", name=library_name)
        self.library = ifcopenshell.api.run(
            "root.create_entity", self.file, ifc_class="IfcProjectLibrary", name=library_name
        )
        ifcopenshell.api.run(
            "project.assign_declaration", self.file, definitions=[self.library], relating_context=self.project
        )
        unit = ifcopenshell.api.run("unit.add_si_unit", self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.run("unit.assign_unit", self.file, units=[unit])

        model = ifcopenshell.api.run("context.add_context", self.file, context_type="Model")
        plan = ifcopenshell.api.run("context.add_context", self.file, context_type="Plan")
        self.representations = {
            "Model/Body/MODEL_VIEW": ifcopenshell.api.run(
                "context.add_context",
                self.file,
                context_type="Model",
                context_identifier="Body",
                target_view="MODEL_VIEW",
                parent=model,
            ),
            "Plan/Body/PLAN_VIEW": ifcopenshell.api.run(
                "context.add_context",
                self.file,
                context_type="Plan",
                context_identifier="Body",
                target_view="PLAN_VIEW",
                parent=plan,
            ),
            "Model/Body/PLAN_VIEW": ifcopenshell.api.run(
                "context.add_context",
                self.file,
                context_type="Model",
                context_identifier="Body",
                target_view="PLAN_VIEW",
                parent=model,
            ),
            "Model/Body/SECTION_VIEW": ifcopenshell.api.run(
                "context.add_context",
                self.file,
                context_type="Model",
                context_identifier="Body",
                target_view="SECTION_VIEW",
                parent=model,
            ),
        }

        # Manually modeled trees
        for obj in bpy.data.objects:
            if not obj.type == "MESH":
                continue
            if "Plan/" in obj.name or "Model/" in obj.name:
                continue
            representations = {"Model/Body/MODEL_VIEW": obj.name}
            for rep_key in self.representations.keys():
                rep_obj = bpy.data.objects.get(obj.name + " " + rep_key)
                if rep_obj:
                    representations[rep_key] = rep_obj.name
            self.create_type("IfcBuildingElementProxyType", obj.name, representations)

        self.file.write(output_filename)

    def create_type(self, ifc_class, name, representations):
        element = ifcopenshell.api.run(
            "root.create_entity", self.file, ifc_class=ifc_class, predefined_type="ENTOURAGE", name=name
        )
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
            styles = []
            for slot in obj.material_slots:
                style = ifcopenshell.api.run("style.add_style", self.file, name=slot.material.name)
                ifcopenshell.api.run(
                    "style.add_surface_style",
                    self.file,
                    style=style,
                    ifc_class="IfcSurfaceStyleShading",
                    attributes=tool.Style.get_surface_shading_attributes(slot.material),
                )
                styles.append(style)
            if styles:
                ifcopenshell.api.run(
                    "style.assign_representation_styles", self.file, shape_representation=representation, styles=styles
                )
            ifcopenshell.api.run(
                "geometry.assign_representation", self.file, product=element, representation=representation
            )
        ifcopenshell.api.run(
            "project.assign_declaration", self.file, definitions=[element], relating_context=self.library
        )


if __name__ == "__main__":
    LibraryGenerator().generate("Entourage Assets Library", output_filename=OUT_PATH)
