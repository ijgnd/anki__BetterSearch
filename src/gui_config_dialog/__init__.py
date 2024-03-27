import json
import os
from pprint import pprint as pp

from aqt import mw
from aqt.utils import tooltip

from .gui_config_dialog import (
    ConfDialog,
)


def read_json_file_abs(file):
    try:
        with open(file, encoding="utf8") as fp:
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
        text_above="",
        text_below="",
        text_right_side="config.md",
        text_about_in_more="",
        list_of_dict_keys_as_tuples_that_should_create_sections=[],
        dict_settings_tuple_to_labels_or_side_explanations_or_tooltips={},
        labels_or_side_explanations_threshold=60,
        dict_settings_and_their_allowed_values={},
        workaround_spacer_height=125,
        conf_gui_type="CollapsibleSections",  # or "GroupBoxes"
    ):
    addon_abs_path = os.path.dirname(os.path.dirname(__file__))
    addon_folder_name = os.path.basename(addon_abs_path)
    default_conf = get_default_conf_for_this_addon(addon_folder_name)
    current_conf = mw.addonManager.getConfig(__name__)
    if not current_conf:
        tooltip("No Config Available. Aborting ...")
        return

    if list_of_dict_keys_as_tuples_that_should_create_sections == "all_level_one":
        list_of_dict_keys_as_tuples_that_should_create_sections = [(l,) for l in list(current_conf.keys())]
    ## nested test:
    # list_of_dict_keys_as_tuples_that_should_create_sections.extend([("misc", "regex replacements while typing")])

    schema = read_json_file_abs(os.path.join(addon_abs_path, "config.schema.json"))
    if not schema:
        schema = {}

    if text_right_side == "config.md":
        config_md_abs = os.path.join(addon_abs_path, "config.md")
        if os.path.isfile(config_md_abs):
            with open(config_md_abs, encoding="utf8") as f:
                text_right_side = f.read()
        else:
            # avoid getting the text "config.md" on top of the dialog ...
            text_right_side = ""

    addon_name = ""
    places_for_name = ["meta.json", "manifest.json"]
    for file in places_for_name:
        if not addon_name:
            file_abs_path = os.path.join(addon_abs_path, file)
            if os.path.isfile(file_abs_path):
                with open(file_abs_path, encoding="utf8") as f:
                    try:
                        d = json.load(f)
                    except json.JSONDecodeError as e:
                        print(f"error while reading file {file}:\n    {e}")
                    addon_name = d.get("name", "")

    d = ConfDialog(
        parent=mw,
        addon_name="BetterSearch",
        window_title=f"Anki: Add-on Config for '{addon_name}'",
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
