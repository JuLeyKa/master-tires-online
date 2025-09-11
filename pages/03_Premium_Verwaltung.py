import streamlit as st
import pandas as pd
import io
from datetime import datetime
from utils import data_manager, apply_main_css, get_efficiency_emoji, get_stock_display, create_metric_card

# Page Config
st.set_page_config(
    page_title="Premium Verwaltung - Ramsperger",
    page_icon="⚙️",
    layout="wide"
)

# CSS anwenden
apply_main_css()

def init_session_state():
    """Initialisiert Session State für Premium Verwaltung"""
    if 'premium_authenticated' not in st.session_state:
        st.session_state.premium_authenticated = False
    if 'premium_mode' not in st.session_state:
        st.session_state.premium_mode = "Reifen Verwaltung"
    if 'premium_filter_applied' not in st.session_state:
        st.session_state.premium_filter_applied = False
    if 'premium_selected_indices' not in st.session_state:
        st.session_state.premium_selected_indices = []
    if 'premium_working_data' not in st.session_state:
        st.session_state.premium_working_data = pd.DataFrame()
    if 'premium_current_index' not in st.session_state:
        st.session_state.premium_current_index = 0

def check_authentication():
    """Prüft Authentifizierung für Admin-Bereich"""
    if not st.session_state.premium_authenticated:
        st.markdown("""
        <div class="main-header">
            <h1>⚙️ Premium Verwaltung</h1>
            <p>Passwort-geschützter Adminbereich</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="warning-box">
            <h4>🔐 Authentifizierung erforderlich</h4>
            <p>Dieser Bereich ist nur für autorisierte Benutzer zugänglich.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password = st.text_input("PIN eingeben:", type="password", key="premium_password")
            
            col_login, col_back = st.columns(2)
            with col_login:
                if st.button("🔓 Anmelden", use_container_width=True, type="primary"):
                    if password == "1234":  # Standard-Passwort
                        st.session_state.premium_authenticated = True
                        st.success("Zugang gewährt!")
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
        <h1>⚙️ Premium Verwaltung</h1>
        <p>Erweiterte Reifen- und Systemverwaltung</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - Modus-Auswahl
    with st.sidebar:
        st.header("Verwaltungsmodus")
        
        modus_options = ["Reifen Verwaltung", "Service-Preise", "Bestandsmanagement"]
        
        new_modus = st.selectbox(
            "Modus wählen:",
            options=modus_options,
            index=modus_options.index(st.session_state.premium_mode),
            key="premium_modus_select"
        )
        
        if new_modus != st.session_state.premium_mode:
            st.session_state.premium_mode = new_modus
            st.rerun()
        
        st.markdown("---")
        
        # Navigation
        if st.button("🔍 Reifen Suche", use_container_width=True):
            st.switch_page("pages/01_Reifen_Suche.py")
        
        if st.button("🛒 Warenkorb", use_container_width=True):
            st.switch_page("pages/02_Warenkorb.py")
        
        if st.button("🗄️ Datenbank Verwaltung", use_container_width=True):
            st.switch_page("pages/04_Datenbank_Verwaltung.py")
        
        if st.button("🚪 Abmelden", use_container_width=True, type="secondary"):
            st.session_state.premium_authenticated = False
            st.rerun()
    
    # Modus-spezifischer Content
    if st.session_state.premium_mode == "Reifen Verwaltung":
        render_tire_management()
    elif st.session_state.premium_mode == "Service-Preise":
        render_service_management()
    elif st.session_state.premium_mode == "Bestandsmanagement":
        render_stock_management()

def render_tire_management():
    """Rendert Reifen-Verwaltung"""
    st.markdown("### 🔧 Reifen Verwaltung")
    st.markdown("Bearbeite EU-Labels, Preise und Bestände für einzelne Reifen.")
    
    # Upload-Bereich für Excel/CSV
    st.markdown("#### 📤 Daten hochladen")
    uploaded_file = st.file_uploader(
        "Excel oder CSV-Datei hochladen:",
        type=['xlsx', 'xls', 'csv'],
        help="Lade eine Excel- oder CSV-Datei mit Reifendaten hoch"
    )
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            df = data_manager.clean_dataframe(df)
            
            if not df.empty:
                st.success(f"✅ {len(df)} Reifen erfolgreich geladen!")
                
                # Zur Central DB hinzufügen
                if st.button("📁 Zur Datenbank hinzufügen", type="primary"):
                    success, count = data_manager.add_or_update_central_data(df)
                    if success:
                        st.success(f"✅ {count} Reifen zur Datenbank hinzugefügt/aktualisiert!")
                    else:
                        st.error("❌ Fehler beim Speichern!")
            else:
                st.error("❌ Keine gültigen Daten in der Datei gefunden!")
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Datei: {e}")
    
    # Aktuelle Daten anzeigen
    st.markdown("---")
    st.markdown("#### 📊 Aktuelle Reifendaten")
    
    combined_data = data_manager.get_combined_data()
    if combined_data.empty:
        st.warning("Keine Reifendaten vorhanden. Bitte lade Daten hoch.")
        return
    
    # Statistiken
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_card("Reifen gesamt", str(len(combined_data))), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Hersteller", str(combined_data['Fabrikat'].nunique())), unsafe_allow_html=True)
    with col3:
        avg_price = combined_data['Preis_EUR'].mean()
        st.markdown(create_metric_card("Ø Preis", f"{avg_price:.0f}€"), unsafe_allow_html=True)
    with col4:
        with_stock = len(combined_data[combined_data['Bestand'].notna()])
        st.markdown(create_metric_card("Mit Bestand", str(with_stock)), unsafe_allow_html=True)
    
    # Filter-Interface
    render_premium_filters(combined_data)
    
    # Einzelreifen-Bearbeitung
    if not st.session_state.premium_working_data.empty:
        render_tire_editor()

def render_premium_filters(df):
    """Rendert Filter-Interface für Premium-Bereich"""
    st.markdown("#### 🔍 Intelligente Filter")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Hersteller Filter
        hersteller_options = ["Alle"] + sorted(df['Fabrikat'].dropna().unique().tolist())
        hersteller_filter = st.multiselect(
            "Hersteller:",
            options=hersteller_options[1:],  # Ohne "Alle"
            default=[],
            key="premium_hersteller"
        )
        
        # Zoll Filter
        zoll_options = sorted(df['Zoll'].unique().tolist())
        zoll_filter = st.multiselect(
            "Zoll-Größen:",
            options=zoll_options,
            default=[],
            key="premium_zoll"
        )
    
    with col2:
        # Preisbereich
        min_price = float(df['Preis_EUR'].min())
        max_price = float(df['Preis_EUR'].max())
        
        price_range = st.slider(
            "Preisbereich (€):",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price),
            step=10.0,
            key="premium_price"
        )
        
        # Teilenummer suchen
        search_term = st.text_input(
            "Teilenummer/Profil suchen:",
            placeholder="z.B. Continental, WinterContact",
            key="premium_search"
        )
    
    with col3:
        # Bestandsfilter
        stock_options = [
            ("alle", "Alle Reifen"),
            ("negative", "🔴 Negative Bestände"),
            ("positive", "🟢 Positive Bestände"),
            ("no_stock", "❓ Ohne Bestandsinfo")
        ]
        
        stock_filter = st.selectbox(
            "Bestandsfilter:",
            options=[opt[0] for opt in stock_options],
            format_func=lambda x: next(opt[1] for opt in stock_options if opt[0] == x),
            key="premium_stock_filter"
        )
    
    # Filter anwenden
    if st.button("🔍 Filter anwenden", type="primary"):
        filtered_df = apply_premium_filters(df, hersteller_filter, zoll_filter, price_range, search_term, stock_filter)
        st.session_state.premium_working_data = filtered_df
        st.session_state.premium_filter_applied = True
        st.success(f"✅ {len(filtered_df)} Reifen gefiltert")
        st.rerun()
    
    if st.button("🔄 Filter zurücksetzen"):
        st.session_state.premium_working_data = pd.DataFrame()
        st.session_state.premium_filter_applied = False
        st.session_state.premium_current_index = 0
        st.rerun()

def apply_premium_filters(df, hersteller_filter, zoll_filter, price_range, search_term, stock_filter):
    """Wendet Premium-Filter an"""
    filtered = df.copy()
    
    # Hersteller Filter
    if hersteller_filter:
        filtered = filtered[filtered['Fabrikat'].isin(hersteller_filter)]
    
    # Zoll Filter
    if zoll_filter:
        filtered = filtered[filtered['Zoll'].isin(zoll_filter)]
    
    # Preisfilter
    filtered = filtered[
        (filtered['Preis_EUR'] >= price_range[0]) & 
        (filtered['Preis_EUR'] <= price_range[1])
    ]
    
    # Suchterm
    if search_term:
        search_terms = [term.strip().upper() for term in search_term.split(',') if term.strip()]
        if search_terms:
            mask = pd.Series([False] * len(filtered))
            for term in search_terms:
                term_mask = (
                    filtered['Teilenummer'].str.upper().str.contains(term, na=False, regex=False) |
                    filtered['Fabrikat'].str.upper().str.contains(term, na=False, regex=False) |
                    filtered['Profil'].str.upper().str.contains(term, na=False, regex=False)
                )
                mask = mask | term_mask
            filtered = filtered[mask]
    
    # Bestandsfilter
    if stock_filter == "negative":
        filtered = filtered[(filtered['Bestand'].notna()) & (filtered['Bestand'] < 0)]
    elif stock_filter == "positive":
        filtered = filtered[(filtered['Bestand'].notna()) & (filtered['Bestand'] > 0)]
    elif stock_filter == "no_stock":
        filtered = filtered[filtered['Bestand'].isna()]
    
    return filtered

def render_tire_editor():
    """Rendert Einzelreifen-Editor"""
    st.markdown("---")
    st.markdown("#### ✏️ Reifen bearbeiten")
    
    if st.session_state.premium_working_data.empty:
        st.info("Keine Reifen zum Bearbeiten. Bitte Filter anwenden.")
        return
    
    df = st.session_state.premium_working_data
    
    # Navigation
    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
    
    with col1:
        st.info(f"Reifen {st.session_state.premium_current_index + 1} von {len(df)}")
    
    with col2:
        if st.button("← Vorheriger", disabled=(st.session_state.premium_current_index == 0)):
            st.session_state.premium_current_index -= 1
            st.rerun()
    
    with col3:
        if st.button("Nächster →", disabled=(st.session_state.premium_current_index >= len(df) - 1)):
            st.session_state.premium_current_index += 1
            st.rerun()
    
    # Aktueller Reifen
    current_tire = df.iloc[st.session_state.premium_current_index]
    
    # Dropdown für direkten Zugriff
    tire_options = []
    for i, (_, row) in enumerate(df.iterrows()):
        option_text = f"{i+1}: {row['Breite']}/{row['Hoehe']} R{row['Zoll']} - {row['Fabrikat']} {row['Profil']}"
        tire_options.append(option_text)
    
    selected_index = st.selectbox(
        "Reifen direkt auswählen:",
        options=range(len(tire_options)),
        index=st.session_state.premium_current_index,
        format_func=lambda x: tire_options[x],
        key="tire_selector"
    )
    
    if selected_index != st.session_state.premium_current_index:
        st.session_state.premium_current_index = selected_index
        st.rerun()
    
    # Bearbeitungsform
    col_info, col_edit = st.columns(2)
    
    with col_info:
        st.markdown("**Reifen-Information:**")
        st.write(f"**Größe:** {current_tire['Breite']}/{current_tire['Hoehe']} R{current_tire['Zoll']}")
        st.write(f"**Hersteller:** {current_tire['Fabrikat']}")
        st.write(f"**Profil:** {current_tire['Profil']}")
        st.write(f"**Teilenummer:** {current_tire['Teilenummer']}")
        st.write(f"**Aktueller Preis:** {current_tire['Preis_EUR']:.2f}€")
    
    with col_edit:
        st.markdown("**Bearbeitung:**")
        
        # Preis
        new_price = st.number_input(
            "Neuer Preis (€):",
            min_value=0.0,
            max_value=2000.0,
            value=float(current_tire['Preis_EUR']),
            step=0.01,
            key="edit_price"
        )
        
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
            key="edit_stock",
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
            key="edit_efficiency"
        )
        
        current_wet_grip = current_tire.get('Nasshaftung', '')
        wet_grip_index = efficiency_options.index(current_wet_grip) if current_wet_grip in efficiency_options else 0
        
        new_wet_grip = st.selectbox(
            "Nasshaftung:",
            options=efficiency_options,
            index=wet_grip_index,
            key="edit_wet_grip"
        )
        
        current_noise = current_tire.get('Geräuschklasse', 70)
        if pd.isna(current_noise):
            current_noise = 70
        
        new_noise = st.number_input(
            "Geräuschklasse (dB):",
            min_value=66,
            max_value=80,
            value=int(current_noise),
            step=1,
            key="edit_noise"
        )
    
    # Speichern Button
    col_save, col_delete = st.columns(2)
    
    with col_save:
        if st.button("💾 Änderungen speichern", use_container_width=True, type="primary"):
            # Reifen in Central DB aktualisieren
            updated_row = {
                'Preis_EUR': new_price,
                'Bestand': new_stock,
                'Kraftstoffeffizienz': new_efficiency,
                'Nasshaftung': new_wet_grip,
                'Geräuschklasse': new_noise if new_noise > 0 else None
            }
            
            success, message = data_manager.update_tire_stock(
                current_tire['Teilenummer'], 
                0,  # Keine Bestandsänderung hier
                "central"
            )
            
            # Reifen zu Central DB hinzufügen/aktualisieren
            tire_df = pd.DataFrame([current_tire])
            for col, value in updated_row.items():
                tire_df[col] = value
            
            success, count = data_manager.add_or_update_central_data(tire_df)
            
            if success:
                st.success("✅ Reifen erfolgreich aktualisiert!")
                # Working data aktualisieren
                st.session_state.premium_working_data.iloc[st.session_state.premium_current_index] = tire_df.iloc[0]
            else:
                st.error("❌ Fehler beim Speichern!")
    
    with col_delete:
        if st.button("🗑️ Aus Bearbeitung entfernen", use_container_width=True, type="secondary"):
            # Aus Working Data entfernen
            st.session_state.premium_working_data = st.session_state.premium_working_data.drop(
                st.session_state.premium_working_data.index[st.session_state.premium_current_index]
            ).reset_index(drop=True)
            
            if st.session_state.premium_current_index >= len(st.session_state.premium_working_data):
                st.session_state.premium_current_index = max(0, len(st.session_state.premium_working_data) - 1)
            
            st.success("✅ Reifen aus Bearbeitung entfernt!")
            st.rerun()

def render_service_management():
    """Rendert Service-Preise Verwaltung"""
    st.markdown("### ⚙️ Service-Preise verwalten")
    st.markdown("Hier können die Preise für Montage, Radwechsel und Einlagerung angepasst werden.")
    
    # Services laden
    services_df = st.session_state.services_config
    
    # Aktuelle Preise in Dictionary
    current_prices = {}
    for _, row in services_df.iterrows():
        current_prices[row['service_name']] = float(row['price'])
    
    # Eingabefelder
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
    
    # Speichern
    if st.button("💾 Preise speichern", use_container_width=True, type="primary"):
        new_prices = {
            'montage_bis_17': montage_17,
            'montage_18_19': montage_18,
            'montage_ab_20': montage_20,
            'radwechsel_1_rad': radwechsel_1,
            'radwechsel_2_raeder': radwechsel_2,
            'radwechsel_3_raeder': radwechsel_3,
            'radwechsel_4_raeder': radwechsel_4,
            'nur_einlagerung': einlagerung
        }
        
        if data_manager.update_service_prices(new_prices):
            st.success("✅ Service-Preise erfolgreich aktualisiert!")
        else:
            st.error("❌ Fehler beim Speichern der Service-Preise!")

def render_stock_management():
    """Rendert Bestandsmanagement"""
    st.markdown("### 📦 Bestandsmanagement & Nachbestellungen")
    st.markdown("Überblick über Lagerbestände und automatische Nachbestelllisten.")
    
    # Kombinierte Daten laden
    all_data = data_manager.get_combined_data()
    
    if all_data.empty:
        st.warning("Keine Daten für Bestandsanalyse verfügbar.")
        return
    
    # Bestandsstatistiken
    stats = calculate_stock_statistics(all_data)
    
    st.markdown("**📊 Bestandsübersicht:**")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(create_metric_card("Reifen gesamt", str(stats['total'])), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Mit Bestandsinfo", str(stats['with_stock'])), unsafe_allow_html=True)
    with col3:
        if stats['negative'] > 0:
            st.markdown(create_metric_card("🔴 Nachbestellung", str(stats['negative'])), unsafe_allow_html=True)
        else:
            st.markdown(create_metric_card("✅ Kein Nachbedarf", str(stats['negative'])), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("🟡 Bestand = 0", str(stats['zero'])), unsafe_allow_html=True)
    with col5:
        st.markdown(create_metric_card("🟢 Verfügbar", str(stats['positive'])), unsafe_allow_html=True)
    
    # Gesamtbestand
    if stats['total_stock'] < 0:
        st.error(f"⚠️ Gesamtbestand: {stats['total_stock']:.0f} (Negative Bilanz!)")
    else:
        st.success(f"✅ Gesamtbestand: {stats['total_stock']:.0f}")
    
    # Nachbestellliste
    if stats['negative'] > 0:
        render_reorder_list(all_data)
    else:
        st.success("✅ Alle Reifen sind ausreichend auf Lager!")

def calculate_stock_statistics(df):
    """Berechnet Bestandsstatistiken"""
    stats = {
        'total': len(df),
        'with_stock': len(df[df['Bestand'].notna()]),
        'no_info': len(df[df['Bestand'].isna()]),
        'negative': 0,
        'zero': 0,
        'positive': 0,
        'total_stock': 0
    }
    
    if 'Bestand' in df.columns:
        stock_data = df[df['Bestand'].notna()]
        stats['negative'] = len(stock_data[stock_data['Bestand'] < 0])
        stats['zero'] = len(stock_data[stock_data['Bestand'] == 0])
        stats['positive'] = len(stock_data[stock_data['Bestand'] > 0])
        stats['total_stock'] = stock_data['Bestand'].sum()
    
    return stats

def render_reorder_list(df):
    """Rendert Nachbestellliste"""
    st.markdown("---")
    st.markdown("#### ⚠️ Reifen mit Nachbedarf")
    
    negative_stock_df = df[
        (df['Bestand'].notna()) & 
        (df['Bestand'] < 0)
    ].copy()
    
    if not negative_stock_df.empty:
        st.markdown(f"**{len(negative_stock_df)} Reifen-Typen benötigen Nachbestellung:**")
        
        # Nach Nachbedarf sortieren
        negative_stock_df = negative_stock_df.sort_values('Bestand')
        
        # Top 10 anzeigen
        for idx, row in negative_stock_df.head(10).iterrows():
            reifengroesse = f"{row['Breite']}/{row['Hoehe']} R{row['Zoll']}"
            bestand = int(row['Bestand'])
            nachbedarf = abs(bestand)
            
            col_info, col_details = st.columns([3, 1])
            with col_info:
                st.markdown(f"🔴 **{reifengroesse}** - {row['Fabrikat']} {row['Profil']}")
                st.markdown(f"Teilenummer: {row['Teilenummer']} | Einzelpreis: {row['Preis_EUR']:.2f}€")
            with col_details:
                st.metric("Rückstand", f"{nachbedarf} Stück")
                st.metric("Bestellwert", f"{nachbedarf * row['Preis_EUR']:.2f}€")
        
        if len(negative_stock_df) > 10:
            st.info(f"... und {len(negative_stock_df) - 10} weitere Reifen mit Nachbedarf")
        
        # Export-Option
        if st.button("📥 Nachbestellliste als CSV exportieren", type="primary"):
            csv_data, filename = data_manager.export_to_csv("central")
            if csv_data:
                st.download_button(
                    label="📋 Download CSV",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()