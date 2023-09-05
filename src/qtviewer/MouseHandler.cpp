#include "MouseHandler.h"
#include <osgGA/CameraManipulator>
#include "MessageLogger.h"

MouseHandler::MouseHandler(osgViewer::Viewer* viewer) :
    osgGA::TrackballManipulator(),
    viewer(viewer)
{
    MessageLogger::log("MouseHandler constructed");
}

bool MouseHandler::handle (
    const osgGA::GUIEventAdapter& ea,
    const osgGA::GUIActionAdapter& aa)
{
    MessageLogger::log("MouseHandler::handle() called");
    switch (ea.getEventType()) {
        case (osgGA::GUIEventAdapter::DRAG):
        {
            if (ea.getButton() == osgGA::GUIEventAdapter::RIGHT_MOUSE_BUTTON)
            { // pan view
                // Calculate the delta movement
                float deltaX = ea.getX() - _ga_t0->getXnormalized();
                float deltaY = ea.getY() - _ga_t1->getYnormalized();

                // Implement panning logic
                osg::Vec3d eye, center, up;
                getInverseMatrix().getLookAt(eye, center, up);
                osg::Vec3d right = (eye - center) ^ up;
                osg::Matrixd rotationMatrix = osg::Matrix::rotate(-deltaX * 0.1, up) * osg::Matrix::rotate(deltaY * 0.1, right);

                osg::Matrixd newMatrix = getMatrix() * rotationMatrix;
                setByMatrix(newMatrix);

                return true; // Event handled
            }
            if (ea.getButton() == osgGA::GUIEventAdapter::LEFT_MOUSE_BUTTON)
            {
                return false;
            }
            // If not a right mouse button drag, let the base class handle it
            //return osgGA::TrackballManipulator::handle(ea, aa);
        }
        default:
            return false;
    }
}
