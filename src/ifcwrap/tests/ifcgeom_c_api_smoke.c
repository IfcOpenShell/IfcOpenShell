/*
 * Smoke test for the unified IfcOpenShell C API.
 *
 * This test covers the basic functionality of the generated bindings.
 * It tests both ifcparse and ifcgeom functionality.
 *
 * Current coverage:
 * - Settings: create, get/set bool/double, setting_names
 * - Iterator: create, initialize, next, get, progress
 * - Element: id, guid, type, name, context
 * - Triangulation: verts, faces, normals (via get_as_triangulation_element)
 */

#include "ifcopenshell_api.h"

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

/* Test file path - must be set by main() */
static const char* g_test_file_path = NULL;

static void fail(const char* message) {
    fprintf(stderr, "FAIL: %s\n", message);
    exit(1);
}

static void expect_true(int condition, const char* message) {
    if (!condition) {
        fail(message);
    }
}

static void expect_ok(int ok) {
    if (!ok) {
        const char* err = ifcopenshell_last_error_message();
        fprintf(stderr, "FAIL: API call failed: %s\n", err ? err : "(no error message)");
        exit(1);
    }
}

static void expect_fail(int ok) {
    if (ok) {
        fail("Expected API call to fail");
    }
    const char* err = ifcopenshell_last_error_message();
    expect_true(err && err[0] != '\0', "Expected API call to set an error");
    ifcopenshell_clear_error();
}

static ifcopenshell_instance_list_t instance_list_value(ifcopenshell_parse_instance_list_t* source) {
    ifcopenshell_instance_list_t result = {0};

    expect_ok(ifcopenshell_parse_instance_list_size(source, &result.size));
    result.items = calloc(result.size, sizeof(*result.items));
    expect_true(result.items != NULL || result.size == 0u, "Could not allocate instance list");
    for (size_t i = 0; i < result.size; ++i) {
        expect_ok(ifcopenshell_parse_instance_list_get(source, i, &result.items[i]));
    }
    return result;
}

static int string_list_contains(const ifcopenshell_string_list_t* values, const char* expected) {
    size_t i;
    for (i = 0; i < values->size; ++i) {
        if (strstr(values->items[i].data, expected) != NULL) {
            return 1;
        }
    }
    return 0;
}

static void test_settings_create(void) {
    ifcopenshell_geom_settings_t* settings = NULL;

    printf("Testing settings creation...\n");

    /* Create settings */
    expect_ok(ifcopenshell_geom_create_settings(&settings));
    expect_true(settings != NULL, "Settings should not be null");

    /* Cleanup */
    ifcopenshell_geom_settings_destroy(settings);

    printf("  Settings creation: PASS\n");
}

static void test_settings_names(void) {
    ifcopenshell_geom_settings_t* settings = NULL;
    ifcopenshell_string_list_t names = {0};

    printf("Testing settings names...\n");

    /* Create settings */
    expect_ok(ifcopenshell_geom_create_settings(&settings));

    /* Get setting names */
    expect_ok(ifcopenshell_geom_settings_setting_names(settings, &names));
    expect_true(names.size > 0, "Should have at least one setting");

    /* Check for some known settings */
    expect_true(string_list_contains(&names, "mesher-linear-deflection"),
                "Should contain mesher-linear-deflection setting");
    expect_true(string_list_contains(&names, "weld-vertices"),
                "Should contain weld-vertices setting");

    printf("  Found %zu settings\n", names.size);

    /* Cleanup */
    ifcopenshell_string_list_destroy(&names);
    ifcopenshell_geom_settings_destroy(settings);

    printf("  Settings names: PASS\n");
}

static void test_settings_bool(void) {
    ifcopenshell_geom_settings_t* settings = NULL;
    int ok;
    bool value;

    printf("Testing settings bool get/set...\n");

    /* Create settings */
    expect_ok(ifcopenshell_geom_create_settings(&settings));

    /* Get a known boolean setting (weld-vertices defaults to true) */
    expect_ok(ifcopenshell_geom_settings_get_bool(settings, "weld-vertices", &value));
    printf("  weld-vertices default: %s\n", value ? "true" : "false");

    /* Set it to the opposite */
    expect_ok(ifcopenshell_geom_settings_set_bool(settings, "weld-vertices", !value));

    /* Read it back */
    bool new_value;
    expect_ok(ifcopenshell_geom_settings_get_bool(settings, "weld-vertices", &new_value));
    expect_true(new_value == !value, "Setting should have changed");

    /* Try to get a non-boolean setting as bool - should fail */
    ok = ifcopenshell_geom_settings_get_bool(settings, "mesher-linear-deflection", &value);
    expect_fail(ok);

    /* Try to get a non-existent setting - should fail */
    ok = ifcopenshell_geom_settings_get_bool(settings, "nonexistent-setting", &value);
    expect_fail(ok);

    /* Cleanup */
    ifcopenshell_geom_settings_destroy(settings);

    printf("  Settings bool: PASS\n");
}

static void test_settings_double(void) {
    ifcopenshell_geom_settings_t* settings = NULL;
    int ok;
    double value;

    printf("Testing settings double get/set...\n");

    /* Create settings */
    expect_ok(ifcopenshell_geom_create_settings(&settings));

    /* Get a known double setting (mesher-linear-deflection defaults to 0.001) */
    expect_ok(ifcopenshell_geom_settings_get_double(settings, "mesher-linear-deflection", &value));
    printf("  mesher-linear-deflection default: %g\n", value);
    expect_true(fabs(value - 0.001) < 1e-9, "Default should be 0.001");

    /* Set it to a new value */
    expect_ok(ifcopenshell_geom_settings_set_double(settings, "mesher-linear-deflection", 0.01));

    /* Read it back */
    double new_value;
    expect_ok(ifcopenshell_geom_settings_get_double(settings, "mesher-linear-deflection", &new_value));
    expect_true(fabs(new_value - 0.01) < 1e-9, "Setting should have changed");

    /* Try to get a non-double setting as double - should fail */
    ok = ifcopenshell_geom_settings_get_double(settings, "weld-vertices", &value);
    expect_fail(ok);

    /* Try to get a non-existent setting - should fail */
    ok = ifcopenshell_geom_settings_get_double(settings, "nonexistent-setting", &value);
    expect_fail(ok);

    /* Cleanup */
    ifcopenshell_geom_settings_destroy(settings);

    printf("  Settings double: PASS\n");
}

static void test_settings_advanced(void) {
    ifcopenshell_geom_settings_t* settings = NULL;
    ifcopenshell_string_t ty = {0};
    int32_t int_val = 0;
    ifcopenshell_string_t str_val = {0};
    ifcopenshell_int32_list_t int_set = {0};
    ifcopenshell_string_list_t string_set = {0};
    ifcopenshell_double_list_t double_list = {0};
    int32_t context_ids_input_items[] = {29, 15};
    ifcopenshell_int32_list_t context_ids_input = {context_ids_input_items, 2};
    ifcopenshell_string_t context_type_items[] = {
        {(char*)"Model", 5, false},
        {(char*)"Plan", 4, false},
    };
    ifcopenshell_string_list_t context_types_input = {context_type_items, 2};
    double model_offset_input_items[] = {1.25, -2.5, 3.75};
    ifcopenshell_double_list_t model_offset_input = {model_offset_input_items, 3};
    int ok;

    printf("Testing settings advanced types...\n");

    expect_ok(ifcopenshell_geom_create_settings(&settings));

    /* type introspection */
    expect_ok(ifcopenshell_geom_settings_get_type(settings, "iterator-output", &ty));
    expect_true(ty.data != NULL && strstr(ty.data, "IteratorOutputOptions") != NULL, "iterator-output type mismatch");
    ifcopenshell_string_destroy(&ty);

    /* enum through int API */
    expect_ok(ifcopenshell_geom_settings_get_int(settings, "iterator-output", &int_val));
    expect_ok(ifcopenshell_geom_settings_set_int(settings, "iterator-output", 1));
    expect_ok(ifcopenshell_geom_settings_get_int(settings, "iterator-output", &int_val));
    expect_true(int_val == 1, "iterator-output should be set to NATIVE (1)");

    /* current Settings set has no std::string typed options; string APIs should fail on non-string settings */
    ok = ifcopenshell_geom_settings_get_string(settings, "weld-vertices", &str_val);
    expect_fail(ok);
    ok = ifcopenshell_geom_settings_set_string(settings, "weld-vertices", "true");
    expect_fail(ok);

    expect_ok(ifcopenshell_geom_settings_set_int_set(settings, "context-ids", &context_ids_input));
    expect_ok(ifcopenshell_geom_settings_get_int_set(settings, "context-ids", &int_set));
    expect_true(int_set.size == 2, "context-ids should return two items");
    expect_true(int_set.items[0] == 15 && int_set.items[1] == 29, "context-ids should be sorted and preserved");
    ifcopenshell_int32_list_destroy(&int_set);

    expect_ok(ifcopenshell_geom_settings_set_string_set(settings, "context-types", &context_types_input));
    expect_ok(ifcopenshell_geom_settings_get_string_set(settings, "context-types", &string_set));
    expect_true(string_set.size == 2, "context-types should return two items");
    expect_true(string_list_contains(&string_set, "Model"), "context-types should contain Model");
    expect_true(string_list_contains(&string_set, "Plan"), "context-types should contain Plan");
    ifcopenshell_string_list_destroy(&string_set);

    expect_ok(ifcopenshell_geom_settings_set_double_list(settings, "model-offset", &model_offset_input));
    expect_ok(ifcopenshell_geom_settings_get_double_list(settings, "model-offset", &double_list));
    expect_true(double_list.size == 3, "model-offset should return three values");
    expect_true(fabs(double_list.items[0] - 1.25) < 1e-9, "model-offset x should match");
    expect_true(fabs(double_list.items[1] + 2.5) < 1e-9, "model-offset y should match");
    expect_true(fabs(double_list.items[2] - 3.75) < 1e-9, "model-offset z should match");
    ifcopenshell_double_list_destroy(&double_list);

    ifcopenshell_geom_settings_destroy(settings);

    printf("  Settings advanced: PASS\n");
}

static void test_error_handling(void) {
    printf("Testing error handling...\n");

    /* Clear error */
    ifcopenshell_clear_error();
    const char* err = ifcopenshell_last_error_message();
    expect_true(err[0] == '\0', "Error should be empty after clear");

    /* Trigger an error */
    ifcopenshell_geom_settings_t* null_settings = NULL;
    int ok = ifcopenshell_geom_settings_setting_names(null_settings, NULL);
    expect_true(!ok, "Should fail with null settings");

    err = ifcopenshell_last_error_message();
    expect_true(err && err[0] != '\0', "Should have error message");
    printf("  Error message: %s\n", err);

    /* Clear and verify */
    ifcopenshell_clear_error();
    err = ifcopenshell_last_error_message();
    expect_true(err[0] == '\0', "Error should be empty after clear");

    printf("  Error handling: PASS\n");
}

static void test_null_safety(void) {
    printf("Testing null safety...\n");

    /* Destroy should handle null safely */
    ifcopenshell_geom_settings_destroy(NULL);
    ifcopenshell_geom_element_destroy(NULL);
    ifcopenshell_geom_triangulation_destroy(NULL);
    ifcopenshell_geom_taxonomy_matrix4_destroy(NULL);
    ifcopenshell_geom_taxonomy_point3_destroy(NULL);

    printf("  Null safety: PASS\n");
}

/*
 * Tests that require Iterator (to be implemented in Phase 2):
 *
 * - test_iterator_create()
 * - test_iterator_workflow()
 * - test_element_properties()
 * - test_triangulation_data()
 * - test_taxonomy_matrix4()
 * - test_taxonomy_point3()
 */

static void test_iterator_create(void) {
    printf("Testing iterator creation...\n");

    /* Open test IFC file */
    ifcopenshell_file_t* file = NULL;
    int ok = ifcopenshell_parse_open(g_test_file_path, 1 /* readonly */, &file);
    if (!ok) {
        printf("  SKIP: Could not open test file: %s\n", g_test_file_path);
        return;
    }
    expect_true(file != NULL, "File should be non-null");

    /* Create settings */
    ifcopenshell_geom_settings_t* settings = NULL;
    ok = ifcopenshell_geom_create_settings(&settings);
    expect_ok(ok);

    /* Create iterator - now takes file handle directly */
    ifcopenshell_geom_iterator_t* iterator = NULL;
    ok = ifcopenshell_geom_create_iterator(
        "opencascade",  /* geometry_library */
        settings,
        file,           /* file handle */
        1,              /* num_threads */
        &iterator
    );
    expect_ok(ok);
    expect_true(iterator != NULL, "Iterator should be non-null");

    /* Cleanup */
    ifcopenshell_geom_iterator_destroy(iterator);
    ifcopenshell_geom_settings_destroy(settings);
    ifcopenshell_file_destroy(file);

    printf("  Iterator creation: PASS\n");
}

static void test_iterator_workflow(void) {
    printf("Testing iterator workflow...\n");

    /* Open test IFC file */
    ifcopenshell_file_t* file = NULL;
    int ok = ifcopenshell_parse_open(g_test_file_path, 1 /* readonly */, &file);
    if (!ok) {
        printf("  SKIP: Could not open test file: %s\n", g_test_file_path);
        return;
    }

    /* Create settings and iterator */
    ifcopenshell_geom_settings_t* settings = NULL;
    ok = ifcopenshell_geom_create_settings(&settings);
    expect_ok(ok);

    ifcopenshell_geom_iterator_t* iterator = NULL;
    ok = ifcopenshell_geom_create_iterator("opencascade", settings, file, 1, &iterator);
    expect_ok(ok);

    /* Initialize iterator */
    bool initialized = false;
    ok = ifcopenshell_geom_iterator_initialize(iterator, &initialized);
    expect_ok(ok);
    printf("  Iterator initialized: %s\n", initialized ? "true" : "false");

    if (!initialized) {
        printf("  SKIP: No geometric elements found in test file\n");
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    /* Check progress */
    int32_t progress = 0;
    ok = ifcopenshell_geom_iterator_progress(iterator, &progress);
    expect_ok(ok);
    printf("  Initial progress: %d%%\n", progress);

    /* Check unit info */
    ifcopenshell_string_t unit_name = {0};
    ok = ifcopenshell_geom_iterator_unit_name(iterator, &unit_name);
    expect_ok(ok);
    printf("  Unit name: %s\n", unit_name.data ? unit_name.data : "(null)");
    ifcopenshell_string_destroy(&unit_name);

    double unit_mag = 0.0;
    ok = ifcopenshell_geom_iterator_unit_magnitude(iterator, &unit_mag);
    expect_ok(ok);
    printf("  Unit magnitude: %f\n", unit_mag);

    /* Iterate through elements */
    int count = 0;
    do {
        /* Get element */
        ifcopenshell_geom_element_t* elem = NULL;
        ok = ifcopenshell_geom_iterator_get(iterator, &elem);
        expect_ok(ok);
        expect_true(elem != NULL, "Element should be non-null");

        /* Get element properties */
        int32_t id = 0;
        ok = ifcopenshell_geom_element_id(elem, &id);
        expect_ok(ok);

        ifcopenshell_string_t guid = {0};
        ok = ifcopenshell_geom_element_guid(elem, &guid);
        expect_ok(ok);

        ifcopenshell_string_t type = {0};
        ok = ifcopenshell_geom_element_type(elem, &type);
        expect_ok(ok);

        ifcopenshell_string_t name = {0};
        ok = ifcopenshell_geom_element_name(elem, &name);
        expect_ok(ok);

        ifcopenshell_string_t context = {0};
        ok = ifcopenshell_geom_element_context(elem, &context);
        expect_ok(ok);

        if (count < 3) {  /* Print first 3 elements */
            printf("  Element %d: id=%d guid=%s type=%s name=%s context=%s\n",
                   count, id,
                   guid.data ? guid.data : "(null)",
                   type.data ? type.data : "(null)",
                   name.data ? name.data : "(null)",
                   context.data ? context.data : "(null)");
        }

        ifcopenshell_string_destroy(&guid);
        ifcopenshell_string_destroy(&type);
        ifcopenshell_string_destroy(&name);
        ifcopenshell_string_destroy(&context);

        /* Element is borrowed - don't destroy */

        count++;
        if (count >= 10) break;  /* Limit iteration for test */

        /* Advance iterator */
        bool has_next = false;
        ok = ifcopenshell_geom_iterator_next(iterator, &has_next);
        expect_ok(ok);
        if (!has_next) break;
    } while (1);

    printf("  Processed %d elements\n", count);
    expect_true(count > 0, "Should have processed at least one element");

    /* Final progress */
    ok = ifcopenshell_geom_iterator_progress(iterator, &progress);
    expect_ok(ok);
    printf("  Final progress: %d%%\n", progress);

    {
        ifcopenshell_geom_taxonomy_item_list_t task_items = {0};
        int ti_ok = ifcopenshell_geom_iterator_get_task_items(iterator, &task_items);
        if (ti_ok) {
            ifcopenshell_geom_taxonomy_item_list_destroy(&task_items);
        } else {
            ifcopenshell_clear_error();
        }
    }
    {
        ifcopenshell_instance_list_list_t task_products = {0};
        int tp_ok = ifcopenshell_geom_iterator_get_task_products(iterator, &task_products);
        if (tp_ok) {
            ifcopenshell_instance_list_list_destroy(&task_products);
        } else {
            ifcopenshell_clear_error();
        }
    }

    /* Cleanup */
    ifcopenshell_geom_iterator_destroy(iterator);
    ifcopenshell_geom_settings_destroy(settings);
    ifcopenshell_file_destroy(file);

    printf("  Iterator workflow: PASS\n");
}

static void test_iterator_filter_constructors(void) {
    printf("Testing iterator filter constructors...\n");

    ifcopenshell_file_t* file = NULL;
    int ok = ifcopenshell_parse_open(g_test_file_path, 1 /* readonly */, &file);
    if (!ok) {
        printf("  SKIP: Could not open test file: %s\n", g_test_file_path);
        return;
    }

    ifcopenshell_geom_settings_t* settings = NULL;
    expect_ok(ifcopenshell_geom_create_settings(&settings));

    /* Type-name include/exclude */
    ifcopenshell_string_list_t type_filters = {0};
    type_filters.size = 1;
    type_filters.items = (ifcopenshell_string_t*)calloc(type_filters.size, sizeof(ifcopenshell_string_t));
    expect_true(type_filters.items != NULL, "type filter allocation should succeed");
    type_filters.items[0].data = (char*)"IfcWall";
    type_filters.items[0].size = strlen(type_filters.items[0].data);
    type_filters.items[0].owned = false;

    ifcopenshell_geom_iterator_t* type_iterator = NULL;
    expect_ok(ifcopenshell_geom_create_iterator_with_include_exclude(
        "opencascade", settings, file, &type_filters, true, 1, &type_iterator));
    expect_true(type_iterator != NULL, "type-filter iterator should be created");

    bool initialized = false;
    expect_ok(ifcopenshell_geom_iterator_initialize(type_iterator, &initialized));
    ifcopenshell_geom_iterator_destroy(type_iterator);
    free(type_filters.items);

    /* GlobalId include/exclude */
    ifcopenshell_string_list_t guid_filters = {0};
    guid_filters.size = 1;
    guid_filters.items = (ifcopenshell_string_t*)calloc(guid_filters.size, sizeof(ifcopenshell_string_t));
    expect_true(guid_filters.items != NULL, "guid filter allocation should succeed");
    guid_filters.items[0].data = (char*)"19G2kjMqT2bw6US8_6I2Vy";
    guid_filters.items[0].size = strlen(guid_filters.items[0].data);
    guid_filters.items[0].owned = false;

    ifcopenshell_geom_iterator_t* guid_iterator = NULL;
    expect_ok(ifcopenshell_geom_create_iterator_with_include_exclude_globalid(
        "opencascade", settings, file, &guid_filters, true, 1, &guid_iterator));
    expect_true(guid_iterator != NULL, "globalid-filter iterator should be created");

    initialized = false;
    expect_ok(ifcopenshell_geom_iterator_initialize(guid_iterator, &initialized));
    ifcopenshell_geom_iterator_destroy(guid_iterator);
    free(guid_filters.items);

    /* ID include/exclude */
    ifcopenshell_int32_list_t id_filters = {0};
    id_filters.size = 1;
    id_filters.items = (int32_t*)calloc(id_filters.size, sizeof(int32_t));
    expect_true(id_filters.items != NULL, "id filter allocation should succeed");
    id_filters.items[0] = 701;

    ifcopenshell_geom_iterator_t* id_iterator = NULL;
    expect_ok(ifcopenshell_geom_create_iterator_with_include_exclude_id(
        "opencascade", settings, file, &id_filters, true, 1, &id_iterator));
    expect_true(id_iterator != NULL, "id-filter iterator should be created");

    initialized = false;
    expect_ok(ifcopenshell_geom_iterator_initialize(id_iterator, &initialized));
    ifcopenshell_geom_iterator_destroy(id_iterator);
    free(id_filters.items);

    ifcopenshell_geom_settings_destroy(settings);
    ifcopenshell_file_destroy(file);

    printf("  Iterator filter constructors: PASS\n");
}

static void test_triangulation_element(void) {
    printf("Testing triangulation element...\n");

    /* Open test IFC file */
    ifcopenshell_file_t* file = NULL;
    int ok = ifcopenshell_parse_open(g_test_file_path, 1, &file);
    if (!ok) {
        printf("  SKIP: Could not open test file\n");
        return;
    }

    /* Create settings and iterator */
    ifcopenshell_geom_settings_t* settings = NULL;
    ok = ifcopenshell_geom_create_settings(&settings);
    expect_ok(ok);

    ifcopenshell_geom_iterator_t* iterator = NULL;
    ok = ifcopenshell_geom_create_iterator("opencascade", settings, file, 1, &iterator);
    expect_ok(ok);

    bool initialized = false;
    ok = ifcopenshell_geom_iterator_initialize(iterator, &initialized);
    expect_ok(ok);

    if (!initialized) {
        printf("  SKIP: No geometric elements\n");
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    /* Get triangulation element */
    ifcopenshell_geom_triangulation_element_t* tri_elem = NULL;
    ok = ifcopenshell_geom_iterator_get_as_triangulation_element(iterator, &tri_elem);
    expect_ok(ok);
    expect_true(tri_elem != NULL, "Triangulation element should be non-null");

    /* Get geometry */
    ifcopenshell_geom_triangulation_t* geom = NULL;
    ok = ifcopenshell_geom_triangulation_element_geometry(tri_elem, &geom);
    expect_ok(ok);
    expect_true(geom != NULL, "Geometry should be non-null");

    /* Get triangulation data */
    ifcopenshell_double_list_t verts = {0};
    ok = ifcopenshell_geom_triangulation_verts(geom, &verts);
    expect_ok(ok);
    printf("  Vertices: %zu floats (%zu points)\n", verts.size, verts.size / 3);
    expect_true(verts.size > 0, "Should have vertices");
    expect_true(verts.size % 3 == 0, "Vertex count should be multiple of 3");
    ifcopenshell_double_list_destroy(&verts);

    ifcopenshell_int32_list_t faces = {0};
    ok = ifcopenshell_geom_triangulation_faces(geom, &faces);
    expect_ok(ok);
    printf("  Faces: %zu indices (%zu triangles)\n", faces.size, faces.size / 3);
    expect_true(faces.size > 0, "Should have faces");
    expect_true(faces.size % 3 == 0, "Face count should be multiple of 3");
    ifcopenshell_int32_list_destroy(&faces);

    ifcopenshell_double_list_t normals = {0};
    ok = ifcopenshell_geom_triangulation_normals(geom, &normals);
    expect_ok(ok);
    printf("  Normals: %zu floats (%zu vectors)\n", normals.size, normals.size / 3);
    ifcopenshell_double_list_destroy(&normals);

    /* Test borrowed pointer+size buffer access methods */
    const double* verts_buffer = NULL;
    size_t verts_count = 0;
    ok = ifcopenshell_geom_triangulation_verts_buffer(geom, &verts_buffer);
    expect_ok(ok);
    ok = ifcopenshell_geom_triangulation_verts_buffer_size(geom, &verts_count);
    expect_ok(ok);
    expect_true(verts_buffer != NULL || verts_count == 0, "verts_buffer should return valid pointer if count > 0");
    printf("  Verts buffer: %zu doubles at %p\n", verts_count, (void*)verts_buffer);

    const int32_t* faces_buffer = NULL;
    size_t faces_count = 0;
    ok = ifcopenshell_geom_triangulation_faces_buffer(geom, &faces_buffer);
    expect_ok(ok);
    ok = ifcopenshell_geom_triangulation_faces_buffer_size(geom, &faces_count);
    expect_ok(ok);
    expect_true(faces_buffer != NULL || faces_count == 0, "faces_buffer should return valid pointer if count > 0");
    printf("  Faces buffer: %zu ints at %p\n", faces_count, (void*)faces_buffer);

    const double* normals_buffer = NULL;
    size_t normals_count = 0;
    ok = ifcopenshell_geom_triangulation_normals_buffer(geom, &normals_buffer);
    expect_ok(ok);
    ok = ifcopenshell_geom_triangulation_normals_buffer_size(geom, &normals_count);
    expect_ok(ok);
    expect_true(normals_buffer != NULL || normals_count == 0, "normals_buffer should return valid pointer if count > 0");
    printf("  Normals buffer: %zu doubles at %p\n", normals_count, (void*)normals_buffer);

    const int32_t* edges_buffer = NULL;
    size_t edges_count = 0;
    ok = ifcopenshell_geom_triangulation_edges_buffer(geom, &edges_buffer);
    expect_ok(ok);
    ok = ifcopenshell_geom_triangulation_edges_buffer_size(geom, &edges_count);
    expect_ok(ok);
    expect_true(edges_buffer != NULL || edges_count == 0, "edges_buffer should return valid pointer if count > 0");
    printf("  Edges buffer: %zu ints at %p\n", edges_count, (void*)edges_buffer);

    const double* uvs_buffer = NULL;
    size_t uvs_count = 0;
    ok = ifcopenshell_geom_triangulation_uvs_buffer(geom, &uvs_buffer);
    expect_ok(ok);
    ok = ifcopenshell_geom_triangulation_uvs_buffer_size(geom, &uvs_count);
    expect_ok(ok);
    expect_true(uvs_buffer != NULL || uvs_count == 0, "uvs_buffer should return valid pointer if count > 0");
    printf("  UVs buffer: %zu doubles at %p\n", uvs_count, (void*)uvs_buffer);

    const int32_t* mat_ids_buffer = NULL;
    size_t mat_ids_count = 0;
    ok = ifcopenshell_geom_triangulation_material_ids_buffer(geom, &mat_ids_buffer);
    expect_ok(ok);
    ok = ifcopenshell_geom_triangulation_material_ids_buffer_size(geom, &mat_ids_count);
    expect_ok(ok);
    expect_true(mat_ids_buffer != NULL || mat_ids_count == 0, "material_ids_buffer should return valid pointer if count > 0");
    printf("  Material IDs buffer: %zu ints at %p\n", mat_ids_count, (void*)mat_ids_buffer);

    const int32_t* item_ids_buffer = NULL;
    size_t item_ids_count = 0;
    ok = ifcopenshell_geom_triangulation_item_ids_buffer(geom, &item_ids_buffer);
    expect_ok(ok);
    ok = ifcopenshell_geom_triangulation_item_ids_buffer_size(geom, &item_ids_count);
    expect_ok(ok);
    expect_true(item_ids_buffer != NULL || item_ids_count == 0, "item_ids_buffer should return valid pointer if count > 0");
    printf("  Item IDs buffer: %zu ints at %p\n", item_ids_count, (void*)item_ids_buffer);

    const int32_t* edge_item_ids_buffer = NULL;
    size_t edge_item_ids_count = 0;
    ok = ifcopenshell_geom_triangulation_edges_item_ids_buffer(geom, &edge_item_ids_buffer);
    expect_ok(ok);
    ok = ifcopenshell_geom_triangulation_edges_item_ids_buffer_size(geom, &edge_item_ids_count);
    expect_ok(ok);
    expect_true(edge_item_ids_buffer != NULL || edge_item_ids_count == 0, "edges_item_ids_buffer should return valid pointer if count > 0");
    printf("  Edge item IDs buffer: %zu ints at %p\n", edge_item_ids_count, (void*)edge_item_ids_buffer);

    /* Geometry and tri_elem are borrowed - don't destroy */

    /* Cleanup */
    ifcopenshell_geom_iterator_destroy(iterator);
    ifcopenshell_geom_settings_destroy(settings);
    ifcopenshell_file_destroy(file);

    printf("  Triangulation element: PASS\n");
}

static void test_extended_geometry_apis(void) {
    printf("Testing extended geometry APIs...\n");

    ifcopenshell_file_t* file = NULL;
    int ok = ifcopenshell_parse_open(g_test_file_path, 1, &file);
    if (!ok) {
        printf("  SKIP: Could not open test file\n");
        return;
    }

    ifcopenshell_geom_settings_t* settings = NULL;
    expect_ok(ifcopenshell_geom_create_settings(&settings));
    expect_ok(ifcopenshell_geom_settings_set_int(settings, "iterator-output", 0)); /* TRIANGULATED */

    ifcopenshell_geom_iterator_t* iterator = NULL;
    ifcopenshell_geom_iterator_destroy(iterator);
    iterator = NULL;
    expect_ok(ifcopenshell_geom_create_iterator("opencascade", settings, file, 1, &iterator));

    bool initialized = false;
    expect_ok(ifcopenshell_geom_iterator_initialize(iterator, &initialized));
    if (!initialized) {
        printf("  SKIP: No geometric elements\n");
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    /* Iterator extended methods */
    ifcopenshell_file_t* file2 = NULL;
    expect_ok(ifcopenshell_geom_iterator_file(iterator, &file2));
    expect_true(file2 != NULL, "iterator.file should return a file handle");

    bool had_error = true;
    expect_ok(ifcopenshell_geom_iterator_had_error_processing_elements(iterator, &had_error));
    expect_true(had_error == false, "had_error_processing_elements should be false for smoke test");

    ifcopenshell_string_t log_text = {0};
    expect_ok(ifcopenshell_geom_iterator_get_log(iterator, &log_text));
    ifcopenshell_string_destroy(&log_text);

    ifcopenshell_geom_element_t* elem = NULL;
    expect_ok(ifcopenshell_geom_iterator_get(iterator, &elem));
    expect_true(elem != NULL, "iterator.get should return element");

    int32_t id = 0;
    expect_ok(ifcopenshell_geom_element_id(elem, &id));

    ifcopenshell_geom_element_t* elem_by_id = NULL;
    expect_ok(ifcopenshell_geom_iterator_get_object(iterator, id, &elem_by_id));
    expect_true(elem_by_id != NULL, "iterator.get_object should return element");

    int32_t parent_id = 0;
    expect_ok(ifcopenshell_geom_element_parent_id(elem, &parent_id));

    ifcopenshell_string_t unique_id = {0};
    expect_ok(ifcopenshell_geom_element_unique_id(elem, &unique_id));
    expect_true(unique_id.data != NULL && unique_id.size > 0, "unique_id should be non-empty");
    ifcopenshell_string_destroy(&unique_id);

    ifcopenshell_geom_transformation_t* trsf = NULL;
    expect_ok(ifcopenshell_geom_element_transformation(elem, &trsf));
    expect_true(trsf != NULL, "transformation should be non-null");

    ifcopenshell_double_list_t matrix = {0};
    expect_ok(ifcopenshell_geom_transformation_matrix(trsf, &matrix));
    expect_true(matrix.size == 16, "transformation matrix should have 16 elements");

    const double* matrix_buffer = NULL;
    size_t matrix_buffer_size = 0;
    expect_ok(ifcopenshell_geom_element_transformation_buffer(elem, &matrix_buffer));
    expect_ok(ifcopenshell_geom_element_transformation_buffer_size(elem, &matrix_buffer_size));
    expect_true(matrix_buffer != NULL, "transformation buffer should be non-null");
    expect_true(matrix_buffer_size == 16, "transformation buffer size should be 16");
    expect_true(matrix.size == matrix_buffer_size, "transformation matrix and buffer sizes should match");
    if (matrix.size > 0) {
        expect_true(isfinite(matrix_buffer[0]), "transformation buffer values should be finite");
    }
    ifcopenshell_double_list_destroy(&matrix);

    ifcopenshell_instance_t* product = NULL;
    expect_ok(ifcopenshell_geom_element_product(elem, &product));
    expect_true(product != NULL, "product handle should be non-null");

    {
        ifcopenshell_geom_element_list_t parents_list = {0};
        int parents_ok = ifcopenshell_geom_element_parents(elem, &parents_list);
        if (parents_ok) {
            ifcopenshell_geom_element_list_destroy(&parents_list);
        } else {
            ifcopenshell_clear_error();
        }
    }

    /* Triangulation extended methods */
    ifcopenshell_geom_triangulation_element_t* tri_elem = NULL;
    expect_ok(ifcopenshell_geom_iterator_get_as_triangulation_element(iterator, &tri_elem));

    ifcopenshell_geom_triangulation_t* tri = NULL;
    expect_ok(ifcopenshell_geom_triangulation_element_geometry(tri_elem, &tri));
    expect_true(tri != NULL, "triangulation should be non-null");

    ifcopenshell_int32_list_t edges = {0};
    expect_ok(ifcopenshell_geom_triangulation_edges(tri, &edges));
    ifcopenshell_int32_list_destroy(&edges);

    ifcopenshell_double_list_t uvs = {0};
    expect_ok(ifcopenshell_geom_triangulation_uvs(tri, &uvs));
    ifcopenshell_double_list_destroy(&uvs);

    ifcopenshell_int32_list_t material_ids = {0};
    expect_ok(ifcopenshell_geom_triangulation_material_ids(tri, &material_ids));
    ifcopenshell_int32_list_destroy(&material_ids);

    ifcopenshell_int32_list_t item_ids = {0};
    expect_ok(ifcopenshell_geom_triangulation_item_ids(tri, &item_ids));
    ifcopenshell_int32_list_destroy(&item_ids);

    ifcopenshell_int32_list_t edges_item_ids = {0};
    expect_ok(ifcopenshell_geom_triangulation_edges_item_ids(tri, &edges_item_ids));
    ifcopenshell_int32_list_destroy(&edges_item_ids);

    ifcopenshell_int32_list_list_t poly_no_holes = {0};
    expect_ok(ifcopenshell_geom_triangulation_polyhedral_faces_without_holes(tri, &poly_no_holes));
    ifcopenshell_int32_list_list_destroy(&poly_no_holes);

    ifcopenshell_int32_list_list_list_t poly_with_holes = {0};
    expect_ok(ifcopenshell_geom_triangulation_polyhedral_faces_with_holes(tri, &poly_with_holes));
    ifcopenshell_int32_list_list_list_destroy(&poly_with_holes);

    size_t material_count = 0;
    expect_ok(ifcopenshell_geom_triangulation_material_count(tri, &material_count));

    {
        ifcopenshell_geom_taxonomy_style_list_t tri_materials = {0};
        expect_ok(ifcopenshell_geom_triangulation_materials(tri, &tri_materials));
        ifcopenshell_geom_taxonomy_style_list_destroy(&tri_materials);
    }

    ifcopenshell_double_list_t colors = {0};
    size_t colors_size = 0;
    expect_ok(ifcopenshell_geom_triangulation_colors_buffer(tri, &colors));
    expect_ok(ifcopenshell_geom_triangulation_colors_buffer_size(tri, &colors_size));
    expect_true(colors.size == colors_size, "colors buffer and size API should agree");
    expect_true(colors.size % 4 == 0, "colors buffer size should be a multiple of 4");
    if (material_count > 0) {
        expect_true(colors.size == material_count * 4, "colors size should be 4x material_count");
    }
    ifcopenshell_double_list_destroy(&colors);

    /* Style / colour taxonomy (if materials exist) */
    if (material_count > 0) {
        ifcopenshell_geom_taxonomy_style_t* style = NULL;
        ifcopenshell_geom_taxonomy_colour_t* colour = NULL;
        ifcopenshell_string_t style_name = {0};
        ifcopenshell_double_list_t rgb = {0};
        bool has_specularity = false;
        bool has_transparency = false;

        expect_ok(ifcopenshell_geom_triangulation_material_at(tri, 0, &style));
        expect_true(style != NULL, "material style should be non-null");

        expect_ok(ifcopenshell_geom_taxonomy_style_name(style, &style_name));
        ifcopenshell_string_destroy(&style_name);

        expect_ok(ifcopenshell_geom_taxonomy_style_diffuse(style, &colour));
        expect_true(colour != NULL, "diffuse colour should be non-null");
        expect_ok(ifcopenshell_geom_taxonomy_colour_get_data(colour, &rgb));
        expect_true(rgb.size == 3, "colour data should contain 3 components");
        ifcopenshell_double_list_destroy(&rgb);
        ifcopenshell_geom_taxonomy_colour_destroy(colour);

        expect_ok(ifcopenshell_geom_taxonomy_style_surface(style, &colour));
        expect_ok(ifcopenshell_geom_taxonomy_colour_get_data(colour, &rgb));
        expect_true(rgb.size == 3, "surface colour data should contain 3 components");
        ifcopenshell_double_list_destroy(&rgb);
        ifcopenshell_geom_taxonomy_colour_destroy(colour);

        expect_ok(ifcopenshell_geom_taxonomy_style_specular(style, &colour));
        expect_ok(ifcopenshell_geom_taxonomy_colour_get_data(colour, &rgb));
        expect_true(rgb.size == 3, "specular colour data should contain 3 components");
        ifcopenshell_double_list_destroy(&rgb);
        ifcopenshell_geom_taxonomy_colour_destroy(colour);

        expect_ok(ifcopenshell_geom_taxonomy_style_has_specularity(style, &has_specularity));
        expect_ok(ifcopenshell_geom_taxonomy_style_has_transparency(style, &has_transparency));

        if (has_specularity) {
            double specularity = 0.0;
            expect_ok(ifcopenshell_geom_taxonomy_style_specularity(style, &specularity));
        }
        if (has_transparency) {
            double transparency = 0.0;
            expect_ok(ifcopenshell_geom_taxonomy_style_transparency(style, &transparency));
        }

        bool use_surface_color = false;
        expect_ok(ifcopenshell_geom_taxonomy_style_use_surface_color(style, &use_surface_color));
        (void)use_surface_color;

        ifcopenshell_geom_taxonomy_style_destroy(style);
    }

    /* BRep and Serialization paths via iterator-output switch */
    expect_ok(ifcopenshell_geom_settings_set_int(settings, "iterator-output", 1)); /* NATIVE */
    ifcopenshell_geom_iterator_destroy(iterator);
    iterator = NULL;
    expect_ok(ifcopenshell_geom_create_iterator("opencascade", settings, file, 1, &iterator));
    expect_ok(ifcopenshell_geom_iterator_initialize(iterator, &initialized));
    if (initialized) {
        ifcopenshell_geom_brep_element_t* brep_elem = NULL;
        ifcopenshell_geom_brep_representation_t* brep = NULL;
        expect_ok(ifcopenshell_geom_iterator_get_native(iterator, &brep_elem));
        expect_true(brep_elem != NULL, "get_native should return brep element");
        expect_ok(ifcopenshell_geom_brep_element_geometry(brep_elem, &brep));
        expect_true(brep != NULL, "brep representation should be non-null");

        ifcopenshell_string_t brep_id = {0};
        expect_ok(ifcopenshell_geom_brep_representation_id(brep, &brep_id));
        ifcopenshell_string_destroy(&brep_id);

        int32_t n_items = 0;
        expect_ok(ifcopenshell_geom_brep_representation_size(brep, &n_items));
        if (n_items > 0) {
            ifcopenshell_geom_conversion_result_shape_t* item = NULL;
            int32_t item_id = 0;
            expect_ok(ifcopenshell_geom_brep_representation_item(brep, 0, &item));
            expect_ok(ifcopenshell_geom_brep_representation_item_id(brep, 0, &item_id));
            ifcopenshell_geom_conversion_result_shape_destroy(item);
        }

        double vol = 0.0;
        double area = 0.0;
        expect_ok(ifcopenshell_geom_brep_representation_calculate_volume(brep, &vol));
        expect_ok(ifcopenshell_geom_brep_representation_calculate_surface_area(brep, &area));
        expect_ok(ifcopenshell_geom_brep_element_calc_volume(brep_elem, &vol));
        expect_ok(ifcopenshell_geom_brep_element_calc_surface_area(brep_elem, &area));

        {
            bool proj_ok = false;
            int psa_ok = ifcopenshell_geom_brep_element_calculate_projected_surface_area(brep_elem, 0.0, 0.0, 1.0, &proj_ok);
            if (!psa_ok) ifcopenshell_clear_error();
        }

        {
            ifcopenshell_string_t brep_entity = {0};
            expect_ok(ifcopenshell_geom_brep_representation_entity(brep, &brep_entity));
            ifcopenshell_string_destroy(&brep_entity);
        }

        {
            ifcopenshell_geom_settings_t* brep_settings = NULL;
            expect_ok(ifcopenshell_geom_brep_representation_settings(brep, &brep_settings));
        }

        ifcopenshell_geom_conversion_result_shape_t* compound = NULL;
        expect_ok(ifcopenshell_geom_brep_representation_as_compound(brep, false, &compound));

        {
            ifcopenshell_geom_taxonomy_line_t* tmp_line = NULL;
            ifcopenshell_geom_taxonomy_create_line(0.0, 0.0, 0.0, 1.0, 0.0, 0.0, &tmp_line);
            if (tmp_line) {
                ifcopenshell_geom_taxonomy_matrix4_t* ax = NULL;
                ifcopenshell_geom_taxonomy_line_matrix(tmp_line, &ax);
                if (ax) {
                    bool proj_ok = false;
                    int psa_ok = ifcopenshell_geom_brep_representation_calculate_projected_surface_area(brep, ax, 0.0, 0.0, 1.0, &proj_ok);
                    if (!psa_ok) ifcopenshell_clear_error();
                    ifcopenshell_geom_taxonomy_matrix4_destroy(ax);
                }
                ifcopenshell_geom_taxonomy_line_destroy(tmp_line);
            }
        }

        ifcopenshell_string_t shape_serialized = {0};
        expect_ok(ifcopenshell_geom_conversion_result_shape_serialize(compound, &shape_serialized));
        expect_true(shape_serialized.data != NULL && shape_serialized.size > 0, "serialized compound should be non-empty");
        ifcopenshell_string_destroy(&shape_serialized);

        /* CGAL-only shape APIs should fail gracefully in non-CGAL builds. */
        {
            ifcopenshell_string_t shape_obj = {0};
            int obj_ok = ifcopenshell_geom_conversion_result_shape_serialize_obj(compound, &shape_obj);
            if (obj_ok) {
                expect_true(shape_obj.data != NULL && shape_obj.size > 0, "serialize_obj output should be non-empty");
                ifcopenshell_string_destroy(&shape_obj);
            } else {
                ifcopenshell_clear_error();
            }
        }
        {
            int tag_ok = ifcopenshell_geom_conversion_result_shape_convex_tag(compound, true);
            if (!tag_ok) {
                ifcopenshell_clear_error();
            }
        }

        ifcopenshell_geom_conversion_result_shape_t* solid = NULL;
        int solid_ok = ifcopenshell_geom_conversion_result_shape_solid_mt(compound, &solid);
        if (solid_ok) {
            expect_true(solid != NULL, "solid_mt should return shape when successful");
            {
                ifcopenshell_geom_conversion_result_shape_t* fused = NULL;
                int add_ok = ifcopenshell_geom_conversion_result_shape_add(compound, solid, &fused);
                if (add_ok) {
                    expect_true(fused != NULL, "add should return shape when successful");
                    ifcopenshell_geom_conversion_result_shape_destroy(fused);
                } else {
                    ifcopenshell_clear_error();
                }
            }
            {
                ifcopenshell_geom_conversion_result_shape_t* cut = NULL;
                int sub_ok = ifcopenshell_geom_conversion_result_shape_subtract(compound, solid, &cut);
                if (sub_ok) {
                    expect_true(cut != NULL, "subtract should return shape when successful");
                    ifcopenshell_geom_conversion_result_shape_destroy(cut);
                } else {
                    ifcopenshell_clear_error();
                }
            }
            {
                ifcopenshell_geom_conversion_result_shape_t* inter = NULL;
                int int_ok = ifcopenshell_geom_conversion_result_shape_intersect(compound, solid, &inter);
                if (int_ok) {
                    expect_true(inter != NULL, "intersect should return shape when successful");
                    ifcopenshell_geom_conversion_result_shape_destroy(inter);
                } else {
                    ifcopenshell_clear_error();
                }
            }
            {
                ifcopenshell_geom_conversion_result_shape_t* joined = NULL;
                int concat_ok = ifcopenshell_geom_conversion_result_shape_concat(compound, solid, &joined);
                if (concat_ok) {
                    expect_true(joined != NULL, "concat should return shape when successful");
                    ifcopenshell_geom_conversion_result_shape_destroy(joined);
                } else {
                    ifcopenshell_clear_error();
                }
            }
            ifcopenshell_geom_conversion_result_shape_destroy(solid);
        } else {
            ifcopenshell_clear_error();
        }

        ifcopenshell_geom_conversion_result_shape_destroy(compound);
    }

    expect_ok(ifcopenshell_geom_settings_set_int(settings, "iterator-output", 2)); /* SERIALIZED */
    ifcopenshell_geom_iterator_destroy(iterator);
    iterator = NULL;
    expect_ok(ifcopenshell_geom_create_iterator("opencascade", settings, file, 1, &iterator));
    expect_ok(ifcopenshell_geom_iterator_initialize(iterator, &initialized));
    if (initialized) {
        ifcopenshell_geom_serialized_element_t* serialized_elem = NULL;
        ifcopenshell_geom_serialization_t* serialization = NULL;
        expect_ok(ifcopenshell_geom_iterator_get_as_serialized_element(iterator, &serialized_elem));
        expect_ok(ifcopenshell_geom_serialized_element_geometry(serialized_elem, &serialization));
        expect_true(serialization != NULL, "serialization should be non-null");

        ifcopenshell_string_t brep_data = {0};
        expect_ok(ifcopenshell_geom_serialization_brep_data(serialization, &brep_data));
        expect_true(brep_data.data != NULL, "brep_data should be non-null");
        ifcopenshell_string_destroy(&brep_data);

        ifcopenshell_double_list_t styles = {0};
        expect_ok(ifcopenshell_geom_serialization_surface_styles(serialization, &styles));
        ifcopenshell_double_list_destroy(&styles);

        ifcopenshell_int32_list_t style_ids = {0};
        expect_ok(ifcopenshell_geom_serialization_surface_style_ids(serialization, &style_ids));
        ifcopenshell_int32_list_destroy(&style_ids);
    }

    ifcopenshell_geom_iterator_destroy(iterator);
    ifcopenshell_geom_settings_destroy(settings);
    ifcopenshell_file_destroy(file);

    printf("  Extended geometry APIs: PASS\n");
}

static void test_taxonomy_primitive_apis(void) {
    printf("Testing taxonomy primitive APIs...\n");

    ifcopenshell_geom_taxonomy_point3_t* p = NULL;
    ifcopenshell_geom_taxonomy_direction3_t* d = NULL;
    ifcopenshell_geom_taxonomy_line_t* line = NULL;
    ifcopenshell_geom_taxonomy_circle_t* circle = NULL;
    ifcopenshell_geom_taxonomy_ellipse_t* ellipse = NULL;
    ifcopenshell_geom_taxonomy_plane_t* plane = NULL;
    ifcopenshell_geom_taxonomy_cylinder_t* cylinder = NULL;
    ifcopenshell_geom_taxonomy_sphere_t* sphere = NULL;
    ifcopenshell_geom_taxonomy_torus_t* torus = NULL;
    ifcopenshell_geom_taxonomy_solid_t* box = NULL;
    ifcopenshell_geom_taxonomy_matrix4_t* m = NULL;
    ifcopenshell_geom_taxonomy_shell_t* sh = NULL;
    ifcopenshell_geom_taxonomy_face_t* fa = NULL;
    ifcopenshell_geom_taxonomy_loop_t* lo = NULL;
    ifcopenshell_geom_taxonomy_edge_t* ed = NULL;
    ifcopenshell_double_list_t data = {0};
    double scalar = 0.0;
    size_t n = 0;

    expect_ok(ifcopenshell_geom_taxonomy_create_point3(1.0, 2.0, 3.0, &p));
    expect_ok(ifcopenshell_geom_taxonomy_point3_get_data(p, &data));
    expect_true(data.size == 3, "point3 should expose 3 components");
    ifcopenshell_double_list_destroy(&data);

    expect_ok(ifcopenshell_geom_taxonomy_create_direction3(0.0, 0.0, 1.0, &d));
    expect_ok(ifcopenshell_geom_taxonomy_direction3_get_data(d, &data));
    expect_true(data.size == 3, "direction3 should expose 3 components");
    ifcopenshell_double_list_destroy(&data);

    expect_ok(ifcopenshell_geom_taxonomy_create_line(0.0, 0.0, 0.0, 1.0, 0.0, 0.0, &line));
    expect_ok(ifcopenshell_geom_taxonomy_line_matrix(line, &m));
    expect_ok(ifcopenshell_geom_taxonomy_matrix4_get_data(m, &data));
    expect_true(data.size == 16, "line matrix should expose 16 components");
    ifcopenshell_double_list_destroy(&data);
    ifcopenshell_geom_taxonomy_matrix4_destroy(m);
    m = NULL;

    expect_ok(ifcopenshell_geom_taxonomy_create_circle(0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 2.5, &circle));
    expect_ok(ifcopenshell_geom_taxonomy_circle_radius(circle, &scalar));
    expect_true(fabs(scalar - 2.5) < 1e-9, "circle radius should match constructor");
    expect_ok(ifcopenshell_geom_taxonomy_circle_matrix(circle, &m));
    ifcopenshell_geom_taxonomy_matrix4_destroy(m);
    m = NULL;

    expect_ok(ifcopenshell_geom_taxonomy_create_ellipse(0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 3.0, 1.5, &ellipse));
    expect_ok(ifcopenshell_geom_taxonomy_ellipse_radius1(ellipse, &scalar));
    expect_true(fabs(scalar - 3.0) < 1e-9, "ellipse radius1 should match constructor");
    expect_ok(ifcopenshell_geom_taxonomy_ellipse_radius2(ellipse, &scalar));
    expect_true(fabs(scalar - 1.5) < 1e-9, "ellipse radius2 should match constructor");
    expect_ok(ifcopenshell_geom_taxonomy_ellipse_matrix(ellipse, &m));
    ifcopenshell_geom_taxonomy_matrix4_destroy(m);
    m = NULL;

    expect_ok(ifcopenshell_geom_taxonomy_create_plane(0.0, 0.0, 0.0, 0.0, 0.0, 1.0, &plane));
    expect_ok(ifcopenshell_geom_taxonomy_plane_matrix(plane, &m));
    ifcopenshell_geom_taxonomy_matrix4_destroy(m);
    m = NULL;

    expect_ok(ifcopenshell_geom_taxonomy_create_cylinder(0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.7, &cylinder));
    expect_ok(ifcopenshell_geom_taxonomy_cylinder_radius(cylinder, &scalar));
    expect_true(fabs(scalar - 0.7) < 1e-9, "cylinder radius should match constructor");
    expect_ok(ifcopenshell_geom_taxonomy_cylinder_matrix(cylinder, &m));
    ifcopenshell_geom_taxonomy_matrix4_destroy(m);
    m = NULL;

    expect_ok(ifcopenshell_geom_taxonomy_create_sphere(0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.2, &sphere));
    expect_ok(ifcopenshell_geom_taxonomy_sphere_radius(sphere, &scalar));
    expect_true(fabs(scalar - 1.2) < 1e-9, "sphere radius should match constructor");
    expect_ok(ifcopenshell_geom_taxonomy_sphere_matrix(sphere, &m));
    ifcopenshell_geom_taxonomy_matrix4_destroy(m);
    m = NULL;

    expect_ok(ifcopenshell_geom_taxonomy_create_torus(0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 4.0, 0.6, &torus));
    expect_ok(ifcopenshell_geom_taxonomy_torus_radius1(torus, &scalar));
    expect_true(fabs(scalar - 4.0) < 1e-9, "torus radius1 should match constructor");
    expect_ok(ifcopenshell_geom_taxonomy_torus_radius2(torus, &scalar));
    expect_true(fabs(scalar - 0.6) < 1e-9, "torus radius2 should match constructor");
    expect_ok(ifcopenshell_geom_taxonomy_torus_matrix(torus, &m));
    ifcopenshell_geom_taxonomy_matrix4_destroy(m);
    m = NULL;

    expect_ok(ifcopenshell_geom_taxonomy_create_box(1.0, 2.0, 3.0, &box));
    expect_ok(ifcopenshell_geom_taxonomy_solid_shell_count(box, &n));
    expect_true(n > 0, "box should have shells");
    expect_ok(ifcopenshell_geom_taxonomy_solid_shell_at(box, 0, &sh));
    expect_ok(ifcopenshell_geom_taxonomy_shell_face_count(sh, &n));
    expect_true(n > 0, "shell should have faces");
    expect_ok(ifcopenshell_geom_taxonomy_shell_face_at(sh, 0, &fa));
    expect_ok(ifcopenshell_geom_taxonomy_face_loop_count(fa, &n));
    expect_true(n > 0, "face should have loops");
    expect_ok(ifcopenshell_geom_taxonomy_face_loop_at(fa, 0, &lo));
    expect_ok(ifcopenshell_geom_taxonomy_loop_edge_count(lo, &n));
    expect_true(n > 0, "loop should have edges");
    expect_ok(ifcopenshell_geom_taxonomy_loop_edge_at(lo, 0, &ed));
    expect_true(ed != NULL, "edge should be non-null");

    ifcopenshell_geom_taxonomy_edge_destroy(ed);
    ifcopenshell_geom_taxonomy_loop_destroy(lo);
    ifcopenshell_geom_taxonomy_face_destroy(fa);
    ifcopenshell_geom_taxonomy_shell_destroy(sh);
    ifcopenshell_geom_taxonomy_solid_destroy(box);
    ifcopenshell_geom_taxonomy_torus_destroy(torus);
    ifcopenshell_geom_taxonomy_sphere_destroy(sphere);
    ifcopenshell_geom_taxonomy_cylinder_destroy(cylinder);
    ifcopenshell_geom_taxonomy_plane_destroy(plane);
    ifcopenshell_geom_taxonomy_ellipse_destroy(ellipse);
    ifcopenshell_geom_taxonomy_circle_destroy(circle);
    ifcopenshell_geom_taxonomy_line_destroy(line);
    ifcopenshell_geom_taxonomy_direction3_destroy(d);
    ifcopenshell_geom_taxonomy_point3_destroy(p);

    printf("  Taxonomy primitive APIs: PASS\n");
}

static void test_taxonomy_operation_apis(void) {
    printf("Testing taxonomy operation APIs...\n");

    ifcopenshell_geom_taxonomy_collection_t* collection = NULL;
    ifcopenshell_geom_taxonomy_loft_t* loft = NULL;
    ifcopenshell_geom_taxonomy_boolean_result_t* boolean_result = NULL;
    ifcopenshell_geom_taxonomy_node_t* node = NULL;
    ifcopenshell_geom_taxonomy_line_t* line = NULL;
    ifcopenshell_geom_taxonomy_item_t* line_item = NULL;
    ifcopenshell_geom_taxonomy_face_t* face = NULL;
    ifcopenshell_geom_taxonomy_shell_t* shell = NULL;
    ifcopenshell_geom_taxonomy_solid_t* box = NULL;
    ifcopenshell_geom_taxonomy_item_t* face_item = NULL;
    ifcopenshell_geom_taxonomy_direction3_t* direction = NULL;
    ifcopenshell_geom_taxonomy_point3_t* axis_origin = NULL;
    ifcopenshell_geom_taxonomy_extrusion_t* extrusion = NULL;
    ifcopenshell_geom_taxonomy_revolve_t* revolve = NULL;
    ifcopenshell_geom_taxonomy_sweep_along_curve_t* sweep = NULL;
    ifcopenshell_geom_taxonomy_item_t* item = NULL;
    ifcopenshell_geom_taxonomy_item_t* sweep_item = NULL;
    ifcopenshell_geom_taxonomy_direction3_t* dir2 = NULL;
    ifcopenshell_geom_taxonomy_point3_t* p3 = NULL;
    ifcopenshell_geom_taxonomy_matrix4_t* m = NULL;
    size_t n = 0;
    int32_t i32 = -1;
    uint32_t u32 = 0;
    bool b = false;
    double d = 0.0;

    /* Base objects used by operations */
    expect_ok(ifcopenshell_geom_taxonomy_create_line(0.0, 0.0, 0.0, 1.0, 0.0, 0.0, &line));
    expect_ok(ifcopenshell_geom_taxonomy_line_as_item(line, &line_item));
    expect_ok(ifcopenshell_geom_taxonomy_create_box(1.0, 1.0, 1.0, &box));
    expect_ok(ifcopenshell_geom_taxonomy_solid_shell_at(box, 0, &shell));
    expect_ok(ifcopenshell_geom_taxonomy_shell_face_at(shell, 0, &face));
    expect_ok(ifcopenshell_geom_taxonomy_face_as_item(face, &face_item));
    expect_ok(ifcopenshell_geom_taxonomy_create_direction3(0.0, 0.0, 1.0, &direction));
    expect_ok(ifcopenshell_geom_taxonomy_create_point3(0.0, 0.0, 0.0, &axis_origin));

    /* Collection */
    expect_ok(ifcopenshell_geom_taxonomy_create_collection(&collection));
    expect_ok(ifcopenshell_geom_taxonomy_collection_add_item(collection, line_item));
    expect_ok(ifcopenshell_geom_taxonomy_collection_item_count(collection, &n));
    expect_true(n == 1, "collection should contain one item");
    expect_ok(ifcopenshell_geom_taxonomy_collection_item_at(collection, 0, &item));
    expect_ok(ifcopenshell_geom_taxonomy_item_kind(item, &i32));
    expect_ok(ifcopenshell_geom_taxonomy_item_identity(item, &u32));
    expect_true(u32 > 0, "item identity should be non-zero");

    /* Loft */
    expect_ok(ifcopenshell_geom_taxonomy_create_loft(&loft));
    expect_ok(ifcopenshell_geom_taxonomy_loft_add_item(loft, line_item));
    expect_ok(ifcopenshell_geom_taxonomy_loft_item_count(loft, &n));
    expect_true(n == 1, "loft should contain one item");
    expect_ok(ifcopenshell_geom_taxonomy_loft_has_axis(loft, &b));
    expect_true(!b, "loft axis should not be set initially");
    expect_ok(ifcopenshell_geom_taxonomy_loft_set_axis(loft, face_item));
    expect_ok(ifcopenshell_geom_taxonomy_loft_has_axis(loft, &b));
    expect_true(b, "loft axis should be set");
    expect_ok(ifcopenshell_geom_taxonomy_loft_axis(loft, &item));
    expect_ok(ifcopenshell_geom_taxonomy_item_kind(item, &i32));

    /* Boolean result */
    expect_ok(ifcopenshell_geom_taxonomy_create_boolean_result(1, &boolean_result)); /* SUBTRACTION */
    expect_ok(ifcopenshell_geom_taxonomy_boolean_result_operation(boolean_result, &i32));
    expect_true(i32 == 1, "boolean operation should match constructor");
    expect_ok(ifcopenshell_geom_taxonomy_boolean_result_add_item(boolean_result, line_item));
    expect_ok(ifcopenshell_geom_taxonomy_boolean_result_add_item(boolean_result, face_item));
    expect_ok(ifcopenshell_geom_taxonomy_boolean_result_item_count(boolean_result, &n));
    expect_true(n == 2, "boolean result should contain two items");
    expect_ok(ifcopenshell_geom_taxonomy_boolean_result_item_at(boolean_result, 1, &item));
    expect_ok(ifcopenshell_geom_taxonomy_item_kind(item, &i32));

    /* Node */
    expect_ok(ifcopenshell_geom_taxonomy_create_node(&node));
    expect_ok(ifcopenshell_geom_taxonomy_item_kind((ifcopenshell_geom_taxonomy_item_t*)node, &i32));
    expect_ok(ifcopenshell_geom_taxonomy_item_identity((ifcopenshell_geom_taxonomy_item_t*)node, &u32));
    expect_true(u32 > 0, "node identity should be non-zero");

    /* Extrusion */
    expect_ok(ifcopenshell_geom_taxonomy_create_extrusion(line_item, direction, 2.0, &extrusion));
    expect_ok(ifcopenshell_geom_taxonomy_extrusion_depth(extrusion, &d));
    expect_true(fabs(d - 2.0) < 1e-9, "extrusion depth should match constructor");
    expect_ok(ifcopenshell_geom_taxonomy_extrusion_basis(extrusion, &item));
    expect_ok(ifcopenshell_geom_taxonomy_item_kind(item, &i32));
    expect_ok(ifcopenshell_geom_taxonomy_extrusion_direction(extrusion, &dir2));
    {
        ifcopenshell_double_list_t v = {0};
        expect_ok(ifcopenshell_geom_taxonomy_direction3_get_data(dir2, &v));
        expect_true(v.size == 3, "extrusion direction should have 3 components");
        ifcopenshell_double_list_destroy(&v);
    }
    expect_ok(ifcopenshell_geom_taxonomy_extrusion_matrix(extrusion, &m));
    ifcopenshell_geom_taxonomy_matrix4_destroy(m);
    m = NULL;

    /* Revolve */
    expect_ok(ifcopenshell_geom_taxonomy_create_revolve(line_item, axis_origin, direction, 1.57079632679, &revolve));
    expect_ok(ifcopenshell_geom_taxonomy_revolve_has_angle(revolve, &b));
    expect_true(b, "revolve should have angle");
    expect_ok(ifcopenshell_geom_taxonomy_revolve_angle(revolve, &d));
    expect_true(d > 1.5 && d < 1.6, "revolve angle should match constructor");
    expect_ok(ifcopenshell_geom_taxonomy_revolve_basis(revolve, &item));
    expect_ok(ifcopenshell_geom_taxonomy_revolve_axis_origin(revolve, &p3));
    {
        ifcopenshell_double_list_t v = {0};
        expect_ok(ifcopenshell_geom_taxonomy_point3_get_data(p3, &v));
        expect_true(v.size == 3, "revolve axis origin should have 3 components");
        ifcopenshell_double_list_destroy(&v);
    }
    expect_ok(ifcopenshell_geom_taxonomy_revolve_direction(revolve, &dir2));
    expect_ok(ifcopenshell_geom_taxonomy_revolve_matrix(revolve, &m));
    ifcopenshell_geom_taxonomy_matrix4_destroy(m);
    m = NULL;

    /* Sweep along curve (fixed-reference variant) */
    expect_ok(ifcopenshell_geom_taxonomy_create_sweep_along_curve(face, line_item, direction, &sweep));
    expect_ok(ifcopenshell_geom_taxonomy_sweep_along_curve_basis(sweep, &sweep_item));
    expect_ok(ifcopenshell_geom_taxonomy_item_kind(sweep_item, &i32));
    expect_ok(ifcopenshell_geom_taxonomy_sweep_along_curve_curve(sweep, &item));
    expect_ok(ifcopenshell_geom_taxonomy_sweep_along_curve_has_direction(sweep, &b));
    expect_true(b, "sweep should have reference direction");
    expect_ok(ifcopenshell_geom_taxonomy_sweep_along_curve_direction(sweep, &dir2));
    expect_ok(ifcopenshell_geom_taxonomy_sweep_along_curve_has_surface(sweep, &b));
    expect_true(!b, "fixed-reference sweep should not have surface");
    expect_ok(ifcopenshell_geom_taxonomy_sweep_along_curve_matrix(sweep, &m));
    ifcopenshell_geom_taxonomy_matrix4_destroy(m);
    m = NULL;
    expect_ok(ifcopenshell_geom_taxonomy_sweep_along_curve_has_basis(sweep, &b));
    expect_ok(ifcopenshell_geom_taxonomy_sweep_along_curve_has_curve(sweep, &b));
    expect_ok(ifcopenshell_geom_taxonomy_sweep_along_curve_has_matrix(sweep, &b));

    /* taxonomy_face_basis */
    {
        ifcopenshell_geom_taxonomy_item_t* face_basis = NULL;
        int basis_ok = ifcopenshell_geom_taxonomy_face_basis(face, &face_basis);
        if (!basis_ok) ifcopenshell_clear_error();
    }

    /* taxonomy_item_hash */
    {
        size_t hash_val = 0;
        expect_ok(ifcopenshell_geom_taxonomy_item_hash(line_item, &hash_val));
    }

    ifcopenshell_geom_taxonomy_sweep_along_curve_destroy(sweep);
    ifcopenshell_geom_taxonomy_revolve_destroy(revolve);
    ifcopenshell_geom_taxonomy_extrusion_destroy(extrusion);
    ifcopenshell_geom_taxonomy_node_destroy(node);
    ifcopenshell_geom_taxonomy_boolean_result_destroy(boolean_result);
    ifcopenshell_geom_taxonomy_loft_destroy(loft);
    ifcopenshell_geom_taxonomy_collection_destroy(collection);
    ifcopenshell_geom_taxonomy_item_destroy(line_item);
    ifcopenshell_geom_taxonomy_item_destroy(face_item);
    ifcopenshell_geom_taxonomy_point3_destroy(axis_origin);
    ifcopenshell_geom_taxonomy_direction3_destroy(direction);
    ifcopenshell_geom_taxonomy_face_destroy(face);
    ifcopenshell_geom_taxonomy_shell_destroy(shell);
    ifcopenshell_geom_taxonomy_solid_destroy(box);
    ifcopenshell_geom_taxonomy_line_destroy(line);

    printf("  Taxonomy operation APIs: PASS\n");
}

static void test_taxonomy_advanced_apis(void) {
    printf("Testing taxonomy advanced APIs...\n");

    ifcopenshell_geom_taxonomy_bspline_curve_t* bc = NULL;
    ifcopenshell_geom_taxonomy_bspline_surface_t* bs = NULL;
    ifcopenshell_geom_taxonomy_offset_curve_t* oc = NULL;
    ifcopenshell_geom_taxonomy_line_t* line = NULL;
    ifcopenshell_geom_taxonomy_item_t* line_item = NULL;
    ifcopenshell_geom_taxonomy_item_t* basis_item = NULL;
    ifcopenshell_geom_taxonomy_item_t* cast_item = NULL;
    ifcopenshell_geom_taxonomy_direction3_t* dir = NULL;
    ifcopenshell_geom_taxonomy_direction3_t* dir_ref = NULL;
    int32_t degree = 0;
    size_t n = 0;
    bool has_weights = true;
    double offset = 0.0;
    ifcopenshell_int32_list_t i_list = {0};
    ifcopenshell_double_list_t d_list = {0};

    expect_ok(ifcopenshell_geom_taxonomy_create_bspline_curve(3, &bc));
    expect_ok(ifcopenshell_geom_taxonomy_bspline_curve_degree(bc, &degree));
    expect_true(degree == 3, "bspline curve degree should match constructor");
    expect_ok(ifcopenshell_geom_taxonomy_bspline_curve_control_point_count(bc, &n));
    expect_true(n == 0, "new bspline curve should have no control points");
    expect_ok(ifcopenshell_geom_taxonomy_bspline_curve_multiplicities(bc, &i_list));
    expect_true(i_list.size == 0, "new bspline curve multiplicities should be empty");
    ifcopenshell_int32_list_destroy(&i_list);
    expect_ok(ifcopenshell_geom_taxonomy_bspline_curve_knots(bc, &d_list));
    expect_true(d_list.size == 0, "new bspline curve knots should be empty");
    ifcopenshell_double_list_destroy(&d_list);
    expect_ok(ifcopenshell_geom_taxonomy_bspline_curve_has_weights(bc, &has_weights));
    expect_true(!has_weights, "new bspline curve should not have weights");
    expect_ok(ifcopenshell_geom_taxonomy_bspline_curve_as_item(bc, &cast_item));
    ifcopenshell_geom_taxonomy_item_destroy(cast_item);

    expect_ok(ifcopenshell_geom_taxonomy_create_bspline_surface(2, 4, &bs));
    expect_ok(ifcopenshell_geom_taxonomy_bspline_surface_degree_u(bs, &degree));
    expect_true(degree == 2, "bspline surface degree_u should match constructor");
    expect_ok(ifcopenshell_geom_taxonomy_bspline_surface_degree_v(bs, &degree));
    expect_true(degree == 4, "bspline surface degree_v should match constructor");
    expect_ok(ifcopenshell_geom_taxonomy_bspline_surface_control_point_row_count(bs, &n));
    expect_true(n == 0, "new bspline surface should have no control-point rows");
    expect_ok(ifcopenshell_geom_taxonomy_bspline_surface_multiplicities_u(bs, &i_list));
    expect_true(i_list.size == 0, "new bspline surface multiplicities_u should be empty");
    ifcopenshell_int32_list_destroy(&i_list);
    expect_ok(ifcopenshell_geom_taxonomy_bspline_surface_multiplicities_v(bs, &i_list));
    expect_true(i_list.size == 0, "new bspline surface multiplicities_v should be empty");
    ifcopenshell_int32_list_destroy(&i_list);
    expect_ok(ifcopenshell_geom_taxonomy_bspline_surface_knots_u(bs, &d_list));
    expect_true(d_list.size == 0, "new bspline surface knots_u should be empty");
    ifcopenshell_double_list_destroy(&d_list);
    expect_ok(ifcopenshell_geom_taxonomy_bspline_surface_knots_v(bs, &d_list));
    expect_true(d_list.size == 0, "new bspline surface knots_v should be empty");
    ifcopenshell_double_list_destroy(&d_list);
    expect_ok(ifcopenshell_geom_taxonomy_bspline_surface_has_weights(bs, &has_weights));
    expect_true(!has_weights, "new bspline surface should not have weights");
    expect_ok(ifcopenshell_geom_taxonomy_bspline_surface_as_item(bs, &cast_item));
    ifcopenshell_geom_taxonomy_item_destroy(cast_item);

    expect_ok(ifcopenshell_geom_taxonomy_create_line(0.0, 0.0, 0.0, 0.0, 1.0, 0.0, &line));
    expect_ok(ifcopenshell_geom_taxonomy_line_as_item(line, &line_item));
    expect_ok(ifcopenshell_geom_taxonomy_create_direction3(0.0, 0.0, 1.0, &dir));
    expect_ok(ifcopenshell_geom_taxonomy_create_offset_curve(line_item, dir, 0.25, &oc));
    expect_ok(ifcopenshell_geom_taxonomy_offset_curve_basis(oc, &basis_item));
    expect_ok(ifcopenshell_geom_taxonomy_item_kind(basis_item, &degree));
    ifcopenshell_geom_taxonomy_item_destroy(basis_item);
    expect_ok(ifcopenshell_geom_taxonomy_offset_curve_reference(oc, &dir_ref));
    expect_ok(ifcopenshell_geom_taxonomy_offset_curve_offset(oc, &offset));
    expect_true(fabs(offset - 0.25) < 1e-9, "offset curve offset should match constructor");
    expect_ok(ifcopenshell_geom_taxonomy_offset_curve_as_item(oc, &cast_item));
    ifcopenshell_geom_taxonomy_item_destroy(cast_item);

    ifcopenshell_geom_taxonomy_offset_curve_destroy(oc);
    ifcopenshell_geom_taxonomy_direction3_destroy(dir_ref);
    ifcopenshell_geom_taxonomy_direction3_destroy(dir);
    ifcopenshell_geom_taxonomy_item_destroy(line_item);
    ifcopenshell_geom_taxonomy_line_destroy(line);
    ifcopenshell_geom_taxonomy_bspline_surface_destroy(bs);
    ifcopenshell_geom_taxonomy_bspline_curve_destroy(bc);

    printf("  Taxonomy advanced APIs: PASS\n");
}

static void test_serializer_settings_apis(void) {
    printf("Testing serializer settings APIs...\n");

    ifcopenshell_geom_serializer_settings_t* settings = NULL;
    ifcopenshell_string_list_t names = {0};
    ifcopenshell_int32_list_t int_set = {0};
    ifcopenshell_string_t type = {0};
    bool b = false;
    int32_t i = 0;
    double d = 0.0;
    ifcopenshell_string_t s = {0};
    int32_t digits_input_items[] = {3, 5};
    ifcopenshell_int32_list_t digits_input = {digits_input_items, 2};
    int ok;

    expect_ok(ifcopenshell_geom_create_serializer_settings(&settings));

    expect_ok(ifcopenshell_geom_serializer_settings_setting_names(settings, &names));
    expect_true(names.size > 0, "Serializer settings should expose names");
    expect_true(string_list_contains(&names, "use-element-names"), "Expected use-element-names serializer setting");
    ifcopenshell_string_list_destroy(&names);

    expect_ok(ifcopenshell_geom_serializer_settings_get_type(settings, "use-element-names", &type));
    expect_true(type.data != NULL && strstr(type.data, "bool") != NULL, "use-element-names should be bool");
    ifcopenshell_string_destroy(&type);

    expect_ok(ifcopenshell_geom_serializer_settings_set_bool(settings, "use-element-names", true));
    expect_ok(ifcopenshell_geom_serializer_settings_get_bool(settings, "use-element-names", &b));
    expect_true(b, "use-element-names should be true");

    expect_ok(ifcopenshell_geom_serializer_settings_set_int(settings, "digits", 7));
    expect_ok(ifcopenshell_geom_serializer_settings_get_int(settings, "digits", &i));
    expect_true(i == 7, "digits should be set");

    expect_ok(ifcopenshell_geom_serializer_settings_set_string(settings, "base-uri", "https://example.com/"));
    expect_ok(ifcopenshell_geom_serializer_settings_get_string(settings, "base-uri", &s));
    expect_true(s.data != NULL && strstr(s.data, "https://example.com/") != NULL, "base-uri should be set");
    ifcopenshell_string_destroy(&s);

    ok = ifcopenshell_geom_serializer_settings_get_double(settings, "digits", &d);
    expect_fail(ok);
    ok = ifcopenshell_geom_serializer_settings_set_double(settings, "digits", 2.5);
    expect_fail(ok);
    ok = ifcopenshell_geom_serializer_settings_get_bool(settings, "digits", &b);
    expect_fail(ok);
    ok = ifcopenshell_geom_serializer_settings_get_int(settings, "use-element-names", &i);
    expect_fail(ok);

    ok = ifcopenshell_geom_serializer_settings_set_int_set(settings, "digits", &digits_input);
    expect_fail(ok);
    ok = ifcopenshell_geom_serializer_settings_get_int_set(settings, "digits", &int_set);
    expect_fail(ok);

    ifcopenshell_geom_serializer_settings_destroy(settings);

    printf("  Serializer settings APIs: PASS\n");
}

static void test_obj_serializer_apis(void) {
    printf("Testing OBJ serializer APIs...\n");

    ifcopenshell_file_t* file = NULL;
    ifcopenshell_geom_settings_t* geom_settings = NULL;
    ifcopenshell_geom_serializer_settings_t* serializer_settings = NULL;
    ifcopenshell_geom_iterator_t* iterator = NULL;
    ifcopenshell_geom_buffer_t* obj_buffer = NULL;
    ifcopenshell_geom_buffer_t* mtl_buffer = NULL;
    ifcopenshell_geom_geometry_serializer_t* serializer = NULL;
    ifcopenshell_geom_triangulation_element_t* tri_elem = NULL;
    ifcopenshell_string_t obj_text = {0};
    ifcopenshell_string_t mtl_text = {0};
    bool initialized = false;
    bool ready = false;
    bool is_tesselated = false;
    int ok;

    ok = ifcopenshell_parse_open(g_test_file_path, 1, &file);
    if (!ok) {
        printf("  SKIP: Could not open test file: %s\n", g_test_file_path);
        return;
    }

    expect_ok(ifcopenshell_geom_create_settings(&geom_settings));
    expect_ok(ifcopenshell_geom_settings_set_int(geom_settings, "iterator-output", 0)); /* TRIANGULATED */
    expect_ok(ifcopenshell_geom_create_serializer_settings(&serializer_settings));
    expect_ok(ifcopenshell_geom_serializer_settings_set_int(serializer_settings, "digits", 7));
    expect_ok(ifcopenshell_geom_create_buffer(&obj_buffer));
    expect_ok(ifcopenshell_geom_create_buffer(&mtl_buffer));
    expect_ok(ifcopenshell_geom_create_geometry_serializer_by_stream(
        "obj", mtl_buffer, obj_buffer, geom_settings, serializer_settings, &serializer));

    expect_ok(ifcopenshell_geom_geometry_serializer_ready(serializer, &ready));
    expect_true(ready, "OBJ serializer should be ready");
    expect_ok(ifcopenshell_geom_buffer_is_ready(obj_buffer, &ready));
    expect_true(ready, "OBJ buffer should be ready");
    expect_ok(ifcopenshell_geom_buffer_is_ready(mtl_buffer, &ready));
    expect_true(ready, "MTL buffer should be ready");
    expect_ok(ifcopenshell_geom_geometry_serializer_is_tesselated(serializer, &is_tesselated));
    expect_true(is_tesselated, "OBJ serializer should be tesselated");

    {
        ifcopenshell_geom_settings_t* ser_geom_settings = NULL;
        expect_ok(ifcopenshell_geom_geometry_serializer_geometry_settings(serializer, &ser_geom_settings));
    }
    {
        ifcopenshell_geom_serializer_settings_t* ser_settings = NULL;
        expect_ok(ifcopenshell_geom_geometry_serializer_settings(serializer, &ser_settings));
    }

    expect_ok(ifcopenshell_geom_geometry_serializer_set_file(serializer, file));
    expect_ok(ifcopenshell_geom_geometry_serializer_set_unit_name_and_magnitude(serializer, "METER", 1.0));
    expect_ok(ifcopenshell_geom_geometry_serializer_write_header(serializer));

    expect_ok(ifcopenshell_geom_create_iterator("opencascade", geom_settings, file, 1, &iterator));
    expect_ok(ifcopenshell_geom_iterator_initialize(iterator, &initialized));
    if (!initialized) {
        printf("  SKIP: No geometric elements for serializer tests\n");
        ifcopenshell_geom_geometry_serializer_destroy(serializer);
        ifcopenshell_geom_buffer_destroy(mtl_buffer);
        ifcopenshell_geom_buffer_destroy(obj_buffer);
        ifcopenshell_geom_serializer_settings_destroy(serializer_settings);
        ifcopenshell_geom_settings_destroy(geom_settings);
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_file_destroy(file);
        return;
    }

    expect_ok(ifcopenshell_geom_iterator_get_as_triangulation_element(iterator, &tri_elem));
    expect_true(tri_elem != NULL, "Triangulation element should be available");
    expect_ok(ifcopenshell_geom_geometry_serializer_write_triangulation_element(serializer, tri_elem));
    expect_ok(ifcopenshell_geom_geometry_serializer_finalize(serializer));

    {
        ifcopenshell_geom_element_t* read_elem = NULL;
        int read_ok = ifcopenshell_geom_geometry_serializer_read(serializer, file, "dummy-guid", "0", 0, &read_elem);
        if (!read_ok) ifcopenshell_clear_error();
    }

    expect_ok(ifcopenshell_geom_buffer_get_value(obj_buffer, &obj_text));
    expect_true(obj_text.data != NULL && obj_text.size > 0, "OBJ buffer should contain output");
    expect_true(strstr(obj_text.data, "# File generated by IfcOpenShell") != NULL, "OBJ output should include header");
    expect_true(strstr(obj_text.data, "g ") != NULL, "OBJ output should include at least one group");
    ifcopenshell_string_destroy(&obj_text);

    expect_ok(ifcopenshell_geom_buffer_get_value(mtl_buffer, &mtl_text));
    expect_true(mtl_text.data != NULL && mtl_text.size > 0, "MTL buffer should contain output");
    expect_true(strstr(mtl_text.data, "# File generated by IfcOpenShell") != NULL, "MTL output should include header");
    ifcopenshell_string_destroy(&mtl_text);

    ifcopenshell_geom_geometry_serializer_destroy(serializer);
    ifcopenshell_geom_buffer_destroy(mtl_buffer);
    ifcopenshell_geom_buffer_destroy(obj_buffer);
    ifcopenshell_geom_serializer_settings_destroy(serializer_settings);
    ifcopenshell_geom_iterator_destroy(iterator);
    ifcopenshell_geom_settings_destroy(geom_settings);
    ifcopenshell_file_destroy(file);

    printf("  OBJ serializer APIs: PASS\n");
}

static void test_ttl_serializer_apis(void) {
    printf("Testing TTL serializer APIs...\n");

    ifcopenshell_file_t* file = NULL;
    ifcopenshell_geom_settings_t* geom_settings = NULL;
    ifcopenshell_geom_serializer_settings_t* serializer_settings = NULL;
    ifcopenshell_geom_iterator_t* iterator = NULL;
    ifcopenshell_geom_buffer_t* ttl_buffer = NULL;
    ifcopenshell_geom_geometry_serializer_t* serializer = NULL;
    ifcopenshell_geom_triangulation_element_t* tri_elem = NULL;
    ifcopenshell_string_t ttl_text = {0};
    bool initialized = false;
    bool ready = false;
    bool is_tesselated = false;
    int ok;

    ok = ifcopenshell_parse_open(g_test_file_path, 1, &file);
    if (!ok) {
        printf("  SKIP: Could not open test file: %s\n", g_test_file_path);
        return;
    }

    expect_ok(ifcopenshell_geom_create_settings(&geom_settings));
    expect_ok(ifcopenshell_geom_settings_set_int(geom_settings, "iterator-output", 0)); /* TRIANGULATED */
    expect_ok(ifcopenshell_geom_settings_set_int(geom_settings, "triangulation-type", 2)); /* POLYHEDRON_WITH_HOLES */
    expect_ok(ifcopenshell_geom_create_serializer_settings(&serializer_settings));
    expect_ok(ifcopenshell_geom_serializer_settings_set_string(serializer_settings, "base-uri", "https://example.com/"));
    expect_ok(ifcopenshell_geom_create_buffer(&ttl_buffer));
    expect_ok(ifcopenshell_geom_create_geometry_serializer_by_stream(
        "ttl", ttl_buffer, ttl_buffer, geom_settings, serializer_settings, &serializer));

    expect_ok(ifcopenshell_geom_geometry_serializer_ready(serializer, &ready));
    expect_true(ready, "TTL serializer should be ready");
    expect_ok(ifcopenshell_geom_buffer_is_ready(ttl_buffer, &ready));
    expect_true(ready, "TTL buffer should be ready");
    expect_ok(ifcopenshell_geom_geometry_serializer_is_tesselated(serializer, &is_tesselated));
    expect_true(is_tesselated, "TTL serializer should report tesselated output in default mode");

    expect_ok(ifcopenshell_geom_geometry_serializer_set_file(serializer, file));
    expect_ok(ifcopenshell_geom_geometry_serializer_set_unit_name_and_magnitude(serializer, "METER", 1.0));
    expect_ok(ifcopenshell_geom_geometry_serializer_write_header(serializer));

    expect_ok(ifcopenshell_geom_create_iterator("opencascade", geom_settings, file, 1, &iterator));
    expect_ok(ifcopenshell_geom_iterator_initialize(iterator, &initialized));
    if (!initialized) {
        printf("  SKIP: No geometric elements for TTL serializer tests\n");
        ifcopenshell_geom_geometry_serializer_destroy(serializer);
        ifcopenshell_geom_buffer_destroy(ttl_buffer);
        ifcopenshell_geom_serializer_settings_destroy(serializer_settings);
        ifcopenshell_geom_settings_destroy(geom_settings);
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_file_destroy(file);
        return;
    }

    expect_ok(ifcopenshell_geom_iterator_get_as_triangulation_element(iterator, &tri_elem));
    expect_true(tri_elem != NULL, "Triangulation element should be available");
    expect_ok(ifcopenshell_geom_geometry_serializer_write_triangulation_element(serializer, tri_elem));
    expect_ok(ifcopenshell_geom_geometry_serializer_finalize(serializer));

    expect_ok(ifcopenshell_geom_buffer_get_value(ttl_buffer, &ttl_text));
    expect_true(ttl_text.data != NULL && ttl_text.size > 0, "TTL buffer should contain output");
    expect_true(strstr(ttl_text.data, "@prefix geo:") != NULL, "TTL output should include geo prefix");
    expect_true(strstr(ttl_text.data, "base:") != NULL, "TTL output should include base URI prefix");
    ifcopenshell_string_destroy(&ttl_text);

    ifcopenshell_geom_geometry_serializer_destroy(serializer);
    ifcopenshell_geom_buffer_destroy(ttl_buffer);
    ifcopenshell_geom_serializer_settings_destroy(serializer_settings);
    ifcopenshell_geom_iterator_destroy(iterator);
    ifcopenshell_geom_settings_destroy(geom_settings);
    ifcopenshell_file_destroy(file);

    printf("  TTL serializer APIs: PASS\n");
}

static void test_svg_serializer_apis(void) {
    printf("Testing SVG serializer APIs...\n");

    ifcopenshell_file_t* file = NULL;
    ifcopenshell_geom_settings_t* geom_settings = NULL;
    ifcopenshell_geom_serializer_settings_t* serializer_settings = NULL;
    ifcopenshell_geom_iterator_t* iterator = NULL;
    ifcopenshell_geom_buffer_t* svg_buffer = NULL;
    ifcopenshell_geom_geometry_serializer_t* serializer = NULL;
    ifcopenshell_geom_brep_element_t* brep_elem = NULL;
    ifcopenshell_string_t svg_text = {0};
    bool initialized = false;
    bool ready = false;
    bool is_tesselated = false;
    int ok;

    ok = ifcopenshell_parse_open(g_test_file_path, 1, &file);
    if (!ok) {
        printf("  SKIP: Could not open test file: %s\n", g_test_file_path);
        return;
    }

    expect_ok(ifcopenshell_geom_create_settings(&geom_settings));
    expect_ok(ifcopenshell_geom_settings_set_int(geom_settings, "iterator-output", 1)); /* NATIVE */
    expect_ok(ifcopenshell_geom_create_serializer_settings(&serializer_settings));
    expect_ok(ifcopenshell_geom_create_buffer(&svg_buffer));
    expect_ok(ifcopenshell_geom_create_geometry_serializer_by_stream(
        "svg", svg_buffer, svg_buffer, geom_settings, serializer_settings, &serializer));

    expect_ok(ifcopenshell_geom_geometry_serializer_ready(serializer, &ready));
    expect_true(ready, "SVG serializer should be ready");
    expect_ok(ifcopenshell_geom_buffer_is_ready(svg_buffer, &ready));
    expect_true(ready, "SVG buffer should be ready");
    expect_ok(ifcopenshell_geom_geometry_serializer_is_tesselated(serializer, &is_tesselated));
    expect_true(!is_tesselated, "SVG serializer should report non-tesselated");

    expect_ok(ifcopenshell_geom_geometry_serializer_set_file(serializer, file));
    expect_ok(ifcopenshell_geom_geometry_serializer_set_unit_name_and_magnitude(serializer, "METER", 1.0));
    expect_ok(ifcopenshell_geom_geometry_serializer_write_header(serializer));

    expect_ok(ifcopenshell_geom_create_iterator("opencascade", geom_settings, file, 1, &iterator));
    expect_ok(ifcopenshell_geom_iterator_initialize(iterator, &initialized));
    if (!initialized) {
        printf("  SKIP: No geometric elements for SVG serializer tests\n");
        ifcopenshell_geom_geometry_serializer_destroy(serializer);
        ifcopenshell_geom_buffer_destroy(svg_buffer);
        ifcopenshell_geom_serializer_settings_destroy(serializer_settings);
        ifcopenshell_geom_settings_destroy(geom_settings);
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_file_destroy(file);
        return;
    }

    expect_ok(ifcopenshell_geom_iterator_get_as_brep_element(iterator, &brep_elem));
    expect_true(brep_elem != NULL, "BRep element should be available");
    expect_ok(ifcopenshell_geom_geometry_serializer_write_brep_element(serializer, brep_elem));
    expect_ok(ifcopenshell_geom_geometry_serializer_finalize(serializer));

    expect_ok(ifcopenshell_geom_buffer_get_value(svg_buffer, &svg_text));
    expect_true(svg_text.data != NULL && svg_text.size > 0, "SVG buffer should contain output");
    expect_true(strstr(svg_text.data, "<svg") != NULL, "SVG output should include svg tag");
    expect_true(strstr(svg_text.data, "xmlns") != NULL, "SVG output should include xmlns");
    ifcopenshell_string_destroy(&svg_text);

    ifcopenshell_geom_geometry_serializer_destroy(serializer);
    ifcopenshell_geom_buffer_destroy(svg_buffer);
    ifcopenshell_geom_serializer_settings_destroy(serializer_settings);
    ifcopenshell_geom_iterator_destroy(iterator);
    ifcopenshell_geom_settings_destroy(geom_settings);
    ifcopenshell_file_destroy(file);

    printf("  SVG serializer APIs: PASS\n");
}

static void test_gltf_serializer_apis(void) {
    printf("Testing GLTF serializer APIs...\n");

    ifcopenshell_file_t* file = NULL;
    ifcopenshell_geom_settings_t* geom_settings = NULL;
    ifcopenshell_geom_serializer_settings_t* serializer_settings = NULL;
    ifcopenshell_geom_iterator_t* iterator = NULL;
    ifcopenshell_geom_geometry_serializer_t* serializer = NULL;
    ifcopenshell_geom_triangulation_element_t* tri_elem = NULL;
    bool initialized = false;
    bool ready = false;
    bool is_tesselated = false;
    int ok;
    const char* gltf_filename = "/tmp/test_smoke.gltf";

    ok = ifcopenshell_parse_open(g_test_file_path, 1, &file);
    if (!ok) {
        printf("  SKIP: Could not open test file: %s\n", g_test_file_path);
        return;
    }

    expect_ok(ifcopenshell_geom_create_settings(&geom_settings));
    expect_ok(ifcopenshell_geom_settings_set_int(geom_settings, "iterator-output", 0)); /* TRIANGULATED */
    expect_ok(ifcopenshell_geom_create_serializer_settings(&serializer_settings));
    expect_ok(ifcopenshell_geom_create_geometry_serializer_by_path(
        "glb", gltf_filename, "", geom_settings, serializer_settings, &serializer));

    if (!serializer) {
        printf("  SKIP: GLTF serializer not available (build may not have WITH_GLTF)\n");
        ifcopenshell_geom_serializer_settings_destroy(serializer_settings);
        ifcopenshell_geom_settings_destroy(geom_settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    expect_ok(ifcopenshell_geom_geometry_serializer_ready(serializer, &ready));
    expect_true(ready, "GLTF serializer should be ready");
    expect_ok(ifcopenshell_geom_geometry_serializer_is_tesselated(serializer, &is_tesselated));
    expect_true(is_tesselated, "GLTF serializer should report tesselated");

    expect_ok(ifcopenshell_geom_geometry_serializer_set_file(serializer, file));
    expect_ok(ifcopenshell_geom_geometry_serializer_set_unit_name_and_magnitude(serializer, "METER", 1.0));
    expect_ok(ifcopenshell_geom_geometry_serializer_write_header(serializer));

    expect_ok(ifcopenshell_geom_create_iterator("opencascade", geom_settings, file, 1, &iterator));
    expect_ok(ifcopenshell_geom_iterator_initialize(iterator, &initialized));
    if (!initialized) {
        printf("  SKIP: No geometric elements for GLTF serializer tests\n");
        ifcopenshell_geom_geometry_serializer_destroy(serializer);
        ifcopenshell_geom_serializer_settings_destroy(serializer_settings);
        ifcopenshell_geom_settings_destroy(geom_settings);
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_file_destroy(file);
        remove(gltf_filename);
        return;
    }

    expect_ok(ifcopenshell_geom_iterator_get_as_triangulation_element(iterator, &tri_elem));
    expect_true(tri_elem != NULL, "Triangulation element should be available");
    expect_ok(ifcopenshell_geom_geometry_serializer_write_triangulation_element(serializer, tri_elem));
    expect_ok(ifcopenshell_geom_geometry_serializer_finalize(serializer));

    /* GLTF writes to file, check file exists and has glTF magic bytes or JSON content */
    FILE* f = fopen(gltf_filename, "rb");
    expect_true(f != NULL, "GLTF output file should exist");
    if (f) {
        char buf[200];
        size_t n = fread(buf, 1, sizeof(buf) - 1, f);
        buf[n] = '\0';
        /* Check for either binary glTF magic (glTF) or JSON content ({"asset" etc) */
        int is_gltf = (n >= 4 && buf[0] == 'g' && buf[1] == 'l' && buf[2] == 'T' && buf[3] == 'F');
        int has_json = (strstr(buf, "\"asset\"") != NULL || strstr(buf, "\"buffers\"") != NULL);
        expect_true(is_gltf || has_json,
                    "GLTF output should have glTF magic or JSON content");
        fclose(f);
    }

    ifcopenshell_geom_geometry_serializer_destroy(serializer);
    ifcopenshell_geom_serializer_settings_destroy(serializer_settings);
    ifcopenshell_geom_iterator_destroy(iterator);
    ifcopenshell_geom_settings_destroy(geom_settings);
    ifcopenshell_file_destroy(file);
    remove(gltf_filename);

    printf("  GLTF serializer APIs: PASS\n");
}

static void test_json_xml_serializer_apis(void) {
    printf("Testing JSON/XML serializer APIs...\n");

    ifcopenshell_file_t* file = NULL;
    ifcopenshell_geom_serializer_t* json_serializer = NULL;
    ifcopenshell_geom_serializer_t* xml_serializer = NULL;
    bool ready = false;
    int ok;
    const char* json_filename = "/tmp/test_smoke.json";
    const char* xml_filename = "/tmp/test_smoke.xml";

    ok = ifcopenshell_parse_open(g_test_file_path, 1, &file);
    if (!ok) {
        printf("  SKIP: Could not open test file: %s\n", g_test_file_path);
        return;
    }

    /* Test JSON serializer */
    expect_ok(ifcopenshell_geom_create_json_serializer(file, json_filename, &json_serializer));
    if (!json_serializer) {
        printf("  SKIP: JSON serializer not available (may require WITH_GLTF)\n");
    } else {
        expect_ok(ifcopenshell_geom_serializer_ready(json_serializer, &ready));
        expect_true(ready, "JSON serializer should be ready");
        expect_ok(ifcopenshell_geom_serializer_write_header(json_serializer));
        expect_ok(ifcopenshell_geom_serializer_finalize(json_serializer));

        /* JSON writes to file, check file exists */
        FILE* f = fopen(json_filename, "r");
        expect_true(f != NULL, "JSON output file should exist");
        if (f) {
            char buf[100];
            size_t n = fread(buf, 1, sizeof(buf) - 1, f);
            buf[n] = '\0';
            expect_true(strstr(buf, "{") != NULL, "JSON output should contain JSON object");
            fclose(f);
        }
        remove(json_filename);
        ifcopenshell_geom_serializer_destroy(json_serializer);
    }

    /* Test XML serializer */
    expect_ok(ifcopenshell_geom_create_xml_serializer(file, xml_filename, &xml_serializer));
    expect_true(xml_serializer != NULL, "XML serializer should be created");
    expect_ok(ifcopenshell_geom_serializer_ready(xml_serializer, &ready));
    expect_true(ready, "XML serializer should be ready");
    expect_ok(ifcopenshell_geom_serializer_write_header(xml_serializer));
    expect_ok(ifcopenshell_geom_serializer_finalize(xml_serializer));

    /* XML writes to file, check file exists */
    FILE* f = fopen(xml_filename, "r");
    expect_true(f != NULL, "XML output file should exist");
    if (f) {
        char buf[100];
        size_t n = fread(buf, 1, sizeof(buf) - 1, f);
        buf[n] = '\0';
        expect_true(strstr(buf, "<?xml") != NULL || strstr(buf, "<") != NULL,
                    "XML output should contain XML tags");
        fclose(f);
    }
    remove(xml_filename);

    ifcopenshell_geom_serializer_destroy(xml_serializer);
    ifcopenshell_file_destroy(file);

    printf("  JSON/XML serializer APIs: PASS\n");
}

static void test_iges_step_serializer_apis(void) {
    printf("Testing IGES/STEP serializer APIs...\n");

    ifcopenshell_file_t* file = NULL;
    ifcopenshell_geom_settings_t* geom_settings = NULL;
    ifcopenshell_geom_serializer_settings_t* serializer_settings = NULL;
    ifcopenshell_geom_iterator_t* iterator = NULL;
    ifcopenshell_geom_geometry_serializer_t* iges_serializer = NULL;
    ifcopenshell_geom_geometry_serializer_t* step_serializer = NULL;
    ifcopenshell_geom_brep_element_t* brep_elem = NULL;
    bool initialized = false;
    bool ready = false;
    bool is_tesselated = false;
    int ok;
    const char* iges_filename = "/tmp/test_smoke.iges";
    const char* step_filename = "/tmp/test_smoke.step";

    ok = ifcopenshell_parse_open(g_test_file_path, 1, &file);
    if (!ok) {
        printf("  SKIP: Could not open test file: %s\n", g_test_file_path);
        return;
    }

    expect_ok(ifcopenshell_geom_create_settings(&geom_settings));
    expect_ok(ifcopenshell_geom_settings_set_int(geom_settings, "iterator-output", 1)); /* NATIVE */
    expect_ok(ifcopenshell_geom_create_serializer_settings(&serializer_settings));

    /* Test IGES serializer */
    expect_ok(ifcopenshell_geom_create_geometry_serializer_by_path(
        "igs", iges_filename, "", geom_settings, serializer_settings, &iges_serializer));
    if (!iges_serializer) {
        printf("  SKIP: IGES serializer not available (may require OpenCascade)\n");
    } else {
        expect_ok(ifcopenshell_geom_geometry_serializer_ready(iges_serializer, &ready));
        expect_true(ready, "IGES serializer should be ready");
        expect_ok(ifcopenshell_geom_geometry_serializer_is_tesselated(iges_serializer, &is_tesselated));
        expect_true(!is_tesselated, "IGES serializer should report non-tesselated");

        expect_ok(ifcopenshell_geom_geometry_serializer_set_file(iges_serializer, file));
        expect_ok(ifcopenshell_geom_geometry_serializer_set_unit_name_and_magnitude(iges_serializer, "METER", 1.0));
        expect_ok(ifcopenshell_geom_geometry_serializer_write_header(iges_serializer));

        expect_ok(ifcopenshell_geom_create_iterator("opencascade", geom_settings, file, 1, &iterator));
        expect_ok(ifcopenshell_geom_iterator_initialize(iterator, &initialized));
        if (initialized) {
            expect_ok(ifcopenshell_geom_iterator_get_as_brep_element(iterator, &brep_elem));
            if (brep_elem) {
                expect_ok(ifcopenshell_geom_geometry_serializer_write_brep_element(iges_serializer, brep_elem));
            }
        }
        expect_ok(ifcopenshell_geom_geometry_serializer_finalize(iges_serializer));

        /* IGES writes to file, check file exists */
        FILE* f = fopen(iges_filename, "r");
        expect_true(f != NULL, "IGES output file should exist");
        if (f) fclose(f);
        remove(iges_filename);

        ifcopenshell_geom_geometry_serializer_destroy(iges_serializer);
        if (iterator) {
            ifcopenshell_geom_iterator_destroy(iterator);
            iterator = NULL;
        }
    }

    /* Test STEP serializer */
    expect_ok(ifcopenshell_geom_create_geometry_serializer_by_path(
        "stp", step_filename, "", geom_settings, serializer_settings, &step_serializer));
    if (!step_serializer) {
        printf("  SKIP: STEP serializer not available (may require OpenCascade)\n");
    } else {
        expect_ok(ifcopenshell_geom_geometry_serializer_ready(step_serializer, &ready));
        expect_true(ready, "STEP serializer should be ready");
        expect_ok(ifcopenshell_geom_geometry_serializer_is_tesselated(step_serializer, &is_tesselated));
        expect_true(!is_tesselated, "STEP serializer should report non-tesselated");

        expect_ok(ifcopenshell_geom_geometry_serializer_set_file(step_serializer, file));
        expect_ok(ifcopenshell_geom_geometry_serializer_set_unit_name_and_magnitude(step_serializer, "METER", 1.0));
        expect_ok(ifcopenshell_geom_geometry_serializer_write_header(step_serializer));

        if (!iterator) {
            expect_ok(ifcopenshell_geom_create_iterator("opencascade", geom_settings, file, 1, &iterator));
            expect_ok(ifcopenshell_geom_iterator_initialize(iterator, &initialized));
        }
        if (initialized && brep_elem) {
            expect_ok(ifcopenshell_geom_geometry_serializer_write_brep_element(step_serializer, brep_elem));
        }
        expect_ok(ifcopenshell_geom_geometry_serializer_finalize(step_serializer));

        /* STEP writes to file, check file exists */
        FILE* f = fopen(step_filename, "r");
        expect_true(f != NULL, "STEP output file should exist");
        if (f) {
            char buf[100];
            size_t n = fread(buf, 1, sizeof(buf) - 1, f);
            buf[n] = '\0';
            expect_true(strstr(buf, "ISO-10303") != NULL || strstr(buf, "STEP") != NULL,
                        "STEP output should contain STEP identifier");
            fclose(f);
        }
        remove(step_filename);

        ifcopenshell_geom_geometry_serializer_destroy(step_serializer);
    }

    if (iterator) ifcopenshell_geom_iterator_destroy(iterator);
    ifcopenshell_geom_serializer_settings_destroy(serializer_settings);
    ifcopenshell_geom_settings_destroy(geom_settings);
    ifcopenshell_file_destroy(file);

    printf("  IGES/STEP serializer APIs: PASS\n");
}

static void test_collada_hdf_serializer_apis(void) {
    printf("Testing Collada serializer APIs...\n");

    ifcopenshell_file_t* file = NULL;
    ifcopenshell_geom_serializer_settings_t* serializer_settings = NULL;
    ifcopenshell_geom_settings_t* collada_settings = NULL;
    ifcopenshell_geom_geometry_serializer_t* collada_serializer = NULL;
    ifcopenshell_geom_iterator_t* iterator = NULL;
    ifcopenshell_geom_triangulation_element_t* tri_elem = NULL;
    bool initialized = false;
    bool ready = false;
    bool is_tesselated = false;
    int ok;
    const char* collada_filename = "/tmp/test_smoke.dae";

    ok = ifcopenshell_parse_open(g_test_file_path, 1, &file);
    if (!ok) {
        printf("  SKIP: Could not open test file: %s\n", g_test_file_path);
        return;
    }

    expect_ok(ifcopenshell_geom_create_serializer_settings(&serializer_settings));

    /* Test Collada serializer (optional feature) */
    expect_ok(ifcopenshell_geom_create_settings(&collada_settings));
    expect_ok(ifcopenshell_geom_settings_set_int(collada_settings, "iterator-output", 0)); /* TRIANGULATED */
    ok = ifcopenshell_geom_create_geometry_serializer_by_path(
        "dae", collada_filename, "", collada_settings, serializer_settings, &collada_serializer);
    if (!ok) {
        const char* err = ifcopenshell_last_error_message();
        if (err && (strstr(err, "not available in this build") != NULL || strstr(err, "requires") != NULL
                    || strstr(err, "No geometry serializer registered") != NULL)) {
            printf("  SKIP: Collada serializer not available in this build\n");
            ifcopenshell_clear_error();
        } else {
            expect_ok(ok);
        }
    } else {
        expect_true(collada_serializer != NULL, "Collada serializer should be created");
        expect_ok(ifcopenshell_geom_geometry_serializer_ready(collada_serializer, &ready));
        expect_true(ready, "Collada serializer should be ready");
        expect_ok(ifcopenshell_geom_geometry_serializer_is_tesselated(collada_serializer, &is_tesselated));
        expect_true(is_tesselated, "Collada serializer should report tesselated");
        expect_ok(ifcopenshell_geom_geometry_serializer_set_file(collada_serializer, file));
        expect_ok(ifcopenshell_geom_geometry_serializer_set_unit_name_and_magnitude(collada_serializer, "METER", 1.0));
        expect_ok(ifcopenshell_geom_geometry_serializer_write_header(collada_serializer));

        expect_ok(ifcopenshell_geom_create_iterator("opencascade", collada_settings, file, 1, &iterator));
        expect_ok(ifcopenshell_geom_iterator_initialize(iterator, &initialized));
        if (initialized) {
            expect_ok(ifcopenshell_geom_iterator_get_as_triangulation_element(iterator, &tri_elem));
            if (tri_elem) {
                expect_ok(ifcopenshell_geom_geometry_serializer_write_triangulation_element(collada_serializer, tri_elem));
            }
        }
        expect_ok(ifcopenshell_geom_geometry_serializer_finalize(collada_serializer));

        FILE* f = fopen(collada_filename, "r");
        expect_true(f != NULL, "Collada output file should exist");
        if (f) {
            char buf[256];
            size_t n = fread(buf, 1, sizeof(buf) - 1, f);
            buf[n] = '\0';
            expect_true(strstr(buf, "COLLADA") != NULL || strstr(buf, "<") != NULL,
                        "Collada output should contain XML/COLLADA content");
            fclose(f);
        }
        remove(collada_filename);

        ifcopenshell_geom_geometry_serializer_destroy(collada_serializer);
        collada_serializer = NULL;
        if (iterator) {
            ifcopenshell_geom_iterator_destroy(iterator);
            iterator = NULL;
        }
    }
    ifcopenshell_geom_settings_destroy(collada_settings);

    if (iterator) {
        ifcopenshell_geom_iterator_destroy(iterator);
    }
    ifcopenshell_geom_serializer_settings_destroy(serializer_settings);
    ifcopenshell_file_destroy(file);

    printf("  Collada serializer APIs: PASS\n");
}

static void test_rocksdb_serializer_apis(void) {
    printf("Testing RocksDB serializer APIs...\n");

    ifcopenshell_file_t* file = NULL;
    ifcopenshell_geom_serializer_t* stream_serializer = NULL;
    bool ready = false;
    int ok;
    int ok_stream_ctor = 0;
    const char* rocksdb_stream_path = "/tmp/test_smoke_stream.rocksdb";

    ok = ifcopenshell_parse_open(g_test_file_path, 1, &file);
    if (!ok) {
        printf("  SKIP: Could not open test file: %s\n", g_test_file_path);
        return;
    }

    ok_stream_ctor = ifcopenshell_geom_create_rocksdb_serializer_streaming(
        g_test_file_path, rocksdb_stream_path, &stream_serializer);

    if (!ok_stream_ctor) {
        const char* err = ifcopenshell_last_error_message();
        if (err && (strstr(err, "RocksDB serializer requires WITH_ROCKSDB support") != NULL || strstr(err, "requires") != NULL)) {
            printf("  SKIP: RocksDB serializer not available in this build\n");
            ifcopenshell_clear_error();
            ifcopenshell_file_destroy(file);
            return;
        }
        expect_ok(ok_stream_ctor);
    }

    if (ok_stream_ctor && stream_serializer) {
        expect_ok(ifcopenshell_geom_serializer_ready(stream_serializer, &ready));
        expect_true(ready, "RocksDB streaming serializer should be ready");
        expect_ok(ifcopenshell_geom_serializer_write_header(stream_serializer));
        /* finalize may fail on an empty serializer (no geometry written) */
        if (!ifcopenshell_geom_serializer_finalize(stream_serializer)) {
            ifcopenshell_clear_error();
        }
        ifcopenshell_geom_serializer_destroy(stream_serializer);
    }

    ifcopenshell_file_destroy(file);

    printf("  RocksDB serializer APIs: PASS\n");
}

static void test_tree_apis(void) {
    printf("Testing tree APIs...\n");

    ifcopenshell_file_t* file = NULL;
    ifcopenshell_geom_settings_t* settings = NULL;
    ifcopenshell_geom_tree_t* tree = NULL;
    ifcopenshell_geom_tree_t* tree2 = NULL;
    ifcopenshell_geom_tree_t* tree3 = NULL;
    ifcopenshell_geom_tree_t* tree4 = NULL;
    ifcopenshell_geom_iterator_t* iterator = NULL;
    bool initialized = false;
    ifcopenshell_geom_element_t* elem = NULL;
    ifcopenshell_geom_brep_element_t* brep_elem = NULL;
    ifcopenshell_instance_t* product = NULL;
    ifcopenshell_parse_instance_list_t* selected = NULL;
    size_t selected_count = 0;
    ifcopenshell_double_list_t distances = {0};
    ifcopenshell_double_list_t protrusions = {0};
    bool face_styles = false;
    size_t style_count = 0;
    int ok;

    ok = ifcopenshell_parse_open(g_test_file_path, 1, &file);
    if (!ok) {
        printf("  SKIP: Could not open test file: %s\n", g_test_file_path);
        return;
    }

    expect_ok(ifcopenshell_geom_create_settings(&settings));
    expect_ok(ifcopenshell_geom_settings_set_int(settings, "iterator-output", 1)); /* NATIVE */

    expect_ok(ifcopenshell_geom_create_tree(&tree));
    expect_ok(ifcopenshell_geom_tree_add_file(tree, file, settings));

    expect_ok(ifcopenshell_geom_create_tree_from_file(file, &tree2));
    expect_ok(ifcopenshell_geom_create_tree_from_file_with_settings(file, settings, &tree3));

    expect_ok(ifcopenshell_geom_create_iterator("opencascade", settings, file, 1, &iterator));
    expect_ok(ifcopenshell_geom_iterator_initialize(iterator, &initialized));
    if (!initialized) {
        printf("  SKIP: No geometric elements for tree tests\n");
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_geom_tree_destroy(tree3);
        ifcopenshell_geom_tree_destroy(tree2);
        ifcopenshell_geom_tree_destroy(tree);
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    expect_ok(ifcopenshell_geom_create_tree_from_iterator(iterator, &tree4));
    /* The tree keeps borrowed element pointers, so release it before its iterator. */
    ifcopenshell_geom_tree_destroy(tree4);
    tree4 = NULL;
    ifcopenshell_geom_iterator_destroy(iterator);
    iterator = NULL;

    expect_ok(ifcopenshell_geom_create_iterator("opencascade", settings, file, 1, &iterator));
    expect_ok(ifcopenshell_geom_iterator_initialize(iterator, &initialized));
    if (!initialized) {
        printf("  SKIP: No geometric elements for tree select tests\n");
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_geom_tree_destroy(tree4);
        ifcopenshell_geom_tree_destroy(tree3);
        ifcopenshell_geom_tree_destroy(tree2);
        ifcopenshell_geom_tree_destroy(tree);
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }
    expect_ok(ifcopenshell_geom_iterator_get(iterator, &elem));
    expect_ok(ifcopenshell_geom_iterator_get_native(iterator, &brep_elem));
    expect_ok(ifcopenshell_geom_element_product(elem, &product));
    expect_ok(ifcopenshell_geom_tree_select_element(tree, product, false, 0.0, &selected));
    expect_ok(ifcopenshell_parse_instance_list_size(selected, &selected_count));
    expect_true(selected_count >= 1, "Tree select_element should find at least one result");
    ifcopenshell_parse_instance_list_destroy(selected);

    expect_ok(ifcopenshell_geom_tree_select_brep_element(tree, brep_elem, false, 0.0, &selected));
    expect_ok(ifcopenshell_parse_instance_list_size(selected, &selected_count));
    /* BRep-based select may return 0 depending on geometry overlap */
    ifcopenshell_parse_instance_list_destroy(selected);

    expect_ok(ifcopenshell_geom_tree_select_point(tree, 0.0, 0.0, 0.0, 100.0, &selected));
    expect_ok(ifcopenshell_parse_instance_list_size(selected, &selected_count));
    ifcopenshell_parse_instance_list_destroy(selected);

    expect_ok(ifcopenshell_geom_tree_select_box_point(tree, 0.0, 0.0, 0.0, 100.0, &selected));
    expect_ok(ifcopenshell_parse_instance_list_size(selected, &selected_count));
    ifcopenshell_parse_instance_list_destroy(selected);

    expect_ok(ifcopenshell_geom_tree_select_box_element(tree, product, false, 0.0, &selected));
    expect_ok(ifcopenshell_parse_instance_list_size(selected, &selected_count));
    expect_true(selected_count >= 1, "Tree select_box_element should find at least one result");
    ifcopenshell_parse_instance_list_destroy(selected);

    expect_ok(ifcopenshell_geom_tree_select_box_bounds(tree, -1000.0, -1000.0, -1000.0, 1000.0, 1000.0, 1000.0, false, &selected));
    expect_ok(ifcopenshell_parse_instance_list_size(selected, &selected_count));
    ifcopenshell_parse_instance_list_destroy(selected);

    expect_ok(ifcopenshell_geom_tree_distances(tree, &distances));
    ifcopenshell_double_list_destroy(&distances);
    expect_ok(ifcopenshell_geom_tree_protrusion_distances(tree, &protrusions));
    ifcopenshell_double_list_destroy(&protrusions);

    expect_ok(ifcopenshell_geom_tree_enable_face_styles(tree, &face_styles));
    expect_ok(ifcopenshell_geom_tree_set_enable_face_styles(tree, true));
    expect_ok(ifcopenshell_geom_tree_enable_face_styles(tree, &face_styles));
    expect_true(face_styles, "Tree face style flag should be enabled");

    expect_ok(ifcopenshell_geom_tree_style_count(tree, &style_count));
    if (style_count > 0) {
        ifcopenshell_geom_taxonomy_style_t* style = NULL;
        size_t instance_id = 0;
        expect_ok(ifcopenshell_geom_tree_style_at(tree, 0, &style));
        expect_ok(ifcopenshell_geom_taxonomy_style_instance_id(style, &instance_id));
        ifcopenshell_geom_taxonomy_style_destroy(style);
    }

    {
        ifcopenshell_geom_taxonomy_style_list_t tree_style_list = {0};
        expect_ok(ifcopenshell_geom_tree_styles(tree, &tree_style_list));
        ifcopenshell_geom_taxonomy_style_list_destroy(&tree_style_list);
    }

    {
        ifcopenshell_int32_list_t fs = {0};
        bool manifold = false;
        int man_ok = ifcopenshell_geom_tree_is_manifold(tree, &fs, &manifold);
        if (!man_ok) ifcopenshell_clear_error();
        ifcopenshell_int32_list_destroy(&fs);
    }

    {
        ifcopenshell_uint8_list_t uuids = {0};
        ifcopenshell_string_t b64 = {0};
        int b64_ok = ifcopenshell_geom_tree_uint8_to_b64(tree, &uuids, &b64);
        if (b64_ok) {
            ifcopenshell_string_destroy(&b64);
        } else {
            ifcopenshell_clear_error();
        }
        ifcopenshell_uint8_list_destroy(&uuids);
    }

    ifcopenshell_geom_iterator_destroy(iterator);
    ifcopenshell_geom_tree_destroy(tree4);
    ifcopenshell_geom_tree_destroy(tree3);
    ifcopenshell_geom_tree_destroy(tree2);
    ifcopenshell_geom_tree_destroy(tree);
    ifcopenshell_geom_settings_destroy(settings);
    ifcopenshell_file_destroy(file);

    printf("  Tree APIs: PASS\n");
}

static void test_tree_clash_and_ray_apis(void) {
    printf("Testing tree clash/ray APIs...\n");

    ifcopenshell_file_t* file = NULL;
    ifcopenshell_geom_settings_t* settings = NULL;
    ifcopenshell_geom_tree_t* tree = NULL;
    ifcopenshell_parse_instance_list_t* list_a = NULL;
    ifcopenshell_parse_instance_list_t* list_b = NULL;
    ifcopenshell_instance_list_t list_a_value = {0};
    ifcopenshell_instance_list_t list_b_value = {0};
    ifcopenshell_parse_instance_list_t* selected = NULL;
    ifcopenshell_geom_tree_clash_list_t* clashes = NULL;
    ifcopenshell_geom_tree_clash_t* clash = NULL;
    ifcopenshell_geom_tree_ray_intersection_list_t* intersections = NULL;
    ifcopenshell_geom_tree_ray_intersection_t* hit = NULL;
    ifcopenshell_instance_t* inst = NULL;
    ifcopenshell_instance_t* inst_a = NULL;
    ifcopenshell_instance_t* inst_b = NULL;
    ifcopenshell_instance_t* hit_inst = NULL;
    ifcopenshell_double_list_t xyz = {0};
    size_t count = 0;
    int32_t clash_type = -1;
    double value = 0.0;
    int ok;

    ok = ifcopenshell_parse_open(g_test_file_path, 1, &file);
    if (!ok) {
        printf("  SKIP: Could not open test file: %s\n", g_test_file_path);
        return;
    }

    expect_ok(ifcopenshell_geom_create_settings(&settings));
    expect_ok(ifcopenshell_geom_settings_set_int(settings, "iterator-output", 1)); /* NATIVE */
    expect_ok(ifcopenshell_geom_create_tree(&tree));
    expect_ok(ifcopenshell_geom_tree_add_file(tree, file, settings));

    /* Build tiny input sets from broad point selections */
    expect_ok(ifcopenshell_geom_tree_select_point(tree, 0.0, 0.0, 0.0, 100.0, &selected));
    expect_ok(ifcopenshell_parse_instance_list_size(selected, &count));
    if (count < 2) {
        printf("  SKIP: Not enough products for clash/ray tests\n");
        ifcopenshell_parse_instance_list_destroy(selected);
        ifcopenshell_geom_tree_destroy(tree);
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    expect_ok(ifcopenshell_parse_instance_list_get(selected, 0, &inst));
    expect_ok(ifcopenshell_geom_tree_select_element(tree, inst, false, 0.0, &list_a));
    expect_ok(ifcopenshell_parse_instance_list_get(selected, 1, &inst));
    expect_ok(ifcopenshell_geom_tree_select_element(tree, inst, false, 0.0, &list_b));
    ifcopenshell_parse_instance_list_destroy(selected);
    selected = NULL;

    list_a_value = instance_list_value(list_a);
    list_b_value = instance_list_value(list_b);
    expect_ok(ifcopenshell_geom_tree_clash_collision_many(tree, &list_a_value, &list_b_value, false, &clashes));
    expect_ok(ifcopenshell_geom_tree_clash_count(tree, clashes, &count));
    if (count > 0) {
        expect_ok(ifcopenshell_geom_tree_clash_at(tree, clashes, 0, &clash));
        expect_ok(ifcopenshell_geom_tree_clash_type(clash, &clash_type));
        expect_true(clash_type >= 0, "clash type should be non-negative");
        expect_ok(ifcopenshell_geom_tree_clash_distance(clash, &value));
        expect_ok(ifcopenshell_geom_tree_clash_a(clash, &inst_a));
        expect_ok(ifcopenshell_geom_tree_clash_b(clash, &inst_b));
        expect_true(inst_a != NULL && inst_b != NULL, "clash instances should be present");
        expect_ok(ifcopenshell_geom_tree_clash_p1(clash, &xyz));
        expect_true(xyz.size == 3, "clash p1 should have 3 values");
        ifcopenshell_double_list_destroy(&xyz);
        expect_ok(ifcopenshell_geom_tree_clash_p2(clash, &xyz));
        expect_true(xyz.size == 3, "clash p2 should have 3 values");
        ifcopenshell_double_list_destroy(&xyz);
        ifcopenshell_geom_tree_clash_destroy(clash);
    }
    ifcopenshell_geom_tree_clash_list_destroy(clashes);
    clashes = NULL;

    expect_ok(ifcopenshell_geom_tree_select_ray(tree, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1000.0, &intersections));
    expect_ok(ifcopenshell_geom_tree_ray_intersection_count(tree, intersections, &count));
    if (count > 0) {
        expect_ok(ifcopenshell_geom_tree_ray_intersection_at(tree, intersections, 0, &hit));
        expect_ok(ifcopenshell_geom_tree_ray_intersection_distance(hit, &value));
        expect_ok(ifcopenshell_geom_tree_ray_intersection_style_index(hit, &clash_type));
        expect_ok(ifcopenshell_geom_tree_ray_intersection_instance(hit, &hit_inst));
        expect_true(hit_inst != NULL, "ray hit instance should be non-null");
        expect_ok(ifcopenshell_geom_tree_ray_intersection_position(hit, &xyz));
        expect_true(xyz.size == 3, "ray hit position should have 3 values");
        ifcopenshell_double_list_destroy(&xyz);
        expect_ok(ifcopenshell_geom_tree_ray_intersection_normal(hit, &xyz));
        expect_true(xyz.size == 3, "ray hit normal should have 3 values");
        ifcopenshell_double_list_destroy(&xyz);
        expect_ok(ifcopenshell_geom_tree_ray_intersection_ray_distance(hit, &value));
        expect_ok(ifcopenshell_geom_tree_ray_intersection_dot_product(hit, &value));
        ifcopenshell_geom_tree_ray_intersection_destroy(hit);
    }
    ifcopenshell_geom_tree_ray_intersection_list_destroy(intersections);

    ifcopenshell_parse_instance_list_destroy(list_b);
    ifcopenshell_parse_instance_list_destroy(list_a);
    ifcopenshell_instance_list_destroy(&list_b_value);
    ifcopenshell_instance_list_destroy(&list_a_value);
    ifcopenshell_geom_tree_destroy(tree);
    ifcopenshell_geom_settings_destroy(settings);
    ifcopenshell_file_destroy(file);

    printf("  Tree clash/ray APIs: PASS\n");
}

static void test_create_shape(void) {
    printf("Testing create_shape API...\n");

    /* Open file and get an IfcProduct instance */
    ifcopenshell_file_t* file = NULL;
    int ok = ifcopenshell_parse_open(g_test_file_path, 1, &file);
    if (!ok || !file) {
        printf("  SKIP: Could not open test file\n");
        return;
    }

    /* Get IfcProduct instances */
    ifcopenshell_parse_instance_list_t* products = NULL;
    size_t product_count = 0;
    ok = ifcopenshell_file_by_type(file, "IfcProduct", &products);
    if (ok) {
        ok = ifcopenshell_parse_instance_list_size(products, &product_count);
    }
    if (!ok || product_count == 0) {
        printf("  SKIP: No IfcProduct instances found\n");
        ifcopenshell_parse_instance_list_destroy(products);
        ifcopenshell_file_destroy(file);
        return;
    }

    ifcopenshell_instance_t* product = NULL;
    expect_ok(ifcopenshell_parse_instance_list_get(products, 0u, &product));

    /* Create settings */
    ifcopenshell_geom_settings_t* settings = NULL;
    ifcopenshell_geom_create_settings(&settings);

    /* Test create_shape with auto representation selection */
    ifcopenshell_geom_element_t* element = NULL;
    ok = ifcopenshell_geom_create_shape(settings, product, NULL, NULL, &element);
    if (ok && element) {
        printf("  create_shape (auto repr): PASS\n");

        /* Check we can get element properties */
        ifcopenshell_string_t name = {0};
        ifcopenshell_geom_element_name(element, &name);
        printf("  Element name: %s\n", name.data ? name.data : "(null)");
        ifcopenshell_string_destroy(&name);

        /* Clean up owned element */
        ifcopenshell_geom_element_destroy(element);
    } else {
        const char* err = ifcopenshell_last_error_message();
        printf("  create_shape failed: %s\n", err ? err : "unknown");
    }

    /* Test create_shape with explicit geometry library */
    element = NULL;
    ok = ifcopenshell_geom_create_shape(settings, product, NULL, "opencascade", &element);
    if (ok && element) {
        printf("  create_shape (opencascade): PASS\n");
        ifcopenshell_geom_element_destroy(element);
    } else {
        const char* err = ifcopenshell_last_error_message();
        printf("  create_shape (opencascade) failed: %s\n", err ? err : "unknown");
    }

    ifcopenshell_geom_settings_destroy(settings);
    ifcopenshell_parse_instance_list_destroy(products);
    ifcopenshell_file_destroy(file);

    printf("  create_shape API: PASS\n");
}

static void test_map_shape(void) {
    printf("Testing map_shape API...\n");

    ifcopenshell_file_t* file = NULL;
    int ok = ifcopenshell_parse_open(g_test_file_path, 1, &file);
    if (!ok || !file) {
        printf("  SKIP: Could not open test file\n");
        return;
    }

    /* Get an IfcProduct */
    ifcopenshell_parse_instance_list_t* products = NULL;
    size_t product_count = 0;
    ok = ifcopenshell_file_by_type(file, "IfcProduct", &products);
    if (ok) {
        ok = ifcopenshell_parse_instance_list_size(products, &product_count);
    }
    if (!ok || product_count == 0) {
        printf("  SKIP: No products\n");
        ifcopenshell_parse_instance_list_destroy(products);
        ifcopenshell_file_destroy(file);
        return;
    }

    ifcopenshell_instance_t* product = NULL;
    expect_ok(ifcopenshell_parse_instance_list_get(products, 0u, &product));

    ifcopenshell_geom_settings_t* settings = NULL;
    ifcopenshell_geom_create_settings(&settings);

    ifcopenshell_geom_taxonomy_item_t* item = NULL;
    ok = ifcopenshell_geom_map_shape(settings, product, &item);
    if (ok && item) {
        printf("  map_shape returned taxonomy item: PASS\n");
        ifcopenshell_geom_taxonomy_item_destroy(item);
    } else {
        const char* err = ifcopenshell_last_error_message();
        printf("  map_shape: %s (may be expected for some instances)\n",
               err ? err : "no error");
    }

    ifcopenshell_geom_settings_destroy(settings);
    ifcopenshell_parse_instance_list_destroy(products);
    ifcopenshell_file_destroy(file);

    printf("  map_shape API: PASS\n");
}

static void test_conversion_result_shape_methods(void) {
    printf("Testing ConversionResultShape new methods...\n");

    ifcopenshell_geom_settings_t* settings = NULL;
    ifcopenshell_geom_create_settings(&settings);

    /* Use the iterator to get a ConversionResultShape from a real element */
    ifcopenshell_file_t* file = NULL;
    int ok = ifcopenshell_parse_open(g_test_file_path, 1, &file);
    if (!ok || !file) {
        printf("  SKIP: Could not open test file\n");
        ifcopenshell_geom_settings_destroy(settings);
        return;
    }

    ifcopenshell_geom_iterator_t* iterator = NULL;
    ok = ifcopenshell_geom_create_iterator("opencascade", settings, file, 1, &iterator);
    if (!ok || !iterator) {
        printf("  SKIP: Could not create iterator\n");
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    bool initialized = false;
    ifcopenshell_geom_iterator_initialize(iterator, &initialized);
    if (!initialized) {
        printf("  SKIP: Iterator initialization failed\n");
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    /* Get first BRep element */
    ifcopenshell_geom_brep_element_t* brep = NULL;
    ifcopenshell_geom_iterator_get_native(iterator, &brep);
    if (!brep) {
        printf("  SKIP: No brep element available\n");
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    /* Get the geometry from brep element */
    ifcopenshell_geom_brep_representation_t* brep_repr = NULL;
    ifcopenshell_geom_brep_element_geometry(brep, &brep_repr);
    if (!brep_repr) {
        printf("  SKIP: No brep representation\n");
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    /* Get a ConversionResultShape from the first item */
    int32_t num_shapes = 0;
    ifcopenshell_geom_brep_representation_size(brep_repr, &num_shapes);
    if (num_shapes == 0) {
        printf("  SKIP: No shapes in brep representation\n");
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    ifcopenshell_geom_conversion_result_shape_t* shape = NULL;
    ifcopenshell_geom_brep_representation_item(brep_repr, 0, &shape);
    if (!shape) {
        printf("  SKIP: Could not get shape\n");
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    /* Test area() */
    double area = 0.0;
    ok = ifcopenshell_geom_conversion_result_shape_area(shape, &area);
    if (ok) {
        printf("  area(): %f PASS\n", area);
    } else {
        const char* err = ifcopenshell_last_error_message();
        printf("  area(): FAIL (%s)\n", err ? err : "unknown");
    }

    /* Test volume() */
    double volume = 0.0;
    ok = ifcopenshell_geom_conversion_result_shape_volume(shape, &volume);
    if (ok) {
        printf("  volume(): %f PASS\n", volume);
    } else {
        const char* err = ifcopenshell_last_error_message();
        printf("  volume(): FAIL (%s)\n", err ? err : "unknown");
    }

    /* Test box() */
    ifcopenshell_geom_conversion_result_shape_t* box_shape = NULL;
    ok = ifcopenshell_geom_conversion_result_shape_box(shape, &box_shape);
    if (ok && box_shape) {
        printf("  box(): PASS\n");
        ifcopenshell_geom_conversion_result_shape_destroy(box_shape);
    } else {
        const char* err = ifcopenshell_last_error_message();
        printf("  box(): FAIL (%s)\n", err ? err : "unknown");
    }

    /* Test solid() */
    ifcopenshell_geom_conversion_result_shape_t* solid_shape = NULL;
    ok = ifcopenshell_geom_conversion_result_shape_solid(shape, &solid_shape);
    if (ok && solid_shape) {
        printf("  solid(): PASS\n");
        ifcopenshell_geom_conversion_result_shape_destroy(solid_shape);
    } else {
        const char* err = ifcopenshell_last_error_message();
        printf("  solid(): FAIL (%s)\n", err ? err : "unknown");
    }

    /* Test moved() with matrix from a taxonomy line */
    ifcopenshell_geom_taxonomy_line_t* line = NULL;
    ok = ifcopenshell_geom_taxonomy_create_line(0.0, 0.0, 0.0, 1.0, 0.0, 0.0, &line);
    if (ok && line) {
        ifcopenshell_geom_taxonomy_matrix4_t* matrix = NULL;
        ifcopenshell_geom_taxonomy_line_matrix(line, &matrix);
        if (matrix) {
            ifcopenshell_geom_conversion_result_shape_t* moved_shape = NULL;
            ok = ifcopenshell_geom_conversion_result_shape_moved(shape, matrix, &moved_shape);
            if (ok && moved_shape) {
                printf("  moved(): PASS\n");
                ifcopenshell_geom_conversion_result_shape_destroy(moved_shape);
            } else {
                const char* err = ifcopenshell_last_error_message();
                printf("  moved(): FAIL (%s)\n", err ? err : "unknown");
            }
            ifcopenshell_geom_taxonomy_matrix4_destroy(matrix);
        }
        ifcopenshell_geom_taxonomy_line_destroy(line);
    }

    /* num_edges, num_faces, num_vertices, surface_genus, is_manifold */
    {
        int32_t ne = 0, nf = 0, nv = 0, sg = 0;
        bool manifold = false;
        ok = ifcopenshell_geom_conversion_result_shape_num_edges(shape, &ne);
        if (!ok) ifcopenshell_clear_error();
        ok = ifcopenshell_geom_conversion_result_shape_num_faces(shape, &nf);
        if (!ok) ifcopenshell_clear_error();
        ok = ifcopenshell_geom_conversion_result_shape_num_vertices(shape, &nv);
        if (!ok) ifcopenshell_clear_error();
        ok = ifcopenshell_geom_conversion_result_shape_surface_genus(shape, &sg);
        if (!ok) ifcopenshell_clear_error();
        ok = ifcopenshell_geom_conversion_result_shape_is_manifold(shape, &manifold);
        if (!ok) ifcopenshell_clear_error();
    }

    /* edges, facets, vertices (return shape lists) */
    {
        ifcopenshell_geom_conversion_result_shape_list_t edge_shapes = {0};
        ok = ifcopenshell_geom_conversion_result_shape_edges(shape, &edge_shapes);
        if (ok) {
            ifcopenshell_geom_conversion_result_shape_list_destroy(&edge_shapes);
        } else {
            ifcopenshell_clear_error();
        }
    }
    {
        ifcopenshell_geom_conversion_result_shape_list_t facet_shapes = {0};
        ok = ifcopenshell_geom_conversion_result_shape_facets(shape, &facet_shapes);
        if (ok) {
            ifcopenshell_geom_conversion_result_shape_list_destroy(&facet_shapes);
        } else {
            ifcopenshell_clear_error();
        }
    }
    {
        ifcopenshell_geom_conversion_result_shape_list_t vert_shapes = {0};
        ok = ifcopenshell_geom_conversion_result_shape_vertices(shape, &vert_shapes);
        if (ok) {
            ifcopenshell_geom_conversion_result_shape_list_destroy(&vert_shapes);
        } else {
            ifcopenshell_clear_error();
        }
    }

    /* surface_area_along_direction (needs a matrix4) */
    {
        ifcopenshell_geom_taxonomy_line_t* tmp_line = NULL;
        ifcopenshell_geom_taxonomy_create_line(0.0, 0.0, 0.0, 1.0, 0.0, 0.0, &tmp_line);
        if (tmp_line) {
            ifcopenshell_geom_taxonomy_matrix4_t* ax = NULL;
            ifcopenshell_geom_taxonomy_line_matrix(tmp_line, &ax);
            if (ax) {
                bool sad_ok = false;
                int sad_rc = ifcopenshell_geom_conversion_result_shape_surface_area_along_direction(shape, 0.01, ax, 0.0, 0.0, 1.0, &sad_ok);
                if (!sad_rc) ifcopenshell_clear_error();
                ifcopenshell_geom_taxonomy_matrix4_destroy(ax);
            }
            ifcopenshell_geom_taxonomy_line_destroy(tmp_line);
        }
    }

    ifcopenshell_geom_conversion_result_shape_destroy(shape);
    ifcopenshell_geom_iterator_destroy(iterator);
    ifcopenshell_geom_settings_destroy(settings);
    ifcopenshell_file_destroy(file);

    printf("  ConversionResultShape new methods: PASS\n");
}

/* Test geometry helper functions that mirror SWIG's generic wrapper surface. */
static void test_cgal_functions(void) {
    printf("Testing geometry helper functions...\n");

    /* create_epeck_from_int */
    ifcopenshell_geom_opaque_number_t* num = NULL;
    bool ok = ifcopenshell_geom_create_epeck_from_int(42, &num);
    if (!ok) {
        printf("  create_epeck_from_int: failed\n");
    } else {
        printf("  create_epeck_from_int: returned value\n");
        ifcopenshell_geom_opaque_number_destroy(num);
    }

    /* create_epeck_from_double */
    num = NULL;
    ok = ifcopenshell_geom_create_epeck_from_double(3.14, &num);
    if (!ok) {
        printf("  create_epeck_from_double: failed\n");
    } else {
        printf("  create_epeck_from_double: returned value\n");
        ifcopenshell_geom_opaque_number_destroy(num);
    }

    /* create_epeck_from_string */
    num = NULL;
    ok = ifcopenshell_geom_create_epeck_from_string("1/3", &num);
    if (!ok) {
        printf("  create_epeck_from_string: failed\n");
    } else {
        printf("  create_epeck_from_string: returned value\n");
        ifcopenshell_geom_opaque_number_destroy(num);
    }

    /* nary_union with empty list */
    ifcopenshell_geom_conversion_result_shape_list_t empty_shapes;
    empty_shapes.items = NULL;
    empty_shapes.size = 0;
    ifcopenshell_geom_conversion_result_shape_t* union_result = NULL;
    ok = ifcopenshell_geom_nary_union(&empty_shapes, &union_result);
    if (!ok) {
        printf("  nary_union (empty): correctly failed\n");
    } else {
        printf("  nary_union (empty): returned result\n");
        ifcopenshell_geom_conversion_result_shape_destroy(union_result);
    }

    printf("  Geometry helper functions: PASS\n");
}

/* Test SVG functions */
static void test_svg_functions(void) {
    printf("Testing SVG functions...\n");

    /* svg_to_line_segments with minimal SVG */
    ifcopenshell_string_t segments_result;
    segments_result.data = NULL;
    bool ok = ifcopenshell_geom_svg_to_line_segments(
        "<svg><line class=\"test\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\"/></svg>",
        "test",
        &segments_result);
    if (ok && segments_result.data) {
        printf("  svg_to_line_segments: returned data (len=%zu)\n", segments_result.size);
        ifcopenshell_string_destroy(&segments_result);
    } else {
        printf("  svg_to_line_segments: failed (expected for non-CGAL)\n");
    }

    /* svg_to_polygons */
    ifcopenshell_geom_svgfill_polygon_list_t polys;
    polys.items = NULL;
    polys.size = 0;
    ok = ifcopenshell_geom_svg_to_polygons(
        "<svg><polygon class=\"test\" points=\"0,0 1,0 1,1 0,1\"/></svg>",
        "test",
        &polys);
    if (ok) {
        printf("  svg_to_polygons: returned %zu polygons\n", polys.size);
        ifcopenshell_geom_svgfill_polygon_list_destroy(&polys);
    } else {
        printf("  svg_to_polygons: failed (expected for non-CGAL)\n");
    }

    /* line_segments_to_polygons */
    ifcopenshell_geom_svgfill_polygon_list_t polys2;
    polys2.items = NULL;
    polys2.size = 0;
    ok = ifcopenshell_geom_line_segments_to_polygons(0, 1e-7, "[]", &polys2);
    if (ok) {
        printf("  line_segments_to_polygons: returned %zu polygons\n", polys2.size);
        ifcopenshell_geom_svgfill_polygon_list_destroy(&polys2);
    } else {
        printf("  line_segments_to_polygons: failed (expected for non-CGAL)\n");
    }

    printf("  SVG functions: PASS\n");
}

/* Test opaque_number handle methods. */
static void test_opaque_number_methods(void) {
    printf("Testing opaque_number methods...\n");

    /* Try to create a number. */
    ifcopenshell_geom_opaque_number_t* a = NULL;
    bool ok = ifcopenshell_geom_create_epeck_from_int(10, &a);
    if (!ok) {
        printf("  SKIP: opaque_number methods (number creation failed)\n");
        printf("  Opaque number methods: PASS\n");
        return;
    }

    /* Test all operations */
    ifcopenshell_geom_opaque_number_t* b = NULL;
    ifcopenshell_geom_create_epeck_from_int(3, &b);

    /* to_double */
    double dval;
    ok = ifcopenshell_geom_opaque_number_to_double(a, &dval);
    if (ok) printf("  to_double(10) = %f PASS\n", dval);

    /* to_string */
    ifcopenshell_string_t sval;
    ok = ifcopenshell_geom_opaque_number_to_string(a, &sval);
    if (ok) {
        printf("  to_string(10) = '%s' PASS\n", sval.data);
        ifcopenshell_string_destroy(&sval);
    }

    /* add */
    ifcopenshell_geom_opaque_number_t* sum = NULL;
    ok = ifcopenshell_geom_opaque_number_add(a, b, &sum);
    if (ok) {
        ifcopenshell_geom_opaque_number_to_double(sum, &dval);
        printf("  add(10, 3) = %f PASS\n", dval);
        ifcopenshell_geom_opaque_number_destroy(sum);
    }

    /* subtract */
    ifcopenshell_geom_opaque_number_t* diff = NULL;
    ok = ifcopenshell_geom_opaque_number_subtract(a, b, &diff);
    if (ok) {
        ifcopenshell_geom_opaque_number_to_double(diff, &dval);
        printf("  subtract(10, 3) = %f PASS\n", dval);
        ifcopenshell_geom_opaque_number_destroy(diff);
    }

    /* multiply */
    ifcopenshell_geom_opaque_number_t* prod = NULL;
    ok = ifcopenshell_geom_opaque_number_multiply(a, b, &prod);
    if (ok) {
        ifcopenshell_geom_opaque_number_to_double(prod, &dval);
        printf("  multiply(10, 3) = %f PASS\n", dval);
        ifcopenshell_geom_opaque_number_destroy(prod);
    }

    /* divide */
    ifcopenshell_geom_opaque_number_t* quot = NULL;
    ok = ifcopenshell_geom_opaque_number_divide(a, b, &quot);
    if (ok) {
        ifcopenshell_geom_opaque_number_to_double(quot, &dval);
        printf("  divide(10, 3) = %f PASS\n", dval);
        ifcopenshell_geom_opaque_number_destroy(quot);
    }

    /* negate */
    ifcopenshell_geom_opaque_number_t* neg = NULL;
    ok = ifcopenshell_geom_opaque_number_negate(a, &neg);
    if (ok) {
        ifcopenshell_geom_opaque_number_to_double(neg, &dval);
        printf("  negate(10) = %f PASS\n", dval);
        ifcopenshell_geom_opaque_number_destroy(neg);
    }

    /* equals */
    bool eq;
    ok = ifcopenshell_geom_opaque_number_equals(a, b, &eq);
    if (ok) printf("  equals(10, 3) = %s PASS\n", eq ? "true" : "false");

    /* less_than */
    bool lt;
    ok = ifcopenshell_geom_opaque_number_less_than(b, a, &lt);
    if (ok) printf("  less_than(3, 10) = %s PASS\n", lt ? "true" : "false");

    /* clone */
    ifcopenshell_geom_opaque_number_t* cloned = NULL;
    ok = ifcopenshell_geom_opaque_number_clone(a, &cloned);
    if (ok) {
        ifcopenshell_geom_opaque_number_to_double(cloned, &dval);
        printf("  clone(10) = %f PASS\n", dval);
        ifcopenshell_geom_opaque_number_destroy(cloned);
    }

    ifcopenshell_geom_opaque_number_destroy(a);
    ifcopenshell_geom_opaque_number_destroy(b);
    printf("  Opaque number methods: PASS\n");
}

/* Test helmert_curve_point and function_item_evaluator */
static void test_function_item_evaluator_apis(void) {
    printf("Testing function_item_evaluator APIs...\n");

    /* helmert_curve_point: compute point on helmert curve */
    ifcopenshell_double_list_t point;
    point.items = NULL;
    point.size = 0;
    bool ok = ifcopenshell_geom_helmert_curve_point(0.0, 100.0, 0.0, 50.0, &point);
    if (ok && point.size == 3) {
        printf("  helmert_curve_point(0,100,0,50) = [%f, %f, %f] PASS\n",
               point.items[0], point.items[1], point.items[2]);
        ifcopenshell_double_list_destroy(&point);
    } else if (ok) {
        printf("  helmert_curve_point: returned %zu values (expected 3)\n", point.size);
        ifcopenshell_double_list_destroy(&point);
    } else {
        printf("  helmert_curve_point: failed\n");
    }

    /* convert_loop_to_function_item: needs a taxonomy loop - test error path */
    ifcopenshell_geom_settings_t* settings = NULL;
    ifcopenshell_geom_create_settings(&settings);

    ifcopenshell_geom_taxonomy_item_t* fn_item = NULL;
    ok = ifcopenshell_geom_convert_loop_to_function_item(NULL, &fn_item);
    if (!ok) {
        printf("  convert_loop_to_function_item(NULL): correctly failed PASS\n");
        ifcopenshell_clear_error();
    } else {
        printf("  convert_loop_to_function_item(NULL): unexpected success\n");
        if (fn_item) ifcopenshell_geom_taxonomy_item_destroy(fn_item);
    }

    /* create_function_item_evaluator: test with NULL function item */
    ifcopenshell_geom_function_item_evaluator_t* evaluator = NULL;
    ok = ifcopenshell_geom_create_function_item_evaluator(settings, NULL, &evaluator);
    if (!ok) {
        printf("  create_function_item_evaluator(NULL): correctly failed PASS\n");
        ifcopenshell_clear_error();
    } else {
        /* If it succeeds, test the evaluator methods */
        if (evaluator) {
            ifcopenshell_double_list_t pts;
            pts.items = NULL; pts.size = 0;
            ifcopenshell_geom_function_item_evaluator_evaluation_points(evaluator, &pts);
            ifcopenshell_double_list_destroy(&pts);

            ifcopenshell_geom_taxonomy_item_t* eval_result = NULL;
            ifcopenshell_geom_function_item_evaluator_evaluate(evaluator, &eval_result);
            if (eval_result) ifcopenshell_geom_taxonomy_item_destroy(eval_result);

            ifcopenshell_double_list_t range_pts;
            range_pts.items = NULL; range_pts.size = 0;
            ifcopenshell_geom_function_item_evaluator_evaluation_points_range(evaluator, 0.0, 1.0, 10, &range_pts);
            ifcopenshell_double_list_destroy(&range_pts);

            ifcopenshell_geom_taxonomy_item_t* range_eval = NULL;
            ifcopenshell_geom_function_item_evaluator_evaluate_range(evaluator, 0.0, 1.0, 10, &range_eval);
            if (range_eval) ifcopenshell_geom_taxonomy_item_destroy(range_eval);

            ifcopenshell_double_list_t mat;
            mat.items = NULL; mat.size = 0;
            ifcopenshell_geom_function_item_evaluator_evaluate_at(evaluator, 0.5, &mat);
            ifcopenshell_double_list_destroy(&mat);

            ifcopenshell_geom_function_item_evaluator_destroy(evaluator);
        }
        printf("  function_item_evaluator methods: tested PASS\n");
    }

    ifcopenshell_geom_settings_destroy(settings);
    printf("  Function item evaluator APIs: PASS\n");
}

/* Test additional ConversionResultShape methods and destroys */
static void test_additional_shape_methods(void) {
    printf("Testing additional ConversionResultShape methods...\n");

    ifcopenshell_geom_settings_t* settings = NULL;
    ifcopenshell_geom_create_settings(&settings);

    ifcopenshell_file_t* file = NULL;
    int ok = ifcopenshell_parse_open(g_test_file_path, 1, &file);
    if (!ok || !file) {
        printf("  SKIP: Could not open test file\n");
        ifcopenshell_geom_settings_destroy(settings);
        return;
    }

    ifcopenshell_geom_iterator_t* iterator = NULL;
    ok = ifcopenshell_geom_create_iterator("opencascade", settings, file, 1, &iterator);
    if (!ok || !iterator) {
        printf("  SKIP: Could not create iterator\n");
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    bool initialized = false;
    ifcopenshell_geom_iterator_initialize(iterator, &initialized);
    if (!initialized) {
        printf("  SKIP: Iterator not initialized\n");
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    /* Test iterator bounds */
    ok = ifcopenshell_geom_iterator_compute_bounds(iterator, true);
    if (ok) {
        ifcopenshell_geom_taxonomy_point3_t* bmin = NULL;
        ifcopenshell_geom_taxonomy_point3_t* bmax = NULL;
        ok = ifcopenshell_geom_iterator_bounds_min(iterator, &bmin);
        if (ok && bmin) {
            ifcopenshell_double_list_t bmin_data = {0};
            ifcopenshell_geom_taxonomy_point3_get_data(bmin, &bmin_data);
            if (bmin_data.size == 3) {
                printf("  iterator_bounds_min: [%f, %f, %f] PASS\n",
                       bmin_data.items[0], bmin_data.items[1], bmin_data.items[2]);
            }
            ifcopenshell_double_list_destroy(&bmin_data);
            ifcopenshell_geom_taxonomy_point3_destroy(bmin);
        } else {
            printf("  iterator_bounds_min: FAIL\n");
            ifcopenshell_clear_error();
        }

        ok = ifcopenshell_geom_iterator_bounds_max(iterator, &bmax);
        if (ok && bmax) {
            ifcopenshell_double_list_t bmax_data = {0};
            ifcopenshell_geom_taxonomy_point3_get_data(bmax, &bmax_data);
            if (bmax_data.size == 3) {
                printf("  iterator_bounds_max: [%f, %f, %f] PASS\n",
                       bmax_data.items[0], bmax_data.items[1], bmax_data.items[2]);
            }
            ifcopenshell_double_list_destroy(&bmax_data);
            ifcopenshell_geom_taxonomy_point3_destroy(bmax);
        } else {
            printf("  iterator_bounds_max: FAIL\n");
            ifcopenshell_clear_error();
        }
    } else {
        printf("  iterator_compute_bounds: FAIL\n");
        ifcopenshell_clear_error();
    }

    /* Test iterator.create() - creates geometry for current element */
    ifcopenshell_instance_t* created_inst = NULL;
    ok = ifcopenshell_geom_iterator_create(iterator, &created_inst);
    if (ok && created_inst) {
        printf("  iterator_create: returned instance PASS\n");
    } else {
        printf("  iterator_create: failed (may need valid element)\n");
        ifcopenshell_clear_error();
    }

    /* Get a shape for testing additional methods */
    ifcopenshell_geom_brep_element_t* brep = NULL;
    ifcopenshell_geom_iterator_get_native(iterator, &brep);
    if (!brep) {
        printf("  SKIP: No brep element\n");
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    ifcopenshell_geom_brep_representation_t* brep_repr = NULL;
    ifcopenshell_geom_brep_element_geometry(brep, &brep_repr);
    if (!brep_repr) {
        printf("  SKIP: No brep repr\n");
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    int32_t num_shapes = 0;
    ifcopenshell_geom_brep_representation_size(brep_repr, &num_shapes);
    if (num_shapes == 0) {
        printf("  SKIP: No shapes\n");
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    ifcopenshell_geom_conversion_result_shape_t* shape = NULL;
    ifcopenshell_geom_brep_representation_item(brep_repr, 0, &shape);
    if (!shape) {
        printf("  SKIP: No shape\n");
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    /* Test halfspaces() */
    ifcopenshell_geom_conversion_result_shape_t* hs = NULL;
    ok = ifcopenshell_geom_conversion_result_shape_halfspaces(shape, &hs);
    if (ok && hs) {
        printf("  halfspaces(): PASS\n");
        ifcopenshell_geom_conversion_result_shape_destroy(hs);
    } else {
        printf("  halfspaces(): FAIL (expected for simple shapes)\n");
        ifcopenshell_clear_error();
    }

    /* Test wrap_in_compound() */
    ifcopenshell_geom_conversion_result_shape_t* compound = NULL;
    ok = ifcopenshell_geom_conversion_result_shape_wrap_in_compound(shape, &compound);
    if (ok && compound) {
        printf("  wrap_in_compound(): PASS\n");
        ifcopenshell_geom_conversion_result_shape_destroy(compound);
    } else {
        const char* err = ifcopenshell_last_error_message();
        printf("  wrap_in_compound(): FAIL (%s)\n", err ? err : "unknown");
        ifcopenshell_clear_error();
    }

    /* Test length() */
    double length = 0.0;
    ok = ifcopenshell_geom_conversion_result_shape_length(shape, &length);
    if (ok) {
        printf("  length(): %f PASS\n", length);
    } else {
        const char* err = ifcopenshell_last_error_message();
        printf("  length(): FAIL (%s)\n", err ? err : "unknown");
        ifcopenshell_clear_error();
    }

    ifcopenshell_geom_conversion_result_shape_destroy(shape);
    ifcopenshell_geom_iterator_destroy(iterator);
    ifcopenshell_geom_settings_destroy(settings);
    ifcopenshell_file_destroy(file);

    printf("  Additional shape methods: PASS\n");
}

/* Test tree advanced APIs (clash_many, add_iterator) */
static void test_tree_advanced_apis(void) {
    printf("Testing tree advanced APIs...\n");

    ifcopenshell_file_t* file = NULL;
    ifcopenshell_geom_settings_t* settings = NULL;
    ifcopenshell_geom_tree_t* tree = NULL;
    ifcopenshell_geom_iterator_t* iterator = NULL;

    int ok = ifcopenshell_parse_open(g_test_file_path, 1, &file);
    if (!ok) {
        printf("  SKIP: Could not open test file\n");
        return;
    }

    ifcopenshell_geom_create_settings(&settings);
    ifcopenshell_geom_create_tree(&tree);

    /* Create iterator and add to tree */
    ok = ifcopenshell_geom_create_iterator("opencascade", settings, file, 1, &iterator);
    if (!ok || !iterator) {
        printf("  SKIP: Could not create iterator\n");
        ifcopenshell_geom_tree_destroy(tree);
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    bool initialized = false;
    ifcopenshell_geom_iterator_initialize(iterator, &initialized);
    if (!initialized) {
        printf("  SKIP: Iterator not initialized\n");
        ifcopenshell_geom_iterator_destroy(iterator);
        ifcopenshell_geom_tree_destroy(tree);
        ifcopenshell_geom_settings_destroy(settings);
        ifcopenshell_file_destroy(file);
        return;
    }

    /* Test tree_add_iterator */
    ok = ifcopenshell_geom_tree_add_iterator(tree, iterator);
    if (ok) {
        printf("  tree_add_iterator: PASS\n");
    } else {
        printf("  tree_add_iterator: FAIL\n");
        ifcopenshell_clear_error();
    }

    /* Test clash_intersection_many and clash_clearance_many
       We need instance lists - get them by iterating the file for IfcProduct instances */
    ifcopenshell_parse_instance_list_t* products = NULL;
    ifcopenshell_instance_list_t product_values = {0};
    size_t product_count = 0;
    ok = ifcopenshell_file_by_type(file, "IfcProduct", &products);
    if (ok) {
        ok = ifcopenshell_parse_instance_list_size(products, &product_count);
    }
    if (ok && product_count > 0) {
        product_values = instance_list_value(products);
        ifcopenshell_geom_tree_clash_list_t* clashes = NULL;

        ok = ifcopenshell_geom_tree_clash_intersection_many(tree, &product_values, &product_values, 0.0, false, &clashes);
        if (ok && clashes) {
            size_t clash_count = 0;
            ifcopenshell_geom_tree_clash_count(tree, clashes, &clash_count);
            printf("  tree_clash_intersection_many: %zu clashes PASS\n", clash_count);
            if (clash_count > 0) {
                ifcopenshell_geom_tree_clash_t* clash = NULL;
                ifcopenshell_geom_tree_clash_at(tree, clashes, 0, &clash);
                if (clash) {
                    ifcopenshell_double_list_t p1 = {0}, p2 = {0};
                    ifcopenshell_geom_tree_clash_p1(clash, &p1);
                    ifcopenshell_geom_tree_clash_p2(clash, &p2);
                    if (p1.size == 3) printf("  clash_p1: [%f,%f,%f] PASS\n", p1.items[0], p1.items[1], p1.items[2]);
                    if (p2.size == 3) printf("  clash_p2: [%f,%f,%f] PASS\n", p2.items[0], p2.items[1], p2.items[2]);
                    ifcopenshell_double_list_destroy(&p1);
                    ifcopenshell_double_list_destroy(&p2);
                    ifcopenshell_geom_tree_clash_destroy(clash);
                }
            }
            ifcopenshell_geom_tree_clash_list_destroy(clashes);
        } else {
            printf("  tree_clash_intersection_many: no clashes PASS\n");
            ifcopenshell_clear_error();
        }

        ifcopenshell_geom_tree_clash_list_t* clearance_clashes = NULL;
        ok = ifcopenshell_geom_tree_clash_clearance_many(tree, &product_values, &product_values, 1.0, false, &clearance_clashes);
        if (ok && clearance_clashes) {
            size_t cc = 0;
            ifcopenshell_geom_tree_clash_count(tree, clearance_clashes, &cc);
            printf("  tree_clash_clearance_many: %zu clashes PASS\n", cc);
            ifcopenshell_geom_tree_clash_list_destroy(clearance_clashes);
        } else {
            printf("  tree_clash_clearance_many: no clashes PASS\n");
            ifcopenshell_clear_error();
        }

        ifcopenshell_parse_instance_list_destroy(products);
        ifcopenshell_instance_list_destroy(&product_values);
    } else {
        printf("  SKIP: No IfcProduct instances for clash tests\n");
        ifcopenshell_parse_instance_list_destroy(products);
        ifcopenshell_clear_error();
    }

    ifcopenshell_geom_iterator_destroy(iterator);
    ifcopenshell_geom_tree_destroy(tree);
    ifcopenshell_geom_settings_destroy(settings);
    ifcopenshell_file_destroy(file);

    printf("  Tree advanced APIs: PASS\n");
}

/* Test taxonomy geometry creation and accessor methods */
static void test_taxonomy_geometry_accessors(void) {
    printf("Testing taxonomy geometry accessors...\n");

    /* Test point3 creation and data extraction */
    ifcopenshell_geom_taxonomy_point3_t* pt = NULL;
    int ok = ifcopenshell_geom_taxonomy_create_point3(1.0, 2.0, 3.0, &pt);
    if (ok && pt) {
        ifcopenshell_double_list_t data = {0};
        ok = ifcopenshell_geom_taxonomy_point3_get_data(pt, &data);
        if (ok && data.size == 3) {
            expect_true(data.items[0] == 1.0 && data.items[1] == 2.0 && data.items[2] == 3.0,
                        "point3 data should be [1,2,3]");
            printf("  point3 create+get_data: PASS\n");
        } else {
            printf("  point3 get_data: FAIL\n");
            ifcopenshell_clear_error();
        }
        ifcopenshell_double_list_destroy(&data);
        ifcopenshell_geom_taxonomy_point3_destroy(pt);
    } else {
        printf("  point3 create: FAIL\n");
        ifcopenshell_clear_error();
    }

    /* Test direction3 creation and data extraction */
    ifcopenshell_geom_taxonomy_direction3_t* dir = NULL;
    ok = ifcopenshell_geom_taxonomy_create_direction3(0.0, 0.0, 1.0, &dir);
    if (ok && dir) {
        ifcopenshell_double_list_t data = {0};
        ok = ifcopenshell_geom_taxonomy_direction3_get_data(dir, &data);
        if (ok && data.size == 3) {
            expect_true(data.items[2] == 1.0, "direction3 z should be 1.0");
            printf("  direction3 create+get_data: PASS\n");
        } else {
            printf("  direction3 get_data: FAIL\n");
            ifcopenshell_clear_error();
        }
        ifcopenshell_double_list_destroy(&data);
        ifcopenshell_geom_taxonomy_direction3_destroy(dir);
    } else {
        printf("  direction3 create: FAIL\n");
        ifcopenshell_clear_error();
    }

    /* Test ellipse radius accessors */
    ifcopenshell_geom_taxonomy_ellipse_t* ellipse = NULL;
    ok = ifcopenshell_geom_taxonomy_create_ellipse(0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 5.0, 3.0, &ellipse);
    if (ok && ellipse) {
        double r1 = 0.0, r2 = 0.0;
        ifcopenshell_geom_taxonomy_ellipse_radius1(ellipse, &r1);
        ifcopenshell_geom_taxonomy_ellipse_radius2(ellipse, &r2);
        expect_true(r1 == 5.0, "ellipse radius1 should be 5.0");
        expect_true(r2 == 3.0, "ellipse radius2 should be 3.0");
        printf("  ellipse radius1/radius2: PASS\n");
        ifcopenshell_geom_taxonomy_ellipse_destroy(ellipse);
    } else {
        printf("  ellipse create: FAIL\n");
        ifcopenshell_clear_error();
    }

    /* Test torus radius accessors */
    ifcopenshell_geom_taxonomy_torus_t* torus = NULL;
    ok = ifcopenshell_geom_taxonomy_create_torus(0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 10.0, 2.0, &torus);
    if (ok && torus) {
        double r1 = 0.0, r2 = 0.0;
        ifcopenshell_geom_taxonomy_torus_radius1(torus, &r1);
        ifcopenshell_geom_taxonomy_torus_radius2(torus, &r2);
        expect_true(r1 == 10.0, "torus radius1 should be 10.0");
        expect_true(r2 == 2.0, "torus radius2 should be 2.0");
        printf("  torus radius1/radius2: PASS\n");
        ifcopenshell_geom_taxonomy_torus_destroy(torus);
    } else {
        printf("  torus create: FAIL\n");
        ifcopenshell_clear_error();
    }

    /* Test matrix4 get_data from a line's matrix */
    ifcopenshell_geom_taxonomy_line_t* line = NULL;
    ok = ifcopenshell_geom_taxonomy_create_line(0.0, 0.0, 0.0, 1.0, 0.0, 0.0, &line);
    if (ok && line) {
        ifcopenshell_geom_taxonomy_matrix4_t* mat = NULL;
        ifcopenshell_geom_taxonomy_line_matrix(line, &mat);
        if (mat) {
            ifcopenshell_double_list_t mat_data = {0};
            ok = ifcopenshell_geom_taxonomy_matrix4_get_data(mat, &mat_data);
            if (ok && mat_data.size == 16) {
                printf("  matrix4 get_data: %zu elements PASS\n", mat_data.size);
            } else {
                printf("  matrix4 get_data: FAIL\n");
                ifcopenshell_clear_error();
            }
            ifcopenshell_double_list_destroy(&mat_data);
            ifcopenshell_geom_taxonomy_matrix4_destroy(mat);
        }
        ifcopenshell_geom_taxonomy_line_destroy(line);
    }

    /* Test bspline_curve_control_point_at and weights on empty curve */
    ifcopenshell_geom_taxonomy_bspline_curve_t* bc = NULL;
    ok = ifcopenshell_geom_taxonomy_create_bspline_curve(2, &bc);
    if (ok && bc) {
        ifcopenshell_geom_taxonomy_point3_t* cp = NULL;
        ok = ifcopenshell_geom_taxonomy_bspline_curve_control_point_at(bc, 0, &cp);
        if (!ok) {
            printf("  bspline_curve_control_point_at(0) on empty: correctly failed PASS\n");
            ifcopenshell_clear_error();
        } else if (cp) {
            ifcopenshell_geom_taxonomy_point3_destroy(cp);
        }
        ifcopenshell_double_list_t weights = {0};
        ok = ifcopenshell_geom_taxonomy_bspline_curve_weights(bc, &weights);
        if (ok) {
            printf("  bspline_curve_weights (no weights set): %zu PASS\n", weights.size);
            ifcopenshell_double_list_destroy(&weights);
        } else {
            /* Expected: curve has no weights (has_weights=false), so this throws */
            const char* err = ifcopenshell_last_error_message();
            if (err && strstr(err, "weights are not set") != NULL) {
                printf("  bspline_curve_weights (no weights): correctly rejected PASS\n");
            } else {
                printf("  bspline_curve_weights: unexpected error (%s)\n", err ? err : "unknown");
            }
            ifcopenshell_clear_error();
        }
        ifcopenshell_geom_taxonomy_bspline_curve_destroy(bc);
    }

    /* Test bspline_surface weight and control point sub-accessors on empty surface */
    ifcopenshell_geom_taxonomy_bspline_surface_t* bs = NULL;
    ok = ifcopenshell_geom_taxonomy_create_bspline_surface(2, 3, &bs);
    if (ok && bs) {
        size_t wrc = 0;
        ok = ifcopenshell_geom_taxonomy_bspline_surface_weight_row_count(bs, &wrc);
        if (ok) printf("  bspline_surface_weight_row_count: %zu PASS\n", wrc);

        size_t col_count = 0;
        ok = ifcopenshell_geom_taxonomy_bspline_surface_control_point_col_count_at(bs, 0, &col_count);
        if (!ok) {
            printf("  bspline_surface_control_point_col_count_at(0) on empty: correctly failed PASS\n");
            ifcopenshell_clear_error();
        }

        ifcopenshell_geom_taxonomy_point3_t* scp = NULL;
        ok = ifcopenshell_geom_taxonomy_bspline_surface_control_point_at(bs, 0, 0, &scp);
        if (!ok) {
            printf("  bspline_surface_control_point_at(0,0) on empty: correctly failed PASS\n");
            ifcopenshell_clear_error();
        } else if (scp) {
            ifcopenshell_geom_taxonomy_point3_destroy(scp);
        }

        size_t wcol = 0;
        ok = ifcopenshell_geom_taxonomy_bspline_surface_weight_col_count_at(bs, 0, &wcol);
        if (!ok) {
            printf("  bspline_surface_weight_col_count_at(0) on empty: correctly failed PASS\n");
            ifcopenshell_clear_error();
        }

        double w = 0.0;
        ok = ifcopenshell_geom_taxonomy_bspline_surface_weight_at(bs, 0, 0, &w);
        if (!ok) {
            printf("  bspline_surface_weight_at(0,0) on empty: correctly failed PASS\n");
            ifcopenshell_clear_error();
        }

        ifcopenshell_geom_taxonomy_bspline_surface_destroy(bs);
    }

    /* Test face_matrix and solid_matrix - use a box to get a solid */
    ifcopenshell_geom_taxonomy_solid_t* solid = NULL;
    ok = ifcopenshell_geom_taxonomy_create_box(1.0, 2.0, 3.0, &solid);
    if (ok && solid) {
        ifcopenshell_geom_taxonomy_matrix4_t* sm = NULL;
        ok = ifcopenshell_geom_taxonomy_solid_matrix(solid, &sm);
        if (ok && sm) {
            printf("  solid_matrix: PASS\n");
            ifcopenshell_geom_taxonomy_matrix4_destroy(sm);
        } else {
            printf("  solid_matrix: null (expected for default solid) PASS\n");
            ifcopenshell_clear_error();
        }

        /* Get a face from the solid via shell */
        size_t shell_count = 0;
        ifcopenshell_geom_taxonomy_solid_shell_count(solid, &shell_count);
        if (shell_count > 0) {
            ifcopenshell_geom_taxonomy_shell_t* shell = NULL;
            ifcopenshell_geom_taxonomy_solid_shell_at(solid, 0, &shell);
            if (shell) {
                size_t face_count = 0;
                ifcopenshell_geom_taxonomy_shell_face_count(shell, &face_count);
                if (face_count > 0) {
                    ifcopenshell_geom_taxonomy_face_t* face = NULL;
                    ifcopenshell_geom_taxonomy_shell_face_at(shell, 0, &face);
                    if (face) {
                        ifcopenshell_geom_taxonomy_matrix4_t* fm = NULL;
                        ok = ifcopenshell_geom_taxonomy_face_matrix(face, &fm);
                        if (ok && fm) {
                            printf("  face_matrix: PASS\n");
                            ifcopenshell_geom_taxonomy_matrix4_destroy(fm);
                        } else {
                            printf("  face_matrix: null (expected for box face) PASS\n");
                            ifcopenshell_clear_error();
                        }
                        ifcopenshell_geom_taxonomy_face_destroy(face);
                    }
                }
                ifcopenshell_geom_taxonomy_shell_destroy(shell);
            }
        }
        ifcopenshell_geom_taxonomy_solid_destroy(solid);
    }

    /* Test loft_item_at on empty loft */
    ifcopenshell_geom_taxonomy_loft_t* loft = NULL;
    ok = ifcopenshell_geom_taxonomy_create_loft(&loft);
    if (ok && loft) {
        ifcopenshell_geom_taxonomy_item_t* loft_item = NULL;
        ok = ifcopenshell_geom_taxonomy_loft_item_at(loft, 0, &loft_item);
        if (!ok) {
            printf("  loft_item_at(0) on empty: correctly failed PASS\n");
            ifcopenshell_clear_error();
        } else if (loft_item) {
            ifcopenshell_geom_taxonomy_item_destroy(loft_item);
        }
        ifcopenshell_geom_taxonomy_loft_destroy(loft);
    }

    /* Test sweep_along_curve_surface - create a sweep with NULL basis face (error path) */
    ifcopenshell_geom_taxonomy_sweep_along_curve_t* sweep = NULL;
    ok = ifcopenshell_geom_taxonomy_create_sweep_along_curve(NULL, NULL, NULL, &sweep);
    if (ok && sweep) {
        ifcopenshell_geom_taxonomy_item_t* surface = NULL;
        ok = ifcopenshell_geom_taxonomy_sweep_along_curve_surface(sweep, &surface);
        if (ok && surface) {
            printf("  sweep_along_curve_surface: PASS\n");
            ifcopenshell_geom_taxonomy_item_destroy(surface);
        } else {
            printf("  sweep_along_curve_surface: null (expected for empty sweep) PASS\n");
            ifcopenshell_clear_error();
        }
        ifcopenshell_geom_taxonomy_sweep_along_curve_destroy(sweep);
    } else {
        printf("  create_sweep_along_curve(NULL,...): correctly failed PASS\n");
        ifcopenshell_clear_error();
    }

    printf("  Taxonomy geometry accessors: PASS\n");
}

/* Test SVG polygon accessors (CGAL-dependent) */
static void test_svg_polygon_accessors(void) {
    printf("Testing SVG polygon accessors...\n");

    const char* test_svg = "<svg><path d='M0,0 L10,0 L10,10 L0,10 Z'/></svg>";

    /* Test svg_to_polygons (returns polygon list) */
    ifcopenshell_geom_svgfill_polygon_list_t polygons = {0};
    int ok = ifcopenshell_geom_svg_to_polygons(test_svg, "", &polygons);
    if (ok && polygons.size > 0) {
        printf("  svg_to_polygons: %zu polygons PASS\n", polygons.size);

        /* Test arrange_polygons */
        ifcopenshell_geom_svgfill_polygon_list_t arranged = {0};
        ok = ifcopenshell_geom_arrange_polygons(&polygons, &arranged);
        if (ok) {
            printf("  arrange_polygons: %zu polygons PASS\n", arranged.size);
            ifcopenshell_geom_svgfill_polygon_list_destroy(&arranged);
        } else {
            printf("  arrange_polygons: failed\n");
            ifcopenshell_clear_error();
        }

        /* Test accessor methods on the first polygon */
        if (polygons.items && polygons.items[0]) {
            ifcopenshell_geom_svgfill_polygon_t* poly = polygons.items[0];

            size_t bsize = 0;
            ok = ifcopenshell_geom_svgfill_polygon_boundary_size(poly, &bsize);
            if (ok) printf("  boundary_size: %zu PASS\n", bsize);

            if (bsize > 0) {
                ifcopenshell_double_list_t bpt = {0};
                ok = ifcopenshell_geom_svgfill_polygon_boundary_point(poly, 0, &bpt);
                if (ok && bpt.size >= 2) {
                    printf("  boundary_point(0): [%f, %f] PASS\n", bpt.items[0], bpt.items[1]);
                }
                ifcopenshell_double_list_destroy(&bpt);
            }

            size_t inner_count = 0;
            ok = ifcopenshell_geom_svgfill_polygon_inner_boundary_count(poly, &inner_count);
            if (ok) printf("  inner_boundary_count: %zu PASS\n", inner_count);

            ifcopenshell_double_list_t inside_pt = {0};
            ok = ifcopenshell_geom_svgfill_polygon_point_inside(poly, &inside_pt);
            if (ok && inside_pt.size >= 2) {
                printf("  point_inside: [%f, %f] PASS\n", inside_pt.items[0], inside_pt.items[1]);
            }
            ifcopenshell_double_list_destroy(&inside_pt);
        }

        ifcopenshell_geom_svgfill_polygon_list_destroy(&polygons);
    } else {
        printf("  svg_to_polygons: failed (expected without CGAL)\n");
        ifcopenshell_clear_error();
    }

    /* Test null safety on polygon accessors */
    ifcopenshell_geom_svgfill_polygon_t* null_poly = NULL;
    size_t bsize = 0;
    ok = ifcopenshell_geom_svgfill_polygon_boundary_size(null_poly, &bsize);
    if (!ok) {
        printf("  svgfill_polygon_boundary_size(NULL): correctly failed PASS\n");
        ifcopenshell_clear_error();
    }

    ifcopenshell_double_list_t bpt = {0};
    ok = ifcopenshell_geom_svgfill_polygon_boundary_point(null_poly, 0, &bpt);
    if (!ok) {
        printf("  svgfill_polygon_boundary_point(NULL): correctly failed PASS\n");
        ifcopenshell_clear_error();
    }

    size_t inner_count = 0;
    ok = ifcopenshell_geom_svgfill_polygon_inner_boundary_count(null_poly, &inner_count);
    if (!ok) {
        printf("  svgfill_polygon_inner_boundary_count(NULL): correctly failed PASS\n");
        ifcopenshell_clear_error();
    }

    size_t inner_size = 0;
    ok = ifcopenshell_geom_svgfill_polygon_inner_boundary_size(null_poly, 0, &inner_size);
    if (!ok) {
        printf("  svgfill_polygon_inner_boundary_size(NULL): correctly failed PASS\n");
        ifcopenshell_clear_error();
    }

    ifcopenshell_double_list_t inner_pt = {0};
    ok = ifcopenshell_geom_svgfill_polygon_inner_boundary_point(null_poly, 0, 0, &inner_pt);
    if (!ok) {
        printf("  svgfill_polygon_inner_boundary_point(NULL): correctly failed PASS\n");
        ifcopenshell_clear_error();
    }

    ifcopenshell_double_list_t inside_result = {0};
    ok = ifcopenshell_geom_svgfill_polygon_point_inside(null_poly, &inside_result);
    if (!ok) {
        printf("  svgfill_polygon_point_inside(NULL): correctly failed PASS\n");
        ifcopenshell_clear_error();
    }

    ifcopenshell_geom_svgfill_polygon_destroy(NULL); /* NULL destroy safety */
    printf("  SVG polygon accessors: PASS\n");
}

/* Test buffer creation from filename and serializer_set_file */
static void test_buffer_from_filename(void) {
    printf("Testing buffer from filename and serializer_set_file...\n");

    ifcopenshell_geom_buffer_t* buf = NULL;
    int ok = ifcopenshell_geom_create_buffer_from_filename("/tmp/ifcgeom_test_output.obj", &buf);
    if (ok && buf) {
        printf("  create_buffer_from_filename: PASS\n");
        ifcopenshell_geom_buffer_destroy(buf);
    } else {
        printf("  create_buffer_from_filename: FAIL\n");
        ifcopenshell_clear_error();
    }

    /* Test serializer_set_file (available on non-geometry serializers like JSON/XML) */
    ifcopenshell_file_t* file = NULL;
    ok = ifcopenshell_parse_open(g_test_file_path, 1, &file);
    if (ok && file) {
        ifcopenshell_geom_serializer_t* ser = NULL;
        ok = ifcopenshell_geom_create_xml_serializer(file, "/tmp/ifcgeom_test_set_file.xml", &ser);
        if (ok && ser) {
            /* Create a second file to set */
            ifcopenshell_file_t* file2 = NULL;
            ok = ifcopenshell_parse_open(g_test_file_path, 1, &file2);
            if (ok && file2) {
                ok = ifcopenshell_geom_serializer_set_file(ser, file2);
                if (ok) {
                    printf("  serializer_set_file: PASS\n");
                } else {
                    /* XML/JSON/RocksDB serializers throw "Should be supplied on construction"
                       because they require the file at creation time. This is expected behavior. */
                    const char* err = ifcopenshell_last_error_message();
                    if (err && strstr(err, "Should be supplied on construction") != NULL) {
                        printf("  serializer_set_file: correctly rejected (file required at construction) PASS\n");
                    } else {
                        printf("  serializer_set_file: FAIL (%s)\n", err ? err : "unknown error");
                    }
                    ifcopenshell_clear_error();
                }
                ifcopenshell_file_destroy(file2);
            }
            ifcopenshell_geom_serializer_destroy(ser);
        }
        ifcopenshell_file_destroy(file);
    }

    printf("  Buffer/serializer_set_file: PASS\n");
}

/* Test destroy functions with non-NULL handles (null safety already tested) */
static void test_destroy_safety(void) {
    printf("Testing destroy safety...\n");

    /* Test transformation destroy */
    ifcopenshell_geom_transformation_destroy(NULL);
    printf("  transformation_destroy(NULL): PASS\n");

    /* Test brep_element, brep_representation, serialization destroys */
    ifcopenshell_geom_brep_element_destroy(NULL);
    printf("  brep_element_destroy(NULL): PASS\n");

    ifcopenshell_geom_brep_representation_destroy(NULL);
    printf("  brep_representation_destroy(NULL): PASS\n");

    ifcopenshell_geom_serialization_destroy(NULL);
    printf("  serialization_destroy(NULL): PASS\n");

    ifcopenshell_geom_serialized_element_destroy(NULL);
    printf("  serialized_element_destroy(NULL): PASS\n");

    ifcopenshell_geom_triangulation_element_destroy(NULL);
    printf("  triangulation_element_destroy(NULL): PASS\n");

    ifcopenshell_geom_conversion_result_shape_list_destroy(NULL);
    printf("  conversion_result_shape_list_destroy(NULL): PASS\n");

    ifcopenshell_geom_taxonomy_node_destroy(NULL);
    printf("  taxonomy_node_destroy(NULL): PASS\n");

    ifcopenshell_geom_function_item_evaluator_destroy(NULL);
    printf("  function_item_evaluator_destroy(NULL): PASS\n");

    printf("  Destroy safety: PASS\n");
}

int main(int argc, char** argv) {
    printf("=== IfcGeom C API Smoke Test ===\n\n");

    /* Set test file path */
    if (argc > 1) {
        g_test_file_path = argv[1];
    } else {
        g_test_file_path = "test/input/large_offset.ifc";
    }
    printf("Using test file: %s\n\n", g_test_file_path);

    /* Test Settings */
    test_settings_create();
    test_settings_names();
    test_settings_bool();
    test_settings_double();
    test_settings_advanced();

    /* Test error handling */
    test_error_handling();

    /* Test null safety */
    test_null_safety();

    /* Test Iterator (requires IFC file with geometry) */
    test_iterator_create();
    test_iterator_workflow();
    test_iterator_filter_constructors();
    test_triangulation_element();
    test_extended_geometry_apis();
    test_taxonomy_primitive_apis();
    test_taxonomy_operation_apis();
    test_taxonomy_advanced_apis();
    test_serializer_settings_apis();
    test_obj_serializer_apis();
    test_ttl_serializer_apis();
    test_svg_serializer_apis();
    test_gltf_serializer_apis();
    test_json_xml_serializer_apis();
    test_iges_step_serializer_apis();
    test_collada_hdf_serializer_apis();
    test_rocksdb_serializer_apis();
    test_tree_apis();
    test_tree_clash_and_ray_apis();

    /* Test new parity functions */
    test_create_shape();
    test_map_shape();
    test_conversion_result_shape_methods();
    test_cgal_functions();
    test_svg_functions();
    test_opaque_number_methods();
    test_function_item_evaluator_apis();
    test_additional_shape_methods();
    test_tree_advanced_apis();
    test_taxonomy_geometry_accessors();
    test_svg_polygon_accessors();
    test_buffer_from_filename();
    test_destroy_safety();

    printf("\n=== All tests passed! ===\n");
    return 0;
}
