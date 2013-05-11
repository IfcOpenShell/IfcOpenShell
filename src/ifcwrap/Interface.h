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

namespace IfcGeom {
	class SurfaceStyle {
	};
}

namespace IfcGeomObjects {

	const int WELD_VERTICES = 1;
	const int USE_WORLD_COORDS = 2;
	const int CONVERT_BACK_UNITS = 3;
	const int USE_BREP_DATA = 4;
	const int SEW_SHELLS = 5;
	const int FASTER_BOOLEANS = 6;
	const int FORCE_CCW_FACE_ORIENTATION = 7;
    const int DISABLE_OPENING_SUBTRACTIONS = 8;

	class IfcRepresentationTriangulation {
	private:
		int _id;
		std::vector<float> _verts;
		std::vector<int> _faces;
		std::vector<int> _edges;
		std::vector<float> _normals;
		std::vector<int> _materials;
		std::vector<const IfcGeom::SurfaceStyle*> _surface_styles;

		IfcRepresentationTriangulation();
		IfcRepresentationTriangulation(const IfcRepresentationTriangulation&);
		IfcRepresentationTriangulation& operator=(const IfcRepresentationTriangulation&);
		virtual ~IfcRepresentationTriangulation();
	public:
		int id() const;
		const std::vector<float>& verts() const;
		const std::vector<int>& faces() const;
		const std::vector<int>& edges() const;
		const std::vector<float>& normals() const;
		const std::vector<int>& materials() const;
	};

	class IfcRepresentationBrepData {
	private:
		int _id;
		std::string _brep_data;

		IfcRepresentationBrepData();
		IfcRepresentationBrepData(const IfcRepresentationBrepData&);
		IfcRepresentationBrepData& operator=(const IfcRepresentationBrepData&);
		virtual ~IfcRepresentationBrepData();
	public:
		int id() const;
		const std::string& brep_data() const;
	};

	class IfcObject {
	private:
		int _id;
		int _parent_id;
		std::string _name;
		std::string _type;
		std::string _guid;
		std::vector<float> _matrix;

		IfcObject();
		IfcObject(const IfcObject& other);
		IfcObject& operator=(const IfcObject& other);
		virtual ~IfcObject() {}
	public:
		int id() const;
		int parent_id() const;
		const std::string& name() const;
		const std::string& type() const;
		const std::string& guid() const;
		const std::vector<float>& matrix() const;
	};

	class IfcGeomObject : public IfcObject {
	private:
		IfcRepresentationTriangulation* _mesh;

		IfcGeomObject();
		IfcGeomObject(const IfcGeomObject& other);
		IfcGeomObject& operator=(const IfcGeomObject& other);
		virtual ~IfcGeomObject();
	public:
		const IfcRepresentationTriangulation& mesh() const;
	};

	class IfcGeomBrepDataObject : public IfcObject {
	private:
		IfcRepresentationBrepData* _mesh;

		IfcGeomBrepDataObject();
		IfcGeomBrepDataObject(const IfcGeomBrepDataObject& other);
		IfcGeomBrepDataObject& operator=(const IfcGeomBrepDataObject& other);
		virtual ~IfcGeomBrepDataObject();
	public:
		const IfcRepresentationBrepData& mesh() const;
	};

	void Settings(int setting, bool value);
	
	bool Init(const std::string fn);
	
	const IfcGeomObject* Get();
	const IfcGeomBrepDataObject* GetBrepData();
	
	const IfcObject* GetObject(int id);

	bool Next();
	
	int Progress();

	const std::string GetLog();
	bool CleanUp();	
};