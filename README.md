# BeautifulSoup
Beautiful Soup is a library that makes it easy to scrape information
from web pages. It sits atop an HTML or XML parser, providing Pythonic
idioms for iterating, searching, and modifying the parse tree.

## Environment Setup and Installation

#### Download the repository from Canvas course page

```bash
~/> cd beautifulsoup
```
#### Create ```Conda``` environment and activate it inside ```~/beautifulsoup``` directory
```bash
# python=3.10 is required
:~/ cd beautifulsoup
beautifulsoup:~/ conda create -n bs4 python=3.10
beautifulsoup:~/ conda activate bs4
```

## OR

#### Create ```Venv``` environment and activate it inside ```~/beautifulsoup``` directory
```bash
# python=3.10 is required
:~/ cd beautifulsoup
beautifulsoup:~/ python3 -m venv venv
beautifulsoup:~/ source venv/bin/activate  # On macOS/Linux
```

#### Install all dependencies with pytest
```bash
beautifulsoup:~/ pip install -e .
beautifulsoup:~/ pip install pytest
```


#### Run Test
```bash
#  If you are using conda env
cd beautifulsoup
beautifulsoup:~/ pytest
```
```bash
# if you are using venv env
cd beautifulsoup/bs4/tests
beautifulsoup/bs4/tests:~/ pytest
```

## Github Repository Setup (GitHub CLI)
- Install [GitHub CLI](https://cli.github.com/) and configure it with your GitHub Account 
- Checkout this to learn [Adding locally hosted code to GitHub](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)
- The following approach is with [GitHub CLI](https://cli.github.com/)
```bash
:~/ cd beautifulsoup
beautifulsoup:~/ git init
beautifulsoup:~/ git add .
beautifulsoup:~/ git commit -m "Initialize Repository" 
beautifulsoup:~/ gh repo create beautifulsoup --source=. --public --push
```

## Github Repository Setup (GitHub Web)
- In your GitHub web account, create a repository named beautifulsoup. 
- It will generate a repository link: https://github.com/YOUR-USERNAME/beautiful.git
- Now open a terminal inside the downloaded ```beautifulsoup``` folder and steup the repository
- *** Replace ```YOUR-USERNAME``` with your GitHub username.

```bash
:~/ cd beautifulsoup
beautifulsoup:~/ git init
beautifulsoup:~/ git commit -m "repository initialization"
beautifulsoup:~/ git branch -M main
beautifulsoup:~/ git remote add origin https://github.com/YOUR-USERNAME/beautiful.git
beautifulsoup:~/ git push -u origin main
```



# Quick start

```
>>> from bs4 import BeautifulSoup
>>> soup = BeautifulSoup("<p>Some<b>bad<i>HTML")
>>> print(soup.prettify())
<html>
 <body>
  <p>
   Some
   <b>
    bad
    <i>
     HTML
    </i>
   </b>
  </p>
 </body>
</html>
>>> soup.find(string="bad")
'bad'
>>> soup.i
<i>HTML</i>
#
>>> soup = BeautifulSoup("<tag1>Some<tag2/>bad<tag3>XML", "xml")
#
>>> print(soup.prettify())
<?xml version="1.0" encoding="utf-8"?>
<tag1>
 Some
 <tag2/>
 bad
 <tag3>
  XML
 </tag3>
</tag1>
```

To go beyond the basics, [comprehensive documentation is available](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).

# Links

* [Homepage](https://www.crummy.com/software/BeautifulSoup/bs4/)
* [Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* [Discussion group](https://groups.google.com/group/beautifulsoup/)
* [Development](https://code.launchpad.net/beautifulsoup/)
* [Bug tracker](https://bugs.launchpad.net/beautifulsoup/)
* [Complete changelog](https://bazaar.launchpad.net/~leonardr/beautifulsoup/bs4/view/head:/CHANGELOG)


# Milestone 2 — Part 2: Beautiful Soup API Source Locations

## Source version used

These locations were checked against the original `beautifulsoup.zip` provided for the course, before making any source-code changes. The source identifies itself as Beautiful Soup **4.13.0** in `bs4/__init__.py`, line 18. Paths below are relative to the repository root (`beautifulsoup/`). The line numbers refer to that original course archive, not to a separately installed version of Beautiful Soup.

This mapping covers the Beautiful Soup APIs called by the Milestone 1 programs (`task1.py` through `task8.py`) and the APIs needed for the Milestone 2 Part 1 `SoupStrainer` programs. Python standard-library calls such as `argparse`, `pathlib.Path.open()`, and `Path.write_text()` are not Beautiful Soup APIs, so they are not listed here.

## APIs used in Milestone 1

| API used by the application | Original source file and line(s) | Purpose in the application |
|---|---|---|
| `BeautifulSoup(...)` / `BeautifulSoup.__init__()` | `bs4/__init__.py`, class definition at **133**, constructor signature at **209–219** | Builds the document tree from an HTML/XML string or file-like object. The `features` argument selects the parser. |
| `prettify()` | `bs4/element.py`, **2601–2617** | Serializes the parsed tree with indentation and line breaks. Used by Task 1 and by Tasks 6–7 to write the modified tree. |
| `find_all()` | `bs4/element.py`, **2715–2745** | Searches descendants and returns all matching elements. Used to find anchors, all tags, tags with an `id`, bold tags, and paragraph tags. |
| `find_parent()` | `bs4/element.py`, **992–1018** | Finds the closest ancestor matching the requested tag name or names. Used by Task 5 to locate the nearest meaningful container for a link. |
| `get_text()` | `bs4/element.py`, **524–550** | Collects text from a tag's descendants; the `separator` and `strip` arguments control joining and whitespace cleanup. Used by Tasks 2 and 5 to display link text, and Task 8 to display heading text. |
| `get()` | `bs4/element.py`, **2160–2171** | Gets an attribute value and optionally returns a default if the attribute is missing. Used to read `href`, `id`, and `class` values safely. |
| `select()` | Public `Tag.select()` wrapper: `bs4/element.py`, **2799–2822**; CSS-selector implementation it delegates to: `bs4/css.py`, **161–196** | Selects elements using CSS selectors. Used by Task 8 with `h1, h2, h3, h4, h5, h6`. |
| `Tag.__setitem__()` (used by `tag["class"] = ...`) | `bs4/element.py`, **2223–2226** | Implements setting a tag attribute through item assignment. Used by Task 7 to set the `class` attribute to `test`. |
| `Tag.__repr__()` / `Tag.__str__` | `bs4/element.py`, **2298–2302** | Renders a tag as markup when a tag is printed. This is invoked implicitly by calls such as `print(tag)`; it is not usually called explicitly in the task code. |

### How these map to the Milestone 1 tasks

| Milestone 1 task | Beautiful Soup API calls |
|---|---|
| Task 1 — pretty-print the document | `BeautifulSoup(...)`, `prettify()` |
| Task 2 — print all `<a>` tags | `BeautifulSoup(...)`, `find_all("a")`, `get("href", default)`, `get_text(" ", strip=True)`, implicit tag string conversion when printing a tag |
| Task 3 — print all tags | `BeautifulSoup(...)`, `find_all(True)`; reads the `name` and `attrs` properties of each `Tag` |
| Task 4 — print tags with an `id` attribute | `BeautifulSoup(...)`, `find_all(id=True)`; printing each tag invokes tag string conversion |
| Task 5 — use `find_parent()` meaningfully | `BeautifulSoup(...)`, `find_all("a")`, `find_parent(...)`, `get("href", default)`, `get("id", default)`, `get("class", default)`, `get_text(" ", strip=True)` |
| Task 6 — rename `<b>` to `<blockquote>` | `BeautifulSoup(...)`, `find_all("b")`, `prettify()`; `tag.name = "blockquote"` is a direct attribute assignment, not a separate API method call |
| Task 7 — set each `<p>` class to `test` | `BeautifulSoup(...)`, `find_all("p")`, `Tag.__setitem__()` via `paragraph["class"] = ["test"]`, `prettify()` |
| Task 8 — use one additional API | `BeautifulSoup(...)`, `select(...)`, `get_text(" ", strip=True)` |

The properties `Tag.name` and `Tag.attrs` are read directly in the application. Likewise, Task 6 assigns to `tag.name`. These are attribute access/assignment operations, not calls to standalone API functions, so they do not have a separate function-definition line to report. `Tag.__setitem__()` is listed because Python invokes it when Task 7 assigns an attribute using `tag["class"] = ...`.

## APIs used in Milestone 2 Part 1 (`SoupStrainer`)

The three Part 1 applications are located at `apps/m2/task2.py`, `apps/m2/task3.py`, and `apps/m2/task4.py`. Each accepts an input HTML/XML file as a command-line argument and uses the original course version of Beautiful Soup. Each script prints its parser name, input size, and parse time to standard error, while the requested tag results are printed to standard output.

### Exact API usage in the three Part 1 applications

| Application | `SoupStrainer` passed as `parse_only` | Search performed on the returned soup | What the program prints |
|---|---|---|---|
| `apps/m2/task2.py` | `SoupStrainer("a")` | `soup.find_all("a")` | Each `<a>` tag's attributes, its `href` value (or a missing-attribute message), and its visible text. |
| `apps/m2/task3.py` | `SoupStrainer()` | `soup.find_all(True)` | Every retained tag's name and attributes. |
| `apps/m2/task4.py` | `SoupStrainer(id=True)` | `soup.find_all(id=True)` | Every tag that itself has an `id` attribute, with its ID and attributes. |

The scripts also use `Tag.get()` and, in Task 2, `Tag.get_text()`. They use `tag.name` and `tag.attrs` as properties. The scripts use Python standard-library facilities (`argparse`, `pathlib`, `time`, and `sys`) for command-line arguments, file access, timing, and error output; those are not Beautiful Soup APIs and therefore do not have Beautiful Soup source locations.

### Original source locations for APIs used by Part 1

All line numbers below refer to the original, unmodified source files in the course `beautifulsoup.zip` (Beautiful Soup **4.13.0**). Paths are relative to the repository root.

| API / implementation point | Original source file and line(s) | How Part 1 uses it |
|---|---|---|
| `BeautifulSoup(...)` / `BeautifulSoup.__init__()` | `bs4/__init__.py`, class starts at **133**; constructor signature at **209–219** | Creates the parsed tree. The scripts supply the selected parser and `parse_only=` argument. |
| `parse_only` constructor handling | `bs4/__init__.py`, **323–331** (validation / warning logic) and **433–440** (stores `parse_only` and reads file-like markup) | Accepts the `SoupStrainer`, makes it available during parsing, and reads the supplied file object. |
| `SoupStrainer` class | `bs4/filter.py`, **313–343** | Represents parsing restrictions. |
| `SoupStrainer.__init__()` | `bs4/filter.py`, **345–396** | Builds rules for the tag name or attribute restriction: `SoupStrainer("a")`, `SoupStrainer()` and `SoupStrainer(id=True)`. |
| `BeautifulSoup.handle_starttag()` | `bs4/__init__.py`, **987–1026**, especially **1021–1026** | Checks whether a new tag can be created when `parse_only` is active. |
| `SoupStrainer.allow_tag_creation()` | `bs4/filter.py`, **580–619** | Evaluates a candidate tag's name and attributes against the strainer's rules. |
| `find_all()` | `bs4/element.py`, **2715–2745** | Task 2 uses `soup.find_all("a")`; Task 3 uses `soup.find_all(True)`; Task 4 uses `soup.find_all(id=True)`. |
| `get()` | `bs4/element.py`, **2160–2171** | Task 2 reads `href`; Task 4 reads `id`. A default is supplied where an attribute may be absent. |
| `get_text()` | `bs4/element.py`, **524–550** | Task 2 extracts readable anchor text with a separator and whitespace stripping. |
| `FeatureNotFound` exception | `bs4/exceptions.py`, **10–13** | The scripts catch this exception and give a useful error if a requested parser is unavailable. |

### Why Task 3 uses an unrestricted `SoupStrainer`

The assignment explicitly asks for an attempt to implement Task 3 with `SoupStrainer`, even though Task 3 must list all tags. The program therefore passes `SoupStrainer()` with no name or attribute restrictions. This keeps all tags, so there is no meaningful subset to skip and little or no expected performance or memory benefit. The program still exercises the requested API and prints the tags using `soup.find_all(True)`.

For Tasks 2 and 4, `SoupStrainer` defines a restriction, but it is important to understand how the API works in this source version: `BeautifulSoup.handle_starttag()` checks `allow_tag_creation()` when the current tag stack is at the document's top level (`bs4/__init__.py:1021–1026`). Once a matching top-level tag is accepted, its nested subtree may also be present. For that reason, Task 4 calls `soup.find_all(id=True)` after parsing so it prints only tags that themselves have an `id` attribute, rather than every descendant retained underneath a matching element.

### Run the Part 1 applications

From the root of the course repository, after installing the project as described above, run:

```bash
python apps/m2/task2.py /path/to/large.html
python apps/m2/task3.py /path/to/large.html
python apps/m2/task4.py /path/to/large.html
```

The scripts default to `html.parser` for non-XML filenames and to the `xml` parser for filenames ending in `.xml`. XML parsing in Beautiful Soup requires the optional `lxml` dependency; install it if needed:

```bash
python -m pip install lxml
```

You can override the inferred parser explicitly, for example `--parser html.parser` or `--parser xml`. Use a large HTML or XML input for all three programs, as required by the assignment. To prevent large result sets from flooding the terminal, redirect standard output to a file; timing information remains on standard error:

```bash
python apps/m2/task2.py /path/to/large.html > task2_output.txt
python apps/m2/task3.py /path/to/large.html > task3_output.txt
python apps/m2/task4.py /path/to/large.html > task4_output.txt
```

Record the input file size, parser, whether each run completed, parse time, and any errors on the machine used for the assignment. Runtime and memory usage depend on the machine, parser, and document structure, so the script's timing output should be used for the student's own experiment rather than treating one machine's measurements as universal.

**Validation run in the development environment:** all three scripts completed against a generated HTML file of **5,244,955 bytes** using `html.parser`. The file contained 72,846 repeated sections with an `<a>` tag, a `<p>` tag, and an `id` attribute on the enclosing `<div>`. One run reported the following approximate measurements:

| Application | Result count | Parse time reported by the script | Total wall time | Maximum resident memory reported by `/usr/bin/time` |
|---|---:|---:|---:|---:|
| `task2.py` | 72,846 hyperlinks | 5.336 s | 6.69 s | 201,596 KB |
| `task3.py` | 218,540 tags | 8.748 s | 10.44 s | 363,244 KB |
| `task4.py` | 72,846 tags with `id` | 8.695 s | 10.67 s | 329,200 KB |

These values are specific to that generated file and execution environment; rerun the programs on the large HTML or XML file you choose and report your own observations. The output was redirected to files for these measurements so the large number of printed tags would not flood the terminal.

The `html5lib` builder does not support `parse_only` in this source version; the warning is in `bs4/builder/_html5lib.py:121–124`. Use a compatible parser such as `html.parser` or an installed `lxml` parser for the `SoupStrainer` experiments.

## References

- Beautiful Soup documentation: <https://www.crummy.com/software/BeautifulSoup/bs4/doc/>
- `SoupStrainer` documentation and parsing only part of a document: <https://beautiful-soup-4.readthedocs.io/en/latest/#parsing-only-part-of-a-document>
