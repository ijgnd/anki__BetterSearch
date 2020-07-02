<b>Before you change the config make sure to read the descriptions below and/or watch the 
following [AnKingMed](https://www.ankingmed.com/) video:</b>

This add-on used to be named "Browser Search Box: Quick Insert Tag, Deck, Notetype". The name
was changed because now it offers much more than this.

<h3># Important notes</h3>
- Besides the functions described on ankiweb this add-on has some additional features, e.g. there's
a menu entry and custom shortcut to open your search history in a filter dialog where long searches 
are split up into multiple lines. The setting is 
`shortcut - select entry from history in fuzzy dialog` (default is "Ctrl+H, h").
- When closing the multi-line dialog newlines and tabs are replaced by spaces.
- The default shortcut to open the multi-line dialog is "Ctrl+t, s". You press "Ctrl+t", 
then release both keys and then press "s". On MacOS instead of "Ctrl+t" you use "Cmd+t".
- If you don't know the difference between the Anki terms *note* and *card* this add-on might be 
confusing. For details see the [manual](https://docs.ankiweb.net/#/), or see 
[here](https://www.reddit.com/r/Anki/comments/8w2b5e/the_fundamental_principle_of_anki_card_creation/) 
or 
[here](https://www.reddit.com/r/Anki/comments/9nkg7i/how_do_i_create_separate_card_types_in_different/e7n0x5n/) or [this youtube video](https://www.youtube.com/watch?v=fUKPtnx8LC0).
- when you type in "card:" this add-on will show you a list of card *names*. In Anki you can also
search by card type *number*. For cloze note types you can only search by card type numbers. If 
you have mostly cloze notes (e.g. if you use the AnKing decks) and often search for specific 
cloze cards with e.g. "card:2" you might want to set the config key `modify_card` to "false". 
- This add-on is quite complex so you might find a bug/problem. If you do let me know
in the [support thread in the anki support forum](https://forums.ankiweb.net/t/browser-search-box-quick-insert-tag-deck-notetype-official-thread/547) or on 
[github](https://github.com/ijgnd/anki__browser_search__quick_insert_tag_deck_notetype/issues").

&nbsp;

<h3># Details</h3>
Most of the options should have telling names. Here are some notes about some options:

- `Add Button to the Browser Search Bar` (default is "true"): whether the "SearchDialog" 
button is shown in the browser.
- `Multiline Dialog: use bigger typewriter font` (default is "true"): This only affects the font 
size in the text box of the extra dialog.
- `Multiline Dialog: shortcut: open window` (default is "Ctrl+t,s"): This shortcut is 
active in the browser and opens a new multi-line window where you can edit the current 
search term.
- `Multiline Dialog: Filter Button overwrites by default` (default is "false"): Depending on the
Anki version you use there's a button "Filter" in the lower left of the multi-line window. This
button is similar to the "Filter" button in the browser. The "Filter" button in the browser
overwrites your search with what you selected. I don't like this so I made this option and set 
it to "false".
- `Multiline Dialog: Shortcut inside: Open History` (default is "Ctrl+H, h"): Inside the multi-line
edit dialog you can insert a prior search which overwrites what's currently in the field.

&nbsp;

- `also use in create filtered deck dialog` (default is "true"): whether to show this dialog in the 
filtered deck dialog. The shortcuts set in this config won't work in the create filtered deck 
dialog. 
The deck list won't include existing filtered decks because cards that are already in a filtered 
deck can't be added to another filtered deck.

&nbsp;

- `autoadjust FilterDialog position` (default is "True"): refers to the positioning of the filter
dialog in the browser.

&nbsp;

- `custom tag&deck string 1` (default is "xx"), `custom tag&deck string 2` (default is "all:"): when 
you type into the browser search box if the last characters match the ones set in these settings 
a dialog with a list of your tags and decks is opened. The selected entry is inserted into the 
search box.

&nbsp;

- `date range dialog for added: string` (default is "dadded:") and 
`date range dialog for rated: string` (default is "drated:") open a dialog with a calender-widget
if you type "dadded"/"drated" into the browser search bar.

&nbsp;

- `ignore upper and lower case (case insensitive search)` (default is "false"): if this setting 
is "true" the search will be case insensitive. If "false" (the default) typing only in lower case 
means case insensitive search while one upper case character makes the search case sensitive.

&nbsp;

- `modify_card` (default is true): If true, when you type into the browser search box if and the 
characters before the cursor are "card:" a dialog with a list of your card types is opened. 
The selected entry is inserted into the search box.
- The other `modify...` config keys work the same way: For `modify_deck` it's "deck:", for 
`modify_note` it's "note:", for `modify_tag` it's "tag:", etc. 

&nbsp;

- `tag insertion - add '*' to matches` (default is "all"): possible values: "all", "if_has_subtags",
"none"

<h3># modifier keys</h3>
The settings

-  `modifier for override autosearch default`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(default is "Shift"), 
-  `modifier for override add * default`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(default is "Meta"), 
-  `modifier for negate`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(default is "Alt"),
-  `modifier for insert current text only`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(default is "Ctrl")

only accept the values "Shift", "Meta", "Alt", "Ctrl" as input. On a Mac "Ctrl" means "Cmd". 
**You may not use "Cmd" for these four config values.**.
