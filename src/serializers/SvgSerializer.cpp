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

#include <string>
#include <fstream>
#include <cstdio>
#include <limits>
#include <algorithm>

#include <gp_Pln.hxx>
#include <gp_Trsf.hxx>
#include <gp_Circ.hxx>
#include <gp_Elips.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Edge.hxx>
#include <TopExp_Explorer.hxx>
#include <BRep_Tool.hxx>
#include <BRepAlgo_Section.hxx>
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

#include <BRepBuilderAPI_MakeFace.hxx>
#include <GProp_GProps.hxx>
#include <BRepGProp.hxx>
#include <BRepTopAdaptor_FClass2d.hxx>

#include <Bnd_Box.hxx>
#include <BRep_Builder.hxx>
#include <BRepBndLib.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>

#include <ShapeFix_Edge.hxx>

#include "../ifcparse/IfcGlobalId.h"

#include "SvgSerializer.h"

const double PI2 = M_PI * 2.;

bool SvgSerializer::ready() {
	return true;
}

void SvgSerializer::write(path_object& p, const TopoDS_Wire& wire) {
	/* ShapeFix_Wire fix;
	Handle(ShapeExtend_WireData) data = new ShapeExtend_WireData;
	for (TopExp_Explorer edges(result, TopAbs_EDGE); edges.More(); edges.Next()) {
		data->Add(edges.Current());
	}
	fix.Load(data);
	fix.FixReorder();
	fix.FixConnected();
	const TopoDS_Wire fixed_wire = fix.Wire(); */

	bool first = true;
	util::string_buffer path;
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

        if (conical && closed) {
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
            path.add("            <path d=\"");
			path.add("M");
			addXCoordinate(path.add(p1.X()));
			path.add(",");
			addYCoordinate(path.add(p1.Y()));

			growBoundingBox(p1.X(), p1.Y());
		}

		growBoundingBox(p2.X(), p2.Y());


		if (ty == STANDARD_TYPE(Geom_Circle) || ty == STANDARD_TYPE(Geom_Ellipse)) {
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
			const double ang = d2.Angle(gp::DX2d());

			// Write radii
			path.add(" A");
			addSizeComponent(path.add(r1));
			path.add(",");
			addSizeComponent(path.add(r2));
					
			// Write X-axis rotation
			{ std::stringstream ss; ss << " " << ang << " ";
			path.add(ss.str()); }
					
			// Write large-arc-flag and sweep-flag
			path.add(std::string(1, '0'+static_cast<int>(larger_arc_segment)));
			path.add(",");
			path.add(std::string(1, '0'+static_cast<int>(positive_direction)));
					
			path.add(" ");

			// Write arc end point
			xcoords.push_back(path.add(p2.X()));
			path.add(",");
			ycoords.push_back(path.add(p2.Y()));
		} else if (ty != STANDARD_TYPE(Geom_Line)) {
			BRepAdaptor_Curve crv(edge);
			GCPnts_QuasiUniformDeflection tessellater(crv, settings().deflection_tolerance());
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

	path.add("\"/>\n");
	p.second.push_back(path);
}

SvgSerializer::path_object& SvgSerializer::start_path(IfcUtil::IfcBaseEntity* storey, const std::string& id) {
	auto key = std::make_pair(std::make_pair(storey, ""), path_object());
	SvgSerializer::path_object& p = paths.insert(key)->second;
	p.first = id;
	return p;
}

SvgSerializer::path_object& SvgSerializer::start_path(const std::string& drawing_name, const std::string& id) {
	auto key = std::make_pair(std::make_pair(nullptr, drawing_name), path_object());
	SvgSerializer::path_object& p = paths.insert(key)->second;
	p.first = id;
	return p;
}

namespace {
	boost::optional<std::pair<IfcUtil::IfcBaseEntity*, double>> storey_elevation_from_element(const IfcGeom::BRepElement<real_t>* o) {
		for (const auto& p : o->parents()) {
			if (p->type() == "IfcBuildingStorey") {
				try {
					const IfcGeom::ElementSettings& settings = o->geometry().settings();
					double e = *p->product()->get("Elevation");
					double storey_elevation = e * settings.unit_magnitude();
					return std::make_pair(p->product(), storey_elevation);
				} catch (...) {
					continue;
				}
				break;
			}
		}
		return boost::none;
	}

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
}

void SvgSerializer::write(const IfcGeom::BRepElement<real_t>* brep_obj) {

	boost::optional<std::string> object_type;
	if (!brep_obj->product()->get("ObjectType")->isNull()) {
		object_type = static_cast<std::string>(*brep_obj->product()->get("ObjectType"));
	}

	TopoDS_Shape compound_local = brep_obj->geometry().as_compound();
	const gp_Trsf& trsf = brep_obj->transformation().data();

	const bool is_section = (section_ref_ && object_type && *section_ref_ == *object_type);
	const bool is_elevation = (elevation_ref_ && object_type && *elevation_ref_ == *object_type);

	if (is_section || is_elevation) {
		BRepBuilderAPI_Transform make_transform_global(compound_local, trsf, true);
		make_transform_global.Build();
		// (When determinant < 0, copy is implied and the input is not mutated.)
		auto compound_unmirrored = make_transform_global.Shape();

		auto e = edge_from_compound(compound_unmirrored);
		if (e) {
			TopoDS_Edge global_edge = TopoDS::Edge(e->Moved(trsf));
			double u0, u1;
			auto crv = BRep_Tool::Curve(global_edge, u0, u1);
			if (crv->DynamicType() == STANDARD_TYPE(Geom_Line)) {
				gp_Pnt P;
				gp_Vec V;
				crv->D1((u0 + u1) / 2., P, V);
				auto N = V.Crossed(gp::DZ());
				gp_Pln pln(gp_Ax3(P, N, V));
				if (!deferred_section_data_) {
					deferred_section_data_.emplace();
				}
				std::string name = brep_obj->name();
				if (name.empty()) {
					name = boost::lexical_cast<std::string>(brep_obj->id());
				}
				if (is_section) {
					deferred_section_data_->push_back(vertical_section{ pln , "Section " + name, false });
				}
				if (is_elevation) {
					deferred_section_data_->push_back(vertical_section{ pln , "Elevation " + name, true });
				}
			}
		}
		return;
	}

	auto p = storey_elevation_from_element(brep_obj);
	IfcUtil::IfcBaseEntity* storey = p ? p->first : nullptr;
	double elev = p ? p->second : std::numeric_limits<double>::quiet_NaN();
	geometry_data data{ compound_local, trsf, brep_obj->product(), storey, elev, brep_obj->name(), nameElement(storey, brep_obj) };

	if (buffer_elements_) {
		element_buffer_.push_back(data);
	}

	write(data);
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

	// SVG has a coordinate system with the origin in the *upper*-left corner
	// therefore we mirror the shape along the XZ-plane.	
	gp_Trsf trsf_mirror;
	trsf_mirror.SetMirror(gp_Ax2(gp::Origin(), gp::DY()));
	BRepBuilderAPI_Transform make_transform_mirror(compound_unmirrored, trsf_mirror, true);
	make_transform_mirror.Build();
	// (When determinant < 0, copy is implied and the input is not mutated.)
	auto compound = make_transform_mirror.Shape();

	TopoDS_Wire annotation;

	if (is_floor_plan_ && draw_door_arcs_ && data.product->declaration().is("IfcDoor")) {

		boost::optional<std::string> operation_type;

		try {
			IfcEntityList::ptr rels;
			if (data.product->declaration().schema()->name() == "IFC2X3") {
				rels = data.product->get_inverse("IsDefinedBy");
			} else {
				// Damn you, IFC
				rels = data.product->get_inverse("IsTypedBy");
			}
			for (auto& rel : *rels) {
				if (rel->declaration().name() == "IfcRelDefinesByType") {
					IfcUtil::IfcBaseClass* ty = *((IfcUtil::IfcBaseEntity*)rel)->get("RelatingType");
					const std::string& ty_entity_name = ty->declaration().name();
					// Damn you, IFC
					if (ty_entity_name == "IfcDoorStyle" || ty_entity_name == "IfcDoorType") {
						operation_type = *((IfcUtil::IfcBaseEntity*)ty)->get("OperationType");
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

		IfcUtil::IfcBaseEntity* storey = nullptr;
		std::string drawing_name;

		bool use_hlr = false;

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
		} else if (variant.which() == 1) {
			projection_direction = gp::DZ();
		} else if (variant.which() == 2) {
			const auto& section = boost::get<vertical_section>(variant);
			projection_direction = section.plane.Axis().Direction();
			drawing_name = section.name;
			use_hlr = section.with_projection;
		}

		auto& compound_to_use = is_floor_plan_ ? compound : compound_unmirrored;

		if (use_hlr && hlr) {
			hlr->Add(compound_to_use);
		}

		TopoDS_Iterator it(compound_to_use);

		TopoDS_Face largest_closed_wire_face;
		double largest_closed_wire_area = 0.;
		path_object* po = nullptr;

		// Iterate over components of compound to have better chance of matching section edges to closed wires
		for (; it.More(); it.Next()) {

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

			if (data.product->declaration().is("IfcAnnotation") && (proj.Magnitude() > 1.e-5) && zmin >= range.first && zmin <= range.second) {
				if (po == nullptr) {
					if (storey) {
						po = &start_path(storey, data.svg_name);
					} else {
						po = &start_path(drawing_name, data.svg_name);
					}
				}

				TopExp_Explorer exp(subshape, TopAbs_EDGE, TopAbs_FACE);
				for (; exp.More(); exp.Next()) {
					const auto& e = TopoDS::Edge(exp.Current());
					TopoDS_Vertex v0, v1;
					TopExp::Vertices(e, v0, v1);
					gp_Pnt p0 = BRep_Tool::Pnt(v0);
					gp_Pnt p1 = BRep_Tool::Pnt(v1);
					// @todo should we take the average parameter value instead?
					gp_XYZ center = (p0.XYZ() + p1.XYZ()) / 2.;
					BRep_Builder B;
					TopoDS_Wire W;
					B.MakeWire(W);
					B.Add(W, e);
					write(*po, W);




					util::string_buffer path;
					// dominant-baseline="central" is not well supported in IE.
					// so we add a 0.35 offset to the dy of the tspans
					path.add("            <text class=\"IfcAnnotation\" text-anchor=\"middle\" x=\"");
					xcoords.push_back(path.add(center.X()));
					path.add("\" y=\"");
					ycoords.push_back(path.add(center.Y()));
					path.add("\">");
					std::vector<std::string> labels{};

					GProp_GProps prop;
					BRepGProp::LinearProperties(e, prop);
					const double area = prop.Mass();
					std::stringstream ss;
					ss << std::setprecision(2) << std::fixed << std::showpoint << area;
					labels.push_back(ss.str() + "m");

					for (auto lit = labels.begin(); lit != labels.end(); ++lit) {
						const auto& l = *lit;
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
					po->second.push_back(path);
				}
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

			if (po == nullptr) {
				if (storey) {
					po = &start_path(storey, data.svg_name);
				} else {
					po = &start_path(drawing_name, data.svg_name);
				}
			}

			// Create a horizontal cross section 1 meter above the bottom point of the shape		
			gp_Pln pln;
			if (variant.which() < 2) {
				pln = gp_Pln(gp_Pnt(0, 0, cut_z), gp::DZ());
			} else {
				const auto& section = boost::get<vertical_section>(variant);
				pln = section.plane;
			}
			TopoDS_Shape result = BRepAlgoAPI_Section(subshape, pln);

			if (variant.which() == 2) {
				gp_Trsf trsf;
				trsf.SetTransformation(gp::XOY(), pln.Position());
				result.Move(trsf);

				gp_Trsf trsf_mirror;
				trsf_mirror.SetMirror(gp_Ax2(gp::Origin(), gp::DY()));
				BRepBuilderAPI_Transform make_transform_mirror(result, trsf_mirror, true);
				make_transform_mirror.Build();
				result = make_transform_mirror.Shape();
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

			for (int i = 1; i <= wires->Length(); ++i) {
				const TopoDS_Wire& wire = TopoDS::Wire(wires->Value(i));
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
				write(*po, wire);
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
					// the distance is not simply euclidian, but we
					// favour the x-component;
					const double d = std::sqrt(
						10 * ((pa.X() - pb.X()) * (pa.X() - pb.X())) +
						1 * ((pa.Y() - pb.Y()) * (pa.Y() - pb.Y()))
					);
					if (d > furthest_points_distance) {
						gp_Pnt p3d((pa.XYZ() + pb.XYZ()) / 2.);
						gp_Pnt2d p2d(p3d.X(), p3d.Y());

						if (fcls.Perform(p2d) == TopAbs_IN) {
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
					if (!attr->isNull()) {
						std::string long_name = *attr;
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
				path.add("\">");
				for (auto lit = labels.begin(); lit != labels.end(); ++lit) {
					const auto& l = *lit;
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
				po->second.push_back(path);
			}
		}

		if (po && !annotation.IsNull()) {
			write(*po, annotation);
		}
	}

	if (!emitted) {
		Logger::Warning("Element not written to SVG due to section heights", data.product);
	}
}

void SvgSerializer::setBoundingRectangle(double width, double height) {
	this->width = width;
	this->height = height;
	this->rescale = true;
}

void SvgSerializer::resize() {
	if (rescale) {
		// Scale the resulting image to a bounding rectangle specified by command line arguments
		const double dx = xmax - xmin;
		const double dy = ymax - ymin;

		double sc, cx, cy;
		if (scale_) {
			sc = (*scale_) * 1000;
			cx = (xmax + xmin) / 2. * sc - width * center_x_.get_value_or(0.5);
			cy = (ymax + ymin) / 2. * sc - height * center_y_.get_value_or(0.5);
		} else {
			if (calculated_scale_) {
				sc = *calculated_scale_;
			} else {
				if (dx / width > dy / height) {
					sc = width / dx;
				} else {
					sc = height / dy;
				}
				calculated_scale_ = sc;
			}
			cx = xmin * sc;
			cy = ymin * sc;
		}

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

	// reset the bounding box, as a subsequent drawing (elevation, section) will be centered, but use the same scale.
	xmin = +std::numeric_limits<double>::infinity();
	ymin = +std::numeric_limits<double>::infinity();
	xmax = -std::numeric_limits<double>::infinity();
	ymax = -std::numeric_limits<double>::infinity();
}

void SvgSerializer::finalize() {
	resize();

	if (deferred_section_data_ && deferred_section_data_->size() && element_buffer_.size()) {

		// Draw door arcs only on floor plans.
		is_floor_plan_ = false;

		for (auto& sd : *deferred_section_data_) {
			bool use_hlr = false;
			std::string drawing_name;
			if (sd.which() == 2) {
				const auto& section = boost::get<vertical_section>(sd);
				use_hlr = section.with_projection;
				drawing_name = section.name;
			}

			if (use_hlr) {
				hlr = new HLRBRep_Algo;
			}

			*section_data_ = { sd };
			for (auto& e : element_buffer_) {
				write(e);
			}

			if (use_hlr) {
				const auto& section = boost::get<vertical_section>(sd);
				gp_Ax2 transform = section.plane.Position().Ax2();
				HLRAlgo_Projector projector(transform);
				hlr->Projector(projector);

				hlr->Update();
				hlr->Hide();

				HLRBRep_HLRToShape hlr_shapes(hlr);
				auto hlr_compound_unmirrored = hlr_shapes.VCompound();

				// Compound 3D curves for mirroring to work
				ShapeFix_Edge sfe;
				TopExp_Explorer exp(hlr_compound_unmirrored, TopAbs_EDGE);
				for (; exp.More(); exp.Next()) {
					sfe.FixAddCurve3d(TopoDS::Edge(exp.Current()));
				}

				// Mirror to match SVG coord system.
				// @todo this is very wasteful. We better do the Y-mirror in the SVG writing and
				// not on the TopoDS_Shape input.

				gp_Trsf trsf_mirror;
				trsf_mirror.SetMirror(gp_Ax2(gp::Origin(), gp::DY()));
				BRepBuilderAPI_Transform make_transform_mirror(hlr_compound_unmirrored, trsf_mirror, true);
				make_transform_mirror.Build();
				auto hlr_compound = make_transform_mirror.Shape();

				exp.Init(hlr_compound, TopAbs_EDGE);
				BRep_Builder B;
				auto& po = start_path(drawing_name, "class=\"projection\"");
				for (; exp.More(); exp.Next()) {
					TopoDS_Wire w;
					B.MakeWire(w);
					B.Add(w, exp.Current());					
					write(po, w);
				}				
			}

			resize();

			if (use_hlr) {
				hlr.Nullify();
			}
		}
	}

	std::multimap<drawing_key, path_object, storey_sorter>::const_iterator it;

	boost::optional<drawing_key> previous;
	for (it = paths.begin(); it != paths.end(); ++it) {
		if (!previous || it->first != *previous) {
			if (previous) {
				svg_file << "    </g>\n";
			}
			std::ostringstream oss;
			if (it->first.first) {
				svg_file << "    <g " << nameElement(it->first.first) << ">\n";
			} else {
				svg_file << "    <g data-name=\"" << it->first.second << "\" class=\"section\">\n";
			}
		}
		svg_file << "        <g " << it->second.first << ">\n";
		std::vector<util::string_buffer>::const_iterator jt;
		for (jt = it->second.second.begin(); jt != it->second.second.end(); ++jt) {
			svg_file << jt->str();
		}
		svg_file << "        </g>\n";
		previous = it->first;
	}
	
	if (previous) {
		svg_file << "    </g>\n";
	}
	svg_file << "</svg>" << std::endl;
}

void SvgSerializer::writeHeader() {
	svg_file << "<svg xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\"";
	if (scale_) {
		svg_file << 
			" width=\"" << width << "mm\""
			" height=\"" << height << "mm\"" << 
			" viewBox=\"0 0 " << width << " " << height << "\"";
	}
		
	svg_file << ">\n"
		"    <defs>\n"
		"        <marker id=\"arrowend\" markerWidth=\"10\" markerHeight=\"7\" refX=\"10\" refY=\"3.5\" orient=\"auto\">\n"
		"          <polygon points=\"0 0, 10 3.5, 0 7\" />\n"
		"        </marker>\n"
		"        <marker id=\"arrowstart\" markerWidth=\"10\" markerHeight=\"7\" refX=\"0\" refY=\"3.5\" orient=\"auto\">\n"
		"          <polygon points=\"10 0, 0 3.5, 10 7\" />\n"
		"        </marker>\n"
		"    </defs>\n"
		"    <style type=\"text/css\" >\n"
		"    <![CDATA[\n"
		"        path {\n"
		"            stroke: #222222;\n"
		"            fill: #444444;\n"
		"        }\n"
		"        .IfcDoor path {\n"
		"            fill: none;\n"
		"        }\n"
		"        .IfcSpace path {\n"
		"            fill-opacity: .2;\n"
		"        }\n"
		"        .IfcAnnotation path {\n"
		"            marker-end: url(#arrowend);\n"
		"            marker-start: url(#arrowstart);\n"
		"        }\n";
	
	if (scale_) {
		// previously:
		//       (pt)  (px)  (in)  (mm)
		// approx 12 / 0.75 / 96 * 25.4

		svg_file <<
		"        text {\n"
		"            font-size: 2;\n" //  (reduced to two).
		"        }\n"
		"        path {\n"
		"            stroke-width: 0.3;\n"
		"        }\n";
	}

	svg_file << 
		"    ]]>\n"
		"    </style>\n";
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

std::string SvgSerializer::nameElement(const IfcUtil::IfcBaseEntity* storey, const IfcGeom::Element<real_t>* elem) {
	return nameElement_({
		{"id", with_section_heights_from_storey_ ? object_id(storey, elem) : GeometrySerializer::object_id(elem)},
		{"class", elem->type()},
		{"data-name", elem->name()},
		{"data-guid", elem->guid()}
		});
}

std::string SvgSerializer::idElement(const IfcUtil::IfcBaseEntity* elem) {
	const std::string type = elem->declaration().is("IfcBuildingStorey") ? "storey" : "product";
	const std::string name =
		(settings().get(SerializerSettings::USE_ELEMENT_GUIDS)
			? static_cast<std::string>(*elem->get("GlobalId"))
			: ((settings().get(SerializerSettings::USE_ELEMENT_NAMES) && !elem->get("Name")->isNull()))
			? static_cast<std::string>(*elem->get("Name"))
			: (settings().get(SerializerSettings::USE_ELEMENT_STEPIDS))
			? ("id-" + boost::lexical_cast<std::string>(elem->data().id()))
			: IfcParse::IfcGlobalId(*elem->get("GlobalId")).formatted());
	return type + "-" + name;
}

std::string SvgSerializer::nameElement(const IfcUtil::IfcBaseEntity* elem) {
	if (elem == 0) { return ""; }

	const std::string& entity = elem->declaration().name();
	std::string ifc_name;
	if (!elem->get("Name")->isNull()) {
		ifc_name = (std::string) *elem->get("Name");
	}

	return nameElement_({
		{"id", idElement(elem)},
		{"class", entity},
		{"data-name", ifc_name},
		{"data-guid", *elem->get("GlobalId")}
		});
}

void SvgSerializer::setFile(IfcParse::IfcFile* f) {
	file = f;

	auto storeys = f->instances_by_type("IfcBuildingStorey");
	if (!storeys || storeys->size() == 0) {

		IfcGeom::Kernel kernel(f);

		std::vector<const IfcParse::declaration*> to_derive_from;
		to_derive_from.push_back(f->schema()->declaration_by_name("IfcBuilding"));
		to_derive_from.push_back(f->schema()->declaration_by_name("IfcSite"));
		for (auto it = to_derive_from.begin(); it != to_derive_from.end(); ++it) {
			IfcEntityList::ptr insts = f->instances_by_type(*it);
			if (insts) {
				for (auto jt = insts->begin(); jt != insts->end(); ++jt) {
					IfcUtil::IfcBaseEntity* product = (IfcUtil::IfcBaseEntity*) *jt;
					if (!product->get("ObjectPlacement")->isNull()) {
						gp_Trsf trsf;
						if (kernel.convert_placement(*product->get("ObjectPlacement"), trsf)) {
							setSectionHeight(trsf.TranslationPart().Z() + 1.);
							Logger::Warning("No building storeys encountered, used for reference:", product);
							return;
						}
					}
				}
			}
		}

		Logger::Warning("No building storeys encountered, output might be invalid or missing");
	}
}

void SvgSerializer::setSectionHeight(double h, IfcUtil::IfcBaseEntity* storey) {
	section_data_.emplace();
	section_data_->push_back(horizontal_plan{ storey, h, 0., std::numeric_limits<double>::infinity() });
}

void SvgSerializer::setSectionHeightsFromStoreys(double offset) {
	with_section_heights_from_storey_ = true;
	section_data_.emplace();
	auto storeys = file->instances_by_type("IfcBuildingStorey");
	const double lu = file->getUnit("LENGTHUNIT").second;
	if (storeys && storeys->size() > 0) {
		for (auto& s : *storeys) {
			auto attr_value = ((IfcUtil::IfcBaseEntity*)s)->get("Elevation");
			if (!attr_value->isNull()) {
				double elev;
				try {
					elev = *attr_value;
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
