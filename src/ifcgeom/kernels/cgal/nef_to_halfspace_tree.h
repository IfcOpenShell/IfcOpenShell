/*******************************************************************************
*                                                                              *
* This file is part of 'nef to halfspace tree' (NTHST).                        *
*                                                                              *
* Copyright (C) 2023 Thomas Krijnen <thomas@aecgeeks.com>                      *
*                                                                              *
* NTHST is free software: you can redistribute it and/or modify                *
* it under the terms of the Lesser GNU General Public License as published by  *
* the Free Software Foundation, either version 3.0 of the License, or          *
* (at your option) any later version.                                          *
*                                                                              *
* NTHST is distributed in the hope that it will be useful,                     *
* but WITHOUT ANY WARRANTY; without even the implied warranty of               *
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
* Lesser GNU General Public License for more details.                          *
*                                                                              *
* You should have received a copy of the Lesser GNU General Public License     *
* along with this program. If not, see <http://www.gnu.org/licenses/>.         *
*                                                                              *
********************************************************************************/

#ifndef NEF_TO_HALFSPACE_TREE_H
#define NEF_TO_HALFSPACE_TREE_H

#include <CGAL/Nef_polyhedron_3.h>
#include <CGAL/convex_decomposition_3.h>
#include <CGAL/Nef_nary_union_3.h>
#include <CGAL/Nef_nary_intersection_3.h>
#include <CGAL/Polygon_mesh_processing/polygon_soup_to_polygon_mesh.h>
#include <CGAL/Polygon_mesh_processing/triangulate_hole.h>
#include <CGAL/Polygon_triangulation_decomposition_2.h>
#include <CGAL/Polygon_2.h>
#include <CGAL/Polygon_with_holes_2.h>

#include <CGAL/Epick_d.h>
#include <CGAL/Kd_tree.h>
#include <CGAL/Search_traits_d.h>
#include <CGAL/Kd_tree.h>
#include <CGAL/Fuzzy_sphere.h>

#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/connected_components.hpp>
#include <boost/graph/breadth_first_search.hpp>
#include <boost/graph/graphviz.hpp>
#include <boost/iterator/indirect_iterator.hpp>
#include <boost/iterator/transform_iterator.hpp>
#include <boost/graph/copy.hpp>

#include <list>
#include <queue>
#include <memory>
#include <functional>

// Functor to lexicographically sort Plane_3
template <typename Kernel>
struct PlaneLess {
	bool operator()(const typename Kernel::Plane_3& lhs, const typename Kernel::Plane_3& rhs) const {
		auto lhs_a = lhs.a();
		auto lhs_b = lhs.b();
		auto lhs_c = lhs.c();
		auto lhs_d = lhs.d();
		auto rhs_a = rhs.a();
		auto rhs_b = rhs.b();
		auto rhs_c = rhs.c();
		auto rhs_d = rhs.d();
		return std::tie(lhs_a, lhs_b, lhs_c, lhs_d) < std::tie(rhs_a, rhs_b, rhs_c, rhs_d);
	}
};

// Functor to hash Plane_3
template <typename Kernel>
struct PlaneHash {
	size_t operator()(const CGAL::Plane_3<Kernel>& plane) const noexcept
	{
		// @todo why can I only get this to work on double?
		std::hash<double> h;
		std::size_t result = h(CGAL::to_double(plane.a()));
		boost::hash_combine(result, h(CGAL::to_double(plane.b())));
		boost::hash_combine(result, h(CGAL::to_double(plane.c())));
		boost::hash_combine(result, h(CGAL::to_double(plane.d())));
		return result;
	}
};

// Utility function to return Nef facet information as string
template <typename Kernel>
std::string dump_facet(typename CGAL::Nef_polyhedron_3<Kernel>::Halffacet_const_handle h) {
	typedef typename CGAL::Nef_polyhedron_3<Kernel>::SHalfedge_const_handle SHalfedge_const_handle;
	typedef typename CGAL::Nef_polyhedron_3<Kernel>::SHalfedge_around_facet_const_circulator SHalfedge_around_facet_const_circulator;

	std::ostringstream oss;

	const auto& p = h->plane();
	oss << "Facet plane=" << p << std::endl;
	
	auto fc = h->facet_cycles_begin();
	auto se = SHalfedge_const_handle(fc);
	CGAL_assertion(se != 0);
	SHalfedge_around_facet_const_circulator hc_start(se);
	SHalfedge_around_facet_const_circulator hc_end(hc_start);
	CGAL_For_all(hc_start, hc_end) {
		oss << "      co=" << hc_start->source()->center_vertex()->point() << std::endl;
	}

	oss << std::endl;
	return oss.str();
}

// Boolean operations
enum halfspace_operation {
	OP_UNION, OP_SUBTRACTION, OP_INTERSECTION
};

// Map of Plane_3 -> Plane_3 used when applied snapping
template <typename Kernel>
using plane_map = std::map<typename Kernel::Plane_3, typename Kernel::Plane_3, PlaneLess<Kernel>>;
// using plane_map = std::unordered_map<typename Kernel::Plane_3, typename Kernel::Plane_3, PlaneHash<Kernel>>;

// Snap halfspace planes
// search_radius: max cartesian distance in plane equation parameters as 4d points in space
template <typename Kernel>
plane_map<Kernel> snap_halfspaces(const std::list<CGAL::Plane_3<Kernel>>& planes, double search_radius) {
	// @todo this should incorporate some recursive or actual clustering approach so that
	// in cases of many approximate neighbours it still produces good results.

	typedef CGAL::Epick_d<CGAL::Dimension_tag<4>> KdKernel;
	typedef KdKernel::Point_d Point_d;
	typedef CGAL::Search_traits_d<KdKernel> TreeTraits;
	typedef CGAL::Kd_tree<TreeTraits> Tree;
	typedef CGAL::Fuzzy_sphere<TreeTraits> Fuzzy_sphere;

	plane_map<Kernel> result;

	std::map<Point_d, std::set<Point_d>> neighbours;
	std::map<Point_d, std::list<CGAL::Plane_3<Kernel>>> originals;
	std::vector<Point_d> planes_as_point;

	for (auto& p : planes) {
		// @todo can we skip normalization (simply divide by largest component perhaps)
		double l = std::sqrt(CGAL::to_double(p.orthogonal_vector().squared_length()));
		// @todo how to properly initialize using p._().exact() without converting to double?
		Point_d pp(CGAL::to_double(p.a()) / l, CGAL::to_double(p.b()) / l, CGAL::to_double(p.c()) / l, CGAL::to_double(p.d()) / l);
		planes_as_point.push_back(pp);
		originals[pp].push_back(p);
	}

	// @todo should we have a proper distance metric for plane equations
	Tree kdtree(planes_as_point.begin(), planes_as_point.end());

	auto plit = planes.begin();
	for (size_t i = 0; i < planes.size(); ++i) {
		if (result.find(*plit++) != result.end()) {
			continue;
		}

		auto& query = planes_as_point[i];

		Fuzzy_sphere fs(query, search_radius, 0.);
		// std::cout << "q " << query << std::endl;
		
		std::list<Point_d> results_pos, results_neg;
		kdtree.search(std::back_inserter(results_pos), fs);

		Point_d n(-query[0], -query[1], -query[2], -query[3]);
		Fuzzy_sphere fsn(n, search_radius, 0.);
		kdtree.search(std::back_inserter(results_neg), fsn);

		auto sum = std::accumulate(++results_pos.begin(), results_pos.end(), results_pos.front(), [](Point_d a, Point_d b) {return Point_d(a[0] + b[0], a[1] + b[1], a[2] + b[2], a[3] + b[3]); });
		int N = results_pos.size();
		auto sum2 = std::accumulate(results_neg.begin(), results_neg.end(), sum, [](Point_d a, Point_d b) {return Point_d(a[0] - b[0], a[1] - b[1], a[2] - b[2], a[3] - b[3]); });
		N += results_neg.size();

		auto avg = CGAL::Plane_3<Kernel>(sum2[0] / N, sum2[1] / N, sum2[2] / N, sum2[3] / N);

		for (auto& p : results_pos) {
			for (auto& pl : originals[p]) {
				result.insert({ pl, avg });
			}
		}
		for (auto& p : results_neg) {
			for (auto& pl : originals[p]) {
				result.insert({ pl, avg.opposite() });
			}
		}
	}

	return result;
}

// Snap halfspace planes
// planes_fixed: candidates
// planes: planes that can be moved to planes_fixed when distance permits
// search_radius: max cartesian distance in plane equation parameters as 4d points in space
template <typename Kernel>
plane_map<Kernel> snap_halfspaces_2(const std::list<CGAL::Plane_3<Kernel>>& planes_fixed, const std::list<CGAL::Plane_3<Kernel>>& planes, double search_radius) {
	// @todo this should incorporate some recursive or actual clustering approach so that
	// in cases of many approximate neighbours it still produces good results.

	typedef CGAL::Epick_d<CGAL::Dimension_tag<4>> KdKernel;
	typedef KdKernel::Point_d Point_d;
	typedef CGAL::Search_traits_d<KdKernel> TreeTraits;
	typedef CGAL::Kd_tree<TreeTraits> Tree;
	typedef CGAL::Fuzzy_sphere<TreeTraits> Fuzzy_sphere;

	plane_map<Kernel> result;

	std::vector<Point_d> planes_as_point;
	std::map<Point_d, CGAL::Plane_3<Kernel>> normalized_to_original;

	for (auto& p : planes_fixed) {
		// @todo can we skip normalization (simply divide by largest component perhaps)
		double l = std::sqrt(CGAL::to_double(p.orthogonal_vector().squared_length()));
		// @todo how to properly initialize using p._().exact() without converting to double?
		Point_d pp(CGAL::to_double(p.a()) / l, CGAL::to_double(p.b()) / l, CGAL::to_double(p.c()) / l, CGAL::to_double(p.d()) / l);
		planes_as_point.push_back(pp);
		normalized_to_original.insert({ pp, p });
	}

	// @todo should we have a proper distance metric for plane equations
	Tree kdtree(planes_as_point.begin(), planes_as_point.end());

	auto plit = planes.begin();
	for (; plit != planes.end(); ++plit) {
		// @todo rewrite to use 1 nearest neighbour
		double l = std::sqrt(CGAL::to_double(plit->orthogonal_vector().squared_length()));
		Point_d query(CGAL::to_double(plit->a()) / l, CGAL::to_double(plit->b()) / l, CGAL::to_double(plit->c()) / l, CGAL::to_double(plit->d()) / l);
		Fuzzy_sphere fs(query, search_radius, 0.);
		// std::cout << "q " << *plit << std::endl;

		std::list<Point_d> results;
		kdtree.search(std::back_inserter(results), fs);
		if (!results.empty()) {
			result.insert({ *plit, normalized_to_original.find(results.front())->second });
			// std::cout << "  " << normalized_to_original.find(results.front())->second << std::endl;
		} else {
			Point_d n(-query[0], -query[1], -query[2], -query[3]);
			Fuzzy_sphere fsn(n, search_radius, 0.);
			kdtree.search(std::back_inserter(results), fsn);
			if (!results.empty()) {
				result.insert({ *plit, normalized_to_original.find(results.front())->second.opposite() });
				// std::cout << "  " << normalized_to_original.find(results.front())->second << std::endl;
			}
		}
	}

	return result;
}

enum tree_type { TT_NARY_BRANCH, TT_PLANE };

// Abstract base class for halfspace tree component
template <typename Kernel>
class halfspace_tree {
public:
	virtual CGAL::Nef_polyhedron_3<Kernel> evaluate() const = 0;
	virtual void accumulate(std::list<typename Kernel::Plane_3>&) const = 0;
	virtual std::unique_ptr<halfspace_tree> map(const plane_map<Kernel>&) const = 0;
	virtual std::string dump(int level = 0) const = 0;
	virtual tree_type kind() const = 0;
	virtual void merge(CGAL::Nef_polyhedron_3<Kernel>&) const = 0;
	virtual ~halfspace_tree() {}
};

// Halfspace tree component as n-ary operands
template <typename Kernel>
class halfspace_tree_nary_branch : public halfspace_tree<Kernel> {
public:
	halfspace_operation operation_;
	std::list<std::unique_ptr<halfspace_tree<Kernel>>> operands_;

public:
	virtual tree_type kind() const {
		return TT_NARY_BRANCH;
	}

	virtual void merge(CGAL::Nef_polyhedron_3<Kernel>&) const {
		throw std::runtime_error("not implemented");
	}

	halfspace_tree_nary_branch(halfspace_operation operation, std::list<std::unique_ptr<halfspace_tree<Kernel>>>&& operands)
		: operation_(operation)
		, operands_(std::move(operands))
	{}
	std::string dump(int level) const {
		static const char* const ops[] = { "union", "subtraction", "intersection" };

		std::ostringstream ss;
		ss << std::string(level * 2, ' ') << ops[operation_] << " (" << std::endl;
		for (auto& op : operands_) {
			ss << op->dump(level + 1);
		}
		ss << std::string(level * 2, ' ') << ")" << std::endl;
		return ss.str();
	}
	virtual CGAL::Nef_polyhedron_3<Kernel> evaluate() const {
		CGAL::Nef_polyhedron_3<Kernel> result;

		if (operation_ == OP_SUBTRACTION) {
			if (operands_.size() != 2) {
				throw std::runtime_error("");
			}
			result = operands_.front()->evaluate() - operands_.back()->evaluate();
		} else if (operation_ == OP_UNION) {
			CGAL::Nef_nary_union_3<CGAL::Nef_polyhedron_3<Kernel>> builder;
			for (auto& op : operands_) {
				builder.add_polyhedron(op->evaluate());
			}
			result = builder.get_union();
		} else if (operation_ == OP_INTERSECTION) {
			bool is_all_planes = true;
			for (auto& op : operands_) {
				if (op->kind() != TT_PLANE) {
					is_all_planes = false;
					break;
				}
			}

			if (is_all_planes) {
				// Instead of creating an operand based on the intersection of plane and cube
				// which results in two intersection operations. Accumulate the result directly.
				bool first = true;
				for (auto& op : operands_) {
					if (first) {
						result = op->evaluate();
						first = false;
					} else {
						op->merge(result);
					}
				}
			} else {
				CGAL::Nef_nary_intersection_3<CGAL::Nef_polyhedron_3<Kernel>> builder;
				for (auto& op : operands_) {
					builder.add_polyhedron(op->evaluate());
				}
				result = builder.get_intersection();
			}

			/*
			CGAL::Nef_polyhedron_3<Kernel> r;
			bool first = true;
			for (auto& op : operands_) {
				if (first) {
					r = op->evaluate();
					first = false;
					continue;
				}
				r = r * op->evaluate();
			}
			return r;
			*/
		}
		return result;
	}
	virtual void accumulate(std::list<typename Kernel::Plane_3>& points) const {
		for (auto& op : operands_) {
			op->accumulate(points);
		}
	}
	virtual std::unique_ptr<halfspace_tree<Kernel>> map(const plane_map<Kernel>& m) const {
		decltype(operands_) mapped;
		for (auto& op : operands_) {
			mapped.emplace_back(op->map(m));
		}
		return std::unique_ptr<halfspace_tree<Kernel>>(new halfspace_tree_nary_branch(operation_, std::move(mapped)));
	}
};

// Utility function to extrude a polyhedral facet
template <typename LoopType, typename Kernel>
void extrude(LoopType bottom, const CGAL::Vector_3<Kernel>& V, CGAL::Polyhedron_3<Kernel>& P) {
	std::list<LoopType> face_list = { bottom };

	for (auto current_vertex = bottom.begin(); current_vertex != bottom.end(); ++current_vertex) {

		auto next_vertex = current_vertex;
		++next_vertex;

		if (next_vertex == bottom.end()) {
			next_vertex = bottom.begin();
		}

		LoopType side = { {
			*next_vertex,
			*current_vertex,
			*current_vertex + V,
			*next_vertex + V	  ,
		} };

		face_list.push_back(side);
	}

	auto top = bottom;
	for (auto& v : top) {
		v += V;
	}
	std::reverse(top.begin(), top.end());

	face_list.push_back(top);

	std::vector<CGAL::Point_3<Kernel>> unique_points;
	std::vector<std::vector<std::size_t>> facet_vertices;
	std::map<CGAL::Point_3<Kernel>, size_t> points;

	for (auto &face : face_list) {
		facet_vertices.emplace_back();
		for (auto &point : face) {
			auto p = points.insert({ point, points.size() });
			if (p.second) {
				unique_points.push_back(point);
			}
			facet_vertices.back().push_back(p.first->second);
		}
	}

	CGAL::Polygon_mesh_processing::polygon_soup_to_polygon_mesh(unique_points, facet_vertices, P);
}

// Create cube of half-distance d
template <typename Kernel>
void createCube(CGAL::Polyhedron_3<Kernel>& P, double d) {
	typedef CGAL::Point_3<Kernel> Point;
	typedef std::array<CGAL::Point_3<Kernel>, 4> Quad;

	Quad bottom = { {
		Point(-d, -d, -d),
		Point(+d, -d, -d),
		Point(+d, +d, -d),
		Point(-d, +d, -d)
	} };

	CGAL::Vector_3<Kernel> V(0, 0, d * 2);

	extrude(bottom, V, P);
}

// Leaf of halfspace tree stored as a Plane_3
template <typename Kernel>
class halfspace_tree_plane : public halfspace_tree<Kernel> {
private:
	typename Kernel::Plane_3 plane_;

public:
	virtual tree_type kind() const {
		return TT_PLANE;
	}

	halfspace_tree_plane(const typename Kernel::Plane_3& plane)
		: plane_(plane)
	{}
	std::string dump(int level) const {
		std::ostringstream ss;
		ss << std::string(level * 2, ' ') << "p " << std::setprecision(15) << plane_ << std::endl;
		return ss.str();
	}
	virtual CGAL::Nef_polyhedron_3<Kernel> evaluate() const {
		if constexpr(CGAL::Is_extended_kernel<Kernel>::value_type::value) {
			throw std::runtime_error("Not implemented yet");
			// typename Kernel::Plane_3 plane(plane_.a().exact(), plane_.b().exact(), plane_.c().exact(), plane_.d().exact());
			// CGAL::Nef_polyhedron_3<Kernel> plane_nef(plane, CGAL::Nef_polyhedron_3<Kernel>::Boundary::INCLUDED);
			// CGAL::Nef_polyhedron_3<Kernel> full_nef(full);
			// auto two_halfspaces = full_nef - plane_nef;
			// @todo
		} else {
			/*static*/ auto almost_complete = []() {
				CGAL::Polyhedron_3<Kernel> P;
				createCube(P, 10000);
				return CGAL::Nef_polyhedron_3<Kernel>(P);
			}();
			return almost_complete.intersection(plane_.opposite(), CGAL::Nef_polyhedron_3<Kernel>::OPEN_HALFSPACE).closure();
		}
	}
	virtual void merge(CGAL::Nef_polyhedron_3<Kernel>& a) const {
		a = a.intersection(plane_.opposite(), CGAL::Nef_polyhedron_3<Kernel>::OPEN_HALFSPACE).closure();
	}
	virtual void accumulate(std::list<typename Kernel::Plane_3>& points) const {
		points.push_back(plane_);
	}
	virtual std::unique_ptr<halfspace_tree<Kernel>> map(const plane_map<Kernel>& m) const {

		std::array<typename Kernel::FT, 3> abc{ plane_.a(), plane_.b(), plane_.c() };
		auto minel = std::min_element(abc.begin(), abc.end());
		auto maxel = std::max_element(abc.begin(), abc.end());
		auto maxval = ((-*minel) > *maxel) ? (-*minel) : *maxel;
		CGAL::Plane_3<Kernel> pp(
			plane_.a() / maxval,
			plane_.b() / maxval,
			plane_.c() / maxval,
			plane_.d() / maxval
		);

		auto it = m.find(pp);
		if (it != m.end()) {
			return std::unique_ptr<halfspace_tree<Kernel>>(new halfspace_tree_plane(it->second));
		} else {
			return std::unique_ptr<halfspace_tree<Kernel>>(new halfspace_tree_plane(plane_));
		}
	}
};

// Triangulate a nef facet. Used for intersection check to find convex subcomponent
template <typename Kernel>
std::vector<CGAL::Triangle_3<Kernel>> triangulate_nef_facet(typename CGAL::Nef_polyhedron_3<Kernel>::Halffacet_const_handle f) {
	typedef typename CGAL::Nef_polyhedron_3<Kernel>::SHalfedge_around_facet_const_circulator SHalfedge_around_facet_const_circulator;

	std::vector<typename Kernel::Point_3> ps;
	SHalfedge_around_facet_const_circulator it(f->facet_cycles_begin());
	SHalfedge_around_facet_const_circulator first(it);
	CGAL_For_all(it, first) {
		ps.push_back(it->source()->center_vertex()->point());
	}

	typedef std::tuple<int, int, int> indices_triple;
	std::vector<indices_triple> patches;
	CGAL::Polygon_mesh_processing::triangulate_hole_polyline(ps, std::back_inserter(patches));

	std::vector<CGAL::Triangle_3<Kernel>> result;
	result.reserve(patches.size());
	std::transform(patches.begin(), patches.end(), std::back_inserter(result), [&ps](indices_triple& t) {
		return CGAL::Triangle_3<Kernel>(ps[std::get<0>(t)], ps[std::get<1>(t)], ps[std::get<2>(t)]);
	});

	return result;
}

enum EdgeType { CONCAVE, CONVEX };

template <typename Kernel>
struct VertexProperties {
	typename CGAL::Nef_polyhedron_3<Kernel>::Halffacet_const_handle facet;
	size_t original_index;
};

template <typename Kernel>
using Graph = boost::adjacency_list<boost::vecS, boost::vecS, boost::undirectedS,
	VertexProperties<Kernel>,
	boost::property<boost::edge_weight_t, EdgeType>>;

// Build a boost graph with vertex corresponding to Nef facet, edge corresponding to Nef edge
// marked as reflex or not.
template <typename Kernel>
Graph<Kernel> build_facet_edge_graph(const CGAL::Nef_polyhedron_3<Kernel>& poly) {
	typedef typename CGAL::Nef_polyhedron_3<Kernel>::Halffacet_const_handle Halffacet_const_handle;

	Graph<Kernel> G;

	std::map<Halffacet_const_handle, size_t> facet_to_idx;

	for (auto it = poly.vertices_begin(); it != poly.vertices_end(); ++it) {
		for (auto a = it->shalfedges_begin(); a != it->shalfedges_end(); ++a) {
			auto b = a->snext();
			if (a->facet()->incident_volume()->mark() && a->facet()->incident_volume() == b->facet()->incident_volume() && a->facet()->is_valid() && b->facet()->is_valid()) {
				// cross product of facet normals
				auto avec = a->facet()->plane().orthogonal_vector();
				auto bvec = b->facet()->plane().orthogonal_vector();
				auto cross = CGAL::cross_product(avec, bvec);

				size_t aidx, bidx;
				{
					auto p = facet_to_idx.insert({ a->facet(), facet_to_idx.size() });
					aidx = p.first->second;
					if (p.second) {
						auto& v = G[boost::add_vertex(G)];
						v.facet = a->facet();
						v.original_index = aidx;
					}
				}
				{
					auto p = facet_to_idx.insert({ b->facet(), facet_to_idx.size() });
					bidx = p.first->second;
					if (p.second) {
						auto& v = G[boost::add_vertex(G)];
						v.facet = b->facet();
						v.original_index = bidx;
					}
				}

				// half edge direction
				auto ref = a->next()->source()->center_vertex()->point() - a->source()->center_vertex()->point();
				// std::cout << ref << " . " << cross << std::endl;

				// check whether half edge direction conforms to facet normal cross
				auto edge_type = CGAL::scalar_product(cross, ref) > 0
					? CONCAVE
					: CONVEX;

				// std::cout << aidx << " -> " << bidx << " " << edge_type << std::endl;

				boost::add_edge(aidx, bidx, edge_type, G);
			}
		}
	}

	return G;
}

template <typename Kernel>
void dump_facets(Graph<Kernel>& G) {
	for (size_t ii = 0; ii < boost::num_vertices(G); ++ii) {
		// std::cout << ii << " " << dump_facet<Kernel>(G[ii].facet) << std::endl;
	}
}

/*
struct Intersection_visitor {
	typedef void result_type;
	void operator()(const Kernel::Point_3& p) const
	{
		std::cout << p << std::endl;
	}
	void operator()(const Kernel::Segment_3& s) const
	{
		std::cout << s << std::endl;
	}
	void operator()(const Kernel::Triangle_3& s) const
	{
		std::cout << s << std::endl;
	}
};
*/

template <typename Kernel>
struct Segment_collector {
	typedef void result_type;
	boost::optional<CGAL::Segment_3<Kernel>> segment;

	void operator()(const CGAL::Point_3<Kernel>&)
	{
	}
	void operator()(const CGAL::Segment_3<Kernel>& s)
	{
		segment = s;
	}
	void operator()(const CGAL::Triangle_3<Kernel>&)
	{
	}
};

template <typename Kernel, typename ComponentMap>
class convex_subcomponent_visitor : public boost::default_bfs_visitor {

private:
	EdgeType edgetype_;
	ComponentMap& components_;

public:
	convex_subcomponent_visitor(EdgeType edgetype, ComponentMap& component)
		: edgetype_(edgetype), components_(component) {}

	template <typename Edge, typename Graph>
	bool tree_edge(Edge e, const Graph& g) {
		if (boost::get(boost::edge_weight, g, e) == edgetype_) {
			auto srcid = boost::source(e, g);
			auto tgtid = boost::target(e, g);

			auto src = &components_[srcid];
			auto tgt = &components_[tgtid];

			if (*src == -1) {
				std::swap(srcid, tgtid);
				std::swap(src, tgt);
			}

			// std::cout << "   v " << srcid << " -> " << tgtid << " ??" << std::endl;

			if (*tgt == -1) {
				bool tgt_has_any_reflex_edge = false;

				typename boost::graph_traits<Graph>::out_edge_iterator ei, ei_end;
				for (boost::tie(ei, ei_end) = boost::out_edges(tgtid, g); ei != ei_end; ++ei) {
					if (boost::get(boost::edge_weight, g, *ei) != edgetype_) {
						tgt_has_any_reflex_edge = true;
						// std::cout << "   reflex: " << boost::source(*ei, g) << " -- " << boost::target(*ei, g) << std::endl;
						break;
					}
				}

				if (tgt_has_any_reflex_edge) {
					// std::cout << "   x has reflex edge" << std::endl;
				} else {
					// topological check completed, now check geometry, non topologically connected facets should not geometrically intersect
					bool any_intersecting = false;
					auto& plane_tgt = g[tgtid].facet->plane();

					// std::cout << "plane_tgt " << plane_tgt << std::endl;

					for (size_t i = 0; i < components_.size(); ++i) {
						if (i == tgtid) {
							continue;
						}

						if (components_[i] == *src) {
							// no need to check for intersection when edge exists
							const bool has_edge = boost::edge(i, tgtid, g).second;
							if (!has_edge) {
								auto triangles_i = triangulate_nef_facet<Kernel>(g[i].facet);

								std::list<CGAL::Segment_3<Kernel>> edges_i;

								for (auto fc = g[i].facet->facet_cycles_begin(); fc != g[i].facet->facet_cycles_end(); ++fc) {
									auto se = typename CGAL::Nef_polyhedron_3<Kernel>::SHalfedge_const_handle(fc);
									CGAL_assertion(se != 0);
									typename CGAL::Nef_polyhedron_3<Kernel>::SHalfedge_around_facet_const_circulator hc(se);
									typename CGAL::Nef_polyhedron_3<Kernel>::SHalfedge_around_facet_const_circulator hc_end(hc);

									CGAL_For_all(hc, hc_end) {
										edges_i.emplace_back(hc->target()->center_vertex()->point(), hc->source()->center_vertex()->point());
									}
								}

								if (std::any_of(triangles_i.begin(), triangles_i.end(), [&plane_tgt, &edges_i](CGAL::Triangle_3<Kernel>& t) {
									auto x = CGAL::intersection(plane_tgt, t);
									if (x) {
										// std::cout << "   triangle: " << t << std::endl;
										// Intersection_visitor v;
										// boost::apply_visitor([](auto x) {std::cout << "   intersects: " << x << std::endl; })(*x);
										Segment_collector<Kernel> sc;
										boost::apply_visitor(sc)(*x);
										if (sc.segment) {
											if (!std::any_of(edges_i.begin(), edges_i.end(), [&sc](CGAL::Segment_3<Kernel>& s) {
												// When intersecting with the boundary of a facet we likely multiple co-planar facets. Exclude intersection.
												auto xy = CGAL::intersection(s, *sc.segment);
												if (!xy) {
													return false;
												}
												Segment_collector<Kernel> scy;
												boost::apply_visitor(scy)(*xy);
												return (bool)scy.segment;
											})) {
												return true;
											}
										}
									}
									return false;
								})) {
									// std::cout << "    intersects with: " << i << ": " << std::endl;
									for (auto& t : triangles_i) {
										// std::cout << "  " << t << std::endl;
									}

									any_intersecting = true;
									break;
								}
							}
						}
					}
					if (any_intersecting) {
						// std::cout << "   x has intersection" << std::endl;
					} else {
						// std::cout << "v " << srcid << " -> " << tgtid << " !!" << std::endl;
						// std::cout << "(" << *src << " " << *tgt << ")" << std::endl;

						*tgt = *src;
						return true;
					}
				}
			}
		}
		return false;
	}
};

// bfs implementation to that respects a predicate on determining whether an edge is applicable
template <typename Kernel, typename Fn>
void bfs(Graph<Kernel>& g, size_t start_vertex, Fn& fn) {
	std::queue<size_t> queue;
	queue.push(start_vertex);

	std::set<size_t> visited;
	visited.insert(start_vertex);

	while (!queue.empty()) {
		auto cur = queue.front();
		queue.pop();

		typename boost::graph_traits<Graph<Kernel>>::out_edge_iterator ei, ei_end;
		for (boost::tie(ei, ei_end) = boost::out_edges(cur, g); ei != ei_end; ++ei) {
			auto s = boost::source(*ei, g);
			auto t = boost::target(*ei, g);
			
			// @todo is this necessary?
			if (cur == t) {
				std::swap(s, t);
			}

			if (visited.find(t) == visited.end()) {
				// @nb a boolean condition on tree_edge() so that
				// we can influence traversal with out topological and geometrical
				// constraints.
				if (fn.tree_edge(*ei, g)) {
					queue.push(t);
					visited.insert(t);
				}
			}
		}
	}
}

// builds a tree of halfspaces from an input nef polyhedron
// checks whether output is equivalent and if not uses a convex decomposition first
template <typename Kernel, typename TreeKernel=Kernel>
std::unique_ptr<halfspace_tree<TreeKernel>> build_halfspace_tree(Graph<Kernel>& G, CGAL::Nef_polyhedron_3<Kernel>& poly, bool negate = false, int level=0) {
	typedef boost::filtered_graph<Graph<Kernel>, boost::keep_all, std::function<bool(typename Graph<Kernel>::vertex_descriptor)>> FilteredGraph;

	auto edge_trait = negate ? CONCAVE : CONVEX;

	/*
	bool all_convex = true;
	typename boost::graph_traits<Graph<Kernel>>::edge_iterator ei, ei_end;
	for (boost::tie(ei, ei_end) = boost::edges(G); ei != ei_end; ++ei) {
		if (boost::get(boost::edge_weight, G, *ei) != edge_trait) {
			// all_convex = false;
			break;
		}
	}
	*/

	// boost::write_graphviz(std::cout, G);

	std::unique_ptr<halfspace_tree<TreeKernel>> tree_0;
	std::list<std::unique_ptr<halfspace_tree<TreeKernel>>> root_expression_0;

	// First isolate into completely loose components
	std::vector<int> components_0(boost::num_vertices(G), -1);
	boost::connected_components(G, &components_0[0]);

	for (size_t i = 0; i <= *std::max_element(components_0.begin(), components_0.end()); ++i) {
		std::unique_ptr<halfspace_tree<TreeKernel>> tree;
		std::list<std::unique_ptr<halfspace_tree<TreeKernel>>> root_expression;

		auto included_in_vertex_subset_0 = [&components_0, &i](typename Graph<Kernel>::vertex_descriptor vd) {
			return components_0[vd] == i;
		};
		FilteredGraph sub_graph_filtered_0(G, boost::keep_all{}, included_in_vertex_subset_0);
		Graph<Kernel> sub_graph_0;
		boost::copy_graph(sub_graph_filtered_0, sub_graph_0);

		std::vector<int> components(boost::num_vertices(sub_graph_0), -1);
		int largest_component_idx = -1;

		int num_components = 0;
		
		// @nb we don't just randomly start from an arbitrary seed, but we sort planes by d / | abc |
		// for (size_t i = 0; i < boost::num_vertices(sub_graph_0); ++i) {
		
		std::vector<size_t> sorted_verts;
		for (size_t i = 0; i < boost::num_vertices(sub_graph_0); ++i) {
			sorted_verts.push_back(i);
		}
		std::sort(sorted_verts.begin(), sorted_verts.end(), [&G](size_t a, size_t b) {
			auto da = G[a].facet->plane().d() / G[a].facet->plane().orthogonal_vector().squared_length();
			auto db = G[b].facet->plane().d() / G[b].facet->plane().orthogonal_vector().squared_length();
			return db < da;
		});

		convex_subcomponent_visitor<Kernel, decltype(components)> visitor(edge_trait, components);
		for (auto& i : sorted_verts) {
			if (components[i] == -1) {
				components[i] = num_components++;
				bfs(sub_graph_0, boost::vertex(i, sub_graph_0), visitor);
			}
		}

		// std::ostream_iterator<size_t> output(std::cout, " ");
		// std::cout << "components: " << std::endl;
		std::map<size_t, size_t> comp;
		size_t iii = 0;
		for (auto it = components.begin(); it != components.end(); ++it, ++iii) {
			comp[sub_graph_0[iii].original_index] = *it;
		}
		iii = comp.rbegin()->first;
		for (size_t iiii = 0; iiii <= iii; ++iiii) {
			// std::cout << std::setw(2) << iiii << " ";
		}
		// std::cout << std::endl;
		for (size_t iiii = 0; iiii <= iii; ++iiii) {
			auto it = comp.find(iiii);
			if (it == comp.end()) {
				// std::cout << "__ ";
			} else {
				// std::cout << std::setw(2) << it->second << " ";
			}
		}
		// std::cout << std::endl;

		std::vector<size_t> component_size(num_components, 0);

		for (auto& idx : components) {
			component_size[idx] ++;
		}

		largest_component_idx = std::distance(component_size.begin(), std::max_element(component_size.begin(), component_size.end()));

		size_t vidx = 0;
		// Convex decomposition is not always optimal, sometimes contains coplanar facets
		std::unordered_set<typename Kernel::Plane_3, PlaneHash<Kernel>> plane_set;
		for (auto it = components.begin(); it != components.end(); ++it, ++vidx) {
			auto fct = sub_graph_0[vidx].facet;
			if (negate) {
				fct = fct->twin();
			}
			if (*it == largest_component_idx && plane_set.find(fct->plane()) == plane_set.end()) {
				root_expression.emplace_back(new halfspace_tree_plane<Kernel>(fct->plane()));
				plane_set.insert(fct->plane());
			}
		}

		tree.reset(new halfspace_tree_nary_branch<TreeKernel>(OP_INTERSECTION, std::move(root_expression)));

		auto included_in_vertex_subset = [&components, &largest_component_idx](typename Graph<Kernel>::vertex_descriptor vd) {
			return components[vd] != largest_component_idx;
		};
		FilteredGraph sub_graph_filtered(sub_graph_0, boost::keep_all{}, included_in_vertex_subset);
		Graph<Kernel> sub_graph;
		// @todo can we go without this copy?
		boost::copy_graph(sub_graph_filtered, sub_graph);

		// std::cout << "nv " << boost::num_vertices(sub_graph) << std::endl;

		// @nb counting vertices on filtered_graph returns the original amount
		if (boost::num_vertices(sub_graph)) {
			auto remainder = build_halfspace_tree<Kernel, TreeKernel>(sub_graph, poly, !negate, level+1);

			std::list<std::unique_ptr<halfspace_tree<TreeKernel>>> sub_expression;
			sub_expression.emplace_back(std::move(tree));
			sub_expression.emplace_back(std::move(remainder));

			tree.reset(new halfspace_tree_nary_branch<TreeKernel>(OP_SUBTRACTION, std::move(sub_expression)));
		}

		root_expression_0.emplace_back(std::move(tree));
	}

	if (root_expression_0.size() == 1) {
		tree_0 = std::move(root_expression_0.front());
	} else {
		tree_0.reset(new halfspace_tree_nary_branch<TreeKernel>(OP_UNION, std::move(root_expression_0)));
	}

	if (false && level == 0) {
		auto compare = tree_0->evaluate();
		auto make_vertex_point_it = [](typename CGAL::Nef_polyhedron_3<Kernel>::Vertex_const_iterator p) {
			return boost::make_transform_iterator(p, [](auto v) { return v.point(); });
		};

		std::set<CGAL::Point_3<Kernel>> s1(make_vertex_point_it(poly.vertices_begin()), make_vertex_point_it(poly.vertices_end()));
		std::set<CGAL::Point_3<Kernel>> s2(make_vertex_point_it(compare.vertices_begin()), make_vertex_point_it(compare.vertices_end()));

		if (s1 != s2) {
			std::unique_ptr<halfspace_tree<TreeKernel>> tree;
			std::list<std::unique_ptr<halfspace_tree<TreeKernel>>> root_expression;

			CGAL::convex_decomposition_3(poly);
			// the first volume is the outer volume, which is
			// ignored in the decomposition
			auto ci = ++poly.volumes_begin();
			int NN = 0;

			for (; ci != poly.volumes_end(); ++ci, ++NN) {
				std::list<std::unique_ptr<halfspace_tree<TreeKernel>>> sub_expression;

				if (ci->mark()) {
					// @todo couldn't get it to work with the multiple volumes of a complex decomposition
					// directly, so for now we need to isolate the individual volumes.
					CGAL::Polyhedron_3<Kernel> P;
					poly.convert_inner_shell_to_polyhedron(ci->shells_begin(), P);
					CGAL::Nef_polyhedron_3<Kernel> Pnef(P);
					auto Pgraph = build_facet_edge_graph(Pnef);
					for (size_t ii = 0; ii < boost::num_vertices(Pgraph); ++ii) {
						auto& p0 = Pgraph[ii].facet->plane();
						// @todo this is to convert from kernel to extended kernel, can be if constexpr perhaps?
						CGAL::Plane_3<TreeKernel> p1(p0.a().exact(), p0.b().exact(), p0.c().exact(), p0.d().exact());
						sub_expression.emplace_back(new halfspace_tree_plane<TreeKernel>(p1));
					}
				}

				root_expression.emplace_back(new halfspace_tree_nary_branch<TreeKernel>(OP_INTERSECTION, std::move(sub_expression)));
			}

			tree.reset(new halfspace_tree_nary_branch<TreeKernel>(OP_UNION, std::move(root_expression)));
			return tree;
		}
	}

	return std::move(tree_0);
}

// Visitor for Nef_polyhedron_3 shells to convert facets to Polyhedron_3
// using the Polygon_mesh_processing package and Polygon_triangulation_decomposition_2
// in case of facets with inner bounds.
template <typename Kernel>
struct Halffacet_collector {
	std::set<typename CGAL::Nef_polyhedron_3<Kernel>::Halffacet_const_handle> facets;
	void visit(typename CGAL::Nef_polyhedron_3<Kernel>::Vertex_const_handle) {}
	void visit(typename CGAL::Nef_polyhedron_3<Kernel>::Halfedge_const_handle) {}
	void visit(typename CGAL::Nef_polyhedron_3<Kernel>::Halffacet_const_handle h) {
		facets.insert(h);
	}
	void visit(typename CGAL::Nef_polyhedron_3<Kernel>::SHalfedge_const_handle) {}
	void visit(typename CGAL::Nef_polyhedron_3<Kernel>::SHalfloop_const_handle) {}
	void visit(typename CGAL::Nef_polyhedron_3<Kernel>::SFace_const_handle) {}
};



// Visitor for Nef_polyhedron_3 shells to convert facets to Polyhedron_3
// using the Polygon_mesh_processing package and Polygon_triangulation_decomposition_2
// in case of facets with inner bounds.
template <typename Kernel, bool eliminate_tiny_facets=false>
class Polysoup_builder {
private:
	std::map<CGAL::Point_3<Kernel>, size_t> verts;
	std::vector<std::vector<size_t>> facets;
public:
	void visit(typename CGAL::Nef_polyhedron_3<Kernel>::Vertex_const_handle) {}
	void visit(typename CGAL::Nef_polyhedron_3<Kernel>::Halfedge_const_handle) {}
	void visit(typename CGAL::Nef_polyhedron_3<Kernel>::Halffacet_const_handle h) {
		// reduce extent of number because otherwise run into float_max
		auto h_plane_ = h->plane();
		std::array<typename Kernel::FT, 3> abc{ h_plane_.a(), h_plane_.b(), h_plane_.c() };
		auto minel = std::min_element(abc.begin(), abc.end());
		auto maxel = std::max_element(abc.begin(), abc.end());
		auto maxval = ((-*minel) > *maxel) ? (-*minel) : *maxel;
		CGAL::Plane_3<Kernel> h_plane(
			h_plane_.a() / maxval,
			h_plane_.b() / maxval,
			h_plane_.c() / maxval,
			h_plane_.d() / maxval
		);

		auto verts_backup = verts;
		auto facets_backup = facets;

		boost::optional<CGAL::Polygon_with_holes_2<Kernel>> pwh;
		auto nf = std::distance(h->facet_cycles_begin(), h->facet_cycles_end());
		for (auto fc = h->facet_cycles_begin(); fc != h->facet_cycles_end(); ++fc) {
			// std::cout << "h_plane.point() " << h_plane.point() << std::endl;
			// std::cout << "h_plane.base1() " << h_plane.base1() << std::endl;
			// std::cout << "h_plane.base2() " << h_plane.base2() << std::endl;

			auto se = typename CGAL::Nef_polyhedron_3<Kernel>::SHalfedge_const_handle(fc);
			CGAL_assertion(se != 0);
			typename CGAL::Nef_polyhedron_3<Kernel>::SHalfedge_around_facet_const_circulator hc(se);
			typename CGAL::Nef_polyhedron_3<Kernel>::SHalfedge_around_facet_const_circulator hc_end(hc);

			CGAL::Polygon_2<Kernel> loop;
			if (nf == 1) {
				facets.emplace_back();
			}

			CGAL_For_all(hc, hc_end) {
				auto p = hc->source()->center_vertex()->point();
				if (nf == 1) {
					facets.back().push_back(verts.insert({ p , verts.size() }).first->second);
				} else {
					// std::cout << "p " << p << std::endl;
					auto v = p - h_plane.point();
					// std::cout << "v " << v << std::endl;
					CGAL::Point_2<Kernel> uv(v * h_plane.base1(), v * h_plane.base2());
					// std::cout << "uv " << uv << std::endl;
					loop.push_back(uv);
				}
			}

			if (pwh) {
				pwh->add_hole(loop);
			} else {
				pwh.emplace(loop);
			}
		}

		if (nf > 1) {
			CGAL::Polygon_triangulation_decomposition_2<Kernel> decompositor;
			std::list<CGAL::Polygon_2<Kernel>> decom_polies;
			decompositor(*pwh, std::back_inserter(decom_polies));
			for (auto& p : decom_polies) {
				facets.emplace_back();
				for (auto it = p.vertices_begin(); it != p.vertices_end(); ++it) {
					// std::cout << "*it " << *it << std::endl;
					auto du = it->x() * h_plane.base1() / h_plane.base1().squared_length();
					auto dv = it->y() * h_plane.base2() / h_plane.base2().squared_length();
					auto pp = h_plane.point() + du + dv;
					// std::cout << "pp " << pp << std::endl;
					facets.back().push_back(verts.insert({ pp, verts.size() }).first->second);
				}
			}
		}

		if constexpr (eliminate_tiny_facets) {
			// Eliminate small slivers that create topologic connections between interior and exterior.
			// Use connected components on polyhedron to eliminate.

			std::vector<const CGAL::Point_3<Kernel>*> verts_vector(verts.size());
			for (auto& p : verts) {
				verts_vector[p.second] = &p.first;
			}

			// We need to normalize because we want to compare to a real-world area value
			auto b1 = h_plane.base1();
			double l = std::sqrt(CGAL::to_double(b1.squared_length()));
			b1 /= l;

			auto b2 = h_plane.base2();
			l = std::sqrt(CGAL::to_double(b2.squared_length()));
			b2 /= l;

			// std::cout << "p " << h_plane << std::endl;
			// std::cout << "x " << b1 << std::endl;
			// std::cout << "y " << b2 << std::endl;

			// check for size of emitted facet, rollback if too insignificant
			typename Kernel::FT area = 0;
			for (auto it = facets.begin() + facets_backup.size(); it != facets.end(); ++it) {
				CGAL::Polygon_2<Kernel> loop;
				for (auto& i : *it) {
					const auto& p = *verts_vector[i];
					auto v = p - h_plane.point();
					// std::cout << "v " << v << std::endl;
					CGAL::Point_2<Kernel> uv(v * b1, v * b2);
					// std::cout << "uv " << uv << std::endl;
					loop.push_back(uv);
				}
				// std::cout << "---" << std::endl;
				area += loop.area();
			}

			// auto pl = h_plane;
			// l = std::sqrt(CGAL::to_double(pl.orthogonal_vector().squared_length()));
			// std::cout << pl.a() / l << " " << pl.b() / l << " " << pl.c() / l << " " << pl.d() / l << ": " << area << std::endl;
			if (area < 1.e-5) {
				verts = verts_backup;
				facets = facets_backup;
			}
		}
	}
	void visit(typename CGAL::Nef_polyhedron_3<Kernel>::SHalfedge_const_handle) {}
	void visit(typename CGAL::Nef_polyhedron_3<Kernel>::SHalfloop_const_handle) {}
	void visit(typename CGAL::Nef_polyhedron_3<Kernel>::SFace_const_handle) {}
	void build(CGAL::Polyhedron_3<Kernel>& P) {
		std::vector<CGAL::Point_3<Kernel>> verts_vector(verts.size());
		for (auto& p : verts) {
			verts_vector[p.second] = p.first;
		}
		CGAL::Polygon_mesh_processing::polygon_soup_to_polygon_mesh(verts_vector, facets, P);
	}
	void write(std::ostream& ofs) {
		std::vector<CGAL::Point_3<Kernel>> verts_vector(verts.size());
		for (auto& p : verts) {
			verts_vector[p.second] = p.first;
		}
		for (auto& v : verts_vector) {
			ofs << "v " << v.cartesian(0) << " " << v.cartesian(1) << " " << v.cartesian(2) << "\n";
		}
		for (auto& idxs : facets) {
			ofs << "f";
			for (auto& i : idxs) {
				ofs << " " << (i+1);
			}
			ofs << "\n";
		}
		ofs << std::flush;
	}
};

template <typename Kernel, typename TreeKernel = Kernel>
std::unique_ptr<halfspace_tree<TreeKernel>> build_halfspace_tree_decomposed(const CGAL::Nef_polyhedron_3<Kernel>& poly_, std::list<CGAL::Plane_3<Kernel>>& planes) {
	std::unique_ptr<halfspace_tree<TreeKernel>> tree;
	std::list<std::unique_ptr<halfspace_tree<TreeKernel>>> root_expression;

	// Don't add intermediate facets created by decomposition
	for (auto it = poly_.halffacets_begin(); it != poly_.halffacets_end(); ++it) {
		// but below is converted to and from vanilla polyhedron, which recomputes planes (but is still exact).
		// Therefore, we do need to have some uniformization step, which in this case is divide by larged a,b or c
		// component.
		if (it->incident_volume()->mark()) {
			std::array<typename Kernel::FT, 3> abc{ it->plane().a(), it->plane().b(), it->plane().c() };
			auto minel = std::min_element(abc.begin(), abc.end());
			auto maxel = std::max_element(abc.begin(), abc.end());
			auto maxval = ((-*minel) > *maxel) ? (-*minel) : *maxel;
			planes.push_back(typename Kernel::Plane_3(
				it->plane().a() / maxval,
				it->plane().b() / maxval,
				it->plane().c() / maxval,
				it->plane().d() / maxval
			));
		}
	}

	auto poly = poly_;
	CGAL::convex_decomposition_3(poly);
	// the first volume is the outer volume, which is
	// ignored in the decomposition
	auto ci = ++poly.volumes_begin();
	int NN = 0;

	for (; ci != poly.volumes_end(); ++ci, ++NN) {
		std::list<std::unique_ptr<halfspace_tree<TreeKernel>>> sub_expression;

		if (ci->mark()) {
			Halffacet_collector<Kernel> vis;
			poly.visit_shell_objects(typename CGAL::Nef_polyhedron_3<Kernel>::SFace_const_handle(ci->shells_begin()), vis);
			for (auto& f : vis.facets) {
				sub_expression.emplace_back(new halfspace_tree_plane<TreeKernel>(f->plane()));
			}

			/*
			// @todo couldn't get it to work with the multiple volumes of a complex decomposition
			// directly, so for now we need to isolate the individual volumes.
			CGAL::Polyhedron_3<Kernel> P;
			poly.convert_inner_shell_to_polyhedron(ci->shells_begin(), P);
			CGAL::Nef_polyhedron_3<Kernel> Pnef(P);			

			for (auto it = Pnef.halffacets_begin(); it != Pnef.halffacets_end(); ++it) {
				if (it->incident_volume()->mark()) {
					sub_expression.emplace_back(new halfspace_tree_plane<TreeKernel>(it->plane()));
				}
			}

			if (sub_expression.size() != vis.facets.size()) {

				Polysoup_builder<Kernel> vis2;
				poly.visit_shell_objects(CGAL::Nef_polyhedron_3<Kernel>::SFace_const_handle(ci->shells_begin()), vis2);

				{
					std::ofstream("debug-nef-decomp.off") << P;
				}
				{
					CGAL::Polyhedron_3<Kernel> temp;
					vis2.build(temp);
					std::ofstream("debug-converted-poly.off") << temp;
				}

				// throw std::runtime_error("Unexpected");
			}
			*/
		}

		root_expression.emplace_back(new halfspace_tree_nary_branch<TreeKernel>(OP_INTERSECTION, std::move(sub_expression)));
	}

	tree.reset(new halfspace_tree_nary_branch<TreeKernel>(OP_UNION, std::move(root_expression)));
	return tree;
}

template <typename Kernel, typename TreeKernel = Kernel>
std::unique_ptr<halfspace_tree<TreeKernel>> build_halfspace_tree_is_decomposed(const CGAL::Nef_polyhedron_3<Kernel>& poly_, std::list<CGAL::Plane_3<Kernel>>& planes) {
	std::unique_ptr<halfspace_tree<TreeKernel>> tree;
	std::list<std::unique_ptr<halfspace_tree<TreeKernel>>> root_expression;

	// Don't add intermediate facets created by decomposition
	for (auto it = poly_.halffacets_begin(); it != poly_.halffacets_end(); ++it) {
		// but below is converted to and from vanilla polyhedron, which recomputes planes (but is still exact).
		// Therefore, we do need to have some uniformization step, which in this case is divide by larged a,b or c
		// component.
		if (it->incident_volume()->mark()) {
			std::array<typename Kernel::FT, 3> abc{ it->plane().a(), it->plane().b(), it->plane().c() };
			auto minel = std::min_element(abc.begin(), abc.end());
			auto maxel = std::max_element(abc.begin(), abc.end());
			auto maxval = ((-*minel) > *maxel) ? (-*minel) : *maxel;
			typename Kernel::Plane_3 pln(
				it->plane().a() / maxval,
				it->plane().b() / maxval,
				it->plane().c() / maxval,
				it->plane().d() / maxval
			);
			planes.push_back(pln);
			root_expression.emplace_back(new halfspace_tree_plane<TreeKernel>(pln));
		}
	}
	tree.reset(new halfspace_tree_nary_branch<TreeKernel>(OP_INTERSECTION, std::move(root_expression)));
	return tree;
}

template <typename Kernel>
size_t edge_contract(Graph<Kernel>& G) {
	size_t n = 0;
	typename boost::graph_traits<Graph<Kernel>>::edge_iterator ei, ei_end;
	bool has_contracted = true;
	while (has_contracted) {
		has_contracted = false;
		for (boost::tie(ei, ei_end) = boost::edges(G); ei != ei_end; ++ei) {
			auto srcid = boost::source(*ei, G);
			auto tgtid = boost::target(*ei, G);
			auto a = G[srcid].facet->plane().orthogonal_vector();
			auto b = G[tgtid].facet->plane().orthogonal_vector();
			// std::cout << srcid << " -- " << tgtid << std::endl << G[srcid].facet->plane() << std::endl << G[tgtid].facet->plane() << std::endl << CGAL::approximate_angle(a, b) << std::endl;
			if (CGAL::approximate_angle(a, b) < 0.1) {
				for (auto oe : boost::make_iterator_range(boost::out_edges(tgtid, G))) {
					auto tt = boost::target(oe, G);
					if (srcid != tt) { // Avoid self-loop
						bool exists = boost::edge(srcid, tt, G).second;
						if (!exists) {
							boost::add_edge(srcid, tt, G);
						}						
					}
				}
				++n;
				has_contracted = true;

				boost::clear_vertex(tgtid, G);
				boost::remove_vertex(tgtid , G);

				break;
			}
		}
	}
	return n;
}

// For some reason gives better results then Nef_polyhedron_3.convert_to_polyhedron() in some cases
template <typename Kernel>
bool convert_to_polyhedron(const CGAL::Nef_polyhedron_3<Kernel>& a, CGAL::Polyhedron_3<Kernel>& b, size_t volume_index=0) {
	size_t v = 0;
	for (auto it = a.volumes_begin(); it != a.volumes_end(); ++it) {
		if (!it->mark()) {
			continue;
		}
		for (auto jt = it->shells_begin(); jt != it->shells_end(); ++jt) {
			if (v++ == volume_index) {
				Polysoup_builder<Kernel> vis;
				a.visit_shell_objects(typename CGAL::Nef_polyhedron_3<Kernel>::SFace_const_handle(jt), vis);
				vis.build(b);
				return true;
			}
		}
	}
	return false;
}

template <typename Kernel>
bool write_to_obj(const CGAL::Nef_polyhedron_3<Kernel>& a, std::ostream& ofs, size_t volume_index = 0) {
	size_t v = 0;
	Polysoup_builder<Kernel> vis;
	for (auto it = a.volumes_begin(); it != a.volumes_end(); ++it) {
		if (!it->mark()) {
			continue;
		}
		for (auto jt = it->shells_begin(); jt != it->shells_end(); ++jt) {
			if (v++ == volume_index || volume_index == std::numeric_limits<size_t>::max()) {
				a.visit_shell_objects(typename CGAL::Nef_polyhedron_3<Kernel>::SFace_const_handle(jt), vis);
				if (volume_index != std::numeric_limits<size_t>::max()) {
					vis.write(ofs);
					return true;
				}
			}
		}
	}
	vis.write(ofs);
	return volume_index == std::numeric_limits<size_t>::max();
}

#endif