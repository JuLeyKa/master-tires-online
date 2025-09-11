# 🚗 Ramsperger Reifen System - Cloud Edition

Ein professionelles Reifenmanagement-System für Autohaus Ramsperger, optimiert für Streamlit Cloud mit echten Produktionsdaten.

## 📋 Features

### 🔍 Intelligente Reifen-Suche
- **Schnellauswahl** für gängige Reifengrößen (195/65 R15, 205/55 R16, etc.)
- **Detailfilter** nach Hersteller, Größe, Preis, Speedindex, Loadindex
- **Bestandsfilter** - nur Reifen mit positivem Lagerbestand anzeigen
- **EU-Label Informationen** - Kraftstoffeffizienz und Nasshaftung
- **Sortierung** nach Preis, Hersteller oder Reifengröße

### 🛒 Professioneller Warenkorb
- **Individuelle Service-Konfiguration** pro Reifen-Typ
- **Dynamische Preisberechnung** basierend auf Zoll-Größe
- **Radwechsel-Optionen** - 1, 2, 3 oder 4 Räder
- **Kundenspezifische Daten** für personalisierte Angebote
- **Automatische Angebotserstellung** im Briefformat

### ⚙️ Premium Verwaltung (Admin)
- **EU-Label Eingabe** - Kraftstoffeffizienz, Nasshaftung, Geräuschklasse
- **Preismanagement** - individuelle Preisanpassungen
- **Bestandsmanagement** - inklusive negativer Bestände für Nachbestellungen
- **Service-Preise verwalten** - Montage, Radwechsel, Einlagerung
- **Excel/CSV Import** für Massendaten-Updates

### 🗄️ Datenbank Verwaltung (Admin)
- **Vollzugriff** auf alle Datenbanken (Master, Zentral, Kombiniert)
- **Import/Export** Funktionen für CSV und Excel
- **Backup-Erstellung** mit Zeitstempel
- **Datenbank-Operationen** - Leeren, Neu laden, Cache verwalten
- **Bestandsstatistiken** und Nachbestelllisten

## 🗂️ Datenstruktur

### Produktionsdaten
Das System verwendet echte Produktionsdaten:

```
data/
├── 2025-07-29_ReifenPremium_Winterreifen_2025-26.xlsx    # Premium Excel-Daten
├── Ramsperger_Winterreifen_20250826_160010.csv          # Master-CSV (Basis)
├── ramsperger_central_database.csv                      # Zentrale Datenbank
└── ramsperger_services_config.csv                       # Service-Konfiguration
```

### Datenbanklogik
- **Master-CSV**: Unveränderliche Basis-Reifendaten (`Ramsperger_Winterreifen_20250826_160010.csv`)
- **Zentrale DB**: Bearbeitete Reifen mit EU-Labels und Beständen (`ramsperger_central_database.csv`)
- **Premium Excel**: Spezielle Reifen für Premium-Verwaltung (`2025-07-29_ReifenPremium_Winterreifen_2025-26.xlsx`)
- **Services**: Konfiguierbare Preise für Montage/Radwechsel (`ramsperger_services_config.csv`)

## 🏗️ Technische Architektur

### Projektstruktur
```
Master_Tires_Online/
├── app.py                          # Haupteinstieg
├── requirements.txt                # Python Dependencies
├── .streamlit/
│   └── config.toml                # Streamlit Konfiguration
├── pages/                         # Multi-page App
│   ├── 01_🔍_Reifen_Suche.py
│   ├── 02_🛒_Warenkorb.py
│   ├── 03_⚙️_Premium_Verwaltung.py
│   └── 04_🗄️_Datenbank_Verwaltung.py
├── utils/                         # Helper Module
│   ├── __init__.py
│   ├── data_manager.py           # Datenbank-Manager
│   ├── cart_manager.py           # Warenkorb-Logik
│   └── styles.py                 # CSS Styles
├── data/                         # ECHTE PRODUKTIONSDATEN
│   ├── 2025-07-29_ReifenPremium_Winterreifen_2025-26.xlsx
│   ├── Ramsperger_Winterreifen_20250826_160010.csv
│   ├── ramsperger_central_database.csv
│   └── ramsperger_services_config.csv
├── README.md                     # Diese Datei
└── .gitignore                   # Git Ignore
```

### Intelligente Datenladung
- **Automatisches Laden** der echten Dateien beim App-Start
- **Fallback-Mechanismus** falls Dateien fehlen
- **Persistierung** aller Änderungen zurück in die CSV-Dateien
- **Backup-Funktionen** für Datensicherheit

### Service-System
- **Dynamische Preisberechnung** basierend auf Zoll-Größe:
  - Bis 17 Zoll: 25,00€ pro Reifen
  - 18-19 Zoll: 30,00€ pro Reifen  
  - Ab 20 Zoll: 40,00€ pro Reifen
- **Flexible Radwechsel-Optionen**: 1-4 Räder mit individueller Preisgestaltung
- **Einlagerung**: Pauschalpreis 55,00€

## 🚀 Installation & Deployment

### Lokale Entwicklung

1. **Repository klonen**
```bash
git clone [your-repo-url]
cd Master_Tires_Online
```

2. **Abhängigkeiten installieren**
```bash
pip install -r requirements.txt
```

3. **App starten**
```bash
streamlit run app.py
```

### Streamlit Cloud Deployment

1. **GitHub Repository erstellen**
   - Repository auf GitHub erstellen
   - Code hochladen

2. **Streamlit Cloud verbinden**
   - Bei [share.streamlit.io](https://share.streamlit.io) anmelden
   - "New app" → GitHub Repository auswählen
   - `app.py` als Main file angeben

3. **Automatisches Deployment**
   - Streamlit Cloud deployt automatisch bei GitHub Push
   - App ist unter `https://[app-name].streamlit.app` erreichbar

## 📊 Datenmanagement für Cloud

### CSV Export/Import Workflow

Da Streamlit Cloud keine persistente Dateispeicherung bietet, nutzt die App diesen Workflow:

1. **Daten bearbeiten** in der Premium-/Datenbank-Verwaltung
2. **CSV exportieren** über die Export-Funktionen
3. **Lokale Datei** via Terminal zu GitHub pushen:
```bash
git add data/updated_data.csv
git commit -m "Datenbank Update"
git push origin main
```
4. **Automatisches Redeploy** durch Streamlit Cloud

### Datenbank-Backup

```bash
# Regelmäßige Backups erstellen
# über die App: Datenbank Verwaltung → Backup erstellen
# Backup-Dateien haben Zeitstempel: Backup_central_20241201_143022.csv
```

## 🔐 Sicherheit

### Passwort-Schutz
- **Standard-PIN**: `1234` (für Demo-Zwecke)
- **Admin-Bereiche**: Premium Verwaltung und Datenbank Verwaltung
- **Session-basiert**: Logout beim Tab-Wechsel

### Produktive Nutzung
Für den produktiven Einsatz sollten Sie:
1. **PIN ändern** in den jeweiligen Admin-Check Funktionen
2. **Streamlit Secrets** für sichere Passwort-Speicherung nutzen
3. **HTTPS** durch Streamlit Cloud automatisch aktiviert

## 📱 Browser-Kompatibilität

Getestet und optimiert für:
- **Chrome** (empfohlen)
- **Firefox**
- **Safari**
- **Edge**

Mobile Ansicht unterstützt, Desktop empfohlen für Admin-Bereiche.

## 🛠️ Anpassungen

### Service-Preise ändern
1. **Premium Verwaltung** → Service-Preise
2. Preise anpassen und speichern
3. Änderungen gelten sofort app-weit

### Neue Reifendaten hinzufügen
1. **CSV/Excel vorbereiten** mit Spalten:
   - Breite, Hoehe, Zoll, Loadindex, Speedindex
   - Fabrikat, Profil, Teilenummer, Preis_EUR
   - Optional: Bestand, Kraftstoffeffizienz, Nasshaftung
2. **Datenbank Verwaltung** → Upload
3. **Export** der aktualisierten Datenbank
4. **GitHub Update** für persistente Speicherung

### CSS Anpassungen
Alle Styles befinden sich in `utils/styles.py`:
- **Farbschema** über CSS-Variablen anpassbar
- **Responsive Design** bereits implementiert
- **Corporate Design** einfach änderbar

## 🎯 Roadmap

### Version 1.1 (geplant)
- [ ] **Cloud-Datenbank Integration** (Supabase/PostgreSQL)
- [ ] **Multi-User Support** mit Benutzerrollen
- [ ] **API Integration** für Großhändler-Preise
- [ ] **PDF-Export** für Angebote

### Version 1.2 (geplant)
- [ ] **Kundenverwaltung** mit Historie
- [ ] **Automatische Nachbestellungen**
- [ ] **Statistik-Dashboard**
- [ ] **Mobile App** (Progressive Web App)

## 🐛 Bekannte Limitationen

1. **Keine persistente Speicherung** ohne manuellen Export/Import
2. **Session-basierte Daten** gehen bei Browser-Refresh verloren
3. **Single-User** - keine gleichzeitigen Bearbeitungen
4. **Upload-Limit**: 200MB (Streamlit Cloud Standard)

## 📞 Support

Bei Fragen oder Problemen:
1. **GitHub Issues** für Bug-Reports
2. **Dokumentation** in diesem README
3. **Code-Kommentare** in den Python-Dateien

## 📄 Lizenz

Proprietäre Software für Autohaus Ramsperger.
Alle Rechte vorbehalten.

---

**Entwickelt von Master Chief & Claude** 🤖  
*Professionelle Streamlit-Anwendungen für moderne Unternehmen*