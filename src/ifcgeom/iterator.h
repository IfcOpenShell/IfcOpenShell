/********************************************************************************
 *																			  *
 * This file is part of IfcOpenShell.										   *
 *																			  *
 * IfcOpenShell is free software: you can redistribute it and/or modify		 *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or		  *
 * (at your option) any later version.										  *
 *																			  *
 * IfcOpenShell is distributed in the hope that it will be useful,			  *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of			   *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the				 *
 * Lesser GNU General Public License for more details.						  *
 *																			  *
 * You should have received a copy of the Lesser GNU General Public License	 *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.		 *
 *																			  *
 ********************************************************************************/

/********************************************************************************
 *																			  *
 * Geometrical data in an IFC file consists of shapes (IfcShapeRepresentation)  *
 * and instances (SUBTYPE OF IfcBuildingElement e.g. IfcWindow).				*
 *																			  *
 * ifcopenshell::geom::triangulation is a class that represents a		  *
 * triangulated IfcShapeRepresentation.										 *
 *   Triangulation.verts is a 1 dimensional vector of float defining the		*
 *	  cartesian coordinates of the vertices of the triangulated shape in the  *
 *	  format of [x1,y1,z1,..,xn,yn,zn]										*
 *   Triangulation.faces is a 1 dimensional vector of int containing the		*
 *	 indices of the triangles referencing positions in Triangulation.verts	*
 *   Triangulation.edges is a 1 dimensional vector of int in {0,1} that dictates*
 *	   the visibility of the edges that span the faces in Triangulation.faces   *
 *																			  *
 * ifcopenshell::geom::element represents the actual IfcBuildingElements.				  *
 *   IfcGeomObject.name is the GUID of the element							  *
 *   IfcGeomObject.type is the datatype of the element e.g. IfcWindow		   *
 *   IfcGeomObject.mesh is a pointer to an IfcMesh							  *
 *   IfcGeomObject.transformation.matrix is a 4x3 matrix that defines the	   *
 *	 orientation and translation of the mesh in relation to the world origin  *
 *																			  *
 * ifcopenshell::geom::iterator::initialize()											  *
 *   finds the most suitable representation contexts. Returns true iff		  *
 *   at least a single representation will process successfully				 *
 *																			  *
 * ifcopenshell::geom::iterator::get()													 *
 *   transfers ownership of the current ifcopenshell::geom::element				  *
 *																			  *
 * ifcopenshell::geom::iterator::next()													*
 *   returns true iff a following entity is available for a successive call to  *
 *   ifcopenshell::geom::iterator::get()												   *
 *																			  *
 * ifcopenshell::geom::iterator::progress()												*
 *   returns an int in [0..100] that indicates the overall progress			 *
 *																			  *
 ********************************************************************************/

#ifndef IFCGEOMITERATOR_H
#define IFCGEOMITERATOR_H

#include "../ifcparse/file.h"

#include "../ifcgeom/element.h"
#include "../ifcgeom/conversion_result.h"
#include "../ifcgeom/filter.h"
#include "../ifcgeom/taxonomy.h"
#include "../ifcgeom/converter.h"
#include "../ifcgeom/abstract_mapping.h"

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
#include <memory>

namespace ifcopenshell::geom {

	struct IFC_GEOM_API geometry_conversion_result {
		geometry_conversion_result() = default;
		geometry_conversion_result(const geometry_conversion_result&) = delete;
		geometry_conversion_result& operator=(const geometry_conversion_result&) = delete;
		geometry_conversion_result(geometry_conversion_result&&) noexcept = default;
		geometry_conversion_result& operator=(geometry_conversion_result&&) noexcept = default;

		int index;

		// For NoParallelMapping==true
		ifcopenshell::geom::taxonomy::ptr item;
		std::vector<std::pair<express::base, ifcopenshell::geom::taxonomy::matrix4::ptr>> products;

		// For NoParallelMapping==false
		express::base representation;
		std::vector<express::base> products_2;

		std::vector<std::unique_ptr<ifcopenshell::geom::native_element>> native_elements;
		std::vector<std::unique_ptr<ifcopenshell::geom::element>> elements;

		bool is_parallel() const {
            return !!representation;
		}
	};


	class IFC_GEOM_API iterator {
	private:
		std::atomic<bool> finished_{ false };
		std::atomic<bool> terminating_{ false };
		std::atomic<bool> had_error_processing_elements_ { false };
		std::atomic<int> progress_{ 0 };

		std::vector<geometry_conversion_result> tasks_;
		std::vector<geometry_conversion_result>::iterator task_iterator_;

		std::list<std::unique_ptr<ifcopenshell::geom::element>> all_processed_elements_;
		std::list<std::unique_ptr<ifcopenshell::geom::native_element>> all_processed_native_elements_;

		std::list<std::unique_ptr<ifcopenshell::geom::element>>::iterator task_result_iterator_;
		std::list<std::unique_ptr<ifcopenshell::geom::native_element>>::iterator native_task_result_iterator_;

		std::mutex element_ready_mutex_;
		bool task_result_ptr_initialized = false;
		bool task_result_ptr_exhausted = false;
		size_t async_elements_returned_ = 0;

		ifcopenshell::geom::settings settings_;
		ifcopenshell::file* ifc_file;
		std::vector<ifcopenshell::geom::filter_function> filters_;
		int num_threads_;
		std::string geometry_library_;
		ifcopenshell::logger& logger_;

		// When single-threaded
		ifcopenshell::geom::converter* converter_;

		// When multi-threaded
		std::vector<ifcopenshell::geom::converter*> kernel_pool;
		std::vector<std::unique_ptr<ifcopenshell::logger>> worker_loggers_;

		// The object is fetched beforehand to be sure that get() returns a valid element
		triangulation_element* current_triangulation;
		native_element* current_shape_model;
		serialized_element* current_serialization;

		double lowest_precision_encountered;
		bool any_precision_encountered;

		int done;
		int total;

		ifcopenshell::geom::taxonomy::point3 bounds_min_;
		ifcopenshell::geom::taxonomy::point3 bounds_max_;

		// Should not be destructed because, destructor is blocking
		std::future<void> init_future_;
		std::array<std::chrono::high_resolution_clock::time_point, 4> time_points;

		template <typename Fn>
		element* create_processed_element_(Fn f) {
			return f();
		}

		express::base create_shape_model_for_next_entity();

		void create_element_(
			ifcopenshell::geom::converter* kernel,
			ifcopenshell::geom::settings settings,
			geometry_conversion_result* rep);

		std::unique_ptr<ifcopenshell::geom::element> process_based_on_settings(
			ifcopenshell::geom::settings settings,
			ifcopenshell::geom::native_element* elem,
			ifcopenshell::logger& logger,
			ifcopenshell::geom::triangulation_element* previous = nullptr);

		void flush_worker_log(ifcopenshell::geom::converter* kernel);

		bool wait_for_element();

		void log_timepoints() const;
		void validate_iterator_state() const;

		ifcopenshell::geom::taxonomy::direction3::ptr remove_offset_();
	public:

		iterator(std::unique_ptr<ifcopenshell::geom::kernels::abstract_kernel>&& geometry_library, const ifcopenshell::geom::settings& settings, ifcopenshell::file* file, const std::vector<ifcopenshell::geom::filter_function>& filters, int num_threads, ifcopenshell::logger& logger = ifcopenshell::logger::root())
			: settings_(settings)
			, ifc_file(file)
			, filters_(filters)
			, num_threads_(num_threads)
			, geometry_library_(geometry_library->geometry_library())
			, logger_(logger)
			// @todo verify whether settings are correctly passed on
			, converter_(new ifcopenshell::geom::converter(std::move(geometry_library), ifc_file, settings_, logger_))
		{
		}

		iterator(std::unique_ptr<ifcopenshell::geom::kernels::abstract_kernel>&& geometry_library, const ifcopenshell::geom::settings& settings, ifcopenshell::file* file, ifcopenshell::logger& logger = ifcopenshell::logger::root())
			: settings_(settings)
			, ifc_file(file)
			, num_threads_(1)
			, geometry_library_(geometry_library->geometry_library())
			, logger_(logger)
			, converter_(new ifcopenshell::geom::converter(std::move(geometry_library), ifc_file, settings_, logger_))
		{
		}

		iterator(std::unique_ptr<ifcopenshell::geom::kernels::abstract_kernel>&& geometry_library, const ifcopenshell::geom::settings& settings, ifcopenshell::file* file, int num_threads, ifcopenshell::logger& logger = ifcopenshell::logger::root())
			: settings_(settings)
			, ifc_file(file)
			, num_threads_(num_threads)
			, geometry_library_(geometry_library->geometry_library())
			, logger_(logger)
			, converter_(new ifcopenshell::geom::converter(std::move(geometry_library), ifc_file, settings_, logger_))
		{
		}

		~iterator();

		std::vector<ifcopenshell::geom::taxonomy::item::ptr> get_task_items() const {
			std::vector<ifcopenshell::geom::taxonomy::item::ptr> items;
			items.reserve(tasks_.size());
			for (const auto& task : tasks_) {
				items.push_back(task.item);
			}
			return items;
		}

		std::vector<std::vector<express::base>> get_task_products() const {
            std::vector<std::vector<express::base>> products;
			for (const auto& task : tasks_) {
				if (task.is_parallel()) {
					products.push_back(task.products_2);
				} else {
					for (auto& product : task.products) {
                        std::vector<express::base> p;
						p.push_back(product.first);
						products.push_back(p);
					}
				}
			}
			return products;
		}

		const std::string& unit_name() const { return converter_->mapping()->get_length_unit_name(); }
		double unit_magnitude() const { return converter_->mapping()->get_length_unit(); }
		// Check if error occurred during iterator initialization or iteration over elements.
		bool had_error_processing_elements() const { return had_error_processing_elements_; }

		std::optional<bool> initialization_outcome_;

		/**
		 * @return Returns true if the iterator is initialized with any elements, false otherwise.
		 *
		 * @note
		 * - A true return value does not guarantee successful initialization of all elements.
		 *   Some elements may have failed to initialize. Check had_error_processing_elements()
		 *   to see whether there were errors during the initialization.
		 *
		 * - For non-concurrent iterators, a false return may occur if initialization of the first
		 *   element fails, even if subsequent elements could be initialized successfully.
		 */
		bool initialize();

		size_t processed_ = 0;

		void process_finished_rep(geometry_conversion_result* rep, ifcopenshell::geom::converter* kernel = nullptr);

		void process_concurrently();

		/// Computes model's bounding box (bounds_min and bounds_max).
		/// @note Can take several minutes for large files.
		void compute_bounds(bool with_geometry);

		int progress() const {
			return progress_;
		}

		std::string getLog() const { return logger_.get_log(); }

		ifcopenshell::file* file() const { return ifc_file; }

		const std::vector<ifcopenshell::geom::filter_function>& filters() const { return filters_; }
        std::vector<ifcopenshell::geom::filter_function>& filters() { return filters_; }

		const ifcopenshell::geom::taxonomy::point3& bounds_min() const { return bounds_min_; }
		const ifcopenshell::geom::taxonomy::point3& bounds_max() const { return bounds_max_; }

		/// Moves to the next shape representation, create its geometry, and returns the associated product.
		/// Use get() to retrieve the created geometry.
		express::base next();

		/// Gets the representation of the current geometrical entity.
		std::unique_ptr<element> get();

		/// Gets the native (Open Cascade or CGAL) representation of the current geometrical entity.
		std::unique_ptr<native_element> get_native()
		{
			validate_iterator_state();
			if (settings_.get<ifcopenshell::geom::settings::IteratorOutput>().get() == ifcopenshell::geom::settings::NATIVE) {
				throw std::runtime_error("native output is returned by get(); use get() instead");
			}
			std::lock_guard<std::mutex> lock(element_ready_mutex_);
			auto result = std::move(*native_task_result_iterator_);
			if (!result) {
				throw std::runtime_error("current native element has already been retrieved");
			}
			return result;
		}

		std::unique_ptr<element> get_object(int id);

		express::base create();
	};
}

#endif
