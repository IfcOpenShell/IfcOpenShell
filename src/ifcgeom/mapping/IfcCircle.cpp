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

#define ALMOST_ZERO 1.e-7;

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcCircle* inst) {
	const double r = inst->Radius() * length_unit_;
	if (r < settings_.get<settings::Precision>().get()) { 
		Logger::Message(Logger::LOG_ERROR, "Radius not greater than zero for:", inst);
		return nullptr;
	}

	IfcSchema::IfcAxis2Placement* placement = inst->Position();
	auto c = taxonomy::make<taxonomy::circle>();
	c->radius = r;
	c->matrix = taxonomy::cast<taxonomy::matrix4>(map(placement));
	return c;
}
