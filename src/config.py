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


def wcs(key, new_val, addnew=False):
    config = mw.addonManager.getConfig(__name__)
    if not config:
        return
    if not (key in config or addnew):
        return
    else:
        config[key] = new_val
        mw.addonManager.writeConfig(__name__, config)
        return True


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
}
