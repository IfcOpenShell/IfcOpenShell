# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
from typing import Literal


MATERIAL_SET_TYPE = Literal[
    "IfcMaterialLayerSet",
    "IfcMaterialProfileSet",
    "IfcMaterialConstituentSet",
    "IfcMaterialList",
]


def add_material_set(
    file: ifcopenshell.file, name: str = "Unnamed", set_type: MATERIAL_SET_TYPE = "IfcMaterialConstituentSet"
) -> ifcopenshell.entity_instance:
    """Adds a new material set

    IFC allows you to state that objects are made out of multiple materials.
    These are known generically as material sets, but may also be called
    layered materials, composite materials, or other names in software.

    There are three types of material sets:

     - A layer set, used for layered construction such as walls, where the
       element is parametrically made out of extruded layers, each layer
       having a thickness defined. Even though this is known as a layer
       "set" it is still recommended to use it for all standared layered
       construction as it describes the intent of the element to be layered
       construction and thus can be used for parametric editing.
     - A profile set, used for profiled construction such as beams or
       columns, where the element is parametrically made out of one or more
       extruded profiles, where each profile may be parametric from a
       standard section (e.g. standardised steel profile) or an arbitrary
       shape (e.g. cold rolled sections, or skirtings, moldings, etc). Note
       that even though this is called a profile "set", it should still be
       used even if there is only a single profile. This is not available in
       IFC2X3.
     - A constituent set, used for arbitrary composite construction where
       the object is made out of multiple materials. The constituents may be
       explicitly defined via a shape, such as a window where the frame
       geometry is made from one material and the panel geometry is made
       from another material. Alternatively, the constituents may be
       represented in terms of percentages, such as in mixtures like
       concrete where there might be a percentage constituent of cement and
       another percentage constituent of binder. This is not available in
       IFC2X3.

    There is also a fourth material set known as a material list, which is a
    legacy type of set used by IFC2X3. It should not be used on IFC4 and
    above, and constituent sets should be used instead.

    :param name: The name of the material set, which may be purely
        descriptive or annotated in drawings. Defaults to "Unnamed".
    :param set_type: What type of set you want to create, chosen from
        IfcMaterialLayerSet, IfcMaterialProfileSet,
        IfcMaterialConstituentSet, or IfcMaterialList. Defaults to
        IfcMaterialConstituentSet.
    :return: The newly created material set element

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
    if set_type == "IfcMaterialLayerSet":
        return file.create_entity("IfcMaterialLayerSet", LayerSetName=name or "Unnamed")
    elif set_type == "IfcMaterialList":
        return file.create_entity("IfcMaterialList")
    return file.create_entity(set_type, Name=name or "Unnamed")
