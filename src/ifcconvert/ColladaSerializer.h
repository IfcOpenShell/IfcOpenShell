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

#include "../ifcgeom/IfcGeomIterator.h"

#include "../ifcconvert/GeometrySerializer.h"

#include <boost/numeric/ublas/matrix.hpp>
#include <boost/numeric/ublas/io.hpp>


class ColladaSerializer : public GeometrySerializer
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
                const std::vector<real_t>& floats, const char* coords = "XYZ");
            void write(const std::string &mesh_id, const std::string& default_material_name,
                const std::vector<real_t>& positions, const std::vector<real_t>& normals,
                const std::vector<int>& faces, const std::vector<int>& edges,
                const std::vector<int> material_ids, const std::vector<IfcGeom::Material>& materials,
                const std::vector<real_t>& uvs);
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
			std::stack<IfcGeom::Transformation<double> > matrixStack;
		public:
			ColladaScene(const std::string& scene_id, COLLADASW::StreamWriter& stream, ColladaSerializer *_serializer)
				: COLLADASW::LibraryVisualScenes(&stream)
				, scene_id(scene_id)
				, scene_opened(false)
                , serializer(_serializer)
			{}
			void add(const std::string& node_id, const std::string& node_name, const std::string& geom_name,
                const std::vector<std::string>& material_ids, const IfcGeom::Transformation<real_t>& matrix);
			void addParent(const IfcGeom::Element<real_t>& parent);
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
				void write(const IfcGeom::Material& material);
				void close();
                ColladaSerializer *serializer;
			};
			std::vector<IfcGeom::Material> materials;
		public:
			explicit ColladaMaterials(COLLADASW::StreamWriter& stream, ColladaSerializer *_serializer)
				: COLLADASW::LibraryMaterials(&stream)
				, serializer(_serializer)
		                , effects(stream)
			{}
			void add(const IfcGeom::Material& material);
			bool contains(const IfcGeom::Material& material);
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
			IfcGeom::Transformation<real_t> transformation;
			std::vector<real_t> vertices;
			std::vector<real_t> normals;
			std::vector<int> faces;
			std::vector<int> edges;
			std::vector<int> material_ids;
			std::vector<IfcGeom::Material> materials;
			std::vector<std::string> material_references;
            std::vector<real_t> uvs;
			std::vector<const IfcGeom::Element<real_t>*> parents_;

			DeferredObject(const std::string& unique_id, const std::string& representation_id, const std::string& type, const IfcGeom::Transformation<real_t>& transformation,
				const std::vector<real_t>& vertices, const std::vector<real_t>& normals, const std::vector<int>& faces,
				const std::vector<int>& edges, const std::vector<int>& material_ids, const std::vector<IfcGeom::Material>& materials,
				const std::vector<std::string>& material_references, const std::vector<real_t>& uvs)
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

			std::vector<const IfcGeom::Element<real_t>*>& parents() { return parents_; }
			const std::vector<const IfcGeom::Element<real_t>*>& parents() const { return parents_; }
		};
		COLLADABU::NativeString filename;
		COLLADASW::StreamWriter stream;
		ColladaScene scene;
		std::string differentiateSlabTypes(const IfcGeom::TriangulationElement<real_t>* o);
	public:
        /// @param double_precision Whether to use "double precision" (up to 16 decimals) or not (6 or 7 decimals).
		ColladaExporter(const std::string& scene_name, const std::string& fn, ColladaSerializer *_serializer,
            bool double_precision)
            : filename(fn)
            , stream(filename, double_precision)
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
		void write(const IfcGeom::TriangulationElement<real_t>* o);
		void endDocument();
	};
	ColladaExporter exporter;
	std::string unit_name;
	float unit_magnitude;
public:
    ColladaSerializer(const std::string& dae_filename, const SerializerSettings& settings)
        : GeometrySerializer(settings)
		, exporter("IfcOpenShell", dae_filename, this, settings.precision >= 15)
    {
        exporter.serializer = this;
        exporter.materials.serializer = this;
        exporter.materials.effects.serializer = this;
        exporter.geometries.serializer = this;
    }
	bool ready();
	void writeHeader();
	void write(const IfcGeom::TriangulationElement<real_t>* o);
    void write(const IfcGeom::BRepElement<real_t>* /*o*/) {}
	void finalize();
	bool isTesselated() const { return true; }
	void setUnitNameAndMagnitude(const std::string& name, float magnitude) {
		unit_name = name;
		unit_magnitude = magnitude;
	}
	void setFile(IfcParse::IfcFile*) {}
};

#endif

#endif
