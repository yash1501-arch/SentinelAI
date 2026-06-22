import io
import csv
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from app.core.synthetic_data import generate_cases, generate_statistics, generate_trends

def generate_csv(resource_type: str, resource_ids: Optional[list[str]] = None) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)

    if resource_type == "cases":
        cases = generate_cases(50)
        writer.writerow(["ID", "FIR ID", "Crime Type", "Incident Date", "Incident Time",
                          "Description", "Modus Operandi", "Solved", "Property Loss",
                          "Injuries", "Fatalities", "Created At"])
        for c in cases:
            writer.writerow([
                c["id"], c["fir_id"], c["crime_type"]["name"],
                c["incident_date"], c.get("incident_time", ""),
                c["description"], c.get("modus_operandi", ""),
                "Yes" if c["is_solved"] else "No",
                c["property_value_loss"], c["injury_count"],
                c["fatality_count"], c["created_at"],
            ])
    elif resource_type == "analytics":
        stats = generate_statistics()
        writer.writerow(["Metric", "Value"])
        for k, v in stats.items():
            writer.writerow([k.replace("_", " ").title(), v])
    else:
        writer.writerow(["resource_type", resource_type])
        writer.writerow(["exported_at", datetime.now(timezone.utc).isoformat()])
        writer.writerow(["record_count", len(resource_ids) if resource_ids else 0])

    return output.getvalue().encode("utf-8-sig")


def generate_pdf(session_id: str, case_ids: Optional[list[str]] = None,
                 include_charts: bool = False) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"],
                                  fontSize=20, textColor=HexColor("#1a237e"),
                                  spaceAfter=6)
    heading_style = ParagraphStyle("Heading2", parent=styles["Heading2"],
                                    fontSize=14, textColor=HexColor("#283593"),
                                    spaceAfter=4, spaceBefore=12)
    normal_style = ParagraphStyle("Normal2", parent=styles["Normal"],
                                   fontSize=10, leading=14)
    small_style = ParagraphStyle("Small2", parent=styles["Normal"],
                                  fontSize=8, textColor=HexColor("#666666"))

    elements = []

    elements.append(Paragraph("SentinelAI Crime Report", title_style))
    elements.append(Paragraph(
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        small_style))
    elements.append(Paragraph(f"Session: {session_id}", small_style))
    elements.append(Spacer(1, 12))

    stats = generate_statistics()
    elements.append(Paragraph("Executive Summary", heading_style))
    stat_data = [["Metric", "Value"]]
    for k, v in stats.items():
        label = k.replace("_", " ").title()
        val = f"{v:.2f}" if isinstance(v, float) else str(v)
        stat_data.append([label, val])
    stat_table = Table(stat_data, colWidths=[180, 100])
    stat_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#283593")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, HexColor("#f5f5f5")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(stat_table)
    elements.append(Spacer(1, 16))

    if include_charts:
        elements.append(Paragraph("Note: Charts are available in the interactive dashboard.", small_style))
        elements.append(Spacer(1, 8))

    if case_ids:
        elements.append(Paragraph(f"Requested Cases ({len(case_ids)})", heading_style))
        cases = generate_cases(10)
        case_data = [["FIR ID", "Crime Type", "Date", "Status"]]
        for c in cases[:10]:
            case_data.append([
                c["fir_id"][:8],
                c["crime_type"]["name"],
                c["incident_date"],
                "Solved" if c["is_solved"] else "Open",
            ])
        case_table = Table(case_data, colWidths=[100, 100, 100, 80])
        case_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#283593")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, HexColor("#f5f5f5")]),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        elements.append(case_table)
        elements.append(Spacer(1, 8))

    elements.append(Paragraph(
        "This report is auto-generated by SentinelAI Crime Intelligence Platform.",
        small_style))

    doc.build(elements)
    buf.seek(0)
    return buf.read()


def generate_case_detail_pdf(case_id: str) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"],
                                  fontSize=18, textColor=HexColor("#1a237e"),
                                  spaceAfter=6)
    heading_style = ParagraphStyle("Heading2", parent=styles["Heading2"],
                                    fontSize=13, textColor=HexColor("#283593"),
                                    spaceAfter=4, spaceBefore=10)
    label_style = ParagraphStyle("Label", parent=styles["Normal"],
                                  fontSize=9, textColor=HexColor("#666666"),
                                  spaceAfter=1)
    value_style = ParagraphStyle("Value", parent=styles["Normal"],
                                  fontSize=11, spaceAfter=6)
    small_style = ParagraphStyle("Small", parent=styles["Normal"],
                                  fontSize=8, textColor=HexColor("#999999"))

    from app.core.synthetic_data import generate_cases
    cases = generate_cases(1)
    case = cases[0] if cases else {}
    ct = case.get("crime_type", {})

    elements = []
    elements.append(Paragraph("Case Detail Report", title_style))
    elements.append(Paragraph(
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        small_style))
    elements.append(Spacer(1, 12))

    details = [
        ("Case ID", str(case.get("id", case_id))[:8]),
        ("FIR ID", case.get("fir_id", "")[:8]),
        ("Crime Type", ct.get("name", "N/A")),
        ("Category", ct.get("category", "N/A")),
        ("Severity", str(ct.get("severity_level", "N/A"))),
        ("Incident Date", case.get("incident_date", "N/A")),
        ("Incident Time", case.get("incident_time", "N/A")),
        ("Status", "Solved" if case.get("is_solved") else "Open"),
        ("Injuries", str(case.get("injury_count", 0))),
        ("Fatalities", str(case.get("fatality_count", 0))),
        ("Property Loss", f"₹{case.get('property_value_loss', 0):,.2f}"),
    ]

    for label, value in details:
        elements.append(Paragraph(label, label_style))
        elements.append(Paragraph(value, value_style))

    if case.get("description"):
        elements.append(Paragraph("Description", heading_style))
        elements.append(Paragraph(case["description"], value_style))

    if case.get("modus_operandi"):
        elements.append(Paragraph("Modus Operandi", heading_style))
        elements.append(Paragraph(case["modus_operandi"], value_style))

    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "This report is auto-generated by SentinelAI Crime Intelligence Platform.",
        small_style))

    doc.build(elements)
    buf.seek(0)
    return buf.read()
