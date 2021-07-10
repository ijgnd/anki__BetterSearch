from aqt.gui_hooks import (
    browser_menus_did_init,
)
from aqt.qt import (
    QKeySequence,
    QShortcut,
)

from .config import gc


def insert_helper(self, arg):
    le = self.form.searchEdit.lineEdit()
    old = le.text()
    le.setText(old + " " + arg)
    self.onSearchActivated()


def cutlist():
    cl = [
#   if False not active, if True contains cut               ,       action 
[gc("shortcut - focus search box and card selector dialog"),     "card:"],
[gc("shortcut - focus search box and note selector dialog"),     "note:"],
[gc("shortcut - focus search box and tag selector dialog"),      "tag:"],
[gc("shortcut - focus search box and deck selector dialog"),     "deck:"],
[gc("shortcut - focus search box and tag/deck selector dialog"), gc("custom tag&deck string 1")],
[gc("shortcut - focus search box and prop dialog"),              "prop:"],
[gc("shortcut - focus search box and is dialog"),                "is:"],
[gc("shortcut - focus search box and card from note dialog"),    "cfn:"],
[gc("shortcut - focus search box and field from note dialog"),   "ffn:"],
[gc("shortcut - focus search box and date added dialog"),        gc("date range dialog for added: string")],
[gc("shortcut - focus search box and date rated dialog"),        gc("date range dialog for rated: string")],
]
    return cl


def setup_menu(browser):
    for cut, action in cutlist():
        if cut and action:
            e = QShortcut(QKeySequence(cut), browser)
            e.activated.connect(lambda b=browser, a=action: insert_helper(b, a))
browser_menus_did_init.append(setup_menu)  # noqa
