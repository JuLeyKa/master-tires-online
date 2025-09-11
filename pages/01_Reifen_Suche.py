import streamlit as st
import pandas as pd
import io
from datetime import datetime
import numpy as np
from pathlib import Path

# Page Config
st.set_page_config(
    page_title="Reifen Suche - Ramsperger",
    page_icon="🔍",
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
    
    .config-card {
        border: 2px solid var(--primary-color);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        box-shadow: var(--shadow-md);
    }
    
    [data-testid="metric-container"] {
        background: var(--background-white);
        border: 1px solid var(--border-color);
        padding: 1rem;
        border-radius: var(--border-radius);
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

def create_metric_card(title, value, delta=None, help_text=None):
    """Erstellt eine ansprechende Metrik-Karte"""
    delta_html = ""
    if delta:
        delta_color = "var(--success-color)" if delta.startswith("↗") else "var(--error-color)" if delta.startswith("↘") else "var(--text-secondary)"
        delta_html = f'<div style="color: {delta_color}; font-size: 0.9rem; margin-top: 0.25rem;">{delta}</div>'
    
    help_html = ""
    if help_text:
        help_html = f'<div style="color: var(--text-secondary); font-size: 0.8rem; margin-top: 0.5rem;">{help_text}</div>'
    
    return f"""
    <div style="
        background: var(--background-white);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        box-shadow: var(--shadow-sm);
        transition: transform 0.2s ease;
    " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="color: var(--text-secondary); font-size: 0.9rem; font-weight: 500;">{title}</div>
        <div style="color: var(--text-primary); font-size: 1.8rem; font-weight: 700; margin: 0.25rem 0;">{value}</div>
        {delta_html}
        {help_html}
    </div>
    """

def clean_dataframe(df):
    """Bereinigt und normalisiert DataFrame"""
    if df.empty:
        return df
    
    # Preis bereinigen
    if "Preis_EUR" in df.columns:
        if df["Preis_EUR"].dtype == object:
            df["Preis_EUR"] = (
                df["Preis_EUR"]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .str.replace("€", "", regex=False)
                .str.strip()
            )
        df["Preis_EUR"] = pd.to_numeric(df["Preis_EUR"], errors="coerce")
    
    # Dimensionen bereinigen
    for c in ["Breite", "Hoehe", "Zoll"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    
    # Bestand als Float (negative Werte erlaubt)
    if "Bestand" in df.columns:
        df["Bestand"] = pd.to_numeric(df["Bestand"], errors="coerce")
    
    # Fehlende Spalten ergänzen
    required_cols = ["Fabrikat", "Profil", "Kraftstoffeffizienz", "Nasshaftung", 
                    "Loadindex", "Speedindex", "Teilenummer"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = pd.NA
    
    # Leere Zeilen entfernen
    df = df.dropna(subset=["Preis_EUR", "Breite", "Hoehe", "Zoll"], how="any")
    
    if not df.empty:
        df["Breite"] = df["Breite"].astype(int)
        df["Hoehe"] = df["Hoehe"].astype(int)
        df["Zoll"] = df["Zoll"].astype(int)
    
    return df

# ================================================================================================
# DATA MANAGEMENT - DIREKT EINGEBETTET
# ================================================================================================
def load_data_from_files():
    """Lädt echte Daten aus dem data/ Ordner"""
    data_dir = Path("data")
    
    # Master CSV laden - Haupt-Reifendatenbank
    master_csv_path = data_dir / "Ramsperger_Winterreifen_20250826_160010.csv"
    central_csv_path = data_dir / "ramsperger_central_database.csv"
    services_csv_path = data_dir / "ramsperger_services_config.csv"
    premium_excel_path = data_dir / "2025-07-29_ReifenPremium_Winterreifen_2025-26.xlsx"
    
    # Master-Daten laden
    master_data = pd.DataFrame()
    try:
        if master_csv_path.exists():
            master_data = pd.read_csv(master_csv_path)
            master_data = clean_dataframe(master_data)
            st.session_state.master_data = master_data
        else:
            st.error(f"Master-Datei nicht gefunden: {master_csv_path}")
    except Exception as e:
        st.error(f"Fehler beim Laden der Master-CSV: {e}")
        # Fallback zu Beispieldaten
        init_fallback_data()
        return

    # Zentrale Datenbank laden
    central_data = pd.DataFrame()
    try:
        if central_csv_path.exists():
            central_data = pd.read_csv(central_csv_path)
            central_data = clean_dataframe(central_data)
            st.session_state.central_data = central_data
        else:
            st.session_state.central_data = pd.DataFrame()
    except Exception as e:
        st.warning(f"Zentrale Datenbank nicht verfuegbar: {e}")
        st.session_state.central_data = pd.DataFrame()

    # Service-Konfiguration laden
    try:
        if services_csv_path.exists():
            services_config = pd.read_csv(services_csv_path)
            st.session_state.services_config = services_config
        else:
            # Standard Services
            init_default_services()
    except Exception as e:
        st.warning(f"Service-Konfiguration nicht verfuegbar: {e}")
        init_default_services()
    
    # Premium Excel für neue Reifen laden (wird in Premium Verwaltung genutzt)
    try:
        if premium_excel_path.exists():
            premium_data = pd.read_excel(premium_excel_path)
            premium_data = clean_dataframe(premium_data)
            st.session_state.premium_excel_data = premium_data
        else:
            st.session_state.premium_excel_data = pd.DataFrame()
    except Exception as e:
        st.warning(f"Premium Excel nicht verfuegbar: {e}")
        st.session_state.premium_excel_data = pd.DataFrame()

def init_default_services():
    """Initialisiert Standard Service-Konfiguration"""
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

def init_fallback_data():
    """Fallback Beispiel-Daten falls echte Dateien nicht geladen werden können"""
    sample_data = {
        'Breite': [195, 205, 215, 225],
        'Hoehe': [65, 55, 60, 55],
        'Zoll': [15, 16, 16, 17],
        'Fabrikat': ['Continental', 'Michelin', 'Bridgestone', 'Pirelli'],
        'Profil': ['WinterContact TS850', 'Alpin 6', 'Blizzak LM005', 'Winter Sottozero 3'],
        'Teilenummer': ['15494940000', '03528700000', '19394', '8019227308853'],
        'Preis_EUR': [89.90, 95.50, 87.20, 99.90],
        'Loadindex': [91, 91, 94, 94],
        'Speedindex': ['T', 'H', 'H', 'V'],
        'Kraftstoffeffizienz': ['C', 'B', 'A', 'C'],
        'Nasshaftung': ['B', 'A', 'A', 'B'],
        'Bestand': [25, 12, 8, 15]
    }
    st.session_state.master_data = pd.DataFrame(sample_data)
    st.session_state.central_data = pd.DataFrame()
    init_default_services()

def init_sample_data():
    """Hauptfunktion - lädt echte Daten oder Fallback"""
    # Nur beim ersten Start laden
    if 'data_loaded' not in st.session_state:
        load_data_from_files()
        st.session_state.data_loaded = True

def get_combined_data():
    """Kombiniert Master und Central Data"""
    init_sample_data()
    
    master_data = st.session_state.master_data
    central_data = st.session_state.central_data
    
    if master_data.empty and central_data.empty:
        return pd.DataFrame()
    
    # Bestand-Spalte sicherstellen
    if not master_data.empty and 'Bestand' not in master_data.columns:
        master_data['Bestand'] = pd.NA
    if not central_data.empty and 'Bestand' not in central_data.columns:
        central_data['Bestand'] = pd.NA
    
    if master_data.empty:
        return clean_dataframe(central_data)
    if central_data.empty:
        return clean_dataframe(master_data)
    
    # Doppelte Teilenummern aus Central entfernen
    if 'Teilenummer' in master_data.columns and 'Teilenummer' in central_data.columns:
        master_teilenummern = set(master_data['Teilenummer'].dropna())
        central_data_filtered = central_data[~central_data['Teilenummer'].isin(master_teilenummern)]
        combined_df = pd.concat([master_data, central_data_filtered], ignore_index=True)
    else:
        combined_df = pd.concat([master_data, central_data], ignore_index=True)
    
    return clean_dataframe(combined_df)

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
def add_to_cart_with_config(tire_data, quantity, services):
    """Fügt einen Reifen mit Konfiguration zum Warenkorb hinzu"""
    tire_id = f"{tire_data['Teilenummer']}_{tire_data['Preis_EUR']}"
    
    # Prüfen ob bereits im Warenkorb
    for item in st.session_state.cart_items:
        if item['id'] == tire_id:
            return False, "Reifen bereits im Warenkorb"
    
    # Warenkorb-Item erstellen
    cart_item = {
        'id': tire_id,
        'Reifengroesse': f"{tire_data['Breite']}/{tire_data['Hoehe']} R{tire_data['Zoll']}",
        'Fabrikat': tire_data['Fabrikat'],
        'Profil': tire_data['Profil'],
        'Teilenummer': tire_data['Teilenummer'],
        'Preis_EUR': tire_data['Preis_EUR'],
        'Zoll': tire_data['Zoll'],
        'Bestand': tire_data.get('Bestand', '-'),
        'Kraftstoffeffizienz': tire_data.get('Kraftstoffeffizienz', ''),
        'Nasshaftung': tire_data.get('Nasshaftung', '')
    }
    
    # Zum Warenkorb hinzufügen
    st.session_state.cart_items.append(cart_item)
    st.session_state.cart_quantities[tire_id] = quantity
    st.session_state.cart_services[tire_id] = services
    
    # Warenkorb-Anzahl aktualisieren
    st.session_state.cart_count = len(st.session_state.cart_items)
    
    return True, f"{quantity}x {cart_item['Reifengroesse']} hinzugefuegt"

# ================================================================================================
# SESSION STATE INITIALISIERUNG
# ================================================================================================
def init_session_state():
    """Initialisiert Session State"""
    if 'selected_size' not in st.session_state:
        st.session_state.selected_size = None
    if 'opened_tire_cards' not in st.session_state:
        st.session_state.opened_tire_cards = set()
    if 'mit_bestand_filter' not in st.session_state:
        st.session_state.mit_bestand_filter = True
    
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
# MAIN FUNCTIONS
# ================================================================================================
def render_config_card(row, idx, filtered_df):
    """Rendert die Konfigurationskarte für einen Reifen"""
    st.markdown(f"""
    <div class="config-card">
    """, unsafe_allow_html=True)
    
    st.markdown(f"**Konfiguration fuer {row['Reifengroesse']} - {row['Fabrikat']} {row['Profil']}**")
    
    col_config1, col_config2 = st.columns(2)
    
    with col_config1:
        # Stückzahl
        quantity = st.number_input(
            "Stueckzahl:",
            min_value=1,
            max_value=8,
            value=4,
            step=1,
            key=f"qty_{idx}",
            help="Anzahl der Reifen (1-8 Stueck)"
        )
        
        # Gesamtpreis anzeigen
        total_price = row['Preis_EUR'] * quantity
        st.metric("Reifen-Gesamtpreis", f"{total_price:.2f} EUR")
    
    with col_config2:
        st.markdown("**Service-Leistungen:**")
        
        # Service-Preise laden
        service_prices = get_service_prices()
        
        # Montage-Preis basierend auf Zoll-Größe
        zoll_size = row['Zoll']
        if zoll_size <= 17:
            montage_price = service_prices.get('montage_bis_17', 25.0)
            montage_label = f"Reifenservice bis 17 Zoll ({montage_price:.2f}EUR pro Reifen)"
        elif zoll_size <= 19:
            montage_price = service_prices.get('montage_18_19', 30.0)
            montage_label = f"Reifenservice 18-19 Zoll ({montage_price:.2f}EUR pro Reifen)"
        else:
            montage_price = service_prices.get('montage_ab_20', 40.0)
            montage_label = f"Reifenservice ab 20 Zoll ({montage_price:.2f}EUR pro Reifen)"
        
        # Montage Checkbox
        montage_selected = st.checkbox(
            montage_label,
            key=f"montage_{idx}",
            value=True
        )
        
        # Radwechsel Checkbox
        radwechsel_selected = st.checkbox(
            "Radwechsel",
            key=f"radwechsel_{idx}"
        )
        
        # Radwechsel-Optionen
        radwechsel_type = '4_raeder'  # Default
        
        if radwechsel_selected:
            with st.expander("Radwechsel-Optionen", expanded=True):
                radwechsel_options = [
                    ('4_raeder', f"4 Raeder ({service_prices.get('radwechsel_4_raeder', 39.90):.2f}EUR)"),
                    ('3_raeder', f"3 Raeder ({service_prices.get('radwechsel_3_raeder', 29.95):.2f}EUR)"),
                    ('2_raeder', f"2 Raeder ({service_prices.get('radwechsel_2_raeder', 19.95):.2f}EUR)"),
                    ('1_rad', f"1 Rad ({service_prices.get('radwechsel_1_rad', 9.95):.2f}EUR)")
                ]
                
                radwechsel_type = st.radio(
                    "Anzahl Raeder:",
                    options=[opt[0] for opt in radwechsel_options],
                    format_func=lambda x: next(opt[1] for opt in radwechsel_options if opt[0] == x),
                    key=f"radwechsel_type_{idx}",
                    index=0
                )
        
        # Einlagerung
        einlagerung_selected = st.checkbox(
            f"Nur Einlagerung (+{service_prices.get('nur_einlagerung', 55.00):.2f}EUR)",
            key=f"einlagerung_{idx}"
        )
        
        # Service-Kosten berechnen
        service_total = 0.0
        
        if montage_selected:
            service_total += montage_price * quantity
            
        if radwechsel_selected:
            if radwechsel_type == '1_rad':
                service_total += service_prices.get('radwechsel_1_rad', 9.95)
            elif radwechsel_type == '2_raeder':
                service_total += service_prices.get('radwechsel_2_raeder', 19.95)
            elif radwechsel_type == '3_raeder':
                service_total += service_prices.get('radwechsel_3_raeder', 29.95)
            else:  # '4_raeder'
                service_total += service_prices.get('radwechsel_4_raeder', 39.90)
                
        if einlagerung_selected:
            service_total += service_prices.get('nur_einlagerung', 55.00)
        
        if service_total > 0:
            st.metric("Service-Kosten", f"{service_total:.2f} EUR")
    
    # Gesamtsumme
    grand_total = total_price + service_total
    st.markdown(f"### **Gesamtsumme: {grand_total:.2f} EUR**")
    
    # Action Buttons
    col_add, col_cancel = st.columns(2)
    
    with col_add:
        if st.button("In Warenkorb legen", 
                   key=f"add_cart_{idx}", 
                   use_container_width=True, 
                   type="primary"):
            
            # Service-Konfiguration
            service_config = {
                'montage': montage_selected,
                'radwechsel': radwechsel_selected,
                'radwechsel_type': radwechsel_type,
                'einlagerung': einlagerung_selected
            }
            
            # Reifen zum Warenkorb hinzufügen
            tire_data = filtered_df.iloc[idx]
            success, message = add_to_cart_with_config(tire_data, quantity, service_config)
            
            if success:
                st.success(message)
                # Karte schließen
                card_key = f"tire_card_{idx}"
                st.session_state.opened_tire_cards.discard(card_key)
                st.rerun()
            else:
                st.warning(message)
    
    with col_cancel:
        if st.button("Abbrechen", 
                   key=f"cancel_{idx}", 
                   use_container_width=True):
            card_key = f"tire_card_{idx}"
            st.session_state.opened_tire_cards.discard(card_key)
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_tire_list(filtered_df):
    """Rendert die Reifen-Liste mit Auswahl-Buttons"""
    display = filtered_df.copy().reset_index(drop=True)
    display["Reifengroesse"] = (
        display["Breite"].astype(str) + "/" + display["Hoehe"].astype(str) + " R" + display["Zoll"].astype(str)
    )
    display["Kraftstoff"] = display["Kraftstoffeffizienz"].apply(lambda x: f"{get_efficiency_emoji(x)} {x}" if pd.notna(x) else "")
    display["Nasshaft."] = display["Nasshaftung"].apply(lambda x: f"{get_efficiency_emoji(x)} {x}" if pd.notna(x) else "")
    display["Preis EUR"] = display["Preis_EUR"].apply(lambda x: f"{float(x):.2f} EUR")
    display["Bestand"] = display["Bestand"].apply(get_stock_display)
    
    st.markdown("**Reifen auswaehlen und konfigurieren:**")
    
    for idx, row in display.iterrows():
        col_info, col_button = st.columns([5, 1])
        
        with col_info:
            # Kompakte Reifen-Info
            effi_display = f" {row['Kraftstoff']}" if row['Kraftstoff'] else ""
            nasshaft_display = f" {row['Nasshaft.']}" if row['Nasshaft.'] else ""
            bestand_display = f" (Bestand: {row['Bestand']})" if row['Bestand'] != "unbekannt" else ""
            
            st.write(f"**{row['Reifengroesse']}** - {row['Fabrikat']} {row['Profil']} - **{row['Preis EUR']}**{bestand_display}{effi_display}{nasshaft_display} - {row['Teilenummer']}")
        
        with col_button:
            card_key = f"tire_card_{idx}"
            is_open = card_key in st.session_state.opened_tire_cards
            
            if st.button("Auswaehlen" if not is_open else "Schliessen", 
                        key=f"select_btn_{idx}", 
                        use_container_width=True,
                        type="primary" if not is_open else "secondary"):
                if is_open:
                    st.session_state.opened_tire_cards.remove(card_key)
                else:
                    st.session_state.opened_tire_cards.add(card_key)
                st.rerun()
        
        # Ausklappbare Konfigurationskarte
        if card_key in st.session_state.opened_tire_cards:
            render_config_card(row, idx, filtered_df)

def render_statistics(filtered_df):
    """Rendert Statistiken"""
    st.subheader("Statistiken")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_price = filtered_df['Preis_EUR'].mean()
        st.markdown(create_metric_card("Durchschnittspreis", f"{avg_price:.2f} EUR"), unsafe_allow_html=True)
    
    with col2:
        min_price = filtered_df['Preis_EUR'].min()
        st.markdown(create_metric_card("Guenstigster Reifen", f"{min_price:.2f} EUR"), unsafe_allow_html=True)
    
    with col3:
        max_price = filtered_df['Preis_EUR'].max()
        st.markdown(create_metric_card("Teuerster Reifen", f"{max_price:.2f} EUR"), unsafe_allow_html=True)
    
    with col4:
        unique_sizes = len(filtered_df[["Breite", "Hoehe", "Zoll"]].drop_duplicates())
        st.markdown(create_metric_card("Verfuegbare Groessen", str(unique_sizes)), unsafe_allow_html=True)

def render_legend(mit_bestand):
    """Rendert die Legende"""
    st.markdown("---")
    st.markdown("**Legende:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Speedindex (max. zulaessige Geschwindigkeit):**")
        st.markdown("R = 170 km/h | S = 180 km/h | T = 190 km/h | H = 210 km/h | V = 240 km/h")
    
    with col2:
        st.markdown("**Reifengroesse:** Breite/Hoehe R Zoll")
        st.markdown("**Loadindex:** Tragfaehigkeit pro Reifen in kg")
        st.markdown("**Bestand:** NACHBESTELLEN | AUSVERKAUFT | VERFUEGBAR | unbekannt")
        if mit_bestand:
            st.markdown("**Bestandsfilter aktiv** - Nur Reifen mit Lagerbestand angezeigt")

# ================================================================================================
# MAIN FUNCTION
# ================================================================================================
def main():
    init_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>Reifen Suche</h1>
        <p>Finde die perfekten Reifen fuer deine Kunden</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Daten laden
    with st.spinner("Lade Daten..."):
        df = get_combined_data()
    
    if df.empty:
        st.warning("Keine Reifen-Daten verfuegbar. Bitte lade Daten in der Datenbank-Verwaltung hoch.")
        st.stop()
    
    # Info über Datenquellen
    master_count = len(st.session_state.master_data) if not st.session_state.master_data.empty else 0
    central_count = len(st.session_state.central_data) if not st.session_state.central_data.empty else 0
    
    st.markdown(f"""
    <div class="info-box">
        <h4>Datenquellen</h4>
        <p>{master_count} Reifen aus Master-Daten + {central_count} bearbeitete Reifen = <strong>{len(df)} gesamt</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Filter
    with st.sidebar:
        st.header("Detailfilter")
        
        # Bestandsfilter (standardmäßig aktiviert)
        mit_bestand = st.checkbox(
            "Mit Bestand",
            value=st.session_state.mit_bestand_filter,
            help="Nur Reifen mit positivem Lagerbestand anzeigen"
        )
        st.session_state.mit_bestand_filter = mit_bestand
        
        st.markdown("---")
        
        # Filter-Optionen
        zoll_opt = ["Alle"] + sorted(df["Zoll"].unique().tolist())
        breite_opt = ["Alle"] + sorted(df["Breite"].unique().tolist())
        hoehe_opt = ["Alle"] + sorted(df["Hoehe"].unique().tolist())
        fabrikat_opt = ["Alle"] + sorted([x for x in df["Fabrikat"].dropna().unique().tolist()])
        
        zoll_filter = st.selectbox("Zoll", options=zoll_opt, index=0)
        breite_filter = st.selectbox("Breite (mm)", options=breite_opt, index=0)
        hoehe_filter = st.selectbox("Hoehe (%)", options=hoehe_opt, index=0)
        fabrikat = st.selectbox("Fabrikat", options=fabrikat_opt, index=0)
        
        loadindex_opt = ["Alle"] + sorted([x for x in df["Loadindex"].dropna().astype(str).unique().tolist()])
        speedindex_opt = ["Alle"] + sorted([x for x in df["Speedindex"].dropna().astype(str).unique().tolist()])
        
        loadindex_filter = st.selectbox("Loadindex", options=loadindex_opt, index=0)
        speedindex_filter = st.selectbox("Speedindex", options=speedindex_opt, index=0)
        
        # Preisbereich
        min_price = float(df["Preis_EUR"].min())
        max_price = float(df["Preis_EUR"].max())
        min_preis, max_preis = st.slider(
            "Preisbereich (EUR)",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price),
            step=5.0,
        )
        
        # Sortierung
        sortierung = st.selectbox(
            "Sortieren nach",
            options=["Preis aufsteigend", "Preis absteigend", "Fabrikat", "Reifengroesse"],
        )
        
        # Statistiken
        show_stats = st.checkbox("Statistiken anzeigen", value=False)
        
        # Navigation zu anderen Bereichen
        st.markdown("---")
        
        if st.button("Zum Warenkorb", use_container_width=True, type="primary"):
            st.switch_page("pages/02_Warenkorb.py")
        
        if st.button("Premium Verwaltung", use_container_width=True, type="secondary"):
            st.switch_page("pages/03_Premium_Verwaltung.py")
        
        if st.button("Datenbank Verwaltung", use_container_width=True, type="secondary"):
            st.switch_page("pages/04_Datenbank_Verwaltung.py")
    
    # Schnellauswahl für gängige Reifengrößen
    st.subheader("Schnellauswahl - gaengige Reifengroessen")
    top_sizes = [
        "195/65 R15", "195/60 R16", "205/55 R16", "205/60 R16",
        "205/65 R16", "215/55 R16", "215/60 R16", "215/65 R16",
        "205/50 R17", "215/55 R17", "215/60 R17", "215/65 R17",
    ]
    
    cols = st.columns(4)
    for i, size in enumerate(top_sizes):
        with cols[i % 4]:
            if st.button(size, key=f"btn_{size}", use_container_width=True):
                st.session_state.selected_size = size
                st.rerun()
    
    # Filter anwenden
    filtered = df.copy()
    
    # Bestandsfilter
    if mit_bestand:
        filtered = filtered[
            (filtered['Bestand'].notna()) & 
            (filtered['Bestand'] > 0)
        ]
    
    # Schnellauswahl
    if st.session_state.selected_size:
        parts = st.session_state.selected_size.split("/")
        b = int(parts[0])
        h = int(parts[1].split(" R")[0])
        z = int(parts[1].split(" R")[1])
        filtered = filtered[(filtered["Breite"] == b) & (filtered["Hoehe"] == h) & (filtered["Zoll"] == z)]
        
        st.markdown(f"""
        <div class="warning-box">
            <h4>Schnellauswahl aktiv: {st.session_state.selected_size}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Schnellauswahl zuruecksetzen"):
            st.session_state.selected_size = None
            st.rerun()
    
    # Detailfilter anwenden
    if zoll_filter != "Alle":
        filtered = filtered[filtered["Zoll"] == int(zoll_filter)]
    if breite_filter != "Alle":
        filtered = filtered[filtered["Breite"] == int(breite_filter)]
    if hoehe_filter != "Alle":
        filtered = filtered[filtered["Hoehe"] == int(hoehe_filter)]
    if fabrikat != "Alle":
        filtered = filtered[filtered["Fabrikat"] == fabrikat]
    if loadindex_filter != "Alle":
        filtered = filtered[filtered["Loadindex"].astype(str) == str(loadindex_filter)]
    if speedindex_filter != "Alle":
        filtered = filtered[filtered["Speedindex"].astype(str) == str(speedindex_filter)]
    
    filtered = filtered[(filtered["Preis_EUR"] >= min_preis) & (filtered["Preis_EUR"] <= max_preis)]
    
    # Sortierung anwenden
    if sortierung == "Preis aufsteigend":
        filtered = filtered.sort_values("Preis_EUR")
    elif sortierung == "Preis absteigend":
        filtered = filtered.sort_values("Preis_EUR", ascending=False)
    elif sortierung == "Fabrikat":
        filtered = filtered.sort_values(["Fabrikat", "Preis_EUR"])
    elif sortierung == "Reifengroesse":
        filtered = filtered.sort_values(["Zoll", "Breite", "Hoehe", "Preis_EUR"])
    
    # Gefundene Reifen anzeigen
    if len(filtered) > 0:
        st.markdown("---")
        
        # Info über Bestandsfilter
        if mit_bestand:
            st.subheader(f"Gefundene Reifen mit Bestand: {len(filtered)}")
            if len(df) > len(filtered):
                nicht_auf_lager = len(df) - len(filtered)
                st.markdown(f"""
                <div class="info-box">
                    <p>{nicht_auf_lager} weitere Reifen ohne Lagerbestand verfuegbar (Bestandsfilter deaktivieren)</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.subheader(f"Gefundene Reifen: {len(filtered)}")
        
        # Reifen-Liste
        render_tire_list(filtered)
        
        # Statistiken
        if show_stats:
            render_statistics(filtered)
    else:
        if mit_bestand:
            st.warning("Keine Reifen mit Bestand gefunden. Bitte Filter anpassen oder Bestandsfilter deaktivieren.")
        else:
            st.warning("Keine Reifen gefunden. Bitte Filter anpassen oder andere Reifengroesse waehlen.")
    
    # Legende
    render_legend(mit_bestand)

if __name__ == "__main__":
    main()