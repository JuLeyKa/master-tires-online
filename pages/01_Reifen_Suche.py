import streamlit as st
import pandas as pd
from utils import data_manager, cart_manager, apply_main_css, get_efficiency_emoji, get_stock_display, create_metric_card

# Page Config
st.set_page_config(
    page_title="Reifen Suche - Ramsperger",
    page_icon="🔍",
    layout="wide"
)

# CSS anwenden
apply_main_css()

def init_session_state():
    """Initialisiert Session State für Reifen Suche"""
    if 'selected_size' not in st.session_state:
        st.session_state.selected_size = None
    if 'opened_tire_cards' not in st.session_state:
        st.session_state.opened_tire_cards = set()
    if 'mit_bestand_filter' not in st.session_state:
        st.session_state.mit_bestand_filter = True

def main():
    init_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Reifen Suche</h1>
        <p>Finde die perfekten Reifen für deine Kunden</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Daten laden
    df = data_manager.get_combined_data()
    if df.empty:
        st.warning("Keine Reifen-Daten verfügbar. Bitte lade Daten in der Datenbank-Verwaltung hoch.")
        st.stop()
    
    # Info über Datenquellen
    master_count = len(st.session_state.master_data) if not st.session_state.master_data.empty else 0
    central_count = len(st.session_state.central_data) if not st.session_state.central_data.empty else 0
    
    st.markdown(f"""
    <div class="info-box">
        <h4>📊 Datenquellen</h4>
        <p>{master_count} Reifen aus Master-Daten + {central_count} bearbeitete Reifen = <strong>{len(df)} gesamt</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Filter
    with st.sidebar:
        st.header("🔍 Detailfilter")
        
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
        hoehe_filter = st.selectbox("Höhe (%)", options=hoehe_opt, index=0)
        fabrikat = st.selectbox("Fabrikat", options=fabrikat_opt, index=0)
        
        loadindex_opt = ["Alle"] + sorted([x for x in df["Loadindex"].dropna().astype(str).unique().tolist()])
        speedindex_opt = ["Alle"] + sorted([x for x in df["Speedindex"].dropna().astype(str).unique().tolist()])
        
        loadindex_filter = st.selectbox("Loadindex", options=loadindex_opt, index=0)
        speedindex_filter = st.selectbox("Speedindex", options=speedindex_opt, index=0)
        
        # Preisbereich
        min_price = float(df["Preis_EUR"].min())
        max_price = float(df["Preis_EUR"].max())
        min_preis, max_preis = st.slider(
            "Preisbereich (€)",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price),
            step=5.0,
        )
        
        # Sortierung
        sortierung = st.selectbox(
            "Sortieren nach",
            options=["Preis aufsteigend", "Preis absteigend", "Fabrikat", "Reifengröße"],
        )
        
        # Statistiken
        show_stats = st.checkbox("📊 Statistiken anzeigen", value=False)
        
        # Navigation zu anderen Bereichen
        st.markdown("---")
        
        if st.button("🛒 Zum Warenkorb", use_container_width=True, type="primary"):
            st.switch_page("pages/02_Warenkorb.py")
        
        if st.button(⚙️ Premium Verwaltung", use_container_width=True, type="secondary"):
            st.switch_page("pages/03_Premium_Verwaltung.py")
        
        if st.button("🗄️ Datenbank Verwaltung", use_container_width=True, type="secondary"):
            st.switch_page("pages/04_Datenbank_Verwaltung.py")
    
    # Schnellauswahl für gängige Reifengrößen
    st.subheader("🚀 Schnellauswahl – gängige Reifengrößen")
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
            <h4>🎯 Schnellauswahl aktiv: {st.session_state.selected_size}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("❌ Schnellauswahl zurücksetzen"):
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
    elif sortierung == "Reifengröße":
        filtered = filtered.sort_values(["Zoll", "Breite", "Hoehe", "Preis_EUR"])
    
    # Gefundene Reifen anzeigen
    if len(filtered) > 0:
        st.markdown("---")
        
        # Info über Bestandsfilter
        if mit_bestand:
            st.subheader(f"🎯 Gefundene Reifen mit Bestand: {len(filtered)}")
            if len(df) > len(filtered):
                nicht_auf_lager = len(df) - len(filtered)
                st.markdown(f"""
                <div class="info-box">
                    <p>ℹ️ {nicht_auf_lager} weitere Reifen ohne Lagerbestand verfügbar (Bestandsfilter deaktivieren)</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.subheader(f"🎯 Gefundene Reifen: {len(filtered)}")
        
        # Reifen-Liste
        render_tire_list(filtered)
        
        # Statistiken
        if show_stats:
            render_statistics(filtered)
    else:
        if mit_bestand:
            st.warning("⚠️ Keine Reifen mit Bestand gefunden. Bitte Filter anpassen oder Bestandsfilter deaktivieren.")
        else:
            st.warning("⚠️ Keine Reifen gefunden. Bitte Filter anpassen oder andere Reifengröße wählen.")
    
    # Legende
    render_legend(mit_bestand)

def render_tire_list(filtered_df):
    """Rendert die Reifen-Liste mit Auswahl-Buttons"""
    display = filtered_df.copy().reset_index(drop=True)
    display["Reifengröße"] = (
        display["Breite"].astype(str) + "/" + display["Hoehe"].astype(str) + " R" + display["Zoll"].astype(str)
    )
    display["Kraftstoff"] = display["Kraftstoffeffizienz"].apply(lambda x: f"{get_efficiency_emoji(x)} {x}" if pd.notna(x) else "")
    display["Nasshaft."] = display["Nasshaftung"].apply(lambda x: f"{get_efficiency_emoji(x)} {x}" if pd.notna(x) else "")
    display["Preis €"] = display["Preis_EUR"].apply(lambda x: f"{float(x):.2f} €")
    display["Bestand"] = display["Bestand"].apply(get_stock_display)
    
    st.markdown("**Reifen auswählen und konfigurieren:**")
    
    for idx, row in display.iterrows():
        col_info, col_button = st.columns([5, 1])
        
        with col_info:
            # Kompakte Reifen-Info
            effi_display = f" {row['Kraftstoff']}" if row['Kraftstoff'] else ""
            nasshaft_display = f" {row['Nasshaft.']}" if row['Nasshaft.'] else ""
            bestand_display = f" (Bestand: {row['Bestand']})" if row['Bestand'] != "❓ unbekannt" else ""
            
            st.write(f"**{row['Reifengröße']}** - {row['Fabrikat']} {row['Profil']} - **{row['Preis €']}**{bestand_display}{effi_display}{nasshaft_display} - {row['Teilenummer']}")
        
        with col_button:
            card_key = f"tire_card_{idx}"
            is_open = card_key in st.session_state.opened_tire_cards
            
            if st.button("🛒 Auswählen" if not is_open else "❌ Schließen", 
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

def render_config_card(row, idx, filtered_df):
    """Rendert die Konfigurationskarte für einen Reifen"""
    st.markdown(f"""
    <div class="config-card">
    """, unsafe_allow_html=True)
    
    st.markdown(f"**Konfiguration für {row['Reifengröße']} - {row['Fabrikat']} {row['Profil']}**")
    
    col_config1, col_config2 = st.columns(2)
    
    with col_config1:
        # Stückzahl
        quantity = st.number_input(
            "Stückzahl:",
            min_value=1,
            max_value=8,
            value=4,
            step=1,
            key=f"qty_{idx}",
            help="Anzahl der Reifen (1-8 Stück)"
        )
        
        # Gesamtpreis anzeigen
        total_price = row['Preis_EUR'] * quantity
        st.metric("Reifen-Gesamtpreis", f"{total_price:.2f} €")
    
    with col_config2:
        st.markdown("**Service-Leistungen:**")
        
        # Service-Preise laden
        service_prices = data_manager.get_service_prices()
        
        # Montage-Preis basierend auf Zoll-Größe
        zoll_size = row['Zoll']
        if zoll_size <= 17:
            montage_price = service_prices.get('montage_bis_17', 25.0)
            montage_label = f"Reifenservice bis 17 Zoll ({montage_price:.2f}€ pro Reifen)"
        elif zoll_size <= 19:
            montage_price = service_prices.get('montage_18_19', 30.0)
            montage_label = f"Reifenservice 18-19 Zoll ({montage_price:.2f}€ pro Reifen)"
        else:
            montage_price = service_prices.get('montage_ab_20', 40.0)
            montage_label = f"Reifenservice ab 20 Zoll ({montage_price:.2f}€ pro Reifen)"
        
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
            with st.expander("🔧 Radwechsel-Optionen", expanded=True):
                radwechsel_options = [
                    ('4_raeder', f"4 Räder ({service_prices.get('radwechsel_4_raeder', 39.90):.2f}€)"),
                    ('3_raeder', f"3 Räder ({service_prices.get('radwechsel_3_raeder', 29.95):.2f}€)"),
                    ('2_raeder', f"2 Räder ({service_prices.get('radwechsel_2_raeder', 19.95):.2f}€)"),
                    ('1_rad', f"1 Rad ({service_prices.get('radwechsel_1_rad', 9.95):.2f}€)")
                ]
                
                radwechsel_type = st.radio(
                    "Anzahl Räder:",
                    options=[opt[0] for opt in radwechsel_options],
                    format_func=lambda x: next(opt[1] for opt in radwechsel_options if opt[0] == x),
                    key=f"radwechsel_type_{idx}",
                    index=0
                )
        
        # Einlagerung
        einlagerung_selected = st.checkbox(
            f"Nur Einlagerung (+{service_prices.get('nur_einlagerung', 55.00):.2f}€)",
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
            st.metric("Service-Kosten", f"{service_total:.2f} €")
    
    # Gesamtsumme
    grand_total = total_price + service_total
    st.markdown(f"### **Gesamtsumme: {grand_total:.2f} €**")
    
    # Action Buttons
    col_add, col_cancel = st.columns(2)
    
    with col_add:
        if st.button("🛒 In Warenkorb legen", 
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
            success, message = cart_manager.add_to_cart(tire_data, quantity, service_config)
            
            if success:
                st.success(message)
                # Karte schließen
                card_key = f"tire_card_{idx}"
                st.session_state.opened_tire_cards.discard(card_key)
                st.rerun()
            else:
                st.warning(message)
    
    with col_cancel:
        if st.button("❌ Abbrechen", 
                   key=f"cancel_{idx}", 
                   use_container_width=True):
            card_key = f"tire_card_{idx}"
            st.session_state.opened_tire_cards.discard(card_key)
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_statistics(filtered_df):
    """Rendert Statistiken"""
    st.subheader("📊 Statistiken")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_price = filtered_df['Preis_EUR'].mean()
        st.markdown(create_metric_card("Durchschnittspreis", f"{avg_price:.2f} €"), unsafe_allow_html=True)
    
    with col2:
        min_price = filtered_df['Preis_EUR'].min()
        st.markdown(create_metric_card("Günstigster Reifen", f"{min_price:.2f} €"), unsafe_allow_html=True)
    
    with col3:
        max_price = filtered_df['Preis_EUR'].max()
        st.markdown(create_metric_card("Teuerster Reifen", f"{max_price:.2f} €"), unsafe_allow_html=True)
    
    with col4:
        unique_sizes = len(filtered_df[["Breite", "Hoehe", "Zoll"]].drop_duplicates())
        st.markdown(create_metric_card("Verfügbare Größen", str(unique_sizes)), unsafe_allow_html=True)

def render_legend(mit_bestand):
    """Rendert die Legende"""
    st.markdown("---")
    st.markdown("**Legende:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**⚡ Speedindex (max. zulässige Geschwindigkeit):**")
        st.markdown("R = 170 km/h | S = 180 km/h | T = 190 km/h | H = 210 km/h | V = 240 km/h")
    
    with col2:
        st.markdown("**Reifengröße:** Breite/Höhe R Zoll")
        st.markdown("**Loadindex:** Tragfähigkeit pro Reifen in kg")
        st.markdown("**Bestand:** ⚠️ Nachbestellung nötig | ⚪ Null | ✅ Verfügbar | ❓ Unbekannt")
        if mit_bestand:
            st.markdown("**🎯 Bestandsfilter aktiv** - Nur Reifen mit Lagerbestand angezeigt")

if __name__ == "__main__":
    main()