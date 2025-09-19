import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

# Import der ausgelagerten PDF- und Angebots-Funktionen - KORRIGIERTER IMPORT FÜR UTILS ORDNER
from utils.pdf_generator import (
    get_filial_data, get_filial_options, get_mitarbeiter_for_filial, get_filial_info, build_phone_number,
    load_service_packages, get_service_package_by_positionsnummer,
    create_personalized_salutation, detect_cart_season, get_season_greeting_text, 
    has_services_in_cart, get_dynamic_title, calculate_position_total, get_cart_total,
    create_professional_pdf, create_email_text, create_mailto_link,
    create_td_email_text, create_td_mailto_link
)

# Page Config
st.set_page_config(
    page_title="Warenkorb - Ramsperger",
    page_icon="🛒",
    layout="wide"
)

# ================================================================================================
# CSS STYLES - EINHEITLICH MIT REIFEN-SUCHE (OHNE CONTAINER-BOXEN)
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

    /* WICHTIG 1: Globale Reduktion des Top-Paddings für den Haupt-Content,
       damit das Logo höher startet (nahe der Sidebar-"app"-Zeile) */
    [data-testid="stAppViewContainer"] .block-container {
        padding-top: 0.5rem !important;   /* ggf. 0–1rem feinjustieren */
    }
    
    .main > div {
        padding-top: 0.2rem;
    }
    
    .stButton > button {
        border-radius: var(--border-radius); border: none; font-weight: 500; transition: all 0.2s ease;
        font-family: 'Inter', sans-serif;
    }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: var(--shadow-md); }
    
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 1.9rem 0 0.5rem 0;
        margin: 0; /* kein Margin-Konflikt */
    }

    /* WICHTIG 2: definierter Abstand NACH dem Logo – kollabiert nicht */
    .logo-spacer {
        height: 64px; /* -> bei Bedarf 48–80px anpassen */
    }
</style>
"""
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# ================================================================================================
# HELPER FUNCTIONS (APP) - ANGEPASST FÜR NEUE SERVICE-PAKETE
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

# ================================================================================================
# CART OPERATIONS - ANGEPASST FÜR NEUE SERVICE-PAKETE
# ================================================================================================
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

# ================================================================================================
# SESSION STATE INITIALISIERUNG - ERWEITERT UM NEUE FELDER
# ================================================================================================
def init_session_state():
    # ERWEITERTE KUNDENDATEN mit allen neuen Feldern
    if 'customer_data' not in st.session_state:
        st.session_state.customer_data = {
            # Basis-Kundendaten (bestehend)
            'anrede':'','name':'','email':'',
            # NEUE Adressfelder
            'strasse':'','hausnummer':'','plz':'','ort':'',
            # NEUE Geschäftsdaten  
            'kunden_nr':'','auftrags_nr':'','betriebs_nr':'',
            # Fahrzeugdaten (bestehend + neu)
            'kennzeichen':'','modell':'','fahrgestellnummer':'',
            # NEUE Fahrzeugdaten
            'typ_modellschluessel':'','erstzulassung':'','km_stand':'',
            # Fahrzeug 2 (bestehend + neu) 
            'kennzeichen_2':'','modell_2':'','fahrgestellnummer_2':'',
            'typ_modellschluessel_2':'','erstzulassung_2':'','km_stand_2':'',
            # NEUE Optionale Felder
            'abnehmer_gruppe':'','leistungsdatum':'','fahrzeugannahme':'','hu_au_datum':'',
            'abnehmer_gruppe_2':'','leistungsdatum_2':'','fahrzeugannahme_2':'','hu_au_datum_2':'',
            # Zusätzliche Angaben Toggle
            'zusaetzliche_angaben': False,
            'zusaetzliche_angaben_2': False
        }

    # Bestehende Cart Session States (unverändert)
    if 'cart_items' not in st.session_state: st.session_state.cart_items = []
    if 'cart_quantities' not in st.session_state: st.session_state.cart_quantities = {}
    if 'cart_services' not in st.session_state: st.session_state.cart_services = {}
    if 'cart_count' not in st.session_state: st.session_state.cart_count = 0

    if 'offer_scenario' not in st.session_state:
        st.session_state.offer_scenario = "vergleich"

    if 'pdf_created' not in st.session_state:
        st.session_state.pdf_created = False

    # Filial- und Mitarbeiter-Session States (unverändert)
    if 'selected_filial' not in st.session_state:
        st.session_state.selected_filial = ""
    if 'selected_mitarbeiter' not in st.session_state:
        st.session_state.selected_mitarbeiter = ""
    if 'selected_filial_info' not in st.session_state:
        st.session_state.selected_filial_info = {}
    if 'selected_mitarbeiter_info' not in st.session_state:
        st.session_state.selected_mitarbeiter_info = {}

    # ALLE Session State Keys für bestehende + neue Felder
    # Basis-Kundendaten
    st.session_state.setdefault('customer_anrede', st.session_state.customer_data.get('anrede',''))
    st.session_state.setdefault('customer_name', st.session_state.customer_data.get('name',''))
    st.session_state.setdefault('customer_email', st.session_state.customer_data.get('email',''))
    # Neue Adressfelder
    st.session_state.setdefault('customer_strasse', st.session_state.customer_data.get('strasse',''))
    st.session_state.setdefault('customer_hausnummer', st.session_state.customer_data.get('hausnummer',''))
    st.session_state.setdefault('customer_plz', st.session_state.customer_data.get('plz',''))
    st.session_state.setdefault('customer_ort', st.session_state.customer_data.get('ort',''))
    # Geschäftsdaten
    st.session_state.setdefault('customer_kunden_nr', st.session_state.customer_data.get('kunden_nr',''))
    st.session_state.setdefault('customer_auftrags_nr', st.session_state.customer_data.get('auftrags_nr',''))
    st.session_state.setdefault('customer_betriebs_nr', st.session_state.customer_data.get('betriebs_nr',''))
    # Fahrzeugdaten 1 (bestehend)
    st.session_state.setdefault('customer_kennzeichen', st.session_state.customer_data.get('kennzeichen',''))
    st.session_state.setdefault('customer_modell', st.session_state.customer_data.get('modell',''))
    st.session_state.setdefault('customer_fahrgestell', st.session_state.customer_data.get('fahrgestellnummer',''))
    # Fahrzeugdaten 1 (neu)
    st.session_state.setdefault('customer_typ_modellschluessel', st.session_state.customer_data.get('typ_modellschluessel',''))
    st.session_state.setdefault('customer_erstzulassung', st.session_state.customer_data.get('erstzulassung',''))
    st.session_state.setdefault('customer_km_stand', st.session_state.customer_data.get('km_stand',''))
    
    # Fahrzeug 2 (bestehend)
    st.session_state.setdefault('customer_kennzeichen_2', st.session_state.customer_data.get('kennzeichen_2',''))
    st.session_state.setdefault('customer_modell_2', st.session_state.customer_data.get('modell_2',''))
    st.session_state.setdefault('customer_fahrgestell_2', st.session_state.customer_data.get('fahrgestellnummer_2',''))
    # Fahrzeug 2 (neu)
    st.session_state.setdefault('customer_typ_modellschluessel_2', st.session_state.customer_data.get('typ_modellschluessel_2',''))
    st.session_state.setdefault('customer_erstzulassung_2', st.session_state.customer_data.get('erstzulassung_2',''))
    st.session_state.setdefault('customer_km_stand_2', st.session_state.customer_data.get('km_stand_2',''))
    
    # Optionale Felder
    st.session_state.setdefault('customer_abnehmer_gruppe', st.session_state.customer_data.get('abnehmer_gruppe',''))
    st.session_state.setdefault('customer_leistungsdatum', st.session_state.customer_data.get('leistungsdatum',''))
    st.session_state.setdefault('customer_fahrzeugannahme', st.session_state.customer_data.get('fahrzeugannahme',''))
    st.session_state.setdefault('customer_hu_au_datum', st.session_state.customer_data.get('hu_au_datum',''))
    # Optionale Felder Fahrzeug 2
    st.session_state.setdefault('customer_abnehmer_gruppe_2', st.session_state.customer_data.get('abnehmer_gruppe_2',''))
    st.session_state.setdefault('customer_leistungsdatum_2', st.session_state.customer_data.get('leistungsdatum_2',''))
    st.session_state.setdefault('customer_fahrzeugannahme_2', st.session_state.customer_data.get('fahrzeugannahme_2',''))
    st.session_state.setdefault('customer_hu_au_datum_2', st.session_state.customer_data.get('hu_au_datum_2',''))
    
    # Toggle States
    st.session_state.setdefault('customer_zusaetzliche_angaben', st.session_state.customer_data.get('zusaetzliche_angaben', False))
    st.session_state.setdefault('customer_zusaetzliche_angaben_2', st.session_state.customer_data.get('zusaetzliche_angaben_2', False))

# ================================================================================================
# INTERNAL UTILITIES FOR WIDGET-STATE - ANGEPASST FÜR NEUE SERVICE-PAKETE (UNVERÄNDERT)
# ================================================================================================
def _ensure_item_defaults(item_id):
    st.session_state.setdefault(f"qty_{item_id}", st.session_state.cart_quantities.get(item_id, 4))
    # Service-Pakete sind jetzt Listen von Dictionaries
    st.session_state.cart_services.setdefault(item_id, [])

def _update_qty(item_id):
    st.session_state.cart_quantities[item_id] = st.session_state.get(f"qty_{item_id}", 4)

def _clear_item_widget_keys(item_id):
    keys_to_clear = [f"qty_{item_id}"]
    # Alle Service-Package Keys für diesen Reifen löschen
    service_packages = load_service_packages()
    for _, package in service_packages.iterrows():
        key = f"service_{item_id}_{package['Positionsnummer']}"
        keys_to_clear.append(key)
    
    for key in keys_to_clear:
        st.session_state.pop(key, None)

# ================================================================================================
# RENDER FUNCTIONS - MIT SCHÖNER POSITIONS-ABTRENNUNG UND NEUEN SERVICE-PAKETEN (UNVERÄNDERT)
# ================================================================================================
def render_empty_cart():
    st.markdown("### Der Warenkorb ist leer")
    st.markdown("Gehe zur **Reifen Suche** und wähle Reifen für dein Angebot aus.")
    if st.button("Zur Reifen Suche", use_container_width=True, type="primary"):
        st.switch_page("pages/01_Reifen_Suche.py")

def render_cart_content():
    st.markdown("#### Reifen im Warenkorb")
    for i, item in enumerate(st.session_state.cart_items, 1):
        render_cart_item(item, i)
        
        # Schöne Abtrennung zwischen Positionen (nur wenn nicht die letzte Position)
        if i < len(st.session_state.cart_items):
            st.markdown("---")

def render_cart_item(item, position_number):
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

    # Kosten berechnen mit neuen Service-Paketen
    quantity = st.session_state.cart_quantities.get(item_id, 4)
    selected_packages = st.session_state.cart_services.get(item_id, [])
    reifen_kosten, service_kosten, position_total = calculate_position_total(item, quantity, selected_packages)
    
    st.markdown(f"### **Position {position_number} Gesamt: {position_total:.2f} EUR**")
    st.markdown(f"Reifen: {reifen_kosten:.2f}EUR + Services: {service_kosten:.2f}EUR")

def render_item_services(item):
    """Rendert Service-Pakete für einen Reifen - KOMPLETT NEUE LOGIK (UNVERÄNDERT)"""
    item_id = item['id']
    _ensure_item_defaults(item_id)

    st.markdown("**Service-Pakete:**")
    
    # Service-Pakete für diese Reifengröße laden
    tire_zoll = item['Zoll']
    service_df = load_service_packages()
    
    if service_df.empty:
        st.info("Keine Service-Pakete verfügbar.")
        return
    
    # Verfügbare Pakete filtern (gleiche Logik wie in Reifen Suche)
    available_packages = []
    
    for _, package in service_df.iterrows():
        package_zoll = package.get('Zoll', None)
        
        # Wenn kein Zoll angegeben (None oder NaN), dann für alle Größen verfügbar
        if pd.isna(package_zoll) or package_zoll is None or package_zoll == '':
            available_packages.append(package)
            continue
            
        # Zoll-Beschränkungen prüfen
        package_zoll_str = str(package_zoll).strip()
        
        if package_zoll_str == '-17':
            # Bis 17 Zoll
            if tire_zoll <= 17:
                available_packages.append(package)
        elif package_zoll_str == '18-19':
            # 18-19 Zoll
            if 18 <= tire_zoll <= 19:
                available_packages.append(package)
        elif package_zoll_str == '20-':
            # Ab 20 Zoll
            if tire_zoll >= 20:
                available_packages.append(package)
        else:
            # Unbekannte Zoll-Angabe - vorsichtshalber anzeigen
            available_packages.append(package)
    
    if not available_packages:
        st.info("Keine passenden Service-Pakete für diese Reifengröße.")
        return
    
    # Aktuelle Auswahl aus Session State laden
    current_selection = st.session_state.cart_services.get(item_id, [])
    current_positionsnummern = {pkg['positionsnummer'] for pkg in current_selection}
    
    # Service-Pakete als Checkboxen anzeigen
    new_selection = []
    
    for package in available_packages:
        package_key = f"service_{item_id}_{package['Positionsnummer']}"
        pkg_price = float(package['Preis'])
        
        # Beschreibung mit Hinweis
        description = package['Bezeichnung']
        if pd.notna(package['Hinweis']) and package['Hinweis'].strip() != '':
            description += f" ({package['Hinweis']})"
        
        # Checkbox für Paket - aktuelle Auswahl berücksichtigen
        is_selected = package['Positionsnummer'] in current_positionsnummern
        
        checkbox_value = st.checkbox(
            f"{description} - {pkg_price:.2f}€",
            value=is_selected,
            key=package_key
        )
        
        if checkbox_value:
            new_selection.append({
                'positionsnummer': package['Positionsnummer'],
                'bezeichnung': package['Bezeichnung'],
                'preis': pkg_price,
                'hinweis': package['Hinweis'] if pd.notna(package['Hinweis']) else ''
            })
    
    # Service-Auswahl in Session State speichern
    st.session_state.cart_services[item_id] = new_selection

def render_price_summary(total, breakdown):
    st.markdown("---")
    st.markdown("#### Preisübersicht")
    col_breakdown, col_total = st.columns([2, 1])
    with col_breakdown:
        st.markdown(f"**Reifen-Kosten:** {breakdown['reifen']:.2f}EUR")
        if breakdown['services']>0: 
            st.markdown(f"**Service-Pakete:** {breakdown['services']:.2f}EUR")
    with col_total:
        st.markdown(f"### **GESAMT: {total:.2f}EUR**")

# ================================================================================================
# ERWEITERTE KUNDENDATEN EINGABE - KOMPLETT NEUE STRUCTURE
# ================================================================================================
def render_customer_data():
    st.markdown("---")
    st.markdown("#### Kundendaten (optional)")
    st.markdown("Diese Angaben werden in das Angebot aufgenommen, falls gewünscht:")

    # === PERSÖNLICHE DATEN ===
    st.markdown("##### Persönliche Daten")
    col1, col2 = st.columns(2)
    
    with col1:
        # Anrede-Dropdown prominent platziert
        anrede_options = ["", "Herr", "Frau", "Firma"]
        st.selectbox("Anrede:", 
                     options=anrede_options, 
                     key="customer_anrede", 
                     help="Für personalisierte Ansprache in Angeboten und E-Mails")
        st.text_input("Kundenname:", key="customer_name", placeholder="z.B. Max Mustermann")
        st.text_input("E-Mail-Adresse:", key="customer_email", placeholder="z.B. max@mustermann.de", 
                      help="Für den E-Mail-Versand des Angebots")

    with col2:
        # NEUE Adressfelder (getrennt)
        st.text_input("Straße:", key="customer_strasse", placeholder="z.B. Musterstraße")
        st.text_input("Hausnummer:", key="customer_hausnummer", placeholder="z.B. 12a")
        col_plz, col_ort = st.columns([1, 2])
        with col_plz:
            st.text_input("PLZ:", key="customer_plz", placeholder="z.B. 12345")
        with col_ort:
            st.text_input("Ort:", key="customer_ort", placeholder="z.B. Musterstadt")

    # === GESCHÄFTSDATEN ===
    st.markdown("##### Geschäftsdaten")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.text_input("Kunden-Nr.:", key="customer_kunden_nr", placeholder="z.B. 12345")
    with col4:
        st.text_input("Auftrags-Nr.:", key="customer_auftrags_nr", placeholder="z.B. A-2025-001")
    with col5:
        st.text_input("Betriebs-Nr.:", key="customer_betriebs_nr", placeholder="z.B. 26727")

    # === FAHRZEUGDATEN 1 ===
    st.markdown("##### Fahrzeug 1")
    col6, col7 = st.columns(2)
    
    with col6:
        st.text_input("Kennzeichen:", key="customer_kennzeichen", placeholder="z.B. GP-AB 123")
        st.text_input("Hersteller / Modell:", key="customer_modell", placeholder="z.B. BMW 3er E90")
        st.text_input("Fahrgestellnummer:", key="customer_fahrgestell", placeholder="z.B. WBAVA31070F123456")

    with col7:
        # NEUE Fahrzeugfelder
        st.text_input("Typ/Modellschlüssel:", key="customer_typ_modellschluessel", placeholder="z.B. D115LE")
        st.date_input("Datum Erstzulassung:", key="customer_erstzulassung", value=None, help="Erstzulassung des Fahrzeugs")
        st.text_input("km-Stand:", key="customer_km_stand", placeholder="z.B. 23000")

    # === ZUSÄTZLICHE ANGABEN FAHRZEUG 1 (Optional) ===
    zusaetzliche_angaben = st.checkbox("Zusätzliche Angaben für Fahrzeug 1", 
                                     key="customer_zusaetzliche_angaben",
                                     help="Weitere optionale Felder anzeigen")
    
    if zusaetzliche_angaben:
        st.markdown("**Zusätzliche Angaben Fahrzeug 1:**")
        col8, col9 = st.columns(2)
        
        with col8:
            st.text_input("Abnehmer-Gruppe:", key="customer_abnehmer_gruppe", placeholder="z.B. 81")
            st.date_input("Leistungsdatum:", key="customer_leistungsdatum", value=None)
        
        with col9:
            st.date_input("Fahrzeugannahmedatum:", key="customer_fahrzeugannahme", value=None)
            st.text_input("HU/AU Datum:", key="customer_hu_au_datum", placeholder="z.B. 06/2027")

    # === FAHRZEUG 2 (nur bei "separate" Szenario) ===
    if st.session_state.offer_scenario == "separate":
        st.markdown("---")
        st.markdown("##### Fahrzeug 2 (Separate Fahrzeuge)")
        
        col10, col11 = st.columns(2)
        
        with col10:
            st.text_input("Kennzeichen 2:", key="customer_kennzeichen_2", placeholder="z.B. GP-CD 456")
            st.text_input("Hersteller / Modell 2:", key="customer_modell_2", placeholder="z.B. Audi A4 B9")
            st.text_input("Fahrgestellnummer 2:", key="customer_fahrgestell_2", placeholder="z.B. WAUEFE123456789")

        with col11:
            # NEUE Fahrzeugfelder 2
            st.text_input("Typ/Modellschlüssel 2:", key="customer_typ_modellschluessel_2", placeholder="z.B. B8K")
            st.date_input("Datum Erstzulassung 2:", key="customer_erstzulassung_2", value=None)
            st.text_input("km-Stand 2:", key="customer_km_stand_2", placeholder="z.B. 45000")

        # === ZUSÄTZLICHE ANGABEN FAHRZEUG 2 (Optional) ===
        zusaetzliche_angaben_2 = st.checkbox("Zusätzliche Angaben für Fahrzeug 2", 
                                           key="customer_zusaetzliche_angaben_2",
                                           help="Weitere optionale Felder für Fahrzeug 2 anzeigen")
        
        if zusaetzliche_angaben_2:
            st.markdown("**Zusätzliche Angaben Fahrzeug 2:**")
            col12, col13 = st.columns(2)
            
            with col12:
                st.text_input("Abnehmer-Gruppe 2:", key="customer_abnehmer_gruppe_2", placeholder="z.B. 82")
                st.date_input("Leistungsdatum 2:", key="customer_leistungsdatum_2", value=None)
            
            with col13:
                st.date_input("Fahrzeugannahmedatum 2:", key="customer_fahrzeugannahme_2", value=None)
                st.text_input("HU/AU Datum 2:", key="customer_hu_au_datum_2", placeholder="z.B. 12/2026")

    # === Session State Update mit ALLEN Feldern ===
    st.session_state.customer_data = {
        # Basis-Kundendaten
        'anrede': st.session_state.get('customer_anrede',''),
        'name': st.session_state.get('customer_name',''),
        'email': st.session_state.get('customer_email',''),
        # Neue Adressfelder
        'strasse': st.session_state.get('customer_strasse',''),
        'hausnummer': st.session_state.get('customer_hausnummer',''),
        'plz': st.session_state.get('customer_plz',''),
        'ort': st.session_state.get('customer_ort',''),
        # Geschäftsdaten
        'kunden_nr': st.session_state.get('customer_kunden_nr',''),
        'auftrags_nr': st.session_state.get('customer_auftrags_nr',''),
        'betriebs_nr': st.session_state.get('customer_betriebs_nr',''),
        # Fahrzeugdaten 1 (bestehend)
        'kennzeichen': st.session_state.get('customer_kennzeichen',''),
        'modell': st.session_state.get('customer_modell',''),
        'fahrgestellnummer': st.session_state.get('customer_fahrgestell',''),
        # Fahrzeugdaten 1 (neu)
        'typ_modellschluessel': st.session_state.get('customer_typ_modellschluessel',''),
        'erstzulassung': st.session_state.get('customer_erstzulassung', None),
        'km_stand': st.session_state.get('customer_km_stand',''),
        # Fahrzeug 2 (bestehend)
        'kennzeichen_2': st.session_state.get('customer_kennzeichen_2',''),
        'modell_2': st.session_state.get('customer_modell_2',''),
        'fahrgestellnummer_2': st.session_state.get('customer_fahrgestell_2',''),
        # Fahrzeug 2 (neu)
        'typ_modellschluessel_2': st.session_state.get('customer_typ_modellschluessel_2',''),
        'erstzulassung_2': st.session_state.get('customer_erstzulassung_2', None),
        'km_stand_2': st.session_state.get('customer_km_stand_2',''),
        # Optionale Felder
        'abnehmer_gruppe': st.session_state.get('customer_abnehmer_gruppe',''),
        'leistungsdatum': st.session_state.get('customer_leistungsdatum', None),
        'fahrzeugannahme': st.session_state.get('customer_fahrzeugannahme', None),
        'hu_au_datum': st.session_state.get('customer_hu_au_datum',''),
        # Optionale Felder Fahrzeug 2
        'abnehmer_gruppe_2': st.session_state.get('customer_abnehmer_gruppe_2',''),
        'leistungsdatum_2': st.session_state.get('customer_leistungsdatum_2', None),
        'fahrzeugannahme_2': st.session_state.get('customer_fahrzeugannahme_2', None),
        'hu_au_datum_2': st.session_state.get('customer_hu_au_datum_2',''),
        # Toggle States
        'zusaetzliche_angaben': st.session_state.get('customer_zusaetzliche_angaben', False),
        'zusaetzliche_angaben_2': st.session_state.get('customer_zusaetzliche_angaben_2', False)
    }

# ================================================================================================
# BESTEHENDE FUNKTIONEN (UNVERÄNDERT)
# ================================================================================================
def render_filial_mitarbeiter_selection():
    """Filial- und Mitarbeiterauswahl mit festen Datenstrukturen (UNVERÄNDERT)"""
    st.markdown("---")
    st.markdown("#### Filiale und Ansprechpartner auswählen")
    st.markdown("Diese Informationen werden in das Angebot und den Footer aufgenommen:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Filial-Dropdown
        filial_options = get_filial_options()
        selected_filial = st.selectbox(
            "Filiale:",
            options=[""] + [key for key, _ in filial_options],
            format_func=lambda x: "Bitte wählen..." if x == "" else next((name for key, name in filial_options if key == x), x),
            key="selected_filial_key",
            help="Auswahl der Filiale für Adresse und Telefon im PDF"
        )
        
        # Filial-Info in Session State speichern
        if selected_filial:
            st.session_state.selected_filial = selected_filial
            st.session_state.selected_filial_info = get_filial_info(selected_filial)
        else:
            st.session_state.selected_filial = ""
            st.session_state.selected_filial_info = {}
    
    with col2:
        # Mitarbeiter-Dropdown (nur wenn Filiale gewählt)
        if st.session_state.selected_filial:
            mitarbeiter = get_mitarbeiter_for_filial(st.session_state.selected_filial)
            
            if mitarbeiter:
                selected_mitarbeiter_idx = st.selectbox(
                    "Ansprechpartner:",
                    options=list(range(-1, len(mitarbeiter))),
                    format_func=lambda x: ("Bitte wählen..." if x == -1 else 
                                          f"{mitarbeiter[x]['name']}" if "E-Mail" in mitarbeiter[x]['position'] else
                                          f"{mitarbeiter[x]['name']} ({mitarbeiter[x]['position']})" if x >= 0 else ""),
                    key="selected_mitarbeiter_key",
                    help="Auswahl des Ansprechpartners für das PDF"
                )
                
                # Mitarbeiter-Info in Session State speichern
                if selected_mitarbeiter_idx >= 0:
                    st.session_state.selected_mitarbeiter = selected_mitarbeiter_idx
                    st.session_state.selected_mitarbeiter_info = mitarbeiter[selected_mitarbeiter_idx]
                else:
                    st.session_state.selected_mitarbeiter = ""
                    st.session_state.selected_mitarbeiter_info = {}
            else:
                st.info("Keine Mitarbeiter für diese Filiale verfügbar")
        else:
            st.selectbox("Ansprechpartner:", options=[], disabled=True, help="Bitte zuerst eine Filiale auswählen")
    
    # Vorschau der ausgewählten Informationen
    if st.session_state.selected_filial_info and st.session_state.selected_mitarbeiter_info:
        st.markdown("##### Vorschau der Auswahl:")
        filial_info = st.session_state.selected_filial_info
        mitarbeiter_info = st.session_state.selected_mitarbeiter_info
        
        col_preview1, col_preview2 = st.columns(2)
        
        with col_preview1:
            st.markdown("**Filiale:**")
            st.markdown(f"{filial_info.get('bereich', '')}")
            st.markdown(f"{filial_info.get('adresse', '')}")
            st.markdown(f"Telefon: {filial_info.get('zentrale', '')}")
        
        with col_preview2:
            st.markdown("**Ansprechpartner:**")
            st.markdown(f"**{mitarbeiter_info.get('name', '')}**")
            if mitarbeiter_info.get('position') and not mitarbeiter_info.get('position', '').endswith("E-Mail"):
                st.markdown(f"{mitarbeiter_info.get('position', '')}")
            if mitarbeiter_info.get('durchwahl'):
                telefon = build_phone_number(filial_info.get('zentrale', ''), mitarbeiter_info.get('durchwahl', ''))
                st.markdown(f"Telefon: {telefon}")
            if mitarbeiter_info.get('email'):
                st.markdown(f"E-Mail: {mitarbeiter_info.get('email', '')}")

def render_scenario_selection():
    # ANGEBOT-TYP AUSWAHL ENTFERNT - Automatisch ein Angebot pro Position
    detected = detect_cart_season(st.session_state.cart_items)
    season_info = get_season_greeting_text(detected)
    
    # Automatisch auf "einzelangebot" setzen (wird für PDF-Erstellung verwendet)
    st.session_state.offer_scenario = "einzelangebot"
    
    st.markdown("---")
    st.markdown("#### Angebot-Erstellung")
    num_positions = len(st.session_state.cart_items)
    if num_positions > 1:
        st.info(f"**{num_positions} separate Angebote:** Für jede Reifenposition wird ein eigenes Angebot erstellt ({season_info['season_name']}-Reifen).")
    else:
        st.info(f"**Einzelangebot:** Ein Angebot für die ausgewählten {season_info['season_name']}-Reifen wird erstellt.")

    return detected

def render_actions(total, breakdown, detected_season):
    st.markdown("---")
    st.markdown("#### PDF-Angebote erstellen")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("📄 PDF-Angebote erstellen", use_container_width=True, type="primary"):
            # Ein PDF pro Position erstellen
            created_pdfs = []
            
            for i, item in enumerate(st.session_state.cart_items, 1):
                # Einzelposition für PDF
                single_item = [item]
                single_quantities = {item['id']: st.session_state.cart_quantities.get(item['id'], 4)}
                single_services = {item['id']: st.session_state.cart_services.get(item['id'], [])}
                
                pdf_data = create_professional_pdf(
                    st.session_state.customer_data,
                    st.session_state.offer_scenario,
                    detected_season,
                    single_item,  # Nur eine Position
                    single_quantities,
                    single_services,
                    st.session_state.selected_filial_info,
                    st.session_state.selected_mitarbeiter_info
                )
                
                if pdf_data:
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    season_info = get_season_greeting_text(detected_season)
                    # Dateiname mit Position
                    filename = f"Angebot_Ramsperger_Position_{i}_{season_info['season_name']}_{ts}.pdf"
                    created_pdfs.append((pdf_data, filename, i))
            
            if created_pdfs:
                st.session_state.current_email_text = create_email_text(
                    st.session_state.customer_data,
                    detected_season
                )
                st.session_state.created_pdfs = created_pdfs
                
                st.success(f"✅ {len(created_pdfs)} PDF-Angebote erfolgreich erstellt!")
                
                # Download-Buttons für alle PDFs
                for pdf_data, filename, position in created_pdfs:
                    st.download_button(
                        label=f"📥 Position {position} herunterladen",
                        data=pdf_data,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                st.session_state.pdf_created = True
            else:
                st.error("Fehler beim Erstellen der PDF-Dateien")

    with col2:
        # Direkter mailto-Flow für Kundenangebot (mit Kunden-E-Mail)
        customer_email = st.session_state.customer_data.get('email', '').strip()
        if not customer_email:
            st.button("📧 E-Mail fehlt", use_container_width=True, disabled=True,
                      help="Bitte E-Mail-Adresse bei Kundendaten eingeben")
        elif not st.session_state.pdf_created:
            st.button("📧 Erst PDF erstellen", use_container_width=True, disabled=True,
                      help="Bitte zuerst PDF-Angebote erstellen")
        else:
            mailto_link = create_mailto_link(
                customer_email,
                st.session_state.get('current_email_text', create_email_text(st.session_state.customer_data, detected_season)),
                detected_season
            )
            if mailto_link:
                st.link_button("📧 Per E-Mail senden", mailto_link,
                               use_container_width=True, type="secondary",
                               help="Öffnet Ihren Standard-Mailclient (z. B. Outlook Desktop)")
            else:
                st.button("📧 Ungültige E-Mail", use_container_width=True, disabled=True,
                          help="Bitte E-Mail-Adresse prüfen")

    with col3:
        # TD-Anfrage Button - IMMER AKTIV, KEIN Empfänger vorgefüllt
        td_email_text = create_td_email_text(
            st.session_state.customer_data, 
            detected_season,
            st.session_state.cart_items,
            st.session_state.cart_quantities
        )
        td_mailto_link = create_td_mailto_link(td_email_text, st.session_state.cart_items)
        
        st.link_button("🔍 Reifen über TD anfragen", td_mailto_link,
                       use_container_width=True, type="secondary",
                       help="Anfrage an Teiledienst - Öffnet Outlook mit leerem An-Feld")

    with col4:
        if st.button("Warenkorb leeren", use_container_width=True, type="secondary"):
            clear_cart()
            st.session_state.pdf_created = False
            if 'created_pdfs' in st.session_state:
                del st.session_state.created_pdfs
            st.success("Warenkorb geleert!")
            st.rerun()

    with col5:
        if st.button("Weitere Reifen", use_container_width=True):
            st.switch_page("pages/01_Reifen_Suche.py")

    # Zweite Reihe für weniger wichtige Aktionen
    col6, col7, col8, col9, col10 = st.columns(5)
    
    with col10:
        if st.button("Reifen ausbuchen", use_container_width=True, type="primary"):
            if st.session_state.cart_items:
                st.success("Reifen erfolgreich ausgebucht!")
                clear_cart()
                st.session_state.pdf_created = False
                if 'created_pdfs' in st.session_state:
                    del st.session_state.created_pdfs
                st.rerun()
            else:
                st.warning("Warenkorb ist leer!")

# ================================================================================================
# MAIN (UNVERÄNDERT)
# ================================================================================================
def main():
    init_session_state()

    # Logo Header ganz oben - EINHEITLICH WIE REIFEN-SUCHE
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    try:
        logo_path = "data/Logo_2.png"
        st.image(logo_path, width=400)
    except:
        st.markdown("### Ramsperger Automobile")
    st.markdown('</div>', unsafe_allow_html=True)

    # Fester Abstand NACH dem Logo (robust gegen Margin-Collapse)
    st.markdown('<div class="logo-spacer"></div>', unsafe_allow_html=True)

    if not st.session_state.cart_items:
        render_empty_cart()
        return

    render_cart_content()
    total, breakdown = get_cart_total(
        st.session_state.cart_items, 
        st.session_state.cart_quantities, 
        st.session_state.cart_services
    )
    render_price_summary(total, breakdown)
    render_customer_data()
    
    # Filial- und Mitarbeiterauswahl mit festen Datenstrukturen
    render_filial_mitarbeiter_selection()
    
    detected = render_scenario_selection()
    render_actions(total, breakdown, detected)

if __name__ == "__main__":
    main()