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

#ifdef _MSC_VER
#pragma warning(push)
#pragma warning(disable : 4201 4512)
#else
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wignored-qualifiers"
#endif
#include <COLLADASWStreamWriter.h>
#include <COLLADASWNode.h>
#include <COLLADASWLibraryGeometries.h>
#include <COLLADASWLibraryVisualScenes.h>
#include <COLLADASWLibraryEffects.h>
#include <COLLADASWLibraryMaterials.h>
#ifdef _MSC_VER
#pragma warning(pop)
#else
#pragma GCC diagnostic pop
#endif

#include "../ifcgeom/Iterator.h"

#include "../serializers/serializers_api.h"
#include "../ifcgeom/GeometrySerializer.h"

#include <boost/numeric/ublas/matrix.hpp>
#include <boost/numeric/ublas/io.hpp>


class SERIALIZERS_API ColladaSerializer : public WriteOnlyGeometrySerializer
{
	// TODO The vast amount of implement details of ColladaSerializer could be hidden to the cpp file.
private:
	std::stack<int> parentStackId;

	class ColladaExporter
	{
	private:
		class ColladaGeometries : public COLLADASW::LibraryGeometries
		{
			ColladaGeometries(const ColladaGeometries&); //N/A
			ColladaGeometries& operator =(const ColladaGeometries&); //N/A
		public:
			explicit ColladaGeometries(COLLADASW::StreamWriter& stream, ColladaSerializer *_serializer)
				: COLLADASW::LibraryGeometries(&stream)
                , serializer(_serializer)
			{}
            void addFloatSource(const std::string& mesh_id, const std::string& suffix,
                const std::vector<double>& floats, const char* coords = "XYZ");
            /// @todo pass simply DeferredObject?
            void write(
                const std::string &mesh_id, const std::string &default_material_name,
                const std::vector<double>& positions, const std::vector<double>& normals,
                const std::vector<int>& faces, const std::vector<int>& edges,
                const std::vector<int>& material_ids, const std::vector<ifcopenshell::geometry::taxonomy::style::ptr>& materials,
                const std::vector<double>& uvs, const std::vector<std::string>& material_references);
			void close();
            ColladaSerializer *serializer;
		};
		class ColladaScene : public COLLADASW::LibraryVisualScenes
		{
		private:
			ColladaScene(const ColladaScene&); //N/A
			ColladaScene& operator =(const ColladaScene&); //N/A

			const std::string scene_id;
			bool scene_opened;
			std::stack<COLLADASW::Node*> parentNodes;
			std::stack<ifcopenshell::geometry::taxonomy::matrix4> matrixStack;
		public:
			ColladaScene(const std::string& scene_id, COLLADASW::StreamWriter& stream, ColladaSerializer *_serializer)
				: COLLADASW::LibraryVisualScenes(&stream)
				, scene_id(scene_id)
				, scene_opened(false)
                , serializer(_serializer)
			{}
			void add(const std::string& node_id, const std::string& node_name, const std::string& geom_name,
                const std::vector<std::string>& material_ids, const IfcGeom::Transformation& matrix);
			void addParent(const IfcGeom::Element& parent);
			void closeParent();
			COLLADASW::Node* GetDirectParent();
			void write();
            ColladaSerializer *serializer;
		};
		class ColladaMaterials : public COLLADASW::LibraryMaterials
		{
			ColladaMaterials(const ColladaMaterials&); //N/A
			ColladaMaterials& operator =(const ColladaMaterials&); //N/A
		private:
			class ColladaEffects : public COLLADASW::LibraryEffects
			{
				ColladaEffects(const ColladaEffects&); //N/A
				ColladaEffects& operator =(const ColladaEffects&); //N/A
			public:
				explicit ColladaEffects(COLLADASW::StreamWriter& stream)
					: COLLADASW::LibraryEffects(&stream)
				{}
				void write(const ifcopenshell::geometry::taxonomy::style::ptr& material, const std::string &material_uri);
				void close();
                ColladaSerializer *serializer;
			};
			std::vector<ifcopenshell::geometry::taxonomy::style::ptr> materials;
			std::vector<std::string> material_uris;
		public:
			explicit ColladaMaterials(COLLADASW::StreamWriter& stream, ColladaSerializer *_serializer)
				: COLLADASW::LibraryMaterials(&stream)
				, serializer(_serializer)
		                , effects(stream)
			{}
			void add(const ifcopenshell::geometry::taxonomy::style::ptr& material);
			std::string getMaterialUri(const ifcopenshell::geometry::taxonomy::style::ptr& material);
			bool contains(const ifcopenshell::geometry::taxonomy::style::ptr& material);
			void write();
            ColladaSerializer *serializer;
            ColladaEffects effects;
		};

		class DeferredObject {
		
			friend bool operator < (const DeferredObject& def_obj1, const DeferredObject& def_obj2) {
				size_t size = (def_obj1.parents_.size() < def_obj2.parents_.size() ? def_obj1.parents_.size() : def_obj2.parents_.size());
				size_t cpt = 0;

				// Skip the shared parents
				while (cpt < size && *(def_obj1.parents_.at(cpt)) == *(def_obj2.parents_.at(cpt))) {
					cpt++;
				}

				// If a parent list container the other one
				if (cpt >= size) {
					return def_obj1.parents_.size() < def_obj2.parents_.size();
				} else {
					return *(def_obj1.parents_.at(cpt)) < *(def_obj2.parents_.at(cpt));
				}
			}

		public:
			std::string unique_id, representation_id, type;
			IfcGeom::Transformation transformation;
			std::vector<double> vertices;
			std::vector<double> normals;
			std::vector<int> faces;
			std::vector<int> edges;
			std::vector<int> material_ids;
			std::vector<ifcopenshell::geometry::taxonomy::style::ptr> materials;
			std::vector<std::string> material_references;
            std::vector<double> uvs;
			std::vector<const IfcGeom::Element*> parents_;

			DeferredObject(const std::string& unique_id, const std::string& representation_id, const std::string& type, const IfcGeom::Transformation& transformation,
				const std::vector<double>& vertices, const std::vector<double>& normals, const std::vector<int>& faces,
				const std::vector<int>& edges, const std::vector<int>& material_ids, const std::vector<ifcopenshell::geometry::taxonomy::style::ptr>& materials,
				const std::vector<std::string>& material_references, const std::vector<double>& uvs)
				: unique_id(unique_id)
				, representation_id(representation_id)
				, type(type)
				, transformation(transformation)
				, vertices(vertices)
				, normals(normals)
				, faces(faces)
				, edges(edges)
				, material_ids(material_ids)
				, materials(materials)
				, material_references(material_references)
				, uvs(uvs)
			{}

			std::vector<const IfcGeom::Element*>& parents() { return parents_; }
			const std::vector<const IfcGeom::Element*>& parents() const { return parents_; }
		};
		COLLADABU::NativeString filename;
		COLLADASW::StreamWriter stream;
		ColladaScene scene;
	public:
        /// @param double_precision Whether to use "double precision" (up to 16 decimals) or not (6 or 7 decimals).
		ColladaExporter(const std::string& scene_name, const std::string& fn, ColladaSerializer *_serializer,
            bool double_precision)
            : filename(fn)
            , stream(COLLADASW::NativeString(filename.c_str(), COLLADASW::NativeString::ENCODING_UTF8), double_precision)
			, scene(scene_name, stream, _serializer)
			, materials(stream, _serializer)
			, geometries(stream, _serializer)
			, serializer(_serializer)
		{
        }
        ColladaMaterials materials;
        ColladaGeometries geometries;
        ColladaSerializer *serializer;
		std::vector<DeferredObject> deferreds;
		virtual ~ColladaExporter() {}
		void startDocument(const std::string& unit_name, float unit_magnitude);
		void write(const IfcGeom::TriangulationElement* o);
		void endDocument();
	};
	ColladaExporter exporter;
	std::string unit_name;
	float unit_magnitude;
public:
    ColladaSerializer(const std::string& dae_filename, const ifcopenshell::geometry::Settings& geometry_settings, const ifcopenshell::geometry::SerializerSettings& settings)
        : WriteOnlyGeometrySerializer(geometry_settings, settings)
		, exporter("IfcOpenShell", dae_filename, this, settings.get<ifcopenshell::geometry::settings::FloatingPointDigits>().get() >= 15)
    {
        exporter.serializer = this;
        exporter.materials.serializer = this;
        exporter.materials.effects.serializer = this;
        exporter.geometries.serializer = this;
    }
	bool ready();
	void writeHeader();
	void write(const IfcGeom::TriangulationElement* o);
    void write(const IfcGeom::BRepElement* /*o*/) {}
	void finalize();
	bool isTesselated() const { return true; }
	void setUnitNameAndMagnitude(const std::string& name, float magnitude) {
		unit_name = name;
		unit_magnitude = magnitude;
	}
	void setFile(IfcParse::IfcFile*) {}

    std::string object_id(const IfcGeom::Element* o) /*override*/;

private:
    static std::string differentiateSlabTypes(const IfcUtil::IfcBaseEntity* slab);
};

#endif

#endif
