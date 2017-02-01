/********************************************************************************
*                                                                              *
* This file is part of IfcOpenShell.                                           *
*                                                                              *
* IfcOpenShell is free software: you can redistribute it and/or modify         *
* it under the terms of the Lesser GNU General Public License as published by  *
* the Free Software Foundation, either version 3.0 of the License, or          *
* (at your option) any later version.                                          *
*                                                                              *
* IfcOpenShell is distributed in the hope that it will be useful,              *
* but WITHOUT ANY WARRANTY; without even the implied warranty of               *
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
* Lesser GNU General Public License for more details.                          *
*                                                                              *
* You should have received a copy of the Lesser GNU General Public License     *
* along with this program. If not, see <http://www.gnu.org/licenses/>.         *
*                                                                              *
********************************************************************************/

#include "../../../ifcgeom/IfcGeomShapeType.h"
#include "../../../ifcgeom/IfcGeom.h"

#include "CgalKernel.h"
#include "CgalConversionResult.h"

using namespace IfcSchema;
using namespace IfcUtil;


bool IfcGeom::CgalKernel::convert_shapes(const IfcBaseClass* l, ConversionResults& r) {
	if (shape_type(l) != ST_SHAPELIST) {
		cgal_shape_t shp;
		if (convert_shape(l, shp)) {
			r.push_back(IfcGeom::ConversionResult(new CgalShape(shp), get_style(l->as<IfcSchema::IfcRepresentationItem>())));
			return true;
		}
		return false;
	}

#include "CgalEntityMappingShapes.h"
	Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l->entity);
	return false;
}

IfcGeom::ShapeType IfcGeom::CgalKernel::shape_type(const IfcBaseClass* l) {
#include "CgalEntityMappingShapeType.h"
	return ST_OTHER;
}

bool IfcGeom::CgalKernel::convert_shape(const IfcBaseClass* l, cgal_shape_t& r) {
	const unsigned int id = l->entity->id();
	bool success = false;
	bool processed = false;
	bool ignored = false;

#ifndef NO_CACHE
	std::map<int, cgal_shape_t>::const_iterator it = cache.Shape.find(id);
	if ( it != cache.Shape.end() ) { r = it->second; return true; }
#endif
	const bool include_curves = getValue(GV_DIMENSIONALITY) != +1;
	const bool include_solids_and_surfaces = getValue(GV_DIMENSIONALITY) != -1;

	IfcGeom::ShapeType st = shape_type(l);
	ignored = (!include_solids_and_surfaces && (st == ST_SHAPE || st == ST_FACE)) || (!include_curves && (st == ST_WIRE || st == ST_CURVE));
	if (st == ST_SHAPE && include_solids_and_surfaces) {
#include "CgalEntityMappingShape.h"
	}

	if ( processed && success ) { 
		const double precision = getValue(GV_PRECISION);
		// apply_tolerance(r, precision);
#ifndef NO_CACHE
		cache.Shape[id] = r;
#endif
	} else if (!ignored) {
		const char* const msg = processed
			? "Failed to convert:"
			: "No operation defined for:";
		Logger::Message(Logger::LOG_ERROR, msg, l->entity);
	}
	return success;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcManifoldSolidBrep* l, ConversionResults& shape) {
  cgal_shape_t s;
  const SurfaceStyle* collective_style = get_style(l);
  if (convert_shape(l->Outer(),s) ) {
//    const SurfaceStyle* indiv_style = get_style(l->Outer());
//    
//    IfcSchema::IfcClosedShell::list::ptr voids(new IfcSchema::IfcClosedShell::list);
//    if (l->is(IfcSchema::Type::IfcFacetedBrepWithVoids)) {
//      voids = l->as<IfcSchema::IfcFacetedBrepWithVoids>()->Voids();
//    }
//#ifdef USE_IFC4
//    if (l->is(IfcSchema::Type::IfcAdvancedBrepWithVoids)) {
//      voids = l->as<IfcSchema::IfcAdvancedBrepWithVoids>()->Voids();
//    }
//#endif
//    
//    for (IfcSchema::IfcClosedShell::list::it it = voids->begin(); it != voids->end(); ++it) {
//      TopoDS_Shape s2;
//      /// @todo No extensive shapefixing since shells should be disjoint.
//      /// @todo Awaiting generalized boolean ops module with appropriate checking
//      if (convert_shape(l->Outer(), s2)) {
//        s = BRepAlgoAPI_Cut(s, s2).Shape();
//      }
//    }
//    
//    shape.push_back(ConversionResult(new OpenCascadeShape(s), indiv_style ? indiv_style : collective_style));
//    return true;
  }
  return false;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcConnectedFaceSet* l, cgal_shape_t& shape) {
  IfcSchema::IfcFace::list::ptr faces = l->CfsFaces();

//  TopTools_ListOfShape face_list;
  for (IfcSchema::IfcFace::list::it it = faces->begin(); it != faces->end(); ++it) {
    bool success = false;
    cgal_face_t face;
    
    try {
      success = convert_face(*it, face);
    } catch (...) {}

    if (!success) {
      Logger::Message(Logger::LOG_WARNING, "Failed to convert face:", (*it)->entity);
      continue;
    }

//    if (face_area(face) > getValue(GV_MINIMAL_FACE_AREA)) {
//      face_list.Append(face);
//    } else {
//      Logger::Message(Logger::LOG_WARNING, "Invalid face:", (*it)->entity);
//    }
  }
//
//  if (face_list.Extent() == 0) {
//    return false;
//  }
//  
//  if (face_list.Extent() > getValue(GV_MAX_FACES_TO_SEW) || !create_solid_from_faces(face_list, shape)) {
//    TopoDS_Compound compound;
//    BRep_Builder builder;
//    builder.MakeCompound(compound);
//    
//    TopTools_ListIteratorOfListOfShape face_iterator;
//    for (face_iterator.Initialize(face_list); face_iterator.More(); face_iterator.Next()) {
//      builder.Add(compound, face_iterator.Value());
//    }
//    shape = compound;
//  }
  
  return true;
}

bool IfcGeom::CgalKernel::convert_wire(const IfcBaseClass* l, cgal_wire_t& r) {
#include "CgalEntityMappingWire.h"
	Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l->entity);
	return false;
}

bool IfcGeom::CgalKernel::convert_face(const IfcBaseClass* l, cgal_face_t& r) {
#include "CgalEntityMappingFace.h"
	Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l->entity);
	return false;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcFace* l, cgal_face_t& face) {
  IfcSchema::IfcFaceBound::list::ptr bounds = l->Bounds();
  
//  Handle(Geom_Surface) face_surface;
//  const bool is_face_surface = l->is(IfcSchema::Type::IfcFaceSurface);
//  
//  if (is_face_surface) {
//    IfcSchema::IfcFaceSurface* fs = (IfcSchema::IfcFaceSurface*) l;
//    fs->FaceSurface();
//    // FIXME: Surfaces are interpreted as a TopoDS_Shape
//    TopoDS_Shape surface_shape;
//    if (!convert_shape(fs->FaceSurface(), surface_shape)) return false;
//    
//    // FIXME: Assert this obtaines the only face
//    TopExp_Explorer exp(surface_shape, TopAbs_FACE);
//    if (!exp.More()) return false;
//    
//    TopoDS_Face surface = TopoDS::Face(exp.Current());
//    face_surface = BRep_Tool::Surface(surface);
//  }
//  
//  const int num_bounds = bounds->size();
//  int num_outer_bounds = 0;
//  
//  for (IfcSchema::IfcFaceBound::list::it it = bounds->begin(); it != bounds->end(); ++it) {
//    IfcSchema::IfcFaceBound* bound = *it;
//    if (bound->is(IfcSchema::Type::IfcFaceOuterBound)) num_outer_bounds ++;
//  }
//  
//  // The number of outer bounds should be one according to the schema. Also Open Cascade
//  // expects this, but it is not strictly checked. Regardless, if the number is greater,
//  // the face will still be processed as long as there are no holes. A compound of faces
//  // is returned in that case.
//  if (num_bounds > 1 && num_outer_bounds > 1 && num_bounds != num_outer_bounds) {
//    Logger::Message(Logger::LOG_ERROR, "Invalid configuration of boundaries for:", l->entity);
//    return false;
//  }
//  
//  TopoDS_Compound compound;
//  BRep_Builder builder;
//  if (num_outer_bounds > 1) {
//    builder.MakeCompound(compound);
//  }
//  
//  TopTools_DataMapOfShapeInteger wire_senses;
//  
//  // The builder is initialized on the heap because of the various different moments
//  // of initialization depending on the configuration of surfaces and boundaries.
//  BRepBuilderAPI_MakeFace* mf = 0;
//  
//  bool success = false;
//  int processed = 0;
//  
//  for (int process_interior = 0; process_interior <= 1; ++process_interior) {
    for (IfcSchema::IfcFaceBound::list::it it = bounds->begin(); it != bounds->end(); ++it) {
      IfcSchema::IfcFaceBound* bound = *it;
      IfcSchema::IfcLoop* loop = bound->Bound();

//      bool same_sense = bound->Orientation();
//      const bool is_interior =
//      !bound->is(IfcSchema::Type::IfcFaceOuterBound) &&
//      (num_bounds > 1) &&
//      (num_outer_bounds < num_bounds);
//      
//      // The exterior face boundary is processed first
//      if (is_interior == !process_interior) continue;
//      
      cgal_wire_t wire;
      if (!convert_wire(loop, wire)) {
        Logger::Message(Logger::LOG_ERROR, "Failed to process face boundary loop", loop->entity);
//        delete mf;
        return false;
      }

//      if (!same_sense) {
//        wire.Reverse();
//      }
//
//      wire_senses.Bind(wire.Oriented(TopAbs_FORWARD), same_sense ? TopAbs_FORWARD : TopAbs_REVERSED);
//      
//      bool flattened_wire = false;
//      
//      if (!mf) {
//      process_wire:
//        
//        if (face_surface.IsNull()) {
//          mf = new BRepBuilderAPI_MakeFace(wire);
//        } else {
//          /// @todo check necessity of false here
//          mf = new BRepBuilderAPI_MakeFace(face_surface, wire, false);
//        }
//        
//        if (mf->IsDone()) {
//          TopoDS_Face outer_face_bound = mf->Face();
//          
//          // In case of (non-planar) face surface, p-curves need to be computed.
//          // For planar faces, Open Cascade generates p-curves on the fly.
//          if (!face_surface.IsNull()) {
//            TopExp_Explorer exp(outer_face_bound, TopAbs_EDGE);
//            for (; exp.More(); exp.Next()) {
//              const TopoDS_Edge& edge = TopoDS::Edge(exp.Current());
//              ShapeFix_Edge fix_edge;
//              fix_edge.FixAddPCurve(edge, outer_face_bound, false, getValue(GV_PRECISION));
//            }
//          }
//          
//          if (BRepCheck_Face(outer_face_bound).OrientationOfWires() == BRepCheck_BadOrientationOfSubshape) {
//            wire.Reverse();
//            same_sense = !same_sense;
//            delete mf;
//            if (face_surface.IsNull()) {
//              mf = new BRepBuilderAPI_MakeFace(wire);
//            } else {
//              mf = new BRepBuilderAPI_MakeFace(face_surface, wire);
//            }
//            ShapeFix_Face fix(mf->Face());
//            fix.FixOrientation();
//            outer_face_bound = fix.Face();
//          }
//          
//          if (num_outer_bounds > 1) {
//            builder.Add(compound, outer_face_bound);
//            delete mf; mf = 0;
//          } else if (num_bounds > 1) {
//            // Reinitialize the builder to the outer face
//            // bound in order to add holes more robustly.
//            delete mf;
//            // TODO: What about the face_surface?
//            mf = new BRepBuilderAPI_MakeFace(outer_face_bound);
//          } else {
//            face = outer_face_bound;
//            success = true;
//          }
//        } else {
//          const bool non_planar = mf->Error() == BRepBuilderAPI_NotPlanar;
//          delete mf;
//          if (!non_planar || flattened_wire || !flatten_wire(wire)) {
//            Logger::Message(Logger::LOG_ERROR, "Failed to process face boundary", bound->entity);
//            return false;
//          } else {
//            Logger::Message(Logger::LOG_ERROR, "Flattening face boundary", bound->entity);
//            flattened_wire = true;
//            goto process_wire;
//          }
//        }
//        
//      } else {
//        mf->Add(wire);
//      }
//      processed ++;
    }
//  }
//  
//  if (!success) {
//    success = processed == num_bounds;
//    if (success) {
//      if (num_outer_bounds > 1) {
//        face = compound;
//      } else {
//        success = success && mf->IsDone();
//        if (success) {
//          face = mf->Face();
//        }
//        
//        ShapeFix_Face sfs(TopoDS::Face(face));
//        TopTools_DataMapOfShapeListOfShape wire_map;
//        sfs.FixOrientation(wire_map);
//        
//        TopoDS_Iterator jt(face, false);
//        for (; jt.More(); jt.Next()) {
//          const TopoDS_Wire& w = TopoDS::Wire(jt.Value());
//          if (wire_map.IsBound(w)) {
//            const TopTools_ListOfShape& shapes = wire_map.Find(w);
//            TopTools_ListIteratorOfListOfShape it(shapes);
//            for (; it.More(); it.Next()) {
//              // Apparently the wire got reversed, so register it with opposite orientation in the map
//              wire_senses.Bind(it.Value(), wire_senses.Find(w) == TopAbs_FORWARD ? TopAbs_REVERSED : TopAbs_FORWARD);
//            }
//          }
//        }
//        
//        face = TopoDS::Face(sfs.Face());				
//      }
//    }
//  }
//  
//  if (success) {
//    // If the wires are reversed the face needs to be reversed as well in order
//    // to maintain the counter-clock-wise ordering of the bounding wire's vertices.
//    if (num_bounds == 1 || true) {
//      bool all_reversed = true;
//      TopoDS_Iterator jt(face, false);
//      for (; jt.More(); jt.Next()) {
//        const TopoDS_Wire& w = TopoDS::Wire(jt.Value());
//        if (!wire_senses.IsBound(w.Oriented(TopAbs_FORWARD)) || (w.Orientation() == wire_senses.Find(w.Oriented(TopAbs_FORWARD)))) {
//          all_reversed = false;
//        }
//      }
//      
//      if (all_reversed) {
//        face.Reverse();
//      }
//    }
//    
//    ShapeFix_ShapeTolerance FTol;
//    FTol.SetTolerance(face, getValue(GV_PRECISION), TopAbs_FACE);
//  }
//  
//  delete mf;
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcPolyLoop* l, cgal_wire_t& result) {
  IfcSchema::IfcCartesianPoint::list::ptr points = l->Polygon();
  
  // Parse and store the points in a sequence
  cgal_wire_t polygon = new std::vector<Kernel::Point_3>();
  for(IfcSchema::IfcCartesianPoint::list::it it = points->begin(); it != points->end(); ++ it) {
    cgal_point_t pnt;
    IfcGeom::CgalKernel::convert(*it, pnt);
//    std::cout << *pnt << std::endl;
    polygon->push_back(*pnt);
  }

  // A loop should consist of at least three vertices
  int original_count = polygon->size();
  if (original_count < 3) {
    Logger::Message(Logger::LOG_ERROR, "Not enough edges for:", l->entity);
    return false;
  }

//  // Remove points that are too close to one another
//  remove_duplicate_points_from_loop(polygon, true);
//  
//  int count = polygon.Length();
//  if (original_count - count != 0) {
//    std::stringstream ss; ss << (original_count - count) << " edges removed for:";
//    Logger::Message(Logger::LOG_WARNING, ss.str(), l->entity);
//  }
//  
//  if (count < 3) {
//    Logger::Message(Logger::LOG_ERROR, "Not enough edges for:", l->entity);
//    return false;
//  }

  result = polygon;
  return true;
}

bool IfcGeom::CgalKernel::convert_curve(const IfcBaseClass* l, cgal_curve_t& r) {
#include "CgalEntityMappingCurve.h"
	Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l->entity);
	return false;
}
