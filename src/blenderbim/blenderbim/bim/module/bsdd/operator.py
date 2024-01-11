# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
import bsdd
import blenderbim.tool as tool
from blenderbim.core import bsdd as core


class LoadBSDDDomains(bpy.types.Operator):
    bl_idname = "bim.load_bsdd_domains"
    bl_label = "Load bSDD Dictionaries"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_bsdd(bsdd.Client(), tool.Bsdd)
        return {"FINISHED"}


class SetActiveBSDDDictionary(bpy.types.Operator):
    bl_idname = "bim.set_active_bsdd_domain"
    bl_label = "Load bSDD Dictionary"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()
    uri: bpy.props.StringProperty()

    def execute(self, context):
        core.set_active_bsdd_dictionary(self.name, self.uri, tool.Bsdd)
        return {"FINISHED"}


class SearchBSDDClass(bpy.types.Operator):
    bl_idname = "bim.search_bsdd_classifications"
    bl_label = "Search bSDD Class"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        keyword = context.scene.BIMBSDDProperties.keyword
        core.search_class(keyword, bsdd.Client(), tool.Bsdd)
        return {"FINISHED"}


class GetBSDDClassificationProperties(bpy.types.Operator):
    bl_idname = "bim.get_bsdd_classification_properties"
    bl_label = "Search bSDD Classifications"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.get_class_properties(bsdd.Client(), tool.Bsdd)
        return {"FINISHED"}
