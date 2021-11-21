"""
Original work Copyright (c): 2018  Rene Schallner
Modified work Copyright (c): 2019- ijgnd
    
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


extracted from https://github.com/renerocksai/sublimeless_zk/tree/6738375c0e371f0c2fde0aa9e539242cfd2b4777/src
mainly from fuzzypanel.py (both Classes) and utils.py (the helper functions from the 
bottom of this file)


This is a pyqt dialog that 
- takes a list or dict
- shows the listitems or dictkeys in a QListWidget that you can filter
- returns select listitem or dictkey/dictvalue

use the class FilterDialog like this:
    d = FilterDialog(parentWindow, dict_, windowtitle)
    if d.exec():
        print(d.selkey)
        print(d.selvalue)  # if input was a dict

syntax for the default search method: 
- strings (separated by space) can be in any order, 
- ! to exclude a string, 
- " to search for space (e.g. "the wind"), 
- _ to indicate that the line must start with this string (e.g. _wind won't match some wind)

"""

from aqt import mw
from aqt.qt import (
    QCheckBox,
    QDialog,
    QEvent,
    QHBoxLayout,
    QKeySequence,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    Qt,
    QVBoxLayout,
    QWidget,
    pyqtSignal,
)
from aqt.utils import tooltip, restoreGeom, saveGeom

from .config import gc


class PanelInputLine(QLineEdit):
    down_pressed = pyqtSignal()
    up_pressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        mod = mw.app.keyboardModifiers() & Qt.ControlModifier
        key = event.key()
        if key == Qt.Key_Down:
            self.down_pressed.emit()
        elif key == Qt.Key_Up:
            self.up_pressed.emit()
        elif mod and (key == Qt.Key_N):
            self.down_pressed.emit()
        elif mod and (key == Qt.Key_P):
            self.up_pressed.emit()
        elif mod and (key == Qt.Key_H):
            self.up_pressed.emit()


class FilterDialog(QDialog):
    def __init__(
        self,
        parent=None,
        parent_is_browser=False,
        values=None,
        windowtitle="",
        max_items=10000,
        prefill="",
        adjPos=False,
        show_star=False,
        check_star=False,
        infotext="",
        show_prepend_minus_button=True,
        check_prepend_minus_button=True,
        sort_vals=True
    ):
        super().__init__(parent)
        self.parent = parent
        self.parent_is_browser = parent_is_browser
        self.max_items = max_items
        self.adjustposition = adjPos
        self.show_star = show_star
        self.check_star = check_star
        self.show_prepend_minus_button = show_prepend_minus_button
        self.check_prepend_minus_button = check_prepend_minus_button
        self.infotext = infotext
        self.setObjectName("FilterDialog")
        if windowtitle:
            self.setWindowTitle(windowtitle)
        if isinstance(values, dict):
            self.dict = values
            self.keys = sorted(self.dict.keys()) if sort_vals else list(self.dict.keys())
        else:
            self.dict = False
            self.keys = sorted(values) if sort_vals else values
        self.fuzzy_items = self.keys[:max_items]
        self.initUI()
        if self.adjustposition:
            self.moveWindow()
        if prefill:
            self.input_line.setText(prefill)

    def initUI(self):
        vlay = QVBoxLayout()
        self.input_line = PanelInputLine()
        if self.infotext:
            self.info_box = QLabel()
            self.info_box.setWordWrap(True)
            self.info_box.setText(self.infotext)
        self.list_box = QListWidget()
        for i in range(self.max_items):
            self.list_box.insertItem(i, "")
        if self.infotext:
            vlay.addWidget(self.info_box)
        vlay.addWidget(self.input_line)
        vlay.addWidget(self.list_box)

        self.cb_star = QCheckBox("append *")
        if self.check_star:
            self.cb_star.setChecked(True)
        if not self.show_star:
            self.cb_star.setVisible(False)
        self.cb_neg = QCheckBox("prepend search with '-'")
        if self.check_prepend_minus_button:
            self.cb_neg.setChecked(True)
        self.button_ok = QPushButton("&OK", self)
        self.button_ok.clicked.connect(self.accept)
        self.button_ok.setToolTip("Return")
        # self.button_ok.setAutoDefault(True)
        self.button_accept_current = QPushButton("O&K (only current Text)", self)
        key = gc("modifier for insert current text only")
        self.button_accept_current.setToolTip(f"{key} + Return")
        if self.show_star:  # shortcut only if this function makes sense
            self.button_accept_current.clicked.connect(self.accept_current)
        else:
            self.button_accept_current.setVisible(False)
        # don't set in dialog because otherwise multiple modifiers aren't detected
        # self.button_accept_current.setShortcut(f"{key}+Return")
        # self.button_accept_current.setShortcut("Ctrl+Return")
        self.button_cancel = QPushButton("&Cancel", self)
        self.button_cancel.clicked.connect(self.reject)

        button_box = QHBoxLayout()
        button_box.addStretch(1)
        button_box.addWidget(self.cb_star)
        if self.show_prepend_minus_button:
            button_box.addWidget(self.cb_neg)
        button_box.addWidget(self.button_ok)
        button_box.addWidget(self.button_accept_current)
        button_box.addWidget(self.button_cancel)
        vlay.addLayout(button_box)

        self.update_listbox()
        self.setLayout(vlay)
        self.resize(800, 350)
        restoreGeom(self, "BrowserSearchInserterFP")
        self.list_box.setAlternatingRowColors(True)

        # connections
        self.input_line.textChanged.connect(self.text_changed)
        self.input_line.returnPressed.connect(self.return_pressed)
        self.input_line.down_pressed.connect(self.down_pressed)
        self.input_line.up_pressed.connect(self.up_pressed)
        self.list_box.itemDoubleClicked.connect(self.item_doubleclicked)
        self.list_box.installEventFilter(self)
        self.input_line.setFocus()

    def moveWindow(self):
        if not self.parent_is_browser:
            return
        sbar = self.parent.sidebarDockWidget
        line = self.parent.form.searchEdit.lineEdit()
        # line.cursor() refers to mouse position
        cursor = line.cursorPosition()
        if sbar.isVisible():
            hori_offset = self.parent.x() + sbar.width() + 125 + int(4 * cursor)
        else:
            hori_offset = self.parent.x() + 125 + int(4 * cursor)
        screen = mw.app.desktop().screenGeometry()
        if hori_offset + self.width() > screen.width():
            hori_offset = screen.width() - self.width()
        vert_offset = self.parent.y() + 15
        self.setGeometry(hori_offset, vert_offset, self.width(), self.height())

    def reject(self):
        saveGeom(self, "BrowserSearchInserterFP")
        QDialog.reject(self)

    def accept(self):
        saveGeom(self, "BrowserSearchInserterFP")
        row = self.list_box.currentRow()
        if len(self.fuzzy_items) > 0:
            self.addstar = self.cb_star.isChecked()
            self.neg = self.cb_neg.isChecked()
            row = self.list_box.currentRow()
            if row > len(self.fuzzy_items) - 1:  # list are zero indexed
                return  # avoid IndexError: list index out of range on the following line
            self.selkey = self.fuzzy_items[row]
            self.inputline = self.input_line.text()
            self.lineonly = False
            self.selvalue = None
            if self.dict:
                self.selvalue = self.dict[self.selkey]
            QDialog.accept(self)
        else:
            tooltip("nothing selected. Aborting ...")
            return

    def accept_current(self):
        saveGeom(self, "BrowserSearchInserterFP")
        self.addstar = self.cb_star.isChecked()
        self.neg = self.cb_neg.isChecked()
        self.selvalue = self.input_line.text()
        self.selkey = self.input_line.text()
        self.lineonly = True
        self.inputline = self.input_line.text()
        QDialog.accept(self)

    def update_listbox(self):
        for i in range(self.max_items):
            item = self.list_box.item(i)
            if i < len(self.fuzzy_items):
                item.setHidden(False)
                item.setText(self.fuzzy_items[i])
            else:
                item.setHidden(True)
        self.list_box.setCurrentRow(0)

    def text_changed(self):
        search_string = self.input_line.text()
        FILTER_WITH = "slzk_mod"  # "slzk", "fuzzyfinder"
        if FILTER_WITH == "fuzzyfinder":  # https://pypi.org/project/fuzzyfinder/
            if search_string:
                self.fuzzy_items = list(fuzzyfinder(search_string, self.keys))[:self.max_items]  # noqa
            else:
                self.fuzzy_items = list(self.keys)[:self.max_items]
        else:
            if not search_string:
                search_string = ""
            if FILTER_WITH == "slzk_mod":
                self.fuzzy_items = process_search_string_withStart(search_string, self.keys, self.max_items)
                if search_string in self.fuzzy_items:
                    self.fuzzy_items.insert(0, self.fuzzy_items.pop(self.fuzzy_items.index(search_string)))
            elif FILTER_WITH == "slzk":
                self.fuzzy_items = process_search_string(search_string, self.keys, self.max_items)
        self.update_listbox()

    def up_pressed(self):
        row = self.list_box.currentRow()
        if row == 0:
            self.list_box.setCurrentRow(len(self.fuzzy_items) - 1)
        else:
            self.list_box.setCurrentRow(row - 1)

    def down_pressed(self):
        row = self.list_box.currentRow()
        if row == len(self.fuzzy_items) - 1:
            self.list_box.setCurrentRow(0)
        else:
            self.list_box.setCurrentRow(row + 1)

    def return_pressed(self):
        self.accept()

    def item_doubleclicked(self):
        self.accept()

    def eventFilter(self, watched, event):
        if event.type() == QEvent.KeyPress and event.matches(QKeySequence.InsertParagraphSeparator):
            self.return_pressed()
            return True
        else:
            return QWidget.eventFilter(self, watched, event)


def process_search_string_withStart(search_terms, keys, max):
    """inspired by find_in_files from sublimelesszk"""
    if gc("ignore upper and lower case (case insensitive search)"):
        search_terms = search_terms.lower()
    search_terms = split_search_terms_withStart(search_terms)
    results = []
    for lent in keys:
        for presence, atstart, term in search_terms:
            if term.islower():
                i = lent.lower()
            else:
                i = lent

            # if presence and term not in i:
                # break
            # elif not presence and term in i:
                # break
                
            if presence:
                if term not in i:
                    break
                elif atstart and not i.startswith(term):
                    break
            else:  # not in
                if term in i:
                    break
                elif atstart and i.startswith(term):
                    break
        else:
            results.append(lent)
    return results


def split_search_terms_withStart(search_string):
    """
    Split a search-spec (for find in files) into tuples:
    (posneg, string)
    posneg: True: must be contained, False must not be contained
    string: what must (not) be contained
    """
    in_quotes = False
    in_neg = False

    at_start = False

    pos = 0
    str_len = len(search_string)
    results = []
    current_snippet = ""

    literal_quote_sign = '"'
    exclude_sign = "!"
    startswith_sign = "_"

    while pos < str_len:
        if search_string[pos:].startswith(literal_quote_sign):
            in_quotes = not in_quotes
            if not in_quotes:
                # finish this snippet
                if current_snippet:
                    results.append((in_neg, at_start, current_snippet))
                in_neg = False
                current_snippet = ""
            pos += 1
        elif search_string[pos:].startswith(exclude_sign) and not in_quotes and not current_snippet:
            in_neg = True
            pos += 1
        elif (
            search_string[pos:].startswith(startswith_sign)
            and not in_quotes
            and not current_snippet
        ):
            at_start = True
            pos += 1
        elif search_string[pos] in (" ", "\t") and not in_quotes:
            # push current snippet
            if current_snippet:
                results.append((in_neg, at_start, current_snippet))
            in_neg = False
            at_start = False
            current_snippet = ""
            pos += 1
        else:
            current_snippet += search_string[pos]
            pos += 1
    if current_snippet:
        results.append((in_neg, at_start, current_snippet))
    return [(not in_neg, at_start, s) for in_neg, at_start, s in results]


def process_search_string(search_terms, keys, max):
    """inspired by find_in_files from sublimelesszk"""
    search_terms = split_search_terms(search_terms)
    results = []
    for lent in keys:
        for presence, term in search_terms:
            if term.islower():
                i = lent.lower()
            else:
                i = lent
            if presence and term not in i:
                break
            elif not presence and term in i:
                break
        else:
            results.append(lent)
    return results


def split_search_terms(search_string):
    """
    Split a search-spec (for find in files) into tuples:
    (posneg, string)
    posneg: True: must be contained, False must not be contained
    string: what must (not) be contained
    """
    in_quotes = False
    in_neg = False
    pos = 0
    str_len = len(search_string)
    results = []
    current_snippet = ""
    while pos < str_len:
        if search_string[pos:].startswith('"'):
            in_quotes = not in_quotes
            if not in_quotes:
                # finish this snippet
                if current_snippet:
                    results.append((in_neg, current_snippet))
                in_neg = False
                current_snippet = ""
            pos += 1
        elif search_string[pos:].startswith("!") and not in_quotes and not current_snippet:
            in_neg = True
            pos += 1
        elif search_string[pos] in (" ", "\t") and not in_quotes:
            # push current snippet
            if current_snippet:
                results.append((in_neg, current_snippet))
            in_neg = False
            current_snippet = ""
            pos += 1
        else:
            current_snippet += search_string[pos]
            pos += 1
    if current_snippet:
        results.append((in_neg, current_snippet))
    return [(not in_neg, s) for in_neg, s in results]
