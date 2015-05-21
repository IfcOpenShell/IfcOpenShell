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

#define ALMOST_ZERO (1e-9)
#define ALMOST_THE_SAME(a,b) (fabs(a-b) < ALMOST_ZERO)

#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <Geom_Curve.hxx>
#include <gp_Pln.hxx>
#include <TColgp_SequenceOfPnt.hxx>

#include "../ifcparse/IfcParse.h"
#include "../ifcparse/IfcUtil.h"

#include "../ifcgeom/IfcGeomElement.h" 
#include "../ifcgeom/IfcGeomRepresentation.h" 
#include "../ifcgeom/IfcRepresentationShapeItem.h"
#include "../ifcgeom/IfcGeomShapeType.h"

#define IN_CACHE(T,E,t,e) std::map<int,t>::const_iterator it = cache.T.find(E->entity->id());\
if ( it != cache.T.end() ) { e = it->second; return true; }
#define CACHE(T,E,e) cache.T[E->entity->id()] = e;

namespace IfcGeom {

class Cache {
public:
#include "IfcRegisterCreateCache.h"
	std::map<int, SurfaceStyle> Style;
	std::map<int, TopoDS_Shape> Shape;
};

class Kernel {
private:
	Cache cache;
public:
	// Tolerances and settings for various geometrical operations:
	enum GeomValue {
		// Specifies the deflection of the mesher
		// Default: 0.001m / 1mm
		GV_DEFLECTION_TOLERANCE, 
		// Specifies the tolerance of the wire builder, most notably for trimmed curves
		// Defailt: 0.0001m / 0.1mm
		GV_WIRE_CREATION_TOLERANCE,
		// Specifies the minimal area of a face to be included in an IfcConnectedFaceset
		// Default: 0.000001m 0.01cm2
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

	bool convert_wire_to_face(const TopoDS_Wire& wire, TopoDS_Face& face);
	bool convert_curve_to_wire(const Handle(Geom_Curve)& curve, TopoDS_Wire& wire);
	bool convert_shapes(const IfcUtil::IfcBaseClass* L, IfcRepresentationShapeItems& result);
	IfcGeom::ShapeType shape_type(const IfcUtil::IfcBaseClass* L);
	bool convert_shape(const IfcUtil::IfcBaseClass* L, TopoDS_Shape& result);
	bool flatten_shape_list(const IfcGeom::IfcRepresentationShapeItems& shapes, TopoDS_Shape& result, bool fuse);
	bool convert_wire(const IfcUtil::IfcBaseClass* L, TopoDS_Wire& result);
	bool convert_curve(const IfcUtil::IfcBaseClass* L, Handle(Geom_Curve)& result);
	bool convert_face(const IfcUtil::IfcBaseClass* L, TopoDS_Shape& result);
	bool convert_openings(const IfcSchema::IfcProduct* entity, const IfcSchema::IfcRelVoidsElement::list::ptr& openings, const IfcRepresentationShapeItems& entity_shapes, const gp_Trsf& entity_trsf, IfcRepresentationShapeItems& cut_shapes);
	bool convert_openings_fast(const IfcSchema::IfcProduct* entity, const IfcSchema::IfcRelVoidsElement::list::ptr& openings, const IfcRepresentationShapeItems& entity_shapes, const gp_Trsf& entity_trsf, IfcRepresentationShapeItems& cut_shapes);
	IfcSchema::IfcSurfaceStyleShading* get_surface_style(IfcSchema::IfcRepresentationItem* item);
	bool create_solid_from_compound(const TopoDS_Shape& compound, TopoDS_Shape& solid);
	bool is_compound(const TopoDS_Shape& shape);
	bool is_convex(const TopoDS_Wire& wire);
	TopoDS_Shape halfspace_from_plane(const gp_Pln& pln,const gp_Pnt& cent);
	gp_Pln plane_from_face(const TopoDS_Face& face);
	gp_Pnt point_above_plane(const gp_Pln& pln, bool agree=true);
	const TopoDS_Shape& ensure_fit_for_subtraction(const TopoDS_Shape& shape, TopoDS_Shape& solid);
	bool profile_helper(int numVerts, double* verts, int numFillets, int* filletIndices, double* filletRadii, gp_Trsf2d trsf, TopoDS_Shape& face); 
	double shape_volume(const TopoDS_Shape& s);
	double face_area(const TopoDS_Face& f);
	void apply_tolerance(TopoDS_Shape& s, double t);
	void setValue(GeomValue var, double value);
	double getValue(GeomValue var);
	bool fill_nonmanifold_wires_with_planar_faces(TopoDS_Shape& shape);
	void remove_redundant_points_from_loop(TColgp_SequenceOfPnt& polygon, bool closed, double tol=-1.);

	std::pair<std::string, double> initializeUnits(IfcSchema::IfcUnitAssignment*);

	IfcSchema::IfcObjectDefinition* get_decomposing_entity(IfcSchema::IfcProduct*);

	template <typename P>
	IfcGeom::BRepElement<P>* create_brep_for_representation_and_product(const IteratorSettings&, IfcSchema::IfcRepresentation*, IfcSchema::IfcProduct*);

	const SurfaceStyle* get_style(const IfcSchema::IfcRepresentationItem* representation_item);
	
	template <typename T> std::pair<IfcSchema::IfcSurfaceStyle*, T*> get_surface_style(const IfcSchema::IfcRepresentationItem* representation_item) {
		IfcSchema::IfcStyledItem::list::ptr styled_items = representation_item->StyledByItem();
		for (IfcSchema::IfcStyledItem::list::it jt = styled_items->begin(); jt != styled_items->end(); ++jt) {
#ifdef USE_IFC4
			IfcEntityList::ptr style_assignments = (*jt)->Styles();
			for (IfcEntityList::it kt = style_assignments->begin(); kt != style_assignments->end(); ++kt) {
				if (!(*kt)->is(IfcSchema::Type::IfcPresentationStyleAssignment)) {
					continue;
				}
				IfcSchema::IfcPresentationStyleAssignment* style_assignment = (IfcSchema::IfcPresentationStyleAssignment*) *kt;
#else
			IfcSchema::IfcPresentationStyleAssignment::list::ptr style_assignments = (*jt)->Styles();
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

			// StyledByItem is a SET [0:1] OF IfcStyledItem, so we
			// break after encountering the first IfcStyledItem
			break;
		}

		return std::make_pair<IfcSchema::IfcSurfaceStyle*, T*>(0,0);
	}

#include "IfcRegisterGeomHeader.h"

};

IfcSchema::IfcProductDefinitionShape* tesselate(TopoDS_Shape& shape, double deflection, IfcEntityList::ptr es);

}
#endif
