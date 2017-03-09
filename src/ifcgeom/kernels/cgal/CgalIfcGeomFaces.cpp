#include "CgalKernel.h"

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcArbitraryClosedProfileDef* l, cgal_face_t& face) {
  cgal_wire_t wire;
  if ( ! convert_wire(l->OuterCurve(),wire) ) return false;
  
  cgal_face_t f;
  bool success = convert_wire_to_face(wire, f);
  if (success) face = f;
  return success;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcRectangleProfileDef* l, cgal_face_t& face) {
  const double x = l->XDim() / 2.0f * getValue(GV_LENGTH_UNIT);
  const double y = l->YDim() / 2.0f * getValue(GV_LENGTH_UNIT);
  
  if ( x < ALMOST_ZERO || y < ALMOST_ZERO ) {
    Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
    return false;
  }
  
  cgal_placement_t trsf2d;
  bool has_position = true;
#ifdef USE_IFC4
  has_position = l->hasPosition();
#endif
  
  face = cgal_face_t();
  face.outer.push_back(Kernel::Point_3(-x, -y, 0.0));
  face.outer.push_back(Kernel::Point_3( x, -y, 0.0));
  face.outer.push_back(Kernel::Point_3( x,  y, 0.0));
  face.outer.push_back(Kernel::Point_3(-x,  y, 0.0));
  
  if (has_position) {
    IfcGeom::CgalKernel::convert(l->Position(), trsf2d);
    for (auto &vertex: face.outer) {
      vertex = vertex.transform(trsf2d);
    }
  }
  
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcRoundedRectangleProfileDef* l, cgal_face_t& face) {
  const double x = l->XDim() / 2.0f * getValue(GV_LENGTH_UNIT);
  const double y = l->YDim() / 2.0f  * getValue(GV_LENGTH_UNIT);
  const double r = l->RoundingRadius() * getValue(GV_LENGTH_UNIT);
  
  if ( x < ALMOST_ZERO || y < ALMOST_ZERO || r < ALMOST_ZERO ) {
    Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
    return false;
  }
  
  cgal_placement_t trsf2d;
  bool has_position = true;
#ifdef USE_IFC4
  has_position = l->hasPosition();
#endif
  
  const int segments = 3;
  
  if (r == 0.0) {
    face = cgal_face_t();
    face.outer.push_back(Kernel::Point_3(-x, -y, 0.0));
    face.outer.push_back(Kernel::Point_3( x, -y, 0.0));
    face.outer.push_back(Kernel::Point_3( x,  y, 0.0));
    face.outer.push_back(Kernel::Point_3(-x,  y, 0.0));
  }
  
  else {
    face = cgal_face_t();
    for (int current_segment = 0; current_segment <= segments; ++current_segment) {
      double current_angle = current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(x-r+r*cos(current_angle), y-r+r*sin(current_angle), 0));
    }
    for (int current_segment = 0; current_segment <= segments; ++current_segment) {
      double current_angle = 0.5*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(-x+r+r*cos(current_angle), y-r+r*sin(current_angle), 0));
    }
    for (int current_segment = 0; current_segment <= segments; ++current_segment) {
      double current_angle = 1.0*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(-x+r+r*cos(current_angle), -y+r+r*sin(current_angle), 0));
    }
    for (int current_segment = 0; current_segment <= segments; ++current_segment) {
      double current_angle = 1.5*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(x-r+r*cos(current_angle), -y+r+r*sin(current_angle), 0));
    }
  }
  
  if (has_position) {
    IfcGeom::CgalKernel::convert(l->Position(), trsf2d);
    for (auto &vertex: face.outer) {
      vertex = vertex.transform(trsf2d);
    }
  }
  
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcRectangleHollowProfileDef* l, cgal_face_t& face) {
  const double x = l->XDim() / 2.0f * getValue(GV_LENGTH_UNIT);
  const double y = l->YDim() / 2.0f  * getValue(GV_LENGTH_UNIT);
  const double d = l->WallThickness() * getValue(GV_LENGTH_UNIT);
  
  const bool fr1 = l->hasOuterFilletRadius();
  const bool fr2 = l->hasInnerFilletRadius();
  
  const double r1 = fr1 ? l->OuterFilletRadius() * getValue(GV_LENGTH_UNIT) : 0.;
  const double r2 = fr2 ? l->InnerFilletRadius() * getValue(GV_LENGTH_UNIT) : 0.;
  
  if ( x < ALMOST_ZERO || y < ALMOST_ZERO ) {
    Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
    return false;
  }
  
  cgal_placement_t trsf2d;
  bool has_position = true;
#ifdef USE_IFC4
  has_position = l->hasPosition();
#endif
  
  const int segments = 3;
  
  if (!fr1 || r1 == 0.0) {
    face = cgal_face_t();
    face.outer.push_back(Kernel::Point_3(-x, -y, 0.0));
    face.outer.push_back(Kernel::Point_3( x, -y, 0.0));
    face.outer.push_back(Kernel::Point_3( x,  y, 0.0));
    face.outer.push_back(Kernel::Point_3(-x,  y, 0.0));
  }
  
  else {
    face = cgal_face_t();
    for (int current_segment = 0; current_segment <= segments; ++current_segment) {
      double current_angle = current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(x-r1+r1*cos(current_angle), y-r1+r1*sin(current_angle), 0));
    }
    for (int current_segment = 0; current_segment <= segments; ++current_segment) {
      double current_angle = 0.5*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(-x+r1+r1*cos(current_angle), y-r1+r1*sin(current_angle), 0));
    }
    for (int current_segment = 0; current_segment <= segments; ++current_segment) {
      double current_angle = 1.0*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(-x+r1+r1*cos(current_angle), -y+r1+r1*sin(current_angle), 0));
    }
    for (int current_segment = 0; current_segment <= segments; ++current_segment) {
      double current_angle = 1.5*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(x-r1+r1*cos(current_angle), -y+r1+r1*sin(current_angle), 0));
    }
  }
  
  if (!fr2 || r2 == 0.0) {
    face.inner.push_back(cgal_wire_t());
    face.inner.back().push_back(Kernel::Point_3(-x+d, -y+d, 0.0));
    face.inner.back().push_back(Kernel::Point_3( x-d, -y+d, 0.0));
    face.inner.back().push_back(Kernel::Point_3( x-d,  y-d, 0.0));
    face.inner.back().push_back(Kernel::Point_3(-x+d,  y-d, 0.0));
  }
  
  else {
    face.inner.push_back(cgal_wire_t());
    for (int current_segment = 0; current_segment <= segments; ++current_segment) {
      double current_angle = current_segment*0.5*3.141592653589793/((double)segments);
      face.inner.back().push_back(Kernel::Point_3(x-d-r1+r1*cos(current_angle), y-d-r1+r1*sin(current_angle), 0));
    }
    for (int current_segment = 0; current_segment <= segments; ++current_segment) {
      double current_angle = 0.5*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.inner.back().push_back(Kernel::Point_3(-x+d+r1+r1*cos(current_angle), y-d-r1+r1*sin(current_angle), 0));
    }
    for (int current_segment = 0; current_segment <= segments; ++current_segment) {
      double current_angle = 1.0*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.inner.back().push_back(Kernel::Point_3(-x+d+r1+r1*cos(current_angle), -y+d+r1+r1*sin(current_angle), 0));
    }
    for (int current_segment = 0; current_segment <= segments; ++current_segment) {
      double current_angle = 1.5*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.inner.back().push_back(Kernel::Point_3(x-d-r1+r1*cos(current_angle), -y+d+r1+r1*sin(current_angle), 0));
    }
  }
  
  if (has_position) {
    IfcGeom::CgalKernel::convert(l->Position(), trsf2d);
    for (auto &vertex: face.outer) {
      vertex = vertex.transform(trsf2d);
    } for (auto &inner: face.inner) {
      for (auto &vertex: inner) {
        vertex = vertex.transform(trsf2d);
      }
    }
  }
  
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcTrapeziumProfileDef* l, cgal_face_t& face) {
  const double x1 = l->BottomXDim() / 2.0f * getValue(GV_LENGTH_UNIT);
  const double w = l->TopXDim() * getValue(GV_LENGTH_UNIT);
  const double dx = l->TopXOffset() * getValue(GV_LENGTH_UNIT);
  const double y = l->YDim() / 2.0f  * getValue(GV_LENGTH_UNIT);
  
  if ( x1 < ALMOST_ZERO || w < ALMOST_ZERO || y < ALMOST_ZERO ) {
    Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
    return false;
  }
  
  cgal_placement_t trsf2d;
  bool has_position = true;
#ifdef USE_IFC4
  has_position = l->hasPosition();
#endif
  
  face = cgal_face_t();
  face.outer.push_back(Kernel::Point_3(-x1, -y, 0.0));
  face.outer.push_back(Kernel::Point_3(x1, -y, 0.0));
  face.outer.push_back(Kernel::Point_3(dx+w-x1, y, 0.0));
  face.outer.push_back(Kernel::Point_3(dx-x1, y, 0.0));
  
  if (has_position) {
    IfcGeom::CgalKernel::convert(l->Position(), trsf2d);
    for (auto &vertex: face.outer) {
      vertex = vertex.transform(trsf2d);
    }
  }
  
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcCircleProfileDef* l, cgal_face_t& face) {
  const double r = l->Radius() * getValue(GV_LENGTH_UNIT);
  if ( r == 0.0f ) {
    Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
    return false;
  }
  
  cgal_placement_t trsf2d;
  bool has_position = true;
#ifdef USE_IFC4
  has_position = l->hasPosition();
#endif
  
  const int segments = 12;
  
  face = cgal_face_t();
  for (int current_segment = 0; current_segment < segments; ++current_segment) {
    double current_angle = current_segment*2.0*3.141592653589793/((double)segments);
    face.outer.push_back(Kernel::Point_3(r*cos(current_angle), r*sin(current_angle), 0));
  }
  
  if (has_position) {
    IfcGeom::CgalKernel::convert(l->Position(), trsf2d);
    for (auto &vertex: face.outer) {
      vertex = vertex.transform(trsf2d);
    }
  }

  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcCircleHollowProfileDef* l, cgal_face_t& face) {
  const double r = l->Radius() * getValue(GV_LENGTH_UNIT);
  const double t = l->WallThickness() * getValue(GV_LENGTH_UNIT);
  
  if ( r == 0.0f || t == 0.0f ) {
    Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
    return false;
  }
  
  cgal_placement_t trsf2d;
  bool has_position = true;
#ifdef USE_IFC4
  has_position = l->hasPosition();
#endif
  
  const int segments = 12;
  
  face = cgal_face_t();
  for (int current_segment = 0; current_segment < segments; ++current_segment) {
    double current_angle = current_segment*2.0*3.141592653589793/((double)segments);
    face.outer.push_back(Kernel::Point_3(r*cos(current_angle), r*sin(current_angle), 0));
  }
  
  face.inner.push_back(cgal_wire_t());
  for (int current_segment = 0; current_segment < segments; ++current_segment) {
    double current_angle = current_segment*2.0*3.141592653589793/((double)segments);
    face.inner.back().push_back(Kernel::Point_3((r-t)*cos(current_angle), (r-t)*sin(current_angle), 0));
  }
  
  if (has_position) {
    IfcGeom::CgalKernel::convert(l->Position(), trsf2d);
    for (auto &vertex: face.outer) {
      vertex = vertex.transform(trsf2d);
    } for (auto &inner: face.inner) {
      for (auto &vertex: inner) {
        vertex = vertex.transform(trsf2d);
      }
    }
  }
  
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcEllipseProfileDef* l, cgal_face_t& face) {
  double rx = l->SemiAxis1() * getValue(GV_LENGTH_UNIT);
  double ry = l->SemiAxis2() * getValue(GV_LENGTH_UNIT);
  
  if ( rx < ALMOST_ZERO || ry < ALMOST_ZERO ) {
    Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
    return false;
  }
  
  cgal_placement_t trsf2d;
  bool has_position = true;
#ifdef USE_IFC4
  has_position = l->hasPosition();
#endif
  
  const int segments = 12;
  
  face = cgal_face_t();
  for (int current_segment = 0; current_segment < segments; ++current_segment) {
    double current_angle = current_segment*2.0*3.141592653589793/((double)segments);
    face.outer.push_back(Kernel::Point_3(rx*cos(current_angle), ry*sin(current_angle), 0));
  }
  
  if (has_position) {
    IfcGeom::CgalKernel::convert(l->Position(), trsf2d);
    for (auto &vertex: face.outer) {
      vertex = vertex.transform(trsf2d);
    }
  }
  
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcFace* l, cgal_face_t& face) {
  IfcSchema::IfcFaceBound::list::ptr bounds = l->Bounds();
  
  int num_outer_bounds = 0;
  
  for (IfcSchema::IfcFaceBound::list::it it = bounds->begin(); it != bounds->end(); ++it) {
    IfcSchema::IfcFaceBound* bound = *it;
    if (bound->is(IfcSchema::Type::IfcFaceOuterBound)) num_outer_bounds ++;
  }
  
  if (num_outer_bounds != 1) {
    Logger::Message(Logger::LOG_ERROR, "Invalid configuration of boundaries for:", l->entity);
    return false;
  }
  
  cgal_face_t mf;
  
  for (IfcSchema::IfcFaceBound::list::it it = bounds->begin(); it != bounds->end(); ++it) {
    IfcSchema::IfcFaceBound* bound = *it;
    IfcSchema::IfcLoop* loop = bound->Bound();
    
    const bool is_interior = !bound->is(IfcSchema::Type::IfcFaceOuterBound);
    
    cgal_wire_t wire;
    if (!convert_wire(loop, wire)) {
      Logger::Message(Logger::LOG_ERROR, "Failed to process face boundary loop", loop->entity);
      return false;
    }
    
    if (!is_interior) {
      mf.outer = wire;
    } else {
      mf.inner.push_back(wire);
    }
  }
  
  face = mf;
  
  //  std::cout << "Face: " << std::endl;
  //  for (auto &point: face.outer) {
  //    std::cout << "\tPoint(" << point << ")" << std::endl;
  //  }
  
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcCShapeProfileDef* l, cgal_face_t& face) {
  const double y = l->Depth() / 2.0f * getValue(GV_LENGTH_UNIT);
  const double x = l->Width() / 2.0f * getValue(GV_LENGTH_UNIT);
  const double d1 = l->WallThickness() * getValue(GV_LENGTH_UNIT);
  const double d2 = l->Girth() * getValue(GV_LENGTH_UNIT);
  bool doFillet = l->hasInternalFilletRadius();
  double f1 = 0;
  double f2 = 0;
  if ( doFillet ) {
    f1 = l->InternalFilletRadius() * getValue(GV_LENGTH_UNIT);
    f2 = f1 + d1;
  }
  
  if ( x < ALMOST_ZERO || y < ALMOST_ZERO || d1 < ALMOST_ZERO || d2 < ALMOST_ZERO ) {
    Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
    return false;
  }
  
  cgal_placement_t trsf2d;
  bool has_position = true;
#ifdef USE_IFC4
  has_position = l->hasPosition();
#endif
  
  const int segments = 3;
  
  if (!doFillet || f1 == 0.0) {
    face = cgal_face_t();
    face.outer.push_back(Kernel::Point_3(-x, -y, 0.0));
    face.outer.push_back(Kernel::Point_3(x, -y, 0.0));
    face.outer.push_back(Kernel::Point_3(x, -y+d2, 0.0));
    face.outer.push_back(Kernel::Point_3(x-d1, -y+d2, 0.0));
    face.outer.push_back(Kernel::Point_3(x-d1, -y+d1, 0.0));
    face.outer.push_back(Kernel::Point_3(-x+d1, -y+d1, 0.0));
    face.outer.push_back(Kernel::Point_3(-x+d1, y-d1, 0.0));
    face.outer.push_back(Kernel::Point_3(x-d1, y-d1, 0.0));
    face.outer.push_back(Kernel::Point_3(x-d1, y-d2, 0.0));
    face.outer.push_back(Kernel::Point_3(x, y-d2, 0.0));
    face.outer.push_back(Kernel::Point_3(x, y, 0.0));
    face.outer.push_back(Kernel::Point_3(-x, y, 0.0));
  }
  
  else {
    face = cgal_face_t();
    for (int current_segment = 0; current_segment <= segments; ++current_segment) {
      double current_angle = 1.0*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(-x+f2+f2*cos(current_angle), -y+f2+f2*sin(current_angle), 0));
    }
    for (int current_segment = 0; current_segment <= segments; ++current_segment) {
      double current_angle = 1.5*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(x-f2+f2*cos(current_angle), -y+f2+f2*sin(current_angle), 0));
    }
    face.outer.push_back(Kernel::Point_3(x, -y+d2, 0.0));
    face.outer.push_back(Kernel::Point_3(x-d1, -y+d2, 0.0));
    for (int current_segment = segments; current_segment >= 0; --current_segment) {
      double current_angle = 1.5*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(x-f2+f1*cos(current_angle), -y+f2+f1*sin(current_angle), 0));
    }
    for (int current_segment = segments; current_segment >= 0; --current_segment) {
      double current_angle = 1.0*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(-x+f2+f1*cos(current_angle), -y+f2+f1*sin(current_angle), 0));
    }
    for (int current_segment = segments; current_segment >= 0; --current_segment) {
      double current_angle = 0.5*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(-x+f2+f1*cos(current_angle), y-f2+f1*sin(current_angle), 0));
    }
    for (int current_segment = segments; current_segment >= 0; --current_segment) {
      double current_angle = current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(x-f2+f1*cos(current_angle), y-f2+f1*sin(current_angle), 0));
    }
    face.outer.push_back(Kernel::Point_3(x-d1, y-d2, 0.0));
    face.outer.push_back(Kernel::Point_3(x, y-d2, 0.0));
    for (int current_segment = 0; current_segment <= segments; ++current_segment) {
      double current_angle = current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(x-f2+f2*cos(current_angle), y-f2+f2*sin(current_angle), 0));
    }
    for (int current_segment = 0; current_segment <= segments; ++current_segment) {
      double current_angle = 0.5*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(-x+f2+f2*cos(current_angle), y-f2+f2*sin(current_angle), 0));
    }
  }
  
  if (has_position) {
    IfcGeom::CgalKernel::convert(l->Position(), trsf2d);
    for (auto &vertex: face.outer) {
      vertex = vertex.transform(trsf2d);
    }
  }
  
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcLShapeProfileDef* l, cgal_face_t& face) {
  const bool hasSlope = l->hasLegSlope();
  const bool doEdgeFillet = l->hasEdgeRadius();
  const bool doFillet = l->hasFilletRadius();
  
  const double y = l->Depth() / 2.0f * getValue(GV_LENGTH_UNIT);
  const double x = (l->hasWidth() ? l->Width() : l->Depth()) / 2.0f * getValue(GV_LENGTH_UNIT);
  const double d = l->Thickness() * getValue(GV_LENGTH_UNIT);
  const double slope = hasSlope ? (l->LegSlope() * getValue(GV_PLANEANGLE_UNIT)) : 0.;
  
  double f1 = 0.0f;
  double f2 = 0.0f;
  if (doFillet) {
    f1 = l->FilletRadius() * getValue(GV_LENGTH_UNIT);
  }
  if ( doEdgeFillet) {
    f2 = l->EdgeRadius() * getValue(GV_LENGTH_UNIT);
  }
  
  if ( x < ALMOST_ZERO || y < ALMOST_ZERO || d < ALMOST_ZERO ) {
    Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
    return false;
  }
  
  double xx = -x+d;
  double xy = -y+d;
  double dy1 = 0.;
  double dy2 = 0.;
  double dx1 = 0.;
  double dx2 = 0.;
  if (hasSlope) {
    dy1 = tan(slope) * x;
    dy2 = tan(slope) * (x - d);
    dx1 = tan(slope) * y;
    dx2 = tan(slope) * (y - d);
    
    const double x1s = x; const double y1s = -y + d - dy1;
    const double x1e = -x + d; const double y1e = -y + d + dy2;
    const double x2s = -x + d - dx1; const double y2s = y;
    const double x2e = -x + d + dx2; const double y2e = -y + d;
    
    const double a1 = y1e - y1s;
    const double b1 = x1s - x1e;
    const double c1 = a1*x1s + b1*y1s;
    
    const double a2 = y2e - y2s;
    const double b2 = x2s - x2e;
    const double c2 = a2*x2s + b2*y2s;
    
    const double det = a1*b2 - a2*b1;
    
    if (ALMOST_THE_SAME(det, 0.)) {
      Logger::Message(Logger::LOG_NOTICE, "Legs do not intersect for:",l->entity);
      return false;
    }
    
    xx = (b2*c1 - b1*c2) / det;
    xy = (a1*c2 - a2*c1) / det;
  }
  
  cgal_placement_t trsf2d;
  bool has_position = true;
#ifdef USE_IFC4
  has_position = l->hasPosition();
#endif
  
  const int segments = 3;
  
  face = cgal_face_t();
  face.outer.push_back(Kernel::Point_3(-x, -y, 0.0));
  face.outer.push_back(Kernel::Point_3(x, -y, 0.0));
  if (f2 == 0.0) {
    face.outer.push_back(Kernel::Point_3(x, -y+d-dy1, 0.0));
  } else {
    for (int current_segment = 0; current_segment <= segments; ++current_segment) {
      double current_angle = current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(x-f2+f2*cos(current_angle), -y+d-dy1-f2+f2*sin(current_angle), 0));
    }
  } if (f1 == 0.0) {
    face.outer.push_back(Kernel::Point_3(xx, xy, 0.0));
  } else {
    for (int current_segment = segments; current_segment >= 0; --current_segment) {
      double current_angle = 1.0*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(xx+f1+f1*cos(current_angle), xy+f1+f1*sin(current_angle), 0));
    }
  } if (f2 == 0.0) {
    face.outer.push_back(Kernel::Point_3(-x+d-dx1, y, 0.0));
  } else {
    for (int current_segment = 0; current_segment <= segments; ++current_segment) {
      double current_angle = current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(-x+d-dx1-f2+f2*cos(current_angle), y-f2+f2*sin(current_angle), 0));
    }
  } face.outer.push_back(Kernel::Point_3(-x, y, 0.0));
  
  if (has_position) {
    IfcGeom::CgalKernel::convert(l->Position(), trsf2d);
    for (auto &vertex: face.outer) {
      vertex = vertex.transform(trsf2d);
    }
  }
  
  return true;
}

// TODO: Untested
bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcIShapeProfileDef* l, cgal_face_t& face) {
  const double x1 = l->OverallWidth() / 2.0f * getValue(GV_LENGTH_UNIT);
  const double y = l->OverallDepth() / 2.0f * getValue(GV_LENGTH_UNIT);
  const double d1 = l->WebThickness() / 2.0f  * getValue(GV_LENGTH_UNIT);
  const double dy1 = l->FlangeThickness() * getValue(GV_LENGTH_UNIT);
  
  bool doFillet1 = l->hasFilletRadius();
  double f1 = 0.;
  if ( doFillet1 ) {
    f1 = l->FilletRadius() * getValue(GV_LENGTH_UNIT);
  }
  
  bool doFillet2 = doFillet1;
  double x2 = x1, dy2 = dy1, f2 = f1;
  
  if (l->is(IfcSchema::Type::IfcAsymmetricIShapeProfileDef)) {
    IfcSchema::IfcAsymmetricIShapeProfileDef* assym = (IfcSchema::IfcAsymmetricIShapeProfileDef*) l;
    x2 = assym->TopFlangeWidth() / 2. * getValue(GV_LENGTH_UNIT);
    doFillet2 = assym->hasTopFlangeFilletRadius();
    if (doFillet2) {
      f2 = assym->TopFlangeFilletRadius() * getValue(GV_LENGTH_UNIT);
    }
    if (assym->hasTopFlangeThickness()) {
      dy2 = assym->TopFlangeThickness() * getValue(GV_LENGTH_UNIT);
    }
  }
  
  if ( x1 < ALMOST_ZERO || x2 < ALMOST_ZERO || y < ALMOST_ZERO || d1 < ALMOST_ZERO || dy1 < ALMOST_ZERO || dy2 < ALMOST_ZERO ) {
    Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
    return false;
  }
  
  cgal_placement_t trsf2d;
  bool has_position = true;
#ifdef USE_IFC4
  has_position = l->hasPosition();
#endif
  
  const int segments = 3;
  
  face = cgal_face_t();
  face.outer.push_back(Kernel::Point_3(-x1, -y, 0.0));
  face.outer.push_back(Kernel::Point_3(x1, -y, 0.0));
  face.outer.push_back(Kernel::Point_3(x1, -y+dy1, 0.0));
  if (f1 == 0.0) {
    face.outer.push_back(Kernel::Point_3(d1, -y+dy1, 0.0));
    face.outer.push_back(Kernel::Point_3(d1, y-dy2, 0.0));
  } else {
    for (int current_segment = segments; current_segment >= 0; --current_segment) {
      double current_angle = 1.0*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(d1+f1+f1*cos(current_angle), -y+dy1+f1+f1*sin(current_angle), 0));
    } for (int current_segment = segments; current_segment >= 0; --current_segment) {
      double current_angle = 0.5*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(d1+f1+f1*cos(current_angle), y-dy2-f1+f1*sin(current_angle), 0));
    }
  } face.outer.push_back(Kernel::Point_3(x2, y-dy2, 0.0));
  face.outer.push_back(Kernel::Point_3(x2, y, 0.0));
  face.outer.push_back(Kernel::Point_3(-x2, y, 0.0));
  face.outer.push_back(Kernel::Point_3(-x2, y-dy2, 0.0));
  if (f2 == 0.0) {
    face.outer.push_back(Kernel::Point_3(-d1, y-dy2, 0.0));
    face.outer.push_back(Kernel::Point_3(-d1, -y+dy1, 0.0));
  } else {
    for (int current_segment = segments; current_segment >= 0; --current_segment) {
      double current_angle = current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(-d1-f2+f2*cos(current_angle), y-dy2-f2+f2*sin(current_angle), 0));
    } for (int current_segment = segments; current_segment >= 0; --current_segment) {
      double current_angle = 1.5*3.141592653589793+current_segment*0.5*3.141592653589793/((double)segments);
      face.outer.push_back(Kernel::Point_3(-d1-f2+f2*cos(current_angle), -y+dy1+f2+f2*sin(current_angle), 0));
    }
  } face.outer.push_back(Kernel::Point_3(-x1, -y+dy1, 0.0));
  
  if (has_position) {
    IfcGeom::CgalKernel::convert(l->Position(), trsf2d);
    for (auto &vertex: face.outer) {
      vertex = vertex.transform(trsf2d);
    }
  }
  
  return true;
}
