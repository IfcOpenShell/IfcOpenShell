#include "MainWindow.h"

#include <QApplication>

int main(int argc, char *argv[])
{
  QApplication app(argc, argv);

  // Set the icon in the window title-bar
  // "icon" alias defined in .qrc file
  // (.rc file sets the file icon on mswindows)
  QIcon appIcon(":/icon");
  app.setWindowIcon(appIcon);

  MainWindow window;

  window.show();

  return app.exec();
}
