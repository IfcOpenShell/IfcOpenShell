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

#include "Max.h"
#include "stdmat.h"
#include "istdplug.h"

#include "../ifcmax/IfcMax.h"
#include "../ifcmax/MaxMaterials.h"
#include "../ifcgeom/IfcGeomObjects.h"

int controlsInit = false;

BOOL WINAPI DllMain(HINSTANCE hinstDLL,ULONG fdwReason,LPVOID lpvReserved) {	
	if (!controlsInit) {
		controlsInit = true;
		InitCommonControls();
	}	
	return true;
}

__declspec( dllexport ) const TCHAR* LibDescription() {
	return _T("IfcOpenShell IFC Importer");
}

__declspec( dllexport ) int LibNumberClasses() { return 1; }

static class IFCImpClassDesc:public ClassDesc {
public:
	int                     IsPublic() {return 1;}
	void *                  Create(BOOL loading = FALSE) {return new IFCImp;} 
	const TCHAR *			ClassName() {return _T("IFCImp");}
	SClass_ID               SuperClassID() {return SCENE_IMPORT_CLASS_ID;} 
	Class_ID                ClassID() {return Class_ID(0x3f230dbf, 0x5b3015c2);}
	const TCHAR*			Category() {return _T("Chrutilities");}
} IFCImpDesc;

__declspec( dllexport ) ClassDesc* LibClassDesc(int i) {
	return i == 0 ? &IFCImpDesc : 0;
}

__declspec( dllexport ) ULONG LibVersion() {
	return VERSION_3DSMAX;
}

int IFCImp::ExtCount() { return 1; }

const TCHAR * IFCImp::Ext(int n) {
	return n == 0 ? _T("IFC") : _T("");
}

const TCHAR * IFCImp::LongDesc() {
	return _T("IfcOpenShell IFC Importer for 3ds Max");
}

const TCHAR * IFCImp::ShortDesc() {
	return _T("Industry Foundation Classes");
}

const TCHAR * IFCImp::AuthorName() {
	return _T("Thomas Krijnen");
}

const TCHAR * IFCImp::CopyrightMessage() {
	return _T("Copyight (c) 2011 IfcOpenShell");
}

const TCHAR * IFCImp::OtherMessage1() {
	return _T("");
}

const TCHAR * IFCImp::OtherMessage2() {
	return _T("");
}

unsigned int IFCImp::Version() {
	return 12;
}

static BOOL CALLBACK AboutBoxDlgProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam) {
	return TRUE;
}       

void IFCImp::ShowAbout(HWND hWnd) {} 

DWORD WINAPI fn(LPVOID arg) { return 0; }

int IFCImp::DoImport(const TCHAR *name, ImpInterface *impitfc, Interface *itfc, BOOL suppressPrompts) {

	itfc->ProgressStart("Importing file...", TRUE, fn, NULL);

	IfcGeomObjects::Settings(IfcGeomObjects::USE_WORLD_COORDS,false);
	IfcGeomObjects::Settings(IfcGeomObjects::WELD_VERTICES,true);
	IfcGeomObjects::Settings(IfcGeomObjects::SEW_SHELLS,true);

	if ( ! IfcGeomObjects::Init((char*)name,0,0) ) return false;

	//std::map<int, TriObject*> dict;
	MtlBaseLib* mats = itfc->GetSceneMtls();
	int slot = mats->Count();

	do{

		const IfcGeomObjects::IfcGeomObject* o = IfcGeomObjects::Get();
		
		Mtl *m;
		const int matIndex = mats->FindMtlByName(MSTR(o->type.c_str()));
		if ( matIndex == -1 ) {
			StdMat2* stdm = GetMaterial(o->type);
			m = stdm;
			m->SetName(o->type.c_str());
			mats->Add(m);
			itfc->PutMtlToMtlEditor(m,slot++);
		} else {
			m = static_cast<Mtl*>((*mats)[matIndex]);
		} 
		
		// This mapping is useless for now, because this even in case
		// meshes entities in IFC share the same representation elements
		// they will never be given the same id.
		// TODO: Fix this!
		// std::map<int, TriObject*>::const_iterator it = dict.find(o->mesh->id);

		TriObject* tri;
		// if ( it == dict.end() ) {
			tri = CreateNewTriObject();
			const int numVerts = o->mesh->verts.size()/3;
			tri->mesh.setNumVerts(numVerts);
			for( int i = 0; i < numVerts; i ++ ) {
				tri->mesh.setVert(i,o->mesh->verts[3*i+0],o->mesh->verts[3*i+1],o->mesh->verts[3*i+2]);
			}
			const int numFaces = o->mesh->faces.size()/3;
			tri->mesh.setNumFaces(numFaces);
			for( int i = 0; i < numFaces; i ++ ) {
				tri->mesh.faces[i].setVerts(o->mesh->faces[3*i+0],o->mesh->faces[3*i+1],o->mesh->faces[3*i+2]);
				tri->mesh.faces[i].setEdgeVisFlags(o->mesh->edges[3*i+0],o->mesh->edges[3*i+1],o->mesh->edges[3*i+2]);
			}
				
			tri->mesh.buildNormals();
			// Either use this or undefine the FACESETS_AS_COMPOUND option in IfcGeom.h to have
			// properly oriented normals. Using only the line below will result in a consistent
			// orientation of normals accross shells, but not always oriented towards the
			// outside.
			// tri->mesh.UnifyNormals(false);
			tri->mesh.BuildStripsAndEdges();
			tri->mesh.InvalidateTopologyCache();
			tri->mesh.InvalidateGeomCache();

		//	dict[o->mesh->id] = tri;
		// } else {
		// 	tri = (*it).second;
		// }

		ImpNode* node = impitfc->CreateNode();
		node->Reference(tri);
		node->SetName(o->guid.c_str());
		node->GetINode()->SetMtl(m);
		node->SetTransform(0,Matrix3 ( Point3(o->matrix[0],o->matrix[1],o->matrix[2]),Point3(o->matrix[3],o->matrix[4],o->matrix[5]),
			Point3(o->matrix[6],o->matrix[7],o->matrix[8]),Point3(o->matrix[9],o->matrix[10],o->matrix[11]) ));
		impitfc->AddNodeToScene(node);

		itfc->ProgressUpdate(IfcGeomObjects::Progress(),true,"");

	} while ( IfcGeomObjects::Next() );

	IfcGeomObjects::CleanUp();

	itfc->ProgressEnd();
	
	return true;
}