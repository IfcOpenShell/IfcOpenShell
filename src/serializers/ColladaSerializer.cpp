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

#include <boost/foreach.hpp>

#include <COLLADASWPrimitves.h>
#include <COLLADASWSource.h>
#include <COLLADASWScene.h>
#include <COLLADASWNode.h>
#include <COLLADASWInstanceGeometry.h>
#include <COLLADASWBaseInputElement.h>
#include <COLLADASWAsset.h>

#include <string>
#include <cmath>

#include "../ifcparse/utils.h"

static std::string& collada_id(std::string& s)
{
    IfcUtil::sanitate_material_name(s);
    IfcUtil::escape_xml(s);
	return s;
}

void ColladaSerializer::ColladaExporter::ColladaGeometries::addFloatSource(const std::string& mesh_id,
    const std::string& suffix, const std::vector<double>& floats, const char* coords /* = "XYZ" */)
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
    for (std::vector<double>::const_iterator it = floats.begin(); it != floats.end(); ++it) {
		source.appendValues(*it);
	}
	source.finish();
}

void ColladaSerializer::ColladaExporter::ColladaGeometries::write(
    const std::string &mesh_id, const std::string &/**<@todo 'default_material_name' unused, remove? */,
    const std::vector<double>& positions, const std::vector<double>& normals,
    const std::vector<int>& faces, const std::vector<int>& edges,
    const std::vector<int>& material_ids, const std::vector<ifcopenshell::geometry::taxonomy::style::ptr>& /**<@todo 'materials' unused, remove? */,
    const std::vector<double>& uvs, const std::vector<std::string>& material_references)
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

            std::string material_name = material_references[previous_material_id];
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
        lines.setMaterial(material_references[it->first]);
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
    const std::vector<std::string>& material_ids, const IfcGeom::Transformation& transformation)
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

	auto transformation_towrite = transformation.data()->ccomponents();
	
	// If this is not the first parent, get the relative placement
	if (parentNodes.size() > 0)
	{
		// @todo check order
		transformation_towrite = matrixStack.top().ccomponents() * transformation_towrite;
	}

	const auto& posmatrix = transformation_towrite;

	// @todo check
	double matrix_array[4][4] = {
		{ (double)posmatrix(0,0), (double)posmatrix(0,1), (double)posmatrix(0,2), (double)posmatrix(0,3) },
		{ (double)posmatrix(1,0), (double)posmatrix(1,1), (double)posmatrix(1,2), (double)posmatrix(1,3) },
		{ (double)posmatrix(2,0), (double)posmatrix(2,1), (double)posmatrix(2,2), (double)posmatrix(2,3) },
		{ (double)posmatrix(3,0), (double)posmatrix(3,1), (double)posmatrix(3,2), (double)posmatrix(3,3) }
	};

	node.start();
	node.addMatrix(matrix_array);
	COLLADASW::InstanceGeometry instanceGeometry(mSW);
	instanceGeometry.setUrl("#" + geom_name);
    BOOST_FOREACH(const std::string &material_name, material_ids) {
		// Unescape to avoid double escaping because OpenCollada's material URI parameter escapes XML internally
    	std::string unescaped = material_name;
    	IfcUtil::unescape_xml(unescaped);

        COLLADASW::InstanceMaterial material(material_name, "#" + unescaped);
		instanceGeometry.getBindMaterial().getInstanceMaterialList().push_back(material);
	}
	instanceGeometry.add();
	node.end();
}

void ColladaSerializer::ColladaExporter::ColladaScene::addParent(const IfcGeom::Element& parent){
	//we open the visual scene tag if it's not.
	if (!scene_opened) {
		openVisualScene(scene_id);
		scene_opened = true;
	}

	const IfcGeom::Transformation& parent_trsf = parent.transformation();

	auto transformation_towrite = parent_trsf.data()->ccomponents();

	// If this is not the first parent, get the relative placement
	if (parentNodes.size() > 0) {
		// @todo check order
		transformation_towrite = matrixStack.top().ccomponents() * transformation_towrite;
	}

	const auto& posmatrix = transformation_towrite;

	double matrix_array[4][4] = {
		{ (double)posmatrix(0,0), (double)posmatrix(1,0), (double)posmatrix(2,0), (double)posmatrix(3,0) },
		{ (double)posmatrix(0,1), (double)posmatrix(1,1), (double)posmatrix(2,1), (double)posmatrix(3,1) },
		{ (double)posmatrix(0,2), (double)posmatrix(1,2), (double)posmatrix(2,2), (double)posmatrix(3,2) },
		{ (double)posmatrix(0,3), (double)posmatrix(1,3), (double)posmatrix(2,3), (double)posmatrix(3,3) }
	};

    std::string name = serializer->object_id(&parent);
	collada_id(name);

	COLLADASW::Node *current_node;
	current_node = new COLLADASW::Node(mSW);
	current_node->setNodeId(name);
    /// @todo redundant information using ID as both ID and Name, maybe omit Name or allow specifying what would be used as the name
	current_node->setNodeName(name);
	current_node->setType(COLLADASW::Node::NODE);
	current_node->start();
	current_node->addMatrix(matrix_array);

	// Add the node to the parent stack
	matrixStack.push(ifcopenshell::geometry::taxonomy::matrix4(parent_trsf.data()->ccomponents().inverse()));
	parentNodes.push(current_node);
	serializer->parentStackId.push(parent.id());
}

void ColladaSerializer::ColladaExporter::ColladaScene::closeParent()
{
	// Get the top element
	COLLADASW::Node *current_node = parentNodes.top();

	// Close the node
	current_node->end();

	// Remove it from the stack
	parentNodes.pop();
	matrixStack.pop();
	serializer->parentStackId.pop();

	// Free the memory
	delete current_node;
	current_node = NULL;
}

void ColladaSerializer::ColladaExporter::ColladaScene::write() {
	if (scene_opened) {
		closeVisualScene();
		closeLibrary();
		
		COLLADASW::Scene scene (mSW, COLLADASW::URI ("#" + scene_id));
		scene.add();		
	}
}

void ColladaSerializer::ColladaExporter::ColladaMaterials::ColladaEffects::write(
    const ifcopenshell::geometry::taxonomy::style::ptr &material, const std::string &material_uri)
{
    openEffect(material_uri + "-fx");
	COLLADASW::EffectProfile effect(mSW);
	effect.setShaderType(COLLADASW::EffectProfile::LAMBERT);
	if (material->diffuse) {
		const auto& diffuse = material->diffuse.ccomponents();
		effect.setDiffuse(COLLADASW::ColorOrTexture(COLLADASW::Color(diffuse(0),diffuse(1),diffuse(2))));
	}
	if (material->specular) {
		const auto& specular = material->specular.ccomponents();
		effect.setSpecular(COLLADASW::ColorOrTexture(COLLADASW::Color(specular(0),specular(1),specular(2))));
	}
	if (material->specularity == material->specularity) {
		effect.setShininess(material->specularity);
	}
	if (material->transparency == material->transparency) {
		const double transparency = material->transparency;
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

void ColladaSerializer::ColladaExporter::ColladaMaterials::add(const ifcopenshell::geometry::taxonomy::style::ptr& material) {
	if (!contains(material)) {
		std::string material_name = material->name;

		if (material_name.empty()) {
			material_name = "missing-material-" + material->name;
		}

		collada_id(material_name);

		effects.write(material, material_name);
		materials.push_back(material);
		material_uris.push_back(material_name);
	}
}

std::string ColladaSerializer::ColladaExporter::ColladaMaterials::getMaterialUri(const ifcopenshell::geometry::taxonomy::style::ptr& material) {
	std::vector<ifcopenshell::geometry::taxonomy::style::ptr>::iterator it = std::find(materials.begin(), materials.end(), material);
	ptrdiff_t index = std::distance(materials.begin(), it);
	return material_uris.at(index);
}

bool ColladaSerializer::ColladaExporter::ColladaMaterials::contains(const ifcopenshell::geometry::taxonomy::style::ptr& material) {
	return std::find(materials.begin(), materials.end(), material) != materials.end();
}

void ColladaSerializer::ColladaExporter::ColladaMaterials::write() {
	effects.close();
    BOOST_FOREACH(const ifcopenshell::geometry::taxonomy::style::ptr& material, materials) {
        std::string material_name = getMaterialUri(material);
		openMaterial(material_name);

		// Unescape to avoid double escaping because OpenCollada's addInstanceEffect escapes XML internally
		IfcUtil::unescape_xml(material_name);

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

void ColladaSerializer::ColladaExporter::write(const IfcGeom::TriangulationElement* o)
{
	const IfcGeom::Representation::Triangulation& mesh = o->geometry();
	
    std::string name = serializer->object_id(o);
	collada_id(name);
	
	std::string representation_id = "representation-" + o->geometry().id();
	collada_id(representation_id);

	std::vector<std::string> material_references;
	BOOST_FOREACH(const ifcopenshell::geometry::taxonomy::style::ptr& material, mesh.materials()) {
		materials.add(material);

		std::string material_name = materials.getMaterialUri(material);
		material_references.push_back(material_name);
	}

	DeferredObject deferred(name, representation_id, o->type(), o->transformation(), mesh.verts(), mesh.normals(),
		mesh.faces(), mesh.edges(), mesh.material_ids(), mesh.materials(), material_references, mesh.uvs());

	if (serializer->geometry_settings().get<ifcopenshell::geometry::settings::UseElementHierarchy>().get()) {
		deferred.parents() = o->parents();
	}

	deferreds.push_back(deferred);
}

std::string ColladaSerializer::differentiateSlabTypes(const IfcUtil::IfcBaseEntity* slab)
{
	auto value = slab->get("PredefinedType");

    if (value.isNull()) {
        return "_Unknown";
    }

	const std::string str_value = value;
	std::string result;

	if (str_value == "FLOOR") {
		result = "_Floor";
	} else if (str_value == "ROOF") {
		result = "_Roof";
	} else if (str_value == "LANDING") {
		result = "_Landing";
	} else if (str_value == "BASESLAB") {
		result = "_BaseSlab";
	} else if (str_value == "NOTDEFINED") {
		result = "_NotDefined";
	} else {
		auto otype = slab->get("ObjectType");
		if (otype.isNull()) {
			result = "_Unknown";
		} else {
			result = (std::string) otype;
		}
	}

	return result;
}

std::string ColladaSerializer::object_id(const IfcGeom::Element* o) /*override*/
{
    if (settings_.get<ifcopenshell::geometry::settings::UseElementTypes>().get()) {
        const std::string slabSuffix = (o->product() && o->product()->declaration().name() == "IfcSlab")
            ? differentiateSlabTypes(o->product())
            : "";
        return o->type() + slabSuffix;
    }
    return GeometrySerializer::object_id(o);
}

void ColladaSerializer::ColladaExporter::endDocument() {
	// In fact due the XML based nature of Collada and its dependency on library nodes,
	// only at this point all objects are written to the stream.
	materials.write();
	bool use_hierarchy = serializer->geometry_settings().get<ifcopenshell::geometry::settings::UseElementHierarchy>().get();
	
	std::set<std::string> geometries_written;

	//if the setting USE_ELEMENT_HIERARCHY is in use, we sort the deferreds objects by their parents.
	
	if (use_hierarchy) {
		std::sort(deferreds.begin(), deferreds.end());
	}
	
	for (std::vector<DeferredObject>::const_iterator it = deferreds.begin(); it != deferreds.end(); ++it) {
		if (geometries_written.find(it->representation_id) != geometries_written.end()) {
			continue;
		}
		geometries_written.insert(it->representation_id);
		geometries.write(it->representation_id, it->type, it->vertices, it->normals, it->faces, it->edges,
            it->material_ids, it->materials, it->uvs, it->material_references);
	}
	geometries.close();

	for (std::vector<DeferredObject>::const_iterator it = deferreds.begin(); it != deferreds.end(); ++it){
		const std::string object_name = it->unique_id;

		if (use_hierarchy)
		{
			size_t parentsNumber = it->parents_.size();
			bool finished = false;

			// If we have no parent in the stack and the object has no parent, nothing to do : skip the loop
			if (parentsNumber == 0 && serializer->parentStackId.size() == 0) { finished = true; }

			while (!finished)
			{
				// If we need to add a parent
				if (serializer->parentStackId.size() <= parentsNumber)
				{
					if (serializer->parentStackId.empty()) { scene.addParent(*(it->parents_.at(0))); }
					else
					{
						size_t diff = parentsNumber - serializer->parentStackId.size();

						// If we have the wrong parent in the list
						if (serializer->parentStackId.top() != it->parents_.at(parentsNumber - diff - 1)->id()) {
							scene.closeParent();
						} else {
							// So far we have the right parents, we just need to add the missing ones
							for (size_t i = parentsNumber - diff; i < parentsNumber; i++) { scene.addParent(*(it->parents_.at(i))); }

							// if diff == 0, we can leave the loop. In fact we have the right number of parents, and the last one is ok
							if (diff == 0) { finished = true; }
						}
					}
				} else {
					// Close the finished nodes. After this we get the first case (serializer->parentStackId.size() <= parentsNumber)
					while (serializer->parentStackId.size() > parentsNumber) { scene.closeParent(); }
				}
			}
		}
		
        /// @todo redundant information using ID as both ID and Name, maybe omit Name or allow specifying what would be used as the name
		scene.add(object_name, object_name, it->representation_id, it->material_references, it->transformation);
	}

	//close the remaining parent tags.
	while (serializer->parentStackId.size() > 0) { scene.closeParent(); }

	scene.write();
	stream.endDocument();
}

bool ColladaSerializer::ready() {
	return true;
}

void ColladaSerializer::writeHeader() {
	exporter.startDocument(unit_name, unit_magnitude);
}

void ColladaSerializer::write(const IfcGeom::TriangulationElement* o) {
    exporter.write(o);
}

void ColladaSerializer::finalize() {
	exporter.endDocument();
}

#endif
