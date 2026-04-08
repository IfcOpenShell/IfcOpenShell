/****************************************************************************
 * SVG fill									        					    *
 * 																			*
 * Copyright(C) 2020 AECgeeks and Bimforce								    *
 * 																		    *
 * This program is free software; you can redistribute it and/or		    *
 * modify it under the terms of the GNU Lesser General Public			    *
 * License as published by the Free Software Foundation; either			    *
 * version 3 of the License, or (at your option) any later version.		    *
 * 																		    *
 * This program is distributed in the hope that it will be useful,		    *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of		    *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU	    *
 * Lesser General Public License for more details.						    *
 * 																		    *
 * You should have received a copy of the GNU Lesser General Public License *
 * along with this program; if not, write to the Free Software Foundation,  *
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.	    *
 ****************************************************************************/

#include "svgfill.h"

#include <libxml/parser.h>

#include <svgpp/svgpp.hpp>
#include <svgpp/policy/xml/libxml2.hpp>

#include <CGAL/Cartesian.h>
#include <CGAL/MP_Float.h>
#include <CGAL/Quotient.h>
#include <CGAL/Arr_segment_traits_2.h>
#include <CGAL/Arrangement_2.h>
#include <CGAL/Polygon_2.h>
#include <CGAL/Polygon_with_holes_2.h>
#include <CGAL/Polygon_triangulation_decomposition_2.h>
#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

#include <random>

using namespace svgpp;

class Context
{
private:
	size_t depth_ = 0;
	int enabled_at_ = -1;
	svgfill::point_2 start_, xy_;

public:
	boost::optional<std::string> class_name;
	std::vector<std::vector<svgfill::line_segment_2>> segments;

	void on_enter_element(tag::element::any)
	{
		++depth_;
	}

	void on_enter_element(tag::element::g)
	{
		++depth_;
		if (enabled_at_ == -1 && !class_name.is_initialized()) {
			enabled_at_ = depth_;
			segments.emplace_back();
		}
	}

	void on_exit_element()
	{
		if (depth_-- == enabled_at_) {
			enabled_at_ = -1;
		}
	}

	template<class Str>
	void set(tag::attribute::id, Str const & s) {
	}

	template<class Str>
	void set(tag::attribute::class_, Str const & s) {
		if (enabled_at_ == -1 && class_name.is_initialized() && std::string(s.begin(), s.size()).find(*class_name) != std::string::npos) {
			enabled_at_ = depth_;
			segments.emplace_back();
		}
	}

	void transform_matrix(const boost::array<double, 6> & matrix)
	{}

	void path_move_to(double x, double y, tag::coordinate::absolute)
	{
		start_ = xy_ = { x, y };
	}

	void path_line_to(double x, double y, tag::coordinate::absolute)
	{
		if (enabled_at_ != -1) {
			svgfill::point_2 next{ x, y };
			segments.back().push_back({ xy_, next });
			xy_ = next;
		}
	}

	void path_cubic_bezier_to(
		double x1, double y1,
		double x2, double y2,
		double x, double y,
		tag::coordinate::absolute) {}

	void path_quadratic_bezier_to(
		double x1, double y1,
		double x, double y,
		tag::coordinate::absolute) {}

	void path_elliptical_arc_to(
		double rx, double ry, double x_axis_rotation,
		bool large_arc_flag, bool sweep_flag,
		double x, double y,
		tag::coordinate::absolute) {}

	void path_close_subpath() {
		if (enabled_at_ != -1) {
			segments.back().push_back({ xy_, start_ });
		}
	}

	void path_exit() {}
};

typedef
boost::mpl::set<
	// SVG Structural Elements
	tag::element::svg,
	tag::element::g,
	// SVG Shape Elements
	tag::element::circle,
	tag::element::ellipse,
	tag::element::line,
	tag::element::path,
	tag::element::polygon,
	tag::element::polyline,
	tag::element::rect
>::type processed_elements_t;

// This cryptic code just merges predefined sequences traits::shapes_attributes_by_element
// and traits::viewport_attributes with tag::attribute::transform and tag::attribute::xlink::href 
// attributes into single MPL sequence
typedef
boost::mpl::fold<
	boost::mpl::protect<
	traits::shapes_attributes_by_element
	>,
	boost::mpl::set<
	tag::attribute::id,
	tag::attribute::class_
	>::type,
	boost::mpl::insert<boost::mpl::_1, boost::mpl::_2>
>::type processed_attributes_t;

bool svgfill::svg_to_line_segments(const std::string& data, const boost::optional<std::string>& class_name, std::vector<std::vector<line_segment_2>>& segments)
{
	Context context;
	context.class_name = class_name;

	xmlDoc* doc = xmlReadMemory(data.c_str(), data.size(), nullptr, nullptr, 0);
	xmlNode* elem = xmlDocGetRootElement(doc);

	try {
		document_traversal<
			processed_elements<processed_elements_t>,
			processed_attributes<processed_attributes_t>
		>::load_document(elem, context);
	}
	catch (std::exception& e) {
		std::cerr << e.what() << std::endl;
		return false;
	}

	segments = context.segments;

	return true;
}

bool svgfill::line_segments_to_polygons(solver s, double eps, const std::vector<std::vector<line_segment_2>>& segments, std::vector<std::vector<polygon_2>>& polygons)
{
	std::function<void(float)> fn = [](float f) {};
	return line_segments_to_polygons(s, eps, segments, polygons, fn);
}

bool svgfill::svg_to_polygons(const std::string& data, const boost::optional<std::string>& class_name, std::vector<polygon_2>& polygons) {
	Context context;
	context.class_name = class_name;
	xmlDoc* doc = xmlReadMemory(data.c_str(), data.size(), nullptr, nullptr, 0);
	xmlNode* elem = xmlDocGetRootElement(doc);

	try {
		document_traversal<
			processed_elements<processed_elements_t>,
			processed_attributes<processed_attributes_t>
		>::load_document(elem, context);
	} catch (std::exception& e) {
		std::cerr << e.what() << std::endl;
		return false;
	}
	std::function<void(float)> fn = [](float f) {};
	std::vector<std::vector<polygon_2>> ps;
	if (!line_segments_to_polygons(svgfill::EXACT_PREDICATES, 0., context.segments, ps, fn)) {
		return false;
	}
	if (ps.empty()) {
		return false;
	}
	for (auto& p : ps) {
		polygons.insert(polygons.end(), p.begin(), p.end());
	}
	return true;
}

template <typename Kernel>
class cgal_arrangement : public svgfill::abstract_arrangement {
	typedef CGAL::Arr_segment_traits_2<Kernel> Traits_2;
	typedef typename Traits_2::Point_2 Point_2;
	typedef typename Traits_2::X_monotone_curve_2 Segment_2;
	typedef CGAL::Arrangement_2<Traits_2> Arrangement_2;
	typedef CGAL::Polygon_2<Kernel> Polygon_2;
	typedef CGAL::Polygon_with_holes_2<Kernel> Polygon_wh_2;
	typedef typename Arrangement_2::Inner_ccb_const_iterator Inner_ccb_const_iterator;
	typedef typename Arrangement_2::Ccb_halfedge_const_circulator Ccb_halfedge_const_circulator;
	typedef typename Arrangement_2::Halfedge_handle Halfedge_handle;
	typedef typename Arrangement_2::Face_handle Face_handle;

	Polygon_2 circ_to_poly(Ccb_halfedge_const_circulator circ)
	{
		Polygon_2 poly;
		auto curr = circ;
		do {
			if (poly.size() == 0 || (*(poly.end() - 1)) != curr->source()->point()) {
				poly.push_back(curr->source()->point());
			}
		} while (++curr != circ);
		return poly;
	}

	CGAL::Triangle_2<Kernel> poly_to_triangle(const Polygon_2& poly)
	{
		auto n = std::distance(poly.vertices_begin(), poly.vertices_end());
		if (n != 3) {
			throw std::runtime_error("Unexpected number of points in polygon");
		}
		auto p = *poly.vertices_begin();
		auto q = *next(poly.vertices_begin(), 1);
		auto r = *next(poly.vertices_begin(), 2);
		return CGAL::Triangle_2<Kernel>(p, q, r);
	}

	Polygon_wh_2 circ_to_poly(Ccb_halfedge_const_circulator circ, Inner_ccb_const_iterator a, Inner_ccb_const_iterator b)
	{
		Polygon_wh_2 poly(circ_to_poly(circ));
		for (auto it = a; it != b; ++it) {
			poly.add_hole(circ_to_poly(*it));
		}
		return poly;
	}

	svgfill::point_2 create_point(const Point_2& pt)
	{
		return svgfill::point_2{
			CGAL::to_double(pt.cartesian(0)),
			CGAL::to_double(pt.cartesian(1)),
		};
	}

	void set_point_inside(const Polygon_wh_2& inpoly, svgfill::polygon_2& outpoly)
	{
		/*
		std::cout << std::endl;
		for (auto& p : inpoly.outer_boundary()) {
			std::cout << " " << p;
		}
		std::cout << std::endl;
		*/
		// create Delaunay triangulation and return the centroid of the largest triangle.
		CGAL::Polygon_triangulation_decomposition_2<Kernel> decompositor;
		std::list<Polygon_2> decom_polies;
		decompositor(inpoly, std::back_inserter(decom_polies));
		decom_polies.sort([](const Polygon_2& a, const Polygon_2& b) {
			return a.area() > b.area();
		});
		if (!decom_polies.empty()) {
			const Polygon_2& largest = decom_polies.front();
			auto triangle = poly_to_triangle(largest);
			/*
			for (auto& p : decom_polies) {
				std::cout << "a " << CGAL::to_double(poly_to_triangle(largest).area()) << std::endl;
			}
			std::cout << "triangle area " << CGAL::to_double(triangle.area()) << std::endl;
			*/
			outpoly.point_inside = create_point(CGAL::centroid(triangle));
		}
	}

	Arrangement_2 arr;
	float total, i;

public:
	bool operator()(double eps, const std::vector<svgfill::line_segment_2>& segments, std::function<void(float)>& progress) {
		i = 0;
		total = segments.size() + segments.size() / 2;

		for (auto& l : segments) {
			Point_2 a(l[0][0], l[0][1]);
			Point_2 b(l[1][0], l[1][1]);
			if (a == b) {
				continue;
			}
			if (eps != 0.) {
				auto ab = b - a;
				ab /= std::sqrt(CGAL::to_double(ab.squared_length()));
				// This appears to work better generally, slightly nudge the
				// end points to make sure segments intersect.
				a -= ab * eps;
				b += ab * eps;
			}
			Segment_2 seg(a, b);
			CGAL::insert(arr, seg);

			if (progress) {
				progress(i++ / total);
			}
		}

		return true;
	}

	void remove_duplicates(svgfill::loop_2& l) {
		auto norm2 = [](auto& a, auto& b) {
			auto dx = a[0] - b[0];
			auto dy = a[1] - b[1];
			return std::sqrt(dx * dx + dy * dy);
		};

		while (l.size() > 1 && l.front() == l.back()) {
			l.pop_back();
		}

		if (l.size() > 1) {
			auto it = l.begin();
			auto next_it = std::next(it);

			while (next_it != l.end()) {
				if (norm2(*it, *next_it) < 1.e-8) {
					next_it = l.erase(next_it);
					// 'it' remains the same; 'next_it' now points to the next element
				} else {
					// Move both iterators forward
					++it;
					++next_it;
				}
			}
		}
	}

	bool write(std::vector<svgfill::polygon_2>& polygons, std::function<void(float)>& progress) {
		std::vector<Polygon_wh_2> ps;
		ps.reserve(std::distance(arr.faces_begin(), arr.faces_end()));

		for (auto it = arr.faces_begin(); it != arr.faces_end(); ++it) {
			const auto& f = *it;
			if (!f.is_unbounded()) {
				ps.push_back(circ_to_poly(
					f.outer_ccb(),
					f.inner_ccbs_begin(),
					f.inner_ccbs_end()
				));
			}

			if (progress) {
				progress(i++ / total);
			}
		}

		// Sort polygons (only taking into account outer boundary) to have inner
		// loops drawn over outer boundaries. In SVG draw order is defined by
		// position in the tree.
		// @nb we do now add the inner boundaries to the path as well.
		/*
		std::sort(ps.begin(), ps.end(), [](const Polygon_wh_2& a, const Polygon_wh_2& b) {
			return a.outer_boundary().area() > b.outer_boundary().area();
		});
		*/

		polygons.reserve(ps.size());



		std::transform(ps.begin(), ps.end(), std::back_inserter(polygons), [this, &progress](const Polygon_wh_2& p) {
			svgfill::polygon_2 p2;
			std::transform(p.outer_boundary().vertices_begin(), p.outer_boundary().vertices_end(), std::back_inserter(p2.boundary), [this](const Point_2& pt) {
				return create_point(pt);
			});

			/*
			static int NN = 0;
			std::cout << NN++ << std::endl;
			for (auto& p : p2.boundary) {
				std::cout << std::setprecision(20) << p[0] << "," << p[1] << " ";
			}
			std::cout << std::endl;
			*/

			// duplicates need to be removed after conversion from epeck to double
			remove_duplicates(p2.boundary);

			/*
			std::cout << "> " << std::endl;
			for (auto& p : p2.boundary) {
				std::cout << std::setprecision(20) << p[0] << "," << p[1] << " ";
			}
			std::cout << std::endl;
			*/

			std::transform(p.holes_begin(), p.holes_end(), std::back_inserter(p2.inner_boundaries), [this](const Polygon_2& poly) {
				svgfill::loop_2 lp;
				std::transform(poly.vertices_begin(), poly.vertices_end(), std::back_inserter(lp), [this](const Point_2& pt) {
					return create_point(pt);
				});
				remove_duplicates(lp);
				return lp;
			});
			set_point_inside(p, p2);

			if (progress) {
				progress(i++ / total);
			}

			return p2;
		});

		return true;
	}

	std::vector<int> get_face_pairs() {
		std::vector<int> ps;
		ps.reserve(arr.number_of_edges() * 2);
		size_t n = 0;

		std::map<Face_handle, size_t> face_to_bounded_index;
		for (auto it = arr.faces_begin(); it != arr.faces_end(); ++it) {
			if (!it->is_unbounded()) {
				face_to_bounded_index[it] = face_to_bounded_index.size();
			}
		}

		for (auto it = arr.edges_begin(); it != arr.edges_end(); ++it, ++n) {
			auto v0 = it->source()->point();
			double v0x = CGAL::to_double(v0.cartesian(0));
			double v0y = CGAL::to_double(v0.cartesian(1));
			auto v1 = it->target()->point();
			double v1x = CGAL::to_double(v1.cartesian(0));
			double v1y = CGAL::to_double(v1.cartesian(1));
			double l = std::sqrt((v1x - v0x) * (v1x - v0x) + (v1y - v0y) * (v1y - v0y));
			// std::cout << n << " l " << l << std::endl;
			bool emitted = false;
			if (l > 1.) {
				// std::cout << std::to_string(n) << " " << v0x << " " << v0y << std::endl;
				// std::cout << std::string(std::to_string(n).size(), ' ') << " " << v1x << " " << v1y << std::endl;

				auto afit = face_to_bounded_index.find(it->face());
				auto bfit = face_to_bounded_index.find(it->twin()->face());

				if (afit != face_to_bounded_index.end() && bfit != face_to_bounded_index.end()) {
					ps.push_back(afit->second);
					ps.push_back(bfit->second);
					emitted = true;
				}
			}
			
			if (!emitted) {
				ps.push_back(-1);
				ps.push_back(-1);
			}
		}
		return ps;
	}

	void merge(const std::vector<int>& edge_indices) {
		if (edge_indices.empty()) {
			return;
		}

		std::list<Halfedge_handle> to_remove;
		auto eit = edge_indices.begin();
		size_t n = 0;
		for (auto it = arr.edges_begin(); it != arr.edges_end(); ++it, ++n) {
			if (n == *eit) {
				++eit;
				to_remove.push_back(it);
				if (eit == edge_indices.end()) {
					break;
				}
			}
		}
		
		for (auto& h : to_remove) {
			/*
			auto v0 = h->source()->point();
			std::cout << CGAL::to_double(v0.cartesian(0)) << " " << CGAL::to_double(v0.cartesian(1)) << std::endl;
			auto v1 = h->target()->point();
			std::cout << CGAL::to_double(v1.cartesian(0)) << " " << CGAL::to_double(v1.cartesian(1)) << std::endl << std::endl;
			*/
			arr.remove_edge(h);
		}
	}

	size_t num_edges() {
		return arr.number_of_edges();
	}

	size_t num_faces() {
		return arr.number_of_faces();
	}
};

bool svgfill::line_segments_to_polygons(solver s, double eps, const std::vector<std::vector<line_segment_2>>& segment_groups, std::vector<std::vector<polygon_2>>& polygons, std::function<void(float)>& progress)
{
	bool b = false;
	for (auto& segments : segment_groups) {
		context ctx(s, eps, progress);
		ctx.add(segments);
		if (ctx.build()) {
			ctx.write(polygons);
			b = true;
		}
	}
	return b;
}

namespace {
	std::string format_pt(const svgfill::point_2& p) {
		std::ostringstream oss;
		oss << std::setprecision(std::numeric_limits<double>::max_digits10);
		oss << p[0] << "," << p[1];
		return oss.str();
	}

	std::string format_poly(const svgfill::loop_2& p) {
		std::ostringstream oss;
		for (auto it = p.begin(); it != p.end(); ++it) {
			oss << ((it == p.begin()) ? "M" : " L");
			oss << format_pt(*it);
		}
		oss << " Z";
		return oss.str();
	}
}

std::string svgfill::polygons_to_svg(const std::vector<std::vector<polygon_2>>& polygons, bool random_color) {
	std::random_device rd;
	std::mt19937 mt(rd());
	std::uniform_int_distribution<size_t> dist(0, 360);

	std::ostringstream oss;

	oss << "<svg xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" xmlns:ifc=\"http://www.ifcopenshell.org/ns\">";
	oss << "<style type=\"text/css\">";
	oss << "	<![CDATA[";
	oss << "		path {";
	oss << "			stroke: #222222;";
	oss << "			fill: #444444;";
	oss << "		}";
	oss << "	]]>";
	oss << "</style>";

	for (auto& g : polygons) {
		oss << "<g>";
		for (auto& p : g) {
			const int h = dist(mt);
			const int s = 50;
			const int l = 50;
			std::string style;
			if (random_color) {
				std::ostringstream oss;
				oss << "style = \"fill: hsl(" << h << "," << s << "%, " << l << "%)\"";
				style = oss.str();
			}
			oss << "<path d=\"" << format_poly(p.boundary);
			for (auto& inner : p.inner_boundaries) {
				oss << " " << format_poly(inner);
			}
			oss << "\" " << style << " ifc:pointInside=\"" << format_pt(p.point_inside) << "\"/>";
		}
		oss << "</g>";
	}

	oss << "</svg>";

	return oss.str();
}


std::string svgfill::polygons_to_svg(const std::vector<polygon_2>& polygons, bool random_color) {
	std::vector<std::vector<polygon_2>> pps = { polygons };
	return polygons_to_svg(pps, random_color);
}

void svgfill::context::add(const std::vector<line_segment_2>& segments) {
	segments_.insert(segments_.end(), segments.begin(), segments.end());
}

bool svgfill::context::build() {
	if (solver_ == CARTESIAN_DOUBLE) {
		arr_ = new cgal_arrangement<CGAL::Cartesian<double>>;
	} else if (solver_ == CARTESIAN_QUOTIENT) {
		arr_ = new cgal_arrangement<CGAL::Cartesian<CGAL::Quotient<CGAL::MP_Float>>>;
	} else if (solver_ == FILTERED_CARTESIAN_QUOTIENT) {
		arr_ = new cgal_arrangement<CGAL::Filtered_kernel<CGAL::Cartesian<CGAL::Quotient<CGAL::MP_Float>>>>;
	} else if (solver_ == EXACT_PREDICATES) {
		arr_ = new cgal_arrangement<CGAL::Epick>;
	} else if (solver_ == EXACT_CONSTRUCTIONS) {
		arr_ = new cgal_arrangement<CGAL::Epeck>;
	}
	return (*arr_)(eps_, segments_, progress_);
}

void svgfill::context::merge(const std::vector<int>& edge_indices) {
	arr_->merge(edge_indices);
}

void svgfill::context::write(std::vector<std::vector<polygon_2>>& p) {
	std::vector<polygon_2> polygons;
	arr_->write(polygons, progress_);
	p.push_back(polygons);
}
