#include "CgalKernel.h"
#include "CgalConversionResult.h"

void IfcGeom::CgalShape::Triangulate(const IfcGeom::IteratorSettings & settings, const IfcGeom::ConversionResultPlacement * place, IfcGeom::Representation::Triangulation<double>* t, int surface_style_id) const {
  cgal_shape_t s = shape_;
  const cgal_placement_t& trsf = dynamic_cast<const CgalPlacement*>(place)->trsf();
//  std::cout << "Model: " << s.size_of_facets() << " facets and " << s.size_of_vertices() << " vertices" << std::endl;
//  std::cout << "Valid: " << s.is_valid() << std::endl;
  
  CGAL::Polyhedron_3<Kernel> polyhedron;
  s.convert_to_polyhedron(polyhedron);
  
  // Apply transformation
  if (place != NULL) for (auto &vertex: vertices(polyhedron)) {
    vertex->point() = vertex->point().transform(trsf);
  }
  
//  std::ofstream fbefore;
//  fbefore.open("/Users/ken/Desktop/before.off");
//  fbefore << s << std::endl;
//  fbefore.close();
  
  // Triangulate the shape and compute the normals
  std::map<cgal_vertex_descriptor_t, Kernel::Vector_3> vertex_normals;
  boost::associative_property_map<std::map<cgal_vertex_descriptor_t, Kernel::Vector_3>> vertex_normals_map(vertex_normals);
  std::map<cgal_face_descriptor_t, Kernel::Vector_3> face_normals;
  boost::associative_property_map<std::map<cgal_face_descriptor_t, Kernel::Vector_3>> face_normals_map(face_normals);
  if (CGAL::Polygon_mesh_processing::triangulate_faces(polyhedron)) {
//    std::cout << "Triangulated model: " << s.size_of_facets() << " facets and " << s.size_of_vertices() << " vertices" << std::endl;
  } else {
    Logger::Message(Logger::LOG_ERROR, "Failed to triangulate shape");
    return;
  }
  
//  std::ofstream fafter;
//  fafter.open("/Users/ken/Desktop/after.off");
//  fafter << s << std::endl;
//  fafter.close();

  CGAL::Polygon_mesh_processing::compute_normals(polyhedron, vertex_normals_map, face_normals_map);
  
  for (auto &face: faces(polyhedron)) {
    if (!face->is_triangle()) {
      std::cout << "Warning: non-triangular face!" << std::endl;
      continue;
    }
    CGAL::Polyhedron_3<Kernel>::Halfedge_around_facet_const_circulator current_halfedge = face->facet_begin();
    do {
      t->faces().push_back((int)t->verts().size()/3);
      t->addVertex(surface_style_id,
                   CGAL::to_double(current_halfedge->vertex()->point().cartesian(0)),
                   CGAL::to_double(current_halfedge->vertex()->point().cartesian(1)),
                   CGAL::to_double(current_halfedge->vertex()->point().cartesian(2)));
      for (int i = 0; i < 3; ++i) t->normals().push_back(CGAL::to_double(face_normals_map[face].cartesian(i)));
      ++current_halfedge;
    } while (current_halfedge != face->facet_begin());
    t->material_ids().push_back(surface_style_id);
  }
}
