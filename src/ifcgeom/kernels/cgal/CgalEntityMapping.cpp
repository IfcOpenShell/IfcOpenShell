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
    const SurfaceStyle* indiv_style = get_style(l->Outer());
    
    IfcSchema::IfcClosedShell::list::ptr voids(new IfcSchema::IfcClosedShell::list);
    if (l->is(IfcSchema::Type::IfcFacetedBrepWithVoids)) {
      voids = l->as<IfcSchema::IfcFacetedBrepWithVoids>()->Voids();
    }
#ifdef USE_IFC4
    if (l->is(IfcSchema::Type::IfcAdvancedBrepWithVoids)) {
      voids = l->as<IfcSchema::IfcAdvancedBrepWithVoids>()->Voids();
    }
#endif
    
    for (IfcSchema::IfcClosedShell::list::it it = voids->begin(); it != voids->end(); ++it) {
//      TopoDS_Shape s2;
//      /// @todo No extensive shapefixing since shells should be disjoint.
//      /// @todo Awaiting generalized boolean ops module with appropriate checking
//      if (convert_shape(l->Outer(), s2)) {
//        s = BRepAlgoAPI_Cut(s, s2).Shape();
//      }
    }
    
    shape.push_back(ConversionResult(new CgalShape(s), indiv_style ? indiv_style : collective_style));
    return true;
  }
  return false;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcConnectedFaceSet* l, cgal_shape_t& shape) {
  IfcSchema::IfcFace::list::ptr faces = l->CfsFaces();

  std::list<cgal_face_t> face_list;
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
    
    face_list.push_back(face);
  }
  
  cgal_shape_t polyhedron = CGAL::Polyhedron_3<Kernel>();
  PolyhedronBuilder builder(&face_list);
  polyhedron.delegate(builder);
  
  shape = polyhedron;
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
  return true;
}

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

  // TODO: Remove repeated points (and points that are too close to one another?)
//  remove_duplicate_points_from_loop(polygon, true);
  
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
  return true;
}

bool IfcGeom::CgalKernel::convert_curve(const IfcBaseClass* l, cgal_curve_t& r) {
#include "CgalEntityMappingCurve.h"
	Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l->entity);
	return false;
}
