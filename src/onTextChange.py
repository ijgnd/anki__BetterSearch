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
    emc,
    tags,
    is_values,
    is_values_with_explanations,
    props,
    fieldnames,
    details_about_searching_fields,
    maybe_add_spaced_between,
)


class Object:
    pass


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
):
    if in_full_anki_with_gui:
        d = FilterDialog(
            parent=parent,
            parent_is_browser=parent_is_browser,
            values_as_list_or_dict=values_as_list_or_dict,
            windowtitle=windowtitle,
            adjPos=adjPos,
            show_star=show_star,
            check_star=check_star,
            infotext=infotext,
            show_prepend_minus_button=show_prepend_minus_button,
            check_prepend_minus_button=check_prepend_minus_button,
            show_run_search_on_exit=show_run_search_on_exit,
            sort_vals=sort_vals,
            multi_selection_enabled=multi_selection_enabled,
            context=context,
        )
        if d.exec():
            return d
        else:
            return None
    else:
        if isinstance(input.test_output_key_list, list) and isinstance(
            input.test_output_key_list[0], list
        ):  # nested lists only for dnf:/dnc:
            keylist = input.test_output_key_list[input.counter]
            input.counter += 1
        else:
            keylist = input.test_output_key_list
        d = Object()
        d.tooltip_after_exit_for_parent = None
        # class input is defined in code for testing
        d.just_returned_input_line_content = input.test_manual_regular_accept
        d.inputline = (input.test_manual_just_line,)
        d.sel_keys_list = keylist
        d.sel_value_from_dict = input.test_output_sel_value_from_dict
        d.neg = (
            check_prepend_minus_button
            if not input.test_manual_override_in_dialog_for_neg
            else not check_prepend_minus_button
        )
        d.addstar = input.test_manual_override_in_dialog_for_star
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
        return None, None, None
    else:
        if d.sel_keys_list == value_for_all:
            return d.sel_keys_list, "", False
        lineonly, _, override_add_star, negate = overrides()
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
        return d.sel_keys_list, out, neg


def note_filter_helper(parent, col, remaining_sentence, prefixed_with_minus):
    infotext = f"""
<span>
In a first step select the note type to search. After this you'll see a dialog to narrow 
by {remaining_sentence}
</span>
"""
    note_type_list, fmt, neg = filter_dialog_and_overrides(
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
    return note_type, fmt, neg


def note__card(parent, col, prefixed_with_minus):
    remaining = "only if the note has multiple cards/card templates."
    # e.g. model = "Basic"; model_search_string = "note:Basic"; modelneg = False
    model, model_search_string, modelneg = note_filter_helper(parent, col, remaining, prefixed_with_minus)
    if not model:
        return None, None, None

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
        card_list, card_search_string, cardneg = filter_dialog_and_overrides(
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
            return None, None, None
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
    return out, 0, cardneg


def note__field(parent, col, prefixed_with_minus):
    remaining = "field (if the note has more than one field)."
    model, model_search_string, modelneg = note_filter_helper(parent, col, remaining, prefixed_with_minus)
    if not model:
        return None, None, None

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
        field_list, field_search_string, fieldneg = filter_dialog_and_overrides(
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
            return None, None, None
        field = field_list[0]

    posback = 0
    field_search_string = emc(field_search_string)
    if field_search_string:
        field_search_string += ":**"
        posback = -2
    # quote if needed
    model_search_string = emc(model_search_string)
    if " " in model_search_string:
        model_search_string = '"' + model_search_string + '"'
    # always quote field search string so that user can type in spaces
    field_search_string = '"' + field_search_string + '"'

    maybe_space = " " if model_search_string and field_search_string else ""
    out = model_search_string + maybe_space + field_search_string

    return out, posback, fieldneg


def note__field__card__helper(parent, col, term, before, after, chars_to_del, prefixed_with_minus):
    """
    this function and the functions it's calling are from early 2020. They deserve
    to be simplified and shortened and maybe merged back into the general code below.
    But they seem to work so I'm not touching them.
    """
    if term == "dnf:":
        out, tomove, prefixed_with_minus = note__field(parent, col, prefixed_with_minus)
    else:  # "dnc:"
        out, tomove, prefixed_with_minus = note__card(parent, col, prefixed_with_minus)
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
        return (new_text, newpos, False)
    else:
        return None, None, None


def get_date_range(parent, col, search_operator, before, after, chars_to_del, prefixed_with_minus):
    if in_full_anki_with_gui:
        test_lower = test_upper = test_custom_datetime = None
    else:
        # class input is defined in testing code
        test_lower = input.test_date_lower
        test_upper = input.test_date_upper
        test_custom_datetime = input.test_custom_datetime

    success, searchtext, TriggerSearchAfter = get_date_range_string(
        parent, col, search_operator, prefixed_with_minus, test_lower, test_upper, test_custom_datetime
    )
    if not success:
        return (None, None, None)
    else:
        _, override_autosearch_default, _, _ = overrides()
        if override_autosearch_default:
            TriggerSearchAfter ^= True
        spaces = maybe_add_spaced_between(before, chars_to_del)
        remove_these = chars_to_del + 1 if prefixed_with_minus else chars_to_del
        new_text = before[:-remove_these] + spaces + searchtext + after
        if chars_to_del == len(before):  # whole before will be deleted -> no leading space required
            spaces = ""
        newpos = len(before[:-chars_to_del] + spaces + searchtext)
        return (new_text, newpos, TriggerSearchAfter)


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
                    return (new_text, newpos, False)  # False here means: do not trigger search

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
                    return (new_text, newpos, False)


def onSearchEditTextChange(
    parent, move_dialog_in_browser, include_filtered_in_deck, input_text, cursorpos, from_button=False
):
    """
    parent: Browser, filtered_deck.FilteredDeckConfigDialog
    """
    col = parent.col

    if cursorpos is None:
        before = input_text
        after = ""
    else:
        before = input_text[:cursorpos]
        after = input_text[cursorpos:]

    did_regex_replacements = regex_replacements(before, after)
    if did_regex_replacements:
        # new_text, newpos, do_not_trigger_search
        return (did_regex_replacements[0], did_regex_replacements[1], False)

    if after and not after.startswith(" "):
        after = " " + after
    TriggerSearchAfter = False

    vals = {}

    for abbrev in ["dnf:", "dnc:"]:
        if before[-4:] == abbrev:
            prefixed_with_minus = True if minus_precedes_search_operator(before, abbrev) else False
            char_to_del = len(abbrev) + 1 if minus_precedes_search_operator else len(abbrev)
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
            "insert_space_at_pos_in_before": before inserting selected additional search string

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
        }
        """

        vals = {
            "remove_from_end_of_before": int(f"-{remove_from_end}"),
            "insert_space_at_pos_in_before": 0,
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
            "context": "tag_and_deck_xx",
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
            "insert_space_at_pos_in_before": -6,
            "dict_for_dialog": False,
            "values_for_filter_dialog": fieldnames(col),
            "surround_with_quotes": True,
            "infotext": field_infotext + details_about_searching_fields,
            "windowtitle": "Anki: Select field to search",
            "show_prepend_minus_button": True,
            "check_prepend_minus_button": prefixed_with_minus,
            "show_star": True,
            "check_star": False,
            "sort_vals": True,
            "context": "field",
        }

    if matches_search_operator(before, "prop:") and (
        gc(["open filter dialog after typing these search operators", "modify_props"]) or from_button
    ):
        it = "<b>After closing the dialog you must adjust what's inserted with your numbers</b>"
        prefixed_with_minus = True if minus_precedes_search_operator(before, "prop:") else False
        vals = {
            "remove_from_end_of_before": -1 if prefixed_with_minus else 0,
            "insert_space_at_pos_in_before": -5,
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
        }

    if matches_search_operator(before, "is:") and (
        gc(["open filter dialog after typing these search operators", "modify_is"]) or from_button
    ):
        expl = gc(["open filter dialog after typing these search operators", "modify_is__show_explanations"])
        prefixed_with_minus = True if minus_precedes_search_operator(before, "is:") else False
        vals = {
            "remove_from_end_of_before": (0 if expl else -3) - (1 if prefixed_with_minus else 0),
            "insert_space_at_pos_in_before": -3,
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
        }

    if matches_search_operator(before, "flag:") and (
        gc(["open filter dialog after typing these search operators", "modify_flag"]) or from_button
    ):
        prefixed_with_minus = True if minus_precedes_search_operator(before, "flag:") else False
        vals = {
            "remove_from_end_of_before": -1 if prefixed_with_minus else 0,
            "insert_space_at_pos_in_before": -5,
            "dict_for_dialog": "flags",
            "values_for_filter_dialog": {
                "red": "1",
                "orange": "2",
                "green": "3",
                "blue": "4",
                "pink": "5",
                "turquoise": "6",
                "purple": "7",
                "no flags": "0",
            },
            "surround_with_quotes": False,
            "infotext": False,
            "windowtitle": "Anki: Search by Flag",
            "show_prepend_minus_button": True,
            "check_prepend_minus_button": prefixed_with_minus,
            "show_star": False,
            "check_star": False,
            "sort_vals": True,
            "context": "flag",
        }

    tag_search = matches_search_operator(before, "tag:") and (
        gc(["open filter dialog after typing these search operators", "modify_tag"]) or from_button
    )
    if tag_search:
        prefixed_with_minus = True if minus_precedes_search_operator(before, "tag:") else False
        vals = {
            "remove_from_end_of_before": -1 if prefixed_with_minus else 0,
            "insert_space_at_pos_in_before": -4,
            "dict_for_dialog": False,
            "values_for_filter_dialog": tags(col),
            "surround_with_quotes": False,
            "infotext": False,
            "windowtitle": "Anki: Select tag to search",
            "show_prepend_minus_button": True,
            "check_prepend_minus_button": prefixed_with_minus,
            "show_star": False,  # since at least 2.1.50 searching for tag:aa also matches tag:aa:bb etc.
            "check_star": False,
            "sort_vals": True,
            "multi_selection_enabled": True,
            "context": "tag",
        }

    elif matches_search_operator(before, "note:") and (
        gc(["open filter dialog after typing these search operators", "modify_note"]) or from_button
    ):
        prefixed_with_minus = True if minus_precedes_search_operator(before, "note:") else False
        vals = {
            "remove_from_end_of_before": -1 if prefixed_with_minus else 0,
            "insert_space_at_pos_in_before": -5,
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
            "context": "note",
        }

    elif matches_search_operator(before, "card:") and (
        gc(["open filter dialog after typing these search operators", "modify_card"]) or from_button
    ):
        prefixed_with_minus = True if minus_precedes_search_operator(before, "card:") else False
        vals = {
            "remove_from_end_of_before": -1 if prefixed_with_minus else 0,
            "insert_space_at_pos_in_before": -5,
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
            "context": "card",
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
            "remove_from_end_of_before": -1 if prefixed_with_minus else 0,
            "insert_space_at_pos_in_before": -4,
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
        }

    if matches_search_operator(before, "ffn:"):
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
            "remove_from_end_of_before": -1 if prefixed_with_minus else 0,
            "insert_space_at_pos_in_before": -4,
            "dict_for_dialog": "ffn",
            "values_for_filter_dialog": fieldnames_modelname_dict(),
            "surround_with_quotes": True,
            "infotext": ffn_infotext + details_about_searching_fields,
            "windowtitle": "Anki: Select Field to search from selected Note Type",
            "show_prepend_minus_button": False,
            "check_prepend_minus_button": prefixed_with_minus,
            "show_star": False,
            "check_star": False,
            "sort_vals": True,
            "context": "field_from_note_ffn",
        }

    elif matches_search_operator(before, "deck:") and gc(
        ["open filter dialog after typing these search operators", "modify_deck"]
    ):
        prefixed_with_minus = True if minus_precedes_search_operator(before, "deck:") else False
        vals = {
            "remove_from_end_of_before": -1 if prefixed_with_minus else 0,
            "insert_space_at_pos_in_before": -5,
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
            "multi_selection_enabled": vals.get("multi_selection_enabled"),
            "context": "deck",
        }

    if not vals:
        return (None, None, None)

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
    )
    if not d:
        return (None, None, None)
    else:
        if d.tooltip_after_exit_for_parent:
            tooltip(d.tooltip_after_exit_for_parent, period=6000)

        just_returned_input_line_content, override_autosearch_default, override_add_star, negate = overrides()
        if d.just_returned_input_line_content:
            just_returned_input_line_content = True
        TriggerSearchAfter = d.run_search_on_exit
        # if override_autosearch_default:
        #     TriggerSearchAfter ^= True
        # print(f"d.sel_keys_list is {d.sel_keys_list}")
        # print(f"d.inputline is {d.inputline}")
        # print(f"d.sel_value_from_dict is {d.sel_value_from_dict}")
        # print(f"just_returned_input_line_content is {just_returned_input_line_content}")

        is_exclusion = any([d.neg, negate])

        if vals["remove_from_end_of_before"] != 0:
            befmod = before[: vals["remove_from_end_of_before"]]
        else:  # equal to   vals["remove_from_end_of_before"] == 0    or    not vals["remove_from_end_of_before"]
            befmod = before

        ############ return for some special dialogs:
        if vals["dict_for_dialog"] == "cfn":
            mycard = d.sel_value_from_dict[0]
            mynote = d.sel_value_from_dict[1]
            mysearch = f"""("card:{emc(mycard)}" and "note:{emc(mynote)}")"""
            already_in_line = befmod[:-4]  # substract cfn:
            is_exclusion = False  # - doesn't really make sense here
            new_text = already_in_line + ("-" if is_exclusion else "") + mysearch + after
            new_pos = len(already_in_line + ("-" if is_exclusion else "") + mysearch)
            return (new_text, new_pos, TriggerSearchAfter)
        if vals["dict_for_dialog"] == "ffn":
            field = d.sel_value_from_dict[0]
            mynote = d.sel_value_from_dict[1]
            mysearch = f'''"note:{emc(mynote)}" "{emc(field)}:**"'''
            already_in_line = befmod[:-4]  # substract ffn:
            is_exclusion = False  # - doesn't really make sense here
            new_text = already_in_line + ("-" if is_exclusion else "") + mysearch + after
            new_pos = (
                len(already_in_line + ("-" if is_exclusion else "") + mysearch) - 2
            )  # -2 I need to go back 2 for *"
            return (
                new_text,
                new_pos,
                False,
            )  # triggering a search makes no sense here: the user needs to fill in the search term for the field
        elif vals["dict_for_dialog"] == "is_with_explanations":
            already_in_line = befmod[:-3]  # substract is:
            new_text = already_in_line + ("-" if is_exclusion else "") + d.sel_value_from_dict + after
            new_pos = len(already_in_line + ("-" if is_exclusion else "") + d.sel_value_from_dict)
            return (
                new_text,
                new_pos,
                False,
            )  # triggering a search makes no sense here: the user needs to fill in the search term for is:
        elif vals["dict_for_dialog"] == "prop":
            already_in_line = befmod[:-5]  # substract prop:
            new_text = already_in_line + ("-" if is_exclusion else "") + d.sel_value_from_dict + after
            new_pos = len(already_in_line + ("-" if is_exclusion else "") + d.sel_value_from_dict)
            return (
                new_text,
                new_pos,
                False,
            )  # triggering a search makes no sense here: the user needs to fill in the search term for prop:

        ############ generate sel_list
        if vals["dict_for_dialog"] == "flags":
            sel_list = [d.sel_value_from_dict]

        if just_returned_input_line_content:
            # if do_tag_deck_search: maybe add tag or deck??? BUT if the user wanted this then they wouldn't have chosen only_input_line ...
            sel_list = [d.inputline]

        # if list is returned, escape some characters and store if the terms need quoting
        # vals["dict_for_dialog"]: UseFilterDialogValue: if values tuple with info - list as input -> False
        if not vals["dict_for_dialog"]:
            sel_list = [emc(e) for e in d.sel_keys_list]
            chars_that_needs_quoting = ["(", ")"]
            if tag_search:
                for c in chars_that_needs_quoting:
                    for element in sel_list:
                        if c in element:
                            vals["surround_with_quotes"] = True
                            break

        ############ maybe add '*' to match other deeper nested hierarchical tags, also handle tag/deck multiple matches
        join_list_with = " "
        for idx, member in enumerate(sel_list):
            if member in ["none", "filtered", "tag:none", "deck:filtered", "re:"]:
                pass
            elif before[-4:] == "tag:":
                # no star at the end needed:
                #   since at least 2.1.50 (and in 2024-03):
                #   e.g. you have tags ab ab::yz
                #   "tag:ab" will also match ab::yz
                #   the star is only needed to match partial tags e.g. tag:a*
                #   -> my dialog always matches full tags so I never need the star
                #   to match a tag without subtags you'd type:  tag:ab -tag:ab::*
                befmod = befmod[:-4]  # prevent next line from creating "tag:tag:" for first element
                join_list_with = " OR " if is_exclusion else " OR "
                member = f"tag:{member}"
            # in 2.1.24 card: and note: can also use *
            elif before[-5:] == "card:":
                if d.addstar and not override_add_star:
                    member = member + "*"
            elif before[-5:] == "note:":
                if d.addstar and not override_add_star:
                    member = member + "*"
            elif before[-5:] == "deck:" and gc(
                ["open filter dialog after typing these search operators", "modify_deck"]
            ):
                if d.addstar and not override_add_star:
                    member = member + "*"
                join_list_with = " " if is_exclusion else " OR "
                befmod = befmod[:-5]  # prevent next line from creating "deck:deck:" for first element
                member = f"deck:{member}"
            elif before[-6:] == "field:":
                member = member + "**"
            # ugly fix for xx etc.
            elif do_tag_deck_search:
                if d.addstar and not override_add_star:
                    member = member + "*"
            sel_list[idx] = member

        ############ surround terms with quotes
        if vals["surround_with_quotes"]:
            sel_list = ['"' + e + '"' for e in sel_list]

        ############ exclusion multiple should be grouped
        merged = join_list_with.join(sel_list)  # at the moment
        if is_exclusion:
            if len(sel_list) > 1:
                merged = f"-({merged})"
            else:
                merged = f"-{merged}"
        new_text = befmod + merged + after
        newpos = len(befmod + merged)
        return (new_text, newpos, TriggerSearchAfter)


if not in_full_anki_with_gui:
    # if not __name__.startswith("1052724801"):
    # if __name__ == "__main__" doesn't work with relative imports outside of a module
    # To run this code/file outside of anki:
    #     1. set cwd to addon repo
    #     2. python3 -m src.onTextChange "collection_path"
    # see e.g. https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
    # to load the collection without the gui, see: https://addon-docs.ankiweb.net/command-line-use.html

    # this add-on has three error-prone parts:
    #    1. the matching inside the filter_dialog with filter_dialog.process_search_string_withStart
    #    2. how the date string is generated for upper and lower dates from dialog__date.date_range_string_from_upper_and_lower
    #    3. if onSearchEditTextChange from this file works correctly (assuming what 1 and 2 return are correct)
    #       here you can test 2 implicitly by running it with "dadded:" and so on.

    # instead of learning about gui testing (@mock.patch decorator?) or completly rewriting this file so that I have smaller/more specialized functions
    # I minimally refactored the code so that gui dialog inputs are hidden behind these functions:
    #   onTextChange.get_filter_dialog_output
    #   onTextChange.get_date_range in combination with dialog_date.get_date_range_string
    # When I'm running outside the regular gui-anki these functions get the output of the gui dialogs from the variable input that
    # references a class that I define below

    import datetime
    import dataclasses
    import sys

    # override some functions:
    def tooltip(text, parent=None, period=3000):
        print(text)

    def overrides():
        lineonly = False
        override_autosearch_default = False
        override_add_star = False
        negate = False
        return lineonly, override_autosearch_default, override_add_star, negate

    @dataclasses.dataclass
    class Input:
        input_text: str = ""
        cursorpos: int = 0
        test_output_key_list: list = dataclasses.field(
            default_factory=list
        )  # for dnf/dnc that use two dialogs nested list
        test_output_sel_value_from_dict: dict = dataclasses.field(default_factory=dict)
        test_manual_override_in_dialog_for_neg: bool = False
        test_manual_override_in_dialog_for_star: bool = False
        test_manual_regular_accept: bool = False
        test_manual_just_line: bool = False
        test_date_lower: int | None = None
        test_date_upper: int | None = None
        test_custom_datetime: datetime.datetime | None = None

    test_cases = [
        [
            Input(
                input_text="-tag:",
                cursorpos=len("-tag:"),
                test_output_key_list=["aa", "bb"],
                test_output_sel_value_from_dict=None,
                test_manual_override_in_dialog_for_neg=False,
                test_manual_override_in_dialog_for_star=False,
                test_manual_regular_accept=True,
                test_manual_just_line=False,
                test_date_lower=None,
                test_date_upper=None,
                test_custom_datetime=None,
            ),
            # new_text, newpos, TriggerSearchAfter
            ["-(tag:aa OR tag:bb)", 19, True],
        ],
        [
            Input(
                input_text="tag:",
                cursorpos=len("tag:"),
                test_output_key_list=["!My_Tags::Jacob::!Expansion::Step_01::#NBME::24"],
                test_output_sel_value_from_dict=None,
                test_manual_override_in_dialog_for_neg=False,
                test_manual_override_in_dialog_for_star=False,
                test_manual_regular_accept=True,
                test_manual_just_line=False,
                test_date_lower=None,
                test_date_upper=None,
                test_custom_datetime=None,
            ),
            # new_text, newpos, TriggerSearchAfter
            [
                "tag:!My\_Tags::Jacob::!Expansion::Step\_01::#NBME::24",
                len("tag:!My\_Tags::Jacob::!Expansion::Step\_01::#NBME::24"),
                True,
            ],
        ],
        [
            Input(
                input_text="ffn:",
                cursorpos=len("ffn:"),
                test_output_key_list=None,
                test_output_sel_value_from_dict=("Back", "Basic"),
                test_manual_override_in_dialog_for_neg=False,
                test_manual_override_in_dialog_for_star=False,
                test_manual_regular_accept=True,
                test_manual_just_line=False,
                test_date_lower=None,
                test_date_upper=None,
                test_custom_datetime=None,
            ),
            # new_text, newpos, TriggerSearchAfter
            ['"note:Basic" "Back:**"', len('"note:Basic" "Back:**"') - 2, False],
        ],
        [
            Input(
                input_text="dadded:",
                cursorpos=len("dadded:"),
                test_output_key_list=None,
                test_output_sel_value_from_dict=None,
                test_manual_override_in_dialog_for_neg=False,
                test_manual_override_in_dialog_for_star=False,
                test_manual_regular_accept=True,
                test_manual_just_line=False,
                test_date_lower=5,
                test_date_upper=4,
                test_custom_datetime=None,
            ),
            # new_text, newpos, TriggerSearchAfter
            ["added:5 -added:3", len("added:5 -added:3"), True],
        ],
        [
            Input(
                input_text="dnf:",
                cursorpos=len("dnf:"),
                test_output_key_list=[["Basic"], ["Back"]],
                test_output_sel_value_from_dict=None,
                test_manual_override_in_dialog_for_neg=False,
                test_manual_override_in_dialog_for_star=False,
                test_manual_regular_accept=True,
                test_manual_just_line=False,
                test_date_lower=5,
                test_date_upper=4,
                test_custom_datetime=None,
            ),
            # new_text, newpos, TriggerSearchAfter
            ['note:Basic "Front:**"', len('note:Basic "Front:**"'), False],
        ],
    ]

    from anki.collection import Collection

    col = Collection(sys.argv[1])
    parent = Object()
    parent.col = col
    if not isinstance(col, Collection):
        print("error on loading the collection. Aborting ...")
        sys.exit()

    test_count = 0
    for input, expected_output in test_cases:
        input.counter = 0
        newtext, newpos, triggersearch = onSearchEditTextChange(
            parent=parent,
            move_dialog_in_browser=False,
            include_filtered_in_deck=True,
            input_text=input.input_text,
            cursorpos=input.cursorpos,
            from_button=True,
        )
        print(
            f"\n\n\nrunning test {test_count} for ||{input.input_text}|| and filter dialog output||{input.test_output_key_list if input.test_output_key_list else input.test_output_sel_value_from_dict}|| ..."
        )
        test_count += 1
        for idx, elem in enumerate([newtext, newpos, triggersearch]):
            if elem == expected_output[idx]:
                print(f'        {["newtext", "newpos", "triggersearch"][idx]}✓')
            else:
                print("\nERROR")
                print(f"   ||{elem}||")
                print(f"   ||{expected_output[idx]}||")
