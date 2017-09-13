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
#include <TopTools_ListOfShape.hxx>
#include <BOPAlgo_Operation.hxx>

#include "../ifcparse/IfcParse.h"
#include "../ifcparse/IfcBaseClass.h"

#include "../ifcgeom/IfcGeomElement.h" 
#include "../ifcgeom/IfcGeomRepresentation.h" 
#include "../ifcgeom/IfcRepresentationShapeItem.h"
#include "../ifcgeom/IfcGeomShapeType.h"
#include "ifc_geom_api.h"

// Define this in case you want to conserve memory usage at all cost. This has been
// benchmarked extensively: https://github.com/IfcOpenShell/IfcOpenShell/pull/47
// #define NO_CACHE

#ifdef NO_CACHE

#define IN_CACHE(T,E,t,e)
#define CACHE(T,E,e)

#else

#define IN_CACHE(T,E,t,e) std::map<int,t>::const_iterator it = cache.T.find(E->entity->id());\
if ( it != cache.T.end() ) { e = it->second; return true; }
#define CACHE(T,E,e) cache.T[E->entity->id()] = e;

#endif

namespace IfcGeom {

class IFC_GEOM_API Cache {
public:
#include "IfcRegisterCreateCache.h"
	std::map<int, TopoDS_Shape> Shape;
};

class IFC_GEOM_API Kernel {
private:

	double deflection_tolerance;
	double wire_creation_tolerance;
	double point_equality_tolerance;
	double max_faces_to_sew;
	double ifc_length_unit;
	double ifc_planeangle_unit;
	double modelling_precision;
	double dimensionality;

#ifndef NO_CACHE
	Cache cache;
#endif

	std::map<int, SurfaceStyle> style_cache;

	const SurfaceStyle* internalize_surface_style(const std::pair<IfcSchema::IfcSurfaceStyle*, IfcSchema::IfcSurfaceStyleShading*>& shading_style);

	 // For stopping PlacementRelTo recursion in convert(const IfcSchema::IfcObjectPlacement* l, gp_Trsf& trsf)
	IfcSchema::Type::Enum placement_rel_to;

public:
	Kernel()
		: deflection_tolerance(0.001)
		, wire_creation_tolerance(0.0001)
		, point_equality_tolerance(0.00001)
		, max_faces_to_sew(-1.0)
		, ifc_length_unit(1.0)
		, ifc_planeangle_unit(-1.0)
		, modelling_precision(0.00001)
		, dimensionality(1.)
		, placement_rel_to(IfcSchema::Type::UNDEFINED)
	{}

	Kernel(const Kernel& other) {
		*this = other;
	}

	Kernel& operator=(const Kernel& other) {
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
	
	bool convert_layerset(const IfcSchema::IfcProduct*, std::vector<Handle_Geom_Surface>&, std::vector<const SurfaceStyle*>&, std::vector<double>&);
	bool apply_layerset(const IfcRepresentationShapeItems&, const std::vector<Handle_Geom_Surface>&, const std::vector<const SurfaceStyle*>&, IfcRepresentationShapeItems&);
	bool apply_folded_layerset(const IfcRepresentationShapeItems&, const std::vector< std::vector<Handle_Geom_Surface> >&, const std::vector<const SurfaceStyle*>&, IfcRepresentationShapeItems&);
	bool fold_layers(const IfcSchema::IfcWall*, const IfcRepresentationShapeItems&, const std::vector<Handle_Geom_Surface>&, const std::vector<double>&, std::vector< std::vector<Handle_Geom_Surface> >&);

	bool split_solid_by_surface(const TopoDS_Shape&, const Handle_Geom_Surface&, TopoDS_Shape&, TopoDS_Shape&);
	bool split_solid_by_shell(const TopoDS_Shape&, const TopoDS_Shape& s, TopoDS_Shape&, TopoDS_Shape&);

#if OCC_VERSION_HEX < 0x60900
	bool boolean_operation(const TopoDS_Shape&, const TopTools_ListOfShape&, BOPAlgo_Operation, TopoDS_Shape&);
	bool boolean_operation(const TopoDS_Shape&, const TopoDS_Shape&, BOPAlgo_Operation, TopoDS_Shape&);
#else
	bool boolean_operation(const TopoDS_Shape&, const TopTools_ListOfShape&, BOPAlgo_Operation, TopoDS_Shape&, double fuzziness = -1.);
	bool boolean_operation(const TopoDS_Shape&, const TopoDS_Shape&, BOPAlgo_Operation, TopoDS_Shape&, double fuzziness = -1.);
#endif

	const Handle_Geom_Curve intersect(const Handle_Geom_Surface&, const Handle_Geom_Surface&);
	const Handle_Geom_Curve intersect(const Handle_Geom_Surface&, const TopoDS_Face&);
	const Handle_Geom_Curve intersect(const TopoDS_Face&, const Handle_Geom_Surface&);
	bool intersect(const Handle_Geom_Curve&, const Handle_Geom_Surface&, gp_Pnt&);
	bool intersect(const Handle_Geom_Curve&, const TopoDS_Face&, gp_Pnt&);
	bool intersect(const Handle_Geom_Curve&, const TopoDS_Shape&, std::vector<gp_Pnt>&);
	bool intersect(const Handle_Geom_Surface&, const TopoDS_Shape&, std::vector< std::pair<Handle_Geom_Surface, Handle_Geom_Curve> >&);
	bool closest(const gp_Pnt&, const std::vector<gp_Pnt>&, gp_Pnt&);
	bool project(const Handle_Geom_Curve&, const gp_Pnt&, gp_Pnt& p, double& u, double& d);
	bool project(const Handle_Geom_Surface&, const TopoDS_Shape&, double& u1, double& v1, double& u2, double& v2, double widen=0.1);
	static int count(const TopoDS_Shape&, TopAbs_ShapeEnum);

	bool find_wall_end_points(const IfcSchema::IfcWall*, gp_Pnt& start, gp_Pnt& end);

	IfcSchema::IfcSurfaceStyleShading* get_surface_style(IfcSchema::IfcRepresentationItem* item);
	const IfcSchema::IfcRepresentationItem* find_item_carrying_style(const IfcSchema::IfcRepresentationItem* item);
	bool create_solid_from_compound(const TopoDS_Shape& compound, TopoDS_Shape& solid);
	bool create_solid_from_faces(const TopTools_ListOfShape& face_list, TopoDS_Shape& solid);
	bool is_compound(const TopoDS_Shape& shape);
	bool is_convex(const TopoDS_Wire& wire);
	TopoDS_Shape halfspace_from_plane(const gp_Pln& pln,const gp_Pnt& cent);
	gp_Pln plane_from_face(const TopoDS_Face& face);
	gp_Pnt point_above_plane(const gp_Pln& pln, bool agree=true);
	const TopoDS_Shape& ensure_fit_for_subtraction(const TopoDS_Shape& shape, TopoDS_Shape& solid);
	bool profile_helper(int numVerts, double* verts, int numFillets, int* filletIndices, double* filletRadii, gp_Trsf2d trsf, TopoDS_Shape& face); 
	void apply_tolerance(TopoDS_Shape& s, double t);
	void setValue(GeomValue var, double value);
	double getValue(GeomValue var) const;
	bool fill_nonmanifold_wires_with_planar_faces(TopoDS_Shape& shape);
	void remove_duplicate_points_from_loop(TColgp_SequenceOfPnt& polygon, bool closed, double tol=-1.);
	void remove_collinear_points_from_loop(TColgp_SequenceOfPnt& polygon, bool closed, double tol=-1.);
	bool wire_to_sequence_of_point(const TopoDS_Wire&, TColgp_SequenceOfPnt&);
	void sequence_of_point_to_wire(const TColgp_SequenceOfPnt&, TopoDS_Wire&, bool closed);
	bool approximate_plane_through_wire(const TopoDS_Wire&, gp_Pln&);
	bool flatten_wire(TopoDS_Wire&);

	static double shape_volume(const TopoDS_Shape& s);
	static double face_area(const TopoDS_Face& f);

	static TopoDS_Shape apply_transformation(const TopoDS_Shape&, const gp_Trsf&);
	static TopoDS_Shape apply_transformation(const TopoDS_Shape&, const gp_GTrsf&);
	
	bool is_identity_transform(IfcUtil::IfcBaseClass*);

	IfcSchema::IfcRelVoidsElement::list::ptr find_openings(IfcSchema::IfcProduct* product);

	IfcSchema::IfcRepresentation* find_representation(const IfcSchema::IfcProduct*, const std::string&);

	std::pair<std::string, double> initializeUnits(IfcSchema::IfcUnitAssignment*);

    static IfcSchema::IfcObjectDefinition* get_decomposing_entity(IfcSchema::IfcProduct*);

    static std::map<std::string, IfcSchema::IfcPresentationLayerAssignment*> get_layers(IfcSchema::IfcProduct* prod);

	template <typename P>
    IfcGeom::BRepElement<P>* create_brep_for_representation_and_product(
        const IteratorSettings&, IfcSchema::IfcRepresentation*, IfcSchema::IfcProduct*);

	template <typename P>
    IfcGeom::BRepElement<P>* create_brep_for_processed_representation(
        const IteratorSettings&, IfcSchema::IfcRepresentation*, IfcSchema::IfcProduct*, IfcGeom::BRepElement<P>*);
	
	const SurfaceStyle* get_style(const IfcSchema::IfcRepresentationItem*);
	const SurfaceStyle* get_style(const IfcSchema::IfcMaterial*);
	
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

	void purge_cache() { 
		// Rather hack-ish, but a stopgap solution to keep memory under control
		// for large files. SurfaceStyles need to be kept at all costs, as they
		// are read later on when serializing Collada files.
#ifndef NO_CACHE
		cache = Cache(); 
#endif
	}

	void set_conversion_placement_rel_to(IfcSchema::Type::Enum type);

#include "IfcRegisterGeomHeader.h"

};

IFC_GEOM_API IfcSchema::IfcProductDefinitionShape* tesselate(const TopoDS_Shape& shape, double deflection);
IFC_GEOM_API IfcSchema::IfcProductDefinitionShape* serialise(const TopoDS_Shape& shape, bool advanced);

}
#endif
