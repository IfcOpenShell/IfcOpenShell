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
#include <CGAL/exceptions.h>

#include <CGAL/Polygon_set_2.h>
#include <CGAL/Boolean_set_operations_2.h>
#include <CGAL/Arr_vertical_decomposition_2.h>
#include <CGAL/Polygon_vertical_decomposition_2.h>
#include <CGAL/Polygon_triangulation_decomposition_2.h>
#include <CGAL/Polygon_mesh_processing/locate.h>

using namespace IfcGeom;
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

namespace {
	struct PolyhedronBuilder : public CGAL::Modifier_base<CGAL::Polyhedron_3<Kernel_>::HalfedgeDS> {
	private:
		std::list<cgal_face_t> *face_list;
	public:
		boost::optional<cgal_shape_t> from_soup;
		PolyhedronBuilder(std::list<cgal_face_t> *face_list);
		void operator()(CGAL::Polyhedron_3<Kernel_>::HalfedgeDS &hds);
	};
}

CGAL::Polyhedron_3<Kernel_> ifcopenshell::geometry::utils::create_polyhedron(std::list<cgal_face_t> &face_list, bool stitch_borders) {

	// Naive creation
	CGAL::Polyhedron_3<Kernel_> polyhedron;
	PolyhedronBuilder builder(&face_list);
	polyhedron.delegate(builder);
	if (builder.from_soup) {
		polyhedron = *builder.from_soup;
	}

	// Stitch edges
	//  std::cout << "Before: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;

	if (stitch_borders) {
		// we have a map of points now in the builder, it's maybe not necessary anymore to stitch_borders?
		// size_t ne = polyhedron.size_of_border_edges();
		CGAL::Polygon_mesh_processing::stitch_borders(polyhedron);
		// size_t ne2 = polyhedron.size_of_border_edges();
		// std::wcout << (ne - ne2) << " removed" << std::endl;
	}

	polyhedron.normalize_border();
	if (!polyhedron.is_valid(false, 1)) {
		Logger::Message(Logger::LOG_ERROR, "create_polyhedron: Polyhedron not valid!");
		//    std::ofstream fresult;
		//    fresult.open("/Users/ken/Desktop/invalid.off");
		//    fresult << polyhedron << std::endl;
		//    fresult.close();
		return CGAL::Polyhedron_3<Kernel_>();
	} if (polyhedron.is_closed()) {
		try {
			if (!CGAL::Polygon_mesh_processing::is_outward_oriented(polyhedron)) {
				CGAL::Polygon_mesh_processing::reverse_face_orientations(polyhedron);
			}
		} catch (CGAL::Failure_exception& e) {
			Logger::Message(Logger::LOG_ERROR, e);
		}
	}

	//  std::cout << "After: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;

	return polyhedron;
}

#ifndef IFOPSH_SIMPLE_KERNEL
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
#endif

bool CgalKernel::convert(const taxonomy::shell::ptr l, cgal_shape_t& shape) {
	if (false && l->children.size() > 100) {
		static double inf = 1.e9; //  std::numeric_limits<double>::infinity();
		std::pair<Eigen::Vector3d, Eigen::Vector3d> minmax(
			Eigen::Vector3d(+inf, +inf, +inf),
			Eigen::Vector3d(-inf, -inf, -inf)
		);
		size_t num_points = 0;
		visit_2<taxonomy::point3, taxonomy::shell>(l, [&minmax, &num_points](const taxonomy::point3::ptr p) {
			auto& c = p->ccomponents();
			++num_points;
			for (int i = 0; i < 3; ++i) {
				if (c(i) < minmax.first(i)) {
					minmax.first(i) = c(i);
				}
				if (c(i) > minmax.second(i)) {
					minmax.second(i) = c(i);
				}
			}
		});
		auto diag = minmax.second - minmax.first;
		double volume = diag(0) * diag(1) * diag(2);
		// @todo volume van be zero also..
		double density = num_points / volume;
		Logger::Notice("Density " + boost::lexical_cast<std::string>(density), l->instance);
		if (density > 5000) {
			Logger::Notice("Substituted element with " + boost::lexical_cast<std::string>(density) + " vertices / m3 with a bounding box");
			CGAL::Point_3<Kernel_> lower(minmax.first(0), minmax.first(1), minmax.first(2));
			CGAL::Point_3<Kernel_> upper(minmax.second(0), minmax.second(1), minmax.second(2));
			shape = utils::create_cube(lower, upper);
			return true;
		}
	}

	std::list<cgal_face_t> face_list;
	for (auto& f : l->children) {
		bool success = false;
		try {
			success = convert(f, face_list);
		} catch (...) {}

		if (!success) {
			Logger::Message(Logger::LOG_WARNING, "Failed to convert face:", f->instance);
			continue;
		}

		//    std::cout << "Face in ConnectedFaceSet: " << std::endl;
		//    for (auto &point: face.outer) {
		//      std::cout << "\tPoint(" << point << ")" << std::endl;
		//    }
	}

	shape = utils::create_polyhedron(face_list);
	return shape.size_of_facets();
}

bool CgalKernel::convert(const taxonomy::face::ptr face, std::list<cgal_face_t>& result) {
	int num_outer_bounds = 0;

	for (auto& bound : face->children) {
		if (bound->external.get_value_or(false)) num_outer_bounds++;
	}

	if (face->children.size() > 1 && num_outer_bounds > 1 && face->children.size() != num_outer_bounds) {
		Logger::Message(Logger::LOG_ERROR, "Invalid configuration of boundaries for:", face->instance);
		return false;
	}

	cgal_face_t mf;

	for (auto& bound : face->children) {

		const bool is_interior = !(bound->external.get_value_or(false) || face->children.size() == 1);
		// single face bound is always external... even if not marked as such

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

		if (num_outer_bounds > 1) {
			result.push_back(mf);
			mf = cgal_face_t{};
		}
	}

	if (num_outer_bounds == 1 || face->children.size() == 1) {
		result.push_back(mf);
	}

	//  std::cout << "Face: " << std::endl;
	//  for (auto &point: face.outer) {
	//    std::cout << "\tPoint(" << point << ")" << std::endl;
	//  }

	return true;
}

namespace {
	// @todo obsolete?
	/*
	bool convert_curve(CgalKernel* kernel, const taxonomy::ptr curve, cgal_wire_t& builder) {
		if (auto e = taxonomy::dcast<taxonomy::edge>(curve)) {
			if (true || e->basis == nullptr) {
				if (builder.empty()) {
					const auto& p = boost::get<taxonomy::point3::ptr>(e->start);
					cgal_point_t pnt(p->ccomponents()(0), p->ccomponents()(1), p->ccomponents()(2));
					builder.push_back(pnt);
				}
				const auto& p = boost::get<taxonomy::point3::ptr>(e->end);
				cgal_point_t pnt(p->ccomponents()(0), p->ccomponents()(1), p->ccomponents()(2));
				builder.push_back(pnt);
			} else if (e->basis->kind() == taxonomy::CIRCLE) {
				// @todo
			} else if (e->basis->kind() == taxonomy::ELLIPSE) {
				// @todo
			} else {
				throw std::runtime_error("Not implemented basis kind");
			}
		} else if (auto lp = taxonomy::dcast<taxonomy::loop>(curve)) {
			for (auto& c : lp->children) {
				convert_curve(kernel, c, builder);
			}
		} else {
			throw std::runtime_error("Not implemented curve");
		}
	}
	*/
}

namespace {
	typedef std::pair<double, double> parameter_range;

	static const parameter_range unbounded = {
		-std::numeric_limits<double>::infinity(),
		+std::numeric_limits<double>::infinity()
	};

	void evaluate_curve(const taxonomy::line::ptr& c, double u, taxonomy::point3& p) {
		Eigen::Vector4d xy{ 0, 0, u, 1. };
		p.components() = (c->matrix->ccomponents() * xy).head<3>();
	}

	void evaluate_curve(const taxonomy::circle::ptr& c, double u, taxonomy::point3& p) {
		Eigen::Vector4d xy{ c->radius * std::cos(u), c->radius * std::sin(u), 0, 1. };
		p.components() = (c->matrix->ccomponents() * xy).head<3>();
	}

	void evaluate_curve(const taxonomy::ellipse::ptr& c, double u, taxonomy::point3& p) {
		Eigen::Vector4d xy{ c->radius * std::cos(u), c->radius2 * std::sin(u), 0, 1. };
		p.components() = (c->matrix->ccomponents() * xy).head<3>();
	}

	// ----

	void project_onto_curve(const taxonomy::line::ptr& c, const taxonomy::point3& p, double& u) {
		u = (c->matrix->ccomponents().inverse() * p.ccomponents().homogeneous())(2);
	}

	void project_onto_curve(const taxonomy::circle::ptr& c, const taxonomy::point3& p, double& u) {
		Eigen::Vector2d xy = (c->matrix->ccomponents().inverse() * p.ccomponents().homogeneous()).head<2>();
		u = std::atan2(xy(1), xy(0));
	}

	void project_onto_curve(const taxonomy::ellipse::ptr& c, const taxonomy::point3& p, double& u) {
		Eigen::Vector2d xy = (c->matrix->ccomponents().inverse() * p.ccomponents().homogeneous()).head<2>();
		u = std::atan2(xy(1), xy(0));
	}

	struct point_projection_visitor_ {
		taxonomy::point3 p;
		double u;
		typedef void result_type;

		void operator()(const taxonomy::line::ptr& c) {
			project_onto_curve(c, p, u);
		}

		void operator()(const taxonomy::circle::ptr& c) {
			project_onto_curve(c, p, u);
		}

		void operator()(const taxonomy::ellipse::ptr& c) {
			project_onto_curve(c, p, u);
		}

		void operator()(const taxonomy::item::ptr&) {
			throw std::runtime_error("Point projection not implemented on this geometry type");
		}
	};

	struct point_projection_visitor {
		taxonomy::ptr curve;
		double u;
		typedef void result_type;

		void operator()(const boost::blank&) {
			throw std::runtime_error("Unbounded curve not supported here");
		}

		void operator()(const taxonomy::point3::ptr& p) {
			point_projection_visitor_ v{ *p };
			dispatch_curve_creation<point_projection_visitor_>::dispatch(curve, v);
			u = v.u;
		}

		void operator()(const double& u) {
			this->u = u;
		}
	};

	struct cgal_curve_creation_visitor {
		Settings& settings_;
		parameter_range param;

		std::vector<taxonomy::point3> points;

		cgal_curve_creation_visitor(Settings& s) : settings_(s), param(unbounded) {}
		cgal_curve_creation_visitor(Settings& s, const parameter_range& p) : settings_(s), param(p) {}

		void operator()(const taxonomy::line::ptr& l) {
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
			if (b <= a) {
				b += 2 * M_PI;
			}
			int num_segments = (int)std::ceil(std::fabs(a - b) / (2 * M_PI) * settings_.get<settings::CircleSegments>().get());
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

		void operator()(const taxonomy::circle::ptr& c) {
			evaluate_conic(c);
		}

		void operator()(const taxonomy::ellipse::ptr& e) {
			evaluate_conic(e);
		}

		void operator()(const taxonomy::trimmed_curve::ptr& e) {
			auto e_basis = e->basis;

			while (e_basis->kind() == taxonomy::EDGE && e_basis->instance && e_basis->instance->declaration().name() == "IfcTrimmedCurve") {
				// @todo we still might have something to wrt orientation on periodic curves
				// to make sure we select the correct arc later on.
				e_basis = taxonomy::cast<taxonomy::edge>(e_basis)->basis;
			}

			point_projection_visitor v1{ e->basis }, v2{ e->basis };
			boost::apply_visitor(v1, e->start);
			boost::apply_visitor(v2, e->end);

			if (!e->curve_sense.get_value_or(true)) {
				std::swap(v1.u, v2.u);
			}

			cgal_curve_creation_visitor v(settings_, { v1.u, v2.u });

			dispatch_curve_creation<cgal_curve_creation_visitor>::dispatch(e->basis, v);
			this->points = v.points;

			if (!e->curve_sense.get_value_or(true)) {
				std::reverse(this->points.begin(), this->points.end());
			}
		}

		void operator()(const taxonomy::edge::ptr& e) {
			return (*this)(taxonomy::dcast<taxonomy::trimmed_curve>(e));
		}

		void operator()(const taxonomy::item::ptr&) {
			throw std::runtime_error("Not supported");
		}
	};

	void convert_curve(Settings& s, taxonomy::ptr i, std::vector<taxonomy::point3>& points) {
		cgal_curve_creation_visitor v(s);
		dispatch_curve_creation<cgal_curve_creation_visitor>::dispatch(i, v);
		points = v.points;
	}

	// @nb mutates a
	void extend_wire(std::vector<taxonomy::point3>& a, const std::vector<taxonomy::point3>& b) {
		if (a.empty()) {
			a = b;
			return;
		}
		if (b.empty()) {
			return;
		}
		double d = (a.back().ccomponents() - b.front().ccomponents()).norm();
		size_t offset = d < 1.e-5 ? 1 : 0;
		a.insert(a.end(), b.begin() + offset, b.end());
	}
}

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/box_intersection_d.h>
#include <vector>
#include <fstream>

typedef CGAL::Box_intersection_d::Box_with_handle_d<double, 3, int*> Box;

namespace {
	void loop_to_segments(const cgal_wire_t& wire, std::vector<Kernel_::Segment_3>& segments) {
		for (int i = 0; i < wire.size(); ++i) {
			int j = (i + 1) % wire.size();
			segments.emplace_back(wire[i], wire[j]);
		}
	}

	struct intersection_collector {

		const std::vector<Kernel_::Segment_3>& segments;
		int num_self_intersections = 0;

		explicit intersection_collector(const std::vector<Kernel_::Segment_3>& s)
			: segments(s)
		{}

		void operator()(const Box& a, const Box& b) {
			int aid = *a.handle();
			int bid = *b.handle();

			if (aid > bid) {
				std::swap(aid, bid);
			}

			if (((aid + 1) == bid) || ((aid == 0) && (bid = (segments.size() - 1)))) {
				// consecutive segments.
				return;
			}

			auto s0 = segments[aid];
			auto s1 = segments[bid];

			if (CGAL::do_intersect(s0, s1)) {
				num_self_intersections++;
			}
		}
	};

	bool do_segments_intersect(const std::vector<Kernel_::Segment_3>& segments) {
		std::vector<Box> boxes;
		std::vector<int> handles(segments.size());
		std::iota(handles.begin(), handles.end(), 0);
		for (auto it = segments.begin(); it != segments.end(); ++it) {
			boxes.push_back(Box(it->bbox(), &*(handles.begin() + std::distance(segments.begin(), it))));
		}
		intersection_collector x(segments);
		CGAL::box_self_intersection_d(boxes.begin(), boxes.end(), x);
		return !!x.num_self_intersections;
	}
}

namespace {
	cgal_direction_t newell(const std::vector<cgal_point_t> & loop) {
		Kernel_::FT a(0.0), b(0.0), c(0.0);
		for (size_t i = 0; i < loop.size(); ++i) {
			auto & curr = loop[i];
			auto & next = loop[(i + 1) % loop.size()];
			a += (curr.y() - next.y()) * (curr.z() + next.z());
			b += (curr.z() - next.z()) * (curr.x() + next.x());
			c += (curr.x() - next.x()) * (curr.y() + next.y());
		}
		return cgal_direction_t(a, b, c);
	}
}

namespace {
	CGAL::Polygon_2<Kernel_> loop_to_polygon_2(taxonomy::loop::ptr loop) {
		CGAL::Polygon_2<Kernel_> polygon;
		for (auto& e : loop->children) {
			auto& p = *boost::get<taxonomy::point3::ptr>(e->start);
			CGAL::Point_2<Kernel_> pnt(p.ccomponents()(0), p.ccomponents()(1));
			polygon.push_back(pnt);
		}
		return polygon;
	}

	CGAL::Polygon_2<Kernel_> wire_to_polygon_2(const cgal_wire_t& w) {
		CGAL::Polygon_2<Kernel_> polygon;
		for (auto& p : w) {
			CGAL::Point_2<Kernel_> pnt(p.cartesian(0), p.cartesian(1));
			polygon.push_back(pnt);
		}
		return polygon;
	}

	cgal_face_t wire_to_face(const cgal_wire_t& w) {
		cgal_face_t f;
		f.outer = w;
		return f;
	}

	class polygon_2_to_wire {
	private:
		const CGAL::Aff_transformation_3<Kernel_>& t_;

	public:
		polygon_2_to_wire(const CGAL::Aff_transformation_3<Kernel_>& t)
			: t_(t) {}

		cgal_wire_t operator()(const CGAL::Polygon_2<Kernel_>& p) {
			cgal_wire_t w;
			for (auto it = p.vertices_begin(); it != p.vertices_end(); ++it) {
				cgal_point_t P(it->cartesian(0), it->cartesian(1), 0);
				P = t_.transform(P);
				w.push_back(P);
			}
			return w;
		}
	};

	void transform_in_place(cgal_wire_t& w, const CGAL::Aff_transformation_3<Kernel_>& t) {
		for (auto& p : w) {
			p = p.transform(t);
		}
	}
}

namespace {
	void face_to_poly_with_holes(const cgal_face_t& face, CGAL::Polygon_with_holes_2<Kernel_>& pwh, CGAL::Aff_transformation_3<Kernel_>& place) {
		// static 
		Kernel_::Vector_3 Z(0, 0, 1);
		// static 
		Kernel_::Vector_3 X(1, 0, 0);

		auto refz = newell(face.outer);
		refz /= std::sqrt(CGAL::to_double(refz.squared_length()));
		auto refx = CGAL::abs(refz.cartesian(0)) > CGAL::abs(refz.cartesian(2)) ? Z : X;
		auto refy = CGAL::cross_product(refz, refx);
		auto refl = face.outer.front();

		place = CGAL::Aff_transformation_3<Kernel_>(
			refx.cartesian(0), refy.cartesian(0), refz.cartesian(0), refl.cartesian(0),
			refx.cartesian(1), refy.cartesian(1), refz.cartesian(1), refl.cartesian(1),
			refx.cartesian(2), refy.cartesian(2), refz.cartesian(2), refl.cartesian(2)
			);

		/*
		CGAL::NT_converter<Kernel_::FT, double> c;
		std::array<std::array<double, 4>, 4> matrix;
		for (int i = 0; i < 4; ++i) {
			for (int j = 0; j < 4; ++j) {
				matrix[i][j] = c(place.cartesian(i, j));
			}
		}
		*/

		auto ref = place.inverse();

		auto face_copy = face;
		transform_in_place(face_copy.outer, ref);
		for (auto& w : face_copy.inner) {
			transform_in_place(w, ref);
		}

		std::vector<CGAL::Polygon_2<Kernel_>> holes;
		holes.reserve(face_copy.inner.size());
		std::transform(face_copy.inner.begin(), face_copy.inner.end(), std::back_inserter(holes), wire_to_polygon_2);
		pwh = CGAL::Polygon_with_holes_2<Kernel_>(wire_to_polygon_2(face_copy.outer), holes.begin(), holes.end());
	}
}


bool CgalKernel::convert(const taxonomy::loop::ptr loop, cgal_wire_t& result) {
	// @todo only implement polygonal loops

	std::vector<taxonomy::point3> points;

	for (auto& e : loop->children) {
		std::vector<taxonomy::point3> edge;
		if (e->basis && e->basis->kind() != taxonomy::LINE) {
			convert_curve(settings_, e, edge);
		} else {
			edge = {
				*boost::get<taxonomy::point3::ptr>(e->start),
				*boost::get<taxonomy::point3::ptr>(e->end)
			};
		}

		if (!e->orientation.get_value_or(true)) {
			std::reverse(edge.begin(), edge.end());
		}

		extend_wire(points, edge);
	}

	if (points.size() >= 2) {
		// the edges -> <p0, ... pn> conversion left us with a duplicate global begin,end point.
		double d = (points.back().ccomponents() - points.front().ccomponents()).norm();
		if (d < 1.e-5) {
			points.erase(points.end() - 1);
		} else {
			Logger::Warning("Loop not closed", loop->instance);
		}
	}

	// Parse and store the points in a sequence
	cgal_wire_t polygon = std::vector<Kernel_::Point_3>();
	for (auto& p : points) {
		cgal_point_t pnt(p.ccomponents()(0), p.ccomponents()(1), p.ccomponents()(2));
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

	std::vector<Kernel_::Segment_3> segments;
	loop_to_segments(polygon, segments);

	auto inf = 1.e9; //  std::numeric_limits<double>::infinity();
	double min_len = +inf;
	for (auto& s : segments) {
		auto l = std::sqrt(CGAL::to_double(s.squared_length()));
		if (l < min_len) {
			min_len = l;
		}
	}

	if (do_segments_intersect(segments)) {
		Logger::Message(Logger::LOG_WARNING, "Skipping self-intersecting loop", loop->instance);
		return false;
	}

	auto dir = newell(polygon);
	Kernel_::FT min_dot(+inf), max_dot(-inf);
	for (auto& p : polygon) {
		auto dot = dir * (p - CGAL::ORIGIN);
		if (dot < min_dot) {
			min_dot = dot;
		}
		if (dot > max_dot) {
			max_dot = dot;
		}
	}

	auto delta_dot = max_dot - min_dot;
	// @todo this can be used to assess face planarity.

	/*
	std::wcerr << "[" << std::endl;
	for (auto& p : polygon) {
		std::wcerr << "    (" << CGAL::to_double(p.cartesian(0)) << ", " << CGAL::to_double(p.cartesian(1)) << ", " << CGAL::to_double(p.cartesian(2)) << ")," << std::endl;
	}
	std::wcerr << "]" << std::endl;
	*/

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


bool CgalKernel::convert_impl(const taxonomy::shell::ptr shell, ConversionResults& results) {
	cgal_shape_t shape;
	if (!convert(shell, shape)) {
		return false;
	}
	if (shape.size_of_facets() == 0) {
		return false;
	}
	results.emplace_back(ConversionResult(
		shell->instance->as<IfcUtil::IfcBaseEntity>()->id(),
		shell->matrix,
		new CgalShape(shape),
		shell->surface_style
	));
	return true;
}

bool CgalKernel::convert_impl(const taxonomy::solid::ptr solid, ConversionResults& results) {
	cgal_shape_t shape;
	if (solid->children.empty()) {
		return false;
	}
	// @todo
	if (!convert((taxonomy::shell::ptr)solid->children[0], shape)) {
		return false;
	}
	if (shape.size_of_facets() == 0) {
		return false;
	}
	results.emplace_back(ConversionResult(
		solid->instance->as<IfcUtil::IfcBaseEntity>()->id(),
		solid->matrix,
		new CgalShape(shape),
		solid->surface_style
	));
	return true;
}

namespace {
	bool convert_placement(const Eigen::Matrix4d& m, cgal_placement_t& trsf) {
		// @todo check
		trsf = cgal_placement_t(
			m(0, 0), m(0, 1), m(0, 2), m(0, 3),
			m(1, 0), m(1, 1), m(1, 2), m(1, 3),
			m(2, 0), m(2, 1), m(2, 2), m(2, 3));

		return true;
	}
	bool convert_placement(ifcopenshell::geometry::taxonomy::matrix4::ptr place, cgal_placement_t& trsf) {
		return convert_placement(place->ccomponents(), trsf);
	}
}

bool ifcopenshell::geometry::kernels::CgalKernel::convert_openings(const IfcUtil::IfcBaseEntity * entity, const std::vector<std::pair<taxonomy::ptr, ifcopenshell::geometry::taxonomy::matrix4>>& openings, const IfcGeom::ConversionResults & entity_shapes, const ifcopenshell::geometry::taxonomy::matrix4 & entity_trsf, IfcGeom::ConversionResults & cut_shapes)
{
#ifdef IFOPSH_SIMPLE_KERNEL
	return false;
#else
	CGAL::Nef_nary_union_3<CGAL::Nef_polyhedron_3<Kernel_>> second_operand_collector;
	size_t second_operand_collector_size = 0;
	
	std::list<std::pair<const IfcUtil::IfcBaseClass*, std::list<cgal_shape_t>>> operands;

	std::list<const IfcUtil::IfcBaseClass*> second_operand_instances;
	std::list<cgal_shape_t> first_operands, second_operands;
	std::list<CGAL::Nef_polyhedron_3<Kernel_>> first_operands_nef, second_operands_nef;

	for (auto& shp : entity_shapes) {
		cgal_shape_t entity_shape = *std::static_pointer_cast<CgalShape>(shp.Shape());
		const auto& m = shp.Placement()->ccomponents();
		if (!m.isIdentity()) {
			cgal_placement_t trsf;
			convert_placement(m, trsf);
			for (auto &vertex : vertices(entity_shape)) {
				vertex->point() = vertex->point().transform(trsf);
			}
		}
		first_operands.push_back(entity_shape);


		CGAL::Nef_polyhedron_3<Kernel_> a;
		if (!preprocess_boolean_operand(entity, {}, {}, {}, entity_shape, a, PP_NONE /*PP_UNIFY_PLANES_INTERNALLY*/)) {
			return false;
		}

		first_operands_nef.push_back(a);
	}

	std::list<Kernel_::Plane_3> all_operand_planes;

	for (auto& op : openings) {
		auto opening_trsf = op.second;
		Eigen::Matrix4d relative = entity_trsf.ccomponents().inverse() * opening_trsf.ccomponents();
		opening_trsf = relative;

		ConversionResults opening_shapes;
		AbstractKernel::convert(op.first, opening_shapes);

		for (unsigned int i = 0; i < opening_shapes.size(); ++i) {
			cgal_shape_t entity_shape_unlocated = *std::static_pointer_cast<CgalShape>(opening_shapes[i].Shape());
			cgal_shape_t entity_shape(entity_shape_unlocated);
			auto gtrsf = opening_shapes[i].Placement();
			// @todo check
			Eigen::Matrix4d m = opening_trsf.ccomponents() * gtrsf->ccomponents();
			if (!m.isIdentity()) {
				cgal_placement_t trsf;
				convert_placement(m, trsf);
				for (auto &vertex : vertices(entity_shape)) {
					vertex->point() = vertex->point().transform(trsf);
				}
			}
			CGAL::Nef_polyhedron_3<Kernel_> nef;
			if (!preprocess_boolean_operand(op.first->instance->as<IfcUtil::IfcBaseClass>(), {}, {}, {}, entity_shape, nef, PP_NONE)) {
				continue;
			}

			// auto tree = build_halfspace_tree_decomposed(nef, all_operand_planes);

			second_operand_instances.push_back(op.first->instance->as<IfcUtil::IfcBaseClass>());
			second_operands.push_back(entity_shape);
			second_operands_nef.push_back(nef);
		}
	}

	auto iit = second_operand_instances.begin();
	auto pit = second_operands.begin();
	for (auto& nef : second_operands_nef) {
		auto& inst = *iit++;
		auto& entity_shape = *pit++;
		if (!preprocess_boolean_operand(inst, first_operands, first_operands_nef, all_operand_planes, entity_shape, nef, PP_MINKOWSKY_DILATE/*PP_SNAP_PLANES_TO_FIRST_OPERAND*/)) {
			continue;
		}
		second_operand_collector.add_polyhedron(nef);
		second_operand_collector_size++;
	}

	if (!second_operand_collector_size) {
		return false;
	}

	auto opening_union = second_operand_collector.get_union();

	auto it = entity_shapes.begin();
	auto nit = first_operands_nef.begin();
	for (auto& entity_shape : first_operands) {
		auto& a = *nit;

		if constexpr (false) {
			static int NN = 0;
			auto s = std::string("debug-first-operand-") + std::to_string(NN++) + ".off";
			std::ofstream ofs(s.c_str());
			ofs << entity_shape;
		}

		a -= opening_union;
		cgal_shape_t a_poly;

		try {
			a.convert_to_polyhedron(a_poly);
		} catch (...) {
			Logger::Message(Logger::LOG_ERROR, "Could not convert from Nef:", entity);
			return false;
		}

		cut_shapes.push_back(IfcGeom::ConversionResult(it->ItemId(), new CgalShape(a_poly), it->StylePtr()));
		it++;
		nit++;
	}

	return true;
#endif
}


bool CgalKernel::convert_impl(const taxonomy::extrusion::ptr extrusion, ConversionResults& results) {
	cgal_shape_t shape;
	if (!convert(extrusion, shape)) {
		return false;
	}
	results.emplace_back(ConversionResult(
		extrusion->instance->as<IfcUtil::IfcBaseEntity>()->id(),
		extrusion->matrix,
		new CgalShape(shape),
		extrusion->surface_style
	));
	return true;
}

bool CgalKernel::process_extrusion(const cgal_face_t& bottom_face, taxonomy::direction3::ptr direction, double height, cgal_shape_t& shape) {

	bool has_inner_bounds = !bottom_face.inner.empty();

	std::list<cgal_wire_t> faces_to_extrude;
	std::set<std::pair<size_t, size_t>> internal_edges;

	// CGAL::Cartesian_converter<CGAL::Epeck, CGAL::Simple_cartesian<double>> C;

	if (has_inner_bounds) {
		CGAL::Polygon_with_holes_2<Kernel_> pwh;
		CGAL::Aff_transformation_3<Kernel_> place;
		// @todo check for segment intersections, analogous to other places.
		// they are caught now below after triangulation.
		face_to_poly_with_holes(bottom_face, pwh, place);
		CGAL::Polygon_triangulation_decomposition_2<Kernel_> decompositor;
		std::list<CGAL::Polygon_2<Kernel_>> decom_polies;
		decompositor(pwh, std::back_inserter(decom_polies));

		int n_vertices = 0;
		std::map<Kernel_::Point_2, size_t> point_map;
		for (auto& p : decom_polies) {
			for (auto it = p.vertices_begin(); it != p.vertices_end(); ++it) {
				point_map.insert({ *it, point_map.size() });
				++n_vertices;
			}
		}

		std::map<std::pair<size_t, size_t>, std::pair<size_t, size_t>> external_edges;

		size_t i = 0;
		for (auto& p : decom_polies) {
			// this is always 3 given the usage of Polygon_triangulation_decomposition_2
			size_t n = std::distance(p.vertices_begin(), p.vertices_end());
			for (size_t j = 0; j < n; ++j) {
				auto k = (j + 1) % n;
				auto& p0 = *(p.vertices_begin() + j);
				auto& p1 = *(p.vertices_begin() + k);
				auto i0 = point_map.find(p0)->second;
				auto i1 = point_map.find(p1)->second;
				if (i0 > i1) {
					std::swap(i0, i1);
				}
				auto p = external_edges.insert({ { i0, i1 }, { i, j} });
				if (!p.second) {
					// Mark as internal before erasure in external
					// This is {i,j} at the time the edge use was inserted.
					internal_edges.insert(p.first->second);
					// not inserted, remove
					external_edges.erase(p.first);

					// @nb note the difference here in indices, {i0, i1} is point indices in
					// point_map. i is index in faces_to_extrude, j is segment index in wire.
					internal_edges.insert({ i, j });
				}
			}
			i++;
		}

		polygon_2_to_wire wire_builder(place);
		std::transform(decom_polies.begin(), decom_polies.end(), std::back_inserter(faces_to_extrude), wire_builder);
	} else {
		faces_to_extrude.push_front(bottom_face.outer);
	}

	std::list<cgal_face_t> face_list;

	int wi = 0;
	for (auto& w : faces_to_extrude) {

		face_list.push_back(cgal_face_t{ w });

		auto& fs = direction->ccomponents();
		cgal_direction_t dir(fs(0), fs(1), fs(2));

		int si = 0;
		for (std::vector<Kernel_::Point_3>::const_iterator current_vertex = w.begin();
			current_vertex != w.end();
			++current_vertex, ++si) {
			if (internal_edges.find({ wi, si }) != internal_edges.end()) {
				continue;
			}

			auto next_vertex = current_vertex + 1;
			if (next_vertex == w.end()) {
				next_vertex = w.begin();
			}

			cgal_face_t side_face;
			side_face.outer.push_back(*next_vertex);
			side_face.outer.push_back(*current_vertex);
			side_face.outer.push_back(*current_vertex + height * dir);
			side_face.outer.push_back(*next_vertex + height * dir);
			face_list.push_back(side_face);
		}

		cgal_face_t top_face;
		for (std::vector<Kernel_::Point_3>::const_reverse_iterator vertex = w.rbegin();
			vertex != w.rend();
			++vertex) {
			top_face.outer.push_back(*vertex + height * dir);
		} face_list.push_back(top_face);

		wi++;
	}

	shape = utils::create_polyhedron(face_list);
	// if (has_position) for (auto &vertex : vertices(shape)) vertex->point() = vertex->point().transform(trsf);
	return true;

	/*
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
			Logger::Message(Logger::LOG_ERROR, "IfcExtrudedAreaSolid: cannot subtract opening for:");
			return false;
		}
	}
	*/

	/*if (has_position) {
		// IfcSweptAreaSolid.Position (trsf) is an IfcAxis2Placement3D
		// and therefore has a unit scale factor
		nef_shape.transform(trsf);
	}*/

	/*
	try {
		nef_shape.convert_to_polyhedron(shape);
		return true;
	} catch (...) {
		Logger::Message(Logger::LOG_ERROR, "IfcExtrudedAreaSolid: cannot convert Nef to polyhedron for:");
		return false;
	}
	*/
}

bool CgalKernel::convert(const taxonomy::extrusion::ptr extrusion, cgal_shape_t &shape) {
	const double& height = extrusion->depth;
	if (height < settings_.get<settings::Precision>().get()) {
		Logger::Message(Logger::LOG_ERROR, "Non-positive extrusion height encountered for:", extrusion->instance);
		return false;
	}

	std::list<cgal_face_t> bottom_face;
	if (!convert(taxonomy::cast<taxonomy::face>(taxonomy::cast<taxonomy::face>(extrusion->basis)), bottom_face) || bottom_face.size() != 1) {
		return false;
	}

	return process_extrusion(bottom_face.front(), extrusion->direction, extrusion->depth, shape);
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
		++current_vertex) {
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
		++vertex) {
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
		++current_vertex) {
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
		++vertex) {
		top_face.outer.push_back(*vertex + dir);
	}

	face_list.push_back(top_face);

	return create_polyhedron(face_list);
}

#ifndef IFOPSH_SIMPLE_KERNEL

bool CgalKernel::thin_solid(const CGAL::Nef_polyhedron_3<Kernel_>& a, CGAL::Nef_polyhedron_3<Kernel_>& result) {
	// @todo this should be possible as a minkowski sum of facet & cube. rather than a set of boolean ops.

	auto precision_cube_ = precision_cube();

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

bool CgalKernel::preprocess_boolean_operand(const IfcUtil::IfcBaseClass* log_reference, const std::list<cgal_shape_t>& first_operands, const std::list<CGAL::Nef_polyhedron_3<Kernel_>>& first_operands_nef, const std::list<Kernel_::Plane_3>& all_operand_planes, const cgal_shape_t& shape_const, CGAL::Nef_polyhedron_3<Kernel_>& result, boolean_operand_preprocess proc) {
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
	} catch (CGAL::Failure_exception& e) {
		Logger::Notice(e);
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

	if (proc == PP_SNAP_POINTS_TO_FIRST_OPERAND) {
		static int NN = 0;
		typedef CGAL::AABB_face_graph_triangle_primitive<cgal_shape_t>                AABB_face_graph_primitive;
		typedef CGAL::AABB_traits<Kernel_, AABB_face_graph_primitive>               AABB_face_graph_traits;

		CGAL::AABB_tree<AABB_face_graph_traits> tree;

		for (auto& op : first_operands) {
			auto tm = op;

			CGAL::Polygon_mesh_processing::triangulate_faces(tm);
			CGAL::Polygon_mesh_processing::build_AABB_tree(tm, tree);

			std::transform(tm.facets_begin(), tm.facets_end(), tm.planes_begin(), [](auto& f) {
				auto h = f.halfedge();
				return CGAL::Plane_3<Kernel_>(h->vertex()->point(),
					h->next()->vertex()->point(),
					h->next()->next()->vertex()->point());
			});

			for (auto it = shape.vertices_begin(); it != shape.vertices_end(); ++it) {
				for (auto& x : first_operands) {
					// @nb snapping_tolerance 'snaps' the barycentric coords to 0 or 1
					// so that not only the point aligns to the face, but to an edge
					// as well. Snapping only to face would cause a rotation of line b:
					//         +
					//         |
					//         |
					//         |
					//         |
					//         |
					//      o-->
					//      |  |
					//      |  |
					//      |  |
					//     b|  |
					//      |  |
					//      |  |
					//      |  |
					//      o  |
					//  +---v--+
					auto ploc = CGAL::Polygon_mesh_processing::locate_with_AABB_tree(it->point(), tree, tm, CGAL::Polygon_mesh_processing::parameters::snapping_tolerance(1.e-5));
					/*std::stringstream ss;
					ss << std::setprecision(16) << ploc.second[0] << " " << ploc.second[1] << " " << ploc.second[2] << std::endl;
					auto sss = ss.str();
					std::wcout << sss.c_str() << std::endl;*/
					auto v = ploc.first->plane().orthogonal_vector();
					auto new_point = CGAL::Polygon_mesh_processing::construct_point(ploc, tm);
					if ((v * (new_point - it->point())) > 0) {
						auto vl = std::sqrt(CGAL::to_double(v.squared_length()));
						// @nb offsetting along plane normal is still necessary even after snapping
						it->point() = new_point + (v / vl) * 1.e-5;
					}
				}
			}
		}
		auto s = std::string("debug-operand-") + std::to_string(NN++) + ".off";
		std::ofstream ofs(s.c_str());
		ofs << shape;
	}

	try {
		result = CGAL::Nef_polyhedron_3<Kernel_>(shape);
	} catch (CGAL::Failure_exception& e) {
		Logger::Notice(e);
		Logger::Message(Logger::LOG_ERROR, "Could not convert geometry to Nef:", log_reference);
		return false;
	}

	if (proc == PP_SNAP_PLANES_TO_FIRST_OPERAND) {
		std::list<Kernel_::Plane_3> planes_fixed;
		std::list<Kernel_::Plane_3> temp;
		for (auto& nef : first_operands_nef) {
			// @todo eliminate this copy (= to remove const)
			auto nef_copy = nef;
			auto tree = build_halfspace_tree_decomposed(nef_copy, planes_fixed);  
		}
		{
			// @nb we snap internally as well...
			// @todo we can probably eliminate an evaluate() here
			{
				// @todo is it deterministic enough so that rebuilding the same tree is identical/compatible?
				auto tree = build_halfspace_tree_decomposed(result, temp);
				auto pmap = snap_halfspaces(all_operand_planes, 1.e-5);
				result = tree->map(pmap)->evaluate();
			}
			{
				std::list<Kernel_::Plane_3> planes;
				auto tree = build_halfspace_tree_decomposed(result, planes);
				auto pmap = snap_halfspaces_2(planes_fixed, planes, 1.e-5);
				result = tree->map(pmap)->evaluate();
			}
		}
	} else if (proc == PP_UNIFY_PLANES_INTERNALLY) {
		std::list<Kernel_::Plane_3> planes;
		auto tree = build_halfspace_tree_decomposed(result, planes);
		auto pmap = snap_halfspaces(planes, 1.e-6);
		std::wcout << tree->dump().c_str() << std::endl;
		auto mapped = tree->map(pmap);
		std::wcout << mapped->dump().c_str() << std::endl;

		{
			static int i = 1;
			auto x = (halfspace_tree_nary_branch<Kernel_>*)&*tree;
			int j = 0;
			for (auto& a : x->operands_) {
				auto A = a->evaluate();
				cgal_shape_t p;
				A.convert_to_Polyhedron(p);
				std::string fn = "debug-orig-" + std::to_string(i) + "-" + std::to_string(j++) + ".off";
				std::ofstream(fn.c_str()) << p;
			}
			i++;
		}
		{
			static int i = 1;
			auto x = (halfspace_tree_nary_branch<Kernel_>*)&*mapped;
			int j = 0;
			for (auto& a : x->operands_) {
				auto A = a->evaluate();
				cgal_shape_t p;
				A.convert_to_Polyhedron(p);
				std::string fn = "debug-mapped-" + std::to_string(i) + "-" + std::to_string(j++) + ".off";
				std::ofstream(fn.c_str()) << p;
			}
			i++;
		}

		result = mapped->evaluate();
	}

	if (proc == PP_MINKOWSKY_DILATE) {
		auto precision_cube_ = precision_cube();
		try {
			// @todo don't dilate in 3 dimensions but only in the XY plane, orthogonal to wall axis.
			result = CGAL::minkowski_sum_3(result, precision_cube_);
		} catch (CGAL::Failure_exception& e) {
			Logger::Notice(e);
			Logger::Message(Logger::LOG_ERROR, "Could not dilate boolean operand", log_reference);
			return false;
		}
	}

	

	/*
	{
		size_t vi = 0;
		static int i = 1;
		std::string fn = "debug-" + std::to_string(i) + "-" + std::to_string(vi) + ".off";
		auto ofs = std::make_unique<std::ofstream>(fn.c_str());
		while (write_to_obj(result, *ofs, vi++)) {
			fn = "debug-" + std::to_string(i++) + "-" + std::to_string(vi) + ".off";
			ofs = std::make_unique<std::ofstream>(fn.c_str());
		}
		i += 1;
	}
	*/

	try {
		cgal_shape_t convert_back;
		result.convert_to_polyhedron(convert_back);
	} catch (CGAL::Failure_exception& e) {
		Logger::Notice(e);
		Logger::Message(Logger::LOG_WARNING, "Final conversion will likely fail. Could not convert geometry from Nef:", log_reference);
	}

	return true;
}

#include <CGAL/Nef_nary_union_3.h>

#endif

bool CgalKernel::process_as_2d_polygon(const taxonomy::boolean_result::ptr br, std::list<CGAL::Polygon_2<Kernel_>>& loops, double& z0, double& z1) {
	// @todo can also be for other boolean operations, just depth/matrix operands are different
	if (br->operation != taxonomy::boolean_result::SUBTRACTION) {
		return false;
	}

	typedef std::pair<Eigen::Matrix4d*, taxonomy::extrusion::ptr> extrusion_pair;
	// @todo delete extrusion_pair.first

	auto& ops = br->children;

	std::vector<extrusion_pair> extrusions;
	std::transform(ops.begin(), ops.end(), std::back_inserter(extrusions), [](taxonomy::ptr op) {
		static std::pair<Eigen::Matrix4d*, taxonomy::extrusion::ptr> nptr = { nullptr, nullptr };
		Eigen::Matrix4d* m4 = nullptr;
		if (auto ex = taxonomy::dcast<taxonomy::extrusion>(op)) {
			return std::make_pair(m4, ex);
		}
		auto cl = taxonomy::dcast<taxonomy::collection>(op);
		if (!cl) return nptr;
		if ((cl)->children.size() != 1) return nptr;
		m4 = new Eigen::Matrix4d(cl->matrix->ccomponents());
		if (cl->children[0]->kind() == taxonomy::COLLECTION) {
			cl = taxonomy::cast<taxonomy::collection>(cl->children[0]);
			if ((cl)->children.size() != 1) {
				delete m4;
				return nptr;
			}
			(*m4) = (*m4) * cl->matrix->ccomponents();
		}
		if (cl->children[0]->kind() != taxonomy::EXTRUSION) {
			delete m4;
			return nptr;
		}
		auto ex = taxonomy::cast<taxonomy::extrusion>(cl->children[0]);
		return std::make_pair(m4, ex);
	});

	if (std::find_if(extrusions.begin(), extrusions.end(), [](extrusion_pair& p) {
		return p.second == nullptr;
	}) != extrusions.end()) {
		return false;
	}

	// op[i].matrix[2,0:3] = <0 0 1>
	Eigen::Vector3d Z(0., 0., 1.);
	if (std::find_if(extrusions.begin(), extrusions.end(), [&Z](extrusion_pair& p) {
		// @todo factor in p.first;
		auto ex = p.second;
		auto& m = ex->matrix->ccomponents();
		return std::abs(1. - std::abs(m.col(2).head<3>().dot(Z))) > 1.e-5;
	}) != extrusions.end()) {
		return false;
	}

	// | op[i].matrix[2,0:3] . op[i].direction | = 1
	if (std::find_if(extrusions.begin(), extrusions.end(), [](extrusion_pair& p) {
		auto ex = p.second;
		auto& d = ex->direction->ccomponents();
		auto& m = ex->matrix->ccomponents();
		return std::abs(1. - std::abs(m.col(2).head<3>().dot(d))) > 1.e-5;
	}) != extrusions.end()) {
		return false;
	}

	// op[0].depth <= op[i..n].depth
	const auto& op_0_depth = extrusions[0].second->depth;
	if (std::find_if(extrusions.begin() + 1, extrusions.end(), [&op_0_depth](extrusion_pair& p) {
		auto ex = p.second;
		return op_0_depth > ex->depth;
	}) != extrusions.end()) {
		return false;
	}

	const auto& op_0_matrix_2_3 = extrusions[0].second->matrix->ccomponents()(2, 3);
	if (std::find_if(extrusions.begin() + 1, extrusions.end(), [&op_0_matrix_2_3](extrusion_pair& p) {
		auto ex = p.second;
		return op_0_matrix_2_3 < ex->matrix->components()(2, 3);
	}) != extrusions.end()) {
		return false;
	}

	std::vector<cgal_wire_t> wires;
	try {
		std::transform(extrusions.begin(), extrusions.end(), std::back_inserter(wires), [this](extrusion_pair& p) {
			auto ex = p.second;
			auto ex_basis = taxonomy::cast<taxonomy::face>(ex->basis);
			if (ex_basis->children.size() == 1 && ex_basis->children[0]->kind() == taxonomy::LOOP) {
				auto l = (taxonomy::loop::ptr) ex_basis->children[0];
				cgal_wire_t w;
				cgal_placement_t trsf;
				convert_placement(ex->matrix, trsf);

				cgal_placement_t trsf2;
				if (p.first) {
					convert_placement(*p.first, trsf2);
				}

				/*
				std::array<std::array<double, 4>, 4> mat;
				for (int i = 0; i < 4; ++i) {
					for (int j = 0; j < 4; ++j) {
						mat[i][j] = CGAL::to_double(trsf.cartesian(i, j));
					}
				}
				*/

				if (convert(l, w)) {
					for (auto& pt : w) {
						// @todo figure out order.
						pt = pt.transform(trsf);
						if (p.first) {
							pt = pt.transform(trsf2);
						}
					}
					return w;
				}
			}
			throw std::runtime_error("failed to convert to polygon");
		});
	} catch (std::runtime_error&) {
		return false;
	}

	loops.clear();
	std::transform(wires.begin(), wires.end(), std::back_inserter(loops), wire_to_polygon_2);

	auto& op_0_matrix = extrusions[0].second->matrix->ccomponents();
	Eigen::Vector4d op_0_dir;
	op_0_dir << extrusions[0].second->direction->ccomponents(), 0;
	op_0_dir = op_0_matrix * op_0_dir;
	z0 = op_0_matrix_2_3;
	z1 = z0 + extrusions[0].second->depth * op_0_dir(2);

	if (z1 < z0) {
		std::swap(z0, z1);
	}

	return true;
}

#include <CGAL/Polygon_mesh_processing/measure.h>

namespace {
	bool orthogonal_edge_length(const cgal_shape_t& shape, const cgal_direction_t& face_normal, std::pair<Kernel_::FT, Kernel_::FT>& distances) {
		static double inf = 1.e9; // std::numeric_limits<double>::infinity();

		std::vector<double> lengths;

		distances = { +inf, -inf };

		for (const auto& e : edges(shape)) {
			const auto& p0 = e.halfedge()->vertex()->point();
			const auto& p1 = e.halfedge()->next()->vertex()->point();
			auto p01 = p1 - p0;
			auto p01_length = std::sqrt(CGAL::to_double(p01.squared_length()));
			p01 /= p01_length;
			auto dot = std::abs(CGAL::to_double(p01 * face_normal));
			if (dot > 1e-5) {
				if (dot < 0.9999) {
					return false;
				} else {
					lengths.push_back(p01_length);
					auto v = (p0 - CGAL::ORIGIN) * face_normal;
					if (v < distances.first) {
						distances.first = v;
					}
					if (v > distances.second) {
						distances.second = v;
					}
					v = (p1 - CGAL::ORIGIN) * face_normal;
					if (v < distances.first) {
						distances.first = v;
					}
					if (v > distances.second) {
						distances.second = v;
					}
				}
			}
		}

		std::sort(lengths.begin(), lengths.end());
		auto edge_len_diff = lengths.back() - lengths.front();

		std::wcout << "edge_len_diff " << edge_len_diff << std::endl;

		if (edge_len_diff > 1e-5) {
			return false;
		}

		return true;
	}
}

bool CgalKernel::process_as_2d_polygon(const std::list<std::list<std::pair<const IfcUtil::IfcBaseClass*, cgal_shape_t>>>& operands, std::list<CGAL::Polygon_2<Kernel_>>& loops, double& z0, double& z1) {
	if (operands.front().size() != 1) {
		return false;
	}
	auto& first_op = operands.front().front().second;

	cgal_shape_t::Facet_handle largest_face;
	Kernel_::FT largest_area = 0;

	for (auto& f : faces(first_op)) {
		auto area = CGAL::Polygon_mesh_processing::face_area(f, first_op);
		if (area > largest_area) {
			largest_area = area;
			largest_face = f;
		}
	}

	// @todo adapt newell() to work on facet circulator as well
	std::vector<cgal_point_t> f_points;
	CGAL::Polyhedron_3<Kernel_>::Halfedge_around_facet_const_circulator current_halfedge = largest_face->facet_begin();
	do {
		f_points.push_back(current_halfedge->vertex()->point());
		++current_halfedge;
	} while (current_halfedge != largest_face->facet_begin());

	auto fnorm = newell(f_points);
	fnorm /= std::sqrt(CGAL::to_double(fnorm.squared_length()));

	std::pair<Kernel_::FT, Kernel_::FT> operand_1_distance_along_normal;

	if (!orthogonal_edge_length(first_op, fnorm, operand_1_distance_along_normal)) {
		return false;
	}

	for (auto it = ++operands.begin(); it != operands.end(); ++it) {
		for (auto jt = it->begin(); jt != it->end(); ++jt) {
			auto& nth_op = jt->second;
			std::pair<Kernel_::FT, Kernel_::FT> operand_n_distance_along_normal;
			if (!orthogonal_edge_length(nth_op, fnorm, operand_n_distance_along_normal)) {
				return false;
			}

			std::wcout << CGAL::to_double(operand_n_distance_along_normal.first) << std::endl;
			std::wcout << CGAL::to_double(operand_n_distance_along_normal.second) << std::endl;
			std::wcout << CGAL::to_double(operand_1_distance_along_normal.first) << std::endl;
			std::wcout << CGAL::to_double(operand_1_distance_along_normal.second) << std::endl;

			if (operand_n_distance_along_normal.first > operand_1_distance_along_normal.first ||
				operand_n_distance_along_normal.second < operand_1_distance_along_normal.second) {
				return false;
			}
		}
	}

	std::wcout << "Process as 2D!!!" << std::endl;

	return true;
}

namespace {
	template <typename It, typename Fn>
	void project_onto_plane(const taxonomy::plane& p, It i, It j, Fn fn) {
		auto mi = p.matrix->ccomponents().inverse();
		Eigen::Vector4d v;
		std::for_each(i, j, [&mi, &v, &fn](const cgal_shape_t& shp) {
			for (auto& vv : vertices(shp)) {
				auto& p = vv->point();
				v = Eigen::Vector4d(CGAL::to_double(p.cartesian(0)),
					CGAL::to_double(p.cartesian(1)),
					CGAL::to_double(p.cartesian(2)),
					1.);
				v = mi * v;
				fn(v.head<3>());
			}
		});
	}
}

bool CgalKernel::convert_impl(const taxonomy::boolean_result::ptr br, ConversionResults& results) {
	double z0, z1;
	std::list<CGAL::Polygon_2<Kernel_>> loops;

	if (process_as_2d_polygon(br, loops, z0, z1)) {
		taxonomy::style::ptr first_item_style = nullptr;
		{
			auto gi = br->children[0];
			while (gi) {
				if (gi->surface_style) {
					first_item_style = gi->surface_style;
					break;
				}
				auto ci = taxonomy::dcast<taxonomy::collection>(gi);
				if (ci && ci->children.size() == 1) {
					gi = ci->children[0];
				} else {
					break;
				}
			}
		}

		std::list<CGAL::Polygon_with_holes_2<Kernel_>> pwhs;

		auto it = loops.begin();
		const auto& p = *it;

		CGAL::Polygon_with_holes_2<Kernel_> pwh(p, ++it, loops.end());
		CGAL::Gps_segment_traits_2<Kernel_> traits;
		if (!CGAL::are_holes_and_boundary_pairwise_disjoint(pwh, traits)) {
			// this is very slow.
			// the check is also slow...

			// It is enabled because in case of overlapping openings the
			// even-odd fill rule will result in incorrect results.
			// See for example the Duplex model roof.

			Logger::Notice("Holes are not disjoint");

			CGAL::Polygon_set_2<Kernel_> result;
			auto it = loops.begin();
			result.insert(*it++);
			for (; it != loops.end(); ++it) {
				result.difference(*it);
			}
			result.polygons_with_holes(std::back_inserter(pwhs));
		} else {
			pwhs.push_back(pwh);
		}

#if 0
		CGAL::Polygon_vertical_decomposition_2<Kernel_> decompositor;
#else
		CGAL::Polygon_triangulation_decomposition_2<Kernel_> decompositor;
#endif

		std::list<CGAL::Polygon_2<Kernel_>> decom_polies;
		for (auto& pwh : pwhs) {
			decompositor(pwh, std::back_inserter(decom_polies));
		}

		std::transform(decom_polies.begin(), decom_polies.end(), std::back_inserter(results), [this, &br, &z0, &z1, &first_item_style](const CGAL::Polygon_2<Kernel_>& p2) {
			cgal_face_t f;
			std::transform(
				p2.vertices_begin(),
				p2.vertices_end(),
				std::back_inserter(f.outer),
				[](const CGAL::Point_2<Kernel_>& p) {
				return CGAL::Point_3<Kernel_>(p.cartesian(0), p.cartesian(1), 0);
			}
			);

			cgal_shape_t shp;
			auto d = taxonomy::make<taxonomy::direction3>(0, 0, 1);
			process_extrusion(f, d, z1 - z0, shp);

			for (auto it = shp.vertices_begin(); it != shp.vertices_end(); ++it) {
				auto p = it->point();
				it->point() = cgal_point_t(p.cartesian(0), p.cartesian(1), p.cartesian(2) + z0);
			}

			return ConversionResult(
				br->instance->as<IfcUtil::IfcBaseEntity>()->id(),
				br->matrix,
				new CgalShape(shp),
				br->surface_style ? br->surface_style : first_item_style
			);
		});

		Logger::Notice("Processed boolean operation as 2d arrangement");

		return true;

	}


#ifdef IFOPSH_SIMPLE_KERNEL
	return false;
#else
	bool first = true;

	CGAL::Nef_polyhedron_3<Kernel_> a;
	CGAL::Nef_nary_union_3<CGAL::Nef_polyhedron_3<Kernel_>> second_operand_collector;
	size_t second_operand_collector_size = 0;

	taxonomy::style::ptr first_item_style = nullptr;

	std::list<std::pair<const IfcUtil::IfcBaseClass*, std::list<cgal_shape_t>>> operands;

	for (auto& c : br->children) {
		// AbstractKernel::convert(c, results);
		// continue;

		ConversionResults cr;

		operands.emplace_back();
		operands.back().first = c->instance->as<IfcUtil::IfcBaseClass>();

		if (c->kind() == taxonomy::SOLID && c->instance->declaration().is("IfcHalfSpaceSolid") && !first) {
			auto face = taxonomy::cast<taxonomy::solid>(c)->children[0]->children[0];

			if (face->basis == nullptr || face->basis->kind() != taxonomy::PLANE) {
				return false;
			}

			static double inf = 1.e9; //  std::numeric_limits<double>::infinity();
			static double eps = 1.e-5;

			double uvw_min[3] = { +inf, +inf, +inf };
			double uvw_max[3] = { -inf, -inf, -inf };
			auto& p = *taxonomy::cast<taxonomy::plane>(face->basis);
			project_onto_plane(p,
				operands.front().second.begin(),
				operands.front().second.end(),
				[&uvw_min, &uvw_max](const Eigen::Vector3d& p) {
				for (int i = 0; i < 3; ++i) {
					if (p(i) < uvw_min[i]) {
						uvw_min[i] = p(i);
					}
					if (p(i) > uvw_max[i]) {
						uvw_max[i] = p(i);
					}
				}
			});

			double wmin, wmax;
			if (face->orientation.get_value_or(false)) {
				wmin = 0.;
				wmax = uvw_max[2] + eps;
			} else {
				wmin = uvw_min[2] - eps;
				wmax = 0.;
			}

			Kernel_::Point_3 lower(uvw_min[0] - eps, uvw_min[1] - eps, wmin);
			Kernel_::Point_3 upper(uvw_max[0] + eps, uvw_max[1] + eps, wmax);
			cgal_shape_t box = utils::create_cube(lower, upper);
			cgal_placement_t pl;
			convert_placement(p.matrix, pl);
			for (auto& v : vertices(box)) {
				v->point() = v->point().transform(pl);
			}

			if (!face->children.empty()) {
				std::list<cgal_face_t> fs;
				if (!convert(face, fs) || fs.size() != 1) {
					return false;
				}
				// static 
				auto z = taxonomy::make<taxonomy::direction3>(0, 0, 1);
				cgal_shape_t poly;
				process_extrusion(fs.front(), z, 200, poly);
				for (auto& v : vertices(poly)) {
					v->point() = Kernel_::Point_3(
						v->point().cartesian(0),
						v->point().cartesian(1),
						v->point().cartesian(2) - 100
					);
				};
				cgal_placement_t trsf;
				convert_placement(face->matrix, trsf);
				for (auto& v : vertices(poly)) {
					v->point() = v->point().transform(trsf);
				}
				CGAL::Nef_polyhedron_3<Kernel_> poly_nef(poly);
				CGAL::Nef_polyhedron_3<Kernel_> box_nef(box);
				auto intersection = poly_nef * box_nef;
				cgal_shape_t intersection_poly;
				intersection.convert_to_polyhedron(intersection_poly);
				operands.back().second.push_back(intersection_poly);
			} else {
				operands.back().second.push_back(box);
			}

			continue;
		}

		AbstractKernel::convert(c, cr);

		if (first && br->operation == taxonomy::boolean_result::SUBTRACTION) {
			first_item_style = c->surface_style;
			if (!first_item_style && c->kind() == taxonomy::COLLECTION) {
				// @todo recursively right?
				first_item_style = taxonomy::cast<taxonomy::collection>(c)->children[0]->surface_style;
			}
		}

		for (auto it = cr.begin(); it != cr.end(); ++it) {
			cgal_shape_t entity_shape_unlocated = *std::static_pointer_cast<CgalShape>(it->Shape());
			cgal_shape_t entity_shape(entity_shape_unlocated);
			if (!it->Placement()->is_identity()) {
				cgal_placement_t trsf;
				convert_placement(it->Placement(), trsf);
				for (auto &vertex : vertices(entity_shape)) {
					vertex->point() = vertex->point().transform(trsf);
				}
			}
			operands.back().second.push_back(entity_shape);
		}

		first = false;
	}

	/*
	for (auto& li : operands) {
		for (auto& s : li.second) {
			results.emplace_back(ConversionResult(
				br->instance->data().id(),
				br->matrix,
				new CgalShape(s),
				br->surface_style ? br->surface_style : first_item_style
			));
		}
	}
	return true;
	*/

	/*
	// Another check in case operands are not extrusion is not fully implemented yet.
	if (process_as_2d_polygon(operands, loops, z0, z1)) {
		return true;
	}
	*/

	/*
	// debugging trick
	for (auto& p : operands) {
		for (auto& s : p.second) {
			results.emplace_back(ConversionResult(
				br->instance->data().id(),
				br->matrix,
				new CgalShape(s),
				br->surface_style ? br->surface_style : first_item_style
			));
		}
	}
	return true;
	*/

	first = true;

	std::list<cgal_shape_t> ops;
	std::list<CGAL::Nef_polyhedron_3<Kernel_>> nefops;
	std::list<Kernel_::Plane_3> all_operand_planes;

	for (auto& li : operands) {

		auto entity_instance = li.first;
		for (auto& entity_shape : li.second) {

			CGAL::Nef_polyhedron_3<Kernel_> nef;
			if (!preprocess_boolean_operand(entity_instance, ops, nefops, all_operand_planes, entity_shape, nef,
				// Snap boolean subtraction operands
				first ? PP_NONE : PP_MINKOWSKY_DILATE/*PP_SNAP_PLANES_TO_FIRST_OPERAND*/)) {
				continue;
			}

			ops.push_front(entity_shape);
			nefops.push_back(nef);

			if (first) {
				a = nef;
			} else {
				if (br->operation == taxonomy::boolean_result::SUBTRACTION) {
					second_operand_collector.add_polyhedron(nef);
					second_operand_collector_size++;
					// a -= nef;
				} else if (br->operation == taxonomy::boolean_result::INTERSECTION) {
					a *= nef;
				} else if (br->operation == taxonomy::boolean_result::UNION) {
					a += nef;
				}
			}
		}

		first = false;
	}

	if (br->operation == taxonomy::boolean_result::SUBTRACTION && second_operand_collector_size) {
		a -= second_operand_collector.get_union();
	}

	cgal_shape_t a_poly;

	// CGAL::Nef_polyhedron_3<Kernel_> b;
	// thin_solid(a, b);

	try {
		a.convert_to_polyhedron(a_poly);
	} catch (...) {
		Logger::Message(Logger::LOG_ERROR, "Could not convert geometry with openings from Nef:", br->instance);
		return false;
	}

	results.emplace_back(ConversionResult(
		br->instance->as<IfcUtil::IfcBaseEntity>()->id(),
		br->matrix,
		new CgalShape(a_poly),
		br->surface_style ? br->surface_style : first_item_style
	));
	return true;

#endif
}

PolyhedronBuilder::PolyhedronBuilder(std::list<cgal_face_t>* face_list) {
	this->face_list = face_list;
}

#include <CGAL/Polygon_mesh_processing/orient_polygon_soup.h>
// @todo shouldn't we just always use polygon_soup_to_polygon_mesh instead of the incremental builder?
#include <CGAL/Polygon_mesh_processing/polygon_soup_to_polygon_mesh.h>

void PolyhedronBuilder::operator()(CGAL::Polyhedron_3<Kernel_>::HalfedgeDS &hds) {
	// std::list<Kernel_::Point_3> points;
	std::map<Kernel_::Point_3, size_t> points;
	std::vector<std::vector<std::size_t>> facet_vertices;
	facet_vertices.reserve(face_list->size());
	CGAL::Polyhedron_incremental_builder_3<CGAL::Polyhedron_3<Kernel_>::HalfedgeDS> builder(hds, true);
	std::list<Kernel_::Point_3> unique_points;

	for (auto &face : *face_list) {

		if (face.inner.empty()) {

			facet_vertices.emplace_back();

			for (auto &point : face.outer) {
				auto p = points.insert({ point, points.size() });
				if (p.second) {
					unique_points.push_back(point);
				}
				facet_vertices.back().push_back(p.first->second);
			}

		} else {

			std::map<Kernel_::Point_2, size_t> points_2d;
			CGAL::Polygon_with_holes_2<Kernel_> pwh;
			CGAL::Aff_transformation_3<Kernel_> place;
			face_to_poly_with_holes(face, pwh, place);

			// we assume the pwh constructor leaves points in order
			// wouldn't it be nice to have the equivalent of Python's zip()
			{
				auto it = pwh.outer_boundary().vertices_begin();
				auto jt = face.outer.begin();
				for (; it != pwh.outer_boundary().vertices_end(); ++it, ++jt) {
					auto p = points.insert({ *jt, points.size() });
					if (p.second) {
						unique_points.push_back(*jt);
					}
					points_2d.insert({ *it, p.first->second });
				}
			}
			auto it = pwh.holes_begin();
			auto kt = face.inner.begin();
			for (; it != pwh.holes_end(); ++it, ++kt) {
				auto jt = it->vertices_begin();
				auto lt = kt->begin();
				for (; jt != it->vertices_end(); ++jt, ++lt) {
					auto p = points.insert({ *lt, points.size() });
					if (p.second) {
						unique_points.push_back(*lt);
					}
					points_2d.insert({ *jt, p.first->second });
				}
			}

			CGAL::Polygon_triangulation_decomposition_2<Kernel_> decompositor;
			std::list<CGAL::Polygon_2<Kernel_>> decom_polies;
			decompositor(pwh, std::back_inserter(decom_polies));

			for (auto& p : decom_polies) {
				facet_vertices.emplace_back();
				for (auto it = p.vertices_begin(); it != p.vertices_end(); ++it) {
					auto pit = points_2d.find(*it);
					if (pit == points_2d.end()) {
						// Likely there are intersections in the polygonal boundaries.
						// For now let's just skip over the triangle. We can also use
						// the Aff_transformation_3 stored in place to convert the 2d
						// coords back to 3d.
						Logger::Warning("Ignoring triangulated facet with novel point likely due to self-intersections");
						facet_vertices.erase(facet_vertices.end() - 1);
						break;
					}
					facet_vertices.back().push_back(pit->second);
				}
			}
		}
	}

	/*
	// We don't do this ourselves anymore, but defer this to is_polygon_soup_a_polygon_mesh()
	bool valid_orientation = true;
	std::set<std::pair<size_t, size_t>> added_edges;
	for (size_t fi = 0; fi < facet_vertices.size(); ++fi) {
		auto& f = facet_vertices[fi];
		for (size_t i = 0; i < f.size(); ++i) {
			auto p = std::pair<size_t, size_t>(f[i], f[(i + 1) % f.size()]);
			if (added_edges.find(p) != added_edges.end()) {
				valid_orientation = false;
				break;
			}
			added_edges.insert(p);
		}
		if (!valid_orientation) {
			break;
		}
	}
	*/

	// if (!valid_orientation) {
	from_soup.emplace();



	// @todo ugh
	std::vector<Kernel_::Point_3> unique_points_as_vector(unique_points.begin(), unique_points.end());

	if (!CGAL::Polygon_mesh_processing::is_polygon_soup_a_polygon_mesh(facet_vertices)) {
		// @todo seems to return false now, almost always?
		// Logger::Warning("Reoriented polygonal surface");
		CGAL::Polygon_mesh_processing::orient_polygon_soup(unique_points_as_vector, facet_vertices);
	}
	CGAL::Polygon_mesh_processing::polygon_soup_to_polygon_mesh(unique_points_as_vector, facet_vertices, *from_soup);

	return;
	// }
/*
	std::vector<size_t> facet_indices_to_delete;
	std::set<std::pair<size_t, size_t>> added_edges;
	for (size_t fi = 0; fi < facet_vertices.size(); ++fi) {
		auto& f = facet_vertices[fi];
		bool reoriented = false, valid = true;

	check_edge_existence:
		for (size_t i = 0; i < f.size(); ++i) {
			auto p = std::pair<size_t, size_t>(f[i], f[(i + 1) % f.size()]);
			if (added_edges.find(p) != added_edges.end()) {
				if (reoriented) {
					facet_indices_to_delete.push_back(fi);
					Logger::Notice("Removed facet");
					valid = false;
					break;
				} else {
					std::reverse(f.begin(), f.end());
					Logger::Notice("Reversed facet");
					reoriented = true;
					goto check_edge_existence;
				}
			}
		}
		if (valid) {
			for (size_t i = 0; i < f.size(); ++i) {
				auto p = std::pair<size_t, size_t>(f[i], f[(i + 1) % f.size()]);
				added_edges.insert(p);
			}
		}
	}

	std::reverse(facet_indices_to_delete.begin(), facet_indices_to_delete.end());
	for (auto& fi : facet_indices_to_delete) {
		facet_vertices.erase(facet_vertices.begin() + fi);
	}
*/

/*
// We just always use polygon_soup_to_polygon_mesh() to now.
// @todo figure out the downsides of this approach.

builder.begin_surface(points.size(), facet_vertices.size()); // , 0, CGAL::Polyhedron_incremental_builder_3<CGAL::Polyhedron_3<Kernel_>::HalfedgeDS>::ABSOLUTE_INDEXING);

for (auto& point : unique_points) {
	builder.add_vertex(point);
}

for (auto &facet : facet_vertices) {
	builder.begin_facet();
	//      std::cout << "Adding facet ";
	for (auto &vertex : facet) {
		//        std::cout << vertex << " ";
		builder.add_vertex_to_facet(vertex);
	}
	//      std::cout << std::endl;
	builder.end_facet();
}

builder.end_surface();
*/
}
