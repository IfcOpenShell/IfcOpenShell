#include "ParseIfcFile.h"
#include "MessageLogger.h"

#include "osg/Array"
#include "osg/Geometry"
#include "osg/Material"
#include "osg/PrimitiveSet"
#include "osg/StateAttribute"
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

    IfcGeom::Iterator* it = new IfcGeom::Iterator(settings, &file);
    if (!it->initialize()) {
        MessageLogger::log("Error: Iterator failed to initialize! Aborting.");
        delete it;
        return false;
    }

    do {
        //const IfcGeom::BRepElement* bRepElem = it->get_native();
        const IfcGeom::TriangulationElement* triElem = static_cast<const IfcGeom::TriangulationElement*>(it->get());
        MessageLogger::log(triElem->type() + ": " + triElem->name());

        const boost::shared_ptr<IfcGeom::Representation::Triangulation>& triElemGeom = triElem->geometry_pointer();

        const std::vector<int>& elemFaces = triElemGeom->faces();
        const std::vector<double>& elemVertices = triElemGeom->verts();
        const std::vector<double>& elemNormals = triElemGeom->normals();

        std::vector<Triangle> triangles = this->createTriangles(elemFaces, elemVertices, elemNormals);

        osg::ref_ptr<osg::Vec3Array> osgVertices = new osg::Vec3Array;
        osg::ref_ptr<osg::Vec3Array> osgNormals = new osg::Vec3Array;

        // Combine the triangles from the vector into a single Vec3Array
        for (const auto& triangle : triangles) {
            osgVertices->push_back(triangle.vn1.vertex);
            osgVertices->push_back(triangle.vn2.vertex);
            osgVertices->push_back(triangle.vn3.vertex);

            osgNormals->push_back(triangle.vn1.normal);
            osgNormals->push_back(triangle.vn2.normal);
            osgNormals->push_back(triangle.vn3.normal);
        }

        osg::ref_ptr<osg::Geometry> elemGeom = new osg::Geometry;
        elemGeom->setVertexArray(osgVertices);
        elemGeom->setNormalArray(osgNormals);
        elemGeom->setNormalBinding(osg::Geometry::BIND_PER_VERTEX);

        osg::ref_ptr<osg::DrawArrays> drawArrays = new osg::DrawArrays(
                osg::PrimitiveSet::TRIANGLES, 0, osgVertices->size());
        elemGeom->addPrimitiveSet(drawArrays);

        // materials
        const std::vector<IfcGeom::Material>& elemMats = triElemGeom->materials();
        std::vector<osg::ref_ptr<osg::Material>> elemOsgMats;
        for (const IfcGeom::Material& mat : elemMats) {
            //MessageLogger::log("    " + mat.original_name());
            elemOsgMats.push_back(getOsgMaterial(mat));
        }
        if (elemOsgMats.size()) {
            // Todo: set respective material for each part of the element
            elemGeom->getOrCreateStateSet()->setAttributeAndModes(elemOsgMats[0].get());
        } else { // sometimes material values are not available (like for IfcOpeningElement)
            osg::ref_ptr<osg::Material> osgMaterial = new osg::Material;
            osgMaterial->setDiffuse(osg::Material::FRONT_AND_BACK, this->getDefaultOsgDiffuseColor());
            elemGeom->getOrCreateStateSet()->setAttributeAndModes(osgMaterial.get());
        }

        geometries.push_back(elemGeom);

    } while (it->next());

    return true;
}

std::vector<Triangle> ParseIfcFile::createTriangles(
    const std::vector<int>& elemFaces,
    const std::vector<double>& elemVertices,
    const std::vector<double>& elemNormals
) {

    std::vector<Triangle> triangles;

    for (size_t i = 0; i < elemFaces.size(); i += 3) {

        auto createVertexWithNormal = [elemFaces, elemVertices, elemNormals](size_t fi) {

            VertexWithNormal vn;

            size_t initVertIndex = 3 * elemFaces[fi];
            size_t x_vertIndex = initVertIndex;
            size_t y_vertIndex = initVertIndex + 1;
            size_t z_vertIndex = initVertIndex + 2;

            vn.vertex = osg::Vec3 (
                elemVertices[x_vertIndex], 
                elemVertices[y_vertIndex], 
                elemVertices[z_vertIndex]
            );

            vn.normal = osg::Vec3 (
                elemNormals[x_vertIndex], 
                elemNormals[y_vertIndex], 
                elemNormals[z_vertIndex]
            );

            return vn;
        };

        auto createTriangle = [createVertexWithNormal, i]() {

            Triangle triangle;

            triangle.vn1 = createVertexWithNormal(i);
            triangle.vn2 = createVertexWithNormal(i + 1);
            triangle.vn3 = createVertexWithNormal(i + 2);

            return triangle;
        };

        triangles.push_back(createTriangle());
    }

    return triangles;

} 

osg::Vec4 ParseIfcFile::getDefaultOsgDiffuseColor()
{
    osg::Vec4 osgDiffuseColor(0.4f, 0.4f, 0.8f, 1.0f);
    return osgDiffuseColor;
}

osg::ref_ptr<osg::Material> ParseIfcFile::getOsgMaterial(const IfcGeom::Material& material)
{
    osg::Vec4 osgDiffuseColor = getDefaultOsgDiffuseColor();

    if(material.hasDiffuse()) {
        const double* diffuseColor = material.diffuse();
        osg::Vec4 matOsgDiffuseColor(
                diffuseColor[0], 
                diffuseColor[1], 
                diffuseColor[2], 
                material.transparency()
            );
        osgDiffuseColor = matOsgDiffuseColor;
    } 

    osg::ref_ptr<osg::Material> osgMaterial = new osg::Material;
    osgMaterial->setDiffuse(osg::Material::FRONT_AND_BACK, osgDiffuseColor);

    return osgMaterial;
}
