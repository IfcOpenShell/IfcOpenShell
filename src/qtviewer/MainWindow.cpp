#include <QCoreApplication>
#include <QMenuBar>
#include <QMenu>
#include <QAction>
#include <QFileDialog>
#include <QFileInfo>
#include <QFile>
#include <QMessageBox>
#include <QSplitter>
#include <sstream>

#include "MainWindow.h"
#include "MessageLogger.h"
#include "IfcViewerWidget.h"

MainWindow::MainWindow(qreal dpiScale, QWidget *parent) 
    : QMainWindow(parent), m_dpiScale(dpiScale)
{
    this->setWindowTitle("IfcOpenShell Viewer");
    this->resize(800, 600); //temporary reasonable initial size

    m_glWidget = new IfcViewerWidget(m_dpiScale, this);
    QSizePolicy glSizePolicy = m_glWidget->sizePolicy();
    glSizePolicy.setVerticalStretch(3);
    m_glWidget->setSizePolicy(glSizePolicy);

    m_outputText = new QPlainTextEdit(this);
    m_outputText->setReadOnly(true);

    QSplitter* splitter = new QSplitter(Qt::Vertical, this);
    splitter->addWidget(m_glWidget);
    splitter->addWidget(m_outputText);

    setCentralWidget(splitter);

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

    //connect(&m_parser, &ParseIfcFile::parsingInfo, this, &MainWindow::appendToOutputText);
    connect(&MessageLogger::getInstance(), SIGNAL(logMessage(QString)), this, SLOT(appendToOutputText(QString)));

    connect(this, SIGNAL(loadFileInViewerWidget(const std::string&)), m_glWidget, SLOT(loadFile(const std::string&)));
}

void MainWindow::appendToOutputText(const QString& message)
{
    m_outputText->appendPlainText(message);
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

    QString message = tr("Opening file: %1\n").arg(filePath);
    appendToOutputText(message);

    setWindowTitle(tr("%1 - IFCViewer").arg(fileName));

    m_outlineAction->setEnabled(true);
    m_backgroundAction->setEnabled(true);

    emit loadFileInViewerWidget(filePath.toStdString());
}
