# pages/01_Reifen_Suche.py

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
        --primary-color: #0ea5e9;  --primary-dark: #0284c7;  --secondary-color: #64748b;
        --success-color: #16a34a;  --warning-color: #f59e0b; --error-color: #dc2626;
        --background-light: #f8fafc; --background-white: #ffffff;
        --text-primary: #1e293b; --text-secondary: #64748b; --border-color: #e2e8f0;
        --border-radius: 8px; --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1); --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    }
    [data-testid="stAppViewContainer"] .block-container { padding-top: 0.5rem !important; }
    .main > div { padding-top: 0.2rem; }
    .warning-box {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        padding: 1rem; border-radius: var(--border-radius); border-left: 4px solid var(--warning-color);
        margin: 1rem 0; box-shadow: var(--shadow-sm);
    }
    .config-card {
        border: 2px solid var(--primary-color); border-radius: 10px;
        padding: 1rem; margin: 0.5rem 0; background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        box-shadow: var(--shadow-md);
    }
    .saison-badge { display:inline-block; padding:0.25rem 0.5rem; border-radius:4px; font-size:0.75rem; font-weight:600; margin-left:0.5rem; }
    .saison-winter{background:#dbeafe;color:#1e40af;} .saison-sommer{background:#fef3c7;color:#92400e;} .saison-ganzjahres{background:#d1fae5;color:#065f46;}
    [data-testid="metric-container"] { background: var(--background-white); border: 1px solid var(--border-color); padding: 1rem; border-radius: var(--border-radius); box-shadow: var(--shadow-sm); }
    .stButton > button { border-radius: var(--border-radius); border: none; font-weight: 500; transition: all 0.2s ease; font-family: 'Inter', sans-serif; }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: var(--shadow-md); }
    .cart-indicator { color:#16a34a; font-weight:bold; margin-left:0.5rem; }
    .logo-container { display:flex; justify-content:center; align-items:center; padding:1.9rem 0 0.5rem 0; margin:0; }
    .logo-spacer { height:64px; }
</style>
"""
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# ================================================================================================
# HELPER FUNCTIONS
# ================================================================================================
def get_efficiency_emoji(rating):
    if pd.isna(rating): return ""
    rating = str(rating).strip().upper()[:1]
    return {"A":"[A]","B":"[B]","C":"[C]","D":"[D]","E":"[E]","F":"[F]","G":"[G]"}.get(rating,"")

def get_stock_display(stock_value):
    if pd.isna(stock_value) or stock_value == '': return "unbekannt"
    try:
        stock_num = float(stock_value)
        if stock_num < 0: return f"NACHBESTELLEN ({int(stock_num)})"
        if stock_num == 0: return f"AUSVERKAUFT ({int(stock_num)})"
        return f"VERFÜGBAR ({int(stock_num)})"
    except: return "unbekannt"

def get_saison_from_teilenummer(teilenummer):
    if pd.isna(teilenummer) or teilenummer == '': return "Unbekannt"
    t = str(teilenummer).strip().upper()
    if t.startswith('ZTW'): return "Winter"
    if t.startswith('ZTR'): return "Ganzjahres"
    if t.startswith('ZTS'): return "Sommer"
    return "Unbekannt"

def get_saison_badge_html(saison):
    if saison == "Winter": return '<span class="saison-badge saison-winter">Winter</span>'
    if saison == "Sommer": return '<span class="saison-badge saison-sommer">Sommer</span>'
    if saison == "Ganzjahres": return '<span class="saison-badge saison-ganzjahres">Ganzjahres</span>'
    return '<span class="saison-badge">Unbekannt</span>'

def is_tire_in_cart(tire_data):
    tire_id = f"{tire_data['Teilenummer']}_{tire_data['Preis_EUR']}"
    return any(item['id'] == tire_id for item in st.session_state.cart_items)

def get_dynamic_tire_sizes(filtered_df, max_sizes=12):
    if filtered_df.empty: return []
    unique = filtered_df[['Breite','Hoehe','Zoll']].drop_duplicates().sort_values(['Zoll','Breite','Hoehe'])
    unique['size_str'] = unique['Breite'].astype(str) + '/' + unique['Hoehe'].astype(str) + ' R' + unique['Zoll'].astype(str)
    return unique.head(min(max_sizes, len(unique)))['size_str'].tolist()

def create_metric_card(title, value, delta=None, help_text=None):
    delta_html = ""
    if delta:
        color = "var(--success-color)" if delta.startswith("↗") else "var(--error-color)" if delta.startswith("↘") else "var(--text-secondary)"
        delta_html = f'<div style="color:{color};font-size:0.9rem;margin-top:0.25rem;">{delta}</div>'
    help_html = f'<div style="color:var(--text-secondary);font-size:0.8rem;margin-top:0.5rem;">{help_text}</div>' if help_text else ""
    return f"""
    <div style="background:var(--background-white);border:1px solid var(--border-color);border-radius:var(--border-radius);padding:1rem;box-shadow:var(--shadow-sm);transition:transform .2s;">
        <div style="color:var(--text-secondary);font-size:.9rem;font-weight:500;">{title}</div>
        <div style="color:var(--text-primary);font-size:1.8rem;font-weight:700;margin:.25rem 0;">{value}</div>
        {delta_html}{help_html}
    </div>"""

def clean_dataframe(df):
    if df.empty: return df
    if "Preis_EUR" in df.columns:
        if df["Preis_EUR"].dtype == object:
            df["Preis_EUR"] = (df["Preis_EUR"].astype(str)
                               .str.replace(",",".",regex=False)
                               .str.replace("€","",regex=False)
                               .str.strip())
        df["Preis_EUR"] = pd.to_numeric(df["Preis_EUR"], errors="coerce")
    for c in ["Breite","Hoehe","Zoll"]:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    if "Bestand" in df.columns: df["Bestand"] = pd.to_numeric(df["Bestand"], errors="coerce")
    for col in ["Fabrikat","Profil","Kraftstoffeffizienz","Nasshaftung","Loadindex","Speedindex","Teilenummer","Geräuschklasse"]:
        if col not in df.columns: df[col] = pd.NA
    if "Saison" not in df.columns: df["Saison"] = df["Teilenummer"].apply(get_saison_from_teilenummer)
    df = df.dropna(subset=["Preis_EUR","Breite","Hoehe","Zoll"], how="any")
    if not df.empty:
        df["Breite"] = df["Breite"].astype(int); df["Hoehe"] = df["Hoehe"].astype(int); df["Zoll"] = df["Zoll"].astype(int)
    return df

# ================================================================================================
# DATA MANAGEMENT - REIFEN CSV
# ================================================================================================
def load_reifen_data():
    data_dir = Path("data")
    csv_path = data_dir / "Ramsperger_Winterreifen_20250826_160010.csv"
    try:
        if csv_path.exists():
            df = pd.read_csv(csv_path, encoding='utf-8')
            return clean_dataframe(df)
        else:
            return create_fallback_data()
    except Exception:
        return create_fallback_data()

def create_fallback_data():
    sample = {
        'Breite':[195,205,215,225,195,205,215,225],
        'Hoehe':[65,55,60,55,60,60,55,50],
        'Zoll':[15,16,16,17,16,17,17,18],
        'Fabrikat':['Continental','Michelin','Bridgestone','Pirelli','Continental','Michelin','Bridgestone','Pirelli'],
        'Profil':['WinterContact TS850','Alpin 6','Blizzak LM005','Winter Sottozero 3','WinterContact TS860','Alpin 5','Blizzak WS90','Winter Sottozero Serie II'],
        'Teilenummer':['ZTW15494940000','ZTW03528700000','ZTW19394','ZTW8019227308853','ZTS15495040000','ZTS03528800000','ZTR19395','ZTR8019227308854'],
        'Preis_EUR':[89.90,95.50,87.20,99.90,92.90,98.50,89.20,103.90],
        'Loadindex':[91,91,94,94,88,91,94,97],
        'Speedindex':['T','H','H','V','H','H','H','V'],
        'Kraftstoffeffizienz':['C','B','A','C','C','B','A','C'],
        'Nasshaftung':['B','A','A','B','B','A','A','B'],
        'Bestand':[25,12,8,15,30,0,-5,20],
        'Geräuschklasse':[68,69,67,70,68,69,67,71]
    }
    df = pd.DataFrame(sample); df["Saison"] = df["Teilenummer"].apply(get_saison_from_teilenummer); return df

def get_reifen_data():
    if 'reifen_data' not in st.session_state or 'data_loaded' not in st.session_state:
        st.session_state.reifen_data = load_reifen_data()
        st.session_state.data_loaded = True
    return st.session_state.reifen_data

# ================================================================================================
# SERVICE-PAKETE – CSV-GETRIEBEN, ROBUSTES LADEN
# ================================================================================================
SERVICE_REQUIRED = {"Positionsnummer","Bezeichnung","Teilenummer","Detail","Preis","Hinweis","Kategorie","Zoll","Anzahl"}

SERVICE_HEADER_ALIASES = {
    'position':'Positionsnummer','positionsnummer':'Positionsnummer','pos':'Positionsnummer',
    'name':'Bezeichnung','bezeichung':'Bezeichnung','title':'Bezeichnung',
    'teilnr':'Teilenummer','teilenr':'Teilenummer','tnr':'Teilenummer','artikelnummer':'Teilenummer',
    'detailtext':'Detail',
    'price':'Preis','preis_eur':'Preis','aktionspreis':'Preis',
    'note':'Hinweis','hinweise':'Hinweis',
    'kategorie':'Kategorie','category':'Kategorie',
    'zollgruppe':'Zoll','zollgroesse':'Zoll','zollgröße':'Zoll',
    'anzahl_raeder':'Anzahl','menge':'Anzahl','räder':'Anzahl','raeder':'Anzahl'
}

def _read_services_csv(csv_path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(csv_path, sep=None, engine='python', encoding='utf-8-sig')
    except Exception:
        try:
            df = pd.read_csv(csv_path, sep=",", encoding='utf-8-sig')
        except Exception:
            df = pd.read_csv(csv_path, sep=";", encoding='utf-8-sig')
    return df

def _normalize_service_df(df: pd.DataFrame) -> pd.DataFrame:
    original_cols = list(df.columns)
    new_cols = []
    for c in original_cols:
        key = str(c).replace("\ufeff","").strip()
        low = key.lower()
        if low in SERVICE_HEADER_ALIASES:
            new_cols.append(SERVICE_HEADER_ALIASES[low])
        else:
            for req in SERVICE_REQUIRED:
                if low == req.lower():
                    new_cols.append(req); break
            else:
                new_cols.append(key)
    df.columns = new_cols

    if "Kategorie" in df.columns:
        df["Kategorie"] = df["Kategorie"].astype(str).str.strip().str.lower()
    if "Zoll" in df.columns:
        df["Zoll"] = df["Zoll"].astype(str).str.strip().str.lower()
    if "Anzahl" in df.columns:
        df["Anzahl"] = pd.to_numeric(df["Anzahl"], errors="coerce").astype("Int64")
    if "Preis" in df.columns:
        df["Preis"] = (df["Preis"].astype(str)
                       .str.replace("€","",regex=False)
                       .str.replace(",",".",regex=False)
                       .str.replace("-","",regex=False)
                       .str.strip())
        df["Preis"] = pd.to_numeric(df["Preis"], errors="coerce")
    for c in ["Positionsnummer","Bezeichnung","Teilenummer","Detail","Hinweis"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.replace("\ufeff","",regex=False).str.strip()
    return df

def _validate_service_df(df: pd.DataFrame) -> bool:
    missing = SERVICE_REQUIRED - set(df.columns)
    if missing:
        st.error(f"services_config.csv: fehlende Spalten: {sorted(list(missing))}")
        return False
    if df.empty:
        st.error("services_config.csv: Datei enthält keine Daten.")
        return False
    return True

def create_default_service_packages() -> pd.DataFrame:
    packages = [
        # Reifenservice bis 17
        {'Positionsnummer':'Z4409','Bezeichnung':'SERVICE PAKET REIFENSERVICE 1 RAD','Teilenummer':'44401995','Detail':'REIFENSERVICE 1 RAD','Preis':25.00,'Hinweis':'inkl. Auswuchtgewichte, Ventil und Altreifenentsorgung','Kategorie':'reifenservice','Zoll':'bis_17','Anzahl':1},
        {'Positionsnummer':'Z44091','Bezeichnung':'SERVICE PAKET REIFENSERVICE 2 RÄDER','Teilenummer':'44402095','Detail':'REIFENSERVICE 2 RÄDER','Preis':50.00,'Hinweis':'inkl. Auswuchtgewichte, Ventile und Altreifenentsorgung','Kategorie':'reifenservice','Zoll':'bis_17','Anzahl':2},
        {'Positionsnummer':'Z44092','Bezeichnung':'SERVICE PAKET REIFENSERVICE 4 RÄDER','Teilenummer':'44402295','Detail':'REIFENSERVICE 4 RÄDER','Preis':100.00,'Hinweis':'inkl. Auswuchtgewichte, Ventile und Altreifenentsorgung','Kategorie':'reifenservice','Zoll':'bis_17','Anzahl':4},
        # 18-19
        {'Positionsnummer':'Z44093','Bezeichnung':'SERVICE PAKET REIFENSERVICE 1 RAD','Teilenummer':'44401996','Detail':'REIFENSERVICE 1 RAD','Preis':30.00,'Hinweis':'inkl. Auswuchtgewichte, Ventil und Altreifenentsorgung','Kategorie':'reifenservice','Zoll':'18_19','Anzahl':1},
        {'Positionsnummer':'Z44094','Bezeichnung':'SERVICE PAKET REIFENSERVICE 2 RÄDER','Teilenummer':'44402096','Detail':'REIFENSERVICE 2 RÄDER','Preis':60.00,'Hinweis':'inkl. Auswuchtgewichte, Ventile und Altreifenentsorgung','Kategorie':'reifenservice','Zoll':'18_19','Anzahl':2},
        {'Positionsnummer':'Z44095','Bezeichnung':'SERVICE PAKET REIFENSERVICE 4 RÄDER','Teilenummer':'44402296','Detail':'REIFENSERVICE 4 RÄDER','Preis':120.00,'Hinweis':'inkl. Auswuchtgewichte, Ventile und Altreifenentsorgung','Kategorie':'reifenservice','Zoll':'18_19','Anzahl':4},
        # ab 20
        {'Positionsnummer':'Z44096','Bezeichnung':'SERVICE PAKET REIFENSERVICE 1 RAD','Teilenummer':'44401997','Detail':'REIFENSERVICE 1 RAD','Preis':40.00,'Hinweis':'inkl. Auswuchtgewichte, Ventil und Altreifenentsorgung','Kategorie':'reifenservice','Zoll':'ab_20','Anzahl':1},
        {'Positionsnummer':'Z44097','Bezeichnung':'SERVICE PAKET REIFENSERVICE 2 RÄDER','Teilenummer':'44402097','Detail':'REIFENSERVICE 2 RÄDER','Preis':80.00,'Hinweis':'inkl. Auswuchtgewichte, Ventile und Altreifenentsorgung','Kategorie':'reifenservice','Zoll':'ab_20','Anzahl':2},
        {'Positionsnummer':'Z44098','Bezeichnung':'SERVICE PAKET REIFENSERVICE 4 RÄDER','Teilenummer':'44402297','Detail':'REIFENSERVICE 4 RÄDER','Preis':160.00,'Hinweis':'inkl. Auswuchtgewichte, Ventile und Altreifenentsorgung','Kategorie':'reifenservice','Zoll':'ab_20','Anzahl':4},
        # Auswuchten
        {'Positionsnummer':'Z4404','Bezeichnung':'SERVICE PAKET RÄDER AUSWUCHTEN 1 RAD','Teilenummer':'44056799','Detail':'1 RAD AUSGEWUCHTET','Preis':7.50,'Hinweis':'inkl. Auswuchtgewichte','Kategorie':'auswuchten','Zoll':'alle','Anzahl':1},
        {'Positionsnummer':'Z44041','Bezeichnung':'SERVICE PAKET RÄDER AUSWUCHTEN 2 RÄDER','Teilenummer':'44056899','Detail':'2 RÄDER AUSGEWUCHTET','Preis':15.00,'Hinweis':'inkl. Auswuchtgewichte','Kategorie':'auswuchten','Zoll':'alle','Anzahl':2},
        {'Positionsnummer':'Z44042','Bezeichnung':'SERVICE PAKET RÄDER AUSWUCHTEN 4 RÄDER','Teilenummer':'44056999','Detail':'4 RÄDER AUSGEWUCHTET','Preis':30.00,'Hinweis':'inkl. Auswuchtgewichte','Kategorie':'auswuchten','Zoll':'alle','Anzahl':4},
        # Räderwechsel
        {'Positionsnummer':'Z44058','Bezeichnung':'SERVICE PAKET RÄDERWECHSEL','Teilenummer':'44051091','Detail':'RÄDERWECHSEL (1 Rad)','Preis':9.98,'Hinweis':'','Kategorie':'raederwechsel','Zoll':'alle','Anzahl':1},
        {'Positionsnummer':'Z44059','Bezeichnung':'SERVICE PAKET RÄDERWECHSEL','Teilenummer':'44051092','Detail':'RÄDERWECHSEL (2 Räder)','Preis':19.95,'Hinweis':'','Kategorie':'raederwechsel','Zoll':'alle','Anzahl':2},
        {'Positionsnummer':'Z44060','Bezeichnung':'SERVICE PAKET RÄDERWECHSEL','Teilenummer':'44051099','Detail':'RÄDERWECHSEL','Preis':39.90,'Hinweis':'','Kategorie':'raederwechsel','Zoll':'alle','Anzahl':4},
        # Kombi
        {'Positionsnummer':'Z44053','Bezeichnung':'RÄDERWECHSEL INKL. EINLAGERUNG KOMFORT','Teilenummer':'44051099','Detail':'RÄDERWECHSEL, SAISONALE RÄDEREINLAGERUNG','Preis':109.90,'Hinweis':'','Kategorie':'kombi_komfort','Zoll':'alle','Anzahl':4},
        {'Positionsnummer':'Z44066','Bezeichnung':'SERVICE PAKET RÄDERWECHSEL & EINLAGERUNG','Teilenummer':'44051099','Detail':'RÄDERWECHSEL, SAISONALE RÄDEREINLAGERUNG','Preis':94.90,'Hinweis':'','Kategorie':'kombi_standard','Zoll':'alle','Anzahl':4},
    ]
    return pd.DataFrame(packages)

def load_service_packages() -> pd.DataFrame:
    data_dir = Path("data"); csv_path = data_dir / "ramsperger_services_config.csv"
    if not csv_path.exists(): return create_default_service_packages()
    try:
        df = _read_services_csv(csv_path)
        df = _normalize_service_df(df)
        if not _validate_service_df(df): return create_default_service_packages()
        return df
    except Exception:
        st.error("services_config.csv konnte nicht gelesen werden. Standard-Pakete werden verwendet.")
        return create_default_service_packages()

def get_service_packages() -> pd.DataFrame:
    if 'service_packages' not in st.session_state:
        st.session_state.service_packages = load_service_packages()
    return st.session_state.service_packages

# ================================================================================================
# CART MANAGEMENT
# ================================================================================================
def add_to_cart_with_config(tire_data, quantity, services):
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
    st.session_state.cart_services[tire_id] = services  # Liste gewählter Pakete + Summe
    st.session_state.cart_count = len(st.session_state.cart_items)
    return True, f"{quantity}x {cart_item['Reifengröße']} hinzugefügt"

def remove_from_cart(tire_data):
    tire_id = f"{tire_data['Teilenummer']}_{tire_data['Preis_EUR']}"
    st.session_state.cart_items = [item for item in st.session_state.cart_items if item['id'] != tire_id]
    if tire_id in st.session_state.cart_quantities: del st.session_state.cart_quantities[tire_id]
    if tire_id in st.session_state.cart_services: del st.session_state.cart_services[tire_id]
    st.session_state.cart_count = len(st.session_state.cart_items)
    return True, f"Reifen {tire_data['Fabrikat']} {tire_data['Profil']} aus Warenkorb entfernt"

# ================================================================================================
# SESSION STATE INITIALISIERUNG
# ================================================================================================
def init_session_state():
    if 'top_saison_filter' not in st.session_state: st.session_state.top_saison_filter = "Alle"
    if 'top_zoll_filter' not in st.session_state:   st.session_state.top_zoll_filter = "Alle"
    if 'top_bestand_filter' not in st.session_state: st.session_state.top_bestand_filter = True
    if 'selected_size' not in st.session_state:     st.session_state.selected_size = None
    if 'opened_tire_cards' not in st.session_state: st.session_state.opened_tire_cards = set()
    if 'cart_items' not in st.session_state:        st.session_state.cart_items = []
    if 'cart_quantities' not in st.session_state:   st.session_state.cart_quantities = {}
    if 'cart_services' not in st.session_state:     st.session_state.cart_services = {}
    if 'cart_count' not in st.session_state:        st.session_state.cart_count = 0

# ================================================================================================
# RENDER FUNCTIONS – neue Pakete: Schalter unter Gesamtsumme, alle Pakete als Checkboxen
# ================================================================================================
def render_config_card(row, idx, filtered_df):
    st.markdown(f"""<div class="config-card">""", unsafe_allow_html=True)
    saison_badge = get_saison_badge_html(row.get('Saison', 'Unbekannt'))
    st.markdown(f"**Konfiguration für {row['Reifengröße']} - {row['Fabrikat']} {row['Profil']}** {saison_badge}", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    # --- Linke Spalte: Menge & Reifenpreis ---
    with col_left:
        quantity = st.number_input("Stückzahl:", min_value=1, max_value=8, value=4, step=1, key=f"qty_{idx}", help="Anzahl der Reifen (1-8 Stück)")
        tire_total = float(row['Preis_EUR']) * quantity
        st.metric("Reifen-Gesamtpreis", f"{tire_total:.2f} EUR")

    # --- Rechte Spalte: 'In Warenkorb legen' (neue Position) ---
    with col_right:
        # wir zeigen hier nur den Add-to-Cart Button
        add_cart_clicked = st.button("In Warenkorb legen", key=f"add_cart_top_{idx}", use_container_width=True, type="primary")

    # --- Service-Pakete unter der Gesamtsumme auswählen ---
    # Platzhalter für später befüllte Summen
    service_total = 0.0
    selected_packages = []

    # Gesamtsumme (vor Services) anzeigen
    st.markdown(f"### **Gesamtsumme: {tire_total:.2f} EUR**")

    # Schalter unter der Gesamtsumme
    show_services = st.checkbox("Service-Leistungen hinzufügen", key=f"services_toggle_bottom_{idx}", value=False)

    if show_services:
        with st.expander("Pakete auswählen", expanded=True):
            # Alle Pakete aus CSV als Checkboxen (keine Filterung)
            pkgs = get_service_packages().reset_index(drop=True)
            if len(pkgs) == 0:
                st.info("Keine Service-Pakete vorhanden.")
            else:
                for i, pkg in pkgs.iterrows():
                    # Sichere Preis-Anzeige
                    price = float(pkg["Preis"]) if pd.notna(pkg["Preis"]) else 0.0
                    label = f"{pkg['Bezeichnung']} – {price:.2f} EUR"
                    # Zusatzinfo klein darunter
                    hint_parts = []
                    if pd.notna(pkg.get("Positionsnummer")) and str(pkg["Positionsnummer"]).strip():
                        hint_parts.append(str(pkg["Positionsnummer"]).strip())
                    if pd.notna(pkg.get("Detail")) and str(pkg["Detail"]).strip():
                        hint_parts.append(str(pkg["Detail"]).strip())
                    if pd.notna(pkg.get("Hinweis")) and str(pkg["Hinweis"]).strip():
                        hint_parts.append(str(pkg["Hinweis"]).strip())
                    hint = " | ".join(hint_parts)
                    checked = st.checkbox(label, key=f"pkg_{idx}_{i}")
                    if hint:
                        st.caption(hint)
                    if checked:
                        service_total += price
                        selected_packages.append({
                            'pos': str(pkg['Positionsnummer']),
                            'title': str(pkg['Bezeichnung']),
                            'preis': price
                        })

        if service_total > 0:
            st.metric("Service-Kosten", f"{service_total:.2f} EUR")

    grand_total = tire_total + service_total
    # Aktualisierte Gesamtsumme (inkl. Services) direkt unter Service-Bereich zeigen
    st.markdown(f"### **Gesamtsumme: {grand_total:.2f} EUR**")

    # Auswahl im Session State speichern (damit Button oben sie mitnimmt)
    st.session_state[f"selected_packages_{idx}"] = selected_packages
    st.session_state[f"service_total_{idx}"] = service_total

    # Buttons unten: nur Abbrechen (Add-to-Cart ist oben)
    col_cancel, _ = st.columns([1, 3])
    with col_cancel:
        if st.button("Abbrechen", key=f"cancel_{idx}", use_container_width=True):
            card_key = f"tire_card_{idx}"
            st.session_state.opened_tire_cards.discard(card_key)
            st.rerun()

    # Verarbeitung des Add-to-Cart Buttons (oben rechts)
    if add_cart_clicked:
        services_payload = {
            'pakete': st.session_state.get(f"selected_packages_{idx}", []),
            'service_summe': st.session_state.get(f"service_total_{idx}", 0.0)
        }
        tire_data = filtered_df.iloc[idx]
        success, message = add_to_cart_with_config(tire_data, quantity, services_payload)
        if success:
            st.success(message)
            card_key = f"tire_card_{idx}"
            st.session_state.opened_tire_cards.discard(card_key)
            st.rerun()
        else:
            st.warning(message)

    st.markdown("</div>", unsafe_allow_html=True)

def render_tire_list(filtered_df):
    display = filtered_df.copy().reset_index(drop=True)
    display["Reifengröße"] = display["Breite"].astype(str) + "/" + display["Hoehe"].astype(str) + " R" + display["Zoll"].astype(str)
    st.markdown("**Reifen auswählen und konfigurieren:**")

    for idx, row in display.iterrows():
        is_in_cart = is_tire_in_cart(row)
        if is_in_cart: col_info, col_button, col_remove = st.columns([4,1,1])
        else:          col_info, col_button = st.columns([5,1])

        with col_info:
            badge = get_saison_badge_html(row.get('Saison','Unbekannt'))
            cart_indicator = '<span class="cart-indicator">🛒 Im Warenkorb</span>' if is_in_cart else ''
            st.markdown(f"**{row['Reifengröße']}** - {row['Fabrikat']} {row['Profil']} {badge} {cart_indicator}", unsafe_allow_html=True)
            preis_display = f"**{float(row['Preis_EUR']):.2f} EUR**"
            bestand = get_stock_display(row['Bestand'])
            tragkraft = f"{row['Loadindex']}{row['Speedindex']}" if pd.notna(row['Loadindex']) and pd.notna(row['Speedindex']) else ""
            info = f"Preis: {preis_display}"
            if bestand != "unbekannt": info += f" | Bestand: {bestand}"
            if tragkraft: info += f" | Tragkraft: {tragkraft}"
            st.markdown(info)
            labels = []
            if pd.notna(row['Kraftstoffeffizienz']) and row['Kraftstoffeffizienz']!='': labels.append(f"Kraftstoff {get_efficiency_emoji(row['Kraftstoffeffizienz'])}")
            if pd.notna(row['Nasshaftung']) and row['Nasshaftung']!='': labels.append(f"Nasshaftung {get_efficiency_emoji(row['Nasshaftung'])}")
            if pd.notna(row['Geräuschklasse']) and row['Geräuschklasse']!='': labels.append(f"Lärm {int(row['Geräuschklasse'])}dB")
            if labels: st.markdown(f"EU-Label: {' | '.join(labels)}")
            st.markdown(f"<small>Teilenummer: {row['Teilenummer']}</small>", unsafe_allow_html=True)

        with col_button:
            card_key = f"tire_card_{idx}"
            is_open = card_key in st.session_state.opened_tire_cards
            if st.button("Auswählen" if not is_open else "Schließen", key=f"select_btn_{idx}", use_container_width=True, type="primary" if not is_open else "secondary"):
                if is_open: st.session_state.opened_tire_cards.remove(card_key)
                else:       st.session_state.opened_tire_cards.add(card_key)
                st.rerun()

        if is_in_cart:
            with col_remove:
                if st.button("🗑️", key=f"remove_btn_{idx}", use_container_width=True, type="secondary", help="Aus Warenkorb entfernen"):
                    success, message = remove_from_cart(row)
                    if success:
                        st.success(message); st.rerun()
                    else:
                        st.error("Fehler beim Entfernen aus dem Warenkorb")

        if card_key in st.session_state.opened_tire_cards:
            render_config_card(row, idx, filtered_df)
        st.markdown("---")

def render_statistics(filtered_df):
    st.subheader("Statistiken")
    col1,col2,col3,col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_card("Durchschnittspreis", f"{filtered_df['Preis_EUR'].mean():.2f} EUR"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Günstigster Reifen", f"{filtered_df['Preis_EUR'].min():.2f} EUR"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("Teuerster Reifen", f"{filtered_df['Preis_EUR'].max():.2f} EUR"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("Verfügbare Größen", str(len(filtered_df[["Breite","Hoehe","Zoll"]].drop_duplicates()))), unsafe_allow_html=True)

def render_legend(mit_bestand, saison_filter, zoll_filter):
    st.markdown("---"); st.markdown("**Legende:**")
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("**Speedindex (max. zulässige Geschwindigkeit):**")
        st.markdown("R = 170 km/h | S = 180 km/h | T = 190 km/h | H = 210 km/h | V = 240 km/h")
        st.markdown("**Saison-Kennzeichnung:**")
        st.markdown("ZTW = Winter | ZTR = Ganzjahres | ZTS = Sommer")
        st.markdown("**Service-Pakete:**")
        st.markdown("Alle auswählbar unter der Gesamtsumme (CSV-basiert)")
    with c2:
        st.markdown("**Reifengröße:** Breite/Höhe R Zoll")
        st.markdown("**Loadindex:** Tragfähigkeit pro Reifen in kg")
        st.markdown("**Bestand:** NACHBESTELLEN | AUSVERKAUFT | VERFÜGBAR | unbekannt")
        st.markdown("**🛒 Im Warenkorb:** Reifen bereits im Warenkorb hinzugefügt")
        st.markdown("**🗑️ Button:** Reifen aus Warenkorb entfernen")
        info = []
        if mit_bestand: info.append("Bestandsfilter aktiv")
        if saison_filter != "Alle": info.append(f"Saison: {saison_filter}")
        if zoll_filter != "Alle": info.append(f"Zoll: {zoll_filter}")
        if info: st.markdown(f"**Aktive Filter:** {' | '.join(info)}")

# ================================================================================================
# MAIN FUNCTION
# ================================================================================================
def main():
    init_session_state()

    # Logo Header
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    try:
        st.image("data/Logo_2.png", width=400)
    except:
        st.markdown("### Ramsperger Automobile")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-spacer"></div>', unsafe_allow_html=True)

    # Daten laden
    df = get_reifen_data()
    if df.empty:
        st.warning("Keine Reifen-Daten verfügbar. Bitte prüfe die CSV-Datei.")
        st.stop()

    # Top-Filter
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        cart_count = st.session_state.cart_count
        cart_text = f"Warenkorb ({cart_count})" if cart_count > 0 else "Warenkorb"
        if st.button(cart_text, key="nav_cart", help="Zum Warenkorb wechseln", use_container_width=True, type="primary"):
            st.switch_page("pages/02_Warenkorb.py")
    with c2:
        st.selectbox("Saison-Typ:", options=["Alle","Winter","Sommer","Ganzjahres"], key="top_saison_filter", help="Filtere nach Reifen-Saison basierend auf Teilenummer")
    with c3:
        st.selectbox("Zoll:", options=["Alle"] + sorted(df["Zoll"].unique().tolist()), key="top_zoll_filter", help="Filtere nach Zoll-Größe")
    with c4:
        st.checkbox("Mit Bestand", key="top_bestand_filter", help="Nur Reifen mit positivem Lagerbestand anzeigen")

    saison_filter = st.session_state.top_saison_filter
    zoll_filter   = st.session_state.top_zoll_filter
    mit_bestand   = st.session_state.top_bestand_filter

    # Für dynamische Größen
    sizes_df = df.copy()
    if mit_bestand: sizes_df = sizes_df[(sizes_df['Bestand'].notna()) & (sizes_df['Bestand'] > 0)]
    if saison_filter != "Alle": sizes_df = sizes_df[sizes_df['Saison'] == saison_filter]
    if zoll_filter != "Alle":  sizes_df = sizes_df[sizes_df["Zoll"] == int(zoll_filter)]

    with st.expander("Gängige Reifengrößen", expanded=False):
        dyn = get_dynamic_tire_sizes(sizes_df, max_sizes=12)
        if dyn:
            st.markdown(f"**Häufigste Reifengrößen aus {len(sizes_df)} verfügbaren Reifen:**")
            cols = st.columns(4)
            for i, size in enumerate(dyn):
                with cols[i % 4]:
                    btn_type = "primary" if st.session_state.selected_size == size else "secondary"
                    if st.button(size, key=f"size_btn_{size}", use_container_width=True, type=btn_type):
                        st.session_state.selected_size = size; st.rerun()
        else:
            st.info("Keine Reifengrößen für die aktuelle Filterauswahl verfügbar.")
        st.markdown("---")
        cA, cB, cC = st.columns([1,1,1])
        with cB:
            if st.button("Schnellauswahl zurücksetzen", key="reset_selection", use_container_width=True, help="Reifengrößen-Auswahl aufheben"):
                if st.session_state.selected_size: st.session_state.selected_size = None; st.rerun()

    # Sidebar-Filter
    with st.sidebar:
        st.header("Detailfilter")
        breite_opt = ["Alle"] + sorted(df["Breite"].unique().tolist())
        hoehe_opt  = ["Alle"] + sorted(df["Hoehe"].unique().tolist())
        fabrikat_opt = ["Alle"] + sorted([x for x in df["Fabrikat"].dropna().unique().tolist()])
        breite_filter   = st.selectbox("Breite (mm)", options=breite_opt, index=0)
        hoehe_filter    = st.selectbox("Höhe (%)", options=hoehe_opt, index=0)
        fabrikat        = st.selectbox("Fabrikat", options=fabrikat_opt, index=0)
        loadindex_opt   = ["Alle"] + sorted([x for x in df["Loadindex"].dropna().astype(str).unique().tolist()])
        speedindex_opt  = ["Alle"] + sorted([x for x in df["Speedindex"].dropna().astype(str).unique().tolist()])
        loadindex_filter  = st.selectbox("Loadindex", options=loadindex_opt, index=0)
        speedindex_filter = st.selectbox("Speedindex", options=speedindex_opt, index=0)
        min_price = float(df["Preis_EUR"].min()); max_price = float(df["Preis_EUR"].max())
        min_preis, max_preis = st.slider("Preisbereich (EUR)", min_value=min_price, max_value=max_price, value=(min_price, max_price), step=5.0)
        sortierung = st.selectbox("Sortieren nach", options=["Preis aufsteigend","Preis absteigend","Fabrikat","Reifengröße","Saison"])
        show_stats = st.checkbox("Statistiken anzeigen", value=False)

    # Komplette Filterung
    filtered = df.copy()
    if mit_bestand: filtered = filtered[(filtered['Bestand'].notna()) & (filtered['Bestand'] > 0)]
    if saison_filter != "Alle": filtered = filtered[filtered['Saison'] == saison_filter]
    if zoll_filter != "Alle": filtered = filtered[filtered["Zoll"] == int(zoll_filter)]

    if st.session_state.selected_size:
        parts = st.session_state.selected_size.split("/")
        b = int(parts[0]); h = int(parts[1].split(" R")[0]); z = int(parts[1].split(" R")[1])
        filtered = filtered[(filtered["Breite"] == b) & (filtered["Hoehe"] == h) & (filtered["Zoll"] == z)]
        st.markdown(f"""<div class="warning-box"><h4>Schnellauswahl aktiv: {st.session_state.selected_size}</h4></div>""", unsafe_allow_html=True)

    if breite_filter != "Alle": filtered = filtered[filtered["Breite"] == int(breite_filter)]
    if hoehe_filter  != "Alle": filtered = filtered[filtered["Hoehe"] == int(hoehe_filter)]
    if fabrikat      != "Alle": filtered = filtered[filtered["Fabrikat"] == fabrikat]
    if loadindex_filter  != "Alle": filtered = filtered[filtered["Loadindex"].astype(str) == str(loadindex_filter)]
    if speedindex_filter != "Alle": filtered = filtered[filtered["Speedindex"].astype(str) == str(speedindex_filter)]
    filtered = filtered[(filtered["Preis_EUR"] >= min_preis) & (filtered["Preis_EUR"] <= max_preis)]

    if sortierung == "Preis aufsteigend":
        filtered = filtered.sort_values("Preis_EUR")
    elif sortierung == "Preis absteigend":
        filtered = filtered.sort_values("Preis_EUR", ascending=False)
    elif sortierung == "Fabrikat":
        filtered = filtered.sort_values(["Fabrikat","Preis_EUR"])
    elif sortierung == "Reifengröße":
        filtered = filtered.sort_values(["Zoll","Breite","Hoehe","Preis_EUR"])
    elif sortierung == "Saison":
        filtered = filtered.sort_values(["Saison","Preis_EUR"])

    # Trefferliste
    if len(filtered) > 0:
        st.markdown("---")
        info = []
        if mit_bestand: info.append("mit Bestand")
        if saison_filter != "Alle": info.append(f"({saison_filter})")
        if zoll_filter != "Alle": info.append(f"{zoll_filter} Zoll")
        header = f"Gefundene Reifen: {len(filtered)}" + (f" {' '.join(info)}" if info else "")
        st.subheader(header)
        render_tire_list(filtered)
        if show_stats: render_statistics(filtered)
    else:
        info = []
        if mit_bestand: info.append("mit Bestand")
        if saison_filter != "Alle": info.append(f"Saison: {saison_filter}")
        if zoll_filter != "Alle": info.append(f"Zoll: {zoll_filter}")
        if info: st.warning(f"Keine Reifen {' und '.join(info)} gefunden. Bitte Filter anpassen.")
        else:    st.warning("Keine Reifen gefunden. Bitte Filter anpassen oder andere Reifengröße wählen.")

    render_legend(mit_bestand, saison_filter, zoll_filter)

if __name__ == "__main__":
    main()
