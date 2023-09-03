#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QObject>
#include <QMainWindow>
#include <QString>
#include <QAction>
#include <QOpenGLWidget>
#include <QPlainTextEdit>

#include "ParseIfcFile.h"

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);

public slots:
    void openFile();

private:
    void createActions();
    void createMenus();
    void createConnections();
    void appendToOutputText(const QString& message);
private:
    QMenu *fileMenu;
    QAction *openAction;
    QAction *quitAction;

    QMenu *viewMenu;
    QAction *m_nativeAction;
    QAction *m_glAction;
    QAction *m_imageAction;
    QAction *m_highQualityAntialiasingAction;
    QAction *m_backgroundAction;
    QAction *m_outlineAction;

    QString m_currentPath;

    QOpenGLWidget *m_glWidget;
    QPlainTextEdit *m_outputText;

    ParseIfcFile m_parser;
};

#endif // MAINWINDOW_H
