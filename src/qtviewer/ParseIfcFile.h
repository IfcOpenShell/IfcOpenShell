#ifndef PARSEIFCFILE_H
#define PARSEIFCFILE_H

#include <QObject>
#include <QString>
#include <string>
#include <vector>
#include "../ifcgeom_schema_agnostic/IfcGeomIterator.h"
#include "osg/Material"
#include "osg/ref_ptr"
#include "osg/Geometry"

struct VertexWithNormal {
    osg::Vec3 vertex;
    osg::Vec3 normal;
};

struct Triangle {
    VertexWithNormal vn1;
    VertexWithNormal vn2;
    VertexWithNormal vn3;
};

class ParseIfcFile : public QObject
{

public:
    ParseIfcFile();
    ~ParseIfcFile();

    bool Parse(
        const std::string& filePath,
        std::vector<osg::ref_ptr<osg::Geometry>>& geometries
    );

private:
    std::vector<Triangle> createTriangles(
            const std::vector<int>& elemFaces,
            const std::vector<double>& elemVertices,
            const std::vector<double>& elemNormals
        );
    osg::Vec4 getDefaultOsgDiffuseColor();
    osg::ref_ptr<osg::Material> getOsgMaterial(const IfcGeom::Material& material);
};

#endif // PARSEIFCFILE_H
