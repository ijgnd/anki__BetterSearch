from .onTextChange import onSearchEditTextChange


# some changes
def button_helper(pte, parent, mw, col, arg, remove_on_cancel=True):
    # pte = QPlainTextEdit-Instance, 
    # arg = string inserted by button that will later be processed
    #       by onSearchEditTextChange

    # https://stackoverflow.com/questions/26358945/qt-find-out-if-qspinbox-was-changed-by-user
    pte.blockSignals(True)
    _button_helper(pte, parent, mw, col, arg, remove_on_cancel)
    pte.blockSignals(False)
    pte.setFocus()


def _button_helper(pte, parent, mw, col, arg, remove_on_cancel):
    all_text = pte.toPlainText()
    pos = pte.textCursor().position()
    before = all_text[:pos]
    after = all_text[pos:]

    if after:
        after = " " + after

    if all_text == "" or before.endswith("\n"):  # if empty or on newline
        spacer = ""
    else:
        spacer = "\n"

    new = before + spacer + arg + after
    pte.setPlainText(new)

    newpos = pos + len(arg) + len(spacer)
    cursor = pte.textCursor()
    cursor.setPosition(newpos)
    pte.setTextCursor(cursor)

    if not remove_on_cancel:
        all_text = new
        pos = newpos

    text_change_helper(pte, parent, mw, col, before=all_text, before_pos=pos)


# only change: parent=self.parent, -> parent=self
def text_change_helper(pte, parent, mw, col, before=None, before_pos=None):
    pos = pte.textCursor().position()
    out = onSearchEditTextChange(
        parent=parent,
        move_dialog_in_browser=False,
        include_filtered_in_deck=True,
        func_gettext=pte.toPlainText,
        func_settext=pte.setPlainText,
        cursorpos=pos,
        mw=mw,
        col=col,
        )
    if out:
        cursor = pte.textCursor()
        cursor.setPosition(out[0])
        pte.setTextCursor(cursor)
    elif before is not None:
        pte.setPlainText(before)
        cursor = pte.textCursor()
        cursor.setPosition(before_pos)
        pte.setTextCursor(cursor)
