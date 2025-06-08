import os

from aqt import mw
from aqt.utils import showInfo


def get_default_conf_for_this_addon(addon_folder_name):
    addon = mw.addonManager.addonFromModule(addon_folder_name)
    return mw.addonManager.addonConfigDefaults(addon)


old_conf_up_to_202303_to_new_conf_dict = {
    "--aliases Replace while typing": ["regex replacements while typing", "matching with normal strings: active"],
    "--aliases dictionary": ["regex replacements while typing", "matching with normal strings: dictionary"],
    "--aliases_regex Replace while typing": [
        "regex replacements while typing",
        "matching with regular expressions strings: active",
    ],
    "--aliases_regex dictionary": [
        "regex replacements while typing",
        "matching with regular expressions strings: dictionary",
    ],
    # "-Add Button to the Browser Search Bar": None,
    # "-Modify Search Bar": None,
    # "-Multiline bar Auto Search on space (only for Anki versions <=2.1.40)": None,
    # "-Multiline bar Height relative to default (when shown in Browser)": None,
    # "-Shortcut for Multi-bar mode: show fuzzy menu": None,
    "Multiline Dialog: use bigger typewriter font": [
        "multiline search window",
        "Multiline Dialog: use bigger typewriter font",
    ],
    "Multiline Dialog: shortcut: open window": ["browser shortcuts", "Multiline Dialog: shortcut: open window"],
    # "Multiline Dialog: show Filter Button (only for Anki versions <=2.1.40)": None,
    # "Multiline Dialog: show Button Bar": ["multiline search window", "Multiline Dialog: show Button Bar"],
    # "Multiline Dialog: Shortcut inside: Open History": None,  # do not reuse strange Alt+h
    # "also use in create filtered deck dialog": None,  # Now I always do this.
    # "autoadjust FilterDialog position": ["filter dialog", "autoadjust FilterDialog position"],
    "custom tag&deck string 1": ["custom search operators for custom filter dialogs", "custom tag&deck string 1"],
    "custom tag&deck string 2": ["custom search operators for custom filter dialogs", "custom tag&deck string 2"],
    "date range dialog for added: string": [
        "custom search operators for custom filter dialogs",
        "date range dialog for added: string",
    ],
    "date range dialog for edited: string": [
        "custom search operators for custom filter dialogs",
        "date range dialog for edited: string",
    ],
    "date range dialog for introduced: string": [
        "custom search operators for custom filter dialogs",
        "date range dialog for introduced: string",
    ],
    "date range dialog for rated: string": [
        "custom search operators for custom filter dialogs",
        "date range dialog for rated: string",
    ],
    "ignore upper and lower case (case insensitive search)": [
        "filter dialog",
        "filter dialog: ignore upper and lower case (case insensitive search)",
    ],
    "lines shown in filter dialog": ["filter dialog", "filter dialog: lines shown"],
    # "modifier for override autosearch default": None,
    # "modifier for override add * default":  None,
    # "modifier for negate": None,
    # "modifier for insert current text only": None,
    # "modify: window opened by search strings triggers search by default": None,
    "modify_card": ["open filter dialog after typing these search operators", "modify_card"],
    "modify_deck": ["open filter dialog after typing these search operators", "modify_deck"],
    "modify_field": ["open filter dialog after typing these search operators", "modify_field"],
    "modify_flag": ["open filter dialog after typing these search operators", "modify_flag"],
    "modify_flag__show_explanations": [
        "open filter dialog after typing these search operators",
        "modify_flag__show_explanations",
    ],
    "modify_is": ["open filter dialog after typing these search operators", "modify_is"],
    "modify_is__show_explanations": [
        "open filter dialog after typing these search operators",
        "modify_is__show_explanations",
    ],
    "modify_note": ["open filter dialog after typing these search operators", "modify_note"],
    "modify_props": ["open filter dialog after typing these search operators", "modify_props"],
    "modify_tag": ["open filter dialog after typing these search operators", "modify_tag"],
    # "shortcut - focus search box and card selector dialog": None,  # no one is using those and they might interfer with other addons
    # "shortcut - focus search box and deck selector dialog": None,
    # "shortcut - focus search box and note selector dialog": None,
    # "shortcut - focus search box and tag selector dialog": None,
    # "shortcut - focus search box and tag/deck selector dialog": None,
    # "shortcut - focus search box and prop dialog": None,
    # "shortcut - focus search box and is dialog": None,
    # "shortcut - focus search box and card from note dialog": None,
    # "shortcut - focus search box and field from note dialog": None,
    # "shortcut - focus search box and date added dialog": None,
    # "shortcut - focus search box and date edited dialog": None,
    # "shortcut - focus search box and date introduced dialog": None,
    # "shortcut - focus search box and date rated dialog": None,
    # "shortcut - select entry from history in fuzzy dialog": ["browser shortcuts", "shortcut - select entry from history in fuzzy dialog"],
    # "shortcuts trigger search by default": None,
    "tag dialog exit on re:": ["filter dialog", "filter dialog for tags: exit on typing re:"],
    # "tag insertion - add '*' to matches": None,
}


##### update to new config from 2024-04


def update_nested_dict(nested_dict, keys, new_value):
    if len(keys) == 1:
        nested_dict[keys[0]] = new_value
    else:
        key = keys[0]
        if key in nested_dict:
            update_nested_dict(nested_dict[key], keys[1:], new_value)
        else:
            # If the key does not exist, create a new dictionary for it
            nested_dict[key] = {}
            update_nested_dict(nested_dict[key], keys[1:], new_value)


def maybe_update_config():
    old_conf = mw.addonManager.getConfig(__name__)
    if not old_conf:
        return

    if all([isinstance(val, dict) for val in old_conf.values()]):
        # then the new config is already used: fresh install or already updated ...
        return


    # since 3.9 __file__ is always an abspath, see
    # https://stackoverflow.com/questions/7116889/is-module-file-attribute-absolute-or-relative
    addon_folder_name = os.path.basename(os.path.dirname(__file__))
    new_conf = get_default_conf_for_this_addon(addon_folder_name)

    for old_key, new_key in old_conf_up_to_202303_to_new_conf_dict.items():
        old_val = old_conf.get(old_key)
        if old_val:
            update_nested_dict(new_conf, new_key, old_val)

    mw.addonManager.writeConfig(__name__, new_conf)
    msg = "You've installed an update for the addon 'BetterSearch'. The config has changed. Check it."
    showInfo(msg)
