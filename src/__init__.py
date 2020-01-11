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


from anki.hooks import wrap 

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
    if arg[-4:] == "tag:":
        if gc("modify_tag"):
            vals = (False, True, self.col.tags.all())
    elif arg[-5:] == "note:":
        if gc("modify_note"):
            vals = (False, True, self.col.models.allNames())
    elif arg[-5:] == "card:":
        if gc("modify_card"):
            d = {}
            for m in self.col.models.all():
                modelname = m['name']
                for t in m['tmpls']:
                    d[t['name'] + " (" + modelname + ")"] = t['name']
            vals = (False, False, d)
    elif arg[-5:] == "deck:":
        if gc("modify_deck"):
            vals = (False, True, sorted(self.col.decks.allNames()))
    elif c1 and arg[-len(c1):] == c1:
            alltags = ["tag:" + t for t in self.mw.col.tags.all()]
            decks = ["deck:" + d  for d in sorted(self.col.decks.allNames())]
            vals = (-len(c1), True, alltags + decks)
    elif c2 and arg[-len(c2):] == c2:
            alltags = ["tag:" + t for t in self.mw.col.tags.all()]
            decks = ["deck:" + d  for d in sorted(self.col.decks.allNames())]
            vals = (-len(c2), True, alltags + decks)
    if vals:
        d = FilterDialog(parent=self, values=vals[2])
        if d.exec():
            if not vals[0]:
                b = le.text()
            else:
                b = le.text()[:vals[0]]
            if vals[1]:
                i = d.selkey
            else:
                i = d.selvalue
            le.setText(b + '"' + i + '"')
Browser.onSearchEditTextChange = onSearchEditTextChange
