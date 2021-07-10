# -*- coding: utf-8 -*-
# this file contains code extracted from aqt.browser.py
# Copyright: 2020 ijgnd
#            Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


from anki.decks import DeckManager
from anki.lang import _
from anki.rsbackend import TR
from anki.utils import pointVersion

from aqt.qt import (
    Qt
)

from aqt.utils import (
    MenuList,
    SubMenu,
    askUser,
    getOnlyText,
    tr,
)

class filter_button_cls:
    def __init__(self, parent, browser, func_gettext, func_settext, overwrites):
        self.mw = browser.mw
        self.parent = parent
        self.col = browser.col
        self.func_gettext = func_gettext
        self.func_settext = func_settext
        self.overwrites = overwrites

        ml = MenuList()

        ml.addChild(self._commonFilters())
        ml.addSeparator()

        ml.addChild(self._todayFilters())
        ml.addChild(self._cardStateFilters())
        ml.addChild(self._deckFilters())
        ml.addChild(self._noteTypeFilters())
        ml.addChild(self._tagFilters())
        ml.addSeparator()

        # ml.addChild(self.sidebarDockWidget.toggleViewAction())
        ml.addSeparator()

        ml.addChild(self._savedSearches())

        ml.popupOver(parent.form.pb_filter)

    def setFilter(self, *args):
        if len(args) == 1:
            txt = args[0]
        else:
            txt = ""
            items = []
            for c, a in enumerate(args):
                if c % 2 == 0:
                    txt += a + ":"
                else:
                    txt += a
                    for chr in " 　()":
                        if chr in txt:
                            txt = '"%s"' % txt
                            break
                    items.append(txt)
                    txt = ""
            txt = " ".join(items)
        if self.mw.app.keyboardModifiers() & Qt.AltModifier:
            txt = "-" + txt
        # if self.mw.app.keyboardModifiers() & Qt.ControlModifier:
        #     cur = self.func_gettext()  # str(self.form.searchEdit.lineEdit().text())
        #     if cur and cur != self._searchPrompt:
        #         txt = cur + " " + txt
        # elif self.mw.app.keyboardModifiers() & Qt.ShiftModifier:
        #     cur = self.func_gettext()  # str(self.form.searchEdit.lineEdit().text())
        #     if cur:
        #         txt = cur + " or " + txt
        if self.overwrites: 
            self.func_settext(txt)  #  self.form.searchEdit.lineEdit().setText(txt)
        else:
            old = self.func_gettext()
            oldlines = old.split("\n")
            if oldlines[-1]:
                old = old + "\n"
            if self.mw.app.keyboardModifiers() & Qt.ShiftModifier and old:
                txt = " or " + txt
            #self.func_settext(old + txt)
            self.txt = txt
            return txt
        # self.onSearchActivated()

    def _simpleFilters(self, items):
        ml = MenuList()
        for row in items:
            if row is None:
                ml.addSeparator()
            else:
                label, filter = row
                ml.addItem(label, self._filterFunc(filter))
        return ml

    def _filterFunc(self, *args):
        return lambda *, f=args: self.setFilter(*f)

    def _commonFilters(self):
        return self._simpleFilters(
            ((_("Whole Collection"), ""), (_("Current Deck"), "deck:current"))
        )

    def _todayFilters(self):
        subm = SubMenu(_("Today"))
        subm.addChild(
            self._simpleFilters(
                (
                    (_("Added Today"), "added:1"),
                    (_("Studied Today"), "rated:1"),
                    (_("Again Today"), "rated:1:1"),
                )
            )
        )
        return subm

    def _cardStateFilters(self):
        subm = SubMenu(_("Card State"))
        subm.addChild(
            self._simpleFilters(
                (
                    (_("New"), "is:new"),
                    (_("Learning"), "is:learn"),
                    (_("Review"), "is:review"),
                    (tr(TR.FILTERING_IS_DUE), "is:due"),
                    None,
                    (_("Suspended"), "is:suspended"),
                    (_("Buried"), "is:buried"),
                    None,
                    (_("Red Flag"), "flag:1"),
                    (_("Orange Flag"), "flag:2"),
                    (_("Green Flag"), "flag:3"),
                    (_("Blue Flag"), "flag:4"),
                    (_("No Flag"), "flag:0"),
                    (_("Any Flag"), "-flag:0"),
                )
            )
        )
        return subm

    def _tagFilters(self):
        m = SubMenu(_("Tags"))

        # m.addItem(_("Clear Unused"), self.clearUnusedTags)
        # m.addSeparator()

        tagList = MenuList()
        for t in sorted(self.col.tags.all(), key=lambda s: s.lower()):
            tagList.addItem(t, self._filterFunc("tag", t))

        m.addChild(tagList.chunked())
        return m

    def _deckFilters(self):
        # deal with changes from commit 0c340eb
        # https://github.com/ankitects/anki/commit/0c340eba645b4babf9a6bda60160ee08b4e91854
        if pointVersion() < 28:
            return self._deckFilters26()
        else:
            return self._deckFilters28()

    def _deckFilters26(self):
        def addDecks(parent, decks):
            for head, did, rev, lrn, new, children in decks:
                name = self.mw.col.decks.get(did)["name"]
                shortname = DeckManager.basename(name)
                if children:
                    subm = parent.addMenu(shortname)
                    subm.addItem(_("Filter"), self._filterFunc("deck", name))
                    subm.addSeparator()
                    addDecks(subm, children)
                else:
                    if did != 1 or self.col.decks.should_default_be_displayed(
                        force_default=False, assume_no_child=True
                    ):
                        parent.addItem(shortname, self._filterFunc("deck", name))

        # fixme: could rewrite to avoid calculating due # in the future
        alldecks = self.col.sched.deckDueTree()
        ml = MenuList()
        addDecks(ml, alldecks)

        root = SubMenu(_("Decks"))
        root.addChild(ml.chunked())

        return root

    def _deckFilters28(self):
        def addDecks(parent, decks, parent_prefix):
            for node in decks:
                fullname = parent_prefix + node.name
                if node.children:
                    subm = parent.addMenu(node.name)
                    subm.addItem(_("Filter"), lambda: self._filterFunc("deck", fullname))
                    subm.addSeparator()
                    addDecks(subm, node.children, fullname + "::")
                else:
                    parent.addItem(node.name, self._filterFunc("deck", fullname))

        alldecks = self.col.decks.deck_tree()
        ml = MenuList()
        addDecks(ml, alldecks.children, "")

        root = SubMenu(_("Decks"))
        root.addChild(ml.chunked())

        return root

    def _noteTypeFilters(self):
        m = SubMenu(_("Note Types"))

        m.addItem(_("Manage..."), self.mw.onNoteTypes)
        m.addSeparator()

        noteTypes = MenuList()
        for nt in sorted(self.col.models.all(), key=lambda nt: nt["name"].lower()):
            # no sub menu if it's a single template
            if len(nt["tmpls"]) == 1:
                noteTypes.addItem(nt["name"], self._filterFunc("note", nt["name"]))
            else:
                subm = noteTypes.addMenu(nt["name"])

                subm.addItem(_("All Card Types"), self._filterFunc("note", nt["name"]))
                subm.addSeparator()

                # add templates
                for c, tmpl in enumerate(nt["tmpls"]):
                    # T: name is a card type name. n it's order in the list of card type.
                    # T: this is shown in browser's filter, when seeing the list of card type of a note type.
                    name = _("%(n)d: %(name)s") % dict(n=c + 1, name=tmpl["name"])
                    subm.addItem(
                        name, self._filterFunc("note", nt["name"], "card", str(c + 1))
                    )

        m.addChild(noteTypes.chunked())
        return m

    # Favourites
    ######################################################################

    def _savedSearches(self):
        ml = MenuList()
        # make sure exists
        if "savedFilters" not in self.col.conf:
            self.col.set_config("savedFilters", {})

        ml.addSeparator()

        # if self._currentFilterIsSaved():
        #     ml.addItem(_("Remove Current Filter..."), self._onRemoveFilter)
        # else:
        #     ml.addItem(_("Save Current Filter..."), self._onSaveFilter)

        saved = self.col.get_config("savedFilters")
        if not saved:
            return ml

        ml.addSeparator()
        for name, filt in sorted(saved.items()):
            ml.addItem(name, self._filterFunc(filt))

        return ml

    def _onSaveFilter(self) -> None:
        name = getOnlyText(_("Please give your filter a name:"))
        if not name:
            return
        filt = self.func_gettext()  # self.form.searchEdit.lineEdit().text()
        conf = self.col.get_config("savedFilters")
        conf[name] = filt
        self.col.set_config("savedFilters", conf)
        self.maybeRefreshSidebar()  # type: ignore  # noqa - I commented out calling the method _onSaveFilter

    def _onRemoveFilter(self):
        name = self._currentFilterIsSaved()
        if not askUser(_("Remove %s from your saved searches?") % name):
            return
        del self.col.conf["savedFilters"][name]
        self.col.setMod()
        self.maybeRefreshSidebar()  # noqa - I commented out calling the method _onRemoveFilter

    # returns name if found
    def _currentFilterIsSaved(self):
        filt = self.func_gettext()  # self.form.searchEdit.lineEdit().text()
        for k, v in self.col.get_config("savedFilters").items():
            if filt == v:
                return k
        return None
