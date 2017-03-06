#include "CgalKernel.h"
#include "CgalConversionResult.h"

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

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcMappedItem* l, ConversionResults& shapes) {
  cgal_placement_t gtrsf;
  IfcSchema::IfcCartesianTransformationOperator* transform = l->MappingTarget();
  if ( transform->is(IfcSchema::Type::IfcCartesianTransformationOperator3DnonUniform) ) {
    Logger::Message(Logger::LOG_ERROR, "Unsupported MappingTarget:", transform->entity);
//    IfcGeom::CgalKernel::convert((IfcSchema::IfcCartesianTransformationOperator3DnonUniform*)transform,gtrsf);
  } else if ( transform->is(IfcSchema::Type::IfcCartesianTransformationOperator2DnonUniform) ) {
    Logger::Message(Logger::LOG_ERROR, "Unsupported MappingTarget:", transform->entity);
    return false;
  } else if ( transform->is(IfcSchema::Type::IfcCartesianTransformationOperator3D) ) {
    cgal_placement_t trsf;
    Logger::Message(Logger::LOG_ERROR, "Unsupported MappingTarget:", transform->entity);
//    IfcGeom::CgalKernel::convert((IfcSchema::IfcCartesianTransformationOperator3D*)transform,trsf);
    gtrsf = trsf;
  } else if ( transform->is(IfcSchema::Type::IfcCartesianTransformationOperator2D) ) {
    cgal_placement_t trsf_2d;
    Logger::Message(Logger::LOG_ERROR, "Unsupported MappingTarget:", transform->entity);
//    IfcGeom::CgalKernel::convert((IfcSchema::IfcCartesianTransformationOperator2D*)transform,trsf_2d);
    gtrsf = (cgal_placement_t) trsf_2d;
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
  //  std::cout << "Direction: " << dir << std::endl;
  
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
    side_face.outer.push_back(*current_vertex+height*dir);
    side_face.outer.push_back(*next_vertex+height*dir);
    face_list.push_back(side_face);
  }
  
  cgal_face_t top_face;
  for (std::vector<Kernel::Point_3>::const_reverse_iterator vertex = face.outer.rbegin();
       vertex != face.outer.rend();
       ++vertex) {
    top_face.outer.push_back(*vertex+height*dir);
  } face_list.push_back(top_face);
  
  // Naive creation
  cgal_shape_t polyhedron = CGAL::Polyhedron_3<Kernel>();
  PolyhedronBuilder builder(&face_list);
  polyhedron.delegate(builder);
  
  // Stitch edges
  //  std::cout << "Before: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
  CGAL::Polygon_mesh_processing::stitch_borders(polyhedron);
  if (!CGAL::Polygon_mesh_processing::is_outward_oriented(polyhedron)) {
    CGAL::Polygon_mesh_processing::reverse_face_orientations(polyhedron);
  } CGAL_postcondition(polyhedron.is_valid() && polyhedron.is_closed());
  //  std::cout << "After: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
  
  shape = polyhedron;
  return true;
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
    
    //    std::cout << "Face in ConnectedFaceSet: " << std::endl;
    //    for (auto &point: face.outer) {
    //      std::cout << "\tPoint(" << point << ")" << std::endl;
    //    }
    
    face_list.push_back(face);
  }
  
  // Naive creation
  cgal_shape_t polyhedron = CGAL::Polyhedron_3<Kernel>();
  PolyhedronBuilder builder(&face_list);
  polyhedron.delegate(builder);
  
  // Stitch edges
  //  std::cout << "Before: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
  CGAL::Polygon_mesh_processing::stitch_borders(polyhedron);
  if (!CGAL::Polygon_mesh_processing::is_outward_oriented(polyhedron)) {
    CGAL::Polygon_mesh_processing::reverse_face_orientations(polyhedron);
  }
  //  std::cout << "After: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
  
  shape = polyhedron;
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcCsgSolid* l, cgal_shape_t& shape) {
  return convert_shape(l->TreeRootExpression(), shape);
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcBlock* l, cgal_shape_t& shape) {
  const double dx = l->XLength() * getValue(GV_LENGTH_UNIT);
  const double dy = l->YLength() * getValue(GV_LENGTH_UNIT);
  const double dz = l->ZLength() * getValue(GV_LENGTH_UNIT);
  
  std::list<cgal_face_t> face_list;
  
  // x = 0
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(Kernel::Point_3(0, 0, 0));
  face_list.back().outer.push_back(Kernel::Point_3(0, dy, 0));
  face_list.back().outer.push_back(Kernel::Point_3(0, dy, dz));
  face_list.back().outer.push_back(Kernel::Point_3(0, 0, dz));
  
  // x = dx
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(Kernel::Point_3(dx, 0, 0));
  face_list.back().outer.push_back(Kernel::Point_3(dx, 0, dz));
  face_list.back().outer.push_back(Kernel::Point_3(dx, dy, dz));
  face_list.back().outer.push_back(Kernel::Point_3(dx, dy, 0));
  
  // y = 0
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(Kernel::Point_3(0, 0, 0));
  face_list.back().outer.push_back(Kernel::Point_3(0, 0, dz));
  face_list.back().outer.push_back(Kernel::Point_3(dx, 0, dz));
  face_list.back().outer.push_back(Kernel::Point_3(dx, 0, 0));
  
  // y = dy
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(Kernel::Point_3(0, dy, 0));
  face_list.back().outer.push_back(Kernel::Point_3(dx, dy, 0));
  face_list.back().outer.push_back(Kernel::Point_3(dx, dy, dz));
  face_list.back().outer.push_back(Kernel::Point_3(0, dy, dz));
  
  // z = 0
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(Kernel::Point_3(0, 0, 0));
  face_list.back().outer.push_back(Kernel::Point_3(dx, 0, 0));
  face_list.back().outer.push_back(Kernel::Point_3(dx, dy, 0));
  face_list.back().outer.push_back(Kernel::Point_3(0, dy, 0));
  
  // z = dz
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(Kernel::Point_3(0, 0, dz));
  face_list.back().outer.push_back(Kernel::Point_3(0, dy, dz));
  face_list.back().outer.push_back(Kernel::Point_3(dx, dy, dz));
  face_list.back().outer.push_back(Kernel::Point_3(dx, 0, dz));
  
  // Naive creation
  cgal_shape_t polyhedron = CGAL::Polyhedron_3<Kernel>();
  PolyhedronBuilder builder(&face_list);
  polyhedron.delegate(builder);
  
  // Stitch edges
  //  std::cout << "Before: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
  CGAL::Polygon_mesh_processing::stitch_borders(polyhedron);
  if (!CGAL::Polygon_mesh_processing::is_outward_oriented(polyhedron)) {
    CGAL::Polygon_mesh_processing::reverse_face_orientations(polyhedron);
  } CGAL_postcondition(polyhedron.is_valid() && polyhedron.is_closed());
  //  std::cout << "After: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
  
  cgal_placement_t trsf;
  IfcGeom::CgalKernel::convert(l->Position(),trsf);

  for (auto &vertex: vertices(polyhedron)) {
    vertex->point() = vertex->point().transform(trsf);
  }

  shape = polyhedron;
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcBooleanResult* l, cgal_shape_t& shape) {
  
  cgal_shape_t s1, s2;
  ConversionResults items1, items2;
  cgal_wire_t boundary_wire;
  IfcSchema::IfcBooleanOperand* operand1 = l->FirstOperand();
  IfcSchema::IfcBooleanOperand* operand2 = l->SecondOperand();
  bool is_halfspace = operand2->is(IfcSchema::Type::IfcHalfSpaceSolid);
  
  if ( shape_type(operand1) == ST_SHAPELIST ) {
    Logger::Message(Logger::LOG_ERROR, "s1: ST_SHAPELIST Unsupported", operand1->entity);
//    if (!(convert_shapes(operand1, items1) && flatten_shape_list(items1, s1, true))) {
      return false;
//    }
  } else if ( shape_type(operand1) == ST_SHAPE ) {
    if ( ! convert_shape(operand1, s1) ) {
      return false;
    }
//    TopoDS_Solid temp_solid;
//    s1 = ensure_fit_for_subtraction(s1, temp_solid);
  } else {
    Logger::Message(Logger::LOG_ERROR, "s1: Invalid representation item for boolean operation", operand1->entity);
    return false;
  }

//  const double first_operand_volume = shape_volume(s1);
//  if ( first_operand_volume <= ALMOST_ZERO )
//    Logger::Message(Logger::LOG_WARNING,"Empty solid for:",l->FirstOperand()->entity);
  
  bool shape2_processed = false;
  if ( shape_type(operand2) == ST_SHAPELIST ) {
    Logger::Message(Logger::LOG_ERROR, "s2: ST_SHAPELIST Unsupported", operand1->entity);
//    shape2_processed = convert_shapes(operand2, items2) && flatten_shape_list(items2, s2, true);
  } else if ( shape_type(operand2) == ST_SHAPE ) {
    shape2_processed = convert_shape(operand2,s2);
    if (shape2_processed && !is_halfspace) {
//      TopoDS_Solid temp_solid;
//      s2 = ensure_fit_for_subtraction(s2, temp_solid);
    }
  } else {
    Logger::Message(Logger::LOG_ERROR, "s2: Invalid representation item for boolean operation", operand2->entity);
  }

  if (!shape2_processed) {
//    shape = s1;
    Logger::Message(Logger::LOG_ERROR,"Failed to convert SecondOperand of:",l->entity);
//    return true;
  }

//  if (!is_halfspace) {
//    const double second_operand_volume = shape_volume(s2);
//    if ( second_operand_volume <= ALMOST_ZERO )
//      Logger::Message(Logger::LOG_WARNING,"Empty solid for:",operand2->entity);
//  }
  
  const IfcSchema::IfcBooleanOperator::IfcBooleanOperator op = l->Operator();
  
  CGAL_precondition(s1.is_valid() && s1.is_closed());
  CGAL::Nef_polyhedron_3<Kernel> nef1(s1);
  if (!nef1.is_simple()) {
    Logger::Message(Logger::LOG_ERROR, "s1: Not simple Nef?", operand1->entity);
    return false;
  }
  
  CGAL_precondition(s2.is_valid() && s2.is_closed());
  CGAL::Nef_polyhedron_3<Kernel> nef2(s2);
  if (!nef2.is_simple()) {
    Logger::Message(Logger::LOG_ERROR, "s2: Not simple Nef?", operand2->entity);
    return false;
  }
  
//  std::ofstream f1;
//  f1.open("/Users/ken/Desktop/s1.off");
//  f1 << s1 << std::endl;
//  f1.close();
//  std::ofstream f2;
//  f2.open("/Users/ken/Desktop/s2.off");
//  f2 << s2 << std::endl;
//  f2.close();
  
  if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_DIFFERENCE) {
    
//    std::cout << "Difference" << std::endl;
    CGAL::Nef_polyhedron_3<Kernel> nef_result = nef1-nef2;
    if (!nef_result.is_simple()) {
      std::cout << "Not simple: " << nef_result.number_of_volumes() << " volumes" << std::endl;
      return false;
    }
    cgal_shape_t result;
    nef_result.convert_to_polyhedron(result);
//    std::ofstream fresult;
//    fresult.open("/Users/ken/Desktop/result.off");
//    fresult << result << std::endl;
//    fresult.close();
    shape = result;
    return true;
    
  } else if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_UNION) {

//    std::cout << "Union" << std::endl;
    CGAL::Nef_polyhedron_3<Kernel> nef_result = nef1+nef2;
    if (!nef_result.is_simple()) {
      std::cout << "Not simple: " << nef_result.number_of_volumes() << " volumes" << std::endl;
      return false;
    }
    cgal_shape_t result;
    nef_result.convert_to_polyhedron(result);
//    std::ofstream fresult;
//    fresult.open("/Users/ken/Desktop/result.off");
//    fresult << result << std::endl;
//    fresult.close();
    shape = result;
    return true;
    
  } else if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_INTERSECTION) {

//    std::cout << "Intersection" << std::endl;
    CGAL::Nef_polyhedron_3<Kernel> nef_result = nef1*nef2;
    if (!nef_result.is_simple()) {
      std::cout << "Not simple: " << nef_result.number_of_volumes() << " volumes" << std::endl;
      return false;
    }
    cgal_shape_t result;
    nef_result.convert_to_polyhedron(result);
//    std::ofstream fresult;
//    fresult.open("/Users/ken/Desktop/result.off");
//    fresult << result << std::endl;
//    fresult.close();
    shape = result;
    return true;
    
  }
  
  return false;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcSphere* l, cgal_shape_t& shape) {
  const double r = l->Radius() * getValue(GV_LENGTH_UNIT);
  
  // Make icosahedron
  float golden_ratio = (1.0+sqrtf(5.0))/2.0;
  float normalising_factor = sqrtf(golden_ratio*golden_ratio+1.0);
  std::vector<Kernel::Point_3> icosahedron_vertices;
  icosahedron_vertices.push_back(Kernel::Point_3(-1.0/normalising_factor,  golden_ratio/normalising_factor, 0.0));
  icosahedron_vertices.push_back(Kernel::Point_3( 1.0/normalising_factor,  golden_ratio/normalising_factor, 0.0));
  icosahedron_vertices.push_back(Kernel::Point_3(-1.0/normalising_factor, -golden_ratio/normalising_factor, 0.0));
  icosahedron_vertices.push_back(Kernel::Point_3( 1.0/normalising_factor, -golden_ratio/normalising_factor, 0.0));
  icosahedron_vertices.push_back(Kernel::Point_3(0.0, -1.0/normalising_factor,  golden_ratio/normalising_factor));
  icosahedron_vertices.push_back(Kernel::Point_3(0.0,  1.0/normalising_factor,  golden_ratio/normalising_factor));
  icosahedron_vertices.push_back(Kernel::Point_3(0.0, -1.0/normalising_factor, -golden_ratio/normalising_factor));
  icosahedron_vertices.push_back(Kernel::Point_3(0.0,  1.0/normalising_factor, -golden_ratio/normalising_factor));
  icosahedron_vertices.push_back(Kernel::Point_3( golden_ratio/normalising_factor, 0.0, -1.0/normalising_factor));
  icosahedron_vertices.push_back(Kernel::Point_3( golden_ratio/normalising_factor, 0.0,  1.0/normalising_factor));
  icosahedron_vertices.push_back(Kernel::Point_3(-golden_ratio/normalising_factor, 0.0, -1.0/normalising_factor));
  icosahedron_vertices.push_back(Kernel::Point_3(-golden_ratio/normalising_factor, 0.0,  1.0/normalising_factor));
  
  std::list<cgal_face_t> face_list;
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[0]);
  face_list.back().outer.push_back(icosahedron_vertices[11]);
  face_list.back().outer.push_back(icosahedron_vertices[5]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[0]);
  face_list.back().outer.push_back(icosahedron_vertices[5]);
  face_list.back().outer.push_back(icosahedron_vertices[1]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[0]);
  face_list.back().outer.push_back(icosahedron_vertices[1]);
  face_list.back().outer.push_back(icosahedron_vertices[7]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[0]);
  face_list.back().outer.push_back(icosahedron_vertices[7]);
  face_list.back().outer.push_back(icosahedron_vertices[10]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[0]);
  face_list.back().outer.push_back(icosahedron_vertices[10]);
  face_list.back().outer.push_back(icosahedron_vertices[11]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[1]);
  face_list.back().outer.push_back(icosahedron_vertices[5]);
  face_list.back().outer.push_back(icosahedron_vertices[9]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[5]);
  face_list.back().outer.push_back(icosahedron_vertices[11]);
  face_list.back().outer.push_back(icosahedron_vertices[4]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[11]);
  face_list.back().outer.push_back(icosahedron_vertices[10]);
  face_list.back().outer.push_back(icosahedron_vertices[2]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[10]);
  face_list.back().outer.push_back(icosahedron_vertices[7]);
  face_list.back().outer.push_back(icosahedron_vertices[6]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[7]);
  face_list.back().outer.push_back(icosahedron_vertices[1]);
  face_list.back().outer.push_back(icosahedron_vertices[8]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[3]);
  face_list.back().outer.push_back(icosahedron_vertices[9]);
  face_list.back().outer.push_back(icosahedron_vertices[4]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[3]);
  face_list.back().outer.push_back(icosahedron_vertices[4]);
  face_list.back().outer.push_back(icosahedron_vertices[2]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[3]);
  face_list.back().outer.push_back(icosahedron_vertices[2]);
  face_list.back().outer.push_back(icosahedron_vertices[6]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[3]);
  face_list.back().outer.push_back(icosahedron_vertices[6]);
  face_list.back().outer.push_back(icosahedron_vertices[8]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[3]);
  face_list.back().outer.push_back(icosahedron_vertices[8]);
  face_list.back().outer.push_back(icosahedron_vertices[9]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[4]);
  face_list.back().outer.push_back(icosahedron_vertices[9]);
  face_list.back().outer.push_back(icosahedron_vertices[5]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[2]);
  face_list.back().outer.push_back(icosahedron_vertices[4]);
  face_list.back().outer.push_back(icosahedron_vertices[11]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[6]);
  face_list.back().outer.push_back(icosahedron_vertices[2]);
  face_list.back().outer.push_back(icosahedron_vertices[10]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[8]);
  face_list.back().outer.push_back(icosahedron_vertices[6]);
  face_list.back().outer.push_back(icosahedron_vertices[7]);
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(icosahedron_vertices[9]);
  face_list.back().outer.push_back(icosahedron_vertices[8]);
  face_list.back().outer.push_back(icosahedron_vertices[1]);
  
  const unsigned int refinements = 2;
  for (unsigned int current_refinement = 0; current_refinement < refinements; ++current_refinement) {
    std::list<cgal_face_t> refined_face_list;
    for (auto &face: face_list) {
      Kernel::Point_3 vertex0 = face.outer[0];
      Kernel::Point_3 vertex1 = face.outer[1];
      Kernel::Point_3 vertex2 = face.outer[2];
      
      Kernel::Point_3 midpoint01 = CGAL::midpoint(vertex0, vertex1);
      Kernel::Point_3 midpoint12 = CGAL::midpoint(vertex1, vertex2);
      Kernel::Point_3 midpoint20 = CGAL::midpoint(vertex2, vertex0);
      
      double midpoint01_distance_to_origin = sqrt(CGAL::to_double(CGAL::squared_distance(midpoint01, Kernel::Point_3(0, 0, 0))));
      midpoint01 = Kernel::Point_3(midpoint01.x()/midpoint01_distance_to_origin,
                                   midpoint01.y()/midpoint01_distance_to_origin,
                                   midpoint01.z()/midpoint01_distance_to_origin);
      double midpoint12_distance_to_origin = sqrt(CGAL::to_double(CGAL::squared_distance(midpoint12, Kernel::Point_3(0, 0, 0))));
      midpoint12 = Kernel::Point_3(midpoint12.x()/midpoint12_distance_to_origin,
                                   midpoint12.y()/midpoint12_distance_to_origin,
                                   midpoint12.z()/midpoint12_distance_to_origin);
      double midpoint20_distance_to_origin = sqrt(CGAL::to_double(CGAL::squared_distance(midpoint20, Kernel::Point_3(0, 0, 0))));
      midpoint20 = Kernel::Point_3(midpoint20.x()/midpoint20_distance_to_origin,
                                   midpoint20.y()/midpoint20_distance_to_origin,
                                   midpoint20.z()/midpoint20_distance_to_origin);
      
      refined_face_list.push_back(cgal_face_t());
      refined_face_list.back().outer.push_back(vertex0);
      refined_face_list.back().outer.push_back(midpoint01);
      refined_face_list.back().outer.push_back(midpoint20);
      
      refined_face_list.push_back(cgal_face_t());
      refined_face_list.back().outer.push_back(vertex1);
      refined_face_list.back().outer.push_back(midpoint12);
      refined_face_list.back().outer.push_back(midpoint01);
      
      refined_face_list.push_back(cgal_face_t());
      refined_face_list.back().outer.push_back(vertex2);
      refined_face_list.back().outer.push_back(midpoint20);
      refined_face_list.back().outer.push_back(midpoint12);
      
      refined_face_list.push_back(cgal_face_t());
      refined_face_list.back().outer.push_back(midpoint01);
      refined_face_list.back().outer.push_back(midpoint12);
      refined_face_list.back().outer.push_back(midpoint20);
    } face_list = refined_face_list;
  }
  
  // Naive creation
  cgal_shape_t polyhedron = CGAL::Polyhedron_3<Kernel>();
  PolyhedronBuilder builder(&face_list);
  polyhedron.delegate(builder);
  
//  std::ofstream fresult;
//  fresult.open("/Users/ken/Desktop/sphere.off");
//  fresult << polyhedron << std::endl;
//  fresult.close();
  
  // Stitch edges
  //  std::cout << "Before: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
  CGAL::Polygon_mesh_processing::stitch_borders(polyhedron);
  if (!CGAL::Polygon_mesh_processing::is_outward_oriented(polyhedron)) {
    CGAL::Polygon_mesh_processing::reverse_face_orientations(polyhedron);
  } CGAL_postcondition(polyhedron.is_valid() && polyhedron.is_closed());
  //  std::cout << "After: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
  
  cgal_placement_t trsf;
  IfcGeom::CgalKernel::convert(l->Position(),trsf);
  
  for (auto &vertex: vertices(polyhedron)) {
    vertex->point() = Kernel::Point_3(vertex->point().x()*r,
                                      vertex->point().y()*r,
                                      vertex->point().z()*r).transform(trsf);
  }
  
//  std::ofstream fresult;
//  fresult.open("/Users/ken/Desktop/sphere.off");
//  fresult << polyhedron << std::endl;
//  fresult.close();
  
  shape = polyhedron;
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcRectangularPyramid* l, cgal_shape_t& shape) {
  const double dx = l->XLength() * getValue(GV_LENGTH_UNIT);
  const double dy = l->YLength() * getValue(GV_LENGTH_UNIT);
  const double dz = l->Height() * getValue(GV_LENGTH_UNIT);
  
  std::list<cgal_face_t> face_list;
  
  // Base
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(Kernel::Point_3(0, 0, 0));
  face_list.back().outer.push_back(Kernel::Point_3(dx, 0, 0));
  face_list.back().outer.push_back(Kernel::Point_3(dx, dy, 0));
  face_list.back().outer.push_back(Kernel::Point_3(0, dy, 0));
  
  // Lateral faces
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(Kernel::Point_3(0, 0, 0));
  face_list.back().outer.push_back(Kernel::Point_3(0, dy, 0));
  face_list.back().outer.push_back(Kernel::Point_3(0.5*dx, 0.5*dy, dz));
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(Kernel::Point_3(0, dy, 0));
  face_list.back().outer.push_back(Kernel::Point_3(dx, dy, 0));
  face_list.back().outer.push_back(Kernel::Point_3(0.5*dx, 0.5*dy, dz));
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(Kernel::Point_3(dx, dy, 0));
  face_list.back().outer.push_back(Kernel::Point_3(dx, 0, 0));
  face_list.back().outer.push_back(Kernel::Point_3(0.5*dx, 0.5*dy, dz));
  
  face_list.push_back(cgal_face_t());
  face_list.back().outer.push_back(Kernel::Point_3(dx, 0, 0));
  face_list.back().outer.push_back(Kernel::Point_3(0, 0, 0));
  face_list.back().outer.push_back(Kernel::Point_3(0.5*dx, 0.5*dy, dz));
  
  // Naive creation
  cgal_shape_t polyhedron = CGAL::Polyhedron_3<Kernel>();
  PolyhedronBuilder builder(&face_list);
  polyhedron.delegate(builder);
  
  // Stitch edges
  //  std::cout << "Before: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
  CGAL::Polygon_mesh_processing::stitch_borders(polyhedron);
  if (!CGAL::Polygon_mesh_processing::is_outward_oriented(polyhedron)) {
    CGAL::Polygon_mesh_processing::reverse_face_orientations(polyhedron);
  } CGAL_postcondition(polyhedron.is_valid() && polyhedron.is_closed());
  //  std::cout << "After: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
  
  cgal_placement_t trsf;
  IfcGeom::CgalKernel::convert(l->Position(),trsf);
  
  for (auto &vertex: vertices(polyhedron)) {
    vertex->point() = vertex->point().transform(trsf);
  }
  
  shape = polyhedron;
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcRightCircularCylinder* l, cgal_shape_t& shape) {
  const double r = l->Radius() * getValue(GV_LENGTH_UNIT);
  const double h = l->Height() * getValue(GV_LENGTH_UNIT);
  
  std::list<cgal_face_t> face_list;
  
  const int segments = 12;
  
  // Base
  face_list.push_back(cgal_face_t());
  for (int current_segment = 0; current_segment < segments; ++current_segment) {
    double current_angle = current_segment*2.0*3.141592653589793/((double)segments);
    face_list.back().outer.push_back(Kernel::Point_3(r*cos(current_angle), r*sin(current_angle), 0));
  }
  
  // Side faces
  for (int current_segment = 0; current_segment < segments; ++current_segment) {
    double current_angle = current_segment*2.0*3.141592653589793/((double)segments);
    int next_segment = (current_segment+1)%segments;
    double next_angle = next_segment*2.0*3.141592653589793/((double)segments);
    face_list.push_back(cgal_face_t());
    face_list.back().outer.push_back(Kernel::Point_3(r*cos(next_angle), r*sin(next_angle), 0));
    face_list.back().outer.push_back(Kernel::Point_3(r*cos(current_angle), r*sin(current_angle), 0));
    face_list.back().outer.push_back(Kernel::Point_3(r*cos(current_angle), r*sin(current_angle), h));
    face_list.back().outer.push_back(Kernel::Point_3(r*cos(next_angle), r*sin(next_angle), h));
  }
  
  // Top
  face_list.push_back(cgal_face_t());
  for (int current_segment = segments-1; current_segment >= 0; --current_segment) {
    double current_angle = current_segment*2.0*3.141592653589793/((double)segments);
    face_list.back().outer.push_back(Kernel::Point_3(r*cos(current_angle), r*sin(current_angle), h));
  }
  
  // Naive creation
  cgal_shape_t polyhedron = CGAL::Polyhedron_3<Kernel>();
  PolyhedronBuilder builder(&face_list);
  polyhedron.delegate(builder);
  
  // Stitch edges
  //  std::cout << "Before: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
  CGAL::Polygon_mesh_processing::stitch_borders(polyhedron);
  if (!CGAL::Polygon_mesh_processing::is_outward_oriented(polyhedron)) {
    CGAL::Polygon_mesh_processing::reverse_face_orientations(polyhedron);
  } CGAL_postcondition(polyhedron.is_valid() && polyhedron.is_closed());
  //  std::cout << "After: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
  
  cgal_placement_t trsf;
  IfcGeom::CgalKernel::convert(l->Position(),trsf);
  
  for (auto &vertex: vertices(polyhedron)) {
    vertex->point() = vertex->point().transform(trsf);
  }
  
  shape = polyhedron;
  return true;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcRightCircularCone* l, cgal_shape_t& shape) {
  const double r = l->BottomRadius() * getValue(GV_LENGTH_UNIT);
  const double h = l->Height() * getValue(GV_LENGTH_UNIT);
  
  std::list<cgal_face_t> face_list;
  
  const int segments = 12;
  
  // Base
  face_list.push_back(cgal_face_t());
  for (int current_segment = 0; current_segment < segments; ++current_segment) {
    double current_angle = current_segment*2.0*3.141592653589793/((double)segments);
    face_list.back().outer.push_back(Kernel::Point_3(r*cos(current_angle), r*sin(current_angle), 0));
  }
  
  // Side faces
  for (int current_segment = 0; current_segment < segments; ++current_segment) {
    double current_angle = current_segment*2.0*3.141592653589793/((double)segments);
    int next_segment = (current_segment+1)%segments;
    double next_angle = next_segment*2.0*3.141592653589793/((double)segments);
    face_list.push_back(cgal_face_t());
    face_list.back().outer.push_back(Kernel::Point_3(r*cos(next_angle), r*sin(next_angle), 0));
    face_list.back().outer.push_back(Kernel::Point_3(r*cos(current_angle), r*sin(current_angle), 0));
    face_list.back().outer.push_back(Kernel::Point_3(0, 0, h));
  }
  
  // Naive creation
  cgal_shape_t polyhedron = CGAL::Polyhedron_3<Kernel>();
  PolyhedronBuilder builder(&face_list);
  polyhedron.delegate(builder);
  
  // Stitch edges
  //  std::cout << "Before: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
  CGAL::Polygon_mesh_processing::stitch_borders(polyhedron);
  if (!CGAL::Polygon_mesh_processing::is_outward_oriented(polyhedron)) {
    CGAL::Polygon_mesh_processing::reverse_face_orientations(polyhedron);
  } CGAL_postcondition(polyhedron.is_valid() && polyhedron.is_closed());
  //  std::cout << "After: " << polyhedron.size_of_vertices() << " vertices and " << polyhedron.size_of_facets() << " facets" << std::endl;
  
  cgal_placement_t trsf;
  IfcGeom::CgalKernel::convert(l->Position(),trsf);
  
  for (auto &vertex: vertices(polyhedron)) {
    vertex->point() = vertex->point().transform(trsf);
  }
  
  shape = polyhedron;
  return true;
}
