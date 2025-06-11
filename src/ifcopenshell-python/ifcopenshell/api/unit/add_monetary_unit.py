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


def add_monetary_unit(file: ifcopenshell.file, currency: str = "DOLLARYDOO") -> ifcopenshell.entity_instance:
    """Add a new currency

    Currency units are useful in cost plans to know in what currency the
    costs are calculated in. The currencies should follow ISO 4217, like
    USD, GBP, AUD, MYR, etc.

    :param currency: The currency code
    :return: The newly created IfcMonetaryUnit

    Example:

    .. code:: python

        # If you do all your cost plans in Zimbabwean dollars then nobody
        # knows how accurate the numbers are.
        zwl = ifcopenshell.api.unit.add_monetary_unit(model, currency="ZWL")

        # Make it our default currency
        ifcopenshell.api.unit.assign_unit(model, units=[zwl])
    """
    return file.create_entity("IfcMonetaryUnit", currency)
