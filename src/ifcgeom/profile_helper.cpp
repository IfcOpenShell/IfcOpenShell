#include "profile_helper.h"

using namespace ifcopenshell::geometry;

taxonomy::loop* ifcopenshell::geometry::fillet_loop(taxonomy::loop* loop, double radius) {
	std::vector<profile_point_with_edges_3d> pps(loop->children.size());
	for (int b = 0; b < loop->children.size(); ++b) {
		int c = (b - 1) % loop->children.size();
		pps[b] = { 
			boost::get<taxonomy::point3>(((taxonomy::edge*)loop->children[c])->start).ccomponents(), 
			radius, (taxonomy::edge*) loop->children[c], (taxonomy::edge*) loop->children[b]
		};
	}
	size_t i = pps.size();
	while (i--) {
		const auto& p = pps[i];
		if (p.radius && *p.radius > 0.) {

			auto p0 = boost::get<taxonomy::point3>(p.previous->start).ccomponents();
			auto p1a = boost::get<taxonomy::point3>(p.previous->end).ccomponents();
			auto p2 = boost::get<taxonomy::point3>(p.next->end).ccomponents();
			auto p1b = boost::get<taxonomy::point3>(p.next->start).ccomponents();

			auto ba_ = p0 - p1a;
			auto bc_ = p2 - p1b;

			auto ba = ba_.normalized();
			auto bc = bc_.normalized();

			const double angle = std::acos(ba.dot(bc));
			const double inset = *p.radius / std::tan(angle / 2.);

			boost::get<taxonomy::point3>(p.previous->end).components() += ba * inset;
			boost::get<taxonomy::point3>(p.next->start).components() += bc * inset;

			auto e = new taxonomy::edge;
			e->start = p.previous->end;
			e->end = p.next->start;

			// @todo untested from here.

			auto ab = ba.cross(bc);

			auto O = boost::get<taxonomy::point3>(p.previous->end).ccomponents().head<3>() + ab * *p.radius;

			auto c = new taxonomy::circle;
			c->matrix = taxonomy::matrix4(O, ab);
			c->radius = *p.radius;
			e->basis = c;

			loop->children.insert(std::find(loop->children.begin(), loop->children.end(), p.next), e);
		}
	};
	return loop;
}

taxonomy::loop* ifcopenshell::geometry::polygon_from_points(const std::vector<taxonomy::point3>& ps, bool external) {
	auto loop = new taxonomy::loop();
	loop->external = external;
	boost::optional<taxonomy::point3> previous;
	for (auto& p : ps) {
		if (previous) {
			auto e = new taxonomy::edge;
			e->start = *previous;
			e->end = p;
			loop->children.push_back(e);
		}
		previous = p;
	}
	return loop;
}

taxonomy::loop* ifcopenshell::geometry::profile_helper(const taxonomy::matrix4& m4, const std::vector<profile_point>& points) {

	/* TopoDS_Vertex* vertices = new TopoDS_Vertex[numVerts];
	for (int i = 0; i < numVerts; i++) {
		gp_XY xy(verts[2 * i], verts[2 * i + 1]);
		trsf.Transforms(xy);
		vertices[i] = BRepBuilderAPI_MakeVertex(gp_Pnt(xy.X(), xy.Y(), 0.0f));
	}
	BRepBuilderAPI_MakeWire w;
	for (int i = 0; i < numVerts; i++)
		w.Add(BRepBuilderAPI_MakeEdge(vertices[i], vertices[(i + 1) % numVerts]));
	TopoDS_Face face;
	convert_wire_to_face(w.Wire(), face);
	if (numFillets && *std::max_element(filletRadii, filletRadii + numFillets) > ALMOST_ZERO) {
		BRepFilletAPI_MakeFillet2d fillet(face);
		for (int i = 0; i < numFillets; i++) {
			const double radius = filletRadii[i];
			if (radius <= ALMOST_ZERO) continue;
			fillet.AddFillet(vertices[filletIndices[i]], radius);
		}
		fillet.Build();
		if (fillet.IsDone()) {
			face = TopoDS::Face(fillet.Shape());
		} else {
			Logger::Error("Failed to process profile fillets");
		}
	}
	*/

	const bool has_position = !m4.is_identity();

	// @todo precision

	std::vector<taxonomy::point3> ps;
	ps.reserve(points.size() + 1);
	std::transform(points.begin(), points.end(), std::back_inserter(ps), [&has_position, &m4](const profile_point& p) {
		if (has_position) {
			Eigen::Vector4d v(p.xy[0], p.xy[1], 0., 1.);
			v = m4.ccomponents() * v;
			return taxonomy::point3(v(0), v(1), 0.);
		} else {
			return taxonomy::point3(p.xy[0], p.xy[1], 0.);
		}
	});
	ps.push_back(ps.front());

	auto loop = polygon_from_points(ps);

	std::vector<profile_point_with_edges> pps(points.size());
	for (int b = 0; b < points.size(); ++b) {
		int c = (b - 1) % points.size();
		pps[b] = { Eigen::Vector2d(points[b].xy[0], points[b].xy[1]), points[b].radius, (taxonomy::edge*) loop->children[c], (taxonomy::edge*) loop->children[b] };
	}

	size_t i = pps.size();
	while (i--) {
		const auto& p = pps[i];
		if (p.radius && *p.radius > 0.) {
			// Position is a IfcAxis2Placement2D, so should remain 2d points
			auto p0 = boost::get<taxonomy::point3>(p.previous->start).components_->head<2>();
			auto p1a = boost::get<taxonomy::point3>(p.previous->end).components_->head<2>();
			auto p2 = boost::get<taxonomy::point3>(p.next->end).components_->head<2>();
			auto p1b = boost::get<taxonomy::point3>(p.next->start).components_->head<2>();

			auto ba_ = p0 - p1a;
			auto bc_ = p2 - p1b;

			auto ba = ba_.normalized();
			auto bc = bc_.normalized();

			const double angle = std::acos(ba.dot(bc));
			const double inset = *p.radius / std::tan(angle / 2.);

			boost::get<taxonomy::point3>(p.previous->end).components_->head<2>() += ba * inset;
			boost::get<taxonomy::point3>(p.next->start).components_->head<2>() += bc * inset;

			auto e = new taxonomy::edge;
			e->start = p.previous->end;
			e->end = p.next->start;

			auto ab = Eigen::Vector3d(-ba(1), +ba(0), 0.);

			double sign = ab.head<2>().dot(bc) > 0 ? 1. : -1.;

			auto O = boost::get<taxonomy::point3>(p.previous->end).ccomponents().head<3>() + ab * *p.radius * sign;

			auto c = new taxonomy::circle;
			c->matrix = Eigen::Matrix4d(Eigen::Affine3d(Eigen::Translation3d(O)).matrix());
			c->radius = *p.radius;
			e->basis = c;
			c->orientation.reset(sign == -1.);

			loop->children.insert(std::find(loop->children.begin(), loop->children.end(), p.next), e);
		}
	};

	return loop;
}
