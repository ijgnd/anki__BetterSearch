from aqt.qt import *

from aqt import mw


def gc(arg, fail=False):
    # if arg == "modifier for override autosearch default":
    #     return "Shift"
    # elif arg == "modifier for override add * default":
    #     return "Meta"
    # elif arg == "modifier for negate":
    #     return "Alt"
    # elif arg == "modifier for insert current text only":
    #     return "Ctrl"
    conf = mw.addonManager.getConfig(__name__)
    if conf:
        return conf.get(arg, fail)
    else:
        return fail

# conf_to_key = {
#     "Shift": Qt.ShiftModifier
#     "Ctrl": Qt.ControlModifier
#     "Alt": Qt.AltModifier
#     "Meta": Qt.MetaModifier
# }

# shiftmod = self.mw.app.keyboardModifiers() & Qt.ShiftModifier
# ctrlmod = self.mw.app.keyboardModifiers() & Qt.ControlModifier
# altmod = self.mw.app.keyboardModifiers() & Qt.AltModifier
# metamod = self.mw.app.keyboardModifiers() & Qt.MetaModifier

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
