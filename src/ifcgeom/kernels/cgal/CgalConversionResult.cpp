#include "CgalKernel.h"
#include "CgalConversionResult.h"

void IfcGeom::CgalShape::Triangulate(const IfcGeom::IteratorSettings & settings, const IfcGeom::ConversionResultPlacement * place, IfcGeom::Representation::Triangulation<double>* t, int surface_style_id) const {
  cgal_shape_t s = shape_;
  const cgal_placement_t& trsf = dynamic_cast<const CgalPlacement*>(place)->trsf();
  
  std::cout << "Nef Model: " << s.number_of_facets() << " facets and " << s.number_of_vertices() << " vertices" << std::endl;
  std::cout << "Simple: " << s.is_simple() << std::endl;
  
  CGAL::Polyhedron_3<Kernel> polyhedron;
  if (s.is_simple()) s.convert_to_polyhedron(polyhedron);
  else {
    std::list<cgal_face_t> face_list;
    face_list.push_back(cgal_face_t());
    std::set<CGAL::Nef_polyhedron_3<Kernel>::Halffacet_const_handle> visited_halffacets;
    for (CGAL::Nef_polyhedron_3<Kernel>::Halffacet_const_iterator current_halffacet = s.halffacets_begin();
         current_halffacet != s.halffacets_end();
         ++current_halffacet) {
      if (visited_halffacets.count(current_halffacet->twin())) continue;
      for (CGAL::Nef_polyhedron_3<Kernel>::Halffacet_cycle_const_iterator current_halffacet_cycle = current_halffacet->facet_cycles_begin();
           current_halffacet_cycle != current_halffacet->facet_cycles_end();
           ++current_halffacet_cycle) {
        if (current_halffacet_cycle.is_shalfloop()) continue;
        CGAL::Nef_polyhedron_3<Kernel>::SHalfedge_const_handle first_shalfedge = current_halffacet_cycle;
        CGAL::Nef_polyhedron_3<Kernel>::SHalfedge_const_handle current_shalfedge = first_shalfedge;
        if (!face_list.back().outer.empty()) face_list.push_back(cgal_face_t());
        do {
          face_list.back().outer.push_back(current_shalfedge->source()->center_vertex()->point());
          current_shalfedge = current_shalfedge->next();
        } while (current_shalfedge != first_shalfedge);
      }
    } if (face_list.back().outer.empty()) face_list.pop_back();
    PolyhedronBuilder builder(&face_list);
    polyhedron.delegate(builder);
  }
  
  std::cout << "Polyhedron Model: " << polyhedron.size_of_facets() << " facets and " << polyhedron.size_of_vertices() << " vertices" << std::endl;
  std::cout << "Valid: " << polyhedron.is_valid() << std::endl;
  
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
