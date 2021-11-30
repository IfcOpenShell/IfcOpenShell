import os
import json
import sys
import webbrowser

import bimtester.reports
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
    def __init__(self, args=None):
        super(GuiWidgetBimTester, self).__init__()

        if args is not None and args != {}:
            self.args = args
        else:
            self.args = {
                "action": "",
                "advanced_arguments": "",
                "console": False,  # has to be False to get a report file
                "feature": "",
                "ifc": "",
                "path": "",
                "report": "",
                "steps": "",
                "schema_file": "",
                "schema_name": "",
                "lang": "",
            }

        self._setup_ui()

    # http://forum.freecadweb.org/viewtopic.php?f=18&t=10732&start=10#p86493
    def __del__(self):
        return

    def _setup_ui(self):
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

        # feature file
        _featurefile_label = QtWidgets.QLabel("Feature file", self)
        self.featurefile_text = QtWidgets.QLineEdit()
        self.featurefile_text.setText(self.args["feature"])
        _featurefile_browse_btn = QtWidgets.QToolButton()
        _featurefile_browse_btn.setText("...")
        _featurefile_browse_btn.clicked.connect(self.select_featurefile)

        # ifc file
        _ifcfile_label = QtWidgets.QLabel("IFC file", self)
        self.ifcfile_text = QtWidgets.QLineEdit()
        self.ifcfile_text.setText(self.args["ifc"])
        _ifcfile_browse_btn = QtWidgets.QToolButton()
        _ifcfile_browse_btn.setText("...")
        _ifcfile_browse_btn.clicked.connect(self.select_ifcfile)

        # buttons
        self.run_button = QtWidgets.QPushButton(
            QtGui.QIcon.fromTheme("document-new"),
            "Run"
        )
        self.close_button = QtWidgets.QPushButton(
            QtGui.QIcon.fromTheme("window-close"),
            "Close"
        )
        self.run_button.clicked.connect(self.run_bimtester)
        self.close_button.clicked.connect(self.close_widget)
        _buttons = QtWidgets.QHBoxLayout()
        _buttons.addWidget(self.run_button)
        _buttons.addWidget(self.close_button)

        # Layout:
        layout = QtWidgets.QGridLayout()
        layout.addWidget(theicon, 1, 0, alignment=QtCore.Qt.AlignRight)

        layout.addWidget(_featurefile_label, 2, 0)
        layout.addWidget(self.featurefile_text, 3, 0)
        layout.addWidget(_featurefile_browse_btn, 3, 1)

        layout.addWidget(_ifcfile_label, 4, 0)
        layout.addWidget(self.ifcfile_text, 5, 0)
        layout.addWidget(_ifcfile_browse_btn, 5, 1)

        layout.addLayout(_buttons, 6, 0)
        # row stretches by 10 compared to the others, std is 0
        # first parameter is the row number
        # second is the stretch factor.
        layout.setRowStretch(0, 10)
        self.setLayout(layout)

    def select_ifcfile(self):
        ifcfile = QtWidgets.QFileDialog.getOpenFileName(
            self, dir=self.get_ifcfile()
        )[0]
        self.set_ifcfile(ifcfile)

    def set_ifcfile(self, a_file):
        self.ifcfile_text.setText(a_file)

    def get_ifcfile(self):
        # get rid of all spaces, new lines etc, might because of copy the text
        # https://stackoverflow.com/a/37001613
        return " ".join(self.ifcfile_text.text().split())

    def select_featurefile(self):
        featurefile = QtWidgets.QFileDialog.getOpenFileName(
            self, dir=self.get_ifcfile()
        )[0]
        self.set_featurefile(featurefile)

    def set_featurefile(self, a_file):
        self.featurefile_text.setText(a_file)

    def get_featurefile(self):
        # get rid of all spaces, new lines etc, might because of copy the text
        # https://stackoverflow.com/a/37001613
        return " ".join(self.featurefile_text.text().split())

    def run_bimtester(self):

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        print("Try to run BIMTester by the GUI")
        # TODO Qt messageboxes on errors

        # set the_feature file and ifc file in args
        the_featurefile = self.get_featurefile()
        the_ifcfile = self.get_ifcfile()
        if os.path.isfile(the_featurefile):
            self.args["feature"] = the_featurefile
            has_feature_file = True
        else:
            print("Feature file does not exist: {}".format(the_featurefile))
            has_feature_file = False
        if os.path.isfile(the_ifcfile):
            self.args["ifc"] = the_ifcfile
            has_ifc_file = True
        else:
            print("IFC file does not exist: {}".format(the_ifcfile))
            # TODO Qt messagebox
            has_ifc_file = False

        # run bimtester
        if has_feature_file is True and has_ifc_file is True:
            print("Args passed from BIMtester GUI:")
            print(json.dumps(self.args, indent=4))
            report_json = bimtester.run.TestRunner(
                self.args["ifc"],
                self.args["schema_file"]
            ).run(self.args)
        else:
            print("Missing files, BIMTester can not run.")
            report_json = ""

        # create html report
        if os.path.isfile(report_json):
            report_html = os.path.join(
                os.path.dirname(os.path.realpath(report_json)),
                "report.html"
            )
            bimtester.reports.ReportGenerator().generate(
                report_json,
                report_html
            )
            print("HTML report generated: {}".format(report_html))
        elif report_json == "":
            report_html = ""
            print("JSON report file has not been written.")
        else:
            report_html = ""
            print("JSON report file does not exist: {}".format(report_json))

        QtWidgets.QApplication.restoreOverrideCursor()

        if os.path.isfile(report_html):
            webbrowser.open(report_html)

    def close_widget(self):
        self.close()

    def closeEvent(self, ev):
        pw = self.parentWidget()
        if pw and pw.inherits("QDockWidget"):
            pw.deleteLater()
