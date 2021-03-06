#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import QSize, QModelIndex, Qt
from PyQt5.QtGui import QPixmap, QColor, QIcon, QBrush
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

from manuskript.enums import Perso


class persoTreeView(QTreeWidget):
    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)
        self._model = None
        self._catRow = [-1, -1, -1]
        self._filter = ""
        self._lastID = -1
        self._updating = False
        self.setRootIsDecorated(False)
        self.setIndentation(10)
        self.setHeaderHidden(True)
        self.setIconSize(QSize(24, 24))

        self.setColumnCount(1)
        self._rootItem = QTreeWidgetItem()
        self.insertTopLevelItem(0, self._rootItem)

    def setPersosModel(self, model):
        self._model = model
        self._model.dataChanged.connect(self.updateMaybe)
        self._model.rowsInserted.connect(self.updateMaybe2)
        self._model.rowsRemoved.connect(self.updateMaybe2)
        self.updateItems()

    def setFilter(self, text):
        self._filter = text
        self.updateItems()

    def updateMaybe(self, topLeft, bottomRight):
        if topLeft.parent() != QModelIndex():
            return

        if topLeft.column() <= Perso.name.value <= bottomRight.column():
            # Update name
            self.updateNames()

        elif topLeft.column() <= Perso.importance.value <= bottomRight.column():
            # Importance changed
            self.updateItems()

    def updateMaybe2(self, parent, first, last):
        # Rows inserted or removed, we update only if they are topLevel rows.
        if parent == QModelIndex():
            self.updateItems()

    def updateNames(self):
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)

            for c in range(item.childCount()):
                sub = item.child(c)
                ID = sub.data(0, Qt.UserRole)
                if ID:
                    # Update name
                    name = self._model.getPersoNameByID(ID)
                    sub.setText(0, name)
                    # Update icon
                    px = QPixmap(32, 32)
                    color = QColor(self._model.getPersoColorByID(ID))
                    px.fill(color)
                    sub.setIcon(0, QIcon(px))

    def updateItems(self):
        if not self._model:
            return

        if self.currentItem():
            self._lastID = self.currentItem().data(0, Qt.UserRole)

        self._updating = True
        self.clear()
        persos = self._model.getPersosByImportance()

        h = [self.tr("Main"), self.tr("Secondary"), self.tr("Minor")]
        for i in range(3):
            cat = QTreeWidgetItem(self, [h[i]])
            cat.setBackground(0, QBrush(QColor(Qt.blue).lighter(190)))
            cat.setForeground(0, QBrush(Qt.darkBlue))
            cat.setTextAlignment(0, Qt.AlignCenter)
            f = cat.font(0)
            f.setBold(True)
            cat.setFont(0, f)
            self.addTopLevelItem(cat)
            # cat.setChildIndicatorPolicy(cat.DontShowIndicator)

            for ID in persos[i]:
                name = self._model.getPersoNameByID(ID)
                if not self._filter.lower() in name.lower():
                    continue
                item = QTreeWidgetItem(cat, [name])
                item.setData(0, Qt.UserRole, ID)
                px = QPixmap(32, 32)
                color = QColor(self._model.getPersoColorByID(ID))
                px.fill(color)
                item.setIcon(0, QIcon(px))

                if ID == self._lastID:
                    self.setCurrentItem(item)

        self.expandAll()
        self._updating = False

    def getItemByID(self, ID):
        for t in range(self.topLevelItemCount()):
            for i in range(self.topLevelItem(t).childCount()):
                item = self.topLevelItem(t).child(i)
                if item.data(0, Qt.UserRole) == ID:
                    return item

    def currentPersoIndex(self):
        ID = None
        if self.currentItem():
            ID = self.currentItem().data(0, Qt.UserRole)

        return self._model.getIndexFromID(ID)

    def mouseDoubleClickEvent(self, event):
        item = self.currentItem()
        # Catching double clicks to forbid collapsing of toplevel items
        if item.parent():
            QTreeWidget.mouseDoubleClickEvent(self, event)
