# TODO merge into bimtester module

import sys
from PySide2 import QtWidgets

from bimtester.guiwidget import GuiWidgetBimTester


def show_widget():

    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)

    # Create and show the form
    form = GuiWidgetBimTester()
    form.show()

    # Run the main Qt loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    show_widget()
