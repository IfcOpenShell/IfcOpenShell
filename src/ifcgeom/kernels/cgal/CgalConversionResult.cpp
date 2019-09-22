#include "CgalConversionResult.h"

#include "../../../ifcparse/IfcLogger.h"
#include "../../../ifcgeom/schema_agnostic/IfcGeomRepresentation.h"

void ifcopenshell::geometry::CgalShape::Triangulate(const settings& settings, const ifcopenshell::geometry::taxonomy::matrix4& place, Representation::Triangulation* t, int surface_style_id) const {
	// Copy is made because triangulate_faces() does not accept a const argument
  cgal_shape_t s = shape_;

  if (!place.components.isIdentity()) {
	  const auto& m = place.components;

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
  
  if (!s.is_valid()) {
    Logger::Message(Logger::LOG_ERROR, "Invalid Polyhedron_3 in object (before triangulation)");
    return;
  }
  
  // Triangulate the shape and compute the normals
//  std::map<cgal_vertex_descriptor_t, Kernel_::Vector_3> vertex_normals;
//  boost::associative_property_map<std::map<cgal_vertex_descriptor_t, Kernel_::Vector_3>> vertex_normals_map(vertex_normals);
  std::map<cgal_face_descriptor_t, Kernel_::Vector_3> face_normals;
  boost::associative_property_map<std::map<cgal_face_descriptor_t, Kernel_::Vector_3>> face_normals_map(face_normals);

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
    return;
  }
  
//  CGAL::Polygon_mesh_processing::compute_normals(s, vertex_normals_map, face_normals_map);
  try {
	  CGAL::Polygon_mesh_processing::compute_face_normals(s, face_normals_map);
  } catch (...) {
	  Logger::Message(Logger::LOG_ERROR, "Face normal calculation failed");
	  return;
  }
  
  int num_faces = 0, num_vertices = 0;
  for (auto &face: faces(s)) {
    if (!face->is_triangle()) {
      std::cout << "Warning: non-triangular face!" << std::endl;
      continue;
    }
    CGAL::Polyhedron_3<Kernel_>::Halfedge_around_facet_const_circulator current_halfedge = face->facet_begin();
	int vertexidx[3];
	int i = 0;
    do {
		vertexidx[i++] = t->addVertex(surface_style_id,
                   CGAL::to_double(current_halfedge->vertex()->point().cartesian(0)),
                   CGAL::to_double(current_halfedge->vertex()->point().cartesian(1)),
                   CGAL::to_double(current_halfedge->vertex()->point().cartesian(2)));

      const double nx = CGAL::to_double(face_normals_map[face].cartesian(0));
      const double ny = CGAL::to_double(face_normals_map[face].cartesian(1));
      const double nz = CGAL::to_double(face_normals_map[face].cartesian(2));
      t->addNormal(nx, ny, nz);

      ++num_vertices;
      ++current_halfedge;
    } while (current_halfedge != face->facet_begin());

    t->addFace(surface_style_id, vertexidx[0], vertexidx[1], vertexidx[2]);

    ++num_faces;
  }

}
