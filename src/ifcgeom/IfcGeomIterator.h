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
 * Geometrical data in an IFC file consists of shapes (IfcShapeRepresentation)  *
 * and instances (SUBTYPE OF IfcBuildingElement e.g. IfcWindow).                *
 *                                                                              *
 * IfcGeom::Representation::Triangulation is a class that represents a          *
 * triangulated IfcShapeRepresentation.                                         *
 *   Triangulation.verts is a 1 dimensional vector of float defining the        *
 *      cartesian coordinates of the vertices of the triangulated shape in the  *
 *      format of [x1,y1,z1,..,xn,yn,zn]                                        *
 *   Triangulation.faces is a 1 dimensional vector of int containing the        *
 *     indices of the triangles referencing positions in Triangulation.verts    *
 *   Triangulation.edges is a 1 dimensional vector of int in {0,1} that dictates*
 *	   the visibility of the edges that span the faces in Triangulation.faces   *
 *                                                                              *
 * IfcGeom::Element represents the actual IfcBuildingElements.                  *
 *   IfcGeomObject.name is the GUID of the element                              *
 *   IfcGeomObject.type is the datatype of the element e.g. IfcWindow           *
 *   IfcGeomObject.mesh is a pointer to an IfcMesh                              *
 *   IfcGeomObject.transformation.matrix is a 4x3 matrix that defines the       *
 *     orientation and translation of the mesh in relation to the world origin  *
 *                                                                              *
 * IfcGeom::Iterator::initialize()                                              *
 *   finds the most suitable representation contexts. Returns true iff          *
 *   at least a single representation will process successfully                 *
 *                                                                              *
 * IfcGeom::Iterator::get()                                                     *
 *   returns a pointer to the current IfcGeom::Element                          *
 *                                                                              * 
 * IfcGeom::Iterator::next()                                                    *
 *   returns true iff a following entity is available for a successive call to  *
 *   IfcGeom::Iterator::get()                                                   *
 *                                                                              *
 * IfcGeom::Iterator::progress()                                                *
 *   returns an int in [0..100] that indicates the overall progress             *
 *                                                                              *
 ********************************************************************************/

#ifndef IFCGEOMITERATOR_H
#define IFCGEOMITERATOR_H

#include <map>
#include <set>
#include <vector>
#include <limits>
#include <algorithm>

#include <boost/algorithm/string.hpp>

#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>

#include "../ifcparse/IfcFile.h"

#include "../ifcgeom/IfcGeom.h"
#include "../ifcgeom/IfcGeomElement.h"
#include "../ifcgeom/IfcGeomMaterial.h"
#include "../ifcgeom/IfcGeomIteratorSettings.h"
#include "../ifcgeom/IfcRepresentationShapeItem.h"
#include "../ifcgeom/IfcGeomFilter.h"

// The infamous min & max Win32 #defines can leak here from OCE depending on the build configuration
#ifdef min
#undef min
#endif
#ifdef max
#undef max
#endif

namespace IfcGeom {
	
	template <typename P>
	class Iterator {
	private:
		Iterator(const Iterator&); // N/I
		Iterator& operator=(const Iterator&); // N/I

		Kernel kernel;
		IteratorSettings settings;

		IfcParse::IfcFile* ifc_file;

		// A container and iterator for IfcRepresentations
		IfcSchema::IfcRepresentation::list::ptr representations;
		IfcSchema::IfcRepresentation::list::it representation_iterator;

		// The object is fetched beforehand to be sure that get() returns a valid element
		TriangulationElement<P>* current_triangulation;
		BRepElement<P>* current_shape_model;
		SerializedElement<P>* current_serialization;
		
		// A container and iterator for IfcBuildingElements for the current IfcRepresentation referenced by *representation_iterator
		IfcSchema::IfcProduct::list::ptr ifcproducts;
		IfcSchema::IfcProduct::list::it ifcproduct_iterator;

		int done;
		int total;

		std::string unit_name;
		double unit_magnitude;

        gp_XYZ bounds_min_;
        gp_XYZ bounds_max_;

        std::vector<filter_t> filters_;

        struct filter_match
        {
            filter_match(IfcSchema::IfcProduct *prod) : product(prod) {}
            bool operator()(const filter_t& filter) const { return filter(product);  }

            IfcSchema::IfcProduct* product;
        };

		void initUnits() {
			IfcSchema::IfcProject::list::ptr projects = ifc_file->entitiesByType<IfcSchema::IfcProject>();
			if (projects->size() == 1) {
				IfcSchema::IfcProject* project = *projects->begin();
				std::pair<std::string, double> length_unit = kernel.initializeUnits(project->UnitsInContext());
				unit_name = length_unit.first;
				unit_magnitude = length_unit.second;
			}
		}

        /// @todo public/private sections all over the place: move all public to the beginning of the class
	public:
        Iterator(const IteratorSettings& settings, IfcParse::IfcFile* file, std::vector<IfcGeom::filter_t>& filters)
            : settings(settings)
            , ifc_file(file)
            , owns_ifc_file(false)
            , filters_(filters)
        {
            _initialize();
        }

		bool initialize() {
			try {
				initUnits();
			} catch (const std::exception& e) {
				Logger::Error(e);
			}

			std::set<std::string> allowed_context_types;
			allowed_context_types.insert("model");
			allowed_context_types.insert("plan");
			allowed_context_types.insert("notdefined");

			std::set<std::string> context_types;
            if (!settings.get(IteratorSettings::EXCLUDE_SOLIDS_AND_SURFACES)) {
				// Really this should only be 'Model', as per 
				// the standard 'Design' is deprecated. So,
				// just for backwards compatibility:
				context_types.insert("model");
				context_types.insert("design");
				// Some earlier (?) versions DDS-CAD output their own ContextTypes
				context_types.insert("model view");
				context_types.insert("detail view");
			}
            if (settings.get(IteratorSettings::INCLUDE_CURVES)) {
				context_types.insert("plan");
			}			

			double lowest_precision_encountered = std::numeric_limits<double>::infinity();
			bool any_precision_encountered = false;

			representations = IfcSchema::IfcRepresentation::list::ptr(new IfcSchema::IfcRepresentation::list);

			IfcSchema::IfcGeometricRepresentationContext::list::it it;
			IfcSchema::IfcGeometricRepresentationSubContext::list::it jt;
			IfcSchema::IfcGeometricRepresentationContext::list::ptr contexts = 
				ifc_file->entitiesByType<IfcSchema::IfcGeometricRepresentationContext>();

			IfcSchema::IfcGeometricRepresentationContext::list::ptr filtered_contexts (new IfcSchema::IfcGeometricRepresentationContext::list);

 			for (it = contexts->begin(); it != contexts->end(); ++it) {
				IfcSchema::IfcGeometricRepresentationContext* context = *it;
				if (context->is(IfcSchema::Type::IfcGeometricRepresentationSubContext)) {
					// Continue, as the list of subcontexts will be considered
					// by the parent's context inverse attributes.
					continue;
				}
				try {
					if (context->hasContextType()) {
						std::string context_type = context->ContextType();
						boost::to_lower(context_type);

						if (allowed_context_types.find(context_type) == allowed_context_types.end()) {
							Logger::Message(Logger::LOG_ERROR, std::string("ContextType '") + context->ContextType() + "' not allowed:", context->entity);
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
					if (!context->is(IfcSchema::Type::IfcGeometricRepresentationSubContext)) {
						filtered_contexts->push(context);
					}
				}
			}

			for (it = filtered_contexts->begin(); it != filtered_contexts->end(); ++it) {
				IfcSchema::IfcGeometricRepresentationContext* context = *it;

				representations->push(context->RepresentationsInContext());
				try {
					if (context->hasPrecision() && context->Precision() < lowest_precision_encountered) {
						lowest_precision_encountered = context->Precision();
						any_precision_encountered = true;
					}
				} catch (const std::exception& e) {
					Logger::Error(e);
				}

				IfcSchema::IfcGeometricRepresentationSubContext::list::ptr sub_contexts = context->HasSubContexts();
				for (jt = sub_contexts->begin(); jt != sub_contexts->end(); ++jt) {
					representations->push((*jt)->RepresentationsInContext());
				}
				// There is no need for full recursion as the following is governed by the schema:
				// WR31: The parent context shall not be another geometric representation sub context. 
			}

			if (any_precision_encountered) {
				// Some arbitrary factor that has proven to work better for the models in the set of test files.
				lowest_precision_encountered *= 10.;

				lowest_precision_encountered *= unit_magnitude;
				if (lowest_precision_encountered < 1.e-7) {
					Logger::Message(Logger::LOG_WARNING, "Precision lower than 0.0000001 meter not enforced");
					kernel.setValue(IfcGeom::Kernel::GV_PRECISION, 1.e-7);
				} else {
					kernel.setValue(IfcGeom::Kernel::GV_PRECISION, lowest_precision_encountered);
				}
			} else {
				kernel.setValue(IfcGeom::Kernel::GV_PRECISION, 1.e-5);
			}

            if (representations->size() == 0) {
                Logger::Message(Logger::LOG_ERROR, "No geometries found");
                return false;
            }

			representation_iterator = representations->begin();
			ifcproducts.reset();

			if (!create()) {
				return false;
			}

			done = 0;
			total = representations->size();

            for (int i = 1; i < 4; ++i) {
                bounds_min_.SetCoord(i, std::numeric_limits<double>::infinity());
                bounds_max_.SetCoord(i, -std::numeric_limits<double>::infinity());
            }

            IfcSchema::IfcProduct::list::ptr products = ifc_file->entitiesByType<IfcSchema::IfcProduct>();
            for (IfcSchema::IfcProduct::list::it iter = products->begin(); iter != products->end(); ++iter) {
                IfcSchema::IfcProduct* product = *iter;
                if (product->hasObjectPlacement()) {
					// Use a fresh trsf every time in order to prevent the result to be concatenated
                    gp_Trsf trsf; 
					bool success = false;
					
					try {
						success = kernel.convert(product->ObjectPlacement(), trsf);
					} catch (const std::exception& e) {
						Logger::Error(e);
					} catch (...) {
						Logger::Error("Failed to construct placement");
					}
					
					if (!success) {
						continue;
					}

                    const gp_XYZ& pos = trsf.TranslationPart();
                    bounds_min_.SetX(std::min(bounds_min_.X(), pos.X()));
                    bounds_min_.SetY(std::min(bounds_min_.Y(), pos.Y()));
                    bounds_min_.SetZ(std::min(bounds_min_.Z(), pos.Z()));
                    bounds_max_.SetX(std::max(bounds_max_.X(), pos.X()));
                    bounds_max_.SetY(std::max(bounds_max_.Y(), pos.Y()));
                    bounds_max_.SetZ(std::max(bounds_max_.Z(), pos.Z()));
                }
            }

			return true;
		}

		int progress() const { return 100 * done / total; }

		const std::string& getUnitName() const { return unit_name; }

        /// @note Double always as per IFC specification.
        double getUnitMagnitude() const { return unit_magnitude; }
	
		std::string getLog() const { return Logger::GetLog(); }

		IfcParse::IfcFile* getFile() const { return ifc_file; }

        const std::vector<IfcGeom::filter_t>& filters() const { return filters_; }
        std::vector<IfcGeom::filter_t>& filters() { return filters_; }

        const gp_XYZ& bounds_min() const { return bounds_min_; }
        const gp_XYZ& bounds_max() const { return bounds_max_; }

	private:
		// Move to the next IfcRepresentation
		void _nextShape() {
			// In order to conserve memory and reduce cache insertion times, the cache is
			// cleared after an arbitary number of processed representations. This has been
			// benchmarked extensively: https://github.com/IfcOpenShell/IfcOpenShell/pull/47
			static const int clear_interval = 64;
			if (done % clear_interval == clear_interval - 1) {
				kernel.purge_cache();
			}
			ifcproducts.reset();
			++ representation_iterator;
			++ done;
		}

		std::set<IfcSchema::IfcRepresentation*> mapped_representations_processed;

		bool geometry_reuse_ok_for_current_representation_;

		BRepElement<P>* create_shape_model_for_next_entity() {
			for (;;) {
				IfcSchema::IfcRepresentation* representation;

				// Have we reached the end of our list of representations?
				if ( representation_iterator == representations->end() ) {
					representations.reset();
					return 0;
				}
				representation = *representation_iterator;

				// Has the list of IfcProducts for this representation been initialized?
				if (!ifcproducts) {
					
					ifcproducts = IfcSchema::IfcProduct::list::ptr(new IfcSchema::IfcProduct::list);
					IfcSchema::IfcProduct::list::ptr unfiltered_products(new IfcSchema::IfcProduct::list);

					{
						IfcSchema::IfcProductRepresentation::list::ptr prodreps = representation->OfProductRepresentation();

						for (IfcSchema::IfcProductRepresentation::list::it it = prodreps->begin(); it != prodreps->end(); ++it) {
							if ((*it)->is(IfcSchema::Type::IfcProductDefinitionShape)) {
								IfcSchema::IfcProductDefinitionShape* pds = (IfcSchema::IfcProductDefinitionShape*)*it;
								unfiltered_products->push(pds->ShapeOfProduct());
							}
							else {
								// http://buildingsmart-tech.org/ifc/IFC2x3/TC1/html/ifcrepresentationresource/lexical/ifcproductrepresentation.htm
								// IFC2x Edition 3 NOTE  Users should not instantiate the entity IfcProductRepresentation from IFC2x Edition 3 onwards. 
								// It will be changed into an ABSTRACT supertype in future releases of IFC.

								// IfcProductRepresentation also lacks the INVERSE relation to IfcProduct
								// Let's find the IfcProducts that reference the IfcProductRepresentation anyway
								unfiltered_products->push((*it)->entity->getInverse(IfcSchema::Type::IfcProduct, -1)->as<IfcSchema::IfcProduct>());
							}
						}
					}

					bool has_openings = false;
					bool has_layers = false;

					for (IfcSchema::IfcProduct::list::it it = unfiltered_products->begin(); it != unfiltered_products->end(); ++it) {
						if (kernel.find_openings(*it)->size()) {
							has_openings = true;
						}
						IfcSchema::IfcRelAssociates::list::ptr associations = (*it)->HasAssociations();
						for (IfcSchema::IfcRelAssociates::list::it jt = associations->begin(); jt != associations->end(); ++jt) {
							IfcSchema::IfcRelAssociatesMaterial* assoc = (*jt)->as<IfcSchema::IfcRelAssociatesMaterial>();
							if (assoc) {
								if (assoc->RelatingMaterial()->is(IfcSchema::Type::IfcMaterialLayerSetUsage)) {
									has_layers = true;
								}
							}
						}
					}
					
					// With world coords enabled, object transformations are directly applied to
					// the BRep. There is no way to re-use the geometry for multiple products.
					geometry_reuse_ok_for_current_representation_ = !settings.get(IteratorSettings::USE_WORLD_COORDS) &&
						(!has_openings || settings.get(IteratorSettings::DISABLE_OPENING_SUBTRACTIONS)) &&
						(!has_layers || !settings.get(IteratorSettings::APPLY_LAYERSETS));
					bool representation_processed_as_mapped_item = false;

					IfcSchema::IfcRepresentation* representation_mapped_to = 0;
					
					if (geometry_reuse_ok_for_current_representation_) {
						IfcSchema::IfcRepresentationItem::list::ptr items = representation->Items();
						if (items->size() == 1) {
							IfcSchema::IfcRepresentationItem* item = *items->begin();
							if (item->is(IfcSchema::Type::IfcMappedItem)) {
								if (item->StyledByItem()->size() == 0) {
									IfcSchema::IfcMappedItem* mapped_item = item->as<IfcSchema::IfcMappedItem>();
									if (kernel.is_identity_transform(mapped_item->MappingTarget())) {
										IfcSchema::IfcRepresentationMap* map = mapped_item->MappingSource();
										if (kernel.is_identity_transform(map->MappingOrigin())) {
											representation_mapped_to = map->MappedRepresentation();
											IfcSchema::IfcProductRepresentation::list::ptr prodreps = representation_mapped_to->OfProductRepresentation();

											bool all_product_without_openings = true;
											IfcSchema::IfcProduct::list::ptr products(new IfcSchema::IfcProduct::list);

											for (IfcSchema::IfcProductRepresentation::list::it it = prodreps->begin(); it != prodreps->end(); ++it) {
												IfcSchema::IfcProduct::list::ptr products_of_prodrep = (*it)->entity->getInverse(IfcSchema::Type::IfcProduct, -1)->as<IfcSchema::IfcProduct>();
												products->push(products_of_prodrep);
												for (IfcSchema::IfcProduct::list::it jt = products_of_prodrep->begin(); jt != products_of_prodrep->end(); ++jt) {
													if (kernel.find_openings(*jt)->size() > 0 && !settings.get(IteratorSettings::DISABLE_OPENING_SUBTRACTIONS)) {
														all_product_without_openings = false;
														break;
													}
												}
											}

											if (all_product_without_openings) {
												representation_processed_as_mapped_item = true;
											}
										}
									}
								}
							}
						}
					}

					if (representation_mapped_to) {
						if (mapped_representations_processed.find(representation_mapped_to) != mapped_representations_processed.end()) {
							_nextShape();
							continue;
						}

						mapped_representations_processed.insert(representation_mapped_to);
					}

					if (representation_processed_as_mapped_item) {
						_nextShape();
						continue;
					}

					IfcSchema::IfcRepresentationMap::list::ptr maps = representation->RepresentationMap();
					
					if (geometry_reuse_ok_for_current_representation_ && maps->size() == 1) {
						IfcSchema::IfcRepresentationMap* map = *maps->begin();
						if (kernel.is_identity_transform(map->MappingOrigin())) {
							IfcSchema::IfcMappedItem::list::ptr items = map->MapUsage();
							for (IfcSchema::IfcMappedItem::list::it it = items->begin(); it != items->end(); ++it) {
								IfcSchema::IfcMappedItem* item = *it;
								if (item->StyledByItem()->size() != 0) continue;
								
								if (!kernel.is_identity_transform(item->MappingTarget())) {
									continue;
								}

								IfcSchema::IfcRepresentation::list::ptr reps = item->entity->getInverse(IfcSchema::Type::IfcRepresentation, -1)->as<IfcSchema::IfcRepresentation>();
								for (IfcSchema::IfcRepresentation::list::it jt = reps->begin(); jt != reps->end(); ++jt) {
									IfcSchema::IfcRepresentation* rep = *jt;
									if (rep->Items()->size() != 1) continue;
									IfcSchema::IfcProductRepresentation::list::ptr prodreps = rep->OfProductRepresentation();
									for (IfcSchema::IfcProductRepresentation::list::it kt = prodreps->begin(); kt != prodreps->end(); ++kt) {
										IfcSchema::IfcProduct::list::ptr prods = (*kt)->entity->getInverse(IfcSchema::Type::IfcProduct, -1)->as<IfcSchema::IfcProduct>();
										for (IfcSchema::IfcProduct::list::it lt = prods->begin(); lt != prods->end(); ++lt) {
											if (kernel.find_openings(*lt)->size() == 0 || settings.get(IteratorSettings::DISABLE_OPENING_SUBTRACTIONS)) {
                                                if (!unfiltered_products->contains(*lt)) {
                                                    unfiltered_products->push(*lt);
                                                }
											}
										}
									}
								}
							}
						}
					}

                    // Filter the products based on the set of entities and/or names being included or excluded for processing.
                    for (IfcSchema::IfcProduct::list::it jt = unfiltered_products->begin(); jt != unfiltered_products->end(); ++jt) {
                        IfcSchema::IfcProduct* prod = *jt;
                        if (boost::all(filters_, filter_match(prod))) {
                            ifcproducts->push(prod);
                        }
                    }

					ifcproduct_iterator = ifcproducts->begin();
				}

				// Have we reached the end of our list of IfcProducts?
				if ( ifcproduct_iterator == ifcproducts->end() ) {
					_nextShape();
					continue;
				}

				IfcSchema::IfcProduct* product = *ifcproduct_iterator;

                Logger::SetProduct(product);

				BRepElement<P>* element;
				if (ifcproduct_iterator == ifcproducts->begin() || !geometry_reuse_ok_for_current_representation_) {
					element = kernel.create_brep_for_representation_and_product<P>(settings, representation, product);
				} else {
					element = kernel.create_brep_for_processed_representation(settings, representation, product, current_shape_model);
				}

				Logger::SetProduct(boost::none);

				if (!element) {
					_nextShape();
					continue;
				}

				return element;
			}
		}

		void free_shapes() {
			// Free all possible representations of the current geometrical entity
			delete current_triangulation;
			current_triangulation = 0;
			delete current_serialization;
			current_serialization = 0;
			delete current_shape_model;
			current_shape_model = 0;
		}

    public:
        /// Returns what would be the product for the next shape representation
        /// @todo Double-check and test the impl.
        //IfcSchema::IfcProduct* peek_next() const
        //{
        //    if (ifcproducts && ifcproduct_iterator + 1 != ifcproducts->end()){
        //        return *(ifcproduct_iterator + 1);
        //    } else {
        //        return 0;
        //    }
        //}

        /// @todo Would this be as simple as the following code?
        //void skip_next() { if (ifcproducts) { ++ifcproduct_iterator; } }

        /// Moves to the next shape representation, create its geometry, and returns the associated product.
        /// Use get() to retrieve the created geometry.
		IfcSchema::IfcProduct* next() {
			// Increment the iterator over the list of products using the current
			// shape representation
			if (ifcproducts) {
				++ifcproduct_iterator;
			}

			return create();
		}

        /// Gets the representation of the current geometrical entity.
        Element<P>* get()
        {
            // TODO: Test settings and throw
            Element<P>* ret = 0;
            if (current_triangulation) { ret = current_triangulation; }
            else if (current_serialization) { ret = current_serialization; }
            else if (current_shape_model) { ret = current_shape_model; }

			// If we want to organize the element considering their hierarchy
			if (settings.get(IteratorSettings::SEARCH_FLOOR))
			{
				// We are going to build a vector with the element parents.
				// First, create the parent vector
				std::vector<const IfcGeom::Element<P>*> parents;
				
				// if the element has a parent
				if (ret->parent_id() != -1)
				{
					const IfcGeom::Element<P>* parent_object = NULL;
					bool hasParent = true;

					// get the parent 
					try {
						parent_object = getObject(ret->parent_id());
					} catch (const std::exception& e) {
						Logger::Error(e);
						hasParent = false;
					}

					// Add the previously found parent to the vector
					if (hasParent) parents.insert(parents.begin(), parent_object);
					
					// We need to find all the parents
					while (parent_object != NULL && hasParent && parent_object->parent_id() != -1)
					{
						// Find the next parent
						try {
							parent_object = getObject(parent_object->parent_id());
						} catch (const std::exception& e) {
							Logger::Error(e);
							hasParent = false;
						}

						// Add the previously found parent to the vector
						if (hasParent) parents.insert(parents.begin(), parent_object);

						hasParent = hasParent && parent_object->parent_id() != -1;
					}

					// when done push the parent list in the Element object
					ret->SetParents(parents);
				}
			}

            return ret;
        }

		/// Gets the native (Open Cascade) representation of the current geometrical entity.
		BRepElement<P>* get_native()
		{
			// TODO: Test settings and throw
			return current_shape_model;
		}

		const Element<P>* getObject(int id) {
			gp_Trsf trsf;
			int parent_id = -1;
			std::string instance_type, product_name, product_guid;
            IfcSchema::IfcProduct* ifc_product = 0;

			try {
				IfcUtil::IfcBaseClass* ifc_entity = ifc_file->entityById(id);
				instance_type = IfcSchema::Type::ToString(ifc_entity->type());

				if (ifc_entity->is(IfcSchema::Type::IfcRoot)) {
					IfcSchema::IfcRoot* ifc_root = ifc_entity->as<IfcSchema::IfcRoot>();
					product_guid = ifc_root->GlobalId();
					product_name = ifc_root->hasName() ? ifc_root->Name() : "";
				}

				if (ifc_entity->is(IfcSchema::Type::IfcProduct)) {
					ifc_product = ifc_entity->as<IfcSchema::IfcProduct>();
					parent_id = -1;
					try {
						IfcSchema::IfcObjectDefinition* parent_object = kernel.get_decomposing_entity(ifc_product);
						if (parent_object) {
							parent_id = parent_object->entity->id();
						}
					} catch (const std::exception& e) {
						Logger::Error(e);
					} catch (...) {
						Logger::Error("Failed to find decomposing entity");
					}

					try {
						kernel.convert(ifc_product->ObjectPlacement(), trsf);
					} catch (const std::exception& e) {
						Logger::Error(e);
					} catch (...) {
						Logger::Error("Failed to construct placement");
					}
				}
			} catch (const std::exception& e) {
				Logger::Error(e);
			} catch (const Standard_Failure& e) {
				if (e.GetMessageString() && strlen(e.GetMessageString())) {
					Logger::Error(e.GetMessageString());
				} else {
					Logger::Error("Unknown error returning product");
				}
			} catch (...) {
				Logger::Error("Unknown error returning product");
			}

			ElementSettings element_settings(settings, unit_magnitude, instance_type);

			Element<P>* ifc_object = new Element<P>(element_settings, id, parent_id, product_name, instance_type, product_guid, "", trsf, ifc_product);
			return ifc_object;
		}

		IfcSchema::IfcProduct* create() {
			IfcGeom::BRepElement<P>* next_shape_model = 0;
			IfcGeom::SerializedElement<P>* next_serialization = 0;
			IfcGeom::TriangulationElement<P>* next_triangulation = 0;

			try {
				next_shape_model = create_shape_model_for_next_entity();
			} catch (const std::exception& e) {
				Logger::Error(e);
			} catch (const Standard_Failure& e) {
				if (e.GetMessageString() && strlen(e.GetMessageString())) {
					Logger::Error(e.GetMessageString());
				} else {
					Logger::Error("Unknown error creating geometry");
				}
			} catch (...) {
				Logger::Error("Unknown error creating geometry");
			}

			if (next_shape_model) {
				if (settings.get(IteratorSettings::USE_BREP_DATA)) {
					try {
						next_serialization = new SerializedElement<P>(*next_shape_model);
					} catch (...) {
                        Logger::Message(Logger::LOG_ERROR, "Getting a serialized element from model failed.");
					}
				} else if (!settings.get(IteratorSettings::DISABLE_TRIANGULATION)) {
					try {
						if (ifcproduct_iterator == ifcproducts->begin() || !geometry_reuse_ok_for_current_representation_) {
							next_triangulation = new TriangulationElement<P>(*next_shape_model);
						} else {
							next_triangulation = new TriangulationElement<P>(*next_shape_model, current_triangulation->geometry_pointer());
						}
					} catch (...) {
                        Logger::Message(Logger::LOG_ERROR, "Getting a triangulation element from model failed.");
					}
				}
			}

			free_shapes();

			current_shape_model = next_shape_model;
			current_serialization = next_serialization;
			current_triangulation = next_triangulation;

            return next_shape_model ? next_shape_model->product() : 0;
		}
	private:
		void _initialize() {
			current_triangulation = 0;
			current_shape_model = 0;
			current_serialization = 0;

			unit_name = "METER";
			unit_magnitude = 1.f;

            kernel.setValue(IfcGeom::Kernel::GV_MAX_FACES_TO_SEW, settings.get(IteratorSettings::SEW_SHELLS) ? 1000 : -1);
            kernel.setValue(IfcGeom::Kernel::GV_DIMENSIONALITY, (settings.get(IteratorSettings::INCLUDE_CURVES)
                ? (settings.get(IteratorSettings::EXCLUDE_SOLIDS_AND_SURFACES) ? -1. : 0.) : +1.));
			if (settings.get(IteratorSettings::SITE_LOCAL_PLACEMENT)) {
				kernel.set_conversion_placement_rel_to(IfcSchema::Type::IfcSite);
			}
		}

		bool owns_ifc_file;
	public:
		Iterator(const IteratorSettings& settings, IfcParse::IfcFile* file)
			: settings(settings)
			, ifc_file(file)
			, owns_ifc_file(false)
		{
			_initialize();
		}
		Iterator(const IteratorSettings& settings, const std::string& filename)
			: settings(settings)
			, ifc_file(new IfcParse::IfcFile)
			, owns_ifc_file(true)
		{
			ifc_file->Init(filename);
			_initialize();
		}
		Iterator(const IteratorSettings& settings, void* data, int length)
			: settings(settings)
			, ifc_file(new IfcParse::IfcFile)
			, owns_ifc_file(true)
		{
			ifc_file->Init(data, length);
			_initialize();
		}
		Iterator(const IteratorSettings& settings, std::istream& filestream, int length)
			: settings(settings)
			, ifc_file(new IfcParse::IfcFile)
			, owns_ifc_file(true)
		{
			ifc_file->Init(filestream, length);
			_initialize();
		}

		~Iterator() {
			if (owns_ifc_file) {
				delete ifc_file;
			}

			free_shapes();
		}
	};
}

#endif
