import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import urllib.parse
import io
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ================================================================================================
# FESTE FILIAL- UND MITARBEITERDATEN (ERSETZT EXCEL-ANBINDUNG) - UNVERÄNDERT
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
# SERVICE-PAKETE LADEN UND VERARBEITEN - UNVERÄNDERT
# ================================================================================================
@st.cache_data
def load_service_packages():
    """Lädt die Service-Pakete aus der CSV"""
    try:
        csv_path = Path("data/ramsperger_services_config.csv")
        if csv_path.exists():
            df = pd.read_csv(csv_path, encoding='utf-8')
            return df
        else:
            return pd.DataFrame(columns=['Positionsnummer', 'Bezeichnung', 'Teilenummer_Detail', 'Preis', 'Hinweis', 'Zoll'])
    except Exception as e:
        return pd.DataFrame(columns=['Positionsnummer', 'Bezeichnung', 'Teilenummer_Detail', 'Preis', 'Hinweis', 'Zoll'])

def get_service_package_by_positionsnummer(positionsnummer):
    """Holt ein Service-Paket anhand der Positionsnummer"""
    service_df = load_service_packages()
    if service_df.empty:
        return None
    
    package = service_df[service_df['Positionsnummer'] == positionsnummer]
    if not package.empty:
        return package.iloc[0].to_dict()
    return None

# ================================================================================================
# PERSONALISIERTE ANREDE FUNKTIONEN - UNVERÄNDERT
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

# ================================================================================================
# SAISON-ERKENNUNG - UNVERÄNDERT
# ================================================================================================
def detect_cart_season(cart_items):
    """Erkennt die dominante Saison im Warenkorb"""
    if not cart_items:
        return "neutral"
    
    saison_counts = {"Winter": 0, "Sommer": 0, "Ganzjahres": 0, "Unbekannt": 0}
    
    for item in cart_items:
        saison = item.get('Saison', 'Unbekannt')
        saison_counts[saison] = saison_counts.get(saison, 0) + 1
    
    total_items = sum(saison_counts.values())
    if total_items == 0:
        return "neutral"
    
    # Dominante Saison finden
    dominant_season, dominant_count = sorted(saison_counts.items(), key=lambda x: x[1], reverse=True)[0]
    
    # Nur als dominant werten wenn mind. 70% der Reifen diese Saison haben
    if dominant_count / total_items >= 0.7:
        return dominant_season.lower()
    else:
        return "gemischt"

def get_season_greeting_text(detected_season):
    """Gibt saisonspezifische Begrüßungstexte zurück"""
    season_texts = {
        "winter": {
            "greeting": "der Winter steht vor der Tür und die Zeichen stehen auf kälter werdende Temperaturen.",
            "transition": "Jetzt wird es auch Zeit für Ihre Winterreifen von Ihrem Auto.",
            "season_name": "Winter"
        },
        "sommer": {
            "greeting": "die warme Jahreszeit kommt und die Temperaturen steigen wieder.",
            "transition": "Jetzt wird es auch Zeit für Ihre Sommerreifen von Ihrem Auto.",
            "season_name": "Sommer"
        },
        "ganzjahres": {
            "greeting": "Sie denken über Ganzjahresreifen nach - eine praktische Lösung für das ganze Jahr.",
            "transition": "Jetzt wird es Zeit für Ihre neuen Allwetter-Reifen von Ihrem Auto.",
            "season_name": "Ganzjahres"
        },
        "gemischt": {
            "greeting": "Sie haben verschiedene Reifen-Optionen für unterschiedliche Anforderungen.",
            "transition": "Gerne stelle ich Ihnen die verschiedenen Möglichkeiten vor.",
            "season_name": "verschiedene"
        },
        "neutral": {
            "greeting": "Sie interessieren sich für neue Reifen für Ihr Fahrzeug.",
            "transition": "Gerne stelle ich Ihnen die passenden Optionen vor.",
            "season_name": "neue"
        }
    }
    return season_texts.get(detected_season, season_texts["neutral"])

# ================================================================================================
# SERVICE DETECTION FÜR DYNAMISCHE ÜBERSCHRIFT - UNVERÄNDERT
# ================================================================================================
def has_services_in_cart(cart_items, cart_services):
    """Prüft ob Services im Warenkorb aktiviert sind"""
    for item in cart_items:
        item_services = cart_services.get(item['id'], [])
        if item_services:  # Wenn Service-Pakete ausgewählt sind
            return True
    return False

def get_dynamic_title(cart_items, cart_services):
    """Generiert dynamische Überschrift basierend auf Warenkorb-Inhalt"""
    if has_services_in_cart(cart_items, cart_services):
        return "Angebot Reifen & Service"
    else:
        return "Angebot Reifen"

# ================================================================================================
# WARENKORB-BERECHNUNGEN - MIT NETTO-PREISEN (19% MWST ABZIEHEN)
# ================================================================================================
def calculate_position_total(item, quantity, selected_packages):
    """Berechnet Gesamtkosten für eine Position - BRUTTOPREISE ZU NETTO KONVERTIEREN"""
    # REIFEN: Bruttopreis zu Netto konvertieren (19% MwSt abziehen)
    brutto_reifen_preis = item['Preis_EUR']
    netto_reifen_preis = brutto_reifen_preis / 1.19  # 19% MwSt abziehen
    reifen_kosten_netto = netto_reifen_preis * quantity
    
    service_kosten_netto = 0.0
    
    # SERVICE-PAKETE: Bruttopreise zu Netto konvertieren
    for package in selected_packages:
        brutto_pkg_price = float(package['preis'])
        netto_pkg_price = brutto_pkg_price / 1.19  # 19% MwSt abziehen
        # Alle Service-Pakete sind Pauschalpreise
        service_kosten_netto += netto_pkg_price
    
    return reifen_kosten_netto, service_kosten_netto, reifen_kosten_netto + service_kosten_netto

def get_cart_total(cart_items, cart_quantities, cart_services):
    """Berechnet Gesamtsumme des Warenkorbs - NETTO-PREISE"""
    total = 0.0
    breakdown = {'reifen': 0.0, 'services': 0.0}
    
    for item in cart_items:
        quantity = cart_quantities.get(item['id'], 4)
        selected_packages = cart_services.get(item['id'], [])
        
        reifen_kosten, service_kosten, position_total = calculate_position_total(item, quantity, selected_packages)
        
        total += position_total
        breakdown['reifen'] += reifen_kosten
        breakdown['services'] += service_kosten
    
    return total, breakdown

# ================================================================================================
# FORMATIERUNGS-FUNKTIONEN FÜR PDF
# ================================================================================================
def format_currency_german(value: float) -> str:
    """Formatiert Euro-Beträge im deutschen Format"""
    s = f"{value:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s

def format_date_german(date_obj):
    """Formatiert Datum als deutschen String (DD.MM.YYYY)"""
    if not date_obj:
        return ""
    if hasattr(date_obj, 'strftime'):
        return date_obj.strftime('%d.%m.%Y')
    return str(date_obj)

# ================================================================================================
# 1:1 PDF LAYOUT NACH VORLAGE - KOMPLETT NEU
# ================================================================================================
def create_header_footer(canvas, doc):
    """Header und Footer nach Original-Vorlage"""
    canvas.saveState()
    width, height = A4
    margin = 20 * mm

    # === HEADER NACH ORIGINAL-VORLAGE ===
    # Logo/Firmenname links
    try:
        logo_path = Path("data/Logo.png")
        if logo_path.exists():
            logo = ImageReader(str(logo_path))
            # Logo links positionieren wie im Original
            logo_width = 60 * mm
            logo_height = 18 * mm
            canvas.drawImage(logo, margin, height - margin - logo_height, 
                           width=logo_width, height=logo_height, 
                           mask='auto', preserveAspectRatio=True)
        else:
            # Fallback Text falls Logo nicht gefunden
            canvas.setFont("Helvetica-Bold", 12)
            canvas.setFillColor(colors.black)
            canvas.drawString(margin, height - margin - 8, "RAMSPERGER")
            canvas.drawString(margin, height - margin - 20, "AUTOMOBILE")
    except Exception:
        # Fallback bei Fehlern
        canvas.setFont("Helvetica-Bold", 12)
        canvas.setFillColor(colors.black)
        canvas.drawString(margin, height - margin - 8, "RAMSPERGER")
        canvas.drawString(margin, height - margin - 20, "AUTOMOBILE")

    # ANGEBOT zentriert wie im Original
    canvas.setFont("Helvetica-Bold", 16)
    canvas.setFillColor(colors.black)
    text_width = canvas.stringWidth("ANGEBOT", "Helvetica-Bold", 16)
    canvas.drawString((width - text_width) / 2, height - margin - 8, "ANGEBOT")
    
    # "unverbindlich" zentriert darunter
    canvas.setFont("Helvetica", 8)
    text_width_unverb = canvas.stringWidth("unverbindlich", "Helvetica", 8)
    canvas.drawString((width - text_width_unverb) / 2, height - margin - 20, "unverbindlich")

    # Firmenadresse unter Header wie im Original
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.black)
    company_address = "Ramsperger Automobile . Postfach 1516 . 73223 Kirchheim u.T."
    canvas.drawString(margin, height - margin - 35, company_address)

    canvas.restoreState()

def create_professional_pdf(customer_data, detected_season, cart_items, cart_quantities, cart_services, selected_filial_info, selected_mitarbeiter_info):
    """Erstellt PDF im EXAKTEN Layout der Vorlage"""
    if not cart_items:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=35*mm,  # Platz für Header
        bottomMargin=20*mm
    )

    # Styles genau wie im Original
    styles = getSampleStyleSheet()
    
    # Standard-Textstil für Hauptinhalt
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        textColor=colors.black
    )
    
    small_style = ParagraphStyle(
        'Small',
        parent=styles['Normal'], 
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.black
    )

    story = []

    # === KUNDENDATEN UND GESCHÄFTSDATEN (wie im Original 2-spaltig) ===
    date_today = datetime.now()
    date_str = date_today.strftime('%d.%m.%Y')
    
    # Linke Spalte: Kundenadresse
    left_address_lines = []
    if customer_data and customer_data.get('name'):
        # Vollständige Adresse aufbauen
        if customer_data.get('anrede') and customer_data.get('name'):
            left_address_lines.append(f"{customer_data['anrede']}")
            left_address_lines.append(f"{customer_data['name']}")
        elif customer_data.get('name'):
            left_address_lines.append(customer_data['name'])
        
        # Straße + Hausnummer
        if customer_data.get('strasse'):
            strasse_haus = customer_data['strasse']
            if customer_data.get('hausnummer'):
                strasse_haus += f" {customer_data['hausnummer']}"
            left_address_lines.append(strasse_haus)
        
        # PLZ + Ort
        if customer_data.get('plz') and customer_data.get('ort'):
            left_address_lines.append(f"{customer_data['plz']} {customer_data['ort']}")
        elif customer_data.get('plz'):
            left_address_lines.append(customer_data['plz'])
        elif customer_data.get('ort'):
            left_address_lines.append(customer_data['ort'])

    # Rechte Spalte: Geschäftsdaten
    right_data_lines = []
    right_data_lines.append(f"Bei Zahlungen bitte Rechnungs-Nr. und Kunden-Nr. angeben.")
    right_data_lines.append(f"Datum (= Tag der Lieferung): {date_str}")
    
    if customer_data:
        if customer_data.get('kunden_nr'):
            right_data_lines.append(f"Kunden-Nr.: {customer_data['kunden_nr']}")
        if customer_data.get('abnehmer_gruppe'):
            right_data_lines.append(f"Abnehmer-Gruppe: {customer_data['abnehmer_gruppe']}")
        if customer_data.get('auftrags_nr'):
            right_data_lines.append(f"Auftrags-Nr.: {customer_data['auftrags_nr']}")
        if customer_data.get('betriebs_nr'):
            right_data_lines.append(f"Betriebs-Nr.: {customer_data['betriebs_nr']}")
        if customer_data.get('leistungsdatum'):
            leistung_str = format_date_german(customer_data['leistungsdatum'])
            if leistung_str:
                right_data_lines.append(f"Leistungsdatum: {leistung_str}")

    # Zwei-Spalten-Layout erstellen
    max_lines = max(len(left_address_lines), len(right_data_lines))
    
    # Listen auf gleiche Länge bringen
    while len(left_address_lines) < max_lines:
        left_address_lines.append("")
    while len(right_data_lines) < max_lines:
        right_data_lines.append("")

    # Tabelle für Address/Business Data
    addr_data = []
    for i in range(max_lines):
        addr_data.append([
            Paragraph(left_address_lines[i], normal_style),
            Paragraph(right_data_lines[i], normal_style)
        ])

    addr_table = Table(addr_data, colWidths=[9*cm, 8*cm])
    addr_table.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),0),
        ('RIGHTPADDING',(0,0),(-1,-1),0),
        ('TOPPADDING',(0,0),(-1,-1),1),
        ('BOTTOMPADDING',(0,0),(-1,-1),1),
    ]))
    story.append(addr_table)
    story.append(Spacer(1, 15))

    # === SEITENINFORMATION WIE IM ORIGINAL ===
    story.append(Paragraph("Seite 1 von 2", ParagraphStyle('PageInfo', parent=normal_style, alignment=TA_RIGHT)))
    story.append(Spacer(1, 10))

    # === FAHRZEUGDATEN-TABELLE WIE IM ORIGINAL ===
    if customer_data and (customer_data.get('kennzeichen') or customer_data.get('typ_modellschluessel') or customer_data.get('fahrgestellnummer')):
        
        # Serviceberater aus Auswahl
        serviceberater_name = ""
        if selected_mitarbeiter_info:
            serviceberater_name = selected_mitarbeiter_info.get('name', '')

        # Header-Zeile der Fahrzeugdaten-Tabelle (EXAKT wie im Original)
        vehicle_headers = [
            "Amtl. Kennzeichen",
            "Typ/\nModellschlüssel", 
            "Datum\nErstzulassung",
            "Fahrzeug-Ident.-Nr.",
            "Fzg.-\nAnnahmedatum",
            "km-Stand\nFahrzeugannahme",
            "Serviceberater"
        ]
        
        # Daten-Zeile
        vehicle_row = [
            customer_data.get('kennzeichen', ''),
            customer_data.get('typ_modellschluessel', ''),
            format_date_german(customer_data.get('erstzulassung')),
            customer_data.get('fahrgestellnummer', ''),
            format_date_german(customer_data.get('fahrzeugannahme')),
            customer_data.get('km_stand', ''),
            serviceberater_name
        ]
        
        vehicle_data = [vehicle_headers, vehicle_row]

        # Spaltenbreiten wie im Original
        vehicle_table = Table(vehicle_data, colWidths=[2.4*cm, 1.8*cm, 1.8*cm, 3.2*cm, 2.0*cm, 2.2*cm, 2.8*cm])
        vehicle_table.setStyle(TableStyle([
            # Header-Style
            ('BACKGROUND',(0,0),(-1,0), colors.grey),
            ('TEXTCOLOR',(0,0),(-1,0), colors.whitesmoke),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('FONTSIZE',(0,0),(-1,-1),7),
            ('BOTTOMPADDING',(0,0),(-1,-1),4),
            ('TOPPADDING',(0,0),(-1,-1),4),
            ('GRID',(0,0),(-1,-1),0.5,colors.black),
            # Datenzeilen
            ('FONTNAME',(0,1),(-1,-1),'Helvetica'),
            ('TEXTCOLOR',(0,1),(-1,-1), colors.black),
            ('FONTSIZE',(0,1),(-1,-1),8),
        ]))
        story.append(vehicle_table)
        story.append(Spacer(1, 12))

        # HU/AU Datum und Standard-Texte wie im Original
        if customer_data.get('hu_au_datum'):
            story.append(Paragraph(f"Ihre nächste HU/AU ist: {customer_data['hu_au_datum']}", normal_style))
        
        story.append(Paragraph("Kostenvoranschläge werden im unzerlegten Zustand erstellt. Schäden die erst nach der Demontage sichtbar werden, sind hierbei nicht berücksichtigt!", normal_style))
        story.append(Spacer(1, 15))

    # === HAUPTTABELLE FÜR POSITIONEN (EXAKT wie im Original) ===
    
    # Header der Haupttabelle
    main_headers = [
        "Nr.", "Arbeitsposition/\nTeilenummer", "Bezeichnung", "Mit-\narbeiter", 
        "Einzel-\npreis", "Menge/\nZeit", "Rabatt", "Steuer-\nCode", "Betrag\nEUR"
    ]
    
    main_table_data = [main_headers]
    
    # Positionen hinzufügen
    for i, item in enumerate(cart_items, 1):
        quantity = cart_quantities.get(item['id'], 4)
        selected_packages = cart_services.get(item['id'], [])
        
        reifen_kosten_netto, service_kosten_netto, _ = calculate_position_total(item, quantity, selected_packages)
        
        # Reifen-Position
        if selected_packages:
            # Service-Paket Struktur wie im Original
            service_package_info = f"SERVICE PAKET {item['Fabrikat'].upper()} {item['Profil'].upper()}"
            
            # Erste Zeile: Service-Paket Header
            main_table_data.append([
                str(i),
                f"Z{40000 + i}",  # Beispiel Service-Paket Nummer
                service_package_info,
                "",  # Mitarbeiter
                "",  # Einzelpreis
                f"{quantity},00 Stück",
                "",  # Rabatt
                "#3",  # Steuer-Code
                format_currency_german(reifen_kosten_netto + service_kosten_netto)
            ])
            
            # Unter-Positionen für Services
            for package in selected_packages:
                netto_pkg_price = float(package['preis']) / 1.19
                main_table_data.append([
                    "",  # Nr leer
                    package['positionsnummer'],
                    package['bezeichnung'].upper(),
                    "",  # Mitarbeiter
                    "",  # Einzelpreis
                    "",  # Menge
                    "",  # Rabatt
                    "",  # Steuer-Code
                    ""   # Betrag
                ])
                
                # Service-Details als weitere Zeilen
                if package.get('hinweis'):
                    main_table_data.append([
                        "", "", package['hinweis'], "", "", "", "", "", ""
                    ])
            
            # Reifen-Details
            reifendetails = f"{item['Reifengröße']} - {item['Fabrikat']} {item['Profil']}"
            main_table_data.append([
                "", "", reifendetails, "", "", "", "", "", ""
            ])
            
        else:
            # Nur Reifen ohne Service-Paket
            reifeninfo = f"{item['Reifengröße']} - {item['Fabrikat']} {item['Profil']}"
            main_table_data.append([
                str(i),
                item['Teilenummer'],
                reifeninfo,
                "",  # Mitarbeiter
                format_currency_german(item['Preis_EUR'] / 1.19),  # Netto-Preis
                f"{quantity},00 Stück",
                "",  # Rabatt
                "#3",  # Steuer-Code
                format_currency_german(reifen_kosten_netto)
            ])

    # Haupttabelle erstellen
    main_table = Table(main_table_data, colWidths=[1*cm, 2*cm, 4.5*cm, 1.2*cm, 1.5*cm, 1.5*cm, 1*cm, 1.2*cm, 1.8*cm])
    main_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND',(0,0),(-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0), colors.whitesmoke),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,0),7),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        
        # Datenzeilen
        ('FONTNAME',(0,1),(-1,-1),'Helvetica'),
        ('FONTSIZE',(0,1),(-1,-1),8),
        ('TEXTCOLOR',(0,1),(-1,-1), colors.black),
        ('LEFTPADDING',(0,0),(-1,-1),3),
        ('RIGHTPADDING',(0,0),(-1,-1),3),
        ('TOPPADDING',(0,0),(-1,-1),2),
        ('BOTTOMPADDING',(0,0),(-1,-1),2),
        
        # Rahmen
        ('GRID',(0,0),(-1,-1),0.5,colors.black),
        
        # Preise rechtsbündig
        ('ALIGN',(4,1),(-1,-1),'RIGHT'),
        ('ALIGN',(5,1),(5,-1),'CENTER'),
        ('ALIGN',(-1,1),(-1,-1),'RIGHT'),
    ]))
    
    story.append(main_table)
    story.append(Spacer(1, 15))

    # === STANDARD-TEXTE NACH DER HAUPTTABELLE (wie im Original) ===
    
    # Reifen/Kompletträder Garantie-Text
    garantie_text = """Reifen/Kompletträder in dieser Rechnung sind inklusive kostenloser 36 Monate Reifen 
Garantie gemäß den Bedingungen im Reifen Garantie Pass (Original Rechnung 
oder Rechnungskopie bitte als Garantienachweis im Fahrzeug mitführen)"""
    
    story.append(Paragraph(garantie_text, small_style))
    story.append(Spacer(1, 10))

    # === GESAMTBETRAG (NETTO) ===
    total_netto, breakdown = get_cart_total(cart_items, cart_quantities, cart_services)
    
    story.append(Paragraph(f"Gesamtbetrag (netto): {format_currency_german(total_netto)}", 
                          ParagraphStyle('NettoTotal', parent=normal_style, alignment=TA_RIGHT)))
    story.append(Spacer(1, 20))

    # === ZWEITE SEITE - ÜBERTRAG UND MWST-AUFSCHLÜSSELUNG ===
    story.append(PageBreak())
    
    # Übertrag
    story.append(Paragraph("Übertrag", ParagraphStyle('Uebertrag', parent=normal_style, alignment=TA_RIGHT)))
    story.append(Paragraph(format_currency_german(total_netto), ParagraphStyle('UebtragWert', parent=normal_style, alignment=TA_RIGHT, fontName='Helvetica-Bold')))
    story.append(Spacer(1, 15))

    # === ANGEBOT GÜLTIGKEITSDATUM (INTERAKTIV - 30 TAGE) ===
    gueltig_bis = date_today + timedelta(days=30)
    gueltig_str = gueltig_bis.strftime('%d-%m-%Y')
    story.append(Paragraph(f"Angebot gültig bis {gueltig_str}", normal_style))

    # === MITARBEITER-REFERENZ (INTERAKTIV) ===
    if selected_mitarbeiter_info:
        mitarbeiter_name = selected_mitarbeiter_info.get('name', '')
        mitarbeiter_email = selected_mitarbeiter_info.get('email', '')
        
        # Check if it's a collective email
        if "E-Mail" in selected_mitarbeiter_info.get('position', ''):
            # Collective email - generic formulation
            service_text = f"Es bediente Sie Ihr Service-Team. Für Rückfragen stehen wir Ihnen gerne zur Verfügung. e-Mail: {mitarbeiter_email}"
        else:
            # Individual employee
            service_text = f"Es bediente Sie Ihr Serviceberater Herr {mitarbeiter_name}. Für Rückfragen stehe ich Ihnen gerne persönlich zur Verfügung. e-Mail: {mitarbeiter_email}"
        
        story.append(Paragraph(service_text, normal_style))
    
    # Standard Schlusstext
    story.append(Paragraph('Besuchen Sie uns doch im Internet. Unter www.ramsperger-automobile.de finden Sie alles über uns und "...die Menschen machen den Unterschied!"', normal_style))
    story.append(Spacer(1, 20))

    # === MWST-AUFSCHLÜSSELUNG (wie im Original) ===
    mwst_betrag = total_netto * 0.19
    brutto_gesamt = total_netto + mwst_betrag

    # MwSt-Tabelle
    mwst_headers = ["Steuer-\nCode", "Arbeit", "Material", "Steuerbasis", "%-Mwst", "Mwst", "Steuerbasis\nAltwert", "Mwst auf\nAltwert", "Gesamtbetrag"]
    mwst_data = [
        mwst_headers,
        ["#3", format_currency_german(total_netto), "0,00", format_currency_german(total_netto), "19%", format_currency_german(mwst_betrag), "0,00", "0,00", ""],
        ["Summe", format_currency_german(total_netto), "0,00", format_currency_german(total_netto), "", format_currency_german(mwst_betrag), "0,00", "", format_currency_german(brutto_gesamt)]
    ]

    mwst_table = Table(mwst_data, colWidths=[1*cm, 1.5*cm, 1.5*cm, 1.8*cm, 1*cm, 1.5*cm, 1.5*cm, 1.2*cm, 1.8*cm])
    mwst_table.setStyle(TableStyle([
        ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
        ('FONTSIZE',(0,0),(-1,-1),8),
        ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ('BACKGROUND',(0,0),(-1,0), colors.lightgrey),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('ALIGN',(1,1),(-1,-1),'RIGHT'),
    ]))

    story.append(mwst_table)
    story.append(Spacer(1, 10))

    # Zahlungsziel
    story.append(Paragraph("Zahlungsziel: Bar / Kasse bar", normal_style))
    story.append(Spacer(1, 20))

    # === FOOTER MIT FILIAL-INFORMATIONEN (INTERAKTIV) ===
    footer_text = "Die Lieferung auf Rechnung Dritter (z.B. Agenturware) erfolgt im Namen und für Rechnung des Leistungserbringers. Ggf. enthaltene USt. ist den beigefügten Belegen zu entnehmen."
    story.append(Paragraph(footer_text, small_style))
    story.append(Spacer(1, 15))

    # Firmen-Footer-Info (angepasst an gewählte Filiale)
    if selected_filial_info:
        filial_adresse = selected_filial_info.get('adresse', 'Robert-Bosch-Str. 9-11\n72622 Nürtingen')
        filial_telefon = selected_filial_info.get('zentrale', '07022/9211-0')
    else:
        # Default Filiale
        filial_adresse = "Robert-Bosch-Str. 9-11\n72622 Nürtingen"
        filial_telefon = "07022/9211-0"

    # Footer-Informations-Tabelle (ohne QR-Code, aber alle anderen Infos)
    footer_data = [
        [
            Paragraph("Ramsperger Automobile<br/>GmbH &amp; Co.KG<br/>" + filial_adresse.replace('\n', '<br/>') + f"<br/>Telefon ({filial_telefon})<br/>Telefax ({filial_telefon.replace('-0', '-613')})<br/>eMail:<br/>info@ramsperger-automobile.de<br/>Internet:<br/>www.ramsperger-automobile.de", small_style),
            
            Paragraph("Bankverbindung:<br/>Volksbank Mittlerer Neckar eG<br/>IBAN:<br/>DE36 6129 0120 0439 6380 03<br/>BIC: GENODES1NUE", small_style),
            
            Paragraph("Rechtsform: KG Sitz: Kirchheim u. T.<br/>Amtsgericht Stuttgart<br/>Handelsregister: HRA 231034<br/>USt-Id.Nr. DE 199 195 203<br/>Steuer-Nr.69026/26107", small_style),
            
            Paragraph("Komplementär:<br/>Ramsperger Automobile<br/>Verwaltungs-GmbH<br/>Sitz Kirchheim u.T.<br/>HRB: 231579<br/>Geschäftsführer:<br/>Frank Eberhart", small_style)
        ]
    ]
    
    footer_table = Table(footer_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    footer_table.setStyle(TableStyle([
        ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
        ('FONTSIZE',(0,0),(-1,-1),7),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),2),
        ('RIGHTPADDING',(0,0),(-1,-1),2),
    ]))
    
    story.append(footer_table)

    # PDF erstellen
    doc.build(story, onFirstPage=create_header_footer, onLaterPages=create_header_footer)
    buffer.seek(0)
    return buffer.getvalue()

# ================================================================================================
# E-MAIL TEXT & MAILTO (unverändert) 
# ================================================================================================
_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

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
# TD-ANFRAGE FUNKTIONEN - UNVERÄNDERT
# ================================================================================================
def create_td_email_text(customer_data, detected_season, cart_items, cart_quantities):
    """Erstellt den E-Mail-Text für die TD-Anfrage"""
    if not cart_items:
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
    
    for i, item in enumerate(cart_items, 1):
        quantity = cart_quantities.get(item['id'], 4)
        
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

def create_td_mailto_link(td_email_text, cart_items):
    """Erstellt den mailto-Link für die TD-Anfrage - KEIN Empfänger vorgefüllt"""
    subject = f"Reifenanfrage Ramsperger Automobile - {len(cart_items)} Position(en)"
    body_crlf = _normalize_crlf(td_email_text)
    subject_encoded = urllib.parse.quote(subject, safe="")
    body_encoded = _urlencode_mail_body(body_crlf)
    
    # WICHTIG: mailto: ohne E-Mail-Adresse = leeres An-Feld in Outlook
    return f"mailto:?subject={subject_encoded}&body={body_encoded}"