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



from anki.hooks import wrap
from anki.utils import (
    isMac,
    pointVersion,
)
import aqt
from aqt.browser import Browser
from aqt.gui_hooks import (
    browser_menus_did_init,
    profile_did_open,
)
from aqt.qt import (
    QAction,
    QCursor,
    QFontMetrics,
    QKeySequence,
    QMenu,
    QPushButton,
    QShortcut,
    qconnect,
)
from aqt.utils import getText, showCritical
from aqt.dyndeckconf import DeckConf

from .button_helper import button_helper
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
profile_did_open.append(check_for_advancedBrowser)


def mysearch(self):
    if gc("-Modify Search Bar") == "multiline":
        return
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
    if isMac:
        sbi.open()
    else:
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



"""
searchEdit occurs in browser.py in 2.1.28 in these lines:

        qconnect(self.form.searchEdit.lineEdit().returnPressed, self.onSearchActivated)
        self.form.searchEdit.setCompleter(None)
        self.form.searchEdit.addItems(
        self.form.searchEdit.lineEdit().setText(self._searchPrompt)
        self.form.searchEdit.lineEdit().selectAll()
        self.form.searchEdit.setFocus()
        if self.form.searchEdit.lineEdit().text() == self._searchPrompt:
            self.form.searchEdit.lineEdit().setText("deck:current ")
        txt = self.form.searchEdit.lineEdit().text()
        self.form.searchEdit.clear()
        self.form.searchEdit.addItems(sh)
            cur = str(self.form.searchEdit.lineEdit().text())
            cur = str(self.form.searchEdit.lineEdit().text())
        self.form.searchEdit.lineEdit().setText(txt)
        filt = self.form.searchEdit.lineEdit().text()
        filt = self.form.searchEdit.lineEdit().text()
        self.form.searchEdit.lineEdit().setText(self._lastSearchTxt)
        self.form.searchEdit.lineEdit().setText(link)
        self.form.searchEdit.setFocus()
        self.form.searchEdit.lineEdit().selectAll()


so I need to modify this:

signals
    returnPressed

the functions are 
    clear()
    
    addItems() - addsList
    setCompleter(None)
    lineEdit().setText(self._searchPrompt)
    lineEdit().text()

    lineEdit().selectAll()
    self.form.searchEdit.setFocus()
    setFocus()
"""

from aqt import mw
from aqt.qt import (
    QPlainTextEdit,
    Qt,
    pyqtSignal,
)

class ComboReplacer(QPlainTextEdit):
    returnPressed = pyqtSignal()
    # add-on "symbols as you type" depends on this signal
    # which is emited from the embeded lineEdit of a 
    # qcombobox
    textEdited = pyqtSignal(str)  

    
    def __init__(self, parent):
        self.parent = parent
        self.browser = parent
        self.col = self.browser.col
        super(ComboReplacer, self).__init__(parent)
        self.makeConnectionsEtc()

    def lineEdit(self):
        return self

    def setText(self, arg):
        self.setPlainText(arg)

    def text(self):
        return self.toPlainText().replace("\n", " ")

    def setCompleter(self, arg):
        pass

    def addItems(self, list_):
        pass
    
    def clear(self):
        # _onSearchActivated clears but I don't need this here
        pass

    def cursorPosition(self):
        # needed for symbols as you type
        return self.textCursor().position()

    def setCursorPosition(self, pos):
        # needed for symbols as you type
        cursor = self.textCursor()
        cursor.setPosition(pos)
        self.setTextCursor(cursor)



    def makeConnectionsEtc(self):
        self.textChanged.connect(self.text_change_helper)

    def keyPressEvent(self, event):
        modshift = True if (mw.app.keyboardModifiers() & Qt.ShiftModifier) else False
        modctrl = True if (mw.app.keyboardModifiers() & Qt.ControlModifier) else False
        key = event.key()
        if any ([modshift, modctrl]) and key in (Qt.Key_Return, Qt.Key_Enter):
            self.returnPressed.emit()  # doesn't work
            
            # I use this complicated way for two reasons: It was very quick to make because
            # I could reuse code I have. It was quicker than finding out how the
            # pyqtSignal returnPressed would behave, etc.
            self.insert_newline()
        elif key in (Qt.Key_Return, Qt.Key_Enter):
            self.browser.onSearchActivated()
        else:
            super().keyPressEvent(event)

    def insert_newline(self):
        all_text = self.toPlainText()
        pos = self.textCursor().position()
        new = all_text[:pos] + "\n" + all_text[pos:]
        self.setPlainText(new)
        cursor = self.textCursor()
        cursor.setPosition(pos+1)
        self.setTextCursor(cursor)

    def text_change_helper(self):
        pos = self.textCursor().position()
        out = onSearchEditTextChange(
            parent=self,
            move_dialog_in_browser=False,
            include_filtered_in_deck=True,
            func_gettext=self.toPlainText,
            func_settext=self.setPlainText,
            cursorpos=pos,
            mw=self.browser.mw,
            col=self.browser.col,
            )
        if out:
            cursor = self.textCursor()
            cursor.setPosition(out[0])
            self.setTextCursor(cursor)
        self.textEdited.emit(self.toPlainText())  # needed for "Symbols as you type"


basic_stylesheet = """
QMenu::item {
    padding-top: 16px;
    padding-bottom: 16px;
    padding-right: 75px;
    padding-left: 20px;
    font-size: 15px;
}
QMenu::item:selected {
    background-color: #fd4332;
}
"""


def fuzzy_helper(self, arg):
    if self.form.searchEdit.lineEdit().text() == self._searchPrompt:
        self.form.searchEdit.lineEdit().setText("")
    button_helper(self.form.searchEdit, self, self.mw, self.col, arg)


def fuzzy_menu(self):
    # self is browser
    actions = [
        ["dnc:", "Note-Card",],
        ["dnf:", "Note-Field",],
        ["deck:", "Deck", ],
        ["note:", "Note",],
        ["card:", "Card",],
        ["tag:", "Tag", ],
        ["prop:", "Card Property", ],
        ["is:", "Card State",],
        [gc("date range dialog for added: string", "dadded"), "Date Added",],
        [gc("date range dialog for rated: string", "drated"), "Date Range",],
    ]
    menu = QMenu(self)
    menu.setStyleSheet(basic_stylesheet)

    for idx, line in enumerate(actions):
        a = QAction(line[1])
        a.triggered.connect(lambda _, b=self, i=line[0]: fuzzy_helper(b, i))
        menu.addAction(a)
        actions[idx].append(a)
    menu.exec(QCursor.pos())


def modify_browser(self):
    # self is browser
    addbutton = gc("-Add Button to the Browser Search Bar")
    justdown = True if gc("-Modify Search Bar") == "down" else False
    multiline = True if gc("-Modify Search Bar") == "multiline" else False

    grid = self.form.gridLayout
    elements = []
    for i in range(grid.count()):
        # row, column, size_cols, size_rows = grid.getItemPosition(i)
        w = grid.itemAt(i).widget()
        name = w.objectName() if hasattr(w, "objectName") else ""
        elements.append((w, name))

    gridcounter = 0

    if multiline:
        self.form.searchEdit.lineEdit().returnPressed.disconnect()
        self.form.searchEdit.setVisible(False)
        for e in elements:
            if e[1] == "searchEdit":
                grid.removeWidget(e[0])
        self.form.searchEdit = ComboReplacer(self)
        user_height = gc("-Multiline bar Height relative to default (when shown in Browser)", 100)
        default_height = self.fontMetrics().lineSpacing()
        new_height = int((default_height + 2) * 2 * user_height/100)
        self.form.searchEdit.setFixedHeight(new_height)
        #self.form.searchEdit.setMaximumHeight(new_height)
        self.form.searchButton.setShortcut("Return")
        grid.addWidget(self.form.searchEdit, 1, 0, 1, -1)
        pb_hist = QPushButton("History")
        pb_hist.clicked.connect(lambda _, browser=self: search_history_helper(browser))
        pb_hist.setObjectName("custom_history")
        grid.addWidget(pb_hist, 0, 0, 1, 1)
        gridcounter += 1

        pb_fm = QPushButton("FF")  # fuzyy menu / fuzzy find
        pb_fm.clicked.connect(lambda _, browser=self: fuzzy_menu(browser))
        pb_fm.setObjectName("fuzzy_menu")
        cut = gc("-Shortcut for Multi-bar mode: show fuzzy menu")
        if cut:
            pb_fm.setToolTip(f"shortcut: {cut}")
        grid.addWidget(pb_fm, 0, gridcounter, 1, 1)
        gridcounter += 1

    if addbutton:
        pb_sd = QPushButton("SearchDialog")
        pb_sd.clicked.connect(lambda _, browser=self: open_multiline_searchwindow(browser))
        pb_sd.setObjectName("SearchDialog")
        cut = gc("Multiline Dialog: shortcut: open window")
        if cut:
            pb_sd.setToolTip(f"shortcut: {cut}")
        grid.addWidget(pb_sd, 0, gridcounter, 1, 1)
        for idx, e in enumerate(elements):
            if e[1] == "filter":
                grid.addWidget(e[0], 0, gridcounter+1, 1, 1)
                del elements[idx]
        for idx, item in enumerate(elements):
            grid.addWidget(item[0], 0, gridcounter+2+idx, 1, 1)

    if justdown:
        # the code for "justdown" is copied verbatim from my older "side-by-side"
        # store lineedit and its index
        grid = self.form.gridLayout
        for idx in range(grid.count()):   
            item = grid.itemAt(idx)
            w = item.widget()
            name = w.objectName() if hasattr(w, "objectName") else ""
            if name == "searchEdit":
                searchbar = w
        self.form.gridLayout.addWidget(searchbar, 1, 0, 1, -1)

browser_menus_did_init.append(modify_browser)
# Browser.setupSearch = wrap(Browser.setupSearch, modify_browser, "after")