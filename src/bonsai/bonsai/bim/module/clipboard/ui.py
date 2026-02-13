# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2025 Dion Moult <dion@thinkmoult.com>
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
import json
import bpy
from bpy.types import Panel
import ifcopenshell
import ifcopenshell.util.element
import bonsai.tool as tool


class BIM_PT_tab_clipboard(Panel):
    bl_idname = "BIM_PT_tab_clipboard"
    bl_label = "Clipboard"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}
    bim_tab_name = "QUALITY"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname):
            return True

    def draw(self, context):
        layout = self.layout
        
        # Clipboard operations
        row = layout.row(align=True)
        row.operator("bim.copy_to_clipboard", text="Copy", icon="COPYDOWN")
        row.operator("bim.paste_from_clipboard", text="Paste", icon="PASTEDOWN")
        
        # Show clipboard status - files are in shared data directory for cross-file operations
        clipboard_json = tool.Blender.get_data_dir_path("bonsai_clipboard.json").__str__()
        clipboard_ifc = tool.Blender.get_data_dir_path("bonsai_clipboard.ifc").__str__()
        
        if os.path.exists(clipboard_json) and os.path.exists(clipboard_ifc):
            with open(clipboard_json, "r") as f:
                data = json.load(f)
            
            # Load the library IFC file to get detailed info
            library = ifcopenshell.open(clipboard_ifc)
            
            # Collect statistics
            product_classes = {}
            product_types = set()
            materials = set()
            surface_styles = set()
            
            for elem_data in data.get('elements', []):
                elem = library.by_guid(elem_data['global_id'])
                
                # Count product classes
                elem_class = elem.is_a()
                product_classes[elem_class] = product_classes.get(elem_class, 0) + 1
                
                # Collect types
                elem_type = ifcopenshell.util.element.get_type(elem)
                if elem_type:
                    type_name = f"{elem_type.is_a()}"
                    if elem_type.Name:
                        type_name += f": {elem_type.Name}"
                    product_types.add(type_name)
                
                # Collect materials
                material = ifcopenshell.util.element.get_material(elem)
                if material:
                    mat_name = getattr(material, 'Name', None) or material.is_a()
                    materials.add(mat_name)
            
            # Collect all surface styles in library
            for style in library.by_type("IfcSurfaceStyle"):
                if style.Name:
                    surface_styles.add(style.Name)
            
            # Display summary
            box = layout.box()
            box.label(text="Clipboard Contents:", icon="INFO")
            box.label(text=f"Schema: {data.get('schema', 'Unknown')}")
            
            props = context.scene.BIMClipboardProperties
            
            # Products summary with dropdown
            section = props.get_section("products")
            prod_box = box.box()
            row = prod_box.row()
            row.prop(
                section,
                "is_expanded",
                icon="TRIA_DOWN" if section and section.is_expanded else "TRIA_RIGHT",
                emboss=False,
                text=f"Products: {len(data.get('elements', []))}",
            )
            if section and section.is_expanded:
                col = prod_box.column(align=True)
                for elem_class, count in sorted(product_classes.items()):
                    col.label(text=f"  {elem_class}: {count}")
            
            # Product types summary with dropdown
            if product_types:
                section = props.get_section("product_types")
                type_box = box.box()
                row = type_box.row()
                row.prop(
                    section,
                    "is_expanded",
                    icon="TRIA_DOWN" if section and section.is_expanded else "TRIA_RIGHT",
                    emboss=False,
                    text=f"Product Types: {len(product_types)}",
                )
                if section and section.is_expanded:
                    col = type_box.column(align=True)
                    for product_type in sorted(list(product_types)):
                        col.label(text=f"  {product_type}")
            
            # Materials summary with dropdown
            if materials:
                section = props.get_section("materials")
                mat_box = box.box()
                row = mat_box.row()
                row.prop(
                    section,
                    "is_expanded",
                    icon="TRIA_DOWN" if section and section.is_expanded else "TRIA_RIGHT",
                    emboss=False,
                    text=f"Materials: {len(materials)}",
                )
                if section and section.is_expanded:
                    col = mat_box.column(align=True)
                    for material in sorted(list(materials)):
                        col.label(text=f"  {material}")
            
            # Surface styles summary with dropdown
            if surface_styles:
                section = props.get_section("surface_styles")
                style_box = box.box()
                row = style_box.row()
                row.prop(
                    section,
                    "is_expanded",
                    icon="TRIA_DOWN" if section and section.is_expanded else "TRIA_RIGHT",
                    emboss=False,
                    text=f"Surface Styles: {len(surface_styles)}",
                )
                if section and section.is_expanded:
                    col = style_box.column(align=True)
                    for style in sorted(list(surface_styles)):
                        col.label(text=f"  {style}")
        else:
            layout.label(text="Clipboard is empty", icon="BLANK1")
