# -*- coding: utf-8 -*-
import brightway2 as bw
from PyQt5 import QtCore, QtGui, QtWidgets

from .activity import ActivitiesTable
from .table import ABTableWidget, ABTableItem
from .ia import MethodsTable
from ..icons import icons
from ...signals import signals


class CSList(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super(CSList, self).__init__(parent)
        # Runs even if selection doesn't change
        self.activated['QString'].connect(self.set_cs)
        signals.calculation_setup_selected.connect(self.sync)

    def sync(self, name):
        self.clear()
        keys = sorted(bw.calculation_setups)
        self.insertItems(0, keys)
        self.setCurrentIndex(keys.index(name))

    def set_cs(self, name):
        signals.calculation_setup_selected.emit(name)

    @property
    def name(self):
        return self.itemText(self.currentIndex())


class CSActivityTable(ABTableWidget):
    COLUMNS = {
        0: "name",
        1: "amount",
        2: "unit",
    }

    def __init__(self):
        super(CSActivityTable, self).__init__()
        self.setColumnCount(3)
        self.setSortingEnabled(True)
        self.setAcceptDrops(True)

        self.cellChanged.connect(self.filter_amount_change)
        signals.calculation_setup_selected.connect(self.sync)

        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.delete_row_action = QtWidgets.QAction(
            QtGui.QIcon(icons.delete), "Remove row", None
        )
        self.addAction(self.delete_row_action)
        self.delete_row_action.triggered.connect(self.delete_rows)

    @ABTableWidget.decorated_sync
    def sync(self, name):
        self.cellChanged.disconnect(self.filter_amount_change)
        self.setRowCount(0)
        self.setHorizontalHeaderLabels(["Activity name", "Amount", "Unit"])

        for func_unit in bw.calculation_setups[name]['inv']:
            for key, amount in func_unit.items():
                act = bw.get_activity(key)
                new_row = self.rowCount()
                self.insertRow(new_row)
                self.setItem(new_row, 0, ABTableItem(act['name'], key=key))
                self.setItem(new_row, 1, ABTableItem(amount, key=key, editable=True))
                self.setItem(new_row, 2, ABTableItem(act.get('unit', 'Unknown'), key=key))

        self.cellChanged.connect(self.filter_amount_change)

    def delete_rows(self, *args):
        to_delete = []
        for range_obj in self.selectedRanges():
            bottom = range_obj.bottomRow()
            top = range_obj.topRow()
            to_delete.extend(list(range(top, bottom + 1)))
        to_delete.sort(reverse=True)
        for row in to_delete:
            self.removeRow(row)
        signals.calculation_setup_changed.emit()

    def dragEnterEvent(self, event):
        if isinstance(event.source(), ActivitiesTable):
            event.accept()

    def dropEvent(self, event):
        new_keys = [item.key for item in event.source().selectedItems()]
        for key in new_keys:
            act = bw.get_activity(key)
            if act['type'] != "process":
                continue

            new_row = self.rowCount()
            self.insertRow(new_row)
            self.setItem(new_row, 0, ABTableItem(act['name'], key=key))
            self.setItem(new_row, 1, ABTableItem("1.0", key=key, editable=True))
            self.setItem(new_row, 2, ABTableItem(act.get('unit', 'Unknown'), key=key))

        event.accept()

        signals.calculation_setup_changed.emit()

        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def to_python(self):
        return [{self.item(row, 0).key: self.item(row, 1).text()} for row in range(self.rowCount())]

    def filter_amount_change(self, row, col):
        if col == 1:
            signals.calculation_setup_changed.emit()


class CSMethodsTable(ABTableWidget):
    def __init__(self):
        super(CSMethodsTable, self).__init__()
        self.setColumnCount(1)
        self.setSortingEnabled(True)
        self.setAcceptDrops(True)

        signals.calculation_setup_selected.connect(self.sync)

        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.delete_row_action = QtWidgets.QAction(
            QtGui.QIcon(icons.delete), "Remove row", None
        )
        self.addAction(self.delete_row_action)
        self.delete_row_action.triggered.connect(self.delete_rows)

    def sync(self, name):
        self.clear()
        self.setRowCount(0)
        self.setHorizontalHeaderLabels(["Name"])

        for obj in bw.calculation_setups[name]['ia']:
            new_row = self.rowCount()
            self.insertRow(new_row)
            self.setItem(new_row, 0, ABTableItem(", ".join(obj), method=obj,))

        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def dragEnterEvent(self, event):
        if isinstance(event.source(), MethodsTable):
            event.accept()

    def dropEvent(self, event):
        new_methods = [item.method for item in event.source().selectedItems()]
        if self.rowCount():
            existing = {self.item(index, 0).method for index in range(self.rowCount())}
        else:
            existing = {}
        for obj in new_methods:
            if obj in existing:
                continue
            new_row = self.rowCount()
            self.insertRow(new_row)
            self.setItem(new_row, 0, ABTableItem(", ".join(obj), method=obj,))
        event.accept()

        signals.calculation_setup_changed.emit()

        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def delete_rows(self, *args):
        to_delete = []
        for range_obj in self.selectedRanges():
            bottom = range_obj.bottomRow()
            top = range_obj.topRow()
            to_delete.extend(list(range(top, bottom + 1)))
        to_delete.sort(reverse=True)
        for row in to_delete:
            self.removeRow(row)
        signals.calculation_setup_changed.emit()

    def to_python(self):
        return [self.item(row, 0).method for row in range(self.rowCount())]
