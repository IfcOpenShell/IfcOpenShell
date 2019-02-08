﻿/********************************************************************************
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
 * Implementations of the various conversion functions defined in IfcGeom.h     *
 *                                                                              *
 ********************************************************************************/

#include <set>
#include <cassert>
#include <algorithm>

#include <Standard_Version.hxx>

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
#include <gp_Ax3.hxx>
#include <gp_Ax2d.hxx>
#include <gp_Pln.hxx>
#include <gp_Circ.hxx>

#include <boost/range/irange.hpp>
#include <boost/range/algorithm_ext/push_back.hpp>

#include <TColgp_Array1OfPnt.hxx>
#include <TColgp_Array1OfPnt2d.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>

#include <Geom_Line.hxx>
#include <Geom_Circle.hxx>
#include <Geom_Ellipse.hxx>
#include <Geom_TrimmedCurve.hxx>

#include <Geom_Plane.hxx>
#include <Geom_OffsetCurve.hxx>
#include <Geom_OffsetSurface.hxx>
#include <Geom_CylindricalSurface.hxx>
#include <Geom_SurfaceOfLinearExtrusion.hxx>

#include <GeomAPI_IntCS.hxx>
#include <GeomAPI_IntSS.hxx>

#include <BRepBndLib.hxx>
#include <BRepOffsetAPI_Sewing.hxx>
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
#include <BRepBuilderAPI_MakeShell.hxx>
#include <BRepBuilderAPI_MakeSolid.hxx>
#include <BRepPrimAPI_MakeHalfSpace.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepAlgoAPI_Fuse.hxx>
#include <BRepAlgoAPI_Common.hxx>
#include <BRepAlgoAPI_BooleanOperation.hxx>
#if OCC_VERSION_HEX >= 0x70200
#include <BRepAlgoAPI_Splitter.hxx>
#endif

#include <BRepAlgo_NormalProjection.hxx>

#include <ShapeFix_Shape.hxx>
#include <ShapeFix_ShapeTolerance.hxx>
#include <ShapeFix_Solid.hxx>

#include <ShapeAnalysis_Curve.hxx>
#include <ShapeAnalysis_Wire.hxx>
#include <ShapeAnalysis_Surface.hxx>
#include <ShapeAnalysis_ShapeTolerance.hxx>

#include <BRepFilletAPI_MakeFillet2d.hxx>

#include <TopLoc_Location.hxx>

#include <GProp_GProps.hxx>
#include <BRepGProp.hxx>

#include <BRepBuilderAPI_Copy.hxx>
#include <BRepBuilderAPI_Transform.hxx>
#include <BRepBuilderAPI_GTransform.hxx>

#include <BRepCheck_Analyzer.hxx>

#include <BRepGProp_Face.hxx>

#include <BRepMesh_IncrementalMesh.hxx>
#include <BRepTools.hxx>
#include <BRepTools_WireExplorer.hxx>

#include <Poly_Triangulation.hxx>
#include <Poly_Array1OfTriangle.hxx>

#include <TopTools_IndexedMapOfShape.hxx>
#include <TopTools_IndexedDataMapOfShapeListOfShape.hxx>
#include <TopTools_ListIteratorOfListOfShape.hxx>
#include <TopTools_HSequenceOfShape.hxx>

#include <BOPAlgo_PaveFiller.hxx>
#include <BOPAlgo_BOP.hxx>

#include <GCPnts_AbscissaPoint.hxx>

#include <BRepClass3d_SolidClassifier.hxx>

#include <GeomAPI_ExtremaCurveCurve.hxx>

#include <Extrema_ExtPC.hxx>
#include <BRepAdaptor_Curve.hxx>

#include "../ifcparse/IfcSIPrefix.h"
#include "../ifcparse/IfcFile.h"
#include "../ifcgeom/IfcGeom.h"
#include "../ifcgeom/IfcGeomTree.h"

#if OCC_VERSION_HEX < 0x60900
#ifdef _MSC_VER
#pragma message("warning: You are linking against Open CASCADE version " OCC_VERSION_COMPLETE ". Version 6.9.0 introduces various improvements with relation to boolean operations. You are advised to upgrade.")
#else
#warning "You are linking against linking against an older version of Open CASCADE. Version 6.9.0 introduces various improvements with relation to boolean operations. You are advised to upgrade."
#endif
#endif

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

		IfcGeom::impl::tree<int> tree;

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

	bool is_manifold(const TopoDS_Shape& a) {
		if (a.ShapeType() == TopAbs_COMPOUND || a.ShapeType() == TopAbs_SOLID) {
			TopoDS_Iterator it(a);
			for (; it.More(); it.Next()) {
				if (!is_manifold(it.Value())) {
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

	bool is_manifold(const TopTools_ListOfShape& l) {
		TopTools_ListOfShape r;
		TopTools_ListIteratorOfListOfShape it(l);
		for (; it.More(); it.Next()) {
			if (!is_manifold(it.Value())) {
				return false;
			}
		}
		return true;
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
}

bool IfcGeom::Kernel::create_solid_from_compound(const TopoDS_Shape& compound, TopoDS_Shape& shape) {
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

bool IfcGeom::Kernel::create_solid_from_faces(const TopTools_ListOfShape& face_list, TopoDS_Shape& shape) {
	bool valid_shell = false;
	

	int max_faces = getValue(GV_MAX_FACES_TO_SEW);
	if (max_faces == -1) {
		max_faces = 1000;
	}

	if (face_list.Extent() > max_faces) {
		throw too_many_faces_exception();
	}

	TopTools_ListIteratorOfListOfShape face_iterator;

	BRepOffsetAPI_Sewing builder;
	builder.SetTolerance(getValue(GV_PRECISION));
	builder.SetMaxTolerance(getValue(GV_PRECISION));
	builder.SetMinTolerance(getValue(GV_PRECISION));

	for (face_iterator.Initialize(face_list); face_iterator.More(); face_iterator.Next()) {
		builder.Add(face_iterator.Value());
	}

	try {
		builder.Perform();
		shape = builder.SewedShape();

		{
			BRepCheck_Analyzer ana(shape);
			if (!ana.IsValid()) {
				ShapeFix_Shape sfs(shape);
				sfs.Perform();
				shape = sfs.Shape();
			}
		}

		BRepCheck_Analyzer ana(shape);
		valid_shell = ana.IsValid() != 0 && count(shape, TopAbs_SHELL) > 0;
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
				solid.SetMaxTolerance(getValue(GV_PRECISION));
				TopoDS_Solid solid_shape = solid.SolidFromShell(TopoDS::Shell(exp.Current()));
				if (!solid_shape.IsNull()) {
					try {
						BRepClass3d_SolidClassifier classifier(solid_shape);
						result_shape = solid_shape;
						classifier.PerformInfinitePoint(getValue(GV_PRECISION));
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
					Logger::Message(Logger::LOG_ERROR, "Multiple components in IfcConnectedFaceSet");
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
				Logger::Message(Logger::LOG_ERROR, "Loose faces in IfcConnectedFaceSet");
			}
			B.Add(complete_shape, loose_faces.Current());
		}

		shape = complete_shape;

	} else {
		Logger::Message(Logger::LOG_WARNING, "Failed to sew faceset");
	}
	
	return valid_shell;
}

bool IfcGeom::Kernel::is_compound(const TopoDS_Shape& shape) {
	bool has_solids = TopExp_Explorer(shape,TopAbs_SOLID).More() != 0;
	bool has_shells = TopExp_Explorer(shape,TopAbs_SHELL).More() != 0;
	bool has_compounds = TopExp_Explorer(shape,TopAbs_COMPOUND).More() != 0;
	bool has_faces = TopExp_Explorer(shape,TopAbs_FACE).More() != 0;
	return has_compounds && has_faces && !has_solids && !has_shells;
}

const TopoDS_Shape& IfcGeom::Kernel::ensure_fit_for_subtraction(const TopoDS_Shape& shape, TopoDS_Shape& solid) {
	const bool is_comp = is_compound(shape);
	if (!is_comp) {
		return solid = shape;
	}
	
	if (!create_solid_from_compound(shape, solid)) {
		return solid = shape;
	}
	
	// If the SEW_SHELLS option had been set this precision had been applied
	// at the end of the generic convert_shape() call.
	const double precision = getValue(GV_PRECISION);
	apply_tolerance(solid, precision);
	
	return solid;
}

bool IfcGeom::Kernel::convert_openings(const IfcSchema::IfcProduct* entity, const IfcSchema::IfcRelVoidsElement::list::ptr& openings, 
							   const IfcGeom::IfcRepresentationShapeItems& entity_shapes, const gp_Trsf& entity_trsf, IfcGeom::IfcRepresentationShapeItems& cut_shapes) {

	// TODO: Refactor convert_openings() convert_openings_fast() and convert(IfcBooleanResult) to use
	// the same code base and conform to the same checks and logging messages.

	// Iterate over IfcOpeningElements
	IfcGeom::IfcRepresentationShapeItems opening_shapes;
	unsigned int last_size = 0;
	for ( IfcSchema::IfcRelVoidsElement::list::it it = openings->begin(); it != openings->end(); ++ it ) {
		IfcSchema::IfcRelVoidsElement* v = *it;
		IfcSchema::IfcFeatureElementSubtraction* fes = v->RelatedOpeningElement();
		if ( fes->is(IfcSchema::Type::IfcOpeningElement) ) {
			if (!fes->hasRepresentation()) continue;

			// Convert the IfcRepresentation of the IfcOpeningElement
			gp_Trsf opening_trsf;
			if (fes->hasObjectPlacement()) {
				try {
					convert(fes->ObjectPlacement(),opening_trsf);
				} catch (const std::exception& e) {
					Logger::Error(e);
				} catch (...) {
					Logger::Error("Failed to construct placement");
				}
			}

			// Move the opening into the coordinate system of the IfcProduct
			opening_trsf.PreMultiply(entity_trsf.Inverted());

			IfcSchema::IfcProductRepresentation* prodrep = fes->Representation();
			IfcSchema::IfcRepresentation::list::ptr reps = prodrep->Representations();
						
			for ( IfcSchema::IfcRepresentation::list::it it2 = reps->begin(); it2 != reps->end(); ++ it2 ) {
				convert_shapes(*it2,opening_shapes);
			}

			const unsigned int current_size = (const unsigned int) opening_shapes.size();
			for ( unsigned int i = last_size; i < current_size; ++ i ) {
				opening_shapes[i].prepend(opening_trsf);
			}
			last_size = current_size;
		}
	}

	// Iterate over the shapes of the IfcProduct
	for ( IfcGeom::IfcRepresentationShapeItems::const_iterator it3 = entity_shapes.begin(); it3 != entity_shapes.end(); ++ it3 ) {
		TopoDS_Shape entity_shape_solid;
		const TopoDS_Shape& entity_shape_unlocated = ensure_fit_for_subtraction(it3->Shape(),entity_shape_solid);
		const gp_GTrsf& entity_shape_gtrsf = it3->Placement();
		if ( entity_shape_gtrsf.Form() == gp_Other ) {
			Logger::Message(Logger::LOG_WARNING, "Applying non uniform transformation to:", entity->entity);
		}
		TopoDS_Shape entity_shape = apply_transformation(entity_shape_unlocated, entity_shape_gtrsf);

		// Iterate over the shapes of the IfcOpeningElements
		for ( IfcGeom::IfcRepresentationShapeItems::const_iterator it4 = opening_shapes.begin(); it4 != opening_shapes.end(); ++ it4 ) {
			TopoDS_Shape opening_shape_solid;
			const TopoDS_Shape& opening_shape_unlocated = ensure_fit_for_subtraction(it4->Shape(),opening_shape_solid);
			const gp_GTrsf& opening_shape_gtrsf = it4->Placement();
			if ( opening_shape_gtrsf.Form() == gp_Other ) {
				Logger::Message(Logger::LOG_WARNING,"Applying non uniform transformation to opening of:",entity->entity);
			}
			TopoDS_Shape opening_shape = apply_transformation(opening_shape_unlocated, opening_shape_gtrsf);
					
			double opening_volume;
			if (Logger::LOG_WARNING >= Logger::Verbosity()) {
				opening_volume = shape_volume(opening_shape);
				if ( opening_volume <= ALMOST_ZERO )
					Logger::Message(Logger::LOG_WARNING,"Empty opening for:",entity->entity);
			}

			if (entity_shape.ShapeType() == TopAbs_COMPSOLID) {

				// For compound solids process the subtraction for the constituent
				// solids individually and write the result back as a compound solid.

				TopoDS_CompSolid compound;
				BRep_Builder builder;
				builder.MakeCompSolid(compound);

				TopExp_Explorer exp(entity_shape, TopAbs_SOLID);

				for (; exp.More(); exp.Next()) {

#if OCC_VERSION_HEX < 0x60900
					BRepAlgoAPI_Cut brep_cut(exp.Current(), opening_shape);
#else
					BRepAlgoAPI_Cut brep_cut;
					TopTools_ListOfShape s1s;
					s1s.Append(exp.Current());
					TopTools_ListOfShape s2s;
					s2s.Append(opening_shape);
					brep_cut.SetFuzzyValue(getValue(GV_PRECISION));
					brep_cut.SetArguments(s1s);
					brep_cut.SetTools(s2s);
					brep_cut.Build();
#endif

					bool added = false;
					if ( brep_cut.IsDone() ) {
						TopoDS_Shape brep_cut_result = brep_cut;
						BRepCheck_Analyzer analyser(brep_cut_result);
						bool is_valid = analyser.IsValid() != 0;
						if (is_valid) {
							TopExp_Explorer exp2(brep_cut_result, TopAbs_SOLID);
							for (; exp2.More(); exp2.Next()) {
								builder.Add(compound, exp2.Current());
								added = true;
							}
						}
					}
					if (!added) {
						// Add the original in case subtraction fails
						builder.Add(compound, exp.Current());
					} else {
						Logger::Message(Logger::LOG_ERROR,"Failed to process subtraction:",entity->entity);
					}
				}

				entity_shape = compound;

			} else {
#if OCC_VERSION_HEX < 0x60900
				BRepAlgoAPI_Cut brep_cut(entity_shape,opening_shape);
#else
				BRepAlgoAPI_Cut brep_cut;
				TopTools_ListOfShape s1s;
				s1s.Append(entity_shape);
				TopTools_ListOfShape s2s;
				s2s.Append(opening_shape);
				brep_cut.SetFuzzyValue(getValue(GV_PRECISION));
				brep_cut.SetArguments(s1s);
				brep_cut.SetTools(s2s);
				brep_cut.Build();
#endif

				if ( brep_cut.IsDone() ) {
					TopoDS_Shape brep_cut_result = brep_cut;

					ShapeFix_Shape fix(brep_cut_result);
					try {
						fix.Perform();
						brep_cut_result = fix.Shape();
					} catch (...) {
						Logger::Message(Logger::LOG_WARNING, "Shape healing failed on opening subtraction result", entity->entity);
					}
					
					BRepCheck_Analyzer analyser(brep_cut_result);
					bool is_valid = analyser.IsValid() != 0;
					if ( is_valid ) {
						entity_shape = brep_cut_result;
						if (Logger::LOG_WARNING >= Logger::Verbosity()) {
							const double volume_after_subtraction = shape_volume(entity_shape);
							double original_shape_volume = shape_volume(entity_shape);
							if ( ALMOST_THE_SAME(original_shape_volume,volume_after_subtraction) )
								Logger::Message(Logger::LOG_WARNING,"Subtraction yields unchanged volume:",entity->entity);
						}
					} else {
						Logger::Message(Logger::LOG_ERROR,"Invalid result from subtraction:",entity->entity);
					}
				} else {
					Logger::Message(Logger::LOG_ERROR,"Failed to process subtraction:",entity->entity);
				}
			}

		}
		cut_shapes.push_back(IfcGeom::IfcRepresentationShapeItem(entity_shape, &it3->Style()));
	}

	return true;
}

#if OCC_VERSION_HEX < 0x60900
bool IfcGeom::Kernel::convert_openings_fast(const IfcSchema::IfcProduct* entity, const IfcSchema::IfcRelVoidsElement::list::ptr& openings, 
							   const IfcGeom::IfcRepresentationShapeItems& entity_shapes, const gp_Trsf& entity_trsf, IfcGeom::IfcRepresentationShapeItems& cut_shapes) {
	
	// Create a compound of all opening shapes in order to speed up the boolean operations
	TopoDS_Compound opening_compound;
	BRep_Builder builder;
	builder.MakeCompound(opening_compound);

	for ( IfcSchema::IfcRelVoidsElement::list::it it = openings->begin(); it != openings->end(); ++ it ) {
		IfcSchema::IfcRelVoidsElement* v = *it;
		IfcSchema::IfcFeatureElementSubtraction* fes = v->RelatedOpeningElement();
		if ( fes->is(IfcSchema::Type::IfcOpeningElement) ) {
			if (!fes->hasRepresentation()) continue;

			// Convert the IfcRepresentation of the IfcOpeningElement
			gp_Trsf opening_trsf;
			if (fes->hasObjectPlacement()) {
				try {
					convert(fes->ObjectPlacement(),opening_trsf);
				} catch (const std::exception& e) {
					Logger::Error(e);
				} catch (...) {
					Logger::Error("Failed to construct placement");
				}
			}

			// Move the opening into the coordinate system of the IfcProduct
			opening_trsf.PreMultiply(entity_trsf.Inverted());

			IfcSchema::IfcProductRepresentation* prodrep = fes->Representation();
			IfcSchema::IfcRepresentation::list::ptr reps = prodrep->Representations();

			IfcGeom::IfcRepresentationShapeItems opening_shapes;
						
			for ( IfcSchema::IfcRepresentation::list::it it2 = reps->begin(); it2 != reps->end(); ++ it2 ) {
				convert_shapes(*it2,opening_shapes);
			}

			for ( unsigned int i = 0; i < opening_shapes.size(); ++ i ) {
				gp_GTrsf gtrsf = opening_shapes[i].Placement();
				gtrsf.PreMultiply(opening_trsf);
				TopoDS_Shape opening_shape = apply_transformation(opening_shapes[i].Shape(), gtrsf);
				builder.Add(opening_compound, opening_shape);
			}

		}
	}

	// Iterate over the shapes of the IfcProduct
	for ( IfcGeom::IfcRepresentationShapeItems::const_iterator it3 = entity_shapes.begin(); it3 != entity_shapes.end(); ++ it3 ) {
		TopoDS_Shape entity_shape_solid;
		const TopoDS_Shape& entity_shape_unlocated = ensure_fit_for_subtraction(it3->Shape(),entity_shape_solid);
		const gp_GTrsf& entity_shape_gtrsf = it3->Placement();
		if (entity_shape_gtrsf.Form() == gp_Other) {
			Logger::Message(Logger::LOG_WARNING, "Applying non uniform transformation to:", entity->entity);
		}
		TopoDS_Shape entity_shape = apply_transformation(entity_shape_unlocated, entity_shape_gtrsf);

		BRepAlgoAPI_Cut brep_cut(entity_shape,opening_compound);

		bool is_valid = false;
		if ( brep_cut.IsDone() ) {
			TopoDS_Shape brep_cut_result = brep_cut;
				
			BRepCheck_Analyzer analyser(brep_cut_result);
			is_valid = analyser.IsValid() != 0;
			if ( is_valid ) {
				cut_shapes.push_back(IfcGeom::IfcRepresentationShapeItem(brep_cut_result, &it3->Style()));
			}
		}
		if ( !is_valid ) {
			// Apparently processing the boolean operation failed or resulted in an invalid result
			// in which case the original shape without the subtractions is returned instead
			// we try convert the openings in the original way, one by one.
			Logger::Message(Logger::LOG_WARNING,"Subtracting combined openings compound failed:",entity->entity);
			return false;
		}
		
	}
	return true;
}
#else

namespace {
	struct opening_sorter {
		bool operator()(const std::pair<double, TopoDS_Shape>& a, const std::pair<double, TopoDS_Shape>& b) const {
			return a.first > b.first;
		}
	};
}

bool IfcGeom::Kernel::convert_openings_fast(const IfcSchema::IfcProduct* entity, const IfcSchema::IfcRelVoidsElement::list::ptr& openings,
	const IfcGeom::IfcRepresentationShapeItems& entity_shapes, const gp_Trsf& entity_trsf, IfcGeom::IfcRepresentationShapeItems& cut_shapes) {

	std::vector< std::pair<double, TopoDS_Shape> > opening_vector;

	for (IfcSchema::IfcRelVoidsElement::list::it it = openings->begin(); it != openings->end(); ++it) {
		IfcSchema::IfcRelVoidsElement* v = *it;
		IfcSchema::IfcFeatureElementSubtraction* fes = v->RelatedOpeningElement();
		if (fes->is(IfcSchema::Type::IfcOpeningElement)) {
			if (!fes->hasRepresentation()) continue;

			// Convert the IfcRepresentation of the IfcOpeningElement
			gp_Trsf opening_trsf;
			if (fes->hasObjectPlacement()) {
				try {
					convert(fes->ObjectPlacement(), opening_trsf);
				} catch (const std::exception& e) {
					Logger::Error(e);
				} catch (...) {
					Logger::Error("Failed to construct placement");
				}
			}

			// Move the opening into the coordinate system of the IfcProduct
			opening_trsf.PreMultiply(entity_trsf.Inverted());

			IfcSchema::IfcProductRepresentation* prodrep = fes->Representation();
			IfcSchema::IfcRepresentation::list::ptr reps = prodrep->Representations();

			IfcGeom::IfcRepresentationShapeItems opening_shapes;

			for (IfcSchema::IfcRepresentation::list::it it2 = reps->begin(); it2 != reps->end(); ++it2) {
				convert_shapes(*it2, opening_shapes);
			}

			for (unsigned int i = 0; i < opening_shapes.size(); ++i) {
				TopoDS_Shape opening_shape_solid;
				const TopoDS_Shape& opening_shape_unlocated = ensure_fit_for_subtraction(opening_shapes[i].Shape(), opening_shape_solid);

				gp_GTrsf gtrsf = opening_shapes[i].Placement();
				gtrsf.PreMultiply(opening_trsf);
				TopoDS_Shape opening_shape = apply_transformation(opening_shape_unlocated, gtrsf);
				opening_vector.push_back(std::make_pair(min_edge_length(opening_shape), opening_shape));
			}

		}
	}

	std::sort(opening_vector.begin(), opening_vector.end(), opening_sorter());

	// Iterate over the shapes of the IfcProduct
	for ( IfcGeom::IfcRepresentationShapeItems::const_iterator it3 = entity_shapes.begin(); it3 != entity_shapes.end(); ++ it3 ) {
		TopoDS_Shape entity_shape_solid;
		const TopoDS_Shape& entity_shape_unlocated = ensure_fit_for_subtraction(it3->Shape(),entity_shape_solid);
		const gp_GTrsf& entity_shape_gtrsf = it3->Placement();
		if (entity_shape_gtrsf.Form() == gp_Other) {
			Logger::Message(Logger::LOG_WARNING, "Applying non uniform transformation to:", entity->entity);
		}
		TopoDS_Shape entity_shape = apply_transformation(entity_shape_unlocated, entity_shape_gtrsf);

		TopoDS_Shape result = entity_shape;
		
		auto it = opening_vector.begin();
		auto jt = it;

		for (;; ++it) {
			if (it == opening_vector.end() || jt->first / it->first > 10.) {

				TopTools_ListOfShape opening_list;
				for (auto kt = jt; kt < it; ++kt) {
					opening_list.Append(kt->second);
				}

				TopoDS_Shape intermediate_result;
				if (boolean_operation(result, opening_list, BOPAlgo_CUT, intermediate_result)) {
					result = intermediate_result;
				} else {
					Logger::Message(Logger::LOG_ERROR, "Opening subtraction failed for " + boost::lexical_cast<std::string>(std::distance(jt, it)) + " openings", entity->entity);
				}

				jt = it;
			}

			if (it == opening_vector.end()) {
				break;
			}
		}

		cut_shapes.push_back(IfcGeom::IfcRepresentationShapeItem(result, &it3->Style()));
	}
	return true;
}
#endif

bool IfcGeom::Kernel::convert_wire_to_face(const TopoDS_Wire& w, TopoDS_Face& face) {
	TopoDS_Wire wire = w;
	
	TopTools_ListOfShape results;
	if (wire_intersections(wire, results)) {
		Logger::Error("Self-intersections with " + boost::lexical_cast<std::string>(results.Extent()) + " cycles detected");
		select_largest(results, wire);
	}

	bool is_2d = true;
	TopExp_Explorer exp(wire, TopAbs_EDGE);
	for (; exp.More(); exp.Next()) {
		double a, b;
		Handle(Geom_Curve) crv = BRep_Tool::Curve(TopoDS::Edge(exp.Current()), a, b);
		if (crv->DynamicType() != STANDARD_TYPE(Geom_Line)) {
			is_2d = false;
			break;
		}
		Handle(Geom_Line) line = Handle(Geom_Line)::DownCast(crv);
		if (line->Lin().Direction().Z() > ALMOST_ZERO) {
			is_2d = false;
			break;
		}
	}

	if (!is_2d) {
		// For 2d wires (e.g. profiles) a higher tolerance for plane fitting is never required.
		ShapeFix_ShapeTolerance FTol;
		FTol.SetTolerance(wire, getValue(GV_PRECISION), TopAbs_WIRE);
	}

	BRepBuilderAPI_MakeFace mf(wire, false);
	BRepBuilderAPI_FaceError er = mf.Error();

	if (er != BRepBuilderAPI_FaceDone) {
		Logger::Error("Failed to create face.");
		return false;
	}
	face = mf.Face();
	
	return true;
}

void IfcGeom::Kernel::assert_closed_wire(TopoDS_Wire& wire) {
	if (wire.Closed() == 0) {
		TopoDS_Vertex v0, v1;
		TopExp::Vertices(wire, v0, v1);

		gp_Pnt p1 = BRep_Tool::Pnt(v0);
		gp_Pnt p2 = BRep_Tool::Pnt(v1);

		if (p1.Distance(p2) > getValue(GV_PRECISION)) {

			BRepBuilderAPI_MakeWire mw;
			mw.Add(wire);
			mw.Add(BRepBuilderAPI_MakeEdge(v0, v1).Edge());
			wire = mw.Wire();

		}

		Logger::Warning("Wire not closed:");
	}
}

bool IfcGeom::Kernel::convert_curve_to_wire(const Handle(Geom_Curve)& curve, TopoDS_Wire& wire) {
	try {
		wire = BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(curve));
		return true;
	} catch (const Standard_Failure& e) {
		if (e.GetMessageString() && strlen(e.GetMessageString())) {
			Logger::Error(e.GetMessageString());
		} else {
			Logger::Error("Unknown error converting curve to wire");
		}
	} catch (...) {
		Logger::Error("Unknown error converting curve to wire");
	}
	return false;
}

bool IfcGeom::Kernel::profile_helper(int numVerts, double* verts, int numFillets, int* filletIndices, double* filletRadii, gp_Trsf2d trsf, TopoDS_Shape& face_shape) {
	TopoDS_Vertex* vertices = new TopoDS_Vertex[numVerts];
	
	for ( int i = 0; i < numVerts; i ++ ) {
		gp_XY xy (verts[2*i],verts[2*i+1]);
		trsf.Transforms(xy);
		vertices[i] = BRepBuilderAPI_MakeVertex(gp_Pnt(xy.X(),xy.Y(),0.0f));
	}

	BRepBuilderAPI_MakeWire w;
	for ( int i = 0; i < numVerts; i ++ )
		w.Add(BRepBuilderAPI_MakeEdge(vertices[i],vertices[(i+1)%numVerts]));

	TopoDS_Face face;
	convert_wire_to_face(w.Wire(),face);

	if ( numFillets && *std::max_element(filletRadii, filletRadii + numFillets) > ALMOST_ZERO ) {
		BRepFilletAPI_MakeFillet2d fillet (face);
		for ( int i = 0; i < numFillets; i ++ ) {
			const double radius = filletRadii[i];
			if ( radius <= ALMOST_ZERO ) continue;
			fillet.AddFillet(vertices[filletIndices[i]],radius);
		}
		fillet.Build();
		if (fillet.IsDone()) {
			face = TopoDS::Face(fillet.Shape());
		} else {
			Logger::Message(Logger::LOG_WARNING, "Failed to process profile fillets");
		}
	}

	face_shape = face;

	delete[] vertices;
	return true;
}
double IfcGeom::Kernel::shape_volume(const TopoDS_Shape& s) {
	GProp_GProps prop;
	BRepGProp::VolumeProperties(s, prop);
	return prop.Mass();
}
double IfcGeom::Kernel::face_area(const TopoDS_Face& f) {
	GProp_GProps prop;
	BRepGProp::SurfaceProperties(f,prop);
	return prop.Mass();
}
bool IfcGeom::Kernel::is_convex(const TopoDS_Wire& wire) {
	for ( TopExp_Explorer exp1(wire,TopAbs_VERTEX); exp1.More(); exp1.Next() ) {
		TopoDS_Vertex V1 = TopoDS::Vertex(exp1.Current());
		gp_Pnt P1 = BRep_Tool::Pnt(V1);
		// Store the neighboring points
		std::vector<gp_Pnt> neighbors;
		for ( TopExp_Explorer exp3(wire,TopAbs_EDGE); exp3.More(); exp3.Next() ) {
			TopoDS_Edge edge = TopoDS::Edge(exp3.Current());
			std::vector<gp_Pnt> edge_points;
			for ( TopExp_Explorer exp2(edge,TopAbs_VERTEX); exp2.More(); exp2.Next() ) {
				TopoDS_Vertex V2 = TopoDS::Vertex(exp2.Current());
				gp_Pnt P2 = BRep_Tool::Pnt(V2);
				edge_points.push_back(P2);
			}
			if ( edge_points.size() != 2 ) continue;
			if ( edge_points[0].IsEqual(P1,getValue(GV_POINT_EQUALITY_TOLERANCE))) neighbors.push_back(edge_points[1]);
			else if ( edge_points[1].IsEqual(P1, getValue(GV_POINT_EQUALITY_TOLERANCE))) neighbors.push_back(edge_points[0]);
		}
		// There should be two of these
		if ( neighbors.size() != 2 ) return false;
		// Now find the non neighboring points
		std::vector<gp_Pnt> non_neighbors;
		for ( TopExp_Explorer exp2(wire,TopAbs_VERTEX); exp2.More(); exp2.Next() ) {
			TopoDS_Vertex V2 = TopoDS::Vertex(exp2.Current());
			gp_Pnt P2 = BRep_Tool::Pnt(V2);
			if ( P1.IsEqual(P2,getValue(GV_POINT_EQUALITY_TOLERANCE)) ) continue;
			bool found = false;
			for( std::vector<gp_Pnt>::const_iterator it = neighbors.begin(); it != neighbors.end(); ++ it ) {
				if ( (*it).IsEqual(P2,getValue(GV_POINT_EQUALITY_TOLERANCE)) ) { found = true; break; }
			}
			if ( ! found ) non_neighbors.push_back(P2);
		}
		// Calculate the angle between the two edges of the vertex
		gp_Dir dir1(neighbors[0].XYZ() - P1.XYZ());
		gp_Dir dir2(neighbors[1].XYZ() - P1.XYZ());
		const double angle = acos(dir1.Dot(dir2)) + 0.0001;
		// Now for the non-neighbors see whether a greater angle can be found with one of the edges
		for ( std::vector<gp_Pnt>::const_iterator it = non_neighbors.begin(); it != non_neighbors.end(); ++ it ) {
			gp_Dir dir3((*it).XYZ() - P1.XYZ());
			const double angle2 = acos(dir3.Dot(dir1));
			const double angle3 = acos(dir3.Dot(dir2));
			if ( angle2 > angle || angle3 > angle ) return false;
		}
	}
	return true;
}
TopoDS_Shape IfcGeom::Kernel::halfspace_from_plane(const gp_Pln& pln,const gp_Pnt& cent) {
	TopoDS_Face face = BRepBuilderAPI_MakeFace(pln).Face();
	return BRepPrimAPI_MakeHalfSpace(face,cent).Solid();
}
gp_Pln IfcGeom::Kernel::plane_from_face(const TopoDS_Face& face) {
	BRepGProp_Face prop(face);
	Standard_Real u1,u2,v1,v2;
	prop.Bounds(u1,u2,v1,v2);
	Standard_Real u = (u1+u2)/2.0;
	Standard_Real v = (v1+v2)/2.0;
	gp_Pnt p;
	gp_Vec n;
	prop.Normal(u,v,p,n);
	return gp_Pln(p,n);
}
gp_Pnt IfcGeom::Kernel::point_above_plane(const gp_Pln& pln, bool agree) {
	if ( agree ) {
		return pln.Location().Translated(pln.Axis().Direction());
	} else {
		return pln.Location().Translated(-pln.Axis().Direction());
	}
}

void IfcGeom::Kernel::apply_tolerance(TopoDS_Shape& s, double t) {
	/*
	// This does not result in actionable error messages and has been disabled.
	ShapeAnalysis_ShapeTolerance toler;
	if (Logger::LOG_WARNING >= Logger::Verbosity()) {
		if (toler.Tolerance(s, 0) > t * 10.) {
			Handle_TopTools_HSequenceOfShape shapes = toler.OverTolerance(s, t * 10.);
			for (int i = 1; i <= shapes->Length(); ++i) {
				const TopoDS_Shape& sub = shapes->Value(i);
				std::stringstream ss;
				TopAbs::Print(sub.ShapeType(), ss);
				Logger::Warning("Tolerance of " + boost::lexical_cast<std::string>(toler.Tolerance(sub, 0)) + " on " + ss.str());
			}
		}
	}
	*/

#if OCC_VERSION_HEX < 0x60900
	// This tolerance hack is not required as the boolean ops use a fuzziness value

	ShapeFix_ShapeTolerance tol;
	tol.LimitTolerance(s, t);
#else
	(void)s;
	(void)t;
#endif
}

void IfcGeom::Kernel::setValue(GeomValue var, double value) {
	switch (var) {
	case GV_DEFLECTION_TOLERANCE:
		deflection_tolerance = value;
		break;
	case GV_WIRE_CREATION_TOLERANCE:
		wire_creation_tolerance = value;
		break;
	case GV_POINT_EQUALITY_TOLERANCE:
		point_equality_tolerance = value;
		break;
	case GV_MAX_FACES_TO_SEW:
		max_faces_to_sew = value;
		break;
	case GV_LENGTH_UNIT:
		ifc_length_unit = value;
		break;
	case GV_PLANEANGLE_UNIT:
		ifc_planeangle_unit = value;
		break;
	case GV_PRECISION:
		modelling_precision = value;
		break;
	case GV_DIMENSIONALITY:
		dimensionality = value;
		break;
	default:
		assert(!"never reach here");
	}
}

double IfcGeom::Kernel::getValue(GeomValue var) const {
	switch (var) {
	case GV_DEFLECTION_TOLERANCE:
		return deflection_tolerance;
	case GV_WIRE_CREATION_TOLERANCE:
		return wire_creation_tolerance;
	case GV_MINIMAL_FACE_AREA:
		// Considering a right-angled triangle, this about the smallest
		// area you can obtain without the vertices being confused.
		return modelling_precision * modelling_precision / 2.;
	case GV_POINT_EQUALITY_TOLERANCE:
		return point_equality_tolerance;
	case GV_MAX_FACES_TO_SEW:
		return max_faces_to_sew;
	case GV_LENGTH_UNIT:
		return ifc_length_unit;
		break;
	case GV_PLANEANGLE_UNIT:
		return ifc_planeangle_unit;
		break;
	case GV_PRECISION:
		return modelling_precision;
		break;
	case GV_DIMENSIONALITY:
		return dimensionality;
		break;
	}
	assert(!"never reach here");
	return 0;
}

// Returns the vertex part of an TopoDS_Edge edge that is not TopoDS_Vertex vertex
TopoDS_Vertex find_other(const TopoDS_Edge& edge, const TopoDS_Vertex& vertex) {
	TopExp_Explorer exp(edge, TopAbs_VERTEX);
	while (exp.More()) {
		if (!exp.Current().IsSame(vertex)) {
			return TopoDS::Vertex(exp.Current());
		}
		exp.Next();
	}
	return TopoDS_Vertex();
}

TopoDS_Edge find_next(const TopTools_IndexedMapOfShape& edge_set, const TopTools_IndexedDataMapOfShapeListOfShape& vertex_to_edges, const TopoDS_Vertex& current, const TopoDS_Edge& previous_edge) {
	const TopTools_ListOfShape& edges = vertex_to_edges.FindFromKey(current);
	TopTools_ListIteratorOfListOfShape eit;
	for (eit.Initialize(edges); eit.More(); eit.Next()) {
		const TopoDS_Edge& edge = TopoDS::Edge(eit.Value());
		if (edge.IsSame(previous_edge)) continue;
		if (edge_set.Contains(edge)) {
			return edge;
		}
	}
	return TopoDS_Edge();
}

bool IfcGeom::Kernel::fill_nonmanifold_wires_with_planar_faces(TopoDS_Shape& shape) {
	BRepOffsetAPI_Sewing sew;
	sew.Add(shape);

	TopTools_IndexedDataMapOfShapeListOfShape edge_to_faces;
	TopTools_IndexedDataMapOfShapeListOfShape vertex_to_edges;
	std::set<int> visited;
	TopTools_IndexedMapOfShape edge_set;

	TopExp::MapShapesAndAncestors (shape, TopAbs_EDGE, TopAbs_FACE, edge_to_faces);

	const int num_edges = edge_to_faces.Extent();
	for (int i = 1; i <= num_edges; ++i) {
		const TopTools_ListOfShape& faces = edge_to_faces.FindFromIndex(i);
		const int count = faces.Extent();
		// Find only the non-manifold edges: Edges that are only part of a
		// single face and therefore part of the wire(s) we want to fill.
		if (count == 1) {
			const TopoDS_Shape& edge = edge_to_faces.FindKey(i);
			TopExp::MapShapesAndAncestors (edge, TopAbs_VERTEX, TopAbs_EDGE, vertex_to_edges);
			edge_set.Add(edge);
		}
	}

	const int num_verts = vertex_to_edges.Extent();
	TopoDS_Vertex first, current;
	TopoDS_Edge previous_edge;

	// Now loop over all the vertices that are part of the wire(s) to be filled
	for (int i = 1; i <= num_verts; ++i) {
		first = current = TopoDS::Vertex(vertex_to_edges.FindKey(i));
		// We keep track of the vertices we already used
		if (visited.find(vertex_to_edges.FindIndex(current)) != visited.end()) {
			continue;
		}
		// Given these vertices, try to find closed loops and create new
		// wires out of them.
		BRepBuilderAPI_MakeWire w;
		for (;;) {
			visited.insert(vertex_to_edges.FindIndex(current));
			// Find the edge that the current vertex is part of and points
			// away from the previous vertex (null for the first vertex).
			TopoDS_Edge edge = find_next(edge_set, vertex_to_edges, current, previous_edge);
			if (edge.IsNull()) {
				return false;
			}
			TopoDS_Vertex other = find_other(edge, current);
			if (other.IsNull()) {
				// Dealing with a conical edge probably, for some reason
				// this works better than adding the edge directly.
				double u1, u2;
				Handle(Geom_Curve) crv = BRep_Tool::Curve(edge, u1, u2);
				w.Add(BRepBuilderAPI_MakeEdge(crv, u1, u2));
				break;
			} else {
				w.Add(edge);
			}
			// See if the starting point of this loop has been reached. Note that
			// additional wires after this one potentially will be created.
			if (other.IsSame(first)) {
				break;
			}
			previous_edge = edge;
			current = other;
		}
		sew.Add(BRepBuilderAPI_MakeFace(w));
		previous_edge.Nullify();
	}
		
	sew.Perform();
	shape = sew.SewedShape();

	try {
		ShapeFix_Solid solid;
		solid.LimitTolerance(getValue(GV_POINT_EQUALITY_TOLERANCE));
		shape = solid.SolidFromShell(TopoDS::Shell(shape));
	} catch (const Standard_Failure& e) {
		if (e.GetMessageString() && strlen(e.GetMessageString())) {
			Logger::Error(e.GetMessageString());
		} else {
			Logger::Error("Unknown error creating solid");
		}
	} catch (...) {
		Logger::Error("Unknown error creating solid");
	}

	return true;
}

bool IfcGeom::Kernel::flatten_shape_list(const IfcGeom::IfcRepresentationShapeItems& shapes, TopoDS_Shape& result, bool fuse) {
	TopoDS_Compound compound;
	BRep_Builder builder;
	builder.MakeCompound(compound);

	result = TopoDS_Shape();
			
	for ( IfcGeom::IfcRepresentationShapeItems::const_iterator it = shapes.begin(); it != shapes.end(); ++ it ) {
		TopoDS_Shape merged;
		const TopoDS_Shape& s = it->Shape();
		if (fuse) {
			ensure_fit_for_subtraction(s, merged);
		} else {
			merged = s;
		}
		const gp_GTrsf& trsf = it->Placement();
		const TopoDS_Shape moved_shape = apply_transformation(merged, trsf);

		if (shapes.size() == 1) {
			result = moved_shape;
			const double precision = getValue(GV_PRECISION);
			apply_tolerance(result, precision);
			return true;
		}

		if (fuse) {
			if (result.IsNull()) {
				result = moved_shape;
			} else {
				BRepAlgoAPI_Fuse brep_fuse(result, moved_shape);
				if ( brep_fuse.IsDone() ) {
					TopoDS_Shape fused = brep_fuse;

					ShapeFix_Shape fix(result);
					fix.Perform();
					result = fix.Shape();
		
					bool is_valid = BRepCheck_Analyzer(result).IsValid() != 0;
					if ( is_valid ) {
						result = fused;
					} 
				}
			}
		} else {
			builder.Add(compound,moved_shape);
		}
	}

	if (!fuse) {
		result = compound;
	}

	const bool success = !result.IsNull();
	if (success) {
		const double precision = getValue(GV_PRECISION);
		apply_tolerance(result, precision);
	}

	return success;
}
	
void IfcGeom::Kernel::remove_duplicate_points_from_loop(TColgp_SequenceOfPnt& polygon, bool closed, double tol) {
	if (tol <= 0.) tol = getValue(GV_PRECISION);
	tol *= tol;

	for (;;) {
		bool removed = false;
		int n = polygon.Length() - (closed ? 0 : 1);
		for (int i = 1; i <= n; ++i) {
			// wrap around to the first point in case of a closed loop
			int j = (i % polygon.Length()) + 1;
			double dist = polygon.Value(i).SquareDistance(polygon.Value(j));
			if (dist < tol) {
				// do not remove the first or last point to
				// maintain connectivity with other wires
				if ((closed && j == 1) || (!closed && j == n)) polygon.Remove(i);
				else polygon.Remove(j);
				removed = true;
				break;
			}
		}
		if (!removed) break;
	}
}

void IfcGeom::Kernel::remove_collinear_points_from_loop(TColgp_SequenceOfPnt& polygon, bool closed, double tol) {
	if (tol <= 0.) tol = getValue(GV_PRECISION);
	const int start = closed ? 1 : 2;
	const int end = polygon.Length() - (closed ? 0 : 1);
	std::vector<bool> to_remove(polygon.Length(), false);
	for (int i = start; i <= end; ++i) {
		const gp_Pnt& a = polygon.Value(((i - 2 + polygon.Length()) % polygon.Length()) + 1);
		const gp_Pnt& b = polygon.Value(i);
		const gp_Pnt& c = polygon.Value((i % polygon.Length()) + 1);
		const gp_Vec d1 = c.XYZ() - a.XYZ();
		const gp_Vec d2 = b.XYZ() - a.XYZ();
		const double dt = d2.Dot(d1) / d1.Dot(d1);
		const gp_Vec d3 = d1.Scaled(dt);
		const gp_Pnt b2 = a.XYZ() + d3.XYZ();
		if (b.Distance(b2) < tol) {
			to_remove[i-1] = true;
		}
	}
	for (int i = (int) to_remove.size() - 1; i >= 0; --i) {
		if (to_remove[i]) {
			polygon.Remove(i+1);
		}
	}
}

bool IfcGeom::Kernel::wire_to_sequence_of_point(const TopoDS_Wire& w, TColgp_SequenceOfPnt& p) {
	TopExp_Explorer exp(w, TopAbs_EDGE);
	for (; exp.More(); exp.Next()) {
		double a, b;
		Handle_Geom_Curve crv = BRep_Tool::Curve(TopoDS::Edge(exp.Current()), a, b);
		if (crv->DynamicType() != STANDARD_TYPE(Geom_Line)) {
			return false;
		}
	}

	exp.ReInit();

	int i = 0;
	for (; exp.More(); exp.Next(), ++i) {
		TopoDS_Vertex v1, v2;
		TopExp::Vertices(TopoDS::Edge(exp.Current()), v1, v2, true);
		if (exp.More()) {
			if (i == 0) {
				p.Append(BRep_Tool::Pnt(v1));
			}
			p.Append(BRep_Tool::Pnt(v2));
		}
	}

	return true;
}

void IfcGeom::Kernel::sequence_of_point_to_wire(const TColgp_SequenceOfPnt& p, TopoDS_Wire& w, bool close) {
	BRepBuilderAPI_MakePolygon builder;
	for (int i = 1; i <= p.Length(); ++i) {
		builder.Add(p.Value(i));
	}
	if (close) {
		builder.Close();
	}
	w = builder.Wire();	
}

IfcSchema::IfcRelVoidsElement::list::ptr IfcGeom::Kernel::find_openings(IfcSchema::IfcProduct* product) {
	
	IfcSchema::IfcRelVoidsElement::list::ptr openings(new IfcSchema::IfcRelVoidsElement::list);
	if ( product->is(IfcSchema::Type::IfcElement) && !product->is(IfcSchema::Type::IfcOpeningElement) ) {
		IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)product;
		openings = element->HasOpenings();
	}

	// Is the IfcElement a decomposition of an IfcElement with any IfcOpeningElements?
	IfcSchema::IfcObjectDefinition* obdef = product->as<IfcSchema::IfcObjectDefinition>();
	for (;;) {
#ifdef USE_IFC4
		IfcSchema::IfcRelAggregates::list::ptr decomposes = obdef->Decomposes();
#else
		IfcSchema::IfcRelDecomposes::list::ptr decomposes = obdef->Decomposes();
#endif
		if (decomposes->size() != 1) break;
		IfcSchema::IfcObjectDefinition* rel_obdef = (*decomposes->begin())->RelatingObject();
		if ( rel_obdef->is(IfcSchema::Type::IfcElement) && !rel_obdef->is(IfcSchema::Type::IfcOpeningElement) ) {
			IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)rel_obdef;
			openings->push(element->HasOpenings());
		}

		obdef = rel_obdef;
	}

	return openings;
}

const IfcSchema::IfcMaterial* IfcGeom::Kernel::get_single_material_association(const IfcSchema::IfcProduct* product) {
	IfcSchema::IfcMaterial* single_material = 0;
	IfcSchema::IfcRelAssociatesMaterial::list::ptr associated_materials = product->HasAssociations()->as<IfcSchema::IfcRelAssociatesMaterial>();
	if (associated_materials->size() == 1) {
		IfcSchema::IfcMaterialSelect* associated_material = (*associated_materials->begin())->RelatingMaterial();
		single_material = associated_material->as<IfcSchema::IfcMaterial>();

		// NB: Single-layer layersets are also considered, regardless of --enable-layerset-slicing, this
		// in accordance with other viewers.
		if (!single_material && associated_material->as<IfcSchema::IfcMaterialLayerSetUsage>()) {
			IfcSchema::IfcMaterialLayerSet* layerset = associated_material->as<IfcSchema::IfcMaterialLayerSetUsage>()->ForLayerSet();
			if (layerset->MaterialLayers()->size() == 1) {
				IfcSchema::IfcMaterialLayer* layer = (*layerset->MaterialLayers()->begin());
				if (layer->hasMaterial()) {
					single_material = layer->Material();
				}
			}
		}
	}
	return single_material;
}

template <typename P>
IfcGeom::BRepElement<P>* IfcGeom::Kernel::create_brep_for_representation_and_product(
    const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product)
{
	std::stringstream representation_id_builder;

	representation_id_builder << representation->entity->id();

	IfcGeom::Representation::BRep* shape;
	IfcGeom::IfcRepresentationShapeItems shapes, shapes2;

	if ( !convert_shapes(representation, shapes) ) {
		return 0;
	}

	if (settings.get(IteratorSettings::APPLY_LAYERSETS)) {
		TopoDS_Shape merge;
		if (flatten_shape_list(shapes, merge, false)) {
			if (count(merge, TopAbs_FACE) > 0) {
				std::vector<double> thickness;
				std::vector<Handle_Geom_Surface> layers;
				std::vector< std::vector<Handle_Geom_Surface> > folded_layers;
				std::vector<const SurfaceStyle*> styles;
				if (convert_layerset(product, layers, styles, thickness)) {

					IfcSchema::IfcRelAssociates::list::ptr associations = product->HasAssociations();
					for (IfcSchema::IfcRelAssociates::list::it it = associations->begin(); it != associations->end(); ++it) {
						IfcSchema::IfcRelAssociatesMaterial* associates_material = (**it).as<IfcSchema::IfcRelAssociatesMaterial>();
						if (associates_material) {
							unsigned layerset_id = associates_material->RelatingMaterial()->entity->id();
							representation_id_builder << "-layerset-" << layerset_id;
							break;
						}
					}
					
					if (styles.size() > 1) {
						// If there's only a single layer there is no need to manipulate geometries.
						bool success = true;
						if (product->as<IfcSchema::IfcWall>() && fold_layers(product->as<IfcSchema::IfcWall>(), shapes, layers, thickness, folded_layers)) {
							if (apply_folded_layerset(shapes, folded_layers, styles, shapes2)) {
								std::swap(shapes, shapes2);
								success = true;
							}
						} else {
							if (apply_layerset(shapes, layers, styles, shapes2)) {
								std::swap(shapes, shapes2);
								success = true;
							}
						}

						if (!success) {
							Logger::Error("Failed processing layerset");
						}
					}
				}
			}
		}
	}

	bool material_style_applied = false;

	const IfcSchema::IfcMaterial* single_material = get_single_material_association(product);
	if (single_material) {
		const IfcGeom::SurfaceStyle* s = get_style(single_material);
		for (IfcGeom::IfcRepresentationShapeItems::iterator it = shapes.begin(); it != shapes.end(); ++it) {
			if (!it->hasStyle() && s) {
				it->setStyle(s);
				material_style_applied = true;
			}
		}
	} else {
		bool some_items_without_style = false;
		for (IfcGeom::IfcRepresentationShapeItems::iterator it = shapes.begin(); it != shapes.end(); ++it) {
			if (!it->hasStyle()) {
				some_items_without_style = true;
				break;
			}
		}
		if (some_items_without_style) {
			Logger::Warning("No material and surface styles for:", product->entity);
		}
    }

	if (material_style_applied) {
		representation_id_builder << "-material-" << single_material->entity->id();
	}

	int parent_id = -1;
	try {
		IfcSchema::IfcObjectDefinition* parent_object = get_decomposing_entity(product);
		if (parent_object) {
			parent_id = parent_object->entity->id();
		}
	} catch (const std::exception& e) {
		Logger::Error(e);
	}
		
	const std::string name = product->hasName() ? product->Name() : "";
	const std::string guid = product->GlobalId();
		
	gp_Trsf trsf;
	try {
		convert(product->ObjectPlacement(),trsf);
	} catch (const std::exception& e) {
		Logger::Error(e);
	} catch (...) {
		Logger::Error("Failed to construct placement");
	}

	// Does the IfcElement have any IfcOpenings?
	// Note that openings for IfcOpeningElements are not processed
	IfcSchema::IfcRelVoidsElement::list::ptr openings = find_openings(product);

	const std::string product_type = IfcSchema::Type::ToString(product->type());
	ElementSettings element_settings(settings, getValue(GV_LENGTH_UNIT), product_type);

    if (!settings.get(IfcGeom::IteratorSettings::DISABLE_OPENING_SUBTRACTIONS) && openings && openings->size()) {
		representation_id_builder << "-openings";
		for (IfcSchema::IfcRelVoidsElement::list::it it = openings->begin(); it != openings->end(); ++it) {
			representation_id_builder << "-" << (*it)->entity->id();
		}

		IfcGeom::IfcRepresentationShapeItems opened_shapes;
		bool caught_error = false;
		try {
#if OCC_VERSION_HEX < 0x60900
            const bool faster_booleans = settings.get(IteratorSettings::FASTER_BOOLEANS);
#else
			const bool faster_booleans = true;
#endif
			if (faster_booleans) {
				bool success = convert_openings_fast(product,openings,shapes,trsf,opened_shapes);
#if OCC_VERSION_HEX < 0x60900
				if (!success) {
					opened_shapes.clear();
					convert_openings(product,openings,shapes,trsf,opened_shapes);
				}
#else
				(void)success;
#endif
			} else {
				convert_openings(product,openings,shapes,trsf,opened_shapes);
			}
		} catch (const std::exception& e) {
			Logger::Message(Logger::LOG_ERROR, std::string("Error processing openings for: ") + e.what() + ":", product->entity);
			caught_error = true;
		} catch(...) {
			Logger::Message(Logger::LOG_ERROR,"Error processing openings for:",product->entity); 
			caught_error = true;
		}

		if (caught_error && opened_shapes.size() < shapes.size()) {
			opened_shapes = shapes;
		}

        if (settings.get(IteratorSettings::USE_WORLD_COORDS)) {
			for ( IfcGeom::IfcRepresentationShapeItems::iterator it = opened_shapes.begin(); it != opened_shapes.end(); ++ it ) {
				it->prepend(trsf);
			}
			trsf = gp_Trsf();
			representation_id_builder << "-world-coords";
		}
		shape = new IfcGeom::Representation::BRep(element_settings, representation_id_builder.str(), opened_shapes);
    } else if (settings.get(IteratorSettings::USE_WORLD_COORDS)) {
		for ( IfcGeom::IfcRepresentationShapeItems::iterator it = shapes.begin(); it != shapes.end(); ++ it ) {
			it->prepend(trsf);
		}
		trsf = gp_Trsf();
		representation_id_builder << "-world-coords";
		shape = new IfcGeom::Representation::BRep(element_settings, representation_id_builder.str(), shapes);
	} else {
		shape = new IfcGeom::Representation::BRep(element_settings, representation_id_builder.str(), shapes);
	}

	std::string context_string = "";
	if (representation->hasRepresentationIdentifier()) {
		context_string = representation->RepresentationIdentifier();
	} else if (representation->ContextOfItems()->hasContextType()) {
		context_string = representation->ContextOfItems()->ContextType();
	}

	return new BRepElement<P>(
		product->entity->id(),
		parent_id,
		name, 
		product_type,
		guid,
		context_string,
		trsf,
		boost::shared_ptr<IfcGeom::Representation::BRep>(shape),
        product
	);
}

IfcSchema::IfcRepresentation* IfcGeom::Kernel::representation_mapped_to(const IfcSchema::IfcRepresentation* representation) {
	IfcSchema::IfcRepresentation* representation_mapped_to = 0;
	IfcSchema::IfcRepresentationItem::list::ptr items = representation->Items();
	if (items->size() == 1) {
		IfcSchema::IfcRepresentationItem* item = *items->begin();
		if (item->is(IfcSchema::Type::IfcMappedItem)) {
			if (item->StyledByItem()->size() == 0) {
				IfcSchema::IfcMappedItem* mapped_item = item->as<IfcSchema::IfcMappedItem>();
				if (is_identity_transform(mapped_item->MappingTarget())) {
					IfcSchema::IfcRepresentationMap* map = mapped_item->MappingSource();
					if (is_identity_transform(map->MappingOrigin())) {
						representation_mapped_to = map->MappedRepresentation();
					}
				}
			}
		}
	}
	return representation_mapped_to;
}

IfcSchema::IfcProduct::list::ptr IfcGeom::Kernel::products_represented_by(const IfcSchema::IfcRepresentation* representation) {
	IfcSchema::IfcProduct::list::ptr products(new IfcSchema::IfcProduct::list);

	IfcSchema::IfcProductRepresentation::list::ptr prodreps = representation->OfProductRepresentation();

	for (IfcSchema::IfcProductRepresentation::list::it it = prodreps->begin(); it != prodreps->end(); ++it) {
		// http://buildingsmart-tech.org/ifc/IFC2x3/TC1/html/ifcrepresentationresource/lexical/ifcproductrepresentation.htm
		// IFC2x Edition 3 NOTE  Users should not instantiate the entity IfcProductRepresentation from IFC2x Edition 3 onwards. 
		// It will be changed into an ABSTRACT supertype in future releases of IFC.

		// IfcProductRepresentation also lacks the INVERSE relation to IfcProduct
		// Let's find the IfcProducts that reference the IfcProductRepresentation anyway
		products->push((*it)->entity->getInverse(IfcSchema::Type::IfcProduct, -1)->as<IfcSchema::IfcProduct>());
	}
	
	IfcSchema::IfcRepresentationMap::list::ptr maps = representation->RepresentationMap();
	if (maps->size() == 1) {
		IfcSchema::IfcRepresentationMap* map = *maps->begin();
		if (is_identity_transform(map->MappingOrigin())) {
			IfcSchema::IfcMappedItem::list::ptr items = map->MapUsage();
			for (IfcSchema::IfcMappedItem::list::it it = items->begin(); it != items->end(); ++it) {
				IfcSchema::IfcMappedItem* item = *it;
				if (item->StyledByItem()->size() != 0) continue;

				if (!is_identity_transform(item->MappingTarget())) {
					continue;
				}

				IfcSchema::IfcRepresentation::list::ptr reps = item->entity->getInverse(IfcSchema::Type::IfcRepresentation, -1)->as<IfcSchema::IfcRepresentation>();
				for (IfcSchema::IfcRepresentation::list::it jt = reps->begin(); jt != reps->end(); ++jt) {
					IfcSchema::IfcRepresentation* rep = *jt;
					if (rep->Items()->size() != 1) continue;
					IfcSchema::IfcProductRepresentation::list::ptr prodreps_mapped = rep->OfProductRepresentation();
					for (IfcSchema::IfcProductRepresentation::list::it kt = prodreps_mapped->begin(); kt != prodreps_mapped->end(); ++kt) {
						IfcSchema::IfcProduct::list::ptr ps = (*kt)->entity->getInverse(IfcSchema::Type::IfcProduct, -1)->as<IfcSchema::IfcProduct>();
						products->push(ps);
					}
				}
			}
		}
	}

	return products;
}

template <typename P>
IfcGeom::BRepElement<P>* IfcGeom::Kernel::create_brep_for_processed_representation(
    const IteratorSettings& /*settings*/, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product,
    IfcGeom::BRepElement<P>* brep)
{
	int parent_id = -1;
	try {
		IfcSchema::IfcObjectDefinition* parent_object = get_decomposing_entity(product);
		if (parent_object) {
			parent_id = parent_object->entity->id();
		}
	} catch (const std::exception& e) {
		Logger::Error(e);
	}
		
	const std::string name = product->hasName() ? product->Name() : "";
	const std::string guid = product->GlobalId();
		
	gp_Trsf trsf;
	try {
		convert(product->ObjectPlacement(),trsf);
	} catch (const std::exception& e) {
		Logger::Error(e);
	} catch (...) {
		Logger::Error("Failed to construct placement");
	}

	std::string context_string = "";
	if (representation->hasRepresentationIdentifier()) {
		context_string = representation->RepresentationIdentifier();
	} else if (representation->ContextOfItems()->hasContextType()) {
		context_string = representation->ContextOfItems()->ContextType();
	}

	const std::string product_type = IfcSchema::Type::ToString(product->type());

	return new BRepElement<P>(
		product->entity->id(),
		parent_id,
		name, 
		product_type,
		guid,
		context_string,
		trsf,
		brep->geometry_pointer(),
        product
	);
}

IfcSchema::IfcObjectDefinition* IfcGeom::Kernel::get_decomposing_entity(IfcSchema::IfcProduct* product) {
	IfcSchema::IfcObjectDefinition* parent = 0;

	// In case of an opening element, parent to the RelatingBuildingElement
	if ( product->is(IfcSchema::Type::IfcOpeningElement ) ) {
		IfcSchema::IfcOpeningElement* opening = (IfcSchema::IfcOpeningElement*)product;
		IfcSchema::IfcRelVoidsElement::list::ptr voids = opening->VoidsElements();
		if ( voids->size() ) {
			IfcSchema::IfcRelVoidsElement* ifc_void = *voids->begin();
			parent = ifc_void->RelatingBuildingElement();
		}
	} else if ( product->is(IfcSchema::Type::IfcElement ) ) {
		IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)product;
		IfcSchema::IfcRelFillsElement::list::ptr fills = element->FillsVoids();
		// In case of a RelatedBuildingElement parent to the opening element
		if ( fills->size() ) {
			for ( IfcSchema::IfcRelFillsElement::list::it it = fills->begin(); it != fills->end(); ++ it ) {
				IfcSchema::IfcRelFillsElement* fill = *it;
				IfcSchema::IfcObjectDefinition* ifc_objectdef = fill->RelatingOpeningElement();
				if ( product == ifc_objectdef ) continue;
				parent = ifc_objectdef;
			}
		} 
		// Else simply parent to the containing structure
		if (!parent) {
			IfcSchema::IfcRelContainedInSpatialStructure::list::ptr parents = element->ContainedInStructure();
			if ( parents->size() ) {
				IfcSchema::IfcRelContainedInSpatialStructure* container = *parents->begin();
				parent = container->RelatingStructure();
			}
		}
	}
	// Parent decompositions to the RelatingObject
	if (!parent) {
		IfcEntityList::ptr parents = product->entity->getInverse(IfcSchema::Type::IfcRelAggregates, -1);
		parents->push(product->entity->getInverse(IfcSchema::Type::IfcRelNests, -1));
		for ( IfcEntityList::it it = parents->begin(); it != parents->end(); ++ it ) {
			IfcSchema::IfcRelDecomposes* decompose = (IfcSchema::IfcRelDecomposes*)*it;
			IfcSchema::IfcObjectDefinition* ifc_objectdef;
#ifdef USE_IFC4
			if (decompose->is(IfcSchema::Type::IfcRelAggregates)) {
				ifc_objectdef = ((IfcSchema::IfcRelAggregates*)decompose)->RelatingObject();
			} else {
				continue;
			}
#else
			ifc_objectdef = decompose->RelatingObject();
#endif
			if ( product == ifc_objectdef ) continue;
			parent = ifc_objectdef;
		}
	}
	return parent;
}

std::map<std::string, IfcSchema::IfcPresentationLayerAssignment*> IfcGeom::Kernel::get_layers(IfcSchema::IfcProduct* prod)
{
    using namespace IfcSchema;
    std::map<std::string, IfcPresentationLayerAssignment*> layers;
    if (prod->hasRepresentation()) {
        IfcEntityList::ptr r = prod->entity->file->traverse(prod->Representation());
        IfcRepresentation::list::ptr representations = r->as<IfcRepresentation>();
        for (IfcRepresentation::list::it it = representations->begin(); it != representations->end(); ++it) {
            IfcPresentationLayerAssignment::list::ptr a = (*it)->LayerAssignments();
            for (IfcPresentationLayerAssignment::list::it jt = a->begin(); jt != a->end(); ++jt) {
                layers[(*jt)->Name()] = *jt;
            }
        }
    }
    return layers;
}

template IFC_GEOM_API IfcGeom::BRepElement<float>* IfcGeom::Kernel::create_brep_for_representation_and_product<float>(
    const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product);
template IFC_GEOM_API IfcGeom::BRepElement<double>* IfcGeom::Kernel::create_brep_for_representation_and_product<double>(
    const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product);

template IFC_GEOM_API IfcGeom::BRepElement<float>* IfcGeom::Kernel::create_brep_for_processed_representation<float>(
    const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product, IfcGeom::BRepElement<float>* brep);
template IFC_GEOM_API IfcGeom::BRepElement<double>* IfcGeom::Kernel::create_brep_for_processed_representation<double>(
    const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product, IfcGeom::BRepElement<double>* brep);

std::pair<std::string, double> IfcGeom::Kernel::initializeUnits(IfcSchema::IfcUnitAssignment* unit_assignment) {
	// Set default units, set length to meters, angles to undefined
	setValue(IfcGeom::Kernel::GV_LENGTH_UNIT, 1.0);
	setValue(IfcGeom::Kernel::GV_PLANEANGLE_UNIT, -1.0);

	std::string unit_name = "METER";
	double unit_magnitude = 1.;

	bool length_unit_encountered = false, angle_unit_encountered = false;

	try {
		IfcEntityList::ptr units = unit_assignment->Units();
		if (!units || !units->size()) {
			Logger::Message(Logger::LOG_ERROR, "No unit information found");
		} else {
			for (IfcEntityList::it it = units->begin(); it != units->end(); ++it) {
				IfcUtil::IfcBaseClass* base = *it;
				if (base->is(IfcSchema::Type::IfcNamedUnit)) {
					IfcSchema::IfcNamedUnit* named_unit = base->as<IfcSchema::IfcNamedUnit>();
					if (named_unit->UnitType() == IfcSchema::IfcUnitEnum::IfcUnit_LENGTHUNIT ||
						named_unit->UnitType() == IfcSchema::IfcUnitEnum::IfcUnit_PLANEANGLEUNIT)
					{
						std::string current_unit_name;
						const double current_unit_magnitude = IfcParse::get_SI_equivalent(named_unit);
						if (current_unit_magnitude != 0.) {
							if (named_unit->is(IfcSchema::Type::IfcConversionBasedUnit)) {
								IfcSchema::IfcConversionBasedUnit* u = (IfcSchema::IfcConversionBasedUnit*)base;
								current_unit_name = u->Name();
							} else if (named_unit->is(IfcSchema::Type::IfcSIUnit)) {
								IfcSchema::IfcSIUnit* si_unit = named_unit->as<IfcSchema::IfcSIUnit>();
								if (si_unit->hasPrefix()) {
									current_unit_name = IfcSchema::IfcSIPrefix::ToString(si_unit->Prefix()) + unit_name;
								}
								current_unit_name += IfcSchema::IfcSIUnitName::ToString(si_unit->Name());
							}
							if (named_unit->UnitType() == IfcSchema::IfcUnitEnum::IfcUnit_LENGTHUNIT) {
								unit_name = current_unit_name;
								unit_magnitude = current_unit_magnitude;
								setValue(IfcGeom::Kernel::GV_LENGTH_UNIT, current_unit_magnitude);
								length_unit_encountered = true;
							} else {
								setValue(IfcGeom::Kernel::GV_PLANEANGLE_UNIT, current_unit_magnitude);
								angle_unit_encountered = true;
							}
						}
					}
				}
			}
		}
	} catch (const IfcParse::IfcException& ex) {
		std::stringstream ss;
		ss << "Failed to determine unit information '" << ex.what() << "'";
		Logger::Message(Logger::LOG_ERROR, ss.str());
	}

	if (!length_unit_encountered) {
		Logger::Error("No length unit encountered");
	}

	if (!angle_unit_encountered) {
		Logger::Error("No plane angle unit encountered");
	}

	return std::pair<std::string, double>(unit_name, unit_magnitude);
}

bool IfcGeom::Kernel::convert_layerset(const IfcSchema::IfcProduct* product, std::vector<Handle_Geom_Surface>& surfaces, std::vector<const SurfaceStyle*>& styles, std::vector<double>& thicknesses) {
	IfcSchema::IfcMaterialLayerSetUsage* usage = 0;
	Handle_Geom_Surface reference_surface;

	IfcSchema::IfcRelAssociates::list::ptr associations = product->HasAssociations();
	for (IfcSchema::IfcRelAssociates::list::it it = associations->begin(); it != associations->end(); ++it) {
		IfcSchema::IfcRelAssociatesMaterial* associates_material = (**it).as<IfcSchema::IfcRelAssociatesMaterial>();
		if (associates_material) {
			usage = associates_material->RelatingMaterial()->as<IfcSchema::IfcMaterialLayerSetUsage>();
			break;
		}
	}

	if (!usage) {
		return false;
	}

	IfcSchema::IfcRepresentation* body_representation = find_representation(product, "Body");

	if (!body_representation) {
		Logger::Warning("No body representation for product", product->entity);
		return false;
	}

	if (product->is(IfcSchema::Type::IfcWall)) {
		IfcSchema::IfcRepresentation* axis_representation = find_representation(product, "Axis");

		if (!axis_representation) {
			Logger::Message(Logger::LOG_WARNING, "No axis representation for:", product->entity);
			return false;
		}

		IfcRepresentationShapeItems axis_items;
		{
			Kernel temp = *this;
			temp.setValue(GV_DIMENSIONALITY, -1.);
			temp.convert_shapes(axis_representation, axis_items);
		}

		TopoDS_Shape axis_shape;
		flatten_shape_list(axis_items, axis_shape, false);

		TopExp_Explorer exp(axis_shape, TopAbs_EDGE);
		TopoDS_Edge axis_edge;
		int edge_count = 0;

		if (exp.More()) {
			axis_edge = TopoDS::Edge(exp.Current());
			++ edge_count;
		} else {
			Logger::Message(Logger::LOG_WARNING, "No edge found in axis representation:", product->entity);
			return false;
		}

		double u1, u2;
		Handle_Geom_Curve axis_curve = BRep_Tool::Curve(axis_edge, u1, u2);

		if (true) { /**< @todo Why always true? */
			if (axis_curve->DynamicType() == STANDARD_TYPE(Geom_Line)) {
				Handle_Geom_Line axis_line = Handle_Geom_Line::DownCast(axis_curve);
				// @todo note that this creates an offset into the wrong order, the cross product arguments should be
				// reversed. This causes some inversions later on, e.g. if(positive) { reverse(); }
				reference_surface = new Geom_Plane(axis_line->Lin().Location(), axis_line->Lin().Direction() ^ gp::DZ());
			} else if (axis_curve->DynamicType() == STANDARD_TYPE(Geom_Circle)) {
				// @todo note that in this branch this inversion does not seem to take place.
				Handle_Geom_Circle axis_line = Handle_Geom_Circle::DownCast(axis_curve);
				reference_surface = new Geom_CylindricalSurface(axis_line->Position(), axis_line->Radius());
			} else {
				Logger::Message(Logger::LOG_ERROR, "Unsupported underlying curve of Axis representation:", product->entity);
				return false;
			}
		} else {
			// Unfortunately this does not work when its intersection
			// is calculated later on when the layerset is applied.
			reference_surface = new Geom_SurfaceOfLinearExtrusion(axis_curve, gp::DZ());
		}
		
	} else {
		IfcSchema::IfcExtrudedAreaSolid::list::ptr extrusions = body_representation->entity->file->traverse(body_representation)->as<IfcSchema::IfcExtrudedAreaSolid>();
		
		if (extrusions->size() != 1) {
			Logger::Message(Logger::LOG_WARNING, "No single extrusion found in body representation for:", product->entity);
			return false;
		}

		IfcSchema::IfcExtrudedAreaSolid* extrusion = *extrusions->begin();

		gp_Trsf extrusion_position;

		bool has_position = true;
#ifdef USE_IFC4
		has_position = extrusion->hasPosition();
#endif
		if (has_position) {
			if (!convert(extrusion->Position(), extrusion_position)) {
				Logger::Message(Logger::LOG_ERROR, "Failed to convert placement for extrusion of:", product->entity);
				return false;
			}
		}

		gp_Dir extrusion_direction;
		if (!convert(extrusion->ExtrudedDirection(), extrusion_direction)) {
			Logger::Message(Logger::LOG_ERROR, "Failed to convert direction for extrusion of:", product->entity);
			return false;
		}

		reference_surface = new Geom_Plane(extrusion_position.TranslationPart(), extrusion_direction);
	}

	const IfcSchema::IfcMaterialLayerSet* layerset = usage->ForLayerSet();
	const bool positive = usage->DirectionSense() == IfcSchema::IfcDirectionSenseEnum::IfcDirectionSense_POSITIVE;
	double offset = usage->OffsetFromReferenceLine() * getValue(GV_LENGTH_UNIT);

	IfcSchema::IfcMaterialLayer::list::ptr material_layers = layerset->MaterialLayers();

	surfaces.push_back(new Geom_OffsetSurface(reference_surface, -offset));

	for (IfcSchema::IfcMaterialLayer::list::it it = material_layers->begin(); it != material_layers->end(); ++it) {
		styles.push_back(get_style((*it)->Material()));

		double thickness = (*it)->LayerThickness() * getValue(GV_LENGTH_UNIT);

		thicknesses.push_back(thickness);
		
		if (!positive) {
			thickness *= -1;
		}

		offset += thickness;

		if (fabs(offset) < 1.e-7) {
			surfaces.push_back(reference_surface);
		} else {
			surfaces.push_back(new Geom_OffsetSurface(reference_surface, -offset));
		}
	}

	if (positive) {
		std::reverse(surfaces.begin(), surfaces.end());
	}

	return true;
}

const Handle_Geom_Curve IfcGeom::Kernel::intersect(const Handle_Geom_Surface& a, const Handle_Geom_Surface& b) {
	GeomAPI_IntSS x(a, b, 1.e-7);
	if (x.IsDone() && x.NbLines() == 1) {
		return x.Line(1);
	} else {
		return Handle_Geom_Curve();
	}
}

const Handle_Geom_Curve IfcGeom::Kernel::intersect(const Handle_Geom_Surface& a, const TopoDS_Face& b) {
	return intersect(a, BRep_Tool::Surface(b));
}

const Handle_Geom_Curve IfcGeom::Kernel::intersect(const TopoDS_Face& a, const Handle_Geom_Surface& b) {
	return intersect(BRep_Tool::Surface(a), b);
}

bool IfcGeom::Kernel::intersect(const Handle_Geom_Curve& a, const Handle_Geom_Surface& b, gp_Pnt& p) {
	GeomAPI_IntCS x(a, b);
	if (x.IsDone() && x.NbPoints() == 1) {
		p = x.Point(1);
		return true;
	} else {
		return false;
	}
}

bool IfcGeom::Kernel::intersect(const Handle_Geom_Curve& a, const TopoDS_Face& b, gp_Pnt &c) {
	return intersect(a, BRep_Tool::Surface(b), c);
}

bool IfcGeom::Kernel::intersect(const Handle_Geom_Curve& a, const TopoDS_Shape& b, std::vector<gp_Pnt>& out) {
	TopExp_Explorer exp(b, TopAbs_FACE);
	gp_Pnt p;
	for (; exp.More(); exp.Next()) {
		if (intersect(a, TopoDS::Face(exp.Current()), p)) {
			out.push_back(p);
		}
	}
	return !out.empty();
}

bool IfcGeom::Kernel::intersect(const Handle_Geom_Surface& a, const TopoDS_Shape& b, std::vector< std::pair<Handle_Geom_Surface, Handle_Geom_Curve> >& out) {
	TopExp_Explorer exp(b, TopAbs_FACE);
	for (; exp.More(); exp.Next()) {
		const TopoDS_Face& f = TopoDS::Face(exp.Current());
		const Handle_Geom_Surface& s = BRep_Tool::Surface(f);
		Handle_Geom_Curve crv = intersect(a, s);
		if (!crv.IsNull()) {
			out.push_back(std::make_pair(s, crv));
		}
	}
	return !out.empty();
}

bool IfcGeom::Kernel::closest(const gp_Pnt& a, const std::vector<gp_Pnt>& b, gp_Pnt& c) {
	double minimal_distance = std::numeric_limits<double>::infinity();
	for (std::vector<gp_Pnt>::const_iterator it = b.begin(); it != b.end(); ++it) {
		const double d = a.Distance(*it);
		if (d < minimal_distance) {
			minimal_distance = d;
			c = *it;
		}
	}
	return minimal_distance != std::numeric_limits<double>::infinity();
}

bool IfcGeom::Kernel::project(const Handle_Geom_Curve& crv, const gp_Pnt& pt, gp_Pnt& p, double& u, double& d) {
	ShapeAnalysis_Curve sac;
	sac.Project(crv, pt, 1e-3, p, u, false);
	d = pt.Distance(p);
	return true;
}

int IfcGeom::Kernel::count(const TopoDS_Shape& s, TopAbs_ShapeEnum t) {
	int i = 0;
	TopExp_Explorer exp(s, t);
	for (; exp.More(); exp.Next()) {
		++i;
	}
	return i;
}

bool IfcGeom::Kernel::find_wall_end_points(const IfcSchema::IfcWall* wall, gp_Pnt& start, gp_Pnt& end) {
	IfcSchema::IfcRepresentation* axis_representation = find_representation(wall, "Axis");
	if (!axis_representation) {
		return false;
	}
		
	IfcRepresentationShapeItems items;
	{
		Kernel temp = *this;
		temp.setValue(GV_DIMENSIONALITY, -1.);
		temp.convert_shapes(axis_representation, items);
	}

	TopoDS_Vertex a, b;
	for (IfcRepresentationShapeItems::const_iterator it = items.begin(); it != items.end(); ++it) {
		TopExp_Explorer exp(it->Shape(), TopAbs_VERTEX);
		for (; exp.More(); exp.Next()) {
			b = TopoDS::Vertex(exp.Current());
			if (a.IsNull()) {
				a = b;
			}				
		}
	}
	
	if (a.IsNull() || b.IsNull()) {
		return false;
	}

	start = BRep_Tool::Pnt(a);
	end = BRep_Tool::Pnt(b);

	return true;
}

bool IfcGeom::Kernel::fold_layers(const IfcSchema::IfcWall* wall, const IfcRepresentationShapeItems& items, const std::vector<Handle_Geom_Surface>& surfaces, const std::vector<double>& thicknesses, std::vector< std::vector<Handle_Geom_Surface> >& result) {
	bool folds_made = false;
	
	IfcSchema::IfcRelConnectsPathElements::list::ptr connections(new IfcSchema::IfcRelConnectsPathElements::list);
	connections->push(wall->ConnectedFrom()->as<IfcSchema::IfcRelConnectsPathElements>());
	connections->push(  wall->ConnectedTo()->as<IfcSchema::IfcRelConnectsPathElements>());

	typedef std::vector<Handle_Geom_Surface> surfaces_t;
	typedef std::pair<Handle_Geom_Surface, Handle_Geom_Curve> curve_on_surface;
	typedef std::vector<curve_on_surface> curves_on_surfaces_t;
	typedef std::vector< std::pair< std::pair<IfcSchema::IfcConnectionTypeEnum::IfcConnectionTypeEnum, IfcSchema::IfcConnectionTypeEnum::IfcConnectionTypeEnum>, const IfcSchema::IfcProduct*> > endpoint_connections_t;
	typedef std::vector< std::vector<Handle_Geom_Surface> > result_t;
	endpoint_connections_t endpoint_connections;

	for (IfcSchema::IfcRelConnectsPathElements::list::it it = connections->begin(); it != connections->end(); ++it) {
		IfcSchema::IfcRelConnectsPathElements* connection = *it;
		IfcSchema::IfcConnectionTypeEnum::IfcConnectionTypeEnum own_type = connection->RelatedElement() == wall
			? connection->RelatedConnectionType()
			: connection->RelatingConnectionType();
		IfcSchema::IfcConnectionTypeEnum::IfcConnectionTypeEnum other_type = connection->RelatedElement() == wall
			? connection->RelatingConnectionType()
			: connection->RelatedConnectionType();
		if (other_type != IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATPATH && 
		   (own_type == IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATEND ||
			own_type == IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATSTART))
		{
			IfcSchema::IfcElement* other = connection->RelatedElement() == wall
				? connection->RelatingElement()
				: connection->RelatedElement();
			if (other->as<IfcSchema::IfcWall>()) {
				endpoint_connections.push_back(std::make_pair(std::make_pair(own_type, other_type), other));
			}
		}
	}

	if (endpoint_connections.size() == 0) {
		return false;
	}

	int connection_type_count[2] = {0,0};
	for (endpoint_connections_t::const_iterator it = endpoint_connections.begin(); it != endpoint_connections.end(); ++it) {
		const int idx = it->first.first == IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATSTART;
		connection_type_count[idx] ++;
	}

	gp_Trsf local;
	if (!convert(wall->ObjectPlacement(), local)) {
		return false;
	}
	local.Invert();

	{
		// Copy the unfolded surfaces
		result.resize(surfaces.size());
		std::vector< std::vector<Handle_Geom_Surface> >::iterator result_it = result.begin() + 1;
		std::vector<Handle_Geom_Surface>::const_iterator input_it = surfaces.begin() + 1;
		for(; input_it != surfaces.end() - 1; ++result_it, ++input_it) {
			result_it->push_back(*input_it);
		}
	}

	gp_Pnt own_axis_start, own_axis_end;
	find_wall_end_points(wall, own_axis_start, own_axis_end);

	for (int idx = 0; idx < 2; ++idx) {
		if (connection_type_count[idx] <= 1) {
			continue;
		}
		
		/*
		IfcSchema::IfcConnectionTypeEnum::IfcConnectionTypeEnum connection_type = idx == 1
			? IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATSTART
			: IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATEND;
		*/

		std::set<const IfcSchema::IfcProduct*> others;
		endpoint_connections_t::iterator it = endpoint_connections.begin();
		while (it != endpoint_connections.end()) {
			const IfcSchema::IfcProduct* other = it->second;
			if (others.find(other) != others.end()) {
				it = endpoint_connections.erase(it);
				-- connection_type_count[idx];
			} else {
				others.insert(other);
				++it;
			}
		}

		/*
		Additionally one could check whether the end points are of the wall are really ~1 LayerThickness away from each other
		for (endpoint_connections_t::const_iterator it = endpoint_connections.begin(); it != endpoint_connections.end(); ++it) {
			IfcSchema::IfcConnectionTypeEnum::IfcConnectionTypeEnum relating_connection_type = it->first.first;
			IfcSchema::IfcConnectionTypeEnum::IfcConnectionTypeEnum related_connection_type = it->first.second;

			if (connection_type != relating_connection_type) {
				continue;
			}

			gp_Pnt other_axis_start, other_axis_end;
			find_wall_end_points(it->second->as<IfcSchema::IfcWall>(), other_axis_start, other_axis_end);

			gp_Trsf other;
			if (!convert(it->second->ObjectPlacement(), other)) {
				continue;
			}

			other.Transforms(other_axis_start.ChangeCoord());
			local.Transforms(other_axis_start.ChangeCoord());
			other.Transforms(other_axis_end.ChangeCoord());
			local.Transforms(other_axis_end.ChangeCoord());

			const gp_Pnt& a = relating_connection_type == IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATSTART
				? own_axis_start
				: own_axis_end;

			const gp_Pnt& b = related_connection_type == IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATSTART
				? other_axis_start
				: other_axis_end;

			const double d = a.Distance(b);
		}
		*/
	}

	for (endpoint_connections_t::const_iterator it = endpoint_connections.begin(); it != endpoint_connections.end(); ++it) {
		IfcSchema::IfcConnectionTypeEnum::IfcConnectionTypeEnum connection_type = it->first.first;

		// If more than one wall connects to this start/end -point assume layers do not need to be folded
		const int idx = connection_type == IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATSTART;
		if (connection_type_count[idx] > 1) continue;

		const gp_Pnt& own_end_point = connection_type == IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATEND
			? own_axis_end
			: own_axis_start;
		const IfcSchema::IfcProduct* other_wall = it->second;

		gp_Trsf other;
		if (!convert(other_wall->ObjectPlacement(), other)) {
			Logger::Error("Failed to convert placement", other_wall->entity);
			continue;
		}

		IfcSchema::IfcRepresentation* axis_representation = find_representation(other_wall, "Axis");

		if (!axis_representation) {
			Logger::Warning("Joined wall has no axis representation", other_wall->entity);
			continue;
		}
		
		IfcRepresentationShapeItems axis_items;
		{
			Kernel temp = *this;
			temp.setValue(GV_DIMENSIONALITY, -1.);
			temp.convert_shapes(axis_representation, axis_items);
		}

		TopoDS_Shape axis_shape;
		flatten_shape_list(axis_items, axis_shape, false);
		
		// local and other are IfcLocalPlacements and therefore have a unit
		// scale factor that can be applied by means of TopoDS_Shape::Move()
		axis_shape.Move(other);
		axis_shape.Move(local);
		
		TopoDS_Shape body_shape;
		flatten_shape_list(items, body_shape, false);

		Handle_Geom_Curve axis_curve;
		double axis_u1, axis_u2;
				
		{ 
			TopExp_Explorer exp(axis_shape, TopAbs_EDGE);
			if (!exp.More()) {
				return false;
			}

			TopoDS_Edge axis_edge = TopoDS::Edge(exp.Current());
			axis_curve = BRep_Tool::Curve(axis_edge, axis_u1, axis_u2);

			gp_Pnt other_a_1, other_a_2;
			axis_curve->D0(axis_u1, other_a_1);
			axis_curve->D0(axis_u2, other_a_2);

			if (axis_u2 < axis_u1) {
				std::swap(axis_u1, axis_u2);
			}
			exp.Next();

			for (; exp.More(); exp.Next()) {
				TopoDS_Edge axis_edge2 = TopoDS::Edge(exp.Current());
				TopExp_Explorer exp2(axis_edge2, TopAbs_VERTEX);
				for (; exp2.More(); exp2.Next()) {
					gp_Pnt p = BRep_Tool::Pnt(TopoDS::Vertex(exp2.Current()));
					gp_Pnt pp;
					double u, d;
					if (project(axis_curve, p, pp, u, d)) {
						if (u < axis_u1) axis_u1 = u;
						if (u > axis_u2) axis_u2 = u;
					}
				}				
			}
		}
		
		double layer_offset = 0;
		
		std::vector<double>::const_iterator thickness = thicknesses.begin();
		result_t::iterator result_vector = result.begin() + 1;

		for (surfaces_t::const_iterator jt = surfaces.begin() + 1; jt != surfaces.end() - 1; ++jt, ++result_vector) {
			layer_offset += *thickness++;

			bool found_intersection = false;
			boost::optional<gp_Pnt> point_outside_param_range;
			//double param;
				
			const Handle_Geom_Surface& surface = *jt;

			GeomAPI_IntCS intersections(axis_curve, surface);
			if (intersections.IsDone() && intersections.NbPoints() == 1) {
				const gp_Pnt& p = intersections.Point(1);
				double u, v, w;
				intersections.Parameters(1, u, v, w);
				if (w < axis_u1 || w > axis_u2) {
					point_outside_param_range = p;
					//param = w;
				} else {
					// Found an intersection. Layer end point is covered by connecting wall
					found_intersection = true;
					break;
				}
			}

			if (!found_intersection && point_outside_param_range) {

				/*
				Is there a bug in Open Cascade related to the intersection
				of offset surfaces constructed from linear extrusions?
				Handle_Geom_Surface xy = new Geom_Plane(gp::Origin(), gp::DZ());
				// Handle_Geom_Surface yz = new Geom_Plane(gp::Origin(), gp::DX());
				// Handle_Geom_Surface yz2 = new Geom_OffsetSurface(yz, 1.);
				Handle_Geom_Curve ln = new Geom_Line(gp::Origin(), gp::DX());
				Handle_Geom_Surface yz = new Geom_SurfaceOfLinearExtrusion(ln, gp::DZ());
				Handle_Geom_Surface yz2 = new Geom_OffsetSurface(yz, 1.);
				intersect(xy, yz2);
				*/
				
				Handle_Geom_Surface plane = new Geom_Plane(*point_outside_param_range, gp::DZ());

				curves_on_surfaces_t layer_ends;
				intersect(surface, body_shape, layer_ends);

				Handle_Geom_Curve layer_body_intersection;
				Handle_Geom_Surface body_surface;
				double mind = std::numeric_limits<double>::infinity();
				for (curves_on_surfaces_t::const_iterator kt = layer_ends.begin(); kt != layer_ends.end(); ++kt) {
					gp_Pnt p;
					gp_Vec v;
					double u, d;
					kt->second->D1(0., p, v);
					if (ALMOST_THE_SAME(0., v.Dot(gp::DZ()))) {
						// Filter horizontal curves
						continue;
					}
					if (project(kt->second, own_end_point, p, u, d)) {
						if (d < mind) {
							body_surface = kt->first;
							layer_body_intersection = kt->second;
							mind = d;
						}
					}
				}

				GeomAPI_IntCS intersection2(layer_body_intersection, plane);
				if (intersection2.IsDone() && intersection2.NbPoints() == 1) {
					const gp_Pnt& layer_end_point = intersection2.Point(1);
					GeomAPI_IntSS intersection3(surface, plane, 1.e-7);
					if (intersection3.IsDone() && intersection3.NbLines() == 1) {
						Handle_Geom_Curve layer_line = intersection3.Line(1);
						GeomAdaptor_Curve layer_line_adaptor(layer_line);
						ShapeAnalysis_Curve sac;
						gp_Pnt layer_end_point_projected; double layer_end_point_param;
						sac.Project(layer_line, layer_end_point, 1e-3, layer_end_point_projected, layer_end_point_param, false);

						GCPnts_AbscissaPoint dst(layer_line_adaptor, layer_offset, layer_end_point_param);
						if (dst.IsDone()) {
							gp_Pnt layer_fold_point;
							layer_line->D0(dst.Parameter(), layer_fold_point);
							
							GeomAPI_IntSS intersection4(body_surface, plane, 1.e-7);
							if (intersection4.IsDone() && intersection4.NbLines() == 1) {
								Handle_Geom_Curve body_trim_curve = intersection4.Line(1);
								ShapeAnalysis_Curve sac2;
								gp_Pnt layer_fold_point_projected; double layer_fold_point_param;
								sac2.Project(body_trim_curve, layer_fold_point, 1.e-7, layer_fold_point_projected, layer_fold_point_param, false);
								Handle_Geom_Curve fold_curve = new Geom_OffsetCurve(body_trim_curve->Reversed(), layer_fold_point_projected.Distance(layer_fold_point), gp::DZ());

								Handle_Geom_Surface fold_surface = new Geom_SurfaceOfLinearExtrusion(fold_curve, gp::DZ());
								result_vector->push_back(fold_surface);
								folds_made = true;
							}
						}
					}
				}
					
			}
		
		}
	}

	return folds_made;
}

namespace {

#if OCC_VERSION_HEX >= 0x70200
	bool split(IfcGeom::Kernel&, const TopoDS_Shape& input, const TopTools_ListOfShape& operands, double eps, std::vector<TopoDS_Shape>& slices) {
		if (operands.Extent() < 2) {
			// Needs to have at least two cutting surfaces for the ordering based on surface containment to work.
			return false;
		}

		BRepAlgoAPI_Splitter split;
		TopTools_ListOfShape input_list;
		input_list.Append(input);
		split.SetArguments(input_list);
		split.SetTools(operands);
		split.SetNonDestructive(true);
		split.SetFuzzyValue(eps);
		split.Build();

		if (!split.IsDone()) {
			return false;
		} else {

			std::map<Geom_Surface*, int> surfaces;

			// NB 1, since first surface has been excluded
			int i = 1;
			for (TopTools_ListIteratorOfListOfShape it(operands); it.More(); it.Next(), ++i) {
				TopExp_Explorer exp(it.Value(), TopAbs_FACE);
				for (; exp.More(); exp.Next()) {
					surfaces.insert(std::make_pair(BRep_Tool::Surface(TopoDS::Face(exp.Current())).get(), i));
				}
			}

			// Count subshapes
			size_t n = 0;
			TopoDS_Iterator sit(split.Shape());
			for (; sit.More(); sit.Next()) {
				++n;
			}

			// Initialize storage
			slices.resize(n);

			sit.Initialize(split.Shape());
			for (; sit.More(); sit.Next()) {

				// Iterate over the faces of solid to find correspondence to original
				// splitting surfaces. For the outmost slices, there will be a single
				// corresponding surface, because the outmost surfaces that align with
				// the body geometry have not been added as operands. For intermediate
				// slices, two surface indices should be find that should be next to
				// each other in the array of input surfaces.

				TopExp_Explorer exp(sit.Value(), TopAbs_FACE);
				int min = std::numeric_limits<int>::max();
				int max = std::numeric_limits<int>::min();
				for (; exp.More(); exp.Next()) {
					auto ssrf = BRep_Tool::Surface(TopoDS::Face(exp.Current()));
					auto it = surfaces.find(ssrf.get());
					if (it != surfaces.end()) {
						if (it->second < min) {
							min = it->second;

						}
						if (it->second > max) {
							max = it->second;
						}
					}
				}

				int idx = std::numeric_limits<int>::max();
				if (min != std::numeric_limits<int>::max()) {
					if (min == 1 && max == 1) {
						idx = 0;
					} else if (min + 1 == max || min == max) {
						idx = min;
					}
				}

				if (idx < (int) slices.size()) {
					if (slices[idx].IsNull()) {
						slices[idx] = sit.Value();
						continue;
					}
				}

				Logger::Error("Unable to map layer geometry to material index");
				return false;
			}
		}

		return true;
	}
#else
	bool split(IfcGeom::Kernel& k, const TopoDS_Shape& input, const TopTools_ListOfShape& operands, double, std::vector<TopoDS_Shape>& slices) {
		TopTools_ListIteratorOfListOfShape it(operands);
		TopoDS_Shape i = input;
		for (; it.More(); it.Next()) {
			const TopoDS_Shape& s = it.Value();
			TopoDS_Shape a, b;

			Handle(Geom_Surface) surf;
			if (s.ShapeType() == TopAbs_FACE) {
				surf = BRep_Tool::Surface(TopoDS::Face(s));
			}

			if ((s.ShapeType() == TopAbs_FACE && k.split_solid_by_surface(i, surf, a, b)) ||
				(s.ShapeType() == TopAbs_SHELL && k.split_solid_by_shell(i, s, a, b)))
			{
				slices.push_back(b);
				i = a;	
			} else {
				return false;
			}
		}
		slices.push_back(i);
		return true;
	}
#endif
}

bool IfcGeom::Kernel::apply_folded_layerset(const IfcRepresentationShapeItems& items, const std::vector< std::vector<Handle_Geom_Surface> >& surfaces, const std::vector<const SurfaceStyle*>& styles, IfcRepresentationShapeItems& result) {
	Bnd_Box bb;
	TopoDS_Shape input;
	flatten_shape_list(items, input, false);

	typedef std::vector< std::vector<Handle_Geom_Surface> > folded_surfaces_t;
	typedef std::vector< std::pair< TopoDS_Face, std::pair<gp_Pnt, gp_Pnt> > > faces_with_mass_t;

	TopTools_ListOfShape shells;

	for (folded_surfaces_t::const_iterator it = surfaces.begin(); it != surfaces.end(); ++it) {
		if (it->empty()) {
			continue;
		} else if (it->size() == 1) {
			const Handle_Geom_Surface& surface = (*it)[0];
			double u1, v1, u2, v2;
			if (!project(surface, input, u1, v1, u2, v2)) {
				continue;
			}
			shells.Append(BRepBuilderAPI_MakeShell(surface, u1, v1, u2, v2).Shell());
		} else {
			faces_with_mass_t solids;		
			for (folded_surfaces_t::value_type::const_iterator jt = it->begin(); jt != it->end(); ++jt) {
				const Handle_Geom_Surface& surface = *jt;
				double u1, v1, u2, v2;
				if (!project(surface, input, u1, v1, u2, v2)) {
					continue;
				}
				TopoDS_Face face = BRepBuilderAPI_MakeFace(surface, u1, u2, v1, v2, 1.e-7).Face();
				gp_Pnt p, p1, p2; gp_Vec vu, vv, n;
				surface->D1((u1+u2)/2., (v1+v2)/2., p, vu, vv);
				n = vu ^ vv;
				p1 = p.Translated( n);
				p2 = p.Translated(-n);
				solids.push_back(std::make_pair(face, std::make_pair(p1, p2)));
			}
			

			if (solids.empty()) {
				continue;
			}

			faces_with_mass_t::iterator jt = solids.begin();
			TopoDS_Face& A = jt->first;
			TopoDS_Shape An = BRepPrimAPI_MakeHalfSpace(A, jt->second.second).Solid();
			for (++jt; jt != solids.end(); ++jt) {
				TopoDS_Face& B = jt->first;
				TopoDS_Shape Bn = BRepPrimAPI_MakeHalfSpace(B, jt->second.second).Solid();

				TopoDS_Shape a = BRepAlgoAPI_Cut(A, Bn);
				if (count(a, TopAbs_FACE) == 1) {
					A = TopoDS::Face(TopExp_Explorer(a, TopAbs_FACE).Current());
				}

				TopoDS_Shape b = BRepAlgoAPI_Cut(B, An);
				if (count(b, TopAbs_FACE) == 1) {
					B = TopoDS::Face(TopExp_Explorer(b, TopAbs_FACE).Current());
				}
			}

			BRepOffsetAPI_Sewing builder;
			for (faces_with_mass_t::const_iterator kt = solids.begin(); kt != solids.end(); ++kt) {
				builder.Add(kt->first);
			}
		
			builder.Perform();
			shells.Append(TopoDS::Shell(builder.SewedShape()));
		}
	}

	if (shells.Extent() == 0) {

		return false;

	} else if (shells.Extent() == 1) {
		
		for (IfcRepresentationShapeItems::const_iterator it = items.begin(); it != items.end(); ++it) {
			TopoDS_Shape a,b;
			if (split_solid_by_shell(it->Shape(), shells.First(), a, b)) {
				result.push_back(IfcRepresentationShapeItem(it->Placement(), b, styles[0] ? styles[0] : &it->Style()));
				result.push_back(IfcRepresentationShapeItem(it->Placement(), a, styles[1] ? styles[1] : &it->Style()));
			} else {
				continue;
			}
		}

		return true;

	} else {

		for (IfcRepresentationShapeItems::const_iterator it = items.begin(); it != items.end(); ++it) {

			const TopoDS_Shape& s = it->Shape();
			TopoDS_Solid sld;
			ensure_fit_for_subtraction(s, sld);

			std::vector<TopoDS_Shape> slices;
			if (split(*this, it->Shape(), shells, getValue(GV_PRECISION), slices) && slices.size() == styles.size()) {
				for (size_t i = 0; i < slices.size(); ++i) {
					result.push_back(IfcRepresentationShapeItem(it->Placement(), slices[i], styles[i] ? styles[i] : &it->Style()));
				}
			} else {
				return false;
			}
		}

		return true;

	}

}

bool IfcGeom::Kernel::apply_layerset(const IfcRepresentationShapeItems& items, const std::vector<Handle_Geom_Surface>& surfaces, const std::vector<const SurfaceStyle*>& styles, IfcRepresentationShapeItems& result) {
	if (surfaces.size() < 3) {

		return false;

	} else if (surfaces.size() == 3) {
		
		for (IfcRepresentationShapeItems::const_iterator it = items.begin(); it != items.end(); ++it) {
			TopoDS_Shape a,b;
			if (split_solid_by_surface(it->Shape(), surfaces[1], a, b)) {
				result.push_back(IfcRepresentationShapeItem(it->Placement(), b, styles[0] ? styles[0] : &it->Style()));
				result.push_back(IfcRepresentationShapeItem(it->Placement(), a, styles[1] ? styles[1] : &it->Style()));
			} else {
				continue;
			}
		}

		return true;

	} else {

		/*
		// Determine whether sequence of surfaces is consistent with surface normal, so that
		// layer operations are applied in the correct order. This seems to be always the case.
		Bnd_Box bb;
		for (IfcRepresentationShapeItems::const_iterator it = items.begin(); it != items.end(); ++it) {
			BRepBndLib::Add(it->Shape(), bb);
		}

		double x1, y1, z1, x2, y2, z2; 
		bb.Get(x1, y1, z1, x2, y2, z2);
		gp_Pnt p1(x1, y1, z1);
		gp_Pnt p2(x2, y2, z2);
		gp_Pnt avg = (p1.XYZ() + p2.XYZ()) / 2.;

		ShapeAnalysis_Surface sas1(surfaces[0]);
		ShapeAnalysis_Surface sas2(surfaces[1]);
		const gp_Pnt2d uv = sas1.ValueOfUV(avg, 1e-3);
		
		gp_Pnt ps1, ps2, mass;
		gp_Vec du1, dv1, du2, dv2;
		surfaces[0]->D1(uv.X(), uv.Y(), ps1, du1, dv1);
		const gp_Vec n1 = dv1.XYZ() ^ du1.XYZ();
		
		const bool reversed = gp_Dir(ps2.XYZ() - ps1.XYZ()).Dot(n1) < 0.;
		
		surfaces[surfaces.size() - 1]->D0(uv.X(), uv.Y(), mass);
		mass.ChangeCoord() += n1.XYZ();
		*/
		
		for (IfcRepresentationShapeItems::const_iterator it = items.begin(); it != items.end(); ++it) {

			const TopoDS_Shape& s = it->Shape();
			TopoDS_Solid sld;
			ensure_fit_for_subtraction(s, sld);

			TopTools_ListOfShape operands;
			for (unsigned i = 1; i < surfaces.size() - 1; ++i) {
				double u1, v1, u2, v2;
				if (!project(surfaces[i], sld, u1, v1, u2, v2)) {
					return false;
				}

				TopoDS_Face face = BRepBuilderAPI_MakeFace(surfaces[i], u1, u2, v1, v2, 1.e-7).Face();

				operands.Append(face);
			}

			std::vector<TopoDS_Shape> slices;
			if (split(*this, it->Shape(), operands, getValue(GV_PRECISION), slices) && slices.size() == styles.size()) {
				for (size_t i = 0; i < slices.size(); ++i) {
					result.push_back(IfcRepresentationShapeItem(it->Placement(), slices[i], styles[i] ? styles[i] : &it->Style()));
				}
			} else {
				return false;
			}
		}

		return true;
	}
}

IfcSchema::IfcRepresentation* IfcGeom::Kernel::find_representation(const IfcSchema::IfcProduct* product, const std::string& identifier) {
	if (!product->hasRepresentation()) return 0;
	IfcSchema::IfcProductRepresentation* prod_rep = product->Representation();
	IfcSchema::IfcRepresentation::list::ptr reps = prod_rep->Representations();
	for (IfcSchema::IfcRepresentation::list::it it = reps->begin(); it != reps->end(); ++it) {
		if ((**it).hasRepresentationIdentifier() && (**it).RepresentationIdentifier() == identifier) {
			return *it;
		}
	}
	return 0;
}

bool IfcGeom::Kernel::split_solid_by_surface(const TopoDS_Shape& input, const Handle_Geom_Surface& surface, TopoDS_Shape& front, TopoDS_Shape& back) {
	// Use an unbounded surface, that isolate part of the input shape,
	// to split this shape into two parts. Make sure that the addition
	// of the two result volumes matches that of the input.

	double u1, v1, u2, v2;
	if (!project(surface, input, u1, v1, u2, v2)) {
		return false;
	}

	TopoDS_Face face = BRepBuilderAPI_MakeFace(surface, u1, u2, v1, v2, 1.e-7).Face();
	gp_Pnt p, p1, p2; gp_Vec vu, vv, n;
	surface->D1((u1+u2)/2., (v1+v2)/2., p, vu, vv);
	n = vu ^ vv;
	p1 = p.Translated(-n);
	TopoDS_Solid solid = BRepPrimAPI_MakeHalfSpace(face, p1).Solid();

	const bool b = split_solid_by_shell(input, solid, front, back);
	return b;
}

bool IfcGeom::Kernel::split_solid_by_shell(const TopoDS_Shape& input, const TopoDS_Shape& shell, TopoDS_Shape& front, TopoDS_Shape& back) {
	// Use a shell, typically one or more connected faces, that isolate part
	// of the input shape, to split this shape into two parts. Make sure that
	// the addition of the two result volumes matches that of the input.
	
	TopoDS_Solid solid;
	if (shell.ShapeType() == TopAbs_SHELL) {
		solid = BRepBuilderAPI_MakeSolid(TopoDS::Shell(shell)).Solid();
	} else if (shell.ShapeType() == TopAbs_SOLID) {
		solid = TopoDS::Solid(shell);
	} else {
		return false;
	}
	apply_tolerance(solid, getValue(GV_PRECISION));

#if OCC_VERSION_HEX >= 0x70300
	TopTools_ListOfShape shapes;
#else
	BOPCol_ListOfShape shapes;
#endif
	shapes.Append(input);
	shapes.Append(solid);
	BOPAlgo_PaveFiller filler(new NCollection_IncAllocator); // TODO: Does this need to be freed?
	filler.SetArguments(shapes);
	filler.Perform();
	front = BRepAlgoAPI_Cut(input, solid, filler);
	back = BRepAlgoAPI_Common(input, solid, filler);

	bool is_null[2];

	for (int i = 0; i < 2; ++i) {
		TopoDS_Shape& shape = i == 0 ? front : back;
        const bool result_is_null = is_null[i] = shape.IsNull() != 0;
		if (result_is_null) {
			continue;
		}
		try {
			ShapeFix_Shape fix(shape);
			if (fix.Perform()) {
				shape = fix.Shape();
			}
		} catch (const Standard_Failure& e) {
			if (e.GetMessageString() && strlen(e.GetMessageString())) {
				Logger::Error(e.GetMessageString());
			} else {
				Logger::Error("Unknown error performing fixes");
			}
		} catch (...) {
			Logger::Error("Unknown error performing fixes");
		}
		BRepCheck_Analyzer analyser(shape);
		bool is_valid = analyser.IsValid() != 0;
		if (!is_valid) {
			return false;
		}
	}

	if (is_null[0] || is_null[1]) {
		Logger::Message(Logger::LOG_ERROR, "Null result obtained from layerset slicing");
		if (is_null[0] && is_null[1]) {
			return false;
		}
	}

	const double ab = shape_volume(input);
	const double a  = shape_volume(front);
	const double b  = shape_volume(back);

	return ALMOST_THE_SAME(ab, a+b, 1.e-3);
}

bool IfcGeom::Kernel::project(const Handle_Geom_Surface& srf, const TopoDS_Shape& shp, double& u1, double& v1, double& u2, double& v2, double widen) {
	// @todo std::unique_ptr for C++11
	ShapeAnalysis_Surface* sas = 0;
	Handle(Geom_Plane) pln;

	if (srf->DynamicType() == STANDARD_TYPE(Geom_Plane)) {
		// Optimize projection for specific cases
		pln = Handle(Geom_Plane)::DownCast(srf);
	} else if (srf->DynamicType() == STANDARD_TYPE(Geom_OffsetSurface) && Handle(Geom_OffsetSurface)::DownCast(srf)->BasisSurface()->DynamicType() == STANDARD_TYPE(Geom_Plane)) {
		// For an offset planar surface the projected UV coords are the same as the basis surface
		pln = Handle(Geom_Plane)::DownCast(Handle(Geom_OffsetSurface)::DownCast(srf)->BasisSurface());
	} else {
		sas = new ShapeAnalysis_Surface(srf);
	}

	u1 = v1 = +std::numeric_limits<double>::infinity();
	u2 = v2 = -std::numeric_limits<double>::infinity();

	gp_Pnt median;
	int vertex_count = 0;
	for (TopExp_Explorer exp(shp, TopAbs_VERTEX); exp.More(); exp.Next(), ++vertex_count) {
		gp_Pnt p = BRep_Tool::Pnt(TopoDS::Vertex(exp.Current()));
		median.ChangeCoord() += p.XYZ();

		gp_Pnt2d uv;
		if (sas) {
			uv = sas->ValueOfUV(p, 1e-3);
		} else {
			gp_Vec d = p.XYZ() - pln->Position().Location().XYZ();
			uv.SetX(d.Dot(pln->Position().XDirection()));
			uv.SetY(d.Dot(pln->Position().YDirection()));
		}
		
		if (uv.X() < u1) u1 = uv.X();
		if (uv.Y() < v1) v1 = uv.Y();
		if (uv.X() > u2) u2 = uv.X();
		if (uv.Y() > v2) v2 = uv.Y();
	}

	if (vertex_count > 0) {

		// Add a little bit of resolution so that the median is shifted towards the mass
		// of the curve. This helps to find the parameter ordering for conic surfaces.
		for (TopExp_Explorer exp(shp, TopAbs_EDGE); exp.More(); exp.Next(), ++vertex_count) {
			const TopoDS_Edge& e = TopoDS::Edge(exp.Current());

			double a, b;
			Handle_Geom_Curve crv = BRep_Tool::Curve(e, a, b);
			gp_Pnt p;
			crv->D0((a + b) / 2., p);

			median.ChangeCoord() += p.XYZ();
		}

		median.ChangeCoord().Divide(vertex_count);
		gp_Pnt2d uv;
		if (sas) {
			uv = sas->ValueOfUV(median, 1e-3);
		} else {
			gp_Vec d = median.XYZ() - pln->Position().Location().XYZ();
			uv.SetX(d.Dot(pln->Position().XDirection()));
			uv.SetY(d.Dot(pln->Position().YDirection()));
		}

		if (uv.X() < u1 || uv.X() > u2) {
			std::swap(u1, u2);
		}

		u1 -= widen;
		u2 += widen;
		v1 -= widen;
		v2 += widen;

	}

	delete sas;	
	return vertex_count > 0;
}

const IfcSchema::IfcRepresentationItem* IfcGeom::Kernel::find_item_carrying_style(const IfcSchema::IfcRepresentationItem* item) {
	if (item->StyledByItem()->size()) {
		return item;
	}

	while (item->is(IfcSchema::Type::IfcBooleanClippingResult)) {
		// All instantiations of IfcBooleanOperand (type of FirstOperand) are subtypes of
		// IfcGeometricRepresentationItem
		item = (IfcSchema::IfcGeometricRepresentationItem*) ((IfcSchema::IfcBooleanClippingResult*) item)->FirstOperand();
		if (item->StyledByItem()->size()) {
			return item;
		}
	}

	// TODO: Ideally this would be done for other entities (such as IfcCsgSolid) as well.
	// But neither are these very prevalent, nor does the current IfcOpenShell style
	// mechanism enable to conveniently style subshapes, which would be necessary for
	// distinctly styled union operands.

	return item;
}

bool IfcGeom::Kernel::is_identity_transform(IfcUtil::IfcBaseClass* l) {
	IfcSchema::IfcAxis2Placement2D* ax2d;
	IfcSchema::IfcAxis2Placement3D* ax3d;

	IfcSchema::IfcCartesianTransformationOperator2D* op2d;
	IfcSchema::IfcCartesianTransformationOperator3D* op3d;
	IfcSchema::IfcCartesianTransformationOperator2DnonUniform* op2dnonu;
	IfcSchema::IfcCartesianTransformationOperator3DnonUniform* op3dnonu;

	if((op2dnonu = l->as<IfcSchema::IfcCartesianTransformationOperator2DnonUniform>()) != 0) {
		gp_GTrsf2d gtrsf2d;
		convert(op2dnonu, gtrsf2d);
		return gtrsf2d.Form() == gp_Identity;
	} else if ((op2d = l->as<IfcSchema::IfcCartesianTransformationOperator2D>()) != 0) {
		gp_Trsf2d trsf2d;
		convert(op2d, trsf2d);
		return trsf2d.Form() == gp_Identity;
	} else if((op3dnonu = l->as<IfcSchema::IfcCartesianTransformationOperator3DnonUniform>()) != 0) {
		gp_GTrsf gtrsf;
		convert(op3dnonu, gtrsf);
		return gtrsf.Form() == gp_Identity;
	} else if ((op3d = l->as<IfcSchema::IfcCartesianTransformationOperator3D>()) != 0) {
		gp_Trsf trsf;
		convert(op3d, trsf);
		return trsf.Form() == gp_Identity;
	} else if((ax2d = l->as<IfcSchema::IfcAxis2Placement2D>()) != 0) {
		gp_Trsf2d trsf2d;
		convert(ax2d, trsf2d);
		return trsf2d.Form() == gp_Identity;
	} else if ((ax3d = l->as<IfcSchema::IfcAxis2Placement3D>()) != 0) {
		gp_Trsf trsf;
		convert(ax3d, trsf);
		return trsf.Form() == gp_Identity;
	} else {
		throw IfcParse::IfcException("Invalid valuation for IfcAxis2Placement / IfcCartesianTransformationOperator");
	}
}

bool IfcGeom::Kernel::approximate_plane_through_wire(const TopoDS_Wire& wire, gp_Pln& plane) {
	// Newell's Method is used for the normal calculation
	// as a simple edge cross product can give opposite results
	// for a concave face boundary.
	// Reference: Graphics Gems III p. 231

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
	return true;
}

bool IfcGeom::Kernel::flatten_wire(TopoDS_Wire& wire) {
	gp_Pln pln;
	if (!approximate_plane_through_wire(wire, pln)) {
		return false;
	}
	TopoDS_Face face = BRepBuilderAPI_MakeFace(pln).Face();
	BRepAlgo_NormalProjection proj(face);
	proj.Add(wire);
	proj.Build();
	if (!proj.IsDone()) {
		return false;
	}
	TopTools_ListOfShape list;
	proj.BuildWire(list);
	if (list.Extent() != 1) {
		return false;
	}
	wire = TopoDS::Wire(list.First());
	return true;
}

bool IfcGeom::Kernel::triangulate_wire(const TopoDS_Wire& wire, TopTools_ListOfShape& faces) {
	// This is a bit of a precarious approach, but seems to work for the 
	// versions of OCCT tested for. OCCT has a Delaunay triangulation function 
	// BRepMesh_Delaun, but it is notoriously hard to interpret the results 
	// (due to the Bowyer-Watson super triangle perhaps?). Therefore 
	// alternatively we use the regular OCCT incremental mesher on a new face 
	// created from the UV coordinates of the original wire. Pray to our gods 
	// that the vertex coordinates are unaffected by the meshing algorithm and 
	// map them back to 3d coordinates when iterating over the mesh triangles. 

	typedef std::pair<double, double> uv_node;

	gp_Pln pln;
	if (!approximate_plane_through_wire(wire, pln)) {
		return false;
	}

	const gp_XYZ& udir = pln.Position().XDirection().XYZ();
	const gp_XYZ& vdir = pln.Position().YDirection().XYZ();
	const gp_XYZ& pnt = pln.Position().Location().XYZ();
	
	BRepTools_WireExplorer exp(wire);
	BRepBuilderAPI_MakePolygon mp;
	std::map<uv_node, gp_Pnt> mapping;

	// Add UV coordinates to a newly created polygon
	for (; exp.More(); exp.Next()) {
		gp_Pnt p = BRep_Tool::Pnt(exp.CurrentVertex());
		double u = (p.XYZ() - pnt).Dot(udir);
		double v = (p.XYZ() - pnt).Dot(vdir);
		mp.Add(gp_Pnt(u, v, 0));
		mapping.insert(std::make_pair(std::make_pair(u, v), p));
	}

	// Not closed by default
	mp.Close();

	// Create a new face from the {u,v,0} wire and mesh the face
	TopoDS_Face face = BRepBuilderAPI_MakeFace(mp.Wire());
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
			BRepBuilderAPI_MakePolygon mp2;
			for (int j = 0; j < 3; ++j) {
				const gp_Pnt& uv = nodes.Value(n123[j]);
				uv_node key = std::make_pair(uv.X(), uv.Y());

				if (mapping.find(key) == mapping.end()) {
					Logger::Error("Internal error: unable to unproject uv-mesh");
					return false;
				}

				const gp_Pnt& p = mapping.find(key)->second;
				mp2.Add(p);
			}
			mp2.Close();

			BRepBuilderAPI_MakeFace mf(mp2.Wire());
			if (mf.IsDone()) {
				TopoDS_Face triangle_face = mf.Face();
				TopoDS_Iterator jt(triangle_face, false);
				for (; jt.More(); jt.Next()) {
					const TopoDS_Wire& w = TopoDS::Wire(jt.Value());
					if (w.Orientation() != wire.Orientation()) {
						triangle_face.Reverse();
					}
				}
				faces.Append(triangle_face);
			}
		}
	}

	return true;
}

TopoDS_Shape IfcGeom::Kernel::apply_transformation(const TopoDS_Shape& s, const gp_Trsf& t) {
	if (t.Form() == gp_Identity) {
		return s;
	} else {
		/// @todo set to 1. and exactly 1. or use epsilon?
		if (t.ScaleFactor() != 1.) {
			return BRepBuilderAPI_Transform(s, t, true);
		} else {
			return s.Moved(t);
		}
	}
}

TopoDS_Shape IfcGeom::Kernel::apply_transformation(const TopoDS_Shape& s, const gp_GTrsf& t) {
	if (t.Form() == gp_Other) {
		return BRepBuilderAPI_GTransform(s, t, true);
	} else {

		return apply_transformation(s, t.Trsf());
	}
}

namespace {

	/*
	 * A small helper utility to wrap around a numeric range
	*/
	class bounded_int {
	private:
		int i;
		size_t n;
	public:
		bounded_int(int i, size_t n) : i(i), n(n) {}

		bounded_int& operator--() {
			--i;
			if (i == -1) {
				i = n - 1;
			}
			return *this;
		}

		bounded_int& operator++() {
			++i;
			if (i == (int) n) {
				i = 0;
			}
			return *this;
		}

		operator int() { return i; }
	};

	inline std::string format_pnt(const gp_Pnt& p) {
		std::stringstream ss;
		ss << std::fixed << std::setprecision(4) << p.X() << " " << p.Y() << " " << p.Z();
		return ss.str();
	}

	inline std::string format_edge(const TopoDS_Edge& e) {
		std::stringstream ss;
		TopoDS_Vertex v1, v2;
		TopExp::Vertices(e, v1, v2);
		gp_Pnt p1 = BRep_Tool::Pnt(v1);
		gp_Pnt p2 = BRep_Tool::Pnt(v2);
		ss << "edge " << format_pnt(p1) << " -> " << format_pnt(p2);
		return ss.str();
	}

}

bool IfcGeom::Kernel::wire_intersections(const TopoDS_Wire& wire, TopTools_ListOfShape& wires) {
	if (!wire.Closed()) {
		wires.Append(wire);
		return false;
	}

	int n = count(wire, TopAbs_EDGE);
	if (n < 3) {
		wires.Append(wire);
		return false;
	}

	// Note: initialize empty
	Handle(ShapeExtend_WireData) wd = new ShapeExtend_WireData();

	// ... to be sure to get consecutive edges
	BRepTools_WireExplorer exp(wire);
	IfcGeom::impl::tree<int> tree;

	int edge_idx = 0;
	for (; exp.More(); exp.Next()) {
		wd->Add(exp.Current());
		if (n > 64) {
			// tfk: indices in tree are 0-based vd 1-based in wiredata
			tree.add(edge_idx++, exp.Current());
		}
	}

	if (wd->NbEdges() != n) {
		// If the number of edges differs, BRepTools_WireExplorer did not
		// reach every edge, probably due to loops exactly at vertex locations.
		// This is not supported by this algorithm which only elimates loops
		// due to edge crossings.

		throw geometry_exception("Invalid loop");
	}
	
	bool intersected = false;

	// tfk: Extrema on infinite curves proved to be more robust.
	// TopoDS_Face face = BRepBuilderAPI_MakeFace(wire, true).Face();
	// ShapeAnalysis_Wire saw(wd, face, getValue(GV_PRECISION));
	
	const double eps = (std::min)(min_edge_length(wire) / 2., getValue(GV_PRECISION) * 10.);

	for (int i = 2; i < n; ++i) {

		std::vector<int> js;
		if (n > 64) {
			Bnd_Box b;
			BRepBndLib::Add(wd->Edge(i + 1), b);
			b.Enlarge(eps);
			js = tree.select_box(b, false);
		} else {
			boost::push_back(js, boost::irange(0, i - 1));
		}

		for(std::vector<int>::const_iterator it = js.begin(); it != js.end(); ++it) {
            int j = *it;

			if (n > 64) {
				if (j > i) {
					continue;
				}
				if ((std::max)(i, j) - (std::min)(i, j) <= 1) {
					continue;
				}
			} 
			
			// Only check non-consecutive edges
			if (i == n - 1 && j == 0) continue;
			
			bool unbounded_intersects;

			double u11, u12, u21, u22, U1, U2;
			GeomAPI_ExtremaCurveCurve ecc(
				BRep_Tool::Curve(wd->Edge(i + 1), u11, u12),
				BRep_Tool::Curve(wd->Edge(j + 1), u21, u22)
			);

			// @todo: extend this to work in case of multiple extrema and curved segments.
			if ((unbounded_intersects = (ecc.NbExtrema() == 1 && ecc.Distance(1) < eps))) {
				ecc.Parameters(1, U1, U2);
			}

			if (u11 > u12) {
				std::swap(u11, u12);
			}
			if (u21 > u22) {
				std::swap(u21, u22);
			}

			/// @todo: tfk: probably need different thresholds on non-linear curves
			u11 -= eps;
			u12 += eps;
			u21 -= eps;
			u22 += eps;

			// tfk: code below is for ShapeAnalysis_Wire::CheckIntersectingEdges()
			// IntRes2d_SequenceOfIntersectionPoint points2d;
			// TColgp_SequenceOfPnt points3d;
			// TColStd_SequenceOfReal errors;
			// if (saw.CheckIntersectingEdges(i + 1, j + 1, points2d, points3d, errors)) {

			if (unbounded_intersects &&	u11 < U1 && U1 < u12 && u21 < U2 && U2 < u22) {

				intersected = true;

				// Explore a forward and backward cycle from the intersection point
				for (int fb = 0; fb <= 1; ++fb) {
					const bool forward = fb == 0;

					BRepBuilderAPI_MakeWire mw;
					bool first = true;

					for (bounded_int k(j, n);;) {
						bool intersecting = k == j || k == i;
						if (intersecting) {
							TopoDS_Edge e = wd->Edge(k + 1);
							
							TopoDS_Vertex v1, v2;
							TopExp::Vertices(e, v1, v2, true);
							const TopoDS_Vertex* v = first == forward ? &v2 : &v1;

							// gp_Pnt p2 = points3d.Value(1);
							
							gp_Pnt p1 = BRep_Tool::Pnt(*v);
							gp_Pnt pp1, pp2;
							ecc.Points(1, pp1, pp2);
							const gp_Pnt& p2 = k == i ? pp1 : pp2;
							
							// Substitute with a new edge from/to the intersection point
							if (p1.Distance(p2) > getValue(GV_PRECISION) * 2) {
								double _, __;
								Handle_Geom_Curve crv = BRep_Tool::Curve(e, _, __);
								BRepBuilderAPI_MakeEdge me(crv, p1, p2);
								TopoDS_Edge ed = me.Edge();
								mw.Add(ed);
							}

							first = false;
						} else {
							// Re-use original edge
							mw.Add(wd->Edge(k+1));
						}

						if (k == i) {
							break;
						}

						if (forward) {
							++k;
						} else {
							--k;
						}
					}

					// Recursively process both cuts
					wire_intersections(mw.Wire(), wires);
				}

				return true;
			}
		}
	}

	// No intersections found, append original wire
	if (!intersected) {
		wires.Append(wire);
	}

	return intersected;
}

void IfcGeom::Kernel::select_largest(const TopTools_ListOfShape& shapes, TopoDS_Shape& largest) {
	double mass = 0.;	
	TopTools_ListIteratorOfListOfShape it(shapes);
	for (; it.More(); it.Next()) {
		/*
		// tfk: bounding box is more efficient probably
		const TopoDS_Wire& w = TopoDS::Wire(it.Value());
		TopoDS_Face face = BRepBuilderAPI_MakeFace(w).Face();
		const double m = face_area(face);
		*/

		Bnd_Box bb;
		BRepBndLib::AddClose(it.Value(), bb);
		double xyz_min[3], xyz_max[3];
		bb.Get(xyz_min[0], xyz_min[1], xyz_min[2], xyz_max[0], xyz_max[1], xyz_max[2]);
		const double eps = getValue(GV_PRECISION);

		double m = 1.;
		for (int i = 0; i < 3; ++i) {
			if (Precision::IsNegativeInfinite(xyz_min[i])) {
				xyz_min[i] = 0.;
			}
			if (Precision::IsInfinite(xyz_max[i])) {
				xyz_max[i] = 0.;
			}			
			m *= (xyz_max[i] + eps) - (xyz_min[i] - eps);
		}

		if (m > mass) {
			mass = m;
			largest = it.Value();
		}
	}
}

bool IfcGeom::Kernel::fit_halfspace(const TopoDS_Shape& a, const TopoDS_Shape& b, TopoDS_Shape& box, double& height) {
	TopExp_Explorer exp(b, TopAbs_FACE);
	if (!exp.More()) {
		return false;
	}

	TopoDS_Face face = TopoDS::Face(exp.Current());
	exp.Next();

	if (exp.More()) {
		return false;
	}

	Handle(Geom_Surface) surf = BRep_Tool::Surface(face);

	// const gp_XYZ xyz = a.Location().Transformation().TranslationPart();
	// std::cout << "dz " << xyz.Z() << std::endl;

	if (surf->DynamicType() != STANDARD_TYPE(Geom_Plane)) {
		return false;
	}

	Bnd_Box bb;
	BRepBndLib::Add(a, bb);

	if (bb.IsVoid()) {
		return false;
	}

	double xs[2], ys[2], zs[2];
	bb.Get(xs[0], ys[0], zs[0], xs[1], ys[1], zs[1]);

	gp_Pln pln = Handle(Geom_Plane)::DownCast(surf)->Pln();

	gp_Pnt P = pln.Position().Location();
	gp_Vec z = pln.Position().Direction();
	gp_Vec x = pln.Position().XDirection();
	gp_Vec y = pln.Position().YDirection();

	if (face.Orientation() != TopAbs_REVERSED) {
		z.Reverse();
	}

	double D, Umin, Umax, Vmin, Vmax;
	D = 0.;
	Umin = Vmin = +std::numeric_limits<double>::infinity();
	Umax = Vmax = -std::numeric_limits<double>::infinity();

	for (int i = 0; i < 2; ++i) {
		for (int j = 0; j < 2; ++j) {
			for (int k = 0; k < 2; ++k) {
				gp_Pnt p(xs[i], ys[j], zs[k]);
				
				gp_Vec d = p.XYZ() - P.XYZ();
				const double u = d.Dot(x);
				const double v = d.Dot(y);
				const double w = d.Dot(z);

				if (w > D) {
					D = w;
				}
				if (u < Umin) {
					Umin = u;
				}
				if (u > Umax) {
					Umax = u;
				}
				if (v < Vmin) {
					Vmin = v;
				}
				if (v > Vmax) {
					Vmax = v;
				}
			}
		}
	}

	const double eps = getValue(GV_PRECISION) * 1000.;

	BRepBuilderAPI_MakePolygon poly;
	poly.Add(P.XYZ() + x.XYZ() * (Umin - eps) + y.XYZ() * (Vmin - eps));
	poly.Add(P.XYZ() + x.XYZ() * (Umax + eps) + y.XYZ() * (Vmin - eps));
	poly.Add(P.XYZ() + x.XYZ() * (Umax + eps) + y.XYZ() * (Vmax + eps));
	poly.Add(P.XYZ() + x.XYZ() * (Umin - eps) + y.XYZ() * (Vmax + eps));
	poly.Close();

	BRepBuilderAPI_MakeFace mf(surf, poly.Wire(), true);

	gp_Vec vec = gp_Vec(z.XYZ() * (D + eps));

	BRepPrimAPI_MakePrism mp(mf.Face(), vec);
	box = mp.Shape();
	
	height = D;
	return true;
}

#if OCC_VERSION_HEX < 0x60900
bool IfcGeom::Kernel::boolean_operation(const TopoDS_Shape& a, const TopTools_ListOfShape& b, BOPAlgo_Operation op, TopoDS_Shape& result) {
	result = a;
	TopTools_ListIteratorOfListOfShape it(b);
	for (; it.More(); it.Next()) {
		TopoDS_Shape r;
		if (!boolean_operation(result, it.Value(), op, r)) {
			return false;
		}
		result = r;
	}
	return true;
}
bool IfcGeom::Kernel::boolean_operation(const TopoDS_Shape& a, const TopoDS_Shape& b, BOPAlgo_Operation op, TopoDS_Shape& result) {
	bool succesful = true;
	BRepAlgoAPI_BooleanOperation* builder;
	if (op == BOPAlgo_CUT) {
		builder = new BRepAlgoAPI_Cut(a, b);
	} else if (op == BOPAlgo_COMMON) {
		builder = new BRepAlgoAPI_Common(a, b);
	} else if (op == BOPAlgo_FUSE) {
		builder = new BRepAlgoAPI_Fuse(a, b);
	} else {
		return false;
	}
	if (builder->IsDone()) {
		TopoDS_Shape r = *builder;
		succesful = BRepCheck_Analyzer(r).IsValid() != 0;
		if (succesful) {
			result = r;

			ShapeFix_Shape fix(result);
			try {
				fix.Perform();
				result = fix.Shape();
			} catch (...) {
				Logger::Message(Logger::LOG_WARNING, "Shape healing failed on boolean result");
			}

		} else {
			// Increase tolerance max 3 times until succesful
			TopoDS_Shape a2 = a;
			TopoDS_Shape b2 = b;
			ShapeAnalysis_ShapeTolerance tolerance;
			const double t1 = tolerance.Tolerance(a, 1) * 10.;
			const double t2 = tolerance.Tolerance(b, 1) * 10.;
			if (((std::max)(t1, t2) + 1e-15) > getValue(GV_PRECISION) * 1000.) {
				return false;
			}
			apply_tolerance(a2, t1);
			apply_tolerance(b2, t2);
			succesful = boolean_operation(a2, b2, op, result);
		}
	}
	delete builder;
	return succesful;
}
#else
bool IfcGeom::Kernel::boolean_operation(const TopoDS_Shape& a, const TopTools_ListOfShape& b_, BOPAlgo_Operation op, TopoDS_Shape& result, double fuzziness) {
	bool success = false;
	BRepAlgoAPI_BooleanOperation* builder;
	TopTools_ListOfShape B, b;
	if (op == BOPAlgo_CUT) {
		builder = new BRepAlgoAPI_Cut();
		bounding_box_overlap(getValue(GV_PRECISION), a, b_, b);
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

	if (fuzziness < 0.) {
		fuzziness = getValue(GV_PRECISION);
	}

	// Find a sensible value for the fuzziness, based on precision
	// and limited by edge lengths and vertex-edge distances.
	const double len_a = min_edge_length(a);
	double min_length_orig = (std::min)(len_a, min_vertex_edge_distance(a, getValue(GV_PRECISION), len_a));
	TopTools_ListIteratorOfListOfShape it(b);
	for (; it.More(); it.Next()) {
		double d = min_edge_length(it.Value());
		if (d < min_length_orig) {
			min_length_orig = d;
		}
		d = min_vertex_edge_distance(it.Value(), getValue(GV_PRECISION), d);
		if (d < min_length_orig) {
			min_length_orig = d;
		}
	}

	const double fuzz = (std::min)(min_length_orig / 10., fuzziness);

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
			Logger::Message(Logger::LOG_WARNING, "Shape healing failed on boolean result");
		}

		success = BRepCheck_Analyzer(r).IsValid() != 0;

		if (success) {

			success = !is_manifold(a) || is_manifold(r);

			if (success) {
				
				// when there are edges or vertex-edge distances close to the used fuzziness, the  
				// output is not trusted and the operation is attempted with a higher fuzziness.
				double min_lengh_result = (std::min)(min_edge_length(r), min_vertex_edge_distance(r, getValue(GV_PRECISION), fuzziness * 10.));
				success = min_lengh_result <= min_length_orig || min_lengh_result > fuzziness * 10.;

				if (success) {
					result = r;
				} else {
					std::stringstream str;
					str << "Boolean operation result failing interference check, with fuzziness " << fuzziness << " min length " << min_lengh_result << " originally " << min_length_orig;
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
		str << "Error code :" << builder->ErrorStatus();
#endif
	Logger::Notice(str.str());
	}
	delete builder;
	if (!success) {
        const double new_fuzziness = fuzziness * 10.;
        if (new_fuzziness + 1e-15 <= getValue(GV_PRECISION) * 1000. && new_fuzziness < min_length_orig) {
            return boolean_operation(a, b, op, result, new_fuzziness);
        }
	}
	return success;
}

bool IfcGeom::Kernel::boolean_operation(const TopoDS_Shape& a, const TopoDS_Shape& b, BOPAlgo_Operation op, TopoDS_Shape& result, double fuzziness) {
	TopTools_ListOfShape bs;
	bs.Append(b);
	return boolean_operation(a, bs, op, result, fuzziness);
}
#endif
