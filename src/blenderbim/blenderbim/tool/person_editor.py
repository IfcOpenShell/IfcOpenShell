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


class PersonEditor(blenderbim.core.tool.PersonEditor):
    @classmethod
    def set_person(cls, person):
        bpy.context.scene.BIMOwnerProperties.active_person_id = person.id()

    @classmethod
    def import_attributes(cls):
        person = tool.Ifc.get().by_id(bpy.context.scene.BIMOwnerProperties.active_person_id)
        props = bpy.context.scene.BIMOwnerProperties
        props.person_attributes.clear()
        props.middle_names.clear()
        props.prefix_titles.clear()
        props.suffix_titles.clear()

        def callback(name, prop, data):
            if name == "MiddleNames":
                for name in data["MiddleNames"] or []:
                    props.middle_names.add().name = name or ""
            if name == "PrefixTitles":
                for name in data["PrefixTitles"] or []:
                    props.prefix_titles.add().name = name or ""
            if name == "SuffixTitles":
                for name in data["SuffixTitles"] or []:
                    props.suffix_titles.add().name = name or ""

        blenderbim.bim.helper.import_attributes("IfcPerson", props.person_attributes, person.get_info(), callback)

    @classmethod
    def clear_person(cls):
        bpy.context.scene.BIMOwnerProperties.active_person_id = 0

    @classmethod
    def export_attributes(cls):
        props = bpy.context.scene.BIMOwnerProperties
        attributes = blenderbim.bim.helper.export_attributes(props.person_attributes)
        attributes["MiddleNames"] = [v.name for v in props.middle_names] if props.middle_names else None
        attributes["PrefixTitles"] = [v.name for v in props.prefix_titles] if props.prefix_titles else None
        attributes["SuffixTitles"] = [v.name for v in props.suffix_titles] if props.suffix_titles else None
        return attributes

    @classmethod
    def get_person(cls):
        return tool.Ifc().get().by_id(bpy.context.scene.BIMOwnerProperties.active_person_id)

    @classmethod
    def add_attribute(cls, name):
        if name == "MiddleNames":
            bpy.context.scene.BIMOwnerProperties.middle_names.add()
        elif name == "PrefixTitles":
            bpy.context.scene.BIMOwnerProperties.prefix_titles.add()
        elif name == "SuffixTitles":
            bpy.context.scene.BIMOwnerProperties.suffix_titles.add()

    @classmethod
    def remove_attribute(cls, name, id):
        if name == "MiddleNames":
            bpy.context.scene.BIMOwnerProperties.middle_names.remove(id)
        elif name == "PrefixTitles":
            bpy.context.scene.BIMOwnerProperties.prefix_titles.remove(id)
        elif name == "SuffixTitles":
            bpy.context.scene.BIMOwnerProperties.suffix_titles.remove(id)
