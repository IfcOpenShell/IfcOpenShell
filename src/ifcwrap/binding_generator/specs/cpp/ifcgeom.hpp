// This file was generated with the assistance of an AI coding tool.
// SPDX-License-Identifier: LGPL-3.0-or-later

#ifndef IFCWRAP_BINDING_GENERATOR_IFCGEOM_SPEC_HPP
#define IFCWRAP_BINDING_GENERATOR_IFCGEOM_SPEC_HPP

#include "spec_macros.h"

#include "ifcparse/express.h"
#include "ifcparse/file.h"
#include "ifcparse/schema.h"

#include "ifc_geom_api.h"
#include "Iterator.h"
#include "Converter.h"
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

IFCAPI_HANDLE(iterator, IfcGeom::Iterator, delete)
IFCAPI_HANDLE(settings, ifcopenshell::geometry::Settings, delete)
IFCAPI_HANDLE(serializer_settings, ifcopenshell::geometry::SerializerSettings, delete)
IFCAPI_HANDLE(geometry_serializer, GeometrySerializer, delete)
IFCAPI_HANDLE(serializer, Serializer, delete)
IFCAPI_HANDLE(buffer, stream_or_filename, delete)
IFCAPI_HANDLE(tree, IfcGeom::tree, delete)
IFCAPI_HANDLE(tree_clash_list, std::vector<IfcGeom::clash>, delete)
IFCAPI_HANDLE(tree_clash, IfcGeom::clash, delete)
IFCAPI_HANDLE(tree_ray_intersection_list, std::vector<IfcGeom::ray_intersection_result>, delete)
IFCAPI_HANDLE(tree_ray_intersection, IfcGeom::ray_intersection_result, delete)
IFCAPI_HANDLE(transformation, IfcGeom::Transformation, delete)
IFCAPI_HANDLE(element, IfcGeom::Element, delete)
IFCAPI_HANDLE(brep_element, IfcGeom::BRepElement, delete)
IFCAPI_HANDLE(triangulation_element, IfcGeom::TriangulationElement, delete)
IFCAPI_HANDLE(serialized_element, IfcGeom::SerializedElement, delete)
IFCAPI_HANDLE(triangulation, IfcGeom::Representation::Triangulation, none)
IFCAPI_HANDLE(brep_representation, IfcGeom::Representation::BRep, none)
IFCAPI_HANDLE(serialization, IfcGeom::Representation::Serialization, none)
IFCAPI_HANDLE(conversion_result_shape, IfcGeom::ConversionResultShape, delete)
IFCAPI_HANDLE(opaque_number, IfcGeom::OpaqueNumber, delete)
IFCAPI_HANDLE(svgfill_polygon, svgfill::polygon_2, delete)
IFCAPI_HANDLE(function_item_evaluator, ifcopenshell::geometry::function_item_evaluator, delete)

IFCAPI_HANDLE(taxonomy_item, ifcopenshell::geometry::taxonomy::item, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_matrix4, ifcopenshell::geometry::taxonomy::matrix4, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_point3, ifcopenshell::geometry::taxonomy::point3, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_direction3, ifcopenshell::geometry::taxonomy::direction3, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_style, ifcopenshell::geometry::taxonomy::style, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_colour, ifcopenshell::geometry::taxonomy::colour, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_line, ifcopenshell::geometry::taxonomy::line, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_circle, ifcopenshell::geometry::taxonomy::circle, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_ellipse, ifcopenshell::geometry::taxonomy::ellipse, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_bspline_curve, ifcopenshell::geometry::taxonomy::bspline_curve, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_offset_curve, ifcopenshell::geometry::taxonomy::offset_curve, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_edge, ifcopenshell::geometry::taxonomy::edge, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_loop, ifcopenshell::geometry::taxonomy::loop, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_face, ifcopenshell::geometry::taxonomy::face, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_shell, ifcopenshell::geometry::taxonomy::shell, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_solid, ifcopenshell::geometry::taxonomy::solid, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_plane, ifcopenshell::geometry::taxonomy::plane, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_cylinder, ifcopenshell::geometry::taxonomy::cylinder, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_sphere, ifcopenshell::geometry::taxonomy::sphere, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_torus, ifcopenshell::geometry::taxonomy::torus, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_bspline_surface, ifcopenshell::geometry::taxonomy::bspline_surface, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_collection, ifcopenshell::geometry::taxonomy::collection, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_loft, ifcopenshell::geometry::taxonomy::loft, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_extrusion, ifcopenshell::geometry::taxonomy::extrusion, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_revolve, ifcopenshell::geometry::taxonomy::revolve, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_sweep_along_curve, ifcopenshell::geometry::taxonomy::sweep_along_curve, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_node, ifcopenshell::geometry::taxonomy::node, shared_ptr, shared_ptr)
IFCAPI_HANDLE(taxonomy_boolean_result, ifcopenshell::geometry::taxonomy::boolean_result, shared_ptr, shared_ptr)

namespace ifcgeom::bindings {

inline std::vector<express::Base> to_base_vector(const std::vector<express::Entity>& entities) {
    std::vector<express::Base> result;
    result.reserve(entities.size());
    for (const auto& entity : entities) {
        result.emplace_back(entity);
    }
    return result;
}

inline std::unique_ptr<IfcGeom::Iterator> create_iterator(
    const std::string& geometry_library_cpp,
    ifcopenshell::geometry::Settings* settings_cpp,
    ifcopenshell::file* file_cpp,
    int num_threads
) {
    auto* settings_ptr = settings_cpp;
    auto kernel = ifcopenshell::geometry::kernels::construct(file_cpp, geometry_library_cpp, *settings_ptr);
    return std::make_unique<IfcGeom::Iterator>(
        std::move(kernel), *settings_ptr, file_cpp, num_threads);
}

inline std::unique_ptr<IfcGeom::Iterator> create_iterator_with_include_exclude(
    const std::string& geometry_library_cpp,
    ifcopenshell::geometry::Settings* settings_cpp,
    ifcopenshell::file* file_cpp,
    const std::vector<std::string>& elems_cpp,
    bool include,
    int num_threads
) {
    auto* settings_ptr = settings_cpp;
    auto kernel = ifcopenshell::geometry::kernels::construct(file_cpp, geometry_library_cpp, *settings_ptr);
    std::set<std::string> elems_set(elems_cpp.begin(), elems_cpp.end());
    IfcGeom::entity_filter ef{include, false, elems_set};
    return std::make_unique<IfcGeom::Iterator>(
        std::move(kernel), *settings_ptr, file_cpp,
        std::vector<ifcopenshell::geometry::filter_t>{ef}, num_threads);
}

inline std::unique_ptr<IfcGeom::Iterator> create_iterator_with_include_exclude_globalid(
    const std::string& geometry_library_cpp,
    ifcopenshell::geometry::Settings* settings_cpp,
    ifcopenshell::file* file_cpp,
    const std::vector<std::string>& elems_cpp,
    bool include,
    int num_threads
) {
    auto* settings_ptr = settings_cpp;
    auto kernel = ifcopenshell::geometry::kernels::construct(file_cpp, geometry_library_cpp, *settings_ptr);
    std::set<std::string> elems_set(elems_cpp.begin(), elems_cpp.end());
    IfcGeom::attribute_filter af;
    af.attribute_name = "GlobalId";
    af.populate(elems_set);
    af.include = include;
    return std::make_unique<IfcGeom::Iterator>(
        std::move(kernel), *settings_ptr, file_cpp,
        std::vector<ifcopenshell::geometry::filter_t>{af}, num_threads);
}

inline std::unique_ptr<IfcGeom::Iterator> create_iterator_with_include_exclude_id(
    const std::string& geometry_library_cpp,
    ifcopenshell::geometry::Settings* settings_cpp,
    ifcopenshell::file* file_cpp,
    const std::vector<int>& elems_cpp,
    bool include,
    int num_threads
) {
    auto* settings_ptr = settings_cpp;
    auto kernel = ifcopenshell::geometry::kernels::construct(file_cpp, geometry_library_cpp, *settings_ptr);
    std::set<int> elems_set(elems_cpp.begin(), elems_cpp.end());
    IfcGeom::instance_id_filter af(include, false, elems_set);
    return std::make_unique<IfcGeom::Iterator>(
        std::move(kernel), *settings_ptr, file_cpp,
        std::vector<ifcopenshell::geometry::filter_t>{af}, num_threads);
}

inline ifcopenshell::geometry::taxonomy::direction3::ptr taxonomy_create_direction3(
    double x,
    double y,
    double z
) {
    Eigen::Vector3d direction(x, y, z);
    if (direction.squaredNorm() <= 1.e-12) {
        throw std::runtime_error("Direction vector must be non-zero");
    }
    return ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::direction3>(direction);
}

inline ifcopenshell::geometry::taxonomy::collection::ptr taxonomy_create_collection() {
    return ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::collection>();
}

inline ifcopenshell::geometry::taxonomy::loft::ptr taxonomy_create_loft() {
    return ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::loft>();
}

inline ifcopenshell::geometry::taxonomy::node::ptr taxonomy_create_node() {
    return ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::node>();
}

inline ifcopenshell::geometry::taxonomy::point3::ptr taxonomy_create_point3(double x, double y, double z) {
    return ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::point3>(x, y, z);
}

inline ifcopenshell::geometry::taxonomy::bspline_curve::ptr taxonomy_create_bspline_curve(int degree) {
    if (degree < 1) {
        throw std::runtime_error("B-spline curve degree must be >= 1");
    }
    auto value = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::bspline_curve>();
    value->degree = degree;
    return value;
}

inline ifcopenshell::geometry::taxonomy::bspline_surface::ptr taxonomy_create_bspline_surface(
    int degree_u,
    int degree_v
) {
    if (degree_u < 1 || degree_v < 1) {
        throw std::runtime_error("B-spline surface degrees must be >= 1");
    }
    auto value = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::bspline_surface>();
    value->degree = {degree_u, degree_v};
    return value;
}

inline ifcopenshell::geometry::taxonomy::boolean_result::ptr taxonomy_create_boolean_result(int operation) {
    if (operation < 0 || operation > 2) {
        throw std::runtime_error("Boolean operation must be 0 (UNION), 1 (SUBTRACTION), or 2 (INTERSECTION)");
    }
    auto value = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::boolean_result>();
    value->operation = static_cast<ifcopenshell::geometry::taxonomy::boolean_result::operation_t>(operation);
    return value;
}

inline ifcopenshell::geometry::taxonomy::offset_curve::ptr taxonomy_create_offset_curve(
    const ifcopenshell::geometry::taxonomy::item::ptr& basis,
    const ifcopenshell::geometry::taxonomy::direction3::ptr& reference,
    double offset
) {
    auto value = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::offset_curve>();
    value->basis = basis;
    value->reference = reference;
    value->offset = offset;
    return value;
}

inline ifcopenshell::geometry::taxonomy::line::ptr taxonomy_create_line(
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
    auto value = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::line>();
    value->matrix = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>(origin, direction);
    return value;
}

inline ifcopenshell::geometry::taxonomy::circle::ptr taxonomy_create_circle(
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
    auto value = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::circle>();
    value->matrix = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>(origin, direction);
    value->radius = radius;
    return value;
}

inline ifcopenshell::geometry::taxonomy::ellipse::ptr taxonomy_create_ellipse(
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
    auto value = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::ellipse>();
    value->matrix = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>(origin, direction);
    value->radius = radius1;
    value->radius2 = radius2;
    return value;
}

inline ifcopenshell::geometry::taxonomy::plane::ptr taxonomy_create_plane(
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
    auto value = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::plane>();
    value->matrix = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>(origin, direction);
    return value;
}

inline ifcopenshell::geometry::taxonomy::cylinder::ptr taxonomy_create_cylinder(
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
    auto value = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::cylinder>();
    value->matrix = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>(origin, direction);
    value->radius = radius;
    return value;
}

inline ifcopenshell::geometry::taxonomy::sphere::ptr taxonomy_create_sphere(
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
    auto value = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::sphere>();
    value->matrix = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>(origin, direction);
    value->radius = radius;
    return value;
}

inline ifcopenshell::geometry::taxonomy::torus::ptr taxonomy_create_torus(
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
    auto value = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::torus>();
    value->matrix = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>(origin, direction);
    value->radius1 = radius1;
    value->radius2 = radius2;
    return value;
}

inline ifcopenshell::geometry::taxonomy::solid::ptr taxonomy_create_box(
    double dx,
    double dy,
    double dz
) {
    if (dx <= 0. || dy <= 0. || dz <= 0.) {
        throw std::runtime_error("Box dimensions must be > 0");
    }
    return ifcopenshell::geometry::create_box(dx, dy, dz);
}

inline ifcopenshell::geometry::taxonomy::extrusion::ptr taxonomy_create_extrusion(
    const ifcopenshell::geometry::taxonomy::item::ptr& basis_cpp,
    const ifcopenshell::geometry::taxonomy::direction3::ptr& direction_cpp,
    double depth
) {
    auto basis_value = ifcopenshell::geometry::taxonomy::dcast<ifcopenshell::geometry::taxonomy::item>(basis_cpp);
    if (!basis_value) {
        throw std::runtime_error("Basis item is invalid");
    }
    if (depth <= 0.) {
        throw std::runtime_error("Extrusion depth must be > 0");
    }
    auto value = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::extrusion>(
        ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>(),
        basis_value,
        direction_cpp,
        depth
    );
    return value;
}

inline ifcopenshell::geometry::taxonomy::revolve::ptr taxonomy_create_revolve(
    const ifcopenshell::geometry::taxonomy::item::ptr& basis_cpp,
    const ifcopenshell::geometry::taxonomy::point3::ptr& axis_origin_cpp,
    const ifcopenshell::geometry::taxonomy::direction3::ptr& direction_cpp,
    double angle
) {
    auto basis_value = ifcopenshell::geometry::taxonomy::dcast<ifcopenshell::geometry::taxonomy::item>(basis_cpp);
    if (!basis_value) {
        throw std::runtime_error("Basis item is invalid");
    }
    auto value = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::revolve>(
        ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>(),
        basis_value,
        axis_origin_cpp,
        direction_cpp,
        std::optional<double>(angle)
    );
    return value;
}

inline ifcopenshell::geometry::taxonomy::sweep_along_curve::ptr taxonomy_create_sweep_along_curve(
    const ifcopenshell::geometry::taxonomy::face::ptr& basis_face_cpp,
    const ifcopenshell::geometry::taxonomy::item::ptr& directrix_cpp,
    const ifcopenshell::geometry::taxonomy::direction3::ptr& reference_direction_cpp
) {
    auto directrix_value = ifcopenshell::geometry::taxonomy::dcast<ifcopenshell::geometry::taxonomy::item>(directrix_cpp);
    if (!directrix_value) {
        throw std::runtime_error("Directrix item is invalid");
    }
    auto value = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::sweep_along_curve>(
        ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>(),
        basis_face_cpp,
        directrix_value,
        reference_direction_cpp
    );
    return value;
}

inline std::unique_ptr<IfcGeom::Element> create_shape(
    ifcopenshell::geometry::Settings* settings_cpp,
    express::Base* instance_cpp,
    std::optional<express::Base> representation,
    std::optional<std::string> geometry_library
) {
    ifcopenshell::file* file = instance_cpp->file();
    if (!file) {
        throw std::runtime_error("Instance has no associated file");
    }
    std::string geom_lib = geometry_library.value_or("opencascade");
    ifcopenshell::geometry::Converter kernel(
        ifcopenshell::geometry::kernels::construct(file, geom_lib, *settings_cpp),
        file, *settings_cpp);

    auto entity = instance_cpp->as<express::Entity>();
    if (!entity) {
        throw std::runtime_error("Instance is not an entity");
    }

    if (entity.declaration().is("IfcProduct")) {
        express::Base ifc_representation = representation.value_or(express::Base());
        if (!ifc_representation) {
            auto prod_rep_attr = entity.get("Representation");
            if (prod_rep_attr.isNull()) {
                throw ifcopenshell::exception("Representation is NULL");
            }
            auto prod_rep = static_cast<express::Base>(prod_rep_attr);
            auto prod_rep_entity = prod_rep.as<express::Entity>();
            auto reps_attr = prod_rep_entity.get("Representations");
            auto reps = static_cast<std::vector<express::Base>>(reps_attr);
            if (reps.empty()) {
                throw ifcopenshell::exception("No suitable IfcRepresentation found");
            }

            bool is_curves = settings_cpp->get<ifcopenshell::geometry::settings::OutputDimensionality>().get()
                == ifcopenshell::geometry::settings::CURVES;

            for (auto it = reps.begin(); it != reps.end(); ++it) {
                auto rep_entity = it->as<express::Entity>();
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
                    auto rep_entity = it->as<express::Entity>();
                    if (!rep_entity) continue;
                    auto ctx_attr = rep_entity.get("ContextOfItems");
                    if (ctx_attr.isNull()) continue;
                    auto ctx = static_cast<express::Base>(ctx_attr).as<express::Entity>();
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

        auto rep_entity = ifc_representation.as<express::Entity>();
        std::unique_ptr<IfcGeom::BRepElement> brep(
            kernel.create_brep_for_representation_and_product(rep_entity, entity));
        if (!brep) {
            throw ifcopenshell::exception("Failed to process shape");
        }

        auto output_type = settings_cpp->get<ifcopenshell::geometry::settings::IteratorOutput>().get();
        if (output_type == ifcopenshell::geometry::settings::SERIALIZED) {
            return std::make_unique<IfcGeom::SerializedElement>(*brep);
        }
        if (output_type == ifcopenshell::geometry::settings::TRIANGULATED) {
            return std::make_unique<IfcGeom::TriangulationElement>(*brep);
        }
        return brep;
    } else if (
        entity.declaration().is("IfcRepresentationItem") ||
        entity.declaration().is("IfcRepresentation") ||
        entity.declaration().is("IfcProfileDef")
    ) {
        IfcGeom::ConversionResults shapes;
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
        auto brep_rep = boost::shared_ptr<IfcGeom::Representation::BRep>(
            new IfcGeom::Representation::BRep(
                kernel.settings(), entity.declaration().name(), std::to_string(entity.id()), shapes
            )
        );

        auto output_type = settings_cpp->get<ifcopenshell::geometry::settings::IteratorOutput>().get();
        auto identity = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>();
        express::Entity null_product;
        auto brep_elem = std::make_unique<IfcGeom::BRepElement>(
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
        if (output_type == ifcopenshell::geometry::settings::SERIALIZED) {
            return std::make_unique<IfcGeom::SerializedElement>(*brep_elem);
        }
        if (output_type == ifcopenshell::geometry::settings::TRIANGULATED) {
            return std::make_unique<IfcGeom::TriangulationElement>(*brep_elem);
        }
        return brep_elem;
    }

    throw ifcopenshell::exception("Unsupported instance type for create_shape. Use map_shape for placements.");
}

inline ifcopenshell::geometry::taxonomy::item::ptr map_shape(
    ifcopenshell::geometry::Settings* settings_cpp,
    express::Base* instance_cpp
) {
    if (instance_cpp->file() == nullptr) {
        throw std::runtime_error("Unable to map instance without file");
    }
    std::unique_ptr<ifcopenshell::geometry::abstract_mapping> mapping(
        ifcopenshell::geometry::impl::mapping_implementations().construct(instance_cpp->file(), *settings_cpp)
    );
    return mapping->map(*instance_cpp);
}

inline std::unique_ptr<IfcGeom::OpaqueNumber> create_epeck_from_int(int value) {
    return std::make_unique<IfcGeom::NumberNativeDouble>(value);
}

inline std::unique_ptr<IfcGeom::OpaqueNumber> create_epeck_from_double(double value) {
    return std::make_unique<IfcGeom::NumberNativeDouble>(value);
}

inline std::unique_ptr<IfcGeom::OpaqueNumber> create_epeck_from_string(const std::string& value_cpp) {
    return std::make_unique<IfcGeom::NumberNativeDouble>(std::stod(value_cpp));
}

inline std::unique_ptr<IfcGeom::OpaqueNumber> add(
    IfcGeom::OpaqueNumber* self,
    IfcGeom::OpaqueNumber* other
) {
    return std::unique_ptr<IfcGeom::OpaqueNumber>((*self) + other);
}

inline std::unique_ptr<IfcGeom::OpaqueNumber> subtract(
    IfcGeom::OpaqueNumber* self,
    IfcGeom::OpaqueNumber* other
) {
    return std::unique_ptr<IfcGeom::OpaqueNumber>((*self) - other);
}

inline std::unique_ptr<IfcGeom::OpaqueNumber> multiply(
    IfcGeom::OpaqueNumber* self,
    IfcGeom::OpaqueNumber* other
) {
    return std::unique_ptr<IfcGeom::OpaqueNumber>((*self) * other);
}

inline std::unique_ptr<IfcGeom::OpaqueNumber> divide(
    IfcGeom::OpaqueNumber* self,
    IfcGeom::OpaqueNumber* other
) {
    return std::unique_ptr<IfcGeom::OpaqueNumber>((*self) / other);
}

inline std::unique_ptr<IfcGeom::OpaqueNumber> negate(IfcGeom::OpaqueNumber* self) {
    return std::unique_ptr<IfcGeom::OpaqueNumber>(-(*self));
}

inline bool equals(IfcGeom::OpaqueNumber* self, IfcGeom::OpaqueNumber* other) {
    return (*self) == other;
}

inline bool less_than(IfcGeom::OpaqueNumber* self, IfcGeom::OpaqueNumber* other) {
    return (*self) < other;
}

inline std::unique_ptr<IfcGeom::OpaqueNumber> clone(IfcGeom::OpaqueNumber* self) {
    return std::unique_ptr<IfcGeom::OpaqueNumber>(self->clone());
}

inline std::unique_ptr<IfcGeom::ConversionResultShape> solid(
    IfcGeom::ConversionResultShape* self
) {
    return std::unique_ptr<IfcGeom::ConversionResultShape>(self->solid());
}

inline std::unique_ptr<IfcGeom::ConversionResultShape> solid_mt(
    IfcGeom::ConversionResultShape* self
) {
    return std::unique_ptr<IfcGeom::ConversionResultShape>(self->solid());
}

inline std::unique_ptr<IfcGeom::ConversionResultShape> add(
    IfcGeom::ConversionResultShape* self,
    IfcGeom::ConversionResultShape* arg_0
) {
    return std::unique_ptr<IfcGeom::ConversionResultShape>(self->add(arg_0));
}

inline std::unique_ptr<IfcGeom::ConversionResultShape> subtract(
    IfcGeom::ConversionResultShape* self,
    IfcGeom::ConversionResultShape* arg_0
) {
    return std::unique_ptr<IfcGeom::ConversionResultShape>(self->subtract(arg_0));
}

inline std::unique_ptr<IfcGeom::ConversionResultShape> intersect(
    IfcGeom::ConversionResultShape* self,
    IfcGeom::ConversionResultShape* arg_0
) {
    return std::unique_ptr<IfcGeom::ConversionResultShape>(self->intersect(arg_0));
}

inline std::unique_ptr<IfcGeom::ConversionResultShape> concat(
    IfcGeom::ConversionResultShape* self,
    IfcGeom::ConversionResultShape* arg_0
) {
    return std::unique_ptr<IfcGeom::ConversionResultShape>(self->concat(arg_0));
}

inline std::unique_ptr<IfcGeom::ConversionResultShape> halfspaces(
    IfcGeom::ConversionResultShape* self
) {
    return std::unique_ptr<IfcGeom::ConversionResultShape>(self->halfspaces());
}

inline std::unique_ptr<IfcGeom::ConversionResultShape> box(
    IfcGeom::ConversionResultShape* self
) {
    return std::unique_ptr<IfcGeom::ConversionResultShape>(self->box());
}

inline std::unique_ptr<IfcGeom::ConversionResultShape> wrap_in_compound(
    IfcGeom::ConversionResultShape* self
) {
    return std::unique_ptr<IfcGeom::ConversionResultShape>(self->wrap_in_compound());
}

inline std::unique_ptr<IfcGeom::ConversionResultShape> moved(
    IfcGeom::ConversionResultShape* self,
    ifcopenshell::geometry::taxonomy::matrix4::ptr arg_0
) {
    return std::unique_ptr<IfcGeom::ConversionResultShape>(self->moved(std::move(arg_0)));
}

namespace detail {
    inline std::vector<std::unique_ptr<IfcGeom::ConversionResultShape>> adopt_shapes(
        std::vector<IfcGeom::ConversionResultShape*> shapes
    ) {
        struct cleanup_guard {
            std::vector<IfcGeom::ConversionResultShape*>& shapes;
            ~cleanup_guard() {
                for (auto* shape : shapes) {
                    delete shape;
                }
            }
        } guard{shapes};
        std::vector<std::unique_ptr<IfcGeom::ConversionResultShape>> result;
        result.reserve(shapes.size());
        for (auto*& shape : shapes) {
            result.emplace_back(shape);
            shape = nullptr;
        }
        return result;
    }
}

inline std::vector<std::unique_ptr<IfcGeom::ConversionResultShape>> vertices(
    IfcGeom::ConversionResultShape* self
) {
    return detail::adopt_shapes(self->vertices());
}

inline std::vector<std::unique_ptr<IfcGeom::ConversionResultShape>> edges(
    IfcGeom::ConversionResultShape* self
) {
    return detail::adopt_shapes(self->edges());
}

inline std::vector<std::unique_ptr<IfcGeom::ConversionResultShape>> facets(
    IfcGeom::ConversionResultShape* self
) {
    return detail::adopt_shapes(self->facets());
}

inline std::unique_ptr<IfcGeom::ConversionResultShape> nary_union(
    const std::vector<const IfcGeom::ConversionResultShape*>& shapes_cpp
) {
    std::unique_ptr<IfcGeom::ConversionResultShape> result;
    std::string backend_id;
    auto identity = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>();
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
            auto* next = result->add(const_cast<IfcGeom::ConversionResultShape*>(shape));
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
#ifdef IFOPSH_WITH_CGAL
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
    throw std::runtime_error("svg_to_line_segments requires IFOPSH_WITH_CGAL");
#endif
}

inline std::vector<std::unique_ptr<svgfill::polygon_2>> svg_to_polygons(
    const std::string& svg_data_cpp,
    std::optional<std::string> class_name
) {
#ifdef IFOPSH_WITH_CGAL
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
    throw std::runtime_error("svg_to_polygons requires IFOPSH_WITH_CGAL");
#endif
}

inline std::vector<std::unique_ptr<svgfill::polygon_2>> arrange_polygons(
    const std::vector<const svgfill::polygon_2*>& polygons_cpp
) {
#ifdef IFOPSH_WITH_CGAL
    std::vector<svgfill::polygon_2> input;
    for (auto* p : polygons_cpp) {
        input.push_back(*p);
    }
    std::vector<svgfill::polygon_2> arranged;
    if (!svgfill::arrange_polygons(svgfill::arrange_polygon_settings(), input, arranged)) {
        throw std::runtime_error("Failed to arrange polygons");
    }
    std::vector<std::unique_ptr<svgfill::polygon_2>> result;
    for (auto& p : arranged) {
        result.push_back(std::make_unique<svgfill::polygon_2>(p));
    }
    return result;
#else
    (void)polygons_cpp;
    throw std::runtime_error("arrange_polygons requires IFOPSH_WITH_CGAL");
#endif
}

inline std::vector<std::unique_ptr<svgfill::polygon_2>> line_segments_to_polygons(
    int solver,
    double eps,
    const std::string& segments_json_cpp
) {
#ifdef IFOPSH_WITH_CGAL
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
    throw std::runtime_error("line_segments_to_polygons requires IFOPSH_WITH_CGAL");
#endif
}

inline ifcopenshell::geometry::taxonomy::item::ptr convert_loop_to_function_item(
    const ifcopenshell::geometry::taxonomy::item::ptr& loop_item_cpp
) {
    auto loop = ifcopenshell::geometry::taxonomy::dcast<ifcopenshell::geometry::taxonomy::loop>(loop_item_cpp);
    if (!loop) {
        throw std::runtime_error("Input is not a taxonomy loop");
    }
    auto result = ifcopenshell::geometry::convert_loop_to_function_item(loop);
    if (!result) {
        throw std::runtime_error("Failed to convert loop to function_item");
    }
    return result;
}

inline std::unique_ptr<ifcopenshell::geometry::function_item_evaluator> create_function_item_evaluator(
    ifcopenshell::geometry::Settings* settings_cpp,
    const ifcopenshell::geometry::taxonomy::item::ptr& fn_item_cpp
) {
    auto fn = ifcopenshell::geometry::taxonomy::dcast<ifcopenshell::geometry::taxonomy::function_item>(fn_item_cpp);
    if (!fn) {
        throw std::runtime_error("Input is not a taxonomy function_item");
    }
    return std::make_unique<ifcopenshell::geometry::function_item_evaluator>(*settings_cpp, fn);
}

inline double taxonomy_function_item_start(const ifcopenshell::geometry::taxonomy::item::ptr& item_cpp) {
    auto fn = ifcopenshell::geometry::taxonomy::dcast<ifcopenshell::geometry::taxonomy::function_item>(item_cpp);
    if (!fn) {
        throw std::runtime_error("Input is not a taxonomy function_item");
    }
    return fn->start();
}

inline double taxonomy_function_item_end(const ifcopenshell::geometry::taxonomy::item::ptr& item_cpp) {
    auto fn = ifcopenshell::geometry::taxonomy::dcast<ifcopenshell::geometry::taxonomy::function_item>(item_cpp);
    if (!fn) {
        throw std::runtime_error("Input is not a taxonomy function_item");
    }
    return fn->end();
}

inline std::vector<express::Base> select_element(
    IfcGeom::tree* self,
    express::Base* instance,
    bool completely_within,
    double extend
) {
    auto entity = instance->as<express::Entity>();
    if (!entity) {
        throw std::runtime_error("Instance should be an IfcProduct entity");
    }
    return to_base_vector(self->select(entity, completely_within, extend));
}

inline std::vector<express::Base> select_point(
    IfcGeom::tree* self,
    double x,
    double y,
    double z,
    double extend
) {
    return to_base_vector(self->select(IfcGeom::tree_point{x, y, z}, extend));
}

inline std::vector<express::Base> select_brep_element(
    IfcGeom::tree* self,
    const IfcGeom::BRepElement* element,
    bool completely_within,
    double extend
) {
    return to_base_vector(self->select(element, completely_within, extend));
}

inline std::vector<express::Base> select_box_point(
    IfcGeom::tree* self,
    double x,
    double y,
    double z,
    double extend
) {
    (void)extend;
    return to_base_vector(self->select_box(IfcGeom::tree_point{x, y, z}));
}

inline std::vector<express::Base> select_box_element(
    IfcGeom::tree* self,
    express::Base* instance,
    bool completely_within,
    double extend
) {
    auto entity = instance->as<express::Entity>();
    if (!entity) {
        throw std::runtime_error("Instance should be an IfcProduct entity");
    }
    return to_base_vector(self->select_box(entity, completely_within, extend));
}

inline std::vector<express::Base> select_box_bounds(
    IfcGeom::tree* self,
    double xmin,
    double ymin,
    double zmin,
    double xmax,
    double ymax,
    double zmax,
    bool completely_within
) {
    return to_base_vector(
        self->select_box(IfcGeom::tree_box{{IfcGeom::tree_point{xmin, ymin, zmin}, IfcGeom::tree_point{xmax, ymax, zmax}}}, completely_within));
}

inline std::vector<IfcGeom::ray_intersection_result> select_ray(
    IfcGeom::tree* self,
    double origin_x,
    double origin_y,
    double origin_z,
    double dir_x,
    double dir_y,
    double dir_z,
    double length
) {
    return self->select_ray(
        IfcGeom::tree_point{origin_x, origin_y, origin_z},
        IfcGeom::tree_point{dir_x, dir_y, dir_z},
        length);
}

inline express::Base instance(IfcGeom::ray_intersection_result* self) {
    return self->instance;
}

inline IfcGeom::TriangulationElement* get_as_triangulation_element(IfcGeom::Iterator* self) {
    IfcGeom::Element* elem = self->get();
    auto* tri = dynamic_cast<IfcGeom::TriangulationElement*>(elem);
    if (!tri) {
        throw std::runtime_error("Current element is not a TriangulationElement");
    }
    return tri;
}

inline IfcGeom::BRepElement* get_as_brep_element(IfcGeom::Iterator* self) {
    IfcGeom::Element* elem = self->get();
    auto* brep = dynamic_cast<IfcGeom::BRepElement*>(elem);
    if (!brep) {
        throw std::runtime_error("Current element is not a BRepElement");
    }
    return brep;
}

inline IfcGeom::SerializedElement* get_as_serialized_element(IfcGeom::Iterator* self) {
    IfcGeom::Element* elem = self->get();
    auto* serialized = dynamic_cast<IfcGeom::SerializedElement*>(elem);
    if (!serialized) {
        throw std::runtime_error("Current element is not a SerializedElement");
    }
    return serialized;
}

inline bool next(IfcGeom::Iterator* self) {
    return static_cast<bool>(self->next());
}

inline const double* transformation_buffer(const IfcGeom::Element* self) {
    return self->transformation().data()->ccomponents().data();
}

inline std::size_t transformation_buffer_size(const IfcGeom::Element* self) {
    return 16;
}

inline double calc_volume(const IfcGeom::BRepElement* self) {
    double v;
    if (self->geometry().calculate_volume(v)) {
        return v;
    }
    return std::numeric_limits<double>::quiet_NaN();
}

inline double calc_surface_area(const IfcGeom::BRepElement* self) {
    double v;
    if (self->geometry().calculate_surface_area(v)) {
        return v;
    }
    return std::numeric_limits<double>::quiet_NaN();
}

inline std::unique_ptr<IfcGeom::ConversionResultShape> as_compound(
    const IfcGeom::Representation::BRep* self,
    bool force_meters
) {
    return std::unique_ptr<IfcGeom::ConversionResultShape>(
        self->as_compound(force_meters));
}

inline std::string serialize(IfcGeom::ConversionResultShape* self) {
    ifcopenshell::geometry::taxonomy::matrix4 identity;
    std::string result;
    self->Serialize(identity, result);
    return result;
}

inline std::string serialize_obj(IfcGeom::ConversionResultShape* self) {
    std::ostringstream result;
    ifcopenshell::geometry::Settings settings;
    std::unique_ptr<IfcGeom::Representation::Triangulation> triangulation(self->Triangulate(settings));

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

inline void convex_tag(IfcGeom::ConversionResultShape* self, bool value) {
    (void)self;
    (void)value;
    throw std::runtime_error("convex_tag is not available through the generic conversion result interface");
}

inline double area(IfcGeom::ConversionResultShape* self) {
    auto* result = self->area();
    double val = result->to_double();
    delete result;
    return val;
}

inline double volume(IfcGeom::ConversionResultShape* self) {
    auto* result = self->volume();
    double val = result->to_double();
    delete result;
    return val;
}

inline double length(IfcGeom::ConversionResultShape* self) {
    auto* result = self->length();
    double val = result->to_double();
    delete result;
    return val;
}

inline const std::vector<double>& verts_buffer(const IfcGeom::Representation::Triangulation* self) {
    return self->verts();
}

inline const std::vector<int>& faces_buffer(const IfcGeom::Representation::Triangulation* self) {
    return self->faces();
}

inline const std::vector<double>& normals_buffer(const IfcGeom::Representation::Triangulation* self) {
    return self->normals();
}

inline const std::vector<int>& edges_buffer(const IfcGeom::Representation::Triangulation* self) {
    return self->edges();
}

inline const std::vector<int>& material_ids_buffer(const IfcGeom::Representation::Triangulation* self) {
    return self->material_ids();
}

inline const std::vector<int>& item_ids_buffer(const IfcGeom::Representation::Triangulation* self) {
    return self->item_ids();
}

inline const std::vector<int>& edges_item_ids_buffer(const IfcGeom::Representation::Triangulation* self) {
    return self->edges_item_ids();
}

inline const std::vector<double>& uvs_buffer(const IfcGeom::Representation::Triangulation* self) {
    return self->uvs();
}

inline std::vector<double> colors_buffer(const IfcGeom::Representation::Triangulation* self) {
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

inline std::size_t colors_buffer_size(const IfcGeom::Representation::Triangulation* self) {
    return self->materials().size() * 4;
}

inline std::size_t instance_id(ifcopenshell::geometry::taxonomy::style* self) {
    if (!self->instance) {
        return static_cast<std::size_t>(0);
    }
    auto entity = self->instance.as<express::Entity>();
    if (!entity) {
        return static_cast<std::size_t>(0);
    }
    return static_cast<std::size_t>(entity.id());
}

inline std::size_t control_point_row_count(
    ifcopenshell::geometry::taxonomy::bspline_surface* self
) {
    return self->control_points.size();
}

inline std::size_t control_point_col_count_at(
    ifcopenshell::geometry::taxonomy::bspline_surface* self,
    std::size_t row
) {
    if (row >= self->control_points.size()) {
        throw std::runtime_error("B-spline surface control-point row out of bounds");
    }
    return self->control_points[row].size();
}

inline ifcopenshell::geometry::taxonomy::point3::ptr control_point_at(
    ifcopenshell::geometry::taxonomy::bspline_surface* self,
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

inline bool has_weights(ifcopenshell::geometry::taxonomy::bspline_surface* self) {
    return static_cast<bool>(self->weights);
}

inline std::size_t weight_row_count(
    ifcopenshell::geometry::taxonomy::bspline_surface* self
) {
    if (!self->weights) {
        throw std::runtime_error("B-spline surface weights are not set");
    }
    return self->weights->size();
}

inline std::size_t weight_col_count_at(
    ifcopenshell::geometry::taxonomy::bspline_surface* self,
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
    ifcopenshell::geometry::taxonomy::bspline_surface* self,
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
    ifcopenshell::geometry::function_item_evaluator* self,
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
        return ifcopenshell::geometry::kernels::kernel_registry_instance().has(id);
    }
    if (kind == "mapping") {
        return ifcopenshell::geometry::impl::mapping_registry_instance().has(id);
    }
    if (kind == "tree") {
        return ifcopenshell::geometry::trees::tree_registry_instance().has(id);
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
        return ifcopenshell::geometry::kernels::load_kernel_plugin(
            ifcopenshell::geometry::kernels::kernel_registry_instance(), id
        );
    }
    if (kind == "mapping") {
        return ifcopenshell::geometry::impl::load_mapping_plugin(
            ifcopenshell::geometry::impl::mapping_registry_instance(), id
        );
    }
    if (kind == "tree") {
        return ifcopenshell::geometry::trees::load_tree_plugin(
            ifcopenshell::geometry::trees::tree_registry_instance(), id
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

inline std::unique_ptr<GeometrySerializer> create_geometry_serializer_by_path(
    const std::string& format,
    const std::string& output_filename,
    const std::string& output_temp_filename,
    ifcopenshell::geometry::Settings* geometry_settings,
    ifcopenshell::geometry::SerializerSettings* serializer_settings
) {
    return std::make_unique<ifcopenshell::serializers::PluginGeometrySerializer>(
        format, output_filename, output_temp_filename, *geometry_settings, *serializer_settings
    );
}

inline std::unique_ptr<GeometrySerializer> create_geometry_serializer_by_stream(
    const std::string& format,
    stream_or_filename* output,
    stream_or_filename* output_temp,
    ifcopenshell::geometry::Settings* geometry_settings,
    ifcopenshell::geometry::SerializerSettings* serializer_settings
) {
    return std::make_unique<ifcopenshell::serializers::PluginGeometrySerializer>(
        format, *output, *output_temp, *geometry_settings, *serializer_settings
    );
}

} // namespace ifcgeom::bindings

#endif // IFCWRAP_BINDING_GENERATOR_IFCGEOM_SPEC_HPP
