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

#ifdef WITH_OPENCOLLADA

#include <string>

#include "ColladaSerializer.h"

std::string collada_id(const std::string& s) {
	std::string id;
	id.reserve(s.size());
	for (std::string::const_iterator it = s.begin(); it != s.end(); ++it) {
		const std::string::value_type c = *it;
		if ((c >= '0' && c <= '9') || (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c == '_')) {
			id.push_back(c);
		}
	}
	return id;
}

void ColladaSerializer::ColladaExporter::ColladaGeometries::addFloatSource(const std::string& mesh_id, const std::string& suffix, const std::vector<float>& floats, const char* coords /* = "XYZ" */) {
	COLLADASW::FloatSource source(mSW);
	source.setId(mesh_id + suffix);
	source.setArrayId(mesh_id + suffix + COLLADASW::LibraryGeometries::ARRAY_ID_SUFFIX);
	source.setAccessorStride(strlen(coords));
	source.setAccessorCount(floats.size() / 3);
	for (unsigned int i = 0; i < source.getAccessorStride(); ++i) {
		source.getParameterNameList().push_back(std::string(1, coords[i]));
	}
	source.prepareToAppendValues();
	for (std::vector<float>::const_iterator it = floats.begin(); it != floats.end(); ++it) {
		source.appendValues(*it);
	}
	source.finish();
}
			
void ColladaSerializer::ColladaExporter::ColladaGeometries::write(const std::string mesh_id, const std::string& default_material_name, const std::vector<float>& positions, const std::vector<float>& normals, const std::vector<int>& indices, const std::vector<int> material_ids, const std::vector<IfcGeomObjects::Material>& materials) {
	openMesh(mesh_id);

	// The normals vector can be empty for example when the WELD_VERTICES setting is used.
	// IfcOpenShell does not provide them with multiple face normals collapsed into a single vertex.
	const bool has_normals = !normals.empty();

	addFloatSource(mesh_id, COLLADASW::LibraryGeometries::POSITIONS_SOURCE_ID_SUFFIX, positions);
	if (has_normals) {
		addFloatSource(mesh_id, COLLADASW::LibraryGeometries::NORMALS_SOURCE_ID_SUFFIX, normals);
	}

	COLLADASW::VerticesElement vertices(mSW);
	vertices.setId(mesh_id + COLLADASW::LibraryGeometries::VERTICES_ID_SUFFIX );
	vertices.getInputList().push_back(COLLADASW::Input(COLLADASW::InputSemantic::POSITION, "#" + mesh_id + COLLADASW::LibraryGeometries::POSITIONS_SOURCE_ID_SUFFIX));
	vertices.add();
	
	std::vector<int>::const_iterator index_range_start = indices.begin();
	std::vector<int>::const_iterator material_it = material_ids.begin();
	int previous_material_id = -2;
	for (std::vector<int>::const_iterator it = indices.begin(); ; it += 3) {
		const int current_material_id = material_it == material_ids.end()
			? -3
			: *(material_it++);
		const int num_triangles = std::distance(index_range_start, it) / 3;
		if ((previous_material_id != current_material_id && num_triangles > 0) || (it == indices.end())) {
			COLLADASW::Triangles triangles(mSW);
			triangles.setMaterial(collada_id(previous_material_id < 0
				? default_material_name
				: materials[previous_material_id].name()));
			triangles.setCount(num_triangles);
			int offset = 0;
			triangles.getInputList().push_back(COLLADASW::Input(COLLADASW::InputSemantic::VERTEX,"#" + mesh_id + COLLADASW::LibraryGeometries::VERTICES_ID_SUFFIX, offset++ ) );
			if (has_normals) {
				triangles.getInputList().push_back(COLLADASW::Input(COLLADASW::InputSemantic::NORMAL,"#" + mesh_id + COLLADASW::LibraryGeometries::NORMALS_SOURCE_ID_SUFFIX, offset++ ) );
			}
			triangles.prepareToAppendValues();
			for (std::vector<int>::const_iterator jt = index_range_start; jt != it; ++jt) {
				const int idx = *jt;
				if (has_normals) {
					triangles.appendValues(idx, idx);
				} else {
					triangles.appendValues(idx);
				}
			}
			triangles.finish();
			index_range_start = it;
		}
		previous_material_id = current_material_id;
		if (it == indices.end()) {
			break;
		}
	}

	closeMesh();
	closeGeometry();
}

void ColladaSerializer::ColladaExporter::ColladaGeometries::close() {
	closeLibrary();
}
			
void ColladaSerializer::ColladaExporter::ColladaScene::add(const std::string& node_id, const std::string& node_name, const std::string& geom_name, const std::vector<std::string>& material_ids, const std::vector<float>& matrix) {
	if (!scene_opened) {
		openVisualScene(scene_id);
		scene_opened = true;
	}
			
	COLLADASW::Node node(mSW);
	node.setNodeId(node_id);
	node.setNodeName(node_name);
	node.setType(COLLADASW::Node::NODE);

	// The matrix attribute of an entity is basically a 4x3 representation of its ObjectPlacement.
	// Note that this placement is absolute, ie it is multiplied with all parent placements.
	double matrix_array[4][4] = {
		{matrix[0], matrix[3], matrix[6], matrix[ 9]},
		{matrix[1], matrix[4], matrix[7], matrix[10]},
		{matrix[2], matrix[5], matrix[8], matrix[11]},
		{        0,         0,         0,          1}
	};

	node.start();
	node.addMatrix(matrix_array);
	COLLADASW::InstanceGeometry instanceGeometry(mSW);
	instanceGeometry.setUrl ("#" + geom_name);
	for (std::vector<std::string>::const_iterator it = material_ids.begin(); it != material_ids.end(); ++it) {
		COLLADASW::InstanceMaterial material (*it, "#" + *it);
		instanceGeometry.getBindMaterial().getInstanceMaterialList().push_back(material);
	}
	instanceGeometry.add();
	node.end();
}

void ColladaSerializer::ColladaExporter::ColladaScene::write() {
	if (scene_opened) {
		closeVisualScene();
		closeLibrary();

		COLLADASW::Scene scene (mSW, COLLADASW::URI ("#" + scene_id));
		scene.add();		
	}
}
		
void ColladaSerializer::ColladaExporter::ColladaMaterials::ColladaEffects::write(const IfcGeomObjects::Material& material) {
	openEffect(collada_id(material.name()) + "-fx");
	COLLADASW::EffectProfile effect(mSW);
	effect.setShaderType(COLLADASW::EffectProfile::LAMBERT);
	if (material.hasDiffuse()) {
		const double* diffuse = material.diffuse();
		effect.setDiffuse(COLLADASW::ColorOrTexture(COLLADASW::Color(diffuse[0],diffuse[1],diffuse[2])));
	}
	if (material.hasSpecular()) {
		const double* specular = material.specular();
		effect.setSpecular(COLLADASW::ColorOrTexture(COLLADASW::Color(specular[0],specular[1],specular[2])));
	}
	if (material.hasSpecularity()) {
		effect.setShininess(material.specularity());
	}
	if (material.hasTransparency()) {
		const double transparency = material.transparency();
		if (transparency > 0) {
			// The default opacity mode for Collada is A_ONE, which apparently indicates a
			// transparency value of 1 to be fully opaque. Hence transparency is inverted.
			effect.setTransparency(1.0 - transparency);
		}
	}
	addEffectProfile(effect);
	closeEffect();
}

void ColladaSerializer::ColladaExporter::ColladaMaterials::ColladaEffects::close() {
	closeLibrary();
}
			
void ColladaSerializer::ColladaExporter::ColladaMaterials::add(const IfcGeomObjects::Material& material) {
	if (!contains(material)) {
		effects.write(material);
		materials.push_back(material);
	}
}

bool ColladaSerializer::ColladaExporter::ColladaMaterials::contains(const IfcGeomObjects::Material& material) {
	return std::find(materials.begin(), materials.end(), material) != materials.end();
}

void ColladaSerializer::ColladaExporter::ColladaMaterials::write() {
	effects.close();
	for (auto it = materials.begin(); it != materials.end(); ++it) {
		const std::string& material_name = collada_id((*it).name());
		openMaterial(material_name);
		addInstanceEffect("#" + material_name + "-fx");
		closeMaterial();
	}
	closeLibrary();
}
		
void ColladaSerializer::ColladaExporter::startDocument(const std::string& unit_name, float unit_magnitude) {
	stream.startDocument();

	COLLADASW::Asset asset(&stream);
	asset.getContributor().mAuthoringTool = std::string("IfcOpenShell ") + IFCOPENSHELL_VERSION;
	asset.setUnit(unit_name, unit_magnitude);
	asset.setUpAxisType(COLLADASW::Asset::Z_UP);
	asset.add();
}

void ColladaSerializer::ColladaExporter::writeTesselated(const std::string& guid, const std::string& name, const std::string& type, int obj_id, const std::vector<float>& matrix, const std::vector<float>& vertices, const std::vector<float>& normals, const std::vector<int>& indices, const std::vector<int>& material_ids, const std::vector<IfcGeomObjects::Material>& _materials) {
	const IfcGeomObjects::Material default_for_type = IfcGeomObjects::Material(IfcGeom::get_default_style(type));
	std::vector<std::string> material_references;
	const bool needs_default = std::find(material_ids.begin(), material_ids.end(), -1) != material_ids.end();
	if (needs_default) {
		if (!materials.contains(default_for_type)) {
			materials.add(default_for_type);
		}
		material_references.push_back(collada_id(default_for_type.name()));
	}	
	for (std::vector<IfcGeomObjects::Material>::const_iterator it = _materials.begin(); it != _materials.end(); ++it) {
		const IfcGeomObjects::Material& material = *it;
		if (!materials.contains(material)) {
			materials.add(material);
		}
		material_references.push_back(collada_id(material.name()));
	}
	deferreds.push_back(DeferredObject(guid, name, type, obj_id, matrix, vertices, normals, indices, material_ids, _materials, material_references));
}

const std::string ColladaSerializer::ColladaExporter::DeferredObject::Name() const {
	std::stringstream ss;
	if (!this->name.empty()) {
		ss << this->obj_id << "_" << this->name;
	} else {
		ss << this->guid;
	}
	return collada_id(ss.str());
}

void ColladaSerializer::ColladaExporter::endDocument() {
	// In fact due the XML based nature of Collada and its dependency on library nodes,
	// only at this point all objects are written to the stream.
	materials.write();
	for (auto it = deferreds.begin(); it != deferreds.end(); ++it) {
		const std::string object_name = it->Name();
		geometries.write(object_name, it->type, it->vertices, it->normals, it->indices, it->material_ids, it->materials);
	}
	geometries.close();
	for (auto it = deferreds.begin(); it != deferreds.end(); ++it) {
		const std::string object_name = it->Name();
		scene.add(object_name, object_name, object_name, it->material_references, it->matrix);
	}
	scene.write();
	stream.endDocument();
}
	
bool ColladaSerializer::ready() {
	return true;
}

void ColladaSerializer::writeHeader() {
	exporter.startDocument(unit_name, unit_magnitude);
}

void ColladaSerializer::writeTesselated(const IfcGeomObjects::IfcGeomObject* o) {
	const IfcGeomObjects::IfcRepresentationTriangulation& mesh = o->mesh();
	exporter.writeTesselated(o->guid(), o->name(), o->type(), o->id(), o->matrix(), mesh.verts(), mesh.normals(), mesh.faces(), mesh.material_ids(), mesh.materials());
}

void ColladaSerializer::finalize() {
	exporter.endDocument();
}

#endif
