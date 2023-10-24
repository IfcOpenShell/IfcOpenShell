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

#include "../ifcparse/IfcFile.h"

#include "../ifcgeom/IfcGeomElement.h"
#include "../ifcgeom/IteratorSettings.h"
#include "../ifcgeom/ConversionResult.h"
#include "../ifcgeom/IfcGeomFilter.h"
#include "../ifcgeom/taxonomy.h"
#include "../ifcgeom/Converter.h"
#include "../ifcgeom/abstract_mapping.h"
#include "../ifcgeom/GeometrySerializer.h"

#ifdef IFOPSH_WITH_OPENCASCADE
#include <Standard_Failure.hxx>
#endif

#include <boost/algorithm/string.hpp>

#include <map>
#include <set>
#include <vector>
#include <limits>
#include <algorithm>
#include <future>
#include <thread>
#include <chrono>
#include <atomic>

// @todo
using namespace ifcopenshell::geometry;

namespace {
	struct geometry_conversion_result {
		int index;
		ifcopenshell::geometry::taxonomy::ptr item;
		std::vector<std::pair<const IfcUtil::IfcBaseEntity*, taxonomy::matrix4::ptr>> products;
		std::vector<IfcGeom::BRepElement*> breps;
		std::vector<IfcGeom::Element*> elements;
	};
}

namespace IfcGeom {

	class Iterator {
	private:
		GeometrySerializer* cache_ = nullptr;

		std::atomic<bool> finished_{ false };
		std::atomic<int> progress_{ 0 };

		std::vector<geometry_conversion_result> tasks_;
		std::vector<geometry_conversion_result>::iterator task_iterator_;

		std::list<IfcGeom::Element*> all_processed_elements_;
		std::list<IfcGeom::BRepElement*> all_processed_native_elements_;

		typename std::list<IfcGeom::Element*>::const_iterator task_result_iterator_;
		typename std::list<IfcGeom::BRepElement*>::const_iterator native_task_result_iterator_;

		std::mutex element_ready_mutex_;
		bool task_result_ptr_initialized = false;
		// ?
		size_t async_elements_returned_ = 0;
		size_t task_result_index_ = 0;

		std::string geometry_library_;
		
		IteratorSettings settings_;
		IfcParse::IfcFile* ifc_file;
		std::vector<filter_t> filters_;
		bool owns_ifc_file;
		int num_threads_;

		// When single-threaded
		Converter* converter_;
		
		// When multi-threaded
		std::vector<Converter*> kernel_pool;

		// The object is fetched beforehand to be sure that get() returns a valid element
		TriangulationElement* current_triangulation;
		BRepElement* current_shape_model;
		SerializedElement* current_serialization;

		double lowest_precision_encountered;
		bool any_precision_encountered;

		int done;
		int total;

		// @todo these appear uninitialized?
		std::string unit_name_;
		double unit_magnitude_;

        taxonomy::point3 bounds_min_;
		taxonomy::point3 bounds_max_;

		// Should not be destructed because, destructor is blocking
		std::future<void> init_future_;

        /// @todo public/private sections all over the place: move all public to the beginning of the class
	public:
		void set_cache(GeometrySerializer* cache) { cache_ = cache; }

		const std::string& unit_name() const { return unit_name_; }
		double unit_magnitude() const { return unit_magnitude_; }

		boost::optional<bool> initialization_outcome_;

		bool initialize() {
			if (initialization_outcome_) {
				return *initialization_outcome_;
			}

			converter_ = new Converter(geometry_library_, ifc_file, settings_);
			std::vector<geometry_conversion_task> reps;
			converter_->mapping()->get_representations(reps, filters_);

			for (auto& task : reps) {
				geometry_conversion_result res;
				res.item = converter_->mapping()->map(task.representation);
				if (!res.item) {
					continue;
				}
				std::transform(task.products->begin(), task.products->end(), std::back_inserter(res.products), [this, &res](IfcUtil::IfcBaseClass* prod) {
					auto prod_item = converter_->mapping()->map(prod);
					return std::make_pair(prod->as<IfcUtil::IfcBaseEntity>(), taxonomy::cast<taxonomy::geom_item>(prod_item)->matrix);
				});
				tasks_.push_back(res);
			}

			std::vector<IfcUtil::IfcBaseClass*> products;
			for (auto& r : reps) {
				std::copy(r.products->begin(), r.products->end(), std::back_inserter(products));
			}

			/*
			// What to do, map representation and product individually?
			// There needs to be two options, mapped item respecting (does that still work?), and optimized based on topology sorting.
			// Or is the sorting not necessary if we just cache?

			std::vector<taxonomy::ptr> items;
			std::map<taxonomy::ptr, taxonomy::matrix4> placements;
			std::transform(products.begin(), products.end(), std::back_inserter(items), [this, &placements](IfcUtil::IfcBaseClass* p) {
				auto item = converter_->mapping()->map(p);
				// Product placements do not affect item reuse and should temporarily be swapped to identity
				if (item) {
					std::swap(placements[item], ((taxonomy::geom_ptr)item)->matrix);
				}
				return item;
			});
			items.erase(std::remove(items.begin(), items.end(), nullptr), items.end());
			std::sort(items.begin(), items.end(), taxonomy::less);
			auto it = items.begin();
			while (it < items.end()) {
				auto jt = std::upper_bound(it, items.end(), *it, taxonomy::less);
				geometry_conversion_result r;
				r.item = *it;
				std::transform(it, jt, std::back_inserter(r.products), [&r, &placements](taxonomy::ptr product_node) {
					return std::make_pair((IfcUtil::IfcBaseEntity*) product_node->instance, placements[product_node]);
				});
				tasks_.push_back(r);
				it = jt;
			}
			*/

			Logger::Notice("Created " + boost::lexical_cast<std::string>(tasks_.size()) + " tasks for " + boost::lexical_cast<std::string>(products.size()) + " products");

			if (tasks_.size() == 0) {
				Logger::Warning("No representations encountered, aborting");
				initialization_outcome_.reset(false);
			} else {

				task_iterator_ = tasks_.begin();

				task_result_index_ = 0;
				done = 0;
				total = tasks_.size();

				if (num_threads_ != 1) {
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

		size_t processed_ = 0;

		void process_finished_rep(geometry_conversion_result* rep) {
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
				kernel_pool.push_back(new Converter(geometry_library_, ifc_file, settings_));
			}

			std::vector<std::future<geometry_conversion_result*>> threadpool;			
			
			for (auto& rep : tasks_) {
				Converter* K = nullptr;
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

				std::future<geometry_conversion_result*> fu = std::async(
					std::launch::async, [this](
						Converter* kernel,
						const IfcGeom::IteratorSettings& settings,
						geometry_conversion_result* rep) {
							this->create_element_(kernel, settings, rep); 
							return rep;
						},
					K,
					std::ref(settings_),
					&rep);

				threadpool.emplace_back(std::move(fu));
			}

			for (auto& fu : threadpool) {
				process_finished_rep(fu.get());
			}

			finished_ = true;

			Logger::Status("\rDone creating geometry (" + boost::lexical_cast<std::string>(all_processed_elements_.size()) +
				" objects)                                ");
		}

        /// Computes model's bounding box (bounds_min and bounds_max).
        /// @note Can take several minutes for large files.
        void compute_bounds(bool with_geometry)
        {
            for (int i = 0; i < 3; ++i) {
                bounds_min_.components()(i) = std::numeric_limits<double>::infinity();
				bounds_max_.components()(i) = -std::numeric_limits<double>::infinity();
            }

			if (with_geometry) {
				size_t num_created = 0;
				do {
					IfcGeom::Element* geom_object = get();
					const IfcGeom::TriangulationElement* o = static_cast<const IfcGeom::TriangulationElement*>(geom_object);
					const IfcGeom::Representation::Triangulation& mesh = o->geometry();
					auto mat = o->transformation().data()->ccomponents();
					Eigen::Vector4d vec, transformed;

					for (typename std::vector<double>::const_iterator it = mesh.verts().begin(); it != mesh.verts().end();) {
						const double& x = *(it++);
						const double& y = *(it++);
						const double& z = *(it++);
						vec << x, y, z, 1.;
						transformed = mat * vec;

						for (int i = 0; i < 3; ++i) {
							bounds_min_.components()(i) = std::min(bounds_min_.components()(i), transformed(i));
							bounds_max_.components()(i) = std::max(bounds_min_.components()(i), transformed(i));
						}
					}
				} while (++num_created, next());
			} else {
				std::vector<geometry_conversion_task> reps;
				converter_->mapping()->get_representations(reps, filters_);

				std::vector<IfcUtil::IfcBaseClass*> products;
				for (auto& r : reps) {
					std::copy(r.products->begin(), r.products->end(), std::back_inserter(products));
				}

				for (auto& product : products) {
					auto prod_item = converter_->mapping()->map(product);
					auto vec = taxonomy::cast<taxonomy::geom_item>(prod_item)->matrix->translation_part();

					for (int i = 0; i < 3; ++i) {
						bounds_min_.components()(i) = std::min(bounds_min_.components()(i), vec(i));
						bounds_max_.components()(i) = std::max(bounds_min_.components()(i), vec(i));
					}
				}
			}
        }

		int progress() const {
			return progress_;
		}

		std::string getLog() const { return Logger::GetLog(); }

		IfcParse::IfcFile* file() const { return ifc_file; }

        const std::vector<IfcGeom::filter_t>& filters() const { return filters_; }
        std::vector<IfcGeom::filter_t>& filters() { return filters_; }

        const taxonomy::point3& bounds_min() const { return bounds_min_; }
        const taxonomy::point3& bounds_max() const { return bounds_max_; }

	private:

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

		const IfcUtil::IfcBaseClass* create_shape_model_for_next_entity() {
			geometry_conversion_result* task = nullptr;
			for (; task_iterator_ < tasks_.end();) {
				task = &*task_iterator_++;
				// @todo where can we still set logger?
				// Logger::SetProduct(product);
				create_element_(converter_, settings_, task);
				if (task->elements.empty()) {
					task = nullptr;
				} else {
					break;
				}
			}
			if (task) {
				process_finished_rep(task);
				return task->item->instance->as<IfcUtil::IfcBaseClass>();
			} else {
				return nullptr;
			}
		}

		void create_element_(
			Converter* kernel,
			const IfcGeom::IteratorSettings& settings,
			geometry_conversion_result* rep)
		{
			auto representation = rep->item;

			auto product_node = rep->products.front();
			const IfcUtil::IfcBaseEntity* product = product_node.first;
			const auto& place = product_node.second;

			Logger::SetProduct(product);
			
			IfcGeom::BRepElement* brep = static_cast<IfcGeom::BRepElement*>(decorate_with_cache_(GeometrySerializer::READ_BREP, (std::string)*product->get("GlobalId"), std::to_string(representation->instance->data().id()), [kernel, settings, product, place, representation]() {
				return kernel->create_brep_for_representation_and_product(representation, product, place);
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

			for (auto it = rep->products.begin() + 1; it != rep->products.end(); ++it) {
				const auto& p = *it;
				const IfcUtil::IfcBaseEntity* product2 = p.first;
				const auto& place2 = p.second;

				IfcGeom::BRepElement* brep2 = static_cast<IfcGeom::BRepElement*>(decorate_with_cache_(GeometrySerializer::READ_BREP, (std::string)*product2->get("GlobalId"), std::to_string(representation->instance->data().id()), [kernel, settings, product2, place2, representation, brep]() {
					return kernel->create_brep_for_processed_representation(product2, place2, brep);
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
		const IfcUtil::IfcBaseClass* next() {
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
				if (task_result_iterator_ == --all_processed_elements_.end()) {
					if (!create()) {
						return nullptr;
					}
				}
				
				task_result_iterator_++;
				native_task_result_iterator_++;

				return (*task_result_iterator_)->product();
			}
		}

        /// Gets the representation of the current geometrical entity.
        Element* get()
        {
            auto ret = *task_result_iterator_;
			
			// If we want to organize the element considering their hierarchy
			if (settings_.get(IteratorSettings::ELEMENT_HIERARCHY))
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

		/// Gets the native (Open Cascade or CGAL) representation of the current geometrical entity.
		BRepElement* get_native()
		{
			return *native_task_result_iterator_;
		}

		const Element* get_object(int id) {
			taxonomy::matrix4::ptr m4;
			int parent_id = -1;
			std::string instance_type, product_name, product_guid;
            IfcUtil::IfcBaseEntity* ifc_product = 0;

			try {
				IfcUtil::IfcBaseEntity* ifc_entity = ifc_file->instance_by_id(id)->as<IfcUtil::IfcBaseEntity>();
				instance_type = ifc_entity->declaration().name();

				if (ifc_entity->declaration().is("IfcRoot")) {
					product_guid = (std::string) *ifc_entity->get("GlobalId");
					product_name = ifc_entity->get_value<std::string>("Name", "");
				}

				auto parent_object = converter_->mapping()->get_decomposing_entity(ifc_entity);
				if (parent_object) {
					parent_id = parent_object->data().id();
				}

				m4 = taxonomy::cast<taxonomy::geom_item>(converter_->mapping()->map(ifc_product))->matrix;
			} catch (const std::exception& e) {
				Logger::Error(e);
			}
#ifdef IFOPSH_WITH_OPENCASCADE
			catch (const Standard_Failure& e) {
				if (e.GetMessageString() && strlen(e.GetMessageString())) {
					Logger::Error(e.GetMessageString());
				} else {
					Logger::Error("Unknown error returning product");
				}
			}
#endif
			catch (...) {
				Logger::Error("Unknown error returning product");
			}

			ElementSettings element_settings(settings_, unit_magnitude_, instance_type);

			Element* ifc_object = new Element(element_settings, id, parent_id, product_name, instance_type, product_guid, "", m4, ifc_product);
			return ifc_object;
		}

		const IfcUtil::IfcBaseClass* create() {
			const IfcUtil::IfcBaseClass* product = nullptr;
			try {
				product = create_shape_model_for_next_entity();
			} catch (const std::exception& e) {
				Logger::Error(e);
			}
#ifdef IFOPSH_WITH_OPENCASCADE
			catch (const Standard_Failure& e) {
				if (e.GetMessageString() && strlen(e.GetMessageString())) {
					Logger::Error(e.GetMessageString());
				} else {
					Logger::Error("Unknown error creating geometry");
				}
			}
#endif
			catch (...) {
				Logger::Error("Unknown error creating geometry");
			}
			return product;
		}

		Iterator(const std::string& geometry_library, const IteratorSettings& settings, IfcParse::IfcFile* file, const std::vector<IfcGeom::filter_t>& filters, int num_threads)
			: settings_(settings)
			, ifc_file(file)
			, filters_(filters)
			, owns_ifc_file(false)
			, num_threads_(num_threads)
			, geometry_library_(geometry_library)
		{
		}

		Iterator(const IteratorSettings& settings, IfcParse::IfcFile* file, const std::vector<IfcGeom::filter_t>& filters, int num_threads)
			: settings_(settings)
			, ifc_file(file)
			, filters_(filters)
			, owns_ifc_file(false)
			, num_threads_(num_threads)
			, geometry_library_("opencascade")
		{
		}

		Iterator(const IteratorSettings& settings, IfcParse::IfcFile* file)
			: settings_(settings)
			, ifc_file(file)
			, owns_ifc_file(false)
			, num_threads_(1)
			, geometry_library_("opencascade")
		{
		}

		Iterator(const std::string& geometry_library, const IteratorSettings& settings, IfcParse::IfcFile* file)
			: settings_(settings)
			, ifc_file(file)
			, owns_ifc_file(false)
			, num_threads_(1)
			, geometry_library_(geometry_library)
		{
		}

		Iterator(const std::string& geometry_library, const IteratorSettings& settings, IfcParse::IfcFile* file, int num_threads)
			: settings_(settings)
			, ifc_file(file)
			, owns_ifc_file(false)
			, num_threads_(num_threads)
			, geometry_library_(geometry_library)
		{
		}

		~Iterator() {
			if (owns_ifc_file) {
				delete ifc_file;
			}

			if (!settings_.get(IfcGeom::IteratorSettings::DISABLE_TRIANGULATION)) {
				for (auto& p : all_processed_native_elements_) {
					delete p;
				}
			}
			
			for (auto& k : kernel_pool) {
				delete k;
			}
			
		    for (auto& p : all_processed_elements_) {
				delete p;
			}
		}
	};
}

#endif
