#ifndef IFCVIEWERWIDGET_H
#define IFCVIEWERWIDGET_H

#include <QOpenGLWidget>
#include <QOpenGLFunctions>
#include <QOpenGLContext>
#include <QMatrix4x4>

#include <osg/ref_ptr>
#include <osgViewer/GraphicsWindow>
#include <osgViewer/Viewer>
#include <osgGA/TrackballManipulator>
#include <osg/Group>
#include <string>

#include "ParseIfcFile.h"
#include "osg/Vec4"

class IfcViewerWidget : public QOpenGLWidget
{
    Q_OBJECT

public:
    IfcViewerWidget(
        qreal dpiScale, 
        QWidget *parent = nullptr
    );

public slots:
    void loadFile(const std::string& filePath);

protected:
    virtual void initializeGL() override; // to set up resources, state
    virtual void resizeGL(int w, int h) override; // to set up viewport, projection, etc.
    virtual void paintGL() override; // to render OpenGL scene

    virtual void mousePressEvent(QMouseEvent *event) override;
    virtual void mouseMoveEvent(QMouseEvent *event) override;
    virtual void mouseReleaseEvent(QMouseEvent *event) override;
    virtual void wheelEvent(QWheelEvent *event) override;
    virtual bool event(QEvent* event) override;

private:
    qreal m_dpiScale;
    QMatrix4x4 m_projection;
    osg::Vec4 m_clearColor;
    osg::ref_ptr<osgGA::TrackballManipulator> m_mouseHandler;
    osg::ref_ptr<osgViewer::GraphicsWindowEmbedded> m_graphicsWindow;
    osg::ref_ptr<osgViewer::Viewer> m_viewer;
    osg::ref_ptr<osg::Group> root; // OSG root node

    ParseIfcFile m_parser;

    osgGA::EventQueue* getEventQueue() const;
    unsigned int getMouseButtonNum(QMouseEvent* event);

    void setupViewController();

    void orientScene(osg::ref_ptr<osg::Group> rootGroup);
};

#endif // IFCVIEWERWIDGET_H
