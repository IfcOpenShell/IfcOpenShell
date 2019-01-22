#include "CgalConversionResult.h"

template <typename Precision>
void triangulate_helper(const cgal_shape_t, const IfcGeom::IteratorSettings & settings, const IfcGeom::ConversionResultPlacement * place, IfcGeom::Representation::Triangulation<Precision>* t, int surface_style_id) {
  cgal_shape_t s = shape_;
  const cgal_placement_t& trsf = dynamic_cast<const CgalPlacement*>(place)->trsf();
//  std::cout << "Model: " << s.size_of_facets() << " facets and " << s.size_of_vertices() << " vertices" << std::endl;
//  std::cout << "Valid: " << s.is_valid() << std::endl;
  
  // Apply transformation
  if (place != NULL) for (auto &vertex: vertices(s)) {
    vertex->point() = vertex->point().transform(trsf);
  }
  
  // Triangulate the shape and compute the normals
  std::map<cgal_vertex_descriptor_t, Kernel::Vector_3> vertex_normals;
  boost::associative_property_map<std::map<cgal_vertex_descriptor_t, Kernel::Vector_3>> vertex_normals_map(vertex_normals);
  std::map<cgal_face_descriptor_t, Kernel::Vector_3> face_normals;
  boost::associative_property_map<std::map<cgal_face_descriptor_t, Kernel::Vector_3>> face_normals_map(face_normals);
  if (CGAL::Polygon_mesh_processing::triangulate_faces(s)) {
//    std::cout << "Triangulated model: " << s.size_of_facets() << " facets and " << s.size_of_vertices() << " vertices" << std::endl;
  } else {
    Logger::Message(Logger::LOG_ERROR, "Failed to triangulate shape");
    return;
  }

  CGAL::Polygon_mesh_processing::compute_normals(s, vertex_normals_map, face_normals_map);

  // Iterates over the faces of the shape
  int num_faces = 0, num_vertices = 0;
  for (auto &face: faces(s)) {
    CGAL::Polyhedron_3<Kernel>::Halfedge_around_facet_const_circulator current_halfedge = face->facet_begin();
    do {
      t->addVertex(surface_style_id,
                   CGAL::to_double(current_halfedge->vertex()->point().cartesian(0)),
                   CGAL::to_double(current_halfedge->vertex()->point().cartesian(1)),
                   CGAL::to_double(current_halfedge->vertex()->point().cartesian(2)));
      for (int i = 0; i < 3; ++i) t->normals().push_back(CGAL::to_double(face_normals_map[face].cartesian(i)));
      t->faces().push_back(num_vertices);
      ++num_vertices;
      ++current_halfedge;
    } while (current_halfedge != face->facet_begin());
    t->material_ids().push_back(surface_style_id);
    ++num_faces;
  }
}

void IfcGeom::CgalShape::Triangulate(const IfcGeom::IteratorSettings & settings, const IfcGeom::ConversionResultPlacement * place, IfcGeom::Representation::Triangulation<float>* t, int surface_style_id) const {
	triangulate_helper(shape_, settings, place, t, surface_style_id);
}

void IfcGeom::CgalShape::Triangulate(const IfcGeom::IteratorSettings & settings, const IfcGeom::ConversionResultPlacement * place, IfcGeom::Representation::Triangulation<double>* t, int surface_style_id) const {
	triangulate_helper(shape_, settings, place, t, surface_style_id);
}
