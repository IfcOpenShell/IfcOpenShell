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

namespace IfcGeomObjects {
	class IfcMesh {
	public:
		int id;
		std::vector<float> verts;
		std::vector<int> faces;
		std::vector<int> edges;
	};

	class IfcGeomObject {
	public:
		std::string name;
		std::string type;
		std::vector<float> matrix;
		IfcMesh* mesh;
	};

	extern bool Next();
	extern const IfcGeomObject* Get();
	extern bool Init(char* fn, bool world_coords = false);
	extern int Progress();
};