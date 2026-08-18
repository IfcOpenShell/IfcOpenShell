// SPDX-License-Identifier: LGPL-3.0-or-later

#ifndef IFCWRAP_BINDING_GENERATOR_IFCGEOM_SPEC_HPP
#define IFCWRAP_BINDING_GENERATOR_IFCGEOM_SPEC_HPP

#include "spec_macros.h"

#include "ifcparse/express.h"
#include "ifcparse/file.h"
#include "ifcparse/schema.h"

#include "ifc_geom_api.h"
#include "iterator.h"
#include "converter.h"
#include "kernel_plugin.h"
#include "kernel_registry.h"
#include "abstract_mapping.h"
#include "mapping_plugin.h"
#include "tree_plugin.h"
#include "tree_registry.h"
#include "tree.h"
#include "taxonomy.h"
#include "function_item_evaluator.h"
#include "geometry_serializer_plugin.h"
#include "document_serializer_plugin.h"
#include "geometry_serializer.h"
#include "json_serializer.h"
#include "rocks_db_serializer.h"
#include "xml_serializer.h"
#include "../svgfill/src/svgfill.h"

#include <Eigen/Dense>

#include <algorithm>
#include <cctype>
#include <limits>
#include <memory>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

/*
 * Opaque C handles exposed by this spec. Each entry gives the binding name,
 * C++ type, and destruction policy. Optional arguments select value or shared
 * pointer storage and define how an empty value is detected.
 */
IFCAPI_HANDLE(iterator, ifcopenshell::geom::iterator, delete)
IFCAPI_HANDLE(settings, ifcopenshell::geom::settings, delete)
IFCAPI_HANDLE(geometry_serializer, ifcopenshell::geom::geometry_serializer, delete)
IFCAPI_HANDLE(serializer, ifcopenshell::geom::serializer, delete)
IFCAPI_HANDLE(buffer, stream_or_filename, delete)
IFCAPI_HANDLE(tree, ifcopenshell::geom::tree, delete)
IFCAPI_HANDLE(tree_clash_list, std::vector<ifcopenshell::geom::clash>, delete)
IFCAPI_HANDLE(tree_clash, ifcopenshell::geom::clash, delete)
IFCAPI_HANDLE(tree_ray_intersection_list, std::vector<ifcopenshell::geom::ray_intersection_result>, delete)
IFCAPI_HANDLE(tree_ray_intersection, ifcopenshell::geom::ray_intersection_result, delete)
IFCAPI_HANDLE(transformation, ifcopenshell::geom::transformation, delete)
IFCAPI_HANDLE(element, ifcopenshell::geom::element, delete)
IFCAPI_HANDLE(brep_element, ifcopenshell::geom::native_element, delete)
IFCAPI_HANDLE(triangulation_element, ifcopenshell::geom::triangulation_element, delete)
IFCAPI_HANDLE(serialized_element, ifcopenshell::geom::serialized_element, delete)
IFCAPI_HANDLE(triangulation, ifcopenshell::geom::triangulation, none)
IFCAPI_HANDLE(brep_representation, ifcopenshell::geom::native, none)
IFCAPI_HANDLE(serialization, ifcopenshell::geom::serialization, none)
IFCAPI_HANDLE(conversion_result_shape, ifcopenshell::geom::conversion_result_shape, delete)
IFCAPI_HANDLE(opaque_number, ifcopenshell::geom::opaque_number, delete)
IFCAPI_HANDLE(svgfill_polygon, svgfill::polygon_2, delete)
IFCAPI_HANDLE(function_item_evaluator, ifcopenshell::geom::function_item_evaluator, delete)

IFCAPI_HANDLE(taxonomy_item, ifcopenshell::geom::taxonomy::item, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_matrix4, ifcopenshell::geom::taxonomy::matrix4, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_point3, ifcopenshell::geom::taxonomy::point3, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_direction3, ifcopenshell::geom::taxonomy::direction3, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_style, ifcopenshell::geom::taxonomy::style, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_colour, ifcopenshell::geom::taxonomy::colour, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_line, ifcopenshell::geom::taxonomy::line, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_circle, ifcopenshell::geom::taxonomy::circle, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_ellipse, ifcopenshell::geom::taxonomy::ellipse, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_bspline_curve, ifcopenshell::geom::taxonomy::bspline_curve, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_offset_curve, ifcopenshell::geom::taxonomy::offset_curve, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_edge, ifcopenshell::geom::taxonomy::edge, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_loop, ifcopenshell::geom::taxonomy::loop, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_face, ifcopenshell::geom::taxonomy::face, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_shell, ifcopenshell::geom::taxonomy::shell, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_solid, ifcopenshell::geom::taxonomy::solid, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_plane, ifcopenshell::geom::taxonomy::plane, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_cylinder, ifcopenshell::geom::taxonomy::cylinder, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_sphere, ifcopenshell::geom::taxonomy::sphere, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_torus, ifcopenshell::geom::taxonomy::torus, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_bspline_surface, ifcopenshell::geom::taxonomy::bspline_surface, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_collection, ifcopenshell::geom::taxonomy::collection, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_loft, ifcopenshell::geom::taxonomy::loft, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_extrusion, ifcopenshell::geom::taxonomy::extrusion, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_revolve, ifcopenshell::geom::taxonomy::revolve, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_sweep_along_curve, ifcopenshell::geom::taxonomy::sweep_along_curve, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_node, ifcopenshell::geom::taxonomy::node, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_boolean_result, ifcopenshell::geom::taxonomy::boolean_result, shared_ptr, shared_ptr)

/*
 * Existing C++ methods included in the C ABI. Entries identify the receiver
 * handle, C++ method, exported name, and exact parameter types when needed to
 * select an overload. Clang supplies the remaining type information.
 */
IFCAPI_DISCOVER_METHOD(triangulation, edges, edges)
IFCAPI_DISCOVER_METHOD(triangulation, edges_item_ids, edges_item_ids)
IFCAPI_DISCOVER_METHOD(triangulation, faces, faces)
IFCAPI_DISCOVER_METHOD(triangulation, item_ids, item_ids)
IFCAPI_DISCOVER_METHOD(triangulation, material_ids, material_ids)
IFCAPI_DISCOVER_METHOD(triangulation, materials, materials)
IFCAPI_DISCOVER_METHOD(triangulation, normals, normals)
IFCAPI_DISCOVER_METHOD(triangulation, polyhedral_faces_with_holes, polyhedral_faces_with_holes)
IFCAPI_DISCOVER_METHOD(triangulation, polyhedral_faces_without_holes, polyhedral_faces_without_holes)
IFCAPI_DISCOVER_METHOD(triangulation, uvs, uvs)
IFCAPI_DISCOVER_METHOD(triangulation, verts, verts)
IFCAPI_DISCOVER_METHOD(iterator, bounds_max, bounds_max)
IFCAPI_DISCOVER_METHOD(iterator, bounds_min, bounds_min)
IFCAPI_DISCOVER_METHOD(iterator, compute_bounds, compute_bounds, bool)
IFCAPI_DISCOVER_METHOD(iterator, create, create)
IFCAPI_DISCOVER_METHOD(iterator, file, file)
IFCAPI_DISCOVER_METHOD(iterator, get, get)
IFCAPI_DISCOVER_METHOD(iterator, getLog, get_log)
IFCAPI_DISCOVER_METHOD(iterator, get_native, get_native)
IFCAPI_DISCOVER_METHOD(iterator, get_object, get_object, int)
IFCAPI_DISCOVER_METHOD(iterator, get_task_items, get_task_items)
IFCAPI_DISCOVER_METHOD(iterator, get_task_products, get_task_products)
IFCAPI_DISCOVER_METHOD(iterator, had_error_processing_elements, had_error_processing_elements)
IFCAPI_DISCOVER_METHOD(iterator, initialize, initialize)
IFCAPI_DISCOVER_METHOD(iterator, next, next)
IFCAPI_DISCOVER_METHOD(iterator, progress, progress)
IFCAPI_DISCOVER_METHOD(iterator, unit_magnitude, unit_magnitude)
IFCAPI_DISCOVER_METHOD(iterator, unit_name, unit_name)
IFCAPI_DISCOVER_METHOD(brep_representation, as_compound, as_compound, bool)
IFCAPI_DISCOVER_METHOD(brep_representation, calculate_projected_surface_area, calculate_projected_surface_area, const std::shared_ptr<ifcopenshell::geom::taxonomy::matrix4>&, double&, double&, double&)
IFCAPI_DISCOVER_METHOD(brep_representation, entity, entity)
IFCAPI_DISCOVER_METHOD(brep_representation, id, id)
IFCAPI_DISCOVER_METHOD(brep_representation, item, item, int)
IFCAPI_DISCOVER_METHOD(brep_representation, item_id, item_id, int)
IFCAPI_DISCOVER_METHOD(brep_representation, settings, settings)
IFCAPI_DISCOVER_METHOD(brep_representation, calculate_surface_area, calculate_surface_area, double&)
IFCAPI_DISCOVER_METHOD(brep_representation, calculate_volume, calculate_volume, double&)
IFCAPI_DISCOVER_METHOD(brep_representation, size, size)
IFCAPI_DISCOVER_METHOD(element, context, context)
IFCAPI_DISCOVER_METHOD(element, guid, guid)
IFCAPI_DISCOVER_METHOD(element, id, id)
IFCAPI_DISCOVER_METHOD(element, name, name)
IFCAPI_DISCOVER_METHOD(element, parent_id, parent_id)
IFCAPI_DISCOVER_METHOD(element, parents, parents)
IFCAPI_DISCOVER_METHOD(element, transformation, transformation)
IFCAPI_DISCOVER_METHOD(element, type, type)
IFCAPI_DISCOVER_METHOD(element, unique_id, unique_id)
IFCAPI_DISCOVER_METHOD(brep_element, calculate_projected_surface_area, calculate_projected_surface_area, double&, double&, double&)
IFCAPI_DISCOVER_METHOD(brep_element, geometry, geometry)
IFCAPI_DISCOVER_METHOD(triangulation_element, geometry, geometry)
IFCAPI_DISCOVER_METHOD(serialized_element, geometry, geometry)
IFCAPI_DISCOVER_METHOD(conversion_result_shape, is_manifold, is_manifold)
IFCAPI_DISCOVER_METHOD(conversion_result_shape, num_edges, num_edges)
IFCAPI_DISCOVER_METHOD(conversion_result_shape, num_faces, num_faces)
IFCAPI_DISCOVER_METHOD(conversion_result_shape, num_vertices, num_vertices)
IFCAPI_DISCOVER_METHOD(conversion_result_shape, surface_area_along_direction, surface_area_along_direction, double, const std::shared_ptr<ifcopenshell::geom::taxonomy::matrix4>&, double&, double&, double&)
IFCAPI_DISCOVER_METHOD(conversion_result_shape, surface_genus, surface_genus)
IFCAPI_DISCOVER_METHOD(function_item_evaluator, evaluation_points, evaluation_points)
IFCAPI_DISCOVER_METHOD(function_item_evaluator, evaluation_points, evaluation_points_range, double, double, IFCAPI_INT32(unsigned int))
IFCAPI_DISCOVER_METHOD(function_item_evaluator, evaluate, evaluate)
IFCAPI_DISCOVER_METHOD(function_item_evaluator, evaluate, evaluate_range, double, double, IFCAPI_INT32(unsigned int))
IFCAPI_DISCOVER_METHOD(serialization, brep_data, brep_data)
IFCAPI_DISCOVER_METHOD(serialization, surface_style_ids, surface_style_ids)
IFCAPI_DISCOVER_METHOD(serialization, surface_styles, surface_styles)
IFCAPI_DISCOVER_METHOD(geometry_serializer, settings, settings)
IFCAPI_DISCOVER_METHOD(geometry_serializer, write, write_triangulation_element, const ifcopenshell::geom::triangulation_element*)
IFCAPI_DISCOVER_METHOD(geometry_serializer, write, write_brep_element, const ifcopenshell::geom::native_element*)
IFCAPI_DISCOVER_METHOD(geometry_serializer, finalize, finalize)
IFCAPI_DISCOVER_METHOD(geometry_serializer, isTesselated, is_tesselated)
IFCAPI_DISCOVER_METHOD(geometry_serializer, is_streaming, is_streaming)
IFCAPI_DISCOVER_METHOD(geometry_serializer, read, read, ifcopenshell::file&, const std::string&, const std::string&, ifcopenshell::geom::geometry_serializer::read_type)
IFCAPI_DISCOVER_METHOD(geometry_serializer, ready, ready)
IFCAPI_DISCOVER_METHOD(geometry_serializer, setFile, set_file, ifcopenshell::file&)
IFCAPI_DISCOVER_METHOD(geometry_serializer, setUnitNameAndMagnitude, set_unit_name_and_magnitude, const std::string&, float)
IFCAPI_DISCOVER_METHOD(geometry_serializer, writeHeader, write_header)
IFCAPI_DISCOVER_METHOD(taxonomy_style, has_specularity, has_specularity)
IFCAPI_DISCOVER_METHOD(taxonomy_style, has_transparency, has_transparency)
IFCAPI_DISCOVER_METHOD(opaque_number, to_double, to_double)
IFCAPI_DISCOVER_METHOD(opaque_number, to_string, to_string)
IFCAPI_DISCOVER_METHOD(serializer, finalize, finalize)
IFCAPI_DISCOVER_METHOD(serializer, is_streaming, is_streaming)
IFCAPI_DISCOVER_METHOD(serializer, ready, ready)
IFCAPI_DISCOVER_METHOD(serializer, setFile, set_file, ifcopenshell::file&)
IFCAPI_DISCOVER_METHOD(serializer, writeHeader, write_header)
IFCAPI_DISCOVER_METHOD(settings, get_type, get_type, const std::string&)
IFCAPI_DISCOVER_METHOD(settings, setting_names, setting_names)
IFCAPI_DISCOVER_METHOD(buffer, get_value, get_value)
IFCAPI_DISCOVER_METHOD(buffer, is_ready, is_ready)
IFCAPI_DISCOVER_METHOD(taxonomy_item, hash, hash)
IFCAPI_DISCOVER_METHOD(taxonomy_item, identity, identity)
IFCAPI_DISCOVER_METHOD(taxonomy_item, kind, kind)
IFCAPI_DISCOVER_METHOD(tree, enable_face_styles, enable_face_styles)
IFCAPI_DISCOVER_METHOD(tree, enable_face_styles, set_enable_face_styles, bool)
IFCAPI_DISCOVER_METHOD(tree, add_file, add_file, ifcopenshell::file&, const ifcopenshell::geom::settings&)
IFCAPI_DISCOVER_METHOD(tree, add_file, add_iterator, ifcopenshell::geom::iterator&)
IFCAPI_DISCOVER_METHOD(tree, clash_clearance_many, clash_clearance_many, const std::vector<express::base>&, const std::vector<express::base>&, double, bool)
IFCAPI_DISCOVER_METHOD(tree, clash_collision_many, clash_collision_many, const std::vector<express::base>&, const std::vector<express::base>&, bool)
IFCAPI_DISCOVER_METHOD(tree, clash_intersection_many, clash_intersection_many, const std::vector<express::base>&, const std::vector<express::base>&, double, bool)
IFCAPI_DISCOVER_METHOD(tree, distances, distances)
IFCAPI_DISCOVER_METHOD(tree, is_manifold, is_manifold, const std::vector<int>&)
IFCAPI_DISCOVER_METHOD(tree, protrusion_distances, protrusion_distances)
IFCAPI_DISCOVER_METHOD(tree, styles, styles)
IFCAPI_DISCOVER_METHOD(tree, uint8_to_b64, uint8_to_b64, const std::vector<unsigned char>&)

/*
 * Binding policy that cannot be inferred from C++ signatures: constructor
 * selection and parameter names, field selection and renaming, collection
 * accessors, ownership details, and compile guards.
 */
IFCAPI_DISCOVER_CONSTRUCTOR(tree, ifcopenshell::geom::tree, create_tree, explicit, IFOPSH_WITH_OPENCASCADE, _)
IFCAPI_DISCOVER_CONSTRUCTOR(tree, ifcopenshell::geom::tree, create_tree_from_file, explicit, IFOPSH_WITH_OPENCASCADE, _)
IFCAPI_CONSTRUCTOR_PARAM(create_tree_from_file, f, file, ifcopenshell::file&)
IFCAPI_DISCOVER_CONSTRUCTOR(tree, ifcopenshell::geom::tree, create_tree_from_file_with_settings, explicit, IFOPSH_WITH_OPENCASCADE, _)
IFCAPI_CONSTRUCTOR_PARAM(create_tree_from_file_with_settings, f, file, ifcopenshell::file&)
IFCAPI_CONSTRUCTOR_PARAM(create_tree_from_file_with_settings, settings, settings, const ifcopenshell::geom::settings&)
IFCAPI_DISCOVER_CONSTRUCTOR(tree, ifcopenshell::geom::tree, create_tree_from_iterator, explicit, IFOPSH_WITH_OPENCASCADE, _)
IFCAPI_CONSTRUCTOR_PARAM(create_tree_from_iterator, it, iterator, ifcopenshell::geom::iterator&)
IFCAPI_DISCOVER_CONSTRUCTOR(buffer, stream_or_filename, create_buffer, explicit, _, _)
IFCAPI_DISCOVER_CONSTRUCTOR(buffer, stream_or_filename, create_buffer_from_filename, explicit, _, _)
IFCAPI_CONSTRUCTOR_PARAM(create_buffer_from_filename, fn, filename, const std::string&)
IFCAPI_DISCOVER_CONSTRUCTOR(settings, ifcopenshell::geom::settings, create_settings, auto, _, _)
IFCAPI_DISCOVER_POLICY(tree_clash_list, list_accessor, tree, clashes, tree_clash, clash_count, clash_at, "Clash index out of range")
IFCAPI_DISCOVER_POLICY(tree_ray_intersection_list, list_accessor, tree, intersections, tree_ray_intersection, ray_intersection_count, ray_intersection_at, "Ray intersection index out of range")
IFCAPI_DISCOVER_POLICY(settings, variant, get, set, ifcopenshell::geom::settings::value_variant_t, bool, bool)
IFCAPI_DISCOVER_POLICY(settings, variant, get, set, ifcopenshell::geom::settings::value_variant_t, int, int, int, ifcopenshell::geom::settings_detail::IteratorOutputOptions, ifcopenshell::geom::settings_detail::FunctionStepMethod, ifcopenshell::geom::settings_detail::OutputDimensionalityTypes, ifcopenshell::geom::settings_detail::TriangulationMethod)
IFCAPI_DISCOVER_POLICY(settings, variant, get, set, ifcopenshell::geom::settings::value_variant_t, double, double)
IFCAPI_DISCOVER_POLICY(settings, variant, get, set, ifcopenshell::geom::settings::value_variant_t, string, std::string)
IFCAPI_DISCOVER_POLICY(settings, variant, get, set, ifcopenshell::geom::settings::value_variant_t, int_set, std::set<int>)
IFCAPI_DISCOVER_POLICY(settings, variant, get, set, ifcopenshell::geom::settings::value_variant_t, string_set, std::set<std::string>)
IFCAPI_DISCOVER_POLICY(settings, variant, get, set, ifcopenshell::geom::settings::value_variant_t, double_list, std::vector<double>)
IFCAPI_DISCOVER_POLICY(triangulation, method_size, verts, verts_buffer_size)
IFCAPI_DISCOVER_POLICY(triangulation, method_size, faces, faces_buffer_size)
IFCAPI_DISCOVER_POLICY(triangulation, method_size, normals, normals_buffer_size)
IFCAPI_DISCOVER_POLICY(triangulation, method_size, edges, edges_buffer_size)
IFCAPI_DISCOVER_POLICY(triangulation, method_size, material_ids, material_ids_buffer_size)
IFCAPI_DISCOVER_POLICY(triangulation, method_size, item_ids, item_ids_buffer_size)
IFCAPI_DISCOVER_POLICY(triangulation, method_size, edges_item_ids, edges_item_ids_buffer_size)
IFCAPI_DISCOVER_POLICY(triangulation, method_size, uvs, uvs_buffer_size)
IFCAPI_DISCOVER_POLICY(triangulation, method_size, materials, material_count)
IFCAPI_DISCOVER_POLICY(triangulation, method_at, materials, material_at, taxonomy_style, "Material index out of bounds", std::runtime_error)
IFCAPI_DISCOVER_POLICY(taxonomy_circle, fields, inherited)
IFCAPI_DISCOVER_POLICY(taxonomy_circle, exclude, instance, orientation, surface_style)
IFCAPI_DISCOVER_POLICY(taxonomy_line, fields, inherited)
IFCAPI_DISCOVER_POLICY(taxonomy_line, exclude, instance, orientation, surface_style)
IFCAPI_DISCOVER_POLICY(taxonomy_line, as_item)
IFCAPI_DISCOVER_POLICY(taxonomy_plane, fields, inherited)
IFCAPI_DISCOVER_POLICY(taxonomy_plane, exclude, instance, orientation, surface_style)
IFCAPI_DISCOVER_POLICY(taxonomy_ellipse, fields, inherited)
IFCAPI_DISCOVER_POLICY(taxonomy_ellipse, exclude, instance, orientation, surface_style)
IFCAPI_DISCOVER_POLICY(taxonomy_ellipse, rename, radius, radius1)
IFCAPI_DISCOVER_POLICY(taxonomy_style, fields)
IFCAPI_DISCOVER_POLICY(taxonomy_style, exclude, instance, orientation, surface_style, clone_, calc_hash, reverse, kind, get_color, print)
IFCAPI_DISCOVER_POLICY(taxonomy_sphere, fields, inherited)
IFCAPI_DISCOVER_POLICY(taxonomy_sphere, exclude, instance, orientation, surface_style)
IFCAPI_DISCOVER_POLICY(taxonomy_torus, fields, inherited)
IFCAPI_DISCOVER_POLICY(taxonomy_torus, exclude, instance, orientation, surface_style)
IFCAPI_DISCOVER_POLICY(taxonomy_cylinder, fields, inherited)
IFCAPI_DISCOVER_POLICY(taxonomy_cylinder, exclude, instance, orientation, surface_style)
IFCAPI_DISCOVER_POLICY(taxonomy_extrusion, fields, inherited)
IFCAPI_DISCOVER_POLICY(taxonomy_extrusion, exclude, instance, orientation, surface_style)
IFCAPI_DISCOVER_POLICY(taxonomy_offset_curve, fields)
IFCAPI_DISCOVER_POLICY(taxonomy_offset_curve, as_item)
IFCAPI_DISCOVER_POLICY(taxonomy_revolve, fields, inherited)
IFCAPI_DISCOVER_POLICY(taxonomy_revolve, exclude, instance, orientation, surface_style)
IFCAPI_DISCOVER_POLICY(taxonomy_bspline_curve, fields)
IFCAPI_DISCOVER_POLICY(taxonomy_bspline_curve, exclude, control_points)
IFCAPI_DISCOVER_POLICY(taxonomy_bspline_curve, as_item)
IFCAPI_DISCOVER_POLICY(taxonomy_bspline_curve, children, control_points, _, _, _, _, _)
IFCAPI_DISCOVER_POLICY(taxonomy_sweep_along_curve, fields, inherited)
IFCAPI_DISCOVER_POLICY(taxonomy_sweep_along_curve, exclude, instance, orientation, surface_style)
IFCAPI_DISCOVER_POLICY(taxonomy_sweep_along_curve, has_fields)
IFCAPI_DISCOVER_POLICY(taxonomy_face, fields)
IFCAPI_DISCOVER_POLICY(taxonomy_face, as_item)
IFCAPI_DISCOVER_POLICY(taxonomy_face, extra_field, matrix, matrix4::ptr)
IFCAPI_DISCOVER_POLICY(taxonomy_face, children, children, _, _, _, _, _)
IFCAPI_DISCOVER_POLICY(taxonomy_loft, fields)
IFCAPI_DISCOVER_POLICY(taxonomy_loft, has_fields)
IFCAPI_DISCOVER_POLICY(taxonomy_loft, field_setter, axis)
IFCAPI_DISCOVER_POLICY(taxonomy_loft, children, children, _, _, _, add_item, ifcopenshell::geom::taxonomy::geom_item)
IFCAPI_DISCOVER_POLICY(taxonomy_loop, children, children, _, _, _, _, _)
IFCAPI_DISCOVER_POLICY(taxonomy_shell, children, children, _, _, _, _, _)
IFCAPI_DISCOVER_POLICY(taxonomy_solid, extra_field, matrix, matrix4::ptr)
IFCAPI_DISCOVER_POLICY(taxonomy_solid, children, children, _, _, _, _, _)
IFCAPI_DISCOVER_POLICY(taxonomy_collection, children, children, _, _, _, add_item, ifcopenshell::geom::taxonomy::geom_item)
IFCAPI_DISCOVER_POLICY(taxonomy_boolean_result, fields)
IFCAPI_DISCOVER_POLICY(taxonomy_boolean_result, children, children, _, _, _, add_item, ifcopenshell::geom::taxonomy::geom_item)
IFCAPI_DISCOVER_POLICY(taxonomy_bspline_surface, as_item)
IFCAPI_DISCOVER_POLICY(taxonomy_bspline_surface, array_pair, degree)
IFCAPI_DISCOVER_POLICY(taxonomy_bspline_surface, array_pair, multiplicities)
IFCAPI_DISCOVER_POLICY(taxonomy_bspline_surface, array_pair, knots)
IFCAPI_DISCOVER_POLICY(tree, method_size, styles, style_count)
IFCAPI_DISCOVER_POLICY(tree, method_at, styles, style_at, taxonomy_style, "Style index out of range", std::out_of_range)
IFCAPI_DISCOVER_POLICY(tree, compile_guard, IFOPSH_WITH_OPENCASCADE)
IFCAPI_DISCOVER_POLICY(tree_clash, fields)
IFCAPI_DISCOVER_POLICY(tree_clash, rename, clash_type, type)
IFCAPI_DISCOVER_POLICY(tree_clash, compile_guard, IFOPSH_WITH_OPENCASCADE)
IFCAPI_DISCOVER_POLICY(tree_ray_intersection, fields)
IFCAPI_DISCOVER_POLICY(tree_ray_intersection, exclude, instance)
IFCAPI_DISCOVER_POLICY(tree_ray_intersection, compile_guard, IFOPSH_WITH_OPENCASCADE)
IFCAPI_DISCOVER_POLICY(taxonomy_point3, ccomponents, get_data, "ccomponents", _)
IFCAPI_DISCOVER_POLICY(taxonomy_direction3, ccomponents, get_data, "ccomponents", _)
IFCAPI_DISCOVER_POLICY(taxonomy_matrix4, ccomponents, get_data, "ccomponents", _)
IFCAPI_DISCOVER_POLICY(taxonomy_colour, ccomponents, get_data, "ccomponents", _)
IFCAPI_DISCOVER_POLICY(transformation, ccomponents, matrix, "data()->ccomponents", _)

// Free functions outside the spec namespace that are selected for the C ABI.
IFCAPI_DISCOVER_FUNCTION(ifcopenshell::geom, helmert_curve_point)

namespace ifcgeom::bindings {

inline std::unique_ptr<ifcopenshell::geom::serializer> create_xml_serializer(
    ifcopenshell::file* file,
    const std::string& filename
) {
    return std::make_unique<xml_serializer>(file, filename);
}

inline std::unique_ptr<ifcopenshell::geom::serializer> create_json_serializer(
    ifcopenshell::file* file,
    const std::string& filename
) {
#ifdef WITH_GLTF
    return std::make_unique<json_serializer>(file, filename);
#else
    (void)file;
    (void)filename;
    throw std::runtime_error("JSON serialization is unavailable in this build");
#endif
}

inline std::unique_ptr<ifcopenshell::geom::serializer> create_rocksdb_serializer_streaming(
    const std::string& input_filename,
    const std::string& rocksdb_filename
) {
#ifdef IFOPSH_WITH_ROCKSDB
    return std::make_unique<RocksDbSerializer>(input_filename, rocksdb_filename);
#else
    (void)input_filename;
    (void)rocksdb_filename;
    throw std::runtime_error("RocksDB serialization is unavailable in this build");
#endif
}

class plugin_geometry_serializer final : public ifcopenshell::geom::geometry_serializer {
public:
    plugin_geometry_serializer(
        const std::string& extension,
        const std::string& output_filename,
        const std::string& output_temp_filename,
        const ifcopenshell::geom::settings& settings
    )
        : ifcopenshell::geom::geometry_serializer(settings)
    {
        ifcopenshell::serializers::geometry_serializer_context context{
            output_filename,
            output_temp_filename.empty() ? output_filename : output_temp_filename,
            settings_
        };
        initialize(extension, context);
    }

    plugin_geometry_serializer(
        const std::string& extension,
        const stream_or_filename& output,
        const stream_or_filename& output_temp,
        const ifcopenshell::geom::settings& settings
    )
        : ifcopenshell::geom::geometry_serializer(settings)
    {
        const auto output_filename = output.filename().value_or("");
        const auto output_temp_filename = output_temp.filename().value_or(output_filename);
        ifcopenshell::serializers::geometry_serializer_context context{
            output_filename,
            output_temp_filename,
            settings_,
            &output,
            &output_temp
        };
        initialize(extension, context);
    }

    bool ready() override { return serializer_->ready(); }
    bool is_streaming() const override { return serializer_->is_streaming(); }
    bool isTesselated() const override { return serializer_->isTesselated(); }
    void writeHeader() override { serializer_->writeHeader(); }
    void finalize() override { serializer_->finalize(); }
    void setFile(ifcopenshell::file& file) override { serializer_->setFile(file); }
    void setUnitNameAndMagnitude(const std::string& name, float magnitude) override {
        serializer_->setUnitNameAndMagnitude(name, magnitude);
    }
    void write(const ifcopenshell::geom::triangulation_element* element) override { serializer_->write(element); }
    void write(const ifcopenshell::geom::native_element* element) override { serializer_->write(element); }
    ifcopenshell::geom::element* read(
        ifcopenshell::file& file,
        const std::string& guid,
        const std::string& representation_id,
        read_type type
    ) override {
        return serializer_->read(file, guid, representation_id, type);
    }

private:
    void initialize(
        const std::string& extension,
        ifcopenshell::serializers::geometry_serializer_context& context
    ) {
        auto& registry = ifcopenshell::serializers::geometry_serializer_registry_instance();
        registry.configure(extension, context);
        serializer_ = registry.create(extension, context);
    }

    std::shared_ptr<ifcopenshell::geom::geometry_serializer> serializer_;
};

inline std::vector<express::base> to_base_vector(const std::vector<express::entity>& entities) {
    std::vector<express::base> result;
    result.reserve(entities.size());
    for (const auto& entity : entities) {
        result.emplace_back(entity);
    }
    return result;
}

inline std::unique_ptr<ifcopenshell::geom::iterator> create_iterator(
    const std::string& geometry_library_cpp,
    ifcopenshell::geom::settings* settings_cpp,
    ifcopenshell::file* file_cpp,
    int num_threads
) {
    auto* settings_ptr = settings_cpp;
    auto kernel = ifcopenshell::geom::kernels::construct(file_cpp, geometry_library_cpp, *settings_ptr);
    return std::make_unique<ifcopenshell::geom::iterator>(
        std::move(kernel), *settings_ptr, file_cpp, num_threads);
}

inline std::unique_ptr<ifcopenshell::geom::iterator> create_iterator_with_include_exclude(
    const std::string& geometry_library_cpp,
    ifcopenshell::geom::settings* settings_cpp,
    ifcopenshell::file* file_cpp,
    const std::vector<std::string>& elems_cpp,
    bool include,
    int num_threads
) {
    auto* settings_ptr = settings_cpp;
    auto kernel = ifcopenshell::geom::kernels::construct(file_cpp, geometry_library_cpp, *settings_ptr);
    std::set<std::string> elems_set(elems_cpp.begin(), elems_cpp.end());
    ifcopenshell::geom::entity_filter ef{include, false, elems_set};
    return std::make_unique<ifcopenshell::geom::iterator>(
        std::move(kernel), *settings_ptr, file_cpp,
        std::vector<ifcopenshell::geom::filter_function>{ef}, num_threads);
}

inline std::unique_ptr<ifcopenshell::geom::iterator> create_iterator_with_include_exclude_globalid(
    const std::string& geometry_library_cpp,
    ifcopenshell::geom::settings* settings_cpp,
    ifcopenshell::file* file_cpp,
    const std::vector<std::string>& elems_cpp,
    bool include,
    int num_threads
) {
    auto* settings_ptr = settings_cpp;
    auto kernel = ifcopenshell::geom::kernels::construct(file_cpp, geometry_library_cpp, *settings_ptr);
    std::set<std::string> elems_set(elems_cpp.begin(), elems_cpp.end());
    ifcopenshell::geom::attribute_filter af;
    af.attribute_name = "GlobalId";
    af.populate(elems_set);
    af.include = include;
    return std::make_unique<ifcopenshell::geom::iterator>(
        std::move(kernel), *settings_ptr, file_cpp,
        std::vector<ifcopenshell::geom::filter_function>{af}, num_threads);
}

inline std::unique_ptr<ifcopenshell::geom::iterator> create_iterator_with_include_exclude_id(
    const std::string& geometry_library_cpp,
    ifcopenshell::geom::settings* settings_cpp,
    ifcopenshell::file* file_cpp,
    const std::vector<int>& elems_cpp,
    bool include,
    int num_threads
) {
    auto* settings_ptr = settings_cpp;
    auto kernel = ifcopenshell::geom::kernels::construct(file_cpp, geometry_library_cpp, *settings_ptr);
    std::set<int> elems_set(elems_cpp.begin(), elems_cpp.end());
    ifcopenshell::geom::instance_id_filter af(include, false, elems_set);
    return std::make_unique<ifcopenshell::geom::iterator>(
        std::move(kernel), *settings_ptr, file_cpp,
        std::vector<ifcopenshell::geom::filter_function>{af}, num_threads);
}

inline ifcopenshell::geom::taxonomy::direction3::ptr taxonomy_create_direction3(
    double x,
    double y,
    double z
) {
    Eigen::Vector3d direction(x, y, z);
    if (direction.squaredNorm() <= 1.e-12) {
        throw std::runtime_error("Direction vector must be non-zero");
    }
    return ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::direction3>(direction);
}

inline ifcopenshell::geom::taxonomy::collection::ptr taxonomy_create_collection() {
    return ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::collection>();
}

inline ifcopenshell::geom::taxonomy::loft::ptr taxonomy_create_loft() {
    return ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::loft>();
}

inline ifcopenshell::geom::taxonomy::node::ptr taxonomy_create_node() {
    return ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::node>();
}

inline ifcopenshell::geom::taxonomy::point3::ptr taxonomy_create_point3(double x, double y, double z) {
    return ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::point3>(x, y, z);
}

inline ifcopenshell::geom::taxonomy::bspline_curve::ptr taxonomy_create_bspline_curve(int degree) {
    if (degree < 1) {
        throw std::runtime_error("B-spline curve degree must be >= 1");
    }
    auto value = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::bspline_curve>();
    value->degree = degree;
    return value;
}

inline ifcopenshell::geom::taxonomy::bspline_surface::ptr taxonomy_create_bspline_surface(
    int degree_u,
    int degree_v
) {
    if (degree_u < 1 || degree_v < 1) {
        throw std::runtime_error("B-spline surface degrees must be >= 1");
    }
    auto value = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::bspline_surface>();
    value->degree = {degree_u, degree_v};
    return value;
}

inline ifcopenshell::geom::taxonomy::boolean_result::ptr taxonomy_create_boolean_result(int operation) {
    if (operation < 0 || operation > 2) {
        throw std::runtime_error("Boolean operation must be 0 (UNION), 1 (SUBTRACTION), or 2 (INTERSECTION)");
    }
    auto value = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::boolean_result>();
    value->operation = static_cast<ifcopenshell::geom::taxonomy::boolean_result::operation_type>(operation);
    return value;
}

inline ifcopenshell::geom::taxonomy::offset_curve::ptr taxonomy_create_offset_curve(
    const ifcopenshell::geom::taxonomy::item::ptr& basis,
    const ifcopenshell::geom::taxonomy::direction3::ptr& reference,
    double offset
) {
    auto value = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::offset_curve>();
    value->basis = basis;
    value->reference = reference;
    value->offset = offset;
    return value;
}

inline ifcopenshell::geom::taxonomy::line::ptr taxonomy_create_line(
    double origin_x,
    double origin_y,
    double origin_z,
    double dir_x,
    double dir_y,
    double dir_z
) {
    Eigen::Vector3d origin(origin_x, origin_y, origin_z);
    Eigen::Vector3d direction(dir_x, dir_y, dir_z);
    if (direction.squaredNorm() <= 1.e-12) {
        throw std::runtime_error("Direction vector must be non-zero");
    }
    auto value = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::line>();
    value->matrix = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>(origin, direction);
    return value;
}

inline ifcopenshell::geom::taxonomy::circle::ptr taxonomy_create_circle(
    double origin_x,
    double origin_y,
    double origin_z,
    double dir_x,
    double dir_y,
    double dir_z,
    double radius
) {
    if (radius <= 0.) {
        throw std::runtime_error("Radius must be > 0");
    }
    Eigen::Vector3d origin(origin_x, origin_y, origin_z);
    Eigen::Vector3d direction(dir_x, dir_y, dir_z);
    if (direction.squaredNorm() <= 1.e-12) {
        throw std::runtime_error("Direction vector must be non-zero");
    }
    auto value = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::circle>();
    value->matrix = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>(origin, direction);
    value->radius = radius;
    return value;
}

inline ifcopenshell::geom::taxonomy::ellipse::ptr taxonomy_create_ellipse(
    double origin_x,
    double origin_y,
    double origin_z,
    double dir_x,
    double dir_y,
    double dir_z,
    double radius1,
    double radius2
) {
    if (radius1 <= 0. || radius2 <= 0.) {
        throw std::runtime_error("Radii must be > 0");
    }
    Eigen::Vector3d origin(origin_x, origin_y, origin_z);
    Eigen::Vector3d direction(dir_x, dir_y, dir_z);
    if (direction.squaredNorm() <= 1.e-12) {
        throw std::runtime_error("Direction vector must be non-zero");
    }
    auto value = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::ellipse>();
    value->matrix = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>(origin, direction);
    value->radius = radius1;
    value->radius2 = radius2;
    return value;
}

inline ifcopenshell::geom::taxonomy::plane::ptr taxonomy_create_plane(
    double origin_x,
    double origin_y,
    double origin_z,
    double dir_x,
    double dir_y,
    double dir_z
) {
    Eigen::Vector3d origin(origin_x, origin_y, origin_z);
    Eigen::Vector3d direction(dir_x, dir_y, dir_z);
    if (direction.squaredNorm() <= 1.e-12) {
        throw std::runtime_error("Direction vector must be non-zero");
    }
    auto value = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::plane>();
    value->matrix = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>(origin, direction);
    return value;
}

inline ifcopenshell::geom::taxonomy::cylinder::ptr taxonomy_create_cylinder(
    double origin_x,
    double origin_y,
    double origin_z,
    double dir_x,
    double dir_y,
    double dir_z,
    double radius
) {
    if (radius <= 0.) {
        throw std::runtime_error("Radius must be > 0");
    }
    Eigen::Vector3d origin(origin_x, origin_y, origin_z);
    Eigen::Vector3d direction(dir_x, dir_y, dir_z);
    if (direction.squaredNorm() <= 1.e-12) {
        throw std::runtime_error("Direction vector must be non-zero");
    }
    auto value = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::cylinder>();
    value->matrix = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>(origin, direction);
    value->radius = radius;
    return value;
}

inline ifcopenshell::geom::taxonomy::sphere::ptr taxonomy_create_sphere(
    double origin_x,
    double origin_y,
    double origin_z,
    double dir_x,
    double dir_y,
    double dir_z,
    double radius
) {
    if (radius <= 0.) {
        throw std::runtime_error("Radius must be > 0");
    }
    Eigen::Vector3d origin(origin_x, origin_y, origin_z);
    Eigen::Vector3d direction(dir_x, dir_y, dir_z);
    if (direction.squaredNorm() <= 1.e-12) {
        throw std::runtime_error("Direction vector must be non-zero");
    }
    auto value = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::sphere>();
    value->matrix = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>(origin, direction);
    value->radius = radius;
    return value;
}

inline ifcopenshell::geom::taxonomy::torus::ptr taxonomy_create_torus(
    double origin_x,
    double origin_y,
    double origin_z,
    double dir_x,
    double dir_y,
    double dir_z,
    double radius1,
    double radius2
) {
    if (radius1 <= 0. || radius2 <= 0.) {
        throw std::runtime_error("Radii must be > 0");
    }
    Eigen::Vector3d origin(origin_x, origin_y, origin_z);
    Eigen::Vector3d direction(dir_x, dir_y, dir_z);
    if (direction.squaredNorm() <= 1.e-12) {
        throw std::runtime_error("Direction vector must be non-zero");
    }
    auto value = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::torus>();
    value->matrix = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>(origin, direction);
    value->radius1 = radius1;
    value->radius2 = radius2;
    return value;
}

inline ifcopenshell::geom::taxonomy::solid::ptr taxonomy_create_box(
    double dx,
    double dy,
    double dz
) {
    if (dx <= 0. || dy <= 0. || dz <= 0.) {
        throw std::runtime_error("Box dimensions must be > 0");
    }
    return ifcopenshell::geom::create_box(dx, dy, dz);
}

inline ifcopenshell::geom::taxonomy::extrusion::ptr taxonomy_create_extrusion(
    const ifcopenshell::geom::taxonomy::item::ptr& basis_cpp,
    const ifcopenshell::geom::taxonomy::direction3::ptr& direction_cpp,
    double depth
) {
    auto basis_value = ifcopenshell::geom::taxonomy::dcast<ifcopenshell::geom::taxonomy::item>(basis_cpp);
    if (!basis_value) {
        throw std::runtime_error("Basis item is invalid");
    }
    if (depth <= 0.) {
        throw std::runtime_error("Extrusion depth must be > 0");
    }
    auto value = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::extrusion>(
        ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>(),
        basis_value,
        direction_cpp,
        depth
    );
    return value;
}

inline ifcopenshell::geom::taxonomy::revolve::ptr taxonomy_create_revolve(
    const ifcopenshell::geom::taxonomy::item::ptr& basis_cpp,
    const ifcopenshell::geom::taxonomy::point3::ptr& axis_origin_cpp,
    const ifcopenshell::geom::taxonomy::direction3::ptr& direction_cpp,
    double angle
) {
    auto basis_value = ifcopenshell::geom::taxonomy::dcast<ifcopenshell::geom::taxonomy::item>(basis_cpp);
    if (!basis_value) {
        throw std::runtime_error("Basis item is invalid");
    }
    auto value = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::revolve>(
        ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>(),
        basis_value,
        axis_origin_cpp,
        direction_cpp,
        std::optional<double>(angle)
    );
    return value;
}

inline ifcopenshell::geom::taxonomy::sweep_along_curve::ptr taxonomy_create_sweep_along_curve(
    const ifcopenshell::geom::taxonomy::face::ptr& basis_face_cpp,
    const ifcopenshell::geom::taxonomy::item::ptr& directrix_cpp,
    const ifcopenshell::geom::taxonomy::direction3::ptr& reference_direction_cpp
) {
    auto directrix_value = ifcopenshell::geom::taxonomy::dcast<ifcopenshell::geom::taxonomy::item>(directrix_cpp);
    if (!directrix_value) {
        throw std::runtime_error("Directrix item is invalid");
    }
    auto value = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::sweep_along_curve>(
        ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>(),
        basis_face_cpp,
        directrix_value,
        reference_direction_cpp
    );
    return value;
}

inline std::unique_ptr<ifcopenshell::geom::element> create_shape(
    ifcopenshell::geom::settings* settings_cpp,
    express::base* instance_cpp,
    std::optional<express::base> representation,
    std::optional<std::string> geometry_library
) {
    ifcopenshell::file* file = instance_cpp->file();
    if (!file) {
        throw std::runtime_error("Instance has no associated file");
    }
    std::string geom_lib = geometry_library.value_or("opencascade");
    ifcopenshell::geom::converter kernel(
        ifcopenshell::geom::kernels::construct(file, geom_lib, *settings_cpp),
        file, *settings_cpp);

    auto entity = instance_cpp->as<express::entity>();
    if (!entity) {
        throw std::runtime_error("Instance is not an entity");
    }

    if (entity.declaration().is("IfcProduct")) {
        express::base ifc_representation = representation.value_or(express::base());
        if (!ifc_representation) {
            auto prod_rep_attr = entity.get("Representation");
            if (prod_rep_attr.isNull()) {
                throw ifcopenshell::exception("Representation is NULL");
            }
            auto prod_rep = static_cast<express::base>(prod_rep_attr);
            auto prod_rep_entity = prod_rep.as<express::entity>();
            auto reps_attr = prod_rep_entity.get("Representations");
            auto reps = static_cast<std::vector<express::base>>(reps_attr);
            if (reps.empty()) {
                throw ifcopenshell::exception("No suitable IfcRepresentation found");
            }

            bool is_curves = settings_cpp->get<ifcopenshell::geom::settings::OutputDimensionality>().get()
                == ifcopenshell::geom::settings::CURVES;

            for (auto it = reps.begin(); it != reps.end(); ++it) {
                auto rep_entity = it->as<express::entity>();
                if (!rep_entity) continue;
                auto id_attr = rep_entity.get("RepresentationIdentifier");
                if (id_attr.isNull()) continue;
                std::string rep_id = (std::string)id_attr;
                if (!is_curves) {
                    if (rep_id == "Body" || rep_id == "Facetation") {
                        ifc_representation = *it;
                        break;
                    }
                } else if (rep_id == "Plan" || rep_id == "Axis") {
                    ifc_representation = *it;
                    break;
                }
            }

            if (!ifc_representation) {
                for (auto it = reps.begin(); it != reps.end(); ++it) {
                    auto rep_entity = it->as<express::entity>();
                    if (!rep_entity) continue;
                    auto ctx_attr = rep_entity.get("ContextOfItems");
                    if (ctx_attr.isNull()) continue;
                    auto ctx = static_cast<express::base>(ctx_attr).as<express::entity>();
                    if (!ctx) continue;
                    auto ct_attr = ctx.get("ContextType");
                    if (ct_attr.isNull()) continue;
                    std::string context_type = (std::string)ct_attr;
                    std::transform(context_type.begin(), context_type.end(), context_type.begin(), ::tolower);
                    std::set<std::string> valid_types;
                    if (!is_curves) {
                        valid_types = {"model", "design", "model view", "detail view"};
                    } else {
                        valid_types = {"plan"};
                    }
                    if (valid_types.count(context_type)) {
                        ifc_representation = *it;
                    }
                }
            }

            if (!ifc_representation) {
                ifc_representation = *reps.begin();
            }
        } else if (!ifc_representation.declaration().is("IfcRepresentation")) {
            throw ifcopenshell::exception("Supplied representation not of type IfcRepresentation");
        }

        auto rep_entity = ifc_representation.as<express::entity>();
        std::unique_ptr<ifcopenshell::geom::native_element> brep(
            kernel.create_brep_for_representation_and_product(rep_entity, entity));
        if (!brep) {
            throw ifcopenshell::exception("Failed to process shape");
        }

        auto output_type = settings_cpp->get<ifcopenshell::geom::settings::IteratorOutput>().get();
        if (output_type == ifcopenshell::geom::settings::SERIALIZED) {
            return std::make_unique<ifcopenshell::geom::serialized_element>(*brep);
        }
        if (output_type == ifcopenshell::geom::settings::TRIANGULATED) {
            return std::make_unique<ifcopenshell::geom::triangulation_element>(*brep);
        }
        return brep;
    } else if (
        entity.declaration().is("IfcRepresentationItem") ||
        entity.declaration().is("IfcRepresentation") ||
        entity.declaration().is("IfcProfileDef")
    ) {
        std::vector<ifcopenshell::geom::conversion_result> shapes;
        try {
            shapes = kernel.convert(*instance_cpp);
        } catch (...) {
            throw ifcopenshell::exception("Failed to process representation item");
        }
        if (shapes.empty()) {
            throw ifcopenshell::exception(
                std::string("kernel.convert produced no shapes for ") +
                entity.declaration().name() + " #" + std::to_string(entity.id())
            );
        }
        auto brep_rep = std::make_shared<ifcopenshell::geom::native>(
            kernel.settings(), entity.declaration().name(), std::to_string(entity.id()), shapes
        );

        auto output_type = settings_cpp->get<ifcopenshell::geom::settings::IteratorOutput>().get();
        auto identity = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>();
        express::entity null_product;
        auto brep_elem = std::make_unique<ifcopenshell::geom::native_element>(
            entity.id(),
            -1,
            entity.declaration().name(),
            entity.declaration().name(),
            std::string(),
            std::string(),
            identity,
            brep_rep,
            null_product
        );
        if (output_type == ifcopenshell::geom::settings::SERIALIZED) {
            return std::make_unique<ifcopenshell::geom::serialized_element>(*brep_elem);
        }
        if (output_type == ifcopenshell::geom::settings::TRIANGULATED) {
            return std::make_unique<ifcopenshell::geom::triangulation_element>(*brep_elem);
        }
        return brep_elem;
    }

    throw ifcopenshell::exception("Unsupported instance type for create_shape. Use map_shape for placements.");
}

inline ifcopenshell::geom::taxonomy::item::ptr map_shape(
    ifcopenshell::geom::settings* settings_cpp,
    express::base* instance_cpp
) {
    if (instance_cpp->file() == nullptr) {
        throw std::runtime_error("Unable to map instance without file");
    }
    std::unique_ptr<ifcopenshell::geom::abstract_mapping> mapping(
        ifcopenshell::geom::impl::mapping_implementations().construct(instance_cpp->file(), *settings_cpp)
    );
    return mapping->map(*instance_cpp);
}

inline std::unique_ptr<ifcopenshell::geom::opaque_number> create_epeck_from_int(int value) {
    return std::make_unique<ifcopenshell::geom::opaque_number>(value);
}

inline std::unique_ptr<ifcopenshell::geom::opaque_number> create_epeck_from_double(double value) {
    return std::make_unique<ifcopenshell::geom::opaque_number>(value);
}

inline std::unique_ptr<ifcopenshell::geom::opaque_number> create_epeck_from_string(const std::string& value_cpp) {
    return std::make_unique<ifcopenshell::geom::opaque_number>(std::stod(value_cpp));
}

inline std::unique_ptr<ifcopenshell::geom::opaque_number> add(
    ifcopenshell::geom::opaque_number* self,
    ifcopenshell::geom::opaque_number* other
) {
    return std::make_unique<ifcopenshell::geom::opaque_number>((*self) + (*other));
}

inline std::unique_ptr<ifcopenshell::geom::opaque_number> subtract(
    ifcopenshell::geom::opaque_number* self,
    ifcopenshell::geom::opaque_number* other
) {
    return std::make_unique<ifcopenshell::geom::opaque_number>((*self) - (*other));
}

inline std::unique_ptr<ifcopenshell::geom::opaque_number> multiply(
    ifcopenshell::geom::opaque_number* self,
    ifcopenshell::geom::opaque_number* other
) {
    return std::make_unique<ifcopenshell::geom::opaque_number>((*self) * (*other));
}

inline std::unique_ptr<ifcopenshell::geom::opaque_number> divide(
    ifcopenshell::geom::opaque_number* self,
    ifcopenshell::geom::opaque_number* other
) {
    return std::make_unique<ifcopenshell::geom::opaque_number>((*self) / (*other));
}

inline std::unique_ptr<ifcopenshell::geom::opaque_number> negate(ifcopenshell::geom::opaque_number* self) {
    return std::make_unique<ifcopenshell::geom::opaque_number>(-(*self));
}

inline bool equals(ifcopenshell::geom::opaque_number* self, ifcopenshell::geom::opaque_number* other) {
    return (*self) == (*other);
}

inline bool less_than(ifcopenshell::geom::opaque_number* self, ifcopenshell::geom::opaque_number* other) {
    return (*self) < (*other);
}

inline std::unique_ptr<ifcopenshell::geom::opaque_number> clone(ifcopenshell::geom::opaque_number* self) {
    return std::make_unique<ifcopenshell::geom::opaque_number>(*self);
}

inline std::unique_ptr<ifcopenshell::geom::conversion_result_shape> solid(
    ifcopenshell::geom::conversion_result_shape* self
) {
    return std::unique_ptr<ifcopenshell::geom::conversion_result_shape>(self->solid());
}

inline std::unique_ptr<ifcopenshell::geom::conversion_result_shape> solid_mt(
    ifcopenshell::geom::conversion_result_shape* self
) {
    return std::unique_ptr<ifcopenshell::geom::conversion_result_shape>(self->solid());
}

inline std::unique_ptr<ifcopenshell::geom::conversion_result_shape> add(
    ifcopenshell::geom::conversion_result_shape* self,
    ifcopenshell::geom::conversion_result_shape* arg_0
) {
    return std::unique_ptr<ifcopenshell::geom::conversion_result_shape>(self->add(arg_0));
}

inline std::unique_ptr<ifcopenshell::geom::conversion_result_shape> subtract(
    ifcopenshell::geom::conversion_result_shape* self,
    ifcopenshell::geom::conversion_result_shape* arg_0
) {
    return std::unique_ptr<ifcopenshell::geom::conversion_result_shape>(self->subtract(arg_0));
}

inline std::unique_ptr<ifcopenshell::geom::conversion_result_shape> intersect(
    ifcopenshell::geom::conversion_result_shape* self,
    ifcopenshell::geom::conversion_result_shape* arg_0
) {
    return std::unique_ptr<ifcopenshell::geom::conversion_result_shape>(self->intersect(arg_0));
}

inline std::unique_ptr<ifcopenshell::geom::conversion_result_shape> concat(
    ifcopenshell::geom::conversion_result_shape* self,
    ifcopenshell::geom::conversion_result_shape* arg_0
) {
    return std::unique_ptr<ifcopenshell::geom::conversion_result_shape>(self->concat(arg_0));
}

inline std::unique_ptr<ifcopenshell::geom::conversion_result_shape> halfspaces(
    ifcopenshell::geom::conversion_result_shape* self
) {
    return std::unique_ptr<ifcopenshell::geom::conversion_result_shape>(self->halfspaces());
}

inline std::unique_ptr<ifcopenshell::geom::conversion_result_shape> box(
    ifcopenshell::geom::conversion_result_shape* self
) {
    return std::unique_ptr<ifcopenshell::geom::conversion_result_shape>(self->box());
}

inline std::unique_ptr<ifcopenshell::geom::conversion_result_shape> wrap_in_compound(
    ifcopenshell::geom::conversion_result_shape* self
) {
    return std::unique_ptr<ifcopenshell::geom::conversion_result_shape>(self->wrap_in_compound());
}

inline std::unique_ptr<ifcopenshell::geom::conversion_result_shape> moved(
    ifcopenshell::geom::conversion_result_shape* self,
    ifcopenshell::geom::taxonomy::matrix4::ptr arg_0
) {
    return std::unique_ptr<ifcopenshell::geom::conversion_result_shape>(self->moved(std::move(arg_0)));
}

namespace detail {
    inline std::vector<std::unique_ptr<ifcopenshell::geom::conversion_result_shape>> adopt_shapes(
        std::vector<ifcopenshell::geom::conversion_result_shape*> shapes
    ) {
        struct cleanup_guard {
            std::vector<ifcopenshell::geom::conversion_result_shape*>& shapes;
            ~cleanup_guard() {
                for (auto* shape : shapes) {
                    delete shape;
                }
            }
        } guard{shapes};
        std::vector<std::unique_ptr<ifcopenshell::geom::conversion_result_shape>> result;
        result.reserve(shapes.size());
        for (auto*& shape : shapes) {
            result.emplace_back(shape);
            shape = nullptr;
        }
        return result;
    }
}

inline std::vector<std::unique_ptr<ifcopenshell::geom::conversion_result_shape>> vertices(
    ifcopenshell::geom::conversion_result_shape* self
) {
    return detail::adopt_shapes(self->vertices());
}

inline std::vector<std::unique_ptr<ifcopenshell::geom::conversion_result_shape>> edges(
    ifcopenshell::geom::conversion_result_shape* self
) {
    return detail::adopt_shapes(self->edges());
}

inline std::vector<std::unique_ptr<ifcopenshell::geom::conversion_result_shape>> facets(
    ifcopenshell::geom::conversion_result_shape* self
) {
    return detail::adopt_shapes(self->facets());
}

inline std::unique_ptr<ifcopenshell::geom::conversion_result_shape> nary_union(
    const std::vector<const ifcopenshell::geom::conversion_result_shape*>& shapes_cpp
) {
    std::unique_ptr<ifcopenshell::geom::conversion_result_shape> result;
    std::string backend_id;
    auto identity = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>();
    for (auto* shape : shapes_cpp) {
        if (!shape) {
            continue;
        }
        const auto element_backend_id = std::string(shape->backend_id());
        if (!result) {
            result.reset(shape->moved(identity));
            backend_id = element_backend_id;
        } else {
            if (element_backend_id != backend_id) {
                throw std::runtime_error("nary_union requires shapes from the same geometry backend");
            }
            auto* next = result->add(const_cast<ifcopenshell::geom::conversion_result_shape*>(shape));
            if (!next) {
                throw std::runtime_error("nary_union failed for backend " + backend_id);
            }
            result.reset(next);
        }
    }
    if (!result) {
        throw std::runtime_error("nary_union requires at least one shape");
    }
    return result;
}

inline std::string svg_to_line_segments(
    const std::string& svg_data_cpp,
    std::optional<std::string> class_name
) {
#if defined(IFOPSH_WITH_CGAL) && !defined(__EMSCRIPTEN__)
    std::vector<std::vector<svgfill::line_segment_2>> segments;
    if (!svgfill::svg_to_line_segments(std::string(svg_data_cpp), class_name, segments)) {
        throw std::runtime_error("Failed to read SVG");
    }
    std::ostringstream oss;
    oss << "[";
    for (size_t g = 0; g < segments.size(); ++g) {
        if (g > 0) oss << ",";
        oss << "[";
        for (size_t s = 0; s < segments[g].size(); ++s) {
            if (s > 0) oss << ",";
            oss << "[[" << segments[g][s][0][0] << "," << segments[g][s][0][1]
                << "],[" << segments[g][s][1][0] << "," << segments[g][s][1][1] << "]]";
        }
        oss << "]";
    }
    oss << "]";
    return oss.str();
#else
    (void)svg_data_cpp;
    (void)class_name;
    throw std::runtime_error("svg_to_line_segments is unavailable in this build");
#endif
}

inline std::vector<std::unique_ptr<svgfill::polygon_2>> svg_to_polygons(
    const std::string& svg_data_cpp,
    std::optional<std::string> class_name
) {
#if defined(IFOPSH_WITH_CGAL) && !defined(__EMSCRIPTEN__)
    std::vector<svgfill::polygon_2> polygons;
    if (!svgfill::svg_to_polygons(std::string(svg_data_cpp), class_name, polygons)) {
        throw std::runtime_error("Failed to read SVG");
    }
    std::vector<std::unique_ptr<svgfill::polygon_2>> result;
    for (auto& p : polygons) {
        result.push_back(std::make_unique<svgfill::polygon_2>(p));
    }
    return result;
#else
    (void)svg_data_cpp;
    (void)class_name;
    throw std::runtime_error("svg_to_polygons is unavailable in this build");
#endif
}

inline std::vector<std::unique_ptr<svgfill::polygon_2>> arrange_polygons(
    const std::vector<const svgfill::polygon_2*>& polygons_cpp
) {
#if defined(IFOPSH_WITH_CGAL) && !defined(__EMSCRIPTEN__)
    std::vector<svgfill::polygon_2> input;
    for (auto* p : polygons_cpp) {
        input.push_back(*p);
    }
    std::vector<svgfill::polygon_2> arranged;
    if (!svgfill::arrange_polygons(
            svgfill::arrange_polygon_settings(), input, arranged, ifcopenshell::logger::root()
        )) {
        throw std::runtime_error("Failed to arrange polygons");
    }
    std::vector<std::unique_ptr<svgfill::polygon_2>> result;
    for (auto& p : arranged) {
        result.push_back(std::make_unique<svgfill::polygon_2>(p));
    }
    return result;
#else
    (void)polygons_cpp;
    throw std::runtime_error("arrange_polygons is unavailable in this build");
#endif
}

inline std::vector<std::unique_ptr<svgfill::polygon_2>> line_segments_to_polygons(
    int solver,
    double eps,
    const std::string& segments_json_cpp
) {
#if defined(IFOPSH_WITH_CGAL) && !defined(__EMSCRIPTEN__)
    std::vector<std::vector<svgfill::line_segment_2>> segments;
    std::string s(segments_json_cpp);
    size_t pos = 0;
    auto skip_ws = [&]() { while (pos < s.size() && isspace(s[pos])) pos++; };
    auto expect = [&](char c) { skip_ws(); if (pos < s.size() && s[pos] == c) { pos++; return true; } return false; };
    auto parse_double = [&]() -> double {
        skip_ws();
        size_t end;
        double v = std::stod(s.substr(pos), &end);
        pos += end;
        return v;
    };
    if (expect('[')) {
        do {
            skip_ws();
            if (s[pos] == ']') break;
            std::vector<svgfill::line_segment_2> group;
            if (expect('[')) {
                do {
                    skip_ws();
                    if (s[pos] == ']') break;
                    svgfill::line_segment_2 seg;
                    expect('['); expect('[');
                    seg[0][0] = parse_double(); expect(',');
                    seg[0][1] = parse_double();
                    expect(']'); expect(','); expect('[');
                    seg[1][0] = parse_double(); expect(',');
                    seg[1][1] = parse_double();
                    expect(']'); expect(']');
                    group.push_back(seg);
                } while (expect(','));
                expect(']');
            }
            segments.push_back(group);
        } while (expect(','));
        expect(']');
    }
    std::vector<std::vector<svgfill::polygon_2>> polygon_groups;
    if (!svgfill::line_segments_to_polygons(static_cast<svgfill::solver>(solver), eps, segments, polygon_groups)) {
        throw std::runtime_error("Failed to process line segments");
    }
    std::vector<std::unique_ptr<svgfill::polygon_2>> result;
    for (auto& group : polygon_groups) {
        for (auto& p : group) {
            result.push_back(std::make_unique<svgfill::polygon_2>(p));
        }
    }
    return result;
#else
    (void)solver;
    (void)eps;
    (void)segments_json_cpp;
    throw std::runtime_error("line_segments_to_polygons is unavailable in this build");
#endif
}

inline ifcopenshell::geom::taxonomy::item::ptr convert_loop_to_function_item(
    const ifcopenshell::geom::taxonomy::item::ptr& loop_item_cpp
) {
    auto loop = ifcopenshell::geom::taxonomy::dcast<ifcopenshell::geom::taxonomy::loop>(loop_item_cpp);
    if (!loop) {
        throw std::runtime_error("Input is not a taxonomy loop");
    }
    auto result = ifcopenshell::geom::convert_loop_to_function_item(loop);
    if (!result) {
        throw std::runtime_error("Failed to convert loop to function_item");
    }
    return result;
}

inline std::unique_ptr<ifcopenshell::geom::function_item_evaluator> create_function_item_evaluator(
    ifcopenshell::geom::settings* settings_cpp,
    const ifcopenshell::geom::taxonomy::item::ptr& fn_item_cpp
) {
    auto fn = ifcopenshell::geom::taxonomy::dcast<ifcopenshell::geom::taxonomy::function_item>(fn_item_cpp);
    if (!fn) {
        throw std::runtime_error("Input is not a taxonomy function_item");
    }
    return std::make_unique<ifcopenshell::geom::function_item_evaluator>(*settings_cpp, fn);
}

inline double taxonomy_function_item_start(const ifcopenshell::geom::taxonomy::item::ptr& item_cpp) {
    auto fn = ifcopenshell::geom::taxonomy::dcast<ifcopenshell::geom::taxonomy::function_item>(item_cpp);
    if (!fn) {
        throw std::runtime_error("Input is not a taxonomy function_item");
    }
    return fn->start();
}

inline double taxonomy_function_item_end(const ifcopenshell::geom::taxonomy::item::ptr& item_cpp) {
    auto fn = ifcopenshell::geom::taxonomy::dcast<ifcopenshell::geom::taxonomy::function_item>(item_cpp);
    if (!fn) {
        throw std::runtime_error("Input is not a taxonomy function_item");
    }
    return fn->end();
}

inline std::vector<express::base> select_element(
    ifcopenshell::geom::tree* self,
    express::base* instance,
    bool completely_within,
    double extend
) {
    auto entity = instance->as<express::entity>();
    if (!entity) {
        throw std::runtime_error("Instance should be an IfcProduct entity");
    }
    return to_base_vector(self->select(entity, completely_within, extend));
}

inline std::vector<express::base> select_point(
    ifcopenshell::geom::tree* self,
    double x,
    double y,
    double z,
    double extend
) {
    return to_base_vector(self->select(ifcopenshell::geom::tree_point{x, y, z}, extend));
}

inline std::vector<express::base> select_brep_element(
    ifcopenshell::geom::tree* self,
    const ifcopenshell::geom::native_element* element,
    bool completely_within,
    double extend
) {
    return to_base_vector(self->select(element, completely_within, extend));
}

inline std::vector<express::base> select_box_point(
    ifcopenshell::geom::tree* self,
    double x,
    double y,
    double z,
    double extend
) {
    (void)extend;
    return to_base_vector(self->select_box(ifcopenshell::geom::tree_point{x, y, z}));
}

inline std::vector<express::base> select_box_element(
    ifcopenshell::geom::tree* self,
    express::base* instance,
    bool completely_within,
    double extend
) {
    auto entity = instance->as<express::entity>();
    if (!entity) {
        throw std::runtime_error("Instance should be an IfcProduct entity");
    }
    return to_base_vector(self->select_box(entity, completely_within, extend));
}

inline std::vector<express::base> select_box_bounds(
    ifcopenshell::geom::tree* self,
    double xmin,
    double ymin,
    double zmin,
    double xmax,
    double ymax,
    double zmax,
    bool completely_within
) {
    return to_base_vector(
        self->select_box(ifcopenshell::geom::tree_box{{ifcopenshell::geom::tree_point{xmin, ymin, zmin}, ifcopenshell::geom::tree_point{xmax, ymax, zmax}}}, completely_within));
}

inline std::vector<ifcopenshell::geom::ray_intersection_result> select_ray(
    ifcopenshell::geom::tree* self,
    double origin_x,
    double origin_y,
    double origin_z,
    double dir_x,
    double dir_y,
    double dir_z,
    double length
) {
    return self->select_ray(
        ifcopenshell::geom::tree_point{origin_x, origin_y, origin_z},
        ifcopenshell::geom::tree_point{dir_x, dir_y, dir_z},
        length);
}

inline express::base instance(ifcopenshell::geom::ray_intersection_result* self) {
    return self->instance;
}

inline express::base product(const ifcopenshell::geom::element* self) {
    return self->product();
}

inline ifcopenshell::geom::triangulation_element* get_as_triangulation_element(ifcopenshell::geom::iterator* self) {
    auto elem = self->get();
    auto* tri = dynamic_cast<ifcopenshell::geom::triangulation_element*>(elem.get());
    if (!tri) {
        throw std::runtime_error("Current element is not a TriangulationElement");
    }
    return static_cast<ifcopenshell::geom::triangulation_element*>(elem.release());
}

inline ifcopenshell::geom::native_element* get_as_brep_element(ifcopenshell::geom::iterator* self) {
    auto elem = self->get();
    auto* brep = dynamic_cast<ifcopenshell::geom::native_element*>(elem.get());
    if (!brep) {
        throw std::runtime_error("Current element is not a BRepElement");
    }
    return static_cast<ifcopenshell::geom::native_element*>(elem.release());
}

inline ifcopenshell::geom::serialized_element* get_as_serialized_element(ifcopenshell::geom::iterator* self) {
    auto elem = self->get();
    auto* serialized = dynamic_cast<ifcopenshell::geom::serialized_element*>(elem.get());
    if (!serialized) {
        throw std::runtime_error("Current element is not a SerializedElement");
    }
    return static_cast<ifcopenshell::geom::serialized_element*>(elem.release());
}

inline bool next(ifcopenshell::geom::iterator* self) {
    return static_cast<bool>(self->next());
}

inline const double* transformation_buffer(const ifcopenshell::geom::element* self) {
    return self->transformation().data()->ccomponents().data();
}

inline std::size_t transformation_buffer_size(const ifcopenshell::geom::element* self) {
    (void)self;
    return 16;
}

inline double calc_volume(const ifcopenshell::geom::native_element* self) {
    double v;
    if (self->geometry().calculate_volume(v)) {
        return v;
    }
    return std::numeric_limits<double>::quiet_NaN();
}

inline double calc_surface_area(const ifcopenshell::geom::native_element* self) {
    double v;
    if (self->geometry().calculate_surface_area(v)) {
        return v;
    }
    return std::numeric_limits<double>::quiet_NaN();
}

inline std::unique_ptr<ifcopenshell::geom::conversion_result_shape> as_compound(
    const ifcopenshell::geom::native* self,
    bool force_meters
) {
    return std::unique_ptr<ifcopenshell::geom::conversion_result_shape>(
        self->as_compound(force_meters));
}

inline std::string serialize(ifcopenshell::geom::conversion_result_shape* self) {
    ifcopenshell::geom::taxonomy::matrix4 identity;
    std::string result;
    self->serialize(identity, result);
    return result;
}

inline std::string serialize_obj(ifcopenshell::geom::conversion_result_shape* self) {
    std::ostringstream result;
    ifcopenshell::geom::settings settings;
    std::unique_ptr<ifcopenshell::geom::triangulation> triangulation(self->triangulate(settings));

    for (auto it = triangulation->verts().begin(); it != triangulation->verts().end();) {
        result << "v " << *(it++) << " " << *(it++) << " " << *(it++) << "\n";
    }
    for (auto it = triangulation->normals().begin(); it != triangulation->normals().end();) {
        result << "vn " << *(it++) << " " << *(it++) << " " << *(it++) << "\n";
    }

    const bool has_normals = !triangulation->normals().empty();
    for (auto it = triangulation->faces().begin(); it != triangulation->faces().end();) {
        const auto v1 = *(it++) + 1;
        const auto v2 = *(it++) + 1;
        const auto v3 = *(it++) + 1;
        if (has_normals) {
            result << "f " << v1 << "//" << v1 << " " << v2 << "//" << v2 << " " << v3 << "//" << v3 << "\n";
        } else {
            result << "f " << v1 << " " << v2 << " " << v3 << "\n";
        }
    }
    return result.str();
}

inline void convex_tag(ifcopenshell::geom::conversion_result_shape* self, bool value) {
    (void)self;
    (void)value;
    throw std::runtime_error("convex_tag is not available through the generic conversion result interface");
}

inline double area(ifcopenshell::geom::conversion_result_shape* self) {
    return self->area().to_double();
}

inline double volume(ifcopenshell::geom::conversion_result_shape* self) {
    return self->volume().to_double();
}

inline double length(ifcopenshell::geom::conversion_result_shape* self) {
    return self->length().to_double();
}

inline const std::vector<double>& verts_buffer(const ifcopenshell::geom::triangulation* self) {
    return self->verts();
}

inline const std::vector<int>& faces_buffer(const ifcopenshell::geom::triangulation* self) {
    return self->faces();
}

inline const std::vector<double>& normals_buffer(const ifcopenshell::geom::triangulation* self) {
    return self->normals();
}

inline const std::vector<int>& edges_buffer(const ifcopenshell::geom::triangulation* self) {
    return self->edges();
}

inline const std::vector<int>& material_ids_buffer(const ifcopenshell::geom::triangulation* self) {
    return self->material_ids();
}

inline const std::vector<int>& item_ids_buffer(const ifcopenshell::geom::triangulation* self) {
    return self->item_ids();
}

inline const std::vector<int>& edges_item_ids_buffer(const ifcopenshell::geom::triangulation* self) {
    return self->edges_item_ids();
}

inline const std::vector<double>& uvs_buffer(const ifcopenshell::geom::triangulation* self) {
    return self->uvs();
}

inline std::vector<double> colors_buffer(const ifcopenshell::geom::triangulation* self) {
    std::vector<double> clrs;
    clrs.reserve(self->materials().size() * 4);
    for (auto& mptr : self->materials()) {
        auto& m = *mptr;
        if (m.diffuse) {
            clrs.push_back(m.diffuse.ccomponents()[0]);
            clrs.push_back(m.diffuse.ccomponents()[1]);
            clrs.push_back(m.diffuse.ccomponents()[2]);
        } else {
            clrs.push_back(0.);
            clrs.push_back(0.);
            clrs.push_back(0.);
        }
        if (m.has_transparency()) {
            clrs.push_back(1. - m.transparency);
        } else {
            clrs.push_back(1.);
        }
    }
    return clrs;
}

inline std::size_t colors_buffer_size(const ifcopenshell::geom::triangulation* self) {
    return self->materials().size() * 4;
}

inline std::size_t instance_id(ifcopenshell::geom::taxonomy::style* self) {
    if (!self->instance) {
        return static_cast<std::size_t>(0);
    }
    auto entity = self->instance.as<express::entity>();
    if (!entity) {
        return static_cast<std::size_t>(0);
    }
    return static_cast<std::size_t>(entity.id());
}

inline std::size_t control_point_row_count(
    ifcopenshell::geom::taxonomy::bspline_surface* self
) {
    return self->control_points.size();
}

inline std::size_t control_point_col_count_at(
    ifcopenshell::geom::taxonomy::bspline_surface* self,
    std::size_t row
) {
    if (row >= self->control_points.size()) {
        throw std::runtime_error("B-spline surface control-point row out of bounds");
    }
    return self->control_points[row].size();
}

inline ifcopenshell::geom::taxonomy::point3::ptr control_point_at(
    ifcopenshell::geom::taxonomy::bspline_surface* self,
    std::size_t row,
    std::size_t col
) {
    if (row >= self->control_points.size()) {
        throw std::runtime_error("B-spline surface control-point row out of bounds");
    }
    if (col >= self->control_points[row].size()) {
        throw std::runtime_error("B-spline surface control-point column out of bounds");
    }
    return self->control_points[row][col];
}

inline bool has_weights(ifcopenshell::geom::taxonomy::bspline_surface* self) {
    return static_cast<bool>(self->weights);
}

inline std::size_t weight_row_count(
    ifcopenshell::geom::taxonomy::bspline_surface* self
) {
    if (!self->weights) {
        throw std::runtime_error("B-spline surface weights are not set");
    }
    return self->weights->size();
}

inline std::size_t weight_col_count_at(
    ifcopenshell::geom::taxonomy::bspline_surface* self,
    std::size_t row
) {
    if (!self->weights) {
        throw std::runtime_error("B-spline surface weights are not set");
    }
    if (row >= self->weights->size()) {
        throw std::runtime_error("B-spline surface weight row out of bounds");
    }
    return (*self->weights)[row].size();
}

inline double weight_at(
    ifcopenshell::geom::taxonomy::bspline_surface* self,
    std::size_t row,
    std::size_t col
) {
    if (!self->weights) {
        throw std::runtime_error("B-spline surface weights are not set");
    }
    if (row >= self->weights->size()) {
        throw std::runtime_error("B-spline surface weight row out of bounds");
    }
    if (col >= (*self->weights)[row].size()) {
        throw std::runtime_error("B-spline surface weight column out of bounds");
    }
    return (*self->weights)[row][col];
}

inline std::size_t boundary_size(svgfill::polygon_2* self) {
    return self->boundary.size();
}

inline std::vector<double> boundary_point(
    svgfill::polygon_2* self,
    std::size_t index
) {
    if (index >= self->boundary.size()) {
        throw std::runtime_error("Index out of bounds");
    }
    return {self->boundary[index][0], self->boundary[index][1]};
}

inline std::size_t inner_boundary_count(svgfill::polygon_2* self) {
    return self->inner_boundaries.size();
}

inline std::size_t inner_boundary_size(
    svgfill::polygon_2* self,
    std::size_t boundary_index
) {
    if (boundary_index >= self->inner_boundaries.size()) {
        throw std::runtime_error("Index out of bounds");
    }
    return self->inner_boundaries[boundary_index].size();
}

inline std::vector<double> inner_boundary_point(
    svgfill::polygon_2* self,
    std::size_t boundary_index,
    std::size_t point_index
) {
    if (boundary_index >= self->inner_boundaries.size()) {
        throw std::runtime_error("Boundary index out of bounds");
    }
    if (point_index >= self->inner_boundaries[boundary_index].size()) {
        throw std::runtime_error("Point index out of bounds");
    }
    const auto& pt = self->inner_boundaries[boundary_index][point_index];
    return {pt[0], pt[1]};
}

inline std::vector<double> point_inside(svgfill::polygon_2* self) {
    return {self->point_inside[0], self->point_inside[1]};
}

inline std::vector<double> evaluate_at(
    ifcopenshell::geom::function_item_evaluator* self,
    double u
) {
    Eigen::Matrix4d mat = self->evaluate(u);
    std::vector<double> result(16);
    for (int i = 0; i < 4; ++i) {
        for (int j = 0; j < 4; ++j) {
            result[i * 4 + j] = mat(i, j);
        }
    }
    return result;
}

inline bool plugin_is_loaded(const std::string& kind, const std::string& id) {
    if (kind == "schema") {
        return ifcopenshell::schema_registry_instance().get(id) != nullptr;
    }
    if (kind == "kernel") {
        return ifcopenshell::geom::kernels::kernel_registry_instance().has(id);
    }
    if (kind == "mapping") {
        return ifcopenshell::geom::impl::mapping_registry_instance().has(id);
    }
    if (kind == "tree") {
        return ifcopenshell::geom::trees::tree_registry_instance().has(id);
    }
    if (kind == "geometry_serializer") {
        return ifcopenshell::serializers::geometry_serializer_registry_instance().has(id);
    }
    if (kind == "document") {
        auto dot_pos = id.find('.');
        if (dot_pos != std::string::npos) {
            auto format = id.substr(0, dot_pos);
            auto schema = id.substr(dot_pos + 1);
            return ifcopenshell::serializers::document_serializer_registry_instance().has(format, schema);
        }
        return ifcopenshell::serializers::document_serializer_registry_instance().has(id);
    }
    return false;
}

inline bool plugin_load(const std::string& kind, const std::string& id) {
    if (kind == "schema") {
        return ifcopenshell::schema_registry_instance().get(id) != nullptr;
    }
    if (kind == "kernel") {
        return ifcopenshell::geom::kernels::load_kernel_plugin(
            ifcopenshell::geom::kernels::kernel_registry_instance(), id
        );
    }
    if (kind == "mapping") {
        return ifcopenshell::geom::impl::load_mapping_plugin(
            ifcopenshell::geom::impl::mapping_registry_instance(), id
        );
    }
    if (kind == "tree") {
        return ifcopenshell::geom::trees::load_tree_plugin(
            ifcopenshell::geom::trees::tree_registry_instance(), id
        );
    }
    if (kind == "geometry_serializer") {
        return ifcopenshell::serializers::load_geometry_serializer_plugin(
            ifcopenshell::serializers::geometry_serializer_registry_instance(), id
        );
    }
    if (kind == "document") {
        auto dot_pos = id.find('.');
        if (dot_pos != std::string::npos) {
            return ifcopenshell::serializers::load_document_serializer_plugin(
                ifcopenshell::serializers::document_serializer_registry_instance(),
                id.substr(0, dot_pos),
                id.substr(dot_pos + 1)
            );
        }
        return ifcopenshell::serializers::load_document_serializer_plugin(
            ifcopenshell::serializers::document_serializer_registry_instance(), id
        );
    }
    return false;
}

inline std::unique_ptr<ifcopenshell::geom::geometry_serializer> create_geometry_serializer_by_path(
    const std::string& format,
    const std::string& output_filename,
    const std::string& output_temp_filename,
    ifcopenshell::geom::settings* settings
) {
    return std::make_unique<plugin_geometry_serializer>(
        format, output_filename, output_temp_filename, *settings
    );
}

inline std::unique_ptr<ifcopenshell::geom::geometry_serializer> create_geometry_serializer_by_stream(
    const std::string& format,
    stream_or_filename* output,
    stream_or_filename* output_temp,
    ifcopenshell::geom::settings* settings
) {
    return std::make_unique<plugin_geometry_serializer>(
        format, *output, *output_temp, *settings
    );
}

} // namespace ifcgeom::bindings

#endif // IFCWRAP_BINDING_GENERATOR_IFCGEOM_SPEC_HPP
