#include "converter.h"

#include "../ifcgeom/element.h"

using namespace ifcopenshell::geom;

ifcopenshell::geom::converter::converter(std::unique_ptr<ifcopenshell::geom::kernels::abstract_kernel>&& geometry_library, ifcopenshell::file* file, ifcopenshell::geom::settings& settings, ifcopenshell::logger& logger)
	: kernel_(std::move(geometry_library))
	, logger_(logger)
{
	mapping_ = impl::mapping_implementations().construct(file, settings, logger_);
	// Mapping reads unit information and applies to settings
	settings_ = mapping_->settings();
}

ifcopenshell::geom::converter::~converter() {
    delete mapping_;
}

ifcopenshell::geom::brep_element* ifcopenshell::geom::converter::create_brep_for_representation_and_product(taxonomy::ptr representation_node, const express::base product_, const taxonomy::matrix4::ptr& place_) {
    auto product = product_.as<express::entity>();
    
	std::stringstream representation_id_builder;

	auto place = place_;

	representation_id_builder << representation_node->instance.id();

	ifcopenshell::geom::brep* shape;
	std::vector<ifcopenshell::geom::conversion_result> shapes;

	if (!kernel_->convert(representation_node, shapes)) {
		return 0;
	}
	
	if (settings_.get<ifcopenshell::geom::settings::ApplyLayerSets>().get()) {
		ifcopenshell::geom::layerset_information layerinfo;
		std::vector<ifcopenshell::geom::endpoint_connection> neighbours;
		std::map<express::base, ifcopenshell::geom::layerset_information> neigbour_layers;
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
							ifcopenshell::logger::root().error("Failed processing layerset");
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
		if (auto itm = mapping_->map(single_material)) {
			auto s = taxonomy::cast<taxonomy::style>(itm);
			for (auto it = shapes.begin(); it != shapes.end(); ++it) {
				if (!it->hasStyle() && s) {
					it->setStyle(s);
					material_style_applied = true;
				}
			}
		}
	} else {
		bool some_items_without_style = false;
		for (auto it = shapes.begin(); it != shapes.end(); ++it) {
			// @todo implement num_faces()
			if (!it->hasStyle() /* && it->shape()->num_faces() */) {
				some_items_without_style = true;
				break;
			}
		}
		if (some_items_without_style) {
			logger_.warning("GEO", 31, "No material and surface styles for:", product);
		}
	}

	if (material_style_applied) {
		representation_id_builder << "-material-" << single_material.id();
	}

	if (settings_.get<ifcopenshell::geom::settings::ForceSpaceTransparency>().has() && product.declaration().is("IfcSpace")) {
		for (auto& s : shapes) {
			if (s.hasStyle()) {
				// @todo the uglyness
				const_cast<taxonomy::style*>(&*s.style_ptr())->transparency = settings_.get<ifcopenshell::geom::settings::ForceSpaceTransparency>().get();
			}
		}
	}

	int parent_id = -1;
	try {
		express::base parent_object = mapping_->get_decomposing_entity(product);
		if (parent_object) {
			parent_id = parent_object.id();
		}
	} catch (const std::exception& e) {
		logger_.error("GEO", 32, e);
	}

	const std::string name = product.get_value<std::string>("Name", "");
	const std::string guid = product.get_value<std::string>("GlobalId", "");

	const std::string product_type = product.declaration().name();

	// Does the IfcElement have any IfcOpenings?
	// Note that openings for IfcOpeningElements are not processed
	auto openings = mapping_->find_openings(product);

	const bool no_openings = openings.empty();
    const bool disable_opening_subtractions = settings_.get<ifcopenshell::geom::settings::DisableOpeningSubtractions>().get();
    const auto max_voids = settings_.get<ifcopenshell::geom::settings::MaxVoidsPerElement>();
    const bool above_limit = max_voids.has() && max_voids.get() != 0 && openings.size() > static_cast<std::size_t>(max_voids.get());

	if (above_limit) {
		logger_.warning("GEO", 403, "Element has more openings than the maximum allowed. Openings will not be processed for this element:", product);
    }

	if (!no_openings && !disable_opening_subtractions && !above_limit) {
		representation_id_builder << "-openings";
        for (auto& op : openings) {
			representation_id_builder << "-" << op.id();
		}

		std::vector<ifcopenshell::geom::conversion_result> opened_shapes;
		bool caught_error = false;
		try {
			std::vector<std::pair<taxonomy::ptr, taxonomy::matrix4>> opening_items;

			std::transform(openings.begin(), openings.end(), std::back_inserter(opening_items), [this](express::base opening) {
				auto prod_item = mapping()->map(opening);
				auto repr = mapping()->representation_of(opening);
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
			logger_.message(ifcopenshell::logger::LOG_ERROR, "GEO", 33, std::string("Error processing openings for: ") + e.what() + ":", product);
			caught_error = true;
		} catch (...) {
			logger_.message(ifcopenshell::logger::LOG_ERROR, "GEO", 34, "Error processing openings for:", product);
		}

		if (!(caught_error && opened_shapes.size() < shapes.size())) {
			if (settings_.get<ifcopenshell::geom::settings::UseWorldCoords>().get()) {
				for (auto it = opened_shapes.begin(); it != opened_shapes.end(); ++it) {
					it->prepend(place);
				}
				place = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>();
				representation_id_builder << "-world-coords";
			}
			shapes = opened_shapes;
		}
	} else if (settings_.get<ifcopenshell::geom::settings::UseWorldCoords>().get()) {
		for (auto it = shapes.begin(); it != shapes.end(); ++it) {
			it->prepend(place);
		}
		place = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>();
		representation_id_builder << "-world-coords";
	}

	if (settings_.get<ifcopenshell::geom::settings::UnifyShapes>().get()) {
		std::vector<ifcopenshell::geom::conversion_result> unified_shapes;
		try {
			if (kernel_->unify_shapes(shapes, unified_shapes)) {
				std::swap(shapes, unified_shapes);
			}
		} catch (std::exception& e) {
			logger_.error("GEO", 35, e);
		}
	}

	shape = new ifcopenshell::geom::brep(settings_, product_type, representation_id_builder.str(), shapes);

	std::string context_string = "";

	// IfcShapeRepresentation.
	auto representation = representation_node->instance.as<express::entity>();
	auto representation_identifier = representation.get("RepresentationIdentifier");
	if (!representation_identifier.isNull()) {
		context_string = (std::string) representation_identifier;
	}
	else {
		auto context = (express::base)representation.get("ContextOfItems");
		auto context_type = context.as<express::entity>().get("ContextType");
		if (!context_type.isNull()) {
			context_string = (std::string)context_type;
		}
	}

	auto elem = new ifcopenshell::geom::brep_element(
		product.id(),
		parent_id,
		name,
		product_type,
		guid,
		context_string,
		place,
		std::shared_ptr<ifcopenshell::geom::brep>(shape),
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
										ifcopenshell::logger::root().error("Validation of surface area failed for:", product);
									} else {
										ifcopenshell::logger::root().notice("Validation of surface area succeeded for:", product);
									}
								} else {
									ifcopenshell::logger::root().error("Validation of surface area failed for:", product);
								}
							} else if (q->as<IfcSchema::IfcQuantityVolume>() && q->Name() == "Volume") {
								double v_calc;
								double v_file = q->as<IfcSchema::IfcQuantityVolume>()->VolumeValue();
								if (elem->geometry().calculate_volume(v_calc)) {
									double diff = std::abs(v_calc - v_file);
									if (diff / std::sqrt(v_file) > getValue(GV_PRECISION)) {
										ifcopenshell::logger::root().error("Validation of volume failed for:", product);
									} else {
										ifcopenshell::logger::root().notice("Validation of volume succeeded for:", product);
									}
								} else {
									ifcopenshell::logger::root().error("Validation of volume failed for:", product);
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
												if (util::surface_genus(part.shape()) != genus) {
													all_succeeded = false;
												}
											}
										}
									}
								}
								if (!all_succeeded) {
									ifcopenshell::logger::root().error("Validation of surface genus failed for:", product);
								} else {
									ifcopenshell::logger::root().notice("Validation of surface genus succeeded for:", product);
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

ifcopenshell::geom::brep_element* ifcopenshell::geom::converter::create_brep_for_processed_representation(const express::base product_, const taxonomy::matrix4::ptr& place, ifcopenshell::geom::brep_element* brep) {
    auto product = product_.as<express::entity>();

	int parent_id = -1;
	try {
		express::base parent_object = mapping_->get_decomposing_entity(product);
		if (parent_object) {
			parent_id = parent_object.id();
		}
	} catch (const std::exception& e) {
		logger_.error("GEO", 36, e);
	}

	const std::string guid = product.get_value<std::string>("GlobalId");
	const std::string name = product.get_value<std::string>("Name", "");
	const std::string product_type = product.declaration().name();
	const std::string context_string = brep->context();

	return new ifcopenshell::geom::brep_element(
		product.id(),
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

ifcopenshell::geom::brep_element* ifcopenshell::geom::converter::create_brep_for_representation_and_product(const express::base representation, const express::base product) {
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

std::vector<ifcopenshell::geom::conversion_result> ifcopenshell::geom::converter::convert(express::base item)
{
	std::clock_t map_start = std::clock();
	auto geom_item = mapping_->map(item);
	std::vector<ifcopenshell::geom::conversion_result> results;
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
