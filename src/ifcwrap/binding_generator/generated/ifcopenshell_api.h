#ifndef IFCOPENSHELL_API_H
#define IFCOPENSHELL_API_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Common types - guarded to allow multiple API headers to be included */
#ifndef IFCOPENSHELL_COMMON_TYPES_DEFINED
#define IFCOPENSHELL_COMMON_TYPES_DEFINED

typedef struct ifcopenshell_string_t {
    char* data;
    size_t size;
    bool owned;
    void* owner;
} ifcopenshell_string_t;

typedef enum ifcopenshell_logical_t {
    IFCOPENSHELL_LOGICAL_UNKNOWN = -1,
    IFCOPENSHELL_LOGICAL_FALSE = 0,
    IFCOPENSHELL_LOGICAL_TRUE = 1
} ifcopenshell_logical_t;

typedef struct ifcopenshell_string_list_t {
    ifcopenshell_string_t* items;
    size_t size;
    void* owner;
} ifcopenshell_string_list_t;

typedef struct ifcopenshell_int32_list_t {
    int32_t* items;
    size_t size;
    void* owner;
} ifcopenshell_int32_list_t;

typedef struct ifcopenshell_double_list_t {
    double* items;
    size_t size;
    void* owner;
} ifcopenshell_double_list_t;

typedef struct ifcopenshell_bool_list_t {
    bool* items;
    size_t size;
    void* owner;
} ifcopenshell_bool_list_t;

typedef struct ifcopenshell_uint32_list_t {
    uint32_t* items;
    size_t size;
    void* owner;
} ifcopenshell_uint32_list_t;

typedef struct ifcopenshell_int32_list_list_t {
    ifcopenshell_int32_list_t* items;
    size_t size;
    void* owner;
} ifcopenshell_int32_list_list_t;

typedef struct ifcopenshell_int32_list_list_list_t {
    ifcopenshell_int32_list_list_t* items;
    size_t size;
    void* owner;
} ifcopenshell_int32_list_list_list_t;

typedef struct ifcopenshell_uint8_list_t {
    uint8_t* items;
    size_t size;
    void* owner;
} ifcopenshell_uint8_list_t;

typedef struct ifcopenshell_double_list_list_t {
    ifcopenshell_double_list_t* items;
    size_t size;
    void* owner;
} ifcopenshell_double_list_list_t;

void ifcopenshell_buffer_owner_destroy(void** owner);

void ifcopenshell_string_destroy(ifcopenshell_string_t* value);

void ifcopenshell_string_list_destroy(ifcopenshell_string_list_t* value);

void ifcopenshell_int32_list_destroy(ifcopenshell_int32_list_t* value);

void ifcopenshell_double_list_destroy(ifcopenshell_double_list_t* value);

void ifcopenshell_bool_list_destroy(ifcopenshell_bool_list_t* value);

void ifcopenshell_uint32_list_destroy(ifcopenshell_uint32_list_t* value);

void ifcopenshell_int32_list_list_destroy(ifcopenshell_int32_list_list_t* value);

void ifcopenshell_int32_list_list_list_destroy(ifcopenshell_int32_list_list_list_t* value);

void ifcopenshell_uint8_list_destroy(ifcopenshell_uint8_list_t* value);

void ifcopenshell_double_list_list_destroy(ifcopenshell_double_list_list_t* value);

#endif /* IFCOPENSHELL_COMMON_TYPES_DEFINED */

typedef struct ifcopenshell_file_t ifcopenshell_file_t;
typedef struct ifcopenshell_instance_streamer_t ifcopenshell_instance_streamer_t;
typedef struct ifcopenshell_instance_t ifcopenshell_instance_t;
typedef struct ifcopenshell_header_t ifcopenshell_header_t;
typedef struct ifcopenshell_file_description_t ifcopenshell_file_description_t;
typedef struct ifcopenshell_file_name_t ifcopenshell_file_name_t;
typedef struct ifcopenshell_file_schema_t ifcopenshell_file_schema_t;
typedef struct ifcopenshell_declaration_t ifcopenshell_declaration_t;
typedef struct ifcopenshell_type_declaration_t ifcopenshell_type_declaration_t;
typedef struct ifcopenshell_select_type_t ifcopenshell_select_type_t;
typedef struct ifcopenshell_schema_t ifcopenshell_schema_t;
typedef struct ifcopenshell_enumeration_t ifcopenshell_enumeration_t;
typedef struct ifcopenshell_parameter_type_t ifcopenshell_parameter_type_t;
typedef struct ifcopenshell_named_type_t ifcopenshell_named_type_t;
typedef struct ifcopenshell_simple_type_t ifcopenshell_simple_type_t;
typedef struct ifcopenshell_aggregation_type_t ifcopenshell_aggregation_type_t;
typedef struct ifcopenshell_entity_t ifcopenshell_entity_t;
typedef struct ifcopenshell_attribute_t ifcopenshell_attribute_t;
typedef struct ifcopenshell_inverse_attribute_t ifcopenshell_inverse_attribute_t;
typedef struct ifcopenshell_parse_attribute_value_t ifcopenshell_parse_attribute_value_t;
typedef struct ifcopenshell_parse_instance_list_t ifcopenshell_parse_instance_list_t;
typedef struct ifcopenshell_geom_iterator_t ifcopenshell_geom_iterator_t;
typedef struct ifcopenshell_geom_settings_t ifcopenshell_geom_settings_t;
typedef struct ifcopenshell_geom_serializer_settings_t ifcopenshell_geom_serializer_settings_t;
typedef struct ifcopenshell_geom_geometry_serializer_t ifcopenshell_geom_geometry_serializer_t;
typedef struct ifcopenshell_geom_serializer_t ifcopenshell_geom_serializer_t;
typedef struct ifcopenshell_geom_buffer_t ifcopenshell_geom_buffer_t;
typedef struct ifcopenshell_geom_tree_t ifcopenshell_geom_tree_t;
typedef struct ifcopenshell_geom_tree_clash_list_t ifcopenshell_geom_tree_clash_list_t;
typedef struct ifcopenshell_geom_tree_clash_t ifcopenshell_geom_tree_clash_t;
typedef struct ifcopenshell_geom_tree_ray_intersection_list_t ifcopenshell_geom_tree_ray_intersection_list_t;
typedef struct ifcopenshell_geom_tree_ray_intersection_t ifcopenshell_geom_tree_ray_intersection_t;
typedef struct ifcopenshell_geom_transformation_t ifcopenshell_geom_transformation_t;
typedef struct ifcopenshell_geom_element_t ifcopenshell_geom_element_t;
typedef struct ifcopenshell_geom_brep_element_t ifcopenshell_geom_brep_element_t;
typedef struct ifcopenshell_geom_triangulation_element_t ifcopenshell_geom_triangulation_element_t;
typedef struct ifcopenshell_geom_serialized_element_t ifcopenshell_geom_serialized_element_t;
typedef struct ifcopenshell_geom_triangulation_t ifcopenshell_geom_triangulation_t;
typedef struct ifcopenshell_geom_brep_representation_t ifcopenshell_geom_brep_representation_t;
typedef struct ifcopenshell_geom_serialization_t ifcopenshell_geom_serialization_t;
typedef struct ifcopenshell_geom_conversion_result_shape_t ifcopenshell_geom_conversion_result_shape_t;
typedef struct ifcopenshell_geom_opaque_number_t ifcopenshell_geom_opaque_number_t;
typedef struct ifcopenshell_geom_svgfill_polygon_t ifcopenshell_geom_svgfill_polygon_t;
typedef struct ifcopenshell_geom_function_item_evaluator_t ifcopenshell_geom_function_item_evaluator_t;
typedef struct ifcopenshell_geom_taxonomy_item_t ifcopenshell_geom_taxonomy_item_t;
typedef struct ifcopenshell_geom_taxonomy_matrix4_t ifcopenshell_geom_taxonomy_matrix4_t;
typedef struct ifcopenshell_geom_taxonomy_point3_t ifcopenshell_geom_taxonomy_point3_t;
typedef struct ifcopenshell_geom_taxonomy_direction3_t ifcopenshell_geom_taxonomy_direction3_t;
typedef struct ifcopenshell_geom_taxonomy_style_t ifcopenshell_geom_taxonomy_style_t;
typedef struct ifcopenshell_geom_taxonomy_colour_t ifcopenshell_geom_taxonomy_colour_t;
typedef struct ifcopenshell_geom_taxonomy_line_t ifcopenshell_geom_taxonomy_line_t;
typedef struct ifcopenshell_geom_taxonomy_circle_t ifcopenshell_geom_taxonomy_circle_t;
typedef struct ifcopenshell_geom_taxonomy_ellipse_t ifcopenshell_geom_taxonomy_ellipse_t;
typedef struct ifcopenshell_geom_taxonomy_bspline_curve_t ifcopenshell_geom_taxonomy_bspline_curve_t;
typedef struct ifcopenshell_geom_taxonomy_offset_curve_t ifcopenshell_geom_taxonomy_offset_curve_t;
typedef struct ifcopenshell_geom_taxonomy_edge_t ifcopenshell_geom_taxonomy_edge_t;
typedef struct ifcopenshell_geom_taxonomy_loop_t ifcopenshell_geom_taxonomy_loop_t;
typedef struct ifcopenshell_geom_taxonomy_face_t ifcopenshell_geom_taxonomy_face_t;
typedef struct ifcopenshell_geom_taxonomy_shell_t ifcopenshell_geom_taxonomy_shell_t;
typedef struct ifcopenshell_geom_taxonomy_solid_t ifcopenshell_geom_taxonomy_solid_t;
typedef struct ifcopenshell_geom_taxonomy_plane_t ifcopenshell_geom_taxonomy_plane_t;
typedef struct ifcopenshell_geom_taxonomy_cylinder_t ifcopenshell_geom_taxonomy_cylinder_t;
typedef struct ifcopenshell_geom_taxonomy_sphere_t ifcopenshell_geom_taxonomy_sphere_t;
typedef struct ifcopenshell_geom_taxonomy_torus_t ifcopenshell_geom_taxonomy_torus_t;
typedef struct ifcopenshell_geom_taxonomy_bspline_surface_t ifcopenshell_geom_taxonomy_bspline_surface_t;
typedef struct ifcopenshell_geom_taxonomy_collection_t ifcopenshell_geom_taxonomy_collection_t;
typedef struct ifcopenshell_geom_taxonomy_loft_t ifcopenshell_geom_taxonomy_loft_t;
typedef struct ifcopenshell_geom_taxonomy_extrusion_t ifcopenshell_geom_taxonomy_extrusion_t;
typedef struct ifcopenshell_geom_taxonomy_revolve_t ifcopenshell_geom_taxonomy_revolve_t;
typedef struct ifcopenshell_geom_taxonomy_sweep_along_curve_t ifcopenshell_geom_taxonomy_sweep_along_curve_t;
typedef struct ifcopenshell_geom_taxonomy_node_t ifcopenshell_geom_taxonomy_node_t;
typedef struct ifcopenshell_geom_taxonomy_boolean_result_t ifcopenshell_geom_taxonomy_boolean_result_t;

typedef struct ifcopenshell_instance_list_t {
    ifcopenshell_instance_t** items;
    size_t size;
} ifcopenshell_instance_list_t;
typedef struct ifcopenshell_geom_svgfill_polygon_list_t {
    ifcopenshell_geom_svgfill_polygon_t** items;
    size_t size;
} ifcopenshell_geom_svgfill_polygon_list_t;
typedef struct ifcopenshell_geom_conversion_result_shape_list_t {
    ifcopenshell_geom_conversion_result_shape_t** items;
    size_t size;
} ifcopenshell_geom_conversion_result_shape_list_t;
typedef struct ifcopenshell_declaration_list_t {
    ifcopenshell_declaration_t** items;
    size_t size;
} ifcopenshell_declaration_list_t;
typedef struct ifcopenshell_entity_list_t {
    ifcopenshell_entity_t** items;
    size_t size;
} ifcopenshell_entity_list_t;
typedef struct ifcopenshell_enumeration_list_t {
    ifcopenshell_enumeration_t** items;
    size_t size;
} ifcopenshell_enumeration_list_t;
typedef struct ifcopenshell_select_type_list_t {
    ifcopenshell_select_type_t** items;
    size_t size;
} ifcopenshell_select_type_list_t;
typedef struct ifcopenshell_type_declaration_list_t {
    ifcopenshell_type_declaration_t** items;
    size_t size;
} ifcopenshell_type_declaration_list_t;
typedef struct ifcopenshell_attribute_list_t {
    ifcopenshell_attribute_t** items;
    size_t size;
} ifcopenshell_attribute_list_t;
typedef struct ifcopenshell_inverse_attribute_list_t {
    ifcopenshell_inverse_attribute_t** items;
    size_t size;
} ifcopenshell_inverse_attribute_list_t;
typedef struct ifcopenshell_geom_taxonomy_style_list_t {
    ifcopenshell_geom_taxonomy_style_t** items;
    size_t size;
} ifcopenshell_geom_taxonomy_style_list_t;
typedef struct ifcopenshell_geom_taxonomy_item_list_t {
    ifcopenshell_geom_taxonomy_item_t** items;
    size_t size;
} ifcopenshell_geom_taxonomy_item_list_t;
typedef struct ifcopenshell_geom_element_list_t {
    ifcopenshell_geom_element_t** items;
    size_t size;
} ifcopenshell_geom_element_list_t;
typedef struct ifcopenshell_instance_list_list_t {
    ifcopenshell_instance_list_t* items;
    size_t size;
} ifcopenshell_instance_list_list_t;















typedef enum {
    IFCOPENSHELL_ERROR_NONE = 0,
    IFCOPENSHELL_ERROR_RUNTIME = 1,
    IFCOPENSHELL_ERROR_VALUE = 2,
    IFCOPENSHELL_ERROR_TYPE = 3,
    IFCOPENSHELL_ERROR_CANCELLED = 4
} ifcopenshell_error_kind_t;

typedef enum {
    IFCOPENSHELL_ERROR_CODE_NONE = 0,
    IFCOPENSHELL_ERROR_CODE_UNSPECIFIED = 1,
    IFCOPENSHELL_ERROR_CODE_INVALID_ARGUMENT = 2,
    IFCOPENSHELL_ERROR_CODE_DOMAIN_ERROR = 3,
    IFCOPENSHELL_ERROR_CODE_OPERATION_CANCELLED = 4
} ifcopenshell_error_code_t;

/*
 * Error state is thread-local. Kinds and codes are stable programmatic
 * identifiers; messages are diagnostics and must not be parsed. Every
 * generated call clears the state before execution. A nullable result is a
 * successful absence only when the kind remains IFCOPENSHELL_ERROR_NONE.
 * Returned message storage remains valid until the next error or clear on
 * the calling thread.
 */
void ifcopenshell_clear_error(void);
const char* ifcopenshell_last_error_message(void);
int ifcopenshell_last_error_kind(void);
int ifcopenshell_last_error_code(void);

void ifcopenshell_file_destroy(ifcopenshell_file_t* handle);
void ifcopenshell_instance_streamer_destroy(ifcopenshell_instance_streamer_t* handle);
void ifcopenshell_instance_destroy(ifcopenshell_instance_t* handle);
void ifcopenshell_header_destroy(ifcopenshell_header_t* handle);
void ifcopenshell_file_description_destroy(ifcopenshell_file_description_t* handle);
void ifcopenshell_file_name_destroy(ifcopenshell_file_name_t* handle);
void ifcopenshell_file_schema_destroy(ifcopenshell_file_schema_t* handle);
void ifcopenshell_declaration_destroy(ifcopenshell_declaration_t* handle);
void ifcopenshell_type_declaration_destroy(ifcopenshell_type_declaration_t* handle);
void ifcopenshell_select_type_destroy(ifcopenshell_select_type_t* handle);
void ifcopenshell_schema_destroy(ifcopenshell_schema_t* handle);
void ifcopenshell_enumeration_destroy(ifcopenshell_enumeration_t* handle);
void ifcopenshell_parameter_type_destroy(ifcopenshell_parameter_type_t* handle);
void ifcopenshell_named_type_destroy(ifcopenshell_named_type_t* handle);
void ifcopenshell_simple_type_destroy(ifcopenshell_simple_type_t* handle);
void ifcopenshell_aggregation_type_destroy(ifcopenshell_aggregation_type_t* handle);
void ifcopenshell_entity_destroy(ifcopenshell_entity_t* handle);
void ifcopenshell_attribute_destroy(ifcopenshell_attribute_t* handle);
void ifcopenshell_inverse_attribute_destroy(ifcopenshell_inverse_attribute_t* handle);
void ifcopenshell_parse_attribute_value_destroy(ifcopenshell_parse_attribute_value_t* handle);
void ifcopenshell_parse_instance_list_destroy(ifcopenshell_parse_instance_list_t* handle);
void ifcopenshell_geom_iterator_destroy(ifcopenshell_geom_iterator_t* handle);
void ifcopenshell_geom_settings_destroy(ifcopenshell_geom_settings_t* handle);
void ifcopenshell_geom_serializer_settings_destroy(ifcopenshell_geom_serializer_settings_t* handle);
void ifcopenshell_geom_geometry_serializer_destroy(ifcopenshell_geom_geometry_serializer_t* handle);
void ifcopenshell_geom_serializer_destroy(ifcopenshell_geom_serializer_t* handle);
void ifcopenshell_geom_buffer_destroy(ifcopenshell_geom_buffer_t* handle);
void ifcopenshell_geom_tree_destroy(ifcopenshell_geom_tree_t* handle);
void ifcopenshell_geom_tree_clash_list_destroy(ifcopenshell_geom_tree_clash_list_t* handle);
void ifcopenshell_geom_tree_clash_destroy(ifcopenshell_geom_tree_clash_t* handle);
void ifcopenshell_geom_tree_ray_intersection_list_destroy(ifcopenshell_geom_tree_ray_intersection_list_t* handle);
void ifcopenshell_geom_tree_ray_intersection_destroy(ifcopenshell_geom_tree_ray_intersection_t* handle);
void ifcopenshell_geom_transformation_destroy(ifcopenshell_geom_transformation_t* handle);
void ifcopenshell_geom_element_destroy(ifcopenshell_geom_element_t* handle);
void ifcopenshell_geom_brep_element_destroy(ifcopenshell_geom_brep_element_t* handle);
void ifcopenshell_geom_triangulation_element_destroy(ifcopenshell_geom_triangulation_element_t* handle);
void ifcopenshell_geom_serialized_element_destroy(ifcopenshell_geom_serialized_element_t* handle);
void ifcopenshell_geom_triangulation_destroy(ifcopenshell_geom_triangulation_t* handle);
void ifcopenshell_geom_brep_representation_destroy(ifcopenshell_geom_brep_representation_t* handle);
void ifcopenshell_geom_serialization_destroy(ifcopenshell_geom_serialization_t* handle);
void ifcopenshell_geom_conversion_result_shape_destroy(ifcopenshell_geom_conversion_result_shape_t* handle);
void ifcopenshell_geom_opaque_number_destroy(ifcopenshell_geom_opaque_number_t* handle);
void ifcopenshell_geom_svgfill_polygon_destroy(ifcopenshell_geom_svgfill_polygon_t* handle);
void ifcopenshell_geom_function_item_evaluator_destroy(ifcopenshell_geom_function_item_evaluator_t* handle);
void ifcopenshell_geom_taxonomy_item_destroy(ifcopenshell_geom_taxonomy_item_t* handle);
void ifcopenshell_geom_taxonomy_matrix4_destroy(ifcopenshell_geom_taxonomy_matrix4_t* handle);
void ifcopenshell_geom_taxonomy_point3_destroy(ifcopenshell_geom_taxonomy_point3_t* handle);
void ifcopenshell_geom_taxonomy_direction3_destroy(ifcopenshell_geom_taxonomy_direction3_t* handle);
void ifcopenshell_geom_taxonomy_style_destroy(ifcopenshell_geom_taxonomy_style_t* handle);
void ifcopenshell_geom_taxonomy_colour_destroy(ifcopenshell_geom_taxonomy_colour_t* handle);
void ifcopenshell_geom_taxonomy_line_destroy(ifcopenshell_geom_taxonomy_line_t* handle);
void ifcopenshell_geom_taxonomy_circle_destroy(ifcopenshell_geom_taxonomy_circle_t* handle);
void ifcopenshell_geom_taxonomy_ellipse_destroy(ifcopenshell_geom_taxonomy_ellipse_t* handle);
void ifcopenshell_geom_taxonomy_bspline_curve_destroy(ifcopenshell_geom_taxonomy_bspline_curve_t* handle);
void ifcopenshell_geom_taxonomy_offset_curve_destroy(ifcopenshell_geom_taxonomy_offset_curve_t* handle);
void ifcopenshell_geom_taxonomy_edge_destroy(ifcopenshell_geom_taxonomy_edge_t* handle);
void ifcopenshell_geom_taxonomy_loop_destroy(ifcopenshell_geom_taxonomy_loop_t* handle);
void ifcopenshell_geom_taxonomy_face_destroy(ifcopenshell_geom_taxonomy_face_t* handle);
void ifcopenshell_geom_taxonomy_shell_destroy(ifcopenshell_geom_taxonomy_shell_t* handle);
void ifcopenshell_geom_taxonomy_solid_destroy(ifcopenshell_geom_taxonomy_solid_t* handle);
void ifcopenshell_geom_taxonomy_plane_destroy(ifcopenshell_geom_taxonomy_plane_t* handle);
void ifcopenshell_geom_taxonomy_cylinder_destroy(ifcopenshell_geom_taxonomy_cylinder_t* handle);
void ifcopenshell_geom_taxonomy_sphere_destroy(ifcopenshell_geom_taxonomy_sphere_t* handle);
void ifcopenshell_geom_taxonomy_torus_destroy(ifcopenshell_geom_taxonomy_torus_t* handle);
void ifcopenshell_geom_taxonomy_bspline_surface_destroy(ifcopenshell_geom_taxonomy_bspline_surface_t* handle);
void ifcopenshell_geom_taxonomy_collection_destroy(ifcopenshell_geom_taxonomy_collection_t* handle);
void ifcopenshell_geom_taxonomy_loft_destroy(ifcopenshell_geom_taxonomy_loft_t* handle);
void ifcopenshell_geom_taxonomy_extrusion_destroy(ifcopenshell_geom_taxonomy_extrusion_t* handle);
void ifcopenshell_geom_taxonomy_revolve_destroy(ifcopenshell_geom_taxonomy_revolve_t* handle);
void ifcopenshell_geom_taxonomy_sweep_along_curve_destroy(ifcopenshell_geom_taxonomy_sweep_along_curve_t* handle);
void ifcopenshell_geom_taxonomy_node_destroy(ifcopenshell_geom_taxonomy_node_t* handle);
void ifcopenshell_geom_taxonomy_boolean_result_destroy(ifcopenshell_geom_taxonomy_boolean_result_t* handle);
void ifcopenshell_instance_list_destroy(ifcopenshell_instance_list_t* value);
void ifcopenshell_geom_svgfill_polygon_list_destroy(ifcopenshell_geom_svgfill_polygon_list_t* value);
void ifcopenshell_geom_conversion_result_shape_list_destroy(ifcopenshell_geom_conversion_result_shape_list_t* value);
void ifcopenshell_declaration_list_destroy(ifcopenshell_declaration_list_t* value);
void ifcopenshell_entity_list_destroy(ifcopenshell_entity_list_t* value);
void ifcopenshell_enumeration_list_destroy(ifcopenshell_enumeration_list_t* value);
void ifcopenshell_select_type_list_destroy(ifcopenshell_select_type_list_t* value);
void ifcopenshell_type_declaration_list_destroy(ifcopenshell_type_declaration_list_t* value);
void ifcopenshell_attribute_list_destroy(ifcopenshell_attribute_list_t* value);
void ifcopenshell_inverse_attribute_list_destroy(ifcopenshell_inverse_attribute_list_t* value);
void ifcopenshell_geom_taxonomy_style_list_destroy(ifcopenshell_geom_taxonomy_style_list_t* value);
void ifcopenshell_geom_taxonomy_item_list_destroy(ifcopenshell_geom_taxonomy_item_list_t* value);
void ifcopenshell_geom_element_list_destroy(ifcopenshell_geom_element_list_t* value);
void ifcopenshell_instance_list_list_destroy(ifcopenshell_instance_list_list_t* value);




bool ifcopenshell_geom_create_xml_serializer(ifcopenshell_file_t* file, const char* filename, ifcopenshell_geom_serializer_t** out_result);
bool ifcopenshell_geom_create_tree(ifcopenshell_geom_tree_t** out_result);
bool ifcopenshell_geom_create_tree_from_file(ifcopenshell_file_t* file, ifcopenshell_geom_tree_t** out_result);
bool ifcopenshell_geom_create_tree_from_file_with_settings(ifcopenshell_file_t* file, ifcopenshell_geom_settings_t* settings, ifcopenshell_geom_tree_t** out_result);
bool ifcopenshell_geom_create_tree_from_iterator(ifcopenshell_geom_iterator_t* iterator, ifcopenshell_geom_tree_t** out_result);
bool ifcopenshell_geom_create_json_serializer(ifcopenshell_file_t* file, const char* filename, ifcopenshell_geom_serializer_t** out_result);
bool ifcopenshell_geom_create_rocksdb_serializer_streaming(const char* input_filename, const char* rocksdb_filename, ifcopenshell_geom_serializer_t** out_result);
bool ifcopenshell_geom_create_buffer(ifcopenshell_geom_buffer_t** out_result);
bool ifcopenshell_geom_create_buffer_from_filename(const char* filename, ifcopenshell_geom_buffer_t** out_result);
bool ifcopenshell_geom_create_settings(ifcopenshell_geom_settings_t** out_result);
bool ifcopenshell_geom_create_serializer_settings(ifcopenshell_geom_serializer_settings_t** out_result);
bool ifcopenshell_parse_argument_type_to_string(int32_t type, ifcopenshell_string_t* out_result);
bool ifcopenshell_parse_clear_plugin_search_paths(void);
bool ifcopenshell_parse_clear_schemas(void);
bool ifcopenshell_parse_escape_xml(const char* text);
bool ifcopenshell_parse_from_parameter_type(ifcopenshell_parameter_type_t* parameter_type, int32_t* out_result);
bool ifcopenshell_parse_general_token_ptr(size_t start, const char* token, int32_t* out_result);
bool ifcopenshell_parse_get_feature(const char* name, bool* out_result);
bool ifcopenshell_parse_get_info_json(ifcopenshell_instance_t* instance, bool include_identifier, ifcopenshell_string_t* out_result);
bool ifcopenshell_parse_get_log(ifcopenshell_string_t* out_result);
bool ifcopenshell_parse_get_plugin_search_paths(ifcopenshell_string_list_t* out_result);
bool ifcopenshell_parse_get_si_equivalent(ifcopenshell_instance_t* named_unit, double* out_result);
bool ifcopenshell_parse_guess_file_type(const char* path, int32_t* out_result);
bool ifcopenshell_parse_instance_list_create_from_handles(const ifcopenshell_instance_list_t* instances, ifcopenshell_parse_instance_list_t** out_result);
bool ifcopenshell_parse_make_aggregate(int32_t element_type, int32_t* out_result);
bool ifcopenshell_parse_new_file(const char* schema_identifier, int32_t file_type, const char* path, ifcopenshell_file_t** out_result);
bool ifcopenshell_parse_open(const char* path, bool readonly, ifcopenshell_file_t** out_result);
bool ifcopenshell_parse_open_bypass(const char* path, const ifcopenshell_string_list_t* type_names, ifcopenshell_file_t** out_result);
bool ifcopenshell_parse_operator_token_ptr(size_t start, const char* data, int32_t* out_result);
bool ifcopenshell_parse_read_memory(void* data, int32_t length, ifcopenshell_file_t** out_result);
bool ifcopenshell_parse_register_schema(ifcopenshell_schema_t* schema);
bool ifcopenshell_parse_sanitate_material_name(const char* material_name);
bool ifcopenshell_parse_schema_by_name(const char* schema_name, ifcopenshell_schema_t** out_result);
bool ifcopenshell_parse_schema_names(ifcopenshell_string_list_t* out_result);
bool ifcopenshell_parse_schema_plugin_registration_symbol(ifcopenshell_string_t* out_result);
bool ifcopenshell_parse_set_feature(const char* name, bool value);
bool ifcopenshell_parse_set_log_format_json(void);
bool ifcopenshell_parse_set_log_format_text(void);
bool ifcopenshell_parse_set_plugin_search_paths(const ifcopenshell_string_list_t* paths);
bool ifcopenshell_parse_si_prefix_to_value(const char* prefix, double* out_result);
bool ifcopenshell_parse_stream(ifcopenshell_instance_streamer_t** out_result);
bool ifcopenshell_parse_stream_from_path(const char* path, bool mmap, ifcopenshell_instance_streamer_t** out_result);
bool ifcopenshell_parse_stream_from_string(const char* data, ifcopenshell_instance_streamer_t** out_result);
bool ifcopenshell_parse_traverse(ifcopenshell_instance_t* instance, int32_t max_depth, ifcopenshell_parse_instance_list_t** out_result);
bool ifcopenshell_parse_traverse_breadth_first(ifcopenshell_instance_t* instance, int32_t max_depth, ifcopenshell_parse_instance_list_t** out_result);
bool ifcopenshell_parse_turn_off_detailed_logging(void);
bool ifcopenshell_parse_turn_on_detailed_logging(void);
bool ifcopenshell_parse_unescape_xml(const char* text);
bool ifcopenshell_parse_valid_binary_string(const char* binary_string, bool* out_result);
bool ifcopenshell_parse_version(ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_arrange_polygons(const ifcopenshell_geom_svgfill_polygon_list_t* polygons_cpp, ifcopenshell_geom_svgfill_polygon_list_t* out_result);
bool ifcopenshell_geom_convert_loop_to_function_item(ifcopenshell_geom_taxonomy_item_t* loop_item_cpp, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_create_epeck_from_double(double value, ifcopenshell_geom_opaque_number_t** out_result);
bool ifcopenshell_geom_create_epeck_from_int(int32_t value, ifcopenshell_geom_opaque_number_t** out_result);
bool ifcopenshell_geom_create_epeck_from_string(const char* value_cpp, ifcopenshell_geom_opaque_number_t** out_result);
bool ifcopenshell_geom_create_function_item_evaluator(ifcopenshell_geom_settings_t* settings_cpp, ifcopenshell_geom_taxonomy_item_t* fn_item_cpp, ifcopenshell_geom_function_item_evaluator_t** out_result);
bool ifcopenshell_geom_create_geometry_serializer_by_path(const char* format, const char* output_filename, const char* output_temp_filename, ifcopenshell_geom_settings_t* geometry_settings, ifcopenshell_geom_serializer_settings_t* serializer_settings, ifcopenshell_geom_geometry_serializer_t** out_result);
bool ifcopenshell_geom_create_geometry_serializer_by_stream(const char* format, ifcopenshell_geom_buffer_t* output, ifcopenshell_geom_buffer_t* output_temp, ifcopenshell_geom_settings_t* geometry_settings, ifcopenshell_geom_serializer_settings_t* serializer_settings, ifcopenshell_geom_geometry_serializer_t** out_result);
bool ifcopenshell_geom_create_iterator(const char* geometry_library_cpp, ifcopenshell_geom_settings_t* settings_cpp, ifcopenshell_file_t* file_cpp, int32_t num_threads, ifcopenshell_geom_iterator_t** out_result);
bool ifcopenshell_geom_create_iterator_with_include_exclude(const char* geometry_library_cpp, ifcopenshell_geom_settings_t* settings_cpp, ifcopenshell_file_t* file_cpp, const ifcopenshell_string_list_t* elems_cpp, bool include, int32_t num_threads, ifcopenshell_geom_iterator_t** out_result);
bool ifcopenshell_geom_create_iterator_with_include_exclude_globalid(const char* geometry_library_cpp, ifcopenshell_geom_settings_t* settings_cpp, ifcopenshell_file_t* file_cpp, const ifcopenshell_string_list_t* elems_cpp, bool include, int32_t num_threads, ifcopenshell_geom_iterator_t** out_result);
bool ifcopenshell_geom_create_iterator_with_include_exclude_id(const char* geometry_library_cpp, ifcopenshell_geom_settings_t* settings_cpp, ifcopenshell_file_t* file_cpp, const ifcopenshell_int32_list_t* elems_cpp, bool include, int32_t num_threads, ifcopenshell_geom_iterator_t** out_result);
bool ifcopenshell_geom_create_shape(ifcopenshell_geom_settings_t* settings_cpp, ifcopenshell_instance_t* instance_cpp, ifcopenshell_instance_t* representation, const char* geometry_library, ifcopenshell_geom_element_t** out_result);
bool ifcopenshell_geom_line_segments_to_polygons(int32_t solver, double eps, const char* segments_json_cpp, ifcopenshell_geom_svgfill_polygon_list_t* out_result);
bool ifcopenshell_geom_map_shape(ifcopenshell_geom_settings_t* settings_cpp, ifcopenshell_instance_t* instance_cpp, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_nary_union(const ifcopenshell_geom_conversion_result_shape_list_t* shapes_cpp, ifcopenshell_geom_conversion_result_shape_t** out_result);
bool ifcopenshell_geom_plugin_is_loaded(const char* kind, const char* id, bool* out_result);
bool ifcopenshell_geom_plugin_load(const char* kind, const char* id, bool* out_result);
bool ifcopenshell_geom_svg_to_line_segments(const char* svg_data_cpp, const char* class_name, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_svg_to_polygons(const char* svg_data_cpp, const char* class_name, ifcopenshell_geom_svgfill_polygon_list_t* out_result);
bool ifcopenshell_geom_taxonomy_create_boolean_result(int32_t operation, ifcopenshell_geom_taxonomy_boolean_result_t** out_result);
bool ifcopenshell_geom_taxonomy_create_box(double dx, double dy, double dz, ifcopenshell_geom_taxonomy_solid_t** out_result);
bool ifcopenshell_geom_taxonomy_create_bspline_curve(int32_t degree, ifcopenshell_geom_taxonomy_bspline_curve_t** out_result);
bool ifcopenshell_geom_taxonomy_create_bspline_surface(int32_t degree_u, int32_t degree_v, ifcopenshell_geom_taxonomy_bspline_surface_t** out_result);
bool ifcopenshell_geom_taxonomy_create_circle(double origin_x, double origin_y, double origin_z, double dir_x, double dir_y, double dir_z, double radius, ifcopenshell_geom_taxonomy_circle_t** out_result);
bool ifcopenshell_geom_taxonomy_create_collection(ifcopenshell_geom_taxonomy_collection_t** out_result);
bool ifcopenshell_geom_taxonomy_create_cylinder(double origin_x, double origin_y, double origin_z, double dir_x, double dir_y, double dir_z, double radius, ifcopenshell_geom_taxonomy_cylinder_t** out_result);
bool ifcopenshell_geom_taxonomy_create_direction3(double x, double y, double z, ifcopenshell_geom_taxonomy_direction3_t** out_result);
bool ifcopenshell_geom_taxonomy_create_ellipse(double origin_x, double origin_y, double origin_z, double dir_x, double dir_y, double dir_z, double radius1, double radius2, ifcopenshell_geom_taxonomy_ellipse_t** out_result);
bool ifcopenshell_geom_taxonomy_create_extrusion(ifcopenshell_geom_taxonomy_item_t* basis_cpp, ifcopenshell_geom_taxonomy_direction3_t* direction_cpp, double depth, ifcopenshell_geom_taxonomy_extrusion_t** out_result);
bool ifcopenshell_geom_taxonomy_create_line(double origin_x, double origin_y, double origin_z, double dir_x, double dir_y, double dir_z, ifcopenshell_geom_taxonomy_line_t** out_result);
bool ifcopenshell_geom_taxonomy_create_loft(ifcopenshell_geom_taxonomy_loft_t** out_result);
bool ifcopenshell_geom_taxonomy_create_node(ifcopenshell_geom_taxonomy_node_t** out_result);
bool ifcopenshell_geom_taxonomy_create_offset_curve(ifcopenshell_geom_taxonomy_item_t* basis, ifcopenshell_geom_taxonomy_direction3_t* reference, double offset, ifcopenshell_geom_taxonomy_offset_curve_t** out_result);
bool ifcopenshell_geom_taxonomy_create_plane(double origin_x, double origin_y, double origin_z, double dir_x, double dir_y, double dir_z, ifcopenshell_geom_taxonomy_plane_t** out_result);
bool ifcopenshell_geom_taxonomy_create_point3(double x, double y, double z, ifcopenshell_geom_taxonomy_point3_t** out_result);
bool ifcopenshell_geom_taxonomy_create_revolve(ifcopenshell_geom_taxonomy_item_t* basis_cpp, ifcopenshell_geom_taxonomy_point3_t* axis_origin_cpp, ifcopenshell_geom_taxonomy_direction3_t* direction_cpp, double angle, ifcopenshell_geom_taxonomy_revolve_t** out_result);
bool ifcopenshell_geom_taxonomy_create_sphere(double origin_x, double origin_y, double origin_z, double dir_x, double dir_y, double dir_z, double radius, ifcopenshell_geom_taxonomy_sphere_t** out_result);
bool ifcopenshell_geom_taxonomy_create_sweep_along_curve(ifcopenshell_geom_taxonomy_face_t* basis_face_cpp, ifcopenshell_geom_taxonomy_item_t* directrix_cpp, ifcopenshell_geom_taxonomy_direction3_t* reference_direction_cpp, ifcopenshell_geom_taxonomy_sweep_along_curve_t** out_result);
bool ifcopenshell_geom_taxonomy_create_torus(double origin_x, double origin_y, double origin_z, double dir_x, double dir_y, double dir_z, double radius1, double radius2, ifcopenshell_geom_taxonomy_torus_t** out_result);
bool ifcopenshell_geom_taxonomy_function_item_end(ifcopenshell_geom_taxonomy_item_t* item_cpp, double* out_result);
bool ifcopenshell_geom_taxonomy_function_item_start(ifcopenshell_geom_taxonomy_item_t* item_cpp, double* out_result);
bool ifcopenshell_geom_helmert_curve_point(double A0, double A1, double A2, double s, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_file_create(ifcopenshell_file_t* self, ifcopenshell_declaration_t* declaration, int32_t instance_id, ifcopenshell_instance_t** out_result);
bool ifcopenshell_file_get_inverses_by_declaration(ifcopenshell_file_t* self, int32_t instance_id, ifcopenshell_declaration_t* declaration, int32_t attribute_index, ifcopenshell_instance_list_t* out_result);
bool ifcopenshell_file_by_type(ifcopenshell_file_t* self, const char* type_name, ifcopenshell_parse_instance_list_t** out_result);
bool ifcopenshell_file_by_type_excl_subtypes(ifcopenshell_file_t* self, const char* type_name, ifcopenshell_parse_instance_list_t** out_result);
bool ifcopenshell_file_add(ifcopenshell_file_t* self, ifcopenshell_instance_t* entity, int32_t instance_id, ifcopenshell_instance_t** out_result);
bool ifcopenshell_file_add_type_ref(ifcopenshell_file_t* self, ifcopenshell_instance_t* new_entity);
bool ifcopenshell_file_batch(ifcopenshell_file_t* self);
bool ifcopenshell_file_build_inverses(ifcopenshell_file_t* self);
bool ifcopenshell_file_build_inverses_(ifcopenshell_file_t* self, ifcopenshell_instance_t* entity);
bool ifcopenshell_file_bypass_type(ifcopenshell_file_t* self, const char* type_name);
bool ifcopenshell_file_create_timestamp(ifcopenshell_file_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_file_fresh_id(ifcopenshell_file_t* self, uint32_t* out_result);
bool ifcopenshell_file_get_inverse_indices_by_id(ifcopenshell_file_t* self, int32_t instance_id, ifcopenshell_int32_list_t* out_result);
bool ifcopenshell_file_get_max_id(ifcopenshell_file_t* self, uint32_t* out_result);
bool ifcopenshell_file_get_total_inverses_by_id(ifcopenshell_file_t* self, int32_t instance_id, size_t* out_result);
bool ifcopenshell_file_ifcroot_type(ifcopenshell_file_t* self, ifcopenshell_declaration_t** out_result);
bool ifcopenshell_file_initialize(ifcopenshell_file_t* self, const char* path, int32_t type, bool read_only, bool* out_result);
bool ifcopenshell_file_by_guid(ifcopenshell_file_t* self, const char* global_id, ifcopenshell_instance_t** out_result);
bool ifcopenshell_file_by_id(ifcopenshell_file_t* self, int32_t instance_id, ifcopenshell_instance_t** out_result);
bool ifcopenshell_file_instances_by_reference(ifcopenshell_file_t* self, int32_t reference_id, ifcopenshell_parse_instance_list_t** out_result);
bool ifcopenshell_file_process_deletion_inverse(ifcopenshell_file_t* self, ifcopenshell_instance_t* entity);
bool ifcopenshell_file_recalculate_id_counter(ifcopenshell_file_t* self);
bool ifcopenshell_file_remove(ifcopenshell_file_t* self, ifcopenshell_instance_t* entity);
bool ifcopenshell_file_remove_type_ref(ifcopenshell_file_t* self, ifcopenshell_instance_t* new_entity);
bool ifcopenshell_file_reset_identity_cache(ifcopenshell_file_t* self);
bool ifcopenshell_file_schema(ifcopenshell_file_t* self, ifcopenshell_schema_t** out_result);
bool ifcopenshell_file_traverse(ifcopenshell_file_t* self, ifcopenshell_instance_t* instance, int32_t max_depth, ifcopenshell_parse_instance_list_t** out_result);
bool ifcopenshell_file_traverse_breadth_first(ifcopenshell_file_t* self, ifcopenshell_instance_t* instance, int32_t max_depth, ifcopenshell_parse_instance_list_t** out_result);
bool ifcopenshell_file_unbatch(ifcopenshell_file_t* self);
bool ifcopenshell_instance_declaration(ifcopenshell_instance_t* self, ifcopenshell_declaration_t** out_result);
bool ifcopenshell_instance_file(ifcopenshell_instance_t* self, ifcopenshell_file_t** out_result);
bool ifcopenshell_instance_get_argument(ifcopenshell_instance_t* self, size_t attribute_index, ifcopenshell_parse_attribute_value_t** out_result);
bool ifcopenshell_instance_id(ifcopenshell_instance_t* self, uint32_t* out_result);
bool ifcopenshell_instance_identity(ifcopenshell_instance_t* self, uint32_t* out_result);
bool ifcopenshell_schema_declaration_by_name(ifcopenshell_schema_t* self, const char* name, ifcopenshell_declaration_t** out_result);
bool ifcopenshell_schema_declaration_by_index(ifcopenshell_schema_t* self, size_t declaration_index, ifcopenshell_declaration_t** out_result);
bool ifcopenshell_schema_declarations(ifcopenshell_schema_t* self, ifcopenshell_declaration_list_t* out_result);
bool ifcopenshell_schema_entities(ifcopenshell_schema_t* self, ifcopenshell_entity_list_t* out_result);
bool ifcopenshell_schema_enumeration_types(ifcopenshell_schema_t* self, ifcopenshell_enumeration_list_t* out_result);
bool ifcopenshell_schema_name(ifcopenshell_schema_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_schema_select_types(ifcopenshell_schema_t* self, ifcopenshell_select_type_list_t* out_result);
bool ifcopenshell_schema_type_declarations(ifcopenshell_schema_t* self, ifcopenshell_type_declaration_list_t* out_result);
bool ifcopenshell_declaration_is_a(ifcopenshell_declaration_t* self, const char* name, bool* out_result);
bool ifcopenshell_declaration_as_entity(ifcopenshell_declaration_t* self, ifcopenshell_entity_t** out_result);
bool ifcopenshell_declaration_as_enumeration_type(ifcopenshell_declaration_t* self, ifcopenshell_enumeration_t** out_result);
bool ifcopenshell_declaration_as_select_type(ifcopenshell_declaration_t* self, ifcopenshell_select_type_t** out_result);
bool ifcopenshell_declaration_as_type_declaration(ifcopenshell_declaration_t* self, ifcopenshell_type_declaration_t** out_result);
bool ifcopenshell_declaration_index_in_schema(ifcopenshell_declaration_t* self, int32_t* out_result);
bool ifcopenshell_declaration_name(ifcopenshell_declaration_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_declaration_name_uc(ifcopenshell_declaration_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_declaration_schema(ifcopenshell_declaration_t* self, ifcopenshell_schema_t** out_result);
bool ifcopenshell_declaration_type(ifcopenshell_declaration_t* self, int32_t* out_result);
bool ifcopenshell_type_declaration_as_type_declaration(ifcopenshell_type_declaration_t* self, ifcopenshell_type_declaration_t** out_result);
bool ifcopenshell_type_declaration_declared_type(ifcopenshell_type_declaration_t* self, ifcopenshell_parameter_type_t** out_result);
bool ifcopenshell_select_type_as_select_type(ifcopenshell_select_type_t* self, ifcopenshell_select_type_t** out_result);
bool ifcopenshell_select_type_select_list(ifcopenshell_select_type_t* self, ifcopenshell_declaration_list_t* out_result);
bool ifcopenshell_enumeration_as_enumeration_type(ifcopenshell_enumeration_t* self, ifcopenshell_enumeration_t** out_result);
bool ifcopenshell_enumeration_enumeration_items(ifcopenshell_enumeration_t* self, ifcopenshell_string_list_t* out_result);
bool ifcopenshell_enumeration_lookup_enum_offset(ifcopenshell_enumeration_t* self, const char* value_name, size_t* out_result);
bool ifcopenshell_enumeration_lookup_enum_value(ifcopenshell_enumeration_t* self, size_t i, ifcopenshell_string_t* out_result);
bool ifcopenshell_parameter_type_as_aggregation_type(ifcopenshell_parameter_type_t* self, ifcopenshell_aggregation_type_t** out_result);
bool ifcopenshell_parameter_type_as_named_type(ifcopenshell_parameter_type_t* self, ifcopenshell_named_type_t** out_result);
bool ifcopenshell_parameter_type_as_simple_type(ifcopenshell_parameter_type_t* self, ifcopenshell_simple_type_t** out_result);
bool ifcopenshell_named_type_is_a(ifcopenshell_named_type_t* self, const char* name, bool* out_result);
bool ifcopenshell_named_type_as_named_type(ifcopenshell_named_type_t* self, ifcopenshell_named_type_t** out_result);
bool ifcopenshell_named_type_declared_type(ifcopenshell_named_type_t* self, ifcopenshell_declaration_t** out_result);
bool ifcopenshell_simple_type_as_simple_type(ifcopenshell_simple_type_t* self, ifcopenshell_simple_type_t** out_result);
bool ifcopenshell_simple_type_declared_type(ifcopenshell_simple_type_t* self, int32_t* out_result);
bool ifcopenshell_aggregation_type_as_aggregation_type(ifcopenshell_aggregation_type_t* self, ifcopenshell_aggregation_type_t** out_result);
bool ifcopenshell_aggregation_type_bound1(ifcopenshell_aggregation_type_t* self, int32_t* out_result);
bool ifcopenshell_aggregation_type_bound2(ifcopenshell_aggregation_type_t* self, int32_t* out_result);
bool ifcopenshell_aggregation_type_type_of_element(ifcopenshell_aggregation_type_t* self, ifcopenshell_parameter_type_t** out_result);
bool ifcopenshell_header_file(ifcopenshell_header_t* self, ifcopenshell_file_t** out_result);
bool ifcopenshell_header_file_description(ifcopenshell_header_t* self, ifcopenshell_file_description_t** out_result);
bool ifcopenshell_header_file_name(ifcopenshell_header_t* self, ifcopenshell_file_name_t** out_result);
bool ifcopenshell_header_file_schema(ifcopenshell_header_t* self, ifcopenshell_file_schema_t** out_result);
bool ifcopenshell_file_description_class(ifcopenshell_file_description_t* self, ifcopenshell_entity_t** out_result);
bool ifcopenshell_file_description_description(ifcopenshell_file_description_t* self, ifcopenshell_string_list_t* out_result);
bool ifcopenshell_file_description_implementation_level(ifcopenshell_file_description_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_file_description_initialize(ifcopenshell_file_description_t* self, const ifcopenshell_string_list_t* v1_description, const char* v2_implementation_level, ifcopenshell_file_description_t** out_result);
bool ifcopenshell_file_description_setdescription(ifcopenshell_file_description_t* self, const ifcopenshell_string_list_t* v);
bool ifcopenshell_file_description_setimplementation_level(ifcopenshell_file_description_t* self, const char* v);
bool ifcopenshell_file_name_class(ifcopenshell_file_name_t* self, ifcopenshell_entity_t** out_result);
bool ifcopenshell_file_name_author(ifcopenshell_file_name_t* self, ifcopenshell_string_list_t* out_result);
bool ifcopenshell_file_name_authorization(ifcopenshell_file_name_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_file_name_initialize(ifcopenshell_file_name_t* self, const char* v1_name, const char* v2_time_stamp, const ifcopenshell_string_list_t* v3_author, const ifcopenshell_string_list_t* v4_organization, const char* v5_preprocessor_version, const char* v6_originating_system, const char* v7_authorization, ifcopenshell_file_name_t** out_result);
bool ifcopenshell_file_name_name(ifcopenshell_file_name_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_file_name_organization(ifcopenshell_file_name_t* self, ifcopenshell_string_list_t* out_result);
bool ifcopenshell_file_name_originating_system(ifcopenshell_file_name_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_file_name_preprocessor_version(ifcopenshell_file_name_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_file_name_setauthor(ifcopenshell_file_name_t* self, const ifcopenshell_string_list_t* v);
bool ifcopenshell_file_name_setauthorization(ifcopenshell_file_name_t* self, const char* v);
bool ifcopenshell_file_name_setname(ifcopenshell_file_name_t* self, const char* v);
bool ifcopenshell_file_name_setorganization(ifcopenshell_file_name_t* self, const ifcopenshell_string_list_t* v);
bool ifcopenshell_file_name_setoriginating_system(ifcopenshell_file_name_t* self, const char* v);
bool ifcopenshell_file_name_setpreprocessor_version(ifcopenshell_file_name_t* self, const char* v);
bool ifcopenshell_file_name_settime_stamp(ifcopenshell_file_name_t* self, const char* v);
bool ifcopenshell_file_name_time_stamp(ifcopenshell_file_name_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_file_schema_class(ifcopenshell_file_schema_t* self, ifcopenshell_entity_t** out_result);
bool ifcopenshell_file_schema_initialize(ifcopenshell_file_schema_t* self, const ifcopenshell_string_list_t* v1_schema_identifiers, ifcopenshell_file_schema_t** out_result);
bool ifcopenshell_file_schema_schema_identifiers(ifcopenshell_file_schema_t* self, ifcopenshell_string_list_t* out_result);
bool ifcopenshell_file_schema_setschema_identifiers(ifcopenshell_file_schema_t* self, const ifcopenshell_string_list_t* v);
bool ifcopenshell_entity_attribute_index(ifcopenshell_entity_t* self, const char* attr_name, int32_t* out_result);
bool ifcopenshell_entity_all_attributes(ifcopenshell_entity_t* self, ifcopenshell_attribute_list_t* out_result);
bool ifcopenshell_entity_all_inverse_attributes(ifcopenshell_entity_t* self, ifcopenshell_inverse_attribute_list_t* out_result);
bool ifcopenshell_entity_as_entity(ifcopenshell_entity_t* self, ifcopenshell_entity_t** out_result);
bool ifcopenshell_entity_attribute_by_index(ifcopenshell_entity_t* self, size_t index, ifcopenshell_attribute_t** out_result);
bool ifcopenshell_entity_attribute_count(ifcopenshell_entity_t* self, size_t* out_result);
bool ifcopenshell_entity_attributes(ifcopenshell_entity_t* self, ifcopenshell_attribute_list_t* out_result);
bool ifcopenshell_entity_derived(ifcopenshell_entity_t* self, ifcopenshell_bool_list_t* out_result);
bool ifcopenshell_entity_inverse_attributes(ifcopenshell_entity_t* self, ifcopenshell_inverse_attribute_list_t* out_result);
bool ifcopenshell_entity_is_abstract(ifcopenshell_entity_t* self, bool* out_result);
bool ifcopenshell_entity_set_attributes(ifcopenshell_entity_t* self, const ifcopenshell_attribute_list_t* attributes, const ifcopenshell_bool_list_t* derived);
bool ifcopenshell_entity_set_inverse_attributes(ifcopenshell_entity_t* self, const ifcopenshell_inverse_attribute_list_t* inverse_attributes);
bool ifcopenshell_entity_set_subtypes(ifcopenshell_entity_t* self, const ifcopenshell_entity_list_t* subtypes);
bool ifcopenshell_entity_subtypes(ifcopenshell_entity_t* self, ifcopenshell_entity_list_t* out_result);
bool ifcopenshell_entity_supertype(ifcopenshell_entity_t* self, ifcopenshell_entity_t** out_result);
bool ifcopenshell_attribute_name(ifcopenshell_attribute_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_attribute_optional(ifcopenshell_attribute_t* self, bool* out_result);
bool ifcopenshell_attribute_type_of_attribute(ifcopenshell_attribute_t* self, ifcopenshell_parameter_type_t** out_result);
bool ifcopenshell_inverse_attribute_attribute_reference(ifcopenshell_inverse_attribute_t* self, ifcopenshell_attribute_t** out_result);
bool ifcopenshell_inverse_attribute_bound1(ifcopenshell_inverse_attribute_t* self, int32_t* out_result);
bool ifcopenshell_inverse_attribute_bound2(ifcopenshell_inverse_attribute_t* self, int32_t* out_result);
bool ifcopenshell_inverse_attribute_entity_reference(ifcopenshell_inverse_attribute_t* self, ifcopenshell_entity_t** out_result);
bool ifcopenshell_inverse_attribute_name(ifcopenshell_inverse_attribute_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_instance_streamer_bypassed_instances(ifcopenshell_instance_streamer_t* self, ifcopenshell_uint32_list_t* out_result);
bool ifcopenshell_instance_streamer_has_semicolon(ifcopenshell_instance_streamer_t* self, bool* out_result);
bool ifcopenshell_instance_streamer_push_page(ifcopenshell_instance_streamer_t* self, const char* page_data);
bool ifcopenshell_instance_streamer_semicolon_count(ifcopenshell_instance_streamer_t* self, size_t* out_result);
bool ifcopenshell_geom_triangulation_edges(ifcopenshell_geom_triangulation_t* self, ifcopenshell_int32_list_t* out_result);
bool ifcopenshell_geom_triangulation_edges_item_ids(ifcopenshell_geom_triangulation_t* self, ifcopenshell_int32_list_t* out_result);
bool ifcopenshell_geom_triangulation_faces(ifcopenshell_geom_triangulation_t* self, ifcopenshell_int32_list_t* out_result);
bool ifcopenshell_geom_triangulation_item_ids(ifcopenshell_geom_triangulation_t* self, ifcopenshell_int32_list_t* out_result);
bool ifcopenshell_geom_triangulation_material_ids(ifcopenshell_geom_triangulation_t* self, ifcopenshell_int32_list_t* out_result);
bool ifcopenshell_geom_triangulation_materials(ifcopenshell_geom_triangulation_t* self, ifcopenshell_geom_taxonomy_style_list_t* out_result);
bool ifcopenshell_geom_triangulation_normals(ifcopenshell_geom_triangulation_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_triangulation_polyhedral_faces_with_holes(ifcopenshell_geom_triangulation_t* self, ifcopenshell_int32_list_list_list_t* out_result);
bool ifcopenshell_geom_triangulation_polyhedral_faces_without_holes(ifcopenshell_geom_triangulation_t* self, ifcopenshell_int32_list_list_t* out_result);
bool ifcopenshell_geom_triangulation_uvs(ifcopenshell_geom_triangulation_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_triangulation_verts(ifcopenshell_geom_triangulation_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_iterator_bounds_max(ifcopenshell_geom_iterator_t* self, ifcopenshell_geom_taxonomy_point3_t** out_result);
bool ifcopenshell_geom_iterator_bounds_min(ifcopenshell_geom_iterator_t* self, ifcopenshell_geom_taxonomy_point3_t** out_result);
bool ifcopenshell_geom_iterator_compute_bounds(ifcopenshell_geom_iterator_t* self, bool with_geometry);
bool ifcopenshell_geom_iterator_create(ifcopenshell_geom_iterator_t* self, ifcopenshell_instance_t** out_result);
bool ifcopenshell_geom_iterator_file(ifcopenshell_geom_iterator_t* self, ifcopenshell_file_t** out_result);
bool ifcopenshell_geom_iterator_get(ifcopenshell_geom_iterator_t* self, ifcopenshell_geom_element_t** out_result);
bool ifcopenshell_geom_iterator_get_log(ifcopenshell_geom_iterator_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_iterator_get_native(ifcopenshell_geom_iterator_t* self, ifcopenshell_geom_brep_element_t** out_result);
bool ifcopenshell_geom_iterator_get_object(ifcopenshell_geom_iterator_t* self, int32_t id, ifcopenshell_geom_element_t** out_result);
bool ifcopenshell_geom_iterator_get_task_items(ifcopenshell_geom_iterator_t* self, ifcopenshell_geom_taxonomy_item_list_t* out_result);
bool ifcopenshell_geom_iterator_get_task_products(ifcopenshell_geom_iterator_t* self, ifcopenshell_instance_list_list_t* out_result);
bool ifcopenshell_geom_iterator_had_error_processing_elements(ifcopenshell_geom_iterator_t* self, bool* out_result);
bool ifcopenshell_geom_iterator_initialize(ifcopenshell_geom_iterator_t* self, bool* out_result);
bool ifcopenshell_geom_iterator_progress(ifcopenshell_geom_iterator_t* self, int32_t* out_result);
bool ifcopenshell_geom_iterator_unit_magnitude(ifcopenshell_geom_iterator_t* self, double* out_result);
bool ifcopenshell_geom_iterator_unit_name(ifcopenshell_geom_iterator_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_brep_representation_calculate_projected_surface_area(ifcopenshell_geom_brep_representation_t* self, ifcopenshell_geom_taxonomy_matrix4_t* ax, double along_x, double along_y, double along_z, bool* out_result);
bool ifcopenshell_geom_brep_representation_entity(ifcopenshell_geom_brep_representation_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_brep_representation_id(ifcopenshell_geom_brep_representation_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_brep_representation_item(ifcopenshell_geom_brep_representation_t* self, int32_t i, ifcopenshell_geom_conversion_result_shape_t** out_result);
bool ifcopenshell_geom_brep_representation_item_id(ifcopenshell_geom_brep_representation_t* self, int32_t i, int32_t* out_result);
bool ifcopenshell_geom_brep_representation_settings(ifcopenshell_geom_brep_representation_t* self, ifcopenshell_geom_settings_t** out_result);
bool ifcopenshell_geom_brep_representation_calculate_surface_area(ifcopenshell_geom_brep_representation_t* self, double* out_result);
bool ifcopenshell_geom_brep_representation_calculate_volume(ifcopenshell_geom_brep_representation_t* self, double* out_result);
bool ifcopenshell_geom_brep_representation_size(ifcopenshell_geom_brep_representation_t* self, int32_t* out_result);
bool ifcopenshell_geom_element_context(ifcopenshell_geom_element_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_element_guid(ifcopenshell_geom_element_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_element_id(ifcopenshell_geom_element_t* self, int32_t* out_result);
bool ifcopenshell_geom_element_name(ifcopenshell_geom_element_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_element_parent_id(ifcopenshell_geom_element_t* self, int32_t* out_result);
bool ifcopenshell_geom_element_parents(ifcopenshell_geom_element_t* self, ifcopenshell_geom_element_list_t* out_result);
bool ifcopenshell_geom_element_product(ifcopenshell_geom_element_t* self, ifcopenshell_instance_t** out_result);
bool ifcopenshell_geom_element_transformation(ifcopenshell_geom_element_t* self, ifcopenshell_geom_transformation_t** out_result);
bool ifcopenshell_geom_element_type(ifcopenshell_geom_element_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_element_unique_id(ifcopenshell_geom_element_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_brep_element_calculate_projected_surface_area(ifcopenshell_geom_brep_element_t* self, double along_x, double along_y, double along_z, bool* out_result);
bool ifcopenshell_geom_brep_element_geometry(ifcopenshell_geom_brep_element_t* self, ifcopenshell_geom_brep_representation_t** out_result);
bool ifcopenshell_geom_triangulation_element_geometry(ifcopenshell_geom_triangulation_element_t* self, ifcopenshell_geom_triangulation_t** out_result);
bool ifcopenshell_geom_serialized_element_geometry(ifcopenshell_geom_serialized_element_t* self, ifcopenshell_geom_serialization_t** out_result);
bool ifcopenshell_geom_conversion_result_shape_is_manifold(ifcopenshell_geom_conversion_result_shape_t* self, bool* out_result);
bool ifcopenshell_geom_conversion_result_shape_num_edges(ifcopenshell_geom_conversion_result_shape_t* self, int32_t* out_result);
bool ifcopenshell_geom_conversion_result_shape_num_faces(ifcopenshell_geom_conversion_result_shape_t* self, int32_t* out_result);
bool ifcopenshell_geom_conversion_result_shape_num_vertices(ifcopenshell_geom_conversion_result_shape_t* self, int32_t* out_result);
bool ifcopenshell_geom_conversion_result_shape_surface_area_along_direction(ifcopenshell_geom_conversion_result_shape_t* self, double tol, ifcopenshell_geom_taxonomy_matrix4_t* arg_1, double along_x, double along_y, double along_z, bool* out_result);
bool ifcopenshell_geom_conversion_result_shape_surface_genus(ifcopenshell_geom_conversion_result_shape_t* self, int32_t* out_result);
bool ifcopenshell_geom_function_item_evaluator_evaluation_points(ifcopenshell_geom_function_item_evaluator_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_function_item_evaluator_evaluation_points_range(ifcopenshell_geom_function_item_evaluator_t* self, double ustart, double uend, int32_t nsteps, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_function_item_evaluator_evaluate(ifcopenshell_geom_function_item_evaluator_t* self, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_function_item_evaluator_evaluate_range(ifcopenshell_geom_function_item_evaluator_t* self, double ustart, double uend, int32_t nsteps, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_serialization_brep_data(ifcopenshell_geom_serialization_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_serialization_surface_style_ids(ifcopenshell_geom_serialization_t* self, ifcopenshell_int32_list_t* out_result);
bool ifcopenshell_geom_serialization_surface_styles(ifcopenshell_geom_serialization_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_geometry_serializer_geometry_settings(ifcopenshell_geom_geometry_serializer_t* self, ifcopenshell_geom_settings_t** out_result);
bool ifcopenshell_geom_geometry_serializer_settings(ifcopenshell_geom_geometry_serializer_t* self, ifcopenshell_geom_serializer_settings_t** out_result);
bool ifcopenshell_geom_geometry_serializer_write_triangulation_element(ifcopenshell_geom_geometry_serializer_t* self, ifcopenshell_geom_triangulation_element_t* o);
bool ifcopenshell_geom_geometry_serializer_write_brep_element(ifcopenshell_geom_geometry_serializer_t* self, ifcopenshell_geom_brep_element_t* o);
bool ifcopenshell_geom_geometry_serializer_finalize(ifcopenshell_geom_geometry_serializer_t* self);
bool ifcopenshell_geom_geometry_serializer_is_tesselated(ifcopenshell_geom_geometry_serializer_t* self, bool* out_result);
bool ifcopenshell_geom_geometry_serializer_is_streaming(ifcopenshell_geom_geometry_serializer_t* self, bool* out_result);
bool ifcopenshell_geom_geometry_serializer_read(ifcopenshell_geom_geometry_serializer_t* self, ifcopenshell_file_t* f, const char* guid, const char* representation_id, int32_t rt, ifcopenshell_geom_element_t** out_result);
bool ifcopenshell_geom_geometry_serializer_ready(ifcopenshell_geom_geometry_serializer_t* self, bool* out_result);
bool ifcopenshell_geom_geometry_serializer_set_file(ifcopenshell_geom_geometry_serializer_t* self, ifcopenshell_file_t* arg_0);
bool ifcopenshell_geom_geometry_serializer_set_unit_name_and_magnitude(ifcopenshell_geom_geometry_serializer_t* self, const char* name, double magnitude);
bool ifcopenshell_geom_geometry_serializer_write_header(ifcopenshell_geom_geometry_serializer_t* self);
bool ifcopenshell_geom_taxonomy_style_has_specularity(ifcopenshell_geom_taxonomy_style_t* self, bool* out_result);
bool ifcopenshell_geom_taxonomy_style_has_transparency(ifcopenshell_geom_taxonomy_style_t* self, bool* out_result);
bool ifcopenshell_geom_opaque_number_to_double(ifcopenshell_geom_opaque_number_t* self, double* out_result);
bool ifcopenshell_geom_opaque_number_to_string(ifcopenshell_geom_opaque_number_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_serializer_finalize(ifcopenshell_geom_serializer_t* self);
bool ifcopenshell_geom_serializer_is_streaming(ifcopenshell_geom_serializer_t* self, bool* out_result);
bool ifcopenshell_geom_serializer_ready(ifcopenshell_geom_serializer_t* self, bool* out_result);
bool ifcopenshell_geom_serializer_set_file(ifcopenshell_geom_serializer_t* self, ifcopenshell_file_t* arg_0);
bool ifcopenshell_geom_serializer_write_header(ifcopenshell_geom_serializer_t* self);
bool ifcopenshell_geom_settings_get_type(ifcopenshell_geom_settings_t* self, const char* name, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_settings_setting_names(ifcopenshell_geom_settings_t* self, ifcopenshell_string_list_t* out_result);
bool ifcopenshell_geom_serializer_settings_get_type(ifcopenshell_geom_serializer_settings_t* self, const char* name, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_serializer_settings_setting_names(ifcopenshell_geom_serializer_settings_t* self, ifcopenshell_string_list_t* out_result);
bool ifcopenshell_geom_buffer_get_value(ifcopenshell_geom_buffer_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_buffer_is_ready(ifcopenshell_geom_buffer_t* self, bool* out_result);
bool ifcopenshell_geom_taxonomy_item_hash(ifcopenshell_geom_taxonomy_item_t* self, size_t* out_result);
bool ifcopenshell_geom_taxonomy_item_identity(ifcopenshell_geom_taxonomy_item_t* self, uint32_t* out_result);
bool ifcopenshell_geom_taxonomy_item_kind(ifcopenshell_geom_taxonomy_item_t* self, int32_t* out_result);
bool ifcopenshell_geom_tree_enable_face_styles(ifcopenshell_geom_tree_t* self, bool* out_result);
bool ifcopenshell_geom_tree_set_enable_face_styles(ifcopenshell_geom_tree_t* self, bool enable);
bool ifcopenshell_geom_tree_add_file(ifcopenshell_geom_tree_t* self, ifcopenshell_file_t* file, ifcopenshell_geom_settings_t* settings);
bool ifcopenshell_geom_tree_add_iterator(ifcopenshell_geom_tree_t* self, ifcopenshell_geom_iterator_t* iterator);
bool ifcopenshell_geom_tree_clash_clearance_many(ifcopenshell_geom_tree_t* self, const ifcopenshell_instance_list_t* set_a, const ifcopenshell_instance_list_t* set_b, double clearance, bool check_all, ifcopenshell_geom_tree_clash_list_t** out_result);
bool ifcopenshell_geom_tree_clash_collision_many(ifcopenshell_geom_tree_t* self, const ifcopenshell_instance_list_t* set_a, const ifcopenshell_instance_list_t* set_b, bool allow_touching, ifcopenshell_geom_tree_clash_list_t** out_result);
bool ifcopenshell_geom_tree_clash_intersection_many(ifcopenshell_geom_tree_t* self, const ifcopenshell_instance_list_t* set_a, const ifcopenshell_instance_list_t* set_b, double tolerance, bool check_all, ifcopenshell_geom_tree_clash_list_t** out_result);
bool ifcopenshell_geom_tree_distances(ifcopenshell_geom_tree_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_tree_is_manifold(ifcopenshell_geom_tree_t* self, const ifcopenshell_int32_list_t* faces, bool* out_result);
bool ifcopenshell_geom_tree_protrusion_distances(ifcopenshell_geom_tree_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_tree_styles(ifcopenshell_geom_tree_t* self, ifcopenshell_geom_taxonomy_style_list_t* out_result);
bool ifcopenshell_geom_tree_uint8_to_b64(ifcopenshell_geom_tree_t* self, const ifcopenshell_uint8_list_t* uuids_array, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_settings_get_bool(ifcopenshell_geom_settings_t* self, const char* name, bool* out_result);
bool ifcopenshell_geom_settings_set_bool(ifcopenshell_geom_settings_t* self, const char* name, bool value);
bool ifcopenshell_geom_settings_get_int(ifcopenshell_geom_settings_t* self, const char* name, int32_t* out_result);
bool ifcopenshell_geom_settings_set_int(ifcopenshell_geom_settings_t* self, const char* name, int32_t value);
bool ifcopenshell_geom_settings_get_double(ifcopenshell_geom_settings_t* self, const char* name, double* out_result);
bool ifcopenshell_geom_settings_set_double(ifcopenshell_geom_settings_t* self, const char* name, double value);
bool ifcopenshell_geom_settings_get_string(ifcopenshell_geom_settings_t* self, const char* name, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_settings_set_string(ifcopenshell_geom_settings_t* self, const char* name, const char* value);
bool ifcopenshell_geom_settings_get_int_set(ifcopenshell_geom_settings_t* self, const char* name, ifcopenshell_int32_list_t* out_result);
bool ifcopenshell_geom_settings_set_int_set(ifcopenshell_geom_settings_t* self, const char* name, const ifcopenshell_int32_list_t* value);
bool ifcopenshell_geom_settings_get_string_set(ifcopenshell_geom_settings_t* self, const char* name, ifcopenshell_string_list_t* out_result);
bool ifcopenshell_geom_settings_set_string_set(ifcopenshell_geom_settings_t* self, const char* name, const ifcopenshell_string_list_t* value);
bool ifcopenshell_geom_settings_get_double_list(ifcopenshell_geom_settings_t* self, const char* name, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_settings_set_double_list(ifcopenshell_geom_settings_t* self, const char* name, const ifcopenshell_double_list_t* value);
bool ifcopenshell_geom_serializer_settings_get_bool(ifcopenshell_geom_serializer_settings_t* self, const char* name, bool* out_result);
bool ifcopenshell_geom_serializer_settings_set_bool(ifcopenshell_geom_serializer_settings_t* self, const char* name, bool value);
bool ifcopenshell_geom_serializer_settings_get_int(ifcopenshell_geom_serializer_settings_t* self, const char* name, int32_t* out_result);
bool ifcopenshell_geom_serializer_settings_set_int(ifcopenshell_geom_serializer_settings_t* self, const char* name, int32_t value);
bool ifcopenshell_geom_serializer_settings_get_double(ifcopenshell_geom_serializer_settings_t* self, const char* name, double* out_result);
bool ifcopenshell_geom_serializer_settings_set_double(ifcopenshell_geom_serializer_settings_t* self, const char* name, double value);
bool ifcopenshell_geom_serializer_settings_get_string(ifcopenshell_geom_serializer_settings_t* self, const char* name, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_serializer_settings_set_string(ifcopenshell_geom_serializer_settings_t* self, const char* name, const char* value);
bool ifcopenshell_geom_serializer_settings_get_int_set(ifcopenshell_geom_serializer_settings_t* self, const char* name, ifcopenshell_int32_list_t* out_result);
bool ifcopenshell_geom_serializer_settings_set_int_set(ifcopenshell_geom_serializer_settings_t* self, const char* name, const ifcopenshell_int32_list_t* value);
bool ifcopenshell_geom_triangulation_verts_buffer_size(ifcopenshell_geom_triangulation_t* self, size_t* out_result);
bool ifcopenshell_geom_triangulation_faces_buffer_size(ifcopenshell_geom_triangulation_t* self, size_t* out_result);
bool ifcopenshell_geom_triangulation_normals_buffer_size(ifcopenshell_geom_triangulation_t* self, size_t* out_result);
bool ifcopenshell_geom_triangulation_edges_buffer_size(ifcopenshell_geom_triangulation_t* self, size_t* out_result);
bool ifcopenshell_geom_triangulation_material_ids_buffer_size(ifcopenshell_geom_triangulation_t* self, size_t* out_result);
bool ifcopenshell_geom_triangulation_item_ids_buffer_size(ifcopenshell_geom_triangulation_t* self, size_t* out_result);
bool ifcopenshell_geom_triangulation_edges_item_ids_buffer_size(ifcopenshell_geom_triangulation_t* self, size_t* out_result);
bool ifcopenshell_geom_triangulation_uvs_buffer_size(ifcopenshell_geom_triangulation_t* self, size_t* out_result);
bool ifcopenshell_geom_triangulation_material_count(ifcopenshell_geom_triangulation_t* self, size_t* out_result);
bool ifcopenshell_geom_triangulation_material_at(ifcopenshell_geom_triangulation_t* self, size_t index, ifcopenshell_geom_taxonomy_style_t** out_result);
bool ifcopenshell_geom_taxonomy_circle_matrix(ifcopenshell_geom_taxonomy_circle_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result);
bool ifcopenshell_geom_taxonomy_circle_radius(ifcopenshell_geom_taxonomy_circle_t* self, double* out_result);
bool ifcopenshell_geom_taxonomy_line_matrix(ifcopenshell_geom_taxonomy_line_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result);
bool ifcopenshell_geom_taxonomy_line_as_item(ifcopenshell_geom_taxonomy_line_t* self, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_taxonomy_plane_matrix(ifcopenshell_geom_taxonomy_plane_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result);
bool ifcopenshell_geom_taxonomy_ellipse_matrix(ifcopenshell_geom_taxonomy_ellipse_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result);
bool ifcopenshell_geom_taxonomy_ellipse_radius1(ifcopenshell_geom_taxonomy_ellipse_t* self, double* out_result);
bool ifcopenshell_geom_taxonomy_ellipse_radius2(ifcopenshell_geom_taxonomy_ellipse_t* self, double* out_result);
bool ifcopenshell_geom_taxonomy_style_diffuse(ifcopenshell_geom_taxonomy_style_t* self, ifcopenshell_geom_taxonomy_colour_t** out_result);
bool ifcopenshell_geom_taxonomy_style_name(ifcopenshell_geom_taxonomy_style_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_taxonomy_style_specular(ifcopenshell_geom_taxonomy_style_t* self, ifcopenshell_geom_taxonomy_colour_t** out_result);
bool ifcopenshell_geom_taxonomy_style_specularity(ifcopenshell_geom_taxonomy_style_t* self, double* out_result);
bool ifcopenshell_geom_taxonomy_style_surface(ifcopenshell_geom_taxonomy_style_t* self, ifcopenshell_geom_taxonomy_colour_t** out_result);
bool ifcopenshell_geom_taxonomy_style_transparency(ifcopenshell_geom_taxonomy_style_t* self, double* out_result);
bool ifcopenshell_geom_taxonomy_style_use_surface_color(ifcopenshell_geom_taxonomy_style_t* self, bool* out_result);
bool ifcopenshell_geom_taxonomy_sphere_matrix(ifcopenshell_geom_taxonomy_sphere_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result);
bool ifcopenshell_geom_taxonomy_sphere_radius(ifcopenshell_geom_taxonomy_sphere_t* self, double* out_result);
bool ifcopenshell_geom_taxonomy_torus_matrix(ifcopenshell_geom_taxonomy_torus_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result);
bool ifcopenshell_geom_taxonomy_torus_radius1(ifcopenshell_geom_taxonomy_torus_t* self, double* out_result);
bool ifcopenshell_geom_taxonomy_torus_radius2(ifcopenshell_geom_taxonomy_torus_t* self, double* out_result);
bool ifcopenshell_geom_taxonomy_cylinder_matrix(ifcopenshell_geom_taxonomy_cylinder_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result);
bool ifcopenshell_geom_taxonomy_cylinder_radius(ifcopenshell_geom_taxonomy_cylinder_t* self, double* out_result);
bool ifcopenshell_geom_taxonomy_extrusion_basis(ifcopenshell_geom_taxonomy_extrusion_t* self, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_taxonomy_extrusion_depth(ifcopenshell_geom_taxonomy_extrusion_t* self, double* out_result);
bool ifcopenshell_geom_taxonomy_extrusion_direction(ifcopenshell_geom_taxonomy_extrusion_t* self, ifcopenshell_geom_taxonomy_direction3_t** out_result);
bool ifcopenshell_geom_taxonomy_extrusion_matrix(ifcopenshell_geom_taxonomy_extrusion_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result);
bool ifcopenshell_geom_taxonomy_offset_curve_basis(ifcopenshell_geom_taxonomy_offset_curve_t* self, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_taxonomy_offset_curve_offset(ifcopenshell_geom_taxonomy_offset_curve_t* self, double* out_result);
bool ifcopenshell_geom_taxonomy_offset_curve_reference(ifcopenshell_geom_taxonomy_offset_curve_t* self, ifcopenshell_geom_taxonomy_direction3_t** out_result);
bool ifcopenshell_geom_taxonomy_offset_curve_as_item(ifcopenshell_geom_taxonomy_offset_curve_t* self, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_taxonomy_revolve_has_angle(ifcopenshell_geom_taxonomy_revolve_t* self, bool* out_result);
bool ifcopenshell_geom_taxonomy_revolve_angle(ifcopenshell_geom_taxonomy_revolve_t* self, double* out_result);
bool ifcopenshell_geom_taxonomy_revolve_axis_origin(ifcopenshell_geom_taxonomy_revolve_t* self, ifcopenshell_geom_taxonomy_point3_t** out_result);
bool ifcopenshell_geom_taxonomy_revolve_basis(ifcopenshell_geom_taxonomy_revolve_t* self, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_taxonomy_revolve_direction(ifcopenshell_geom_taxonomy_revolve_t* self, ifcopenshell_geom_taxonomy_direction3_t** out_result);
bool ifcopenshell_geom_taxonomy_revolve_matrix(ifcopenshell_geom_taxonomy_revolve_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result);
bool ifcopenshell_geom_taxonomy_bspline_curve_degree(ifcopenshell_geom_taxonomy_bspline_curve_t* self, int32_t* out_result);
bool ifcopenshell_geom_taxonomy_bspline_curve_knots(ifcopenshell_geom_taxonomy_bspline_curve_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_taxonomy_bspline_curve_multiplicities(ifcopenshell_geom_taxonomy_bspline_curve_t* self, ifcopenshell_int32_list_t* out_result);
bool ifcopenshell_geom_taxonomy_bspline_curve_has_weights(ifcopenshell_geom_taxonomy_bspline_curve_t* self, bool* out_result);
bool ifcopenshell_geom_taxonomy_bspline_curve_weights(ifcopenshell_geom_taxonomy_bspline_curve_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_taxonomy_bspline_curve_control_point_count(ifcopenshell_geom_taxonomy_bspline_curve_t* self, size_t* out_result);
bool ifcopenshell_geom_taxonomy_bspline_curve_control_point_at(ifcopenshell_geom_taxonomy_bspline_curve_t* self, size_t index, ifcopenshell_geom_taxonomy_point3_t** out_result);
bool ifcopenshell_geom_taxonomy_bspline_curve_as_item(ifcopenshell_geom_taxonomy_bspline_curve_t* self, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_taxonomy_sweep_along_curve_basis(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_taxonomy_sweep_along_curve_has_basis(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, bool* out_result);
bool ifcopenshell_geom_taxonomy_sweep_along_curve_curve(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_taxonomy_sweep_along_curve_has_curve(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, bool* out_result);
bool ifcopenshell_geom_taxonomy_sweep_along_curve_direction(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, ifcopenshell_geom_taxonomy_direction3_t** out_result);
bool ifcopenshell_geom_taxonomy_sweep_along_curve_has_direction(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, bool* out_result);
bool ifcopenshell_geom_taxonomy_sweep_along_curve_matrix(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result);
bool ifcopenshell_geom_taxonomy_sweep_along_curve_has_matrix(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, bool* out_result);
bool ifcopenshell_geom_taxonomy_sweep_along_curve_surface(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_taxonomy_sweep_along_curve_has_surface(ifcopenshell_geom_taxonomy_sweep_along_curve_t* self, bool* out_result);
bool ifcopenshell_geom_taxonomy_face_basis(ifcopenshell_geom_taxonomy_face_t* self, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_taxonomy_face_loop_count(ifcopenshell_geom_taxonomy_face_t* self, size_t* out_result);
bool ifcopenshell_geom_taxonomy_face_loop_at(ifcopenshell_geom_taxonomy_face_t* self, size_t index, ifcopenshell_geom_taxonomy_loop_t** out_result);
bool ifcopenshell_geom_taxonomy_face_matrix(ifcopenshell_geom_taxonomy_face_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result);
bool ifcopenshell_geom_taxonomy_face_as_item(ifcopenshell_geom_taxonomy_face_t* self, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_taxonomy_loft_axis(ifcopenshell_geom_taxonomy_loft_t* self, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_taxonomy_loft_has_axis(ifcopenshell_geom_taxonomy_loft_t* self, bool* out_result);
bool ifcopenshell_geom_taxonomy_loft_item_count(ifcopenshell_geom_taxonomy_loft_t* self, size_t* out_result);
bool ifcopenshell_geom_taxonomy_loft_item_at(ifcopenshell_geom_taxonomy_loft_t* self, size_t index, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_taxonomy_loft_add_item(ifcopenshell_geom_taxonomy_loft_t* self, ifcopenshell_geom_taxonomy_item_t* item);
bool ifcopenshell_geom_taxonomy_loft_set_axis(ifcopenshell_geom_taxonomy_loft_t* self, ifcopenshell_geom_taxonomy_item_t* value);
bool ifcopenshell_geom_taxonomy_loop_edge_count(ifcopenshell_geom_taxonomy_loop_t* self, size_t* out_result);
bool ifcopenshell_geom_taxonomy_loop_edge_at(ifcopenshell_geom_taxonomy_loop_t* self, size_t index, ifcopenshell_geom_taxonomy_edge_t** out_result);
bool ifcopenshell_geom_taxonomy_shell_face_count(ifcopenshell_geom_taxonomy_shell_t* self, size_t* out_result);
bool ifcopenshell_geom_taxonomy_shell_face_at(ifcopenshell_geom_taxonomy_shell_t* self, size_t index, ifcopenshell_geom_taxonomy_face_t** out_result);
bool ifcopenshell_geom_taxonomy_solid_shell_count(ifcopenshell_geom_taxonomy_solid_t* self, size_t* out_result);
bool ifcopenshell_geom_taxonomy_solid_shell_at(ifcopenshell_geom_taxonomy_solid_t* self, size_t index, ifcopenshell_geom_taxonomy_shell_t** out_result);
bool ifcopenshell_geom_taxonomy_solid_matrix(ifcopenshell_geom_taxonomy_solid_t* self, ifcopenshell_geom_taxonomy_matrix4_t** out_result);
bool ifcopenshell_geom_taxonomy_collection_item_count(ifcopenshell_geom_taxonomy_collection_t* self, size_t* out_result);
bool ifcopenshell_geom_taxonomy_collection_item_at(ifcopenshell_geom_taxonomy_collection_t* self, size_t index, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_taxonomy_collection_add_item(ifcopenshell_geom_taxonomy_collection_t* self, ifcopenshell_geom_taxonomy_item_t* item);
bool ifcopenshell_geom_taxonomy_boolean_result_operation(ifcopenshell_geom_taxonomy_boolean_result_t* self, int32_t* out_result);
bool ifcopenshell_geom_taxonomy_boolean_result_item_count(ifcopenshell_geom_taxonomy_boolean_result_t* self, size_t* out_result);
bool ifcopenshell_geom_taxonomy_boolean_result_item_at(ifcopenshell_geom_taxonomy_boolean_result_t* self, size_t index, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_taxonomy_boolean_result_add_item(ifcopenshell_geom_taxonomy_boolean_result_t* self, ifcopenshell_geom_taxonomy_item_t* item);
bool ifcopenshell_geom_taxonomy_bspline_surface_degree_u(ifcopenshell_geom_taxonomy_bspline_surface_t* self, int32_t* out_result);
bool ifcopenshell_geom_taxonomy_bspline_surface_degree_v(ifcopenshell_geom_taxonomy_bspline_surface_t* self, int32_t* out_result);
bool ifcopenshell_geom_taxonomy_bspline_surface_multiplicities_u(ifcopenshell_geom_taxonomy_bspline_surface_t* self, ifcopenshell_int32_list_t* out_result);
bool ifcopenshell_geom_taxonomy_bspline_surface_multiplicities_v(ifcopenshell_geom_taxonomy_bspline_surface_t* self, ifcopenshell_int32_list_t* out_result);
bool ifcopenshell_geom_taxonomy_bspline_surface_knots_u(ifcopenshell_geom_taxonomy_bspline_surface_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_taxonomy_bspline_surface_knots_v(ifcopenshell_geom_taxonomy_bspline_surface_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_taxonomy_bspline_surface_as_item(ifcopenshell_geom_taxonomy_bspline_surface_t* self, ifcopenshell_geom_taxonomy_item_t** out_result);
bool ifcopenshell_geom_tree_style_count(ifcopenshell_geom_tree_t* self, size_t* out_result);
bool ifcopenshell_geom_tree_style_at(ifcopenshell_geom_tree_t* self, size_t index, ifcopenshell_geom_taxonomy_style_t** out_result);
bool ifcopenshell_geom_tree_clash_a(ifcopenshell_geom_tree_clash_t* self, ifcopenshell_instance_t** out_result);
bool ifcopenshell_geom_tree_clash_b(ifcopenshell_geom_tree_clash_t* self, ifcopenshell_instance_t** out_result);
bool ifcopenshell_geom_tree_clash_type(ifcopenshell_geom_tree_clash_t* self, int32_t* out_result);
bool ifcopenshell_geom_tree_clash_distance(ifcopenshell_geom_tree_clash_t* self, double* out_result);
bool ifcopenshell_geom_tree_clash_p1(ifcopenshell_geom_tree_clash_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_tree_clash_p2(ifcopenshell_geom_tree_clash_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_tree_ray_intersection_distance(ifcopenshell_geom_tree_ray_intersection_t* self, double* out_result);
bool ifcopenshell_geom_tree_ray_intersection_dot_product(ifcopenshell_geom_tree_ray_intersection_t* self, double* out_result);
bool ifcopenshell_geom_tree_ray_intersection_normal(ifcopenshell_geom_tree_ray_intersection_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_tree_ray_intersection_position(ifcopenshell_geom_tree_ray_intersection_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_tree_ray_intersection_ray_distance(ifcopenshell_geom_tree_ray_intersection_t* self, double* out_result);
bool ifcopenshell_geom_tree_ray_intersection_style_index(ifcopenshell_geom_tree_ray_intersection_t* self, int32_t* out_result);
bool ifcopenshell_geom_taxonomy_point3_get_data(ifcopenshell_geom_taxonomy_point3_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_taxonomy_direction3_get_data(ifcopenshell_geom_taxonomy_direction3_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_taxonomy_matrix4_get_data(ifcopenshell_geom_taxonomy_matrix4_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_taxonomy_colour_get_data(ifcopenshell_geom_taxonomy_colour_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_transformation_matrix(ifcopenshell_geom_transformation_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_tree_clash_count(ifcopenshell_geom_tree_t* self, ifcopenshell_geom_tree_clash_list_t* clashes, size_t* out_result);
bool ifcopenshell_geom_tree_clash_at(ifcopenshell_geom_tree_t* self, ifcopenshell_geom_tree_clash_list_t* clashes, size_t index, ifcopenshell_geom_tree_clash_t** out_result);
bool ifcopenshell_geom_tree_ray_intersection_count(ifcopenshell_geom_tree_t* self, ifcopenshell_geom_tree_ray_intersection_list_t* intersections, size_t* out_result);
bool ifcopenshell_geom_tree_ray_intersection_at(ifcopenshell_geom_tree_t* self, ifcopenshell_geom_tree_ray_intersection_list_t* intersections, size_t index, ifcopenshell_geom_tree_ray_intersection_t** out_result);
bool ifcopenshell_file_add_entity(ifcopenshell_file_t* self, ifcopenshell_instance_t* instance, uint32_t id, ifcopenshell_instance_t** out_result);
bool ifcopenshell_type_declaration_argument_types(ifcopenshell_type_declaration_t* self, ifcopenshell_string_list_t* out_result);
bool ifcopenshell_enumeration_argument_types(ifcopenshell_enumeration_t* self, ifcopenshell_string_list_t* out_result);
bool ifcopenshell_entity_argument_types(ifcopenshell_entity_t* self, ifcopenshell_string_list_t* out_result);
bool ifcopenshell_parse_attribute_value_as_bool(ifcopenshell_parse_attribute_value_t* self, bool* out_result);
bool ifcopenshell_parse_attribute_value_as_double(ifcopenshell_parse_attribute_value_t* self, double* out_result);
bool ifcopenshell_parse_attribute_value_as_double_list(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_parse_attribute_value_as_double_list_list(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_double_list_list_t* out_result);
bool ifcopenshell_parse_attribute_value_as_enumeration_index(ifcopenshell_parse_attribute_value_t* self, size_t* out_result);
bool ifcopenshell_parse_attribute_value_as_enumeration_type(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_enumeration_t** out_result);
bool ifcopenshell_parse_attribute_value_as_enumeration_value(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_parse_attribute_value_as_instance(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_instance_t** out_result);
bool ifcopenshell_parse_attribute_value_as_instance_id_list_list(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_int32_list_list_t* out_result);
bool ifcopenshell_parse_attribute_value_as_instance_list(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_parse_instance_list_t** out_result);
bool ifcopenshell_parse_attribute_value_as_int32(ifcopenshell_parse_attribute_value_t* self, int32_t* out_result);
bool ifcopenshell_parse_attribute_value_as_int32_list(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_int32_list_t* out_result);
bool ifcopenshell_parse_attribute_value_as_int32_list_list(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_int32_list_list_t* out_result);
bool ifcopenshell_parse_attribute_value_as_logical(ifcopenshell_parse_attribute_value_t* self, int32_t* out_result);
bool ifcopenshell_parse_attribute_value_as_string(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_parse_attribute_value_as_string_list(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_string_list_t* out_result);
bool ifcopenshell_instance_class_name(ifcopenshell_instance_t* self, bool with_schema, ifcopenshell_string_t* out_result);
bool ifcopenshell_file_create_entity_by_name(ifcopenshell_file_t* self, const char* type_name, ifcopenshell_instance_t** out_result);
bool ifcopenshell_file_create_entity_by_name_with_id(ifcopenshell_file_t* self, const char* type_name, uint32_t id, ifcopenshell_instance_t** out_result);
bool ifcopenshell_file_entity_names(ifcopenshell_file_t* self, ifcopenshell_uint32_list_t* out_result);
bool ifcopenshell_file_file_pointer(ifcopenshell_file_t* self, size_t* out_result);
bool ifcopenshell_instance_file_pointer(ifcopenshell_instance_t* self, size_t* out_result);
bool ifcopenshell_parse_instance_list_get(ifcopenshell_parse_instance_list_t* self, size_t index, ifcopenshell_instance_t** out_result);
bool ifcopenshell_instance_get_argument_by_name(ifcopenshell_instance_t* self, const char* name, ifcopenshell_parse_attribute_value_t** out_result);
bool ifcopenshell_instance_get_argument_index(ifcopenshell_instance_t* self, const char* name, uint32_t* out_result);
bool ifcopenshell_instance_get_argument_name(ifcopenshell_instance_t* self, uint32_t index, ifcopenshell_string_t* out_result);
bool ifcopenshell_instance_get_argument_type(ifcopenshell_instance_t* self, uint32_t index, ifcopenshell_string_t* out_result);
bool ifcopenshell_instance_get_attribute_category(ifcopenshell_instance_t* self, const char* name, int32_t* out_result);
bool ifcopenshell_instance_get_attribute_names(ifcopenshell_instance_t* self, ifcopenshell_string_list_t* out_result);
bool ifcopenshell_instance_get_attribute_value(ifcopenshell_instance_t* self, size_t index, ifcopenshell_parse_attribute_value_t** out_result);
bool ifcopenshell_file_get_inverse(ifcopenshell_file_t* self, ifcopenshell_instance_t* instance, ifcopenshell_parse_instance_list_t** out_result);
bool ifcopenshell_instance_get_inverse(ifcopenshell_instance_t* self, const char* name, ifcopenshell_parse_instance_list_t** out_result);
bool ifcopenshell_instance_get_inverse_attribute_by_name(ifcopenshell_instance_t* self, const char* name, ifcopenshell_parse_instance_list_t** out_result);
bool ifcopenshell_instance_get_inverse_attribute_names(ifcopenshell_instance_t* self, ifcopenshell_string_list_t* out_result);
bool ifcopenshell_file_get_inverse_indices(ifcopenshell_file_t* self, ifcopenshell_instance_t* instance, ifcopenshell_int32_list_t* out_result);
bool ifcopenshell_file_get_total_inverses(ifcopenshell_file_t* self, ifcopenshell_instance_t* instance, int32_t* out_result);
bool ifcopenshell_file_get_unit(ifcopenshell_file_t* self, const char* unit_type, double* out_result);
bool ifcopenshell_file_good(ifcopenshell_file_t* self, int32_t* out_result);
bool ifcopenshell_file_header(ifcopenshell_file_t* self, ifcopenshell_header_t** out_result);
bool ifcopenshell_file_header_file_description(ifcopenshell_file_t* self, ifcopenshell_instance_t** out_result);
bool ifcopenshell_file_header_file_name(ifcopenshell_file_t* self, ifcopenshell_instance_t** out_result);
bool ifcopenshell_file_header_file_schema(ifcopenshell_file_t* self, ifcopenshell_instance_t** out_result);
bool ifcopenshell_instance_streamer_inverses(ifcopenshell_instance_streamer_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_instance_is_a(ifcopenshell_instance_t* self, const char* declaration_name, bool* out_result);
bool ifcopenshell_parse_attribute_value_is_null(ifcopenshell_parse_attribute_value_t* self, bool* out_result);
bool ifcopenshell_file_key_value_store_iter(ifcopenshell_file_t* self, const char* prefix, ifcopenshell_string_list_t* out_result);
bool ifcopenshell_file_key_value_store_query(ifcopenshell_file_t* self, const char* key, ifcopenshell_uint8_list_t* out_result);
bool ifcopenshell_parameter_type_kind(ifcopenshell_parameter_type_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_simple_type_kind(ifcopenshell_simple_type_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_aggregation_type_kind(ifcopenshell_aggregation_type_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_instance_streamer_read_instance_json(ifcopenshell_instance_streamer_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_instance_streamer_references(ifcopenshell_instance_streamer_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_file_schema_name(ifcopenshell_file_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_select_type_select_list_names(ifcopenshell_select_type_t* self, ifcopenshell_string_list_t* out_result);
bool ifcopenshell_instance_set_argument_as_aggregate_of_aggregate_of_entity_instance(ifcopenshell_instance_t* self, size_t index, const ifcopenshell_int32_list_list_t* value);
bool ifcopenshell_instance_set_argument_bool(ifcopenshell_instance_t* self, size_t index, bool value);
bool ifcopenshell_instance_set_argument_double(ifcopenshell_instance_t* self, size_t index, double value);
bool ifcopenshell_instance_set_argument_double_list(ifcopenshell_instance_t* self, size_t index, const ifcopenshell_double_list_t* value);
bool ifcopenshell_instance_set_argument_double_list_list(ifcopenshell_instance_t* self, size_t index, const ifcopenshell_double_list_list_t* value);
bool ifcopenshell_instance_set_argument_enumeration(ifcopenshell_instance_t* self, size_t index, ifcopenshell_enumeration_t* enumeration, size_t enumeration_index);
bool ifcopenshell_instance_set_argument_enumeration_by_name(ifcopenshell_instance_t* self, size_t index, const char* value, bool* out_result);
bool ifcopenshell_instance_set_argument_instance(ifcopenshell_instance_t* self, size_t index, ifcopenshell_instance_t* value);
bool ifcopenshell_instance_set_argument_instance_list(ifcopenshell_instance_t* self, size_t index, ifcopenshell_parse_instance_list_t* value);
bool ifcopenshell_instance_set_argument_int32(ifcopenshell_instance_t* self, size_t index, int32_t value);
bool ifcopenshell_instance_set_argument_int32_list(ifcopenshell_instance_t* self, size_t index, const ifcopenshell_int32_list_t* value);
bool ifcopenshell_instance_set_argument_int32_list_list(ifcopenshell_instance_t* self, size_t index, const ifcopenshell_int32_list_list_t* value);
bool ifcopenshell_instance_set_argument_logical(ifcopenshell_instance_t* self, size_t index, int32_t value);
bool ifcopenshell_instance_set_argument_string(ifcopenshell_instance_t* self, size_t index, const char* value);
bool ifcopenshell_instance_set_argument_string_list(ifcopenshell_instance_t* self, size_t index, const ifcopenshell_string_list_t* value);
bool ifcopenshell_instance_set_attribute_value(ifcopenshell_instance_t* self, const char* name, ifcopenshell_parse_attribute_value_t* value);
bool ifcopenshell_parse_attribute_value_size(ifcopenshell_parse_attribute_value_t* self, size_t* out_result);
bool ifcopenshell_parse_instance_list_size(ifcopenshell_parse_instance_list_t* self, size_t* out_result);
bool ifcopenshell_instance_streamer_status(ifcopenshell_instance_streamer_t* self, int32_t* out_result);
bool ifcopenshell_file_storage_mode(ifcopenshell_file_t* self, int32_t* out_result);
bool ifcopenshell_file_to_string(ifcopenshell_file_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_instance_to_string(ifcopenshell_instance_t* self, bool valid_spf, ifcopenshell_string_t* out_result);
bool ifcopenshell_parse_attribute_value_type(ifcopenshell_parse_attribute_value_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_aggregation_type_type_of_aggregation(ifcopenshell_aggregation_type_t* self, int32_t* out_result);
bool ifcopenshell_inverse_attribute_type_of_aggregation(ifcopenshell_inverse_attribute_t* self, int32_t* out_result);
bool ifcopenshell_aggregation_type_type_of_aggregation_string(ifcopenshell_aggregation_type_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_inverse_attribute_type_of_aggregation_string(ifcopenshell_inverse_attribute_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_file_types(ifcopenshell_file_t* self, ifcopenshell_string_list_t* out_result);
bool ifcopenshell_instance_unset_argument(ifcopenshell_instance_t* self, size_t index);
bool ifcopenshell_instance_unset_attribute_value(ifcopenshell_instance_t* self, const char* name);
bool ifcopenshell_file_write(ifcopenshell_file_t* self, const char* path);
bool ifcopenshell_header_write(ifcopenshell_header_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_opaque_number_add(ifcopenshell_geom_opaque_number_t* self, ifcopenshell_geom_opaque_number_t* other, ifcopenshell_geom_opaque_number_t** out_result);
bool ifcopenshell_geom_conversion_result_shape_add(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_t* arg_0, ifcopenshell_geom_conversion_result_shape_t** out_result);
bool ifcopenshell_geom_conversion_result_shape_area(ifcopenshell_geom_conversion_result_shape_t* self, double* out_result);
bool ifcopenshell_geom_brep_representation_as_compound(ifcopenshell_geom_brep_representation_t* self, bool force_meters, ifcopenshell_geom_conversion_result_shape_t** out_result);
bool ifcopenshell_geom_svgfill_polygon_boundary_point(ifcopenshell_geom_svgfill_polygon_t* self, size_t index, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_svgfill_polygon_boundary_size(ifcopenshell_geom_svgfill_polygon_t* self, size_t* out_result);
bool ifcopenshell_geom_conversion_result_shape_box(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_t** out_result);
bool ifcopenshell_geom_brep_element_calc_surface_area(ifcopenshell_geom_brep_element_t* self, double* out_result);
bool ifcopenshell_geom_brep_element_calc_volume(ifcopenshell_geom_brep_element_t* self, double* out_result);
bool ifcopenshell_geom_opaque_number_clone(ifcopenshell_geom_opaque_number_t* self, ifcopenshell_geom_opaque_number_t** out_result);
bool ifcopenshell_geom_triangulation_colors_buffer(ifcopenshell_geom_triangulation_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_triangulation_colors_buffer_size(ifcopenshell_geom_triangulation_t* self, size_t* out_result);
bool ifcopenshell_geom_conversion_result_shape_concat(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_t* arg_0, ifcopenshell_geom_conversion_result_shape_t** out_result);
bool ifcopenshell_geom_taxonomy_bspline_surface_control_point_at(ifcopenshell_geom_taxonomy_bspline_surface_t* self, size_t row, size_t col, ifcopenshell_geom_taxonomy_point3_t** out_result);
bool ifcopenshell_geom_taxonomy_bspline_surface_control_point_col_count_at(ifcopenshell_geom_taxonomy_bspline_surface_t* self, size_t row, size_t* out_result);
bool ifcopenshell_geom_taxonomy_bspline_surface_control_point_row_count(ifcopenshell_geom_taxonomy_bspline_surface_t* self, size_t* out_result);
bool ifcopenshell_geom_conversion_result_shape_convex_tag(ifcopenshell_geom_conversion_result_shape_t* self, bool value);
bool ifcopenshell_geom_opaque_number_divide(ifcopenshell_geom_opaque_number_t* self, ifcopenshell_geom_opaque_number_t* other, ifcopenshell_geom_opaque_number_t** out_result);
bool ifcopenshell_geom_conversion_result_shape_edges(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_list_t* out_result);
bool ifcopenshell_geom_triangulation_edges_buffer(ifcopenshell_geom_triangulation_t* self, const int32_t** out_result);
bool ifcopenshell_geom_triangulation_edges_item_ids_buffer(ifcopenshell_geom_triangulation_t* self, const int32_t** out_result);
bool ifcopenshell_geom_opaque_number_equals(ifcopenshell_geom_opaque_number_t* self, ifcopenshell_geom_opaque_number_t* other, bool* out_result);
bool ifcopenshell_geom_function_item_evaluator_evaluate_at(ifcopenshell_geom_function_item_evaluator_t* self, double u, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_triangulation_faces_buffer(ifcopenshell_geom_triangulation_t* self, const int32_t** out_result);
bool ifcopenshell_geom_conversion_result_shape_facets(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_list_t* out_result);
bool ifcopenshell_geom_iterator_get_as_brep_element(ifcopenshell_geom_iterator_t* self, ifcopenshell_geom_brep_element_t** out_result);
bool ifcopenshell_geom_iterator_get_as_serialized_element(ifcopenshell_geom_iterator_t* self, ifcopenshell_geom_serialized_element_t** out_result);
bool ifcopenshell_geom_iterator_get_as_triangulation_element(ifcopenshell_geom_iterator_t* self, ifcopenshell_geom_triangulation_element_t** out_result);
bool ifcopenshell_geom_conversion_result_shape_halfspaces(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_t** out_result);
bool ifcopenshell_geom_taxonomy_bspline_surface_has_weights(ifcopenshell_geom_taxonomy_bspline_surface_t* self, bool* out_result);
bool ifcopenshell_geom_svgfill_polygon_inner_boundary_count(ifcopenshell_geom_svgfill_polygon_t* self, size_t* out_result);
bool ifcopenshell_geom_svgfill_polygon_inner_boundary_point(ifcopenshell_geom_svgfill_polygon_t* self, size_t boundary_index, size_t point_index, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_svgfill_polygon_inner_boundary_size(ifcopenshell_geom_svgfill_polygon_t* self, size_t boundary_index, size_t* out_result);
bool ifcopenshell_geom_tree_ray_intersection_instance(ifcopenshell_geom_tree_ray_intersection_t* self, ifcopenshell_instance_t** out_result);
bool ifcopenshell_geom_taxonomy_style_instance_id(ifcopenshell_geom_taxonomy_style_t* self, size_t* out_result);
bool ifcopenshell_geom_conversion_result_shape_intersect(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_t* arg_0, ifcopenshell_geom_conversion_result_shape_t** out_result);
bool ifcopenshell_geom_triangulation_item_ids_buffer(ifcopenshell_geom_triangulation_t* self, const int32_t** out_result);
bool ifcopenshell_geom_conversion_result_shape_length(ifcopenshell_geom_conversion_result_shape_t* self, double* out_result);
bool ifcopenshell_geom_opaque_number_less_than(ifcopenshell_geom_opaque_number_t* self, ifcopenshell_geom_opaque_number_t* other, bool* out_result);
bool ifcopenshell_geom_triangulation_material_ids_buffer(ifcopenshell_geom_triangulation_t* self, const int32_t** out_result);
bool ifcopenshell_geom_conversion_result_shape_moved(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_taxonomy_matrix4_t* arg_0, ifcopenshell_geom_conversion_result_shape_t** out_result);
bool ifcopenshell_geom_opaque_number_multiply(ifcopenshell_geom_opaque_number_t* self, ifcopenshell_geom_opaque_number_t* other, ifcopenshell_geom_opaque_number_t** out_result);
bool ifcopenshell_geom_opaque_number_negate(ifcopenshell_geom_opaque_number_t* self, ifcopenshell_geom_opaque_number_t** out_result);
bool ifcopenshell_geom_iterator_next(ifcopenshell_geom_iterator_t* self, bool* out_result);
bool ifcopenshell_geom_triangulation_normals_buffer(ifcopenshell_geom_triangulation_t* self, const double** out_result);
bool ifcopenshell_geom_svgfill_polygon_point_inside(ifcopenshell_geom_svgfill_polygon_t* self, ifcopenshell_double_list_t* out_result);
bool ifcopenshell_geom_tree_select_box_bounds(ifcopenshell_geom_tree_t* self, double xmin, double ymin, double zmin, double xmax, double ymax, double zmax, bool completely_within, ifcopenshell_parse_instance_list_t** out_result);
bool ifcopenshell_geom_tree_select_box_element(ifcopenshell_geom_tree_t* self, ifcopenshell_instance_t* instance, bool completely_within, double extend, ifcopenshell_parse_instance_list_t** out_result);
bool ifcopenshell_geom_tree_select_box_point(ifcopenshell_geom_tree_t* self, double x, double y, double z, double extend, ifcopenshell_parse_instance_list_t** out_result);
bool ifcopenshell_geom_tree_select_brep_element(ifcopenshell_geom_tree_t* self, ifcopenshell_geom_brep_element_t* element, bool completely_within, double extend, ifcopenshell_parse_instance_list_t** out_result);
bool ifcopenshell_geom_tree_select_element(ifcopenshell_geom_tree_t* self, ifcopenshell_instance_t* instance, bool completely_within, double extend, ifcopenshell_parse_instance_list_t** out_result);
bool ifcopenshell_geom_tree_select_point(ifcopenshell_geom_tree_t* self, double x, double y, double z, double extend, ifcopenshell_parse_instance_list_t** out_result);
bool ifcopenshell_geom_tree_select_ray(ifcopenshell_geom_tree_t* self, double origin_x, double origin_y, double origin_z, double dir_x, double dir_y, double dir_z, double length, ifcopenshell_geom_tree_ray_intersection_list_t** out_result);
bool ifcopenshell_geom_conversion_result_shape_serialize(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_conversion_result_shape_serialize_obj(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_string_t* out_result);
bool ifcopenshell_geom_conversion_result_shape_solid(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_t** out_result);
bool ifcopenshell_geom_conversion_result_shape_solid_mt(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_t** out_result);
bool ifcopenshell_geom_opaque_number_subtract(ifcopenshell_geom_opaque_number_t* self, ifcopenshell_geom_opaque_number_t* other, ifcopenshell_geom_opaque_number_t** out_result);
bool ifcopenshell_geom_conversion_result_shape_subtract(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_t* arg_0, ifcopenshell_geom_conversion_result_shape_t** out_result);
bool ifcopenshell_geom_element_transformation_buffer(ifcopenshell_geom_element_t* self, const double** out_result);
bool ifcopenshell_geom_element_transformation_buffer_size(ifcopenshell_geom_element_t* self, size_t* out_result);
bool ifcopenshell_geom_triangulation_uvs_buffer(ifcopenshell_geom_triangulation_t* self, const double** out_result);
bool ifcopenshell_geom_conversion_result_shape_vertices(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_list_t* out_result);
bool ifcopenshell_geom_triangulation_verts_buffer(ifcopenshell_geom_triangulation_t* self, const double** out_result);
bool ifcopenshell_geom_conversion_result_shape_volume(ifcopenshell_geom_conversion_result_shape_t* self, double* out_result);
bool ifcopenshell_geom_taxonomy_bspline_surface_weight_at(ifcopenshell_geom_taxonomy_bspline_surface_t* self, size_t row, size_t col, double* out_result);
bool ifcopenshell_geom_taxonomy_bspline_surface_weight_col_count_at(ifcopenshell_geom_taxonomy_bspline_surface_t* self, size_t row, size_t* out_result);
bool ifcopenshell_geom_taxonomy_bspline_surface_weight_row_count(ifcopenshell_geom_taxonomy_bspline_surface_t* self, size_t* out_result);
bool ifcopenshell_geom_conversion_result_shape_wrap_in_compound(ifcopenshell_geom_conversion_result_shape_t* self, ifcopenshell_geom_conversion_result_shape_t** out_result);

#ifdef __cplusplus
}
#endif

#endif
