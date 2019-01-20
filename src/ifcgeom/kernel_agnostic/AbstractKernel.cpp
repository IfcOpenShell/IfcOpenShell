#include "AbstractKernel.h"

#include "../../ifcgeom/schema_agnostic/IfcGeomElement.h"

#define AbstractKernel MAKE_TYPE_NAME(AbstractKernel)

void IfcGeom::AbstractKernel::set_conversion_placement_rel_to(const IfcParse::declaration* type) {
	placement_rel_to = type;
}

void IfcGeom::AbstractKernel::setValue(GeomValue var, double value) {
	switch (var) {
	case GV_DEFLECTION_TOLERANCE:
		deflection_tolerance = value;
		break;
	case GV_WIRE_CREATION_TOLERANCE:
		wire_creation_tolerance = value;
		break;
	case GV_POINT_EQUALITY_TOLERANCE:
		point_equality_tolerance = value;
		break;
	case GV_LENGTH_UNIT:
		ifc_length_unit = value;
		break;
	case GV_PLANEANGLE_UNIT:
		ifc_planeangle_unit = value;
		break;
	case GV_PRECISION:
		modelling_precision = value;
		break;
	case GV_DIMENSIONALITY:
		dimensionality = value;
		break;
	default:
		assert(!"never reach here");
	}
}

double IfcGeom::AbstractKernel::getValue(GeomValue var) const {
	switch (var) {
	case GV_DEFLECTION_TOLERANCE:
		return deflection_tolerance;
	case GV_WIRE_CREATION_TOLERANCE:
		return wire_creation_tolerance;
	case GV_MINIMAL_FACE_AREA:
		// Considering a right-angled triangle, this about the smallest
		// area you can obtain without the vertices being confused.
		return modelling_precision * modelling_precision / 2.;
	case GV_POINT_EQUALITY_TOLERANCE:
		return point_equality_tolerance;
	case GV_LENGTH_UNIT:
		return ifc_length_unit;
		break;
	case GV_PLANEANGLE_UNIT:
		return ifc_planeangle_unit;
		break;
	case GV_PRECISION:
		return modelling_precision;
		break;
	case GV_DIMENSIONALITY:
		return dimensionality;
		break;
	}
	assert(!"never reach here");
	return 0;
}

const IfcSchema::IfcMaterial* IfcGeom::AbstractKernel::get_single_material_association(const IfcSchema::IfcProduct* product) {
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

IfcSchema::IfcRepresentation* IfcGeom::AbstractKernel::representation_mapped_to(const IfcSchema::IfcRepresentation* representation) {
	IfcSchema::IfcRepresentation* representation_mapped_to = 0;
	IfcSchema::IfcRepresentationItem::list::ptr items = representation->Items();
	if (items->size() == 1) {
		IfcSchema::IfcRepresentationItem* item = *items->begin();
		if (item->declaration().is(IfcSchema::IfcMappedItem::Class())) {
			if (item->StyledByItem()->size() == 0) {
				IfcSchema::IfcMappedItem* mapped_item = item->as<IfcSchema::IfcMappedItem>();
				if (is_identity_transform(mapped_item->MappingTarget())) {
					IfcSchema::IfcRepresentationMap* map = mapped_item->MappingSource();
					if (is_identity_transform(map->MappingOrigin())) {
						representation_mapped_to = map->MappedRepresentation();
					}
				}
			}
		}
	}
	return representation_mapped_to;
}

IfcSchema::IfcProduct::list::ptr IfcGeom::AbstractKernel::products_represented_by(const IfcSchema::IfcRepresentation* representation) {
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
		IfcSchema::IfcRepresentationMap* map = *maps->begin();
		if (is_identity_transform(map->MappingOrigin())) {
			IfcSchema::IfcMappedItem::list::ptr items = map->MapUsage();
			for (IfcSchema::IfcMappedItem::list::it it = items->begin(); it != items->end(); ++it) {
				IfcSchema::IfcMappedItem* item = *it;
				if (item->StyledByItem()->size() != 0) continue;

				if (!is_identity_transform(item->MappingTarget())) {
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
	std::pair<IfcSchema::IfcSurfaceStyle*, T*> _get_surface_style(const IfcSchema::IfcStyledItem* si) {
#ifdef USE_IFC4
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

	template <typename T>
	std::pair<IfcSchema::IfcSurfaceStyle*, T*> get_surface_style(const IfcSchema::IfcRepresentationItem* representation_item) {
		// For certain representation items, most notably boolean operands,
		// a style definition might reside on one of its operands.
		representation_item = find_item_carrying_style(representation_item);

		if (representation_item->as<IfcSchema::IfcStyledItem>()) {
			return _get_surface_style<T>(representation_item->as<IfcSchema::IfcStyledItem>());
		}
		IfcSchema::IfcStyledItem::list::ptr styled_items = representation_item->StyledByItem();
		if (styled_items->size()) {
			// StyledByItem is a SET [0:1] OF IfcStyledItem, so we return after the first IfcStyledItem:
			return _get_surface_style<T>(*styled_items->begin());
		}
		return std::make_pair<IfcSchema::IfcSurfaceStyle*, T*>(0, 0);
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

const IfcGeom::SurfaceStyle* IfcGeom::AbstractKernel::get_style(const IfcSchema::IfcRepresentationItem* item) {
	return internalize_surface_style(get_surface_style<IfcSchema::IfcSurfaceStyleShading>(item));
}

const IfcGeom::SurfaceStyle* IfcGeom::AbstractKernel::get_style(const IfcSchema::IfcMaterial* material) {
	IfcSchema::IfcMaterialDefinitionRepresentation::list::ptr defs = material->HasRepresentation();
	for (IfcSchema::IfcMaterialDefinitionRepresentation::list::it jt = defs->begin(); jt != defs->end(); ++jt) {
		IfcSchema::IfcRepresentation::list::ptr reps = (*jt)->Representations();
		IfcSchema::IfcStyledItem::list::ptr styles(new IfcSchema::IfcStyledItem::list);
		for (IfcSchema::IfcRepresentation::list::it it = reps->begin(); it != reps->end(); ++it) {
			styles->push((**it).Items()->as<IfcSchema::IfcStyledItem>());
		}
		for (IfcSchema::IfcStyledItem::list::it it = styles->begin(); it != styles->end(); ++it) {
			const std::pair<IfcSchema::IfcSurfaceStyle*, IfcSchema::IfcSurfaceStyleShading*> ss = get_surface_style<IfcSchema::IfcSurfaceStyleShading>(*it);
			if (ss.second) {
				return internalize_surface_style(ss);
			}
		}
	}
	IfcGeom::SurfaceStyle material_style = IfcGeom::SurfaceStyle(material->data().id(), material->Name());
	return &(style_cache[material->data().id()] = material_style);
}

const IfcGeom::SurfaceStyle* IfcGeom::AbstractKernel::internalize_surface_style(const std::pair<IfcUtil::IfcBaseClass*, IfcUtil::IfcBaseClass*>& shading_styles) {
	if (shading_styles.second == 0) {
		return 0;
	}
	int surface_style_id = shading_styles.first->data().id();
	std::map<int, SurfaceStyle>::const_iterator it = style_cache.find(surface_style_id);
	if (it != style_cache.end()) {
		return &(it->second);
	}
	SurfaceStyle surface_style;

	IfcSchema::IfcSurfaceStyle* style = shading_styles.first->as<IfcSchema::IfcSurfaceStyle>();
	IfcSchema::IfcSurfaceStyleShading* shading = shading_styles.second->as<IfcSchema::IfcSurfaceStyleShading>();

	if (style->hasName()) {
		surface_style = SurfaceStyle(surface_style_id, style->Name());
	} else {
		surface_style = SurfaceStyle(surface_style_id);
	}
	double rgb[3];
	if (process_colour(shading->SurfaceColour(), rgb)) {
		surface_style.Diffuse().reset(SurfaceStyle::ColorComponent(rgb[0], rgb[1], rgb[2]));
	}
	if (shading_styles.second->declaration().is(IfcSchema::IfcSurfaceStyleRendering::Class())) {
		IfcSchema::IfcSurfaceStyleRendering* rendering_style = static_cast<IfcSchema::IfcSurfaceStyleRendering*>(shading_styles.second);
		if (rendering_style->hasDiffuseColour() && process_colour(rendering_style->DiffuseColour(), rgb)) {
			SurfaceStyle::ColorComponent diffuse = surface_style.Diffuse().get_value_or(SurfaceStyle::ColorComponent(1, 1, 1));
			surface_style.Diffuse().reset(SurfaceStyle::ColorComponent(diffuse.R() * rgb[0], diffuse.G() * rgb[1], diffuse.B() * rgb[2]));
		}
		if (rendering_style->hasDiffuseTransmissionColour()) {
			// Not supported
		}
		if (rendering_style->hasReflectionColour()) {
			// Not supported
		}
		if (rendering_style->hasSpecularColour() && process_colour(rendering_style->SpecularColour(), rgb)) {
			surface_style.Specular().reset(SurfaceStyle::ColorComponent(rgb[0], rgb[1], rgb[2]));
		}
		if (rendering_style->hasSpecularHighlight()) {
			IfcSchema::IfcSpecularHighlightSelect* highlight = rendering_style->SpecularHighlight();
			if (highlight->declaration().is(IfcSchema::IfcSpecularRoughness::Class())) {
				double roughness = *((IfcSchema::IfcSpecularRoughness*)highlight);
				if (roughness >= 1e-9) {
					surface_style.Specularity().reset(1.0 / roughness);
				}
			} else if (highlight->declaration().is(IfcSchema::IfcSpecularExponent::Class())) {
				surface_style.Specularity().reset(*((IfcSchema::IfcSpecularExponent*)highlight));
			}
		}
		if (rendering_style->hasTransmissionColour()) {
			// Not supported
		}
		if (rendering_style->hasTransparency()) {
			const double d = rendering_style->Transparency();
			surface_style.Transparency().reset(d);
		}
	}
	return &(style_cache[surface_style_id] = surface_style);
}


template <typename P, typename PP>
IfcGeom::NativeElement<P, PP>* IfcGeom::AbstractKernel::create_brep_for_representation_and_product(
	const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product) {
	std::stringstream representation_id_builder;

	representation_id_builder << representation->data().id();

	IfcGeom::Representation::BRep* shape;
	IfcGeom::ConversionResults shapes;

	if (!convert_shapes(representation, shapes)) {
		return 0;
	}

	if (settings.get(IteratorSettings::APPLY_LAYERSETS)) {
		if (apply_layerset(product, shapes)) {

			IfcSchema::IfcRelAssociates::list::ptr associations = product->HasAssociations();
			for (IfcSchema::IfcRelAssociates::list::it it = associations->begin(); it != associations->end(); ++it) {
				IfcSchema::IfcRelAssociatesMaterial* associates_material = (**it).as<IfcSchema::IfcRelAssociatesMaterial>();
				if (associates_material) {
					unsigned layerset_id = associates_material->RelatingMaterial()->data().id();
					representation_id_builder << "-layerset-" << layerset_id;
					break;
				}
			}

		}
	}

	bool material_style_applied = false;

	const IfcSchema::IfcMaterial* single_material = get_single_material_association(product);
	if (single_material) {
		const IfcGeom::SurfaceStyle* s = get_style(single_material);
		for (IfcGeom::ConversionResults::iterator it = shapes.begin(); it != shapes.end(); ++it) {
			if (!it->hasStyle() && s) {
				it->setStyle(s);
				material_style_applied = true;
			}
		}
	} else {
		bool some_items_without_style = false;
		for (IfcGeom::ConversionResults::iterator it = shapes.begin(); it != shapes.end(); ++it) {
			if (!it->hasStyle()) {
				some_items_without_style = true;
				break;
			}
		}
		if (some_items_without_style) {
			Logger::Warning("No material and surface styles for:", product);
		}
	}

	if (material_style_applied) {
		representation_id_builder << "-material-" << single_material->data().id();
	}

	int parent_id = -1;
	try {
		IfcUtil::IfcBaseEntity* parent_object = get_decomposing_entity(product);
		if (parent_object && parent_object->as<IfcSchema::IfcObjectDefinition>()) {
			parent_id = parent_object->data().id();
		}
	} catch (const std::exception& e) {
		Logger::Error(e);
	}

	const std::string name = product->hasName() ? product->Name() : "";
	const std::string guid = product->GlobalId();

	ConversionResultPlacement* trsf = nullptr;
	try {
		convert_placement(product->ObjectPlacement(), trsf);
	} catch (const std::exception& e) {
		Logger::Error(e);
	} catch (...) {
		Logger::Error("Failed to construct placement");
	}

	// Does the IfcElement have any IfcOpenings?
	// Note that openings for IfcOpeningElements are not processed
	IfcSchema::IfcRelVoidsElement::list::ptr openings = find_openings(product)->as<IfcSchema::IfcRelVoidsElement>();

	const std::string product_type = product->declaration().name();
	ElementSettings element_settings(settings, getValue(GV_LENGTH_UNIT), product_type);

	if (!settings.get(IfcGeom::IteratorSettings::DISABLE_OPENING_SUBTRACTIONS) && openings && openings->size()) {
		representation_id_builder << "-openings";
		for (IfcSchema::IfcRelVoidsElement::list::it it = openings->begin(); it != openings->end(); ++it) {
			representation_id_builder << "-" << (*it)->data().id();
		}

		IfcGeom::ConversionResults opened_shapes;
		bool caught_error = false;
		try {
			convert_openings(product, openings, shapes, trsf, opened_shapes);
		} catch (const std::exception& e) {
			Logger::Message(Logger::LOG_ERROR, std::string("Error processing openings for: ") + e.what() + ":", product);
			caught_error = true;
		} catch (...) {
			Logger::Message(Logger::LOG_ERROR, "Error processing openings for:", product);
		}

		if (caught_error && opened_shapes.size() < shapes.size()) {
			opened_shapes = shapes;
		}

		if (settings.get(IteratorSettings::USE_WORLD_COORDS)) {
			for (IfcGeom::ConversionResults::iterator it = opened_shapes.begin(); it != opened_shapes.end(); ++it) {
				it->prepend(trsf);
			}
			trsf = nullptr;
			representation_id_builder << "-world-coords";
		}
		shape = new IfcGeom::Representation::BRep(element_settings, representation_id_builder.str(), opened_shapes);
	} else if (settings.get(IteratorSettings::USE_WORLD_COORDS)) {
		for (IfcGeom::ConversionResults::iterator it = shapes.begin(); it != shapes.end(); ++it) {
			it->prepend(trsf);
		}
		trsf = nullptr;
		representation_id_builder << "-world-coords";
		shape = new IfcGeom::Representation::BRep(element_settings, representation_id_builder.str(), shapes);
	} else {
		shape = new IfcGeom::Representation::BRep(element_settings, representation_id_builder.str(), shapes);
	}

	std::string context_string = "";
	if (representation->hasRepresentationIdentifier()) {
		context_string = representation->RepresentationIdentifier();
	} else if (representation->ContextOfItems()->hasContextType()) {
		context_string = representation->ContextOfItems()->ContextType();
	}

	auto elem = new NativeElement<P, PP>(
		product->data().id(),
		parent_id,
		name,
		product_type,
		guid,
		context_string,
		trsf,
		boost::shared_ptr<IfcGeom::Representation::BRep>(shape),
		product
	);

	if (settings.get(IteratorSettings::VALIDATE_QUANTITIES)) {
		validate_quantities(product, elem->geometry());
	}

	return elem;
}

template <typename P, typename PP>
IfcGeom::NativeElement<P, PP>* IfcGeom::AbstractKernel::create_brep_for_processed_representation(
	const IteratorSettings& /*settings*/, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product,
	IfcGeom::NativeElement<P, PP>* brep) {
	int parent_id = -1;
	try {
		IfcUtil::IfcBaseEntity* parent_object = get_decomposing_entity(product);
		if (parent_object && parent_object->as<IfcSchema::IfcObjectDefinition>()) {
			parent_id = parent_object->data().id();
		}
	} catch (const std::exception& e) {
		Logger::Error(e);
	}

	const std::string name = product->hasName() ? product->Name() : "";
	const std::string guid = product->GlobalId();

	ConversionResultPlacement* trsf = nullptr;
	try {
		convert_placement(product->ObjectPlacement(), trsf);
	} catch (const std::exception& e) {
		Logger::Error(e);
	} catch (...) {
		Logger::Error("Failed to construct placement");
	}

	std::string context_string = "";
	if (representation->hasRepresentationIdentifier()) {
		context_string = representation->RepresentationIdentifier();
	} else if (representation->ContextOfItems()->hasContextType()) {
		context_string = representation->ContextOfItems()->ContextType();
	}

	const std::string product_type = product->declaration().name();

	return new NativeElement<P, PP>(
		product->data().id(),
		parent_id,
		name,
		product_type,
		guid,
		context_string,
		trsf,
		brep->geometry_pointer(),
		product
		);
}

template IFC_GEOM_API IfcGeom::NativeElement<float, float>* IfcGeom::AbstractKernel::create_brep_for_representation_and_product<float, float>(
	const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product);
template IFC_GEOM_API IfcGeom::NativeElement<float, double>* IfcGeom::AbstractKernel::create_brep_for_representation_and_product<float, double>(
	const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product);
template IFC_GEOM_API IfcGeom::NativeElement<double, double>* IfcGeom::AbstractKernel::create_brep_for_representation_and_product<double, double>(
	const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product);

template IFC_GEOM_API IfcGeom::NativeElement<float, float>* IfcGeom::AbstractKernel::create_brep_for_processed_representation<float, float>(
	const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product, IfcGeom::NativeElement<float, float>* brep);
template IFC_GEOM_API IfcGeom::NativeElement<float, double>* IfcGeom::AbstractKernel::create_brep_for_processed_representation<float, double>(
	const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product, IfcGeom::NativeElement<float, double>* brep);
template IFC_GEOM_API IfcGeom::NativeElement<double, double>* IfcGeom::AbstractKernel::create_brep_for_processed_representation<double, double>(
	const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product, IfcGeom::NativeElement<double, double>* brep);