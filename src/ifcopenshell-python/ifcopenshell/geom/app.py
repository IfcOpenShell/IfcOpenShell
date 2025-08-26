# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import time
import operator
import functools
import multiprocessing
import ifcopenshell.ifcopenshell_wrapper as W

try:
    from OCC.Core import AIS

    USE_OCCT_HANDLE = False
except ImportError:
    from OCC import AIS

    USE_OCCT_HANDLE = True

from collections import defaultdict, OrderedDict
from collections.abc import Iterable

try:
    QString = unicode
except NameError:
    # Python 3
    QString = str

os.environ["QT_API"] = "pyqt5"
try:
    from pyqode.qt import QtCore
except BaseException:
    pass

from PyQt5 import QtCore, QtGui, QtWidgets

from .code_editor_pane import code_edit

try:
    from OCC.Display.pyqt5Display import qtViewer3d
except BaseException:
    import OCC.Display

    try:
        import OCC.Display.backend
    except BaseException:
        pass

    try:
        OCC.Display.backend.get_backend("qt-pyqt5")
    except BaseException:
        OCC.Display.backend.load_backend("qt-pyqt5")

    from OCC.Display.qtDisplay import qtViewer3d

from .main import settings, iterator
from .occ_utils import display_shape

from .. import open as open_ifc_file
from .. import version as ifcopenshell_version

if ifcopenshell_version < "0.6":
    # not yet ported
    from .. import get_supertype


class geometry_creation_signals(QtCore.QObject):
    completed = QtCore.pyqtSignal("PyQt_PyObject")
    progress = QtCore.pyqtSignal("PyQt_PyObject")


class geometry_creation_thread(QtCore.QThread):
    def __init__(self, signals, settings, f):
        QtCore.QThread.__init__(self)
        self.signals = signals
        self.settings = settings
        self.f = f

    def run(self):
        t0 = time.time()

        # detect concurrency from hardware, we need to have
        # at least two threads because otherwise the interface
        # is different
        # is different
        it = iterator(self.settings, self.f, max(2, multiprocessing.cpu_count()))
        if not it.initialize():
            self.signals.completed.emit([])
            return

        def _():

            old_progress = -1
            while True:
                shape = it.get()

                if shape:
                    yield shape

                if not it.next():
                    break

        self.signals.completed.emit((it, self.f, list(_())))


class configuration:
    def __init__(self):
        try:
            import ConfigParser

            Cfg = ConfigParser.RawConfigParser
        except BaseException:
            import configparser

            def Cfg():
                return configparser.ConfigParser(interpolation=None)

        conf_file = os.path.expanduser(os.path.join("~", ".ifcopenshell", "app", "snippets.conf"))
        if conf_file.startswith("~"):
            conf_file = None
            return

        self.config_encode = lambda s: s.replace("\\", "\\\\").replace("\n", "\n|")
        self.config_decode = lambda s: s.replace("\n|", "\n").replace("\\\\", "\\")

        if not os.path.exists(os.path.dirname(conf_file)):
            os.makedirs(os.path.dirname(conf_file))

        if not os.path.exists(conf_file):
            config = Cfg()
            config.add_section("snippets")
            config.set(
                "snippets",
                "print all wall ids",
                self.config_encode(
                    """
###########################################################################
# A simple script that iterates over all walls in the current model       #
# and prints their Globally unique IDs (GUIDS) to the console window      #
###########################################################################

for wall in model.by_type("IfcWall"):
    print ("wall with global id: "+str(wall.GlobalId))
""".lstrip()
                ),
            )

            config.set(
                "snippets",
                "print properties of current selection",
                self.config_encode(
                    """
###########################################################################
# A simple script that iterates over all IfcPropertySets of the currently #
# selected object and prints them to the console                          #
###########################################################################

# check if something is selected
if selection:
    #get the IfcProduct that is stored in the global variable 'selection'
    obj = selection
    for relDefinesByProperties in obj.IsDefinedBy:
        if not relDefinesByProperties.is_a("IfcRelDefinesByProperties"):
            continue
         print("[{0}]".format(relDefinesByProperties.RelatingPropertyDefinition.Name))
         if relDefinesByProperties.RelatingPropertyDefinition.is_a("IfcPropertySet"):
             for prop in relDefinesByProperties.RelatingPropertyDefinition.HasProperties:
                 print ("{:<20} :{}".format(prop.Name,prop.NominalValue.wrappedValue))
         print ("\\n")
""".lstrip()
                ),
            )
            with open(conf_file, "w") as configfile:
                config.write(configfile)

        self.config = Cfg()
        self.config.read(conf_file)

    def options(self, s):
        return OrderedDict([(k, self.config_decode(self.config.get(s, k))) for k in self.config.options(s)])


class application(QtWidgets.QApplication):
    """A pythonOCC, PyQt based IfcOpenShell application
    with two tree views and a graphical 3d view"""

    class abstract_treeview(QtWidgets.QTreeWidget):
        """Base class for the two treeview controls"""

        instanceSelected = QtCore.pyqtSignal([object])
        instanceVisibilityChanged = QtCore.pyqtSignal([object, int])
        instanceDisplayModeChanged = QtCore.pyqtSignal([object, int])

        def __init__(self):
            QtWidgets.QTreeView.__init__(self)
            self.setColumnCount(len(self.ATTRIBUTES))
            self.setHeaderLabels(self.ATTRIBUTES)
            self.children = defaultdict(list)

        def get_children(self, inst):
            c = [inst]
            i = 0
            while i < len(c):
                c.extend(self.children[c[i]])
                i += 1
            return c

        def contextMenuEvent(self, event):
            menu = QtWidgets.QMenu(self)
            visibility = [menu.addAction("Show"), menu.addAction("Hide")]
            displaymode = [menu.addAction("Solid"), menu.addAction("Wireframe")]
            action = menu.exec_(self.mapToGlobal(event.pos()))
            index = self.selectionModel().currentIndex()
            inst = index.data(QtCore.Qt.UserRole)
            if hasattr(inst, "toPyObject"):
                inst = inst
            if action in visibility:
                self.instanceVisibilityChanged.emit(inst, visibility.index(action))
            elif action in displaymode:
                self.instanceDisplayModeChanged.emit(inst, displaymode.index(action))

        def clicked_(self, index):
            inst = index.data(QtCore.Qt.UserRole)
            if hasattr(inst, "toPyObject"):
                inst = inst
            if inst:
                self.instanceSelected.emit(inst)

        def select(self, product):
            itm = self.product_to_item.get(product)
            if itm is None:
                return
            self.selectionModel().setCurrentIndex(
                itm, QtCore.QItemSelectionModel.SelectCurrent | QtCore.QItemSelectionModel.Rows
            )

    class decomposition_treeview(abstract_treeview):
        """Treeview with typical IFC decomposition relationships"""

        ATTRIBUTES = ["Entity", "GlobalId", "Name"]

        def parent(self, instance):
            if instance.is_a("IfcOpeningElement"):
                return instance.VoidsElements[0].RelatingBuildingElement
            if instance.is_a("IfcElement"):
                fills = instance.FillsVoids
                if len(fills):
                    return fills[0].RelatingOpeningElement
                containments = instance.ContainedInStructure
                if len(containments):
                    return containments[0].RelatingStructure
            if instance.is_a("IfcObjectDefinition"):
                decompositions = instance.Decomposes
                if len(decompositions):
                    return decompositions[0].RelatingObject

        def load_file(self, f, **kwargs):
            products = list(f.by_type("IfcProduct")) + list(f.by_type("IfcProject"))
            parents = list(map(self.parent, products))
            items = {}
            skipped = 0
            ATTRS = self.ATTRIBUTES
            while len(items) + skipped < len(products):
                for product, parent in zip(products, parents):
                    if parent is None and not product.is_a("IfcProject"):
                        skipped += 1
                        continue
                    if (parent is None or parent in items) and product not in items:
                        sl = []
                        for attr in ATTRS:
                            if attr == "Entity":
                                sl.append(product.is_a())
                            else:
                                sl.append(getattr(product, attr) or "")
                        itm = items[product] = QtWidgets.QTreeWidgetItem(items.get(parent, self), sl)
                        itm.setData(0, QtCore.Qt.UserRole, product)
                        self.children[parent].append(product)
            self.product_to_item = dict(zip(items.keys(), map(self.indexFromItem, items.values())))
            self.clicked.connect(self.clicked_)
            self.expandAll()

    class type_treeview(abstract_treeview):
        """Treeview with typical IFC decomposition relationships"""

        ATTRIBUTES = ["Name"]

        def load_file(self, f, **kwargs):
            products = list(f.by_type("IfcProduct"))
            types = set(map(lambda i: i.is_a(), products))
            items = {}
            for t in types:

                def add(t):
                    s = get_supertype(t)
                    if s:
                        add(s)
                    s2, t2 = map(QString, (s, t))
                    if t2 not in items:
                        itm = items[t2] = QtWidgets.QTreeWidgetItem(items.get(s2, self), [t2])
                        itm.setData(0, QtCore.Qt.UserRole, t2)
                        self.children[s2].append(t2)

                if ifcopenshell_version < "0.6":
                    add(t)

            for p in products:
                t = QString(p.is_a())
                itm = items[p] = QtWidgets.QTreeWidgetItem(items.get(t, self), [p.Name or "<no name>"])
                itm.setData(0, QtCore.Qt.UserRole, t)
                self.children[t].append(p)

            self.product_to_item = dict(zip(items.keys(), map(self.indexFromItem, items.values())))
            self.clicked.connect(self.clicked)
            self.expandAll()

    class property_table(QtWidgets.QWidget):
        def __init__(self):
            QtWidgets.QWidget.__init__(self)
            self.layout = QtWidgets.QVBoxLayout(self)
            self.setLayout(self.layout)
            self.scroll = QtWidgets.QScrollArea(self)
            self.layout.addWidget(self.scroll)
            self.scroll.setWidgetResizable(True)
            self.scrollContent = QtWidgets.QWidget(self.scroll)
            self.scrollLayout = QtWidgets.QVBoxLayout(self.scrollContent)
            self.scrollContent.setLayout(self.scrollLayout)
            self.scroll.setWidget(self.scrollContent)
            self.prop_dict = {}

        # triggered by selection event in either component of parent
        def select(self, product):

            # Clear the old contents if any
            while self.scrollLayout.count():
                child = self.scrollLayout.takeAt(0)
                if child is not None:
                    if child.widget() is not None:
                        child.widget().deleteLater()

            self.scroll = QtWidgets.QScrollArea()
            self.scroll.setWidgetResizable(True)

            prop_sets = self.prop_dict.get(str(product))

            if prop_sets is not None:
                for k, v in prop_sets:
                    group_box = QtWidgets.QGroupBox()

                    group_box.setTitle(k)
                    group_layout = QtWidgets.QVBoxLayout()
                    group_box.setLayout(group_layout)

                    for name, value in v.items():
                        prop_name = str(name)

                        value_str = value
                        if hasattr(value_str, "wrappedValue"):
                            value_str = value_str.wrappedValue

                        if isinstance(value_str, unicode):
                            value_str = value_str.encode("utf-8")
                        else:
                            value_str = str(value_str)

                        if hasattr(value, "is_a"):
                            type_str = " <i>(%s)</i>" % value.is_a()
                        else:
                            type_str = ""
                        label = QtWidgets.QLabel("<b>%s</b>: %s%s" % (prop_name, value_str, type_str))
                        group_layout.addWidget(label)

                    group_layout.addStretch()
                    self.scrollLayout.addWidget(group_box)

                self.scrollLayout.addStretch()
            else:
                label = QtWidgets.QLabel("No IfcPropertySets associated with selected entity instance")
                self.scrollLayout.addWidget(label)

        def load_file(self, f, **kwargs):
            for p in f.by_type("IfcProduct"):
                propsets = []

                def process_pset(prop_def):
                    if prop_def is not None:
                        prop_set_name = prop_def.Name
                        props = {}
                        if prop_def.is_a("IfcElementQuantity"):
                            for q in prop_def.Quantities:
                                if q.is_a("IfcPhysicalSimpleQuantity"):
                                    props[q.Name] = q[3]
                        elif prop_def.is_a("IfcPropertySet"):
                            for prop in prop_def.HasProperties:
                                if prop.is_a("IfcPropertySingleValue"):
                                    props[prop.Name] = prop.NominalValue
                        else:
                            # Entity introduced in IFC4
                            # prop_def.is_a("IfcPreDefinedPropertySet"):
                            for prop in range(4, len(prop_def)):
                                props[prop_def.attribute_name(prop)] = prop_def[prop]
                        return prop_set_name, props

                try:
                    for is_def_by in p.IsDefinedBy:
                        if is_def_by.is_a("IfcRelDefinesByProperties"):
                            propsets.append(process_pset(is_def_by.RelatingPropertyDefinition))
                        elif is_def_by.is_a("IfcRelDefinesByType"):
                            type_psets = is_def_by.RelatingType.HasPropertySets
                            if type_psets is None:
                                continue
                            for propset in type_psets:
                                propsets.append(process_pset(propset))
                except Exception as e:
                    import traceback

                    print("failed to load properties: {}".format(e))
                    traceback.print_exc()

                if len(propsets):
                    self.prop_dict[str(p)] = propsets

            print("property set dictionary has {} entries".format(len(self.prop_dict)))

    class viewer(qtViewer3d):

        instanceSelected = QtCore.pyqtSignal([object])

        #         @staticmethod
        #         def ais_to_key(ais_handle):
        #             def yield_shapes():
        #                 ais = ais_handle.GetObject()
        #                 if hasattr(ais, "Shape"):
        #                     yield ais.Shape()
        #                     return
        #                 shp = OCC.AIS.Handle_AIS_Shape.DownCast(ais_handle)
        #                 if not shp.IsNull():
        #                     yield shp.Shape()
        #                 return
        #                 mult = ais_handle
        #                 if mult.IsNull():
        #                     shp = OCC.AIS.Handle_AIS_Shape.DownCast(ais_handle)
        #                     if not shp.IsNull():
        #                         yield shp
        #                 else:
        #                     li = mult.GetObject().ConnectedTo()
        #                     for i in range(li.Length()):
        #                         shp = OCC.AIS.Handle_AIS_Shape.DownCast(li.Value(i + 1))
        #                         if not shp.IsNull():
        #                             yield shp

        #             return tuple(shp.HashCode(1 << 24) for shp in yield_shapes())

        def __init__(self, widget):
            qtViewer3d.__init__(self, widget)
            self.ais_to_product = {}
            self.product_to_ais = {}
            self.counter = 0
            self.window = widget
            self.thread = None

        def initialize(self):
            self.InitDriver()
            self._display.Select = self.HandleSelection

        def finished(self, file_shapes):
            it, f, shapes = file_shapes
            v = self._display

            t = {0: time.time()}

            def update(dt=None):
                t1 = time.time()
                if dt is None or t1 - t[0] > dt:
                    v.FitAll()
                    v.Repaint()
                    t[0] = t1

            for shape in shapes:
                ais = display_shape(shape, viewer_handle=v)
                product = f[shape.data.id]

                if USE_OCCT_HANDLE:
                    ais.GetObject().SetSelectionPriority(self.counter)
                self.ais_to_product[self.counter] = product
                self.product_to_ais[product] = ais
                self.counter += 1

                QtWidgets.QApplication.processEvents()

                if product.is_a() in {"IfcSpace", "IfcOpeningElement"}:
                    v.Context.Erase(ais, True)

                update(1.0)

            update()

            self.thread = None

        def load_file(self, f, setting=None):

            if self.thread is not None:
                return

            if setting is None:
                setting = settings()
                setting.set("dimensionality", W.CURVES_SURFACES_AND_SOLIDS)
                setting.set("use-python-opencascade", True)

            self.signals = geometry_creation_signals()
            thread = self.thread = geometry_creation_thread(self.signals, setting, f)
            self.window.window_closed.connect(lambda *args: thread.terminate())
            self.signals.completed.connect(self.finished)
            self.thread.start()

        def select(self, product):
            ais = self.product_to_ais.get(product)
            if ais is None:
                return
            v = self._display.Context
            v.ClearSelected(False)
            v.SetSelected(ais, True)

        def toggle(self, product_or_products, fn):
            if not isinstance(product_or_products, Iterable):
                product_or_products = [product_or_products]
            aiss = list(filter(None, map(self.product_to_ais.get, product_or_products)))
            last = len(aiss) - 1
            for i, ais in enumerate(aiss):
                fn(ais, i == last)

        def toggle_visibility(self, product_or_products, flag):
            v = self._display.Context
            if flag:

                def visibility(ais, last):
                    v.Erase(ais, last)

            else:

                def visibility(ais, last):
                    v.Display(ais, last)

            self.toggle(product_or_products, visibility)

        def toggle_wireframe(self, product_or_products, flag):
            v = self._display.Context
            if flag:

                def wireframe(ais, last):
                    if v.IsDisplayed(ais):
                        v.SetDisplayMode(ais, 0, last)

            else:

                def wireframe(ais, last):
                    if v.IsDisplayed(ais):
                        v.SetDisplayMode(ais, 1, last)

            self.toggle(product_or_products, wireframe)

        def HandleSelection(self, X, Y):
            v = self._display.Context
            v.Select()
            v.InitSelected()
            if v.MoreSelected():
                ais = v.SelectedInteractive()
                inst = self.ais_to_product[ais.GetObject().SelectionPriority()]
                self.instanceSelected.emit(inst)

    class window(QtWidgets.QMainWindow):

        TITLE = "IfcOpenShell IFC viewer"

        window_closed = QtCore.pyqtSignal([])

        def __init__(self):
            QtWidgets.QMainWindow.__init__(self)
            self.setWindowTitle(self.TITLE)
            self.menu = self.menuBar()
            self.menus = {}

        def closeEvent(self, *args):
            self.window_closed.emit()

        def add_menu_item(self, menu, label, callback, icon=None, shortcut=None):
            m = self.menus.get(menu)
            if m is None:
                m = self.menu.addMenu(menu)
                self.menus[menu] = m

            if icon:
                a = QtWidgets.QAction(QtGui.QIcon(icon), label, self)
            else:
                a = QtWidgets.QAction(label, self)

            if shortcut:
                a.setShortcut(shortcut)

            a.triggered.connect(callback)
            m.addAction(a)

    def makeSelectionHandler(self, component):
        def handler(inst):
            for c in self.components:
                if c != component:
                    c.select(inst)

        return handler

    def __init__(self, settings=None):
        QtWidgets.QApplication.__init__(self, sys.argv)
        self.window = application.window()
        self.tree = application.decomposition_treeview()
        self.tree2 = application.type_treeview()
        self.propview = self.property_table()
        self.canvas = application.viewer(self.window)
        self.tabs = QtWidgets.QTabWidget()
        self.window.resize(800, 600)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.tabs)
        self.tabs.addTab(self.tree, "Decomposition")
        self.tabs.addTab(self.tree2, "Types")
        self.tabs.addTab(self.propview, "Properties")
        splitter2 = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter2.addWidget(self.canvas)
        self.editor = code_edit(self.canvas, configuration().options("snippets"))
        splitter2.addWidget(self.editor)
        splitter.addWidget(splitter2)
        splitter.setSizes([200, 600])
        splitter2.setSizes([400, 200])
        self.window.setCentralWidget(splitter)
        self.canvas.initialize()
        self.components = [self.tree, self.tree2, self.canvas, self.propview, self.editor]
        self.files = {}

        self.window.add_menu_item("File", "&Open", self.browse, shortcut="CTRL+O")
        self.window.add_menu_item("File", "&Close", self.clear, shortcut="CTRL+W")
        self.window.add_menu_item("File", "&Exit", self.window.close, shortcut="ALT+F4")

        self.tree.instanceSelected.connect(self.makeSelectionHandler(self.tree))
        self.tree2.instanceSelected.connect(self.makeSelectionHandler(self.tree2))
        self.canvas.instanceSelected.connect(self.makeSelectionHandler(self.canvas))
        for t in [self.tree, self.tree2]:
            t.instanceVisibilityChanged.connect(functools.partial(self.change_visibility, t))
            t.instanceDisplayModeChanged.connect(functools.partial(self.change_displaymode, t))

        self.settings = settings

    def change_visibility(self, tree, inst, flag):
        insts = tree.get_children(inst)
        self.canvas.toggle_visibility(insts, flag)

    def change_displaymode(self, tree, inst, flag):
        insts = tree.get_children(inst)
        self.canvas.toggle_wireframe(insts, flag)

    def start(self):
        self.window.show()
        sys.exit(self.exec_())

    def browse(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self.window, "Open file", ".", "Industry Foundation Classes (*.ifc)"
        )[0]
        self.load(filename)

    def clear(self):
        self.canvas._display.Context.RemoveAll()
        self.tree.clear()
        self.files.clear()

    def load(self, fn):
        if fn in self.files:
            return
        f = open_ifc_file(str(fn))
        self.files[fn] = f
        for c in self.components:
            c.load_file(f, setting=self.settings)


if __name__ == "__main__":
    application().start()
