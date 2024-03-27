import copy
import json
import os

from aqt import mw
from aqt.utils import showInfo, tooltip

from .dialog__config_helper import (
    ConfDialog,
)


def gc(arg, fail=False):
    conf = mw.addonManager.getConfig(__name__)
    if not conf:
        return fail
    if isinstance(arg, str):
        return conf.get(arg, fail)
    if isinstance(arg, list):
        if len(arg) == 1:
            return conf.get(arg, fail)
        else:  # len 2
            group = conf.get(arg[0])
            if not group:
                return fail
            return group.get(arg[1], fail)


def wcs(key, new_val, addnew=False):
    config = mw.addonManager.getConfig(__name__)
    if not config:
        return
    if isinstance(key, str) or (isinstance(key, list) and len(key) == 1):
        if not (key in config or addnew):
            return
        else:
            config[key] = new_val
            mw.addonManager.writeConfig(__name__, config)
            return True
    elif isinstance(key, list) and len(key) == 2:
        try:
            parent = config.get(key[0])
        except:
            return
        else:
            if not (key[1] in parent or addnew):
                return
            else:
                config[key[0]][key[1]] = new_val
                mw.addonManager.writeConfig(__name__, config)
                return True


def read_json_file_abs(file):
    try:
        with open(file, "r") as fp:
            # TODO
            content = json.load(fp)
    except:
        print("Aborting. Error while reading file.")
    else:
        return content


def get_default_conf_for_this_addon():
    addon = mw.addonManager.addonFromModule("1052724801")  # TODO handle different folder names
    return mw.addonManager.addonConfigDefaults(addon)


old_conf_up_to_202303_to_new_conf_dict = {
    "--aliases Replace while typing": ["regex replacements while typing", "matching with normal strings: enabled"],
    "--aliases dictionary": ["regex replacements while typing", "matching with normal strings: dictionary"],
    "--aliases_regex Replace while typing": [
        "regex replacements while typing",
        "matching with regular expressions strings: enabled",
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
    "modify_is": ["open filter dialog after typing these search operators", "modify_is"],
    "modify_is__show_explanations": ["open filter dialog after typing these search operators", "modify_is__show_explanations"],
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

text_above = """The main functionality of this addon is to show filter dialogs when you type "tag:", "deck:", "xx:" etc. To
close such a dialog just press "Esc".

The Anking made two videos that among other things show older versions of 
this addon. Though a few things have changed in my addon they're still a very useful introduction
to my addon. Watch [Anki: Better Searching Tools](https://www.youtube.com/watch?v=PlcsNIsYc7k) 
and [Anki: How to Find Cards and Tags in the Browser](https://www.youtube.com/watch?v=NHpl-j9pULU).

Most of the settings are not relevant for regular users. You'll find the settings mentioned in
the Anking videos below in the sections "browser shortcuts" and "custom search operators for 
custom filter dialogs" and "open filter dialog after typing these search operators".

Override keys are no longer working in this version. Also some config options from old versions were removed. 
I removed the functionality to just insert the current text from the filter dialog: Just use 
Ctrl+A,Ctrl+C,Esc,Ctrl+V. I also removed the functionality to add a star at the end, just edit the 
inserted string after closing the dialog. Those features were hardly used based on reports I got.
Whether closing the dialog triggers a search can now only be set in the lower left of each filter
dialog by using a checkbox.
"""


text_below = """If you find a bug please notify me by posting in the [add-on support 
thread in the official forum](https://forums.ankiweb.net/t/browser-search-box-quick-insert-tag-deck-notetype-official-thread/547). 
If you post somewhere else (like a new thread, addon rating, etc.) I won't be notified and I will miss your report."""


text_about_in_more = """Credits:

This add-on was made by ijgnd. I've used some code made by other people:

The filter dialog is made of source code in the files filter_dialog.py and split_string.py. Most of
the code inside these files was originally made by Rene Schallner for his 
https://github.com/renerocksai/sublimeless_zk. I made some changes to these files. For details
see the top of the two aforementioned files. These files are licensed as GPLv3.

The code from highlight_delegate.py is adopted from https://stackoverflow.com/a/53357083 (Copyright (c): 2018 eyllanesc, CC BY-SA 4.0)

The code from auto-resizing-text-edit.py is adopted from https://github.com/cameel/auto-resizing-text-edit (Copyright (c): 2013 Kamil Śliwak, MIT License)

the class CollapsibleSection in collapsible_section_for_qwidget.py is adopted from https://github.com/MichaelVoelkel/qt-collapsible-section/blob/master/Section.py ((c) 2016 Michael A. Voelkel - michael.alexander.voelkel@gmail.com).

This add-on uses the files "sakura.css" and "sakura-dark.css" from https://github.com/oxalorg/sakura
(Copyright (c) 2016 Mitesh Shah, MIT License).
"""


addon_path = os.path.dirname(__file__)
user_files_folder = os.path.join(addon_path, "user_files")


def on_settings():
    current_conf = mw.addonManager.getConfig(__name__)
    if not current_conf:
        tooltip("No Config Available. Aborting ...")
        return

    list_of_dict_keys_as_tuples_that_should_create_sections = [(l,) for l in list(current_conf.keys())]
    list_of_dict_keys_as_tuples_that_should_create_sections.append(("misc", "nested test"))
    # list_of_dict_keys_as_tuples_that_should_create_sections = [("misc",)]
    # list_of_dict_keys_as_tuples_that_should_create_sections = [("misc",), ("misc", "nested test")]

    # I'm assuming you rarely need an explanation. So I think a flat dict
    # with tuples is simpler than a nested dict that mirrors your full conf
    # or reading from a config.schema.json
    explanations_dict = {
        # ("misc", "config dialog style"): "This settings allows you change how the gui config dialog looks like",
        # ("misc",): "This text should go the right side. Bla sdfas fasdf asfasd fasdf asdf asdf asdf asdf asdf asdf sadf sadf ",
        # ("browser shortcuts",): "label",
    }

    # I'm assuming you rarely have limited allowed values. So I think a flat dict
    # with tuples is simpler than a nested dict that mirrors your full conf
    # or reading from a config.schema.json
    allowed_values_dict = {("misc", "config dialog style"): ["GroupBoxes", "CollapsibleSections"]}
    print(f"allowed_values_dict is --{type(allowed_values_dict)}--")

    nested_dialog_conf_list = []
    for key, val in current_conf.items():
        nested_dialog_conf_list.append([key, "", copy.deepcopy(val), ""])

    default_conf = get_default_conf_for_this_addon()
    nested_DEFAULT_conf_list = []
    for key, val in default_conf.items():
        nested_DEFAULT_conf_list.append([key, "", copy.deepcopy(val), ""])

    schema = read_json_file_abs(os.path.join(addon_path, "config.schema.json"))
    if not schema:
        schema = {}

    d = ConfDialog(
        parent=mw,
        addon_name="BetterSearch",
        window_title="Anki BetterSearch Add-on Config",
        context="BettersearchConfig",
        text_above="",
        text_below="",
        text_right_side=text_below + "\n\n" + text_above,
        text_about_in_more=text_about_in_more,
        current_conf=current_conf,
        default_conf=default_conf,
        schema=schema,
        list_of_dict_keys_as_tuples_that_should_create_sections=list_of_dict_keys_as_tuples_that_should_create_sections,
        dict_settings_tuple_to_labels_or_side_explanations_or_tooltips=explanations_dict,
        labels_or_side_explanations_threshold=60,
        dict_settings_and_their_allowed_values=allowed_values_dict,
        conf_gui_type=gc(["misc", "config dialog style"]),
    )
    if d.exec():
        mw.addonManager.writeConfig(__name__, d.new_conf)


if gc(["misc", "use gui config window instead of built-in dialog"]):
    mw.addonManager.setConfigAction(__name__, on_settings)


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

    new_conf = get_default_conf_for_this_addon()

    for old_key, new_key in old_conf_up_to_202303_to_new_conf_dict.items():
        old_val = old_conf.get(old_key)
        if old_val:
            update_nested_dict(new_conf, new_key, old_val)

    mw.addonManager.writeConfig(__name__, new_conf)
    msg = "You've installed an update for the addon 'BetterSearch'. The config has changed. Check it."
    showInfo(msg)
