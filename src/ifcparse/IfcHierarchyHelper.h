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

#include <map>

#include "ifc_parse_api.h"

#include "../ifcparse/Ifc2x3.h"
#include "../ifcparse/Ifc4.h"
#include "../ifcparse/Ifc4x1.h"
#include "../ifcparse/Ifc4x2.h"
#include "../ifcparse/Ifc4x3_rc1.h"


#include "../ifcparse/IfcFile.h"
#include "../ifcparse/IfcWrite.h"
#include "../ifcparse/IfcGlobalId.h"

namespace {
	IfcUtil::IfcBaseClass* get_parent_of_relation(IfcUtil::IfcBaseClass* t) {
		return *t->data().getArgument(
			t->declaration().as_entity()->attribute_index("RelatingObject")
		);
	}

	Ifc2x3::IfcObjectDefinition* get_parent_of_relation(Ifc2x3::IfcRelContainedInSpatialStructure* t) {
		return t->RelatingStructure();
	}

	Ifc4::IfcObjectDefinition* get_parent_of_relation(Ifc4::IfcRelContainedInSpatialStructure* t) {
		return t->RelatingStructure();
	}

	Ifc4x1::IfcObjectDefinition* get_parent_of_relation(Ifc4x1::IfcRelContainedInSpatialStructure* t) {
		return t->RelatingStructure();
	}

	Ifc4x2::IfcObjectDefinition* get_parent_of_relation(Ifc4x2::IfcRelContainedInSpatialStructure* t) {
		return t->RelatingStructure();
	}

	Ifc4x3_rc1::IfcObjectDefinition* get_parent_of_relation(Ifc4x3_rc1::IfcRelContainedInSpatialStructure* t) {
		return t->RelatingStructure();
	}

	IfcEntityList::ptr get_children_of_relation(IfcUtil::IfcBaseClass* t) {
		return *t->data().getArgument(
			t->declaration().as_entity()->attribute_index("RelatedElements")
			);
	}

	IfcEntityList::ptr get_children_of_relation(Ifc2x3::IfcRelContainedInSpatialStructure* t) {
		return t->RelatedElements()->generalize();
	}

	IfcEntityList::ptr get_children_of_relation(Ifc4::IfcRelContainedInSpatialStructure* t) {
		return t->RelatedElements()->generalize();
	}

	IfcEntityList::ptr get_children_of_relation(Ifc4x1::IfcRelContainedInSpatialStructure* t) {
		return t->RelatedElements()->generalize();
	}

	IfcEntityList::ptr get_children_of_relation(Ifc4x2::IfcRelContainedInSpatialStructure* t) {
		return t->RelatedElements()->generalize();
	}

	IfcEntityList::ptr get_children_of_relation(Ifc4x3_rc1::IfcRelContainedInSpatialStructure* t) {
		return t->RelatedElements()->generalize();
	}

	IfcEntityList::ptr get_children_of_relation(Ifc2x3::IfcRelAggregates* t) {
		return t->RelatedObjects()->generalize();
	}

	IfcEntityList::ptr get_children_of_relation(Ifc4::IfcRelAggregates* t) {
		return t->RelatedObjects()->generalize();
	}

	IfcEntityList::ptr get_children_of_relation(Ifc4x1::IfcRelAggregates* t) {
		return t->RelatedObjects()->generalize();
	}

	IfcEntityList::ptr get_children_of_relation(Ifc4x2::IfcRelAggregates* t) {
		return t->RelatedObjects()->generalize();
	}

	IfcEntityList::ptr get_children_of_relation(Ifc4x3_rc1::IfcRelAggregates* t) {
		return t->RelatedObjects()->generalize();
	}

	void set_children_of_relation(IfcUtil::IfcBaseClass* t, IfcEntityList::ptr& cs) {
		IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument;
		attr->set(cs);
		t->data().setArgument(
			t->declaration().as_entity()->attribute_index("RelatedElements"),
			attr
		);
	}

	void set_children_of_relation(Ifc2x3::IfcRelContainedInSpatialStructure* t, IfcEntityList::ptr& cs) {
		t->setRelatedElements(cs->as<Ifc2x3::IfcProduct>());
	}

	void set_children_of_relation(Ifc4::IfcRelContainedInSpatialStructure* t, IfcEntityList::ptr& cs) {
		t->setRelatedElements(cs->as<Ifc4::IfcProduct>());
	}
	
	void set_children_of_relation(Ifc4x1::IfcRelContainedInSpatialStructure* t, IfcEntityList::ptr& cs) {
		t->setRelatedElements(cs->as<Ifc4x1::IfcProduct>());
	}

	void set_children_of_relation(Ifc4x2::IfcRelContainedInSpatialStructure* t, IfcEntityList::ptr& cs) {
		t->setRelatedElements(cs->as<Ifc4x2::IfcProduct>());
	}

	void set_children_of_relation(Ifc4x3_rc1::IfcRelContainedInSpatialStructure* t, IfcEntityList::ptr& cs) {
		t->setRelatedElements(cs->as<Ifc4x3_rc1::IfcProduct>());
	}

	void set_children_of_relation(Ifc2x3::IfcRelAggregates* t, IfcEntityList::ptr& cs) {
		t->setRelatedObjects(cs->as<Ifc2x3::IfcObjectDefinition>());
	}

	void set_children_of_relation(Ifc4::IfcRelAggregates* t, IfcEntityList::ptr& cs) {
		t->setRelatedObjects(cs->as<Ifc4::IfcObjectDefinition>());
	}

	void set_children_of_relation(Ifc4x1::IfcRelAggregates* t, IfcEntityList::ptr& cs) {
		t->setRelatedObjects(cs->as<Ifc4x1::IfcObjectDefinition>());
	}

	void set_children_of_relation(Ifc4x2::IfcRelAggregates* t, IfcEntityList::ptr& cs) {
		t->setRelatedObjects(cs->as<Ifc4x2::IfcObjectDefinition>());
	}

	void set_children_of_relation(Ifc4x3_rc1::IfcRelAggregates* t, IfcEntityList::ptr& cs) {
		t->setRelatedObjects(cs->as<Ifc4x3_rc1::IfcObjectDefinition>());
	}
}
template <typename Schema>
class IFC_PARSE_API IfcHierarchyHelper : public IfcParse::IfcFile {
public:
	IfcHierarchyHelper() : IfcParse::IfcFile(&Schema::get_schema()) {}

	template <class T> 
	T* addTriplet(double x, double y, double z) {
		std::vector<double> a; a.push_back(x); a.push_back(y); a.push_back(z);
		T* t = new T(a);
		addEntity(t);
		return t;
	}

	template <class T> 
	T* addDoublet(double x, double y) {
		std::vector<double> a; a.push_back(x); a.push_back(y);
		T* t = new T(a);
		addEntity(t);
		return t;
	}

	template <class T>
	T* getSingle() {
		typename T::list::ptr ts = instances_by_type<T>();
		if (ts->size() != 1) return 0;
		return *ts->begin();
	}
	
	typename Schema::IfcAxis2Placement3D* addPlacement3d(double ox=0.0, double oy=0.0, double oz=0.0,
		double zx=0.0, double zy=0.0, double zz=1.0,
		double xx=1.0, double xy=0.0, double xz=0.0);

	typename Schema::IfcAxis2Placement2D* addPlacement2d(double ox=0.0, double oy=0.0,
		double xx=1.0, double xy=0.0);

	typename Schema::IfcLocalPlacement* addLocalPlacement(typename Schema::IfcObjectPlacement* parent = 0,
		double ox=0.0, double oy=0.0, double oz=0.0,
		double zx=0.0, double zy=0.0, double zz=1.0,
		double xx=1.0, double xy=0.0, double xz=0.0);

	template <class T>
	void addRelatedObject(typename Schema::IfcObjectDefinition* relating_object, 
		typename Schema::IfcObjectDefinition* related_object, typename Schema::IfcOwnerHistory* owner_hist = 0)
	{
		typename T::list::ptr li = instances_by_type<T>();
		bool found = false;
		for (typename T::list::it i = li->begin(); i != li->end(); ++i) {
			T* rel = *i;
            try {
                if (get_parent_of_relation(rel) == relating_object) {
                    IfcEntityList::ptr products = get_children_of_relation(rel);
                    products->push(related_object);
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
		if (! found) {
			if (! owner_hist) {
				owner_hist = getSingle<typename Schema::IfcOwnerHistory>();
			}
			if (! owner_hist) {
				owner_hist = addOwnerHistory();
			}

			IfcEntityList::ptr related_objects (new IfcEntityList);
			related_objects->push(related_object);

			IfcEntityInstanceData* data = new IfcEntityInstanceData(&T::Class());
			{ IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument(); attr->set<std::string>(IfcParse::IfcGlobalId()); data->setArgument(0, attr); }
			{ IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument(); attr->set(owner_hist); data->setArgument(1, attr); }
			int relating_index = 4, related_index = 5;
			if (T::Class().name() == "IfcRelContainedInSpatialStructure") {
				// IfcRelContainedInSpatialStructure has attributes reversed.
				std::swap(relating_index, related_index);
			}
			{ IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument(); attr->set(relating_object); data->setArgument(relating_index, attr); }
			{ IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument(); attr->set(related_objects); data->setArgument(related_index, attr); }
			
			T* t = (T*)Schema::get_schema().instantiate(data);
			addEntity(t);
		}
	}

	typename Schema::IfcOwnerHistory* addOwnerHistory();	
	typename Schema::IfcProject* addProject(typename Schema::IfcOwnerHistory* owner_hist = 0);
	void relatePlacements(typename Schema::IfcProduct* parent, typename Schema::IfcProduct* product);	
	typename Schema::IfcSite* addSite(typename Schema::IfcProject* proj = 0, typename Schema::IfcOwnerHistory* owner_hist = 0);	
	typename Schema::IfcBuilding* addBuilding(typename Schema::IfcSite* site = 0, typename Schema::IfcOwnerHistory* owner_hist = 0);

	typename Schema::IfcBuildingStorey* addBuildingStorey(typename Schema::IfcBuilding* building = 0, 
		typename Schema::IfcOwnerHistory* owner_hist = 0);

	typename Schema::IfcBuildingStorey* addBuildingProduct(typename Schema::IfcProduct* product, 
		typename Schema::IfcBuildingStorey* storey = 0, typename Schema::IfcOwnerHistory* owner_hist = 0);

	void addExtrudedPolyline(typename Schema::IfcShapeRepresentation* rep, const std::vector<std::pair<double, double> >& points, double h, 
		typename Schema::IfcAxis2Placement2D* place=0, typename Schema::IfcAxis2Placement3D* place2=0, 
		typename Schema::IfcDirection* dir=0, typename Schema::IfcRepresentationContext* context=0);

	typename Schema::IfcProductDefinitionShape* addExtrudedPolyline(const std::vector<std::pair<double, double> >& points, double h, 
		typename Schema::IfcAxis2Placement2D* place=0, typename Schema::IfcAxis2Placement3D* place2=0, typename Schema::IfcDirection* dir=0, 
		typename Schema::IfcRepresentationContext* context=0);

	void addBox(typename Schema::IfcShapeRepresentation* rep, double w, double d, double h, 
		typename Schema::IfcAxis2Placement2D* place=0, typename Schema::IfcAxis2Placement3D* place2=0, 
		typename Schema::IfcDirection* dir=0, typename Schema::IfcRepresentationContext* context=0);

	typename Schema::IfcProductDefinitionShape* addBox(double w, double d, double h, typename Schema::IfcAxis2Placement2D* place=0, 
		typename Schema::IfcAxis2Placement3D* place2=0, typename Schema::IfcDirection* dir=0, typename Schema::IfcRepresentationContext* context=0);

	void addAxis(typename Schema::IfcShapeRepresentation* rep, double l, typename Schema::IfcRepresentationContext* context=0);

	typename Schema::IfcProductDefinitionShape* addAxisBox(double w, double d, double h, typename Schema::IfcRepresentationContext* context=0);

	void clipRepresentation(typename Schema::IfcProductRepresentation* shape, 
		typename Schema::IfcAxis2Placement3D* place, bool agree);

	void clipRepresentation(typename Schema::IfcRepresentation* shape, 
		typename Schema::IfcAxis2Placement3D* place, bool agree);

	typename Schema::IfcPresentationStyleAssignment* addStyleAssignment(double r, double g, double b, double a=1.0);

	typename Schema::IfcPresentationStyleAssignment* setSurfaceColour(typename Schema::IfcProductRepresentation* shape, 
		double r, double g, double b, double a=1.0);

	typename Schema::IfcPresentationStyleAssignment* setSurfaceColour(typename Schema::IfcRepresentation* shape, 
		double r, double g, double b, double a=1.0);

	void setSurfaceColour(typename Schema::IfcProductRepresentation* shape, 
		typename Schema::IfcPresentationStyleAssignment* style_assignment);

	void setSurfaceColour(typename Schema::IfcRepresentation* shape, 
		typename Schema::IfcPresentationStyleAssignment* style_assignment);

	typename Schema::IfcProductDefinitionShape* addMappedItem(typename Schema::IfcShapeRepresentation*, 
		typename Schema::IfcCartesianTransformationOperator3D* transform = 0,
		typename Schema::IfcProductDefinitionShape* def = 0);

	typename Schema::IfcProductDefinitionShape* addMappedItem(typename Schema::IfcShapeRepresentation::list::ptr, 
		typename Schema::IfcCartesianTransformationOperator3D* transform = 0);
	
	typename Schema::IfcShapeRepresentation* addEmptyRepresentation(const std::string& repid = "Body", const std::string& reptype = "SweptSolid");

	typename Schema::IfcGeometricRepresentationContext* getRepresentationContext(const std::string&);

private:
	std::map<std::string, typename Schema::IfcGeometricRepresentationContext*> contexts;
};

/*
template <>
inline void IfcHierarchyHelper::addRelatedObject <typename Schema::IfcRelContainedInSpatialStructure> (typename Schema::IfcObjectDefinition* relating_structure, 
	typename Schema::IfcObjectDefinition* related_object, typename Schema::IfcOwnerHistory* owner_hist)
{
	typename Schema::IfcRelContainedInSpatialStructure::list::ptr li = instances_by_type<typename Schema::IfcRelContainedInSpatialStructure>();
	bool found = false;
	for (typename Schema::IfcRelContainedInSpatialStructure::list::it i = li->begin(); i != li->end(); ++i) {
		typename Schema::IfcRelContainedInSpatialStructure* rel = *i;
		if (rel->RelatingStructure() == relating_structure) {
			typename Schema::IfcProduct::list::ptr products = rel->RelatedElements();
			products->push((typename Schema::IfcProduct*)related_object);
			rel->setRelatedElements(products);
			found = true;
			break;
		}
	}
	if (! found) {
		if (! owner_hist) {
			owner_hist = getSingle<typename Schema::IfcOwnerHistory>();
		}
		if (! owner_hist) {
			owner_hist = addOwnerHistory();
		}
		typename Schema::IfcProduct::list::ptr related_objects (new IfcTemplatedEntityList<typename Schema::IfcProduct>());
		related_objects->push((typename Schema::IfcProduct*)related_object);
		typename Schema::IfcRelContainedInSpatialStructure* t = new typename Schema::IfcRelContainedInSpatialStructure(IfcParse::IfcGlobalId(), owner_hist, 
			boost::none, boost::none, related_objects, (typename Schema::IfcSpatialStructureElement*)relating_structure);

		addEntity(t);
	}
}

template <>
inline void IfcHierarchyHelper::addRelatedObject <typename Schema::IfcRelDefinesByType> (typename Schema::IfcObjectDefinition* relating_type, 
	typename Schema::IfcObjectDefinition* related_object, typename Schema::IfcOwnerHistory* owner_hist)
{
	typename Schema::IfcRelDefinesByType::list::ptr li = instances_by_type<typename Schema::IfcRelDefinesByType>();
	bool found = false;
	for (typename Schema::IfcRelDefinesByType::list::it i = li->begin(); i != li->end(); ++i) {
		typename Schema::IfcRelDefinesByType* rel = *i;
		if (rel->RelatingType() == relating_type) {
			typename Schema::IfcObject::list::ptr objects = rel->RelatedObjects();
			objects->push((typename Schema::IfcObject*)related_object);
			rel->setRelatedObjects(objects);
			found = true;
			break;
		}
	}
	if (! found) {
		if (! owner_hist) {
			owner_hist = getSingle<typename Schema::IfcOwnerHistory>();
		}
		if (! owner_hist) {
			owner_hist = addOwnerHistory();
		}
		typename Schema::IfcObject::list::ptr related_objects (new IfcTemplatedEntityList<typename Schema::IfcObject>());
		related_objects->push((typename Schema::IfcObject*)related_object);
		typename Schema::IfcRelDefinesByType* t = new typename Schema::IfcRelDefinesByType(IfcParse::IfcGlobalId(), owner_hist, 
			boost::none, boost::none, related_objects, (typename Schema::IfcTypeObject*)relating_type);

		addEntity(t);
	}
}
*/

#endif
