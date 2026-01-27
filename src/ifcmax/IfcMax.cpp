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
#include <set>

#include <stdmat.h>
#include <istdplug.h>
#include <spline3d.h>
#include <splshape.h>
#include <hold.h>

// should fix a iterator missallignment assertion ?
#define IFOPSH_WITH_ROCKSDB

#include "../ifcgeom/Iterator.h"
#include "../ifcgeom/taxonomy.h"
#include "../ifcgeom/ConversionSettings.h"
#include "../ifcgeom/hybrid_kernel.h"

#include "resource.h"
#include "IfcMax.h"

// include those at last, as they cause compile errors regarding boost templates
#include <maxscript/maxscript.h>
#include <maxscript/util/listener.h>


static const Class_ID IFCIMP_CLASS_ID = Class_ID(0x3f230dbf, 0x5b3015c2);
static const TSTR IFCIMP_CLASS_NAME =  _T("IFCImp");
static const TSTR IFCIMP_CATEGORY_NAME = _T("Importer Plugins");

static const int NUM_MATERIAL_SLOTS = 24;

static HINSTANCE hInstance;
static TCHAR *GetString(int id)
{
	static TCHAR buf[256];
	if (hInstance)
		return LoadString(hInstance, id, buf, _countof(buf)) ? buf : NULL;
	return NULL;
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, ULONG /*fdwReason*/, LPVOID /*lpvReserved*/) {
    static int controlsInit = false;
	hInstance = hinstDLL;
	if (!controlsInit) {
		controlsInit = true;
		InitCommonControls();
	}
	return TRUE;
}

static class IFCImpClassDesc :public ClassDesc {
public:
    int                     IsPublic() { return 1; }
    void *                  Create(BOOL /*loading = FALSE*/) { return new IFCImp; }
    // TODO Delete() function?
    const TCHAR* ClassName() { return IFCIMP_CLASS_NAME; }

#if MAX_VERSION_MAJOR >= 24
	const TCHAR *	NonLocalizedClassName() { return ClassName(); }
#endif 

    SClass_ID               SuperClassID() { return SCENE_IMPORT_CLASS_ID; }
    Class_ID				ClassID() { return IFCIMP_CLASS_ID; }
    const TCHAR*			Category() { return IFCIMP_CATEGORY_NAME; }
} IFCImpDesc;

#define DLLEXPORT __declspec(dllexport)

extern "C" {
#if BUILD_FREE_TIER
DLLEXPORT const TCHAR* LibDescription() { return GetString(IDS_LIBDESCRIPTION_FREE); }
#else
	DLLEXPORT const TCHAR* LibDescription() { return GetString(IDS_LIBDESCRIPTION); }
#endif

DLLEXPORT int LibNumberClasses() { return 1; }

DLLEXPORT ClassDesc* LibClassDesc(int i) { return i == 0 ? &IFCImpDesc : 0; }

DLLEXPORT ULONG LibVersion() { return VERSION_3DSMAX; }

} // extern "C"

int IFCImp::ExtCount() { return 1; }

const TCHAR * IFCImp::Ext(int n) { return n == 0 ? _T("IFC") : _T(""); }

const TCHAR * IFCImp::LongDesc() { return GetString(IDS_LONG_DESCRIPTION); }

const TCHAR * IFCImp::ShortDesc() {	return GetString(IDS_SHORT_DESCRIPTION);  }

const TCHAR * IFCImp::AuthorName() { return GetString(IDS_AUTHOR_NAME);  }

const TCHAR * IFCImp::CopyrightMessage() { return GetString(IDS_COPYRIGHT_MESSAGE);  }

const TCHAR * IFCImp::OtherMessage1() {	return _T(""); }

const TCHAR * IFCImp::OtherMessage2() {	return _T(""); }

unsigned int IFCImp::Version() { return 25; }

// TODO Use this in IFCImp::ShowAbout() if/when wanted
//static BOOL CALLBACK AboutBoxDlgProc(HWND /*hWnd*/, UINT /*msg*/, WPARAM /*wParam*/, LPARAM /*lParam*/) {
//	return TRUE;
//}

void IFCImp::ShowAbout(HWND /*hWnd*/) {}

DWORD WINAPI fn(LPVOID /*arg*/) { return 0; }

#if MAX_RELEASE > 14000
# define S(x) (TSTR::FromCStr(x.c_str()))
#elif defined(_UNICODE)
# define S(x) (WStr(x.c_str()))
#else
# define S(x) (CStr(x.c_str()))
#endif


// Function to log messages to the Listener
static void LogToListener(const MCHAR* format, ...) 
{
	if (format == nullptr) {
		return;
	}

	const int BUFFER_SIZE = 2048;
	static MCHAR buffer[BUFFER_SIZE];

	va_list args;

	va_start(args, format);
	int result = _vstprintf_s(buffer, BUFFER_SIZE, format, args);

	va_end(args);

#if BUILD_FREE_TIER
	if(result < 0) {
		the_listener->edit_stream->printf(_M("IfcImp[Free]: Skipped invalid log output !\n"));
		return;
	}
	the_listener->edit_stream->printf(_M("IfcImp[Free]: %s"), buffer);
#else
	if(result < 0) {
		the_listener->edit_stream->printf(_M("IfcImp[Pro]: Skipped invalid log output !\n"));
		return;
	}
	the_listener->edit_stream->printf(_M("IfcImp[Pro]: %s"), buffer);
#endif
}


static Mtl* FindMaterialByName(MtlBaseLib* library, const std::string& material_name) {
    TSTR mat_name = S(material_name);
	const int mat_index = library->FindMtlByName(mat_name);
	Mtl* m = 0;
	if (mat_index != -1) {
		m = static_cast<Mtl*>((*library)[mat_index]);
	}
	return m;
}


static Mtl* FindOrCreateMaterial(MtlBaseLib* library, Interface* max_interface, int& slot, const ifcopenshell::geometry::taxonomy::style::ptr styleptr) {

	auto& style = *styleptr;
    std::string material_name = style.name;

	Mtl* m = FindMaterialByName(library, material_name);
	if (m == 0) {
		StdMat2* stdm = NewDefaultStdMat();
		const TimeValue t = -1;
		if (style.diffuse) {
            const ifcopenshell::geometry::taxonomy::colour diffuse = style.diffuse;
			stdm->SetDiffuse(Color(diffuse.r(), diffuse.g(), diffuse.b()),t);
		}
		if (style.specular) {
            const ifcopenshell::geometry::taxonomy::colour specular = style.specular;
			stdm->SetSpecular(Color(specular.r(), specular.g(), specular.b()),t);
		}
		if (style.has_specularity()) {
			stdm->SetShininess((float)style.specularity, t);
		}
		if (style.has_transparency()) {
			stdm->SetOpacity(1.0f - (float)style.transparency, t);
		}
		m = stdm;
		m->SetName(S(material_name));
		library->Add(m);
		if (slot < NUM_MATERIAL_SLOTS) {
			max_interface->PutMtlToMtlEditor(m,slot++);
		}
	}
	return m;
}


static Mtl* ComposeMultiMaterial(std::map<std::vector<std::string>, Mtl*>& multi_mats, MtlBaseLib* library,
    Interface* max_interface, int& slot, const std::vector<ifcopenshell::geometry::taxonomy::style::ptr> styleptrs,
    const std::string& object_type, const std::vector<int>& material_ids)
{
	std::vector<std::string> material_names;
	bool needs_default = std::find(material_ids.begin(), material_ids.end(), -1) != material_ids.end();

	if (needs_default) {
		material_names.push_back(object_type);
	}

	for (auto it = styleptrs.begin(); it != styleptrs.end(); ++it) {		
		material_names.push_back( (*it)->name);
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
			return FindOrCreateMaterial(library, max_interface, slot, *styleptrs.begin());
		}
	}

	std::map<std::vector<std::string>, Mtl*>::const_iterator i = multi_mats.find(material_names);
	if (i != multi_mats.end()) {
		return i->second;
	}
	MultiMtl* multi_mat = NewDefaultMultiMtl();
	multi_mat->SetNumSubMtls((int)material_names.size());
	int mtl_id = 0;
	if (needs_default) {
		multi_mat->SetSubMtlAndName(mtl_id ++, default_material, default_material->GetName());
	}
	for (auto it = styleptrs.begin(); it != styleptrs.end(); ++it) {
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

int IFCImp::DoImport(const TCHAR *file_name, ImpInterface *impitfc, Interface *ip, BOOL noPrompts ) {

	ifcopenshell::geometry::Settings settings;

	//settings.get<ifcopenshell::geometry::settings::MesherLinearDeflection>().value = 0.001;
	//settings.get<ifcopenshell::geometry::settings::MesherAngularDeflection>().value = 0.5;


	// should adapt to 3ds Max Systemm units ?
	//settings.get<ifcopenshell::geometry::settings::LengthUnit>().value = 1.0;
	//settings.get<ifcopenshell::geometry::settings::PlaneUnit>().value = 1.0;
	//settings.get<ifcopenshell::geometry::settings::Precision>().value = 0.00001;

	//settings.get<ifcopenshell::geometry::settings::PrecisionFactor>().value = 1.0;
	//settings.get<ifcopenshell::geometry::settings::BooleanAttempt2d>().value = true;

	//settings.get<ifcopenshell::geometry::settings::LayersetFirst>().value = false;
	//settings.get<ifcopenshell::geometry::settings::DisableBooleanResult>().value = false;
	//settings.get<ifcopenshell::geometry::settings::NoWireIntersectionCheck>().value = false;
	//settings.get<ifcopenshell::geometry::settings::NoWireIntersectionTolerance>().value = false;


	settings.get<ifcopenshell::geometry::settings::ReorientShells>().value = true; // should be true
	settings.get<ifcopenshell::geometry::settings::UnifyShapes>().value = true;   // should be true
	settings.get<ifcopenshell::geometry::settings::UseWorldCoords>().value = false; // should be false to get a pivot with correct coordinates
	//settings.get<ifcopenshell::geometry::settings::UseMaterialNames>().value = false;
	//settings.get<ifcopenshell::geometry::settings::ConvertBackUnits>().value = false;


	// some settings which seem to make sense
	settings.get<ifcopenshell::geometry::settings::UseElementHierarchy>().value = true;
	settings.get<ifcopenshell::geometry::settings::BuildingLocalPlacement>().value = true;  // should be true

	// ATTENTION: breaks hierarchy positioning when active ( "site-local-placement" )
	settings.get<ifcopenshell::geometry::settings::SiteLocalPlacement>().value = false;      // should be FALSE

	// when vertex welding is enabled, normals  calculation is internally disabled ( see OpenCascadeConversionResult.cpp:239 )
	settings.get<ifcopenshell::geometry::settings::WeldVertices>().value = true;   // should be true

	settings.get<ifcopenshell::geometry::settings::DontEmitNormals>().value = false;
	settings.get<ifcopenshell::geometry::settings::GenerateUvs>().value = false;


	settings.get<ifcopenshell::geometry::settings::CircleSegments>().value = 32;    // should be 32
	settings.get<ifcopenshell::geometry::settings::EdgeArrows>().value = true;
	settings.get<ifcopenshell::geometry::settings::OutputDimensionality>().value = ifcopenshell::geometry::settings::SURFACES_AND_SOLIDS; // default is SURFACES_AND_SOLIDS

#ifdef _UNICODE
	int fn_buffer_size = WideCharToMultiByte(CP_UTF8, 0, file_name, -1, 0, 0, 0, 0);
	char* fn_mb = new char[fn_buffer_size];
	WideCharToMultiByte(CP_UTF8, 0, file_name, -1, fn_mb, fn_buffer_size, 0, 0);
#else
	const char* fn_mb = name;
#endif

    IfcParse::IfcFile file(fn_mb);

	IfcParse::file_open_status status = file.good();

	if (status != IfcParse::file_open_status::SUCCESS) {
        const MCHAR* reason = status == IfcParse::file_open_status::UNSUPPORTED_SCHEMA 
										? _M("Import aborted: unsupported IFC Schema") 
										: _M("Import aborted: failure parsing IFC file");

        ip->DisplayTempPrompt( reason, 10000 );
        return false;
    }

	auto mapped = file.instances_by_type( "IfcMappedItem" );
    auto annotations = file.instances_by_type("IfcAnnotation");
    auto solids = file.instances_by_type("IfcSolidModel");

	// cgal kernels produce std::vector incompatiblities
    //auto kernel = ifcopenshell::geometry::kernels::construct(&file, "hybrid-cgal-simple-opencascade", settings);
    
	//auto kernel = ifcopenshell::geometry::kernels::construct(&file, "opencascade", settings);
    //IfcGeom::Iterator iterator( std::move( kernel), settings, &file);
    
	IfcGeom::Iterator iterator(
        ifcopenshell::geometry::kernels::construct(&file, "opencascade", settings),
        settings,
        &file);


    delete[] fn_mb;

	LogToListener(_M("Importing '%s'...\n"), file_name);
	if (!iterator.initialize()) {
		if(!iterator.had_error_processing_elements()) {
			LogToListener(_M("No elements found in '%s'...\n"), file_name);
			return IMPEXP_SUCCESS;
		}

		LogToListener(_M("Error processing elements in '%s'...\n"), file_name);
		return IMPEXP_FAIL;
	}

	ip->ProgressStart(_T("Importing file..."), TRUE, fn, NULL);

	MtlBaseLib* mats = ip->GetSceneMtls();
	int slot = mats->Count();

	std::vector<ImpNode *> impnode_cache;
	std::map<std::vector<std::string>, Mtl*> material_cache;
	

	bool wasCanceled=false;
	auto startTime = std::chrono::high_resolution_clock::now();
	std::stringstream log_stream;

	do {
		// clear the log
		log_stream.str("");

		//const IfcGeom::Element* element = static_cast<const IfcGeom::Element*>(iterator.get());
		//const IfcGeom::BRepElement* brepElement = static_cast<const IfcGeom::BRepElement*>(iterator.get_native());
		const IfcGeom::Element* element = iterator.get();
		const IfcGeom::TriangulationElement* triElement = static_cast<const IfcGeom::TriangulationElement*>(element);

		if(triElement==nullptr)
		{
			LogToListener(_M("%3d%% - Skipping non/null TriangulationElement [#%d]\n"), iterator.progress(), element != nullptr ? element->id() : -1);
			continue;
		}

		auto prod = triElement->product();
		TSTR e_type = TSTR::FromUTF8(triElement->type().c_str());
		TSTR e_guid = TSTR::FromUTF8(triElement->guid().c_str());
		TSTR e_name = TSTR::FromUTF8(triElement->name().c_str());
		TSTR e_idStr = TSTR(std::to_wstring(triElement->id()).c_str());


		// dump out the parent tree up to IfcProject for each element
        auto parents = triElement->parents(); // keep a persistent copy
        if (!parents.empty()) {
			for(auto it =parents.rbegin(); it != parents.rend(); ++it) {
				auto p_e = *it;
				log_stream << "->" << p_e->type() << " [#" << p_e->id() << "]";
			}
		}
        TSTR logString = TSTR::FromUTF8(log_stream.str().c_str());
        LogToListener(_M("%3d%% - [#%d] %s: '%s' %s\n"), iterator.progress(), triElement->id(), e_type.data(), e_name.data(), logString.data());

		Mtl *mat = ComposeMultiMaterial(material_cache, mats, ip, slot, triElement->geometry().materials(), triElement->type(), triElement->geometry().material_ids());

		ImpNode* impNode = impitfc->CreateNode();

        RefResult refSuccess = REF_INVALID;

		auto mesh = BuildMesh(triElement);

		if ( mesh != nullptr)
            refSuccess = impNode->Reference(mesh);

        if (refSuccess != REF_SUCCEED) {
			LogToListener(_M("Error creating importer reference for imported element #%d.\n"), triElement->id());
            continue;
        }

		TSTR longName;
		BuildFullName( *prod, longName);
        impNode->SetName(longName);

        const auto& mtx = triElement->transformation().data()->ccomponents();
        impNode->SetTransform(0, Matrix3(Point3(mtx(0, 0), mtx(1, 0), mtx(2, 0)), Point3(mtx(0, 1), mtx(1, 1), mtx(2, 1)), Point3(mtx(0, 2), mtx(1, 2), mtx(2, 2)), Point3(mtx(0, 3), mtx(1, 3), mtx(2, 3))));

        INode* inode = impNode->GetINode();

        inode->Hide(triElement->type() == "IfcOpeningElement" || triElement->type() == "IfcSpace");

        if (mat != nullptr) {
            inode->SetMtl(mat);

            // set wirecolor to material color
            inode->SetWireColor(mat->GetDiffuse().toRGB());
        }

		// add to the cache, not to the scene, thisd allows a clean exit if cancel was pressed
		impnode_cache.push_back(impNode);

		ip->ProgressUpdate(iterator.progress(), true, _T(""));

		if (ip->GetCancel()) {
            wasCanceled = noPrompts ? true : VerifyCancel();
            if (wasCanceled) 
				break;
            else 
				ip->SetCancel(false);
        }

	} while (iterator.next());

	ip->ProgressEnd();

	if(wasCanceled) {
		LogToListener(_T("Import canceled by User\n"));
		return IMPEXP_CANCEL;
	}
	// add all objects to the scene
	for( int i = 0; i < impnode_cache.size(); i++ ) 
        impitfc->AddNodeToScene(impnode_cache[i]);

	// Calculate the duration
	INT64 seconds = std::chrono::duration_cast<std::chrono::seconds>(std::chrono::high_resolution_clock::now() - startTime).count();
	LogToListener(_M("Import finished in %u seconds\n"), seconds);
		
	return IMPEXP_SUCCESS;
}

BOOL IFCImp::VerifyCancel() {
#if MAX_VERSION_MAJOR < 23
    return IDYES == MaxMsgBox(GetCOREInterface()->GetMAXHWnd(), GetString(IDS_IMPORT_CANCEL_MESSAGE), GetString(IDS_IMPORT_CANCEL_CAPTION), MB_YESNO);
#else
	// new MaxMessageBox API
    return IDYES == MaxSDK::MaxMessageBox(GetCOREInterface()->GetMAXHWnd(), GetString(IDS_IMPORT_CANCEL_MESSAGE), GetString(IDS_IMPORT_CANCEL_CAPTION), MB_YESNO);
#endif
}


void IFCImp::BuildFullName( const IfcUtil::IfcBaseEntity& entity, MSTR& long_name) 
{  
	TSTR name = TSTR::FromUTF8(entity.get_value<std::string>("Name", "").c_str());          
	TSTR declName = TSTR::FromUTF8(entity.declaration().name().c_str());          

	if( _tcslen( name ) > 0) {
        long_name.printf(_M("%s/%s [#%d]"), declName.data(), name.data(), entity.id_);
	}
	else {
        long_name.printf(_M("%s [#%d]"), declName.data(), entity.id_);
	}
}

TriObject* IFCImp::BuildMesh(const IfcGeom::TriangulationElement* element) {
    TriObject* tri = CreateNewTriObject();

	const IfcGeom::Representation::Triangulation& ios_mesh = element->geometry();

    const auto& verts = ios_mesh.verts();
    const int numVerts = (int)verts.size() / 3;

	//const auto& normals = ios_mesh.normals();
 //   const int numNormals = (int)normals.size() / 3;

 //   const auto& uvs = ios_mesh.uvs();
 //   const int numUVs = (int)uvs.size() / 3;


    tri->mesh.setNumVerts(numVerts);
    for (int i = 0; i < numVerts; i++) {
        tri->mesh.setVert(i, Point3ByIndex(verts, i));
		//if( i < numNormals ) {
  //          tri->mesh.setNormal(i, Point3ByIndex(normals, i));
  //      }
    }

    bool needs_default = std::find(ios_mesh.material_ids().begin(), ios_mesh.material_ids().end(), -1) != ios_mesh.material_ids().end();

    typedef std::pair<int, int> edge_t;

    std::set<edge_t> face_boundaries;
    for (std::vector<int>::const_iterator it = ios_mesh.edges().begin(); it != ios_mesh.edges().end();) {
        const int v1 = *it++;
        const int v2 = *it++;

        const edge_t e((std::min)(v1, v2), (std::max)(v1, v2));
        face_boundaries.insert(e);
    }

    const auto& faces = ios_mesh.faces();

    const int numFaces = (int)faces.size() / 3;

    tri->mesh.setNumFaces(numFaces);

    for (int i = 0; i < numFaces; i++) {
        const int v1 = faces[3 * i + 0];
        const int v2 = faces[3 * i + 1];
        const int v3 = faces[3 * i + 2];

        const edge_t e1((std::min)(v1, v2), (std::max)(v1, v2));
        const edge_t e2((std::min)(v2, v3), (std::max)(v2, v3));
        const edge_t e3((std::min)(v3, v1), (std::max)(v3, v1));

        const bool b1 = face_boundaries.find(e1) != face_boundaries.end();
        const bool b2 = face_boundaries.find(e2) != face_boundaries.end();
        const bool b3 = face_boundaries.find(e3) != face_boundaries.end();

        tri->mesh.faces[i].setVerts(v1, v2, v3);
        tri->mesh.faces[i].setEdgeVisFlags(b1, b2, b3);

        MtlID mtlid = (MtlID)ios_mesh.material_ids()[i];
        if (needs_default) {
            mtlid++;
        }
        tri->mesh.faces[i].setMatID(mtlid);
    }

    bool valid = tri->CheckObjectIntegrity();

    if (!valid) {
        return nullptr;
    }
    
	// apply simple box mapping 
#if MAX_VERSION_MAJOR < 22
	// in 3ds Max 2017-2019 SDK, Matrix3::Identity was declared in matrix3.h, but did'nt actually exist in the lib ....
	Matrix3 ident(TRUE);
    tri->mesh.ApplyUVWMap(MAP_ACAD_BOX, 1, 1, 1, 0, 0, 0, 0, ident);
#else
    tri->mesh.ApplyUVWMap(MAP_ACAD_BOX, 1, 1, 1, 0, 0, 0, 0, Matrix3::Identity);
#endif

    // this one tends to crash, so we skip it for the time being
    // tri->mesh.buildNormals();

    // Either use this or undefine the FACESETS_AS_COMPOUND option in IfcGeom.h to have
    // properly oriented normals. Using only the line below will result in a consistent
    // orientation of normals across shells, but not always oriented towards the
    // outside.
    // tri->mesh.UnifyNormals(false);

	tri->mesh.BuildStripsAndEdges();
    tri->mesh.InvalidateTopologyCache();
    tri->mesh.InvalidateGeomCache();
    return tri;
}

inline Point3 IFCImp::Point3ByIndex(const std::vector<double>& verts, int index) {
	return Point3(verts[3 * index + 0], verts[3 * index + 1], verts[3 * index + 2]);
}
