"""
Original work Copyright (c): 2018  Rene Schallner
Modified work Copyright (c): 2019- ijgnd
    
This file (filter_dialog.py) is free software: you can redistribute it and/or modify
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
- returns 
   - when the input is a list: a list of selected
   - when the input is a dict: only one value
   - this unexpected behavior occurs because originally I always returned just one value
     but later I was interested in returning multiple selections just for decks and tags.


use the class FilterDialog like this:
    d = FilterDialog(parentWindow, dict_, windowtitle)
    if d.exec():
        print(d.sel_keys_list)
        print(d.sel_value_from_dict)  # if input was a dict

syntax for the default search method: 
- strings (separated by space) can be in any order, 
- ! to exclude a string, 
- " to search for space (e.g. "the wind"), 
- ^ to indicate that the line must start with this string (e.g. _wind won't match some wind)

"""

import aqt
from aqt.qt import (
    QAbstractItemView,
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
    qtmajor,
)
from aqt.utils import tooltip, restoreGeom, saveGeom

from .config import gc, wcs
from .highlight_delegate import HighlightDelegate


inputline_last_content = {}


class PanelInputLine(QLineEdit):
    down_pressed = pyqtSignal()
    up_pressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        mod = aqt.mw.app.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier
        key = event.key()
        if key == Qt.Key.Key_Down:
            self.down_pressed.emit()
        elif key == Qt.Key.Key_Up:
            self.up_pressed.emit()
        elif mod and (key == Qt.Key.Key_N):
            self.down_pressed.emit()
        elif mod and (key == Qt.Key.Key_P):
            self.up_pressed.emit()
        elif mod and (key == Qt.Key.Key_H):
            self.up_pressed.emit()


class FilterDialog(QDialog):
    silentlyClose = True

    def __init__(
        self,
        parent=None,
        parent_is_browser=False,
        values_as_list_or_dict=None,
        windowtitle="",
        max_items=None,
        prefill="",
        adjPos=False,
        show_star=False,
        check_star=False,
        infotext="",
        show_prepend_minus_button=True,
        check_prepend_minus_button=False,
        show_run_search_on_exit=True,
        sort_vals=True,
        multi_selection_enabled=True,
        context="",
    ):
        super().__init__(parent)
        aqt.mw.garbage_collect_on_dialog_finish(self)
        self.parent = parent
        self.parent_is_browser = parent_is_browser
        self.max_items = gc(["filter dialog", "filter dialog: lines shown"], 500) if max_items is None else max_items
        self.adjustposition = adjPos
        self.show_star = show_star
        self.check_star = check_star
        self.show_prepend_minus_button = show_prepend_minus_button
        self.check_prepend_minus_button = check_prepend_minus_button
        self.show_run_search_on_exit = show_run_search_on_exit
        self.run_search_on_exit = False
        self.info_text_top = infotext
        self.context = context  # windows size, restore last input
        self.multi_selection_enabled = multi_selection_enabled
        self.tooltip_after_exit_for_parent = ""
        self.setObjectName("FilterDialog")
        if windowtitle:
            self.setWindowTitle(windowtitle)
        if isinstance(values_as_list_or_dict, dict):
            self.dict = values_as_list_or_dict
            self.keys = sorted(self.dict.keys()) if sort_vals else list(self.dict.keys())
        else:
            self.dict = False
            self.keys = sorted(values_as_list_or_dict) if sort_vals else values_as_list_or_dict
        self.matched_items_in_list_widget = self.keys
        self.endswith_sign = gc(["filter dialog", "filter dialog: endswith character(s)"], "$$")
        self.exclude_sign = gc(["filter dialog", "filter dialog: exclude character (max one char)"], "!")
        self.startswith_sign = gc(["filter dialog", "filter dialog: startswith character (max one char)"], "^")
        self.initUI()
        if self.adjustposition:
            self.moveWindow()
        if prefill:
            self.input_line.setText(prefill)

    def initUI(self):
        vlay = QVBoxLayout()
        self.input_line = PanelInputLine()
        if self.info_text_top:
            self.info_box = QLabel()
            self.info_box.setWordWrap(True)
            self.info_box.setText(self.info_text_top)
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        if all(
            [
                gc(["filter dialog", "filter dialog: allow multiple selections (only in some dialogs)"]),
                self.multi_selection_enabled,
                not self.dict,
            ]
        ):
            self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        if gc(["filter dialog", "filter dialog: highlight matches in list"]):
            self._delegate = HighlightDelegate(self.list_widget)
            self.list_widget.setItemDelegate(self._delegate)
        for i in range(self.max_items):
            self.list_widget.insertItem(i, "")
        if self.info_text_top:
            vlay.addWidget(self.info_box)
        vlay.addWidget(self.input_line)
        vlay.addWidget(self.list_widget)

        self.label_not_all_shown = QLabel()
        vlay.addWidget(self.label_not_all_shown)

        if gc(["filter dialog", "filter dialog: show info text about endwith/exclude/start char at bottom"]):
            self.info_box_bottom = QLabel()
            self.info_box_bottom.setWordWrap(True)
            text = (
                f"""{gc(["filter dialog", "filter dialog: startswith character (max one char)"], "^")} match at beginning of line (e.g. <i>^AK</i>); """
                f"""{gc(["filter dialog", "filter dialog: endswith character(s)"], "$$")} match at end of line (e.g. <i>end$$</i>); """
                f"""{gc(["filter dialog", "filter dialog: exclude character (max one char)"], "~")} exclude this (e.g. <i>~exclude</i>);"""
                "<br>In the addon config you can adjust these characters and hide this info text."
            )
            self.info_box_bottom.setText(text)
            vlay.addWidget(self.info_box_bottom)

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
        self.button_return_only_input_line = QPushButton("O&K (only current Text)", self)
        key = gc("modifier for insert current text only", "Ctrl")
        self.button_return_only_input_line.setToolTip(f"{key} + Return")
        if self.show_star:  # shortcut only if this function makes sense
            self.button_return_only_input_line.clicked.connect(self.only_input_line)
        else:
            self.button_return_only_input_line.setVisible(False)
        # don't set in dialog because otherwise multiple modifiers aren't detected
        # self.button_return_only_input_line.setShortcut(f"{key}+Return")
        # self.button_return_only_input_line.setShortcut("Ctrl+Return")
        self.button_cancel = QPushButton("&Cancel", self)
        self.button_cancel.clicked.connect(self.reject)

        self.button_run_search_on_exit = QCheckBox("run search after closing dialog")
        if self.show_run_search_on_exit:
            if gc(["filter dialog automatically search on close", self.context]):
                self.button_run_search_on_exit.setChecked(True)
        else:
            self.button_run_search_on_exit.setVisible(False)

        if self.check_star:
            self.cb_star.setChecked(True)
        button_box = QHBoxLayout()
        button_box.addWidget(self.button_run_search_on_exit)
        button_box.addStretch(1)
        button_box.addWidget(self.cb_star)
        if self.show_prepend_minus_button:
            button_box.addWidget(self.cb_neg)
        button_box.addWidget(self.button_ok)
        button_box.addWidget(self.button_return_only_input_line)
        button_box.addWidget(self.button_cancel)
        vlay.addLayout(button_box)

        self.update_listwidget()
        self.setLayout(vlay)
        self.resize(800, 350)
        restoreGeom(self, f"BrowserSearchInserterFP-{self.context}")

        # connections
        self.input_line.textChanged.connect(self.text_changed)
        self.input_line.returnPressed.connect(self.return_pressed)
        self.input_line.down_pressed.connect(self.down_pressed)
        self.input_line.up_pressed.connect(self.up_pressed)
        self.list_widget.itemDoubleClicked.connect(self.item_doubleclicked)
        self.list_widget.installEventFilter(self)
        self.input_line.setFocus()
        self.maybe_show_warning_about_hidden_tags()

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
        if qtmajor == 5:
            screen = aqt.mw.app.desktop().screenGeometry()
        else:
            screen = aqt.mw.screen().availableGeometry()
        if hori_offset + self.width() > screen.width():
            hori_offset = screen.width() - self.width()
        vert_offset = self.parent.y() + 15
        self.setGeometry(hori_offset, vert_offset, self.width(), self.height())

    def reject(self):
        # global inputline_last_content
        # inputline_last_content[self.context] = self.input_line.text()
        saveGeom(self, f"BrowserSearchInserterFP-{self.context}")
        QDialog.reject(self)

    def accept(self):
        global inputline_last_content
        sel_rows = [item.row() for item in self.list_widget.selectedIndexes()]
        if not sel_rows or len(self.matched_items_in_list_widget) == 0:
            tooltip("nothing selected. Aborting ...")
            return
        saveGeom(self, f"BrowserSearchInserterFP-{self.context}")
        self.addstar = self.cb_star.isChecked()
        self.neg = self.cb_neg.isChecked()
        self.sel_keys_list = [self.matched_items_in_list_widget[row] for row in sel_rows]
        self.inputline = self.input_line.text()
        self.just_returned_input_line_content = False
        self.sel_value_from_dict = None
        if self.dict:  # no multi selection enabled, so only one row is selected
            self.sel_value_from_dict = self.dict[self.matched_items_in_list_widget[sel_rows[0]]]
            print(f"self.sel_value_from_dict is --{self.sel_value_from_dict}--")
        inputline_last_content[self.context] = self.input_line.text()
        checked = True if self.button_run_search_on_exit.isChecked() else False
        self.run_search_on_exit = checked
        wcs(["filter dialog automatically search on close", self.context], checked)
        QDialog.accept(self)

    def only_input_line(self):
        global inputline_last_content
        saveGeom(self, f"BrowserSearchInserterFP-{self.context}")
        self.addstar = self.cb_star.isChecked()
        self.neg = self.cb_neg.isChecked()
        self.sel_value_from_dict = self.input_line.text()
        self.sel_keys_list = [self.input_line.text()]
        self.just_returned_input_line_content = True
        self.inputline = self.input_line.text()
        inputline_last_content[self.context] = self.input_line.text()
        QDialog.accept(self)

    def update_listwidget(self):
        for i in range(self.max_items):
            item = self.list_widget.item(i)
            if i < len(self.matched_items_in_list_widget):
                item.setHidden(False)
                item.setText(self.matched_items_in_list_widget[i])
            else:
                item.setHidden(True)
        self.list_widget.setCurrentRow(0)
        if gc(["filter dialog", "filter dialog: highlight matches in list"]):
            term_tuples = split_search_terms_withStart(
                self.input_line.text(), self.endswith_sign, self.exclude_sign, self.startswith_sign
            )
            terms = [item[3] for item in term_tuples if item[0]]
            self._delegate.setFilters(terms)
            self.list_widget.viewport().update()
        self.maybe_show_warning_about_hidden_tags()

    def maybe_show_warning_about_hidden_tags(self):
        if len(self.matched_items_in_list_widget) > self.max_items:
            text = f"""only showing {self.max_items} of {len(self.matched_items_in_list_widget)} matching entries. Type in more characters to narrow down the search"""
            self.label_not_all_shown.setText(text)
            self.label_not_all_shown.setVisible(True)
        else:
            self.label_not_all_shown.setVisible(False)

    def text_changed(self):
        search_string = self.input_line.text()
        if (
            search_string == "re:"
            and self.context == "tag"
            and gc(["filter dialog", "filter dialog for tags: exit on typing re:"])
        ):
            msg = "re: directly exists the tag filter dialog. If you don't want this adjust the BetterSearch settings"
            self.tooltip_after_exit_for_parent = msg
            self.sel_keys_list = "re:"
            self.addstar = False
            self.neg = False
            self.just_returned_input_line_content = False
            saveGeom(self, f"BrowserSearchInserterFP-{self.context}")
            QDialog.accept(self)
        if search_string == gc(
            ["filter dialog", "filter dialog: typing this restores inputline content from last time"]
        ):
            self.input_line.setText(inputline_last_content.get(self.context, ""))
            return
        if not search_string:
            search_string = ""
        self.matched_items_in_list_widget = process_search_string_withStart(
            search_string, self.keys, self.endswith_sign, self.exclude_sign, self.startswith_sign
        )
        if search_string in self.matched_items_in_list_widget:
            self.matched_items_in_list_widget.insert(
                0, self.matched_items_in_list_widget.pop(self.matched_items_in_list_widget.index(search_string))
            )
        self.update_listwidget()

    def up_pressed(self):
        row = self.list_widget.currentRow()
        if row == 0:
            self.list_widget.setCurrentRow(len(self.matched_items_in_list_widget) - 1)
        else:
            self.list_widget.setCurrentRow(row - 1)

    def down_pressed(self):
        row = self.list_widget.currentRow()
        if row == len(self.matched_items_in_list_widget) - 1:
            self.list_widget.setCurrentRow(0)
        else:
            self.list_widget.setCurrentRow(row + 1)

    def return_pressed(self):
        self.accept()

    def item_doubleclicked(self):
        self.accept()

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.KeyPress and event.matches(QKeySequence.StandardKey.InsertParagraphSeparator):
            self.return_pressed()
            return True
        else:
            return QWidget.eventFilter(self, watched, event)


def process_search_string_withStart(search_terms, keys, endswith_sign, exclude_sign, startswith_sign):
    """inspired by find_in_files from sublimelesszk"""
    if gc(["filter dialog", "filter dialog: ignore upper and lower case (case insensitive search)"]):
        search_terms = search_terms.lower()
    search_terms = split_search_terms_withStart(search_terms, endswith_sign, exclude_sign, startswith_sign)
    results = []
    for elem in keys:
        for presence, atstart, atend, term in search_terms:
            if term.islower():
                i = elem.lower()
            else:
                i = elem

            if presence:
                if term not in i:
                    break
                elif atstart and not i.startswith(term):
                    break
                elif atend and not i.endswith(term):
                    break
            else:  # not in
                if term in i:
                    break
                elif atstart and i.startswith(term):
                    break
                elif atend and not i.endswith(term):
                    break
        else:
            results.append(elem)
    return results


def split_search_terms_withStart(search_string, endswith_sign, exclude_sign, startswith_sign):
    """
    Split a search-spec (for find in files) into tuples:
    (in_neg, at_start, at_end, string)
    in_neg: True: must be contained, False must not be contained
    at_start:
    at_end:
    string: what must (not) be contained
    """
    in_quotes = False
    in_neg = False

    at_start = False
    at_end = False

    pos = 0
    str_len = len(search_string)
    results = []
    current_snippet = ""

    literal_quote_sign = '"'

    while pos < str_len:
        if search_string[pos:].startswith(literal_quote_sign):
            in_quotes = not in_quotes
            if not in_quotes:
                # finish this snippet
                if current_snippet:
                    if current_snippet.endswith(endswith_sign):
                        current_snippet = current_snippet[: -len(endswith_sign)]
                        at_end = True
                    results.append((in_neg, at_start, at_end, current_snippet))
                    at_end = False
                in_neg = False
                current_snippet = ""
            pos += 1
        elif search_string[pos:].startswith(exclude_sign) and not in_quotes and not current_snippet:
            in_neg = True
            pos += 1
        elif search_string[pos:].startswith(startswith_sign) and not in_quotes and not current_snippet:
            at_start = True
            pos += 1
        elif search_string[pos] in (" ", "\t") and not in_quotes:
            # push current snippet
            if current_snippet:
                if current_snippet.endswith(endswith_sign):
                    current_snippet = current_snippet[: -len(endswith_sign)]
                    at_end = True
                results.append((in_neg, at_start, at_end, current_snippet))
                at_end = False
            in_neg = False
            at_start = False
            current_snippet = ""
            pos += 1
        else:
            current_snippet += search_string[pos]
            pos += 1
    if current_snippet:
        if current_snippet.endswith(endswith_sign):
            current_snippet = current_snippet[: -len(endswith_sign)]
            at_end = True
        results.append((in_neg, at_start, at_end, current_snippet))
    return [(not in_neg, at_start, at_end, s) for in_neg, at_start, at_end, s in results]
