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
#include "../ifcconvert/SurfaceStyle.h"

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
			void write(const std::string mesh_id, const std::vector<float>& positions, const std::vector<float>& normals, const std::vector<int>& indices);
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
			void add(const std::string& node_id, const std::string& node_name, const std::string& geom_id, const std::string& material_id, const std::vector<float>& matrix);
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
				void write(const SurfaceStyle& style);
				void close();
			};
			std::vector<SurfaceStyle> surface_styles;
			ColladaEffects effects;
		public:
			explicit ColladaMaterials(COLLADASW::StreamWriter& stream)
				: COLLADASW::LibraryMaterials(&stream)
				, effects(stream)
			{}
			void add(const SurfaceStyle& style);
			bool contains(const std::string& name);
			void write();
		};
		class DeferedObject {
		public:
			const std::string type;
			int obj_id;
			const std::vector<float> matrix;
			const std::vector<float> vertices;
			const std::vector<float> normals;
			const std::vector<int> indices;
			DeferedObject(const std::string& type, int obj_id, const std::vector<float>& matrix, const std::vector<float>& vertices,
				const std::vector<float>& normals, const std::vector<int>& indices)
				: type(type)
				, obj_id(obj_id)
				, matrix(matrix)
				, vertices(vertices)
				, normals(normals)
				, indices(indices)
			{}
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
		std::vector<DeferedObject> deferreds;
		virtual ~ColladaExporter() {}
		void startDocument();
		void writeTesselated(const std::string& type, int obj_id, const std::vector<float>& matrix, const std::vector<float>& vertices, const std::vector<float>& normals, const std::vector<int>& indices);
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