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


conf_to_key = {
    "Shift": shiftdown,
    "Ctrl": ctrldown,
    "Alt": altdown,
    "Meta": metadown,
    "not set": lambda: None
}


# UNUSED
def overrides():
    # 4 Modifiers = 4 Overrides
    # defaults:
    #   CTRL : insert current text only : already used in dialog
    #   SHIFT: override autosearch default
    #   META : override add * default
    #   ALT  : negate

    lineonly = False
    force_run_search_after = False
    override_add_star = False
    negate = False

    lineonly = False
    if conf_to_key[gc(["modifier keys", "modifier for insert current text only"], "not set")]():
        lineonly = True
    if conf_to_key[gc(["modifier keys", "modifier to trigger search (irrespective of general config)"], "not set")]():
        force_run_search_after = True
    override_add_star = False
    if conf_to_key[gc(["modifier keys", "modifier for override add * default"], "not set")]():
        override_add_star = True
    negate = False
    if conf_to_key[gc(["modifier keys", "modifier for negate"], "not set")]():
        negate = True
    # print(f"lineonly is {lineonly}")
    # print(f"force_run_search_after is {force_run_search_after}")
    # print(f"override_add_star is {override_add_star}")
    # print(f"negate is {negate}")
    return lineonly, force_run_search_after, override_add_star, negate
