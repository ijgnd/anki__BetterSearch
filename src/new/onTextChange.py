import re

from . import in_full_anki_with_gui

if in_full_anki_with_gui:
    from aqt.utils import tooltip
    from .filter_dialog import FilterDialog
    from .overrides import overrides
    from .config import gc
else:
    from .config_substitute import gc

from .dialog__date import get_date_range_string
from .helpers import (
    # this is the order in helpers.py
    cardnames,
    decknames,
    escape_metachars,
    tags,
    is_values,
    is_values_with_explanations,
    props,
    fieldnames,
    details_about_searching_fields_string,
    maybe_add_spaced_between,
)


if not in_full_anki_with_gui:
    class Object:
        pass

    # override some functions:
    def tooltip(text, parent=None, period=3000):
        print(text)

    def overrides():
        lineonly = False
        force_run_search_after = False
        override_add_star = False
        negate = False
        return lineonly, force_run_search_after, override_add_star, negate



def get_filter_dialog_output(
    parent=None,
    parent_is_browser=False,
    values_as_list_or_dict=None,
    windowtitle="",
    adjPos=False,
    show_star=False,
    check_star=False,
    infotext="",
    show_prepend_minus_button=True,
    check_prepend_minus_button=False,
    show_run_search_on_exit=True,
    sort_vals=True,
    multi_selection_enabled=True,
    context="",
    tag_completer=None,
    dict_for_dialog=False,
):
    if in_full_anki_with_gui:
        d = FilterDialog(
            parent=parent,
            parent_is_browser=parent_is_browser,
            values_as_list_or_dict=values_as_list_or_dict,
            windowtitle=windowtitle,
            #max_items=None,
            #prefill="",
            adjPos=adjPos,
            show_star=show_star,
            check_star=check_star,
            infotext=infotext,
            show_prepend_minus_button=show_prepend_minus_button,
            check_prepend_minus_button=check_prepend_minus_button,
            show_run_search_on_exit=show_run_search_on_exit,
            #do_run_search_on_exit=False,
            sort_vals=sort_vals,
            multi_selection_enabled=multi_selection_enabled,
            context=context,
            tag_completer=tag_completer,
        )
        if d.exec():
            d.dict_for_dialog = dict_for_dialog
            return d
        else:
            return None
    else:
        if isinstance(testinput.test_output_key_list, list) and isinstance(
            testinput.test_output_key_list[0], list
        ):  # nested lists only for dnf:/dnc:
            keylist = testinput.test_output_key_list[testinput.counter]
            testinput.counter += 1
        else:
            keylist = testinput.test_output_key_list
        d = Object()
        d.tooltip_after_exit_for_parent = None
        # class testinput is defined in code for testing
        d.just_returned_input_line_content = testinput.test_manual_regular_accept
        d.inputline = testinput.test_manual_just_line
        d.sel_keys_list = keylist
        d.sel_value_from_dict = testinput.test_output_sel_value_from_dict
        d.run_search_on_exit = False
        d.dict_for_dialog = dict_for_dialog
        d.neg = (
            check_prepend_minus_button
            if not testinput.test_manual_override_in_dialog_for_neg
            else not check_prepend_minus_button
        )
        d.addstar = testinput.test_manual_override_in_dialog_for_star
        return d


def filter_dialog_and_overrides(
    parent,
    vals,
    value_for_all,
    windowtitle,
    infotext,
    prefix,
    sort_vals,
    show_star,
    check_prepend_minus_button,
    context,
):
    d = get_filter_dialog_output(
        parent=parent,
        parent_is_browser=True,
        values_as_list_or_dict=vals,
        windowtitle=windowtitle,
        adjPos=False,
        show_star=show_star,
        check_star=False,
        infotext=infotext,
        show_prepend_minus_button=True,
        check_prepend_minus_button=check_prepend_minus_button,
        sort_vals=sort_vals,
        context=context,
    )
    if not d:
        return None, None, None, None
    else:
        if d.sel_keys_list == value_for_all:
            return d.sel_keys_list, "", False, d.run_search_on_exit
        lineonly, force_run_search_after, override_add_star, negate = overrides()
        if d.just_returned_input_line_content:
            lineonly = True
        if override_add_star:
            d.addstar ^= True
        if d.sel_value_from_dict:
            out = d.sel_value_from_dict
        else:
            out = " ".join(d.sel_keys_list)
        if lineonly or d.addstar:
            out += "*"
        out = prefix + out
        print(f"filter_dialog_and_overrides: out is --{out}--, type ist: --{type(out)}--")
        neg = True if (negate or d.neg) else False
        run_search_on_exit = True if force_run_search_after else d.run_search_on_exit
        return d.sel_keys_list, out, neg, run_search_on_exit


def note_filter_helper(parent, col, remaining_sentence, prefixed_with_minus):
    infotext = f"""
<span>
In a first step select the note type to search. After this you'll see a dialog to narrow
by {remaining_sentence}
</span>
"""
    note_type_list, fmt, neg, run_search = filter_dialog_and_overrides(
        parent=parent,
        vals=["--All Note Types--"] + col.models.allNames(),
        value_for_all="--All Note Types--",
        windowtitle="Anki: Step 1: Select Note Type to search",
        infotext=infotext,
        prefix="note:",
        sort_vals=True,
        show_star=False,
        check_prepend_minus_button=prefixed_with_minus,
        context="note",
    )
    note_type = note_type_list[0] if note_type_list else note_type_list
    return note_type, fmt, neg, run_search


def note__card(parent, col, prefixed_with_minus):
    remaining = "only if the note has multiple cards/card templates."
    # e.g. model = "Basic"; model_search_string = "note:Basic"; modelneg = False
    model, model_search_string, modelneg, run_search = note_filter_helper(parent, col, remaining, prefixed_with_minus)
    if not model:
        return None, None, None, None

    infotext = """
<span>
After having selected the note types to search now select the
card template/type/name you want to search.
</span>
"""
    iscloze = False
    show_card_dialog = True
    if not model_search_string:
        # then from all notetypes
        vals = cardnames(col)
        sort_vals = True
    else:
        # for one note type
        sort_vals = False
        nt = col.models.byName(model)
        if nt["type"] == 1:  # it's a cloze and for cloze it doesn't make sense to show a list
            # of cards
            show_card_dialog = False
            iscloze = True
        else:
            card_name_to_fmt_dict = {}
            for c, tmpl in enumerate(nt["tmpls"]):
                # T: name is a card type name. n it's order in the list of card type.
                name = tmpl["name"]
                n = str(c + 1)
                fmt = f"{n.zfill(2)}: {name}"
                card_name_to_fmt_dict[fmt] = name
            default_fake_dict = {"--All the Card Types--": "--All the Card Types--"}
            vals = {**default_fake_dict, **card_name_to_fmt_dict}
            vals_are_dict = True
            if c == 0:  # only one card type
                show_card_dialog = False
    if not show_card_dialog:
        card_search_string = ""
        cardneg = False
    else:
        # e.g. card = "Card 6"; card_search_string = "card:Card 6"; cardneg = False
        card_list, card_search_string, cardneg, run_search = filter_dialog_and_overrides(
            parent=parent,
            vals=vals,
            value_for_all="--All the Card Types--",
            windowtitle="Anki: Step 2: Select Card Type to search",
            infotext=infotext,
            prefix="card:",
            sort_vals=sort_vals,
            show_star=False,
            check_prepend_minus_button=modelneg,
            context="card",
        )
        if not card_list:
            return None, None, None, None
        card = card_list[0]

    # quote if needed
    if " " in model_search_string:
        model_search_string = f'"{model_search_string}"'
    if " " in card_search_string:
        card_search_string = f'"{card_search_string}"'

    maybe_space = " " if model_search_string and card_search_string else ""
    out = model_search_string + maybe_space + card_search_string

    if iscloze:
        msg = """
You selected a cloze note type. To match only c2 clozes type you would have to
add&nbsp;&nbsp;card:2&nbsp;&nbsp;
"""
        tooltip(msg, parent=parent)  # default is period=3000
    # parent.button_helper(out, False)
    return out, 0, cardneg, run_search


def note__field(parent, col, prefixed_with_minus):
    remaining = "field (if the note has more than one field)."
    model, model_search_string, modelneg, run_search = note_filter_helper(parent, col, remaining, prefixed_with_minus)
    if not model:
        return None, None, None, None

    infotext = """
<span>
After having selected the note type to search now select the field name you want
to search. After closing this dialog the text inserted will be "fieldname:**"
which doesn't limit your search yet. You must <b>adjust</b> this search and
add some text to limit to a certain term.
<span>
"""
    show_card_dialog = True
    if not model_search_string:
        # then from all notetypes
        fnames = fieldnames(col)
        value_for_all = False
    else:
        # for one note type
        nt = parent.col.models.byName(model)
        fnames = [fld["name"] for fld in nt["flds"]]
        if not len(fnames) > 1:
            show_card_dialog = False
        value_for_all = "--All the Card Types--"
        fnames.insert(0, value_for_all)
    if not show_card_dialog:
        field_search_string = ""
        fieldneg = False
    else:
        field_list, field_search_string, fieldneg, run_search = filter_dialog_and_overrides(
            parent=parent,
            vals=fnames,
            value_for_all=value_for_all,
            windowtitle="Anki: Step 2: Select Field Name to search",
            infotext=infotext,
            prefix="",
            sort_vals=False,
            show_star=False,
            check_prepend_minus_button=modelneg,
            context="field",
        )
        if not field_list:
            return None, None, None, None
        field = field_list[0]

    posback = 0
    field_search_string = escape_metachars(field_search_string)
    if field_search_string:
        field_search_string += ":**"
        posback = -2
    # quote if needed
    model_search_string = escape_metachars(model_search_string)
    if " " in model_search_string:
        model_search_string = '"' + model_search_string + '"'
    # always quote field search string so that user can type in spaces
    field_search_string = '"' + field_search_string + '"'

    maybe_space = " " if model_search_string and field_search_string else ""
    out = model_search_string + maybe_space + field_search_string

    return out, posback, fieldneg, run_search


def note__field__card__helper(parent, col, term, before, after, chars_to_del, prefixed_with_minus):
    """
    this function and the functions it's calling are from early 2020. They deserve
    to be simplified and shortened and maybe merged back into the general code below.
    But they seem to work so I'm not touching them.
    """
    if term == "dnf:":
        out, tomove, prefixed_with_minus, run_search = note__field(parent, col, prefixed_with_minus)
    else:  # "dnc:"
        out, tomove, prefixed_with_minus, run_search = note__card(parent, col, prefixed_with_minus)
    if out:
        spaces = maybe_add_spaced_between(before, chars_to_del)
        if prefixed_with_minus:
            out = f"-({out})"
            tomove -= 1  # I'm adding a ) so I must move the cursor one to the left
        if chars_to_del == len(before):  # whole before will be deleted -> no leading space required
            spaces = ""
        new_text = before[:-chars_to_del] + spaces + out + after
        newpos = len(before[:-chars_to_del] + spaces + out) + tomove
        # triggering a search makes no sense here:
        #  for dnf: the user needs to type in the searchstring for the field
        #  for dnc: the user would usually add additional search terms such as is:
        print(f"note__field__card__helper: new_text is ||{new_text}||")
        return new_text, newpos, run_search
    else:
        return None, None, run_search


def get_date_range(parent, col, search_operator, before, after, chars_to_del, prefixed_with_minus):
    if in_full_anki_with_gui:
        test_lower = test_upper = test_custom_datetime = None
    else:
        # class testinput is defined in testing code
        test_lower = testinput.test_date_lower
        test_upper = testinput.test_date_upper
        test_custom_datetime = testinput.test_custom_datetime

    success, searchtext, TriggerSearchAfter = get_date_range_string(
        parent, col, search_operator, prefixed_with_minus, test_lower, test_upper, test_custom_datetime
    )
    if not success:
        return None, None, None
    else:
        _, force_run_search_after, _, _ = overrides()
        if force_run_search_after:
            TriggerSearchAfter = True
        spaces = maybe_add_spaced_between(before, chars_to_del)
        remove_these = chars_to_del + 1 if prefixed_with_minus else chars_to_del
        new_text = before[:-remove_these] + spaces + searchtext + after
        if chars_to_del == len(before):  # whole before will be deleted -> no leading space required
            spaces = ""
        newpos = len(before[:-chars_to_del] + spaces + searchtext)
        return new_text, newpos, TriggerSearchAfter


def matches_search_operator(before, term):
    if before in [term, f"-{term}"]:
        return True
    # in my multiline dialog users can type RETURN or TAB
    if before[-(len(term) + 1) :] in [f" {term}", f"\n{term}", f"\t{term}"]:
        return True
    # handle -
    if before[-(len(term) + 2) :] in [f" -{term}", f"\n-{term}", f"\t-{term}"]:
        return True


def minus_precedes_search_operator(before, term):
    if before == f"-{term}":
        return True
    if before[-(len(term) + 2) :] in [f" -{term}", f"\n-{term}", f"\t-{term}"]:
        return True


def regex_replacements(before, after):
    # This offers similar functionality to
    #     - my addon "browser search aliases/abbreviations", https://ankiweb.net/shared/info/546509374
    #       difference: the search aliases replaces only when you execute the search
    #       I'm not sure if this is worse, e.g. maybe I don't know that the orange flag has the number two.
    #       Direct replacements after each character typed means I'll never have an understandable term like "florange"
    #       in a longer search term that I might want to check ...
    #     - Symbols as you type, https://ankiweb.net/shared/info/2040501954
    #       difference: "Symbols as you type" does not offer a regex replacement in 2024-02
    #       Both addons can be used at the same time.

    if gc(["regex replacements while typing", "matching with normal strings: active"]) and not after:
        alias_dict = gc(["regex replacements while typing", "matching with normal strings: dictionary"])
        if alias_dict and isinstance(alias_dict, dict):
            """
            the following doesn't make sense here because I replace after each char typed
            so I can never get to longer strings (as in my separate alias addon)
            # sort dict by length of keys, so that "added:1" is replaced before "added:"
            # in python 3.7 keeps insertion order
            # for original in sorted(alias_dict, key=len, reverse=True):
            for abbrev in sorted(alias_dict, key=lambda k: len(alias_dict[k]), reverse=True):
                repl = alias_dict[abbrev]
                if ...
            """
            for abbrev, repl in alias_dict.items():
                if before == abbrev or before.endswith(f" {abbrev}"):
                    before = before.replace(abbrev, repl)
                    new_text = before + after
                    newpos = len(before + after)
                    return new_text, newpos, False  # False here means: do not trigger search

    """
    e.g.:

        --aliases_regex dictionary": {
            "aa(\\d{1,4})(?= |$)" : "added:\\1",
            "ee(\\d{1,4})(?= |$)" : "edited:\\1",
            "ii(\\d{1,4})(?= |$)" : "introduced:\\1",
            "rr(\\d{1,4})(?= |$|:)" : "rated:\\1",
            "nid(\\d{13})(?= |$)" : "nid:\\1",
            "cid(\\d{13})(?= |$)" : "cid:\\1",
            "due(\\!?=?>?<?-?)(?=\\d{1,4})" : "prop:due\\1",
            "laps(\\!?=?>?<?-?)(?=\\d{1,4})" : "prop:lapses\\1",
            "lapses(\\!?=?>?<?-?)(?=\\d{1,4})" : "prop:lapses\\1",
            "ease(\\!?=?>?<?-?)(?=\\d{1,4})" : "prop:ease\\1",
            "ivl(\\!?=?>?<?-?)(?=\\d{1,4})" : "prop:ivl\\1",
            "isdue(?= |$)": "is:due",
            "isnew(?= |$)": "is:new",
            "islearn(?= |$)" : "is:learn",
            "isreview(?= |$)" : "is:review",
            "issuspended(?= |$)" : "is:suspended",
            "issuspend(?= |$)" : "is:suspended",
            "isburied(?= |$)" : "is:buried",
            "isbury(?= |$)" : "is:buried",
            "flag(\\d{1,2})(?= |$)": "flag:\\1",
            "flred(?= |$)" : "flag:1",
            "florange(?= |$)" : "flag:2",
            "flgreen(?= |$)" : "flag:3",
            "flblue(?= |$)" : "flag:4",
            "flpink(?= |$)" : "flag:5",
            "flturquoise(?= |$)" : "flag:6",
            "fltur(?= |$)" : "flag:6",
            "flpurple(?= |$)" : "flag7",
            "flpurp(?= |$)" : "flag7",
            "flpur(?= |$)" : "flag7",
            "flpu(?= |$)" : "flag7",
            "flp(?= |$)" : "flag7",
            "retag:": "tag:re:"
        },
    """
    if gc(["regex replacements while typing", "matching with regular expressions strings: active"]) and not after:
        regex_alias_dict = gc(
            ["regex replacements while typing", "matching with regular expressions strings: dictionary"]
        )
        if regex_alias_dict and isinstance(regex_alias_dict, dict):
            for abbrev, repl in regex_alias_dict.items():
                before, number_replacements = re.subn(abbrev, repl, before)
                if number_replacements:
                    new_text = before + after
                    newpos = len(before + after)
                    return new_text, newpos, False


def onSearchEditTextChange(
    parent, move_dialog_in_browser, include_filtered_in_deck, input_text, cursorpos, from_button=False, test_input=False
):
    # parent: Browser, filtered_deck.FilteredDeckConfigDialog
    global testinput
    testinput = test_input

    col = parent.col
    TriggerSearchAfter = False

    if cursorpos is None:
        before = input_text
        after = ""
    else:
        before = input_text[:cursorpos]
        after = input_text[cursorpos:]

    did_regex_replacements = regex_replacements(before, after)
    if did_regex_replacements:
        # new_text, newpos, do_not_trigger_search
        return did_regex_replacements[0], did_regex_replacements[1], TriggerSearchAfter

    if after and not after.startswith(" "):
        after = " " + after

    vals = {}

    for abbrev in ["dnf:", "dnc:"]:
        if before[-4:] == abbrev:
            prefixed_with_minus = True if minus_precedes_search_operator(before, abbrev) else False
            char_to_del = len(abbrev) + 1 if minus_precedes_search_operator else len(abbrev)
            # new_text, newpos, run_search
            return note__field__card__helper(parent, col, abbrev, before, after, char_to_del, prefixed_with_minus)

    for dialog_abbrev, anki_search_operator in {
        gc(
            ["custom search operators for custom filter dialogs", "date range dialog for added: string"]
        ): "added",  # dadded:
        gc(
            ["custom search operators for custom filter dialogs", "date range dialog for edited: string"]
        ): "edited",  # dedited:
        gc(
            ["custom search operators for custom filter dialogs", "date range dialog for rated: string"]
        ): "rated",  # drated:
        gc(
            ["custom search operators for custom filter dialogs", "date range dialog for introduced: string"]
        ): "introduced",  # dintroduced:
        gc(
            ["custom search operators for custom filter dialogs", "date range dialog for resched: string"]
        ): "resched",  # dresched, resched: introduced for 2.1.41
    }.items():
        if dialog_abbrev and matches_search_operator(before, dialog_abbrev):
            length = len(dialog_abbrev)
            prefixed_with_minus = True if minus_precedes_search_operator(before, dialog_abbrev) else False
            return get_date_range(parent, col, anki_search_operator, before, after, length, prefixed_with_minus)

    do_tag_deck_search = False
    for tag_deck_term in [
        gc(["custom search operators for custom filter dialogs", "custom tag&deck string 1"], ""),
        gc(["custom search operators for custom filter dialogs", "custom tag&deck string 2"], ""),
    ]:
        if tag_deck_term and tag_deck_term == before[-len(tag_deck_term) :]:
            do_tag_deck_search = tag_deck_term
            prefixed_with_minus = True if minus_precedes_search_operator(before, tag_deck_term) else False
            remove_from_end = len(tag_deck_term) + 1 if prefixed_with_minus else len(tag_deck_term)
            break
    if do_tag_deck_search:
        """
        vals = {
            "remove_from_end_of_before": number of characters to delete from the text before inserting
                                    the selection. E.g. if the user had typed in "xx" and then
                                    "tag:hallo" will be inserted the "xx" part must be removed
                                    beforehand
                                    if nothing to remove you must set it to "0".
            "dict_for_dialog": if True use a string that describes it: I use this string for
                            an if-loop after the dialog closes.
            "values_for_filter_dialog": tags(col, True) + decknames(col, include_filtered_in_deck, True),
            "surround_with_quotes": ,
            "infotext": text that is shown over the filterbar
            "windowtitle":
            "show_prepend_minus_button": whether the checkbox left from the ok button is SHOWN
            "check_prepend_minus_button": whether the checkbox left from the ok button is CHECKED
            "show_star": whether the checkbox left from the ok button is SHOWN
            "check_star": whether the checkbox left from the ok button is CHECKED
            "sort_vals": whether vals are sorted alphabetically in the filter dialog
            "context": needed for remembering window size etc.
            "operator": used to add operator after filter dialog was closed to re-add it to the terms
        }
        """

        vals = {
            "remove_from_end_of_before": int(f"-{remove_from_end}"),
            "dict_for_dialog": False,
            "values_for_filter_dialog": tags(col, True) + decknames(col, include_filtered_in_deck, True),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select from decks and tags",
            "show_prepend_minus_button": True,
            "check_prepend_minus_button": prefixed_with_minus,
            "show_star": False,  # deck: and tag: also match subdecks, * only needed for exclusion: -deck:xyz::*
            "check_star": False,
            "sort_vals": True,
            "multi_selection_enabled": True,
            "context": "tag_and_deck_xx",
            "operator": "",
        }


    do_saved_search = gc(["custom search operators for custom filter dialogs", "saved searches"], False)
    if do_saved_search and do_saved_search == before[-len(do_saved_search) :]:
        prefixed_with_minus = True if minus_precedes_search_operator(before, do_saved_search) else False
        remove_from_end = len(do_saved_search) + 1 if prefixed_with_minus else len(do_saved_search)

        def saved_searches_dict():
            d = {}
            for key, val in col.get_config("savedFilters", {}).items():
                d[f"{key} ['''{val}''']"] = val
            print(d)
            return d

        vals = {
            "remove_from_end_of_before": int(f"-{remove_from_end}"),
            "dict_for_dialog": "saved_searches",
            "values_for_filter_dialog": saved_searches_dict(),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select saved search",
            "show_prepend_minus_button": False,
            "check_prepend_minus_button": prefixed_with_minus,
            "show_star": False,  # deck: and tag: also match subdecks, * only needed for exclusion: -deck:xyz::*
            "check_star": False,
            "sort_vals": True,
            "multi_selection_enabled": False,
            "context": "saved_search",
            "operator": "",
        }


    if matches_search_operator(before, "field:") and (
        gc(["open filter dialog after typing these search operators", "modify_field"]) or from_button
    ):
        field_infotext = """
<div><b>This dialog inserts the field name to search. After closing the dialog you <br>
should enter the actual search term for the field</b>. By default this add-on adds "**"
which doesn't limit your search. You must put your search term between the "**".</div>
"""
        prefixed_with_minus = True if minus_precedes_search_operator(before, "field:") else False
        vals = {
            "remove_from_end_of_before": -7 if prefixed_with_minus else -6,
            "dict_for_dialog": False,
            "values_for_filter_dialog": fieldnames(col),
            "surround_with_quotes": True,
            "infotext": field_infotext + details_about_searching_fields_string,
            "windowtitle": "Anki: Select field to search",
            "show_prepend_minus_button": True,
            "check_prepend_minus_button": prefixed_with_minus,
            "show_star": True,
            "check_star": False,
            "sort_vals": True,
            "multi_selection_enabled": True,
            "context": "field",
            "operator": "field:",
        }

    if matches_search_operator(before, "prop:") and (
        gc(["open filter dialog after typing these search operators", "modify_props"]) or from_button
    ):
        it = "<b>After closing the dialog you must adjust what's inserted with your numbers</b>"
        prefixed_with_minus = True if minus_precedes_search_operator(before, "prop:") else False
        vals = {
            "remove_from_end_of_before": -6 if prefixed_with_minus else -5,
            "dict_for_dialog": "prop",
            "values_for_filter_dialog": props(),
            "surround_with_quotes": False,
            "infotext": it,
            "windowtitle": "Anki: Select properties to search",
            "show_prepend_minus_button": True,
            "check_prepend_minus_button": prefixed_with_minus,
            "show_star": False,
            "check_star": False,
            "sort_vals": False,
            "context": "prop",
            "operator": "prop:",
        }

    if matches_search_operator(before, "is:") and (
        gc(["open filter dialog after typing these search operators", "modify_is"]) or from_button
    ):
        expl = gc(["open filter dialog after typing these search operators", "modify_is__show_explanations"])
        prefixed_with_minus = True if minus_precedes_search_operator(before, "is:") else False
        vals = {
            "remove_from_end_of_before": -4 if prefixed_with_minus else -3,
            "dict_for_dialog": "is_with_explanations" if expl else False,
            "values_for_filter_dialog": is_values_with_explanations() if expl else is_values(),
            "surround_with_quotes": False,
            "infotext": False,
            "windowtitle": "Anki: Search by Card State",
            "show_prepend_minus_button": True,
            "check_prepend_minus_button": prefixed_with_minus,
            "show_star": False,
            "check_star": False,
            "sort_vals": True,
            "context": "is",
            "operator": "is:",
        }

    if matches_search_operator(before, "flag:") and (
        gc(["open filter dialog after typing these search operators", "modify_flag"]) or from_button
    ):
        prefixed_with_minus = True if minus_precedes_search_operator(before, "flag:") else False
        vals = {
            "remove_from_end_of_before": -6 if prefixed_with_minus else -5,
            "dict_for_dialog": "flags",
            "values_for_filter_dialog": {
                "no flags": "flag:0",
                "any flags": "-flag:0",
                "red": "flag:1",
                "orange": "flag:2",
                "green": "flag:3",
                "blue": "flag:4",
                "pink": "flag:5",
                "turquoise": "flag:6",
                "purple": "flag:7",
            },
            "surround_with_quotes": False,
            "infotext": False,
            "windowtitle": "Anki: Search by Flag",
            "show_prepend_minus_button": True,
            "check_prepend_minus_button": prefixed_with_minus,
            "show_star": False,
            "check_star": False,
            "sort_vals": True,
            "multi_selection_enabled": True,
            "context": "flag",
            "operator": "",
        }

    tag_search = matches_search_operator(before, "tag:") and (
        gc(["open filter dialog after typing these search operators", "modify_tag"]) or from_button
    )
    if tag_search:
        prefixed_with_minus = True if minus_precedes_search_operator(before, "tag:") else False

        def _tag_completer(search_string):
            matches = list(col._backend.complete_tag(input=search_string, match_limit=750))
            matches.append("none")
            return matches

        vals = {
            "remove_from_end_of_before": -5 if prefixed_with_minus else -4,
            "dict_for_dialog": False,
            "values_for_filter_dialog": _tag_completer(""),
            "surround_with_quotes": False,
            "infotext": False,
            "windowtitle": "Anki: Select tag to search",
            "show_prepend_minus_button": True,
            "check_prepend_minus_button": prefixed_with_minus,
            "show_star": False,  # since at least 2.1.50 searching for tag:aa also matches tag:aa:bb etc.
            "check_star": False,
            "sort_vals": False,
            "tag_completer": _tag_completer,
            "multi_selection_enabled": True,
            "context": "tag",
            "operator": "tag:",
        }

    elif matches_search_operator(before, "note:") and (
        gc(["open filter dialog after typing these search operators", "modify_note"]) or from_button
    ):
        prefixed_with_minus = True if minus_precedes_search_operator(before, "note:") else False
        vals = {
            "remove_from_end_of_before": -6 if prefixed_with_minus else -5,
            "dict_for_dialog": False,
            "values_for_filter_dialog": col.models.allNames(),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select Note Type to search",
            "show_prepend_minus_button": True,
            "check_prepend_minus_button": prefixed_with_minus,
            "show_star": False,
            "check_star": False,
            "sort_vals": True,
            "multi_selection_enabled": True,
            "context": "note",
            "operator": "note:",
        }

    elif matches_search_operator(before, "card:") and (
        gc(["open filter dialog after typing these search operators", "modify_card"]) or from_button
    ):
        prefixed_with_minus = True if minus_precedes_search_operator(before, "card:") else False
        vals = {
            "remove_from_end_of_before": -6 if prefixed_with_minus else -5,
            "dict_for_dialog": False,
            "values_for_filter_dialog": cardnames(col),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select Card (Type) Name to search",
            "show_prepend_minus_button": True,
            "check_prepend_minus_button": prefixed_with_minus,
            "show_star": False,
            "check_star": False,
            "sort_vals": True,
            "multi_selection_enabled": True,
            "context": "card",
            "operator": "card:",
        }

    elif matches_search_operator(before, "cfn:"):  # cards from note

        def cardnames_modelname_dict():
            d = {}
            for m in col.models.all():
                modelname = m["name"]
                for t in m["tmpls"]:
                    d[t["name"] + " (" + modelname + ")"] = (t["name"], modelname)
            return d

        prefixed_with_minus = True if minus_precedes_search_operator(before, "cfn:") else False
        vals = {
            "remove_from_end_of_before": -5 if prefixed_with_minus else -4,
            "dict_for_dialog": "cfn",
            "values_for_filter_dialog": cardnames_modelname_dict(),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select Card (Type) Name from selected Note Type",
            # doesn't really make sense, so I also remove a preceeding - ???
            "show_prepend_minus_button": False,
            "check_prepend_minus_button": prefixed_with_minus,
            "show_star": False,
            "check_star": False,
            "sort_vals": True,
            "context": "card_from_note_cfn",
            "operator": "",
        }

    elif matches_search_operator(before, "ffn:"):
        ffn_infotext = (
            "<b>"
            "Besides the note type name this dialog only inserts the field name to search. After closing "
            "the dialog you must enter the actual search term for the field between '**'.<br>"
            "</b>"
        )

        def fieldnames_modelname_dict():
            d = {}
            for m in col.models.all():
                modelname = m["name"]
                for f in m["flds"]:
                    d[f["name"] + " (" + modelname + ")"] = (f["name"], modelname)
            return d

        prefixed_with_minus = True if minus_precedes_search_operator(before, "ffn:") else False
        vals = {
            "remove_from_end_of_before": -5 if prefixed_with_minus else -4,
            "dict_for_dialog": "ffn",
            "values_for_filter_dialog": fieldnames_modelname_dict(),
            "surround_with_quotes": True,
            "infotext": ffn_infotext + details_about_searching_fields_string,
            "windowtitle": "Anki: Select Field to search from selected Note Type",
            "show_prepend_minus_button": False,
            "check_prepend_minus_button": prefixed_with_minus,
            "show_star": False,
            "check_star": False,
            "sort_vals": True,
            "context": "field_from_note_ffn",
            "operator": "",
        }

    elif matches_search_operator(before, "deck:") and gc(
        ["open filter dialog after typing these search operators", "modify_deck"]
    ):
        prefixed_with_minus = True if minus_precedes_search_operator(before, "deck:") else False
        vals = {
            "remove_from_end_of_before": -6 if prefixed_with_minus else -5,
            "dict_for_dialog": False,
            "values_for_filter_dialog": decknames(col, include_filtered_in_deck),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select Deck to search",
            "show_prepend_minus_button": True,
            "check_prepend_minus_button": prefixed_with_minus,
            "show_star": False,  # deck also match subdecks, * only needed for exclusion: -deck:xyz::*
            "check_star": False,
            "sort_vals": True,
            "multi_selection_enabled": True,
            "context": "deck",
            "operator": "deck:",
        }

    if not vals:
        return None, None, None

    d = get_filter_dialog_output(
        parent=parent,
        parent_is_browser=move_dialog_in_browser,
        values_as_list_or_dict=vals["values_for_filter_dialog"],
        windowtitle=vals["windowtitle"],
        adjPos=True if gc(["filter dialog", "autoadjust FilterDialog position"]) else False,
        show_star=vals["show_star"],
        check_star=vals["check_star"],
        infotext=vals["infotext"],
        show_prepend_minus_button=vals["show_prepend_minus_button"],
        check_prepend_minus_button=vals["check_prepend_minus_button"],
        sort_vals=vals["sort_vals"],
        multi_selection_enabled=vals.get("multi_selection_enabled"),
        context=vals.get("context"),
        tag_completer=vals.get("tag_completer"),
        dict_for_dialog=vals["dict_for_dialog"]
    )
    if not d:
        return None, None, None
    else:
        if d.tooltip_after_exit_for_parent:
            tooltip(d.tooltip_after_exit_for_parent, period=6000)

        just_returned_input_line_content, force_run_search_after, override_add_star, negate = overrides()
        if d.just_returned_input_line_content:
            just_returned_input_line_content = True
        TriggerSearchAfter = d.run_search_on_exit
        if force_run_search_after:
            TriggerSearchAfter = True
        # print(f"d.sel_keys_list is {d.sel_keys_list}")
        # print(f"d.inputline is {d.inputline}")
        # print(f"d.sel_value_from_dict is {d.sel_value_from_dict}")
        # print(f"d.dict_for_dialog is {d.dict_for_dialog}")
        # print(f"just_returned_input_line_content is {just_returned_input_line_content}")

        is_exclusion = any([d.neg, negate])
        # print(f"is_exclusion is --{is_exclusion}")

        # I always remove the search term operator fully, re-add it later
        if vals["remove_from_end_of_before"] != 0:
            befmod = before[: vals["remove_from_end_of_before"]]
        else:  # equal to   vals["remove_from_end_of_before"] == 0    or    not vals["remove_from_end_of_before"]
            befmod = before
        # print(f"before is --{before}--")
        # print(f"YYbefmod is --{befmod}--")

        ############ return for some special dialogs:
        if d.dict_for_dialog == "cfn":
            mycard = d.sel_value_from_dict[0]
            mynote = d.sel_value_from_dict[1]
            if is_exclusion:  # doesn't really make sense here
                mysearch = f'''-("card:{escape_metachars(mycard)}" "note:{escape_metachars(mynote)}")'''
            else:
                mysearch = f'''"card:{escape_metachars(mycard)}" "note:{escape_metachars(mynote)}"'''
            new_text = befmod + mysearch + after
            new_pos = len(befmod + mysearch)
            return new_text, new_pos, TriggerSearchAfter
        elif d.dict_for_dialog == "ffn":
            field = d.sel_value_from_dict[0]
            mynote = d.sel_value_from_dict[1]
            if is_exclusion: # - doesn't really make sense here
                mysearch = f'''-("note:{escape_metachars(mynote)}" "{escape_metachars(field)}:**")'''
            else:
                mysearch = f'''"note:{escape_metachars(mynote)}" "{escape_metachars(field)}:**"'''
            new_text = befmod + mysearch + after
            cursor_adj = 3 if is_exclusion else 2
            new_pos = len(befmod + mysearch) - cursor_adj  # -2/-3 I need to go back 2/3 for *"
            return (
                new_text,
                new_pos,
                False,
            )  # triggering a search makes no sense here: the user needs to fill in the search term for the field
        elif d.dict_for_dialog == "is_with_explanations":
            new_text = befmod + ("-" if is_exclusion else "") + d.sel_value_from_dict + after
            new_pos = len(befmod + ("-" if is_exclusion else "") + d.sel_value_from_dict)
            return (
                new_text,
                new_pos,
                False,
            )  # triggering a search makes no sense here: the user needs to fill in the search term for is:
        elif d.dict_for_dialog == "prop":
            new_text = befmod + ("-" if is_exclusion else "") + d.sel_value_from_dict + after
            new_pos = len(befmod + ("-" if is_exclusion else "") + d.sel_value_from_dict)
            return (
                new_text,
                new_pos,
                False,
            )  # triggering a search makes no sense here: the user needs to fill in the search term for prop:
        elif d.dict_for_dialog == "saved_searches":
            new_text = befmod + ("-" if is_exclusion else "") + d.sel_value_from_dict + after
            new_pos = len(befmod + ("-" if is_exclusion else "") + d.sel_value_from_dict)
            return (
                new_text,
                new_pos,
                TriggerSearchAfter,
            )

        ############ generate sel_list
        if d.dict_for_dialog == "flags":
            sel_list = [str(d.sel_value_from_dict)]

        if just_returned_input_line_content:
            # if do_tag_deck_search: maybe add tag or deck??? BUT if the user wanted this then they wouldn't have chosen only_input_line ...
            sel_list = [d.inputline]

        # if list is returned, escape some characters and store if the terms need quoting
        # d.dict_for_dialog: UseFilterDialogValue: if values tuple with info - list as input -> False
        if not d.dict_for_dialog:
             #print(f"d.sel_keys_list is --{d.sel_keys_list}")
            sel_list = [escape_metachars(e) for e in d.sel_keys_list]
            # print(f"sel_list is --{sel_list}--")
            chars_that_needs_quoting = ["(", ")"]
            if tag_search:
                for c in chars_that_needs_quoting:
                    for element in sel_list:
                        if c in element:
                            vals["surround_with_quotes"] = True
                            break

        # print(f"sel_list is --{sel_list}--")
        ############ maybe add '*' to match other deeper nested hierarchical tags, also handle tag/deck multiple matches
        for idx, member in enumerate(sel_list):
            if member in ["none", "filtered", "tag:none", "deck:filtered", "re:"]:
                pass
            elif vals["operator"] == "tag:":
                # no star at the end needed:
                #   since at least 2.1.50 (and in 2024-03):
                #   e.g. you have tags ab ab::yz
                #   "tag:ab" will also match ab::yz
                #   the star is only needed to match partial tags e.g. tag:a*
                #   -> my dialog always matches full tags so I never need the star
                #   to match a tag without subtags you'd type:  tag:ab -tag:ab::*
                pass
            # since 2.1.24 card: and note: can also use *
            elif vals["operator"] == "card:":
                if d.addstar and not override_add_star:
                    member = member + "*"
            elif vals["operator"] == "note:":
                if d.addstar and not override_add_star:
                    member = member + "*"
            elif vals["operator"] == "deck:" and gc(
                ["open filter dialog after typing these search operators", "modify_deck"]
            ):
                if d.addstar and not override_add_star:
                    member = member + "*"
            elif vals["operator"] == "field:":
                member = member + "**"
            # ugly fix for xx etc.
            elif do_tag_deck_search:
                if d.addstar and not override_add_star:
                    member = member + "*"
            sel_list[idx] = member

        ############ surround terms with quotes
        # print(f'vals["surround_with_quotes"] is --{vals["surround_with_quotes"]}--')
        # print(f"sel_list is --{sel_list}--")
        if vals["surround_with_quotes"]:
            new_list = []
            for e in sel_list:
                # tag:\*a\_\(a   gets rewritten to   "tag:\*a\_(a"
                needs_quoting = any([c in e for c in chars_that_needs_quoting if not f"\\{c}" in e])
                needs_quoting = True if (" " in e) else needs_quoting  # "\ " doesn't work, space needs quoting in decknames
                new = '"' + e + '"' if needs_quoting else e
                new_list.append(new)
            sel_list = new_list

        # print('dddddddddddddddd')
        # print(sel_list)
        # print(type((sel_list)))
        ############ merge and exclusion

        merged = "(" if (not is_exclusion and len(sel_list) > 1) else ""
        maybe_minus = "-" if is_exclusion else ""
        connector = " " if is_exclusion else " OR "
        for e in sel_list:
            if vals["operator"] == "field:":
                merged += f'{maybe_minus}{e}{connector}'
            else:
                merged += f'{maybe_minus}{vals["operator"]}{e}{connector}'
        if not is_exclusion:
            merged = merged[:-4]   # remove final ' OR '
            if len(sel_list) > 1:
                merged += ")"

        merged = merged.rstrip()  # strip trailing spaces

        # quick workaround for "
        merged = merged.replace('deck:"', '"deck:')
        merged = merged.replace('note:"', '"note:')
        merged = merged.replace('tag:"', '"tag:')
        merged = merged.replace('card:"', '"card:')

        # print('zzzzzzzzzzzzzzzzzzz')
        # print(befmod)
        # print(merged)
        # print(after)
        new_text = befmod + merged + after
        newpos = len(befmod + merged)
        if vals["operator"] == "field:":
            if merged.endswith('")'):
                move_left = 3
            elif merged.endswith((")", '"')):
                move_left = 2
            else:
                move_left = 1
            newpos -= move_left  # move cursor between **
        return new_text, newpos, TriggerSearchAfter
