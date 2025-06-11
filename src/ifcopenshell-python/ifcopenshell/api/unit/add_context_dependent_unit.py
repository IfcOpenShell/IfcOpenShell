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


def add_context_dependent_unit(
    file: ifcopenshell.file,
    unit_type: str = "USERDEFINED",
    name: str = "THINGAMAJIG",
    dimensions: tuple[int, int, int, int, int, int, int] = (0, 0, 0, 0, 0, 0, 0),
) -> ifcopenshell.entity_instance:
    """Add a new arbitrary unit that can only be interpreted in a project specific context

    Occasionally the construction industry uses arbitrary units to quantify
    objects, like "pairs" of door hardware, "palettes" or "boxes" of fixings
    or equipment.

    :param unit_type: Typically should be left as USERDEFINED, unless for
        some bizarre reason you are redefining something you could use a
        sensible normal unit for. In that case, firstly stop whatever you're
        doing and have a hard think about your life, and then if life really
        is going that badly for you, check out the IFC docs for IfcUnitEnum.
    :param name: Give your unit a name. X what? X bananas?
    :param dimensions: Units typically measure one of 7 fundamental physical
        dimensions: length, mass, time, electric current, temperature,
        substance amount, or luminous intensity. These are represented as a
        list of 7 integers, representing the exponents of each one of these
        dimensions. For example, a length unit is (1, 0, 0, 0, 0, 0, 0),
        where as an area unit is (2, 0, 0, 0, 0, 0, 0). A unit of meters per
        second is (1, 0, -1, 0, 0, 0, 0). For context dependent units, it is
        recommended to leave this as the default of (0, 0, 0, 0, 0, 0, 0).
    :return: The new IfcContextDependentUnit

    Example:

    .. code:: python

        # Boxes of things
        ifcopenshell.api.unit.add_context_dependent_unit(model, name="BOXES")
    """
    return file.create_entity(
        "IfcContextDependentUnit",
        Dimensions=file.createIfcDimensionalExponents(*dimensions),
        UnitType=unit_type,
        Name=name,
    )
