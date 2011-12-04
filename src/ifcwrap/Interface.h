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

	const int WELD_VERTICES = 1;
	const int USE_WORLD_COORDS = 2;

	class IfcMesh {
	public:
		int id;
		std::vector<float> verts;
		std::vector<int> faces;
		std::vector<int> edges;
		std::vector<float> normals;
	};

	class IfcObject {
	public:
		int id;
		int parent_id;
		std::string name;
		std::string type;
		std::string guid;
		std::vector<float> matrix;
	};

	class IfcGeomObject : public IfcObject {
	public:
		IfcMesh* mesh;
	};

	bool Next();
	const IfcGeomObject* Get();
	bool Init(const std::string fn);
	bool InitUCS2(char* fn);
	void Settings(int setting, bool value);
	int Progress();
	const IfcObject* GetObject(int id);
	bool CleanUp();
	std::string GetLog();

};