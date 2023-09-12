#include "IfcViewerWidget.h"
#include <OpenGL/OpenGL.h>
#include <osg/ShapeDrawable>
#include <osg/Material>
#include <osg/MatrixTransform>
#include <osg/ComputeBoundsVisitor>
#include <QMouseEvent>
#include <QWheelEvent>
#include <string>
#include <vector>
#include "MainWindow.h"
#include "MessageLogger.h"
#include "osg/Geode"
#include "osg/Geometry"
#include "osg/Vec3"
#include "osg/ref_ptr"
#include "osgGA/TrackballManipulator"

IfcViewerWidget::IfcViewerWidget(qreal dpiScale, QWidget *parent) : 
    QOpenGLWidget(parent),
    m_dpiScale(dpiScale),
    m_graphicsWindow(new osgViewer::GraphicsWindowEmbedded(
                         this->x(), this->y(),
                         this->width(), this->height()
                     )),
    m_viewer(new osgViewer::Viewer),
    root(new osg::Group)
{ 
    m_mouseHandler = new osgGA::TrackballManipulator;
    m_clearColor = osg::Vec4(0.7, 0.7, 0.7, 1.0);

    //debug - override
    //std::string filePath = "/Users/onizudb/Downloads/IFC/wallAtOrigin.ifc";
    //this->loadFile(filePath);
}

void IfcViewerWidget::initializeGL()
{
    MessageLogger::log("Press `Cmd/Ctrl + o` or use the File menu to open an IFC file");

    // Set up the rendering context, load shaders and other resources, etc.:

    // Set the root node as the scene data for the viewer
    m_viewer->setSceneData(root);

    osg::StateSet* state = root->getOrCreateStateSet();
    state->setMode(GL_DEPTH_TEST, osg::StateAttribute::ON);

    m_viewer->getCamera()->setViewport(0, 0, this->width(), this->height());
    m_viewer->getCamera()->setClearColor(m_clearColor);
    m_viewer->getCamera()->setGraphicsContext(m_graphicsWindow);

    // Add event handlers

    this->setMouseTracking(false);

    m_mouseHandler->setAllowThrow(false);

    m_viewer->setCameraManipulator(m_mouseHandler);

    m_viewer->setThreadingModel(osgViewer::Viewer::SingleThreaded);
    m_viewer->realize();
}

void IfcViewerWidget::resizeGL(int w, int h)
{
    this->getEventQueue()->windowResize(this->x() * m_dpiScale, this->y() * m_dpiScale, w * m_dpiScale, h * m_dpiScale);
    m_graphicsWindow->resized(this->x() * m_dpiScale, this->y() * m_dpiScale, w * m_dpiScale, h * m_dpiScale);

    m_viewer->getCamera()->setViewport(0, 0, this->width() * m_dpiScale, this->height() * m_dpiScale);
    
    const float aspectRatio = static_cast<float>(w) / static_cast<float>(h);
    m_viewer->getCamera()->setProjectionMatrixAsPerspective(30.0f, aspectRatio, 1.0f, 1000.0f);
}

void IfcViewerWidget::paintGL()
{
    // Render OSG scene
    m_viewer->frame();
}

void IfcViewerWidget::mouseMoveEvent(QMouseEvent *event)
{
    this->getEventQueue()->mouseMotion(event->position().x() * m_dpiScale, event->position().y() * m_dpiScale);
}

void IfcViewerWidget::mousePressEvent(QMouseEvent *event)
{
    unsigned int button = this->getMouseButtonNum(event);
    this->getEventQueue()->mouseButtonPress(event->position().x() * m_dpiScale, event->position().y() * m_dpiScale, button);
}

void IfcViewerWidget::mouseReleaseEvent(QMouseEvent *event)
{
    unsigned int button = this->getMouseButtonNum(event);
    this->getEventQueue()->mouseButtonRelease(event->position().x() * m_dpiScale, event->position().y() * m_dpiScale, button);
}

void IfcViewerWidget::wheelEvent(QWheelEvent *event)
{
    int delta = event->angleDelta().y();
    osgGA::GUIEventAdapter::ScrollingMotion motion = delta > 0 ?
            osgGA::GUIEventAdapter::SCROLL_UP : osgGA::GUIEventAdapter::SCROLL_DOWN;
    this->getEventQueue()->mouseScroll(motion);
}

bool IfcViewerWidget::event(QEvent* event)
{
    bool handled = QOpenGLWidget::event(event);
    this->update();
    return handled;
}

osgGA::EventQueue* IfcViewerWidget::getEventQueue() const 
{
    osgGA::EventQueue* eventQueue = m_graphicsWindow->getEventQueue();
    return eventQueue;
}

unsigned int IfcViewerWidget::getMouseButtonNum(QMouseEvent* event)
{
    unsigned int button = 0;
    switch (event->button()){
    case Qt::LeftButton:
        button = 1;
        break;
    case Qt::MiddleButton:
        button = 2;
        break;
    case Qt::RightButton:
        button = 3;
        break;
    default:
        break;
    }
    return button;
}

void IfcViewerWidget::loadFile(const std::string& filePath)
{
    std::vector<osg::ref_ptr<osg::Geometry>> geometries;

    if(!m_parser.Parse(filePath, geometries)) {
        MessageLogger::log("Failed to prepare IFC geometry");
        return;
    }

    MessageLogger::log("\nIFC geometry prepared");

    osg::ref_ptr<osg::Geode> geode = new osg::Geode;
    for (auto geometry : geometries) {
        geode->addDrawable(geometry);
    }

    prepareSceneWithGeometry(geode);

    m_viewer->setCameraManipulator(m_mouseHandler);
}

void IfcViewerWidget::prepareSceneWithGeometry(osg::ref_ptr<osg::Geode> geode)
{
    // Apply a rotation to the model
    // MatrixTransform allows applying transformations (translation, rotation, scaling) to its children
    osg::ref_ptr<osg::MatrixTransform> rotationTransform = new osg::MatrixTransform;
    rotationTransform->setMatrix(osg::Matrix::rotate(osg::DegreesToRadians(45.0), osg::Vec3(0.0, 0.0, 1.0)));
    rotationTransform->addChild(geode);

    // Add the model to the root node
    root->addChild(rotationTransform);
}
