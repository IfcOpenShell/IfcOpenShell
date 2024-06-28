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


def add_layer(
    file: ifcopenshell.file, layer_set: ifcopenshell.entity_instance, material: ifcopenshell.entity_instance
) -> ifcopenshell.entity_instance:
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
    :type layer_set: ifcopenshell.entity_instance
    :param material: The IfcMaterial that the layer is made out of.
    :type material: ifcopenshell.entity_instance
    :return: The newly created IfcMaterialLayer
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        # Let's imagine we have a wall type that has two layers of
        # gypsum with steel studs inside. Notice we are assigning to
        # the type only, as all occurrences of that type will automatically
        # inherit the material.
        wall_type = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWallType", name="WAL01")

        # First, let's create a material set. This will later be assigned
        # to our wall type element.
        material_set = ifcopenshell.api.material.add_material_set(model,
            name="GYP-ST-GYP", set_type="IfcMaterialLayerSet")

        # Let's create a few materials, it's important to also give them
        # categories. This makes it easy for model recipients to do things
        # like "show me everything made out of aluminium / concrete / steel
        # / glass / etc". The IFC specification states a list of categories
        # you can use.
        gypsum = ifcopenshell.api.material.add_material(model, name="PB01", category="gypsum")
        steel = ifcopenshell.api.material.add_material(model, name="ST01", category="steel")

        # Now let's use those materials as three layers in our set, such
        # that the steel studs are sandwiched by the gypsum. Let's imagine
        # we're setting the layer thickness in millimeters.
        layer = ifcopenshell.api.material.add_layer(model, layer_set=material_set, material=gypsum)
        ifcopenshell.api.material.edit_layer(model, layer=layer, attributes={"LayerThickness": 13})
        layer = ifcopenshell.api.material.add_layer(model, layer_set=material_set, material=steel)
        ifcopenshell.api.material.edit_layer(model, layer=layer, attributes={"LayerThickness": 92})
        layer = ifcopenshell.api.material.add_layer(model, layer_set=material_set, material=gypsum)
        ifcopenshell.api.material.edit_layer(model, layer=layer, attributes={"LayerThickness": 13})

        # Great! Let's assign our material set to our wall type.
        ifcopenshell.api.material.assign_material(model, products=[wall_type], material=material_set)
    """
    settings = {"layer_set": layer_set, "material": material}

    layers = list(settings["layer_set"].MaterialLayers or [])
    layer = file.create_entity("IfcMaterialLayer", **{"Material": settings["material"], "LayerThickness": 1.0})
    layers.append(layer)
    settings["layer_set"].MaterialLayers = layers
    return layer
