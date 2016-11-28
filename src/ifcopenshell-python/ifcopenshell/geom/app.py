from __future__ import print_function

import os
import sys
import time
import operator
import functools

import OCC.AIS

from collections import defaultdict, Iterable, OrderedDict

os.environ['QT_API'] = 'pyqt4'
try:
    from pyqode.qt import QtCore
except: pass

from PyQt4 import QtGui, QtCore

from .code_editor_pane import code_edit

try: from OCC.Display.pyqt4Display import qtViewer3d
except: 
    import OCC.Display

    try: import OCC.Display.backend
    except: pass

    try: OCC.Display.backend.get_backend("qt-pyqt4")
    except: OCC.Display.backend.load_backend("qt-pyqt4")

    from OCC.Display.qtDisplay import qtViewer3d


from .main import settings, iterator
from .occ_utils import display_shape

from .. import open as open_ifc_file
from .. import get_supertype

# Depending on Python version and what not there may or may not be a QString
try:
    from PyQt4.QtCore import QString
except ImportError:
    QString = str
    
class configuration(object):
    def __init__(self):
        try:
            import ConfigParser
            Cfg = ConfigParser.RawConfigParser
        except:
            import configparser
            Cfg = configparser.ConfigParser(interpolation=None)
            
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
            config.set("snippets", "print all wall ids", self.config_encode("""
###########################################################################
# A simple script that iterates over all walls in the current model       #
# and prints their Globally unique IDs (GUIDS) to the console window      #
###########################################################################

for wall in model.by_type("IfcWall"):
    print ("wall with global id: "+str(wall.GlobalId))
""".lstrip()))
            
            config.set("snippets", "print properties of current selection", self.config_encode("""
###########################################################################
# A simple script that iterates over all IfcPropertySets of the currently #
# selected object and prints them to the console                          #
###########################################################################

# check if something is selected
if selection:
    #get the IfcProduct that is stored in the global variable 'selection'
    obj = selection
    for relDefinesByProperties in obj.IsDefinedBy:
         print("[{0}]".format(relDefinesByProperties.RelatingPropertyDefinition.Name))
         for prop in relDefinesByProperties.RelatingPropertyDefinition.HasProperties:
             print ("{:<20} :{}".format(prop.Name,prop.NominalValue.wrappedValue))
         print ("\\n")
""".lstrip()))
            with open(conf_file, 'w') as configfile:
                config.write(configfile)
        
        self.config = Cfg()
        self.config.read(conf_file)
        
    def options(self, s):
        return OrderedDict([(k, self.config_decode(self.config.get(s, k))) for k in self.config.options(s)])
        

class application(QtGui.QApplication):

    """A pythonOCC, PyQt based IfcOpenShell application
    with two tree views and a graphical 3d view"""

    class abstract_treeview(QtGui.QTreeWidget):
    
        """Base class for the two treeview controls"""
        
        instanceSelected = QtCore.pyqtSignal([object])
        instanceVisibilityChanged = QtCore.pyqtSignal([object, int])
        instanceDisplayModeChanged = QtCore.pyqtSignal([object, int])
        
        def __init__(self):
            QtGui.QTreeView.__init__(self)
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
            menu = QtGui.QMenu(self)
            visibility = [menu.addAction("Show"), menu.addAction("Hide")]
            displaymode = [menu.addAction("Solid"), menu.addAction("Wireframe")]
            action = menu.exec_(self.mapToGlobal(event.pos()))
            index = self.selectionModel().currentIndex()
            inst = index.data(QtCore.Qt.UserRole)
            if hasattr(inst, 'toPyObject'):
                inst = inst.toPyObject()
            if action in visibility:
                self.instanceVisibilityChanged.emit(inst, visibility.index(action))
            elif action in displaymode:
                self.instanceDisplayModeChanged.emit(inst, displaymode.index(action))
                    
        def clicked(self, index):
            inst = index.data(QtCore.Qt.UserRole)
            if hasattr(inst, 'toPyObject'):
                inst = inst.toPyObject()
            if inst:
                self.instanceSelected.emit(inst)
        
        def select(self, product):
            itm = self.product_to_item.get(product)
            if itm is None: return
            self.selectionModel().setCurrentIndex(itm, QtGui.QItemSelectionModel.SelectCurrent | QtGui.QItemSelectionModel.Rows);
        
    class decomposition_treeview(abstract_treeview):
    
        """Treeview with typical IFC decomposition relationships"""
    
        ATTRIBUTES = ['Entity', 'GlobalId', 'Name']
        
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
                            if attr == 'Entity':
                                sl.append(product.is_a())
                            else:
                                sl.append(getattr(product, attr) or '')
                        itm = items[product] = QtGui.QTreeWidgetItem(items.get(parent, self), sl)
                        itm.setData(0, QtCore.Qt.UserRole, product)
                        self.children[parent].append(product)
            self.product_to_item = dict(zip(items.keys(), map(self.indexFromItem, items.values())))
            self.connect(self, QtCore.SIGNAL("clicked(const QModelIndex &)"), self.clicked)
            self.expandAll()
                
    class type_treeview(abstract_treeview):
    
        """Treeview with typical IFC decomposition relationships"""
    
        ATTRIBUTES = ['Name']
                            
        def load_file(self, f, **kwargs):
            products = list(f.by_type("IfcProduct"))
            types = set(map(lambda i: i.is_a(), products))
            items = {}
            for t in types:
                def add(t):
                    s = get_supertype(t)
                    if s: add(s)
                    s2, t2 = map(QString, (s,t))
                    if t2 not in items:
                        itm = items[t2] = QtGui.QTreeWidgetItem(items.get(s2, self), [t2])
                        itm.setData(0, QtCore.Qt.UserRole, t2)
                        self.children[s2].append(t2)
                add(t)
            
            for p in products:
                t = QString(p.is_a())
                itm = items[p] = QtGui.QTreeWidgetItem(items.get(t, self), [p.Name or '<no name>'])
                itm.setData(0, QtCore.Qt.UserRole, t)
                self.children[t].append(p)
                
            self.product_to_item = dict(zip(items.keys(), map(self.indexFromItem, items.values())))
            self.connect(self, QtCore.SIGNAL("clicked(const QModelIndex &)"), self.clicked)
            self.expandAll()



    class property_table(QtGui.QWidget):

        def __init__(self):
            QtGui.QWidget.__init__(self)
            self.layout= QtGui.QVBoxLayout(self)
            self.setLayout(self.layout)
            self.scroll = QtGui.QScrollArea(self)
            self.layout.addWidget(self.scroll)
            self.scroll.setWidgetResizable(True)
            self.scrollContent = QtGui.QWidget(self.scroll)
            self.scrollLayout = QtGui.QVBoxLayout(self.scrollContent)
            self.scrollContent.setLayout(self.scrollLayout)
            self.scroll.setWidget(self.scrollContent)
            self.prop_dict = {}

        #triggered by selection event in either component of parent
        def select(self, product):
        
            # Clear the old contents if any
            while self.scrollLayout.count():
                child = self.scrollLayout.takeAt(0)
                if child is not None:
                    if child.widget() is not None:
                        child.widget().deleteLater()

            self.scroll = QtGui.QScrollArea()
            self.scroll.setWidgetResizable(True)

            prop_sets = self.prop_dict.get(str(product))
            
            if prop_sets is not None:
                for k,v in prop_sets:
                    group_box = QtGui.QGroupBox()

                    group_box.setTitle(k)
                    group_layout = QtGui.QVBoxLayout()
                    group_box.setLayout(group_layout)
                    
                    for name, value in v.items():
                        prop_name = str(name)
                        
                        value_str = value
                        if hasattr(value_str, "wrappedValue"):
                            value_str = value_str.wrappedValue
                            
                        if isinstance(value_str, unicode):
                            value_str = value_str.encode('utf-8')
                        else:
                            value_str = str(value_str)
                            
                        if hasattr(value, "is_a"):
                            type_str = " <i>(%s)</i>" % value.is_a()
                        else:
                            type_str = ""
                        label = QtGui.QLabel("<b>%s</b>: %s%s" % (prop_name, value_str, type_str))
                        group_layout.addWidget(label)
                        
                    group_layout.addStretch()
                    self.scrollLayout.addWidget(group_box)

                self.scrollLayout.addStretch()
            else:
                label = QtGui.QLabel("No IfcPropertySets asscociated with selected entity instance" )
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
                                    props[q.Name]=q[3]
                        elif prop_def.is_a("IfcPropertySet"):
                            for prop in prop_def.HasProperties:
                                if prop.is_a("IfcPropertySingleValue"):
                                    props[prop.Name]=prop.NominalValue
                        else:
                            # Entity introduced in IFC4
                            # prop_def.is_a("IfcPreDefinedPropertySet"):
                            for prop in range(4, len(prop_def)):
                                props[prop_def.attribute_name(prop)]=prop_def[prop]
                        return prop_set_name, props
                
                try:
                    for is_def_by in p.IsDefinedBy:
                        if is_def_by.is_a("IfcRelDefinesByProperties"):
                            propsets.append(process_pset(is_def_by.RelatingPropertyDefinition))
                        elif is_def_by.is_a("IfcRelDefinesByType"):
                            type_psets = is_def_by.RelatingType.HasPropertySets
                            if type_psets is None: continue
                            for propset in type_psets:
                                propsets.append(process_pset(propset))
                except Exception, e:
                    import traceback
                    print("failed to load properties: {}".format(e))
                    traceback.print_exc()
                    
                if len(propsets):
                    self.prop_dict[str(p)] = propsets
                
            print ("property set dictionary has {} entries".format(len(self.prop_dict)))

    class viewer(qtViewer3d):

        instanceSelected = QtCore.pyqtSignal([object])

        @staticmethod
        def ais_to_key(ais_handle):
            def yield_shapes():
                ais = ais_handle.GetObject()
                if hasattr(ais, 'Shape'):
                    yield ais.Shape()
                    return
                shp = OCC.AIS.Handle_AIS_Shape.DownCast(ais_handle)
                if not shp.IsNull(): yield shp.Shape()
                return
                mult = ais_handle
                if mult.IsNull():
                    shp = OCC.AIS.Handle_AIS_Shape.DownCast(ais_handle)
                    if not shp.IsNull(): yield shp
                else:
                    li = mult.GetObject().ConnectedTo()
                    for i in range(li.Length()):
                        shp = OCC.AIS.Handle_AIS_Shape.DownCast(li.Value(i+1))
                        if not shp.IsNull(): yield shp
            return tuple(shp.HashCode(1 << 24) for shp in yield_shapes())

        def __init__(self, widget):
            qtViewer3d.__init__(self, widget)
            self.ais_to_product = {}
            self.product_to_ais = {}
            self.counter = 0
            self.window = widget

        def initialize(self):
            self.InitDriver()
            self._display.Select = self.HandleSelection

        def load_file(self, f, setting=None):

            if setting is None:
                setting = settings()
                setting.set(setting.USE_PYTHON_OPENCASCADE, True)

            v = self._display

            t = {0: time.time()}
            def update(dt = None):
                t1 = time.time()
                if t1 - t[0] > (dt or -1):
                    v.FitAll()
                    v.Repaint()
                    t[0] = t1

            terminate = [False]
            self.window.window_closed.connect(lambda *args: operator.setitem(terminate, 0, True))

            t0 = time.time()

            it = iterator(setting, f)
            if not it.initialize():
                return

            old_progress = -1
            while True:
                if terminate[0]: break
                shape = it.get()
                product = f[shape.data.id]
                ais = display_shape(shape, viewer_handle=v)
                ais.GetObject().SetSelectionPriority(self.counter)
                self.ais_to_product[self.counter] = product
                self.product_to_ais[product] = ais
                self.counter += 1
                QtGui.QApplication.processEvents()
                if product.is_a() in {'IfcSpace', 'IfcOpeningElement'}:
                    v.Context.Erase(ais, True)
                progress = it.progress() // 2
                if progress > old_progress:
                    print("\r[" + "#" * progress + " " * (50 - progress) + "]", end="")
                    old_progress = progress
                if not it.next():
                    break
                update(0.2)

            print("\rOpened file in %.2f seconds%s" % (time.time() - t0, " "*25))

            update()

        def select(self, product):
            ais = self.product_to_ais.get(product)
            if ais is None: return
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

    class window(QtGui.QMainWindow):

        TITLE = "IfcOpenShell IFC viewer"

        window_closed = QtCore.pyqtSignal([])

        def __init__(self):
            QtGui.QMainWindow.__init__(self)
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
                a = QtGui.QAction(QtGui.QIcon(icon), label, self)
            else:
                a = QtGui.QAction(label, self)

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
        QtGui.QApplication.__init__(self, sys.argv)
        self.window = application.window()
        self.tree = application.decomposition_treeview()
        self.tree2 = application.type_treeview()
        self.propview = self.property_table()
        self.canvas = application.viewer(self.window)
        self.tabs = QtGui.QTabWidget()
        self.window.resize(800, 600)
        splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.tabs)
        self.tabs.addTab(self.tree, 'Decomposition')
        self.tabs.addTab(self.tree2, 'Types')
        self.tabs.addTab(self.propview, "Properties")
        splitter2 = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter2.addWidget(self.canvas)
        self.editor = code_edit(self.canvas, configuration().options('snippets'))
        splitter2.addWidget(self.editor)
        splitter.addWidget(splitter2)
        splitter.setSizes([200,600])
        splitter2.setSizes([400,200])
        self.window.setCentralWidget(splitter)
        self.canvas.initialize()
        self.components = [self.tree, self.tree2, self.canvas, self.propview, self.editor]
        self.files = {}

        self.window.add_menu_item('File', '&Open', self.browse, shortcut='CTRL+O')
        self.window.add_menu_item('File', '&Close', self.clear, shortcut='CTRL+W')
        self.window.add_menu_item('File', '&Exit', self.window.close, shortcut='ALT+F4')

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
        filename = QtGui.QFileDialog.getOpenFileName(self.window, 'Open file',".","Industry Foundation Classes (*.ifc)")
        self.load(filename)
        
    def clear(self):
        self.canvas._display.Context.RemoveAll()
        self.tree.clear()
        self.files.clear()
        
    def load(self, fn):
        if fn in self.files: return        
        f = open_ifc_file(str(fn))
        self.files[fn] = f
        for c in self.components:
            c.load_file(f, setting=self.settings)
            
if __name__ == "__main__":
    application().start()
