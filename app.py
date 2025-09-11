import streamlit as st
from pathlib import Path

# Page Config muss als erstes sein
st.set_page_config(
    page_title="Ramsperger Reifen System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e40af, #3b82f6);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
</style>
""", unsafe_allow_html=True)

def main():
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
    
    # Beispiel-Daten laden (später durch echte Daten ersetzen)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Reifen im System", "1,234", "↗ 45")
    with col2:
        st.metric("Hersteller", "15", "")
    with col3:
        st.metric("Verfügbare Größen", "89", "")
    with col4:
        st.metric("Warenkorb", st.session_state.get('cart_count', 0), "")
    
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
    # Session State initialisieren
    if 'cart_count' not in st.session_state:
        st.session_state.cart_count = 0
    
    main()