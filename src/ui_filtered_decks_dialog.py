from anki.hooks import wrap

from .onTextChange import onSearchEditTextChange


# TODO setup shortcuts


from aqt.filtered_deck import FilteredDeckConfigDialog


def dyn_setup_search(self):
    # self is filtered_deck.FilteredDeckConfigDialog
    self.form.search.textChanged.connect(self.onDynSetupSearchEditTextChange)
    self.form.search_2.textChanged.connect(self.onDynSetupSearchEditTextChange)


FilteredDeckConfigDialog._initial_dialog_setup = wrap(FilteredDeckConfigDialog._initial_dialog_setup, dyn_setup_search)


def onDynSetupSearchEditTextChange(self, arg):
    # self is filtered_deck.FilteredDeckConfigDialog
    le = self.sender()  # https://stackoverflow.com/a/33981172
    pos = le.cursorPosition()
    newtext, newpos, triggersearch = onSearchEditTextChange(
        parent=self,
        move_dialog_in_browser=False,
        include_filtered_in_deck=False,
        input_text=le.text(),
        cursorpos=pos,
    )
    if newtext is None:
        return
    else:
        le.setText(newtext)
        if newpos:
            le.setCursorPosition(newpos)


FilteredDeckConfigDialog.onDynSetupSearchEditTextChange = onDynSetupSearchEditTextChange
