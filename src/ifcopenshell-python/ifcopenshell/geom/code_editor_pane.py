import os
import sys
import logging
from pyqode.core.panels import CheckerPanel

logging.basicConfig(level=logging.CRITICAL)
from pyqode.qt import QtCore, QtGui, QtWidgets
print('Qt version:%s' % QtCore.__version__)
from code import InteractiveConsole
from pyqode.core import api
from pyqode.core import modes
from pyqode.core import panels
from pyqode.core.api import CodeEdit, ColorScheme
from pyqode.python.modes import PyAutoIndentMode, PythonSH
from pyqode.python.backend import server
from pyqode.python import modes as pymodes, panels as pypanels, widgets
from pyqode.python.widgets import PyInteractiveConsole



class StdoutRedirector(QtGui.QTextEdit):
    '''A class for redirecting stdout to this Text widget.'''
    def __init__(self, widget):
       self.widget=widget
       self.isError = False
    def write(self,str):
        # print(str)
        # self.widget.append(str)
        self.widget.moveCursor(QtGui.QTextCursor.End)
        if self.isError:
            self.widget.setTextColor(QtCore.Qt.red)
        else:
            self.widget.setTextColor(QtCore.Qt.black)
        self.widget.insertPlainText(str)
        self.widget.moveCursor(QtGui.QTextCursor.End)
        # scroll = self.widget.verticalScrollBar()
        # scroll.setValue(scroll.maximum())


class code_edit(QtGui.QWidget):
    class  Console(InteractiveConsole):

        def __init__(*args): InteractiveConsole.__init__(*args)

        def enter(self, source):
            source = self.preprocess(source)
            self.runcode(source)

        @staticmethod
        def preprocess(source): return source
        def runCode(self):
            c =self.Console({'model':self.files[0]})
            c.enter("print (model.by_type('IfcDoor')")

    def runCode(self):

        sys.stdout = StdoutRedirector(self.output)
        err_redirect= StdoutRedirector(self.output)
        err_redirect.isError=True
        sys.stderr = err_redirect

        if not self.model:
            print("please load a model first")
        if not self.c:
            self.c = self.Console({'model':self.model, 'viewer':self.viewer})
        else:
            # self.console.start_process(sys.executable,args= [ os.path.join(os.getcwd(), 'interactive_process.py')],env={'model':self.model})
            self.c.enter(str(self.editor.toPlainText()))
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def select(self,product):
        self.c = self.Console({'model':self.model, 'viewer':self.viewer, 'selection':product})
        self.c.enter

    def __init__(self,viewer,snippets=None):

        logging.basicConfig(level=logging.CRITICAL)
        self.model=None
        self.viewer = viewer
        QtGui.QWidget.__init__(self)
        self.layout= QtGui.QVBoxLayout(self)
        self.setLayout(self.layout)
        self.c = None


        editor = CodeEdit()

        # start the backend as soon as possible
        # editor.backend.start('server.py')
        editor.backend.start(server.__file__)
        #--- core panels
        editor.panels.append(panels.FoldingPanel())
        editor.panels.append(panels.LineNumberPanel())
        # editor.panels.append(panels.CheckerPanel())
        editor.panels.append(panels.SearchAndReplacePanel(),
                           panels.SearchAndReplacePanel.Position.BOTTOM)
        editor.panels.append(panels.EncodingPanel(), api.Panel.Position.TOP)
        # add a context menu separator between editor's
        # builtin action and the python specific actions
        editor.add_separator()

        #--- python specific panels
        editor.panels.append(pypanels.QuickDocPanel(), api.Panel.Position.BOTTOM)
        sh = editor.modes.append(PythonSH(editor.document()))
        # sh.color_scheme = ColorScheme('monokai')
        #--- core modes
        editor.modes.append(modes.CaretLineHighlighterMode())
        editor.modes.append(modes.CodeCompletionMode())
        editor.modes.append(modes.ExtendedSelectionMode())
        editor.modes.append(modes.FileWatcherMode())
        editor.modes.append(modes.OccurrencesHighlighterMode())
        editor.modes.append(modes.RightMarginMode())
        editor.modes.append(modes.SmartBackSpaceMode())
        editor.modes.append(modes.SymbolMatcherMode())
        editor.modes.append(modes.ZoomMode())

        #---  python specific modes
        editor.modes.append(pymodes.CommentsMode())
        editor.modes.append(pymodes.CalltipsMode())
        auto = pymodes.PyAutoCompleteMode()
        auto.logger.setLevel(logging.CRITICAL)
        editor.modes.append(auto)
        editor.modes.append(pymodes.PyAutoIndentMode())
        editor.modes.append(pymodes.PyIndenterMode())
        editor.show()


        self.editor = editor
        self.snippets = snippets
        if not self.snippets:
            self.editor.setPlainText("""print('hello from console')
for w in model.by_type('IfcWall'):
    print ("wall with GlobalId " + str(w.GlobalId))
        ""","","")
        else:
            self.editor.setPlainText(self.snippets.values()[0],"","")
            self.list = QtWidgets.QComboBox(self)
            for snip_name in self.snippets.keys():
                self.list.addItem(snip_name)
            self.layout.addWidget(self.list)
            QtCore.QObject.connect(self.list, QtCore.SIGNAL("currentIndexChanged(int)"), self.replace_snippet)
        # self.textedit = QtGui.QTextEdit()
        # self.scrollLayout.addWidget(self.textedit)

        self.layout.addWidget(self.editor)

        self.output = QtGui.QTextEdit()
        self.output.setReadOnly(False)
        self.output.setStyleSheet('font-size: 10pt; font-family: Consolas,Courier;')
        self.layout.addWidget(self.output)

    def replace_snippet (self,number):
        self.editor.setPlainText(self.snippets[self.list.currentText()],"","")

    def load_file(self, f, **kwargs):
        output = []
        sys.stdout = StdoutRedirector(self.output)
        self.model = f
        self.c = self.Console({'model':self.model})
        # c.enter("print (model.by_type('IfcWall'))")
        sys.stdout = sys.__stdout__