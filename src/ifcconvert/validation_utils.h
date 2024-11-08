#ifdef IFOPSH_WITH_CGAL

#include "../ifcgeom/kernels/cgal/CgalKernel.h"
#include "../ifcgeom/IfcGeomFilter.h"
#include "../ifcgeom/Iterator.h"

#include <CGAL/box_intersection_d.h>
#include <CGAL/minkowski_sum_3.h>

#include <CGAL/AABB_tree.h>
#include <CGAL/AABB_traits.h>
#include <CGAL/Polyhedron_3.h>
#include <CGAL/AABB_face_graph_triangle_primitive.h>

#include <fstream>
#include <iostream>

template <typename T>
T enlarge(const T& t, double d = 1.e-5) {
	typename T::NT min[3];
	typename T::NT max[3];
	for (int i = 0; i < t.dimension(); ++i) {
		min[i] = t.min_coord(i) - d;
		max[i] = t.max_coord(i) + d;
	}
	return T(min, max, t.handle());
}

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
std::list<cgal_shape_t::Facet_handle> connected_faces(cgal_shape_t::Facet_handle f, const Ts& excluded) {
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

double facet_area(const cgal_shape_t::Facet_handle& f);

void dump_facet(const cgal_shape_t::Facet_handle& f);

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

		std::list<cgal_shape_t::Facet_handle> non_degenerate, degenerate, longitudinal;
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
		}

		std::wcout << "THIN SIDES:" << std::endl;
		for (auto& f : thin_sides) {
			dump_facet(f);
		}

		for (auto& f : non_degenerate) {
			if (thin_sides.find(f) == thin_sides.end()) {
				longitudinal.push_back(f);
			}
		}

		std::wcout << "LONGITUDONAL:" << std::endl;
		for (auto& f : longitudinal) {
			dump_facet(f);
		}

		std::wcout << "faces " << faces(polyhedron).size() << "long " << longitudinal.size() << "thin " << thin_sides.size() << "non-degen " << non_degenerate.size() << std::endl;

		cgal_shape_t enlarged_indiv_triangles;
		Build_Offset<cgal_shape_t::HDS> bo2;
		bo2.input = longitudinal;
		enlarged_indiv_triangles.delegate(bo2);

		{
			std::ofstream ofs("enlarged.off");
			ofs.precision(17);
			ofs << enlarged_indiv_triangles;
		}

		Tree tree2(faces(enlarged_indiv_triangles).begin(), faces(enlarged_indiv_triangles).end(), enlarged_indiv_triangles);

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

		auto thin_sides_degenerate = thin_sides;
		thin_sides_degenerate.insert(degenerate.begin(), degenerate.end());

		// @todo choose connected / connected_opposing based on largest combined area of facets?

		if (longitudinal.size() == 0) {
			std::wcout << "no longitudinal faces detected :(" << std::endl;
			return;
		}

		auto connected = connected_faces(*longitudinal.begin(), thin_sides_degenerate);
		decltype(connected) connected_opposing;

		for (auto& f : longitudinal) {
			if (std::find(connected.begin(), connected.end(), f) == connected.end()) {
				connected_opposing = connected_faces(f, thin_sides_degenerate);

				std::set<cgal_shape_t::Facet_handle> longi(longitudinal.begin(), longitudinal.end());
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


struct intersection_validator {
	typedef std::list<std::pair<const IfcUtil::IfcBaseEntity*, CGAL::Nef_polyhedron_3<Kernel_>> > nefs_t;
	typedef CGAL::Box_intersection_d::Box_with_handle_d<double, 3, nefs_t::value_type*> Box;

	std::vector<Box> boxes;
	nefs_t nefs;

	double total_map_time = 0.;
	double total_geom_time = 0.;
	double total_nef_time = 0.;
	double total_minkowsky_time = 0.;
	double total_box_time = 0.;

	std::set<const IfcUtil::IfcBaseEntity*> successfully_processed;

	intersection_validator(IfcParse::IfcFile& f, std::initializer_list<std::string> entities, double eps, bool no_progress, bool quiet, bool stderr_progress) {

		ifcopenshell::geometry::Settings settings;
		settings.get<ifcopenshell::geometry::settings::UseWorldCoords>().value = false;
		settings.get<ifcopenshell::geometry::settings::WeldVertices>().value = false;
		settings.get<ifcopenshell::geometry::settings::ReorientShells>().value = true;
		settings.get<ifcopenshell::geometry::settings::ConvertBackUnits>().value = true;
		settings.get<ifcopenshell::geometry::settings::IteratorOutput>().value = ifcopenshell::geometry::settings::NATIVE;
		settings.get<ifcopenshell::geometry::settings::DisableOpeningSubtractions>().value = true;

		std::vector<ifcopenshell::geometry::filter_t> spaces_and_walls = {
			IfcGeom::entity_filter(true, false, entities)
		};

		IfcGeom::Iterator context_iterator("cgal", settings, &f, spaces_and_walls, 1);

		if (!context_iterator.initialize()) {
			return;
		}

		auto polycube = ifcopenshell::geometry::utils::create_cube(eps);
		auto cube = ifcopenshell::geometry::utils::create_nef_polyhedron(polycube);

		size_t num_created = 0;
		int old_progress = quiet ? 0 : -1;

		for (;; ++num_created) {
			bool has_more = true;
			if (num_created) {
				has_more = context_iterator.next();
			}
			IfcGeom::BRepElement* geom_object = nullptr;
			if (has_more) {
				geom_object = context_iterator.get_native();
			}
			if (!geom_object) {
				break;
			}

			std::stringstream ss;
			geom_object->product()->toString(ss);
			auto sss = ss.str();
			std::wcout << sss.c_str() << std::endl;

			for (auto& g : geom_object->geometry()) {
				cgal_shape_t s = *std::static_pointer_cast<ifcopenshell::geometry::CgalShape>(g.Shape());
				const auto& m = g.Placement()->ccomponents();
				const auto& n = geom_object->transformation().data()->ccomponents();

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
				}

				std::clock_t nef_begin = std::clock();
				CGAL::Nef_polyhedron_3<Kernel_> nef = ifcopenshell::geometry::utils::create_nef_polyhedron(s);
				std::clock_t nef_end = std::clock();
				total_nef_time += (nef_end - nef_begin) / (double) CLOCKS_PER_SEC;
				if (nef.is_empty()) {
					std::wcout << "Failed to create nef" << std::endl;
					continue;
				}

				successfully_processed.insert(geom_object->product());

				nef = CGAL::minkowski_sum_3(nef, cube);
				std::clock_t minkowski_end = std::clock();
				total_minkowsky_time += (minkowski_end - nef_end) / (double) CLOCKS_PER_SEC;

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

		/*
		// @todo
		total_geom_time = context_iterator.converter().total_geom_time;
		total_map_time = context_iterator.converter().total_map_time;
		*/
	}

	template <typename Fn>
	void operator()(Fn fn) {
		std::clock_t box_overlap_begin = std::clock();
		CGAL::box_self_intersection_d(boxes.begin(), boxes.end(), [](Box& x, Box& y) {});
		std::clock_t box_overlap_end = std::clock();
		total_box_time += (box_overlap_end - box_overlap_begin) / (double) CLOCKS_PER_SEC;
		CGAL::box_self_intersection_d(boxes.begin(), boxes.end(), fn);
	}
};

#endif