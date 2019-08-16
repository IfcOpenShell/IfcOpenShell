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

#include "mapping.h"

#include "../../ifcparse/IfcLogger.h"
#include "../../ifcparse/IfcFile.h"

using namespace IfcUtil;
using namespace ifcopenshell::geometry;

namespace {
	struct POSTFIX_SCHEMA(factory_t) {
		abstract_mapping* operator()(IfcParse::IfcFile* file) const {
			ifcopenshell::geometry::POSTFIX_SCHEMA(mapping)* m = new ifcopenshell::geometry::POSTFIX_SCHEMA(mapping)(file);
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

namespace {
	// Hacks around not wanting to use if constexpr
	template <typename T>
	class loop_to_face_upgrade {
	public:
		loop_to_face_upgrade(taxonomy::item*) {}

		operator bool() const {
			return false;
		}

		operator taxonomy::face() const {
			throw taxonomy::topology_error();
		}

		operator T() const {
			throw taxonomy::topology_error();
		}
	};

	template <>
	class loop_to_face_upgrade<taxonomy::face> {
	private:
		boost::optional<taxonomy::face> face_;
	public:
		loop_to_face_upgrade(taxonomy::item* item) {
			taxonomy::loop* loop = dynamic_cast<taxonomy::loop*>(item);
			if (loop) {
				face_ = taxonomy::face(loop->instance, loop->matrix, *loop);
			}
		}

		operator bool() const {
			return face_.is_initialized();
		}

		operator taxonomy::face() const {
			return *face_;
		}
	};

	// A RAII-based mechanism to cast the conversion results
	// from map() into the right type expected by the higher
	// level typology items. An exception is thrown if the
	// types do not match or the result was nullptr. A copy
	// will be assigned to the higher level topology member
	// and the original pointer will be deleted.

	// This class is also able to uplift some topology items
	// to higher level types, such as a loop to a face, which
	// is why the cast operator does not return a reference.
	template <typename T>
	class as {
	private:
		taxonomy::item* item_;

	public:
		as(taxonomy::item* item) : item_(item) {}
		operator T() const {
			if (!item_) {
				throw taxonomy::topology_error();
			}
			T* t = dynamic_cast<T*>(item_);
			if (t) {
				return *t;
			} else {
				{
					loop_to_face_upgrade<T> upgrade(item_);
					if (upgrade) {
						return upgrade;
					}
				}
				throw taxonomy::topology_error();
			}
		}
		~as() {
			delete item_;
		}
	};
};

taxonomy::item* mapping::map(const IfcSchema::IfcExtrudedAreaSolid* inst) {
	// @todo length unit
	return new taxonomy::extrusion(
		inst,
		as<taxonomy::matrix4>(map(inst->Position())),
		as<taxonomy::face>(map(inst->SweptArea())),
		as<taxonomy::direction3>(map(inst->ExtrudedDirection())),
		inst->Depth()
	);
}

taxonomy::item* mapping::map(const IfcSchema::IfcAxis2Placement3D* inst) {
	// @todo length unit
	return new taxonomy::matrix4();
}

IfcSchema::IfcProduct::list::ptr mapping::products_represented_by(const IfcSchema::IfcRepresentation* representation) {
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

	IfcSchema::IfcRepresentationMap::list::ptr maps = representation->RepresentationMap();
	if (maps->size() == 1) {
		IfcSchema::IfcRepresentationMap* rmap = *maps->begin();
		taxonomy::matrix4 origin = as<taxonomy::matrix4>(map(rmap->MappingOrigin()));
		if (origin.components.isIdentity()) {
			IfcSchema::IfcMappedItem::list::ptr items = rmap->MapUsage();
			for (IfcSchema::IfcMappedItem::list::it it = items->begin(); it != items->end(); ++it) {
				IfcSchema::IfcMappedItem* item = *it;
				if (item->StyledByItem()->size() != 0) continue;

				taxonomy::matrix4 target = as<taxonomy::matrix4>(map(item->MappingTarget()));
				if (target.components.isIdentity()) {
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

bool mapping::reuse_ok_(settings& s, const IfcSchema::IfcProduct::list::ptr& products) {
	// With world coords enabled, object transformations are directly applied to
	// the BRep. There is no way to re-use the geometry for multiple products.
	if (s.get(settings::USE_WORLD_COORDS)) {
		return false;
	}

	std::set<const IfcSchema::IfcMaterial*> associated_single_materials;

	for (IfcSchema::IfcProduct::list::it it = products->begin(); it != products->end(); ++it) {
		IfcSchema::IfcProduct* product = *it;

		if (!s.get(settings::DISABLE_OPENING_SUBTRACTIONS) && find_openings(product)->size()) {
			return false;
		}

		if (s.get(settings::APPLY_LAYERSETS)) {
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

IfcEntityList::ptr mapping::find_openings(IfcSchema::IfcProduct* product) {

	IfcEntityList::ptr openings(new IfcEntityList);
	if (product->declaration().is(IfcSchema::IfcElement::Class()) && !product->declaration().is(IfcSchema::IfcOpeningElement::Class())) {
		IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)product;
		openings = element->HasOpenings()->generalize();
	}

	// Is the IfcElement a decomposition of an IfcElement with any IfcOpeningElements?
	IfcSchema::IfcObjectDefinition* obdef = product->as<IfcSchema::IfcObjectDefinition>();
	for (;;) {
		auto decomposes = obdef->Decomposes()->generalize();
		if (decomposes->size() != 1) break;
		IfcSchema::IfcObjectDefinition* rel_obdef = (*decomposes->begin())->as<IfcSchema::IfcRelAggregates>()->RelatingObject();
		if (rel_obdef->declaration().is(IfcSchema::IfcElement::Class()) && !rel_obdef->declaration().is(IfcSchema::IfcOpeningElement::Class())) {
			IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)rel_obdef;
			openings->push(element->HasOpenings()->generalize());
		}

		obdef = rel_obdef;
	}

	return openings;
}


void mapping::get_representations(std::vector<geometry_conversion_task>& tasks, std::vector<filter_t>& filters, settings& s) {
	IfcSchema::IfcRepresentation::list::ptr representations(new IfcSchema::IfcRepresentation::list);

	std::set<std::string> allowed_context_types;
	allowed_context_types.insert("model");
	allowed_context_types.insert("plan");
	allowed_context_types.insert("notdefined");

	std::set<std::string> context_types;
	if (!s.get(settings::EXCLUDE_SOLIDS_AND_SURFACES)) {
		// Really this should only be 'Model', as per 
		// the standard 'Design' is deprecated. So,
		// just for backwards compatibility:
		context_types.insert("model");
		context_types.insert("design");
		// Some earlier (?) versions DDS-CAD output their own ContextTypes
		context_types.insert("model view");
		context_types.insert("detail view");
	}
	if (s.get(settings::INCLUDE_CURVES)) {
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
			if (context->hasContextType()) {
				std::string context_type = context->ContextType();
				boost::to_lower(context_type);

				if (allowed_context_types.find(context_type) == allowed_context_types.end()) {
					Logger::Warning(std::string("ContextType '") + context->ContextType() + "' not allowed:", context);
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
		representations = file_->instances_by_type<IfcSchema::IfcRepresentation>();
	}

	IfcSchema::IfcRepresentation::list::ptr ok_mapped_representations;

	int task_index = 0;
	
	for (auto representation : *representations) {

		// Init. the list of filtered IfcProducts for this representation
		
		// Include only the desired products for processing.
		IfcSchema::IfcProduct::list::ptr ifcproducts = filter_products(products_represented_by(representation), filters);
		
		if (ifcproducts->size() == 0) {
			continue;
		}

		auto geometry_reuse_ok_for_current_representation_ = reuse_ok_(s, ifcproducts);

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

		// Check if this represenation has (or will be) processed as part its mapped representation
		bool representation_processed_as_mapped_item = false;
		IfcSchema::IfcRepresentation* rep_mapped_to = representation_mapped_to(representation);
		if (rep_mapped_to) {
			representation_processed_as_mapped_item = geometry_reuse_ok_for_current_representation_ && (
				ok_mapped_representations->contains(rep_mapped_to) || reuse_ok_(s, filter_products(products_represented_by(rep_mapped_to), filters)));
		}

		if (representation_processed_as_mapped_item) {
			ok_mapped_representations->push(rep_mapped_to);
			continue;
		}

		geometry_conversion_task task;
		task.index = task_index++;
		task.representation = representation;
		task.products = ifcproducts->generalize();

		tasks.emplace_back(task);
	}
}

const IfcSchema::IfcMaterial* mapping::get_single_material_association(const IfcSchema::IfcProduct* product) {
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
				if (layer->hasMaterial()) {
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
				taxonomy::matrix4 target = as<taxonomy::matrix4>(map(mapped_item->MappingTarget()));
				if (target.components.isIdentity()) {
					IfcSchema::IfcRepresentationMap* rmap = mapped_item->MappingSource();
					taxonomy::matrix4 origin = as<taxonomy::matrix4>(map(rmap->MappingOrigin()));
					if (origin.components.isIdentity()) {
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
		IfcEntityList::ptr style_assignments = si->Styles();
		for (IfcEntityList::it kt = style_assignments->begin(); kt != style_assignments->end(); ++kt) {
			if (!(*kt)->declaration().is(IfcSchema::IfcPresentationStyleAssignment::Class())) {
				continue;
			}
			IfcSchema::IfcPresentationStyleAssignment* style_assignment = (IfcSchema::IfcPresentationStyleAssignment*) *kt;
#else
		IfcSchema::IfcPresentationStyleAssignment::list::ptr style_assignments = si->Styles();
		for (IfcSchema::IfcPresentationStyleAssignment::list::it kt = style_assignments->begin(); kt != style_assignments->end(); ++kt) {
			IfcSchema::IfcPresentationStyleAssignment* style_assignment = *kt;
#endif
			IfcEntityList::ptr styles = style_assignment->Styles();
			for (IfcEntityList::it lt = styles->begin(); lt != styles->end(); ++lt) {
				IfcUtil::IfcBaseClass* style = *lt;
				if (style->declaration().is(IfcSchema::IfcSurfaceStyle::Class())) {
					IfcSchema::IfcSurfaceStyle* surface_style = (IfcSchema::IfcSurfaceStyle*) style;
					if (surface_style->Side() != IfcSchema::IfcSurfaceSide::IfcSurfaceSide_NEGATIVE) {
						IfcEntityList::ptr styles_elements = surface_style->Styles();
						for (IfcEntityList::it mt = styles_elements->begin(); mt != styles_elements->end(); ++mt) {
							if ((*mt)->declaration().is(T::Class())) {
								return std::make_pair(surface_style, (T*)*mt);
							}
						}
					}
				}
			}
		}

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

taxonomy::item* mapping::map(const IfcSchema::IfcMaterial* material) {
	IfcSchema::IfcMaterialDefinitionRepresentation::list::ptr defs = material->HasRepresentation();
	for (IfcSchema::IfcMaterialDefinitionRepresentation::list::it jt = defs->begin(); jt != defs->end(); ++jt) {
		IfcSchema::IfcRepresentation::list::ptr reps = (*jt)->Representations();
		IfcSchema::IfcStyledItem::list::ptr styles(new IfcSchema::IfcStyledItem::list);
		for (IfcSchema::IfcRepresentation::list::it it = reps->begin(); it != reps->end(); ++it) {
			styles->push((**it).Items()->as<IfcSchema::IfcStyledItem>());
		}
		for (IfcSchema::IfcStyledItem::list::it it = styles->begin(); it != styles->end(); ++it) {
			return map(*it);
		}
	}

	taxonomy::style* material_style = new taxonomy::style;
	return material_style;

	// @todo
	// IfcGeom::SurfaceStyle material_style = IfcGeom::SurfaceStyle(material->data().id(), material->Name());
	// return &(style_cache[material->data().id()] = material_style);
}

taxonomy::item* mapping::map(const IfcSchema::IfcStyledItem* inst) {
	static taxonomy::colour white = taxonomy::colour(1., 1., 1.);

	taxonomy::style* surface_style = new taxonomy::style;

	auto style_pair = get_surface_style<IfcSchema::IfcSurfaceStyleShading>(inst);

	IfcSchema::IfcSurfaceStyle* style = style_pair.first;
	IfcSchema::IfcSurfaceStyleShading* shading = style_pair.second;

	surface_style->instance = style;
	if (style->hasName()) {
		surface_style->name = style->Name();
	}
	
	double rgb[3];
	if (process_colour(shading->SurfaceColour(), rgb)) {
		surface_style->diffuse.emplace();
		(*surface_style->diffuse).components << rgb[0], rgb[1], rgb[2];
	}

	if (auto rendering_style = shading->as<IfcSchema::IfcSurfaceStyleRendering>()) {
		if (rendering_style->hasDiffuseColour() && process_colour(rendering_style->DiffuseColour(), rgb)) {
			const taxonomy::colour& old_diffuse = surface_style->diffuse.get_value_or(white);
			surface_style->diffuse.reset(taxonomy::colour(old_diffuse.r() * rgb[0], old_diffuse.g() * rgb[1], old_diffuse.b() * rgb[2]));
		}
		if (rendering_style->hasDiffuseTransmissionColour()) {
			// Not supported
		}
		if (rendering_style->hasReflectionColour()) {
			// Not supported
		}
		if (rendering_style->hasSpecularColour() && process_colour(rendering_style->SpecularColour(), rgb)) {
			surface_style->specular.reset(taxonomy::colour(rgb[0], rgb[1], rgb[2]));
		}
		if (rendering_style->hasSpecularHighlight()) {
			IfcSchema::IfcSpecularHighlightSelect* highlight = rendering_style->SpecularHighlight();
			if (highlight->declaration().is(IfcSchema::IfcSpecularRoughness::Class())) {
				double roughness = *((IfcSchema::IfcSpecularRoughness*)highlight);
				if (roughness >= 1e-9) {
					surface_style->specularity.reset(1.0 / roughness);
				}
			} else if (highlight->declaration().is(IfcSchema::IfcSpecularExponent::Class())) {
				surface_style->specularity.reset(*((IfcSchema::IfcSpecularExponent*)highlight));
			}
		}
		if (rendering_style->hasTransmissionColour()) {
			// Not supported
		}
		if (rendering_style->hasTransparency()) {
			const double d = rendering_style->Transparency();
			surface_style->transparency.reset(d);
		}
	}
	
	return surface_style;
}


taxonomy::item* mapping::map(const IfcBaseClass* l) {
#include "bind_convert_impl.i"
	Logger::Message(Logger::LOG_ERROR, "No operation defined for:", l);
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


IfcUtil::IfcBaseEntity* get_decomposing_entity(IfcUtil::IfcBaseEntity* inst, bool include_openings) {
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
		IfcEntityList::ptr parents = product->data().getInverse((&IfcSchema::IfcRelAggregates::Class()), -1);
		parents->push(product->data().getInverse((&IfcSchema::IfcRelNests::Class()), -1));
		for (IfcEntityList::it it = parents->begin(); it != parents->end(); ++it) {
			IfcSchema::IfcRelDecomposes* decompose = (IfcSchema::IfcRelDecomposes*)*it;
			IfcUtil::IfcBaseEntity* ifc_objectdef;
			ifc_objectdef = get_RelatingObject(decompose);
			if (product == ifc_objectdef) continue;
			parent = ifc_objectdef->as<IfcSchema::IfcObjectDefinition>();
		}
	}

	return parent;
}
