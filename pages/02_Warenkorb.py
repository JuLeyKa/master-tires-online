import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import urllib.parse
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
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
# HELPER FUNCTIONS
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
    # zugehörige Widget-Keys säubern
    _clear_item_widget_keys(tire_id)
    st.session_state.cart_count = len(st.session_state.cart_items)

def clear_cart():
    # alle dynamischen Widget-Keys entfernen
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

# ---------------------- PDF GENERATION (NEU) ----------------------
def create_professional_pdf(customer_data=None, offer_scenario="vergleich", detected_season="neutral"):
    """Erstellt eine professionelle PDF-Angebotsdatei"""
    if not st.session_state.cart_items:
        return None

    total, breakdown = get_cart_total()
    season_info = get_season_greeting_text(detected_season)
    
    # PDF Buffer
    buffer = io.BytesIO()
    
    # PDF Document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#0ea5e9'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#1e293b'),
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        textColor=colors.HexColor('#1e293b')
    )
    
    # Story (PDF Inhalt)
    story = []
    
    # Header
    story.append(Paragraph("AUTOHAUS RAMSPERGER", title_style))
    story.append(Paragraph("Professionelles Reifenangebot", styles['Heading3']))
    story.append(Spacer(1, 20))
    
    # Datum und Angebotsnummer
    date_str = datetime.now().strftime('%d.%m.%Y')
    offer_number = f"RRS-{datetime.now().strftime('%Y%m%d')}-{len(st.session_state.cart_items):03d}"
    
    info_data = [
        ['Datum:', date_str],
        ['Angebotsnummer:', offer_number],
        ['Saison-Typ:', season_info['season_name']]
    ]
    
    info_table = Table(info_data, colWidths=[4*cm, 8*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Kundendaten
    if customer_data and any(customer_data.values()):
        story.append(Paragraph("KUNDENDATEN", heading_style))
        
        customer_table_data = []
        if customer_data.get('name'): customer_table_data.append(['Kunde:', customer_data['name']])
        if customer_data.get('email'): customer_table_data.append(['E-Mail:', customer_data['email']])
        if customer_data.get('kennzeichen'): customer_table_data.append(['Kennzeichen:', customer_data['kennzeichen']])
        if customer_data.get('modell'): customer_table_data.append(['Fahrzeug:', customer_data['modell']])
        if customer_data.get('fahrgestellnummer'): customer_table_data.append(['Fahrgestellnummer:', customer_data['fahrgestellnummer']])
        
        if customer_table_data:
            customer_table = Table(customer_table_data, colWidths=[4*cm, 10*cm])
            customer_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(customer_table)
            story.append(Spacer(1, 20))
    
    # Angebot Header
    scenario_headers = {
        "vergleich": "IHRE REIFENOPTIONEN ZUR AUSWAHL",
        "separate": "ANGEBOT FÜR IHRE FAHRZEUGE", 
        "einzelangebot": "IHR INDIVIDUELLES REIFENANGEBOT"
    }
    
    story.append(Paragraph(scenario_headers.get(offer_scenario, "IHR REIFENANGEBOT"), heading_style))
    story.append(Spacer(1, 10))
    
    # Reifen-Tabelle
    table_data = [['Pos.', 'Reifengröße', 'Marke', 'Profil', 'Stück', 'Einzelpreis', 'Services', 'Gesamtpreis']]
    
    for i, item in enumerate(st.session_state.cart_items, 1):
        reifen_kosten, service_kosten, position_total = calculate_position_total(item)
        quantity = st.session_state.cart_quantities.get(item['id'], 4)
        
        # Service-Text aufbauen
        services_text = ""
        item_services = st.session_state.cart_services.get(item['id'], {})
        service_parts = []
        
        if item_services.get('montage', False):
            service_parts.append("Montage")
        if item_services.get('radwechsel', False):
            radwechsel_type = item_services.get('radwechsel_type', '4_raeder')
            type_map = {'1_rad': '1 Rad', '2_raeder': '2 Räder', '3_raeder': '3 Räder', '4_raeder': '4 Räder'}
            service_parts.append(f"Radwechsel {type_map.get(radwechsel_type, '4 Räder')}")
        if item_services.get('einlagerung', False):
            service_parts.append("Einlagerung")
        
        if service_parts:
            services_text = ", ".join(service_parts)
        else:
            services_text = "Keine"
        
        table_data.append([
            str(i),
            item['Reifengröße'],
            item['Fabrikat'],
            item['Profil'],
            f"{quantity}x",
            f"{item['Preis_EUR']:.2f} EUR",
            services_text,
            f"{position_total:.2f} EUR"
        ])
    
    # Reifen-Tabelle erstellen
    reifen_table = Table(table_data, colWidths=[1*cm, 3*cm, 2.5*cm, 4*cm, 1.5*cm, 2.5*cm, 3*cm, 2.5*cm])
    reifen_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0ea5e9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Position
        ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Stück
        ('ALIGN', (5, 1), (5, -1), 'RIGHT'),   # Einzelpreis
        ('ALIGN', (7, 1), (7, -1), 'RIGHT'),   # Gesamtpreis
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Borders
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(reifen_table)
    story.append(Spacer(1, 20))
    
    # Kostenaufstellung
    story.append(Paragraph("KOSTENAUFSTELLUNG", heading_style))
    
    cost_data = [
        ['Reifen-Kosten:', f"{breakdown['reifen']:.2f} EUR"],
    ]
    
    if breakdown['montage'] > 0:
        cost_data.append(['Montage-Service:', f"{breakdown['montage']:.2f} EUR"])
    if breakdown['radwechsel'] > 0:
        cost_data.append(['Radwechsel-Service:', f"{breakdown['radwechsel']:.2f} EUR"])
    if breakdown['einlagerung'] > 0:
        cost_data.append(['Einlagerung:', f"{breakdown['einlagerung']:.2f} EUR"])
    
    # Gesamtsumme
    cost_data.append(['', ''])  # Leerzeile
    cost_data.append(['GESAMTSUMME:', f"{total:.2f} EUR"])
    
    cost_table = Table(cost_data, colWidths=[10*cm, 4*cm])
    cost_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -2), 11),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, -2), (-1, -2), 2, colors.black),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0fdf4')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(cost_table)
    story.append(Spacer(1, 30))
    
    # Zusatzinformationen
    additional_info = []
    if detected_season == "winter":
        additional_info.append("• Wir empfehlen den rechtzeitigen Wechsel auf Winterreifen für optimale Sicherheit bei winterlichen Bedingungen.")
    elif detected_season == "sommer":
        additional_info.append("• Sommerreifen bieten optimalen Grip und Fahrkomfort bei warmen Temperaturen und trockenen Straßen.")
    elif detected_season == "ganzjahres":
        additional_info.append("• Ganzjahresreifen bieten eine praktische Lösung für den ganzjährigen Einsatz ohne saisonalen Wechsel.")
    
    additional_info.extend([
        "• Alle Preise verstehen sich inklusive der gewählten Service-Leistungen.",
        "• Montage und Service werden von unseren Fachkräften durchgeführt.",
        "• Bei Fragen stehen wir Ihnen gerne zur Verfügung."
    ])
    
    for info in additional_info:
        story.append(Paragraph(info, normal_style))
    
    story.append(Spacer(1, 30))
    
    # Footer
    story.append(Paragraph("Vielen Dank für Ihr Vertrauen!", styles['Heading3']))
    story.append(Paragraph("Ihr Team vom Autohaus Ramsperger", normal_style))
    
    # PDF generieren
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ---------------------- E-MAIL TEXT FUNCTIONS (VERKÜRZT) ----------------------
def create_email_text(customer_data=None, detected_season="neutral"):
    """Erstellt verkürzten E-Mail-Text mit Verweis auf PDF-Anhang"""
    season_info = get_season_greeting_text(detected_season)
    
    # SEHR kurzer Text für mailto: Limits
    email_content = f"""Sehr geehrte Damen und Herren,

anbei sende ich Ihnen Ihr Reifenangebot für {season_info["season_name"]}-Reifen.

Alle Details finden Sie im angehängten PDF-Dokument.

Bei Fragen stehen wir gerne zur Verfügung.

Mit freundlichen Grüßen
Autohaus Ramsperger"""

    return email_content

def create_mailto_link(customer_email, email_text, detected_season):
    """Erstellt einen mailto: Link mit verkürztem Text"""
    if not customer_email or not customer_email.strip():
        return None
    
    season_info = get_season_greeting_text(detected_season)
    
    # E-Mail Betreff
    subject = f"Ihr Reifenangebot von Autohaus Ramsperger - {season_info['season_name']}-Reifen"
    
    # URL-Encoding für mailto: Link
    subject_encoded = urllib.parse.quote(subject)
    body_encoded = urllib.parse.quote(email_text)
    
    mailto_link = f"mailto:{customer_email}?subject={subject_encoded}&body={body_encoded}"
    
    return mailto_link

def create_gmail_link(customer_email, email_text, detected_season):
    """Erstellt einen direkten Gmail Compose Link"""
    if not customer_email or not customer_email.strip():
        return None
    
    season_info = get_season_greeting_text(detected_season)
    
    # E-Mail Betreff
    subject = f"Ihr Reifenangebot von Autohaus Ramsperger - {season_info['season_name']}-Reifen"
    
    # URL-Encoding für Gmail compose Link
    to_encoded = urllib.parse.quote(customer_email)
    subject_encoded = urllib.parse.quote(subject)
    body_encoded = urllib.parse.quote(email_text)
    
    # Gmail compose URL
    gmail_url = f"https://mail.google.com/mail/u/0/?view=cm&to={to_encoded}&su={subject_encoded}&body={body_encoded}"
    
    return gmail_url

# ================================================================================================
# SESSION STATE INITIALISIERUNG (Single Source of Truth)
# ================================================================================================
def init_session_state():
    if 'customer_data' not in st.session_state:
        st.session_state.customer_data = {'name':'','email':'','kennzeichen':'','modell':'','fahrgestellnummer':''}

    if 'cart_items' not in st.session_state: st.session_state.cart_items = []
    if 'cart_quantities' not in st.session_state: st.session_state.cart_quantities = {}
    if 'cart_services' not in st.session_state: st.session_state.cart_services = {}
    if 'cart_count' not in st.session_state: st.session_state.cart_count = 0

    # Angebot-Szenario – direkt als Widget-Quelle
    if 'offer_scenario' not in st.session_state:
        st.session_state.offer_scenario = "vergleich"

    # E-Mail-Optionen Anzeige
    if 'show_email_options' not in st.session_state:
        st.session_state.show_email_options = False

    # PDF wurde erstellt
    if 'pdf_created' not in st.session_state:
        st.session_state.pdf_created = False

    # Kundendaten-Feld-Keys (damit Textfelder ohne value= auskommen)
    st.session_state.setdefault('customer_name', st.session_state.customer_data.get('name',''))
    st.session_state.setdefault('customer_email', st.session_state.customer_data.get('email',''))
    st.session_state.setdefault('customer_kennzeichen', st.session_state.customer_data.get('kennzeichen',''))
    st.session_state.setdefault('customer_modell', st.session_state.customer_data.get('modell',''))
    st.session_state.setdefault('customer_fahrgestell', st.session_state.customer_data.get('fahrgestellnummer',''))

# ================================================================================================
# INTERNAL UTILITIES FOR WIDGET-STATE
# ================================================================================================
def _ensure_item_defaults(item_id):
    # Mengen-Key
    st.session_state.setdefault(f"qty_{item_id}", st.session_state.cart_quantities.get(item_id, 4))
    # Service-Objekt
    st.session_state.cart_services.setdefault(item_id, {'montage':False,'radwechsel':False,'radwechsel_type':'4_raeder','einlagerung':False})
    # Widget-Keys für Services
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
        # cart_quantities wurde im Callback aktualisiert

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

    # Montage (Preis abhängig vom Zoll)
    z = item['Zoll']
    montage_price = (sp.get('montage_bis_17',25.0) if z<=17 else sp.get('montage_18_19',30.0) if z<=19 else sp.get('montage_ab_20',40.0))
    montage_label = f"Montage ({montage_price:.2f}EUR/Stk)"
    st.checkbox(montage_label, key=f"montage_{item_id}",
                on_change=_update_service, args=(item_id,'montage'))

    # Radwechsel
    st.checkbox("Radwechsel", key=f"radwechsel_{item_id}",
                on_change=_update_service, args=(item_id,'radwechsel'))

    # Radwechsel-Optionen (nur wenn aktiv)
    if st.session_state.get(f"radwechsel_{item_id}", False):
        options = [
            ('4_raeder', f"4 Räder ({sp.get('radwechsel_4_raeder',39.90):.2f}EUR)"),
            ('3_raeder', f"3 Räder ({sp.get('radwechsel_3_raeder',29.95):.2f}EUR)"),
            ('2_raeder', f"2 Räder ({sp.get('radwechsel_2_raeder',19.95):.2f}EUR)"),
            ('1_rad',   f"1 Rad ({sp.get('radwechsel_1_rad',9.95):.2f}EUR)")
        ]
        # kein index/value -> Single Source: st.session_state['cart_radwechsel_type_<id>']
        st.selectbox("Anzahl:", options=[k for k,_ in options],
                     format_func=lambda x: next(lbl for k,lbl in options if k==x),
                     key=f"cart_radwechsel_type_{item_id}",
                     on_change=_update_radwechsel_type, args=(item_id,))

    # Einlagerung
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

    # Sync in dict (eine Quelle für Offer)
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
    season_display = {
        "winter":"❄️ Winter-Reifen erkannt",
        "sommer":"☀️ Sommer-Reifen erkannt",
        "ganzjahres":"🌍 Ganzjahres-Reifen erkannt",
        "gemischt":"🔄 Verschiedene Reifen-Typen",
        "neutral":"🔍 Reifen-Typ wird analysiert"
    }
    st.markdown(f"""
    <div class="saison-info-box">
        <h4>🎯 Automatische Saison-Erkennung</h4>
        <p><strong>{season_display.get(detected,'🔍 Analysiere Reifen...')}</strong></p>
        <p>Das Angebot wird automatisch an die erkannte Saison angepasst.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="scenario-box">
        <h4>Wie soll das Angebot erstellt werden?</h4>
        <p>Wähle das passende Szenario für deine Situation:</p>
    </div>
    """, unsafe_allow_html=True)

    # Single Source: key="offer_scenario"
    st.radio(
        "Angebot-Szenario:",
        options=["vergleich","separate","einzelangebot"],
        format_func=lambda x: {
            "vergleich":"Vergleichsangebot - Verschiedene Reifenoptionen zur Auswahl für ein Fahrzeug",
            "separate":"Separate Fahrzeuge - Jede Position ist für ein anderes Fahrzeug",
            "einzelangebot":"Einzelangebot - Spezifisches Angebot für die gewählten Reifen"
        }[x],
        key="offer_scenario"
    )

    # Info-Box je nach Auswahl
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

    return detected  # für spätere Nutzung

def render_email_options(email_text, detected_season):
    """Rendert die E-Mail-Optionen Box"""
    customer_email = st.session_state.customer_data.get('email', '').strip()
    
    if not customer_email:
        st.warning("Bitte geben Sie eine E-Mail-Adresse bei den Kundendaten ein.")
        return
    
    st.markdown(f"""
    <div class="email-options-box">
        <h4>📧 E-Mail-Versand Optionen</h4>
        <p>Wählen Sie Ihren bevorzugten E-Mail-Client zum Versenden des Angebots an <strong>{customer_email}</strong>:</p>
        <p><strong>Wichtig:</strong> Bitte fügen Sie die heruntergeladene PDF-Datei manuell als Anhang zur E-Mail hinzu.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📧 Mit Outlook senden", use_container_width=True, type="secondary", help="Öffnet Ihren Standard-E-Mail-Client (meist Outlook)"):
            mailto_link = create_mailto_link(customer_email, email_text, detected_season)
            if mailto_link:
                st.markdown(f'<a href="{mailto_link}" target="_blank" style="display: none;" id="outlook-email-link"></a>', unsafe_allow_html=True)
                st.markdown("""
                <script>
                    document.getElementById('outlook-email-link').click();
                </script>
                """, unsafe_allow_html=True)
                st.success(f"Outlook wird automatisch geöffnet mit E-Mail an {customer_email}")
                st.info("Die E-Mail ist vorbereitet. Fügen Sie jetzt die PDF-Datei als Anhang hinzu und senden Sie die E-Mail ab.")
    
    with col2:
        if st.button("📧 Mit Gmail senden", use_container_width=True, type="secondary", help="Öffnet Gmail.com direkt im Browser"):
            gmail_link = create_gmail_link(customer_email, email_text, detected_season)
            if gmail_link:
                st.success("Gmail wird im Browser geöffnet!")
                st.markdown(f'**[📧 Gmail öffnen - Klicken Sie hier]({gmail_link})**', unsafe_allow_html=True)
                st.info("Der Link öffnet Gmail.com mit der vorbereiteten E-Mail. Fügen Sie die PDF-Datei als Anhang hinzu.")
    
    # Schließen Button
    if st.button("❌ E-Mail-Optionen schließen", use_container_width=True):
        st.session_state.show_email_options = False
        st.rerun()

def render_actions(total, breakdown, detected_season):
    st.markdown("---")
    st.markdown("#### Professionelles PDF-Angebot erstellen")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("📄 PDF-Angebot erstellen", use_container_width=True, type="primary"):
            # PDF erstellen
            pdf_data = create_professional_pdf(
                st.session_state.customer_data,
                st.session_state.offer_scenario,
                detected_season
            )
            
            if pdf_data:
                # E-Mail-Text für E-Mail erstellen
                st.session_state.current_email_text = create_email_text(
                    st.session_state.customer_data,
                    detected_season
                )
                
                # PDF Download anbieten
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
        # E-Mail versenden Button (nur wenn PDF erstellt wurde)
        customer_email = st.session_state.customer_data.get('email', '').strip()
        if customer_email and st.session_state.pdf_created:
            if st.button("📧 Per E-Mail senden", use_container_width=True, type="secondary", help="Zeigt E-Mail-Optionen an"):
                st.session_state.show_email_options = True
                st.rerun()
        elif not customer_email:
            if st.button("📧 E-Mail fehlt", use_container_width=True, disabled=True, help="Bitte E-Mail-Adresse bei Kundendaten eingeben"):
                st.warning("Bitte geben Sie eine E-Mail-Adresse bei den Kundendaten ein.")
        else:
            if st.button("📧 Erst PDF erstellen", use_container_width=True, disabled=True, help="Bitte zuerst PDF-Angebot erstellen"):
                st.info("Bitte erstellen Sie zuerst das PDF-Angebot.")

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
                # hier würde real die Bestandsreduktion passieren
                st.success("Reifen erfolgreich ausgebucht!")
                clear_cart()
                st.session_state.pdf_created = False
                st.rerun()
            else:
                st.warning("Warenkorb ist leer!")

    # E-Mail-Optionen anzeigen (falls aktiviert)
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