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

#ifdef WITH_USD

 // windows stuff: defines max as a macro when including windows.h
 // error C2589: '(': illegal token on right side of '::'
#define NOMINMAX

#include "USDSerializer.h"

#include "pxr/base/gf/vec3f.h"
#include "pxr/usd/usdGeom/xform.h"
#include "pxr/usd/usdGeom/scope.h"
#include "pxr/usd/usdGeom/tokens.h"
#include "pxr/usd/usdGeom/metrics.h"
#include "pxr/usd/usdLux/distantLight.h"
#include "pxr/usd/usdShade/shader.h"
#include "pxr/usd/usdShade/materialBindingAPI.h"

#include <math.h>

USDSerializer::USDSerializer(const std::string& out_filename, const ifcopenshell::geometry::Settings& geometry_settings, const ifcopenshell::geometry::SerializerSettings& settings):
	WriteOnlyGeometrySerializer(geometry_settings, settings),
	filename_(out_filename)
{
	std::size_t found = filename_.find_last_of("/\\");
	parent_path_ = filename_.substr(0, found != std::string::npos ? found + 1 : 0);
	stage_ = pxr::UsdStage::CreateNew(filename_);

	if(!stage_)
		throw std::runtime_error("Could not create USD stage");

    if (!settings.get<ifcopenshell::geometry::settings::UseYUp>().get()) {
        pxr::UsdGeomSetStageUpAxis(stage_, pxr::UsdGeomTokens->z);
    }

	pxr::UsdGeomSetStageMetersPerUnit(stage_, 1.0f);

  	pxr::UsdGeomScope::Define(stage_, pxr::SdfPath("/Looks"));
  	auto light = pxr::UsdLuxDistantLight::Define(stage_, pxr::SdfPath("/defaultLight"));
  	light.CreateIntensityAttr().Set(1000.0f);
  	light.CreateColorAttr().Set(pxr::GfVec3f(1.0f, 1.0f, 1.0f));
  	ready_ = true;
}

USDSerializer::~USDSerializer() {

}

std::vector<pxr::UsdShadeMaterial> USDSerializer::createMaterials(const std::vector<ifcopenshell::geometry::taxonomy::style::ptr>& styles)
{
  	if(styles.empty())
  	  	throw std::runtime_error("No styles to create materials from");

  	std::vector<pxr::UsdShadeMaterial> materials {};

  	for(auto styleptr : styles) {
        auto& style = *styleptr;
        std::string material_path(style.name);
		usd_utils::toPath(material_path);

		if(materials_.find(material_path) != materials_.end()) {
			materials.push_back(materials_[material_path]);
			continue;
		}

  	  	const std::string path("/Looks/" + material_path);
  	  	auto material = pxr::UsdShadeMaterial::Define(stage_, pxr::SdfPath(path));
  	  	auto shader = pxr::UsdShadeShader::Define(stage_, pxr::SdfPath(path + "/Shader"));
  	  	shader.CreateIdAttr().Set(pxr::TfToken("UsdPreviewSurface"));

  	  	float rgba[4] { 0.18f, 0.18f, 0.18f, 1.0f };
  	  	if (style.diffuse)
			for (int i = 0; i < 3; ++i)
  	  	    	rgba[i] = static_cast<float>(style.diffuse.ccomponents()(i));
  	  	shader.CreateInput(pxr::TfToken("diffuseColor"), pxr::SdfValueTypeNames->Color3f).Set(pxr::GfVec3f(rgba[0], rgba[1], rgba[2]));

        if (style.has_transparency())
            rgba[3] -= style.transparency;
  	  	shader.CreateInput(pxr::TfToken("opacity"), pxr::SdfValueTypeNames->Float).Set(rgba[3]);

  	  	if(style.specular) {
  	  		for (int i = 0; i < 3; ++i)
  	  	    	rgba[i] = static_cast<float>(style.specular.ccomponents()(i));
  	  	  	shader.CreateInput(pxr::TfToken("useSpecularWorkflow"), pxr::SdfValueTypeNames->Int).Set(1);
  	  	} else {
  	  	  	shader.CreateInput(pxr::TfToken("useSpecularWorkflow"), pxr::SdfValueTypeNames->Int).Set(0);
  	  	}
  	  	shader.CreateInput(pxr::TfToken("specularColor"), pxr::SdfValueTypeNames->Color3f).Set(pxr::GfVec3f(rgba[0], rgba[1], rgba[2]));

  	  	material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), pxr::TfToken("surface"));
  	  	materials.push_back(material);
		materials_[material_path] = material;
  	}

  	return materials;
}

void USDSerializer::writeHeader() {
  	stage_->GetRootLayer()->SetComment("File generated by IfcOpenShell " + std::string(IFCOPENSHELL_VERSION)); 
}

std::string USDSerializer::object_id_unique(const IfcGeom::Element* o) {
    auto it = element_names_.find(o->id());
    if (it != element_names_.end()) {
        return it->second;
    }
    int postfix = 0;
    auto name = object_id(o);
    auto suffix = "-" + boost::to_lower_copy(o->context());
    if (name.size() > suffix.size() && std::equal(suffix.rbegin(), suffix.rend(), name.rbegin())) {
        name = name.substr(0, name.size() - suffix.size());
    }
    while (true) {
        auto unique_name = name;
        if (postfix) {
            unique_name += "_" + std::to_string(postfix);
        }
        unique_name = usd_utils::toPath(unique_name);
        if (emitted_names_.find(unique_name) == emitted_names_.end()) {
            emitted_names_.insert(unique_name);
            return element_names_[o->id()] = unique_name;
        }
        postfix += 1;
    }
}

template <typename T>
T USDSerializer::writeNode(const IfcGeom::Element* o, const IfcGeom::Element* p) {
    written_.insert(o->id());

    auto m = o->transformation().data()->ccomponents();
    
    // store absolute matrix for calculating relative child matrices later on.
    placements_[o->id()] = o->transformation().data();
    
    bool is_root = false;
    std::string prefix = "/";
    if (geometry_settings_.get<ifcopenshell::geometry::settings::UseElementHierarchy>().get() && p == nullptr && o->parents().empty()) {
        // Emitting hierarchy
        // p == nullptr means we're in the first pass serializing geometric elements
        // in that case empty parents vector means it's the root
        is_root = true;
    } else if (p != nullptr) {
        // Providing explicit parent pointer, lookup previously serialized m4 and path
        prefix = paths_[p->id()] + "/";
        m = placements_[p->id()]->ccomponents().inverse() * m;
    } else {
        std::vector<std::string> names;
        std::transform(o->parents().begin(), o->parents().end(), std::back_inserter(names), [this](auto& i) { return object_id_unique(i); });
        std::ostringstream oss;
        std::copy(names.begin(), names.end(), std::ostream_iterator<std::string>(oss, "/"));
        prefix += oss.str();
            
        // std::ostringstream pss;
        // pss << "MATT" << std::endl << std::endl;
        // pss << m << std::endl << std::endl << o->parents().back()->transformation().data()->ccomponents() << std::endl << std::endl;
        if (!o->parents().empty())
        m = o->parents().back()->transformation().data()->ccomponents().inverse() * m;
        // pss << m << std::endl << std::endl;
        // auto psss = pss.str();
        // std::wcout << psss.c_str() << std::endl;
    }
    auto el_path = prefix + object_id_unique(o);
    paths_[o->id()] = el_path;
    
    T t = T::Define(stage_, pxr::SdfPath(el_path));
    if (is_root) {
        stage_->SetDefaultPrim(t.GetPrim());
    }
    
    t.AddTransformOp().Set(pxr::GfMatrix4d(
        m.data()[0], m.data()[1], m.data()[2], m.data()[3],
        m.data()[4], m.data()[5], m.data()[6], m.data()[7],
        m.data()[8], m.data()[9], m.data()[10], m.data()[11],
        m.data()[12], m.data()[13], m.data()[14], m.data()[15]
    ));
    return t;
}

void USDSerializer::write(const IfcGeom::TriangulationElement* o) {
    IfcGeom::Element const * previous = nullptr;
    for (auto it = o->parents().begin(); it != o->parents().end(); ++it) {
        parents_.push_back({ *it, previous });
        previous = *it;
    }
    pxr::UsdGeomXform usd_mesh_container = writeNode<pxr::UsdGeomXform>(o); //  writeNode<pxr::UsdGeomMesh>(o);
    auto usd_mesh = pxr::UsdGeomMesh::Define(stage_, pxr::SdfPath(usd_mesh_container.GetPath().GetString() + "/" + o->context()));
    const IfcGeom::Representation::Triangulation& mesh = o->geometry();
    const auto verts = mesh.verts();
    const auto faces = mesh.faces();
    const auto material_ids = mesh.material_ids();
    

  	pxr::VtVec3fArray points;
  	for(std::size_t i = 0; i < verts.size(); i+=3) {
		points.push_back(pxr::GfVec3f(static_cast<float>(verts[i]),
									  static_cast<float>(verts[i+1]),
									  static_cast<float>(verts[i+2])));
  	}
  	usd_mesh.CreatePointsAttr().Set(points);
  	usd_mesh.CreateFaceVertexIndicesAttr().Set(usd_utils::toVtArray(faces));
  	usd_mesh.CreateFaceVertexCountsAttr().Set(pxr::VtArray<int>((int) faces.size() / 3, 3));

  	pxr::VtVec3fArray normals;
  	for (std::vector<double>::const_iterator it = mesh.normals().begin(); it != mesh.normals().end();)
  	  	normals.push_back(pxr::GfVec3f(static_cast<float>(*(it++)), static_cast<float>(*(it++)), static_cast<float>(*(it++))));
  	usd_mesh.CreateNormalsAttr().Set(normals);

  	auto materials = createMaterials(mesh.materials());
  	pxr::UsdShadeMaterialBindingAPI material_api(usd_mesh);
  	if(materials.size() > 1) {
  	  	std::vector<pxr::VtArray<int>> subsets(materials.size());
  	  	for(int i = 0; i < material_ids.size(); ++i)
  	  	  	subsets[material_ids[i]].push_back(i);

  	  	for(std::size_t i = 0; i < subsets.size(); ++i){
  	  	  	auto subset = material_api.CreateMaterialBindSubset(pxr::TfToken("subset_" + std::to_string(i)), subsets[i]);
  	  	  	pxr::UsdShadeMaterialBindingAPI(subset).Bind(materials[i]);
  	  	}
  	} else {
  	  	material_api.Bind(materials[0]);
  	}
}

void USDSerializer::finalize() {
    // we write the parents at the end, because some parents might actually be
    // geometrical entities such as the IfcSite.
    std::set<int> written;
    for (auto& [p, q] : parents_) {
        if (written.find(p->id()) == written.end() && written_.find(p->id()) == written_.end()) {
            written.insert(p->id());
            writeNode<pxr::UsdGeomXform>(p, q);
        }
    }

  	stage_->Save();
}

template pxr::UsdGeomMesh USDSerializer::writeNode<pxr::UsdGeomMesh>(const IfcGeom::Element*, const IfcGeom::Element*);
template pxr::UsdGeomXform USDSerializer::writeNode<pxr::UsdGeomXform>(const IfcGeom::Element*, const IfcGeom::Element*);

#endif // WITH_USD