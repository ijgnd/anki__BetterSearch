from anki.utils import (
    isMac,
    pointVersion,
)

import aqt
from aqt.qt import (
    QDialog,
    QFont,
    QKeySequence,
    QTextCursor,
    Qt,
    QVBoxLayout,
    qtminor,
)

from aqt.utils import (
    openHelp,
    restoreGeom,
    saveGeom,
    tooltip,
)

from .config import gc
from .dialog__help import MiniHelpSearch, mini_search_help_dialog_title
from .filter_button import filter_button_cls
from .forms import search_box
from .fuzzy_panel import FilterDialog
from .helpers import (
    # this is the order in helpers.py
    tags,
    is_values,
    is_values_with_explanations,
    props,
    overrides,
    field_infotext,
)
from .onTextChange import onSearchEditTextChange
from .split_string import (
    split_to_multiline,
)


# aqt.dialogs.register_dialog(mini_search_help_dialog_title, MiniHelpSearch, None)


searchbox_geom_name = "BSMH"


class SearchBox(QDialog):
    def __init__(self, browser, searchstring):
        if searchstring == browser._searchPrompt:
            self.searchstring = ""
        else:
            self.searchstring = searchstring
        self.parent = browser
        self.browser = browser
        self.col = browser.col
        QDialog.__init__(self, self.parent, Qt.Window)
        self.form = search_box.Ui_Dialog()
        self.form.setupUi(self)
        self.help_dialog = None
        self.setupUI()
        self.config_pte()
        self.settext()
        self.makeConnections()

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

        history_tooltip_text = "overwrites the contents of the field"
        cut = gc("Multiline Dialog: Shortcut inside: Open History")
        if cut:
            self.form.pb_history.setShortcut(QKeySequence(cut))
            history_tooltip_text += f"(shortcut: {cut})"
        self.form.pb_history.setToolTip(history_tooltip_text)

        if pointVersion() >= 26 and gc("Multiline Dialog: show Filter Button"):
            self.form.pb_filter.clicked.connect(self.filter_menu)
        else:
            self.form.pb_filter.setVisible(False)
            self.form.ql_filter.setVisible(False)

        if not gc("Multiline Dialog: show Button Bar"):
            self.form.ql_button_bar.setVisible(False)
            self.form.pb_nc.setVisible(False)
            self.form.pb_nf.setVisible(False)
            self.form.pb_deck.setVisible(False)
            self.form.pb_tag.setVisible(False)
            self.form.pb_card_props.setVisible(False)
            self.form.pb_card_state.setVisible(False)
            self.form.pb_date_added.setVisible(False)
            self.form.pb_date_rated.setVisible(False)

        self.form.pb_nc.setToolTip('for note type use "note:",\nfor cards use "card:"')
        self.form.pb_nf.setToolTip('for note type use "note:",\nfor fields use "field:"')       
        self.form.pb_deck.setToolTip("deck:")
        self.form.pb_tag.setToolTip("tag:")
        self.form.pb_card_props.setToolTip("prop:")
        self.form.pb_card_state.setToolTip("is:")
        st = gc("date range dialog for added: string")
        self.form.pb_date_added.setToolTip(st)
        st = gc("date range dialog for rated: string")
        self.form.pb_date_rated.setToolTip(st)

    def config_pte(self):
        #self.form.pte.setTabStopDistance(20)
        # as in  clayout
        if qtminor < 10:
            self.form.pte.setTabStopWidth(30)
        else:
            tab_width = self.fontMetrics().width(" " * 4)
            self.form.pte.setTabStopDistance(tab_width)
        if gc("Multiline Dialog: use bigger typewriter font"):
            font = QFont("Monospace")
            font.setStyleHint(QFont.TypeWriter)
            defaultFontSize = font.pointSize()
            font.setPointSize(int(defaultFontSize*1.1))
            self.form.pte.setFont(font)

    def makeConnections(self):
        self.form.pte.textChanged.connect(self.text_change_helper)
        self.form.pb_nc.clicked.connect(lambda _, a="dnc:": self.button_helper(a))
        self.form.pb_nf.clicked.connect(lambda _, a="dnf:": self.button_helper(a))
        self.form.pb_deck.clicked.connect(lambda _, a="deck:": self.button_helper(a))
        self.form.pb_tag.clicked.connect(lambda _, a="tag:": self.button_helper(a))
        self.form.pb_card_props.clicked.connect(lambda _, a="prop:": self.button_helper(a))
        self.form.pb_card_state.clicked.connect(lambda _, a="is:": self.button_helper(a))
        da = gc("date range dialog for added: string", "dadded")
        self.form.pb_date_added.clicked.connect(lambda _, a=da: self.button_helper(a))
        dr = gc("date range dialog for rated: string", "drated")
        self.form.pb_date_rated.clicked.connect(lambda _, a=dr: self.button_helper(a))

    def button_helper(self, arg):
        # https://stackoverflow.com/questions/26358945/qt-find-out-if-qspinbox-was-changed-by-user
        self.form.pte.blockSignals(True)
        self._button_helper(arg)
        self.form.pte.blockSignals(False)
        self.raise_()
        self.form.pte.setFocus()
    
    def _button_helper(self, arg):
        all_text = self.form.pte.toPlainText()
        pos = self.form.pte.textCursor().position()
        before = all_text[:pos]
        after = all_text[pos:]

        if after:
            after = " " + after

        if all_text == "" or before.endswith("\n"):  # if empty or on newline
            spacer = ""
        else:
            spacer = "\n"

        new = before + spacer + arg + after
        self.form.pte.setPlainText(new)

        newpos = pos + len(arg) + len(spacer)
        cursor = self.form.pte.textCursor()
        cursor.setPosition(newpos)
        self.form.pte.setTextCursor(cursor)

        self.text_change_helper(before=all_text, before_pos=pos)

    def help_short(self):
        if self.help_dialog:
            tooltip("mini help window is already open (but maybe it's below another window of yours).")
            self.help_dialog.raise_()  # doesn't work on MacOS
        else:
            self.help_dialog = MiniHelpSearch(self)
            self.help_dialog.show()
        #aqt.dialogs.open(mini_search_help_dialog_title, aqt.mw)

    def help_long(self):
        openHelp("searching")

    def on_history(self):
        hist_list = self.parent.mw.pm.profile["searchHistory"]
        processed_list = [split_to_multiline(e) for e in hist_list]
        d = FilterDialog(
            parent=self.parent,
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
            new = split_to_multiline(d.selkey)
            self.form.pte.setPlainText(new)
            self.form.pte.moveCursor(QTextCursor.End)

    def filter_menu(self):
        func_gettext = self.form.pte.toPlainText
        old = func_gettext()
        func_settext = self.form.pte.setPlainText
        d = filter_button_cls(self, self.browser, func_gettext, func_settext, False)
        # detect if closed e.g. with "Esc"
        if not hasattr(d, "txt") or not isinstance(d.txt, str):
            self.form.pte.setFocus()
            return
        self.button_helper(d.txt, False)

    def settext(self):
        processed = split_to_multiline(self.searchstring)
        self.form.pte.setPlainText(processed)
        self.form.pte.setFocus()
        self.form.pte.moveCursor(QTextCursor.End)

    def process_text(self):
        text = self.form.pte.toPlainText()
        return text.replace("\n", " ").replace("\t", " ")

    def text_change_helper(self, before=None, before_pos=None):
        pos = self.form.pte.textCursor().position()
        out = onSearchEditTextChange(
            parent=self.parent,
            move_dialog_in_browser=False,
            include_filtered_in_deck=True,
            func_gettext=self.form.pte.toPlainText,
            func_settext=self.form.pte.setPlainText,
            cursorpos=pos,
            mw=self.browser.mw,
            col=self.browser.col,
            )
        if out:
            cursor = self.form.pte.textCursor()
            cursor.setPosition(out[0])
            self.form.pte.setTextCursor(cursor)
        elif before is not None:
            self.form.pte.setPlainText(before)
            cursor = self.form.pte.textCursor()
            cursor.setPosition(before_pos)
            self.form.pte.setTextCursor(cursor)

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
