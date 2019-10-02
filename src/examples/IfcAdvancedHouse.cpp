//#ifdef USE_IFC4
#include "../ifcparse/Ifc4.h"
#define IfcSchema Ifc4
//#else
//#include "../ifcparse/Ifc2x3.h"
//#define IfcSchema Ifc2x3
//#endif

#include <iostream>
#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <gp_Dir.hxx>
#include <gp_Pnt2d.hxx>
#include <gp_Vec2d.hxx>
#include <gp_Dir2d.hxx>
#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include <gp_Ax1.hxx>
#include <gp_Ax3.hxx>
#include <gp_Ax2d.hxx>
#include <gp_Pln.hxx>
#include <gp_Circ.hxx>

#include <TColgp_Array1OfPnt.hxx>
#include <TColgp_Array1OfPnt2d.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>

#include <Geom_Line.hxx>
#include <Geom_Circle.hxx>
#include <Geom_Ellipse.hxx>
#include <Geom_TrimmedCurve.hxx>
#include <Geom_CylindricalSurface.hxx>

#include <BRepOffsetAPI_Sewing.hxx>
#include <BRepOffsetAPI_MakePipe.hxx>
#include <BRepOffsetAPI_MakePipeShell.hxx>

#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_MakeVertex.hxx>

#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <TopoDS_CompSolid.hxx>

#include <TopExp.hxx>
#include <TopExp_Explorer.hxx>

#include <BRepPrimAPI_MakePrism.hxx>
#include <BRepPrimAPI_MakeRevol.hxx>
#include <BRepPrimAPI_MakeBox.hxx>
#include <BRepPrimAPI_MakeCone.hxx>
#include <BRepPrimAPI_MakeCylinder.hxx>
#include <BRepPrimAPI_MakeSphere.hxx>
#include <BRepPrimAPI_MakeWedge.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>

#include <BRepBuilderAPI_Transform.hxx>
#include <BRepBuilderAPI_MakeShell.hxx>
#include <BRepBuilderAPI_MakeSolid.hxx>
#include <BRepPrimAPI_MakeHalfSpace.hxx>

#include <BRepAlgoAPI_Cut.hxx>
#include <BRepAlgoAPI_Fuse.hxx>
#include <BRepAlgoAPI_Common.hxx>

#include <ShapeFix_Shape.hxx>
#include <ShapeFix_ShapeTolerance.hxx>
#include <ShapeFix_Solid.hxx>

#include <TopLoc_Location.hxx>

#include <BRepCheck_Analyzer.hxx>
#include <BRepClass3d_SolidClassifier.hxx>

#include <Standard_Version.hxx>

#include <TopTools_ListIteratorOfListOfShape.hxx>

//#include "..\ifcgeom\IfcGeom.h"


#include "../ifcparse/IfcBaseClass.h"
#include "../ifcparse/IfcHierarchyHelper.h"
//#include "../ifcgeom/IfcGeom.h"
#include "../ifcgeom_schema_agnostic/Serialization.h"

#include "../ifcgeom_schema_agnostic/Kernel.h"

#if USE_VLD
#include <vld.h>
#endif

#include "../ifcparse/IfcSchema.h"
#include "../ifcgeom_schema_agnostic/IfcGeomIterator.h"
#include "../ifcgeom/IfcGeomElement.h"

#include "../ifcgeom/IfcRepresentationShapeItem.h"


//const GV_LENGTH_UNIT = 1;

int main() {
	/*std::cout << "Hdello DWorld";*/
	IfcParse::IfcFile f("C:/Users/jlutt/Desktop/Thomas/ifc_with_polygonalfaceset.ifc");

	//std::cout << "Hello DWorld";
	//std::cout << "LLLLLLLLLLLLLLLLLLLLLLL";

	IfcEntityList::ptr face_set_instances(new IfcEntityList());
	face_set_instances = f.instances_by_type("IfcPolygonalFaceSet");

	IfcSchema::IfcPolygonalFaceSet* pfs = (IfcSchema::IfcPolygonalFaceSet*)*face_set_instances->begin();
	IfcSchema::IfcCartesianPointList3D* point_list = pfs->Coordinates();
	const std::vector< std::vector<double> > coordinates = point_list->CoordList();
	/*std::cout << "Hdello DWorldd";*/
	std::vector<gp_Pnt> points;
	points.reserve(coordinates.size());
	for (std::vector< std::vector<double> >::const_iterator it = coordinates.begin(); it != coordinates.end(); ++it) {
		const std::vector<double>& coords = *it;
	/*	if (coords.size() != 4) {
			Logger::Message(Logger::LOG_ERROR, "Invalid dimensions encountered on Coordinates", pfs);
			return false;
		}*/
		points.push_back(gp_Pnt(coords[0], coords[1], coords[2]));
	}

	//std::cout << "BONJOUR";
	//std::vector<IfcSchema::IfcIndexedPolygonalFace*>polygonal_faces = pfs->Faces();;

	auto polygonal_faces = pfs->Faces();
	//std::vector<std::vector<int>> points; 
	int compt = 0;


	for (IfcSchema::IfcIndexedPolygonalFace* it = (IfcSchema::IfcIndexedPolygonalFace*)*polygonal_faces->begin(); it != (IfcSchema::IfcIndexedPolygonalFace*)*polygonal_faces->end(); ++it) {
		compt++;
	}
	std::cout << "compt"<<" "<<compt;

	
	
}











