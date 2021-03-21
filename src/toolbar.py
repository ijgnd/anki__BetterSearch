# -*- coding: utf-8 -*-
# Copyright (c) 2020 Lovac42
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


from aqt import QMenu


def getMenu(parent, menuName):
    menubar = parent.form.menubar
    for a in menubar.actions():
        if menuName == a.text():
            return a.menu()
    else:
        return menubar.addMenu(menuName)


def getAction(parent, actionName):
    menubar = parent.form.menubar
    for a in menubar.actions():
        if actionName == a.text():
            return a
    else:
        return menubar.addAction(actionName)
