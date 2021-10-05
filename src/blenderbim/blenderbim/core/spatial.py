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

import blenderbim.core


def assign_container(ifc, collector, container, surveyor, structure_obj=None, element_obj=None):
    if not container.can_contain(structure_obj, element_obj):
        return
    rel = ifc.run(
        "spatial.assign_container",
        product=ifc.get_entity(element_obj),
        relating_structure=ifc.get_entity(structure_obj),
    )
    blenderbim.core.geometry.edit_object_placement(ifc, surveyor, obj=element_obj)
    container.disable_editing(element_obj)
    collector.assign(element_obj)
    return rel


def enable_editing_container(container, obj=None):
    container.enable_editing(obj)
    container.import_containers()


def disable_editing_container(container, obj=None):
    container.disable_editing(obj)


def change_spatial_level(container, parent=None):
    container.import_containers(parent=parent)


def remove_container(ifc, collector, obj=None):
    ifc.run("spatial.remove_container", product=ifc.get_entity(obj))
    collector.assign(obj)
