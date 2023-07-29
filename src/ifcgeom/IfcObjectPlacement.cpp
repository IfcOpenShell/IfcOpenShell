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

#include "../ifcgeom/IfcGeom.h"

#include <gp_Trsf.hxx>
#include <Geom_OffsetCurve.hxx>
#include <GeomAPI_ExtremaCurveCurve.hxx>

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcObjectPlacement* l, gp_Trsf& trsf) {
	IN_CACHE(IfcObjectPlacement, l, gp_Trsf, trsf);

	IfcSchema::IfcLocalPlacement const* current;
	IfcSchema::IfcGridPlacement const* gridp;

	if ((current = l->as<IfcSchema::IfcLocalPlacement>())) {
		for (;;) {

			gp_Trsf trsf2;
			IfcSchema::IfcAxis2Placement* relplacement = current->RelativePlacement();
			if (relplacement->as<IfcSchema::IfcAxis2Placement3D>()) {
				IfcGeom::Kernel::convert(relplacement->as<IfcSchema::IfcAxis2Placement3D>(), trsf2);
				trsf.PreMultiply(trsf2);
			}

			if (current->PlacementRelTo()) {
				IfcSchema::IfcObjectPlacement* parent = current->PlacementRelTo();

				bool parent_placement_ignored = false;
				if (placement_rel_to_type_ || placement_rel_to_instance_) {
					IfcSchema::IfcProduct::list::ptr parent_places = parent->PlacesObject();
					for (auto iter = parent_places->begin(); iter != parent_places->end(); ++iter) {
						if ((placement_rel_to_type_ && (*iter)->declaration().is(*placement_rel_to_type_)) ||
							(placement_rel_to_instance_ && (*iter)->as<IfcUtil::IfcBaseEntity>() == placement_rel_to_instance_)) {
							parent_placement_ignored = true;
						}
					}
				}

				if (parent_placement_ignored) {
					// The parent placement of the current is a placement for a type that is
					// being ignored (Site or Building) or it is the host element of an opening.
					break;
				} else if (parent->declaration().is(IfcSchema::IfcLocalPlacement::Class())) {
					// Keep processing parent placements
					current = current->PlacementRelTo()->as<IfcSchema::IfcLocalPlacement>();
				} else {
					// This is the root placement (typically Site).
					break;
				}
			} else {
				break;
			}
		}
	} else if (gridp = l->as<IfcSchema::IfcGridPlacement>()) {
		gp_Trsf grid_position;

		auto axes = gridp->PlacementLocation()->IntersectingAxes();
		auto offsets = gridp->PlacementLocation()->OffsetDistances();
		Handle(Geom_Curve) c1, c2;
		std::unique_ptr<GeomAPI_ExtremaCurveCurve> ecc;

#ifdef SCHEMA_IfcObjectPlacement_HAS_PlacementRelTo
		// From 4.3 onwards the parent grid placement is directly referenced
		// in the schema to translate the grid axes to world coords
		convert(l->PlacementRelTo(), grid_position);
#else
		IfcSchema::IfcGrid* grid = nullptr;
		auto grids = (*axes->begin())->data().file->getInverse<IfcSchema::IfcGrid>((*axes->begin())->data().id(), -1);
		if (grids && grids->size()) {
			grid = *grids->begin();
			if (grid->ObjectPlacement()) {
				convert(grid->ObjectPlacement(), grid_position);
			}
		}
#endif

		auto get_point = [this, &c1, &c2, &ecc](IfcSchema::IfcVirtualGridIntersection const* x, gp_Pnt& P) {
			auto axes = x->IntersectingAxes();
			auto offsets = x->OffsetDistances();

			if (axes->size() != 2) {
				Logger::Message(Logger::LOG_WARNING, "Unexpected grid axes count:" + std::to_string(axes->size()), x);
				return false;
			}
			if (offsets.size() != 3) {
				Logger::Message(Logger::LOG_WARNING, "Unexpected offset count:" + std::to_string(offsets.size()), x);
				return false;
			}
			auto first = *axes->begin();
			auto second = *++axes->begin();
			TopoDS_Wire w;
			// Might display a lot of 'No operation defined for ...' messages
			if (!convert_curve(first->AxisCurve(), c1)) {
				if (!convert_wire(first->AxisCurve(), w)) {
					return false;
				}
				double a, b;
				c1 = BRep_Tool::Curve(TopoDS::Edge(TopoDS_Iterator(w).Value()), a, b);
			}
			if (!convert_curve(second->AxisCurve(), c2)) {
				if (!convert_wire(second->AxisCurve(), w)) {
					return false;
				}
				double a, b;
				c2 = BRep_Tool::Curve(TopoDS::Edge(TopoDS_Iterator(w).Value()), a, b);
			}
			if (std::fabs(offsets[0]) > getValue(GV_PRECISION)) {
				c1 = new Geom_OffsetCurve(c1, offsets[0], gp::DZ());
			}
			if (std::fabs(offsets[1]) > getValue(GV_PRECISION)) {
				c2 = new Geom_OffsetCurve(c2, offsets[1], gp::DZ());
			}
			ecc.reset(new GeomAPI_ExtremaCurveCurve(c1, c2));
			gp_Pnt pp1, pp2;
			ecc->Points(1, pp1, pp2);
			if (pp1.Distance(pp2) > getValue(GV_PRECISION)) {
				Logger::Message(Logger::LOG_WARNING, "No axis intersection:", x);
				return false;
			}
			P = pp1;
			return true;
		};

		gp_Pnt origin;
		if (!get_point(gridp->PlacementLocation(), origin)) {
			return false;
		}

		gp_Vec V;
		gp_Dir D;
		if (gridp->PlacementRefDirection()) {
			IfcSchema::IfcDirection const* dir;
			IfcSchema::IfcVirtualGridIntersection const* refx;

			if ((dir = gridp->PlacementRefDirection()->as<IfcSchema::IfcDirection>())) {
				if (!convert(dir, D)) {
					return false;
				}
			} else if ((refx = gridp->PlacementRefDirection()->as<IfcSchema::IfcVirtualGridIntersection>())) {
				gp_Pnt P;
				if (!get_point(refx, P)) {
					return false;
				}
				V = P.XYZ() - origin.XYZ();
				if (V.Magnitude() > 1.e-9) {
					D = V;
				} else {
					Logger::Message(Logger::LOG_ERROR, "Unable to obtain ref direction:", l);
					return false;
				}
			}
		} else {
			gp_Pnt tmp_;
			double u1, u2;
			ecc->Parameters(1, u1, u2);

			c1->D1(u1, tmp_, V);
			if (V.Magnitude() > 1.e-9) {
				D = V;
			} else {
				Logger::Message(Logger::LOG_ERROR, "Unable to obtain ref direction:", l);
				return false;
			}
		}

		// Can be applied post hoc because z component of offsets for origin
		// and ref direction should be sme.
		origin.SetZ(origin.Z() + offsets[2]);

		gp_Ax2 ax(origin, gp::DZ(), D);
		trsf.SetTransformation(ax, gp::XOY());

		trsf.PreMultiply(grid_position);
	} else {
		Logger::Message(Logger::LOG_ERROR, "Unsupported IfcObjectPlacement:", l);
		return false;
	}

	trsf.PreMultiply(offset_and_rotation);
	
	CACHE(IfcObjectPlacement,l,trsf)
	return true;
}
