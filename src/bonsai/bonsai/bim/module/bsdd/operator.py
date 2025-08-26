# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
import textwrap
import bpy
import bsdd
import bonsai.tool as tool
import ifcopenshell.api.pset
import ifcopenshell.util.element
from bonsai.core import bsdd as core
from typing import Any


class LoadBSDDDictionaries(bpy.types.Operator):
    bl_idname = "bim.load_bsdd_dictionaries"
    bl_label = "Load bSDD Dictionaries"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_bsdd(tool.Bsdd)
        return {"FINISHED"}


class SearchBSDDClassifications(bpy.types.Operator):
    bl_idname = "bim.search_bsdd_classifications"
    bl_label = "Search bSDD Class"
    bl_description = "Search for bSDD classes by the provided keyword"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        total = core.search_bsdd_class(tool.Bsdd, tool.Bsdd.get_bsdd_props().keyword)
        self.report({"INFO"}, f"{total} bSDD classes found.")
        return {"FINISHED"}


class ImportBSDDClasses(bpy.types.Operator):
    bl_idname = "bim.import_bsdd_classes"
    bl_label = "Import bSDD Classes"
    bl_description = "Load bSDD classes that apply to the current element"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        props = tool.Bsdd.get_bsdd_props()
        core.import_bsdd_classes(tool.Bsdd, self.obj, self.obj_type)
        self.report({"INFO"}, f"{len(props.classes)} bSDD classes found.")
        return {"FINISHED"}


class SearchBSDDProperties(bpy.types.Operator):
    bl_idname = "bim.search_bsdd_properties"
    bl_label = "Search bSDD Properties"
    bl_description = "Search for bSDD properties that apply to the current element"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        props = tool.Bsdd.get_bsdd_props()
        core.search_bsdd_properties(tool.Bsdd, tool.Bsdd.get_bsdd_props().keyword, self.obj, self.obj_type)
        self.report({"INFO"}, f"{len(props.properties)} bSDD properties found.")
        return {"FINISHED"}


class AddBSDDProperties(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_bsdd_properties"
    bl_label = "Add bSDD Properties"
    bl_description = "Add selected bSDD properties to the active object"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        props = tool.Bsdd.get_bsdd_props()
        if not props.selected_properties:
            cls.poll_message_set("No properties selected to add.")
            return False
        return True

    def _execute(self, context):
        self.file = tool.Ifc.get()
        bprops = tool.Bsdd.get_bsdd_props()

        psets: dict[str, dict[str, Any]] = {}
        for selected_property in bprops.selected_properties:
            psets.setdefault(selected_property.metadata, {})[selected_property.name] = selected_property.get_value()

        ifc_definition_id = tool.Blender.get_obj_ifc_definition_id(self.obj, self.obj_type, context)
        assert ifc_definition_id
        element = tool.Ifc.get().by_id(ifc_definition_id)

        current_psets = ifcopenshell.util.element.get_psets(element, verbose=True)
        for pset_name, properties in psets.items():
            if pset := current_psets.get(pset_name, None):
                pset = self.file.by_id(pset["id"])
            else:
                pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name=pset_name)
            ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties=properties)


class BIM_OT_show_bsdd_description(bpy.types.Operator):
    bl_idname = "bim.show_bsdd_description"
    bl_label = "bSDD Description"
    url: bpy.props.StringProperty()

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=450)

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        WIDTH = 80
        layout = self.layout
        wrapper = textwrap.TextWrapper(width=WIDTH)
        result = tool.Bsdd.get_bsdd_property(self.url)
        description = result.get("description") or ""
        definition = result.get("definition") or ""
        if description != definition:
            text = wrapper.wrap(f"Description : {description}")
            text.append("-" * (WIDTH - 15))
            text += wrapper.wrap(f"Definition : {definition}")
        else:
            text = wrapper.wrap(f"Description : {description}")
        for line in text:
            layout.label(text=line)
        if self.url:
            url_op = layout.operator("bim.open_uri", icon="URL", text="Online bSDD Documentation")
            url_op.uri = self.url
