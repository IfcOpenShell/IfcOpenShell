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

#ifndef COLLADASERIALIZER_H
#define COLLADASERIALIZER_H

#include <COLLADASWStreamWriter.h>
#include <COLLADASWPrimitves.h>
#include <COLLADASWLibraryGeometries.h>
#include <COLLADASWSource.h>
#include <COLLADASWScene.h>
#include <COLLADASWNode.h>
#include <COLLADASWInstanceGeometry.h>
#include <COLLADASWLibraryVisualScenes.h>
#include <COLLADASWLibraryEffects.h>
#include <COLLADASWLibraryMaterials.h>
#include <COLLADASWBaseInputElement.h>
#include <COLLADASWAsset.h>

#include "../ifcgeom/IfcGeomObjects.h"

#include "../ifcconvert/GeometrySerializer.h"

class ColladaSerializer : public GeometrySerializer
{
private:
	class ColladaExporter
	{
	private:
		class ColladaGeometries : public COLLADASW::LibraryGeometries
		{
		public:
			explicit ColladaGeometries(COLLADASW::StreamWriter& stream)
				: COLLADASW::LibraryGeometries(&stream)
			{}
			void addFloatSource(const std::string& mesh_id, const std::string& suffix, const std::vector<float>& floats, const char* coords = "XYZ");
			void write(const std::string mesh_id, const std::string& default_material_name, const std::vector<float>& positions, const std::vector<float>& normals, const std::vector<int>& indices, const std::vector<int> material_ids, const std::vector<IfcGeomObjects::Material>& materials);
			void close();
		};
		class ColladaScene : public COLLADASW::LibraryVisualScenes
		{
		private:
			const std::string scene_id;
			bool scene_opened;
		public:
			ColladaScene(const std::string& scene_id, COLLADASW::StreamWriter& stream)
				: COLLADASW::LibraryVisualScenes(&stream)
				, scene_id(scene_id)
				, scene_opened(false)			
			{}
			void add(const std::string& node_id, const std::string& node_name, const std::string& geom_name, const std::vector<std::string>& material_ids, const std::vector<float>& matrix);
			void write();
		};
		class ColladaMaterials : public COLLADASW::LibraryMaterials
		{
		private:
			class ColladaEffects : public COLLADASW::LibraryEffects
			{
			public:
				explicit ColladaEffects(COLLADASW::StreamWriter& stream)
					: COLLADASW::LibraryEffects(&stream)
				{}
				void write(const IfcGeomObjects::Material& material);
				void close();
			};
			std::vector<IfcGeomObjects::Material> materials;
			ColladaEffects effects;
		public:
			explicit ColladaMaterials(COLLADASW::StreamWriter& stream)
				: COLLADASW::LibraryMaterials(&stream)
				, effects(stream)
			{}
			void add(const IfcGeomObjects::Material& material);
			bool contains(const IfcGeomObjects::Material& material);
			void write();
		};
		class DeferredObject {
		public:
			std::string guid, name, type;
			int obj_id;
			std::vector<float> matrix;
			std::vector<float> vertices;
			std::vector<float> normals;
			std::vector<int> indices;
			std::vector<int> material_ids;
			std::vector<IfcGeomObjects::Material> materials;
			std::vector<std::string> material_references;
			DeferredObject(const std::string& guid, const std::string& name, const std::string& type, int obj_id, const std::vector<float>& matrix, const std::vector<float>& vertices,
				const std::vector<float>& normals, const std::vector<int>& indices, const std::vector<int>& material_ids, 
				const std::vector<IfcGeomObjects::Material>& materials, const std::vector<std::string>& material_references)
				: guid(guid)
				, name(name)
				, type(type)
				, obj_id(obj_id)
				, matrix(matrix)
				, vertices(vertices)
				, normals(normals)
				, indices(indices)
				, material_ids(material_ids)
				, materials(materials)
				, material_references(material_references)
			{}
			const std::string Name() const;
		};
		COLLADABU::NativeString filename;
		COLLADASW::StreamWriter stream;
		ColladaGeometries geometries;
		ColladaScene scene;
		ColladaMaterials materials;
	public:
		ColladaExporter(const std::string& scene_name, const std::string& fn)
			: filename(fn.c_str())
			, stream(filename)
			, geometries(stream)
			, scene(scene_name, stream)
			, materials(stream)
		{}
		std::vector<DeferredObject> deferreds;
		virtual ~ColladaExporter() {}
		void startDocument();
		void writeTesselated(const std::string& guid, const std::string& name, const std::string& type, int obj_id, const std::vector<float>& matrix, const std::vector<float>& vertices, const std::vector<float>& normals, const std::vector<int>& indices, const std::vector<int>& material_ids, const std::vector<IfcGeomObjects::Material>& materials);
		void endDocument();
	};
	ColladaExporter exporter;
public:
	ColladaSerializer(const std::string& dae_filename)
		: GeometrySerializer()
		, exporter("IfcOpenShell", dae_filename)
	{}
	bool ready();
	void writeHeader();
	void writeTesselated(const IfcGeomObjects::IfcGeomObject* o);
	void writeShapeModel(const IfcGeomObjects::IfcGeomShapeModelObject* o) {}
	void finalize();
	bool isTesselated() const { return true; }
};

#endif

#endif
