'''
Nikolai Rusakov <nikolai.rusakov@gmail.com>  08-04-2012

You can grab precompiled pyside binaries for windows from dvlabs via this article or directly from hex-rays.com
http://dvlabs.tippingpoint.com/blog/2012/02/25/mindshare-yo-dawg-i-heard-you-like-reversing
http://dvlabs.tippingpoint.com/img/mindshare/PySide-1.0.8qt473.win32-py2.6.exe

This was designed for IDA 6.1 QT.

While I'm aware that 6.2+ already includes a more complex version of this. This is for those people who do not
have support plans any longer and are still using IDA 6.1.

It will inject an edit line into the window allowing for filtering by regex, default is case sensitive,
just edit the source and change it or add more widgets to control it.
You may also call directly n.filter('expression', ignorecase=True)

Tested and works with Names, Functions, Strings, Imports, Exports. Pretty much any subview that uses
the same basic table view layout will work.

You can change the column to filter by changing the filterColumn kwarg on the constructor.

    There may be a way to handle this but currently I'm not aware of it.
    IDA uses its own data model/source for looking up interacting/modifying its original data
    which leads us to problems with indexing. Since we can not override functions in the original QTableView instance
    from pyside (that i know of) we can not map the index to the original source index to allow proper functionality.
    We are going to implement basic navigation functionality ourselves by remapping the doubleClicked signal. This
    will leave right click context menu operations broken but I personally never use them so this does not affect me.
    Context menus in the names/functions window will be disabled to avoid someone accidently operating on the wrong
    object and creating a mess of their IDB.

Intended usage...

import filter
n = filter.filterInjectNames()
s = filter.filterInjectStrings()
f = filter.filterInjectFunctions()
i = filter.filterInject('Imports')

'''

from PySide import QtGui, QtCore
import idc

class filterInject(object):
    """
    Base class for injecting into IDA window to add regex filtering support (Names/Functions/Strings/etc)
    """
    def __init__(self, windowName, filterColumn=0):
        #collect necessary info
        self.window = self.findWindow(windowName)
        self.layout = self.findWindowLayout()
        self.table = self.findTableView()
        self.orig_model = self.table.model()

        #setup our new proxy model
        self.proxy_model = QtGui.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.orig_model)
        self.proxy_model.setFilterKeyColumn(filterColumn)
        self.proxy_model.setDynamicSortFilter(True)

        #create our lineedit to take input and add it to the layout
        self.expr_lineedit = QtGui.QLineEdit()
        self.expr_lineedit.textChanged.connect(self.__updateFilter)
        self.layout.addWidget(self.expr_lineedit)

        #inject our new proxy model into the tableview
        self.table.setModel(self.proxy_model)

        #disconnect the old handler and connect our new one
        self.table.doubleClicked.disconnect()
        self.table.doubleClicked.connect(self.onDoubleClicked)

    def onDoubleClicked(self, *args, **kwargs):
        offset = self.getJumpAddress()
        idc.Jump(offset)

    def getJumpAddress(self):
        raise NotImplementedError()

    def findWindow(self, windowName):
        """
        Locate the IDA window we are looking for
        """
        a = QtCore.QCoreApplication.instance()
        widgets = a.allWidgets()
        for x in widgets:
            if x.objectName() == windowName:
                return x
        raise Exception('Could not locate window, make sure that it is open.')

    def findTableView(self):
        """
        Locate the TableView inside the window
        """
        for x in self.window.children()[-1].children(): #last QWidget seems to hold all the children
            if type(x) == QtGui.QTableView:
                return x
        raise Exception('Could not locate QTableView of the window.')

    def findWindowLayout(self):
        """
        Locate the the QVBoxLayout of the window
        """
        for x in self.window.children(): #should always be [1] but we will search for it anyways
            if type(x) == QtGui.QVBoxLayout:
                return x
        raise Exception('Could not locate QVBoxLayout of the window.')

    def __updateFilter(self):
        self.filter(self.expr_lineedit.text())

    def filter(self, expr, ignorecase=False):
        case = QtCore.Qt.CaseInsensitive if ignorecase else QtCore.Qt.CaseSensitive
        rx = QtCore.QRegExp(expr, case, QtCore.QRegExp.RegExp2)
        self.proxy_model.setFilterRegExp(rx)


class filterInjectStrings(filterInject):
    def __init__(self, windowName='Strings window', filterColumn=3):
        super(filterInjectStrings, self).__init__(windowName, filterColumn)

    def getJumpAddress(self):
        idx = self.table.currentIndex()
        offset_idx = self.proxy_model.index(idx.row(), 0)
        offset = self.proxy_model.data(offset_idx)
        return int(offset[offset.find(':')+1:], 16)


class filterInjectNames(filterInject):
    def __init__(self, windowName='Names window', filterColumn=0):
        super(filterInjectNames, self).__init__(windowName, filterColumn)
        #disable context menu so people dont use it while filter is injected and mess up their IDBs
        for i in self.window.children()[2].children():
            if type(i) == QtGui.QMenu:
                i.setEnabled(False)

    def getJumpAddress(self):
        idx = self.table.currentIndex()
        offset_idx = self.proxy_model.index(idx.row(), 1)
        return int(self.proxy_model.data(offset_idx), 16)


class filterInjectFunctions(filterInject):
    def __init__(self, windowName='Functions window', filterColumn=0):
        super(filterInjectFunctions, self).__init__(windowName, filterColumn)
        #disable context menu so people dont use it while filter is injected and mess up their IDBs
        for i in self.window.children()[2].children():
            if type(i) == QtGui.QMenu:
                i.setEnabled(False)

    def getJumpAddress(self):
        idx = self.table.currentIndex()
        offset_idx = self.proxy_model.index(idx.row(), 2)
        return int(self.proxy_model.data(offset_idx), 16)

print '''
IDA 6.1 QT filterInject
Usage..
n = filter.filterInjectNames()
s = filter.filterInjectStrings()
f = filter.filterInjectFunctions()
i = filter.filterInject('Imports')
'''