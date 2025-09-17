import streamlit as st
import pandas as pd
import io
from pathlib import Path
from datetime import datetime
import numpy as np

# Page Config
st.set_page_config(
    page_title="Reifen Verwaltung - Ramsperger",
    page_icon="⚙️",
    layout="wide"
)

# ================================================================================================
# BASISKONFIGURATION - AKTUALISIERT FÜR MULTI-SAISON
# ================================================================================================
BASE_DIR = Path("data")
MASTER_CSV = BASE_DIR / "Ramsperger_Reifen_Master_Database.csv"
EXCEL_VORLAGEN = BASE_DIR / "2025-07-29_ReifenPremium_Winterreifen_2025-26.xlsx"  # Enthält jetzt alle Saisons
SERVICES_CONFIG_CSV = BASE_DIR / "ramsperger_services_config.csv"

# ================================================================================================
# CUSTOM CSS - ERWEITERT FÜR SAISON-ANZEIGE
# ================================================================================================
CUSTOM_CSS = """
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
    
    .workflow-step {
        background: linear-gradient(135deg, #dbeafe, #bfdbfe);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #2563eb;
        font-family: Arial, sans-serif;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stats-container {
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #0ea5e9;
    }
    
    .saison-overview {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid #16a34a;
        box-shadow: var(--shadow-md);
    }
    
    .saison-stats {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .saison-stat {
        text-align: center;
        padding: 1rem;
        border-radius: 8px;
        min-width: 120px;
        box-shadow: var(--shadow-sm);
    }
    
    .saison-stat.winter {
        background: linear-gradient(135deg, #dbeafe, #bfdbfe);
        border: 2px solid #2563eb;
    }
    
    .saison-stat.sommer {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        border: 2px solid #f59e0b;
    }
    
    .saison-stat.ganzjahres {
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        border: 2px solid #10b981;
    }
    
    .saison-stat h4 {
        margin: 0 0 0.5rem 0;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .saison-stat .count {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .filter-info {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #f59e0b;
    }
    
    .database-info {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #16a34a;
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
    
    .error-box {
        background: linear-gradient(135deg, #fef2f2, #fee2e2);
        padding: 1rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--error-color);
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
    }
    
    .duplicate-warning {
        background: linear-gradient(135deg, #fef2f2, #fee2e2);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid var(--error-color);
        margin: 1rem 0;
        box-shadow: var(--shadow-md);
    }
    
    .missing-warning {
        background: linear-gradient(135deg, #fffbeb, #fef3c7);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid var(--warning-color);
        margin: 1rem 0;
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
</style>
"""

# CSS anwenden
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ================================================================================================
# HELPER FUNCTIONS FÜR SAISON
# ================================================================================================
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
        return '<span class="saison-badge saison-winter">❄️ Winter</span>'
    elif saison == "Sommer":
        return '<span class="saison-badge saison-sommer">☀️ Sommer</span>'
    elif saison == "Ganzjahres":
        return '<span class="saison-badge saison-ganzjahres">🌍 Ganzjahres</span>'
    else:
        return '<span class="saison-badge">❓ Unbekannt</span>'

def create_empty_tire_template(teilenummer):
    """Erstellt WIRKLICH LEERE Reifen-Vorlage mit 0-Werten für unbekannte Teilenummern"""
    return {
        'Dimension': f"Unbekannt ({teilenummer})",
        'Fabrikat': '',
        'Profil': '',
        'Teilenummer': teilenummer,
        'Preis_EUR': 0.0,
        'Zoll': 0,  # STARTET BEI 0
        'Breite': 0,  # STARTET BEI 0
        'Hoehe': 0,  # STARTET BEI 0
        'RF': '',
        'Kennzeichen': '',
        'Speedindex': '',  # LEER
        'Loadindex': 0,  # STARTET BEI 0
        'Saison': get_saison_from_teilenummer(teilenummer),
        'Bestand': 0,
        'Kraftstoffeffizienz': '',
        'Nasshaftung': '',
        'Geräuschklasse': 0  # STARTET BEI 0
    }

# ================================================================================================
# SESSION STATE INITIALISIERUNG
# ================================================================================================
def init_session_state():
    """Initialisiert den Session State"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Reifen Verwaltung
    if 'df_original' not in st.session_state:
        st.session_state.df_original = None
    if 'df_filtered' not in st.session_state:
        st.session_state.df_filtered = None
    if 'df_working' not in st.session_state:
        st.session_state.df_working = None
    if 'file_uploaded' not in st.session_state:
        st.session_state.file_uploaded = False
    if 'selected_indices' not in st.session_state:
        st.session_state.selected_indices = []
    if 'filter_applied' not in st.session_state:
        st.session_state.filter_applied = False
    if 'selection_confirmed' not in st.session_state:
        st.session_state.selection_confirmed = False
    if 'current_tire_index' not in st.session_state:
        st.session_state.current_tire_index = 0
    if 'auto_advance' not in st.session_state:
        st.session_state.auto_advance = True
    if 'services_mode' not in st.session_state:
        st.session_state.services_mode = False
    if 'stock_mode' not in st.session_state:
        st.session_state.stock_mode = False

# ================================================================================================
# SERVICE KONFIGURATION
# ================================================================================================
def load_services_config():
    """Lädt oder erstellt die Service-Konfiguration"""
    if not SERVICES_CONFIG_CSV.exists():
        default_services = pd.DataFrame({
            'service_name': ['montage_bis_17', 'montage_18_19', 'montage_ab_20', 'radwechsel_1_rad', 'radwechsel_2_raeder', 'radwechsel_3_raeder', 'radwechsel_4_raeder', 'nur_einlagerung'],
            'service_label': ['Montage bis 17 Zoll', 'Montage 18-19 Zoll', 'Montage ab 20 Zoll', 'Radwechsel 1 Rad', 'Radwechsel 2 Räder', 'Radwechsel 3 Räder', 'Radwechsel 4 Räder', 'Nur Einlagerung'],
            'price': [25.0, 30.0, 40.0, 9.95, 19.95, 29.95, 39.90, 55.00],
            'unit': ['pro Reifen', 'pro Reifen', 'pro Reifen', 'pauschal', 'pauschal', 'pauschal', 'pauschal', 'pauschal']
        })
        SERVICES_CONFIG_CSV.parent.mkdir(parents=True, exist_ok=True)
        default_services.to_csv(SERVICES_CONFIG_CSV, index=False, encoding='utf-8')
        return default_services
    else:
        return pd.read_csv(SERVICES_CONFIG_CSV, encoding='utf-8')

def save_services_config(services_df):
    """Speichert die Service-Konfiguration"""
    try:
        SERVICES_CONFIG_CSV.parent.mkdir(parents=True, exist_ok=True)
        services_df.to_csv(SERVICES_CONFIG_CSV, index=False, encoding='utf-8')
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern der Service-Konfiguration: {e}")
        return False

# ================================================================================================
# DATENBANK FUNKTIONEN (VEREINFACHT - NUR MASTER CSV)
# ================================================================================================
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Bereinigt und normalisiert DataFrame"""
    if df.empty:
        return df
    
    # Preis-Spalte bereinigen
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
    elif "Preis Leasing netto" in df.columns:
        # Excel-Datei hat diese Spalte
        df["Preis_EUR"] = pd.to_numeric(df["Preis Leasing netto"], errors="coerce")

    for c in ["Breite", "Hoehe", "Zoll"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")

    if "Bestand" in df.columns:
        df["Bestand"] = pd.to_numeric(df["Bestand"], errors="coerce")
    else:
        df["Bestand"] = 0

    for c in ["Fabrikat", "Profil", "Kraftstoffeffizienz", "Nasshaftung", 
              "Loadindex", "Speedindex", "Teilenummer"]:
        if c not in df.columns:
            df[c] = pd.NA
    
    # Saison-Spalte hinzufügen wenn nicht vorhanden
    if "Saison" not in df.columns:
        df["Saison"] = df["Teilenummer"].apply(get_saison_from_teilenummer)

    # Nur Zeilen mit gültigen Grunddaten behalten
    df = df.dropna(subset=["Preis_EUR", "Breite", "Hoehe", "Zoll"], how="any")
    if not df.empty:
        df["Breite"] = df["Breite"].astype(int)
        df["Hoehe"] = df["Hoehe"].astype(int)
        df["Zoll"] = df["Zoll"].astype(int)

    return df

@st.cache_data(show_spinner=False, ttl=300)  # Cache für 5 Minuten
def load_master_csv() -> pd.DataFrame:
    """Lädt die Master-CSV"""
    if not MASTER_CSV.exists():
        return pd.DataFrame()

    df = pd.read_csv(MASTER_CSV, encoding='utf-8')
    return clean_dataframe(df)

def save_to_master_csv(df):
    """Speichert DataFrame direkt in die Master-CSV"""
    try:
        MASTER_CSV.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(MASTER_CSV, index=False, encoding='utf-8')
        
        # Cache leeren damit neue Daten geladen werden
        load_master_csv.clear()
        
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern in Master-CSV: {e}")
        return False

def update_master_csv_with_tire(tire_data):
    """Aktualisiert einzelnen Reifen in Master-CSV"""
    try:
        master_df = load_master_csv()
        
        if master_df.empty:
            # Neue CSV erstellen
            new_df = pd.DataFrame([tire_data])
            return save_to_master_csv(new_df)
        else:
            # Prüfen ob Reifen bereits existiert (basierend auf Teilenummer)
            if 'Teilenummer' in tire_data and tire_data['Teilenummer']:
                existing_mask = master_df['Teilenummer'] == tire_data['Teilenummer']
                
                if existing_mask.any():
                    # Bestehenden Reifen aktualisieren
                    for col, value in tire_data.items():
                        if col in master_df.columns:
                            master_df.loc[existing_mask, col] = value
                else:
                    # Neuen Reifen hinzufügen
                    new_row_df = pd.DataFrame([tire_data])
                    master_df = pd.concat([master_df, new_row_df], ignore_index=True)
            else:
                # Neuen Reifen hinzufügen
                new_row_df = pd.DataFrame([tire_data])
                master_df = pd.concat([master_df, new_row_df], ignore_index=True)
            
            return save_to_master_csv(master_df)
    except Exception as e:
        st.error(f"Fehler beim Aktualisieren der Master-CSV: {e}")
        return False

def check_duplicate_in_master(teilenummer):
    """Prüft ob Teilenummer bereits in Master-CSV existiert"""
    if not teilenummer:
        return False
    
    master_df = load_master_csv()
    if master_df.empty or 'Teilenummer' not in master_df.columns:
        return False
    
    return teilenummer in master_df['Teilenummer'].values

# ================================================================================================
# EXCEL DATEN LADEN (VORLAGEN) - OPTIMIERT FÜR GROSSE DATENMENGEN
# ================================================================================================
@st.cache_data(show_spinner=True, ttl=3600)  # Cache für 1 Stunde
def load_excel_vorlagen() -> pd.DataFrame:
    """Lädt die Excel-Vorlagen für neue Reifen - OPTIMIERT für große Datenmengen"""
    if not EXCEL_VORLAGEN.exists():
        st.error(f"Excel-Datei nicht gefunden: {EXCEL_VORLAGEN}")
        return pd.DataFrame()
    
    try:
        with st.spinner(f'Lade Reifen-Datenbank aus Excel...'):
            df = pd.read_excel(EXCEL_VORLAGEN, sheet_name=0)
            
            # Spalten-Namen bereinigen
            df.columns = df.columns.str.replace(r'\r\n', ' ', regex=True).str.strip()
            
            # Dimension zusammenbauen
            df['Dimension'] = (
                df['Breite'].astype(str) + '/' + 
                df['Hoehe'].astype(str) + ' ' + 
                df['R'].astype(str) + df['Zoll'].astype(str) + ' ' + 
                df['Loadindex'].astype(str) + df['Speedindex'].astype(str)
            )
            
            # Runflat-Kennzeichnung
            df['Dimension'] = df.apply(
                lambda row: row['Dimension'] + (' RF' if pd.notna(row['RF']) and row['RF'] != '' else ''), 
                axis=1
            )
            
            # Preis-Spalte finden und umbenennen
            preis_col = None
            for col in df.columns:
                if 'Preis' in col and 'netto' in col.lower():
                    preis_col = col
                    break
            
            if preis_col:
                df['Preis_EUR'] = pd.to_numeric(df[preis_col], errors='coerce')
            else:
                df['Preis_EUR'] = 0.0
            
            # Spalten umbenennen/erstellen
            required_cols = ['Dimension', 'Fabrikat', 'Profil', 'Teilenummer', 'Preis_EUR', 
                            'Zoll', 'Breite', 'Hoehe', 'RF', 'Kennzeichen']
            for col in required_cols:
                if col not in df.columns:
                    df[col] = ''
            
            # Nur relevante Spalten
            df = df[['Dimension', 'Fabrikat', 'Profil', 'Teilenummer', 'Preis_EUR', 'Zoll', 
                    'Breite', 'Hoehe', 'RF', 'Kennzeichen', 'Speedindex', 'Loadindex']]
            df = df.fillna('')
            
            # Saison basierend auf Teilenummer hinzufügen
            df['Saison'] = df['Teilenummer'].apply(get_saison_from_teilenummer)
            
            return df
    except Exception as e:
        st.error(f"Fehler beim Laden der Excel-Datei: {e}")
        return pd.DataFrame()

def get_saison_statistics(df):
    """Berechnet Saison-Statistiken für Dashboard-Anzeige"""
    if df.empty or 'Saison' not in df.columns:
        return {'Winter': 0, 'Sommer': 0, 'Ganzjahres': 0, 'Unbekannt': 0, 'Gesamt': 0}
    
    saison_counts = df['Saison'].value_counts()
    return {
        'Winter': saison_counts.get('Winter', 0),
        'Sommer': saison_counts.get('Sommer', 0),
        'Ganzjahres': saison_counts.get('Ganzjahres', 0),
        'Unbekannt': saison_counts.get('Unbekannt', 0),
        'Gesamt': len(df)
    }

def parse_bulk_teilenummern(teilenummer_input):
    """Robustes Parsing der Bulk-Teilenummern aus Textarea - FIXED VERSION"""
    if not teilenummer_input or not teilenummer_input.strip():
        return []
    
    bulk_teilenummern = []
    
    # Text aufräumen
    text = teilenummer_input.strip()
    
    # Sowohl Zeilen als auch Kommas als Trenner behandeln
    # Erst nach Zeilenumbrüchen splitten
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if line:  # Nur nicht-leere Zeilen verarbeiten
            # Dann nach Kommas splitten
            parts = line.split(',')
            for part in parts:
                part = part.strip()
                if part:  # Nur nicht-leere Teile hinzufügen
                    bulk_teilenummern.append(part)
    
    # Duplikate entfernen aber Reihenfolge beibehalten
    seen = set()
    unique_teilenummern = []
    for tn in bulk_teilenummern:
        if tn not in seen:
            seen.add(tn)
            unique_teilenummern.append(tn)
    
    return unique_teilenummern

def load_excel_with_bulk_teilenummern(bulk_teilenummern_list):
    """Lädt Excel-Vorlagen und ergänzt fehlende Teilenummern als leere Vorlagen"""
    # Excel-Vorlagen laden
    df_excel = load_excel_vorlagen()
    
    if bulk_teilenummern_list:
        # Prüfen welche Teilenummern nicht in Excel sind
        excel_teilenummern = set(df_excel['Teilenummer'].tolist()) if not df_excel.empty else set()
        missing_teilenummern = []
        
        for tn in bulk_teilenummern_list:
            tn_clean = str(tn).strip()
            if tn_clean and tn_clean not in excel_teilenummern:
                missing_teilenummern.append(tn_clean)
        
        # Leere Vorlagen für fehlende Teilenummern erstellen
        if missing_teilenummern:
            missing_templates = []
            for tn in missing_teilenummern:
                template = create_empty_tire_template(tn)
                missing_templates.append(template)
            
            df_missing = pd.DataFrame(missing_templates)
            
            # Excel-Daten und fehlende Vorlagen kombinieren
            if df_excel.empty:
                return df_missing
            else:
                # Spalten angleichen
                all_columns = list(set(df_excel.columns.tolist() + df_missing.columns.tolist()))
                for col in all_columns:
                    if col not in df_excel.columns:
                        df_excel[col] = ''
                    if col not in df_missing.columns:
                        df_missing[col] = ''
                
                # Reihenfolge der Spalten angleichen
                df_missing = df_missing[df_excel.columns]
                
                # Zusammenführen
                combined_df = pd.concat([df_excel, df_missing], ignore_index=True)
                return combined_df
    
    return df_excel

def add_new_columns(df):
    """Fügt EU-Label Spalten hinzu"""
    required_original_cols = ['Dimension', 'Fabrikat', 'Profil', 'Teilenummer', 'Preis_EUR']
    for col in required_original_cols:
        if col not in df.columns:
            df[col] = ''
    
    if 'Bestand' not in df.columns:
        df['Bestand'] = pd.Series([0] * len(df), dtype='float64')
    if 'Kraftstoffeffizienz' not in df.columns:
        df['Kraftstoffeffizienz'] = ''
    if 'Nasshaftung' not in df.columns:
        df['Nasshaftung'] = ''
    if 'Geräuschklasse' not in df.columns:
        df['Geräuschklasse'] = pd.Series([70] * len(df), dtype='float64')
    if 'Saison' not in df.columns:
        df['Saison'] = df['Teilenummer'].apply(get_saison_from_teilenummer)
    
    return df

# ================================================================================================
# FILTER FUNKTIONEN - ERWEITERT FÜR SAISON - FIXED INDEX BUG
# ================================================================================================
def apply_filters(df, hersteller_filter, zoll_filter, preis_range, runflat_filter, 
                 breite_filter, hoehe_filter, teilenummer_search, speed_filter, 
                 saison_filter="alle", stock_filter="alle"):
    """Wendet Sidebar-Filter an - erweitert um Saison - FIXED INDEX BUG"""
    filtered_df = df.copy()
    
    if hersteller_filter and len(hersteller_filter) > 0:
        filtered_df = filtered_df[filtered_df['Fabrikat'].isin(hersteller_filter)]
    
    if zoll_filter and len(zoll_filter) > 0:
        filtered_df = filtered_df[filtered_df['Zoll'].isin(zoll_filter)]
    
    filtered_df = filtered_df[
        (filtered_df['Preis_EUR'] >= preis_range[0]) & 
        (filtered_df['Preis_EUR'] <= preis_range[1])
    ]
    
    if runflat_filter == "Nur Runflat":
        filtered_df = filtered_df[filtered_df['RF'] != '']
    elif runflat_filter == "Ohne Runflat":
        filtered_df = filtered_df[filtered_df['RF'] == '']
    
    if breite_filter and len(breite_filter) > 0:
        filtered_df = filtered_df[filtered_df['Breite'].isin(breite_filter)]
    
    if hoehe_filter and len(hoehe_filter) > 0:
        filtered_df = filtered_df[filtered_df['Hoehe'].isin(hoehe_filter)]
    
    # SAISON-FILTER
    if saison_filter and saison_filter.lower() != "alle":
        filtered_df = filtered_df[filtered_df['Saison'] == saison_filter]
    
    # TEILENUMMER-SUCHE - FIXED INDEX BUG
    if teilenummer_search and teilenummer_search.strip() != "":
        search_terms = [term.strip().upper() for term in teilenummer_search.split(',') if term.strip()]
        
        if search_terms:
            # Index zurücksetzen BEVOR die Mask erstellt wird
            filtered_df = filtered_df.reset_index(drop=True)
            
            # Jetzt ist der Index 0, 1, 2, 3... und die Mask passt
            mask = pd.Series([False] * len(filtered_df))
            
            for search_term in search_terms:
                term_mask = (
                    filtered_df['Teilenummer'].str.upper().str.contains(search_term, na=False, regex=False) |
                    filtered_df['Fabrikat'].str.upper().str.contains(search_term, na=False, regex=False) |
                    filtered_df['Profil'].str.upper().str.contains(search_term, na=False, regex=False)
                )
                mask = mask | term_mask
            
            filtered_df = filtered_df[mask]
    
    if speed_filter and len(speed_filter) > 0:
        filtered_df = filtered_df[filtered_df['Speedindex'].isin(speed_filter)]
    
    return filtered_df

# ================================================================================================
# BESTANDSMANAGEMENT
# ================================================================================================
def get_stock_statistics(df):
    """Berechnet Bestandsstatistiken"""
    stats = {}
    
    if 'Bestand' not in df.columns:
        return {'total': len(df), 'with_stock': 0, 'negative': 0, 'zero': 0, 'positive': 0, 'no_info': len(df)}
    
    stats['total'] = len(df)
    stats['with_stock'] = len(df[df['Bestand'].notna()])
    stats['no_info'] = len(df[df['Bestand'].isna()])
    
    stock_data = df[df['Bestand'].notna()]
    stats['negative'] = len(stock_data[stock_data['Bestand'] < 0])
    stats['zero'] = len(stock_data[stock_data['Bestand'] == 0])
    stats['positive'] = len(stock_data[stock_data['Bestand'] > 0])
    
    stats['total_stock'] = stock_data['Bestand'].sum()
    
    return stats

# ================================================================================================
# EXPORT FUNKTIONEN
# ================================================================================================
def create_github_export():
    """Erstellt GitHub-Export der Master-CSV"""
    try:
        master_df = load_master_csv()
        
        if master_df.empty:
            return None
        
        # CSV erstellen
        csv_buffer = io.StringIO()
        master_df.to_csv(csv_buffer, index=False, encoding='utf-8')
        
        return csv_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Fehler beim Erstellen des GitHub-Exports: {e}")
        return None

# ================================================================================================
# AUTHENTICATION
# ================================================================================================
def check_authentication():
    """Prüft Authentifizierung für Admin-Bereich"""
    if not st.session_state.authenticated:
        st.markdown("""
        <div class="main-header">
            <h1>Reifen Verwaltung</h1>
            <p>Passwort-geschützter Adminbereich</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="warning-box">
            <h4>Authentifizierung erforderlich</h4>
            <p>Dieser Bereich ist nur für autorisierte Benutzer zugänglich.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password = st.text_input("PIN eingeben:", type="password", key="reifen_password")
            
            col_login, col_back = st.columns(2)
            with col_login:
                if st.button("Anmelden", use_container_width=True, type="primary"):
                    if password == "1234":
                        st.session_state.authenticated = True
                        st.success("Zugang gewährt!")
                        st.rerun()
                    else:
                        st.error("Falsches Passwort!")
            
            with col_back:
                if st.button("Zurück", use_container_width=True):
                    st.switch_page("pages/01_Reifen_Suche.py")
        
        return False
    return True

# ================================================================================================
# SERVICE MANAGEMENT
# ================================================================================================
def render_services_management():
    """Service-Preise Verwaltung"""
    st.markdown("#### ⚙️ Service-Preise verwalten")
    st.markdown("Hier können die Preise für Montage, Radwechsel und Einlagerung angepasst werden.")
    
    services_df = load_services_config()
    
    st.markdown("**Aktuelle Service-Preise:**")
    
    current_prices = {}
    for _, row in services_df.iterrows():
        current_prices[row['service_name']] = float(row['price'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Montage-Preise:**")
        
        montage_17 = st.number_input(
            "Montage bis 17 Zoll (€ pro Reifen):",
            min_value=0.0,
            max_value=100.0,
            value=current_prices.get('montage_bis_17', 25.0),
            step=0.10,
            key="service_montage_17"
        )
        
        montage_18 = st.number_input(
            "Montage 18-19 Zoll (€ pro Reifen):",
            min_value=0.0,
            max_value=100.0,
            value=current_prices.get('montage_18_19', 30.0),
            step=0.10,
            key="service_montage_18"
        )
        
        montage_20 = st.number_input(
            "Montage ab 20 Zoll (€ pro Reifen):",
            min_value=0.0,
            max_value=100.0,
            value=current_prices.get('montage_ab_20', 40.0),
            step=0.10,
            key="service_montage_20"
        )
    
    with col2:
        st.markdown("**Radwechsel & Einlagerung:**")
        
        radwechsel_1 = st.number_input(
            "Radwechsel 1 Rad (€):",
            min_value=0.0,
            max_value=50.0,
            value=current_prices.get('radwechsel_1_rad', 9.95),
            step=0.05,
            key="service_radwechsel_1"
        )
        
        radwechsel_2 = st.number_input(
            "Radwechsel 2 Räder (€):",
            min_value=0.0,
            max_value=50.0,
            value=current_prices.get('radwechsel_2_raeder', 19.95),
            step=0.05,
            key="service_radwechsel_2"
        )
        
        radwechsel_3 = st.number_input(
            "Radwechsel 3 Räder (€):",
            min_value=0.0,
            max_value=50.0,
            value=current_prices.get('radwechsel_3_raeder', 29.95),
            step=0.05,
            key="service_radwechsel_3"
        )
        
        radwechsel_4 = st.number_input(
            "Radwechsel 4 Räder (€):",
            min_value=0.0,
            max_value=100.0,
            value=current_prices.get('radwechsel_4_raeder', 39.90),
            step=0.10,
            key="service_radwechsel_4"
        )
        
        einlagerung = st.number_input(
            "Nur Einlagerung (€ pauschal):",
            min_value=0.0,
            max_value=200.0,
            value=current_prices.get('nur_einlagerung', 55.00),
            step=0.10,
            key="service_einlagerung"
        )
    
    if st.button("💾 Preise speichern", use_container_width=True, type="primary"):
        services_df.loc[services_df['service_name'] == 'montage_bis_17', 'price'] = montage_17
        services_df.loc[services_df['service_name'] == 'montage_18_19', 'price'] = montage_18
        services_df.loc[services_df['service_name'] == 'montage_ab_20', 'price'] = montage_20
        services_df.loc[services_df['service_name'] == 'radwechsel_1_rad', 'price'] = radwechsel_1
        services_df.loc[services_df['service_name'] == 'radwechsel_2_raeder', 'price'] = radwechsel_2
        services_df.loc[services_df['service_name'] == 'radwechsel_3_raeder', 'price'] = radwechsel_3
        services_df.loc[services_df['service_name'] == 'radwechsel_4_raeder', 'price'] = radwechsel_4
        services_df.loc[services_df['service_name'] == 'nur_einlagerung', 'price'] = einlagerung
        
        if save_services_config(services_df):
            st.success("Service-Preise erfolgreich aktualisiert!")
            st.rerun()
        else:
            st.error("Fehler beim Speichern der Service-Preise!")
    
    if st.button("🔧 Zur Reifen-Verwaltung", use_container_width=True):
        st.session_state.services_mode = False
        st.rerun()

# ================================================================================================
# STOCK MANAGEMENT
# ================================================================================================
def render_stock_management():
    """Bestandsmanagement & Nachbestellungen"""
    st.markdown("#### 📦 Bestandsmanagement & Nachbestellungen")
    st.markdown("Überblick über Lagerbestände und automatische Nachbestelllisten.")
    
    master_data = load_master_csv()
    
    if master_data.empty:
        st.warning("Keine Daten für Bestandsanalysis verfügbar.")
        return
    
    stats = get_stock_statistics(master_data)
    
    st.markdown("**📊 Bestandsübersicht:**")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Reifen gesamt", stats['total'])
    with col2:
        st.metric("Mit Bestandsinfo", stats['with_stock'])
    with col3:
        if stats['negative'] > 0:
            st.metric("🔴 Nachbestellung", stats['negative'])
        else:
            st.metric("✅ Keine Nachbestellung", stats['negative'])
    with col4:
        st.metric("🟡 Bestand = 0", stats['zero'])
    with col5:
        st.metric("🟢 Verfügbar", stats['positive'])
    
    if stats['total_stock'] < 0:
        st.error(f"⚠️ Gesamtbestand: {stats['total_stock']:.0f} (Negative Bilanz!)")
    else:
        st.success(f"✅ Gesamtbestand: {stats['total_stock']:.0f}")
    
    if st.button("🔧 Zur Reifen-Verwaltung", use_container_width=True):
        st.session_state.services_mode = False
        st.session_state.stock_mode = False
        st.rerun()

# ================================================================================================
# MAIN REIFEN CONTENT - AUTO-LOAD EXCEL + BULK ERGÄNZUNG
# ================================================================================================
def render_reifen_content():
    """Hauptinhalt der Reifen Verwaltung - mit automatischem Excel-Load und Multi-Saison Support"""
    
    # AUTO-LOAD: Excel-Vorlagen automatisch laden wenn noch nicht geladen
    if st.session_state.df_original is None or st.session_state.df_original.empty:
        with st.spinner('Lade Reifen-Datenbank (14.000+ Reifen)...'):
            df_excel = load_excel_vorlagen()
            if not df_excel.empty:
                st.session_state.df_original = df_excel.copy()
                st.session_state.file_uploaded = True
                st.session_state.filter_applied = False
                st.session_state.selection_confirmed = False
                st.success(f"✅ {len(df_excel)} Reifen aus erweiteter Datenbank geladen!")
            else:
                st.error("❌ Excel-Datei konnte nicht geladen werden. Bitte prüfe ob die Datei '2025-07-29_ReifenPremium_Winterreifen_2025-26.xlsx' im data/ Ordner existiert.")
                return
    
    # Sidebar Filter - FIXED REIHENFOLGE
    with st.sidebar:
        st.header("Workflow-Status")
        if not st.session_state.filter_applied:
            st.info("Schritt 1: Filter setzen")
            if st.session_state.df_original is not None:
                st.success(f"{len(st.session_state.df_original)} Reifen geladen")
        elif not st.session_state.selection_confirmed:
            st.info("Schritt 2: Reifen auswählen")
            if st.session_state.df_filtered is not None:
                st.success(f"{len(st.session_state.df_filtered)} Reifen gefiltert")
        else:
            st.success("Schritt 3: Bearbeitung")
            if st.session_state.df_working is not None:
                st.success(f"{len(st.session_state.df_working)} Reifen ausgewählt")
        
        # Filter nur anzeigen wenn passend
        if st.session_state.df_original is not None and not st.session_state.selection_confirmed:
            st.header("🔍 Intelligente Filter")
            
            df_orig = st.session_state.df_original
            
            alle_hersteller = sorted(df_orig['Fabrikat'].unique())
            hersteller_filter = st.multiselect(
                "Hersteller wählen:",
                options=alle_hersteller,
                default=[],
                key="hersteller_filter"
            )
            
            alle_zolle = sorted(df_orig['Zoll'].unique())
            zoll_filter = st.multiselect(
                "Zoll-Größen:",
                options=alle_zolle,
                default=[],
                key="zoll_filter"
            )
            
            # SAISON-FILTER - PROMINENTE PLATZIERUNG
            alle_saisonen = sorted(df_orig['Saison'].unique()) if 'Saison' in df_orig.columns else ['Winter', 'Sommer', 'Ganzjahres']
            saison_filter = st.selectbox(
                "🌦️ Saison-Typ:",
                options=["Alle"] + alle_saisonen,
                index=0,
                key="saison_filter_select",
                help="Filtere nach Winter-, Sommer- oder Ganzjahresreifen"
            )
            
            st.markdown("**Preisfilter:**")
            min_preis_input = st.number_input(
                "Mindestpreis (€):",
                min_value=0.0,
                max_value=10000.0,
                value=0.0,
                step=10.0,
                key="min_preis_input"
            )
            max_preis_input = st.number_input(
                "Höchstpreis (€):",
                min_value=0.0,
                max_value=10000.0,
                value=1000.0,
                step=10.0,
                key="max_preis_input"
            )
            preis_range = (min_preis_input, max_preis_input)
            
            runflat_filter = st.selectbox(
                "Runflat-Reifen:",
                options=["Alle", "Nur Runflat", "Ohne Runflat"],
                key="runflat_filter"
            )
            
            alle_breiten = sorted(df_orig['Breite'].unique())
            breite_filter = st.multiselect(
                "Reifenbreite:",
                options=alle_breiten,
                default=[],
                key="breite_filter"
            )
            
            alle_hoehen = sorted(df_orig['Hoehe'].unique())
            hoehe_filter = st.multiselect(
                "Reifenhöhe:",
                options=alle_hoehen,
                default=[],
                key="hoehe_filter"
            )
            
            # GESCHWINDIGKEITSINDEX
            alle_speed = sorted(df_orig['Speedindex'].unique())
            speed_filter = st.multiselect(
                "Geschwindigkeitsindex:",
                options=alle_speed,
                default=[],
                key="speed_filter"
            )
            
            # ERWEITERTE BULK-TEILENUMMER-EINGABE
            st.markdown("---")
            st.markdown("**📝 Zusätzliche Reifen hinzufügen:**")
            
            teilenummer_search = st.text_area(
                "Teilenummern hinzufügen:",
                placeholder="ZTW12345\nZTS67890\nZTR11111, ZTW22222\n\noder für Suche: Continental, WinterContact",
                help="Eine Teilenummer pro Zeile oder kommagetrennt. Unbekannte Teilenummern werden als leere Vorlagen hinzugefügt.",
                key="teilenummer_search",
                height=100
            )
            
            if st.button("Filter anwenden", use_container_width=True, type="primary"):
                # Parse zusätzliche Teilenummern mit neuer robuster Funktion
                bulk_teilenummern = parse_bulk_teilenummern(teilenummer_search)
                
                # Daten mit zusätzlichen Teilenummern laden
                if bulk_teilenummern:
                    df_with_bulk = load_excel_with_bulk_teilenummern(bulk_teilenummern)
                    working_df = df_with_bulk
                    
                    # Info über hinzugefügte leere Vorlagen
                    excel_count = len(working_df[working_df['Fabrikat'] != '']) if 'Fabrikat' in working_df.columns else 0
                    missing_count = len(working_df) - excel_count
                    
                    if missing_count > 0:
                        st.info(f"📝 {missing_count} unbekannte Teilenummern als leere Vorlagen hinzugefügt!")
                else:
                    working_df = df_orig
                
                # Filter anwenden
                filtered_df = apply_filters(
                    working_df, hersteller_filter, zoll_filter, preis_range, 
                    runflat_filter, breite_filter, hoehe_filter, teilenummer_search, 
                    speed_filter, saison_filter
                )
                
                st.session_state.df_filtered = filtered_df
                st.session_state.filter_applied = True
                st.session_state.selected_indices = []
                st.rerun()
            
            if st.button("Filter zurücksetzen"):
                st.session_state.filter_applied = False
                st.session_state.df_filtered = None
                st.session_state.selected_indices = []
                st.rerun()
    
    # STUFE 1: Automatisch geladen - ERWEITERTE SAISON-ANZEIGE
    if not st.session_state.filter_applied:
        st.markdown("### ✅ Multi-Saison Reifen-Datenbank automatisch geladen")
        st.markdown(f"Aus {len(st.session_state.df_original)} Reifen (Winter, Sommer & Ganzjahres) die gewünschten herausfiltern")
        
        df_orig = st.session_state.df_original
        saison_stats = get_saison_statistics(df_orig)
        
        # Saison-Übersicht mit verbessertem Design
        st.markdown("""
        <div class="saison-overview">
            <h4>🌦️ Saison-Verteilung der Reifen-Datenbank</h4>
            <div class="saison-stats">
                <div class="saison-stat winter">
                    <h4>❄️ Winter</h4>
                    <p class="count">{}</p>
                </div>
                <div class="saison-stat sommer">
                    <h4>☀️ Sommer</h4>
                    <p class="count">{}</p>
                </div>
                <div class="saison-stat ganzjahres">
                    <h4>🌍 Ganzjahres</h4>
                    <p class="count">{}</p>
                </div>
            </div>
        </div>
        """.format(saison_stats['Winter'], saison_stats['Sommer'], saison_stats['Ganzjahres']), unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Gesamt Reifen", saison_stats['Gesamt'])
        with col2:
            st.metric("Hersteller", df_orig['Fabrikat'].nunique())
        with col3:
            st.metric("Zoll-Größen", df_orig['Zoll'].nunique())
        with col4:
            avg_preis = df_orig[df_orig['Preis_EUR'] > 0]['Preis_EUR'].mean()
            st.metric("Durchschnittspreis", f"{avg_preis:.0f} Euro")
        
        st.markdown("""
        <div class="info-box">
            <h4>📋 Nächste Schritte:</h4>
            <p>1. Setze deine <strong>Filter in der Sidebar</strong> (z.B. gewünschte Saison)</p>
            <p>2. Optional: Füge <strong>zusätzliche Teilenummern</strong> hinzu (werden als leere Vorlagen erstellt wenn nicht in der Datenbank)</p>
            <p>3. Klicke <strong>"Filter anwenden"</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # STUFE 2: Reifen-Auswahl - ERWEITERTE SCHNELL-AUSWAHL MIT LÖSCHEN BUTTON (ROTE BUTTONS)
    elif st.session_state.filter_applied and not st.session_state.selection_confirmed:
        st.markdown("### Schritt 2: Gefilterte Reifen auswählen")
        st.markdown(f"Wähle aus den {len(st.session_state.df_filtered)} gefilterten Reifen deine gewünschten aus")
        
        df_filtered = st.session_state.df_filtered
        
        if len(df_filtered) == 0:
            st.warning("Keine Reifen gefunden! Bitte Filter anpassen.")
            if st.button("Zurück zu Schritt 1"):
                st.session_state.filter_applied = False
                st.rerun()
        else:
            # Gefilterte Saison-Statistiken
            filtered_saison_stats = get_saison_statistics(df_filtered)
            if filtered_saison_stats['Gesamt'] > 0:
                st.markdown("**Gefilterte Saison-Verteilung:**")
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                
                with col_s1:
                    if filtered_saison_stats['Winter'] > 0:
                        st.markdown(f"❄️ **Winter:** {filtered_saison_stats['Winter']}")
                with col_s2:
                    if filtered_saison_stats['Sommer'] > 0:
                        st.markdown(f"☀️ **Sommer:** {filtered_saison_stats['Sommer']}")
                with col_s3:
                    if filtered_saison_stats['Ganzjahres'] > 0:
                        st.markdown(f"🌍 **Ganzjahres:** {filtered_saison_stats['Ganzjahres']}")
                with col_s4:
                    if filtered_saison_stats['Unbekannt'] > 0:
                        st.markdown(f"❓ **Unbekannt:** {filtered_saison_stats['Unbekannt']}")
            
            # ERWEITERTE Schnell-Auswahl Buttons - ALLE MIT type="primary" für ROT
            st.markdown("**Schnell-Auswahl:**")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if st.button("Alle auswählen", type="primary"):
                    st.session_state.selected_indices = df_filtered.index.tolist()
                    st.rerun()
            
            with col2:
                if st.button("Alle abwählen", type="primary"):
                    st.session_state.selected_indices = []
                    st.rerun()
            
            with col3:
                if st.button("Nur fehlende Reifen", type="primary"):
                    # Nur Reifen ohne Fabrikat (= aus Bulk-Eingabe)
                    missing_tires = df_filtered[df_filtered['Fabrikat'] == '']
                    st.session_state.selected_indices = missing_tires.index.tolist()
                    st.rerun()
            
            with col4:
                if st.button("Nur Datenbank-Reifen", type="primary"):
                    # Nur Reifen mit Fabrikat (= aus Excel)
                    excel_tires = df_filtered[df_filtered['Fabrikat'] != '']
                    st.session_state.selected_indices = excel_tires.index.tolist()
                    st.rerun()
            
            with col5:
                # NEUER BUTTON: Gewählte Reifen LÖSCHEN (aus Liste entfernen)
                if st.button("Gewählte löschen", type="primary", help="Löscht die ausgewählten Reifen komplett aus der Liste"):
                    if st.session_state.selected_indices:
                        # Ausgewählte Reifen komplett aus df_filtered entfernen
                        remaining_indices = [idx for idx in df_filtered.index if idx not in st.session_state.selected_indices]
                        st.session_state.df_filtered = df_filtered.loc[remaining_indices].reset_index(drop=True)
                        st.session_state.selected_indices = []
                        st.success(f"Ausgewählte Reifen wurden aus der Liste gelöscht!")
                        st.rerun()
            
            # Auswahl-Statistiken
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Gefiltert", len(df_filtered))
            with col2:
                st.metric("Ausgewählt", len(st.session_state.selected_indices))
            with col3:
                if len(st.session_state.selected_indices) > 0:
                    selected_df = df_filtered.loc[st.session_state.selected_indices]
                    avg_preis = selected_df[selected_df['Preis_EUR'] > 0]['Preis_EUR'].mean()
                    st.metric("Durchschnittspreis Auswahl", f"{avg_preis:.0f} Euro" if not pd.isna(avg_preis) else "0 Euro")
            
            # Duplikaten und fehlende Reifen Warnungen
            if len(st.session_state.selected_indices) > 0:
                selected_df = df_filtered.loc[st.session_state.selected_indices]
                
                duplicates = []
                missing_tires = []
                
                for idx in st.session_state.selected_indices:
                    tire = df_filtered.loc[idx]
                    
                    # Prüfung auf Duplikate in Master-CSV
                    if check_duplicate_in_master(tire['Teilenummer']):
                        duplicates.append(tire['Teilenummer'])
                    
                    # Prüfung auf fehlende Excel-Daten
                    if tire['Fabrikat'] == '' or tire['Fabrikat'] is None:
                        missing_tires.append(tire['Teilenummer'])
                
                # Duplikaten-Warnung
                if duplicates:
                    st.markdown(f"""
                    <div class="duplicate-warning">
                        <h4>⚠️ DUPLIKATE GEFUNDEN!</h4>
                        <p>Die folgenden Teilenummern existieren bereits in der Master-Datenbank:</p>
                        <ul>
                    """, unsafe_allow_html=True)
                    for tn in duplicates:
                        st.markdown(f"<li><strong>{tn}</strong></li>", unsafe_allow_html=True)
                    st.markdown("""
                        </ul>
                        <p>Beim Speichern werden diese Reifen <strong>aktualisiert</strong> statt neu hinzugefügt.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Fehlende Reifen Info
                if missing_tires:
                    st.markdown(f"""
                    <div class="missing-warning">
                        <h4>📝 LEERE VORLAGEN GEFUNDEN!</h4>
                        <p>Die folgenden Teilenummern waren nicht in der Datenbank und wurden als leere Vorlagen erstellt:</p>
                        <ul>
                    """, unsafe_allow_html=True)
                    for tn in missing_tires:
                        saison = get_saison_from_teilenummer(tn)
                        badge = get_saison_badge_html(saison)
                        st.markdown(f"<li><strong>{tn}</strong> {badge}</li>", unsafe_allow_html=True)
                    st.markdown("""
                        </ul>
                        <p>Diese Reifen können manuell bearbeitet werden um fehlende Informationen zu ergänzen.</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Reifen-Liste mit Checkboxes - ERWEITERT FÜR SAISON UND MISSING
            st.markdown("**Reifen einzeln auswählen:**")
            
            items_per_page = 50
            total_pages = (len(df_filtered) + items_per_page - 1) // items_per_page
            
            if total_pages > 1:
                page = st.selectbox(f"Seite (je {items_per_page} Reifen):", range(1, total_pages + 1)) - 1
                start_idx = page * items_per_page
                end_idx = min(start_idx + items_per_page, len(df_filtered))
                page_data = df_filtered.iloc[start_idx:end_idx]
            else:
                page_data = df_filtered
            
            for idx, row in page_data.iterrows():
                is_selected = idx in st.session_state.selected_indices
                is_duplicate = check_duplicate_in_master(row['Teilenummer'])
                is_missing = (row['Fabrikat'] == '' or row['Fabrikat'] is None)
                
                col_check, col_info = st.columns([1, 9])
                
                with col_check:
                    if st.checkbox("Auswählen", value=is_selected, key=f"check_{idx}", label_visibility="hidden"):
                        if idx not in st.session_state.selected_indices:
                            st.session_state.selected_indices.append(idx)
                    else:
                        if idx in st.session_state.selected_indices:
                            st.session_state.selected_indices.remove(idx)
                
                with col_info:
                    runflat_info = " **RF**" if row['RF'] != '' else ""
                    duplicate_info = " ⚠️ **DUPLIKAT**" if is_duplicate else ""
                    missing_info = " 📝 **LEERE VORLAGE**" if is_missing else ""
                    saison_badge = get_saison_badge_html(row.get('Saison', 'Unbekannt'))
                    
                    if is_missing:
                        # Leere Vorlage - nur Teilenummer und Saison
                        st.markdown(f"**{row['Dimension']}**{runflat_info} - {row['Teilenummer']} {saison_badge}{duplicate_info}{missing_info}", unsafe_allow_html=True)
                    else:
                        # Vollständiger Reifen
                        st.markdown(f"**{row['Dimension']}**{runflat_info} - {row['Fabrikat']} {row['Profil']} - **{row['Preis_EUR']:.2f}€** - {row['Teilenummer']} {saison_badge}{duplicate_info}", unsafe_allow_html=True)
            
            # Auswahl bestätigen
            if len(st.session_state.selected_indices) > 0:
                if st.button("Auswahl bestätigen & weiter zu Schritt 3", use_container_width=True, type="primary"):
                    st.session_state.df_selected = df_filtered.loc[st.session_state.selected_indices].copy()
                    st.session_state.df_selected = add_new_columns(st.session_state.df_selected)
                    st.session_state.df_working = st.session_state.df_selected.copy()
                    st.session_state.selection_confirmed = True
                    st.rerun()
            else:
                st.warning("Bitte mindestens einen Reifen auswählen!")
            
            if st.button("Zurück zu Filter-Einstellungen"):
                st.session_state.filter_applied = False
                st.rerun()
    
    # STUFE 3: Bearbeitung - ERWEITERT FÜR SAISON MIT 0-WERTEN BEI LEEREN VORLAGEN
    elif st.session_state.selection_confirmed and st.session_state.df_working is not None:
        st.markdown("### Schritt 3: Reifen bearbeiten, EU-Labels hinzufügen & Saison verwalten")
        st.markdown(f"Bearbeite die {len(st.session_state.df_working)} ausgewählten Reifen (alle Saisons)")
        
        # Anzeige-Tabelle
        st.markdown("#### Ausgewählte Reifen")
        
        display_df = st.session_state.df_working.copy()
        
        display_columns = ['Breite', 'Hoehe', 'Zoll', 'Loadindex', 'Speedindex', 'Fabrikat', 
                          'Profil', 'Teilenummer', 'Saison', 'Preis_EUR', 'Bestand', 'Kraftstoffeffizienz', 
                          'Nasshaftung', 'Geräuschklasse']
        available_display_columns = [col for col in display_columns if col in display_df.columns]
        display_df = display_df[available_display_columns]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Einzelnen Reifen bearbeiten
        st.markdown("#### Einzelnen Reifen bearbeiten")
        
        if len(st.session_state.df_working) > 0:
            max_index = len(st.session_state.df_working) - 1
            if st.session_state.current_tire_index > max_index:
                st.session_state.current_tire_index = max_index
            if st.session_state.current_tire_index < 0:
                st.session_state.current_tire_index = 0
            
            # Navigation-Controls
            col_nav1, col_nav2, col_nav3, col_nav4, col_nav5 = st.columns([2, 1, 1, 1, 2])
            
            with col_nav1:
                st.info(f"Reifen {st.session_state.current_tire_index + 1} von {len(st.session_state.df_working)}")
            
            with col_nav2:
                if st.button("< Vorheriger", disabled=(st.session_state.current_tire_index == 0)):
                    st.session_state.current_tire_index -= 1
                    st.rerun()
            
            with col_nav3:
                if st.button("Nächster >", disabled=(st.session_state.current_tire_index >= max_index)):
                    st.session_state.current_tire_index += 1
                    st.rerun()
            
            with col_nav5:
                st.session_state.auto_advance = st.checkbox("Auto-Advance", value=st.session_state.auto_advance, 
                                                          help="Automatisch zum nächsten Reifen nach dem Speichern")
            
            # Reifen-Liste für Dropdown
            reifen_options = []
            df_working_list = list(st.session_state.df_working.iterrows())
            
            for i, (idx, row) in enumerate(df_working_list):
                if row['Fabrikat'] == '':
                    option_text = f"{i+1}: {row['Teilenummer']} (Leere Vorlage - {row['Saison']})"
                else:
                    option_text = f"{i+1}: {row['Dimension']} - {row['Fabrikat']} {row['Profil']} ({row['Preis_EUR']:.2f}€) - {row['Saison']}"
                reifen_options.append((option_text, i))
            
            # Dropdown
            selected_dropdown_index = st.selectbox(
                "Oder Reifen aus Liste auswählen:",
                options=range(len(reifen_options)),
                index=st.session_state.current_tire_index,
                format_func=lambda x: reifen_options[x][0],
                key="reifen_select"
            )
            
            if selected_dropdown_index != st.session_state.current_tire_index:
                st.session_state.current_tire_index = selected_dropdown_index
                st.rerun()
            
            # Aktuellen Reifen holen
            current_position = st.session_state.current_tire_index
            selected_idx, selected_row = df_working_list[current_position]
            
            # Duplikaten-Warnung für aktuellen Reifen
            is_duplicate = check_duplicate_in_master(selected_row['Teilenummer'])
            is_missing_template = (selected_row['Fabrikat'] == '' or selected_row['Fabrikat'] is None)
            
            if is_duplicate:
                st.markdown(f"""
                <div class="duplicate-warning">
                    <h4>⚠️ DUPLIKAT ERKANNT</h4>
                    <p>Teilenummer <strong>{selected_row['Teilenummer']}</strong> existiert bereits in der Master-Datenbank.</p>
                    <p>Beim Speichern wird der bestehende Reifen <strong>aktualisiert</strong>.</p>
                </div>
                """, unsafe_allow_html=True)
            
            if is_missing_template:
                st.markdown(f"""
                <div class="missing-warning">
                    <h4>📝 LEERE VORLAGE</h4>
                    <p>Dieser Reifen <strong>{selected_row['Teilenummer']}</strong> war nicht in der Datenbank.</p>
                    <p>Bitte ergänze die fehlenden Informationen manuell.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Bearbeitungsbereich - ERWEITERT FÜR ALLE FELDER BEI LEEREN VORLAGEN MIT 0-WERTEN
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Reifen Info:**")
                
                if is_missing_template:
                    # Bei leerer Vorlage: alle Grunddaten editierbar - MIT 0-WERTEN
                    new_fabrikat = st.text_input(
                        "Hersteller:",
                        value=str(selected_row['Fabrikat']) if selected_row['Fabrikat'] != '' else '',
                        key=f"fabrikat_{selected_idx}"
                    )
                    
                    new_profil = st.text_input(
                        "Profil:",
                        value=str(selected_row['Profil']) if selected_row['Profil'] != '' else '',
                        key=f"profil_{selected_idx}"
                    )
                    
                    # 0-WERTE für bessere User Experience
                    new_breite = st.number_input(
                        "Breite (mm):",
                        min_value=0,
                        max_value=355,
                        value=int(selected_row['Breite']) if selected_row['Breite'] and pd.notna(selected_row['Breite']) and selected_row['Breite'] != 0 else 0,
                        step=10,
                        key=f"breite_{selected_idx}"
                    )
                    
                    new_hoehe = st.number_input(
                        "Höhe (%):",
                        min_value=0,
                        max_value=85,
                        value=int(selected_row['Hoehe']) if selected_row['Hoehe'] and pd.notna(selected_row['Hoehe']) and selected_row['Hoehe'] != 0 else 0,
                        step=5,
                        key=f"hoehe_{selected_idx}"
                    )
                    
                    new_zoll = st.number_input(
                        "Zoll:",
                        min_value=0,
                        max_value=24,
                        value=int(selected_row['Zoll']) if selected_row['Zoll'] and pd.notna(selected_row['Zoll']) and selected_row['Zoll'] != 0 else 0,
                        step=1,
                        key=f"zoll_{selected_idx}"
                    )
                    
                    new_loadindex = st.number_input(
                        "Loadindex:",
                        min_value=0,
                        max_value=125,
                        value=int(selected_row['Loadindex']) if pd.notna(selected_row['Loadindex']) and selected_row['Loadindex'] != 0 else 0,
                        step=1,
                        key=f"loadindex_{selected_idx}"
                    )
                    
                    speed_options = ['', 'T', 'H', 'V', 'W', 'Y', 'Z', 'ZR']
                    current_speed = selected_row['Speedindex'] if pd.notna(selected_row['Speedindex']) and selected_row['Speedindex'] != '' else ''
                    speed_index = speed_options.index(current_speed) if current_speed in speed_options else 0
                    
                    new_speedindex = st.selectbox(
                        "Speedindex:",
                        options=speed_options,
                        index=speed_index,
                        key=f"speedindex_{selected_idx}"
                    )
                    
                else:
                    # Bei Datenbank-Reifen: nur Info anzeigen
                    st.write(f"**Dimension:** {selected_row['Dimension']}")
                    st.write(f"**Hersteller:** {selected_row['Fabrikat']}")
                    st.write(f"**Profil:** {selected_row['Profil']}")
                    # Standardwerte für nicht-editierbare Felder
                    new_fabrikat = selected_row['Fabrikat']
                    new_profil = selected_row['Profil']
                    new_breite = selected_row['Breite']
                    new_hoehe = selected_row['Hoehe']
                    new_zoll = selected_row['Zoll']
                    new_loadindex = selected_row['Loadindex']
                    new_speedindex = selected_row['Speedindex']
                
                st.write(f"**Teilenummer:** {selected_row['Teilenummer']}")
                
                new_preis = st.number_input(
                    "Preis:",
                    min_value=0.0,
                    max_value=2000.0,
                    value=float(selected_row['Preis_EUR']),
                    step=0.01,
                    key=f"preis_{selected_idx}"
                )
            
            with col2:
                st.markdown("**Saison, EU-Labels & Bestand:**")
                
                # SAISON-DROPDOWN mit automatischer Vorselektion
                saison_options = ['Winter', 'Sommer', 'Ganzjahres', 'Unbekannt']
                current_saison = selected_row.get('Saison', 'Unbekannt')
                saison_index = saison_options.index(current_saison) if current_saison in saison_options else 3
                
                new_saison = st.selectbox(
                    "🌦️ Saison:",
                    options=saison_options,
                    index=saison_index,
                    key=f"saison_{selected_idx}",
                    help="Automatisch basierend auf Teilenummer vorselektiert (ZTW=Winter, ZTS=Sommer, ZTR=Ganzjahres)"
                )
                
                current_bestand = selected_row.get('Bestand', 0)
                if pd.isna(current_bestand) or current_bestand == '':
                    bestand_value = 0
                else:
                    bestand_value = int(current_bestand)
                    
                new_bestand = st.number_input(
                    "Bestand:",
                    min_value=-999,
                    max_value=1000,
                    value=bestand_value,
                    step=1,
                    key=f"bestand_{selected_idx}",
                    help="Negative Werte = Nachbestellung nötig"
                )
                
                current_kraftstoff = selected_row.get('Kraftstoffeffizienz', '')
                kraftstoff_options = ['', 'A', 'B', 'C', 'D', 'E', 'F', 'G']
                kraftstoff_index = kraftstoff_options.index(current_kraftstoff) if current_kraftstoff in kraftstoff_options else 0
                
                new_kraftstoff = st.selectbox(
                    "Kraftstoffeffizienz:",
                    options=kraftstoff_options,
                    index=kraftstoff_index,
                    key=f"kraftstoff_{selected_idx}"
                )
                
                current_nasshaftung = selected_row.get('Nasshaftung', '')
                nasshaftung_index = kraftstoff_options.index(current_nasshaftung) if current_nasshaftung in kraftstoff_options else 0
                
                new_nasshaftung = st.selectbox(
                    "Nasshaftung:",
                    options=kraftstoff_options,
                    index=nasshaftung_index,
                    key=f"nasshaftung_{selected_idx}"
                )
                
                # GERÄUSCHKLASSE MIT 0-WERT BEI LEEREN VORLAGEN
                current_geraeusch = selected_row.get('Geräuschklasse', None)
                if pd.isna(current_geraeusch) or current_geraeusch == '' or current_geraeusch is None or current_geraeusch == 0:
                    geraeusch_value = 0  # Startet bei 0 für leere Vorlagen
                else:
                    geraeusch_value = int(current_geraeusch)
                    
                new_geraeusch = st.number_input(
                    "Geräuschklasse (dB):",
                    min_value=0,
                    max_value=75,
                    value=geraeusch_value,
                    step=1,
                    key=f"geraeusch_{selected_idx}"
                )
            
            # Speichern Button (AUTO-SAVE in Master-CSV)
            col_save, col_remove = st.columns(2)
            
            with col_save:
                if st.button("Änderungen speichern", use_container_width=True, type="primary"):
                    # Reifen-Daten für Master-CSV vorbereiten
                    tire_data = {
                        'Breite': new_breite,
                        'Hoehe': new_hoehe, 
                        'Zoll': new_zoll,
                        'Loadindex': new_loadindex,
                        'Speedindex': new_speedindex,
                        'Fabrikat': new_fabrikat,
                        'Profil': new_profil,
                        'Teilenummer': selected_row['Teilenummer'],
                        'Preis_EUR': new_preis,
                        'Bestand': new_bestand,
                        'Kraftstoffeffizienz': new_kraftstoff,
                        'Nasshaftung': new_nasshaftung,
                        'Geräuschklasse': new_geraeusch if new_geraeusch > 0 else None,
                        'Saison': new_saison
                    }
                    
                    # AUTO-SAVE: Direkt in Master-CSV speichern
                    if update_master_csv_with_tire(tire_data):
                        # Working DataFrame aktualisieren
                        st.session_state.df_working.loc[selected_idx, 'Fabrikat'] = new_fabrikat
                        st.session_state.df_working.loc[selected_idx, 'Profil'] = new_profil
                        st.session_state.df_working.loc[selected_idx, 'Breite'] = new_breite
                        st.session_state.df_working.loc[selected_idx, 'Hoehe'] = new_hoehe
                        st.session_state.df_working.loc[selected_idx, 'Zoll'] = new_zoll
                        st.session_state.df_working.loc[selected_idx, 'Loadindex'] = new_loadindex
                        st.session_state.df_working.loc[selected_idx, 'Speedindex'] = new_speedindex
                        st.session_state.df_working.loc[selected_idx, 'Preis_EUR'] = new_preis
                        st.session_state.df_working.loc[selected_idx, 'Bestand'] = new_bestand
                        st.session_state.df_working.loc[selected_idx, 'Kraftstoffeffizienz'] = new_kraftstoff
                        st.session_state.df_working.loc[selected_idx, 'Nasshaftung'] = new_nasshaftung
                        st.session_state.df_working.loc[selected_idx, 'Geräuschklasse'] = new_geraeusch if new_geraeusch > 0 else None
                        st.session_state.df_working.loc[selected_idx, 'Saison'] = new_saison
                        
                        if st.session_state.auto_advance and st.session_state.current_tire_index < len(st.session_state.df_working) - 1:
                            st.session_state.current_tire_index += 1
                            st.success(f"Reifen erfolgreich in Master-CSV gespeichert! Automatisch zu Reifen {st.session_state.current_tire_index + 1} gewechselt.")
                        else:
                            st.success("Reifen erfolgreich in Master-CSV gespeichert!")
                    else:
                        st.error("Fehler beim Speichern in Master-CSV!")
                    
                    st.rerun()
            
            with col_remove:
                if st.button("Reifen entfernen", use_container_width=True, type="secondary"):
                    st.session_state.df_working = st.session_state.df_working.drop(index=[selected_idx])
                    
                    if selected_idx in st.session_state.selected_indices:
                        st.session_state.selected_indices.remove(selected_idx)
                    
                    if st.session_state.current_tire_index >= len(st.session_state.df_working):
                        st.session_state.current_tire_index = max(0, len(st.session_state.df_working) - 1)
                    
                    st.success(f"Reifen aus Bearbeitung entfernt! Noch {len(st.session_state.df_working)} Reifen in der Liste.")
                    st.rerun()
        else:
            st.warning("Keine Reifen mehr vorhanden!")
        
        # Action Buttons (REDUZIERT)
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("Zurück zur Auswahl", help="Neue Reifen auswählen"):
                st.session_state.selection_confirmed = False
                st.session_state.current_tire_index = 0
                st.rerun()
        
        with col_btn2:
            if st.button("Workflow zurücksetzen", help="Komplett von vorne beginnen"):
                st.session_state.filter_applied = False
                st.session_state.selection_confirmed = False
                st.session_state.df_filtered = None
                st.session_state.df_working = None
                st.session_state.selected_indices = []
                st.session_state.current_tire_index = 0
                st.rerun()
        
        # GitHub Export
        st.markdown("---")
        st.markdown("#### 🔄 Vollständige Datenbank für GitHub Update")
        
        github_data = create_github_export()
        if github_data:
            col_info, col_download = st.columns([2, 1])
            with col_info:
                st.info("Lädt die komplette Master-Datenbank für das GitHub Update herunter.")
            with col_download:
                st.download_button(
                    label="📥 Master-DB herunterladen",
                    data=github_data,
                    file_name="Ramsperger_Reifen_Master_Database.csv",
                    mime="text/csv",
                    help="Master-Datenbank für GitHub Update",
                    use_container_width=True
                )
        else:
            st.warning("Keine Daten für GitHub-Export verfügbar")
        
        st.markdown("---")
        st.info("🔄 **Multi-Saison System:** Die erweiterte Datenbank wird automatisch geladen mit über 14.000 Winter-, Sommer- und Ganzjahresreifen. Zusätzliche Teilenummern können über die Sidebar hinzugefügt werden. Leere Vorlagen für unbekannte Teilenummern werden automatisch erstellt!")

# ================================================================================================
# MAIN TAB RENDER FUNCTION
# ================================================================================================
def render_reifen_tab():
    """Hauptfunktion für Reifen Verwaltung Tab"""
    st.markdown("### Multi-Saison Reifen Verwaltung")
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("---")
        if st.button("← Zurück zur Reifen Suche", use_container_width=True):
            st.switch_page("pages/01_Reifen_Suche.py")
        
        if st.button("🛒 Zum Warenkorb", use_container_width=True, type="primary"):
            st.switch_page("pages/02_Warenkorb.py")
        
        if st.button("🗄️ Datenbank Verwaltung", use_container_width=True, type="secondary"):
            st.switch_page("pages/04_Datenbank_Verwaltung.py")
        
        # Modus-Auswahl
        st.markdown("---")
        st.header("Verwaltungsmodus")
        
        modus_options = ["Reifen Verwaltung", "Service-Preise", "Bestandsmanagement"]
        
        if st.session_state.services_mode:
            current_modus = "Service-Preise"
        elif getattr(st.session_state, 'stock_mode', False):
            current_modus = "Bestandsmanagement"
        else:
            current_modus = "Reifen Verwaltung"
        
        new_modus = st.selectbox(
            "Modus wählen:",
            options=modus_options,
            index=modus_options.index(current_modus),
            key="reifen_modus_select"
        )
        
        if new_modus != current_modus:
            st.session_state.services_mode = (new_modus == "Service-Preise")
            st.session_state.stock_mode = (new_modus == "Bestandsmanagement")
            st.rerun()
    
    # Modus-spezifischer Content
    if st.session_state.services_mode:
        render_services_management()
    elif getattr(st.session_state, 'stock_mode', False):
        render_stock_management()
    else:
        render_reifen_content()

# ================================================================================================
# MAIN FUNCTION
# ================================================================================================
def main():
    init_session_state()
    
    if not check_authentication():
        return
    
    # Header - AKTUALISIERT FÜR MULTI-SAISON
    st.markdown("""
    <div class="main-header">
        <h1>Multi-Saison Reifen Verwaltung</h1>
        <p>Erweiterte Verwaltung für Winter-, Sommer- und Ganzjahresreifen mit über 14.000 Reifen</p>
    </div>
    """, unsafe_allow_html=True)
    
    render_reifen_tab()

if __name__ == "__main__":
    main()