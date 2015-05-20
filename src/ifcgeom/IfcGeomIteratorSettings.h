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

#ifndef IFCGEOMITERATORSETTINGS_H
#define IFCGEOMITERATORSETTINGS_H

#include <string>

#include "../ifcparse/IfcException.h"

namespace IfcGeom {

	class IteratorSettings {
	public:
		// Enumeration of setting identifiers. These settings define the
		// behaviour of various aspects of IfcOpenShell.

		// Specifies whether vertices are welded, meaning that the coordinates
		// vector will only contain unique xyz-triplets. This results in a 
		// manifold mesh which is useful for modelling applications, but might 
		// result in unwanted shading artifacts in rendering applications.
		static const int WELD_VERTICES = 1;
		// Specifies whether to apply the local placements of building elements
		// directly to the coordinates of the representation mesh rather than
		// to represent the local placement in the 4x3 matrix, which will in that
		// case be the identity matrix.
		static const int USE_WORLD_COORDS = 2;
		// Internally IfcOpenShell measures everything in meters. This settings
		// specifies whether to convert IfcGeomObjects back to the units in which
		// the geometry in the IFC file is specified.
		static const int CONVERT_BACK_UNITS = 3;
		// Specifies whether to use the Open Cascade BREP format for representation
		// items rather than to create triangle meshes. This is useful is IfcOpenShell
		// is used as a library in an application that is also built on Open Cascade.
		static const int USE_BREP_DATA = 4;
		// Specifies whether to sew IfcConnectedFaceSets (open and closed shells) to
		// TopoDS_Shells or whether to keep them as a loose collection of faces.
		static const int SEW_SHELLS = 5;
		// Specifies whether to compose IfcOpeningElements into a single compound
		// in order to speed up the processing of opening subtractions.
		static const int FASTER_BOOLEANS = 6;
		// Disables the subtraction of IfcOpeningElement representations from
		// the related building element representations.
		static const int DISABLE_OPENING_SUBTRACTIONS = 8;
		// Disables the triangulation of the topological representations. Useful if
		// the client application understands Open Cascade's native format.
		static const int DISABLE_TRIANGULATION = 9;
		// Applies default materials to entity instances without a surface style.
		static const int APPLY_DEFAULT_MATERIALS = 10;
		// Specifies whether to include subtypes of IfcCurve.
		static const int INCLUDE_CURVES = 11;
		// Specifies whether to exclude subtypes of IfcSolidModel and IfcSurface.
		static const int EXCLUDE_SOLIDS_AND_SURFACES = 12;

		// End of settings enumeration.

	private:
		bool _weld_vertices, _use_world_coords, _convert_back_units, _use_brep_data, _sew_shells, _faster_booleans, _disable_opening_subtractions, _disable_triangulation, _apply_default_materials, _include_curves, _exclude_solids_and_surfaces;
		double _deflection_tolerance;
	public:
		IteratorSettings()
			: _weld_vertices(true)
			, _use_world_coords(false)
			, _convert_back_units(false)
			, _use_brep_data(false)
			, _sew_shells(false)
			, _faster_booleans(false)
			, _disable_opening_subtractions(false)
			, _disable_triangulation(false)
			, _apply_default_materials(false)
			, _include_curves(false)
			, _exclude_solids_and_surfaces(false)
			// TODO: Make deflection tolerance into a command line argument
			// For now, stick to one millimeter. Note that this is independent of the IFC length unit.
			, _deflection_tolerance(1.e-3)
		{}

		const bool& weld_vertices() const { return _weld_vertices; }
		bool& weld_vertices() { return _weld_vertices; }
		const bool& use_world_coords() const { return _use_world_coords; }
		bool& use_world_coords() { return _use_world_coords; }
		const bool& convert_back_units() const { return _convert_back_units; }
		bool& convert_back_units() { return _convert_back_units; }
		const bool& use_brep_data() const { return _use_brep_data; }
		bool& use_brep_data() { return _use_brep_data; }
		const bool& sew_shells() const { return _sew_shells; }
		bool& sew_shells() { return _sew_shells; }
		const bool& faster_booleans() const { return _faster_booleans; }
		bool& faster_booleans() { return _faster_booleans; }
		const bool& disable_opening_subtractions() const { return _disable_opening_subtractions; }
		bool& disable_opening_subtractions() { return _disable_opening_subtractions; }
		const bool& disable_triangulation() const { return _disable_triangulation; }
		bool& disable_triangulation() { return _disable_triangulation; }
		const bool& apply_default_materials() const { return _apply_default_materials; }
		bool& apply_default_materials() { return _apply_default_materials; }
		const bool& include_curves() const { return _include_curves; }
		bool& include_curves() { return _include_curves; }
		const bool& exclude_solids_and_surfaces() const { return _exclude_solids_and_surfaces; }
		bool& exclude_solids_and_surfaces() { return _exclude_solids_and_surfaces; }
		
		const double& deflection_tolerance() const { return _deflection_tolerance; }
		double& deflection_tolerance() { return _deflection_tolerance; }
		
		void set(int setting, bool value) {
			switch (setting) {
			case USE_WORLD_COORDS:
				_use_world_coords = value;
				break;
			case WELD_VERTICES:
				_weld_vertices = value;
				break;
			case CONVERT_BACK_UNITS:
				_convert_back_units = value;
				break;
			case USE_BREP_DATA:
				_use_brep_data = value;
				break;
			case FASTER_BOOLEANS:
				_faster_booleans = value;
				break;
			case SEW_SHELLS:
				_sew_shells = value;
				break;
			case DISABLE_OPENING_SUBTRACTIONS:
				_disable_opening_subtractions = value;
				break;
			case DISABLE_TRIANGULATION:
				_disable_triangulation = value;
				break;
			case APPLY_DEFAULT_MATERIALS:
				_apply_default_materials = value;
				break;
			case INCLUDE_CURVES:
				_include_curves = value;
				break;
			case EXCLUDE_SOLIDS_AND_SURFACES:
				_exclude_solids_and_surfaces = value;
				break;
			default: throw IfcParse::IfcException("Invalid IteratorSetting");
			}
		}
	};
	
	class ElementSettings : public IteratorSettings {
	private:
		double _unit_magnitude;
		std::string _element_type;
	public:
		ElementSettings(const IteratorSettings& settings,
			double unit_magnitude,
			const std::string& element_type)
			: IteratorSettings(settings)
			, _unit_magnitude(unit_magnitude)
			, _element_type(element_type)
		{}

		const double& unit_magnitude() const { return _unit_magnitude; }
		const std::string& element_type() const { return _element_type; }
	};

}

#endif