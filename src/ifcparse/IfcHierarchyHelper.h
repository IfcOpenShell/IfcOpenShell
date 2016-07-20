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

#ifdef USE_IFC4
#include "../ifcparse/Ifc4.h"
#else
#include "../ifcparse/Ifc2x3.h"
#endif

#include "../ifcparse/IfcFile.h"
#include "../ifcparse/IfcWrite.h"
#include "../ifcparse/IfcGlobalId.h"

class IFC_PARSE_API IfcHierarchyHelper : public IfcParse::IfcFile {
public:
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
		typename T::list::ptr ts = entitiesByType<T>();
		if (ts->size() != 1) return 0;
		return *ts->begin();
	}
	
	IfcSchema::IfcAxis2Placement3D* addPlacement3d(double ox=0.0, double oy=0.0, double oz=0.0,
		double zx=0.0, double zy=0.0, double zz=1.0,
		double xx=1.0, double xy=0.0, double xz=0.0);

	IfcSchema::IfcAxis2Placement2D* addPlacement2d(double ox=0.0, double oy=0.0,
		double xx=1.0, double xy=0.0);

	IfcSchema::IfcLocalPlacement* addLocalPlacement(IfcSchema::IfcObjectPlacement* parent = 0,
		double ox=0.0, double oy=0.0, double oz=0.0,
		double zx=0.0, double zy=0.0, double zz=1.0,
		double xx=1.0, double xy=0.0, double xz=0.0);

	template <class T>
	void addRelatedObject(IfcSchema::IfcObjectDefinition* relating_object, 
		IfcSchema::IfcObjectDefinition* related_object, IfcSchema::IfcOwnerHistory* owner_hist = 0)
	{
		typename T::list::ptr li = entitiesByType<T>();
		bool found = false;
		for (typename T::list::it i = li->begin(); i != li->end(); ++i) {
			T* rel = *i;
			if (rel->RelatingObject() == relating_object) {
				IfcSchema::IfcObjectDefinition::list::ptr products = rel->RelatedObjects();
				products->push(related_object);
				rel->setRelatedObjects(products);
				found = true;
				break;
			}
		}
		if (! found) {
			if (! owner_hist) {
				owner_hist = getSingle<IfcSchema::IfcOwnerHistory>();
			}
			if (! owner_hist) {
				owner_hist = addOwnerHistory();
			}
			IfcSchema::IfcObjectDefinition::list::ptr related_objects (new IfcTemplatedEntityList<IfcSchema::IfcObjectDefinition>());
			related_objects->push(related_object);
			T* t = new T(IfcParse::IfcGlobalId(), owner_hist, boost::none, boost::none, relating_object, related_objects);
			addEntity(t);
		}
	}

	IfcSchema::IfcOwnerHistory* addOwnerHistory();	
	IfcSchema::IfcProject* addProject(IfcSchema::IfcOwnerHistory* owner_hist = 0);
	void relatePlacements(IfcSchema::IfcProduct* parent, IfcSchema::IfcProduct* product);	
	IfcSchema::IfcSite* addSite(IfcSchema::IfcProject* proj = 0, IfcSchema::IfcOwnerHistory* owner_hist = 0);	
	IfcSchema::IfcBuilding* addBuilding(IfcSchema::IfcSite* site = 0, IfcSchema::IfcOwnerHistory* owner_hist = 0);

	IfcSchema::IfcBuildingStorey* addBuildingStorey(IfcSchema::IfcBuilding* building = 0, 
		IfcSchema::IfcOwnerHistory* owner_hist = 0);

	IfcSchema::IfcBuildingStorey* addBuildingProduct(IfcSchema::IfcProduct* product, 
		IfcSchema::IfcBuildingStorey* storey = 0, IfcSchema::IfcOwnerHistory* owner_hist = 0);

	void addExtrudedPolyline(IfcSchema::IfcShapeRepresentation* rep, const std::vector<std::pair<double, double> >& points, double h, 
		IfcSchema::IfcAxis2Placement2D* place=0, IfcSchema::IfcAxis2Placement3D* place2=0, 
		IfcSchema::IfcDirection* dir=0, IfcSchema::IfcRepresentationContext* context=0);

	IfcSchema::IfcProductDefinitionShape* addExtrudedPolyline(const std::vector<std::pair<double, double> >& points, double h, 
		IfcSchema::IfcAxis2Placement2D* place=0, IfcSchema::IfcAxis2Placement3D* place2=0, IfcSchema::IfcDirection* dir=0, 
		IfcSchema::IfcRepresentationContext* context=0);

	void addBox(IfcSchema::IfcShapeRepresentation* rep, double w, double d, double h, 
		IfcSchema::IfcAxis2Placement2D* place=0, IfcSchema::IfcAxis2Placement3D* place2=0, 
		IfcSchema::IfcDirection* dir=0, IfcSchema::IfcRepresentationContext* context=0);

	IfcSchema::IfcProductDefinitionShape* addBox(double w, double d, double h, IfcSchema::IfcAxis2Placement2D* place=0, 
		IfcSchema::IfcAxis2Placement3D* place2=0, IfcSchema::IfcDirection* dir=0, IfcSchema::IfcRepresentationContext* context=0);

	void addAxis(IfcSchema::IfcShapeRepresentation* rep, double l, IfcSchema::IfcRepresentationContext* context=0);

	IfcSchema::IfcProductDefinitionShape* addAxisBox(double w, double d, double h, IfcSchema::IfcRepresentationContext* context=0);

	void clipRepresentation(IfcSchema::IfcProductRepresentation* shape, 
		IfcSchema::IfcAxis2Placement3D* place, bool agree);

	void clipRepresentation(IfcSchema::IfcRepresentation* shape, 
		IfcSchema::IfcAxis2Placement3D* place, bool agree);

	IfcSchema::IfcPresentationStyleAssignment* addStyleAssignment(double r, double g, double b, double a=1.0);

	IfcSchema::IfcPresentationStyleAssignment* setSurfaceColour(IfcSchema::IfcProductRepresentation* shape, 
		double r, double g, double b, double a=1.0);

	IfcSchema::IfcPresentationStyleAssignment* setSurfaceColour(IfcSchema::IfcRepresentation* shape, 
		double r, double g, double b, double a=1.0);

	void setSurfaceColour(IfcSchema::IfcProductRepresentation* shape, 
		IfcSchema::IfcPresentationStyleAssignment* style_assignment);

	void setSurfaceColour(IfcSchema::IfcRepresentation* shape, 
		IfcSchema::IfcPresentationStyleAssignment* style_assignment);

	IfcSchema::IfcProductDefinitionShape* addMappedItem(IfcSchema::IfcShapeRepresentation*, 
		IfcSchema::IfcCartesianTransformationOperator3D* transform = 0,
		IfcSchema::IfcProductDefinitionShape* def = 0);

	IfcSchema::IfcProductDefinitionShape* addMappedItem(IfcSchema::IfcShapeRepresentation::list::ptr, 
		IfcSchema::IfcCartesianTransformationOperator3D* transform = 0);
	
	IfcSchema::IfcShapeRepresentation* addEmptyRepresentation(const std::string& repid = "Body", const std::string& reptype = "SweptSolid");

	IfcSchema::IfcGeometricRepresentationContext* getRepresentationContext(const std::string&);

private:
	std::map<std::string, IfcSchema::IfcGeometricRepresentationContext*> contexts;
};

template <>
inline void IfcHierarchyHelper::addRelatedObject <IfcSchema::IfcRelContainedInSpatialStructure> (IfcSchema::IfcObjectDefinition* relating_structure, 
	IfcSchema::IfcObjectDefinition* related_object, IfcSchema::IfcOwnerHistory* owner_hist)
{
	IfcSchema::IfcRelContainedInSpatialStructure::list::ptr li = entitiesByType<IfcSchema::IfcRelContainedInSpatialStructure>();
	bool found = false;
	for (IfcSchema::IfcRelContainedInSpatialStructure::list::it i = li->begin(); i != li->end(); ++i) {
		IfcSchema::IfcRelContainedInSpatialStructure* rel = *i;
		if (rel->RelatingStructure() == relating_structure) {
			IfcSchema::IfcProduct::list::ptr products = rel->RelatedElements();
			products->push((IfcSchema::IfcProduct*)related_object);
			rel->setRelatedElements(products);
			found = true;
			break;
		}
	}
	if (! found) {
		if (! owner_hist) {
			owner_hist = getSingle<IfcSchema::IfcOwnerHistory>();
		}
		if (! owner_hist) {
			owner_hist = addOwnerHistory();
		}
		IfcSchema::IfcProduct::list::ptr related_objects (new IfcTemplatedEntityList<IfcSchema::IfcProduct>());
		related_objects->push((IfcSchema::IfcProduct*)related_object);
		IfcSchema::IfcRelContainedInSpatialStructure* t = new IfcSchema::IfcRelContainedInSpatialStructure(IfcParse::IfcGlobalId(), owner_hist, 
			boost::none, boost::none, related_objects, (IfcSchema::IfcSpatialStructureElement*)relating_structure);

		addEntity(t);
	}
}

template <>
inline void IfcHierarchyHelper::addRelatedObject <IfcSchema::IfcRelDefinesByType> (IfcSchema::IfcObjectDefinition* relating_type, 
	IfcSchema::IfcObjectDefinition* related_object, IfcSchema::IfcOwnerHistory* owner_hist)
{
	IfcSchema::IfcRelDefinesByType::list::ptr li = entitiesByType<IfcSchema::IfcRelDefinesByType>();
	bool found = false;
	for (IfcSchema::IfcRelDefinesByType::list::it i = li->begin(); i != li->end(); ++i) {
		IfcSchema::IfcRelDefinesByType* rel = *i;
		if (rel->RelatingType() == relating_type) {
			IfcSchema::IfcObject::list::ptr objects = rel->RelatedObjects();
			objects->push((IfcSchema::IfcObject*)related_object);
			rel->setRelatedObjects(objects);
			found = true;
			break;
		}
	}
	if (! found) {
		if (! owner_hist) {
			owner_hist = getSingle<IfcSchema::IfcOwnerHistory>();
		}
		if (! owner_hist) {
			owner_hist = addOwnerHistory();
		}
		IfcSchema::IfcObject::list::ptr related_objects (new IfcTemplatedEntityList<IfcSchema::IfcObject>());
		related_objects->push((IfcSchema::IfcObject*)related_object);
		IfcSchema::IfcRelDefinesByType* t = new IfcSchema::IfcRelDefinesByType(IfcParse::IfcGlobalId(), owner_hist, 
			boost::none, boost::none, related_objects, (IfcSchema::IfcTypeObject*)relating_type);

		addEntity(t);
	}
}

#endif