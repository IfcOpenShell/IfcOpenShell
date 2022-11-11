#include "face_definition.h"

#include <TopoDS.hxx>
#include <Geom_Line.hxx>
#include <BRep_Tool.hxx>
#include <TopoDS_Iterator.hxx>

/* Returns whether wire conforms to a polyhedron, i.e. only edges with linear curves*/
bool ifcopenshell::geometry::util::is_polyhedron(const TopoDS_Wire& wire) {
	double a, b;
	TopLoc_Location l;

	TopoDS_Iterator it(wire, false, false);
	for (; it.More(); it.Next()) {
		auto crv = BRep_Tool::Curve(TopoDS::Edge(it.Value()), l, a, b);
		if (!crv || crv->DynamicType() != STANDARD_TYPE(Geom_Line)) {
			return false;
		}
	}

	return true;
}

/* Returns whether wire conforms to a polyhedron, i.e. only edges with linear curves*/
bool ifcopenshell::geometry::util::is_polyhedron(const taxonomy::loop* wire) {
	for (auto& edge : wire->children_as<taxonomy::edge>()) {
		if (edge->basis) {
			if (edge->basis->kind() != taxonomy::LINE) {
				return false;
			}
		}
	}
	return true;
}