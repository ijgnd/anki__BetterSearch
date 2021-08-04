from anki.utils import pointVersion

from .config import gc


# for multiline add-on
def help_string_for_actions_used():
    lines = []
    if gc("modify_note"):
        s = '"note:" filter by note type (model) name'
        lines.append(s)
    if gc("modify_card"):
        s = '"card:" filter for card (type) names'
        lines.append(s)
    if gc("modify_field"):
        s = '"field:" filter by field name'
        lines.append(s)
    if gc("modify_deck"):
        s = '"deck:" filter by deck name'
        lines.append(s)
    s = '"ffn:" select two filters: field from note'
    lines.append(s)
    s = '"cfn:" select two filters: card from note'
    lines.append(s)
    if gc("modify_tag"):
        s = '"tag:" filter by tag'
        lines.append(s)
    if gc("modify_is"):
        s = '"is:" filter by card state'
        lines.append(s)
    if gc("modify_props"):
        s = '"prop:" filter by card properties (like due date, ease)'
        lines.append(s)
    if gc("custom tag&deck string 1"):
        s = f'"{gc("custom tag&deck string 1")}": filter by deck or tag'
        lines.append(s)
    if gc("custom tag&deck string 2"):
        s = f'"{gc("custom tag&deck string 2")}": filter by deck or tag'
        lines.append(s)
    if gc("date range dialog for added: string"):
        s = f'"{gc("date range dialog for added: string")}": date range dialog for date added'
        lines.append(s)
    if gc("date range dialog for edited: string") and pointVersion() >= 28:
        s = f'"{gc("date range dialog for edited: string")}": date range dialog for date edited'
        lines.append(s)
    if gc("date range dialog for introduced: string") and pointVersion() >= 45:
        s = f'"{gc("date range dialog for introduced: string")}": date range dialog for date introduced'
        lines.append(s)
    if gc("date range dialog for rated: string"):
        s = f'"{gc("date range dialog for rated: string")}": date range dialog for date rated'
        lines.append(s)
    s = """
<div style="font-size: 120%;">
<b>
BetterSearch Add-on: terms/keywords that open a filter dialog:
</b>
</div>
"""
    s += "<ul>"
    for l in lines:
        s += "<li>" + l + "</li>"
    s += "</ul>"
    return s



helptext = help_string_for_actions_used() + """
<br>
<div>
The following section is copied from the manual in 2021-08-04. So you have the search section with you 
even if you are offline. In the future the rest of this page might get replaced with some shorter
notes.
</div>
<ul>
<li><a href="#simple-searches">Simple searches</a></li>
<li><a href="#limiting-to-a-field">Limiting to a field</a></li>
<li><a href="#tags-decks-cards-and-notes">Tags, decks, cards and notes</a></li>
<li><a href="#ignoring-accentscombining-characters">Ignoring accents/combining characters</a></li>
<li><a href="#regular-expressions">Regular expressions</a></li>
<li><a href="#card-state">Card state</a></li>
<li><a href="#card-properties">Card properties</a></li>
<li><a href="#recent-events">Recent Events</a>
<ul>
<li><a href="#added">Added</a></li>
<li><a href="#edited">Edited</a></li>
<li><a href="#answered">Answered</a></li>
<li><a href="#first-answered">First Answered</a></li>
</ul>
</li>
<li><a href="#matching-special-characters">Matching special characters</a>
<ul>
<li><a href="#raw-input">Raw input</a></li>
</ul>
</li>
<li><a href="#object-ids">Object IDs</a></li>
</ul>
<p>Anki's Browse screen and the Filtered Deck feature use a common method
of searching for specific cards/notes.</p>
<h2 id="simple-searches"><a class="header" href="#simple-searches">Simple searches</a></h2>
<p>When you type some text into the search box, Anki finds matching notes
and displays their cards. Anki searches in all fields of the notes, but
does not search for tags (see later in this section for how to search
for tags). Some examples:</p>
<p><code>dog</code><br />
search for &quot;dog&quot; - will match words like &quot;doggy&quot; and &quot;underdog&quot; too.</p>
<p><code>dog cat</code><br />
finds notes that have both &quot;dog&quot; and &quot;cat&quot; on them, such as &quot;raining
cats and dogs&quot;.</p>
<p><code>dog or cat</code><br />
finds notes with either &quot;dog&quot; or &quot;cat&quot;.</p>
<p><code>dog (cat or mouse)</code><br />
finds notes with dog and cat, or dog and mouse.</p>
<p><code>-cat</code><br />
finds notes without the word &quot;cat&quot;.</p>
<p><code>-cat -mouse</code><br />
finds notes with neither &quot;cat&quot; nor &quot;mouse&quot;.</p>
<p><code>-(cat or mouse)</code><br />
same as the above.</p>
<p><code>&quot;a dog&quot;</code><br />
finds notes with the exact sequence of characters &quot;a dog&quot; on them, such
as &quot;atta dog&quot;, but not &quot;dog a&quot; or &quot;adog&quot;.</p>
<p><code>-&quot;a dog&quot;</code><br />
finds notes without the exact phrase &quot;a dog&quot;</p>
<p><code>d_g</code><br />
finds notes with d, &lt;a letter&gt;, g, like dog, dig, dug, and so on.</p>
<p><code>d*g</code><br />
finds notes with d, &lt;zero or more letters&gt;, g, like dg, dog, dung,
etc.</p>
<p><code>w:dog</code><br />
search for &quot;dog&quot; on a word boundary - will match &quot;dog&quot;, but not &quot;doggy&quot;
or &quot;underdog&quot;. Requires Anki 2.1.24+ or AnkiMobile 2.1.61+.</p>
<p><code>w:dog*</code><br />
will match &quot;dog&quot; and &quot;doggy&quot;, but not &quot;underdog&quot;.</p>
<p><code>w:*dog</code><br />
will match &quot;dog&quot; and &quot;underdog&quot;, but not &quot;doggy&quot;.</p>
<p>Things to note from the above:</p>
<ul>
<li>
<p>Search terms are separated by spaces.</p>
</li>
<li>
<p>When multiple search terms are provided, Anki looks for notes that
match all of the terms - an implicit 'and' is inserted between each
term. On Anki 2.1.24+ and AnkiMobile 2.0.60+ you can be explicit
if you like (&quot;dog and cat&quot; is the same as &quot;dog cat&quot;), but older
Anki versions will treat &quot;and&quot; as just another word to search for.</p>
</li>
<li>
<p>You can use &quot;or&quot; if you only need one of the terms to match.</p>
</li>
<li>
<p>You can prepend a minus sign to a term to find notes that don’t
match.</p>
</li>
<li>
<p>You can group search terms by placing them in parentheses, as in the
<strong>dog (cat or mouse)</strong> example. This becomes important when
combining OR and AND searches — in the example, with the
parentheses, it matches either 'dog cat' or 'dog mouse', whereas
without them it would match either 'dog and cat' or 'mouse'.</p>
</li>
<li>
<p>Anki is only able to search within formatting in the <a href="editing.html#customizing-fields">sort
field</a> you’ve configured. For example, if you add
&quot;<strong>exa</strong>mple&quot; to one of your fields, this will not be matched when
searching for &quot;example&quot; unless that field is the sort field. If a
word is not formatted, or the formatting does not change in the
middle of the word, then Anki will be able to find it in any field.</p>
</li>
<li>
<p>Standard searches are case insensitive for Latin characters - a-z will
match A-Z, and vice versa. Other characters such as Cyrillic are case sensitive
in a standard search, but can be made case insensitive by searching on a word
boundary or regular expression (w:, re:).</p>
</li>
</ul>
<h2 id="limiting-to-a-field"><a class="header" href="#limiting-to-a-field">Limiting to a field</a></h2>
<p>You can also ask Anki to match only if a particular field contains some
text. Unlike the searches above, searching on fields requires an 'exact
match' by default.</p>
<p><code>front:dog</code><br />
find notes with a Front field of exactly &quot;dog&quot;. A field that says &quot;a
dog&quot; will not match.</p>
<p><code>front:*dog*</code><br />
find notes with Front field containing dog somewhere</p>
<p><code>front:</code><br />
find notes that have an empty Front field</p>
<p><code>front:_*</code><br />
find notes that have a non-empty Front field</p>
<p><code>front:*</code><br />
find notes that have a Front field, empty or not</p>
<p><code>fr*:text</code>
find notes in a field starting with &quot;fr&quot;. Requires Anki 2.1.24+ or AnkiMobile 2.1.60+.</p>
<h2 id="tags-decks-cards-and-notes"><a class="header" href="#tags-decks-cards-and-notes">Tags, decks, cards and notes</a></h2>
<p><code>tag:animal</code><br />
find notes with the tag &quot;animal&quot;</p>
<p><code>tag:none</code><br />
find notes with no tags</p>
<p><code>tag:ani*</code><br />
find notes with tags starting with ani</p>
<p><code>deck:french</code><br />
find cards in a French deck, or subdecks like French::Vocab</p>
<p><code>deck:french -deck:french::*</code><br />
find cards in French, but not subdecks</p>
<p><code>deck:&quot;french vocab&quot;</code><br />
searching when a deck has a space</p>
<p><code>&quot;deck:french vocab&quot;</code><br />
also ok</p>
<p><code>deck:filtered</code><br />
filtered decks only</p>
<p><code>-deck:filtered</code><br />
normal decks only</p>
<p><code>card:forward</code><br />
search for Forward cards</p>
<p><code>card:1</code><br />
search for cards by template number - eg, to find the second cloze
deletion for a note, you’d use card:2</p>
<p><code>note:basic</code><br />
search for cards with a Basic note type</p>
<h2 id="ignoring-accentscombining-characters"><a class="header" href="#ignoring-accentscombining-characters">Ignoring accents/combining characters</a></h2>
<p>Requires Anki 2.1.24+ or AnkiMobile 2.0.60+.</p>
<p>You can use <code>nc:</code> to remove combining characters (&quot;no combining&quot;). For example:</p>
<p><code>nc:uber</code><br />
matches notes with &quot;uber&quot;, &quot;über&quot;, &quot;Über&quot; and so on.</p>
<p><code>nc:は</code><br />
matches &quot;は&quot;, &quot;ば&quot;, and &quot;ぱ&quot;</p>
<p>Searches that ignore combining characters are slower than regular searches.</p>
<h2 id="regular-expressions"><a class="header" href="#regular-expressions">Regular expressions</a></h2>
<p>Anki 2.1.24+ and AnkiMobile 2.0.60+ support searching in notes with &quot;regular expressions&quot;,
a standard and powerful way of searching in text.</p>
<p>Start a search with <code>re:</code> to search by regular expression. To make things easier, Anki will
treat the following as <a href="#raw-input">raw input</a>, so bear in mind the rules listed there.</p>
<p>Some examples:</p>
<p><code>&quot;re:(some|another).*thing&quot;</code><br />
find notes that have &quot;some&quot; or &quot;another&quot; on them, followed by 0 or more characters, and then &quot;thing&quot;</p>
<p><code>re:\d{3}</code><br />
find notes that have 3 digits in a row</p>
<p>Regular expressions can also be limited to a specific field. Please note that unlike the normal searches
in a specific field, regular expressions in fields don't require an exact match. Eg:</p>
<p><code>front:re:[a-c]1</code><br />
matches uppercase or lowercase a1, B1 or c1 that occurs anywhere in the &quot;Front&quot; field</p>
<p><code>front:re:^[a-c]1$</code><br />
like the above, but will not match if any other text falls before or after a1/b1/c1.</p>
<p>You can learn more about regular expressions here: <a href="https://regexone.com/lesson/introduction_abcs">https://regexone.com/lesson/introduction_abcs</a></p>
<p>Some things to be aware of:</p>
<ul>
<li>The search is case-insensitive by default; use (?-i) at the start to turn on case sensitivity.</li>
<li>Some text like spaces and newlines may be represented differently in HTML - you can
use the HTML editor in the editing screen to see the underlying HTML contents.</li>
<li>For the specifics of Anki's regex support, please see the regex crate documentation: <a href="https://docs.rs/regex/1.3.9/regex/#syntax">https://docs.rs/regex/1.3.9/regex/#syntax</a></li>
</ul>
<h2 id="card-state"><a class="header" href="#card-state">Card state</a></h2>
<p><code>is:due</code><br />
review cards and learning cards waiting to be studied</p>
<p><code>is:new</code><br />
new cards</p>
<p><code>is:learn</code><br />
cards in learning</p>
<p><code>is:review</code><br />
reviews (both due and not due) and lapsed cards</p>
<p><code>is:suspended</code><br />
cards that have been manually suspended</p>
<p><code>is:buried</code><br />
cards that have been buried, either <a href="studying.html#siblings-and-burying">automatically</a> or
manually</p>
<p>Note that with the <a href="https://faqs.ankiweb.net/the-anki-2.1-scheduler.html">new scheduler</a>,
Anki now distinguishes between manually and automatically buried cards so you can
unbury one set without the other.</p>
<p>Cards that have lapsed fall into several of these categories, so it may
be useful to combine them to get more precise results:</p>
<p><code>is:learn is:review</code><br />
cards that have lapsed and are awaiting relearning</p>
<p><code>-is:learn is:review</code><br />
review cards, not including lapsed cards</p>
<p><code>is:learn -is:review</code><br />
cards that are in learning for the first time</p>
<p><code>flag:1</code><br />
cards with a red flag</p>
<p><code>flag:2</code><br />
cards with an orange flag</p>
<p><code>flag:3</code><br />
cards with a green flag</p>
<p><code>flag:4</code><br />
cards with a blue flag</p>
<h2 id="card-properties"><a class="header" href="#card-properties">Card properties</a></h2>
<p><code>prop:ivl&gt;=10</code><br />
cards with interval of 10 days or more</p>
<p><code>prop:due=1</code><br />
cards due tomorrow</p>
<p><code>prop:due=-1</code><br />
cards due yesterday that haven’t been answered yet</p>
<p><code>prop:due&gt;-1 prop:due&lt;1</code><br />
cards due between yesterday and tomorrow</p>
<p><code>prop:reps&lt;10</code><br />
cards that have been answered less than 10 times</p>
<p><code>prop:lapses&gt;3</code><br />
cards that have moved into relearning more than 3 times</p>
<p><code>prop:ease!=2.5</code><br />
cards easier or harder than default</p>
<p>Note that due only matches review cards and learning cards with an
interval of a day or more: cards in learning with small intervals like
10 minutes are not included.</p>
<h2 id="recent-events"><a class="header" href="#recent-events">Recent Events</a></h2>
<h3 id="added"><a class="header" href="#added">Added</a></h3>
<p><code>added:1</code><br />
cards added today</p>
<p><code>added:7</code><br />
cards added in last week</p>
<p>The check is made against card creation time rather than note creation
time, so cards that were generated within the time frame will be
included even if their notes were added a long time ago.</p>
<h3 id="edited"><a class="header" href="#edited">Edited</a></h3>
<p><code>edited:n</code><br />
cards where the note text was added/edited in the last n days.</p>
<p>This requires Anki 2.1.28+ / AnkiMobile 2.0.64+.</p>
<h3 id="answered"><a class="header" href="#answered">Answered</a></h3>
<p><code>rated:1</code><br />
cards answered today</p>
<p><code>rated:1:2</code><br />
cards answered Hard (2) today</p>
<p><code>rated:7:1</code><br />
cards answered Again (1) over the last 7 days</p>
<p><code>rated:31:4</code><br />
cards answered Easy (4) in the last month</p>
<p>Rating searches had been limited to 31 days before version 2.1.39.</p>
<h3 id="first-answered"><a class="header" href="#first-answered">First Answered</a></h3>
<p>On version 2.1.45+, you can also search for the very first review only:</p>
<p><code>introduced:1</code><br />
cards answered for the first time today</p>
<p><code>introduced:365</code><br />
cards answered for the first time within the last 365 days</p>
<h2 id="matching-special-characters"><a class="header" href="#matching-special-characters">Matching special characters</a></h2>
<p>This section was written for Anki 2.1.36+ - earlier versions did not support escaping
characters in certain situations.</p>
<p>As shown in the previous section, some characters like <code>*</code>, <code>_</code> and <code>&quot;</code> have a
special meaning in Anki. If you need to locate those characters in a search,
you need to tell Anki not to treat them specially.</p>
<ul>
<li>
<p><em>Space</em><br />
To match something including spaces, enclose the <code>&quot;entire term&quot;</code> in double
quotes. If it is a colon search, you also have the option to only quote the
<code>part:&quot;after the colon&quot;</code>.</p>
</li>
<li>
<p><code>&quot;</code>, <code>*</code> and <code>_</code><br />
Add a backslash before these characters to treat them literally. For example,
<code>_</code> will match any single character, but <code>\_</code> matches only an actual underscore.</p>
</li>
<li>
<p><code>\</code><br />
Because a backlash is used to remove the special meaning from other characters,
it too is treated specially. If you need to search for an actual backslash,
use <code>\\</code> instead of <code>\</code>.</p>
</li>
<li>
<p><code>(</code> and <code>)</code><br />
You can search for parentheses either by enclosing the full term in quotes,
and/or by using a backslash. That is, <code>&quot;some(text)&quot;</code>, <code>some\(text\)</code> and
<code>&quot;some\(text\)&quot;</code> are all equivalent, but <code>some(text)</code> is not.</p>
</li>
<li>
<p><code>-</code><br />
Starting a search term with <code>-</code> usually inverts it: <code>-dog</code> matches everything
except dog for example. If you instead wish to include an actual hyphen,
you can either use a backslash, or include the text in quotes, such as
<code>\-.-</code> or <code>&quot;-.-&quot;</code>.</p>
</li>
<li>
<p><code>:</code><br />
Colons have to be escaped unless they are preceded by another, unescaped colon.
So <code>w:e:b</code> is a word boundary search for <code>e:b</code>, <code>w\:e\:b</code> searches literally for
<code>w:e:b</code> and <code>w\:e:b</code> searches the field <code>w:e</code> for <code>b</code> (see
<a href="#limiting-to-a-field">field searches</a>).</p>
</li>
</ul>
<h3 id="raw-input"><a class="header" href="#raw-input">Raw input</a></h3>
<p>Text preceded by certain keywords (like <code>re:</code>) will be treated as raw input. That is,
the charcters listed above largely lose their special meaning. In such a context, only
a minimum of escaping is required to prevent ambiguity:</p>
<ul>
<li>
<p><code>&quot;</code> must be escaped.</p>
</li>
<li>
<p>Spaces and unescaped parentheses require the search term to be quoted.</p>
</li>
<li>
<p>The search term must not end in an odd number of backslashes.</p>
</li>
</ul>
<h2 id="object-ids"><a class="header" href="#object-ids">Object IDs</a></h2>
<p><code>nid:123</code><br />
all cards of the note with note id 123</p>
<p><code>cid:123</code><br />
the card with card id 123</p>
<p>Note and card IDs can be found in the <a href="stats.html">card info</a> dialog in the
browser. These searches may also be helpful when doing add-on
development or otherwise working closely with the database.</p>
<p>Object IDs will not work in the mobile clients, and are not intended to
be used in filtered decks at the moment.</p>
"""