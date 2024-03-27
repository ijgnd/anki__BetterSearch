from anki.hooks import wrap

from aqt.browser import Browser
from aqt.gui_hooks import (
    browser_menus_did_init,
)
from aqt.qt import (
    QAction,
    QCursor,
    QMenu,
    QPushButton,
)
from .button_helper import button_helper
from .config import gc
from .hint import (
    browser_searchEdit_hint_shown,
)
from .onTextChange import onSearchEditTextChange
from .ui_browser import (
    search_history_helper,
    open_multiline_searchwindow,
)
from .ui_browser_ComboReplacer import ComboReplacer


def mysearch_41(self, card=None, search=None):
    self.form.searchEdit.editTextChanged.connect(self.onBrowserSearchEditTextChange)


Browser.setupSearch = wrap(Browser.setupSearch, mysearch_41)


def onBrowserSearchEditTextChange(self, arg):
    le = self.form.searchEdit.lineEdit()
    pos = le.cursorPosition()
    newtext, newpos, triggersearch = onSearchEditTextChange(
        parent=self,
        move_dialog_in_browser=True,
        include_filtered_in_deck=True,
        input_text=le.text(),
        cursorpos=pos,
    )
    if newtext is None:
        return
    else:
        le.setText(newtext)
        if newpos:
            le.setCursorPosition(newpos)
        if triggersearch:  # randialog and TriggerSearchAfter:
            self.onSearchActivated()


Browser.onBrowserSearchEditTextChange = onBrowserSearchEditTextChange


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
    if browser_searchEdit_hint_shown(self.form.searchEdit.lineEdit().text(), self):
        self.form.searchEdit.lineEdit().setText("")
    button_helper(self.form.searchEdit, self, self.mw, self.col, arg)


def fuzzy_menu(self):
    # self is browser
    actions = [
        [
            "dnc:",
            "Note-Card",
        ],
        [
            "dnf:",
            "Note-Field",
        ],
        [
            "deck:",
            "Deck",
        ],
        [
            "note:",
            "Note",
        ],
        [
            "card:",
            "Card",
        ],
        [
            "tag:",
            "Tag",
        ],
        [
            "prop:",
            "Card Property",
        ],
        [
            "is:",
            "Card State",
        ],
        [
            gc(["custom search operators for custom filter dialogs", "date range dialog for added: string"], "dadded"),
            "Date Added",
        ],
        [
            gc(["custom search operators for custom filter dialogs", "date range dialog for rated: string"], "drated"),
            "Date Range",
        ],
    ]
    menu = QMenu(self)
    # menu.setStyleSheet(basic_stylesheet)

    for idx, line in enumerate(actions):
        a = QAction(line[1])
        a.triggered.connect(lambda _, b=self, i=line[0]: fuzzy_helper(b, i))
        menu.addAction(a)
        actions[idx].append(a)
    menu.exec(QCursor.pos())


def modify_browser(self):
    pass


browser_menus_did_init.append(modify_browser)
