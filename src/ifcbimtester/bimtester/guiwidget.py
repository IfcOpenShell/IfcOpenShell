# TODO: all args should be passed to the gui,
# either pass them further to behave or make it possible to edit them before
# TODO: if browse widgets will be canceled, last QLineEdit should be restored
# TODO: keep path or file if in browse widget canceled
# TODO: make a frame around features direcory chooser and
# use features path from ifc button

import os

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from .run import run_all


class GuiWidgetBimTester(QtWidgets.QWidget):

    def __init__(
        self,
        featurespath="",
        ifcfile="",
        get_featurepath_from_ifcpath=False,
        args=[]
    ):
        super(GuiWidgetBimTester, self).__init__()

        user_path = os.path.expanduser("~")

        # get features dir
        # print(featurespath)
        if not os.path.isdir(featurespath):
            featurespath = user_path

        # get ifc file
        # print(ifcfile)
        if not os.path.isfile(ifcfile):
            ifcfile = user_path

        self.initial_featurespath = featurespath
        self.initial_ifcfile = ifcfile
        self.get_featurepath_from_ifcpath = get_featurepath_from_ifcpath
        self.args = args
        # print(self.initial_featurespath)
        # print(self.initial_ifcfile)
        # print(self.get_featurepath_from_ifcpath)

        # init ui
        self._setup_ui()

    def __del__(self,):
        # need as fix for qt event error
        # http://forum.freecadweb.org/viewtopic.php?f=18&t=10732&start=10#p86493
        return

    def _setup_ui(self):

        # a lot code is taken from FreeCAD FEM solver frame work task panel
        # https://forum.freecadweb.org/viewtopic.php?f=10&t=51419
        # use a browse button, and a line edit
        # the browse button opens a file dialog, which will set the line edit

        # icon
        # print(__file__)
        package_path = os.path.dirname(os.path.realpath(__file__))
        iconpath = os.path.join(
            package_path, "resources", "icons", "bimtester.ico"
        )
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
        self.set_ifcfile(self.initial_ifcfile)
        _ifcfile_browse_btn = QtWidgets.QToolButton()
        _ifcfile_browse_btn.setText("...")
        _ifcfile_browse_btn.clicked.connect(self.select_ifcfile)

        # feature files path
        # use a layout with a frame and a title, see solver framework tp
        # beside button
        ffifc_str = (
            "Feature files in a directory 'features' beside the IFC file."
        )
        featuredirfromifc_label = QtWidgets.QLabel(ffifc_str, self)
        self.featuredirfromifc_cb = QtWidgets.QCheckBox(self)
        self.featuredirfromifc_cb.stateChanged.connect(
            self.featuredirfromifc_clicked
        )

        # path browser and line edit
        _ffdir_str = (
            "Feature files directory. "
            "'features' directory has to be in there."
        )
        _featurefilesdir_label = QtWidgets.QLabel(_ffdir_str, self)
        self.featurefilesdir_text = QtWidgets.QLineEdit()
        self.set_featurefilesdir(self.initial_featurespath)
        self.feafilesdir_browse_btn = QtWidgets.QToolButton()
        self.feafilesdir_browse_btn.setText("...")
        self.feafilesdir_browse_btn.clicked.connect(
            self.select_featurefilesdir
        )

        # buttons
        self.run_button = QtWidgets.QPushButton(
            QtGui.QIcon.fromTheme("document-new"), "Run"
        )
        self.close_button = QtWidgets.QPushButton(
            QtGui.QIcon.fromTheme("window-close"), "Close"
        )
        self.run_button.clicked.connect(self.run_bimtester)
        self.close_button.clicked.connect(self.close_widget)
        _buttons = QtWidgets.QHBoxLayout()
        _buttons.addWidget(self.run_button)
        _buttons.addWidget(self.close_button)

        # Layout:
        layout = QtWidgets.QGridLayout()
        layout.addWidget(theicon, 1, 0, alignment=QtCore.Qt.AlignRight)

        layout.addWidget(featuredirfromifc_label, 2, 0)
        layout.addWidget(self.featuredirfromifc_cb, 2, 1)

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

        # set button state, needs to be here after gui has beed set up
        self.featuredirfromifc_cb.setChecked(self.get_featurepath_from_ifcpath)

    # **********************************************************
    def select_ifcfile(self):
        # print(self.get_ifcfile())
        # print(os.path.isfile(self.get_ifcfile()))
        ifcfile = QtWidgets.QFileDialog.getOpenFileName(
            self,
            dir=self.get_ifcfile()
        )[0]
        self.set_ifcfile(ifcfile)

    def set_ifcfile(self, a_file):
        self.ifcfile_text.setText(a_file)

    def get_ifcfile(self):
        return self.ifcfile_text.text()

    def featuredirfromifc_clicked(self):
        if self.featuredirfromifc_cb.isChecked() is True:
            self.set_featurefilesdir("")
            self.featurefilesdir_text.setEnabled(False)
            self.feafilesdir_browse_btn.setEnabled(False)
        else:
            self.set_featurefilesdir(self.initial_featurespath)
            self.featurefilesdir_text.setEnabled(True)
            self.feafilesdir_browse_btn.setEnabled(True)

    def select_featurefilesdir(self):
        thedir = self.featurefilesdir_text.text()
        # print(thedir)
        # print(os.path.isdir(thedir))
        # hidden directories are only shown if the option is set
        features_path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            caption="Choose features directory ...",
            dir=thedir,
            options=QtWidgets.QFileDialog.HideNameFilterDetails
        )
        self.set_featurefilesdir(features_path)

    def set_featurefilesdir(self, a_directory):
        self.featurefilesdir_text.setText(a_directory)

    def get_featurefilesdir(self):
        return self.featurefilesdir_text.text()

    # **********************************************************
    def run_bimtester(self):
        print("Run BIMTester by the GUI")
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        # get features dir
        if self.featuredirfromifc_cb.isChecked() is True:
            ifcfile = self.get_ifcfile()
            print(
                "Make sure the feature files are beside "
                "the ifc file in a directory named 'features'."
            )
            if ifcfile == "":
                # os.path.realpath("") would return the cmd dir and not ""
                print(
                    "No ifcfile given, "
                    "thus features files path will be set to ''."
                )
                the_features_path = ""
            elif os.path.isfile(ifcfile) is not True:
                # if ifcfile does not exist set features path to ""
                print(
                    "The ifcfile does not exist, "
                    "thus features files path will be set to ''."
                )
                the_features_path = ""
            else:
                ifcfilepath = os.path.dirname(os.path.realpath(ifcfile))
                if os.path.isdir(ifcfilepath):
                    the_features_path = ifcfilepath
                else:
                    print(
                        "ifcfilepath does not exist, "
                        "thus features files path will be set to ''."
                        "this shold never happen, please debug. "
                    )
                    the_features_path = ""

        else:
            the_features_path = self.get_featurefilesdir()
        print(the_features_path)

        # get ifc file
        the_ifcfile = self.get_ifcfile()
        print(the_ifcfile)

        # overwrite the_features_path and ifcfile in args
        patched_args = self.args
        patched_args["featuresdir"] = the_features_path
        patched_args["ifcfile"] = the_ifcfile

        # run bimtester
        status = run_all(patched_args)
        print(status)

        QtWidgets.QApplication.restoreOverrideCursor()

    def close_widget(self):
        print("Close BIMTester Gui")
        self.close()

    def closeEvent(self, ev):
        pw = self.parentWidget()
        if pw and pw.inherits("QDockWidget"):
            pw.deleteLater()
