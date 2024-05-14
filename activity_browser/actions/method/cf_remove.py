from typing import List

from PySide2 import QtWidgets

from activity_browser import application
from activity_browser.brightway import bd
from activity_browser.actions.base import NewABAction
from activity_browser.ui.icons import qicons


class CFRemove(NewABAction):
    """
    ABAction to remove one or more Characterization Factors from a method. First ask for confirmation and return if the
    user cancels. Otherwise instruct the ImpactCategoryController to remove the selected Characterization Factors.
    """
    icon = qicons.delete
    text = "Remove CF('s)"

    @staticmethod
    def run(method_name: tuple, char_factors: List[tuple]):
        # ask the user whether they are sure to delete the calculation setup
        warning = QtWidgets.QMessageBox.warning(application.main_window,
                                                "Deleting Characterization Factors",
                                                f"Are you sure you want to delete {len(char_factors)} CF('s)?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                QtWidgets.QMessageBox.No
                                                )

        # return if the users cancels
        if warning == QtWidgets.QMessageBox.No: return

        method = bd.Method(method_name)
        method_dict = method.load_dict()

        for cf in char_factors:
            method_dict.pop(cf[0])

        method.write_dict(method_dict)
