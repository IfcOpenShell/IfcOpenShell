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
    def __init__(self, file, currency="DOLLARYDOO"):
        """Add a new currency

        Currency units are useful in cost plans to know in what currency the
        costs are calculated in. The currencies should follow ISO 4217, like
        USD, GBP, AUD, MYR, etc.

        :param currency: The currency code
        :type currency: str
        :return: The newly created IfcMonetaryUnit
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # If you do all your cost plans in Zimbabwean dollars then nobody
            # knows how accurate the numbers are.
            zwl = ifcopenshell.api.run("unit.add_monetary_unit", model, currency="ZWL")

            # Make it our default currency
            ifcopenshell.api.run("unit.assign_unit", model, units=[zwl])
        """
        self.file = file
        self.settings = {"currency": currency}

    def execute(self):
        return self.file.create_entity("IfcMonetaryUnit", self.settings["currency"])
