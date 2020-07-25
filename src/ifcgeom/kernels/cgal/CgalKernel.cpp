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
#define _USE_MATH_DEFINES
#include <cmath>

#include "CgalKernel.h"

#include "../../../ifcparse/IfcLogger.h"
#include "../../../ifcgeom/kernels/cgal/CgalConversionResult.h"

#include <CGAL/minkowski_sum_3.h>

using namespace ifcopenshell::geometry; 
using namespace ifcopenshell::geometry::kernels;

void CgalKernel::remove_duplicate_points_from_loop(cgal_wire_t& polygon) {
	std::set<cgal_point_t> points;
	for (int i = 0; i < polygon.size(); ++i) {
		if (points.count(polygon[i])) {
			polygon.erase(polygon.begin() + i);
			--i;
		} else points.insert(polygon[i]);
	}
}

CGAL::Polyhedron_3<Kernel_> ifcopenshell::geometry::utils::create_polyhedron(std::list<cgal_face_t> &face_list) {

	// Naive creation
	CGAL::Polyhedron_3<Kernel_> polyhedron;
	PolyhedronBuilder builder(&face_list);
	polyhedron.delegate(builder);

	// Stitch edges
	//  std::cout << "Before: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
	CGAL::Polygon_mesh_processing::stitch_borders(polyhedron);
	if (!polyhedron.is_valid()) {
		Logger::Message(Logger::LOG_ERROR, "create_polyhedron: Polyhedron not valid!");
		//    std::ofstream fresult;
		//    fresult.open("/Users/ken/Desktop/invalid.off");
		//    fresult << polyhedron << std::endl;
		//    fresult.close();
		return CGAL::Polyhedron_3<Kernel_>();
	} if (polyhedron.is_closed()) {
		if (!CGAL::Polygon_mesh_processing::is_outward_oriented(polyhedron)) {
			CGAL::Polygon_mesh_processing::reverse_face_orientations(polyhedron);
		}
	}

	//  std::cout << "After: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;

	return polyhedron;
}

CGAL::Polyhedron_3<Kernel_> ifcopenshell::geometry::utils::create_polyhedron(const CGAL::Nef_polyhedron_3<Kernel_>& nef_polyhedron) {
	if (nef_polyhedron.is_simple()) {
		try {
			CGAL::Polyhedron_3<Kernel_> polyhedron;
			nef_polyhedron.convert_to_polyhedron(polyhedron);
			return polyhedron;
		} catch (...) {
			Logger::Message(Logger::LOG_ERROR, "Conversion from Nef to polyhedron failed!");
			return CGAL::Polyhedron_3<Kernel_>();
		}
	} else {
		Logger::Message(Logger::LOG_ERROR, "Nef polyhedron not simple: cannot create polyhedron!");
		return CGAL::Polyhedron_3<Kernel_>();
	}
}

CGAL::Nef_polyhedron_3<Kernel_> ifcopenshell::geometry::utils::create_nef_polyhedron(std::list<cgal_face_t> &face_list) {
	CGAL::Polyhedron_3<Kernel_> polyhedron = create_polyhedron(face_list);
	CGAL::Polygon_mesh_processing::triangulate_faces(polyhedron);
	CGAL::Nef_polyhedron_3<Kernel_> nef_polyhedron;
	try {
		nef_polyhedron = CGAL::Nef_polyhedron_3<Kernel_>(polyhedron);
	} catch (...) {
		Logger::Message(Logger::LOG_ERROR, "Conversion to Nef polyhedron failed!");
	}
	return nef_polyhedron;
}

CGAL::Nef_polyhedron_3<Kernel_> ifcopenshell::geometry::utils::create_nef_polyhedron(CGAL::Polyhedron_3<Kernel_> &polyhedron) {
	// @todo needed?
	polyhedron.normalize_border();
	if (polyhedron.is_valid(false, 3) && polyhedron.is_closed()) {
		// @todo is it necessary to triangulat?
		CGAL::Polygon_mesh_processing::triangulate_faces(polyhedron);
		CGAL::Nef_polyhedron_3<Kernel_> nef_polyhedron;
		try {
			nef_polyhedron = CGAL::Nef_polyhedron_3<Kernel_>(polyhedron);
		} catch (...) {
			Logger::Message(Logger::LOG_ERROR, "Conversion to Nef polyhedron failed!");
		}
		return nef_polyhedron;
	} else {
		Logger::Message(Logger::LOG_ERROR, "Polyhedron not valid: cannot create Nef polyhedron!");
		return CGAL::Nef_polyhedron_3<Kernel_>();
	}
}

bool CgalKernel::convert(const taxonomy::shell* l, cgal_shape_t& shape) {
	auto faces = l->children_as<taxonomy::face>();

	std::list<cgal_face_t> face_list;
	for (auto& f : faces) {
		bool success = false;
		cgal_face_t face;

		try {
			success = convert(f, face);
		} catch (...) {}

		if (!success) {
			Logger::Message(Logger::LOG_WARNING, "Failed to convert face:", f->instance);
			continue;
		}

		//    std::cout << "Face in ConnectedFaceSet: " << std::endl;
		//    for (auto &point: face.outer) {
		//      std::cout << "\tPoint(" << point << ")" << std::endl;
		//    }

		face_list.push_back(face);
	}

	shape = utils::create_polyhedron(face_list);
	return true;
}

bool CgalKernel::convert(const taxonomy::face* face, cgal_face_t& result) {
	auto bounds = face->children_as<taxonomy::loop>();

	int num_outer_bounds = 0;

	for (auto& bound : bounds) {
		if (bound->external.get_value_or(false)) num_outer_bounds++;
	}

	if (num_outer_bounds != 1) {
		Logger::Message(Logger::LOG_ERROR, "Invalid configuration of boundaries for:", face->instance);
		return false;
	}

	cgal_face_t mf;

	for (auto& bound : bounds) {

		const bool is_interior = !bound->external.get_value_or(false);

		cgal_wire_t wire;
		if (!convert(bound, wire)) {
			Logger::Message(Logger::LOG_ERROR, "Failed to process face boundary loop", bound->instance);
			return false;
		}

		if (!is_interior) {
			mf.outer = wire;
		} else {
			mf.inner.push_back(wire);
		}
	}

	result = mf;

	//  std::cout << "Face: " << std::endl;
	//  for (auto &point: face.outer) {
	//    std::cout << "\tPoint(" << point << ")" << std::endl;
	//  }

	return true;
}

namespace {
	// @todo obsolete?
	bool convert_curve(CgalKernel* kernel, const taxonomy::item* curve, cgal_wire_t& builder) {
		if (curve->kind() == taxonomy::EDGE) {
			auto e = (taxonomy::edge*) curve;
			if (true || e->basis == nullptr) {
				if (builder.empty()) {
					const auto& p = boost::get<taxonomy::point3>(e->start);
					cgal_point_t pnt((*p.components)(0), (*p.components)(1), (*p.components)(2));
					builder.push_back(pnt);
				}
				const auto& p = boost::get<taxonomy::point3>(e->end);
				cgal_point_t pnt((*p.components)(0), (*p.components)(1), (*p.components)(2));
				builder.push_back(pnt);
			} else if (e->basis->kind() == taxonomy::CIRCLE) {
				// @todo
			} else if (e->basis->kind() == taxonomy::ELLIPSE) {

			} else {
				throw std::runtime_error("Not implemented basis kind");
			}
		} else if (curve->kind() == taxonomy::LOOP) {
			const auto& edges = ((taxonomy::loop*) curve)->children;
			for (auto& c : edges) {
				convert_curve(kernel, c, builder);
			}
		} else {
			throw std::runtime_error("Not implemented curve");
		}
	}
}

namespace {
	typedef std::pair<double, double> parameter_range;

	static const parameter_range unbounded = {
		-std::numeric_limits<double>::infinity(),
		+std::numeric_limits<double>::infinity()
	};

	void evaluate_curve(const taxonomy::line& c, double u, taxonomy::point3& p) {
		Eigen::Vector4d xy{ u, 0, 0, 1. };
		*p.components = (*c.matrix.components * xy).head<3>();
	}

	void evaluate_curve(const taxonomy::circle& c, double u, taxonomy::point3& p) {
		Eigen::Vector4d xy{ c.radius * std::cos(u), c.radius * std::sin(u), 0, 1. };
		*p.components = (*c.matrix.components * xy).head<3>();
	}

	void evaluate_curve(const taxonomy::ellipse& c, double u, taxonomy::point3& p) {
		Eigen::Vector4d xy{ c.radius * std::cos(u), c.radius2 * std::sin(u), 0, 1. };
		*p.components = (*c.matrix.components * xy).head<3>();
	}

	// ----

	void project_onto_curve(const taxonomy::line& c, const taxonomy::point3& p, double& u) {
		u = (c.matrix.components->inverse() * p.components->homogeneous())(0);
	}

	void project_onto_curve(const taxonomy::circle& c, const taxonomy::point3& p, double& u) {
		Eigen::Vector2d xy = (c.matrix.components->inverse() * p.components->homogeneous()).head<2>();
		u = std::atan2(xy(1), xy(0));
	}

	void project_onto_curve(const taxonomy::ellipse& c, const taxonomy::point3& p, double& u) {
		Eigen::Vector2d xy = (c.matrix.components->inverse() * p.components->homogeneous()).head<2>();
		u = std::atan2(xy(1), xy(0));
	}

	struct point_projection_visitor_ {
		taxonomy::point3 p;
		double u;
		typedef void result_type;

		void operator()(const taxonomy::line& c) {
			project_onto_curve(c, p, u);
		}

		void operator()(const taxonomy::circle& c) {
			project_onto_curve(c, p, u);
		}

		void operator()(const taxonomy::ellipse& c) {
			project_onto_curve(c, p, u);
		}

		void operator()(const taxonomy::item& c) {
			throw std::runtime_error("Point projection not implemented on this geometry type");
		}
	};

	struct point_projection_visitor {
		taxonomy::item* curve;
		double u;
		typedef void result_type;
		
		void operator()(const taxonomy::point3& p) {
			point_projection_visitor_ v{ p };
			dispatch_curve_creation<point_projection_visitor_>::dispatch(curve, v);
			u = v.u;
		}

		void operator()(const double& u) {
			this->u = u;
		}
	};

	struct cgal_curve_creation_visitor {
		static const int FULL_CIRCLE_NUM_SEGMENTS = 32;
		parameter_range param;

		std::vector<taxonomy::point3> points;

		cgal_curve_creation_visitor() : param(unbounded) {}
		cgal_curve_creation_visitor(const parameter_range& p) : param(p) {}

		void operator()(const taxonomy::line& l) {
			if (param == unbounded) {
				throw std::runtime_error("Cannot represent infinite line segment");
			}
			taxonomy::point3 start, end;
			evaluate_curve(l, param.first, start);
			evaluate_curve(l, param.second, end);
			points.push_back(start);
			points.push_back(end);
		}

		template <typename T>
		void evaluate_conic(const T& t) {
			double a, b;
			if (param == unbounded) {
				a = 0.;
				b = 2 * M_PI;
			} else {
				std::tie(a, b) = param;
			}
			a = std::fmod(a, 2 * M_PI);
			b = std::fmod(b, 2 * M_PI);
			if (b < a) {
				b += 2 * M_PI;
			}
			int num_segments = (int)std::ceil(std::fabs(a - b) / (2 * M_PI) * FULL_CIRCLE_NUM_SEGMENTS);
			double du = (b - a) / num_segments;
			taxonomy::point3 P;
			// @nb for loop is not inclusive of the both end points
			evaluate_curve(t, a, P);
			points.push_back(P);
			for (int i = 1; i < num_segments; ++i) {
				double u = a + du * i;
				evaluate_curve(t, u, P);
				points.push_back(P);
			}
			evaluate_curve(t, b, P);
			points.push_back(P);
		}

		void operator()(const taxonomy::circle& c) {
			evaluate_conic(c);
		}

		void operator()(const taxonomy::ellipse& e) {
			evaluate_conic(e);
		}

		void operator()(const taxonomy::trimmed_curve& e) {
			point_projection_visitor v1, v2;
			boost::apply_visitor(v1, e.start);
			boost::apply_visitor(v2, e.end);

			if (!e.orientation.get_value_or(true)) {
				std::swap(v1.u, v2.u);
			}

			cgal_curve_creation_visitor v({ v1.u, v2.u });

			dispatch_curve_creation<cgal_curve_creation_visitor>::dispatch(e.basis, v);
			this->points = v.points;
		}

		void operator()(const taxonomy::item& e) {
			throw std::runtime_error("Not supported");
		}
	};

	void convert_curve(taxonomy::item* i, std::vector<taxonomy::point3>& points) {
		cgal_curve_creation_visitor v;
		dispatch_curve_creation<cgal_curve_creation_visitor>::dispatch(i, v);
		points = v.points;
	}

	// @nb mutates a
	void extend_wire(std::vector<taxonomy::point3>& a, const std::vector<taxonomy::point3>& b) {
		if (a.empty()) {
			a = b;
		}
		if (b.empty()) {
			return;
		}
		double d = (*a.back().components - *b.front().components).norm();
		size_t offset = d < 1.e-5 ? 1 : 0;
		a.insert(a.end(), b.begin() + offset, b.end());
	}
}

bool CgalKernel::convert(const taxonomy::loop* loop, cgal_wire_t& result) {
	// @todo only implement polygonal loops

	auto edges = loop->children_as<taxonomy::edge>();
	std::vector<taxonomy::point3> points;

	for (auto& e : edges) {
		if (e->basis) {
			std::vector<taxonomy::point3> edge;
			convert_curve(e, edge);
			if (!e->orientation_2.get_value_or(true)) {
				std::reverse(edge.begin(), edge.end());
			}
			extend_wire(points, edge);
		} else {
			extend_wire(points, {
				boost::get<taxonomy::point3>(e->start),
				boost::get<taxonomy::point3>(e->end)
				});
		}
	}

	if (points.size() >= 2) {
		// the edges -> <p0, ... pn> conversion left us with a duplicate global begin,end point.
		double d = (*points.back().components - *points.front().components).norm();
		points.erase(points.end() - 1);
	}

	// Parse and store the points in a sequence
	cgal_wire_t polygon = std::vector<Kernel_::Point_3>();
	for (auto& p : points) {
		cgal_point_t pnt((*p.components)(0), (*p.components)(1), (*p.components)(2));
		polygon.push_back(pnt);
	}

	// A loop should consist of at least three vertices
	std::size_t original_count = polygon.size();
	if (original_count < 3) {
		Logger::Message(Logger::LOG_ERROR, "Not enough edges for:", loop->instance);
		return false;
	}

	// Remove points that are too close to one another
	remove_duplicate_points_from_loop(polygon);

	std::size_t count = polygon.size();
	if (original_count - count != 0) {
		std::stringstream ss; ss << (original_count - count) << " edges removed for:";
		Logger::Message(Logger::LOG_WARNING, ss.str(), loop->instance);
	}

	if (count < 3) {
		Logger::Message(Logger::LOG_ERROR, "Not enough edges for:", loop->instance);
		return false;
	}

	result = polygon;

	//  std::cout << "PolyLoop: " << std::endl;
	//  for (auto &point: polygon) {
	//    std::cout << "\tPoint(" << point << ")" << std::endl;
	//  }

	return true;
}


bool CgalKernel::convert_impl(const taxonomy::shell *shell, ifcopenshell::geometry::ConversionResults& results) {
	cgal_shape_t shape;
	if (!convert(shell, shape)) {
		return false;
	}
	results.emplace_back(ConversionResult(
		shell->instance->data().id(),
		shell->matrix,
		new CgalShape(shape),
		shell->surface_style
	));
	return true;
}

bool CgalKernel::convert_impl(const taxonomy::extrusion* extrusion, ifcopenshell::geometry::ConversionResults& results) {
	cgal_shape_t shape;
	if (!convert(extrusion, shape)) {
		return false;
	}
	results.emplace_back(ConversionResult(
		extrusion->instance->data().id(),
		extrusion->matrix,
		new CgalShape(shape),
		extrusion->surface_style
	));
	return true;
}

bool CgalKernel::convert(const taxonomy::extrusion* extrusion, cgal_shape_t &shape) {
	const double& height = extrusion->depth;
	if (height < precision_) {
		Logger::Message(Logger::LOG_ERROR, "Non-positive extrusion height encountered for:", extrusion->instance);
		return false;
	}

	// Outer
	cgal_face_t bottom_face;
	if (!convert(&extrusion->basis, bottom_face)) {
		return false;
	}
	//  std::cout << "Face vertices: " << face.outer.size() << std::endl;

	auto fs = *extrusion->direction.components;
	cgal_direction_t dir(fs(0), fs(1), fs(2));
	//  std::cout << "Direction: " << dir << std::endl;

	std::list<cgal_face_t> face_list;
	face_list.push_back(bottom_face);

	for (std::vector<Kernel_::Point_3>::const_iterator current_vertex = bottom_face.outer.begin();
		current_vertex != bottom_face.outer.end();
		++current_vertex) {
		std::vector<Kernel_::Point_3>::const_iterator next_vertex = current_vertex;
		++next_vertex;
		if (next_vertex == bottom_face.outer.end()) {
			next_vertex = bottom_face.outer.begin();
		} cgal_face_t side_face;
		side_face.outer.push_back(*next_vertex);
		side_face.outer.push_back(*current_vertex);
		side_face.outer.push_back(*current_vertex + height * dir);
		side_face.outer.push_back(*next_vertex + height * dir);
		face_list.push_back(side_face);
	}

	cgal_face_t top_face;
	for (std::vector<Kernel_::Point_3>::const_reverse_iterator vertex = bottom_face.outer.rbegin();
		vertex != bottom_face.outer.rend();
		++vertex) {
		top_face.outer.push_back(*vertex + height * dir);
	} face_list.push_back(top_face);

	if (bottom_face.inner.empty()) {
		shape = utils::create_polyhedron(face_list);
		// if (has_position) for (auto &vertex : vertices(shape)) vertex->point() = vertex->point().transform(trsf);
		return true;
	}

	CGAL::Nef_polyhedron_3<Kernel_> nef_shape = utils::create_nef_polyhedron(face_list);

	// Inner
	// TODO: Would be faster to triangulate top/bottom face template rather than use Nef polyhedra for subtraction
	for (auto &inner : bottom_face.inner) {
		//    std::cout << "Inner wire" << std::endl;
		face_list.clear();

		cgal_face_t hole_bottom_face;
		hole_bottom_face.outer = inner;
		remove_duplicate_points_from_loop(hole_bottom_face.outer);
		face_list.push_back(hole_bottom_face);

		for (std::vector<Kernel_::Point_3>::const_iterator current_vertex = inner.begin();
			current_vertex != inner.end();
			++current_vertex) {
			std::vector<Kernel_::Point_3>::const_iterator next_vertex = current_vertex;
			++next_vertex;
			if (next_vertex == inner.end()) {
				next_vertex = inner.begin();
			} cgal_face_t hole_side_face;
			hole_side_face.outer.push_back(*next_vertex);
			hole_side_face.outer.push_back(*current_vertex);
			hole_side_face.outer.push_back(*current_vertex + height * dir);
			hole_side_face.outer.push_back(*next_vertex + height * dir);
			face_list.push_back(hole_side_face);
		}

		cgal_face_t hole_top_face;
		for (std::vector<Kernel_::Point_3>::const_reverse_iterator vertex = inner.rbegin();
			vertex != inner.rend();
			++vertex) {
			hole_top_face.outer.push_back(*vertex + height * dir);
		} face_list.push_back(hole_top_face);

		try {
			nef_shape -= utils::create_nef_polyhedron(face_list);
		} catch (...) {
			Logger::Message(Logger::LOG_ERROR, "IfcExtrudedAreaSolid: cannot subtract opening for:", extrusion->instance);
			return false;
		}
	}

	/*if (has_position) {
		// IfcSweptAreaSolid.Position (trsf) is an IfcAxis2Placement3D
		// and therefore has a unit scale factor
		nef_shape.transform(trsf);
	}*/

	try {
		nef_shape.convert_to_polyhedron(shape);
		return true;
	} catch (...) {
		Logger::Message(Logger::LOG_ERROR, "IfcExtrudedAreaSolid: cannot convert Nef to polyhedron for:", extrusion->instance);
		return false;
	}

}

CGAL::Polyhedron_3<Kernel_> ifcopenshell::geometry::utils::create_cube(double d) {
	cgal_face_t bottom_face;
	bottom_face.outer.push_back(Kernel_::Point_3(-d, -d, -d));
	bottom_face.outer.push_back(Kernel_::Point_3(+d, -d, -d));
	bottom_face.outer.push_back(Kernel_::Point_3(+d, +d, -d));
	bottom_face.outer.push_back(Kernel_::Point_3(-d, +d, -d));

	cgal_direction_t dir(0, 0, 2 * d);

	std::list<cgal_face_t> face_list = { bottom_face };
		
	for (std::vector<Kernel_::Point_3>::const_iterator current_vertex = bottom_face.outer.begin();
		current_vertex != bottom_face.outer.end();
		++current_vertex)
	{
		std::vector<Kernel_::Point_3>::const_iterator next_vertex = current_vertex;
		++next_vertex;

		if (next_vertex == bottom_face.outer.end()) {
			next_vertex = bottom_face.outer.begin();
		}
			
		cgal_face_t side_face;
			
		side_face.outer.push_back(*next_vertex);
		side_face.outer.push_back(*current_vertex);
		side_face.outer.push_back(*current_vertex + dir);
		side_face.outer.push_back(*next_vertex + dir);

		face_list.push_back(side_face);
	}

	cgal_face_t top_face;

	for (std::vector<Kernel_::Point_3>::const_reverse_iterator vertex = bottom_face.outer.rbegin();
		vertex != bottom_face.outer.rend();
		++vertex)
	{
		top_face.outer.push_back(*vertex + dir);
	}
		
	face_list.push_back(top_face);

	return create_polyhedron(face_list);
}


CGAL::Polyhedron_3<Kernel_> ifcopenshell::geometry::utils::create_cube(const Kernel_::Point_3& lower, const Kernel_::Point_3& upper) {
	cgal_face_t bottom_face;

	auto a0 = lower.cartesian(0);
	auto a1 = lower.cartesian(1);
	auto a2 = lower.cartesian(2);

	auto b0 = upper.cartesian(0);
	auto b1 = upper.cartesian(1);
	auto b2 = upper.cartesian(2);

	bottom_face.outer.push_back(Kernel_::Point_3(a0, a1, a2));
	bottom_face.outer.push_back(Kernel_::Point_3(b0, a1, a2));
	bottom_face.outer.push_back(Kernel_::Point_3(b0, b1, a2));
	bottom_face.outer.push_back(Kernel_::Point_3(a0, b1, a2));

	cgal_direction_t dir(0, 0, b2 - a2);

	std::list<cgal_face_t> face_list = { bottom_face };
		
	for (std::vector<Kernel_::Point_3>::const_iterator current_vertex = bottom_face.outer.begin();
		current_vertex != bottom_face.outer.end();
		++current_vertex)
	{
		std::vector<Kernel_::Point_3>::const_iterator next_vertex = current_vertex;
		++next_vertex;

		if (next_vertex == bottom_face.outer.end()) {
			next_vertex = bottom_face.outer.begin();
		}
			
		cgal_face_t side_face;
			
		side_face.outer.push_back(*next_vertex);
		side_face.outer.push_back(*current_vertex);
		side_face.outer.push_back(*current_vertex + dir);
		side_face.outer.push_back(*next_vertex + dir);

		face_list.push_back(side_face);
	}

	cgal_face_t top_face;

	for (std::vector<Kernel_::Point_3>::const_reverse_iterator vertex = bottom_face.outer.rbegin();
		vertex != bottom_face.outer.rend();
		++vertex)
	{
		top_face.outer.push_back(*vertex + dir);
	}
		
	face_list.push_back(top_face);

	return create_polyhedron(face_list);
}

bool CgalKernel::thin_solid(const CGAL::Nef_polyhedron_3<Kernel_>& a, CGAL::Nef_polyhedron_3<Kernel_>& result) {
	// @todo this should be possible as a minkowski sum of facet & cube. rather than a set of boolean ops.

	auto a_nonconst = a;
	auto ax = CGAL::minkowski_sum_3(a_nonconst, precision_cube_);
	auto x = ax - a;

	result = x;
	return true;

	auto yxy = CGAL::minkowski_sum_3(x, precision_cube_);
	auto y = yxy * a;
	auto zyz = CGAL::minkowski_sum_3(y, precision_cube_);
	result = yxy * zyz;

	return true;
}

bool CgalKernel::preprocess_boolean_operand(const IfcUtil::IfcBaseClass* log_reference, const cgal_shape_t& shape_const, CGAL::Nef_polyhedron_3<Kernel_>& result, bool dilate) {
	cgal_shape_t shape = shape_const;

	if (!shape.is_valid()) {
		Logger::Message(Logger::LOG_ERROR, "Conversion to Nef will fail. Invalid geometry:", log_reference);
		return false;
	}

	if (!shape.is_closed()) {
		// TODO: There can be substractions to remove parts of non-volumetric objects. Maybe iterate over all faces of an entity and put them in a Nef_polyhedron_3 through Boolean union? Highly inefficient but maybe desirable...
		Logger::Message(Logger::LOG_ERROR, "Subtraction of openings not supported for non-closed geometry:", log_reference);
		return false;
	}

	bool success = false;

	try {
		success = CGAL::Polygon_mesh_processing::triangulate_faces(shape);
	} catch (...) {
		Logger::Message(Logger::LOG_ERROR, "Triangulation of geometry crashed:", log_reference);
		return false;
	}

	if (!success) {
		Logger::Message(Logger::LOG_ERROR, "Triangulation of geometry failed:", log_reference);
		return false;
	}

	if (CGAL::Polygon_mesh_processing::does_self_intersect(shape)) {
		Logger::Message(Logger::LOG_ERROR, "Conversion to Nef will fail. Self-intersecting geometry:", log_reference);
		return false;
	}

	try {
		result = CGAL::Nef_polyhedron_3<Kernel_>(shape);
	} catch (...) {
		Logger::Message(Logger::LOG_ERROR, "Could not convert geometry to Nef:", log_reference);
		return false;
	}

	if (dilate) {
		try {
			// @todo don't dilate in 3 dimensions but only in the XY plane, orthogonal to wall axis.
			result = CGAL::minkowski_sum_3(result, precision_cube_);
		} catch (...) {
			Logger::Message(Logger::LOG_ERROR, "Could not dilate boolean operand", log_reference);
			return false;
		}
	}		

	try {
		cgal_shape_t convert_back;
		result.convert_to_polyhedron(convert_back);
	} catch (...) {
		Logger::Message(Logger::LOG_WARNING, "Final conversion will likely fail. Could not convert geometry from Nef:", log_reference);
	}

	return true;
}

namespace {
	bool convert_placement(const ifcopenshell::geometry::taxonomy::matrix4& place, cgal_placement_t& trsf) {
		const auto& m = *place.components;

		// @todo check
		trsf = cgal_placement_t(
			m(0, 0), m(0, 1), m(0, 2), m(0, 3),
			m(1, 0), m(1, 1), m(1, 2), m(1, 3),
			m(2, 0), m(2, 1), m(2, 2), m(2, 3));

		return true;
	}
}



bool CgalKernel::convert_impl(const taxonomy::boolean_result* br, ifcopenshell::geometry::ConversionResults& results) {
	bool first = true;

	CGAL::Nef_polyhedron_3<Kernel_> a;

	taxonomy::style first_item_style;

	for (auto& c : br->children) {
		// AbstractKernel::convert(c, results);
		// continue;

		ifcopenshell::geometry::ConversionResults cr;
		// @todo half-space detection
		AbstractKernel::convert(c, cr);

		if (first && br->operation == taxonomy::boolean_result::SUBTRACTION) {
			first_item_style = ((taxonomy::geom_item*)c)->surface_style;
			if (!first_item_style.diffuse && c->kind() == taxonomy::COLLECTION) {
				first_item_style = ((taxonomy::geom_item*) ((taxonomy::collection*)c)->children[0])->surface_style;
			}
		}

		for (auto it = cr.begin(); it != cr.end(); ++it) {
			const cgal_shape_t& entity_shape_unlocated(((CgalShape*)it->Shape())->shape());
			cgal_shape_t entity_shape(entity_shape_unlocated);
			if (!it->Placement().components->isIdentity()) {
				cgal_placement_t trsf;
				convert_placement(it->Placement(), trsf);
				for (auto &vertex : vertices(entity_shape)) {
					if (false) {
						auto x = CGAL::to_double(vertex->point().x());
						auto y = CGAL::to_double(vertex->point().y());
						auto z = CGAL::to_double(vertex->point().z());
						std::wcout << x << " " << y << " " << z << std::endl;
					}
					vertex->point() = vertex->point().transform(trsf);
					if (false) {
						auto x = CGAL::to_double(vertex->point().x());
						auto y = CGAL::to_double(vertex->point().y());
						auto z = CGAL::to_double(vertex->point().z());
						std::wcout << x << " " << y << " " << z << std::endl;
					}
				}
			}

			CGAL::Nef_polyhedron_3<Kernel_> nef;
			preprocess_boolean_operand(c->instance, entity_shape, nef,
				// Dilate boolean subtraction operands
				(!first && br->operation == taxonomy::boolean_result::SUBTRACTION));

			if (first) {
				a = nef;
			} else {
				if (br->operation == taxonomy::boolean_result::SUBTRACTION) {
					a -= nef;
				} else if (br->operation == taxonomy::boolean_result::INTERSECTION) {
					a *= nef;
				} else if (br->operation == taxonomy::boolean_result::UNION) {
					a += nef;
				}
			}
		}

		first = false;
	}

	cgal_shape_t a_poly, b_poly;

	// CGAL::Nef_polyhedron_3<Kernel_> b;
	// thin_solid(a, b);

	try {
		a.convert_to_polyhedron(a_poly);
	} catch (...) {
		Logger::Message(Logger::LOG_ERROR, "Could not convert geometry with openings from Nef:", br->instance);
		return false;
	}

	results.emplace_back(ConversionResult(
		br->instance->data().id(),
		br->matrix,
		new CgalShape(a_poly),
		br->surface_style.diffuse ? br->surface_style : first_item_style
	));
	return true;
}