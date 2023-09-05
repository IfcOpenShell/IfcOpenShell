#include "IfcViewerWidget.h"
#include <OpenGL/OpenGL.h>
#include <osgGA/TrackballManipulator>
#include <osgGA/FirstPersonManipulator>
#include <osg/ShapeDrawable>
#include <osg/Material>
#include <osg/MatrixTransform>
#include <QMouseEvent>
#include <QWheelEvent>
#include <string>
#include "MessageLogger.h"
#include "MouseHandler.h"
#include "osg/ref_ptr"

IfcViewerWidget::IfcViewerWidget(qreal dpiScale, QWidget *parent) : 
    QOpenGLWidget(parent),
    m_dpiScale(dpiScale),
    m_graphicsWindow(new osgViewer::GraphicsWindowEmbedded(
                         this->x(), this->y(),
                         this->width(), this->height()
                     )),
    m_viewer(new osgViewer::Viewer),
    root(new osg::Group)
{ }

void IfcViewerWidget::initializeGL()
{
    // Set up the rendering context, load shaders and other resources, etc.:

    MessageLogger::log("devicePixelRatio: " + std::to_string(m_dpiScale));

    this->buildSceneData();

    // Set the root node as the scene data for the viewer
    m_viewer->setSceneData(root);

    osg::StateSet* state = root->getOrCreateStateSet();
    state->setMode(GL_DEPTH_TEST, osg::StateAttribute::ON);

    m_viewer->getCamera()->setViewport(0, 0, this->width(), this->height());
    m_viewer->getCamera()->setClearColor(osg::Vec4(0.8f, 0.8f, 0.8f, 1.0f));
    m_viewer->getCamera()->setGraphicsContext(m_graphicsWindow);

    // Add event handlers

    this->setMouseTracking(false);
    
    //osg::ref_ptr<osgGA::TrackballManipulator> trackballManipulator = new osgGA::TrackballManipulator;
    //trackballManipulator->setAllowThrow(false);
    //m_viewer->setCameraManipulator(trackballManipulator);

    osg::ref_ptr<MouseHandler> mouseHandler = new MouseHandler(m_viewer);
    mouseHandler->setAllowThrow(false);
    m_viewer->setCameraManipulator(mouseHandler);

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
    // Render geometries from the parsed IFC file
    // Draw the scene:
    //QOpenGLFunctions *f = QOpenGLContext::currentContext()->functions();
    //f->glClear(GL_COLOR_BUFFER_BIT); 

    //MessageLogger::log("paintGL called");

    glClear(GL_COLOR_BUFFER_BIT);
    //glClearColor(0.2f, 0.6f, 0.9f, 0.5f);

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

void IfcViewerWidget::buildSceneData()
{
    // Cube
    osg::ref_ptr<osg::Box> box = new osg::Box(osg::Vec3(0, 0, 0), 1.0f);
    osg::ref_ptr<osg::ShapeDrawable> shapeDrawable = new osg::ShapeDrawable(box);

    // Set material properties (optional)
    osg::ref_ptr<osg::Material> material = new osg::Material;
    material->setDiffuse(osg::Material::FRONT_AND_BACK, osg::Vec4(1.0f, 0.0f, 0.0f, 1.0f)); // Red color
    shapeDrawable->getOrCreateStateSet()->setAttributeAndModes(material.get());

    osg::ref_ptr<osg::Geode> geode = new osg::Geode;
    geode->addDrawable(shapeDrawable);

    // Apply a rotation to the cube to make it 3D
    osg::ref_ptr<osg::MatrixTransform> cubeTransform = new osg::MatrixTransform;
    osg::ref_ptr<osg::MatrixTransform> rotationTransform = new osg::MatrixTransform;
    rotationTransform->setMatrix(osg::Matrix::rotate(osg::DegreesToRadians(45.0), osg::Vec3(1.0, 1.0, 0.0)));
    cubeTransform->addChild(geode);
    rotationTransform->addChild(cubeTransform);

    // Translate the cube to a proper position
    osg::ref_ptr<osg::MatrixTransform> translationTransform = new osg::MatrixTransform;
    translationTransform->setMatrix(osg::Matrix::translate(osg::Vec3(0.0, 0.0, -5.0)));
    translationTransform->addChild(rotationTransform);

    // Add the cube to the root node
    root->addChild(translationTransform);
}
