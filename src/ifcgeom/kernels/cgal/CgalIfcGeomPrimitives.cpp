#include "CgalKernel.h"

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcCartesianPoint* l, cgal_point_t& point) {
  std::vector<double> xyz = l->Coordinates();
  point = Kernel::Point_3(xyz.size()     ? (xyz[0]*getValue(GV_LENGTH_UNIT)) : 0.0f,
                          xyz.size() > 1 ? (xyz[1]*getValue(GV_LENGTH_UNIT)) : 0.0f,
                          xyz.size() > 2 ? (xyz[2]*getValue(GV_LENGTH_UNIT)) : 0.0f);
  //  std::cout << "Converted Point(" << point << ")" << std::endl;
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcDirection* l, cgal_direction_t& dir) {
  //  IN_CACHE(IfcDirection,l,cgal_direction_t,dir)
  std::vector<double> xyz = l->DirectionRatios();
  dir = Kernel::Vector_3(xyz.size()     ? xyz[0] : 0.0f,
                         xyz.size() > 1 ? xyz[1] : 0.0f,
                         xyz.size() > 2 ? xyz[2] : 0.0f);
  //  CACHE(IfcDirection,l,dir)
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcVector* l, cgal_vector_t& v) {
  //  IN_CACHE(IfcVector,l,cgal_vector_t,v)
  cgal_direction_t d;
  IfcGeom::CgalKernel::convert(l->Orientation(),d);
  v = l->Magnitude() * getValue(GV_LENGTH_UNIT) * d;
  //  CACHE(IfcVector,l,v)
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcPlane* pln, cgal_plane_t& plane) {
  //  IN_CACHE(IfcPlane,pln,gp_Pln,plane)
  IfcSchema::IfcAxis2Placement3D* l = pln->Position();
  cgal_point_t o;
  cgal_direction_t axis = Kernel::Vector_3(0,0,1);
  cgal_direction_t refDirection = Kernel::Vector_3(1,0,0);
  IfcGeom::CgalKernel::convert(l->Location(),o);
  bool hasRef = l->hasRefDirection();
  if ( l->hasAxis() ) IfcGeom::CgalKernel::convert(l->Axis(),axis);
  if ( hasRef ) IfcGeom::CgalKernel::convert(l->RefDirection(),refDirection);
  Kernel::Vector_3 y = CGAL::cross_product(axis, refDirection);
  Kernel::Vector_3 x = CGAL::cross_product(y, axis);
  
  cgal_plane_t ax3;
  if ( hasRef ) ax3 = Kernel::Plane_3(o,o+x,o+y);
  else ax3 = Kernel::Plane_3(o,axis);
  plane = ax3;
  
  //  std::cout << "IfcPlane C = " << o << std::endl;
  //  std::cout << "IfcPlane z (axis, exact) = " << axis << std::endl;
  //  std::cout << "IfcPlane x (refDirection, approximate) = " << refDirection << std::endl;
  //  std::cout << "IfcPlane y (computed, exact) = " << y << std::endl;
  //  std::cout << "IfcPlane x (computed, exact) = " << x << std::endl;
  //
  //  std::cout << "Plane_3 o = " << o << std::endl;
  //  std::cout << "Plane_3 o+x = " << o+x << std::endl;
  //  std::cout << "Plane_3 o+y = " << o+y << std::endl;
  
  // ax + by + cz + d = 0
  //  std::cout << "Plane: a = " << plane.a() << ", b = " << plane.b() << ", c = " << plane.c() << ", d = " << plane.d() << std::endl;
  
  //  std::ofstream fresult;
  //  fresult.open("/Users/ken/Desktop/plane.obj");
  //  // x = -5, y = -5, z = (5a +5b -d)/c
  //  fresult << "v -5 -5 " << (5.0*CGAL::to_double(plane.a())+5.0*CGAL::to_double(plane.b())-CGAL::to_double(plane.d()))/CGAL::to_double(plane.c()) << std::endl;
  //  // x = -5, y = +5, z = (5a -5b -d)/c
  //  fresult << "v -5 5 " << (5.0*CGAL::to_double(plane.a())-5.0*CGAL::to_double(plane.b())-CGAL::to_double(plane.d()))/CGAL::to_double(plane.c()) << std::endl;
  //  // x = 5, y = -5, z = (-5a +5b -d)/c
  //  fresult << "v 5 -5 " << (-5.0*CGAL::to_double(plane.a())+5.0*CGAL::to_double(plane.b())-CGAL::to_double(plane.d()))/CGAL::to_double(plane.c()) << std::endl;
  //  // x = 5, y = +5, z = (-5a -5b -d)/c
  //  fresult << "v 5 5 " << (-5.0*CGAL::to_double(plane.a())-5.0*CGAL::to_double(plane.b())-CGAL::to_double(plane.d()))/CGAL::to_double(plane.c()) << std::endl;
  //  fresult << "f 1 2 3" << std::endl;
  //  fresult << "f 4 3 2" << std::endl;
  //  fresult.close();
  
  //  CACHE(IfcPlane,pln,plane)
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcAxis2Placement2D* l, cgal_placement_t& trsf) {
  //  IN_CACHE(IfcAxis2Placement3D,l,gp_Trsf,trsf)
  cgal_point_t o;
  cgal_direction_t refDirection = Kernel::Vector_3(1,0,0);
  IfcGeom::CgalKernel::convert(l->Location(),o);
  bool hasRef = l->hasRefDirection();
  if ( hasRef ) IfcGeom::CgalKernel::convert(l->RefDirection(),refDirection);
  cgal_direction_t y = Kernel::Vector_3(-refDirection.y(), refDirection.x(), 0.0);
  
  // TODO: Should be checked.
  trsf = Kernel::Aff_transformation_3(refDirection.cartesian(0), y.cartesian(0), 0.0, o.cartesian(0),
                                      refDirection.cartesian(1), y.cartesian(1), 0.0, o.cartesian(1),
                                      0.0, 0.0, 1.0, 0.0);
  
  //  CACHE(IfcAxis2Placement3D,l,trsf)
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcAxis2Placement3D* l, cgal_placement_t& trsf) {
  //  IN_CACHE(IfcAxis2Placement3D,l,gp_Trsf,trsf)
  cgal_point_t o;
  cgal_direction_t axis = Kernel::Vector_3(0,0,1);
  cgal_direction_t refDirection = Kernel::Vector_3(1,0,0);
  IfcGeom::CgalKernel::convert(l->Location(),o);
  bool hasRef = l->hasRefDirection();
  if ( l->hasAxis() ) IfcGeom::CgalKernel::convert(l->Axis(),axis);
  if ( hasRef ) IfcGeom::CgalKernel::convert(l->RefDirection(),refDirection);
  Kernel::Vector_3 y = CGAL::cross_product(axis, refDirection);
  Kernel::Vector_3 x = CGAL::cross_product(y, axis);
  
  //  std::cout << "Ref direction: " << refDirection << std::endl;
  //  std::cout << "Axis: " << axis << std::endl;
  //  std::cout << "Origin: " << o << std::endl;
  
  // TODO: Should be checked.
  trsf = Kernel::Aff_transformation_3(x.cartesian(0), y.cartesian(0), axis.cartesian(0), o.cartesian(0),
                                      x.cartesian(1), y.cartesian(1), axis.cartesian(1), o.cartesian(1),
                                      x.cartesian(2), y.cartesian(2), axis.cartesian(2), o.cartesian(2));
  
  //  for (int i = 0; i < 3; ++i) {
  //    for (int j = 0; j < 4; ++j) {
  //      std::cout << trsf.cartesian(i, j) << " ";
  //    } std::cout << std::endl;
  //  }
  
  //  CACHE(IfcAxis2Placement3D,l,trsf)
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcObjectPlacement* l, cgal_placement_t& trsf) {
  //  IN_CACHE(IfcObjectPlacement,l,cgal_placement_t,trsf)
  if ( ! l->is(IfcSchema::Type::IfcLocalPlacement) ) {
    Logger::Message(Logger::LOG_ERROR, "Unsupported IfcObjectPlacement:", l->entity);
    return false;
  }
  
  //  std::cout << "initial trsf (identity?)" << std::endl;
  //  for (int i = 0; i < 3; ++i) {
  //    for (int j = 0; j < 4; ++j) {
  //      std::cout << trsf.cartesian(i, j) << " ";
  //    } std::cout << std::endl;
  //  }
  
  IfcSchema::IfcLocalPlacement* current = (IfcSchema::IfcLocalPlacement*)l;
  for (;;) {
    cgal_placement_t trsf2;
    
    IfcSchema::IfcAxis2Placement* relplacement = current->RelativePlacement();
    if ( relplacement->is(IfcSchema::Type::IfcAxis2Placement3D) ) {
      IfcGeom::CgalKernel::convert((IfcSchema::IfcAxis2Placement3D*)relplacement,trsf2);
      
      //      std::cout << "trsf2" << std::endl;
      //      for (int i = 0; i < 3; ++i) {
      //        for (int j = 0; j < 4; ++j) {
      //          std::cout << trsf2.cartesian(i, j) << " ";
      //        } std::cout << std::endl;
      //      }
      
      trsf = trsf * trsf2; // TODO: I think it's fine, but maybe should it be the other way around?
      
      //      std::cout << "trsf (after multiplication)" << std::endl;
      //      for (int i = 0; i < 3; ++i) {
      //        for (int j = 0; j < 4; ++j) {
      //          std::cout << trsf.cartesian(i, j) << " ";
      //        } std::cout << std::endl;
      //      }
    }
    if ( current->hasPlacementRelTo() ) {
      IfcSchema::IfcObjectPlacement* relto = current->PlacementRelTo();
      if ( relto->is(IfcSchema::Type::IfcLocalPlacement) )
        current = (IfcSchema::IfcLocalPlacement*)current->PlacementRelTo();
      else break;
    } else break;
  }
  //  CACHE(IfcObjectPlacement,l,trsf)
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcCartesianTransformationOperator2D* l, cgal_placement_t& trsf) {
  //  IN_CACHE(IfcCartesianTransformationOperator2D,l,cgal_placement_t,trsf)
  
  cgal_point_t origin;
  cgal_direction_t axis1 (1.,0.,0.);
  cgal_direction_t axis2 (0.,1.,0.);
  
  IfcGeom::CgalKernel::convert(l->LocalOrigin(),origin);
  if ( l->hasAxis1() ) IfcGeom::CgalKernel::convert(l->Axis1(),axis1);
  if ( l->hasAxis2() ) IfcGeom::CgalKernel::convert(l->Axis2(),axis2);
  double scale = 1.0;
  if (l->hasScale()) {
    scale = l->Scale();
  }
  
  // TODO: Untested
  trsf = Kernel::Aff_transformation_3(scale*axis1.cartesian(0), axis2.cartesian(0), 0.0, origin.cartesian(0),
                                      axis1.cartesian(1), scale*axis2.cartesian(1), 0.0, origin.cartesian(1),
                                      0.0, 0.0, 1.0, 0.0);
  
  //  CACHE(IfcCartesianTransformationOperator2D,l,trsf)
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcCartesianTransformationOperator2DnonUniform* l, cgal_placement_t& gtrsf) {
  //  IN_CACHE(IfcCartesianTransformationOperator2DnonUniform,l,cgal_placement_t,gtrsf)
  
  cgal_placement_t trsf;
  cgal_point_t origin;
  cgal_direction_t axis1 (1.,0.,0.);
  cgal_direction_t axis2 (0.,1.,0.);
  
  IfcGeom::CgalKernel::convert(l->LocalOrigin(),origin);
  if ( l->hasAxis1() ) IfcGeom::CgalKernel::convert(l->Axis1(),axis1);
  if ( l->hasAxis2() ) IfcGeom::CgalKernel::convert(l->Axis2(),axis2);
  
  const double scale1 = l->hasScale() ? l->Scale() : 1.0f;
  const double scale2 = l->hasScale2() ? l->Scale2() : scale1;
  
  // TODO: Untested
  trsf = Kernel::Aff_transformation_3(scale1*axis1.cartesian(0), axis2.cartesian(0), 0.0, origin.cartesian(0),
                                      axis1.cartesian(1), scale2*axis2.cartesian(1), 0.0, origin.cartesian(1),
                                      0.0, 0.0, 1.0, 0.0);
  
  //  CACHE(IfcCartesianTransformationOperator2DnonUniform,l,gtrsf)
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcCartesianTransformationOperator3D* l, cgal_placement_t& trsf) {
  //  IN_CACHE(IfcCartesianTransformationOperator3D,l,gp_Trsf,trsf)
  cgal_point_t origin;
  IfcGeom::CgalKernel::convert(l->LocalOrigin(),origin);
  cgal_direction_t axis1 (1.,0.,0.);
  cgal_direction_t axis2 (0.,1.,0.);
  cgal_direction_t axis3 (0.,0.,1.);
  if ( l->hasAxis1() ) IfcGeom::CgalKernel::convert(l->Axis1(),axis1);
  if ( l->hasAxis2() ) IfcGeom::CgalKernel::convert(l->Axis2(),axis2);
  if ( l->hasAxis3() ) IfcGeom::CgalKernel::convert(l->Axis3(),axis3);
  double scale = 1.0;
  if (l->hasScale()) {
    scale = l->Scale();
  }
  
  // TODO: Untested
  trsf = Kernel::Aff_transformation_3(scale*axis1.cartesian(0), axis2.cartesian(0), axis3.cartesian(0), origin.cartesian(0),
                                      axis1.cartesian(1), scale*axis2.cartesian(1), axis3.cartesian(1), origin.cartesian(1),
                                      axis1.cartesian(2), axis2.cartesian(2), scale*axis3.cartesian(2), origin.cartesian(2));
  
  //  std::cout << std::endl;
  //  for (int i = 0; i < 3; ++i) {
  //    for (int j = 0; j < 4; ++j) {
  //      std::cout << trsf.cartesian(i, j) << " ";
  //    } std::cout << std::endl;
  //  }
  
  //  CACHE(IfcCartesianTransformationOperator3D,l,trsf)
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcCartesianTransformationOperator3DnonUniform* l, cgal_placement_t& gtrsf) {
  //  IN_CACHE(IfcCartesianTransformationOperator3DnonUniform,l,gp_GTrsf,gtrsf)
  cgal_point_t origin;
  IfcGeom::CgalKernel::convert(l->LocalOrigin(),origin);
  cgal_direction_t axis1 (1.,0.,0.);
  cgal_direction_t axis2 (0.,1.,0.);
  cgal_direction_t axis3 (0.,0.,1.);
  if ( l->hasAxis1() ) IfcGeom::CgalKernel::convert(l->Axis1(),axis1);
  if ( l->hasAxis2() ) IfcGeom::CgalKernel::convert(l->Axis2(),axis2);
  if ( l->hasAxis3() ) IfcGeom::CgalKernel::convert(l->Axis3(),axis3);
  const double scale1 = l->hasScale() ? l->Scale() : 1.0f;
  const double scale2 = l->hasScale2() ? l->Scale2() : scale1;
  const double scale3 = l->hasScale3() ? l->Scale3() : scale1;
  
  // TODO: Untested
  gtrsf = Kernel::Aff_transformation_3(scale1*axis1.cartesian(0), axis2.cartesian(0), axis3.cartesian(0), origin.cartesian(0),
                                       axis1.cartesian(1), scale2*axis2.cartesian(1), axis3.cartesian(1), origin.cartesian(1),
                                       axis1.cartesian(2), axis2.cartesian(2), scale3*axis3.cartesian(2), origin.cartesian(2));
  
  //  for (int i = 0; i < 3; ++i) {
  //    for (int j = 0; j < 4; ++j) {
  //      std::cout << gtrsf.cartesian(i, j) << " ";
  //    } std::cout << std::endl;
  //  }
  
  //  CACHE(IfcCartesianTransformationOperator3DnonUniform,l,gtrsf)
  return true;
}
