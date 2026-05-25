from __future__ import annotations

import textwrap
from collections import Counter
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
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
# Palet Warna
# ---------------------------------------------------------------------------
C_PRIMARY       = colors.HexColor("#00a6f4")   # biru utama
C_PRIMARY_DARK  = colors.HexColor("#0088cc")   # biru gelap
C_PRIMARY_DEEP  = colors.HexColor("#005f8e")   # biru lebih gelap untuk header
C_PRIMARY_LIGHT = colors.HexColor("#e6f6fe")   # biru muda – background kartu
C_ACCENT        = colors.HexColor("#00c4ff")   # biru terang aksen
C_ACCENT_LINE   = colors.HexColor("#7ddcff")   # garis aksen tipis

C_SUCCESS       = colors.HexColor("#10b981")   # hijau
C_WARNING       = colors.HexColor("#f59e0b")   # kuning
C_DANGER        = colors.HexColor("#ef4444")   # merah
C_NEUTRAL       = colors.HexColor("#6b7280")   # abu-abu

C_TABLE_HEAD    = colors.HexColor("#005f8e")   # header tabel
C_ROW_ODD       = colors.HexColor("#f0faff")   # baris ganjil
C_ROW_EVEN      = colors.white
C_BORDER        = colors.HexColor("#bae6fd")   # border biru muda
C_BORDER_SOFT   = colors.HexColor("#e0f2fe")

C_TEXT_DARK     = colors.HexColor("#0c1a29")   # teks utama
C_TEXT_MID      = colors.HexColor("#0284c7")   # teks menengah
C_TEXT_GREY     = colors.HexColor("#64748b")   # teks abu-abu

PAGE_W, PAGE_H  = A4
MARGIN          = 1.6 * cm


# ---------------------------------------------------------------------------
# Utilitas
# ---------------------------------------------------------------------------

def _fmt_dt(value: datetime | None) -> str:
    if not value:
        return "—"
    return value.strftime("%d %B %Y, %H:%M")


def _fmt_dt_short(value: datetime | None) -> str:
    if not value:
        return "—"
    return value.strftime("%d %b %Y")


def _truncate(value: str | None, n: int = 200) -> str:
    if not value:
        return ""
    return value[: n - 3].rstrip() + "…" if len(value) > n else value


def _label_color(label: str | None) -> colors.Color:
    if not label:
        return C_NEUTRAL
    l = label.lower()
    if l in ("positive", "pos", "good", "positif"):
        return C_SUCCESS
    if l in ("negative", "neg", "bad", "negatif"):
        return C_DANGER
    if l in ("neutral", "netral"):
        return C_NEUTRAL
    return C_PRIMARY


def _label_id(label: str | None) -> str:
    """Terjemahkan label sentimen ke Bahasa Indonesia."""
    if not label:
        return "—"
    mapping = {
        "positive": "Positif",
        "negative": "Negatif",
        "neutral":  "Netral",
    }
    return mapping.get(label.lower(), label.capitalize())


def _fmt_label_counts(lc: dict | None) -> str:
    if not lc:
        return "—"
    parts = []
    for k, v in sorted(lc.items()):
        parts.append(f"{_label_id(k)}: {v}")
    return "  |  ".join(parts)


def _status_id(status: str | None) -> str:
    mapping = {
        "completed":  "Selesai",
        "processing": "Diproses",
        "failed":     "Gagal",
        "pending":    "Menunggu",
    }
    if not status:
        return "—"
    return mapping.get(status.lower(), status.capitalize())


# ---------------------------------------------------------------------------
# Canvas kustom – header & footer setiap halaman
# ---------------------------------------------------------------------------

def _make_page_canvas(report: Report, total_pages_ref: list):
    def _on_page(canvas, doc):
        canvas.saveState()
        w, h = A4

        # ── Header band utama ──────────────────────────────────────────────
        band_h = 1.25 * cm
        canvas.setFillColor(C_PRIMARY_DEEP)
        canvas.rect(0, h - band_h, w, band_h, fill=1, stroke=0)

        # Aksen warna di sisi kiri header
        canvas.setFillColor(C_PRIMARY)
        canvas.rect(0, h - band_h, 0.5 * cm, band_h, fill=1, stroke=0)

        # Nama aplikasi
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 10.5)
        canvas.drawString(MARGIN, h - band_h + 0.42 * cm, "Sentexa")

        canvas.setFont("Helvetica", 8.5)
        canvas.setFillColor(C_ACCENT_LINE)
        canvas.drawString(
            MARGIN + 1.6 * cm,
            h - band_h + 0.42 * cm,
            "Platform Analisis Sentimen",
        )

        # Judul laporan (kanan)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#cce9f6"))
        title_short = _truncate(report.title, 52)
        canvas.drawRightString(w - MARGIN, h - band_h + 0.42 * cm, title_short)

        # Garis aksen di bawah header
        canvas.setFillColor(C_ACCENT)
        canvas.rect(0, h - band_h - 0.12 * cm, w, 0.12 * cm, fill=1, stroke=0)

        # ── Footer ─────────────────────────────────────────────────────────
        footer_y = 0.9 * cm
        canvas.setStrokeColor(C_BORDER)
        canvas.setLineWidth(0.6)
        canvas.line(MARGIN, footer_y + 0.3 * cm, w - MARGIN, footer_y + 0.3 * cm)

        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(C_TEXT_GREY)
        canvas.drawString(
            MARGIN,
            footer_y - 0.05 * cm,
            f"Dibuat pada {_fmt_dt(datetime.utcnow())} UTC   ·   ID Laporan: {report.id}",
        )
        canvas.drawRightString(
            w - MARGIN,
            footer_y - 0.05 * cm,
            f"Halaman {doc.page}",
        )

        canvas.restoreState()

    return _on_page


# ---------------------------------------------------------------------------
# Registry gaya teks
# ---------------------------------------------------------------------------

def _build_styles():
    base = getSampleStyleSheet()

    def add(name, **kw):
        base.add(ParagraphStyle(name=name, **kw))

    add("SectionTitle",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=C_PRIMARY_DEEP,
        spaceBefore=16,
        spaceAfter=4,
    )
    add("SectionSubtitle",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=C_TEXT_GREY,
        spaceAfter=6,
    )
    add("MetaLabel",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        textColor=C_TEXT_GREY,
        spaceAfter=1,
    )
    add("MetaValue",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=C_TEXT_DARK,
        spaceAfter=3,
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
    add("TableCellCenter",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=C_TEXT_DARK,
        alignment=TA_CENTER,
    )
    add("StatNumber",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=C_PRIMARY_DEEP,
        alignment=TA_CENTER,
        spaceAfter=2,
    )
    add("StatLabel",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
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
    add("CoverTag",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        textColor=C_PRIMARY,
        spaceAfter=2,
    )

    return base


# ---------------------------------------------------------------------------
# Cover / Ringkasan
# ---------------------------------------------------------------------------

def _build_cover(report: Report, analyses: list[AnalysisHistory], styles) -> list:
    story = []

    # ── Judul laporan ──────────────────────────────────────────────────────
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("LAPORAN ANALISIS SENTIMEN", styles["CoverTag"]))
    story.append(Paragraph(report.title, ParagraphStyle(
        "BigTitle",
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=C_PRIMARY_DEEP,
        leading=25,
        spaceAfter=5,
    )))
    if report.description:
        story.append(Paragraph(report.description, styles["BodyDesc"]))

    # Garis pemisah berwarna primary
    story.append(HRFlowable(
        width="100%", thickness=2, color=C_PRIMARY, spaceAfter=10, spaceBefore=4,
    ))

    # ── Tabel metadata ─────────────────────────────────────────────────────
    meta = [
        ["ID Laporan",    str(report.id),
         "ID Pekerjaan",  report.job_id or "—"],
        ["Tanggal Mulai", _fmt_dt(report.start_date),
         "Tanggal Selesai", _fmt_dt(report.end_date)],
        ["Total Data",   str(len(analyses)),
         "Waktu Dibuat", _fmt_dt(datetime.utcnow()) + " UTC"],
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
        colWidths=[3.0 * cm, 5.8 * cm, 3.4 * cm, 5.8 * cm],
        hAlign="LEFT",
    )
    meta_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_PRIMARY_LIGHT),
        ("GRID",          (0, 0), (-1, -1), 0, colors.white),
        ("BOX",           (0, 0), (-1, -1), 0.8, C_BORDER),
        ("LINEAFTER",     (1, 0), (1, -1), 0.5, C_BORDER),
        ("LEFTPADDING",   (0, 0), (-1, -1), 9),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 9),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.55 * cm))

    # ── Kartu statistik ────────────────────────────────────────────────────
    total = len(analyses)
    label_counter: Counter = Counter()
    status_counter: Counter = Counter()
    for a in analyses:
        if a.result_label:
            label_counter[a.result_label.lower()] += 1
        if a.status:
            status_counter[a.status.lower()] += 1

    top_raw    = label_counter.most_common(1)[0][0] if label_counter else None
    top_label  = _label_id(top_raw) if top_raw else "—"
    top_status = _status_id(status_counter.most_common(1)[0][0]) if status_counter else "—"
    avg_score  = (
        sum(a.result_score for a in analyses if a.result_score is not None)
        / max(1, sum(1 for a in analyses if a.result_score is not None))
    )

    cards = [
        (str(total),          "Total Data"),
        (f"{avg_score:.2f}",  "Rata-rata Skor"),
        (top_label,           "Label Utama"),
        (top_status,          "Status Utama"),
    ]

    def stat_card(number, label):
        inner = Table(
            [
                [Paragraph(number, styles["StatNumber"])],
                [Paragraph(label,  styles["StatLabel"])],
            ],
            colWidths=[4.2 * cm],
        )
        inner.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), colors.white),
            ("BOX",           (0, 0), (-1, -1), 1, C_BORDER),
            ("LINEABOVE",     (0, 0), (-1, 0),  3, C_PRIMARY),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING",   (0, 0), (-1, -1), 4),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ]))
        return inner

    cards_row   = [[stat_card(n, l) for n, l in cards]]
    cards_table = Table(cards_row, colWidths=[4.3 * cm] * 4, hAlign="CENTER")
    cards_table.setStyle(TableStyle([
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
    ]))
    story.append(cards_table)
    story.append(Spacer(1, 0.6 * cm))

    # ── Distribusi label ───────────────────────────────────────────────────
    if label_counter:
        story.append(Paragraph("Distribusi Label Sentimen", styles["SectionTitle"]))
        story.append(HRFlowable(
            width="100%", thickness=1, color=C_BORDER, spaceAfter=6, spaceBefore=2,
        ))

        dist_data = [[
            Paragraph("Label",      styles["TableHead"]),
            Paragraph("Jumlah",     styles["TableHead"]),
            Paragraph("Persentase", styles["TableHead"]),
            Paragraph("Proporsi",   styles["TableHead"]),
        ]]
        for lbl_raw, cnt in label_counter.most_common():
            pct = cnt / total * 100
            lbl_id  = _label_id(lbl_raw)
            lc      = _label_color(lbl_raw)

            # Bar proporsi sederhana menggunakan teks
            bar_len = int(pct / 100 * 20)
            bar     = "█" * bar_len + "░" * (20 - bar_len)

            dist_data.append([
                Paragraph(
                    f'<font color="{lc.hexval()}">●</font>  {lbl_id}',
                    styles["TableCell"],
                ),
                Paragraph(str(cnt), styles["TableCellCenter"]),
                Paragraph(f"{pct:.1f}%", styles["TableCellCenter"]),
                Paragraph(
                    f'<font color="{lc.hexval()}">{bar}</font>',
                    styles["TableCellGrey"],
                ),
            ])

        dist_table = Table(
            dist_data,
            colWidths=[4.5 * cm, 2.5 * cm, 2.5 * cm, 8.5 * cm],
            hAlign="LEFT",
        )
        dist_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  C_TABLE_HEAD),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
            ("GRID",          (0, 0), (-1, -1), 0.3, C_BORDER_SOFT),
            ("LINEBELOW",     (0, 0), (-1, 0),  1.5, C_PRIMARY),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C_ROW_ODD, C_ROW_EVEN]),
            ("LEFTPADDING",   (0, 0), (-1, -1), 9),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("ALIGN",         (1, 0), (2, -1),  "CENTER"),
        ]))
        story.append(dist_table)
        story.append(Spacer(1, 0.3 * cm))

    return story


# ---------------------------------------------------------------------------
# Tabel data detail
# ---------------------------------------------------------------------------

def _build_data_table(analyses: list[AnalysisHistory], styles) -> list:
    story = []
    story.append(PageBreak())
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("Data Analisis Lengkap", styles["SectionTitle"]))
    story.append(Paragraph(
        "Rincian lengkap seluruh entri analisis dalam periode laporan ini.",
        styles["SectionSubtitle"],
    ))
    story.append(HRFlowable(
        width="100%", thickness=1.5, color=C_PRIMARY, spaceAfter=8, spaceBefore=2,
    ))

    # Header kolom
    headers = [
        "No",
        "Sumber",
        "Teks Masukan",
        "Status",
        "Label",
        "Skor",
        "Distribusi Label",
        "Tanggal",
    ]

    def head(t):
        return Paragraph(t, styles["TableHead"])

    rows = [[head(h) for h in headers]]
    col_w = [0.75*cm, 2.6*cm, 5.0*cm, 1.8*cm, 1.7*cm, 1.3*cm, 2.7*cm, 2.65*cm]

    for idx, a in enumerate(analyses, start=1):
        source = (
            f"{a.source_type or '—'}\n{_truncate(a.source_name, 30) or '—'}"
        )
        label_raw = a.result_label or None
        label_id  = _label_id(label_raw)
        lc        = _label_color(label_raw)
        score     = f"{a.result_score:.4f}" if a.result_score is not None else "—"

        badge = Paragraph(
            f'<font color="{lc.hexval()}"><b>{label_id.upper()}</b></font>',
            styles["TableCell"],
        )

        rows.append([
            Paragraph(str(idx), styles["TableCellGrey"]),
            Paragraph(textwrap.fill(source, 20), styles["TableCell"]),
            Paragraph(textwrap.fill(_truncate(a.input_text, 140), 38), styles["TableCell"]),
            Paragraph(_status_id(a.status), styles["TableCellGrey"]),
            badge,
            Paragraph(score, styles["TableCellGrey"]),
            Paragraph(textwrap.fill(_fmt_label_counts(a.label_counts), 26), styles["TableCellGrey"]),
            Paragraph(_fmt_dt_short(a.created_at), styles["TableCellGrey"]),
        ])

    table = Table(rows, repeatRows=1, colWidths=col_w)

    ts = TableStyle([
        # Header
        ("BACKGROUND",    (0, 0), (-1, 0),  C_TABLE_HEAD),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  8),
        ("LINEBELOW",     (0, 0), (-1, 0),  2, C_PRIMARY),
        # Body
        ("FONTSIZE",      (0, 1), (-1, -1), 7.5),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("GRID",          (0, 0), (-1, -1), 0.25, C_BORDER_SOFT),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.4, C_BORDER),
        # Padding
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])

    # Baris selang-seling
    for i in range(1, len(rows)):
        bg = C_ROW_ODD if i % 2 == 1 else C_ROW_EVEN
        ts.add("BACKGROUND", (0, i), (-1, i), bg)

    table.setStyle(ts)
    story.append(table)

    # ── Catatan kaki tabel ─────────────────────────────────────────────────
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        f"Total {len(analyses)} entri ditampilkan dalam laporan ini.",
        ParagraphStyle(
            "FootNote",
            fontName="Helvetica",
            fontSize=7.5,
            textColor=C_TEXT_GREY,
            alignment=TA_RIGHT,
        ),
    ))

    return story


# ---------------------------------------------------------------------------
# Fungsi utama
# ---------------------------------------------------------------------------

def build_report_pdf(
    report: Report,
    analyses: list[AnalysisHistory],
    file_path: str,
) -> None:
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    styles = _build_styles()

    HEADER_H = 1.37 * cm   # band + garis aksen
    FOOTER_H = 1.25 * cm

    frame = Frame(
        MARGIN,
        FOOTER_H,
        PAGE_W - 2 * MARGIN,
        PAGE_H - HEADER_H - FOOTER_H,
        leftPadding=0,
        rightPadding=0,
        topPadding=0.35 * cm,
        bottomPadding=0,
    )

    on_page  = _make_page_canvas(report, [])
    template = PageTemplate(id="main", frames=[frame], onPage=on_page)
    doc      = BaseDocTemplate(
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