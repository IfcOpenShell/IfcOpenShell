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
	if (height < settings_.get<settings::Precision>().get()) {
		Logger::Message(Logger::LOG_ERROR, "Non-positive extrusion height encountered for:", inst);
		return nullptr;
	}

	taxonomy::direction3::ptr dir = taxonomy::cast<taxonomy::direction3>(map(inst->ExtrudedDirection()));
	Eigen::Affine3d af3d(Eigen::Translation3d(height * dir->ccomponents()));
	Eigen::Matrix4d end_profile = af3d.matrix();

	auto loft = taxonomy::make<taxonomy::loft>();
	loft->axis = nullptr;
	loft->children = {
		taxonomy::cast<taxonomy::face>(map(inst->SweptArea())),
		taxonomy::cast<taxonomy::face>(map(inst->EndSweptArea()))
	};

	if (!loft->children.back()->matrix) {
		loft->children.back()->matrix = taxonomy::make<taxonomy::matrix4>();
	}
	auto old = loft->children.back()->matrix->ccomponents();
	loft->children.back()->matrix->components() = old * end_profile;

	taxonomy::matrix4::ptr matrix;
	bool has_position = true;
#ifdef SCHEMA_IfcSweptAreaSolid_Position_IS_OPTIONAL
	has_position = inst->Position() != nullptr;
#endif
	if (has_position) {
		matrix = taxonomy::cast<taxonomy::matrix4>(map(inst->Position()));
	}
	
	loft->matrix = matrix;

	return loft;
}
#endif
