from investor_db.fetch import html_to_text, is_blocked


def test_html_to_text_drops_scripts_and_keeps_visible_text() -> None:
    html = "<html><script>var x = 'hidden';</script><p>Seed <b>fund</b></p></html>"
    text = html_to_text(html)
    assert "hidden" not in text
    assert "Seed" in text and "fund" in text


def test_linkedin_is_blocked_on_any_subdomain() -> None:
    assert is_blocked("https://cz.linkedin.com/company/x")
    assert not is_blocked("https://credoventures.com")
