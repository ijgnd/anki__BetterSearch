from anki.utils import (
    isMac,
)
from aqt.gui_hooks import (
    browser_menus_did_init,
)
from aqt.qt import (
    QAction,
    QKeySequence,
    QMenu,
    QShortcut,
    qconnect,
)
from .anki_version_detection import anki_point_version
if anki_point_version >= 41:
    from aqt.utils import (
        TR,
        tr,
    )
from aqt.utils import (
    openHelp,
    tooltip,
)

from .config import gc, wcs
from .dialog__date import DateRangeDialog
from .dialog__help import MiniHelpSearch
from .dialog__multi_line import SearchBox
from .fuzzy_panel import FilterDialog
from .helpers import overrides
from .split_string import split_to_multiline
from .ui_browser_ComboReplacer import ComboReplacer  # noqa
from .toolbar import getMenu


def date_range_dialog_helper(self, term):
    # self is browser
    d = DateRangeDialog(self, term)
    if d.exec():
        trigger_search_after = gc("modify: window opened by search strings triggers search by default")
        _, override_autosearch_default, _, _ = overrides()
        if override_autosearch_default:
            trigger_search_after ^= True
        le = self.form.searchEdit.lineEdit()
        prompt_for_current_version = self._searchPrompt if anki_point_version < 41 else tr(TR.BROWSING_SEARCH_BAR_HINT)
        if le.text() == prompt_for_current_version:
            new = d.searchtext
        else:
            new = le.text() + "  " + d.searchtext
        le.setText(new)
        if trigger_search_after:
            self.onSearchActivated()


def open_multiline_searchwindow(browser):
    le = browser.form.searchEdit.lineEdit()
    sbi = SearchBox(browser, le.text())
    if isMac:
        sbi.open()
    else:
        if sbi.exec():
            le.setText(sbi.newsearch)
            le.setFocus()
            browser.onSearchActivated()


def search_history_helper(self):
    # self is browser
    # similar to method from dialog__multi_line
    hist_list = self.mw.pm.profile["searchHistory"]
    processed_list = [split_to_multiline(e) for e in hist_list]
    d = FilterDialog(
        parent=self,
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
        new = d.selkey.replace("\n", "  ")
        le = self.form.searchEdit.lineEdit()
        le.setText(new)
        self.onSearchActivated()


def open_local_help_window(self):
    if self.help_dialog:
        tooltip("mini help window is already open (but maybe it's below another window of yours).")
        self.help_dialog.raise_()  # doesn't work on MacOS
    else:
        self.help_dialog = MiniHelpSearch(self)
        self.help_dialog.show()
    #aqt.dialogs.open(mini_search_help_dialog_title, aqt.mw)


def toggle_preference(what):
    key = f"modify_{what}"
    wcs(key=key, new_val=not gc(key))


def setup_browser_menu(self):
    self.help_dialog = None

    # self is browser
    bs_menu = getMenu(self, "&BetterSearch")
    if not hasattr(self, "menuView"):
        self.menuBettersearch = bs_menu
    cut = gc("Multiline Dialog: shortcut: open window")
    action = QAction(self)
    action.setText("Show search string in multi-line dialog")
    if cut:
        action.setShortcut(QKeySequence(cut))
    bs_menu.addAction(action)
    action.triggered.connect(lambda _, b=self: open_multiline_searchwindow(b))

    self.BeSeAction = QAction(self)
    self.BeSeAction.setText("BetterSearch")
    if cut:
        self.BeSeAction.setToolTip(cut)
    self.BeSeAction.triggered.connect(lambda _, b=self: open_multiline_searchwindow(b))

    cut = gc("shortcut - select entry from history in fuzzy dialog")
    # if cut:
    #    cm = QShortcut(QKeySequence(cut), self)
    #    qconnect(cm.activated, lambda b=self: search_history_helper(b))
    action = QAction(self)
    action.setText("Select entry from search history")
    if cut:
        action.setShortcut(QKeySequence(cut))
    bs_menu.addAction(action)
    action.triggered.connect(lambda _, b=self: search_history_helper(b))

    bs_menu.addSeparator()

    action = QAction(self)
    action.setText("Show Date Range Dialog for Added")
    bs_menu.addAction(action)
    action.triggered.connect(lambda _, b=self, t="added": date_range_dialog_helper(b, t))

    if anki_point_version >= 28:
        action = QAction(self)
        action.setText("Show Date Range Dialog for Edited")
        bs_menu.addAction(action)
        action.triggered.connect(lambda _, b=self, t="edited": date_range_dialog_helper(b, t))

    action = QAction(self)
    action.setText("Show Date Range Dialog for Rated")
    bs_menu.addAction(action)
    action.triggered.connect(lambda _, b=self, t="rated": date_range_dialog_helper(b, t))

    bs_menu.addSeparator()

    action = QAction(self)
    action.setText("Show Manual for Searching (online)")
    bs_menu.addAction(action)
    action.triggered.connect(lambda _: openHelp("searching"))

    action = QAction(self)
    action.setText("Show Manual for Searching (offline copy, version from 2023-06)")
    bs_menu.addAction(action)
    action.triggered.connect(lambda _,b=self: open_local_help_window(b))


    edm = QMenu("(en-/dis-)able dialog for search terms/dialog triggered by ...", self)
    bs_menu.addMenu(edm)
    elements = [
        "card",
        "deck",
        "field",
        "flag",
        "is",
        "note",
        "props",
        "tag",
    ]
    for e in elements:
        a = edm.addAction(f"{e}:")
        a.setCheckable(True)
        if gc(f"modify_{e}"):
            a.setChecked(True)
        a.toggled.connect(lambda _, arg=e: toggle_preference(arg))


browser_menus_did_init.append(setup_browser_menu)  # noqa
