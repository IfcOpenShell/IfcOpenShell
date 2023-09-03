#ifndef IFCVIEWERWIDGET_H
#define IFCVIEWERWIDGET_H

#include <QOpenGLWidget>
#include <QOpenGLFunctions>
#include <QOpenGLContext>
#include <QMatrix4x4>

class IfcViewerWidget : public QOpenGLWidget
{
public:
    IfcViewerWidget(QWidget *parent = nullptr);

protected:
    void initializeGL() override; 
    void resizeGL(int w, int h) override;
    void paintGL() override;

private:
    QMatrix4x4 m_projection;
};

#endif // IFCVIEWERWIDGET_H