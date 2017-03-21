#include "CgalKernel.h"

bool IfcGeom::CgalKernel::convert_wire_to_face(const cgal_wire_t& wire, cgal_face_t& face) {
  face.outer = wire;
  return true;
}

void IfcGeom::CgalKernel::remove_duplicate_points_from_loop(cgal_wire_t& polygon, bool closed, double tol) {
  if (tol <= 0.) tol = getValue(GV_PRECISION);
  tol *= tol;
  
  for (int i = 0; i < polygon.size(); ++i) {
    for (int j = i+1; j < polygon.size(); ++j) {
      if (CGAL::squared_distance(polygon[i], polygon[j]) < tol) {
        polygon.erase(polygon.begin()+j);
        --j;
      }
    } if (closed) {
      if (CGAL::squared_distance(polygon.front(), polygon.back()) < tol) {
        polygon.erase(polygon.begin()+polygon.size()-1);
      }
    }
  }
}

CGAL::Nef_polyhedron_3<Kernel> IfcGeom::CgalKernel::create_nef_polyhedron(std::list<cgal_face_t> &face_list) {
  
  // Naive creation
  CGAL::Polyhedron_3<Kernel> polyhedron = CGAL::Polyhedron_3<Kernel>();
  PolyhedronBuilder builder(&face_list);
  polyhedron.delegate(builder);
  
  // Stitch edges
  //  std::cout << "Before: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
  CGAL::Polygon_mesh_processing::stitch_borders(polyhedron);
  if (!polyhedron.is_valid()) {
    std::cout << "create_nef_polyhedron: Polyhedron not valid!" << std::endl;
//    std::ofstream fresult;
//    fresult.open("/Users/ken/Desktop/invalid.off");
//    fresult << polyhedron << std::endl;
//    fresult.close();
    return CGAL::Nef_polyhedron_3<Kernel>();
  } if (!polyhedron.is_closed()) {
    std::cout << "create_nef_polyhedron: Polyhedron not closed" << std::endl;
//    std::ofstream fresult;
//    fresult.open("/Users/ken/Desktop/open.off");
//    fresult << polyhedron << std::endl;
//    fresult.close();
    // TODO: Nef constructor doesn't support open meshes
    return CGAL::Nef_polyhedron_3<Kernel>(polyhedron);
  }
  if (!CGAL::Polygon_mesh_processing::is_outward_oriented(polyhedron)) {
    CGAL::Polygon_mesh_processing::reverse_face_orientations(polyhedron);
  }
  //  std::cout << "After: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
  
  return CGAL::Nef_polyhedron_3<Kernel>(polyhedron);
}
