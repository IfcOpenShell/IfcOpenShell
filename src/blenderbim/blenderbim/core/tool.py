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
class Brick:
    def add_brick_breadcrumb(cls): pass
    def clear_brick_browser(cls): pass
    def clear_project(cls): pass
    def get_item_class(cls, item): pass
    def import_brick_classes(cls, brick_class): pass
    def import_brick_items(cls, brick_class): pass
    def load_brick_file(cls, filepath): pass
    def pop_brick_breadcrumb(cls): pass
    def select_browser_item(cls, item): pass
    def set_active_brick_class(cls, brick_class): pass


@interface
class Collector:
    def assign(cls, obj): pass
    def sync(cls, obj): pass


@interface
class Context:
    def clear_context(cls): pass
    def export_attributes(cls): pass
    def get_context(cls): pass
    def import_attributes(cls): pass
    def set_context(cls, context): pass


@interface
class Geometry:
    def change_object_data(cls, obj, data, is_global=False): pass
    def clear_modifiers(cls, obj): pass
    def create_dynamic_voids(cls, obj): pass
    def delete_data(cls, data): pass
    def does_object_have_mesh_with_faces(cls, obj): pass
    def duplicate_object_data(cls, obj): pass
    def get_cartesian_point_coordinate_offset(cls, obj): pass
    def get_element_type(cls, element): pass
    def get_elements_of_type(cls, type): pass
    def get_ifc_representation_class(cls, element, representation): pass
    def get_object_data(cls, obj): pass
    def get_object_materials_without_styles(cls, obj): pass
    def get_profile_set_usage(cls, element): pass
    def get_representation_data(cls, representation): pass
    def get_representation_name(cls, representation): pass
    def get_total_representation_items(cls, obj): pass
    def has_data_users(cls, data): pass
    def import_representation(cls, obj, representation, enable_dynamic_voids=False): pass
    def import_representation_parameters(cls, data): pass
    def is_body_representation(cls, representation): pass
    def is_box_representation(cls, representation): pass
    def is_edited(cls, obj): pass
    def is_mapped_representation(cls, representation): pass
    def is_type_product(cls, element): pass
    def link(cls, element, obj): pass
    def rename_object(cls, obj, name): pass
    def replace_object_with_empty(cls, obj): pass
    def resolve_mapped_representation(cls, representation): pass
    def run_geometry_update_representation(cls, obj=None): pass
    def should_force_faceted_brep(cls): pass
    def should_force_triangulation(cls): pass
    def should_use_presentation_style_assignment(cls): pass


@interface
class Ifc:
    def get(cls): pass
    def get_entity(cls, obj): pass
    def get_object(cls, obj): pass
    def link(cls, element, obj): pass
    def run(cls, command, **kwargs): pass
    def unlink(cls, element=None, obj=None): pass


@interface
class Material:
    def add_default_material_object(cls): pass
    def link(cls, element, obj): pass
    def unlink(cls, obj): pass


@interface
class Misc:
    def get_object_storey(cls, obj): pass
    def get_storey_elevation_in_si(cls, storey): pass
    def get_storey_height_in_si(cls, storey, total_storeys): pass
    def mark_object_as_edited(cls, obj): pass
    def move_object_to_elevation(cls, obj, elevation): pass
    def run_root_copy_class(cls, obj=None): pass
    def scale_object_to_height(cls, obj, height): pass
    def set_object_origin_to_bottom(cls, obj): pass
    def split_objects_with_cutter(cls, objs, cutter): pass


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
class Pset:
    def get_element_pset(cls, element, pset_name): pass


@interface
class Qto:
    def get_radius_of_selected_vertices(cls, obj): pass
    def set_qto_result(cls, result): pass


@interface
class Root:
    def add_dynamic_opening_voids(cls, element, obj): pass
    def does_type_have_representations(cls, element): pass
    def get_element_type(cls, element): pass
    def get_object_representation(cls, obj): pass
    def get_representation_context(cls, representation): pass
    def is_opening_element(cls, element): pass
    def link_object_data(cls, source_obj, destination_obj): pass
    def run_geometry_add_representation(cls, obj=None, context=None, ifc_representation_class=None, profile_set_usage=None): pass


@interface
class Selector:
    def set_active(cls, obj): pass


@interface
class Spatial:
    def can_contain(cls, structure_obj, element_obj): pass
    def disable_editing(cls, obj): pass
    def duplicate_object_and_data(cls, obj): pass
    def enable_editing(cls, obj): pass
    def get_container(cls, element): pass
    def get_decomposed_elements(cls, container): pass
    def get_object_matrix(cls, obj): pass
    def get_relative_object_matrix(cls, target_obj, relative_to_obj): pass
    def import_containers(cls, parent=None): pass
    def run_root_copy_class(cls, obj=None): pass
    def run_spatial_assign_container(cls, structure_obj=None, element_obj=None): pass
    def select_object(cls, obj): pass
    def set_active_object(cls, obj): pass
    def set_relative_object_matrix(cls, target_obj, relative_to_obj, matrix): pass


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
class Type:
    def change_object_data(cls, obj, data, is_global=False): pass
    def disable_editing(cls, obj): pass
    def get_body_context(cls): pass
    def get_body_representation(cls, element): pass
    def get_ifc_representation_class(cls, element): pass
    def get_object_data(cls, obj): pass
    def get_profile_set_usage(cls, element): pass
    def get_representation_context(cls, representation): pass
    def has_dynamic_voids(cls, obj): pass
    def has_material_usage(cls, element): pass
    def run_geometry_add_representation(cls, obj=None, context=None, ifc_representation_class=None, profile_set_usage=None): pass
    def run_geometry_switch_representation(cls, obj=None, representation=None, should_reload=None, enable_dynamic_voids=None, is_global=None): pass


@interface
class Unit:
    def clear_active_unit(cls): pass
    def disable_editing_units(cls): pass
    def enable_editing_units(cls): pass
    def export_unit_attributes(cls): pass
    def get_scene_unit_name(cls, unit_type): pass
    def get_scene_unit_si_prefix(cls): pass
    def get_si_name_from_unit_type(cls, unit_type): pass
    def get_unit_class(cls, unit): pass
    def import_unit_attributes(cls, unit): pass
    def import_units(cls): pass
    def is_scene_unit_metric(cls): pass
    def set_active_unit(cls, unit): pass


@interface
class Voider:
    def can_void(cls, opening, element): pass
    def set_void_display(cls, opening_obj): pass
    def unvoid(cls, opening_obj): pass
    def void(cls, opening_obj, building_obj): pass
