#include "CgalKernel.h"

bool IfcGeom::CgalKernel::convert_wire_to_face(const cgal_wire_t& wire, cgal_face_t& face) {
  face.outer = wire;
  return true;
}

void IfcGeom::CgalKernel::remove_duplicate_points_from_loop(cgal_wire_t& polygon) {
  std::set<cgal_point_t> points;
  for (int i = 0; i < polygon.size(); ++i) {
    if (points.count(polygon[i])) {
      polygon.erase(polygon.begin()+i);
      --i;
    } else points.insert(polygon[i]);
  }
}

CGAL::Polyhedron_3<Kernel> IfcGeom::CgalKernel::create_polyhedron(std::list<cgal_face_t> &face_list) {
  
  // Naive creation
  CGAL::Polyhedron_3<Kernel> polyhedron;
  PolyhedronBuilder builder(&face_list);
  polyhedron.delegate(builder);
  
  // Stitch edges
  //  std::cout << "Before: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
  CGAL::Polygon_mesh_processing::stitch_borders(polyhedron);
  if (!polyhedron.is_valid()) {
    Logger::Message(Logger::LOG_ERROR, "create_polyhedron: Polyhedron not valid!");
    //    std::ofstream fresult;
    //    fresult.open("/Users/ken/Desktop/invalid.off");
    //    fresult << polyhedron << std::endl;
    //    fresult.close();
    return CGAL::Polyhedron_3<Kernel>();
  } if (polyhedron.is_closed()) {
    if (!CGAL::Polygon_mesh_processing::is_outward_oriented(polyhedron)) {
      CGAL::Polygon_mesh_processing::reverse_face_orientations(polyhedron);
    }
  }
  
  //  std::cout << "After: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
  
  return polyhedron;
}

CGAL::Polyhedron_3<Kernel> IfcGeom::CgalKernel::create_polyhedron(CGAL::Nef_polyhedron_3<Kernel> &nef_polyhedron) {
  if (nef_polyhedron.is_simple()) {
    try {
      CGAL::Polyhedron_3<Kernel> polyhedron;
      nef_polyhedron.convert_to_polyhedron(polyhedron);
      return polyhedron;
    } catch (...) {
      Logger::Message(Logger::LOG_ERROR, "Conversion from Nef to polyhedron failed!");
      return CGAL::Polyhedron_3<Kernel>();
    }
  } else {
    Logger::Message(Logger::LOG_ERROR, "Nef polyhedron not simple: cannot create polyhedron!");
    return CGAL::Polyhedron_3<Kernel>();
  }
}

CGAL::Nef_polyhedron_3<Kernel> IfcGeom::CgalKernel::create_nef_polyhedron(std::list<cgal_face_t> &face_list) {
  CGAL::Polyhedron_3<Kernel> polyhedron = create_polyhedron(face_list);
  CGAL::Polygon_mesh_processing::triangulate_faces(polyhedron);
  CGAL::Nef_polyhedron_3<Kernel> nef_polyhedron;
  try {
    nef_polyhedron = CGAL::Nef_polyhedron_3<Kernel>(polyhedron);
  } catch (...) {
    Logger::Message(Logger::LOG_ERROR, "Conversion to Nef polyhedron failed!");
    return nef_polyhedron;
  } return nef_polyhedron;
}

CGAL::Nef_polyhedron_3<Kernel> IfcGeom::CgalKernel::create_nef_polyhedron(CGAL::Polyhedron_3<Kernel> &polyhedron) {
  if (polyhedron.is_valid()) {
    CGAL::Polygon_mesh_processing::triangulate_faces(polyhedron);
    CGAL::Nef_polyhedron_3<Kernel> nef_polyhedron;
    try {
      nef_polyhedron = CGAL::Nef_polyhedron_3<Kernel>(polyhedron);
    } catch (...) {
      Logger::Message(Logger::LOG_ERROR, "Conversion to Nef polyhedron failed!");
      return nef_polyhedron;
    } return nef_polyhedron;
  } else {
    Logger::Message(Logger::LOG_ERROR, "Polyhedron not valid: cannot create Nef polyhedron!");
    return CGAL::Nef_polyhedron_3<Kernel>();
  }
}

//CGAL::Polyhedron_3<Kernel> IfcGeom::CgalKernel::triangulate_faces(CGAL::Polyhedron_3<Kernel> &polyhedron) {
//  std::list<cgal_face_t> face_list;
//  
//  for (CGAL::Polyhedron_3<Kernel>::Facet_const_iterator current_facet = polyhedron.facets_begin();
//       current_facet != polyhedron.facets_end();
//       ++current_facet) {
//    
//    // Triangle
//    if (current_facet->is_triangle()) {
//      face_list.push_back(cgal_face_t());
//      CGAL::Polyhedron_3<Kernel>::Halfedge_around_facet_const_circulator current_halfedge = current_facet->facet_begin();
//      do {
//        face_list.back().outer.push_back(current_halfedge->vertex()->point());
//        ++current_halfedge;
//      } while (current_halfedge != current_facet->facet_begin());
//    }
//    
//    // Polygon
//    else {
//      std::list<Kernel::Point_3> points_in_polygon;
//      
//    }
//  }
//  
//  return create_polyhedron(face_list);
//}
