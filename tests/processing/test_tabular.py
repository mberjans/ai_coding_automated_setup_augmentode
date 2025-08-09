from pathlib import Path
import io
import csv
import tempfile


def _write_csv(path: Path, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        i = 0
        while i < len(rows):
            w.writerow(rows[i])
            i = i + 1


def _write_tsv(path: Path, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        i = 0
        while i < len(rows):
            w.writerow(rows[i])
            i = i + 1


def _write_xlsx(path: Path, sheets):
    # sheets: list of tuples (name, rows)
    from openpyxl import Workbook

    wb = Workbook()
    # Remove default sheet
    ws = wb.active
    wb.remove(ws)

    i = 0
    while i < len(sheets):
        name, rows = sheets[i]
        ws = wb.create_sheet(title=name)
        r = 0
        while r < len(rows):
            c = 0
            ws_row = []
            while c < len(rows[r]):
                ws_row.append(rows[r][c])
                c = c + 1
            ws.append(ws_row)
            r = r + 1
        i = i + 1
    wb.save(path)


# TICKET-008.01/008.02: Failing tests for xlsx export and csv/tsv normalization

def test_parse_csv_normalizes_to_tabs_and_counts(tmp_path: Path):
    from src.processing.parsers import tabular

    src = tmp_path / "data.csv"
    _write_csv(src, [["H1", "H2"], ["A", "B"], ["C", ""]])

    out = tabular.parse_csv(src, tmp_path)
    assert isinstance(out, dict)
    assert "out_path" in out and "text" in out and "rows" in out

    out_path = out["out_path"]
    assert str(out_path).endswith(str(Path("processed_documents") / "text" / "data.txt"))

    text = out["text"].splitlines()
    assert text[0] == "H1\tH2"
    assert text[1] == "A\tB"
    assert text[2] == "C\t"
    assert out["rows"] == 3


def test_parse_tsv_keeps_tabs_and_counts(tmp_path: Path):
    from src.processing.parsers import tabular

    src = tmp_path / "data.tsv"
    _write_tsv(src, [["H1", "H2"], ["A", "B"], ["C", "D"]])

    out = tabular.parse_tsv(src, tmp_path)
    text = out["text"].splitlines()
    assert text[0] == "H1\tH2"
    assert text[1] == "A\tB"
    assert out["rows"] == 3


def test_parse_xlsx_sheets_with_separators_and_counts(tmp_path: Path):
    from src.processing.parsers import tabular

    src = tmp_path / "book.xlsx"
    _write_xlsx(src, [
        ("Sheet1", [["H1", "H2"], ["A", "B"]]),
        ("Second", [["X"], ["Y"]])
    ])

    out = tabular.parse_xlsx(src, tmp_path)
    text = out["text"]
    assert "=== Sheet: Sheet1 ===" in text
    assert "=== Sheet: Second ===" in text
    lines = text.splitlines()
    assert "H1\tH2" in lines
    assert out["sheets"][0]["name"] == "Sheet1"
    assert out["sheets"][0]["rows"] == 2
    assert out["sheets"][1]["name"] == "Second"
    assert out["sheets"][1]["rows"] == 2
