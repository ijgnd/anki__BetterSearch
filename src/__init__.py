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

from .fuzzy_panel import FilterDialog


def gc(arg, fail=False):
    conf = aqt.mw.addonManager.getConfig(__name__)
    if conf:
        return conf.get(arg, fail)
    else:
        return fail


tup = None
def check_for_advancedBrowser():
    global tup
    try:
        __import__("874215009").advancedbrowser.core.AdvancedBrowser
    except:
        tup = Browser
    else:
        tup = (AdvancedBrowser, Browser)
addHook("profileLoaded", check_for_advancedBrowser)


def warn_on_night_mode_change():
    # add-on "Opening the same window multiple time"
    try:
        aqt.dialogs._openDialogs
    except:
        addon = False
    else:
        addon = True

    if addon:
        browsers = []
        for e in aqt.dialogs._openDialogs:
            if isinstance(e, tup):
                browsers.append(e)
    else:
        if aqt.dialogs._dialogs["Browser"][1]:
            browsers = True
        else:
            browsers = False

    if browsers:
        t = ("You changed the night mode state while a Browser window is open. Close all Browser "
             "windows and reopen them. Otherwise the dialog of the add-on 'Browser Search Box: "
             "Quick Insert Tag, Deck, Notetype' will have broken colors.")
        showCritical(t)


night_mode_on = False
def refresh_night_mode_state(nm_state):
    global night_mode_on
    prior = night_mode_on
    night_mode_on = nm_state
    if nm_state != prior:
        warn_on_night_mode_change()
addHook("night_mode_state_changed", refresh_night_mode_state)


def mysearch(self):
    self.form.searchEdit.editTextChanged.connect(self.onSearchEditTextChange)
Browser.setupSearch = wrap(Browser.setupSearch,mysearch)


def onSearchEditTextChange(self, arg):
    le = self.form.searchEdit.lineEdit()
    vals = False
    c1 = gc("custom tag&deck string 1", "")
    c2 = gc("custom tag&deck string 2", "")
    # vals = (remove some characters from the right of searchboxstring, 
    #         InsertSpaceAtPos, 
    #         UseFilterDialogKey(orValue),
    #         ListForFilterDialog)
    if arg[-4:] == "tag:":
        if gc("modify_tag"):
            vals = (False, -4, True, self.col.tags.all())
    elif arg[-5:] == "note:":
        if gc("modify_note"):
            vals = (False, -5, True, self.col.models.allNames())
    elif arg[-5:] == "card:":
        if gc("modify_card"):
            d = {}
            for m in self.col.models.all():
                modelname = m['name']
                for t in m['tmpls']:
                    d[t['name'] + " (" + modelname + ")"] = t['name']
            vals = (False, -5, False, d)
    elif arg[-5:] == "deck:":
        if gc("modify_deck"):
            vals = (False, -5, True, sorted(self.col.decks.allNames()))
    elif c1 and arg[-len(c1):] == c1:
            alltags = ["tag:" + t for t in self.mw.col.tags.all()]
            decks = ["deck:" + d  for d in sorted(self.col.decks.allNames())]
            vals = (-len(c1), 0, True, alltags + decks)
    elif c2 and arg[-len(c2):] == c2:
            alltags = ["tag:" + t for t in self.mw.col.tags.all()]
            decks = ["deck:" + d  for d in sorted(self.col.decks.allNames())]
            vals = (-len(c2), 0, True, alltags + decks)
    if vals:
        d = FilterDialog(parent=self, values=vals[3], nm=night_mode_on)
        if d.exec():
            shiftmod = self.mw.app.keyboardModifiers() & Qt.ShiftModifier
            ctrlmod = self.mw.app.keyboardModifiers() & Qt.ControlModifier
            if not vals[0]:
                t = le.text()
                n = vals[1]
                # multiple runs of insert_helper are still separated by spaces and in other 
                # situations this makes the search more readable
                # make sure that "-" remains in front of terms like deck
                if len(t[:n]) > 0 and t[:n][-1] == "-":
                    b = t[:n-1] + "  -" + t[n:]
                else:
                    b = t[:n] + "  " + t[n:]  
            else:
                b = le.text()[:vals[0]]
            if vals[2]:
                sel = d.selkey
            else:
                sel = d.selvalue
            # maybe add '*' to match other deeper nested hierarchical tags
            if arg[-4:] == "tag:":
                if gc("tag insertion - add '*' to matches") == "all" and not ctrlmod:
                    sel = sel + '*'
                elif gc("tag insertion - add '*' to matches") == "if_has_subtags" and not ctrlmod:
                    other_subtags_matched = []
                    selplus = sel + "::"
                    for e in vals[3]:
                        if e.startswith(selplus):
                            other_subtags_matched.append(e)
                    if other_subtags_matched:
                        sel = sel + '*'
            le.setText(b + '"' + sel + '"')
Browser.onSearchEditTextChange = onSearchEditTextChange


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


def insert_helper(self, arg):
    le = self.form.searchEdit.lineEdit()
    # vals = (insert arg into searchboxstring, 
    #         UseFilterDialogKey(False means Value),
    #         ListForFilterDialog)
    if arg == "tag:":
        vals = (True, True, self.col.tags.all())
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
        vals = (True, True, sorted(self.col.decks.allNames()))
    elif arg == "xx":
        alltags = ["tag:" + t for t in self.mw.col.tags.all()]
        decks = ["deck:" + d  for d in sorted(self.col.decks.allNames())]
        vals = (False, True, alltags + decks)
    d = FilterDialog(parent=self, values=vals[2], nm=night_mode_on)
    if d.exec():
        shiftmod = self.mw.app.keyboardModifiers() & Qt.ShiftModifier
        ctrlmod = self.mw.app.keyboardModifiers() & Qt.ControlModifier
        altmod = self.mw.app.keyboardModifiers() & Qt.AltModifier
        t = le.text()
        # clear preset text if necessary
        if t == self._searchPrompt:
            t = ""
        if vals[1]:
            sel = d.selkey
        else:
            sel = d.selvalue
        # maybe add '*' to match other deeper nested hierarchical tags
        if arg == "tag:":
            if gc("tag insertion - add '*' to matches") == "all" and not ctrlmod:
                sel = sel + '*'
            elif gc("tag insertion - add '*' to matches") == "if_has_subtags" and not ctrlmod:
                other_subtags_matched = []
                selplus = sel + "::"
                for e in vals[2]:
                    if e.startswith(selplus):
                        other_subtags_matched.append(e)
                if other_subtags_matched:
                    sel = sel + '*'
        if altmod:
            neg = "-"
        else:
            neg = ""
        if vals[0]:
            nt = t + "  " + neg + arg + '"' + sel + '"'
        else:
            nt = t + "  " + neg +       '"' + sel + '"'
        le.setText(nt)
        # shiftmod toggle default search trigger setting 
        if gc("shortcuts trigger search by default"):
            if not shiftmod:
                self.onSearchActivated()
        else:
            if shiftmod:
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
