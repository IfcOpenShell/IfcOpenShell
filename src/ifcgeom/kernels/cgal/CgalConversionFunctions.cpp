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

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcExtrudedAreaSolid*, cgal_shape_t&) {
	throw std::runtime_error("Not implemented IfcExtrudedAreaSolid");
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcCartesianPoint* l, cgal_point_t& point) {
  std::vector<double> xyz = l->Coordinates();
  if (xyz.size() == 3) {
    point = new Kernel::Point_3(xyz.size()     ? (xyz[0]*getValue(GV_LENGTH_UNIT)) : 0.0f,
                                xyz.size() > 1 ? (xyz[1]*getValue(GV_LENGTH_UNIT)) : 0.0f,
                                xyz.size() > 2 ? (xyz[2]*getValue(GV_LENGTH_UNIT)) : 0.0f);
    return true;
  } else {
    throw std::runtime_error("Point without 3 coordinates");
  }
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcDirection* l, cgal_direction_t& dir) {
//  IN_CACHE(IfcDirection,l,cgal_direction_t,dir)
  std::vector<double> xyz = l->DirectionRatios();
  dir = new Kernel::Vector_3(xyz.size()     ? xyz[0] : 0.0f,
                             xyz.size() > 1 ? xyz[1] : 0.0f,
                             xyz.size() > 2 ? xyz[2] : 0.0f);
//  CACHE(IfcDirection,l,dir)
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcAxis2Placement3D* l, cgal_placement_t& trsf) {
//  IN_CACHE(IfcAxis2Placement3D,l,gp_Trsf,trsf)
//  cgal_point_t o;cgal_direction_t axis = new Kernel::Vector_3(0,0,1);cgal_direction_t refDirection;
//  IfcGeom::OpenCascadeKernel::convert(l->Location(),o);
//  bool hasRef = l->hasRefDirection();
//  if ( l->hasAxis() ) IfcGeom::OpenCascadeKernel::convert(l->Axis(),axis);
//  if ( hasRef ) IfcGeom::OpenCascadeKernel::convert(l->RefDirection(),refDirection);
//  gp_Ax3 ax3;
//  if ( hasRef ) ax3 = gp_Ax3(o,axis,refDirection);
//  else ax3 = gp_Ax3(o,axis);
//  
//  if (!axis_equal(ax3, (gp_Ax3) gp::XOY(), getValue(GV_PRECISION))) {
//    trsf.SetTransformation(ax3, gp::XOY());
//  }
//  
//  CACHE(IfcAxis2Placement3D,l,trsf)
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcObjectPlacement* l, cgal_placement_t& trsf) {
//  IN_CACHE(IfcObjectPlacement,l,cgal_placement_t,trsf)
  if ( ! l->is(IfcSchema::Type::IfcLocalPlacement) ) {
    Logger::Message(Logger::LOG_ERROR, "Unsupported IfcObjectPlacement:", l->entity);
    return false;
  }
  IfcSchema::IfcLocalPlacement* current = (IfcSchema::IfcLocalPlacement*)l;
  for (;;) {
    cgal_placement_t trsf2;
    IfcSchema::IfcAxis2Placement* relplacement = current->RelativePlacement();
    if ( relplacement->is(IfcSchema::Type::IfcAxis2Placement3D) ) {
      IfcGeom::CgalKernel::convert((IfcSchema::IfcAxis2Placement3D*)relplacement,trsf2);
      *trsf = *trsf * *trsf2; // TODO: Or should it be the other way around?
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
