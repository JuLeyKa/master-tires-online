import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import urllib.parse
import io
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Page Config
st.set_page_config(
    page_title="Warenkorb - Ramsperger",
    page_icon="🛒",
    layout="wide"
)

# ================================================================================================
# CSS STYLES - DIREKT EINGEBETTET
# ================================================================================================
MAIN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-color: #0ea5e9;
        --primary-dark: #0284c7;
        --secondary-color: #64748b;
        --success-color: #16a34a;
        --warning-color: #f59e0b;
        --error-color: #dc2626;
        --background-light: #f8fafc;
        --background-white: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border-color: #e2e8f0;
        --border-radius: 8px;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    }

    .main > div {
        padding-top: 1rem;
    }

    .main-header {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-lg);
    }

    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
    }

    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }

    .cart-container {
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid var(--primary-color);
        box-shadow: var(--shadow-md);
    }

    .cart-item {
        background: var(--background-white);
        padding: 1rem;
        border-radius: var(--border-radius);
        margin: 0.5rem 0;
        border-left: 4px solid var(--primary-color);
        box-shadow: var(--shadow-sm);
        transition: transform 0.1s ease;
    }

    .cart-item:hover {
        transform: translateX(4px);
    }

    .total-box {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid var(--success-color);
        box-shadow: var(--shadow-md);
    }

    .info-box {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        padding: 1rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--success-color);
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
    }

    .warning-box {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        padding: 1rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--warning-color);
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
    }

    .scenario-box {
        background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
        padding: 1rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--secondary-color);
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
    }

    .saison-info-box {
        background: linear-gradient(135deg, #e0f2fe, #bae6fd);
        padding: 1rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--primary-color);
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
    }

    .email-options-box {
        background: linear-gradient(135deg, #f8fafc, #e2e8f0);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid var(--secondary-color);
        box-shadow: var(--shadow-md);
    }

    .stButton > button {
        border-radius: var(--border-radius);
        border: none;
        font-weight: 500;
        transition: all 0.2s ease;
        font-family: 'Inter', sans-serif;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
</style>
"""
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# ================================================================================================
# HELPER FUNCTIONS (APP)
# ================================================================================================
def get_efficiency_emoji(rating):
    if pd.isna(rating):
        return ""
    rating = str(rating).strip().upper()[:1]
    return {"A":"[A]","B":"[B]","C":"[C]","D":"[D]","E":"[E]","F":"[F]","G":"[G]"}.get(rating, "")

def get_stock_display(stock_value):
    if pd.isna(stock_value) or stock_value == '':
        return "unbekannt"
    try:
        stock_num = float(stock_value)
        if stock_num < 0: return f"NACHBESTELLEN ({int(stock_num)})"
        if stock_num == 0: return f"AUSVERKAUFT ({int(stock_num)})"
        return f"VERFÜGBAR ({int(stock_num)})"
    except:
        return "unbekannt"

def init_default_services():
    services_data = {
        'service_name': ['montage_bis_17','montage_18_19','montage_ab_20',
                         'radwechsel_1_rad','radwechsel_2_raeder','radwechsel_3_raeder',
                         'radwechsel_4_raeder','nur_einlagerung'],
        'service_label': ['Montage bis 17 Zoll','Montage 18-19 Zoll','Montage ab 20 Zoll',
                          'Radwechsel 1 Rad','Radwechsel 2 Räder','Radwechsel 3 Räder',
                          'Radwechsel 4 Räder','Nur Einlagerung'],
        'price': [25.0,30.0,40.0,9.95,19.95,29.95,39.90,55.00],
        'unit': ['pro Reifen','pro Reifen','pro Reifen','pauschal','pauschal','pauschal','pauschal','pauschal']
    }
    return pd.DataFrame(services_data)

def get_service_prices():
    if 'services_config' not in st.session_state:
        st.session_state.services_config = init_default_services()
    prices = {}
    for _, row in st.session_state.services_config.iterrows():
        prices[row['service_name']] = row['price']
    return prices

# ---------------------- Saison-Erkennung ----------------------
def detect_cart_season():
    if not st.session_state.cart_items:
        return "neutral"
    saison_counts = {"Winter":0,"Sommer":0,"Ganzjahres":0,"Unbekannt":0}
    for item in st.session_state.cart_items:
        saison_counts[item.get('Saison','Unbekannt')] = saison_counts.get(item.get('Saison','Unbekannt'),0) + 1
    total_items = sum(saison_counts.values())
    if total_items == 0: return "neutral"
    dominant_season, dominant_count = sorted(saison_counts.items(), key=lambda x: x[1], reverse=True)[0]
    return dominant_season.lower() if dominant_count/total_items >= 0.7 else "gemischt"

def get_season_greeting_text(detected_season):
    season_texts = {
        "winter": {"greeting":"der Winter steht vor der Tür und die Zeichen stehen auf kälter werdende Temperaturen.",
                   "transition":"Jetzt wird es auch Zeit für Ihre Winterreifen von Ihrem Auto.","season_name":"Winter"},
        "sommer": {"greeting":"die warme Jahreszeit kommt und die Temperaturen steigen wieder.",
                   "transition":"Jetzt wird es auch Zeit für Ihre Sommerreifen von Ihrem Auto.","season_name":"Sommer"},
        "ganzjahres":{"greeting":"Sie denken über Ganzjahresreifen nach - eine praktische Lösung für das ganze Jahr.",
                      "transition":"Jetzt wird es Zeit für Ihre neuen Allwetter-Reifen von Ihrem Auto.","season_name":"Ganzjahres"},
        "gemischt":{"greeting":"Sie haben verschiedene Reifen-Optionen für unterschiedliche Anforderungen.",
                    "transition":"Gerne stelle ich Ihnen die verschiedenen Möglichkeiten vor.","season_name":"verschiedene"},
        "neutral":{"greeting":"Sie interessieren sich für neue Reifen für Ihr Fahrzeug.",
                   "transition":"Gerne stelle ich Ihnen die passenden Optionen vor.","season_name":"neue"}
    }
    return season_texts.get(detected_season, season_texts["neutral"])

# ---------------------- Cart Ops ----------------------
def remove_from_cart(tire_id):
    st.session_state.cart_items = [item for item in st.session_state.cart_items if item['id'] != tire_id]
    st.session_state.cart_quantities.pop(tire_id, None)
    st.session_state.cart_services.pop(tire_id, None)
    _clear_item_widget_keys(tire_id)
    st.session_state.cart_count = len(st.session_state.cart_items)

def clear_cart():
    for item in list(st.session_state.cart_items):
        _clear_item_widget_keys(item['id'])
    st.session_state.cart_items = []
    st.session_state.cart_quantities = {}
    st.session_state.cart_services = {}
    st.session_state.cart_count = 0

def calculate_position_total(item):
    tire_id = item['id']
    quantity = st.session_state.cart_quantities.get(tire_id, 4)
    service_prices = get_service_prices()

    reifen_kosten = item['Preis_EUR'] * quantity
    item_services = st.session_state.cart_services.get(tire_id, {})
    service_kosten = 0.0

    if item_services.get('montage', False):
        z = item['Zoll']
        montage_preis = (service_prices.get('montage_bis_17',25.0) if z<=17
                         else service_prices.get('montage_18_19',30.0) if z<=19
                         else service_prices.get('montage_ab_20',40.0))
        service_kosten += montage_preis * quantity

    if item_services.get('radwechsel', False):
        t = item_services.get('radwechsel_type','4_raeder')
        service_kosten += {
            '1_rad': service_prices.get('radwechsel_1_rad',9.95),
            '2_raeder': service_prices.get('radwechsel_2_raeder',19.95),
            '3_raeder': service_prices.get('radwechsel_3_raeder',29.95),
            '4_raeder': service_prices.get('radwechsel_4_raeder',39.90)
        }.get(t, service_prices.get('radwechsel_4_raeder',39.90))

    if item_services.get('einlagerung', False):
        service_kosten += service_prices.get('nur_einlagerung',55.00)

    return reifen_kosten, service_kosten, reifen_kosten + service_kosten

def get_cart_total():
    total = 0.0
    breakdown = {'reifen':0.0,'montage':0.0,'radwechsel':0.0,'einlagerung':0.0}
    sp = get_service_prices()

    for item in st.session_state.cart_items:
        reifen_kosten, service_kosten, position_total = calculate_position_total(item)
        total += position_total
        breakdown['reifen'] += reifen_kosten

        item_services = st.session_state.cart_services.get(item['id'], {})
        qty = st.session_state.cart_quantities.get(item['id'], 4)

        if item_services.get('montage', False):
            z = item['Zoll']
            mp = (sp.get('montage_bis_17',25.0) if z<=17 else sp.get('montage_18_19',30.0) if z<=19 else sp.get('montage_ab_20',40.0))
            breakdown['montage'] += mp * qty

        if item_services.get('radwechsel', False):
            t = item_services.get('radwechsel_type','4_raeder')
            breakdown['radwechsel'] += {
                '1_rad': sp.get('radwechsel_1_rad',9.95),
                '2_raeder': sp.get('radwechsel_2_raeder',19.95),
                '3_raeder': sp.get('radwechsel_3_raeder',29.95),
                '4_raeder': sp.get('radwechsel_4_raeder',39.90)
            }.get(t, sp.get('radwechsel_4_raeder',39.90))

        if item_services.get('einlagerung', False):
            breakdown['einlagerung'] += sp.get('nur_einlagerung',55.00)

    return total, breakdown

# ================================================================================================
# PDF GENERATION (SCHÖN & PROFESSIONELL)
# ================================================================================================
def format_eur(value: float) -> str:
    s = f"{value:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €"

def _header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    margin = 2 * cm

    canvas.setFillColor(colors.HexColor("#0ea5e9"))
    canvas.rect(margin, height - margin + 6, width - 2*margin, 2, fill=1, stroke=0)

    canvas.setFont("Helvetica-Bold", 11)
    canvas.setFillColor(colors.HexColor("#1e293b"))
    canvas.drawRightString(width - margin, height - margin + 14, "AUTOHAUS RAMSPERGER")
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawRightString(width - margin, height - margin - 2, "Reifen • Service • Einlagerung")

    canvas.setFillColor(colors.HexColor("#e2e8f0"))
    canvas.rect(margin, margin - 8, width - 2*margin, 1, fill=1, stroke=0)

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    left_text = "Autohaus Ramsperger • Musterstraße 1 • 73033 Göppingen • Tel. 07161 00000 • service@ramsperger.de"
    canvas.drawString(margin, margin - 18, left_text)
    canvas.drawRightString(width - margin, margin - 18, f"Seite {doc.page}")
    canvas.restoreState()

def create_professional_pdf(customer_data=None, offer_scenario="vergleich", detected_season="neutral"):
    if not st.session_state.cart_items:
        return None

    total, breakdown = get_cart_total()
    season_info = get_season_greeting_text(detected_season)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=28*mm,
        bottomMargin=25*mm
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle('H1', parent=styles['Heading1'],
                        fontSize=20, leading=24, spaceAfter=12,
                        textColor=colors.HexColor('#0ea5e9'),
                        alignment=TA_LEFT)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'],
                        fontSize=14, leading=18, spaceAfter=8,
                        textColor=colors.HexColor('#1e293b'),
                        alignment=TA_LEFT)
    normal = ParagraphStyle('NormalPlus', parent=styles['Normal'],
                            fontSize=10.5, leading=14, textColor=colors.HexColor('#1e293b'))
    small = ParagraphStyle('Small', parent=styles['Normal'],
                           fontSize=9, leading=12, textColor=colors.HexColor('#64748b'))

    story = []

    date_str = datetime.now().strftime('%d.%m.%Y')
    offer_number = f"RRS-{datetime.now().strftime('%Y%m%d')}-{len(st.session_state.cart_items):03d}"

    story.append(Paragraph("Angebot Reifen & Service", h1))
    meta_tbl = Table([
        ["Datum:", date_str, "Angebotsnummer:", offer_number],
        ["Saison:", season_info['season_name'], "", ""]
    ], colWidths=[2.5*cm, 5.5*cm, 3.5*cm, 4*cm])
    meta_tbl.setStyle(TableStyle([
        ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
        ('FONTSIZE',(0,0),(-1,-1),9.5),
        ('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor('#1e293b')),
        ('ALIGN',(0,0),(0,-1),'RIGHT'),
        ('ALIGN',(2,0),(2,0),'RIGHT'),
        ('BOTTOMPADDING',(0,0),(-1,-1),4),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 6))

    if customer_data and any(customer_data.values()):
        cust_rows = []
        if customer_data.get('name'): cust_rows.append(["Kunde:", customer_data['name']])
        if customer_data.get('email'): cust_rows.append(["E-Mail:", customer_data['email']])
        if customer_data.get('kennzeichen'): cust_rows.append(["Kennzeichen:", customer_data['kennzeichen']])
        if customer_data.get('modell'): cust_rows.append(["Fahrzeug:", customer_data['modell']])
        if customer_data.get('fahrgestellnummer'): cust_rows.append(["Fahrgestellnr.:", customer_data['fahrgestellnummer']])

        if cust_rows:
            story.append(Paragraph("Kundendaten", h2))
            cust_tbl = Table(cust_rows, colWidths=[3.5*cm, 12.5*cm])
            cust_tbl.setStyle(TableStyle([
                ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
                ('FONTSIZE',(0,0),(-1,-1),9.5),
                ('ALIGN',(0,0),(0,-1),'RIGHT'),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('BOTTOMPADDING',(0,0),(-1,-1),3),
            ]))
            story.append(cust_tbl)
            story.append(Spacer(1, 8))

    intro_text = (
        f"Sehr geehrte Damen und Herren,<br/>"
        f"{season_info['greeting']} {season_info['transition']} "
        f"Nachfolgend erhalten Sie Ihr individuelles Angebot."
    )
    story.append(Paragraph(intro_text, normal))
    story.append(Spacer(1, 12))

    scenario_headers = {
        "vergleich": "Ihre Reifenoptionen zur Auswahl",
        "separate": "Angebot für Ihre Fahrzeuge",
        "einzelangebot": "Ihr individuelles Reifenangebot"
    }
    story.append(Paragraph(scenario_headers.get(offer_scenario, "Ihr Reifenangebot"), h2))
    story.append(Spacer(1, 4))

    table_data = [['Pos.', 'Reifengröße', 'Marke', 'Profil', 'Stück', 'Einzelpreis', 'Services', 'Gesamtpreis']]
    for i, item in enumerate(st.session_state.cart_items, 1):
        reifen_kosten, service_kosten, position_total = calculate_position_total(item)
        quantity = st.session_state.cart_quantities.get(item['id'], 4)

        item_services = st.session_state.cart_services.get(item['id'], {})
        svc_parts = []
        if item_services.get('montage', False):
            svc_parts.append("Montage")
        if item_services.get('radwechsel', False):
            type_map = {'1_rad':'1 Rad','2_raeder': '2 Räder','3_raeder':'3 Räder','4_raeder':'4 Räder'}
            svc_parts.append(f"Radwechsel {type_map.get(item_services.get('radwechsel_type','4_raeder'),'4 Räder')}")
        if item_services.get('einlagerung', False):
            svc_parts.append("Einlagerung")
        services_text = ", ".join(svc_parts) if svc_parts else "Keine"

        table_data.append([
            str(i),
            item['Reifengröße'],
            item['Fabrikat'],
            item['Profil'],
            f"{quantity}x",
            format_eur(item['Preis_EUR']),
            services_text,
            format_eur(position_total)
        ])

    col_widths = [1.1*cm, 3.2*cm, 2.6*cm, 4.2*cm, 1.6*cm, 2.8*cm, 3.4*cm, 3.0*cm]
    reifen_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    reifen_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0ea5e9')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9.5),
        ('ALIGN', (0,1), (0,-1), 'CENTER'),
        ('ALIGN', (4,1), (4,-1), 'CENTER'),
        ('ALIGN', (5,1), (5,-1), 'RIGHT'),
        ('ALIGN', (7,1), (7,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#e2e8f0')),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(KeepTogether(reifen_table))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Kostenaufstellung", h2))
    cost_rows = [['Reifen-Kosten:', format_eur(breakdown['reifen'])]]
    if breakdown['montage'] > 0:
        cost_rows.append(['Montage-Service:', format_eur(breakdown['montage'])])
    if breakdown['radwechsel'] > 0:
        cost_rows.append(['Radwechsel-Service:', format_eur(breakdown['radwechsel'])])
    if breakdown['einlagerung'] > 0:
        cost_rows.append(['Einlagerung:', format_eur(breakdown['einlagerung'])])

    cost_rows.append(['', ''])
    cost_rows.append(['GESAMTSUMME:', format_eur(total)])

    cost_tbl = Table(cost_rows, colWidths=[10.2*cm, 4.0*cm])
    cost_tbl.setStyle(TableStyle([
        ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
        ('FONTSIZE',(0,0),(-1,-2),10.5),
        ('ALIGN',(0,0),(0,-1),'RIGHT'),
        ('ALIGN',(1,0),(1,-1),'RIGHT'),
        ('TEXTCOLOR',(0,0),(-1,-2),colors.HexColor('#1e293b')),
        ('LINEBELOW',(0,-2),(-1,-2), 1, colors.HexColor('#e2e8f0')),
        ('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold'),
        ('FONTSIZE',(0,-1),(-1,-1),13),
        ('BACKGROUND',(0,-1),(-1,-1), colors.HexColor('#f0fdf4')),
        ('TEXTCOLOR',(0,-1),(-1,-1), colors.HexColor('#166534')),
        ('TOPPADDING',(0,0),(-1,-1),6),
        ('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),6),
        ('RIGHTPADDING',(0,0),(-1,-1),6),
    ]))
    story.append(KeepTogether(cost_tbl))
    story.append(Spacer(1, 10))

    bullets = []
    if detected_season == "winter":
        bullets.append("Wir empfehlen den rechtzeitigen Wechsel auf Winterreifen für optimale Sicherheit bei winterlichen Bedingungen.")
    elif detected_season == "sommer":
        bullets.append("Sommerreifen bieten optimalen Grip und Fahrkomfort bei warmen Temperaturen und trockenen Straßen.")
    elif detected_season == "ganzjahres":
        bullets.append("Ganzjahresreifen sind eine praktische Lösung für das ganze Jahr ohne saisonalen Wechsel.")
    bullets.extend([
        "Alle Preise verstehen sich inklusive der gewählten Service-Leistungen.",
        "Montage und Service werden von unseren Fachkräften durchgeführt.",
        "Für Rückfragen stehen wir Ihnen gerne zur Verfügung."
    ])
    for b in bullets:
        story.append(Paragraph(f"• {b}", normal))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Vielen Dank für Ihr Vertrauen!", h2))
    story.append(Paragraph("Ihr Team vom Autohaus Ramsperger", normal))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Hinweis: Dieses Angebot ist freibleibend. Verfügbarkeit abhängig vom Lagerbestand.", small))

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    buffer.seek(0)
    return buffer.getvalue()

# ================================================================================================
# E-MAIL TEXT & LINKS (OUTLOOK-DESKTOP-SICHER + OWA + GMAIL)
# ================================================================================================
_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def _normalize_crlf(text: str) -> str:
    if text is None:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.replace("\n", "\r\n")

def _urlencode_mail_body(text: str) -> str:
    return urllib.parse.quote(text, safe="")

def _valid_email(addr: str) -> bool:
    return bool(_EMAIL_REGEX.match(addr or ""))

def create_email_text(customer_data=None, detected_season="neutral"):
    season_info = get_season_greeting_text(detected_season)
    email_content = (
        "Sehr geehrte Damen und Herren,\n\n"
        f"anbei sende ich Ihnen Ihr Reifenangebot für {season_info['season_name']}-Reifen.\n\n"
        "Alle Details finden Sie im angehängten PDF-Dokument.\n\n"
        "Bei Fragen stehen wir Ihnen gerne zur Verfügung.\n\n"
        "Mit freundlichen Grüßen\n"
        "Autohaus Ramsperger"
    )
    return email_content

def create_mailto_link(customer_email, email_text, detected_season):
    if not customer_email or not _valid_email(customer_email.strip()):
        return None
    season_info = get_season_greeting_text(detected_season)
    subject = f"Ihr Reifenangebot von Autohaus Ramsperger - {season_info['season_name']}-Reifen"
    body_crlf = _normalize_crlf(email_text)
    subject_encoded = urllib.parse.quote(subject, safe="")
    body_encoded = _urlencode_mail_body(body_crlf)
    to_addr = customer_email.strip()
    return f"mailto:{to_addr}?subject={subject_encoded}&body={body_encoded}"

# ================================================================================================
# SESSION STATE INITIALISIERUNG
# ================================================================================================
def init_session_state():
    if 'customer_data' not in st.session_state:
        st.session_state.customer_data = {'name':'','email':'','kennzeichen':'','modell':'','fahrgestellnummer':''}

    if 'cart_items' not in st.session_state: st.session_state.cart_items = []
    if 'cart_quantities' not in st.session_state: st.session_state.cart_quantities = {}
    if 'cart_services' not in st.session_state: st.session_state.cart_services = {}
    if 'cart_count' not in st.session_state: st.session_state.cart_count = 0

    if 'offer_scenario' not in st.session_state:
        st.session_state.offer_scenario = "vergleich"

    if 'show_email_options' not in st.session_state:
        st.session_state.show_email_options = False

    if 'pdf_created' not in st.session_state:
        st.session_state.pdf_created = False

    st.session_state.setdefault('customer_name', st.session_state.customer_data.get('name',''))
    st.session_state.setdefault('customer_email', st.session_state.customer_data.get('email',''))
    st.session_state.setdefault('customer_kennzeichen', st.session_state.customer_data.get('kennzeichen',''))
    st.session_state.setdefault('customer_modell', st.session_state.customer_data.get('modell',''))
    st.session_state.setdefault('customer_fahrgestell', st.session_state.customer_data.get('fahrgestellnummer',''))

# ================================================================================================
# INTERNAL UTILITIES FOR WIDGET-STATE
# ================================================================================================
def _ensure_item_defaults(item_id):
    st.session_state.setdefault(f"qty_{item_id}", st.session_state.cart_quantities.get(item_id, 4))
    st.session_state.cart_services.setdefault(item_id, {'montage':False,'radwechsel':False,'radwechsel_type':'4_raeder','einlagerung':False})

    cs = st.session_state.cart_services[item_id]
    st.session_state.setdefault(f"montage_{item_id}", cs.get('montage', False))
    st.session_state.setdefault(f"radwechsel_{item_id}", cs.get('radwechsel', False))
    st.session_state.setdefault(f"cart_radwechsel_type_{item_id}", cs.get('radwechsel_type', '4_raeder'))
    st.session_state.setdefault(f"einlagerung_{item_id}", cs.get('einlagerung', False))

def _update_qty(item_id):
    st.session_state.cart_quantities[item_id] = st.session_state.get(f"qty_{item_id}", 4)

def _update_service(item_id, field):
    st.session_state.cart_services.setdefault(item_id, {})
    st.session_state.cart_services[item_id][field] = st.session_state.get(f"{field}_{item_id}", False)

def _update_radwechsel_type(item_id):
    st.session_state.cart_services.setdefault(item_id, {})
    st.session_state.cart_services[item_id]['radwechsel_type'] = st.session_state.get(f"cart_radwechsel_type_{item_id}", '4_raeder')

def _clear_item_widget_keys(item_id):
    for key in [f"qty_{item_id}", f"montage_{item_id}", f"radwechsel_{item_id}", f"cart_radwechsel_type_{item_id}", f"einlagerung_{item_id}"]:
        st.session_state.pop(key, None)

# ================================================================================================
# RENDER FUNCTIONS
# ================================================================================================
def render_empty_cart():
    st.markdown("""
    <div class="cart-container">
        <h3>Der Warenkorb ist leer</h3>
        <p>Gehe zur <strong>Reifen Suche</strong> und wähle Reifen für dein Angebot aus.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Zur Reifen Suche", use_container_width=True, type="primary"):
        st.switch_page("pages/01_Reifen_Suche.py")

def render_cart_content():
    st.markdown("#### Reifen im Warenkorb")
    for i, item in enumerate(st.session_state.cart_items, 1):
        render_cart_item(item, i)

def render_cart_item(item, position_number):
    st.markdown('<div class="cart-item">', unsafe_allow_html=True)
    st.markdown(f"### Position {position_number}")

    item_id = item['id']
    _ensure_item_defaults(item_id)

    col_info, col_qty, col_services, col_remove = st.columns([3, 1, 2, 1])

    with col_info:
        st.markdown(f"**{item['Reifengröße']}** - {item['Fabrikat']} {item['Profil']}")
        st.markdown(f"Teilenummer: {item['Teilenummer']} | Einzelpreis: **{item['Preis_EUR']:.2f}EUR**")
        effi = f" {get_efficiency_emoji(item['Kraftstoffeffizienz'])}{item['Kraftstoffeffizienz']}" if item.get('Kraftstoffeffizienz') else ""
        nass = f" {get_efficiency_emoji(item['Nasshaftung'])}{item['Nasshaftung']}" if item.get('Nasshaftung') else ""
        best = f" | {get_stock_display(item.get('Bestand'))}"
        saz  = f" | Saison: {item.get('Saison','Unbekannt')}"
        st.markdown(f"EU-Label:{effi}{nass}{best}{saz}")

    with col_qty:
        st.number_input("Stückzahl:", 1, 8,
                        key=f"qty_{item_id}",
                        on_change=_update_qty, args=(item_id,))

    with col_services:
        render_item_services(item)

    with col_remove:
        if st.button("Entfernen", key=f"remove_{item_id}", help="Aus Warenkorb entfernen"):
            remove_from_cart(item_id)
            st.rerun()

    reifen_kosten, service_kosten, position_total = calculate_position_total(item)
    st.markdown(f"### **Position {position_number} Gesamt: {position_total:.2f} EUR**")
    st.markdown(f"Reifen: {reifen_kosten:.2f}EUR + Services: {service_kosten:.2f}EUR")

    st.markdown('</div>', unsafe_allow_html=True)

def render_item_services(item):
    item_id = item['id']
    _ensure_item_defaults(item_id)
    sp = get_service_prices()

    st.markdown("**Services:**")

    z = item['Zoll']
    montage_price = (sp.get('montage_bis_17',25.0) if z<=17 else sp.get('montage_18_19',30.0) if z<=19 else sp.get('montage_ab_20',40.0))
    montage_label = f"Montage ({montage_price:.2f}EUR/Stk)"
    st.checkbox(montage_label, key=f"montage_{item_id}",
                on_change=_update_service, args=(item_id,'montage'))

    st.checkbox("Radwechsel", key=f"radwechsel_{item_id}",
                on_change=_update_service, args=(item_id,'radwechsel'))

    if st.session_state.get(f"radwechsel_{item_id}", False):
        options = [
            ('4_raeder', f"4 Räder ({sp.get('radwechsel_4_raeder',39.90):.2f}EUR)"),
            ('3_raeder', f"3 Räder ({sp.get('radwechsel_3_raeder',29.95):.2f}EUR)"),
            ('2_raeder', f"2 Räder ({sp.get('radwechsel_2_raeder',19.95):.2f}EUR)"),
            ('1_rad',   f"1 Rad ({sp.get('radwechsel_1_rad',9.95):.2f}EUR)")
        ]
        st.selectbox("Anzahl:", options=[k for k,_ in options],
                     format_func=lambda x: next(lbl for k,lbl in options if k==x),
                     key=f"cart_radwechsel_type_{item_id}",
                     on_change=_update_radwechsel_type, args=(item_id,))

    st.checkbox(f"Einlagerung ({sp.get('nur_einlagerung',55.00):.2f}EUR)",
                key=f"einlagerung_{item_id}",
                on_change=_update_service, args=(item_id,'einlagerung'))

def render_price_summary(total, breakdown):
    st.markdown("---")
    st.markdown('<div class="total-box">', unsafe_allow_html=True)
    st.markdown("#### Preisübersicht")
    col_breakdown, col_total = st.columns([2, 1])
    with col_breakdown:
        st.markdown(f"**Reifen-Kosten:** {breakdown['reifen']:.2f}EUR")
        if breakdown['montage']>0: st.markdown(f"**Montage:** {breakdown['montage']:.2f}EUR")
        if breakdown['radwechsel']>0: st.markdown(f"**Radwechsel:** {breakdown['radwechsel']:.2f}EUR")
        if breakdown['einlagerung']>0: st.markdown(f"**Einlagerung:** {breakdown['einlagerung']:.2f}EUR")
    with col_total:
        st.markdown(f"### **GESAMT: {total:.2f}EUR**")
    st.markdown('</div>', unsafe_allow_html=True)

def render_customer_data():
    st.markdown("---")
    st.markdown("#### Kundendaten (optional)")
    st.markdown("Diese Angaben werden in das Angebot aufgenommen, falls gewünscht:")

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Kundenname:", key="customer_name", placeholder="z.B. Max Mustermann")
        st.text_input("E-Mail-Adresse:", key="customer_email", placeholder="z.B. max@mustermann.de", help="Für den E-Mail-Versand des Angebots")
        st.text_input("Kennzeichen:", key="customer_kennzeichen", placeholder="z.B. GP-AB 123")
    with col2:
        st.text_input("Fahrzeugmodell:", key="customer_modell", placeholder="z.B. BMW 3er E90")
        st.text_input("Fahrgestellnummer:", key="customer_fahrgestell", placeholder="z.B. WBAVA31070F123456")

    st.session_state.customer_data = {
        'name': st.session_state.get('customer_name',''),
        'email': st.session_state.get('customer_email',''),
        'kennzeichen': st.session_state.get('customer_kennzeichen',''),
        'modell': st.session_state.get('customer_modell',''),
        'fahrgestellnummer': st.session_state.get('customer_fahrgestell','')
    }

def render_scenario_selection():
    st.markdown("---")
    st.markdown("#### Angebot-Typ auswählen")

    detected = detect_cart_season()
    season_info = get_season_greeting_text(detected)

    st.radio(
        "Angebot-Szenario:",
        options=["vergleich","separate","einzelangebot"],
        format_func=lambda x: {
            "vergleich":"Vergleichsangebot - Verschiedene Reifenoptionen zur Auswahl für ein Fahrzeug",
            "separate":"Separate Fahrzeuge - Jede Position ist für ein anderes Fahrzeug",
            "einzelangebot":"Einzelangebot - Spezifisches Angebot für die ausgewählten Reifen"
        }[x],
        key="offer_scenario"
    )

    if st.session_state.offer_scenario == "vergleich":
        st.markdown(f"""
        <div class="info-box">
            <strong>Vergleichsangebot:</strong> Der Kunde bekommt mehrere {season_info['season_name']}-Reifenoptionen 
            zur Auswahl präsentiert und kann sich für eine davon entscheiden.
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.offer_scenario == "separate":
        st.markdown(f"""
        <div class="info-box">
            <strong>Separate Fahrzeuge:</strong> Jede Position wird als separates Fahrzeug 
            behandelt mit eigenständiger {season_info['season_name']}-Reifen-Berechnung.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="info-box">
            <strong>Einzelangebot:</strong> Direktes, spezifisches Angebot für die ausgewählten 
            {season_info['season_name']}-Reifen ohne Vergleichsoptionen.
        </div>
        """, unsafe_allow_html=True)

    return detected

def render_email_options(email_text, detected_season):
    customer_email = st.session_state.customer_data.get('email', '').strip()
    if not customer_email:
        st.warning("Bitte geben Sie eine E-Mail-Adresse bei den Kundendaten ein.")
        return
    if not _valid_email(customer_email):
        st.error("Die E-Mail-Adresse scheint ungültig zu sein. Bitte prüfen.")
        return

    st.markdown(f"""
    <div class="email-options-box">
        <h4>📧 E-Mail-Versand Optionen</h4>
        <p>Wählen Sie Ihren E-Mail-Client zum Versenden des Angebots an <strong>{customer_email}</strong>:</p>
        <p><strong>Wichtig:</strong> Bitte fügen Sie die heruntergeladene PDF-Datei manuell als Anhang zur E-Mail hinzu.</p>
    </div>
    """, unsafe_allow_html=True)

    mailto_link = create_mailto_link(customer_email, email_text, detected_season)

    if mailto_link:
        st.link_button("📧 Outlook (Desktop)", mailto_link,
                       use_container_width=True, type="secondary",
                       help="Öffnet Ihren Standard-Mailclient (z. B. Outlook Desktop)")

    if st.button("❌ E-Mail-Optionen schließen", use_container_width=True):
        st.session_state.show_email_options = False
        st.rerun()

def render_actions(total, breakdown, detected_season):
    st.markdown("---")
    st.markdown("#### PDF-Angebot erstellen")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("📄 PDF-Angebot erstellen", use_container_width=True, type="primary"):
            pdf_data = create_professional_pdf(
                st.session_state.customer_data,
                st.session_state.offer_scenario,
                detected_season
            )
            if pdf_data:
                st.session_state.current_email_text = create_email_text(
                    st.session_state.customer_data,
                    detected_season
                )
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                season_info = get_season_greeting_text(detected_season)
                filename = f"Angebot_Ramsperger_{season_info['season_name']}_{ts}.pdf"

                st.success("✅ PDF-Angebot erfolgreich erstellt!")
                st.download_button(
                    label="📥 PDF-Angebot herunterladen",
                    data=pdf_data,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
                st.session_state.pdf_created = True
            else:
                st.error("Fehler beim Erstellen der PDF-Datei")

    with col2:
        customer_email = st.session_state.customer_data.get('email', '').strip()
        if customer_email and st.session_state.pdf_created:
            if st.button("📧 Per E-Mail senden", use_container_width=True, type="secondary",
                         help="Zeigt E-Mail-Optionen an"):
                st.session_state.show_email_options = True
                st.rerun()
        elif not customer_email:
            st.button("📧 E-Mail fehlt", use_container_width=True, disabled=True,
                      help="Bitte E-Mail-Adresse bei Kundendaten eingeben")
        else:
            st.button("📧 Erst PDF erstellen", use_container_width=True, disabled=True,
                      help="Bitte zuerst PDF-Angebot erstellen")

    with col3:
        if st.button("Warenkorb leeren", use_container_width=True, type="secondary"):
            clear_cart()
            st.session_state.pdf_created = False
            st.success("Warenkorb geleert!")
            st.rerun()

    with col4:
        if st.button("Weitere Reifen", use_container_width=True):
            st.switch_page("pages/01_Reifen_Suche.py")

    with col5:
        if st.button("Reifen ausbuchen", use_container_width=True, type="primary"):
            if st.session_state.cart_items:
                st.success("Reifen erfolgreich ausgebucht!")
                clear_cart()
                st.session_state.pdf_created = False
                st.rerun()
            else:
                st.warning("Warenkorb ist leer!")

    if st.session_state.show_email_options and hasattr(st.session_state, 'current_email_text'):
        st.markdown("---")
        render_email_options(st.session_state.current_email_text, detected_season)

# ================================================================================================
# MAIN
# ================================================================================================
def main():
    init_session_state()

    st.markdown("""
    <div class="main-header">
        <h1>Warenkorb & Angebotserstellung</h1>
        <p>Erstelle professionelle PDF-Angebote mit automatischer Saison-Erkennung und flexiblem E-Mail-Versand</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.cart_items:
        render_empty_cart()
        return

    render_cart_content()
    total, breakdown = get_cart_total()
    render_price_summary(total, breakdown)
    render_customer_data()
    detected = render_scenario_selection()
    render_actions(total, breakdown, detected)

if __name__ == "__main__":
    main()