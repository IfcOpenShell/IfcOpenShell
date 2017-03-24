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

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcGeometricSet* l, ConversionResults& shapes) {
  IfcEntityList::ptr elements = l->Elements();
  if ( !elements->size() ) return false;
  bool part_succes = false;
  const IfcGeom::SurfaceStyle* parent_style = get_style(l);
  for ( IfcEntityList::it it = elements->begin(); it != elements->end(); ++ it ) {
    IfcSchema::IfcGeometricSetSelect* element = *it;
    cgal_shape_t s;
    if (convert_shape(element, s)) {
      part_succes = true;
      const IfcGeom::SurfaceStyle* style = 0;
      if (element->is(IfcSchema::Type::IfcPoint)) {
        style = get_style((IfcSchema::IfcPoint*) element);
      } else if (element->is(IfcSchema::Type::IfcCurve)) {
        style = get_style((IfcSchema::IfcCurve*) element);
      } else if (element->is(IfcSchema::Type::IfcSurface)) {
        style = get_style((IfcSchema::IfcSurface*) element);
      }
      shapes.push_back(ConversionResult(new CgalShape(s), style ? style : parent_style));
    }
  }
  return part_succes;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcShellBasedSurfaceModel* l, ConversionResults& shapes) {
  IfcEntityList::ptr shells = l->SbsmBoundary();
  const SurfaceStyle* collective_style = get_style(l);
  for( IfcEntityList::it it = shells->begin(); it != shells->end(); ++ it ) {
    cgal_shape_t s;
    const SurfaceStyle* shell_style = 0;
    if ((*it)->is(IfcSchema::Type::IfcRepresentationItem)) {
      shell_style = get_style((IfcSchema::IfcRepresentationItem*)*it);
    }
    if (convert_shape(*it,s)) {
      shapes.push_back(ConversionResult(new CgalShape(s), shell_style ? shell_style : collective_style));
    }
  }
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcManifoldSolidBrep* l, ConversionResults& shape) {
  cgal_shape_t s;
  CGAL::Nef_polyhedron_3<Kernel> nef_s(s);
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
      cgal_shape_t s2;
      CGAL::Nef_polyhedron_3<Kernel> nef_s2(s2);
      // TODO: This looks weird. Aren't we removing the outer shell again and again?
      // Maybe it should be
      // if (convert_shape(*it, s2)) {
      if (convert_shape(l->Outer(), s2)) {
        nef_s -= nef_s2;
      }
    }
    
    nef_s.convert_to_polyhedron(s);
    shape.push_back(ConversionResult(new CgalShape(s), indiv_style ? indiv_style : collective_style));
    return true;
  }
  return false;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcMappedItem* l, ConversionResults& shapes) {
  cgal_placement_t gtrsf;
  IfcSchema::IfcCartesianTransformationOperator* transform = l->MappingTarget();
  if ( transform->is(IfcSchema::Type::IfcCartesianTransformationOperator3DnonUniform) ) {
    IfcGeom::CgalKernel::convert((IfcSchema::IfcCartesianTransformationOperator3DnonUniform*)transform,gtrsf);
  } else if ( transform->is(IfcSchema::Type::IfcCartesianTransformationOperator2DnonUniform) ) {
    IfcGeom::CgalKernel::convert((IfcSchema::IfcCartesianTransformationOperator2DnonUniform*)transform,gtrsf);
  } else if ( transform->is(IfcSchema::Type::IfcCartesianTransformationOperator3D) ) {
    IfcGeom::CgalKernel::convert((IfcSchema::IfcCartesianTransformationOperator3D*)transform,gtrsf);
  } else if ( transform->is(IfcSchema::Type::IfcCartesianTransformationOperator2D) ) {
    IfcGeom::CgalKernel::convert((IfcSchema::IfcCartesianTransformationOperator2D*)transform,gtrsf);
  }
  IfcSchema::IfcRepresentationMap* map = l->MappingSource();
  IfcSchema::IfcAxis2Placement* placement = map->MappingOrigin();
  cgal_placement_t trsf;
  if (placement->is(IfcSchema::Type::IfcAxis2Placement3D)) {
    IfcGeom::CgalKernel::convert((IfcSchema::IfcAxis2Placement3D*)placement,trsf);
  } else {
    cgal_placement_t trsf_2d;
    IfcGeom::CgalKernel::convert((IfcSchema::IfcAxis2Placement2D*)placement,trsf_2d);
    trsf = trsf_2d;
  }
  
  // TODO: Check
  gtrsf = trsf * gtrsf;
  
  //  std::cout << std::endl;
  //  for (int i = 0; i < 3; ++i) {
  //    for (int j = 0; j < 4; ++j) {
  //      std::cout << gtrsf.cartesian(i, j) << " ";
  //    } std::cout << std::endl;
  //  }
  
  const IfcGeom::SurfaceStyle* mapped_item_style = get_style(l);
  
  const size_t previous_size = shapes.size();
  bool b = convert_shapes(map->MappedRepresentation(), shapes);
  
  for (size_t i = previous_size; i < shapes.size(); ++ i ) {
    IfcGeom::CgalPlacement place(gtrsf);
    shapes[i].prepend(&place);
    
    // Apply styles assigned to the mapped item only if on
    // a more granular level no styles have been applied
    if (!shapes[i].hasStyle()) {
      shapes[i].setStyle(mapped_item_style);
    }
  }
  
  return b;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcFaceBasedSurfaceModel* l, ConversionResults& shapes) {
  bool part_success = false;
  IfcSchema::IfcConnectedFaceSet::list::ptr facesets = l->FbsmFaces();
  const SurfaceStyle* collective_style = get_style(l);
  for( IfcSchema::IfcConnectedFaceSet::list::it it = facesets->begin(); it != facesets->end(); ++ it ) {
    cgal_shape_t s;
    const SurfaceStyle* shell_style = get_style(*it);
    if (convert_shape(*it,s)) {
      shapes.push_back(ConversionResult(new CgalShape(s), shell_style ? shell_style : collective_style));
      part_success |= true;
    }
  }
  return part_success;
}
