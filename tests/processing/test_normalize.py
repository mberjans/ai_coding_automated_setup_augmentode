from src.processing import normalize as norm


def test_newline_policy_and_trimming():
    raw = "Line 1\r\nLine 2\r\n\n  Line 3  \n\t\n"
    s = norm.normalize_newlines(raw)
    s = norm.trim_trailing_spaces_per_line(s)
    s = norm.strip_outer_blank_lines(s)
    assert s == "Line 1\nLine 2\n  Line 3"


def test_safe_filename_sanitation():
    bad = "A:/\\*?\"<>| name\t"
    good = norm.safe_filename(bad)
    # only allow alnum, space, dot, dash, underscore; others replaced with underscore
    assert good == "A__________ name_"


def test_header_footer_stripping_simple():
    text = "CONFIDENTIAL HEADER\nActual content line\nAnother line\nPage 1"
    out = norm.strip_simple_headers_footers(text, header_prefixes=["CONFIDENTIAL"], footer_prefixes=["Page "])
    assert out == "Actual content line\nAnother line"
