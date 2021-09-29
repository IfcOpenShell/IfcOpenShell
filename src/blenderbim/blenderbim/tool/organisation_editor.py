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

import bpy
import ifcopenshell.api
import blenderbim.core.tool
import blenderbim.bim.helper
import blenderbim.tool as tool


class OrganisationEditor(blenderbim.core.tool.organisation_editor.OrganisationEditor):
    @classmethod
    def set_organisation(cls, organisation):
        bpy.context.scene.BIMOwnerProperties.active_organisation_id = organisation.id()

    @classmethod
    def import_attributes(cls):
        organisation = tool.Ifc.get().by_id(bpy.context.scene.BIMOwnerProperties.active_organisation_id)
        props = bpy.context.scene.BIMOwnerProperties
        props.organisation_attributes.clear()

        blenderbim.bim.helper.import_attributes(
            "IfcOrganization", props.organisation_attributes, organisation.get_info()
        )

    @classmethod
    def clear_organisation(cls):
        bpy.context.scene.BIMOwnerProperties.active_organisation_id = 0

    @classmethod
    def export_attributes(cls):
        props = bpy.context.scene.BIMOwnerProperties
        attributes = blenderbim.bim.helper.export_attributes(props.organisation_attributes)
        return attributes

    @classmethod
    def get_organisation(cls):
        return tool.Ifc().get().by_id(bpy.context.scene.BIMOwnerProperties.active_organisation_id)
