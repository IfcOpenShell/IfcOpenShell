from pyqode.qt import QtCore, QtGui, QtWidgets
from configobj import ConfigObj

from ..geom.app import  application
try:
    from ..geom.code_editor_pane import code_edit
except ImportError:
    print ("code editor or one of its dependencies (pyQode) could not be found. Please make sure to install pyQode")
class my_app(application):

    class toolbar(QtGui.QToolBar):
        def __init__(self):
            QtGui.QToolBar.__init__(self)
            self.widget.append()

    def __init__(self):
        application.__init__(self)
       # self.window = my_app.window()
        self.window.setWindowTitle("Interactive IfcOpenShell Viewer with REPL-like funcionality")
        tb = self.window.addToolBar("File")
        self.window.resize(1024,720)
        # loadButton = QtGui.QAction(QtGui.QIcon("new.bmp"),"new",self)
        loadButton = QtGui.QAction("Quickload",self)
        loadButton.triggered.connect(self.loadExampleFile)
        loadButton.setShortcut(QtGui.QKeySequence("CTRL+L"))
        tb.addAction(loadButton)
        # zoomAllButton = QtGui.QAction(QtGui.QIcon("new.bmp"),"new",self)
        zoomAllButton = QtGui.QAction("zoom All",self)
        zoomAllButton.triggered.connect(self.zoomAll)
        tb.addAction(zoomAllButton)
        self.config = ConfigObj("snippets.config")
        print (self.config["snippets"])

        snippets = self.config["snippets"]

        self.codeedit= code_edit(self.canvas, snippets )

        self.components.append(self.codeedit)
        self.window.centralWidget().addWidget(self.codeedit)
        self.runButton = QtGui.QAction("execute code (Strg+P)",self)
        self.runButton.setShortcut(QtGui.QKeySequence("CTRL+P"))
        self.runButton.triggered.connect(self.codeedit.runCode)

        tb.addAction(self.runButton)
    def loadExampleFile(self):
        self.load(self.config["quickload_model"])
    def zoomAll(self):
        self.canvas._display.FitAll()


my_app().start()