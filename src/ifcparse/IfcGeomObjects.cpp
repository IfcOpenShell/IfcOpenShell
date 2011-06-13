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

#include <map>

#include <gp_Trsf.hxx>
#include <TopoDS_Compound.hxx>
#include <BRep_Builder.hxx>
#include <BRepTools.hxx>
#include <BRep_Tool.hxx>
#include <TopExp_Explorer.hxx>
#include <BRepMesh.hxx>
#include <Poly_Triangulation.hxx>
#include <Poly_PolygonOnTriangulation.hxx>
#include <TColgp_Array1OfPnt.hxx>
#include <TShort_Array1OfShortReal.hxx>
#include <Poly_Array1OfTriangle.hxx>
#include <StdFail_NotDone.hxx>

#include "../ifcparse/IfcGeomObjects.h"
#include "../ifcparse/IfcGeom.h"
#include "../ifcparse/IfcEnum.h"
#include "../ifcparse/IfcTypes.h"

// Welds vertices that belong to different faces
int IfcGeomObjects::IfcMesh::addvert(gp_Pnt p) {
	int i = 0; const float X = (float)p.X();const float Y = (float)p.Y();const float Z = (float)p.Z();
	for ( std::vector<float>::const_iterator it = verts.begin(); it != verts.end(); ) {
		const float x = *it; ++it;
		const float y = *it; ++it;
		const float z = *it; ++it;
		if ( X == x && Y == y && Z == z ) return i;
		++i;
	}
	verts.push_back(X);
	verts.push_back(Y);
	verts.push_back(Z);
	return i;
}

IfcGeomObjects::IfcMesh::IfcMesh(int i, TopoDS_Shape s) {
	id = i;

	// Triangulate the shape
	try {
		BRepTools::Clean(s);
		BRepMesh::Mesh(s,0.001f);
	} catch(...) {
		std::cout << "[Error] Failed to triangulate IFC Entity #" << i << std::endl;
		return;
	}
	TopExp_Explorer exp;

	// Iterates over the faces of the shape
	for ( exp.Init(s,TopAbs_FACE); exp.More(); exp.Next() ) {
		TopoDS_Face face = TopoDS::Face(exp.Current());
		TopLoc_Location loc;
		Handle_Poly_Triangulation tri = BRep_Tool::Triangulation(face,loc);

		if ( ! tri.IsNull() ) {
			
			// Keep track of the number of times an edge is used
			// Manifold edges (i.e. edges used twice) are deemed invisible
			std::map<std::pair<int,int>,int> edgecount;
			std::vector<std::pair<int,int> > edges_temp;

			const TColgp_Array1OfPnt& nodes = tri->Nodes();
			std::map<int,int> dict;
			for( int i = 1; i <= nodes.Length(); ++ i ) {
				dict[i] = addvert(nodes(i).Transformed(loc));
			}

			const Poly_Array1OfTriangle& triangles = tri->Triangles();			
			for( int i = 1; i <= triangles.Length(); ++ i ) {
				int n1,n2,n3;
				if ( face.Orientation() == TopAbs_REVERSED )
					triangles(i).Get(n3,n2,n1);
				else triangles(i).Get(n1,n2,n3);
				faces.push_back(dict[n1]);
				faces.push_back(dict[n2]);
				faces.push_back(dict[n3]);

				addedge(n1,n2,edgecount,edges_temp);
				addedge(n2,n3,edgecount,edges_temp);
				addedge(n3,n1,edgecount,edges_temp);
			}
			for ( std::vector<std::pair<int,int> >::const_iterator it = edges_temp.begin(); it != edges_temp.end(); ++it ) {
				edges.push_back(edgecount[*it]==1);
			}
		}
	}
}

IfcGeomObjects::IfcGeomObject::IfcGeomObject( const std::string& n, const std::string& t, gp_Trsf trsf, IfcMesh* m ) {
	// Convert the gp_Trsf into a 4x3 Matrix
	for( int i = 1; i < 5; ++ i )
		for ( int j = 1; j < 4; ++ j )
			matrix.push_back((float)trsf.Value(j,i));

	name = n;
	type = t;
	mesh = m;
}

// A container and iterator for IfcShapeRepresentations
IfcEntities shapereps;
IfcParse::Entities::it outer;

// The triangulated shape is stored globally because it can be used by multiple IfcBuildingElements
IfcGeomObjects::IfcMesh* shape;
// The compound shape is stored globally because multiple IfcShapeRepresentations 
// can have IfcBuildingElements with different IfcOpeningElements
TopoDS_Compound shapes;

// The object is fetched beforehand to be positive an entity actually exists
IfcGeomObjects::IfcGeomObject* currentGeomObj;

// A container and iterator for IfcBuildingElements for the current IfcShapeRepresentation referenced by *outer
IfcEntities entities;
IfcParse::Entities::it inner;

bool use_world_coords;
int done;
int total;

// Move the the next IfcShapeRepresentation
void _nextShape() {
	if ( shape ) delete shape;
	shapes.Nullify();
	shape = 0;
	entities.reset();
	++ outer;
	++ done;
}

// Returns the current IfcGeomObject*
IfcGeomObjects::IfcGeomObject* _get() {
	while ( true ) {
		IfcEntity shaperep;
		if ( outer == shapereps->end() ) {
			shapereps.reset();
			return 0;
		}
		shaperep = *outer;
		if ( ! entities ) {
			if ( shaperep->arg(1)->s() != "Body" ) {
				_nextShape();
				continue;
			}
#ifdef _DEBUG
			std::cout << shaperep->toString() << std::endl;
#endif
			// Find the IfcBuildingElements that refer to the current IfcShapeRepresentation
			entities = shaperep->parents(IfcSchema::Enum::IfcProductDefinitionShape)->parents();
			entities->pushs(shaperep->parents(IfcSchema::Enum::IfcProductRepresentation)->parents()); // 2x2 compatibility
			entities->pushs(shaperep->parents(IfcSchema::Enum::IfcRepresentationMap)->parents(IfcSchema::Enum::IfcMappedItem)
				->parents(IfcSchema::Enum::IfcShapeRepresentation,1,"Body")->parents(IfcSchema::Enum::IfcProductDefinitionShape)->parents());
			entities->pushs(shaperep->parents(IfcSchema::Enum::IfcRepresentationMap)->parents(IfcSchema::Enum::IfcMappedItem)
				->parents(IfcSchema::Enum::IfcShapeRepresentation,1,"Body")->parents(IfcSchema::Enum::IfcProductRepresentation)->parents());
			if ( ! entities->size ) {
				_nextShape();
				continue;
			}
			inner = entities->begin();
		}
		if ( inner == entities->end() ) {
			_nextShape();
			continue;
		}
		if ( shapes.IsNull() ) {
			BRep_Builder builder;
			builder.MakeCompound (shapes);

			bool hasShapes = false;
			IfcEntities l = ((IfcSchema::ShapeRepresentation*)shaperep.get())->Shapes();
			for( IfcParse::Entities::it it = l->begin(); it != l->end(); ++ it ) {
				const IfcEntity ifcshape = *it;
				if ( ifcshape->dt == IfcSchema::Enum::IfcMappedItem ) continue;
				TopoDS_Shape ss;
				if ( IfcGeom::convert_shape(ifcshape,ss) ) {
					builder.Add(shapes,ss);
					hasShapes = true;
#ifdef _DEBUG
					std::cout << ifcshape->toString() << std::endl;
#endif
				}
			}
			if ( ! hasShapes || shapes.IsNull() ) {
				_nextShape();
				continue;
			}
		}

		IfcSchema::BuildingElement* entity = (IfcSchema::BuildingElement*)(*inner).get();
#ifdef _DEBUG
		std::cout << entity->toString() << std::endl;
#endif
		const std::string guid = entity->Guid();
		gp_Trsf trsf;
		try {
			IfcGeom::convert((IfcSchema::LocalPlacement*)(entity->Placement().get()),trsf);
		} catch( IfcParse::IfcException& e ) {std::cout << "[Error] " << e.what() << std::endl; _nextShape(); }
		IfcEntities openings = IfcEntities();
		if ( entity->dt != IfcSchema::Enum::IfcOpeningElement ) {
			openings = entity->parents(IfcSchema::Enum::IfcRelVoidsElement);
		}

		if ( (openings && openings->size) || use_world_coords ) {
			if ( shape ) delete shape;
			TopoDS_Shape temp_shape (shapes);
			try {
				if (openings && openings->size) IfcGeom::convert_openings(entity,openings,temp_shape,trsf);
			} catch( IfcParse::IfcException& e ) {std::cout << "[Warning] " << e.what() << std::endl; }
			catch(StdFail_NotDone&) { std::cout << "[Error] Unknown modelling processing openings for:" << std::endl << entity->toString() << std::endl; }
			if ( use_world_coords ) {
				shape = new IfcGeomObjects::IfcMesh(shaperep->id,temp_shape.Moved(trsf));
				trsf = gp_Trsf();
			} else {
				shape = new IfcGeomObjects::IfcMesh(shaperep->id,temp_shape);
			}
		} else if ( ! shape ) {
			shape = new IfcGeomObjects::IfcMesh(shaperep->id,shapes);
		}
		return new IfcGeomObjects::IfcGeomObject(guid, entity->datatype(), trsf, shape);		
	}
}

extern bool IfcGeomObjects::Next() {
	if ( entities ) {
		++inner;
	}
	delete currentGeomObj;
	currentGeomObj = _get();
	if ( ! currentGeomObj ) {
		delete shape;
		Ifc::Dispose();
		return false;
	} else {
		return true;
	}
}
extern const IfcGeomObjects::IfcGeomObject* IfcGeomObjects::Get() {
	return currentGeomObj;
}
extern bool IfcGeomObjects::Init(char* fn, bool world_coords) {
	use_world_coords = world_coords;
	if ( !Ifc::Init(fn) ) return false;

	shapereps = Ifc::EntitiesByType(IfcSchema::Enum::IfcShapeRepresentation);
	if ( ! shapereps ) return false;
	
	outer = shapereps->begin();
	entities.reset();
	currentGeomObj = _get();
	
	if ( ! currentGeomObj ) return false;

	done = 0;
	total = shapereps->size;
	return 1;
}
extern int IfcGeomObjects::Progress() {
	return 100 * done / total;
}
