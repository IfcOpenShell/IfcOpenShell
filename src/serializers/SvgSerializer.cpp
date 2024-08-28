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

#include <gp_Pln.hxx>
#include <gp_Trsf.hxx>
#include <gp_Circ.hxx>
#include <gp_Elips.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Edge.hxx>
#include <TopExp_Explorer.hxx>
#include <BRep_Tool.hxx>
#include <BRepTools.hxx>
#include <BRepAlgoAPI_Section.hxx>
#include <ShapeAnalysis_FreeBounds.hxx>
#include <TopTools_HSequenceOfShape.hxx>
#include <TopExp.hxx>

#include <BRepAdaptor_Curve.hxx>
#include <GCPnts_QuasiUniformDeflection.hxx>

#include <Geom_Curve.hxx>
#include <Geom_Line.hxx>
#include <Geom_Plane.hxx>
#include <Geom_Circle.hxx>
#include <Geom_Ellipse.hxx>
#include <gp_Ax22d.hxx>
#include <Standard_Version.hxx>
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
	return true;
}

void SvgSerializer::write(path_object& p, const TopoDS_Shape& comp_or_wire, boost::optional<std::vector<double>> dash_array) {
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
				Handle_Geom_Surface surf;

				BRep_Tool::CurveOnSurface(edge, curve2d, surf, loc, u1, u2);

				if (curve2d.IsNull()) {
					Logger::Error("Failed to obtain 2d and 3d curve from edge");
					continue;
				}

				Handle(Standard_Type) sty = surf->DynamicType();
				if (sty != STANDARD_TYPE(Geom_Plane)) {
					Logger::Error("Non-planar p-curves are not supported by this serializer");
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
					Logger::Warning(ss.str());
				}
			}

			const bool reversed = edge.Orientation() == TopAbs_REVERSED;

			gp_Pnt p1, p2;
			curve->D0(u1, p1);
			curve->D0(u2, p2);

			if (reversed) {
				std::swap(p1, p2);
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
						auto value = v->data().get_attribute_value(0);
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
		compound_local = IfcGeom::util::unify(compound_local, 1.e-6);
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

	geometry_data data{ compound_local, dash_arrays, trsf, brep_obj->product(), storey, elev, brep_obj->name(), nameElement(storey, brep_obj) };

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

void SvgSerializer::write(const geometry_data& data) {
	std::vector<section_data> section_heights_storage;
	const std::vector<section_data>* section_heights_used = &section_heights_storage;

	if (section_data_) {
		section_heights_used = section_data_.get_ptr();
	} else {
		if (data.storey) {
			section_heights_storage.push_back(horizontal_plan{ data.storey, data.storey_elevation,  +1. });
		} else {
			Logger::Warning("No global section height and unable to determine building storey for:", data.product);
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
			Logger::Notice("Not including element due to viewBox", data.product);
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
			Logger::Error(e);
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
								auto part = BRepAlgoAPI_Cut(it.Value(), s).Shape();
								BB.Add(C, part);
							}

							subtracted_shape = C;

							compound_to_hlr = &subtracted_shape;
						} catch (...) {
							Logger::Error("Failed to cut element for HLR", data.product);
						}
					}
				}

				TopoDS_Compound profile_edges;
				if (profile_threshold_ != -1 && !(data.product->declaration().is("IfcWall") || data.product->declaration().is("IfcSlab"))) {
					TopTools_IndexedDataMapOfShapeListOfShape map;
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

				if (is_floor_plan_) {
					if (storey) {
						auto it = storey_hlr.find(storey);
						if (it == storey_hlr.end()) {
							it = storey_hlr.insert({ storey, hlr_t(use_prefiltering_, use_hlr_poly_, segment_projection_, projection_plane) }).first;
						}
						it->second.add(*compound_to_hlr, data.product);
					} else {
						Logger::Warning("Unable to invoke HLR due to absence of storey containment", data.product);
					}
				} else if (hlr) {
					hlr->add(*compound_to_hlr, data.product);
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

			TopoDS_Shape result = BRepAlgoAPI_Section(subshape, pln);

			if (variant.which() == 2) {
				gp_Trsf trsf;
				trsf.SetTransformation(gp::XOY(), pln.Position());
				result.Move(trsf);

				BRepBuilderAPI_Transform make_transform_mirror_(result, trsf_mirror, true);
				make_transform_mirror_.Build();
				result = make_transform_mirror_.Shape();
			}

			Handle(TopTools_HSequenceOfShape) edges = new TopTools_HSequenceOfShape();
			Handle(TopTools_HSequenceOfShape) wires = new TopTools_HSequenceOfShape();
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
		Logger::Warning("Element not written to SVG due to section heights", data.product);
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

void SvgSerializer::draw_hlr(const gp_Pln& pln, const drawing_key& drawing_name) {
	auto hlr_items = (drawing_name.first ? this->storey_hlr.find(drawing_name.first)->second : *hlr).build();

	for (auto& p : hlr_items) {
		const TopoDS_Shape& hlr_compound_unmirrored = p.second;

		if (!hlr_compound_unmirrored.IsNull()) {
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

			exp.Init(hlr_compound, TopAbs_EDGE);
			BRep_Builder B;
			path_object* po;
			std::string name;
			if (p.first) {
				name = nameElement(p.first);
				boost::replace_all(name, "class=\"", "class=\"projection ");
			} else {
				name = "class=\"projection\"";
			}
			if (drawing_name.first) {
				po = &start_path(pln, drawing_name.first, name);
			} else {
				po = &start_path(pln, drawing_name.second, name);
			}
			for (; exp.More(); exp.Next()) {
				TopoDS_Wire w;
				B.MakeWire(w);
				B.Add(w, exp.Current());
				write(*po, w);
			}

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
					auto mapping = ifcopenshell::geometry::impl::mapping_implementations().construct(file, geometry_settings_);
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
				hlr = new hlr_t(use_prefiltering_, use_hlr_poly_, segment_projection_, *pln);
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
								C,{boost::none},trsf,storey,storey,elev,name,nameElement(storey)
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
		auto mapping = ifcopenshell::geometry::impl::mapping_implementations().construct(file, geometry_settings_);

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
							Logger::Warning("No building storeys encountered, used for reference:", product);
							return;
						}
					}
				}
			}
		}

		delete mapping;

		Logger::Warning("No building storeys encountered, output might be invalid or missing");
	}
}

void SvgSerializer::setSectionHeight(double h, const IfcUtil::IfcBaseEntity* storey) {
	section_data_.emplace();
	section_data_->push_back(horizontal_plan{ storey, h, 0., std::numeric_limits<double>::infinity() });
}

void SvgSerializer::setSectionHeightsFromStoreys(double offset) {
	if (!file) {
		Logger::Error("No file specified");
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
					Logger::Error(e);
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
	// @todo
	std::array<std::array<double, 4>, 4> m4 = {{
		{{ 1, 0, 0, 0 }},
		{{ 0, 1, 0, 0 }},
		{{ 0, 0, 1, 0 }},
		{{ 0, 0, 0, 1 }}
	}};
	return namespace_prefix_ + "plane=\""+ array_to_string(m4) +"\" " +
		namespace_prefix_ + "matrix3=\"" + array_to_string(m.matrix_3) + "\"";
}

#endif
