#include "ParseIfcFile.h"

#include "MessageLogger.h"
#include "osg/Array"
#include "osg/Geometry"
#include "osg/Material"
#include "osg/Matrixd"
#include "osg/MatrixTransform"
#include "osg/PrimitiveSet"
#include "osg/ref_ptr"
#include "osg/StateAttribute"
#include "osg/StateSet"
#include "osg/Vec4"

#include <cstddef> // size_t
#include <osg/Vec3>
#include <string>
#include <vector>

ParseIfcFile::ParseIfcFile() {}

ParseIfcFile::~ParseIfcFile() {}

bool ParseIfcFile::Parse(
    const std::string& filePath,
    std::vector<osg::ref_ptr<osg::MatrixTransform>>& matrixTransforms
) {
    IfcParse::IfcFile file(filePath);
    ifcopenshell::geometry::Settings settings;
    settings.set("use-world-coords", false);
    settings.set("weld-vertices", false);
    settings.set("apply-default-materials", true);

    IfcGeom::Iterator* it = new IfcGeom::Iterator(settings, &file);
    if (!it->initialize()) {
        MessageLogger::log("Error: Iterator failed to initialize! Aborting.");
        delete it;
        return false;
    }

    std::string lastId;
    std::vector<osg::ref_ptr<osg::Geometry>> lastGeometrySet;

    do {
        //const IfcGeom::BRepElement* bRepElem = it->get_native();
        const IfcGeom::TriangulationElement* triElem = static_cast<const IfcGeom::TriangulationElement*>(it->get());

        // Print element info
        std::string elemInfo = triElem->type();
        elemInfo += triElem->name() == "" ? "" : ": " + triElem->name();
        MessageLogger::log(elemInfo);
        
        const std::string id = triElem->geometry().id();
        
        //MessageLogger::log("id: " + id);

        // Transformation Matrix
        std::vector<double> matrixData;
        auto transform4x4 = triElem->transformation().data()->components();
        for (int col = 0; col<4; col++)
        {
            for (int row =0; row<3; row++)
            {
                matrixData.push_back(transform4x4(row,col));
            }

        }

        // Debugging:
        std::string matrixStr = "";
        int col = 0;
        int row = 0;
        for (auto d : matrixData) {
            matrixStr += std::to_string(d) + "  ";
            if (++col == 3) {
                std::string lastCol = (row == 3) ? "1" : "0";
                matrixStr += lastCol + "\n";
                col = 0;
                row++;
            }
        }
        //MessageLogger::log(matrixStr); // Print matrix data
        
        const osg::Matrixd matrixd (
            matrixData[0], matrixData[1], matrixData[2], 0,
            matrixData[3], matrixData[4], matrixData[5], 0,
            matrixData[6], matrixData[7], matrixData[8], 0,
            matrixData[9], matrixData[10], matrixData[11], 1
        );

        const osg::ref_ptr<osg::MatrixTransform> matrixTransform = new osg::MatrixTransform;
        matrixTransform->setMatrix(matrixd);

        if (id == lastId) {
            for (auto geometry : lastGeometrySet) {
                matrixTransform->addChild(geometry);
            }
            matrixTransforms.push_back(matrixTransform);
            continue;
        }

        const boost::shared_ptr<IfcGeom::Representation::Triangulation>& triElemGeom = triElem->geometry_pointer();

        const std::vector<int>& elemFaces = triElemGeom->faces();
        const std::vector<double>& elemVertices = triElemGeom->verts();
        const std::vector<double>& elemNormals = triElemGeom->normals();
        const std::vector<ifcopenshell::geometry::taxonomy::style::ptr>& elemMats = triElemGeom->materials();
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

        std::vector<osg::ref_ptr<osg::Geometry>> geometrySet;

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

            matrixTransform->addChild(geometry);

            geometrySet.push_back(geometry);
        }

        matrixTransforms.push_back(matrixTransform);

        lastId = id;
        lastGeometrySet = geometrySet;

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

osg::ref_ptr<osg::Material> ParseIfcFile::getOsgMaterial(const ifcopenshell::geometry::taxonomy::style::ptr& material)
{
    ifcopenshell::geometry::taxonomy::colour diffuseColor = material->diffuse;
    osg::Vec4 matOsgDiffuseColor(
        diffuseColor.r(),
        diffuseColor.g(),
        diffuseColor.b(),
        material->transparency);

    osg::ref_ptr<osg::Material> osgMaterial = new osg::Material;
    osgMaterial->setDiffuse(osg::Material::FRONT_AND_BACK, matOsgDiffuseColor);

    return osgMaterial;
}
