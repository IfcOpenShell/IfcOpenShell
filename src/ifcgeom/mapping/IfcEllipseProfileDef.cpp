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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcEllipseProfileDef* inst) {
	double rx = inst->SemiAxis1() * length_unit_;
	double ry = inst->SemiAxis2() * length_unit_;
	const double tol = settings_.get<settings::Precision>().get();
	if (rx < tol || ry < tol) {
		Logger::Message(Logger::LOG_ERROR, "Radius not greater than zero for:", inst);
		return nullptr;
	}

	const bool rotated = ry > rx;

	taxonomy::matrix4::ptr m4;
	bool has_position = true;
#ifdef SCHEMA_IfcParameterizedProfileDef_Position_IS_OPTIONAL
	has_position = !!inst->Position();
#endif
	if (has_position) {
		m4 = taxonomy::cast<taxonomy::matrix4>(map(inst->Position()));
	}

	if (ry > rx) {
		// @todo is a copy necesary here or can this be done in place?
		auto m4_copy = *m4;
		m4->components() <<
			-m4_copy.components().col(1),
			m4_copy.components().col(0),
			m4_copy.components().col(2),
			m4_copy.components().col(3);
		std::swap(rx, ry);
	}

	auto fc = taxonomy::make<taxonomy::face>();
	auto lp = taxonomy::make<taxonomy::loop>();
	auto ed = taxonomy::make<taxonomy::edge>();
	auto el = taxonomy::make<taxonomy::ellipse>();
	el->radius = rx;
	el->radius2 = ry;
	ed->basis = el;
	lp->children.push_back(ed);
	fc->children.push_back(lp);
	fc->matrix = m4;
	return fc;
}
