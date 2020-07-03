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


This add-on uses the files "sakura.css" and "sakura-dark.css" from https://github.com/oxalorg/sakura
which have this copyright and permission notice:

    MIT License

    Copyright (c) 2016 Mitesh Shah

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

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
    QPushButton,
    QShortcut,
    qconnect,
)
from aqt.utils import getText, showCritical
from aqt.dyndeckconf import DeckConf

from .config import gc
from .dialog__date import DateRangeDialog
from .dialog__multi_line import SearchBox
from .fuzzy_panel import FilterDialog
from .helpers import overrides
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
    le = self.sender()  # https://stackoverflow.com/a/33981172
    pos = le.cursorPosition()
    onSearchEditTextChange(
        parent=self,
        move_dialog_in_browser=False,
        include_filtered_in_deck=False,
        func_gettext=le.text,
        func_settext=le.setText,
        cursorpos=pos,
        mw=self.mw,
        col=self.mw.col
    )
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
    le = self.form.searchEdit.lineEdit()
    pos = le.cursorPosition()
    ret = onSearchEditTextChange(
        parent=self,
        move_dialog_in_browser=True,
        include_filtered_in_deck=True,
        func_gettext=le.text,
        func_settext=le.setText,
        cursorpos=pos,
        mw=self.mw,
        col=self.col
    )
    if not ret:
        return
    else:
        if ret[0] and ret[1]:  #randialog and TriggerSearchAfter:
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
        show_star=False,
        check_star=False,
        infotext=False,
        show_prepend_minus_button=False,
        check_prepend_minus_button=False,
    )
    if d.exec():
        new = d.selkey.replace("\n", "  ")
        le = self.form.searchEdit.lineEdit()
        le.setText(new)
        self.onSearchActivated()


def setupBrowserMenu(self):
    # self is browser
    view = getMenu(self, "&View")
    if not hasattr(self, "menuView"):
        self.menuView = view
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


def add_multi_dialog_open_button(self):
    # self is browser
    if not gc("-Add Button to the Browser Search Bar"):
        return
    if gc("-Put Multiline Search Panel into Browser"):  # this takes precendence
        return
    but = QPushButton("SearchDialog")
    but.clicked.connect(lambda _, browser=self: open_multiline_searchwindow(browser))
    but.setObjectName("SearchDialog")
    cut = gc("Multiline Dialog: shortcut: open window")
    if cut:
        but.setToolTip(f"shortcut: {cut}")

    grid = self.form.gridLayout
    elements = []
    for i in range(grid.count()):
        w = grid.itemAt(i).widget()
        name = w.objectName() if hasattr(w, "objectName") else ""
        elements.append((w,name))
    
    grid.addWidget(but, 0, 0, 1, 1)
    for idx, e in enumerate(elements):
        if e[1] == "filter":
            grid.addWidget(e[0], 0, 1, 1, 1)
            del elements[idx]
    for idx, item in enumerate(elements):
        grid.addWidget(item[0], 0, 2+idx, 1, 1)
browser_menus_did_init.append(add_multi_dialog_open_button)
