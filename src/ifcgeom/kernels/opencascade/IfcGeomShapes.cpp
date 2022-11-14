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
#include "IfcGeomTree.h"

using namespace ifcopenshell::geometry; 
using namespace ifcopenshell::geometry::kernels;


#include <TopTools_DataMapOfShapeInteger.hxx>
#include <Geom_Plane.hxx>
#include <BRepLib_FindSurface.hxx>
#include <ShapeFix_Edge.hxx>
#include <BRepBuilderAPI_GTransform.hxx>


#include <Geom_Curve.hxx>
#include <Geom_Line.hxx>
#include <Approx_Curve3d.hxx>
#include <BRepAdaptor_CompCurve.hxx>
#include <BRepAdaptor_HCompCurve.hxx>
#include <Approx_Curve3d.hxx>

#include <ShapeBuild_ReShape.hxx>
#include <GC_MakeCircle.hxx>




#include <BRepTools_WireExplorer.hxx>


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
	sewing_builder.SetTolerance(settings_.getValue(ConversionSettings::GV_PRECISION));
	sewing_builder.SetMaxTolerance(settings_.getValue(ConversionSettings::GV_PRECISION));
	sewing_builder.SetMinTolerance(settings_.getValue(ConversionSettings::GV_PRECISION));

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
				solid.SetMaxTolerance(settings_.getValue(ConversionSettings::GV_PRECISION));
				TopoDS_Solid solid_shape = solid.SolidFromShell(TopoDS::Shell(exp.Current()));
				// @todo: BRepClass3d_SolidClassifier::PerformInfinitePoint() is done by SolidFromShell
				//        and this is done again, to be able to catch errors during this process.
				//        This is double work that should be avoided.
				if (!solid_shape.IsNull()) {
					try {
						BRepClass3d_SolidClassifier classifier(solid_shape);
						result_shape = solid_shape;
						classifier.PerformInfinitePoint(settings_.getValue(ConversionSettings::GV_PRECISION));
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

bool OpenCascadeKernel::boolean_operation(const TopoDS_Shape& a_, const TopTools_ListOfShape& b__, BOPAlgo_Operation op, TopoDS_Shape& result, double fuzziness) {

	if (fuzziness < 0.) {
		fuzziness = settings_.getValue(ConversionSettings::GV_PRECISION);
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
		bounding_box_overlap(settings_.getValue(ConversionSettings::GV_PRECISION), a, b_, b);
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
	double min_length_orig = (std::min)(len_a, min_vertex_edge_distance(a_, settings_.getValue(ConversionSettings::GV_PRECISION), len_a));
	TopTools_ListIteratorOfListOfShape it(b__);
	for (; it.More(); it.Next()) {
		double d = min_edge_length(it.Value());
		if (d < min_length_orig) {
			min_length_orig = d;
		}
		d = min_vertex_edge_distance(it.Value(), settings_.getValue(ConversionSettings::GV_PRECISION), d);
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
				} else if ((v = min_vertex_edge_distance(r, settings_.getValue(ConversionSettings::GV_PRECISION), fuzziness * 3.)) < fuzziness * 3.) {
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
		if (new_fuzziness - 1e-15 <= settings_.getValue(ConversionSettings::GV_PRECISION) * 10000. && new_fuzziness < min_length_orig) {
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
