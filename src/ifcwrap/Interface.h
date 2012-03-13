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
	const int CONVERT_BACK_UNITS = 3;
	const int USE_BREP_DATA = 4;

	class IfcMesh {
	public:
		int id;
		std::vector<double> verts;
		std::vector<int> faces;
		std::vector<int> edges;
		std::vector<double> normals;
		std::string brep_data;
	};

	class IfcObject {
	public:
		int id;
		int parent_id;
		std::string name;
		std::string type;
		std::string guid;
		std::vector<double> matrix;
		const std::vector<int> name_as_intvector() {
			std::vector<int> r;
			for ( std::string::const_iterator it = name.begin(); it != name.end(); ++ it ) r.push_back(*it);
			return r;
		}
		const std::vector<int> type_as_intvector() {
			std::vector<int> r;
			for ( std::string::const_iterator it = type.begin(); it != type.end(); ++ it ) r.push_back(*it);
			return r;
		}
		const std::vector<int> guid_as_intvector() {
			std::vector<int> r;
			for ( std::string::const_iterator it = guid.begin(); it != guid.end(); ++ it ) r.push_back(*it);
			return r;
		}
	};

	class IfcGeomObject : public IfcObject {
	public:
		IfcMesh* mesh;
	};

	bool Next();
	const IfcGeomObject* Get();
	bool Init(const std::string fn);
	bool InitUCS2(const char* fn) {
        return Init(std::string(fn+1));
    }
	void Settings(int setting, bool value);
	int Progress();
	const IfcObject* GetObject(int id);
	bool CleanUp();
	std::string GetLog();

};