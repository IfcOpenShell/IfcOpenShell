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


def copy_property_to_selection(ifc, pset, is_pset=True, obj=None, pset_name=None, prop_name=None, prop_value=None):
    element = ifc.get_entity(obj)
    if not element:
        return
    ifc_pset = pset.get_element_pset(element, pset_name)
    if not ifc_pset:
        ifc_pset = ifc.run("pset.add_pset" if is_pset else "pset.add_qto", product=element, name=pset_name)
    if is_pset:
        ifc.run("pset.edit_pset", pset=ifc_pset, properties={prop_name: prop_value})
    else:
        ifc.run("pset.edit_qto", qto=ifc_pset, properties={prop_name: prop_value})
