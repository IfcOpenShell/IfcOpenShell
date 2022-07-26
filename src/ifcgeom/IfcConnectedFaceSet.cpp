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

#include <TopoDS.hxx>
#include <TopoDS_Face.hxx>
#include "../ifcgeom/IfcGeom.h"
#include <memory>

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcConnectedFaceSet* l, TopoDS_Shape& shape) {
	std::unique_ptr<faceset_helper<>> helper_scope;

	IfcSchema::IfcCartesianPoint::list::ptr points = IfcParse::traverse((IfcUtil::IfcBaseClass*) l)->as<IfcSchema::IfcCartesianPoint>();
	std::vector<const IfcSchema::IfcCartesianPoint*> points_(points->begin(), points->end());

	IfcSchema::IfcPolyLoop::list::ptr loops = IfcParse::traverse((IfcUtil::IfcBaseClass*)l)->as<IfcSchema::IfcPolyLoop>();
	std::vector<const IfcSchema::IfcPolyLoop*> loops_(loops->begin(), loops->end());

	helper_scope.reset(new faceset_helper<>(
		this,
		points_,
		loops_,
		l->declaration().is(IfcSchema::IfcClosedShell::Class())
	));

	faceset_helper_ = helper_scope.get();

	IfcSchema::IfcFace::list::ptr faces = l->CfsFaces();

	double min_face_area = faceset_helper_
		? (faceset_helper_->epsilon() * faceset_helper_->epsilon() / 20.)
		: getValue(GV_MINIMAL_FACE_AREA);

	TopTools_ListOfShape face_list;
	for (IfcSchema::IfcFace::list::it it = faces->begin(); it != faces->end(); ++it) {
		bool success = false;
		TopoDS_Face face;
		
		try {
			success = convert_face(*it, face);
		} catch (const std::exception& e) {
			Logger::Error(e);
		} catch (const Standard_Failure& e) {
			if (e.GetMessageString() && strlen(e.GetMessageString())) {
				Logger::Error(e.GetMessageString());
			} else {
				Logger::Error("Unknown error creating face");
			}
		} catch (...) {
			Logger::Error("Unknown error creating face");
		}

		if (!success) {
			Logger::Message(Logger::LOG_WARNING, "Failed to convert face:", (*it));
			continue;
		}

		if (face.ShapeType() == TopAbs_COMPOUND) {
			TopoDS_Iterator face_it(face, false);
			for (; face_it.More(); face_it.Next()) {
				if (face_it.Value().ShapeType() == TopAbs_FACE) {
					// This should really be the case. This is not asserted.
					const TopoDS_Face& triangle = TopoDS::Face(face_it.Value());
					if (face_area(triangle) > min_face_area) {
						face_list.Append(triangle);
					} else {
						Logger::Message(Logger::LOG_WARNING, "Degenerate face:", (*it));
					}
				}
			}
		} else {
			if (face_area(face) > min_face_area) {
				face_list.Append(face);
			} else {
				Logger::Message(Logger::LOG_WARNING, "Degenerate face:", (*it));
			}
		}
	}

	if (face_list.Extent() == 0) {
		return false;
	}

	if (face_list.Extent() > getValue(GV_MAX_FACES_TO_ORIENT) || !create_solid_from_faces(face_list, shape)) {
		TopoDS_Compound compound;
		BRep_Builder builder;
		builder.MakeCompound(compound);
		
		TopTools_ListIteratorOfListOfShape face_iterator;
		for (face_iterator.Initialize(face_list); face_iterator.More(); face_iterator.Next()) {
			builder.Add(compound, face_iterator.Value());
		}
		shape = compound;
	}

	return true;
}
