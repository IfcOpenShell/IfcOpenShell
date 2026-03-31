/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

/********************************************************************************
 *                                                                              *
 * This class is a subclass of the regular file class that implements        *
 * several convenience functions for creating geometrical representations and   *
 * spatial containers.                                                          *
 *                                                                              *
 ********************************************************************************/

#ifndef IFCHIERARCHYHELPER_H
#define IFCHIERARCHYHELPER_H

#include "ifc_parse_api.h"
#include "logger.h"

#include <map>

#ifdef HAS_SCHEMA_2x3
#include "schemas/Ifc2x3.h"
#endif
#ifdef HAS_SCHEMA_4
#include "schemas/Ifc4.h"
#endif
#ifdef HAS_SCHEMA_4x1
#include "schemas/Ifc4x1.h"
#endif
#ifdef HAS_SCHEMA_4x2
#include "schemas/Ifc4x2.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc1
#include "schemas/Ifc4x3_rc1.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc2
#include "schemas/Ifc4x3_rc2.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc3
#include "schemas/Ifc4x3_rc3.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc4
#include "schemas/Ifc4x3_rc4.h"
#endif
#ifdef HAS_SCHEMA_4x3
#include "schemas/Ifc4x3.h"
#endif
#ifdef HAS_SCHEMA_4x3_tc1
#include "schemas/Ifc4x3_tc1.h"
#endif
#ifdef HAS_SCHEMA_4x3_add1
#include "schemas/Ifc4x3_add1.h"
#endif
#ifdef HAS_SCHEMA_4x3_add2
#include "schemas/Ifc4x3_add2.h"
#endif

#include "file.h"
#include "global_id.h"

namespace {
#ifdef HAS_SCHEMA_2x3
Ifc2x3::IfcObjectDefinition get_parent_of_relation(const Ifc2x3::IfcRelContainedInSpatialStructure& relation) {
    return relation.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc2x3::IfcRelContainedInSpatialStructure& relation) {
    return cast_vector<express::Base>(relation.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc2x3::IfcRelAggregates& relation) {
    return cast_vector<express::Base>(relation.RelatedObjects());
}

void set_children_of_relation(Ifc2x3::IfcRelContainedInSpatialStructure& relation, std::vector<express::Base>& children) {
    relation.setRelatedElements(cast_vector<Ifc2x3::IfcProduct>(children));
}

void set_children_of_relation(Ifc2x3::IfcRelAggregates& relation, std::vector<express::Base>& children) {
    relation.setRelatedObjects(cast_vector<Ifc2x3::IfcObjectDefinition>(children));
}
#endif

#ifdef HAS_SCHEMA_4
Ifc4::IfcObjectDefinition get_parent_of_relation(const Ifc4::IfcRelContainedInSpatialStructure& relation) {
    return relation.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4::IfcRelContainedInSpatialStructure& relation) {
    return cast_vector<express::Base>(relation.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4::IfcRelAggregates& relation) {
    return cast_vector<express::Base>(relation.RelatedObjects());
}

void set_children_of_relation(Ifc4::IfcRelContainedInSpatialStructure& relation, std::vector<express::Base>& children) {
    relation.setRelatedElements(cast_vector<Ifc4::IfcProduct>(children));
}

void set_children_of_relation(Ifc4::IfcRelAggregates& relation, std::vector<express::Base>& children) {
    relation.setRelatedObjects(cast_vector<Ifc4::IfcObjectDefinition>(children));
}
#endif

#ifdef HAS_SCHEMA_4x1
Ifc4x1::IfcObjectDefinition get_parent_of_relation(const Ifc4x1::IfcRelContainedInSpatialStructure& relation) {
    return relation.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x1::IfcRelContainedInSpatialStructure& relation) {
    return cast_vector<express::Base>(relation.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x1::IfcRelAggregates& relation) {
    return cast_vector<express::Base>(relation.RelatedObjects());
}

void set_children_of_relation(Ifc4x1::IfcRelContainedInSpatialStructure& relation, std::vector<express::Base>& children) {
    relation.setRelatedElements(cast_vector<Ifc4x1::IfcProduct>(children));
}

void set_children_of_relation(Ifc4x1::IfcRelAggregates& relation, std::vector<express::Base>& children) {
    relation.setRelatedObjects(cast_vector<Ifc4x1::IfcObjectDefinition>(children));
}
#endif

#ifdef HAS_SCHEMA_4x2
Ifc4x2::IfcObjectDefinition get_parent_of_relation(const Ifc4x2::IfcRelContainedInSpatialStructure& relation) {
    return relation.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x2::IfcRelContainedInSpatialStructure& relation) {
    return cast_vector<express::Base>(relation.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x2::IfcRelAggregates& relation) {
    return cast_vector<express::Base>(relation.RelatedObjects());
}

void set_children_of_relation(Ifc4x2::IfcRelContainedInSpatialStructure& relation, std::vector<express::Base>& children) {
    relation.setRelatedElements(cast_vector<Ifc4x2::IfcProduct>(children));
}

void set_children_of_relation(Ifc4x2::IfcRelAggregates& relation, std::vector<express::Base>& children) {
    relation.setRelatedObjects(cast_vector<Ifc4x2::IfcObjectDefinition>(children));
}
#endif

#ifdef HAS_SCHEMA_4x3_rc1
Ifc4x3_rc1::IfcObjectDefinition get_parent_of_relation(const Ifc4x3_rc1::IfcRelContainedInSpatialStructure& relation) {
    return relation.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_rc1::IfcRelContainedInSpatialStructure& relation) {
    return cast_vector<express::Base>(relation.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_rc1::IfcRelAggregates& relation) {
    return cast_vector<express::Base>(relation.RelatedObjects());
}

void set_children_of_relation(Ifc4x3_rc1::IfcRelContainedInSpatialStructure& relation, std::vector<express::Base>& children) {
    relation.setRelatedElements(cast_vector<Ifc4x3_rc1::IfcProduct>(children));
}

void set_children_of_relation(Ifc4x3_rc1::IfcRelAggregates& relation, std::vector<express::Base>& children) {
    relation.setRelatedObjects(cast_vector<Ifc4x3_rc1::IfcObjectDefinition>(children));
}
#endif

#ifdef HAS_SCHEMA_4x3_rc2
Ifc4x3_rc2::IfcObjectDefinition get_parent_of_relation(const Ifc4x3_rc2::IfcRelContainedInSpatialStructure& relation) {
    return relation.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_rc2::IfcRelContainedInSpatialStructure& relation) {
    return cast_vector<express::Base>(relation.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_rc2::IfcRelAggregates& relation) {
    return cast_vector<express::Base>(relation.RelatedObjects());
}

void set_children_of_relation(Ifc4x3_rc2::IfcRelContainedInSpatialStructure& relation, std::vector<express::Base>& children) {
    relation.setRelatedElements(cast_vector<Ifc4x3_rc2::IfcProduct>(children));
}

void set_children_of_relation(Ifc4x3_rc2::IfcRelAggregates& relation, std::vector<express::Base>& children) {
    relation.setRelatedObjects(cast_vector<Ifc4x3_rc2::IfcObjectDefinition>(children));
}
#endif

#ifdef HAS_SCHEMA_4x3_rc3
Ifc4x3_rc3::IfcObjectDefinition get_parent_of_relation(const Ifc4x3_rc3::IfcRelContainedInSpatialStructure& relation) {
    return relation.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_rc3::IfcRelContainedInSpatialStructure& relation) {
    return cast_vector<express::Base>(relation.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_rc3::IfcRelAggregates& relation) {
    return cast_vector<express::Base>(relation.RelatedObjects());
}

void set_children_of_relation(Ifc4x3_rc3::IfcRelContainedInSpatialStructure& relation, std::vector<express::Base>& children) {
    relation.setRelatedElements(cast_vector<Ifc4x3_rc3::IfcProduct>(children));
}

void set_children_of_relation(Ifc4x3_rc3::IfcRelAggregates& relation, std::vector<express::Base>& children) {
    relation.setRelatedObjects(cast_vector<Ifc4x3_rc3::IfcObjectDefinition>(children));
}
#endif

#ifdef HAS_SCHEMA_4x3_rc4
Ifc4x3_rc4::IfcObjectDefinition get_parent_of_relation(const Ifc4x3_rc4::IfcRelContainedInSpatialStructure& relation) {
    return relation.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_rc4::IfcRelContainedInSpatialStructure& relation) {
    return cast_vector<express::Base>(relation.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_rc4::IfcRelAggregates& relation) {
    return cast_vector<express::Base>(relation.RelatedObjects());
}

void set_children_of_relation(Ifc4x3_rc4::IfcRelContainedInSpatialStructure& relation, std::vector<express::Base>& children) {
    relation.setRelatedElements(cast_vector<Ifc4x3_rc4::IfcProduct>(children));
}

void set_children_of_relation(Ifc4x3_rc4::IfcRelAggregates& relation, std::vector<express::Base>& children) {
    relation.setRelatedObjects(cast_vector<Ifc4x3_rc4::IfcObjectDefinition>(children));
}
#endif

#ifdef HAS_SCHEMA_4x3
Ifc4x3::IfcObjectDefinition get_parent_of_relation(const Ifc4x3::IfcRelContainedInSpatialStructure& relation) {
    return relation.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3::IfcRelContainedInSpatialStructure& relation) {
    return cast_vector<express::Base>(relation.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3::IfcRelAggregates& relation) {
    return cast_vector<express::Base>(relation.RelatedObjects());
}

void set_children_of_relation(Ifc4x3::IfcRelContainedInSpatialStructure& relation, std::vector<express::Base>& children) {
    relation.setRelatedElements(cast_vector<Ifc4x3::IfcProduct>(children));
}

void set_children_of_relation(Ifc4x3::IfcRelAggregates& relation, std::vector<express::Base>& children) {
    relation.setRelatedObjects(cast_vector<Ifc4x3::IfcObjectDefinition>(children));
}
#endif

#ifdef HAS_SCHEMA_4x3_tc1
Ifc4x3_tc1::IfcObjectDefinition get_parent_of_relation(const Ifc4x3_tc1::IfcRelContainedInSpatialStructure& relation) {
    return relation.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_tc1::IfcRelContainedInSpatialStructure& relation) {
    return cast_vector<express::Base>(relation.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_tc1::IfcRelAggregates& relation) {
    return cast_vector<express::Base>(relation.RelatedObjects());
}

void set_children_of_relation(Ifc4x3_tc1::IfcRelContainedInSpatialStructure& relation, std::vector<express::Base>& children) {
    relation.setRelatedElements(cast_vector<Ifc4x3_tc1::IfcProduct>(children));
}

void set_children_of_relation(Ifc4x3_tc1::IfcRelAggregates& relation, std::vector<express::Base>& children) {
    relation.setRelatedObjects(cast_vector<Ifc4x3_tc1::IfcObjectDefinition>(children));
}
#endif

#ifdef HAS_SCHEMA_4x3_add1
Ifc4x3_add1::IfcObjectDefinition get_parent_of_relation(const Ifc4x3_add1::IfcRelContainedInSpatialStructure& relation) {
    return relation.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_add1::IfcRelContainedInSpatialStructure& relation) {
    return cast_vector<express::Base>(relation.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_add1::IfcRelAggregates& relation) {
    return cast_vector<express::Base>(relation.RelatedObjects());
}

void set_children_of_relation(Ifc4x3_add1::IfcRelContainedInSpatialStructure& relation, std::vector<express::Base>& children) {
    relation.setRelatedElements(cast_vector<Ifc4x3_add1::IfcProduct>(children));
}

void set_children_of_relation(Ifc4x3_add1::IfcRelAggregates& relation, std::vector<express::Base>& children) {
    relation.setRelatedObjects(cast_vector<Ifc4x3_add1::IfcObjectDefinition>(children));
}
#endif

#ifdef HAS_SCHEMA_4x3_add2
Ifc4x3_add2::IfcObjectDefinition get_parent_of_relation(const Ifc4x3_add2::IfcRelContainedInSpatialStructure& relation) {
    return relation.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_add2::IfcRelContainedInSpatialStructure& relation) {
    return cast_vector<express::Base>(relation.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_add2::IfcRelAggregates& relation) {
    return cast_vector<express::Base>(relation.RelatedObjects());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_add2::IfcRelNests& relation) {
    return cast_vector<express::Base>(relation.RelatedObjects());
}

void set_children_of_relation(Ifc4x3_add2::IfcRelContainedInSpatialStructure& relation, std::vector<express::Base>& children) {
    relation.setRelatedElements(cast_vector<Ifc4x3_add2::IfcProduct>(children));
}

void set_children_of_relation(Ifc4x3_add2::IfcRelAggregates& relation, std::vector<express::Base>& children) {
    relation.setRelatedObjects(cast_vector<Ifc4x3_add2::IfcObjectDefinition>(children));
}

void set_children_of_relation(Ifc4x3_add2::IfcRelNests& relation, std::vector<express::Base>& children) {
    relation.setRelatedObjects(cast_vector<Ifc4x3_add2::IfcObjectDefinition>(children));
}
#endif

express::Base get_parent_of_relation(const express::Base& relation) {
    return relation.as<express::Entity>().get("RelatingObject");
}

std::vector<express::Base> get_children_of_relation(const express::Base& relation) {
    return relation.as<express::Entity>().get("RelatedElements");
}

void set_children_of_relation(express::Base& relation, std::vector<express::Base>& children) {
    return relation.set_attribute_value("RelatedElements", children);
}
} // namespace
template <typename Schema>
class IFC_PARSE_API hierarchy_helper : public ifcopenshell::file {
  public:
    hierarchy_helper() : ifcopenshell::file(&Schema::get_schema()) {}

    template <class T>
    T addTriplet(double x, double y, double z) {
        auto t = create<T>();
        t.set_attribute_value(0, std::vector<double>{x, y, z});
        return t;
    }

    template <class T>
    T addDoublet(double x, double y) {
        auto t = create<T>();
        t.set_attribute_value(0, std::vector<double>{x, y});
        return t;
    }    

    template <typename T, typename U>
    T addValue(U value) {
        auto measure = create<T>();
        measure.set_attribute_value(0, value);
        return measure;
    }

    template <class T>
    T getSingle() {
        auto ts = instances_by_type<T>();
        if (ts.size() != 1) {
            return T{};
        }
        return ts.front();
    }

    typename Schema::IfcAxis2Placement3D addPlacement3d(double origin_x = 0.0, double origin_y = 0.0, double origin_z = 0.0, double z_axis_x = 0.0, double z_axis_y = 0.0, double z_axis_z = 1.0, double x_axis_x = 1.0, double x_axis_y = 0.0, double x_axis_z = 0.0);

    typename Schema::IfcAxis2Placement2D addPlacement2d(double origin_x = 0.0, double origin_y = 0.0, double x_axis_x = 1.0, double x_axis_y = 0.0);

    typename Schema::IfcLocalPlacement addLocalPlacement(typename Schema::IfcObjectPlacement parent_placement = typename Schema::IfcObjectPlacement{},
                                                         double origin_x = 0.0,
                                                         double origin_y = 0.0,
                                                         double origin_z = 0.0,
                                                         double z_axis_x = 0.0,
                                                         double z_axis_y = 0.0,
                                                         double z_axis_z = 1.0,
                                                         double x_axis_x = 1.0,
                                                         double x_axis_y = 0.0,
                                                         double x_axis_z = 0.0);

    template <class T>
    void addRelatedObject(const typename Schema::IfcObjectDefinition& relating_object,
                          const typename Schema::IfcObjectDefinition& related_object,
                          typename Schema::IfcOwnerHistory owner_history = typename Schema::IfcOwnerHistory{})
    {
        if constexpr (std::is_same_v<T, typename Schema::IfcRelDefinesByType>) {
            auto li = instances_by_type<typename Schema::IfcRelDefinesByType>();
            bool found = false;
            for (auto & rel : li) {
                if (rel.RelatingType() == relating_object) {
                    auto objects = rel.RelatedObjects();
                    objects.push_back(add_entity(related_object).template as<typename Schema::IfcObject>());
                    rel.setRelatedObjects(objects);
                    found = true;
                    break;
                }
            }
            if (!found) {
                if (!owner_history) {
                    owner_history = getSingle<typename Schema::IfcOwnerHistory>();
                }
                if (!owner_history) {
                    owner_history = addOwnerHistory();
                }
                std::vector<typename Schema::IfcObject> related_objects = {related_object.template as<typename Schema::IfcObject>()};
                auto t = create<typename Schema::IfcRelDefinesByType>();
                t.setGlobalId(ifcopenshell::global_id());
                t.setOwnerHistory(owner_history);
                t.setRelatedObjects(related_objects);
                t.setRelatingType(relating_object.template as<typename Schema::IfcTypeObject>());
            }
        } else {
            auto li = instances_by_type<T>();
            bool found = false;
            for (auto& rel : li) {
                try {
                    if (get_parent_of_relation(rel) == relating_object) {
                        auto products = get_children_of_relation(rel);
                        products.push_back(add_entity(related_object));
                        set_children_of_relation(rel, products);
                        found = true;
                        break;
                    }
                } catch (std::exception& e) {
                    logger::error(e);
                } catch (...) {
                    logger::error("Unknown error in addRelatedObject()");
                }
            }
            if (!found) {
                if (!owner_history) {
                    owner_history = getSingle<typename Schema::IfcOwnerHistory>();
                }
                if (!owner_history) {
                    owner_history = addOwnerHistory();
                }

                std::vector<express::Base> related_objects;
                related_objects.push_back(related_object);

                T t = create<T>();
                t.set_attribute_value(0, (std::string)ifcopenshell::global_id());
                t.set_attribute_value(1, owner_history);
                int relating_index = 4;
                int related_index = 5;
                if (T::Class().name() == "IfcRelContainedInSpatialStructure" || std::is_base_of<typename Schema::IfcRelDefines, T>::value) {
                    // some classes have attributes reversed.
                    std::swap(relating_index, related_index);
                }
                t.set_attribute_value(relating_index, relating_object);
                t.set_attribute_value(related_index, related_objects);
            }
        }
    }

    typename Schema::IfcOwnerHistory addOwnerHistory();
    typename Schema::IfcProject addProject(typename Schema::IfcOwnerHistory owner_history = typename Schema::IfcOwnerHistory{});
    void relatePlacements(typename Schema::IfcProduct parent, typename Schema::IfcProduct product);
    typename Schema::IfcSite addSite(typename Schema::IfcProject project = typename Schema::IfcProject{}, typename Schema::IfcOwnerHistory owner_history = typename Schema::IfcOwnerHistory{});
    typename Schema::IfcBuilding addBuilding(typename Schema::IfcSite site = typename Schema::IfcSite{}, typename Schema::IfcOwnerHistory owner_history = typename Schema::IfcOwnerHistory{});

    typename Schema::IfcBuildingStorey addBuildingStorey(typename Schema::IfcBuilding building = typename Schema::IfcBuilding{},
                                                         typename Schema::IfcOwnerHistory owner_history = typename Schema::IfcOwnerHistory{});

    typename Schema::IfcBuildingStorey addBuildingProduct(typename Schema::IfcProduct product,
                                                          typename Schema::IfcBuildingStorey storey = typename Schema::IfcBuildingStorey{},
                                                          typename Schema::IfcOwnerHistory owner_history = typename Schema::IfcOwnerHistory{});

    void addExtrudedPolyline(typename Schema::IfcShapeRepresentation representation, const std::vector<std::pair<double, double>>& points, double height, typename Schema::IfcAxis2Placement2D profile_placement = typename Schema::IfcAxis2Placement2D{}, typename Schema::IfcAxis2Placement3D extrusion_placement = typename Schema::IfcAxis2Placement3D{}, typename Schema::IfcDirection extrusion_direction = typename Schema::IfcDirection{}, typename Schema::IfcRepresentationContext context = typename Schema::IfcRepresentationContext{});

    typename Schema::IfcProductDefinitionShape addExtrudedPolyline(const std::vector<std::pair<double, double>>& points, double height, typename Schema::IfcAxis2Placement2D profile_placement = typename Schema::IfcAxis2Placement2D{}, typename Schema::IfcAxis2Placement3D extrusion_placement = typename Schema::IfcAxis2Placement3D{}, typename Schema::IfcDirection extrusion_direction = typename Schema::IfcDirection{}, typename Schema::IfcRepresentationContext context = typename Schema::IfcRepresentationContext{});

    void addBox(typename Schema::IfcShapeRepresentation representation, double width, double depth, double height, typename Schema::IfcAxis2Placement2D profile_placement = typename Schema::IfcAxis2Placement2D{}, typename Schema::IfcAxis2Placement3D extrusion_placement = typename Schema::IfcAxis2Placement3D{}, typename Schema::IfcDirection extrusion_direction = typename Schema::IfcDirection{}, typename Schema::IfcRepresentationContext context = typename Schema::IfcRepresentationContext{});

    typename Schema::IfcProductDefinitionShape addBox(double width, double depth, double height, typename Schema::IfcAxis2Placement2D profile_placement = typename Schema::IfcAxis2Placement2D{}, typename Schema::IfcAxis2Placement3D extrusion_placement = typename Schema::IfcAxis2Placement3D{}, typename Schema::IfcDirection extrusion_direction = typename Schema::IfcDirection{}, typename Schema::IfcRepresentationContext context = typename Schema::IfcRepresentationContext{});

    void addAxis(typename Schema::IfcShapeRepresentation representation, double length, typename Schema::IfcRepresentationContext context = typename Schema::IfcRepresentationContext{});

    typename Schema::IfcProductDefinitionShape addAxisBox(double width, double depth, double height, typename Schema::IfcRepresentationContext context = typename Schema::IfcRepresentationContext{});

    void clipRepresentation(typename Schema::IfcProductRepresentation representation,
                            typename Schema::IfcAxis2Placement3D placement,
                            bool sense_agreement);

    void clipRepresentation(typename Schema::IfcRepresentation representation,
                            typename Schema::IfcAxis2Placement3D placement,
                            bool sense_agreement);

    typename Schema::IfcProductDefinitionShape addMappedItem(typename Schema::IfcShapeRepresentation source_representation,
                                                              typename Schema::IfcCartesianTransformationOperator3D transform = typename Schema::IfcCartesianTransformationOperator3D{},
                                                              typename Schema::IfcProductDefinitionShape definition_shape = typename Schema::IfcProductDefinitionShape{});

    typename Schema::IfcProductDefinitionShape addMappedItem(std::vector<typename Schema::IfcShapeRepresentation>& source_representations,
                                                              typename Schema::IfcCartesianTransformationOperator3D transform = typename Schema::IfcCartesianTransformationOperator3D{});

    typename Schema::IfcShapeRepresentation addEmptyRepresentation(const std::string& representation_identifier = "Body", const std::string& representation_type = "SweptSolid");

    typename Schema::IfcGeometricRepresentationContext getRepresentationContext(const std::string& context_identifier);

    typename Schema::IfcGeometricRepresentationSubContext getRepresentationSubContext(const std::string& context_identifier, const std::string& context_type);

  private:
    std::map<std::string, typename Schema::IfcGeometricRepresentationContext> contexts_;
};

#ifdef HAS_SCHEMA_2x3
IFC_PARSE_API Ifc2x3::IfcPresentationStyleAssignment addStyleAssignment(hierarchy_helper<Ifc2x3>& model, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc2x3::IfcPresentationStyleAssignment setSurfaceColour(hierarchy_helper<Ifc2x3>& model, const Ifc2x3::IfcProductRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc2x3::IfcPresentationStyleAssignment setSurfaceColour(hierarchy_helper<Ifc2x3>& model, const Ifc2x3::IfcRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc2x3>& model, const Ifc2x3::IfcProductRepresentation& shape, const Ifc2x3::IfcPresentationStyleAssignment& style_assignment);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc2x3>& model, const Ifc2x3::IfcRepresentation& shape, const Ifc2x3::IfcPresentationStyleAssignment& style_assignment);
#endif

#ifdef HAS_SCHEMA_4
IFC_PARSE_API Ifc4::IfcPresentationStyleAssignment addStyleAssignment(hierarchy_helper<Ifc4>& model, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4::IfcPresentationStyleAssignment setSurfaceColour(hierarchy_helper<Ifc4>& model, const Ifc4::IfcProductRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4::IfcPresentationStyleAssignment setSurfaceColour(hierarchy_helper<Ifc4>& model, const Ifc4::IfcRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4>& model, const Ifc4::IfcProductRepresentation& shape, const Ifc4::IfcPresentationStyleAssignment& style_assignment);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4>& model, const Ifc4::IfcRepresentation& shape, const Ifc4::IfcPresentationStyleAssignment& style_assignment);
#endif

#ifdef HAS_SCHEMA_4x1
IFC_PARSE_API Ifc4x1::IfcPresentationStyleAssignment addStyleAssignment(hierarchy_helper<Ifc4x1>& model, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x1::IfcPresentationStyleAssignment setSurfaceColour(hierarchy_helper<Ifc4x1>& model, const Ifc4x1::IfcProductRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x1::IfcPresentationStyleAssignment setSurfaceColour(hierarchy_helper<Ifc4x1>& model, const Ifc4x1::IfcRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x1>& model, const Ifc4x1::IfcProductRepresentation& shape, const Ifc4x1::IfcPresentationStyleAssignment& style_assignment);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x1>& model, const Ifc4x1::IfcRepresentation& shape, const Ifc4x1::IfcPresentationStyleAssignment& style_assignment);
#endif

#ifdef HAS_SCHEMA_4x2
IFC_PARSE_API Ifc4x2::IfcPresentationStyleAssignment addStyleAssignment(hierarchy_helper<Ifc4x2>& model, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x2::IfcPresentationStyleAssignment setSurfaceColour(hierarchy_helper<Ifc4x2>& model, const Ifc4x2::IfcProductRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x2::IfcPresentationStyleAssignment setSurfaceColour(hierarchy_helper<Ifc4x2>& model, const Ifc4x2::IfcRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x2>& model, const Ifc4x2::IfcProductRepresentation& shape, const Ifc4x2::IfcPresentationStyleAssignment& style_assignment);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x2>& model, const Ifc4x2::IfcRepresentation& shape, const Ifc4x2::IfcPresentationStyleAssignment& style_assignment);
#endif

#ifdef HAS_SCHEMA_4x3_rc1
IFC_PARSE_API Ifc4x3_rc1::IfcPresentationStyleAssignment addStyleAssignment(hierarchy_helper<Ifc4x3_rc1>& model, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x3_rc1::IfcPresentationStyleAssignment setSurfaceColour(hierarchy_helper<Ifc4x3_rc1>& model, const Ifc4x3_rc1::IfcProductRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x3_rc1::IfcPresentationStyleAssignment setSurfaceColour(hierarchy_helper<Ifc4x3_rc1>& model, const Ifc4x3_rc1::IfcRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x3_rc1>& model, const Ifc4x3_rc1::IfcProductRepresentation& shape, const Ifc4x3_rc1::IfcPresentationStyleAssignment& style_assignment);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x3_rc1>& model, const Ifc4x3_rc1::IfcRepresentation& shape, const Ifc4x3_rc1::IfcPresentationStyleAssignment& style_assignment);
#endif

#ifdef HAS_SCHEMA_4x3_rc2
IFC_PARSE_API Ifc4x3_rc2::IfcPresentationStyleAssignment addStyleAssignment(hierarchy_helper<Ifc4x3_rc2>& model, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x3_rc2::IfcPresentationStyleAssignment setSurfaceColour(hierarchy_helper<Ifc4x3_rc2>& model, const Ifc4x3_rc2::IfcProductRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x3_rc2::IfcPresentationStyleAssignment setSurfaceColour(hierarchy_helper<Ifc4x3_rc2>& model, const Ifc4x3_rc2::IfcRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x3_rc2>& model, const Ifc4x3_rc2::IfcProductRepresentation& shape, const Ifc4x3_rc2::IfcPresentationStyleAssignment& style_assignment);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x3_rc2>& model, const Ifc4x3_rc2::IfcRepresentation& shape, const Ifc4x3_rc2::IfcPresentationStyleAssignment& style_assignment);
#endif

#ifdef HAS_SCHEMA_4x3_rc3
IFC_PARSE_API Ifc4x3_rc3::IfcPresentationStyle addStyleAssignment(hierarchy_helper<Ifc4x3_rc3>& model, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x3_rc3::IfcPresentationStyle setSurfaceColour(hierarchy_helper<Ifc4x3_rc3>& model, const Ifc4x3_rc3::IfcProductRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x3_rc3::IfcPresentationStyle setSurfaceColour(hierarchy_helper<Ifc4x3_rc3>& model, const Ifc4x3_rc3::IfcRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x3_rc3>& model, const Ifc4x3_rc3::IfcProductRepresentation& shape, const Ifc4x3_rc3::IfcPresentationStyle& style);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x3_rc3>& model, const Ifc4x3_rc3::IfcRepresentation& shape, const Ifc4x3_rc3::IfcPresentationStyle& style);
#endif

#ifdef HAS_SCHEMA_4x3_rc4
IFC_PARSE_API Ifc4x3_rc4::IfcPresentationStyle addStyleAssignment(hierarchy_helper<Ifc4x3_rc4>& model, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x3_rc4::IfcPresentationStyle setSurfaceColour(hierarchy_helper<Ifc4x3_rc4>& model, const Ifc4x3_rc4::IfcProductRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x3_rc4::IfcPresentationStyle setSurfaceColour(hierarchy_helper<Ifc4x3_rc4>& model, const Ifc4x3_rc4::IfcRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x3_rc4>& model, const Ifc4x3_rc4::IfcProductRepresentation& shape, const Ifc4x3_rc4::IfcPresentationStyle& style);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x3_rc4>& model, const Ifc4x3_rc4::IfcRepresentation& shape, const Ifc4x3_rc4::IfcPresentationStyle& style);
#endif

#ifdef HAS_SCHEMA_4x3
IFC_PARSE_API Ifc4x3::IfcPresentationStyle addStyleAssignment(hierarchy_helper<Ifc4x3>& model, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x3::IfcPresentationStyle setSurfaceColour(hierarchy_helper<Ifc4x3>& model, const Ifc4x3::IfcProductRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x3::IfcPresentationStyle setSurfaceColour(hierarchy_helper<Ifc4x3>& model, const Ifc4x3::IfcRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x3>& model, const Ifc4x3::IfcProductRepresentation& shape, const Ifc4x3::IfcPresentationStyle& style);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x3>& model, const Ifc4x3::IfcRepresentation& shape, const Ifc4x3::IfcPresentationStyle& style);
#endif

#ifdef HAS_SCHEMA_4x3_tc1
IFC_PARSE_API Ifc4x3_tc1::IfcPresentationStyle addStyleAssignment(hierarchy_helper<Ifc4x3_tc1>& model, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x3_tc1::IfcPresentationStyle setSurfaceColour(hierarchy_helper<Ifc4x3_tc1>& model, const Ifc4x3_tc1::IfcProductRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x3_tc1::IfcPresentationStyle setSurfaceColour(hierarchy_helper<Ifc4x3_tc1>& model, const Ifc4x3_tc1::IfcRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x3_tc1>& model, const Ifc4x3_tc1::IfcProductRepresentation& shape, const Ifc4x3_tc1::IfcPresentationStyle& style);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x3_tc1>& model, const Ifc4x3_tc1::IfcRepresentation& shape, const Ifc4x3_tc1::IfcPresentationStyle& style);
#endif

#ifdef HAS_SCHEMA_4x3_add1
IFC_PARSE_API Ifc4x3_add1::IfcPresentationStyle addStyleAssignment(hierarchy_helper<Ifc4x3_add1>& model, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x3_add1::IfcPresentationStyle setSurfaceColour(hierarchy_helper<Ifc4x3_add1>& model, const Ifc4x3_add1::IfcProductRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x3_add1::IfcPresentationStyle setSurfaceColour(hierarchy_helper<Ifc4x3_add1>& model, const Ifc4x3_add1::IfcRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x3_add1>& model, const Ifc4x3_add1::IfcProductRepresentation& shape, const Ifc4x3_add1::IfcPresentationStyle& style);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x3_add1>& model, const Ifc4x3_add1::IfcRepresentation& shape, const Ifc4x3_add1::IfcPresentationStyle& style);
#endif

#ifdef HAS_SCHEMA_4x3_add2
IFC_PARSE_API Ifc4x3_add2::IfcPresentationStyle addStyleAssignment(hierarchy_helper<Ifc4x3_add2>& model, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x3_add2::IfcPresentationStyle setSurfaceColour(hierarchy_helper<Ifc4x3_add2>& model, const Ifc4x3_add2::IfcProductRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API Ifc4x3_add2::IfcPresentationStyle setSurfaceColour(hierarchy_helper<Ifc4x3_add2>& model, const Ifc4x3_add2::IfcRepresentation& shape, double red, double green, double blue, double alpha = 1.0);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x3_add2>& model, const Ifc4x3_add2::IfcProductRepresentation& shape, const Ifc4x3_add2::IfcPresentationStyle& style);
IFC_PARSE_API void setSurfaceColour(hierarchy_helper<Ifc4x3_add2>& model, const Ifc4x3_add2::IfcRepresentation& shape, const Ifc4x3_add2::IfcPresentationStyle& style);
#endif

#endif

