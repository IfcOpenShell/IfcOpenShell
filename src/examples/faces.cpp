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
 * Example that generates various forms of IfcFace                              *
 *                                                                              *
 ********************************************************************************/

#include "../ifcparse/Ifc2x3.h"
#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/IfcHierarchyHelper.h"

typedef std::string S;
typedef IfcParse::IfcGlobalId guid;
boost::none_t const null = (static_cast<boost::none_t>(0));

static int x = 0;

void create_testcase(IfcHierarchyHelper& file, IfcSchema::IfcFace* face, const std::string& name) {
	IfcSchema::IfcFace::list::ptr faces(new IfcSchema::IfcFace::list);
	faces->push(face);
	IfcSchema::IfcOpenShell* shell = new IfcSchema::IfcOpenShell(faces);

	IfcSchema::IfcConnectedFaceSet::list::ptr shells(new IfcSchema::IfcConnectedFaceSet::list);
	shells->push(shell);
	IfcSchema::IfcFaceBasedSurfaceModel* model = new IfcSchema::IfcFaceBasedSurfaceModel(shells);
	
	IfcSchema::IfcBuildingElementProxy* product = new IfcSchema::IfcBuildingElementProxy(
		guid(), 0, name, null, null, 0, 0, null, null);
	file.addBuildingProduct(product);
	product->setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());

	product->setObjectPlacement(file.addLocalPlacement(0, 1000 * x++, 0));

	IfcSchema::IfcRepresentation::list::ptr reps (new IfcSchema::IfcRepresentation::list);
	IfcSchema::IfcRepresentationItem::list::ptr items (new IfcSchema::IfcRepresentationItem::list);
		
	items->push(model);
	IfcSchema::IfcShapeRepresentation* rep = new IfcSchema::IfcShapeRepresentation(
		file.getRepresentationContext("Model"), S("Body"), S("SurfaceModel"), items);
	reps->push(rep);

	IfcSchema::IfcProductDefinitionShape* shape = new IfcSchema::IfcProductDefinitionShape(0, 0, reps);
	file.addEntity(shape);
		
	product->setRepresentation(shape);
}

int main(int argc, char** argv) {
	IfcHierarchyHelper file;
	{ 
		IfcSchema::IfcCartesianPoint::list::ptr points (new IfcSchema::IfcCartesianPoint::list);
		points->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(-400, -400, 0));
		points->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(+400, -400, 0));
		points->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(+400, +400, 0));
		points->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(-400, +400, 0));
		IfcSchema::IfcPolyLoop* loop = new IfcSchema::IfcPolyLoop(points);
		IfcSchema::IfcFaceOuterBound* bound = new IfcSchema::IfcFaceOuterBound(loop, true);
		
		IfcSchema::IfcFaceBound::list::ptr bounds (new IfcSchema::IfcFaceBound::list);
		bounds->push(bound);
		IfcSchema::IfcFace* face = new IfcSchema::IfcFace(bounds);
		create_testcase(file, face, "polyloop");
	}
	{ 
		IfcSchema::IfcCartesianPoint* point1 = file.addTriplet<IfcSchema::IfcCartesianPoint>(+400, 0., 0.);
		IfcSchema::IfcCartesianPoint* point2 = file.addTriplet<IfcSchema::IfcCartesianPoint>(-400, 0., 0.);
		IfcSchema::IfcVertexPoint* vertex1 = new IfcSchema::IfcVertexPoint(point1);
		IfcSchema::IfcVertexPoint* vertex2 = new IfcSchema::IfcVertexPoint(point2);
		IfcSchema::IfcCircle* circle = new IfcSchema::IfcCircle(file.addPlacement2d(), 400.);
		IfcSchema::IfcEdgeCurve* edge1 = new IfcSchema::IfcEdgeCurve(vertex1, vertex2, circle, true);
		IfcSchema::IfcEdgeCurve* edge2 = new IfcSchema::IfcEdgeCurve(vertex2, vertex1, circle, true);
		IfcSchema::IfcOrientedEdge* oriented_edge1 = new IfcSchema::IfcOrientedEdge(edge1, true);
		IfcSchema::IfcOrientedEdge* oriented_edge2 = new IfcSchema::IfcOrientedEdge(edge2, true);
		IfcSchema::IfcOrientedEdge::list::ptr edges(new IfcSchema::IfcOrientedEdge::list);
		edges->push(oriented_edge1);
		edges->push(oriented_edge2);
		IfcSchema::IfcEdgeLoop* loop = new IfcSchema::IfcEdgeLoop(edges);
		IfcSchema::IfcFaceOuterBound* bound = new IfcSchema::IfcFaceOuterBound(loop, true);
		
		IfcSchema::IfcFaceBound::list::ptr bounds (new IfcSchema::IfcFaceBound::list);
		bounds->push(bound);
		IfcSchema::IfcFace* face = new IfcSchema::IfcFace(bounds);
		create_testcase(file, face, "circle");
	}
	{ 
		IfcSchema::IfcCartesianPoint::list::ptr points (new IfcSchema::IfcCartesianPoint::list);
		points->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(-400, -400, 0));
		points->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(+400, -400, 0));
		points->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(+400, +400, 0));
		points->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(-400, +400, 0));
		IfcSchema::IfcPolyLoop* loop = new IfcSchema::IfcPolyLoop(points);
		IfcSchema::IfcFaceOuterBound* outer_bound = new IfcSchema::IfcFaceOuterBound(loop, true);

		IfcSchema::IfcCartesianPoint::list::ptr points2 (new IfcSchema::IfcCartesianPoint::list);
		points2->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(-300, -300, 0));
		points2->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(-100, -300, 0));
		points2->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(-100, +300, 0));
		points2->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(-300, +300, 0));
		IfcSchema::IfcPolyLoop* loop2 = new IfcSchema::IfcPolyLoop(points2);
		IfcSchema::IfcFaceBound* inner_bound1 = new IfcSchema::IfcFaceBound(loop2, false);

		IfcSchema::IfcCartesianPoint::list::ptr points3 (new IfcSchema::IfcCartesianPoint::list);
		points3->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(+100, +300, 0));
		points3->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(+300, +300, 0));
		points3->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(+300, -300, 0));
		points3->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(+100, -300, 0));
		IfcSchema::IfcPolyLoop* loop3 = new IfcSchema::IfcPolyLoop(points3);
		IfcSchema::IfcFaceBound* inner_bound2 = new IfcSchema::IfcFaceBound(loop3, true);
		
		IfcSchema::IfcFaceBound::list::ptr bounds (new IfcSchema::IfcFaceBound::list);
		bounds->push(inner_bound1);
		bounds->push(outer_bound);
		bounds->push(inner_bound2);
		IfcSchema::IfcFace* face = new IfcSchema::IfcFace(bounds);
		create_testcase(file, face, "polyloop with holes");
	}
	{ 
		IfcSchema::IfcCartesianPoint::list::ptr points (new IfcSchema::IfcCartesianPoint::list);
		points->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(-400, -400, 0));
		points->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(-100, -400, 0));
		points->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(-100, +400, 0));
		points->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(-400, +400, 0));
		IfcSchema::IfcPolyLoop* loop = new IfcSchema::IfcPolyLoop(points);
		IfcSchema::IfcFaceOuterBound* bound1 = new IfcSchema::IfcFaceOuterBound(loop, true);

		IfcSchema::IfcCartesianPoint::list::ptr points2 (new IfcSchema::IfcCartesianPoint::list);
		points2->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(+100, +400, 0));
		points2->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(+400, +400, 0));
		points2->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(+400, -400, 0));
		points2->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(+100, -400, 0));
		IfcSchema::IfcPolyLoop* loop2 = new IfcSchema::IfcPolyLoop(points2);
		IfcSchema::IfcFaceOuterBound* bound2 = new IfcSchema::IfcFaceOuterBound(loop2, false);

		IfcSchema::IfcFaceBound::list::ptr bounds (new IfcSchema::IfcFaceBound::list);
		bounds->push(bound1);
		bounds->push(bound2);
		IfcSchema::IfcFace* face = new IfcSchema::IfcFace(bounds);
		create_testcase(file, face, "multiple outer boundaries (invalid)");
	}
	{ 
		IfcSchema::IfcCartesianPoint::list::ptr points (new IfcSchema::IfcCartesianPoint::list);
		points->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(-400, -400, 1e-6));
		points->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(+400, -400, 0));
		points->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(+400, +400, 0));
		points->push(file.addTriplet<IfcSchema::IfcCartesianPoint>(-400, +400, 0));
		IfcSchema::IfcPolyLoop* loop = new IfcSchema::IfcPolyLoop(points);
		IfcSchema::IfcFaceOuterBound* bound = new IfcSchema::IfcFaceOuterBound(loop, true);
		
		IfcSchema::IfcFaceBound::list::ptr bounds (new IfcSchema::IfcFaceBound::list);
		bounds->push(bound);
		IfcSchema::IfcFace* face = new IfcSchema::IfcFace(bounds);
		create_testcase(file, face, "imprecise polyloop");
	}
	{ 
		IfcSchema::IfcCartesianPoint* point1 = file.addTriplet<IfcSchema::IfcCartesianPoint>(+400, 0., 0.);
		IfcSchema::IfcCartesianPoint* point2 = file.addTriplet<IfcSchema::IfcCartesianPoint>(-400, 0., 0.);
		IfcSchema::IfcVertexPoint* vertex1 = new IfcSchema::IfcVertexPoint(point1);
		IfcSchema::IfcVertexPoint* vertex2 = new IfcSchema::IfcVertexPoint(point2);
		IfcSchema::IfcCircle* circle = new IfcSchema::IfcCircle(file.addPlacement2d(), 400.);
		IfcSchema::IfcEdgeCurve* edge1 = new IfcSchema::IfcEdgeCurve(vertex1, vertex2, circle, true);
		IfcSchema::IfcEdgeCurve* edge2 = new IfcSchema::IfcEdgeCurve(vertex2, vertex1, circle, true);
		IfcSchema::IfcOrientedEdge* oriented_edge1 = new IfcSchema::IfcOrientedEdge(edge1, true);
		IfcSchema::IfcOrientedEdge* oriented_edge2 = new IfcSchema::IfcOrientedEdge(edge2, true);
		IfcSchema::IfcOrientedEdge::list::ptr edges(new IfcSchema::IfcOrientedEdge::list);
		edges->push(oriented_edge1);
		edges->push(oriented_edge2);
		IfcSchema::IfcEdgeLoop* loop = new IfcSchema::IfcEdgeLoop(edges);
		IfcSchema::IfcFaceOuterBound* bound = new IfcSchema::IfcFaceOuterBound(loop, true);
		
		IfcSchema::IfcFaceBound::list::ptr bounds (new IfcSchema::IfcFaceBound::list);
		bounds->push(bound);

		IfcSchema::IfcCartesianPoint::list::ptr trim1(new IfcSchema::IfcCartesianPoint::list);
		IfcSchema::IfcCartesianPoint::list::ptr trim2(new IfcSchema::IfcCartesianPoint::list);
		trim1->push(point1);
		trim2->push(point2);
		IfcSchema::IfcTrimmedCurve* trimmed_curve = new IfcSchema::IfcTrimmedCurve(circle, trim1->generalize(), trim2->generalize(), true, IfcSchema::IfcTrimmingPreference::IfcTrimmingPreference_CARTESIAN);
		IfcSchema::IfcArbitraryOpenProfileDef* profile = new IfcSchema::IfcArbitraryOpenProfileDef(IfcSchema::IfcProfileTypeEnum::IfcProfileType_CURVE, boost::none, trimmed_curve);
		IfcSchema::IfcAxis1Placement* place = new IfcSchema::IfcAxis1Placement(file.addTriplet<IfcSchema::IfcCartesianPoint>(0., 0., 0.), file.addTriplet<IfcSchema::IfcDirection>(1., 0., 0.));
		IfcSchema::IfcSurfaceOfRevolution* surface = new IfcSchema::IfcSurfaceOfRevolution(profile, file.addPlacement3d(), place);

		IfcSchema::IfcFace* face = new IfcSchema::IfcFaceSurface(bounds, surface, true);
		create_testcase(file, face, "face surface");
	}
	const std::string filename = "faces.ifc";
	file.header().file_name().name(filename);
	std::ofstream f(filename.c_str());
	f << file;
}