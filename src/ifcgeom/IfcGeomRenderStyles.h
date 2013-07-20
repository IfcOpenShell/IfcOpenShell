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
#include <array>
#endif

#include "../ifcparse/Ifc2x3.h"

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
		SurfaceStyle() {}
		SurfaceStyle(int id) : id(id) {}
		SurfaceStyle(const std::string& name) : name(name) {}
		SurfaceStyle(int id, const std::string& name) : id(id), name(name) {}
		
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
		
		const std::string Name() const { 
			if (name && id) {
				std::stringstream sstr; 
				sstr << (*id) << "_" << (*name);
				return sstr.str(); 
			} else if (name) { 
				return *name; 
			} else if (id) { 
				std::stringstream sstr; 
				sstr << "IfcSurfaceStyleShading_" << (*id); 
				return sstr.str(); 
			} else {
				return "IfcSurfaceStyleShading";
			}
		}

		const boost::optional<ColorComponent>& Diffuse() const { return diffuse; }
		const boost::optional<ColorComponent>& Specular() const { return specular; }
		const boost::optional<double>& Transparency() const { return transparency; }
		const boost::optional<double>& Specularity() const { return specularity; }
		boost::optional<ColorComponent>& Diffuse() { return diffuse; }
		boost::optional<ColorComponent>& Specular() { return specular; }
		boost::optional<double>& Transparency() { return transparency; }
		boost::optional<double>& Specularity() { return specularity; }
	};

	template <typename T> std::pair<Ifc2x3::IfcSurfaceStyle*, T*> get_surface_style(Ifc2x3::IfcRepresentationItem* representation_item) {
		Ifc2x3::IfcStyledItem::list styled_items = representation_item->StyledByItem();
		for (Ifc2x3::IfcStyledItem::it jt = styled_items->begin(); jt != styled_items->end(); ++jt) {
			Ifc2x3::IfcPresentationStyleAssignment::list style_assignments = (*jt)->Styles();
			for (Ifc2x3::IfcPresentationStyleAssignment::it kt = style_assignments->begin(); kt != style_assignments->end(); ++kt) {
				IfcAbstractSelect::list styles = (*kt)->Styles();
				for (IfcAbstractSelect::it lt = styles->begin(); lt != styles->end(); ++lt) {
					IfcAbstractSelect::ptr style = *lt;
					if (style->is(Ifc2x3::Type::IfcSurfaceStyle)) {
						Ifc2x3::IfcSurfaceStyle* surface_style = (Ifc2x3::IfcSurfaceStyle*) style;
						if (surface_style->Side() != Ifc2x3::IfcSurfaceSide::IfcSurfaceSide_NEGATIVE) {
							IfcAbstractSelect::list styles_elements = surface_style->Styles();
							for (IfcAbstractSelect::it mt = styles_elements->begin(); mt != styles_elements->end(); ++mt) {
								if ((*mt)->is(T::Class())) {
									return std::make_pair(surface_style, (T*) *mt);
								}
							}
						}
					}
				}
			}

			// StyledByItem is a SET [0:1] OF IfcStyledItem, so we
			// break after encountering the first IfcStyledItem
			break;
		}

		return std::make_pair<Ifc2x3::IfcSurfaceStyle*, T*>(0,0);
	}

	const SurfaceStyle* get_style(Ifc2x3::IfcRepresentationItem* representation_item);
	const SurfaceStyle* get_default_style(const std::string& ifc_type);
	
	namespace Cache {
		void PurgeStyleCache();
	}
}

#endif