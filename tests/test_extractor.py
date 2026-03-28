"""
tests/test_extractor.py — Unit tests for the pdf-table-extractor.

Run with: pytest tests/ -v
"""

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch

from pdf_table_extractor.extractor import extract_tables_from_pdf, clean_header
from pdf_table_extractor.exporter import export_tables


# ---------------------------------------------------------------------------
# _clean_header tests
# ---------------------------------------------------------------------------

def test_clean_header_basic():
    result = clean_header(["Name", "Age", "City"])
    assert result == ["Name", "Age", "City"]


def test_clean_header_none_values():
    result = clean_header([None, "Age", None])
    assert result[0] == "Unnamed"
    assert result[2] == "Unnamed_1"


def test_clean_header_duplicates():
    result = clean_header(["Col", "Col", "Col"])
    assert result == ["Col", "Col_1", "Col_2"]


# ---------------------------------------------------------------------------
# extract_tables_from_pdf tests (mocked pdfplumber)
# ---------------------------------------------------------------------------

def _make_mock_pdf(pages_tables: list[list]):
    """
    Build a mock pdfplumber PDF where each element of pages_tables
    is the list of raw tables on that page.
    """
    mock_pages = []
    for raw_tables in pages_tables:
        page = MagicMock()
        page.extract_tables.return_value = raw_tables
        mock_pages.append(page)

    mock_pdf = MagicMock()
    mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
    mock_pdf.__exit__ = MagicMock(return_value=False)
    mock_pdf.pages = mock_pages
    return mock_pdf


@patch("pdf_table_extractor.extractor.pdfplumber.open")
@patch("pdf_table_extractor.extractor.Path.exists", return_value=True)
def test_extract_single_table(mock_exists, mock_open):
    raw = [["Name", "Dose", "Lot"], ["ParaA", "500mg", "L001"], ["ParaB", "250mg", "L002"]]
    mock_open.return_value = _make_mock_pdf([[raw]])

    results = extract_tables_from_pdf("dummy.pdf")

    assert len(results) == 1
    assert results[0]["page"] == 1
    assert results[0]["row_count"] == 2
    assert list(results[0]["df"].columns) == ["Name", "Dose", "Lot"]


@patch("pdf_table_extractor.extractor.pdfplumber.open")
@patch("pdf_table_extractor.extractor.Path.exists", return_value=True)
def test_extract_multiple_pages(mock_exists, mock_open):
    t1 = [["A", "B"], ["1", "2"]]
    t2 = [["X", "Y"], ["3", "4"]]
    mock_open.return_value = _make_mock_pdf([[t1], [t2]])

    results = extract_tables_from_pdf("dummy.pdf")
    assert len(results) == 2
    assert results[0]["page"] == 1
    assert results[1]["page"] == 2


@patch("pdf_table_extractor.extractor.pdfplumber.open")
@patch("pdf_table_extractor.extractor.Path.exists", return_value=True)
def test_page_filter(mock_exists, mock_open):
    t1 = [["A", "B"], ["1", "2"]]
    t2 = [["X", "Y"], ["3", "4"]]
    mock_open.return_value = _make_mock_pdf([[t1], [t2]])

    results = extract_tables_from_pdf("dummy.pdf", page_filter=[2])
    assert len(results) == 1
    assert results[0]["page"] == 2


@patch("pdf_table_extractor.extractor.pdfplumber.open")
@patch("pdf_table_extractor.extractor.Path.exists", return_value=True)
def test_empty_tables_skipped(mock_exists, mock_open):
    mock_open.return_value = _make_mock_pdf([[[]]])
    results = extract_tables_from_pdf("dummy.pdf")
    assert results == []


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        extract_tables_from_pdf("/nonexistent/path/file.pdf")


# ---------------------------------------------------------------------------
# export_tables tests
# ---------------------------------------------------------------------------

def _make_tables():
    df = pd.DataFrame({"Name": ["Alice", "Bob"], "Score": ["90", "85"]})
    return [{"page": 1, "table_index": 1, "df": df, "row_count": 2, "col_count": 2}]


def test_export_csv(tmp_path):
    tables = _make_tables()
    written = export_tables(tables, str(tmp_path), "csv")
    assert len(written) == 1
    assert written[0].endswith(".csv")
    result = pd.read_csv(written[0])
    assert list(result.columns) == ["Name", "Score"]


def test_export_excel(tmp_path):
    tables = _make_tables()
    written = export_tables(tables, str(tmp_path), "excel")
    assert len(written) == 1
    assert written[0].endswith(".xlsx")
    xl = pd.read_excel(written[0], sheet_name=None)
    assert len(xl) == 1


def test_export_json(tmp_path):
    import json
    tables = _make_tables()
    written = export_tables(tables, str(tmp_path), "json")
    assert len(written) == 1
    payload = json.loads(open(written[0]).read())
    assert "meta" in payload
    assert "data" in payload
    assert payload["meta"]["page"] == 1


def test_export_invalid_format(tmp_path):
    with pytest.raises(ValueError, match="Unsupported format"):
        export_tables(_make_tables(), str(tmp_path), "xml")
