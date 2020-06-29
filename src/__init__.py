"""
Add-on for Anki
Copyright (c): 2020 ijgnd
               Ankitects Pty Ltd and contributors (filter_button.py)
               lovac42 (toolbar.py)


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.



This add-on uses the file fuzzy_panel.py which has this copyright and permission notice:

    Copyright (c): 2018  Rene Schallner
                   2019- ijgnd
        
    This file (fuzzy_panel.py) is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This file is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this file.  If not, see <http://www.gnu.org/licenses/>.



This add-on uses the file "split_string.py" which has this copyright and permission notice:

    Copyright (c): 2018  Rene Schallner
                   2020- ijgnd
        
    This file (split_string.py) is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This file is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this file.  If not, see <http://www.gnu.org/licenses/>.
"""



from anki.hooks import wrap, addHook
from anki.utils import pointVersion

import aqt
from aqt.browser import Browser
from aqt.gui_hooks import (
    browser_menus_did_init,
)
from aqt.qt import (
    QAction,
    QKeySequence,
    QShortcut,
    qconnect,
)
from aqt.utils import getText, showCritical
from aqt.dyndeckconf import DeckConf

from .config import gc
from .dialog__date import DateRangeDialog
from .fuzzy_panel import FilterDialog
from .dialog__multi_line import SearchBox
from .onTextChange import onSearchEditTextChange
from .split_string import split_to_multiline
from .toolbar import getMenu


from . import browser_shortcuts_for_insert_dialog



######### Filtered Decks GUI
def dyn_setup_search(self):
    self.form.search.textChanged.connect(self.onDynSetupSearchEditTextChange)
    self.form.search_2.textChanged.connect(self.onDynSetupSearchEditTextChange)
DeckConf.initialSetup = wrap(DeckConf.initialSetup, dyn_setup_search)


def onDynSetupSearchEditTextChange(self, arg):
    parent = self
    move_dialog_in_browser = False
    include_filtered_in_deck = False
    lineedit = self.sender()  # https://stackoverflow.com/a/33981172
    mw = self.mw
    col = self.mw.col
    onSearchEditTextChange(parent, move_dialog_in_browser, include_filtered_in_deck, lineedit.text, lineedit.setText, mw, col, arg)
DeckConf.onDynSetupSearchEditTextChange = onDynSetupSearchEditTextChange





######### Browser GUI

tup = None
def check_for_advancedBrowser():
    global tup
    try:
        a = __import__("874215009").advancedbrowser.core.AdvancedBrowser
    except:
        tup = Browser
    else: 
        tup = (a, Browser)
addHook("profileLoaded", check_for_advancedBrowser)


def mysearch(self):
    self.form.searchEdit.editTextChanged.connect(self.onBrowserSearchEditTextChange)
Browser.setupSearch = wrap(Browser.setupSearch,mysearch)


def onBrowserSearchEditTextChange(self, arg):
    parent = self
    move_dialog_in_browser = True
    include_filtered_in_deck = True
    lineedit = self.form.searchEdit.lineEdit()
    mw = self.mw
    col = self.col
    dialogclosed = onSearchEditTextChange(parent, move_dialog_in_browser, include_filtered_in_deck, lineedit.text, lineedit.setText, mw, col, arg)
    if dialogclosed and dialogclosed[1]:
        self.onSearchActivated()
Browser.onBrowserSearchEditTextChange = onBrowserSearchEditTextChange


def date_range_dialog_helper(self, term):
    # self is browser
    d = DateRangeDialog(self, term)
    if d.exec():
        TriggerSearchAfter = gc("modify: window opened by search strings triggers search by default")
        _, override_autosearch_default, _, _ = overrides()
        if override_autosearch_default:
            TriggerSearchAfter ^= True
        le = self.form.searchEdit.lineEdit()
        new = le.text() + "  " + d.searchtext
        le.setText(new)
        if TriggerSearchAfter:
            self.onSearchActivated()


def open_multiline_searchwindow(browser):
    le = browser.form.searchEdit.lineEdit()
    sbi = SearchBox(browser, le.text())
    if sbi.exec():
        le.setText(sbi.newsearch)
        le.setFocus()
        browser.onSearchActivated()


def search_history_helper(self):
    # self is browser
    # similar to method from dialog__multi_line
    hist_list = self.mw.pm.profile["searchHistory"]
    processed_list = [split_to_multiline(e) for e in hist_list]
    d = FilterDialog(
        parent=self,
        parent_is_browser=True,
        values=processed_list,
        windowtitle="Filter Anki Browser Search History",
        adjPos=False,
        allowstar=False,
        infotext=False,
        show_prepend_minus_button=False,
    )
    if d.exec():
        new = d.selkey.replace("\n", "  ")
        le = self.form.searchEdit.lineEdit()
        le.setText(new)
        self.onSearchActivated()


def setupBrowserMenu(self):
    # self is browser
    view = getMenu(self, "&View")

    cut = gc("Multiline Dialog: shortcut: open window")
    # if cut:
    #    cm = QShortcut(QKeySequence(cut), self)
    #    qconnect(cm.activated, lambda b=self: open_multiline_searchwindow(b))
    action = QAction(self)
    action.setText("Show search string in multi-line dialog")
    if cut:
        action.setShortcut(QKeySequence(cut))
    view.addAction(action)
    action.triggered.connect(lambda _, b=self: open_multiline_searchwindow(b))

    cut = gc("shortcut - select entry from history in fuzzy dialog")
    # if cut:
    #    cm = QShortcut(QKeySequence(cut), self)
    #    qconnect(cm.activated, lambda b=self: search_history_helper(b))
    action = QAction(self)
    action.setText("Select entry from search history")
    if cut:
        action.setShortcut(QKeySequence(cut))
    view.addAction(action)
    action.triggered.connect(lambda _, b=self: search_history_helper(b))

    action = QAction(self)
    action.setText("Show Date Range Dialog for Added")
    view.addAction(action)
    action.triggered.connect(lambda _, b=self, t="added": date_range_dialog_helper(b, t))

    action = QAction(self)
    action.setText("Show Date Range Dialog for Rated")
    view.addAction(action)
    action.triggered.connect(lambda _, b=self, t="rated": date_range_dialog_helper(b, t))
browser_menus_did_init.append(setupBrowserMenu)

