# Milestone-3

## Technical brief: the `SoupReplacer` API, Milestone 2 vs. Milestone 3

**To:** the Beautiful Soup team
**Re:** whether to extend Beautiful Soup with parse-time tag replacement, and in what shape

### Recommendation

Adopt the **transformer interface** from Milestone 3 as the core of the feature, and keep the Milestone 2 pair `SoupReplacer("b", "blockquote")` only as a convenience shorthand. Ship it with three clearly documented rules:

1. transformers run at start-tag time, so the tag has no children yet;
2. end tags are matched by the tag's name in the source markup, not its new name;
3. the tree's structure (which tags are void, where tags close) follows the source markup.

Before calling it stable, add an end-of-tag hook for content-aware transforms, and decide how several replacers compose. Both are discussed under "Open questions" below.

### The two APIs

| | Milestone 2: replacement pair | Milestone 3: transformers |
|---|---|---|
| Constructor | `SoupReplacer(og_tag, alt_tag)` | `SoupReplacer(name_xformer=None, attrs_xformer=None, xformer=None)` |
| What it can change | One tag name, matched exactly | Any tag's name, its attributes, or anything else about the tag (`xformer` side effects) |
| How a rule is expressed | Data: two strings | Code: functions that take the `Tag` |
| Decisions per tag | One fixed mapping | Arbitrary: can depend on the name, the attributes, `sourceline`, parent, or outside state |
| Validation | Fully checkable at construction | Callability checked at construction; return values checked at parse time |
| Readability, simple case | Best: `SoupReplacer("b", "blockquote")` | Wordier: `name_xformer=lambda t: "blockquote" if t.name == "b" else t.name` |
| Failure modes | Practically none | A user function can raise, return the wrong type, or mutate the tree in unsafe ways |

**Why the transformer interface should be the core.** The pair interface is a single special case of `name_xformer`. Every rule it can express, the transformer interface can express too, but not the other way around. Milestone 1's Task 7 (set every `<p>`'s class) shows this: Milestone 2 cannot do it at all, while Milestone 3 does it with one `attrs_xformer` (`apps/m3/task7_soup_replacer.py`).

The transformer design also matches what Beautiful Soup users already know. Like `find_all()` and `SoupStrainer`, it accepts a function that takes a tag.

**Why the pair interface is still worth keeping.** It is the most common case, it reads well, and it cannot fail at parse time. In our implementation it is a thin layer over the same `transform()` code path, so keeping it costs almost nothing.

We do **not** allow mixing the two forms in one instance (it raises `ValueError`). The precedence between a pair and a `name_xformer` would be a guess, and anyone who needs both can write the pair as a `name_xformer`.

### Implementation summary

| Change | Location |
|---|---|
| `SoupReplacer` with both constructor forms, argument validation, `transform()`, attribute normalization | `bs4/filter.py`, class at **318**; `replace_tag_name()` **413**; `transform()` **423**; `_normalize_attrs()` **460** |
| `replacer=` constructor argument; warning when combined with html5lib | `bs4/__init__.py`, **220**, **445** |
| Start-tag hook: create the tag, transform it, then apply `parse_only` and add it to the tree | `bs4/__init__.py`, `handle_starttag()` **1004** → `_handle_starttag_with_replacer()` **1081** |
| End-tag matching by source name | `bs4/__init__.py`, `handle_endtag()` **1141** → `_popToSourceTag()` **1156**; bookkeeping reset at **696** |
| Tests | `bs4/tests/test_replacer.py` (2 from Milestone 2, 6 new from **64**) |
| Application (Milestone 1 Task 7) | `apps/m3/task7_soup_replacer.py` |

When no replacer is passed, `handle_starttag()` and `handle_endtag()` run exactly the original code. The default parse path is unchanged.

### Design decisions and their trade-offs

**1. Transformers run at the start tag.** This is the only point where renaming is still cheap, because the tag has not entered the tree. The cost is that the tag is empty: `tag.contents` is `[]` and `tag.get_text()` returns `""`.

Users will try to write "rename `<div>`s that contain a table" and be surprised. This needs to be in the documentation (`test_xformer_side_effects_from_assignment_example` asserts it). For the same reason, `xformer` must not detach the tag or insert siblings. The parser still owns the tree at that moment.

**2. End tags are matched by source name.** This was the main correctness problem. In Milestone 2 the name was replaced *before* the `Tag` was created, so the end tag `</b>` could be renamed the same way and still match.

A `name_xformer` needs the `Tag` object, so the tag must exist first, and the parser keeps reporting `</b>`. Matching that against the open tag's new name (`blockquote`) finds nothing, so the renamed tag never closes and swallows the rest of the document.

We record each tag's source name when it is opened and close the most recent open tag with that source name (`_popToSourceTag`). Disabling this makes 3 tests fail, including the end-tag test on both html.parser and lxml.

Both versions now use the same code path, so the Milestone 2 pair mode also creates the tag under its source name and renames it right after.

**3. Structure follows the source markup.** Whether a tag is void (like `<br>`) is decided from its source name. Renaming `<br>` to `<hr>` produces a void `<hr/>`. Renaming `<span>` to `br` produces a `<br>` that still contains the span's children.

This is deliberate. The markup's closing tags describe the structure, and redefining it mid-parse would move content around unpredictably. It should be documented as part of the contract.

**4. `parse_only` sees the transformed tag.** This matches Milestone 2, where the strainer saw the replaced name. The consequence is that transformers also run on tags the strainer will then discard, so their side effects happen for those tags too.

**5. Order is name, then attributes, then side effects.** `attrs_xformer` and `xformer` see the new name (`test_transformers_combine_in_documented_order`).

**6. Returned attributes are normalized like parsed ones.** If `attrs_xformer` returns `{"class": "test highlighted"}`, the stored value becomes `["test", "highlighted"]` under HTML parsers. Otherwise a transformed tag would behave differently from one parsed from the same markup.

**7. Wrong return types fail loudly.** A `name_xformer` that returns `None`, or an `attrs_xformer` that returns a list, raises `TypeError` naming the transformer and the tag. Silently keeping the old value would hide bugs.

**8. html5lib is not supported.** html5lib builds its own tree and never calls `handle_starttag()`. The replacer would be ignored silently, so the constructor now warns. Milestone 2 had the same limitation without the warning.

### Open questions for the team

- **An end-of-tag hook.** A transformer called when the tag *closes* (for example `on_close=`) could see the tag's full contents, which covers the "rename divs that contain a table" case. It could not safely rename, though, since by then children may refer to the tag's position. Two hooks with different powers is the honest design.
- **Composing replacers.** Today `replacer=` takes one instance. Accepting a list, applied in order, would let teams reuse small replacers. The ordering rules must be specified first.
- **Performance.** Moving the work into parsing avoids a second pass over the tree, but it adds a Python function call for *every* tag, not just matching ones. On a generated 1.6 MB file, parse plus transform took about the same time as parse plus Milestone 1's `find_all("p")` loop. Run-to-run noise was larger than any difference. We should not advertise this as a speed feature; its value is expressiveness and a single pass.

## Running

From the repository root, after `pip install -e .` and `pip install pytest` (see the top-level README):

```bash
pytest bs4/tests/test_replacer.py          # the 2 Milestone 2 tests and the 6 Milestone 3 tests
python apps/m3/task7_soup_replacer.py path/to/input.html
python apps/m3/task7_soup_replacer.py path/to/input.xml          # uses the xml parser
python apps/m3/task7_soup_replacer.py input.html --parser lxml -o out.html
```

The program writes `<input-stem>_task7.<suffix>` next to the input unless `-o` is given. It prints how many `<p>` tags were found and how many now have `class="test"`.

The full suite (`pytest bs4/tests`) passes apart from 4 tests that also fail on the unmodified course archive in our environment (Python 3.13, lxml 6.1): `test_htmlparser.py::test_rejected_input` and three in `test_lxml.py`. They come from parser-version differences, not from this change. Under the course's Python 3.10 they may pass.
