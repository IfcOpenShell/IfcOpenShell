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
    def __init__(self, file, layer=None, attributes=None, material=None):
        """Edits the attributes of an IfcMaterialLayer

        For more information about the attributes and data types of an
        IfcMaterialLayer, consult the IFC documentation.

        :param layer: The IfcMaterialLayer entity you want to edit
        :type layer: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
        :param material: The IfcMaterial entity you want the layer to be made
            from.
        :type material: ifcopenshell.entity_instance.entity_instance, optional
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Let's create two materials typically used for steel stud partition
            # walls with gypsum lining.
            gypsum = ifcopenshell.api.run("material.add_material", model, name="PB01", category="gypsum")
            steel = ifcopenshell.api.run("material.add_material", model, name="ST01", category="steel")

            # Create a material layer set to contain our layers.
            material_set = ifcopenshell.api.run("material.add_material_set", model,
                name="GYP-ST-GYP", set_type="IfcMaterialLayerSet")

            # Now let's use those materials as three layers in our set, such
            # that the steel studs are sandwiched by the gypsum. Let's imagine
            # we're setting the layer thickness in millimeters.
            layer = ifcopenshell.api.run("material.add_layer", model, layer_set=material_set, material=gypsum)
            ifcopenshell.api.run("material.edit_layer", model, layer=layer, attributes={"LayerThickness": 13})
            layer = ifcopenshell.api.run("material.add_layer", model, layer_set=material_set, material=steel)
            ifcopenshell.api.run("material.edit_layer", model, layer=layer, attributes={"LayerThickness": 92})
            layer = ifcopenshell.api.run("material.add_layer", model, layer_set=material_set, material=gypsum)
            ifcopenshell.api.run("material.edit_layer", model, layer=layer, attributes={"LayerThickness": 13})
        """
        self.file = file
        self.settings = {"layer": layer, "attributes": attributes or {}, "material": material}

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["layer"], name, value)
        if self.settings["material"]:
            self.settings["layer"].Material = self.settings["material"]
