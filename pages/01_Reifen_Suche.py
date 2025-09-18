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
# CSS STYLES - OHNE STICKY, NORMAL SCROLLBAR
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
    
    .saison-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    .saison-winter {
        background-color: #dbeafe;
        color: #1e40af;
    }
    
    .saison-sommer {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .saison-ganzjahres {
        background-color: #d1fae5;
        color: #065f46;
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
    
    .cart-indicator {
        color: #16a34a;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    
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

def get_saison_from_teilenummer(teilenummer):
    """Ermittelt Saison basierend auf Teilenummer"""
    if pd.isna(teilenummer) or teilenummer == '':
        return "Unbekannt"
    teilenummer_str = str(teilenummer).strip().upper()
    if teilenummer_str.startswith('ZTW'):
        return "Winter"
    elif teilenummer_str.startswith('ZTR'):
        return "Ganzjahres"
    elif teilenummer_str.startswith('ZTS'):
        return "Sommer"
    else:
        return "Unbekannt"

def get_saison_badge_html(saison):
    """Erstellt HTML Badge für Saison-Anzeige"""
    if saison == "Winter":
        return '<span class="saison-badge saison-winter">Winter</span>'
    elif saison == "Sommer":
        return '<span class="saison-badge saison-sommer">Sommer</span>'
    elif saison == "Ganzjahres":
        return '<span class="saison-badge saison-ganzjahres">Ganzjahres</span>'
    else:
        return '<span class="saison-badge">Unbekannt</span>'

def is_tire_in_cart(tire_data):
    """Prüft ob ein Reifen bereits im Warenkorb ist"""
    tire_id = f"{tire_data['Teilenummer']}_{tire_data['Preis_EUR']}"
    return any(item['id'] == tire_id for item in st.session_state.cart_items)

def get_dynamic_tire_sizes(filtered_df, max_sizes=12):
    """Erstellt dynamische Liste von Reifengrößen aus gefilterten Daten, sortiert nach Größe"""
    if filtered_df.empty:
        return []
    unique_sizes = filtered_df[['Breite', 'Hoehe', 'Zoll']].drop_duplicates()
    unique_sizes = unique_sizes.sort_values(['Zoll', 'Breite', 'Hoehe'])
    unique_sizes['size_str'] = (unique_sizes['Breite'].astype(str) + '/' + 
                               unique_sizes['Hoehe'].astype(str) + ' R' + 
                               unique_sizes['Zoll'].astype(str))
    num_sizes = min(max_sizes, len(unique_sizes))
    top_sizes = unique_sizes.head(num_sizes)['size_str'].tolist()
    return top_sizes

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
    for c in ["Breite", "Hoehe", "Zoll"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    if "Bestand" in df.columns:
        df["Bestand"] = pd.to_numeric(df["Bestand"], errors="coerce")
    required_cols = ["Fabrikat", "Profil", "Kraftstoffeffizienz", "Nasshaftung", 
                     "Loadindex", "Speedindex", "Teilenummer", "Geräuschklasse"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = pd.NA
    if "Saison" not in df.columns:
        df["Saison"] = df["Teilenummer"].apply(get_saison_from_teilenummer)
    df = df.dropna(subset=["Preis_EUR", "Breite", "Hoehe", "Zoll"], how="any")
    if not df.empty:
        df["Breite"] = df["Breite"].astype(int)
        df["Hoehe"] = df["Hoehe"].astype(int)
        df["Zoll"] = df["Zoll"].astype(int)
    return df

# ================================================================================================
# DATA MANAGEMENT - VEREINFACHT FÜR EINE CSV
# ================================================================================================
def load_reifen_data():
    """Lädt die Reifen-CSV-Datei"""
    data_dir = Path("data")
    csv_path = data_dir / "Ramsperger_Winterreifen_20250826_160010.csv"
    try:
        if csv_path.exists():
            df = pd.read_csv(csv_path, encoding='utf-8')
            df_clean = clean_dataframe(df)
            return df_clean
        else:
            return create_fallback_data()
    except Exception:
        return create_fallback_data()

def create_fallback_data():
    """Fallback Beispiel-Daten falls CSV nicht geladen werden kann"""
    sample_data = {
        'Breite': [195, 205, 215, 225, 195, 205, 215, 225],
        'Hoehe': [65, 55, 60, 55, 60, 60, 55, 50],
        'Zoll': [15, 16, 16, 17, 16, 17, 17, 18],
        'Fabrikat': ['Continental', 'Michelin', 'Bridgestone', 'Pirelli', 'Continental', 'Michelin', 'Bridgestone', 'Pirelli'],
        'Profil': ['WinterContact TS850', 'Alpin 6', 'Blizzak LM005', 'Winter Sottozero 3', 'WinterContact TS860', 'Alpin 5', 'Blizzak WS90', 'Winter Sottozero Serie II'],
        'Teilenummer': ['ZTW15494940000', 'ZTW03528700000', 'ZTW19394', 'ZTW8019227308853', 'ZTS15495040000', 'ZTS03528800000', 'ZTR19395', 'ZTR8019227308854'],
        'Preis_EUR': [89.90, 95.50, 87.20, 99.90, 92.90, 98.50, 89.20, 103.90],
        'Loadindex': [91, 91, 94, 94, 88, 91, 94, 97],
        'Speedindex': ['T', 'H', 'H', 'V', 'H', 'H', 'H', 'V'],
        'Kraftstoffeffizienz': ['C', 'B', 'A', 'C', 'C', 'B', 'A', 'C'],
        'Nasshaftung': ['B', 'A', 'A', 'B', 'B', 'A', 'A', 'B'],
        'Bestand': [25, 12, 8, 15, 30, 0, -5, 20],
        'Geräuschklasse': [68, 69, 67, 70, 68, 69, 67, 71]
    }
    df = pd.DataFrame(sample_data)
    df["Saison"] = df["Teilenummer"].apply(get_saison_from_teilenummer)
    return df

def get_reifen_data():
    """Hauptfunktion - lädt Reifen-Daten"""
    if 'reifen_data' not in st.session_state or 'data_loaded' not in st.session_state:
        st.session_state.reifen_data = load_reifen_data()
        st.session_state.data_loaded = True
    return st.session_state.reifen_data

# ================================================================================================
# NEUE SERVICE-PAKET FUNKTIONEN
# ================================================================================================
def load_service_packages():
    """Lädt die neuen Service-Pakete aus CSV"""
    data_dir = Path("data")
    csv_path = data_dir / "ramsperger_services_config.csv"
    
    if not csv_path.exists():
        return create_default_service_packages()
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        return df
    except Exception:
        return create_default_service_packages()

def create_default_service_packages():
    """Erstellt Standard Service-Pakete basierend auf deinen neuen Paketen"""
    packages = [
        # REIFENSERVICE bis 17 Zoll
        {'Positionsnummer': 'Z4409', 'Bezeichnung': 'SERVICE PAKET REIFENSERVICE 1 RAD', 'Teilenummer': '44401995', 'Detail': 'REIFENSERVICE 1 RAD', 'Preis': 25.00, 'Hinweis': 'inkl. Auswuchtgewichte, Ventil und Altreifenentsorgung', 'Kategorie': 'reifenservice', 'Zoll': 'bis_17', 'Anzahl': 1},
        {'Positionsnummer': 'Z44091', 'Bezeichnung': 'SERVICE PAKET REIFENSERVICE 2 RÄDER', 'Teilenummer': '44402095', 'Detail': 'REIFENSERVICE 2 RÄDER', 'Preis': 50.00, 'Hinweis': 'inkl. Auswuchtgewichte, Ventile und Altreifenentsorgung', 'Kategorie': 'reifenservice', 'Zoll': 'bis_17', 'Anzahl': 2},
        {'Positionsnummer': 'Z44092', 'Bezeichnung': 'SERVICE PAKET REIFENSERVICE 4 RÄDER', 'Teilenummer': '44402295', 'Detail': 'REIFENSERVICE 4 RÄDER', 'Preis': 100.00, 'Hinweis': 'inkl. Auswuchtgewichte, Ventile und Altreifenentsorgung', 'Kategorie': 'reifenservice', 'Zoll': 'bis_17', 'Anzahl': 4},
        
        # REIFENSERVICE 18-19 Zoll
        {'Positionsnummer': 'Z44093', 'Bezeichnung': 'SERVICE PAKET REIFENSERVICE 1 RAD', 'Teilenummer': '44401996', 'Detail': 'REIFENSERVICE 1 RAD', 'Preis': 30.00, 'Hinweis': 'inkl. Auswuchtgewichte, Ventil und Altreifenentsorgung', 'Kategorie': 'reifenservice', 'Zoll': '18_19', 'Anzahl': 1},
        {'Positionsnummer': 'Z44094', 'Bezeichnung': 'SERVICE PAKET REIFENSERVICE 2 RÄDER', 'Teilenummer': '44402096', 'Detail': 'REIFENSERVICE 2 RÄDER', 'Preis': 60.00, 'Hinweis': 'inkl. Auswuchtgewichte, Ventile und Altreifenentsorgung', 'Kategorie': 'reifenservice', 'Zoll': '18_19', 'Anzahl': 2},
        {'Positionsnummer': 'Z44095', 'Bezeichnung': 'SERVICE PAKET REIFENSERVICE 4 RÄDER', 'Teilenummer': '44402296', 'Detail': 'REIFENSERVICE 4 RÄDER', 'Preis': 120.00, 'Hinweis': 'inkl. Auswuchtgewichte, Ventile und Altreifenentsorgung', 'Kategorie': 'reifenservice', 'Zoll': '18_19', 'Anzahl': 4},
        
        # REIFENSERVICE ab 20 Zoll
        {'Positionsnummer': 'Z44096', 'Bezeichnung': 'SERVICE PAKET REIFENSERVICE 1 RAD', 'Teilenummer': '44401997', 'Detail': 'REIFENSERVICE 1 RAD', 'Preis': 40.00, 'Hinweis': 'inkl. Auswuchtgewichte, Ventil und Altreifenentsorgung', 'Kategorie': 'reifenservice', 'Zoll': 'ab_20', 'Anzahl': 1},
        {'Positionsnummer': 'Z44097', 'Bezeichnung': 'SERVICE PAKET REIFENSERVICE 2 RÄDER', 'Teilenummer': '44402097', 'Detail': 'REIFENSERVICE 2 RÄDER', 'Preis': 80.00, 'Hinweis': 'inkl. Auswuchtgewichte, Ventile und Altreifenentsorgung', 'Kategorie': 'reifenservice', 'Zoll': 'ab_20', 'Anzahl': 2},
        {'Positionsnummer': 'Z44098', 'Bezeichnung': 'SERVICE PAKET REIFENSERVICE 4 RÄDER', 'Teilenummer': '44402297', 'Detail': 'REIFENSERVICE 4 RÄDER', 'Preis': 160.00, 'Hinweis': 'inkl. Auswuchtgewichte, Ventile und Altreifenentsorgung', 'Kategorie': 'reifenservice', 'Zoll': 'ab_20', 'Anzahl': 4},
        
        # AUSWUCHTEN
        {'Positionsnummer': 'Z4404', 'Bezeichnung': 'SERVICE PAKET RÄDER AUSWUCHTEN 1 RAD', 'Teilenummer': '44056799', 'Detail': '1 RAD AUSGEWUCHTET', 'Preis': 7.50, 'Hinweis': 'inkl. Auswuchtgewichte', 'Kategorie': 'auswuchten', 'Zoll': 'alle', 'Anzahl': 1},
        {'Positionsnummer': 'Z44041', 'Bezeichnung': 'SERVICE PAKET RÄDER AUSWUCHTEN 2 RÄDER', 'Teilenummer': '44056899', 'Detail': '2 RÄDER AUSGEWUCHTET', 'Preis': 15.00, 'Hinweis': 'inkl. Auswuchtgewichte', 'Kategorie': 'auswuchten', 'Zoll': 'alle', 'Anzahl': 2},
        {'Positionsnummer': 'Z44042', 'Bezeichnung': 'SERVICE PAKET RÄDER AUSWUCHTEN 4 RÄDER', 'Teilenummer': '44056999', 'Detail': '4 RÄDER AUSGEWUCHTET', 'Preis': 30.00, 'Hinweis': 'inkl. Auswuchtgewichte', 'Kategorie': 'auswuchten', 'Zoll': 'alle', 'Anzahl': 4},
        
        # RÄDERWECHSEL
        {'Positionsnummer': 'Z44058', 'Bezeichnung': 'SERVICE PAKET RÄDERWECHSEL', 'Teilenummer': '44051091', 'Detail': 'RÄDERWECHSEL (1 Rad)', 'Preis': 9.98, 'Hinweis': '', 'Kategorie': 'raederwechsel', 'Zoll': 'alle', 'Anzahl': 1},
        {'Positionsnummer': 'Z44059', 'Bezeichnung': 'SERVICE PAKET RÄDERWECHSEL', 'Teilenummer': '44051092', 'Detail': 'RÄDERWECHSEL (2 Räder)', 'Preis': 19.95, 'Hinweis': '', 'Kategorie': 'raederwechsel', 'Zoll': 'alle', 'Anzahl': 2},
        {'Positionsnummer': 'Z44060', 'Bezeichnung': 'SERVICE PAKET RÄDERWECHSEL', 'Teilenummer': '44051099', 'Detail': 'RÄDERWECHSEL', 'Preis': 39.90, 'Hinweis': '', 'Kategorie': 'raederwechsel', 'Zoll': 'alle', 'Anzahl': 4},
        
        # KOMBIPAKETE
        {'Positionsnummer': 'Z44053', 'Bezeichnung': 'RÄDERWECHSEL INKL. EINLAGERUNG KOMFORT', 'Teilenummer': '44051099', 'Detail': 'RÄDERWECHSEL, SAISONALE RÄDEREINLAGERUNG', 'Preis': 109.90, 'Hinweis': '', 'Kategorie': 'kombi_komfort', 'Zoll': 'alle', 'Anzahl': 4},
        {'Positionsnummer': 'Z44066', 'Bezeichnung': 'SERVICE PAKET RÄDERWECHSEL & EINLAGERUNG', 'Teilenummer': '44051099', 'Detail': 'RÄDERWECHSEL, SAISONALE RÄDEREINLAGERUNG', 'Preis': 94.90, 'Hinweis': '', 'Kategorie': 'kombi_standard', 'Zoll': 'alle', 'Anzahl': 4}
    ]
    return pd.DataFrame(packages)

def get_service_packages():
    """Gibt Service-Pakete zurück"""
    if 'service_packages' not in st.session_state:
        st.session_state.service_packages = load_service_packages()
    return st.session_state.service_packages

def get_reifenservice_package(zoll_size, anzahl):
    """Gibt das passende Reifenservice-Paket zurück"""
    packages = get_service_packages()
    
    # Zoll-Kategorie bestimmen
    if zoll_size <= 17:
        zoll_cat = 'bis_17'
    elif zoll_size <= 19:
        zoll_cat = '18_19'
    else:
        zoll_cat = 'ab_20'
    
    # Passendes Paket finden
    package = packages[
        (packages['Kategorie'] == 'reifenservice') & 
        (packages['Zoll'] == zoll_cat) & 
        (packages['Anzahl'] == anzahl)
    ]
    
    if not package.empty:
        return package.iloc[0]
    return None

def get_auswuchten_package(anzahl):
    """Gibt das passende Auswuchten-Paket zurück"""
    packages = get_service_packages()
    package = packages[
        (packages['Kategorie'] == 'auswuchten') & 
        (packages['Anzahl'] == anzahl)
    ]
    
    if not package.empty:
        return package.iloc[0]
    return None

def get_raederwechsel_package(anzahl):
    """Gibt das passende Räderwechsel-Paket zurück"""
    packages = get_service_packages()
    package = packages[
        (packages['Kategorie'] == 'raederwechsel') & 
        (packages['Anzahl'] == anzahl)
    ]
    
    if not package.empty:
        return package.iloc[0]
    return None

def get_kombi_package(typ):
    """Gibt das passende Kombi-Paket zurück"""
    packages = get_service_packages()
    kategorie = 'kombi_komfort' if typ == 'komfort' else 'kombi_standard'
    package = packages[packages['Kategorie'] == kategorie]
    
    if not package.empty:
        return package.iloc[0]
    return None

# ================================================================================================
# CART MANAGEMENT - ANGEPASST FÜR NEUE SERVICE-PAKETE
# ================================================================================================
def add_to_cart_with_config(tire_data, quantity, services):
    """Fügt einen Reifen mit Konfiguration zum Warenkorb hinzu"""
    tire_id = f"{tire_data['Teilenummer']}_{tire_data['Preis_EUR']}"
    for item in st.session_state.cart_items:
        if item['id'] == tire_id:
            return False, "Reifen bereits im Warenkorb"
    cart_item = {
        'id': tire_id,
        'Reifengröße': f"{tire_data['Breite']}/{tire_data['Hoehe']} R{tire_data['Zoll']}",
        'Fabrikat': tire_data['Fabrikat'],
        'Profil': tire_data['Profil'],
        'Teilenummer': tire_data['Teilenummer'],
        'Preis_EUR': tire_data['Preis_EUR'],
        'Zoll': tire_data['Zoll'],
        'Bestand': tire_data.get('Bestand', '-'),
        'Kraftstoffeffizienz': tire_data.get('Kraftstoffeffizienz', ''),
        'Nasshaftung': tire_data.get('Nasshaftung', ''),
        'Saison': tire_data.get('Saison', 'Unbekannt')
    }
    st.session_state.cart_items.append(cart_item)
    st.session_state.cart_quantities[tire_id] = quantity
    st.session_state.cart_services[tire_id] = services
    st.session_state.cart_count = len(st.session_state.cart_items)
    return True, f"{quantity}x {cart_item['Reifengröße']} hinzugefügt"

def remove_from_cart(tire_data):
    """Entfernt einen Reifen aus dem Warenkorb"""
    tire_id = f"{tire_data['Teilenummer']}_{tire_data['Preis_EUR']}"
    
    st.session_state.cart_items = [item for item in st.session_state.cart_items if item['id'] != tire_id]
    
    if tire_id in st.session_state.cart_quantities:
        del st.session_state.cart_quantities[tire_id]
    
    if tire_id in st.session_state.cart_services:
        del st.session_state.cart_services[tire_id]
    
    st.session_state.cart_count = len(st.session_state.cart_items)
    
    return True, f"Reifen {tire_data['Fabrikat']} {tire_data['Profil']} aus Warenkorb entfernt"

# ================================================================================================
# SESSION STATE INITIALISIERUNG (Single Source of Truth für Widgets)
# ================================================================================================
def init_session_state():
    """Initialisiert Session State"""
    if 'top_saison_filter' not in st.session_state:
        st.session_state.top_saison_filter = "Alle"
    if 'top_zoll_filter' not in st.session_state:
        st.session_state.top_zoll_filter = "Alle"
    if 'top_bestand_filter' not in st.session_state:
        st.session_state.top_bestand_filter = True
    if 'selected_size' not in st.session_state:
        st.session_state.selected_size = None
    if 'opened_tire_cards' not in st.session_state:
        st.session_state.opened_tire_cards = set()
    if 'cart_items' not in st.session_state:
        st.session_state.cart_items = []
    if 'cart_quantities' not in st.session_state:
        st.session_state.cart_quantities = {}
    if 'cart_services' not in st.session_state:
        st.session_state.cart_services = {}
    if 'cart_count' not in st.session_state:
        st.session_state.cart_count = 0

# ================================================================================================
# RENDER FUNCTIONS - ANGEPASST FÜR NEUE SERVICE-PAKETE
# ================================================================================================
def render_config_card(row, idx, filtered_df):
    """Rendert die Konfigurationskarte für einen Reifen mit neuen Service-Paketen"""
    st.markdown(f"""<div class="config-card">""", unsafe_allow_html=True)
    saison_badge = get_saison_badge_html(row.get('Saison', 'Unbekannt'))
    st.markdown(f"**Konfiguration für {row['Reifengröße']} - {row['Fabrikat']} {row['Profil']}** {saison_badge}", unsafe_allow_html=True)

    col_config1, col_config2 = st.columns(2)

    with col_config1:
        quantity = st.number_input(
            "Stückzahl:",
            min_value=1,
            max_value=8,
            value=4,
            step=1,
            key=f"qty_{idx}",
            help="Anzahl der Reifen (1-8 Stück)"
        )
        total_price = row['Preis_EUR'] * quantity
        st.metric("Reifen-Gesamtpreis", f"{total_price:.2f} EUR")

    with col_config2:
        st.markdown("**Service-Leistungen:**")
        
        zoll_size = row['Zoll']
        
        # REIFENSERVICE-AUSWAHL
        reifenservice_selected = st.checkbox(
            "Reifenservice",
            key=f"reifenservice_{idx}",
            value=True,
            help="Kompletter Reifenservice inkl. Montage, Auswuchten, Ventil und Entsorgung"
        )
        
        # AUSWUCHTEN-AUSWAHL (nur wenn kein Reifenservice)
        auswuchten_selected = False
        if not reifenservice_selected:
            auswuchten_selected = st.checkbox(
                "Nur Auswuchten",
                key=f"auswuchten_{idx}",
                help="Nur Räder auswuchten ohne Montage"
            )
        
        # RÄDERWECHSEL-AUSWAHL
        raederwechsel_selected = st.checkbox(
            "Räderwechsel",
            key=f"raederwechsel_{idx}"
        )
        
        raederwechsel_anzahl = quantity
        if raederwechsel_selected:
            with st.expander("Räderwechsel-Optionen", expanded=True):
                raederwechsel_options = [
                    (4, "4 Räder (Standard)"),
                    (2, "2 Räder"),
                    (1, "1 Rad")
                ]
                
                raederwechsel_anzahl = st.radio(
                    "Anzahl Räder:",
                    options=[opt[0] for opt in raederwechsel_options],
                    format_func=lambda x: next(opt[1] for opt in raederwechsel_options if opt[0] == x),
                    key=f"raederwechsel_anzahl_{idx}",
                    index=0
                )
        
        # EINLAGERUNG-AUSWAHL
        einlagerung_selected = st.checkbox(
            "Mit Einlagerung",
            key=f"einlagerung_{idx}"
        )
        
        einlagerung_typ = 'standard'
        if einlagerung_selected:
            einlagerung_typ = st.radio(
                "Einlagerung-Typ:",
                options=['standard', 'komfort'],
                format_func=lambda x: 'Standard (94,90 EUR)' if x == 'standard' else 'Komfort (109,90 EUR)',
                key=f"einlagerung_typ_{idx}",
                index=0
            )
        
        # KOSTENBERECHNUNG
        service_total = 0.0
        service_details = []
        
        if reifenservice_selected:
            package = get_reifenservice_package(zoll_size, quantity)
            if package is not None:
                service_total += package['Preis']
                service_details.append(f"Reifenservice: {package['Preis']:.2f} EUR ({package['Positionsnummer']})")
        
        elif auswuchten_selected:
            package = get_auswuchten_package(quantity)
            if package is not None:
                service_total += package['Preis']
                service_details.append(f"Auswuchten: {package['Preis']:.2f} EUR ({package['Positionsnummer']})")
        
        if raederwechsel_selected and not einlagerung_selected:
            package = get_raederwechsel_package(raederwechsel_anzahl)
            if package is not None:
                service_total += package['Preis']
                service_details.append(f"Räderwechsel: {package['Preis']:.2f} EUR ({package['Positionsnummer']})")
        
        if einlagerung_selected:
            package = get_kombi_package(einlagerung_typ)
            if package is not None:
                service_total += package['Preis']
                service_details.append(f"Räderwechsel + Einlagerung: {package['Preis']:.2f} EUR ({package['Positionsnummer']})")
        
        if service_total > 0:
            st.metric("Service-Kosten", f"{service_total:.2f} EUR")
            for detail in service_details:
                st.caption(detail)

    grand_total = total_price + service_total
    st.markdown(f"### **Gesamtsumme: {grand_total:.2f} EUR**")

    col_add, col_cancel = st.columns(2)
    with col_add:
        if st.button("In Warenkorb legen", key=f"add_cart_{idx}", use_container_width=True, type="primary"):
            service_config = {
                'reifenservice': reifenservice_selected,
                'auswuchten': auswuchten_selected,
                'raederwechsel': raederwechsel_selected,
                'raederwechsel_anzahl': raederwechsel_anzahl,
                'einlagerung': einlagerung_selected,
                'einlagerung_typ': einlagerung_typ
            }
            tire_data = filtered_df.iloc[idx]
            success, message = add_to_cart_with_config(tire_data, quantity, service_config)
            if success:
                st.success(message)
                card_key = f"tire_card_{idx}"
                st.session_state.opened_tire_cards.discard(card_key)
                st.rerun()
            else:
                st.warning(message)

    with col_cancel:
        if st.button("Abbrechen", key=f"cancel_{idx}", use_container_width=True):
            card_key = f"tire_card_{idx}"
            st.session_state.opened_tire_cards.discard(card_key)
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

def render_tire_list(filtered_df):
    """Rendert die Reifen-Liste mit verbesserter Darstellung und Warenkorb-Anzeige"""
    display = filtered_df.copy().reset_index(drop=True)
    display["Reifengröße"] = (
        display["Breite"].astype(str) + "/" + display["Hoehe"].astype(str) + " R" + display["Zoll"].astype(str)
    )

    st.markdown("**Reifen auswählen und konfigurieren:**")

    for idx, row in display.iterrows():
        is_in_cart = is_tire_in_cart(row)
        
        if is_in_cart:
            col_info, col_button, col_remove = st.columns([4, 1, 1])
        else:
            col_info, col_button = st.columns([5, 1])

        with col_info:
            saison_badge = get_saison_badge_html(row.get('Saison', 'Unbekannt'))
            cart_indicator = ""
            if is_in_cart:
                cart_indicator = '<span class="cart-indicator">🛒 Im Warenkorb</span>'
            st.markdown(f"**{row['Reifengröße']}** - {row['Fabrikat']} {row['Profil']} {saison_badge} {cart_indicator}", unsafe_allow_html=True)

            preis_display = f"**{float(row['Preis_EUR']):.2f} EUR**"
            bestand_display = get_stock_display(row['Bestand'])
            tragkraft_display = f"{row['Loadindex']}{row['Speedindex']}" if pd.notna(row['Loadindex']) and pd.notna(row['Speedindex']) else ""

            info_zeile = f"Preis: {preis_display}"
            if bestand_display != "unbekannt":
                info_zeile += f" | Bestand: {bestand_display}"
            if tragkraft_display:
                info_zeile += f" | Tragkraft: {tragkraft_display}"
            st.markdown(info_zeile)

            eu_labels = []
            if pd.notna(row['Kraftstoffeffizienz']) and row['Kraftstoffeffizienz'] != '':
                eu_labels.append(f"Kraftstoff {get_efficiency_emoji(row['Kraftstoffeffizienz'])}")
            if pd.notna(row['Nasshaftung']) and row['Nasshaftung'] != '':
                eu_labels.append(f"Nasshaftung {get_efficiency_emoji(row['Nasshaftung'])}")
            if pd.notna(row['Geräuschklasse']) and row['Geräuschklasse'] != '':
                eu_labels.append(f"Lärm {int(row['Geräuschklasse'])}dB")
            if eu_labels:
                st.markdown(f"EU-Label: {' | '.join(eu_labels)}")

            st.markdown(f"<small>Teilenummer: {row['Teilenummer']}</small>", unsafe_allow_html=True)

        with col_button:
            card_key = f"tire_card_{idx}"
            is_open = card_key in st.session_state.opened_tire_cards
            if st.button("Auswählen" if not is_open else "Schließen",
                         key=f"select_btn_{idx}",
                         use_container_width=True,
                         type="primary" if not is_open else "secondary"):
                if is_open:
                    st.session_state.opened_tire_cards.remove(card_key)
                else:
                    st.session_state.opened_tire_cards.add(card_key)
                st.rerun()

        if is_in_cart:
            with col_remove:
                if st.button("🗑️", 
                           key=f"remove_btn_{idx}",
                           use_container_width=True,
                           type="secondary",
                           help="Aus Warenkorb entfernen"):
                    success, message = remove_from_cart(row)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error("Fehler beim Entfernen aus dem Warenkorb")

        if card_key in st.session_state.opened_tire_cards:
            render_config_card(row, idx, filtered_df)

        st.markdown("---")

def render_statistics(filtered_df):
    """Rendert Statistiken"""
    st.subheader("Statistiken")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_price = filtered_df['Preis_EUR'].mean()
        st.markdown(create_metric_card("Durchschnittspreis", f"{avg_price:.2f} EUR"), unsafe_allow_html=True)
    with col2:
        min_price = filtered_df['Preis_EUR'].min()
        st.markdown(create_metric_card("Günstigster Reifen", f"{min_price:.2f} EUR"), unsafe_allow_html=True)
    with col3:
        max_price = filtered_df['Preis_EUR'].max()
        st.markdown(create_metric_card("Teuerster Reifen", f"{max_price:.2f} EUR"), unsafe_allow_html=True)
    with col4:
        unique_sizes = len(filtered_df[["Breite", "Hoehe", "Zoll"]].drop_duplicates())
        st.markdown(create_metric_card("Verfügbare Größen", str(unique_sizes)), unsafe_allow_html=True)

def render_legend(mit_bestand, saison_filter, zoll_filter):
    """Rendert die Legende mit neuen Service-Paketen"""
    st.markdown("---")
    st.markdown("**Legende:**")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Speedindex (max. zulässige Geschwindigkeit):**")
        st.markdown("R = 170 km/h | S = 180 km/h | T = 190 km/h | H = 210 km/h | V = 240 km/h")
        st.markdown("**Saison-Kennzeichnung:**")
        st.markdown("ZTW = Winter | ZTR = Ganzjahres | ZTS = Sommer")
        st.markdown("**Neue Service-Pakete:**")
        st.markdown("Reifenservice: Komplettservice nach Zoll-Größe | Auswuchten: Nur Auswuchten | Räderwechsel + Einlagerung: Kombipakete")
    with col2:
        st.markdown("**Reifengröße:** Breite/Höhe R Zoll")
        st.markdown("**Loadindex:** Tragfähigkeit pro Reifen in kg")
        st.markdown("**Bestand:** NACHBESTELLEN | AUSVERKAUFT | VERFÜGBAR | unbekannt")
        st.markdown("**🛒 Im Warenkorb:** Reifen bereits im Warenkorb hinzugefügt")
        st.markdown("**🗑️ Button:** Reifen aus Warenkorb entfernen")
        filter_info = []
        if mit_bestand:
            filter_info.append("Bestandsfilter aktiv")
        if saison_filter != "Alle":
            filter_info.append(f"Saison: {saison_filter}")
        if zoll_filter != "Alle":
            filter_info.append(f"Zoll: {zoll_filter}")
        if filter_info:
            st.markdown(f"**Aktive Filter:** {' | '.join(filter_info)}")

# ================================================================================================
# MAIN FUNCTION - MIT LOGO GANZ OBEN UND LOGO_2.PNG
# ================================================================================================
def main():
    init_session_state()

    # Logo Header ganz oben
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    try:
        logo_path = "data/Logo_2.png"
        st.image(logo_path, width=400)
    except:
        st.markdown("### Ramsperger Automobile")
    st.markdown('</div>', unsafe_allow_html=True)

    # Fester Abstand NACH dem Logo (robust gegen Margin-Collapse)
    st.markdown('<div class="logo-spacer"></div>', unsafe_allow_html=True)

    # Daten laden
    df = get_reifen_data()
    if df.empty:
        st.warning("Keine Reifen-Daten verfügbar. Bitte prüfe die CSV-Datei.")
        st.stop()

    # Top-Filter direkt ohne Container
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        cart_count = st.session_state.cart_count
        cart_text = f"Warenkorb ({cart_count})" if cart_count > 0 else "Warenkorb"
        if st.button(cart_text, key="nav_cart", help="Zum Warenkorb wechseln", use_container_width=True, type="primary"):
            st.switch_page("pages/02_Warenkorb.py")

    with col2:
        saison_options = ["Alle", "Winter", "Sommer", "Ganzjahres"]
        st.selectbox(
            "Saison-Typ:",
            options=saison_options,
            key="top_saison_filter",
            help="Filtere nach Reifen-Saison basierend auf Teilenummer",
        )

    with col3:
        zoll_opt = ["Alle"] + sorted(df["Zoll"].unique().tolist())
        st.selectbox(
            "Zoll:",
            options=zoll_opt,
            key="top_zoll_filter",
            help="Filtere nach Zoll-Größe",
        )

    with col4:
        st.checkbox(
            "Mit Bestand",
            key="top_bestand_filter",
            help="Nur Reifen mit positivem Lagerbestand anzeigen",
        )

    # EINZIGE QUELLEN
    saison_filter = st.session_state.top_saison_filter
    zoll_filter   = st.session_state.top_zoll_filter
    mit_bestand   = st.session_state.top_bestand_filter

    # FILTER BEREITS HIER ANWENDEN FÜR DYNAMISCHE REIFENGRÖSSEN
    filtered_for_sizes = df.copy()

    if mit_bestand:
        filtered_for_sizes = filtered_for_sizes[(filtered_for_sizes['Bestand'].notna()) & (filtered_for_sizes['Bestand'] > 0)]
    if saison_filter != "Alle":
        filtered_for_sizes = filtered_for_sizes[filtered_for_sizes['Saison'] == saison_filter]
    if zoll_filter != "Alle":
        filtered_for_sizes = filtered_for_sizes[filtered_for_sizes["Zoll"] == int(zoll_filter)]

    # AUFKLAPPBARE REIFENGRÖSSEN MIT DYNAMISCHER LISTE
    with st.expander("Gängige Reifengrößen", expanded=False):
        dynamic_sizes = get_dynamic_tire_sizes(filtered_for_sizes, max_sizes=12)
        if dynamic_sizes:
            st.markdown(f"**Häufigste Reifengrößen aus {len(filtered_for_sizes)} verfügbaren Reifen:**")
            cols = st.columns(4)
            for i, size in enumerate(dynamic_sizes):
                with cols[i % 4]:
                    button_type = "primary" if st.session_state.selected_size == size else "secondary"
                    if st.button(size, key=f"size_btn_{size}", use_container_width=True, type=button_type):
                        st.session_state.selected_size = size
                        st.rerun()
        else:
            st.info("Keine Reifengrößen für die aktuelle Filterauswahl verfügbar.")

        st.markdown("---")
        col_reset1, col_reset2, col_reset3 = st.columns([1, 1, 1])
        with col_reset2:
            if st.button("Schnellauswahl zurücksetzen", key="reset_selection", help="Reifengrößen-Auswahl aufheben", use_container_width=True):
                if st.session_state.selected_size:
                    st.session_state.selected_size = None
                    st.rerun()

    # Sidebar: Detailfilter
    with st.sidebar:
        st.header("Detailfilter")
        breite_opt = ["Alle"] + sorted(df["Breite"].unique().tolist())
        hoehe_opt = ["Alle"] + sorted(df["Hoehe"].unique().tolist())
        fabrikat_opt = ["Alle"] + sorted([x for x in df["Fabrikat"].dropna().unique().tolist()])

        breite_filter = st.selectbox("Breite (mm)", options=breite_opt, index=0)
        hoehe_filter = st.selectbox("Höhe (%)", options=hoehe_opt, index=0)
        fabrikat = st.selectbox("Fabrikat", options=fabrikat_opt, index=0)

        loadindex_opt = ["Alle"] + sorted([x for x in df["Loadindex"].dropna().astype(str).unique().tolist()])
        speedindex_opt = ["Alle"] + sorted([x for x in df["Speedindex"].dropna().astype(str).unique().tolist()])

        loadindex_filter = st.selectbox("Loadindex", options=loadindex_opt, index=0)
        speedindex_filter = st.selectbox("Speedindex", options=speedindex_opt, index=0)

        min_price = float(df["Preis_EUR"].min())
        max_price = float(df["Preis_EUR"].max())
        min_preis, max_preis = st.slider(
            "Preisbereich (EUR)",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price),
            step=5.0,
        )

        sortierung = st.selectbox(
            "Sortieren nach",
            options=["Preis aufsteigend", "Preis absteigend", "Fabrikat", "Reifengröße", "Saison"],
        )

        show_stats = st.checkbox("Statistiken anzeigen", value=False)

    # Komplette Filterung
    filtered = df.copy()
    if mit_bestand:
        filtered = filtered[(filtered['Bestand'].notna()) & (filtered['Bestand'] > 0)]
    if saison_filter != "Alle":
        filtered = filtered[filtered['Saison'] == saison_filter]
    if zoll_filter != "Alle":
        filtered = filtered[filtered["Zoll"] == int(zoll_filter)]

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

    if sortierung == "Preis aufsteigend":
        filtered = filtered.sort_values("Preis_EUR")
    elif sortierung == "Preis absteigend":
        filtered = filtered.sort_values("Preis_EUR", ascending=False)
    elif sortierung == "Fabrikat":
        filtered = filtered.sort_values(["Fabrikat", "Preis_EUR"])
    elif sortierung == "Reifengröße":
        filtered = filtered.sort_values(["Zoll", "Breite", "Hoehe", "Preis_EUR"])
    elif sortierung == "Saison":
        filtered = filtered.sort_values(["Saison", "Preis_EUR"])

    # Gefundene Reifen anzeigen
    if len(filtered) > 0:
        st.markdown("---")
        filter_info = []
        if mit_bestand:
            filter_info.append("mit Bestand")
        if saison_filter != "Alle":
            filter_info.append(f"({saison_filter})")
        if zoll_filter != "Alle":
            filter_info.append(f"{zoll_filter} Zoll")

        header_text = f"Gefundene Reifen: {len(filtered)}"
        if filter_info:
            header_text += f" {' '.join(filter_info)}"

        st.subheader(header_text)
        render_tire_list(filtered)

        if show_stats:
            render_statistics(filtered)
    else:
        filter_info = []
        if mit_bestand:
            filter_info.append("mit Bestand")
        if saison_filter != "Alle":
            filter_info.append(f"Saison: {saison_filter}")
        if zoll_filter != "Alle":
            filter_info.append(f"Zoll: {zoll_filter}")
        if filter_info:
            st.warning(f"Keine Reifen {' und '.join(filter_info)} gefunden. Bitte Filter anpassen.")
        else:
            st.warning("Keine Reifen gefunden. Bitte Filter anpassen oder andere Reifengröße wählen.")

    render_legend(mit_bestand, saison_filter, zoll_filter)

if __name__ == "__main__":
    main()