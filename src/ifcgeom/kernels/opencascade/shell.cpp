#include "OpenCascadeKernel.h"

#include "base_utils.h"

using namespace ifcopenshell::geometry;
using namespace ifcopenshell::geometry::kernels;
using namespace IfcGeom;
using namespace IfcGeom::util;

namespace {
	// @todo move into taxonomy;
	bool shell_polyhedral(const taxonomy::shell::ptr& sh) {
		for (auto& f : sh->children) {
			for (auto& w : f->children) {
				if (!w->is_polyhedron()) {
					return false;
				}
			}
			if (f->basis && f->basis->kind() != taxonomy::PLANE) {
				return false;
			}
		}
		return true;
	}
}

bool OpenCascadeKernel::convert(const taxonomy::shell::ptr l, TopoDS_Shape& shape) {
	std::unique_ptr<faceset_helper> helper_scope;
	if (shell_polyhedral(l)) {
		helper_scope.reset(new faceset_helper(this, l));
	}

	faceset_helper_ = helper_scope.get();

	double minimal_face_area = precision_ * precision_ * 0.5;

	double min_face_area = faceset_helper_
		? (faceset_helper_->epsilon() * faceset_helper_->epsilon() / 20.)
		: minimal_face_area;

	TopTools_ListOfShape face_list;
	for (auto& face : l->children) {
		bool success = false;
		TopoDS_Face occ_face;

		try {
			success = convert(face, occ_face);
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
			Logger::Message(Logger::LOG_WARNING, "Failed to convert face:", face->instance);
			continue;
		}

		if (occ_face.ShapeType() == TopAbs_COMPOUND) {
			TopoDS_Iterator face_it(occ_face, false);
			for (; face_it.More(); face_it.Next()) {
				if (face_it.Value().ShapeType() == TopAbs_FACE) {
					// This should really be the case. This is not asserted.
					const TopoDS_Face& triangle = TopoDS::Face(face_it.Value());
					if (face_area(triangle) > min_face_area) {
						face_list.Append(triangle);
					} else {
						Logger::Message(Logger::LOG_WARNING, "Degenerate face:", face->instance);
					}
				}
			}
		} else {
			if (face_area(occ_face) > min_face_area) {
				face_list.Append(occ_face);
			} else {
				Logger::Message(Logger::LOG_WARNING, "Degenerate face:", face->instance);
			}
		}
	}

	if (face_list.Extent() == 0) {
		return false;
	}

	// @todo
	// face_list.Extent() <= settings_.get<settings::MaxFacesToReorient>().get() &&

	if (!settings_.get<settings::ReorientShells>().get() || !create_solid_from_faces(face_list, shape, settings_.get<settings::Precision>().get())) {
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

bool OpenCascadeKernel::convert_impl(const taxonomy::shell::ptr shell, IfcGeom::ConversionResults& results) {
	TopoDS_Shape shape;
	if (!convert(shell, shape)) {
		return false;
	}
	results.emplace_back(ConversionResult(
		shell->instance->as<IfcUtil::IfcBaseEntity>()->id(),
		shell->matrix,
		new OpenCascadeShape(shape),
		shell->surface_style
	));
	return true;
}
