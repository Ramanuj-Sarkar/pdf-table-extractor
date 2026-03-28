"""
exporter.py — Export extracted tables to CSV, Excel, or JSON.
"""

import os
import json
import pandas as pd
from pathlib import Path


SUPPORTED_FORMATS = ("csv", "excel", "json")


def export_tables(
    tables: list[dict],
    output_dir: str,
    fmt: str,
    prefix: str = "table",
) -> list[str]:
    """
    Export a list of extracted table dicts to files.

    Args:
        tables:     Output from extract_tables_from_pdf().
        output_dir: Directory to write files into (created if absent).
        fmt:        One of 'csv', 'excel', 'json'.
        prefix:     Filename prefix (default: 'table').

    Returns:
        List of written file paths.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []

    if fmt == "excel":
        out_path = output_dir / f"{prefix}_all_tables.xlsx"
        with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
            for t in tables:
                sheet_name = f"P{t['page']}_T{t['table_index']}"
                # Excel sheet names max 31 chars
                sheet_name = sheet_name[:31]
                t["df"].to_excel(writer, sheet_name=sheet_name, index=False)
        written.append(str(out_path))

    else:
        for t in tables:
            name = f"{prefix}_page{t['page']:03d}_table{t['table_index']}"
            if fmt == "csv":
                out_path = output_dir / f"{name}.csv"
                t["df"].to_csv(out_path, index=False)
            elif fmt == "json":
                out_path = output_dir / f"{name}.json"
                payload = {
                    "meta": {
                        "page": t["page"],
                        "table_index": t["table_index"],
                        "row_count": t["row_count"],
                        "col_count": t["col_count"],
                    },
                    "data": t["df"].to_dict(orient="records"),
                }
                out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
            written.append(str(out_path))

    return written
