from .onTextChange import onSearchEditTextChange


##### TODO: deduplicate this file with dialog__multi_line

# some changes
def button_helper(self, arg):
    # https://stackoverflow.com/questions/26358945/qt-find-out-if-qspinbox-was-changed-by-user
    self.form.pte = self.form.searchEdit

    self.form.pte.blockSignals(True)
    #self._button_helper(arg)
    _button_helper(self, arg)
    self.form.pte.blockSignals(False)
    self.form.pte.setFocus()


# only change in last line
def _button_helper(self, arg):
    all_text = self.form.pte.toPlainText()
    pos = self.form.pte.textCursor().position()
    before = all_text[:pos]
    after = all_text[pos:]

    if after:
        after = " " + after

    if all_text == "" or before.endswith("\n"):  # if empty or on newline
        spacer = ""
    else:
        spacer = "\n"

    new = before + spacer + arg + after
    self.form.pte.setPlainText(new)

    newpos = pos + len(arg) + len(spacer)
    cursor = self.form.pte.textCursor()
    cursor.setPosition(newpos)
    self.form.pte.setTextCursor(cursor)

    #self.text_change_helper(before=all_text, before_pos=pos)
    text_change_helper(self, before=all_text, before_pos=pos)


# only change: parent=self.parent, -> parent=self
def text_change_helper(self, before=None, before_pos=None):
    pos = self.form.pte.textCursor().position()
    out = onSearchEditTextChange(
        parent=self,
        move_dialog_in_browser=False,
        include_filtered_in_deck=True,
        func_gettext=self.form.pte.toPlainText,
        func_settext=self.form.pte.setPlainText,
        cursorpos=pos,
        mw=self.mw,
        col=self.col,
        )
    if out:
        cursor = self.form.pte.textCursor()
        cursor.setPosition(out[0])
        self.form.pte.setTextCursor(cursor)
    elif before is not None:
        self.form.pte.setPlainText(before)
        cursor = self.form.pte.textCursor()
        cursor.setPosition(before_pos)
        self.form.pte.setTextCursor(cursor)
