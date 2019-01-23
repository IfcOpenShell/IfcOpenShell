#include "CgalConversionResult.h"

#include "../../../ifcparse/IfcLogger.h"
#include "../../../ifcgeom/schema_agnostic/IfcGeomRepresentation.h"

template <typename Precision>
void triangulate_helper(const cgal_shape_t& shape_const, const IfcGeom::IteratorSettings & settings, const IfcGeom::ConversionResultPlacement * place, IfcGeom::Representation::Triangulation<Precision>* t, int surface_style_id) {
  // Copy is made because triangulate_faces() does not accept a const argument
  cgal_shape_t s = shape_const;

  const cgal_placement_t& trsf = dynamic_cast<const IfcGeom::CgalPlacement*>(place)->trsf();
//  std::cout << "Model: " << s.size_of_facets() << " facets and " << s.size_of_vertices() << " vertices" << std::endl;
//  std::cout << "Valid: " << s.is_valid() << std::endl;
  
  // Apply transformation
  if (place != NULL) for (auto &vertex: vertices(s)) {
    vertex->point() = vertex->point().transform(trsf);
  }
  
  if (!s.is_valid()) {
    Logger::Message(Logger::LOG_ERROR, "Invalid Polyhedron_3 in object (before triangulation)");
    return;
  }
  
  // Triangulate the shape and compute the normals
//  std::map<cgal_vertex_descriptor_t, Kernel::Vector_3> vertex_normals;
//  boost::associative_property_map<std::map<cgal_vertex_descriptor_t, Kernel::Vector_3>> vertex_normals_map(vertex_normals);
  std::map<cgal_face_descriptor_t, Kernel::Vector_3> face_normals;
  boost::associative_property_map<std::map<cgal_face_descriptor_t, Kernel::Vector_3>> face_normals_map(face_normals);

  bool success = false;
  try {
    success = CGAL::Polygon_mesh_processing::triangulate_faces(s);
  } catch (...) {
    Logger::Message(Logger::LOG_ERROR, "Triangulation crashed");
    return;
  }
  
  if (!success) {
    Logger::Message(Logger::LOG_ERROR,     return;
"Triangulation failed");
  }
  //    std::cout << "Triangulated model: " << s.size_of_facets() << " facets and " << s.size_of_vertices() << " vertices" << std::endl;
  
  if (!s.is_valid()) {
    Logger::Message(Logger::LOG_ERROR, "Invalid Polyhedron_3 in object (after triangulation)");
    return;
  }
  
//  CGAL::Polygon_mesh_processing::compute_normals(s, vertex_normals_map, face_normals_map);
  CGAL::Polygon_mesh_processing::compute_face_normals(s, face_normals_map);
  
  for (auto &face: faces(s)) {
    if (!face->is_triangle()) {
      std::cout << "Warning: non-triangular face!" << std::endl;
      continue;
    }
    CGAL::Polyhedron_3<Kernel>::Halfedge_around_facet_const_circulator current_halfedge = face->facet_begin();
    do {
      t->addVertex(surface_style_id,
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

    t->addFace(surface_style_id, num_vertices-3, num_vertices-2, num_vertices-1);

    ++num_faces;
  }

}

void IfcGeom::CgalShape::Triangulate(const IfcGeom::IteratorSettings & settings, const IfcGeom::ConversionResultPlacement * place, IfcGeom::Representation::Triangulation<float>* t, int surface_style_id) const {
	triangulate_helper(shape_, settings, place, t, surface_style_id);
}

void IfcGeom::CgalShape::Triangulate(const IfcGeom::IteratorSettings & settings, const IfcGeom::ConversionResultPlacement * place, IfcGeom::Representation::Triangulation<double>* t, int surface_style_id) const {
	triangulate_helper(shape_, settings, place, t, surface_style_id);
}
