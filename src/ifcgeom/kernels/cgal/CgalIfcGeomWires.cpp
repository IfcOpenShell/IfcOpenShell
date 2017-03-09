#include "CgalKernel.h"

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcPolyLoop* l, cgal_wire_t& result) {
  IfcSchema::IfcCartesianPoint::list::ptr points = l->Polygon();
  
  // Parse and store the points in a sequence
  cgal_wire_t polygon = std::vector<Kernel::Point_3>();
  for(IfcSchema::IfcCartesianPoint::list::it it = points->begin(); it != points->end(); ++ it) {
    cgal_point_t pnt;
    IfcGeom::CgalKernel::convert(*it, pnt);
    polygon.push_back(pnt);
  }
  
  // A loop should consist of at least three vertices
  std::size_t original_count = polygon.size();
  if (original_count < 3) {
    Logger::Message(Logger::LOG_ERROR, "Not enough edges for:", l->entity);
    return false;
  }
  
  // Remove points that are too close to one another
  remove_duplicate_points_from_loop(polygon, true);
  
  std::size_t count = polygon.size();
  if (original_count - count != 0) {
    std::stringstream ss; ss << (original_count - count) << " edges removed for:";
    Logger::Message(Logger::LOG_WARNING, ss.str(), l->entity);
  }
  
  if (count < 3) {
    Logger::Message(Logger::LOG_ERROR, "Not enough edges for:", l->entity);
    return false;
  }
  
  result = polygon;
  
  //  std::cout << "PolyLoop: " << std::endl;
  //  for (auto &point: polygon) {
  //    std::cout << "\tPoint(" << point << ")" << std::endl;
  //  }
  
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcPolyline* l, cgal_wire_t& result) {
  IfcSchema::IfcCartesianPoint::list::ptr points = l->Points();
  
  // Parse and store the points in a sequence
  cgal_wire_t polygon = std::vector<Kernel::Point_3>();
  for(IfcSchema::IfcCartesianPoint::list::it it = points->begin(); it != points->end(); ++ it) {
    cgal_point_t pnt;
    IfcGeom::CgalKernel::convert(*it, pnt);
    polygon.push_back(pnt);
  }
  
  // Remove points that are too close to one another
  remove_duplicate_points_from_loop(polygon, false);
  
  result = polygon;
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcEdgeLoop* l, cgal_wire_t& result) {
  IfcSchema::IfcOrientedEdge::list::ptr li = l->EdgeList();
  cgal_wire_t mw;
  for (IfcSchema::IfcOrientedEdge::list::it it = li->begin(); it != li->end(); ++it) {
    cgal_wire_t w;
    if (convert_wire(*it, w)) {
      // TODO: What to do here? Add some points only?
//      mw.Add(TopoDS::Edge(TopoDS_Iterator(w).Value()));
      return false;
    }
  }
  result = mw;
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcOrientedEdge* l, cgal_wire_t& result) {
  if (convert_wire(l->EdgeElement(), result)) {
    if (!l->Orientation()) {
      std::reverse(result.begin(),result.end());
    }
    return true;
  } else {
    return false;
  }
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcCompositeCurve* l, cgal_wire_t& wire) {
  if ( getValue(GV_PLANEANGLE_UNIT)<0 ) {
    Logger::Message(Logger::LOG_WARNING,"Creating a composite curve without unit information:",l->entity);
    
    // Temporarily pretend we do have unit information
    setValue(GV_PLANEANGLE_UNIT,1.0);
    
    bool succes_radians = false;
    bool succes_degrees = false;
    bool use_radians = false;
    bool use_degrees = false;
    
    // First try radians
    cgal_wire_t wire_radians, wire_degrees;
    try {
		    succes_radians = IfcGeom::CgalKernel::convert(l,wire_radians);
    } catch (...) {}
    
    // Now try degrees
    setValue(GV_PLANEANGLE_UNIT,0.0174532925199433);
    try {
		    succes_degrees = IfcGeom::CgalKernel::convert(l,wire_degrees);
    } catch (...) {}
    
    // Restore to unknown unit state
    setValue(GV_PLANEANGLE_UNIT,-1.0);
    
    if ( succes_degrees && ! succes_radians ) {
      use_degrees = true;
    } else if ( succes_radians && ! succes_degrees ) {
      use_radians = true;
    } else if ( succes_radians && succes_degrees ) {
      if ( wire_degrees.back() == wire_degrees.front() && wire_radians.back() != wire_radians.front() ) {
        use_degrees = true;
      } else if ( wire_radians.back() == wire_radians.front() && wire_degrees.back() != wire_degrees.front() ) {
        use_radians = true;
      } else {
        // No heuristic left to prefer the one over the other,
        // apparently both variants are equally succesful.
        // The curve might be composed of only straight segments.
        // Let's go with the wire created using radians as that
        // at least is a SI unit.
        use_radians = true;
      }
    }
    
    if ( use_radians ) {
      Logger::Message(Logger::LOG_NOTICE,"Used radians to create composite curve");
      wire = wire_radians;
    } else if ( use_degrees ) {
      Logger::Message(Logger::LOG_NOTICE,"Used degrees to create composite curve");
      wire = wire_degrees;
    }
    
    return use_radians || use_degrees;
  }
  IfcSchema::IfcCompositeCurveSegment::list::ptr segments = l->Segments();
  cgal_wire_t w;
  //TopoDS_Vertex last_vertex;
  for( IfcSchema::IfcCompositeCurveSegment::list::it it = segments->begin(); it != segments->end(); ++ it ) {
    IfcSchema::IfcCurve* curve = (*it)->ParentCurve();
    cgal_wire_t wire2;
    if ( !convert_wire(curve,wire2) ) {
      Logger::Message(Logger::LOG_ERROR,"Failed to convert curve:",curve->entity);
      continue;
    }
    if ( ! (*it)->SameSense() ) std::reverse(wire2.begin(),wire2.end());
    
    if (wire2.empty()) {
      continue;
    } else if (w.empty()) {
      w = wire2;
    } else if (w.back() == w.front()) {
      std::vector<Kernel::Point_3>::const_iterator vertex = wire2.begin();
      ++vertex;
      while (vertex != wire2.end()) {
        w.push_back(*vertex);
        ++vertex;
      }
    } else {
      for (auto &vertex: wire2) w.push_back(vertex);
    }
  }
  
  remove_duplicate_points_from_loop(w, false);
  
  wire = w;
  return true;
}
