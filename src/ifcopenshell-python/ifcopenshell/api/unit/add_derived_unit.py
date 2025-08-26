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
from typing import Any, Optional


def add_derived_unit(
    file: ifcopenshell.file, unit_type: str, userdefinedtype: str, attributes: dict[ifcopenshell.entity_instance, int]
) -> ifcopenshell.entity_instance:
    """Add a new Derive unit

    The supported types are ANGULARVELOCITYUNIT, AREADENSITYUNIT, COMPOUNDPLANEANGLEUNIT,
    DYNAMICVISCOSITYUNIT, HEATFLUXDENSITYUNIT, INTEGERCOUNTRATEUNIT, ISOTHERMALMOISTURECAPACITYUNIT,
    KINEMATICVISCOSITYUNIT, LINEARVELOCITYUNIT, MASSDENSITYUNIT, MASSFLOWRATEUNIT, MOISTUREDIFFUSIVITYUNIT,
    MOLECULARWEIGHTUNIT, SPECIFICHEATCAPACITYUNIT, THERMALADMITTANCEUNIT, THERMALCONDUCTANCEUNIT,
    THERMALRESISTANCEUNIT, THERMALTRANSMITTANCEUNIT, VAPORPERMEABILITYUNIT, VOLUMETRICFLOWRATEUNIT,
    ROTATIONALFREQUENCYUNIT, TORQUEUNIT, MOMENTOFINERTIAUNIT, LINEARMOMENTUNIT, LINEARFORCEUNIT,
    PLANARFORCEUNIT, MODULUSOFELASTICITYUNIT, SHEARMODULUSUNIT, LINEARSTIFFNESSUNIT, ROTATIONALSTIFFNESSUNIT,
    MODULUSOFSUBGRADEREACTIONUNIT, ACCELERATIONUNIT, CURVATUREUNIT, HEATINGVALUEUNIT, IONCONCENTRATIONUNIT,
    LUMINOUSINTENSITYDISTRIBUTIONUNIT, MASSPERLENGTHUNIT, MODULUSOFLINEARSUBGRADEREACTIONUNIT,
    MODULUSOFROTATIONALSUBGRADEREACTIONUNIT, PHUNIT, ROTATIONALMASSUNIT, SECTIONAREAINTEGRALUNIT,
    SECTIONMODULUSUNIT, SOUNDPOWERLEVELUNIT, SOUNDPOWERUNIT, SOUNDPRESSURELEVELUNIT, SOUNDPRESSUREUNIT,
    TEMPERATUREGRADIENTUNIT, TEMPERATURERATEOFCHANGEUNIT, THERMALEXPANSIONCOEFFICIENTUNIT, WARPINGCONSTANTUNIT,
    WARPINGMOMENTUNIT, USERDEFINED.

    In case of choosing USERDEFINED, the UserDefinedType parameter needs to be provided

    :param unit_type: A type of unit chosen from the list above. For
        example, choosing THERMALCONDUCTANCEUNIT will give you a Thermal conductance.
    :param userdefinedtype: The user defined type in case of choosing USERDEFINED, or None for no
        user defined type.
    :param attributes: a dictionary of attribute names and values.
    :return: The newly created IfcDerivedUnit

    Example:

    .. code:: python

        # Linear velocity in m/s
        length = ifcopenshell.api.unit.add_si_unit(model, unit_type="LENGTHUNIT")
        #2=IfcSIUnit(*,.LENGTHUNIT.,$,.METRE.)

        time = ifcopenshell.api.unit.add_si_unit(model, unit_type="TIMEUNIT")
        #4=IfcSIUnit(*,.TIMEUNIT.,$,.SECOND.)

        linear_velocity = ifcopenshell.api.unit.add_derived_unit(model, 'LINEARVELOCITY', None, {length : 1, time : -1})
        #10=IfcDerivedUnitElement(#2, 1)
        #11=IfcDerivedUnitElement(#4, -1)
        #12=IfcDerivedUnit((#10,#11),.LINEARVELOCITY.,$)

    """
    derive_unit_elements = []

    for named_unit in attributes:
        derive_unit_elements.append(
            file.create_entity("IfcDerivedUnitElement", Unit=named_unit, Exponent=attributes[named_unit])
        )

    return file.create_entity(
        "IfcDerivedUnit", Elements=derive_unit_elements, UnitType=unit_type, UserDefinedType=userdefinedtype
    )
