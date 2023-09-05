#ifndef IFCVIEWERWIDGET_H
#define IFCVIEWERWIDGET_H

#include <QOpenGLWidget>
#include <QOpenGLFunctions>
#include <QOpenGLContext>
#include <QMatrix4x4>

#include <osg/ref_ptr>
#include <osgViewer/GraphicsWindow>
#include <osgViewer/Viewer>
#include <osg/Group>

class IfcViewerWidget : public QOpenGLWidget
{

public:
    IfcViewerWidget(qreal dpiScale, QWidget *parent = nullptr);

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
    osg::ref_ptr<osgViewer::GraphicsWindowEmbedded> m_graphicsWindow;
    osg::ref_ptr<osgViewer::Viewer> m_viewer;
    osg::ref_ptr<osg::Group> root; // OSG root node

    osgGA::EventQueue* getEventQueue() const;
    unsigned int getMouseButtonNum(QMouseEvent* event);
    void buildSceneData();
};

#endif // IFCVIEWERWIDGET_H
