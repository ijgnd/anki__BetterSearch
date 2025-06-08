from .anki_version_detection import anki_point_version
from .config import gc


def cardnames(col):
    cards = set()
    for m in col.models.all():
        for t in m["tmpls"]:
            cards.add(t["name"])
    return list(cards)


def decknames(col, also_include_filtered, prepend_with_deck=False):
    decks = col.decks.allNames(dyn=also_include_filtered)
    # also_include_filtered only True in the browser but not in the Create Filtered Deck dialog
    # Filtered decks can't include filtered decks so I don't want "filtered" for those.
    if also_include_filtered:
        decks += ["filtered"]
    if prepend_with_deck:
        decks = ["deck:" + d for d in decks]
    return sorted(decks)


def tags(col, prepend_with_tag=False):
    tags = col.tags.all() + ["none"]
    if prepend_with_tag:  # for xx1 and xx2
        tags = ["tag:" + t for t in tags]
    return sorted(tags)


def is_values():
    return [
        "is:due",
        "is:new",
        "is:learn",
        "is:review",
        "is:suspended",
        "is:buried",
        "is:learn is:review",
        "-is:learn is:review",
        "is:learn -is:review",
    ]


def is_values_with_explanations():
    return {
        "is:due (review cards and learning cards waiting to be studied)": "is:due",
        "is:new (new cards)": "is:new",
        "is:learn (cards in learning)": "is:learn",
        "is:review (reviews (both due and not due) and lapsed cards)": "is:review",
        "is:suspended (cards that have been manually suspended)": "is:suspended",
        "is:buried (cards that have been buried, either automatically (siblings) or manually)": "is:buried",
        "is:learn is:review (cards that have lapsed and are awaiting relearning)": "is:learn is:review",
        "-is:learn is:review (review cards, not including lapsed cards)": "-is:learn is:review",
        "is:learn -is:review (cards that are in learning for the first time)": "is:learn -is:review",
    }

def flag_values():
    return [
        "flag:1",
        "flag:2",
        "flag:3",
        "flag:4",
        "flag:5",
        "flag:6",
        "flag:7",
        "flag:0",
        "-flag:0",
        "-flag:1",
    ]


def flag_values_with_explanations():
    return {
         "red flag": "flag:1",
        "orange flag": "flag:2",
        "green flag": "flag:3",
        "blue flag": "flag:4",
        "pink flag": "flag:5",
        "turquoise flag": "flag:6",
        "purple flag": "flag:7",
        "no flags": "flag:0",
        "any flag": "-flag:0",
        "no red flags": "-flag:1",
    }

def props():
    all_version_texts = {
        "prop:ivl>=10 - cards with interval of 10 days or more": "prop:ivl>=",
        "prop:due=1 - cards due tomorrow": "prop:due=",
        "prop:due=-1 - cards due yesterday that haven't been answered yet": "prop:due=",
        "prop:due>-1 prop:due<1 - cards due between yesterday and tomorrow": "prop:due> prop:due<",
        "prop:reps<10 - cards that have been answered less than 10 times": "prop:reps<",
        "prop:lapses>3 - cards that have moved into relearning more than 3 times": "prop:lapses>",
        "prop:ease!=2.5 - cards easier or harder than default": "prop:ease!=",
        # the following were introduced in 2.1.41 (released in 2021-03-07, in 2024-03 not documented in manual)
        "prop:resched - search for rescheduled cards over specific time periods": "prop:resched",
        "prop:rated - search for rated cards over specific time periods": "prop:rated",
        "prop:pos - search for new card position": "prop:pos",
    }
    fsrs_texts = {
        # "prop:cdn:d>5 - cards with the value of d in custom data greater than 5 (FSRS)": "prop:cdn",
        # "prop:cds:v=reschedule - cards with the string v in custom data equal to reschedule (FSRS)": "prop:cds:",
        " prop:s>21 - cards with stability greater than 21 days (FSRS)": "prop:s>",
        " prop:d>0.3 - cards with difficulty greater than 0.3 (FSRS)": "prop:d>",
        " prop:r<0.9 - cards with retention less than 0.9 (FSRS)": "prop:r<",
    }
    if anki_point_version > 231000:
        return {**all_version_texts, **fsrs_texts}
    else:
        return all_version_texts


def fieldnames(col):
    fieldnames = set()
    for model in col.models.all():
        for t in model["flds"]:
            fieldnames.add(t["name"] + ":")
    return list(fieldnames)


details_about_searching_fields = """
When searching fields keep in mind that searching on fields requires an 'exact match' by default.
<br>Here are some examples from the manual:
 <table border="0" style="border-collapse: collapse; width: 100%;">
  <colgroup>
   <col style="width: 3%;">
   <col style="width: 14%;">
   <col style="width: 3%;">
   <col style="width: 80%;">
  </colgroup>
  <tbody>
   <tr>
    <td>
     <span style="font-size: 90%;">
      &nbsp;
     </span>
    </td>
    <td>
     <span style="font-size: 90%;">
      front:dog
     </span>
    </td>
    <td>
     &nbsp;
    </td>
    <td>
     <span style="font-size: 85%;">
      <i>
       find notes with a field named "Front" of exactly &ldquo;dog&rdquo;. A field that says &ldquo;a dog&rdquo; will not match.
      </i>
     </span>
    </td>
   </tr>
   <tr>
    <td>
     <span style="font-size: 90%;">
      &nbsp;
     </span>
    </td>
    <td>
     <span style="font-size: 90%;">
      front:*dog*
     </span>
    </td>
    <td>
     &nbsp;
    </td>
    <td>
     <span style="font-size: 85%;">
      <i>
       find notes with a field named "Front" containing dog somewhere
      </i>
     </span>
    </td>
   </tr>
   <tr>
    <td>
     <span style="font-size: 90%;">
      &nbsp;
     </span>
    </td>
    <td>
     <span style="font-size: 90%;">
      front:
     </span>
    </td>
    <td>
     &nbsp;
    </td>
    <td>
     <span style="font-size: 85%;">
      <i>
       find notes that have an empty field named "Front"
      </i>
     </span>
    </td>
   </tr>
   <tr>
    <td>
     <span style="font-size: 90%;">
      &nbsp;
     </span>
    </td>
    <td>
     <span style="font-size: 90%;">
      front:_*
     </span>
    </td>
    <td>
     &nbsp;
    </td>
    <td>
     <span style="font-size: 85%;">
      <i>
       find notes that have a non-empty field named "Front"
      </i>
     </span>
    </td>
   </tr>
   <tr>
    <td>
     <span style="font-size: 90%;">
      &nbsp;
     </span>
    </td>
    <td>
     <span style="font-size: 90%;">
      front:*
     </span>
    </td>
    <td>
     &nbsp;
    </td>
    <td>
     <span style="font-size: 85%;">
      <i>
       find notes that have a field named "Front", empty or not
      </i>
     </span>
    </td>
   </tr>
   <tr>
    <td>
     <span style="font-size: 90%;">
      &nbsp;
     </span>
    </td>
    <td>
     <span style="font-size: 90%;">
      fr*:text
     </span>
    </td>
    <td>
     &nbsp;
    </td>
    <td>
     <span style="font-size: 85%;">
      <i>
       find notes in a field whose name is starting with &ldquo;fr&rdquo;
      </i>
     </span>
    </td>
   </tr>
  </tbody>
 </table>
"""


def maybe_add_spaced_between(before, insert_space_at_pos_in_old):
    # if at beginning of line don't insert space after old
    if "\n" in before:
        lines = before.split("\n")
        length_to_compare = len(lines[-1])
    else:
        length_to_compare = len(before)
    if length_to_compare - abs(insert_space_at_pos_in_old) == 0:
        spacing = ""
    else:
        spacing = " "
    return spacing


def emc(s):  # escape some metachars, relevant for search, see rslib
    # Anki also escapes _ in tags - e.g. click a tag in the left sidebar
    return s.replace("*", "\\*").replace("_", "\\_")
