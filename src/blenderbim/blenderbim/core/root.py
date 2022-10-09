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


def copy_class(ifc, collector, geometry, root, obj=None):
    element = ifc.get_entity(obj)
    if not element:
        return
    representation = root.get_object_representation(obj)
    new = ifc.run("root.copy_class", product=element)
    ifc.link(new, obj)
    relating_type = root.get_element_type(new)
    if relating_type and root.does_type_have_representations(relating_type):
        ifc.run("type.map_type_representations", related_object=new, relating_type=relating_type)
        root.link_object_data(ifc.get_object(relating_type), obj)
    elif representation:
        root.copy_representation(element, new)
        new_representation = root.get_element_representation(new, root.get_representation_context(representation))
        data = geometry.duplicate_object_data(obj)
        geometry.change_object_data(obj, data, is_global=True)
        geometry.rename_object(data, geometry.get_representation_name(new_representation))
        geometry.link(new_representation, data)
    collector.assign(obj)
    if root.is_opening_element(new):
        root.add_tracked_opening(obj)
    return new


def assign_class(
    ifc,
    collector,
    root,
    obj=None,
    ifc_class=None,
    predefined_type=None,
    should_add_representation=True,
    context=None,
    ifc_representation_class=None,
):
    if ifc.get_entity(obj):
        return

    name = root.get_object_name(obj)
    element = ifc.run("root.create_entity", ifc_class=ifc_class, predefined_type=predefined_type, name=name)
    root.set_object_name(obj, element)
    ifc.link(element, obj)

    if should_add_representation:
        root.run_geometry_add_representation(
            obj=obj, context=context, ifc_representation_class=ifc_representation_class, profile_set_usage=None
        )

    root.set_element_specific_display_settings(obj, element)

    collector.sync(obj)
    collector.assign(obj)
    return element
