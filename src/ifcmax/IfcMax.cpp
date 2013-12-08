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

#include <Max.h>
#include <stdmat.h>
#include <istdplug.h>

#include "../ifcmax/IfcMax.h"
#include "../ifcgeom/IfcGeomObjects.h"

static const int NUM_MATERIAL_SLOTS = 24;

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

#if MAX_RELEASE > 14000
# define S(x) (TSTR::FromCStr(x.c_str()))
#elif defined(_UNICODE)
# define S(x) (WStr(x.c_str()))
#else
# define S(x) (CStr(x.c_str()))
#endif

Mtl* FindMaterialByName(MtlBaseLib* library, const std::string& material_name) {
	const int mat_index = library->FindMtlByName(S(material_name));
	Mtl* m = 0;
	if (mat_index != -1) {
		m = static_cast<Mtl*>((*library)[mat_index]);
	}
	return m;
}

Mtl* FindOrCreateMaterial(MtlBaseLib* library, Interface* max_interface, int& slot, const IfcGeomObjects::Material& material) {
	Mtl* m = FindMaterialByName(library, material.name());
	if (m == 0) {
		StdMat2* stdm = NewDefaultStdMat();
		const TimeValue t = -1;
		if (material.hasDiffuse()) {
			const double* diffuse = material.diffuse();
			stdm->SetDiffuse(Color(diffuse[0], diffuse[1], diffuse[2]),t);
		}
		if (material.hasSpecular()) {
			const double* specular = material.specular();
			stdm->SetSpecular(Color(specular[0], specular[1], specular[2]),t);
		}
		if (material.hasSpecularity()) {
			stdm->SetShininess(material.specularity(), t);
		}
		if (material.hasTransparency()) {
			stdm->SetOpacity(1.0 - material.transparency(), t);
		}
		m = stdm;
		m->SetName(S(material.name()));
		library->Add(m);
		if (slot < NUM_MATERIAL_SLOTS) {
			max_interface->PutMtlToMtlEditor(m,slot++);
		}
	}
	return m;
}

Mtl* ComposeMultiMaterial(std::map<std::vector<std::string>, Mtl*>& multi_mats, MtlBaseLib* library, Interface* max_interface, int& slot, const std::vector<IfcGeomObjects::Material>& materials, const std::string& object_type, const std::vector<int>& material_ids) {
	std::vector<std::string> material_names;
	bool needs_default = std::find(material_ids.begin(), material_ids.end(), -1) != material_ids.end();
	if (needs_default) {
		material_names.push_back(object_type);
	}
	for (auto it = materials.begin(); it != materials.end(); ++it) {
		material_names.push_back(it->name());
	}
	Mtl* default_material = 0;
	if (needs_default) {
		default_material = FindMaterialByName(library, object_type);
		if (default_material == 0) {
			default_material = NewDefaultStdMat();
			default_material->SetName(S(object_type));
			library->Add(default_material);
			if (slot < NUM_MATERIAL_SLOTS) {
				max_interface->PutMtlToMtlEditor(default_material, slot++);
			}
		}
	}
	if (material_names.size() == 1) {
		if (needs_default) {
			return default_material;
		} else {
			return FindOrCreateMaterial(library, max_interface, slot, *materials.begin());
		}
	}
	std::map<std::vector<std::string>, Mtl*>::const_iterator i = multi_mats.find(material_names);
	if (i != multi_mats.end()) {
		return i->second;
	}
	MultiMtl* multi_mat = NewDefaultMultiMtl();
	multi_mat->SetNumSubMtls(material_names.size());
	int mtl_id = 0;
	if (needs_default) {
		multi_mat->SetSubMtlAndName(mtl_id ++, default_material, default_material->GetName());
	}
	for (auto it = materials.begin(); it != materials.end(); ++it) {
		Mtl* mtl = FindOrCreateMaterial(library, max_interface, slot, *it);
		multi_mat->SetSubMtl(mtl_id ++, mtl);
	}
	library->Add(multi_mat);
	if (slot < NUM_MATERIAL_SLOTS) {
		max_interface->PutMtlToMtlEditor(multi_mat,slot++);
	}
	multi_mats.insert(std::pair<std::vector<std::string>, Mtl*>(material_names, multi_mat));
	return multi_mat;
}

int IFCImp::DoImport(const TCHAR *name, ImpInterface *impitfc, Interface *itfc, BOOL suppressPrompts) {

	IfcGeomObjects::Settings(IfcGeomObjects::USE_WORLD_COORDS,false);
	IfcGeomObjects::Settings(IfcGeomObjects::WELD_VERTICES,true);
	IfcGeomObjects::Settings(IfcGeomObjects::SEW_SHELLS,true);

#ifdef _UNICODE
	int fn_buffer_size = WideCharToMultiByte(CP_UTF8, 0, name, -1, 0, 0, 0, 0);
	char* fn_mb = new char[fn_buffer_size];
	WideCharToMultiByte(CP_UTF8, 0, name, -1, fn_mb, fn_buffer_size, 0, 0);
#else
	const char* fn_mb = name;
#endif

	if ( ! IfcGeomObjects::Init(fn_mb,0,0) ) return false;

	itfc->ProgressStart(_T("Importing file..."), TRUE, fn, NULL);

	MtlBaseLib* mats = itfc->GetSceneMtls();
	int slot = mats->Count();

	std::map<std::vector<std::string>, Mtl*> material_cache;

	do{

		const IfcGeomObjects::IfcGeomObject* o = IfcGeomObjects::Get();

		TSTR o_type = S(o->type());
		TSTR o_guid = S(o->guid());

		Mtl *m = ComposeMultiMaterial(material_cache, mats, itfc, slot, o->mesh().materials(), o->type(), o->mesh().material_ids());

		TriObject* tri = CreateNewTriObject();

		const int numVerts = o->mesh().verts().size()/3;
		tri->mesh.setNumVerts(numVerts);
		for( int i = 0; i < numVerts; i ++ ) {
			tri->mesh.setVert(i,o->mesh().verts()[3*i+0],o->mesh().verts()[3*i+1],o->mesh().verts()[3*i+2]);
		}
		const int numFaces = o->mesh().faces().size()/3;
		tri->mesh.setNumFaces(numFaces);

		bool needs_default = std::find(o->mesh().material_ids().begin(), o->mesh().material_ids().end(), -1) != o->mesh().material_ids().end();

		for( int i = 0; i < numFaces; i ++ ) {
			tri->mesh.faces[i].setVerts(o->mesh().faces()[3*i+0],o->mesh().faces()[3*i+1],o->mesh().faces()[3*i+2]);
			tri->mesh.faces[i].setEdgeVisFlags(o->mesh().edges()[3*i+0],o->mesh().edges()[3*i+1],o->mesh().edges()[3*i+2]);
			MtlID mtlid = o->mesh().material_ids()[i];
			if (needs_default) mtlid ++;
			tri->mesh.faces[i].setMatID(mtlid);
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

		ImpNode* node = impitfc->CreateNode();
		node->Reference(tri);
		node->SetName(o_guid);
		node->GetINode()->Hide(o->type() == "IfcOpeningElement" || o->type() == "IfcSpace");
		if (m) {
			node->GetINode()->SetMtl(m);
		}
		node->SetTransform(0,Matrix3 ( Point3(o->matrix()[0],o->matrix()[1],o->matrix()[2]),Point3(o->matrix()[3],o->matrix()[4],o->matrix()[5]),
			Point3(o->matrix()[6],o->matrix()[7],o->matrix()[8]),Point3(o->matrix()[9],o->matrix()[10],o->matrix()[11]) ));
		impitfc->AddNodeToScene(node);

		itfc->ProgressUpdate(IfcGeomObjects::Progress(),true,_T(""));

	} while ( IfcGeomObjects::Next() );

	IfcGeomObjects::CleanUp();

	itfc->ProgressEnd();
	
	return true;
}