import os

from anki.utils import (
    is_lin
)

import aqt

from aqt.qt import *

from aqt.utils import (
    restoreGeom,
    saveGeom,
)
from aqt.theme import theme_manager
from aqt.webview import AnkiWebView

from .anki_version_detection import anki_point_version
from .help_text import helptext


minihelp_geom_name = "minihelp"
mini_search_help_dialog_title = "search_cheat_sheet"  # dialog manager



# adjusted from my half-baked ir add-on
def move_window(left, right, newpos):
    if qtmajor == 5:
        screen = aqt.mw.app.desktop().screenGeometry()
    else:
        screen = aqt.mw.screen().availableGeometry()
    width = screen.width()
    height = screen.height()
    rx = right.x()
    ry = right.y()
    rw = right.width()
    rh = right.height()
    lx = left.x()
    ly = left.y()
    lw = left.width()
    lh = left.height()
    if newpos == "side-by-side":
        if rx > lw:  # if there's enough space left of the right dialog, don't move right
                     # and just put the left dialog next to it.
            # try to level top of windows, doesn't really work on my computer?
            if (height-ry) > lh:
                ly = ry
            left.setGeometry(rx-lw, ly, lw, lh)
        elif lw + rw <= width:  # if there's enough space on the screen, if you move the right dialog
                               # move
            leftspace = (width - (lw+rw))/2
            # try to level top of windows, doesn't really work on my computer?
            if (height-ry) > lh:
                ly = ry
            left.setGeometry( leftspace,      ly, lw, lh)
            right.setGeometry(leftspace + lw, ry, rw, rh)
        else:  # total width over screen width: shrink and move
            # fully fixing is too complicated, just resize info box and move to left and hope for
            # the best
            if lw > 350:
                lw = 350
            # try to level top of windows, doesn't really work on my computer?
            if (height-ry) > lh:
                ly = ry
            left.setGeometry(  0, ly, lw, lh)
            right.setGeometry(rx, ry, rw, rh)


addon_folder_abs_path = os.path.dirname(__file__)


def return_file_content(filename):
    file = os.path.join(addon_folder_abs_path, filename)
    with open(file) as fo:
        return fo.read()


def get_theme():
    if theme_manager.night_mode:
        filename = "sakura-dark.css"
    else:
        filename = "sakura.css"
    return return_file_content(filename)

def maybe_inject_css_for_night_mode_scrollbar():
    # copied over from 8ea9702 from anki__reviewer_deck_and_card_info_sidebar
    # TODO Fixme
    return "" if not theme_manager.night_mode else """
:root {
--canvas:#2c2c2c;
--scrollbar-bg:#454545;
--scrollbar-bg-hover:#545454;
--scrollbar-bg-active:#636363;
}

html body:not(.isMac)::-webkit-scrollbar,
html body:not(.isMac) *::-webkit-scrollbar {
    background-color: var(--canvas);
}
html body:not(.isMac)::-webkit-scrollbar-thumb:hover,
html body:not(.isMac) *::-webkit-scrollbar-thumb:hover {
    background: var(--scrollbar-bg-hover);
}
html body:not(.isMac)::-webkit-scrollbar-thumb:active,
html body:not(.isMac) *::-webkit-scrollbar-thumb:active {
    background: var(--scrollbar-bg-active);
}
html body:not(.isMac)::-webkit-scrollbar-corner,
html body:not(.isMac) *::-webkit-scrollbar-corner {
    background-color: var(--canvas);
}
html body:not(.isMac)::-webkit-scrollbar-thumb,
html body:not(.isMac) *::-webkit-scrollbar-thumb {
background: var(--scrollbar-bg);
}
}
html body:not(.isMac)::-webkit-scrollbar-track,
html body:not(.isMac) *::-webkit-scrollbar-track {
background-color: transparent;
}

html body:not(.isMac)::-webkit-scrollbar:horizontal,
html body:not(.isMac) *::-webkit-scrollbar:horizontal {
    height: 12px;
}
html body:not(.isMac)::-webkit-scrollbar:vertical,
html body:not(.isMac) *::-webkit-scrollbar:vertical {
    width: 12px;
}
html body:not(.isMac)::-webkit-scrollbar-thumb:horizontal,
html body:not(.isMac) *::-webkit-scrollbar-thumb:horizontal {
    min-width: 40px;
}
html body:not(.isMac)::-webkit-scrollbar-thumb:vertical,
html body:not(.isMac) *::-webkit-scrollbar-thumb:vertical {
    min-height: 40px;
}
"""


def help_as_webpage():
    return """
    <style>
%(THEME)s
%(SCROLLBAR_WORKAROUND)s
    </style>
%(HELPTEXT)s
"""  % {
"THEME": get_theme(),
"SCROLLBAR_WORKAROUND": maybe_inject_css_for_night_mode_scrollbar(),
"HELPTEXT": helptext,
}


class AnkiWebViewWrapper(AnkiWebView):
    def on_theme_did_change(self):
        # self.setHtml(help_as_webpage())
        pass

# TODO maybe use https://stackoverflow.com/a/54888872 by eyllanesc
# Since its from Feb 26, 2019 its CC BY-SA 4.0 (see https://stackoverflow.com/help/licensing)
# so that it should be useable
# also possibly relevant: https://doc.qt.io/qtforpython-6/examples/example_webenginewidgets_tabbedbrowser.html

class MiniHelpSearch(QDialog):
    silentlyClose = True  # dialog manager

    def __init__(self, parent):
        QDialog.__init__(self, parent, Qt.WindowType.Window)
        if anki_point_version < 45:
            aqt.mw.setupDialogGC(self)
        else:
            aqt.mw.garbage_collect_on_dialog_finish(self)
        self.parent = parent
        self.setup_ui()
        self.setup_shortcuts()
        self.resize(380, 650)
        restoreGeom(self, minihelp_geom_name)
        move_window(left=self, right=parent, newpos="side-by-side")
        # P: on MacOS it's behind. "self.raise_()" doesn't help

    def setup_ui(self):
        self.setWindowTitle("Anki - Search Cheatsheet")
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)
        
        self.webview = AnkiWebViewWrapper()  # QWebEngineView
        self.webview.setHtml(help_as_webpage())
        self.vbox.addWidget(self.webview)
        
        self.bottom_layout = QHBoxLayout()

        self.line_edit = QLineEdit()
        self.line_edit.textChanged.connect(self.on_text_change)
        self.line_edit.setClearButtonEnabled(True)
        self.line_edit.setPlaceholderText("Find...")
        self.bottom_layout.addWidget(self.line_edit)

        # TODO when focusing the line edit this first button is also
        # focused and triggered by Return. So I do not need
        # to connect the returnPressed signal (and if I did a 
        # search would be run twice)
        # Though I wonder why this button has focus?
        # Ideally I should switch this with the prev button (but then
        # return would trigger a backward search which is worse)
        self.next_button = QPushButton("∨")
        self.next_button.clicked.connect(self.on_find_next)
        self.next_button.setToolTip("Ctrl+F")
        self.next_button.setMaximumWidth(40)
        self.bottom_layout.addWidget(self.next_button)

        self.prev_button = QPushButton("∧")
        self.prev_button.clicked.connect(self.on_find_previous)
        self.prev_button.setToolTip("Ctrl+R")
        self.prev_button.setMaximumWidth(40)
        self.bottom_layout.addWidget(self.prev_button)
            
        self.close_bottom_button = QPushButton("x")
        self.close_bottom_button.clicked.connect(self.hide_bottom)
        self.close_bottom_button.setToolTip("Esc")
        self.close_bottom_button.setMaximumWidth(40)
        self.bottom_layout.addWidget(self.close_bottom_button)

        self.vbox.addLayout(self.bottom_layout)

        self.bottom_is_visible = True
        self.hide_bottom()
        self.setLayout(self.vbox)

    def hide_bottom(self):
        self.line_edit.setVisible(False)
        self.next_button.setVisible(False)
        self.prev_button.setVisible(False)
        self.close_bottom_button.setVisible(False)
        self.bottom_is_visible = False

    def show_bottom(self):
        self.line_edit.setVisible(True)
        self.next_button.setVisible(True)
        self.prev_button.setVisible(True)
        self.close_bottom_button.setVisible(True)
        self.bottom_is_visible = True

    def setup_shortcuts(self):
        # https://doc.qt.io/qt-6/qkeysequence.html
        # |StandardKey |Windows              |Mac         |Linux-KDE |Linux-Gnome          |
        # |FindNext    |F3,Ctrl+G            |Ctrl+G      |F3        |Ctrl+G,F3            |
        # |FindPrevious|Shift+F3,Ctrl+Shift+G|Ctrl+Shift+G|Shift+F3  |Ctrl+Shift+G,Shift+F3|

        shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut.activated.connect(self.handle_shortcut_find_next)

        if is_lin:
            shortcut = QShortcut(QKeySequence("Ctrl+G"), self)
            shortcut.activated.connect(self.handle_shortcut_find_next)

        shortcut = QShortcut(QKeySequence.StandardKey.FindNext, self)
        shortcut.activated.connect(self.handle_shortcut_find_next)

        shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        shortcut.activated.connect(self.handle_shortcut_find_prev)

        shortcut = QShortcut(QKeySequence.StandardKey.FindPrevious, self)
        shortcut.activated.connect(self.handle_shortcut_find_prev)

        shortcut = QShortcut(QKeySequence.StandardKey.Close, self)  # Ctrl + W
        shortcut.activated.connect(self.reject)

    def log(self, text):
        pass
        
    def on_text_change(self):
        self.log("on_text_change")
        self.on_find_next()

    def on_return_pressed(self):
        self.log('on_return_pressed')
        #self.on_find_next()

    def handle_shortcut_find_next(self):
        if not self.bottom_is_visible:
            self.show_bottom()
            self.line_edit.setFocus()
        else:
            self.log('handle_shortcut_find_next')
            self.next_button.animateClick()

    def handle_shortcut_find_prev(self):
        if not self.bottom_is_visible:
            self.show_bottom()
            self.line_edit.setFocus()
        else:
            self.log('handle_shortcut_find_prev')
            self.prev_button.animateClick() 
    
    def on_find_previous(self):
        self.log('on_find_previous')
        self.update_searching(QWebEnginePage.FindFlag.FindBackward)

    def on_find_next(self):
        self.log('on_find_next')
        self.update_searching()

    def update_searching(self, backward=False):
        self.log('update_searching')
        if backward:
            self.webview.findText(self.line_edit.text(), backward)  
        else:
            self.webview.findText(self.line_edit.text())

    def reopen(self, parent):  # dialog manager
        pass

    def reject(self):
        if self.bottom_is_visible:
            self.hide_bottom()
        else:
            self.parent.help_dialog = None
            # print(f"in rejected, width: {self.width()}, height: {self.height()}") 
            saveGeom(self, minihelp_geom_name)
            # for AnkiWebView:
            self.webview.cleanup()
            self.webview = None
            # aqt.dialogs.markClosed(mini_search_help_dialog_title)  # dialog manager
            QDialog.reject(self)

    def accept(self):
        saveGeom(self, minihelp_geom_name)
        # aqt.dialogs.markClosed(mini_search_help_dialog_title)  # dialog manager
        QDialog.accept(self)

