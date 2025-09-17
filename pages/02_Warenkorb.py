import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import urllib.parse
import io
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Page Config
st.set_page_config(
    page_title="Warenkorb - Ramsperger",
    page_icon="🛒",
    layout="wide"
)

# ================================================================================================
# CSS STYLES - EINHEITLICH MIT REIFEN-SUCHE (OHNE CONTAINER-BOXEN)
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

    /* WICHTIG 1: Globale Reduktion des Top-Paddings für den Haupt-Content,
       damit das Logo höher startet (nahe der Sidebar-"app"-Zeile) */
    [data-testid="stAppViewContainer"] .block-container {
        padding-top: 0.5rem !important;   /* ggf. 0–1rem feinjustieren */
    }
    
    .main > div {
        padding-top: 0.2rem;
    }
    
    .stButton > button {
        border-radius: var(--border-radius); border: none; font-weight: 500; transition: all 0.2s ease;
        font-family: 'Inter', sans-serif;
    }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: var(--shadow-md); }
    
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 1.9rem 0 0.5rem 0;
        margin: 0; /* kein Margin-Konflikt */
    }

    /* WICHTIG 2: definierter Abstand NACH dem Logo – kollabiert nicht */
    .logo-spacer {
        height: 64px; /* -> bei Bedarf 48–80px anpassen */
    }
</style>
"""
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# ================================================================================================
# FESTE FILIAL- UND MITARBEITERDATEN (ERSETZT EXCEL-ANBINDUNG)
# ================================================================================================
def get_filial_data():
    """Gibt die fest definierte Filial- und Mitarbeiterstruktur zurück"""
    return {
        "vw_kh": {
            "filial_name": "KH - VW",
            "bereich": "VW",
            "adresse": "Hindenburgstr. 45 | 73230 Kirchheim",
            "zentrale": "07021/5001-100",
            "verteiler": "ma-vw-kh@ramsperger-automobile.de",
            "mitarbeiter": [
                {
                    "name": "ma-vw-kh@ramsperger-automobile.de",
                    "position": "Management E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "ma-vw-kh@ramsperger-automobile.de"
                },
                {
                    "name": "sb-vw-kh@ramsperger-automobile.de",
                    "position": "Serviceberatung Sammel-E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "sb-vw-kh@ramsperger-automobile.de"
                },
                {
                    "name": "td-vw-kh@ramsperger-automobile.de",
                    "position": "Teiledienst Sammel-E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "td-vw-kh@ramsperger-automobile.de"
                },
                {
                    "name": "Etienne Winkler",
                    "position": "Serviceberatung",
                    "durchwahl": "131",
                    "fax": "",
                    "mobil": "",
                    "email": "etienne.winkler@ramsperger-automobile.de"
                },
                {
                    "name": "Jonas Reich",
                    "position": "Serviceberatung",
                    "durchwahl": "138",
                    "fax": "",
                    "mobil": "",
                    "email": "jonas.reich@ramsperger-automobile.de"
                },
                {
                    "name": "Jürgen Nöpel",
                    "position": "Serviceberatung",
                    "durchwahl": "134",
                    "fax": "",
                    "mobil": "",
                    "email": "juergen.noepel@ramsperger-automobile.de"
                },
                {
                    "name": "Thomas Salomon",
                    "position": "Serviceberatung",
                    "durchwahl": "136",
                    "fax": "",
                    "mobil": "",
                    "email": "thomas.salomon@ramsperger-automobile.de"
                },
                {
                    "name": "Gabriele Randazzo",
                    "position": "Teiledienst",
                    "durchwahl": "129",
                    "fax": "",
                    "mobil": "",
                    "email": "gabriele.randazzo@ramsperger-automobile.de"
                },
                {
                    "name": "Steffen Schmidt",
                    "position": "Teiledienst",
                    "durchwahl": "120",
                    "fax": "",
                    "mobil": "",
                    "email": "steffen.schmidt@ramsperger-automobile.de"
                },
                {
                    "name": "Sybille Kubis",
                    "position": "Teiledienst",
                    "durchwahl": "122",
                    "fax": "",
                    "mobil": "",
                    "email": "sybille.kubis@ramsperger-automobile.de"
                },
                {
                    "name": "Steffen Brüssow",
                    "position": "Teiledienst",
                    "durchwahl": "124",
                    "fax": "",
                    "mobil": "",
                    "email": "steffen.bruessow@ramsperger-automobile.de"
                }
            ]
        },
        "vw_nfz_kh": {
            "filial_name": "KH - VW NFZ Service",
            "bereich": "VW NFZ Service",
            "adresse": "Lenninger Str. 15 | 73230 Kirchheim",
            "zentrale": "07021/5001-200",
            "verteiler": "ma-vw-nfz@ramsperger-automobile.de",
            "mitarbeiter": [
                {
                    "name": "ma-vw-nfz@ramsperger-automobile.de",
                    "position": "Management E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "ma-vw-nfz@ramsperger-automobile.de"
                },
                {
                    "name": "sb-nfz-kh@ramsperger-automobile.de",
                    "position": "Serviceberatung Sammel-E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "sb-nfz-kh@ramsperger-automobile.de"
                },
                {
                    "name": "td-nfz-kh@ramsperger-automobile.de",
                    "position": "Teiledienst Sammel-E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "td-nfz-kh@ramsperger-automobile.de"
                },
                {
                    "name": "Anesh Chandra Kumaran",
                    "position": "Serviceberatung",
                    "durchwahl": "237",
                    "fax": "",
                    "mobil": "",
                    "email": "anesh.kumaran@ramsperger-automobile.de"
                },
                {
                    "name": "Damiano De Biase",
                    "position": "Serviceberatung",
                    "durchwahl": "238",
                    "fax": "",
                    "mobil": "",
                    "email": "damiano.debiase@ramsperger-automobile.de"
                },
                {
                    "name": "Jörg Peter",
                    "position": "Serviceberatung",
                    "durchwahl": "232",
                    "fax": "",
                    "mobil": "",
                    "email": "joerg.peter@ramsperger-automobile.de"
                },
                {
                    "name": "Jannick Klosius",
                    "position": "Serviceberatung",
                    "durchwahl": "231",
                    "fax": "",
                    "mobil": "",
                    "email": "jannick.klosius@ramsperger-automobile.de"
                },
                {
                    "name": "Gabriele Randazzo",
                    "position": "Teiledienst",
                    "durchwahl": "129",
                    "fax": "",
                    "mobil": "",
                    "email": "gabriele.randazzo@ramsperger-automobile.de"
                },
                {
                    "name": "Horst Carrle",
                    "position": "Teiledienst",
                    "durchwahl": "222",
                    "fax": "",
                    "mobil": "",
                    "email": "horst.carrle@ramsperger-automobile.de"
                },
                {
                    "name": "Andreas Renz",
                    "position": "Teiledienst",
                    "durchwahl": "225",
                    "fax": "",
                    "mobil": "",
                    "email": "andreas.renz@ramsperger-automobile.de"
                },
                {
                    "name": "Enes Cetinkaya",
                    "position": "Teiledienst",
                    "durchwahl": "226",
                    "fax": "",
                    "mobil": "",
                    "email": "enes.cetinkaya@ramsperger-automobile.de"
                }
            ]
        },
        "audi_kh": {
            "filial_name": "KH - Audi",
            "bereich": "Audi",
            "adresse": "Nürtinger Str. 98 | 73230 Kirchheim",
            "zentrale": "07021/5001-300",
            "verteiler": "ma-audi@ramsperger-automobile.de",
            "mitarbeiter": [
                {
                    "name": "ma-audi@ramsperger-automobile.de",
                    "position": "Management E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "ma-audi@ramsperger-automobile.de"
                },
                {
                    "name": "sb-audi-kh@ramsperger-automobile.de",
                    "position": "Serviceberatung Sammel-E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "sb-audi-kh@ramsperger-automobile.de"
                },
                {
                    "name": "td-audi-kh@ramsperger-automobile.de",
                    "position": "Teiledienst Sammel-E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "td-audi-kh@ramsperger-automobile.de"
                },
                {
                    "name": "Martin Rams",
                    "position": "Serviceberatung",
                    "durchwahl": "332",
                    "fax": "",
                    "mobil": "",
                    "email": "martin.rams@ramsperger-automobile.de"
                },
                {
                    "name": "Patrick Zeyfang",
                    "position": "Serviceberatung",
                    "durchwahl": "334",
                    "fax": "",
                    "mobil": "",
                    "email": "patrick.zeyfang@ramsperger-automobile.de"
                },
                {
                    "name": "Edmund Deuschle",
                    "position": "Serviceberatung",
                    "durchwahl": "335",
                    "fax": "",
                    "mobil": "",
                    "email": "edmund.deuschle@ramsperger-automobile.de"
                },
                {
                    "name": "Kaan Köse",
                    "position": "Serviceberatung",
                    "durchwahl": "337",
                    "fax": "",
                    "mobil": "",
                    "email": "kaan.koese@ramsperger-automobile.de"
                },
                {
                    "name": "Florian Neu",
                    "position": "Serviceberatung",
                    "durchwahl": "331",
                    "fax": "",
                    "mobil": "",
                    "email": "florian.neu@ramsperger-automobile.de"
                },
                {
                    "name": "Tobias Sebert",
                    "position": "Teiledienst",
                    "durchwahl": "320",
                    "fax": "",
                    "mobil": "",
                    "email": "tobias.sebert@ramsperger-automobile.de"
                },
                {
                    "name": "Philipp Häberle",
                    "position": "Teiledienst",
                    "durchwahl": "323",
                    "fax": "",
                    "mobil": "",
                    "email": "philipp.haeberle@ramsperger-automobile.de"
                },
                {
                    "name": "Krisztian Kopasz",
                    "position": "Teiledienst",
                    "durchwahl": "322",
                    "fax": "",
                    "mobil": "",
                    "email": "krisztian.kopasz@ramsperger-automobile.de"
                },
                {
                    "name": "Yilmaz Yildirim",
                    "position": "Teiledienst",
                    "durchwahl": "321",
                    "fax": "",
                    "mobil": "",
                    "email": "yilmaz.yildirim@ramsperger-automobile.de"
                },
                {
                    "name": "Kevin Simon",
                    "position": "Teiledienst",
                    "durchwahl": "327",
                    "fax": "",
                    "mobil": "",
                    "email": "kevin.simon@ramsperger-automobile.de"
                }
            ]
        },
        "skoda_kh": {
            "filial_name": "KH - ŠKODA",
            "bereich": "ŠKODA",
            "adresse": "Sudetenstr. 9 | 73230 Kirchheim",
            "zentrale": "07021/5001-800",
            "verteiler": "ma-skoda@ramsperger-automobile.de",
            "mitarbeiter": [
                {
                    "name": "ma-skoda@ramsperger-automobile.de",
                    "position": "Management E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "ma-skoda@ramsperger-automobile.de"
                },
                {
                    "name": "sb-skoda-kh@ramsperger-automobile.de",
                    "position": "Serviceberatung Sammel-E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "sb-skoda-kh@ramsperger-automobile.de"
                },
                {
                    "name": "td-skoda-kh@ramsperger-automobile.de",
                    "position": "Teiledienst Sammel-E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "td-skoda-kh@ramsperger-automobile.de"
                },
                {
                    "name": "Thomas Wolpert",
                    "position": "Serviceberatung",
                    "durchwahl": "830",
                    "fax": "",
                    "mobil": "",
                    "email": "thomas.wolpert@ramsperger-automobile.de"
                },
                {
                    "name": "Tim Zerlaut",
                    "position": "Serviceberatung",
                    "durchwahl": "831",
                    "fax": "",
                    "mobil": "",
                    "email": "tim.zerlaut@ramsperger-automobile.de"
                },
                {
                    "name": "Frank Abele",
                    "position": "Serviceberatung",
                    "durchwahl": "832",
                    "fax": "",
                    "mobil": "",
                    "email": "frank.abele@ramsperger-automobile.de"
                },
                {
                    "name": "Gabriele Randazzo",
                    "position": "Teiledienst",
                    "durchwahl": "129",
                    "fax": "",
                    "mobil": "",
                    "email": "gabriele.randazzo@ramsperger-automobile.de"
                },
                {
                    "name": "Ilirjon Sutaj",
                    "position": "Teiledienst",
                    "durchwahl": "820",
                    "fax": "",
                    "mobil": "",
                    "email": "ilirjon.sutaj@ramsperger-automobile.de"
                },
                {
                    "name": "Matthias Zadka",
                    "position": "Teiledienst",
                    "durchwahl": "821",
                    "fax": "",
                    "mobil": "",
                    "email": "matthias.zadka@ramsperger-automobile.de"
                }
            ]
        },
        "vw_nt": {
            "filial_name": "NT - VW NFZ Service / ŠKODA Service",
            "bereich": "VW NFZ Service / ŠKODA Service",
            "adresse": "Robert-Bosch-Str. 9-11 | 72622 Nürtingen",
            "zentrale": "07022/9211-0",
            "verteiler": "ma-vw-nt@ramsperger-automobile.de",
            "mitarbeiter": [
                {
                    "name": "ma-vw-nt@ramsperger-automobile.de",
                    "position": "Management E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "ma-vw-nt@ramsperger-automobile.de"
                },
                {
                    "name": "sb-vw-nt@ramsperger-automobile.de",
                    "position": "Serviceberatung Sammel-E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "sb-vw-nt@ramsperger-automobile.de"
                },
                {
                    "name": "td-vw-nt@ramsperger-automobile.de",
                    "position": "Teiledienst Sammel-E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "td-vw-nt@ramsperger-automobile.de"
                },
                {
                    "name": "Frank Trost",
                    "position": "Serviceberatung",
                    "durchwahl": "632",
                    "fax": "",
                    "mobil": "",
                    "email": "frank.trost@ramsperger-automobile.de"
                },
                {
                    "name": "Frank Dreher",
                    "position": "Serviceberatung",
                    "durchwahl": "630",
                    "fax": "",
                    "mobil": "",
                    "email": "frank.dreher@ramsperger-automobile.de"
                },
                {
                    "name": "Michael Stallherm",
                    "position": "Serviceberatung",
                    "durchwahl": "636",
                    "fax": "",
                    "mobil": "",
                    "email": "michael.stallherm@ramsperger-automobile.de"
                },
                {
                    "name": "Rafael Weikum",
                    "position": "Serviceberatung",
                    "durchwahl": "638",
                    "fax": "",
                    "mobil": "",
                    "email": "rafael.weikum@ramsperger-automobile.de"
                },
                {
                    "name": "Emmanuel Ruff",
                    "position": "Serviceberatung",
                    "durchwahl": "633",
                    "fax": "",
                    "mobil": "",
                    "email": "emmanuel.ruff@ramsperger-automobile.de"
                },
                {
                    "name": "Jürgen Burkhardt",
                    "position": "Teiledienst",
                    "durchwahl": "621",
                    "fax": "",
                    "mobil": "",
                    "email": "juergen.burkhardt@ramsperger-automobile.de"
                },
                {
                    "name": "Christopher Eisenhardt",
                    "position": "Teiledienst",
                    "durchwahl": "627",
                    "fax": "",
                    "mobil": "",
                    "email": "christopher.eisenhardt@ramsperger-automobile.de"
                },
                {
                    "name": "Daniel Koller",
                    "position": "Teiledienst",
                    "durchwahl": "620",
                    "fax": "",
                    "mobil": "",
                    "email": "daniel.koller@ramsperger-automobile.de"
                },
                {
                    "name": "Igor Povalec",
                    "position": "Teiledienst",
                    "durchwahl": "624",
                    "fax": "",
                    "mobil": "",
                    "email": "igor.povalec@ramsperger-automobile.de"
                },
                {
                    "name": "Dimitrij Weiß",
                    "position": "Teiledienst",
                    "durchwahl": "625",
                    "fax": "",
                    "mobil": "",
                    "email": "dimitrij.weiss@ramsperger-automobile.de"
                },
                {
                    "name": "Roberto Greco",
                    "position": "Teiledienst",
                    "durchwahl": "626",
                    "fax": "",
                    "mobil": "",
                    "email": "roberto.greco@ramsperger-automobile.de"
                }
            ]
        },
        "vw_economy_nt": {
            "filial_name": "NT - VW Economy Service",
            "bereich": "VW Economy Service",
            "adresse": "Neuffener Str. 138 | 72622 Nürtingen",
            "zentrale": "07022/9211-510",
            "verteiler": "ma-ecs-nt@ramsperger-automobile.de",
            "mitarbeiter": [
                {
                    "name": "ma-ecs-nt@ramsperger-automobile.de",
                    "position": "Management E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "ma-ecs-nt@ramsperger-automobile.de"
                },
                {
                    "name": "José Lopes",
                    "position": "Serviceberatung",
                    "durchwahl": "531",
                    "fax": "",
                    "mobil": "",
                    "email": "jose.lopes@ramsperger-automobile.de"
                },
                {
                    "name": "Timo Klingler",
                    "position": "Serviceberatung",
                    "durchwahl": "516",
                    "fax": "",
                    "mobil": "",
                    "email": "timo.klingler@ramsperger-automobile.de"
                },
                {
                    "name": "Jan Tetting",
                    "position": "Serviceberatung",
                    "durchwahl": "532",
                    "fax": "",
                    "mobil": "",
                    "email": "jan.tetting@ramsperger-automobile.de"
                },
                {
                    "name": "Jürgen Burkhardt",
                    "position": "Teiledienst",
                    "durchwahl": "621",
                    "fax": "",
                    "mobil": "",
                    "email": "juergen.burkhardt@ramsperger-automobile.de"
                },
                {
                    "name": "Christian Knapp",
                    "position": "Teiledienst",
                    "durchwahl": "524",
                    "fax": "",
                    "mobil": "",
                    "email": "christian.knapp@ramsperger-automobile.de"
                }
            ]
        },
        "vw_economy_ntz": {
            "filial_name": "NTZ - VW Economy Service",
            "bereich": "VW Economy Service",
            "adresse": "Robert-Bosch-Str. 1-3 | 72654 Neckartenzlingen",
            "zentrale": "07022/9211-700",
            "verteiler": "ma-ecs-ntz@ramsperger-automobile.de",
            "mitarbeiter": [
                {
                    "name": "ma-ecs-ntz@ramsperger-automobile.de",
                    "position": "Management E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "ma-ecs-ntz@ramsperger-automobile.de"
                },
                {
                    "name": "sb-ecs-ntz@ramsperger-automobile.de",
                    "position": "Serviceberatung Sammel-E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "sb-ecs-ntz@ramsperger-automobile.de"
                },
                {
                    "name": "td-ecs-ntz@ramsperger-automobile.de",
                    "position": "Teiledienst Sammel-E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "td-ecs-ntz@ramsperger-automobile.de"
                },
                {
                    "name": "Nico Mercaldi",
                    "position": "Serviceberatung",
                    "durchwahl": "730",
                    "fax": "",
                    "mobil": "",
                    "email": "nico.mercaldi@ramsperger-automobile.de"
                },
                {
                    "name": "Dimitrios Dermentzopoulos",
                    "position": "Serviceberatung",
                    "durchwahl": "731",
                    "fax": "",
                    "mobil": "",
                    "email": "dimitrios.dermentzopoulos@ramsperger-automobile.de"
                },
                {
                    "name": "Peter Hauck",
                    "position": "Serviceberatung",
                    "durchwahl": "732",
                    "fax": "",
                    "mobil": "",
                    "email": "peter.hauck@ramsperger-automobile.de"
                },
                {
                    "name": "Jürgen Burkhardt",
                    "position": "Teiledienst",
                    "durchwahl": "621",
                    "fax": "",
                    "mobil": "",
                    "email": "juergen.burkhardt@ramsperger-automobile.de"
                },
                {
                    "name": "Frank Wild",
                    "position": "Teiledienst",
                    "durchwahl": "721",
                    "fax": "",
                    "mobil": "",
                    "email": "frank.wild@ramsperger-automobile.de"
                },
                {
                    "name": "Marco Mundt",
                    "position": "Teiledienst",
                    "durchwahl": "720",
                    "fax": "",
                    "mobil": "",
                    "email": "marco.mundt@ramsperger-automobile.de"
                }
            ]
        },
        "seat_nt": {
            "filial_name": "NT - SEAT Cupra",
            "bereich": "SEAT Cupra",
            "adresse": "Otto-Hahn-Str. 3 | 72622 Nürtingen",
            "zentrale": "07021/5001-900",
            "verteiler": "ma-seat@ramsperger-automobile.de",
            "mitarbeiter": [
                {
                    "name": "ma-seat@ramsperger-automobile.de",
                    "position": "Management E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "ma-seat@ramsperger-automobile.de"
                },
                {
                    "name": "sb-seat-nt@ramsperger-automobile.de",
                    "position": "Serviceberatung Sammel-E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "sb-seat-nt@ramsperger-automobile.de"
                },
                {
                    "name": "td-seat-nt@ramsperger-automobile.de",
                    "position": "Teiledienst Sammel-E-Mail",
                    "durchwahl": "",
                    "fax": "",
                    "mobil": "",
                    "email": "td-seat-nt@ramsperger-automobile.de"
                },
                {
                    "name": "Sebastian Müller",
                    "position": "Serviceberatung",
                    "durchwahl": "930",
                    "fax": "",
                    "mobil": "",
                    "email": "sebastian.mueller@ramsperger-automobile.de"
                },
                {
                    "name": "Andreas Windmeier",
                    "position": "Serviceberatung",
                    "durchwahl": "933",
                    "fax": "",
                    "mobil": "",
                    "email": "andreas.windmeier@ramsperger-automobile.de"
                },
                {
                    "name": "Rolf Werner",
                    "position": "Serviceberatung",
                    "durchwahl": "931",
                    "fax": "",
                    "mobil": "",
                    "email": "rolf.werner@ramsperger-automobile.de"
                },
                {
                    "name": "Jürgen Burkhardt",
                    "position": "Teiledienst",
                    "durchwahl": "621",
                    "fax": "",
                    "mobil": "",
                    "email": "juergen.burkhardt@ramsperger-automobile.de"
                },
                {
                    "name": "Christoph Bongartz",
                    "position": "Teiledienst",
                    "durchwahl": "920",
                    "fax": "",
                    "mobil": "",
                    "email": "christoph.bongartz@ramsperger-automobile.de"
                },
                {
                    "name": "Stefan Pultermann",
                    "position": "Teiledienst",
                    "durchwahl": "921",
                    "fax": "",
                    "mobil": "",
                    "email": "stefan.pultermann@ramsperger-automobile.de"
                },
                {
                    "name": "Florian Krebs",
                    "position": "Serviceberatung",
                    "durchwahl": "940",
                    "fax": "",
                    "mobil": "",
                    "email": "florian.krebs@ramsperger-automobile.de"
                }
            ]
        }
    }

def get_filial_options():
    """Gibt die Optionen für das Filial-Dropdown zurück"""
    filial_data = get_filial_data()
    options = []
    for key, data in filial_data.items():
        options.append((key, data["filial_name"]))
    return options

def get_mitarbeiter_for_filial(filial_key):
    """Gibt die Mitarbeiter für eine bestimmte Filiale zurück"""
    filial_data = get_filial_data()
    if filial_key in filial_data:
        return filial_data[filial_key]["mitarbeiter"]
    return []

def get_filial_info(filial_key):
    """Gibt alle Informationen zu einer Filiale zurück"""
    filial_data = get_filial_data()
    return filial_data.get(filial_key, {})

def build_phone_number(zentrale, durchwahl):
    """Baut komplette Telefonnummer aus Zentrale + Durchwahl"""
    if not durchwahl or durchwahl.strip() == "":
        return zentrale
    if not zentrale:
        return durchwahl
    
    # Zentrale bereinigen
    zentrale_clean = zentrale.replace("Zentrale ", "").replace("Zentr. ", "").strip()
    if "-" in zentrale_clean:
        base = zentrale_clean.split("-")[0]
        return f"{base}-{durchwahl}"
    return f"{zentrale_clean}-{durchwahl}"

# ================================================================================================
# HELPER FUNCTIONS (APP)
# ================================================================================================
def get_efficiency_emoji(rating):
    if pd.isna(rating):
        return ""
    rating = str(rating).strip().upper()[:1]
    return {"A":"[A]","B":"[B]","C":"[C]","D":"[D]","E":"[E]","F":"[F]","G":"[G]"}.get(rating, "")

def get_stock_display(stock_value):
    if pd.isna(stock_value) or stock_value == '':
        return "unbekannt"
    try:
        stock_num = float(stock_value)
        if stock_num < 0: return f"NACHBESTELLEN ({int(stock_num)})"
        if stock_num == 0: return f"AUSVERKAUFT ({int(stock_num)})"
        return f"VERFÜGBAR ({int(stock_num)})"
    except:
        return "unbekannt"

def init_default_services():
    services_data = {
        'service_name': ['montage_bis_17','montage_18_19','montage_ab_20',
                         'radwechsel_1_rad','radwechsel_2_raeder','radwechsel_3_raeder',
                         'radwechsel_4_raeder','nur_einlagerung'],
        'service_label': ['Montage bis 17 Zoll','Montage 18-19 Zoll','Montage ab 20 Zoll',
                          'Radwechsel 1 Rad','Radwechsel 2 Räder','Radwechsel 3 Räder',
                          'Radwechsel 4 Räder','Nur Einlagerung'],
        'price': [25.0,30.0,40.0,9.95,19.95,29.95,39.90,55.00],
        'unit': ['pro Reifen','pro Reifen','pro Reifen','pauschal','pauschal','pauschal','pauschal','pauschal']
    }
    return pd.DataFrame(services_data)

def get_service_prices():
    if 'services_config' not in st.session_state:
        st.session_state.services_config = init_default_services()
    prices = {}
    for _, row in st.session_state.services_config.iterrows():
        prices[row['service_name']] = row['price']
    return prices

# ================================================================================================
# PERSONALISIERTE ANREDE FUNKTIONEN
# ================================================================================================
def create_personalized_salutation(customer_data=None):
    """Erstellt personalisierte Anrede basierend auf Anrede und Name"""
    if not customer_data:
        return "Sehr geehrte Damen und Herren"
    
    anrede = customer_data.get('anrede', '').strip()
    name = customer_data.get('name', '').strip()
    
    if anrede and name:
        if anrede == "Herr":
            return f"Sehr geehrter Herr {name}"
        elif anrede == "Frau":
            return f"Sehr geehrte Frau {name}"
        elif anrede == "Firma":
            return "Sehr geehrte Damen und Herren"
    
    # Fallback für leere Anrede oder fehlenden Namen
    return "Sehr geehrte Damen und Herren"

# ---------------------- Saison-Erkennung ----------------------
def detect_cart_season():
    if not st.session_state.cart_items:
        return "neutral"
    saison_counts = {"Winter":0,"Sommer":0,"Ganzjahres":0,"Unbekannt":0}
    for item in st.session_state.cart_items:
        saison_counts[item.get('Saison','Unbekannt')] = saison_counts.get(item.get('Saison','Unbekannt'),0) + 1
    total_items = sum(saison_counts.values())
    if total_items == 0: return "neutral"
    dominant_season, dominant_count = sorted(saison_counts.items(), key=lambda x: x[1], reverse=True)[0]
    return dominant_season.lower() if dominant_count/total_items >= 0.7 else "gemischt"

def get_season_greeting_text(detected_season):
    season_texts = {
        "winter": {"greeting":"der Winter steht vor der Tür und die Zeichen stehen auf kälter werdende Temperaturen.",
                   "transition":"Jetzt wird es auch Zeit für Ihre Winterreifen von Ihrem Auto.","season_name":"Winter"},
        "sommer": {"greeting":"die warme Jahreszeit kommt und die Temperaturen steigen wieder.",
                   "transition":"Jetzt wird es auch Zeit für Ihre Sommerreifen von Ihrem Auto.","season_name":"Sommer"},
        "ganzjahres":{"greeting":"Sie denken über Ganzjahresreifen nach - eine praktische Lösung für das ganze Jahr.",
                      "transition":"Jetzt wird es Zeit für Ihre neuen Allwetter-Reifen von Ihrem Auto.","season_name":"Ganzjahres"},
        "gemischt":{"greeting":"Sie haben verschiedene Reifen-Optionen für unterschiedliche Anforderungen.",
                    "transition":"Gerne stelle ich Ihnen die verschiedenen Möglichkeiten vor.","season_name":"verschiedene"},
        "neutral":{"greeting":"Sie interessieren sich für neue Reifen für Ihr Fahrzeug.",
                   "transition":"Gerne stelle ich Ihnen die passenden Optionen vor.","season_name":"neue"}
    }
    return season_texts.get(detected_season, season_texts["neutral"])

# ---------------------- Service Detection für dynamische Überschrift ----------------------
def has_services_in_cart():
    """Prüft ob Services im Warenkorb aktiviert sind"""
    for item in st.session_state.cart_items:
        item_services = st.session_state.cart_services.get(item['id'], {})
        if (item_services.get('montage', False) or 
            item_services.get('radwechsel', False) or 
            item_services.get('einlagerung', False)):
            return True
    return False

def get_dynamic_title():
    """Generiert dynamische Überschrift basierend auf Warenkorb-Inhalt"""
    if has_services_in_cart():
        return "Angebot Reifen & Service"
    else:
        return "Angebot Reifen"

# ---------------------- Cart Ops ----------------------
def remove_from_cart(tire_id):
    st.session_state.cart_items = [item for item in st.session_state.cart_items if item['id'] != tire_id]
    st.session_state.cart_quantities.pop(tire_id, None)
    st.session_state.cart_services.pop(tire_id, None)
    _clear_item_widget_keys(tire_id)
    st.session_state.cart_count = len(st.session_state.cart_items)

def clear_cart():
    for item in list(st.session_state.cart_items):
        _clear_item_widget_keys(item['id'])
    st.session_state.cart_items = []
    st.session_state.cart_quantities = {}
    st.session_state.cart_services = {}
    st.session_state.cart_count = 0

def calculate_position_total(item):
    tire_id = item['id']
    quantity = st.session_state.cart_quantities.get(tire_id, 4)
    service_prices = get_service_prices()

    reifen_kosten = item['Preis_EUR'] * quantity
    item_services = st.session_state.cart_services.get(tire_id, {})
    service_kosten = 0.0

    if item_services.get('montage', False):
        z = item['Zoll']
        montage_preis = (service_prices.get('montage_bis_17',25.0) if z<=17
                         else service_prices.get('montage_18_19',30.0) if z<=19
                         else service_prices.get('montage_ab_20',40.0))
        service_kosten += montage_preis * quantity

    if item_services.get('radwechsel', False):
        t = item_services.get('radwechsel_type','4_raeder')
        service_kosten += {
            '1_rad': service_prices.get('radwechsel_1_rad',9.95),
            '2_raeder': service_prices.get('radwechsel_2_raeder',19.95),
            '3_raeder': service_prices.get('radwechsel_3_raeder',29.95),
            '4_raeder': service_prices.get('radwechsel_4_raeder',39.90)
        }.get(t, service_prices.get('radwechsel_4_raeder',39.90))

    if item_services.get('einlagerung', False):
        service_kosten += service_prices.get('nur_einlagerung',55.00)

    return reifen_kosten, service_kosten, reifen_kosten + service_kosten

def get_cart_total():
    total = 0.0
    breakdown = {'reifen':0.0,'montage':0.0,'radwechsel':0.0,'einlagerung':0.0}
    sp = get_service_prices()

    for item in st.session_state.cart_items:
        reifen_kosten, service_kosten, position_total = calculate_position_total(item)
        total += position_total
        breakdown['reifen'] += reifen_kosten

        item_services = st.session_state.cart_services.get(item['id'], {})
        qty = st.session_state.cart_quantities.get(item['id'], 4)

        if item_services.get('montage', False):
            z = item['Zoll']
            mp = (sp.get('montage_bis_17',25.0) if z<=17 else sp.get('montage_18_19',30.0) if z<=19 else sp.get('montage_ab_20',40.0))
            breakdown['montage'] += mp * qty

        if item_services.get('radwechsel', False):
            t = item_services.get('radwechsel_type','4_raeder')
            breakdown['radwechsel'] += {
                '1_rad': sp.get('radwechsel_1_rad',9.95),
                '2_raeder': sp.get('radwechsel_2_raeder',19.95),
                '3_raeder': sp.get('radwechsel_3_raeder',29.95),
                '4_raeder': sp.get('radwechsel_4_raeder',39.90)
            }.get(t, sp.get('radwechsel_4_raeder',39.90))

        if item_services.get('einlagerung', False):
            breakdown['einlagerung'] += sp.get('nur_einlagerung',55.00)

    return total, breakdown

# ================================================================================================
# PDF GENERATION (Überarbeitet mit neuen Anforderungen)
# ================================================================================================
def format_eur(value: float) -> str:
    s = f"{value:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €"

def _header_footer(canvas, doc):
    """
    Header mit Ramsperger Logo (20% größer) + Footer mit Filialinformationen.
    """
    canvas.saveState()
    width, height = A4
    margin = 20 * mm

    # Header mit Logo - 20% größer
    try:
        # Logo laden und zeichnen
        logo_path = Path("data/Logo.png")
        if logo_path.exists():
            logo = ImageReader(str(logo_path))
            # Logo-Dimensionen 20% größer: 60mm x 18mm (war 50mm x 15mm)
            logo_width = 60 * mm
            logo_height = 18 * mm
            
            # Logo links im Header positionieren
            canvas.drawImage(logo, margin, height - margin + 2, 
                           width=logo_width, height=logo_height, 
                           mask='auto', preserveAspectRatio=True)
        else:
            # Fallback Text falls Logo nicht gefunden
            canvas.setFont("Helvetica-Bold", 11)
            canvas.setFillColor(colors.black)
            canvas.drawString(margin, height - margin + 6, "AUTOHAUS RAMSPERGER")
    except Exception:
        # Fallback bei Fehlern
        canvas.setFont("Helvetica-Bold", 11)
        canvas.setFillColor(colors.black)
        canvas.drawString(margin, height - margin + 6, "AUTOHAUS RAMSPERGER")

    # Dünne Linie unter Header
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(0.5)
    canvas.line(margin, height - margin + 2, width - margin, height - margin + 2)

    # Footer mit Filialinformationen
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(colors.black)
    
    # Filialinformationen aus Session State
    filial_info = st.session_state.get('selected_filial_info', {})
    if filial_info:
        filial_text = f"Ramsperger Automobile {filial_info.get('bereich', '')} {filial_info.get('adresse', '')} Telefon: {filial_info.get('zentrale', '')}"
        canvas.drawString(margin, margin - 8, filial_text)

    canvas.restoreState()

def _p(text, style):
    return Paragraph(text, style)

def create_professional_pdf(customer_data=None, offer_scenario="vergleich", detected_season="neutral"):
    if not st.session_state.cart_items:
        return None

    total, breakdown = get_cart_total()
    season_info = get_season_greeting_text(detected_season)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=28*mm,
        bottomMargin=25*mm
    )

    # Styles (kompakter - alles etwas kleiner)
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontName="Helvetica-Bold",
                        fontSize=16, leading=19, spaceAfter=6, textColor=colors.black, alignment=TA_LEFT)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontName="Helvetica-Bold",
                        fontSize=11, leading=13, spaceAfter=4, textColor=colors.black, alignment=TA_LEFT)
    normal = ParagraphStyle('NormalPlus', parent=styles['Normal'], fontName="Helvetica",
                            fontSize=9.5, leading=12, textColor=colors.black)
    small = ParagraphStyle('Small', parent=styles['Normal'], fontName="Helvetica",
                           fontSize=8.5, leading=10, textColor=colors.black)
    cell = ParagraphStyle('cell', parent=normal, fontSize=9, leading=11)
    cell_c = ParagraphStyle('cellc', parent=cell, alignment=TA_CENTER)
    cell_r = ParagraphStyle('cellr', parent=cell, alignment=TA_RIGHT)

    # Datum rechts ausrichten Style
    date_style = ParagraphStyle('DateRight', parent=styles['Normal'], fontName="Helvetica",
                               fontSize=9.5, leading=12, alignment=TA_RIGHT, textColor=colors.black)

    story = []

    # Kopf - mit reduziertem Abstand zum Logo (kompakter)
    date_str = datetime.now().strftime('%d.%m.%Y')

    # Nur 1 Leerzeile zwischen Logo und Überschrift (kompakter)
    story.append(Spacer(1, 10))
    
    # Dynamische Überschrift basierend auf Warenkorb-Inhalt
    dynamic_title = get_dynamic_title()
    story.append(_p(dynamic_title, h1))

    # Datum rechts oben positionieren (ÄNDERUNG: rechts statt mittig)
    story.append(_p(f"Datum: {date_str}", date_style))

    # Kompaktere Leerzeilen zwischen Überschrift und Kundendaten
    story.append(Spacer(1, 12))
    story.append(Spacer(1, 12))

    # Kundendaten ohne Labels - erweitert für separate Fahrzeuge
    cust_lines = []
    if customer_data:
        if customer_data.get('anrede') and customer_data.get('name'):
            cust_lines.append(f"{customer_data['anrede']} {customer_data['name']}")
        elif customer_data.get('name'):
            cust_lines.append(f"{customer_data['name']}")
        if customer_data.get('email'):
            cust_lines.append(f"{customer_data['email']}")
        
        # Fahrzeug 1 Daten
        if customer_data.get('kennzeichen'):
            cust_lines.append(f"{customer_data['kennzeichen']}")
        extra = []
        if customer_data.get('modell'):
            extra.append(f"{customer_data['modell']}")
        if customer_data.get('fahrgestellnummer'):
            extra.append(f"FIN: {customer_data['fahrgestellnummer']}")
        if extra:
            cust_lines.append(" · ".join(extra))
        
        # Fahrzeug 2 Daten (nur bei "separate" Szenario)
        if offer_scenario == "separate":
            if customer_data.get('kennzeichen_2'):
                cust_lines.append(f"Fahrzeug 2: {customer_data['kennzeichen_2']}")
            extra_2 = []
            if customer_data.get('modell_2'):
                extra_2.append(f"{customer_data['modell_2']}")
            if customer_data.get('fahrgestellnummer_2'):
                extra_2.append(f"FIN: {customer_data['fahrgestellnummer_2']}")
            if extra_2:
                cust_lines.append(" · ".join(extra_2))

    if cust_lines:
        for line in cust_lines:
            story.append(_p(line, normal))
        # Kompaktere Leerzeilen zwischen Kundendaten und Anrede
        story.append(Spacer(1, 7))

    # Einleitung mit personalisierter Anrede
    personal_salutation = create_personalized_salutation(customer_data)
    intro_text = (
        f"{personal_salutation},<br/>"
        f"{season_info['greeting']} {season_info['transition']} "
        f"Nachfolgend erhalten Sie Ihr individuelles Angebot."
    )
    story.append(_p(intro_text, normal))
    story.append(Spacer(1, 6))

    # Positionsdarstellung ohne "Position X" Titel
    section_title = {
        "vergleich": f"Ihr individuelles {dynamic_title.split(' ', 1)[1]}",  # "Ihr individuelles Reifenangebot" oder "Ihr individuelles Reifen & Service"
        "separate": f"Angebot für Ihre Fahrzeuge",
        "einzelangebot": f"Ihr individuelles {dynamic_title.split(' ', 1)[1]}"
    }.get(offer_scenario, f"Ihr {dynamic_title.split(' ', 1)[1]}")
    story.append(_p(section_title, h2))
    story.append(Spacer(1, 4))

    for i, item in enumerate(st.session_state.cart_items, 1):
        reifen_kosten, service_kosten, position_total = calculate_position_total(item)
        quantity = st.session_state.cart_quantities.get(item['id'], 4)
        service_prices = get_service_prices()

        # EU-Label kompakt (falls vorhanden)
        eu_parts = []
        if item.get('Kraftstoffeffizienz'): eu_parts.append(f"Kraftstoff: {str(item['Kraftstoffeffizienz']).strip()}")
        if item.get('Nasshaftung'): eu_parts.append(f"Nass: {str(item['Nasshaftung']).strip()}")
        if item.get('Geräuschemissionen'): eu_parts.append(f"Geräusch: {str(item['Geräuschemissionen']).strip()}")
        eu_label = " | ".join(eu_parts) if eu_parts else "EU-Label: –"

        # Service-Aufschlüsselung für linke Spalte
        item_services = st.session_state.cart_services.get(item['id'], {})
        service_lines = []
        
        if item_services.get('montage', False):
            z = item['Zoll']
            montage_preis = (service_prices.get('montage_bis_17',25.0) if z<=17
                             else service_prices.get('montage_18_19',30.0) if z<=19
                             else service_prices.get('montage_ab_20',40.0))
            montage_gesamt = montage_preis * quantity
            service_lines.append(f"Montage: {format_eur(montage_gesamt)}")
        
        if item_services.get('radwechsel', False):
            t = item_services.get('radwechsel_type','4_raeder')
            radwechsel_preis = {
                '1_rad': service_prices.get('radwechsel_1_rad',9.95),
                '2_raeder': service_prices.get('radwechsel_2_raeder',19.95),
                '3_raeder': service_prices.get('radwechsel_3_raeder',29.95),
                '4_raeder': service_prices.get('radwechsel_4_raeder',39.90)
            }.get(t, service_prices.get('radwechsel_4_raeder',39.90))
            type_map = {'1_rad':'1 Rad','2_raeder': '2 Räder','3_raeder':'3 Räder','4_raeder':'4 Räder'}
            service_lines.append(f"Radwechsel {type_map.get(t,'4 Räder')}: {format_eur(radwechsel_preis)}")
        
        if item_services.get('einlagerung', False):
            einlagerung_preis = service_prices.get('nur_einlagerung',55.00)
            service_lines.append(f"Einlagerung: {format_eur(einlagerung_preis)}")

        # Linke Spalte (Info + Services) - größere Schrift
        left_rows = [
            [_p(f"<b>{item['Reifengröße']}</b> – <b>{item['Fabrikat']} {item['Profil']}</b>", cell)],
            [_p(f"Teilenummer: {item['Teilenummer']} · Einzelpreis: <b>{format_eur(item['Preis_EUR'])}</b>", cell)],
            [_p(f"{eu_label}", cell)]
        ]
        
        # Service-Zeilen hinzufügen
        for service_line in service_lines:
            left_rows.append([_p(service_line, cell)])

        left_tbl = Table(left_rows, colWidths=[12*cm])
        left_tbl.setStyle(TableStyle([
            ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
            ('FONTSIZE',(0,0),(-1,-1),9),
            ('TEXTCOLOR',(0,0),(-1,-1),colors.black),
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('BOTTOMPADDING',(0,0),(-1,-1),2),
            ('TOPPADDING',(0,0),(-1,-1),1),
        ]))

        # Rechte Spalte - GROSSE GRÜNE BOX für Gesamtpreis bei Vergleichsangeboten
        if offer_scenario == "vergleich":
            # Aufschlüsselung oberhalb der grünen Box für Vergleichsangebote
            right_rows = [
                [_p(f"<b>{quantity}×</b>", cell_c)],  # Stückzahl
                [_p(" ", cell_c)],  # Spacer
                [_p(f"Reifen: {format_eur(reifen_kosten)}", cell_r)],  # Reifen-Aufschlüsselung
                [_p(f"Services: {format_eur(service_kosten)}", cell_r)],  # Service-Aufschlüsselung
                [_p(f"<b>GESAMT</b><br/><b>{format_eur(position_total)}</b>", cell_c)],  # Grüne Box
            ]

            right_tbl = Table(right_rows, colWidths=[5.6*cm])
            right_tbl.setStyle(TableStyle([
                ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
                ('FONTSIZE',(0,0),(-1,-1),9),
                ('TEXTCOLOR',(0,0),(-1,-1),colors.black),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('BOTTOMPADDING',(0,0),(-1,-1),2),
                ('TOPPADDING',(0,0),(-1,-1),1),
                
                # Grüne Box für Gesamtpreis (Position 4 - jetzt nach Aufschlüsselung)
                ('FONTNAME',(0,4),(-1,4),'Helvetica-Bold'),
                ('FONTSIZE',(0,4),(-1,4),12),
                ('BACKGROUND',(0,4),(-1,4), colors.HexColor('#f0fdf4')),
                ('TEXTCOLOR',(0,4),(-1,4), colors.HexColor('#166534')),
                ('ALIGN',(0,4),(-1,4),'CENTER'),
                ('TOPPADDING',(0,4),(-1,4),6),
                ('BOTTOMPADDING',(0,4),(-1,4),6),
                ('LEFTPADDING',(0,4),(-1,4),6),
                ('RIGHTPADDING',(0,4),(-1,4),6),
            ]))
        else:
            # Normale Darstellung für andere Szenarien
            right_rows = [
                [_p(f"<b>{quantity}×</b>", cell_c)],  # Stückzahl mittig
                [_p(" ", cell_c)],  # Spacer
                [_p(f"Reifen: {format_eur(reifen_kosten)}", cell_r)],
                [_p(f"Services: {format_eur(service_kosten)}", cell_r)],
                [_p(f"<b>Gesamt: {format_eur(position_total)}</b>", cell_r)],
            ]

            right_tbl = Table(right_rows, colWidths=[5.6*cm])
            right_tbl.setStyle(TableStyle([
                ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
                ('FONTSIZE',(0,0),(-1,-1),9),
                ('TEXTCOLOR',(0,0),(-1,-1),colors.black),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('BOTTOMPADDING',(0,0),(-1,-1),2),
                ('TOPPADDING',(0,0),(-1,-1),1),
            ]))

        card = Table([[left_tbl, right_tbl]], colWidths=[12*cm, 5.6*cm])
        card.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('INNERGRID',(0,0),(-1,-1),0, colors.white),
            ('BOX',(0,0),(-1,-1),0, colors.white),
        ]))

        # Direkt Card ohne Position-Titel
        story.append(KeepTogether(card))

        # Dünne Trennlinie zwischen Cards (nur wenn nicht letzte Position)
        if i < len(st.session_state.cart_items):
            story.append(Table([[""]], colWidths=[17.6*cm], rowHeights=[0.2]))
            story[-1].setStyle(TableStyle([
                ('LINEABOVE',(0,0),(-1,-1),0.3,colors.black),
                ('LEFTPADDING',(0,0),(-1,-1),0),
                ('RIGHTPADDING',(0,0),(-1,-1),0),
                ('TOPPADDING',(0,0),(-1,-1),0),
                ('BOTTOMPADDING',(0,0),(-1,-1),0),
            ]))
        story.append(Spacer(1, 3))

    # WICHTIGE ÄNDERUNG: Grüne Vergleichsbox für Vergleichsangebote ENTFERNT
    # Kostenaufstellung nur für andere Szenarien
    if offer_scenario != "vergleich":
        story.append(_p("Kostenaufstellung", h2))
        cost_rows = [['Reifen-Kosten', format_eur(breakdown['reifen'])]]
        if breakdown['montage'] > 0:
            cost_rows.append(['Montage-Service', format_eur(breakdown['montage'])])
        if breakdown['radwechsel'] > 0:
            cost_rows.append(['Radwechsel-Service', format_eur(breakdown['radwechsel'])])
        if breakdown['einlagerung'] > 0:
            cost_rows.append(['Einlagerung', format_eur(breakdown['einlagerung'])])

        cost_rows.append(['', ''])
        cost_rows.append(['GESAMTSUMME', format_eur(total)])

        cost_tbl = Table(cost_rows, colWidths=[12*cm, 5*cm])
        cost_tbl.setStyle(TableStyle([
            ('FONTNAME',(0,0),(-1,-2),'Helvetica'),
            ('FONTSIZE',(0,0),(-1,-2),9),
            ('TEXTCOLOR',(0,0),(-1,-2),colors.black),
            ('ALIGN',(0,0),(0,-2),'LEFT'),
            ('ALIGN',(1,0),(1,-2),'RIGHT'),
            ('LINEBELOW',(0,-2),(-1,-2), 0.6, colors.black),

            # Gesamtsumme (einzige Farbe)
            ('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold'),
            ('FONTSIZE',(0,-1),(-1,-1),11),
            ('BACKGROUND',(0,-1),(-1,-1), colors.HexColor('#f0fdf4')),
            ('TEXTCOLOR',(0,-1),(-1,-1), colors.HexColor('#166534')),
            ('ALIGN',(0,-1),(0,-1),'LEFT'),
            ('ALIGN',(1,-1),(1,-1),'RIGHT'),

            ('TOPPADDING',(0,0),(-1,-1),3),
            ('BOTTOMPADDING',(0,0),(-1,-1),3),
            ('LEFTPADDING',(0,0),(-1,-1),3),
            ('RIGHTPADDING',(0,0),(-1,-1),3),
        ]))
        story.append(KeepTogether(cost_tbl))
        story.append(Spacer(1, 5))

    # NEUE BULLET POINTS (anstelle der alten) - kompakter
    story.append(Spacer(1, 5))
    bullets = [
        "Angebot gültig 14 Tage",
        "Inklusive Reifengarantie 36 Monate",
        "Inklusive Entsorgung Altreifen"
    ]
    
    # Saisonspezifische Bullet Points hinzufügen
    if detected_season == "winter":
        bullets.append("Wir empfehlen den rechtzeitigen Wechsel auf Winterreifen für optimale Sicherheit bei winterlichen Bedingungen.")
    elif detected_season == "sommer":
        bullets.append("Sommerreifen bieten optimalen Grip und Fahrkomfort bei warmen Temperaturen und trockenen Straßen.")
    elif detected_season == "ganzjahres":
        bullets.append("Ganzjahresreifen sind eine praktische Lösung für das ganze Jahr ohne saisonalen Wechsel.")
    
    if offer_scenario == "vergleich":
        bullets.append("Sie können sich für eine der angebotenen Reifenoptionen entscheiden.")

    for b in bullets:
        story.append(_p(f"• {b}", small))
    story.append(Spacer(1, 5))

    # Geänderte Reihenfolge: Zuerst "Vielen Dank", dann "Für Rückfragen", dann Mitarbeiter
    story.append(_p("Vielen Dank für Ihr Vertrauen!", h2))
    story.append(_p("Ihr Team von Ramsperger Automobile", normal))
    story.append(Spacer(1, 5))
    
    story.append(_p("Für Rückfragen stehen wir Ihnen gerne zur Verfügung.", small))
    story.append(Spacer(1, 5))

    # Mitarbeiterinformationen hinzufügen
    selected_mitarbeiter = st.session_state.get('selected_mitarbeiter_info', {})
    if selected_mitarbeiter:
        mitarbeiter_name = selected_mitarbeiter.get('name', '')
        mitarbeiter_position = selected_mitarbeiter.get('position', '')
        mitarbeiter_email = selected_mitarbeiter.get('email', '')
        
        # Telefonnummer aufbauen
        filial_info = st.session_state.get('selected_filial_info', {})
        zentrale = filial_info.get('zentrale', '')
        durchwahl = selected_mitarbeiter.get('durchwahl', '')
        telefon = build_phone_number(zentrale, durchwahl) if durchwahl else zentrale
        
        mitarbeiter_text = f"<b>{mitarbeiter_name}</b>"
        if mitarbeiter_position and not mitarbeiter_position.endswith("E-Mail") and mitarbeiter_position != "Interner Verteiler":
            mitarbeiter_text += f", {mitarbeiter_position}"
        mitarbeiter_text += "<br/>"
        if telefon:
            mitarbeiter_text += f"Telefon: {telefon}"
        if mitarbeiter_email:
            mitarbeiter_text += f" | E-Mail: {mitarbeiter_email}"
        
        story.append(_p(mitarbeiter_text, small))

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    buffer.seek(0)
    return buffer.getvalue()

# ================================================================================================
# E-MAIL TEXT & MAILTO (direkter Flow, Regex FIX)
# ================================================================================================
_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")  # FIX: korrekte Whitespaces

def _normalize_crlf(text: str) -> str:
    if text is None:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.replace("\n", "\r\n")

def _urlencode_mail_body(text: str) -> str:
    return urllib.parse.quote(text, safe="")

def _valid_email(addr: str) -> bool:
    return bool(_EMAIL_REGEX.match((addr or "").strip()))

def create_email_text(customer_data=None, detected_season="neutral"):
    season_info = get_season_greeting_text(detected_season)
    personal_salutation = create_personalized_salutation(customer_data)
    
    email_content = (
        f"{personal_salutation},\r\n\r\n"
        f"anbei sende ich Ihnen Ihr Reifenangebot für {season_info['season_name']}-Reifen.\r\n\r\n"
        "Alle Details finden Sie im angehängten PDF-Dokument.\r\n\r\n"
        "Bei Fragen stehen wir Ihnen gerne zur Verfügung.\r\n\r\n"
        "Mit freundlichen Grüßen\r\n"
        "Ramsperger Automobile"
    )
    return email_content

def create_mailto_link(customer_email, email_text, detected_season):
    if not customer_email or not _valid_email(customer_email):
        return None
    season_info = get_season_greeting_text(detected_season)
    subject = f"Ihr Reifenangebot von Ramsperger Automobile - {season_info['season_name']}-Reifen"
    body_crlf = _normalize_crlf(email_text)
    subject_encoded = urllib.parse.quote(subject, safe="")
    body_encoded = _urlencode_mail_body(body_crlf)
    to_addr = customer_email.strip()
    return f"mailto:{to_addr}?subject={subject_encoded}&body={body_encoded}"

# ================================================================================================
# TD-ANFRAGE FUNKTIONEN
# ================================================================================================
def create_td_email_text(customer_data=None, detected_season="neutral"):
    """Erstellt den E-Mail-Text für die TD-Anfrage"""
    if not st.session_state.cart_items:
        return ""
    
    # Kopf der E-Mail
    email_content = (
        "Liebe Kollegen,\r\n\r\n"
        "wollten mal anfragen ob die folgenden Reifen verfügbar sind:\r\n\r\n"
    )
    
    # Kundendaten falls vorhanden
    if customer_data and (customer_data.get('name') or customer_data.get('kennzeichen') or customer_data.get('modell')):
        email_content += "KUNDENDATEN:\r\n"
        if customer_data.get('anrede') and customer_data.get('name'):
            email_content += f"Kunde: {customer_data['anrede']} {customer_data['name']}\r\n"
        elif customer_data.get('name'):
            email_content += f"Kunde: {customer_data['name']}\r\n"
        if customer_data.get('kennzeichen'):
            email_content += f"Kennzeichen: {customer_data['kennzeichen']}\r\n"
        if customer_data.get('modell'):
            email_content += f"Fahrzeug: {customer_data['modell']}\r\n"
        if customer_data.get('fahrgestellnummer'):
            email_content += f"Fahrgestellnummer: {customer_data['fahrgestellnummer']}\r\n"
        
        # Fahrzeug 2 Daten falls vorhanden
        if customer_data.get('kennzeichen_2') or customer_data.get('modell_2') or customer_data.get('fahrgestellnummer_2'):
            email_content += f"Fahrzeug 2:\r\n"
            if customer_data.get('kennzeichen_2'):
                email_content += f"Kennzeichen 2: {customer_data['kennzeichen_2']}\r\n"
            if customer_data.get('modell_2'):
                email_content += f"Fahrzeug 2: {customer_data['modell_2']}\r\n"
            if customer_data.get('fahrgestellnummer_2'):
                email_content += f"Fahrgestellnummer 2: {customer_data['fahrgestellnummer_2']}\r\n"
        
        email_content += "\r\n"
    
    # Reifenpositionen
    email_content += "REIFENANFRAGE:\r\n"
    email_content += "="*50 + "\r\n\r\n"
    
    for i, item in enumerate(st.session_state.cart_items, 1):
        quantity = st.session_state.cart_quantities.get(item['id'], 4)
        
        email_content += f"Position {i}:\r\n"
        email_content += f"Reifengröße: {item['Reifengröße']}\r\n"
        email_content += f"Fabrikat: {item['Fabrikat']}\r\n"
        email_content += f"Profil: {item['Profil']}\r\n"
        email_content += f"Teilenummer: {item['Teilenummer']}\r\n"
        email_content += f"Stückzahl: {quantity} Stück\r\n"
        email_content += f"Aktueller Preis: {item['Preis_EUR']:.2f} EUR\r\n"
        
        if item.get('Saison'):
            email_content += f"Saison: {item['Saison']}\r\n"
        
        # EU-Label Informationen falls vorhanden
        eu_info = []
        if item.get('Kraftstoffeffizienz'):
            eu_info.append(f"Kraftstoffeffizienz: {item['Kraftstoffeffizienz']}")
        if item.get('Nasshaftung'):
            eu_info.append(f"Nasshaftung: {item['Nasshaftung']}")
        if item.get('Geräuschemissionen'):
            eu_info.append(f"Geräusch: {item['Geräuschemissionen']}")
        
        if eu_info:
            email_content += f"EU-Label: {' | '.join(eu_info)}\r\n"
        
        email_content += "\r\n"
    
    return email_content

def create_td_mailto_link(td_email_text):
    """Erstellt den mailto-Link für die TD-Anfrage - KEIN Empfänger vorgefüllt"""
    subject = f"Reifenanfrage Ramsperger Automobile - {len(st.session_state.cart_items)} Position(en)"
    body_crlf = _normalize_crlf(td_email_text)
    subject_encoded = urllib.parse.quote(subject, safe="")
    body_encoded = _urlencode_mail_body(body_crlf)
    
    # WICHTIG: mailto: ohne E-Mail-Adresse = leeres An-Feld in Outlook
    return f"mailto:?subject={subject_encoded}&body={body_encoded}"

# ================================================================================================
# SESSION STATE INITIALISIERUNG
# ================================================================================================
def init_session_state():
    if 'customer_data' not in st.session_state:
        st.session_state.customer_data = {
            'anrede':'','name':'','email':'','kennzeichen':'','modell':'','fahrgestellnummer':'',
            'kennzeichen_2':'','modell_2':'','fahrgestellnummer_2':''
        }

    if 'cart_items' not in st.session_state: st.session_state.cart_items = []
    if 'cart_quantities' not in st.session_state: st.session_state.cart_quantities = {}
    if 'cart_services' not in st.session_state: st.session_state.cart_services = {}
    if 'cart_count' not in st.session_state: st.session_state.cart_count = 0

    if 'offer_scenario' not in st.session_state:
        st.session_state.offer_scenario = "vergleich"

    if 'show_email_options' not in st.session_state:
        # bleibt nur der Vollständigkeit halber; wird nicht mehr genutzt
        st.session_state.show_email_options = False

    if 'pdf_created' not in st.session_state:
        st.session_state.pdf_created = False

    # Filial- und Mitarbeiter-Session States
    if 'selected_filial' not in st.session_state:
        st.session_state.selected_filial = ""
    if 'selected_mitarbeiter' not in st.session_state:
        st.session_state.selected_mitarbeiter = ""
    if 'selected_filial_info' not in st.session_state:
        st.session_state.selected_filial_info = {}
    if 'selected_mitarbeiter_info' not in st.session_state:
        st.session_state.selected_mitarbeiter_info = {}

    st.session_state.setdefault('customer_anrede', st.session_state.customer_data.get('anrede',''))
    st.session_state.setdefault('customer_name', st.session_state.customer_data.get('name',''))
    st.session_state.setdefault('customer_email', st.session_state.customer_data.get('email',''))
    st.session_state.setdefault('customer_kennzeichen', st.session_state.customer_data.get('kennzeichen',''))
    st.session_state.setdefault('customer_modell', st.session_state.customer_data.get('modell',''))
    st.session_state.setdefault('customer_fahrgestell', st.session_state.customer_data.get('fahrgestellnummer',''))
    
    # Fahrzeug 2 Session States
    st.session_state.setdefault('customer_kennzeichen_2', st.session_state.customer_data.get('kennzeichen_2',''))
    st.session_state.setdefault('customer_modell_2', st.session_state.customer_data.get('modell_2',''))
    st.session_state.setdefault('customer_fahrgestell_2', st.session_state.customer_data.get('fahrgestellnummer_2',''))

# ================================================================================================
# INTERNAL UTILITIES FOR WIDGET-STATE
# ================================================================================================
def _ensure_item_defaults(item_id):
    st.session_state.setdefault(f"qty_{item_id}", st.session_state.cart_quantities.get(item_id, 4))
    st.session_state.cart_services.setdefault(item_id, {'montage':False,'radwechsel':False,'radwechsel_type':'4_raeder','einlagerung':False})

    cs = st.session_state.cart_services[item_id]
    st.session_state.setdefault(f"montage_{item_id}", cs.get('montage', False))
    st.session_state.setdefault(f"radwechsel_{item_id}", cs.get('radwechsel', False))
    st.session_state.setdefault(f"cart_radwechsel_type_{item_id}", cs.get('radwechsel_type', '4_raeder'))
    st.session_state.setdefault(f"einlagerung_{item_id}", cs.get('einlagerung', False))

def _update_qty(item_id):
    st.session_state.cart_quantities[item_id] = st.session_state.get(f"qty_{item_id}", 4)

def _update_service(item_id, field):
    st.session_state.cart_services.setdefault(item_id, {})
    st.session_state.cart_services[item_id][field] = st.session_state.get(f"{field}_{item_id}", False)

def _update_radwechsel_type(item_id):
    st.session_state.cart_services.setdefault(item_id, {})
    st.session_state.cart_services[item_id]['radwechsel_type'] = st.session_state.get(f"cart_radwechsel_type_{item_id}", '4_raeder')

def _clear_item_widget_keys(item_id):
    for key in [f"qty_{item_id}", f"montage_{item_id}", f"radwechsel_{item_id}", f"cart_radwechsel_type_{item_id}", f"einlagerung_{item_id}"]:
        st.session_state.pop(key, None)

# ================================================================================================
# RENDER FUNCTIONS - MIT SCHÖNER POSITIONS-ABTRENNUNG
# ================================================================================================
def render_empty_cart():
    st.markdown("### Der Warenkorb ist leer")
    st.markdown("Gehe zur **Reifen Suche** und wähle Reifen für dein Angebot aus.")
    if st.button("Zur Reifen Suche", use_container_width=True, type="primary"):
        st.switch_page("pages/01_Reifen_Suche.py")

def render_cart_content():
    st.markdown("#### Reifen im Warenkorb")
    for i, item in enumerate(st.session_state.cart_items, 1):
        render_cart_item(item, i)
        
        # Schöne Abtrennung zwischen Positionen (nur wenn nicht die letzte Position)
        if i < len(st.session_state.cart_items):
            st.markdown("---")

def render_cart_item(item, position_number):
    st.markdown(f"### Position {position_number}")

    item_id = item['id']
    _ensure_item_defaults(item_id)

    col_info, col_qty, col_services, col_remove = st.columns([3, 1, 2, 1])

    with col_info:
        st.markdown(f"**{item['Reifengröße']}** - {item['Fabrikat']} {item['Profil']}")
        st.markdown(f"Teilenummer: {item['Teilenummer']} | Einzelpreis: **{item['Preis_EUR']:.2f}EUR**")
        effi = f" {get_efficiency_emoji(item['Kraftstoffeffizienz'])}{item['Kraftstoffeffizienz']}" if item.get('Kraftstoffeffizienz') else ""
        nass = f" {get_efficiency_emoji(item['Nasshaftung'])}{item['Nasshaftung']}" if item.get('Nasshaftung') else ""
        best = f" | {get_stock_display(item.get('Bestand'))}"
        saz  = f" | Saison: {item.get('Saison','Unbekannt')}"
        st.markdown(f"EU-Label:{effi}{nass}{best}{saz}")

    with col_qty:
        st.number_input("Stückzahl:", 1, 8,
                        key=f"qty_{item_id}",
                        on_change=_update_qty, args=(item_id,))

    with col_services:
        render_item_services(item)

    with col_remove:
        if st.button("Entfernen", key=f"remove_{item_id}", help="Aus Warenkorb entfernen"):
            remove_from_cart(item_id)
            st.rerun()

    reifen_kosten, service_kosten, position_total = calculate_position_total(item)
    st.markdown(f"### **Position {position_number} Gesamt: {position_total:.2f} EUR**")
    st.markdown(f"Reifen: {reifen_kosten:.2f}EUR + Services: {service_kosten:.2f}EUR")

def render_item_services(item):
    item_id = item['id']
    _ensure_item_defaults(item_id)
    sp = get_service_prices()

    st.markdown("**Services:**")

    z = item['Zoll']
    montage_price = (sp.get('montage_bis_17',25.0) if z<=17 else sp.get('montage_18_19',30.0) if z<=19 else sp.get('montage_ab_20',40.0))
    montage_label = f"Montage ({montage_price:.2f}EUR/Stk)"
    st.checkbox(montage_label, key=f"montage_{item_id}",
                on_change=_update_service, args=(item_id,'montage'))

    st.checkbox("Radwechsel", key=f"radwechsel_{item_id}",
                on_change=_update_service, args=(item_id,'radwechsel'))

    if st.session_state.get(f"radwechsel_{item_id}", False):
        options = [
            ('4_raeder', f"4 Räder ({sp.get('radwechsel_4_raeder',39.90):.2f}EUR)"),
            ('3_raeder', f"3 Räder ({sp.get('radwechsel_3_raeder',29.95):.2f}EUR)"),
            ('2_raeder', f"2 Räder ({sp.get('radwechsel_2_raeder',19.95):.2f}EUR)"),
            ('1_rad',   f"1 Rad ({sp.get('radwechsel_1_rad',9.95):.2f}EUR)")
        ]
        st.selectbox("Anzahl:", options=[k for k,_ in options],
                     format_func=lambda x: next(lbl for k,lbl in options if k==x),
                     key=f"cart_radwechsel_type_{item_id}",
                     on_change=_update_radwechsel_type, args=(item_id,))

    st.checkbox(f"Einlagerung ({sp.get('nur_einlagerung',55.00):.2f}EUR)",
                key=f"einlagerung_{item_id}",
                on_change=_update_service, args=(item_id,'einlagerung'))

def render_price_summary(total, breakdown):
    st.markdown("---")
    st.markdown("#### Preisübersicht")
    col_breakdown, col_total = st.columns([2, 1])
    with col_breakdown:
        st.markdown(f"**Reifen-Kosten:** {breakdown['reifen']:.2f}EUR")
        if breakdown['montage']>0: st.markdown(f"**Montage:** {breakdown['montage']:.2f}EUR")
        if breakdown['radwechsel']>0: st.markdown(f"**Radwechsel:** {breakdown['radwechsel']:.2f}EUR")
        if breakdown['einlagerung']>0: st.markdown(f"**Einlagerung:** {breakdown['einlagerung']:.2f}EUR")
    with col_total:
        st.markdown(f"### **GESAMT: {total:.2f}EUR**")

def render_customer_data():
    st.markdown("---")
    st.markdown("#### Kundendaten (optional)")
    st.markdown("Diese Angaben werden in das Angebot aufgenommen, falls gewünscht:")

    # Anrede-Dropdown prominent platziert - ganze Breite
    anrede_options = ["", "Herr", "Frau", "Firma"]
    st.selectbox("Anrede:", 
                 options=anrede_options, 
                 key="customer_anrede", 
                 help="Für personalisierte Ansprache in Angeboten und E-Mails")

    # Rest der Kundendaten in zwei Spalten
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Kundenname:", key="customer_name", placeholder="z.B. Max Mustermann")
        st.text_input("E-Mail-Adresse:", key="customer_email", placeholder="z.B. max@mustermann.de", help="Für den E-Mail-Versand des Angebots")
        st.text_input("Kennzeichen:", key="customer_kennzeichen", placeholder="z.B. GP-AB 123")
    with col2:
        st.text_input("Hersteller / Modell:", key="customer_modell", placeholder="z.B. BMW 3er E90")
        st.text_input("Fahrgestellnummer:", key="customer_fahrgestell", placeholder="z.B. WBAVA31070F123456")

    # Fahrzeug 2 Felder nur bei "separate" Szenario
    if st.session_state.offer_scenario == "separate":
        st.markdown("---")
        st.markdown("##### Fahrzeug 2 (Separate Fahrzeuge)")
        
        col3, col4 = st.columns(2)
        with col3:
            st.text_input("Kennzeichen 2:", key="customer_kennzeichen_2", placeholder="z.B. GP-CD 456")
            st.text_input("Hersteller / Modell 2:", key="customer_modell_2", placeholder="z.B. Audi A4 B9")
        with col4:
            st.text_input("Fahrgestellnummer 2:", key="customer_fahrgestell_2", placeholder="z.B. WAUEFE123456789")

    # Session State Update
    st.session_state.customer_data = {
        'anrede': st.session_state.get('customer_anrede',''),
        'name': st.session_state.get('customer_name',''),
        'email': st.session_state.get('customer_email',''),
        'kennzeichen': st.session_state.get('customer_kennzeichen',''),
        'modell': st.session_state.get('customer_modell',''),
        'fahrgestellnummer': st.session_state.get('customer_fahrgestell',''),
        'kennzeichen_2': st.session_state.get('customer_kennzeichen_2',''),
        'modell_2': st.session_state.get('customer_modell_2',''),
        'fahrgestellnummer_2': st.session_state.get('customer_fahrgestell_2','')
    }

def render_filial_mitarbeiter_selection():
    """Filial- und Mitarbeiterauswahl mit festen Datenstrukturen"""
    st.markdown("---")
    st.markdown("#### Filiale und Ansprechpartner auswählen")
    st.markdown("Diese Informationen werden in das Angebot und den Footer aufgenommen:")
    
    # Filial-Daten aus fester Struktur laden
    filial_data = get_filial_data()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Filial-Dropdown
        filial_options = get_filial_options()
        selected_filial = st.selectbox(
            "Filiale:",
            options=[""] + [key for key, _ in filial_options],
            format_func=lambda x: "Bitte wählen..." if x == "" else next((name for key, name in filial_options if key == x), x),
            key="selected_filial_key",
            help="Auswahl der Filiale für Adresse und Telefon im PDF"
        )
        
        # Filial-Info in Session State speichern
        if selected_filial:
            st.session_state.selected_filial = selected_filial
            st.session_state.selected_filial_info = get_filial_info(selected_filial)
        else:
            st.session_state.selected_filial = ""
            st.session_state.selected_filial_info = {}
    
    with col2:
        # Mitarbeiter-Dropdown (nur wenn Filiale gewählt)
        if st.session_state.selected_filial:
            mitarbeiter = get_mitarbeiter_for_filial(st.session_state.selected_filial)
            
            if mitarbeiter:
                selected_mitarbeiter_idx = st.selectbox(
                    "Ansprechpartner:",
                    options=list(range(-1, len(mitarbeiter))),
                    format_func=lambda x: ("Bitte wählen..." if x == -1 else 
                                          f"{mitarbeiter[x]['name']}" if "E-Mail" in mitarbeiter[x]['position'] else
                                          f"{mitarbeiter[x]['name']} ({mitarbeiter[x]['position']})" if x >= 0 else ""),
                    key="selected_mitarbeiter_key",
                    help="Auswahl des Ansprechpartners für das PDF"
                )
                
                # Mitarbeiter-Info in Session State speichern
                if selected_mitarbeiter_idx >= 0:
                    st.session_state.selected_mitarbeiter = selected_mitarbeiter_idx
                    st.session_state.selected_mitarbeiter_info = mitarbeiter[selected_mitarbeiter_idx]
                else:
                    st.session_state.selected_mitarbeiter = ""
                    st.session_state.selected_mitarbeiter_info = {}
            else:
                st.info("Keine Mitarbeiter für diese Filiale verfügbar")
        else:
            st.selectbox("Ansprechpartner:", options=[], disabled=True, help="Bitte zuerst eine Filiale auswählen")
    
    # Vorschau der ausgewählten Informationen
    if st.session_state.selected_filial_info and st.session_state.selected_mitarbeiter_info:
        st.markdown("##### Vorschau der Auswahl:")
        filial_info = st.session_state.selected_filial_info
        mitarbeiter_info = st.session_state.selected_mitarbeiter_info
        
        col_preview1, col_preview2 = st.columns(2)
        
        with col_preview1:
            st.markdown("**Filiale:**")
            st.markdown(f"{filial_info.get('bereich', '')}")
            st.markdown(f"{filial_info.get('adresse', '')}")
            st.markdown(f"Telefon: {filial_info.get('zentrale', '')}")
        
        with col_preview2:
            st.markdown("**Ansprechpartner:**")
            st.markdown(f"**{mitarbeiter_info.get('name', '')}**")
            if mitarbeiter_info.get('position') and not mitarbeiter_info.get('position', '').endswith("E-Mail"):
                st.markdown(f"{mitarbeiter_info.get('position', '')}")
            if mitarbeiter_info.get('durchwahl'):
                telefon = build_phone_number(filial_info.get('zentrale', ''), mitarbeiter_info.get('durchwahl', ''))
                st.markdown(f"Telefon: {telefon}")
            if mitarbeiter_info.get('email'):
                st.markdown(f"E-Mail: {mitarbeiter_info.get('email', '')}")

def render_scenario_selection():
    st.markdown("---")
    st.markdown("#### Angebot-Typ auswählen")

    detected = detect_cart_season()
    season_info = get_season_greeting_text(detected)

    st.radio(
        "Angebot-Szenario:",
        options=["vergleich","separate","einzelangebot"],
        format_func=lambda x: {
            "vergleich":"Vergleichsangebot - Verschiedene Reifenoptionen zur Auswahl für ein Fahrzeug",
            "separate":"Separate Fahrzeuge - Jede Position ist für ein anderes Fahrzeug",
            "einzelangebot":"Einzelangebot - Spezifisches Angebot für die ausgewählten Reifen"
        }[x],
        key="offer_scenario"
    )

    if st.session_state.offer_scenario == "vergleich":
        st.info(f"**Vergleichsangebot:** Der Kunde bekommt mehrere {season_info['season_name']}-Reifenoptionen zur Auswahl präsentiert und kann sich für eine davon entscheiden.")
    elif st.session_state.offer_scenario == "separate":
        st.info(f"**Separate Fahrzeuge:** Jede Position wird als separates Fahrzeug behandelt mit eigenständiger {season_info['season_name']}-Reifen-Berechnung.")
    else:
        st.info(f"**Einzelangebot:** Direktes, spezifisches Angebot für die ausgewählten {season_info['season_name']}-Reifen ohne Vergleichsoptionen.")

    return detected

def render_actions(total, breakdown, detected_season):
    st.markdown("---")
    st.markdown("#### PDF-Angebot erstellen")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("📄 PDF-Angebot erstellen", use_container_width=True, type="primary"):
            pdf_data = create_professional_pdf(
                st.session_state.customer_data,
                st.session_state.offer_scenario,
                detected_season
            )
            if pdf_data:
                st.session_state.current_email_text = create_email_text(
                    st.session_state.customer_data,
                    detected_season
                )
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                season_info = get_season_greeting_text(detected_season)
                filename = f"Angebot_Ramsperger_{season_info['season_name']}_{ts}.pdf"

                st.success("✅ PDF-Angebot erfolgreich erstellt!")
                st.download_button(
                    label="📥 PDF-Angebot herunterladen",
                    data=pdf_data,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
                st.session_state.pdf_created = True
            else:
                st.error("Fehler beim Erstellen der PDF-Datei")

    with col2:
        # Direkter mailto-Flow für Kundenangebot (mit Kunden-E-Mail)
        customer_email = st.session_state.customer_data.get('email', '').strip()
        if not customer_email:
            st.button("📧 E-Mail fehlt", use_container_width=True, disabled=True,
                      help="Bitte E-Mail-Adresse bei Kundendaten eingeben")
        elif not st.session_state.pdf_created:
            st.button("📧 Erst PDF erstellen", use_container_width=True, disabled=True,
                      help="Bitte zuerst PDF-Angebot erstellen")
        else:
            mailto_link = create_mailto_link(
                customer_email,
                st.session_state.get('current_email_text', create_email_text(st.session_state.customer_data, detected_season)),
                detected_season
            )
            if mailto_link:
                st.link_button("📧 Per E-Mail senden", mailto_link,
                               use_container_width=True, type="secondary",
                               help="Öffnet Ihren Standard-Mailclient (z. B. Outlook Desktop)")
            else:
                st.button("📧 Ungültige E-Mail", use_container_width=True, disabled=True,
                          help="Bitte E-Mail-Adresse prüfen")

    with col3:
        # TD-Anfrage Button - IMMER AKTIV, KEIN Empfänger vorgefüllt
        td_email_text = create_td_email_text(st.session_state.customer_data, detected_season)
        td_mailto_link = create_td_mailto_link(td_email_text)
        
        st.link_button("🔍 Reifen über TD anfragen", td_mailto_link,
                       use_container_width=True, type="secondary",
                       help="Anfrage an Teiledienst - Öffnet Outlook mit leerem An-Feld")

    with col4:
        if st.button("Warenkorb leeren", use_container_width=True, type="secondary"):
            clear_cart()
            st.session_state.pdf_created = False
            st.success("Warenkorb geleert!")
            st.rerun()

    with col5:
        if st.button("Weitere Reifen", use_container_width=True):
            st.switch_page("pages/01_Reifen_Suche.py")

    # Zweite Reihe für weniger wichtige Aktionen
    col6, col7, col8, col9, col10 = st.columns(5)
    
    with col10:
        if st.button("Reifen ausbuchen", use_container_width=True, type="primary"):
            if st.session_state.cart_items:
                st.success("Reifen erfolgreich ausgebucht!")
                clear_cart()
                st.session_state.pdf_created = False
                st.rerun()
            else:
                st.warning("Warenkorb ist leer!")

# ================================================================================================
# MAIN
# ================================================================================================
def main():
    init_session_state()

    # Logo Header ganz oben - EINHEITLICH WIE REIFEN-SUCHE
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    try:
        logo_path = "data/Logo_2.png"
        st.image(logo_path, width=400)
    except:
        st.markdown("### Ramsperger Automobile")
    st.markdown('</div>', unsafe_allow_html=True)

    # Fester Abstand NACH dem Logo (robust gegen Margin-Collapse)
    st.markdown('<div class="logo-spacer"></div>', unsafe_allow_html=True)

    if not st.session_state.cart_items:
        render_empty_cart()
        return

    render_cart_content()
    total, breakdown = get_cart_total()
    render_price_summary(total, breakdown)
    render_customer_data()
    
    # Filial- und Mitarbeiterauswahl mit festen Datenstrukturen
    render_filial_mitarbeiter_selection()
    
    detected = render_scenario_selection()
    render_actions(total, breakdown, detected)

if __name__ == "__main__":
    main()