#ifndef MOUSEHANDLER_H
#define MOUSEHANDLER_H

#include <osgViewer/Viewer>
#include <osgGA/TrackballManipulator>

class MouseHandler : public osgGA::TrackballManipulator
{
    public:
        MouseHandler(osgViewer::Viewer* viewer);

        using osgGA::GUIEventHandler::handle;
        virtual bool handle(
            const osgGA::GUIEventAdapter& ea,
            const osgGA::GUIActionAdapter& aa
        ); 
    private:
        osgViewer::Viewer* viewer;
};

#endif // MOUSEHANDLER_H
