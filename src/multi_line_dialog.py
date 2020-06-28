from anki.utils import pointVersion

import aqt
from aqt.qt import (
    QDialog,
    QTextCursor,
    Qt,
    QVBoxLayout,
)

from aqt.utils import (
    openHelp,
    restoreGeom,
    saveGeom,
)

from .config import gc
from .filter_button import filter_button_cls
from .forms import search_box
from .help_dialog import MiniHelpSearch, mini_search_help_dialog_title
from .split_string import split_to_multiline


aqt.dialogs.register_dialog(mini_search_help_dialog_title, MiniHelpSearch, None)


searchbox_geom_name = "BSMH"


class SearchBox(QDialog):
    def __init__(self, browser, searchstring, quick_insert_addon_filter_func):
        self.searchstring = searchstring
        self.parent = browser
        self.browser = browser
        QDialog.__init__(self, self.parent, Qt.Window)
        self.form = search_box.Ui_Dialog()
        self.form.setupUi(self)
        self.setupUI()
        self.settext()
        if quick_insert_addon_filter_func:
            self.quick_insert_addon_filter_func = quick_insert_addon_filter_func
            self.form.pte.textChanged.connect(self.text_change_helper)

    def setupUI(self):
        self.setWindowTitle("Anki: Search Term Multiline Window")
        self.resize(800, 350)
        restoreGeom(self, searchbox_geom_name)
        self.form.pb_accepted.clicked.connect(self.accept)
        self.form.pb_accepted.setShortcut("Ctrl+Return")
        self.form.pb_accepted.setToolTip("Ctrl+Return")
        self.form.pb_rejected.clicked.connect(self.reject)
        self.form.pb_rejected.setShortcut("Esc")
        self.form.pb_rejected.setToolTip("Esc")
        self.form.pb_help_short.clicked.connect(self.help_short)
        self.form.pb_help_long.clicked.connect(self.help_long)

        # TODO
        self.form.pb_history.setVisible(False)

        if gc("Multiline Dialog: Filter Button overwrites by default"):
            self.cb_overwrite.setChecked(True)

        if pointVersion() >= 26:
            self.form.pb_filter.clicked.connect(self.filter_menu)
        else:
            # hide it
            self.form.pb_filter.setVisible(False)

    def help_short(self):
        print('in help short')
        aqt.dialogs.open(mini_search_help_dialog_title, aqt.mw)

    def help_long(self):
        openHelp("searching")

    def filter_menu(self):
        func_gettext = self.form.pte.toPlainText
        func_settext = self.form.pte.setPlainText
        filter_button_cls(self, self.browser, func_gettext, func_settext, self.form.cb_overwrite.isChecked())

    def settext(self):
        processed = split_to_multiline(self.searchstring)
        self.form.pte.setPlainText(processed)
        self.form.pte.setFocus()
        self.form.pte.moveCursor(QTextCursor.End)

    def process_text(self):
        text = self.form.pte.toPlainText()
        return text.replace("\n", "  ")

    def text_change_helper(self):
        self.quick_insert_addon_filter_func(
            parent=self.parent,
            move_dialog_in_browser=False,
            include_filtered_in_deck=True,
            func_gettext=self.form.pte.toPlainText,
            func_settext=self.form.pte.setPlainText,
            mw=self.browser.mw,
            col=self.browser.col,
            arg=self.form.pte.toPlainText(),
            )
        self.form.pte.moveCursor(QTextCursor.End)

    def reject(self):
        saveGeom(self, searchbox_geom_name)
        QDialog.reject(self)

    def accept(self):
        saveGeom(self, searchbox_geom_name)
        self.newsearch = self.process_text()
        QDialog.accept(self)
