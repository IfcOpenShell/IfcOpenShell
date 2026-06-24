#include "CgalConversionResult.h"
#include "CgalKernel.h"

#include <CGAL/Polygon_mesh_processing/repair.h>
#include <CGAL/Polygon_mesh_processing/self_intersections.h>
#include <CGAL/Polygon_mesh_processing/polygon_soup_to_polygon_mesh.h>
#include <CGAL/Polygon_mesh_processing/polygon_mesh_to_polygon_soup.h>

#include "../../../ifcparse/IfcLogger.h"
#include "../../../ifcgeom/IfcGeomRepresentation.h"

using IfcGeom::OpaqueNumber;
using IfcGeom::OpaqueCoordinate;
using IfcGeom::ConversionResultShape;

#ifdef IFOPSH_SIMPLE_KERNEL
#define NumberType OpaqueNumber
#else
using ifcopenshell::geometry::NumberEpeck;
#define NumberType NumberEpeck
#endif

#ifdef IFOPSH_SIMPLE_KERNEL
#define CgalShape SimpleCgalShape
#endif

typedef CGAL::Polyhedron_3<Kernel_> Polyhedron;
typedef Polyhedron::Facet_const_handle Facet_const_handle;
typedef Polyhedron::Halfedge_around_facet_const_circulator Halfedge_around_facet_circulator;

namespace {
	cgal_placement_t make_transform(const ifcopenshell::geometry::taxonomy::matrix4& place) {
		const auto& m = place.ccomponents();
		return cgal_placement_t(
			m(0, 0), m(0, 1), m(0, 2), m(0, 3),
			m(1, 0), m(1, 1), m(1, 2), m(1, 3),
			m(2, 0), m(2, 1), m(2, 2), m(2, 3));
	}

	OpaqueCoordinate<3> opaque_point(const cgal_point_t& p) {
		return OpaqueCoordinate<3>(
			NumberType(p.cartesian(0)),
			NumberType(p.cartesian(1)),
			NumberType(p.cartesian(2))
		);
	}

	typename Kernel_::FT max_abs3(const typename Kernel_::FT& a, const typename Kernel_::FT& b, const typename Kernel_::FT& c) {
		std::array<typename Kernel_::FT, 3> abc{ a, b, c };
		auto minel = std::min_element(abc.begin(), abc.end());
		auto maxel = std::max_element(abc.begin(), abc.end());
		return ((-*minel) > *maxel) ? (-*minel) : *maxel;
	}

	OpaqueCoordinate<3> opaque_axis(const cgal_vector_t& v) {
		auto maxval = max_abs3(v.x(), v.y(), v.z());
		if (maxval == 0) {
			throw std::runtime_error("Invalid shape type");
		}
		return OpaqueCoordinate<3>(
			NumberType(v.x() / maxval),
			NumberType(v.y() / maxval),
			NumberType(v.z() / maxval)
		);
	}

	OpaqueCoordinate<4> opaque_plane(const cgal_plane_t& p) {
		auto maxval = max_abs3(p.a(), p.b(), p.c());
		if (maxval == 0) {
			throw std::runtime_error("Invalid shape type");
		}
		return OpaqueCoordinate<4>(
			NumberType(p.a() / maxval),
			NumberType(p.b() / maxval),
			NumberType(p.c() / maxval),
			NumberType(p.d() / maxval)
		);
	}

	cgal_plane_t plane_from_opaque(const OpaqueCoordinate<4>& p) {
#ifdef IFOPSH_SIMPLE_KERNEL
		return cgal_plane_t(
			p.get(0).to_double(),
			p.get(1).to_double(),
			p.get(2).to_double(),
			p.get(3).to_double()
		);
#else
		return cgal_plane_t(
			p.get(0).value_as<CGAL::Epeck::FT>(),
			p.get(1).value_as<CGAL::Epeck::FT>(),
			p.get(2).value_as<CGAL::Epeck::FT>(),
			p.get(3).value_as<CGAL::Epeck::FT>()
		);
#endif
	}

	void insert_normalized_plane_map(plane_map<Kernel_>& mp, const OpaqueCoordinate<4>& from, const OpaqueCoordinate<4>& to) {
		mp.insert({
			normalized_plane_for_map<Kernel_>(plane_from_opaque(from)),
			normalized_plane_for_map<Kernel_>(plane_from_opaque(to))
		});
	}

	void apply_normalized_plane_map(const plane_map<Kernel_>& mp, std::list<cgal_plane_t>& planes) {
		for (auto& plane : planes) {
			auto it = mp.find(normalized_plane_for_map<Kernel_>(plane));
			if (it != mp.end()) {
				plane = it->second;
			}
		}
	}

	cgal_vector_t wire_normal(const cgal_wire_t& wire) {
		typename Kernel_::FT a(0), b(0), c(0);
		if (wire.size() < 3) {
			return cgal_vector_t(a, b, c);
		}
		for (std::size_t i = 0; i < wire.size(); ++i) {
			const auto& curr = wire[i];
			const auto& next = wire[(i + 1) % wire.size()];
			a += (curr.y() - next.y()) * (curr.z() + next.z());
			b += (curr.z() - next.z()) * (curr.x() + next.x());
			c += (curr.x() - next.x()) * (curr.y() + next.y());
		}
		return cgal_vector_t(a, b, c);
	}

	cgal_point_t wire_centroid(const cgal_wire_t& wire) {
		if (wire.empty()) {
			throw std::runtime_error("Invalid shape type");
		}
		std::array<Kernel_::FT, 3> p{ Kernel_::FT(0), Kernel_::FT(0), Kernel_::FT(0) };
		for (const auto& point : wire) {
			for (int i = 0; i < 3; ++i) {
				p[i] += point.cartesian(i);
			}
		}
		Kernel_::FT n(wire.size());
		return cgal_point_t(p[0] / n, p[1] / n, p[2] / n);
	}

	Kernel_::FT wire_length(const cgal_wire_t& wire) {
		Kernel_::FT len(0);
		if (wire.size() < 2) {
			return len;
		}
		for (std::size_t i = 1; i < wire.size(); ++i) {
			len += CGAL::approximate_sqrt(CGAL::Segment_3<Kernel_>(wire[i - 1], wire[i]).squared_length());
		}
		if (wire.size() > 2) {
			len += CGAL::approximate_sqrt(CGAL::Segment_3<Kernel_>(wire.back(), wire.front()).squared_length());
		}
		return len;
	}

	Kernel_::FT wire_area(const cgal_wire_t& wire) {
		Kernel_::FT area(0);
		if (wire.size() < 3) {
			return area;
		}
		const auto& origin = wire.front();
		for (std::size_t i = 1; i + 1 < wire.size(); ++i) {
			auto v1 = wire[i] - origin;
			auto v2 = wire[i + 1] - origin;
			area += CGAL::approximate_sqrt(CGAL::cross_product(v1, v2).squared_length()) / Kernel_::FT(2);
		}
		return area;
	}

	cgal_wire_t moved_wire(const cgal_wire_t& wire, const cgal_placement_t& trsf) {
		cgal_wire_t result;
		result.reserve(wire.size());
		for (const auto& point : wire) {
			result.push_back(point.transform(trsf));
		}
		return result;
	}

	void write_off_point(std::stringstream& sstream, const cgal_point_t& point) {
		sstream << "OFF\n1 0 0\n";
		sstream << point.x() << " " << point.y() << " " << point.z() << "\n";
	}

	void write_off_wire(std::stringstream& sstream, const cgal_wire_t& wire) {
		const bool face = wire.size() >= 3;
		sstream << "OFF\n" << wire.size() << " " << (face ? 1 : 0) << " 0\n";
		for (const auto& point : wire) {
			sstream << point.x() << " " << point.y() << " " << point.z() << "\n";
		}
		if (face) {
			sstream << wire.size();
			for (std::size_t i = 0; i < wire.size(); ++i) {
				sstream << " " << i;
			}
			sstream << "\n";
		}
	}

	template <typename Facet>
	CGAL::Direction_3<Kernel_> newell(Facet& face) {
		typename Kernel_::FT a(0), b(0), c(0);
		CGAL::Polyhedron_3<Kernel_>::Halfedge_around_facet_const_circulator current_halfedge = face.facet_begin();
		do {
			auto& curr = current_halfedge->vertex()->point();
			auto& next = current_halfedge->next()->vertex()->point();
			a += (curr.y() - next.y()) * (curr.z() + next.z());
			b += (curr.z() - next.z()) * (curr.x() + next.x());
			c += (curr.x() - next.x()) * (curr.y() + next.y());
		} while (++current_halfedge != face.facet_begin());
		return CGAL::Direction_3<Kernel_>(a, b, c);
	}

	struct Plane_equation {
		template <typename Facet>
		typename Facet::Plane_3 operator()(Facet& face) {
			typename Facet::Halfedge_handle h = face.halfedge();
			return typename Facet::Plane_3(h->vertex()->point(), newell(face));
		}
	};

	bool are_facets_coplanar(const Facet_const_handle& f1, const Facet_const_handle& f2) {
		auto normal_1 = CGAL::normal(f1->halfedge()->vertex()->point(),
			f1->halfedge()->next()->vertex()->point(),
			f1->halfedge()->next()->next()->vertex()->point());

		auto normal_2 = CGAL::normal(f2->halfedge()->vertex()->point(),
			f2->halfedge()->next()->vertex()->point(),
			f2->halfedge()->next()->next()->vertex()->point());

		return CGAL::collinear(CGAL::ORIGIN + decltype(normal_1)(0., 0., 0.), CGAL::ORIGIN + normal_1, CGAL::ORIGIN + normal_2);
	}

	void partition_coplanar_components(const Polyhedron& shape,
		std::vector<std::set<Facet_const_handle>>& components) {
		std::set<Facet_const_handle> visited;

		for (auto& face : shape.facet_handles()) {
			if (visited.find(face) != visited.end()) {
				continue;
			}

			components.emplace_back();
			auto& component = components.back();
			std::queue<Facet_const_handle> queue;

			queue.push(face);
			visited.insert(face);

			while (!queue.empty()) {
				Facet_const_handle current = queue.front();
				queue.pop();

				component.insert(current);

				Halfedge_around_facet_circulator he = current->facet_begin();
				do {
					Facet_const_handle neighbour = he->opposite()->face();
					if (visited.find(neighbour) == visited.end() && neighbour != nullptr && visited.find(neighbour) == visited.end() && are_facets_coplanar(current, neighbour)) {
						queue.push(neighbour);
						visited.insert(neighbour);
					}
				} while (++he != current->facet_begin());
			}
		}
	}
}

ifcopenshell::geometry::CgalShape::CgalShape(const cgal_shape_t& shape, bool convex, Logger& logger) {
	shape_ = shape;
	convex_tag_ = convex;
	auto& poly = std::get<cgal_shape_t>(*shape_);

	std::set<cgal_shape_t::Facet_handle> faces_to_remove;

	for (const auto& face : CGAL::faces(poly)) {
		auto V = newell(*face).to_vector();
		CGAL::Plane_3<Kernel_> plane(CGAL::Point_3<Kernel_>(), V);
		auto b1 = plane.base1();
		auto b2 = plane.base2();

		if (V.squared_length() == 0) {
			logger.Warning("GEO", 62, "Removed face due to self-intersections");
			faces_to_remove.insert(face);
			continue;
		}
		auto C = face->halfedge()->vertex()->point();
		auto transform_point = [&V, &C, &b1, &b2](const auto& p) {
			auto dv = p - C;
			return CGAL::Point_2<Kernel_>(
				dv * b1,
				dv * b2
			);
		};

		std::vector<CGAL::Point_2<Kernel_>> ps;
			
		for (auto& he1 : CGAL::halfedges_around_face(face->halfedge(), poly)) {
			const auto& source = he1->vertex()->point();
			ps.push_back(transform_point(source));
		}

		if (!CGAL::Polygon_2<Kernel_>(ps.begin(), ps.end()).is_simple()) {
			logger.Warning("GEO", 63, "Removed face due to self-intersections");
			faces_to_remove.insert(face);
		}
	}

	{
		for (auto& face : faces_to_remove) {
			CGAL::Euler::remove_face(face->halfedge(), poly);
		}
	}
}

ifcopenshell::geometry::CgalShape::CgalShape(const cgal_point_t& point, bool convex) {
	shape_ = point;
	convex_tag_ = convex;
}

ifcopenshell::geometry::CgalShape::CgalShape(const cgal_wire_t& wire, bool convex) {
	shape_ = wire;
	convex_tag_ = convex;
}

const cgal_shape_t& ifcopenshell::geometry::CgalShape::poly() const {
#ifndef IFOPSH_SIMPLE_KERNEL
	to_poly();
#endif
	if (!shape_ || !std::holds_alternative<cgal_shape_t>(*shape_)) {
		throw std::runtime_error("Invalid shape type");
	}
	return std::get<cgal_shape_t>(*shape_);
}

#ifndef IFOPSH_SIMPLE_KERNEL
void ifcopenshell::geometry::CgalShape::to_poly() const {
	if (!shape_) {
		cgal_shape_t poly;
		convert_to_polyhedron(*nef_, poly, std::numeric_limits<std::size_t>::max());
		if (poly.size_of_vertices() > 0) {
			// @todo why is this necessary? we have the mark of the volumes?
			CGAL::Polygon_mesh_processing::orient_to_bound_a_volume(poly);
		}
		shape_ = poly;
		
		// nef_->convert_to_polyhedron(*shape_);
	}
}

void ifcopenshell::geometry::CgalShape::to_nef() const {
	if (!nef_) {
		auto shp = poly();
		if (!convex_tag_) {
			CGAL::Polygon_mesh_processing::triangulate_faces(shp);
			if (CGAL::Polygon_mesh_processing::does_self_intersect(shp)) {
				throw std::runtime_error("Self-intersections detected, unable to proceed");
			}
		}
		nef_ = utils::create_nef_polyhedron(shp);
	}
}
#endif

void ifcopenshell::geometry::CgalShape::Triangulate(ifcopenshell::geometry::Settings settings, const ifcopenshell::geometry::taxonomy::matrix4& place, IfcGeom::Representation::Triangulation* t, int item_id, int surface_style_id, Logger& logger) const {
	if (is_point() || is_wire()) {
		return;
	}
	const auto& base_shape = poly();
	const bool all_triangles = std::all_of(base_shape.facets_begin(), base_shape.facets_end(), [](auto f) { return f.is_triangle(); });
	const bool has_iden_transform = place.is_identity();

	std::unique_ptr<cgal_shape_t> shape_copy_holder;
	cgal_shape_t* shape_to_use;

	if (!all_triangles || !has_iden_transform) {
		// A copy is made when triangulate_faces() is required or when vertex positions need be transformed
		shape_copy_holder.reset(new cgal_shape_t(base_shape));
		shape_to_use = shape_copy_holder.get();
	} else {
		shape_to_use = const_cast<cgal_shape_t*>(&base_shape);
	}

	const bool setting_use_original_edges = settings.get<ifcopenshell::geometry::settings::CgalEmitOriginalEdges>().get();
	
	std::set<std::set<Kernel_::Point_3>> original_edges;
	if (setting_use_original_edges) {
		for (auto it = shape_to_use->edges_begin(); it != shape_to_use->edges_end(); ++it) {
			original_edges.insert({ it->vertex()->point(), it->prev()->vertex()->point() });
		}
	}

	if (!has_iden_transform) {
		const auto& m = place.ccomponents();

		// @todo check
		const cgal_placement_t trsf(
			m(0, 0), m(0, 1), m(0, 2), m(0, 3),
			m(1, 0), m(1, 1), m(1, 2), m(1, 3),
			m(2, 0), m(2, 1), m(2, 2), m(2, 3));

		// Apply transformation
		for (auto &vertex : shape_to_use->vertex_handles()) {
			vertex->point() = vertex->point().transform(trsf);
		}
	}

	boost::optional<double> smooth_treshold;
	{
		auto setting_value = settings.get<ifcopenshell::geometry::settings::CgalSmoothAngleDegrees>().get();
		if (setting_value > 0.) {
			smooth_treshold = std::cos(setting_value * boost::math::constants::pi<double>() / 180.0);
		}
	}

	if (!all_triangles) {
		if (!shape_to_use->is_valid()) {
			logger.Message(Logger::LOG_ERROR, "GEO", 64, "Invalid Polyhedron_3 in object (before triangulation)");
			return;
		}

		bool success = false;
		try {
			success = CGAL::Polygon_mesh_processing::triangulate_faces(*shape_to_use);
		} catch (...) {
			logger.Message(Logger::LOG_ERROR, "GEO", 65, "Triangulation crashed");
			return;
		}

		CGAL::Polygon_mesh_processing::remove_degenerate_faces(*shape_to_use);

		if (!success) {
			logger.Message(Logger::LOG_ERROR, "GEO", 66, "Triangulation failed");
			return;
		}

		if (!shape_to_use->is_valid()) {
			logger.Message(Logger::LOG_ERROR, "GEO", 67, "Invalid Polyhedron_3 in object (after triangulation)");
			return;
		}
	}

	// Facet -> planar component map for determining which
	// edges are to be registered.
	std::vector<std::set<Facet_const_handle>> components;
	std::map<Facet_const_handle, typename decltype(components)::const_iterator> facet_to_component;
	if (!setting_use_original_edges) {
		partition_coplanar_components(*shape_to_use, components);
		for (auto it = components.begin(); it != components.end(); ++it) {
			for (auto& f : *it) {
				facet_to_component[f] = it;
			}
		}
	}

	// std::map<cgal_vertex_descriptor_t, Kernel_::Vector_3> vertex_normals;
	// boost::associative_property_map<std::map<cgal_vertex_descriptor_t, Kernel_::Vector_3>> vertex_normals_map(vertex_normals);
	
	// Triangulate the shape and compute the normals
	std::map<Facet_const_handle, Kernel_::Vector_3> face_normals;
	boost::associative_property_map<std::map<Facet_const_handle, Kernel_::Vector_3>> face_normals_map(face_normals);

	//  CGAL::Polygon_mesh_processing::compute_normals(s, vertex_normals_map, face_normals_map);
	try {
		CGAL::Polygon_mesh_processing::compute_face_normals(*shape_to_use, face_normals_map);
	} catch (...) {
		logger.Message(Logger::LOG_ERROR, "GEO", 68, "Face normal calculation failed");
		return;
	}

	// We do welding here in addition to in the triangulation item, because
	// CGAL does not have a concept of vertices with identity like OCCT has.
	typedef std::tuple<Kernel_::FT, Kernel_::FT, Kernel_::FT, Kernel_::FT, Kernel_::FT, Kernel_::FT> postion_normal;
	std::map<postion_normal, size_t> welds;

	std::set<std::pair<int, int>> registered_edges;

	int num_faces = 0, num_vertices = 0;
	for (auto &face : faces(*shape_to_use)) {
		if (!face->is_triangle()) {
			std::cout << "Warning: non-triangular face!" << std::endl;
			continue;
		}
		CGAL::Polyhedron_3<Kernel_>::Halfedge_around_facet_const_circulator current_halfedge = face->facet_begin();

		const Kernel_::Vector_3 facet_normal = face_normals_map[face];

		int vertexidx[3];
		bool is_face_boundary[3];
		int i = 0;
		do {
			auto v = current_halfedge->vertex();

			auto vertex_norm = facet_normal;

			if (smooth_treshold) {
				Kernel_::Vector_3 normal_accum(0, 0, 0);
				{
					// circulator around the vertex
					auto vh_begin = v->vertex_begin();
					if (vh_begin != nullptr) {
						auto vh = vh_begin;
						do {
							if (!vh->is_border()) {
								Facet_const_handle adj_f = vh->facet();
								const auto fn2 = face_normals_map[adj_f];
								if ((fn2 * facet_normal) >= *smooth_treshold) {
									normal_accum = normal_accum + fn2;
								}
								++vh;
							}
						} while (vh != vh_begin);
					}
				}
				const double len = std::sqrt(CGAL::to_double(normal_accum.squared_length()));
				if (len > 0) {
					vertex_norm = normal_accum / len;
				}
			}

			postion_normal pn = {
				v->point().cartesian(0),
				v->point().cartesian(1),
				v->point().cartesian(2),
				vertex_norm.cartesian(0),
				vertex_norm.cartesian(1),
				vertex_norm.cartesian(2)
			};

			// @todo normalzie based on largest component?

			size_t vidx;
			auto it = welds.find(pn);
			if (it == welds.end()) {
				vidx = t->addVertex(
					item_id,
					surface_style_id,
					CGAL::to_double(current_halfedge->vertex()->point().cartesian(0)),
					CGAL::to_double(current_halfedge->vertex()->point().cartesian(1)),
					CGAL::to_double(current_halfedge->vertex()->point().cartesian(2))
				);
				welds.insert({ pn, vidx });

				auto nx = CGAL::to_double(face_normals_map[face].cartesian(0));
				auto ny = CGAL::to_double(face_normals_map[face].cartesian(1));
				auto nz = CGAL::to_double(face_normals_map[face].cartesian(2));

				t->addNormal(nx, ny, nz);
			} else {
				vidx = it->second;
			}

			vertexidx[i] = (int)vidx;
			is_face_boundary[i] = setting_use_original_edges
				? original_edges.find({ current_halfedge->vertex()->point(), current_halfedge->prev()->vertex()->point() }) != original_edges.end()
				: facet_to_component[face] != facet_to_component[current_halfedge->opposite()->face()];
				
			++i;
			++num_vertices;
			++current_halfedge;
		} while (current_halfedge != face->facet_begin());

		t->addFace(item_id, surface_style_id, vertexidx[0], vertexidx[1], vertexidx[2]);
		for (size_t i = 0; i < 3; ++i) {
			if (is_face_boundary[i]) {
				// In CGAL, the vertex of a halfedge is the incident vertex, i.e
				// the second vertex of the edge, so in order to get corresponding
				// vertex and edge indices we need to find vertexids (i-1, i) for
				// the boundary registered in i.
				auto a = vertexidx[(i + 2) % 3];
				auto b = vertexidx[(i + 3) % 3];
				if (a > b) {
					std::swap(a, b);
				}
				if (registered_edges.find({ a, b }) == registered_edges.end()) {
					registered_edges.insert({ a,b });
					t->registerEdge(item_id, a, b);
				}
			}
		}

		++num_faces;
	}

}

void ifcopenshell::geometry::CgalShape::Serialize(const ifcopenshell::geometry::taxonomy::matrix4& place, std::string& r) const {
	std::stringstream sstream;
	if (is_point()) {
		auto p = point();
		if (!place.is_identity()) {
			p = p.transform(make_transform(place));
		}
		write_off_point(sstream, p);
	} else if (is_wire()) {
		auto w = wire();
		if (!place.is_identity()) {
			w = moved_wire(w, make_transform(place));
		}
		write_off_wire(sstream, w);
	} else {
		cgal_shape_t s = poly();

		if (!place.is_identity()) {
			const auto trsf = make_transform(place);

			// Apply transformation
			for (auto &vertex : s.vertex_handles()) {
				vertex->point() = vertex->point().transform(trsf);
			}
		}

		sstream << s;
	}
	r = sstream.str();
}

#include <CGAL/Polygon_mesh_processing/bbox.h>

double ifcopenshell::geometry::CgalShape::bounding_box(void *& b) const {
	if (b == nullptr) {
		b = new CGAL::Bbox_3;
	}
	auto& bb = (*((CGAL::Bbox_3*)b));
	if (is_point()) {
		bb += point().bbox();
	} else if (is_wire()) {
		for (const auto& point : wire()) {
			bb += point.bbox();
		}
	} else {
		bb += CGAL::Polygon_mesh_processing::bbox(poly());
	}
	return (bb.xmax() - bb.xmin()) * (bb.ymax() - bb.ymin()) * (bb.zmax() - bb.zmin());
}

int ifcopenshell::geometry::CgalShape::num_vertices() const {
	if (is_point()) {
		return 1;
	}
	if (is_wire()) {
		return (int) wire().size();
	}
	return (int) poly().size_of_vertices();
}

void ifcopenshell::geometry::CgalShape::set_box(void * b) {
	auto& bb = (*((CGAL::Bbox_3*)b));
	Kernel_::Point_3 lower(bb.xmin(), bb.ymin(), bb.zmin());
	Kernel_::Point_3 upper(bb.xmax(), bb.ymax(), bb.zmax());
	shape_ = ifcopenshell::geometry::utils::create_cube(lower, upper);
}

int ifcopenshell::geometry::CgalShape::surface_genus() const {
	if (is_point() || is_wire()) {
		return 0;
	}
	const auto& shp = poly();
	auto nv = shp.size_of_vertices();
	auto ne = shp.size_of_halfedges() / 2;
	auto nf = shp.size_of_facets();

	auto euler = nv - ne + nf;
	auto genus = (2 - euler) / 2;

	return (int) genus;
}

bool ifcopenshell::geometry::CgalShape::is_manifold() const {
	// @todo ?
	return (is_point() || is_wire()) ? true : poly().is_valid();
}

int ifcopenshell::geometry::CgalShape::num_edges() const
{
	if (is_point()) {
		return 0;
	}
	if (is_wire()) {
		const auto n = wire().size();
		if (n < 2) {
			return 0;
		}
		return (int)(n == 2 ? 1 : n);
	}
	return (int) poly().size_of_halfedges() / 2;
}

int ifcopenshell::geometry::CgalShape::num_faces() const
{
#ifndef IFOPSH_SIMPLE_KERNEL
	if (nef_) {
		return (int) nef_->number_of_facets();
	} else
#endif
	if (shape_) {
		if (is_poly()) {
			return (int) poly().size_of_facets();
		}
		if (is_wire() && wire().size() >= 3) {
			return 1;
		}
		return 0;
	} else {
		return 0;
	}
}

OpaqueNumber ifcopenshell::geometry::CgalShape::CgalShape::length()
{
	Kernel_::FT len = 0;
	if (is_wire()) {
		len = wire_length(wire());
	} else if (!is_point()) {
		const auto& shp = poly();
		for (auto it = shp.edges_begin(); it != shp.edges_end(); ++it) {
			len += CGAL::approximate_sqrt(CGAL::Segment_3<Kernel_>(
				it->vertex()->point(),
				it->opposite()->vertex()->point()
			).squared_length());
		}
	}
	return NumberType(len);
}

OpaqueNumber ifcopenshell::geometry::CgalShape::area()
{
	if (is_wire()) {
		return NumberType(wire_area(wire()));
	}
	if (is_point()) {
		return NumberType(Kernel_::FT(0));
	}
	auto s = poly();
	CGAL::Polygon_mesh_processing::triangulate_faces(s);
	return NumberType(CGAL::Polygon_mesh_processing::area(s));
}

OpaqueNumber ifcopenshell::geometry::CgalShape::volume()
{
	if (is_point() || is_wire()) {
		return NumberType(Kernel_::FT(0));
	}
	auto s = poly();
	CGAL::Polygon_mesh_processing::triangulate_faces(s);
	return NumberType(CGAL::Polygon_mesh_processing::volume(s));
}

OpaqueCoordinate<3> ifcopenshell::geometry::CgalShape::position()
{
	if (is_point()) {
		return opaque_point(point());
	}
	if (is_wire()) {
		return opaque_point(wire_centroid(wire()));
	}
	const auto& shp = poly();
	if (shp.size_of_facets() == 1) {
		// return centroid;
		// CGAL::Vector_3<Kernel_> p;
		std::array<Kernel_::FT, 3> p{ Kernel_::FT(0), Kernel_::FT(0), Kernel_::FT(0) };
		for (auto it = shp.points_begin(); it != shp.points_end(); ++it) {
			for (int i = 0; i < 3; ++i) {
				p[i] += it->cartesian(i);
			}			
		}
		Kernel_::FT N(std::distance(shp.points_begin(), shp.points_end()));
		for (int i = 0; i < 3; ++i) {
			p[i] /= N;
		}
		return OpaqueCoordinate<3>(
			NumberType(p[0]),
			NumberType(p[1]),
			NumberType(p[2])
		);
	} else {
		throw std::runtime_error("Invalid shape type");
	}
}

OpaqueCoordinate<3> ifcopenshell::geometry::CgalShape::axis()
{
	if (is_wire()) {
		if (wire().size() == 2) {
			return opaque_axis(wire()[1] - wire()[0]);
		}
		if (wire().size() >= 3) {
			return opaque_axis(wire_normal(wire()));
		}
		throw std::runtime_error("Invalid shape type");
	}
	auto shp = poly();
	if (shp.size_of_facets() == 1) {
		auto pl = Plane_equation()(*shp.facets_begin());
		return opaque_axis(cgal_vector_t(pl.a(), pl.b(), pl.c()));
	} else {
		throw std::runtime_error("Invalid shape type");
	}
}

OpaqueCoordinate<4> ifcopenshell::geometry::CgalShape::plane_equation()
{
	if (is_wire() && wire().size() >= 3) {
		auto normal = wire_normal(wire());
		return opaque_plane(cgal_plane_t(wire().front(), CGAL::Direction_3<Kernel_>(normal)));
	}
	auto shp = poly();
	if (shp.size_of_facets() == 1) {
		return opaque_plane(Plane_equation()(*shp.facets_begin()));
	}
	throw std::runtime_error("Invalid shape type");
}

std::vector<ConversionResultShape*> ifcopenshell::geometry::CgalShape::convex_decomposition()
{
#ifdef IFOPSH_SIMPLE_KERNEL
	throw std::runtime_error("Not implemented");
#else
	std::vector<ConversionResultShape*> result;
	auto copy = nef();
	CGAL::convex_decomposition_3(copy);
	// the first volume is the outer volume, which is
	// ignored in the decomposition
	auto ci = ++copy.volumes_begin();
	int NN = 0;

	for (; ci != copy.volumes_end(); ++ci, ++NN) {
		if (ci->mark()) {
			// @todo couldn't get it to work with the multiple volumes of a complex decomposition
			// directly, so for now we need to isolate the individual volumes.
			CGAL::Polyhedron_3<Kernel_> P;
			copy.convert_inner_shell_to_polyhedron(ci->shells_begin(), P);
			result.push_back(new CgalShape(P, /*convex=*/ true));
		}
	}
	return result;
#endif
}

ConversionResultShape* ifcopenshell::geometry::CgalShape::halfspaces()
{
#ifdef IFOPSH_SIMPLE_KERNEL
	throw std::runtime_error("Not implemented");
#else
	return new CgalShapeHalfSpaceDecomposition(nef(), convex_tag_);
#endif
}

ConversionResultShape* ifcopenshell::geometry::CgalShape::solid()
{
	throw std::runtime_error("Not implemented");
}

ConversionResultShape * ifcopenshell::geometry::CgalShape::box()
{
	throw std::runtime_error("Not implemented");
}

ConversionResultShape* ifcopenshell::geometry::CgalShape::wrap_in_compound()
{
	return clone();
}

std::vector<ConversionResultShape*> ifcopenshell::geometry::CgalShape::vertices()
{
	std::vector<ConversionResultShape*> result;
	if (is_point()) {
		result.push_back(new CgalShape(point()));
		return result;
	}
	if (is_wire()) {
		for (const auto& p : wire()) {
			result.push_back(new CgalShape(p));
		}
		return result;
	}
	for (const auto& p : poly().points()) {
		result.push_back(new CgalShape(p));
	}
	return result;
}

std::vector<ConversionResultShape*> ifcopenshell::geometry::CgalShape::edges()
{
	std::vector<ConversionResultShape*> result;
	if (is_point()) {
		return result;
	}
	if (is_wire()) {
		const auto& w = wire();
		for (std::size_t i = 1; i < w.size(); ++i) {
			result.push_back(new CgalShape(cgal_wire_t{ w[i - 1], w[i] }));
		}
		if (w.size() > 2) {
			result.push_back(new CgalShape(cgal_wire_t{ w.back(), w.front() }));
		}
		return result;
	}
	for (auto ed : poly().edges()) {
		result.push_back(new CgalShape(cgal_wire_t{ ed.vertex()->point(), ed.opposite()->vertex()->point() }));
	}
	return result;
}

std::vector<ConversionResultShape*> ifcopenshell::geometry::CgalShape::facets()
{
	std::vector<ConversionResultShape*> result;
	if (is_point()) {
		return result;
	}
	if (is_wire()) {
		if (wire().size() >= 3) {
			result.push_back(new CgalShape(wire()));
		}
		return result;
	}
	for (auto face : faces(poly())) {
		std::vector<cgal_point_t> ps;

		auto it = face->facet_begin();
		do {
			ps.push_back(it->vertex()->point());
		} while (++it != face->facet_begin());

		result.push_back(new CgalShape(ps));
	}
	return result;
}

ConversionResultShape* ifcopenshell::geometry::CgalShape::add(ConversionResultShape* other)
{
#ifdef IFOPSH_SIMPLE_KERNEL
	throw std::runtime_error("Not implemented");
#else
	return new CgalShape(this->nef() + ((CgalShape*)other)->nef());
#endif
}

ConversionResultShape* ifcopenshell::geometry::CgalShape::subtract(ConversionResultShape* other)
{
#ifdef IFOPSH_SIMPLE_KERNEL
	throw std::runtime_error("Not implemented");
#else
	return new CgalShape(this->nef() - ((CgalShape*)other)->nef());
#endif
}

ConversionResultShape* ifcopenshell::geometry::CgalShape::intersect(ConversionResultShape* other)
{
#ifdef IFOPSH_SIMPLE_KERNEL
	throw std::runtime_error("Not implemented");
#else
	return new CgalShape(this->nef() * ((CgalShape*)other)->nef());
#endif
}

namespace {
	template <typename Polyhedron>
	void concatenate_polyhedra(Polyhedron& p1, const Polyhedron& p2) {
		std::vector<cgal_point_t> points1, points2;
		std::vector<std::vector<std::size_t>> faces1, faces2;

		// Extract soups
		CGAL::Polygon_mesh_processing::polygon_mesh_to_polygon_soup(p1, points1, faces1);
		CGAL::Polygon_mesh_processing::polygon_mesh_to_polygon_soup(p2, points2, faces2);

		// Offset indices in faces2 by current number of points in points1
		std::size_t offset = points1.size();
		for (auto& f : faces2) {
			for (auto& idx : f) {
				idx += offset;
			}
		}

		// Merge soups
		points1.insert(points1.end(), points2.begin(), points2.end());
		faces1.insert(faces1.end(), faces2.begin(), faces2.end());

		// Build merged polyhedron
		Polyhedron merged;
		CGAL::Polygon_mesh_processing::polygon_soup_to_polygon_mesh(points1, faces1, merged);

		p1 = std::move(merged);
	}
}

ConversionResultShape* ifcopenshell::geometry::CgalShape::concat(ConversionResultShape* other)
{
	auto shp = poly();
	concatenate_polyhedra(shp, ((CgalShape*)other)->poly());
	return new CgalShape(shp);
}

std::pair<OpaqueCoordinate<3>, OpaqueCoordinate<3>> ifcopenshell::geometry::CgalShape::bounding_box() const
{
	throw std::runtime_error("Not implemented");
}

ConversionResultShape* ifcopenshell::geometry::CgalShape::moved(ifcopenshell::geometry::taxonomy::matrix4::ptr place) const
{
	if (place->is_identity()) {
		return clone();
	}

	const auto trsf = make_transform(*place);
	if (is_point()) {
		return new CgalShape(point().transform(trsf), convex_tag_);
	}
	if (is_wire()) {
		return new CgalShape(moved_wire(wire(), trsf), convex_tag_);
	}

	cgal_shape_t s = poly();
	for (auto &vertex : s.vertex_handles()) {
		vertex->point() = vertex->point().transform(trsf);
	}

	return new CgalShape(s, convex_tag_);
}

std::size_t ifcopenshell::geometry::CgalShape::map(OpaqueCoordinate<4>&, OpaqueCoordinate<4>&) {
	throw std::runtime_error("Not implemented");
}

std::size_t ifcopenshell::geometry::CgalShape::map(const std::vector<OpaqueCoordinate<4>>&, const std::vector<OpaqueCoordinate<4>>&) {
	throw std::runtime_error("Not implemented");
}

bool ifcopenshell::geometry::CgalShape::surface_area_along_direction(double tol, const ifcopenshell::geometry::taxonomy::matrix4::ptr& place, double& along_x, double& along_y, double& along_z) const {
	// @todo
	return false;
}

#ifndef IFOPSH_SIMPLE_KERNEL

void ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::Triangulate(ifcopenshell::geometry::Settings settings, const ifcopenshell::geometry::taxonomy::matrix4& place, IfcGeom::Representation::Triangulation* t, int item_id, int surface_style_id, Logger& logger) const {
	throw std::runtime_error("Not implemented");
}

void ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::Serialize(const ifcopenshell::geometry::taxonomy::matrix4& place, std::string& r) const {
	throw std::runtime_error("Not implemented");
}

int ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::num_vertices() const {
	throw std::runtime_error("Not implemented");
}

void ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::set_box(void * b) {
	throw std::runtime_error("Not implemented");
}

int ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::surface_genus() const {
	throw std::runtime_error("Not implemented");
}

bool ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::is_manifold() const {
	throw std::runtime_error("Not implemented");
}

int ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::num_edges() const
{
	throw std::runtime_error("Not implemented");
}

int ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::num_faces() const
{
	throw std::runtime_error("Not implemented");
}

OpaqueNumber ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::CgalShapeHalfSpaceDecomposition::length()
{
	throw std::runtime_error("Not implemented");
}

OpaqueNumber ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::area()
{
	throw std::runtime_error("Not implemented");
}

OpaqueNumber ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::volume()
{
	throw std::runtime_error("Not implemented");
}

OpaqueCoordinate<3> ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::position()
{
	if (planes_.size() == 1) {
		auto xyz = CGAL::ORIGIN + planes_.front().d() * CGAL::Vector_3<Kernel_>(planes_.front().a(), planes_.front().b(), planes_.front().c());
		return OpaqueCoordinate<3>(
			NumberType(xyz.cartesian(0)),
			NumberType(xyz.cartesian(1)),
			NumberType(xyz.cartesian(2))
		);
	} else {
		throw std::runtime_error("Invalid shape type");
	}
}

OpaqueCoordinate<3> ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::axis()
{
	if (planes_.size() == 1) {
		std::array<typename Kernel_::FT, 3> abc{ planes_.front().a(), planes_.front().b(), planes_.front().c() };
		auto minel = std::min_element(abc.begin(), abc.end());
		auto maxel = std::max_element(abc.begin(), abc.end());
		auto maxval = ((-*minel) > *maxel) ? (-*minel) : *maxel;
		return OpaqueCoordinate<3>(
			NumberType(planes_.front().a() / maxval),
			NumberType(planes_.front().b() / maxval),
			NumberType(planes_.front().c() / maxval)
		);
	} else {
		throw std::runtime_error("Invalid shape type");
	}
}

OpaqueCoordinate<4> ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::plane_equation()
{
	if (planes_.size() == 1) {
		std::array<typename Kernel_::FT, 3> abc{ planes_.front().a(), planes_.front().b(), planes_.front().c() };
		auto minel = std::min_element(abc.begin(), abc.end());
		auto maxel = std::max_element(abc.begin(), abc.end());
		auto maxval = ((-*minel) > *maxel) ? (-*minel) : *maxel;
		return OpaqueCoordinate<4>(
			NumberType(planes_.front().a() / maxval),
			NumberType(planes_.front().b() / maxval),
			NumberType(planes_.front().c() / maxval),
			NumberType(planes_.front().d() / maxval)
		);
	} else {
		throw std::runtime_error("Invalid shape type");
	}
}

std::vector<ConversionResultShape*> ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::convex_decomposition()
{
	throw std::runtime_error("Not implemented");
}

ConversionResultShape* ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::halfspaces()
{
	throw std::runtime_error("Not implemented");
}

ConversionResultShape* ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::solid()
{
	return new CgalShape(shape_->evaluate());
}

ConversionResultShape * ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::box()
{
	throw std::runtime_error("Not implemented");
}

std::vector<ConversionResultShape*> ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::vertices()
{
	throw std::runtime_error("Not implemented");
}

std::vector<ConversionResultShape*> ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::edges()
{
	throw std::runtime_error("Not implemented");
}

std::vector<ConversionResultShape*> ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::facets()
{
	std::vector<ConversionResultShape*> res;
	for (auto& p : planes_) {
		res.push_back(new CgalShapeHalfSpaceDecomposition(p));
	}
	return res;
}

ConversionResultShape* ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::add(ConversionResultShape* other)
{
	throw std::runtime_error("Not implemented");
}

ConversionResultShape* ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::subtract(ConversionResultShape* other)
{
	throw std::runtime_error("Not implemented");
}

ConversionResultShape* ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::intersect(ConversionResultShape* other)
{
	throw std::runtime_error("Not implemented");
}

std::pair<OpaqueCoordinate<3>, OpaqueCoordinate<3>> ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::bounding_box() const
{
	throw std::runtime_error("Not implemented");
}

double ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::bounding_box(void *& b) const {
	throw std::runtime_error("Not implemented");
}

ConversionResultShape* ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::moved(ifcopenshell::geometry::taxonomy::matrix4::ptr) const
{
	throw std::runtime_error("Not implemented");
}

std::size_t ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::map(OpaqueCoordinate<4>& from, OpaqueCoordinate<4>& to) {
	plane_map<Kernel_> mp;
	insert_normalized_plane_map(mp, from, to);
	std::size_t mutated = 0;
	auto nw = shape_->map(mp, mutated);
	shape_ = std::move(nw);
	apply_normalized_plane_map(mp, planes_);
	return mutated;
}

std::size_t ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::map(const std::vector<OpaqueCoordinate<4>>& froms, const std::vector<OpaqueCoordinate<4>>& tos) {
	plane_map<Kernel_> mp;
	if (froms.size() != tos.size()) {
		throw std::runtime_error("Expected equal size");
	}
	auto it = froms.begin();
	auto jt = tos.begin();
	for (; it < froms.end(); ++it, ++jt) {
		auto& from = *it;
		auto& to = *jt;
		insert_normalized_plane_map(mp, from, to);
	}
	std::size_t mutated = 0;
	auto nw = shape_->map(mp, mutated);
	shape_ = std::move(nw);
	apply_normalized_plane_map(mp, planes_);
	return mutated;
}


ConversionResultShape* ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::wrap_in_compound()
{
	throw std::runtime_error("Not implemented");
}

#endif
