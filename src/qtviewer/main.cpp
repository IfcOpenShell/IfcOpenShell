#include "MainWindow.h"

#include <QApplication>

int main(int argc, char *argv[])
{
  QApplication app(argc, argv);

  // Set the icon in the window title-bar on mswindows
  // and dock icon on macos.
  // "icon" alias defined in .qrc file
  QIcon appIcon(":/icon");
  app.setWindowIcon(appIcon);
  // File icon set with:
  // mswindows - .rc file
  // macos - .icns file (using CMake)

  qreal dpiScale = app.devicePixelRatio();

  MainWindow window(dpiScale);

  window.show();

  return app.exec();
}
