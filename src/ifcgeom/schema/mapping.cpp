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

using namespace IfcUtil;
using namespace ifcopenshell::geometry;

namespace {
	struct POSTFIX_SCHEMA(factory_t) {
		abstract_mapping* operator()(IfcParse::IfcFile* file, settings& settings) const {
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
				loop->external = true;

				face_ = taxonomy::face();
				face_->instance = loop->instance;
				face_->matrix = loop->matrix;
				// @todo make sure loop is not freed
				// this is accounted for below with as::upgraded_
				face_->children = { loop };
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
		mutable bool upgraded_;

	public:
		as(taxonomy::item* item) : item_(item), upgraded_(false) {}
		operator T() const {
			if (!item_) {
				throw taxonomy::topology_error("item was nullptr");
			}
			T* t = dynamic_cast<T*>(item_);
			if (t) {
				return *t;
			} else {
				{
					loop_to_face_upgrade<T> upgrade(item_);
					if (upgrade) {
						upgraded_ = true;
						return upgrade;
					}
				}
				throw taxonomy::topology_error("item does not match type");
			}
		}
		~as() {
			if (!upgraded_) {
				// @todo revisit this
				delete item_;
			}
		}
	};

	template <typename U = taxonomy::collection, typename T>
	U* map_to_collection(mapping* m, const T& ts) {
		auto c = new U;
		if (ts->size()) {
			for (auto it = ts->begin(); it != ts->end(); ++it) {
				if (auto r = m->map(*it)) {
					c->children.push_back(r);
				}
			}
		}
		if (c->children.empty()) {
			delete c;
			return nullptr;
		}
		return c;
	}
};

taxonomy::item* mapping::map_impl(const IfcSchema::IfcExtrudedAreaSolid* inst) {
	return new taxonomy::extrusion(
		as<taxonomy::matrix4>(map(inst->Position())),
		as<taxonomy::face>(map(inst->SweptArea())),
		as<taxonomy::direction3>(map(inst->ExtrudedDirection())),
		inst->Depth() * length_unit_
	);
}

namespace {
	template <typename Fn>
	void visit(taxonomy::collection* deep, Fn fn) {
		for (auto& c : deep->children) {
			if (c->kind() == taxonomy::COLLECTION) {
				visit((taxonomy::collection*)c, fn);
			} else {
				fn(c);
			}
		}
	}

	taxonomy::collection* flatten(taxonomy::collection* deep) {
		auto flat = new taxonomy::collection;
		visit(deep, [&flat](taxonomy::item* i) {
			flat->children.push_back(i);
		});
		return flat;
	}

	template <typename Fn>
	bool apply_predicate_to_collection(taxonomy::item* i, Fn fn) {
		if (i->kind() == taxonomy::COLLECTION) {
			auto c = (taxonomy::collection*) i;
			for (auto& child : c->children) {
				if (apply_predicate_to_collection(child, fn)) {
					return true;
				}
			}
		} else {
			return fn(i);
		}
	}

	// @nb traverses nested collections
	template <typename Fn>
	taxonomy::collection* filter(taxonomy::collection* collection, Fn fn) {
		auto filtered = new taxonomy::collection;
		for (auto& child : collection->children) {
			if (apply_predicate_to_collection(child, fn)) {
				filtered->children.push_back(child);
			}
		}
		if (filtered->children.empty()) {
			delete filtered;
			return nullptr;
		}
		return filtered;
	}
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcRepresentation* inst) {
	const bool use_body = !this->settings_.get(ifcopenshell::geometry::settings::INCLUDE_CURVES);

	auto items = map_to_collection(this, inst->Items());
	if (items == nullptr) {
		return nullptr;
	}

	/*
	// Don't blindly flatten, as we're culling away IfcMappedItem transformations

	auto flat = flatten(items);
	if (flat == nullptr) {
		return nullptr;
	}
	*/

	auto filtered = filter(items, [&use_body](taxonomy::item* i) {
		// @todo just filter loops for now.
		return (i->kind() != taxonomy::LOOP) == use_body;
	});

	delete items;

	return filtered;
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcFaceBasedSurfaceModel* inst) {
	return map_to_collection(this, inst->FbsmFaces());
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcShellBasedSurfaceModel* inst) {
	return map_to_collection(this, inst->SbsmBoundary());
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcManifoldSolidBrep* inst) {
	// @todo voids
	return map(inst->Outer());
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcGeometricSet* inst) {
	return map_to_collection(this, inst->Elements());
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcConnectedFaceSet* inst) {
	auto shell = map_to_collection<taxonomy::shell>(this, inst->CfsFaces());
	if (shell == nullptr) {
		return nullptr;
	}
	shell->closed = inst->declaration().is(IfcSchema::IfcClosedShell::Class());
	return shell;
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcFace* inst) {
	taxonomy::face* face = new taxonomy::face;
	auto bounds = inst->Bounds();
	for (auto& bound : *bounds) {
		if (auto r = map(bound->Bound())) {
			if (!bound->Orientation()) {
				r->reverse();
			}
			if (bound->declaration().is(IfcSchema::IfcFaceOuterBound::Class())) {
				// Make a copy in case we need immutability later for e.g. caching
				auto s = r->clone();
				((taxonomy::loop*)s)->external = true;
				delete r;
				r = s;
			}
			face->children.push_back(r);
		}		
	}
	if (face->children.empty()) {
		delete face;
		return nullptr;
	}
	return face;
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcPolyLoop* inst) {
	taxonomy::loop* loop = new taxonomy::loop;
	
	taxonomy::point3 first, previous;
	bool is_first = true;
	
	auto points = inst->Polygon();
	for (auto& point : *points) {
		auto p = as<taxonomy::point3>(map(point));
		if (is_first) {
			previous = first = p;
			is_first = false;
		} else {
			auto edge = new taxonomy::edge;
			edge->start = previous;
			edge->end = p;
			loop->children.push_back(edge);
			previous = p;
		}
	}
	
	auto edge = new taxonomy::edge;
	edge->start = previous;
	edge->end = first;
	loop->children.push_back(edge);
	
	if (loop->children.size() < 3) {
		Logger::Warning("Not enough edges for", inst);
		delete loop;
		return nullptr;
	}
	return loop;
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcCartesianPoint* inst) {
	auto coords = inst->Coordinates();
	return new taxonomy::point3(
		coords.size() >= 1 ? coords[0] * length_unit_ : 0.,
		coords.size() >= 2 ? coords[1] * length_unit_ : 0.,
		coords.size() >= 3 ? coords[2] * length_unit_ : 0.
	);
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcDirection* inst) {
	auto coords = inst->DirectionRatios();
	return new taxonomy::direction3(
		coords.size() >= 1 ? coords[0] : 0.,
		coords.size() >= 2 ? coords[1] : 0.,
		coords.size() >= 3 ? coords[2] : 0.
	);
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcProduct* inst) {
	const bool use_body = !this->settings_.get(ifcopenshell::geometry::settings::INCLUDE_CURVES);

	auto openings = find_openings(inst);
	// @todo const cast
	auto reps = inst->data().file->traverse((IfcSchema::IfcProduct*) inst, 2)->as<IfcSchema::IfcRepresentation>();
	IfcSchema::IfcRepresentation* body = nullptr;
	for (auto& rep : *reps) {
		if ((rep->RepresentationIdentifier() == "Body") == use_body) {
			body = rep;
		}
	}
	if (!body) {
		return nullptr;
	}

	auto c = new taxonomy::collection;
	c->matrix = as<taxonomy::matrix4>(map(inst->ObjectPlacement()));

	const IfcSchema::IfcMaterial* single_material = get_single_material_association(inst);
	if (single_material) {
		auto material_style = map(single_material);
		if (material_style) {
			c->surface_style = as<taxonomy::style>(material_style);
		}
	}

	if (openings->size() && !settings_.get(settings::DISABLE_OPENING_SUBTRACTIONS) && use_body) {
		auto ci = c->matrix.components->inverse();

		IfcEntityList::ptr operands(new IfcEntityList);
		operands->push(body);
		operands->push(openings);
		auto n = map_to_collection<taxonomy::boolean_result>(this, operands);
		std::for_each(n->children.begin() + 1, n->children.end(), [&ci](taxonomy::item* i) {
			*((taxonomy::geom_item*)i)->matrix.components = ci * *((taxonomy::geom_item*)i)->matrix.components;
		});
		n->operation = taxonomy::boolean_result::SUBTRACTION;
		// @todo one indirection too many
		n->instance = inst;
		c->children = { n };
	} else {
		auto child = map(body);
		if (child) {
			c->children = { child };
		} else {
			delete c;
			return nullptr;			
		}
	}

	return c;
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcAxis2Placement3D* inst) {
	Eigen::Vector3d o, axis(0, 0, 1), refDirection, X(1, 0, 0);
	{
		taxonomy::point3 v = as<taxonomy::point3>(map(inst->Location()));
		o = *v.components;
	}
	const bool hasAxis = inst->hasAxis();
	const bool hasRef = inst->hasRefDirection();

	if (hasAxis != hasRef) {
		Logger::Warning("Axis and RefDirection should be specified together", inst);
	}

	if (hasAxis) {
		taxonomy::direction3 v = as<taxonomy::direction3>(map(inst->Axis()));
		axis = *v.components;
	}

	if (hasRef) {
		taxonomy::direction3 v = as<taxonomy::direction3>(map(inst->RefDirection()));
		refDirection = *v.components;
	} else {
		if (acos(axis.dot(X)) > 1.e-5) {
			refDirection = { 1., 0., 0. };
		} else {
			refDirection = { 0., 0., 1. };
		}
		auto Xvec = axis.dot(refDirection) * axis;
		auto Xaxis = refDirection - Xvec;
		refDirection = Xaxis;
	}
	return new taxonomy::matrix4(o, axis, refDirection);
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcAxis2Placement2D* inst) {
	Eigen::Vector3d P, axis(0, 0, 1), V(1, 0, 0);
	{
		taxonomy::point3 v = as<taxonomy::point3>(map(inst->Location()));
		P = *v.components;
	}
	const bool hasRef = inst->hasRefDirection();
	if (hasRef) {
		taxonomy::direction3 v = as<taxonomy::direction3>(map(inst->RefDirection()));
		V = *v.components;
	}
	return new taxonomy::matrix4(P, axis, V);
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcCartesianTransformationOperator2D* inst) {
	auto m = new taxonomy::matrix4;
	
	Eigen::Vector4d origin, axis1(1.0, 0.0, 0.0, 0.0), axis2(0.0, 1.0, 0.0, 0.0), axis3(0.0, 0.0, 1.0, 0.0);
	
	taxonomy::point3 O = as<taxonomy::point3>(map(inst->LocalOrigin()));
	origin << *O.components, 1.0;
	
	if (inst->hasAxis1()) {
		taxonomy::direction3 ax1 = as<taxonomy::direction3>(map(inst->Axis1()));
		axis1 << *ax1.components, 0.0;
	}	
	if (inst->hasAxis2()) {
		taxonomy::direction3 ax2 = as<taxonomy::direction3>(map(inst->Axis1()));
		axis2 << *ax2.components, 0.0;
	}

	double scale1, scale2;
	scale1 = scale2 = 1.0;

	if (inst->hasScale()) {
		scale1 = inst->Scale();
	}
	if (inst->as<IfcSchema::IfcCartesianTransformationOperator2DnonUniform>()) {
		auto nu = inst->as<IfcSchema::IfcCartesianTransformationOperator2DnonUniform>();
		scale2 = nu->hasScale2() ? nu->Scale2() : scale1;
	}

	*m->components << 
		axis1 * scale1, 
		axis2 * scale2, 
		axis3, 
		origin;

	m->components->transposeInPlace();

	return m;
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcCartesianTransformationOperator3D* inst) {
	auto m = new taxonomy::matrix4;

	Eigen::Vector4d origin;
	Eigen::Vector4d axis1(1., 0., 0., 0.);
	Eigen::Vector4d axis2(0., 1., 0., 0.);
	Eigen::Vector4d axis3(0., 0., 1., 0.);

	taxonomy::point3 O = as<taxonomy::point3>(map(inst->LocalOrigin()));
	origin << *O.components, 1.0;

	if (inst->hasAxis1()) {
		taxonomy::direction3 ax1 = as<taxonomy::direction3>(map(inst->Axis1()));
		axis1 << *ax1.components, 0.0;
	}
	if (inst->hasAxis2()) {
		taxonomy::direction3 ax2 = as<taxonomy::direction3>(map(inst->Axis2()));
		axis2 << *ax2.components, 0.0;
	}
	if (inst->hasAxis3()) {
		taxonomy::direction3 ax3 = as<taxonomy::direction3>(map(inst->Axis3()));
		axis3 << *ax3.components, 0.0;
	}

	double scale1, scale2, scale3;
	scale1 = scale2 = scale3 = 1.;

	if (inst->hasScale()) {
		scale1 = inst->Scale();
	}
	if (inst->as<IfcSchema::IfcCartesianTransformationOperator3DnonUniform>()) {
		auto nu = inst->as<IfcSchema::IfcCartesianTransformationOperator3DnonUniform>();
		scale2 = nu->hasScale2() ? nu->Scale2() : scale1;
		scale3 = nu->hasScale3() ? nu->Scale3() : scale1;
	}

	Eigen::Matrix4d tmp;
	tmp <<
		axis1 * scale1,
		axis2 * scale2,
		axis3 * scale3,
		origin;

	*m->components = tmp.inverse();
	m->components->transposeInPlace();

	// @todo tag identity?

	return m;
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcLocalPlacement* inst) {
	IfcSchema::IfcLocalPlacement* current = (IfcSchema::IfcLocalPlacement*)inst;
	auto m4 = new taxonomy::matrix4;
	for (;;) {
		IfcSchema::IfcAxis2Placement* relplacement = current->RelativePlacement();
		if (relplacement->declaration().is(IfcSchema::IfcAxis2Placement3D::Class())) {
			taxonomy::matrix4 trsf2 = as<taxonomy::matrix4>(map(relplacement));
			// @todo check
			*m4->components = *trsf2.components * *m4->components;
		}
		if (current->hasPlacementRelTo()) {
			IfcSchema::IfcObjectPlacement* parent = current->PlacementRelTo();
			IfcSchema::IfcProduct::list::ptr parentPlaces = parent->PlacesObject();
			bool parentPlacesType = false;
			for (IfcSchema::IfcProduct::list::it iter = parentPlaces->begin();
				iter != parentPlaces->end(); ++iter) {
				if ((*iter)->declaration().is(*placement_rel_to_)) {
					parentPlacesType = true;
				}
			}
			if (parentPlacesType) {
				break;
			} else if (parent->declaration().is(IfcSchema::IfcLocalPlacement::Class())) {
				current = (IfcSchema::IfcLocalPlacement*)current->PlacementRelTo();
			} else {
				break;
			}
		} else {
			break;
		}
	}
	return m4;
}

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
		taxonomy::matrix4 origin = as<taxonomy::matrix4>(map(rmap->MappingOrigin()));
		if (origin.components->isIdentity()) {
			IfcSchema::IfcMappedItem::list::ptr items = rmap->MapUsage();
			for (IfcSchema::IfcMappedItem::list::it it = items->begin(); it != items->end(); ++it) {
				IfcSchema::IfcMappedItem* item = *it;
				if (item->StyledByItem()->size() != 0) continue;

				taxonomy::matrix4 target = as<taxonomy::matrix4>(map(item->MappingTarget()));
				if (target.components->isIdentity()) {
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

IfcEntityList::ptr mapping::find_openings(const IfcSchema::IfcProduct* product) {

	IfcEntityList::ptr openings(new IfcEntityList);
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

	IfcSchema::IfcRepresentation::list::ptr ok_mapped_representations(new IfcSchema::IfcRepresentation::list);

	int task_index = 0;
	
	for (auto representation : *representations) {
		// There used to be a whole lot of magic in here to pair multiple products with,
		// representations but this is now handled at a later stage where equivalent
		// taxonomy::items (sorted based on std::less) are grouped.

		IfcSchema::IfcProduct::list::ptr ifcproducts = filter_products(products_represented_by(representation, true), filters);
		
		if (ifcproducts->size() == 0) {
			continue;
		}

		// @todo, fix this properly by considering the mapped geometry types in the representation.
		if (representation->hasRepresentationIdentifier() && representation->RepresentationIdentifier() == "Body") {
			geometry_conversion_task task;
			task.index = task_index++;
			task.representation = representation;
			task.products = ifcproducts->generalize();

			tasks.emplace_back(task);
		}
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
				if (target.components->isIdentity()) {
					IfcSchema::IfcRepresentationMap* rmap = mapped_item->MappingSource();
					taxonomy::matrix4 origin = as<taxonomy::matrix4>(map(rmap->MappingOrigin()));
					if (origin.components->isIdentity()) {
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

taxonomy::item* mapping::map_impl(const IfcSchema::IfcMaterial* material) {
	IfcSchema::IfcMaterialDefinitionRepresentation::list::ptr defs = material->HasRepresentation();
	for (IfcSchema::IfcMaterialDefinitionRepresentation::list::it jt = defs->begin(); jt != defs->end(); ++jt) {
		IfcSchema::IfcRepresentation::list::ptr reps = (*jt)->Representations();
		IfcSchema::IfcStyledItem::list::ptr styles(new IfcSchema::IfcStyledItem::list);
		for (IfcSchema::IfcRepresentation::list::it it = reps->begin(); it != reps->end(); ++it) {
			styles->push((**it).Items()->as<IfcSchema::IfcStyledItem>());
		}
		if (styles->size() == 1) {
			auto s = map(*styles->begin());
			if (s) {
				return s;
			}
		}
	}

	taxonomy::style* material_style = new taxonomy::style;
	return material_style;

	// @todo
	// IfcGeom::SurfaceStyle material_style = IfcGeom::SurfaceStyle(material->data().id(), material->Name());
	// return &(style_cache[material->data().id()] = material_style);
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcStyledItem* inst) {
	auto style_pair = get_surface_style<IfcSchema::IfcSurfaceStyleShading>(inst);
	IfcSchema::IfcSurfaceStyle* style = style_pair.first;
	IfcSchema::IfcSurfaceStyleShading* shading = style_pair.second;

	if (style == nullptr) {
		return nullptr;
	}
	
	static taxonomy::colour white = taxonomy::colour(1., 1., 1.);

	taxonomy::style* surface_style = new taxonomy::style;

	surface_style->instance = style;
	if (style->hasName()) {
		surface_style->name = style->Name();
	}
	
	double rgb[3];
	if (process_colour(shading->SurfaceColour(), rgb)) {
		surface_style->diffuse.emplace();
		(*(*surface_style->diffuse).components) << rgb[0], rgb[1], rgb[2];
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
	// std::wcout << l->data().toString().c_str() << std::endl;
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

IfcUtil::IfcBaseEntity* mapping::get_decomposing_entity(IfcUtil::IfcBaseEntity* inst, bool include_openings) {
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

std::map<std::string, IfcUtil::IfcBaseEntity*> mapping::get_layers(IfcUtil::IfcBaseEntity* inst) {
	auto prod = inst->as<IfcSchema::IfcProduct>();
	std::map<std::string, IfcUtil::IfcBaseEntity*> layers;
	if (prod->hasRepresentation()) {
		IfcEntityList::ptr r = IfcParse::traverse(prod->Representation());
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

#include "../../ifcparse/IfcSIPrefix.h"

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
		IfcEntityList::ptr units = unit_assignment->Units();
		if (!units || !units->size()) {
			Logger::Warning("No unit information found");
		} else {
			for (IfcEntityList::it it = units->begin(); it != units->end(); ++it) {
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
								if (si_unit->hasPrefix()) {
									current_unit_name = IfcSchema::IfcSIPrefix::ToString(si_unit->Prefix());
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

namespace {
	struct profile_point {
		std::array<double, 2> xy;
		boost::optional<double> radius;
	};

	struct profile_point_with_edges {
		Eigen::Vector2d xy;
		boost::optional<double> radius;
		taxonomy::edge *previous, *next;
	};

	taxonomy::loop* polygon_from_points(const std::vector<taxonomy::point3>& ps, bool external = true) {
		auto loop = new taxonomy::loop();
		loop->external = external;
		boost::optional<taxonomy::point3> previous;
		for (auto& p : ps) {
			if (previous) {
				auto e = new taxonomy::edge;
				e->start = *previous;
				e->end = p;
				loop->children.push_back(e);
			}
			previous = p;			
		}
		return loop;
	}

	taxonomy::loop* profile_helper(mapping* self, const IfcSchema::IfcParameterizedProfileDef* inst, const std::vector<profile_point>& points) {
		
		/* TopoDS_Vertex* vertices = new TopoDS_Vertex[numVerts];

		for (int i = 0; i < numVerts; i++) {
			gp_XY xy(verts[2 * i], verts[2 * i + 1]);
			trsf.Transforms(xy);
			vertices[i] = BRepBuilderAPI_MakeVertex(gp_Pnt(xy.X(), xy.Y(), 0.0f));
		}

		BRepBuilderAPI_MakeWire w;
		for (int i = 0; i < numVerts; i++)
			w.Add(BRepBuilderAPI_MakeEdge(vertices[i], vertices[(i + 1) % numVerts]));

		TopoDS_Face face;
		convert_wire_to_face(w.Wire(), face);

		if (numFillets && *std::max_element(filletRadii, filletRadii + numFillets) > ALMOST_ZERO) {
			BRepFilletAPI_MakeFillet2d fillet(face);
			for (int i = 0; i < numFillets; i++) {
				const double radius = filletRadii[i];
				if (radius <= ALMOST_ZERO) continue;
				fillet.AddFillet(vertices[filletIndices[i]], radius);
			}
			fillet.Build();
			if (fillet.IsDone()) {
				face = TopoDS::Face(fillet.Shape());
			} else {
				Logger::Error("Failed to process profile fillets");
			}
		}
		*/

		Eigen::Matrix4d m4;

		bool has_position = true;
#ifdef SCHEMA_IfcParameterizedProfileDef_Position_IS_OPTIONAL
		has_position = inst->hasPosition();
#endif
		if (has_position) {
			taxonomy::matrix4 m = as<taxonomy::matrix4>(self->map(inst->Position()));
			m4 = *m.components;
		}

		// @todo precision
		if (m4.isIdentity()) {
			has_position = false;
		}

		std::vector<taxonomy::point3> ps;
		ps.reserve(points.size() + 1);
		std::transform(points.begin(), points.end(), std::back_inserter(ps), [&has_position, &m4](const profile_point& p) {
			if (has_position) {
				Eigen::Vector4d v(p.xy[0], p.xy[1], 0., 1.);
				v = m4 * v;
				return taxonomy::point3(v(0), v(1), 0.);
			} else {
				return taxonomy::point3(p.xy[0], p.xy[1], 0.);
			}			
		});
		ps.push_back(ps.front());

		auto loop = polygon_from_points(ps);

		std::vector<profile_point_with_edges> pps(points.size());
		for (int b = 0; b < points.size(); ++b) {
			int c = (b - 1) % points.size();
			pps[b] = { Eigen::Vector2d(points[b].xy[0], points[b].xy[1]), points[b].radius, (taxonomy::edge*) loop->children[c], (taxonomy::edge*) loop->children[b]};
		}

		size_t i = pps.size();
		while (i--) {
			const auto& p = pps[i];
			if (p.radius && *p.radius > 0.) {
				// Position is a IfcAxis2Placement2D, so should remain 2d points
				auto p0 = boost::get<taxonomy::point3>(p.previous->start).components->head<2>();
				auto p1a = boost::get<taxonomy::point3>(p.previous->end).components->head<2>();
				auto p2 = boost::get<taxonomy::point3>(p.next->end).components->head<2>();
				auto p1b = boost::get<taxonomy::point3>(p.next->start).components->head<2>();

				auto ba_ = p0 - p1a;
				auto bc_ = p2 - p1b;

				auto ba = ba_.normalized();
				auto bc = bc_.normalized();

				const double angle = std::acos(ba.dot(bc));
				const double inset = *p.radius / std::tan(angle / 2.);

				boost::get<taxonomy::point3>(p.previous->end).components->head<2>() += ba * inset;
				boost::get<taxonomy::point3>(p.next->start).components->head<2>() += bc * inset;

				auto e = new taxonomy::edge;
				e->start = p.previous->end;
				e->end = p.next->start;

				auto ab = Eigen::Vector3d(-ba(1), +ba(0), 0.);
				
				double sign = ab.head<2>().dot(bc) > 0 ? 1. : -1.;

				auto O = boost::get<taxonomy::point3>(p.previous->end).components->head<3>() + ab * *p.radius * sign;

				auto c = new taxonomy::circle;
				*c->matrix.components = Eigen::Affine3d(Eigen::Translation3d(O)).matrix();
				c->radius = *p.radius;
				e->basis = c;
				c->orientation.reset(sign == -1.);

				loop->children.insert(std::find(loop->children.begin(), loop->children.end(), p.next), e);
			}
		};

		return loop;
	}
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcRectangleProfileDef* inst) {
	const double x = inst->XDim() / 2.0f * length_unit_;
	const double y = inst->YDim() / 2.0f * length_unit_;
	boost::optional<double> radius;
	if (inst->as<IfcSchema::IfcRoundedRectangleProfileDef>()) {
		radius = inst->as<IfcSchema::IfcRoundedRectangleProfileDef>()->RoundingRadius() * length_unit_;
	}
	
	// @todo
	const double precision_ = 1.e-5;

	if (x < precision_ || y < precision_) {
		Logger::Message(Logger::LOG_NOTICE, "Skipping zero sized profile:", inst);
		return nullptr;
	}

	return profile_helper(this, inst, {
		{{-x, -y}, radius},
		{{+x, -y}, radius},
		{{+x, +y}, radius},
		{{-x, +y}, radius},
	});
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcRectangleHollowProfileDef* inst) {
	const double x = inst->XDim() / 2.0f * length_unit_;
	const double y = inst->YDim() / 2.0f * length_unit_;
	const double d = inst->WallThickness() * length_unit_;

	boost::optional<double> radius1, radius2;
	if (inst->hasOuterFilletRadius()) {
		radius1 = inst->OuterFilletRadius() * length_unit_;
	}
	if (inst->hasInnerFilletRadius()) {
		radius2 = inst->InnerFilletRadius() * length_unit_;
	}
	
	// @todo
	const double precision_ = 1.e-5;

	if (x < precision_ || y < precision_) {
		Logger::Message(Logger::LOG_NOTICE, "Skipping zero sized profile:", inst);
		return nullptr;
	}

	auto outer_loop = profile_helper(this, inst, {
		{{-x, -y}, radius1},
		{{+x, -y}, radius1},
		{{+x, +y}, radius1},
		{{-x, +y}, radius1},
	});
	outer_loop->external = true;

	auto inner_loop = profile_helper(this, inst, {
		{{-x + d, -y + d}, radius2},
		{{+x - d, -y + d}, radius2},
		{{+x - d, +y - d}, radius2},
		{{-x + d, +y - d}, radius2},
	});
	inner_loop->reverse();
	inner_loop->external = false;

	auto face = new taxonomy::face;
	face->children = { outer_loop, inner_loop };

	// @todo is this necessary;
	std::swap(outer_loop->matrix, face->matrix);
	inner_loop->matrix = outer_loop->matrix;
	
	return face;
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcCircleProfileDef* inst) {
	std::vector<double> radii = { inst->Radius() * length_unit_ };
	
	if (inst->as<IfcSchema::IfcCircleHollowProfileDef>()) {
		double t = inst->as<IfcSchema::IfcCircleHollowProfileDef>()->WallThickness() * length_unit_;
		radii.push_back(radii.front() - t);
	}

	auto f = new taxonomy::face;

	for (auto it = radii.begin(); it != radii.end(); ++it) {
		const double r = *it;
		const bool exterior = it == radii.begin();

		auto c = new taxonomy::circle;
		c->radius = r;

		bool has_position = true;
#ifdef SCHEMA_IfcParameterizedProfileDef_Position_IS_OPTIONAL
		has_position = inst->hasPosition();
#endif
		if (has_position) {
			taxonomy::matrix4 m = as<taxonomy::matrix4>(map(inst->Position()));
			c->matrix = *m.components;
		}

		auto e = new taxonomy::edge;
		e->basis = c;
		e->start = 0.;
		e->end = 2 * M_PI;

		auto l = new taxonomy::loop;
		l->children = { e };
		l->external = exterior;

		f->children.push_back(l);
	}

	return f;
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcIShapeProfileDef* inst) {
	const double x1 = inst->OverallWidth() / 2.0f * length_unit_;
	const double y = inst->OverallDepth() / 2.0f * length_unit_;
	const double d1 = inst->WebThickness() / 2.0f  * length_unit_;
	const double dy1 = inst->FlangeThickness() * length_unit_;

	bool doFillet1 = inst->hasFilletRadius();
	double f1 = 0.;
	if (doFillet1) {
		f1 = inst->FilletRadius() * length_unit_;
	}

	bool doFillet2 = doFillet1;
	double x2 = x1, dy2 = dy1, f2 = f1;

	if (inst->declaration().is(IfcSchema::IfcAsymmetricIShapeProfileDef::Class())) {
		IfcSchema::IfcAsymmetricIShapeProfileDef* assym = (IfcSchema::IfcAsymmetricIShapeProfileDef*) inst;
		x2 = assym->TopFlangeWidth() / 2. * length_unit_;
		doFillet2 = assym->hasTopFlangeFilletRadius();
		if (doFillet2) {
			f2 = assym->TopFlangeFilletRadius() * length_unit_;
		}
		if (assym->hasTopFlangeThickness()) {
			dy2 = assym->TopFlangeThickness() * length_unit_;
		}
	}

	// @todo
	const double precision_ = 1.e-5;

	if (x1 < precision_ || x2 < precision_ || y < precision_ || d1 < precision_ || dy1 < precision_ || dy2 < precision_) {
		Logger::Message(Logger::LOG_NOTICE, "Skipping zero sized profile:", inst);

		return nullptr;
	}

	return profile_helper(this, inst, {
		{{-x1,-y}},
		{{x1,-y}},
		{{x1,-y + dy1}},
		{{d1,-y + dy1}, f1},
		{{d1,y - dy2}, f2},
		{{x2,y - dy2}},
		{{x2,y}},
		{{-x2,y}},
		{{-x2,y - dy2}},
		{{-d1,y - dy2}, f2},
		{{-d1,-y + dy1}, f1},
		{{-x1,-y + dy1}}
	});
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcArbitraryClosedProfileDef* inst) {
	auto loop = map(inst->OuterCurve());
	if (loop) {
		auto face = new taxonomy::face;
		((taxonomy::loop*)loop)->external = true;
		face->children = { loop };
		if (inst->as<IfcSchema::IfcArbitraryProfileDefWithVoids>()) {
			auto with_voids = inst->as<IfcSchema::IfcArbitraryProfileDefWithVoids>();
			auto voids = with_voids->InnerCurves();
			for (auto& v : *voids) {
				auto inner_loop = map(v);
				if (inner_loop) {
					((taxonomy::loop*)inner_loop)->external = false;
					face->children.push_back(inner_loop);
				}
			}
		}
		return face;
	} else {
		return nullptr;
	}
}

namespace {
	void remove_duplicate_points_from_loop(std::vector<taxonomy::point3>& polygon, bool closed, double tol) {
		for (;;) {
			bool removed = false;
			int n = polygon.size() - (closed ? 0 : 1);
			for (int i = 1; i <= n; ++i) {
				// wrap around to the first point in case of a closed loop
				int j = (i % polygon.size()) + 1;
				double dist = (*polygon.at(i - 1).components - *polygon.at(j - 1).components).squaredNorm();
				if (dist < tol) {
					// do not remove the first or last point to
					// maintain connectivity with other wires
					if ((closed && j == 1) || (!closed && j == n)) polygon.erase(polygon.begin() + i - 1);
					else polygon.erase(polygon.begin() + j - 1);
					removed = true;
					break;
				}
			}
			if (!removed) break;
		}
	}
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcPolyline* inst) {
	IfcSchema::IfcCartesianPoint::list::ptr points = inst->Points();

	// @todo
	const double precision_ = 1.e-5;

	// Parse and store the points in a sequence
	std::vector<taxonomy::point3> polygon;
	polygon.reserve(points->size());
	std::transform(points->begin(), points->end(), std::back_inserter(polygon), [this](const IfcSchema::IfcCartesianPoint* p) {
		return as<taxonomy::point3>(map(p));
	});

	const double eps = precision_ * 10;
	const bool closed_by_proximity = polygon.size() >= 3 && (*polygon.front().components - *polygon.back().components).norm() < eps;
	
	// @todo this removes the end point, since it's identical to the beginning. 
	if (closed_by_proximity) {
		// polygon.resize(polygon.size() - 1);
	}

	// Remove points that are too close to one another
	// remove_duplicate_points_from_loop(polygon, closed_by_proximity, eps);

	if (polygon.size() < 2) {
		return nullptr;
	}

	return polygon_from_points(polygon);
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcMappedItem* inst) {
	IfcSchema::IfcCartesianTransformationOperator* transform = inst->MappingTarget();
	taxonomy::matrix4 gtrsf = as<taxonomy::matrix4>(map(transform));
	IfcSchema::IfcRepresentationMap* rmap = inst->MappingSource();
	IfcSchema::IfcAxis2Placement* placement = rmap->MappingOrigin();
	taxonomy::matrix4 trsf2 = as<taxonomy::matrix4>(map(placement));
	*gtrsf.components = *gtrsf.components * *trsf2.components;
	
	// @todo immutable for caching?
	// @todo allow for multiple levels of matrix?
	auto shapes = map(rmap->MappedRepresentation());
	if (shapes == nullptr) {
		return shapes;
	}

	auto collection = new taxonomy::collection;
	collection->children.push_back(shapes);
	collection->matrix = *gtrsf.components;

	if (shapes != nullptr) {
		for (auto& c : ((taxonomy::collection*)shapes)->children) {
			// @todo previously style was also copied.
		}
	}

	return collection;
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcCompositeCurve* inst) {
	auto loop = new taxonomy::loop;
	auto segments = inst->Segments();
	for (auto& segment : *segments) {
		auto crv = map(segment->ParentCurve());
		if (crv) {
			if (crv->kind() == taxonomy::EDGE) {
				((taxonomy::edge*)crv)->orientation_2.reset(segment->SameSense());
				loop->children.push_back(crv);
			} else if (crv->kind() == taxonomy::LOOP) {
				if (!segment->SameSense()) {
					crv->reverse();
				}
				auto curve_segments = ((taxonomy::loop*)crv)->children_as<taxonomy::edge>();
				for (auto& s : curve_segments) {
					loop->children.push_back(s);
				}
				// @todo delete crv without children
			}
		}
	}
	IfcEntityList::ptr profile = inst->data().getInverse(&IfcSchema::IfcProfileDef::Class(), -1);
	const bool force_close = profile && profile->size() > 0;
	loop->closed = force_close;
	return loop;
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcTrimmedCurve* inst) {
	IfcSchema::IfcCurve* basis_curve = inst->BasisCurve();
	bool isConic = basis_curve->declaration().is(IfcSchema::IfcConic::Class());
	double parameterFactor = isConic ? angle_unit_ : length_unit_;

	auto tc = new taxonomy::edge;
	tc->basis = map(inst->BasisCurve());

	bool trim_cartesian = inst->MasterRepresentation() != IfcSchema::IfcTrimmingPreference::IfcTrimmingPreference_PARAMETER;
	IfcEntityList::ptr trims1 = inst->Trim1();
	IfcEntityList::ptr trims2 = inst->Trim2();

	// reversed orientation handling happens in geometry kernel
	unsigned sense_agreement = 0; // inst->SenseAgreement() ? 0 : 1;
	double flts[2];
	taxonomy::point3 pnts[2];
	bool has_flts[2] = { false,false };
	bool has_pnts[2] = { false,false };

	tc->orientation = inst->SenseAgreement();

	for (IfcEntityList::it it = trims1->begin(); it != trims1->end(); it++) {
		IfcUtil::IfcBaseClass* i = *it;
		if (i->declaration().is(IfcSchema::IfcCartesianPoint::Class())) {
			pnts[sense_agreement] = as<taxonomy::point3>(map(i));
			has_pnts[sense_agreement] = true;
		} else if (i->declaration().is(IfcSchema::IfcParameterValue::Class())) {
			const double value = *((IfcSchema::IfcParameterValue*)i);
			flts[sense_agreement] = value * parameterFactor;
			has_flts[sense_agreement] = true;
		}
	}

	for (IfcEntityList::it it = trims2->begin(); it != trims2->end(); it++) {
		IfcUtil::IfcBaseClass* i = *it;
		if (i->declaration().is(IfcSchema::IfcCartesianPoint::Class())) {
			pnts[1 - sense_agreement] = as<taxonomy::point3>(map(i));
			has_pnts[1 - sense_agreement] = true;
		} else if (i->declaration().is(IfcSchema::IfcParameterValue::Class())) {
			const double value = *((IfcSchema::IfcParameterValue*)i);
			flts[1 - sense_agreement] = value * parameterFactor;
			has_flts[1 - sense_agreement] = true;
		}
	}

	// @todo
	const double precision_ = 1.e-5;

	trim_cartesian &= has_pnts[0] && has_pnts[1];
	if (trim_cartesian) {
		if ((*pnts[0].components - *pnts[1].components).norm() < (2 * precision_)) {
			Logger::Message(Logger::LOG_WARNING, "Skipping segment with length below tolerance level:", inst);
			return nullptr;
		}
		tc->start = pnts[0];
		tc->end = pnts[1];
	} else if (has_flts[0] && has_flts[1]) {
		// The Geom_Line is constructed from a gp_Pnt and gp_Dir, whereas the IfcLine
		// is defined by an IfcCartesianPoint and an IfcVector with Magnitude. Because
		// the vector is normalised when passed to Geom_Line constructor the magnitude
		// needs to be factored in with the IfcParameterValue here.
		if (basis_curve->declaration().is(IfcSchema::IfcLine::Class())) {
			IfcSchema::IfcLine* line = static_cast<IfcSchema::IfcLine*>(basis_curve);
			const double magnitude = line->Dir()->Magnitude();
			flts[0] *= magnitude; flts[1] *= magnitude;
		}
		if (basis_curve->declaration().is(IfcSchema::IfcEllipse::Class())) {
			IfcSchema::IfcEllipse* ellipse = static_cast<IfcSchema::IfcEllipse*>(basis_curve);
			double x = ellipse->SemiAxis1() * length_unit_;
			double y = ellipse->SemiAxis2() * length_unit_;
			// @todo the need for this rotation is OCCT-specific
			const bool rotated = y > x;
			if (rotated) {
				flts[0] -= M_PI / 2.;
				flts[1] -= M_PI / 2.;
			}
		}
		tc->start = flts[0];
		tc->end = flts[1];
	}

	/*
	// @todo
	if (isConic) {
		// Tiny circle segnments can cause issues later on, for example
		// when the comp curve is used as the sweeping directrix.
		double a, b;
		Handle(Geom_Curve) crv = BRep_Tool::Curve(e, a, b);
		double radius = -1.;
		if (crv->DynamicType() == STANDARD_TYPE(Geom_Circle)) {
			radius = Handle(Geom_Circle)::DownCast(crv)->Radius();
		} else if (crv->DynamicType() == STANDARD_TYPE(Geom_Ellipse)) {
			// The formula above is for circles, but probably good enough
			radius = Handle(Geom_Ellipse)::DownCast(crv)->MajorRadius();
		}
		if (radius > 0. && deflection_for_approximating_circle(radius, b - a) < getValue(GV_PRECISION)) {
			TopoDS_Vertex v0, v1;
			TopExp::Vertices(e, v0, v1);
			e = TopoDS::Edge(BRepBuilderAPI_MakeEdge(v0, v1).Edge().Oriented(e.Orientation()));
			Logger::Warning("Subsituted edge with linear approximation", l);
		}
	}
	*/
		
	return tc;
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcCircle* inst) {
	auto c = new taxonomy::circle;
	c->matrix = as<taxonomy::matrix4>(map(inst->Position()));
	c->radius = inst->Radius() * length_unit_;
	return c;
}

namespace {
	taxonomy::boolean_result::operation_t boolean_op_type(IfcSchema::IfcBooleanOperator::Value op) {
		if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_DIFFERENCE) {
			return taxonomy::boolean_result::SUBTRACTION;
		} else if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_INTERSECTION) {
			return taxonomy::boolean_result::INTERSECTION;
		} else if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_UNION) {
			return taxonomy::boolean_result::UNION;
		} else {
			throw taxonomy::topology_error("Unknown boolean operation");
		}
	}

}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcBooleanResult* inst) {
	IfcSchema::IfcBooleanOperand* operand1 = inst->FirstOperand();
	IfcSchema::IfcBooleanOperand* operand2 = inst->SecondOperand();

	IfcEntityList::ptr operands(new IfcEntityList);
	operands->push(operand1);
	operands->push(operand2);

	auto op = boolean_op_type(inst->Operator());

	bool process_as_list = true;
	while (true) {
		auto res1 = operand1->as<IfcSchema::IfcBooleanResult>();
		if (res1) {
			if (boolean_op_type(res1->Operator()) == op) {
				operand1 = res1->FirstOperand();
				operands->push(res1->SecondOperand());
			} else {
				process_as_list = false;
				break;
			}
		} else {
			break;
		}
	}

	if (!process_as_list) {
		operand1 = inst->FirstOperand();
		operands.reset(new IfcEntityList);
		operands->push(operand1);
		operands->push(operand2);
	}

	auto br = map_to_collection<taxonomy::boolean_result>(this, operands);
	if (br) {
		br->operation = op;
	}
	return br;
}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcPolygonalBoundedHalfSpace* inst) {
	auto f = map_impl((IfcSchema::IfcHalfSpaceSolid*) inst);
	((taxonomy::face*)f)->children = ((taxonomy::loop)as<taxonomy::loop>(map(inst->PolygonalBoundary()))).children;
	return f;
}


taxonomy::item* mapping::map_impl(const IfcSchema::IfcHalfSpaceSolid* inst) {
	IfcSchema::IfcSurface* surface = inst->BaseSurface();
	if (!surface->declaration().is(IfcSchema::IfcPlane::Class())) {
		Logger::Message(Logger::LOG_ERROR, "Unsupported BaseSurface:", surface);
		return nullptr;
	}
	auto p = new taxonomy::plane;
	p->matrix = as<taxonomy::matrix4>(map(((IfcSchema::IfcPlane*)surface)->Position()));
	p->orientation.reset(!inst->AgreementFlag());
	auto f = new taxonomy::face;
	f->basis = p;
	return f;
}
