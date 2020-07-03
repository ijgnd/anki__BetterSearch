import os

import aqt

from aqt.qt import (
    QDialog,
    Qt,
    QVBoxLayout,
    QTextEdit,
)

from aqt.utils import (
    restoreGeom,
    saveGeom,
)
from aqt.theme import theme_manager
from aqt.webview import AnkiWebView

from .help_text import helptext


minihelp_geom_name = "minihelp"
mini_search_help_dialog_title = "search_cheat_sheet"  # dialog manager



# adjusted from my half-baked ir add-on
def move_window(left, right, newpos):
    screen = aqt.mw.app.desktop().screenGeometry()
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


def help_as_webpage():
    return """
    <style>
%(THEME)s
    </style>
%(HELPTEXT)s
"""  % {
"THEME": get_theme(),
"HELPTEXT": helptext,
}



class MiniHelpSearch(QDialog):
    silentlyClose = True  # dialog manager

    def __init__(self, parent):
        QDialog.__init__(self, parent, Qt.Window)
        self.parent = parent
        self.setWindowTitle("Anki - Search Cheatsheet")
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)
        #self.te = QTextEdit()
        #self.te.setText(helptext)
        #self.te.setReadOnly(True)
        self.te = AnkiWebView()
        self.te.setHtml(help_as_webpage())
        self.vbox.addWidget(self.te)
        self.setLayout(self.vbox)
        self.resize(380, 650)
        restoreGeom(self, minihelp_geom_name)
        move_window(left=self, right=parent, newpos="side-by-side")
        # P: on MacOS it's behind. "self.raise_()" doesn't help.

    # self.move_window_left(self):
        # move_window(left=self, right=parent, newpos="side-by-side")

    def reopen(self, parent):  # dialog manager
        pass

    def reject(self):
        self.parent.help_dialog = None
        # print(f"in rejected, width: {self.width()}, height: {self.height()}") 
        saveGeom(self, minihelp_geom_name)
        # aqt.dialogs.markClosed(mini_search_help_dialog_title)  # dialog manager
        QDialog.reject(self)

    def accept(self):
        saveGeom(self, minihelp_geom_name)
        # aqt.dialogs.markClosed(mini_search_help_dialog_title)  # dialog manager
        QDialog.accept(self)
