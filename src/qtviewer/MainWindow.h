#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QObject>
#include <QMainWindow>
#include <QString>
#include <QAction>
#include <QOpenGLWidget>
#include <QPlainTextEdit>
#include <string>

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(qreal dpiScale, QWidget *parent = nullptr);

signals:
    void loadFileInViewerWidget(const std::string& filePath);

public slots:
    void openFile();
    void appendToOutputText(const QString& message);

private:
    void createActions();
    void createMenus();
    void createConnections();
private:
    qreal m_dpiScale;

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

    QOpenGLWidget *m_glWidget;
    QPlainTextEdit *m_outputText;
};

#endif // MAINWINDOW_H
