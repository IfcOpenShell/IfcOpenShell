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


class Usecase:
    def __init__(self, file, layer=None):
        """Removes a layer from a layer set

        Note that it is invalid to have zero items in a set, so you should leave
        at least one layer to ensure a valid IFC dataset.

        :param layer: The IfcMaterialLayer entity you want to remove
        :type layer: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Create a material set for steel stud partition walls.
            material_set = ifcopenshell.api.run("material.add_material_set", model,
                name="Window", set_type="IfcMaterialConstituentSet")

            gypsum = ifcopenshell.api.run("material.add_material", model, name="PB01", category="gypsum")
            steel = ifcopenshell.api.run("material.add_material", model, name="ST01", category="steel")

            # Now let's use those materials as three layers in our set, such
            # that the steel studs are sandwiched by the gypsum. Let's imagine
            # we're setting the layer thickness in millimeters.
            layer1 = ifcopenshell.api.run("material.add_layer", model, layer_set=material_set, material=gypsum)
            ifcopenshell.api.run("material.edit_layer", model, layer=layer1, attributes={"LayerThickness": 13})
            layer2 = ifcopenshell.api.run("material.add_layer", model, layer_set=material_set, material=steel)
            ifcopenshell.api.run("material.edit_layer", model, layer=layer2, attributes={"LayerThickness": 92})
            layer3 = ifcopenshell.api.run("material.add_layer", model, layer_set=material_set, material=gypsum)
            ifcopenshell.api.run("material.edit_layer", model, layer=layer3, attributes={"LayerThickness": 13})

            # Let's remove the last layer, such that the wall might be clad only
            # one one side such as to line a services riser.
            ifcopenshell.api.run("material.remove_layer", model, layer=layer3)
        """
        self.file = file
        self.settings = {"layer": layer}

    def execute(self):
        self.file.remove(self.settings["layer"])
