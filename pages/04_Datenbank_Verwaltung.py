import streamlit as st
import pandas as pd
import io
from datetime import datetime
import sys
from pathlib import Path

# Pfad-Fix für Streamlit Cloud
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

# Imports nach Pfad-Fix
try:
    from utils.data_manager import data_manager
    from utils.styles import apply_main_css, get_efficiency_emoji, get_stock_display, create_metric_card, create_status_badge
except ImportError:
    # Fallback für lokale Entwicklung
    from utils import data_manager, apply_main_css, get_efficiency_emoji, get_stock_display, create_metric_card, create_status_badge

# Page Config
st.set_page_config(
    page_title="Datenbank Verwaltung - Ramsperger",
    page_icon="🗄️",
    layout="wide"
)

# CSS anwenden
apply_main_css()

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

def check_authentication():
    """Prüft Authentifizierung für Admin-Bereich"""
    if not st.session_state.db_authenticated:
        st.markdown("""
        <div class="main-header">
            <h1>🗄️ Datenbank Verwaltung</h1>
            <p>Vollzugriff auf die Reifendatenbank</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="warning-box">
            <h4>🔐 Administratorzugang erforderlich</h4>
            <p>Dieser Bereich ermöglicht vollständige Datenbank-Operationen und ist nur für Administratoren zugänglich.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password = st.text_input("Administrator-PIN:", type="password", key="db_password")
            
            col_login, col_back = st.columns(2)
            with col_login:
                if st.button("🔓 Anmelden", use_container_width=True, type="primary"):
                    if password == "1234":  # Standard-Passwort
                        st.session_state.db_authenticated = True
                        st.success("Administratorzugang gewährt!")
                        st.rerun()
                    else:
                        st.error("Falsches Passwort!")
            
            with col_back:
                if st.button("← Zurück", use_container_width=True):
                    st.switch_page("app.py")
        
        return False
    return True

def main():
    init_session_state()
    
    if not check_authentication():
        return
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🗄️ Datenbank Verwaltung</h1>
        <p>Vollständige Kontrolle über die Reifendatenbank</p>
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
        
        if st.button("📤 Datenbank exportieren", use_container_width=True, type="primary"):
            export_database()
        
        if st.button("🔄 Cache leeren", use_container_width=True):
            # Session State für Daten zurücksetzen
            if 'master_data' in st.session_state:
                del st.session_state.master_data
            if 'central_data' in st.session_state:
                del st.session_state.central_data
            data_manager.init_sample_data()
            st.success("✅ Cache geleert und Beispieldaten geladen!")
            st.rerun()
        
        st.markdown("---")
        
        # Navigation
        if st.button("🔍 Reifen Suche", use_container_width=True):
            st.switch_page("pages/01_Reifen_Suche.py")
        
        if st.button("🛒 Warenkorb", use_container_width=True):
            st.switch_page("pages/02_Warenkorb.py")
        
        if st.button("⚙️ Premium Verwaltung", use_container_width=True):
            st.switch_page("pages/03_Premium_Verwaltung.py")
        
        if st.button("🚪 Abmelden", use_container_width=True, type="secondary"):
            st.session_state.db_authenticated = False
            st.rerun()
    
    # Hauptinhalt basierend auf gewählter Datenquelle
    if st.session_state.db_current_source == "Zentrale Datenbank":
        render_central_database_management()
    elif st.session_state.db_current_source == "Master-Daten":
        render_master_data_management()
    else:
        render_combined_view()

def render_central_database_management():
    """Rendert Zentrale Datenbank Verwaltung"""
    st.markdown("### 🎯 Zentrale Datenbank")
    st.markdown("Bearbeitete und ergänzte Reifendaten mit EU-Labels und Beständen.")
    
    # Upload-Bereich
    render_upload_section("central")
    
    # Aktuelle Daten
    central_data = st.session_state.central_data
    
    if central_data.empty:
        st.markdown("""
        <div class="info-box">
            <h4>💡 Zentrale Datenbank ist leer</h4>
            <p>Die zentrale Datenbank enthält keine Daten. Lade eine CSV/Excel-Datei hoch oder füge Daten aus der Premium-Verwaltung hinzu.</p>
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
    st.markdown("### 📊 Master-Daten")
    st.markdown("Ursprüngliche Reifendaten - schreibgeschützte Basisdaten.")
    
    # Upload-Bereich
    render_upload_section("master")
    
    # Warnung für Master-Daten
    st.markdown("""
    <div class="warning-box">
        <h4>⚠️ Vorsicht bei Master-Daten</h4>
        <p>Master-Daten sind die Basis aller Operationen. Änderungen hier wirken sich auf die gesamte Anwendung aus.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Aktuelle Daten
    master_data = st.session_state.master_data
    
    if master_data.empty:
        st.markdown("""
        <div class="error-box">
            <h4>❌ Keine Master-Daten verfügbar</h4>
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
    st.markdown("### 🔄 Kombinierte Ansicht")
    st.markdown("Vereint Master-Daten und zentrale Datenbank - so wie sie in der Reifen-Suche erscheinen.")
    
    combined_data = data_manager.get_combined_data()
    
    if combined_data.empty:
        st.warning("Keine Daten verfügbar. Bitte lade Daten in den anderen Bereichen hoch.")
        return
    
    # Statistiken
    render_database_statistics(combined_data, "Kombinierte Daten")
    
    # Merge-Logik erklären
    st.markdown("""
    <div class="info-box">
        <h4>🔄 Merge-Logik</h4>
        <ul>
            <li><strong>Master-Daten:</strong> Basis-Reifenkatelog</li>
            <li><strong>Zentrale DB:</strong> Bearbeitete und neue Reifen</li>
            <li><strong>Regel:</strong> Zentrale DB überschreibt Master-Daten bei gleicher Teilenummer</li>
            <li><strong>Ergebnis:</strong> Aktuelle Daten für die Reifen-Suche</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Export der kombinierten Daten
    if st.button("📤 Kombinierte Daten exportieren", type="primary"):
        csv_data, filename = data_manager.export_to_csv("combined")
        if csv_data:
            st.download_button(
                label="📋 Download CSV",
                data=csv_data,
                file_name=filename,
                mime="text/csv"
            )
    
    # Daten anzeigen (schreibgeschützt)
    render_data_viewer(combined_data)

def render_upload_section(data_type):
    """Rendert Upload-Bereich"""
    st.markdown("#### 📤 Daten hochladen")
    
    uploaded_file = st.file_uploader(
        f"CSV oder Excel-Datei für {data_type} hochladen:",
        type=['csv', 'xlsx', 'xls'],
        help="Unterstützte Formate: CSV, Excel (.xlsx, .xls)",
        key=f"upload_{data_type}"
    )
    
    if uploaded_file:
        try:
            with st.spinner("Datei wird verarbeitet..."):
                success, result = data_manager.load_csv_file(uploaded_file, data_type)
                
                if success:
                    st.success(f"✅ {result} Reifen erfolgreich geladen!")
                    st.rerun()
                else:
                    st.error(f"❌ Fehler beim Laden: {result}")
        except Exception as e:
            st.error(f"❌ Unerwarteter Fehler: {e}")

def render_database_statistics(df, db_name):
    """Rendert Datenbank-Statistiken"""
    st.markdown("---")
    st.markdown(f"#### 📊 {db_name} Statistiken")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(create_metric_card("Reifen gesamt", str(len(df))), unsafe_allow_html=True)
    
    with col2:
        hersteller_count = df['Fabrikat'].nunique()
        st.markdown(create_metric_card("Hersteller", str(hersteller_count)), unsafe_allow_html=True)
    
    with col3:
        avg_price = df['Preis_EUR'].mean() if not df.empty else 0
        st.markdown(create_metric_card("Ø Preis", f"{avg_price:.0f}€"), unsafe_allow_html=True)
    
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
    st.markdown("**📦 Bestandsverteilung:**")
    
    stock_data = df[df['Bestand'].notna()]
    if not stock_data.empty:
        negative = len(stock_data[stock_data['Bestand'] < 0])
        zero = len(stock_data[stock_data['Bestand'] == 0])
        positive = len(stock_data[stock_data['Bestand'] > 0])
        total_stock = stock_data['Bestand'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"🔴 **Negativ:** {negative}")
        with col2:
            st.markdown(f"⚪ **Null:** {zero}")
        with col3:
            st.markdown(f"🟢 **Positiv:** {positive}")
        with col4:
            color = "🔴" if total_stock < 0 else "🟢"
            st.markdown(f"{color} **Gesamt:** {total_stock:.0f}")

def render_database_operations(df, data_type):
    """Rendert Datenbank-Operationen"""
    st.markdown("---")
    st.markdown("#### ⚙️ Datenbank-Operationen")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Export
        if st.button(f"📤 {data_type.title()} exportieren", use_container_width=True):
            csv_data, filename = data_manager.export_to_csv(data_type)
            if csv_data:
                st.download_button(
                    label="📋 Download CSV",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    key=f"download_{data_type}"
                )
    
    with col2:
        # Backup erstellen
        if st.button(f"💾 Backup erstellen", use_container_width=True):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"Backup_{data_type}_{timestamp}.csv"
            csv_data, _ = data_manager.export_to_csv(data_type)
            if csv_data:
                st.download_button(
                    label="📥 Backup herunterladen",
                    data=csv_data,
                    file_name=backup_filename,
                    mime="text/csv",
                    key=f"backup_{data_type}"
                )
    
    with col3:
        # Datenbank leeren (mit Bestätigung)
        if st.button(f"🗑️ Datenbank leeren", use_container_width=True, type="secondary"):
            st.session_state[f'confirm_clear_{data_type}'] = True
    
    with col4:
        # Daten neu laden
        if st.button(f"🔄 Neu laden", use_container_width=True):
            data_manager.init_sample_data()
            st.success("✅ Daten neu geladen!")
            st.rerun()
    
    # Bestätigung für Löschen
    if st.session_state.get(f'confirm_clear_{data_type}', False):
        st.markdown("""
        <div class="error-box">
            <h4>⚠️ Datenbank wirklich leeren?</h4>
            <p>Diese Aktion kann nicht rückgängig gemacht werden!</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("✅ Ja, leeren", type="primary", key=f"confirm_yes_{data_type}"):
                if data_type == "central":
                    st.session_state.central_data = pd.DataFrame()
                else:
                    st.session_state.master_data = pd.DataFrame()
                st.session_state[f'confirm_clear_{data_type}'] = False
                st.success(f"✅ {data_type.title()}-Datenbank geleert!")
                st.rerun()
        
        with col_no:
            if st.button("❌ Abbrechen", key=f"confirm_no_{data_type}"):
                st.session_state[f'confirm_clear_{data_type}'] = False
                st.rerun()

def render_data_editor(df, data_type):
    """Rendert bearbeitbaren Dateneditor"""
    if df.empty:
        return
    
    st.markdown("---")
    st.markdown("#### ✏️ Daten bearbeiten")
    
    # Einfache Tabellenansicht mit Pagination
    items_per_page = 20
    total_pages = (len(df) + items_per_page - 1) // items_per_page
    
    if total_pages > 1:
        page = st.selectbox(f"Seite auswählen (je {items_per_page} Reifen):", 
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
    st.markdown("#### 👁️ Daten anzeigen (schreibgeschützt)")
    
    # Pagination
    items_per_page = 25
    total_pages = (len(df) + items_per_page - 1) // items_per_page
    
    if total_pages > 1:
        page = st.selectbox(f"Seite auswählen (je {items_per_page} Reifen):", range(1, total_pages + 1)) - 1
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
    st.markdown("#### 🔧 Einzelreifen bearbeiten")
    
    # Reifen auswählen
    tire_options = []
    for i, (_, row) in enumerate(df.iterrows()):
        display_text = f"{i+1}: {row['Breite']}/{row['Hoehe']} R{row['Zoll']} - {row['Fabrikat']} {row['Profil']}"
        tire_options.append(display_text)
    
    selected_tire_idx = st.selectbox(
        "Reifen zum Bearbeiten auswählen:",
        options=range(len(tire_options)),
        format_func=lambda x: tire_options[x],
        key=f"tire_editor_{data_type}"
    )
    
    current_tire = df.iloc[selected_tire_idx]
    
    # Bearbeitungsformular
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Reifen-Info:**")
        st.write(f"**Größe:** {current_tire['Breite']}/{current_tire['Hoehe']} R{current_tire['Zoll']}")
        st.write(f"**Hersteller:** {current_tire['Fabrikat']}")
        st.write(f"**Profil:** {current_tire['Profil']}")
        st.write(f"**Teilenummer:** {current_tire['Teilenummer']}")
        
        # Preis bearbeiten
        new_price = st.number_input(
            "Preis (€):",
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
            help="Negative Werte = Nachbestellung nötig"
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
    if st.button(f"💾 Änderungen speichern", key=f"save_{data_type}_{selected_tire_idx}", type="primary"):
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
        
        st.success("✅ Reifen erfolgreich aktualisiert!")
        st.rerun()

def export_database():
    """Exportiert komplette Datenbank"""
    st.markdown("### 📤 Datenbank Export")
    
    export_option = st.selectbox(
        "Was möchten Sie exportieren?",
        options=["Zentrale Datenbank", "Master-Daten", "Kombinierte Daten", "Alle Daten (ZIP)"],
        key="export_option"
    )
    
    if export_option == "Alle Daten (ZIP)":
        st.info("ZIP-Export wird in einer zukünftigen Version verfügbar sein.")
    else:
        data_type_map = {
            "Zentrale Datenbank": "central",
            "Master-Daten": "master", 
            "Kombinierte Daten": "combined"
        }
        
        data_type = data_type_map[export_option]
        csv_data, filename = data_manager.export_to_csv(data_type)
        
        if csv_data:
            st.download_button(
                label=f"📋 {export_option} herunterladen",
                data=csv_data,
                file_name=filename,
                mime="text/csv"
            )
        else:
            st.error("Keine Daten zum Exportieren verfügbar!")

if __name__ == "__main__":
    main()