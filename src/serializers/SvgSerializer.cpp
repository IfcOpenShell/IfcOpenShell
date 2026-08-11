/********************************************************************************
 *                                                                              *
 * Copyright 2015 IfcOpenShell and ROOT B.V.                                    *
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

#ifdef IFOPSH_WITH_OPENCASCADE

#include "../ifcgeom/abstract_mapping.h"

#include <string>
#include <fstream>
#include <cstdio>
#include <limits>
#include <algorithm>
#include <numeric>
#include <unordered_set>

#include <gp_Pln.hxx>
#include <gp_Trsf.hxx>
#include <gp_Circ.hxx>
#include <gp_Elips.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Edge.hxx>
#include <TopExp_Explorer.hxx>
#include <BRep_Tool.hxx>
#include <BRepTools.hxx>
#include <BRepTools_WireExplorer.hxx>
#include <BRepAlgoAPI_Section.hxx>
#include <ShapeAnalysis_FreeBounds.hxx>

#include <Standard_Version.hxx>
#if OCC_VERSION_HEX >= 0x80000
#include <Standard_Macro.hxx>
#include <TopoDS_Shape.hxx>
#include <NCollection_HSequence.hxx>
#else
#include <TopTools_HSequenceOfShape.hxx>
#endif

#include <TopExp.hxx>

#include <BRepAdaptor_Curve.hxx>
#include <GCPnts_QuasiUniformDeflection.hxx>

#include <Geom_Curve.hxx>
#include <Geom_Line.hxx>
#include <Geom_Plane.hxx>
#include <Geom_Circle.hxx>
#include <Geom_Ellipse.hxx>
#include <gp_Ax22d.hxx>
#include <GeomAPI.hxx>
#include <TopoDS_Wire.hxx>

#include <BRepBuilderAPI_Transform.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>

#include <BRepAlgoAPI_Cut.hxx>
#include <BRepPrimAPI_MakeHalfSpace.hxx>

#include <GProp_GProps.hxx>
#include <BRepGProp.hxx>
#include <BRepTopAdaptor_FClass2d.hxx>

#include <Bnd_Box.hxx>
#include <BRep_Builder.hxx>
#include <BRepBndLib.hxx>

#include <ShapeFix_Edge.hxx>
#include <ShapeFix_Shape.hxx>
#include <BRepCheck_Analyzer.hxx>

#include <HLRBRep_PolyHLRToShape.hxx>

#include <Extrema_ExtPElS.hxx>

#include "../ifcparse/IfcGlobalId.h"
#include "../ifcgeom/kernels/opencascade/base_utils.h"
#include "../ifcgeom/kernels/opencascade/boolean_utils.h"
#include "../ifcgeom/kernels/opencascade/wire_utils.h"

#include "../ifcgeom/kernels/opencascade/OpenCascadeConversionResult.h"

#include <boost/format.hpp>
#include <boost/tokenizer.hpp>

#include "SvgSerializer.h"

const double PI2 = M_PI * 2.;

bool SvgSerializer::ready() {
	svg_ridge_angle_min_deg_ = geometry_settings().get<ifcopenshell::geometry::settings::SvgRidgeAngleMinDegrees>().get();
	svg_valley_angle_min_deg_ = geometry_settings().get<ifcopenshell::geometry::settings::SvgValleyAngleMinDegrees>().get();
	svg_emit_flush_edges_ = geometry_settings().get<ifcopenshell::geometry::settings::SvgEmitFlushEdges>().get();
	svg_use_edge_classification_ = geometry_settings().get<ifcopenshell::geometry::settings::SvgUseEdgeClassification>().get();
	svg_render_crease_edges_ = geometry_settings().get<ifcopenshell::geometry::settings::SvgRenderCreaseEdges>().get();
	svg_render_sharp_edges_ = geometry_settings().get<ifcopenshell::geometry::settings::SvgRenderSharpEdges>().get();
	svg_use_cross_coplanar_classification_ = geometry_settings().get<ifcopenshell::geometry::settings::SvgUseCrossCoplanarClassification>().get();
	svg_render_cross_coplanar_edges_ = geometry_settings().get<ifcopenshell::geometry::settings::SvgRenderCrossCoplanarEdges>().get();
	svg_cross_coplanar_tolerance_ = geometry_settings().get<ifcopenshell::geometry::settings::SvgCrossCoplanarTolerance>().get();
	svg_use_mat_style_change_classification_ = geometry_settings().get<ifcopenshell::geometry::settings::SvgUseMatStyleChangeClassification>().get();
	return true;
}

void SvgSerializer::write(path_object& p, const TopoDS_Shape& comp_or_wire, boost::optional<std::vector<double>> dash_array, boost::optional<std::string> css_class) {
	/* ShapeFix_Wire fix;
	Handle(ShapeExtend_WireData) data = new ShapeExtend_WireData;
	for (TopExp_Explorer edges(result, TopAbs_EDGE); edges.More(); edges.Next()) {
		data->Add(edges.Current());
	}
	fix.Load(data);
	fix.FixReorder();
	fix.FixConnected();
	const TopoDS_Wire fixed_wire = fix.Wire(); */

	util::string_buffer path;

	std::list<TopoDS_Shape> wires;
	if (comp_or_wire.ShapeType() == TopAbs_WIRE) {
		wires.push_back(comp_or_wire);
	} else if (comp_or_wire.ShapeType() == TopAbs_COMPOUND) {
		TopoDS_Iterator it(comp_or_wire);
		for (; it.More(); it.Next()) {
			wires.push_back(it.Value());
		}
	}

	bool first_wire = true;

	for (auto& wire : wires) {

		bool first = true;

		for (TopExp_Explorer edges(wire, TopAbs_EDGE); edges.More(); edges.Next()) {
			const TopoDS_Edge& edge = TopoDS::Edge(edges.Current());

			double u1, u2;
			Handle(Geom_Curve) curve = BRep_Tool::Curve(edge, u1, u2);
			Handle(Geom2d_Curve) curve2d;
			if (curve.IsNull()) {
				TopLoc_Location loc;
				opencascade::handle<Geom_Surface> surf;

				BRep_Tool::CurveOnSurface(edge, curve2d, surf, loc, u1, u2);

				if (curve2d.IsNull()) {
					logger_.Error("SER", 20, "Failed to obtain 2d and 3d curve from edge");
					continue;
				}

				Handle(Standard_Type) sty = surf->DynamicType();
				if (sty != STANDARD_TYPE(Geom_Plane)) {
					logger_.Error("SER", 21, "Non-planar p-curves are not supported by this serializer");
					continue;
				}

				gp_Pln pln = Handle(Geom_Plane)::DownCast(surf)->Pln();
				curve = GeomAPI::To3d(curve2d, pln);
			}

			Handle(Standard_Type) ty = curve->DynamicType();
			bool conical = (ty == STANDARD_TYPE(Geom_Circle) || ty == STANDARD_TYPE(Geom_Ellipse));

			// TODO: ALMOST_THE_SAME utilities in separate header
			bool closed = fabs((u1 + PI2) - u2) < 1.e-9;

			// Write the element as a svg circle or ellipse. This isn't possible
			// when forced writing of polygonal output or when there are multiple
			// wires to be written.
			if (!polygonal_ && (conical && closed) && wires.size() == 1) {
				if (first) {
					if (ty == STANDARD_TYPE(Geom_Circle)) {
						Handle(Geom_Circle) circle = Handle(Geom_Circle)::DownCast(curve);
						double r = circle->Radius();
						gp_Circ c = circle->Circ();
						gp_Pnt center = c.Location();
						path.add("            <circle r=\"");
						radii.push_back(path.add(r));
						path.add("\" cx=\"");
						xcoords.push_back(path.add(center.X()));
						path.add("\" cy=\"");
						ycoords.push_back(path.add(center.Y()));

						growBoundingBox(center.X() - r, center.Y() - r);
						growBoundingBox(center.X() + r, center.Y() + r);

						first = false;
						continue;
					} else if (ty == STANDARD_TYPE(Geom_Ellipse)) {
						Handle(Geom_Ellipse) ellipse = Handle(Geom_Ellipse)::DownCast(curve);
						gp_Elips e = ellipse->Elips();
						gp_Pnt center = e.Location();

						// Write the ellipse with major radius along X axis:
						path.add("            <ellipse rx=\"");
						radii.push_back(path.add(e.MajorRadius()));
						path.add("\" ry=\"");
						radii.push_back(path.add(e.MinorRadius()));
						path.add("\" cx=\"");
						xcoords.push_back(path.add(center.X()));
						path.add("\" cy=\"");
						ycoords.push_back(path.add(center.Y()));
						path.add("\"");

						// Rotate it with "transform":
						gp_Ax1 major_axis = e.XAxis();
						double z_rotation = major_axis.Direction().AngleWithRef(gp_Dir(1., 0., 0.), gp_Dir(0., 0., 1.));
						path.add(" transform=\"rotate(");
						path.add(z_rotation);
						path.add(" ");
						path.add(center.X());
						path.add(" ");
						path.add(center.Y());
						// @todo isn't there a ")" missing here?
						// @todo also X, Y are not added to {x,y}coords vector
						// @todo also z_rotation is in radians, should be in degrees

						// Bounding box:
						// More important to have all geometry in bounding box than to be minimal
						growBoundingBox(center.X() - e.MajorRadius(), center.Y() - e.MajorRadius());
						growBoundingBox(center.X() + e.MajorRadius(), center.Y() + e.MajorRadius());

						first = false;
						continue;
					}
				} else {
					std::stringstream ss;
					ss << "Skipping full circle/ellipse inside aggregated <path> (id "
						<< p.first << ")";
					logger_.Warning("SER", 22, ss.str());
				}
			}

			const bool reversed = edge.Orientation() == TopAbs_REVERSED;

			gp_Pnt p1, p2;
			curve->D0(u1, p1);
			curve->D0(u2, p2);

			if (reversed) {
				std::swap(p1, p2);
			}

			// p1/p2 are in model-space (metres) at this point -- the paper-space mm
			// scale factor (scale_ * 1000) isn't applied until the later, deferred
			// SvgSerializer::resize() pass (which patches every already-buffered
			// xcoords/ycoords float_item in place once the whole drawing's bounding
			// box is known). scale_ is set earlier in the pipeline, from the
			// drawing's own EPset_Drawing.Scale, so it's already available here for
			// the common case (an explicit drawing scale, as opposed to resize()'s
			// auto-fit calculated_scale_, which genuinely isn't known yet at this
			// point -- skip the filter in that rarer case rather than guess).
			// Threshold matches the old (now superseded) Python
			// join_coplanar_boundary_lines's MIN_VISIBLE_LENGTH precedent (0.1mm,
			// paper space).
			if (scale_) {
				constexpr double MIN_VISIBLE_LENGTH_MM = 0.1;
				if (p1.Distance(p2) * (*scale_) * 1000. < MIN_VISIBLE_LENGTH_MM) {
					continue;
				}
			}

			if (first) {
				if (first_wire) {
					path.add("            <path d=\"");
				} else {
					path.add(" ");
				}

				path.add("M");
				addXCoordinate(path.add(p1.X()));
				path.add(",");
				addYCoordinate(path.add(p1.Y()));

				growBoundingBox(p1.X(), p1.Y());
			}

			growBoundingBox(p2.X(), p2.Y());


			if (!polygonal_ && (ty == STANDARD_TYPE(Geom_Circle) || ty == STANDARD_TYPE(Geom_Ellipse))) {
				Handle(Geom_Conic) conic = Handle(Geom_Conic)::DownCast(curve);
				const bool mirrored = conic->Position().Axis().Direction().Z() < 0;

				double r1, r2;
				bool larger_arc_segment = (fmod(u2 - u1 + PI2, PI2) > M_PI);
				bool positive_direction = (u2 > u1);

				if (mirrored != reversed) {
					// In case the local coordinate system is mirrored
					// the direction is reversed.
					positive_direction = !positive_direction;
				}

				gp_Pnt center;
				if (ty == STANDARD_TYPE(Geom_Circle)) {
					Handle(Geom_Circle) circle = Handle(Geom_Circle)::DownCast(curve);
					r1 = r2 = circle->Radius();
					center = circle->Location();
				} else {
					Handle(Geom_Ellipse) ellipse = Handle(Geom_Ellipse)::DownCast(curve);
					r1 = ellipse->MajorRadius();
					r2 = ellipse->MinorRadius();
					center = ellipse->Location();
				}

				// Make sure the arc segment is entirely inside bounding box:
				growBoundingBox(center.X() - r1, center.Y() - r1);
				growBoundingBox(center.X() + r1, center.Y() + r1);

				// Calculate the angle between 2d vecs to have signed result
				const gp_Dir& d = conic->Position().XDirection();
				const gp_Dir2d d2(d.X(), d.Y());
				const double ang = closed ? M_PI * 2. : d2.Angle(gp::DX2d());

				// Write radii
				path.add(" A");
				addSizeComponent(path.add(r1));
				path.add(",");
				addSizeComponent(path.add(r2));

				// Write X-axis rotation
				{ std::stringstream ss; ss << " " << ang << " ";
				path.add(ss.str()); }

				// Write large-arc-flag and sweep-flag
				path.add(std::string(1, '0' + static_cast<int>(larger_arc_segment)));
				path.add(",");
				path.add(std::string(1, '0' + static_cast<int>(positive_direction)));

				path.add(" ");

				// Write arc end point
				xcoords.push_back(path.add(p2.X()));
				path.add(",");
				ycoords.push_back(path.add(p2.Y()));
			} else if (ty != STANDARD_TYPE(Geom_Line)) {
				BRepAdaptor_Curve crv(edge);
				GCPnts_QuasiUniformDeflection tessellater(crv, geometry_settings().get<ifcopenshell::geometry::settings::MesherLinearDeflection>().get());
				// NB: Start at 2: 1-based and skip the first point, assume it coincides with p1.
				for (int i = 2; i <= tessellater.NbPoints(); ++i) {
					gp_Pnt pi = tessellater.Value(i);
					path.add(" L");
					xcoords.push_back(path.add(pi.X()));
					path.add(",");
					ycoords.push_back(path.add(pi.Y()));

					growBoundingBox(pi.X(), pi.Y());
				}
			} else {
				// Either a Geom_Line or something unimplemented,
				// drawn as a straight line segment.
				path.add(" L");
				xcoords.push_back(path.add(p2.X()));
				path.add(",");
				ycoords.push_back(path.add(p2.Y()));
			}

			first = false;
		}

		first_wire = false;
	}

	if (!path.empty()) {
		path.add("\"");

		if (css_class) {
			path.add(" class=\"");
			path.add(*css_class);
			path.add("\"");
		}

		if (dash_array) {
			path.add(" stroke-dasharray=\"");
			bool first = true;
			for (auto& d : *dash_array) {
				if (!first) {
					path.add(" ");
				}
				first = false;
				radii.push_back(path.add(d));
			}
			path.add("\"");
		}

		path.add("/>\n");
		p.second.push_back(path);
	}
}

SvgSerializer::path_object& SvgSerializer::start_path(const gp_Pln& pln, const IfcUtil::IfcBaseEntity* storey, const std::string& id) {
	auto key = std::make_pair(std::make_pair(storey, ""), path_object());
	SvgSerializer::path_object& p = paths.insert(key)->second;
	drawing_metadata[key.first].pln_3d = pln;
	p.first = id;
	return p;
}

SvgSerializer::path_object& SvgSerializer::start_path(const gp_Pln& pln, const std::string& drawing_name, const std::string& id) {
	auto key = std::make_pair(std::make_pair(nullptr, drawing_name), path_object());
	SvgSerializer::path_object& p = paths.insert(key)->second;
	drawing_metadata[key.first].pln_3d = pln;
	p.first = id;
	return p;
}

namespace {
	boost::optional<std::pair<const IfcUtil::IfcBaseEntity*, double>> storey_elevation_from_element(const IfcGeom::BRepElement* o) {
		for (const auto& p : o->parents()) {
			if (p->type() == "IfcBuildingStorey") {
				try {
					double e = p->product()->get("Elevation");
					double storey_elevation = e * o->geometry().settings().get<ifcopenshell::geometry::settings::LengthUnit>().get();
					return std::make_pair(p->product(), storey_elevation);
				} catch (...) {
					continue;
				}
				break;
			}
		}
		return boost::none;
	}

	typedef std::pair<std::array<double, 3>, std::array<double, 3>> box_t;

	boost::optional<TopoDS_Edge> edge_from_compound(TopoDS_Shape& compound) {
		TopoDS_Iterator it(compound);
		if (it.More()) {
			TopoDS_Shape wire = it.Value();
			it.Next();
			if (!it.More() && wire.ShapeType() == TopAbs_WIRE) {
				TopoDS_Iterator jt(wire);
				if (jt.More()) {
					TopoDS_Shape edge = jt.Value();
					jt.Next();
					if (!jt.More() && edge.ShapeType() == TopAbs_EDGE) {
						return TopoDS::Edge(edge);
					}
				}
			}
		}
		return boost::none;
	}

	class almost {
	private:
		double v_, eps_;
	public:
		almost(double v, double eps = 1.e-7)
			: v_(v)
			, eps_(eps)
		{}

		bool operator==(double other) const {
			return std::fabs(other - v_) < eps_;
		}

		bool operator!=(double other) const {
			return !(*this == other);
		}
	};

	boost::optional<box_t> box_from_compound(TopoDS_Shape& compound) {
		/*
		// in v0.8 apparently we don't get a solid/shell anymore because
		// we no longer use PrimAPI, but rather resolve the box to an
		// explicit shell with 6 faces in the mapping, which - depending 
		// on settings - may remain solely a compound of 6.

		TopExp_Explorer exp(compound, TopAbs_SHELL);
		TopoDS_Shell shell;
		if (exp.More()) {
			shell = TopoDS::Shell(exp.Current());
			exp.Next();
			if (exp.More()) {
				return boost::none;
			}
		}
		else {
			return boost::none;
		}
		*/
		auto& shell = compound;

		if (IfcGeom::util::count(shell, TopAbs_FACE) != 6) {
			return boost::none;
		}

		TopExp_Explorer it(shell, TopAbs_FACE);
		for (; it.More(); it.Next()) {
			const auto& face = TopoDS::Face(it.Current());
			auto surf = BRep_Tool::Surface(face);
			if (surf->DynamicType() != STANDARD_TYPE(Geom_Plane)) {
				return boost::none;
			}
			auto pln = Handle(Geom_Plane)::DownCast(surf);
			auto dz = std::abs(pln->Position().Direction().Z());
			if (almost(0.) != dz && almost(1.) != dz) {
				return boost::none;
			}
			auto dy = std::abs(pln->Position().Direction().Y());
			if (almost(0.) != dy && almost(1.) != dy) {
				return boost::none;
			}
		}

		Bnd_Box b;
		BRepBndLib::Add(compound, b, false);

		double x0, y0, z0, x1, y1, z1;
		b.Get(x0, y0, z0, x1, y1, z1);

		return box_t{ {{x0, y0, z0}}, {{x1, y1, z1}} };
	}

	struct string_property {
		std::string pset_name, prop_name, value;
	};

	template <typename It>
	void enumerate_string_properties(const IfcUtil::IfcBaseEntity* product, It output_it) {
		auto rels = product->get_inverse("IsDefinedBy");
		for (auto& rel : *rels) {
			if (rel->declaration().is("IfcRelDefinesByProperties")) {
				auto pset = ((IfcUtil::IfcBaseClass*) ((IfcUtil::IfcBaseEntity*) rel)->get("RelatingPropertyDefinition"))->as<IfcUtil::IfcBaseEntity>();
				if (!pset->declaration().is("IfcPropertySet")) {
					continue;
                }
				std::string pset_name;
				if (!pset->get("Name").isNull()) {
					pset_name = (std::string) pset->get("Name");
				}
				aggregate_of_instance::ptr props = pset->get("HasProperties");
				for (auto& prop : *props) {
					if (prop->declaration().is("IfcPropertySingleValue")) {
						std::string name = ((IfcUtil::IfcBaseEntity*) prop)->get("Name");
                        if (((IfcUtil::IfcBaseEntity*) prop)->get("NominalValue").isNull()) {
                            continue;
                        }
						IfcUtil::IfcBaseClass* v = ((IfcUtil::IfcBaseEntity*) prop)->get("NominalValue");
						auto value = v->get_attribute_value(0);
						if (value.type() == IfcUtil::Argument_STRING) {
							std::string v_str = value;
							*output_it++ = string_property{ pset_name, name, v_str };
						}
					}
				}
			}
		}
	}
}

namespace {
	boost::optional<std::string> get_curve_style_name(IfcUtil::IfcBaseEntity* item) {
		auto refs = item->get_inverse("StyledByItem");
		for (auto& ref : *refs) {
			if (ref->declaration().is("IfcStyledItem")) {
				aggregate_of_instance::ptr styles = ((IfcUtil::IfcBaseEntity*)ref)->get("Styles");
				for (auto& s_ : *styles) {
					auto s = (IfcUtil::IfcBaseEntity*) s_;
					std::vector<IfcUtil::IfcBaseEntity*> pss;
					if (s->declaration().is("IfcPresentationStyleAssignment")) {
						aggregate_of_instance::ptr pstyles = s->get("Styles");
						for (auto& ssss : *pstyles) {
							pss.push_back((IfcUtil::IfcBaseEntity*) ssss);
						}
					} else {
						pss.push_back(s);
					}
					for (auto& ps : pss) {
						if (ps->declaration().is("IfcCurveStyle")) {
							auto arg = ps->get("Name");
							if (!arg.isNull()) {
								return (std::string) arg;
							}
						}
					}
				}
			}
		}
		return boost::none;
	}

	// Resolves the material genuinely associated with `product`, for the cross-coplanar
	// "same substance" comparison (issue #3742) -- schema-agnostic like get_curve_style_name()
	// above (walking get_inverse()/get() generically), since this file has no access to
	// mapping_'s typed Converter machinery. Mirrors the simple cases of
	// mapping::get_single_material_association() (Converter.cpp) run in its "layerset first"
	// mode: a direct IfcMaterial, or the *first* layer of an IfcMaterialLayerSet/-SetUsage
	// regardless of how many layers it has. Same per-product, whichever-resolves-first
	// simplification already accepted for cross_coplanar_style_instance -- the layer actually
	// touching a neighbour's face isn't tracked, so a multi-layer element's non-first-layer
	// matches are a known, accepted gap (documented alongside the style one). Other
	// multi-material constructs (profile sets, constituent sets) deliberately return nullptr
	// rather than guessing -- material only takes priority over style when it *is* resolved, so
	// an unresolved product just falls back to the existing style comparison, a safe default.
	IfcUtil::IfcBaseEntity* get_single_material_association(IfcUtil::IfcBaseEntity* product) {
		auto rels = product->get_inverse("HasAssociations");
		IfcUtil::IfcBaseEntity* relating_material = nullptr;
		size_t n_material_rels = 0;
		for (auto& ref : *rels) {
			if (ref->declaration().is("IfcRelAssociatesMaterial")) {
				n_material_rels++;
				auto arg = ((IfcUtil::IfcBaseEntity*) ref)->get("RelatingMaterial");
				if (!arg.isNull()) {
					relating_material = ((IfcUtil::IfcBaseClass*) arg)->as<IfcUtil::IfcBaseEntity>();
				}
			}
		}
		if (n_material_rels != 1 || !relating_material) {
			return nullptr;
		}

		if (relating_material->declaration().is("IfcMaterial")) {
			return relating_material;
		}

		if (relating_material->declaration().is("IfcMaterialLayerSetUsage") ||
			relating_material->declaration().is("IfcMaterialLayerSet"))
		{
			IfcUtil::IfcBaseEntity* layerset = relating_material;
			if (relating_material->declaration().is("IfcMaterialLayerSetUsage")) {
				auto fls = relating_material->get("ForLayerSet");
				if (fls.isNull()) {
					return nullptr;
				}
				layerset = ((IfcUtil::IfcBaseClass*) fls)->as<IfcUtil::IfcBaseEntity>();
			}
			aggregate_of_instance::ptr layers = layerset->get("MaterialLayers");
			if (layers && layers->size() >= 1) {
				auto layer = (IfcUtil::IfcBaseEntity*) (*layers->begin());
				auto mat = layer->get("Material");
				if (!mat.isNull()) {
					return ((IfcUtil::IfcBaseClass*) mat)->as<IfcUtil::IfcBaseEntity>();
				}
			}
		}

		return nullptr;
	}

	// Resolves a per-layer material lookup table for `product` (issue #3742, v2) -- lets
	// find_cross_coplanar_matches() classify a candidate face into its own layer instead of
	// relying on get_single_material_association()'s single, whole-product approximation.
	// Schema-agnostic like the helpers above; deliberately does NOT split any geometry (see
	// the plan discussion this was designed against: AbstractKernel::apply_layerset() isn't
	// implemented for the OCCT kernel) -- this is a pure geometric lookup using data that's
	// already fully resolved by the time this runs: IfcMaterialLayerSetUsage's own
	// LayerSetDirection/MaterialLayers attributes, and `compound_local`'s own measured extent
	// along that axis (calibrating the raw, unscaled IFC LayerThickness values against real
	// geometry sidesteps needing this schema-agnostic file to know the project's length unit
	// scale at all -- robust regardless of what units the source file uses, and regardless of
	// any scale baked into `trsf`, since bounding-box extent is measured before `trsf` is
	// applied and rigid transforms preserve length).
	//
	// nullptr/boost::none for anything that isn't an IfcMaterialLayerSetUsage with 2+ layers
	// (a single layer, or no material at all, is already unambiguous -- get_single_material_
	// association() alone is correct for those) or where LayerSetDirection is missing, or
	// where the shape's measured extent along that axis is degenerate.
	boost::optional<layer_projection> resolve_layer_projection(IfcUtil::IfcBaseEntity* product, const TopoDS_Shape& compound_local, const gp_Trsf& trsf) {
		auto rels = product->get_inverse("HasAssociations");
		IfcUtil::IfcBaseEntity* relating_material = nullptr;
		size_t n_material_rels = 0;
		for (auto& ref : *rels) {
			if (ref->declaration().is("IfcRelAssociatesMaterial")) {
				n_material_rels++;
				auto arg = ((IfcUtil::IfcBaseEntity*) ref)->get("RelatingMaterial");
				if (!arg.isNull()) {
					relating_material = ((IfcUtil::IfcBaseClass*) arg)->as<IfcUtil::IfcBaseEntity>();
				}
			}
		}
		if (n_material_rels != 1 || !relating_material || !relating_material->declaration().is("IfcMaterialLayerSetUsage")) {
			return boost::none;
		}

		auto dir_arg = relating_material->get("LayerSetDirection");
		if (dir_arg.isNull()) {
			return boost::none;
		}
		std::string direction_str = (std::string) dir_arg;
		int axis_index = direction_str == "AXIS1" ? 0 : direction_str == "AXIS2" ? 1 : direction_str == "AXIS3" ? 2 : -1;
		if (axis_index < 0) {
			return boost::none;
		}

		auto fls = relating_material->get("ForLayerSet");
		if (fls.isNull()) {
			return boost::none;
		}
		auto layerset = ((IfcUtil::IfcBaseClass*) fls)->as<IfcUtil::IfcBaseEntity>();
		aggregate_of_instance::ptr layers = layerset->get("MaterialLayers");
		if (!layers || layers->size() < 2) {
			return boost::none;
		}

		std::vector<double> raw_thickness;
		std::vector<const IfcUtil::IfcBaseInterface*> materials;
		for (auto& layer_ : *layers) {
			auto layer = (IfcUtil::IfcBaseEntity*) layer_;
			auto th_arg = layer->get("LayerThickness");
			if (th_arg.isNull()) {
				return boost::none;
			}
			raw_thickness.push_back((double) th_arg);
			auto mat_arg = layer->get("Material");
			materials.push_back(mat_arg.isNull() ? nullptr : ((IfcUtil::IfcBaseClass*) mat_arg)->as<IfcUtil::IfcBaseEntity>());
		}
		double raw_total = std::accumulate(raw_thickness.begin(), raw_thickness.end(), 0.0);
		if (raw_total < 1.e-9) {
			return boost::none;
		}

		gp_Dir local_axis = axis_index == 0 ? gp_Dir(1, 0, 0) : axis_index == 1 ? gp_Dir(0, 1, 0) : gp_Dir(0, 0, 1);

		Bnd_Box local_bbox;
		BRepBndLib::Add(compound_local, local_bbox);
		if (local_bbox.IsVoid()) {
			return boost::none;
		}
		double xmin, ymin, zmin, xmax, ymax, zmax;
		local_bbox.Get(xmin, ymin, zmin, xmax, ymax, zmax);
		double local_min = axis_index == 0 ? xmin : axis_index == 1 ? ymin : zmin;
		double local_max = axis_index == 0 ? xmax : axis_index == 1 ? ymax : zmax;
		double measured_span = local_max - local_min;
		if (measured_span < 1.e-9) {
			return boost::none;
		}

		layer_projection proj;
		gp_Pnt local_origin(
			axis_index == 0 ? local_min : 0.0,
			axis_index == 1 ? local_min : 0.0,
			axis_index == 2 ? local_min : 0.0);
		proj.origin = local_origin.Transformed(trsf);
		proj.axis = local_axis.Transformed(trsf);

		double scale = measured_span / raw_total;
		double acc = 0.0;
		proj.cumulative_offsets.push_back(0.0);
		for (double t : raw_thickness) {
			acc += t * scale;
			proj.cumulative_offsets.push_back(acc);
		}
		proj.materials = materials;
		return proj;
	}
}

void SvgSerializer::write(const IfcGeom::BRepElement* brep_obj) {

	boost::optional<std::string> object_type;
	if (!brep_obj->product()->get("ObjectType").isNull()) {
		object_type = static_cast<std::string>(brep_obj->product()->get("ObjectType"));
	}

	std::vector<boost::optional<std::vector<double>>> dash_arrays;

	auto itm = brep_obj->geometry().as_compound();
	TopoDS_Shape compound_local = ((ifcopenshell::geometry::OpenCascadeShape*)itm)->shape();
	delete itm;

	// Cross-object "cross-coplanar" edge classification (issue #3742): a single representative
	// style/material identity for the whole product -- see geometry_data::
	// cross_coplanar_style_instance for why this is per-product rather than per-face/per-item.
	// Whichever item resolves a style first wins; good enough for the common case, and cheap
	// to skip entirely when the feature is off.
	const IfcUtil::IfcBaseInterface* cross_coplanar_style_instance = nullptr;
	// Material takes priority over style in the cross-object comparison -- see
	// geometry_data::cross_coplanar_material_instance -- so resolve it once per product here
	// too, only when the feature is on. Material is a product-level association (not per-item
	// like style), so a single lookup suffices, no loop needed.
	const IfcUtil::IfcBaseInterface* cross_coplanar_material_instance = nullptr;
	if (svg_use_cross_coplanar_classification_) {
		for (auto& x : brep_obj->geometry()) {
			if (x.hasStyle() && x.Style().instance) {
				cross_coplanar_style_instance = x.Style().instance;
				break;
			}
		}
		if (file) {
			cross_coplanar_material_instance = get_single_material_association(
				(IfcUtil::IfcBaseEntity*) brep_obj->product());
		}
	}

	for (auto& x : brep_obj->geometry()) {
		dash_arrays.emplace_back();

		boost::optional<std::string> curve_style_name;
		if (file) {
			auto item = (IfcUtil::IfcBaseEntity*) this->file->instance_by_id(x.ItemId());
			curve_style_name = get_curve_style_name(item);
		}		
		
		if (curve_style_name && 
			(boost::starts_with(*curve_style_name, "LINE_") ||
			 boost::starts_with(*curve_style_name, "DASH_")))
		{
			std::vector<std::string> tokens;
			boost::split(tokens, *curve_style_name, boost::is_any_of("_"));
			if (tokens.size() > 1) {
				dash_arrays.back().emplace();
				for (auto& tok : tokens) {
					double d;
					try {
						d = boost::lexical_cast<double>(tok);
					} catch (boost::bad_lexical_cast&) {
						continue;
					}
					dash_arrays.back()->push_back(d / 1000.);
				}
			}
		}
	}

	gp_Trsf trsf;
	// @todo
	const auto& m = brep_obj->transformation().data()->ccomponents();
	trsf.SetValues(
		m(0, 0), m(0, 1), m(0, 2), m(0, 3),
		m(1, 0), m(1, 1), m(1, 2), m(1, 3),
		m(2, 0), m(2, 1), m(2, 2), m(2, 3)
	);

	// v2: needs both compound_local (still untransformed here -- resolve_layer_projection()
	// measures its own bbox in local frame, since a rigid trsf preserves the resulting
	// lengths regardless) and trsf (to place the resolved axis/origin into the same frame
	// compound_local ends up in once transformed) -- see geometry_data::
	// cross_coplanar_layer_projection.
	boost::optional<layer_projection> cross_coplanar_layer_projection;
	if ((svg_use_cross_coplanar_classification_ || svg_use_mat_style_change_classification_) && file) {
		cross_coplanar_layer_projection = resolve_layer_projection(
			(IfcUtil::IfcBaseEntity*) brep_obj->product(), compound_local, trsf);
	}

	const bool is_section = (section_ref_ && object_type && *section_ref_ == *object_type);
	bool is_elevation = false;
	if (elevation_ref_ && object_type) {
		is_elevation = *elevation_ref_ == *object_type;
	} else if (elevation_ref_guid_) {
		is_elevation = *elevation_ref_guid_ == brep_obj->guid();
	}

	BRepBuilderAPI_Transform make_transform_global(compound_local, trsf, true);
	make_transform_global.Build();
	// (When determinant < 0, copy is implied and the input is not mutated.)
	auto compound_unmirrored = make_transform_global.Shape();

	if (is_section || is_elevation) {
		boost::optional<double> scale;
		boost::optional<std::pair<double, double>> size;

		auto e = edge_from_compound(compound_unmirrored);
		boost::optional<gp_Pln> pln;
		if (e) {
			TopoDS_Edge global_edge = TopoDS::Edge(e->Moved(trsf));
			double u0, u1;
			auto crv = BRep_Tool::Curve(global_edge, u0, u1);
			if (crv->DynamicType() == STANDARD_TYPE(Geom_Line)) {
				gp_Pnt P;
				gp_Vec V;
				crv->D1((u0 + u1) / 2., P, V);
				auto N = V.Crossed(gp::DZ());
				pln = gp_Pln(gp_Ax3(P, N, V));
			}
		}
		else if (boost::optional<box_t> b = box_from_compound(compound_local)) {
			pln = gp_Pln().Transformed(trsf);
			size = std::make_pair(
				b->second[0] - b->first[0],
				b->second[1] - b->first[1]
			);

#if OCC_VERSION_HEX >= 0x70300
			view_box_3d_.emplace();
			BRepBndLib::AddOBB(compound_unmirrored, *view_box_3d_, false, false, false);
#endif
		} else {
			logger_.Error("SER", 23, "Failed to box or edge from drawing annotation");
		}

		std::vector<string_property> props;
		enumerate_string_properties(brep_obj->product(), std::back_inserter(props));
		std::map<std::string, std::string> prop_map;
		for (auto& p : props) {
			prop_map[p.pset_name + "." + p.prop_name] = p.value;
		}
		auto pit = prop_map.find("EPset_Drawing.Scale");
		if (pit != prop_map.end()) {
			typedef boost::tokenizer<boost::char_separator<char>> tokenizer;
			tokenizer tok{ pit->second };
			auto tokit = tok.begin();
			std::string num, denum;
			if (tokit != tok.end()) {
				num = *tokit++;
			}
			tokit++;
			if (tokit != tok.end()) {
				denum = *tokit++;
			}
			if (num.size() && denum.size()) {
				try {
					scale = (float) boost::lexical_cast<int>(num) / boost::lexical_cast<int>(denum);
				}
				catch (boost::bad_lexical_cast&) {}
			}
		}

		if (!emit_building_storeys_ && scale && size) {
			scale_ = scale;
			size_ = std::make_pair(
				// The header writes values in mm
				size->first * 1000 * *scale_,
				size->second * 1000 * *scale_
			);
		}

		if (pln) {
			// Move pln to have projection of origin at plane center.
			// This is necessary to have Poly and BRep HLR at the same position
			// (Poly) is wrong otherwise.
			double pu, pv;
			Extrema_ExtPElS ext;
			ext.Perform(gp::Origin(), *pln, 1.e-5);
			auto P0 = pln->Location();
			pln->SetLocation(ext.Point(1).Value());
			ext.Point(1).Parameter(pu, pv);

			if (!emit_building_storeys_ && scale && size) {
				offset_2d_ = std::make_pair(
					((-size->first / 2.) - pu) * 1000 * *scale_,
					((-size->second / 2.) + pv) * 1000 * *scale_
				);
			}

			if (!deferred_section_data_) {
				deferred_section_data_.emplace();
			}
			std::string name = brep_obj->name();
			if (name.empty()) {
				name = boost::lexical_cast<std::string>(brep_obj->id());
			}
			if (is_section) {
				deferred_section_data_->push_back(vertical_section{ *pln , "Section " + name, false, scale, size });
			}
			if (is_elevation) {
				deferred_section_data_->push_back(vertical_section{ *pln , "Elevation " + name, true, scale, size });
			}
		}

		return;
	}

	auto p = storey_elevation_from_element(brep_obj);
	const IfcUtil::IfcBaseEntity* storey = p ? p->first : nullptr;
	double elev = p ? p->second : std::numeric_limits<double>::quiet_NaN();
	// @todo is it correct to call nameElement() here with a single storey (what if this element spans multiple?)

	if (unify_inputs_) {
		compound_local = IfcGeom::util::heal_for_linework(compound_local, svg_cross_coplanar_tolerance_);
	}

	{
		bool any_wires_converted_to_face = false;
		BRep_Builder BB;
		TopoDS_Compound comp2;
		BB.MakeCompound(comp2);
		TopoDS_Iterator it(compound_local);
		for (; it.More(); it.Next()) {
			auto& s = it.Value();
			if (s.ShapeType() == TopAbs_WIRE && s.Closed()) {
				IfcGeom::util::wire_tolerance_settings wts{ false, false, Precision::Confusion(), Precision::Confusion() };
				TopoDS_Compound faces;
				IfcGeom::util::convert_wire_to_faces(TopoDS::Wire(s), faces, wts);
				BB.Add(comp2, faces);
				any_wires_converted_to_face = true;
			} else {
				BB.Add(comp2, s);
			}
		}
		compound_local = comp2;
	}

	if (only_valid_ && !IfcGeom::util::validate_shape(compound_local)) {
		return;
	}

	geometry_data data{ compound_local, dash_arrays, trsf, brep_obj->product(), storey, elev, brep_obj->name(), nameElement(storey, brep_obj), cross_coplanar_style_instance, cross_coplanar_material_instance, cross_coplanar_layer_projection };

	if (auto_section_ || auto_elevation_ || section_ref_ || elevation_ref_ || elevation_ref_guid_ || deferred_section_data_) {
		element_buffer_.push_back(data);
	}

	// Augment bnd_ regardless of whether emitting storeys as we depend
	// on the global bounds also for the storey height annotations.
	BRepBndLib::Add(compound_unmirrored, bnd_);

	if (emit_building_storeys_) {
		write(data);
	}
}

namespace {
	int infront_or_behind(const gp_Pln& pln, const gp_Pnt& p) {
		auto d = (p.XYZ() - pln.Location().XYZ()).Dot(pln.Axis().Direction().XYZ());
		int state;
		if (std::abs(d) < 1.e-5) {
			state = 0;
		} else {
			state = d < 0. ? -1 : 1;
		}
		return state;
	}
}

namespace {
	// SVG edge classification (issue #3668). See edge-classification.md at the repo root for
	// the authoritative definition of the five classes and their evaluation order.
	//
	// cross_coplanar (issue #3742) is a 6th, separately-gated class layered on top of the
	// original five: it is never assigned by classify_edge_from_faces() itself (which only
	// ever looks at a single product's own topology), but is instead applied afterward, in
	// prefiltered_hlr::build(), to edges that classify_edge_from_faces() already resolved to
	// one of the original five, whenever that edge's entire length also happens to lie on a
	// coincident, same-style/material face of a *different* product.
	enum class edge_style_class { boundary, outline, sharp, crease, flush, cross_coplanar };

	const char* edge_style_class_name(edge_style_class c) {
		switch (c) {
		case edge_style_class::boundary:       return "boundary";
		case edge_style_class::outline:        return "outline";
		case edge_style_class::sharp:          return "sharp";
		case edge_style_class::crease:         return "crease";
		case edge_style_class::cross_coplanar: return "cross-coplanar";
		default:                               return "flush";
		}
	}

	// Outward face normal, accounting for face orientation. Only planar faces are supported;
	// returns false otherwise (caller should conservatively treat the edge as an outline).
	bool face_normal_from_planar_face(const TopoDS_Face& f, gp_Dir& out) {
		auto s = BRep_Tool::Surface(f);
		if (s->DynamicType() != STANDARD_TYPE(Geom_Plane)) {
			return false;
		}
		auto p = Handle(Geom_Plane)::DownCast(s);
		gp_Dir d = p->Axis().Direction();
		if (f.Orientation() == TopAbs_REVERSED) {
			d.Reverse();
		}
		out = d;
		return true;
	}

	double clamp_dot(double v) {
		if (v < -1.0) return -1.0;
		if (v > 1.0) return 1.0;
		return v;
	}

	// True if the wire-order triple (v0 -> v1 -> v2) turns right (concave/reflex) at v1, judged
	// via an in-plane cross-product turn test against the face's own outward normal `n`. For a
	// simple polygon walked in the winding order BRepTools_WireExplorer gives over a face's own
	// (orientation-composed) outer wire, consecutive edge vectors turn left (positive
	// cross(a,b).Dot(n)) at every convex corner and right (negative) at every reflex corner --
	// the same "outward normal + consistent winding" convention face_normal_from_planar_face()
	// already relies on elsewhere in this function, just applied in-plane instead of
	// face-to-face. Deliberately biased towards "not reflex" (trust the candidate) on a
	// degenerate/near-collinear triple, minimizing regression risk on ambiguous input.
	bool is_reflex_vertex(const gp_Pnt& v0, const gp_Pnt& v1, const gp_Pnt& v2, const gp_Dir& n) {
		const gp_Vec a(v0, v1), b(v1, v2);
		const double la = a.Magnitude(), lb = b.Magnitude();
		if (la < Precision::Confusion() || lb < Precision::Confusion()) {
			return false;
		}
		constexpr double kSinEps = 1.e-6;
		return a.Crossed(b).Dot(gp_Vec(n.XYZ())) < -kSinEps * la * lb;
	}

	// Locates `target_edge` within a properly wire-ordered traversal of face `f`'s boundary --
	// tries BRepTools::OuterWire(f) first (the common case), then falls back to every other wire
	// of f via TopExp_Explorer(f, TopAbs_WIRE) in case the shared edge sits on an inner/hole
	// boundary. Matches by edge identity (IsSame), not vertex geometry/identity, specifically to
	// sidestep duplicate-vertex ambiguity -- the shared edge between f0 and f1 is the same
	// TopoDS_Edge instance in both, since both come from the same edge-face map built off one
	// compound.
	//
	// For each of the caller-supplied endpoints (ev0, ev1) of target_edge, reports the
	// wire-neighbor vertex reached via the *other* wire-edge incident to that endpoint (i.e.
	// continuing along the wire, not back across target_edge), and whether that endpoint is
	// itself a reflex corner of the wire it was found on. Output order mirrors (ev0, ev1) as
	// passed in, regardless of the wire's own internal start/end order for target_edge.
	//
	// Returns false if target_edge could not be located on any wire of f (shouldn't happen for a
	// legitimately shared 2-manifold edge; caller must treat this as "fall back to whole-face
	// scan").
	// `matched_wire_is_outer` reports whether `target_edge` was found on `f`'s *outer* boundary
	// wire, as opposed to one of its inner (hole/void) boundary wires. This matters to the
	// caller: walking further around a face's own wire to find a "trustworthy" neighbor point
	// only reflects genuine material extent when that wire is the face's outer boundary. On an
	// inner (hole) wire, the next vertex around the SAME rim lies on the *far side of the empty
	// hole*, not on material -- confirmed on a real-world project file, a window frame member
	// extruded from an `IfcArbitraryProfileDefWithVoids` profile (a genuine through-hole, not a
	// notch) had its hole-rim edges consistently misclassified `crease` instead of `sharp`,
	// traced to exactly this: the position-based sign test's "trustworthy candidate" always came
	// from the flat cap face's own hole-rim wire (the only wire containing that edge on that
	// face), whose next vertex sits across the hole, giving a dot product that is *always*
	// positive (same side as the wall's into-the-hole normal) regardless of the true 3D fold
	// direction -- a structural artifact of the hole, not noise, so no amount of "prefer larger
	// |dot|" tie-breaking can fix it. The other face meeting at that edge (the hole's own inner
	// wall) has no hole of its own; its neighbor vertex correctly extends into the wall's own
	// depth and gives the right answer. See the caller for how this flag is used to prefer that.
	bool wire_neighbors_of_edge(
		const TopoDS_Face& f, const TopoDS_Edge& target_edge,
		const TopoDS_Vertex& ev0, const TopoDS_Vertex& ev1, const gp_Dir& f_normal,
		TopoDS_Vertex& neighbor_of_ev0, bool& ev0_is_reflex,
		TopoDS_Vertex& neighbor_of_ev1, bool& ev1_is_reflex,
		bool& matched_wire_is_outer)
	{
		std::vector<TopoDS_Wire> wires;
		std::vector<bool> wire_is_outer;
		TopoDS_Wire outer = BRepTools::OuterWire(f);
		if (!outer.IsNull()) {
			wires.push_back(outer);
			wire_is_outer.push_back(true);
		}
		for (TopExp_Explorer wexp(f, TopAbs_WIRE); wexp.More(); wexp.Next()) {
			TopoDS_Wire w = TopoDS::Wire(wexp.Current());
			if (outer.IsNull() || !w.IsSame(outer)) {
				wires.push_back(w);
				wire_is_outer.push_back(false);
			}
		}

		for (size_t wire_idx = 0; wire_idx < wires.size(); ++wire_idx) {
			const TopoDS_Wire& w = wires[wire_idx];
			std::vector<TopoDS_Vertex> verts;
			std::vector<TopoDS_Edge> edges;
			for (BRepTools_WireExplorer exp(w, f); exp.More(); exp.Next()) {
				verts.push_back(exp.CurrentVertex());
				edges.push_back(TopoDS::Edge(exp.Current()));
			}
			const int n = (int)edges.size();
			if (n < 3) {
				continue;
			}

			int i = -1;
			for (int k = 0; k < n; ++k) {
				if (edges[k].IsSame(target_edge)) {
					i = k;
					break;
				}
			}
			if (i < 0) {
				continue;
			}

			// `is_reflex_vertex()` assumes the wire's vertex sequence runs counter-clockwise as
			// seen from the +f_normal side (the standard "convex corners turn towards the normal"
			// convention). That assumption doesn't universally hold: confirmed on a real-world
			// project file, a side/reveal face of a thin extruded frame member had its whole
			// 4-vertex wire wound the *opposite* way relative to its own outward face normal (as
			// returned by face_normal_from_planar_face()) -- every one of its 4 corners, on a
			// simple planar quad where none can genuinely be reflex, tested as reflex. Rather than
			// track down which OCCT face-construction path produces this (side faces of prisms
			// built from a swept profile boundary can end up with either winding relative to their
			// topological Orientation flag), self-correct here: sum the signed turning across the
			// *entire* wire once, and if the aggregate is negative (wire runs clockwise as seen
			// from f_normal), use the reversed normal for every reflex test on this wire instead.
			// This makes the reflex test internally consistent regardless of whichever winding
			// convention this particular face's boundary happens to have -- a real, convex quad
			// then correctly reports zero reflex vertices no matter which way its wire winds.
			double winding = 0.0;
			for (int k = 0; k < n; ++k) {
				const gp_Pnt pprev = BRep_Tool::Pnt(verts[(k - 1 + n) % n]);
				const gp_Pnt pcur = BRep_Tool::Pnt(verts[k]);
				const gp_Pnt pnext = BRep_Tool::Pnt(verts[(k + 1) % n]);
				winding += gp_Vec(pprev, pcur).Crossed(gp_Vec(pcur, pnext)).Dot(gp_Vec(f_normal.XYZ()));
			}
			const gp_Dir effective_normal = (winding < 0.0) ? f_normal.Reversed() : f_normal;

			const TopoDS_Vertex& a = verts[i];
			const TopoDS_Vertex& b = verts[(i + 1) % n];
			const TopoDS_Vertex& prev = verts[(i - 1 + n) % n];
			const TopoDS_Vertex& next2 = verts[(i + 2) % n];

			const bool a_reflex = is_reflex_vertex(
				BRep_Tool::Pnt(prev), BRep_Tool::Pnt(a), BRep_Tool::Pnt(b), effective_normal);
			const bool b_reflex = is_reflex_vertex(
				BRep_Tool::Pnt(a), BRep_Tool::Pnt(b), BRep_Tool::Pnt(next2), effective_normal);

			matched_wire_is_outer = wire_is_outer[wire_idx];

			if (a.IsSame(ev0)) {
				neighbor_of_ev0 = prev;  ev0_is_reflex = a_reflex;
				neighbor_of_ev1 = next2; ev1_is_reflex = b_reflex;
			} else {
				neighbor_of_ev0 = next2; ev0_is_reflex = b_reflex;
				neighbor_of_ev1 = prev;  ev1_is_reflex = a_reflex;
			}
			return true;
		}
		return false;
	}

	edge_style_class classify_edge_from_faces(
		const TopoDS_Edge& edge,
		const NCollection_List<TopoDS_Shape>& faces,
		const gp_Dir& projection_direction,
		double ridge_angle_min_deg,
		double valley_angle_min_deg,
		bool product_has_naked_edge
	) {
		std::vector<TopoDS_Face> faces_vec;
		for (NCollection_List<TopoDS_Shape>::Iterator it(faces); it.More(); it.Next()) {
			const TopoDS_Shape& s = it.Value();
			if (s.ShapeType() == TopAbs_FACE) {
				faces_vec.push_back(TopoDS::Face(s));
			}
		}

		// Boundary: naked edge, or non-manifold (3+ faces) -- the latter is explicitly out of
		// scope for the 5-class scheme (a geometry-health/QA concern), so fall back to the
		// same conservative bucket rather than force-fitting it into outline/sharp/crease.
		if (faces_vec.size() != 2) {
			return edge_style_class::boundary;
		}

		const TopoDS_Face& f0 = faces_vec[0];
		const TopoDS_Face& f1 = faces_vec[1];

		gp_Dir n0, n1;
		if (!face_normal_from_planar_face(f0, n0) || !face_normal_from_planar_face(f1, n1)) {
			// Conservative fallback for non-planar-face edges.
			return edge_style_class::outline;
		}

		// Note the negation: `projection_direction` (as constructed by the caller from the
		// drawing plane's axis) points from the scene *towards the camera*, not into the scene.
		// A face that's actually front-facing (visible, facing the viewer) has an outward normal
		// pointing the same general way as that -- i.e. a *positive* dot product -- so negate
		// here to get the more intuitive "front-facing is negative" convention used below.
		// Confirmed against this feature's own real-world test scene: the SOUTH ELEVATION
		// camera's placement matrix transforms local +Z (what the un-negated projection_direction
		// is built from) to world (0, 1, 0), while the camera's actual Blender-convention view
		// direction (local -Z) transforms to world (0, -1, 0) -- i.e. exactly opposite.
		const double d0 = -projection_direction.Dot(n0);
		const double d1 = -projection_direction.Dot(n1);

		// Front/back/edge-on classification of each face relative to the view direction, using
		// a tolerance band around zero rather than a bare sign comparison. A face at or near
		// edge-on to the camera (|d| within the band) is common for regular/symmetric
		// tessellations viewed from "nice" angles (icospheres, N-gon cylinder/cone
		// approximations) and must count as outline on both its edges, not just the one that
		// happens to pair it with a clearly front-facing neighbour.
		constexpr double kOutlineDotEps = 1.e-4;
		const bool front0 = d0 < -kOutlineDotEps;
		const bool back0 = d0 > kOutlineDotEps;
		const bool front1 = d1 < -kOutlineDotEps;
		const bool back1 = d1 > kOutlineDotEps;

		// Outline: silhouette, either a genuine front/back flip, or either face is at/near
		// edge-on to the view direction (also covers both faces edge-on at once).
		if (!(front0 && front1) && !(back0 && back1)) {
			return edge_style_class::outline;
		}

		// Signed deviation from flat (0 degrees between outward normals = perfectly flat, i.e.
		// coplanar faces have identical outward normals). Positive = convex (ridge/sharp),
		// negative = concave (valley/crease).
		//
		// Sign via a position-based (not orientation-based) test: find a vertex of f1 that
		// isn't one of the shared edge's own endpoints, and check which side of f0's plane it
		// falls on. If it's behind f0's plane (opposite side from f0's outward normal), f1
		// curves back towards the solid's interior relative to f0 -- a convex fold, like a box
		// corner. This avoids relying on TopoDS_Edge/wire orientation semantics (which proved
		// unreliable in practice: an earlier attempt using edge.Orientation() combined with
		// cross(n0, n1) gave a self-consistent-looking but wrong sign on real BRep topology --
		// verified against known-convex geometry, e.g. every edge of a convex icosphere, where
		// that approach misclassified a majority of edges as concave).
		double deviation_deg = std::acos(clamp_dot(n0.Dot(n1))) * 180.0 / M_PI;

		TopoDS_Vertex ev0, ev1;
		TopExp::Vertices(edge, ev0, ev1);
		const gp_Pnt edge_p0 = BRep_Tool::Pnt(ev0);
		const gp_Pnt edge_p1 = BRep_Tool::Pnt(ev1);

		// Trustworthy-candidate selection (issue #3742 follow-up): only consider the
		// wire-neighbor vertex reached from each of the target edge's own endpoints, and only
		// when that endpoint is NOT itself a reflex corner of the face's boundary. Scanning every
		// vertex of a face and keeping the largest |dot| (the previous behaviour) is only valid
		// when that face is convex -- every vertex of a convex polygon lies on the same side of
		// any line through one of its edges, so the sign is invariant to which vertex is picked,
		// and "largest magnitude" is just a noise-robustness tiebreak. When the face is non-convex
		// (e.g. an L-shaped face, or a face with a notch cut into it by a boolean void), vertices
		// reachable only by crossing through a reflex corner -- or lying on a distant, unrelated
		// part of the polygon -- give an INVERTED sign. Confirmed against real geometry (an
		// L-shaped roof slab's bottom face, and a wall's notch cut by an IfcOpeningElement): in
		// both cases the wrong-sign vertex also had the larger |dot|, so the old "most decisive"
		// heuristic reliably picked the wrong answer, misclassifying genuinely convex/sharp edges
		// as concave/crease.
		//
		// Pooled from BOTH faces, not just f1 (issue #3742, hole/void follow-up): a candidate
		// from f1's wire, tested against n0, and a candidate from f0's wire, tested against n1,
		// are symmetric -- "does a genuine extension point of either face lie behind the OTHER
		// face's plane" is the same convex test either way round. This matters because f0/f1 is
		// an arbitrary ordering (whichever face came first out of an unordered edge-face map),
		// and which face's wire is usable is NOT arbitrary: confirmed on a real-world project
		// file, a window frame member extruded from a profile with a genuine hole (through-hole,
		// not a notch) has its hole-rim edges shared between the hole's inner wall (a plain quad,
		// only an outer wire) and the flat cap face (an annulus, with an INNER wire running around
		// the hole). Whichever face happened to land in the "f1" slot, if it was the cap, its own
		// hole-rim wire's next vertex sits on the *far side of the hole* -- not on material at
		// all -- giving a dot product that is always positive (wrong) regardless of the true fold,
		// no matter how large its magnitude. The wall's own wire has no such issue (it has no
		// voids of its own), so pooling both and strongly preferring whichever candidate came from
		// an OUTER wire (see wire_neighbors_of_edge()'s own comment) reliably picks the wall's
		// correct signal over the cap's structurally-misleading one, regardless of f0/f1 order.
		struct SignCandidate { double dot; bool is_outer; };
		std::vector<SignCandidate> candidates;

		auto collect_candidates = [&](const TopoDS_Face& face_for_wire, const gp_Dir& wire_normal,
		                               const gp_Dir& test_against_normal) {
			TopoDS_Vertex nb0, nb1;
			bool ev0_reflex = false, ev1_reflex = false;
			bool wire_is_outer = false;
			if (!wire_neighbors_of_edge(face_for_wire, edge, ev0, ev1, wire_normal, nb0, ev0_reflex, nb1, ev1_reflex, wire_is_outer)) {
				return;
			}
			for (const auto& nb_pair : { std::make_pair(nb0, ev0_reflex), std::make_pair(nb1, ev1_reflex) }) {
				if (nb_pair.second) {
					continue;
				}
				const gp_Pnt p = BRep_Tool::Pnt(nb_pair.first);
				if (p.Distance(edge_p0) > Precision::Confusion() && p.Distance(edge_p1) > Precision::Confusion()) {
					candidates.push_back({ gp_Vec(edge_p0, p).Dot(gp_Vec(test_against_normal.XYZ())), wire_is_outer });
				}
			}
		};
		collect_candidates(f1, n1, n0);
		collect_candidates(f0, n0, n1);

		double decisive_dot = 0.0;
		bool have_decisive_vertex = false;
		bool have_outer_decisive = false;

		// Prefer candidates from an outer wire outright; only fall back to inner-wire candidates
		// (still useful for genuine notches, just not for holes) if no outer-wire one exists.
		for (const SignCandidate& c : candidates) {
			if (c.is_outer) {
				if (!have_outer_decisive || std::abs(c.dot) > std::abs(decisive_dot)) {
					decisive_dot = c.dot;
					have_outer_decisive = true;
					have_decisive_vertex = true;
				}
			}
		}
		if (!have_outer_decisive) {
			for (const SignCandidate& c : candidates) {
				if (!have_decisive_vertex || std::abs(c.dot) > std::abs(decisive_dot)) {
					decisive_dot = c.dot;
					have_decisive_vertex = true;
				}
			}
		}

		if (!have_decisive_vertex) {
			// Conservative fallback: both endpoints reflex on both faces, or the edge couldn't be
			// located on any wire of either face (degenerate/non-manifold-looking topology) --
			// fall back to the original whole-face scan (both faces, not just f1) rather than
			// giving up outright.
			for (const auto& face_normal_pair : { std::make_pair(&f1, &n0), std::make_pair(&f0, &n1) }) {
				for (TopExp_Explorer vexp(*face_normal_pair.first, TopAbs_VERTEX); vexp.More(); vexp.Next()) {
					const gp_Pnt p = BRep_Tool::Pnt(TopoDS::Vertex(vexp.Current()));
					if (p.Distance(edge_p0) > Precision::Confusion() && p.Distance(edge_p1) > Precision::Confusion()) {
						double dot = gp_Vec(edge_p0, p).Dot(gp_Vec(face_normal_pair.second->XYZ()));
						if (!have_decisive_vertex || std::abs(dot) > std::abs(decisive_dot)) {
							decisive_dot = dot;
							have_decisive_vertex = true;
						}
					}
				}
			}
		}

		if (have_decisive_vertex) {
			const bool convex = decisive_dot < 0.0;
			if (!convex) {
				deviation_deg = -deviation_deg;
			}
		}

		// View-relative flip for folds seen from behind through an opening (e.g. the "Rotated
		// Box w/Boundary" test object -- a box with one face removed; the 3 interior lines
		// visible through the opening read as the *inside* of an ordinary convex box corner,
		// which should look like a crease, not a sharp ridge). Two earlier unconditional
		// versions of this flip (triggered on plain back0&&back1, with no further gate) were
		// tried and reverted -- see edge-classification.md follow-up notes -- because they
		// corrupted otherwise-correct classification broadly, manifesting as spurious `crease`
		// edges on a fully-convex icosphere test case that has no opening at all.
		//
		// That corruption wasn't a fundamental inability to distinguish "genuinely seen through
		// a hole" from "ordinary far side of closed geometry": bucket membership here is purely
		// a post-hoc query key into an already-completed, correct HLR visibility computation,
		// so reclassifying an edge can never make a genuinely hidden edge appear or vice versa.
		// The real cause is a threshold-crossing artifact: near the silhouette, facet-normal
		// noise on regular/symmetric tessellations (icospheres, N-gon cylinder/cone
		// approximations) makes some genuinely near-edge-on facets test as "back" under the
		// flat-normal-based back0/back1 test even though they're still visible. An unconditional
		// negate then took their small, correctly-`flush` solid-relative deviation and re-tested
		// it against the *other* threshold -- `ridge_angle_min_deg` (45 degrees by default) and
		// `valley_angle_min_deg` (12 degrees by default) are deliberately asymmetric, so a gentle
		// ~20 degree convex facet transition that safely sits under the ridge threshold crosses
		// well over the much smaller valley threshold once flipped, becoming a spurious `crease`.
		//
		// Fix: gate the flip so it can only reinterpret a fold that would already be visible
		// (sharp or crease) under its own pre-flip threshold -- i.e. only folds sharp/deep
		// enough to draw from the front get reinterpreted as the opposite class from behind.
		// Gentle tessellation-noise deviations that are correctly `flush` either way never cross
		// the asymmetric threshold gap, because they never reach the flip at all. Verified
		// against the full test scene: every object's classification is byte-for-byte unchanged
		// except "Rotated Box w/Boundary", whose 3 interior lines now correctly read `crease`
		// (previously all 4 non-boundary edges read `sharp`).
		//
		// Second fix (issue #3742 follow-up): `back0 && back1` alone is true for countless
		// ordinary edges on any closed, watertight solid -- it just means this particular fold
		// happens to face away from the camera, which says nothing about whether there's an
		// actual hole to be "seeing through" at all. Confirmed on a real-world project file: a
		// flush-mounted (no recess) window frame -- a fully closed solid, no missing faces
		// anywhere -- had several genuinely convex, back-facing 90-degree corners wrongly
		// flipped to `crease`. The flip's own motivating case ("a box with one face removed")
		// necessarily has genuine naked/boundary edges somewhere on the product (the rim of the
		// removed face), even though the specific *interior* edges it flips still have exactly 2
		// adjacent faces each. `product_has_naked_edge` (computed once per product, not per
		// edge, from the same edge-face map already built at the call site) is that real,
		// topological signal -- not a heuristic guess -- for "this product actually has an
		// opening somewhere," so only allow the flip when it's true.
		if (back0 && back1 && product_has_naked_edge) {
			const bool would_show_unflipped =
				(deviation_deg >= 0.0) ? (deviation_deg >= ridge_angle_min_deg) : (-deviation_deg >= valley_angle_min_deg);
			if (would_show_unflipped) {
				deviation_deg = -deviation_deg;
			}
		}

		if (deviation_deg >= 0.0) {
			return (deviation_deg >= ridge_angle_min_deg) ? edge_style_class::sharp : edge_style_class::flush;
		} else {
			return (-deviation_deg >= valley_angle_min_deg) ? edge_style_class::crease : edge_style_class::flush;
		}
	}
}

void SvgSerializer::write(const geometry_data& data) {
	std::vector<section_data> section_heights_storage;
	const std::vector<section_data>* section_heights_used = &section_heights_storage;

	if (section_data_) {
		section_heights_used = section_data_.get_ptr();
	} else {
		if (data.storey) {
			section_heights_storage.push_back(horizontal_plan{ data.storey, data.storey_elevation,  +1. });
		} else {
			logger_.Warning("SER", 24, "No global section height and unable to determine building storey for:", data.product);
			return;
		}
	}

	BRepBuilderAPI_Transform make_transform_global(data.compound_local, data.trsf, true);
	make_transform_global.Build();
	// (When determinant < 0, copy is implied and the input is not mutated.)
	auto compound_unmirrored = make_transform_global.Shape();

#if OCC_VERSION_HEX >= 0x70300
	if (view_box_3d_) {
		Bnd_OBB obb;
		BRepBndLib::AddOBB(compound_unmirrored, obb, false, false, false);
		if (view_box_3d_->IsOut(obb)) {
			logger_.Notice("SER", 25, "Not including element due to viewBox", data.product);
			return;
		}
	}
#endif

	// SVG has a coordinate system with the origin in the *upper*-left corner
	// therefore we mirror the shape along the XZ-plane.	
	gp_Trsf trsf_mirror;
	if (!mirror_y_) {
		trsf_mirror.SetMirror(gp_Ax2(gp::Origin(), gp::DY()));
	}
	if (mirror_x_) {
		gp_Trsf mirror_x;
		mirror_x.SetMirror(gp_Ax2(gp::Origin(), gp::DX()));
		trsf_mirror.PreMultiply(mirror_x);
	}
	BRepBuilderAPI_Transform make_transform_mirror(compound_unmirrored, trsf_mirror, true);
	make_transform_mirror.Build();
	// (When determinant < 0, copy is implied and the input is not mutated.)
	auto compound = make_transform_mirror.Shape();

	TopoDS_Wire annotation;

	if (is_floor_plan_ && draw_door_arcs_ && data.product->declaration().is("IfcDoor")) {

		boost::optional<std::string> operation_type;

		try {
			aggregate_of_instance::ptr rels;
			if (data.product->declaration().schema()->name() == "IFC2X3") {
				rels = data.product->get_inverse("IsDefinedBy");
			} else {
				// Damn you, IFC
				rels = data.product->get_inverse("IsTypedBy");
			}
			for (auto& rel : *rels) {
				if (rel->declaration().name() == "IfcRelDefinesByType") {
					IfcUtil::IfcBaseClass* ty = ((IfcUtil::IfcBaseEntity*)rel)->get("RelatingType");
					const std::string& ty_entity_name = ty->declaration().name();
					// Damn you, IFC
					if (ty_entity_name == "IfcDoorStyle" || ty_entity_name == "IfcDoorType") {
						operation_type = (std::string)((IfcUtil::IfcBaseEntity*)ty)->get("OperationType");
					}
				}
			}
		} catch (std::exception& e) {
			logger_.Error("SER", 26, e);
		}

		if (operation_type && ((*operation_type == "SINGLE_SWING_LEFT") || (*operation_type == "SINGLE_SWING_RIGHT"))) {
			const bool is_left = *operation_type == "SINGLE_SWING_LEFT";

			Bnd_Box bb;
			BRepBndLib::Add(data.compound_local, bb);

			if (bb.IsVoid()) {
				return;
			}

			double x1, y1, z1, x2, y2, z2;
			bb.Get(x1, y1, z1, x2, y2, z2);
			double width = x2 - x1;
			double y12 = (y1 + y2) / 2.;

			gp_Pnt center(is_left ? x1 : x2, y12, 0);
			gp_Pnt p1(is_left ? x2 : x1, y12, 0);
			gp_Pnt p2(is_left ? x1 : x2, y12 + width, 0);

			if (!is_left) {
				// circles are counter clockwise, so for swing right
				// we need to reverse the points in order to get the
				// shorter part of the circle arc.
				std::swap(p1, p2);
			}

			BRepBuilderAPI_MakeEdge me(gp_Circ(gp_Ax2(center, gp::DZ()), width), p1, p2);
			if (me.IsDone()) {
				BRep_Builder B;
				B.MakeWire(annotation);
				auto edge = me.Edge();

				make_transform_global.Perform(edge, true);
				auto edge_global = make_transform_global.Shape();
				make_transform_mirror.Perform(edge_global, true);
				auto edge_global_mirrored = make_transform_mirror.Shape();

				center.Transform(data.trsf);
				p1.Transform(data.trsf);
				p2.Transform(data.trsf);
				center.Transform(trsf_mirror);
				p1.Transform(trsf_mirror);
				p2.Transform(trsf_mirror);

				if (!is_left) {
					// For the purpose of the SVG serializer we do not a topologically
					// connected wire. So adding disconnected edges is fine.

					B.Add(annotation, BRepBuilderAPI_MakeEdge(center, p1).Edge());
				}

				B.Add(annotation, edge_global_mirrored);

				if (is_left) {
					B.Add(annotation, BRepBuilderAPI_MakeEdge(p2, center).Edge());
				}
			}
		}		
	}

	bool emitted = false;

	for (auto sit = section_heights_used->begin(); sit != section_heights_used->end(); ++sit) {
		const auto& variant = *sit;

		// Elev + offset
		double cut_z = std::numeric_limits<double>::infinity();
		
		// Elev .. Elev(next)
		std::pair<double, double> range;

		gp_Vec projection_direction;
		gp_Pln projection_plane;

		const IfcUtil::IfcBaseEntity* storey = nullptr;
		std::string drawing_name;

		bool use_hlr = always_project_;

		// @todo use visitor
		// horizontal_plan, horizontal_plan_at_element, vertical_section
		if (variant.which() == 0) {
			const auto& plan = boost::get<horizontal_plan>(variant);
			storey = plan.storey;
			cut_z = plan.elevation + plan.offset;
			range = { plan.elevation, plan.next_elevation };
			if (sit == section_heights_used->begin()) {
				range.first = -std::numeric_limits<double>::infinity();
			}
			projection_direction = gp::DZ();
			projection_plane = gp_Pln(gp_Ax3(gp_Pnt(0, 0, cut_z), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0)));
		} else if (variant.which() == 1) {
			projection_direction = gp::DZ();
			projection_plane = gp_Pln(gp_Ax3(gp_Pnt(0, 0, cut_z), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0)));
		} else if (variant.which() == 2) {
			const auto& section = boost::get<vertical_section>(variant);
			projection_direction = section.plane.Axis().Direction();
			projection_plane = section.plane;
			drawing_name = section.name;
			use_hlr = section.with_projection;
		}

		auto& compound_to_use = is_floor_plan_ ? compound : compound_unmirrored;

		if (use_hlr) { // && (hlr.which())) {

			// Check if any of the bounding box points is on the correct side of the plane
			Bnd_Box bb;
			try {
				BRepBndLib::Add(compound_to_use, bb);
			}
			catch (const Standard_Failure&) {}

			if (bb.IsVoid()) {
				continue;
			}

			double xs[2], ys[2], zs[2];
			bb.Get(xs[0], ys[0], zs[0], xs[1], ys[1], zs[1]);

			bool any_in_front = false, any_behind = false;

			// See if any of the vertices is in the negative Z-axis of the projection plane
			for (int i = 0; i < 8; ++i) {
				gp_Pnt p(xs[(i & 1) == 1], ys[(i & 2) == 2], zs[(i & 4) == 4]);
				int state = infront_or_behind(projection_plane, p);
				if (state == -1) {
					any_in_front = true;
				} else if (state == +1) {
					any_behind = true;
				}
			}

			// Exclude annotations, spaces and grids from HLR
			if (any_in_front && !data.product->declaration().is("IfcAnnotation") && !data.product->declaration().is("IfcSpace") && !data.product->declaration().is("IfcGrid")) {
				TopoDS_Shape* compound_to_hlr = &compound_to_use;
				TopoDS_Shape subtracted_shape;

				bool should_subtract = false;

				if (subtraction_settings_ == ON_SLABS_AT_FLOORPLANS) {
					should_subtract = data.product->declaration().is("IfcSlab") && is_floor_plan_;
				} else if (subtraction_settings_ == ON_SLABS_AND_WALLS) {
					should_subtract = data.product->declaration().is("IfcSlab") || data.product->declaration().is("IfcWall");
				} else if (subtraction_settings_ == ALWAYS) {
					should_subtract = true;
				}

				if (any_in_front && any_behind && should_subtract) {
					// This is currently only for slanted roof slabs on floor plans
					bool should_cut = false;
					TopExp_Explorer exp(compound_to_use, TopAbs_FACE);
					for (; exp.More(); exp.Next()) {
						
						const TopoDS_Face& face = TopoDS::Face(exp.Current());
						BRepGProp_Face prop(face);
						gp_Pnt _;
						gp_Vec normal_direction;
						double u0, u1, v0, v1;
						BRepTools::UVBounds(face, u0, u1, v0, v1);
						prop.Normal((u0 + u1) / 2., (v0 + v1) / 2., _, normal_direction);
						const double dx = std::fabs(normal_direction.X());
						const double dy = std::fabs(normal_direction.Y());
						const double dz = std::fabs(normal_direction.Z());
						auto largest = dx > dy ? dx : dy;
						largest = largest > dz ? largest : dz;

						if (subtraction_settings_ != ON_SLABS_AT_FLOORPLANS || largest < (1. - 1.e-5)) {

							bool any_in_front_face = false, any_behind_face = false;

							TopExp_Explorer exp2(face, TopAbs_VERTEX);
							for (; exp2.More(); exp2.Next()) {
								gp_Pnt p = BRep_Tool::Pnt(TopoDS::Vertex(exp2.Current()));
								int state = infront_or_behind(projection_plane, p);
								if (state == -1) {
									any_in_front_face = true;
								} else if (state == +1) {
									any_behind_face = true;
								}
							}

							should_cut = any_in_front_face && any_behind_face;
							if (should_cut) {
								break;
							}
						}
					}

					if (should_cut) {

						// Sample eight bounding box points, project on plane
						// and take the min and max U, V parameters to form
						// a 2d bounding box in parameter space on the plane.

						// This is used to form a cutting plane (halfspace)
						// to trim away parts behind the projection plane
						// before performing HLR.

						double min_u = +std::numeric_limits<double>::infinity();
						double max_u = -std::numeric_limits<double>::infinity();
						double min_v = +std::numeric_limits<double>::infinity();
						double max_v = -std::numeric_limits<double>::infinity();

						for (int i = 0; i < 8; ++i) {
							gp_Pnt p(xs[(i & 1) == 1], ys[(i & 2) == 2], zs[(i & 4) == 4]);
							Extrema_ExtPElS ext;
							ext.Perform(p, projection_plane, 1.e-5);
							if (ext.NbExt() == 1) {
								double pu, pv;
								ext.Point(1).Parameter(pu, pv);
								if (pu < min_u) {
									min_u = pu;
								}
								if (pu > max_u) {
									max_u = pu;
								}
								if (pv < min_v) {
									min_v = pv;
								}
								if (pv > max_v) {
									max_v = pv;
								}
							}
						}

						try {

							BRepBuilderAPI_MakeFace mf(new Geom_Plane(projection_plane), min_u - 1., max_u + 1., min_v - 1., max_v + 1., Precision::Confusion());
							auto f = mf.Face();
							gp_Pnt ref = projection_plane.Position().Location().XYZ() + projection_plane.Position().Direction().XYZ();
							BRepPrimAPI_MakeHalfSpace mhs(f, ref);
							auto s = mhs.Solid();

							BRep_Builder BB;
							TopoDS_Compound C;
							BB.MakeCompound(C);

							// loop over parts to have better luck with co-planar parts
							TopoDS_Iterator it(compound_to_use);
							for (; it.More(); it.Next()) {
								// A genuinely degenerate/self-intersecting part (confirmed against a
								// real wall with two overlapping IfcOpeningElement voids, issue:
								// PROPOSED SECTION crash) can make BRepAlgoAPI_Cut itself crash
								// outright rather than throw -- BRepCheck_Analyzer/ShapeFix_Shape
								// first gives OCCT a chance to heal it before the cut ever runs.
								TopoDS_Shape part_to_cut = it.Value();
								try {
									if (!BRepCheck_Analyzer(part_to_cut).IsValid()) {
										ShapeFix_Shape fixer(part_to_cut);
										fixer.Perform();
										part_to_cut = fixer.Shape();
									}
								} catch (const Standard_Failure&) {
									// Leave part_to_cut as the original -- BRepAlgoAPI_Cut below
									// still has its own IsDone()/IsNull() guards for whatever
									// this leaves behind.
								}
								BRepAlgoAPI_Cut cut_op(part_to_cut, s);
								if (!cut_op.IsDone()) {
									continue;
								}
								auto part = cut_op.Shape();
								// BRepAlgoAPI_Cut can also report success (IsDone()) yet still hand
								// back a null shape for the same kind of degenerate input --
								// BRep_Builder::Add() below has no defence of its own against that,
								// so check first rather than let it corrupt/crash.
								if (part.IsNull()) {
									continue;
								}
								BB.Add(C, part);
							}

							subtracted_shape = C;
							compound_to_hlr = &subtracted_shape;
						} catch (...) {
							logger_.Error("SER", 27, "Failed to cut element for HLR", data.product);
						}
					}
				}

				TopoDS_Compound profile_edges;
				if (profile_threshold_ != -1 && !(data.product->declaration().is("IfcWall") || data.product->declaration().is("IfcSlab"))) {
                    NCollection_IndexedDataMap<TopoDS_Shape, NCollection_List<TopoDS_Shape>, TopTools_ShapeMapHasher> map;
					TopExp::MapShapesAndAncestors(*compound_to_hlr, TopAbs_EDGE, TopAbs_FACE, map);
					if (map.Extent() > profile_threshold_) {
						BRep_Builder BB;
						BB.MakeCompound(profile_edges);
						compound_to_hlr = &profile_edges;

						for (int i = 1; i <= map.Extent(); ++i) {
							auto& edge = TopoDS::Edge(map.FindKey(i));
							TopoDS_Vertex v0, v1;
							TopExp::Vertices(edge, v0, v1);
							auto pnt0 = BRep_Tool::Pnt(v0);
							auto pnt1 = BRep_Tool::Pnt(v1);
							
							// Exclude edges that have both vertices behind plane;
							if (infront_or_behind(projection_plane, pnt0) != -1 && infront_or_behind(projection_plane, pnt1) != -1) {
								continue;
							}
							
							double u0, u1;
							auto crv = BRep_Tool::Curve(edge, u0, u1);
							gp_Pnt _;
							gp_Vec crvd1;
							crv->D1((u0 + u1) / 2., _, crvd1);
							if (crvd1.SquareMagnitude() < 1.e-5) {
								continue;
							}
							crvd1.Normalize();
							// Exclude edges parallel to view direction
							if (std::fabs(crvd1.Dot(projection_direction)) > 0.99) {
								continue;
							}

							auto faces = map.FindFromIndex(i);
							
							// Add non-manifold edges
							bool add = faces.Extent() != 2;

							// Add profile edges
							if (!add) {
								const auto& f0 = TopoDS::Face(faces.First());
								const auto& f1 = TopoDS::Face(faces.Last());

								auto s0 = BRep_Tool::Surface(f0);
								auto s1 = BRep_Tool::Surface(f1);

								// Only supported for planar faces at the moment
								if (s0->DynamicType() != STANDARD_TYPE(Geom_Plane)) {
									continue;
								}
								if (s1->DynamicType() != STANDARD_TYPE(Geom_Plane)) {
									continue;
								}

								// Look up direction
								auto p0 = Handle(Geom_Plane)::DownCast(s0);
								auto p1 = Handle(Geom_Plane)::DownCast(s1);
								auto d0 = p0->Axis().Direction();
								auto d1 = p1->Axis().Direction();

								auto dot0 = projection_direction.Dot(d0);
								auto dot1 = projection_direction.Dot(d1);

								if (std::fabs(dot0) < 1.e-5 || std::fabs(dot1)) {
									// In case one face is co planar with the view
									// direction, add the edge in between
									add = true;
								} else {
									// Profile edges are adges where the sign of the
									// dot product Vdir . Fnormal flips sign.
									add = std::signbit(dot0) != std::signbit(dot1);
								}								
							}

							if (add) {
								BB.Add(profile_edges, edge);
							}							
						}
					}
				}

				// SVG edge classification (issue #3668): classify *compound_to_hlr's edges (real
				// face topology, pre-HLR) into per-class edge-only sub-compounds. The full shape
				// is still registered via add()/it->second.add() below, unchanged, for correct
				// occlusion; these buckets only affect which class each edge's visible portion is
				// later extracted as (see hlr_calc::extract() in SvgSerializer.h).
				//
				// Gated behind svg_use_edge_classification_ (default false): the whole block must
				// be skipped, not just individually suppressed per-edge, so that when disabled
				// classified_edge_buckets stays empty for *every* product in the document, not
				// just this one. hlr_calc::extract() only takes the classified-buckets branch
				// when its shared classified_shapes_ list is non-empty; if even one product added
				// classified buckets while others didn't, those others would silently fall back
				// to unclassified linework while this one used classification, an inconsistent
				// mix. Leaving classified_edge_buckets empty here means add_classified_edges() is
				// never called for this product either, so every product uniformly falls through
				// to the pre-existing product_shapes_ fallback -- the original, pre-classification
				// linework.
				std::map<std::string, TopoDS_Compound> classified_edge_buckets;
				if (svg_use_edge_classification_) {
					NCollection_IndexedDataMap<TopoDS_Shape, NCollection_List<TopoDS_Shape>, TopTools_ShapeMapHasher> edge_face_map;
					TopExp::MapShapesAndAncestors(*compound_to_hlr, TopAbs_EDGE, TopAbs_FACE, edge_face_map);

					gp_Dir view_dir;
					try {
						view_dir = gp_Dir(projection_direction);
					} catch (const Standard_Failure&) {
						view_dir = gp::DZ();
					}

					// Once per product (not per edge): does this product's own shape have a
					// genuine opening anywhere (a naked/boundary edge with != 2 adjacent
					// faces)? classify_edge_from_faces()'s back-facing "seen through an
					// opening" reinterpretation only makes sense when this is true -- see its
					// own comment for the real-world bug this was found from.
					bool product_has_naked_edge = false;
					for (int i = 1; i <= edge_face_map.Extent(); ++i) {
						if (edge_face_map.FindFromIndex(i).Extent() != 2) {
							product_has_naked_edge = true;
							break;
						}
					}

					BRep_Builder BBcls;
					for (int i = 1; i <= edge_face_map.Extent(); ++i) {
						const TopoDS_Edge& cls_edge = TopoDS::Edge(edge_face_map.FindKey(i));

						edge_style_class cls = edge_style_class::outline;
						try {
							cls = classify_edge_from_faces(cls_edge, edge_face_map.FindFromIndex(i), view_dir, svg_ridge_angle_min_deg_, svg_valley_angle_min_deg_, product_has_naked_edge);
						} catch (const Standard_Failure& e) {
							logger_.Warning("SER", 30, std::string("SVG edge classification OCC exception: ") + e.GetMessageString());
						} catch (const std::exception& e) {
							logger_.Warning("SER", 31, std::string("SVG edge classification exception: ") + e.what());
						}

						if (cls == edge_style_class::flush && !svg_emit_flush_edges_) {
							continue;
						}
						if (cls == edge_style_class::crease && !svg_render_crease_edges_) {
							continue;
						}
						if (cls == edge_style_class::sharp && !svg_render_sharp_edges_) {
							continue;
						}

						std::string name = edge_style_class_name(cls);
						auto bucket_it = classified_edge_buckets.find(name);
						if (bucket_it == classified_edge_buckets.end()) {
							TopoDS_Compound c;
							BBcls.MakeCompound(c);
							bucket_it = classified_edge_buckets.emplace(name, c).first;
						}
						BBcls.Add(bucket_it->second, cls_edge);
					}

					// Non-planar faces (e.g. a real analytic cylindrical wall from a
					// circular-profile column/pile, swept via BRepPrimAPI_MakePrism rather than
					// faceted) have a silhouette that HLR synthesizes on the fly -- it is not a
					// pre-existing topological edge, so the edge-only loop above can never bucket
					// it. OutLineVCompound(S) correlates a curved face's silhouette by the
					// identity of the originating *face*, not any edge, so add the non-planar
					// face itself into the outline bucket alongside whatever edges it already
					// contributed (top/bottom/seam), giving HLR's per-face OutLine reconstruction
					// something to match against.
					for (TopExp_Explorer fexp(*compound_to_hlr, TopAbs_FACE); fexp.More(); fexp.Next()) {
						const TopoDS_Face& f = TopoDS::Face(fexp.Current());
						if (BRep_Tool::Surface(f)->DynamicType() != STANDARD_TYPE(Geom_Plane)) {
							std::string name = edge_style_class_name(edge_style_class::outline);
							auto bucket_it = classified_edge_buckets.find(name);
							if (bucket_it == classified_edge_buckets.end()) {
								TopoDS_Compound c;
								BBcls.MakeCompound(c);
								bucket_it = classified_edge_buckets.emplace(name, c).first;
							}
							BBcls.Add(bucket_it->second, f);
						}
					}
				}

				// "mat-style-change" case B (intra-product layer-boundary lining) used to run
				// here, per-item. It now runs from hlr_t::build(), after every product sharing
				// this drawing/storey has been add()-ed -- see generate_mat_style_change_case_b_
				// edges() and the mat_style_change namespace's own comments in SvgSerializer.h
				// for why: telling a genuinely-matched touching boundary apart from a face with
				// no neighbour at all needs every other product's geometry to already be known,
				// which per-item processing here structurally can't provide.

				if (is_floor_plan_) {
					if (storey) {
						auto it = storey_hlr.find(storey);
						if (it == storey_hlr.end()) {
							it = storey_hlr.insert({ storey, hlr_t(logger_, use_prefiltering_, use_hlr_poly_, segment_projection_, projection_plane,
								svg_use_edge_classification_, svg_use_cross_coplanar_classification_, svg_cross_coplanar_tolerance_,
								svg_render_cross_coplanar_edges_, svg_use_mat_style_change_classification_) }).first;
						}
						it->second.add(*compound_to_hlr, data.product, data.cross_coplanar_style_instance, data.cross_coplanar_material_instance, data.cross_coplanar_layer_projection);
						for (auto& kv : classified_edge_buckets) {
							it->second.add_classified_edges(data.product, kv.first, kv.second);
						}
					} else {
						logger_.Warning("SER", 28, "Unable to invoke HLR due to absence of storey containment", data.product);
					}
				} else if (hlr) {
					hlr->add(*compound_to_hlr, data.product, data.cross_coplanar_style_instance, data.cross_coplanar_material_instance, data.cross_coplanar_layer_projection);
					for (auto& kv : classified_edge_buckets) {
						hlr->add_classified_edges(data.product, kv.first, kv.second);
					}
				}
			}
		}

		TopoDS_Iterator it(compound_to_use);
		auto dash_it = data.dash_arrays.begin();

		TopoDS_Face largest_closed_wire_face;
		double largest_closed_wire_area = 0.;

		gp_Pln pln;
		if (variant.which() < 2) {
			pln = gp_Pln(gp_Pnt(0, 0, cut_z), gp::DZ());
		} else {
			const auto& section = boost::get<vertical_section>(variant);
			pln = section.plane;
		}

		auto svg_name = data.svg_name;
		
		path_object* po_ = nullptr;
		auto po = [this, &po_, &pln, &storey, &drawing_name, &svg_name]() {
			if (po_ == nullptr) {
				if (storey) {
					po_ = &start_path(pln, storey, svg_name);
				} else {
					po_ = &start_path(pln, drawing_name, svg_name);
				}
			}
			return po_;
		};

		// Iterate over components of compound to have better chance of matching section edges to closed wires
		for (; it.More(); it.Next(), ++dash_it) {

			const TopoDS_Shape& subshape = it.Value();

			Bnd_Box bb;
			try {
				BRepBndLib::Add(it.Value(), bb);
			} catch (const Standard_Failure&) {}

			// Empty geometry
			if (bb.IsVoid()) {
				continue;
			}

			double x1, y1, zmin, x2, y2, zmax;
			bb.Get(x1, y1, zmin, x2, y2, zmax);

			// Determine slicing plane z coordinate, priority:
			// 1) explicitly set global section height
			// 2) containing building storey elevation + 1m
			// 3) zmin (from geometry bounding box) + 1m

			if (variant.which() == 1) {
				cut_z = zmin + 1.;
			}

			gp_Vec bbmin(x1, y1, zmin);
			gp_Vec bbmax(x2, y2, zmax);
			auto bbdif = bbmax - bbmin;
			auto proj = projection_direction ^ bbdif ^ projection_direction;

			std::string object_type;
			auto ot_arg = data.product->get("ObjectType");
			if (!ot_arg.isNull()) {
				object_type = (std::string) ot_arg;
				object_type.erase(std::remove_if(object_type.begin(), object_type.end(), [](char c) { return !std::isalnum(c); }), object_type.end());
			}

			auto z_global = gp::DZ().Transformed(data.trsf);
			auto xyz_global = gp_Pnt().Transformed(data.trsf);
			int state = infront_or_behind(projection_plane, xyz_global);

			if (data.product->declaration().is("IfcAnnotation") &&     // is an Annotation
				(proj.Magnitude() > 1.e-5) && 					       // when projected onto the view has a length
				(is_floor_plan_
					? (zmin >= range.first && zmin < (range.second - 1.e-5)) // the Z-coords are within the range of the building storey,
				                                                             // this excludes the upper bound with a small tolerance
					: (projection_direction.Dot(z_global) > 0.99 && state == -1)            // For elevations only include annotations that are "facing" the view direction
				))
			{
				if (object_type.size()) {
					// postfix the object_type for CSS matching
					boost::replace_all(svg_name, "class=\"IfcAnnotation\"", "class=\"IfcAnnotation " + object_type + "\"");
				}

				auto subshape_to_use = subshape;
				if (variant.which() == 2) {
					// @todo remove duplication with code below.

					gp_Trsf trsf;
					trsf.SetTransformation(gp::XOY(), pln.Position());
					subshape_to_use.Move(trsf);

					BRepBuilderAPI_Transform make_transform_mirror_(subshape_to_use, trsf_mirror, true);
					make_transform_mirror_.Build();
					subshape_to_use = make_transform_mirror_.Shape();
				}

				if (object_type == "Dimension") {

					TopExp_Explorer exp(subshape_to_use, TopAbs_EDGE, TopAbs_FACE);
					for (; exp.More(); exp.Next()) {
						const auto& e = TopoDS::Edge(exp.Current());
						TopoDS_Vertex v0, v1;
						TopExp::Vertices(e, v0, v1);
						gp_Pnt p0 = BRep_Tool::Pnt(v0);
						gp_Pnt p1 = BRep_Tool::Pnt(v1);
						BRep_Builder B;
						TopoDS_Wire W;
						B.MakeWire(W);
						B.Add(W, e);
						write(*po(), W);

						// @todo should we take the average parameter value instead?
						gp_XYZ center = (p0.XYZ() + p1.XYZ()) / 2.;
						double z_rotation = gp_Dir(p0.XYZ() - p1.XYZ()).AngleWithRef(gp_Dir(1., 0., 0.), gp_Dir(0., 0., 1.));
						z_rotation *= 180. / M_PI;
						if (z_rotation < -88) {
							z_rotation += 180;
						}
						if (z_rotation > +90) {
							z_rotation -= 180;
						}

						std::string text_offset = "8";
						if (scale_) {
							text_offset = "1";
						}

						util::string_buffer path;
						// dominant-baseline="central" is not well supported in IE.
						// so we add a 0.35 offset to the dy of the tspans
						path.add("            <text class=\"IfcAnnotation\" text-anchor=\"middle\" x=\"");
						xcoords.push_back(path.add(center.X()));
						path.add("\" y=\"");
						ycoords.push_back(path.add(center.Y()));
						path.add("\" transform=\"rotate(");
						path.add(z_rotation);
						path.add(" ");
						xcoords.push_back(path.add(center.X()));
						path.add(" ");
						ycoords.push_back(path.add(center.Y()));
						path.add(") translate(0 -" + text_offset + ")\">");

						std::vector<std::string> labels{};

						GProp_GProps prop;
						BRepGProp::LinearProperties(e, prop);
						const double area = prop.Mass();
						std::stringstream ss;
						ss << std::setprecision(2) << std::fixed << std::showpoint << area;
						labels.push_back(ss.str() + "m");

						for (auto lit = labels.begin(); lit != labels.end(); ++lit) {
							auto l = *lit;
							IfcUtil::escape_xml(l);
							double dy = labels.begin() == lit
								? 0.35 - (labels.size() - 1.) / 2.
								: 1.0; // <- dy is relative to the previous text element, so
									   //    always 1 for successive spans.
							path.add("<tspan x=\"");
							xcoords.push_back(path.add(center.X()));
							path.add("\" dy=\"");
							path.add(boost::lexical_cast<std::string>(dy));
							path.add("em\">");
							path.add(l);
							path.add("</tspan>");
						}
						path.add("</text>");
						po()->second.push_back(path);
					}
					
				} else if (object_type == "Symbol") {

					TopExp_Explorer exp(subshape_to_use, TopAbs_WIRE, TopAbs_FACE);
					for (; exp.More(); exp.Next()) {
						const auto& W = TopoDS::Wire(exp.Current());
						write(*po(), W, *dash_it);
					}
					
				}

				// We're finished processing IfcAnnotation instances
				continue;
			}

			if (subshape.ShapeType() > TopAbs_FACE) {
				// Except for annotations we only emit solids and surfaces to SVG.
				emitted = true;
				continue;
			}

			// No intersection with bounding box, fail early
			if (variant.which() < 2) {
				if (zmin > cut_z || zmax < cut_z) continue;
			}

			emitted = true;

			if (object_type.size()) {
				// prefix class to indicate this is a cut element
				// @todo this is getting out of control, use a proper xml/svg library.
				if(svg_name.find("class=\"cut ") == std::string::npos) {
					boost::replace_all(svg_name, "class=\"", "class=\"cut ");
				}
			}

			// Same defensive healing as the halfspace-cut path above (BRepAlgoAPI_Cut): a
			// genuinely degenerate/self-intersecting subshape can make BRepAlgoAPI_Section
			// itself crash outright rather than throw (confirmed against the same real wall
			// with two overlapping IfcOpeningElement voids, issue: PROPOSED SECTION crash --
			// this is a second OCCT boolean-adjacent operation the same bad geometry reaches,
			// not a duplicate fix for the same call).
			TopoDS_Shape subshape_to_cut = subshape;
			try {
				if (!BRepCheck_Analyzer(subshape_to_cut).IsValid()) {
					ShapeFix_Shape fixer(subshape_to_cut);
					fixer.Perform();
					subshape_to_cut = fixer.Shape();
				}
			} catch (const Standard_Failure&) {
				// Leave subshape_to_cut as the original -- worst case we're back to the
				// original (unguarded) crash risk for this one degenerate subshape, same as
				// before this fix existed.
			}
			TopoDS_Shape result = BRepAlgoAPI_Section(subshape_to_cut, pln);

			if (variant.which() == 2) {
				gp_Trsf trsf;
				trsf.SetTransformation(gp::XOY(), pln.Position());
				result.Move(trsf);

				BRepBuilderAPI_Transform make_transform_mirror_(result, trsf_mirror, true);
				make_transform_mirror_.Build();
				result = make_transform_mirror_.Shape();
			}

#if OCC_VERSION_HEX >= 0x80000
			opencascade::handle<NCollection_HSequence<TopoDS_Shape>> edges = new NCollection_HSequence<TopoDS_Shape>();
			opencascade::handle<NCollection_HSequence<TopoDS_Shape>> wires = new NCollection_HSequence<TopoDS_Shape>();
#else
			Handle(TopTools_HSequenceOfShape) edges = new TopTools_HSequenceOfShape();
			Handle(TopTools_HSequenceOfShape) wires = new TopTools_HSequenceOfShape();
#endif
			{
				TopExp_Explorer exp(result, TopAbs_EDGE);
				for (; exp.More(); exp.Next()) {
					edges->Append(exp.Current());
				}
			}
			ShapeAnalysis_FreeBounds::ConnectEdgesToWires(edges, 1e-5, false, wires);

			gp_Pnt prev;

			TopoDS_Compound wires_compound;
			BRep_Builder BB;
			BB.MakeCompound(wires_compound);

			for (int i = 1; i <= wires->Length(); ++i) {
				
				// @nb not const, because in case of storey annotations we might
				// generate a new wire with fixed length

				TopoDS_Wire wire = TopoDS::Wire(wires->Value(i));

				if (wire.Closed() && (print_space_names_ || print_space_areas_) && data.product->declaration().is("IfcSpace")) {
					// we explicitly specify the surface here, to later on
					// simplify the projection from {x,y,z} to {u, v} because
					// we know we can simply discard z.
					BRepBuilderAPI_MakeFace mf(pln, wire);
					if (mf.IsDone()) {
						TopoDS_Face f = mf.Face();
						GProp_GProps prop;
						BRepGProp::SurfaceProperties(f, prop);
						const double area = prop.Mass();
						if (area > largest_closed_wire_area) {
							largest_closed_wire_face = f;
							largest_closed_wire_area = area;
						}
					}

				}
				
				if (file && data.product->declaration().is("IfcBuildingStorey") && storey_height_display_ != SH_NONE && wires->Length() == 1 && IfcGeom::util::count(wire, TopAbs_EDGE) == 1) {
					
					std::string elev_str;

					const double lu = file->getUnit("LENGTHUNIT").second;
					auto a = data.product->get("Elevation");
					if (!a.isNull()) {
						double elev = a;
						
						// @nb we don't actually factor in the length unit.
						// elev *= lu;
						
						if (almost(1.) == lu) {
							// m
							elev_str = boost::str(boost::format("%.3f") % elev);
						}
						else {
							elev_str = boost::str(boost::format("%d") % ((int) elev));
						}
					}

					std::vector<std::string> labels{ data.ifc_name, elev_str };
					util::string_buffer path;

					TopExp_Explorer exp(wire, TopAbs_EDGE);
					auto edge = TopoDS::Edge(exp.Current());
					TopoDS_Vertex v0, v1;
					TopExp::Vertices(edge, v0, v1);
					gp_Pnt p0 = BRep_Tool::Pnt(v0);
					gp_Pnt p1 = BRep_Tool::Pnt(v1);

					if (p0.X() > p1.X()) {
						std::swap(p0, p1);
					}

					// @todo these settings are getting out of hand, how can we
					// streamline this?
					std::string anchor;
					gp_Pnt* anchor_pt;
					if (storey_height_display_ == SH_FULL) {
						anchor = "end";
						anchor_pt = &p1;
					} else {
						anchor = "start";
						anchor_pt = &p0;

						auto d = (p1.XYZ() - p0.XYZ());
						d.Normalize();
						const double shll = storey_height_line_length_.get_value_or(2.);
						d *= shll;
						gp_Pnt p1x(p0.XYZ() + d);

						wire = BRepBuilderAPI_MakePolygon(p0, p1x).Wire();
					}

					// dominant-baseline="central" is not well supported in IE.
					// so we add a 0.35 offset to the dy of the tspans
					path.add("            <text text-anchor=\"" + anchor + "\" x=\"");
					xcoords.push_back(path.add(anchor_pt->X()));
					path.add("\" y=\"");
					ycoords.push_back(path.add(anchor_pt->Y()));
					path.add("\">");
					for (auto lit = labels.begin(); lit != labels.end(); ++lit) {
						auto l = *lit;
						IfcUtil::escape_xml(l);
						double dy = labels.begin() == lit
							? 0.35 - (labels.size() - 1.) / 2.
							: 1.0; // <- dy is relative to the previous text element, so
								   //    always 1 for successive spans.
						path.add("<tspan x=\"");
						xcoords.push_back(path.add(anchor_pt->X()));
						path.add("\" dy=\"");
						path.add(boost::lexical_cast<std::string>(dy));
						path.add("em\">");
						path.add(l);
						path.add("</tspan>");
					}
					path.add("</text>");
					po()->second.push_back(path);
				}

				BB.Add(wires_compound, wire);
			}

			if (TopoDS_Iterator(wires_compound).More()) {
				write(*po(), wires_compound);
			}
		}

		if (!largest_closed_wire_face.IsNull()) {
			std::vector<gp_Pnt> points;
			TopExp_Explorer exp(largest_closed_wire_face, TopAbs_VERTEX);
			for (; exp.More(); exp.Next()) {
				if (exp.Current().Orientation() == TopAbs_FORWARD) {
					const TopoDS_Vertex& v = TopoDS::Vertex(exp.Current());
					points.push_back(BRep_Tool::Pnt(v));
				}
			}

			// we brute force the largest distance between pairs of points where
			// the center is contained in the face.

			std::pair<const gp_Pnt*, const gp_Pnt*> furthest_points = { nullptr, nullptr };
			double furthest_points_distance = 0.;
			boost::optional<gp_Pnt> center_point;

			BRepTopAdaptor_FClass2d fcls(largest_closed_wire_face, BRep_Tool::Tolerance(largest_closed_wire_face));

			for (size_t i = 0; i < points.size(); ++i) {
				for (size_t j = 0; j < i; ++j) {
					const gp_Pnt& pa = points[i];
					const gp_Pnt& pb = points[j];
					// Since the text is always displayed horizontally,
					// the distance is not simply euclidean, but we
					// favour the x-component;
					const double d = std::sqrt(
						10 * ((pa.X() - pb.X()) * (pa.X() - pb.X())) +
						1 * ((pa.Y() - pb.Y()) * (pa.Y() - pb.Y()))
					);

					if (d > furthest_points_distance) {
						
						// Sample some points on the line and assure it's inside.
						bool all_inside = true;
						for (int n = 5; n < 95; ++n) {
							gp_Pnt p3d((pa.XYZ() + (pb.XYZ() - pa.XYZ()) * n / 100.));
							gp_Pnt2d p2d(p3d.X(), p3d.Y());

							if (fcls.Perform(p2d) != TopAbs_IN) {
								all_inside = false;
							}
						}

						if (all_inside) {
							gp_Pnt p3d((pa.XYZ() + pb.XYZ()) * 0.5);
							gp_Pnt2d p2d(p3d.X(), p3d.Y());
							furthest_points = { &pa, &pb };
							furthest_points_distance = d;
							center_point = p3d;
						}

					}
				}
			}

			if (center_point) {
				std::vector<std::string> labels;
				if (print_space_names_) {
					labels.push_back(data.ifc_name);
				}
				if (print_space_names_ && data.product->declaration().is("IfcSpace")) {
					auto attr = data.product->get("LongName");
					if (!attr.isNull()) {
						std::string long_name = attr;
						if (!long_name.empty()) {
							labels.insert(labels.begin(), long_name);
						}
					}
				}
				if (print_space_areas_) {
					GProp_GProps prop;
					BRepGProp::SurfaceProperties(largest_closed_wire_face, prop);
					const double area = prop.Mass();
					std::stringstream ss;
					ss << std::setprecision(2) << std::fixed << std::showpoint << area;
					labels.push_back(ss.str() + "m&#178;");
				}

				util::string_buffer path;
				// dominant-baseline="central" is not well supported in IE.
				// so we add a 0.35 offset to the dy of the tspans
				path.add("            <text text-anchor=\"middle\" x=\"");
				xcoords.push_back(path.add(center_point->X()));
				path.add("\" y=\"");
				ycoords.push_back(path.add(center_point->Y()));
				path.add("\"");
				if (space_name_transform_) {
					path.add(" transform=\"" + *space_name_transform_ + "\"");
				}
				path.add(">");
				for (auto lit = labels.begin(); lit != labels.end(); ++lit) {
					auto l = *lit;
					IfcUtil::escape_xml(l);
					double dy = labels.begin() == lit
						? 0.35 - (labels.size() - 1.) / 2.
						: 1.0; // <- dy is relative to the previous text element, so
							   //    always 1 for successive spans.
					path.add("<tspan x=\"");
					xcoords.push_back(path.add(center_point->X()));
					path.add("\" dy=\"");
					path.add(boost::lexical_cast<std::string>(dy));
					path.add("em\">");
					path.add(l);
					path.add("</tspan>");
				}
				path.add("</text>");
				po()->second.push_back(path);
			}
		}

		if (!annotation.IsNull()) {
			write(*po(), annotation);
		}
	}

	if (!emitted) {
		logger_.Warning("SER", 29, "Element not written to SVG due to section heights", data.product);
	}
}

void SvgSerializer::setBoundingRectangle(double width, double height) {
	size_ = std::make_pair(width, height);
}

std::array<std::array<double, 3>, 3> SvgSerializer::resize() {
	// identity matrix;
	std::array<std::array<double, 3>, 3> m = {{ {{1,0,0}},{{0,1,0}},{{0,0,1}} }};

	if (size_) {
		// Scale the resulting image to a bounding rectangle specified by command line arguments
		// or specified by IfcAnnotation[ObjectType=DRAWING]
		const double dx = xmax - xmin;
		const double dy = ymax - ymin;

		double sc, cx, cy;
		if (offset_2d_ && scale_) {
			// offset_2d is the offset in plane u,v coordinates as we want to keep the 
			// plane coordinates used for HLR close to the model origin.
			sc = (*scale_) * 1000;
			cx = offset_2d_->first;
			cy = offset_2d_->second;
		} else if (scale_) {
			sc = (*scale_) * 1000;
			cx = (xmax + xmin) / 2. * sc - size_->first * center_x_.get_value_or(0.5);
			cy = (ymax + ymin) / 2. * sc - size_->second * center_y_.get_value_or(0.5);
		} else {
			if (calculated_scale_) {
				sc = *calculated_scale_;
			}
			else {
				if (dx / size_->first > dy / size_->second) {
					sc = size_->first / dx;
				}
				else {
					sc = size_->second / dy;
				}
				calculated_scale_ = sc;
			}
			cx = xmin * sc;
			cy = ymin * sc;
		}

		if (mirror_y_) {
			cy = - size_->second - cy;
		}
		if (mirror_x_) {
			cx = - size_->first - cx;
		}

		m = {{ {{sc,0,-cx}},{{0,sc,-cy}},{{0,0,1}} }};

		float_item_list::const_iterator it;
		for (it = xcoords.begin() + xcoords_begin; it != xcoords.end(); ++it, ++xcoords_begin) {
			double& v = (*it)->value();
			v = v * sc - cx;
		}
		for (it = ycoords.begin() + ycoords_begin; it != ycoords.end(); ++it, ++ycoords_begin) {
			double& v = (*it)->value();
			v = v * sc - cy;
		}
		for (it = radii.begin() + radii_begin; it != radii.end(); ++it, ++radii_begin) {
			(*it)->value() *= sc;
		}
	}

	return m;
}

namespace {
	// Cross-product coincident-edge deduplication (issue #3742 follow-up). When two DIFFERENT
	// products each independently produce an edge at (or extremely near) the same real-world
	// location -- e.g. two touching objects whose shared boundary is visible from both sides --
	// which one ends up drawn on top in the final flat SVG is NOT spatial: it comes from
	// IfcGeom::Iterator's multi-threaded worker-completion order (a race between threads
	// finishing geometry conversion for different products), then products are written to the
	// SVG in that same order -- since SVG has no Z-index, later elements simply paint over
	// earlier ones regardless of true camera-space depth. Real, correct, cross-product HLR
	// *does* already run (prefiltered_hlr::build() adds every product sharing a drawing/storey
	// into one shared HLRBRep_Algo/PolyAlgo before a single Hide()/Update() call), so this is
	// never a visibility-computation bug -- both of two touching products' coincident edges are
	// genuinely, correctly visible (neither occludes the other, since they're at the same
	// location). The bug is purely which of two coincident-but-both-visible edges paints on top.
	//
	// Fixed here with a pass over every item's edges (still real TopoDS_Edge/gp_Pnt data, before
	// any mirroring or stringification into SVG path text), bucketing by a canonical
	// (endpoint-order-independent) key quantized to cross-coplanar-tolerance-scale precision.
	// Any bucket spanning more than one distinct product keeps only the single highest-priority
	// edge (see kClassPriority below) -- deterministic regardless of processing order, so the
	// visually-correct edge always wins.

	// Priority for picking a winner among coincident duplicate edges from different products
	// (lower number = higher priority = wins). `outline` is a product's own true silhouette and
	// always wins when it coincides with anything else -- confirmed against a reported case
	// where a mat-style-change edge wrongly painted over the true outline of the object actually
	// visible from this camera. `mat-style-change`/`cross-coplanar` represent a *resolved*
	// cross-product matching decision (more specific than an ordinary single-object
	// classification), so they outrank sharp/crease/flush, but still lose to a genuine outline
	// on the other side. `boundary` (naked/non-manifold edges) has no confirmed test case in
	// this scenario; placed conservatively last.
	int coincident_edge_class_priority(const std::string& cls) {
		if (cls == "outline") return 0;
		if (cls == mat_style_change::class_name) return 1;
		if (cls == cross_coplanar::class_name) return 2;
		if (cls == "sharp") return 3;
		if (cls == "crease") return 4;
		if (cls == "flush") return 5;
		return 6; // "boundary" or anything unrecognised
	}

	using quant_pnt = std::tuple<long long, long long, long long>;
	using quant_edge_key = std::pair<quant_pnt, quant_pnt>;

	size_t mix_quant_triple(long long a, long long b, long long c) {
		size_t h = std::hash<long long>()(a);
		h ^= std::hash<long long>()(b) + 0x9e3779b9 + (h << 6) + (h >> 2);
		h ^= std::hash<long long>()(c) + 0x9e3779b9 + (h << 6) + (h >> 2);
		return h;
	}

	struct quant_pnt_hash {
		size_t operator()(const quant_pnt& p) const {
			return mix_quant_triple(std::get<0>(p), std::get<1>(p), std::get<2>(p));
		}
	};

	struct quant_edge_key_hash {
		size_t operator()(const quant_edge_key& k) const {
			size_t h0 = mix_quant_triple(std::get<0>(k.first), std::get<1>(k.first), std::get<2>(k.first));
			size_t h1 = mix_quant_triple(std::get<0>(k.second), std::get<1>(k.second), std::get<2>(k.second));
			return h0 ^ (h1 + 0x9e3779b9 + (h0 << 6) + (h0 >> 2));
		}
	};

	quant_pnt quantize_point(const gp_Pnt& p, double scale) {
		return { std::llround(p.X() * scale), std::llround(p.Y() * scale), std::llround(p.Z() * scale) };
	}

	quant_edge_key make_edge_key(const gp_Pnt& p0, const gp_Pnt& p1, double scale) {
		quant_pnt q0 = quantize_point(p0, scale);
		quant_pnt q1 = quantize_point(p1, scale);
		return (q0 <= q1) ? quant_edge_key{ q0, q1 } : quant_edge_key{ q1, q0 };
	}

	// Flattens a 3D point onto the current view/drawing plane by dropping its depth (Z)
	// coordinate. Used ONLY by the coincident-edge dedup passes below
	// (compute_coincident_edge_best_priority()/compute_coincident_edge_overlap_coverage()) --
	// unlike cross_coplanar's own matching (which needs true 3D coincidence, since it's about two
	// products genuinely touching in the model), dedup is about "which of two edges paints on top
	// of the other in the final flat SVG", which is a *screen-space* question. By the time
	// draw_hlr() runs, hlr_items' edges are already expressed in the camera-aligned frame HLR was
	// computed in -- X/Y are already the (pre-scale, pre-mirror) SVG plot coordinates and Z is
	// purely depth-into-screen (see SvgSerializer::write()'s own comment on this, where the same
	// convention is relied on for path-text output); dropping Z is therefore all "projection"
	// requires here, with no plane-basis reconstruction needed. Two edges belonging to genuinely
	// different, non-touching 3D locations (e.g. a sloped wall edge crossing a level slab edge at
	// different heights) can still land almost exactly on top of each other once flattened --
	// confirmed directly against a real drawing (issue #3742 follow-up): a wall's own diagonal
	// edge and a slab's own top-face outline edge differed by up to ~0.7 model units of depth
	// (their true 3D lines are NOT collinear, so the pre-existing 3D-space collinearity test
	// correctly, but unhelpfully, rejected them as unrelated), yet agreed to within a fraction of
	// a millimetre in X/Y, painting a visually-duplicate stray line end-to-end alongside the
	// slab's correct outline. Parallel/orthographic projection (the only kind these architectural
	// drawings use) preserves a segment's own [0,1] parametrization under projection, so overlap
	// fractions computed here remain valid when re-applied to the original, unprojected 3D edge
	// for clipping (see compute_coincident_edge_overlap_coverage()).
	gp_Pnt project_to_view_plane(const gp_Pnt& p) {
		return gp_Pnt(p.X(), p.Y(), 0.0);
	}

	// Computes, for every coincident-edge bucket that genuinely mixes classes across more than
	// one product, the best (lowest-number) class priority present. Deliberately does NOT
	// resolve buckets where every contributing product agrees on the same class -- e.g. both
	// sides of a legitimate internal seam independently computing `cross-coplanar`, or both
	// sides of a real material transition computing `mat-style-change`, is the correct,
	// *intentional* outcome (both are meant to be shown together when cross-coplanar/
	// mat-style-change rendering is enabled for QA, or both hidden together otherwise) -- not a
	// paint-order bug to fix. Only a genuine class *mismatch* (e.g. one side `outline`, the
	// other `sharp`) indicates one of the two is the wrong edge to be painting on top of the
	// other; same-class duplicates are left completely untouched.
	// Second element: keys where an `outline` edge shares the exact same quantized endpoints as a
	// `cross-coplanar` OR Case-A `mat-style-change` edge -- `outline` unconditionally loses that
	// specific collision (see the cross-coplanar-vs-outline exception in
	// compute_coincident_edge_overlap_coverage()'s own comment for the full rationale; this is
	// that same exception's exact-key counterpart, extended to mat-style-change here because the
	// EXACT-key case is specifically an HLR duplicate-fragment artifact, never Case B's own
	// deliberate nesting -- Case B's layer-boundary edges are constructed strictly shorter than
	// (nested inside) the outline edge they share a line with, so they essentially never share
	// BOTH endpoints exactly; that confirmed regression's own fix lives entirely in the
	// overlap-coverage function below, untouched by this exact-key exception. Issue #3742
	// follow-up, NORTH SECTION TILT "Extrusion L2"/"Shifted in space"/"Hole on edge" cases: HLR's
	// own silhouette computation for a product's plain `outline` bucket and for that same
	// product's already-verified `cross-coplanar`/`mat-style-change` bucket can each independently
	// emit a short fragment with IDENTICAL endpoints at a genuine corner, and the plain aggregate
	// "lowest priority number wins" rule can't express "outline loses to X but still beats
	// everything else" -- outline's own priority number (0, the global minimum) can never be
	// "worse than the best" by that comparison alone.
	std::pair<std::unordered_map<quant_edge_key, int, quant_edge_key_hash>, std::unordered_set<quant_edge_key, quant_edge_key_hash>>
	compute_coincident_edge_best_priority(
		const std::list<std::tuple<const IfcUtil::IfcBaseEntity*, std::string, TopoDS_Shape>>& hlr_items,
		double tolerance
	) {
		const double scale = 1.0 / tolerance;
		struct edge_ref {
			const IfcUtil::IfcBaseEntity* product;
			int priority;
			std::string cls;
		};
		std::unordered_map<quant_edge_key, std::vector<edge_ref>, quant_edge_key_hash> buckets;

		for (auto& item : hlr_items) {
			const IfcUtil::IfcBaseEntity* product = std::get<0>(item);
			const std::string& cls = std::get<1>(item);
			const TopoDS_Shape& shape = std::get<2>(item);
			if (shape.IsNull()) {
				continue;
			}
			int prio = coincident_edge_class_priority(cls);
			for (TopExp_Explorer eexp(shape, TopAbs_EDGE); eexp.More(); eexp.Next()) {
				TopoDS_Vertex v0, v1;
				TopExp::Vertices(TopoDS::Edge(eexp.Current()), v0, v1);
				if (v0.IsNull() || v1.IsNull()) {
					continue;
				}
				// Keyed on the SCREEN-projected position, not true 3D -- see
				// project_to_view_plane()'s own comment for why.
				auto key = make_edge_key(
					project_to_view_plane(BRep_Tool::Pnt(v0)),
					project_to_view_plane(BRep_Tool::Pnt(v1)),
					scale);
				buckets[key].push_back({ product, prio, cls });
			}
		}

		std::unordered_map<quant_edge_key, int, quant_edge_key_hash> best_priority_by_key;
		std::unordered_set<quant_edge_key, quant_edge_key_hash> outline_loses_exact_key;
		for (auto& kv : buckets) {
			bool multi_product = false;
			bool multi_priority = false;
			bool has_outline = false;
			bool has_exception_class = false; // cross-coplanar or mat-style-change
			int best_prio = kv.second[0].priority;
			int best_prio_excluding_outline = kv.second[0].cls == "outline"
				? std::numeric_limits<int>::max() : kv.second[0].priority;
			for (size_t i = 0; i < kv.second.size(); ++i) {
				if (kv.second[i].product != kv.second[0].product) {
					multi_product = true;
				}
				if (kv.second[i].priority != kv.second[0].priority) {
					multi_priority = true;
				}
				if (kv.second[i].cls == "outline") {
					has_outline = true;
				} else {
					best_prio_excluding_outline = std::min(best_prio_excluding_outline, kv.second[i].priority);
				}
				if (kv.second[i].cls == cross_coplanar::class_name || kv.second[i].cls == mat_style_change::class_name) {
					has_exception_class = true;
				}
				if (i > 0) {
					best_prio = std::min(best_prio, kv.second[i].priority);
				}
			}
			bool exception_applies = has_outline && has_exception_class;
			// Only record a resolution for buckets that genuinely mix both products AND
			// classes -- same-class duplicates across products (e.g. both cross-coplanar) are
			// intentional and must be left alone (see the function comment above).
			if (multi_product && multi_priority) {
				best_priority_by_key[kv.first] = exception_applies ? best_prio_excluding_outline : best_prio;
			}
			if (exception_applies) {
				outline_loses_exact_key.insert(kv.first);
			}
		}
		return { best_priority_by_key, outline_loses_exact_key };
	}

	// Angular bucket width for the line-identity prefilter below. Deliberately looser than
	// kCoplanarNormalTolerance's own implied ~0.0087 rad (acos(1 - 3.8e-5)) -- over-inclusion here
	// only costs a few extra pairwise checks inside one small bucket, while under-inclusion would
	// silently skip a genuine nested-duplicate pair. Consistent in spirit with make_edge_key()'s
	// own single-rounding scheme just above.
	constexpr double kLineBucketAngularTolerance = 0.01;

	// Sign-canonicalizes `dir` (forces the largest-magnitude component positive -- two
	// independently-computed collinear edges can disagree on sign) then quantizes at
	// kLineBucketAngularTolerance-scale precision. Reuses quant_pnt as the tuple shape.
	quant_pnt quantize_direction(const gp_Dir& dir, double scale) {
		double c[3] = { dir.X(), dir.Y(), dir.Z() };
		int axis = 0;
		if (std::abs(c[1]) > std::abs(c[axis])) axis = 1;
		if (std::abs(c[2]) > std::abs(c[axis])) axis = 2;
		double sign = (c[axis] < 0.0) ? -1.0 : 1.0;
		return {
			std::llround(sign * c[0] * scale),
			std::llround(sign * c[1] * scale),
			std::llround(sign * c[2] * scale)
		};
	}

	// Builds a LineSeg directly from an edge's two vertex positions, rather than
	// cross_coplanar::edge_to_line_seg()'s BRep_Tool::Curve()-based approach. HLR output edges
	// (hlr_compound_full, before ShapeFix_Edge::FixAddCurve3d() runs further down in draw_hlr())
	// have no 3D curve attached yet, so edge_to_line_seg() -- built for pre-HLR real-face-topology
	// edges -- always returns boost::none here. Since HLR output for a BRep model is always
	// straight polygonal segments, reconstructing the line from its two endpoints is both
	// sufficient and more robust for this specific post-HLR use than depending on curve-type
	// introspection.
	boost::optional<cross_coplanar::LineSeg> edge_to_line_seg_from_vertices(const TopoDS_Edge& e) {
		TopoDS_Vertex v0, v1;
		TopExp::Vertices(e, v0, v1);
		if (v0.IsNull() || v1.IsNull()) {
			return boost::none;
		}
		gp_Pnt p0 = BRep_Tool::Pnt(v0);
		gp_Pnt p1 = BRep_Tool::Pnt(v1);
		if (p0.Distance(p1) < Precision::Confusion()) {
			return boost::none;
		}
		gp_Vec v(p0, p1);
		return cross_coplanar::LineSeg{ p0, p1, gp_Dir(v), v.Magnitude(), e };
	}

	// Detects collinear-overlap coincident-edge duplicates that compute_coincident_edge_best_priority
	// misses -- e.g. one edge fully nested inside another, collinear, LONGER edge (sharing at most
	// one endpoint; the exact-endpoint bucket above never groups these). Buckets every straight-line
	// edge across hlr_items by (quantized canonical direction, quantized foot point) -- i.e. "which
	// infinite 3D line is this edge on" -- so the pairwise collinear/overlap test only ever runs
	// within a small per-line bucket, never across the whole drawing. Within a bucket, for every pair
	// with *different* class priorities (same-priority overlaps -- e.g. both genuinely cross-coplanar
	// -- are skipped before any geometry test, same "intentional agreement" rule as
	// compute_coincident_edge_best_priority()) that are genuinely collinear with a non-trivial
	// overlap, the lower-priority edge's overlapped sub-range is recorded, in its own [0, length]
	// parametrization, into a cross_coplanar::edge_coverage_map_t -- ready for
	// cross_coplanar::split_edge_by_coverage() to trim.
	//
	// Deliberately NOT restricted to cross-product pairs (unlike compute_coincident_edge_best_priority's
	// exact-key sibling, whose own same-product restriction is still correct -- distinct-topology
	// exact duplicates only ever arise cross-product). Case B (mat_style_change::layer_boundary_
	// edges_for_face(), SvgSerializer.h) constructs brand-new loose edges clipped to their own
	// product's face outline, so a Case B edge's endpoint is *structurally* collinear with, and often
	// nested inside, part of that same product's own outline edge at that location -- not a rare
	// coincidence, but the normal shape of any exposed/unmatched layered end cap. Before this
	// mechanism covered the same-product case, whether that overlap was visible depended entirely on
	// SVG DOM emission order (whichever class happened to be emitted last painted over the other) --
	// confirmed as a real regression when Case B's own emission point moved later in the pipeline
	// (see the mat_style_change namespace's own comments), which flipped that accidental order and
	// made previously-invisible mat-style-change edges paint over their own product's outline.
	cross_coplanar::edge_coverage_map_t compute_coincident_edge_overlap_coverage(
		const std::list<std::tuple<const IfcUtil::IfcBaseEntity*, std::string, TopoDS_Shape>>& hlr_items,
		double tolerance
	) {
		struct entry {
			const IfcUtil::IfcBaseEntity* product;
			int priority;
			std::string cls;
			cross_coplanar::LineSeg seg;      // true 3D -- used only for `.edge`/real length rescaling
			cross_coplanar::LineSeg proj_seg; // screen-projected -- see project_to_view_plane()
		};
		std::vector<entry> entries;
		for (auto& item : hlr_items) {
			const IfcUtil::IfcBaseEntity* product = std::get<0>(item);
			const std::string& cls = std::get<1>(item);
			const TopoDS_Shape& shape = std::get<2>(item);
			if (shape.IsNull()) {
				continue;
			}
			int prio = coincident_edge_class_priority(cls);
			for (TopExp_Explorer eexp(shape, TopAbs_EDGE); eexp.More(); eexp.Next()) {
				const TopoDS_Edge& e = TopoDS::Edge(eexp.Current());
				auto seg = edge_to_line_seg_from_vertices(e);
				if (!seg) {
					continue; // curved edge -- ineligible for this pass, falls back to exact-key only
				}
				gp_Pnt pp0 = project_to_view_plane(seg->p0);
				gp_Pnt pp1 = project_to_view_plane(seg->p1);
				if (pp0.Distance(pp1) < Precision::Confusion()) {
					continue; // edge-on to the camera -- projects to a point, no screen-space line to dedup
				}
				gp_Vec pv(pp0, pp1);
				cross_coplanar::LineSeg proj_seg{ pp0, pp1, gp_Dir(pv), pv.Magnitude(), e };
				entries.push_back({ product, prio, cls, *seg, proj_seg });
			}
		}

		// Bucket by quantized direction ONLY (not also by a quantized foot-point, as an earlier
		// version of this pass tried) -- a two-level quantized key is fragile exactly where it
		// matters most: two independently-computed collinear edges from different products can
		// differ enough in the 6th-7th decimal digit (the same floating-point noise seen
		// throughout this codebase's cross-product matching) to land their foot points in
		// *adjacent*, not identical, hash cells, silently skipping a genuine nested-duplicate
		// pair -- confirmed as the actual cause of a real miss during development. Direction
		// quantization alone is a much looser, safer prefilter (kLineBucketAngularTolerance is
		// already deliberately looser than the position tolerance); the actual collinearity test
		// below uses the true (non-quantized) perpendicular-distance computation, so no precision
		// is lost -- only the O(n^2) prefilter grouping is coarser, trading a larger per-bucket
		// pairwise cost for correctness. Bucketed by the PROJECTED direction -- see
		// project_to_view_plane()'s own comment for why screen space, not true 3D, is what matters
		// for this pass.
		const double dir_scale = 1.0 / kLineBucketAngularTolerance;

		std::unordered_map<quant_pnt, std::vector<size_t>, quant_pnt_hash> buckets;
		buckets.reserve(entries.size());
		for (size_t i = 0; i < entries.size(); ++i) {
			quant_pnt dkey = quantize_direction(entries[i].proj_seg.dir, dir_scale);
			buckets[dkey].push_back(i);
		}

		cross_coplanar::edge_coverage_map_t coverage;
		auto record = [&](const TopoDS_Edge& e, double lo, double hi) {
			auto* existing = coverage.ChangeSeek(e);
			if (existing) {
				existing->push_back({ lo, hi });
			} else {
				coverage.Bind(e, { { lo, hi } });
			}
		};

		// First pass: which `entries` indices are an `outline` edge that genuinely, collinearly
		// overlaps a `cross-coplanar` edge somewhere in its own bucket -- i.e. confirmed to be
		// part of a Case-A cross-product match group, not merely an isolated Case-B same-product
		// nesting (Case B never produces a cross-coplanar collision at all, only mat-style-change,
		// see the mat_style_change namespace's own comment). Used below to gate the
		// mat-style-change-vs-outline exception onto exactly the shape this HLR-duplicate-fragment
		// artifact actually takes (issue #3742 follow-up, "Shifted in space"/"Extrusion L2 diff
		// mat" cases): the SAME outline edge splitting across adjacent sub-ranges into one
		// cross-coplanar match and one mat-style-change match, from the same or a neighbouring
		// product -- without this gate, the exception also fired for genuine Case B nesting in
		// unrelated products (confirmed as a real regression during development: "Extrusion L2
		// same mat", which has no cross-coplanar story at all at that edge, picked up spurious
		// extra mat-style-change/outline duplicates).
		std::unordered_set<size_t> outline_confirms_case_a;
		for (auto& kv : buckets) {
			auto& idxs = kv.second;
			for (size_t a = 0; a < idxs.size(); ++a) {
				for (size_t b = a + 1; b < idxs.size(); ++b) {
					const entry& ei = entries[idxs[a]];
					const entry& ej = entries[idxs[b]];
					bool pair_is_cc_outline =
						(ei.cls == cross_coplanar::class_name && ej.cls == "outline") ||
						(ej.cls == cross_coplanar::class_name && ei.cls == "outline");
					if (!pair_is_cc_outline) {
						continue;
					}
					if (std::abs(ei.proj_seg.dir.Dot(ej.proj_seg.dir)) <= 1.0 - cross_coplanar::kCoplanarNormalTolerance) {
						continue;
					}
					gp_Vec to_other(ei.proj_seg.p0, ej.proj_seg.p0);
					double perp_dist = to_other.Crossed(gp_Vec(ei.proj_seg.dir)).Magnitude();
					if (perp_dist >= tolerance) {
						continue;
					}
					double t0 = gp_Vec(ei.proj_seg.p0, ej.proj_seg.p0).Dot(gp_Vec(ei.proj_seg.dir));
					double t1 = gp_Vec(ei.proj_seg.p0, ej.proj_seg.p1).Dot(gp_Vec(ei.proj_seg.dir));
					bool has_overlap_i = (std::min(std::max(t0, t1), ei.proj_seg.length) - std::max(std::min(t0, t1), 0.0)) >= tolerance;
					double u0 = gp_Vec(ej.proj_seg.p0, ei.proj_seg.p0).Dot(gp_Vec(ej.proj_seg.dir));
					double u1 = gp_Vec(ej.proj_seg.p0, ei.proj_seg.p1).Dot(gp_Vec(ej.proj_seg.dir));
					bool has_overlap_j = (std::min(std::max(u0, u1), ej.proj_seg.length) - std::max(std::min(u0, u1), 0.0)) >= tolerance;
					if (!has_overlap_i && !has_overlap_j) {
						continue;
					}
					if (ei.cls == "outline") {
						outline_confirms_case_a.insert(idxs[a]);
					}
					if (ej.cls == "outline") {
						outline_confirms_case_a.insert(idxs[b]);
					}
				}
			}
		}

		for (auto& kv : buckets) {
			auto& idxs = kv.second;
			for (size_t a = 0; a < idxs.size(); ++a) {
				for (size_t b = a + 1; b < idxs.size(); ++b) {
					const entry& ei = entries[idxs[a]];
					const entry& ej = entries[idxs[b]];
					if (ei.priority == ej.priority) continue;  // intentional agreement -- leave alone

					// Collinearity/perp-distance test in PROJECTED (screen) space -- two edges at
					// genuinely different depths/3D directions can still paint on top of each
					// other once flattened by the camera; that's the visual duplicate this pass
					// exists to resolve, not true 3D coincidence (see project_to_view_plane()).
					if (std::abs(ei.proj_seg.dir.Dot(ej.proj_seg.dir)) <= 1.0 - cross_coplanar::kCoplanarNormalTolerance) {
						continue;
					}
					gp_Vec to_other(ei.proj_seg.p0, ej.proj_seg.p0);
					double perp_dist = to_other.Crossed(gp_Vec(ei.proj_seg.dir)).Magnitude();
					if (perp_dist >= tolerance) {
						continue;
					}

					// Overlap fraction in ei's own PROJECTED frame, then rescaled onto ei's real
					// 3D edge length -- parallel/orthographic projection preserves a segment's
					// [0,1] parametrization (see project_to_view_plane()), so a fraction computed
					// in screen space maps directly onto the corresponding real-3D sub-range for
					// clipping the original, unprojected edge.
					double t0 = gp_Vec(ei.proj_seg.p0, ej.proj_seg.p0).Dot(gp_Vec(ei.proj_seg.dir));
					double t1 = gp_Vec(ei.proj_seg.p0, ej.proj_seg.p1).Dot(gp_Vec(ei.proj_seg.dir));
					double lo_i_proj = std::max(std::min(t0, t1), 0.0);
					double hi_i_proj = std::min(std::max(t0, t1), ei.proj_seg.length);
					bool has_i_overlap = (hi_i_proj - lo_i_proj) >= tolerance;
					double real_scale_i = ei.seg.length / ei.proj_seg.length;
					double lo_i = lo_i_proj * real_scale_i;
					double hi_i = hi_i_proj * real_scale_i;

					// Overlap in ej's own PROJECTED frame (independently -- must not reuse ei's t-values).
					double u0 = gp_Vec(ej.proj_seg.p0, ei.proj_seg.p0).Dot(gp_Vec(ej.proj_seg.dir));
					double u1 = gp_Vec(ej.proj_seg.p0, ei.proj_seg.p1).Dot(gp_Vec(ej.proj_seg.dir));
					double lo_j_proj = std::max(std::min(u0, u1), 0.0);
					double hi_j_proj = std::min(std::max(u0, u1), ej.proj_seg.length);
					bool has_j_overlap = (hi_j_proj - lo_j_proj) >= tolerance;
					double real_scale_j = ej.seg.length / ej.proj_seg.length;
					double lo_j = lo_j_proj * real_scale_j;
					double hi_j = hi_j_proj * real_scale_j;

					if (!has_i_overlap && !has_j_overlap) {
						continue; // touching at a shared vertex only, not a genuine overlap range
					}

					// cross-coplanar-vs-outline exception: HLR output edges carry no usable depth
					// (they're genuinely flattened, Z==0, by the time they reach this pass --
					// confirmed via direct instrumentation, not just unpopulated), so this dedup can
					// only ever arbitrate by class priority, never by "which one is actually
					// nearer". The general "outline always wins" rule has a confirmed cross-product
					// justification for `mat-style-change` (a case where it wrongly painted over the
					// true outline of the object actually visible from this camera) -- but no
					// equivalent case justifies it for `cross-coplanar`, and issue #3742 follow-up
					// (NORTH SECTION TILT "Extrusion L2" cases) found the opposite: a product's own
					// interior corner edge (a real, different-Y line, correctly classified `outline`)
					// coincidentally screen-aligned, under the oblique TILT camera, with either that
					// SAME product's or its matched NEIGHBOUR's already-verified, full-length
					// cross-coplanar corner match, silently clipping it in both the same-product and
					// cross-product form of the collision. A `cross-coplanar` edge is the result of
					// an explicit, already-verified touching-boundary decision (two genuinely
					// coincident, camera-facing winning faces, see resolve_edge_location_subrange())
					// -- strictly more informed than a same-line-in-screen-space-only `outline`
					// classification, so it wins this collision unconditionally.
					bool cross_coplanar_vs_outline =
						(ei.cls == cross_coplanar::class_name && ej.cls == "outline") ||
						(ej.cls == cross_coplanar::class_name && ei.cls == "outline");

					// mat-style-change-vs-outline exception: unlike cross-coplanar's, this is NOT
					// unconditional -- Case B's own same-product nesting (a layer-boundary edge
					// genuinely nested inside part of a much longer outline edge, see
					// layer_boundary_edges_for_face()'s comment) relies on outline continuing to
					// win in exactly this function, and the general "outline always wins" rule has
					// its own confirmed cross-product justification for mat-style-change (a case
					// where it wrongly painted over the true outline of the object actually visible
					// from this camera). Gated on `outline_confirms_case_a` (computed above): the
					// SAME outline entry must ALSO have a confirmed, genuinely-collinear overlap
					// with a `cross-coplanar` edge somewhere -- the one signal that reliably tells
					// this HLR-duplicate-fragment artifact (issue #3742 follow-up, "Shifted in
					// space"/"Extrusion L2 diff mat" cases: the same outline duplicate splitting
					// into adjacent cross-coplanar- and mat-style-change-matching sub-ranges) apart
					// from genuine Case B nesting, since Case B never produces a cross-coplanar
					// collision at all (see mat_style_change namespace's own comment) -- confirmed
					// necessary during development: an earlier, ungated version of this exception
					// also fired for "Extrusion L2 same mat"'s own genuine Case B edge, which has no
					// cross-coplanar story at that location, adding spurious duplicates there.
					bool mat_style_change_vs_outline_case_a =
						(ei.cls == mat_style_change::class_name && ej.cls == "outline" && outline_confirms_case_a.count(idxs[b])) ||
						(ej.cls == mat_style_change::class_name && ei.cls == "outline" && outline_confirms_case_a.count(idxs[a]));

					bool i_wins = cross_coplanar_vs_outline
						? (ei.cls == cross_coplanar::class_name)
						: mat_style_change_vs_outline_case_a
						? (ei.cls == mat_style_change::class_name)
						: (ei.priority <= ej.priority);

					if (!i_wins) {
						if (has_i_overlap) {
							record(ei.seg.edge, lo_i, hi_i); // ei loses
						}
					} else {
						if (has_j_overlap) {
							record(ej.seg.edge, lo_j, hi_j); // ej loses
						}
					}
				}
			}
		}
		return coverage;
	}
}

void SvgSerializer::draw_hlr(const gp_Pln& pln, const drawing_key& drawing_name) {
	hlr_t& hlr_source = drawing_name.first ? this->storey_hlr.find(drawing_name.first)->second : *hlr;
	auto hlr_items = hlr_source.build();

	auto [coincident_best_priority, outline_loses_exact_key] =
		compute_coincident_edge_best_priority(hlr_items, svg_cross_coplanar_tolerance_);
	auto coincident_overlap_coverage = compute_coincident_edge_overlap_coverage(hlr_items, svg_cross_coplanar_tolerance_);

	// SVG edge classification (issue #3668): each item's class is already known -- it was
	// determined pre-HLR from real face topology (see the classified_edge_buckets block in
	// write(const geometry_data&)) and threaded through via hlr_calc::extract(). No post-hoc
	// lookup against HLR's own (face-less) output is needed. Multiple items can share the same
	// product (one per non-empty class bucket); keep a single path_object/group per product so
	// per-path classes survive Bonsai's merge_linework_and_add_metadata untouched, rather than
	// creating a <g> per class (see plan notes on why that clobbers classes in Python).
	std::map<const IfcUtil::IfcBaseEntity*, path_object*> group_by_product;

	for (auto& item : hlr_items) {
		const IfcUtil::IfcBaseEntity* product = std::get<0>(item);
		const std::string& cls = std::get<1>(item);
		const TopoDS_Shape& hlr_compound_full = std::get<2>(item);

		if (hlr_compound_full.IsNull()) {
			continue;
		}

		// Drop any edge whose coincident-duplicate bucket (computed above, in the same
		// pre-mirror coordinate space) genuinely mixes classes across products AND this edge's
		// own class is strictly worse than the best one present -- e.g. a `sharp` edge dropped
		// in favour of another product's coincident `outline`. An edge at the *same* (tied)
		// best priority as another product's coincident edge is always kept (never arbitrarily
		// picks between equally-good duplicates), and a bucket where every product agrees on the
		// same class (e.g. both sides `cross-coplanar`) has no entry in coincident_best_priority
		// at all, so nothing here is ever touched for those -- see
		// compute_coincident_edge_best_priority()'s own comment for why that's intentional.
		TopoDS_Compound hlr_compound_filtered;
		BRep_Builder dedup_builder;
		dedup_builder.MakeCompound(hlr_compound_filtered);
		{
			const double scale = 1.0 / svg_cross_coplanar_tolerance_;
			const int this_priority = coincident_edge_class_priority(cls);
			for (TopExp_Explorer eexp(hlr_compound_full, TopAbs_EDGE); eexp.More(); eexp.Next()) {
				const TopoDS_Edge& e = TopoDS::Edge(eexp.Current());
				TopoDS_Vertex v0, v1;
				TopExp::Vertices(e, v0, v1);
				bool keep = true;
				if (!v0.IsNull() && !v1.IsNull()) {
					auto key = make_edge_key(
						project_to_view_plane(BRep_Tool::Pnt(v0)),
						project_to_view_plane(BRep_Tool::Pnt(v1)),
						scale);
					// `outline` unconditionally loses an exact-key collision against
					// `cross-coplanar`/`mat-style-change` (see compute_coincident_edge_best_priority()'s
					// own comment) -- checked before the generic priority comparison, since outline's
					// own priority number (0, the global minimum) can never be "worse than the best" by
					// that comparison alone.
					if (cls == "outline" && outline_loses_exact_key.count(key)) {
						keep = false;
					} else {
						auto it = coincident_best_priority.find(key);
						if (it != coincident_best_priority.end() && this_priority > it->second) {
							keep = false;
						}
					}
				}
				if (!keep) {
					continue; // exact-duplicate fast path: dropped entirely
				}

				// Collinear-overlap pass (nested/sub-range duplicates the exact-key pass above
				// can't see -- see compute_coincident_edge_overlap_coverage()'s own comment).
				// Edges absent from this map (the overwhelming majority) fall straight through to
				// the unchanged-original path below, byte-identical to before this pass existed.
				auto* raw_overlap = coincident_overlap_coverage.ChangeSeek(e);
				if (!raw_overlap) {
					dedup_builder.Add(hlr_compound_filtered, e);
					continue;
				}
				auto seg = edge_to_line_seg_from_vertices(e);
				if (!seg) {
					// Shouldn't happen -- compute_coincident_edge_overlap_coverage() only ever
					// records entries for edges it already built a LineSeg for -- but never
					// crash or silently drop.
					dedup_builder.Add(hlr_compound_filtered, e);
					continue;
				}
				auto split = cross_coplanar::split_edge_by_coverage(e, *seg, *raw_overlap, svg_cross_coplanar_tolerance_);
				for (auto& r : split.remainder) {
					dedup_builder.Add(hlr_compound_filtered, r);
				}
				// split.covered (the overlapped-by-better-priority portion) is deliberately
				// discarded -- it's simply a wrong-priority duplicate of another product's edge,
				// not something to feed into a second class bucket.
			}
		}
		const TopoDS_Shape& hlr_compound_unmirrored = hlr_compound_filtered;

		if (TopExp_Explorer(hlr_compound_unmirrored, TopAbs_EDGE).More() == Standard_False) {
			continue;
		}

		// Compound 3D curves for mirroring to work
		ShapeFix_Edge sfe;
		TopExp_Explorer exp(hlr_compound_unmirrored, TopAbs_EDGE);
		for (; exp.More(); exp.Next()) {
			sfe.FixAddCurve3d(TopoDS::Edge(exp.Current()));
		}

		// Mirror to match SVG coord system.
		// @todo this is very wasteful. We better do the Y-mirror in the SVG writing and
		// not on the TopoDS_Shape input.

		TopoDS_Shape hlr_compound;
		if (drawing_name.first == nullptr) {
			gp_Trsf trsf_mirror;
			if (!mirror_y_) {
				trsf_mirror.SetMirror(gp_Ax2(gp::Origin(), gp::DY()));
			}
			if (mirror_x_) {
				gp_Trsf mirror_x;
				mirror_x.SetMirror(gp_Ax2(gp::Origin(), gp::DX()));
				trsf_mirror.PreMultiply(mirror_x);
			}
			BRepBuilderAPI_Transform make_transform_mirror(hlr_compound_unmirrored, trsf_mirror, true);
			make_transform_mirror.Build();
			hlr_compound = make_transform_mirror.Shape();
		} else {
			// In case of building storey-based floor plan the mirroring has already
			// been taken into account before projection.
			hlr_compound = hlr_compound_unmirrored;
		}

		path_object*& po = group_by_product[product];
		if (!po) {
			std::string name;
			if (product) {
				name = nameElement(product);
				boost::replace_all(name, "class=\"", "class=\"projection ");
			} else {
				name = "class=\"projection\"";
			}
			if (drawing_name.first) {
				po = &start_path(pln, drawing_name.first, name);
			} else {
				po = &start_path(pln, drawing_name.second, name);
			}
		}

		boost::optional<std::string> css_class;
		if (!cls.empty()) {
			css_class = cls;
		}

		BRep_Builder B;
		for (TopExp_Explorer exp_mirrored(hlr_compound, TopAbs_EDGE); exp_mirrored.More(); exp_mirrored.Next()) {
			TopoDS_Wire w;
			B.MakeWire(w);
			B.Add(w, exp_mirrored.Current());
			write(*po, w, boost::none, css_class);
		}
	}
}

void SvgSerializer::resetScale() {
	// reset the bounding box, as a subsequent drawing (elevation, section) will be centered, but use the same scale.
	// this is a separate call now as we first need to read drawing extents for automatically positioning sections and
	// elevations
	xmin = +std::numeric_limits<double>::infinity();
	ymin = +std::numeric_limits<double>::infinity();
	xmax = -std::numeric_limits<double>::infinity();
	ymax = -std::numeric_limits<double>::infinity();
}

void SvgSerializer::addTextAnnotations(const drawing_key& k) {
	auto& meta = drawing_metadata[k];

	boost::optional<std::pair<double, double>> range;

	if (k.first && section_data_) {
		for (auto& sd : *section_data_) {
			if (sd.which() == 0) {
				const auto& plan = boost::get<horizontal_plan>(sd);
				if (k.first == plan.storey) {
					range = std::make_pair(plan.elevation, plan.next_elevation);
				}
			}
		}
	}

	aggregate_of_instance::ptr annotations;
	if (file) {
		annotations = file->instances_by_type("IfcAnnotation");
	}
	if (annotations) {
		for (auto& ann_ : *annotations) {
			auto ann = (IfcUtil::IfcBaseEntity*) ann_;

			auto ot = ann->get("ObjectType");
			auto nm = ann->get("Name");
			auto ds = ann->get("Description");
			auto pl = ann->get("ObjectPlacement");

			if (!ot.isNull() && !nm.isNull() && !ds.isNull() && !pl.isNull()) {
				auto object_type = (std::string) ot;
				auto name = (std::string) nm;
				auto desc = (std::string) ds;

				if (object_type == "Text") {
					auto mapping = ifcopenshell::geometry::impl::mapping_implementations().construct(file, geometry_settings_, logger_);
					auto item = mapping->map(pl);
					auto matrix = ifcopenshell::geometry::taxonomy::cast<ifcopenshell::geometry::taxonomy::matrix4>(item);
					delete mapping;
					if (item) {
						gp_Trsf trsf;
						auto& m = matrix->ccomponents();
						trsf.SetValues(
							m(0, 0), m(0, 1), m(0, 2), m(0, 3),
							m(1, 0), m(1, 1), m(1, 2), m(1, 3),
							m(2, 0), m(2, 1), m(2, 2), m(2, 3)
						);
#ifdef TAXONOMY_USE_NAKED_PTR
						delete matrix;
#endif

						auto v = gp_Pnt(trsf.TranslationPart());

						auto z_local = gp::DZ().Transformed(trsf);
						auto view_dir = z_local.Dot(meta.pln_3d.Axis().Direction());

						if ((!range || (v.Z() >= range->first && v.Z() < range->second)) && view_dir > 0.99) {

							gp_Trsf trsf_view;
							trsf_view.SetTransformation(gp::XOY(), meta.pln_3d.Position());
							v.Transform(trsf_view);

							auto svg_name = nameElement(ann);

							if (object_type.size()) {
								// postfix the object_type for CSS matching
								boost::replace_all(svg_name, "class=\"IfcAnnotation\"", "class=\"IfcAnnotation " + object_type + "\"");
							}

							path_object* po;
							if (k.first) {
								po = &start_path(meta.pln_3d, k.first, svg_name);
							} else {
								po = &start_path(meta.pln_3d, k.second, svg_name);
							}							

							boost::optional<double> font_size;
							std::vector<std::string> tokens;
							boost::split(tokens, name, boost::is_any_of("_"));
							if (tokens.size() == 2) {
								try {
									font_size = boost::lexical_cast<double>(tokens.back());
								}
								catch (...) {}
							}

							// @todo column or row?
							double z_rotation = gp::DX().Transformed(trsf).AngleWithRef(
								meta.pln_3d.Position().XDirection(),
								meta.pln_3d.Position().Direction()									
							);
							z_rotation *= 180. / M_PI;

							auto y = -v.Y();

							util::string_buffer path;
							// dominant-baseline="central" is not well supported in IE.
							// so we add a 0.35 offset to the dy of the tspans
							path.add("            <text text-anchor=\"left\" x=\"");
							xcoords.push_back(path.add(v.X()));
							path.add("\" y=\"");
							ycoords.push_back(path.add(y));

							path.add("\" transform=\"rotate(");
							path.add(z_rotation);
							path.add(" ");
							xcoords.push_back(path.add(v.X()));
							path.add(" ");
							ycoords.push_back(path.add(y));
							path.add(")\"");

							if (font_size) {
								path.add(" font-size=\"");
								path.add(*font_size);
								path.add("\"");
							}
							path.add(">");

							std::vector<std::string> labels{ desc };

							for (auto lit = labels.begin(); lit != labels.end(); ++lit) {
								auto l = *lit;
								IfcUtil::escape_xml(l);
								double dy = labels.begin() == lit
									? 0.0  // align bottom
									: 1.0; // <- dy is relative to the previous text element, so
											//    always 1 for successive spans.
								path.add("<tspan x=\"");
								xcoords.push_back(path.add(v.X()));
								path.add("\" dy=\"");
								path.add(boost::lexical_cast<std::string>(dy));
								path.add("em\">");
								path.add(l);
								path.add("</tspan>");
							}

							path.add("</text>");

							po->second.push_back(path);
						}
					}
				}
			}
		}
	}
}

void SvgSerializer::finalize() {
	doWriteHeader();

	for (auto& p : drawing_metadata) {
		addTextAnnotations(p.first);
	}

	for (auto& p : storey_hlr) {
		draw_hlr(drawing_metadata[{p.first, ""}].pln_3d, { p.first, "" });
	}

	auto m = resize();

	// Update the paper space scale matrices
	for (auto& p : paths) {
		drawing_metadata[p.first].matrix_3 = m;
	}

	if (!deferred_section_data_.is_initialized() && (auto_section_ || auto_elevation_)) {
		deferred_section_data_.emplace();
	}

	// @nb keep in mind Y-axis is negated in these 6 definitions to account
	// for coordinate system differences.
	if (auto_section_) {
		{
			gp_Pln pln(gp_Ax3(
				gp_Pnt((xmin + xmax) / 2., (ymin + ymax) / 2., 0.),
				gp_Dir(-1, 0, 0),
				gp_Dir(0, -1, 0)));
			deferred_section_data_->push_back(vertical_section{ pln , "Section North South", true });
		}
		{
			gp_Pln pln(gp_Ax3(
				gp_Pnt((xmin + xmax) / 2., (ymin + ymax) / -2., 0.),
				gp_Dir(0, -1, 0),
				gp_Dir(1, 0, 0)));
			deferred_section_data_->push_back(vertical_section{ pln , "Section East West", true });
		}
	}

	if (auto_elevation_) {
		{
			gp_Pln pln(gp_Ax3(
				gp_Pnt(0., -(ymin - 0.1), 0.),
				gp_Dir(0, 1, 0),
				gp_Dir(-1, 0, 0)));
			deferred_section_data_->push_back(vertical_section{ pln , "Elevation South", true });
		}
		{
			gp_Pln pln(gp_Ax3(
				gp_Pnt(xmax + 0.1, 0., 0.),
				gp_Dir(1, 0, 0),
				gp_Dir(0, 1, 0)));
			deferred_section_data_->push_back(vertical_section{ pln , "Elevation East", true });
		}
		{
			gp_Pln pln(gp_Ax3(
				gp_Pnt(0., -(ymax + 0.1), 0.),
				gp_Dir(0, -1, 0),
				gp_Dir(1, 0, 0)));
			deferred_section_data_->push_back(vertical_section{ pln , "Elevation North", true });
		}
		{
			gp_Pln pln(gp_Ax3(
				gp_Pnt(xmin - 0.1, 0., 0.),
				gp_Dir(-1, 0, 0),
				gp_Dir(0, -1, 0)));
			deferred_section_data_->push_back(vertical_section{ pln , "Elevation West", true });
		}
	}

	resetScale();
	
	if (deferred_section_data_ && deferred_section_data_->size() && element_buffer_.size()) {

		// Draw door arcs only on floor plans.
		is_floor_plan_ = false;

		for (auto& sd : *deferred_section_data_) {
			bool use_hlr = true;
			const gp_Pln* pln = nullptr;
			std::string drawing_name;
			if (sd.which() == 2) {
				const auto& section = boost::get<vertical_section>(sd);
				use_hlr = section.with_projection;
				drawing_name = section.name;
				pln = &section.plane;
			}

			// @todo do we have always have pln here?
			if (use_hlr && pln) {
				hlr = new hlr_t(logger_, use_prefiltering_, use_hlr_poly_, segment_projection_, *pln,
					svg_use_edge_classification_, svg_use_cross_coplanar_classification_, svg_cross_coplanar_tolerance_,
					svg_render_cross_coplanar_edges_, svg_use_mat_style_change_classification_);
			}

			section_data_ = std::vector<section_data>{ sd };
			for (auto& e : element_buffer_) {
				write(e);
			}

			if (use_hlr) {
				const auto& section = boost::get<vertical_section>(sd);
				const auto& ax = section.plane.Position();
				
				draw_hlr(ax, { nullptr, drawing_name });
			}

			addTextAnnotations({ nullptr, drawing_name });

			if (file && storey_height_display_ != SH_NONE && pln && std::abs(pln->Position().Direction().Z()) < 1.e-5) {
				auto storeys = file->instances_by_type("IfcBuildingStorey");
				if (storeys) {
					const double lu = file->getUnit("LENGTHUNIT").second;
					for (auto& s : *storeys) {
						auto storey = (IfcUtil::IfcBaseEntity*) s;
						auto a = storey->get("Elevation");
						if (!a.isNull()) {
							double elev = a;
							elev *= lu;
							auto svg_name = nameElement(storey);

							gp_Pln elev_pln(gp_Ax3(gp_Pnt(0, 0, elev), gp::DZ(), gp::DX()));
							//, pln->Position().XDirection()));
							// auto ref_y = pln->Position().YDirection().XYZ().Dot(pln->Position().Location().XYZ());

							double x0, y0, z0, x1, y1, z1;
							bnd_.Get(x0, y0, z0, x1, y1, z1);

							// @todo this is a hack in order to get the auto elevations (which are 0.1 offset from
							// the global bounding box) to include the storey height symbols.
							x0 -= 0.2;
							y0 -= 0.2;
							z0 -= 0.2;

							x1 += 0.2;
							y1 += 0.2;
							z1 += 0.2;

							const double shll = storey_height_line_length_.get_value_or(2.);

							BRepBuilderAPI_MakeFace mf(elev_pln, x0 - shll, x1 + shll, y0 - shll, y1 + shll);
							gp_Trsf trsf;
							TopoDS_Compound C;
							BRep_Builder B;
							B.MakeCompound(C);
							B.Add(C, mf.Face());
							std::string name;
							auto a2 = storey->get("Name");
							if (!a2.isNull()) {
								name = (std::string) a2;
							}
							write(geometry_data{
								C,{boost::none},trsf,storey,storey,elev,name,nameElement(storey),nullptr,nullptr,boost::none
							});
						}
					}
				}
			}

			auto m3 = resize();

			auto k = std::make_pair(nullptr, drawing_name);
			drawing_metadata[k].matrix_3 = m3;

			resetScale();

			delete hlr;
		}
	}

	std::multimap<drawing_key, path_object, storey_sorter>::const_iterator it;

	boost::optional<drawing_key> previous;
	for (it = paths.begin(); it != paths.end(); ++it) {
		if (!previous || it->first != *previous) {
			if (previous) {
				svg_file.stream << "    </g>\n";
			}
			std::ostringstream oss;
			if (it->first.first) {
				svg_file.stream << "    <g " << nameElement(it->first.first) << " " << writeMetadata(drawing_metadata[it->first]) << ">\n";
			} else {
				auto n = it->first.second;
				IfcUtil::escape_xml(n);
				svg_file.stream << "    <g " << namespace_prefix_  << "name=\"" << n << "\" class=\"section\" " << writeMetadata(drawing_metadata[it->first]) << ">\n";
			}
		}

		previous = it->first;

		if (it->second.second.empty()) {
			continue;
		}

		svg_file.stream << "        <g " << it->second.first << ">\n";
		std::vector<util::string_buffer>::const_iterator jt;
		for (jt = it->second.second.begin(); jt != it->second.second.end(); ++jt) {
			svg_file.stream << jt->str();
		}
		svg_file.stream << "        </g>\n";
	}
	
	if (previous) {
		svg_file.stream << "    </g>\n";
	}
	svg_file.stream << "</svg>" << std::endl;
}

void SvgSerializer::writeHeader() {
	// This doesn't do anything anymore because there is now the option that an
	// IfcAnnotation[ObjectType=DRAWING] defines the SVG viewBox and dimensions
}

void SvgSerializer::doWriteHeader() {
	svg_file.stream << "<svg xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\"";
	if (use_namespace_) {
		svg_file.stream << " xmlns:ifc=\"http://www.ifcopenshell.org/ns\"";
	}
	if (scale_ && size_) {
		svg_file.stream << 
			" width=\"" << size_->first << "mm\""
			" height=\"" << size_->second << "mm\"" <<
			" viewBox=\"0 0 " << size_->first << " " << size_->second << "\"";
	}
		
	svg_file.stream << ">\n"
		"    <defs>\n"
		"        <marker id=\"arrowend\" markerWidth=\"10\" markerHeight=\"7\" refX=\"10\" refY=\"3.5\" orient=\"auto\">\n"
		"          <polygon points=\"0 0, 10 3.5, 0 7\" />\n"
		"        </marker>\n"
		"        <marker id=\"arrowstart\" markerWidth=\"10\" markerHeight=\"7\" refX=\"0\" refY=\"3.5\" orient=\"auto\">\n"
		"          <polygon points=\"10 0, 0 3.5, 10 7\" />\n"
		"        </marker>\n"
		"    </defs>\n";

	if (!no_css_) {
		svg_file.stream <<
			"    <style type=\"text/css\" >\n"
			"    <![CDATA[\n"
			"        .cut path {\n"
			"            stroke: #222222;\n"
			"            fill: #444444;\n"
			"            fill-rule: evenodd;\n"
			"        }\n"
			"        .projection path {\n"
			"            stroke: #222222;\n"
			"            fill: none;\n"
			"            stroke-opacity: 0.6;\n"
			"        }\n"
			// SVG edge classification (issue #3668) -- see edge-classification.md. These
			// select directly on the <path> element (each classified edge carries its own
			// class), not on an ancestor <g>, so they win over the inherited .projection
			// path rule above regardless of specificity.
			"        path.outline {\n"
			"            stroke: #000000;\n"
			"            stroke-width: 0.35px;\n"
			"            stroke-opacity: 1;\n"
			"        }\n"
			"        path.boundary {\n"
			"            stroke: #000000;\n"
			"            stroke-width: 0.3px;\n"
			"            stroke-opacity: 0.9;\n"
			"        }\n"
			"        path.sharp {\n"
			"            stroke: #000000;\n"
			"            stroke-width: 0.25px;\n"
			"            stroke-opacity: 0.85;\n"
			"        }\n"
			"        path.crease {\n"
			"            stroke: #000000;\n"
			"            stroke-width: 0.18px;\n"
			"            stroke-opacity: 0.7;\n"
			"        }\n"
			"        path.flush {\n"
			"            stroke: #000000;\n"
			"            stroke-width: 0.1px;\n"
			"            stroke-opacity: 0.4;\n"
			"        }\n"
			"        .IfcDoor path,\n"
			"        .Symbol path {\n"
			"            fill: none;\n"
			"        }\n"
			"        .Symbol path {\n"
			"            stroke-width: 0.5px;\n"
			"        }\n"
			"        .IfcSpace path {\n"
			"            fill-opacity: .2;\n"
			"        }\n"
			"        .Dimension path {\n"
			"            marker-end: url(#arrowend);\n"
			"            marker-start: url(#arrowstart);\n"
			"        }\n";

		if (scale_) {
			// previously:
			//       (pt)  (px)  (in)  (mm)
			// approx 12 / 0.75 / 96 * 25.4

			svg_file.stream <<
				"        text {\n"
				"            font-size: 2;\n" //  (reduced to two).
				"        }\n"
				"        path {\n"
				"            stroke-width: 0.3;\n"
				"        }\n";
		}

		svg_file.stream <<
			"    ]]>\n"
			"    </style>\n";
	}
}

namespace {
	std::string nameElement_(const std::vector<std::pair<std::string, std::string> >& attrs) {
		std::ostringstream oss;
for (auto& a : attrs) {
	// @todo while we're at it might as well implement escaping
	oss << a.first << "=\"" << a.second << "\" ";
}
return oss.str();
	}
}

std::string SvgSerializer::nameElement(const IfcUtil::IfcBaseEntity* storey, const IfcGeom::Element* elem) {
	auto n = elem->name();
	IfcUtil::escape_xml(n);

	return nameElement_({
		{"id", with_section_heights_from_storey_ ? object_id(storey, elem) : GeometrySerializer::object_id(elem)},
		{"class", elem->type()},
		{namespace_prefix_ + "name", n},
		{namespace_prefix_ + "guid", elem->guid()}
		});
}

std::string SvgSerializer::idElement(const IfcUtil::IfcBaseEntity* elem) {
	const std::string type = elem->declaration().is("IfcBuildingStorey") ? "storey" : "product";
	const std::string name =
		(settings().get<ifcopenshell::geometry::settings::UseElementGuids>().get()
			? static_cast<std::string>(elem->get("GlobalId"))
			: ((settings().get<ifcopenshell::geometry::settings::UseElementNames>().get() && !elem->get("Name").isNull()))
			? static_cast<std::string>(elem->get("Name"))
			: (settings().get<ifcopenshell::geometry::settings::UseElementStepIds>().get())
			? ("id-" + boost::lexical_cast<std::string>(elem->id()))
			: IfcParse::IfcGlobalId(elem->get("GlobalId")).formatted());
	return type + "-" + name;
}

std::string SvgSerializer::nameElement(const IfcUtil::IfcBaseEntity* elem) {
	if (elem == 0) { return ""; }

	const std::string& entity = elem->declaration().name();
	std::string ifc_name;
	if (!elem->get("Name").isNull()) {
		ifc_name = (std::string) elem->get("Name");
		IfcUtil::escape_xml(ifc_name);
	}

	return nameElement_({
		{"id", idElement(elem)},
		{"class", entity},
		{namespace_prefix_ + "name", ifc_name},
		{namespace_prefix_ + "guid", elem->get("GlobalId")}
		});
}

void SvgSerializer::setFile(IfcParse::IfcFile* f) {
	file = f;

	auto storeys = f->instances_by_type("IfcBuildingStorey");
	if (!storeys || storeys->size() == 0) {
		auto mapping = ifcopenshell::geometry::impl::mapping_implementations().construct(file, geometry_settings_, logger_);

		std::vector<const IfcParse::declaration*> to_derive_from;
		to_derive_from.push_back(f->schema()->declaration_by_name("IfcBuilding"));
		to_derive_from.push_back(f->schema()->declaration_by_name("IfcSite"));
		for (auto it = to_derive_from.begin(); it != to_derive_from.end(); ++it) {
			aggregate_of_instance::ptr insts = f->instances_by_type(*it);
			if (insts) {
				for (auto jt = insts->begin(); jt != insts->end(); ++jt) {
					IfcUtil::IfcBaseEntity* product = (IfcUtil::IfcBaseEntity*) *jt;
					if (!product->get("ObjectPlacement").isNull()) {
						auto item = mapping->map(product->get("ObjectPlacement"));
						auto matrix = ifcopenshell::geometry::taxonomy::cast<ifcopenshell::geometry::taxonomy::matrix4>(item);
						gp_Trsf trsf;
						if (matrix) {
							// @todo shouldn't this take into account configurable section height?
							setSectionHeight(matrix->translation_part()(2) + 1.);
#ifdef TAXONOMY_USE_NAKED_PTR
							delete matrix;
#endif
							logger_.Warning("SER", 30, "No building storeys encountered, used for reference:", product);
							return;
						}
					}
				}
			}
		}

		delete mapping;

		logger_.Warning("SER", 31, "No building storeys encountered, output might be invalid or missing");
	}
}

void SvgSerializer::setSectionHeight(double h, const IfcUtil::IfcBaseEntity* storey) {
	section_data_.emplace();
	section_data_->push_back(horizontal_plan{ storey, h, 0., std::numeric_limits<double>::infinity() });
}

void SvgSerializer::setSectionHeightsFromStoreys(double offset) {
	if (!file) {
		logger_.Error("SER", 32, "No file specified");
		return;
	}
	with_section_heights_from_storey_ = true;
	section_data_.emplace();
	auto storeys = file->instances_by_type("IfcBuildingStorey");
	const double lu = file->getUnit("LENGTHUNIT").second;
	if (storeys && storeys->size() > 0) {
		for (auto& s : *storeys) {
			auto attr_value = ((IfcUtil::IfcBaseEntity*)s)->get("Elevation");
			if (!attr_value.isNull()) {
				double elev;
				try {
					elev = attr_value;
				} catch (std::exception& e) {
					logger_.Error("SER", 33, e);
					continue;
				}
				if (!section_data_->empty()) {
					boost::get<horizontal_plan>(section_data_->back()).next_elevation = elev * lu;
				}
				section_data_->push_back(horizontal_plan{ (IfcUtil::IfcBaseEntity*)s, elev * lu, offset, std::numeric_limits<double>::infinity() });
			}			
		}
	} else {
		section_data_->push_back(horizontal_plan_at_element{});
	}
}

namespace {
	std::string array_to_string(double v) {
		return std::to_string(v);
	}

	template <typename T>
	std::string array_to_string(const T& v) {
		return "[" + std::accumulate(
			v.begin() + 1, v.end(), 
			array_to_string(v.front()),
			[](const std::string& accum, decltype(*v.cbegin())& item) {
				return accum + "," + array_to_string(item);
		}) + "]";
	}
}

std::string SvgSerializer::writeMetadata(const drawing_meta& m) {
	gp_Trsf trsf;
	trsf.SetTransformation(m.pln_3d.Position(), gp::XOY());
	NCollection_Mat4<double> mat4;
	trsf.GetMat4(mat4);
	const auto* d = mat4.GetData();
	std::array<std::array<double, 4>, 4> m4 = { {
	   {{ d[0], d[4], d[8], d[12] }},
	   {{ d[1], d[5], d[9], d[13] }},
	   {{ d[2], d[6], d[10], d[14] }},
	   {{ d[3], d[7], d[11], d[15] }}
	} };
	return namespace_prefix_ + "plane=\""+ array_to_string(m4) +"\" " +
		namespace_prefix_ + "matrix3=\"" + array_to_string(m.matrix_3) + "\"";
}

#endif
