# Normalization helpers (functional style)
# No regex, no OOP, no list comprehensions

from typing import AnyStr, List, Optional


def utf8_decode_remove_bom(data: bytes) -> str:
    # Remove UTF-8 BOM if present
    if len(data) >= 3:
        if data[0] == 0xEF and data[1] == 0xBB and data[2] == 0xBF:
            data = data[3:]
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(f"Invalid UTF-8: {e}")


def normalize_newlines(text: str) -> str:
    # Convert CRLF and CR to LF
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    # Ensure trailing newline
    if not text.endswith("\n"):
        text = text + "\n"
    return text


def remove_control_chars(text: str) -> str:
    # Remove ASCII control characters except newline and tab
    # Keep chars with code >= 32, plus \n and \t
    out = []
    i = 0
    while i < len(text):
        ch = text[i]
        code = ord(ch)
        if code >= 32 or ch == "\n" or ch == "\t":
            out.append(ch)
        i = i + 1
    return "".join(out)


def join_columns_to_tabs(columns: List[Optional[str]]) -> str:
    """Join columns into a tab-delimited line.

    Avoids list comprehensions and handles None as empty string.
    """
    out = ""
    i = 0
    while i < len(columns):
        if i > 0:
            out = out + "\t"
        val = columns[i]
        if val is None:
            val = ""
        out = out + str(val)
        i = i + 1
    return out


def trim_trailing_spaces_per_line(text: str) -> str:
    """Remove trailing spaces and tabs from each line."""
    lines = text.split("\n")
    out_lines: List[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # trim only spaces and tabs from end
        j = len(line) - 1
        while j >= 0 and (line[j] == " " or line[j] == "\t"):
            j = j - 1
        out_lines.append(line[: j + 1])
        i = i + 1
    return "\n".join(out_lines)


def strip_outer_blank_lines(text: str) -> str:
    """Remove leading and trailing blank lines (ignoring spaces/tabs)."""
    lines = text.split("\n")
    start = 0
    end = len(lines) - 1

    # find first non-blank
    while start <= end:
        s = lines[start]
        # check if blank (spaces/tabs only)
        k = 0
        all_blank = True
        while k < len(s):
            ch = s[k]
            if ch != " " and ch != "\t":
                all_blank = False
                break
            k = k + 1
        if all_blank:
            start = start + 1
        else:
            break

    # find last non-blank
    while end >= start:
        s = lines[end]
        k = 0
        all_blank = True
        while k < len(s):
            ch = s[k]
            if ch != " " and ch != "\t":
                all_blank = False
                break
            k = k + 1
        if all_blank:
            end = end - 1
        else:
            break

    kept: List[str] = []
    idx = start
    while idx <= end:
        # Skip entirely blank lines (spaces/tabs only)
        s = lines[idx]
        k = 0
        all_blank = True
        while k < len(s):
            ch = s[k]
            if ch != " " and ch != "\t":
                all_blank = False
                break
            k = k + 1
        if not all_blank:
            kept.append(s)
        idx = idx + 1
    return "\n".join(kept)


def safe_filename(name: str) -> str:
    """Sanitize filename by replacing disallowed characters with underscore.

    Allowed: A-Z a-z 0-9 space dot dash underscore
    Others become underscores. No path separators or control chars.
    """
    out_chars: List[str] = []
    i = 0
    while i < len(name):
        ch = name[i]
        is_alnum = ("0" <= ch <= "9") or ("A" <= ch <= "Z") or ("a" <= ch <= "z")
        if is_alnum or ch == " " or ch == "." or ch == "-" or ch == "_":
            out_chars.append(ch)
        else:
            # Special-case colon to map to two underscores to avoid drive letters or schemes
            if ch == ":":
                out_chars.append("_")
                out_chars.append("_")
            else:
                out_chars.append("_")
        i = i + 1
    return "".join(out_chars)


def _startswith_any(s: str, prefixes: List[str]) -> bool:
    i = 0
    while i < len(prefixes):
        pref = prefixes[i]
        # explicit startswith without regex
        matched = True
        if len(pref) > len(s):
            matched = False
        else:
            j = 0
            while j < len(pref):
                if s[j] != pref[j]:
                    matched = False
                    break
                j = j + 1
        if matched:
            return True
        i = i + 1
    return False


def strip_simple_headers_footers(text: str, header_prefixes: List[str], footer_prefixes: List[str]) -> str:
    """Strip a simple header line (prefix match) and footer line (prefix match).

    Only removes at most one header (first line) and one footer (last line).
    """
    lines = text.split("\n")
    if len(lines) == 0:
        return text

    start = 0
    end = len(lines) - 1

    if len(lines) > 0 and _startswith_any(lines[0], header_prefixes):
        start = 1
    if end >= start and _startswith_any(lines[end], footer_prefixes):
        end = end - 1

    kept: List[str] = []
    i = start
    while i <= end:
        kept.append(lines[i])
        i = i + 1
    return "\n".join(kept)
