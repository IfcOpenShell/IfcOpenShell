#include "ParseIfcFile.h"
#include "MessageLogger.h"

#include "osg/Array"
#include "osg/Geometry"
#include "osg/Material"
#include "osg/PrimitiveSet"
#include "osg/StateAttribute"
#include "osg/StateSet"
#include "osg/Vec4"
#include "osg/ref_ptr"
#include <OpenGL/OpenGL.h>
#include <cstddef> // size_t
#include <string>

#include <osg/Vec3>
#include <vector>

ParseIfcFile::ParseIfcFile() {}

ParseIfcFile::~ParseIfcFile() {}

bool ParseIfcFile::Parse(
    const std::string& filePath,
    std::vector<osg::ref_ptr<osg::Geometry>>& geometries
) {
    IfcParse::IfcFile file(filePath);

    IfcGeom::IteratorSettings settings;
    settings.set(IfcGeom::IteratorSettings::USE_WORLD_COORDS, true);
    settings.set(IfcGeom::IteratorSettings::WELD_VERTICES, false);
    settings.set(IfcGeom::IteratorSettings::APPLY_DEFAULT_MATERIALS, true);

    IfcGeom::Iterator* it = new IfcGeom::Iterator(settings, &file);
    if (!it->initialize()) {
        MessageLogger::log("Error: Iterator failed to initialize! Aborting.");
        delete it;
        return false;
    }

    do {
        //const IfcGeom::BRepElement* bRepElem = it->get_native();
        const IfcGeom::TriangulationElement* triElem = static_cast<const IfcGeom::TriangulationElement*>(it->get());

        // Print element info
        std::string elemInfo = triElem->type();
        elemInfo += triElem->name() == "" ? "" : ": " + triElem->name();
        MessageLogger::log(elemInfo);

        // Transformation Matrix
        const std::vector<double>& matrixData = triElem->transformation().matrix().data();
        std::string matrixStr = "";
        int di = 0;
        for (auto d : matrixData) {
            if (di == 4) {
                matrixStr += "\n";
                di = 0;
            }
            matrixStr += std::to_string(d) + "  ";
            di++;
        }
        //MessageLogger::log(matrixStr); // Print matrix data

        //MessageLogger::log(triElem->geometry().id());

        const boost::shared_ptr<IfcGeom::Representation::Triangulation>& triElemGeom = triElem->geometry_pointer();

        const std::vector<int>& elemFaces = triElemGeom->faces();
        const std::vector<double>& elemVertices = triElemGeom->verts();
        const std::vector<double>& elemNormals = triElemGeom->normals();
        const std::vector<IfcGeom::Material>& elemMats = triElemGeom->materials();
        const std::vector<int>& elemMatIds = triElemGeom->material_ids();

        std::map<int, osg::ref_ptr<osg::Material>> uniqueMaterials;

        std::map<int, std::vector<int>> elemFaces_grouped;
        auto fit = elemFaces.begin();
        for (const int& matId : elemMatIds) {
            for (int i = 0; i < 3; ++i) {
                elemFaces_grouped[matId].push_back(*fit++);
            }
        }

        if (fit != elemFaces.end())
            MessageLogger::log("** Failed to map the faces to material IDs!");

        for (const auto& group : elemFaces_grouped) {
            int matId = group.first;
            const std::vector<int>& fVertIds = group.second;

            osg::ref_ptr<osg::Vec3Array> osgVertices = new osg::Vec3Array;
            osg::ref_ptr<osg::Vec3Array> osgNormals = new osg::Vec3Array;

            for (size_t i = 0; i < fVertIds.size(); i += 3) {
                buildTriangleNodes(
                        fVertIds, elemVertices, elemNormals, i,
                        osgVertices, osgNormals
                    );
            }

            osg::ref_ptr<osg::Geometry> geometry = new osg::Geometry;

            geometry->setVertexArray(osgVertices);
            geometry->setNormalArray(osgNormals);
            geometry->setNormalBinding(osg::Geometry::BIND_PER_VERTEX);

            osg::ref_ptr<osg::DrawArrays> drawArrays = new osg::DrawArrays(
                    osg::PrimitiveSet::TRIANGLES, 0, osgVertices->size());
            geometry->addPrimitiveSet(drawArrays);

            osg::ref_ptr<osg::Material> osgMaterial = getOsgMaterial(elemMats[matId]);
            geometry->getOrCreateStateSet()->setAttributeAndModes(osgMaterial.get());

            geometries.push_back(geometry);
        }

    } while (it->next());

    return true;
}

void ParseIfcFile::buildTriangleNodes(
    const std::vector<int>& fVertIds,
    const std::vector<double>& elemVertices, 
    const std::vector<double>& elemNormals,
    size_t index,
    osg::ref_ptr<osg::Vec3Array> osgVertices,
    osg::ref_ptr<osg::Vec3Array> osgNormals)
{
    auto addVertexAndNormal = [fVertIds, elemVertices, elemNormals, osgVertices, osgNormals](size_t i) {

        size_t initVertIndex = 3 * fVertIds[i];
        size_t x_vertIndex = initVertIndex;
        size_t y_vertIndex = initVertIndex + 1;
        size_t z_vertIndex = initVertIndex + 2;

        osgVertices->push_back(osg::Vec3 (
            elemVertices[x_vertIndex], 
            elemVertices[y_vertIndex], 
            elemVertices[z_vertIndex]
        ));

        osgNormals->push_back(osg::Vec3 (
            elemNormals[x_vertIndex], 
            elemNormals[y_vertIndex], 
            elemNormals[z_vertIndex]
        ));
    };

    addVertexAndNormal(index);
    addVertexAndNormal(index + 1);
    addVertexAndNormal(index + 2);
}

osg::ref_ptr<osg::Material> ParseIfcFile::getOsgMaterial(const IfcGeom::Material& material)
{
    const double* diffuseColor = material.diffuse();
    osg::Vec4 matOsgDiffuseColor(
            diffuseColor[0], 
            diffuseColor[1], 
            diffuseColor[2], 
            material.transparency()
        );

    osg::ref_ptr<osg::Material> osgMaterial = new osg::Material;
    osgMaterial->setDiffuse(osg::Material::FRONT_AND_BACK, matOsgDiffuseColor);

    return osgMaterial;
}
