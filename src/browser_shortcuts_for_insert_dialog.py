# DEPRECATED. NO LONGER DEVELOPED


from anki.utils import pointVersion

from aqt.gui_hooks import (
    browser_menus_did_init,
)
from aqt.qt import (
    QKeySequence,
    QShortcut,
)

from .config import gc
from .fuzzy_panel import FilterDialog
from .helpers import (
    decknames,
    overrides,
    tags,
)

# doesn't work: when I press cancel the dialog is opened once more and if I cancel val remains
# in the search bar
# def insert_helper(self, val):
#     l = self.form.searchEdit.lineEdit()
#     if l.text() == self._searchPrompt:
#         l.setText(val)
#     else:
#         l.setText(l.text() + val)
#     mod = self.mw.app.keyboardModifiers() & Qt.ShiftModifier
#     if gc("shortcuts trigger search by default"):
#         if not mod:
#             self.onSearchActivated()
#     else:
#         if mod:
#             self.onSearchActivated()


# TODO maybe remerge with onSearchEditTextChange 
def _insert_helper(self, arg):
    # self is browser
    le = self.form.searchEdit.lineEdit()
    # vals = (insert arg into searchboxstring, 
    #         UseFilterDialogKey(False means Value),
    #         ListForFilterDialog)
    if arg == "tag:":
        vals = (True, True, tags(self.col))
        allowstar = True
    elif arg == "note:":
        vals = (True, True, self.col.models.allNames())
        allowstar = False if pointVersion() < 24 else True
    elif arg == "card:":
        cards = set()
        for m in self.col.models.all():
            for t in m['tmpls']:
                cards.add(t['name'])
        vals = (True, True, cards)
        allowstar = False if pointVersion() < 24 else True      
    elif arg == "cfn:":
        d = {}
        for m in self.col.models.all():
            modelname = m['name']
            for t in m['tmpls']:
                d[t['name'] + " (" + modelname + ")"] = t['name']
        vals = (True, False, d)
        allowstar = False
    elif arg == "deck:":
        vals = (True, True, decknames(self.col, True))
        allowstar = True
    elif arg == "xx":
        alltags = ["tag:" + t for t in tags(self.col)]
        decks = ["deck:" + d  for d in decknames(self.col, True)]
        vals = (False, True, alltags + decks)
        allowstar = True
    if gc("autoadjust FilterDialog position", True):
        adjPos = True
    else:
        adjPos = False
    d = FilterDialog(
        parent=self,
        parent_is_browser=True,
        values=vals[2],
        adjPos=adjPos,
        show_star=allowstar,
        check_star=False,
    )
    if d.exec():
        lineonly, override_autosearch_default, override_add_star, negate = overrides()
        if d.lineonly:
            lineonly = True

        t = le.text()
        # clear preset text if necessary
        if t == self._searchPrompt:
            t = ""
        if vals[1]:
            sel = d.selkey
        else:
            sel = d.selvalue
        if lineonly and allowstar:
            if arg == "xx":
                # I need to add tag or deck
                if d.selkey.startswith("tag:"):
                    sel = "tag:" + d.inputline
                else:
                    sel = "deck:" + d.inputline
            else:
                sel = d.inputline
        # maybe add '*' to match other deeper nested hierarchical tags
        if sel in ["none", "filtered", "tag:none", "deck:filtered"]:
            pass
        elif arg == "tag:":
            if allowstar and (gc("tag insertion - add '*' to matches") == "all" or d.addstar) and not override_add_star:
                sel = sel + '*'
            elif allowstar and gc("tag insertion - add '*' to matches") == "if_has_subtags" or d.addstar and not override_add_star:
                other_subtags_matched = []
                selplus = sel + "::"
                for e in vals[2]:
                    if e.startswith(selplus):
                        other_subtags_matched.append(e)
                if other_subtags_matched:
                    sel = sel + '*'
        elif allowstar and arg == "deck:" and gc("modify_deck"):
            if d.addstar and not override_add_star:
                sel = sel + '*'
        # in 2.1.24 card: and note: can also use *
        elif arg == "card:":
            if allowstar and (gc("tag insertion - add '*' to matches") == "all" or d.addstar) and not override_add_star:
                sel = sel + '*'
        elif arg == "note:":          
            if allowstar and (gc("tag insertion - add '*' to matches") == "all" or d.addstar) and not override_add_star:
                sel = sel + '*'
        # ugly fix for xx etc.
        elif allowstar and arg == "xx" and gc("modify_deck"):
            if d.addstar and not override_add_star:
                sel = sel + '*'

        if negate or d.neg:
            neg = "-"
        else:
            neg = ""
        if vals[0]:
            nt = t + "  " + neg + arg + '"' + sel + '"'
        else:
            nt = t + "  " + neg +       '"' + sel + '"'
        le.setText(nt)
        return override_autosearch_default


def insert_helper(self, arg):
    override_autosearch_default = _insert_helper(self, arg)
    # shiftmod toggle default search trigger setting 
    if gc("shortcuts trigger search by default"):
        if not override_autosearch_default:
            self.onSearchActivated()
    else:
        if override_autosearch_default:
            self.onSearchActivated()


def setupMenu(browser):
    c1 = gc("shortcut - focus search box and card selector dialog")
    if c1:
        a = QShortcut(QKeySequence(c1), browser)
        a.activated.connect(lambda b=browser: insert_helper(b, "card:"))
    c2 = gc("shortcut - focus search box and note selector dialog")
    if c2:
        b = QShortcut(QKeySequence(c2), browser)
        b.activated.connect(lambda b=browser: insert_helper(b, "note:"))
    c3 = gc("shortcut - focus search box and tag selector dialog")
    if c3:
        c = QShortcut(QKeySequence(c3), browser)
        c.activated.connect(lambda b=browser: insert_helper(b, "tag:"))
    c4 = gc("shortcut - focus search box and tag/deck selector dialog")
    if c4:
        d = QShortcut(QKeySequence(c4), browser)
        d.activated.connect(lambda b=browser: insert_helper(b, "xx"))
    c5 = gc("shortcut - focus search box and deck selector dialog")
    if c5:
        e = QShortcut(QKeySequence(c5), browser)
        e.activated.connect(lambda b=browser: insert_helper(b, "deck:"))
browser_menus_did_init.append(setupMenu)
