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


def copy_class(ifc, collector, root, obj=None):
    element = ifc.get_entity(obj)
    if not element:
        return
    element = ifc.run("root.copy_class", product=element)
    ifc.link(element, obj)
    relating_type = root.get_element_type(element)
    if relating_type and root.does_type_have_representations(relating_type):
        ifc.run("type.assign_type", related_object=element, relating_type=relating_type)
    else:
        root.run_geometry_add_representation(obj=obj, context=root.get_object_context(obj))
    collector.assign(obj)
    if root.is_opening_element(element):
        root.add_dynamic_opening_voids(element, obj)
