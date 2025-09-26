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
 * IfcGeom::Representation::Triangulation is a class that represents a		  *
 * triangulated IfcShapeRepresentation.										 *
 *   Triangulation.verts is a 1 dimensional vector of float defining the		*
 *	  cartesian coordinates of the vertices of the triangulated shape in the  *
 *	  format of [x1,y1,z1,..,xn,yn,zn]										*
 *   Triangulation.faces is a 1 dimensional vector of int containing the		*
 *	 indices of the triangles referencing positions in Triangulation.verts	*
 *   Triangulation.edges is a 1 dimensional vector of int in {0,1} that dictates*
 *	   the visibility of the edges that span the faces in Triangulation.faces   *
 *																			  *
 * IfcGeom::Element represents the actual IfcBuildingElements.				  *
 *   IfcGeomObject.name is the GUID of the element							  *
 *   IfcGeomObject.type is the datatype of the element e.g. IfcWindow		   *
 *   IfcGeomObject.mesh is a pointer to an IfcMesh							  *
 *   IfcGeomObject.transformation.matrix is a 4x3 matrix that defines the	   *
 *	 orientation and translation of the mesh in relation to the world origin  *
 *																			  *
 * IfcGeom::Iterator::initialize()											  *
 *   finds the most suitable representation contexts. Returns true iff		  *
 *   at least a single representation will process successfully				 *
 *																			  *
 * IfcGeom::Iterator::get()													 *
 *   returns a pointer to the current IfcGeom::Element						  *
 *																			  *
 * IfcGeom::Iterator::next()													*
 *   returns true iff a following entity is available for a successive call to  *
 *   IfcGeom::Iterator::get()												   *
 *																			  *
 * IfcGeom::Iterator::progress()												*
 *   returns an int in [0..100] that indicates the overall progress			 *
 *																			  *
 ********************************************************************************/

#ifndef IFCGEOMITERATOR_H
#define IFCGEOMITERATOR_H

#include "../ifcparse/IfcFile.h"

#include "../ifcgeom/IfcGeomElement.h"
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

namespace IfcGeom {

	struct IFC_GEOM_API geometry_conversion_result {
		int index;

		// For NoParallelMapping==true
		ifcopenshell::geometry::taxonomy::ptr item;
		std::vector<std::pair<IfcUtil::IfcBaseEntity*, ifcopenshell::geometry::taxonomy::matrix4::ptr>> products;

		// For NoParallelMapping==false
		IfcUtil::IfcBaseEntity* representation;
		aggregate_of_instance::ptr products_2;

		std::vector<IfcGeom::BRepElement*> breps;
		std::vector<IfcGeom::Element*> elements;
	};


	class IFC_GEOM_API Iterator {
	private:
		GeometrySerializer* cache_ = nullptr;

		std::atomic<bool> finished_{ false };
		std::atomic<bool> terminating_{ false };
		std::atomic<bool> had_error_processing_elements_ { false };
		std::atomic<int> progress_{ 0 };

		std::vector<geometry_conversion_result> tasks_;
		std::vector<geometry_conversion_result>::iterator task_iterator_;

		std::list<IfcGeom::Element*> all_processed_elements_;
		std::list<IfcGeom::BRepElement*> all_processed_native_elements_;

		std::list<IfcGeom::Element*>::const_iterator task_result_iterator_;
		std::list<IfcGeom::BRepElement*>::const_iterator native_task_result_iterator_;

		std::mutex element_ready_mutex_;
		bool task_result_ptr_initialized = false;
		bool task_result_ptr_exhausted = false;
		size_t async_elements_returned_ = 0;
		
		ifcopenshell::geometry::Settings settings_;
		IfcParse::IfcFile* ifc_file;
		std::vector<filter_t> filters_;
		int num_threads_;
		std::string geometry_library_;

		// When single-threaded
		ifcopenshell::geometry::Converter* converter_;
		
		// When multi-threaded
		std::vector<ifcopenshell::geometry::Converter*> kernel_pool;

		// The object is fetched beforehand to be sure that get() returns a valid element
		TriangulationElement* current_triangulation;
		BRepElement* current_shape_model;
		SerializedElement* current_serialization;

		double lowest_precision_encountered;
		bool any_precision_encountered;

		int done;
		int total;

		ifcopenshell::geometry::taxonomy::point3 bounds_min_;
		ifcopenshell::geometry::taxonomy::point3 bounds_max_;

		// Should not be destructed because, destructor is blocking
		std::future<void> init_future_;
		std::mutex caching_mutex_;

		std::array<std::chrono::high_resolution_clock::time_point, 4> time_points;

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
					cache_->write((IfcGeom::TriangulationElement*)element);
				} else {
					cache_->write((IfcGeom::BRepElement*)element);
				}
			}
#endif

			return element;
		}

		const IfcUtil::IfcBaseClass* create_shape_model_for_next_entity();

		void create_element_(
			ifcopenshell::geometry::Converter* kernel,
			ifcopenshell::geometry::Settings settings,
			geometry_conversion_result* rep);

		IfcGeom::Element* process_based_on_settings(
			ifcopenshell::geometry::Settings settings,
			IfcGeom::BRepElement* elem,
			IfcGeom::TriangulationElement* previous = nullptr);

		bool wait_for_element();

		void log_timepoints() const;
		void validate_iterator_state() const;

		ifcopenshell::geometry::taxonomy::direction3::ptr remove_offset_();
	public:

		Iterator(std::unique_ptr<ifcopenshell::geometry::kernels::AbstractKernel>&& geometry_library, const ifcopenshell::geometry::Settings& settings, IfcParse::IfcFile* file, const std::vector<IfcGeom::filter_t>& filters, int num_threads)
			: settings_(settings)
			, ifc_file(file)
			, filters_(filters)
			, num_threads_(num_threads)
			, geometry_library_(geometry_library->geometry_library())
			// @todo verify whether settings are correctly passed on
			, converter_(new ifcopenshell::geometry::Converter(std::move(geometry_library), ifc_file, settings_))
		{
		}

		Iterator(std::unique_ptr<ifcopenshell::geometry::kernels::AbstractKernel>&& geometry_library, const ifcopenshell::geometry::Settings& settings, IfcParse::IfcFile* file)
			: settings_(settings)
			, ifc_file(file)
			, num_threads_(1)
			, geometry_library_(geometry_library->geometry_library())
			, converter_(new ifcopenshell::geometry::Converter(std::move(geometry_library), ifc_file, settings_))
		{
		}

		Iterator(std::unique_ptr<ifcopenshell::geometry::kernels::AbstractKernel>&& geometry_library, const ifcopenshell::geometry::Settings& settings, IfcParse::IfcFile* file, int num_threads)
			: settings_(settings)
			, ifc_file(file)
			, num_threads_(num_threads)
			, geometry_library_(geometry_library->geometry_library())
			, converter_(new ifcopenshell::geometry::Converter(std::move(geometry_library), ifc_file, settings_))
		{
		}

		~Iterator();

		void set_cache(GeometrySerializer* cache) { cache_ = cache; }

		std::vector<ifcopenshell::geometry::taxonomy::item::ptr> get_task_items() const {
			std::vector<ifcopenshell::geometry::taxonomy::item::ptr> items;
			items.reserve(tasks_.size());
			for (const auto& task : tasks_) {
				items.push_back(task.item);
			}
			return items;
		}

		aggregate_of_aggregate_of_instance::ptr get_task_products() const {
			aggregate_of_aggregate_of_instance::ptr products = aggregate_of_aggregate_of_instance::ptr(new aggregate_of_aggregate_of_instance);
			for (const auto& task : tasks_) {
				if (task.products_2) {
					products->push(task.products_2);
				} else {
					for (auto& product : task.products) {
						aggregate_of_instance::ptr p(new aggregate_of_instance);
						p->push(product.first);
						products->push(p);
					}
				}
			}
			return products;
		}

		const std::string& unit_name() const { return converter_->mapping()->get_length_unit_name(); }
		double unit_magnitude() const { return converter_->mapping()->get_length_unit(); }
		// Check if error occurred during iterator initialization or iteration over elements.
		bool had_error_processing_elements() const { return had_error_processing_elements_; }

		boost::optional<bool> initialization_outcome_;

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

		void process_finished_rep(geometry_conversion_result* rep);

		void process_concurrently();

		/// Computes model's bounding box (bounds_min and bounds_max).
		/// @note Can take several minutes for large files.
		void compute_bounds(bool with_geometry);

		int progress() const {
			return progress_;
		}

		std::string getLog() const { return Logger::GetLog(); }

		IfcParse::IfcFile* file() const { return ifc_file; }

		const std::vector<IfcGeom::filter_t>& filters() const { return filters_; }
		std::vector<IfcGeom::filter_t>& filters() { return filters_; }

		const ifcopenshell::geometry::taxonomy::point3& bounds_min() const { return bounds_min_; }
		const ifcopenshell::geometry::taxonomy::point3& bounds_max() const { return bounds_max_; }

		/// Moves to the next shape representation, create its geometry, and returns the associated product.
		/// Use get() to retrieve the created geometry.
		const IfcUtil::IfcBaseClass* next();

		/// Gets the representation of the current geometrical entity.
		Element* get();

		/// Gets the native (Open Cascade or CGAL) representation of the current geometrical entity.
		BRepElement* get_native()
		{
			return *native_task_result_iterator_;
		}

		const Element* get_object(int id);

		const IfcUtil::IfcBaseClass* create();
	};
}

#endif
