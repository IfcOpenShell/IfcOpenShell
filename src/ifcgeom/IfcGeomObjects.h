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
 * Init(char* fn, bool world_coords) parses the IFC file in fn, returns true    *
 *   on succes, world_coords = true will result in all IfcGeomObject.matrix     *
 *   being an identity matrix and IfcMesh.verts containing global positions     *
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

#include "../ifcgeom/IfcShapeList.h"

namespace IfcGeomObjects {

	const int WELD_VERTICES = 1;
	const int USE_WORLD_COORDS = 2;
	const int CONVERT_BACK_UNITS = 3;

	typedef std::vector<int>::const_iterator IntIt;
	typedef std::vector<float>::const_iterator FltIt;
	typedef std::pair< float,std::pair<float,float> > VertKey;
	typedef std::map<VertKey,int> VertKeyMap;
	typedef std::pair<int,int> Edge;

	class IfcMesh {
	public:
		int id;
		std::vector<float> verts;
		std::vector<int> faces;
		std::vector<int> edges;
		std::vector<float> normals;
		VertKeyMap welds;
		
		IfcMesh(int i, const IfcGeom::ShapeList& s);
	private:
		int addvert(const gp_XYZ& p);
		inline void addedge(int n1, int n2, std::map<std::pair<int,int>,int>& edgecount, std::vector<std::pair<int,int> >& edges_temp) {
			const Edge e = Edge( (std::min)(n1,n2),(std::max)(n1,n2) );
			if ( edgecount.find(e) == edgecount.end() ) edgecount[e] = 1;
			else edgecount[e] ++;
			edges_temp.push_back(e);
		}
	};

	class IfcObject {
	public:
		int id;
		int parent_id;
		std::string name;
		std::string type;
		std::string guid;
		std::vector<float> matrix;
		IfcObject(int my_id, int p_id, const std::string& n, const std::string& t, const std::string& g, const gp_Trsf& trsf);
	};

	class IfcGeomObject : public IfcObject {
	public:
		IfcMesh* mesh;
		IfcGeomObject(int my_id, int p_id, const std::string& n, const std::string& t, const std::string& g, const gp_Trsf& trsf, IfcMesh* m);
	};

	bool Init(const std::string fn);
	bool InitUCS2(char* fn);
	bool Init(void* data, int len);
	bool Init(const std::string fn, std::ostream* log1= 0, std::ostream* log2= 0);
	bool Init(std::istream& f, int len, std::ostream* log1= 0, std::ostream* log2= 0);
	void Settings(int setting, bool value);
	bool CleanUp();
	const IfcGeomObject* Get();
	bool Next();	
	int Progress();
	const IfcObject* GetObject(int id);
	std::string GetLog();

}

#endif
