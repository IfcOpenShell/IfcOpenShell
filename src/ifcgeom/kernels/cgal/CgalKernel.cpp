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

#include "CgalKernel.h"

namespace {
	struct MAKE_TYPE_NAME(factory_t) {
		IfcGeom::Kernel* operator()(IfcParse::IfcFile* file) const {
			IfcGeom::MAKE_TYPE_NAME(CgalKernel)* k = new IfcGeom::MAKE_TYPE_NAME(CgalKernel);
			return k;
		}
	};
}

void MAKE_INIT_FN(KernelImplementation_cgal_)(IfcGeom::impl::KernelFactoryImplementation* mapping) {
	static const std::string schema_name = STRINGIFY(IfcSchema);
	MAKE_TYPE_NAME(factory_t) factory;
	mapping->bind(schema_name, "cgal", factory);
}

#define CgalKernel MAKE_TYPE_NAME(CgalKernel)

bool IfcGeom::CgalKernel::is_identity_transform(const IfcUtil::IfcBaseClass* l) {
	Logger::Message(Logger::LOG_ERROR, "Not implemented is_identity_transform()");
	return false;
	/*
	// OpenCascade kernel code below

	IfcSchema::IfcAxis2Placement2D* ax2d;
	IfcSchema::IfcAxis2Placement3D* ax3d;

	IfcSchema::IfcCartesianTransformationOperator2D* op2d;
	IfcSchema::IfcCartesianTransformationOperator3D* op3d;
	IfcSchema::IfcCartesianTransformationOperator2DnonUniform* op2dnonu;
	IfcSchema::IfcCartesianTransformationOperator3DnonUniform* op3dnonu;

	if ((op2dnonu = l->as<IfcSchema::IfcCartesianTransformationOperator2DnonUniform>()) != 0) {
		gp_GTrsf2d gtrsf2d;
		convert(op2dnonu, gtrsf2d);
		return gtrsf2d.Form() == gp_Identity;
	} else if ((op2d = l->as<IfcSchema::IfcCartesianTransformationOperator2D>()) != 0) {
		gp_Trsf2d trsf2d;
		convert(op2d, trsf2d);
		return trsf2d.Form() == gp_Identity;
	} else if ((op3dnonu = l->as<IfcSchema::IfcCartesianTransformationOperator3DnonUniform>()) != 0) {
		gp_GTrsf gtrsf;
		convert(op3dnonu, gtrsf);
		return gtrsf.Form() == gp_Identity;
	} else if ((op3d = l->as<IfcSchema::IfcCartesianTransformationOperator3D>()) != 0) {
		gp_Trsf trsf;
		convert(op3d, trsf);
		return trsf.Form() == gp_Identity;
	} else if ((ax2d = l->as<IfcSchema::IfcAxis2Placement2D>()) != 0) {
		gp_Trsf2d trsf2d;
		convert(ax2d, trsf2d);
		return trsf2d.Form() == gp_Identity;
	} else if ((ax3d = l->as<IfcSchema::IfcAxis2Placement3D>()) != 0) {
		gp_Trsf trsf;
		convert(ax3d, trsf);
		return trsf.Form() == gp_Identity;
	} else {
		throw IfcParse::IfcException("Invalid valuation for IfcAxis2Placement / IfcCartesianTransformationOperator");
	}
	*/
}

bool IfcGeom::CgalKernel::apply_layerset(const IfcSchema::IfcProduct* product, IfcGeom::ConversionResults& shapes) {
	throw std::runtime_error("not implemented");
}

bool IfcGeom::CgalKernel::validate_quantities(const IfcSchema::IfcProduct* product, const IfcGeom::Representation::BRep& brep) {
	throw std::runtime_error("not implemented");
}

bool IfcGeom::CgalKernel::convert_openings(const IfcSchema::IfcProduct* product, const IfcSchema::IfcRelVoidsElement::list::ptr& openings, const IfcGeom::ConversionResults& shapes, const IfcGeom::ConversionResultPlacement* trsf, IfcGeom::ConversionResults& opened_shapes) {
  std::list<cgal_shape_t> opening_shapelist;
  
  for ( IfcSchema::IfcRelVoidsElement::list::it it = openings->begin(); it != openings->end(); ++ it ) {
    IfcSchema::IfcRelVoidsElement* v = *it;
    IfcSchema::IfcFeatureElementSubtraction* fes = v->RelatedOpeningElement();
    if ( fes->is(IfcSchema::Type::IfcOpeningElement) ) {
      if (!fes->hasRepresentation()) continue;
      
      // Convert the IfcRepresentation of the IfcOpeningElement
      cgal_placement_t opening_trsf;
      if (fes->hasObjectPlacement()) {
        try {
          convert(fes->ObjectPlacement(),opening_trsf);
        } catch (...) {}
      }
      
      // Move the opening into the coordinate system of the IfcProduct
      opening_trsf = entity_trsf.inverse() * opening_trsf;
      
      IfcSchema::IfcProductRepresentation* prodrep = fes->Representation();
      IfcSchema::IfcRepresentation::list::ptr reps = prodrep->Representations();
      
      IfcGeom::ConversionResults opening_shapes;
						
      for ( IfcSchema::IfcRepresentation::list::it it2 = reps->begin(); it2 != reps->end(); ++ it2 ) {
        convert_shapes(*it2,opening_shapes);
      }
      
      for ( unsigned int i = 0; i < opening_shapes.size(); ++ i ) {
        cgal_placement_t gtrsf;
        if (opening_shapes[i].Placement()) {
          gtrsf = *(CgalPlacement*)opening_shapes[i].Placement();
        }
        gtrsf = opening_trsf * gtrsf;
        cgal_shape_t opening_shape(((CgalShape*)opening_shapes[i].Shape())->shape());
        for (auto &vertex: vertices(opening_shape)) vertex->point() = vertex->point().transform(gtrsf);
        opening_shapelist.push_back(opening_shape);
      }
      
    }
  }
  
  // Iterate over the shapes of the IfcProduct
  for ( IfcGeom::ConversionResults::const_iterator it3 = entity_shapes.begin(); it3 != entity_shapes.end(); ++ it3 ) {
    const cgal_shape_t& entity_shape_unlocated(((CgalShape*)it3->Shape())->shape());
    cgal_shape_t entity_shape(entity_shape_unlocated);
    if (it3->Placement()) {
      const cgal_placement_t& entity_shape_gtrsf = *(CgalPlacement*)it3->Placement();
      for (auto &vertex: vertices(entity_shape)) vertex->point() = vertex->point().transform(entity_shape_gtrsf);
    }
    
    cgal_shape_t original_entity_shape(entity_shape);
    
    if (!entity_shape.is_valid()) {
      Logger::Message(Logger::LOG_ERROR, "Conversion to Nef will fail. Invalid entity:", entity->entity);
      return false;
    }
    
    if (!entity_shape.is_closed()) {
      // TODO: There can be substractions to remove parts of non-volumetric objects. Maybe iterate over all faces of an entity and put them in a Nef_polyhedron_3 through Boolean union? Highly inefficient but maybe desirable...
      Logger::Message(Logger::LOG_ERROR, "Subtraction of openings not supported for non-closed entity:", entity->entity);
      return false;
    }
    
    bool success = false;
    
    try {
      success = CGAL::Polygon_mesh_processing::triangulate_faces(entity_shape);
    } catch (...) {
      Logger::Message(Logger::LOG_ERROR, "Triangulation of entity crashed:", entity->entity);
      return false;
    }
    
    if (!success) {
      Logger::Message(Logger::LOG_ERROR, "Triangulation of entity failed:", entity->entity);
      return false;
    }
    
    if (CGAL::Polygon_mesh_processing::does_self_intersect(entity_shape)) {
      Logger::Message(Logger::LOG_ERROR, "Conversion to Nef will fail. Self-intersecting entity:", entity->entity);
      return false;
    }
    
    CGAL::Nef_polyhedron_3<Kernel> nef_brep_cut_result;
    
    try {
      nef_brep_cut_result = CGAL::Nef_polyhedron_3<Kernel>(entity_shape);
    } catch (...) {
      Logger::Message(Logger::LOG_ERROR, "Could not convert entity to Nef:", entity->entity);
      return false;
    }
    
    try {
      cgal_shape_t brep_cut_result;
      nef_brep_cut_result.convert_to_polyhedron(brep_cut_result);
    } catch (...) {
      Logger::Message(Logger::LOG_WARNING, "Final conversion will likely fail. Could not convert entity from Nef:", entity->entity);
    }
    
    for (auto &opening: opening_shapelist) {
      
      cgal_shape_t original_opening_shape(opening);
      if (!opening.is_valid()) {
        Logger::Message(Logger::LOG_ERROR, "Conversion to Nef will fail. Invalid opening in entity:", entity->entity);
        return false;
      } if (!opening.is_closed()) {
        Logger::Message(Logger::LOG_ERROR, "Subtraction of opening makes no sense. Not closed opening in entity:", entity->entity);
        return false;
      }
      
      success = false;
      
      try {
        success = CGAL::Polygon_mesh_processing::triangulate_faces(opening);
      } catch (...) {
        Logger::Message(Logger::LOG_ERROR, "Triangulation of opening of entity crashed:", entity->entity);
        return false;
      }
      
      if (!success) {
        Logger::Message(Logger::LOG_ERROR, "Triangulation of opening of entity failed:", entity->entity);
        return false;
      }
      
      if (CGAL::Polygon_mesh_processing::does_self_intersect(entity_shape)) {
        Logger::Message(Logger::LOG_ERROR, "Conversion to Nef will fail. Self-intersecting opening of entity:", entity->entity);
      }
      
      CGAL::Nef_polyhedron_3<Kernel> nef_opening;
      
      try {
        nef_opening = CGAL::Nef_polyhedron_3<Kernel>(opening);
      } catch (...) {
        Logger::Message(Logger::LOG_ERROR, "Could not convert opening of entity to Nef:", entity->entity);
        return false;
      }
      
      try {
        cgal_shape_t opening_shape;
        nef_opening.convert_to_polyhedron(opening_shape);
      } catch (...) {
        Logger::Message(Logger::LOG_WARNING, "Final conversion will likely fail. Could not convert opening of entity from Nef:", entity->entity);
        // return false;
      }
      
      try {
        nef_brep_cut_result -= nef_opening;
      } catch (...) {
        Logger::Message(Logger::LOG_ERROR, "Could not subtract Nef opening of entity:", entity->entity);
        return false;
      }
    }
    
    try {
      nef_brep_cut_result.convert_to_polyhedron(entity_shape);
    } catch (...) {
      Logger::Message(Logger::LOG_ERROR, "Could not convert entity with openings from Nef:", entity->entity);
      return false;
    }
    
    cut_shapes.push_back(IfcGeom::ConversionResult(new CgalShape(entity_shape), &it3->Style()));
    
  } return true;
}
