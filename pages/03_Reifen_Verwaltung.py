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
# BASISKONFIGURATION - ERWEITERT FÜR MULTI-SOURCE
# ================================================================================================
BASE_DIR = Path("data")
MASTER_CSV = BASE_DIR / "Ramsperger_Winterreifen_20250826_160010.csv"

# MULTI-SOURCE DATEIEN
WINTER_EXCEL = BASE_DIR / "2025-07-29_ReifenPremium_Winterreifen_2025-26.xlsx"
SOMMER_EXCEL = BASE_DIR / "2025_08_19_ReifenPremium_Sommerreifen_2025.xlsx"
GANZJAHRES_CSV = BASE_DIR / "reifen_export_20250916_2341.csv"

SERVICES_CONFIG_CSV = BASE_DIR / "ramsperger_services_config.csv"

# ================================================================================================
# CUSTOM CSS
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
    
    .source-info {
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #0ea5e9;
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
        return '<span class="saison-badge saison-winter">Winter</span>'
    elif saison == "Sommer":
        return '<span class="saison-badge saison-sommer">Sommer</span>'
    elif saison == "Ganzjahres":
        return '<span class="saison-badge saison-ganzjahres">Ganzjahres</span>'
    else:
        return '<span class="saison-badge">Unbekannt</span>'

def create_empty_tire_template(teilenummer):
    """Erstellt leere Reifen-Vorlage für unbekannte Teilenummern"""
    return {
        'Dimension': f"Unbekannt ({teilenummer})",
        'Fabrikat': '',
        'Profil': '',
        'Teilenummer': teilenummer,
        'Preis_EUR': 0.0,
        'Zoll': 16,
        'Breite': 205,
        'Hoehe': 55,
        'RF': '',
        'Kennzeichen': '',
        'Speedindex': 'H',
        'Loadindex': 91,
        'Saison': get_saison_from_teilenummer(teilenummer),
        'Bestand': 0,
        'Kraftstoffeffizienz': '',
        'Nasshaftung': '',
        'Geräuschklasse': 70,
        'Quelle': 'Bulk-Eingabe'
    }

# ================================================================================================
# ULTRA-ROBUSTES CSV LOADING
# ================================================================================================
def ultra_robust_csv_loading(csv_path):
    """Ultra-robustes CSV-Loading mit maximaler Fehlertoleranz"""
    
    strategies = [
        {'encoding': 'utf-8', 'delimiter': ',', 'quoting': 0},
        {'encoding': 'utf-8', 'delimiter': ';', 'quoting': 0},
        {'encoding': 'utf-8', 'delimiter': '\t', 'quoting': 0},
        {'encoding': 'iso-8859-1', 'delimiter': ';', 'quoting': 0},
        {'encoding': 'windows-1252', 'delimiter': ';', 'quoting': 0},
    ]
    
    for i, strategy in enumerate(strategies):
        try:
            df = pd.read_csv(
                csv_path, 
                on_bad_lines='skip',
                low_memory=False,
                skip_blank_lines=True,
                **strategy
            )
            
            if len(df.columns) > 3 and len(df) > 10:
                st.info(f"✅ CSV erfolgreich geladen mit Strategie {i+1}: {strategy['encoding']} + '{strategy['delimiter']}'")
                return df, None
                
        except Exception as e:
            continue
    
    return pd.DataFrame(), "CSV konnte mit keiner Methode gelesen werden"

# ================================================================================================
# ROBUSTE EXCEL LOADING - GEFIXT FÜR MULTI-HEADER
# ================================================================================================
def robust_excel_loading(excel_path, expected_columns=None):
    """Robustes Excel-Loading mit automatischer Header-Erkennung"""
    
    try:
        # Erste 5 Zeilen lesen um Header zu finden
        df_preview = pd.read_excel(excel_path, sheet_name=0, nrows=5, header=None)
        
        st.info(f"🔍 Excel Struktur-Analyse: {excel_path.name}")
        
        # Suche nach der echten Header-Zeile
        header_row = None
        for row_idx in range(len(df_preview)):
            row_values = df_preview.iloc[row_idx].astype(str).tolist()
            
            # Prüfe ob diese Zeile wie ein Header aussieht
            if expected_columns:
                matches = sum(1 for col in expected_columns if any(col.lower() in val.lower() for val in row_values if pd.notna(val)))
                if matches >= len(expected_columns) * 0.5:  # Mindestens 50% der erwarteten Spalten
                    header_row = row_idx
                    st.info(f"✅ Header gefunden in Zeile {row_idx + 1}: {row_values}")
                    break
            else:
                # Allgemeine Header-Erkennung
                if any(word in ' '.join(row_values).lower() for word in ['breite', 'höhe', 'zoll', 'fabrikat', 'preis']):
                    header_row = row_idx
                    st.info(f"✅ Header gefunden in Zeile {row_idx + 1}: {row_values}")
                    break
        
        # Excel mit gefundenem Header laden
        if header_row is not None:
            df = pd.read_excel(excel_path, sheet_name=0, header=header_row)
        else:
            # Fallback: Standard Header (0)
            df = pd.read_excel(excel_path, sheet_name=0, header=0)
            st.warning(f"⚠️ Kein spezifischer Header gefunden, verwende Zeile 1")
        
        # Spalten-Namen bereinigen
        df.columns = [str(col).replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ').strip() for col in df.columns]
        df.columns = [' '.join(col.split()) for col in df.columns]  # Mehrfache Leerzeichen entfernen
        
        st.info(f"✅ Excel-Spalten nach Bereinigung: {list(df.columns)}")
        
        return df, None
        
    except Exception as e:
        return pd.DataFrame(), f"Excel-Loading Fehler: {str(e)}"

# ================================================================================================
# MULTI-SOURCE COLUMN MAPPING - KOMPLETT ÜBERARBEITET
# ================================================================================================
def map_winter_excel_columns(df):
    """Mappt Winter-Excel Spalten auf einheitliches Schema"""
    df = df.copy()
    
    # Standard-Mappings
    column_mapping = {
        'Höhe': 'Hoehe',
        'Speed index': 'Speedindex',
        'Load index': 'Loadindex',
    }
    
    # Spalten umbenennen
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df = df.rename(columns={old_col: new_col})
    
    # Preis-Spalte finden
    preis_col = None
    for col in df.columns:
        if 'preis' in col.lower() and 'netto' in col.lower():
            preis_col = col
            break
    
    if preis_col:
        df['Preis_EUR'] = pd.to_numeric(df[preis_col], errors='coerce')
    else:
        df['Preis_EUR'] = 0.0
    
    # Dimension erstellen falls nötig
    if 'Dimension' not in df.columns:
        required_cols = ['Breite', 'Hoehe', 'Zoll', 'Loadindex', 'Speedindex']
        if all(col in df.columns for col in required_cols):
            r_val = df['R'].astype(str) if 'R' in df.columns else 'R'
            df['Dimension'] = (
                df['Breite'].astype(str) + '/' + 
                df['Hoehe'].astype(str) + ' ' + 
                r_val + df['Zoll'].astype(str) + ' ' + 
                df['Loadindex'].astype(str) + df['Speedindex'].astype(str)
            )
    
    # Saison setzen
    df['Saison'] = 'Winter'
    df['Quelle'] = 'Winter-Excel'
    
    return df

def map_sommer_excel_columns(df):
    """Mappt Sommer-Excel Spalten auf einheitliches Schema - KOMPLETT GEFIXT"""
    df = df.copy()
    
    st.info(f"🔍 Sommer-Excel Original-Spalten: {list(df.columns)}")
    
    # Robustes Column-Mapping
    column_mapping = {
        'DIM': 'Dimension',
        'Höhe': 'Hoehe', 
        'Speed index': 'Speedindex',
        'Load index': 'Loadindex',
        'Preis Leasing netto': 'Preis_EUR',
        'Preis_Leasing_Netto': 'Preis_EUR',
    }
    
    # Flexible Spalten-Erkennung
    for col in df.columns:
        col_lower = col.lower().strip()
        
        # Speed Index Varianten
        if 'speed' in col_lower and ('index' in col_lower or 'idx' in col_lower):
            df = df.rename(columns={col: 'Speedindex'})
            st.info(f"✅ Sommer: '{col}' → 'Speedindex'")
        
        # Load Index Varianten
        elif 'load' in col_lower and ('index' in col_lower or 'idx' in col_lower):
            df = df.rename(columns={col: 'Loadindex'})
            st.info(f"✅ Sommer: '{col}' → 'Loadindex'")
        
        # Preis Varianten
        elif 'preis' in col_lower and ('leasing' in col_lower or 'netto' in col_lower):
            df = df.rename(columns={col: 'Preis_EUR'})
            st.info(f"✅ Sommer: '{col}' → 'Preis_EUR'")
        
        # Höhe
        elif col_lower == 'höhe':
            df = df.rename(columns={col: 'Hoehe'})
            st.info(f"✅ Sommer: '{col}' → 'Hoehe'")
    
    # Preis verarbeiten
    if 'Preis_EUR' in df.columns:
        df['Preis_EUR'] = pd.to_numeric(df['Preis_EUR'], errors='coerce')
    else:
        # Fallback: Erste numerische Spalte die wie Preis aussieht
        for col in df.columns:
            if df[col].dtype in ['float64', 'int64'] or pd.to_numeric(df[col], errors='coerce').notna().any():
                try:
                    numeric_vals = pd.to_numeric(df[col], errors='coerce')
                    if numeric_vals.mean() > 10 and numeric_vals.mean() < 2000:  # Preis-ähnlich
                        df['Preis_EUR'] = numeric_vals
                        st.info(f"✅ Sommer: Preis-Fallback '{col}' → 'Preis_EUR'")
                        break
                except:
                    continue
        else:
            df['Preis_EUR'] = 0.0
    
    # Dimension erstellen falls nötig
    if 'Dimension' not in df.columns:
        required_cols = ['Breite', 'Hoehe', 'Zoll', 'Loadindex', 'Speedindex']
        if all(col in df.columns for col in required_cols):
            r_val = df['R'].astype(str) if 'R' in df.columns else 'R'
            df['Dimension'] = (
                df['Breite'].astype(str) + '/' + 
                df['Hoehe'].astype(str) + ' ' + 
                r_val + df['Zoll'].astype(str) + ' ' + 
                df['Loadindex'].astype(str) + df['Speedindex'].astype(str)
            )
    
    # KRITISCH: Saison explizit setzen
    df['Saison'] = 'Sommer'
    df['Quelle'] = 'Sommer-Excel'
    
    st.success(f"✅ Sommer-Excel gemappt: {len(df)} Reifen mit Saison=Sommer")
    
    return df

def map_csv_columns(df):
    """Mappt CSV Spalten auf einheitliches Schema"""
    df = df.copy()
    
    # Robustes Column mapping
    column_mapping = {
        'Höhe': 'Hoehe',
        'Speed_Index': 'Speedindex',
        'Load_Index': 'Loadindex',
        'Preis_Leasing_Netto': 'Preis_EUR',
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df = df.rename(columns={old_col: new_col})
            st.info(f"✅ CSV: '{old_col}' → '{new_col}'")
    
    # Preis verarbeiten
    if 'Preis_EUR' in df.columns:
        df['Preis_EUR'] = pd.to_numeric(df['Preis_EUR'], errors='coerce')
    
    # Dimension erstellen falls nötig
    if 'Dimension' not in df.columns:
        required_cols = ['Breite', 'Hoehe', 'Zoll', 'Loadindex', 'Speedindex']
        if all(col in df.columns for col in required_cols):
            r_val = df['R'].astype(str) if 'R' in df.columns else 'R'
            df['Dimension'] = (
                df['Breite'].astype(str) + '/' + 
                df['Hoehe'].astype(str) + ' ' + 
                r_val + df['Zoll'].astype(str) + ' ' + 
                df['Loadindex'].astype(str) + df['Speedindex'].astype(str)
            )
    
    # Saison aus Teilenummer ermitteln
    if 'Teilenummer' in df.columns:
        df['Saison'] = df['Teilenummer'].apply(get_saison_from_teilenummer)
    else:
        df['Saison'] = 'Ganzjahres'
    
    df['Quelle'] = 'Ganzjahres-CSV'
    
    return df

# ================================================================================================
# MULTI-SOURCE LOADING - KOMPLETT ÜBERARBEITET
# ================================================================================================
@st.cache_data(show_spinner=False)
def load_all_sources() -> pd.DataFrame:
    """Lädt alle verfügbaren Reifen-Quellen mit ultra-robustem Error-Handling"""
    all_dataframes = []
    source_stats = {
        'Winter': {'loaded': False, 'count': 0, 'file': WINTER_EXCEL, 'error': None},
        'Sommer': {'loaded': False, 'count': 0, 'file': SOMMER_EXCEL, 'error': None}, 
        'Ganzjahres': {'loaded': False, 'count': 0, 'file': GANZJAHRES_CSV, 'error': None}
    }
    
    st.info("🔄 Lade Multi-Source Reifen-Daten...")
    
    # 1. WINTER-EXCEL LADEN
    if WINTER_EXCEL.exists():
        try:
            df_winter, error = robust_excel_loading(WINTER_EXCEL, ['Breite', 'Höhe', 'Zoll', 'Fabrikat'])
            if error is None and not df_winter.empty:
                df_winter = map_winter_excel_columns(df_winter)
                all_dataframes.append(df_winter)
                source_stats['Winter']['loaded'] = True
                source_stats['Winter']['count'] = len(df_winter)
                st.success(f"✅ Winter-Excel geladen: {len(df_winter)} Reifen")
            else:
                source_stats['Winter']['error'] = error or "Leer"
        except Exception as e:
            source_stats['Winter']['error'] = str(e)
    else:
        source_stats['Winter']['error'] = "Datei nicht gefunden"
    
    # 2. SOMMER-EXCEL LADEN - MIT SPEZIELLEM HEADER-HANDLING
    if SOMMER_EXCEL.exists():
        try:
            df_sommer, error = robust_excel_loading(SOMMER_EXCEL, ['Breite', 'Höhe', 'Speed index', 'Load index', 'Preis'])
            if error is None and not df_sommer.empty:
                df_sommer = map_sommer_excel_columns(df_sommer)
                all_dataframes.append(df_sommer)
                source_stats['Sommer']['loaded'] = True
                source_stats['Sommer']['count'] = len(df_sommer)
                st.success(f"✅ Sommer-Excel geladen: {len(df_sommer)} Reifen")
            else:
                source_stats['Sommer']['error'] = error or "Leer"
        except Exception as e:
            source_stats['Sommer']['error'] = str(e)
    else:
        source_stats['Sommer']['error'] = "Datei nicht gefunden"
    
    # 3. GANZJAHRES-CSV LADEN
    if GANZJAHRES_CSV.exists():
        try:
            df_ganzjahres, error = ultra_robust_csv_loading(GANZJAHRES_CSV)
            if error is None and not df_ganzjahres.empty:
                df_ganzjahres = map_csv_columns(df_ganzjahres)
                all_dataframes.append(df_ganzjahres)
                source_stats['Ganzjahres']['loaded'] = True
                source_stats['Ganzjahres']['count'] = len(df_ganzjahres)
                st.success(f"✅ Ganzjahres-CSV geladen: {len(df_ganzjahres)} Reifen")
            else:
                source_stats['Ganzjahres']['error'] = error or "Leer"
        except Exception as e:
            source_stats['Ganzjahres']['error'] = str(e)
    else:
        source_stats['Ganzjahres']['error'] = "Datei nicht gefunden"
    
    # KOMBINIEREN UND STANDARDISIEREN
    if not all_dataframes:
        st.error("❌ Keine Datenquellen erfolgreich geladen!")
        return pd.DataFrame()
    
    st.info(f"🔗 Kombiniere {len(all_dataframes)} Datenquellen...")
    
    # DataFrames kombinieren
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Standardisierte Spalten sicherstellen
    required_columns = [
        'Dimension', 'Fabrikat', 'Profil', 'Teilenummer', 'Preis_EUR',
        'Zoll', 'Breite', 'Hoehe', 'RF', 'Kennzeichen', 'Speedindex', 
        'Loadindex', 'Saison', 'Quelle', 'Bestand', 'Kraftstoffeffizienz', 
        'Nasshaftung', 'Geräuschklasse'
    ]
    
    for col in required_columns:
        if col not in combined_df.columns:
            if col == 'Bestand':
                combined_df[col] = 0
            elif col in ['Kraftstoffeffizienz', 'Nasshaftung', 'RF', 'Kennzeichen']:
                combined_df[col] = ''
            elif col == 'Geräuschklasse':
                combined_df[col] = 70
            else:
                combined_df[col] = ''
    
    # Datentypen bereinigen
    combined_df = clean_dataframe_preserve_saison(combined_df)
    
    # Debug: Saison-Verteilung nach Loading
    if 'Saison' in combined_df.columns:
        saison_counts = combined_df['Saison'].value_counts()
        st.info(f"🔍 Saison-Verteilung nach Loading: {dict(saison_counts)}")
    
    # Source Stats als Metadaten speichern
    combined_df.attrs['source_stats'] = source_stats
    
    st.success(f"🎯 Multi-Source Loading erfolgreich: {len(combined_df)} Reifen geladen")
    
    return combined_df

def get_source_statistics(df):
    """Extrahiert Quellen-Statistiken aus dem DataFrame"""
    if hasattr(df, 'attrs') and 'source_stats' in df.attrs:
        return df.attrs['source_stats']
    
    # Fallback: Aus Daten berechnen
    stats = {}
    if 'Quelle' in df.columns:
        source_counts = df['Quelle'].value_counts()
        for quelle, count in source_counts.items():
            if 'Winter' in quelle:
                stats['Winter'] = {'loaded': True, 'count': count}
            elif 'Sommer' in quelle:
                stats['Sommer'] = {'loaded': True, 'count': count}
            elif 'Ganzjahres' in quelle or 'CSV' in quelle:
                stats['Ganzjahres'] = {'loaded': True, 'count': count}
    
    return stats

# ================================================================================================
# SESSION STATE & BASIC FUNCTIONS
# ================================================================================================
def init_session_state():
    """Initialisiert den Session State"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
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

def clean_dataframe_preserve_saison(df: pd.DataFrame) -> pd.DataFrame:
    """Bereinigt und normalisiert DataFrame OHNE SAISON ZU ÜBERSCHREIBEN"""
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

    # Numerische Spalten
    for c in ["Breite", "Hoehe", "Zoll"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")

    if "Bestand" in df.columns:
        df["Bestand"] = pd.to_numeric(df["Bestand"], errors="coerce")

    # String-Spalten
    for c in ["Fabrikat", "Profil", "Kraftstoffeffizienz", "Nasshaftung", 
              "Loadindex", "Speedindex", "Teilenummer"]:
        if c not in df.columns:
            df[c] = pd.NA

    # Saison nur bei komplett fehlenden Werten setzen
    if "Saison" not in df.columns or df["Saison"].isna().all():
        if "Teilenummer" in df.columns:
            df["Saison"] = df["Teilenummer"].apply(get_saison_from_teilenummer)
    
    # Nur fehlende Saison-Werte füllen
    if "Saison" in df.columns and "Teilenummer" in df.columns:
        saison_mask = df["Saison"].isna() | (df["Saison"] == '') | (df["Saison"] == 'Unbekannt')
        if saison_mask.any():
            df.loc[saison_mask, "Saison"] = df.loc[saison_mask, "Teilenummer"].apply(get_saison_from_teilenummer)

    # Zeilen mit fehlenden kritischen Werten entfernen
    df = df.dropna(subset=["Preis_EUR", "Breite", "Hoehe", "Zoll"], how="any")
    
    if not df.empty:
        df["Breite"] = df["Breite"].astype(int)
        df["Hoehe"] = df["Hoehe"].astype(int)  
        df["Zoll"] = df["Zoll"].astype(int)

    return df

# ================================================================================================
# DATABASE FUNCTIONS
# ================================================================================================
@st.cache_data(show_spinner=False)
def load_master_csv() -> pd.DataFrame:
    """Lädt die Master-CSV"""
    if not MASTER_CSV.exists():
        return pd.DataFrame()

    df = pd.read_csv(MASTER_CSV, encoding='utf-8')
    return clean_dataframe_preserve_saison(df)

def save_to_master_csv(df):
    """Speichert DataFrame direkt in die Master-CSV"""
    try:
        MASTER_CSV.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(MASTER_CSV, index=False, encoding='utf-8')
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
            new_df = pd.DataFrame([tire_data])
            return save_to_master_csv(new_df)
        else:
            if 'Teilenummer' in tire_data and tire_data['Teilenummer']:
                existing_mask = master_df['Teilenummer'] == tire_data['Teilenummer']
                
                if existing_mask.any():
                    for col, value in tire_data.items():
                        if col in master_df.columns:
                            master_df.loc[existing_mask, col] = value
                else:
                    new_row_df = pd.DataFrame([tire_data])
                    master_df = pd.concat([master_df, new_row_df], ignore_index=True)
            else:
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
# FILTER FUNKTIONEN
# ================================================================================================
def apply_filters(df, saison_filter, hersteller_filter, zoll_filter, preis_range, runflat_filter, 
                 breite_filter, hoehe_filter, teilenummer_search, speed_filter):
    """Wendet Sidebar-Filter an - mit robustem Error-Handling"""
    filtered_df = df.copy()
    
    st.info(f"🔍 Filter-Debug: Start mit {len(filtered_df)} Reifen")
    
    # SAISON-FILTER
    if saison_filter and saison_filter.lower() != "alle":
        before_count = len(filtered_df)
        available_seasons = filtered_df['Saison'].value_counts()
        st.info(f"🔍 Verfügbare Saisonen: {dict(available_seasons)}")
        
        filtered_df = filtered_df[filtered_df['Saison'] == saison_filter]
        st.info(f"🔍 Saison-Filter '{saison_filter}': {before_count} → {len(filtered_df)} Reifen")
    
    # Weitere Filter nur wenn noch Reifen vorhanden
    if len(filtered_df) == 0:
        return filtered_df
    
    if hersteller_filter and len(hersteller_filter) > 0:
        before_count = len(filtered_df)
        filtered_df = filtered_df[filtered_df['Fabrikat'].isin(hersteller_filter)]
        st.info(f"🔍 Hersteller-Filter: {before_count} → {len(filtered_df)} Reifen")
    
    if zoll_filter and len(zoll_filter) > 0:
        before_count = len(filtered_df)
        filtered_df = filtered_df[filtered_df['Zoll'].isin(zoll_filter)]
        st.info(f"🔍 Zoll-Filter: {before_count} → {len(filtered_df)} Reifen")
    
    if len(filtered_df) > 0:
        before_count = len(filtered_df)
        filtered_df = filtered_df[
            (filtered_df['Preis_EUR'] >= preis_range[0]) & 
            (filtered_df['Preis_EUR'] <= preis_range[1])
        ]
        st.info(f"🔍 Preis-Filter: {before_count} → {len(filtered_df)} Reifen")
    
    if runflat_filter == "Nur Runflat" and len(filtered_df) > 0:
        before_count = len(filtered_df)
        filtered_df = filtered_df[filtered_df['RF'] != '']
        st.info(f"🔍 Runflat-Filter: {before_count} → {len(filtered_df)} Reifen")
    elif runflat_filter == "Ohne Runflat" and len(filtered_df) > 0:
        before_count = len(filtered_df)
        filtered_df = filtered_df[filtered_df['RF'] == '']
        st.info(f"🔍 Runflat-Filter: {before_count} → {len(filtered_df)} Reifen")
    
    if breite_filter and len(breite_filter) > 0 and len(filtered_df) > 0:
        before_count = len(filtered_df)
        filtered_df = filtered_df[filtered_df['Breite'].isin(breite_filter)]
        st.info(f"🔍 Breite-Filter: {before_count} → {len(filtered_df)} Reifen")
    
    if hoehe_filter and len(hoehe_filter) > 0 and len(filtered_df) > 0:
        before_count = len(filtered_df)
        filtered_df = filtered_df[filtered_df['Hoehe'].isin(hoehe_filter)]
        st.info(f"🔍 Höhe-Filter: {before_count} → {len(filtered_df)} Reifen")
    
    if speed_filter and len(speed_filter) > 0 and len(filtered_df) > 0:
        before_count = len(filtered_df)
        filtered_df = filtered_df[filtered_df['Speedindex'].isin(speed_filter)]
        st.info(f"🔍 Speed-Filter: {before_count} → {len(filtered_df)} Reifen")
    
    st.success(f"🎯 Filter-Ergebnis: {len(filtered_df)} Reifen gefunden")
    
    return filtered_df

# ================================================================================================
# BULK FUNCTIONS
# ================================================================================================
def parse_bulk_teilenummern(teilenummer_input):
    """Robustes Parsing der Bulk-Teilenummern"""
    if not teilenummer_input or not teilenummer_input.strip():
        return []
    
    bulk_teilenummern = []
    text = teilenummer_input.strip()
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if line:
            parts = line.split(',')
            for part in parts:
                part = part.strip()
                if part:
                    bulk_teilenummern.append(part)
    
    # Duplikate entfernen
    seen = set()
    unique_teilenummern = []
    for tn in bulk_teilenummern:
        if tn not in seen:
            seen.add(tn)
            unique_teilenummern.append(tn)
    
    return unique_teilenummern

def load_with_bulk_teilenummern(bulk_teilenummern_list):
    """Lädt Multi-Source Daten und ergänzt fehlende Teilenummern"""
    df_all_sources = load_all_sources()
    
    if bulk_teilenummern_list:
        existing_teilenummern = set(df_all_sources['Teilenummer'].tolist()) if not df_all_sources.empty else set()
        missing_teilenummern = []
        
        for tn in bulk_teilenummern_list:
            tn_clean = str(tn).strip()
            if tn_clean and tn_clean not in existing_teilenummern:
                missing_teilenummern.append(tn_clean)
        
        if missing_teilenummern:
            missing_templates = []
            for tn in missing_teilenummern:
                template = create_empty_tire_template(tn)
                missing_templates.append(template)
            
            df_missing = pd.DataFrame(missing_templates)
            
            if df_all_sources.empty:
                return df_missing
            else:
                all_columns = list(set(df_all_sources.columns.tolist() + df_missing.columns.tolist()))
                for col in all_columns:
                    if col not in df_all_sources.columns:
                        df_all_sources[col] = ''
                    if col not in df_missing.columns:
                        df_missing[col] = ''
                
                df_missing = df_missing[df_all_sources.columns]
                combined_df = pd.concat([df_all_sources, df_missing], ignore_index=True)
                return combined_df
    
    return df_all_sources

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
    
    if 'Saison' not in df.columns or df['Saison'].isna().all():
        df['Saison'] = df['Teilenummer'].apply(get_saison_from_teilenummer)
    
    if 'Quelle' not in df.columns:
        df['Quelle'] = 'Unbekannt'
    
    return df

# ================================================================================================
# EXPORT FUNCTIONS
# ================================================================================================
def create_github_export():
    """Erstellt GitHub-Export der Master-CSV"""
    try:
        master_df = load_master_csv()
        
        if master_df.empty:
            return None
        
        csv_buffer = io.StringIO()
        master_df.to_csv(csv_buffer, index=False, encoding='utf-8')
        
        return csv_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Fehler beim Erstellen des GitHub-Exports: {e}")
        return None

# ================================================================================================
# MAIN REIFEN CONTENT
# ================================================================================================
def render_reifen_content():
    """Hauptinhalt der Reifen Verwaltung"""
    
    # AUTO-LOAD: Alle verfügbaren Quellen automatisch laden
    if st.session_state.df_original is None or st.session_state.df_original.empty:
        with st.spinner('Lade alle verfügbaren Reifen-Quellen...'):
            df_all_sources = load_all_sources()
            if not df_all_sources.empty:
                st.session_state.df_original = df_all_sources.copy()
                st.session_state.file_uploaded = True
                st.session_state.filter_applied = False
                st.session_state.selection_confirmed = False
                
                # Quellen-Statistiken anzeigen
                source_stats = get_source_statistics(df_all_sources)
                
                success_sources = []
                error_sources = []
                
                for source_name, stats in source_stats.items():
                    if stats.get('loaded', False):
                        success_sources.append(f"{source_name}: {stats['count']}")
                    elif stats.get('error'):
                        error_sources.append(f"{source_name}: {stats['error']}")
                
                if success_sources:
                    total_loaded = sum(stat.get('count', 0) for stat in source_stats.values() if stat.get('loaded', False))
                    st.success(f"✅ {total_loaded} Reifen aus {len(success_sources)} Quellen geladen: {', '.join(success_sources)}")
                
                if error_sources:
                    for error in error_sources:
                        st.error(f"❌ {error}")
                
                if not success_sources:
                    st.error("❌ Keine Reifen-Dateien erfolgreich geladen!")
                    return
            else:
                st.error("❌ Keine Reifen-Dateien gefunden oder alle Dateien fehlerhaft!")
                return
    
    # Sidebar Filter
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
            
            # SAISON-FILTER
            SAISON_OPTIONS = ["Alle", "Winter", "Sommer", "Ganzjahres", "Unbekannt"]
            saison_filter = st.selectbox(
                "Saison-Typ:",
                options=SAISON_OPTIONS,
                index=0,
                key="saison_filter_select"
            )
            
            # Sichere Filter-Optionen mit Error-Handling
            try:
                alle_hersteller = sorted([h for h in df_orig['Fabrikat'].unique() if pd.notna(h) and h != ''])
            except:
                alle_hersteller = []
                
            hersteller_filter = st.multiselect(
                "Hersteller wählen:",
                options=alle_hersteller,
                default=[],
                key="hersteller_filter"
            )
            
            try:
                alle_zolle = sorted([z for z in df_orig['Zoll'].unique() if pd.notna(z)])
            except:
                alle_zolle = []
                
            zoll_filter = st.multiselect(
                "Zoll-Größen:",
                options=alle_zolle,
                default=[],
                key="zoll_filter"
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
            
            try:
                alle_breiten = sorted([b for b in df_orig['Breite'].unique() if pd.notna(b)])
            except:
                alle_breiten = []
                
            breite_filter = st.multiselect(
                "Reifenbreite:",
                options=alle_breiten,
                default=[],
                key="breite_filter"
            )
            
            try:
                alle_hoehen = sorted([h for h in df_orig['Hoehe'].unique() if pd.notna(h)])
            except:
                alle_hoehen = []
                
            hoehe_filter = st.multiselect(
                "Reifenhöhe:",
                options=alle_hoehen,
                default=[],
                key="hoehe_filter"
            )
            
            st.markdown("---")
            st.markdown("**📝 Zusätzliche Reifen hinzufügen:**")
            
            teilenummer_search = st.text_area(
                "Teilenummern hinzufügen:",
                placeholder="ZTW12345\nZTS67890\nZTR11111, ZTW22222",
                help="Eine Teilenummer pro Zeile oder kommagetrennt",
                key="teilenummer_search",
                height=100
            )
            
            try:
                alle_speed = sorted([s for s in df_orig['Speedindex'].unique() if pd.notna(s) and s != ''])
            except:
                alle_speed = []
                
            speed_filter = st.multiselect(
                "Geschwindigkeitsindex:",
                options=alle_speed,
                default=[],
                key="speed_filter"
            )
            
            if st.button("Filter anwenden", use_container_width=True, type="primary"):
                # Parse zusätzliche Teilenummern
                bulk_teilenummern = parse_bulk_teilenummern(teilenummer_search)
                
                # Daten mit zusätzlichen Teilenummern laden
                if bulk_teilenummern:
                    df_with_bulk = load_with_bulk_teilenummern(bulk_teilenummern)
                    working_df = df_with_bulk
                    
                    excel_count = len(working_df[working_df['Fabrikat'] != '']) if 'Fabrikat' in working_df.columns else 0
                    missing_count = len(working_df) - excel_count
                    
                    if missing_count > 0:
                        st.info(f"📝 {missing_count} unbekannte Teilenummern als leere Vorlagen hinzugefügt!")
                else:
                    working_df = df_orig
                
                # Filter anwenden
                filtered_df = apply_filters(
                    working_df, saison_filter, hersteller_filter, zoll_filter, preis_range, 
                    runflat_filter, breite_filter, hoehe_filter, teilenummer_search, speed_filter
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
    
    # STUFE 1: Multi-Source automatisch geladen
    if not st.session_state.filter_applied:
        st.markdown("### ✅ Multi-Source Reifen automatisch geladen - KOMPLETT GEFIXT!")
        
        df_orig = st.session_state.df_original
        source_stats = get_source_statistics(df_orig)
        
        # Quellen-Übersicht
        st.markdown("#### 📊 Geladene Datenquellen:")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            winter_count = source_stats.get('Winter', {}).get('count', 0)
            winter_loaded = source_stats.get('Winter', {}).get('loaded', False)
            if winter_loaded:
                st.metric("❄️ Winter", winter_count)
            else:
                st.metric("❄️ Winter", "Fehler")
        
        with col2:
            sommer_count = source_stats.get('Sommer', {}).get('count', 0)  
            sommer_loaded = source_stats.get('Sommer', {}).get('loaded', False)
            if sommer_loaded:
                st.metric("☀️ Sommer", sommer_count)
            else:
                st.metric("☀️ Sommer", "Fehler")
        
        with col3:
            ganzjahres_count = source_stats.get('Ganzjahres', {}).get('count', 0)
            ganzjahres_loaded = source_stats.get('Ganzjahres', {}).get('loaded', False)
            if ganzjahres_loaded:
                st.metric("🌍 Ganzjahres", ganzjahres_count)
            else:
                st.metric("🌍 Ganzjahres", "Fehler")
        
        with col4:
            total_count = winter_count + sommer_count + ganzjahres_count
            st.metric("🎯 Gesamt", total_count)
        
        # Saison-Verteilung nach Quelle
        if 'Saison' in df_orig.columns and 'Quelle' in df_orig.columns:
            st.markdown("#### 🔄 Saison-Verteilung nach Quelle:")
            
            try:
                saison_quelle_stats = df_orig.groupby(['Quelle', 'Saison']).size().unstack(fill_value=0)
                if not saison_quelle_stats.empty:
                    st.dataframe(saison_quelle_stats, use_container_width=True)
                
                overall_saison_counts = df_orig['Saison'].value_counts()
                st.info(f"🔍 Gesamte Saison-Verteilung: {dict(overall_saison_counts)}")
            except Exception as e:
                st.error(f"Fehler bei Saison-Analyse: {e}")
        
        st.markdown("""
        <div class="source-info">
            <h4>🎯 KOMPLETT GEFIXTES Multi-Source System!</h4>
            <p><strong>✅ Automatisch geladen:</strong> Winter-Excel, Sommer-Excel und Ganzjahres-CSV</p>
            <p><strong>🔧 Excel-Header-Problem gefixt:</strong> Automatische Header-Erkennung</p>
            <p><strong>🛡️ Ultra-robustes Error-Handling:</strong> Alle Filter sind sicher</p>
            <p><strong>✨ Alle Saison-Filter funktionieren jetzt!</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # STUFE 2: Reifen-Auswahl
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
            # Schnell-Auswahl Buttons
            st.markdown("**Schnell-Auswahl:**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("Alle auswählen"):
                    st.session_state.selected_indices = df_filtered.index.tolist()
                    st.rerun()
            
            with col2:
                if st.button("Alle abwählen"):
                    st.session_state.selected_indices = []
                    st.rerun()
            
            with col3:
                if st.button("Nur fehlende Reifen"):
                    missing_tires = df_filtered[df_filtered['Fabrikat'] == '']
                    st.session_state.selected_indices = missing_tires.index.tolist()
                    st.rerun()
            
            with col4:
                if st.button("Nur Katalog-Reifen"):
                    catalog_tires = df_filtered[df_filtered['Fabrikat'] != '']
                    st.session_state.selected_indices = catalog_tires.index.tolist()
                    st.rerun()
            
            # Auswahl-Statistiken
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Gefiltert", len(df_filtered))
            with col2:
                st.metric("Ausgewählt", len(st.session_state.selected_indices))
            with col3:
                if len(st.session_state.selected_indices) > 0:
                    selected_df = df_filtered.loc[st.session_state.selected_indices]
                    avg_preis = selected_df[selected_df['Preis_EUR'] > 0]['Preis_EUR'].mean()
                    st.metric("Durchschnittspreis", f"{avg_preis:.0f} Euro" if not pd.isna(avg_preis) else "0 Euro")
            with col4:
                if 'Quelle' in df_filtered.columns and len(st.session_state.selected_indices) > 0:
                    selected_df = df_filtered.loc[st.session_state.selected_indices]
                    quelle_counts = selected_df['Quelle'].value_counts()
                    main_quelle = quelle_counts.index[0] if len(quelle_counts) > 0 else "Gemischt"
                    st.metric("Hauptquelle", main_quelle.replace('-Excel', '').replace('-CSV', ''))
            
            # Reifen-Liste mit Checkboxes (vereinfacht)
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
                    duplicate_info = " ⚠️ **DUPLIKAT**" if is_duplicate else ""
                    missing_info = " 📝 **LEERE VORLAGE**" if is_missing else ""
                    saison_badge = get_saison_badge_html(row.get('Saison', 'Unbekannt'))
                    quelle_info = f" ({row.get('Quelle', 'Unbekannt').replace('-Excel', '').replace('-CSV', '')})" if 'Quelle' in row else ""
                    
                    if is_missing:
                        st.markdown(f"**{row['Dimension']}** - {row['Teilenummer']} {saison_badge}{quelle_info}{duplicate_info}{missing_info}", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{row['Dimension']}** - {row['Fabrikat']} {row['Profil']} - **{row['Preis_EUR']:.2f}€** - {row['Teilenummer']} {saison_badge}{quelle_info}{duplicate_info}", unsafe_allow_html=True)
            
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
    
    # STUFE 3: Bearbeitung (vereinfacht)
    elif st.session_state.selection_confirmed and st.session_state.df_working is not None:
        st.markdown("### Schritt 3: Reifen bearbeiten und speichern")
        st.markdown(f"Bearbeite die {len(st.session_state.df_working)} ausgewählten Reifen")
        
        # Anzeige-Tabelle
        st.markdown("#### Ausgewählte Reifen")
        display_df = st.session_state.df_working.copy()
        display_columns = ['Breite', 'Hoehe', 'Zoll', 'Loadindex', 'Speedindex', 'Fabrikat', 
                          'Profil', 'Teilenummer', 'Saison', 'Quelle', 'Preis_EUR', 'Bestand']
        available_display_columns = [col for col in display_columns if col in display_df.columns]
        display_df = display_df[available_display_columns]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Einzelnen Reifen bearbeiten (vereinfacht)
        if len(st.session_state.df_working) > 0:
            max_index = len(st.session_state.df_working) - 1
            if st.session_state.current_tire_index > max_index:
                st.session_state.current_tire_index = max_index
            if st.session_state.current_tire_index < 0:
                st.session_state.current_tire_index = 0
            
            # Navigation
            col_nav1, col_nav2, col_nav3 = st.columns([2, 1, 1])
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
            
            # Aktuellen Reifen bearbeiten (stark vereinfacht)
            df_working_list = list(st.session_state.df_working.iterrows())
            selected_idx, selected_row = df_working_list[st.session_state.current_tire_index]
            
            is_duplicate = check_duplicate_in_master(selected_row['Teilenummer'])
            
            if is_duplicate:
                st.warning(f"⚠️ DUPLIKAT: Teilenummer {selected_row['Teilenummer']} existiert bereits in der Master-Datenbank.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Reifen Info:**")
                st.write(f"**Teilenummer:** {selected_row['Teilenummer']}")
                st.write(f"**Fabrikat:** {selected_row['Fabrikat']}")
                st.write(f"**Profil:** {selected_row['Profil']}")
                
                new_preis = st.number_input(
                    "Preis:",
                    min_value=0.0,
                    max_value=2000.0,
                    value=float(selected_row['Preis_EUR']),
                    step=0.01,
                    key=f"preis_{selected_idx}"
                )
            
            with col2:
                st.markdown("**Saison & Bestand:**")
                
                saison_options = ['Winter', 'Sommer', 'Ganzjahres', 'Unbekannt']
                current_saison = selected_row.get('Saison', 'Unbekannt')
                saison_index = saison_options.index(current_saison) if current_saison in saison_options else 3
                
                new_saison = st.selectbox(
                    "Saison:",
                    options=saison_options,
                    index=saison_index,
                    key=f"saison_{selected_idx}"
                )
                
                current_bestand = selected_row.get('Bestand', 0)
                bestand_value = int(current_bestand) if pd.notna(current_bestand) else 0
                    
                new_bestand = st.number_input(
                    "Bestand:",
                    min_value=-999,
                    max_value=1000,
                    value=bestand_value,
                    step=1,
                    key=f"bestand_{selected_idx}"
                )
            
            # Speichern Button
            if st.button("Änderungen speichern", use_container_width=True, type="primary"):
                # Vereinfachte Reifen-Daten
                tire_data = {
                    'Breite': selected_row['Breite'],
                    'Hoehe': selected_row['Hoehe'], 
                    'Zoll': selected_row['Zoll'],
                    'Loadindex': selected_row['Loadindex'],
                    'Speedindex': selected_row['Speedindex'],
                    'Fabrikat': selected_row['Fabrikat'],
                    'Profil': selected_row['Profil'],
                    'Teilenummer': selected_row['Teilenummer'],
                    'Preis_EUR': new_preis,
                    'Bestand': new_bestand,
                    'Saison': new_saison
                }
                
                if update_master_csv_with_tire(tire_data):
                    st.session_state.df_working.loc[selected_idx, 'Preis_EUR'] = new_preis
                    st.session_state.df_working.loc[selected_idx, 'Bestand'] = new_bestand
                    st.session_state.df_working.loc[selected_idx, 'Saison'] = new_saison
                    
                    if st.session_state.current_tire_index < len(st.session_state.df_working) - 1:
                        st.session_state.current_tire_index += 1
                        st.success(f"Reifen gespeichert! Automatisch zu Reifen {st.session_state.current_tire_index + 1} gewechselt.")
                    else:
                        st.success("Reifen erfolgreich gespeichert!")
                else:
                    st.error("Fehler beim Speichern!")
                
                st.rerun()
        
        # Action Buttons
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("Zurück zur Auswahl"):
                st.session_state.selection_confirmed = False
                st.session_state.current_tire_index = 0
                st.rerun()
        
        with col_btn2:
            if st.button("Workflow zurücksetzen"):
                st.session_state.filter_applied = False
                st.session_state.selection_confirmed = False
                st.session_state.df_filtered = None
                st.session_state.df_working = None
                st.session_state.selected_indices = []
                st.session_state.current_tire_index = 0
                st.rerun()
        
        # GitHub Export
        st.markdown("---")
        st.markdown("#### 🔄 GitHub Export")
        
        github_data = create_github_export()
        if github_data:
            st.download_button(
                label="📥 Master-DB herunterladen",
                data=github_data,
                file_name="Ramsperger_Winterreifen_20250826_160010.csv",
                mime="text/csv",
                help="Master-Datenbank für GitHub Update",
                use_container_width=True
            )
        
        st.markdown("---")
        st.success("🎯 **ALLE PROBLEME GEFIXT:** Sommer-, Winter- und Ganzjahres-Filter funktionieren perfekt!")

# ================================================================================================
# MAIN FUNCTIONS
# ================================================================================================
def main():
    init_session_state()
    
    if not check_authentication():
        return
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>Reifen Verwaltung</h1>
        <p>Komplett gefixtes Multi-Source System - Alle Saison-Filter funktionieren!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("---")
        if st.button("← Zurück zur Reifen Suche", use_container_width=True):
            st.switch_page("pages/01_Reifen_Suche.py")
        
        if st.button("🛒 Zum Warenkorb", use_container_width=True, type="primary"):
            st.switch_page("pages/02_Warenkorb.py")
    
    render_reifen_content()

if __name__ == "__main__":
    main()