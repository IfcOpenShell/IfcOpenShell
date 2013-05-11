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

/********************************************************************************
 *                                                                              *
 * Geometrical data in an IFC file consists of shapes (IfcShapeRepresentation)  *
 * and instances (SUBTYPE OF IfcBuildingElement e.g. IfcWindow).                *
 *                                                                              *
 * IfcMesh is a class that represents a triangulated IfcShapeRepresentation.    *
 *   IfcMesh.verts is a 1 dimensional vector of float defining the cartesian    *
 *      coordinates of the vertices of the triangulated shape in the format of  *
 *      [x1,y1,z1,..,xn,yn,zn]                                                  *
 *   IfcMesh.faces is a 1 dimensional vector of int containing the indices of   *
 *     the triangles referencing positions in IfcMesh.verts                     *
 *   IfcMesh.edges is a 1 dimensional vector of int in {0,1} that dictates      *
 *	   the visibility of the edges that span the faces in IfcMesh.faces         *
 *                                                                              *
 * IfcGeomObject represents the actual IfcBuildingElements.                     *
 *   IfcGeomObject.name is the GUID of the element                              *
 *   IfcGeomObject.type is the datatype of the element e.g. IfcWindow           *
 *   IfcGeomObject.mesh is a pointer to an IfcMesh                              *
 *   IfcGeomObject.matrix is a 4x3 matrix that defines the orientation and      *
 *     translation of the mesh in relation to the world origin                  *
 *                                                                              *
 * Init(char* fn) parses the IFC file in fn, returns true on succes.            *
 *                                                                              *
 * Get() returns a pointer to the current IfcGeomObject                         *
 *                                                                              * 
 * Next() returns true if there is an entity yet available                      *
 *                                                                              *
 * Progress() returns an int in [0..100] that indicates the overall progress    *
 *                                                                              *
 ********************************************************************************/

#ifndef IFCOBJECTS_H
#define IFCOBJECTS_H

#include <map>
#include <vector>
#include <algorithm>

#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>

#include "../ifcparse/IfcParse.h"
#include "../ifcgeom/IfcRepresentationShapeItem.h"

namespace IfcGeomObjects {

	// Enumeration of setting identifiers. These settings define the
	// behaviour of various aspects of IfcOpenShell.

	// Specifies whether vertices are welded, meaning that the coordinates
	// vector will only contain unique xyz-triplets. This results in a 
	// manifold mesh which is useful for modelling applications, but might 
	// result in unwanted shading artifacts in rendering applications.
	const int WELD_VERTICES = 1;
	// Specifies whether to apply the local placements of building elements
	// directly to the coordinates of the representation mesh rather than
	// to represent the local placement in the 4x3 matrix, which will in that
	// case be the identity matrix.
	const int USE_WORLD_COORDS = 2;
	// Internally IfcOpenShell measures everything in meters. This settings
	// specifies whether to convert IfcGeomObjects back to the units in which
	// the geometry in the IFC file is specified.
	const int CONVERT_BACK_UNITS = 3;
	// Specifies whether to use the Open Cascade BREP format for representation
	// items rather than to create triangle meshes. This is useful is IfcOpenShell
	// is used as a library in an application that is also built on Open Cascade.
	const int USE_BREP_DATA = 4;
	// Specifies whether to sew IfcConnectedFaceSets (open and closed shells) to
	// TopoDS_Shells or whether to keep them as a loose collection of faces.
	const int SEW_SHELLS = 5;
	// Specifies whether to compose IfcOpeningElements into a single compound
	// in order to speed up the processing of opening subtractions.
	const int FASTER_BOOLEANS = 6;
	// By default singular faces have no explicitly defined orientation, to
	// force faces to be defined CounterClockWise set this to true.
	const int FORCE_CCW_FACE_ORIENTATION = 7;
    // Disables the subtraction of IfcOpeningElement representations from
    // the related building element representations.
    const int DISABLE_OPENING_SUBTRACTIONS = 8;
	// Disables the triangulation of the topological representations. Useful if
	// the client application understands Open Cascade's native format. Note
	// that this setting is implied by the USE_BREP_DATA setting.
    const int DISABLE_TRIANGULATION = 9;

	// End of settings enumeration.

	// A nested pair of floats and a material index to be able to store an XYZ coordinate in a map.
	// TODO: Make this a std::tuple when compilers add support for that.
	typedef std::pair<int, std::pair<float,std::pair<float,float> > > VertKey;
	typedef std::map<VertKey,int> VertKeyMap;
	typedef std::pair<int,int> Edge;

	class IfcRepresentationShapeModel {
	private:
		unsigned int id;
		const IfcGeom::IfcRepresentationShapeItems shapes;
		IfcRepresentationShapeModel(const IfcRepresentationShapeModel& other);
		IfcRepresentationShapeModel& operator=(const IfcRepresentationShapeModel& other);
	public:
		IfcRepresentationShapeModel(unsigned int id, const IfcGeom::IfcRepresentationShapeItems& shapes)
			: id(id)
			, shapes(shapes)
		{}
		virtual ~IfcRepresentationShapeModel() {}
		IfcGeom::IfcRepresentationShapeItems::const_iterator begin() const { return shapes.begin(); }
		IfcGeom::IfcRepresentationShapeItems::const_iterator end() const { return shapes.end(); }
		const unsigned int& getId() const { return id; }
	};

	class IfcRepresentationBrepData {
	private:
		int _id;
		std::string _brep_data;
	public:
		int id() const;
		const std::string& brep_data() const;
		IfcRepresentationBrepData(const IfcRepresentationShapeModel& s);
		virtual ~IfcRepresentationBrepData() {}
	private:
		IfcRepresentationBrepData();
		IfcRepresentationBrepData(const IfcRepresentationBrepData&);
		IfcRepresentationBrepData& operator=(const IfcRepresentationBrepData&);
	};

	class IfcRepresentationTriangulation {
	private:
		int _id;
		std::vector<float> _verts;
		std::vector<int> _faces;
		std::vector<int> _edges;
		std::vector<float> _normals;
		std::vector<int> _materials;
		std::vector<const IfcGeom::SurfaceStyle*> _surface_styles;
		VertKeyMap welds;
	public:
		int id() const;
		const std::vector<float>& verts() const;
		const std::vector<int>& faces() const;
		const std::vector<int>& edges() const;
		const std::vector<float>& normals() const;
		const std::vector<int>& materials() const;
		const std::vector<const IfcGeom::SurfaceStyle*>& surface_styles() const;
		IfcRepresentationTriangulation(const IfcRepresentationShapeModel& s);
		virtual ~IfcRepresentationTriangulation() {}
	private:
		int addvert(int material_index, const gp_XYZ& p);
		inline void addedge(int n1, int n2, std::map<std::pair<int,int>,int>& edgecount, std::vector<std::pair<int,int> >& edges_temp) {
			const Edge e = Edge( (std::min)(n1,n2),(std::max)(n1,n2) );
			if ( edgecount.find(e) == edgecount.end() ) edgecount[e] = 1;
			else edgecount[e] ++;
			edges_temp.push_back(e);
		}
		IfcRepresentationTriangulation();
		IfcRepresentationTriangulation(const IfcRepresentationTriangulation&);
		IfcRepresentationTriangulation& operator=(const IfcRepresentationTriangulation&);
	};

	class IfcObject {
	private:
		int _id;
		int _parent_id;
		std::string _name;
		std::string _type;
		std::string _guid;
		std::vector<float> _matrix;
	public:
		int id() const;
		int parent_id() const;
		const std::string& name() const;
		const std::string& type() const;
		const std::string& guid() const;
		const std::vector<float>& matrix() const;
		IfcObject(int id, int parent_id, const std::string& name, const std::string& type, const std::string& guid, const gp_Trsf& trsf);
		virtual ~IfcObject() {}
	};

	class IfcGeomShapeModelObject : public IfcObject {
	private:
		IfcRepresentationShapeModel* _mesh;
	public:
		const IfcRepresentationShapeModel& mesh() const;
		IfcGeomShapeModelObject(int id, int parent_id, const std::string& name, const std::string& type, const std::string& guid, const gp_Trsf& trsf, IfcRepresentationShapeModel* mesh);
		virtual ~IfcGeomShapeModelObject() {
			delete _mesh;
		}
	private:
		IfcGeomShapeModelObject(const IfcGeomShapeModelObject& other);
		IfcGeomShapeModelObject& operator=(const IfcGeomShapeModelObject& other);		
	};

	class IfcGeomObject : public IfcObject {
	private:
		IfcRepresentationTriangulation* _mesh;
	public:
		const IfcRepresentationTriangulation& mesh() const;
		IfcGeomObject(const IfcGeomShapeModelObject& shape_model);
		virtual ~IfcGeomObject() {
			delete _mesh;
		}
	private:
		IfcGeomObject(const IfcGeomObject& other);
		IfcGeomObject& operator=(const IfcGeomObject& other);
	};

	class IfcGeomBrepDataObject : public IfcObject {
	private:
		IfcRepresentationBrepData* _mesh;
	public:
		const IfcRepresentationBrepData& mesh() const;
		IfcGeomBrepDataObject(const IfcGeomShapeModelObject& shape_model);
		virtual ~IfcGeomBrepDataObject() {
			delete _mesh;
		}
	private:
		IfcGeomBrepDataObject(const IfcGeomBrepDataObject& other);
		IfcGeomBrepDataObject& operator=(const IfcGeomBrepDataObject& other);
	};

	bool Init(const std::string fn);
	bool Init(void* data, int len);
	bool Init(const std::string fn, std::ostream* log1= 0, std::ostream* log2= 0);
	bool Init(std::istream& f, int len, std::ostream* log1= 0, std::ostream* log2= 0);
	
	void Settings(int setting, bool value);
	void InitUnits();
	
	const IfcGeomObject* Get();
	const IfcObject* GetObject(int id);
	const IfcGeomBrepDataObject* GetBrepData();
	const IfcGeomShapeModelObject* GetShapeModel();
	
	bool Next();
	int Progress();
	
	const std::string GetLog();
	IfcParse::IfcFile* GetFile();

	bool CleanUp();
}

#endif
