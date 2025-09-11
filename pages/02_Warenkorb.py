import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

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

# CSS anwenden
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# ================================================================================================
# HELPER FUNCTIONS - DIREKT EINGEBETTET  
# ================================================================================================
def get_efficiency_emoji(rating):
    """Gibt Text für Effizienz-Rating zurück"""
    if pd.isna(rating):
        return ""
    rating = str(rating).strip().upper()[:1]
    return {
        "A": "[A]", "B": "[B]", "C": "[C]", 
        "D": "[D]", "E": "[E]", "F": "[F]", "G": "[G]"
    }.get(rating, "")

def get_stock_display(stock_value):
    """Formatiert Bestandsanzeige mit Text"""
    if pd.isna(stock_value) or stock_value == '':
        return "unbekannt"
    
    try:
        stock_num = float(stock_value)
        if stock_num < 0:
            return f"NACHBESTELLEN ({int(stock_num)})"
        elif stock_num == 0:
            return f"AUSVERKAUFT ({int(stock_num)})"
        else:
            return f"VERFÜGBAR ({int(stock_num)})"
    except:
        return "unbekannt"

def init_default_services():
    """Initialisiert Standard Service-Konfiguration"""
    services_data = {
        'service_name': ['montage_bis_17', 'montage_18_19', 'montage_ab_20', 
                       'radwechsel_1_rad', 'radwechsel_2_raeder', 'radwechsel_3_raeder', 
                       'radwechsel_4_raeder', 'nur_einlagerung'],
        'service_label': ['Montage bis 17 Zoll', 'Montage 18-19 Zoll', 'Montage ab 20 Zoll',
                        'Radwechsel 1 Rad', 'Radwechsel 2 Räder', 'Radwechsel 3 Räder',
                        'Radwechsel 4 Räder', 'Nur Einlagerung'],
        'price': [25.0, 30.0, 40.0, 9.95, 19.95, 29.95, 39.90, 55.00],
        'unit': ['pro Reifen', 'pro Reifen', 'pro Reifen', 
                'pauschal', 'pauschal', 'pauschal', 'pauschal', 'pauschal']
    }
    return pd.DataFrame(services_data)

def get_service_prices():
    """Gibt aktuelle Service-Preise zurück"""
    if 'services_config' not in st.session_state:
        st.session_state.services_config = init_default_services()
    
    services_config = st.session_state.services_config
    prices = {}
    for _, row in services_config.iterrows():
        prices[row['service_name']] = row['price']
    return prices

# ================================================================================================
# CART MANAGEMENT - ERWEITERT MIT POSITION-PREISEN
# ================================================================================================
def remove_from_cart(tire_id):
    """Entfernt einen Reifen aus dem Warenkorb"""
    st.session_state.cart_items = [item for item in st.session_state.cart_items if item['id'] != tire_id]
    if tire_id in st.session_state.cart_quantities:
        del st.session_state.cart_quantities[tire_id]
    if tire_id in st.session_state.cart_services:
        del st.session_state.cart_services[tire_id]
    st.session_state.cart_count = len(st.session_state.cart_items)

def clear_cart():
    """Leert den kompletten Warenkorb"""
    st.session_state.cart_items = []
    st.session_state.cart_quantities = {}
    st.session_state.cart_services = {}
    st.session_state.cart_count = 0

def calculate_position_total(item):
    """Berechnet Gesamtpreis für eine Position (Reifen + Services)"""
    tire_id = item['id']
    quantity = st.session_state.cart_quantities.get(tire_id, 4)
    service_prices = get_service_prices()
    
    # Reifen-Kosten
    reifen_kosten = item['Preis_EUR'] * quantity
    
    # Services für diesen Reifen
    item_services = st.session_state.cart_services.get(tire_id, {})
    service_kosten = 0.0
    
    # Montage-Kosten
    if item_services.get('montage', False):
        zoll_size = item['Zoll']
        if zoll_size <= 17:
            montage_preis = service_prices.get('montage_bis_17', 25.0)
        elif zoll_size <= 19:
            montage_preis = service_prices.get('montage_18_19', 30.0)
        else:
            montage_preis = service_prices.get('montage_ab_20', 40.0)
        service_kosten += montage_preis * quantity
    
    # Radwechsel-Kosten
    if item_services.get('radwechsel', False):
        radwechsel_type = item_services.get('radwechsel_type', '4_raeder')
        if radwechsel_type == '1_rad':
            service_kosten += service_prices.get('radwechsel_1_rad', 9.95)
        elif radwechsel_type == '2_raeder':
            service_kosten += service_prices.get('radwechsel_2_raeder', 19.95)
        elif radwechsel_type == '3_raeder':
            service_kosten += service_prices.get('radwechsel_3_raeder', 29.95)
        else:  # '4_raeder'
            service_kosten += service_prices.get('radwechsel_4_raeder', 39.90)
    
    # Einlagerungs-Kosten
    if item_services.get('einlagerung', False):
        service_kosten += service_prices.get('nur_einlagerung', 55.00)
    
    return reifen_kosten, service_kosten, reifen_kosten + service_kosten

def get_cart_total():
    """Berechnet Warenkorb-Gesamtsumme"""
    total = 0.0
    breakdown = {'reifen': 0.0, 'montage': 0.0, 'radwechsel': 0.0, 'einlagerung': 0.0}
    
    for item in st.session_state.cart_items:
        reifen_kosten, service_kosten, position_total = calculate_position_total(item)
        total += position_total
        breakdown['reifen'] += reifen_kosten
        
        # Service-Breakdown für Gesamtübersicht
        tire_id = item['id']
        item_services = st.session_state.cart_services.get(tire_id, {})
        service_prices = get_service_prices()
        quantity = st.session_state.cart_quantities.get(tire_id, 4)
        
        if item_services.get('montage', False):
            zoll_size = item['Zoll']
            if zoll_size <= 17:
                montage_preis = service_prices.get('montage_bis_17', 25.0)
            elif zoll_size <= 19:
                montage_preis = service_prices.get('montage_18_19', 30.0)
            else:
                montage_preis = service_prices.get('montage_ab_20', 40.0)
            breakdown['montage'] += montage_preis * quantity
        
        if item_services.get('radwechsel', False):
            radwechsel_type = item_services.get('radwechsel_type', '4_raeder')
            if radwechsel_type == '1_rad':
                breakdown['radwechsel'] += service_prices.get('radwechsel_1_rad', 9.95)
            elif radwechsel_type == '2_raeder':
                breakdown['radwechsel'] += service_prices.get('radwechsel_2_raeder', 19.95)
            elif radwechsel_type == '3_raeder':
                breakdown['radwechsel'] += service_prices.get('radwechsel_3_raeder', 29.95)
            else:
                breakdown['radwechsel'] += service_prices.get('radwechsel_4_raeder', 39.90)
        
        if item_services.get('einlagerung', False):
            breakdown['einlagerung'] += service_prices.get('nur_einlagerung', 55.00)
    
    return total, breakdown

def create_professional_offer(customer_data=None, offer_scenario="vergleich"):
    """Erstellt professionelles Angebot mit Szenario-Unterstützung"""
    if not st.session_state.cart_items:
        return "Warenkorb ist leer"
    
    total, breakdown = get_cart_total()
    service_prices = get_service_prices()
    
    content = []
    
    # Header
    content.append("AUTOHAUS RAMSPERGER")
    content.append("Kostenvoranschlag für Winterreifen")
    content.append("=" * 60)
    content.append(f"Datum: {datetime.now().strftime('%d.%m.%Y')}")
    content.append("")
    
    # Kundendaten
    if customer_data and any(customer_data.values()):
        content.append("KUNDENDATEN:")
        content.append("-" * 30)
        if customer_data.get('name'):
            content.append(f"Kunde: {customer_data['name']}")
        if customer_data.get('kennzeichen'):
            content.append(f"Kennzeichen: {customer_data['kennzeichen']}")
        if customer_data.get('modell'):
            content.append(f"Fahrzeug: {customer_data['modell']}")
        if customer_data.get('fahrgestellnummer'):
            content.append(f"Fahrgestellnummer: {customer_data['fahrgestellnummer']}")
        content.append("")
    
    # Anrede je nach Szenario
    content.append("Sehr geehrter Kunde,")
    content.append("")
    
    if offer_scenario == "vergleich":
        content.append("der Sommer geht langsam zu Ende und die Zeichen stehen auf Winter.")
        content.append("Jetzt wird es auch Zeit für Ihre Winterreifen von Ihrem Auto.")
        content.append("Gerne stelle ich Ihnen verschiedene hochwertige Reifenmodelle vor,")
        content.append("aus denen Sie die für Sie beste Option wählen können:")
    else:  # separate fahrzeuge
        content.append("der Sommer geht langsam zu Ende und die Zeichen stehen auf Winter.")
        content.append("Jetzt wird es auch Zeit für Ihre Winterreifen.")
        content.append("Gerne erstelle ich Ihnen ein Angebot für Ihre beiden Fahrzeuge:")
    
    content.append("")
    
    # Reifen-Details je nach Szenario
    if offer_scenario == "vergleich":
        content.append("IHRE REIFENOPTIONEN ZUR AUSWAHL:")
        content.append("=" * 60)
        
        for i, item in enumerate(st.session_state.cart_items, 1):
            reifen_kosten, service_kosten, position_total = calculate_position_total(item)
            quantity = st.session_state.cart_quantities.get(item['id'], 4)
            
            content.append(f"OPTION {i}:")
            content.append("-" * 20)
            content.append(f"Größe: {item['Reifengroesse']}")
            content.append(f"Marke: {item['Fabrikat']} {item['Profil']}")
            content.append(f"Teilenummer: {item['Teilenummer']}")
            
            # EU-Label
            if item.get('Kraftstoffeffizienz') or item.get('Nasshaftung'):
                label_info = []
                if item.get('Kraftstoffeffizienz'):
                    label_info.append(f"Kraftstoff: {item['Kraftstoffeffizienz']}")
                if item.get('Nasshaftung'):
                    label_info.append(f"Nasshaftung: {item['Nasshaftung']}")
                content.append(f"EU-Label: {' | '.join(label_info)}")
            
            content.append(f"Anzahl: {quantity} Reifen")
            content.append(f"Reifenpreis: {reifen_kosten:.2f}EUR")
            if service_kosten > 0:
                content.append(f"Service-Leistungen: {service_kosten:.2f}EUR")
            content.append(f"OPTION {i} GESAMT: {position_total:.2f}EUR")
            content.append("")
    
    else:  # separate fahrzeuge
        content.append("ANGEBOT FÜR IHRE FAHRZEUGE:")
        content.append("=" * 60)
        
        for i, item in enumerate(st.session_state.cart_items, 1):
            reifen_kosten, service_kosten, position_total = calculate_position_total(item)
            quantity = st.session_state.cart_quantities.get(item['id'], 4)
            
            content.append(f"FAHRZEUG {i}:")
            content.append("-" * 20)
            content.append(f"Größe: {item['Reifengroesse']}")
            content.append(f"Marke: {item['Fabrikat']} {item['Profil']}")
            content.append(f"Teilenummer: {item['Teilenummer']}")
            
            # EU-Label
            if item.get('Kraftstoffeffizienz') or item.get('Nasshaftung'):
                label_info = []
                if item.get('Kraftstoffeffizienz'):
                    label_info.append(f"Kraftstoff: {item['Kraftstoffeffizienz']}")
                if item.get('Nasshaftung'):
                    label_info.append(f"Nasshaftung: {item['Nasshaftung']}")
                content.append(f"EU-Label: {' | '.join(label_info)}")
            
            content.append(f"Anzahl: {quantity} Reifen")
            content.append(f"Reifenpreis: {reifen_kosten:.2f}EUR")
            if service_kosten > 0:
                content.append(f"Service-Leistungen: {service_kosten:.2f}EUR")
            content.append(f"FAHRZEUG {i} GESAMT: {position_total:.2f}EUR")
            content.append("")
    
    # Gesamtübersicht
    content.append("GESAMTÜBERSICHT:")
    content.append("=" * 30)
    
    if offer_scenario == "vergleich":
        content.append("Sie können zwischen den oben genannten Optionen wählen.")
        content.append("Die Preise verstehen sich als Komplettpreis inkl. aller")
        content.append("gewählten Service-Leistungen.")
    else:
        content.append(f"Reifen-Kosten gesamt: {breakdown['reifen']:.2f}EUR")
        if breakdown['montage'] + breakdown['radwechsel'] + breakdown['einlagerung'] > 0:
            content.append(f"Service-Leistungen gesamt: {breakdown['montage'] + breakdown['radwechsel'] + breakdown['einlagerung']:.2f}EUR")
        content.append("")
        content.append("*" * 60)
        content.append(f"GESAMTSUMME BEIDE FAHRZEUGE: {total:.2f}EUR")
        content.append("*" * 60)
    
    content.append("")
    
    # Abschluss
    content.append("Gerne stehen wir Ihnen für Rückfragen zur Verfügung.")
    content.append("Wir freuen uns auf Ihren Auftrag!")
    content.append("")
    content.append("Mit freundlichen Grüßen")
    content.append("Autohaus Ramsperger")
    
    return "\n".join(content)

# ================================================================================================
# SESSION STATE INITIALISIERUNG
# ================================================================================================
def init_session_state():
    """Initialisiert Session State für Warenkorb"""
    if 'customer_data' not in st.session_state:
        st.session_state.customer_data = {
            'name': '',
            'kennzeichen': '',
            'modell': '',
            'fahrgestellnummer': ''
        }
    
    # Warenkorb initialisieren
    if 'cart_items' not in st.session_state:
        st.session_state.cart_items = []
    if 'cart_quantities' not in st.session_state:
        st.session_state.cart_quantities = {}
    if 'cart_services' not in st.session_state:
        st.session_state.cart_services = {}
    if 'cart_count' not in st.session_state:
        st.session_state.cart_count = 0
    
    # Angebot-Szenario
    if 'offer_scenario' not in st.session_state:
        st.session_state.offer_scenario = "vergleich"

# ================================================================================================
# RENDER FUNCTIONS
# ================================================================================================
def render_empty_cart():
    """Rendert leeren Warenkorb"""
    st.markdown("""
    <div class="cart-container">
        <h3>Der Warenkorb ist leer</h3>
        <p>Gehe zur <strong>Reifen Suche</strong> und wähle Reifen für dein Angebot aus.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Zur Reifen Suche", use_container_width=True, type="primary"):
        st.switch_page("pages/01_Reifen_Suche.py")

def render_cart_content():
    """Rendert Warenkorb-Inhalt mit verbesserten Position-Preisen"""
    st.markdown("#### Reifen im Warenkorb")
    
    for i, item in enumerate(st.session_state.cart_items, 1):
        render_cart_item(item, i)

def render_cart_item(item, position_number):
    """Rendert ein einzelnes Warenkorb-Item mit Position-Preis"""
    st.markdown('<div class="cart-item">', unsafe_allow_html=True)
    
    # Header mit Position
    st.markdown(f"### Position {position_number}")
    
    col_info, col_qty, col_services, col_remove = st.columns([3, 1, 2, 1])
    
    with col_info:
        st.markdown(f"**{item['Reifengroesse']}** - {item['Fabrikat']} {item['Profil']}")
        st.markdown(f"Teilenummer: {item['Teilenummer']} | Einzelpreis: **{item['Preis_EUR']:.2f}EUR**")
        
        # EU-Label und Bestand
        effi_display = f" {get_efficiency_emoji(item['Kraftstoffeffizienz'])}{item['Kraftstoffeffizienz']}" if item['Kraftstoffeffizienz'] else ""
        nasshaft_display = f" {get_efficiency_emoji(item['Nasshaftung'])}{item['Nasshaftung']}" if item['Nasshaftung'] else ""
        bestand_display = f" | {get_stock_display(item['Bestand'])}"
        
        if effi_display or nasshaft_display or bestand_display:
            st.markdown(f"EU-Label:{effi_display}{nasshaft_display}{bestand_display}")
    
    with col_qty:
        current_qty = st.session_state.cart_quantities.get(item['id'], 4)
        new_qty = st.number_input(
            "Stückzahl:",
            min_value=1,
            max_value=8,
            value=current_qty,
            step=1,
            key=f"qty_{item['id']}"
        )
        st.session_state.cart_quantities[item['id']] = new_qty
    
    with col_services:
        render_item_services(item)
    
    with col_remove:
        if st.button("Entfernen", key=f"remove_{item['id']}", help="Aus Warenkorb entfernen"):
            remove_from_cart(item['id'])
            st.rerun()
    
    # Position-Gesamtpreis OHNE blauen Kasten - nur fetter Text
    reifen_kosten, service_kosten, position_total = calculate_position_total(item)
    
    st.markdown(f"### **Position {position_number} Gesamt: {position_total:.2f} EUR**")
    st.markdown(f"Reifen: {reifen_kosten:.2f}EUR + Services: {service_kosten:.2f}EUR")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_item_services(item):
    """Rendert Service-Optionen für ein Item"""
    st.markdown("**Services:**")
    
    # Services für diesen Reifen holen oder Standard setzen
    if item['id'] not in st.session_state.cart_services:
        st.session_state.cart_services[item['id']] = {
            'montage': False, 'radwechsel': False, 'radwechsel_type': '4_raeder', 'einlagerung': False
        }
    
    current_services = st.session_state.cart_services[item['id']]
    service_prices = get_service_prices()
    
    # Montage
    zoll_size = item['Zoll']
    if zoll_size <= 17:
        montage_price = service_prices.get('montage_bis_17', 25.0)
        montage_label = f"Montage ({montage_price:.2f}EUR/Stk)"
    elif zoll_size <= 19:
        montage_price = service_prices.get('montage_18_19', 30.0)
        montage_label = f"Montage ({montage_price:.2f}EUR/Stk)"
    else:
        montage_price = service_prices.get('montage_ab_20', 40.0)
        montage_label = f"Montage ({montage_price:.2f}EUR/Stk)"
    
    montage_selected = st.checkbox(
        montage_label,
        value=current_services.get('montage', False),
        key=f"cart_montage_{item['id']}"
    )
    st.session_state.cart_services[item['id']]['montage'] = montage_selected
    
    # Radwechsel
    radwechsel_selected = st.checkbox(
        "Radwechsel",
        value=current_services.get('radwechsel', False),
        key=f"cart_radwechsel_{item['id']}"
    )
    st.session_state.cart_services[item['id']]['radwechsel'] = radwechsel_selected
    
    # Radwechsel-Optionen (editierbar im Warenkorb)
    if radwechsel_selected:
        radwechsel_options = [
            ('4_raeder', f"4 Räder ({service_prices.get('radwechsel_4_raeder', 39.90):.2f}EUR)"),
            ('3_raeder', f"3 Räder ({service_prices.get('radwechsel_3_raeder', 29.95):.2f}EUR)"),
            ('2_raeder', f"2 Räder ({service_prices.get('radwechsel_2_raeder', 19.95):.2f}EUR)"),
            ('1_rad', f"1 Rad ({service_prices.get('radwechsel_1_rad', 9.95):.2f}EUR)")
        ]
        
        current_radwechsel_type = current_services.get('radwechsel_type', '4_raeder')
        current_index = next((i for i, (key, _) in enumerate(radwechsel_options) if key == current_radwechsel_type), 0)
        
        radwechsel_type = st.selectbox(
            "Anzahl:",
            options=[opt[0] for opt in radwechsel_options],
            index=current_index,
            format_func=lambda x: next(opt[1] for opt in radwechsel_options if opt[0] == x),
            key=f"cart_radwechsel_type_{item['id']}"
        )
        st.session_state.cart_services[item['id']]['radwechsel_type'] = radwechsel_type
    
    # Einlagerung
    einlagerung_selected = st.checkbox(
        f"Einlagerung ({service_prices.get('nur_einlagerung', 55.00):.2f}EUR)",
        value=current_services.get('einlagerung', False),
        key=f"cart_einlagerung_{item['id']}"
    )
    st.session_state.cart_services[item['id']]['einlagerung'] = einlagerung_selected

def render_price_summary(total, breakdown):
    """Rendert Preisübersicht"""
    st.markdown("---")
    st.markdown('<div class="total-box">', unsafe_allow_html=True)
    st.markdown("#### Preisübersicht")
    
    col_breakdown, col_total = st.columns([2, 1])
    
    with col_breakdown:
        st.markdown(f"**Reifen-Kosten:** {breakdown['reifen']:.2f}EUR")
        
        if breakdown['montage'] > 0:
            st.markdown(f"**Montage:** {breakdown['montage']:.2f}EUR")
        
        if breakdown['radwechsel'] > 0:
            st.markdown(f"**Radwechsel:** {breakdown['radwechsel']:.2f}EUR")
        
        if breakdown['einlagerung'] > 0:
            st.markdown(f"**Einlagerung:** {breakdown['einlagerung']:.2f}EUR")
    
    with col_total:
        st.markdown(f"### **GESAMT: {total:.2f}EUR**")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_customer_data():
    """Rendert Kundendaten-Eingabe"""
    st.markdown("---")
    st.markdown("#### Kundendaten (optional)")
    st.markdown("Diese Angaben werden in das Angebot aufgenommen, falls gewünscht:")
    
    col_kunde1, col_kunde2 = st.columns(2)
    
    with col_kunde1:
        st.session_state.customer_data['name'] = st.text_input(
            "Kundenname:",
            value=st.session_state.customer_data.get('name', ''),
            placeholder="z.B. Max Mustermann",
            key="customer_name"
        )
        
        st.session_state.customer_data['kennzeichen'] = st.text_input(
            "Kennzeichen:",
            value=st.session_state.customer_data.get('kennzeichen', ''),
            placeholder="z.B. GP-AB 123",
            key="customer_kennzeichen"
        )
    
    with col_kunde2:
        st.session_state.customer_data['modell'] = st.text_input(
            "Fahrzeugmodell:",
            value=st.session_state.customer_data.get('modell', ''),
            placeholder="z.B. BMW 3er E90",
            key="customer_modell"
        )
        
        st.session_state.customer_data['fahrgestellnummer'] = st.text_input(
            "Fahrgestellnummer:",
            value=st.session_state.customer_data.get('fahrgestellnummer', ''),
            placeholder="z.B. WBAVA31070F123456",
            key="customer_fahrgestell"
        )

def render_scenario_selection():
    """Rendert Szenario-Auswahl für Angebotserstellung"""
    st.markdown("---")
    st.markdown("#### Angebot-Typ auswählen")
    
    st.markdown("""
    <div class="scenario-box">
        <h4>Wie soll das Angebot erstellt werden?</h4>
        <p>Wähle das passende Szenario für deine Situation:</p>
    </div>
    """, unsafe_allow_html=True)
    
    scenario_options = [
        ("vergleich", "Vergleichsangebot - Verschiedene Reifenoptionen zur Auswahl für ein Fahrzeug"),
        ("separate", "Separate Fahrzeuge - Jede Position ist für ein anderes Fahrzeug")
    ]
    
    selected_scenario = st.radio(
        "Angebot-Szenario:",
        options=[opt[0] for opt in scenario_options],
        format_func=lambda x: next(opt[1] for opt in scenario_options if opt[0] == x),
        index=0 if st.session_state.offer_scenario == "vergleich" else 1,
        key="scenario_selection"
    )
    
    st.session_state.offer_scenario = selected_scenario
    
    # Erklärung je nach Szenario
    if selected_scenario == "vergleich":
        st.markdown("""
        <div class="info-box">
            <strong>Vergleichsangebot:</strong> Der Kunde bekommt mehrere Reifenoptionen 
            zur Auswahl präsentiert und kann sich für eine davon entscheiden.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-box">
            <strong>Separate Fahrzeuge:</strong> Jede Position wird als separates Fahrzeug 
            behandelt mit eigenständiger Berechnung.
        </div>
        """, unsafe_allow_html=True)

def render_actions(total, breakdown):
    """Rendert Export & Aktionen"""
    st.markdown("---")
    st.markdown("#### Angebot erstellen")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        # Professionelles Angebot erstellen
        if st.button("Angebot erstellen", use_container_width=True, type="primary"):
            professional_offer = create_professional_offer(
                st.session_state.customer_data, 
                st.session_state.offer_scenario
            )
            
            # Angebot anzeigen
            st.markdown("---")
            st.markdown("### Ihr Angebot")
            st.markdown("*Das folgende Angebot können Sie kopieren und in Ihre E-Mail einfügen:*")
            
            # Text in breiter Text-Area
            st.text_area(
                "Angebot:",
                value=professional_offer,
                height=600,
                max_chars=None,
                label_visibility="collapsed"
            )
            
            # Download-Option
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Angebot_Ramsperger_{timestamp}.txt"
            
            st.download_button(
                label="Angebot als Datei herunterladen",
                data=professional_offer,
                file_name=filename,
                mime="text/plain"
            )
    
    with col2:
        # Warenkorb leeren
        if st.button("Warenkorb leeren", use_container_width=True, type="secondary"):
            clear_cart()
            st.success("Warenkorb geleert!")
            st.rerun()
    
    with col3:
        # Zurück zur Suche
        if st.button("Weitere Reifen", use_container_width=True):
            st.switch_page("pages/01_Reifen_Suche.py")
    
    with col4:
        # Service-Preise bearbeiten (für Admins)
        if st.button("Service-Preise", use_container_width=True):
            st.switch_page("pages/03_Premium_Verwaltung.py")
    
    with col5:
        # Bestände reduzieren
        if st.button("Reifen ausbuchen", use_container_width=True, type="primary"):
            if st.session_state.cart_items:
                # Hier würde in der echten App die Bestandsreduktion erfolgen
                st.success("Reifen erfolgreich ausgebucht!")
                clear_cart()
                st.rerun()
            else:
                st.warning("Warenkorb ist leer!")

# ================================================================================================
# MAIN FUNCTION
# ================================================================================================
def main():
    init_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>Warenkorb & Angebotserstellung</h1>
        <p>Erstelle professionelle Angebote für deine Kunden</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Warenkorb leer?
    if not st.session_state.cart_items:
        render_empty_cart()
        return
    
    # Warenkorb Inhalt mit verbesserten Position-Preisen
    render_cart_content()
    
    # Preisberechnung
    total, breakdown = get_cart_total()
    render_price_summary(total, breakdown)
    
    # Kundendaten
    render_customer_data()
    
    # Szenario-Auswahl für Angebotserstellung
    render_scenario_selection()
    
    # Export & Aktionen
    render_actions(total, breakdown)

if __name__ == "__main__":
    main()