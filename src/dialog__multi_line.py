from anki.utils import (
    isMac,
)

import aqt
from aqt.qt import (
    QDialog,
    QFont,
    QKeySequence,
    QTextCursor,
    Qt,
    QVBoxLayout,
    qtmajor,
    qtminor,
)

from aqt.utils import (
    openHelp,
    restoreGeom,
    saveGeom,
    shortcut,
    tooltip,
)

from .button_helper import (
    button_helper,
    text_change_helper,
)
from .config import gc
from .dialog__help import MiniHelpSearch, mini_search_help_dialog_title

if qtmajor == 5:
    from .forms5 import search_box  # type: ignore  # noqa
else:
    from .forms6 import search_box  # type: ignore  # noqa
from .filter_dialog import FilterDialog
from .hint import (
    browser_searchEdit_hint_shown,
)
from .split_string import (
    split_to_multiline,
)


# aqt.dialogs.register_dialog(mini_search_help_dialog_title, MiniHelpSearch, None)


searchbox_geom_name = "BSMH"


class SearchBox(QDialog):
    silentlyClose = True

    def __init__(self, browser, searchstring):
        if browser_searchEdit_hint_shown(searchstring, browser):
            self.searchstring = ""
        else:
            self.searchstring = searchstring
        self.parent = browser
        self.browser = browser
        self.mw = browser.mw
        self.col = browser.col
        QDialog.__init__(self, self.parent, Qt.WindowType.Window)
        aqt.mw.garbage_collect_on_dialog_finish(self)
        self.form = search_box.Ui_Dialog()
        self.form.setupUi(self)
        self.help_dialog = None
        self.setupUI()
        self.config_pte()
        self.settext()
        self.makeConnections()

    def settext(self):
        processed = split_to_multiline(self.searchstring)
        self.form.pte.setPlainText(processed)
        self.form.pte.setFocus()
        self.form.pte.moveCursor(QTextCursor.MoveOperation.End)

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
        self.form.pb_history.clicked.connect(self.on_history)

        but_to_cut_dict = {
            self.form.pb_nc: gc(["browser shortcuts", "shortcut - focus search box and card from note dialog"], ""),
            self.form.pb_nf: gc(["browser shortcuts", "shortcut - focus search box and field from note dialog"], ""),
            self.form.pb_deck: gc(["browser shortcuts", "shortcut - focus search box and deck selector dialog"], ""),
            self.form.pb_tag: gc(["browser shortcuts", "shortcut - focus search box and tag selector dialog"], ""),
            self.form.pb_card_props: gc(["browser shortcuts", "shortcut - focus search box and prop dialog"], ""),
            self.form.pb_card_state: gc(["browser shortcuts", "shortcut - focus search box and is dialog"], ""),
            self.form.pb_date_added: gc(["browser shortcuts", "shortcut - focus search box and date added dialog"], ""),
            self.form.pb_date_rated: gc(["browser shortcuts", "shortcut - focus search box and date rated dialog"], ""),
            self.form.pb_date_introduced: gc(
                ["browser shortcuts", "shortcut - focus search box and date introduced dialog"], ""
            ),
            self.form.pb_date_edited: gc(
                ["browser shortcuts", "shortcut - focus search box and date edited dialog"], ""
            ),
        }
        for but, cut in but_to_cut_dict.items():
            if cut:
                but.setShortcut(shortcut(cut))  # aqt.utils.shortcut replaces ctrl with cmd for macos

        history_tooltip_text = "overwrites the contents of the field"
        cut = gc(["multiline search window", "Multiline Dialog: Shortcut inside: Open History"])
        if cut:
            self.form.pb_history.setShortcut(QKeySequence(cut))
            history_tooltip_text += f"(shortcut: {cut})"
        self.form.pb_history.setToolTip(history_tooltip_text)

        option_one_shown = False
        self.form.pb_filter.setVisible(False)
        self.form.ql_filter.setVisible(False)

        option_two_shown = True
        if not gc(["multiline search window", "Multiline Dialog: show Button Bar"]):
            option_two_shown = False
            self.form.ql_button_bar.setVisible(False)
            self.form.pb_nc.setVisible(False)
            self.form.pb_nf.setVisible(False)
            self.form.pb_deck.setVisible(False)
            self.form.pb_tag.setVisible(False)
            self.form.pb_card_props.setVisible(False)
            self.form.pb_card_state.setVisible(False)
            self.form.pb_date_added.setVisible(False)
            self.form.pb_date_rated.setVisible(False)
            self.form.pb_date_introduced.setVisible(False)
            self.form.pb_date_edited.setVisible(False)

        label1 = "add filter from a nested menu. This is similar to the button from the top left of the browser:"
        label2 = "open dialog to select filter to limit by:"
        if option_one_shown and option_two_shown:
            label1 = f"Option 1: {label1}"
            label2 = f"Option 2: {label2}"
        self.form.ql_filter.setText(label1)
        self.form.ql_button_bar.setText(label2)

        self.form.pb_nc.setToolTip('for note type use "note:",\nfor cards use "card:"')
        self.form.pb_nf.setToolTip('for note type use "note:",\nfor fields use "field:"')
        self.form.pb_deck.setToolTip("deck:")
        self.form.pb_tag.setToolTip("tag:")
        self.form.pb_card_props.setToolTip("prop:")
        self.form.pb_card_state.setToolTip("is:")
        st = gc(["custom search operators for custom filter dialogs", "date range dialog for added: string"])
        if st:
            self.form.pb_date_added.setToolTip(st)
        st = gc(["custom search operators for custom filter dialogs", "date range dialog for rated: string"])
        if st:
            self.form.pb_date_rated.setToolTip(st)
        st = gc(["custom search operators for custom filter dialogs", "date range dialog for edited: string"])
        if st:
            self.form.pb_date_edited.setToolTip(st)
        st = gc(["custom search operators for custom filter dialogs", "date range dialog for introduced: string"])
        if st:
            self.form.pb_date_introduced.setToolTip(st)
        st = gc(["custom search operators for custom filter dialogs", "date range dialog for resched: string"])
        if st:
            self.form.pb_date_introduced.setToolTip(st)

    def config_pte(self):
        # self.form.pte.setTabStopDistance(20)
        # as in  clayout
        if qtmajor == 5 and qtminor < 10:
            self.form.pte.setTabStopWidth(30)
        else:
            if qtmajor == 5:
                tab_width = self.fontMetrics().width(" " * 4)
            else:
                tab_width = self.fontMetrics().horizontalAdvance(" " * 4)
            self.form.pte.setTabStopDistance(tab_width)
        if gc(["multiline search window", "Multiline Dialog: use bigger typewriter font"]):
            font = QFont("Monospace")
            font.setStyleHint(QFont.StyleHint.TypeWriter)
            defaultFontSize = font.pointSize()
            font.setPointSize(int(defaultFontSize * 1.1))
            self.form.pte.setFont(font)

    def makeConnections(self):
        self.form.pte.textChanged.connect(self.text_change_helper)
        self.form.pb_nc.clicked.connect(lambda _, a="dnc:": self.onButton(a))
        self.form.pb_nf.clicked.connect(lambda _, a="dnf:": self.onButton(a))
        self.form.pb_deck.clicked.connect(lambda _, a="deck:": self.onButton(a))
        self.form.pb_tag.clicked.connect(lambda _, a="tag:": self.onButton(a))
        self.form.pb_card_props.clicked.connect(lambda _, a="prop:": self.onButton(a))
        self.form.pb_card_state.clicked.connect(lambda _, a="is:": self.onButton(a))
        da = gc(["custom search operators for custom filter dialogs", "date range dialog for added: string"], "dadded")
        self.form.pb_date_added.clicked.connect(lambda _, a=da: self.onButton(a))
        de = gc(
            ["custom search operators for custom filter dialogs", "date range dialog for edited: string"], "dedited"
        )
        self.form.pb_date_edited.clicked.connect(lambda _, a=de: self.onButton(a))
        drat = gc(
            ["custom search operators for custom filter dialogs", "date range dialog for rated: string"], "drated"
        )
        self.form.pb_date_rated.clicked.connect(lambda _, a=drat: self.onButton(a))
        di = gc(
            ["custom search operators for custom filter dialogs", "date range dialog for introduced: string"],
            "dintroduced",
        )
        self.form.pb_date_introduced.clicked.connect(lambda _, a=di: self.onButton(a))
        dresch = gc(
            ["custom search operators for custom filter dialogs", "date range dialog for resched: string"],
            "dresched",
        )
        self.form.pb_date_resched.clicked.connect(lambda _, a=dresch: self.onButton(a))

    def onButton(self, arg, remove_on_cancel=True):
        # this will ultimately insert the arg into the QPlainTextEdit
        # which will trigger onSearchEditTextChange
        button_helper(self.form.pte, self.browser, self.mw, self.col, arg, remove_on_cancel)
        self.raise_()

    def text_change_helper(self):
        text_change_helper(self.form.pte, self.browser, self.mw, self.col)

    def help_short(self):
        if self.help_dialog:
            tooltip("mini help window is already open (but maybe it's below another window of yours).")
            self.help_dialog.raise_()  # doesn't work on MacOS
        else:
            self.help_dialog = MiniHelpSearch(self)
            self.help_dialog.show()
        # aqt.dialogs.open(mini_search_help_dialog_title, aqt.mw)

    def help_long(self):
        openHelp("searching")

    def on_history(self):
        hist_list = self.mw.pm.profile["searchHistory"]
        processed_list = [split_to_multiline(e) for e in hist_list]
        d = FilterDialog(
            parent=self.parent,
            parent_is_browser=True,
            values_as_list_or_dict=processed_list,
            windowtitle="Filter Anki Browser Search History",
            adjPos=False,
            show_star=False,
            check_star=False,
            infotext=False,
            show_prepend_minus_button=False,
            check_prepend_minus_button=False,
            multi_selection_enabled=False,
        )
        if d.exec():
            new = split_to_multiline(d.sel_keys_list[0])
            self.form.pte.setPlainText(new)
            self.form.pte.moveCursor(QTextCursor.MoveOperation.End)

    def process_text(self):
        text = self.form.pte.toPlainText()
        return text.replace("\n", " ").replace("\t", " ")

    def reject(self):
        saveGeom(self, searchbox_geom_name)
        if self.help_dialog:
            self.help_dialog.reject()
        QDialog.reject(self)

    def accept(self):
        saveGeom(self, searchbox_geom_name)
        if self.help_dialog:
            self.help_dialog.reject()
        self.newsearch = self.process_text()

        if isMac:
            le = self.browser.form.searchEdit.lineEdit()
            le.setText(self.newsearch)
            le.setFocus()
            self.browser.onSearchActivated()

        QDialog.accept(self)
