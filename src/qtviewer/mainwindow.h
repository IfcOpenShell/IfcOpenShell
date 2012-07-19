

#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <qobject.h>
#include <QMainWindow>
#include <QString>
#include "../ifcgeom/IfcGeomObjects.h"

class ObjectsView;

class QGLViewer;

QT_BEGIN_NAMESPACE
class QAction;
class QGraphicsView;
class QGraphicsScene;
class QGraphicsRectItem;
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow();


public Q_SLOTS:
  void draw();

public slots:
    void openFile(const QString &path = QString());

private:
    QAction *m_nativeAction;
    QAction *m_glAction;
    QAction *m_imageAction;
    QAction *m_highQualityAntialiasingAction;
    QAction *m_backgroundAction;
    QAction *m_outlineAction;

    QString m_currentPath;
};

#endif
