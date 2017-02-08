#include "CgalKernel.h"
#include "CgalConversionResult.h"

void IfcGeom::CgalShape::Triangulate(const IfcGeom::IteratorSettings & settings, const IfcGeom::ConversionResultPlacement * place, IfcGeom::Representation::Triangulation<double>* t, int surface_style_id) const {
  cgal_shape_t s = shape_;
  const cgal_placement_t& trsf = dynamic_cast<const CgalPlacement*>(place)->trsf();
  
  // Apply transformation
//  for (auto &vertex: vertices(s)) {
//    vertex->point() = vertex->point().transform(trsf);
//  }
  
  // Triangulate the shape and compute the normals
  std::map<cgal_vertex_descriptor_t, Kernel::Vector_3> vertex_normals;
  boost::associative_property_map<std::map<cgal_vertex_descriptor_t, Kernel::Vector_3>> vertex_normals_map(vertex_normals);
  std::map<cgal_face_descriptor_t, Kernel::Vector_3> face_normals;
  boost::associative_property_map<std::map<cgal_face_descriptor_t, Kernel::Vector_3>> face_normals_map(face_normals);
  try {
    CGAL::Polygon_mesh_processing::triangulate_faces(s);
    CGAL::Polygon_mesh_processing::compute_normals(s, vertex_normals_map, face_normals_map);
  } catch (...) {

    // TODO: Catch outside
    // Logger::Message(Logger::LOG_ERROR,"Failed to triangulate shape:",ifc_file->entityById(_id)->entity);
    Logger::Message(Logger::LOG_ERROR, "Failed to triangulate shape");
    return;
  }

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
