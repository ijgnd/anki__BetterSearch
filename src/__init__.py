"""
Add-on for Anki
Copyright (c): 2020 ijgnd


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


from anki.hooks import wrap, addHook

import aqt
from aqt.browser import Browser
from aqt.qt import *
from aqt.utils import getText, showCritical
from aqt.dyndeckconf import DeckConf

from .config import conf_to_key, gc, shiftdown, ctrldown, altdown, metadown
from .fuzzy_panel import FilterDialog


def dyn_setup_search(self):
    self.form.search.textChanged.connect(self.onDynSetupSearchEditTextChange)
    self.form.search_2.textChanged.connect(self.onDynSetupSearchEditTextChange)
DeckConf.initialSetup = wrap(DeckConf.initialSetup, dyn_setup_search)


def onDynSetupSearchEditTextChange(self, arg):
    parent = self
    parent_is_browser = False
    lineedit = self.sender()  # https://stackoverflow.com/a/33981172
    mw = self.mw
    col = self.mw.col
    onSearchEditTextChange(parent, parent_is_browser, lineedit, mw, col, arg)
DeckConf.onDynSetupSearchEditTextChange = onDynSetupSearchEditTextChange


tup = None
def check_for_advancedBrowser():
    global tup
    try:
        a = __import__("874215009").advancedbrowser.core.AdvancedBrowser
    except:
        tup = Browser
    else: 
        tup = (a, Browser)
addHook("profileLoaded", check_for_advancedBrowser)


def mysearch(self):
    self.form.searchEdit.editTextChanged.connect(self.onBrowserSearchEditTextChange)
Browser.setupSearch = wrap(Browser.setupSearch,mysearch)


def onBrowserSearchEditTextChange(self, arg):
    parent = self
    parent_is_browser = True
    lineedit = self.form.searchEdit.lineEdit()
    mw = self.mw
    col = self.col
    dialogclosed = onSearchEditTextChange(parent, parent_is_browser, lineedit, mw, col, arg)
    if dialogclosed and dialogclosed[1]:
        self.onSearchActivated()
Browser.onBrowserSearchEditTextChange = onBrowserSearchEditTextChange


def decknames(col, also_include_filtered):
    decks = col.decks.allNames(dyn=also_include_filtered)
    # also_include_filtered only True in the browser but not in the Create Filtered Deck dialog
    # Filtered decks can't include filtered decks so I don't want "filtered" for those.
    if also_include_filtered:  
        decks += ["filtered"]
    return sorted(decks)


def tags(col):
    tags = col.tags.all() + ["none"]
    return sorted(tags)


def overrides():
    # 4 Modifiers = 4 Overrides
    #   SHIFT: override autosearch default
    #   META : override add * default  # originally Ctrl 
    #   ALT  : negate
    #   CTRL : insert current text only : already used in dialog
    override_autosearch_default = False
    if conf_to_key[gc("modifier for override autosearch default")]():
        override_autosearch_default = True
    override_add_star = False
    if conf_to_key[gc("modifier for override add * default")]():
        override_add_star = True
    negate = False
    if conf_to_key[gc("modifier for negate")]():
        negate = True
    # print(f"shift - override_autosearch_default is {override_autosearch_default}")
    # print(f"meta - override_add_star is {override_add_star}")
    # print(f"alt - negate is {negate}")
    return override_autosearch_default, override_add_star, negate


def onSearchEditTextChange(parent, parent_is_browser, lineedit, mw, col, arg):
    le = lineedit
    vals = False
    c1 = gc("custom tag&deck string 1", "")
    c2 = gc("custom tag&deck string 2", "")
    # vals = (remove some characters from the right of searchboxstring, 
    #         InsertSpaceAtPos, 
    #         UseFilterDialogKey(orValue),
    #         ListForFilterDialog)
    if arg[-4:] == "tag:":
        if gc("modify_tag"):
            vals = (False, -4, True, tags(col))
    elif arg[-5:] == "note:":
        if gc("modify_note"):
            vals = (False, -5, True, col.models.allNames())
    elif arg[-5:] == "card:":
        if gc("modify_card"):
            d = {}
            for m in col.models.all():
                modelname = m['name']
                for t in m['tmpls']:
                    d[t['name'] + " (" + modelname + ")"] = t['name']
            vals = (False, -5, False, d)
    elif arg[-5:] == "deck:":
        if gc("modify_deck"):
            vals = (False, -5, True, decknames(col, parent_is_browser))
    elif c1 and arg[-len(c1):] == c1:
        alltags = ["tag:" + t for t in tags(col)]
        decks = ["deck:" + d  for d in decknames(col, parent_is_browser)]
        vals = (-len(c1), 0, True, alltags + decks)
    elif c2 and arg[-len(c2):] == c2:
        alltags = ["tag:" + t for t in tags(col)]
        decks = ["deck:" + d  for d in decknames(col, parent_is_browser)]
        vals = (-len(c2), 0, True, alltags + decks)
    if vals:
        if gc("autoadjust FilterDialog position", True):
            adjPos = True
        else:
            adjPos = False
        d = FilterDialog(parent=parent, parent_is_browser=parent_is_browser, values=vals[3], adjPos=adjPos)
        if d.exec():
            override_autosearch_default, override_add_star, negate = overrides()
            if negate or d.neg:
                neg = "-"
            else:
                neg = ""
            if not vals[0]:
                t = le.text()
                n = vals[1]
                # multiple runs of insert_helper are still separated by spaces and in other 
                # situations this makes the search more readable
                # make sure that "-" remains in front of terms like deck
                if len(t[:n]) > 0 and t[:n][-1] == "-":
                    b = t[:n-1] + "  -" + t[n:]
                else:
                    b = t[:n] + "  " + neg + t[n:]  
            else:
                b = neg + le.text()[:vals[0]]
            if vals[2]:
                sel = d.selkey
            else:
                sel = d.selvalue
            # maybe add '*' to match other deeper nested hierarchical tags
            if sel in ["none", "filtered", "tag:none", "deck:filtered"]:
                pass
            elif arg[-4:] == "tag:":
                if (gc("tag insertion - add '*' to matches") == "all" or d.addstar) and not override_add_star:
                    sel = sel + '*'
                elif gc("tag insertion - add '*' to matches") == "if_has_subtags" or d.addstar and not override_add_star:
                    other_subtags_matched = []
                    selplus = sel + "::"
                    for e in vals[3]:
                        if e.startswith(selplus):
                            other_subtags_matched.append(e)
                    if other_subtags_matched:
                        sel = sel + '*'
            # ugly fix for xx etc.
            elif (c1 and arg[-len(c1):] == c1) or (c2 and arg[-len(c2):] == c2):
                if gc("tag insertion - add '*' to matches") == "all" and not override_add_star:
                    sel = sel + '*'
            elif arg[-5:] == "deck:" and gc("modify_deck"):
                 if not override_add_star:
                     sel = sel + '*'
            le.setText(b + '"' + sel + '"')
            return (True, override_autosearch_default)  # shiftmod toggle default search trigger setting 


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
    le = self.form.searchEdit.lineEdit()
    # vals = (insert arg into searchboxstring, 
    #         UseFilterDialogKey(False means Value),
    #         ListForFilterDialog)
    if arg == "tag:":
        vals = (True, True, tags(self.col))
    elif arg == "note:":
        vals = (True, True, self.col.models.allNames())
    elif arg == "card:":
        d = {}
        for m in self.col.models.all():
            modelname = m['name']
            for t in m['tmpls']:
                d[t['name'] + " (" + modelname + ")"] = t['name']
        vals = (True, False, d)
    elif arg == "deck:":
        vals = (True, True, decknames(self.col, True))
    elif arg == "xx":
        alltags = ["tag:" + t for t in tags(self.col)]
        decks = ["deck:" + d  for d in decknames(self.col, True)]
        vals = (False, True, alltags + decks)
    if gc("autoadjust FilterDialog position", True):
        adjPos = True
    else:
        adjPos = False
    d = FilterDialog(parent=self, parent_is_browser=True, values=vals[2], adjPos=adjPos)
    if d.exec():
        override_autosearch_default, override_add_star, negate = overrides()

        t = le.text()
        # clear preset text if necessary
        if t == self._searchPrompt:
            t = ""
        if vals[1]:
            sel = d.selkey
        else:
            sel = d.selvalue

        # maybe add '*' to match other deeper nested hierarchical tags
        if sel in ["none", "filtered", "tag:none", "deck:filtered"]:
            pass
        elif arg == "tag:":
            if (gc("tag insertion - add '*' to matches") == "all" or d.addstar) and not override_add_star:
                sel = sel + '*'
            elif gc("tag insertion - add '*' to matches") == "if_has_subtags" or d.addstar and not override_add_star:
                other_subtags_matched = []
                selplus = sel + "::"
                for e in vals[2]:
                    if e.startswith(selplus):
                        other_subtags_matched.append(e)
                if other_subtags_matched:
                    sel = sel + '*'
        elif arg == "deck:" and gc("modify_deck"):
            sel = sel + '*'
        # ugly fix for xx etc.
        elif arg == "xx" and gc("modify_deck"):
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
addHook("browser.setupMenus", setupMenu)
