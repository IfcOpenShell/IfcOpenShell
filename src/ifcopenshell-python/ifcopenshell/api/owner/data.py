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


class Data:
    is_loaded = False
    people = {}
    organisations = {}
    addresses = {}
    roles = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.people = {}
        cls.organisations = {}
        cls.addresses = {}
        cls.roles = {}

    @classmethod
    def load(cls, file):
        if not file:
            return
        cls.people = {}
        cls.organisations = {}
        cls.addresses = {}
        cls.roles = {}
        for person in file.by_type("IfcPerson"):
            data = person.get_info()
            data["is_engaged"] = bool(person.EngagedIn)
            cls.people[person.id()] = data

            roles = []
            if data["Roles"]:
                for role in data["Roles"]:
                    roles.append(role.id())
            data["Roles"] = roles

            addresses = []
            if data["Addresses"]:
                for address in data["Addresses"]:
                    addresses.append(address.id())
            data["Addresses"] = addresses

        for organisation in file.by_type("IfcOrganization"):
            data = organisation.get_info()
            data["is_engaged"] = (
                bool(organisation.IsRelatedBy) or bool(organisation.Relates) or bool(organisation.Engages)
            )
            cls.organisations[organisation.id()] = data

            roles = []
            if data["Roles"]:
                for role in data["Roles"]:
                    roles.append(role.id())
            data["Roles"] = roles

            addresses = []
            if data["Addresses"]:
                for address in data["Addresses"]:
                    addresses.append(address.id())
            data["Addresses"] = addresses

        for address in file.by_type("IfcAddress"):
            cls.addresses[address.id()] = address.get_info()

        for role in file.by_type("IfcActorRole"):
            cls.roles[role.id()] = role.get_info()
        cls.is_loaded = True
