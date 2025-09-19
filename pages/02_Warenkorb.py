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
# SESSION STATE INITIALISIERUNG
# ================================================================================================
def init_session_state():
    if 'customer_data' not in st.session_state:
        st.session_state.customer_data = {
            'anrede':'','name':'','email':'','kennzeichen':'','modell':'','fahrgestellnummer':'',
            'kennzeichen_2':'','modell_2':'','fahrgestellnummer_2':''
        }

    if 'cart_items' not in st.session_state: st.session_state.cart_items = []
    if 'cart_quantities' not in st.session_state: st.session_state.cart_quantities = {}
    if 'cart_services' not in st.session_state: st.session_state.cart_services = {}
    if 'cart_count' not in st.session_state: st.session_state.cart_count = 0

    if 'offer_scenario' not in st.session_state:
        st.session_state.offer_scenario = "vergleich"

    if 'pdf_created' not in st.session_state:
        st.session_state.pdf_created = False

    # Filial- und Mitarbeiter-Session States
    if 'selected_filial' not in st.session_state:
        st.session_state.selected_filial = ""
    if 'selected_mitarbeiter' not in st.session_state:
        st.session_state.selected_mitarbeiter = ""
    if 'selected_filial_info' not in st.session_state:
        st.session_state.selected_filial_info = {}
    if 'selected_mitarbeiter_info' not in st.session_state:
        st.session_state.selected_mitarbeiter_info = {}

    st.session_state.setdefault('customer_anrede', st.session_state.customer_data.get('anrede',''))
    st.session_state.setdefault('customer_name', st.session_state.customer_data.get('name',''))
    st.session_state.setdefault('customer_email', st.session_state.customer_data.get('email',''))
    st.session_state.setdefault('customer_kennzeichen', st.session_state.customer_data.get('kennzeichen',''))
    st.session_state.setdefault('customer_modell', st.session_state.customer_data.get('modell',''))
    st.session_state.setdefault('customer_fahrgestell', st.session_state.customer_data.get('fahrgestellnummer',''))
    
    # Fahrzeug 2 Session States
    st.session_state.setdefault('customer_kennzeichen_2', st.session_state.customer_data.get('kennzeichen_2',''))
    st.session_state.setdefault('customer_modell_2', st.session_state.customer_data.get('modell_2',''))
    st.session_state.setdefault('customer_fahrgestell_2', st.session_state.customer_data.get('fahrgestellnummer_2',''))

# ================================================================================================
# INTERNAL UTILITIES FOR WIDGET-STATE - ANGEPASST FÜR NEUE SERVICE-PAKETE
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
# RENDER FUNCTIONS - MIT SCHÖNER POSITIONS-ABTRENNUNG UND NEUEN SERVICE-PAKETEN
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
    """Rendert Service-Pakete für einen Reifen - KOMPLETT NEUE LOGIK"""
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

def render_customer_data():
    st.markdown("---")
    st.markdown("#### Kundendaten (optional)")
    st.markdown("Diese Angaben werden in das Angebot aufgenommen, falls gewünscht:")

    # Anrede-Dropdown prominent platziert - ganze Breite
    anrede_options = ["", "Herr", "Frau", "Firma"]
    st.selectbox("Anrede:", 
                 options=anrede_options, 
                 key="customer_anrede", 
                 help="Für personalisierte Ansprache in Angeboten und E-Mails")

    # Rest der Kundendaten in zwei Spalten
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Kundenname:", key="customer_name", placeholder="z.B. Max Mustermann")
        st.text_input("E-Mail-Adresse:", key="customer_email", placeholder="z.B. max@mustermann.de", help="Für den E-Mail-Versand des Angebots")
        st.text_input("Kennzeichen:", key="customer_kennzeichen", placeholder="z.B. GP-AB 123")
    with col2:
        st.text_input("Hersteller / Modell:", key="customer_modell", placeholder="z.B. BMW 3er E90")
        st.text_input("Fahrgestellnummer:", key="customer_fahrgestell", placeholder="z.B. WBAVA31070F123456")

    # Fahrzeug 2 Felder nur bei "separate" Szenario
    if st.session_state.offer_scenario == "separate":
        st.markdown("---")
        st.markdown("##### Fahrzeug 2 (Separate Fahrzeuge)")
        
        col3, col4 = st.columns(2)
        with col3:
            st.text_input("Kennzeichen 2:", key="customer_kennzeichen_2", placeholder="z.B. GP-CD 456")
            st.text_input("Hersteller / Modell 2:", key="customer_modell_2", placeholder="z.B. Audi A4 B9")
        with col4:
            st.text_input("Fahrgestellnummer 2:", key="customer_fahrgestell_2", placeholder="z.B. WAUEFE123456789")

    # Session State Update
    st.session_state.customer_data = {
        'anrede': st.session_state.get('customer_anrede',''),
        'name': st.session_state.get('customer_name',''),
        'email': st.session_state.get('customer_email',''),
        'kennzeichen': st.session_state.get('customer_kennzeichen',''),
        'modell': st.session_state.get('customer_modell',''),
        'fahrgestellnummer': st.session_state.get('customer_fahrgestell',''),
        'kennzeichen_2': st.session_state.get('customer_kennzeichen_2',''),
        'modell_2': st.session_state.get('customer_modell_2',''),
        'fahrgestellnummer_2': st.session_state.get('customer_fahrgestell_2','')
    }

def render_filial_mitarbeiter_selection():
    """Filial- und Mitarbeiterauswahl mit festen Datenstrukturen"""
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
    st.markdown("---")
    st.markdown("#### Angebot-Typ auswählen")

    detected = detect_cart_season(st.session_state.cart_items)
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
        st.info(f"**Vergleichsangebot:** Der Kunde bekommt mehrere {season_info['season_name']}-Reifenoptionen zur Auswahl präsentiert und kann sich für eine davon entscheiden.")
    elif st.session_state.offer_scenario == "separate":
        st.info(f"**Separate Fahrzeuge:** Jede Position wird als separates Fahrzeug behandelt mit eigenständiger {season_info['season_name']}-Reifen-Berechnung.")
    else:
        st.info(f"**Einzelangebot:** Direktes, spezifisches Angebot für die ausgewählten {season_info['season_name']}-Reifen ohne Vergleichsoptionen.")

    return detected

def render_actions(total, breakdown, detected_season):
    st.markdown("---")
    st.markdown("#### PDF-Angebot erstellen")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("📄 PDF-Angebot erstellen", use_container_width=True, type="primary"):
            # PDF mit importierten Funktionen erstellen
            pdf_data = create_professional_pdf(
                st.session_state.customer_data,
                st.session_state.offer_scenario,
                detected_season,
                st.session_state.cart_items,
                st.session_state.cart_quantities,
                st.session_state.cart_services,
                st.session_state.selected_filial_info,
                st.session_state.selected_mitarbeiter_info
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
        # Direkter mailto-Flow für Kundenangebot (mit Kunden-E-Mail)
        customer_email = st.session_state.customer_data.get('email', '').strip()
        if not customer_email:
            st.button("📧 E-Mail fehlt", use_container_width=True, disabled=True,
                      help="Bitte E-Mail-Adresse bei Kundendaten eingeben")
        elif not st.session_state.pdf_created:
            st.button("📧 Erst PDF erstellen", use_container_width=True, disabled=True,
                      help="Bitte zuerst PDF-Angebot erstellen")
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
                st.rerun()
            else:
                st.warning("Warenkorb ist leer!")

# ================================================================================================
# MAIN
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