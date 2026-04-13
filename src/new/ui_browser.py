from anki.utils import (
    isMac,
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

from aqt.utils import (
    TR,
    tr,
)
from aqt.utils import (
    openHelp,
    showInfo,
    tooltip,
)

from .config import gc, on_settings
from .dialog__date import get_date_range_string
from .dialog__help import MiniHelpSearch
from .dialog__multi_line import SearchBox
from .filter_dialog import FilterDialog
from .overrides import overrides
from .split_string import split_to_multiline
from .toolbar import getMenu


def settings_helper():
    txt = "After changing settings close the browser window so that your change take effect"
    showInfo(txt)
    on_settings()


from aqt.utils import askUser
from .. import load_old_conf
def switch_back_to_old_version():
    if not askUser("Really switch to old version of this addon?"):
        return
    # store current config in user files + write old config meta.json
    load_old_conf()
    msg = ("Restart Anki now. Otherwise you'll run into error messages. The old config "
           "has been restored. The old and new configs are independent of each other. So "
           "config changes for the new version only affect the new version and vice versa.")
    showInfo(msg)


def date_range_dialog_helper(browser, search_operator):
    # self is browser
    success, searchtext, trigger_search_after = get_date_range_string(
        parent=browser, col=browser.col, search_operator=search_operator, prefixed_with_minus=False
    )
    if success:
        _, override_autosearch_default, _, _ = overrides()
        if override_autosearch_default:
            trigger_search_after ^= True
        le = browser.form.searchEdit.lineEdit()
        prompt_for_current_version = tr(TR.BROWSING_SEARCH_BAR_HINT)
        if le.text() == prompt_for_current_version:
            new = searchtext
        else:
            new = le.text() + " " + searchtext
        le.setText(new)
        if trigger_search_after:
            browser.onSearchActivated()


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


def helper(browser, kind):
    if kind == "Browser history":
        # similar to method from dialog__multi_line
        hist_list = browser.mw.pm.profile["searchHistory"]
        candidates_list = [split_to_multiline(e) for e in hist_list]
        title = "Filter Anki Browser Search History"
    elif kind == "Browser saved searches":
        candidates = browser.col.get_config("savedFilters", {})  # browser.sidebar._saved_searches_key
        candidates_list = [f"{label}----{term}" for label, term in candidates.items()]
        title = "Filter Anki Browser Saved Searches"
    else:
        return
    d = FilterDialog(
        parent=browser,
        parent_is_browser=True,
        values_as_list_or_dict=candidates_list,
        windowtitle=title,
        #max_items=None,
        #prefill="",
        adjPos=False,
        show_star=False,
        check_star=False,
        infotext=False,
        show_prepend_minus_button=False,
        check_prepend_minus_button=False,
        #show_run_search_on_exit=True,
        #do_run_search_on_exit=False,
        #sort_vals=True,
        multi_selection_enabled=False,
        context=kind,
    )
    if d.exec():
        if kind == "Browser history":
            new = d.sel_keys_list[0].replace("\n", " ")
        elif kind == "Browser saved searches":
            # new = d.sel_keys_list[0].split("\n")[1]
            new = d.sel_keys_list[0].split("----")[1]
        le = browser.form.searchEdit.lineEdit()
        le.setText(new)
        browser.onSearchActivated()


def open_local_help_window(self):
    if self.help_dialog:
        tooltip("mini help window is already open (but maybe it's below another window of yours).")
        self.help_dialog.raise_()  # doesn't work on MacOS
    else:
        self.help_dialog = MiniHelpSearch(self)
        self.help_dialog.show()
    # aqt.dialogs.open(mini_search_help_dialog_title, aqt.mw)


def setup_browser_menu(self):
    self.help_dialog = None

    # self is browser
    bs_menu = getMenu(self, "&BetterSearch")
    if not hasattr(self, "menuView"):
        self.menuBettersearch = bs_menu
    cut1 = gc(["browser shortcuts", "Multiline Dialog: shortcut: open window"])
    action = QAction(self)
    action.setText("Show search string in multi-line dialog")
    if cut1:
        action.setShortcut(QKeySequence(cut1))
    bs_menu.addAction(action)
    action.triggered.connect(lambda _, b=self: open_multiline_searchwindow(b))

    cut2 = gc(["browser shortcuts", "Multiline Dialog: shortcut: open window (alternative)"])
    if cut2:
        self.CutFilterDialogAlternative = QShortcut(QKeySequence(cut2), self)
        qconnect(self.CutFilterDialogAlternative.activated, lambda b=self: open_multiline_searchwindow(b))

    self.BeSeAction = QAction(self)
    self.BeSeAction.setText("BetterSearch")
    if cut1:
        self.BeSeAction.setToolTip(cut1)
    self.BeSeAction.triggered.connect(lambda _, b=self: open_multiline_searchwindow(b))

    cut = gc(["browser shortcuts", "shortcut - select entry from history in fuzzy dialog"])
    # if cut:
    #    cm = QShortcut(QKeySequence(cut), self)
    #    qconnect(cm.activated, lambda b=self: search_history_helper(b))
    action = QAction(self)
    action.setText("Select entry from search history")
    if cut:
        action.setShortcut(QKeySequence(cut))
    bs_menu.addAction(action)
    action.triggered.connect(lambda _, b=self: helper(b, "Browser history"))

    cut = gc(["browser shortcuts", "shortcut - select entry from saved searches in fuzzy dialog"])
    action = QAction(self)
    action.setText("Select entry from saved searches")
    if cut:
        action.setShortcut(QKeySequence(cut))
    bs_menu.addAction(action)
    action.triggered.connect(lambda _, b=self: helper(b, "Browser saved searches"))

    bs_menu.addSeparator()

    action = QAction(self)
    action.setText("Show Date Range Dialog for Added")
    bs_menu.addAction(action)
    action.triggered.connect(lambda _, b=self, t="added": date_range_dialog_helper(b, t))

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
    action.setText("Show Manual for Searching (offline copy, version from 2024-03)")
    bs_menu.addAction(action)
    action.triggered.connect(lambda _, b=self: open_local_help_window(b))

    bs_menu.addSeparator()

    action = QAction(self)
    action.setText("Switch back to old add-on version")
    bs_menu.addAction(action)
    action.triggered.connect(lambda _: switch_back_to_old_version())

    bs_menu.addSeparator()

    action = QAction(self)
    action.setText("AddonSettings")
    bs_menu.addAction(action)
    action.triggered.connect(lambda _: settings_helper())


browser_menus_did_init.append(setup_browser_menu)  # noqa
