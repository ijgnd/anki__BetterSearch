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

from .help_text import helptext


minihelp_geom_name = "minihelp"
mini_search_help_dialog_title = "search_cheat_sheet"  # dialog manager


class MiniHelpSearch(QDialog):
    silentlyClose = True  # dialog manager

    def __init__(self, parent):
        QDialog.__init__(self, parent, Qt.Window)
        self.parent = parent
        self.setWindowTitle("Anki - Search Cheatsheet")
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.te = QTextEdit()
        self.vbox.addWidget(self.te)
        self.setLayout(self.vbox)
        self.te.setText(helptext)
        self.te.setReadOnly(True)
        self.show()
        self.resize(450, 650)
        restoreGeom(self, minihelp_geom_name)

    def reopen(self, parent):  # dialog manager
        pass

    def reject(self):
        saveGeom(self, minihelp_geom_name)
        # aqt.dialogs.markClosed(mini_search_help_dialog_title)  # dialog manager
        QDialog.reject(self)

    def accept(self):
        saveGeom(self, minihelp_geom_name)
        # aqt.dialogs.markClosed(mini_search_help_dialog_title)  # dialog manager
        QDialog.accept(self)
