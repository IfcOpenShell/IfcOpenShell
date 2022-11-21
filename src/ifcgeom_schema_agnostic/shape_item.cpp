#include "IfcRepresentationShapeItem.h"

#include "boolean_utils.h"
#include "base_utils.h"

#include <TopoDS_Compound.hxx>
#include <BRep_Builder.hxx>
#include <BRepAlgoAPI_Fuse.hxx>
#include <ShapeFix_Shape.hxx>
#include <BRepCheck_Analyzer.hxx>

bool IfcGeom::util::flatten_shape_list(const IfcGeom::IfcRepresentationShapeItems& shapes, TopoDS_Shape& result, bool fuse, double tol) {
	TopoDS_Compound compound;
	BRep_Builder builder;
	builder.MakeCompound(compound);

	result = TopoDS_Shape();

	for (IfcGeom::IfcRepresentationShapeItems::const_iterator it = shapes.begin(); it != shapes.end(); ++it) {
		TopoDS_Shape merged;
		const TopoDS_Shape& s = it->Shape();
		if (fuse) {
			util::ensure_fit_for_subtraction(s, merged, tol);
		} else {
			merged = s;
		}
		const gp_GTrsf& trsf = it->Placement();
		const TopoDS_Shape moved_shape = util::apply_transformation(merged, trsf);

		if (shapes.size() == 1) {
			result = moved_shape;
			return true;
		}

		if (fuse) {
			if (result.IsNull()) {
				result = moved_shape;
			} else {
				BRepAlgoAPI_Fuse brep_fuse(result, moved_shape);
				if (brep_fuse.IsDone()) {
					TopoDS_Shape fused = brep_fuse;

					ShapeFix_Shape fix(result);
					fix.Perform();
					result = fix.Shape();

					bool is_valid = BRepCheck_Analyzer(result).IsValid() != 0;
					if (is_valid) {
						result = fused;
					}
				}
			}
		} else {
			builder.Add(compound, moved_shape);
		}
	}

	if (!fuse) {
		result = compound;
	}

	const bool success = !result.IsNull();
	return success;
}
