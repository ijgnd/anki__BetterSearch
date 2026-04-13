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

from .onTextChange import onSearchEditTextChange

class Object:
    pass



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
    dict_for_dialog: bool = False


simple_cases = [
    ["-tag:", ["*aa", "bb"], "-tag:\*aa -tag:bb"],
    ["tag:",  ["!My_Tags::Jacob::!Expansion::Step_01::#NBME::24"], "tag:!My\_Tags::Jacob::!Expansion::Step\_01::#NBME::24"],
    
    ["deck:",  ["*a _\\a"], '"deck:\*a \_\\\\a"'],
    ["-deck:", ["a _\\a"], '-"deck:a \_\\\\a"'],
    ["-deck:", ["a _\\a", "b \\b"], '-"deck:a \_\\\\a" -"deck:b \\\\b"'],

    ["note:",  ["*a _a"], '"note:\*a \_a"'],
    ["-note:", ["*a _a"], '-"note:\*a \_a"'],
    ["-note:", ["*a _a", "b b"], '-"note:\*a \_a" -"note:b b"'],

    ["card:",  ["*a _a"], '"card:\*a \_a"'],
    ["-card:", ["*a _a"], '-"card:\*a \_a"'],
    ["-card:", ["*a a", "b b"], '-"card:\*a a" -"card:b b"'],

    ["field:",  ["*a _a"], '"\*a \_a:**"'],
    ["-field:", ["*a _a"], '-"\*a \_a:**"'],
    ["-field:", ["*a _a", "b b"], '-"\*a \_a:**" -"b b:**"'],
    
    ["xx",   ['deck:AnKing::Step 1::Lolnotacop::Drugs', 'tag:!AK_UpdateTags::Step1decks::Lolnotacop::Drugs'], '''"deck:AnKing::Step 1::Lolnotacop::Drugs" tag:!AK\\_UpdateTags::Step1decks::Lolnotacop::Drugs'''],
    ["xx",   ['tag:*a_(a', 'deck:b c'], '"tag:\*a\_(a" "deck:b c"'],
    ["all:", ['tag:*a_a', 'deck:b c'], 'tag:\*a\_a "deck:b c"'],
    
    # flag: -> detailed_test needed because dict

    ## special handling earliest on top
    # ["dnf:",  [["Basic"], ["Back"]], 'note:Basic "Back:**"'],
    # dnc

    ## special handling earliest on top
    # dadded:
    # dedited:
    # drated:
    # dintroduced:
    # dresched:

    ## special handling earlier
    # prop:
    # cfn:
    # ffn:
]

test_cases = []

for input_text, test_output_key_list, search_string in simple_cases:
    test_cases.append(
        [
            Input(
                input_text=input_text,
                cursorpos=len(input_text),
                test_output_key_list=test_output_key_list,
                test_output_sel_value_from_dict=None,
                test_manual_override_in_dialog_for_neg=False,
                test_manual_override_in_dialog_for_star=False,
                test_manual_regular_accept=False,
                test_manual_just_line=False,
                test_date_lower=None,
                test_date_upper=None,
                test_custom_datetime=None,
            ),
            # new_text, newpos, TriggerSearchAfter
            [search_string, len(search_string), False],
        ],
    )


detailed_tests = [
    [
        Input(
            input_text="ffn:",
            cursorpos=len("ffn:"),
            test_output_key_list=None,
            test_output_sel_value_from_dict=("Back", "Basic"),
            test_manual_override_in_dialog_for_neg=False,
            test_manual_override_in_dialog_for_star=False,
            test_manual_regular_accept=True,
        ),
        # new_text, newpos, TriggerSearchAfter
        ['"note:Basic" "Back:**"', len('"note:Basic" "Back:**"') - 2, False],
    ],
    [
        Input(
            input_text="is:",
            cursorpos=len("is:"),
            test_output_key_list=None,
            test_output_sel_value_from_dict="is:learn is:review",
            test_manual_override_in_dialog_for_neg=False,
            test_manual_override_in_dialog_for_star=False,
            test_manual_regular_accept=True,
        ),
        # new_text, newpos, TriggerSearchAfter
        ['is:learn is:review', len('is:learn is:review'), False],
    ],
    [
        Input(
            input_text="dadded:",
            cursorpos=len("dadded:"),
            test_output_key_list=None,
            test_output_sel_value_from_dict=None,
            test_manual_regular_accept=True,
            test_date_lower=5,
            test_date_upper=4,
            test_custom_datetime=None,
        ),
        # new_text, newpos, TriggerSearchAfter
        ["added:5 -added:3", len("added:5 -added:3"), False],
    ],
    [
        # 6
        Input(
            input_text="-flag:",
            cursorpos=len("-flag:"),
            test_output_key_list=None,
            test_output_sel_value_from_dict=5,
            dict_for_dialog="flags"
        ),
        # new_text, newpos, TriggerSearchAfter
        ['-flag:5', len('-flag:5'), False],
    ],
]


test_cases.extend(detailed_tests)


from anki.collection import Collection

col = Collection(sys.argv[1])
parent = Object()
parent.col = col
if not isinstance(col, Collection):
    print("error on loading the collection. Aborting ...")
    sys.exit()

test_count = 1
for input, expected_output in test_cases:
    input.counter = 0
    print(
        f"\n\n\nrunning test {test_count} for ||{input.input_text}|| and filter dialog output||{input.test_output_key_list if input.test_output_key_list else input.test_output_sel_value_from_dict}|| ..."
    )
    print(input.test_output_sel_value_from_dict)
    newtext, newpos, triggersearch = onSearchEditTextChange(
        parent=parent,
        move_dialog_in_browser=False,
        include_filtered_in_deck=True,
        input_text=input.input_text,
        cursorpos=input.cursorpos,
        from_button=True,
        test_input=input,
    )
    test_count += 1
    for idx, elem in enumerate([newtext, newpos, triggersearch]):
        if elem == expected_output[idx]:
            print(f'        {["newtext", "newpos", "triggersearch"][idx]}✓')
        elif not elem and not expected_output[idx]:
            # maybe elem is False and expected_putput[idx] is None: this is ok
            print(f'        {["newtext", "newpos", "triggersearch"][idx]}✓ (not (False/None))') 
        else:
            print("\nERROR")
            print(f"   ||{elem}||")
            print(f"   ||{expected_output[idx]}||")
