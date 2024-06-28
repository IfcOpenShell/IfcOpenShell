# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.
import ifcopenshell


def reorder_set_item(
    file: ifcopenshell.file, material_set: ifcopenshell.entity_instance, old_index: int = 0, new_index: int = 0
) -> None:
    """Reorders an item in a material set

    In some material sets, the order have meaning, like in a layer set. In
    other cases, it is purely for human convenience.

    :param material_set: The IfcMaterialSet which you want to reorder an
        item in.
    :type material_set: ifcopenshell.entity_instance
    :param old_index: The index of the item you want to move. This starts
        counting from 0.
    :type old_index: int
    :param new_index: The index of the new position the item will move to.
        This starts counting from 0.
    :type new_index: int
    :return: None
    :rtype: None

    Example:

    .. code:: python

        material_set = ifcopenshell.api.material.add_material_set(model,
            name="Window", set_type="IfcMaterialList")

        aluminium = ifcopenshell.api.material.add_material(model, name="AL01", category="aluminium")
        glass = ifcopenshell.api.material.add_material(model, name="GLZ01", category="glass")

        # Now let's use those materials as two items in our list.
        ifcopenshell.api.material.add_list_item(model, material_list=material_set, material=aluminium)
        ifcopenshell.api.material.add_list_item(model, material_list=material_set, material=glass)

        # Switch the order around, this has no meaning for a list, so this
        # is just for fun.
        ifcopenshell.api.material.reorder_set_item(model,
            material_set=material_set, old_index=0, new_index=1)
    """
    settings = {"material_set": material_set, "old_index": old_index, "new_index": new_index}

    if settings["material_set"].is_a("IfcMaterialConstituentSet"):
        set_name = "MaterialConstituents"
    elif settings["material_set"].is_a("IfcMaterialLayerSet"):
        set_name = "MaterialLayers"
    elif settings["material_set"].is_a("IfcMaterialProfileSet"):
        set_name = "MaterialProfiles"
    elif settings["material_set"].is_a("IfcMaterialList"):
        set_name = "Materials"
    items = list(getattr(settings["material_set"], set_name) or [])
    items.insert(settings["new_index"], items.pop(settings["old_index"]))
    setattr(settings["material_set"], set_name, items)
