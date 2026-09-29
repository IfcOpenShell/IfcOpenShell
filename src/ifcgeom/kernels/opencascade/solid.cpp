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

#include <BRepPrimAPI_MakeHalfSpace.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepPrimAPI_MakePrism.hxx>
#include <BRepAlgoAPI_Common.hxx>
#include <ShapeFix_Solid.hxx>
#include <BRepPrimAPI_MakeSphere.hxx>

using namespace ifcopenshell::geom;
using namespace ifcopenshell::geom::kernels;
using namespace ifcopenshell::geom::util;

bool open_cascade_kernel::convert(const taxonomy::solid::ptr solid, TopoDS_Shape& result) {
	TopoDS_Shape S;

	if (solid->instance.declaration().is("IfcHalfSpaceSolid")) {
		// halfspace
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
				prism.Move(trsf*down);

				halfspace = BRepAlgoAPI_Common(halfspace, prism);
			}
		}

		result = halfspace;
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

	for (auto& s : solid->children) {
		TopoDS_Shape shl;
		if (convert(s, shl)) {
			if (shl.ShapeType() == TopAbs_SHELL) {
				ShapeFix_Solid solid;
				S = solid.SolidFromShell(TopoDS::Shell(shl));
			} else if (solid->children.size() == 1) {
				S = shl;
			} else {
				throw std::runtime_error("Unexpected configuration of subshapes");
			}
		} else {
			logger_.warning("GEO", 201, "Ignored shell", s->instance);
		}
	}
	if (!S.IsNull()) {
		result = S;
	}
	return !result.IsNull();
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
