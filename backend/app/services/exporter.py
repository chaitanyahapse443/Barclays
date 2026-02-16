from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

def sar_to_pdf_bytes(sar_text: str, case: dict = None) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    title = 'Suspicious Activity Report'
    story.append(Paragraph(title, styles['Title']))
    if case:
        story.append(Paragraph(f"Case ID: {case.get('case_id')}", styles['Normal']))
        story.append(Paragraph(f"Customer: {case.get('customer_name')}", styles['Normal']))
        story.append(Spacer(1, 12))
    for line in sar_text.split('\n'):
        story.append(Paragraph(line or ' ', styles['Normal']))
    doc.build(story)
    pdf = buf.getvalue()
    buf.close()
    return pdf
