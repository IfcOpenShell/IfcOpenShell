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
 * This class is a subclass of the regular IfcFile class that implements        *
 * several convenience functions for creating geometrical representations and   *
 * spatial containers.                                                          *
 *                                                                              *
 ********************************************************************************/

#ifndef IFCHIERARCHYHELPER_H
#define IFCHIERARCHYHELPER_H

#include "ifc_parse_api.h"
#include "IfcLogger.h"

#include <map>

#ifdef HAS_SCHEMA_2x3
#include "Ifc2x3.h"
#endif
#ifdef HAS_SCHEMA_4
#include "Ifc4.h"
#endif
#ifdef HAS_SCHEMA_4x1
#include "Ifc4x1.h"
#endif
#ifdef HAS_SCHEMA_4x2
#include "Ifc4x2.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc1
#include "Ifc4x3_rc1.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc2
#include "Ifc4x3_rc2.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc3
#include "Ifc4x3_rc3.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc4
#include "Ifc4x3_rc4.h"
#endif
#ifdef HAS_SCHEMA_4x3
#include "Ifc4x3.h"
#endif
#ifdef HAS_SCHEMA_4x3_tc1
#include "Ifc4x3_tc1.h"
#endif
#ifdef HAS_SCHEMA_4x3_add1
#include "Ifc4x3_add1.h"
#endif
#ifdef HAS_SCHEMA_4x3_add2
#include "Ifc4x3_add2.h"
#endif

#include "IfcFile.h"
#include "IfcGlobalId.h"
#include "IfcWrite.h"

namespace {
#ifdef HAS_SCHEMA_2x3
Ifc2x3::IfcObjectDefinition get_parent_of_relation(const Ifc2x3::IfcRelContainedInSpatialStructure& t) {
    return t.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc2x3::IfcRelContainedInSpatialStructure& t) {
    return cast_vector<express::Base>(t.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc2x3::IfcRelAggregates& t) {
    return cast_vector<express::Base>(t.RelatedObjects());
}

void set_children_of_relation(Ifc2x3::IfcRelContainedInSpatialStructure& t, std::vector<express::Base>& cs) {
    t.setRelatedElements(cast_vector<Ifc2x3::IfcProduct>(cs));
}

void set_children_of_relation(Ifc2x3::IfcRelAggregates& t, std::vector<express::Base>& cs) {
    t.setRelatedObjects(cast_vector<Ifc2x3::IfcObjectDefinition>(cs));
}
#endif

#ifdef HAS_SCHEMA_4
Ifc4::IfcObjectDefinition get_parent_of_relation(const Ifc4::IfcRelContainedInSpatialStructure& t) {
    return t.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4::IfcRelContainedInSpatialStructure& t) {
    return cast_vector<express::Base>(t.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4::IfcRelAggregates& t) {
    return cast_vector<express::Base>(t.RelatedObjects());
}

void set_children_of_relation(Ifc4::IfcRelContainedInSpatialStructure& t, std::vector<express::Base>& cs) {
    t.setRelatedElements(cast_vector<Ifc4::IfcProduct>(cs));
}

void set_children_of_relation(Ifc4::IfcRelAggregates& t, std::vector<express::Base>& cs) {
    t.setRelatedObjects(cast_vector<Ifc4::IfcObjectDefinition>(cs));
}
#endif

#ifdef HAS_SCHEMA_4x1
Ifc4x1::IfcObjectDefinition get_parent_of_relation(const Ifc4x1::IfcRelContainedInSpatialStructure& t) {
    return t.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x1::IfcRelContainedInSpatialStructure& t) {
    return cast_vector<express::Base>(t.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x1::IfcRelAggregates& t) {
    return cast_vector<express::Base>(t.RelatedObjects());
}

void set_children_of_relation(Ifc4x1::IfcRelContainedInSpatialStructure& t, std::vector<express::Base>& cs) {
    t.setRelatedElements(cast_vector<Ifc4x1::IfcProduct>(cs));
}

void set_children_of_relation(Ifc4x1::IfcRelAggregates& t, std::vector<express::Base>& cs) {
    t.setRelatedObjects(cast_vector<Ifc4x1::IfcObjectDefinition>(cs));
}
#endif

#ifdef HAS_SCHEMA_4x2
Ifc4x2::IfcObjectDefinition get_parent_of_relation(const Ifc4x2::IfcRelContainedInSpatialStructure& t) {
    return t.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x2::IfcRelContainedInSpatialStructure& t) {
    return cast_vector<express::Base>(t.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x2::IfcRelAggregates& t) {
    return cast_vector<express::Base>(t.RelatedObjects());
}

void set_children_of_relation(Ifc4x2::IfcRelContainedInSpatialStructure& t, std::vector<express::Base>& cs) {
    t.setRelatedElements(cast_vector<Ifc4x2::IfcProduct>(cs));
}

void set_children_of_relation(Ifc4x2::IfcRelAggregates& t, std::vector<express::Base>& cs) {
    t.setRelatedObjects(cast_vector<Ifc4x2::IfcObjectDefinition>(cs));
}
#endif

#ifdef HAS_SCHEMA_4x3_rc1
Ifc4x3_rc1::IfcObjectDefinition get_parent_of_relation(const Ifc4x3_rc1::IfcRelContainedInSpatialStructure& t) {
    return t.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_rc1::IfcRelContainedInSpatialStructure& t) {
    return cast_vector<express::Base>(t.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_rc1::IfcRelAggregates& t) {
    return cast_vector<express::Base>(t.RelatedObjects());
}

void set_children_of_relation(Ifc4x3_rc1::IfcRelContainedInSpatialStructure& t, std::vector<express::Base>& cs) {
    t.setRelatedElements(cast_vector<Ifc4x3_rc1::IfcProduct>(cs));
}

void set_children_of_relation(Ifc4x3_rc1::IfcRelAggregates& t, std::vector<express::Base>& cs) {
    t.setRelatedObjects(cast_vector<Ifc4x3_rc1::IfcObjectDefinition>(cs));
}
#endif

#ifdef HAS_SCHEMA_4x3_rc2
Ifc4x3_rc2::IfcObjectDefinition get_parent_of_relation(const Ifc4x3_rc2::IfcRelContainedInSpatialStructure& t) {
    return t.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_rc2::IfcRelContainedInSpatialStructure& t) {
    return cast_vector<express::Base>(t.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_rc2::IfcRelAggregates& t) {
    return cast_vector<express::Base>(t.RelatedObjects());
}

void set_children_of_relation(Ifc4x3_rc2::IfcRelContainedInSpatialStructure& t, std::vector<express::Base>& cs) {
    t.setRelatedElements(cast_vector<Ifc4x3_rc2::IfcProduct>(cs));
}

void set_children_of_relation(Ifc4x3_rc2::IfcRelAggregates& t, std::vector<express::Base>& cs) {
    t.setRelatedObjects(cast_vector<Ifc4x3_rc2::IfcObjectDefinition>(cs));
}
#endif

#ifdef HAS_SCHEMA_4x3_rc3
Ifc4x3_rc3::IfcObjectDefinition get_parent_of_relation(const Ifc4x3_rc3::IfcRelContainedInSpatialStructure& t) {
    return t.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_rc3::IfcRelContainedInSpatialStructure& t) {
    return cast_vector<express::Base>(t.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_rc3::IfcRelAggregates& t) {
    return cast_vector<express::Base>(t.RelatedObjects());
}

void set_children_of_relation(Ifc4x3_rc3::IfcRelContainedInSpatialStructure& t, std::vector<express::Base>& cs) {
    t.setRelatedElements(cast_vector<Ifc4x3_rc3::IfcProduct>(cs));
}

void set_children_of_relation(Ifc4x3_rc3::IfcRelAggregates& t, std::vector<express::Base>& cs) {
    t.setRelatedObjects(cast_vector<Ifc4x3_rc3::IfcObjectDefinition>(cs));
}
#endif

#ifdef HAS_SCHEMA_4x3_rc4
Ifc4x3_rc4::IfcObjectDefinition get_parent_of_relation(const Ifc4x3_rc4::IfcRelContainedInSpatialStructure& t) {
    return t.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_rc4::IfcRelContainedInSpatialStructure& t) {
    return cast_vector<express::Base>(t.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_rc4::IfcRelAggregates& t) {
    return cast_vector<express::Base>(t.RelatedObjects());
}

void set_children_of_relation(Ifc4x3_rc4::IfcRelContainedInSpatialStructure& t, std::vector<express::Base>& cs) {
    t.setRelatedElements(cast_vector<Ifc4x3_rc4::IfcProduct>(cs));
}

void set_children_of_relation(Ifc4x3_rc4::IfcRelAggregates& t, std::vector<express::Base>& cs) {
    t.setRelatedObjects(cast_vector<Ifc4x3_rc4::IfcObjectDefinition>(cs));
}
#endif

#ifdef HAS_SCHEMA_4x3
Ifc4x3::IfcObjectDefinition get_parent_of_relation(const Ifc4x3::IfcRelContainedInSpatialStructure& t) {
    return t.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3::IfcRelContainedInSpatialStructure& t) {
    return cast_vector<express::Base>(t.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3::IfcRelAggregates& t) {
    return cast_vector<express::Base>(t.RelatedObjects());
}

void set_children_of_relation(Ifc4x3::IfcRelContainedInSpatialStructure& t, std::vector<express::Base>& cs) {
    t.setRelatedElements(cast_vector<Ifc4x3::IfcProduct>(cs));
}

void set_children_of_relation(Ifc4x3::IfcRelAggregates& t, std::vector<express::Base>& cs) {
    t.setRelatedObjects(cast_vector<Ifc4x3::IfcObjectDefinition>(cs));
}
#endif

#ifdef HAS_SCHEMA_4x3_tc1
Ifc4x3_tc1::IfcObjectDefinition get_parent_of_relation(const Ifc4x3_tc1::IfcRelContainedInSpatialStructure& t) {
    return t.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_tc1::IfcRelContainedInSpatialStructure& t) {
    return cast_vector<express::Base>(t.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_tc1::IfcRelAggregates& t) {
    return cast_vector<express::Base>(t.RelatedObjects());
}

void set_children_of_relation(Ifc4x3_tc1::IfcRelContainedInSpatialStructure& t, std::vector<express::Base>& cs) {
    t.setRelatedElements(cast_vector<Ifc4x3_tc1::IfcProduct>(cs));
}

void set_children_of_relation(Ifc4x3_tc1::IfcRelAggregates& t, std::vector<express::Base>& cs) {
    t.setRelatedObjects(cast_vector<Ifc4x3_tc1::IfcObjectDefinition>(cs));
}
#endif

#ifdef HAS_SCHEMA_4x3_add1
Ifc4x3_add1::IfcObjectDefinition get_parent_of_relation(const Ifc4x3_add1::IfcRelContainedInSpatialStructure& t) {
    return t.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_add1::IfcRelContainedInSpatialStructure& t) {
    return cast_vector<express::Base>(t.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_add1::IfcRelAggregates& t) {
    return cast_vector<express::Base>(t.RelatedObjects());
}

void set_children_of_relation(Ifc4x3_add1::IfcRelContainedInSpatialStructure& t, std::vector<express::Base>& cs) {
    t.setRelatedElements(cast_vector<Ifc4x3_add1::IfcProduct>(cs));
}

void set_children_of_relation(Ifc4x3_add1::IfcRelAggregates& t, std::vector<express::Base>& cs) {
    t.setRelatedObjects(cast_vector<Ifc4x3_add1::IfcObjectDefinition>(cs));
}
#endif

#ifdef HAS_SCHEMA_4x3_add2
Ifc4x3_add2::IfcObjectDefinition get_parent_of_relation(const Ifc4x3_add2::IfcRelContainedInSpatialStructure& t) {
    return t.RelatingStructure();
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_add2::IfcRelContainedInSpatialStructure& t) {
    return cast_vector<express::Base>(t.RelatedElements());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_add2::IfcRelAggregates& t) {
    return cast_vector<express::Base>(t.RelatedObjects());
}

std::vector<express::Base> get_children_of_relation(const Ifc4x3_add2::IfcRelNests& t) {
    return cast_vector<express::Base>(t.RelatedObjects());
}

void set_children_of_relation(Ifc4x3_add2::IfcRelContainedInSpatialStructure& t, std::vector<express::Base>& cs) {
    t.setRelatedElements(cast_vector<Ifc4x3_add2::IfcProduct>(cs));
}

void set_children_of_relation(Ifc4x3_add2::IfcRelAggregates& t, std::vector<express::Base>& cs) {
    t.setRelatedObjects(cast_vector<Ifc4x3_add2::IfcObjectDefinition>(cs));
}

void set_children_of_relation(Ifc4x3_add2::IfcRelNests& t, std::vector<express::Base>& cs) {
    t.setRelatedObjects(cast_vector<Ifc4x3_add2::IfcObjectDefinition>(cs));
}
#endif

express::Base get_parent_of_relation(const express::Base& t) {
    return t.as<express::Entity>().get("RelatingObject");
}

std::vector<express::Base> get_children_of_relation(const express::Base& t) {
    return t.as<express::Entity>().get("RelatedElements");
}

void set_children_of_relation(express::Base& t, std::vector<express::Base>& cs) {
    return t.set_attribute_value("RelatedElements", cs);
}
} // namespace
template <typename Schema>
class IFC_PARSE_API IfcHierarchyHelper : public IfcParse::IfcFile {
  public:
    IfcHierarchyHelper() : IfcParse::IfcFile(&Schema::get_schema()) {}

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
    T addValue(U v) {
        auto measure = create<T>();
        measure.set_attribute_value(0, v);
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

    typename Schema::IfcAxis2Placement3D addPlacement3d(double ox = 0.0, double oy = 0.0, double oz = 0.0, double zx = 0.0, double zy = 0.0, double zz = 1.0, double xx = 1.0, double xy = 0.0, double xz = 0.0);

    typename Schema::IfcAxis2Placement2D addPlacement2d(double ox = 0.0, double oy = 0.0, double xx = 1.0, double xy = 0.0);

    typename Schema::IfcLocalPlacement addLocalPlacement(typename Schema::IfcObjectPlacement parent = typename Schema::IfcObjectPlacement{},
                                                          double ox = 0.0,
                                                          double oy = 0.0,
                                                          double oz = 0.0,
                                                          double zx = 0.0,
                                                          double zy = 0.0,
                                                          double zz = 1.0,
                                                          double xx = 1.0,
                                                          double xy = 0.0,
                                                          double xz = 0.0);

    template <class T>
    void addRelatedObject(const typename Schema::IfcObjectDefinition& relating_object,
                          const typename Schema::IfcObjectDefinition& related_object,
                          typename Schema::IfcOwnerHistory owner_hist = typename Schema::IfcOwnerHistory{})
    {
        if constexpr (std::is_same_v<T, typename Schema::IfcRelDefinesByType>) {
            auto li = instances_by_type<typename Schema::IfcRelDefinesByType>();
            bool found = false;
            for (auto & rel : li) {
                if (rel.RelatingType() == relating_object) {
                    auto objects = rel.RelatedObjects();
                    objects.push_back(addEntity(related_object).template as<typename Schema::IfcObject>());
                    rel.setRelatedObjects(objects);
                    found = true;
                    break;
                }
            }
            if (!found) {
                if (!owner_hist) {
                    owner_hist = getSingle<typename Schema::IfcOwnerHistory>();
                }
                if (!owner_hist) {
                    owner_hist = addOwnerHistory();
                }
                std::vector<typename Schema::IfcObject> related_objects = {related_object.template as<typename Schema::IfcObject>()};
                auto t = create<typename Schema::IfcRelDefinesByType>();
                t.setGlobalId(IfcParse::IfcGlobalId());
                t.setOwnerHistory(owner_hist);
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
                        products.push_back(addEntity(related_object));
                        set_children_of_relation(rel, products);
                        found = true;
                        break;
                    }
                } catch (std::exception& e) {
                    Logger::Error(e);
                } catch (...) {
                    Logger::Error("Unknown error in addRelatedObject()");
                }
            }
            if (!found) {
                if (!owner_hist) {
                    owner_hist = getSingle<typename Schema::IfcOwnerHistory>();
                }
                if (!owner_hist) {
                    owner_hist = addOwnerHistory();
                }

                std::vector<express::Base> related_objects;
                related_objects.push_back(related_object);

                T t = create<T>();
                t.set_attribute_value(0, (std::string)IfcParse::IfcGlobalId());
                t.set_attribute_value(1, owner_hist);
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
    typename Schema::IfcProject addProject(typename Schema::IfcOwnerHistory owner_hist = typename Schema::IfcOwnerHistory{});
    void relatePlacements(typename Schema::IfcProduct parent, typename Schema::IfcProduct product);
    typename Schema::IfcSite addSite(typename Schema::IfcProject = typename Schema::IfcProject{}, typename Schema::IfcOwnerHistory = typename Schema::IfcOwnerHistory{});
    typename Schema::IfcBuilding addBuilding(typename Schema::IfcSite site = typename Schema::IfcSite{}, typename Schema::IfcOwnerHistory owner_hist = typename Schema::IfcOwnerHistory{});

    typename Schema::IfcBuildingStorey addBuildingStorey(typename Schema::IfcBuilding building = typename Schema::IfcBuilding{},
                                                          typename Schema::IfcOwnerHistory owner_hist = typename Schema::IfcOwnerHistory{});

    typename Schema::IfcBuildingStorey addBuildingProduct(typename Schema::IfcProduct product,
                                                           typename Schema::IfcBuildingStorey storey = typename Schema::IfcBuildingStorey{},
                                                           typename Schema::IfcOwnerHistory owner_hist = typename Schema::IfcOwnerHistory{});

    void addExtrudedPolyline(typename Schema::IfcShapeRepresentation rep, const std::vector<std::pair<double, double>>& points, double h, typename Schema::IfcAxis2Placement2D place = typename Schema::IfcAxis2Placement2D{}, typename Schema::IfcAxis2Placement3D place2 = typename Schema::IfcAxis2Placement3D{}, typename Schema::IfcDirection dir = typename Schema::IfcDirection{}, typename Schema::IfcRepresentationContext context = typename Schema::IfcRepresentationContext{});

    typename Schema::IfcProductDefinitionShape addExtrudedPolyline(const std::vector<std::pair<double, double>>& points, double h, typename Schema::IfcAxis2Placement2D place = typename Schema::IfcAxis2Placement2D{}, typename Schema::IfcAxis2Placement3D place2 = typename Schema::IfcAxis2Placement3D{}, typename Schema::IfcDirection dir = typename Schema::IfcDirection{}, typename Schema::IfcRepresentationContext context = typename Schema::IfcRepresentationContext{});

    void addBox(typename Schema::IfcShapeRepresentation rep, double w, double d, double h, typename Schema::IfcAxis2Placement2D place = typename Schema::IfcAxis2Placement2D{}, typename Schema::IfcAxis2Placement3D place2 = typename Schema::IfcAxis2Placement3D{}, typename Schema::IfcDirection dir = typename Schema::IfcDirection{}, typename Schema::IfcRepresentationContext context = typename Schema::IfcRepresentationContext{});

    typename Schema::IfcProductDefinitionShape addBox(double w, double d, double h, typename Schema::IfcAxis2Placement2D place = typename Schema::IfcAxis2Placement2D{}, typename Schema::IfcAxis2Placement3D place2 = typename Schema::IfcAxis2Placement3D{}, typename Schema::IfcDirection dir = typename Schema::IfcDirection{}, typename Schema::IfcRepresentationContext context = typename Schema::IfcRepresentationContext{});

    void addAxis(typename Schema::IfcShapeRepresentation rep, double l, typename Schema::IfcRepresentationContext context = typename Schema::IfcRepresentationContext{});

    typename Schema::IfcProductDefinitionShape addAxisBox(double w, double d, double h, typename Schema::IfcRepresentationContext context = typename Schema::IfcRepresentationContext{});

    void clipRepresentation(typename Schema::IfcProductRepresentation shape,
                            typename Schema::IfcAxis2Placement3D place,
                            bool agree);

    void clipRepresentation(typename Schema::IfcRepresentation shape,
                            typename Schema::IfcAxis2Placement3D place,
                            bool agree);

    typename Schema::IfcProductDefinitionShape addMappedItem(typename Schema::IfcShapeRepresentation,
                                                              typename Schema::IfcCartesianTransformationOperator3D transform = typename Schema::IfcCartesianTransformationOperator3D{},
                                                              typename Schema::IfcProductDefinitionShape def = typename Schema::IfcProductDefinitionShape{});

    typename Schema::IfcProductDefinitionShape addMappedItem(std::vector<typename Schema::IfcShapeRepresentation>&,
                                                              typename Schema::IfcCartesianTransformationOperator3D transform = typename Schema::IfcCartesianTransformationOperator3D{});

    typename Schema::IfcShapeRepresentation addEmptyRepresentation(const std::string& repid = "Body", const std::string& reptype = "SweptSolid");

    typename Schema::IfcGeometricRepresentationContext getRepresentationContext(const std::string&);

    typename Schema::IfcGeometricRepresentationSubContext getRepresentationSubContext(const std::string& ident, const std::string& type);

  private:
    std::map<std::string, typename Schema::IfcGeometricRepresentationContext> contexts_;
};

#ifdef HAS_SCHEMA_2x3
IFC_PARSE_API Ifc2x3::IfcPresentationStyleAssignment addStyleAssignment(IfcHierarchyHelper<Ifc2x3>& file, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc2x3::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc2x3>& file, const Ifc2x3::IfcProductRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc2x3::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc2x3>& file, const Ifc2x3::IfcRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc2x3>& file, const Ifc2x3::IfcProductRepresentation& shape, const Ifc2x3::IfcPresentationStyleAssignment& style_assignment);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc2x3>& file, const Ifc2x3::IfcRepresentation& shape, const Ifc2x3::IfcPresentationStyleAssignment& style_assignment);
#endif

#ifdef HAS_SCHEMA_4
IFC_PARSE_API Ifc4::IfcPresentationStyleAssignment addStyleAssignment(IfcHierarchyHelper<Ifc4>& file, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4>& file, const Ifc4::IfcProductRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4>& file, const Ifc4::IfcRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4>& file, const Ifc4::IfcProductRepresentation& shape, const Ifc4::IfcPresentationStyleAssignment& style_assignment);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4>& file, const Ifc4::IfcRepresentation& shape, const Ifc4::IfcPresentationStyleAssignment& style_assignment);
#endif

#ifdef HAS_SCHEMA_4x1
IFC_PARSE_API Ifc4x1::IfcPresentationStyleAssignment addStyleAssignment(IfcHierarchyHelper<Ifc4x1>& file, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x1::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4x1>& file, const Ifc4x1::IfcProductRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x1::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4x1>& file, const Ifc4x1::IfcRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x1>& file, const Ifc4x1::IfcProductRepresentation& shape, const Ifc4x1::IfcPresentationStyleAssignment& style_assignment);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x1>& file, const Ifc4x1::IfcRepresentation& shape, const Ifc4x1::IfcPresentationStyleAssignment& style_assignment);
#endif

#ifdef HAS_SCHEMA_4x2
IFC_PARSE_API Ifc4x2::IfcPresentationStyleAssignment addStyleAssignment(IfcHierarchyHelper<Ifc4x2>& file, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x2::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4x2>& file, const Ifc4x2::IfcProductRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x2::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4x2>& file, const Ifc4x2::IfcRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x2>& file, const Ifc4x2::IfcProductRepresentation& shape, const Ifc4x2::IfcPresentationStyleAssignment& style_assignment);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x2>& file, const Ifc4x2::IfcRepresentation& shape, const Ifc4x2::IfcPresentationStyleAssignment& style_assignment);
#endif

#ifdef HAS_SCHEMA_4x3_rc1
IFC_PARSE_API Ifc4x3_rc1::IfcPresentationStyleAssignment addStyleAssignment(IfcHierarchyHelper<Ifc4x3_rc1>& file, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x3_rc1::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc1>& file, const Ifc4x3_rc1::IfcProductRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x3_rc1::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc1>& file, const Ifc4x3_rc1::IfcRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc1>& file, const Ifc4x3_rc1::IfcProductRepresentation& shape, const Ifc4x3_rc1::IfcPresentationStyleAssignment& style_assignment);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc1>& file, const Ifc4x3_rc1::IfcRepresentation& shape, const Ifc4x3_rc1::IfcPresentationStyleAssignment& style_assignment);
#endif

#ifdef HAS_SCHEMA_4x3_rc2
IFC_PARSE_API Ifc4x3_rc2::IfcPresentationStyleAssignment addStyleAssignment(IfcHierarchyHelper<Ifc4x3_rc2>& file, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x3_rc2::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc2>& file, const Ifc4x3_rc2::IfcProductRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x3_rc2::IfcPresentationStyleAssignment setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc2>& file, const Ifc4x3_rc2::IfcRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc2>& file, const Ifc4x3_rc2::IfcProductRepresentation& shape, const Ifc4x3_rc2::IfcPresentationStyleAssignment& style_assignment);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc2>& file, const Ifc4x3_rc2::IfcRepresentation& shape, const Ifc4x3_rc2::IfcPresentationStyleAssignment& style_assignment);
#endif

#ifdef HAS_SCHEMA_4x3_rc3
IFC_PARSE_API Ifc4x3_rc3::IfcPresentationStyle addStyleAssignment(IfcHierarchyHelper<Ifc4x3_rc3>& file, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x3_rc3::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc3>& file, const Ifc4x3_rc3::IfcProductRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x3_rc3::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc3>& file, const Ifc4x3_rc3::IfcRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc3>& file, const Ifc4x3_rc3::IfcProductRepresentation& shape, const Ifc4x3_rc3::IfcPresentationStyle& style);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc3>& file, const Ifc4x3_rc3::IfcRepresentation& shape, const Ifc4x3_rc3::IfcPresentationStyle& style);
#endif

#ifdef HAS_SCHEMA_4x3_rc4
IFC_PARSE_API Ifc4x3_rc4::IfcPresentationStyle addStyleAssignment(IfcHierarchyHelper<Ifc4x3_rc4>& file, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x3_rc4::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc4>& file, const Ifc4x3_rc4::IfcProductRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x3_rc4::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc4>& file, const Ifc4x3_rc4::IfcRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc4>& file, const Ifc4x3_rc4::IfcProductRepresentation& shape, const Ifc4x3_rc4::IfcPresentationStyle& style);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_rc4>& file, const Ifc4x3_rc4::IfcRepresentation& shape, const Ifc4x3_rc4::IfcPresentationStyle& style);
#endif

#ifdef HAS_SCHEMA_4x3
IFC_PARSE_API Ifc4x3::IfcPresentationStyle addStyleAssignment(IfcHierarchyHelper<Ifc4x3>& file, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x3::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3>& file, const Ifc4x3::IfcProductRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x3::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3>& file, const Ifc4x3::IfcRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x3>& file, const Ifc4x3::IfcProductRepresentation& shape, const Ifc4x3::IfcPresentationStyle& style);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x3>& file, const Ifc4x3::IfcRepresentation& shape, const Ifc4x3::IfcPresentationStyle& style);
#endif

#ifdef HAS_SCHEMA_4x3_tc1
IFC_PARSE_API Ifc4x3_tc1::IfcPresentationStyle addStyleAssignment(IfcHierarchyHelper<Ifc4x3_tc1>& file, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x3_tc1::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_tc1>& file, const Ifc4x3_tc1::IfcProductRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x3_tc1::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_tc1>& file, const Ifc4x3_tc1::IfcRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_tc1>& file, const Ifc4x3_tc1::IfcProductRepresentation& shape, const Ifc4x3_tc1::IfcPresentationStyle& style);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_tc1>& file, const Ifc4x3_tc1::IfcRepresentation& shape, const Ifc4x3_tc1::IfcPresentationStyle& style);
#endif

#ifdef HAS_SCHEMA_4x3_add1
IFC_PARSE_API Ifc4x3_add1::IfcPresentationStyle addStyleAssignment(IfcHierarchyHelper<Ifc4x3_add1>& file, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x3_add1::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_add1>& file, const Ifc4x3_add1::IfcProductRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x3_add1::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_add1>& file, const Ifc4x3_add1::IfcRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_add1>& file, const Ifc4x3_add1::IfcProductRepresentation& shape, const Ifc4x3_add1::IfcPresentationStyle& style);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_add1>& file, const Ifc4x3_add1::IfcRepresentation& shape, const Ifc4x3_add1::IfcPresentationStyle& style);
#endif

#ifdef HAS_SCHEMA_4x3_add2
IFC_PARSE_API Ifc4x3_add2::IfcPresentationStyle addStyleAssignment(IfcHierarchyHelper<Ifc4x3_add2>& file, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x3_add2::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_add2>& file, const Ifc4x3_add2::IfcProductRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API Ifc4x3_add2::IfcPresentationStyle setSurfaceColour(IfcHierarchyHelper<Ifc4x3_add2>& file, const Ifc4x3_add2::IfcRepresentation& shape, double r, double g, double b, double a = 1.0);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_add2>& file, const Ifc4x3_add2::IfcProductRepresentation& shape, const Ifc4x3_add2::IfcPresentationStyle& style);
IFC_PARSE_API void setSurfaceColour(IfcHierarchyHelper<Ifc4x3_add2>& file, const Ifc4x3_add2::IfcRepresentation& shape, const Ifc4x3_add2::IfcPresentationStyle& style);
#endif

#endif
