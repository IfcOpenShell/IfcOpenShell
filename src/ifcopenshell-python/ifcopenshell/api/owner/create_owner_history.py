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

import time
import ifcopenshell
import ifcopenshell.api.owner.settings
from typing import Union


def create_owner_history(file: ifcopenshell.file) -> Union[ifcopenshell.entity_instance, None]:
    """Creates a new owner history indicating an element was added

    Any object in IFC with a unique ID and name (such as physical products,
    tasks, calendars, etc) may have an owner associated with it. An owner is
    a liable person and/or organisation which a bit of metadata indicating
    whether they have created the object, edited the object, when the change
    was made, and which application they used.

    IFC does not offer a comprehensive specification for version control and
    change tracking, as this is completely out of scope. However this
    similar ability allows IFC to satisfy legal requirements where object
    ownership, responsibilities, and permissions must be specified.
    Recording the owner is mandatory in IFC2X3 but optional in IFC4. It is
    not recommended to store this ownership data in IFC4 unless a legal
    requirement is in place.

    Because owner tracking is mandatory in IFC2X3, be aware that some
    configuration may be required to work correctly. Read on.

    To track the owner, at a minimum we have to know the application that
    the element was authored from, as well as the user (person and
    organisation) that made the change. The IfcOpenShell API is a low level
    software library and will not know what application the API is being
    called from, and nor does it have the responsibility to manage the
    "active user" making edits, which may be as simple as hardcoding it to
    "Bob" or even be as complex as integration with a CDE's authentication
    system. As a result, the developer responsible to integrate with
    IfcOpenShell is expected to overload the
    ifcopenshell.api.owner.settings.get_user and
    ifcopenshell.api.owner.settings.get_application functions.

    It is not necessary to call this function directly if you are already
    using other API calls. It is a low level function only available if you
    are writing your own advanced scripts and want to take advantage of the
    easier ownership tracking.

    :return: The newly created IfcOwnerHistory element or `None` if it's
        not IFC2X3 and user or application is not found in the current project.
    :rtype: Union[ifcopenshell.entity_instance, None]

    Example:

    .. code:: python

        # Let's imagine we're writing a small script, not large enough to be
        # its own fully branded application. In this case, let's use the
        # default application which is prepopulated with "IfcOpenShell" as
        # the name and version.
        application = ifcopenshell.api.owner.add_application(model)

        # Let's imagine we run this as an automated QA process in an
        # architectural firm. However, the results must be signed off by the
        # registered architect who is liable for the project.
        person = ifcopenshell.api.owner.add_person(model,
            identification="LPARTEE", family_name="Partee", given_name="Leeable")
        organisation = ifcopenshell.api.owner.add_organisation(model,
            identification="AWB", name="Architects Without Ballpens")
        user = ifcopenshell.api.owner.add_person_and_organisation(model,
            person=person, organisation=organisation)

        # Let's configure our owner settings to hardcode always returning
        # the application and user. In theory, you could build complex user
        # access control lookup functions here, but this is simple enough.
        ifcopenshell.api.owner.settings.get_user = lambda x: user
        ifcopenshell.api.owner.settings.get_application = lambda x: application

        # We've finished our ownership setup. Now let's start our script and
        # create a space. Notice we don't actually call
        # create_owner_history at all. This is already automatically handled
        # by the API when necessary. Under the hood, the API is actually
        # running this code on the IfcSpace element:
        # element.OwnerHistory = ifcopenshell.api.owner.create_owner_history(model)
        space = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSpace")
    """
    settings = {}

    user = ifcopenshell.api.owner.settings.get_user(file)
    if file.schema != "IFC2X3" and not user:
        return
    application = ifcopenshell.api.owner.settings.get_application(file)
    if file.schema != "IFC2X3" and not application:
        return
    return file.create_entity(
        "IfcOwnerHistory",
        OwningUser=user,
        OwningApplication=application,
        State="READWRITE",
        ChangeAction="ADDED",
        LastModifiedDate=int(time.time()),
        LastModifyingUser=user,
        LastModifyingApplication=application,
        CreationDate=int(time.time()),
    )
