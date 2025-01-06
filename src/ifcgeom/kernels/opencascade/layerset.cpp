#include "layerset.h"
#include "OpenCascadeConversionResult.h"

#include "base_utils.h"
#include "boolean_utils.h"

#include "../../../ifcparse/IfcLogger.h"

#include <BRep_Tool.hxx>

#include <TopoDS.hxx>
#include <TopoDS_Solid.hxx>
#include <TopoDS_Shell.hxx>
#include <TopoDS_Iterator.hxx>
#include <TopExp_Explorer.hxx>
#include <TopTools_ListOfShape.hxx>

#include <Bnd_Box.hxx>

#include <BRepBuilderAPI_MakeShell.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepBuilderAPI_MakeSolid.hxx>
#include <BRepAlgoAPI_Splitter.hxx>
#include <BRepPrimAPI_MakeHalfSpace.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepAlgoAPI_Common.hxx>
#include <BRepOffsetAPI_Sewing.hxx>
#include <BOPAlgo_PaveFiller.hxx>
#include <Standard_Version.hxx>
#include <BRepCheck_Analyzer.hxx>
#include <ShapeFix_Shape.hxx>
#include <NCollection_IncAllocator.hxx>

using namespace ifcopenshell::geometry;

namespace {

	void subshapes(const TopoDS_Shape& in, std::list<TopoDS_Shape>& out) {
		TopoDS_Iterator sit(in);
		for (; sit.More(); sit.Next()) {
			out.push_back(sit.Value());
		}
	}

#if OCC_VERSION_HEX >= 0x70200
	bool split(const TopoDS_Shape& input, const TopTools_ListOfShape& operands, double eps, std::vector<TopoDS_Shape>& slices) {
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

			auto result_shape = split.Shape();
			std::list<TopoDS_Shape> subs;
			subshapes(result_shape, subs);

			// Sometimes there is more nesting of compounds, so when we find a single compound we again try to explode it into a list.
			if (subs.size() == 1 && (subs.front().ShapeType() == TopAbs_COMPSOLID || subs.front().ShapeType() == TopAbs_COMPOUND)) {
				auto s = subs.front();
				subs.clear();
				subshapes(s, subs);
			}

			// Initialize storage
			slices.resize(subs.size());

			for (auto& s : subs) {

				// Iterate over the faces of solid to find correspondence to original
				// splitting surfaces. For the outmost slices, there will be a single
				// corresponding surface, because the outmost surfaces that align with
				// the body geometry have not been added as operands. For intermediate
				// slices, two surface indices should be find that should be next to
				// each other in the array of input surfaces.

				TopExp_Explorer exp(s, TopAbs_FACE);
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

				if (idx < (int)slices.size()) {
					if (slices[idx].IsNull()) {
						slices[idx] = s;
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
	bool split(const TopoDS_Shape& input, const TopTools_ListOfShape& operands, double, std::vector<TopoDS_Shape>& slices) {
		TopTools_ListIteratorOfListOfShape it(operands);
		TopoDS_Shape i = input;
		for (; it.More(); it.Next()) {
			const TopoDS_Shape& s = it.Value();
			TopoDS_Shape a, b;

			Handle(Geom_Surface) surf;
			if (s.ShapeType() == TopAbs_FACE) {
				surf = BRep_Tool::Surface(TopoDS::Face(s));
			}

			if ((s.ShapeType() == TopAbs_FACE && IfcGeom::util::split_solid_by_surface(i, surf, a, b)) ||
				(s.ShapeType() == TopAbs_SHELL && IfcGeom::util::split_solid_by_shell(i, s, a, b))) {
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


bool IfcGeom::util::apply_folded_layerset(const ConversionResults& items, const std::vector< std::vector<Handle_Geom_Surface> >& surfaces, const std::vector<ifcopenshell::geometry::taxonomy::style::ptr>& styles, ConversionResults& result, double tol) {
	Bnd_Box bb;
	TopoDS_Shape input;
	flatten_shape_list(items, input, false, false, tol);

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
				surface->D1((u1 + u2) / 2., (v1 + v2) / 2., p, vu, vv);
				n = vu ^ vv;
				p1 = p.Translated(n);
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
				if (util::count(a, TopAbs_FACE) == 1) {
					A = TopoDS::Face(TopExp_Explorer(a, TopAbs_FACE).Current());
				}

				TopoDS_Shape b = BRepAlgoAPI_Cut(B, An);
				if (util::count(b, TopAbs_FACE) == 1) {
					B = TopoDS::Face(TopExp_Explorer(b, TopAbs_FACE).Current());
				}
			}

			BRepOffsetAPI_Sewing builder;
			for (faces_with_mass_t::const_iterator kt = solids.begin(); kt != solids.end(); ++kt) {
				builder.Add(kt->first);
			}

			builder.Perform();
			TopoDS_Shape s = builder.SewedShape();
			if (s.ShapeType() == TopAbs_SHELL) {
				shells.Append(TopoDS::Shell(s));
			} else {
				Logger::Error("Expected shell type in layerset processing");
				return false;
			}
		}
	}

	if (shells.Extent() == 0) {

		return false;

	} else if (shells.Extent() == 1) {

		for (ConversionResults::const_iterator it = items.begin(); it != items.end(); ++it) {
			TopoDS_Shape a, b;
			if (split_solid_by_shell(std::static_pointer_cast<OpenCascadeShape>(it->Shape())->shape(), shells.First(), a, b, tol)) {
				result.push_back(ConversionResult(it->ItemId(), it->Placement(), new OpenCascadeShape(b), (!!styles[0] ? styles[0] : it->StylePtr())));
				result.push_back(ConversionResult(it->ItemId(), it->Placement(), new OpenCascadeShape(a), (!!styles[1] ? styles[1] : it->StylePtr())));
			} else {
				continue;
			}
		}

		return true;

	} else {

		for (ConversionResults::const_iterator it = items.begin(); it != items.end(); ++it) {

			const TopoDS_Shape& s = std::static_pointer_cast<OpenCascadeShape>(it->Shape())->shape();
			TopoDS_Shape sld = ensure_fit_for_subtraction(s, tol);

			std::vector<TopoDS_Shape> slices;
			if (split(s, shells, tol, slices) && slices.size() == styles.size()) {
				for (size_t i = 0; i < slices.size(); ++i) {
					result.push_back(ConversionResult(it->ItemId(), it->Placement(), new OpenCascadeShape(slices[i]), (!!styles[i] ? styles[i] : it->StylePtr())));
				}
			} else {
				return false;
			}
		}

		return true;

	}

}

bool IfcGeom::util::apply_layerset(const ConversionResults& items, const std::vector<Handle_Geom_Surface>& surfaces, const std::vector<ifcopenshell::geometry::taxonomy::style::ptr>& styles, ConversionResults& result, double tol) {
	if (surfaces.size() < 3) {

		return false;

	} else if (surfaces.size() == 3) {

		for (ConversionResults::const_iterator it = items.begin(); it != items.end(); ++it) {
			TopoDS_Shape a, b;
			if (split_solid_by_surface(std::static_pointer_cast<OpenCascadeShape>(it->Shape())->shape(), surfaces[1], a, b, tol)) {
				result.push_back(ConversionResult(it->ItemId(), it->Placement(),new OpenCascadeShape(b), (!!styles[0] ? styles[0] : it->StylePtr())));
				result.push_back(ConversionResult(it->ItemId(), it->Placement(),new OpenCascadeShape(a), (!!styles[1] ? styles[1] : it->StylePtr())));
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
		for (ConversionResults::const_iterator it = items.begin(); it != items.end(); ++it) {
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

		for (ConversionResults::const_iterator it = items.begin(); it != items.end(); ++it) {

			const TopoDS_Shape& s = std::static_pointer_cast<OpenCascadeShape>(it->Shape())->shape();
			TopoDS_Shape sld = ensure_fit_for_subtraction(s, tol);

			TopTools_ListOfShape operands;
			for (unsigned i = 1; i < surfaces.size() - 1; ++i) {
				double u1, v1, u2, v2;
				if (!project(surfaces[i], sld, u1, v1, u2, v2)) {
					return false;
				}

				TopoDS_Face face = BRepBuilderAPI_MakeFace(surfaces[i], u1, u2, v1, v2, 1.e-7).Face();

				operands.Append(face);
			}

			/*
			// enable this is you want to see how IfcOpenShell has placed the layer surfaces
			for (auto& x : operands) {
				result.push_back(ConversionResult(it->ItemId(), it->Placement(), x, nullptr));
			}
			*/

			std::vector<TopoDS_Shape> slices;
			if (split(s, operands, tol, slices) && slices.size() == styles.size()) {
				for (size_t i = 0; i < slices.size(); ++i) {
					result.push_back(ConversionResult(it->ItemId(), it->Placement(), new OpenCascadeShape(slices[i]), (!!styles[i] ? styles[i] : it->StylePtr())));
				}
			} else {
				return false;
			}
		}

		return true;
	}
}


bool IfcGeom::util::split_solid_by_surface(const TopoDS_Shape& input, const Handle_Geom_Surface& surface, TopoDS_Shape& front, TopoDS_Shape& back, double tol) {
	// Use an unbounded surface, that isolate part of the input shape,
	// to split this shape into two parts. Make sure that the addition
	// of the two result volumes matches that of the input.

	double u1, v1, u2, v2;
	if (!project(surface, input, u1, v1, u2, v2)) {
		return false;
	}

	TopoDS_Face face = BRepBuilderAPI_MakeFace(surface, u1, u2, v1, v2, 1.e-7).Face();
	gp_Pnt p, p1, p2; gp_Vec vu, vv, n;
	surface->D1((u1 + u2) / 2., (v1 + v2) / 2., p, vu, vv);
	n = vu ^ vv;
	p1 = p.Translated(-n);
	TopoDS_Solid solid = BRepPrimAPI_MakeHalfSpace(face, p1).Solid();

	const bool b = split_solid_by_shell(input, solid, front, back, tol);
	return b;
}

bool IfcGeom::util::split_solid_by_shell(const TopoDS_Shape& input, const TopoDS_Shape& shell, TopoDS_Shape& front, TopoDS_Shape& back, double tol) {
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
	const double a = shape_volume(front);
	const double b = shape_volume(back);

	return std::fabs(ab - (a + b)) < tol;
}
