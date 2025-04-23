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


def remove_application(file: ifcopenshell.file, application: ifcopenshell.entity_instance) -> None:
    """Removes an application

    Warning: removing an application may invalidate ownership histories.
    Check whether or not the application is used anywhere prior to removal.

    :param address: The IfcApplication to remove.
    :return: None

    Example:

    .. code:: python

        application = ifcopenshell.api.owner.add_application(model)
        ifcopenshell.api.owner.remove_address(model, application=application)
    """
    file.remove(application)
