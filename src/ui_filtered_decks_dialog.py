from anki.hooks import wrap
from aqt.dyndeckconf import DeckConf

from .onTextChange import onSearchEditTextChange


# TODO setup shortcuts


def dyn_setup_search(self):
    self.form.search.textChanged.connect(self.onDynSetupSearchEditTextChange)
    self.form.search_2.textChanged.connect(self.onDynSetupSearchEditTextChange)
DeckConf.initialSetup = wrap(DeckConf.initialSetup, dyn_setup_search)


def onDynSetupSearchEditTextChange(self, arg):
    le = self.sender()  # https://stackoverflow.com/a/33981172
    pos = le.cursorPosition()
    ret = onSearchEditTextChange(
        parent=self,
        move_dialog_in_browser=False,
        include_filtered_in_deck=False,
        func_gettext=le.text,
        func_settext=le.setText,
        cursorpos=pos,
        mw=self.mw,
        col=self.mw.col
    )
    if not ret:
        return
    else:
        newpos, triggersearch = ret
        if newpos:
            le.setCursorPosition(newpos)
DeckConf.onDynSetupSearchEditTextChange = onDynSetupSearchEditTextChange
