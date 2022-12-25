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

# Note: it is the intent for you to override these with your own functions


def get_application(ifc):
    """Returns the application representing the authoring software

    It is expected for you to overload this function with your own
    IfcApplication. See ifcopenshell.api.owner.create_owner_history for details.

    :param ifc: The IFC file object that is being edited.
    :type ifc: ifcopenshell.file.file
    :return: The IfcApplication with metadata of the authoring software.
    :rtype: ifcopenshell.entity_instance.entity_instance
    """
    return (ifc.by_type("IfcApplication") or [None])[0]


def get_user(ifc):
    """Returns the active authoring user

    It is expected for you to overload this function with your own
    IfcApplication. See ifcopenshell.api.owner.create_owner_history for details.

    :param ifc: The IFC file object that is being edited.
    :type ifc: ifcopenshell.file.file
    :return: The IfcPersonAndOrganization with metadata of the authoring user.
    :rtype: ifcopenshell.entity_instance.entity_instance
    """
    return (ifc.by_type("IfcPersonAndOrganization") or [None])[0]


get_application_factory = get_application
get_application_backup = get_application
get_user_factory = get_user
get_user_backup = get_user


def factory_reset():
    """Reset the get_user and get_application functions to what came out of box

    When you are developing a custom application, you will typically override
    the get_user and get_application function to your own needs. Sometimes you
    want to reset it to before you monkey-patched it. This function does that
    reset.
    """
    global get_application_factory
    global get_application_backup
    global get_application
    global get_user_factory
    global get_user_backup
    global get_user
    get_application_backup = get_application
    get_application = get_application_factory
    get_user_backup = get_user
    get_user = get_user_factory


def restore():
    """Restore the get_user and get_application function prior to a reset

    In case you want to restore the monkey-patched version of get_user and
    get_application that existed before you applied a factory_reset(), this
    function will do that.
    """
    global get_application_factory
    global get_application_backup
    global get_application
    global get_user_factory
    global get_user_backup
    global get_user
    get_application = get_application_backup
    get_user = get_user_backup
