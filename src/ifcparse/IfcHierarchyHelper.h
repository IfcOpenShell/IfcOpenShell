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

#include "../ifcparse/Ifc2x3.h"
#include "../ifcparse/IfcFile.h"
#include "../ifcparse/IfcWrite.h"

class IfcHierarchyHelper : public IfcParse::IfcFile {
public:
	template <class T> 
	T* addTriplet(double x, double y, double z) {
		std::vector<double> a; a.push_back(x); a.push_back(y); a.push_back(z);
		T* t = new T(a);
		AddEntity(t);
		return t;
	}

	template <class T> 
	T* addDoublet(double x, double y) {
		std::vector<double> a; a.push_back(x); a.push_back(y);
		T* t = new T(a);
		AddEntity(t);
		return t;
	}

	template <class T>
	T* getSingle() {
		typename T::list ts = EntitiesByType<T>();
		if (ts->Size() != 1) return 0;
		return *ts->begin();
	}
	
	Ifc2x3::IfcAxis2Placement3D* addPlacement3d(double ox=0.0, double oy=0.0, double oz=0.0,
		double zx=0.0, double zy=0.0, double zz=1.0,
		double xx=1.0, double xy=0.0, double xz=0.0);

	Ifc2x3::IfcAxis2Placement2D* addPlacement2d(double ox=0.0, double oy=0.0,
		double xx=1.0, double xy=0.0);

	Ifc2x3::IfcLocalPlacement* addLocalPlacement(double ox=0.0, double oy=0.0, double oz=0.0,
		double zx=0.0, double zy=0.0, double zz=1.0,
		double xx=1.0, double xy=0.0, double xz=0.0);

	template <class T>
	void addRelatedObject(Ifc2x3::IfcObjectDefinition* related_object, 
		Ifc2x3::IfcObjectDefinition* relating_object, Ifc2x3::IfcOwnerHistory* owner_hist = 0)
	{
		typename T::list li = EntitiesByType<T>();
		bool found = false;
		for (typename T::it i = li->begin(); i != li->end(); ++i) {
			T* rel = *i;
			if (rel->RelatingObject() == relating_object) {
				Ifc2x3::IfcObjectDefinition::list products = rel->RelatedObjects();
				products->push(related_object);
				rel->setRelatedObjects(products);
				found = true;
				break;
			}
		}
		if (! found) {
			if (! owner_hist) {
				owner_hist = getSingle<Ifc2x3::IfcOwnerHistory>();
			}
			if (! owner_hist) {
				owner_hist = addOwnerHistory();
			}
			Ifc2x3::IfcObjectDefinition::list relating_objects (new IfcTemplatedEntityList<Ifc2x3::IfcObjectDefinition>());
			relating_objects->push(relating_object);
			T* t = new T(IfcWrite::IfcGuidHelper(), owner_hist, boost::none, boost::none, related_object, relating_objects);
			AddEntity(t);
		}
	}

	Ifc2x3::IfcOwnerHistory* addOwnerHistory();	
	Ifc2x3::IfcProject* addProject(Ifc2x3::IfcOwnerHistory* owner_hist = 0);
	void relatePlacements(Ifc2x3::IfcProduct* parent, Ifc2x3::IfcProduct* product);	
	Ifc2x3::IfcSite* addSite(Ifc2x3::IfcProject* proj = 0, Ifc2x3::IfcOwnerHistory* owner_hist = 0);	
	Ifc2x3::IfcBuilding* addBuilding(Ifc2x3::IfcSite* site = 0, Ifc2x3::IfcOwnerHistory* owner_hist = 0);

	Ifc2x3::IfcBuildingStorey* addBuildingStorey(Ifc2x3::IfcBuilding* building = 0, 
		Ifc2x3::IfcOwnerHistory* owner_hist = 0);

	Ifc2x3::IfcBuildingStorey* addBuildingProduct(Ifc2x3::IfcProduct* product, 
		Ifc2x3::IfcBuildingStorey* storey = 0, Ifc2x3::IfcOwnerHistory* owner_hist = 0);

	void addExtrudedPolyline(Ifc2x3::IfcShapeRepresentation* rep, const std::vector<std::pair<double, double> >& points, double h, 
		Ifc2x3::IfcAxis2Placement2D* place=0, Ifc2x3::IfcAxis2Placement3D* place2=0, 
		Ifc2x3::IfcDirection* dir=0, Ifc2x3::IfcRepresentationContext* context=0);

	Ifc2x3::IfcProductDefinitionShape* addExtrudedPolyline(const std::vector<std::pair<double, double> >& points, double h, 
		Ifc2x3::IfcAxis2Placement2D* place=0, Ifc2x3::IfcAxis2Placement3D* place2=0, Ifc2x3::IfcDirection* dir=0, 
		Ifc2x3::IfcRepresentationContext* context=0);

	void addBox(Ifc2x3::IfcShapeRepresentation* rep, double w, double d, double h, 
		Ifc2x3::IfcAxis2Placement2D* place=0, Ifc2x3::IfcAxis2Placement3D* place2=0, 
		Ifc2x3::IfcDirection* dir=0, Ifc2x3::IfcRepresentationContext* context=0);

	Ifc2x3::IfcProductDefinitionShape* addBox(double w, double d, double h, Ifc2x3::IfcAxis2Placement2D* place=0, 
		Ifc2x3::IfcAxis2Placement3D* place2=0, Ifc2x3::IfcDirection* dir=0, Ifc2x3::IfcRepresentationContext* context=0);

	void clipRepresentation(Ifc2x3::IfcProductRepresentation* shape, 
		Ifc2x3::IfcAxis2Placement3D* place, bool agree);

	Ifc2x3::IfcPresentationStyleAssignment* setSurfaceColour(Ifc2x3::IfcProductRepresentation* shape, 
		double r, double g, double b, double a=1.0);

	void setSurfaceColour(Ifc2x3::IfcProductRepresentation* shape, 
		Ifc2x3::IfcPresentationStyleAssignment* style_assignment);

};

template <>
inline void IfcHierarchyHelper::addRelatedObject <Ifc2x3::IfcRelContainedInSpatialStructure> (Ifc2x3::IfcObjectDefinition* related_object, 
	Ifc2x3::IfcObjectDefinition* relating_object, Ifc2x3::IfcOwnerHistory* owner_hist)
{
	Ifc2x3::IfcRelContainedInSpatialStructure::list li = EntitiesByType<Ifc2x3::IfcRelContainedInSpatialStructure>();
	bool found = false;
	for (Ifc2x3::IfcRelContainedInSpatialStructure::it i = li->begin(); i != li->end(); ++i) {
		Ifc2x3::IfcRelContainedInSpatialStructure* rel = *i;
		if (rel->RelatingStructure() == relating_object) {
			Ifc2x3::IfcProduct::list products = rel->RelatedElements();
			products->push((Ifc2x3::IfcProduct*)related_object);
			rel->setRelatedElements(products);
			found = true;
			break;
		}
	}
	if (! found) {
		if (! owner_hist) {
			owner_hist = getSingle<Ifc2x3::IfcOwnerHistory>();
		}
		if (! owner_hist) {
			owner_hist = addOwnerHistory();
		}
		Ifc2x3::IfcProduct::list relating_objects (new IfcTemplatedEntityList<Ifc2x3::IfcProduct>());
		relating_objects->push((Ifc2x3::IfcProduct*)relating_object);
		Ifc2x3::IfcRelContainedInSpatialStructure* t = new Ifc2x3::IfcRelContainedInSpatialStructure(IfcWrite::IfcGuidHelper(), owner_hist, 
			boost::none, boost::none, relating_objects, (Ifc2x3::IfcSpatialStructureElement*)related_object);

		AddEntity(t);
	}
}

#endif