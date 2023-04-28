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


class Usecase:
    def __init__(self, file, material_list=None, material_index=0):
        """Removes an item in an material list

        Note that it is invalid to have zero items in a list, so you should leave
        at least one item to ensure a valid IFC dataset.

        :param material_list: The IfcMaterialList entity you want to remove an
            item from.
        :type material_list: ifcopenshell.entity_instance.entity_instance
        :param material_index: The index of the material you want to remove from
            the list. Starts counting at 0. Defaults to 0.
        :type material_index: int, optional
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Create a material list for aluminium windows.
            material_set = ifcopenshell.api.run("material.add_material_set", model,
                name="Window", set_type="IfcMaterialMaterialList")

            aluminium = ifcopenshell.api.run("material.add_material", model, name="AL01", category="aluminium")
            glass = ifcopenshell.api.run("material.add_material", model, name="GLZ01", category="glass")

            # Now let's use those materials as two items in our list.
            ifcopenshell.api.run("material.add_list_item", model, material_list=material_set, material=aluminium)
            ifcopenshell.api.run("material.add_list_item", model, material_list=material_set, material=glass)

            # Let's remove the glass
            ifcopenshell.api.run("material.remove_list_item", model, material_list=material_set, material_index=1)
        """
        self.file = file
        self.settings = {"material_list": material_list, "material_index": material_index}

    def execute(self):
        materials = list(self.settings["material_list"].Materials)
        materials.pop(self.settings["material_index"])
        self.settings["material_list"].Materials = materials
