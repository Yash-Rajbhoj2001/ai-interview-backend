from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO


def generate_report_pdf(report, interview):

    buffer = BytesIO()

    p = canvas.Canvas(buffer, pagesize=letter)

    y = 750

    # Title
    p.setFont("Helvetica-Bold", 20)
    p.drawString(180, y, "AI Interview Report")

    y -= 40

    p.setFont("Helvetica", 12)

    # Interview Info
    p.drawString(50, y, f"Session ID: {interview.id}")
    y -= 20
    p.drawString(50, y, f"Role: {interview.jd.role}")
    y -= 20
    p.drawString(50, y, f"Interview Type: {interview.interview_type}")
    y -= 20
    p.drawString(50, y, f"Date: {interview.created_at.strftime('%d/%m/%Y %H:%M')}")
    y -= 40

    # Scores
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Score Breakdown")
    y -= 20

    p.setFont("Helvetica", 12)
    p.drawString(60, y, f"Overall Score: {report.overall_score}%")
    y -= 20
    p.drawString(60, y, f"Technical Score: {report.technical_score}%")
    y -= 20
    p.drawString(60, y, f"Communication Score: {report.communication_score}%")
    y -= 40

    # Strengths
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Strengths")
    y -= 20

    p.setFont("Helvetica", 12)
    for line in report.strengths.split("\n"):
        p.drawString(60, y, f"- {line}")
        y -= 15

    y -= 20

    # Weaknesses
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Areas to Improve")
    y -= 20

    p.setFont("Helvetica", 12)
    for line in report.weaknesses.split("\n"):
        p.drawString(60, y, f"- {line}")
        y -= 15

    y -= 20

    # Suggestions
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Suggestions")
    y -= 20

    p.setFont("Helvetica", 12)
    for line in report.suggestions.split("\n"):
        p.drawString(60, y, f"- {line}")
        y -= 15

    p.save()

    buffer.seek(0)

    return buffer