#include <QCoreApplication>
#include <QMenuBar>
#include <QMenu>
#include <QAction>
#include <QFileDialog>
#include <QFileInfo>
#include <QFile>
#include <QMessageBox>
#include <sstream>

#include "MainWindow.h"
#include "ParseIfcFile.h"
#include "IfcViewerWidget.h"

MainWindow::MainWindow(QWidget *parent) 
    : QMainWindow(parent)
{
    this->setWindowTitle("IfcOpenShell Viewer");
    this->resize(800, 600); //temporary reasonable initial size

    m_glWidget = new IfcViewerWidget(this);
    setCentralWidget(m_glWidget);

    createActions();
    createMenus();
    createConnections();
}

void MainWindow::createActions()
{
    openAction = new QAction(tr("&Open"), this);
    openAction->setShortcut(QKeySequence(tr("Ctrl+O")));

    quitAction = new QAction(tr("E&xit"), this);
    quitAction->setShortcut(QKeySequence::Quit);

    m_backgroundAction = new QAction(tr("&Background"));
    m_backgroundAction->setEnabled(false);
    m_backgroundAction->setCheckable(true);
    m_backgroundAction->setChecked(false);

    m_outlineAction = new QAction(tr("&Outline"));
    m_outlineAction->setEnabled(false);
    m_outlineAction->setCheckable(true);
    m_outlineAction->setChecked(false);
}

void MainWindow::createMenus()
{
    QMenuBar *menuBar = new QMenuBar();
    setMenuBar(menuBar);

    fileMenu = new QMenu(tr("&File"), menuBar);
    menuBar->addMenu(fileMenu);

    fileMenu->addAction(openAction);
    fileMenu->addAction(quitAction);

    viewMenu = new QMenu(tr("&View"), menuBar);
    menuBar->addMenu(viewMenu);

    viewMenu->addAction(m_backgroundAction);
    viewMenu->addAction(m_outlineAction);
}

void MainWindow::createConnections()
{
    connect(openAction, SIGNAL(triggered()), this, SLOT(openFile()));
    connect(quitAction, SIGNAL(triggered()), qApp, SLOT(quit()));
    //connect(m_backgroundAction, SIGNAL(toggled(bool)), (QWidget*)m_v, SLOT(setViewBackground(bool)));
    //connect(m_outlineAction, SIGNAL(toggled(bool)), (QWidget*)m_v, SLOT(setViewOutline(bool)));
}

void MainWindow::openFile()
{
    QString filePath = QFileDialog::getOpenFileName(this, tr("Open IFC File"), 
        ".", tr("IFC Files (*.ifc)"));

    QFileInfo fileInfo(filePath);
    QString fileName = fileInfo.fileName();

    if (fileName.isEmpty())
        return;

    // Check if the file is a Qt resource file
    if (fileName.startsWith(":/"))
        return;

    QFile file(filePath);
    if (!file.exists()) {
        QMessageBox::critical(this, tr("Open IFC"),
            QString("Could not open '%1'.").arg(filePath));

        m_outlineAction->setEnabled(false);
        m_backgroundAction->setEnabled(false);
        return;
    }

    ParseIfcFile parser;
    parser.Parse(filePath.toStdString());

    m_currentPath = filePath;
    setWindowTitle(tr("%1 - IFCViewer").arg(fileName));

    m_outlineAction->setEnabled(true);
    m_backgroundAction->setEnabled(true);
}