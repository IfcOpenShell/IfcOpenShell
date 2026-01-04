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
#include "../ifcgeom/ConversionSettings.h"

#include <boost/function.hpp>

#include <map>
#include <string>
#include <tuple>

namespace ifcopenshell {

namespace geometry {

	struct IFC_GEOM_API geometry_conversion_task {
		int index;
        express::Base representation;
		std::vector<express::Base> products;
	};

    /// The filter function (free or member function) or function object (use boost::ref() to reference to it)
    /// should return true if the geometry for the product is wanted to be included in the output.
    /// http://www.boost.org/doc/libs/1_62_0/doc/html/function/tutorial.html
	typedef boost::function<bool(const express::Base&)> filter_t;
    
    class IFC_GEOM_API abstract_mapping {
	protected:
		Settings settings_;

		bool use_caching_ = true;

	public:
		abstract_mapping(Settings& s) : settings_(s) {}
		virtual ~abstract_mapping() {}

		virtual ifcopenshell::geometry::taxonomy::ptr map(const express::Base&) = 0;
        virtual void get_representations(std::vector<geometry_conversion_task>& tasks, std::vector<filter_t>& filters) = 0;
        virtual express::Base get_decomposing_entity(const express::Base& product, bool include_openings = true) = 0;
		virtual std::map<std::string, express::Base> get_layers(const express::Base&) = 0;
		virtual std::vector<express::Base> find_openings(const express::Base&) = 0;
		virtual void initialize_settings() = 0;
		virtual bool get_layerset_information(const express::Base&, layerset_information&, int&) = 0;
        virtual bool get_wall_neighbours(const express::Base&, std::vector<endpoint_connection>&) = 0;
        virtual const express::Base get_product_type(const express::Base&) = 0;
        virtual const express::Base get_single_material_association(const express::Base&) = 0;
		virtual double get_length_unit() const = 0;
		virtual const std::string& get_length_unit_name() const = 0;
        virtual express::Base representation_of(const express::Base& product) = 0;

		const Settings& settings() const { return settings_; }
		Settings& settings() { return settings_; }

		bool use_caching() const { return use_caching_; }
		bool& use_caching() { return use_caching_; }
    };

	namespace impl {
		typedef boost::function2<abstract_mapping*, IfcParse::IfcFile*, Settings&> mapping_fn;

		class IFC_GEOM_API MappingFactoryImplementation : public std::map<std::string, mapping_fn> {
		public:
			MappingFactoryImplementation();
			void bind(const std::string& schema_name, mapping_fn);
			abstract_mapping* construct(IfcParse::IfcFile*, Settings&);
		};

		IFC_GEOM_API MappingFactoryImplementation& mapping_implementations();
	}
    
}

}

#endif
