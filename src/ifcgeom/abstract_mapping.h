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

#ifndef ABSTRACT_MAPPING_H
#define ABSTRACT_MAPPING_H

#include "../ifcparse/express.h"
#include "../ifcgeom/taxonomy.h"
#include "../ifcgeom/conversion_settings.h"
#include "../plugin/plugin.h"

#include <functional>
#include <map>
#include <string>
#include <tuple>

namespace ifcopenshell {

namespace geom {

	struct IFC_GEOM_API geometry_conversion_task {
		int index;
        express::base representation;
		std::vector<express::base> products;
	};

    /// The filter function (free or member function) or function object (use std::ref() to reference to it)
    /// should return true if the geometry for the product is wanted to be included in the output.
    /// http://www.boost.org/doc/libs/1_62_0/doc/html/function/tutorial.html
	typedef std::function<bool(const express::base&)> filter_function;

	class IFC_GEOM_API abstract_mapping {
	protected:
		ifcopenshell::geom::settings settings_;
		ifcopenshell::logger& logger_;

		bool use_caching_ = true;

	public:
		abstract_mapping(ifcopenshell::geom::settings& settings, ifcopenshell::logger& logger = ifcopenshell::logger::root()) : settings_(settings), logger_(logger) {}
		virtual ~abstract_mapping() {}

		virtual ifcopenshell::geom::taxonomy::ptr map(const express::base&) = 0;
        virtual void get_representations(std::vector<geometry_conversion_task>& tasks, std::vector<filter_function>& filters) = 0;
        virtual express::base get_decomposing_entity(const express::base& product, bool include_openings = true) = 0;
		virtual std::map<std::string, express::base> get_layers(const express::base&) = 0;
		virtual std::vector<express::base> find_openings(const express::base&) = 0;
		virtual void initialize_settings() = 0;
		virtual bool get_layerset_information(const express::base&, layerset_information&, int&) = 0;
        virtual bool get_wall_neighbours(const express::base&, std::vector<endpoint_connection>&) = 0;
        virtual const express::base get_product_type(const express::base&) = 0;
        virtual const express::base get_single_material_association(const express::base&) = 0;
		virtual double get_length_unit() const = 0;
		virtual const std::string& get_length_unit_name() const = 0;
        virtual express::base representation_of(const express::base& product) = 0;

		const ifcopenshell::geom::settings& settings() const { return settings_; }
		ifcopenshell::geom::settings& settings() { return settings_; }
		ifcopenshell::logger& logger() const { return logger_; }

		bool use_caching() const { return use_caching_; }
		bool& use_caching() { return use_caching_; }
    };

	namespace impl {
		typedef std::function<abstract_mapping*(ifcopenshell::file*, ifcopenshell::geom::settings&, ifcopenshell::logger&)> mapping_fn;

		class IFC_GEOM_API mapping_registry {
		public:
			void bind(const std::string& schema_name, mapping_fn fn, const ifcopenshell::plugin::module& module = ifcopenshell::plugin::module());
			abstract_mapping* construct(ifcopenshell::file* file, ifcopenshell::geom::settings& settings, ifcopenshell::logger& logger = ifcopenshell::logger::root());

		private:
			struct entry {
				ifcopenshell::plugin::module module_;
				mapping_fn fn_;
			};

			std::map<std::string, entry> entries_;
		};

		IFC_GEOM_API mapping_registry& mapping_registry_instance();

		class IFC_GEOM_API mapping_factory_implementation {
		public:
			mapping_factory_implementation();
			void bind(const std::string& schema_name, mapping_fn);
			abstract_mapping* construct(ifcopenshell::file*, ifcopenshell::geom::settings&, ifcopenshell::logger& logger = ifcopenshell::logger::root());
		};

		IFC_GEOM_API mapping_factory_implementation& mapping_implementations();
	}

}

}

#endif
