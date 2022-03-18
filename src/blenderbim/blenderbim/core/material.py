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


def unlink_material(ifc, obj=None):
    ifc.unlink(obj=obj)


def add_default_material(ifc, material):
    obj = material.add_default_material_object()
    ifc.link(ifc.run("material.add_material", name="Default"), obj)
    return obj


def load_materials(material, material_type):
    material.import_material_definitions(material_type)
    material.enable_editing_materials()


def disable_editing_materials(material):
    material.disable_editing_materials()
