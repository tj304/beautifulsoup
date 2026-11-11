"""Tests for the SoupReplacer API (Milestone 2 pair, Milestone 3 transformers)."""

from bs4 import BeautifulSoup, SoupReplacer


def test_replaces_all_matching_tags_during_parsing():
    markup = (
        "<p>before <b class='emphasis'>bold <i>nested</i></b> after</p>"
        "<b id='second'>second</b>"
    )

    soup = BeautifulSoup(
        markup, "html.parser", replacer=SoupReplacer("b", "blockquote")
    )

    replacements = soup.find_all("blockquote")
    assert len(replacements) == 2
    assert soup.find_all("b") == []
    assert replacements[0].get("class") == ["emphasis"]
    assert replacements[0].find("i").get_text() == "nested"
    assert replacements[1].get("id") == "second"
    assert soup.get_text(" ", strip=True) == "before bold nested after second"


def test_non_matching_tags_and_default_behavior_are_unchanged():
    markup = "<p><b>bold</b><i>italic</i><strong>strong</strong></p>"
    soup = BeautifulSoup(
        markup, "html.parser", replacer=SoupReplacer("b", "blockquote")
    )

    assert soup.p.blockquote.get_text() == "bold"
    assert soup.p.i.get_text() == "italic"
    assert soup.p.strong.get_text() == "strong"
    assert soup.find_all("b") == []

    # Omitting the optional argument preserves Beautiful Soup's old behavior.
    unchanged = BeautifulSoup(markup, "html.parser")
    assert unchanged.p.b.get_text() == "bold"
    assert unchanged.find_all("blockquote") == []


# ---------------------------------------------------------------------------
# Milestone 3: transformer-based SoupReplacer API
# ---------------------------------------------------------------------------

import pytest

from bs4.builder import builder_registry

PARSERS_WITH_REPLACER = ["html.parser"] + (
    ["lxml"] if builder_registry.lookup("lxml") is not None else []
)


def b_to_blockquote(tag):
    return "blockquote" if tag.name == "b" else tag.name


def remove_class_attr(tag):
    if "class" in tag.attrs:
        del tag.attrs["class"]


def test_name_xformer_renames_tags_during_parsing():
    markup = (
        "<p>before <b class='emphasis'>bold <i>nested</i></b> after</p>"
        "<b id='second'>second</b>"
    )
    soup = BeautifulSoup(
        markup, "html.parser", replacer=SoupReplacer(name_xformer=b_to_blockquote)
    )

    replacements = soup.find_all("blockquote")
    assert len(replacements) == 2
    assert soup.find_all("b") == []
    assert replacements[0].get("class") == ["emphasis"]
    assert replacements[0].i.get_text() == "nested"
    assert replacements[1].get("id") == "second"
    # Tags the function leaves alone keep their names.
    assert [t.name for t in soup.find_all(True)] == [
        "p", "blockquote", "i", "blockquote",
    ]


def test_attrs_xformer_replaces_attributes_like_the_parser_would():
    def p_class_to_test(tag):
        if tag.name != "p":
            return tag.attrs
        new_attrs = dict(tag.attrs)
        new_attrs["class"] = "test highlighted"
        new_attrs.pop("style", None)
        return new_attrs

    markup = "<p class='old' style='x' id='a'>one</p><div class='keep'>two</div>"
    soup = BeautifulSoup(
        markup, "html.parser", replacer=SoupReplacer(attrs_xformer=p_class_to_test)
    )

    # "class" is turned into a list, exactly as for a normally parsed tag.
    assert soup.p["class"] == ["test", "highlighted"]
    assert soup.p.get("style") is None
    assert soup.p["id"] == "a"
    assert soup.div["class"] == ["keep"]
    assert str(soup.p) == '<p class="test highlighted" id="a">one</p>'


def test_xformer_side_effects_from_assignment_example():
    markup = (
        "<div class='a'><p class='b' id='keep'>text</p>"
        "<span class='c'>more</span></div>"
    )
    seen = []

    def record_and_remove(tag):
        seen.append(tag.name)
        # At start-tag time the tag has no children yet.
        assert tag.contents == []
        remove_class_attr(tag)

    soup = BeautifulSoup(
        markup, "html.parser", replacer=SoupReplacer(xformer=record_and_remove)
    )

    assert soup.find_all(class_=True) == []
    assert soup.p["id"] == "keep"
    assert soup.span.get_text() == "more"
    assert seen == ["div", "p", "span"]


def test_transformers_combine_in_documented_order():
    calls = []

    def name_x(tag):
        calls.append(("name", tag.name))
        return "section" if tag.name == "div" else tag.name

    def attrs_x(tag):
        calls.append(("attrs", tag.name))
        attrs = dict(tag.attrs)
        if tag.name == "section":
            attrs["data-was"] = "div"
        return attrs

    def x(tag):
        calls.append(("x", tag.name))
        remove_class_attr(tag)

    replacer = SoupReplacer(name_xformer=name_x, attrs_xformer=attrs_x, xformer=x)
    soup = BeautifulSoup(
        "<div class='box'>hi</div>", "html.parser", replacer=replacer
    )

    assert str(soup) == '<section data-was="div">hi</section>'
    # attrs_xformer and xformer already see the new name.
    assert calls == [("name", "div"), ("attrs", "section"), ("x", "section")]


@pytest.mark.parametrize("parser", PARSERS_WITH_REPLACER)
def test_renamed_tags_still_close_at_their_own_end_tags(parser):
    # The parser reports </b> by its source name, but the open tag is now
    # called <blockquote>. Matching end tags by the current name would find
    # no open <b>, so the renamed tag would never close and would swallow
    # the rest of the document. Real <blockquote> tags must be unaffected.
    markup = (
        "<div><b>outer <blockquote>real</blockquote> "
        "<b>inner</b> tail</b><p>after</p><br>end</div>"
    )
    soup = BeautifulSoup(
        markup, parser, replacer=SoupReplacer(name_xformer=b_to_blockquote)
    )

    outer = soup.div.blockquote
    assert [c.name for c in outer.find_all(True, recursive=False)] == [
        "blockquote", "blockquote",
    ]
    assert outer.get_text() == "outer real inner tail"
    # Siblings after the renamed tag are not swallowed by it.
    assert outer.find_next_sibling("p").get_text() == "after"
    # Void elements keep working.
    assert soup.div.br.contents == []
    assert soup.div.get_text() == "outer real inner tailafterend"


def test_invalid_replacer_configurations_are_rejected():
    with pytest.raises(ValueError):
        SoupReplacer()
    with pytest.raises(ValueError):
        SoupReplacer("b", "blockquote", xformer=remove_class_attr)
    with pytest.raises(TypeError):
        SoupReplacer(name_xformer="blockquote")
    with pytest.raises(TypeError):
        SoupReplacer("b")

    with pytest.raises(TypeError, match="name_xformer"):
        BeautifulSoup(
            "<b>x</b>",
            "html.parser",
            replacer=SoupReplacer(name_xformer=lambda tag: None),
        )
    with pytest.raises(TypeError, match="attrs_xformer"):
        BeautifulSoup(
            "<b>x</b>",
            "html.parser",
            replacer=SoupReplacer(attrs_xformer=lambda tag: ["class"]),
        )

    # The Milestone 2 constructor keeps working alongside the new one.
    assert repr(SoupReplacer("b", "blockquote")) == "<SoupReplacer 'b' -> 'blockquote'>"
