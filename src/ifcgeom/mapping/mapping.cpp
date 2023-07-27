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

#define _USE_MATH_DEFINES
#include <cmath>

#include "mapping.h"

#include "../../ifcparse/IfcLogger.h"
#include "../../ifcparse/IfcFile.h"
#include "../../ifcparse/IfcSIPrefix.h"

using namespace IfcUtil;
using namespace ifcopenshell::geometry;
using namespace IfcGeom;

namespace {
	struct POSTFIX_SCHEMA(factory_t) {
		abstract_mapping* operator()(IfcParse::IfcFile* file, IteratorSettings& settings) const {
			ifcopenshell::geometry::POSTFIX_SCHEMA(mapping)* m = new ifcopenshell::geometry::POSTFIX_SCHEMA(mapping)(file, settings);
			return m;
		}
	};
}

void MAKE_INIT_FN(MappingImplementation)(ifcopenshell::geometry::impl::MappingFactoryImplementation* mapping) {
	static const std::string schema_name = STRINGIFY(IfcSchema);
	POSTFIX_SCHEMA(factory_t) factory;
	mapping->bind(schema_name, factory);
}

#define mapping POSTFIX_SCHEMA(mapping)

IfcSchema::IfcProduct::list::ptr mapping::products_represented_by(const IfcSchema::IfcRepresentation* representation, bool only_direct) {
	IfcSchema::IfcProduct::list::ptr products(new IfcSchema::IfcProduct::list);

	IfcSchema::IfcProductRepresentation::list::ptr prodreps = representation->OfProductRepresentation();

	for (IfcSchema::IfcProductRepresentation::list::it it = prodreps->begin(); it != prodreps->end(); ++it) {
		// http://buildingsmart-tech.org/ifc/IFC2x3/TC1/html/ifcrepresentationresource/lexical/ifcproductrepresentation.htm
		// IFC2x Edition 3 NOTE  Users should not instantiate the entity IfcProductRepresentation from IFC2x Edition 3 onwards.
		// It will be changed into an ABSTRACT supertype in future releases of IFC.

		// IfcProductRepresentation also lacks the INVERSE relation to IfcProduct
		// Let's find the IfcProducts that reference the IfcProductRepresentation anyway
		products->push((*it)->data().getInverse((&IfcSchema::IfcProduct::Class()), -1)->as<IfcSchema::IfcProduct>());
	}

	if (only_direct) {
		return products;
	}

	IfcSchema::IfcRepresentationMap::list::ptr maps = representation->RepresentationMap();
	if (maps->size() == 1) {
		IfcSchema::IfcRepresentationMap* rmap = *maps->begin();
		taxonomy::matrix4::ptr origin = taxonomy::cast<taxonomy::matrix4>(map(rmap->MappingOrigin()));
		if (origin->is_identity()) {
			IfcSchema::IfcMappedItem::list::ptr items = rmap->MapUsage();
			for (IfcSchema::IfcMappedItem::list::it it = items->begin(); it != items->end(); ++it) {
				IfcSchema::IfcMappedItem* item = *it;
				if (item->StyledByItem()->size() != 0) continue;

				taxonomy::matrix4::ptr target = taxonomy::cast<taxonomy::matrix4>(map(item->MappingTarget()));
				if (!target->is_identity()) {
					continue;
				}

				IfcSchema::IfcRepresentation::list::ptr reps = item->data().getInverse((&IfcSchema::IfcRepresentation::Class()), -1)->as<IfcSchema::IfcRepresentation>();
				for (IfcSchema::IfcRepresentation::list::it jt = reps->begin(); jt != reps->end(); ++jt) {
					IfcSchema::IfcRepresentation* rep = *jt;
					if (rep->Items()->size() != 1) continue;
					IfcSchema::IfcProductRepresentation::list::ptr prodreps_mapped = rep->OfProductRepresentation();
					for (IfcSchema::IfcProductRepresentation::list::it kt = prodreps_mapped->begin(); kt != prodreps_mapped->end(); ++kt) {
						IfcSchema::IfcProduct::list::ptr ps = (*kt)->data().getInverse((&IfcSchema::IfcProduct::Class()), -1)->as<IfcSchema::IfcProduct>();
						products->push(ps);
					}
				}
			}
		}
	}

	return products;
}

namespace {
	IfcSchema::IfcProduct::list::ptr filter_products(IfcSchema::IfcProduct::list::ptr unfiltered_products, std::vector<filter_t>& filters) {
		auto ifcproducts = IfcSchema::IfcProduct::list::ptr(new IfcSchema::IfcProduct::list);
		for (IfcSchema::IfcProduct::list::it jt = unfiltered_products->begin(); jt != unfiltered_products->end(); ++jt) {
			IfcSchema::IfcProduct* prod = *jt;
			if (boost::all(filters, [prod](const filter_t& f) { return f(prod); })) {
				ifcproducts->push(prod);
			}
		}
		return ifcproducts;
	}
}

bool mapping::reuse_ok_(const IfcSchema::IfcProduct::list::ptr& products) {
	// With world coords enabled, object transformations are directly applied to
	// the BRep. There is no way to re-use the geometry for multiple products.
	if (settings_.get(IfcGeom::IteratorSettings::USE_WORLD_COORDS)) {
		return false;
	}

	if (products->size() == 1) {
		return true;
	}

	std::set<const IfcUtil::IfcBaseEntity*> associated_single_materials;

	for (IfcSchema::IfcProduct::list::it it = products->begin(); it != products->end(); ++it) {
		IfcSchema::IfcProduct* product = *it;

		if (!settings_.get(IfcGeom::IteratorSettings::DISABLE_OPENING_SUBTRACTIONS) && find_openings(product)->size()) {
			return false;
		}

		if (settings_.get(IfcGeom::IteratorSettings::APPLY_LAYERSETS)) {
			IfcSchema::IfcRelAssociates::list::ptr associations = product->HasAssociations();
			for (IfcSchema::IfcRelAssociates::list::it jt = associations->begin(); jt != associations->end(); ++jt) {
				IfcSchema::IfcRelAssociatesMaterial* assoc = (*jt)->as<IfcSchema::IfcRelAssociatesMaterial>();
				if (assoc) {
					if (assoc->RelatingMaterial()->declaration().is(IfcSchema::IfcMaterialLayerSetUsage::Class())) {
						// TODO: Check whether single layer?
						return false;
					}
				}
			}
		}

		// Note that this can be a nullptr (!), but the fact that set size should be one still holds
		associated_single_materials.insert(get_single_material_association(product));
		if (associated_single_materials.size() > 1) return false;
	}

	return associated_single_materials.size() == 1;
}

aggregate_of_instance::ptr mapping::find_openings(const IfcUtil::IfcBaseEntity* inst) {
	auto product = inst->as<IfcSchema::IfcProduct>();

	aggregate_of_instance::ptr openings(new aggregate_of_instance);
	if (product->declaration().is(IfcSchema::IfcElement::Class()) && !product->declaration().is(IfcSchema::IfcOpeningElement::Class())) {
		IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)product;
		auto rels = element->HasOpenings();
		for (auto& rel : *rels) {
			openings->push(rel->RelatedOpeningElement());
		}
	}

	// Is the IfcElement a decomposition of an IfcElement with any IfcOpeningElements?
	const IfcSchema::IfcObjectDefinition* obdef = product->as<IfcSchema::IfcObjectDefinition>();
	for (;;) {
		auto decomposes = obdef->Decomposes()->generalize();
		if (decomposes->size() != 1) break;
		IfcSchema::IfcObjectDefinition* rel_obdef = (*decomposes->begin())->as<IfcSchema::IfcRelAggregates>()->RelatingObject();
		if (rel_obdef->declaration().is(IfcSchema::IfcElement::Class()) && !rel_obdef->declaration().is(IfcSchema::IfcOpeningElement::Class())) {
			IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)rel_obdef;
			auto rels = element->HasOpenings();
			for (auto& rel : *rels) {
				openings->push(rel->RelatedOpeningElement());
			}
		}

		obdef = rel_obdef;
	}

	return openings;
}


void mapping::get_representations(std::vector<geometry_conversion_task>& tasks, std::vector<filter_t>& filters) {
	IfcSchema::IfcRepresentation::list::ptr representations(new IfcSchema::IfcRepresentation::list);

	if (settings_.context_ids().empty()) {
		addRepresentationsFromDefaultContexts(representations);
	} else {
		addRepresentationsFromContextIds(representations);
	}

	IfcSchema::IfcRepresentation::list::ptr ok_mapped_representations(new IfcSchema::IfcRepresentation::list);

	int task_index = 0;
	
	for (auto representation : *representations) {
		IfcSchema::IfcProduct::list::ptr ifcproducts = filter_products(products_represented_by(representation, false), filters);
		
		if (ifcproducts->size() == 0) {
			continue;
		}

		auto geometry_reuse_ok_for_current_representation_ = reuse_ok_(ifcproducts);

		IfcSchema::IfcRepresentationMap::list::ptr maps = representation->RepresentationMap();

		if (!geometry_reuse_ok_for_current_representation_ && maps->size() == 1) {
			// unfiltered_products contains products represented by this representation by means of mapped items.
			// For example because of openings applied to products, reuse might not be acceptable and then the
			// products will be processed by means of their immediate representation and not the mapped representation.

			// IfcRepresentationMaps are also used for IfcTypeProducts, so an additional check is performed whether the map
			// is indeed used by IfcMappedItems.
			IfcSchema::IfcRepresentationMap* map = *maps->begin();
			if (map->MapUsage()->size() > 0) {
				continue;
			}
		}

		// Check if this representation has (or will be) processed as part its mapped representation
		bool representation_processed_as_mapped_item = false;
		IfcSchema::IfcRepresentation* representation_mapped_to_result = representation_mapped_to(representation);
		if (representation_mapped_to_result) {
			representation_processed_as_mapped_item = geometry_reuse_ok_for_current_representation_ && (
				ok_mapped_representations->contains(representation_mapped_to_result) || reuse_ok_(products_represented_by(representation_mapped_to_result)));
		}

		if (representation_processed_as_mapped_item) {
			ok_mapped_representations->push(representation_mapped_to_result);
			continue;
		}

		// @todo, fix this properly by considering the mapped geometry types in the representation.
		if (representation->RepresentationIdentifier() && *representation->RepresentationIdentifier() == "Body") {
			geometry_conversion_task task;
			task.index = task_index++;
			task.representation = representation;
			task.products = ifcproducts->generalize();

			tasks.emplace_back(task);
		}
	}
}

const IfcUtil::IfcBaseEntity* mapping::get_single_material_association(const IfcUtil::IfcBaseEntity* product_) {
	auto product = product_->as<IfcSchema::IfcProduct>();
	IfcSchema::IfcMaterial* single_material = 0;
	IfcSchema::IfcRelAssociatesMaterial::list::ptr associated_materials = product->HasAssociations()->as<IfcSchema::IfcRelAssociatesMaterial>();
	if (associated_materials->size() == 1) {
		IfcSchema::IfcMaterialSelect* associated_material = (*associated_materials->begin())->RelatingMaterial();
		single_material = associated_material->as<IfcSchema::IfcMaterial>();

		// NB: Single-layer layersets are also considered, regardless of --enable-layerset-slicing, this
		// in accordance with other viewers.
		if (!single_material && associated_material->as<IfcSchema::IfcMaterialLayerSetUsage>()) {
			IfcSchema::IfcMaterialLayerSet* layerset = associated_material->as<IfcSchema::IfcMaterialLayerSetUsage>()->ForLayerSet();
			if (layerset->MaterialLayers()->size() == 1) {
				IfcSchema::IfcMaterialLayer* layer = (*layerset->MaterialLayers()->begin());
				if (layer->Material()) {
					single_material = layer->Material();
				}
			}
		}
	}
	return single_material;
}

IfcSchema::IfcRepresentation* mapping::representation_mapped_to(const IfcSchema::IfcRepresentation* representation) {
	IfcSchema::IfcRepresentation* representation_mapped_to = 0;
	IfcSchema::IfcRepresentationItem::list::ptr items = representation->Items();
	if (items->size() == 1) {
		IfcSchema::IfcRepresentationItem* item = *items->begin();
		if (item->declaration().is(IfcSchema::IfcMappedItem::Class())) {
			if (item->StyledByItem()->size() == 0) {
				IfcSchema::IfcMappedItem* mapped_item = item->as<IfcSchema::IfcMappedItem>();
				taxonomy::matrix4::ptr target = taxonomy::cast<taxonomy::matrix4>(map(mapped_item->MappingTarget()));
				if (target->is_identity()) {
					IfcSchema::IfcRepresentationMap* rmap = mapped_item->MappingSource();
					taxonomy::matrix4::ptr origin = taxonomy::cast<taxonomy::matrix4>(map(rmap->MappingOrigin()));
					if (origin->is_identity()) {
						representation_mapped_to = rmap->MappedRepresentation();
					}
				}
			}
		}
	}
	return representation_mapped_to;
}

namespace {
	const IfcSchema::IfcRepresentationItem* find_item_carrying_style(const IfcSchema::IfcRepresentationItem* item) {
		if (item->StyledByItem()->size()) {
			return item;
		}

		while (item->declaration().is(IfcSchema::IfcBooleanClippingResult::Class())) {
			// All instantiations of IfcBooleanOperand (type of FirstOperand) are subtypes of
			// IfcGeometricRepresentationItem
			item = (IfcSchema::IfcGeometricRepresentationItem*) ((IfcSchema::IfcBooleanClippingResult*) item)->FirstOperand();
			if (item->StyledByItem()->size()) {
				return item;
			}
		}

		// TODO: Ideally this would be done for other entities (such as IfcCsgSolid) as well.
		// But neither are these very prevalent, nor does the current IfcOpenShell style
		// mechanism enable to conveniently style subshapes, which would be necessary for
		// distinctly styled union operands.

		return item;
	}

	template <typename T>
	std::pair<IfcSchema::IfcSurfaceStyle*, T*> get_surface_style(const IfcSchema::IfcStyledItem* si) {
#ifdef SCHEMA_HAS_IfcStyleAssignmentSelect
		aggregate_of_instance::ptr style_assignments = si->Styles();
		for (aggregate_of_instance::it kt = style_assignments->begin(); kt != style_assignments->end(); ++kt) {
			if (!(*kt)->declaration().is(IfcSchema::IfcPresentationStyleAssignment::Class())) {
				continue;
			}
			IfcSchema::IfcPresentationStyleAssignment* style_assignment = (IfcSchema::IfcPresentationStyleAssignment*) *kt;

			// Only in case of 2x3 or old style IfcPresentationStyleAssignment
			auto styles = style_assignment->Styles();
#elif defined(SCHEMA_HAS_IfcPresentationStyleAssignment)
		IfcSchema::IfcPresentationStyleAssignment::list::ptr style_assignments = si->Styles();
		for (IfcSchema::IfcPresentationStyleAssignment::list::it kt = style_assignments->begin(); kt != style_assignments->end(); ++kt) {
			IfcSchema::IfcPresentationStyleAssignment* style_assignment = *kt;

			// Only in case of 2x3 or old style IfcPresentationStyleAssignment
			auto styles = style_assignment->Styles();
#else
		auto styles = si->Styles();
#endif
			for (auto lt = styles->begin(); lt != styles->end(); ++lt) {
				IfcUtil::IfcBaseClass* style = *lt;
				if (style->declaration().is(IfcSchema::IfcSurfaceStyle::Class())) {
					IfcSchema::IfcSurfaceStyle* surface_style = (IfcSchema::IfcSurfaceStyle*) style;
					if (surface_style->Side() != IfcSchema::IfcSurfaceSide::IfcSurfaceSide_NEGATIVE) {
						aggregate_of_instance::ptr styles_elements = surface_style->Styles();
						for (aggregate_of_instance::it mt = styles_elements->begin(); mt != styles_elements->end(); ++mt) {
							if ((*mt)->declaration().is(T::Class())) {
								return std::make_pair(surface_style, (T*)*mt);
							}
						}
					}
				}
			}
#if defined(SCHEMA_HAS_IfcStyleAssignmentSelect) || defined(SCHEMA_HAS_IfcPresentationStyleAssignment)
		}
#endif

		return std::make_pair<IfcSchema::IfcSurfaceStyle*, T*>(0, 0);
	}

	const IfcSchema::IfcStyledItem* find_style(const IfcSchema::IfcRepresentationItem* representation_item) {
		// For certain representation items, most notably boolean operands,
		// a style definition might reside on one of its operands.
		representation_item = find_item_carrying_style(representation_item);

		if (representation_item->as<IfcSchema::IfcStyledItem>()) {
			return representation_item->as<IfcSchema::IfcStyledItem>();
		}

		IfcSchema::IfcStyledItem::list::ptr styled_items = representation_item->StyledByItem();
		if (styled_items->size()) {
			// StyledByItem is a SET [0:1] OF IfcStyledItem, so we return after the first IfcStyledItem:
			return *styled_items->begin();
		}

		return nullptr;
	}

	bool process_colour(IfcSchema::IfcColourRgb* colour, double* rgb) {
		if (colour != 0) {
			rgb[0] = colour->Red();
			rgb[1] = colour->Green();
			rgb[2] = colour->Blue();
		}
		return colour != 0;
	}

	bool process_colour(IfcSchema::IfcNormalisedRatioMeasure* factor, double* rgb) {
		if (factor != 0) {
			const double f = *factor;
			rgb[0] = rgb[1] = rgb[2] = f;
		}
		return factor != 0;
	}

	bool process_colour(IfcSchema::IfcColourOrFactor* colour_or_factor, double* rgb) {
		if (colour_or_factor == 0) {
			return false;
		} else if (colour_or_factor->declaration().is(IfcSchema::IfcColourRgb::Class())) {
			return process_colour(static_cast<IfcSchema::IfcColourRgb*>(colour_or_factor), rgb);
		} else if (colour_or_factor->declaration().is(IfcSchema::IfcNormalisedRatioMeasure::Class())) {
			return process_colour(static_cast<IfcSchema::IfcNormalisedRatioMeasure*>(colour_or_factor), rgb);
		} else {
			return false;
		}
	}
}

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcMaterial* material) {
	IfcSchema::IfcMaterialDefinitionRepresentation::list::ptr defs = material->HasRepresentation();
	for (IfcSchema::IfcMaterialDefinitionRepresentation::list::it jt = defs->begin(); jt != defs->end(); ++jt) {
		IfcSchema::IfcRepresentation::list::ptr reps = (*jt)->Representations();
		IfcSchema::IfcStyledItem::list::ptr styles(new IfcSchema::IfcStyledItem::list);
		for (IfcSchema::IfcRepresentation::list::it it = reps->begin(); it != reps->end(); ++it) {
			styles->push((**it).Items()->as<IfcSchema::IfcStyledItem>());
		}
		if (styles->size() == 1) {
			return map(*styles->begin());
		}
	}

	taxonomy::style::ptr material_style = taxonomy::make<taxonomy::style>();
	return material_style;

	// @todo
	// IfcGeom::SurfaceStyle material_style = IfcGeom::SurfaceStyle(material->data().id(), material->Name());
	// return &(style_cache[material->data().id()] = material_style);
}

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcStyledItem* inst) {
	auto style_pair = get_surface_style<IfcSchema::IfcSurfaceStyleShading>(inst);

	IfcSchema::IfcSurfaceStyle* style = style_pair.first;
	IfcSchema::IfcSurfaceStyleShading* shading = style_pair.second;

	if (style == nullptr) {
		return nullptr;
	}

	static taxonomy::colour white = taxonomy::colour(1., 1., 1.);

	taxonomy::style::ptr surface_style = taxonomy::make<taxonomy::style>();

	surface_style->instance = style;
	if (style->Name()) {
		surface_style->name = *style->Name();
	}
	
	double rgb[3];
	if (process_colour(shading->SurfaceColour(), rgb)) {
		surface_style->diffuse.components() << rgb[0], rgb[1], rgb[2];
	}

	if (auto rendering_style = shading->as<IfcSchema::IfcSurfaceStyleRendering>()) {
		if (rendering_style->DiffuseColour() && process_colour(rendering_style->DiffuseColour(), rgb)) {
			const taxonomy::colour& old_diffuse = surface_style->diffuse ? surface_style->diffuse : white;
			surface_style->diffuse = taxonomy::colour(old_diffuse.r() * rgb[0], old_diffuse.g() * rgb[1], old_diffuse.b() * rgb[2]);
		}
		if (rendering_style->DiffuseTransmissionColour()) {
			// Not supported
		}
		if (rendering_style->ReflectionColour()) {
			// Not supported
		}
		if (rendering_style->SpecularColour() && process_colour(rendering_style->SpecularColour(), rgb)) {
			surface_style->specular = taxonomy::colour(rgb[0], rgb[1], rgb[2]);
		}
		if (rendering_style->SpecularHighlight()) {
			IfcSchema::IfcSpecularHighlightSelect* highlight = rendering_style->SpecularHighlight();
			if (highlight->declaration().is(IfcSchema::IfcSpecularRoughness::Class())) {
				double roughness = *((IfcSchema::IfcSpecularRoughness*)highlight);
				if (roughness >= 1e-9) {
					surface_style->specularity = (1.0 / roughness);
				}
			} else if (highlight->declaration().is(IfcSchema::IfcSpecularExponent::Class())) {
				surface_style->specularity = (*((IfcSchema::IfcSpecularExponent*)highlight));
			}
		}
		if (rendering_style->TransmissionColour()) {
			// Not supported
		}
		if (rendering_style->Transparency()) {
			const double d = *rendering_style->Transparency();
			surface_style->transparency = d;
		}
	}
	
	return surface_style;
}


taxonomy::ptr mapping::map(const IfcBaseInterface* inst) {
	// std::wcout << inst->data().toString().c_str() << std::endl;
#include "bind_convert_impl.i"
	Logger::Message(Logger::LOG_ERROR, "No operation defined for:", inst);
	return nullptr;
}

namespace {
	IfcUtil::IfcBaseEntity* get_RelatingObject(IfcSchema::IfcRelDecomposes* decompose) {
#ifdef SCHEMA_IfcRelDecomposes_HAS_RelatingObject
		return decompose->RelatingObject();
#else
		IfcSchema::IfcRelAggregates* aggr = decompose->as<IfcSchema::IfcRelAggregates>();
		if (aggr != nullptr) {
			return aggr->RelatingObject();
		}
		return nullptr;
#endif
	}
}

IfcUtil::IfcBaseEntity* mapping::get_decomposing_entity(const IfcUtil::IfcBaseEntity* inst, bool include_openings) {
	IfcSchema::IfcObjectDefinition* parent = 0;

	auto product = inst->as<IfcSchema::IfcProduct>();
	if (!product) {
		return parent;
	}

	/* In case of an opening element, parent to the RelatingBuildingElement */
	if (include_openings && product->declaration().is(IfcSchema::IfcOpeningElement::Class())) {
		IfcSchema::IfcOpeningElement* opening = (IfcSchema::IfcOpeningElement*)product;
		IfcSchema::IfcRelVoidsElement::list::ptr voids = opening->VoidsElements();
		if (voids->size()) {
			IfcSchema::IfcRelVoidsElement* ifc_void = *voids->begin();
			parent = ifc_void->RelatingBuildingElement();
		}
	} else if (product->declaration().is(IfcSchema::IfcElement::Class())) {
		IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)product;
		IfcSchema::IfcRelFillsElement::list::ptr fills = element->FillsVoids();
		/* In case of a RelatedBuildingElement parent to the opening element */
		if (fills->size() && include_openings) {
			for (IfcSchema::IfcRelFillsElement::list::it it = fills->begin(); it != fills->end(); ++it) {
				IfcSchema::IfcRelFillsElement* fill = *it;
				IfcSchema::IfcObjectDefinition* ifc_objectdef = fill->RelatingOpeningElement();
				if (product == ifc_objectdef) continue;
				parent = ifc_objectdef;
			}
		}
		/* Else simply parent to the containing structure */
		if (!parent) {
			IfcSchema::IfcRelContainedInSpatialStructure::list::ptr parents = element->ContainedInStructure();
			if (parents->size()) {
				IfcSchema::IfcRelContainedInSpatialStructure* container = *parents->begin();
				parent = container->RelatingStructure();
			}
		}
	}

	/* Parent decompositions to the RelatingObject */
	if (!parent) {
		aggregate_of_instance::ptr parents = product->data().getInverse((&IfcSchema::IfcRelAggregates::Class()), -1);
		parents->push(product->data().getInverse((&IfcSchema::IfcRelNests::Class()), -1));
		for (aggregate_of_instance::it it = parents->begin(); it != parents->end(); ++it) {
			IfcSchema::IfcRelDecomposes* decompose = (*it)->as<IfcSchema::IfcRelDecomposes>();
			IfcUtil::IfcBaseEntity* ifc_objectdef;
                 																								
			ifc_objectdef = get_RelatingObject(decompose);

			if (!ifc_objectdef || product == ifc_objectdef) continue;
			parent = ifc_objectdef->as<IfcSchema::IfcObjectDefinition>();
		}
	}
	return parent;
}

std::map<std::string, IfcUtil::IfcBaseEntity*> mapping::get_layers(IfcUtil::IfcBaseEntity* inst) {
	auto prod = inst->as<IfcSchema::IfcProduct>();
	std::map<std::string, IfcUtil::IfcBaseEntity*> layers;
	if (prod->Representation()) {
		aggregate_of_instance::ptr r = IfcParse::traverse(prod->Representation());
		IfcSchema::IfcRepresentation::list::ptr representations = r->as<IfcSchema::IfcRepresentation>();
		for (IfcSchema::IfcRepresentation::list::it it = representations->begin(); it != representations->end(); ++it) {
			IfcSchema::IfcPresentationLayerAssignment::list::ptr a = (*it)->LayerAssignments();
			for (IfcSchema::IfcPresentationLayerAssignment::list::it jt = a->begin(); jt != a->end(); ++jt) {
				layers[(*jt)->Name()] = *jt;
			}
		}
	}
	return layers;
}

void mapping::initialize_units_() {
	// Set default units, set length to meters, angles to undefined
	length_unit_ = 1.;
	angle_unit_ = -1.;
	length_unit_name_ = "METER";
	
	auto unit_assignments = file_->instances_by_type<IfcSchema::IfcUnitAssignment>();
	if (unit_assignments->size() != 1) {
		Logger::Warning("Not a single unit assignment in file");
	}
	auto unit_assignment = *unit_assignments->begin();

	bool length_unit_encountered = false, angle_unit_encountered = false;

	try {
		aggregate_of_instance::ptr units = unit_assignment->Units();
		if (!units || !units->size()) {
			Logger::Warning("No unit information found");
		} else {
			for (aggregate_of_instance::it it = units->begin(); it != units->end(); ++it) {
				IfcUtil::IfcBaseClass* base = *it;
				if (base->declaration().is(IfcSchema::IfcNamedUnit::Class())) {
					IfcSchema::IfcNamedUnit* named_unit = base->as<IfcSchema::IfcNamedUnit>();
					if (named_unit->UnitType() == IfcSchema::IfcUnitEnum::IfcUnit_LENGTHUNIT ||
						named_unit->UnitType() == IfcSchema::IfcUnitEnum::IfcUnit_PLANEANGLEUNIT) {
						std::string current_unit_name;
						const double current_unit_magnitude = IfcParse::get_SI_equivalent<IfcSchema>(named_unit);
						if (current_unit_magnitude != 0.) {
							if (named_unit->declaration().is(IfcSchema::IfcConversionBasedUnit::Class())) {
								IfcSchema::IfcConversionBasedUnit* u = (IfcSchema::IfcConversionBasedUnit*)base;
								current_unit_name = u->Name();
							} else if (named_unit->declaration().is(IfcSchema::IfcSIUnit::Class())) {
								IfcSchema::IfcSIUnit* si_unit = named_unit->as<IfcSchema::IfcSIUnit>();
								if (si_unit->Prefix()) {
									current_unit_name = IfcSchema::IfcSIPrefix::ToString(*si_unit->Prefix());
								}
								current_unit_name += IfcSchema::IfcSIUnitName::ToString(si_unit->Name());
							}
							if (named_unit->UnitType() == IfcSchema::IfcUnitEnum::IfcUnit_LENGTHUNIT) {
								length_unit_name_ = current_unit_name;
								length_unit_ = current_unit_magnitude;
								length_unit_encountered = true;
							} else {
								angle_unit_ = current_unit_magnitude;
								angle_unit_encountered = true;
							}
						}
					}
				}
			}
		}
	} catch (const IfcParse::IfcException& ex) {
		std::stringstream ss;
		ss << "Failed to determine unit information '" << ex.what() << "'";
		Logger::Message(Logger::LOG_ERROR, ss.str());
	}

	if (!length_unit_encountered) {
		Logger::Warning("No length unit encountered");
	}

	if (!angle_unit_encountered) {
		Logger::Warning("No plane angle unit encountered");
	}
}

void mapping::initialize_settings() {
	conv_settings_.setValue(ConversionSettings::GV_LENGTH_UNIT, length_unit_);
	conv_settings_.setValue(ConversionSettings::GV_PLANEANGLE_UNIT, angle_unit_);

	// Set precision from file
	double lowest_precision_encountered = std::numeric_limits<double>::infinity();
	bool any_precision_encountered = false;

	IfcSchema::IfcGeometricRepresentationContext::list::it it;
	IfcSchema::IfcGeometricRepresentationContext::list::ptr contexts =
		file_->instances_by_type_excl_subtypes<IfcSchema::IfcGeometricRepresentationContext>();

	for (it = contexts->begin(); it != contexts->end(); ++it) {
		IfcSchema::IfcGeometricRepresentationContext* context = *it;

		// See if there is a context_id filter and whether the context is selected
		if (!settings_.context_ids().empty()) {
			if (settings_.context_ids().find(context->data().id()) == settings_.context_ids().end()) {
				bool selected_sub_context = false;
				auto subs = context->HasSubContexts();
				for (auto& sub : *subs) {
					if (settings_.context_ids().find(context->data().id()) != settings_.context_ids().end()) {
						selected_sub_context = true;
						break;
					}
				}
				if (!selected_sub_context) {
					continue;
				}
			}
		}

		if (context->Precision() && (*context->Precision() * length_unit_ * 10.) < lowest_precision_encountered) {
			// Some arbitrary factor that has proven to work better for the models in the set of test files.
			lowest_precision_encountered = *context->Precision() * length_unit_ * 10.;
			any_precision_encountered = true;
		}
	}

	double precision_to_set = 1.e-5;

	if (any_precision_encountered) {
		if (lowest_precision_encountered < 1.e-7) {
			Logger::Message(Logger::LOG_WARNING, "Precision lower than 0.0000001 meter not enforced");
			precision_to_set = 1.e-7;
		} else {
			precision_to_set = lowest_precision_encountered;
		}
	}

	conv_settings_.setValue(ConversionSettings::GV_PRECISION, precision_to_set);
}

bool mapping::get_layerset_information(const IfcUtil::IfcBaseInterface* p, layerset_information& info, int &)
{
	const IfcSchema::IfcProduct* product = p->as<IfcSchema::IfcProduct>();

	if (!product) {
		return false;
	}

	IfcSchema::IfcMaterialLayerSetUsage* usage = 0;
	// Handle_Geom_Surface reference_surface;

	IfcSchema::IfcRelAssociates::list::ptr associations = product->HasAssociations();
	for (IfcSchema::IfcRelAssociates::list::it it = associations->begin(); it != associations->end(); ++it) {
		IfcSchema::IfcRelAssociatesMaterial* associates_material = (**it).as<IfcSchema::IfcRelAssociatesMaterial>();
		if (associates_material) {
			usage = associates_material->RelatingMaterial()->as<IfcSchema::IfcMaterialLayerSetUsage>();
			break;
		}
	}

	if (!usage) {
		return false;
	}

	IfcSchema::IfcRepresentation* body_representation = find_representation(product, "Body");

	if (!body_representation) {
		Logger::Warning("No body representation for product", product);
		return false;
	}

	const IfcSchema::IfcMaterialLayerSet* layerset = usage->ForLayerSet();
	const bool positive = usage->DirectionSense() == IfcSchema::IfcDirectionSenseEnum::IfcDirectionSense_POSITIVE;
	double offset = usage->OffsetFromReferenceLine() * this->length_unit_;

	IfcSchema::IfcMaterialLayer::list::ptr material_layers = layerset->MaterialLayers();

	if (product->declaration().is(IfcSchema::IfcWall::Class())) {
		IfcSchema::IfcRepresentation* axis_representation = find_representation(product, "Axis");

		if (!axis_representation) {
			Logger::Message(Logger::LOG_WARNING, "No axis representation for:", product);
			return false;
		}

		auto curve = map(axis_representation);
		auto product_node = taxonomy::cast<taxonomy::geom_item>(map(product));

		auto& m4 = product_node->matrix;
		auto c2 = flatten(taxonomy::cast<taxonomy::collection>(curve));
		if (c2->children.empty()) {
			return false;
		}

#ifdef TAXONOMY_USE_NAKED_PTR
		delete curve;
		delete product_node;
#endif

		auto c = c2->children[0];

		auto Z = taxonomy::make<taxonomy::direction3>(0, 0, 1);;

		auto ofc = taxonomy::make<taxonomy::offset_curve>();
		ofc->offset = -offset;
		ofc->reference = Z;
		ofc->basis = c2->children[0];
		ofc->matrix = m4;
		info.layers.push_back(ofc);

		for (IfcSchema::IfcMaterialLayer::list::it it = material_layers->begin(); it != material_layers->end(); ++it) {
			info.styles.push_back(*taxonomy::cast<taxonomy::style>(map((*it)->Material())));

			double thickness = (*it)->LayerThickness() * this->length_unit_;

			info.thicknesses.push_back(thickness);

			if (!positive) {
				thickness *= -1;
			}

			offset += thickness;

			if (fabs(offset) < 1.e-7) {
				auto ofc = c;
				c->matrix = m4;
				info.layers.push_back(ofc);
			} else {
				auto ofc = taxonomy::make<taxonomy::offset_curve>();
				ofc->offset = -offset;
				ofc->reference = Z;
				ofc->basis = c2;
				ofc->matrix = m4;
				info.layers.push_back(ofc);
			}
		}

#ifdef TAXONOMY_USE_NAKED_PTR
		delete c2;
#endif

		if (positive) {
			std::reverse(info.thicknesses.begin(), info.thicknesses.end());
			std::reverse(info.styles.begin(), info.styles.end());
			std::reverse(info.layers.begin(), info.layers.end());
		}
	} else {
		IfcSchema::IfcExtrudedAreaSolid::list::ptr extrusions = IfcParse::traverse(body_representation)->as<IfcSchema::IfcExtrudedAreaSolid>();

		if (extrusions->size() != 1) {
			Logger::Message(Logger::LOG_WARNING, "No single extrusion found in body representation for:", product);
			return false;
		}

		IfcSchema::IfcExtrudedAreaSolid* extrusion = *extrusions->begin();

		taxonomy::matrix4::ptr extrusion_position;

		bool has_position = true;
#ifdef SCHEMA_IfcSweptAreaSolid_Position_IS_OPTIONAL
		has_position = extrusion->Position() != nullptr;
#endif
		if (has_position) {
			auto m4 = taxonomy::cast<taxonomy::matrix4>(map(extrusion->Position()));
			if (!m4) {
				Logger::Message(Logger::LOG_ERROR, "Failed to convert placement for extrusion of:", product);
				return false;
			} else {
				extrusion_position = m4;
			}
		}

		taxonomy::direction3::ptr extrusion_direction = taxonomy::cast<taxonomy::direction3>(map(extrusion->ExtrudedDirection()));

		if (!extrusion_direction) {
			Logger::Message(Logger::LOG_ERROR, "Failed to convert direction for extrusion of:", product);
			return false;
		}

		// @todo I don't think this is correct actually. This shouldn't take into account extrusion direction?
		// reference_surface = new Geom_Plane(extrusion_position.TranslationPart(), extrusion_direction);

		{
			auto pln = taxonomy::make<taxonomy::plane>();
			pln->matrix = extrusion_position;

			info.layers.push_back(pln);
		}

		for (IfcSchema::IfcMaterialLayer::list::it it = material_layers->begin(); it != material_layers->end(); ++it) {
			info.styles.push_back(*taxonomy::cast<taxonomy::style>(map((*it)->Material())));

			double thickness = (*it)->LayerThickness() * this->length_unit_;

			info.thicknesses.push_back(thickness);

			if (!positive) {
				thickness *= -1;
			}

			offset += thickness;

			auto offset_matrix = taxonomy::make<taxonomy::matrix4>();
			offset_matrix->components()(2, 3) = offset;
			offset_matrix->components()(3, 3) = 1.;
			offset_matrix->components() *= extrusion_position->components();

			auto pln = taxonomy::make<taxonomy::plane>();
			pln->matrix = offset_matrix;

			info.layers.push_back(pln);
		}

		if (positive) {
			std::reverse(info.thicknesses.begin(), info.thicknesses.end());
			std::reverse(info.styles.begin(), info.styles.end());
			std::reverse(info.layers.begin(), info.layers.end());
		}

	}

	

	return true;
}

bool mapping::get_wall_neighbours(const IfcUtil::IfcBaseInterface *, std::vector<endpoint_connection>&)
{
	return false;
}

IfcSchema::IfcRepresentation* mapping::find_representation(const IfcSchema::IfcProduct* product, const std::string& identifier) {
	if (!product->Representation()) return 0;
	IfcSchema::IfcProductRepresentation* prod_rep = product->Representation();
	IfcSchema::IfcRepresentation::list::ptr reps = prod_rep->Representations();
	for (IfcSchema::IfcRepresentation::list::it it = reps->begin(); it != reps->end(); ++it) {
		if ((**it).RepresentationIdentifier() && (*(**it).RepresentationIdentifier()) == identifier) {
			return *it;
		}
	}
	return 0;
}

void mapping::addRepresentationsFromContextIds(IfcSchema::IfcRepresentation::list::ptr& representations) {
	for (auto context_id : settings_.context_ids()) {
		IfcSchema::IfcGeometricRepresentationContext* context;
		try {
			context = file_->instance_by_id(context_id)->as<IfcSchema::IfcGeometricRepresentationContext>();
		} catch (IfcParse::IfcException& e) {
			Logger::Error(e);
		}

		if (!context) {
			Logger::Error("Failed to process context ID " + std::to_string(context_id));
			continue;
		}

		representations->push(context->RepresentationsInContext());
	}
}

void mapping::addRepresentationsFromDefaultContexts(IfcSchema::IfcRepresentation::list::ptr& representations) {
	std::set<std::string> allowed_context_types;
	allowed_context_types.insert("model");
	allowed_context_types.insert("plan");
	allowed_context_types.insert("notdefined");

	std::set<std::string> context_types;
	if (!settings_.get(IfcGeom::IteratorSettings::EXCLUDE_SOLIDS_AND_SURFACES)) {
		// Really this should only be 'Model', as per
		// the standard 'Design' is deprecated. So,
		// just for backwards compatibility:
		context_types.insert("model");
		context_types.insert("design");
		// Some earlier (?) versions DDS-CAD output their own ContextTypes
		context_types.insert("model view");
		context_types.insert("detail view");
	}
	if (settings_.get(IfcGeom::IteratorSettings::INCLUDE_CURVES)) {
		context_types.insert("plan");
	}

	IfcSchema::IfcGeometricRepresentationContext::list::it it;
	IfcSchema::IfcGeometricRepresentationSubContext::list::it jt;
	IfcSchema::IfcGeometricRepresentationContext::list::ptr contexts =
		file_->instances_by_type<IfcSchema::IfcGeometricRepresentationContext>();

	IfcSchema::IfcGeometricRepresentationContext::list::ptr filtered_contexts(new IfcSchema::IfcGeometricRepresentationContext::list);

	for (it = contexts->begin(); it != contexts->end(); ++it) {
		IfcSchema::IfcGeometricRepresentationContext* context = *it;
		if (context->declaration().is(IfcSchema::IfcGeometricRepresentationSubContext::Class())) {
			// Continue, as the list of subcontexts will be considered
			// by the parent's context inverse attributes.
			continue;
		}
		try {
			if (context->ContextType()) {
				std::string context_type = *context->ContextType();
				boost::to_lower(context_type);

				if (allowed_context_types.find(context_type) == allowed_context_types.end()) {
					Logger::Warning(std::string("ContextType '") + *context->ContextType() + "' not allowed:", context);
				}
				if (context_types.find(context_type) != context_types.end()) {
					filtered_contexts->push(context);
				}
			}
		} catch (const std::exception& e) {
			Logger::Error(e);
		}
	}

	// In case no contexts are identified based on their ContextType, all contexts are
	// considered. Note that sub contexts are excluded as they are considered later on.
	if (filtered_contexts->size() == 0) {
		for (it = contexts->begin(); it != contexts->end(); ++it) {
			IfcSchema::IfcGeometricRepresentationContext* context = *it;
			if (!context->declaration().is(IfcSchema::IfcGeometricRepresentationSubContext::Class())) {
				filtered_contexts->push(context);
			}
		}
	}

	for (it = filtered_contexts->begin(); it != filtered_contexts->end(); ++it) {
		IfcSchema::IfcGeometricRepresentationContext* context = *it;

		representations->push(context->RepresentationsInContext());

		IfcSchema::IfcGeometricRepresentationSubContext::list::ptr sub_contexts = context->HasSubContexts();
		for (jt = sub_contexts->begin(); jt != sub_contexts->end(); ++jt) {
			representations->push((*jt)->RepresentationsInContext());
		}

		// There is no need for full recursion as the following is governed by the schema:
		// WR31: The parent context shall not be another geometric representation sub context.
	}

	if (representations->size() == 0) {
		Logger::Warning("No representations encountered in relevant contexts, using all");
		representations->push(file_->instances_by_type<IfcSchema::IfcRepresentation>());
	}
}

void mapping::apply_settings() {
	conv_settings_.setValue(ConversionSettings::GV_MAX_FACES_TO_ORIENT, settings_.get(IfcGeom::IteratorSettings::SEW_SHELLS) ? std::numeric_limits<double>::infinity() : -1);
	conv_settings_.setValue(ConversionSettings::GV_DIMENSIONALITY, (settings_.get(IfcGeom::IteratorSettings::INCLUDE_CURVES)
		? (settings_.get(IfcGeom::IteratorSettings::EXCLUDE_SOLIDS_AND_SURFACES) ? -1. : 0.) : +1.));
	conv_settings_.setValue(ConversionSettings::GV_LAYERSET_FIRST,
		settings_.get(IfcGeom::IteratorSettings::LAYERSET_FIRST)
		? +1.0
		: -1.0
	);
	conv_settings_.setValue(ConversionSettings::GV_NO_WIRE_INTERSECTION_CHECK,
		settings_.get(IfcGeom::IteratorSettings::NO_WIRE_INTERSECTION_CHECK)
		? +1.0
		: -1.0
	);
	conv_settings_.setValue(ConversionSettings::GV_NO_WIRE_INTERSECTION_TOLERANCE,
		settings_.get(IfcGeom::IteratorSettings::NO_WIRE_INTERSECTION_TOLERANCE)
		? +1.0
		: -1.0
	);
	conv_settings_.setValue(ConversionSettings::GV_PRECISION_FACTOR,
		settings_.get(IfcGeom::IteratorSettings::STRICT_TOLERANCE)
		? 1.0
		: 10.0
	);

	conv_settings_.setValue(ConversionSettings::GV_DISABLE_BOOLEAN_RESULT,
		settings_.get(IfcGeom::IteratorSettings::DISABLE_BOOLEAN_RESULT)
		? +1.0
		: -1.0
	);

	conv_settings_.setValue(ConversionSettings::GV_DEBUG_BOOLEAN,
		settings_.get(IfcGeom::IteratorSettings::DEBUG_BOOLEAN)
		? +1.0
		: -1.0
	);

	conv_settings_.setValue(ConversionSettings::GV_BOOLEAN_ATTEMPT_2D,
		settings_.get(IfcGeom::IteratorSettings::BOOLEAN_ATTEMPT_2D)
		? +1.0
		: -1.0
	);

	if (settings_.get(IfcGeom::IteratorSettings::BUILDING_LOCAL_PLACEMENT)) {
		if (settings_.get(IfcGeom::IteratorSettings::SITE_LOCAL_PLACEMENT)) {
			Logger::Message(Logger::LOG_WARNING, "building-local-placement takes precedence over site-local-placement");
		}
		placement_rel_to_type_ = &IfcSchema::IfcBuilding::Class();
	} else if (settings_.get(IfcGeom::IteratorSettings::SITE_LOCAL_PLACEMENT)) {
		placement_rel_to_type_ = &IfcSchema::IfcSite::Class();
	}

	// @todo
	// conv_settings_.set_offset(settings_.offset);
	// conv_settings_.set_rotation(settings_.rotation);
}

IfcUtil::IfcBaseEntity* mapping::representation_of(const IfcUtil::IfcBaseEntity* product) {
	// @todo correct, but very inefficient
	IfcSchema::IfcRepresentation::list::ptr representations(new IfcSchema::IfcRepresentation::list);
	IfcSchema::IfcRepresentation::list::ptr of_product(new IfcSchema::IfcRepresentation::list);
	IfcSchema::IfcRepresentation::list::ptr intersection(new IfcSchema::IfcRepresentation::list);
	IfcSchema::IfcRepresentation::list::ptr intersection_no_box(new IfcSchema::IfcRepresentation::list);

	if (settings_.context_ids().empty()) {
		addRepresentationsFromDefaultContexts(representations);
	} else {
		addRepresentationsFromContextIds(representations);
	}

	if (product->as<IfcSchema::IfcProduct>()->Representation()) {
		of_product->push(product->as<IfcSchema::IfcProduct>()->Representation()->Representations());
	}

	for (auto& r : *of_product) {
		if (representations->contains(r)) {
			intersection->push(r);
		}
	}

	if (intersection->size() == 0 && settings_.context_ids().empty() && settings_.get(IfcGeom::IteratorSettings::INCLUDE_CURVES) && settings_.get(IfcGeom::IteratorSettings::EXCLUDE_SOLIDS_AND_SURFACES)) {
		for (auto& r : *of_product) {
			if (r->RepresentationIdentifier() && *r->RepresentationIdentifier() == "Axis") {
				intersection->push(r);
			}
		}
	}

	if (intersection->size() == 0) {
		return nullptr;
	} else {
		for (auto& r : *intersection) {
			if (IfcParse::traverse((r))->as<IfcSchema::IfcBoundingBox>()->size()) {
				continue;
			}
			intersection_no_box->push(r);
		}
		if (intersection_no_box->size() > 1) {
			Logger::Warning("Multiple applicable representations found for element, selecting arbitrary");
		}
		if (intersection_no_box->size()) {
			return (*intersection_no_box->begin())->as<IfcUtil::IfcBaseEntity>();
		} else {
			return (*intersection->begin())->as<IfcUtil::IfcBaseEntity>();
		}
	}
}
