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

#include "../ifcparse/IfcException.h"
#include "../ifcgeom/IfcGeomObjects.h"
#include "../ifcgeom/IfcGeom.h"

// Welds vertices that belong to different faces
int IfcGeomObjects::IfcMesh::addvert(gp_Pnt p) {
	const float X = (float)p.X();const float Y = (float)p.Y();const float Z = (float)p.Z();
	const VertKey key = VertKey(X,std::pair<float,float>(Y,Z));
	VertKeyMap::const_iterator it = welds.find(key);
	if ( it != welds.end() ) return it->second;
	verts.push_back(X);
	verts.push_back(Y);
	verts.push_back(Z);
	int i = (int) welds.size();
	welds[key] = i;
	return i;
}

IfcGeomObjects::IfcMesh::IfcMesh(int i, TopoDS_Shape s) {
	id = i;

	// Triangulate the shape
	try {
		BRepTools::Clean(s);
		BRepMesh::Mesh(s,0.001f);
	} catch(...) {
		Ifc::LogMessage("Error","Failed to triangulate mesh");
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

IfcGeomObjects::IfcObject::IfcObject(int my_id, 
		int p_id, 
		const std::string& n, 
		const std::string& t, 
		const std::string& g, 
		const gp_Trsf& trsf) {

	// Convert the gp_Trsf into a 4x3 Matrix
	for( int i = 1; i < 5; ++ i )
		for ( int j = 1; j < 4; ++ j )
			matrix.push_back((float)trsf.Value(j,i));

	id = my_id;
	parent_id = p_id;
	name = n;
	type = t;
	guid = g;
}

IfcGeomObjects::IfcGeomObject::IfcGeomObject(int my_id, 
		int p_id, 
		const std::string& n, 
		const std::string& t, 
		const std::string& g,
		const gp_Trsf& trsf, 
		IfcMesh* m) : IfcObject(my_id,p_id,n,t,g,trsf) {	

	mesh = m;
}

// A container and iterator for IfcShapeRepresentations
Ifc2x3::IfcShapeRepresentation::list shapereps;
Ifc2x3::IfcShapeRepresentation::it outer;

// The triangulated shape is stored globally because it can be used by multiple IfcBuildingElements
IfcGeomObjects::IfcMesh* shape;
// The compound shape is stored globally because multiple IfcShapeRepresentations 
// can have IfcBuildingElements with different IfcOpeningElements
TopoDS_Shape shapes;

// The object is fetched beforehand to be positive an entity actually exists
IfcGeomObjects::IfcGeomObject* currentGeomObj;

// A container and iterator for IfcBuildingElements for the current IfcShapeRepresentation referenced by *outer
Ifc2x3::IfcProduct::list entities;
Ifc2x3::IfcProduct::it inner;

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
		Ifc2x3::IfcShapeRepresentation::ptr shaperep;

		// Have we reached the end of our list of representations?
		if ( outer == shapereps->end() ) {
			shapereps.reset();
			return 0;
		}
		shaperep = *outer;

		// Has the list of IfcProducts for this representation been initialized?
		if ( ! entities ) {
			if ( shaperep->RepresentationIdentifier() != "Body" &&
				shaperep->RepresentationIdentifier() != "Facetation" ) {
				_nextShape();
				continue;
			}
			Ifc2x3::IfcProductRepresentation::list prodreps = shaperep->OfProductRepresentation();
			entities = Ifc2x3::IfcProduct::list( new IfcTemplatedEntityList<Ifc2x3::IfcProduct>() );
			for ( Ifc2x3::IfcProductRepresentation::it it = prodreps->begin(); it != prodreps->end(); ++it ) {
				if ( (*it)->is(Ifc2x3::Type::IfcProductDefinitionShape) ) {
					Ifc2x3::IfcProductDefinitionShape::ptr pds = reinterpret_pointer_cast<Ifc2x3::IfcProductRepresentation,Ifc2x3::IfcProductDefinitionShape>(*it);
					entities->push(pds->ShapeOfProduct());
				}
			}
			// Does this representation have any IfcProducts?
			if ( ! entities->Size() ) {
				_nextShape();
				continue;
			}
			inner = entities->begin();
		}
		// Have we reached the end of our list of IfcProducts?
		if ( inner == entities->end() ) {
			_nextShape();
			continue;
		}
		// Has the TopoDS_Shape been created for this representation?
		if ( shapes.IsNull() ) {
			if ( !IfcGeom::convert_shape(shaperep,shapes) ) {
				_nextShape();
				continue;
			}
		}
		Ifc2x3::IfcProduct::ptr ifc_product = *inner;
		int parent_id = -1;
		const std::string name = ifc_product->hasName() ? ifc_product->Name() : "";
		const std::string guid = ifc_product->GlobalId();

		gp_Trsf trsf;
		try {
			IfcGeom::convert(ifc_product->ObjectPlacement(),trsf);
		} catch (...) {}

		// Does the IfcElement have any IfcOpenings?
		Ifc2x3::IfcRelVoidsElement::list openings = Ifc2x3::IfcRelVoidsElement::list();
		if ( ifc_product->is(Ifc2x3::Type::IfcElement) ) {
			Ifc2x3::IfcElement::ptr element = reinterpret_pointer_cast<Ifc2x3::IfcProduct,Ifc2x3::IfcElement>(ifc_product);
			openings = element->HasOpenings();
		}
		// Is the IfcElement a decomposition of an IfcElement with any IfcOpeningElements?
		if ( ifc_product->is(Ifc2x3::Type::IfcBuildingElementPart ) ) {
			Ifc2x3::IfcBuildingElementPart::ptr part = reinterpret_pointer_cast<Ifc2x3::IfcProduct,Ifc2x3::IfcBuildingElementPart>(ifc_product);
			Ifc2x3::IfcRelDecomposes::list decomposes = part->Decomposes();
			for ( Ifc2x3::IfcRelDecomposes::it it = decomposes->begin(); it != decomposes->end(); ++ it ) {
				Ifc2x3::IfcObjectDefinition::ptr obdef = (*it)->RelatingObject();
				if ( obdef->is(Ifc2x3::Type::IfcElement) ) {
					Ifc2x3::IfcElement::ptr element = reinterpret_pointer_cast<Ifc2x3::IfcObjectDefinition,Ifc2x3::IfcElement>(obdef);
					openings->push(element->HasOpenings());
				}
			}
		}

		if ( ifc_product->is(Ifc2x3::Type::IfcElement ) ) {
			Ifc2x3::IfcElement::ptr element = reinterpret_pointer_cast<Ifc2x3::IfcProduct,Ifc2x3::IfcElement>(ifc_product);
			Ifc2x3::IfcRelContainedInSpatialStructure::list parents = element->ContainedInStructure();
			if ( parents->Size() ) {
				Ifc2x3::IfcRelContainedInSpatialStructure::ptr parent = *parents->begin();
				parent_id = parent->RelatingStructure()->entity->id();
			}
		}
		if ( parent_id == -1 ) {
			Ifc2x3::IfcRelDecomposes::list decomposes = ifc_product->IsDecomposedBy();
			// This is a bug in IfcParse IsDecomposedBy() and Decomposes() are mixed
			for ( Ifc2x3::IfcRelDecomposes::it it = decomposes->begin(); it != decomposes->end(); ++ it ) {
				Ifc2x3::IfcRelDecomposes::ptr decompose = *it;
				Ifc2x3::IfcObjectDefinition* ifc_objectdef = decompose->RelatingObject();
				if ( ifc_product == ifc_objectdef ) continue;
				parent_id = ifc_objectdef->entity->id();
			}
		}

		if ( (openings && openings->Size()) || use_world_coords ) {
			if ( shape ) delete shape;
			TopoDS_Shape temp_shape = shapes.Moved(gp_Trsf());
			try {
				if (openings && openings->Size()) {
					IfcGeom::convert_openings(ifc_product,openings,temp_shape,trsf);
				}
			} catch( IfcParse::IfcException& e ) {
				Ifc::LogMessage("Warning",e.what()); 
			} catch(...) { 
				Ifc::LogMessage("Error","Error processing openings for:",ifc_product->entity); 
			}
			if ( use_world_coords ) {
				shape = new IfcGeomObjects::IfcMesh(shaperep->entity->id(),temp_shape.Moved(trsf));
				trsf = gp_Trsf();
			} else {
				shape = new IfcGeomObjects::IfcMesh(shaperep->entity->id(),temp_shape);
			}
		} else if ( ! shape ) {
			shape = new IfcGeomObjects::IfcMesh(shaperep->entity->id(),shapes);
		}

		return new IfcGeomObjects::IfcGeomObject(ifc_product->entity->id(), parent_id, name, 
			Ifc2x3::Type::ToString(ifc_product->type()), guid, trsf, shape);		
	}
	
}

bool IfcGeomObjects::Next() {
	if ( entities ) {
		++inner;
	}
	delete currentGeomObj;
	currentGeomObj = _get();
	if ( ! currentGeomObj ) {
		delete shape;
		return false;
	} else {
		return true;
	}
}
std::vector<IfcGeomObjects::IfcObject*> returned_objects;
bool IfcGeomObjects::CleanUp() {
	Ifc::Dispose();
	IfcGeom::Cache::Purge();
	for ( std::vector<IfcGeomObjects::IfcObject*>::const_iterator it = returned_objects.begin();
		it != returned_objects.end(); 
		++ it ) {
			delete *it;			
	}
	return true;
}
const IfcGeomObjects::IfcObject* IfcGeomObjects::GetObject(int id) {
	IfcObject* ifc_object = 0;
	try {
		const IfcEntity& ifc_entity = Ifc::EntityById(id);
		if ( ifc_entity->is(Ifc2x3::Type::IfcProduct) ) {
			Ifc2x3::IfcProduct::ptr ifc_product = reinterpret_pointer_cast<IfcUtil::IfcBaseClass,Ifc2x3::IfcProduct>(ifc_entity);
			int parent_id = -1;
			if ( ifc_product->is(Ifc2x3::Type::IfcElement ) ) {
				Ifc2x3::IfcElement::ptr element = reinterpret_pointer_cast<Ifc2x3::IfcProduct,Ifc2x3::IfcElement>(ifc_product);
				Ifc2x3::IfcRelContainedInSpatialStructure::list parents = element->ContainedInStructure();
				if ( parents->Size() ) {
					Ifc2x3::IfcRelContainedInSpatialStructure::ptr parent = *parents->begin();
					parent_id = parent->RelatingStructure()->entity->id();
				}
			}
			if ( parent_id == -1 ) {
				Ifc2x3::IfcRelDecomposes::list decomposes = ifc_product->IsDecomposedBy();
				// This is a bug in IfcParse IsDecomposedBy() and Decomposes() are mixed
				for ( Ifc2x3::IfcRelDecomposes::it it = decomposes->begin(); it != decomposes->end(); ++ it ) {
					Ifc2x3::IfcRelDecomposes::ptr decompose = *it;
					Ifc2x3::IfcObjectDefinition* ifc_objectdef = decompose->RelatingObject();
					if ( ifc_product == ifc_objectdef ) continue;
					parent_id = ifc_objectdef->entity->id();
				}
			}
			const std::string name = ifc_product->hasName() ? ifc_product->Name() : "";
			gp_Trsf trsf;
			try {
				IfcGeom::convert(ifc_product->ObjectPlacement(),trsf);
			} catch (...) {}
			ifc_object = new IfcObject(ifc_product->entity->id(),parent_id,name,
				Ifc2x3::Type::ToString(ifc_product->type()),ifc_product->GlobalId(),trsf);
		}
	} catch(...) {}
	if ( !ifc_object ) ifc_object = new IfcObject(-1,-1,"","","",gp_Trsf());
	returned_objects.push_back(ifc_object);
	return ifc_object;
}
const IfcGeomObjects::IfcGeomObject* IfcGeomObjects::Get() {
	return currentGeomObj;
}
bool IfcGeomObjects::Init(const char* fn, bool world_coords) {
	return IfcGeomObjects::Init(fn, world_coords, 0, 0);
}
bool IfcGeomObjects::Init(const char* fn, bool world_coords, std::ostream* log1, std::ostream* log2) {
	if ( log1 || log2 ) Ifc::SetOutput(log1,log2);
	use_world_coords = world_coords;
	if ( !Ifc::Init(fn) ) return false;

	shapereps = Ifc::EntitiesByType<Ifc2x3::IfcShapeRepresentation>();
	if ( ! shapereps ) return false;
	
	outer = shapereps->begin();
	entities.reset();
	currentGeomObj = _get();
	
	if ( ! currentGeomObj ) return false;

	done = 0;
	total = shapereps->Size();
	return true;
}
bool IfcGeomObjects::Init(std::istream& f, int len, bool world_coords, std::ostream* log1, std::ostream* log2) {
	if ( log1 || log2 ) Ifc::SetOutput(log1,log2);
	use_world_coords = world_coords;
	if ( !Ifc::Init(f, len) ) return false;

	shapereps = Ifc::EntitiesByType<Ifc2x3::IfcShapeRepresentation>();
	if ( ! shapereps ) return false;
	
	outer = shapereps->begin();
	entities.reset();
	currentGeomObj = _get();
	
	if ( ! currentGeomObj ) return false;

	done = 0;
	total = shapereps->Size();
	return true;
}
int IfcGeomObjects::Progress() {
	return 100 * done / total;
}
