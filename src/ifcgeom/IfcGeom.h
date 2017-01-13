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

#ifndef IFCGEOM_H
#define IFCGEOM_H

#include <cmath>

static const double ALMOST_ZERO = 1.e-9;

template <typename T>
inline static bool ALMOST_THE_SAME(const T& a, const T& b, double tolerance=ALMOST_ZERO) {
	return fabs(a-b) < tolerance; 
}

#include "../ifcparse/IfcParse.h"
#include "../ifcparse/IfcUtil.h"

#include "../ifcgeom/ConversionResult.h"
#include "../ifcgeom/IfcGeomElement.h" 
#include "../ifcgeom/IfcGeomRepresentation.h" 
#include "../ifcgeom/IfcGeomShapeType.h"
#include "ifc_geom_api.h"

namespace IfcGeom {

class IFC_GEOM_API AbstractKernel {
private:

	double deflection_tolerance;
	double wire_creation_tolerance;
	double point_equality_tolerance;
	double max_faces_to_sew;
	double ifc_length_unit;
	double ifc_planeangle_unit;
	double modelling_precision;
	double dimensionality;

	std::map<int, SurfaceStyle> style_cache;

	const SurfaceStyle* internalize_surface_style(const std::pair<IfcSchema::IfcSurfaceStyle*, IfcSchema::IfcSurfaceStyleShading*>& shading_style);
public:
	AbstractKernel()
		: deflection_tolerance(0.001)
		, wire_creation_tolerance(0.0001)
		, point_equality_tolerance(0.00001)
		, max_faces_to_sew(-1.0)
		, ifc_length_unit(1.0)
		, ifc_planeangle_unit(-1.0)
		, modelling_precision(0.00001)
		, dimensionality(1.)
	{}

	AbstractKernel(const AbstractKernel& other) {
		*this = other;
	}

	AbstractKernel& operator=(const AbstractKernel& other) {
		setValue(GV_DEFLECTION_TOLERANCE,     other.getValue(GV_DEFLECTION_TOLERANCE));
		setValue(GV_WIRE_CREATION_TOLERANCE,  other.getValue(GV_WIRE_CREATION_TOLERANCE));
		setValue(GV_POINT_EQUALITY_TOLERANCE, other.getValue(GV_POINT_EQUALITY_TOLERANCE));
		setValue(GV_MAX_FACES_TO_SEW,         other.getValue(GV_MAX_FACES_TO_SEW));
		setValue(GV_LENGTH_UNIT,              other.getValue(GV_LENGTH_UNIT));
		setValue(GV_PLANEANGLE_UNIT,          other.getValue(GV_PLANEANGLE_UNIT));
		setValue(GV_PRECISION,                other.getValue(GV_PRECISION));
		setValue(GV_DIMENSIONALITY,           other.getValue(GV_DIMENSIONALITY));
		setValue(GV_DEFLECTION_TOLERANCE,     other.getValue(GV_DEFLECTION_TOLERANCE));
		return *this;
	}

	// Tolerances and settings for various geometrical operations:
	enum GeomValue {
		// Specifies the deflection of the mesher
		// Default: 0.001m / 1mm
		GV_DEFLECTION_TOLERANCE, 
		// Specifies the tolerance of the wire builder, most notably for trimmed curves
		// Defailt: 0.0001m / 0.1mm
		GV_WIRE_CREATION_TOLERANCE,
		// Specifies the minimal area of a face to be included in an IfcConnectedFaceset
		// Read-only
		GV_MINIMAL_FACE_AREA,
		// Specifies the treshold distance under which cartesian points are deemed equal
		// Default: 0.00001m / 0.01mm
		GV_POINT_EQUALITY_TOLERANCE,
		// Specifies maximum number of faces for a shell to be sewed. Sewing shells
		// that consist of many faces is really detrimental for the performance.
		// Default: 1000
		GV_MAX_FACES_TO_SEW,
		// The length unit used the creation of TopoDS_Shapes, primarily affects the
		// interpretation of IfcCartesianPoints and IfcVector magnitudes
		// DefaultL 1.0
		GV_LENGTH_UNIT,
		// The plane angle unit used for the creation of TopoDS_Shapes, primarily affects
		// the interpretation of IfcParamaterValues of IfcTrimmedCurves
		// Default: -1.0 (= not set, fist try degrees, then radians)
		GV_PLANEANGLE_UNIT,
		// The precision used in boolean operations, setting this value too low results
		// in artefacts and potentially modelling failures
		// Default: 0.00001 (obtained from IfcGeometricRepresentationContext if available)
		GV_PRECISION,
		// Whether to process shapes of type Face or higher (1) Wire or lower (-1) or all (0)
		GV_DIMENSIONALITY
	};

	IfcSchema::IfcSurfaceStyleShading* get_surface_style(IfcSchema::IfcRepresentationItem* item);
	const IfcSchema::IfcRepresentationItem* find_item_carrying_style(const IfcSchema::IfcRepresentationItem* item);
	
    void setValue(GeomValue var, double value);
	double getValue(GeomValue var) const;
	
	IfcSchema::IfcRelVoidsElement::list::ptr find_openings(IfcSchema::IfcProduct* product);
	IfcSchema::IfcRepresentation* find_representation(const IfcSchema::IfcProduct*, const std::string&);
	std::pair<std::string, double> initializeUnits(IfcSchema::IfcUnitAssignment*);
	IfcSchema::IfcObjectDefinition* get_decomposing_entity(IfcSchema::IfcProduct*);

	virtual bool is_identity_transform(IfcUtil::IfcBaseClass*) = 0;

	virtual IfcGeom::NativeElement<double>* create_brep_for_representation_and_product(
		const IteratorSettings&, IfcSchema::IfcRepresentation*, IfcSchema::IfcProduct*) = 0;

	virtual IfcGeom::NativeElement<double>* create_brep_for_processed_representation(
		const IteratorSettings&, IfcSchema::IfcRepresentation*, IfcSchema::IfcProduct*, IfcGeom::NativeElement<double>*) = 0;
	
	const SurfaceStyle* get_style(const IfcSchema::IfcRepresentationItem*);
	const SurfaceStyle* get_style(const IfcSchema::IfcMaterial*);

	static AbstractKernel* kernel_by_name(const std::string&);
	
	template <typename T> std::pair<IfcSchema::IfcSurfaceStyle*, T*> _get_surface_style(const IfcSchema::IfcStyledItem* si) {
#ifdef USE_IFC4
		IfcEntityList::ptr style_assignments = si->Styles();
		for (IfcEntityList::it kt = style_assignments->begin(); kt != style_assignments->end(); ++kt) {
			if (!(*kt)->is(IfcSchema::Type::IfcPresentationStyleAssignment)) {
				continue;
			}
			IfcSchema::IfcPresentationStyleAssignment* style_assignment = (IfcSchema::IfcPresentationStyleAssignment*) *kt;
#else
		IfcSchema::IfcPresentationStyleAssignment::list::ptr style_assignments = si->Styles();
		for (IfcSchema::IfcPresentationStyleAssignment::list::it kt = style_assignments->begin(); kt != style_assignments->end(); ++kt) {
			IfcSchema::IfcPresentationStyleAssignment* style_assignment = *kt;
#endif
			IfcEntityList::ptr styles = style_assignment->Styles();
			for (IfcEntityList::it lt = styles->begin(); lt != styles->end(); ++lt) {
				IfcUtil::IfcBaseClass* style = *lt;
				if (style->is(IfcSchema::Type::IfcSurfaceStyle)) {
					IfcSchema::IfcSurfaceStyle* surface_style = (IfcSchema::IfcSurfaceStyle*) style;
					if (surface_style->Side() != IfcSchema::IfcSurfaceSide::IfcSurfaceSide_NEGATIVE) {
						IfcEntityList::ptr styles_elements = surface_style->Styles();
						for (IfcEntityList::it mt = styles_elements->begin(); mt != styles_elements->end(); ++mt) {
							if ((*mt)->is(T::Class())) {
								return std::make_pair(surface_style, (T*) *mt);
							}
						}
					}
				}
			}
		}

		return std::make_pair<IfcSchema::IfcSurfaceStyle*, T*>(0,0);
	}

	template <typename T> std::pair<IfcSchema::IfcSurfaceStyle*, T*> get_surface_style(const IfcSchema::IfcRepresentationItem* representation_item) {
  		// For certain representation items, most notably boolean operands,
		// a style definition might reside on one of its operands.
		representation_item = find_item_carrying_style(representation_item);

		if (representation_item->as<IfcSchema::IfcStyledItem>()) {
			return _get_surface_style<T>(representation_item->as<IfcSchema::IfcStyledItem>());
		}
		IfcSchema::IfcStyledItem::list::ptr styled_items = representation_item->StyledByItem();
		if (styled_items->size()) {
			// StyledByItem is a SET [0:1] OF IfcStyledItem, so we return after the first IfcStyledItem:
			return _get_surface_style<T>(*styled_items->begin());
		}
		return std::make_pair<IfcSchema::IfcSurfaceStyle*, T*>(0,0);
	}

};

}
#endif
