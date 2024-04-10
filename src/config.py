from aqt import mw


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


from .gui_config_dialog import gui_config_helper


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


# I'm assuming you rarely need an explanation. So I think a flat dict
# with tuples is simpler than a nested dict that mirrors your full conf
# or reading from a config.schema.json
explanations_dict = {
    # ("misc", "config dialog style"): "This settings allows you change how the gui config dialog looks like",
}


# I'm assuming you rarely have limited allowed values. So I think a flat dict
# with tuples is simpler than a nested dict that mirrors your full conf
# or reading from a config.schema.json
allowed_values_dict = {("misc", "config dialog style"): ["GroupBoxes", "CollapsibleSections"]}


def on_settings():
    gui_config_helper(
        text_above="",
        text_below="",
        text_right_side="config.md",
        ankiwebview_for_right=True,
        text_about_in_more=text_about_in_more,
        list_of_dict_keys_as_tuples_that_should_create_sections="all_level_one",
        dict_settings_tuple_to_labels_or_side_explanations_or_tooltips=explanations_dict,
        labels_or_side_explanations_threshold=60,
        dict_settings_and_their_allowed_values=allowed_values_dict,
        workaround_spacer_height=125,
        conf_gui_type=gc(["misc", "config dialog style"]),  # allowed: "CollapsibleSections" (default), "GroupBoxes"
        import_setting_text="""misc->'use gui config window instead of built-in dialog'""",
        import_setting_value=False,
    )


if gc(["misc", "use gui config window instead of built-in dialog"]):
    mw.addonManager.setConfigAction(__name__, on_settings)
