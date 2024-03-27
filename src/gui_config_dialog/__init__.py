import copy
import json
import os
from pprint import pprint as pp

from aqt import mw
from aqt.utils import showInfo, tooltip

from .gui_config_dialog import (
    ConfDialog,
)


def read_json_file_abs(file):
    try:
        with open(file, "r") as fp:
            # TODO
            content = json.load(fp)
    except:
        print("Aborting. Error while reading file.")
    else:
        return content


def get_default_conf_for_this_addon(addon_folder_name):
    addon = mw.addonManager.addonFromModule(addon_folder_name)
    return mw.addonManager.addonConfigDefaults(addon)


def gui_config_helper(
        addon_name,
        text_above,
        text_below,
        text_right_side,
        text_about_in_more,
        list_of_dict_keys_as_tuples_that_should_create_sections,
        dict_settings_tuple_to_labels_or_side_explanations_or_tooltips,
        labels_or_side_explanations_threshold,
        dict_settings_and_their_allowed_values,
        conf_gui_type,
        workaround_spacer_height,
    ):

    current_conf = mw.addonManager.getConfig(__name__)
    if not current_conf:
        tooltip("No Config Available. Aborting ...")
        return

    if list_of_dict_keys_as_tuples_that_should_create_sections == "all_level_one":
        list_of_dict_keys_as_tuples_that_should_create_sections = [(l,) for l in list(current_conf.keys())]
    ## nested test:
    # list_of_dict_keys_as_tuples_that_should_create_sections.extend([("misc", "regex replacements while typing")])

    addon_abs_path = os.path.dirname(os.path.dirname(__file__))
    addon_folder_name = os.path.basename(addon_abs_path)
    schema = read_json_file_abs(os.path.join(addon_abs_path, "config.schema.json"))
    if not schema:
        schema = {}


    default_conf = get_default_conf_for_this_addon(addon_folder_name)
    nested_DEFAULT_conf_list = []
    for key, val in default_conf.items():
        nested_DEFAULT_conf_list.append([key, "", copy.deepcopy(val), ""])

    if text_right_side == "config.md":
        config_md_abs = os.path.join(addon_abs_path, "config.md")
        if os.path.isfile(config_md_abs):
            with open(config_md_abs) as f:
                text_right_side = f.read()

    d = ConfDialog(
        parent=mw,
        addon_name="BetterSearch",
        window_title="Anki: Add-on Config for '{addon_name}'",
        context=f"{addon_name}Config",  # at the moment only used to remember the dialog size
        text_above=text_above,
        text_below=text_below,
        text_right_side=text_right_side,
        text_about_in_more=text_about_in_more,
        current_conf=current_conf,
        default_conf=default_conf,
        schema=schema,
        list_of_dict_keys_as_tuples_that_should_create_sections=list_of_dict_keys_as_tuples_that_should_create_sections,
        dict_settings_tuple_to_labels_or_side_explanations_or_tooltips=dict_settings_tuple_to_labels_or_side_explanations_or_tooltips,
        labels_or_side_explanations_threshold=labels_or_side_explanations_threshold,
        dict_settings_and_their_allowed_values=dict_settings_and_their_allowed_values,
        conf_gui_type=conf_gui_type,
        workaround_spacer_height=workaround_spacer_height,
    )
    if d.exec():
        mw.addonManager.writeConfig(__name__, d.new_conf)
