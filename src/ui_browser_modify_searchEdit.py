from anki.hooks import wrap
from anki.utils import (
    pointVersion,
)
from aqt.browser import Browser
from aqt.gui_hooks import (
    browser_menus_did_init,
)
from aqt.qt import (
    QAction,
    QCursor,
    QMenu,
    QPushButton,
)
from .button_helper import button_helper
from .config import gc
from .helpers import (
    browser_searchEdit_hint_shown,
)
from .onTextChange import onSearchEditTextChange
from .ui_browser import (
    search_history_helper,
    open_multiline_searchwindow,
)
from .ui_browser_ComboReplacer import ComboReplacer


def mysearch_before41(self):
    if gc("-Modify Search Bar") == "multiline":
        return
    self.form.searchEdit.editTextChanged.connect(self.onBrowserSearchEditTextChange)
def mysearch_41(self, card=None, search=None):
    if gc("-Modify Search Bar") == "multiline":
        return
    self.form.searchEdit.editTextChanged.connect(self.onBrowserSearchEditTextChange)
if pointVersion() < 41:
    Browser.setupSearch = wrap(Browser.setupSearch, mysearch_before41)
else:
    Browser.setupSearch = wrap(Browser.setupSearch, mysearch_41)


def onBrowserSearchEditTextChange(self, arg):
    le = self.form.searchEdit.lineEdit()
    pos = le.cursorPosition()
    ret = onSearchEditTextChange(
        parent=self,
        move_dialog_in_browser=True,
        include_filtered_in_deck=True,
        func_gettext=le.text,
        func_settext=le.setText,
        cursorpos=pos,
        mw=self.mw,
        col=self.col
    )
    if not ret:
        return
    else:
        newpos, triggersearch = ret
        if newpos:
            self.form.searchEdit.lineEdit().setCursorPosition(newpos)
        if triggersearch:  # randialog and TriggerSearchAfter:
            self.onSearchActivated()
Browser.onBrowserSearchEditTextChange = onBrowserSearchEditTextChange


basic_stylesheet = """
QMenu::item {
    padding-top: 16px;
    padding-bottom: 16px;
    padding-right: 75px;
    padding-left: 20px;
    font-size: 15px;
}
QMenu::item:selected {
    background-color: #fd4332;
}
"""


def fuzzy_helper(self, arg):
    if browser_searchEdit_hint_shown(self.form.searchEdit.lineEdit().text(), self):
        self.form.searchEdit.lineEdit().setText("")
    button_helper(self.form.searchEdit, self, self.mw, self.col, arg)


def fuzzy_menu(self):
    # self is browser
    actions = [
        ["dnc:", "Note-Card",],
        ["dnf:", "Note-Field",],
        ["deck:", "Deck", ],
        ["note:", "Note",],
        ["card:", "Card",],
        ["tag:", "Tag", ],
        ["prop:", "Card Property", ],
        ["is:", "Card State",],
        [gc("date range dialog for added: string", "dadded"), "Date Added",],
        [gc("date range dialog for rated: string", "drated"), "Date Range",],
    ]
    menu = QMenu(self)
    # menu.setStyleSheet(basic_stylesheet)

    for idx, line in enumerate(actions):
        a = QAction(line[1])
        a.triggered.connect(lambda _, b=self, i=line[0]: fuzzy_helper(b, i))
        menu.addAction(a)
        actions[idx].append(a)
    menu.exec(QCursor.pos())


def modify_browser(self):
    # self is browser
    addbutton = gc("-Add Button to the Browser Search Bar")
    justdown = True if gc("-Modify Search Bar") == "down" and pointVersion() < 41  else False
    multiline = True if gc("-Modify Search Bar") == "multiline" else False
    # the following is needed for my add-on side-by-side so that it still moves the
    # search bar if it's not done here. The current function is run by the hook
    # browser_menus_did_init which is run before the hook browser_will_show that the side-by-side 
    # add-on uses
    self.bettersearch_modified_searchbar_position = justdown or multiline

    grid = self.form.gridLayout
    elements = []
    for i in range(grid.count()):
        # row, column, size_cols, size_rows = grid.getItemPosition(i)
        w = grid.itemAt(i).widget()
        name = w.objectName() if hasattr(w, "objectName") else ""
        elements.append((w, name))

    gridcounter = 0

    pb_hist = QPushButton("History")
    pb_hist.clicked.connect(lambda _, browser=self: search_history_helper(browser))
    pb_hist.setObjectName("custom_history")
    cut = gc("shortcut - select entry from history in fuzzy dialog")
    if cut:
        pb_hist.setToolTip(f"shortcut: {cut}")

    pb_fm = QPushButton("FF")  # fuzyy menu / fuzzy find
    pb_fm.clicked.connect(lambda _, browser=self: fuzzy_menu(browser))
    pb_fm.setObjectName("fuzzy_menu")
    cut = gc("-Shortcut for Multi-bar mode: show fuzzy menu")
    if cut:
        pb_fm.setToolTip(f"shortcut: {cut}")
        pb_fm.setShortcut(cut)

    pb_sd = QPushButton("SearchDialog")
    pb_sd.clicked.connect(lambda _, browser=self: open_multiline_searchwindow(browser))
    pb_sd.setObjectName("SearchDialog")
    cut = gc("Multiline Dialog: shortcut: open window")
    if cut:
        pb_sd.setToolTip(f"shortcut: {cut}")

    if multiline:
        self.form.searchEdit.lineEdit().returnPressed.disconnect()
        self.form.searchEdit.setVisible(False)
        for e in elements:
            if e[1] == "searchEdit":
                grid.removeWidget(e[0])
        self.form.searchEdit = ComboReplacer(self)
        user_height = gc("-Multiline bar Height relative to default (when shown in Browser)", 100)
        default_height = self.fontMetrics().lineSpacing()
        new_height = int((default_height + 5) * 2 * user_height/100)
        self.form.searchEdit.setFixedHeight(new_height)
        #self.form.searchEdit.setMaximumHeight(new_height)

    if multiline and pointVersion() < 41:
        self.form.searchButton.setShortcut("Return")
        grid.addWidget(self.form.searchEdit, 1, 0, 1, -1)
        grid.addWidget(pb_hist, 0, 0, 1, 1)
        gridcounter += 1
        grid.addWidget(pb_fm, 0, gridcounter, 1, 1)
        gridcounter += 1

    if addbutton and pointVersion() < 41:
        grid.addWidget(pb_sd, 0, gridcounter, 1, 1)
        for idx, e in enumerate(elements):
            if e[1] == "filter":
                grid.addWidget(e[0], 0, gridcounter+1, 1, 1)
                del elements[idx]
        for idx, item in enumerate(elements):
            grid.addWidget(item[0], 0, gridcounter+2+idx, 1, 1)

    if justdown:  # never True for pointVersion >= 41
        # the code for "justdown" is copied verbatim from my older "side-by-side"
        # store lineedit and its index
        grid = self.form.gridLayout
        for idx in range(grid.count()):   
            item = grid.itemAt(idx)
            w = item.widget()
            name = w.objectName() if hasattr(w, "objectName") else ""
            if name == "searchEdit":
                searchbar = w
        self.form.gridLayout.addWidget(searchbar, 1, 0, 1, -1)

    if pointVersion() >=41 and multiline:
        pb_hist.setMaximumWidth(45)
        grid.addWidget(self.form.searchEdit, 0, 0, 1, 1)
        grid.addWidget(pb_hist, 0, 1, 1, 1)

browser_menus_did_init.append(modify_browser)
