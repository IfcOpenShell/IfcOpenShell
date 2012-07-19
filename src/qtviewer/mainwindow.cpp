

#include "mainwindow.h"
#include <math.h>

#include <QtGui>

MainWindow::MainWindow()
    : QMainWindow()
{


	IfcGeomObjects::Settings(IfcGeomObjects::USE_WORLD_COORDS,true);
	IfcGeomObjects::Settings(IfcGeomObjects::WELD_VERTICES,false);
    IfcGeomObjects::Settings(IfcGeomObjects::SEW_SHELLS,true);



    QMenu *fileMenu = new QMenu(tr("&File"), this);
    QAction *openAction = fileMenu->addAction(tr("&Open..."));
    openAction->setShortcut(QKeySequence(tr("Ctrl+O")));
    QAction *quitAction = fileMenu->addAction(tr("E&xit"));
    quitAction->setShortcuts(QKeySequence::Quit);

    menuBar()->addMenu(fileMenu);

    QMenu *viewMenu = new QMenu(tr("&View"), this);
    m_backgroundAction = viewMenu->addAction(tr("&Background"));
    m_backgroundAction->setEnabled(false);
    m_backgroundAction->setCheckable(true);
    m_backgroundAction->setChecked(false);
    //connect(m_backgroundAction, SIGNAL(toggled(bool)), (QWidget*)m_v, SLOT(setViewBackground(bool)));

    m_outlineAction = viewMenu->addAction(tr("&Outline"));
    m_outlineAction->setEnabled(false);
    m_outlineAction->setCheckable(true);
    m_outlineAction->setChecked(true);
   // connect(m_outlineAction, SIGNAL(toggled(bool)), (QWidget*)m_v, SLOT(setViewOutline(bool)));

    menuBar()->addMenu(viewMenu);

    connect(openAction, SIGNAL(triggered()), this, SLOT(openFile()));
    connect(quitAction, SIGNAL(triggered()), qApp, SLOT(quit()));

    //setCentralWidget((QWidget*)m_v);
    setWindowTitle(tr("IfcOpenShell QT Viewer"));
}

void MainWindow::openFile(const QString &path)
{
    QString fileName;
    if (path.isNull())
        fileName = QFileDialog::getOpenFileName(this, tr("Open IFC"),
                m_currentPath, "IFC files (*.ifc)");
    else
        fileName = path;

    if (!fileName.isEmpty()) {
        QFile file(fileName);
        if (!file.exists()) {
            QMessageBox::critical(this, tr("Open IFC"),
                           QString("Could not open file '%1'.").arg(fileName));

            m_outlineAction->setEnabled(false);
            m_backgroundAction->setEnabled(false);
            return;
        }
		std::stringstream ss;
    	if ( ! IfcGeomObjects::Init(fileName.toStdString(),&std::cout,&ss) ) {
    			QMessageBox::critical(this, tr("Open IFC"),
    			                           QString("[Error] unable to parse file '%1'. Or no geometrical entities found" ).arg(fileName));
    			return;
    	}

    	//connect((QWidget*)m_view, SIGNAL(drawNeeded()), this, SLOT(drawIfcObject()));

        if (!fileName.startsWith(":/")) {
            m_currentPath = fileName;
            setWindowTitle(tr("%1 - IFCViewer").arg(m_currentPath));
        }

        m_outlineAction->setEnabled(true);
        m_backgroundAction->setEnabled(true);

//        resize(m_view->sizeHint() + QSize(80, 80 + menuBar()->height()));
    }
}


void MainWindow::draw()
{



}


