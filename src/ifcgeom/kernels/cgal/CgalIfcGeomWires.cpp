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
  remove_duplicate_points_from_loop(polygon);
  
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
  remove_duplicate_points_from_loop(polygon);
  
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

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcEdge* l, cgal_wire_t& result) {
  if (!l->EdgeStart()->is(IfcSchema::Type::IfcVertexPoint) || !l->EdgeEnd()->is(IfcSchema::Type::IfcVertexPoint)) {
    Logger::Message(Logger::LOG_ERROR, "Only IfcVertexPoints are supported for EdgeStart and -End", l->entity);
    return false;
  }
  
  IfcSchema::IfcPoint* pnt1 = ((IfcSchema::IfcVertexPoint*) l->EdgeStart())->VertexGeometry();
  IfcSchema::IfcPoint* pnt2 = ((IfcSchema::IfcVertexPoint*) l->EdgeEnd())->VertexGeometry();
  if (!pnt1->is(IfcSchema::Type::IfcCartesianPoint) || !pnt2->is(IfcSchema::Type::IfcCartesianPoint)) {
    Logger::Message(Logger::LOG_ERROR, "Only IfcCartesianPoints are supported for VertexGeometry", l->entity);
    return false;
  }
  
  cgal_point_t p1, p2;
  if (!convert(((IfcSchema::IfcCartesianPoint*)pnt1), p1) ||
      !convert(((IfcSchema::IfcCartesianPoint*)pnt2), p2))
  {
    return false;
  }
  
  cgal_wire_t mw;
  mw.push_back(p1);
  mw.push_back(p2);
  
  result = mw;
  return true;
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
  
  remove_duplicate_points_from_loop(w);
  
  wire = w;
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcTrimmedCurve* l, cgal_wire_t& wire) {
  IfcSchema::IfcCurve* basis_curve = l->BasisCurve();
  bool isConic = basis_curve->is(IfcSchema::Type::IfcConic);
  double parameterFactor = isConic ? getValue(GV_PLANEANGLE_UNIT) : getValue(GV_LENGTH_UNIT);
  cgal_curve_t curve;
  if ( !convert_curve(basis_curve,curve) ) return false;
  bool trim_cartesian = l->MasterRepresentation() == IfcSchema::IfcTrimmingPreference::IfcTrimmingPreference_CARTESIAN;
  IfcEntityList::ptr trims1 = l->Trim1();
  IfcEntityList::ptr trims2 = l->Trim2();
  unsigned sense_agreement = l->SenseAgreement() ? 0 : 1;
  double flts[2];
  cgal_point_t pnts[2];
  bool has_flts[2] = {false,false};
  bool has_pnts[2] = {false,false};
  cgal_wire_t w;
  for ( IfcEntityList::it it = trims1->begin(); it != trims1->end(); it ++ ) {
    IfcUtil::IfcBaseClass* i = *it;
    if ( i->is(IfcSchema::Type::IfcCartesianPoint) ) {
      IfcGeom::CgalKernel::convert((IfcSchema::IfcCartesianPoint*)i, pnts[sense_agreement] );
      has_pnts[sense_agreement] = true;
    } else if ( i->is(IfcSchema::Type::IfcParameterValue) ) {
      const double value = *((IfcSchema::IfcParameterValue*)i);
      flts[sense_agreement] = value * parameterFactor;
      has_flts[sense_agreement] = true;
    }
  }
  for ( IfcEntityList::it it = trims2->begin(); it != trims2->end(); it ++ ) {
    IfcUtil::IfcBaseClass* i = *it;
    if ( i->is(IfcSchema::Type::IfcCartesianPoint) ) {
      IfcGeom::CgalKernel::convert((IfcSchema::IfcCartesianPoint*)i, pnts[1-sense_agreement] );
      has_pnts[1-sense_agreement] = true;
    } else if ( i->is(IfcSchema::Type::IfcParameterValue) ) {
      const double value = *((IfcSchema::IfcParameterValue*)i);
      flts[1-sense_agreement] = value * parameterFactor;
      has_flts[1-sense_agreement] = true;
    }
  }
  trim_cartesian &= has_pnts[0] && has_pnts[1];
  bool trim_cartesian_failed = !trim_cartesian;
  if ( trim_cartesian ) {
    // TODO: Project points to closest point in curve?
    if ( CGAL::squared_distance(pnts[0], pnts[1]) < getValue(GV_WIRE_CREATION_TOLERANCE)*getValue(GV_WIRE_CREATION_TOLERANCE) ) {
      Logger::Message(Logger::LOG_WARNING,"Skipping segment with length below tolerance level:",l->entity);
      return false;
    }
    if (l->SenseAgreement()) {
      bool found = false;
      int loops_to_go = 2;
      std::vector<Kernel::Point_3>::const_iterator point = curve.begin();
      do {
        if (!found) {
          if (CGAL::squared_distance(*point, pnts[0]) < getValue(GV_WIRE_CREATION_TOLERANCE)*getValue(GV_WIRE_CREATION_TOLERANCE)) {
            found = true;
            w.push_back(*point);
          }
        } else {
          w.push_back(*point);
          if (CGAL::squared_distance(*point, pnts[1]) < getValue(GV_WIRE_CREATION_TOLERANCE)*getValue(GV_WIRE_CREATION_TOLERANCE)) {
            break;
          }
        } ++point;
        if (point == curve.end()) {
          point = curve.begin();
          --loops_to_go;
        }
      } while (point != curve.begin() && loops_to_go > 0);
    } else {
      bool found = false;
      int loops_to_go = 2;
      std::vector<Kernel::Point_3>::const_reverse_iterator point = curve.rbegin();
      do {
        if (!found) {
          if (CGAL::squared_distance(*point, pnts[0]) < getValue(GV_WIRE_CREATION_TOLERANCE)*getValue(GV_WIRE_CREATION_TOLERANCE)) {
            found = true;
            w.push_back(*point);
          }
        } else {
          w.push_back(*point);
          if (CGAL::squared_distance(*point, pnts[1]) < getValue(GV_WIRE_CREATION_TOLERANCE)*getValue(GV_WIRE_CREATION_TOLERANCE)) {
            break;
          }
        } ++point;
        if (point == curve.rend() && loops_to_go > 0) point = curve.rbegin();
      } while (point != curve.rbegin());
    }
  }
  if ( (!trim_cartesian || trim_cartesian_failed) && (has_flts[0] && has_flts[1]) ) {
    // The Geom_Line is constructed from a gp_Pnt and gp_Dir, whereas the IfcLine
    // is defined by an IfcCartesianPoint and an IfcVector with Magnitude. Because
    // the vector is normalised when passed to Geom_Line constructor the magnitude
    // needs to be factored in with the IfcParameterValue here.
    if ( basis_curve->is(IfcSchema::Type::IfcLine) ) {
      IfcSchema::IfcLine* line = static_cast<IfcSchema::IfcLine*>(basis_curve);
      const double magnitude = line->Dir()->Magnitude();
      flts[0] *= magnitude; flts[1] *= magnitude;
    }
    if ( isConic && ALMOST_THE_SAME(fmod(flts[1]-flts[0],M_PI*2.),0.) ) {
      for (auto &point: curve) w.push_back(point);
    } else {
      const int segments_of_full_curve = 12;
      double segment_angle = 2.0*3.141592653589793/segments_of_full_curve;
      if ( basis_curve->is(IfcSchema::Type::IfcEllipse) ) {
        IfcSchema::IfcEllipse* ellipse = static_cast<IfcSchema::IfcEllipse*>(basis_curve);
        double x = ellipse->SemiAxis1() * getValue(GV_LENGTH_UNIT);
        double y = ellipse->SemiAxis2() * getValue(GV_LENGTH_UNIT);
        for (double current_angle = flts[0]; current_angle < flts[1]; current_angle += segment_angle) {
          w.push_back(Kernel::Point_3(x*cos(current_angle), y*sin(current_angle), 0));
        } w.push_back(Kernel::Point_3(x*cos(flts[1]), y*sin(flts[1]), 0));
      } if ( basis_curve->is(IfcSchema::Type::IfcCircle) ) {
        IfcSchema::IfcCircle* circle = static_cast<IfcSchema::IfcCircle*>(basis_curve);
        double r = circle->Radius() * getValue(GV_LENGTH_UNIT);
        for (double current_angle = flts[0]; current_angle < flts[1]; current_angle += segment_angle) {
          w.push_back(Kernel::Point_3(r*cos(current_angle), r*sin(current_angle), 0));
        } w.push_back(Kernel::Point_3(r*cos(flts[1]), r*sin(flts[1]), 0));
      }
    }
  } else if ( trim_cartesian_failed && (has_pnts[0] && has_pnts[1]) ) {
    w.push_back(pnts[0]);
    w.push_back(pnts[1]);
  }
  wire = w;
  return true;
}
