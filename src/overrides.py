from aqt import mw
from aqt.qt import (
    Qt,
)

from .config import gc


def shiftdown():
    return mw.app.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier


def ctrldown():
    return mw.app.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier


def altdown():
    return mw.app.keyboardModifiers() & Qt.KeyboardModifier.AltModifier


def metadown():
    return mw.app.keyboardModifiers() & Qt.KeyboardModifier.MetaModifier


conf_to_key = {"Shift": shiftdown, "Ctrl": ctrldown, "Alt": altdown, "Meta": metadown, "not set": lambda: None}


# UNUSED
def overrides():
    # 4 Modifiers = 4 Overrides
    # defaults:
    #   CTRL : insert current text only : already used in dialog
    #   SHIFT: override autosearch default
    #   META : override add * default
    #   ALT  : negate

    lineonly = False
    override_autosearch_default = False
    override_add_star = False
    negate = False

    lineonly = False
    if conf_to_key[gc(["modifier keys", "modifier for insert current text only"], "not set")]():
        lineonly = True
    override_autosearch_default = False
    if conf_to_key[gc(["modifier keys", "modifier for override autosearch default"], "not set")]():
        override_autosearch_default = True
    override_add_star = False
    if conf_to_key[gc(["modifier keys", "modifier for override add * default"], "not set")]():
        override_add_star = True
    negate = False
    if conf_to_key[gc(["modifier keys", "modifier for negate"], "not set")]():
        negate = True
    # print(f"ctrl - lineonly is {lineonly}")
    # print(f"shift - override_autosearch_default is {override_autosearch_default}")
    # print(f"meta - override_add_star is {override_add_star}")
    # print(f"alt - negate is {negate}")
    return lineonly, override_autosearch_default, override_add_star, negate
