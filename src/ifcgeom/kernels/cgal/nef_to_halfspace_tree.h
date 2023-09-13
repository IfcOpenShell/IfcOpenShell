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

#include <memory>
#include <functional>

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

template <typename Kernel>
struct PlaneHash {
	size_t operator()(const CGAL::Plane_3<Kernel>& plane) const
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

template <typename Kernel>
std::string dump_facet(typename CGAL::Nef_polyhedron_3<Kernel>::Halffacet_const_handle h) {
	typedef CGAL::Nef_polyhedron_3<Kernel>::SHalfedge_const_handle SHalfedge_const_handle;
	typedef CGAL::Nef_polyhedron_3<Kernel>::SHalfedge_around_facet_const_circulator SHalfedge_around_facet_const_circulator;

	std::ostringstream oss;

	const auto& p = h->plane();
	oss << "F plane=" << p << std::endl;
	h->facet_cycles_begin();

	auto fc = h->facet_cycles_begin();
	auto se = SHalfedge_const_handle(fc);
	CGAL_assertion(se != 0);
	SHalfedge_around_facet_const_circulator hc_start(se);
	SHalfedge_around_facet_const_circulator hc_end(hc_start);
	CGAL_For_all(hc_start, hc_end) {
		oss << "  co=" << hc_start->source()->center_vertex()->point() << std::endl;
	}

	oss << std::endl;
	return oss.str();
}

enum halfspace_operation {
	OP_UNION, OP_SUBTRACTION, OP_INTERSECTION
};

template <typename Kernel>
using plane_map = std::map<typename Kernel::Plane_3, typename Kernel::Plane_3, PlaneLess<Kernel>>;

template <typename Kernel>
class halfspace_tree {
public:
	virtual CGAL::Nef_polyhedron_3<Kernel> evaluate(int level = 0) const = 0;
	virtual void accumulate(std::list<typename Kernel::Plane_3>&) const = 0;
	virtual std::unique_ptr<halfspace_tree> map(const plane_map<Kernel>&) const = 0;
};

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

	std::vector<Point_d> planes_as_point;

	for (auto& p : planes) {
		// @todo can we skip normalization (simply divide by largest component perhaps)
		double l = std::sqrt(CGAL::to_double(p.orthogonal_vector().squared_length()));
		// @todo how to properly initialize using p._().exact() without converting to double?
		Point_d pp(CGAL::to_double(p.a()) / l, CGAL::to_double(p.b()) / l, CGAL::to_double(p.c()) / l, CGAL::to_double(p.d()) / l);
		planes_as_point.push_back(pp);
	}

	// @todo should we have a proper distance metric for plane equations
	Tree kdtree(planes_as_point.begin(), planes_as_point.end());

	auto plit = planes.begin();
	for (size_t i = 0; i < planes.size(); ++i) {
		auto& query = planes_as_point[i];
		Fuzzy_sphere fs(query, search_radius, 0.);
		// std::cout << "q " << query << std::endl;

		std::list<Point_d> results;
		kdtree.search(std::back_inserter(results), fs);
		for (auto& r : results) {
			// std::cout << " " << r << std::endl;
		}
		auto sum = std::accumulate(++results.begin(), results.end(), results.front(), [](Point_d a, Point_d b) {return Point_d(a[0] + b[0], a[1] + b[1], a[2] + b[2], a[3] + b[3]); });
		int N = results.size();
		results.clear();

		// Search for the negation of the query point as well.
		// @todo should we rather make sure planes are filtered to one hemisphere before inserted?
		Point_d n(-query[0], -query[1], -query[2], -query[3]);
		Fuzzy_sphere fsn(n, search_radius, 0.);
		kdtree.search(std::back_inserter(results), fsn);
		for (auto& r : results) {
			// std::cout << " " << r << std::endl;
		}
		N += results.size();
		auto sum2 = std::accumulate(results.begin(), results.end(), sum, [](Point_d a, Point_d b) {return Point_d(a[0] - b[0], a[1] - b[1], a[2] - b[2], a[3] - b[3]); });

		// It is imperative that there are no rounding errors, I think that's covered by using the Point_d
		// (even if we populated it inaccurately using doubles and sqrt).
		auto avg = Kernel::Plane_3(sum[0] / N, sum[1] / N, sum[2] / N, sum[3] / N);

		// std::cout << *plit << " -> " << avg << std::endl;
		result.insert({ *plit++, avg });
	}

	return result;
}


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
		normalized_to_original.insert({pp, p});
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


template <typename Kernel>
class halfspace_tree_nary_branch : public halfspace_tree<Kernel> {
private:
	halfspace_operation operation_;
	std::list<std::unique_ptr<halfspace_tree<Kernel>>> operands_;

public:
	halfspace_tree_nary_branch(halfspace_operation operation, std::list<std::unique_ptr<halfspace_tree<Kernel>>>&& operands)
		: operation_(operation)
		, operands_(std::move(operands))
	{}
	virtual CGAL::Nef_polyhedron_3<Kernel> evaluate(int level) const {
		static const char* const ops[] = { "union", "subtraction", "intersection" };
		// std::cout << std::string(level * 2, ' ') << ops[operation_] << " (" << std::endl;

		CGAL::Nef_polyhedron_3<Kernel> result;

		if (operation_ == OP_SUBTRACTION) {
			if (operands_.size() != 2) {
				throw std::runtime_error("");
			}
			result = operands_.front()->evaluate(level + 1) - operands_.back()->evaluate(level + 1);
		} else if (operation_ == OP_UNION) {
			CGAL::Nef_nary_union_3<CGAL::Nef_polyhedron_3<Kernel>> builder;
			for (auto& op : operands_) {
				builder.add_polyhedron(op->evaluate(level + 1));
			}
			result = builder.get_union();
		} else if (operation_ == OP_INTERSECTION) {
			CGAL::Nef_nary_intersection_3<CGAL::Nef_polyhedron_3<Kernel>> builder;
			for (auto& op : operands_) {
				builder.add_polyhedron(op->evaluate(level + 1));
			}
			result = builder.get_intersection();

			/*
			CGAL::Nef_polyhedron_3<Kernel> r;
			bool first = true;
			for (auto& op : operands_) {
				if (first) {
					r = op->evaluate(level + 1);
					first = false;
					continue;
				}
				r = r * op->evaluate(level + 1);
			}
			return r;
			*/
		}

		// std::cout << std::string(level * 2, ' ') << ")" << std::endl;

		return result;
	}
	virtual void accumulate(std::list<typename Kernel::Plane_3>& points) const {
		for (auto& op : operands_) {
			op->accumulate(points);
		}
	}
	virtual std::unique_ptr<halfspace_tree<Kernel>> map(const std::map<typename Kernel::Plane_3, typename Kernel::Plane_3, PlaneLess<Kernel>>& m) const {
		decltype(operands_) mapped;
		for (auto& op : operands_) {
			mapped.emplace_back(op->map(m));
		}
		return std::unique_ptr<halfspace_tree<Kernel>>(new halfspace_tree_nary_branch(operation_, std::move(mapped)));
	}
};

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

	typename Kernel::Vector_3 V(0, 0, d * 2);

	extrude(bottom, V, P);
}

template <typename Kernel>
class halfspace_tree_plane : public halfspace_tree<Kernel> {
private:
	typename Kernel::Plane_3 plane_;

public:
	halfspace_tree_plane(const typename Kernel::Plane_3& plane)
		: plane_(plane)
	{}
	virtual CGAL::Nef_polyhedron_3<Kernel> evaluate(int level) const {
		// std::cout << std::string(level * 2, ' ') << "p " << plane_ << std::endl;

		if constexpr(CGAL::Is_extended_kernel<Kernel>::value_type::value) {
			static_assert(false, "Not implemented yet");
			// typename Kernel::Plane_3 plane(plane_.a().exact(), plane_.b().exact(), plane_.c().exact(), plane_.d().exact());
			// CGAL::Nef_polyhedron_3<Kernel> plane_nef(plane, CGAL::Nef_polyhedron_3<Kernel>::Boundary::INCLUDED);
			// CGAL::Nef_polyhedron_3<Kernel> full_nef(full);
			// auto two_halfspaces = full_nef - plane_nef;
			// @todo
		} else {
			static auto almost_complete = []() {
				CGAL::Polyhedron_3<Kernel> P;
				createCube(P, 10000);
				return CGAL::Nef_polyhedron_3<Kernel>(P);
			}();
			return almost_complete.intersection(plane_.opposite(), CGAL::Nef_polyhedron_3<Kernel>::CLOSED_HALFSPACE);
		}
	}
	virtual void accumulate(std::list<typename Kernel::Plane_3>& points) const {
		points.push_back(plane_);
	}
	virtual std::unique_ptr<halfspace_tree<Kernel>> map(const std::map<typename Kernel::Plane_3, typename Kernel::Plane_3, PlaneLess<Kernel>>& m) const {
		auto it = m.find(plane_);
		if (it != m.end()) {
			return std::unique_ptr<halfspace_tree<Kernel>>(new halfspace_tree_plane(it->second));
		} else {
			return std::unique_ptr<halfspace_tree<Kernel>>(new halfspace_tree_plane(plane_));
		}
	}
};

template <typename Kernel>
std::vector<CGAL::Triangle_3<Kernel>> triangulate_nef_facet(typename CGAL::Nef_polyhedron_3<Kernel>::Halffacet_const_handle f) {
	typedef CGAL::Nef_polyhedron_3<Kernel>::SHalfedge_around_facet_const_circulator SHalfedge_around_facet_const_circulator;

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

template <typename Kernel>
Graph<Kernel> build_facet_edge_graph(const CGAL::Nef_polyhedron_3<Kernel>& poly) {
	typedef CGAL::Nef_polyhedron_3<Kernel>::Halffacet_const_handle Halffacet_const_handle;

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

	for (size_t ii = 0; ii < boost::num_vertices(G); ++ii) {
		// std::cout << ii << " " << dump_facet<Kernel>(G[ii].facet) << std::endl;
	}

	return G;
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

template <typename Kernel, typename ComponentMap>
class convex_subcomponent_visitor : public boost::default_bfs_visitor {

private:
	EdgeType edgetype_;
	ComponentMap& components_;

public:
	convex_subcomponent_visitor(EdgeType edgetype, ComponentMap& component)
		: edgetype_(edgetype), components_(component) {}

	template <typename Edge, typename Graph>
	void tree_edge(Edge e, const Graph& g) {
		if (boost::get(boost::edge_weight, g, e) == edgetype_) {
			auto srcid = boost::source(e, g);
			auto tgtid = boost::target(e, g);

			auto src = &components_[srcid];
			auto tgt = &components_[tgtid];

			if (*src == -1) {
				std::swap(srcid, tgtid);
				std::swap(src, tgt);
			}

			if (*tgt == -1) {
				bool tgt_has_any_reflex_edge = false;

				typename boost::graph_traits<Graph>::out_edge_iterator ei, ei_end;
				for (boost::tie(ei, ei_end) = boost::out_edges(tgtid, g); ei != ei_end; ++ei) {
					if (boost::get(boost::edge_weight, g, *ei) != edgetype_) {
						tgt_has_any_reflex_edge = true;
						break;
					}
				}

				if (!tgt_has_any_reflex_edge) {
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

								// std::cout << "i " << i << ": " << std::endl;
								for (auto& t : triangles_i) {
									// std::cout << "  " << t << std::endl;
								}

								if (std::any_of(triangles_i.begin(), triangles_i.end(), [&plane_tgt](CGAL::Triangle_3<Kernel>& t) {
									auto x = CGAL::intersection(plane_tgt, t);
									if (x) {
										// std::cout << "t " << t << " x " << std::endl;
										// Intersection_visitor v;
										// boost::apply_visitor([](auto x) {std::cout << x << std::endl; })(*x);
									}
									return (bool)x;
								})) {
									any_intersecting = true;
									break;
								}
							}
						}
					}
					if (!any_intersecting) {
						// std::cout << "v " << srcid << " -> " << tgtid << std::endl;
						// std::cout << "(" << *src << " " << *tgt << ")" << std::endl;

						*tgt = *src;
					}
				}
			}
		}
	}
};

template <typename Kernel, typename TreeKernel=Kernel>
std::unique_ptr<halfspace_tree<TreeKernel>> build_halfspace_tree(Graph<Kernel>& G, CGAL::Nef_polyhedron_3<Kernel>& poly, bool negate = false) {
	typedef boost::filtered_graph<Graph<Kernel>, boost::keep_all, std::function<bool(Graph<Kernel>::vertex_descriptor)>> FilteredGraph;

	auto edge_trait = negate ? CONCAVE : CONVEX;

	bool all_convex = true;
	typename boost::graph_traits<Graph<Kernel>>::edge_iterator ei, ei_end;
	for (boost::tie(ei, ei_end) = boost::edges(G); ei != ei_end; ++ei) {
		if (boost::get(boost::edge_weight, G, *ei) != edge_trait) {
			// all_convex = false;
			break;
		}
	}

	if (!all_convex) {
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

		convex_subcomponent_visitor<Kernel, decltype(components)> visitor(edge_trait, components);
		int num_components = 0;
		for (size_t i = 0; i < boost::num_vertices(sub_graph_0); ++i) {
			if (components[i] == -1) {
				components[i] = num_components++;
				boost::breadth_first_search(sub_graph_0, boost::vertex(i, sub_graph_0), boost::visitor(visitor));
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
			auto remainder = build_halfspace_tree<Kernel, TreeKernel>(sub_graph, poly, !negate);

			std::list<std::unique_ptr<halfspace_tree<TreeKernel>>> sub_expression;
			sub_expression.emplace_back(std::move(tree));
			sub_expression.emplace_back(std::move(remainder));

			tree.reset(new halfspace_tree_nary_branch<TreeKernel>(OP_SUBTRACTION, std::move(sub_expression)));
		}

		root_expression_0.emplace_back(std::move(tree));
	}

	if (root_expression_0.size() == 1) {
		return std::move(root_expression_0.front());
	}
	tree_0.reset(new halfspace_tree_nary_branch<TreeKernel>(OP_UNION, std::move(root_expression_0)));
	return std::move(tree_0);
}

#endif