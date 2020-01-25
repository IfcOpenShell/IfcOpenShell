#include "../ifcgeom/kernels/cgal/CgalKernel.h"
#include "../ifcgeom/schema_agnostic/IfcGeomFilter.h"
#include "../ifcgeom/schema_agnostic/IfcGeomIterator.h"

#include <CGAL/box_intersection_d.h>
#include <CGAL/minkowski_sum_3.h>

#include <CGAL/Surface_mesh.h>
#include <CGAL/Surface_mesh_simplification/edge_collapse.h>
#include <CGAL/Surface_mesh_simplification/Policies/Edge_collapse/Edge_length_stop_predicate.h>
#include <CGAL/Surface_mesh_simplification/Policies/Edge_collapse/Edge_length_cost.h>
#include <CGAL/Surface_mesh_simplification/Edge_collapse_visitor_base.h>
namespace SMS = CGAL::Surface_mesh_simplification;

#include <fstream>
#include <iostream>

template <typename T>
T enlarge(const T& t, double d = 1.e-5) {
	T::NT min[3];
	T::NT max[3];
	for (int i = 0; i < t.dimension(); ++i) {
		min[i] = t.min_coord(i) - d;
		max[i] = t.max_coord(i) + d;
	}
	return T(min, max, t.handle());
	// return T(min, max);
}

int convert_to_nef(cgal_shape_t& shape, CGAL::Nef_polyhedron_3<Kernel_>& result) {
	if (!shape.is_valid()) {
		return 1;
	}

	if (!shape.is_closed()) {
		return 2;
	}

	bool success = false;

	try {
		success = CGAL::Polygon_mesh_processing::triangulate_faces(shape);
	} catch (...) {
		return 3;
	}

	if (!success) {
		return 4;
	}

	if (CGAL::Polygon_mesh_processing::does_self_intersect(shape)) {
		return 5;
	}

	try {
		result = CGAL::Nef_polyhedron_3<Kernel_>(shape);
	} catch (...) {
		return 6;
	}

	return 0;
}

namespace {
	// Can be used to convert polyhedron from exact to inexact and vice-versa
	template <class Polyhedron_input,
		class Polyhedron_output>
		struct Copy_polyhedron_to
		: public CGAL::Modifier_base<typename Polyhedron_output::HalfedgeDS> {
		Copy_polyhedron_to(const Polyhedron_input& in_poly)
			: in_poly(in_poly) {}

		void operator()(typename Polyhedron_output::HalfedgeDS& out_hds) {
			typedef typename Polyhedron_output::HalfedgeDS Output_HDS;
			typedef typename Polyhedron_input::HalfedgeDS Input_HDS;

			CGAL::Polyhedron_incremental_builder_3<Output_HDS> builder(out_hds);

			typedef typename Polyhedron_input::Vertex_const_iterator Vertex_const_iterator;
			typedef typename Polyhedron_input::Facet_const_iterator  Facet_const_iterator;
			typedef typename Polyhedron_input::Halfedge_around_facet_const_circulator HFCC;

			builder.begin_surface(in_poly.size_of_vertices(),
				in_poly.size_of_facets(),
				in_poly.size_of_halfedges());

			for (Vertex_const_iterator
				vi = in_poly.vertices_begin(), end = in_poly.vertices_end();
				vi != end; ++vi) {
				typename Polyhedron_output::Point_3 p(::CGAL::to_double(vi->point().x()),
					::CGAL::to_double(vi->point().y()),
					::CGAL::to_double(vi->point().z()));
				builder.add_vertex(p);
			}

			typedef CGAL::Inverse_index<Vertex_const_iterator> Index;
			Index index(in_poly.vertices_begin(), in_poly.vertices_end());

			for (Facet_const_iterator
				fi = in_poly.facets_begin(), end = in_poly.facets_end();
				fi != end; ++fi) {
				HFCC hc = fi->facet_begin();
				HFCC hc_end = hc;
				builder.begin_facet();
				do {
					builder.add_vertex_to_facet(index[hc->vertex()]);
					++hc;
				} while (hc != hc_end);
				builder.end_facet();
			}
			builder.end_surface();
		} // end operator()(..)
		private:
			const Polyhedron_input& in_poly;
	}; // end Copy_polyhedron_to<>

	template <class Poly_B, class Poly_A>
	void poly_copy(Poly_B& poly_b, const Poly_A& poly_a) {
		poly_b.clear();
		Copy_polyhedron_to<Poly_A, Poly_B> modifier(poly_a);
		poly_b.delegate(modifier);
	}

}

namespace {
	// The following is a Visitor that keeps track of the simplification process.
// In this example the progress is printed real-time and a few statistics are
// recorded (and printed in the end).
//
	struct Stats {
		Stats()
			: collected(0)
			, processed(0)
			, collapsed(0)
			, non_collapsable(0)
			, cost_uncomputable(0)
			, placement_uncomputable(0) {}

		std::size_t collected;
		std::size_t processed;
		std::size_t collapsed;
		std::size_t non_collapsable;
		std::size_t cost_uncomputable;
		std::size_t placement_uncomputable;
	};
	struct My_visitor : SMS::Edge_collapse_visitor_base<CGAL::Polyhedron_3<CGAL::Simple_cartesian<double>>> {
		My_visitor(Stats* s) : stats(s) {}
		// Called during the collecting phase for each edge collected.
		void OnCollected(Profile const&, boost::optional<double> const&) {
			++stats->collected;
			std::wcerr << "\rEdges collected: " << stats->collected << std::flush;
		}

		// Called during the processing phase for each edge selected.
		// If cost is absent the edge won't be collapsed.
		void OnSelected(Profile const&
			, boost::optional<double> cost
			, std::size_t             initial
			, std::size_t             current
		) {
			++stats->processed;
			if (!cost)
				++stats->cost_uncomputable;

			if (current == initial)
				std::wcerr << "\n" << std::flush;
			std::wcerr << "\r" << current << std::flush;
		}

		// Called during the processing phase for each edge being collapsed.
		// If placement is absent the edge is left uncollapsed.
		void OnCollapsing(Profile const&
			, boost::optional<Point>  placement
		) {
			if (!placement)
				++stats->placement_uncomputable;
		}

		// Called for each edge which failed the so called link-condition,
		// that is, which cannot be collapsed because doing so would
		// turn the surface mesh into a non-manifold.
		void OnNonCollapsable(Profile const&) {
			++stats->non_collapsable;
		}

		// Called after each edge has been collapsed
		void OnCollapsed(Profile const&, vertex_descriptor) {
			++stats->collapsed;
		}

		Stats* stats;
	};

}

namespace {
	template <typename T>
	T approx_normalized(const T& t) {
		return t * (1. / Kernel_::FT(CGAL::sqrt(CGAL::to_double(t.squared_length()))));
	}
}

#include <CGAL/AABB_tree.h>
#include <CGAL/AABB_traits.h>
#include <CGAL/Polyhedron_3.h>
#include <CGAL/AABB_face_graph_triangle_primitive.h>

namespace {
	template <class HDS>
	struct Build_Offset : public CGAL::Modifier_base<HDS> {
		std::list<cgal_shape_t::Facet_handle> input;

		void operator()(HDS& hds) {
			// Postcondition: hds is a valid polyhedral surface.
			CGAL::Polyhedron_incremental_builder_3<HDS> B(hds);

			int Nv = 0, Nf = 0;
			for (auto& f : input) {
				Nv += 3;
				Nf += 1;
			}

			B.begin_surface(Nv, Nf);

			for (auto& f : input) {
				auto p0 = f->facet_begin()->vertex()->point();
				auto p1 = f->facet_begin()->next()->vertex()->point();
				auto p2 = f->facet_begin()->next()->next()->vertex()->point();

				auto O = CGAL::centroid(p0, p1, p2);

				Kernel_::Point_3* p012[3] = { &p0, &p1, &p2 };
				for (int i = 0; i < 3; ++i) {
					*p012[i] = CGAL::ORIGIN + (((*(p012[i])) - CGAL::ORIGIN) + ((*(p012[i])) - O));
					B.add_vertex(*p012[i]);
				}
			}

			Nv = 0;
			for (int i = 0; i < Nf; ++i) {
				B.begin_facet();
				B.add_vertex_to_facet(Nv++);
				B.add_vertex_to_facet(Nv++);
				B.add_vertex_to_facet(Nv++);
				B.end_facet();
			}

			B.end_surface();
		}
	};

	template <typename Ts>
	std::list<cgal_shape_t::Facet_handle> connected_faces(cgal_shape_t::Facet_handle& f, const Ts& excluded) {
		std::set<cgal_shape_t::Facet_handle> fs = { f };

		std::function<void(cgal_shape_t::Facet_handle& f)> process;
		process = [&fs, &process, &excluded](cgal_shape_t::Facet_handle& f) {
			cgal_shape_t::Halfedge_around_facet_circulator circ = f->facet_begin(), end(circ);
			do {
				auto ff = circ->opposite()->facet();
				if (excluded.find(ff) == excluded.end()) {
					auto p = fs.insert(ff);
					if (p.second) {
						process(ff);
					}
				}
			} while (++circ != end);
		};

		process(f);
		return std::list<cgal_shape_t::Facet_handle>(fs.begin(), fs.end());
	}

	template <class HDS>
	struct Builder_With_Map : public CGAL::Modifier_base<HDS> {
		std::list<cgal_shape_t::Facet_handle> input;
		std::map<Kernel_::Point_3, Kernel_::Point_3> mapping;

		void operator()(HDS& hds) {
			// Postcondition: hds is a valid polyhedral surface.
			CGAL::Polyhedron_incremental_builder_3<HDS> B(hds);

			std::set<Kernel_::Point_3> used_points;

			for (auto& f : input) {
				cgal_shape_t::Halfedge_around_facet_circulator circ = f->facet_begin(), end(circ);
				do {
					auto P = circ->vertex()->point();
					auto it = mapping.find(P);
					if (it == mapping.end()) {
						std::wcout << "WARNING unprojected point :(" << std::endl;
					} else {
						P = it->second;
					}
					used_points.insert(P);
				} while (++circ != end);
			}

			B.begin_surface(used_points.size(), input.size());

			for (auto& p : used_points) {
				B.add_vertex(p);
			}

			for (auto& f : input) {
				B.begin_facet();
				cgal_shape_t::Halfedge_around_facet_circulator circ = f->facet_begin(), end(circ);
				do {
					auto P = circ->vertex()->point();
					auto it = mapping.find(P);
					if (it == mapping.end()) {
						std::wcout << "WARNING unprojected point :(" << std::endl;
					} else {
						P = it->second;
					}

					auto jt = used_points.find(P);
					if (jt == used_points.end()) {
						throw std::runtime_error("Unable to map point");
					}
					size_t idx = std::distance(used_points.begin(), jt);
					std::wcout << "idx " << idx << std::endl;
					B.add_vertex_to_facet(idx);
				} while (++circ != end);

				B.end_facet();
			}

			B.end_surface();
		}
	};
}

namespace {
	template <typename T>
	T edge_collapse(T polyhedron) {
		typedef CGAL::Simple_cartesian<double> simple;
		CGAL::Polyhedron_3<simple> simple_poly;
		poly_copy(simple_poly, polyhedron);

		// flattening from a thin box to a plane is not valid in edge_collapse()
		Stats stats;
		My_visitor vis(&stats);
		SMS::Edge_length_cost<double> elc;
		SMS::Edge_length_stop_predicate<double> stop(1.e-3);

		int r = SMS::edge_collapse(simple_poly, stop,
			CGAL::parameters::vertex_index_map(get(CGAL::vertex_external_index, simple_poly))
			.halfedge_index_map(get(CGAL::halfedge_external_index, simple_poly))
			.visitor(vis)
			.get_cost(elc)
		);

		std::wcout << "Removed: " << r << std::endl;

		T result;
		poly_copy(result, simple_poly);
		return result;
	}


	double facet_area(const cgal_shape_t::Facet_handle& f) {
		auto p0 = f->facet_begin()->vertex()->point();
		auto p1 = f->facet_begin()->next()->vertex()->point();
		auto p2 = f->facet_begin()->next()->next()->vertex()->point();
		return std::sqrt(CGAL::to_double(CGAL::cross_product(p0 - p1, p2 - p1).squared_length()));
	}

	void dump_facet(const cgal_shape_t::Facet_handle& f) {
		auto p0 = f->facet_begin()->vertex()->point();
		auto p1 = f->facet_begin()->next()->vertex()->point();
		auto p2 = f->facet_begin()->next()->next()->vertex()->point();
		auto V = CGAL::cross_product(p0 - p1, p2 - p1);
		auto d = std::sqrt(CGAL::to_double(V.squared_length()));
		if (d > 1.e-20) {
			V /= d;
		}

		std::ostringstream oss;
		oss.precision(8);
		oss << "Facet with area " << facet_area(f) << " and normal ("
			<< CGAL::to_double(V.cartesian(0)) << " " << CGAL::to_double(V.cartesian(1)) << " "
			<< CGAL::to_double(V.cartesian(2)) << ")";

		auto osss = oss.str();
		std::wcout << osss.c_str() << std::endl;
	}

	struct remove_thickness {
		typedef Kernel_::Point_3 Point;
		typedef Kernel_::Plane_3 Plane;
		typedef Kernel_::Vector_3 Vector;
		typedef Kernel_::Segment_3 Segment;
		typedef Kernel_::Ray_3 Ray;

		typedef CGAL::Polyhedron_3<Kernel_> Polyhedron;
		typedef CGAL::AABB_face_graph_triangle_primitive<Polyhedron> Primitive;
		typedef CGAL::AABB_traits<Kernel_, Primitive> Traits;
		typedef CGAL::AABB_tree<Traits> Tree;
		typedef boost::optional<Tree::Intersection_and_primitive_id<Ray>::Type> Ray_intersection;

		cgal_shape_t polyhedron, polyhedron2, flattened;

		remove_thickness(const cgal_shape_t& p)
			// edge_collapse(p) still does not work :(
			: polyhedron(p)
			, polyhedron2(p) {
			CGAL::Polygon_mesh_processing::triangulate_faces(polyhedron);
			CGAL::Polygon_mesh_processing::triangulate_faces(polyhedron2);

			std::list<cgal_shape_t::Facet_handle> non_degenerate, degenerate, longitudonal;
			std::set<cgal_shape_t::Facet_iterator> thin_sides;

			std::wcout << "ALL FACES:" << std::endl;

			for (auto& f : faces(polyhedron)) {
				dump_facet(f);
				if (facet_area(f) > 1.e-20) {
					non_degenerate.push_back(f);
				} else {
					degenerate.push_front(f);
					std::wcout << "Degenerate, area: " << facet_area(f) << std::endl;
				}
			}

			std::wcout << "NON DEGENERATE:" << std::endl;
			for (auto& f : non_degenerate) {
				dump_facet(f);
			}

			cgal_shape_t enlarged_non_degenerate_triangles;
			Build_Offset<cgal_shape_t::HDS> bo;
			bo.input = non_degenerate;
			enlarged_non_degenerate_triangles.delegate(bo);

			// @todo, first on non-enlarged faces, then on enlarged; to fix projection on concave surfaces where the enlarging operation shortens projection distances.

			Tree tree(faces(enlarged_non_degenerate_triangles).first, faces(enlarged_non_degenerate_triangles).second, enlarged_non_degenerate_triangles);

			std::map<cgal_face_descriptor_t, Kernel_::Vector_3> face_normals;
			boost::associative_property_map<std::map<cgal_face_descriptor_t, Kernel_::Vector_3>> face_normals_map(face_normals);
			CGAL::Polygon_mesh_processing::compute_face_normals(polyhedron, face_normals_map);

			for (auto& f : non_degenerate) {
				auto O = CGAL::centroid(
					f->facet_begin()->vertex()->point(),
					f->facet_begin()->next()->vertex()->point(),
					f->facet_begin()->next()->next()->vertex()->point()
				);

				Ray ray(O, -face_normals_map[f]);

				std::list<Ray_intersection> intersections;
				tree.all_intersections(ray, std::back_inserter(intersections));
				double N = std::numeric_limits<double>::infinity();
				Point P;
				for (auto& intersection : intersections) {
					if (boost::get<Point>(&(intersection->first))) {
						const Point* p = boost::get<Point>(&(intersection->first));
						const double d = std::sqrt(CGAL::to_double((*p - O).squared_length()));
						if (d > 1.e-20 && d < N) {
							N = d;
						}
					}
				}
				if (N != std::numeric_limits<double>::infinity() && N > 1.e-4) {
					thin_sides.insert(f);
				}

				/*
				Ray_intersection intersection = tree.first_intersection(ray, [f](const cgal_shape_t::Facet_handle& p) {
					return p == f;
				});
				if (intersection) {
					if (boost::get<Point>(&(intersection->first))) {
						const Point* p = boost::get<Point>(&(intersection->first));
						const double d = std::sqrt(CGAL::to_double((*p - O).squared_length()));
						if (d > 1.e-4) {
							thin_sides.insert(f);
						}
					}
				} else {
					std::wcout << "No intersection :((!!!" << std::endl;
				}
				*/
			}

			std::wcout << "THIN SIDES:" << std::endl;
			for (auto& f : thin_sides) {
				dump_facet(f);
			}

			for (auto& f : non_degenerate) {
				if (thin_sides.find(f) == thin_sides.end()) {
					longitudonal.push_back(f);
				}
			}

			std::wcout << "LONGITUDONAL:" << std::endl;
			for (auto& f : longitudonal) {
				dump_facet(f);
			}

			std::wcout << "faces " << faces(polyhedron).size() << "long " << longitudonal.size() << "thin " << thin_sides.size() << "non-degen " << non_degenerate.size() << std::endl;

			cgal_shape_t enlarged_indiv_triangles;
			Build_Offset<cgal_shape_t::HDS> bo2;
			bo2.input = longitudonal;
			enlarged_indiv_triangles.delegate(bo2);

			{
				std::ofstream ofs("enlarged.off");
				ofs.precision(17);
				ofs << enlarged_indiv_triangles;
			}

			Tree tree2(faces(enlarged_indiv_triangles).begin(), faces(enlarged_indiv_triangles).end(), enlarged_indiv_triangles);

			// std::map<cgal_face_descriptor_t, Kernel_::Vector_3> face_normals_2;
			// boost::associative_property_map<std::map<cgal_face_descriptor_t, Kernel_::Vector_3>> face_normals_map_2(face_normals_2);
			// CGAL::Polygon_mesh_processing::compute_face_normals(polyhedron, face_normals_map_2);

			// below does not seem to work? Do manually?
			// std::map<cgal_vertex_descriptor_t, Kernel_::Vector_3> vertex_normals;
			// boost::associative_property_map<std::map<cgal_vertex_descriptor_t, Kernel_::Vector_3>> vertex_normals_map(vertex_normals);
			// CGAL::Polygon_mesh_processing::compute_normals(polyhedron, vertex_normals_map, face_normals_map_2);

			std::map<Kernel_::Point_3, Kernel_::Point_3> new_points;

			for (Polyhedron::Facet_iterator fit = polyhedron.facets_begin();
				fit != polyhedron.facets_end();
				++fit) {
				if (CGAL::collinear(
					fit->halfedge()->vertex()->point(),
					fit->halfedge()->next()->vertex()->point(),
					fit->halfedge()->opposite()->vertex()->point())) {
					std::wcout << "degenerate triangle" << std::endl;
				}
			}

			/*
			std::list<cgal_shape_t::Vertex_handle> vertices;
			for (auto& f : non_degenerate) {
				CGAL::Face_around_target_circulator<cgal_shape_t> it(f->halfedge(), polyhedron), end(it);
				do {
					vertices.push_back((*it)->halfedge()->vertex());
					++it;
				} while (it != end);
			}*/


			for (auto& v : vertices(polyhedron)) {
				auto O = v->point();

				Kernel_::Vector_3 norm;
				Kernel_::Vector_3 accum;
				int count = 0;
				CGAL::Face_around_target_circulator<cgal_shape_t> it(v->halfedge(), polyhedron), end(it);
				do {
					cgal_shape_t::Facet_handle fh = (*it)->halfedge()->facet();

					auto jt = std::find(non_degenerate.begin(), non_degenerate.end(), fh);
					std::wcout << "non degen: " << (jt != non_degenerate.end()) << std::endl;
					auto kt = std::find(thin_sides.begin(), thin_sides.end(), fh);
					std::wcout << "thin side: " << (kt != thin_sides.end()) << std::endl;
					if (jt != non_degenerate.end() && kt == thin_sides.end()) {
						// else degenerate, prevent div by zero, do not incorporate in vnorm.
						// or else part of thin side

						auto p0 = (*it)->facet_begin()->vertex()->point();
						auto p1 = (*it)->facet_begin()->next()->vertex()->point();
						auto p2 = (*it)->facet_begin()->next()->next()->vertex()->point();

						{
							std::ostringstream oss;
							oss.precision(8);
							oss << "p0 " << p0.cartesian(0) << " " << p0.cartesian(1) << " " << p0.cartesian(2) << "\n";
							oss << "p1 " << p1.cartesian(0) << " " << p1.cartesian(1) << " " << p1.cartesian(2) << "\n";
							oss << "p2 " << p2.cartesian(0) << " " << p2.cartesian(1) << " " << p2.cartesian(2) << "\n";
							auto osss = oss.str();
							std::wcout << osss.c_str() << std::endl;
						}

						auto fnorm = CGAL::cross_product(p0 - p1, p2 - p1);
						fnorm /= std::sqrt(CGAL::to_double(fnorm.squared_length()));

						// const auto& fnorm = face_normals_map_2[*it];
						std::ostringstream oss;
						oss.precision(8);
						oss << fnorm.cartesian(0) << " " << fnorm.cartesian(1) << " " << fnorm.cartesian(2);
						auto osss = oss.str();
						std::wcout << osss.c_str() << std::endl;
						accum += fnorm;

						++count;
					}

					++it;
				} while (it != end);

				norm = accum / count;
				std::wcout << "count " << count << std::endl;

				if (count == 0) {
					// part of only degenerate or only thin sides
					continue;
				}

				// v->vertex_begin();
				Ray ray(O, norm);
				std::ostringstream oss;
				oss.precision(8);
				oss << O << " -> " << norm;
				auto osss = oss.str();
				std::wcout << osss.c_str() << std::endl;

				//// skip does not work anymore because we have offset the facets
				// auto skip = [this, &v](const cgal_shape_t::Facet_handle& p) {
				// 	CGAL::Face_around_target_circulator<cgal_shape_t> it(v->halfedge(), polyhedron), end(it);
				// 	do {
				// 		if ((*it)->facet_begin()->facet() == p) {
				// 			return true;
				// 		}
				// 	} while (++it != end);
				// 	return false;
				// };

				std::list<Ray_intersection> intersections;
				tree2.all_intersections(ray, std::back_inserter(intersections));
				double N = std::numeric_limits<double>::infinity();
				Point P;

				bool used_intersection = false;

				if (intersections.size()) {
					for (auto& intersection : intersections) {
						if (boost::get<Point>(&(intersection->first))) {
							const Point* p = boost::get<Point>(&(intersection->first));
							const double d = std::sqrt(CGAL::to_double((*p - O).squared_length()));
							if (d < N && d > 1.e-20) {
								N = d;
								P = *p;
								std::wcout << "intersection @ " << d << std::endl;
							}
						}
					}
					std::wcout << "-----------" << std::endl;

					// average the new point
					new_points[O] = CGAL::ORIGIN + (((O - CGAL::ORIGIN) + (P - CGAL::ORIGIN))) / 2;
					used_intersection = true;
				}

				if (!used_intersection) {
					std::wcout << "no intersection :(" << std::endl;
				}
			}

			/*
			for (auto& fi : thin_sides) {
				auto f_circ = fi->facet_begin();
				polyhedron2.erase_facet(f_circ);
			}
			*/

			auto thin_sides_degenerate = thin_sides;
			thin_sides_degenerate.insert(degenerate.begin(), degenerate.end());

			// @todo choose connected / connected_opposing based on largest combined area of facets?

			auto connected = connected_faces(*longitudonal.begin(), thin_sides_degenerate);
			decltype(connected) connected_opposing;

			for (auto& f : longitudonal) {
				if (std::find(connected.begin(), connected.end(), f) == connected.end()) {
					connected_opposing = connected_faces(f, thin_sides_degenerate);

					std::set<cgal_shape_t::Facet_handle> longi(longitudonal.begin(), longitudonal.end());
					std::set<cgal_shape_t::Facet_handle> both_sides(connected.begin(), connected.end());
					both_sides.insert(connected_opposing.begin(), connected_opposing.end());

					if (longi == both_sides) {
						std::wcout << "Facet connection functioning properly" << std::endl;
					} else {
						std::wcout << "Facet connection functioning incorrectly" << std::endl;
					}

					break;
				}
			}

			Builder_With_Map<cgal_shape_t::HDS> b2;
			b2.input = connected;
			b2.mapping = new_points;

			flattened.delegate(b2);
		}
	};
}

void fix_spaceboundaries(IfcParse::IfcFile& f, bool no_progress, bool quiet, bool stderr_progress) {
	typedef std::list<std::pair<IfcUtil::IfcBaseEntity*, CGAL::Nef_polyhedron_3<Kernel_>> > nefs_t;
	typedef CGAL::Box_intersection_d::Box_with_handle_d<double, 3, nefs_t::value_type*> Box;
	// typedef CGAL::Box_intersection_d::Box_d<double, 3, CGAL::Box_intersection_d::ID_EXPLICIT> Box;
	// std::map<size_t, nefs_t::value_type*> id_map;

	ifcopenshell::geometry::settings settings;
	settings.set(ifcopenshell::geometry::settings::USE_WORLD_COORDS, false);
	settings.set(ifcopenshell::geometry::settings::WELD_VERTICES, false);
	settings.set(ifcopenshell::geometry::settings::SEW_SHELLS, true);
	settings.set(ifcopenshell::geometry::settings::CONVERT_BACK_UNITS, true);
	settings.set(ifcopenshell::geometry::settings::DISABLE_TRIANGULATION, true);
	settings.set(ifcopenshell::geometry::settings::DISABLE_OPENING_SUBTRACTIONS, true);

	std::vector<ifcopenshell::geometry::filter_t> spaces_and_walls = {
		IfcGeom::entity_filter(true, false, {"IfcWall", "IfcSpace"})
	};

	ifcopenshell::geometry::Iterator context_iterator("cgal", settings, &f, spaces_and_walls);

	if (!context_iterator.initialize()) {
		return;
	}

	auto kernel = (ifcopenshell::geometry::kernels::CgalKernel*) context_iterator.converter().kernel();
	auto cube = kernel->precision_cube();

	size_t num_created = 0;
	int old_progress = quiet ? 0 : -1;

	std::vector<Box> boxes;
	nefs_t nefs;

	for (;; ++num_created) {
		bool has_more = true;
		if (num_created) {
			has_more = context_iterator.next();
		}
		ifcopenshell::geometry::NativeElement* geom_object = nullptr;
		if (has_more) {
			geom_object = context_iterator.get_native();
		}
		if (!geom_object) {
			break;
		}

		std::stringstream ss;
		ss << geom_object->product()->data().toString();
		auto sss = ss.str();
		std::wcout << sss.c_str() << std::endl;

		for (auto& g : geom_object->geometry()) {
			auto s = ((ifcopenshell::geometry::CgalShape*) g.Shape())->shape();
			const auto& m = g.Placement().components;
			const auto& n = geom_object->transformation().data().components;

			const cgal_placement_t trsf(
				m(0, 0), m(0, 1), m(0, 2), m(0, 3),
				m(1, 0), m(1, 1), m(1, 2), m(1, 3),
				m(2, 0), m(2, 1), m(2, 2), m(2, 3));

			const cgal_placement_t trsf2(
				n(0, 0), n(0, 1), n(0, 2), n(0, 3),
				n(1, 0), n(1, 1), n(1, 2), n(1, 3),
				n(2, 0), n(2, 1), n(2, 2), n(2, 3));

			// Apply transformation
			for (auto &vertex : vertices(s)) {
				vertex->point() = vertex->point().transform(trsf).transform(trsf2);
				std::ostringstream ss;
				ss << vertex->point().cartesian(0);
				auto sss = ss.str();
				std::wcout << sss.c_str() << std::endl;
			}

			CGAL::Nef_polyhedron_3<Kernel_> nef;
			auto c = convert_to_nef(s, nef);
			if (c != 0) {
				std::wcout << "Error " << c << std::endl;
				continue;
			}
			nef = CGAL::minkowski_sum_3(nef, cube);
			std::wcout << "product: " << geom_object->product() << std::endl;
			nefs.push_back({ geom_object->product(), nef });

			Box b(&*(nefs.rbegin()));
			// id_map[b.id()] = ;

			for (auto &vertex : vertices(s)) {
				double p[3] = {
					CGAL::to_double(vertex->point().cartesian(0)),
					CGAL::to_double(vertex->point().cartesian(1)),
					CGAL::to_double(vertex->point().cartesian(2))
				};
				b.extend(p);
			}

			boxes.push_back(enlarge(b));

			/*
			std::ostringstream ss;
			ss << geom_object->product()->data().toString() << std::endl << b.min_coord(0) << " - " << b.max_coord(0) << std::endl;
			auto sss = ss.str();
			std::wcout << sss.c_str();
			*/
		}

		if (!no_progress) {
			if (quiet) {
				const int progress = context_iterator.progress();
				for (; old_progress < progress; ++old_progress) {
					std::cout << ".";
					if (stderr_progress)
						std::cerr << ".";
				}
				std::cout << std::flush;
				if (stderr_progress)
					std::cerr << std::flush;
			} else {
				const int progress = context_iterator.progress() / 2;
				if (old_progress != progress) Logger::ProgressBar(progress);
				old_progress = progress;
			}
		}
	}

	CGAL::box_self_intersection_d(boxes.begin(), boxes.end(), [](const Box& a, const Box& b) {
		std::ostringstream ss;
		// ss << id_map[a.id()]->first->data().toString() << "x" << id_map[b.id()]->first->data().toString() << std::endl;
		// auto x = id_map[a.id()]->second * id_map[b.id()]->second;

		ss << a.handle()->first->data().toString() << "x" << a.handle()->first->data().toString() << std::endl;
		auto x = a.handle()->second * b.handle()->second;
		cgal_shape_t x_poly;
		x.convert_to_polyhedron(x_poly);

		CGAL::Polygon_mesh_processing::triangulate_faces(x_poly);

		auto vs = vertices(x_poly);
		if (std::distance(vs.begin(), vs.end()) == 0) {
			return;
		}

		auto s0 = a.handle()->first->declaration().name();
		auto s1 = b.handle()->first->declaration().name();
		auto i0 = a.handle()->first->data().id();
		auto i1 = b.handle()->first->data().id();

		if (s0 < s1) {
			std::swap(s1, s0);
			std::swap(i0, i1);
		}

		{
			auto FN = s0 + "-" + s1 + "-" + std::to_string(i0) + "-" + std::to_string(i1) + "sb.off";

			std::ofstream os(FN.c_str());
			os.precision(17);
			os << x_poly;
		}

		remove_thickness r(x_poly);

		{
			auto FN = s0 + "-" + s1 + "-" + std::to_string(i0) + "-" + std::to_string(i1) + "-sides-sb.off";

			std::ofstream os(FN.c_str());
			os.precision(17);
			os << r.polyhedron2;
		}

		{
			auto FN = s0 + "-" + s1 + "-" + std::to_string(i0) + "-" + std::to_string(i1) + "-flat-sb.off";

			std::ofstream os(FN.c_str());
			os.precision(17);
			os << r.flattened;
		}
		// r();

		/*
		std::map<cgal_shape_t::Halfedge_const_handle, cgal_shape_t::Point_3> collapsed;
		std::map<cgal_shape_t::Vertex_const_handle, cgal_shape_t::Point_3> collapsed_v;

		for (auto it = x_poly.edges_begin(); it != x_poly.edges_end(); ++it) {
			auto& e = *it;
			cgal_shape_t::Vertex_iterator v0 = e.vertex();
			cgal_shape_t::Vertex_iterator v1 = e.prev()->vertex();
			auto p0 = v0->point();
			auto p1 = v1->point();
			auto l = std::sqrt(CGAL::to_double((p1 - p0).squared_length()));
			std::wcout << "edge w/ length " << l << std::endl;

			cgal_shape_t::Plane_3 plane(it->vertex()->point(),
				it->next()->vertex()->point(),
				it->next()->next()->vertex()->point());

			auto d0 = plane.to_2d(e.prev()->vertex()->point()) - plane.to_2d(e.prev()->prev()->vertex()->point());
			auto d1 = plane.to_2d(e.vertex()->point()) - plane.to_2d(e.prev()->vertex()->point());
			auto d2 = plane.to_2d(e.next()->vertex()->point()) - plane.to_2d(e.vertex()->point());
			auto a0 = std::atan2(CGAL::to_double(d0.cartesian(1)), CGAL::to_double(d0.cartesian(0)));
			auto a1 = std::atan2(CGAL::to_double(d1.cartesian(1)), CGAL::to_double(d1.cartesian(0)));
			auto a2 = std::atan2(CGAL::to_double(d2.cartesian(1)), CGAL::to_double(d2.cartesian(0)));
			auto a10 = a1 - a0;
			auto a21 = a2 - a1;
			if (a10 < 0.) {
				a10 += 2 * M_PI;
			}
			if (a21 < 0.) {
				a21 += 2 * M_PI;
			}

			const bool is_convex = a10 < M_PI && a21 < M_PI;

			cgal_shape_t::Plane_3 opposite_plane(it->opposite()->vertex()->point(),
				it->opposite()->next()->vertex()->point(),
				it->opposite()->next()->next()->vertex()->point()
			);

			{
				std::ostringstream oss;
				oss << plane << " vs " << opposite_plane << "\n";
				oss << plane.orthogonal_vector() << " vs " << opposite_plane.orthogonal_vector();
				auto osss = oss.str();
				std::wcout << osss.c_str() << std::endl;
			}

			bool is_internal = false;
			if (std::sqrt(CGAL::to_double(plane.orthogonal_vector().squared_length())) < 1.e-15 ||
				std::sqrt(CGAL::to_double(opposite_plane.orthogonal_vector().squared_length())) < 1.e-15
				) {
				is_internal = true;
				std::wcout << "Degenerate" << std::endl;
			} else {
				const double face_normal_dot = CGAL::to_double(approx_normalized(plane.orthogonal_vector()) * approx_normalized(opposite_plane.orthogonal_vector()));
				std::wcout << "Face normal dot " << face_normal_dot << std::endl;
				is_internal = face_normal_dot > 0.9;
			}

			std::wcout << "Angles " << a0 << " " << a1 << " " << a2 << std::endl;

			if (l < 4.e-5 && (is_convex || is_internal)) {
				auto p2 = CGAL::ORIGIN + ((p0 - CGAL::ORIGIN) + (p1 - CGAL::ORIGIN)) / 2;

				std::wcout << "(a) " << CGAL::to_double(p0.cartesian(0)) << " " << CGAL::to_double(p0.cartesian(1)) << " " << CGAL::to_double(p0.cartesian(2)) << "\n";
				std::wcout << "(b) " << CGAL::to_double(p1.cartesian(0)) << " " << CGAL::to_double(p1.cartesian(1)) << " " << CGAL::to_double(p1.cartesian(2)) << "\n";
				std::wcout << "(c) " << CGAL::to_double(p2.cartesian(0)) << " " << CGAL::to_double(p2.cartesian(1)) << " " << CGAL::to_double(p2.cartesian(2)) << "\n";
				// collapsed.insert({ v0, p2 });
				// collapsed.insert({ v1, p2 });
				collapsed.insert({ it, p2 });
				// Edges includes only half of the halfedges
				collapsed.insert({ it->opposite(), p2 });

				collapsed_v.insert({ v0, p2 });
				collapsed_v.insert({ v1, p2 });
			}
		}

		{
			auto FN = s0 + "-" + s1 + "-" + std::to_string(i0) + "-" + std::to_string(i1) + "sb.obj";
			std::ofstream ofs(FN.c_str());
			ofs.precision(17);

			int N = 1;

			std::set<std::set<Kernel_::Point_3> > faces_emitted;
			for (auto& f : faces(x_poly)) {
				std::ostringstream oss;
				auto start = f->facet_begin();

				bool part_collapsed = false;

				CGAL::Polyhedron_3<Kernel_>::Halfedge_around_facet_const_circulator e = f->facet_begin();
				do {
					auto it = collapsed.find(e);
					if (it != collapsed.end()) {
						part_collapsed = true;
						break;
					}
					++e;
				} while (e != f->facet_begin());

				decltype(faces_emitted)::key_type vss;
				std::list<cgal_shape_t::Point_3> points;

				if (!part_collapsed) {
					e = f->facet_begin();
					do {
						cgal_shape_t::Vertex_const_handle v = e->vertex();
						auto it = collapsed_v.find(v);
						if (it == collapsed_v.end()) {
							std::wcout << "Unexpected "
								<< CGAL::to_double(v->point().cartesian(0)) << " "
								<< CGAL::to_double(v->point().cartesian(1)) << " "
								<< CGAL::to_double(v->point().cartesian(2)) << std::endl;
						} else {
							points.push_back(it->second);
							vss.insert(it->second);
						}
						++e;
					} while (e != f->facet_begin());

					if (faces_emitted.find(vss) != faces_emitted.end()) {
						std::wcout << "Emitted" << std::endl;
					} else {
						faces_emitted.insert(vss);

						for (auto& p : points) {
							ofs << "v " << CGAL::to_double(p.cartesian(0)) << " " << CGAL::to_double(p.cartesian(1)) << " " << CGAL::to_double(p.cartesian(2)) << "\n";
						}

						ofs << "f ";
						for (auto i = 0; i < points.size(); ++i) {
							if (i) {
								ofs << " ";
							}
							ofs << i + N;
						}
						ofs << "\n";

						N += points.size();
					}
				}
			}
		}

		*/

		/*
		// edge collapse does not work on the rational number types
		typedef CGAL::Simple_cartesian<double> simple;
		CGAL::Polyhedron_3<simple> x_simple;
		poly_copy(x_simple, x_poly);

		// flattening from a thin box to a plane is not valid in edge_collapse()
		Stats stats;
		My_visitor vis(&stats);
		SMS::Edge_length_cost<double> elc;
		SMS::Edge_length_stop_predicate<double> stop(1.e-3);

		int r = SMS::edge_collapse(x_simple, stop,
			CGAL::parameters::vertex_index_map(get(CGAL::vertex_external_index, x_simple))
				.halfedge_index_map(get(CGAL::halfedge_external_index, x_simple))
				.visitor(vis)
				.get_cost(elc)
		);

		std::wcout << "Removed: " << r << std::endl;
		*/

		/*
		for (auto& v : vertices(x_poly)) {
			auto p = v->point();
			for (int i = 0; i < 3; ++i) {
				ss << p.cartesian(i) << " ";
			}
			ss << std::endl;
		}
		ss << "---" << std::endl;
		auto sss = ss.str();
		std::wcout << sss.c_str();
		*/
	});

	if (!no_progress && quiet) {
		for (; old_progress < 100; ++old_progress) {
			std::cout << ".";
			if (stderr_progress)
				std::cerr << ".";
		}
		std::cout << std::flush;
		if (stderr_progress)
			std::cerr << std::flush;
	} else {
		Logger::Status("\rDone fixing space boundaries for " + boost::lexical_cast<std::string>(num_created) +
			" objects                                ");
	}
}
