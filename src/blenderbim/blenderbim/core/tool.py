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

# This interface class and decorator is magic syntactic sugar to allow concise interface definitions
# If we didn't do this, Python is unnecessarily verbose, which I find distracting. Don't black this file :)
class Interface(abc.ABC): pass
def interface(cls):
    attrs = {n: classmethod(abc.abstractmethod(f)) for n, f in inspect.getmembers(cls, predicate=inspect.isfunction)}
    return type(cls.__name__, (Interface, cls), attrs)


# ############################################################################ #

# Hey there! Welcome to the BlenderBIM Add-on code. Please feel free to reach
# out if you have any questions or need further guidance. Happy hacking!

# ############################################################################ #

# This portion of the code is singled out as it is part of the Demo module, used
# to teach people how the code is structured in the BlenderBIM Add-on.

# This is an example "interface" (as in, a software interface, not a user
# interface) for the Demo module. Think of it as a list of all of the functions
# your module can perform. In this file, you will come across every single
# capability of the entire add-on. By breaking it down into little functions, we
# can test each one separately, and at a glance know if there are opportunities
# for code reuse or refactoring. At this point, we're only interested in a list
# of functions, not the details of how they're implemented. This is because the
# purpose of the core is to just give a high level overview of the application's
# capabilities.

@interface
class Demo:
    def clear_name_field(cls): pass
    def get_project(cls): pass
    def hide_user_hints(cls): pass
    def set_message(cls, message): pass
    def show_user_hints(cls): pass

# The rest of the code in this file is not part of the Demo tutorial.

# ############################################################################ #

@interface
class Aggregate:
    def can_aggregate(cls, relating_object, related_object): pass
    def disable_editing(cls, obj): pass
    def enable_editing(cls, obj): pass
    def get_container(cls, element): pass


@interface
class Blender:
    def set_active_object(cls, obj): pass
    def get_name(cls, ifc_class, name): pass
    def get_selected_objects(cls): pass
    def create_ifc_object(cls, ifc_class: str, name: str = None, data=None): pass
    def get_obj_ifc_definition_id(cls, obj=None, obj_type=None): pass
    def is_ifc_object(cls, obj): pass
    def is_ifc_class_active(cls, ifc_class): pass
    def get_viewport_context(cls): pass
    def update_viewport(cls): pass
    def get_default_selection_keypmap(cls): pass
    def get_object_bounding_box(cls, obj): pass
    def apply_bmesh(cls, mesh, bm, obj=None): pass
    def get_bmesh_for_mesh(cls, mesh, clean=False): pass
    def bmesh_join(cls, bm_a, bm_b, callback=None): pass


@interface
class Boundary: pass


@interface
class Brick:
    def add_brick(cls, namespace, brick_class): pass
    def add_brick_breadcrumb(cls): pass
    def add_brick_from_element(cls, element, namespace, brick_class): pass
    def add_brickifc_project(cls, namespace): pass
    def add_brickifc_reference(cls, brick, element, project): pass
    def add_feed(cls, source, destination): pass
    def clear_brick_browser(cls): pass
    def clear_project(cls): pass
    def export_brick_attributes(cls, brick_uri): pass
    def get_active_brick_class(cls): pass
    def get_brick(cls, element): pass
    def get_brick_class(cls, element): pass
    def get_brick_path(cls): pass
    def get_brick_path_name(cls): pass
    def get_brickifc_project(cls): pass
    def get_convertable_brick_elements(cls): pass
    def get_item_class(cls, item): pass
    def get_library_brick_reference(cls, library, brick_uri): pass
    def get_namespace(cls, uri): pass
    def import_brick_classes(cls, brick_class): pass
    def import_brick_items(cls, brick_class): pass
    def load_brick_file(cls, filepath): pass
    def new_brick_file(cls): pass
    def pop_brick_breadcrumb(cls): pass
    def remove_brick(cls, brick_uri): pass
    def run_assign_brick_reference(cls, element=None, library=None, brick_uri=None): pass
    def run_refresh_brick_viewer(cls): pass
    def run_view_brick_class(cls, brick_class=None): pass
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
class Cost:
    def add_cost_column(cls, name): pass
    def change_parent_cost_item(cls, cost_item, new_parent): pass
    def clean_up_cost_item_tree(cls, cost_item): pass
    def contract_cost_item_rate(cls, cost_item): pass
    def contract_cost_item(cls, cost_item): pass
    def contract_cost_items(cls): pass
    def create_new_cost_item_li(props_collection, cost_item, level_index, type): pass
    def disable_editing_cost_item_parent(cls): pass
    def disable_editing_cost_item_quantity(cls): pass
    def disable_editing_cost_item_value(cls): pass
    def disable_editing_cost_item(cls): pass
    def disable_editing_cost_schedule(cls): pass
    def enable_editing_cost_item_attributes(cls, cost_item): pass
    def enable_editing_cost_item_quantities(cls, cost_item): pass
    def enable_editing_cost_item_quantity(cls, physical_quantity): pass
    def enable_editing_cost_item_value_formula(cls, cost_value): pass
    def enable_editing_cost_item_value(cls, cost_value): pass
    def enable_editing_cost_item_values(cls, cost_item): pass
    def enable_editing_cost_items(cls, cost_schedule): pass
    def enable_editing_cost_schedule_attributes(cls, cost_schedule): pass
    def expand_cost_item_rate(cls, cost_item): pass
    def expand_cost_item(cls, cost_item): pass
    def expand_cost_items(cls): pass
    def export_cost_schedules(cls, format): pass
    def export_cost_schedules(cls, format): pass
    def format_unit(cls, unit): pass
    def get_active_cost_item(cls): pass
    def get_active_cost_schedule(cls): pass
    def get_active_cost_schedule(cls): pass
    def get_attributes_for_cost_value(cls, cost_type, cost_category): pass
    def get_cost_item_attributes(cls, cost_item): pass
    def get_cost_item_products(cls): pass
    def get_cost_item_quantity_attributes(cls): pass
    def get_cost_item_value_formula(cls): pass
    def get_cost_items_for_product(cls, product, cost_schedule): pass
    def get_cost_schedule_attributes(cls): pass
    def get_cost_schedule_products(cls, cost_schedule): pass
    def get_cost_schedule(cls, cost_schedule): pass
    def get_cost_value_attributes(cls): pass
    def get_cost_value_unit_component(cls): pass
    def get_direct_cost_item_products(cls): pass
    def get_highlighted_cost_item(cls): pass
    def get_highlighted_cost_item(cls): pass
    def get_products(cls, related_object_type): pass
    def get_schedule_cost_items(cls, cost_schedule): pass
    def get_units(cls): pass
    def get_units(cls):pass
    def has_cost_assignments(cls, cost_item): pass
    def has_cost_assignments(cls, product, cost_schedule): pass
    def has_schedules(cls): pass
    def highlight_cost_item(cls, cost_item): pass
    def import_cost_schedule_csv(cls, file_path, is_schedule_of_rates): pass
    def is_active_schedule_of_rates(cls): pass
    def is_cost_schedule_active(cls, cost_schedule): pass
    def is_root_cost_item(cls, cost_item): pass
    def load_cost_item_attributes(cls): pass
    def load_cost_item_quantities(cls, cost_item, related_object_type): pass
    def load_cost_item_quantity_attributes(cls, physical_quantity): pass
    def load_cost_item_types(cls, cost_item): pass
    def load_cost_item_value_attributes(cls, cost_value): pass
    def load_cost_item_value_formula_attributes(cls, cost_value): pass
    def load_cost_schedule_tree(cls): pass
    def load_product_cost_items(cls, product): pass
    def load_schedule_of_rates_tree(cls, schedule_of_rates): pass
    def play_chaching_sound(cls): pass
    def remove_cost_column(cls, name): pass
    def toggle_cost_item_parent_change(cls, cost_item): pass
    def update_cost_items(cls, product, pset): pass


@interface
class Debug:
    def add_schema_identifier(cls, schema): pass
    def load_express(cls, filename): pass
    def purge_hdf5_cache(cls): pass


@interface
class Document:
    def add_breadcrumb(cls, document): pass
    def clear_breadcrumbs(cls): pass
    def clear_document_tree(cls): pass
    def disable_editing_document(cls): pass
    def disable_editing_ui(cls): pass
    def enable_editing_ui(cls): pass
    def export_document_attributes(cls): pass
    def get_active_breadcrumb(cls): pass
    def import_document_attributes(cls, document): pass
    def import_project_documents(cls): pass
    def import_references(cls, document): pass
    def import_subdocuments(cls, document): pass
    def is_document_information(cls, document): pass
    def remove_latest_breadcrumb(cls): pass
    def set_active_document(cls, document): pass


@interface
class Drawing:
    def activate_drawing(cls, camera): pass
    def add_literal_to_annotation(cls, obj, Literal='Literal', Path='RIGHT', BoxAlignment='bottom-left'): pass
    def copy_representation(cls, source, dest): pass
    def create_annotation_object(cls, drawing, object_type): pass
    def create_camera(cls, name, matrix): pass
    def create_svg_schedule(cls, schedule): pass
    def create_svg_sheet(cls, document, titleblock): pass
    def delete_collection(cls, collection): pass
    def delete_drawing_elements(cls, elements): pass
    def delete_file(cls, uri): pass
    def delete_object(cls, obj): pass
    def disable_editing_assigned_product(cls, obj): pass
    def disable_editing_drawings(cls): pass
    def disable_editing_schedules(cls): pass
    def disable_editing_sheets(cls): pass
    def disable_editing_text(cls, obj): pass
    def does_file_exist(cls, uri): pass
    def enable_editing(cls, obj): pass
    def enable_editing_assigned_product(cls, obj): pass
    def enable_editing_drawings(cls): pass
    def enable_editing_schedules(cls): pass
    def enable_editing_sheets(cls): pass
    def enable_editing_text(cls, obj): pass
    def ensure_unique_drawing_name(cls, name): pass
    def ensure_unique_identification(cls, identification): pass
    def export_text_literal_attributes(cls, obj): pass
    def generate_drawing_matrix(cls, target_view, location_hint): pass
    def generate_drawing_name(cls, target_view, location_hint): pass
    def generate_sheet_identification(cls): pass
    def get_annotation_context(cls, target_view): pass
    def get_assigned_product(cls, element): pass
    def get_body_context(cls): pass
    def get_default_drawing_path(cls, name): pass
    def get_default_drawing_resource_path(cls, resource): pass
    def get_default_layout_path(cls, identification, name): pass
    def get_default_sheet_path(cls, identification, name): pass
    def get_default_sheet_path(cls, identification, name): pass
    def get_default_titleblock_path(cls, name): pass
    def get_document_references(cls, document): pass
    def get_document_uri(cls, document, description=None): pass
    def get_drawing_collection(cls, drawing): pass
    def get_drawing_document(cls, drawing): pass
    def get_drawing_group(cls, drawing): pass
    def get_drawing_references(cls, drawing): pass
    def get_drawing_target_view(cls, drawing): pass
    def get_group_elements(cls, group): pass
    def get_ifc_representation_class(cls, object_type): pass
    def get_name(cls, element): pass
    def get_path_filename(cls, uri): pass
    def get_reference_description(cls, reference): pass
    def get_reference_document(cls, reference): pass
    def get_reference_location(cls, reference): pass
    def get_references_with_location(cls, location): pass
    def get_text_literal(cls, obj): pass
    def get_unit_system(cls): pass
    def import_assigned_product(cls, obj): pass
    def import_drawings(cls): pass
    def import_schedules(cls): pass
    def import_sheets(cls): pass
    def import_text_attributes(cls, obj): pass
    def is_camera_orthographic(cls): pass
    def is_drawing_active(cls): pass
    def move_file(cls, src, dest): pass
    def open_spreadsheet(cls, uri): pass
    def open_svg(cls, filepath): pass
    def remove_literal_from_annotation(cls, obj, literal): pass
    def run_root_assign_class(cls, obj=None, ifc_class=None, predefined_type=None, should_add_representation=True, context=None, ifc_representation_class=None): pass
    def select_assigned_product(cls, drawing): pass
    def set_drawing_collection_name(cls, group, collection): pass
    def set_name(cls, element, name): pass
    def setup_annotation_object(cls, obj, object_type): pass
    def show_decorations(cls): pass
    def sync_object_placement(cls, obj): pass
    def synchronise_ifc_and_text_attributes(cls, obj): pass
    def update_embedded_svg_location(cls, uri, old_location, new_location): pass
    def update_text_size_pset(cls, obj): pass
    def update_text_value(cls, obj): pass


@interface
class Geometry:
    def change_object_data(cls, obj, data, is_global=False): pass
    def clear_cache(cls, element): pass
    def clear_modifiers(cls, obj): pass
    def clear_scale(cls, obj): pass
    def delete_data(cls, data): pass
    def does_representation_id_exist(cls, representation_id): pass
    def duplicate_object_data(cls, obj): pass
    def get_cartesian_point_coordinate_offset(cls, obj): pass
    def get_element_type(cls, element): pass
    def get_elements_of_type(cls, type): pass
    def get_ifc_representation_class(cls, element, representation): pass
    def get_object_data(cls, obj): pass
    def get_object_materials_without_styles(cls, obj): pass
    def get_profile_set_usage(cls, element): pass
    def get_representation_data(cls, representation): pass
    def get_representation_id(cls, representation): pass
    def get_representation_name(cls, representation): pass
    def get_styles(cls, obj): pass
    def get_total_representation_items(cls, obj): pass
    def has_data_users(cls, data): pass
    def import_representation(cls, obj, representation, apply_openings=True): pass
    def import_representation_parameters(cls, data): pass
    def is_body_representation(cls, representation): pass
    def is_box_representation(cls, representation): pass
    def is_edited(cls, obj): pass
    def is_mapped_representation(cls, representation): pass
    def is_type_product(cls, element): pass
    def link(cls, element, obj): pass
    def record_object_materials(cls, obj): pass
    def record_object_position(cls, obj): pass
    def remove_connection(cls, connection): pass
    def rename_object(cls, obj, name): pass
    def replace_object_with_empty(cls, obj): pass
    def resolve_mapped_representation(cls, representation): pass
    def run_geometry_update_representation(cls, obj=None): pass
    def run_style_add_style(cls, obj=None): pass
    def select_connection(cls, connection): pass
    def should_force_faceted_brep(cls): pass
    def should_force_triangulation(cls): pass
    def should_generate_uvs(cls, obj): pass
    def should_use_presentation_style_assignment(cls): pass


@interface
class Georeference:
    def disable_editing(cls): pass
    def enable_editing(cls): pass
    def enh2xyz(cls, map_conversion, coordinates): pass
    def get_coordinates(cls, io): pass
    def get_cursor_location(cls): pass
    def get_map_conversion(cls): pass
    def get_map_conversion_attributes(cls): pass
    def get_projected_crs_attributes(cls): pass
    def get_true_north_attributes(cls): pass
    def import_map_conversion(cls): pass
    def import_projected_crs(cls): pass
    def import_true_north(cls): pass
    def set_blender_grid_north(cls): pass
    def set_blender_true_north(cls): pass
    def set_coordinates(cls, io, coordinates): pass
    def set_cursor_location(cls, coordinates): pass
    def set_ifc_grid_north(cls): pass
    def set_ifc_true_north(cls): pass
    def xyz2enh(cls, map_conversion, coordinates): pass


@interface
class Ifc:
    def get(cls): pass
    def get_entity(cls, obj): pass
    def get_object(cls, entity): pass
    def get_path(cls): pass
    def get_schema(cls): pass
    def is_edited(cls, obj): pass
    def is_moved(cls, obj): pass
    def link(cls, element, obj): pass
    def schema(cls): pass
    def edit(cls, obj): pass
    def resolve_uri(cls, uri): pass
    def run(cls, command, **kwargs): pass
    def set(cls, ifc): pass
    def unlink(cls, element=None, obj=None): pass
    def get_all_element_occurences(cls, element): pass


@interface
class Library:
    def clear_editing_mode(cls): pass
    def export_library_attributes(cls): pass
    def export_reference_attributes(cls): pass
    def get_active_library(cls): pass
    def get_active_reference(cls): pass
    def import_library_attributes(cls, library): pass
    def import_reference_attributes(cls, reference): pass
    def import_references(cls, library): pass
    def set_active_library(cls, library): pass
    def set_active_reference(cls, reference): pass
    def set_editing_mode(cls, mode): pass


@interface
class Loader:
    pass


@interface
class Material:
    def add_default_material_object(cls): pass
    def delete_object(cls, obj): pass
    def disable_editing_materials(cls): pass
    def enable_editing_materials(cls): pass
    def get_active_material_type(cls): pass
    def get_elements_by_material(cls, material): pass
    def get_name(cls, obj): pass
    def import_material_definitions(cls, material_type): pass
    def is_editing_materials(cls): pass
    def is_material_used_in_sets(cls, material): pass
    def select_elements(cls, elements): pass


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
class Model:
    def convert_si_to_unit(cls, value): pass
    def convert_unit_to_si(cls, value): pass
    def export_curve(cls, position, edge_indices, points=None): pass
    def export_points(cls, position, indices): pass
    def export_profile(cls, obj, position=None): pass
    def generate_occurrence_name(cls, element_type, ifc_class): pass
    def get_extrusion(cls, representation): pass
    def import_profile(cls, profile, obj=None, position=None): pass
    def import_curve(cls, obj, position, curve): pass
    def import_rectangle(cls, obj, position, profile): pass
    def load_openings(cls, element, openings): pass
    def clear_scene_openings(cls): pass
    def get_material_layer_parameters(cls, element): pass
    def get_manual_booleans(cls, element): pass
    def get_wall_axis(cls, obj, layers=None): pass
    def regenerate_array(cls, parent, data): pass
    def replace_object_ifc_representation(cls, ifc_file, ifc_context, obj, new_representation): pass


@interface
class Patch:
    def run_migrate_patch(cls, infile, outfile, schema): pass


@interface
class Owner:
    def add_address_attribute(cls, name): pass
    def add_person_attribute(cls, name): pass
    def clear_actor(cls): pass
    def clear_address(cls): pass
    def clear_organisation(cls): pass
    def clear_person(cls): pass
    def clear_role(cls): pass
    def clear_user(cls): pass
    def export_actor_attributes(cls): pass
    def export_address_attributes(cls): pass
    def export_organisation_attributes(cls): pass
    def export_person_attributes(cls): pass
    def export_role_attributes(cls): pass
    def get_actor(cls): pass
    def get_address(cls): pass
    def get_organisation(cls): pass
    def get_person(cls): pass
    def get_role(cls): pass
    def get_user(cls): pass
    def import_actor_attributes(cls, actor): pass
    def import_address_attributes(cls): pass
    def import_organisation_attributes(cls): pass
    def import_person_attributes(cls): pass
    def import_role_attributes(cls): pass
    def remove_address_attribute(cls, name, id): pass
    def remove_person_attribute(cls, name, id): pass
    def set_actor(cls, actor): pass
    def set_address(cls, address): pass
    def set_organisation(cls, organisation): pass
    def set_person(cls, person): pass
    def set_role(cls, role): pass
    def set_user(cls, user): pass


@interface
class Project:
    def append_all_types_from_template(cls, template): pass
    def create_empty(cls, name): pass
    def load_default_thumbnails(cls): pass
    def run_aggregate_assign_object(cls, relating_obj=None, related_obj=None): pass
    def run_context_add_context(cls, context_type=None, context_identifier=None, target_view=None, parent=None): pass
    def run_owner_add_organisation(cls): pass
    def run_owner_add_person(cls): pass
    def run_owner_add_person_and_organisation(cls, person=None, organisation=None): pass
    def run_owner_set_user(cls, user=None): pass
    def run_root_assign_class(cls, obj=None, ifc_class=None, predefined_type=None, should_add_representation=True, context=None, ifc_representation_class=None): pass
    def run_unit_assign_scene_units(cls): pass
    def set_active_spatial_element(cls, obj): pass
    def set_context(cls, context): pass
    def set_default_context(cls): pass
    def set_default_modeling_dimensions(cls): pass


@interface
class Profile:
    def draw_image_for_ifc_profile(cls, draw, profile, size): pass


@interface
class Pset:
    def get_element_pset(cls, element, pset_name): pass
    def get_pset_name(cls, obj, obj_type): pass
    def is_pset_applicable(cls,element, pset_name): pass


@interface
class Qto:
    def get_radius_of_selected_vertices(cls, obj): pass
    def set_qto_result(cls, result): pass
    def get_applicable_quantity_names(cls, qto_name): pass
    def get_applicable_base_quantity_name(cls, product): pass
    def get_rounded_value(cls, new_quantity): pass
    def get_calculated_object_quantities(cls, calculator, baste_qto, object): pass
    def add_object_base_qto(cls, object): pass
    def add_product_base_qto(cls, product): pass
    def get_new_calculated_quantity(cls, qto_name, quantity_name, object): pass
    def get_new_guessed_quantity(cls, object, qto_name, quantity_name, ): pass
    def get_related_cost_item_quantities(cls, product): pass


@interface
class Resource:
    def clear_productivity_data(cls, props): pass
    def contract_resource(cls, resource): pass
    def disable_editing_resource_cost_value(cls): pass
    def disable_editing_resource_quantity(cls): pass
    def disable_editing_resource(cls): pass
    def disable_resource_editing_ui(cls): pass
    def edit_productivity_pset(cls, resource, attributes): pass
    def enable_editing_cost_value_attributes(cls, cost_value): pass
    def enable_editing_resource_base_quantity(cls, resource): pass
    def enable_editing_resource_cost_value_formula(cls, cost_value): pass
    def enable_editing_resource_costs(cls, resource): pass
    def enable_editing_resource_quantity(cls, resource_quantity): pass
    def enable_editing_resource_time(cls, resource): pass
    def enable_editing_resource(cls, resource): pass
    def expand_resource(cls, resource): pass
    def get_highlighted_resource(cls): pass
    def get_productivity_attributes(cls): pass
    def get_productivity(cls, resource, should_inherit): pass
    def get_resource_attributes(cls): pass
    def get_resource_cost_value_attributes(cls): pass
    def get_resource_cost_value_formula(cls): pass
    def get_resource_quantity_attributes(cls): pass
    def get_resource_time_attributes(cls): pass
    def get_resource_time(cls, resource): pass
    def import_resources(cls, file_path): pass
    def load_cost_value_attributes(cls, cost_value): pass
    def load_productivity_data(cls): pass
    def load_resource_attributes(cls, resource): pass
    def load_resource_properties(cls): pass
    def load_resource_time_attributes(cls, resource_time): pass
    def load_resources(cls): pass

@interface
class Root:
    def add_tracked_opening(cls, obj): pass
    def assign_body_styles(cls, element, obj): pass
    def copy_representation(cls, source, dest): pass
    def does_type_have_representations(cls, element): pass
    def get_decomposition_relationships(cls, objs): pass
    def get_element_representation(cls, element, context): pass
    def get_element_type(cls, element): pass
    def get_object_name(cls, obj): pass
    def get_object_representation(cls, obj): pass
    def get_representation_context(cls, representation): pass
    def is_element_a(cls, element, ifc_class): pass
    def link_object_data(cls, source_obj, destination_obj): pass
    def recreate_decompositions(cls, relationships, old_to_new): pass
    def run_geometry_add_representation(cls, obj=None, context=None, ifc_representation_class=None, profile_set_usage=None): pass
    def set_object_name(cls, obj, element): pass


@interface
class Selector:
    def set_active(cls, obj): pass

@interface
class Search:
    def from_selector_query(cls, query): pass

@interface
class Sequence:
    def add_task_column(cls, column_type, name, data_type): pass
    def add_text_animation_handler(cls, settings): pass
    def animate_consumption(cls, obj, start_frame, product_frame, color, animation_type): pass
    def animate_creation(cls, obj, start_frame, product_frame, color): pass
    def animate_destruction(cls, obj, start_frame, color, animation_type): pass
    def animate_input(cls, obj, start_frame, product_frame, animation_type): pass
    def animate_movement_from(cls, obj, start_frame, color, animation_type): pass
    def animate_movement_to(cls, obj, start_frame, product_frame, color): pass
    def animate_objects(cls, settings, frames, clear_previous, animation_type): pass
    def animate_operation(cls, obj, start_frame, product_frame, color): pass
    def animate_output(cls, obj, start_frame, product_frame): pass
    def clear_object_animation(cls, obj): pass
    def clear_objects_animation(cls, include_blender_objects): pass
    def contract_all_tasks(cls): pass
    def contract_task(cls, task): pass
    def create_bars(cls, tasks): pass
    def create_new_task_json(cls, task, json, type_map=None): pass
    def create_tasks_json(cls, work_schedule=None): pass
    def disable_editing_rel_sequence(cls): pass
    def disable_editing_task_animation_colors(cls): pass
    def disable_editing_task_time(cls): pass
    def disable_editing_task(cls): pass
    def disable_editing_work_calendar(cls): pass
    def disable_editing_work_plan(cls): pass
    def disable_editing_work_schedule(cls): pass
    def disable_editing_work_time(cls): pass
    def disable_selecting_deleted_task(cls): pass
    def disable_work_schedule(cls): pass
    def enable_editing_rel_sequence_attributes(cls, rel_sequence): pass
    def enable_editing_sequence_lag_time(cls, rel_sequence): pass
    def enable_editing_task_animation_colors(cls): pass
    def enable_editing_task_attributes(cls, task): pass
    def enable_editing_task_calendar(cls, task): pass
    def enable_editing_task_sequence(cls, task): pass
    def enable_editing_task_time(cls, task): pass
    def enable_editing_work_calendar_times(cls, work_calendar): pass
    def enable_editing_work_calendar(cls, work_calendar): pass
    def enable_editing_work_plan_schedules(cls, work_plan): pass
    def enable_editing_work_plan(cls, work_plan): pass
    def enable_editing_work_schedule_tasks(cls, work_schedule): pass
    def enable_editing_work_schedule(cls,work_schedule): pass
    def enable_editing_work_time(cls, work_time): pass
    def expand_all_tasks(cls): pass
    def expand_task(cls, task): pass
    def find_related_input_tasks(cls, product): pass
    def find_related_output_tasks(cls, product): pass
    def generate_gantt_browser_chart(cls, task_json): pass
    def get_active_task(cls): pass
    def get_active_work_schedule(cls): pass
    def get_animation_bar_tasks(cls): pass
    def get_animation_product_frames(cls, work_schedule, settings): pass
    def get_animation_settings(cls): pass
    def get_checked_tasks(cls): pass
    def get_direct_nested_tasks(cls, task):pass
    def get_direct_task_outputs(cls, task): pass
    def get_finish_date(cls): pass
    def get_highlighted_task(cls): pass
    def get_lag_time_attributes(cls): pass
    def get_recurrence_pattern_attributes(cls, recurrence_pattern): pass
    def get_recurrence_pattern_times(cls): pass
    def get_rel_sequence_attributes(cls): pass
    def get_selected_resource(cls): pass
    def get_start_date(cls): pass
    def get_task_attribute_value(cls, attribute_name): pass
    def get_task_attributes(cls): pass
    def get_task_inputs(cls, task): pass
    def get_task_outputs(cls, task): pass
    def get_task_resources(cls, task):pass
    def get_task_time_attributes(cls): pass
    def get_task_time(cls, task): pass
    def get_tasks_for_product(cls, product, work_schedule): pass
    def get_work_calendar_attributes(cls): pass
    def get_work_plan_attributes(cls): pass
    def get_work_schedule_attributes(cls): pass
    def get_work_schedule_products(cls, work_schedule): pass
    def get_work_schedule(cls, task): pass
    def get_work_time_attributes(cls): pass
    def guess_date_range(cls, work_schedule): pass
    def has_task_assignments(cls, product, cost_schedule=None): pass
    def highlight_task(cls, task): pass
    def is_filter_by_active_schedule(cls): pass
    def is_work_schedule_active(cls, work_schedule): pass
    def load_lag_time_attributes(cls, lag_time): pass
    def load_product_related_tasks(cls, product): pass
    def load_rel_sequence_attributes(cls, rel_sequence): pass
    def load_resources(cls): pass
    def load_task_animation_colors(cls): pass
    def load_task_attributes(cls, task): pass
    def load_task_inputs(cls, inputs): pass
    def load_task_outputs(cls, outputs): pass
    def load_task_properties(cls, task): pass
    def load_task_resources(cls,resources): pass
    def load_task_time_attributes(cls, task_time): pass
    def load_task_tree(cls, work_schedule): pass
    def load_work_calendar_attributes(cls, work_calendar): pass
    def load_work_plan_attributes(cls, work_plan): pass
    def load_work_schedule_attributes(cls, work_schedule): pass
    def load_work_time_attributes(cls, work_time): pass
    def process_construction_state(cls, work_schedule, date): pass
    def process_task_status(cls, task, date): pass
    def remove_task_column(cls, name): pass
    def reset_time_period(cls): pass
    def set_object_shading(cls): pass
    def set_task_sort_column(cls, column): pass
    def setup_default_task_columns(cls): pass
    def show_snapshot(cls, product_states): pass
    def update_visualisation_date(cls, start_date, finish_date): pass


@interface
class Spatial:
    def can_contain(cls, structure_obj, element_obj): pass
    def can_reference(cls, structure, element): pass
    def copy_xy(cls, src_obj, destination_obj): pass
    def deselect_objects(cls): pass
    def disable_editing(cls, obj): pass
    def duplicate_object_and_data(cls, obj): pass
    def enable_editing(cls, obj): pass
    def filter_products(cls, products, action): pass
    def get_container(cls, element): pass
    def get_decomposed_elements(cls, container): pass
    def get_object_matrix(cls, obj): pass
    def get_relative_object_matrix(cls, target_obj, relative_to_obj): pass
    def get_selected_product_types(cls): pass
    def get_selected_products(cls): pass
    def import_containers(cls, parent=None): pass
    def run_root_copy_class(cls, obj=None): pass
    def run_spatial_assign_container(cls, structure_obj=None, element_obj=None): pass
    def select_object(cls, obj): pass
    def select_products(cls, products, unhide=False): pass
    def set_active_object(cls, obj): pass
    def set_relative_object_matrix(cls, target_obj, relative_to_obj, matrix): pass
    def show_scene_objects(cls): pass

@interface
class Structural:
    def disable_editing_structural_analysis_model(cls): pass
    def disable_structural_analysis_model_editing_ui(cls): pass
    def enable_editing_structural_analysis_model(cls, model): pass
    def enable_structural_analysis_model_editing_ui(cls): pass
    def enabled_structural_analysis_model_editing_ui(cls): pass
    def ensure_representation_contexts(cls): pass
    def get_active_structural_analysis_model(cls): pass
    def get_ifc_structural_analysis_model_attributes(cls, model): pass
    def get_ifc_structural_analysis_models(cls): pass
    def get_product_or_active_object(cls): pass
    def get_structural_analysis_model_attributes(cls): pass
    def load_structural_analysis_model_attributes(cls, data): pass
    def load_structural_analysis_models(cls): pass


@interface
class Style:
    def can_support_rendering_style(cls, obj): pass
    def disable_editing(cls, obj): pass
    def disable_editing_styles(cls): pass
    def enable_editing(cls, obj): pass
    def enable_editing_styles(cls): pass
    def export_surface_attributes(cls, obj): pass
    def get_active_style_type(cls): pass
    def get_context(cls, obj): pass
    def get_elements_by_style(cls, style): pass
    def get_name(cls, obj): pass
    def get_style(cls, obj): pass
    def get_surface_rendering_attributes(cls, obj): pass
    def get_surface_rendering_style(cls, obj): pass
    def get_surface_shading_attributes(cls, obj): pass
    def get_surface_shading_style(cls, obj): pass
    def get_surface_texture_style(cls, obj): pass
    def get_uv_maps(cls, representation): pass
    def import_presentation_styles(cls, style_type): pass
    def import_surface_attributes(cls, style, obj): pass
    def is_editing_styles(cls): pass
    def record_shading(cls, obj): pass
    def select_elements(cls, elements): pass


@interface
class Surveyor:
    def get_absolute_matrix(cls, obj): pass


@interface
class System:
    def create_empty_at_cursor_with_element_orientation(cls, element): pass
    def delete_element_objects(cls, elements): pass
    def disable_editing_system(cls): pass
    def disable_system_editing_ui(cls): pass
    def enable_system_editing_ui(cls): pass
    def export_system_attributes(cls): pass
    def get_connected_port(cls, port): pass
    def get_ports(cls, element): pass
    def import_system_attributes(cls, system): pass
    def import_systems(cls): pass
    def load_ports(cls, element, ports): pass
    def run_geometry_edit_object_placement(cls, obj=None): pass
    def run_root_assign_class(cls, obj=None, ifc_class=None, predefined_type=None, should_add_representation=True, context=None, ifc_representation_class=None): pass
    def select_elements(cls, elements): pass
    def select_system_products(cls, system): pass
    def set_active_system(cls, system): pass


@interface
class Type:
    def change_object_data(cls, obj, data, is_global=False): pass
    def disable_editing(cls, obj): pass
    def get_body_context(cls): pass
    def get_body_representation(cls, element): pass
    def get_ifc_representation_class(cls, element): pass
    def get_model_types(cls): pass
    def get_object_data(cls, obj): pass
    def get_profile_set_usage(cls, element): pass
    def get_representation_context(cls, representation): pass
    def get_type_occurrences(cls, element_type): pass
    def has_material_usage(cls, element): pass
    def remove_object(cls, obj): pass
    def run_geometry_add_representation(cls, obj=None, context=None, ifc_representation_class=None, profile_set_usage=None): pass
    def run_geometry_switch_representation(cls, obj=None, representation=None, should_reload=None, is_global=None): pass


@interface
class Unit:
    def clear_active_unit(cls): pass
    def disable_editing_units(cls): pass
    def enable_editing_units(cls): pass
    def export_unit_attributes(cls): pass
    def get_scene_unit_name(cls, unit_type): pass
    def get_scene_unit_si_prefix(cls, unit_type): pass
    def import_unit_attributes(cls, unit): pass
    def import_units(cls): pass
    def is_scene_unit_metric(cls): pass
    def is_unit_class(cls, unit, ifc_class): pass
    def set_active_unit(cls, unit): pass


@interface
class Voider:
    def can_void(cls, opening, element): pass
    def set_void_display(cls, opening_obj): pass
    def unvoid(cls, opening_obj): pass
    def void(cls, opening_obj, building_obj): pass
