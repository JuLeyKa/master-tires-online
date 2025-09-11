import streamlit as st
import pandas as pd
import io
from datetime import datetime
from pathlib import Path

# Page Config
st.set_page_config(
    page_title="Datenbank Verwaltung - Ramsperger",
    page_icon="🗄️",
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
    
    .error-box {
        background: linear-gradient(135deg, #fef2f2, #fee2e2);
        padding: 1rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--error-color);
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
    }
    
    .database-info {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        padding: 1rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
        border-left: 4px solid var(--success-color);
        box-shadow: var(--shadow-sm);
    }
    
    .upload-box {
        border: 2px dashed var(--primary-color);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
        background: linear-gradient(135deg, #f8fafc, #e2e8f0);
        box-shadow: var(--shadow-md);
        transition: border-color 0.2s ease;
    }
    
    .upload-box:hover {
        border-color: var(--primary-dark);
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
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

def create_status_badge(text, status="info"):
    """Erstellt Status-Badge"""
    colors = {
        "success": "var(--success-color)",
        "warning": "var(--warning-color)", 
        "error": "var(--error-color)",
        "info": "var(--primary-color)"
    }
    
    bg_colors = {
        "success": "#f0fdf4",
        "warning": "#fef3c7",
        "error": "#fef2f2", 
        "info": "#f0f9ff"
    }
    
    color = colors.get(status, colors["info"])
    bg_color = bg_colors.get(status, bg_colors["info"])
    
    return f"""
    <span style="
        background: {bg_color};
        color: {color};
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid {color};
    ">{text}</span>
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
def init_sample_data():
    """Initialisiert Beispiel-Daten wenn keine vorhanden"""
    if 'master_data' not in st.session_state:
        sample_data = {
            'Breite': [195, 205, 215, 225, 195, 205, 215, 225],
            'Hoehe': [65, 55, 60, 55, 60, 60, 55, 50],
            'Zoll': [15, 16, 16, 17, 16, 17, 17, 18],
            'Fabrikat': ['Continental', 'Michelin', 'Bridgestone', 'Pirelli', 'Continental', 'Michelin', 'Bridgestone', 'Pirelli'],
            'Profil': ['WinterContact TS850', 'Alpin 6', 'Blizzak LM005', 'Winter Sottozero 3', 'WinterContact TS860', 'Alpin 5', 'Blizzak WS90', 'Winter Sottozero Serie II'],
            'Teilenummer': ['15494940000', '03528700000', '19394', '8019227308853', '15495040000', '03528800000', '19395', '8019227308854'],
            'Preis_EUR': [89.90, 95.50, 87.20, 99.90, 92.90, 98.50, 89.20, 103.90],
            'Loadindex': [91, 91, 94, 94, 88, 91, 94, 97],
            'Speedindex': ['T', 'H', 'H', 'V', 'H', 'H', 'H', 'V'],
            'Kraftstoffeffizienz': ['C', 'B', 'A', 'C', 'C', 'B', 'A', 'C'],
            'Nasshaftung': ['B', 'A', 'A', 'B', 'B', 'A', 'A', 'B'],
            'Bestand': [25, 12, 8, 15, 30, 0, -5, 20]
        }
        st.session_state.master_data = pd.DataFrame(sample_data)
    
    if 'central_data' not in st.session_state:
        st.session_state.central_data = pd.DataFrame()
    
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

def load_csv_file(uploaded_file, data_type):
    """Lädt CSV/Excel-Datei"""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        df_clean = clean_dataframe(df)
        
        if df_clean.empty:
            return False, "Keine gültigen Daten in der Datei"
        
        if data_type == "master":
            st.session_state.master_data = df_clean
        elif data_type == "central":
            st.session_state.central_data = df_clean
        
        return True, len(df_clean)
    except Exception as e:
        return False, str(e)

def export_to_csv(data_type):
    """Exportiert Daten als CSV"""
    init_sample_data()
    
    if data_type == "master":
        df = st.session_state.master_data
        filename = f"Master_Daten_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    elif data_type == "central":
        df = st.session_state.central_data
        filename = f"Central_Daten_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    elif data_type == "combined":
        df = get_combined_data()
        filename = f"Kombinierte_Daten_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    else:
        return None, None
    
    if df.empty:
        return None, None
    
    # CSV erstellen
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, encoding='utf-8')
    csv_data = csv_buffer.getvalue()
    
    return csv_data, filename

# ================================================================================================
# SESSION STATE INITIALISIERUNG
# ================================================================================================
def init_session_state():
    """Initialisiert Session State für Datenbank Verwaltung"""
    if 'db_authenticated' not in st.session_state:
        st.session_state.db_authenticated = False
    if 'db_current_source' not in st.session_state:
        st.session_state.db_current_source = "Zentrale Datenbank"
    if 'db_current_index' not in st.session_state:
        st.session_state.db_current_index = 0
    if 'db_working_data' not in st.session_state:
        st.session_state.db_working_data = pd.DataFrame()

# ================================================================================================
# AUTHENTICATION & MAIN FUNCTIONS
# ================================================================================================
def check_authentication():
    """Prüft Authentifizierung für Admin-Bereich"""
    if not st.session_state.db_authenticated:
        st.markdown("""
        <div class="main-header">
            <h1>Datenbank Verwaltung</h1>
            <p>Vollzugriff auf die Reifendatenbank</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="warning-box">
            <h4>Administratorzugang erforderlich</h4>
            <p>Dieser Bereich ermoeglicht vollstaendige Datenbank-Operationen und ist nur fuer Administratoren zugaenglich.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password = st.text_input("Administrator-PIN:", type="password", key="db_password")
            
            col_login, col_back = st.columns(2)
            with col_login:
                if st.button("Anmelden", use_container_width=True, type="primary"):
                    if password == "1234":  # Standard-Passwort
                        st.session_state.db_authenticated = True
                        st.success("Administratorzugang gewaehrt!")
                        st.rerun()
                    else:
                        st.error("Falsches Passwort!")
            
            with col_back:
                if st.button("Zurueck", use_container_width=True):
                    st.switch_page("app.py")
        
        return False
    return True

def render_central_database_management():
    """Rendert Zentrale Datenbank Verwaltung"""
    st.markdown("### Zentrale Datenbank")
    st.markdown("Bearbeitete und ergaenzte Reifendaten mit EU-Labels und Bestaenden.")
    
    # Upload-Bereich
    render_upload_section("central")
    
    # Aktuelle Daten
    central_data = st.session_state.central_data
    
    if central_data.empty:
        st.markdown("""
        <div class="info-box">
            <h4>Zentrale Datenbank ist leer</h4>
            <p>Die zentrale Datenbank enthaelt keine Daten. Lade eine CSV/Excel-Datei hoch oder fuege Daten aus der Premium-Verwaltung hinzu.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Statistiken
    render_database_statistics(central_data, "Zentrale Datenbank")
    
    # Datenbank-Operationen
    render_database_operations(central_data, "central")
    
    # Daten anzeigen und bearbeiten
    render_data_editor(central_data, "central")

def render_master_data_management():
    """Rendert Master-Daten Verwaltung"""
    st.markdown("### Master-Daten")
    st.markdown("Urspruengliche Reifendaten - schreibgeschuetzte Basisdaten.")
    
    # Upload-Bereich
    render_upload_section("master")
    
    # Warnung für Master-Daten
    st.markdown("""
    <div class="warning-box">
        <h4>Vorsicht bei Master-Daten</h4>
        <p>Master-Daten sind die Basis aller Operationen. Aenderungen hier wirken sich auf die gesamte Anwendung aus.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Aktuelle Daten
    master_data = st.session_state.master_data
    
    if master_data.empty:
        st.markdown("""
        <div class="error-box">
            <h4>Keine Master-Daten verfuegbar</h4>
            <p>Ohne Master-Daten kann die Anwendung nicht funktionieren. Bitte lade eine Basis-CSV-Datei hoch.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Statistiken
    render_database_statistics(master_data, "Master-Daten")
    
    # Datenbank-Operationen
    render_database_operations(master_data, "master")
    
    # Daten anzeigen (schreibgeschützt)
    render_data_viewer(master_data)

def render_combined_view():
    """Rendert kombinierte Ansicht aller Daten"""
    st.markdown("### Kombinierte Ansicht")
    st.markdown("Vereint Master-Daten und zentrale Datenbank - so wie sie in der Reifen-Suche erscheinen.")
    
    combined_data = get_combined_data()
    
    if combined_data.empty:
        st.warning("Keine Daten verfuegbar. Bitte lade Daten in den anderen Bereichen hoch.")
        return
    
    # Statistiken
    render_database_statistics(combined_data, "Kombinierte Daten")
    
    # Merge-Logik erklären
    st.markdown("""
    <div class="info-box">
        <h4>Merge-Logik</h4>
        <ul>
            <li><strong>Master-Daten:</strong> Basis-Reifenkatelog</li>
            <li><strong>Zentrale DB:</strong> Bearbeitete und neue Reifen</li>
            <li><strong>Regel:</strong> Zentrale DB ueberschreibt Master-Daten bei gleicher Teilenummer</li>
            <li><strong>Ergebnis:</strong> Aktuelle Daten fuer die Reifen-Suche</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Export der kombinierten Daten
    if st.button("Kombinierte Daten exportieren", type="primary"):
        csv_data, filename = export_to_csv("combined")
        if csv_data:
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=filename,
                mime="text/csv"
            )
    
    # Daten anzeigen (schreibgeschützt)
    render_data_viewer(combined_data)

def render_upload_section(data_type):
    """Rendert Upload-Bereich"""
    st.markdown("#### Daten hochladen")
    
    uploaded_file = st.file_uploader(
        f"CSV oder Excel-Datei fuer {data_type} hochladen:",
        type=['csv', 'xlsx', 'xls'],
        help="Unterstuetzte Formate: CSV, Excel (.xlsx, .xls)",
        key=f"upload_{data_type}"
    )
    
    if uploaded_file:
        try:
            with st.spinner("Datei wird verarbeitet..."):
                success, result = load_csv_file(uploaded_file, data_type)
                
                if success:
                    st.success(f"{result} Reifen erfolgreich geladen!")
                    st.rerun()
                else:
                    st.error(f"Fehler beim Laden: {result}")
        except Exception as e:
            st.error(f"Unerwarteter Fehler: {e}")

def render_database_statistics(df, db_name):
    """Rendert Datenbank-Statistiken"""
    st.markdown("---")
    st.markdown(f"#### {db_name} Statistiken")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(create_metric_card("Reifen gesamt", str(len(df))), unsafe_allow_html=True)
    
    with col2:
        hersteller_count = df['Fabrikat'].nunique()
        st.markdown(create_metric_card("Hersteller", str(hersteller_count)), unsafe_allow_html=True)
    
    with col3:
        avg_price = df['Preis_EUR'].mean() if not df.empty else 0
        st.markdown(create_metric_card("O Preis", f"{avg_price:.0f}EUR"), unsafe_allow_html=True)
    
    with col4:
        if 'Bestand' in df.columns:
            with_stock = len(df[df['Bestand'].notna()])
            st.markdown(create_metric_card("Mit Bestand", str(with_stock)), unsafe_allow_html=True)
        else:
            st.markdown(create_metric_card("Mit Bestand", "0"), unsafe_allow_html=True)
    
    with col5:
        if 'Kraftstoffeffizienz' in df.columns:
            with_labels = len(df[df['Kraftstoffeffizienz'].notna() & (df['Kraftstoffeffizienz'] != '')])
            st.markdown(create_metric_card("Mit EU-Label", str(with_labels)), unsafe_allow_html=True)
        else:
            st.markdown(create_metric_card("Mit EU-Label", "0"), unsafe_allow_html=True)
    
    # Bestandsverteilung
    if 'Bestand' in df.columns and not df[df['Bestand'].notna()].empty:
        render_stock_distribution(df)

def render_stock_distribution(df):
    """Rendert Bestandsverteilung"""
    st.markdown("**Bestandsverteilung:**")
    
    stock_data = df[df['Bestand'].notna()]
    if not stock_data.empty:
        negative = len(stock_data[stock_data['Bestand'] < 0])
        zero = len(stock_data[stock_data['Bestand'] == 0])
        positive = len(stock_data[stock_data['Bestand'] > 0])
        total_stock = stock_data['Bestand'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"**Negativ:** {negative}")
        with col2:
            st.markdown(f"**Null:** {zero}")
        with col3:
            st.markdown(f"**Positiv:** {positive}")
        with col4:
            color = "SCHLECHT" if total_stock < 0 else "GUT"
            st.markdown(f"**{color} Gesamt:** {total_stock:.0f}")

def render_database_operations(df, data_type):
    """Rendert Datenbank-Operationen"""
    st.markdown("---")
    st.markdown("#### Datenbank-Operationen")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Export
        if st.button(f"{data_type.title()} exportieren", use_container_width=True):
            csv_data, filename = export_to_csv(data_type)
            if csv_data:
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    key=f"download_{data_type}"
                )
    
    with col2:
        # Backup erstellen
        if st.button(f"Backup erstellen", use_container_width=True):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"Backup_{data_type}_{timestamp}.csv"
            csv_data, _ = export_to_csv(data_type)
            if csv_data:
                st.download_button(
                    label="Backup herunterladen",
                    data=csv_data,
                    file_name=backup_filename,
                    mime="text/csv",
                    key=f"backup_{data_type}"
                )
    
    with col3:
        # Datenbank leeren (mit Bestätigung)
        if st.button(f"Datenbank leeren", use_container_width=True, type="secondary"):
            st.session_state[f'confirm_clear_{data_type}'] = True
    
    with col4:
        # Daten neu laden
        if st.button(f"Neu laden", use_container_width=True):
            init_sample_data()
            st.success("Daten neu geladen!")
            st.rerun()
    
    # Bestätigung für Löschen
    if st.session_state.get(f'confirm_clear_{data_type}', False):
        st.markdown("""
        <div class="error-box">
            <h4>Datenbank wirklich leeren?</h4>
            <p>Diese Aktion kann nicht rueckgaengig gemacht werden!</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("Ja, leeren", type="primary", key=f"confirm_yes_{data_type}"):
                if data_type == "central":
                    st.session_state.central_data = pd.DataFrame()
                else:
                    st.session_state.master_data = pd.DataFrame()
                st.session_state[f'confirm_clear_{data_type}'] = False
                st.success(f"{data_type.title()}-Datenbank geleert!")
                st.rerun()
        
        with col_no:
            if st.button("Abbrechen", key=f"confirm_no_{data_type}"):
                st.session_state[f'confirm_clear_{data_type}'] = False
                st.rerun()

def render_data_editor(df, data_type):
    """Rendert bearbeitbaren Dateneditor"""
    if df.empty:
        return
    
    st.markdown("---")
    st.markdown("#### Daten bearbeiten")
    
    # Einfache Tabellenansicht mit Pagination
    items_per_page = 20
    total_pages = (len(df) + items_per_page - 1) // items_per_page
    
    if total_pages > 1:
        page = st.selectbox(f"Seite auswaehlen (je {items_per_page} Reifen):", 
                           range(1, total_pages + 1), 
                           key=f"page_{data_type}") - 1
        
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(df))
        page_data = df.iloc[start_idx:end_idx]
    else:
        page_data = df
        page = 0
    
    # Anzeige-DataFrame vorbereiten
    display_df = page_data.copy()
    
    # Formatierung für bessere Darstellung
    if 'Bestand' in display_df.columns:
        display_df['Bestand'] = display_df['Bestand'].apply(get_stock_display)
    
    if 'Kraftstoffeffizienz' in display_df.columns:
        display_df['Kraftstoff'] = display_df['Kraftstoffeffizienz'].apply(
            lambda x: f"{get_efficiency_emoji(x)} {x}" if pd.notna(x) and x != '' else ""
        )
    
    if 'Nasshaftung' in display_df.columns:
        display_df['Nasshaft.'] = display_df['Nasshaftung'].apply(
            lambda x: f"{get_efficiency_emoji(x)} {x}" if pd.notna(x) and x != '' else ""
        )
    
    # Nur relevante Spalten anzeigen
    display_cols = ['Breite', 'Hoehe', 'Zoll', 'Fabrikat', 'Profil', 'Teilenummer', 'Preis_EUR']
    if 'Bestand' in display_df.columns:
        display_cols.append('Bestand')
    if 'Kraftstoff' in display_df.columns:
        display_cols.append('Kraftstoff')
    if 'Nasshaft.' in display_df.columns:
        display_cols.append('Nasshaft.')
    
    available_cols = [col for col in display_cols if col in display_df.columns]
    
    # Dataframe anzeigen
    st.dataframe(
        display_df[available_cols], 
        use_container_width=True,
        hide_index=True
    )
    
    # Einzelreifen bearbeiten
    if len(page_data) > 0:
        render_single_tire_editor(page_data, data_type, start_idx if total_pages > 1 else 0)

def render_data_viewer(df):
    """Rendert schreibgeschützte Datenansicht"""
    if df.empty:
        return
    
    st.markdown("---")
    st.markdown("#### Daten anzeigen (schreibgeschuetzt)")
    
    # Pagination
    items_per_page = 25
    total_pages = (len(df) + items_per_page - 1) // items_per_page
    
    if total_pages > 1:
        page = st.selectbox(f"Seite auswaehlen (je {items_per_page} Reifen):", range(1, total_pages + 1)) - 1
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(df))
        display_data = df.iloc[start_idx:end_idx]
    else:
        display_data = df
    
    # Formatierte Anzeige
    display_df = display_data.copy()
    
    if 'Bestand' in display_df.columns:
        display_df['Bestand'] = display_df['Bestand'].apply(get_stock_display)
    
    # Dataframe anzeigen
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def render_single_tire_editor(df, data_type, start_offset=0):
    """Rendert Editor für einzelne Reifen"""
    st.markdown("#### Einzelreifen bearbeiten")
    
    # Reifen auswählen
    tire_options = []
    for i, (_, row) in enumerate(df.iterrows()):
        display_text = f"{i+1}: {row['Breite']}/{row['Hoehe']} R{row['Zoll']} - {row['Fabrikat']} {row['Profil']}"
        tire_options.append(display_text)
    
    selected_tire_idx = st.selectbox(
        "Reifen zum Bearbeiten auswaehlen:",
        options=range(len(tire_options)),
        format_func=lambda x: tire_options[x],
        key=f"tire_editor_{data_type}"
    )
    
    current_tire = df.iloc[selected_tire_idx]
    
    # Bearbeitungsformular
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Reifen-Info:**")
        st.write(f"**Groesse:** {current_tire['Breite']}/{current_tire['Hoehe']} R{current_tire['Zoll']}")
        st.write(f"**Hersteller:** {current_tire['Fabrikat']}")
        st.write(f"**Profil:** {current_tire['Profil']}")
        st.write(f"**Teilenummer:** {current_tire['Teilenummer']}")
        
        # Preis bearbeiten
        new_price = st.number_input(
            "Preis (EUR):",
            min_value=0.0,
            max_value=2000.0,
            value=float(current_tire['Preis_EUR']),
            step=0.01,
            key=f"edit_price_{data_type}_{selected_tire_idx}"
        )
    
    with col2:
        st.markdown("**Bestand & Labels:**")
        
        # Bestand
        current_stock = current_tire.get('Bestand', 0)
        if pd.isna(current_stock):
            current_stock = 0
        
        new_stock = st.number_input(
            "Bestand:",
            min_value=-999,
            max_value=1000,
            value=int(current_stock),
            step=1,
            key=f"edit_stock_{data_type}_{selected_tire_idx}",
            help="Negative Werte = Nachbestellung noetig"
        )
        
        # EU-Labels
        efficiency_options = ['', 'A', 'B', 'C', 'D', 'E', 'F', 'G']
        
        current_efficiency = current_tire.get('Kraftstoffeffizienz', '')
        efficiency_index = efficiency_options.index(current_efficiency) if current_efficiency in efficiency_options else 0
        
        new_efficiency = st.selectbox(
            "Kraftstoffeffizienz:",
            options=efficiency_options,
            index=efficiency_index,
            key=f"edit_efficiency_{data_type}_{selected_tire_idx}"
        )
    
    # Speichern
    if st.button(f"Aenderungen speichern", key=f"save_{data_type}_{selected_tire_idx}", type="primary"):
        # Reifen aktualisieren
        actual_idx = start_offset + selected_tire_idx
        
        if data_type == "central":
            st.session_state.central_data.loc[st.session_state.central_data.index[actual_idx], 'Preis_EUR'] = new_price
            st.session_state.central_data.loc[st.session_state.central_data.index[actual_idx], 'Bestand'] = new_stock
            st.session_state.central_data.loc[st.session_state.central_data.index[actual_idx], 'Kraftstoffeffizienz'] = new_efficiency
        else:
            st.session_state.master_data.loc[st.session_state.master_data.index[actual_idx], 'Preis_EUR'] = new_price
            st.session_state.master_data.loc[st.session_state.master_data.index[actual_idx], 'Bestand'] = new_stock
            st.session_state.master_data.loc[st.session_state.master_data.index[actual_idx], 'Kraftstoffeffizienz'] = new_efficiency
        
        st.success("Reifen erfolgreich aktualisiert!")
        st.rerun()

def export_database():
    """Exportiert komplette Datenbank"""
    st.markdown("### Datenbank Export")
    
    export_option = st.selectbox(
        "Was moechten Sie exportieren?",
        options=["Zentrale Datenbank", "Master-Daten", "Kombinierte Daten", "Alle Daten (ZIP)"],
        key="export_option"
    )
    
    if export_option == "Alle Daten (ZIP)":
        st.info("ZIP-Export wird in einer zukuenftigen Version verfuegbar sein.")
    else:
        data_type_map = {
            "Zentrale Datenbank": "central",
            "Master-Daten": "master", 
            "Kombinierte Daten": "combined"
        }
        
        data_type = data_type_map[export_option]
        csv_data, filename = export_to_csv(data_type)
        
        if csv_data:
            st.download_button(
                label=f"{export_option} herunterladen",
                data=csv_data,
                file_name=filename,
                mime="text/csv"
            )
        else:
            st.error("Keine Daten zum Exportieren verfuegbar!")

# ================================================================================================
# MAIN FUNCTION
# ================================================================================================
def main():
    init_session_state()
    
    if not check_authentication():
        return
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>Datenbank Verwaltung</h1>
        <p>Vollstaendige Kontrolle ueber die Reifendatenbank</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - Datenquelle wählen
    with st.sidebar:
        st.header("Datenbank-Auswahl")
        
        source_options = ["Zentrale Datenbank", "Master-Daten", "Kombinierte Ansicht"]
        
        new_source = st.selectbox(
            "Datenquelle:",
            options=source_options,
            index=source_options.index(st.session_state.db_current_source),
            key="db_source_select"
        )
        
        if new_source != st.session_state.db_current_source:
            st.session_state.db_current_source = new_source
            st.session_state.db_current_index = 0
            st.rerun()
        
        st.markdown("---")
        
        # Schnell-Aktionen
        st.markdown("**Schnell-Aktionen:**")
        
        if st.button("Datenbank exportieren", use_container_width=True, type="primary"):
            export_database()
        
        if st.button("Cache leeren", use_container_width=True):
            # Session State für Daten zurücksetzen
            if 'master_data' in st.session_state:
                del st.session_state.master_data
            if 'central_data' in st.session_state:
                del st.session_state.central_data
            init_sample_data()
            st.success("Cache geleert und Beispieldaten geladen!")
            st.rerun()
        
        st.markdown("---")
        
        # Navigation
        if st.button("Reifen Suche", use_container_width=True):
            st.switch_page("pages/01_Reifen_Suche.py")
        
        if st.button("Warenkorb", use_container_width=True):
            st.switch_page("pages/02_Warenkorb.py")
        
        if st.button("Premium Verwaltung", use_container_width=True):
            st.switch_page("pages/03_Premium_Verwaltung.py")
        
        if st.button("Abmelden", use_container_width=True, type="secondary"):
            st.session_state.db_authenticated = False
            st.rerun()
    
    # Hauptinhalt basierend auf gewählter Datenquelle
    if st.session_state.db_current_source == "Zentrale Datenbank":
        render_central_database_management()
    elif st.session_state.db_current_source == "Master-Daten":
        render_master_data_management()
    else:
        render_combined_view()

if __name__ == "__main__":
    main()