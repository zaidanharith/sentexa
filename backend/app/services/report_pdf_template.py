from __future__ import annotations

import textwrap
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import HRFlowable

from app.models.analysis_history import AnalysisHistory
from app.models.report_feedback_alert import Report


# ---------------------------------------------------------------------------
# Brand palette
# ---------------------------------------------------------------------------
C_PRIMARY      = colors.HexColor("#4F46E5")   # indigo-600
C_PRIMARY_DARK = colors.HexColor("#3730A3")   # indigo-800
C_ACCENT       = colors.HexColor("#7C3AED")   # violet-600
C_BG_HEADER    = colors.HexColor("#EEF2FF")   # indigo-50
C_SUCCESS      = colors.HexColor("#059669")   # emerald-600
C_WARNING      = colors.HexColor("#D97706")   # amber-600
C_DANGER       = colors.HexColor("#DC2626")   # red-600
C_NEUTRAL      = colors.HexColor("#6B7280")   # gray-500

C_TABLE_HEAD   = colors.HexColor("#312E81")   # indigo-900
C_ROW_ODD      = colors.HexColor("#F5F3FF")   # violet-50
C_ROW_EVEN     = colors.white
C_BORDER       = colors.HexColor("#C7D2FE")   # indigo-200
C_TEXT_DARK    = colors.HexColor("#1E1B4B")   # indigo-950
C_TEXT_MID     = colors.HexColor("#4338CA")   # indigo-700
C_TEXT_GREY    = colors.HexColor("#6B7280")

PAGE_W, PAGE_H = A4
MARGIN = 1.6 * cm


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_dt(value: datetime | None) -> str:
    return value.strftime("%d %b %Y, %H:%M") if value else "—"


def _truncate(value: str | None, n: int = 200) -> str:
    if not value:
        return ""
    return value[:n - 3].rstrip() + "…" if len(value) > n else value


def _label_color(label: str | None) -> colors.Color:
    if not label:
        return C_NEUTRAL
    l = label.lower()
    if l in ("positive", "pos", "good"):
        return C_SUCCESS
    if l in ("negative", "neg", "bad"):
        return C_DANGER
    if l in ("neutral",):
        return C_NEUTRAL
    return C_PRIMARY


def _fmt_label_counts(lc: dict | None) -> str:
    if not lc:
        return ""
    return "  ".join(f"{k}: {v}" for k, v in sorted(lc.items()))


# ---------------------------------------------------------------------------
# Custom page canvas – draws header band + footer on every page
# ---------------------------------------------------------------------------

def _make_page_canvas(report: Report, total_pages_ref: list):
    """Return a canvas drawing callback."""

    def _on_page(canvas, doc):
        canvas.saveState()
        w, h = A4

        # ── Top gradient band ──────────────────────────────────────────────
        band_h = 1.2 * cm
        canvas.setFillColor(C_PRIMARY_DARK)
        canvas.rect(0, h - band_h, w, band_h, fill=1, stroke=0)

        # App name (left)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(MARGIN, h - band_h + 0.4 * cm, "Sentexa")
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.HexColor("#C7D2FE"))
        canvas.drawString(MARGIN + 1.45 * cm, h - band_h + 0.4 * cm, "Sentiment Analysis Platform")

        # Report title (right)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#E0E7FF"))
        title_short = _truncate(report.title, 55)
        canvas.drawRightString(w - MARGIN, h - band_h + 0.4 * cm, title_short)

        # ── Thin accent stripe below band ──────────────────────────────────
        canvas.setFillColor(C_ACCENT)
        canvas.rect(0, h - band_h - 0.15 * cm, w, 0.15 * cm, fill=1, stroke=0)

        # ── Footer ─────────────────────────────────────────────────────────
        footer_y = 0.85 * cm
        canvas.setStrokeColor(C_BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, footer_y + 0.35 * cm, w - MARGIN, footer_y + 0.35 * cm)

        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(C_TEXT_GREY)
        canvas.drawString(MARGIN, footer_y, f"Generated {_fmt_dt(datetime.utcnow())} UTC   ·   Report ID: {report.id}")
        canvas.drawRightString(w - MARGIN, footer_y, f"Page {doc.page}")

        canvas.restoreState()

    return _on_page


# ---------------------------------------------------------------------------
# Style registry
# ---------------------------------------------------------------------------

def _build_styles():
    base = getSampleStyleSheet()

    def add(name, **kw):
        base.add(ParagraphStyle(name=name, **kw))

    add("SectionTitle",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=C_PRIMARY_DARK,
        spaceBefore=14,
        spaceAfter=4,
    )
    add("SubTitle",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=C_TEXT_MID,
        spaceAfter=6,
    )
    add("MetaLabel",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        textColor=C_TEXT_GREY,
    )
    add("MetaValue",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        textColor=C_TEXT_DARK,
        spaceAfter=4,
    )
    add("TableHead",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        textColor=colors.white,
        alignment=TA_LEFT,
    )
    add("TableCell",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=C_TEXT_DARK,
    )
    add("TableCellGrey",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=C_TEXT_GREY,
    )
    add("Badge",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        alignment=TA_CENTER,
    )
    add("StatNumber",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=C_PRIMARY_DARK,
        alignment=TA_CENTER,
    )
    add("StatLabel",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=8,
        textColor=C_TEXT_GREY,
        alignment=TA_CENTER,
    )
    add("BodyDesc",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        textColor=C_TEXT_DARK,
        leading=14,
        spaceAfter=6,
    )

    return base


# ---------------------------------------------------------------------------
# Cover / summary block
# ---------------------------------------------------------------------------

def _build_cover(report: Report, analyses: list[AnalysisHistory], styles) -> list:
    story = []

    # ── Report main title ──────────────────────────────────────────────────
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Analysis Report", styles["SectionTitle"]))
    story.append(Paragraph(report.title, ParagraphStyle(
        "BigTitle",
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=C_PRIMARY_DARK,
        leading=24,
        spaceAfter=4,
    )))
    if report.description:
        story.append(Paragraph(report.description, styles["BodyDesc"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_ACCENT, spaceAfter=10))

    # ── Metadata table ─────────────────────────────────────────────────────
    meta = [
        ["Report ID", str(report.id),        "Job ID",     report.job_id or "—"],
        ["Start Date", _fmt_dt(report.start_date), "End Date", _fmt_dt(report.end_date)],
        ["Total Records", str(len(analyses)), "Generated",  _fmt_dt(datetime.utcnow()) + " UTC"],
    ]

    def meta_row(row):
        return [
            Paragraph(row[0], styles["MetaLabel"]),
            Paragraph(row[1], styles["MetaValue"]),
            Paragraph(row[2], styles["MetaLabel"]),
            Paragraph(row[3], styles["MetaValue"]),
        ]

    meta_table = Table(
        [meta_row(r) for r in meta],
        colWidths=[3.2 * cm, 5.8 * cm, 3.2 * cm, 5.8 * cm],
        hAlign="LEFT",
    )
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_BG_HEADER),
        ("GRID", (0, 0), (-1, -1), 0, colors.white),
        ("BOX", (0, 0), (-1, -1), 0.8, C_BORDER),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("ROUNDEDCORNERS", [4]),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Stat cards ─────────────────────────────────────────────────────────
    total = len(analyses)
    label_counter: Counter = Counter()
    status_counter: Counter = Counter()
    for a in analyses:
        if a.result_label:
            label_counter[a.result_label.capitalize()] += 1
        if a.status:
            status_counter[a.status.capitalize()] += 1

    top_label  = label_counter.most_common(1)[0][0] if label_counter else "—"
    top_status = status_counter.most_common(1)[0][0] if status_counter else "—"
    avg_score  = (
        sum(a.result_score for a in analyses if a.result_score is not None)
        / max(1, sum(1 for a in analyses if a.result_score is not None))
    )

    cards = [
        (str(total),           "Total Records"),
        (f"{avg_score:.3f}",   "Avg. Confidence"),
        (top_label,            "Top Label"),
        (top_status,           "Top Status"),
    ]

    def stat_card(number, label):
        inner = Table(
            [[Paragraph(number, styles["StatNumber"])],
             [Paragraph(label,  styles["StatLabel"])]],
            colWidths=[4.0 * cm],
        )
        inner.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, -1), colors.white),
            ("BOX",          (0, 0), (-1, -1), 1.2, C_BORDER),
            ("TOPPADDING",   (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
        ]))
        return inner

    cards_row = [[stat_card(n, l) for n, l in cards]]
    cards_table = Table(cards_row, colWidths=[4.3 * cm] * 4, hAlign="CENTER")
    cards_table.setStyle(TableStyle([
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(cards_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Label distribution mini-table ──────────────────────────────────────
    if label_counter:
        story.append(Paragraph("Label Distribution", styles["SectionTitle"]))
        dist_data = [["Label", "Count", "Percentage"]]
        for lbl, cnt in label_counter.most_common():
            pct = f"{cnt / total * 100:.1f}%"
            dist_data.append([
                Paragraph(f'<font color="{_label_color(lbl).hexval()}">\u25CF</font>  {lbl}',
                          styles["TableCell"]),
                Paragraph(str(cnt), styles["TableCell"]),
                Paragraph(pct, styles["TableCell"]),
            ])
        dist_table = Table(dist_data, colWidths=[7 * cm, 3 * cm, 4 * cm], hAlign="LEFT")
        dist_table.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0),  C_TABLE_HEAD),
            ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, -1), 8.5),
            ("GRID",         (0, 0), (-1, -1), 0.4, C_BORDER),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C_ROW_ODD, C_ROW_EVEN]),
            ("LEFTPADDING",  (0, 0), (-1, -1), 8),
            ("TOPPADDING",   (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ]))
        story.append(dist_table)
        story.append(Spacer(1, 0.3 * cm))

    return story


# ---------------------------------------------------------------------------
# Data table
# ---------------------------------------------------------------------------

def _build_data_table(analyses: list[AnalysisHistory], styles) -> list:
    story = []
    story.append(PageBreak())
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Analysis Records", styles["SectionTitle"]))
    story.append(Paragraph(
        "Detailed breakdown of all analysed entries in this report period.",
        styles["SubTitle"],
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceAfter=8))

    # Header row
    headers = ["#", "Source", "Input Text", "Status", "Label", "Score", "Label Counts", "Date"]

    def head(t):
        return Paragraph(t, styles["TableHead"])

    rows = [[head(h) for h in headers]]

    col_w = [0.9 * cm, 2.8 * cm, 5.0 * cm, 1.8 * cm, 1.6 * cm, 1.3 * cm, 2.5 * cm, 2.8 * cm]

    for a in analyses:
        source = f"{a.source_type}\n{a.source_name or '—'}"
        label  = a.result_label or "—"
        lc     = _label_color(label)
        score  = f"{a.result_score:.4f}" if a.result_score is not None else "—"

        # Coloured label badge
        badge = Paragraph(
            f'<font color="{lc.hexval()}"><b>{label.upper()}</b></font>',
            styles["TableCell"],
        )

        rows.append([
            Paragraph(str(a.id), styles["TableCellGrey"]),
            Paragraph(textwrap.fill(source, 22), styles["TableCell"]),
            Paragraph(textwrap.fill(_truncate(a.input_text, 140), 38), styles["TableCell"]),
            Paragraph(a.status or "—", styles["TableCellGrey"]),
            badge,
            Paragraph(score, styles["TableCellGrey"]),
            Paragraph(textwrap.fill(_fmt_label_counts(a.label_counts), 28), styles["TableCellGrey"]),
            Paragraph(_fmt_dt(a.created_at), styles["TableCellGrey"]),
        ])

    table = Table(rows, repeatRows=1, colWidths=col_w)

    ts = TableStyle([
        # Header
        ("BACKGROUND",    (0, 0), (-1, 0),  C_TABLE_HEAD),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  8),
        # Body
        ("FONTSIZE",      (0, 1), (-1, -1), 7.5),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("GRID",          (0, 0), (-1, -1), 0.3, C_BORDER),
        ("LINEBELOW",     (0, 0), (-1, 0),  1.2, C_ACCENT),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])
    # Alternating rows
    for i in range(1, len(rows)):
        bg = C_ROW_ODD if i % 2 == 1 else C_ROW_EVEN
        ts.add("BACKGROUND", (0, i), (-1, i), bg)

    table.setStyle(ts)
    story.append(table)
    return story


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_report_pdf(report: Report, analyses: list[AnalysisHistory], file_path: str) -> None:
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    styles = _build_styles()

    # ── Document with custom page template ────────────────────────────────
    HEADER_H = 1.35 * cm   # top band + accent stripe
    FOOTER_H = 1.2  * cm

    frame = Frame(
        MARGIN,
        FOOTER_H,
        PAGE_W - 2 * MARGIN,
        PAGE_H - HEADER_H - FOOTER_H,
        leftPadding=0,
        rightPadding=0,
        topPadding=0.3 * cm,
        bottomPadding=0,
    )

    on_page = _make_page_canvas(report, [])
    template = PageTemplate(id="main", frames=[frame], onPage=on_page)
    doc = BaseDocTemplate(
        file_path,
        pagesize=A4,
        pageTemplates=[template],
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=HEADER_H,
        bottomMargin=FOOTER_H,
    )

    story: list = []
    story += _build_cover(report, analyses, styles)
    story += _build_data_table(analyses, styles)

    doc.build(story)