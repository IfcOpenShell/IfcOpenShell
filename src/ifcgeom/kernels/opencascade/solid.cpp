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

#include "opencascade_kernel.h"
#include "boolean_utils.h"

#include <BRepPrimAPI_MakeHalfSpace.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepPrimAPI_MakePrism.hxx>
#include <BRepAlgoAPI_Common.hxx>
#include <BRepClass3d_SolidClassifier.hxx>
#include <BRepPrimAPI_MakeSphere.hxx>

using namespace ifcopenshell::geom;
using namespace ifcopenshell::geom::kernels;
using namespace ifcopenshell::geom::util;

TopoDS_Shape open_cascade_kernel::halfspace_solid(const taxonomy::solid::ptr& solid, const gp_Trsf& bound_correction) {
	if (solid->children.size() != 1) {
		throw std::runtime_error("Unexpected number of children on solid");
	}

	auto face = solid->children[0]->children[0];

	const auto& m = taxonomy::cast<taxonomy::plane>(face->basis)->matrix->ccomponents();
	gp_Pln pln(convert_xyz2<gp_Pnt>(m.col(3)), convert_xyz2<gp_Dir>(m.col(2)));
	const gp_Pnt pnt = pln.Location().Translated(face->orientation.value_or(false) ? pln.Axis().Direction() : -pln.Axis().Direction());
	TopoDS_Shape halfspace = BRepPrimAPI_MakeHalfSpace(BRepBuilderAPI_MakeFace(pln), pnt).Solid();

	if (!face->children.empty()) {
		TopoDS_Wire wire;
		gp_GTrsf gtrsf;

		if (convert((taxonomy::loop::ptr)face->children[0], wire) && wire.Closed() && convert(face->matrix, gtrsf)) {
			gp_Trsf trsf = gtrsf.Trsf();
			TopoDS_Shape prism = BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(wire), gp_Vec(0, 0, 200));
			gp_Trsf down; down.SetTranslation(gp_Vec(0, 0, -100.0));

			// `trsf` and `down` both have a unit scale factor
			prism.Move(bound_correction * trsf * down);

			halfspace = BRepAlgoAPI_Common(halfspace, prism);
		}
	}

	return halfspace;
}

bool open_cascade_kernel::convert(const taxonomy::solid::ptr solid, TopoDS_Shape& result) {
	if (solid->instance.declaration().is("IfcHalfSpaceSolid")) {
		result = halfspace_solid(solid, gp_Trsf());
		return true;
	} else if (solid->children.size() == 1
		&& solid->children[0]->children.size() == 1
		&& solid->children[0]->children[0]->basis
		&& solid->children[0]->children[0]->basis->kind() == taxonomy::SPHERE)
	{
		auto sphere = taxonomy::cast<taxonomy::sphere>(solid->children[0]->children[0]->basis);
		gp_GTrsf gtrsf;
		convert(sphere->matrix, gtrsf);
		BRepPrimAPI_MakeSphere builder(sphere->radius);
		auto s = builder.Solid();
		s.Move(gtrsf.Trsf());
		result = s;
		return true;
	}

    BRep_Builder builder;
    std::vector<TopoDS_Shape> boundaries;
    bool all_solids = true;
    for (auto& shell : solid->children) {
        TopoDS_Shape boundary;
        if (!convert(shell, boundary) || boundary.IsNull()) {
            logger_.warning("GEO", 201, "Failed to convert shell", shell->instance);
            return false;
        }
        if (boundary.ShapeType() == TopAbs_SHELL) {
            TopoDS_Solid shell_solid;
            builder.MakeSolid(shell_solid);
            builder.Add(shell_solid, boundary);
            boundary = shell_solid;
        }
        if (boundary.ShapeType() == TopAbs_SOLID) {
            // IFC identifies the external shell explicitly; all following shells are voids.
            BRepClass3d_SolidClassifier classifier(boundary);
            classifier.PerformInfinitePoint(settings_.get<settings::Precision>().get());
            const auto expected = boundaries.empty() ? TopAbs_OUT : TopAbs_IN;
            if (classifier.State() != TopAbs_OUT && classifier.State() != TopAbs_IN) {
                throw std::runtime_error("Unable to determine shell orientation");
            }
            if (classifier.State() != expected) {
                boundary.Reverse();
            }
        } else {
            all_solids = false;
            if (solid->children.size() > 1 && boundary.ShapeType() != TopAbs_COMPOUND) {
                throw std::runtime_error("Unexpected configuration of subshapes");
            }
        }
        boundaries.push_back(boundary);
    }
    if (boundaries.empty()) {
        return false;
    }
    if (boundaries.size() == 1) {
        result = boundaries.front();
    } else if (all_solids) {
        TopoDS_Solid assembled;
        builder.MakeSolid(assembled);
        for (const auto& boundary : boundaries) {
            for (TopoDS_Iterator shells(boundary); shells.More(); shells.Next()) {
                builder.Add(assembled, shells.Value());
            }
        }
        result = assembled;
    } else {
        TopoDS_Compound compound;
        builder.MakeCompound(compound);
        for (const auto& boundary : boundaries) {
            if (boundary.ShapeType() == TopAbs_COMPOUND) {
                builder.Add(compound, boundary);
            } else {
                // Keep one face compound per boundary when some shells remain unsewn.
                TopoDS_Compound faces;
                builder.MakeCompound(faces);
                for (TopExp_Explorer it(boundary, TopAbs_FACE); it.More(); it.Next()) {
                    builder.Add(faces, it.Current());
                }
                builder.Add(compound, faces);
            }
        }
        result = util::ensure_fit_for_subtraction(compound, settings_.get<settings::Precision>().get());
    }
    return true;
}

bool open_cascade_kernel::convert_impl(const taxonomy::solid::ptr solid, std::vector<ifcopenshell::geom::conversion_result>& results) {
    return handle_occt_exception([&]() -> bool {

	TopoDS_Shape shape;
	if (!convert(solid, shape)) {
		return false;
	}
	results.emplace_back(conversion_result(
		solid->instance.id(),
		solid->matrix,
		new open_cascade_shape(shape),
		solid->surface_style
	));
	return true;

	});
}
