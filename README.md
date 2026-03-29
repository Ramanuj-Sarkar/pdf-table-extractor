# pdf-table-extractor

![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)

A fast, zero-config CLI tool to extract tables from PDF files and export them as **CSV**, **Excel**, or **JSON**.

Built for real-world documents — including pharmaceutical Batch Manufacturing Records (BMRs), lab reports, financial statements, and regulatory filings.

---
<!--
## Features

- 📄 Extracts all tables across all pages (or a subset of pages)
- 📊 Export as **CSV** (one file per table), **Excel** (one sheet per table), or **JSON** (with metadata)
- 🔍 `--preview` mode to inspect tables directly in the terminal (via `rich`)
- 🧹 Cleans up `None` values, empty rows, and duplicate column names automatically
- ⚙️ Installable as a CLI command (`pdf-extract`)
- 🧪 Full unit test suite with `pytest`

---

## Installation

```bash
git clone https://github.com/Ramanuj-Sarkar/pdf-table-extractor.git
cd pdf-table-extractor
pip install -e .
```

Or install dependencies directly:

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
# Extract all tables → CSV (default)
pdf-extract report.pdf

# Export as a single Excel workbook (one sheet per table)
pdf-extract report.pdf --format excel --output-dir ./results

# Extract only pages 1 and 3, export as JSON
pdf-extract report.pdf --pages 1,3 --format json

# Preview tables in the terminal (first 5 rows each)
pdf-extract report.pdf --preview

# Preview with more rows
pdf-extract report.pdf --preview --preview-rows 10

# Skip tables with fewer than 3 data rows
pdf-extract report.pdf --min-rows 3
```

---

## Options

| Option | Short | Default | Description |
|---|---|---|---|
| `--format` | `-f` | `csv` | Output format: `csv`, `excel`, `json` |
| `--output-dir` | `-o` | `./output` | Directory to write files |
| `--pages` | `-p` | all | Comma-separated page numbers, e.g. `1,3,5` |
| `--prefix` | | `table` | Filename prefix for output files |
| `--min-rows` | | `1` | Minimum data rows to include a table |
| `--preview` | | off | Print first N rows of each table to terminal |
| `--preview-rows` | | `5` | Rows shown in preview |
| `--version` | | | Show version and exit |

---

## Output Structure

### CSV mode
```
output/
├── table_page001_table1.csv
├── table_page001_table2.csv
└── table_page003_table1.csv
```

### Excel mode
```
output/
└── table_all_tables.xlsx   # each table on a separate sheet
```

### JSON mode (with metadata)
```json
{
  "meta": {
    "page": 1,
    "table_index": 1,
    "row_count": 12,
    "col_count": 5
  },
  "data": [
    { "Ingredient": "Microcrystalline Cellulose", "Quantity": "200mg", "Lot": "L-2024-01" },
    ...
  ]
}
```

---

## Python API

You can also use this as a library:

```python
from pdf_table_extractor import extract_tables_from_pdf, export_tables

tables = extract_tables_from_pdf("report.pdf", page_filter=[1, 3])

for t in tables:
    print(f"Page {t['page']} — {t['row_count']} rows × {t['col_count']} cols")
    print(t["df"].head())

export_tables(tables, output_dir="./output", fmt="excel")
```

---

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## Use Cases

- **Pharmaceutical BMRs** — extract raw material tables, equipment logs, QC results
- **Lab reports** — pull assay results and calibration data
- **Financial filings** — grab income statement and balance sheet tables from PDF reports
- **Regulatory documents** — extract structured data from FDA/EMA submissions

---

## Limitations

- Works best on **digitally generated PDFs** (not scanned images). For scanned PDFs, consider combining with an OCR step (e.g. `pytesseract` or Azure Document Intelligence).
- Complex merged-cell layouts may require manual post-processing.

---
-->
## License

MIT
