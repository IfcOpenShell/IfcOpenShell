from __future__ import print_function

import os
import sys
import logging

from code import InteractiveConsole
from PyQt4 import QtCore, QtGui

try:
    from PyQt4 import QtWidgets
except:
    QtWidgets = QtGui

try:
    from pyqode.core.panels import CheckerPanel
    from pyqode.core import api
    from pyqode.core import modes
    from pyqode.core import panels
    from pyqode.core.api import CodeEdit, ColorScheme
    from pyqode.python.modes import PyAutoIndentMode, PythonSH
    from pyqode.python.backend import server
    from pyqode.python import modes as pymodes, panels as pypanels, widgets
    from pyqode.python.widgets import PyInteractiveConsole
    has_pyqode = True
except:
    has_pyqode = False
    CodeEdit = QtWidgets.QPlainTextEdit
    
    
class StdoutRedirector(object):

    '''A class for redirecting stdout to this Text widget.'''

    def __init__(self, widget):
       self.widget=widget
       self.isError = False

    def write(self,str):
        self.widget.moveCursor(QtGui.QTextCursor.End)
        if self.isError:
            self.widget.setTextColor(QtCore.Qt.red)
        else:
            self.widget.setTextColor(QtCore.Qt.white)
        self.widget.insertPlainText(str)
        self.widget.moveCursor(QtGui.QTextCursor.End)


class code_edit(QtGui.QWidget):

    class Console(InteractiveConsole):
        def __init__(*args):
            InteractiveConsole.__init__(*args)

        def enter(self, source):
            self.runcode(source)

    def runCode(self):
        sys.stdout = StdoutRedirector(self.output)
        sys.stderr = StdoutRedirector(self.output)
        sys.stderr.isError=True

        if not self.model:
            print("please load a model first", file=sys.stderr)
        else:
            self.c.enter(str(self.editor.toPlainText()))
            
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def select(self,product):
        self.c = self.Console({'model':self.model, 'viewer':self.viewer, 'selection':product})

    def __init__(self,viewer,snippets=None):
    
        self.model=None
        self.viewer = viewer
        QtGui.QWidget.__init__(self)
        self.layout= QtGui.QVBoxLayout(self)
        self.setLayout(self.layout)
        self.c = None
        
        self.tools = QtGui.QHBoxLayout(self)
        self.layout.addLayout(self.tools)
        
        self.runbutton = QtGui.QPushButton("Run")
        width = self.runbutton.fontMetrics().boundingRect("Run").width() + 20
        self.runbutton.setMaximumWidth(width)
        self.tools.addWidget(self.runbutton)
        self.runbutton.clicked.connect(self.runCode)
        
        editor = CodeEdit()
        if has_pyqode:
            editor.backend.start(server.__file__)
            editor.panels.append(panels.FoldingPanel())
            editor.panels.append(panels.LineNumberPanel())
            editor.panels.append(panels.SearchAndReplacePanel(),
                                 panels.SearchAndReplacePanel.Position.BOTTOM)
            editor.panels.append(panels.EncodingPanel(), api.Panel.Position.TOP)
            editor.add_separator()
            editor.panels.append(pypanels.QuickDocPanel(), api.Panel.Position.BOTTOM)
            sh = editor.modes.append(PythonSH(editor.document()))
            editor.modes.append(modes.CaretLineHighlighterMode())
            editor.modes.append(modes.CodeCompletionMode())
            editor.modes.append(modes.ExtendedSelectionMode())
            editor.modes.append(modes.FileWatcherMode())
            editor.modes.append(modes.OccurrencesHighlighterMode())
            editor.modes.append(modes.RightMarginMode())
            editor.modes.append(modes.SmartBackSpaceMode())
            editor.modes.append(modes.SymbolMatcherMode())
            editor.modes.append(modes.ZoomMode())
            editor.modes.append(pymodes.CommentsMode())
            editor.modes.append(pymodes.CalltipsMode())
            auto = pymodes.PyAutoCompleteMode()
            auto.logger.setLevel(logging.CRITICAL)
            editor.modes.append(auto)
            editor.modes.append(pymodes.PyAutoIndentMode())
            editor.modes.append(pymodes.PyIndenterMode())
            editor.show()
        else:
            editor.setStyleSheet('font-size: 10pt; font-family: Consolas, Courier;')

        self.editor = editor
        self.snippets = snippets
        if self.snippets:
            self.list = QtWidgets.QComboBox(self)
            self.replace_snippet(0)
            for snip_name in self.snippets.keys():
                self.list.addItem(snip_name)
            self.tools.addWidget(self.list)
            QtCore.QObject.connect(self.list, QtCore.SIGNAL("currentIndexChanged(int)"), self.replace_snippet)

        self.layout.addWidget(self.editor)

        self.output = QtGui.QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet('font-size: 10pt; font-family: Consolas, Courier; background-color: #444;')
        self.layout.addWidget(self.output)

    def replace_snippet(self, number=None):
        snip = list(self.snippets.values())[number]
        if has_pyqode:
            self.editor.setPlainText(snip, "", "")
        else:
            self.editor.setPlainText(snip)

    def load_file(self, f, **kwargs):
        output = []
        sys.stdout = StdoutRedirector(self.output)
        self.model = f
        self.c = self.Console({'model':self.model, 'selection':None, 'viewer':self.viewer})
        sys.stdout = sys.__stdout__
