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

from aqt import mw
from aqt.browser import Browser
from aqt.qt import *
from aqt.utils import getText

from .fuzzy_panel import FilterDialog


def gc(arg, fail=False):
    conf = mw.addonManager.getConfig(__name__)
    if conf:
        return conf.get(arg, fail)
    else:
        return fail


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
        d = FilterDialog(parent=self, values=vals[3])
        if d.exec():
            if not vals[0]:
                t = le.text()
                n = vals[1]
                # multiple runs of insert_helper are still separated by spaces and in other 
                # situations this makes the search more readable
                b = t[:n] + " " + t[n:]  
            else:
                b = le.text()[:vals[0]]
            if vals[2]:
                i = d.selkey
            else:
                i = d.selvalue
            le.setText(b + '"' + i + '"')
Browser.onSearchEditTextChange = onSearchEditTextChange


def insert_helper(self, val):
    l = self.form.searchEdit.lineEdit()
    if l.text() == self._searchPrompt:
        l.setText(val)
    else:
        l.setText(l.text() + val)
    mod = self.mw.app.keyboardModifiers() & Qt.ShiftModifier
    if gc("shortcuts trigger search by default"):
        if not mod:
            self.onSearchActivated()
    else:
        if mod:
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
        d.activated.connect(lambda b=browser: insert_helper(b, gc("custom tag&deck string 1", "xx")))
    c5 = gc("shortcut - focus search box and deck selector dialog")
    if c5:
        e = QShortcut(QKeySequence(c5), browser)
        e.activated.connect(lambda b=browser: insert_helper(b, "deck:"))
addHook("browser.setupMenus", setupMenu)
