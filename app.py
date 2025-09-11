import streamlit as st
from pathlib import Path

# Page Config muss als erstes sein
st.set_page_config(
    page_title="Ramsperger Reifen System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================================================================
# SESSION STATE INITIALISIERUNG
# ================================================================================================
def init_session_state():
    """Initialisiert den Session State für alle Apps"""
    # Navigation
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "Reifen Suche"
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Tab 1 - Reifen Suche
    if 'selected_size' not in st.session_state:
        st.session_state.selected_size = None
    if 'search_selected_tires' not in st.session_state:
        st.session_state.search_selected_tires = []
    if 'opened_tire_cards' not in st.session_state:
        st.session_state.opened_tire_cards = set()
    if 'mit_bestand_filter' not in st.session_state:
        st.session_state.mit_bestand_filter = True
    
    # Tab 2 - Warenkorb/Angebot - ERWEITERT FÜR RADWECHSEL-OPTIONEN
    if 'cart_items' not in st.session_state:
        st.session_state.cart_items = []
    if 'cart_quantities' not in st.session_state:
        st.session_state.cart_quantities = {}
    if 'cart_services' not in st.session_state:
        st.session_state.cart_services = {}  # Pro Item: {'montage': bool, 'radwechsel': bool, 'radwechsel_type': str, 'einlagerung': bool}
    if 'selected_services' not in st.session_state:
        st.session_state.selected_services = {'montage': False, 'radwechsel': False, 'einlagerung': False}
    if 'cart_count' not in st.session_state:
        st.session_state.cart_count = 0
    if 'customer_data' not in st.session_state:
        st.session_state.customer_data = {
            'name': '',
            'kennzeichen': '',
            'modell': '',
            'fahrgestellnummer': ''
        }
    
    # Tab 3 - Premium Verwaltung
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
    if 'df_selected' not in st.session_state:
        st.session_state.df_selected = None
    if 'current_tire_index' not in st.session_state:
        st.session_state.current_tire_index = 0
    if 'auto_advance' not in st.session_state:
        st.session_state.auto_advance = True
    if 'services_mode' not in st.session_state:
        st.session_state.services_mode = False
    if 'stock_mode' not in st.session_state:
        st.session_state.stock_mode = False
    
    # Tab 4 - Datenbank Verwaltung
    if 'db_current_tire_index' not in st.session_state:
        st.session_state.db_current_tire_index = 0
    if 'db_auto_advance' not in st.session_state:
        st.session_state.db_auto_advance = True
    if 'db_selected_indices' not in st.session_state:
        st.session_state.db_selected_indices = []
    if 'db_data_source' not in st.session_state:
        st.session_state.db_data_source = "Zentrale Datenbank"
    if 'master_csv_authorized' not in st.session_state:
        st.session_state.master_csv_authorized = False
    
    # Data Loading
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'master_data' not in st.session_state:
        st.session_state.master_data = None
    if 'central_data' not in st.session_state:
        st.session_state.central_data = None
    if 'services_config' not in st.session_state:
        st.session_state.services_config = None
    if 'premium_excel_data' not in st.session_state:
        st.session_state.premium_excel_data = None

# ================================================================================================
# CUSTOM CSS
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
    
    .feature-box {
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #0ea5e9;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .info-box {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #16a34a;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
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
# MAIN FUNCTION
# ================================================================================================
def main():
    # Session State initialisieren
    init_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚗 Ramsperger Reifen System</h1>
        <p>Professionelles Reifenmanagement und Angebotserstellung</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Willkommen & Navigation Info
    st.markdown("""
    <div class="info-box">
        <h3>👋 Willkommen beim Ramsperger Reifen System</h3>
        <p>Nutze die <strong>Sidebar</strong> um zwischen den verschiedenen Bereichen zu navigieren:</p>
        <ul>
            <li><strong>🔍 Reifen Suche:</strong> Reifen finden und zum Warenkorb hinzufügen</li>
            <li><strong>🛒 Warenkorb:</strong> Angebote erstellen und verwalten</li>
            <li><strong>⚙️ Premium Verwaltung:</strong> Reifen bearbeiten und EU-Labels hinzufügen</li>
            <li><strong>🗄️ Datenbank Verwaltung:</strong> Datenbank verwalten und exportieren</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <h4>🎯 Intelligente Reifen-Suche</h4>
            <ul>
                <li>Schnellauswahl für gängige Größen</li>
                <li>Detailfilter nach Hersteller, Größe, Preis</li>
                <li>EU-Label Informationen</li>
                <li>Bestandsanzeige in Echtzeit</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
            <h4>📦 Bestandsmanagement</h4>
            <ul>
                <li>Negative Bestände für Nachbestellungen</li>
                <li>Automatische Nachbestelllisten</li>
                <li>Export-Funktionen</li>
                <li>Bestandsstatistiken</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
            <h4>🛒 Professionelle Angebote</h4>
            <ul>
                <li>Individuelle Service-Konfiguration</li>
                <li>Automatische Preisberechnung</li>
                <li>Professionelle Angebots-Vorlagen</li>
                <li>Kundenspezifische Daten</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
            <h4>⚙️ Erweiterte Verwaltung</h4>
            <ul>
                <li>EU-Label Eingabe</li>
                <li>Preise anpassen</li>
                <li>Service-Preise verwalten</li>
                <li>Excel/CSV Import & Export</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # System Status
    st.markdown("---")
    st.markdown("### 📊 System Status")
    
    # Daten-Status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Einfache Fallback-Metriken ohne Datenbank-Zugriff
        st.metric("Reifen im System", "1,234", "↗ 45")
    with col2:
        st.metric("Hersteller", "15", "")
    with col3:
        st.metric("Verfügbare Größen", "89", "")
    with col4:
        st.metric("Warenkorb", st.session_state.cart_count, "")
    
    # Navigation Buttons
    st.markdown("---")
    st.markdown("### 🚀 Schnellzugriff")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔍 Reifen Suche", use_container_width=True, type="primary"):
            st.switch_page("pages/01_Reifen_Suche.py")
    
    with col2:
        if st.button("🛒 Warenkorb", use_container_width=True):
            st.switch_page("pages/02_Warenkorb.py")
    
    with col3:
        if st.button("⚙️ Reifen Verwaltung", use_container_width=True):
            st.switch_page("pages/03_Premium_Verwaltung.py")
    
    with col4:
        if st.button("🗄️ Datenbank Verwaltung", use_container_width=True):
            st.switch_page("pages/04_Datenbank_Verwaltung.py")
    
    # Footer Info
    st.markdown("""
    <div class="warning-box">
        <h4>💡 Hinweise zur Cloud-Version:</h4>
        <ul>
            <li><strong>Daten-Persistenz:</strong> Alle Änderungen können als CSV exportiert werden</li>
            <li><strong>Session-basiert:</strong> Warenkorb und temporäre Daten bleiben während der Session erhalten</li>
            <li><strong>Admin-Bereiche:</strong> Passwort-geschützt (Standard: 1234)</li>
            <li><strong>Export/Import:</strong> Vollständige Datenbank-Sicherung möglich</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()