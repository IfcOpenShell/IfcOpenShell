#include "../../../ifcparse/IfcParse.h"

#include "CgalKernel.h"
#include "CgalConversionResult.h"

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcRepresentation* l, ConversionResults& shapes) {
	IfcSchema::IfcRepresentationItem::list::ptr items = l->Items();
	bool part_succes = false;
	if (items->size()) {
		for (IfcSchema::IfcRepresentationItem::list::it it = items->begin(); it != items->end(); ++it) {
			IfcSchema::IfcRepresentationItem* representation_item = *it;
			if (shape_type(representation_item) == ST_SHAPELIST) {
				part_succes |= convert_shapes(*it, shapes);
			} else {
				cgal_shape_t s;
				if (convert_shape(representation_item, s)) {
					shapes.push_back(ConversionResult(new CgalShape(s), get_style(representation_item)));
					part_succes |= true;
				}
			}
		}
	}
	return part_succes;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcCartesianPoint* l, cgal_point_t& point) {
  std::vector<double> xyz = l->Coordinates();
  if (xyz.size() < 4) {
    point = Kernel::Point_3(xyz.size()     ? (xyz[0]*getValue(GV_LENGTH_UNIT)) : 0.0f,
                            xyz.size() > 1 ? (xyz[1]*getValue(GV_LENGTH_UNIT)) : 0.0f,
                            xyz.size() > 2 ? (xyz[2]*getValue(GV_LENGTH_UNIT)) : 0.0f);
//    std::cout << "Converted Point(" << point << ")" << std::endl;
    return true;
  } else {
    std::cout << "Point(";
    for (auto &coordinate: xyz) std::cout << coordinate << " ";
    std::cout << ")";
    throw std::runtime_error("Could not parse point");
  }
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

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcAxis2Placement2D* l, cgal_placement_t& trsf) {
  //  IN_CACHE(IfcAxis2Placement3D,l,gp_Trsf,trsf)
  cgal_point_t o;
  cgal_direction_t axis = Kernel::Vector_3(0,0,1);
  cgal_direction_t refDirection = Kernel::Vector_3(1,0,0);
  IfcGeom::CgalKernel::convert(l->Location(),o);
  bool hasRef = l->hasRefDirection();
  if ( hasRef ) IfcGeom::CgalKernel::convert(l->RefDirection(),refDirection);
  
  // TODO: From Thomas' email. Should be checked.
  Kernel::Vector_3 y = CGAL::cross_product(Kernel::Vector_3(0.0, 0.0, 1.0), refDirection);
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
  
//  std::cout << "Ref direction: " << refDirection << std::endl;
//  std::cout << "Axis: " << axis << std::endl;
//  std::cout << "Origin: " << o << std::endl;
  
  // TODO: From Thomas' email. Should be checked.
  Kernel::Vector_3 y = CGAL::cross_product(axis, refDirection);
  trsf = Kernel::Aff_transformation_3(refDirection.cartesian(0), y.cartesian(0), axis.cartesian(0), o.cartesian(0),
                                      refDirection.cartesian(1), y.cartesian(1), axis.cartesian(1), o.cartesian(1),
                                      refDirection.cartesian(2), y.cartesian(2), axis.cartesian(2), o.cartesian(2));
  
//  for (int i = 0; i < 3; ++i) {
//    for (int j = 0; j < 4; ++j) {
//      std::cout << trsf.cartesian(i, j) << " ";
//    } std::cout << std::endl;
//  }
  
//  CACHE(IfcAxis2Placement3D,l,trsf)
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcObjectPlacement* l, cgal_placement_t& trsf) {
  // TODO: These macros don't work for the CGAL types. Need to check why.
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

bool IfcGeom::CgalKernel::convert_wire_to_face(const cgal_wire_t& wire, cgal_face_t& face) {
  face.outer = wire;
  return true;
}
