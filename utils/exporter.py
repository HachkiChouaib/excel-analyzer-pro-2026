"""Export layer: clean datasets (Excel/CSV) and PDF analysis reports.

All exporters return ``bytes`` so the Streamlit UI can stream them directly to
a download button without writing temporary files.
"""

from __future__ import annotations

import io
from datetime import datetime

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from utils.analyzer import AIInsight

BRAND_COLOR = colors.HexColor("#2563eb")


# ---------------------------------------------------------------------------
# Tabular exports
# ---------------------------------------------------------------------------
def to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Serialise a DataFrame to an in-memory ``.xlsx`` file.

    Args:
        df: The (cleaned) DataFrame to export.

    Returns:
        The Excel file contents as bytes.
    """
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    buffer.seek(0)
    return buffer.getvalue()


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Serialise a DataFrame to an in-memory UTF-8 CSV file.

    Args:
        df: The (cleaned) DataFrame to export.

    Returns:
        The CSV file contents as bytes.
    """
    return df.to_csv(index=False).encode("utf-8-sig")


# ---------------------------------------------------------------------------
# PDF report
# ---------------------------------------------------------------------------
def _section_title(text: str) -> Paragraph:
    """Create a styled section-title paragraph."""
    style = ParagraphStyle(
        "SectionTitle",
        parent=getSampleStyleSheet()["Heading2"],
        textColor=BRAND_COLOR,
        spaceBefore=14,
        spaceAfter=6,
    )
    return Paragraph(text, style)


def _kpi_table(kpis: dict[str, str]) -> Table:
    """Build a two-column KPI table from a label/value mapping."""
    rows = [[label, value] for label, value in kpis.items()]
    table = Table(rows, colWidths=[8 * cm, 8 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eff6ff")),
                ("TEXTCOLOR", (0, 0), (0, -1), BRAND_COLOR),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("ROWBACKGROUNDS", (1, 0), (1, -1), [colors.white]),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def _stats_table(stats: pd.DataFrame) -> Table:
    """Build a table from the numeric-statistics DataFrame."""
    header = ["Column", *[c.capitalize() for c in stats.columns]]
    body = [
        [str(idx), *[f"{val:,.2f}" for val in row]]
        for idx, row in stats.iterrows()
    ]
    table = Table([header, *body], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BRAND_COLOR),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def build_pdf_report(
    filename: str,
    kpis: dict[str, str],
    stats: pd.DataFrame,
    insight: AIInsight,
) -> bytes:
    """Assemble a complete PDF analysis report.

    Args:
        filename: Name of the analysed dataset.
        kpis: Mapping of KPI labels to display values.
        stats: Numeric-statistics DataFrame (see
            :func:`utils.analyzer.numeric_statistics`).
        insight: The rule-based AI assessment.

    Returns:
        The PDF file contents as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Excel Analyzer Pro 2026 - Report",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        textColor=BRAND_COLOR,
    )

    story: list = []

    # --- Header ---
    story.append(Paragraph("Excel Analyzer Pro 2026", title_style))
    story.append(Paragraph("Automated Data Analysis Report", styles["Heading3"]))
    story.append(
        Paragraph(
            f"File: <b>{filename}</b> &nbsp;|&nbsp; "
            f"Generated: {datetime.now():%Y-%m-%d %H:%M}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.4 * cm))

    # --- Summary ---
    story.append(_section_title("1. Summary"))
    story.append(Paragraph(insight.summary, styles["Normal"]))

    # --- KPIs ---
    story.append(_section_title("2. Key Performance Indicators"))
    story.append(_kpi_table(kpis))

    # --- Statistics ---
    if not stats.empty:
        story.append(_section_title("3. Numeric Statistics"))
        story.append(_stats_table(stats))

    # --- Detected issues ---
    story.append(_section_title("4. Detected Issues"))
    for item in insight.issues:
        story.append(Paragraph(f"&bull; {item}", styles["Normal"]))

    # --- Recommendations ---
    story.append(_section_title("5. Recommendations"))
    if insight.recommendations:
        for item in insight.recommendations:
            story.append(Paragraph(f"&bull; {item}", styles["Normal"]))
    else:
        story.append(Paragraph("No specific recommendations.", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
