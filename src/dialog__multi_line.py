from anki.utils import pointVersion

import aqt
from aqt.qt import (
    QDialog,
    QKeySequence,
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
from .dialog__help import MiniHelpSearch, mini_search_help_dialog_title
from .filter_button import filter_button_cls
from .forms import search_box
from .fuzzy_panel import FilterDialog
from .helpers import (
    # this is the order in helpers.py
    cardnames,
    decknames,
    tags,
    is_values,
    is_values_with_explanations,
    props,
    fieldnames,
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
        if searchstring == "<type here to search; hit enter to show current deck>":
            self.searchstring = ""
        else:
            self.searchstring = searchstring
        self.parent = browser
        self.browser = browser
        QDialog.__init__(self, self.parent, Qt.Window)
        self.form = search_box.Ui_Dialog()
        self.form.setupUi(self)
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
            self.form.pb_note_type.setVisible(False)
            self.form.pb_card.setVisible(False)
            self.form.pb_field.setVisible(False)
            self.form.pb_deck.setVisible(False)
            self.form.pb_tag.setVisible(False)
            self.form.pb_card_props.setVisible(False)
            self.form.pb_card_state.setVisible(False)
            self.form.pb_date_added.setVisible(False)
            self.form.pb_date_rated.setVisible(False)

        self.form.pb_note_type.setToolTip("note:")
        self.form.pb_card.setToolTip("card:")
        self.form.pb_field.setToolTip("field:")
        self.form.pb_deck.setToolTip("deck:")
        self.form.pb_tag.setToolTip("tag:")
        self.form.pb_card_props.setToolTip("prop:")
        self.form.pb_card_state.setToolTip("is:")
        st = gc("date range dialog for added: string")
        self.form.pb_date_added.setToolTip(st)
        st = gc("date range dialog for rated: string")
        self.form.pb_date_rated.setToolTip(st)

    def config_pte(self):
        self.form.pte.setTabStopDistance(20)

    def makeConnections(self):
        self.form.pte.textChanged.connect(self.text_change_helper)
        self.form.pb_note_type.clicked.connect(lambda _, action="note:": self.button_helper(action))
        self.form.pb_card.clicked.connect(lambda _, action="card:": self.button_helper(action))
        self.form.pb_field.clicked.connect(lambda _, action="field:": self.button_helper(action))
        self.form.pb_deck.clicked.connect(lambda _, action="deck:": self.button_helper(action))
        self.form.pb_tag.clicked.connect(lambda _, action="tag:": self.button_helper(action))
        self.form.pb_card_props.clicked.connect(lambda _, action="prop:": self.button_helper(action))
        self.form.pb_card_state.clicked.connect(lambda _, action="is:": self.button_helper(action))
        self.form.pb_date_added.clicked.connect(lambda _, action=gc("date range dialog for added: string", "dadded"): self.button_helper(action))
        self.form.pb_date_rated.clicked.connect(lambda _, action=gc("date range dialog for rated: string", "drated"): self.button_helper(action))

    def button_helper(self, arg):
        old = self.form.pte.toPlainText()
        new = old + "\n" + arg
        self.form.pte.setPlainText(new)
        self.form.pte.setFocus()

    def filter_helper(self, vals, wintitle, allowstar, infotext, show_minus):
        d = FilterDialog(
            parent=self.parent,
            parent_is_browser=True,
            values=vals,
            windowtitle=wintitle,
            adjPos=False,
            allowstar=allowstar,
            infotext=infotext,
            show_prepend_minus_button=show_minus,
        )
        if d.exec():
            new = split_to_multiline(d.selkey)
            self.form.pte.setPlainText(new)
            self.form.pte.moveCursor(QTextCursor.End)

    def help_short(self):
        MiniHelpSearch(self)
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
            allowstar=False,
            infotext=False,
            show_prepend_minus_button=False,
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
        # TODO: properly format
        oldlines = old.split("\n")
        if oldlines[-1]:
            old = old + "\n"
        func_settext(old + d.txt)
        self.form.pte.setFocus()
        self.form.pte.moveCursor(QTextCursor.End)

        # TODO
        #new = split_to_multiline(old + d.txt)
        #self.form.pte.setPlainText(new)
        #self.form.pte.setFocus()

    def settext(self):
        processed = split_to_multiline(self.searchstring)
        self.form.pte.setPlainText(processed)
        self.form.pte.setFocus()
        self.form.pte.moveCursor(QTextCursor.End)

    def process_text(self):
        text = self.form.pte.toPlainText()
        return text.replace("\n", " ").replace("\t", " ")

    def text_change_helper(self):
        out = onSearchEditTextChange(
            parent=self.parent,
            move_dialog_in_browser=False,
            include_filtered_in_deck=True,
            func_gettext=self.form.pte.toPlainText,
            func_settext=self.form.pte.setPlainText,
            mw=self.browser.mw,
            col=self.browser.col,
            arg=self.form.pte.toPlainText(),
            )
        if out:
            self.form.pte.moveCursor(QTextCursor.End)

    def reject(self):
        saveGeom(self, searchbox_geom_name)
        QDialog.reject(self)

    def accept(self):
        saveGeom(self, searchbox_geom_name)
        self.newsearch = self.process_text()
        QDialog.accept(self)
