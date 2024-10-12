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

#include "../ifcparse/IfcFile.h"

#include "../ifcgeom/IfcGeom.h"

#include "../ifcgeom_schema_agnostic/IfcGeomElement.h"
#include "../ifcgeom_schema_agnostic/IfcGeomMaterial.h"
#include "../ifcgeom_schema_agnostic/IfcGeomIteratorSettings.h"
#include "../ifcgeom_schema_agnostic/IfcRepresentationShapeItem.h"
#include "../ifcgeom_schema_agnostic/IfcGeomFilter.h"
#include "../ifcgeom_schema_agnostic/IteratorImplementation.h"

#include <atomic>

// The infamous min & max Win32 #defines can leak here from OCE depending on the build configuration
#ifdef min
#undef min
#endif
#ifdef max
#undef max
#endif

namespace {
	struct geometry_conversion_task {
		int index;
		IfcSchema::IfcRepresentation *representation;
		IfcSchema::IfcProduct::list::ptr products;
		std::vector<IfcGeom::BRepElement*> breps;
		std::vector<IfcGeom::Element*> elements;
	};
}

namespace IfcGeom {

	class MAKE_TYPE_NAME(IteratorImplementation_) : public IteratorImplementation {
	private:

		std::atomic<bool> finished_{ false };
		std::atomic<bool> terminating_{ false };
		std::atomic<int> progress_{ 0 };

		std::vector<geometry_conversion_task> tasks_;

		std::list<IfcGeom::Element*> all_processed_elements_;
		std::list<IfcGeom::BRepElement*> all_processed_native_elements_;

		typename std::list<IfcGeom::Element*>::const_iterator task_result_iterator_;
		typename std::list<IfcGeom::BRepElement*>::const_iterator native_task_result_iterator_;

		std::mutex element_ready_mutex_;
		bool task_result_ptr_initialized = false;
		size_t async_elements_returned_ = 0;
		
		MAKE_TYPE_NAME(IteratorImplementation_)(const MAKE_TYPE_NAME(IteratorImplementation_)&); // N/I
		MAKE_TYPE_NAME(IteratorImplementation_)& operator=(const MAKE_TYPE_NAME(IteratorImplementation_)&); // N/I

		// When single-threaded
		MAKE_TYPE_NAME(Kernel) kernel;

		// When multi-threaded
		std::vector<MAKE_TYPE_NAME(Kernel)*> kernel_pool;

		IteratorSettings settings;
		IfcParse::IfcFile* ifc_file;
		std::vector<filter_t> filters_;
		bool owns_ifc_file;
		int num_threads_;

		// A container and iterator for IfcRepresentations
		IfcSchema::IfcRepresentation::list::ptr representations;
		IfcSchema::IfcRepresentation::list::it representation_iterator;

		// The object is fetched beforehand to be sure that get() returns a valid element
		TriangulationElement* current_triangulation;
		BRepElement* current_shape_model;
		SerializedElement* current_serialization;

		// A container and iterator for IfcBuildingElements for the current IfcRepresentation referenced by *representation_iterator
		IfcSchema::IfcProduct::list::ptr ifcproducts;
		IfcSchema::IfcProduct::list::it ifcproduct_iterator;


		double lowest_precision_encountered;
		bool any_precision_encountered;

		int done;
		int total;

		std::string unit_name;
		double unit_magnitude;

        gp_XYZ bounds_min_;
        gp_XYZ bounds_max_;

        struct filter_match
        {
            filter_match(IfcSchema::IfcProduct *prod) : product(prod) {}
            bool operator()(const filter_t& filter) const { return filter(product);  }

            IfcSchema::IfcProduct* product;
        };

		void initUnits() {
			IfcSchema::IfcProject::list::ptr projects = ifc_file->instances_by_type<IfcSchema::IfcProject>();
			if (projects->size() == 1) {
				IfcSchema::IfcProject* project = *projects->begin();
				std::pair<std::string, double> length_unit = kernel.initializeUnits(project->UnitsInContext());
				unit_name = length_unit.first;
				unit_magnitude = length_unit.second;
			} else {
				Logger::Warning("A single IfcProject is expected (encountered " + boost::lexical_cast<std::string>(projects->size()) + "); unable to read unit information.");
			}
		}

        /// @todo public/private sections all over the place: move all public to the beginning of the class
	public:

		boost::optional<bool> initialization_outcome_;

		// Should not be destructed because, destructor is blocking
		std::future<void> init_future_;

		bool initialize() {
			if (initialization_outcome_) {
				return *initialization_outcome_;
			}

			try {
				initUnits();
			} catch (const std::exception& e) {
				Logger::Error(e);
			}

			representations = IfcSchema::IfcRepresentation::list::ptr(new IfcSchema::IfcRepresentation::list);
			lowest_precision_encountered = std::numeric_limits<double>::infinity();
			any_precision_encountered = false;

			if (settings.context_ids().size() != 0) {
				addRepresentationsFromContextIds();
			} else {
				addRepresentationsFromDefaultContexts();
			}

			if (any_precision_encountered) {
				// Some arbitrary factor that has proven to work better for the models in the set of test files.
				lowest_precision_encountered *= kernel.getValue(IfcGeom::Kernel::GV_PRECISION_FACTOR);

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
				Logger::Warning("No representations encountered, aborting");
				initialization_outcome_ = false;
			} else {
				representation_iterator = representations->begin();
				ifcproducts.reset();

				done = 0;
				total = representations->size();

				if (num_threads_ != 1) {
					collect();

					init_future_ = std::async(std::launch::async, [this]() { process_concurrently(); });

					// wait for the first element, because after init(), get() can be called.
					// so the element conversion must succeed
					initialization_outcome_ = wait_for_element();
				} else {
					initialization_outcome_ = create();
				}
			}

			return *initialization_outcome_;
		}

		void collect() {
			int i = 0;
			IfcSchema::IfcProduct::list* previous = nullptr;
			while (auto rp = try_get_next_task()) {
				// Note that get_next_task() mutates the state of the iterator
				// we use that capture all products that can be processed as
				// part of this representation and then keep iterating until
				// the underlying list of products changes.
				if (ifcproducts.get() != previous) {
					previous = ifcproducts.get();
					if (ifcproducts->size()) {
						geometry_conversion_task t;
						t.index = i++;
						t.representation = *representation_iterator;
						t.products = ifcproducts;
						tasks_.emplace_back(t);
					}
				}

				if (rp->which() == 1) {
					Logger::Error(boost::get<IfcParse::IfcException>(*rp));
				}

				_nextShape();
			}
		}

		size_t processed_ = 0;

		void process_finished_rep(geometry_conversion_task* rep) {
			if (rep->elements.empty()) {
				return;
			}

			std::lock_guard<std::mutex> lk(element_ready_mutex_);

			all_processed_elements_.insert(all_processed_elements_.end(), rep->elements.begin(), rep->elements.end());
			all_processed_native_elements_.insert(all_processed_native_elements_.end(), rep->breps.begin(), rep->breps.end());

			if (!task_result_ptr_initialized) {
				task_result_iterator_ = all_processed_elements_.begin();
				native_task_result_iterator_ = all_processed_native_elements_.begin();
				task_result_ptr_initialized = true;
			}

			progress_ = (int) (++processed_ * 100 / tasks_.size());
		}

		void process_concurrently() {
			size_t conc_threads = num_threads_;
			if (conc_threads > tasks_.size()) {
				conc_threads = tasks_.size();
			}

			kernel_pool.reserve(conc_threads);
			for (unsigned i = 0; i < conc_threads; ++i) {
				kernel_pool.push_back(new MAKE_TYPE_NAME(Kernel)(kernel));
			}

			std::vector<std::future<geometry_conversion_task*>> threadpool;			
			
			for (auto& rep : tasks_) {
				MAKE_TYPE_NAME(Kernel)* K = nullptr;
				if (threadpool.size() < kernel_pool.size()) {
					K = kernel_pool[threadpool.size()];
				}

				while (threadpool.size() == conc_threads) {
					for (int i = 0; i < (int)threadpool.size(); i++) {
						auto& fu = threadpool[i];
						std::future_status status;
						status = fu.wait_for(std::chrono::seconds(0));
						if (status == std::future_status::ready) {
							process_finished_rep(fu.get());							

							std::swap(threadpool[i], threadpool.back());
							threadpool.pop_back();
							std::swap(kernel_pool[i], kernel_pool.back());
							K = kernel_pool.back();
							break;
						} // if
					}   // for
				}     // while

				std::future<geometry_conversion_task*> fu = std::async(
					std::launch::async, [this](
						IfcGeom::MAKE_TYPE_NAME(Kernel)* kernel,
						const IfcGeom::IteratorSettings& settings,
						geometry_conversion_task* rep) {
							this->create_element_(kernel, settings, rep); 
							return rep;
						},
					K,
					std::ref(settings),
					&rep);

				if (terminating_) {
					break;
				}

				threadpool.emplace_back(std::move(fu));
			}

			for (auto& fu : threadpool) {
				process_finished_rep(fu.get());
			}

			finished_ = true;

			if (!terminating_) {
				Logger::Status("\rDone creating geometry (" + boost::lexical_cast<std::string>(all_processed_elements_.size()) +
					" objects)                                ");
			}
		}

        /// Computes model's bounding box (bounds_min and bounds_max).
        /// @note Can take several minutes for large files.
        void compute_bounds(bool with_geometry)
        {
            for (int i = 1; i < 4; ++i) {
                bounds_min_.SetCoord(i, std::numeric_limits<double>::infinity());
                bounds_max_.SetCoord(i, -std::numeric_limits<double>::infinity());
            }

			if (with_geometry) {
				size_t num_created = 0;
				do {
					IfcGeom::Element* geom_object = get();
					const IfcGeom::TriangulationElement* o = static_cast<const IfcGeom::TriangulationElement*>(geom_object);
					const IfcGeom::Representation::Triangulation& mesh = o->geometry();
					const gp_XYZ& pos = o->transformation().data().TranslationPart();

					for (typename std::vector<double>::const_iterator it = mesh.verts().begin(); it != mesh.verts().end();) {
						const double& x = *(it++);
						const double& y = *(it++);
						const double& z = *(it++);

						bounds_min_.SetX(std::min(bounds_min_.X(), pos.X() + x));
						bounds_min_.SetY(std::min(bounds_min_.Y(), pos.Y() + y));
						bounds_min_.SetZ(std::min(bounds_min_.Z(), pos.Z() + z));
						bounds_max_.SetX(std::max(bounds_max_.X(), pos.X() + x));
						bounds_max_.SetY(std::max(bounds_max_.Y(), pos.Y() + y));
						bounds_max_.SetZ(std::max(bounds_max_.Z(), pos.Z() + z));
					}
				} while (++num_created, next());
			} else {
				IfcSchema::IfcProduct::list::ptr products = ifc_file->instances_by_type<IfcSchema::IfcProduct>();
				for (IfcSchema::IfcProduct::list::it iter = products->begin(); iter != products->end(); ++iter) {
					IfcSchema::IfcProduct* product = *iter;
					if (product->ObjectPlacement()) {
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
		void addRepresentationsFromContextIds() {
			for (auto context_id : settings.context_ids()) {
				IfcSchema::IfcGeometricRepresentationContext* context = ifc_file->instance_by_id(context_id)->as<IfcSchema::IfcGeometricRepresentationContext>();

				if (!context) {
					Logger::Error("Failed to process context ID " + std::to_string(context_id));
					continue;
				}

				representations->push(context->RepresentationsInContext());

				try {
					double precision;

					if (context->as<IfcSchema::IfcGeometricRepresentationSubContext>()) {
						precision = *context->as<IfcSchema::IfcGeometricRepresentationSubContext>()->ParentContext()->Precision();
					} else {
						precision = *context->Precision();
					}

					if (precision && precision < lowest_precision_encountered) {
						lowest_precision_encountered = precision;
						any_precision_encountered = true;
					}
				} catch (const std::exception& e) {
					Logger::Error(e);
				}
			}
		}

		void addRepresentationsFromDefaultContexts() {
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
				try {
					if (context->Precision() && *context->Precision() < lowest_precision_encountered) {
						lowest_precision_encountered = *context->Precision();
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

			if (representations->size() == 0) {
				Logger::Warning("No representations encountered in relevant contexts, using all");
				representations = ifc_file->instances_by_type<IfcSchema::IfcRepresentation>();
			}
		}

		// Move to the next IfcRepresentation
		void _nextShape() {
			// In order to conserve memory and reduce cache insertion times, the cache is
			// cleared after an arbitrary number of processed representations. This has been
			// benchmarked extensively: https://github.com/IfcOpenShell/IfcOpenShell/pull/47
			static const int clear_interval = 64;
			if (done % clear_interval == clear_interval - 1) {
				kernel.purge_cache();
			}
			ifcproducts.reset();
			++ representation_iterator;
			++ done;
		}

		bool geometry_reuse_ok_for_current_representation_;

		IfcSchema::IfcTypeProduct* get_product_type(IfcSchema::IfcProduct* product) {
			auto rels = product->IsTypedBy();
			for (auto it = rels->begin(); it != rels->end(); ++it) {
				auto rel = *it;
				// Avoid segfault if RelatingType is unset.
				if (rel->get("RelatingType")->isNull()){
					return nullptr;
				}
				return rel->RelatingType()->as<IfcSchema::IfcTypeProduct>();
			}
			return nullptr;
		}

		IfcSchema::IfcPresentationStyle* get_material_style(const IfcSchema::IfcMaterial* material) {
			if (material_styles.find(material) != material_styles.end()) {
				return material_styles[material];
			}
			auto representations = material->HasRepresentation();
			if (representations->size() != 0) {
				auto representation = *representations->begin();
				auto traversed = IfcParse::traverse(representation)->as<IfcSchema::IfcPresentationStyle>();
				if (traversed->size() != 0){
					auto style = *traversed->begin();
					material_styles[material] = style;
					return style;
				}
			}
			material_styles[material] = nullptr;
			return nullptr;
		}

		// Return true if it's okay for this product to reuse the mapped representation,
		// returns false if it must use it's immediate representation.
		bool reuse_ok_(IfcSchema::IfcProduct* product) {
			// With world coords enabled, object transformations are directly applied to
			// the BRep. There is no way to re-use the geometry for multiple products.
			if (settings.get(IteratorSettings::USE_WORLD_COORDS)) {
				return false;
			}

			std::set<const IfcSchema::IfcMaterial*> associated_single_materials;

			if (!settings.get(IteratorSettings::DISABLE_OPENING_SUBTRACTIONS) && kernel.find_openings(product)->size()) {
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

			// Use an immediate representation in case if product is an occurrence
			// that has an overriding material style.
			auto material = kernel.get_single_material_association(product->as<IfcSchema::IfcObjectDefinition>());
			if (material) {
				auto style = get_material_style(material);
				if (style) {
					// Even if product has no type/type material but has it's own material style,
					// it should use it's immediate representation
					// since it's possible that other product with the same mapped
					// representation will have it's own material style.
					auto product_type = get_product_type(product);
					if (!product_type) {
						return false;
					}
					auto type_material = kernel.get_single_material_association(product_type->as<IfcSchema::IfcObjectDefinition>());
					if (!type_material){
						return false;
					}
					auto type_material_style = get_material_style(type_material);
					if (!type_material_style || style != type_material_style) {
						return false;
					}
				}
			}
			return true;
		}

		boost::optional<boost::variant<std::pair<IfcSchema::IfcRepresentation*, IfcSchema::IfcProduct*>,IfcParse::IfcException>> try_get_next_task() {
			boost::variant<
				std::pair<IfcSchema::IfcRepresentation*, IfcSchema::IfcProduct*>,
				IfcParse::IfcException
			> r;
			try {
				auto p = get_next_task();
				if (p) {
					r = *p;
				} else {
					return boost::none;
				}
			} catch (IfcParse::IfcException& e) {
				r = e;
			} catch (...) {
				r = IfcParse::IfcException("Unknown error");
			}
			return r;
		}

		std::map<const IfcSchema::IfcMaterial*, IfcSchema::IfcPresentationStyle*> material_styles;
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
					IfcSchema::IfcProduct::list::ptr unfiltered_products = kernel.products_represented_by(representation);
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

					// Check if representation is mapped to another.
					IfcSchema::IfcRepresentation* representation_mapped_to = kernel.representation_mapped_to(representation);
					IfcSchema::IfcProduct::list::ptr ifcproducts_ = IfcSchema::IfcProduct::list::ptr(new IfcSchema::IfcProduct::list);
					if (representation_mapped_to) {
						// Immediate representation that's using mapped representation.
						// Could be a type occurrence representation or some other type of mapping.
						// We filter only the products that must use this immediate representation
						// (e.g. they have openings, see reuse_ok_).
						for (IfcSchema::IfcProduct::list::it jt = ifcproducts->begin(); jt != ifcproducts->end(); ++jt) {
							IfcSchema::IfcProduct* prod = *jt;
							// If there's no reason for this product to have an immediate representaiton,
							// we skip it as it will be processed with it's mapped representation.
							if (reuse_ok_(prod)) {
								continue;
							}
							ifcproducts_->push(prod);
						}
                        ifcproducts = ifcproducts_;
						geometry_reuse_ok_for_current_representation_ = false;
					} else {
						// Mapped representation / immediate representations that don't use any other mapped representations.
						// Do opposite of the above, filter products that have no reason
						// to use their immediate representation (or if they don't have one).
						for (IfcSchema::IfcProduct::list::it jt = ifcproducts->begin(); jt != ifcproducts->end(); ++jt) {
							IfcSchema::IfcProduct* prod = *jt;
							if (!reuse_ok_(prod)) {
								IfcSchema::IfcRepresentation* prod_representation;
								prod_representation = kernel.find_representation(prod, representation->ContextOfItems());
								// Skip product only if it does have a mapped representation.
								// So we don't skip cases like an occurrence with openings without a type.
								if (representation != prod_representation) {
									continue;
								}
							}
							ifcproducts_->push(prod);
						}
                        ifcproducts = ifcproducts_;
						geometry_reuse_ok_for_current_representation_ = true;
					}

					if (ifcproducts->size() == 0) {
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

		std::mutex caching_mutex_;

		template <typename Fn>
		Element* decorate_with_cache_(GeometrySerializer::read_type rt, const std::string& product_guid, const std::string& representation_id, Fn f) {
			
			bool read_from_cache = false;
			Element* element = nullptr;

#ifdef WITH_HDF5
			if (cache_) {
				std::lock_guard<std::mutex> lk(caching_mutex_);

				auto from_cache = cache_->read(*ifc_file, product_guid, representation_id, rt);
				if (from_cache) {
					read_from_cache = true;
					element = from_cache;
				}
			}
#endif
			if (!read_from_cache) {
				element = f();
			}

#ifdef WITH_HDF5
			if (cache_ && !read_from_cache && element) {
				std::lock_guard<std::mutex> lk(caching_mutex_);

				if (rt == GeometrySerializer::READ_TRIANGULATION) {
					cache_->write((IfcGeom::TriangulationElement*) element);
				} else {
					cache_->write((IfcGeom::BRepElement*)element);
				}				
			}
#endif

			return element;
		}

		BRepElement* create_shape_model_for_next_entity() {
			for (;;) {
				auto rp = get_next_task();
				if (!rp) {
					return nullptr;
				}
				auto representation = rp->first;
				auto product = rp->second;

				Logger::SetProduct(product);

				BRepElement* element = (BRepElement*)decorate_with_cache_(GeometrySerializer::READ_BREP, product->GlobalId(), std::to_string(representation->data().id()), [this, product, representation]() {
					if (ifcproduct_iterator == ifcproducts->begin() || !geometry_reuse_ok_for_current_representation_) {
						return kernel.create_brep_for_representation_and_product(settings, representation, product);
					} else {
						return kernel.create_brep_for_processed_representation(settings, representation, product, current_shape_model);
					}
				});

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

		void create_element_(
			IfcGeom::MAKE_TYPE_NAME(Kernel)* kernel,
			const IfcGeom::IteratorSettings& settings,
			geometry_conversion_task* rep)
		{
			IfcSchema::IfcRepresentation *representation = rep->representation;
			IfcSchema::IfcProduct *product = *rep->products->begin();

			IfcGeom::BRepElement* brep = static_cast<IfcGeom::BRepElement*>(decorate_with_cache_(GeometrySerializer::READ_BREP, product->GlobalId(), std::to_string(representation->data().id()), [kernel, settings, product, representation]() {
				return kernel->create_brep_for_representation_and_product(settings, representation, product);
			}));

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
				auto product2 = *it;
				IfcGeom::BRepElement* brep2 = static_cast<IfcGeom::BRepElement*>(decorate_with_cache_(GeometrySerializer::READ_BREP, product2->GlobalId(), std::to_string(representation->data().id()), [kernel, settings, product2, representation, brep]() {
					return kernel->create_brep_for_processed_representation(settings, representation, product2, brep);
				}));
				if (brep2) {
					auto elem2 = process_based_on_settings(settings, brep2, dynamic_cast<IfcGeom::TriangulationElement*>(elem));
					if (elem2) {
						rep->breps.push_back(brep2);
						rep->elements.push_back(elem2);
					}
				}
			}
		}

		IfcGeom::Element* process_based_on_settings(
			const IfcGeom::IteratorSettings& settings,
			IfcGeom::BRepElement* elem,
			IfcGeom::TriangulationElement* previous = nullptr)
		{
			if (settings.get(IfcGeom::IteratorSettings::USE_BREP_DATA)) {
				try {
					return new IfcGeom::SerializedElement(*elem);
				} catch (...) {
					Logger::Message(Logger::LOG_ERROR, "Getting a serialized element from model failed.");
					return nullptr;
				}
			} else if (!settings.get(IfcGeom::IteratorSettings::DISABLE_TRIANGULATION)) {
				// the part before the hyphen is the representation id
				auto gid2 = elem->geometry().id();
				auto hyphen = gid2.find("-");
				if (hyphen != std::string::npos) {
					gid2 = gid2.substr(0, hyphen);
				}

				return decorate_with_cache_(GeometrySerializer::READ_TRIANGULATION, elem->guid(), gid2, [elem, previous]() {
					try {
						if (!previous) {
							return new TriangulationElement(*elem);
						} else {
							return new TriangulationElement(*elem, previous->geometry_pointer());
						}
					} catch (...) {
						Logger::Message(Logger::LOG_ERROR, "Getting a triangulation element from model failed.");
					}
					return (TriangulationElement*)nullptr;
				});
			} else {
				return elem;
			}
		}

		bool wait_for_element() {
			while (true) {
				size_t s;
				{
					std::lock_guard<std::mutex> lk(element_ready_mutex_);
					s = all_processed_elements_.size();
				}
				if (s > async_elements_returned_) {
					++async_elements_returned_;
					return true;
				} else if (finished_) {
					return false;
				} else {
					std::this_thread::sleep_for(std::chrono::milliseconds(10));
				}
			}
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
				if (!wait_for_element()) {
					return nullptr;
				}

				task_result_iterator_++;
				native_task_result_iterator_++;

				return (*task_result_iterator_)->product();
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
        Element* get()
        {
            // TODO: Test settings and throw
            Element* ret = 0;

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
			if (settings.get(IteratorSettings::ELEMENT_HIERARCHY))
			{
				// We are going to build a vector with the element parents.
				// First, create the parent vector
				std::vector<const IfcGeom::Element*> parents;

				// if the element has a parent
				if (ret->parent_id() != -1)
				{
					const IfcGeom::Element* parent_object = NULL;
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
		BRepElement* get_native()
		{
			// TODO: Test settings and throw
			if (num_threads_ != 1) {
				return *native_task_result_iterator_;
			} else {
				return current_shape_model;
			}
		}

		const Element* get_object(int id) {
			gp_Trsf trsf;
			int parent_id = -1;
			std::string instance_type, product_name, product_guid;
            IfcSchema::IfcProduct* ifc_product = 0;

			try {
				IfcUtil::IfcBaseClass* ifc_entity = ifc_file->instance_by_id(id);
				instance_type = ifc_entity->declaration().name();

				if (ifc_entity->declaration().is(IfcSchema::IfcRoot::Class())) {
					IfcSchema::IfcRoot* ifc_root = ifc_entity->as<IfcSchema::IfcRoot>();
					product_guid = ifc_root->GlobalId();
					product_name = ifc_root->Name().get_value_or("");
				}

				if (ifc_entity->declaration().is(IfcSchema::IfcProduct::Class())) {
					ifc_product = ifc_entity->as<IfcSchema::IfcProduct>();
					parent_id = -1;
					try {
						auto parent_object = kernel.get_decomposing_entity(ifc_product);
						if (parent_object) {
							parent_id = parent_object->data().id();
						}
					} catch (const std::exception& e) {
						Logger::Error(e);
					} catch (...) {
						Logger::Error("Failed to find decomposing entity");
					}

					if (ifc_product->ObjectPlacement()) {
						try {
							kernel.convert(ifc_product->ObjectPlacement(), trsf);
						} catch (const std::exception& e) {
							Logger::Error(e);
						} catch (...) {
							Logger::Error("Failed to construct placement");
						}
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

			Element* ifc_object = new Element(element_settings, id, parent_id, product_name, instance_type, product_guid, "", trsf, ifc_product);
			return ifc_object;
		}

		IfcUtil::IfcBaseClass* create() {
			IfcGeom::BRepElement* next_shape_model = 0;
			IfcGeom::SerializedElement* next_serialization = 0;
			IfcGeom::TriangulationElement* next_triangulation = 0;

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
						next_serialization = new SerializedElement(*next_shape_model);
					} catch (...) {
                        Logger::Message(Logger::LOG_ERROR, "Getting a serialized element from model failed.");
					}
				} else if (!settings.get(IteratorSettings::DISABLE_TRIANGULATION)) {
					// the part before the hyphen is the representation id
					auto gid2 = next_shape_model->geometry().id();
					auto hyphen = gid2.find("-");
					if (hyphen != std::string::npos) {
						gid2 = gid2.substr(0, hyphen);
					}

					next_triangulation = (TriangulationElement*)decorate_with_cache_(GeometrySerializer::READ_TRIANGULATION, next_shape_model->guid(), gid2, [this, next_shape_model]() {
						try {
							if (ifcproduct_iterator == ifcproducts->begin() || !geometry_reuse_ok_for_current_representation_) {
								return new TriangulationElement(*next_shape_model);
							} else {
								return new TriangulationElement(*next_shape_model, current_triangulation->geometry_pointer());
							}
						} catch (...) {
							Logger::Message(Logger::LOG_ERROR, "Getting a triangulation element from model failed.");
						}
						return (TriangulationElement*) nullptr;
					});
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

            kernel.setValue(IfcGeom::Kernel::GV_MAX_FACES_TO_ORIENT, settings.get(IteratorSettings::SEW_SHELLS) ? std::numeric_limits<double>::infinity() : -1);
            kernel.setValue(IfcGeom::Kernel::GV_DIMENSIONALITY, (settings.get(IteratorSettings::INCLUDE_CURVES)
                ? (settings.get(IteratorSettings::EXCLUDE_SOLIDS_AND_SURFACES) ? -1. : 0.) : +1.));
			kernel.setValue(IfcGeom::Kernel::GV_LAYERSET_FIRST,
				settings.get(IteratorSettings::LAYERSET_FIRST)
				? +1.0
				: -1.0
			);
			kernel.setValue(IfcGeom::Kernel::GV_NO_WIRE_INTERSECTION_CHECK,
							settings.get(IteratorSettings::NO_WIRE_INTERSECTION_CHECK)
							? +1.0
							: -1.0
			);
			kernel.setValue(IfcGeom::Kernel::GV_NO_WIRE_INTERSECTION_TOLERANCE,
							settings.get(IteratorSettings::NO_WIRE_INTERSECTION_TOLERANCE)
							? +1.0
							: -1.0
			);
			kernel.setValue(IfcGeom::Kernel::GV_PRECISION_FACTOR,
							settings.get(IteratorSettings::STRICT_TOLERANCE)
							? 1.0
							: 10.0
			);

			kernel.setValue(IfcGeom::Kernel::GV_DISABLE_BOOLEAN_RESULT,
				settings.get(IteratorSettings::DISABLE_BOOLEAN_RESULT)
				? +1.0
				: -1.0
			);

			kernel.setValue(IfcGeom::Kernel::GV_DEBUG_BOOLEAN,
				settings.get(IteratorSettings::DEBUG_BOOLEAN)
				? +1.0
				: -1.0
			);

			kernel.setValue(IfcGeom::Kernel::GV_BOOLEAN_ATTEMPT_2D,
				settings.get(IteratorSettings::BOOLEAN_ATTEMPT_2D)
				? +1.0
				: -1.0
			);

			if (settings.get(IteratorSettings::BUILDING_LOCAL_PLACEMENT)) {
				if (settings.get(IteratorSettings::SITE_LOCAL_PLACEMENT)) {
					Logger::Message(Logger::LOG_WARNING, "building-local-placement takes precedence over site-local-placement");
				}
				kernel.set_conversion_placement_rel_to_type(&IfcSchema::IfcBuilding::Class());
			} else if (settings.get(IteratorSettings::SITE_LOCAL_PLACEMENT)) {
				kernel.set_conversion_placement_rel_to_type(&IfcSchema::IfcSite::Class());
			}
			kernel.set_offset(settings.offset);
			kernel.set_rotation(settings.rotation);
		}

	public:
		MAKE_TYPE_NAME(IteratorImplementation_)(const IteratorSettings& settings, IfcParse::IfcFile* file, const std::vector<IfcGeom::filter_t>& filters, int num_threads)
			: settings(settings)
			, ifc_file(file)
			, filters_(filters)
			, owns_ifc_file(false)
			, num_threads_(num_threads)
		{
			_initialize();
		}

		~MAKE_TYPE_NAME(IteratorImplementation_)() {
			if (num_threads_ != 1) {
				terminating_ = true;

				if (init_future_.valid()) {
					init_future_.wait();
				}
			}

			if (owns_ifc_file) {
				delete ifc_file;
			}

			if (!settings.get(IfcGeom::IteratorSettings::DISABLE_TRIANGULATION)) {
				for (auto& p : all_processed_native_elements_) {
					delete p;
				}
			}

			for (auto& p : all_processed_elements_) {
				delete p;
			}

			for (auto& k : kernel_pool) {
				delete k;
			}

			free_shapes();
		}
	};
}

#endif
