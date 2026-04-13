from anki.hooks import wrap
from anki.utils import is_mac
from aqt.filtered_deck import FilteredDeckConfigDialog
from aqt.qt import QShortcut, QKeySequence
from aqt.utils import showInfo

from .config import gc
from .dialog__multi_line import SearchBox
from .onTextChange import onSearchEditTextChange


# self is FilteredDeckConfigDialog
def open_multiline_searchwindow(self):
    if self.form.search_2.hasFocus():
        le = self.form.search_2
    else:
        le = self.form.search
    sbi = SearchBox(self, le.text(), in_browser=False, relevant_line_edit=le)
    if is_mac:
        sbi.open()
    else:
        if sbi.exec():
            le.setText(sbi.newsearch)
            le.setFocus()


def dyn_setup_search(self):
    # self is filtered_deck.FilteredDeckConfigDialog
    self.form.search.textChanged.connect(self.onDynSetupSearchEditTextChange)
    self.form.search_2.textChanged.connect(self.onDynSetupSearchEditTextChange)

    cut1 = gc(["browser shortcuts", "Multiline Dialog: shortcut: open window"])
    if cut1:
        shortcut = QShortcut(QKeySequence(cut1), self)
        shortcut.activated.connect(lambda s=self: open_multiline_searchwindow(s))  
    cut2 = gc(["browser shortcuts", "Multiline Dialog: shortcut: open window (alternative)"])
    if cut2:
        shortcut = QShortcut(QKeySequence(cut2), self)
        shortcut.activated.connect(lambda s=self: open_multiline_searchwindow(s))

FilteredDeckConfigDialog._initial_dialog_setup = wrap(FilteredDeckConfigDialog._initial_dialog_setup, dyn_setup_search)


def onDynSetupSearchEditTextChange(self, arg):
    # self is filtered_deck.FilteredDeckConfigDialog
    le = self.sender()  # https://stackoverflow.com/a/33981172
    pos = le.cursorPosition()
    newtext, newpos, triggersearch = onSearchEditTextChange(
        parent=self,
        move_dialog_in_browser=False,
        include_filtered_in_deck=False,
        input_text=le.text(),
        cursorpos=pos,
        test_input=None,
    )
    if newtext is None:
        return
    else:
        le.setText(newtext)
        if newpos:
            le.setCursorPosition(newpos)


FilteredDeckConfigDialog.onDynSetupSearchEditTextChange = onDynSetupSearchEditTextChange
