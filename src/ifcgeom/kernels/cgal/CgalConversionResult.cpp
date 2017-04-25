#include "CgalKernel.h"
#include "CgalConversionResult.h"

void IfcGeom::CgalShape::Triangulate(const IfcGeom::IteratorSettings & settings, const IfcGeom::ConversionResultPlacement * place, IfcGeom::Representation::Triangulation<double>* t, int surface_style_id) const {
  cgal_shape_t s = shape_;
  const cgal_placement_t& trsf = dynamic_cast<const CgalPlacement*>(place)->trsf();
  
  // Apply transformation
  if (place != NULL) for (auto &vertex: vertices(s)) {
    vertex->point() = vertex->point().transform(trsf);
  }
  
  std::string error_file_path;
  for (unsigned int error_number = 1; error_number < 1000; ++error_number) {
    error_file_path = std::string("/Users/ken/Desktop/error/error");
    error_file_path += std::to_string(error_number);
    error_file_path += ".off";
    std::ifstream file_path_test(error_file_path);
    if (!file_path_test.good()) break;
  }
  
  if (!s.is_valid()) {
    Logger::Message(Logger::LOG_ERROR, "Invalid Polyhedron_3 in object (before triangulation)");
    std::ofstream ferror;
    ferror.open(error_file_path);
    ferror << s << std::endl;
    ferror.close();
    return;
  }
  
//  std::ofstream fbefore;
//  fbefore.open("/Users/ken/Desktop/before.off");
//  fbefore << s << std::endl;
//  fbefore.close();
  
  // Triangulate the shape and compute the normals
//  std::map<cgal_vertex_descriptor_t, Kernel::Vector_3> vertex_normals;
//  boost::associative_property_map<std::map<cgal_vertex_descriptor_t, Kernel::Vector_3>> vertex_normals_map(vertex_normals);
  std::map<cgal_face_descriptor_t, Kernel::Vector_3> face_normals;
  boost::associative_property_map<std::map<cgal_face_descriptor_t, Kernel::Vector_3>> face_normals_map(face_normals);
  cgal_shape_t s_copy(s);
  bool success = false;
  try {
    success = CGAL::Polygon_mesh_processing::triangulate_faces(s);
  } catch (...) {
    Logger::Message(Logger::LOG_ERROR, "Triangulation crashed");
    std::ofstream ferror;
    ferror.open(error_file_path);
    ferror << s << std::endl;
    ferror.close();
    return;
  } if (!success) {
    Logger::Message(Logger::LOG_ERROR, "Triangulation failed");
    std::ofstream ferror;
    ferror.open(error_file_path);
    ferror << s << std::endl;
    ferror.close();
    return;
  }
  //    std::cout << "Triangulated model: " << s.size_of_facets() << " facets and " << s.size_of_vertices() << " vertices" << std::endl;
  
//  std::ofstream fafter;
//  fafter.open("/Users/ken/Desktop/after.off");
//  fafter << s << std::endl;
//  fafter.close();
  
  if (!s.is_valid()) {
    Logger::Message(Logger::LOG_ERROR, "Invalid Polyhedron_3 in object (after triangulation)");
    std::ofstream ferror;
    ferror.open(error_file_path);
    ferror << s_copy << std::endl;
    ferror.close();
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
