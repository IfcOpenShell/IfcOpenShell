#ifndef PARSEIFCFILE_H
#define PARSEIFCFILE_H

#include "../ifcgeom/Iterator.h"
#include "osg/Geometry"
#include "osg/Material"
#include "osg/MatrixTransform"
#include "osg/ref_ptr"

#include <QObject>
#include <QString>
#include <string>
#include <vector>

class ParseIfcFile : public QObject {

  public:
    ParseIfcFile();
    ~ParseIfcFile();

    bool Parse(
        const std::string& filePath,
        std::vector<osg::ref_ptr<osg::MatrixTransform>>& matrixTransforms);

  private:
    void buildTriangleNodes(
        const std::vector<int>& fVertIds,
        const std::vector<double>& elemVertices,
        const std::vector<double>& elemNormals,
        size_t index,
        osg::ref_ptr<osg::Vec3Array> osgVertices,
        osg::ref_ptr<osg::Vec3Array> osgNormals);

    osg::ref_ptr<osg::Material> getOsgMaterial(const ifcopenshell::geometry::taxonomy::style::ptr& material);
};

#endif // PARSEIFCFILE_H
