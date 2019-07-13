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

#include <gp_Pnt.hxx>
#include <IntTools_FaceFace.hxx>
#include <BRepAlgoAPI_Common.hxx>

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



bool faces_overlap(TopoDS_Face f1, TopoDS_Face f2) {



	BRepAlgoAPI_Common common(f1, f2);
	TopoDS_Shape ashape1 = common.Shape();

	//std::cout << "Is the Shape empty ? " << ashape1.IsNull() << std::endl;
	

	BRepTools::Write(ashape1, "d.brep");
	return 0;



}

gp_Dir gives_normal(TopoDS_Face aface) {
	Handle(Geom_Surface) surf = BRep_Tool::Surface(aface);
	Handle(Geom_Plane) pln;
	pln = Handle(Geom_Plane)::DownCast(surf);
	gp_Pln plan = Handle(Geom_Plane)::DownCast(surf)->Pln();
	gp_Dir normal_direction = pln->Pln().Axis().Direction();
	return normal_direction;
}


void print_coordinates(gp_Dir normal_direction) {
	Standard_Real x_coord = normal_direction.X();
	Standard_Real y_coord = normal_direction.Y();
	Standard_Real z_coord = normal_direction.Z();
	
	if (x_coord || x_coord==0) {
		/*std::cout << "X: " << x_coord << std::endl;*/
	}

	else {
		/*std::cout << "non" << std::endl;*/
	}


	if (y_coord || y_coord == 0) {
		/*std::cout << "Y: " << y_coord << std::endl;*/
		
	}

	else{ /*std::cout << "non" << std::endl;*/ }

	if (z_coord || z_coord == 0) {
		/*std::cout << "Z: " << z_coord << std::endl;*/
		
	}
	else { /*std::cout << "non" << std::endl;*/ }



}


struct WallFace {

	std::string GUI; 
	TopoDS_Face aface; 
	Standard_Real area; 

};

bool compareByArea(const WallFace &a, const WallFace &b)
{
	return a.area < b.area;
}


namespace latebound_access {

	template <typename T>
	void set(IfcUtil::IfcBaseClass* inst, const std::string& attr, T t);

	template <typename T>
	void set_enumeration(IfcUtil::IfcBaseClass*, const std::string&, const IfcParse::enumeration_type*, T) {}

	template <>
	void set_enumeration(IfcUtil::IfcBaseClass* inst, const std::string& attr, const IfcParse::enumeration_type* enum_type, std::string t) {
		std::vector<std::string>::const_iterator it = std::find(
			enum_type->enumeration_items().begin(),
			enum_type->enumeration_items().end(),
			t);

		return set(inst, attr, IfcWrite::IfcWriteArgument::EnumerationReference(it - enum_type->enumeration_items().begin(), it->c_str()));
	}

	template <typename T>
	void set(IfcUtil::IfcBaseClass* inst, const std::string& attr, T t) {
		auto decl = inst->declaration().as_entity();
		auto i = decl->attribute_index(attr);

		auto attr_type = decl->attribute_by_index(i)->type_of_attribute();
		if (attr_type->as_named_type() && attr_type->as_named_type()->declared_type()->as_enumeration_type()) {
			set_enumeration(inst, attr, attr_type->as_named_type()->declared_type()->as_enumeration_type(), t);
		}

		IfcWrite::IfcWriteArgument* a = new IfcWrite::IfcWriteArgument;
		a->set(t);
		inst->data().attributes()[i] = a;
	}

	IfcUtil::IfcBaseClass* create(IfcParse::IfcFile& f, const std::string& entity) {
		auto decl = f.schema()->declaration_by_name(entity);
		auto data = new IfcEntityInstanceData(decl);
		auto inst = f.schema()->instantiate(data);
		if (decl->is("IfcRoot")) {
			IfcParse::IfcGlobalId guid;
			latebound_access::set(inst, "GlobalId", (std::string) guid);
		}
		return f.addEntity(inst);
	}
}


int main() {

	// Open the Duplex file
	/*IfcParse::IfcFile f("C:/Users/jlutt/Documents/BIM/Models database/Internet/030811DuplexModel-IFC-2011-05-05/Duplex_A_20110505.ifc");*/
	IfcParse::IfcFile f("C:/Users/jlutt/Desktop/Duplex2.ifc");


	auto person = latebound_access::create(f, "IfcPerson");
	latebound_access::set(person, "FamilyName", std::string("IfcOpenShell"));
	latebound_access::set(person, "GivenName", std::string("IfcOpenShell"));


	//std::ofstream f("IfcAdvancedHouse.ifc");
	//f << file;

	// Get the IfcSpace entities
	IfcEntityList::ptr entities(new IfcEntityList());
	entities = f.instances_by_type("IfcSpace");

	// Test on an indivual IFC entity 
	//IfcEntityList::it it = entities->begin();
	//IfcSchema::IfcProduct * prod = (IfcSchema::IfcProduct*)*it;
	//IfcSchema::IfcRepresentation* body_rep = find_representation(prod, "Body");

	// Building the compound to store the spaces and create the builder 
	// to add them to the compound
	BRep_Builder compound_builder;
	TopoDS_Compound face_compound;
	compound_builder.MakeCompound(face_compound);

	// Settings to convert IFC definition to Brep
	IfcGeom::IteratorSettings settings;
	settings.set(IfcGeom::IteratorSettings::USE_WORLD_COORDS, true);
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


		// For now only the faces of 2 spaces are stored
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
			//if (nom == "2gRXFgjRn2HPE$YoDLX3FV" and normal_direction.Z() == 0) {
			//	//std::cout << "The normal of the face space has the following coordinates:" << std::endl;
			//	//std::cout << "X: " << x_coord << std::endl;
			//	//std::cout << "Y: " << y_coord << std::endl;
			//	//std::cout << "Z: " << z_coord << std::endl;

			//	compound_builder.Add(face_compound, aface);
			//}

			//if (nom == "0BTBFw6f90Nfh9rP1dlXre" and normal_direction.Z() == 0) {
			//	//std::cout << "The normal of the face space has the following coordinates:" << std::endl;
			//	//std::cout << "X: " << x_coord << std::endl;
			//	//std::cout << "Y: " << y_coord << std::endl;
			//	//std::cout << "Z: " << z_coord << std::endl;

			//	compound_builder.Add(face_compound, aface);
			//}


			////SECOND CHECK 
			///*and normal_direction.Z()*/
			//if (nom == "0BTBFw6f90Nfh9rP1dlXri") {
			//	//std::cout << "The normal of the face space has the following coordinates:" << std::endl;
			//	//std::cout << "X: " << x_coord << std::endl;
			//	//std::cout << "Y: " << y_coord << std::endl;
			//	//std::cout << "Z: " << z_coord << std::endl;

			//	compound_builder.Add(face_compound, aface);
			//}


			//if (nom == "0BTBFw6f90Nfh9rP1dlXrc") {
			//	//std::cout << "The normal of the face space has the following coordinates:" << std::endl;
			//	//std::cout << "X: " << x_coord << std::endl;
			//	//std::cout << "Y: " << y_coord << std::endl;
			//	//std::cout << "Z: " << z_coord << std::endl;

			//	compound_builder.Add(face_compound, aface);
			//}

			////SECOND CHECK 





			compound_builder.Add(face_compound, aface);





		}


	}



	BRepTools::Write(face_compound, "spaces.brep");




	// Get the IfcWall entities
	IfcEntityList::ptr wall_entities(new IfcEntityList());
	wall_entities = f.instances_by_type("IfcWall");

	TopoDS_Compound wall_faces_compound;
	BRep_Builder wall_compound_builder;
	wall_compound_builder.MakeCompound(wall_faces_compound);

	// Loop over each wall entity to 1. Get the vertical faces (the ones with the highest surface area) and 2. check for each of theses faces 
	// if it overlaps with a space face
	int jecompte = 0;


	TopoDS_Compound fortest;
	BRep_Builder test;
	test.MakeCompound(fortest);



	ofstream myfile;
	myfile.open("autreexample3.txt");



	for (IfcEntityList::it it = wall_entities->begin(); it != wall_entities->end(); ++it) {
		jecompte++;


		IfcUtil::IfcBaseEntity * wall_entity = (IfcUtil::IfcBaseEntity*)*it;
		std::string nom = *(wall_entity)->get("GlobalId");

		


		/*if (nom == "2O2Fr$t4X7Zf8NOew3FL96") {*/
			/*std::cout << nom << std::endl;*/
			IfcUtil::IfcBaseEntity * entity = (IfcUtil::IfcBaseEntity*)*it;
			IfcSchema::IfcProduct * prod = (IfcSchema::IfcProduct*)*it;

			// Get the Body and Axis representations (sometimes we don't have IfcAxisRepresentation)
			IfcSchema::IfcRepresentation* body_rep = find_representation(prod, "Body");
			IfcGeom::BRepElement<double, double>* elem = temp.convert(settings, body_rep, wall_entity);


			IfcSchema::IfcRepresentation* axis_rep = find_representation(prod, "Axis");

			// Get the Brep definition of the IFC entity
			/*IfcGeom::BRepElement<double, double>* axis_elem = temp.convert(settings, axis_rep, entity);
			TopoDS_Compound edges_compound = axis_elem->geometry().as_compound(true);*/

			/*TopExp_Explorer edge_exp(edges_compound, TopAbs_EDGE);
			int icom = 0;
			for (TopExp_Explorer edge_exp(edges_compound, TopAbs_EDGE); edge_exp.More(); edge_exp.Next()) {
				icom++;


			}*/

			/*	std::cout << "nb de edges " << icom << std::endl;
				BRepTools::Write(edges_compound, "edge.brep");*/


				// Convert the geometric representation to Brep
			TopoDS_Compound compound = elem->geometry().as_compound(true);
			//TopoDS_Compound compoundaxis = axis_elem->geometry().as_compound(true);
			BRepTools::Write(compound, "wall.brep");

			TopExp_Explorer wall_exp(compound, TopAbs_FACE);

			std::vector<WallFace>face_storing;

			int compterr = 0;
			for (TopExp_Explorer exp(compound, TopAbs_FACE); exp.More(); exp.Next()) {
				WallFace awallface;
				compterr++;

				TopoDS_Face aface;
				aface = TopoDS::Face(exp.Current());
				awallface.aface = aface;

				GProp_GProps System;
				BRepGProp::SurfaceProperties(aface, System);
				Standard_Real area = System.Mass();
				/*	std::cout << "sur : " << sur << " ";*/
				/*	surfaces.push_back(sur);*/
				awallface.area = area;
				/*std::cout << area << " "; */
				face_storing.push_back(awallface);


			}


			//std::cout << compterr << std::endl; 
			std::sort(face_storing.begin(), face_storing.end(), compareByArea);

			//std::cout << nom << std::endl;
			/*	for (auto&& x : face_storing) {
					std::cout << x.area << '\n';
				}*/

			int avantdernier = face_storing.size() - 2;
			int dernier = face_storing.size() - 1;

			Standard_Real AD = face_storing[avantdernier].area;
			Standard_Real D = face_storing[dernier].area;

		/*	std::cout << "Avant dernier: " << AD << std::endl;
			std::cout << "Dernier: " << D << std::endl;*/

			/*	std::cout << std::endl;*/


			TopoDS_Face face1 = face_storing[avantdernier].aface;
			TopoDS_Face face2 = face_storing[dernier].aface;
			bool face1_check;
			bool face2_check;


			// Get the center point of face1
			GProp_GProps massProps;
			BRepGProp::SurfaceProperties(face1, massProps);
			gp_Pnt gPt = massProps.CentreOfMass();

			// Get the center point of face2 
			GProp_GProps massProps2;
			BRepGProp::SurfaceProperties(face2, massProps);
			gp_Pnt gPt2 = massProps2.CentreOfMass();


			//TopoDS_Compound fortest;
			//BRep_Builder test;
			//test.MakeCompound(fortest);

			int icop = 0; 
			char l = 'a'; 

			for (TopExp_Explorer space_expp(face_compound, TopAbs_FACE); space_expp.More(); space_expp.Next()) {
				TopoDS_Face aspaceface = TopoDS::Face(space_expp.Current());

				/*	std::cout << faces_overlap(face1, aspaceface) << std::endl;*/

				/*	test.Add(fortest, face1);
					test.Add(fortest, face2);
					test.Add(fortest, aspaceface);
	*/				icop++; 

				
					BRepAlgoAPI_Common common(face1, aspaceface);
					TopoDS_Shape ashape1 = common.Shape();

					BRepAlgoAPI_Common common2(face2, aspaceface);
					TopoDS_Shape ashape2 = common2.Shape();

				/*	std::cout << "Is the Shape empty ? " << ashape1.IsNull() << std::endl; */
					test.Add(fortest, ashape1);
					test.Add(fortest, ashape2);


					/*std::cout << "Shape 1" << std::endl; */
					TopExp_Explorer jexp(ashape1, TopAbs_FACE);
				for (; jexp.More(); jexp.Next()) {

						TopoDS_Face faceone = TopoDS::Face(jexp.Current());
						gp_Dir directionfaceone = gives_normal(faceone);
						print_coordinates(directionfaceone);
						myfile << nom <<","<<"face 1,"<<"X,"<<directionfaceone.X() << ",Y," << directionfaceone.Y() << ",Z," << directionfaceone.Z()<<"\n";

					}


				/*	std::cout << "Shape 2" << std::endl;*/
					TopExp_Explorer jexp2(ashape2, TopAbs_FACE);
					for (; jexp2.More(); jexp2.Next()) {

						TopoDS_Face facetwo = TopoDS::Face(jexp2.Current());
						gp_Dir directionfacetwo = gives_normal(facetwo);
						print_coordinates(directionfacetwo);
						myfile << nom << "," << "face 2," << "X," << directionfacetwo.X() << ",Y," << directionfacetwo.Y() << ",Z," << directionfacetwo.Z()<<"\n";

					}



				/*	TopoDS_Face facetwo = TopoDS::Face(ashape2);*/

					
			/*		gp_Dir directionfacetwo = gives_normal(facetwo);*/

					
				/*	print_coordinates(directionfacetwo);*/


					//BRepTools::Write(fortest, l+".brep");

					l++; 
				



				BRepTools::Write(fortest, "untest4.brep");
	/*
				BRepAlgoAPI_Common common2(face2, aspaceface);
				TopoDS_Shape ashape2 = common2.Shape();
				test.Add(fortest, ashape2);
					*/


				//TopoDS_Face aspaceface = TopoDS::Face(space_expp.Current());
				//GProp_GProps massPropss;
				//BRepGProp::SurfaceProperties(aspaceface, massPropss);
				//gp_Pnt gPtt = massPropss.CentreOfMass();

				//Standard_Real dist1 = gPtt.Distance(gPt);

				//Standard_Real dist2 = gPtt.Distance(gPt2);

				////std::cout << "The distance between f1 center and this space is " << dist1 << std::endl;
				//std::cout << "The distance between f2 center and this space is " << dist2 << std::endl;

			/*}*/
		/*	BRepTools::Write(fortest, "unetest.brep");*/
			/*BRepTools::Write(fortest, "monessai2.brep");*/
			/*std::cout << std::endl;*/




















		}
	}
	myfile.close();
}

