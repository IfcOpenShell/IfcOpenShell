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

#include <string>
#include <iostream>
#include <fstream>

#include <TColgp_Array2OfPnt.hxx>
#include <TColgp_Array1OfPnt.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>

#include <Geom_BSplineSurface.hxx>

#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepBuilderAPI_NurbsConvert.hxx>

#include <BRepPrimAPI_MakeBox.hxx>
#include <BRepPrimAPI_MakeSphere.hxx>

#include <BRepAlgoAPI_Cut.hxx>

#include <Standard_Version.hxx>

#ifdef USE_IFC4
#include "../ifcparse/Ifc4.h"
#else
#include "../ifcparse/Ifc2x3.h"
#endif

#include "../ifcparse/IfcBaseClass.h"
#include "../ifcparse/IfcHierarchyHelper.h"
#include "../ifcgeom/IfcGeom.h"

#if USE_VLD
#include <vld.h>
#endif

// The creation of Nurbs-surface for the IfcSite mesh, to be implemented lateron
void createGroundShape(TopoDS_Shape& shape);

int main() {

	// The IfcHierarchyHelper is a subclass of the regular IfcFile that provides several
	// convenience functions for working with geometry in IFC files.
	IfcHierarchyHelper file;
	file.header().file_name().name("IfcAdvancedHouse.ifc");

	IfcSchema::IfcBuilding* building = file.addBuilding();
	// By adding a building, a hierarchy has been automatically created that consists of the following
	// structure: IfcProject > IfcSite > IfcBuilding

	// Lateron changing the name of the IfcProject can be done by obtaining a reference to the 
	// project, which has been created automatically.
	file.getSingle<IfcSchema::IfcProject>()->setName("IfcOpenHouse");

	// To demonstrate the ability to serialize arbitrary opencascade solids a building envelope is
	// constructed by applying boolean operations. Naturally, in IFC, building elements should be 
	// modeled separately, with rich parametric and relational semantics. Creating geometry in this
	// way does not preserve any history and is merely a demonstration of technical capabilities.
	TopoDS_Shape outer =   BRepPrimAPI_MakeBox(gp_Pnt(-5000., -180., -2000.), gp_Pnt(5000., 5180., 3000.)).Shape();
	TopoDS_Shape inner =   BRepPrimAPI_MakeBox(gp_Pnt(-4640.,  180.,     0.), gp_Pnt(4640., 4820., 3000.)).Shape();
	TopoDS_Shape window1 = BRepPrimAPI_MakeBox(gp_Pnt(-5000., -180.,   400.), gp_Pnt( 500., 1180., 2000.)).Shape();
	TopoDS_Shape window2 = BRepPrimAPI_MakeBox(gp_Pnt( 2070., -180.,   400.), gp_Pnt(3930.,  180., 2000.)).Shape();

	TopoDS_Shape building_shell = BRepAlgoAPI_Cut(
		BRepAlgoAPI_Cut(
			BRepAlgoAPI_Cut(outer, inner),
			window1
			),
		window2
	);

	// Since the solid consists only of planar faces and straight edges it can be serialized as an
	// IfcFacetedBRep. If it would not be a polyhedron, serialise() can only be successful when linked
	// to the IFC4 model and with `advanced` set to `true` which introduces IfcAdvancedFace. It would
	// return `0` otherwise.
	IfcSchema::IfcProductDefinitionShape* building_shape = IfcGeom::serialise(building_shell, false);
	
	file.addEntity(building_shape);
	IfcSchema::IfcRepresentation* rep = *building_shape->Representations()->begin();
	rep->setContextOfItems(file.getRepresentationContext("model"));

	building->setRepresentation(building_shape);

	// A pale white colour is assigned to the building.
	file.setSurfaceColour(
		building_shape, 0.75, 0.73, 0.68);

	// For the ground mesh of the IfcSite we will use a Nurbs surface created in Open Cascade. Only
	// in IFC4 the surface can be directly serialized. In IFC2X3 the it will have to be tesselated.
	TopoDS_Shape shape;
	createGroundShape(shape);

	IfcSchema::IfcProductDefinitionShape* ground_representation = IfcGeom::serialise(shape, true);
	if (!ground_representation) {
		ground_representation = IfcGeom::tesselate(shape, 100.);
	}
	file.getSingle<IfcSchema::IfcSite>()->setRepresentation(ground_representation);
	
	IfcSchema::IfcRepresentation::list::ptr ground_reps = file.getSingle<IfcSchema::IfcSite>()->Representation()->Representations();
	for (IfcSchema::IfcRepresentation::list::it it = ground_reps->begin(); it != ground_reps->end(); ++it) {
		(*it)->setContextOfItems(file.getRepresentationContext("Model"));
	}
	file.addEntity(ground_representation);
	file.setSurfaceColour(ground_representation, 0.15, 0.25, 0.05);

    /*
    // Note that IFC lacks elementary surfaces that STEP does have, such as spherical_surface.
    // BRepBuilderAPI_NurbsConvert can be used to serialize such surfaces as nurbs surfaces.
	TopoDS_Shape sphere = BRepPrimAPI_MakeSphere(gp_Pnt(), 1000.).Shape();
	IfcSchema::IfcProductDefinitionShape* sphere_representation = IfcGeom::serialise(sphere, true);
	if (S(IfcSchema::Identifier) == "IFC4") {
		sphere = BRepBuilderAPI_NurbsConvert(sphere, true).Shape();
		sphere_representation = IfcGeom::serialise(sphere, true);
	}
    */

	// Finally create a file stream for our output and write the IFC file to it.
	std::ofstream f("IfcAdvancedHouse.ifc");
	f << file;
}

void createGroundShape(TopoDS_Shape& shape) {
	TColgp_Array2OfPnt cv (0, 4, 0, 4);
	cv.SetValue(0, 0, gp_Pnt(-10000, -10000, -4130));
	cv.SetValue(0, 1, gp_Pnt(-10000,  -4330, -4130));
	cv.SetValue(0, 2, gp_Pnt(-10000,      0, -5130));
	cv.SetValue(0, 3, gp_Pnt(-10000,   4330, -7130));
	cv.SetValue(0, 4, gp_Pnt(-10000,  10000, -7130));
	cv.SetValue(1, 0, gp_Pnt( -3330, -10000, -5130));
	cv.SetValue(1, 1, gp_Pnt( -7670,  -3670,  5000));
	cv.SetValue(1, 2, gp_Pnt( -9000,      0,  1000));
	cv.SetValue(1, 3, gp_Pnt( -7670,   7670,  6000));
	cv.SetValue(1, 4, gp_Pnt( -3330,  10000, -4130));
	cv.SetValue(2, 0, gp_Pnt(     0, -10000, -5530));
	cv.SetValue(2, 1, gp_Pnt(     0,  -3670,  3000));
	cv.SetValue(2, 2, gp_Pnt(     0,      0, -12000));
	cv.SetValue(2, 3, gp_Pnt(     0,   7670,  1500));
	cv.SetValue(2, 4, gp_Pnt(     0,  10000, -4130));
	cv.SetValue(3, 0, gp_Pnt(  3330, -10000, -6130));
	cv.SetValue(3, 1, gp_Pnt(  7670,  -3670,  6000));
	cv.SetValue(3, 2, gp_Pnt(  9000,      0,  5000));
	cv.SetValue(3, 3, gp_Pnt(  7670,   9000,  7000));
	cv.SetValue(3, 4, gp_Pnt(  3330,  10000, -4130));
	cv.SetValue(4, 0, gp_Pnt( 10000, -10000, -6130));
	cv.SetValue(4, 1, gp_Pnt( 10000,  -4330, -5130));
	cv.SetValue(4, 2, gp_Pnt( 10000,      0, -4130));
	cv.SetValue(4, 3, gp_Pnt( 10000,   4330, -4130));
	cv.SetValue(4, 4, gp_Pnt( 10000,  10000, -8130));
	TColStd_Array1OfReal knots(0, 1);
	knots(0) = 0;
	knots(1) = 1;		
	TColStd_Array1OfInteger mult(0, 1);
	mult(0) = 5;
	mult(1) = 5;	
	Handle(Geom_BSplineSurface) surf = new Geom_BSplineSurface(cv, knots, knots, mult, mult, 4, 4);
#if OCC_VERSION_HEX < 0x60502
	shape = BRepBuilderAPI_MakeFace(surf);
#else
	shape = BRepBuilderAPI_MakeFace(surf, Precision::Confusion());
#endif
}
