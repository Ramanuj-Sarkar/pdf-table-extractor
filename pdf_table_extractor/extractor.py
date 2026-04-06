"""
extractor.py — Core PDF table extraction logic using pdfplumber.
"""

import pdfplumber
import pandas as pd
from pathlib import Path


def extract_tables_from_pdf(
    pdf_path: str,
    page_filter: list[int] | None = None,
    min_rows: int = 1,
) -> list[dict]:
    """
    Extract all tables from a PDF file.

    Args:
        pdf_path:     Path to the PDF file.
        page_filter:  Optional list of 1-based page numbers to process.
        min_rows:     Minimum number of data rows for a table to be included.

    Returns:
        List of dicts with keys: page, table_index, df, row_count, col_count.
    """
    results = []
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)

        for page_num, page in enumerate(pdf.pages, start=1):
            if page_filter and page_num not in page_filter:
                continue

            tables = page.extract_tables()

            for i, table in enumerate(tables):
                if not table or len(table) < 2:
                    # Need at least a header row + one data row
                    continue

                header = table[0]
                rows = table[1:]

                # Skip tables that are mostly empty
                if len(rows) < min_rows:
                    continue

                # Handle duplicate or None column names
                header = clean_header(header)

                df = pd.DataFrame(rows, columns=header)
                df = df.fillna("").map(lambda x: str(x).strip() if x else "")

                # Drop fully-empty rows
                df = df[df.apply(lambda r: r.str.strip().any(), axis=1)].reset_index(drop=True)

                if len(df) < min_rows:
                    continue

                results.append({
                    "page": page_num,
                    "table_index": i + 1,
                    "df": df,
                    "row_count": len(df),
                    "col_count": len(df.columns),
                    "total_pages": total_pages,
                })

    return results


def clean_header(header: list) -> list[str]:
    """
    Normalise column names: fill None values, deduplicate.
    """
    seen = {}
    cleaned = []
    for col in header:
        col = str(col).strip() if col else "Unnamed"
        if col in seen:
            seen[col] += 1
            col = f"{col}_{seen[col]}"
        else:
            seen[col] = 0
        cleaned.append(col)
    return cleaned
