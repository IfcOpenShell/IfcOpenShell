
#include <QApplication>
#include <QString>
#ifndef QT_NO_OPENGL
#include <QGLFormat>
#endif

#include "mainwindow.h"

int main(int argc, char **argv)
{
    QApplication app(argc, argv);

	//QGLViewer viewer;

   // Restore the previous viewer state.
   //viewer.restoreStateFromFile();

    MainWindow window;
    //window.openFile("	");

  window.show();

  return app.exec();
}
