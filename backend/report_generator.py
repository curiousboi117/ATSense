import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from typing import Dict, Any, List

def generate_pdf_report(data: Dict[str, Any], output_path: str):
    """
    Generates a professional, print-friendly PDF report of the resume analysis using ReportLab.
    """
    # Create the document template
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    primary_color = colors.HexColor("#0f172a")    # Slate 900
    secondary_color = colors.HexColor("#0ea5e9")  # Sky 500
    text_color = colors.HexColor("#334155")       # Slate 700
    bg_light = colors.HexColor("#f8fafc")         # Slate 50
    border_color = colors.HexColor("#e2e8f0")     # Slate 200
    
    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=secondary_color,
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'HeadingSection',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_color
    )
    
    body_bold = ParagraphStyle(
        'BodyBoldCustom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    story = []
    
    # Header block
    story.append(Paragraph("ATSense: Professional Resume Audit Report", title_style))
    date_str = datetime.now().strftime("%B %d, %Y - %H:%M")
    story.append(Paragraph(f"Generated on {date_str} | Resume: {data.get('filename')} (v{data.get('version', 1)})", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Summary Details Table
    p_info = data.get("personal_info", {})
    summary_data = [
        [
            Paragraph("<b>Candidate Name:</b>", body_style),
            Paragraph(p_info.get("name") or "Not Detected", body_bold),
            Paragraph("<b>ATS Score:</b>", body_style),
            Paragraph(f"<b><font color='{secondary_color.hexval()}'>{data.get('ats_score')}/100</font></b>", body_bold)
        ],
        [
            Paragraph("<b>Email:</b>", body_style),
            Paragraph(p_info.get("email") or "Not Detected", body_style),
            Paragraph("<b>Phone:</b>", body_style),
            Paragraph(p_info.get("phone") or "Not Detected", body_style)
        ],
        [
            Paragraph("<b>Location:</b>", body_style),
            Paragraph(p_info.get("location") or "Not Detected", body_style),
            Paragraph("<b>Job Match Score:</b>", body_style),
            Paragraph(f"{data.get('similarity_metrics', {}).get('overall_match', 'N/A')}%" if data.get('similarity_metrics') else "N/A (No JD Paste)", body_style)
        ]
    ]
    
    t_summary = Table(summary_data, colWidths=[100, 170, 100, 160])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_light),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TEXTCOLOR', (0,0), (-1,-1), text_color),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 15))
    
    # Component Score Breakdown
    story.append(Paragraph("ATS Score Breakdown", h1_style))
    breakdown = data.get("score_breakdown", {})
    breakdown_data = [[Paragraph("<b>Evaluation Metric</b>", body_bold), Paragraph("<b>Score Contribution</b>", body_bold)]]
    for metric, score in breakdown.items():
        metric_name = metric.replace("_", " ").title()
        breakdown_data.append([
            Paragraph(metric_name, body_style),
            Paragraph(f"{score}%", body_bold)
        ])
    t_breakdown = Table(breakdown_data, colWidths=[270, 260])
    t_breakdown.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), border_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_breakdown)
    story.append(Spacer(1, 15))
    
    # Job Description Matching Metrics (if exists)
    sim = data.get("similarity_metrics")
    if sim:
        story.append(Paragraph("Job Description Matching Metrics", h1_style))
        match_data = [
            [Paragraph("<b>Job Match Metric</b>", body_bold), Paragraph("<b>Match Level</b>", body_bold)],
            [Paragraph("Overall Job Match Score", body_style), Paragraph(f"<b>{sim.get('overall_match')}%</b>", body_style)],
            [Paragraph("Semantic Similarity (SentenceTransformers)", body_style), Paragraph(f"{sim.get('semantic_match')}%", body_style)],
            [Paragraph("TF-IDF Vector Similarity", body_style), Paragraph(f"{sim.get('tfidf_match')}%", body_style)],
            [Paragraph("Keyword Occurrences Overlap", body_style), Paragraph(f"{sim.get('keyword_match')}%", body_style)],
        ]
        t_match = Table(match_data, colWidths=[270, 260])
        t_match.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), border_color),
            ('BOX', (0,0), (-1,-1), 1, border_color),
            ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t_match)
        story.append(Spacer(1, 15))
        
        # Missing Skills
        missing = sim.get("missing_skills", [])
        matched = sim.get("matched_skills", [])
        if missing or matched:
            skills_block = []
            skills_block.append(Paragraph("Target Job Description Skills Analysis", h1_style))
            
            if matched:
                skills_block.append(Paragraph(f"<b>Matched Skills ({len(matched)}):</b> " + ", ".join(matched), body_style))
                skills_block.append(Spacer(1, 4))
            if missing:
                # color missing red
                skills_block.append(Paragraph(f"<b>Missing Skills ({len(missing)}):</b> <font color='red'>" + ", ".join(missing) + "</font>", body_style))
            
            story.append(KeepTogether(skills_block))
            story.append(Spacer(1, 15))

    # Extracted Resume Skills
    skills = data.get("skills", {})
    if any(skills.values()):
        story.append(Paragraph("Detected Resume Skills Taxonomy", h1_style))
        skills_data = []
        for cat, list_skills in skills.items():
            if list_skills:
                cat_name = cat.replace("_", " ").title()
                skills_data.append([
                    Paragraph(f"<b>{cat_name}</b>", body_style),
                    Paragraph(", ".join(list_skills), body_style)
                ])
        t_skills = Table(skills_data, colWidths=[130, 400])
        t_skills.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOX', (0,0), (-1,-1), 1, border_color),
            ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
            ('BACKGROUND', (0,0), (0,-1), bg_light),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t_skills)
        story.append(Spacer(1, 15))

    # ATS Checks / Warnings
    checks = data.get("ats_checks", [])
    if checks:
        checks_block = []
        checks_block.append(Paragraph("ATS System Compliance Audits", h1_style))
        
        # Sort checks by severity (HIGH -> MEDIUM -> LOW)
        severity_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        sorted_checks = sorted(checks, key=lambda x: severity_rank.get(x.get("severity"), 3))
        
        for c in sorted_checks:
            sev = c.get("severity")
            cat = c.get("category")
            exp = c.get("explanation")
            
            # Text coloring based on severity
            color_str = "red" if sev == "HIGH" else "orange" if sev == "MEDIUM" else "gray"
            bullet = f"• <b>[{cat}]</b> <font color='{color_str}'><b>{sev}</b></font>: {exp}"
            checks_block.append(Paragraph(bullet, bullet_style))
            
        story.append(KeepTogether(checks_block))
        story.append(Spacer(1, 15))

    # Recommendations
    recs = data.get("recommendations", [])
    if recs:
        recs_block = []
        recs_block.append(Paragraph("Actionable Improvement Guidelines", h1_style))
        for r in recs:
            recs_block.append(Paragraph(f"• {r}", bullet_style))
        story.append(KeepTogether(recs_block))
        
    # Build the document
    doc.build(story)
