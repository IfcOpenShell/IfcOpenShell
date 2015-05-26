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

#ifdef __GNUC__
#include <tr1/array>
#else
#if _MSC_VER < 1600
#include <boost/tr1/array.hpp>
#else
#include <array>
#endif
#endif

#ifdef USE_IFC4
#include "../ifcparse/Ifc4.h"
#else
#include "../ifcparse/Ifc2x3.h"
#endif

namespace IfcGeom {
	class SurfaceStyle {
	public:
		class ColorComponent {
		private:
			std::tr1::array<double, 3> data;
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
		boost::optional<std::string> name;
		boost::optional<int> id;
		boost::optional<ColorComponent> diffuse, specular;
		boost::optional<double> transparency;
		boost::optional<double> specularity;
	public:
		SurfaceStyle() {
			this->name = "surface-style";
		}
		SurfaceStyle(int id) : id(id) {
			std::stringstream sstr; 
			sstr << "surface-style-" << id; 
			this->name = sstr.str(); 
		}
		SurfaceStyle(const std::string& name) : name(name) {}
		SurfaceStyle(int id, const std::string& name) : id(id) {
			std::stringstream sstr; 
			std::string sanitized = name;
			std::transform(sanitized.begin(), sanitized.end(), sanitized.begin(), ::tolower);
			std::replace(sanitized.begin(), sanitized.end(), ' ', '-');
			sstr << "surface-style-" << id << "-" << sanitized;
			this->name = sstr.str(); 
		}
		
		// Not used at this point. In fact, equality testing in the current
		// architecture can just as easily be accomplished by comparing the
		// pointer addresses of the styles, as they are always referenced 
		// from out of a global map of some sort.
		bool operator==(const SurfaceStyle& other) {
			if (name && other.name) {
				return *name == *other.name;
			} else if (id && other.id) {
				return *id == *other.id;
			} else {
				return false;
			}
		}
		
		const std::string& Name() const { return *name; }

		const boost::optional<ColorComponent>& Diffuse() const { return diffuse; }
		const boost::optional<ColorComponent>& Specular() const { return specular; }
		const boost::optional<double>& Transparency() const { return transparency; }
		const boost::optional<double>& Specularity() const { return specularity; }
		boost::optional<ColorComponent>& Diffuse() { return diffuse; }
		boost::optional<ColorComponent>& Specular() { return specular; }
		boost::optional<double>& Transparency() { return transparency; }
		boost::optional<double>& Specularity() { return specularity; }
	};

	const SurfaceStyle* get_default_style(const std::string& ifc_type);
}

#endif