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

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcExtrudedAreaSolid *l, cgal_shape_t &shape) {
  const double height = l->Depth() * getValue(GV_LENGTH_UNIT);
  if (height < getValue(GV_PRECISION)) {
    Logger::Message(Logger::LOG_ERROR, "Non-positive extrusion height encountered for:", l->entity);
    return false;
  }
  
  cgal_face_t face;
  if ( !convert_face(l->SweptArea(),face) ) return false;

  cgal_placement_t trsf;
  bool has_position = true;
#ifdef USE_IFC4
  has_position = l->hasPosition();
#endif
  if (has_position) {
    IfcGeom::CgalKernel::convert(l->Position(), trsf);
  }

  cgal_direction_t dir;
  convert(l->ExtrudedDirection(),dir);
  
  std::list<cgal_face_t> face_list;
  face_list.push_back(face);
  
  for (std::vector<Kernel::Point_3>::const_iterator current_vertex = face.outer.begin();
       current_vertex != face.outer.end();
       ++current_vertex) {
    std::vector<Kernel::Point_3>::const_iterator next_vertex = current_vertex;
    ++next_vertex;
    if (next_vertex == face.outer.end()) {
      next_vertex = face.outer.begin();
    } cgal_face_t side_face;
    side_face.outer.push_back(*next_vertex);
    side_face.outer.push_back(*current_vertex);
    side_face.outer.push_back(*current_vertex+dir);
    side_face.outer.push_back(*next_vertex+dir);
    face_list.push_back(side_face);
  }
  
  cgal_face_t top_face;
  for (std::vector<Kernel::Point_3>::const_reverse_iterator vertex = face.outer.rbegin();
       vertex != face.outer.rend();
       ++vertex) {
    top_face.outer.push_back(*vertex+dir);
  } face_list.push_back(top_face);
  
  cgal_shape_t polyhedron = CGAL::Polyhedron_3<Kernel>();
  PolyhedronBuilder builder(&face_list);
  polyhedron.delegate(builder);
  
  shape = polyhedron;
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcCartesianPoint* l, cgal_point_t& point) {
  std::vector<double> xyz = l->Coordinates();
  if (xyz.size() == 3) {
    point = Kernel::Point_3(xyz.size()     ? (xyz[0]*getValue(GV_LENGTH_UNIT)) : 0.0f,
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
  cgal_direction_t refDirection = Kernel::Vector_3(1,0,0);  // TODO: Put identity for now. Check?
  IfcGeom::CgalKernel::convert(l->Location(),o);
  bool hasRef = l->hasRefDirection();
  if ( hasRef ) IfcGeom::CgalKernel::convert(l->RefDirection(),refDirection);
  
  // TODO: From Thomas' email. Should be checked.
  Kernel::Vector_3 y = CGAL::cross_product(Kernel::Vector_3(0.0, 0.0, 1.0), refDirection);
  trsf = Kernel::Aff_transformation_3(refDirection.cartesian(0), y.cartesian(0), 0.0, o.cartesian(0),
                                      refDirection.cartesian(1), y.cartesian(1), 0.0, o.cartesian(1),
                                      0.0, y.cartesian(2), 1.0, 0.0);
  
  //  CACHE(IfcAxis2Placement3D,l,trsf)
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcAxis2Placement3D* l, cgal_placement_t& trsf) {
//  IN_CACHE(IfcAxis2Placement3D,l,gp_Trsf,trsf)
  cgal_point_t o;
  cgal_direction_t axis = Kernel::Vector_3(0,0,1);
  cgal_direction_t refDirection = Kernel::Vector_3(1,0,0);  // TODO: Put identity for now. Check?
  IfcGeom::CgalKernel::convert(l->Location(),o);
  bool hasRef = l->hasRefDirection();
  if ( l->hasAxis() ) IfcGeom::CgalKernel::convert(l->Axis(),axis);
  if ( hasRef ) IfcGeom::CgalKernel::convert(l->RefDirection(),refDirection);
  
  // TODO: From Thomas' email. Should be checked.
  Kernel::Vector_3 y = CGAL::cross_product(axis, refDirection);
  trsf = Kernel::Aff_transformation_3(refDirection.cartesian(0), y.cartesian(0), axis.cartesian(0), o.cartesian(0),
                                      refDirection.cartesian(1), y.cartesian(1), axis.cartesian(1), o.cartesian(1),
                                      refDirection.cartesian(2), y.cartesian(2), axis.cartesian(2), o.cartesian(2));
  
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
  IfcSchema::IfcLocalPlacement* current = (IfcSchema::IfcLocalPlacement*)l;
  for (;;) {
    cgal_placement_t trsf2;
    IfcSchema::IfcAxis2Placement* relplacement = current->RelativePlacement();
    if ( relplacement->is(IfcSchema::Type::IfcAxis2Placement3D) ) {
      IfcGeom::CgalKernel::convert((IfcSchema::IfcAxis2Placement3D*)relplacement,trsf2);
      trsf = trsf * trsf2; // TODO: I think it's fine, but maybe should it be the other way around?
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
