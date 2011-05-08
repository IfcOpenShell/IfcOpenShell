#ifndef IFCGEOM_H
#define IFCGEOM_H
#include "../ifcparse/IfcParse.h"
#include "../ifcparse/IfcTypes.h"

#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <gp_Pnt2d.hxx>
#include <gp_Vec2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include <gp_Mat.hxx>
#include <gp_Ax3.hxx>
#include <gp_Ax2d.hxx>
#include <gp_Pln.hxx>

#include <TColgp_Array1OfPnt.hxx>
#include <TColgp_Array1OfPnt2d.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>
#include <Geom2d_BSplineCurve.hxx>
#include <Geom_BSplineCurve.hxx>

#include <BRepOffsetAPI_Sewing.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>

#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>

#include <BRepPrimAPI_MakePrism.hxx>
#include <BRepBuilderAPI_MakeShell.hxx>
#include <BRepBuilderAPI_MakeSolid.hxx>
#include <BRepPrimAPI_MakeHalfSpace.hxx>
#include <BRepAlgoAPI_Cut.hxx>

#include <ShapeFix_Shape.hxx>
#include <ShapeFix_ShapeTolerance.hxx>

#include <TopLoc_Location.hxx>

#define SCALE 1000.0f

/*
namespace IFCgeom {
	bool convert( Entity* L, gp_Vec*& CC );
	bool convert( Entity* L, gp_Pnt*& CC );
	bool convert( Entity* L, gp_Vec2d*& CC );
	bool convert( Entity* L, gp_Pnt2d*& CC );
	bool convert ( Entity* L, gp_Ax3*& ax3 );
	bool convert ( Entity* L, gp_Trsf*& trsf );
	bool convert ( Entity* L, gp_Trsf2d*& trsf );
	bool convert ( Entity* L, gp_Pln*& pln );
	bool convert ( const Entity* L, TopoDS_Wire& wire, int& count );
	bool convert( const Entity* L, TopoDS_Face& face);
	bool convert( const Entity* L, TopoDS_Shape& shape);
	bool move ( const Entity* L, gp_Trsf& trsf );
	bool move ( const Entity* L, TopoDS_Shape& shape );
	bool hasopenings( const Entity* L );
	bool open( const Entity* L, TopoDS_Shape& shape );
	bool open( const Entity* L, TopoDS_Shape& shape, gp_Trsf trsf2 );
}
*/
#endif