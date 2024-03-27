import datetime
from functools import reduce
import json
from operator import getitem
from pprint import pprint as pp

import aqt
from aqt.qt import (
    QCheckBox,
    QComboBox,
    QCursor,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QKeySequenceEdit,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    Qt,
    QVBoxLayout,
    QWidget,
)
from aqt.theme import theme_manager
from aqt.utils import (
    askUser,
    getFile,
    getSaveFile,
    restoreGeom,
    saveGeom,
    showInfo,
    showText,
    tooltip,
)

# from aqt.webview import AnkiWebView, AnkiWebViewKind

from .auto_resizing_text_widget import AutoResizingTextEdit, AutoResizingTextBrowser
from .collapsible_section_for_qwidget import CollapsibleSection


# class MyListEdit(QPlainTextEdit):
class MyListEdit(AutoResizingTextEdit):
    pass


# class MyDictEdit(QPlainTextEdit):
class MyDictEdit(AutoResizingTextEdit):
    pass


def gui_select_json_file_and_return_content(parent, window_title):
    file = getFile(
        parent=parent,
        title=window_title,
        cb=None,
        filter="*.json",
        dir=None,
        key=".json",
        multi=False,  # I only want one file
    )
    if not file:
        return
    try:
        with open(file, "r") as fp:
            content = json.load(fp)
    except:
        showInfo("Aborting. Error while reading file.")
    else:
        return content


def export_config_to_file(parent, addon_name, conf):
    CurrentDT = datetime.datetime.now()
    cur_time_string = CurrentDT.strftime("%Y-%m-%dT%H-%M-%S")
    save_path = getSaveFile(
        parent=parent,
        title="Export Config of AnkiAddon %s" % addon_name,  # windowtitle
        dir_description="addon_config_save__bettersearch",  # used to remember last user choice
        key="config as json",
        ext="json",
        fname="Anki_AddonConfig__BetterSearch__%s.json" % cur_time_string,
    )
    if not save_path:
        return
    aqt.mw.progress.start(immediate=True)
    try:
        with open(save_path, mode="w", encoding="utf-8") as file:
            # json.dump(conf, file)
            fmt = json.dumps(conf, indent=4, sort_keys=True)
            file.write(fmt)
    finally:
        aqt.mw.progress.finish()
        tooltip('Config File saved to "%s"' % str(save_path), period=5000)


def json_formatted_as_in_anki_addon_conf(val):
    return json.dumps(
        val,
        ensure_ascii=False,
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
    )


def get_value(widget):
    """
    either returns Success, value
    or False, expected type string
    """
    if isinstance(widget, QCheckBox):
        val = widget.isChecked()
    elif isinstance(widget, QSpinBox):
        val = widget.value()
    elif isinstance(widget, QDoubleSpinBox):
        val = widget.value()
    elif isinstance(widget, QLabel):
        val = widget.text()
    elif isinstance(widget, QLineEdit):
        val = widget.text()
    elif isinstance(widget, QKeySequenceEdit):
        val = widget.keySequence().toString()
    elif isinstance(widget, QComboBox):
        val = widget.currentText()
    elif isinstance(widget, MyListEdit):
        text = widget.toPlainText()
        try:
            data = json.loads(text)
        except:
            return False, f"not a list: --{text}--"
        else:
            val = data
    elif isinstance(widget, MyDictEdit):
        text = widget.toPlainText()
        try:
            # note: difference python-dict to json
            # a dict can look like this: {1:2}
            # in json {1:2} gives the error: Expecting property name enclosed in double quotes
            data = json.loads(text)
        except json.JSONDecodeError as err:
            # maybe add more info, see e.g. addons.py or https://stackoverflow.com/a/35150895
            return False, err
        else:
            val = data
    elif isinstance(widget, QWidget):
        val = None
        print("get_value: widget is just an instance of QWidget ...")
    return True, val


# Sort a nested dictionary and all its sub-dictionaries alphabetically
def sort_nested_dict_alphabetically(d):
    if isinstance(d, dict):
        return {k: sort_nested_dict_alphabetically(v) for k, v in sorted(d.items())}
    else:
        return d


def get_nested_value(source_dict, keys):
    """
    source_dict: the dictionary you're querying
    keys: tuple of keys representing the path to the value you want to retrieve
    The  reduce function applies getitem to the dictionary and each key in the tuple, effectively 
    navigating through the nested dictionaries. If any key in the path does not exist, a 
    KeyError is raised, which is caught and handled by returning None.
    """
    try:
        return reduce(getitem, keys, source_dict)
    except KeyError:
        return None


# P: multiple nested don't really work: the spacing is not properly adjusted in the parent dialogs
#    so breaks when longer nested settings on second level
#    -> signal to resize parent or another spacer workaround?
# P: import
class ConfDialog(QDialog):
    silentlyClose = True

    def __init__(
        self,
        parent,
        addon_name,
        window_title,
        context,
        text_above,
        text_below,
        text_right_side,
        text_about_in_more,
        current_conf,
        default_conf,
        schema,
        list_of_dict_keys_as_tuples_that_should_create_sections,
        dict_settings_tuple_to_labels_or_side_explanations_or_tooltips,
        labels_or_side_explanations_threshold,
        dict_settings_and_their_allowed_values,
        conf_gui_type,
    ):
        # super().__init__(parent)
        QDialog.__init__(self, parent, Qt.WindowType.Window)
        aqt.mw.garbage_collect_on_dialog_finish(self)

        self.parent = parent
        self.addon_name = addon_name
        self.window_title = window_title
        self.context = context
        self.text_above = text_above
        self.text_below = text_below
        self.text_right_side = text_right_side
        self.text_about_in_more = text_about_in_more
        self.conf = current_conf
        self.default_conf = default_conf
        self.schema = schema
        self.list_of_sections = list_of_dict_keys_as_tuples_that_should_create_sections
        self.dict_explanations = dict_settings_tuple_to_labels_or_side_explanations_or_tooltips
        self.labels_or_side_explanations_threshold = labels_or_side_explanations_threshold
        self.dict_allowed_values = dict_settings_and_their_allowed_values
        self.conf_gui_type = conf_gui_type

        self.check_input()
        self.conf = sort_nested_dict_alphabetically(self.conf)
        self.default_conf = sort_nested_dict_alphabetically(self.default_conf)
        self.dialog_dict_with_widgets, outer_widget = self.process_conf(
            self.conf, tuple(), QWidget(), self.text_right_side
        )
        scrollArea = QScrollArea()
        scrollArea.setWidget(outer_widget)
        scrollArea.setWidgetResizable(True)
        scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.center_area_widget = scrollArea
        self.setup_ui()
        self.resize(1000, 700)
        restoreGeom(self, self.context)

    def process_conf(self, this_conf_dict, this_conf_key, outer_widget, desc_or_right_text):
        print(f"\n\n\n\n\n...........in process_conf and this_conf_key is --{this_conf_key}--")
        out_dict = {}
        outer_layout = QVBoxLayout()
        form_layout = False
        has_text_edit = False
        has_no_collapsible = True

        for key, val in this_conf_dict.items():
            this_full_key = this_conf_key + (key,)
            allowed_members = self.dict_allowed_values.get(this_full_key)
            if allowed_members:
                print(f"---allowed_members is {allowed_members} for key {key}")
            explan_text = self.dict_explanations.get(this_full_key)
            # print(f"...this_full_key is {this_full_key}")
            if isinstance(val, dict) and this_full_key in self.list_of_sections:
                has_no_collapsible = False
                is_section = True
                widget_with_conf_val = False
                if self.conf_gui_type == "CollapsibleSections":
                    inner_widget = CollapsibleSection(title=key, parent=self)
                else:
                    inner_widget = QGroupBox(key, parent=self)
                default_value = None
                cur_val, inner_widget = self.process_conf(
                    this_conf_dict=val,
                    this_conf_key=this_full_key,
                    outer_widget=inner_widget,
                    desc_or_right_text=explan_text,
                )
                if form_layout:  # previously created form layout needs to be added before adding a section
                    outer_layout.addLayout(form_layout)
                outer_layout.addWidget(inner_widget)  # CollapsibleSection
                form_layout = False
            else:
                is_section = False
                cur_val = val
                default_value = get_nested_value(self.default_conf, this_full_key)

                if not form_layout:
                    form_layout = QFormLayout()
                widget_with_conf_val, has_text_edit = self.set_row_in_form_layout(
                    form_layout, this_full_key, allowed_members, key, val, has_text_edit, explan_text
                )
            inner_dict = {
                "is_section": is_section,
                "current_value": cur_val,
                "default_value": default_value,
                "explan_text": explan_text,
                "allowed_members": allowed_members,
                "widget": widget_with_conf_val,
            }
            out_dict[key] = inner_dict
        if form_layout:
            outer_layout.addLayout(form_layout)
            if has_text_edit:
                # this is an ugly workaround for the problem that otherwise the text_edit
                # is too small. A proper solution would be to resize the parent which should
                # be some work (if it's the custom collapsible element I use)
                # width(int), heigt(int), hPolicy(QSizePolicy), vPolicy(QSizePolicy)
                spacer = QSpacerItem(10, 125, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
                outer_layout.addItem(spacer)
        if not has_no_collapsible:
            # this is an ugly workaround for two problems:
            #  - otherwise when collapsible is mixed with regular key-val conf on same level there's too
            #    much spacing around the non collapsible elements, i.e. the rows are not aligned to the top.
            #  - avoid too much space at bottom of collapsible
            # width(int), heigt(int), hPolicy(QSizePolicy), vPolicy(QSizePolicy)
            spacer = QSpacerItem(10, 125, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
            outer_layout.addItem(spacer)

        if not desc_or_right_text:
            top_layout = outer_layout
        else:
            if len(desc_or_right_text) < self.labels_or_side_explanations_threshold:
                top_layout = QVBoxLayout()
                label = QLabel(f"<i>{desc_or_right_text}</i>")
                label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
                top_layout.addWidget(label)
                top_layout.addLayout(outer_layout)
            else:  # long explanations go to the sides.
                top_layout = QHBoxLayout()
                helper_widget = QWidget()
                helper_widget.setLayout(outer_layout)
                sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                sizePolicy.setHorizontalStretch(5)
                sizePolicy.setVerticalStretch(0)
                helper_widget.setSizePolicy(sizePolicy)
                top_layout.addWidget(helper_widget)
                help_text = self.get_read_only_auto_resizing_text_widget(desc_or_right_text)
                sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                sizePolicy.setHorizontalStretch(2)
                sizePolicy.setVerticalStretch(0)
                help_text.setSizePolicy(sizePolicy)
                top_layout.addWidget(help_text)
        if isinstance(outer_widget, CollapsibleSection):
            # https://doc.qt.io/qt-6/qspaceritem.html#QSpacerItem
            # width(int), heigt(int), hPolicy(QSizePolicy), vPolicy(QSizePolicy)
            # spacer = QSpacerItem(10, 25, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
            # outer_layout.addItem(spacer)
            outer_widget.setContentLayout(top_layout)
        else:
            outer_widget.setLayout(top_layout)
        return out_dict, outer_widget

    def check_input(self):
        pass
        # TODO
        # e.g.
        # - dict_keys_that_should_create_sections must be in self.conf and be dicts
        # - labels_or_side_explanations_threshold: keys must be in self.conf
        # - dict_settings_and_their_allowed_values: keys must be in self.conf

    def setup_ui(self):
        if self.window_title:
            self.setWindowTitle(self.window_title)

        if self.text_above:
            self.info_text_top = self.get_read_only_auto_resizing_text_widget(self.text_above)
        if self.text_below:
            self.info_text_bottom = self.get_read_only_auto_resizing_text_widget(self.text_below)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.exportButton = QPushButton("More")
        self.exportButton.setAutoDefault(False)
        self.buttonBox.addButton(self.exportButton, QDialogButtonBox.ButtonRole.HelpRole)
        self.exportButton.clicked.connect(self.show_export_import_menu)

        self.outer_layout = QVBoxLayout()
        if self.text_above:
            self.outer_layout.addWidget(self.info_text_top)
        self.outer_layout.addWidget(self.center_area_widget)
        if self.text_below:
            self.outer_layout.addWidget(self.info_text_bottom)
        self.outer_layout.addWidget(self.buttonBox)
        self.setLayout(self.outer_layout)

    def get_read_only_auto_resizing_text_widget(self, text):
        text_widget = AutoResizingTextBrowser()
        text_widget.setMarkdown(text)
        text_widget.setReadOnly(True)
        ### The following parts don't work with the Anki styling (native styling should work):
        # color = self.palette().color(QPalette.ColorRole.Window)
        # palette = text_widget.viewport().palette()
        # palette.setColor(text_widget.viewport().backgroundRole(), color)
        # palette.setColor(text_widget.viewport().backgroundRole(), None)  # needds qcolor - can't remove like this
        # text_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # text_widget.viewport().setPalette(palette)
        ### So I use:
        bgcol = "#2C2C2C" if theme_manager.night_mode else "#F5F5F5"
        text_widget.setStyleSheet(
            f"""
QTextEdit, QListView {{
    background-color: {bgcol} !important;
    border:none;

}}
"""
        )
        text_widget.setFrameStyle(QFrame.Shape.NoFrame)  # no border
        return text_widget

    def show_export_import_menu(self):
        menu = QMenu(self)
        # menu.setStyleSheet(stylesheet)
        action_export = menu.addAction("Export")
        action_export.triggered.connect(self.on_export)
        action_import = menu.addAction("Import")
        action_import.triggered.connect(self.on_import)
        action_reset = menu.addAction("reset to default values")
        action_reset.triggered.connect(self.on_restore)
        action_about = menu.addAction("About")
        action_about.triggered.connect(self.on_about)
        menu.exec(QCursor.pos())

    def on_restore(self):
        if not askUser("Reset config to default values?"):
            return
        # TODO deduplicate dict walking
        self.do_reset_to_default_values(self.dialog_dict_with_widgets)

    def do_reset_to_default_values(self, d):
        for key, val in d.copy().items():
            if isinstance(
                val, dict
            ):  # I don't want to iterate over the innermost dict contents like widget, current_value etc.
                subdict = val
                if "is_section" not in subdict:
                    print(f"key {key} has no subdict")
                    continue
                if subdict["is_section"]:
                    self.gui_values__check_and_to_new_conf(subdict["current_value"])
                else:
                    widget = subdict.get("widget")
                    if widget:
                        # print(f"for key {key} widget is {widget}")
                        default = subdict.get("default_value", "FAIL")
                        widget = subdict.get("widget")
                        if default != "FAIL" and widget:
                            self.set_value_for_widget_in_form_layout(
                                widget, key, default, subdict.get("allowed_members")
                            )
                        else:
                            msg = f"couldn't set default value for key '{key}'"
                            print(msg)
                            tooltip(msg)

    def on_import(self):
        showInfo(
            (
                """Not implemented yet ... set misc->"use gui config window instead of built-in dialog" to """
                """false and restart and copy it in the regular config, then change the config again and restar again."""
            )
        )
        # conf = gui_select_json_file_and_return_content(self, "Anki: addon BetterSearch: Select config file to import")
        # self.update_conf_dicts()
        # self.maybe_update_values_shown(conf)
        # TODO validate that keys from imported match existing fields?
        #      OR maybe if not matching: just restart dialog with new values?
        #      what about descriptions and help_texts?

    def on_export(self):
        self.new_conf = self.gui_values__check_and_to_new_conf(self.dialog_dict_with_widgets)
        if not self.new_conf:
            return None
        export_config_to_file(parent=self, addon_name=self.addon_name, conf=self.new_conf)

    def on_about(self):
        showText(self.text_about_in_more)

    def set_value_for_widget_in_form_layout(self, widget, key, val, allowed_members):
        if isinstance(widget, QCheckBox):  # bool
            if val:
                widget.setChecked(val)
        elif isinstance(widget, QSpinBox):  # int
            widget.setValue(val)
        elif isinstance(widget, QDoubleSpinBox):  # float
            widget.setValue(val)
        elif isinstance(widget, QKeySequenceEdit):  # str and "shortcut" in key.lower()
            widget.setKeySequence(val)
        elif isinstance(widget, QLineEdit):  # str
            widget.setText(val)
        elif isinstance(widget, MyListEdit):  # list
            text = json_formatted_as_in_anki_addon_conf(val)
            widget.setPlainText(text)
        elif isinstance(widget, MyDictEdit):  # dict
            text = json_formatted_as_in_anki_addon_conf(val)
            widget.setPlainText(text)
        elif isinstance(widget, QComboBox):
            values_list = allowed_members
            widget.addItems(values_list)
            widget.setCurrentText(val)

    def set_row_in_form_layout(self, form_layout, this_full_key, allowed_members, key, val, has_text_edit, explan_text):
        if isinstance(val, bool):
            right = QCheckBox("")
        elif isinstance(val, int):
            right = QSpinBox()
            right.setMaximum(99999)
        elif isinstance(val, float):
            right = QDoubleSpinBox()
            right.setMaximum(99999)
        elif isinstance(val, str) and "shortcut" in key.lower():
            right = QKeySequenceEdit()
        elif isinstance(val, str):
            right = QLineEdit()
        elif isinstance(val, list):
            right = MyListEdit()
            has_text_edit = True
        elif isinstance(val, dict):
            right = MyDictEdit()
            has_text_edit = True
        if allowed_members:
            # for tup in self.dict_allowed_values.keys():
            #    if tup == this_full_key:
            print(f"!!!!!!!!!for key '{key}' only limited values allowed")
            right = QComboBox()
        self.set_value_for_widget_in_form_layout(right, key, val, allowed_members)

        # without setting these widgets to expanding, the qlabel on top is expanding and
        # has a lot of spacing below and above it in the groupbox.
        # TODO: use a solution that doesn't modify all other widgets ...
        left_widget = QLabel(key)
        if explan_text:
            left_widget.setToolTip(explan_text)
        if isinstance(val, (list, dict)):
            left_widget.setWordWrap(True)

        # left_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        form_layout.addRow(left_widget, right)
        return right, has_text_edit

    def gui_values__check_and_to_new_conf(self, d):
        conf = {}
        for key, val in d.copy().items():
            if isinstance(
                val, dict
            ):  # I don't want to iterate over the innermost dict contents like widget, current_value etc.
                subdict = val
                if "is_section" not in subdict:
                    print(f"key {key} has no subdict")
                    continue
                if subdict["is_section"]:
                    val = self.gui_values__check_and_to_new_conf(subdict["current_value"])
                    if val is None:
                        return
                    else:
                        conf[key] = val
                else:
                    widget = subdict.get("widget")
                    if widget:
                        print(f"for key {key} widget is {widget}")
                        success, current = get_value(widget)
                        if not success:
                            msg = f"Can't save: error in key '{key}': {current}"
                            print(msg)
                            tooltip(msg, period=7000, parent=self)
                            return None
                        else:
                            subdict["current_value"] = current
                            conf[key] = current
        return conf

    def store_values_from_gui(self):
        self.new_conf = self.gui_values__check_and_to_new_conf(self.dialog_dict_with_widgets)
        print(f"self.gui_values__check_and_to_new_conf returned {self.new_conf}")
        if self.new_conf:
            return True

    def reject(self):
        saveGeom(self, self.context)
        QDialog.reject(self)

    def accept(self):
        if self.store_values_from_gui():
            saveGeom(self, self.context)
            QDialog.accept(self)


############# Test
### TestConf
sample_conf = {
    "window_title": "test",
    "text above": "**bla**blub fgsdfgf dsfgfsd gfsdfgf sdfgf sdf",
    "text below": "**blub**blubasd fasdf asdfsad ",
    "text_left_side": "sdkfljasklö dkjlsfd kjlsfkjlk kjas kjlösksa kjlös kjls djkl öjklösa jklöjköl jköl jklösa jklö jklösa öjkla jklöa jklöa jkösa jklösa jklös jklös jklösa jklsa jklöa jklsa jklsa jkl jklö jköl as jklösa jklösa jklösa jklösa jklöa jkölsa jklöa jklsa j jkljkl a jksjkls jklöa jkla jkla jkls jkls jkla jkls jklös jk sasa j kl",
    "about_text": "asdfasdfasdfasdf asdfasdf asdf asdf asdf asdf asfd",
    "context": "test",
    "addon_name": "BetterSearch",
    "default_conf_list": [],
    "nested_dialog_conf_list": [
        [
            "heading",
            "description",
            {
                "a number": 1,
                "a string": "some words",
                "a float": 2.5,
                "a bool": True,
                "a list": [1, "prior line is int", "1", "prior line is string", 3],
                "a dict": {
                    "a": 1,
                    "b": 2,
                },
            },
            """**bold** explanatory text Anki (/ˈɒŋkiː/; Japanese: [aŋki]) is a free and open-source flashcard program. It uses techniques from cognitive science such as active recall testing and spaced repetition to aid the user in memorization.[4][5] The name comes from the Japanese word for "memorization" (暗記)""",
        ],
        [
            "Heading2",
            "another des",
            {
                "some number": 1,
                "some string": "some words",
                "some float": 3.5,
                "some bool": True,
                "Some list": [7, 8, 9],
                "some dict": {
                    "x": 4,
                    "c": 5,
                },
            },
            """The user can design cards that test the information contained in each note. One card may have a question (expression) and an answer (pronunciation, meaning). """,
        ],
    ],
    "schema": {},
}


def helper(cls):
    d = cls(
        parent=aqt.mw,
        window_title=sample_conf["window_title"],
        text_above=sample_conf["text above"],
        text_below=sample_conf["text below"],
        text_left_side=sample_conf["text_left_side"],
        about_text=sample_conf["about_text"],
        context=sample_conf["context"],
        addon_name=sample_conf["addon_name"],
        default_conf_list=sample_conf["default_conf_list"],
        nested_dialog_conf_list=sample_conf["nested_dialog_conf_list"],
        schema=sample_conf["schema"],
    )
    if not d.exec():
        return

    in_list = sample_conf["nested_dialog_conf_list"]
    out_list = d.nested_dialog_conf_list

    pp(in_list == out_list)
    pp(d.nested_dialog_conf_list)


def show_test_config_dialogs_on_startup():
    # helper(ConfDialogWithGroupBoxes)
    # helper(ConfDialogWithTabWidget)
    # helper(ConfDialogWithListAndStackedwidget)
    # helper(ConfDialogWithCollapsibleSection)
    # helper(ConfDialogWithToolbox)
    pass
