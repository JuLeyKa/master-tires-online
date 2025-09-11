import streamlit as st
import pandas as pd
from datetime import datetime
from utils import data_manager, cart_manager, apply_main_css, get_efficiency_emoji, get_stock_display

# Page Config
st.set_page_config(
    page_title="Warenkorb - Ramsperger",
    page_icon="🛒",
    layout="wide"
)

# CSS anwenden
apply_main_css()

def init_session_state():
    """Initialisiert Session State für Warenkorb"""
    if 'customer_data' not in st.session_state:
        st.session_state.customer_data = {
            'name': '',
            'kennzeichen': '',
            'modell': '',
            'fahrgestellnummer': ''
        }

def main():
    init_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🛒 Warenkorb & Angebotserstellung</h1>
        <p>Erstelle professionelle Angebote für deine Kunden</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Warenkorb leer?
    if not st.session_state.cart_items:
        render_empty_cart()
        return
    
    # Warenkorb Inhalt
    render_cart_content()
    
    # Preisberechnung
    total, breakdown = cart_manager.get_cart_total()
    render_price_summary(total, breakdown)
    
    # Kundendaten
    render_customer_data()
    
    # Export & Aktionen
    render_actions(total, breakdown)

def render_empty_cart():
    """Rendert leeren Warenkorb"""
    st.markdown("""
    <div class="cart-container">
        <h3>Der Warenkorb ist leer</h3>
        <p>Gehe zur <strong>Reifen Suche</strong> und wähle Reifen für dein Angebot aus.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔍 Zur Reifen Suche", use_container_width=True, type="primary"):
        st.switch_page("pages/01_🔍_Reifen_Suche.py")

def render_cart_content():
    """Rendert Warenkorb-Inhalt"""
    st.markdown("#### 🔧 Reifen im Warenkorb")
    
    for item in st.session_state.cart_items:
        render_cart_item(item)

def render_cart_item(item):
    """Rendert ein einzelnes Warenkorb-Item"""
    st.markdown('<div class="cart-item">', unsafe_allow_html=True)
    
    col_info, col_qty, col_services, col_remove = st.columns([3, 1, 2, 1])
    
    with col_info:
        st.markdown(f"**{item['Reifengröße']}** - {item['Fabrikat']} {item['Profil']}")
        st.markdown(f"Teilenummer: {item['Teilenummer']} | Einzelpreis: **{item['Preis_EUR']:.2f}€**")
        
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
        
        subtotal = item['Preis_EUR'] * new_qty
        st.markdown(f"**Summe: {subtotal:.2f}€**")
    
    with col_services:
        render_item_services(item)
    
    with col_remove:
        if st.button("🗑️", key=f"remove_{item['id']}", help="Aus Warenkorb entfernen"):
            cart_manager.remove_from_cart(item['id'])
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
    service_prices = data_manager.get_service_prices()
    
    # Montage
    zoll_size = item['Zoll']
    if zoll_size <= 17:
        montage_price = service_prices.get('montage_bis_17', 25.0)
        montage_label = f"Montage ({montage_price:.2f}€/Stk)"
    elif zoll_size <= 19:
        montage_price = service_prices.get('montage_18_19', 30.0)
        montage_label = f"Montage ({montage_price:.2f}€/Stk)"
    else:
        montage_price = service_prices.get('montage_ab_20', 40.0)
        montage_label = f"Montage ({montage_price:.2f}€/Stk)"
    
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
            ('4_raeder', f"4 Räder ({service_prices.get('radwechsel_4_raeder', 39.90):.2f}€)"),
            ('3_raeder', f"3 Räder ({service_prices.get('radwechsel_3_raeder', 29.95):.2f}€)"),
            ('2_raeder', f"2 Räder ({service_prices.get('radwechsel_2_raeder', 19.95):.2f}€)"),
            ('1_rad', f"1 Rad ({service_prices.get('radwechsel_1_rad', 9.95):.2f}€)")
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
        f"Einlagerung ({service_prices.get('nur_einlagerung', 55.00):.2f}€)",
        value=current_services.get('einlagerung', False),
        key=f"cart_einlagerung_{item['id']}"
    )
    st.session_state.cart_services[item['id']]['einlagerung'] = einlagerung_selected

def render_price_summary(total, breakdown):
    """Rendert Preisübersicht"""
    st.markdown("---")
    st.markdown('<div class="total-box">', unsafe_allow_html=True)
    st.markdown("#### 💰 Preisübersicht")
    
    col_breakdown, col_total = st.columns([2, 1])
    
    with col_breakdown:
        st.markdown(f"**Reifen-Kosten:** {breakdown['reifen']:.2f}€")
        
        if breakdown['montage'] > 0:
            st.markdown(f"**Montage:** {breakdown['montage']:.2f}€")
        
        if breakdown['radwechsel'] > 0:
            st.markdown(f"**Radwechsel:** {breakdown['radwechsel']:.2f}€")
        
        if breakdown['einlagerung'] > 0:
            st.markdown(f"**Einlagerung:** {breakdown['einlagerung']:.2f}€")
    
    with col_total:
        st.markdown(f"### **GESAMT: {total:.2f}€**")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Service-Zusammenfassung anzeigen
    if any(st.session_state.cart_services.values()):
        render_service_summary()

def render_service_summary():
    """Rendert Service-Zusammenfassung"""
    st.markdown("---")
    st.markdown("#### 📋 Service-Zusammenfassung")
    
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
        summary_text.append(f"• Montage für {service_summary['montage']} Reifen-Typ(en)")
    
    for key, count in service_summary.items():
        if key.startswith('radwechsel_') and count > 0:
            radwechsel_type = key.replace('radwechsel_', '')
            radwechsel_label = {
                '1_rad': '1 Rad', '2_raeder': '2 Räder', '3_raeder': '3 Räder', '4_raeder': '4 Räder'
            }.get(radwechsel_type, '4 Räder')
            summary_text.append(f"• Radwechsel {radwechsel_label} für {count} Reifen-Typ(en)")
    
    if service_summary.get('einlagerung', 0) > 0:
        summary_text.append(f"• Einlagerung für {service_summary['einlagerung']} Reifen-Typ(en)")
    
    if summary_text:
        for line in summary_text:
            st.markdown(line)

def render_customer_data():
    """Rendert Kundendaten-Eingabe"""
    st.markdown("---")
    st.markdown("#### 👤 Kundendaten (optional)")
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

def render_actions(total, breakdown):
    """Rendert Export & Aktionen"""
    st.markdown("---")
    st.markdown("#### 📄 Angebot erstellen")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        # Professionelles Angebot erstellen
        if st.button("📄 Angebot erstellen", use_container_width=True, type="primary"):
            professional_offer = cart_manager.create_professional_offer(st.session_state.customer_data)
            
            # Angebot anzeigen
            st.markdown("---")
            st.markdown("### 📋 Ihr Angebot")
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
                label="📥 Angebot als Datei herunterladen",
                data=professional_offer,
                file_name=filename,
                mime="text/plain"
            )
    
    with col2:
        # Warenkorb leeren
        if st.button("🗑️ Warenkorb leeren", use_container_width=True, type="secondary"):
            cart_manager.clear_cart()
            st.success("Warenkorb geleert!")
            st.rerun()
    
    with col3:
        # Zurück zur Suche
        if st.button("🔍 Weitere Reifen", use_container_width=True):
            st.switch_page("pages/01_Reifen_Suche.py")
    
    with col4:
        # Service-Preise bearbeiten (für Admins)
        if st.button("⚙️ Service-Preise", use_container_width=True):
            st.switch_page("pages/03_Premium_Verwaltung.py")
    
    with col5:
        # Reifen ausbuchen
        if st.button("📦 Reifen ausbuchen", use_container_width=True, type="primary"):
            if st.session_state.cart_items:
                success, message = cart_manager.process_checkout(reduce_stock=True)
                
                if success:
                    st.success(f"✅ {message}")
                    cart_manager.clear_cart()
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.warning("Warenkorb ist leer!")

if __name__ == "__main__":
    main()