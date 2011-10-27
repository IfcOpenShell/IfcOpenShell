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

#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include <gp_Quaternion.hxx>
#include <TopoDS_Compound.hxx>
#include <BRep_Builder.hxx>
#include <BRepTools.hxx>
#include <BRep_Tool.hxx>
#include <TopExp_Explorer.hxx>
#include <BRepMesh.hxx>
#include <Poly_Triangulation.hxx>
#include <Poly_PolygonOnTriangulation.hxx>
#include <TColgp_Array1OfPnt.hxx>
#include <TColgp_Array1OfPnt2d.hxx>
#include <TShort_Array1OfShortReal.hxx>
#include <Poly_Array1OfTriangle.hxx>
#include <StdFail_NotDone.hxx>
#include <BRepGProp_Face.hxx>

#include "../ifcparse/IfcException.h"
#include "../ifcgeom/IfcGeomObjects.h"
#include "../ifcgeom/IfcGeom.h"

// Welds vertices that belong to different faces
bool weld_vertices = false;

int IfcGeomObjects::IfcMesh::addvert(const gp_XYZ& p) {
	const float X = (float)p.X();const float Y = (float)p.Y();const float Z = (float)p.Z();
	int i = (int) verts.size() / 3;
	if ( weld_vertices ) {
		const VertKey key = VertKey(X,std::pair<float,float>(Y,Z));
		VertKeyMap::const_iterator it = welds.find(key);
		if ( it != welds.end() ) return it->second;
		i = (int) welds.size();
		welds[key] = i;
	}
	verts.push_back(X);
	verts.push_back(Y);
	verts.push_back(Z);
	return i;
}

bool use_world_coords = false;

IfcGeomObjects::IfcMesh::IfcMesh(int i, const IfcGeom::ShapeList& shapes) {
	id = i;

	for ( IfcGeom::ShapeList::const_iterator it = shapes.begin(); it != shapes.end(); ++ it ) {

		const TopoDS_Shape& s = *(*it).second;
		const gp_GTrsf& trsf = *(*it).first;

		// Triangulate the shape
		try {
			//BRepTools::Clean(s);
			BRepMesh::Mesh(s,0.001f);
		} catch(...) {
			Ifc::LogMessage("Error","Failed to triangulate mesh:",Ifc::EntityById(i)->entity);
			continue;
		}
		TopExp_Explorer exp;

		// Iterates over the faces of the shape
		for ( exp.Init(s,TopAbs_FACE); exp.More(); exp.Next() ) {
			TopoDS_Face face = TopoDS::Face(exp.Current());
			TopLoc_Location loc;
			Handle_Poly_Triangulation tri = BRep_Tool::Triangulation(face,loc);

			if ( ! tri.IsNull() ) {

				// A 3x3 matrix to rotate the vertex normals
				const gp_Mat rotation_matrix = use_world_coords 
					? trsf.VectorialPart() * loc.Transformation().VectorialPart()
					: loc.Transformation().VectorialPart();
			
				// Keep track of the number of times an edge is used
				// Manifold edges (i.e. edges used twice) are deemed invisible
				std::map<std::pair<int,int>,int> edgecount;
				std::vector<std::pair<int,int> > edges_temp;

				const TColgp_Array1OfPnt& nodes = tri->Nodes();
				const TColgp_Array1OfPnt2d& uvs = tri->UVNodes();
				std::vector<gp_XYZ> coords;
				BRepGProp_Face prop(face);
				std::map<int,int> dict;

				// Vertex normals are only calculated if vertices are not welded
				const bool calculate_normals = ! weld_vertices;

				for( int i = 1; i <= nodes.Length(); ++ i ) {
					coords.push_back(nodes(i).Transformed(loc).XYZ());
					trsf.Transforms(*coords.rbegin());
					dict[i] = addvert(*coords.rbegin());
					
					if ( calculate_normals ) {
						const gp_Pnt2d& uv = uvs(i);
						gp_Pnt p;
						gp_Vec normal_direction;
						prop.Normal(uv.X(),uv.Y(),p,normal_direction);						
						gp_Dir normal = gp_Dir(normal_direction.XYZ() * rotation_matrix);
						normals.push_back((float)normal.X());
						normals.push_back((float)normal.Y());
						normals.push_back((float)normal.Z());
					}
				}

				const Poly_Array1OfTriangle& triangles = tri->Triangles();			
				for( int i = 1; i <= triangles.Length(); ++ i ) {
					int n1,n2,n3;
					if ( face.Orientation() == TopAbs_REVERSED )
						triangles(i).Get(n3,n2,n1);
					else triangles(i).Get(n1,n2,n3);

					/* An alternative would be to calculate normals based
					 * on the coordinates of the mesh vertices */
					/*
					const gp_XYZ pt1 = coords[n1-1];
					const gp_XYZ pt2 = coords[n2-1];
					const gp_XYZ pt3 = coords[n3-1];
					const gp_XYZ v1 = pt2-pt1;
					const gp_XYZ v2 = pt3-pt2;
					gp_Dir normal = gp_Dir(v1^v2);
					normals.push_back((float)normal.X());
					normals.push_back((float)normal.Y());
					normals.push_back((float)normal.Z());
					*/

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

// The object is fetched beforehand to be positive an entity actually exists
IfcGeomObjects::IfcGeomObject* current_geom_obj;

// A container and iterator for IfcBuildingElements for the current IfcShapeRepresentation referenced by *outer
Ifc2x3::IfcProduct::list entities;
Ifc2x3::IfcProduct::it inner;

int done;
int total;

// Move the the next IfcShapeRepresentation
void _nextShape() {
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
				} else {
					// http://buildingsmart-tech.org/ifc/IFC2x3/TC1/html/ifcrepresentationresource/lexical/ifcproductrepresentation.htm
					// IFC2x Edition 3 NOTE  Users should not instantiate the entity IfcProductRepresentation from IFC2x Edition 3 onwards. 
					// It will be changed into an ABSTRACT supertype in future releases of IFC.

					// IfcProductRepresentation also lacks the INVERSE relation to IfcProduct
					// Let's find the IfcProducts that reference the IfcProductRepresentation anyway
					IfcEntities products = (*it)->entity->getInverse(Ifc2x3::Type::IfcProduct);
					for ( IfcEntityList::it it = products->begin(); it != products->end(); ++ it ) {
						entities->push(reinterpret_pointer_cast<IfcBaseClass,Ifc2x3::IfcProduct>(*it));
					}
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
		
		IfcGeomObjects::IfcMesh* shape;
		IfcGeom::ShapeList shapes;

		if ( !IfcGeom::convert_shapes(shaperep,shapes) ) {
			_nextShape();
			continue;
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
		// Note that openings for IfcOpeningElements are not processed
		Ifc2x3::IfcRelVoidsElement::list openings = Ifc2x3::IfcRelVoidsElement::list();
		if ( ifc_product->is(Ifc2x3::Type::IfcElement) && !ifc_product->is(Ifc2x3::Type::IfcOpeningElement) ) {
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

		if ( openings && openings->Size() ) {
			IfcGeom::ShapeList opened_shapes;
			try {
				IfcGeom::convert_openings(ifc_product,openings,shapes,trsf,opened_shapes);
			} catch(...) { 
				Ifc::LogMessage("Error","Error processing openings for:",ifc_product->entity); 
			}
			if ( use_world_coords ) {
				for ( IfcGeom::ShapeList::const_iterator it = opened_shapes.begin(); it != opened_shapes.end(); ++ it ) {
					it->first->PreMultiply(trsf);
				}
				trsf = gp_Trsf();
			}
			shape = new IfcGeomObjects::IfcMesh(shaperep->entity->id(),opened_shapes);
			for ( IfcGeom::ShapeList::const_iterator it = opened_shapes.begin(); it != opened_shapes.end(); ++ it ) {
				delete it->first;
				delete it->second;
			}
		} else if ( use_world_coords ) {
			for ( IfcGeom::ShapeList::const_iterator it = shapes.begin(); it != shapes.end(); ++ it ) {
				it->first->PreMultiply(trsf);
			}
			trsf = gp_Trsf();
			shape = new IfcGeomObjects::IfcMesh(shaperep->entity->id(),shapes);
		} else {
			shape = new IfcGeomObjects::IfcMesh(shaperep->entity->id(),shapes);
		}

		IfcGeomObjects::IfcGeomObject* geom_obj = new IfcGeomObjects::IfcGeomObject(ifc_product->entity->id(), parent_id, name, 
			Ifc2x3::Type::ToString(ifc_product->type()), guid, trsf, shape);

		for ( IfcGeom::ShapeList::const_iterator it = shapes.begin(); it != shapes.end(); ++ it ) {
			delete it->first;
		}

		return geom_obj;
	}	
}

bool IfcGeomObjects::Next() {
	if ( current_geom_obj ) {
		delete current_geom_obj->mesh;
		delete current_geom_obj;
	}
	if ( entities ) {
		++inner;
	}
	current_geom_obj = _get();
	if ( ! current_geom_obj ) {
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
	returned_objects.clear();
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
	return current_geom_obj;
}
bool IfcGeomObjects::Init(const char* fn, bool world_coords) {
	return IfcGeomObjects::Init(fn, world_coords, 0, 0);
}
bool IfcGeomObjects::Init(const char* fn, bool world_coords, std::ostream* log1, std::ostream* log2) {
	Ifc::SetOutput(log1,log2);
	use_world_coords = world_coords;
	if ( !Ifc::Init(fn) ) return false;

	shapereps = Ifc::EntitiesByType<Ifc2x3::IfcShapeRepresentation>();
	if ( ! shapereps ) return false;
	
	outer = shapereps->begin();
	entities.reset();
	current_geom_obj = _get();
	
	if ( ! current_geom_obj ) return false;

	done = 0;
	total = shapereps->Size();
	return true;
}
bool IfcGeomObjects::Init(std::istream& f, int len, bool world_coords, std::ostream* log1, std::ostream* log2) {
	Ifc::SetOutput(log1,log2);
	use_world_coords = world_coords;
	if ( !Ifc::Init(f, len) ) return false;

	shapereps = Ifc::EntitiesByType<Ifc2x3::IfcShapeRepresentation>();
	if ( ! shapereps ) return false;
	
	outer = shapereps->begin();
	entities.reset();
	current_geom_obj = _get();
	
	if ( ! current_geom_obj ) return false;

	done = 0;
	total = shapereps->Size();
	return true;
}
bool IfcGeomObjects::Init(void* data, int len) {
	Ifc::SetOutput(0,0);
	use_world_coords = true;
	weld_vertices = false;
	if ( !Ifc::Init(data, len) ) return false;

	shapereps = Ifc::EntitiesByType<Ifc2x3::IfcShapeRepresentation>();
	if ( ! shapereps ) return false;
	
	outer = shapereps->begin();
	entities.reset();
	current_geom_obj = _get();
	
	if ( ! current_geom_obj ) return false;

	done = 0;
	total = shapereps->Size();
	return true;
}
int IfcGeomObjects::Progress() {
	return 100 * done / total;
}
std::string IfcGeomObjects::GetLog() {
	return Ifc::GetLog();
}
