from anki.utils import (
    isMac,
    pointVersion,
)
from aqt.gui_hooks import (
    browser_menus_did_init,
)
from aqt.qt import (
    QAction,
    QKeySequence,
    QShortcut,
    qconnect,
)
if pointVersion() >= 41:
    from aqt.utils import (
        TR,
        tr,
    )

from .config import gc
from .dialog__date import DateRangeDialog
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
        prompt_for_current_version = self._searchPrompt if pointVersion() < 41 else tr(TR.BROWSING_SEARCH_BAR_HINT)
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


def setup_browser_menu(self):
    # self is browser
    view = getMenu(self, "&View")
    if not hasattr(self, "menuView"):
        self.menuView = view
    cut = gc("Multiline Dialog: shortcut: open window")
    # if cut:
    #    cm = QShortcut(QKeySequence(cut), self)
    #    qconnect(cm.activated, lambda b=self: open_multiline_searchwindow(b))
    action = QAction(self)
    action.setText("Show search string in multi-line dialog")
    if cut:
        action.setShortcut(QKeySequence(cut))
    view.addAction(action)
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
    view.addAction(action)
    action.triggered.connect(lambda _, b=self: search_history_helper(b))

    action = QAction(self)
    action.setText("Show Date Range Dialog for Added")
    view.addAction(action)
    action.triggered.connect(lambda _, b=self, t="added": date_range_dialog_helper(b, t))

    if pointVersion() >= 28:
        action = QAction(self)
        action.setText("Show Date Range Dialog for Edited")
        view.addAction(action)
        action.triggered.connect(lambda _, b=self, t="edited": date_range_dialog_helper(b, t))

    action = QAction(self)
    action.setText("Show Date Range Dialog for Rated")
    view.addAction(action)
    action.triggered.connect(lambda _, b=self, t="rated": date_range_dialog_helper(b, t))
browser_menus_did_init.append(setup_browser_menu)  # noqa
