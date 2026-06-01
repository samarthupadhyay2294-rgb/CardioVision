from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ai_engine.prediction.features import FEATURE_DESCRIPTIONS, FEATURE_NAMES


def generate_pdf_report(
    input_values: dict,
    risk_pct: float,
    risk_label: str,
    disease_risks: dict,
    explanations: list,
    recommendations: dict,
    shap_factors: list,
    output_path: str = "cardiovision_report.pdf",
):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    story = []

    BLUE = colors.HexColor("#2563EB")
    RED = colors.HexColor("#EF4444")
    GREEN = colors.HexColor("#10B981")
    AMBER = colors.HexColor("#F59E0B")

    if risk_pct >= 75:
        risk_color = RED
    elif risk_pct >= 55:
        risk_color = RED
    elif risk_pct >= 35:
        risk_color = AMBER
    else:
        risk_color = GREEN

    title_style = ParagraphStyle(
        "Title", parent=styles["Title"], fontSize=20, textColor=BLUE, spaceAfter=6
    )
    h2_style = ParagraphStyle(
        "H2", parent=styles["Heading2"], textColor=BLUE, spaceBefore=12, spaceAfter=4
    )
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, spaceAfter=3)
    risk_style = ParagraphStyle(
        "Risk",
        parent=styles["Normal"],
        fontSize=28,
        textColor=risk_color,
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    story.append(Paragraph("CardioVision — Cardiovascular Risk Report", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(f"Overall Risk: {risk_pct}%", risk_style))
    story.append(
        Paragraph(
            f"Category: {risk_label}",
            ParagraphStyle(
                "RL",
                parent=styles["Normal"],
                fontSize=14,
                textColor=risk_color,
                alignment=TA_CENTER,
            ),
        )
    )
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Disease-Specific Risk Scores", h2_style))
    ds_data = [["Condition", "Risk %"]] + [[k, f"{v}%"] for k, v in disease_risks.items()]
    ds_table = Table(ds_data, colWidths=[10 * cm, 4 * cm])
    ds_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BLUE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF2F7")]),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ]
        )
    )
    story.append(ds_table)
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Clinical Parameters", h2_style))
    param_rows = [["Parameter", "Value", "Description"]]
    for feat in FEATURE_NAMES:
        param_rows.append(
            [feat, str(input_values.get(feat, "N/A")), FEATURE_DESCRIPTIONS[feat]]
        )
    param_table = Table(param_rows, colWidths=[4 * cm, 3 * cm, 9 * cm])
    param_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BLUE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF2F7")]),
            ]
        )
    )
    story.append(param_table)
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Key Risk Drivers", h2_style))
    for e in explanations:
        story.append(Paragraph(f"• {e}", body_style))

    if shap_factors:
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph("SHAP Feature Contributions", h2_style))
        for item in shap_factors[:5]:
            story.append(
                Paragraph(
                    f"• {item['label']}: +{item['contribution_pct']}% ({item['direction']})",
                    body_style,
                )
            )

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("Recommendations", h2_style))
    for section in ("diet", "exercise", "lifestyle", "follow_up", "monitoring"):
        items = recommendations.get(section, [])
        if items:
            story.append(Paragraph(f"<b>{section.replace('_', ' ').title()}</b>", body_style))
            for r in items:
                story.append(Paragraph(f"  • {r}", body_style))

    doc.build(story)
    return output_path
