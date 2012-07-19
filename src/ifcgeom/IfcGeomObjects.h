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
#include "../ifcgeom/IfcShapeList.h"

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

	// End of settings enumeration.

	// Some typedefs for convenience
	typedef std::vector<int>::const_iterator IntIt;
	typedef std::vector<float>::const_iterator FltIt;
	// A nested pair of doubles to be able to store an XYZ coordinate in a map.
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
		std::string brep_data;
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
