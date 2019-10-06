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
 * ifcopenshell::geometry::Representation::Triangulation is a class that represents a          *
 * triangulated IfcShapeRepresentation.                                         *
 *   Triangulation.verts is a 1 dimensional vector of float defining the        *
 *      cartesian coordinates of the vertices of the triangulated shape in the  *
 *      format of [x1,y1,z1,..,xn,yn,zn]                                        *
 *   Triangulation.faces is a 1 dimensional vector of int containing the        *
 *     indices of the triangles referencing positions in Triangulation.verts    *
 *   Triangulation.edges is a 1 dimensional vector of int in {0,1} that dictates*
 *	   the visibility of the edges that span the faces in Triangulation.faces   *
 *                                                                              *
 * ifcopenshell::geometry::Element represents the actual IfcBuildingElements.                  *
 *   IfcGeomObject.name is the GUID of the element                              *
 *   IfcGeomObject.type is the datatype of the element e.g. IfcWindow           *
 *   IfcGeomObject.mesh is a pointer to an IfcMesh                              *
 *   IfcGeomObject.transformation.matrix is a 4x3 matrix that defines the       *
 *     orientation and translation of the mesh in relation to the world origin  *
 *                                                                              *
 * ifcopenshell::geometry::Iterator::initialize()                                              *
 *   finds the most suitable representation contexts. Returns true iff          *
 *   at least a single representation will process successfully                 *
 *                                                                              *
 * ifcopenshell::geometry::Iterator::get()                                                     *
 *   returns a pointer to the current ifcopenshell::geometry::Element                          *
 *                                                                              * 
 * ifcopenshell::geometry::Iterator::next()                                                    *
 *   returns true iff a following entity is available for a successive call to  *
 *   ifcopenshell::geometry::Iterator::get()                                                   *
 *                                                                              *
 * ifcopenshell::geometry::Iterator::progress()                                                *
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
#include "../../ifcgeom/settings.h"
#include "../../ifcgeom/schema_agnostic/ConversionResult.h"

#include "../../ifcgeom/schema_agnostic/IfcGeomFilter.h"

#include "../../ifcgeom/kernel_agnostic/AbstractKernel.h"

#include "../../ifcgeom/schema_agnostic/Converter.h"

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
	ifcopenshell::geometry::Element* process_based_on_settings(
		const ifcopenshell::geometry::settings& settings,
		ifcopenshell::geometry::NativeElement* elem, 
		ifcopenshell::geometry::TriangulationElement* previous=nullptr)
	{
		if (settings.get(ifcopenshell::geometry::settings::USE_BREP_DATA)) {
			try {
				return new ifcopenshell::geometry::SerializedElement(*elem);
			} catch (...) {
				Logger::Message(Logger::LOG_ERROR, "Getting a serialized element from model failed.");
				return nullptr;
			}
		} else if (!settings.get(ifcopenshell::geometry::settings::DISABLE_TRIANGULATION)) {
			try {
				if (!previous) {
					return  new ifcopenshell::geometry::TriangulationElement(*elem);
				} else {
					return  new ifcopenshell::geometry::TriangulationElement(*elem, previous->geometry_pointer());
				}
			} catch (...) {
				Logger::Message(Logger::LOG_ERROR, "Getting a triangulation element from model failed.");
				return nullptr;
			}
		} else {
			return elem;
		}
	}

	void create_element(
		ifcopenshell::geometry::Converter* converter, 
		const ifcopenshell::geometry::settings& settings,
		ifcopenshell::geometry::geometry_conversion_task* rep)
	{
		IfcUtil::IfcBaseEntity* representation = rep->representation;
		IfcUtil::IfcBaseEntity* product = (IfcUtil::IfcBaseEntity*) *rep->products->begin();
		auto brep = converter->create_brep_for_representation_and_product(representation, product);
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
			auto brep2 = converter->create_brep_for_processed_representation(representation, (IfcUtil::IfcBaseEntity*) *it, brep);
			if (brep2) {
				auto elem2 = process_based_on_settings(settings, brep, dynamic_cast<ifcopenshell::geometry::TriangulationElement*>(elem));
				if (elem2) {
					rep->breps.push_back(brep2);
					rep->elements.push_back(elem2);
				}
			}
		}
	}
}

namespace ifcopenshell { namespace geometry {
	
	class Iterator {
	private:

		int num_threads_;
		std::atomic<int> progress_;
		std::vector<geometry_conversion_task> tasks_;
		std::vector<geometry_conversion_task>::iterator task_iterator_;

		std::vector<ifcopenshell::geometry::Element*> all_processed_elements_;
		std::vector<ifcopenshell::geometry::NativeElement*> all_processed_native_elements_;
		size_t task_result_index_;

		std::string geometry_library_;

		Iterator(const Iterator&); // N/I
		Iterator& operator=(const Iterator&); // N/I

		Converter* converter_;
		settings settings_;

		IfcParse::IfcFile* ifc_file;

		int done;
		int total;

		std::string unit_name_;
		double unit_magnitude_;

        gp_XYZ bounds_min_;
        gp_XYZ bounds_max_;

        std::vector<filter_t> filters_;

        /// @todo public/private sections all over the place: move all public to the beginning of the class
	public:

		const std::string& unit_name() const { return unit_name_; }
		const double unit_magnitude() const { return unit_magnitude_; }

		bool initialize() {
			converter_ = new Converter(geometry_library_, ifc_file, settings_);
			converter_->mapping()->get_representations(tasks_, filters_, settings_);

			if (tasks_.size() == 0) {
				Logger::Warning("No representations encountered, aborting");
				return false;
			}

			task_iterator_ = tasks_.begin();

			task_result_index_ = 0;
			done = 0;
			total = tasks_.size();

			if (num_threads_ != 1) {
				process_concurrently();
			} else {
				if (!create()) {
					return false;
				}
			}
			
			return true;
		}

		void process_concurrently() {
			size_t conc_threads = num_threads_;
			if (conc_threads > tasks_.size()) {
				conc_threads = tasks_.size();
			}
			
			std::vector<Converter*> kernel_pool;
			kernel_pool.reserve(conc_threads);
			for (unsigned i = 0; i < conc_threads; ++i) {
				kernel_pool.push_back(new Converter(geometry_library_, ifc_file, settings_));
			}

			std::vector<std::future<void>> threadpool;

			int old_progress = -1;
			int processed = 0;

			Logger::ProgressBar(0);

			for (auto& rep : tasks_) {
				Converter* K = nullptr;
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

				std::future<void> fu = std::async(std::launch::async, create_element, K, std::ref(settings_), &rep);
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

			task_result_index_ = 0;

			Logger::Status("\rDone creating geometry (" + boost::lexical_cast<std::string>(all_processed_elements_.size()) +
				" objects)                                ");
		}

        /// Computes model's bounding box (bounds_min and bounds_max).
        /// @note Can take several minutes for large files.
        void compute_bounds()
        {
			// @todo

			/*
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
			*/
        }

		int progress() const { 
			if (num_threads_ == 1) {
				return 100 * done / total;
			} else {
				return progress_;
			}
		}

		const std::string& getUnitName() const { return unit_name_; }

        /// @note Double always as per IFC specification.
        double getUnitMagnitude() const { return unit_magnitude_; }
	
		std::string getLog() const { return Logger::GetLog(); }

		IfcParse::IfcFile* file() const { return ifc_file; }

        const std::vector<ifcopenshell::geometry::filter_t>& filters() const { return filters_; }
        std::vector<ifcopenshell::geometry::filter_t>& filters() { return filters_; }

        const gp_XYZ& bounds_min() const { return bounds_min_; }
        const gp_XYZ& bounds_max() const { return bounds_max_; }

		Converter& converter() { return *converter_; }

	private:
		// Move to the next IfcRepresentation
		void _nextShape() {
			++task_iterator_;
			++done;
		}		

		IfcUtil::IfcBaseClass* create_shape_model_for_next_entity() {
			geometry_conversion_task* task = nullptr;
			while (task_iterator_ != tasks_.end()) {
				task = &*task_iterator_++;
				create_element(converter_, settings_, task);
				if (task->elements.empty()) {
					task = nullptr;
				} else {
					break;
				}
			}
			if (task) {
				all_processed_elements_.insert(all_processed_elements_.end(), task->elements.begin(), task->elements.end());
				all_processed_native_elements_.insert(all_processed_native_elements_.end(), task->breps.begin(), task->breps.end());
				return (*task->products)[0];
			} else {
				return nullptr;
			}
		}

    public:

        /// Moves to the next shape representation, create its geometry, and returns the associated product.
        /// Use get() to retrieve the created geometry.
		IfcUtil::IfcBaseClass* next() {
			if (num_threads_ != 1) {
				task_result_index_++;
				if (task_result_index_ == all_processed_elements_.size()) {
					return nullptr;
				} else {
					return all_processed_elements_[task_result_index_]->product();
				}
			} else {
				// Increment the iterator over the list of products using the current
				// shape representation
				++task_result_index_;
				if (task_result_index_ == all_processed_elements_.size()) {
					return create();
				}
				if (task_result_index_ == all_processed_elements_.size()) {
					return nullptr;
				}
				return all_processed_elements_[task_result_index_]->product();
			}
		}

        /// Gets the representation of the current geometrical entity.
        Element* get()
        {
            // TODO: Test settings and throw
            Element* ret = 0;

			ret = all_processed_elements_[task_result_index_];

			// If we want to organize the element considering their hierarchy
			if (settings_.get(settings::SEARCH_FLOOR))
			{
				// We are going to build a vector with the element parents.
				// First, create the parent vector
				std::vector<const ifcopenshell::geometry::Element*> parents;
				
				// if the element has a parent
				if (ret->parent_id() != -1)
				{
					const ifcopenshell::geometry::Element* parent_object = NULL;
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
		NativeElement* get_native()
		{
			return all_processed_native_elements_[task_result_index_];
		}

		const Element* get_object(int id) {
			// @todo
			return nullptr;
			/*
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

			Element* ifc_object = new Element(element_settings, id, parent_id, product_name, instance_type, product_guid, "", trsf, ifc_product);
			return ifc_object;
			*/
		}

		IfcUtil::IfcBaseClass* create() {
			IfcUtil::IfcBaseClass* product = nullptr;
			try {
				product = create_shape_model_for_next_entity();
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
			return product;
		}
	private:
		void _initialize() {
			unit_name_ = "METER";
			unit_magnitude_ = 1.f;

			// @todo

			/*
            kernel->setValue(ifcopenshell::geometry::Kernel::GV_MAX_FACES_TO_ORIENT, settings.get(settings::SEW_SHELLS) ? std::numeric_limits<double>::infinity() : -1);
            kernel->setValue(ifcopenshell::geometry::Kernel::GV_DIMENSIONALITY, (settings.get(settings::INCLUDE_CURVES)
                ? (settings.get(settings::EXCLUDE_SOLIDS_AND_SURFACES) ? -1. : 0.) : +1.));
			if (settings.get(settings::BUILDING_LOCAL_PLACEMENT)) {
				if (settings.get(settings::SITE_LOCAL_PLACEMENT)) {
					Logger::Message(Logger::LOG_WARNING, "building-local-placement takes precedence over site-local-placement");
				}
				kernel->set_conversion_placement_rel_to(&IfcSchema::IfcBuilding::Class());
			} else if (settings.get(settings::SITE_LOCAL_PLACEMENT)) {
				kernel->set_conversion_placement_rel_to(&IfcSchema::IfcSite::Class());
			}
			*/
		}

		bool owns_ifc_file;
	public:
		Iterator(const std::string& geometry_library, const settings& settings, IfcParse::IfcFile* file, const std::vector<ifcopenshell::geometry::filter_t>& filters, int num_threads = 1)
			: settings_(settings)
			, ifc_file(file)
			, filters_(filters)
			, owns_ifc_file(false)
			, num_threads_(num_threads)
			, geometry_library_(geometry_library)
		{
			_initialize();
		}

		Iterator(const settings& settings, IfcParse::IfcFile* file, int num_threads = 1)
			: settings_(settings)
			, ifc_file(file)
			, owns_ifc_file(false)
			, num_threads_(num_threads)
			, geometry_library_("opencascade")
		{
			_initialize();
		}

		~Iterator() {
			if (owns_ifc_file) {
				delete ifc_file;
			}

			if (settings_.get(settings::DISABLE_TRIANGULATION)) {
				for (auto& p : all_processed_native_elements_) {
					delete p;
				}
			}

			for (auto& p : all_processed_elements_) {
				delete p;
			}
		}
	};
}}

#endif
