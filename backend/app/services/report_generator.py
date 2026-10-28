import os
from datetime import datetime
from typing import List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from app.db.models import Document, Clause, RiskFlag
from app.core.config import settings


class ReportGenerator:
    @staticmethod
    def generate_pdf_report(doc: Document, clauses: List[Clause], output_path: str) -> str:
        pdf = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
            alignment=0
        )

        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#475569")
        )

        disclaimer_style = ParagraphStyle(
            "Disclaimer",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#dc2626"),
            alignment=0
        )

        heading2_style = ParagraphStyle(
            "Heading2",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=12,
            spaceAfter=6
        )

        clause_heading_style = ParagraphStyle(
            "ClauseHeading",
            parent=styles["Heading3"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#0f172a")
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#1e293b")
        )

        explanation_style = ParagraphStyle(
            "Explanation",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155")
        )

        story = []

        # 1. Header & Branding
        story.append(Paragraph("<b>ClauseGuard — AI Contract Risk Analysis Report</b>", title_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"Contract: <b>{doc.filename}</b> | Generated on: {datetime.utcnow().strftime('%B %d, %Y, %H:%M UTC')}", subtitle_style))
        story.append(Spacer(1, 6))

        # Legal Disclaimer
        disclaimer_box = [
            [Paragraph("<b>LEGAL DISCLAIMER:</b> This tool is informational and is not legal advice. "
                       "ClauseGuard uses automated pattern extraction and machine learning to assist human review. "
                       "Always consult a qualified attorney for legal matters.", disclaimer_style)]
        ]
        disclaimer_table = Table(disclaimer_box, colWidths=[540])
        disclaimer_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fef2f2")),
            ("BORDER", (0, 0), (-1, -1), 1, colors.HexColor("#f87171")),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(disclaimer_table)
        story.append(Spacer(1, 14))

        # 2. Executive Summary Metrics
        high_count = sum(1 for c in clauses if c.risk_flag and c.risk_flag.risk_level == "High")
        med_count = sum(1 for c in clauses if c.risk_flag and c.risk_flag.risk_level == "Medium")
        low_count = sum(1 for c in clauses if c.risk_flag and c.risk_flag.risk_level == "Low")
        review_count = sum(1 for c in clauses if c.risk_flag and c.risk_flag.needs_review)

        summary_data = [
            ["Metric", "Count", "Assessment"],
            ["Total Analyzed Clauses", str(len(clauses)), "Complete Contract Coverage"],
            ["High Risk Clauses", str(high_count), "Urgent Attention & Renegotiation Recommended" if high_count > 0 else "None Detected"],
            ["Medium Risk Clauses", str(med_count), "Commercial Terms to Verify" if med_count > 0 else "None Detected"],
            ["Low Risk Clauses", str(low_count), "Standard & Commercially Balanced"],
            ["Clauses Requiring Review", str(review_count), "Low Confidence or Ambiguous Wording"]
        ]
        summary_table = Table(summary_data, colWidths=[180, 80, 280])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ]))
        story.append(Paragraph("Executive Risk Summary", heading2_style))
        story.append(summary_table)
        story.append(Spacer(1, 14))

        # 3. Clauses Detail Breakdown
        story.append(Paragraph("Detailed Clause-by-Clause Analysis", heading2_style))
        story.append(Spacer(1, 6))

        for c in clauses:
            rf = c.risk_flag
            risk_level = rf.risk_level if rf else "Low"
            risk_score = rf.risk_score if rf else 0
            explanation = rf.explanation if rf else "No explanation available."
            suggestion = rf.suggestion if rf else "Terms appear standard."
            rules = ", ".join([r["rule_code"] for r in rf.triggered_rules]) if (rf and rf.triggered_rules) else "None"

            # Risk color
            if risk_level == "High":
                bg_color = colors.HexColor("#fef2f2")
                border_color = colors.HexColor("#ef4444")
                badge_color = "#dc2626"
            elif risk_level == "Medium":
                bg_color = colors.HexColor("#fffbeb")
                border_color = colors.HexColor("#f59e0b")
                badge_color = "#d97706"
            else:
                bg_color = colors.HexColor("#f0fdf4")
                border_color = colors.HexColor("#22c55e")
                badge_color = "#16a34a"

            clause_title = f"Clause {c.clause_number}: {c.heading or c.primary_category} (Page {c.page_number})"
            clause_meta = (
                f"Category: <b>{c.primary_category}</b> | "
                f"Risk: <font color='{badge_color}'><b>{risk_level} ({risk_score}/100)</b></font> | "
                f"Confidence: <b>{int(c.confidence * 100)}%</b>"
            )

            clause_card = [
                [Paragraph(f"<b>{clause_title}</b>", clause_heading_style)],
                [Paragraph(clause_meta, subtitle_style)],
                [HRFlowable(width="100%", thickness=0.5, color=border_color, spaceBefore=4, spaceAfter=6)],
                [Paragraph(f"<b>Clause Text:</b> {c.text[:600]}{'...' if len(c.text) > 600 else ''}", body_style)],
                [Spacer(1, 4)],
                [Paragraph(f"<b>Triggered Rules:</b> {rules}", body_style)],
                [Paragraph(f"<b>Analysis:</b> {explanation}", explanation_style)],
                [Paragraph(f"<b>Recommendation:</b> {suggestion}", explanation_style)],
            ]

            card_table = Table(clause_card, colWidths=[540])
            card_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), bg_color),
                ("BOX", (0, 0), (-1, -1), 1, border_color),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]))

            story.append(KeepTogether([card_table, Spacer(1, 10)]))

        # Build PDF
        pdf.build(story)
        return output_path
