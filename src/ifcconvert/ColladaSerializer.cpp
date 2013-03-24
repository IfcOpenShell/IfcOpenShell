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

#include "ColladaSerializer.h"

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
			
void ColladaSerializer::ColladaExporter::ColladaGeometries::write(const std::string mesh_id, const std::vector<float>& positions, const std::vector<float>& normals, const std::vector<int>& indices) {
	openMesh(mesh_id);

	addFloatSource(mesh_id, COLLADASW::LibraryGeometries::POSITIONS_SOURCE_ID_SUFFIX, positions);
	if (!normals.empty()) {
		// The normals vector can be empty for example when the WELD_VERTICES setting is used.
		// IfcOpenShell does not provide them with multiple face normals collapsed into a single vertex.
		addFloatSource(mesh_id, COLLADASW::LibraryGeometries::NORMALS_SOURCE_ID_SUFFIX, normals);
	}

	COLLADASW::VerticesElement vertices(mSW);
	vertices.setId(mesh_id + COLLADASW::LibraryGeometries::VERTICES_ID_SUFFIX );
	vertices.getInputList().push_back(COLLADASW::Input(COLLADASW::InputSemantic::POSITION, "#" + mesh_id + COLLADASW::LibraryGeometries::POSITIONS_SOURCE_ID_SUFFIX));
	vertices.add();
	
	COLLADASW::Triangles triangles(mSW);
	triangles.setCount(indices.size() / 3);
	int offset = 0;
	triangles.getInputList().push_back(COLLADASW::Input(COLLADASW::InputSemantic::VERTEX,"#" + mesh_id + COLLADASW::LibraryGeometries::VERTICES_ID_SUFFIX, offset++ ) );
	if (!normals.empty()) {
		triangles.getInputList().push_back(COLLADASW::Input(COLLADASW::InputSemantic::NORMAL,"#" + mesh_id + COLLADASW::LibraryGeometries::NORMALS_SOURCE_ID_SUFFIX, offset++ ) );
	}
	triangles.prepareToAppendValues();
	for (auto it = indices.begin(); it != indices.end(); ++it) {
		const auto& idx = *it;
		if (!normals.empty()) {
			triangles.appendValues(idx, idx);
		} else {
			triangles.appendValues(idx);
		}
	}
	triangles.finish();

	closeMesh();
	closeGeometry();
}

void ColladaSerializer::ColladaExporter::ColladaGeometries::close() {
	closeLibrary();
}
			
void ColladaSerializer::ColladaExporter::ColladaScene::add(const std::string& node_id, const std::string& node_name, const std::string& geom_id, const std::string& material_id, const std::vector<float>& matrix) {
	if (!scene_opened) {
		openVisualScene(scene_id);
		scene_opened = true;
	}
			
	COLLADASW::Node node(mSW);
	node.setNodeId(node_id);
	node.setNodeName(node_name);
	node.setType(COLLADASW::Node::DEFAULT);

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
	instanceGeometry.setUrl ("#" + geom_id);
	COLLADASW::InstanceMaterial material ("ColorMaterial", "#" + material_id);
	instanceGeometry.getBindMaterial().getInstanceMaterialList().push_back(material);
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
		
void ColladaSerializer::ColladaExporter::ColladaMaterials::ColladaEffects::write(const SurfaceStyle& style) {
	openEffect(style.Name() + "-fx");
	COLLADASW::EffectProfile effect(mSW);
	effect.setShaderType(COLLADASW::EffectProfile::LAMBERT);
	effect.setDiffuse(COLLADASW::ColorOrTexture(COLLADASW::Color(style.Diffuse().R(),style.Diffuse().G(),style.Diffuse().B())));
	addEffectProfile(effect);
}

void ColladaSerializer::ColladaExporter::ColladaMaterials::ColladaEffects::close() {
	closeLibrary();
}
			
void ColladaSerializer::ColladaExporter::ColladaMaterials::add(const SurfaceStyle& style) {
	if (!contains(style.Name())) {
		effects.write(style);
		surface_styles.push_back(style);
	}
}

bool ColladaSerializer::ColladaExporter::ColladaMaterials::contains(const std::string& name) {
	for (auto it = surface_styles.begin(); it != surface_styles.end(); ++it) {
		if (it->Name() == name) return true;
	}
	return false;
}

void ColladaSerializer::ColladaExporter::ColladaMaterials::write() {
	effects.close();
	for (auto it = surface_styles.begin(); it != surface_styles.end(); ++it) {
		const std::string& material_name = it->Name();
		openMaterial(material_name);
		addInstanceEffect("#" + material_name + "-fx");
		closeLibrary();
	}
}
		
void ColladaSerializer::ColladaExporter::startDocument() {
	stream.startDocument();

	COLLADASW::Asset asset(&stream);
	asset.getContributor().mAuthoringTool = std::string("IfcOpenShell ") + IFCOPENSHELL_VERSION;
	// TODO: Get the appropriate unit from the IFC file.
	asset.setUnit("meter", 1.0);
	asset.setUpAxisType(COLLADASW::Asset::Z_UP);
	asset.add();
}

void ColladaSerializer::ColladaExporter::writeTesselated(const std::string& type, int obj_id, const std::vector<float>& matrix, const std::vector<float>& vertices, const std::vector<float>& normals, const std::vector<int>& indices) {
	if (!materials.contains(type)) materials.add(GetDefaultMaterial(type));
	deferreds.push_back(DeferedObject(type, obj_id, matrix, vertices, normals, indices));
}

void ColladaSerializer::ColladaExporter::endDocument() {
	// In fact due the XML based nature of Collada and its dependency on library nodes,
	// only at this point all objects are written to the stream.
	materials.write();
	for (auto it = deferreds.begin(); it != deferreds.end(); ++it) {
		std::stringstream ss; ss << "object" << it->obj_id;
		const std::string object_id = ss.str();
		geometries.write(object_id, it->vertices, it->normals, it->indices);
	}
	geometries.close();
	for (auto it = deferreds.begin(); it != deferreds.end(); ++it) {
		std::stringstream ss; ss << "object" << it->obj_id;
		const std::string object_id = ss.str();
		scene.add(object_id, object_id, object_id, it->type, it->matrix);
	}
	scene.write();
	stream.endDocument();
}
	
bool ColladaSerializer::ready() {
	return true;
}

void ColladaSerializer::writeHeader() {
	exporter.startDocument();
}

void ColladaSerializer::writeTesselated(const IfcGeomObjects::IfcGeomObject* o) {
	exporter.writeTesselated(o->type, o->id, o->matrix, o->mesh->verts, o->mesh->normals, o->mesh->faces);
}

void ColladaSerializer::finalize() {
	exporter.endDocument();
}

