#include "MainWindow.h"

#include <QApplication>

int main(int argc, char *argv[])
{
  QApplication app(argc, argv);

  QIcon appIcon(":/resources/ifcopenshell_logo.png");

  MainWindow window;

  window.setWindowIcon(appIcon);
  window.show();

  return app.exec();
}
