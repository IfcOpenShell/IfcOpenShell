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
    def __init__(self, file, layer_set=None, material=None, thickness=1., ventilated=None, name=None, description=None,
                 category=None, priority=None):
        """Adds a new layer to a layer set

        A layer represents a portion of material within a layered build up,
        defined by a thickness. Typical layered construction includes walls and
        slabs, where a wall might include a layer of finish, a layer of
        structure, a layer of insulation, and so on. It is recommended to define
        layered construction this way where it is unnecessary to define the
        exact geometry of how the wall or slab will be built, and it will
        instead be determined on site by a trade.

        Layers are defined in a particular order and thickness, so that it is
        clear which layer comes next.

        :param layer_set: The IfcMaterialLayerSet that the layer is part of. The
            layer set represents a group of layers. See
            ifcopenshell.api.material.add_material_set for more information on
            how to add a layer set.
        :type layer_set: ifcopenshell.entity_instance.entity_instance
        :param material: The IfcMaterial that the layer is made out of.
        :type material: ifcopenshell.entity_instance.entity_instance
        :param thickness: The thickness of the material layer.
        :type thickness: float
        :param ventilated: Indication of whether the material layer represents an air layer (or cavity).
        :type ventilated: bool
        :param name: The name by which the material layer is known.
        :type name: str
        :param description: Definition of the material layer in more descriptive terms than given by attributes Name or Category.
        :type description: str
        :param category: Category of the material layer, e.g. the role it has in the layer set it belongs to
            (such as 'load bearing', 'thermal insulation' etc.).
        :type category: str
        :param priority: The relative priority of the layer, expressed as normalised integer range [0..100].
            Controls how layers intersect in connections and corners of building elements.
        :type priority: int
        :return: The newly created IfcMaterialLayer
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # Let's imagine we have a wall type that has two layers of
            # gypsum with steel studs inside. Notice we are assigning to
            # the type only, as all occurrences of that type will automatically
            # inherit the material.
            wall_type = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWallType", name="WAL01")

            # First, let's create a material set. This will later be assigned
            # to our wall type element.
            material_set = ifcopenshell.api.run("material.add_material_set", model,
                name="GYP-ST-GYP", set_type="IfcMaterialLayerSet")

            # Let's create a few materials, it's important to also give them
            # categories. This makes it easy for model recipients to do things
            # like "show me everything made out of aluminium / concrete / steel
            # / glass / etc". The IFC specification states a list of categories
            # you can use.
            gypsum = ifcopenshell.api.run("material.add_material", model, name="PB01", category="gypsum")
            steel = ifcopenshell.api.run("material.add_material", model, name="ST01", category="steel")

            # Now let's use those materials as three layers in our set, such
            # that the steel studs are sandwiched by the gypsum. Let's imagine
            # we're setting the layer thickness in millimeters.
            layer = ifcopenshell.api.run("material.add_layer", model, layer_set=material_set, material=gypsum)
            ifcopenshell.api.run("material.edit_layer", model, layer=layer, attributes={"LayerThickness": 13})
            layer = ifcopenshell.api.run("material.add_layer", model, layer_set=material_set, material=steel)
            ifcopenshell.api.run("material.edit_layer", model, layer=layer, attributes={"LayerThickness": 92})
            layer = ifcopenshell.api.run("material.add_layer", model, layer_set=material_set, material=gypsum)
            ifcopenshell.api.run("material.edit_layer", model, layer=layer, attributes={"LayerThickness": 13})

            # Great! Let's assign our material set to our wall type.
            ifcopenshell.api.run("material.assign_material", model, product=wall_type, material=material_set)
        """
        self.file = file
        self.settings = {
            "layer_set": layer_set, "material": material, "thickness": thickness, "ventilated": ventilated,
            "name": name, "description": description, "category": category, "priority": priority
        }

    def execute(self):
        layers = list(self.settings["layer_set"].MaterialLayers or [])
        args = {"Material": self.settings["material"], "LayerThickness": self.settings["thickness"]}
        if self.settings["ventilated"]:
            args["IsVentilated"] = self.settings["ventilated"]
        if self.settings["name"]:
            args["Name"] = self.settings["name"]
        if self.settings["description"]:
            args["Description"] = self.settings["description"]
        if self.settings["category"]:
            args["Category"] = self.settings["category"]
        if self.settings["priority"]:
            args["Priority"] = self.settings["priority"]
        layer = self.file.create_entity("IfcMaterialLayer", **args)
        layers.append(layer)
        self.settings["layer_set"].MaterialLayers = layers
        return layer
