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

import ifcopenshell.util.unit
from typing import Optional


def add_si_unit(
    file: ifcopenshell.file, unit_type: str = "LENGTHUNIT", prefix: Optional[str] = None
) -> ifcopenshell.entity_instance:
    """Add a new SI unit

    The supported types are ABSORBEDDOSEUNIT, AMOUNTOFSUBSTANCEUNIT,
    AREAUNIT, DOSEEQUIVALENTUNIT, ELECTRICCAPACITANCEUNIT,
    ELECTRICCHARGEUNIT, ELECTRICCONDUCTANCEUNIT, ELECTRICCURRENTUNIT,
    ELECTRICRESISTANCEUNIT, ELECTRICVOLTAGEUNIT, ENERGYUNIT, FORCEUNIT,
    FREQUENCYUNIT, ILLUMINANCEUNIT, INDUCTANCEUNIT, LENGTHUNIT,
    LUMINOUSFLUXUNIT, LUMINOUSINTENSITYUNIT, MAGNETICFLUXDENSITYUNIT,
    MAGNETICFLUXUNIT, MASSUNIT, PLANEANGLEUNIT, POWERUNIT, PRESSUREUNIT,
    RADIOACTIVITYUNIT, SOLIDANGLEUNIT, THERMODYNAMICTEMPERATUREUNIT,
    TIMEUNIT, VOLUMEUNIT.

    Prefixes supported are ATTO, CENTI, DECA, DECI, EXA, FEMTO, GIGA, HECTO,
    KILO, MEGA, MICRO, MILLI, NANO, PETA, PICO, TERA.

    :param unit_type: A type of unit chosen from the list above. For
        example, choosing LENGTHUNIT will give you a metre.
    :type unit_type: str
    :param prefix: A prefix chosen from the list above, or None for no
        prefix.
    :type prefix: str,optional
    :return: The newly created IfcSIUnit
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        # Millimeters and square meters
        length = ifcopenshell.api.unit.add_si_unit(model, unit_type="LENGTHUNIT", prefix="MILLI")
        area = ifcopenshell.api.unit.add_si_unit(model, unit_type="AREAUNIT")

        # Make it our default units, if we are doing a metric building
        ifcopenshell.api.unit.assign_unit(model, units=[length, area])
    """
    settings = {"unit_type": unit_type, "prefix": prefix}

    name = ifcopenshell.util.unit.si_type_names.get(settings["unit_type"], None)
    return file.create_entity("IfcSIUnit", UnitType=settings["unit_type"], Name=name, Prefix=settings["prefix"])
