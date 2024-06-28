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
from typing import Any


def edit_layer_usage(file: ifcopenshell.file, usage: ifcopenshell.entity_instance, attributes: dict[str, Any]) -> None:
    """Edits the attributes of an IfcMaterialLayerSetUsage

    This is typically used to change the offset from the reference line to
    the layers.

    For more information about the attributes and data types of an
    IfcMaterialLayerSetUsage, consult the IFC documentation.

    :param usage: The IfcMaterialLayerSetUsage entity you want to edit
    :type usage: ifcopenshell.entity_instance
    :param attributes: a dictionary of attribute names and values.
    :type attributes: dict
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # Let's start with a simple concrete material
        concrete = ifcopenshell.api.material.add_material(model, name="CON01", category="concrete")

        # If we have a concrete wall, we should use a layer set. Again,
        # let's start with a wall type, not occurrences.
        wall_type = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWallType", name="WAL01")

        # Even though there is only one layer in our layer set, we still use
        # a layer set because it makes it clear that this is a layered
        # construction. Let's say it's a 200mm thick concrete layer.
        material_set = ifcopenshell.api.material.add_material_set(model,
            name="CON200", set_type="IfcMaterialLayerSet")
        layer = ifcopenshell.api.material.add_layer(model, layer_set=material_set, material=steel)
        ifcopenshell.api.material.edit_layer(model, layer=layer, attributes={"LayerThickness": 200})

        # Our wall type now has the layer set assigned to it
        ifcopenshell.api.material.assign_material(model,
            products=[wall_type], type="IfcMaterialLayerSet", material=material_set)

        # Let's imagine an occurrence of this wall type.
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(model, related_objects=[wall], relating_type=wall_type)

        # Our wall occurrence needs to have a "set usage" which describes
        # how the layers relate to a reference line (typically a 2D line
        # representing the extents of the wall). Usages are special since
        # they automatically detect the inherited material set from the
        # type. You'd write similar code for a profile set.
        rel = ifcopenshell.api.material.assign_material(model,
            products=[wall], type="IfcMaterialLayerSetUsage")

        # Let's change the offset from the reference line to be 200mm
        # instead of the default of 0mm.
        ifcopenshell.api.material.edit_layer_usage(model,
            usage=rel.RelatingMaterial, attributes={"OffsetFromReferenceLine": 200})
    """
    settings = {"usage": usage, "attributes": attributes}

    for name, value in settings["attributes"].items():
        setattr(settings["usage"], name, value)
