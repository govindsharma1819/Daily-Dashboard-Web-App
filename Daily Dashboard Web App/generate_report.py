from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, ListFlowable, ListItem, PageBreak
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import os


def header_footer(canvas_obj, doc):
    canvas_obj.setFont("Helvetica", 9)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    canvas_obj.setFillColor(colors.grey)
    canvas_obj.drawString(2 * cm, 1.2 * cm, f"Generated: {timestamp}")
    canvas_obj.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas_obj.setFillColor(colors.black)


def draw_architecture_diagram(c):
    c.saveState()
    c.setStrokeColor(colors.HexColor("#444444"))
    c.setFillColor(colors.whitesmoke)

    # Coordinates and sizes
    left_margin = 2.0 * cm
    top = A4[1] - 3.0 * cm
    box_w = 6.0 * cm
    box_h = 1.6 * cm
    gap_x = 1.5 * cm
    gap_y = 1.6 * cm

    # Boxes: Browser → Flask App → Cache/DB/External APIs
    # Browser
    c.roundRect(left_margin, top, box_w, box_h, 8, stroke=1, fill=1)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.black)
    c.drawCentredString(left_margin + box_w / 2, top + box_h / 2 - 4, "Browser (UI)")

    # Flask App
    flask_x = left_margin + box_w + gap_x
    c.setFillColor(colors.whitesmoke)
    c.roundRect(flask_x, top, box_w, box_h, 8, stroke=1, fill=1)
    c.setFillColor(colors.black)
    c.drawCentredString(flask_x + box_w / 2, top + box_h / 2 - 4, "Flask App (Routing/API)")

    # Arrow Browser -> Flask
    c.setLineWidth(1.2)
    c.line(left_margin + box_w, top + box_h / 2, flask_x, top + box_h / 2)
    c.line(flask_x - 8, top + box_h / 2 + 4, flask_x, top + box_h / 2)
    c.line(flask_x - 8, top + box_h / 2 - 4, flask_x, top + box_h / 2)

    # Cache
    cache_y = top - box_h - gap_y
    c.setFillColor(colors.whitesmoke)
    c.roundRect(flask_x, cache_y, box_w, box_h, 8, stroke=1, fill=1)
    c.setFillColor(colors.black)
    c.drawCentredString(flask_x + box_w / 2, cache_y + box_h / 2 - 4, "In-memory Cache (TTL)")

    # DB (PostgreSQL / SQLite)
    db_x = left_margin
    db_y = cache_y
    c.setFillColor(colors.whitesmoke)
    c.roundRect(db_x, db_y, box_w, box_h, 8, stroke=1, fill=1)
    c.setFillColor(colors.black)
    c.drawCentredString(db_x + box_w / 2, db_y + box_h / 2 - 4, "DB: PostgreSQL → SQLite fallback")

    # External APIs
    api_x = flask_x + box_w + gap_x
    api_y = cache_y
    c.setFillColor(colors.whitesmoke)
    c.roundRect(api_x, api_y, box_w, box_h, 8, stroke=1, fill=1)
    c.setFillColor(colors.black)
    c.drawCentredString(api_x + box_w / 2, api_y + box_h / 2 - 4, "External APIs (Weather/News)")

    # Arrows from Flask to Cache/DB/APIs
    # Flask -> Cache
    c.line(flask_x + box_w / 2, top, flask_x + box_w / 2, cache_y + box_h)
    c.line(flask_x + box_w / 2 - 4, cache_y + box_h + 8, flask_x + box_w / 2, cache_y + box_h)
    c.line(flask_x + box_w / 2 + 4, cache_y + box_h + 8, flask_x + box_w / 2, cache_y + box_h)

    # Flask -> DB
    c.line(flask_x, top + box_h / 2, db_x + box_w, db_y + box_h / 2)
    c.line(db_x + box_w + 8, db_y + box_h / 2 + 4, db_x + box_w, db_y + box_h / 2)
    c.line(db_x + box_w + 8, db_y + box_h / 2 - 4, db_x + box_w, db_y + box_h / 2)

    # Flask -> External APIs
    c.line(flask_x + box_w, top + box_h / 2, api_x, api_y + box_h / 2)
    c.line(api_x - 8, api_y + box_h / 2 + 4, api_x, api_y + box_h / 2)
    c.line(api_x - 8, api_y + box_h / 2 - 4, api_x, api_y + box_h / 2)

    # Captions
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawCentredString(flask_x + box_w / 2, cache_y - 12, "Caching reduces API/DB load; TTL from env")

    c.restoreState()


def make_paragraph(text, style):
    return Paragraph(text, style)


def build_pdf(output_path):
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    title_style.alignment = TA_CENTER
    h_style = styles["Heading2"]
    body = styles["BodyText"]

    elements = []

    # Cover Page
    elements.append(Paragraph("Daily Dashboard - Project Presentation", title_style))
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(Paragraph("Flask-based dashboard for Stocks, Weather, and News", body))
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body))
    elements.append(PageBreak())

    # Executive Overview
    elements.append(Paragraph("Executive Overview", h_style))
    elements.append(Spacer(1, 0.2 * cm))
    overview_items = [
        "Flask app with session auth and three data modules (Stocks, Weather, News)",
        "Responsive UI with Bootstrap and clean templates",
        "Environment-driven config; mock data enabled without API keys",
        "DB strategy: PostgreSQL preferred → SQLite fallback → in-memory last resort",
    ]
    elements.append(ListFlowable([ListItem(make_paragraph(i, body)) for i in overview_items], bulletType='bullet'))
    elements.append(PageBreak())

    # Architecture Page with Diagram
    elements.append(Paragraph("Architecture Overview", h_style))
    elements.append(Spacer(1, 0.3 * cm))
    arch_points = [
        "Frontend: Bootstrap 5, icons, modular pages (login/register/dashboard)",
        "Backend: Flask routes, session management, cache, API endpoints",
        "Data: PostgreSQL primary, SQLite fallback, mock-friendly APIs",
        "Caching: In-memory TTL cache per data domain",
    ]
    elements.append(ListFlowable([ListItem(make_paragraph(i, body)) for i in arch_points], bulletType='bullet'))

    def diagram_canvas(canv, doc):
        header_footer(canv, doc)
        draw_architecture_diagram(canv)

    doc = SimpleDocTemplate(output_path, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm)

    # Custom onPage to place diagram for this page only
    def on_first_page(canv, doc):
        header_footer(canv, doc)

    # Build in two steps to insert a diagram page hook
    doc.build(elements, onFirstPage=on_first_page, onLaterPages=on_first_page, canvasmaker=None)

    # Create a second pass to actually draw the diagram: use a direct canvas on same file
    c = canvas.Canvas(output_path, pagesize=A4)

    # Re-render the pages: cover + overview already exist; now add diagram page
    # Instead, we will fully regenerate in a single pass with manual pages for precise placement
    c.setTitle("Daily Dashboard - Presentation")

    # Manual Cover
    header_footer(c, type("D", (), {"page": 1}))
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(A4[0] / 2, A4[1] - 5 * cm, "Daily Dashboard - Project Presentation")
    c.setFont("Helvetica", 12)
    c.drawCentredString(A4[0] / 2, A4[1] - 6 * cm, "Flask-based dashboard for Stocks, Weather, and News")
    c.drawCentredString(A4[0] / 2, A4[1] - 7 * cm, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.showPage()

    # Manual Overview
    header_footer(c, type("D", (), {"page": 2}))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, A4[1] - 3 * cm, "Executive Overview")
    c.setFont("Helvetica", 12)
    y = A4[1] - 4 * cm
    for item in overview_items:
        c.circle(2 * cm, y + 3, 1.2)
        c.drawString(2.6 * cm, y, item)
        y -= 1.0 * cm
    c.showPage()

    # Manual Architecture + Diagram
    header_footer(c, type("D", (), {"page": 3}))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, A4[1] - 3 * cm, "Architecture Overview")
    c.setFont("Helvetica", 12)
    y = A4[1] - 4 * cm
    for item in arch_points:
        c.circle(2 * cm, y + 3, 1.2)
        c.drawString(2.6 * cm, y, item)
        y -= 0.9 * cm

    draw_architecture_diagram(c)
    c.showPage()

    # Modules & Endpoints
    header_footer(c, type("D", (), {"page": 4}))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, A4[1] - 3 * cm, "Modules & Endpoints")
    c.setFont("Helvetica", 12)
    y = A4[1] - 4 * cm
    sections = [
        ("Auth", ["/login (GET, POST)", "/register (GET, POST)", "/logout (GET)", "/dashboard (GET, protected)"]),
        ("APIs (protected)", ["/api/stocks (GET)", "/api/weather?location=... (GET)", "/api/news (GET)"]),
    ]
    for section, items in sections:
        c.setFont("Helvetica-Bold", 13)
        c.drawString(2 * cm, y, section)
        y -= 0.8 * cm
        c.setFont("Helvetica", 12)
        for it in items:
            c.circle(2 * cm, y + 3, 1.2)
            c.drawString(2.6 * cm, y, it)
            y -= 0.7 * cm
        y -= 0.4 * cm
    c.showPage()

    # Security & Roadmap
    header_footer(c, type("D", (), {"page": 5}))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, A4[1] - 3 * cm, "Security, Risks & Roadmap")
    y = A4[1] - 4 * cm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(2 * cm, y, "Security")
    y -= 0.8 * cm
    c.setFont("Helvetica", 12)
    for it in [
        "Hashed passwords (Werkzeug), session idle timeout (30 min)",
        "Login-required decorator on data endpoints",
    ]:
        c.circle(2 * cm, y + 3, 1.2)
        c.drawString(2.6 * cm, y, it)
        y -= 0.7 * cm
    y -= 0.4 * cm

    c.setFont("Helvetica-Bold", 13)
    c.drawString(2 * cm, y, "Gaps & Risks")
    y -= 0.8 * cm
    c.setFont("Helvetica", 12)
    for it in [
        "Docs mention MySQL; code uses PostgreSQL/SQLite → update docs",
        "No rate limiting; consider Flask-Limiter",
        "Client-side sessions; consider Redis server-side sessions",
    ]:
        c.circle(2 * cm, y + 3, 1.2)
        c.drawString(2.6 * cm, y, it)
        y -= 0.7 * cm
    y -= 0.4 * cm

    c.setFont("Helvetica-Bold", 13)
    c.drawString(2 * cm, y, "Roadmap")
    y -= 0.8 * cm
    c.setFont("Helvetica", 12)
    for it in [
        "Wire real APIs (OpenWeatherMap, NewsAPI) with backoff handling",
        "Add user preferences (default location, refresh interval)",
        "Observability: structured logs, metrics, health endpoints",
        "Deployment hardening: Gunicorn, HTTPS, CSRF, security headers",
    ]:
        c.circle(2 * cm, y + 3, 1.2)
        c.drawString(2.6 * cm, y, it)
        y -= 0.7 * cm

    c.showPage()
    c.save()


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(__file__), "report")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "Daily_Dashboard_Presentation.pdf")
    build_pdf(output_file)
    print(f"PDF generated at: {output_file}")
