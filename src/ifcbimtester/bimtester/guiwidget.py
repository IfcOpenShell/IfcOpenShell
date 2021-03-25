import os
import sys
import bimtester.run
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets


def run():
    app = QtWidgets.QApplication(sys.argv)
    form = GuiWidgetBimTester()
    form.show()
    sys.exit(app.exec_())


class GuiWidgetBimTester(QtWidgets.QWidget):
    def __init__(self, args=[]):
        super(GuiWidgetBimTester, self).__init__()
        self.args = args

        self._setup_ui()

    # http://forum.freecadweb.org/viewtopic.php?f=18&t=10732&start=10#p86493
    def __del__(self):
        return

    def _setup_ui(self):
        package_path = os.path.dirname(os.path.realpath(__file__))
        iconpath = os.path.join(package_path, "resources", "icons", "bimtester.ico")

        """
        # as svg
        # https://stackoverflow.com/a/35138314
        theicon = QtSvg.QSvgWidget(iconpath)
        # none works ...
        #theicon.setGeometry(20,20,200,200)
        #theicon.setSizePolicy(
        #    QtGui.QSizePolicy.Policy.Maximum,
        #    QtGui.QSizePolicy.Policy.Maximum
        #)
        #theicon.sizeHint()
        """

        # as pixmap
        theicon = QtWidgets.QLabel(self)
        iconpixmap = QtGui.QPixmap(iconpath)
        iconpixmap = iconpixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio)
        theicon.setPixmap(iconpixmap)

        # ifc file
        _ifcfile_label = QtWidgets.QLabel("IFC file", self)
        self.ifcfile_text = QtWidgets.QLineEdit()
        _ifcfile_browse_btn = QtWidgets.QToolButton()
        _ifcfile_browse_btn.setText("...")
        _ifcfile_browse_btn.clicked.connect(self.select_ifcfile)

        # feature files path
        # use a layout with a frame and a title, see solver framework tp
        # beside button
        ffifc_str = "Feature files in a directory 'features' beside the IFC file."
        featuredirfromifc_label = QtWidgets.QLabel(ffifc_str, self)

        # path browser and line edit
        _ffdir_str = "Feature files directory. " "'features' directory has to be in there."
        _featurefilesdir_label = QtWidgets.QLabel(_ffdir_str, self)
        self.featurefilesdir_text = QtWidgets.QLineEdit()
        self.feafilesdir_browse_btn = QtWidgets.QToolButton()
        self.feafilesdir_browse_btn.setText("...")
        self.feafilesdir_browse_btn.clicked.connect(self.select_featurefilesdir)

        # buttons
        self.run_button = QtWidgets.QPushButton(QtGui.QIcon.fromTheme("document-new"), "Run")
        self.close_button = QtWidgets.QPushButton(QtGui.QIcon.fromTheme("window-close"), "Close")
        self.run_button.clicked.connect(self.run_bimtester)
        self.close_button.clicked.connect(self.close_widget)
        _buttons = QtWidgets.QHBoxLayout()
        _buttons.addWidget(self.run_button)
        _buttons.addWidget(self.close_button)

        # Layout:
        layout = QtWidgets.QGridLayout()
        layout.addWidget(theicon, 1, 0, alignment=QtCore.Qt.AlignRight)

        layout.addWidget(featuredirfromifc_label, 2, 0)

        layout.addWidget(_featurefilesdir_label, 3, 0)
        layout.addWidget(self.featurefilesdir_text, 4, 0)
        layout.addWidget(self.feafilesdir_browse_btn, 4, 1)

        layout.addWidget(_ifcfile_label, 5, 0)
        layout.addWidget(self.ifcfile_text, 6, 0)
        layout.addWidget(_ifcfile_browse_btn, 6, 1)

        layout.addLayout(_buttons, 7, 0)
        # row stretches by 10 compared to the others, std is 0
        # first parameter is the row number
        # second is the stretch factor.
        layout.setRowStretch(0, 10)
        self.setLayout(layout)

    def select_ifcfile(self):
        ifcfile = QtWidgets.QFileDialog.getOpenFileName(self, dir=self.get_ifcfile())[0]
        self.set_ifcfile(ifcfile)

    def set_ifcfile(self, a_file):
        self.ifcfile_text.setText(a_file)

    def get_ifcfile(self):
        return self.ifcfile_text.text()

    def select_featurefilesdir(self):
        thedir = self.featurefilesdir_text.text()
        features_path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            caption="Choose features directory ...",
            dir=thedir,
            options=QtWidgets.QFileDialog.HideNameFilterDetails,
        )
        self.set_featurefilesdir(features_path)

    def set_featurefilesdir(self, a_directory):
        self.featurefilesdir_text.setText(a_directory)

    def get_featurefilesdir(self):
        return self.featurefilesdir_text.text()

    def run_bimtester(self):
        print("Run BIMTester by the GUI")
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        the_features_path = self.get_featurefilesdir()
        print(the_features_path)

        # get ifc file
        the_ifcfile = self.get_ifcfile()
        print(the_ifcfile)

        # overwrite the_features_path and ifcfile in args
        patched_args = self.args
        patched_args["featuresdir"] = the_features_path
        patched_args["ifcfile"] = the_ifcfile

        bimtester.run.TestRunner("file.ifc").run({})

        QtWidgets.QApplication.restoreOverrideCursor()

    def close_widget(self):
        self.close()

    def closeEvent(self, ev):
        pw = self.parentWidget()
        if pw and pw.inherits("QDockWidget"):
            pw.deleteLater()
