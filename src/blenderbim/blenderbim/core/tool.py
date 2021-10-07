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
import inspect

# fmt: off
# pylint: skip-file

# This interface class and decorator is magic syntatic sugar to allow concise interface definitions
# If we didn't do this, Python is unnecessarily verbose, which I find distracting. Don't black this file :)
class Interface(abc.ABC): pass
def interface(cls):
    attrs = {n: classmethod(abc.abstractmethod(f)) for n, f in inspect.getmembers(cls, predicate=inspect.isfunction)}
    return type(cls.__name__, (Interface, cls), attrs)


@interface
class Aggregate:
    def can_aggregate(cls, relating_object, related_object): pass
    def disable_editing(cls, obj): pass
    def enable_editing(cls, obj): pass


@interface
class Blender: pass


@interface
class Collector:
    def assign(cls, obj): pass


@interface
class Container:
    def can_contain(cls, structure_obj, element_obj): pass
    def disable_editing(cls, obj): pass
    def enable_editing(cls, obj): pass
    def import_containers(cls, parent=None): pass


@interface
class Context:
    def clear_context(cls): pass
    def export_attributes(cls): pass
    def get_context(cls): pass
    def import_attributes(cls): pass
    def set_context(cls, context): pass


@interface
class Ifc:
    def get(cls): pass
    def get_entity(cls, obj): pass
    def link(cls, element, obj): pass
    def run(cls, command, **kwargs): pass
    def unlink(cls, element=None, obj=None): pass


@interface
class Owner:
    def add_address_attribute(cls, name): pass
    def add_person_attribute(cls, name): pass
    def clear_address(cls): pass
    def clear_organisation(cls): pass
    def clear_person(cls): pass
    def clear_role(cls): pass
    def clear_user(cls): pass
    def export_address_attributes(cls): pass
    def export_organisation_attributes(cls): pass
    def export_person_attributes(cls): pass
    def export_role_attributes(cls): pass
    def get_address(cls): pass
    def get_organisation(cls): pass
    def get_person(cls): pass
    def get_role(cls): pass
    def get_user(cls): pass
    def import_address_attributes(cls): pass
    def import_organisation_attributes(cls): pass
    def import_person_attributes(cls): pass
    def import_role_attributes(cls): pass
    def remove_address_attribute(cls, name, id): pass
    def remove_person_attribute(cls, name, id): pass
    def set_address(cls, address): pass
    def set_organisation(cls, organisation): pass
    def set_person(cls, person): pass
    def set_role(cls, role): pass
    def set_user(cls, user): pass


@interface
class Selector:
    def set_active(cls, obj): pass


@interface
class Style:
    def disable_editing(cls, obj): pass
    def enable_editing(cls, obj): pass
    def export_surface_attributes(cls, obj): pass
    def get_context(cls, obj): pass
    def get_name(cls, obj): pass
    def get_style(cls, obj): pass
    def get_surface_rendering_attributes(cls, obj): pass
    def get_surface_rendering_style(cls, obj): pass
    def get_surface_shading_attributes(cls, obj): pass
    def get_surface_shading_style(cls, obj): pass
    def import_surface_attributes(cls, style, obj): pass
    def link(cls, style, obj): pass
    def unlink(cls, obj): pass


@interface
class Surveyor:
    def get_absolute_matrix(cls, obj): pass


@interface
class Voider:
    def can_void(cls, opening, element): pass
    def set_void_display(cls, opening_obj): pass
    def unvoid(cls, opening_obj): pass
    def void(cls, opening_obj, building_obj): pass
