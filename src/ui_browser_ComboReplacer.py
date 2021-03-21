"""
searchEdit occurs in browser.py in 2.1.28 in these lines:

        qconnect(self.form.searchEdit.lineEdit().returnPressed, self.onSearchActivated)
        self.form.searchEdit.setCompleter(None)
        self.form.searchEdit.addItems(
        self.form.searchEdit.lineEdit().setText(self._searchPrompt)
        self.form.searchEdit.lineEdit().selectAll()
        self.form.searchEdit.setFocus()
        if self.form.searchEdit.lineEdit().text() == self._searchPrompt:
            self.form.searchEdit.lineEdit().setText("deck:current ")
        txt = self.form.searchEdit.lineEdit().text()
        self.form.searchEdit.clear()
        self.form.searchEdit.addItems(sh)
            cur = str(self.form.searchEdit.lineEdit().text())
            cur = str(self.form.searchEdit.lineEdit().text())
        self.form.searchEdit.lineEdit().setText(txt)
        filt = self.form.searchEdit.lineEdit().text()
        filt = self.form.searchEdit.lineEdit().text()
        self.form.searchEdit.lineEdit().setText(self._lastSearchTxt)
        self.form.searchEdit.lineEdit().setText(link)
        self.form.searchEdit.setFocus()
        self.form.searchEdit.lineEdit().selectAll()


so I need to modify this:

signals
    returnPressed

the functions are 
    clear()
    
    addItems() - addsList
    setCompleter(None)
    lineEdit().setText(self._searchPrompt)
    lineEdit().text()

    lineEdit().selectAll()
    self.form.searchEdit.setFocus()
    setFocus()
"""

from anki.utils import (
    pointVersion
)
from aqt import mw
from aqt.browser import Browser
from aqt.qt import (
    QPlainTextEdit,
    Qt,
    pyqtSignal,
)

from .config import gc
from .helpers import (
    browser_searchEdit_hint_shown,
)
from .onTextChange import onSearchEditTextChange





def _onSearchActivated_dont_add_to_history(self):
    # self is browser

    # convert guide text before we save history
    if browser_searchEdit_hint_shown(self.form.searchEdit.lineEdit().text(), self):
        self.form.searchEdit.lineEdit().setText("deck:current ")

    # grab search text and normalize
    txt = self.form.searchEdit.lineEdit().text()

    """
    # update history
    sh = self.mw.pm.profile["searchHistory"]
    if txt in sh:
        sh.remove(txt)
    sh.insert(0, txt)
    sh = sh[:30]
    self.form.searchEdit.clear()
    self.form.searchEdit.addItems(sh)
    self.mw.pm.profile["searchHistory"] = sh
    """
    
    # keep track of search string so that we reuse identical search when
    # refreshing, rather than whatever is currently in the search field
    self._lastSearchTxt = txt
    self.search()






class ComboReplacer(QPlainTextEdit):
    returnPressed = pyqtSignal()
    # add-on "symbols as you type" depends on this signal
    # which is emited from the embeded lineEdit of a 
    # qcombobox
    textEdited = pyqtSignal(str)  

    
    def __init__(self, parent):
        self.parent = parent
        self.browser = parent
        self.col = self.browser.col
        super(ComboReplacer, self).__init__(parent)
        self.makeConnectionsEtc()

    def lineEdit(self):
        return self

    def setText(self, arg):
        self.setPlainText(arg)

    def text(self):
        return self.toPlainText().replace("\n", " ")

    def setCompleter(self, arg):
        pass

    def addItems(self, list_):
        pass
    
    def clear(self):
        # _onSearchActivated clears but I don't need this here
        pass

    def cursorPosition(self):
        # needed for symbols as you type
        return self.textCursor().position()

    def setCursorPosition(self, pos):
        # needed for symbols as you type
        cursor = self.textCursor()
        cursor.setPosition(pos)
        self.setTextCursor(cursor)



    def makeConnectionsEtc(self):
        self.textChanged.connect(self.text_change_helper)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Space and gc("-Multiline bar Auto Search on space (only for Anki versions <=2.1.40)") and pointVersion() < 41:
            _onSearchActivated_dont_add_to_history(self.browser)
        # modshift = True if (mw.app.keyboardModifiers() & Qt.ShiftModifier) else False
        # modctrl = True if (mw.app.keyboardModifiers() & Qt.ControlModifier) else False
        modalt = True if (mw.app.keyboardModifiers() & Qt.AltModifier) else False
        if modalt and key in (Qt.Key_Return, Qt.Key_Enter):
            #self.returnPressed.emit()  # doesn't work - needed for add-ons?
            
            if gc("-Multiline bar Auto Search on space (only for Anki versions <=2.1.40)") and pointVersion() < 41:
                _onSearchActivated_dont_add_to_history(self.browser)
            # I use this complicated way for two reasons: It was very quick to make because
            # I could reuse code I have. It was quicker than finding out how the
            # pyqtSignal returnPressed would behave, etc.
            self.insert_newline()
        elif key in (Qt.Key_Return, Qt.Key_Enter):
            self.browser.onSearchActivated()
        else:
            super().keyPressEvent(event)

    def insert_newline(self):
        all_text = self.toPlainText()
        pos = self.textCursor().position()
        new = all_text[:pos] + "\n" + all_text[pos:]
        self.setPlainText(new)
        cursor = self.textCursor()
        cursor.setPosition(pos+1)
        self.setTextCursor(cursor)

    def text_change_helper(self):
        pos = self.textCursor().position()
        out = onSearchEditTextChange(
            parent=self,
            move_dialog_in_browser=False,
            include_filtered_in_deck=True,
            func_gettext=self.toPlainText,
            func_settext=self.setPlainText,
            cursorpos=pos,
            mw=self.browser.mw,
            col=self.browser.col,
            )
        if out:
            newpos, triggersearch = out
            cursor = self.textCursor()
            cursor.setPosition(newpos)
            self.setTextCursor(cursor)
            if triggersearch:
                self.browser.onSearchActivated()
        self.textEdited.emit(self.toPlainText())  # needed for "Symbols as you type"
