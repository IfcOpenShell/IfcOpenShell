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

import bpy
import bsdd
import bonsai.tool as tool
from bonsai.core import bsdd as core


class LoadBSDDDomains(bpy.types.Operator):
    bl_idname = "bim.load_bsdd_domains"
    bl_label = "Load bSDD Dictionaries"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_bsdd(bsdd.Client(), tool.Bsdd)
        return {"FINISHED"}


class SetActiveBSDDDictionary(bpy.types.Operator):
    bl_idname = "bim.set_active_bsdd_domain"
    bl_label = "Set bSDD Dictionary as active"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()
    uri: bpy.props.StringProperty()

    def execute(self, context):
        core.set_active_bsdd_dictionary(self.name, self.uri, tool.Bsdd)
        return {"FINISHED"}


class SearchBSDDClass(bpy.types.Operator):
    bl_idname = "bim.search_bsdd_classifications"
    bl_label = "Search bSDD Class"
    bl_description = "Search for bSDD classes by the provided keyword"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        # Requirement by buildingSMART bSDD api.
        if len(context.scene.BIMBSDDProperties.keyword) < 3:
            cls.poll_message_set("Search query has to be at least 3 characters long.")
            return False
        return True

    def execute(self, context):
        keyword = context.scene.BIMBSDDProperties.keyword
        classes_found = core.search_class(keyword, bsdd.Client(), tool.Bsdd)
        self.report({"INFO"}, f"{classes_found} bSDD classes found for '{keyword}'.")
        return {"FINISHED"}


class GetBSDDClassificationProperties(bpy.types.Operator):
    bl_idname = "bim.get_bsdd_classification_properties"
    bl_label = "Search bSDD Class Properties"
    bl_description = "Search for bSDD class properties for the currently selected class"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        pset_data = core.get_class_properties(bsdd.Client(), tool.Bsdd)
        psets_found = len(pset_data)
        props_found = sum(len(pset) for pset in pset_data.values())
        self.report({"INFO"}, f"{psets_found} psets found ({props_found} props) for the active classification.")
        return {"FINISHED"}
