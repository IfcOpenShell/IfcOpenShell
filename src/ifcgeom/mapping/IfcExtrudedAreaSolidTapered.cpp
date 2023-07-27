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

#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

#ifdef SCHEMA_HAS_IfcExtrudedAreaSolidTapered

#define mapping POSTFIX_SCHEMA(mapping)
taxonomy::ptr mapping::map_impl(const IfcSchema::IfcExtrudedAreaSolidTapered* inst) {
	const double height = inst->Depth() * length_unit_;
	if (height < conv_settings_.getValue(ConversionSettings::GV_PRECISION)) {
		Logger::Message(Logger::LOG_ERROR, "Non-positive extrusion height encountered for:", inst);
		return nullptr;
	}

	taxonomy::direction3::ptr dir = taxonomy::cast<taxonomy::direction3>(map(inst->ExtrudedDirection()));
	Eigen::Affine3d af3d(Eigen::Translation3d(height * dir->ccomponents()));
	Eigen::Matrix4d end_profile = af3d.matrix();

	auto loft = taxonomy::make<taxonomy::loft>();
	loft->children = {
		taxonomy::cast<taxonomy::face>(map(inst->SweptArea())),
		taxonomy::cast<taxonomy::face>(map(inst->EndSweptArea()))
	};

	auto old = loft->children.back()->matrix->ccomponents();
	loft->children.back()->matrix->components() = old * end_profile;

	return loft;

	/*
	gp_Trsf trsf;
	bool has_position = true;
#ifdef SCHEMA_IfcSweptAreaSolid_Position_IS_OPTIONAL
	has_position = inst->Position() != nullptr;
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(inst->Position(), trsf);
	}

	gp_Dir dir;
	convert(inst->ExtrudedDirection(), dir);

	gp_Trsf end_profile;
	end_profile.SetTranslation(height * dir);

	TopoDS_Edge spine_edge = BRepBuilderAPI_MakeEdge(gp_Pnt(), gp_Pnt((height * dir).XYZ())).Edge();
	TopoDS_Wire wire = BRepBuilderAPI_MakeWire(spine_edge).Wire();

	shape.Nullify();

	TopExp_Explorer exp1(face1, TopAbs_WIRE);
	TopExp_Explorer exp2(face2, TopAbs_WIRE);

	TopoDS_Vertex v1, v2;
	TopExp::Vertices(wire, v1, v2);

	TopoDS_Shape shell;
	TopoDS_Compound compound;
	BRep_Builder compound_builder;

	for (; exp1.More() && exp2.More(); exp1.Next(), exp2.Next()) {
		const TopoDS_Wire& w1 = TopoDS::Wire(exp1.Current());
		const TopoDS_Wire& w2 = TopoDS::Wire(exp2.Current());

		BRepOffsetAPI_MakePipeShell builder(wire);
		builder.Add(w1, v1);
		builder.Add(w2.Moved(end_profile), v2);

		TopoDS_Shape result = builder.Shape();

		TopTools_ListOfShape li;
		util::shape_to_face_list(result, li);
		li.Append(BRepBuilderAPI_MakeFace(w1).Face().Reversed());
		li.Append(BRepBuilderAPI_MakeFace(w2).Face().Moved(end_profile));
		
		util::create_solid_from_faces(li, result, true);

		// @todo ugly hack

		// The reason for this distinction is that at this point of the loop we're not sure anymore
		// whether this was constructed from an inner or outer bound. So rather than iterating over
		// wires of `face1` and `face2` we should iterate over the faces and then properly check with
		// BRepTools::OuterBound().
		// Currently this distinction happens based on profile type which is not robust and probably
		// not complete.
		if (shell.IsNull()) {
			shell = result;
		} else if (inst->SweptArea()->declaration().is(IfcSchema::IfcCircleHollowProfileDef::Class()) ||
			inst->SweptArea()->declaration().is(IfcSchema::IfcRectangleHollowProfileDef::Class()) ||
			inst->SweptArea()->declaration().is(IfcSchema::IfcArbitraryProfileDefWithVoids::Class()))
		{
			// @todo properly check for failure and all.
			shell = BRepAlgoAPI_Cut(shell, result).Shape();
		} else {
			if (compound.IsNull()) {
				compound_builder.MakeCompound(compound);
				compound_builder.Add(compound, shell);
			}
			compound_builder.Add(compound, result);
		}
	}

	if (!compound.IsNull()) {
		shell = compound;
	}

	shape = shell;

	if (exp1.More() != exp2.More()) {
		Logger::Message(Logger::LOG_ERROR, "Inconsistent profiles encountered for:", l);
	}

	if (has_position && !shape.IsNull()) {
		// IfcSweptAreaSolid.Position (trsf) is an IfcAxis2Placement3D
		// and therefore has a unit scale factor
		shape.Move(trsf);
	}

	return !shape.IsNull();
	*/
}
#endif
