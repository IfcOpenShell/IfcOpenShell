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

#ifndef IFCGEOMRENDERSTYLES_H
#define IFCGEOMRENDERSTYLES_H

#include "ifc_geom_api.h"
#ifdef USE_IFC4
#include "../ifcparse/Ifc4.h"
#else
#include "../ifcparse/Ifc2x3.h"
#endif

#include <boost/algorithm/string/case_conv.hpp>
#include <boost/algorithm/string/replace.hpp>

namespace IfcGeom {
	class IFC_GEOM_API SurfaceStyle {
	public:
		class ColorComponent {
		private:
			double data[3];
		public:
			ColorComponent(double r, double g, double b) {
				data[0] = r; data[1] = g; data[2] = b;
			}
			const double& R() const { return data[0]; }
			const double& G() const { return data[1]; }
			const double& B() const { return data[2]; }
			double& R() { return data[0]; }
			double& G() { return data[1]; }
			double& B() { return data[2]; }
		};
	private:
		std::string name;
        std::string original_name_;
		boost::optional<int> id;
		boost::optional<ColorComponent> diffuse, specular;
		boost::optional<double> transparency;
		boost::optional<double> specularity;
	public:
        SurfaceStyle() : name("surface-style") {}
		SurfaceStyle(int id) : id(id) {
			std::stringstream sstr; 
			sstr << "surface-style-" << id; 
			this->name = sstr.str(); 
		}
        SurfaceStyle(const std::string& name) : name(name), original_name_(name) {}
        SurfaceStyle(int id, const std::string& name) : original_name_(name), id(id)
        {
			std::stringstream sstr; 
			std::string sanitized = name;
            boost::to_lower(sanitized);
            boost::replace_all(sanitized, " ", "-");
			sstr << "surface-style-" << id << "-" << sanitized;
			this->name = sstr.str(); 
		}
		
		// Not used at this point. In fact, equality testing in the current
		// architecture can just as easily be accomplished by comparing the
		// pointer addresses of the styles, as they are always referenced 
		// from out of a global map of some sort.
		bool operator==(const SurfaceStyle& other) {
			return name == other.name;
		}
		
        /// ID name, e.g. "surface-style-66675-metal---aluminium"
		const std::string& Name() const { return name; }

        /// Original name, if available, e.g. "Metal - Aluminium"
        const std::string& original_name() const { return original_name_; }

		const boost::optional<ColorComponent>& Diffuse() const { return diffuse; }
		const boost::optional<ColorComponent>& Specular() const { return specular; }
		const boost::optional<double>& Transparency() const { return transparency; }
		const boost::optional<double>& Specularity() const { return specularity; }
		boost::optional<ColorComponent>& Diffuse() { return diffuse; }
		boost::optional<ColorComponent>& Specular() { return specular; }
		boost::optional<double>& Transparency() { return transparency; }
		boost::optional<double>& Specularity() { return specularity; }
	};

    IFC_GEOM_API const SurfaceStyle* get_default_style(const std::string& ifc_type);
}

#endif
