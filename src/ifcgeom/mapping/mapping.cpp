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
        abstract_mapping* operator()(IfcParse::IfcFile* file, Settings& settings) const {
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

std::vector<IfcSchema::IfcProduct> mapping::products_represented_by(const IfcSchema::IfcRepresentation& representation, IfcSchema::IfcRepresentationMap& rmap, bool only_direct) {
    std::vector<IfcSchema::IfcProduct> products;

    std::vector<IfcSchema::IfcProductRepresentation> prodreps = representation.OfProductRepresentation();
    for (auto& prodrep : prodreps) {
        // http://buildingsmart-tech.org/ifc/IFC2x3/TC1/html/ifcrepresentationresource/lexical/ifcproductrepresentation.htm
        // IFC2x Edition 3 NOTE  Users should not instantiate the entity IfcProductRepresentation from IFC2x Edition 3 onwards.
        // It will be changed into an ABSTRACT supertype in future releases of IFC.

        // IfcProductRepresentation also lacks the INVERSE relation to IfcProduct
        // Let's find the IfcProducts that reference the IfcProductRepresentation anyway
        auto invs = prodrep.data()->file()->getInverse(prodrep.id(), &IfcSchema::IfcProduct::Class(), -1);
        for (auto& inv : invs) {
            products.push_back(inv.as<IfcSchema::IfcProduct>());
        }        
    }

    if (only_direct) {
        return products;
    }

    std::vector<IfcSchema::IfcRepresentationMap> maps = representation.RepresentationMap();
    if (maps.size() == 1) {
        rmap = maps.front();
        if (not_reusable_maps_.find(rmap) != not_reusable_maps_.end()) {
            return products;
        }
        taxonomy::matrix4::ptr origin = taxonomy::cast<taxonomy::matrix4>(map(rmap.MappingOrigin()));
        if (origin->is_identity()) {
            std::vector<IfcSchema::IfcMappedItem> items = rmap.MapUsage();
            for (auto& item : items) {
                if (item.StyledByItem().size() != 0) continue;

                taxonomy::matrix4::ptr target;
                try {
                    target = taxonomy::cast<taxonomy::matrix4>(map(item.MappingTarget()));
                } catch (const std::exception& e) {
                    Logger::Error(e);
                    continue;
                }
                if (!target->is_identity()) {
                    continue;
                }

                auto reps = item.data()->file()->getInverse(item.id(), (&IfcSchema::IfcRepresentation::Class()), -1);
                for (auto& rep : reps) {
                    if (rep.as<IfcSchema::IfcRepresentation>().Items().size() != 1) continue;
                    std::vector<IfcSchema::IfcProductRepresentation> prodreps_mapped = rep.as<IfcSchema::IfcRepresentation>().OfProductRepresentation();
                    for (auto& prm : prodreps_mapped) {
                        auto ps = prm.data()->file()->getInverse(prm.id(), (&IfcSchema::IfcProduct::Class()), -1);
                        for (auto& p : ps) {
                            products.push_back(p.as<IfcSchema::IfcProduct>());
                        }
                    }
                }
            }
        }
    }

    return products;
}

namespace {
std::vector<IfcSchema::IfcProduct> filter_products(const std::vector<IfcSchema::IfcProduct>& unfiltered_products, const std::vector<filter_t>& filters) {
    std::vector<IfcSchema::IfcProduct> ifcproducts;
    for (auto& prod : unfiltered_products) {
        if (boost::all(filters, [prod](const filter_t& f) { return f(prod); })) {
            ifcproducts.push_back(prod);
        }
    }
    return ifcproducts;
}
}

bool mapping::reuse_ok_(const std::vector<IfcSchema::IfcProduct>& products) {
    // With world coords enabled, object transformations are directly applied to
    // the BRep. There is no way to re-use the geometry for multiple products.
    if (settings_.get<settings::UseWorldCoords>().get()) {
        return false;
    }

    if (products.size() == 1) {
        return true;
    }

    std::set<express::Base> associated_single_materials;

    for (auto& product : products) {
        if (!settings_.get<settings::DisableOpeningSubtractions>().get() && !find_openings(product).empty()) {
            return false;
        }

        if (settings_.get<settings::ApplyLayerSets>().get()) {
            std::vector<IfcSchema::IfcRelAssociates> associations = product.HasAssociations();
            for (auto& assoc : associations) {
                if (auto assocm = assoc.as<IfcSchema::IfcRelAssociatesMaterial>()) {
                    if (assocm.RelatingMaterial().declaration().is(IfcSchema::IfcMaterialLayerSetUsage::Class())) {
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

std::vector<express::Base> mapping::find_openings(const express::Base& inst) {
    std::vector<express::Base> openings;
    
    if (auto rep = inst.as<IfcSchema::IfcRepresentation>()) {
        // @todo this is essentially only for hybrid kernel trying to guess
        // when not to use a simple kernel.
        IfcSchema::IfcRepresentationMap rmap;
        auto prods = products_represented_by(rep, rmap, true);
        for (auto& p : prods) {
            auto ops = find_openings(p);
            openings.insert(openings.end(), ops.begin(), ops.end());
        }
        return openings;
    }

    if (inst.as<IfcSchema::IfcElement>() && !inst.as<IfcSchema::IfcFeatureElementSubtraction>()) {
        auto element = inst.as<IfcSchema::IfcElement>();
        auto rels = element.HasOpenings();
        for (auto& rel : rels) {
            openings.push_back(rel.RelatedOpeningElement());
        }
    }

    // Is the IfcElement a decomposition of an IfcElement with any IfcOpeningElements?
    auto obdef = inst.as<IfcSchema::IfcObjectDefinition>();
    if (obdef) {
        for (;;) {
            auto decomposes = obdef.Decomposes();
            if (decomposes.size() != 1) {
                // If we have multiple decompositions, not allowed by schema,
                // openings associated to relating decompositions are not
                // considered;
                break;
            }
            if (!decomposes.front().as<IfcSchema::IfcRelAggregates>()) {
                // Only aggregation, not nesting is considered.
                break;
            }
            auto rel_obdef = decomposes.front().as<IfcSchema::IfcRelAggregates>().RelatingObject();
            if (rel_obdef.as<IfcSchema::IfcElement>() && !rel_obdef.as<IfcSchema::IfcFeatureElementSubtraction>()) {
                auto element = rel_obdef.as<IfcSchema::IfcElement>();
                auto rels = element.HasOpenings();
                for (auto& rel : rels) {
                    openings.push_back(rel.RelatedOpeningElement());
                }
            }

            obdef = rel_obdef;
        }
    }

    return openings;
}


void mapping::get_representations(std::vector<geometry_conversion_task>& tasks, std::vector<filter_t>& filters) {
    std::vector<IfcSchema::IfcRepresentation> representations;

    if (!settings_.get<settings::ContextIds>().has()) {
        addRepresentationsFromDefaultContexts(representations);
    } else {
        addRepresentationsFromContextIds(representations);
    }

    std::vector<IfcSchema::IfcRepresentation> ok_mapped_representations;

    int task_index = 0;
    
    for (auto representation : representations) {
        IfcSchema::IfcRepresentationMap rmap;
        std::vector<IfcSchema::IfcProduct> ifcproducts = filter_products(products_represented_by(representation, rmap, false), filters);
        
        if (ifcproducts.empty()) {
            continue;
        }

        auto geometry_reuse_ok_for_current_representation_ = reuse_ok_(ifcproducts);
        if (!geometry_reuse_ok_for_current_representation_ && rmap) {
            not_reusable_maps_.insert(rmap);
        }

        std::vector<IfcSchema::IfcRepresentationMap> maps = representation.RepresentationMap();

        if (!geometry_reuse_ok_for_current_representation_ && maps.size() == 1) {
            // unfiltered_products contains products represented by this representation by means of mapped items.
            // For example because of openings applied to products, reuse might not be acceptable and then the
            // products will be processed by means of their immediate representation and not the mapped representation.

            // IfcRepresentationMaps are also used for IfcTypeProducts, so an additional check is performed whether the map
            // is indeed used by IfcMappedItems.
            auto& map = maps.front();
            if (map.MapUsage().size() > 0) {
                continue;
            }
        }

        // Check if this representation has (or will be) processed as part its mapped representation
        bool representation_processed_as_mapped_item = false;
        auto representation_mapped_to_result = representation_mapped_to(representation);
        if (representation_mapped_to_result) {
            representation_processed_as_mapped_item = geometry_reuse_ok_for_current_representation_ && (
                std::find(ok_mapped_representations.begin(), ok_mapped_representations.end(), representation_mapped_to_result) != ok_mapped_representations.end() ||
                reuse_ok_(products_represented_by(representation_mapped_to_result, rmap)));
        }

        if (representation_processed_as_mapped_item) {
            ok_mapped_representations.push_back(representation_mapped_to_result);
            continue;
        }

        if (!geometry_reuse_ok_for_current_representation_ && ifcproducts.size() > 1) {
            // reuse_ok is taken into account in products_represented_by(), but not when
            // the same IfcRepresentation is directly assigned to multiple products.
            for (auto& p : ifcproducts) {
                geometry_conversion_task task;
                task.index = task_index++;
                task.representation = representation;
                task.products.push_back(p);
                tasks.emplace_back(task);
            }
        } else {
            geometry_conversion_task task;
            task.index = task_index++;
            task.representation = representation;
            task.products.insert(task.products.end(), ifcproducts.begin(), ifcproducts.end());
            tasks.emplace_back(task);
        }
    }
}

const express::Base mapping::get_product_type(const express::Base& product_) {
    auto product = product_.as<IfcSchema::IfcProduct>();
#ifdef SCHEMA_IfcObject_HAS_IsTypedBy
    auto rels = product.IsTypedBy();
#else // IFC2X3.
    auto rels = product.IsDefinedBy();
#endif
    for (auto it = rels.begin(); it != rels.end(); ++it) {
#ifdef SCHEMA_IfcObject_HAS_IsTypedBy
        auto rel = *it;
#else // IFC2X3.
        auto rel = (*it).as<IfcSchema::IfcRelDefinesByType>();
        if (!rel) {
            continue;
        }
#endif
        // Avoid segfault if RelatingType is unset.
        if (rel.get("RelatingType").isNull()){
            break;
        }
        return rel.RelatingType();
    }
    return express::Base{};
}

const express::Base mapping::get_single_material_association(const express::Base& product_) {
    auto product = product_.as<IfcSchema::IfcObjectDefinition>();
    IfcSchema::IfcMaterial single_material;
    auto associations = product.HasAssociations();
    std::vector<IfcSchema::IfcRelAssociatesMaterial> associated_materials;
    for (auto& assoc : associations) {
        if (auto assocm = assoc.as<IfcSchema::IfcRelAssociatesMaterial>()) {
            associated_materials.push_back(assocm);
        }
    }
    if (associated_materials.size() == 1) {
        express::Base associated_material;

        try {
            associated_material = associated_materials.front().RelatingMaterial().concrete();
        } catch(IfcParse::IfcException& e) {
            Logger::Error(e.what());
        }

        if (associated_material) {
            single_material = associated_material.as<IfcSchema::IfcMaterial>();

            // NB: Single-layer layersets are also considered, regardless of --enable-layerset-slicing, this
            // in accordance with other viewers.
            if (!single_material) {
                if (associated_material.as<IfcSchema::IfcMaterialLayerSetUsage>() || associated_material.as<IfcSchema::IfcMaterialLayerSet>()) {
                    IfcSchema::IfcMaterialLayerSet layerset;
                    if (auto m = associated_material.as<IfcSchema::IfcMaterialLayerSetUsage>()) {
                        if (m.get("ForLayerSet").isNull()) {
                            Logger::Warning("Missing ForLayerSet for:", m);
                            return express::Base{};
                        }
                        layerset = m.ForLayerSet();
                    } else {
                        layerset = associated_material.as<IfcSchema::IfcMaterialLayerSet>();
                    }
                    if (settings_.get<settings::LayersetFirst>().value ? layerset.MaterialLayers().size() >= 1 : layerset.MaterialLayers().size() == 1) {
                        IfcSchema::IfcMaterialLayer layer = layerset.MaterialLayers().front();
                        if (auto m_ = layer.Material()) {
                            single_material = m_;
                        }
                    }
                }

#ifdef SCHEMA_HAS_IfcMaterialProfileSet
                if (associated_material.as<IfcSchema::IfcMaterialProfileSetUsage>() || associated_material.as<IfcSchema::IfcMaterialProfileSet>()) {
                    IfcSchema::IfcMaterialProfileSet profileset;
                    if (auto m = associated_material.as<IfcSchema::IfcMaterialProfileSetUsage>()) {
                        if (m.get("ForProfileSet").isNull()) {
                            Logger::Warning("Missing ForProfileSet for:", m);
                            return express::Base{};
                        }
                        profileset = m.ForProfileSet();
                    } else {
                        profileset = associated_material.as<IfcSchema::IfcMaterialProfileSet>();
                    }
                    if (settings_.get<settings::LayersetFirst>().value ? profileset.MaterialProfiles().size() >= 1 : profileset.MaterialProfiles().size() == 1) {
                        IfcSchema::IfcMaterialProfile profile = profileset.MaterialProfiles().front();
                        if (auto m_ = profile.Material()) {
                            single_material = m_;
                        }
                    }
                }
#endif

#ifdef SCHEMA_HAS_IfcMaterialConstituentSet
                if (associated_material.as<IfcSchema::IfcMaterialConstituentSet>() && associated_material.as<IfcSchema::IfcMaterialConstituentSet>().MaterialConstituents()) {
                    IfcSchema::IfcMaterialConstituentSet constituentset = associated_material.as<IfcSchema::IfcMaterialConstituentSet>();
                    if (settings_.get<settings::LayersetFirst>().value ? constituentset.MaterialConstituents().value().size() >= 1 : constituentset.MaterialConstituents().value().size() == 1) {
                        IfcSchema::IfcMaterialConstituent constituent = constituentset.MaterialConstituents().value().front();
                        if (auto m_ = constituent.Material()) {
                            single_material = m_;
                        }
                    }
                }
#endif
            }
        }
    }
    return single_material;
}

IfcSchema::IfcRepresentation mapping::representation_mapped_to(const IfcSchema::IfcRepresentation& representation) {
    IfcSchema::IfcRepresentation representation_mapped_to;
    std::vector<IfcSchema::IfcRepresentationItem> items = representation.Items();
    if (items.size() == 1) {
        IfcSchema::IfcRepresentationItem& item = items.front();
        if (item.declaration().is(IfcSchema::IfcMappedItem::Class())) {
            if (item.StyledByItem().size() == 0) {
                IfcSchema::IfcMappedItem mapped_item = item.as<IfcSchema::IfcMappedItem>();
                taxonomy::matrix4::ptr target;
                try {
                    target = taxonomy::cast<taxonomy::matrix4>(map(mapped_item.MappingTarget()));
                } catch (const std::exception& e) {
                    Logger::Error(e);
                }
                if (target && target->is_identity()) {
                    IfcSchema::IfcRepresentationMap rmap = mapped_item.MappingSource();
                    taxonomy::matrix4::ptr origin = taxonomy::cast<taxonomy::matrix4>(map(rmap.MappingOrigin()));
                    if (origin->is_identity()) {
                        representation_mapped_to = rmap.MappedRepresentation();
                    }
                }
            }
        }
    }
    return representation_mapped_to;
}

namespace {
    const IfcSchema::IfcRepresentationItem find_item_carrying_style(IfcSchema::IfcRepresentationItem item) {
        if (!item.StyledByItem().empty()) {
            return item;
        }

        while (auto booleanresult = item.as<IfcSchema::IfcBooleanClippingResult>()) {
            // All instantiations of IfcBooleanOperand (type of FirstOperand) are subtypes of
            // IfcGeometricRepresentationItem
            // @nb this is not really how the select hierarchy is structured, not all representation items are selected here
            item = booleanresult.FirstOperand().concrete().as<IfcSchema::IfcRepresentationItem>();
            if (!item.StyledByItem().empty()) {
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
    std::pair<IfcSchema::IfcSurfaceStyle, T> get_surface_style(const IfcSchema::IfcStyledItem& si) {
        std::vector<IfcSchema::IfcPresentationStyle> prs_styles;

#ifdef SCHEMA_HAS_IfcStyleAssignmentSelect
        auto style_assignments = si.Styles();
        for (auto kt = style_assignments.begin(); kt != style_assignments.end(); ++kt) {
            // Using IfcPresentationStyleAssignment is deprecated, use the direct assignment of a subtype of IfcPresentationStyle instead.
            auto style_k = (*kt).as<IfcSchema::IfcPresentationStyle>();
            if (style_k) {
                prs_styles.push_back(style_k);
                continue;
            }

            auto style_assignment = (*kt).as<IfcSchema::IfcPresentationStyleAssignment>();
            if (!style_assignment) {
                continue;
            }

            // Only in case of 2x3 or old style IfcPresentationStyleAssignment
            auto styles = style_assignment.Styles();
#elif defined(SCHEMA_HAS_IfcPresentationStyleAssignment)
        std::vector<IfcSchema::IfcPresentationStyleAssignment> style_assignments = si.Styles();
        for (auto& style_assignment : style_assignments) {
            // Only in case of 2x3 or old style IfcPresentationStyleAssignment
            auto styles = style_assignment.Styles();
#else
            auto styles = si.Styles();
#endif
            for (auto lt = styles.begin(); lt != styles.end(); ++lt) {
                auto style_l = (*lt).as<IfcSchema::IfcPresentationStyle>();
                if (style_l) {
                    prs_styles.push_back(style_l);
                }
            }
#if defined(SCHEMA_HAS_IfcStyleAssignmentSelect) || defined(SCHEMA_HAS_IfcPresentationStyleAssignment)
        }
#endif

        IfcSchema::IfcSurfaceStyle surface_style_;
        for (auto& style : prs_styles) {
            if (auto surface_style = style.as<IfcSchema::IfcSurfaceStyle>()) {
                if (surface_style.Side() != IfcSchema::IfcSurfaceSide::IfcSurfaceSide_NEGATIVE) {
                    surface_style_ = surface_style;
                    auto styles_elements = surface_style.Styles();
                    for (auto mt = styles_elements.begin(); mt != styles_elements.end(); ++mt) {
                        if (auto mtt = (*mt).template as<T>()) {
                            return std::make_pair(surface_style, mtt);
                        }
                    }
                }
            }
        }
        return std::make_pair(surface_style_, T{});
    }

    bool process_colour(const IfcSchema::IfcColourRgb& colour, std::array<double, 3>& rgb) {
        if (colour) {
            rgb[0] = colour.Red();
            rgb[1] = colour.Green();
            rgb[2] = colour.Blue();
        }
        return colour;
    }

    bool process_colour(const IfcSchema::IfcNormalisedRatioMeasure& factor, std::array<double, 3>& rgb) {
        if (factor) {
            const double f = factor;
            rgb[0] = rgb[1] = rgb[2] = f;
        }
        return factor;
    }

    bool process_colour(const IfcSchema::IfcColourOrFactor& colour_or_factor, std::array<double, 3>& rgb) {
        if (!colour_or_factor) {
            return false;
        } else if (auto crgb = colour_or_factor.as<IfcSchema::IfcColourRgb>()) {
            return process_colour(crgb, rgb);
        } else if (auto ratio = colour_or_factor.as<IfcSchema::IfcNormalisedRatioMeasure>()) {
            return process_colour(ratio, rgb);
        } else {
            return false;
        }
    }
}

IfcSchema::IfcStyledItem mapping::find_style(const IfcSchema::IfcRepresentationItem& representation_item_) {
    // For certain representation items, most notably boolean operands,
    // a style definition might reside on one of its operands.
    auto representation_item = representation_item_;
    representation_item = find_item_carrying_style(representation_item);

    if (auto st = representation_item.as<IfcSchema::IfcStyledItem>()) {
        return st;
    }

    auto styled_items = representation_item.StyledByItem();
    if (styled_items.size()) {
        // StyledByItem is a SET [0:1] OF IfcStyledItem, so we return after the first IfcStyledItem:
        return styled_items.front();
    }

    return IfcSchema::IfcStyledItem{};
}

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcMaterial& material) {
    std::vector<IfcSchema::IfcMaterialDefinitionRepresentation> defs = material.HasRepresentation();
    for (auto jt = defs.begin(); jt != defs.end(); ++jt) {
        std::vector<IfcSchema::IfcRepresentation> reps = (*jt).Representations();
        std::vector<IfcSchema::IfcStyledItem> styles;
        for (auto it = reps.begin(); it != reps.end(); ++it) {
            auto itms = it->Items();
            for (auto& itm : itms) {
                if (auto si = itm.as<IfcSchema::IfcStyledItem>()) {
                    styles.push_back(si);
                }
            }
        }
        if (styles.size() == 1) {
            IfcSchema::IfcStyledItem& styled_item = styles.front();
            auto mapped_item = map(styled_item);
            if (mapped_item) {
                return mapped_item;
            }
            // Check if it's failed or just some unsupported case.
            if (failed_on_purpose_.find(styled_item) == failed_on_purpose_.end()) {
                return nullptr;
            }
            Logger::Warning("Skipping unsupported material style for material: ", material);
        }
    }

    // When material does not have a representation we don't create a style from it
    return nullptr;

    /*
    taxonomy::style::ptr material_style = taxonomy::make<taxonomy::style>();
    material_style->instance = material;
    if (settings_.get<settings::UseMaterialNames>().get()) {
        material_style->name = material->Name();
    } else {
        std::ostringstream oss;
        oss << material->declaration().name() << "-" << material->id();
        material_style->name = oss.str();
    }
    return material_style;
    */

    // @todo
    // IfcGeom::SurfaceStyle material_style = IfcGeom::SurfaceStyle(material->data().id(), material->Name());
    // return &(style_cache[material->data().id()] = material_style);
}

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcStyledItem& inst) {
    auto style_pair = get_surface_style<IfcSchema::IfcSurfaceStyleShading>(inst);

    auto [style, shading] = style_pair;

    if (!style) {
        // E.g. IfcCurveStyle is skipped as unsupported.
        Logger::Warning("Only IfcSurfaceStyle is supported, couldn't find it in IfcStyledItem: ", inst);
        failed_on_purpose_.insert(inst);
        return nullptr;
    }

    // map and not map_impl otherwise no caching
    return map(style);
}

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcSurfaceStyle& style) {
    auto styles = style.Styles();
    IfcSchema::IfcSurfaceStyleShading shading;
    for (auto& s : styles) {
        if (shading = s.as<IfcSchema::IfcSurfaceStyleShading>()) {
            break;
        }
    }
    taxonomy::style::ptr surface_style = taxonomy::make<taxonomy::style>();
    surface_style->instance = style;
    if (settings_.get<settings::UseMaterialNames>().get() && style.Name()) {
        surface_style->name = *style.Name();
    } else {
        std::ostringstream oss;
        if (shading) {
            oss << shading.declaration().name() << "-" << shading.id();
        } else {
            oss << "-";
        }
        surface_style->name = oss.str();
    }

    if (!shading) {
        // E.g. IfcSurface style has only IfcExternallyDefinedSurfaceStyle.
        return surface_style;
    }

	surface_style->use_surface_color = settings_.get<settings::SurfaceColour>().get();

	static taxonomy::colour white = taxonomy::colour(1., 1., 1.);
	std::array<double, 3> rgb;
	if (process_colour(shading.SurfaceColour(), rgb)) {
		surface_style->surface.components() << rgb[0], rgb[1], rgb[2];
        surface_style->diffuse = surface_style->surface;
	}

    if (auto rendering_style = shading.as<IfcSchema::IfcSurfaceStyleRendering>()) {
        if (rendering_style.DiffuseColour() && process_colour(rendering_style.DiffuseColour(), rgb)) {
            const taxonomy::colour& old_diffuse = surface_style->diffuse ? surface_style->diffuse : white;
            surface_style->diffuse = taxonomy::colour(old_diffuse.r() * rgb[0], old_diffuse.g() * rgb[1], old_diffuse.b() * rgb[2]);
        }
        if (rendering_style.DiffuseTransmissionColour()) {
            // Not supported
        }
        if (rendering_style.ReflectionColour()) {
            // Not supported
        }
        if (rendering_style.SpecularColour() && process_colour(rendering_style.SpecularColour(), rgb)) {
            surface_style->specular = taxonomy::colour(rgb[0], rgb[1], rgb[2]);
        }
        if (rendering_style.SpecularHighlight()) {
            IfcSchema::IfcSpecularHighlightSelect highlight = rendering_style.SpecularHighlight();
            if (auto roughness_ = highlight.as<IfcSchema::IfcSpecularRoughness>()) {
                double roughness = roughness_;
                if (roughness >= 1e-9) {
                    surface_style->specularity = (1.0 / roughness);
                }
            } else if (auto exponent = highlight.as<IfcSchema::IfcSpecularExponent>()) {
                surface_style->specularity = exponent;
            }
        }
        if (rendering_style.TransmissionColour()) {
            // Not supported
        }
#ifndef SCHEMA_IfcSurfaceStyleShading_HAS_Transparency
        // ifc2x3
        if (rendering_style.Transparency()) {
            const double d = *rendering_style.Transparency();
            surface_style->transparency = d;
        }
#endif
    }

#ifdef SCHEMA_IfcSurfaceStyleShading_HAS_Transparency
    // ifc4 and onwards
    if (shading.Transparency()) {
        const double d = *shading.Transparency();
        surface_style->transparency = d;
    }
#endif

    return surface_style;
}

taxonomy::ptr mapping::map(const express::Base& inst) {
    auto iden = inst.identity();
    if (use_caching_) {
        std::lock_guard<std::mutex> guard(cache_guard_);
        auto it = cache_.find(iden);
        if (it != cache_.end()) {
            return it->second;
        }
    }
    taxonomy::ptr item = nullptr;

    // @todo we should check whether there is a notice performance impact on the large sequence
    // of if-statements and whether a switch on e.g inst.declaration()->index_in_schema()
    // isn't more efficient (which would disable inheritance though).

    bool matched = false;

#include "bind_convert_impl.i"

    if (item) {
        if (use_caching_) {
            std::lock_guard<std::mutex> guard(cache_guard_);
            cache_.insert({iden, item});
        }
    } else if (!matched) {
        Logger::Message(Logger::LOG_ERROR, "No operation defined for:", inst);
    }
    return item;
}

namespace {
    express::Base get_RelatingObject(IfcSchema::IfcRelDecomposes& decompose) {
#ifdef SCHEMA_IfcRelDecomposes_HAS_RelatingObject
        return decompose.RelatingObject();
#else
        IfcSchema::IfcRelAggregates aggr = decompose.as<IfcSchema::IfcRelAggregates>();
        if (aggr) {
            return aggr.RelatingObject();
        }
        return express::Base{};
#endif
    }
}

express::Base mapping::get_decomposing_entity(const express::Base& inst, bool include_openings) {
    IfcSchema::IfcObjectDefinition parent;

    auto product = inst.as<IfcSchema::IfcProduct>();
    if (!product) {
        return parent;
    }

    /* In case of an opening element, parent to the RelatingBuildingElement */
    if (include_openings && product.declaration().is(IfcSchema::IfcOpeningElement::Class())) {
        IfcSchema::IfcOpeningElement opening = product.as<IfcSchema::IfcOpeningElement>();
        std::vector<IfcSchema::IfcRelVoidsElement> voids = opening.VoidsElements();
        if (voids.size()) {
            IfcSchema::IfcRelVoidsElement& ifc_void = voids.front();
            parent = ifc_void.RelatingBuildingElement();
        }
    } else if (product.declaration().is(IfcSchema::IfcElement::Class())) {
        IfcSchema::IfcElement element = product.as<IfcSchema::IfcElement>();
        std::vector<IfcSchema::IfcRelFillsElement> fills = element.FillsVoids();
        /* In case of a RelatedBuildingElement parent to the opening element */
        if (fills.size() && include_openings) {
            for (auto& fill : fills) {
                IfcSchema::IfcObjectDefinition ifc_objectdef = fill.RelatingOpeningElement();
                if (product == ifc_objectdef) continue;
                parent = ifc_objectdef;
            }
        }
        /* Else simply parent to the containing structure */
        if (!parent) {
            std::vector<IfcSchema::IfcRelContainedInSpatialStructure> parents = element.ContainedInStructure();
            if (parents.size()) {
                IfcSchema::IfcRelContainedInSpatialStructure& container = parents.front();
                parent = container.RelatingStructure();
            }
        }
    }

    /* Parent decompositions to the RelatingObject */
    if (!parent) {
        std::vector<express::Entity> parents = product.data()->file()->getInverse(product.id(), (&IfcSchema::IfcRelAggregates::Class()), -1);
        auto nests = product.data()->file()->getInverse(product.id(), (&IfcSchema::IfcRelNests::Class()), -1);
        parents.insert(parents.end(), nests.begin(), nests.end());
        for (auto it = parents.begin(); it != parents.end(); ++it) {
            IfcSchema::IfcRelDecomposes decompose = (*it).as<IfcSchema::IfcRelDecomposes>();
            express::Base ifc_objectdef;
                                                                                                                
            ifc_objectdef = get_RelatingObject(decompose);

            if (!ifc_objectdef || product == ifc_objectdef) continue;
            parent = ifc_objectdef.as<IfcSchema::IfcObjectDefinition>();
        }
    }
    return parent;
}

std::map<std::string, express::Base> mapping::get_layers(const express::Base& inst) {
    auto prod = inst.as<IfcSchema::IfcProduct>();
    std::map<std::string, express::Base> layers;
    if (prod.Representation()) {
        std::vector<express::Base> representations = IfcParse::traverse(prod.Representation());
        for (auto& inst : representations) {
            if (auto repr = inst.as<IfcSchema::IfcRepresentation>()) {
                std::vector<IfcSchema::IfcPresentationLayerAssignment> a = repr.LayerAssignments();
                for (auto& b : a) {
                    layers[b.Name()] = b;
                }

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
    
#ifdef SCHEMA_HAS_IfcContext
    auto projects = file_->instances_by_type<IfcSchema::IfcContext>();
#else
    auto projects = file_->instances_by_type<IfcSchema::IfcProject>();
#endif
    IfcSchema::IfcUnitAssignment unit_assignment;
    if (projects.size() == 1) {
        auto& project = projects.front();
        unit_assignment = project.UnitsInContext();
    } else {
        Logger::Warning("Not a single project or context in file");
    }
    if (!unit_assignment) {
        Logger::Warning("Unable to detect unit information");
        return;
    }

    bool length_unit_encountered = false, angle_unit_encountered = false;

    try {
        auto units = unit_assignment.Units();
        if (units.empty()) {
            Logger::Warning("No unit information found");
        } else {
            for (auto& base : units) {
                if (auto named_unit = base.as<IfcSchema::IfcNamedUnit>()) {
                    if (named_unit.UnitType() == IfcSchema::IfcUnitEnum::IfcUnit_LENGTHUNIT ||
                        named_unit.UnitType() == IfcSchema::IfcUnitEnum::IfcUnit_PLANEANGLEUNIT) {
                        std::string current_unit_name;
                        const double current_unit_magnitude = IfcParse::get_SI_equivalent<IfcSchema>(named_unit);
                        if (current_unit_magnitude != 0.) {
                            if (auto u = named_unit.as<IfcSchema::IfcConversionBasedUnit>()) {
                                current_unit_name = u.Name();
                            } else if (auto si_unit = named_unit.as<IfcSchema::IfcSIUnit>()) {
                                if (si_unit.Prefix()) {
                                    current_unit_name = IfcSchema::IfcSIPrefix::ToString(*si_unit.Prefix());
                                }
                                current_unit_name += IfcSchema::IfcSIUnitName::ToString(si_unit.Name());
                            }
                            if (named_unit.UnitType() == IfcSchema::IfcUnitEnum::IfcUnit_LENGTHUNIT) {
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

    // @todo move to a more descriptive function
    if (settings_.get<settings::BuildingLocalPlacement>().get()) {
        placement_rel_to_type_ = file_->schema()->declaration_by_name("IfcBuilding");
    }
    if (settings_.get<settings::SiteLocalPlacement>().get()) {
        placement_rel_to_type_ = file_->schema()->declaration_by_name("IfcSite");
    }

    // Translation is applied first, then rotation.
    if (settings_.get<ModelOffset>().has()) {
        auto vs = settings_.get<ModelOffset>().get();
        if (vs.size() == 3) {
            offset_and_rotation_ *= Eigen::Affine3d(Eigen::Translation3d(vs[0], vs[1], vs[2])).matrix();
        } else {
            Logger::Error("Expected 3 values for model-offset setting");
        }
    }

    if (settings_.get<ModelRotation>().has()) {
        auto vs = settings_.get<ModelRotation>().get();
        if (vs.size() == 4) {
            // @nb W, X, Y, Z
            auto m3 = Eigen::Quaterniond(vs[3], vs[0], vs[1], vs[2]).normalized().matrix();
            Eigen::Matrix4d m4 = Eigen::Matrix4d::Identity();
            m4 << m3;
            offset_and_rotation_ *= m4;
        } else {
            Logger::Error("Expected 4 values for model-rotation setting");
        }
    }
}

void mapping::initialize_settings() {
    settings_.get<settings::LengthUnit>().value = length_unit_;
    settings_.get<settings::PlaneUnit>().value = angle_unit_;

    // Set precision from file
    double lowest_precision_encountered = std::numeric_limits<double>::infinity();
    bool any_precision_encountered = false;

    std::vector<IfcSchema::IfcGeometricRepresentationContext> contexts =
        file_->instances_by_type_excl_subtypes<IfcSchema::IfcGeometricRepresentationContext>();

    for (auto& context : contexts) {
        // See if there is a context_id filter and whether the context is selected
        if (settings_.get<settings::ContextIds>().has()) {
            auto cids = settings_.get<settings::ContextIds>().get();
            if (cids.find(context.id()) == cids.end()) {
                bool selected_sub_context = false;
                auto subs = context.HasSubContexts();
                for (auto& sub : subs) {
                    if (cids.find(context.id()) != cids.end()) {
                        selected_sub_context = true;
                        break;
                    }
                }
                if (!selected_sub_context) {
                    continue;
                }
            }
        }

        auto fp = settings_.get<settings::PrecisionFactor>().get();
        if (context.Precision() && (*context.Precision() * length_unit_ * fp) < lowest_precision_encountered) {
            // Some arbitrary factor that has proven to work better for the models in the set of test files.
            lowest_precision_encountered = *context.Precision() * length_unit_ * fp;
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

    settings_.get<Precision>().value = precision_to_set;
}

bool mapping::get_layerset_information(const express::Base& p, layerset_information& info, int &)
{
    auto product = p.as<IfcSchema::IfcProduct>();

    if (!product) {
        return false;
    }

    IfcSchema::IfcMaterialLayerSetUsage usage;
    // Handle_Geom_Surface reference_surface;

    std::vector<IfcSchema::IfcRelAssociates> associations = product.HasAssociations();
    for (auto it = associations.begin(); it != associations.end(); ++it) {
        IfcSchema::IfcRelAssociatesMaterial associates_material = (*it).as<IfcSchema::IfcRelAssociatesMaterial>();
        if (associates_material) {
            usage = associates_material.RelatingMaterial().as<IfcSchema::IfcMaterialLayerSetUsage>();
            break;
        }
    }

    if (!usage) {
        return false;
    }

    IfcSchema::IfcRepresentation body_representation = find_representation(product, "Body");

    if (!body_representation) {
        Logger::Warning("No body representation for product", product);
        return false;
    }

    const IfcSchema::IfcMaterialLayerSet layerset = usage.ForLayerSet();
    const bool positive = usage.DirectionSense() == IfcSchema::IfcDirectionSenseEnum::IfcDirectionSense_POSITIVE;
    double offset = usage.OffsetFromReferenceLine() * this->length_unit_;

    std::vector<IfcSchema::IfcMaterialLayer> material_layers = layerset.MaterialLayers();

    if (product.declaration().is(IfcSchema::IfcWall::Class())) {
        IfcSchema::IfcRepresentation axis_representation = find_representation(product, "Axis");

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

        for (auto it = material_layers.begin(); it != material_layers.end(); ++it) {
            info.styles.push_back(*taxonomy::cast<taxonomy::style>(map((*it).Material())));

            double thickness = (*it).LayerThickness() * this->length_unit_;

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
        auto resources = IfcParse::traverse(body_representation);
        std::vector<IfcSchema::IfcExtrudedAreaSolid> extrusions;
        for (auto& r : resources) {
            if (auto ex = r.as<IfcSchema::IfcExtrudedAreaSolid>()) {
                extrusions.push_back(ex);   
            }
        }

        if (extrusions.size() != 1) {
            Logger::Message(Logger::LOG_WARNING, "No single extrusion found in body representation for:", product);
            return false;
        }

        IfcSchema::IfcExtrudedAreaSolid& extrusion = extrusions.front();

        taxonomy::matrix4::ptr extrusion_position;

        bool has_position = true;
#ifdef SCHEMA_IfcSweptAreaSolid_Position_IS_OPTIONAL
        has_position = !!extrusion.Position();
#endif
        if (has_position) {
            auto m4 = taxonomy::cast<taxonomy::matrix4>(map(extrusion.Position()));
            if (!m4) {
                Logger::Message(Logger::LOG_ERROR, "Failed to convert placement for extrusion of:", product);
                return false;
            } else {
                extrusion_position = m4;
            }
        }

        taxonomy::direction3::ptr extrusion_direction = taxonomy::cast<taxonomy::direction3>(map(extrusion.ExtrudedDirection()));

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

        for (auto& layer : material_layers) {
            info.styles.push_back(*taxonomy::cast<taxonomy::style>(map(layer.Material())));

            double thickness = layer.LayerThickness() * this->length_unit_;

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

bool mapping::get_wall_neighbours(const express::Base&, std::vector<endpoint_connection>&) {
    return false;
}

IfcSchema::IfcRepresentation mapping::find_representation(const IfcSchema::IfcProduct& product, const std::string& identifier) {
    if (auto prod_rep = product.Representation()) {
        std::vector<IfcSchema::IfcRepresentation> reps = prod_rep.Representations();
        for (auto& rep : reps) {
            if (rep.RepresentationIdentifier() && *rep.RepresentationIdentifier() == identifier) {
                return rep;
            }
        }
    }
    return IfcSchema::IfcRepresentation{};
}

void mapping::addRepresentationsFromContextIds(std::vector<IfcSchema::IfcRepresentation>& representations) {
    for (auto context_id : settings_.get<settings::ContextIds>().get()) {
        IfcSchema::IfcGeometricRepresentationContext context;
        try {
            context = file_->instance_by_id(context_id).as<IfcSchema::IfcGeometricRepresentationContext>();
        } catch (IfcParse::IfcException& e) {
            Logger::Error(e);
            continue;
        }

        if (!context) {
            Logger::Error("Failed to process context ID " + std::to_string(context_id));
            continue;
        }

        auto reps_in_context = context.RepresentationsInContext();
        for (auto& rep : reps_in_context) {
            representations.push_back(rep);
        }
    }
}

void mapping::addRepresentationsFromDefaultContexts(std::vector<IfcSchema::IfcRepresentation>& representations) {
    std::set<std::string> allowed_context_types;
    allowed_context_types.insert("model");
    allowed_context_types.insert("plan");
    allowed_context_types.insert("notdefined");

    std::set<std::string> context_types;
    if (this->settings_.get<settings::OutputDimensionality>().get() != settings::CURVES) {
        // Really this should only be 'Model', as per
        // the standard 'Design' is deprecated. So,
        // just for backwards compatibility:
        context_types.insert("model");
        context_types.insert("design");
        // Some earlier (?) versions DDS-CAD output their own ContextTypes
        context_types.insert("model view");
        context_types.insert("detail view");
    }
    if (this->settings_.get<settings::OutputDimensionality>().get() != settings::SURFACES_AND_SOLIDS) {
        context_types.insert("plan");
    }

    auto contexts =
        file_->instances_by_type<IfcSchema::IfcGeometricRepresentationContext>();

    std::vector<IfcSchema::IfcGeometricRepresentationContext> filtered_contexts;

    for (auto& context : contexts) {
        if (context.declaration().is(IfcSchema::IfcGeometricRepresentationSubContext::Class())) {
            // Continue, as the list of subcontexts will be considered
            // by the parent's context inverse attributes.
            continue;
        }
        try {
            if (context.ContextType()) {
                std::string context_type = *context.ContextType();
                boost::to_lower(context_type);

                if (allowed_context_types.find(context_type) == allowed_context_types.end()) {
                    Logger::Warning(std::string("ContextType '") + *context.ContextType() + "' not allowed:", context);
                }
                if (context_types.find(context_type) != context_types.end()) {
                    filtered_contexts.push_back(context);
                }
            }
        } catch (const std::exception& e) {
            Logger::Error(e);
        }
    }

    // In case no contexts are identified based on their ContextType, all contexts are
    // considered. Note that sub contexts are excluded as they are considered later on.
    if (filtered_contexts.empty()) {
        for (auto& context : contexts) {
            if (!context.declaration().is(IfcSchema::IfcGeometricRepresentationSubContext::Class())) {
                filtered_contexts.push_back(context);
            }
        }
    }

    for (auto& context : filtered_contexts) {
        auto reps_in_context = context.RepresentationsInContext();
        representations.insert(representations.end(), reps_in_context.begin(), reps_in_context.end());

        std::vector<IfcSchema::IfcGeometricRepresentationSubContext> sub_contexts = context.HasSubContexts();
        for (auto& subcontext : sub_contexts) {
            auto reps_in_subcontext = subcontext.RepresentationsInContext();
            representations.insert(representations.end(), reps_in_subcontext.begin(), reps_in_subcontext.end());
        }

        // There is no need for full recursion as the following is governed by the schema:
        // WR31: The parent context shall not be another geometric representation sub context.
    }

    if (representations.empty()) {
        Logger::Warning("No representations encountered in relevant contexts, using all");
        auto all_reps = file_->instances_by_type<IfcSchema::IfcRepresentation>();
        representations = all_reps;
    }
}

express::Base mapping::representation_of(const express::Base& product) {
    // @todo correct, but very inefficient
    std::vector<IfcSchema::IfcRepresentation> representations;
    std::vector<IfcSchema::IfcRepresentation> of_product;
    std::vector<IfcSchema::IfcRepresentation> intersection;
    std::vector<IfcSchema::IfcRepresentation> intersection_no_box;

    if (!settings_.get<settings::ContextIds>().has()) {
        addRepresentationsFromDefaultContexts(representations);
    } else {
        addRepresentationsFromContextIds(representations);
    }

    if (product.as<IfcSchema::IfcProduct>().Representation()) {
        of_product = product.as<IfcSchema::IfcProduct>().Representation().Representations();
    }

    for (auto& r : of_product) {
        if (std::find(representations.begin(), representations.end(), r) != representations.end()) {
            intersection.push_back(r);
        }
    }

    if (intersection.size() == 0 && settings_.get<settings::ContextIds>().has() && this->settings_.get<settings::OutputDimensionality>().get() == settings::CURVES) {
        for (auto& r : of_product) {
            if (r.RepresentationIdentifier() && *r.RepresentationIdentifier() == "Axis") {
                intersection.push_back(r);
            }
        }
    }

    if (intersection.size() == 0) {
        return express::Base{};
    } else {
        for (auto& r : intersection) {
            auto resources = IfcParse::traverse(r);
            auto is_bounding_box = std::any_of(resources.begin(), resources.end(), [](const auto& res) { return res.declaration().is(IfcSchema::IfcBoundingBox::Class()); });
            if (is_bounding_box) {
                continue;
            }
            intersection_no_box.push_back(r);
        }
        if (intersection_no_box.size() > 1) {
            Logger::Warning("Multiple applicable representations found for element, selecting arbitrary");
        }
        if (intersection_no_box.size()) {
            return intersection_no_box.front();
        } else {
            return intersection.front();
        }
    }
}
