"""
for copyright information & licensing information see
new/__init__.py resp old/__init__.py
"""

import datetime
import importlib
import json
import os
import shutil

from aqt import mw


def load_module(name):
    try:
        module = importlib.import_module(f".{name}", package=__name__)
    except ImportError as e:
        print(f"Error importing module for version '{name}': {e}")
        pass
    else:
        if hasattr(module, "main"):
            module.main()
        else:
            print(f"Error: The module '{module.__name__}' does not define a main() function.")
            pass


def backup_this_conf(arg):
    conf = mw.addonManager.getConfig(__name__)
    path = NEW_USER_CONF_PATH if arg == "new" else OLD_CONF_PATH
    with open(path, mode="w", encoding="utf8") as f:
        json.dump(conf, f)


def write_this_conf_to_meta(arg):
    path = NEW_USER_CONF_PATH if arg == "new" else OLD_CONF_PATH
    if os.path.isfile(NEW_USER_CONF_PATH):
        with open(path, mode="r", encoding="utf8") as f:
            conf = json.load(f)
    else:
        conf = {}
    addon_folder_name = os.path.basename(os.path.dirname(__file__))  # works because I'm in the outer folder
    addon = mw.addonManager.addonFromModule(addon_folder_name)
    meta = mw.addonManager.addonMeta(addon)
    meta["config"] = conf
    mw.addonManager.writeAddonMeta(addon, meta)


def load_new_conf():
    backup_this_conf("old")
    shutil.copy(NEW_CONF_PATH, CONF_PATH)
    write_this_conf_to_meta("new")
    with open(use_this_version, mode="w", encoding="utf8") as f:
        f.write("NEW")


def load_old_conf():
    backup_this_conf("new")
    shutil.copy(OLD_CONF_PATH, CONF_PATH)
    write_this_conf_to_meta("old")
    with open(use_this_version, mode="w", encoding="utf8") as f:
        f.write("OLD")


now = datetime.datetime.today().strftime('%Y-%m-%d__%H:%M:%S')
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
USER_FILES = os.path.join(SCRIPT_DIR, "user_files")

NEW_ABS = os.path.join(SCRIPT_DIR, "new")
OLD_ABS = os.path.join(SCRIPT_DIR, "old")

CONF_PATH = os.path.join(SCRIPT_DIR, "config.json")
NEW_CONF_PATH = os.path.join(NEW_ABS, "config.json")
OLD_CONF_PATH = os.path.join(OLD_ABS, "config.json")

NEW_USER_CONF_PATH = os.path.join(USER_FILES, "config_new")
OLD_USER_CONF_PATH = os.path.join(USER_FILES, "config_old")

use_this_version = os.path.join(USER_FILES, "use_this_version")


if os.path.isfile(use_this_version):
    with open(use_this_version) as f:
        content = f.read().strip()
        if content == "NEW":
            shutil.copy(NEW_CONF_PATH, CONF_PATH)
            load_module("new")
        elif content == "OLD":
            shutil.copy(OLD_CONF_PATH, CONF_PATH)
            load_module("old")
else:
    if not os.path.exists(USER_FILES):
        os.makedirs(USER_FILES)
    with open(use_this_version, "w") as f:
        f.write("NEW")

    # backup old user custom config (changes from old default)
    # it's not enough to read the config key from the addon meta because a user
    # might have an unchanged config. 
    shutil.copy(OLD_CONF_PATH, CONF_PATH)
    conf = mw.addonManager.getConfig(__name__)
    with open(OLD_USER_CONF_PATH, "w") as f:
        json.dump(conf, f)

    shutil.copy(NEW_CONF_PATH, CONF_PATH)
    load_module("new")
