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
 * Implementations of the various conversion functions defined in IfcRegister.h *
 *                                                                              *
 ********************************************************************************/

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

#include "OpenCascadeKernel.h"

#include <memory>

#include "../../../ifcparse/IfcLogger.h"
#include "../../../ifcgeom/kernels/opencascade/OpenCascadeConversionResult.h"

using namespace ifcopenshell::geometry; 
using namespace ifcopenshell::geometry::kernels;


#include <TopTools_DataMapOfShapeInteger.hxx>
#include <Geom_Plane.hxx>
#include <BRepLib_FindSurface.hxx>
#include <ShapeFix_Edge.hxx>



#include <Geom_Curve.hxx>
#include <Geom_Line.hxx>
#include <Approx_Curve3d.hxx>
#include <BRepAdaptor_CompCurve.hxx>
#include <BRepAdaptor_HCompCurve.hxx>
#include <Approx_Curve3d.hxx>

#include <ShapeBuild_ReShape.hxx>
#include <GC_MakeCircle.hxx>




#include <BRepTools_WireExplorer.hxx>

bool OpenCascadeKernel::approximate_plane_through_wire(const TopoDS_Wire& wire, gp_Pln& plane, double eps) {
	// Newell's Method is used for the normal calculation
	// as a simple edge cross product can give opposite results
	// for a concave face boundary.
	// Reference: Graphics Gems III p. 231

	const double eps_ = eps < 1. ? precision_ : eps;
	const double eps2 = eps_ * eps_;

	double x = 0, y = 0, z = 0;
	gp_Pnt current, previous, first;
	gp_XYZ center;
	int n = 0;

	BRepTools_WireExplorer exp(wire);

	for (;; exp.Next()) {
		const bool has_more = exp.More() != 0;
		if (has_more) {
			const TopoDS_Vertex& v = exp.CurrentVertex();
			current = BRep_Tool::Pnt(v);
			center += current.XYZ();
		} else {
			current = first;
		}
		if (n) {
			const double& xn = previous.X();
			const double& yn = previous.Y();
			const double& zn = previous.Z();
			const double& xn1 = current.X();
			const double& yn1 = current.Y();
			const double& zn1 = current.Z();
			x += (yn - yn1)*(zn + zn1);
			y += (xn + xn1)*(zn - zn1);
			z += (xn - xn1)*(yn + yn1);
		} else {
			first = current;
		}
		if (!has_more) {
			break;
		}
		previous = current;
		++n;
	}

	if (n < 3) {
		return false;
	}

	plane = gp_Pln(center / n, gp_Dir(x, y, z));

	exp.Init(wire);
	for (; exp.More(); exp.Next()) {
		const TopoDS_Vertex& v = exp.CurrentVertex();
		current = BRep_Tool::Pnt(v);
		if (plane.SquareDistance(current) > eps2) {
			return false;
		}
	}

	return true;
}


bool OpenCascadeKernel::triangulate_wire(const std::vector<TopoDS_Wire>& wires, TopTools_ListOfShape& faces) {
	// This is a bit of a precarious approach, but seems to work for the 
	// versions of OCCT tested for. OCCT has a Delaunay triangulation function 
	// BRepMesh_Delaun, but it is notoriously hard to interpret the results 
	// (due to the Bowyer-Watson super triangle perhaps?). Therefore 
	// alternatively we use the regular OCCT incremental mesher on a new face 
	// created from the UV coordinates of the original wire. Pray to our gods 
	// that the vertex coordinates are unaffected by the meshing algorithm and 
	// map them back to 3d coordinates when iterating over the mesh triangles.

	// In addition, to maintain a manifold shell, we need to make sure that 
	// every edge from the input wire is used exactly once in the list of 
	// resulting faces. And that other internal edges are used twice.

	typedef std::pair<double, double> uv_node;

	gp_Pln pln;
	if (!approximate_plane_through_wire(wires.front(), pln, std::numeric_limits<double>::infinity())) {
		return false;
	}

	const gp_XYZ& udir = pln.Position().XDirection().XYZ();
	const gp_XYZ& vdir = pln.Position().YDirection().XYZ();
	const gp_XYZ& pnt = pln.Position().Location().XYZ();

	std::map<uv_node, TopoDS_Vertex> mapping;
	std::map<std::pair<uv_node, uv_node>, TopoDS_Edge> existing_edges, new_edges;

	std::unique_ptr<BRepBuilderAPI_MakeFace> mf;

	for (auto it = wires.begin(); it != wires.end(); ++it) {
		const TopoDS_Wire& wire = *it;
		BRepTools_WireExplorer exp(wire);
		BRepBuilderAPI_MakePolygon mp;

		// Add UV coordinates to a newly created polygon
		for (; exp.More(); exp.Next()) {
			// Project onto plane
			const TopoDS_Vertex& V = exp.CurrentVertex();
			gp_Pnt p = BRep_Tool::Pnt(V);
			double u = (p.XYZ() - pnt).Dot(udir);
			double v = (p.XYZ() - pnt).Dot(vdir);
			mp.Add(gp_Pnt(u, v, 0.));

			mapping.insert(std::make_pair(std::make_pair(u, v), V));

			// Store existing edges in a map so that triangles can
			// actually reference the preexisting edges.
			const TopoDS_Edge& e = exp.Current();
			TopoDS_Vertex V0, V1;
			TopExp::Vertices(e, V0, V1, true);
			gp_Pnt p0 = BRep_Tool::Pnt(V0);
			gp_Pnt p1 = BRep_Tool::Pnt(V1);
			double u0 = (p0.XYZ() - pnt).Dot(udir);
			double v0 = (p0.XYZ() - pnt).Dot(vdir);
			double u1 = (p1.XYZ() - pnt).Dot(udir);
			double v1 = (p1.XYZ() - pnt).Dot(vdir);
			uv_node uv0 = std::make_pair(u0, v0);
			uv_node uv1 = std::make_pair(u1, v1);
			existing_edges.insert(std::make_pair(std::make_pair(uv0, uv1), e));
			existing_edges.insert(std::make_pair(std::make_pair(uv1, uv0), TopoDS::Edge(e.Reversed())));
		}

		// Not closed by default
		mp.Close();

		if (mf) {
			if (it - 1 == wires.begin()) {
				// @todo is this necessary?
				TopoDS_Face f = mf->Face();
				mf->Init(f);
			}
			mf->Add(mp.Wire());
		} else {
			mf.reset(new BRepBuilderAPI_MakeFace(mp.Wire()));
		}
	}

	const TopoDS_Face& face = mf->Face();

	// Create a triangular mesh from the face
	BRepMesh_IncrementalMesh(face, Precision::Confusion());

	int n123[3];
	TopLoc_Location loc;
	Handle_Poly_Triangulation tri = BRep_Tool::Triangulation(face, loc);

	if (!tri.IsNull()) {
		const TColgp_Array1OfPnt& nodes = tri->Nodes();

		const Poly_Array1OfTriangle& triangles = tri->Triangles();
		for (int i = 1; i <= triangles.Length(); ++i) {
			if (face.Orientation() == TopAbs_REVERSED)
				triangles(i).Get(n123[2], n123[1], n123[0]);
			else triangles(i).Get(n123[0], n123[1], n123[2]);

			// Create polygons from the mesh vertices
			BRepBuilderAPI_MakeWire mp2;
			for (int j = 0; j < 3; ++j) {

				uv_node uvnodes[2];
				TopoDS_Vertex vs[2];

				for (int k = 0; k < 2; ++k) {
					const gp_Pnt& uv = nodes.Value(n123[(j + k) % 3]);
					uvnodes[k] = std::make_pair(uv.X(), uv.Y());

					auto it = mapping.find(uvnodes[k]);
					if (it == mapping.end()) {
						Logger::Error("Internal error: unable to unproject uv-mesh");
						return false;
					}

					vs[k] = it->second;
				}

				auto it = existing_edges.find(std::make_pair(uvnodes[0], uvnodes[1]));
				if (it != existing_edges.end()) {
					// This is a boundary edge, reuse existing edge from wire
					mp2.Add(it->second);
				} else {
					auto jt = new_edges.find(std::make_pair(uvnodes[0], uvnodes[1]));
					if (jt != new_edges.end()) {
						// We have already added the reverse as part of another
						// triangle, reuse this edge.
						mp2.Add(TopoDS::Edge(jt->second));
					} else {
						// This is a new internal edge. Register the reverse
						// for reuse later. We need to be sure to reuse vertices
						// for the edge construction because otherwise the wire
						// builder will use geometrical proximity for vertex
						// connections in which case the edge will be copied
						// and no longer partner with other edges from the shell.
						TopoDS_Edge ne = BRepBuilderAPI_MakeEdge(vs[0], vs[1]);
						mp2.Add(ne);
						// Store the reverse to be picked up later.
						new_edges.insert(std::make_pair(std::make_pair(uvnodes[1], uvnodes[0]), TopoDS::Edge(ne.Reversed())));
					}
				}
			}

			BRepBuilderAPI_MakeFace mft(mp2.Wire());
			if (mft.IsDone()) {
				TopoDS_Face triangle_face = mft.Face();
				TopoDS_Iterator jt(triangle_face, false);
				for (; jt.More(); jt.Next()) {
					const TopoDS_Wire& w = TopoDS::Wire(jt.Value());
					if (w.Orientation() != wires.front().Orientation()) {
						triangle_face.Reverse();
					}
				}
				faces.Append(triangle_face);
			} else {
				Logger::Error("Internal error: missing face");
				return false;
			}
		}
	}

	TopTools_IndexedDataMapOfShapeListOfShape mape, mapn;
	for (auto& wire : wires) {
		TopExp::MapShapesAndAncestors(wire, TopAbs_EDGE, TopAbs_WIRE, mape);
	}
	TopTools_ListIteratorOfListOfShape it(faces);
	for (; it.More(); it.Next()) {
		TopExp::MapShapesAndAncestors(it.Value(), TopAbs_EDGE, TopAbs_WIRE, mapn);
	}

	// Validation

	for (int i = 1; i <= mape.Extent(); ++i) {
#if OCC_VERSION_HEX >= 0x70000
		TopTools_ListOfShape val;
		if (!mapn.FindFromKey(mape.FindKey(i), val)) {
#else
		bool contains = false;
		try {
			TopTools_ListOfShape val = mapn.FindFromKey(mape.FindKey(i));
			contains = true;
		} catch (Standard_NoSuchObject&) {}
		if (!contains) {
#endif
			// All existing edges need to exist in the new faces
			Logger::Error("Internal error, missing edge from triangulation");
			if (faceset_helper_ != nullptr) {
				faceset_helper_->non_manifold() = true;
			}
		}
		}

	for (int i = 1; i <= mapn.Extent(); ++i) {
		const TopoDS_Shape& v = mapn.FindKey(i);
		int n = mapn.FindFromIndex(i).Extent();
		// Existing edges are boundaries with use 1
		// New edges are internal with use 2
		if (n != (mape.Contains(v) ? 1 : 2)) {
			Logger::Error("Internal error, non-manifold result from triangulation");
			if (faceset_helper_ != nullptr) {
				faceset_helper_->non_manifold() = true;
			}
		}
	}

	return true;
}

bool OpenCascadeKernel::convert(const taxonomy::shell* l, TopoDS_Shape& shape) {
	std::unique_ptr<faceset_helper> helper_scope;
	helper_scope.reset(new faceset_helper(this, l));

	auto faces = l->children_as<taxonomy::face>();
	double minimal_face_area = precision_ * precision_ * 0.5;

	double min_face_area = faceset_helper_
		? (faceset_helper_->epsilon() * faceset_helper_->epsilon() / 20.)
		: minimal_face_area;

	TopTools_ListOfShape face_list;
	for (auto& face : faces) {
		bool success = false;
		TopoDS_Face occ_face;

		try {
			success = convert(face, occ_face);
		} catch (const std::exception& e) {
			Logger::Error(e);
		} catch (const Standard_Failure& e) {
			if (e.GetMessageString() && strlen(e.GetMessageString())) {
				Logger::Error(e.GetMessageString());
			} else {
				Logger::Error("Unknown error creating face");
			}
		} catch (...) {
			Logger::Error("Unknown error creating face");
		}

		if (!success) {
			Logger::Message(Logger::LOG_WARNING, "Failed to convert face:", face->instance);
			continue;
		}

		if (occ_face.ShapeType() == TopAbs_COMPOUND) {
			TopoDS_Iterator face_it(occ_face, false);
			for (; face_it.More(); face_it.Next()) {
				if (face_it.Value().ShapeType() == TopAbs_FACE) {
					// This should really be the case. This is not asserted.
					const TopoDS_Face& triangle = TopoDS::Face(face_it.Value());
					if (face_area(triangle) > min_face_area) {
						face_list.Append(triangle);
					} else {
						Logger::Message(Logger::LOG_WARNING, "Degenerate face:", face->instance);
					}
				}
			}
		} else {
			if (face_area(occ_face) > min_face_area) {
				face_list.Append(occ_face);
			} else {
				Logger::Message(Logger::LOG_WARNING, "Degenerate face:", face->instance);
			}
		}
	}

	if (face_list.Extent() == 0) {
		return false;
	}

	// @todo
	/* face_list.Extent() > getValue(GV_MAX_FACES_TO_ORIENT) ||  */

	if (!create_solid_from_faces(face_list, shape)) {
		TopoDS_Compound compound;
		BRep_Builder builder;
		builder.MakeCompound(compound);

		TopTools_ListIteratorOfListOfShape face_iterator;
		for (face_iterator.Initialize(face_list); face_iterator.More(); face_iterator.Next()) {
			builder.Add(compound, face_iterator.Value());
		}
		shape = compound;
	}

	return true;
}

#include <BRepGProp.hxx>
#include <GProp_GProps.hxx>

double OpenCascadeKernel::shape_volume(const TopoDS_Shape& s) {
	GProp_GProps prop;
	BRepGProp::VolumeProperties(s, prop);
	return prop.Mass();
}

double OpenCascadeKernel::face_area(const TopoDS_Face& f) {
	GProp_GProps prop;
	BRepGProp::SurfaceProperties(f, prop);
	return prop.Mass();
}

bool OpenCascadeKernel::create_solid_from_compound(const TopoDS_Shape& compound, TopoDS_Shape& shape) {
	TopTools_ListOfShape face_list;
	TopExp_Explorer exp(compound, TopAbs_FACE);
	for (; exp.More(); exp.Next()) {
		TopoDS_Face face = TopoDS::Face(exp.Current());
		face_list.Append(face);
	}

	if (face_list.Extent() == 0) {
		return false;
	}

	return create_solid_from_faces(face_list, shape);
}

bool OpenCascadeKernel::create_solid_from_faces(const TopTools_ListOfShape& face_list, TopoDS_Shape& shape) {
	bool valid_shell = false;

	if (face_list.Extent() == 1) {
		shape = face_list.First();
		// A bit dubious what to return here.
		return true;
	} else if (face_list.Extent() == 0) {
		return false;
	}

	TopTools_ListIteratorOfListOfShape face_iterator;

	bool has_shared_edges = false;
	TopTools_MapOfShape edge_set;

	// In case there are wire interesections or failures in non-planar wire triangulations
	// the idea is to let occt do an exhaustive search of edge partners. But we have not
	// found a case where this actually improves boolean ops later on.
	// if (!faceset_helper_ || !faceset_helper_->non_manifold()) {

	for (face_iterator.Initialize(face_list); face_iterator.More(); face_iterator.Next()) {
		// As soon as is detected one of the edges is shared, the assumption is made no
		// additional sewing is necessary.
		if (!has_shared_edges) {
			TopExp_Explorer exp(face_iterator.Value(), TopAbs_EDGE);
			for (; exp.More(); exp.Next()) {
				if (edge_set.Contains(exp.Current())) {
					has_shared_edges = true;
					break;
				}
				edge_set.Add(exp.Current());
			}
		}
	}

	BRepOffsetAPI_Sewing sewing_builder;
	sewing_builder.SetTolerance(precision_);
	sewing_builder.SetMaxTolerance(precision_);
	sewing_builder.SetMinTolerance(precision_);

	BRep_Builder builder;
	TopoDS_Shell shell;
	builder.MakeShell(shell);

	for (face_iterator.Initialize(face_list); face_iterator.More(); face_iterator.Next()) {
		if (has_shared_edges) {
			builder.Add(shell, face_iterator.Value());
		} else {
			sewing_builder.Add(face_iterator.Value());
		}
	}

	try {
		if (has_shared_edges) {
			ShapeFix_Shell fix;
			fix.FixFaceOrientation(shell);
			shape = fix.Shape();
		} else {
			sewing_builder.Perform();
			shape = sewing_builder.SewedShape();
		}

		BRepCheck_Analyzer ana(shape);
		valid_shell = ana.IsValid();

		if (!valid_shell) {
			ShapeFix_Shape sfs(shape);
			sfs.Perform();
			shape = sfs.Shape();

			BRepCheck_Analyzer reana(shape);
			valid_shell = reana.IsValid();
		}

		valid_shell &= count(shape, TopAbs_SHELL) > 0;
	} catch (const Standard_Failure& e) {
		if (e.GetMessageString() && strlen(e.GetMessageString())) {
			Logger::Error(e.GetMessageString());
		} else {
			Logger::Error("Unknown error sewing shell");
		}
	} catch (...) {
		Logger::Error("Unknown error sewing shell");
	}

	if (valid_shell) {

		TopoDS_Shape complete_shape;
		TopExp_Explorer exp(shape, TopAbs_SHELL);

		for (; exp.More(); exp.Next()) {
			TopoDS_Shape result_shape = exp.Current();

			try {
				ShapeFix_Solid solid;
				solid.SetMaxTolerance(precision_);
				TopoDS_Solid solid_shape = solid.SolidFromShell(TopoDS::Shell(exp.Current()));
				// @todo: BRepClass3d_SolidClassifier::PerformInfinitePoint() is done by SolidFromShell
				//        and this is done again, to be able to catch errors during this process.
				//        This is double work that should be avoided.
				if (!solid_shape.IsNull()) {
					try {
						BRepClass3d_SolidClassifier classifier(solid_shape);
						result_shape = solid_shape;
						classifier.PerformInfinitePoint(precision_);
						if (classifier.State() == TopAbs_IN) {
							shape.Reverse();
						}
					} catch (const Standard_Failure& e) {
						if (e.GetMessageString() && strlen(e.GetMessageString())) {
							Logger::Error(e.GetMessageString());
						} else {
							Logger::Error("Unknown error classifying solid");
						}
					} catch (...) {
						Logger::Error("Unknown error classifying solid");
					}
				}
			} catch (const Standard_Failure& e) {
				if (e.GetMessageString() && strlen(e.GetMessageString())) {
					Logger::Error(e.GetMessageString());
				} else {
					Logger::Error("Unknown error creating solid");
				}
			} catch (...) {
				Logger::Error("Unknown error creating solid");
			}

			if (complete_shape.IsNull()) {
				complete_shape = result_shape;
			} else {
				BRep_Builder B;
				if (complete_shape.ShapeType() != TopAbs_COMPOUND) {
					TopoDS_Compound C;
					B.MakeCompound(C);
					B.Add(C, complete_shape);
					complete_shape = C;
					Logger::Warning("Multiple components in IfcConnectedFaceSet");
				}
				B.Add(complete_shape, result_shape);
			}
		}

		TopExp_Explorer loose_faces(shape, TopAbs_FACE, TopAbs_SHELL);

		for (; loose_faces.More(); loose_faces.Next()) {
			BRep_Builder B;
			if (complete_shape.ShapeType() != TopAbs_COMPOUND) {
				TopoDS_Compound C;
				B.MakeCompound(C);
				B.Add(C, complete_shape);
				complete_shape = C;
				Logger::Warning("Loose faces in IfcConnectedFaceSet");
			}
			B.Add(complete_shape, loose_faces.Current());
		}

		shape = complete_shape;

	} else {
		Logger::Error("Failed to sew faceset");
	}

	return valid_shell;
}

int OpenCascadeKernel::count(const TopoDS_Shape& s, TopAbs_ShapeEnum t, bool unique) {
	if (unique) {
		TopTools_IndexedMapOfShape map;
		TopExp::MapShapes(s, t, map);
		return map.Extent();
	} else {
		int i = 0;
		TopExp_Explorer exp(s, t);
		for (; exp.More(); exp.Next()) {
			++i;
		}
		return i;
	}
}

OpenCascadeKernel::faceset_helper::~faceset_helper() {
	kernel_->faceset_helper_ = nullptr;
}

#include "IfcGeomTree.h"

namespace {
	void find_neighbours(ifcopenshell::geometry::impl::tree<int>& tree, std::vector<std::unique_ptr<gp_Pnt>>& pnts, std::set<int>& visited, int p, double eps) {
		visited.insert(p);

		Bnd_Box b;
		b.Set(*pnts[p].get());
		b.Enlarge(eps);

		std::vector<int> js = tree.select_box(b, false);
		for (int j : js) {
			visited.insert(j);
#ifdef FACESET_HELPER_RECURSIVE
			if (visited.find(j) == visited.end()) {
				// @todo, making this recursive removes the dependence on the initial ordering, but will
				// likely result in empty results when all vertices are within 1 eps from another point.
				find_neighbours(tree, pnts, visited, j, eps);
			}
#endif
		}
	}
}

OpenCascadeKernel::faceset_helper::faceset_helper(OpenCascadeKernel* kernel, const taxonomy::shell* shell)
	: kernel_(kernel)
	, non_manifold_(false) {
	kernel->faceset_helper_ = this;

	// @todo use pointers?
	std::vector<taxonomy::point3> points;
	std::vector<taxonomy::loop*> loops;

	for (auto& f : shell->children_as<taxonomy::face>()) {
		for (auto& l : f->children_as<taxonomy::loop>()) {
			loops.push_back(l);
			for (auto& e : l->children_as<taxonomy::edge>()) {
				// @todo make sure only cartesian points are provided here
				points.push_back(boost::get<taxonomy::point3>(e->start));
			}
		}
	}
	
	std::vector<std::unique_ptr<gp_Pnt>> pnts(points.size());
	std::vector<TopoDS_Vertex> vertices(pnts.size());

	// @todo
	impl::tree<int> tree;

	BRep_Builder B;

	Bnd_Box box;
	for (size_t i = 0; i < points.size(); ++i) {
		gp_Pnt* p = new gp_Pnt(convert_xyz<gp_Pnt>(points[i]));
		pnts[i].reset(p);
		B.MakeVertex(vertices[i], *p, Precision::Confusion());
		tree.add(i, vertices[i]);
		box.Add(*p);
	}

	// Use the bbox diagonal to influence local epsilon
	// double bdiff = std::sqrt(box.SquareExtent());

	// @todo the bounding box diagonal is not used (see above)
	// because we're explicitly interested in the miminal
	// dimension of the element to limit the tolerance (for sheet-
	// like elements for example). But the way below is very
	// dependent on orientation due to the usage of the
	// axis-aligned bounding box. Use PCA to find three non-aligned
	// set of dimensions and use the one with the smallest eigenvalue.

	// Find the minimal bounding box edge
	double bmin[3], bmax[3];
	box.Get(bmin[0], bmin[1], bmin[2], bmax[0], bmax[1], bmax[2]);
	double bdiff = std::numeric_limits<double>::infinity();
	for (size_t i = 0; i < 3; ++i) {
		const double d = bmax[i] - bmin[i];
		if (d > kernel->precision_ * 10. && d < bdiff) {
			bdiff = d;
		}
	}

	eps_ = kernel->precision_ * 10. * (std::min)(1.0, bdiff);

	// @todo, there a tiny possibility that the duplicate faces are triggered
	// for an internal boundary, that is also present as an external boundary.
	// This will result in non-manifold configuration then, but this is deemed
	// such as corner-case that it is not considered.
	
	size_t loops_removed, non_manifold, duplicate_faces;

	std::map<std::pair<int, int>, int> edge_use;

	for (int i = 0; i < 3; ++i) {
		// Some times files, have large tolerance values specified collapsing too many vertices.
		// This case we detect below and re-run the loop with smaller epsilon. Normally
		// the body of this loop would only be executed once.

		loops_removed = 0;
		non_manifold = 0;
		duplicate_faces = 0;

		vertex_mapping_.clear();
		duplicates_.clear();

		edge_use.clear();

		if (eps_ < Precision::Confusion()) {
			// occt uses some hard coded precision values, don't go smaller than that.
			// @todo, can be reset though with BRepLib::Precision(double)
			eps_ = Precision::Confusion();
		}

		for (int i = 0; i < (int)pnts.size(); ++i) {
			if (pnts[i]) {
				std::set<int> vs;
				find_neighbours(tree, pnts, vs, i, eps_);

				for (int v : vs) {
					auto& pt = points[v];
					// NB: insert() ignores duplicate keys
					vertex_mapping_.insert({ pt.instance->data().id() , i });
				}
			}
		}

		typedef std::array<int, 2> edge_t;
		typedef std::set<edge_t> edge_set_t;
		std::set<edge_set_t> edge_sets;

		for (auto& loop : loops) {
			std::vector<std::pair<int, int> > segments;
			edge_set_t segment_set;

			loop_(loop, [&segments, &segment_set](int C, int D, bool) {
				segment_set.insert({ { C, D } });
				segments.push_back({ C, D });
			});

			if (edge_sets.find(segment_set) != edge_sets.end()) {
				duplicate_faces++;
				duplicates_.insert(loop->instance->data().id());
				continue;
			}
			edge_sets.insert(segment_set);

			if (segments.size() >= 3) {
				for (auto& p : segments) {
					edge_use[p] ++;
				}
			} else {
				loops_removed += 1;
			}
		}

		if (edge_use.size() != 0) {
			break;
		} else {
			eps_ /= 10.;
		}
	}

	for (auto& p : edge_use) {
		int a, b;
		std::tie(a, b) = p.first;
		edges_[p.first] = BRepBuilderAPI_MakeEdge(vertices[a], vertices[b]);

		if (p.second != 2) {
			non_manifold += 1;
		}
	}

	if (loops_removed || (non_manifold && shell->closed.get_value_or(false))) {
		Logger::Warning(boost::lexical_cast<std::string>(duplicate_faces) + " duplicate faces removed, " + boost::lexical_cast<std::string>(loops_removed) + " loops removed and " + boost::lexical_cast<std::string>(non_manifold) + " non-manifold edges for:", shell->instance);
	}
}

#include <ShapeUpgrade_UnifySameDomain.hxx>
#include <Extrema_ExtPC.hxx>
#include <BRepTopAdaptor_FClass2d.hxx>

namespace {
	void copy_operand(const TopTools_ListOfShape& l, TopTools_ListOfShape& r) {
#if OCC_VERSION_HEX < 0x70000
		TopTools_ListIteratorOfListOfShape it(l);
		for (; it.More(); it.Next()) {
			r.Append(BRepBuilderAPI_Copy(it.Value()));
		}
#else
		// On OCCT 7.0 and higher BRepAlgoAPI_BuilderAlgo::SetNonDestructive(true) is
		// called. Not entirely sure on the behaviour before 7.0, so overcautiously
		// create copies.
		r.Assign(l);
#endif
	}

	TopoDS_Shape copy_operand(const TopoDS_Shape& s) {
#if OCC_VERSION_HEX < 0x70000
		return BRepBuilderAPI_Copy(s);
#else
		return s;
#endif
	}

	double min_edge_length(const TopoDS_Shape& a) {
		double min_edge_len = std::numeric_limits<double>::infinity();
		TopExp_Explorer exp(a, TopAbs_EDGE);
		for (; exp.More(); exp.Next()) {
			GProp_GProps prop;
			BRepGProp::LinearProperties(exp.Current(), prop);
			double l = prop.Mass();
			if (l < min_edge_len) {
				min_edge_len = l;
			}
		}
		return min_edge_len;
	}

	double min_vertex_edge_distance(const TopoDS_Shape& a, double min_search, double max_search) {
		double M = std::numeric_limits<double>::infinity();

		TopTools_IndexedMapOfShape vertices, edges;

		TopExp::MapShapes(a, TopAbs_VERTEX, vertices);
		TopExp::MapShapes(a, TopAbs_EDGE, edges);

		impl::tree<int> tree;

		// Add edges to tree
		for (int i = 1; i <= edges.Extent(); ++i) {
			tree.add(i, edges(i));
		}

		for (int j = 1; j <= vertices.Extent(); ++j) {
			const TopoDS_Vertex& v = TopoDS::Vertex(vertices(j));
			gp_Pnt p = BRep_Tool::Pnt(v);

			Bnd_Box b;
			b.Add(p);
			b.Enlarge(max_search);

			std::vector<int> edge_idxs = tree.select_box(b, false);
			std::vector<int>::const_iterator it = edge_idxs.begin();
			for (; it != edge_idxs.end(); ++it) {
				const TopoDS_Edge& e = TopoDS::Edge(edges(*it));
				TopoDS_Vertex v1, v2;
				TopExp::Vertices(e, v1, v2);

				if (v.IsSame(v1) || v.IsSame(v2)) {
					continue;
				}

				BRepAdaptor_Curve crv(e);
				Extrema_ExtPC ext(p, crv);
				if (!ext.IsDone()) {
					continue;
				}

				for (int i = 1; i <= ext.NbExt(); ++i) {
					const double m = sqrt(ext.SquareDistance(i));
					if (m < M && m > min_search) {
						M = m;
					}
				}
			}
		}

		return M;
	}

	class points_on_planar_face_generator {
	private:
		const TopoDS_Face& f_;
		Handle(Geom_Surface) plane_;
		BRepTopAdaptor_FClass2d cls_;
		double u0, u1, v0, v1;
		int i, j;
		static const int N = 10;

	public:
		points_on_planar_face_generator(const TopoDS_Face& f)
			: f_(f)
			, plane_(BRep_Tool::Surface(f_))
			, cls_(f_, BRep_Tool::Tolerance(f_))
			, i(0), j(0) {
			BRepTools::UVBounds(f_, u0, u1, v0, v1);
		}

		void reset() {
			i = j = 0;
		}

		bool operator()(gp_Pnt& p) {
			while (j < N) {
				double u = u0 + (u1 - u0) * i / N;
				double v = v0 + (v1 - v0) * j / N;

				i++;
				if (i == N) {
					i = 0;
					j++;
				}

				// Specifically does not consider ON
				if (cls_.Perform(gp_Pnt2d(u, v)) == TopAbs_IN) {
					plane_->D0(u, v, p);
					return true;
				}
			}

			return false;
		}
	};

	double min_face_face_distance(const TopoDS_Shape& a, double max_search) {
		/*
		NB: This is currently only implemented for planar surfaces.
		*/
		double M = std::numeric_limits<double>::infinity();

		TopTools_IndexedMapOfShape faces;

		TopExp::MapShapes(a, TopAbs_FACE, faces);

		ifcopenshell::geometry::impl::tree<int> tree;

		// Add faces to tree
		for (int i = 1; i <= faces.Extent(); ++i) {
			if (BRep_Tool::Surface(TopoDS::Face(faces(i)))->DynamicType() == STANDARD_TYPE(Geom_Plane)) {
				tree.add(i, faces(i));
			}
		}

		for (int j = 1; j <= faces.Extent(); ++j) {
			const TopoDS_Face& f = TopoDS::Face(faces(j));
			const Handle(Geom_Surface)& fs = BRep_Tool::Surface(f);

			if (fs->DynamicType() != STANDARD_TYPE(Geom_Plane)) {
				continue;
			}

			points_on_planar_face_generator pgen(f);

			Bnd_Box b;
			BRepBndLib::AddClose(f, b);
			b.Enlarge(max_search);

			std::vector<int> face_idxs = tree.select_box(b, false);
			std::vector<int>::const_iterator it = face_idxs.begin();
			for (; it != face_idxs.end(); ++it) {
				if (*it == j) {
					continue;
				}

				const TopoDS_Face& g = TopoDS::Face(faces(*it));
				const Handle(Geom_Surface)& gs = BRep_Tool::Surface(g);

				auto p0 = Handle(Geom_Plane)::DownCast(fs);
				auto p1 = Handle(Geom_Plane)::DownCast(gs);

				if (p0->Position().IsCoplanar(p1->Position(), max_search, asin(max_search))) {
					pgen.reset();

					BRepTopAdaptor_FClass2d cls(g, BRep_Tool::Tolerance(g));

					gp_Pnt test;
					while (pgen(test)) {
						gp_Vec d = test.XYZ() - p1->Position().Location().XYZ();
						double u = d.Dot(p1->Position().XDirection());
						double v = d.Dot(p1->Position().YDirection());

						// nb: TopAbs_ON is explicitly not considered to prevent matching adjacent faces
						// with similar orientations.
						if (cls.Perform(gp_Pnt2d(u, v)) == TopAbs_IN) {
							gp_Pnt test2;
							p1->D0(u, v, test2);
							double w = gp_Vec(p1->Position().Direction().XYZ()).Dot(test2.XYZ() - test.XYZ());
							if (w < M) {
								M = w;
							}
						}
					}
				}
			}
		}

		return M;
	}

	void bounding_box_overlap(double p, const TopoDS_Shape& a, const TopTools_ListOfShape& b, TopTools_ListOfShape& c) {
		Bnd_Box A;
		BRepBndLib::Add(a, A);

		if (A.IsVoid()) {
			return;
		}

		TopTools_ListIteratorOfListOfShape it(b);
		for (; it.More(); it.Next()) {
			Bnd_Box B;
			BRepBndLib::Add(it.Value(), B);

			if (B.IsVoid()) {
				continue;
			}

			if (A.Distance(B) < p) {
				c.Append(it.Value());
			}
		}
	}

	TopoDS_Shape unify(const TopoDS_Shape& s, double tolerance) {
		tolerance = (std::min)(min_edge_length(s) / 2., tolerance);
		ShapeUpgrade_UnifySameDomain usd(s);
		usd.SetSafeInputMode(true);
		usd.SetLinearTolerance(tolerance);
		usd.SetAngularTolerance(1.e-3);
		usd.Build();
		return usd.Shape();
	}

	bool is_manifold_occt(const TopoDS_Shape& a) {
		if (a.ShapeType() == TopAbs_COMPOUND || a.ShapeType() == TopAbs_SOLID) {
			TopoDS_Iterator it(a);
			for (; it.More(); it.Next()) {
				if (!is_manifold_occt(it.Value())) {
					return false;
				}
			}
			return true;
		} else {
			TopTools_IndexedDataMapOfShapeListOfShape map;
			TopExp::MapShapesAndAncestors(a, TopAbs_EDGE, TopAbs_FACE, map);

			for (int i = 1; i <= map.Extent(); ++i) {
				if (map.FindFromIndex(i).Extent() != 2) {
					return false;
				}
			}

			return true;
		}
	}	
}

bool OpenCascadeKernel::boolean_operation(const TopoDS_Shape& a_, const TopTools_ListOfShape& b__, BOPAlgo_Operation op, TopoDS_Shape& result, double fuzziness) {

	if (fuzziness < 0.) {
		fuzziness = precision_;
	}

	// @todo, it does seem a bit odd, we first triangulate non-planar faces
	// to later unify them again. Can we make this a bit more intelligent?
	TopoDS_Shape a = unify(a_, fuzziness);
	TopTools_ListOfShape b_;
	{
		TopTools_ListIteratorOfListOfShape it(b__);
		for (; it.More(); it.Next()) {
			b_.Append(unify(it.Value(), fuzziness));
		}
	}

	bool success = false;
	BRepAlgoAPI_BooleanOperation* builder;
	TopTools_ListOfShape B, b;
	if (op == BOPAlgo_CUT) {
		builder = new BRepAlgoAPI_Cut();
		bounding_box_overlap(precision_, a, b_, b);
	} else if (op == BOPAlgo_COMMON) {
		builder = new BRepAlgoAPI_Common();
		b = b_;
	} else if (op == BOPAlgo_FUSE) {
		builder = new BRepAlgoAPI_Fuse();
		b = b_;
	} else {
		return false;
	}

	if (b.Extent() == 0) {
		result = a;
		return true;
	}

	// Find a sensible value for the fuzziness, based on precision
	// and limited by edge lengths and vertex-edge distances.
	const double len_a = min_edge_length(a_);
	double min_length_orig = (std::min)(len_a, min_vertex_edge_distance(a_, precision_, len_a));
	TopTools_ListIteratorOfListOfShape it(b__);
	for (; it.More(); it.Next()) {
		double d = min_edge_length(it.Value());
		if (d < min_length_orig) {
			min_length_orig = d;
		}
		d = min_vertex_edge_distance(it.Value(), precision_, d);
		if (d < min_length_orig) {
			min_length_orig = d;
		}
	}

	const double fuzz = (std::min)(min_length_orig / 3., fuzziness);

	TopTools_ListOfShape s1s;
	s1s.Append(copy_operand(a));
#if OCC_VERSION_HEX >= 0x70000
	builder->SetNonDestructive(true);
#endif
	builder->SetFuzzyValue(fuzz);
	builder->SetArguments(s1s);
	copy_operand(b, B);
	builder->SetTools(B);
	builder->Build();
	if (builder->IsDone()) {
		TopoDS_Shape r = *builder;

		ShapeFix_Shape fix(r);
		try {
			fix.SetMinTolerance(fuzz);
			fix.SetMaxTolerance(fuzz);
			fix.SetPrecision(fuzz);
			fix.Perform();
			r = fix.Shape();
		} catch (...) {
			Logger::Error("Shape healing failed on boolean result");
		}

		success = BRepCheck_Analyzer(r).IsValid() != 0;

		if (success) {

			success = !is_manifold_occt(a) || is_manifold_occt(r);

			if (success) {

				// when there are edges or vertex-edge distances close to the used fuzziness, the  
				// output is not trusted and the operation is attempted with a higher fuzziness.
				int reason = 0;
				double v;
				if ((v = min_edge_length(r)) < fuzziness * 3.) {
					reason = 0;
					success = false;
				} else if ((v = min_vertex_edge_distance(r, precision_, fuzziness * 3.)) < fuzziness * 3.) {
					reason = 1;
					success = false;
				} else if ((v = min_face_face_distance(r, fuzziness * 3.)) < fuzziness * 3.) {
					reason = 2;
					success = false;
				}

				if (success) {
					result = r;
				} else {
					static const char* const reason_strings[] = { "edge length", "vertex-edge", "face-face" };
					std::stringstream str;
					str << "Boolean operation result failing " << reason_strings[reason] << " interference check, with fuzziness " << fuzziness << " with length " << v;
					Logger::Notice(str.str());
				}
			} else {
				Logger::Notice("Boolean operation yields non-manifold result");
			}
		} else {
			Logger::Notice("Boolean operation yields invalid result");
		}
	} else {
		std::stringstream str;
#if OCC_VERSION_HEX >= 0x70000
		builder->DumpErrors(str);
#else
		str << "Error code: " << builder->ErrorStatus();
#endif
		std::string str_str = str.str();
		if (str_str.size()) {
			Logger::Notice(str_str);
		}
	}
	delete builder;
	if (!success) {
		const double new_fuzziness = fuzziness * 10.;
		if (new_fuzziness - 1e-15 <= precision_ * 10000. && new_fuzziness < min_length_orig) {
			return boolean_operation(a, b, op, result, new_fuzziness);
		} else {
			Logger::Notice("No longer attempting boolean operation with higher fuzziness");
		}
	}
	return success;
}

namespace {
	BOPAlgo_Operation op_to_occt(taxonomy::boolean_result::operation_t t) {
		switch (t) {
		case taxonomy::boolean_result::UNION: return BOPAlgo_FUSE;
		case taxonomy::boolean_result::INTERSECTION: return BOPAlgo_COMMON;
		case taxonomy::boolean_result::SUBTRACTION: return BOPAlgo_CUT;
		}
	}
}

bool OpenCascadeKernel::convert_impl(const taxonomy::boolean_result* br, ifcopenshell::geometry::ConversionResults& results) {
	bool first = true;

	TopoDS_Shape a;
	TopTools_ListOfShape b;

	taxonomy::style* first_item_style = nullptr;

	for (auto& c : br->children) {
		// AbstractKernel::convert(c, results);
		// continue;

		ifcopenshell::geometry::ConversionResults cr;
		// @todo half-space detection
		AbstractKernel::convert(c, cr);
		if (first && br->operation == taxonomy::boolean_result::SUBTRACTION) {
			// @todo A will be null on union/intersection, intended?
			flatten_shape_list(cr, a, false);
			first_item_style = ((taxonomy::geom_item*)c)->surface_style;
			if (!first_item_style && c->kind() == taxonomy::COLLECTION) {
				// @todo recursively right?
				first_item_style = ((taxonomy::geom_item*) ((taxonomy::collection*)c)->children[0])->surface_style;
			}
		} else {
			for (auto& r : cr) {
				auto S = ((OpenCascadeShape*)r.Shape())->shape();
				gp_GTrsf trsf;
				convert(&r.Placement(), trsf);
				// @todo it really confuses me why I cannot use Moved() here instead
				S.Location(S.Location() * trsf.Trsf());
				b.Append(S);
				/*results.emplace_back(ConversionResult(
					r.ItemId(),
					ifcopenshell::geometry::taxonomy::matrix4(),
					new OpenCascadeShape(S),
					r.Style()
				));*/
			}			
		}
		first = false;
	}

	TopoDS_Shape r;
	if (!boolean_operation(a, b, op_to_occt(br->operation), r)) {
		return false;
	}

	/*
	TopoDS_Compound r;
	BRep_Builder B;
	B.MakeCompound(r);
	B.Add(r, a);
	for (auto& bb : b) {
		B.Add(r, bb);
	}
	*/

	results.emplace_back(ConversionResult(
		br->instance->data().id(),
		br->matrix,
		new OpenCascadeShape(r),
		br->surface_style ? br->surface_style : first_item_style
	));
	return true;
}

bool OpenCascadeKernel::is_compound(const TopoDS_Shape& shape) {
	bool has_solids = TopExp_Explorer(shape, TopAbs_SOLID).More() != 0;
	bool has_shells = TopExp_Explorer(shape, TopAbs_SHELL).More() != 0;
	bool has_compounds = TopExp_Explorer(shape, TopAbs_COMPOUND).More() != 0;
	bool has_faces = TopExp_Explorer(shape, TopAbs_FACE).More() != 0;
	return has_compounds && has_faces && !has_solids && !has_shells;
}

const TopoDS_Shape& OpenCascadeKernel::ensure_fit_for_subtraction(const TopoDS_Shape& shape, TopoDS_Shape& solid) {
	const bool is_comp = is_compound(shape);
	if (!is_comp) {
		return solid = shape;
	}

	if (!create_solid_from_compound(shape, solid)) {
		return solid = shape;
	}

	return solid;
}

bool OpenCascadeKernel::flatten_shape_list(const ifcopenshell::geometry::ConversionResults& shapes, TopoDS_Shape& result, bool fuse) {
	TopoDS_Compound compound;
	BRep_Builder builder;
	builder.MakeCompound(compound);

	result = TopoDS_Shape();

	for (ifcopenshell::geometry::ConversionResults::const_iterator it = shapes.begin(); it != shapes.end(); ++it) {
		TopoDS_Shape merged;
		const TopoDS_Shape& s = *(OpenCascadeShape*)it->Shape();
		if (fuse) {
			ensure_fit_for_subtraction(s, merged);
		} else {
			merged = s;
		}
		const TopoDS_Shape moved_shape = apply_transformation(merged, it->Placement());

		if (shapes.size() == 1) {
			result = moved_shape;
			return true;
		}

		if (fuse) {
			if (result.IsNull()) {
				result = moved_shape;
			} else {
				BRepAlgoAPI_Fuse brep_fuse(result, moved_shape);
				if (brep_fuse.IsDone()) {
					TopoDS_Shape fused = brep_fuse;

					ShapeFix_Shape fix(result);
					fix.Perform();
					result = fix.Shape();

					bool is_valid = BRepCheck_Analyzer(result).IsValid() != 0;
					if (is_valid) {
						result = fused;
					}
				}
			}
		} else {
			builder.Add(compound, moved_shape);
		}
	}

	if (!fuse) {
		result = compound;
	}

	const bool success = !result.IsNull();
	return success;
}

TopoDS_Shape OpenCascadeKernel::apply_transformation(const TopoDS_Shape& s, const taxonomy::matrix4& t) {
	if (t.is_identity()) {
		return s;
	} else {
		gp_GTrsf trsf;
		convert(&t, trsf);
		return apply_transformation(s, trsf);
	}
}

#include <BRepBuilderAPI_GTransform.hxx>

TopoDS_Shape OpenCascadeKernel::apply_transformation(const TopoDS_Shape& s, const gp_GTrsf& t) {
	if (t.Form() == gp_Other) {
		Logger::Message(Logger::LOG_WARNING, "Applying non uniform transformation");
		return BRepBuilderAPI_GTransform(s, t, true);
	} else {
		return apply_transformation(s, t.Trsf());
	}
}

TopoDS_Shape OpenCascadeKernel::apply_transformation(const TopoDS_Shape& s, const gp_Trsf& t) {
	/// @todo set to 1. and exactly 1. or use epsilon?
	if (t.ScaleFactor() != 1.) {
		return BRepBuilderAPI_Transform(s, t, true);
	} else {
		return s.Moved(t);
	}
}

bool OpenCascadeKernel::convert_impl(const taxonomy::face* face, ifcopenshell::geometry::ConversionResults& results) {
	// Root level faces are only encountered in case of half spaces

	if (face->basis == nullptr) {
		Logger::Error("Half space without underlying surface:", face->instance);
		return false;
	}

	if (face->basis->kind() != taxonomy::PLANE) {
		Logger::Message(Logger::LOG_ERROR, "Unsupported BaseSurface:", face->basis->instance);
		return false;
	}

	// @todo boundary
	const auto& m = ((taxonomy::geom_item*)face->basis)->matrix.ccomponents();
	gp_Pln pln(convert_xyz2<gp_Pnt>(m.col(3)), convert_xyz2<gp_Dir>(m.col(2)));
	const gp_Pnt pnt = pln.Location().Translated(face->orientation.get_value_or(false) ? -pln.Axis().Direction() : pln.Axis().Direction());
	TopoDS_Shape shape = BRepPrimAPI_MakeHalfSpace(BRepBuilderAPI_MakeFace(pln), pnt).Solid();
	results.emplace_back(ConversionResult(
		face->instance->data().id(),
		new OpenCascadeShape(shape),
		face->surface_style
	));

	return true;
}
