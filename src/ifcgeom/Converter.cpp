#include "Converter.h"

#include "../ifcgeom/IfcGeomElement.h"

using namespace ifcopenshell::geometry;

ifcopenshell::geometry::Converter::Converter(const std::string& geometry_library, IfcParse::IfcFile* file, ifcopenshell::geometry::Settings& s)
	: geometry_library_(boost::to_lower_copy(geometry_library))
	, settings_(s)
{
	mapping_ = impl::mapping_implementations().construct(file, settings_);
	kernel_ = kernels::construct(file, geometry_library, mapping_->settings());
}

namespace {
	void substitute_with_box_based_on_density(IfcGeom::ConversionResults& items, double& density) {
		int nv = 0;
		void* box = nullptr;
		double volume = 0.;
		for (auto& i : items) {
			nv += i.Shape()->num_vertices();
			volume = i.Shape()->bounding_box(box);
		}
		density = nv / volume;
		if (density > 1e5) {
			items[0].Shape()->set_box(box);
			items.erase(items.begin() + 1, items.end());
			Logger::Notice("Substituted element with " + boost::lexical_cast<std::string>(density) + " vertices / m3 with a bounding box");
		}
	}
}

IfcGeom::BRepElement* ifcopenshell::geometry::Converter::create_brep_for_representation_and_product(taxonomy::ptr representation_node, const IfcUtil::IfcBaseEntity* product, const taxonomy::matrix4::ptr& place_) {
	std::stringstream representation_id_builder;

	auto place = place_;

	representation_id_builder << representation_node->instance->as<IfcUtil::IfcBaseEntity>()->id();

	IfcGeom::Representation::BRep* shape;
	IfcGeom::ConversionResults shapes;

	if (!kernel_->convert(representation_node, shapes)) {
		return 0;
	}

	if (settings_.get<ifcopenshell::geometry::settings::ApplyLayerSets>().get()) {
		ifcopenshell::geometry::layerset_information layerinfo;
		std::vector<ifcopenshell::geometry::endpoint_connection> neighbours;
		std::map<IfcUtil::IfcBaseEntity*, ifcopenshell::geometry::layerset_information> neigbour_layers;
		int layerset_id, lid;

		if (mapping_->get_layerset_information(product, layerinfo, layerset_id)) {
			representation_id_builder << "-layerset-" << layerset_id;
			if (mapping_->get_wall_neighbours(product, neighbours)) {
				for (auto& n : neighbours) {
					auto p = std::get<2>(n);
					mapping_->get_layerset_information(p, neigbour_layers[p], lid);
				}
				kernel_->apply_folded_layerset(shapes, layerinfo, neigbour_layers);
			} else {
				kernel_->apply_layerset(shapes, layerinfo);
			}
		}

		/*
		if (util::flatten_shape_list(shapes, merge, false, getValue(GV_PRECISION))) {
			if (util::count(merge, TopAbs_FACE) > 0) {
				
				if (convert_layerset(product, layers, styles, thickness)) {

					IfcSchema::IfcRelAssociates::list::ptr associations = product->HasAssociations();
					for (IfcSchema::IfcRelAssociates::list::it it = associations->begin(); it != associations->end(); ++it) {
						IfcSchema::IfcRelAssociatesMaterial* associates_material = (**it).as<IfcSchema::IfcRelAssociatesMaterial>();
						if (associates_material) {
							unsigned layerset_id = associates_material->RelatingMaterial()->data().id();
							representation_id_builder << "-layerset-" << layerset_id;
							break;
						}
					}

					if (styles.size() > 1) {
						// If there's only a single layer there is no need to manipulate geometries.
						bool success = true;
						if (product->as<IfcSchema::IfcWall>() && fold_layers(product->as<IfcSchema::IfcWall>(), shapes, layers, thickness, folded_layers)) {
							if (util::apply_folded_layerset(shapes, folded_layers, styles, shapes2, getValue(GV_PRECISION))) {
								std::swap(shapes, shapes2);
								success = true;
							}
						} else {
							if (util::apply_layerset(shapes, layers, styles, shapes2, getValue(GV_PRECISION))) {
								std::swap(shapes, shapes2);
								success = true;
							}
						}

						if (!success) {
							Logger::Error("Failed processing layerset");
						}
					}
				}
			}
		}
		*/
	}

	bool material_style_applied = false;

	auto single_material = mapping_->get_single_material_association(product);
	if (!single_material) {
		auto type_product = mapping_->get_product_type(product);
		if (type_product) {
			single_material = mapping_->get_single_material_association(type_product);
		}
	}

	if (single_material) {
		auto s = taxonomy::cast<taxonomy::style>(mapping_->map(single_material));
		for (auto it = shapes.begin(); it != shapes.end(); ++it) {
			if (!it->hasStyle() && s) {
				it->setStyle(s);
				material_style_applied = true;
			}
		}
	} else {
		bool some_items_without_style = false;
		for (auto it = shapes.begin(); it != shapes.end(); ++it) {
			// @todo implement num_faces()
			if (!it->hasStyle() /* && it->Shape()->num_faces() */) {
				some_items_without_style = true;
				break;
			}
		}
		if (some_items_without_style) {
			Logger::Warning("No material and surface styles for:", product);
		}
	}

	if (material_style_applied) {
		representation_id_builder << "-material-" << single_material->id();
	}

	if (settings_.get<ifcopenshell::geometry::settings::ForceSpaceTransparency>().has() && product->declaration().is("IfcSpace")) {
		for (auto& s : shapes) {
			if (s.hasStyle()) {
				// @todo the uglyness
				const_cast<taxonomy::style*>(&*s.StylePtr())->transparency = settings_.get<ifcopenshell::geometry::settings::ForceSpaceTransparency>().get();
			}
		}
	}

	int parent_id = -1;
	try {
		IfcUtil::IfcBaseEntity* parent_object = mapping_->get_decomposing_entity(product);
		if (parent_object) {
			parent_id = parent_object->id();
		}
	} catch (const std::exception& e) {
		Logger::Error(e);
	}

	const std::string name = product->get_value<std::string>("Name", "");
	const std::string guid = product->get_value<std::string>("GlobalId", "");

	const std::string product_type = product->declaration().name();

	// Does the IfcElement have any IfcOpenings?
	// Note that openings for IfcOpeningElements are not processed
	auto openings = mapping_->find_openings(product);

	if (!settings_.get<ifcopenshell::geometry::settings::DisableOpeningSubtractions>().get() && openings && openings->size()) {
		representation_id_builder << "-openings";
		for (auto it = openings->begin(); it != openings->end(); ++it) {
			representation_id_builder << "-" << (*it)->id();
		}

		IfcGeom::ConversionResults opened_shapes;
		bool caught_error = false;
		try {
			std::vector<std::pair<taxonomy::ptr, taxonomy::matrix4>> opening_items;

			std::transform(openings->begin(), openings->end(), std::back_inserter(opening_items), [this](IfcUtil::IfcBaseClass* opening) {
				auto prod_item = mapping()->map(opening);
				auto repr = mapping()->representation_of(opening->as<IfcUtil::IfcBaseEntity>());
				if (repr) {
					return std::make_pair(mapping()->map(repr), *taxonomy::cast<taxonomy::geom_item>(prod_item)->matrix);
				} else {
					return std::make_pair(taxonomy::ptr{}, taxonomy::matrix4{});
				}
			});

			opening_items.erase(
				std::remove_if(
					opening_items.begin(),
					opening_items.end(),
					[](const std::pair<taxonomy::ptr, taxonomy::matrix4>& p) { return !p.first; }
			), opening_items.end());

			if (opening_items.empty()) {
				opened_shapes = shapes;
			} else {
				kernel_->convert_openings(product, opening_items, shapes, *place, opened_shapes);
			}
		} catch (const std::exception& e) {
			Logger::Message(Logger::LOG_ERROR, std::string("Error processing openings for: ") + e.what() + ":", product);
			caught_error = true;
		} catch (...) {
			Logger::Message(Logger::LOG_ERROR, "Error processing openings for:", product);
		}

		if (caught_error && opened_shapes.size() < shapes.size()) {
			opened_shapes = shapes;
		}

		if (settings_.get<ifcopenshell::geometry::settings::UseWorldCoords>().get()) {
			for (auto it = opened_shapes.begin(); it != opened_shapes.end(); ++it) {
				it->prepend(place);
			}
			place = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>();
			representation_id_builder << "-world-coords";
		}
		shape = new IfcGeom::Representation::BRep(settings_, product_type, representation_id_builder.str(), opened_shapes);
	} else if (settings_.get<ifcopenshell::geometry::settings::UseWorldCoords>().get()) {
		for (auto it = shapes.begin(); it != shapes.end(); ++it) {
			it->prepend(place);
		}
		place = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>();
		representation_id_builder << "-world-coords";
		shape = new IfcGeom::Representation::BRep(settings_, product_type, representation_id_builder.str(), shapes);
	} else {
		shape = new IfcGeom::Representation::BRep(settings_, product_type, representation_id_builder.str(), shapes);
	}

	std::string context_string = "";

	// IfcShapeRepresentation.
	const IfcUtil::IfcBaseEntity *representation = representation_node->instance->as<IfcUtil::IfcBaseEntity>();
	auto representation_identifier = representation->get("RepresentationIdentifier");
	if (!representation_identifier.isNull()) {
		context_string = (std::string) representation_identifier;
	}
	else {
		IfcUtil::IfcBaseClass *context = (IfcUtil::IfcBaseClass*)representation->get("ContextOfItems");
		auto context_type = context->as<IfcUtil::IfcBaseEntity>()->get("ContextType");
		if (!context_type.isNull()) {
			context_string = (std::string)context_type;
		}
	}

	auto elem = new IfcGeom::BRepElement(
		product->id(),
		parent_id,
		name,
		product_type,
		guid,
		context_string,
		place,
		boost::shared_ptr<IfcGeom::Representation::BRep>(shape),
		product
	);

	/*
	// @todo
	if (settings_.get(IteratorSettings::VALIDATE_QUANTITIES)) {
		auto rels = product->IsDefinedBy();
		for (auto& rel : *rels) {
			if (rel->as<IfcSchema::IfcRelDefinesByProperties>()) {
				auto pdef = rel->as<IfcSchema::IfcRelDefinesByProperties>()->RelatingPropertyDefinition();
				if (pdef->as<IfcSchema::IfcElementQuantity>()) {
					std::string organization_name;
					try {
						// A couple of files are not according to the schema here.
						organization_name = pdef->as<IfcSchema::IfcElementQuantity>()->OwnerHistory()->OwningApplication()->ApplicationDeveloper()->Name();
					} catch (...) {}
					if (organization_name == "IfcOpenShell") {
						auto qs = pdef->as<IfcSchema::IfcElementQuantity>()->Quantities();
						for (auto& q : *qs) {
							if (q->as<IfcSchema::IfcQuantityArea>() && q->Name() == "Total Surface Area") {
								double a_calc;
								double a_file = q->as<IfcSchema::IfcQuantityArea>()->AreaValue();
								if (elem->geometry().calculate_surface_area(a_calc)) {
									double diff = std::abs(a_calc - a_file);
									if (diff / std::sqrt(a_file) > getValue(GV_PRECISION)) {
										Logger::Error("Validation of surface area failed for:", product);
									} else {
										Logger::Notice("Validation of surface area succeeded for:", product);
									}
								} else {
									Logger::Error("Validation of surface area failed for:", product);
								}
							} else if (q->as<IfcSchema::IfcQuantityVolume>() && q->Name() == "Volume") {
								double v_calc;
								double v_file = q->as<IfcSchema::IfcQuantityVolume>()->VolumeValue();
								if (elem->geometry().calculate_volume(v_calc)) {
									double diff = std::abs(v_calc - v_file);
									if (diff / std::sqrt(v_file) > getValue(GV_PRECISION)) {
										Logger::Error("Validation of volume failed for:", product);
									} else {
										Logger::Notice("Validation of volume succeeded for:", product);
									}
								} else {
									Logger::Error("Validation of volume failed for:", product);
								}
							} else if (q->as<IfcSchema::IfcPhysicalComplexQuantity>() && q->Name() == "Shape Validation Properties") {
								auto qs2 = q->as<IfcSchema::IfcPhysicalComplexQuantity>()->HasQuantities();
								bool all_succeeded = qs2->size() > 0;
								for (auto& q2 : *qs2) {
									if (q2->as<IfcSchema::IfcQuantityCount>() && q2->Name() == "Surface Genus" && q2->Description()) {
										int item_id = boost::lexical_cast<int>((*q2->Description()).substr(1));
										int genus = (int)q2->as<IfcSchema::IfcQuantityCount>()->CountValue();
										for (auto& part : elem->geometry()) {
											if (part.ItemId() == item_id) {
												if (util::surface_genus(part.Shape()) != genus) {
													all_succeeded = false;
												}
											}
										}
									}
								}
								if (!all_succeeded) {
									Logger::Error("Validation of surface genus failed for:", product);
								} else {
									Logger::Notice("Validation of surface genus succeeded for:", product);
								}
							}
						}
					}
				}
			}
		}
	}
	*/

	return elem;
}

IfcGeom::BRepElement* ifcopenshell::geometry::Converter::create_brep_for_processed_representation(const IfcUtil::IfcBaseEntity* product, const taxonomy::matrix4::ptr& place, IfcGeom::BRepElement* brep) {

	int parent_id = -1;
	try {
		IfcUtil::IfcBaseEntity* parent_object = mapping_->get_decomposing_entity(product);
		if (parent_object) {
			parent_id = parent_object->id();
		}
	} catch (const std::exception& e) {
		Logger::Error(e);
	}

	const std::string guid = product->get_value<std::string>("GlobalId");
	const std::string name = product->get_value<std::string>("Name", "");
	const std::string product_type = product->declaration().name();
	const std::string context_string = brep->context();

	return new IfcGeom::BRepElement(
		product->id(),
		parent_id,
		name,
		product_type,
		guid,
		context_string,
		place,
		brep->geometry_pointer(),
		product
	);
}

IfcGeom::BRepElement* ifcopenshell::geometry::Converter::create_brep_for_representation_and_product(const IfcUtil::IfcBaseEntity* representation, const IfcUtil::IfcBaseEntity* product) {
	auto interpreted_representation = mapping_->map(representation);
	if (!interpreted_representation) {
		interpreted_representation = taxonomy::make<taxonomy::collection>();
		interpreted_representation->instance = representation;
	}
	return create_brep_for_representation_and_product(
		interpreted_representation,
		product,
		taxonomy::cast<taxonomy::geom_item>(mapping_->map(product))->matrix
	);
}

IfcGeom::ConversionResults ifcopenshell::geometry::Converter::convert(IfcUtil::IfcBaseClass * item)
{
	std::clock_t map_start = std::clock();
	auto geom_item = mapping_->map(item);
	IfcGeom::ConversionResults results;
	if (geom_item) {
		std::clock_t geom_start = std::clock();
		if (!kernel_->convert(geom_item, results)) {
			throw std::runtime_error("Failed to convert item");
		}
		std::clock_t geom_end = std::clock();
		total_map_time += (geom_start - map_start) / (double) CLOCKS_PER_SEC;
		total_geom_time += (geom_end - geom_start) / (double) CLOCKS_PER_SEC;
	}
	return results;
}

//#include "../../ifcparse/Ifc2x3.h"
//#include "../../ifcparse/Ifc4.h"
//
//// @todo remove
//#include "../../ifcgeom/schema_agnostic/opencascade/OpenCascadeConversionResult.h"
//
//#include <TopExp.hxx>
//#include <TopTools_ListOfShape.hxx>
//#include <TopTools_IndexedMapOfShape.hxx>
//#include <TopTools_IndexedDataMapOfShapeListOfShape.hxx>
//
//IfcGeom::Kernel::Kernel(const std::string& geometry_library, IfcParse::IfcFile* file) {
//	if (file != 0) {
//		if (file->schema() == 0) {
//			throw IfcParse::IfcException("No schema associated with file");
//		}
//
//		const std::string& schema_name = file->schema()->name();
//		implementation_ = impl::kernel_implementations().construct(schema_name, geometry_library, file);
//	}
//}
//
//int IfcGeom::Kernel::count(const ConversionResultShape* s_, int t_, bool unique) {
//	// @todo make kernel agnostic
//	const TopoDS_Shape& s = ((OpenCascadeShape*) s_)->shape();
//	TopAbs_ShapeEnum t = (TopAbs_ShapeEnum) t_;
//
//	if (unique) {
//		TopTools_IndexedMapOfShape map;
//		TopExp::MapShapes(s, t, map);
//		return map.Extent();
//	} else {
//		int i = 0;
//		TopExp_Explorer exp(s, t);
//		for (; exp.More(); exp.Next()) {
//			++i;
//		}
//		return i;
//	}
//}
//
//
//int IfcGeom::Kernel::surface_genus(const ConversionResultShape* s_) {
//	// @todo make kernel agnostic
//	const TopoDS_Shape& s = ((OpenCascadeShape*) s_)->shape();
//	OpenCascadeShape Ss(s);
//
//	int nv = count(&Ss, (int) TopAbs_VERTEX, true);
//	int ne = count(&Ss, (int) TopAbs_EDGE, true);
//	int nf = count(&Ss, (int) TopAbs_FACE, true);
//
//	const int euler = nv - ne + nf;
//	const int genus = (2 - euler) / 2;
//
//	return genus;
//}
//
//
//IfcUtil::IfcBaseEntity* IfcGeom::Kernel::get_decomposing_entity(IfcUtil::IfcBaseEntity* inst, bool include_openings) {
//	if (inst->as<Ifc2x3::IfcProduct>()) {
//		return get_decomposing_entity_impl(inst->as<Ifc2x3::IfcProduct>(), include_openings);
//	} else if (inst->as<Ifc4::IfcProduct>()) {
//		return get_decomposing_entity_impl(inst->as<Ifc4::IfcProduct>(), include_openings);
//	} else if (inst->declaration().name() == "IfcProject") {
//		return nullptr;
//	} else {
//		throw IfcParse::IfcException("Unexpected entity " + inst->declaration().name());
//	}
//}
//
//
//bool IfcGeom::Kernel::is_manifold(const ConversionResultShape* s_) {
//        // @todo make kernel agnostic
//        const TopoDS_Shape& a = ((OpenCascadeShape*) s_)->shape();
//
//	if (a.ShapeType() == TopAbs_COMPOUND || a.ShapeType() == TopAbs_SOLID) {
//		TopoDS_Iterator it(a);
//		for (; it.More(); it.Next()) {
//			OpenCascadeShape s(it.Value());
//			if (!is_manifold(&s)) {
//				return false;
//			}
//		}
//		return true;
//	} else {
//		TopTools_IndexedDataMapOfShapeListOfShape map;
//		TopExp::MapShapesAndAncestors(a, TopAbs_EDGE, TopAbs_FACE, map);
//
//		for (int i = 1; i <= map.Extent(); ++i) {
//			if (map.FindFromIndex(i).Extent() != 2) {
//				return false;
//			}
//		}
//
//		return true;
//	}
//}
