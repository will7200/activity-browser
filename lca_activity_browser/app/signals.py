# -*- coding: utf-8 -*-
from PyQt5 import QtCore


class Signals(QtCore.QObject):

    # General Settings
    switch_bw2_dir_path = QtCore.pyqtSignal()

    # Copy Text (Clipboard)
    copy_selection_to_clipboard = QtCore.pyqtSignal(str)

    # Project
    change_project = QtCore.pyqtSignal()
    new_project = QtCore.pyqtSignal()
    copy_project = QtCore.pyqtSignal()
    delete_project = QtCore.pyqtSignal()

    # Database
    add_database = QtCore.pyqtSignal()
    delete_database = QtCore.pyqtSignal()
    copy_database = QtCore.pyqtSignal()
    install_default_data = QtCore.pyqtSignal()
    import_database = QtCore.pyqtSignal()

    database_selected = QtCore.pyqtSignal(str)
    databases_changed = QtCore.pyqtSignal()
    database_changed = QtCore.pyqtSignal(str)

    # Activity (key, field, new value)
    new_activity = QtCore.pyqtSignal(str)
    activity_selected = QtCore.pyqtSignal(tuple)

    activity_modified = QtCore.pyqtSignal(tuple, str, object)
    copy_activity = QtCore.pyqtSignal(tuple)
    open_activity_tab = QtCore.pyqtSignal(str, tuple)
    activity_tabs_changed = QtCore.pyqtSignal()
    delete_activity = QtCore.pyqtSignal(tuple)

    # Exchanges
    exchanges_output_modified = QtCore.pyqtSignal(list, tuple)
    exchanges_deleted = QtCore.pyqtSignal(list)
    exchanges_add = QtCore.pyqtSignal(list, tuple)
    exchange_amount_modified = QtCore.pyqtSignal(object, float)

    # Calculation Setups
    new_calculation_setup = QtCore.pyqtSignal()
    delete_calculation_setup = QtCore.pyqtSignal()
    rename_calculation_setup = QtCore.pyqtSignal()

    calculation_setup_changed = QtCore.pyqtSignal()
    calculation_setup_selected = QtCore.pyqtSignal(str)



    # LCA Calculation
    lca_calculation = QtCore.pyqtSignal(str)

    method_selected = QtCore.pyqtSignal(tuple)
    project_selected = QtCore.pyqtSignal(str)


signals = Signals()
