"""Tests for the SoupReplacer API added for Milestone 2."""

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
