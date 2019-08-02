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
#include <atomic>

#include <future>
#include <thread>
#include <chrono>

#include <boost/algorithm/string.hpp>

#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>

#include "../../ifcparse/macros.h"
#include "../../ifcparse/IfcFile.h"

#include "../../ifcgeom/schema_agnostic/IfcGeomElement.h"
#include "../../ifcgeom/schema_agnostic/IfcGeomMaterial.h"
#include "../../ifcgeom/schema_agnostic/IfcGeomIteratorSettings.h"
#include "../../ifcgeom/schema_agnostic/ConversionResult.h"

#include "../../ifcgeom/schema_agnostic/IfcGeomFilter.h"
#include "../../ifcgeom/schema_agnostic/IteratorImplementation.h"

#include "../../ifcgeom/kernel_agnostic/AbstractKernel.h"

#define INCLUDE_SCHEMA(x) STRINGIFY(../../ifcparse/x.h)
#include INCLUDE_SCHEMA(IfcSchema)
#undef INCLUDE_SCHEMA

#include <atomic>

// The infamous min & max Win32 #defines can leak here from OCE depending on the build configuration
#ifdef min
#undef min
#endif
#ifdef max
#undef max
#endif

namespace {
	template <typename P, typename PP=P>
	struct geometry_conversion_task {
		int index;
		IfcSchema::IfcRepresentation *representation;
		IfcSchema::IfcProduct::list::ptr products;
		std::vector<IfcGeom::NativeElement<P, PP>*> breps;
		std::vector<IfcGeom::Element<P, PP>*> elements;
	};

	template <typename P, typename PP=P>
	IfcGeom::Element<P, PP>* process_based_on_settings(
		const IfcGeom::IteratorSettings& settings,
		IfcGeom::NativeElement<P, PP>* elem, 
		IfcGeom::TriangulationElement<P, PP>* previous=nullptr)
	{
		if (settings.get(IfcGeom::IteratorSettings::USE_BREP_DATA)) {
			try {
				return new IfcGeom::SerializedElement<P, PP>(*elem);
			} catch (...) {
				Logger::Message(Logger::LOG_ERROR, "Getting a serialized element from model failed.");
				return nullptr;
			}
		} else if (!settings.get(IfcGeom::IteratorSettings::DISABLE_TRIANGULATION)) {
			try {
				if (!previous) {
					return  new IfcGeom::TriangulationElement<P, PP>(*elem);
				} else {
					return  new IfcGeom::TriangulationElement<P, PP>(*elem, previous->geometry_pointer());
				}
			} catch (...) {
				Logger::Message(Logger::LOG_ERROR, "Getting a triangulation element from model failed.");
				return nullptr;
			}
		} else {
			return elem;
		}
	}

	template <typename P, typename PP = P>
	void create_element(
		IfcGeom::MAKE_TYPE_NAME(AbstractKernel)* kernel, 
		const IfcGeom::IteratorSettings& settings,
		geometry_conversion_task<P, PP>* rep) 
	{
		IfcSchema::IfcRepresentation *representation = rep->representation;
		IfcSchema::IfcProduct *product = *rep->products->begin();
		auto brep = kernel->create_brep_for_representation_and_product<P, PP>(settings, representation, product);
		if (!brep) {
			return;
		}

		auto elem = process_based_on_settings(settings, brep);
		if (!elem) {
			return;
		}

		rep->breps = { brep };
		rep->elements = { elem };

		for (auto it = rep->products->begin() + 1; it != rep->products->end(); ++it) {
			auto brep2 = kernel->create_brep_for_processed_representation<P, PP>(settings, representation, *it, brep);
			if (brep2) {
				auto elem2 = process_based_on_settings(settings, brep, dynamic_cast<IfcGeom::TriangulationElement<P, PP>*>(elem));
				if (elem2) {
					rep->breps.push_back(brep2);
					rep->elements.push_back(elem2);
				}
			}
		}
	}
}

namespace IfcGeom {
	
	template <typename P, typename PP>
	class MAKE_TYPE_NAME(IteratorImplementation_) : public IteratorImplementation<P, PP> {
	private:

		int num_threads_;
		std::atomic<int> progress_;
		std::vector<geometry_conversion_task<P, PP>> tasks_;
		std::vector<IfcGeom::Element<P, PP>*> all_processed_elements_;
		std::vector<IfcGeom::NativeElement<P, PP>*> all_processed_native_elements_;
		typename std::vector<IfcGeom::Element<P, PP>*>::const_iterator task_result_iterator_;
		typename std::vector<IfcGeom::NativeElement<P, PP>*>::const_iterator native_task_result_iterator_;

		std::string geometry_library_;

		MAKE_TYPE_NAME(IteratorImplementation_)(const MAKE_TYPE_NAME(IteratorImplementation_)&); // N/I
		MAKE_TYPE_NAME(IteratorImplementation_)& operator=(const MAKE_TYPE_NAME(IteratorImplementation_)&); // N/I

		MAKE_TYPE_NAME(AbstractKernel)* kernel;
		IteratorSettings settings;

		IfcParse::IfcFile* ifc_file;

		// A container and iterator for IfcRepresentations
		IfcSchema::IfcRepresentation::list::ptr representations;
		IfcSchema::IfcRepresentation::list::it representation_iterator;

		// The object is fetched beforehand to be sure that get() returns a valid element
		TriangulationElement<P, PP>* current_triangulation;
		NativeElement<P, PP>* current_shape_model;
		SerializedElement<P, PP>* current_serialization;
		
		// A container and iterator for IfcBuildingElements for the current IfcRepresentation referenced by *representation_iterator
		IfcSchema::IfcProduct::list::ptr ifcproducts;
		IfcSchema::IfcProduct::list::it ifcproduct_iterator;


        IfcSchema::IfcRepresentation::list::ptr ok_mapped_representations;

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

        /// @todo public/private sections all over the place: move all public to the beginning of the class
	public:
		typedef P Precision;
		typedef PP PlacementPrecision;

		bool initialize() {

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

			representations = IfcSchema::IfcRepresentation::list::ptr(new IfcSchema::IfcRepresentation::list);
            ok_mapped_representations = IfcSchema::IfcRepresentation::list::ptr(new IfcSchema::IfcRepresentation::list);

			IfcSchema::IfcGeometricRepresentationContext::list::it it;
			IfcSchema::IfcGeometricRepresentationSubContext::list::it jt;
			IfcSchema::IfcGeometricRepresentationContext::list::ptr contexts = 
				ifc_file->instances_by_type<IfcSchema::IfcGeometricRepresentationContext>();

			IfcSchema::IfcGeometricRepresentationContext::list::ptr filtered_contexts (new IfcSchema::IfcGeometricRepresentationContext::list);

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
				representations = ifc_file->instances_by_type<IfcSchema::IfcRepresentation>();
            }

			if (representations->size() == 0) {
				Logger::Warning("No representations encountered, aborting");
				return false;
			}

			representation_iterator = representations->begin();
			ifcproducts.reset();

			done = 0;
			total = representations->size();

			if (num_threads_ != 1) {
				collect();
				process_concurrently();
			} else {
				if (!create()) {
					return false;
				}
			}
			
			return true;
		}

		void collect() {
			int i = 0;
			IfcSchema::IfcProduct::list* previous = nullptr;
			while (auto rp = get_next_task()) {
				// Note that get_next_task() mutates the state of the iterator
				// we use that capture all products that can be processed as
				// part of this representation and then keep iterating until
				// the underlying list of products changes.
				if (ifcproducts.get() != previous) {
					previous = ifcproducts.get();
					geometry_conversion_task<P, PP> t;
					t.index = i++;
					t.representation = *representation_iterator;
					t.products = ifcproducts;
					tasks_.emplace_back(t);
				}

				_nextShape();
			}
		}

		void process_concurrently() {
			size_t conc_threads = num_threads_;
			if (conc_threads > tasks_.size()) {
				conc_threads = tasks_.size();
			}
			
			std::vector<MAKE_TYPE_NAME(AbstractKernel)*> kernel_pool;
			kernel_pool.reserve(conc_threads);
			for (unsigned i = 0; i < conc_threads; ++i) {
				kernel_pool.push_back((MAKE_TYPE_NAME(AbstractKernel)*) impl::kernel_implementations().construct(ifc_file->schema()->name(), geometry_library_, ifc_file));
			}

			std::vector<std::future<void>> threadpool;

			int old_progress = -1;
			int processed = 0;

			Logger::ProgressBar(0);

			for (auto& rep : tasks_) {
				MAKE_TYPE_NAME(AbstractKernel)* K = nullptr;
				if (threadpool.size() < kernel_pool.size()) {
					K = kernel_pool[threadpool.size()];
				}

				while (threadpool.size() == conc_threads) {
					for (int i = 0; i < (int)threadpool.size(); i++) {
						std::future<void> &fu = threadpool[i];
						std::future_status status;
						status = fu.wait_for(std::chrono::seconds(0));
						if (status == std::future_status::ready) {
							fu.get();
							
							processed += 1;
							progress_ = processed * 50 / tasks_.size();
							if (progress_ != old_progress) {
								Logger::ProgressBar(progress_);
								old_progress = progress_;
							}
								
							std::swap(threadpool[i], threadpool.back());
							threadpool.pop_back();
							std::swap(kernel_pool[i], kernel_pool.back());
							K = kernel_pool.back();
							break;
						} // if
					}   // for
				}     // while

				std::future<void> fu = std::async(std::launch::async, create_element<P, PP>, K, std::ref(settings), &rep);
				threadpool.emplace_back(std::move(fu));
			}

			for (std::future<void> &fu : threadpool) {
				fu.get();

				processed += 1;
				progress_ = processed * 50 / tasks_.size();
				if (progress_ != old_progress) {
					Logger::ProgressBar(progress_);
					old_progress = progress_;
				}
			}

			for (auto& rep : tasks_) {
				all_processed_elements_.insert(all_processed_elements_.end(), rep.elements.begin(), rep.elements.end());
				all_processed_native_elements_.insert(all_processed_native_elements_.end(), rep.breps.begin(), rep.breps.end());
			}

			task_result_iterator_ = all_processed_elements_.begin();
			native_task_result_iterator_ = all_processed_native_elements_.begin();

			Logger::Status("\rDone creating geometry (" + boost::lexical_cast<std::string>(all_processed_elements_.size()) +
				" objects)                                ");
		}

        /// Computes model's bounding box (bounds_min and bounds_max).
        /// @note Can take several minutes for large files.
        void compute_bounds()
        {
            for (int i = 1; i < 4; ++i) {
                bounds_min_.SetCoord(i, std::numeric_limits<double>::infinity());
                bounds_max_.SetCoord(i, -std::numeric_limits<double>::infinity());
            }

            IfcSchema::IfcProduct::list::ptr products = ifc_file->instances_by_type<IfcSchema::IfcProduct>();
            for (IfcSchema::IfcProduct::list::it iter = products->begin(); iter != products->end(); ++iter) {
                IfcSchema::IfcProduct* product = *iter;
                if (product->hasObjectPlacement()) {
                    // Use a fresh trsf every time in order to prevent the result to be concatenated
                    ConversionResultPlacement* trsf; 
                    bool success = false;

                    try {
                        success = kernel->convert_placement(product->ObjectPlacement(), trsf);
                    } catch (const std::exception& e) {
                        Logger::Error(e);
                    } catch (...) {
                        Logger::Error("Failed to construct placement");
                    }

                    if (!success) {
                        continue;
                    }

					double X, Y, Z;
                    trsf->TranslationPart(X, Y, Z);
                    bounds_min_.SetX(std::min(bounds_min_.X(), X));
                    bounds_min_.SetY(std::min(bounds_min_.Y(), Y));
                    bounds_min_.SetZ(std::min(bounds_min_.Z(), Z));
                    bounds_max_.SetX(std::max(bounds_max_.X(), X));
                    bounds_max_.SetY(std::max(bounds_max_.Y(), Y));
                    bounds_max_.SetZ(std::max(bounds_max_.Z(), Z));
                }
            }
        }

		int progress() const { 
			if (num_threads_ == 1) {
				return 100 * done / total;
			} else {
				return progress_;
			}
		}

		const std::string& getUnitName() const { return unit_name; }

        /// @note Double always as per IFC specification.
        double getUnitMagnitude() const { return unit_magnitude; }
	
		std::string getLog() const { return Logger::GetLog(); }

		IfcParse::IfcFile* file() const { return ifc_file; }

        const std::vector<IfcGeom::filter_t>& filters() const { return filters_; }
        std::vector<IfcGeom::filter_t>& filters() { return filters_; }

        const gp_XYZ& bounds_min() const { return bounds_min_; }
        const gp_XYZ& bounds_max() const { return bounds_max_; }

	private:
		// Move to the next IfcRepresentation
		void _nextShape() {
			ifcproducts.reset();
			++ representation_iterator;
			++ done;
		}

		bool geometry_reuse_ok_for_current_representation_;

		bool reuse_ok_(const IfcSchema::IfcProduct::list::ptr& products) {
			// With world coords enabled, object transformations are directly applied to
			// the BRep. There is no way to re-use the geometry for multiple products.
			if (settings.get(IteratorSettings::USE_WORLD_COORDS)) {
				return false;
			}

			std::set<const IfcSchema::IfcMaterial*> associated_single_materials;

			for (IfcSchema::IfcProduct::list::it it = products->begin(); it != products->end(); ++it) {
				IfcSchema::IfcProduct* product = *it;

				if (!settings.get(IteratorSettings::DISABLE_OPENING_SUBTRACTIONS) && kernel->find_openings(product)->size()) {
					return false;
				}

				if (settings.get(IteratorSettings::APPLY_LAYERSETS)) {
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
				associated_single_materials.insert(kernel->get_single_material_association(product));
                if (associated_single_materials.size() > 1) return false;
			}

			return associated_single_materials.size() == 1;
		}

		boost::optional<std::pair<IfcSchema::IfcRepresentation*, IfcSchema::IfcProduct*>> get_next_task() {
			for (;;) {
				IfcSchema::IfcRepresentation* representation;

				if (representation_iterator == representations->end()) {
					representations.reset();
					return boost::none; // reached the end of our list of representations
				}
				representation = *representation_iterator;

				if (!ifcproducts) {
					// Init. the list of filtered IfcProducts for this representation
					ifcproducts = IfcSchema::IfcProduct::list::ptr(new IfcSchema::IfcProduct::list);
					IfcSchema::IfcProduct::list::ptr unfiltered_products = kernel->products_represented_by(representation);
                    // Include only the desired products for processing.
                    for (IfcSchema::IfcProduct::list::it jt = unfiltered_products->begin(); jt != unfiltered_products->end(); ++jt) {
                        IfcSchema::IfcProduct* prod = *jt;
                        if (boost::all(filters_, filter_match(prod))) {
                            ifcproducts->push(prod);
                        }
                    }

					if (ifcproducts->size() == 0) {
						_nextShape();
						continue;
					}

					geometry_reuse_ok_for_current_representation_ = reuse_ok_(ifcproducts);

					IfcSchema::IfcRepresentationMap::list::ptr maps = representation->RepresentationMap();

					if (!geometry_reuse_ok_for_current_representation_ && maps->size() == 1) {
						// unfiltered_products contains products represented by this representation by means of mapped items.
						// For example because of openings applied to products, reuse might not be acceptable and then the
						// products will be processed by means of their immediate representation and not the mapped representation.

						// IfcRepresentationMaps are also used for IfcTypeProducts, so an additional check is performed whether the map
						// is indeed used by IfcMappedItems.
						IfcSchema::IfcRepresentationMap* map = *maps->begin();
						if (map->MapUsage()->size() > 0) {
							_nextShape();
							continue;
						}
					}

					// Check if this represenation has (or will be) processed as part its mapped representation
					bool representation_processed_as_mapped_item = false;
                    IfcSchema::IfcRepresentation* representation_mapped_to = kernel->representation_mapped_to(representation);
					if (representation_mapped_to) {
                        representation_processed_as_mapped_item = geometry_reuse_ok_for_current_representation_ && (
                            ok_mapped_representations->contains(representation_mapped_to) || reuse_ok_(kernel->products_represented_by(representation_mapped_to)));
					}

					if (representation_processed_as_mapped_item) {
						ok_mapped_representations->push(representation_mapped_to);
						_nextShape();
						continue;
					}

					ifcproduct_iterator = ifcproducts->begin();
				}

				// Have we reached the end of our list of IfcProducts?
				if (ifcproduct_iterator == ifcproducts->end()) {
					_nextShape();
					continue;
				}

				IfcSchema::IfcProduct* product = *ifcproduct_iterator;


				return std::make_pair(representation, product);
			}
		}

		NativeElement<P, PP>* create_shape_model_for_next_entity() {
			for (;;) {
				auto rp = get_next_task();
				if (!rp) {
					return nullptr;
				}
				auto representation = rp->first;
				auto product = rp->second;

				Logger::SetProduct(product);

				NativeElement<P, PP>* element;
				if (ifcproduct_iterator == ifcproducts->begin() || !geometry_reuse_ok_for_current_representation_) {
					element = kernel->create_brep_for_representation_and_product<P, PP>(settings, representation, product);
				} else {
					element = kernel->create_brep_for_processed_representation(settings, representation, product, current_shape_model);
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
		IfcUtil::IfcBaseClass* next() {
			if (num_threads_ != 1) {
				task_result_iterator_++;
				native_task_result_iterator_++;
				if (task_result_iterator_ == all_processed_elements_.end()) {
					return nullptr;
				} else {
					return (*task_result_iterator_)->product();
				}
			} else {
				// Increment the iterator over the list of products using the current
				// shape representation
				if (ifcproducts) {
					++ifcproduct_iterator;
				}

				return create();
			}
		}

        /// Gets the representation of the current geometrical entity.
        Element<P, PP>* get()
        {
            // TODO: Test settings and throw
            Element<P, PP>* ret = 0;

			if (num_threads_ != 1) {
				ret = *task_result_iterator_;
			} else {
				if (current_triangulation) { 
					ret = current_triangulation; 
				} else if (current_serialization) { 
					ret = current_serialization; 
				} else if (current_shape_model) { 
					ret = current_shape_model; 
				}
			}

			// If we want to organize the element considering their hierarchy
			if (settings.get(IteratorSettings::SEARCH_FLOOR))
			{
				// We are going to build a vector with the element parents.
				// First, create the parent vector
				std::vector<const IfcGeom::Element<P, PP>*> parents;
				
				// if the element has a parent
				if (ret->parent_id() != -1)
				{
					const IfcGeom::Element<P, PP>* parent_object = NULL;
					bool hasParent = true;

					// get the parent 
					try {
						parent_object = get_object(ret->parent_id());
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
							parent_object = get_object(parent_object->parent_id());
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
		NativeElement<P, PP>* get_native()
		{
			// TODO: Test settings and throw
			if (num_threads_ != 1) {
				return *native_task_result_iterator_;
			} else {
				return current_shape_model;
			}
		}

		const Element<P, PP>* get_object(int id) {
			ConversionResultPlacement* trsf;
			int parent_id = -1;
			std::string instance_type, product_name, product_guid;
            IfcSchema::IfcProduct* ifc_product = 0;

			try {
				IfcUtil::IfcBaseClass* ifc_entity = ifc_file->instance_by_id(id);
				instance_type = ifc_entity->declaration().name();

				if (ifc_entity->declaration().is(IfcSchema::IfcRoot::Class())) {
					IfcSchema::IfcRoot* ifc_root = ifc_entity->as<IfcSchema::IfcRoot>();
					product_guid = ifc_root->GlobalId();
					product_name = ifc_root->hasName() ? ifc_root->Name() : "";
				}

				if (ifc_entity->declaration().is(IfcSchema::IfcProduct::Class())) {
					ifc_product = ifc_entity->as<IfcSchema::IfcProduct>();
					parent_id = -1;
					try {
						IfcSchema::IfcObjectDefinition* parent_object = kernel->get_decomposing_entity(ifc_product)->template as<IfcSchema::IfcObjectDefinition>();
						if (parent_object) {
							parent_id = parent_object->data().id();
						}
					} catch (const std::exception& e) {
						Logger::Error(e);
					} catch (...) {
						Logger::Error("Failed to find decomposing entity");
					}

					try {
						kernel->convert_placement(ifc_product->ObjectPlacement(), trsf);
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

			Element<P, PP>* ifc_object = new Element<P, PP>(element_settings, id, parent_id, product_name, instance_type, product_guid, "", trsf, ifc_product);
			return ifc_object;
		}

		IfcUtil::IfcBaseClass* create() {
			IfcGeom::NativeElement<P, PP>* next_shape_model = 0;
			IfcGeom::SerializedElement<P, PP>* next_serialization = 0;
			IfcGeom::TriangulationElement<P, PP>* next_triangulation = 0;

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
						next_serialization = new SerializedElement<P, PP>(*next_shape_model);
					} catch (...) {
                        Logger::Message(Logger::LOG_ERROR, "Getting a serialized element from model failed.");
					}
				} else if (!settings.get(IteratorSettings::DISABLE_TRIANGULATION)) {
					try {
						if (ifcproduct_iterator == ifcproducts->begin() || !geometry_reuse_ok_for_current_representation_) {
							next_triangulation = new TriangulationElement<P, PP>(*next_shape_model);
						} else {
							next_triangulation = new TriangulationElement<P, PP>(*next_shape_model, current_triangulation->geometry_pointer());
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

            kernel->setValue(IfcGeom::Kernel::GV_MAX_FACES_TO_ORIENT, settings.get(IteratorSettings::SEW_SHELLS) ? std::numeric_limits<double>::infinity() : -1);
            kernel->setValue(IfcGeom::Kernel::GV_DIMENSIONALITY, (settings.get(IteratorSettings::INCLUDE_CURVES)
                ? (settings.get(IteratorSettings::EXCLUDE_SOLIDS_AND_SURFACES) ? -1. : 0.) : +1.));
			if (settings.get(IteratorSettings::BUILDING_LOCAL_PLACEMENT)) {
				if (settings.get(IteratorSettings::SITE_LOCAL_PLACEMENT)) {
					Logger::Message(Logger::LOG_WARNING, "building-local-placement takes precedence over site-local-placement");
				}
				kernel->set_conversion_placement_rel_to(&IfcSchema::IfcBuilding::Class());
			} else if (settings.get(IteratorSettings::SITE_LOCAL_PLACEMENT)) {
				kernel->set_conversion_placement_rel_to(&IfcSchema::IfcSite::Class());
			}
		}

		bool owns_ifc_file;
	public:
		MAKE_TYPE_NAME(IteratorImplementation_)(const std::string& geometry_library, const IteratorSettings& settings, IfcParse::IfcFile* file, const std::vector<IfcGeom::filter_t>& filters, int num_threads)
			: settings(settings)
			, ifc_file(file)
			, filters_(filters)
			, owns_ifc_file(false)
			, num_threads_(num_threads)
			, geometry_library_(geometry_library)
		{
			kernel = (MAKE_TYPE_NAME(AbstractKernel)*) impl::kernel_implementations().construct(file->schema()->name(), geometry_library, file);
			// kernel = new Kernel(geometry_library, file);
			_initialize();
		}

		~MAKE_TYPE_NAME(IteratorImplementation_)() {
			if (owns_ifc_file) {
				delete ifc_file;
			}

			if (settings.get(IfcGeom::IteratorSettings::DISABLE_TRIANGULATION)) {
				for (auto& p : all_processed_native_elements_) {
					delete p;
				}
			}

			for (auto& p : all_processed_elements_) {
				delete p;
			}

			free_shapes();
		}
	};
}

#endif
