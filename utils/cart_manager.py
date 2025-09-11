import streamlit as st
import pandas as pd
from datetime import datetime
from .data_manager import data_manager

class CartManager:
    """Warenkorb Manager für die Cloud-Version"""
    
    def __init__(self):
        self.init_session_state()
    
    def init_session_state(self):
        """Initialisiert Warenkorb Session State"""
        if 'cart_items' not in st.session_state:
            st.session_state.cart_items = []
        if 'cart_quantities' not in st.session_state:
            st.session_state.cart_quantities = {}
        if 'cart_services' not in st.session_state:
            st.session_state.cart_services = {}
        if 'cart_count' not in st.session_state:
            st.session_state.cart_count = 0
    
    def add_to_cart(self, tire_data, quantity=4, services=None):
        """Fügt einen Reifen zum Warenkorb hinzu"""
        tire_id = f"{tire_data['Teilenummer']}_{tire_data['Preis_EUR']}"
        
        # Prüfen ob bereits im Warenkorb
        for item in st.session_state.cart_items:
            if item['id'] == tire_id:
                return False, "Reifen bereits im Warenkorb"
        
        # Warenkorb-Item erstellen
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
            'Nasshaftung': tire_data.get('Nasshaftung', '')
        }
        
        # Standard Services wenn nicht angegeben
        if services is None:
            services = {
                'montage': True,
                'radwechsel': False,
                'radwechsel_type': '4_raeder',
                'einlagerung': False
            }
        
        # Zum Warenkorb hinzufügen
        st.session_state.cart_items.append(cart_item)
        st.session_state.cart_quantities[tire_id] = quantity
        st.session_state.cart_services[tire_id] = services
        self.update_cart_count()
        
        return True, f"{quantity}x {cart_item['Reifengröße']} hinzugefügt"
    
    def remove_from_cart(self, tire_id):
        """Entfernt einen Reifen aus dem Warenkorb"""
        st.session_state.cart_items = [item for item in st.session_state.cart_items if item['id'] != tire_id]
        if tire_id in st.session_state.cart_quantities:
            del st.session_state.cart_quantities[tire_id]
        if tire_id in st.session_state.cart_services:
            del st.session_state.cart_services[tire_id]
        self.update_cart_count()
    
    def clear_cart(self):
        """Leert den kompletten Warenkorb"""
        st.session_state.cart_items = []
        st.session_state.cart_quantities = {}
        st.session_state.cart_services = {}
        st.session_state.cart_count = 0
    
    def update_cart_count(self):
        """Aktualisiert die Warenkorb-Anzahl"""
        st.session_state.cart_count = len(st.session_state.cart_items)
    
    def get_cart_total(self):
        """Berechnet Warenkorb-Gesamtsumme"""
        if not st.session_state.cart_items:
            return 0.0, {}
        
        service_prices = data_manager.get_service_prices()
        total = 0.0
        breakdown = {'reifen': 0.0, 'montage': 0.0, 'radwechsel': 0.0, 'einlagerung': 0.0}
        
        for item in st.session_state.cart_items:
            tire_id = item['id']
            quantity = st.session_state.cart_quantities.get(tire_id, 4)
            
            # Reifen-Kosten
            reifen_kosten = item['Preis_EUR'] * quantity
            total += reifen_kosten
            breakdown['reifen'] += reifen_kosten
            
            # Services für diesen Reifen
            item_services = st.session_state.cart_services.get(tire_id, {})
            
            # Montage-Kosten
            if item_services.get('montage', False):
                zoll_size = item['Zoll']
                if zoll_size <= 17:
                    montage_preis = service_prices.get('montage_bis_17', 25.0)
                elif zoll_size <= 19:
                    montage_preis = service_prices.get('montage_18_19', 30.0)
                else:
                    montage_preis = service_prices.get('montage_ab_20', 40.0)
                
                montage_kosten = montage_preis * quantity
                total += montage_kosten
                breakdown['montage'] += montage_kosten
            
            # Radwechsel-Kosten
            if item_services.get('radwechsel', False):
                radwechsel_type = item_services.get('radwechsel_type', '4_raeder')
                
                if radwechsel_type == '1_rad':
                    radwechsel_kosten = service_prices.get('radwechsel_1_rad', 9.95)
                elif radwechsel_type == '2_raeder':
                    radwechsel_kosten = service_prices.get('radwechsel_2_raeder', 19.95)
                elif radwechsel_type == '3_raeder':
                    radwechsel_kosten = service_prices.get('radwechsel_3_raeder', 29.95)
                else:  # '4_raeder'
                    radwechsel_kosten = service_prices.get('radwechsel_4_raeder', 39.90)
                
                total += radwechsel_kosten
                breakdown['radwechsel'] += radwechsel_kosten
            
            # Einlagerungs-Kosten
            if item_services.get('einlagerung', False):
                einlagerungs_kosten = service_prices.get('nur_einlagerung', 55.00)
                total += einlagerungs_kosten
                breakdown['einlagerung'] += einlagerungs_kosten
        
        return total, breakdown
    
    def create_professional_offer(self, customer_data=None):
        """Erstellt professionelles Angebot"""
        if not st.session_state.cart_items:
            return "Warenkorb ist leer"
        
        total, breakdown = self.get_cart_total()
        service_prices = data_manager.get_service_prices()
        
        content = []
        
        # Header
        content.append("AUTOHAUS RAMSPERGER")
        content.append("Kostenvoranschlag für Winterreifen")
        content.append("=" * 60)
        content.append(f"Datum: {datetime.now().strftime('%d.%m.%Y')}")
        content.append("")
        
        # Kundendaten
        if customer_data and any(customer_data.values()):
            content.append("KUNDENDATEN:")
            content.append("-" * 30)
            if customer_data.get('name'):
                content.append(f"Kunde: {customer_data['name']}")
            if customer_data.get('kennzeichen'):
                content.append(f"Kennzeichen: {customer_data['kennzeichen']}")
            if customer_data.get('modell'):
                content.append(f"Fahrzeug: {customer_data['modell']}")
            if customer_data.get('fahrgestellnummer'):
                content.append(f"Fahrgestellnummer: {customer_data['fahrgestellnummer']}")
            content.append("")
        
        # Anrede
        content.append("Sehr geehrter Kunde,")
        content.append("")
        content.append("der Sommer geht langsam zu Ende und die Zeichen stehen auf Winter.")
        content.append("Jetzt wird es auch Zeit für Ihre Winterreifen von Ihrem Auto.")
        content.append("Gerne stelle ich Ihnen hochwertige Reifenmodelle vor, die perfekt")
        content.append("zu Ihren Anforderungen passen:")
        content.append("")
        
        # Reifen-Details
        content.append("IHRE REIFENAUSWAHL:")
        content.append("=" * 60)
        
        for i, item in enumerate(st.session_state.cart_items, 1):
            tire_id = item['id']
            qty = st.session_state.cart_quantities.get(tire_id, 4)
            einzelpreis = item['Preis_EUR']
            reifen_gesamtpreis = einzelpreis * qty
            
            content.append(f"REIFEN {i}:")
            content.append("-" * 30)
            content.append(f"Größe: {item['Reifengröße']}")
            content.append(f"Marke: {item['Fabrikat']} {item['Profil']}")
            content.append(f"Teilenummer: {item['Teilenummer']}")
            
            # EU-Label
            if item.get('Kraftstoffeffizienz') or item.get('Nasshaftung'):
                label_info = []
                if item.get('Kraftstoffeffizienz'):
                    label_info.append(f"Kraftstoff: {item['Kraftstoffeffizienz']}")
                if item.get('Nasshaftung'):
                    label_info.append(f"Nasshaftung: {item['Nasshaftung']}")
                content.append(f"EU-Label: {' | '.join(label_info)}")
            
            content.append(f"Stückzahl: {qty} Reifen")
            content.append(f"Einzelpreis: {einzelpreis:.2f}€")
            content.append(f"Reifen-Summe: {reifen_gesamtpreis:.2f}€")
            content.append("")
            
            # Services für diesen Reifen
            item_services = st.session_state.cart_services.get(tire_id, {})
            service_kosten = 0.0
            
            if item_services.get('montage', False):
                zoll_size = item['Zoll']
                if zoll_size <= 17:
                    montage_price = service_prices.get('montage_bis_17', 25.0)
                    montage_text = "Reifenservice bis 17 Zoll"
                elif zoll_size <= 19:
                    montage_price = service_prices.get('montage_18_19', 30.0)
                    montage_text = "Reifenservice 18-19 Zoll"
                else:
                    montage_price = service_prices.get('montage_ab_20', 40.0)
                    montage_text = "Reifenservice ab 20 Zoll"
                
                montage_gesamt = montage_price * qty
                service_kosten += montage_gesamt
                content.append(f"+ {montage_text}: {qty}x {montage_price:.2f}€ = {montage_gesamt:.2f}€")
            
            if item_services.get('radwechsel', False):
                radwechsel_type = item_services.get('radwechsel_type', '4_raeder')
                
                if radwechsel_type == '1_rad':
                    radwechsel_preis = service_prices.get('radwechsel_1_rad', 9.95)
                    radwechsel_text = "Radwechsel 1 Rad"
                elif radwechsel_type == '2_raeder':
                    radwechsel_preis = service_prices.get('radwechsel_2_raeder', 19.95)
                    radwechsel_text = "Radwechsel 2 Räder"
                elif radwechsel_type == '3_raeder':
                    radwechsel_preis = service_prices.get('radwechsel_3_raeder', 29.95)
                    radwechsel_text = "Radwechsel 3 Räder"
                else:
                    radwechsel_preis = service_prices.get('radwechsel_4_raeder', 39.90)
                    radwechsel_text = "Radwechsel 4 Räder"
                
                service_kosten += radwechsel_preis
                content.append(f"+ {radwechsel_text}: {radwechsel_preis:.2f}€")
            
            if item_services.get('einlagerung', False):
                einlagerung_preis = service_prices.get('nur_einlagerung', 55.00)
                service_kosten += einlagerung_preis
                content.append(f"+ Einlagerung: {einlagerung_preis:.2f}€")
            
            # Zwischensumme
            reifen_total = reifen_gesamtpreis + service_kosten
            content.append("")
            content.append(f"ZWISCHENSUMME REIFEN {i}: {reifen_total:.2f}€")
            content.append("=" * 30)
            content.append("")
        
        # Gesamtübersicht
        content.append("GESAMTÜBERSICHT:")
        content.append("=" * 30)
        content.append(f"Reifen-Kosten gesamt: {breakdown['reifen']:.2f}€")
        
        if breakdown['montage'] > 0:
            content.append(f"Service-Leistungen gesamt: {breakdown['montage'] + breakdown['radwechsel'] + breakdown['einlagerung']:.2f}€")
        
        content.append("")
        content.append("*" * 60)
        content.append(f"GESAMTSUMME: {total:.2f}€")
        content.append("*" * 60)
        content.append("")
        
        # Abschluss
        content.append("Gerne stehen wir Ihnen für Rückfragen zur Verfügung.")
        content.append("Wir freuen uns auf Ihren Auftrag!")
        content.append("")
        content.append("Mit freundlichen Grüßen")
        content.append("Autohaus Ramsperger")
        
        return "\n".join(content)
    
    def process_checkout(self, reduce_stock=False):
        """Verarbeitet Warenkorb-Checkout (optional mit Bestandsreduktion)"""
        if not st.session_state.cart_items:
            return False, "Warenkorb ist leer"
        
        if reduce_stock:
            # Bestände reduzieren
            success_count = 0
            for item in st.session_state.cart_items:
                tire_id = item['id']
                quantity = st.session_state.cart_quantities.get(tire_id, 4)
                
                success, message = data_manager.update_tire_stock(
                    item['Teilenummer'], 
                    -quantity,  # Negative Reduktion
                    "central"   # Aus Central DB reduzieren
                )
                
                if success:
                    success_count += 1
            
            return success_count > 0, f"{success_count} Reifen-Bestände aktualisiert"
        
        return True, "Checkout erfolgreich"

# Globale Instanz
cart_manager = CartManager()