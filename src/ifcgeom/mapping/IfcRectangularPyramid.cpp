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

taxonomy::item* mapping::map_impl(const IfcSchema::IfcRectangularPyramid* inst) {
	const double dx = inst->XLength() * length_unit_;
	const double dy = inst->YLength() * length_unit_;
	const double dz = inst->Height() * length_unit_;

	auto solid = new taxonomy::solid;
	auto shell = new taxonomy::shell;
	solid->children.push_back(shell);

	// Base
	{
		auto face = new taxonomy::face;
		auto loop = new taxonomy::loop;
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3, 4> points{
			taxonomy::point3(0, 0, 0),
			taxonomy::point3(dx, 0, 0),
			taxonomy::point3(dx, dy, 0),
			taxonomy::point3(0, dy, 0)
		};

		loop->children.push_back(new taxonomy::edge(points[0], points[1]));
		loop->children.push_back(new taxonomy::edge(points[1], points[2]));
		loop->children.push_back(new taxonomy::edge(points[2], points[3]));
		loop->children.push_back(new taxonomy::edge(points[3], points[0]));
	}

	// Lateral faces
	{
		auto face = new taxonomy::face;
		auto loop = new taxonomy::loop;
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3, 3> points{
			taxonomy::point3(0, 0, 0),
			taxonomy::point3(0, dy, 0),
			taxonomy::point3(0.5*dx, 0.5*dy, dz)
		};

		loop->children.push_back(new taxonomy::edge(points[0], points[1]));
		loop->children.push_back(new taxonomy::edge(points[1], points[2]));
		loop->children.push_back(new taxonomy::edge(points[2], points[0]));
	}

	{
		auto face = new taxonomy::face;
		auto loop = new taxonomy::loop;
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3, 3> points{
			taxonomy::point3(0, dy, 0),
			taxonomy::point3(dx, dy, 0),
			taxonomy::point3(0.5*dx, 0.5*dy, dz)
		};

		loop->children.push_back(new taxonomy::edge(points[0], points[1]));
		loop->children.push_back(new taxonomy::edge(points[1], points[2]));
		loop->children.push_back(new taxonomy::edge(points[2], points[0]));
	}

	{
		auto face = new taxonomy::face;
		auto loop = new taxonomy::loop;
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3, 3> points{
			taxonomy::point3(dx, dy, 0),
			taxonomy::point3(dx, 0, 0),
			taxonomy::point3(0.5*dx, 0.5*dy, dz)
		};

		loop->children.push_back(new taxonomy::edge(points[0], points[1]));
		loop->children.push_back(new taxonomy::edge(points[1], points[2]));
		loop->children.push_back(new taxonomy::edge(points[2], points[0]));
	}

	{
		auto face = new taxonomy::face;
		auto loop = new taxonomy::loop;
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3, 3> points{
			taxonomy::point3(dx, 0, 0),
			taxonomy::point3(0, 0, 0),
			taxonomy::point3(0.5*dx, 0.5*dy, dz)
		};

		loop->children.push_back(new taxonomy::edge(points[0], points[1]));
		loop->children.push_back(new taxonomy::edge(points[1], points[2]));
		loop->children.push_back(new taxonomy::edge(points[2], points[0]));
	}

	return solid;
}
