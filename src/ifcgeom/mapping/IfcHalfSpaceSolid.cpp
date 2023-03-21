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

taxonomy::item* mapping::map_impl(const IfcSchema::IfcHalfSpaceSolid* inst) {
	IfcSchema::IfcSurface* surface = inst->BaseSurface();
	if (!surface->declaration().is(IfcSchema::IfcPlane::Class())) {
		Logger::Message(Logger::LOG_ERROR, "Unsupported BaseSurface:", surface);
		return nullptr;
	}
	auto p = new taxonomy::plane;
	p->matrix = as<taxonomy::matrix4>(map(((IfcSchema::IfcPlane*)surface)->Position()));
	auto f = new taxonomy::face;
	f->orientation.reset(!inst->AgreementFlag());
	f->basis = p;
	auto s = new taxonomy::solid;
	s->children.push_back(f);
	return s;
}
