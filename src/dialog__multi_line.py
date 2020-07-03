from anki.utils import pointVersion

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
        self.form.pb_nc.clicked.connect(self.note__card)
        self.form.pb_nf.clicked.connect(self.note__field)
        self.form.pb_deck.clicked.connect(lambda _, action="deck:": self.button_helper(action))
        self.form.pb_tag.clicked.connect(lambda _, action="tag:": self.button_helper(action))
        self.form.pb_card_props.clicked.connect(lambda _, action="prop:": self.button_helper(action))
        self.form.pb_card_state.clicked.connect(lambda _, action="is:": self.button_helper(action))
        self.form.pb_date_added.clicked.connect(lambda _, action=gc("date range dialog for added: string", "dadded"): self.button_helper(action))
        self.form.pb_date_rated.clicked.connect(lambda _, action=gc("date range dialog for rated: string", "drated"): self.button_helper(action))

    def button_helper(self, arg):
        # https://stackoverflow.com/questions/26358945/qt-find-out-if-qspinbox-was-changed-by-user
        self.form.pte.blockSignals(True)
        self._button_helper(arg)
        self.form.pte.blockSignals(False)
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

    def run_filter_dialog(self, vals, vals_are_dict, value_for_all, windowtitle, infotext, prefix, sort_vals):
        d = FilterDialog(
            parent=self.parent,
            parent_is_browser=True,
            values=vals,
            windowtitle=windowtitle,
            adjPos=False,
            show_star=True,
            check_star=False,
            infotext=infotext,
            show_prepend_minus_button=True,
            check_prepend_minus_button=False,
            sort_vals=sort_vals
        )
        if not d.exec():
            return None, None, None
        else:
            if d.selkey == value_for_all:
                return d.selkey, ""
            lineonly, _, override_add_star, negate = overrides()
            if d.lineonly:
                lineonly = True
            if override_add_star:
                d.addstar ^= True
            out = d.selvalue if vals_are_dict else d.selkey
            if lineonly or d.addstar:
                out += "*"
            out = prefix + out
            neg = True if (negate or d.neg) else False
            return d.selkey, out, neg

    def note_filter_helper(self, remaining_sentence):
        infotext = (f"""
<span>
In a first step select the note type to search. After this you'll see a dialog to narrow 
by {remaining_sentence}
</span>
""")
        val, fmt, neg = self.run_filter_dialog(
            vals=["--All Note Types--"] + self.col.models.allNames(),
            vals_are_dict=False,
            value_for_all="--All Note Types--",
            windowtitle="Anki: Step 1: Select Note Type to search",
            infotext=infotext,
            prefix="note:",
            sort_vals=True,
        )
        return val, fmt, neg

    def note__card(self):
        remaining = "card template name if the note has multiple cards." 
        model, model_search_string, modelneg = self.note_filter_helper(remaining)
        if not model:
            return

        infotext = ("""
<span>
After having selected the note types to search now select the
card template/type/name you want to search.
</span>
""")
        iscloze = False
        show_card_dialog = True
        if not model_search_string:
            # then from all notetypes
            vals = cardnames(self.col)
            vals_are_dict = False
            sort_vals = True
        else:
            # for one note type
            sort_vals = False
            nt = self.col.models.byName(model)
            if nt["type"] == 1:  # it's a cloze and for cloze it doesn't make sense to show a list
                                 # of cards
                show_card_dialog = False
                iscloze = True
            else:
                card_name_to_fmt_dict = {}
                for c, tmpl in enumerate(nt["tmpls"]):
                    # T: name is a card type name. n it's order in the list of card type.
                    name = tmpl["name"]
                    n = str(c + 1)
                    fmt = f"{n.zfill(2)}: {name}"
                    card_name_to_fmt_dict[fmt] = name
                default_fake_dict = {"--All the Card Types--":"--All the Card Types--"}
                vals = {**default_fake_dict, **card_name_to_fmt_dict}
                vals_are_dict = True
                if c == 0:  # only one card type 
                    show_card_dialog = False
        if not show_card_dialog:
            card_string = ""
            cardneg = False
        else:
            card, card_string, cardneg = self.run_filter_dialog(
                vals=vals,
                vals_are_dict=vals_are_dict,
                value_for_all="--All the Card Types--",
                windowtitle="Anki: Step 2: Select Card Type to search",
                infotext=infotext,
                prefix="card:",
                sort_vals=sort_vals,
            )
            if not card:
                return


        if " " in model_search_string:
            model_search_string = '"' + model_search_string + '"'
        if model_search_string:
            model_search_string += " "
        if " " in card_string:
            card_string = '"' + card_string + '"'
        out = '(' + model_search_string + card_string + ')'
        if modelneg or cardneg:
            out = "-" + out
        self.button_helper(out)
        if iscloze:
            msg = ("""
You selected a cloze note type. To match only c2 clozes type you would have to 
add&nbsp;&nbsp;card:2&nbsp;&nbsp;
"""
            )
            tooltip(msg, parent=self)  # default is period=3000

    def note__field(self):
        remaining = "field (if the note has more than one field)." 
        model, model_search_string, modelneg = self.note_filter_helper(remaining)
        if not model:
            return

        infotext = ("""
<span>
After having selected the note type to search now select the field name you want 
to search. After closing this dialog the text inserted will be "fieldname:**" 
which doesn't limit your search yet. You must <b>adjust</b> this search and
 add some text to limit to a certain term.
<span>
""")
        show_card_dialog = True
        if not model_search_string:
            # then from all notetypes
            fnames = fieldnames()
            value_for_all = False
        else:
            # for one note type
            nt = self.col.models.byName(model)
            fnames = [fld["name"] for fld in nt["flds"]]
            if not len(fnames) > 1:
                show_card_dialog = False
            value_for_all="--All the Card Types--"
            fnames.insert(0, value_for_all)
        if not show_card_dialog:
            field_string = ""
            fieldneg = False
        else:
            field, field_string, fieldneg = self.run_filter_dialog(
                vals=fnames,
                vals_are_dict=False,
                value_for_all=value_for_all,
                windowtitle="Anki: Step 2: Select Field Name to search",
                infotext=infotext,
                prefix="",
                sort_vals=False
            )
            if not field:
                return

        if " " in model_search_string:
            model_search_string = '"' + model_search_string + '"'
        if model_search_string:
            model_search_string += " "
        if field_string:
            field_string += ":**"
        if " " in field_string:
            field_string = '"' + field_string + '"'
        out = '(' + model_search_string + field_string + ')'
        if modelneg or fieldneg:
            out = "-" + out
        self.button_helper(out)

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
        self.button_helper(d.txt)

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

        le = self.browser.form.searchEdit.lineEdit()
        le.setText(self.newsearch)
        le.setFocus()
        self.browser.onSearchActivated()
        
        QDialog.accept(self)
