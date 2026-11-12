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
#include <type_traits>
#include <vector>

#include "file.h"
#include "global_id.h"

namespace ifcopenshell::hierarchy_detail {

inline const char* parent_attribute_name(const ifcopenshell::declaration& declaration) {
    return declaration.name() == "IfcRelContainedInSpatialStructure" ? "RelatingStructure" : "RelatingObject";
}

inline const char* children_attribute_name(const ifcopenshell::declaration& declaration) {
    return declaration.name() == "IfcRelContainedInSpatialStructure" ? "RelatedElements" : "RelatedObjects";
}

template <typename Relation>
express::base get_parent_of_relation(const Relation& relation) {
    return relation.template as<express::entity>().get(parent_attribute_name(relation.declaration()));
}

template <typename Relation>
std::vector<express::base> get_children_of_relation(const Relation& relation) {
    return relation.template as<express::entity>().get(children_attribute_name(relation.declaration()));
}

template <typename Relation>
void set_children_of_relation(Relation& relation, std::vector<express::base>& children) {
    relation.set_attribute_value(children_attribute_name(relation.declaration()), children);
}

template <typename Schema, typename = void>
struct styled_item_accepts_presentation_style : std::false_type {};

template <typename Schema>
struct styled_item_accepts_presentation_style<Schema,
    std::void_t<decltype(std::declval<typename Schema::IfcStyledItem&>().setStyles(
        std::declval<std::vector<typename Schema::IfcPresentationStyle>>()))>> : std::true_type {};

template <typename Schema, bool DirectStyle = styled_item_accepts_presentation_style<Schema>::value>
struct surface_style_type_selector {
    using type = typename Schema::IfcPresentationStyleAssignment;
};

template <typename Schema>
struct surface_style_type_selector<Schema, true> {
    using type = typename Schema::IfcPresentationStyle;
};

template <typename Schema>
using surface_style_type = typename surface_style_type_selector<Schema>::type;

} // namespace ifcopenshell::hierarchy_detail

template <typename Schema>
class IFC_SCHEMA_API hierarchy_helper : public ifcopenshell::file {
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
                    if (ifcopenshell::hierarchy_detail::get_parent_of_relation(rel) == relating_object) {
                        auto products = ifcopenshell::hierarchy_detail::get_children_of_relation(rel);
                        products.push_back(add_entity(related_object));
                        ifcopenshell::hierarchy_detail::set_children_of_relation(rel, products);
                        found = true;
                        break;
                    }
                } catch (std::exception& e) {
                    ifcopenshell::logger::root().error(e);
                } catch (...) {
                    ifcopenshell::logger::root().error("Unknown error in addRelatedObject()");
                }
            }
            if (!found) {
                if (!owner_history) {
                    owner_history = getSingle<typename Schema::IfcOwnerHistory>();
                }
                if (!owner_history) {
                    owner_history = addOwnerHistory();
                }

                std::vector<express::base> related_objects;
                related_objects.push_back(related_object);

                T t = create<T>();
                t.set_attribute_value(0, (std::string)ifcopenshell::global_id());
                t.set_attribute_value(1, owner_history);
                int relating_index = 4;
                int related_index = 5;
                if (T::Class().name() == "IfcRelContainedInSpatialStructure" || T::Class().name() == "IfcRelReferencedInSpatialStructure" || std::is_base_of<typename Schema::IfcRelDefines, T>::value) {
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

template <typename Schema>
IFC_SCHEMA_API ifcopenshell::hierarchy_detail::surface_style_type<Schema>
addStyleAssignment(hierarchy_helper<Schema>& model, double red, double green, double blue, double alpha = 1.0);

template <typename Schema>
IFC_SCHEMA_API ifcopenshell::hierarchy_detail::surface_style_type<Schema>
setSurfaceColour(hierarchy_helper<Schema>& model,
                 const typename Schema::IfcProductRepresentation& shape,
                 double red,
                 double green,
                 double blue,
                 double alpha = 1.0);

template <typename Schema>
IFC_SCHEMA_API ifcopenshell::hierarchy_detail::surface_style_type<Schema>
setSurfaceColour(hierarchy_helper<Schema>& model,
                 const typename Schema::IfcRepresentation& shape,
                 double red,
                 double green,
                 double blue,
                 double alpha = 1.0);

template <typename Schema>
IFC_SCHEMA_API void setSurfaceColour(
    hierarchy_helper<Schema>& model,
    const typename Schema::IfcProductRepresentation& shape,
    const ifcopenshell::hierarchy_detail::surface_style_type<Schema>& style);

template <typename Schema>
IFC_SCHEMA_API void setSurfaceColour(
    hierarchy_helper<Schema>& model,
    const typename Schema::IfcRepresentation& shape,
    const ifcopenshell::hierarchy_detail::surface_style_type<Schema>& style);

#endif
