#include "CgalKernel.h"

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcCircle* l, cgal_curve_t& curve) {
  const double r = l->Radius() * getValue(GV_LENGTH_UNIT);
  if ( r < ALMOST_ZERO ) {
    Logger::Message(Logger::LOG_ERROR, "Radius not greater than zero for:", l->entity);
    return false;
  }
  cgal_placement_t trsf;
  IfcSchema::IfcAxis2Placement* placement = l->Position();
  if (placement->is(IfcSchema::Type::IfcAxis2Placement3D)) {
    IfcGeom::CgalKernel::convert((IfcSchema::IfcAxis2Placement3D*)placement,trsf);
  } else {
    cgal_placement_t trsf2d;
    IfcGeom::CgalKernel::convert((IfcSchema::IfcAxis2Placement2D*)placement,trsf2d);
    trsf = trsf2d;
  }
  
  const int segments = 12;
  
  curve = cgal_curve_t();
  for (int current_segment = 0; current_segment < segments; ++current_segment) {
    double current_angle = current_segment*2.0*3.141592653589793/((double)segments);
    curve.push_back(Kernel::Point_3(r*cos(current_angle), r*sin(current_angle), 0));
  }
  
  for (auto &vertex: curve) {
    vertex = vertex.transform(trsf);
  }
  
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcEllipse* l, cgal_curve_t& curve) {
  double x = l->SemiAxis1() * getValue(GV_LENGTH_UNIT);
  double y = l->SemiAxis2() * getValue(GV_LENGTH_UNIT);
  if (x < ALMOST_ZERO || y < ALMOST_ZERO) {
    Logger::Message(Logger::LOG_ERROR, "Radius not greater than zero for:", l->entity);
    return false;
  }
  cgal_placement_t trsf;
  IfcSchema::IfcAxis2Placement* placement = l->Position();
  if (placement->is(IfcSchema::Type::IfcAxis2Placement3D)) {
    convert((IfcSchema::IfcAxis2Placement3D*)placement,trsf);
  } else {
    cgal_placement_t trsf2d;
    convert((IfcSchema::IfcAxis2Placement2D*)placement,trsf2d);
    trsf = trsf2d;
  }
  
  const int segments = 12;
  
  curve = cgal_curve_t();
  for (int current_segment = 0; current_segment < segments; ++current_segment) {
    double current_angle = current_segment*2.0*3.141592653589793/((double)segments);
    curve.push_back(Kernel::Point_3(x*cos(current_angle), y*sin(current_angle), 0));
  }
  
  for (auto &vertex: curve) {
    vertex = vertex.transform(trsf);
  }
  
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcLine* l, cgal_curve_t& curve) {
  cgal_point_t pnt;
  cgal_direction_t vec;
  convert(l->Pnt(),pnt);
  convert(l->Dir(),vec);
  curve = cgal_curve_t();
  curve.push_back(pnt);
  curve.push_back(pnt+vec);
  return true;
}
