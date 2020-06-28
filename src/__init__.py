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



This add-on uses the file fuzzy_panel.py which has this copyright and permission notice:

    Copyright (c): 2018  Rene Schallner
                   2019- ijgnd
        
    This file (fuzzy_panel.py) is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This file is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this file.  If not, see <http://www.gnu.org/licenses/>.
"""



from anki.hooks import wrap, addHook
from anki.utils import pointVersion

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
    move_dialog_in_browser = False
    include_filtered_in_deck = False
    lineedit = self.sender()  # https://stackoverflow.com/a/33981172
    mw = self.mw
    col = self.mw.col
    onSearchEditTextChange(parent, move_dialog_in_browser, include_filtered_in_deck, lineedit.text, lineedit.setText, mw, col, arg)
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
    move_dialog_in_browser = True
    include_filtered_in_deck = True
    lineedit = self.form.searchEdit.lineEdit()
    mw = self.mw
    col = self.col
    dialogclosed = onSearchEditTextChange(parent, move_dialog_in_browser, include_filtered_in_deck, lineedit.text, lineedit.setText, mw, col, arg)
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


def is_values():
    return [
        "is:due",
        "is:new",
        "is:learn",
        "is:review",
        "is:suspended",
        "is:buried",
        "is:learn is:review",
        "-is:learn is:review",
        "is:learn -is:review",
    ]


def is_values_with_explanations():
    return {
    "is:due (review cards and learning cards waiting to be studied)" : "is:due",
    "is:new (new cards)" : "is:new",
    "is:learn (cards in learning)" : "is:learn",
    "is:review (reviews (both due and not due) and lapsed cards)" : "is:review",
    "is:suspended (cards that have been manually suspended)" : "is:suspended",
    "is:buried (cards that have been buried, either automatically (siblings) or manually)" : "is:buried",
    "is:learn is:review (cards that have lapsed and are awaiting relearning)" : "is:learn is:review",
    "-is:learn is:review (review cards, not including lapsed cards)" : "-is:learn is:review",
    "is:learn -is:review (cards that are in learning for the first time)" : "is:learn -is:review",
    }


def props():
    return {
        "prop:due=-1 - cards due yesterday that haven't been answered yet": "prop:due=",
        "prop:due=1 - cards due tomorrow": "prop:due=",
        "prop:due>-1 prop:due<1 - cards due between yesterday and tomorrow": "prop:due> prop:due<",
        "prop:ease!=2.5 - cards easier or harder than default": "prop:ease!=",
        "prop:ivl>=10 - cards with interval of 10 days or more": "prop:ivl>=",
        "prop:lapses>3 - cards that have moved into relearning more than 3 times": "prop:lapses>",
        "prop:reps<10 - cards that have been answered less than 10 times": "prop:reps<",
    }

def overrides():
    # 4 Modifiers = 4 Overrides
    #   SHIFT: override autosearch default
    #   META : override add * default  # originally Ctrl 
    #   ALT  : negate
    #   CTRL : insert current text only : already used in dialog
    lineonly = False
    if conf_to_key[gc("modifier for insert current text only")]():
        lineonly = True
    override_autosearch_default = False
    if conf_to_key[gc("modifier for override autosearch default")]():
        override_autosearch_default = True
    override_add_star = False
    if conf_to_key[gc("modifier for override add * default")]():
        override_add_star = True
    negate = False
    if conf_to_key[gc("modifier for negate")]():
        negate = True
    # print(f"ctrl - lineonly is {lineonly}")
    # print(f"shift - override_autosearch_default is {override_autosearch_default}")
    # print(f"meta - override_add_star is {override_add_star}")
    # print(f"alt - negate is {negate}")
    return lineonly, override_autosearch_default, override_add_star, negate


def onSearchEditTextChange(parent, move_dialog_in_browser, include_filtered_in_deck, func_gettext, func_settext, mw, col, arg):
    vals = False
    c1 = gc("custom tag&deck string 1", "")
    xx1 = c1 and arg[-len(c1):] == c1
    c2 = gc("custom tag&deck string 2", "")
    xx2 = c2 and arg[-len(c2):] == c2
    # vals = (0 remove some characters from the right of searchboxstring, 
    #         1 InsertSpaceAtPos, 
    #         2 UseFilterDialogValue: if True (use a string that describes it) is True, if list is False
    #         3 FilterDialogLines
    #         4 surround search with ""
    #         5 infotext
    #         6 windowtitle
    #        )
    if arg[-5:] == "prop:":
        if gc("modify_props"):
            infotxt = "<b>After closing the dialog you must adjust what's inserted with your numbers</b>"
            vals = (False, -5, "prop", props(), False, infotxt, "Anki: Select properties to search")
        allowstar = False
    if arg[-3:] == "is:":
        if gc("modify_is"):
            if gc("modify_is__show_explanations"):
                vals = (False, -3, "is_with_explanations", is_values_with_explanations(), False, False, "Anki: Search by Card State")
            else:
                vals = (-3, -3, False, is_values(), False, False, "Anki: Search by Card State")
        allowstar = False
    if arg[-4:] == "tag:":
        if gc("modify_tag"):
            vals = (False, -4, False, tags(col), False, False, "Anki: Select tag to search")
        allowstar = True
    elif arg[-5:] == "note:":
        if gc("modify_note"):
            vals = (False, -5, False, col.models.allNames(), True, False, "Anki: Select Note Type to search")
        allowstar = False if pointVersion() < 24 else True
    elif arg[-5:] == "card:":
        if gc("modify_card"):
            cards = set()
            for m in col.models.all():
                for t in m['tmpls']:
                    cards.add(t['name'])
            vals = (False, -5, False, cards, True, False, "Anki: Select Card (Type) Name to search")
        allowstar = False if pointVersion() < 24 else True      
    elif arg == "cfn:":  # cards from note
        d = {}
        for m in col.models.all():
            modelname = m['name']
            for t in m['tmpls']:
                d[t['name'] + " (" + modelname + ")"] = t['name']
        vals = (False, -4, "cfn", d, True, False, "Anki: Select Card (Type) Name from selected Note Type")
        allowstar = False
    elif arg[-5:] == "deck:":
        if gc("modify_deck"):
            vals = (False, -5, False, decknames(col, include_filtered_in_deck), True, False, "Anki: Select Deck to search")
        allowstar = True
    elif xx1:
        alltags = ["tag:" + t for t in tags(col)]
        decks = ["deck:" + d  for d in decknames(col, include_filtered_in_deck)]
        vals = (-len(c1), 0, False, alltags + decks, True, False, "Anki: Select from decks and tags")
        allowstar = True
    elif xx2:
        alltags = ["tag:" + t for t in tags(col)]
        decks = ["deck:" + d  for d in decknames(col, include_filtered_in_deck)]
        vals = (-len(c2), 0, False, alltags + decks, True, False, "Anki: Select from decks and tags")
        allowstar = True

    if vals:
        if gc("autoadjust FilterDialog position", True):
            adjPos = True
        else:
            adjPos = False
        d = FilterDialog(
            parent=parent,
            parent_is_browser=move_dialog_in_browser,
            values=vals[3],
            windowtitle=vals[6],
            adjPos=adjPos,
            allowstar=allowstar,
            infotext=vals[5],
        )
        if d.exec():
            # print('###############################')
            lineonly, override_autosearch_default, override_add_star, negate = overrides()
            if d.lineonly:
                lineonly = True
            # print(f"d.selkey is {d.selkey}")
            # print(f"d.inputline is {d.inputline}")
            # print(f"d.selvalue is {d.selvalue}")
            # print(f"lineonly is {lineonly}")
            # print(f"allowstar is {allowstar}")
            if negate or d.neg:
                neg = "-"
            else:
                neg = ""

            if not vals[0]:
                t = func_gettext()
                n = vals[1]
                # multiple runs of insert_helper are still separated by spaces and in other 
                # situations this makes the search more readable
                # make sure that "-" remains in front of terms like deck
                if len(t[:n]) > 0 and t[:n][-1] == "-":
                    b = t[:n-1] + "  -" + t[n:]
                else:
                    b = t[:n] + "  " + neg + t[n:]  
            else:
                b = neg + func_gettext()[:vals[0]]
            # print(f"b is:  {b}")


            # vals[2] = UseFilterDialogValue: if values tuple with info, if list is False
            # sofar only True for cases where allowstar is always wrong: quick workaround finish here
            if vals[2]:
                if vals[2] == "cfn":
                    mycard = d.selvalue
                    mynote = d.selkey.lstrip(d.selvalue)[1:-1]
                    mysearch = f'''("card:{mycard}" and "note:{mynote}")'''
                    already_in_line = b[:-4]  # substract cfn:
                    func_settext(already_in_line + mysearch)
                    return (True, override_autosearch_default)
                elif vals[2] == "is_with_explanations":
                    already_in_line = b[:-3]  # substract is:
                    func_settext(already_in_line + d.selvalue)
                    return (True, override_autosearch_default)
                elif vals[2] == "prop":
                    already_in_line = b[:-5]  # substract prop:
                    func_settext(already_in_line + d.selvalue)
                    return (True, override_autosearch_default)                         
            else:
                sel = d.selkey
            # print(f"sel is {sel}")
            if lineonly and allowstar:
                if xx1 or xx2:
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
            elif arg[-4:] == "tag:":
                if allowstar and (gc("tag insertion - add '*' to matches") == "all" or d.addstar) and not override_add_star:
                    sel = sel + '*'
                elif allowstar and gc("tag insertion - add '*' to matches") == "if_has_subtags" or d.addstar and not override_add_star:
                    other_subtags_matched = []
                    selplus = sel + "::"
                    for e in vals[3]:
                        if e.startswith(selplus):
                            other_subtags_matched.append(e)
                    if other_subtags_matched:
                        sel = sel + '*'
            # in 2.1.24 card: and note: can also use *
            elif arg[-5:] == "card:":
                if allowstar and (gc("tag insertion - add '*' to matches") == "all" or d.addstar) and not override_add_star:
                    sel = sel + '*'
            elif arg[-5:] == "note:":          
                if allowstar and (gc("tag insertion - add '*' to matches") == "all" or d.addstar) and not override_add_star:
                    sel = sel + '*'
            # ugly fix for xx etc.
            elif (c1 and arg[-len(c1):] == c1) or (c2 and arg[-len(c2):] == c2):
                if allowstar and gc("tag insertion - add '*' to matches") == "all" and not override_add_star:
                    sel = sel + '*'
            elif allowstar and arg[-5:] == "deck:" and gc("modify_deck"):
                 if d.addstar and not override_add_star:
                     sel = sel + '*'
            if vals[4]:  # surround with ""
                sel = '"' + sel + '"'
            func_settext(b + sel)
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
    d = FilterDialog(parent=self, parent_is_browser=True, values=vals[2], adjPos=adjPos, allowstar=allowstar)
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
addHook("browser.setupMenus", setupMenu)
