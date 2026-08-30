import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)

def generate_pdf_report(dataset_meta: dict, scored_works: list, validation_report: dict = None) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12
    )

    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )

    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#0F172A')
    )

    cell_regular = ParagraphStyle(
        'CellRegular',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # Title & Header
    story.append(Paragraph("MPLAD INTELLIGENCE — EXECUTIVE INTELLIGENCE REPORT", title_style))
    story.append(Paragraph("AI-Assisted Project Integrity & Statutory Risk Prioritization Platform (SIH26102)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F172A'), spaceAfter=12))

    # A. Dataset Summary & Metadata
    name = dataset_meta.get('name', 'Active MPLADS Dataset')
    state = dataset_meta.get('state', 'State')
    district = dataset_meta.get('district', 'District')
    constituency = dataset_meta.get('constituency', 'Constituency')
    upload_dt = dataset_meta.get('uploaded_at') or datetime.now().strftime('%Y-%m-%d %H:%M IST')
    active_status = "CURRENTLY ACTIVE" if dataset_meta.get('is_active') else "STORED IN LIBRARY"

    summary_data = [
        [Paragraph("<b>Dataset Name:</b>", body_style), Paragraph(name, body_style), Paragraph("<b>Status:</b>", body_style), Paragraph(f"<b>{active_status}</b>", body_style)],
        [Paragraph("<b>State:</b>", body_style), Paragraph(state, body_style), Paragraph("<b>District:</b>", body_style), Paragraph(district, body_style)],
        [Paragraph("<b>Constituency:</b>", body_style), Paragraph(constituency, body_style), Paragraph("<b>Analysis Date:</b>", body_style), Paragraph(str(upload_dt)[:19], body_style)]
    ]

    t_summary = Table(summary_data, colWidths=[90, 180, 80, 190])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 10))

    # B. Dataset Statistics & ML Intelligence Summary
    story.append(Paragraph("1. Executive Dataset Statistics & Risk Distribution", heading_style))
    
    total_sanct = dataset_meta.get('sanctioned_count', len(scored_works))
    total_rec = dataset_meta.get('recommended_count', total_sanct)
    total_comp = dataset_meta.get('completed_count', 0)
    anomalies = dataset_meta.get('ml_anomaly_count', 0)
    critical_c = dataset_meta.get('critical_risk_count', 0)
    high_c = dataset_meta.get('high_risk_count', 0)
    medium_c = dataset_meta.get('medium_risk_count', 0)
    normal_c = dataset_meta.get('normal_risk_count', 0)

    kpi_data = [
        [
            Paragraph("<b>Total Sanctioned</b>", cell_bold),
            Paragraph("<b>Recommended</b>", cell_bold),
            Paragraph("<b>Completed</b>", cell_bold),
            Paragraph("<b>ML Anomalies</b>", cell_bold),
            Paragraph("<b>Critical Risk</b>", cell_bold),
            Paragraph("<b>High Risk</b>", cell_bold)
        ],
        [
            Paragraph(f"<b>{total_sanct}</b>", cell_regular),
            Paragraph(f"{total_rec}", cell_regular),
            Paragraph(f"{total_comp}", cell_regular),
            Paragraph(f"<b>{anomalies}</b> ({round(anomalies/total_sanct*100, 1) if total_sanct else 0}%)", cell_regular),
            Paragraph(f"<b>{critical_c}</b>", cell_regular),
            Paragraph(f"<b>{high_c}</b>", cell_regular)
        ]
    ]

    t_kpis = Table(kpi_data, colWidths=[90, 85, 85, 95, 90, 95])
    t_kpis.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F1F5F9')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#94A3B8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_kpis)
    story.append(Spacer(1, 10))

    # C. Statutory Risk Scoring Methodology
    story.append(Paragraph("2. Algorithmic Risk Prioritization Methodology", heading_style))
    story.append(Paragraph(
        "The platform utilizes an explainable composite risk model: <b>S_risk = 0.60 × S_ml + 0.40 × S_rule</b>. "
        "<b>S_ml</b> is generated via a Pure Python Isolation Forest (100 estimators, 6-feature vector matrix). "
        "<b>S_rule</b> evaluates statutory compliance rules (administrative delay thresholds >120d, category cost outliers Z>+2.0, high outlay ≥₹25L, duplicate titles, and disbursement variances).",
        body_style
    ))
    story.append(Spacer(1, 10))

    # D. Top Highest-Risk Priority Projects Table
    story.append(Paragraph("3. High-Priority Audit & Investigation Findings (Top Ranked)", heading_style))
    
    top_works = scored_works[:10]
    headers_table = [
        Paragraph("<b>#</b>", cell_bold),
        Paragraph("<b>Work ID</b>", cell_bold),
        Paragraph("<b>Work Description</b>", cell_bold),
        Paragraph("<b>Amount (Lakhs)</b>", cell_bold),
        Paragraph("<b>S_ml</b>", cell_bold),
        Paragraph("<b>S_rule</b>", cell_bold),
        Paragraph("<b>S_risk</b>", cell_bold),
        Paragraph("<b>Severity Band</b>", cell_bold)
    ]
    
    table_rows = [headers_table]
    for idx, w in enumerate(top_works):
        title_snippet = (w.get('title') or '')[:45] + '...' if len(w.get('title') or '') > 45 else (w.get('title') or '')
        band_str = w.get('severity_band', 'NORMAL RISK').replace(' PRIORITY', '')
        amt_str = f"₹{w.get('sanctioned_amount_lakhs', 0):.2f} L"
        s_ml_val = f"{w.get('ml_anomaly_score', 0):.1f}"
        s_rule_val = f"{w.get('rule_score', 0):.1f}"
        s_risk_val = f"{w.get('risk_priority_score', 0):.1f}"
        
        table_rows.append([
            Paragraph(str(idx + 1), cell_regular),
            Paragraph(w.get('id', ''), cell_bold),
            Paragraph(title_snippet, cell_regular),
            Paragraph(amt_str, cell_regular),
            Paragraph(s_ml_val, cell_regular),
            Paragraph(s_rule_val, cell_regular),
            Paragraph(f"<b>{s_risk_val}</b>", cell_bold),
            Paragraph(band_str, cell_bold)
        ])

    t_findings = Table(table_rows, colWidths=[20, 110, 180, 60, 35, 35, 45, 55])
    t_findings.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#94A3B8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_findings)
    story.append(Spacer(1, 10))

    # E. Top Work Explainability Highlight
    if top_works:
        top_1 = top_works[0]
        story.append(Paragraph("4. Deep-Dive Explainability Case Study: Top Priority Work", heading_style))
        exp_text = f"<b>Project:</b> {top_1.get('id')} — {top_1.get('title')}<br/>"
        exp_text += f"<b>Severity:</b> {top_1.get('severity_band')} (S_risk = {top_1.get('risk_priority_score'):.1f}/100)<br/>"
        exp_text += f"<b>Score Formula:</b> 0.60 × ({top_1.get('ml_anomaly_score'):.1f}) + 0.40 × ({top_1.get('rule_score'):.1f}) = {top_1.get('risk_priority_score'):.1f}<br/>"
        
        signals = top_1.get('rule_signals') or []
        if signals:
            exp_text += f"<b>Triggered Compliance Signals:</b> {'; '.join(signals)}<br/>"
        
        feats = top_1.get('features') or {}
        exp_text += f"<b>Multivariate Vectors:</b> Sanction Delay: {feats.get('sanction_delay_days', top_1.get('sanction_delay_days', 0))} Days | Category Cost Z-Score: +{feats.get('category_cost_zscore', 0):.2f} SD | Agency Outlay Concentration: {feats.get('ida_concentration_pct', 0):.1f}%"
        
        story.append(Paragraph(exp_text, body_style))

    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=6))
    story.append(Paragraph("CONFIDENTIAL • FOR OFFICIAL STATE AUDIT & FIELD VERIFICATION PURPOSES ONLY • SIH26102 MPLAD INTELLIGENCE", ParagraphStyle('Footer', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7, textColor=colors.HexColor('#64748B'), alignment=1)))

    doc.build(story)
    return buffer.getvalue()
