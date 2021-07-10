from anki.hooks import wrap

from anki.utils import pointVersion

from .onTextChange import onSearchEditTextChange


# TODO setup shortcuts


if pointVersion() <= 44:
    from aqt.dyndeckconf import DeckConf  # noqa

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


else:
    from aqt.filtered_deck import FilteredDeckConfigDialog

    def dyn_setup_search(self):
        self.form.search.textChanged.connect(self.onDynSetupSearchEditTextChange)
        self.form.search_2.textChanged.connect(self.onDynSetupSearchEditTextChange)
    FilteredDeckConfigDialog._initial_dialog_setup = wrap(FilteredDeckConfigDialog._initial_dialog_setup, dyn_setup_search)


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
    FilteredDeckConfigDialog.onDynSetupSearchEditTextChange = onDynSetupSearchEditTextChange
