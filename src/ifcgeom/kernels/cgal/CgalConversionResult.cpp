#include "CgalConversionResult.h"
#include "CgalKernel.h"

#include <CGAL/Polygon_mesh_processing/repair.h>

#include "../../../ifcparse/IfcLogger.h"
#include "../../../ifcgeom/IfcGeomRepresentation.h"

using IfcGeom::OpaqueNumber;
using IfcGeom::OpaqueCoordinate;
using IfcGeom::NumberNativeDouble;
using IfcGeom::ConversionResultShape;

#ifdef IFOPSH_SIMPLE_KERNEL
#define NumberType NumberNativeDouble
#else
using ifcopenshell::geometry::NumberEpeck;
#define NumberType NumberEpeck
#endif

ifcopenshell::geometry::CgalShape::CgalShape(const cgal_shape_t & shape) {
	shape_ = shape;
	CGAL::Polygon_mesh_processing::triangulate_faces(*shape_);
	CGAL::Polygon_mesh_processing::remove_degenerate_faces(*shape_);
}

#ifndef IFOPSH_SIMPLE_KERNEL
void ifcopenshell::geometry::CgalShape::to_poly() const {
	if (!shape_) {
		shape_.emplace();
		nef_->convert_to_polyhedron(*shape_);
	}
}

void ifcopenshell::geometry::CgalShape::to_nef() const {
	if (!nef_) {
		nef_ = utils::create_nef_polyhedron(*shape_);
	}
}
#endif

void ifcopenshell::geometry::CgalShape::Triangulate(ifcopenshell::geometry::Settings settings, const ifcopenshell::geometry::taxonomy::matrix4& place, IfcGeom::Representation::Triangulation* t, int surface_style_id) const {
	// Copy is made because triangulate_faces() obviously does not accept a const argument
	// ... also becuase of transforming the vertex positions, right?
	cgal_shape_t s = *this;

	if (!place.is_identity()) {
		const auto& m = place.ccomponents();

		// @todo check
		const cgal_placement_t trsf(
			m(0, 0), m(0, 1), m(0, 2), m(0, 3),
			m(1, 0), m(1, 1), m(1, 2), m(1, 3),
			m(2, 0), m(2, 1), m(2, 2), m(2, 3));

		// Apply transformation
		for (auto &vertex : vertices(s)) {
			vertex->point() = vertex->point().transform(trsf);
		}
	}

	if (!std::all_of(s.facets_begin(), s.facets_end(), [](auto f) { return f.is_triangle(); })) {

		if (!s.is_valid()) {
			Logger::Message(Logger::LOG_ERROR, "Invalid Polyhedron_3 in object (before triangulation)");
			return;
		}

		CGAL::Polygon_mesh_processing::remove_degenerate_faces(s);

		bool success = false;
		try {
			success = CGAL::Polygon_mesh_processing::triangulate_faces(s);
		} catch (...) {
			Logger::Message(Logger::LOG_ERROR, "Triangulation crashed");
			return;
		}

		if (!success) {
			Logger::Message(Logger::LOG_ERROR, "Triangulation failed");
			return;
		}
		//    std::cout << "Triangulated model: " << s.size_of_facets() << " facets and " << s.size_of_vertices() << " vertices" << std::endl;

		if (!s.is_valid()) {
			Logger::Message(Logger::LOG_ERROR, "Invalid Polyhedron_3 in object (after triangulation)");
			// return;
		}

	}

	// std::map<cgal_vertex_descriptor_t, Kernel_::Vector_3> vertex_normals;
	// boost::associative_property_map<std::map<cgal_vertex_descriptor_t, Kernel_::Vector_3>> vertex_normals_map(vertex_normals);
	
	// Triangulate the shape and compute the normals
	std::map<cgal_face_descriptor_t, Kernel_::Vector_3> face_normals;
	boost::associative_property_map<std::map<cgal_face_descriptor_t, Kernel_::Vector_3>> face_normals_map(face_normals);

	//  CGAL::Polygon_mesh_processing::compute_normals(s, vertex_normals_map, face_normals_map);
	try {
		CGAL::Polygon_mesh_processing::compute_face_normals(s, face_normals_map);
	} catch (...) {
		Logger::Message(Logger::LOG_ERROR, "Face normal calculation failed");
		return;
	}

	// We do welding here in addition to in the triangulation item, because
	// CGAL does not have a concept of vertices with identity like OCCT has.
	typedef std::tuple<Kernel_::FT, Kernel_::FT, Kernel_::FT, Kernel_::FT, Kernel_::FT, Kernel_::FT> postion_normal;
	std::map<postion_normal, size_t> welds;

	int num_faces = 0, num_vertices = 0;
	for (auto &face : faces(s)) {
		if (!face->is_triangle()) {
			std::cout << "Warning: non-triangular face!" << std::endl;
			continue;
		}
		CGAL::Polyhedron_3<Kernel_>::Halfedge_around_facet_const_circulator current_halfedge = face->facet_begin();
		int vertexidx[3];
		int i = 0;
		do {
			postion_normal pn = {
				current_halfedge->vertex()->point().cartesian(0),
				current_halfedge->vertex()->point().cartesian(1),
				current_halfedge->vertex()->point().cartesian(2),
				face_normals_map[face].cartesian(0),
				face_normals_map[face].cartesian(1),
				face_normals_map[face].cartesian(2)
			};

			// @todo normalzie based on largest component?

			size_t vidx;
			auto it = welds.find(pn);
			if (it == welds.end()) {
				vidx = t->addVertex(
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

			vertexidx[i++] = vidx;

			++num_vertices;
			++current_halfedge;
		} while (current_halfedge != face->facet_begin());

		t->addFace(surface_style_id, vertexidx[0], vertexidx[1], vertexidx[2]);

		++num_faces;
	}

}

void ifcopenshell::geometry::CgalShape::Serialize(const ifcopenshell::geometry::taxonomy::matrix4& place, std::string& r) const {
	cgal_shape_t s = *this;

	if (!place.is_identity()) {
		const auto& m = place.ccomponents();

		// @todo check
		const cgal_placement_t trsf(
			m(0, 0), m(0, 1), m(0, 2), m(0, 3),
			m(1, 0), m(1, 1), m(1, 2), m(1, 3),
			m(2, 0), m(2, 1), m(2, 2), m(2, 3));

		// Apply transformation
		for (auto &vertex : vertices(s)) {
			vertex->point() = vertex->point().transform(trsf);
		}
	}

	std::stringstream sstream;
	sstream << s;
	r = sstream.str();
}

#include <CGAL/Polygon_mesh_processing/bbox.h>

double ifcopenshell::geometry::CgalShape::bounding_box(void *& b) const {
	if (b == nullptr) {
		b = new CGAL::Bbox_3;
	}
	auto& bb = (*((CGAL::Bbox_3*)b));
	bb += CGAL::Polygon_mesh_processing::bbox(static_cast<cgal_shape_t>(*this));
	return (bb.xmax() - bb.xmin()) * (bb.ymax() - bb.ymin()) * (bb.zmax() - bb.zmin());
}

int ifcopenshell::geometry::CgalShape::num_vertices() const {
	return static_cast<cgal_shape_t>(*this).size_of_vertices();
}

void ifcopenshell::geometry::CgalShape::set_box(void * b) {
	auto& bb = (*((CGAL::Bbox_3*)b));
	Kernel_::Point_3 lower(bb.xmin(), bb.ymin(), bb.zmin());
	Kernel_::Point_3 upper(bb.xmax(), bb.ymax(), bb.zmax());
	shape_ = ifcopenshell::geometry::utils::create_cube(lower, upper);
}

int ifcopenshell::geometry::CgalShape::surface_genus() const {
	to_poly();
	int nv = shape_->size_of_vertices();
	int ne = shape_->size_of_halfedges() / 2;
	int nf = shape_->size_of_facets();

	const int euler = nv - ne + nf;
	const int genus = (2 - euler) / 2;

	return genus;
}

bool ifcopenshell::geometry::CgalShape::is_manifold() const {
	// @todo ?
	to_poly();
	return shape_->is_valid();
}

int ifcopenshell::geometry::CgalShape::num_edges() const
{
	to_poly();
	return shape_->size_of_halfedges() / 2;
}

int ifcopenshell::geometry::CgalShape::num_faces() const
{
	to_poly();
	return shape_->size_of_facets();
}

std::shared_ptr<OpaqueNumber> ifcopenshell::geometry::CgalShape::CgalShape::length()
{
	to_poly();
	Kernel_::FT len = 0;
	for (auto it = shape_->edges_begin(); it != shape_->edges_end(); ++it) {
		len += CGAL::approximate_sqrt(CGAL::Segment_3<Kernel_>(
			it->vertex()->point(),
			it->next()->vertex()->point()
		).squared_length());
	}
	return std::make_shared<NumberType>(len);
}

std::shared_ptr<OpaqueNumber> ifcopenshell::geometry::CgalShape::area()
{
	to_poly();
	return std::make_shared<NumberType>(CGAL::Polygon_mesh_processing::area(*shape_));
}

std::shared_ptr<OpaqueNumber> ifcopenshell::geometry::CgalShape::volume()
{
	to_poly();
	return std::make_shared<NumberType>(CGAL::Polygon_mesh_processing::volume(*shape_));
}

OpaqueCoordinate<3> ifcopenshell::geometry::CgalShape::position()
{
	throw std::runtime_error("Invalid shape type");
}

OpaqueCoordinate<3> ifcopenshell::geometry::CgalShape::axis()
{
	throw std::runtime_error("Invalid shape type");
}

OpaqueCoordinate<4> ifcopenshell::geometry::CgalShape::plane_equation()
{
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
			result.push_back(new CgalShape(P));
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
	return new CgalShapeHalfSpaceDecomposition(nef());
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

std::vector<ConversionResultShape*> ifcopenshell::geometry::CgalShape::edges()
{
	throw std::runtime_error("Not implemented");
}

std::vector<ConversionResultShape*> ifcopenshell::geometry::CgalShape::facets()
{
	throw std::runtime_error("Not implemented");
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

std::pair<OpaqueCoordinate<3>, OpaqueCoordinate<3>> ifcopenshell::geometry::CgalShape::bounding_box() const
{
	throw std::runtime_error("Not implemented");
}

ConversionResultShape* ifcopenshell::geometry::CgalShape::moved(ifcopenshell::geometry::taxonomy::matrix4::ptr place) const
{
	cgal_shape_t s = *this;

	if (!place->is_identity()) {
		const auto& m = place->ccomponents();

		// @todo check
		const cgal_placement_t trsf(
			m(0, 0), m(0, 1), m(0, 2), m(0, 3),
			m(1, 0), m(1, 1), m(1, 2), m(1, 3),
			m(2, 0), m(2, 1), m(2, 2), m(2, 3));

		// Apply transformation
		for (auto &vertex : vertices(s)) {
			vertex->point() = vertex->point().transform(trsf);
		}
	}

	return new CgalShape(s);
}

void ifcopenshell::geometry::CgalShape::map(OpaqueCoordinate<4>& from, OpaqueCoordinate<4>& to) {
	throw std::runtime_error("Not implemented");
}

#ifndef IFOPSH_SIMPLE_KERNEL

void ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::Triangulate(ifcopenshell::geometry::Settings settings, const ifcopenshell::geometry::taxonomy::matrix4& place, IfcGeom::Representation::Triangulation* t, int surface_style_id) const {
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

std::shared_ptr<OpaqueNumber> ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::CgalShapeHalfSpaceDecomposition::length()
{
	throw std::runtime_error("Not implemented");
}

std::shared_ptr<OpaqueNumber> ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::area()
{
	throw std::runtime_error("Not implemented");
}

std::shared_ptr<OpaqueNumber> ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::volume()
{
	throw std::runtime_error("Not implemented");
}

OpaqueCoordinate<3> ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::position()
{
	if (planes_.size() == 1) {
		auto xyz = CGAL::ORIGIN + planes_.front().d() * CGAL::Vector_3<Kernel_>(planes_.front().a(), planes_.front().b(), planes_.front().c());
		return OpaqueCoordinate<3>(
			std::make_shared<NumberType>(xyz.cartesian(0)),
			std::make_shared<NumberType>(xyz.cartesian(1)),
			std::make_shared<NumberType>(xyz.cartesian(2))
		);
	} else {
		throw std::runtime_error("Invalid shape type");
	}
}

OpaqueCoordinate<3> ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::axis()
{
	if (planes_.size() == 1) {
		return OpaqueCoordinate<3>(
			std::make_shared<NumberType>(planes_.front().a()),
			std::make_shared<NumberType>(planes_.front().b()),
			std::make_shared<NumberType>(planes_.front().c())
		);
	} else {
		throw std::runtime_error("Invalid shape type");
	}
}

OpaqueCoordinate<4> ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::plane_equation()
{
	if (planes_.size() == 1) {
		return OpaqueCoordinate<4>(
			std::make_shared<NumberType>(planes_.front().a()),
			std::make_shared<NumberType>(planes_.front().b()),
			std::make_shared<NumberType>(planes_.front().c()),
			std::make_shared<NumberType>(planes_.front().d())
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

void ifcopenshell::geometry::CgalShapeHalfSpaceDecomposition::map(OpaqueCoordinate<4>& from, OpaqueCoordinate<4>& to) {
	plane_map<Kernel_> mp;
	mp.insert({
		CGAL::Plane_3<Kernel_>(
			std::static_pointer_cast<NumberEpeck>(from.values[0])->value(),
			std::static_pointer_cast<NumberEpeck>(from.values[1])->value(),
			std::static_pointer_cast<NumberEpeck>(from.values[2])->value(),
			std::static_pointer_cast<NumberEpeck>(from.values[3])->value()
		),
		CGAL::Plane_3<Kernel_>(
			std::static_pointer_cast<NumberEpeck>(to.values[0])->value(),
			std::static_pointer_cast<NumberEpeck>(to.values[1])->value(),
			std::static_pointer_cast<NumberEpeck>(to.values[2])->value(),
			std::static_pointer_cast<NumberEpeck>(to.values[3])->value()
		)
	});
	auto nw = shape_->map(mp);
	shape_ = std::move(nw);
}

#endif