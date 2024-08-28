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

 /********************************************************************************
  *                                                                              *
  * Implementations of the various conversion functions defined in IfcGeom.h     *
  *                                                                              *
  ********************************************************************************/

// #include <set>
// #include <algorithm>
// #include <numeric>
// 
// #include <Standard_Version.hxx>
// 
// #include <gp_Pnt.hxx>
// #include <gp_Vec.hxx>
// #include <gp_Dir.hxx>
// #include <gp_Pnt2d.hxx>
// #include <gp_GTrsf.hxx>
// #include <gp_GTrsf2d.hxx>
// #include <gp_Trsf.hxx>
// #include <gp_Trsf2d.hxx>
// #include <gp_Ax3.hxx>
// #include <gp_Pln.hxx>
// 
// #include <Geom_Line.hxx>
// #include <Geom_Circle.hxx>
// 
// #include <Geom_Plane.hxx>
// #include <Geom_OffsetCurve.hxx>
// #include <Geom_OffsetSurface.hxx>
// #include <Geom_CylindricalSurface.hxx>
// #include <Geom_SurfaceOfLinearExtrusion.hxx>
// 
// #include <GeomAPI_IntCS.hxx>
// #include <GeomAPI_IntSS.hxx>
// 
// #include <BRepBndLib.hxx>
// #include <BRepOffsetAPI_Sewing.hxx>
// #include <BRepBuilderAPI_MakeFace.hxx>
// #include <BRepBuilderAPI_MakeEdge.hxx>
// #include <BRepBuilderAPI_MakeWire.hxx>
// #include <BRepBuilderAPI_MakePolygon.hxx>
// #include <BRepBuilderAPI_MakeVertex.hxx>
// 
// #include <TopoDS.hxx>
// #include <TopoDS_Wire.hxx>
// #include <TopoDS_Face.hxx>
// #include <TopoDS_CompSolid.hxx>
// 
// #include <TopExp.hxx>
// #include <TopExp_Explorer.hxx>
// 
// #include <BRepPrimAPI_MakePrism.hxx>
// #include <BRepBuilderAPI_MakeShell.hxx>
// #include <BRepBuilderAPI_MakeSolid.hxx>
// #include <BRepPrimAPI_MakeHalfSpace.hxx>
// #include <BRepAlgoAPI_Cut.hxx>
// #include <BRepAlgoAPI_Fuse.hxx>
// #include <BRepAlgoAPI_Common.hxx>
// #include <BRepAlgoAPI_BooleanOperation.hxx>
// #if OCC_VERSION_HEX >= 0x70200
// #include <BRepAlgoAPI_Splitter.hxx>
// #endif
// 
// #include <BRepAlgo_NormalProjection.hxx>
// 
// #include <ShapeFix_Shape.hxx>
// #include <ShapeFix_ShapeTolerance.hxx>
// #include <ShapeFix_Solid.hxx>
// #include <ShapeFix_Shell.hxx>
// 
// #include <ShapeAnalysis_Curve.hxx>
// #include <ShapeAnalysis_Surface.hxx>
// 
// 
// #include <BRepFilletAPI_MakeFillet2d.hxx>
// 
// #include <TopLoc_Location.hxx>
// 
// #include <GProp_GProps.hxx>
// #include <BRepGProp.hxx>
// 
// #include <BRepBuilderAPI_Transform.hxx>
// #include <BRepBuilderAPI_GTransform.hxx>
// 
// #include <BRepGProp_Face.hxx>
// #include <BRepCheck.hxx>
// #include <BRepCheck_Analyzer.hxx>
// 
// #include <BRepMesh_IncrementalMesh.hxx>
// #include <BRepTools.hxx>
// #include <BRepTools_WireExplorer.hxx>
// 
// #include <Poly_Triangulation.hxx>
// #include <Poly_Array1OfTriangle.hxx>
// 
// #include <TopTools_IndexedMapOfShape.hxx>
// #include <TopTools_IndexedDataMapOfShapeListOfShape.hxx>
// 
// #include <BOPAlgo_PaveFiller.hxx>
// 
// #include <GCPnts_AbscissaPoint.hxx>
// 
// #include <BRepClass3d_SolidClassifier.hxx>
// 
// #include <GeomAPI_ExtremaCurveCurve.hxx>
// 
// #include <Extrema_ExtCS.hxx>
// 
// #include <ShapeAnalysis_Edge.hxx>
// 
// #if OCC_VERSION_HEX >= 0x70200
// #include <BOPAlgo_Alerts.hxx>
// #endif
// 
// #include "../../../ifcparse/macros.h"
// #include "../../../ifcparse/IfcSIPrefix.h"
// 
// #include "../../../ifcparse/IfcFile.h"
// 

#include "OpenCascadeKernel.h"

// #include "IfcGeomTree.h"

#include "boolean_utils.h"

// #include "wire_utils.h"

#include "base_utils.h"

// #include "layerset.h"
// 
// #include <memory>
// #include <thread>
// 
// #if OCC_VERSION_HEX < 0x60900
// #ifdef _MSC_VER
// #pragma message("warning: You are linking against Open CASCADE version " OCC_VERSION_COMPLETE ". Version 6.9.0 introduces various improvements with relation to boolean operations. You are advised to upgrade.")
// #else
// #warning "You are linking against an older version of Open CASCADE. Version 6.9.0 introduces various improvements with relation to boolean operations. You are advised to upgrade."
// #endif
// #endif
// 
// namespace {
// 	struct POSTFIX_SCHEMA(factory_t) {
// 		IfcGeom::Kernel* operator()(IfcParse::IfcFile* file) const {
// 			IfcGeom::POSTFIX_SCHEMA(Kernel)* k = new IfcGeom::POSTFIX_SCHEMA(Kernel);
// 			if (file) {
// 
// 			}
// 			return k;
// 		}
// 	};
// }
// 
// void MAKE_INIT_FN(KernelImplementation_)(IfcGeom::impl::KernelFactoryImplementation* mapping) {
// 	static const std::string schema_name = STRINGIFY(IfcSchema);
// 	POSTFIX_SCHEMA(factory_t) factory;
// 	mapping->bind(schema_name, factory);
// }
// 
// #define Kernel POSTFIX_SCHEMA(Kernel)
// 
// void IfcGeom::Kernel::set_offset(const std::array<double, 3> &p_offset) {
// 	offset = gp_Vec(p_offset[0], p_offset[1], p_offset[2]);
// 
// 	offset_and_rotation = util::combine_offset_and_rotation(offset, rotation);
// }
// 
// void IfcGeom::Kernel::set_rotation(const std::array<double, 4> &p_rotation) {
// 	rotation = gp_Quaternion(p_rotation[0], p_rotation[1], p_rotation[2], p_rotation[3]);
// 
// 	offset_and_rotation = util::combine_offset_and_rotation(offset, rotation);
// }
// 

namespace {
	struct opening_sorter {
		bool operator()(const std::pair<double, TopoDS_Shape>& a, const std::pair<double, TopoDS_Shape>& b) const {
			return a.first > b.first;
		}
	};
}

using namespace ifcopenshell::geometry;

bool IfcGeom::OpenCascadeKernel::convert_openings(const IfcUtil::IfcBaseEntity* entity, const std::vector<std::pair<taxonomy::ptr, ifcopenshell::geometry::taxonomy::matrix4>>& openings,
	const IfcGeom::ConversionResults& entity_shapes, const ifcopenshell::geometry::taxonomy::matrix4& entity_trsf, IfcGeom::ConversionResults& cut_shapes) {

	util::boolean_settings bst;
	bst.attempt_2d = settings_.get<settings::BooleanAttempt2d>().get();
	bst.debug = settings_.get<settings::DebugBooleanOperations>().get();
	bst.precision = settings_.get<settings::Precision>().get();

	std::vector< std::pair<double, TopoDS_Shape> > opening_vector;

	for (auto& op : openings) {
		/*
		// Not yet implemented and tested, process opening placement up to parent wall
		// placement so that the matrix inverse can be eliminated.
		// @todo property check and handle the decomposition into parts (where element
		// carying geom and opening are in different branches).
		// @todo properly check whether opening correctly references wall placement
		// and fallback to matrix inverse when not the case.
		auto relative = entity;
		{
			auto ds = relative->Decomposes();
			if (ds->size() == 1) {
				relative = (*ds->begin())->RelatingObject()->as<IfcSchema::IfcProduct>();
			}
		}
		set_conversion_placement_rel_to_instance(relative);
		*/

		// Convert the IfcRepresentation of the IfcOpeningElement
		auto opening_trsf = op.second;

		// set_conversion_placement_rel_to_instance(nullptr);

		// Move the opening into the coordinate system of the IfcProduct

		// @todo
		Eigen::Matrix4d relative = entity_trsf.ccomponents().inverse() * opening_trsf.ccomponents();
		// opening_trsf = relative;

		IfcGeom::ConversionResults opening_shapes;
		
		// @todo
		AbstractKernel::convert(op.first, opening_shapes);

		for (unsigned int i = 0; i < opening_shapes.size(); ++i) {
			auto opening_shape_i = std::static_pointer_cast<OpenCascadeShape>(opening_shapes[i].Shape())->shape();
			const TopoDS_Shape& opening_shape_unlocated = util::ensure_fit_for_subtraction(opening_shape_i, settings_.get<settings::Precision>().get());

			auto gtrsf = opening_shapes[i].Placement();
			// @todo check
			Eigen::Matrix4d m = relative * gtrsf->ccomponents();
			gp_Trsf trsf;
			trsf.SetValues(
				m(0, 0), m(0, 1), m(0, 2), m(0, 3),
				m(1, 0), m(1, 1), m(1, 2), m(1, 3),
				m(2, 0), m(2, 1), m(2, 2), m(2, 3)
			);
			TopoDS_Shape opening_shape = util::apply_transformation(opening_shape_unlocated, trsf);
			opening_vector.push_back(std::make_pair(util::min_edge_length(opening_shape), opening_shape));
		}

	}

	std::sort(opening_vector.begin(), opening_vector.end(), opening_sorter());

	// Iterate over the shapes of the IfcProduct
	for (IfcGeom::ConversionResults::const_iterator it3 = entity_shapes.begin(); it3 != entity_shapes.end(); ++it3) {

		TopoDS_Compound C;
		BRep_Builder B;
		B.MakeCompound(C);
		TopoDS_Shape combined_result;

		std::list<TopoDS_Shape> parts;

		auto it3_shape = std::static_pointer_cast<OpenCascadeShape>(it3->Shape())->shape();
		if (it3_shape.IsNull()) {
			Logger::Error("Null operand");
			continue;
		}

		bool is_multiple = it3_shape.ShapeType() == TopAbs_COMPOUND && TopoDS_Iterator(it3_shape).More() && util::is_nested_compound_of_solid(it3_shape);

		if (is_multiple) {
			TopoDS_Iterator sit(it3_shape);
			for (; sit.More(); sit.Next()) {
				parts.push_back(sit.Value());
			}
		} else {
			parts.push_back(it3_shape);
		}

		for (auto& entity_part : parts) {
			bool is_manifold = util::is_manifold(entity_part);

			if (!is_manifold) {
				Logger::Warning("Non-manifold first operand");
			}

			TopoDS_Shape entity_part_result;

			for (int as_shell = 0; as_shell < 2; ++as_shell) {
				TopoDS_Shape entity_shape_unlocated;
				if (as_shell) {
					entity_shape_unlocated = entity_part;
				} else {
					entity_shape_unlocated = util::ensure_fit_for_subtraction(entity_part, settings_.get<settings::Precision>().get());
				}
				const auto& m = it3->Placement()->ccomponents();
				// @todo
				// if (entity_shape_gtrsf.Form() == gp_Other) {
				// 	Logger::Message(Logger::LOG_WARNING, "Applying non uniform transformation to:", entity);
				// }
				gp_Trsf entity_shape_gtrsf;
				entity_shape_gtrsf.SetValues(
					m(0, 0), m(0, 1), m(0, 2), m(0, 3),
					m(1, 0), m(1, 1), m(1, 2), m(1, 3),
					m(2, 0), m(2, 1), m(2, 2), m(2, 3)
				);
				TopoDS_Shape entity_shape = util::apply_transformation(entity_shape_unlocated, entity_shape_gtrsf);

				TopoDS_Shape result = entity_shape;

				auto it = opening_vector.begin();
				auto jt = it;

				for (;; ++it) {
					if (it == opening_vector.end() || jt->first / it->first > 10.) {

						TopTools_ListOfShape opening_list;
						for (auto kt = jt; kt < it; ++kt) {
							opening_list.Append(kt->second);
						}

						TopoDS_Shape intermediate_result;
						if (util::boolean_operation(bst, result, opening_list, BOPAlgo_CUT, intermediate_result)) {
							result = intermediate_result;
						} else {
							Logger::Message(Logger::LOG_ERROR, "Opening subtraction failed for " + boost::lexical_cast<std::string>(std::distance(jt, it)) + " openings", entity);
						}

						jt = it;
					}

					if (it == opening_vector.end()) {
						break;
					}
				}

				int result_n_faces = util::count(result, TopAbs_FACE);

				if (!is_manifold && as_shell == 0 && result_n_faces == 0) {
					// If we have a non-manifold first operand and our first attempt
					// on a Solid-Solid subtraction yielded a empty result (no faces)
					// or a strange result, a larger number of faces with the original input
					// included. Then retry (another iteration on the for-loop on as-shell)
					// where we keep the first operand as is (a compound of faces probably,
					// unless --orient-shells was activated in which case we're already lost).
					if (!is_manifold) {
						Logger::Warning("Retrying boolean operation on individual faces");
					}
					continue;
				}

				entity_part_result = result;

				// For manifold first operands we're not even going to try if processing
				// as loose faces gives a better result.
				break;
			}

			if (is_multiple) {
				B.Add(C, entity_part_result);
			} else {
				combined_result = entity_part_result;
			}

		}

		if (is_multiple) {
			combined_result = C;
		}

		cut_shapes.push_back(IfcGeom::ConversionResult(it3->ItemId(), new OpenCascadeShape(combined_result), it3->StylePtr()));
	}
	return true;
}

#include <BRepPrimAPI_MakeRevol.hxx>

bool IfcGeom::OpenCascadeKernel::convert_impl(const taxonomy::revolve::ptr r, IfcGeom::ConversionResults& results) {


	gp_Ax1 ax(
		convert_xyz<gp_Pnt>(*r->axis_origin),
		convert_xyz<gp_Dir>(*r->direction));

	TopoDS_Shape face;
	if (!convert(taxonomy::cast<taxonomy::face>(r->basis), face)) {
		return false;
	}

	TopoDS_Shape shape = BRepPrimAPI_MakeRevol(face, ax);

	results.emplace_back(ConversionResult(
		r->instance->as<IfcUtil::IfcBaseEntity>()->id(),
		r->matrix,
		new OpenCascadeShape(shape),
		r->surface_style
	));
	return true;
}

// IfcSchema::IfcRelVoidsElement::list::ptr IfcGeom::Kernel::find_openings(IfcSchema::IfcProduct* product) {
// 	std::vector<IfcSchema::IfcRelVoidsElement*> rs;
// 
// 	if (product->declaration().is(IfcSchema::IfcElement::Class()) && !product->declaration().is(IfcSchema::IfcOpeningElement::Class())) {
// 		IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)product;
// 		auto rels = element->HasOpenings();
// 		rs.insert(rs.end(), rels->begin(), rels->end());
// 	}
// 
// 	// Is the IfcElement a decomposition of an IfcElement with any IfcOpeningElements?
// 	IfcSchema::IfcObjectDefinition* obdef = product->as<IfcSchema::IfcObjectDefinition>();
// 	for (;;) {
// 		auto decomposes = obdef->Decomposes();
// 		if (decomposes->size() != 1) break;
// 		IfcSchema::IfcObjectDefinition* rel_obdef = (*decomposes->begin())->RelatingObject();
// 		if (rel_obdef->declaration().is(IfcSchema::IfcElement::Class()) && !rel_obdef->declaration().is(IfcSchema::IfcOpeningElement::Class())) {
// 			IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)rel_obdef;
// 			auto rels = element->HasOpenings();
// 			rs.insert(rs.end(), rels->begin(), rels->end());
// 		}
// 
// 		obdef = rel_obdef;
// 	}
// 
// 	// Filter openings in Reference view, solely marked as Reference.
// 	IfcSchema::IfcRelVoidsElement::list::ptr openings(new IfcSchema::IfcRelVoidsElement::list);
// 	std::for_each(rs.begin(), rs.end(), [&openings](IfcSchema::IfcRelVoidsElement* rel) {
// 		if (rel->RelatedOpeningElement()->ObjectPlacement() && rel->RelatedOpeningElement()->Representation()) {
// 			auto reps = rel->RelatedOpeningElement()->Representation()->Representations();
// 			if (!(reps->size() == 1 && (*reps->begin())->RepresentationIdentifier().get_value_or("") == "Reference")) {
// 				openings->push(rel);
// 			}
// 		}
// 	});
// 
// 	return openings;
// }
// 
// const IfcSchema::IfcMaterial* IfcGeom::Kernel::get_single_material_association(const IfcSchema::IfcProduct* product) {
// 	IfcSchema::IfcMaterial* single_material = 0;
// 	IfcSchema::IfcRelAssociatesMaterial::list::ptr associated_materials = product->HasAssociations()->as<IfcSchema::IfcRelAssociatesMaterial>();
// 	if (associated_materials->size() == 1) {
// 		IfcSchema::IfcMaterialSelect* associated_material = (*associated_materials->begin())->RelatingMaterial();
// 		single_material = associated_material->as<IfcSchema::IfcMaterial>();
// 
// 		// NB: IfcMaterialLayerSets are also considered, regardless of --enable-layerset-slicing. Picking
// 		// the first material (in accordance with other viewers) when layerset-slicing is disabled.
// 		if (!single_material && associated_material->as<IfcSchema::IfcMaterialLayerSetUsage>()) {
// 			IfcSchema::IfcMaterialLayerSet* layerset = associated_material->as<IfcSchema::IfcMaterialLayerSetUsage>()->ForLayerSet();
// 			if (getValue(GV_LAYERSET_FIRST) > 0.0 ? layerset->MaterialLayers()->size() >= 1 : layerset->MaterialLayers()->size() == 1) {
// 				IfcSchema::IfcMaterialLayer* layer = (*layerset->MaterialLayers()->begin());
// 				if (layer->Material()) {
// 					single_material = layer->Material();
// 				}
// 			}
// 		}
// 	}
// 	return single_material;
// }
// 
// IfcGeom::BRepElement* IfcGeom::Kernel::create_brep_for_representation_and_product(
// 	const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product)
// {
// 	std::stringstream representation_id_builder;
// 
// 	representation_id_builder << representation->data().id();
// 
// 	IfcGeom::Representation::BRep* shape;
// 	IfcGeom::ConversionResults shapes, shapes2;
// 
// 	if (!convert_shapes(representation, shapes)) {
// 		return 0;
// 	}
// 
// 	if (settings.get(IteratorSettings::APPLY_LAYERSETS)) {
// 		TopoDS_Shape merge;
// 		if (util::flatten_shape_list(shapes, merge, false, getValue(GV_PRECISION))) {
// 			if (util::count(merge, TopAbs_FACE) > 0) {
// 				std::vector<double> thickness;
// 				std::vector<Handle_Geom_Surface> layers;
// 				std::vector< std::vector<Handle_Geom_Surface> > folded_layers;
// 				std::vector<std::shared_ptr<const SurfaceStyle>> styles;
// 				if (convert_layerset(product, layers, styles, thickness)) {
// 
// 					IfcSchema::IfcRelAssociates::list::ptr associations = product->HasAssociations();
// 					for (IfcSchema::IfcRelAssociates::list::it it = associations->begin(); it != associations->end(); ++it) {
// 						IfcSchema::IfcRelAssociatesMaterial* associates_material = (**it).as<IfcSchema::IfcRelAssociatesMaterial>();
// 						if (associates_material) {
// 							unsigned layerset_id = associates_material->RelatingMaterial()->data().id();
// 							representation_id_builder << "-layerset-" << layerset_id;
// 							break;
// 						}
// 					}
// 
// 					if (styles.size() > 1) {
// 						// If there's only a single layer there is no need to manipulate geometries.
// 						bool success = true;
// 						if (product->as<IfcSchema::IfcWall>() && fold_layers(product->as<IfcSchema::IfcWall>(), shapes, layers, thickness, folded_layers)) {
// 							if (util::apply_folded_layerset(shapes, folded_layers, styles, shapes2, getValue(GV_PRECISION))) {
// 								std::swap(shapes, shapes2);
// 								success = true;
// 							}
// 						} else {
// 							if (util::apply_layerset(shapes, layers, styles, shapes2, getValue(GV_PRECISION))) {
// 								std::swap(shapes, shapes2);
// 								success = true;
// 							}
// 						}
// 
// 						if (!success) {
// 							Logger::Error("Failed processing layerset");
// 						}
// 					}
// 				}
// 			}
// 		}
// 	}
// 
// 	bool material_style_applied = false;
// 
// 	const IfcSchema::IfcMaterial* single_material = get_single_material_association(product);
// 	if (single_material) {
// 		auto s = get_style(single_material);
// 		for (IfcGeom::ConversionResults::iterator it = shapes.begin(); it != shapes.end(); ++it) {
// 			if (!it->hasStyle() && s) {
// 				it->setStyle(s);
// 				material_style_applied = true;
// 			}
// 		}
// 	} else {
// 		bool some_items_without_style = false;
// 		for (IfcGeom::ConversionResults::iterator it = shapes.begin(); it != shapes.end(); ++it) {
// 			if (!it->hasStyle() && util::count(it->Shape(), TopAbs_FACE)) {
// 				some_items_without_style = true;
// 				break;
// 			}
// 		}
// 		if (some_items_without_style) {
// 			Logger::Warning("No material and surface styles for:", product);
// 		}
// 	}
// 
// 	if (material_style_applied) {
// 		representation_id_builder << "-material-" << single_material->data().id();
// 	}
// 
// 	if (settings.force_space_transparency() >= 0. && product->declaration().is("IfcSpace")) {
// 		for (auto& s : shapes) {
// 			if (s.hasStyle()) {
// 				for (auto& p : style_cache) {
// 					if (p.second == s.StylePtr()) {
// 						std::const_pointer_cast<IfcGeom::SurfaceStyle>(p.second)->Transparency() = settings.force_space_transparency();
// 					}
// 				}
// 			}
// 		}
// 	}
// 
// 	int parent_id = -1;
// 	try {
// 		IfcUtil::IfcBaseEntity* parent_object = get_decomposing_entity(product);
// 		if (parent_object && parent_object->as<IfcSchema::IfcObjectDefinition>()) {
// 			parent_id = parent_object->data().id();
// 		}
// 	} catch (const std::exception& e) {
// 		Logger::Error(e);
// 	}
// 
// 	const std::string name = product->Name().get_value_or("");
// 	const std::string guid = product->GlobalId();
// 
// 	gp_Trsf trsf;
// 	try {
// 		if (product->ObjectPlacement()) {
// 			convert(product->ObjectPlacement(), trsf);
// 		}
// 	} catch (const std::exception& e) {
// 		Logger::Error(e);
// 	} catch (...) {
// 		Logger::Error("Failed to construct placement");
// 	}
// 
// 	// Does the IfcElement have any IfcOpenings?
// 	// Note that openings for IfcOpeningElements are not processed
// 	IfcSchema::IfcRelVoidsElement::list::ptr openings = find_openings(product);
// 
// 	const std::string product_type = product->declaration().name();
// 	ElementSettings element_settings(settings, getValue(GV_LENGTH_UNIT), product_type);
// 
// 	if (!settings.get(IfcGeom::IteratorSettings::DISABLE_OPENING_SUBTRACTIONS) && openings && openings->size()) {
// 		representation_id_builder << "-openings";
// 		for (IfcSchema::IfcRelVoidsElement::list::it it = openings->begin(); it != openings->end(); ++it) {
// 			representation_id_builder << "-" << (*it)->data().id();
// 		}
// 
// 		IfcGeom::ConversionResults opened_shapes;
// 		bool caught_error = false;
// 		try {
// 			convert_openings(product, openings, shapes, trsf, opened_shapes);
// 		} catch (const std::exception& e) {
// 			Logger::Message(Logger::LOG_ERROR, std::string("Error processing openings for: ") + e.what() + ":", product);
// 			caught_error = true;
// 		} catch (...) {
// 			Logger::Message(Logger::LOG_ERROR, "Error processing openings for:", product);
// 		}
// 
// 		if (caught_error && opened_shapes.size() < shapes.size()) {
// 			opened_shapes = shapes;
// 		}
// 
// 		if (settings.get(IteratorSettings::USE_WORLD_COORDS)) {
// 			for (IfcGeom::ConversionResults::iterator it = opened_shapes.begin(); it != opened_shapes.end(); ++it) {
// 				it->prepend(trsf);
// 			}
// 			trsf = gp_Trsf();
// 			representation_id_builder << "-world-coords";
// 		}
// 		shape = new IfcGeom::Representation::BRep(element_settings, representation_id_builder.str(), opened_shapes);
// 	} else if (settings.get(IteratorSettings::USE_WORLD_COORDS)) {
// 		for (IfcGeom::ConversionResults::iterator it = shapes.begin(); it != shapes.end(); ++it) {
// 			it->prepend(trsf);
// 		}
// 		trsf = gp_Trsf();
// 		representation_id_builder << "-world-coords";
// 		shape = new IfcGeom::Representation::BRep(element_settings, representation_id_builder.str(), shapes);
// 	} else {
// 		shape = new IfcGeom::Representation::BRep(element_settings, representation_id_builder.str(), shapes);
// 	}
// 
// 	std::string context_string = "";
// 	if (representation->RepresentationIdentifier()) {
// 		context_string = *representation->RepresentationIdentifier();
// 	} else if (representation->ContextOfItems()->ContextType()) {
// 		context_string = *representation->ContextOfItems()->ContextType();
// 	}
// 
// 	auto elem = new BRepElement(
// 		product->data().id(),
// 		parent_id,
// 		name,
// 		product_type,
// 		guid,
// 		context_string,
// 		trsf,
// 		boost::shared_ptr<IfcGeom::Representation::BRep>(shape),
// 		product
// 	);
// 
// 	if (settings.get(IteratorSettings::VALIDATE_QUANTITIES)) {
// 		auto rels = product->IsDefinedBy();
// 		for (auto& rel : *rels) {
// 			if (rel->as<IfcSchema::IfcRelDefinesByProperties>()) {
// 				auto pdef = rel->as<IfcSchema::IfcRelDefinesByProperties>()->RelatingPropertyDefinition();
// 				if (pdef->as<IfcSchema::IfcElementQuantity>()) {
// 					std::string organization_name;
// 					try {
// 						// A couple of files are not according to the schema here.
// 						organization_name = pdef->as<IfcSchema::IfcElementQuantity>()->OwnerHistory()->OwningApplication()->ApplicationDeveloper()->Name();
// 					} catch (...) {}
// 					if (organization_name == "IfcOpenShell") {
// 						auto qs = pdef->as<IfcSchema::IfcElementQuantity>()->Quantities();
// 						for (auto& q : *qs) {
// 							if (q->as<IfcSchema::IfcQuantityArea>() && q->Name() == "Total Surface Area") {
// 								double a_calc;
// 								double a_file = q->as<IfcSchema::IfcQuantityArea>()->AreaValue();
// 								if (elem->geometry().calculate_surface_area(a_calc)) {
// 									double diff = std::abs(a_calc - a_file);
// 									if (diff / std::sqrt(a_file) > getValue(GV_PRECISION)) {
// 										Logger::Error("Validation of surface area failed for:", product);
// 									} else {
// 										Logger::Notice("Validation of surface area succeeded for:", product);
// 									}
// 								} else {
// 									Logger::Error("Validation of surface area failed for:", product);
// 								}
// 							} else if (q->as<IfcSchema::IfcQuantityVolume>() && q->Name() == "Volume") {
// 								double v_calc;
// 								double v_file = q->as<IfcSchema::IfcQuantityVolume>()->VolumeValue();
// 								if (elem->geometry().calculate_volume(v_calc)) {
// 									double diff = std::abs(v_calc - v_file);
// 									if (diff / std::sqrt(v_file) > getValue(GV_PRECISION)) {
// 										Logger::Error("Validation of volume failed for:", product);
// 									} else {
// 										Logger::Notice("Validation of volume succeeded for:", product);
// 									}
// 								} else {
// 									Logger::Error("Validation of volume failed for:", product);
// 								}
// 							} else if (q->as<IfcSchema::IfcPhysicalComplexQuantity>() && q->Name() == "Shape Validation Properties") {
// 								auto qs2 = q->as<IfcSchema::IfcPhysicalComplexQuantity>()->HasQuantities();
// 								bool all_succeeded = qs2->size() > 0;
// 								for (auto& q2 : *qs2) {
// 									if (q2->as<IfcSchema::IfcQuantityCount>() && q2->Name() == "Surface Genus" && q2->Description()) {
// 										int item_id = boost::lexical_cast<int>((*q2->Description()).substr(1));
// 										int genus = (int)q2->as<IfcSchema::IfcQuantityCount>()->CountValue();
// 										for (auto& part : elem->geometry()) {
// 											if (part.ItemId() == item_id) {
// 												if (util::surface_genus(part.Shape()) != genus) {
// 													all_succeeded = false;
// 												}
// 											}
// 										}
// 									}
// 								}
// 								if (!all_succeeded) {
// 									Logger::Error("Validation of surface genus failed for:", product);
// 								} else {
// 									Logger::Notice("Validation of surface genus succeeded for:", product);
// 								}
// 							}
// 						}
// 					}
// 				}
// 			}
// 		}
// 	}
// 
// 	return elem;
// }
// 
// IfcSchema::IfcRepresentation* IfcGeom::Kernel::representation_mapped_to(const IfcSchema::IfcRepresentation* representation) {
// 	IfcSchema::IfcRepresentation* representation_mapped_to = 0;
// 	try {
// 		IfcSchema::IfcRepresentationItem::list::ptr items = representation->Items();
// 		if (items->size() == 1) {
// 			IfcSchema::IfcRepresentationptr item = *items->begin();
// 			if (item->declaration().is(IfcSchema::IfcMappedItem::Class())) {
// 				if (item->StyledByItem()->size() == 0) {
// 					IfcSchema::IfcMappedptr mapped_item = item->as<IfcSchema::IfcMappedItem>();
// 					if (is_identity_transform(mapped_item->MappingTarget())) {
// 						IfcSchema::IfcRepresentationMap* map = mapped_item->MappingSource();
// 						if (is_identity_transform(map->MappingOrigin())) {
// 							representation_mapped_to = map->MappedRepresentation();
// 						}
// 					}
// 				}
// 			}
// 		}
// 	} catch (const IfcParse::IfcException& e) {
// 		Logger::Error(e);
// 		// @todo reset representation_mapped_to to zero?
// 	}
// 	return representation_mapped_to;
// }
// 
// IfcSchema::IfcProduct::list::ptr IfcGeom::Kernel::products_represented_by(const IfcSchema::IfcRepresentation* representation) {
// 	IfcSchema::IfcProduct::list::ptr products(new IfcSchema::IfcProduct::list);
// 
// 	IfcSchema::IfcProductRepresentation::list::ptr prodreps = representation->OfProductRepresentation();
// 
// 	for (IfcSchema::IfcProductRepresentation::list::it it = prodreps->begin(); it != prodreps->end(); ++it) {
// 		// http://buildingsmart-tech.org/ifc/IFC2x3/TC1/html/ifcrepresentationresource/lexical/ifcproductrepresentation.htm
// 		// IFC2x Edition 3 NOTE  Users should not instantiate the entity IfcProductRepresentation from IFC2x Edition 3 onwards.
// 		// It will be changed into an ABSTRACT supertype in future releases of IFC.
// 
// 		// IfcProductRepresentation also lacks the INVERSE relation to IfcProduct
// 		// Let's find the IfcProducts that reference the IfcProductRepresentation anyway
// 		products->push((*it)->data().getInverse((&IfcSchema::IfcProduct::Class()), -1)->as<IfcSchema::IfcProduct>());
// 	}
// 
// 	IfcSchema::IfcRepresentationMap::list::ptr maps = representation->RepresentationMap();
// 
// 	if (products->size() && maps->size()) {
// 		Logger::Warning("Representation used by IfcRepresentationMap and IfcProductDefinitionShape", representation);
// 	}
// 
// 	if (prodreps->size() > 1) {
// 		Logger::Warning("Multiple IfcProductDefinitionShapes for representation", representation);
// 	}
// 
// 	if (maps->size() > 1) {
// 		Logger::Warning("Multiple IfcRepresentationMaps for representation", representation);
// 	}
// 
// 	if (maps->size() == 1) {
// 		IfcSchema::IfcRepresentationMap* map = *maps->begin();
// 		if (is_identity_transform(map->MappingOrigin())) {
// 			IfcSchema::IfcMappedItem::list::ptr items = map->MapUsage();
// 			for (IfcSchema::IfcMappedItem::list::it it = items->begin(); it != items->end(); ++it) {
// 				IfcSchema::IfcMappedptr item = *it;
// 				if (item->StyledByItem()->size() != 0) continue;
// 
// 				if (!is_identity_transform(item->MappingTarget())) {
// 					continue;
// 				}
// 
// 				IfcSchema::IfcRepresentation::list::ptr reps = item->data().getInverse((&IfcSchema::IfcRepresentation::Class()), -1)->as<IfcSchema::IfcRepresentation>();
// 				for (IfcSchema::IfcRepresentation::list::it jt = reps->begin(); jt != reps->end(); ++jt) {
// 					IfcSchema::IfcRepresentation* rep = *jt;
// 					if (rep->Items()->size() != 1) continue;
// 					IfcSchema::IfcProductRepresentation::list::ptr prodreps_mapped = rep->OfProductRepresentation();
// 					for (IfcSchema::IfcProductRepresentation::list::it kt = prodreps_mapped->begin(); kt != prodreps_mapped->end(); ++kt) {
// 						IfcSchema::IfcProduct::list::ptr ps = (*kt)->data().getInverse((&IfcSchema::IfcProduct::Class()), -1)->as<IfcSchema::IfcProduct>();
// 						products->push(ps);
// 					}
// 				}
// 			}
// 		}
// 	}
// 
// 	return products;
// }
// 
// IfcGeom::BRepElement* IfcGeom::Kernel::create_brep_for_processed_representation(
// 	const IteratorSettings& /*settings*/, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product,
// 	IfcGeom::BRepElement* brep)
// {
// 	int parent_id = -1;
// 	try {
// 		IfcUtil::IfcBaseEntity* parent_object = get_decomposing_entity(product);
// 		if (parent_object && parent_object->as<IfcSchema::IfcObjectDefinition>()) {
// 			parent_id = parent_object->data().id();
// 		}
// 	} catch (const std::exception& e) {
// 		Logger::Error(e);
// 	}
// 
// 	const std::string name = product->Name().get_value_or("");
// 	const std::string guid = product->GlobalId();
// 
// 	gp_Trsf trsf;
// 	try {
// 		if (product->ObjectPlacement()) {
// 			convert(product->ObjectPlacement(), trsf);
// 		}
// 	} catch (const std::exception& e) {
// 		Logger::Error(e);
// 	} catch (...) {
// 		Logger::Error("Failed to construct placement");
// 	}
// 
// 	std::string context_string = "";
// 	if (representation->RepresentationIdentifier()) {
// 		context_string = *representation->RepresentationIdentifier();
// 	} else if (representation->ContextOfItems()->ContextType()) {
// 		context_string = *representation->ContextOfItems()->ContextType();
// 	}
// 
// 	const std::string product_type = product->declaration().name();
// 
// 	return new BRepElement(
// 		product->data().id(),
// 		parent_id,
// 		name,
// 		product_type,
// 		guid,
// 		context_string,
// 		trsf,
// 		brep->geometry_pointer(),
// 		product
// 	);
// }
// 
// bool IfcGeom::Kernel::convert_layerset(const IfcSchema::IfcProduct* product, std::vector<Handle_Geom_Surface>& surfaces, std::vector<std::shared_ptr<const SurfaceStyle>>& styles, std::vector<double>& thicknesses) {
// 
// }
// 
// bool IfcGeom::Kernel::find_wall_end_points(const IfcSchema::IfcWall* wall, gp_Pnt& start, gp_Pnt& end) {
// 	IfcSchema::IfcRepresentation* axis_representation = find_representation(wall, "Axis");
// 	if (!axis_representation) {
// 		return false;
// 	}
// 
// 	ConversionResults items;
// 	{
// 		Kernel temp = *this;
// 		temp.setValue(GV_DIMENSIONALITY, -1.);
// 		temp.convert_shapes(axis_representation, items);
// 	}
// 
// 	TopoDS_Vertex a, b;
// 	for (ConversionResults::const_iterator it = items.begin(); it != items.end(); ++it) {
// 		TopExp_Explorer exp(it->Shape(), TopAbs_VERTEX);
// 		for (; exp.More(); exp.Next()) {
// 			b = TopoDS::Vertex(exp.Current());
// 			if (a.IsNull()) {
// 				a = b;
// 			}
// 		}
// 	}
// 
// 	if (a.IsNull() || b.IsNull()) {
// 		return false;
// 	}
// 
// 	start = BRep_Tool::Pnt(a);
// 	end = BRep_Tool::Pnt(b);
// 
// 	return true;
// }
// 
// bool IfcGeom::Kernel::fold_layers(const IfcSchema::IfcWall* wall, const ConversionResults& items, const std::vector<Handle_Geom_Surface>& surfaces, const std::vector<double>& thicknesses, std::vector< std::vector<Handle_Geom_Surface> >& result) {
// 	/*
// 	 * @todo isn't it easier to do this based on the non-folded surfaces of
// 	 * the connected walls and fold both pairs of layersets simultaneously?
// 	*/
// 
// 	bool folds_made = false;
// 
// 	IfcSchema::IfcRelConnectsPathElements::list::ptr connections(new IfcSchema::IfcRelConnectsPathElements::list);
// 	connections->push(wall->ConnectedFrom()->as<IfcSchema::IfcRelConnectsPathElements>());
// 	connections->push(wall->ConnectedTo()->as<IfcSchema::IfcRelConnectsPathElements>());
// 
// 	typedef std::vector<Handle_Geom_Surface> surfaces_t;
// 	typedef std::pair<Handle_Geom_Surface, Handle_Geom_Curve> curve_on_surface;
// 	typedef std::vector<curve_on_surface> curves_on_surfaces_t;
// 	typedef std::vector< std::pair< std::pair<IfcSchema::IfcConnectionTypeEnum::Value, IfcSchema::IfcConnectionTypeEnum::Value>, const IfcSchema::IfcProduct*> > endpoint_connections_t;
// 	typedef std::vector< std::vector<Handle_Geom_Surface> > result_t;
// 	endpoint_connections_t endpoint_connections;
// 
// 	// Find the semantic connections to other wall elements when they are not connected 'AT_PATH' because
// 	// in that latter case no folds need to be made.
// 	for (IfcSchema::IfcRelConnectsPathElements::list::it it = connections->begin(); it != connections->end(); ++it) {
// 		IfcSchema::IfcRelConnectsPathElements* connection = *it;
// 		IfcSchema::IfcConnectionTypeEnum::Value own_type = connection->RelatedElement() == wall
// 			? connection->RelatedConnectionType()
// 			: connection->RelatingConnectionType();
// 		IfcSchema::IfcConnectionTypeEnum::Value other_type = connection->RelatedElement() == wall
// 			? connection->RelatingConnectionType()
// 			: connection->RelatedConnectionType();
// 		if (other_type != IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATPATH &&
// 			(own_type == IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATEND ||
// 				own_type == IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATSTART)) {
// 			IfcSchema::IfcElement* other = connection->RelatedElement() == wall
// 				? connection->RelatingElement()
// 				: connection->RelatedElement();
// 			if (other->as<IfcSchema::IfcWall>()) {
// 				endpoint_connections.push_back(std::make_pair(std::make_pair(own_type, other_type), other));
// 			}
// 		}
// 	}
// 
// 	if (endpoint_connections.size() == 0) {
// 		return false;
// 	}
// 
// 	// Count how many connections are made AT_START and AT_END respectively
// 	int connection_type_count[2] = { 0,0 };
// 	for (endpoint_connections_t::const_iterator it = endpoint_connections.begin(); it != endpoint_connections.end(); ++it) {
// 		const int idx = it->first.first == IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATSTART;
// 		connection_type_count[idx] ++;
// 	}
// 
// 	gp_Trsf local;
// 	if (wall->ObjectPlacement()) {
// 		if (!convert(wall->ObjectPlacement(), local)) {
// 			return false;
// 		}
// 	}
// 	local.Invert();
// 
// 	{
// 		// Copy the unfolded surfaces
// 		result.resize(surfaces.size());
// 		std::vector< std::vector<Handle_Geom_Surface> >::iterator result_it = result.begin() + 1;
// 		std::vector<Handle_Geom_Surface>::const_iterator input_it = surfaces.begin() + 1;
// 		for (; input_it != surfaces.end() - 1; ++result_it, ++input_it) {
// 			result_it->push_back(*input_it);
// 		}
// 	}
// 
// 	const double total_thickness = std::accumulate(thicknesses.begin(), thicknesses.end(), 0.);
// 
// 	gp_Pnt own_axis_start, own_axis_end;
// 	find_wall_end_points(wall, own_axis_start, own_axis_end);
// 
// 	// Sometimes duplicate IfcRelConnectsPathElements exist. These are detected
// 	// and the counts of connections are decremented accordingly.
// 	for (int idx = 0; idx < 2; ++idx) {
// 		if (connection_type_count[idx] <= 1) {
// 			continue;
// 		}
// 
// 		/*
// 		IfcSchema::IfcConnectionTypeEnum::Value connection_type = idx == 1
// 			? IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATSTART
// 			: IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATEND;
// 		*/
// 
// 		std::set<const IfcSchema::IfcProduct*> others;
// 		endpoint_connections_t::iterator it = endpoint_connections.begin();
// 		while (it != endpoint_connections.end()) {
// 			const IfcSchema::IfcProduct* other = it->second;
// 			if (others.find(other) != others.end()) {
// 				it = endpoint_connections.erase(it);
// 				--connection_type_count[idx];
// 			} else {
// 				others.insert(other);
// 				++it;
// 			}
// 		}
// 	}
// 
// 	// Check whether the end points are of the wall are really ~1 LayerThickness away from each other
// 	/*
// 	for (endpoint_connections_t::const_iterator it = endpoint_connections.begin(); it != endpoint_connections.end(); ++it) {
// 		IfcSchema::IfcConnectionTypeEnum::Value own_type = it->first.first;
// 		IfcSchema::IfcConnectionTypeEnum::Value other_type = it->first.second;
// 
// 		gp_Pnt other_axis_start, other_axis_end;
// 		find_wall_end_points(it->second->as<IfcSchema::IfcWall>(), other_axis_start, other_axis_end);
// 
// 		gp_Trsf other;
// 		if (!convert(it->second->ObjectPlacement(), other)) {
// 			continue;
// 		}
// 
// 		other.Transforms(other_axis_start.ChangeCoord());
// 		local.Transforms(other_axis_start.ChangeCoord());
// 		other.Transforms(other_axis_end.ChangeCoord());
// 		local.Transforms(other_axis_end.ChangeCoord());
// 
// 		const gp_Pnt& a = own_type == IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATSTART
// 			? own_axis_start
// 			: own_axis_end;
// 
// 		const gp_Pnt& b = other_type == IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATSTART
// 			? other_axis_start
// 			: other_axis_end;
// 
// 		const double d = a.Distance(b);
// 	}
// 	*/
// 
// 	const double length_required = endpoint_connections.size() * total_thickness;
// 	// @todo this is not precisely the distance in case of curved walls. Also, it's safer
// 	// to first reproject the body onto the axis to get the precise curve parametrization
// 	// range. It's only a safeguard though, so can probably be approximated.
// 	const double axis_length = own_axis_start.Distance(own_axis_end);
// 	if (length_required > axis_length) {
// 		Logger::Warning("The wall axis is not long enough to accommodate the fold points");
// 		return false;
// 	}
// 
// 	for (endpoint_connections_t::const_iterator it = endpoint_connections.begin(); it != endpoint_connections.end(); ++it) {
// 		IfcSchema::IfcConnectionTypeEnum::Value connection_type = it->first.first;
// 
// 		// If more than one wall connects to this start/end -point assume layers do not need to be folded
// 		const int idx = connection_type == IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATSTART;
// 		if (connection_type_count[idx] > 1) continue;
// 
// 		// Pick the corresponding point from the axis
// 		const gp_Pnt& own_end_point = connection_type == IfcSchema::IfcConnectionTypeEnum::IfcConnectionType_ATEND
// 			? own_axis_end
// 			: own_axis_start;
// 		const IfcSchema::IfcProduct* other_wall = it->second;
// 
// 		gp_Trsf other;
// 		if (other_wall->ObjectPlacement()) {
// 			if (!convert(other_wall->ObjectPlacement(), other)) {
// 				Logger::Error("Failed to convert placement", other_wall);
// 				continue;
// 			}
// 		}
// 
// 		IfcSchema::IfcRepresentation* axis_representation = find_representation(other_wall, "Axis");
// 
// 		if (!axis_representation) {
// 			Logger::Warning("Joined wall has no axis representation", other_wall);
// 			continue;
// 		}
// 
// 		ConversionResults axis_items;
// 		{
// 			Kernel temp = *this;
// 			temp.setValue(GV_DIMENSIONALITY, -1.);
// 			temp.convert_shapes(axis_representation, axis_items);
// 		}
// 
// 		TopoDS_Shape axis_shape;
// 		util::flatten_shape_list(axis_items, axis_shape, false, getValue(GV_PRECISION));
// 
// 		// local and other are IfcLocalPlacements and therefore have a unit
// 		// scale factor that can be applied by means of TopoDS_Shape::Move()
// 		axis_shape.Move(other);
// 		axis_shape.Move(local);
// 
// 		TopoDS_Shape body_shape;
// 		util::flatten_shape_list(items, body_shape, false, getValue(GV_PRECISION));
// 
// 		// Create a single paremetric range over a single curve
// 		// that represents the entire 1d domain of the other wall
// 		// Sometimes there are multiple edges in the Axis shape
// 		// but it is assumed these are colinear.
// 		Handle_Geom_Curve other_axis_curve;
// 		double axis_u1, axis_u2;
// 		{
// 			TopExp_Explorer exp(axis_shape, TopAbs_EDGE);
// 			if (!exp.More()) {
// 				return false;
// 			}
// 
// 			TopoDS_Edge axis_edge = TopoDS::Edge(exp.Current());
// 			other_axis_curve = BRep_Tool::Curve(axis_edge, axis_u1, axis_u2);
// 
// 			gp_Pnt other_a_1, other_a_2;
// 			other_axis_curve->D0(axis_u1, other_a_1);
// 			other_axis_curve->D0(axis_u2, other_a_2);
// 
// 			if (axis_u2 < axis_u1) {
// 				std::swap(axis_u1, axis_u2);
// 			}
// 			exp.Next();
// 
// 			for (; exp.More(); exp.Next()) {
// 				TopoDS_Edge axis_edge2 = TopoDS::Edge(exp.Current());
// 				TopExp_Explorer exp2(axis_edge2, TopAbs_VERTEX);
// 				for (; exp2.More(); exp2.Next()) {
// 					gp_Pnt p = BRep_Tool::Pnt(TopoDS::Vertex(exp2.Current()));
// 					gp_Pnt pp;
// 					double u, d;
// 					if (util::project(other_axis_curve, p, pp, u, d)) {
// 						if (u < axis_u1) axis_u1 = u;
// 						if (u > axis_u2) axis_u2 = u;
// 					}
// 				}
// 			}
// 		}
// 
// 		double layer_offset = 0;
// 
// 		std::vector<double>::const_iterator thickness = thicknesses.begin();
// 		result_t::iterator result_vector = result.begin() + 1;
// 
// 		// nb The first layer is never folded, because it corresponds
// 		// to one of the longitudinal faces of the wall. Hence the +1
// 		for (surfaces_t::const_iterator jt = surfaces.begin() + 1; jt != surfaces.end() - 1; ++jt, ++result_vector) {
// 			layer_offset += *thickness++;
// 
// 			bool found_intersection = false, parallel = false;
// 			boost::optional<gp_Pnt> point_outside_param_range;
// 
// 			const Handle_Geom_Surface& surface = *jt;
// 
// 			// Find the intersection point between the layerset surface
// 			// and the other axis curve. If it's within the parametric
// 			// range of the other wall it means the walls are connected
// 			// with an angle.
// 			GeomAPI_IntCS intersections(other_axis_curve, surface);
// 			if (intersections.IsDone() && intersections.NbPoints() == 1) {
// 				const gp_Pnt& p = intersections.Point(1);
// 
// 				double u, v, w;
// 				intersections.Parameters(1, u, v, w);
// 
// 				gp_Pnt Pc, Ps;
// 				gp_Vec Vc, Vs1, Vs2;
// 				other_axis_curve->D1(w, Pc, Vc);
// 				surface->D1(u, v, Ps, Vs1, Vs2);
// 				Vs1.Cross(Vs2);
// 
// 				if (Vs1.IsNormal(Vc, 1.e-5)) {
// 					Logger::Warning("Connected walls are parallel");
// 					parallel = true;
// 				} else if (w < axis_u1 || w > axis_u2) {
// 					point_outside_param_range = p;
// 				} else {
// 					// Found an intersection. Layer end point is covered by connecting wall
// 					found_intersection = true;
// 					break;
// 				}
// 			}
// 
// 			if (!parallel && !found_intersection && point_outside_param_range) {
// 
// 				/*
// 				Is there a bug in Open Cascade related to the intersection
// 				of offset surfaces constructed from linear extrusions?
// 				Handle_Geom_Surface xy = new Geom_Plane(gp::Origin(), gp::DZ());
// 				// Handle_Geom_Surface yz = new Geom_Plane(gp::Origin(), gp::DX());
// 				// Handle_Geom_Surface yz2 = new Geom_OffsetSurface(yz, 1.);
// 				Handle_Geom_Curve ln = new Geom_Line(gp::Origin(), gp::DX());
// 				Handle_Geom_Surface yz = new Geom_SurfaceOfLinearExtrusion(ln, gp::DZ());
// 				Handle_Geom_Surface yz2 = new Geom_OffsetSurface(yz, 1.);
// 				intersect(xy, yz2);
// 				*/
// 
// 				Handle_Geom_Surface plane = new Geom_Plane(*point_outside_param_range, gp::DZ());
// 
// 				// vertical edges at wall end point face.
// 				curves_on_surfaces_t layer_ends;
// 				util::intersect(surface, body_shape, layer_ends);
// 
// 				Handle_Geom_Curve layer_body_intersection;
// 				Handle_Geom_Surface body_surface;
// 				double mind = std::numeric_limits<double>::infinity();
// 				for (curves_on_surfaces_t::const_iterator kt = layer_ends.begin(); kt != layer_ends.end(); ++kt) {
// 					gp_Pnt p;
// 					gp_Vec v;
// 					double u, d;
// 					kt->second->D1(0., p, v);
// 					if (ALMOST_THE_SAME(0., v.Dot(gp::DZ()))) {
// 						// Filter horizontal curves
// 						continue;
// 					}
// 					// Find vertical wall end point edge closest to end point associated with semantic connection
// 					if (util::project(kt->second, own_end_point, p, u, d)) {
// 						// In addition to closest, there is a length threshold based on thickness.
// 						// @todo ideally, first, the point closest to end-point is selected, and
// 						// after that the parallel check is performed. But threshold probably
// 						// functions good enough.
// 						if (d < total_thickness * 3 && d < mind) {
// 							GeomAdaptor_Curve GAC(other_axis_curve);
// 							GeomAdaptor_Surface GAS(kt->first);
// 
// 							Extrema_ExtCS x(GAC, GAS, getValue(GV_PRECISION), getValue(GV_PRECISION));
// 
// 							if (x.IsParallel()) {
// 								body_surface = kt->first;
// 								layer_body_intersection = kt->second;
// 								mind = d;
// 							}
// 						}
// 					}
// 				}
// 
// 				if (body_surface.IsNull()) {
// 					continue;
// 				}
// 
// 				// Intersect vertical edge with ground plane for point.
// 				GeomAPI_IntCS intersection2(layer_body_intersection, plane);
// 				if (intersection2.IsDone() && intersection2.NbPoints() == 1) {
// 					const gp_Pnt& layer_end_point = intersection2.Point(1);
// 
// 					// Intersect layerset surface with ground plane
// 					GeomAPI_IntSS intersection3(surface, plane, 1.e-7);
// 					if (intersection3.IsDone() && intersection3.NbLines() == 1) {
// 						Handle_Geom_Curve layer_line = intersection3.Line(1);
// 						GeomAdaptor_Curve layer_line_adaptor(layer_line);
// 						ShapeAnalysis_Curve sac;
// 						gp_Pnt layer_end_point_projected; double layer_end_point_param;
// 						sac.Project(layer_line, layer_end_point, 1e-3, layer_end_point_projected, layer_end_point_param, false);
// 
// 						// Move point inwards by distance from other layerset
// 						GCPnts_AbscissaPoint dst(layer_line_adaptor, layer_offset, layer_end_point_param);
// 						if (dst.IsDone()) {
// 							// Convert parameter to point
// 							gp_Pnt layer_fold_point;
// 							layer_line->D0(dst.Parameter(), layer_fold_point);
// 
// 							GeomAPI_IntSS intersection4(body_surface, plane, 1.e-7);
// 							if (intersection4.IsDone() && intersection4.NbLines() == 1) {
// 								Handle_Geom_Curve body_trim_curve = intersection4.Line(1);
// 								ShapeAnalysis_Curve sac2;
// 								gp_Pnt layer_fold_point_projected; double layer_fold_point_param;
// 								sac2.Project(body_trim_curve, layer_fold_point, 1.e-7, layer_fold_point_projected, layer_fold_point_param, false);
// 								Handle_Geom_Curve fold_curve = new Geom_OffsetCurve(body_trim_curve->Reversed(), layer_fold_point_projected.Distance(layer_fold_point), gp::DZ());
// 
// 								Handle_Geom_Surface fold_surface = new Geom_SurfaceOfLinearExtrusion(fold_curve, gp::DZ());
// 								result_vector->push_back(fold_surface);
// 								folds_made = true;
// 							}
// 						}
// 					}
// 				}
// 
// 			}
// 
// 		}
// 	}
// 
// 	return folds_made;
// }
// 
// IfcSchema::IfcRepresentation* IfcGeom::Kernel::find_representation(const IfcSchema::IfcProduct* product, const std::string& identifier) {
// 	if (!product->Representation()) return 0;
// 	IfcSchema::IfcProductRepresentation* prod_rep = product->Representation();
// 	IfcSchema::IfcRepresentation::list::ptr reps = prod_rep->Representations();
// 	for (IfcSchema::IfcRepresentation::list::it it = reps->begin(); it != reps->end(); ++it) {
// 		if ((**it).RepresentationIdentifier() && (*(**it).RepresentationIdentifier()) == identifier) {
// 			return *it;
// 		}
// 	}
// 	return 0;
// }
// 
// const IfcSchema::IfcRepresentationptr IfcGeom::Kernel::find_item_carrying_style(const IfcSchema::IfcRepresentationptr item) {
// 	if (item->StyledByItem()->size()) {
// 		return item;
// 	}
// 
// 	while (item->declaration().is(IfcSchema::IfcBooleanResult::Class())) {
// 		// All instantiations of IfcBooleanOperand (type of FirstOperand) are subtypes of
// 		// IfcGeometricRepresentationItem
// 		item = item->as<IfcSchema::IfcBooleanResult>()->FirstOperand()->as<IfcSchema::IfcRepresentationItem>();
// 		if (item && item->StyledByItem()->size()) {
// 			return item;
// 		}
// 	}
// 
// 	// TODO: Ideally this would be done for other entities (such as IfcCsgSolid) as well.
// 	// But neither are these very prevalent, nor does the current IfcOpenShell style
// 	// mechanism enable to conveniently style subshapes, which would be necessary for
// 	// distinctly styled union operands.
// 
// 	return item;
// }
// 
// bool IfcGeom::Kernel::is_identity_transform(IfcUtil::IfcBaseInterface* l) {
// 	IfcSchema::IfcAxis2Placement2D* ax2d;
// 	IfcSchema::IfcAxis2Placement3D* ax3d;
// 
// 	IfcSchema::IfcCartesianTransformationOperator2D* op2d;
// 	IfcSchema::IfcCartesianTransformationOperator3D* op3d;
// 	IfcSchema::IfcCartesianTransformationOperator2DnonUniform* op2dnonu;
// 	IfcSchema::IfcCartesianTransformationOperator3DnonUniform* op3dnonu;
// 
// 	if ((op2dnonu = l->as<IfcSchema::IfcCartesianTransformationOperator2DnonUniform>()) != 0) {
// 		gp_GTrsf2d gtrsf2d;
// 		convert(op2dnonu, gtrsf2d);
// 		return gtrsf2d.Form() == gp_Identity;
// 	} else if ((op2d = l->as<IfcSchema::IfcCartesianTransformationOperator2D>()) != 0) {
// 		gp_Trsf2d trsf2d;
// 		convert(op2d, trsf2d);
// 		return trsf2d.Form() == gp_Identity;
// 	} else if ((op3dnonu = l->as<IfcSchema::IfcCartesianTransformationOperator3DnonUniform>()) != 0) {
// 		gp_GTrsf gtrsf;
// 		convert(op3dnonu, gtrsf);
// 		return gtrsf.Form() == gp_Identity;
// 	} else if ((op3d = l->as<IfcSchema::IfcCartesianTransformationOperator3D>()) != 0) {
// 		gp_Trsf trsf;
// 		convert(op3d, trsf);
// 		return trsf.Form() == gp_Identity;
// 	} else if ((ax2d = l->as<IfcSchema::IfcAxis2Placement2D>()) != 0) {
// 		gp_Trsf2d trsf2d;
// 		convert(ax2d, trsf2d);
// 		return trsf2d.Form() == gp_Identity;
// 	} else if ((ax3d = l->as<IfcSchema::IfcAxis2Placement3D>()) != 0) {
// 		gp_Trsf trsf;
// 		convert(ax3d, trsf);
// 		return trsf.Form() == gp_Identity;
// 	} else {
// 		throw IfcParse::IfcException("Invalid valuation for IfcAxis2Placement / IfcCartesianTransformationOperator");
// 	}
// }
// 
// void IfcGeom::Kernel::set_conversion_placement_rel_to_type(const IfcParse::declaration* type) {
// 	placement_rel_to_type_ = type;
// }
// 
// void IfcGeom::Kernel::set_conversion_placement_rel_to_instance(const IfcUtil::IfcBaseEntity* instance) {
// 	placement_rel_to_instance_ = instance;
// }
// 
// 
// namespace {
// 
// 	bool process_colour(IfcSchema::IfcColourRgb* colour, double* rgb) {
// 		if (colour != 0) {
// 			rgb[0] = colour->Red();
// 			rgb[1] = colour->Green();
// 			rgb[2] = colour->Blue();
// 		}
// 		return colour != 0;
// 	}
// 
// 	bool process_colour(IfcSchema::IfcNormalisedRatioMeasure* factor, double* rgb) {
// 		if (factor != 0) {
// 			const double f = *factor;
// 			rgb[0] = rgb[1] = rgb[2] = f;
// 		}
// 		return factor != 0;
// 	}
// 
// 	bool process_colour(IfcSchema::IfcColourOrFactor* colour_or_factor, double* rgb) {
// 		if (colour_or_factor == 0) {
// 			return false;
// 		} else if (colour_or_factor->declaration().is(IfcSchema::IfcColourRgb::Class())) {
// 			return process_colour(static_cast<IfcSchema::IfcColourRgb*>(colour_or_factor), rgb);
// 		} else if (colour_or_factor->declaration().is(IfcSchema::IfcNormalisedRatioMeasure::Class())) {
// 			return process_colour(static_cast<IfcSchema::IfcNormalisedRatioMeasure*>(colour_or_factor), rgb);
// 		} else {
// 			return false;
// 		}
// 	}
// 
// }
// 
// #define Kernel POSTFIX_SCHEMA(Kernel)
// 
// std::shared_ptr<const IfcGeom::SurfaceStyle> IfcGeom::Kernel::internalize_surface_style(const std::pair<IfcUtil::IfcBaseClass*, IfcUtil::IfcBaseClass*>& shading_styles) {
// 	if (shading_styles.second == 0) {
// 		return 0;
// 	}
// 	int surface_style_id = shading_styles.first->data().id();
// 	auto it = style_cache.find(surface_style_id);
// 	if (it != style_cache.end()) {
// 		return it->second;
// 	}
// 
// 
// 	IfcSchema::IfcSurfaceStyle* style = shading_styles.first->as<IfcSchema::IfcSurfaceStyle>();
// 	IfcSchema::IfcSurfaceStyleShading* shading = shading_styles.second->as<IfcSchema::IfcSurfaceStyleShading>();
// 
// 	std::shared_ptr<SurfaceStyle> surface_style_ptr;
// 
// 	if (style->Name()) {
// 		surface_style_ptr.reset(new SurfaceStyle(surface_style_id, *style->Name()));
// 	} else {
// 		surface_style_ptr.reset(new SurfaceStyle(surface_style_id));
// 	}
// 
// 	std::shared_ptr<const SurfaceStyle> surface_style_ptr_const = std::const_pointer_cast<const SurfaceStyle>(surface_style_ptr);
// 	SurfaceStyle& surface_style = *surface_style_ptr;
// 
// 	double rgb[3];
// 	if (process_colour(shading->SurfaceColour(), rgb)) {
// 		surface_style.Diffuse().reset(SurfaceStyle::ColorComponent(rgb[0], rgb[1], rgb[2]));
// 	}
// 	if (shading_styles.second->declaration().is(IfcSchema::IfcSurfaceStyleRendering::Class())) {
// 		IfcSchema::IfcSurfaceStyleRendering* rendering_style = static_cast<IfcSchema::IfcSurfaceStyleRendering*>(shading_styles.second);
// 		if (rendering_style->DiffuseColour() && process_colour(rendering_style->DiffuseColour(), rgb)) {
// 			SurfaceStyle::ColorComponent diffuse = surface_style.Diffuse().get_value_or(SurfaceStyle::ColorComponent(1, 1, 1));
// 			surface_style.Diffuse().reset(SurfaceStyle::ColorComponent(diffuse.R() * rgb[0], diffuse.G() * rgb[1], diffuse.B() * rgb[2]));
// 		}
// 		if (rendering_style->DiffuseTransmissionColour()) {
// 			// Not supported
// 		}
// 		if (rendering_style->ReflectionColour()) {
// 			// Not supported
// 		}
// 		if (rendering_style->SpecularColour() && process_colour(rendering_style->SpecularColour(), rgb)) {
// 			surface_style.Specular().reset(SurfaceStyle::ColorComponent(rgb[0], rgb[1], rgb[2]));
// 		}
// 		if (rendering_style->SpecularHighlight()) {
// 			IfcSchema::IfcSpecularHighlightSelect* highlight = rendering_style->SpecularHighlight();
// 			if (highlight->declaration().is(IfcSchema::IfcSpecularRoughness::Class())) {
// 				double roughness = *((IfcSchema::IfcSpecularRoughness*)highlight);
// 				if (roughness >= 1e-9) {
// 					surface_style.Specularity().reset(1.0 / roughness);
// 				}
// 			} else if (highlight->declaration().is(IfcSchema::IfcSpecularExponent::Class())) {
// 				surface_style.Specularity().reset(*((IfcSchema::IfcSpecularExponent*)highlight));
// 			}
// 		}
// 		if (rendering_style->TransmissionColour()) {
// 			// Not supported
// 		}
// 		if (rendering_style->Transparency()) {
// 			const double d = *rendering_style->Transparency();
// 			surface_style.Transparency().reset(d);
// 		}
// 	}
// 	return style_cache[surface_style_id] = surface_style_ptr_const;
// }
// 
// std::shared_ptr<const IfcGeom::SurfaceStyle> IfcGeom::Kernel::get_style(const IfcSchema::IfcRepresentationptr item) {
// 	return internalize_surface_style(get_surface_style<IfcSchema::IfcSurfaceStyleShading>(item));
// }
// 
// std::shared_ptr<const IfcGeom::SurfaceStyle> IfcGeom::Kernel::get_style(const IfcSchema::IfcMaterial* material) {
// 	IfcSchema::IfcMaterialDefinitionRepresentation::list::ptr defs = material->HasRepresentation();
// 	for (IfcSchema::IfcMaterialDefinitionRepresentation::list::it jt = defs->begin(); jt != defs->end(); ++jt) {
// 		IfcSchema::IfcRepresentation::list::ptr reps = (*jt)->Representations();
// 		IfcSchema::IfcStyledItem::list::ptr styles(new IfcSchema::IfcStyledItem::list);
// 		for (IfcSchema::IfcRepresentation::list::it it = reps->begin(); it != reps->end(); ++it) {
// 			styles->push((**it).Items()->as<IfcSchema::IfcStyledItem>());
// 		}
// 		for (IfcSchema::IfcStyledItem::list::it it = styles->begin(); it != styles->end(); ++it) {
// 			const std::pair<IfcSchema::IfcSurfaceStyle*, IfcSchema::IfcSurfaceStyleShading*> ss = get_surface_style<IfcSchema::IfcSurfaceStyleShading>(*it);
// 			if (ss.second) {
// 				return internalize_surface_style(ss);
// 			}
// 		}
// 	}
// 	auto material_style = std::make_shared<IfcGeom::SurfaceStyle>(material->data().id(), material->Name());
// 	return style_cache[material->data().id()] = material_style;
// }
// 
// void IfcGeom::Kernel::apply_layerset(IfcGeom::ConversionResults& r, const ifcopenshell::geometry::layerset_information& info) {
// 	convert(info.layers);
// 
// 	if (info.layers.empty()) {
// 		return;
// 	}
// 
// 	if (axis_curve->DynamicType() == STANDARD_TYPE(Geom_Line)) {
// 		Handle_Geom_Line axis_line = Handle_Geom_Line::DownCast(axis_curve);
// 		// @todo note that this creates an offset into the wrong order, the cross product arguments should be
// 		// reversed. This causes some inversions later on, e.g. if(positive) { reverse(); }
// 		reference_surface = new Geom_Plane(axis_line->Lin().Location(), axis_line->Lin().Direction() ^ gp::DZ());
// 	} else if (axis_curve->DynamicType() == STANDARD_TYPE(Geom_Circle)) {
// 		// @todo note that in this branch this inversion does not seem to take place.
// 		Handle_Geom_Circle axis_line = Handle_Geom_Circle::DownCast(axis_curve);
// 		reference_surface = new Geom_CylindricalSurface(axis_li->Position(), axis_line->Radius());
// 	} else {
// 		Logger::Message(Logger::LOG_ERROR, "Unsupported underlying curve of Axis representation:", product);
// 		return false;
// 	}
// 
// 	IfcGeom::ConversionResults r2;
// 	if (IfcGeom::util::apply_layerset(r, const std::vector<ifcopenshell::geometry::taxonomy::style>&, ConversionResults& r2, double tol)) {
// 		std::swap(r, r2)
// 	}
// }