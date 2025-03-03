# -*- coding: utf-8 -*-
from .panel import ABTab


class LeftPanel(ABTab):
    side = "left"

    def __init__(self, *args):
        from ..tabs import HistoryTab, MethodsTab, ProjectTab

        super(LeftPanel, self).__init__(*args)

        self.tabs = {
            "Project": ProjectTab(self),
            "Impact Categories": MethodsTab(self),
            "History": HistoryTab(self),
        }
        for tab_name, tab in self.tabs.items():
            self.addTab(tab, tab_name)
        # tabs hidden at start
        self.hide_tab("History")
