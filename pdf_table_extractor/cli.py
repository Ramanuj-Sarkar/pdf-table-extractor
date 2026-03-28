"""
cli.py — Command-line interface for pdf-table-extractor.
"""

import sys
import click

from pdf_table_extractor.extractor import extract_tables_from_pdf
from pdf_table_extractor.exporter import export_tables


def _rich_preview(tables: list[dict], max_rows: int = 5) -> None:
    """Print a rich table preview to the terminal."""
    try:
        from rich.console import Console
        from rich.table import Table as RichTable
        from rich import box

        console = Console()

        for t in tables:
            title = f"[bold cyan]Page {t['page']} — Table {t['table_index']}[/bold cyan]  " \
                    f"[dim]({t['row_count']} rows × {t['col_count']} cols)[/dim]"
            console.print(title)

            rt = RichTable(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold magenta")
            for col in t["df"].columns:
                rt.add_column(col, overflow="fold", max_width=30)

            preview_df = t["df"].head(max_rows)
            for _, row in preview_df.iterrows():
                rt.add_row(*[str(v) for v in row])

            console.print(rt)

            if t["row_count"] > max_rows:
                console.print(f"  [dim]... {t['row_count'] - max_rows} more rows[/dim]\n")

    except ImportError:
        # Fallback: plain text
        for t in tables:
            click.echo(f"\n--- Page {t['page']} | Table {t['table_index']} "
                       f"({t['row_count']} rows × {t['col_count']} cols) ---")
            click.echo(t["df"].head(max_rows).to_string(index=False))


@click.command()
@click.argument("pdf_path", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--format", "-f", "fmt",
    default="csv",
    type=click.Choice(["csv", "excel", "json"], case_sensitive=False),
    show_default=True,
    help="Output file format.",
)
@click.option(
    "--output-dir", "-o",
    default="./output",
    show_default=True,
    help="Directory to save extracted tables.",
)
@click.option(
    "--pages", "-p",
    default=None,
    help="Comma-separated 1-based page numbers to process (e.g. '1,3,5').",
)
@click.option(
    "--prefix",
    default="table",
    show_default=True,
    help="Filename prefix for output files.",
)
@click.option(
    "--min-rows",
    default=1,
    show_default=True,
    help="Minimum data rows required to include a table.",
)
@click.option(
    "--preview/--no-preview",
    default=False,
    help="Print first 5 rows of each table to the terminal.",
)
@click.option(
    "--preview-rows",
    default=5,
    show_default=True,
    help="Number of rows to show in --preview mode.",
)
@click.version_option("0.1.0", prog_name="pdf-extract")
def main(pdf_path, fmt, output_dir, pages, prefix, min_rows, preview, preview_rows):
    """
    Extract tables from PDF_PATH and export them.

    \b
    Examples:
      pdf-extract report.pdf
      pdf-extract report.pdf --format excel --output-dir ./results
      pdf-extract report.pdf --pages 1,3 --format json --preview
    """
    # Parse page filter
    page_filter = None
    if pages:
        try:
            page_filter = [int(p.strip()) for p in pages.split(",")]
        except ValueError:
            click.echo("Error: --pages must be comma-separated integers (e.g. '1,3,5').", err=True)
            sys.exit(1)

    click.echo(f"📄 Reading: {pdf_path}")

    try:
        tables = extract_tables_from_pdf(pdf_path, page_filter=page_filter, min_rows=min_rows)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    if not tables:
        click.echo("⚠️  No tables found in the specified page(s).")
        sys.exit(0)

    # Summary
    total_pages_seen = len({t["page"] for t in tables})
    click.echo(f"✅ Found {len(tables)} table(s) across {total_pages_seen} page(s).")

    # Preview
    if preview:
        click.echo("")
        _rich_preview(tables, max_rows=preview_rows)

    # Export
    written = export_tables(tables, output_dir, fmt, prefix=prefix)
    click.echo(f"\n💾 Saved {len(written)} file(s) to '{output_dir}/':")
    for path in written:
        click.echo(f"   {path}")
