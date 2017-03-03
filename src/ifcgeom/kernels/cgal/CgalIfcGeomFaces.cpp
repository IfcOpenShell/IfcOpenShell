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
  if (has_position) {
    IfcGeom::CgalKernel::convert(l->Position(), trsf2d);
  }
  
  face = cgal_face_t();
  face.outer.push_back(Kernel::Point_3(-x, -y, 0.0));
  face.outer.push_back(Kernel::Point_3( x, -y, 0.0));
  face.outer.push_back(Kernel::Point_3( x,  y, 0.0));
  face.outer.push_back(Kernel::Point_3(-x,  y, 0.0));
  
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
