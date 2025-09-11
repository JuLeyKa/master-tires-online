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
            return f"VERFUEGBAR ({int(stock_num)})"
    except:
        return "unbekannt"

def init_sample_data():
    """Initialisiert Beispiel-Daten wenn keine vorhanden"""
    if 'services_config' not in st.session_state:
        services_data = {
            'service_name': ['montage_bis_17', 'montage_18_19', 'montage_ab_20', 
                           'radwechsel_1_rad', 'radwechsel_2_raeder', 'radwechsel_3_raeder', 
                           'radwechsel_4_raeder', 'nur_einlagerung'],
            'service_label': ['Montage bis 17 Zoll', 'Montage 18-19 Zoll', 'Montage ab 20 Zoll',
                            'Radwechsel 1 Rad', 'Radwechsel 2 Raeder', 'Radwechsel 3 Raeder',
                            'Radwechsel 4 Raeder', 'Nur Einlagerung'],
            'price': [25.0, 30.0, 40.0, 9.95, 19.95, 29.95, 39.90, 55.00],
            'unit': ['pro Reifen', 'pro Reifen', 'pro Reifen', 
                    'pauschal', 'pauschal', 'pauschal', 'pauschal', 'pauschal']
        }
        st.session_state.services_config = pd.DataFrame(services_data)

def get_service_prices():
    """Gibt aktuelle Service-Preise zurück"""
    init_sample_data()
    services_config = st.session_state.services_config
    prices = {}
    for _, row in services_config.iterrows():
        prices[row['service_name']] = row['price']
    return prices

# ================================================================================================
# CART MANAGEMENT - DIREKT EINGEBETTET
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

def get_cart_total():
    """Berechnet Warenkorb-Gesamtsumme"""
    if not st.session_state.cart_items:
        return 0.0, {}
    
    service_prices = get_service_prices()
    total = 0.0
    breakdown = {'reifen': 0.0, 'montage': 0.0, 'radwechsel': 0.0, 'einlagerung': 0.0}
    
    for item in st.session_state.cart_items:
        tire_id = item['id']
        quantity = st.session_state.cart_quantities.get(tire_id, 4)
        
        # Reifen-Kosten
        reifen_kosten = item['Preis_EUR'] * quantity
        total += reifen_kosten
        breakdown['reifen'] += reifen_kosten
        
        # Services für diesen Reifen
        item_services = st.session_state.cart_services.get(tire_id, {})
        
        # Montage-Kosten
        if item_services.get('montage', False):
            zoll_size = item['Zoll']
            if zoll_size <= 17:
                montage_preis = service_prices.get('montage_bis_17', 25.0)
            elif zoll_size <= 19:
                montage_preis = service_prices.get('montage_18_19', 30.0)
            else:
                montage_preis = service_prices.get('montage_ab_20', 40.0)
            
            montage_kosten = montage_preis * quantity
            total += montage_kosten
            breakdown['montage'] += montage_kosten
        
        # Radwechsel-Kosten
        if item_services.get('radwechsel', False):
            radwechsel_type = item_services.get('radwechsel_type', '4_raeder')
            
            if radwechsel_type == '1_rad':
                radwechsel_kosten = service_prices.get('radwechsel_1_rad', 9.95)
            elif radwechsel_type == '2_raeder':
                radwechsel_kosten = service_prices.get('radwechsel_2_raeder', 19.95)
            elif radwechsel_type == '3_raeder':
                radwechsel_kosten = service_prices.get('radwechsel_3_raeder', 29.95)
            else:  # '4_raeder'
                radwechsel_kosten = service_prices.get('radwechsel_4_raeder', 39.90)
            
            total += radwechsel_kosten
            breakdown['radwechsel'] += radwechsel_kosten
        
        # Einlagerungs-Kosten
        if item_services.get('einlagerung', False):
            einlagerungs_kosten = service_prices.get('nur_einlagerung', 55.00)
            total += einlagerungs_kosten
            breakdown['einlagerung'] += einlagerungs_kosten
    
    return total, breakdown

def create_professional_offer(customer_data=None):
    """Erstellt professionelles Angebot"""
    if not st.session_state.cart_items:
        return "Warenkorb ist leer"
    
    total, breakdown = get_cart_total()
    service_prices = get_service_prices()
    
    content = []
    
    # Header
    content.append("AUTOHAUS RAMSPERGER")
    content.append("Kostenvoranschlag fuer Winterreifen")
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
    
    # Anrede
    content.append("Sehr geehrter Kunde,")
    content.append("")
    content.append("der Sommer geht langsam zu Ende und die Zeichen stehen auf Winter.")
    content.append("Jetzt wird es auch Zeit fuer Ihre Winterreifen von Ihrem Auto.")
    content.append("Gerne stelle ich Ihnen hochwertige Reifenmodelle vor, die perfekt")
    content.append("zu Ihren Anforderungen passen:")
    content.append("")
    
    # Reifen-Details
    content.append("IHRE REIFENAUSWAHL:")
    content.append("=" * 60)
    
    for i, item in enumerate(st.session_state.cart_items, 1):
        tire_id = item['id']
        qty = st.session_state.cart_quantities.get(tire_id, 4)
        einzelpreis = item['Preis_EUR']
        reifen_gesamtpreis = einzelpreis * qty
        
        content.append(f"REIFEN {i}:")
        content.append("-" * 30)
        content.append(f"Groesse: {item['Reifengroesse']}")
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
        
        content.append(f"Stueckzahl: {qty} Reifen")
        content.append(f"Einzelpreis: {einzelpreis:.2f}EUR")
        content.append(f"Reifen-Summe: {reifen_gesamtpreis:.2f}EUR")
        content.append("")
        
        # Services für diesen Reifen
        item_services = st.session_state.cart_services.get(tire_id, {})
        service_kosten = 0.0
        
        if item_services.get('montage', False):
            zoll_size = item['Zoll']
            if zoll_size <= 17:
                montage_price = service_prices.get('montage_bis_17', 25.0)
                montage_text = "Reifenservice bis 17 Zoll"
            elif zoll_size <= 19:
                montage_price = service_prices.get('montage_18_19', 30.0)
                montage_text = "Reifenservice 18-19 Zoll"
            else:
                montage_price = service_prices.get('montage_ab_20', 40.0)
                montage_text = "Reifenservice ab 20 Zoll"
            
            montage_gesamt = montage_price * qty
            service_kosten += montage_gesamt
            content.append(f"+ {montage_text}: {qty}x {montage_price:.2f}EUR = {montage_gesamt:.2f}EUR")
        
        if item_services.get('radwechsel', False):
            radwechsel_type = item_services.get('radwechsel_type', '4_raeder')
            
            if radwechsel_type == '1_rad':
                radwechsel_preis = service_prices.get('radwechsel_1_rad', 9.95)
                radwechsel_text = "Radwechsel 1 Rad"
            elif radwechsel_type == '2_raeder':
                radwechsel_preis = service_prices.get('radwechsel_2_raeder', 19.95)
                radwechsel_text = "Radwechsel 2 Raeder"
            elif radwechsel_type == '3_raeder':
                radwechsel_preis = service_prices.get('radwechsel_3_raeder', 29.95)
                radwechsel_text = "Radwechsel 3 Raeder"
            else:
                radwechsel_preis = service_prices.get('radwechsel_4_raeder', 39.90)
                radwechsel_text = "Radwechsel 4 Raeder"
            
            service_kosten += radwechsel_preis
            content.append(f"+ {radwechsel_text}: {radwechsel_preis:.2f}EUR")
        
        if item_services.get('einlagerung', False):
            einlagerung_preis = service_prices.get('nur_einlagerung', 55.00)
            service_kosten += einlagerung_preis
            content.append(f"+ Einlagerung: {einlagerung_preis:.2f}EUR")
        
        # Zwischensumme
        reifen_total = reifen_gesamtpreis + service_kosten
        content.append("")
        content.append(f"ZWISCHENSUMME REIFEN {i}: {reifen_total:.2f}EUR")
        content.append("=" * 30)
        content.append("")
    
    # Gesamtübersicht
    content.append("GESAMTUEBERSICHT:")
    content.append("=" * 30)
    content.append(f"Reifen-Kosten gesamt: {breakdown['reifen']:.2f}EUR")
    
    if breakdown['montage'] > 0:
        content.append(f"Service-Leistungen gesamt: {breakdown['montage'] + breakdown['radwechsel'] + breakdown['einlagerung']:.2f}EUR")
    
    content.append("")
    content.append("*" * 60)
    content.append(f"GESAMTSUMME: {total:.2f}EUR")
    content.append("*" * 60)
    content.append("")
    
    # Abschluss
    content.append("Gerne stehen wir Ihnen fuer Rueckfragen zur Verfuegung.")
    content.append("Wir freuen uns auf Ihren Auftrag!")
    content.append("")
    content.append("Mit freundlichen Gruessen")
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

# ================================================================================================
# RENDER FUNCTIONS
# ================================================================================================
def render_empty_cart():
    """Rendert leeren Warenkorb"""
    st.markdown("""
    <div class="cart-container">
        <h3>Der Warenkorb ist leer</h3>
        <p>Gehe zur <strong>Reifen Suche</strong> und waehle Reifen fuer dein Angebot aus.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Zur Reifen Suche", use_container_width=True, type="primary"):
        st.switch_page("pages/01_Reifen_Suche.py")

def render_cart_content():
    """Rendert Warenkorb-Inhalt"""
    st.markdown("#### Reifen im Warenkorb")
    
    for item in st.session_state.cart_items:
        render_cart_item(item)

def render_cart_item(item):
    """Rendert ein einzelnes Warenkorb-Item"""
    st.markdown('<div class="cart-item">', unsafe_allow_html=True)
    
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
            "Stueckzahl:",
            min_value=1,
            max_value=8,
            value=current_qty,
            step=1,
            key=f"qty_{item['id']}"
        )
        st.session_state.cart_quantities[item['id']] = new_qty
        
        subtotal = item['Preis_EUR'] * new_qty
        st.markdown(f"**Summe: {subtotal:.2f}EUR**")
    
    with col_services:
        render_item_services(item)
    
    with col_remove:
        if st.button("Entfernen", key=f"remove_{item['id']}", help="Aus Warenkorb entfernen"):
            remove_from_cart(item['id'])
            st.rerun()
    
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
            ('4_raeder', f"4 Raeder ({service_prices.get('radwechsel_4_raeder', 39.90):.2f}EUR)"),
            ('3_raeder', f"3 Raeder ({service_prices.get('radwechsel_3_raeder', 29.95):.2f}EUR)"),
            ('2_raeder', f"2 Raeder ({service_prices.get('radwechsel_2_raeder', 19.95):.2f}EUR)"),
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
    st.markdown("#### Preisuebersicht")
    
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
    
    # Service-Zusammenfassung anzeigen
    if any(st.session_state.cart_services.values()):
        render_service_summary()

def render_service_summary():
    """Rendert Service-Zusammenfassung"""
    st.markdown("---")
    st.markdown("#### Service-Zusammenfassung")
    
    service_summary = {}
    for item in st.session_state.cart_items:
        item_services = st.session_state.cart_services.get(item['id'], {})
        
        if item_services.get('montage', False):
            service_summary['montage'] = service_summary.get('montage', 0) + 1
        
        if item_services.get('radwechsel', False):
            radwechsel_type = item_services.get('radwechsel_type', '4_raeder')
            service_summary[f'radwechsel_{radwechsel_type}'] = service_summary.get(f'radwechsel_{radwechsel_type}', 0) + 1
        
        if item_services.get('einlagerung', False):
            service_summary['einlagerung'] = service_summary.get('einlagerung', 0) + 1
    
    summary_text = []
    if service_summary.get('montage', 0) > 0:
        summary_text.append(f"- Montage fuer {service_summary['montage']} Reifen-Typ(en)")
    
    for key, count in service_summary.items():
        if key.startswith('radwechsel_') and count > 0:
            radwechsel_type = key.replace('radwechsel_', '')
            radwechsel_label = {
                '1_rad': '1 Rad', '2_raeder': '2 Raeder', '3_raeder': '3 Raeder', '4_raeder': '4 Raeder'
            }.get(radwechsel_type, '4 Raeder')
            summary_text.append(f"- Radwechsel {radwechsel_label} fuer {count} Reifen-Typ(en)")
    
    if service_summary.get('einlagerung', 0) > 0:
        summary_text.append(f"- Einlagerung fuer {service_summary['einlagerung']} Reifen-Typ(en)")
    
    if summary_text:
        for line in summary_text:
            st.markdown(line)

def render_customer_data():
    """Rendert Kundendaten-Eingabe"""
    st.markdown("---")
    st.markdown("#### Kundendaten (optional)")
    st.markdown("Diese Angaben werden in das Angebot aufgenommen, falls gewuenscht:")
    
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

def render_actions(total, breakdown):
    """Rendert Export & Aktionen"""
    st.markdown("---")
    st.markdown("#### Angebot erstellen")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        # Professionelles Angebot erstellen
        if st.button("Angebot erstellen", use_container_width=True, type="primary"):
            professional_offer = create_professional_offer(st.session_state.customer_data)
            
            # Angebot anzeigen
            st.markdown("---")
            st.markdown("### Ihr Angebot")
            st.markdown("*Das folgende Angebot koennen Sie kopieren und in Ihre E-Mail einfuegen:*")
            
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
        <p>Erstelle professionelle Angebote fuer deine Kunden</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Warenkorb leer?
    if not st.session_state.cart_items:
        render_empty_cart()
        return
    
    # Warenkorb Inhalt
    render_cart_content()
    
    # Preisberechnung
    total, breakdown = get_cart_total()
    render_price_summary(total, breakdown)
    
    # Kundendaten
    render_customer_data()
    
    # Export & Aktionen
    render_actions(total, breakdown)

if __name__ == "__main__":
    main()