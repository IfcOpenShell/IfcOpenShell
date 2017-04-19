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

#include "ColladaSerializer.h"

#include <COLLADASWPrimitves.h>
#include <COLLADASWSource.h>
#include <COLLADASWScene.h>
#include <COLLADASWNode.h>
#include <COLLADASWInstanceGeometry.h>
#include <COLLADASWBaseInputElement.h>
#include <COLLADASWAsset.h>

#include <boost/lexical_cast.hpp>

#include <string>
#include <cmath>

using namespace IfcSchema;

static void collada_id(std::string &s)
{
    IfcUtil::sanitate_material_name(s);
    IfcUtil::escape_xml(s);
}

void ColladaSerializer::ColladaExporter::ColladaGeometries::addFloatSource(const std::string& mesh_id,
    const std::string& suffix, const std::vector<real_t>& floats, const char* coords /* = "XYZ" */)
{
	COLLADASW::FloatSource source(mSW);
	source.setId(mesh_id + suffix);
	source.setArrayId(mesh_id + suffix + COLLADASW::LibraryGeometries::ARRAY_ID_SUFFIX);
    const size_t num_elems = strlen(coords);
    source.setAccessorStride(static_cast<unsigned long>(num_elems));
    source.setAccessorCount(static_cast<unsigned long>(floats.size() / num_elems));
    for (size_t i = 0; i < num_elems; ++i) {
		source.getParameterNameList().push_back(std::string(1, coords[i]));
	}
	source.prepareToAppendValues();
    for (std::vector<real_t>::const_iterator it = floats.begin(); it != floats.end(); ++it) {
		source.appendValues(*it);
	}
	source.finish();
}

void ColladaSerializer::ColladaExporter::ColladaGeometries::write(
    const std::string &mesh_id, const std::string& default_material_name, const std::vector<real_t>& positions,
    const std::vector<real_t>& normals, const std::vector<int>& faces, const std::vector<int>& edges,
    const std::vector<int> material_ids, const std::vector<IfcGeom::Material>& materials,
    const std::vector<real_t>& uvs)
{
	openMesh(mesh_id);
	
	// The normals vector can be empty for example when the WELD_VERTICES setting is used.
	// IfcOpenShell does not provide them with multiple face normals collapsed into a single vertex.
	const bool has_normals = !normals.empty();
    const bool has_uvs = !uvs.empty();
	
	addFloatSource(mesh_id, COLLADASW::LibraryGeometries::POSITIONS_SOURCE_ID_SUFFIX, positions);
	if (has_normals) {
		addFloatSource(mesh_id, COLLADASW::LibraryGeometries::NORMALS_SOURCE_ID_SUFFIX, normals);
        if (has_uvs) {
            addFloatSource(mesh_id, COLLADASW::LibraryGeometries::TEXCOORDS_SOURCE_ID_SUFFIX, uvs, "UV");
        }
	}

	COLLADASW::VerticesElement vertices(mSW);
	vertices.setId(mesh_id + COLLADASW::LibraryGeometries::VERTICES_ID_SUFFIX );
	vertices.getInputList().push_back(COLLADASW::Input(COLLADASW::InputSemantic::POSITION, "#" + mesh_id + COLLADASW::LibraryGeometries::POSITIONS_SOURCE_ID_SUFFIX));
	vertices.add();
	
	std::vector<int>::const_iterator index_range_start = faces.begin();
	std::vector<int>::const_iterator material_it = material_ids.begin();
	int previous_material_id = -1;
	for (std::vector<int>::const_iterator it = faces.begin(); !faces.empty(); it += 3) {

		int current_material_id = 0;
		if (material_it != material_ids.end()) {
			// In order for the last range of equal material ids to be output as well, this loop iterates
			// one element past the end of the vector. This needs to be observed when incrementing.
			current_material_id = *(material_it++);
		}

		const size_t num_triangles = std::distance(index_range_start, it) / 3;
		if ((previous_material_id != current_material_id && num_triangles > 0) || (it == faces.end())) {
			COLLADASW::Triangles triangles(mSW);
            std::string material_name = (serializer->settings().get(SerializerSettings::USE_MATERIAL_NAMES)
                ? materials[previous_material_id].original_name() : materials[previous_material_id].name());
            collada_id(material_name);
            triangles.setMaterial(material_name);
            triangles.setCount((unsigned long)num_triangles);
			int offset = 0;
			triangles.getInputList().push_back(COLLADASW::Input(COLLADASW::InputSemantic::VERTEX,"#" + mesh_id + COLLADASW::LibraryGeometries::VERTICES_ID_SUFFIX, offset++));
			if (has_normals) {
				triangles.getInputList().push_back(COLLADASW::Input(COLLADASW::InputSemantic::NORMAL,"#" + mesh_id + COLLADASW::LibraryGeometries::NORMALS_SOURCE_ID_SUFFIX, offset++));
			}
            if (has_uvs) {
                triangles.getInputList().push_back(COLLADASW::Input(COLLADASW::InputSemantic::TEXCOORD,"#" + mesh_id + COLLADASW::LibraryGeometries::TEXCOORDS_SOURCE_ID_SUFFIX, offset++));
            }
			triangles.prepareToAppendValues();
			for (std::vector<int>::const_iterator jt = index_range_start; jt != it; ++jt) {
				const int idx = *jt;
                if (has_normals && has_uvs) {
                    triangles.appendValues(idx, idx, idx);
                } else if(has_normals) {
					triangles.appendValues(idx, idx);
				} else {
					triangles.appendValues(idx);
				}
			}
			triangles.finish();
			index_range_start = it;
		}
		previous_material_id = current_material_id;
		if (it == faces.end()) {
			break;
		}
	}

	std::set<int> faces_set (faces.begin(), faces.end());
	typedef std::vector< std::pair<int, std::vector<unsigned long> > > linelist_t;
	linelist_t linelist;

	int num_lines = 0;
	for ( std::vector<int>::const_iterator it = edges.begin(); it != edges.end(); ++num_lines) {
		const int i1 = *(it++);
		const int i2 = *(it++);

		if (faces_set.find(i1) != faces_set.end() || faces_set.find(i2) != faces_set.end()) {
			continue;
		}

		const int current_material_id = *(material_it++);
		if ((previous_material_id != current_material_id) || (num_lines == 0)) {
			linelist.resize(linelist.size() + 1);
		}

		linelist.rbegin()->second.push_back(i1);
		linelist.rbegin()->second.push_back(i2);
	}

	for (linelist_t::const_iterator it = linelist.begin(); it != linelist.end(); ++it) {
		COLLADASW::Lines lines(mSW);
        std::string material_name = (serializer->settings().get(SerializerSettings::USE_MATERIAL_NAMES)
            ? materials[it->first].original_name() : materials[it->first].name());
        collada_id(material_name);
        lines.setMaterial(material_name);
		lines.setCount((unsigned long)it->second.size());
		int offset = 0;
		lines.getInputList().push_back(COLLADASW::Input(COLLADASW::InputSemantic::VERTEX, "#" + mesh_id + COLLADASW::LibraryGeometries::VERTICES_ID_SUFFIX, offset));
		lines.prepareToAppendValues();
		lines.appendValues(it->second);
		lines.finish();
	}

	closeMesh();
	closeGeometry();
}

void ColladaSerializer::ColladaExporter::ColladaGeometries::close() {
	closeLibrary();
}

void ColladaSerializer::ColladaExporter::ColladaScene::add(
    const std::string& node_id, const std::string& node_name, const std::string& geom_name,
    const std::vector<std::string>& material_ids, const std::vector<real_t>& matrix)
{
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
        { (double)matrix[0], (double)matrix[3], (double)matrix[6], (double)matrix[ 9] },
        { (double)matrix[1], (double)matrix[4], (double)matrix[7], (double)matrix[10] },
        { (double)matrix[2], (double)matrix[5], (double)matrix[8], (double)matrix[11] },
        { 0, 0, 0, 1 }
	};

    matrix_array[0][3] += serializer->settings().offset[0];
    matrix_array[1][3] += serializer->settings().offset[1];
    matrix_array[2][3] += serializer->settings().offset[2];

	node.start();
	node.addMatrix(matrix_array);
	COLLADASW::InstanceGeometry instanceGeometry(mSW);
	instanceGeometry.setUrl ("#" + geom_name);
    foreach(std::string material_name, material_ids) {
        /// @todo This is done 6 times in this file, try to perform this once and be done with the material naming for the export.
        collada_id(material_name);
        COLLADASW::InstanceMaterial material (material_name, "#" + material_name);
		instanceGeometry.getBindMaterial().getInstanceMaterialList().push_back(material);
	}
	instanceGeometry.add();
	node.end();
}

void ColladaSerializer::ColladaExporter::ColladaScene::addParent(const IfcGeom::Element<real_t>& parent){

	if (!scene_opened) {
		openVisualScene(scene_id);
		scene_opened = true;
	}
	const std::vector<real_t> matrix = parent.transformation().matrix().data();
	
	double matrix_array[4][4] = {
		{ (double)matrix[0], (double)matrix[3], (double)matrix[6], (double)matrix[9] },
		{ (double)matrix[1], (double)matrix[4], (double)matrix[7], (double)matrix[10] },
		{ (double)matrix[2], (double)matrix[5], (double)matrix[8], (double)matrix[11] },
		{ 0, 0, 0, 1 }
	};

	matrix_array[0][3] += serializer->settings().offset[0];
	matrix_array[1][3] += serializer->settings().offset[1];
	matrix_array[2][3] += serializer->settings().offset[2];
	
	
	const std::string id = "representation-" + boost::lexical_cast<std::string>(parent.id());

	current_node = new COLLADASW::Node(mSW);
	current_node->setNodeId(id);
	current_node->setNodeName(parent.name());
	current_node->addMatrix(matrix_array);
	current_node->setType(COLLADASW::Node::NODE);
	current_node->start();
}

void ColladaSerializer::ColladaExporter::ColladaScene::closeParent(){
	if (current_node != NULL) { std::cout << "current node is not null\n"; current_node->end(); }
}

void ColladaSerializer::ColladaExporter::ColladaScene::write() {
	if (scene_opened) {
		closeVisualScene();
		closeLibrary();
		
		COLLADASW::Scene scene (mSW, COLLADASW::URI ("#" + scene_id));
		scene.add();		
	}
}

void ColladaSerializer::ColladaExporter::ColladaMaterials::ColladaEffects::write(const IfcGeom::Material& material)
{
    std::string material_name = (serializer->settings().get(SerializerSettings::USE_MATERIAL_NAMES)
        ? material.original_name() : material.name());
    collada_id(material_name);
    openEffect(material_name + "-fx");
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

void ColladaSerializer::ColladaExporter::ColladaMaterials::add(const IfcGeom::Material& material) {
	if (!contains(material)) {
		effects.write(material);
		materials.push_back(material);
	}
}

bool ColladaSerializer::ColladaExporter::ColladaMaterials::contains(const IfcGeom::Material& material) {
	return std::find(materials.begin(), materials.end(), material) != materials.end();
}

void ColladaSerializer::ColladaExporter::ColladaMaterials::write() {
	effects.close();
    foreach(const IfcGeom::Material& material, materials) {
        std::string material_name = (serializer->settings().get(SerializerSettings::USE_MATERIAL_NAMES)
            ? material.original_name() : material.name());
        std::string  material_name_unescaped = material_name; // workaround double-escaping that would occur in addInstanceEffect()
        IfcUtil::sanitate_material_name(material_name_unescaped);
        collada_id(material_name);
		openMaterial(material_name);
        addInstanceEffect("#" + material_name_unescaped + "-fx");
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

void ColladaSerializer::ColladaExporter::write(const IfcGeom::TriangulationElement<real_t>* o)
{	
    const IfcGeom::Representation::Triangulation<real_t>& mesh = o->geometry();
    const std::string name = serializer->settings().get(SerializerSettings::USE_ELEMENT_GUIDS) ?
           o->guid() : (serializer->settings().get(SerializerSettings::USE_ELEMENT_NAMES) ? 
			   o->name() : (serializer->settings().get(SerializerSettings::USE_ELEMENT_TYPES) ? o->type() + "_" + o->name() : o->unique_id()));
    const std::string representation_id = "representation-" + boost::lexical_cast<std::string>(o->geometry().id());
	std::vector<std::string> material_references;
    foreach(const IfcGeom::Material& material, mesh.materials()) {
		if (!materials.contains(material)) {
			materials.add(material);
		}
        std::string material_name = (serializer->settings().get(SerializerSettings::USE_MATERIAL_NAMES)
            ? material.original_name() : material.name());
        collada_id(material_name);
        material_references.push_back(material_name);
	}

	deferreds.push_back(
		DeferredObject(name, representation_id, o->type(), o->transformation().matrix().data(), mesh.verts(), mesh.normals(),
			mesh.faces(), mesh.edges(), mesh.material_ids(), mesh.materials(), material_references, mesh.uvs())
    );
}

void ColladaSerializer::ColladaExporter::write(const IfcGeom::TriangulationElement<real_t>* o, const IfcGeom::Element<real_t>* parent)
{
	const IfcGeom::Representation::Triangulation<real_t>& mesh = o->geometry();
	const std::string name = serializer->settings().get(SerializerSettings::USE_ELEMENT_GUIDS) ?
		o->guid() : (serializer->settings().get(SerializerSettings::USE_ELEMENT_NAMES) ?
			o->name() : (serializer->settings().get(SerializerSettings::USE_ELEMENT_TYPES) ? o->type() + "_" + o->name() : o->unique_id()));
	const std::string representation_id = "representation-" + boost::lexical_cast<std::string>(o->geometry().id());
	std::vector<std::string> material_references;
	foreach(const IfcGeom::Material& material, mesh.materials()) {
		if (!materials.contains(material)) {
			materials.add(material);
		}
		std::string material_name = (serializer->settings().get(SerializerSettings::USE_MATERIAL_NAMES)
			? material.original_name() : material.name());
		collada_id(material_name);
		material_references.push_back(material_name);
	}

	DeferredObject defered = (serializer->settings().get(SerializerSettings::USE_ELEMENT_HIERARCHY) ?
		DeferredObject(name, representation_id, o->type(), o->transformation().matrix().data(), mesh.verts(), mesh.normals(),
			mesh.faces(), mesh.edges(), mesh.material_ids(), mesh.materials(), material_references, mesh.uvs(), *parent) : 
		DeferredObject(name, representation_id, o->type(), o->transformation().matrix().data(), mesh.verts(), mesh.normals(),
				mesh.faces(), mesh.edges(), mesh.material_ids(), mesh.materials(), material_references, mesh.uvs()));
	deferreds.push_back(defered);
	
}

void ColladaSerializer::ColladaExporter::endDocument() {
	// In fact due the XML based nature of Collada and its dependency on library nodes,
	// only at this point all objects are written to the stream.
	std::cout << "starting end document\n";
	materials.write();
	std::set<std::string> geometries_written;
	std::cout << "sorting defered list...\n";
	std::sort(deferreds.begin(), deferreds.end());
	std::cout << "done\n";
	for (std::vector<DeferredObject>::const_iterator it = deferreds.begin(); it != deferreds.end(); ++it) {
		if (geometries_written.find(it->representation_id) != geometries_written.end()) {
			continue;
		}
		geometries_written.insert(it->representation_id);
		geometries.write(it->representation_id, it->type, it->vertices, it->normals, it->faces, it->edges, it->material_ids, it->materials, it->uvs);
	}
	geometries.close();
	int parent_id = -1;
	bool is_parent_empty = true; 
	for (std::vector<DeferredObject>::const_iterator it = deferreds.begin(); it != deferreds.end(); ++it) 
	{
		const std::string object_name = it->unique_id;
		//std::cout << "working on " << it->unique_id;
		//std::cout << (it->parent == NULL ? " parent is null\n" : "parent is not null\n");
		if (it->parent != NULL && parent_id != it->parent->id())
		{
			std::cout << "parent description : \n --- Type : " << it->parent->type() << " \n --- Name : " << it->parent->name() << "\n";
			//std::cout << "parent is not null. Id : " << it->parent->id() << '\n';
			//std::cout << "test if parent is empty ... \n";
			if (!is_parent_empty)
			{
				//std::cout << "close parent1 ... \n";
				scene.closeParent();
				//std::cout << "done\n";
			}
			//std::cout << "get parent id .. \n";
			parent_id = it->parent->id();
			//std::cout << "add parent to scene .. \n";
			scene.addParent(*it->parent);
			//std::cout << "done \n";
			is_parent_empty = false;
		}
		//std::cout << "add node to scene ... \n";
        /// @todo redundant information using ID as both ID and Name, maybe omit Name or allow specifying what would be used as the name
		scene.add(object_name, object_name, it->representation_id, it->material_references, it->matrix);
		//std::cout << "done \n";
	}
	std::cout << "close parent2 : \n";
	if (!is_parent_empty) scene.closeParent();
	std::cout << "write : \n";
	scene.write();
	stream.endDocument();
}

bool ColladaSerializer::ready() {
	return true;
}

void ColladaSerializer::writeHeader() {
	exporter.startDocument(unit_name, unit_magnitude);
}

void ColladaSerializer::write(const IfcGeom::TriangulationElement<real_t>* o) {
    exporter.write(o);
}

void ColladaSerializer::write(const IfcGeom::TriangulationElement<real_t>* o, const IfcGeom::Element<real_t>* parent)
{
	exporter.write(o, parent);
}


void ColladaSerializer::finalize() {
	exporter.endDocument();
}

#endif
