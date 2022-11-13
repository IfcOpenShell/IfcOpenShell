#include "base_utils.h"

#include <TopTools_IndexedMapOfShape.hxx>
#include <TopExp.hxx>
#include <TopExp_Explorer.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Vertex.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>

// For axis placements detect equality early in order for the
// relatively computionaly expensive gp_Trsf calculation to be skipped
bool IfcGeom::util::axis_equal(const gp_Ax3 & a, const gp_Ax3 & b, double tolerance) {
	if (!a.Location().IsEqual(b.Location(), tolerance)) return false;
	// Note that the tolerance below is angular, above is linear. Since architectural
	// objects are about 1m'ish in scale, it should be somewhat equivalent. Besides,
	// this is mostly a filter for NULL or default values in the placements.
	if (!a.Direction().IsEqual(b.Direction(), tolerance)) return false;
	if (!a.XDirection().IsEqual(b.XDirection(), tolerance)) return false;
	if (!a.YDirection().IsEqual(b.YDirection(), tolerance)) return false;
	return true;
}

bool IfcGeom::util::axis_equal(const gp_Ax2d & a, const gp_Ax2d & b, double tolerance) {
	if (!a.Location().IsEqual(b.Location(), tolerance)) return false;
	if (!a.Direction().IsEqual(b.Direction(), tolerance)) return false;
	return true;
}

int IfcGeom::util::count(const TopoDS_Shape& s, TopAbs_ShapeEnum t, bool unique) {
	if (unique) {
		TopTools_IndexedMapOfShape map;
		TopExp::MapShapes(s, t, map);
		return map.Extent();
	} else {
		int i = 0;
		TopExp_Explorer exp(s, t);
		for (; exp.More(); exp.Next()) {
			++i;
		}
		return i;
	}
}


int IfcGeom::util::surface_genus(const TopoDS_Shape& s) {
	int nv = count(s, TopAbs_VERTEX, true);
	int ne = count(s, TopAbs_EDGE, true);
	int nf = count(s, TopAbs_FACE, true);

	const int euler = nv - ne + nf;
	const int genus = (2 - euler) / 2;

	return genus;
}

bool IfcGeom::util::is_manifold(const TopoDS_Shape& a) {
	if (a.ShapeType() == TopAbs_COMPOUND || a.ShapeType() == TopAbs_SOLID) {
		TopoDS_Iterator it(a);
		for (; it.More(); it.Next()) {
			if (!is_manifold(it.Value())) {
				return false;
			}
		}
		return true;
	} else {
		TopTools_IndexedDataMapOfShapeListOfShape map;
		TopExp::MapShapesAndAncestors(a, TopAbs_EDGE, TopAbs_FACE, map);

		for (int i = 1; i <= map.Extent(); ++i) {
			const TopoDS_Edge& e = TopoDS::Edge(map.FindKey(i));

			TopoDS_Vertex v0, v1;
			TopExp::Vertices(e, v0, v1);
			const bool degenerate = !v0.IsNull() && !v1.IsNull() && v0.IsSame(v1);

			if (degenerate) {
				continue;
			}

			if (map.FindFromIndex(i).Extent() != 2) {
				return false;
			}
		}

		return true;
	}
}


bool IfcGeom::util::is_nested_compound_of_solid(const TopoDS_Shape& s, int depth) {
	if (s.ShapeType() == TopAbs_COMPOUND) {
		TopoDS_Iterator it(s);
		for (; it.More(); it.Next()) {
			if (!is_nested_compound_of_solid(it.Value(), depth + 1)) {
				return false;
			}
		}
		return true;
	} else if (s.ShapeType() == TopAbs_SOLID) {
		return depth > 0;
	} else {
		return false;
	}
}

namespace {
	template <typename T> struct dimension_count {};
	template <>           struct dimension_count <gp_Trsf2d > { static const int n = 2; };
	template <>           struct dimension_count <gp_GTrsf2d> { static const int n = 2; };
	template <>           struct dimension_count < gp_Trsf  > { static const int n = 3; };
	template <>           struct dimension_count < gp_GTrsf > { static const int n = 3; };

	template <typename T>
	bool is_identity_helper(const T& t, double tolerance) {
		// Note the {1, n+1} range due to Open Cascade's 1-based indexing
		// Note the {1, n+2} range due to the translation part of the matrix
		for (int i = 1; i < dimension_count<T>::n + 2; ++i) {
			for (int j = 1; j < dimension_count<T>::n + 1; ++j) {
				const double iden_value = i == j ? 1. : 0.;
				const double trsf_value = t.Value(j, i);
				if (fabs(trsf_value - iden_value) > tolerance) {
					return false;
				}
			}
		}
		return true;
	}
}

bool IfcGeom::util::is_identity(const gp_Trsf2d& t, double tolerance) {
	return is_identity_helper(t, tolerance);
}

bool IfcGeom::util::is_identity(const gp_GTrsf2d& t, double tolerance) {
	return is_identity_helper(t, tolerance);
}

bool IfcGeom::util::is_identity(const gp_Trsf& t, double tolerance) {
	return is_identity_helper(t, tolerance);
}

bool IfcGeom::util::is_identity(const gp_GTrsf& t, double tolerance) {
	return is_identity_helper(t, tolerance);
}

gp_Trsf IfcGeom::util::combine_offset_and_rotation(const gp_Vec & offset, const gp_Quaternion & rotation) {
	auto offset_transform = gp_Trsf{};
	offset_transform.SetTranslation(offset);

	auto rotation_transform = gp_Trsf{};
	rotation_transform.SetRotation(rotation);

	return rotation_transform * offset_transform;
}
