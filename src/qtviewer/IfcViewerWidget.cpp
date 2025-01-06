#include "IfcViewerWidget.h"
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
#include "osg/Group"
#include "osg/StateSet"
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
    m_clearColor = osg::Vec4(0.8, 0.8, 0.8, 1.0);

    //debug - override
    //std::string filePath = "/Users/onizudb/Downloads/IFC/wallAtOrigin.ifc";
    //std::string filePath = "/Users/onizudb/Downloads/IFC/FromAC_IFC4ref.ifc";
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

    // set camera manipulator, etc.
    setupViewController();

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

void IfcViewerWidget::setupViewController()
{
    setMouseTracking(false);
    m_mouseHandler = new osgGA::TrackballManipulator;
    m_mouseHandler->setAllowThrow(false);
    m_viewer->setCameraManipulator(m_mouseHandler);
}

void IfcViewerWidget::loadFile(const std::string& filePath)
{
    std::vector<osg::ref_ptr<osg::MatrixTransform>> matrixTransforms;

    if(!m_parser.Parse(filePath, matrixTransforms)) {
        MessageLogger::log("Failed to prepare IFC geometry");
        return;
    }

    MessageLogger::log("\nIFC geometry prepared");

    for (auto matrixTransform : matrixTransforms) {
        root->addChild(matrixTransform);
    }

    // set initial camera position
    orientScene(root);

    // request redraw
    update();
}

void IfcViewerWidget::orientScene(osg::ref_ptr<osg::Group> rootGroup)
{
    // Get the bounding-box
    osg::ComputeBoundsVisitor cbv;
    rootGroup->accept(cbv);
    const osg::BoundingBox& bb = cbv.getBoundingBox();

    // Center (average of opposite corners of bb)
    osg::Vec3d center = (bb.corner(0) + bb.corner(7)) * 0.5;

    // Radius (distance between the center and the corner)
    // assuming corner(7) has maximum x,y,z coords
    float radius = (bb.corner(7) - center).length();

    // Calc. eye position
    osg::Vec3d eye = center + osg::Vec3d(radius * 3, -radius * 3, 0.0);

    osg::Vec3d up = osg::Vec3d(0.0, 0.0, 1.0);

    // Set the camera's view matrix
    // In case a cameraManipulator is set, lookAt position setting does not work on the camera
    // as it is overridden.
    // So set it on the manipulator and reapply it to the viewer
    if (m_mouseHandler.valid())
    {
      m_mouseHandler->setHomePosition(eye, center, up);
    }

    m_viewer->setCameraManipulator(m_mouseHandler);

  auto log = [center, radius, eye]() {
      MessageLogger::log("center: " + std::to_string(center.length()));
      MessageLogger::log("radius: " + std::to_string(radius));
      MessageLogger::log("center: " + std::to_string(center.x()) + ", " + std::to_string(center.y()) + ", " + std::to_string(center.z()));
      MessageLogger::log("eye: " + std::to_string(eye.x()) + ", " + std::to_string(eye.y()) + ", " + std::to_string(eye.z()));
  };
  //log();
}
