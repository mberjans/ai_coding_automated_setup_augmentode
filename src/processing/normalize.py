# Normalization helpers (functional style)
# No regex, no OOP, no list comprehensions

from typing import AnyStr


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
