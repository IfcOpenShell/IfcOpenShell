#include <iostream>
#ifdef USE_IFC4
#include "../ifcparse/Ifc4.h"
#define IfcSchema Ifc4
#else
#include "../ifcparse/Ifc2x3.h"
#define IfcSchema Ifc2x3
#endif
#include "..\ifcgeom\IfcGeom.h"


#include "../ifcparse/IfcBaseClass.h"
#include "../ifcparse/IfcHierarchyHelper.h"
#include "../ifcgeom/IfcGeom.h"
#include "../ifcgeom_schema_agnostic/Serialization.h"

#include "../ifcgeom_schema_agnostic/Kernel.h"

#if USE_VLD
#include <vld.h>
#endif

#include "../ifcparse/IfcSchema.h"
#include "../ifcgeom_schema_agnostic/IfcGeomIterator.h"
#include "../ifcgeom/IfcGeomElement.h"

#include "../ifcgeom/IfcRepresentationShapeItem.h"
#include <Geom_Plane.hxx>
#include <BRepAlgo_Common.hxx>

#include <BRepGProp.hxx>
#include <GProp_GProps.hxx>


#include <AIS_Shape.hxx>
#include <AIS_InteractiveContext.hxx>

IfcSchema::IfcRepresentation* find_representation(const IfcSchema::IfcProduct* product, const std::string& identifier) {
	if (!product->hasRepresentation()) return 0;
	IfcSchema::IfcProductRepresentation* prod_rep = product->Representation();
	IfcSchema::IfcRepresentation::list::ptr reps = prod_rep->Representations();
	for (IfcSchema::IfcRepresentation::list::it it = reps->begin(); it != reps->end(); ++it) {
		if ((**it).hasRepresentationIdentifier() && (**it).RepresentationIdentifier() == identifier) {
			return *it;
		}
	}
	return 0;
}



int main() {

	// Open the Duplex file
	IfcParse::IfcFile f("C:/Users/jlutt/Documents/BIM/Models database/Internet/030811DuplexModel-IFC-2011-05-05/Duplex_A_20110505.ifc");

	// Get the IfcSpace entities
	IfcEntityList::ptr entities(new IfcEntityList());
	entities = f.instances_by_type("IfcSpace");


	// Test on an indivual IFC entity 
	//IfcEntityList::it it = entities->begin();
	//IfcSchema::IfcProduct * prod = (IfcSchema::IfcProduct*)*it;
	//IfcSchema::IfcRepresentation* body_rep = find_representation(prod, "Body");


	// Building the compound to store the spaces
	BRep_Builder compound_builder;
	TopoDS_Compound face_compound;
	compound_builder.MakeCompound(face_compound);



	// Settings to convert IFC definition to Brep
	IfcGeom::IteratorSettings settings;
	settings.set(IfcGeom::IteratorSettings::USE_WORLD_COORDS, false);
	settings.set(IfcGeom::IteratorSettings::WELD_VERTICES, false);
	settings.set(IfcGeom::IteratorSettings::CONVERT_BACK_UNITS, true);
	settings.set(IfcGeom::IteratorSettings::DISABLE_TRIANGULATION, true);
	IfcGeom::Kernel temp(&f);

	// Loop to store the vertical faces of the spaces in the compound
	for (IfcEntityList::it it = entities->begin(); it != entities->end(); ++it) {

		IfcUtil::IfcBaseEntity * entity = (IfcUtil::IfcBaseEntity*)*it;
		std::string nom = *(entity)->get("GlobalId");
		IfcSchema::IfcProduct * prod = (IfcSchema::IfcProduct*)*it;
		IfcSchema::IfcRepresentation* body_rep = find_representation(prod, "Body");

		// Get the Brep definition of the IFC entity
		IfcGeom::BRepElement<double, double>* elem = temp.convert(settings, body_rep, entity);


		TopoDS_Compound compound = elem->geometry().as_compound(true);
		TopExp_Explorer exp(compound, TopAbs_FACE);

		int nface = 0;

		for (; exp.More(); exp.Next()) {

			nface++;

			// Storing the face
			TopoDS_Face aface;
			aface = TopoDS::Face(exp.Current());
			Handle(Geom_Surface) surf = BRep_Tool::Surface(aface);
			Handle(Geom_Plane) pln;
			pln = Handle(Geom_Plane)::DownCast(surf);
			gp_Pln plan = Handle(Geom_Plane)::DownCast(surf)->Pln();
			gp_Dir normal_direction = pln->Pln().Axis().Direction();
			Standard_Real x_coord = normal_direction.X();
			Standard_Real y_coord = normal_direction.Y();
			Standard_Real z_coord = normal_direction.Z();

			// Checking for 2 specific spaces (those are 2 spaces witch each 4 faces)
			if (nom == "2gRXFgjRn2HPE$YoDLX3FV" and normal_direction.Z() == 0) {
				//std::cout << "The normal of the face space has the following coordinates:" << std::endl;
				//std::cout << "X: " << x_coord << std::endl;
				//std::cout << "Y: " << y_coord << std::endl;
				//std::cout << "Z: " << z_coord << std::endl;

				compound_builder.Add(face_compound, aface);
			}

			if (nom == "0BTBFw6f90Nfh9rP1dlXre" and normal_direction.Z() == 0) {
				//std::cout << "The normal of the face space has the following coordinates:" << std::endl;
				//std::cout << "X: " << x_coord << std::endl;
				//std::cout << "Y: " << y_coord << std::endl;
				//std::cout << "Z: " << z_coord << std::endl;

				compound_builder.Add(face_compound, aface);
			}


			//compound_builder.Add(face_compound, aface);


		}




	}


	// Check the compound content


	// GO OVER EACH FACE ONLY ONCE 


	
	int comptage = 0;
	//for (; forchecking.More(); forchecking.Next()) {
	//	comptage++;
	//}

	std::cout << "the total numer of faces in this compound is of " << comptage << std::endl;

	// Get the IfcWall entities
	IfcEntityList::ptr wall_entities(new IfcEntityList());
	wall_entities = f.instances_by_type("IfcWall");

	// Loop over each wall entity to 1. Get the vertical faces (the ones with the highest surface area) and 2. check for each of theses faces 
	// if it overlaps with a space face
	for (IfcEntityList::it it = wall_entities->begin(); it != wall_entities->end(); ++it) {

		IfcUtil::IfcBaseEntity * wall_entity = (IfcUtil::IfcBaseEntity*)*it;
		//std::string nom = *(wall_entity)->get("Name");
		//std::cout << nom << std::endl;
		IfcUtil::IfcBaseEntity * entity = (IfcUtil::IfcBaseEntity*)*it;
		IfcSchema::IfcProduct * prod = (IfcSchema::IfcProduct*)*it;

		IfcSchema::IfcRepresentation* body_rep = find_representation(prod, "Body");
		IfcGeom::BRepElement<double, double>* elem = temp.convert(settings, body_rep, wall_entity);
		TopoDS_Compound compound = elem->geometry().as_compound(true);
		TopExp_Explorer wall_exp(compound, TopAbs_FACE);
		int nbface = 0;

		// To store the 2 faces of interest of the wall 
		TopoDS_Face face1;
		TopoDS_Face face2;

		// Tools to calculate the surface area of the faces of the wall 
		GProp_GProps myProps;
		double surfaces[2];
		surfaces[0] = 0;
		surfaces[1] = 0;


		for (; wall_exp.More(); wall_exp.Next()) {

			nbface++;
			TopoDS_Face aface;
			aface = TopoDS::Face(wall_exp.Current());
			Handle(Geom_Surface) surf = BRep_Tool::Surface(aface);
			Handle(Geom_Plane) pln;
			pln = Handle(Geom_Plane)::DownCast(surf);
			gp_Pln plan = Handle(Geom_Plane)::DownCast(surf)->Pln();
			gp_Dir normal_direction = pln->Pln().Axis().Direction();

			BRepGProp::SurfaceProperties(wall_exp.Current(), myProps);
			Standard_Real area = myProps.Mass();

			if (area > surfaces[0]) {
				surfaces[0] = area;
				face1 = aface;
			}
			if (area > surfaces[1]) {
				surfaces[1] = area;
				face2 = aface;

			}

			//std::cout << area << std::endl;
	/*		for (TopExp_Explorer(...); More(); Next()*/

			// Check whether faces of the wall overlap with a space face 
			for (TopExp_Explorer forchecking(face_compound, TopAbs_FACE);forchecking.More();forchecking.Next()) {
				TopoDS_Face aspace;
				aspace = TopoDS::Face(forchecking.Current());
				BRepAlgo_Common bc(face1, aspace);
				TopoDS_Shape com1 = bc.Shape();
				BRepTools::Write(com1, "johan.brep");



				//	// OCCT viewer trial
				//	Handle(V3d_Viewer)aViewer;
				//	Handle(AIS_InteractiveContext)aContext;
				//	aContext = new AIS_InteractiveContext(aViewer);
				//	Handle(AIS_Shape) anAis = new AIS_Shape(com1);
				//	aContext->OpenLocalContext();
				//	aContext->Display();
				//}

				//for (; forchecking.More(); forchecking.Next()) {
				//	TopoDS_Face aspace;
				//	aspace = TopoDS::Face(forchecking.Current());
				//	BRepAlgo_Common bc(face2, aspace);
				//	TopoDS_Shape com2 = bc.Shape();
				//	BRepTools::Write(com2, "johann.brep");
				//}




			}

			//std::cout << surfaces[0] << " " << surfaces[1] << std::endl;


			//;std::cout << nbface << std::endl; 



		}













		//IfcUtil::IfcBaseEntity * entity = (IfcUtil::IfcBaseEntity*)*it;


		//IfcGeom::IteratorSettings settings;
		//settings.set(IfcGeom::IteratorSettings::USE_WORLD_COORDS, false);
		//settings.set(IfcGeom::IteratorSettings::WELD_VERTICES, false);
		//settings.set(IfcGeom::IteratorSettings::CONVERT_BACK_UNITS, true);
		//settings.set(IfcGeom::IteratorSettings::DISABLE_TRIANGULATION, true);
		////IfcGeom::Kernel temp;
		//IfcGeom::Kernel temp(&f);

		//IfcGeom::BRepElement<double, double>* elem = temp.convert(settings, body_rep, entity);
		//TopoDS_Compound compound = elem->geometry().as_compound(true);
		//TopExp_Explorer exp(compound, TopAbs_FACE);

		//const Standard_Real XX = 0;
		//const Standard_Real YY = 1;
		//const Standard_Real ZZ = 0;

		//const gp_XYZ lol(XX, YY, ZZ);


		//gp_Dir s(lol);



		//int compto = 0; 


		//for (; exp.More(); exp.Next()) {

		//	compto++; 

		//	TopoDS_Face aface;
		//	aface = TopoDS::Face(exp.Current());
		//	Handle(Geom_Surface) surf = BRep_Tool::Surface(aface);
		//	Handle(Geom_Plane) pln;
		//	pln = Handle(Geom_Plane)::DownCast(surf);
		//	gp_Pln plan = Handle(Geom_Plane)::DownCast(surf)->Pln();

		//	gp_Dir normal_direction = pln->Pln().Axis().Direction();

		///*	if (normal_direction == s)std::cout << "YEEEEEES" << std::endl; */

		//	Standard_Real x_coord = normal_direction.X();
		//	Standard_Real y_coord = normal_direction.Y();
		//	Standard_Real z_coord = normal_direction.Z();
		//	std::cout << "The normal of the wall has the following coordinates:" << std::endl;
		//	std::cout << "X: " << x_coord << std::endl;
		//	std::cout << "Y: " << y_coord << std::endl;
		//	std::cout << "Z: " << z_coord << std::endl;

		//	std::cout << endl; 


		//}



		//gp_Dir normalX = gp_Dir();
		//Standard_Real x_coordo = normalX.X();
		//Standard_Real y_coordo = normalX.Y();
		//Standard_Real z_coordo = normalX.Z();

		//std::cout << "Other" << std::endl;
		//std::cout << "other X: "<< x_coordo<<std::endl;
		//std::cout << "other Y: " << y_coordo << std::endl;
		//std::cout << "other Z: " << z_coordo << std::endl;

		//std::cout << compto; 

		//TopoDS_Shape s1; 
		//TopoDS_Shape s2;
		//BRepAlgo_Common common(s1, s2); 




		//







	}



}
