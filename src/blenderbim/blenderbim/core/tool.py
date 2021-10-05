# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import abc


class AddressEditor(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def set_address(cls, address):
        pass

    @classmethod
    @abc.abstractmethod
    def import_attributes(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def clear_address(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def get_address(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def export_attributes(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def add_attribute(cls, name):
        pass

    @classmethod
    @abc.abstractmethod
    def remove_attribute(cls, name, id):
        pass


class Blender(abc.ABC):
    pass


class Collector(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def assign(cls, obj):
        pass


class Container(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def can_contain(cls, structure_obj, element_obj):
        pass

    @classmethod
    @abc.abstractmethod
    def enable_editing(cls, obj):
        pass

    @classmethod
    @abc.abstractmethod
    def disable_editing(cls, obj):
        pass

    @classmethod
    @abc.abstractmethod
    def import_containers(cls, parent=None):
        pass


class ContextEditor(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def set_context(cls, context):
        pass

    @classmethod
    @abc.abstractmethod
    def import_attributes(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def clear_context(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def get_context(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def export_attributes(cls):
        pass


class Ifc(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def run(cls, command, **kwargs):
        pass

    @classmethod
    @abc.abstractmethod
    def get_entity(cls, obj):
        pass


class OrganisationEditor(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def set_organisation(cls, organisation):
        pass

    @classmethod
    @abc.abstractmethod
    def import_attributes(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def clear_organisation(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def get_organisation(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def export_attributes(cls):
        pass


class Owner(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def set_user(cls, user):
        pass

    @classmethod
    @abc.abstractmethod
    def get_user(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def clear_user(cls):
        pass


class PersonEditor(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def set_person(cls, person):
        pass

    @classmethod
    @abc.abstractmethod
    def import_attributes(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def clear_person(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def export_attributes(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def get_person(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def add_attribute(cls, name):
        pass

    @classmethod
    @abc.abstractmethod
    def remove_attribute(cls, name, id):
        pass


class RoleEditor(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def set_role(cls, role):
        pass

    @classmethod
    @abc.abstractmethod
    def import_attributes(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def clear_role(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def get_role(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def export_attributes(cls):
        pass


class Selector(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def set_active(cls, obj):
        pass


class Surveyor(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def get_absolute_matrix(cls, obj):
        pass


class Voider(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def can_void(cls, opening, element):
        pass

    @classmethod
    @abc.abstractmethod
    def void(cls, opening_obj, building_obj):
        pass

    @classmethod
    @abc.abstractmethod
    def unvoid(cls, opening_obj):
        pass

    @classmethod
    @abc.abstractmethod
    def set_void_display(cls, opening_obj):
        pass
