from aqt.qt import (
    Qt,
)

from aqt import mw


def gc(arg, fail=False):
    conf = mw.addonManager.getConfig(__name__)
    if conf:
        return conf.get(arg, fail)
    else:
        return fail


def shiftdown():
    return mw.app.keyboardModifiers() & Qt.ShiftModifier


def ctrldown():
    return mw.app.keyboardModifiers() & Qt.ControlModifier


def altdown():
    return mw.app.keyboardModifiers() & Qt.AltModifier


def metadown():
    return mw.app.keyboardModifiers() & Qt.MetaModifier


conf_to_key = {
    "Shift": shiftdown,
    "Ctrl": ctrldown,
    "Alt": altdown,
    "Meta": metadown,
}
