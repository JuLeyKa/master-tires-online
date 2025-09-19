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
# GLOBALE VARIABLEN FÜR HEADER-DATEN (werden in create_header_footer genutzt)
# ================================================================================================
_header_data = {}

def set_header_data(customer_data, selected_filial_info, selected_mitarbeiter_info, page_count):
    """Setzt die globalen Header-Daten für die PDF-Generierung"""
    global _header_data
    _header_data = {
        'customer_data': customer_data,
        'selected_filial_info': selected_filial_info,
        'selected_mitarbeiter_info': selected_mitarbeiter_info,
        'page_count': page_count
    }

# ================================================================================================
# ERWEITERTE HEADER-FUNKTION MIT ORIGINALEN TABLE-LAYOUTS
# ================================================================================================
def draw_table_on_canvas(canvas, table_data, table_style, col_widths, x, y):
    """Zeichnet eine Tabelle mit exakt dem originalen Layout auf Canvas"""
    # Tabellen-Maße berechnen
    total_width = sum(col_widths)
    row_height = 15  # Standard-Zeilenhöhe
    num_rows = len(table_data)
    total_height = num_rows * row_height
    
    canvas.saveState()
    
    # Style-Einstellungen aus TableStyle extrahieren und anwenden
    for style_cmd in table_style._cmds:
        cmd = style_cmd[0]
        
        if cmd == 'BACKGROUND':
            # Hintergrundfarbe für Header
            start_col, start_row, end_col, end_row = style_cmd[1:5]
            color = style_cmd[5]
            if start_row == 0 and end_row == 0:  # Header-Zeile
                canvas.setFillColor(color)
                canvas.rect(x, y + total_height - row_height, total_width, row_height, fill=1, stroke=0)
        
        elif cmd == 'LINEBELOW':
            # Linie unter Header
            start_col, start_row, end_col, end_row = style_cmd[1:5]
            line_width = style_cmd[5]
            line_color = style_cmd[6]
            if start_row == 0:
                canvas.setStrokeColor(line_color)
                canvas.setLineWidth(line_width)
                canvas.line(x, y + total_height - row_height, x + total_width, y + total_height - row_height)
    
    # Text zeichnen
    for row_idx, row_data in enumerate(table_data):
        y_pos = y + total_height - (row_idx + 1) * row_height + 5  # +5 für Padding
        x_pos = x + 2  # +2 für Padding
        
        for col_idx, cell_data in enumerate(row_data):
            # Schriftart und -größe setzen
            if row_idx == 0:  # Header
                canvas.setFont("Helvetica-Bold", 5)
                canvas.setFillColor(colors.black)
            else:  # Daten
                canvas.setFont("Helvetica", 7)
                canvas.setFillColor(colors.black)
            
            # Text-Alignment (vereinfacht für CENTER)
            cell_width = col_widths[col_idx]
            text_width = canvas.stringWidth(str(cell_data), canvas._fontname, canvas._fontsize)
            text_x = x_pos + (cell_width - text_width) / 2  # Zentriert
            
            # Mehrzeiligen Text handhaben (vereinfacht)
            if '\n' in str(cell_data):
                lines = str(cell_data).split('\n')
                for line_idx, line in enumerate(lines):
                    line_y = y_pos - (line_idx * 8)  # 8 für Zeilenabstand
                    canvas.drawString(text_x, line_y, line)
            else:
                canvas.drawString(text_x, y_pos, str(cell_data))
            
            x_pos += cell_width
    
    # Tabellen-Rahmen zeichnen
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(0.5)
    canvas.rect(x, y, total_width, total_height, fill=0, stroke=1)
    
    # Vertikale Linien
    x_line = x
    for width in col_widths[:-1]:
        x_line += width
        canvas.line(x_line, y, x_line, y + total_height)
    
    # Horizontale Linien (nur zwischen Header und Daten)
    if num_rows > 1:
        canvas.line(x, y + total_height - row_height, x + total_width, y + total_height - row_height)
    
    canvas.restoreState()
    return total_height

def create_header_footer(canvas, doc):
    """EXAKTER Header mit originalen Table-Layouts auf jeder Seite"""
    canvas.saveState()
    width, height = A4
    margin = 20 * mm
    
    # Globale Header-Daten abrufen
    global _header_data
    customer_data = _header_data.get('customer_data', {})
    selected_filial_info = _header_data.get('selected_filial_info', {})
    selected_mitarbeiter_info = _header_data.get('selected_mitarbeiter_info', {})
    page_count = _header_data.get('page_count', 1)
    
    # Y-Position Tracker
    current_y = height - margin
    
    # === 1. LOGO LINKS OBEN ===
    try:
        logo_path = Path("data/Logo.png")
        if logo_path.exists():
            logo = ImageReader(str(logo_path))
            logo_width = 65 * mm
            logo_height = 18 * mm
            canvas.drawImage(logo, margin, current_y - logo_height, 
                           width=logo_width, height=logo_height, 
                           mask='auto', preserveAspectRatio=True)
        else:
            # Fallback Text
            canvas.setFont("Helvetica-Bold", 12)
            canvas.setFillColor(colors.black)
            canvas.drawString(margin, current_y - 12, "RAMSPERGER")
            canvas.drawString(margin, current_y - 24, "AUTOMOBILE")
    except Exception:
        # Fallback Text
        canvas.setFont("Helvetica-Bold", 12)
        canvas.setFillColor(colors.black)
        canvas.drawString(margin, current_y - 12, "RAMSPERGER")
        canvas.drawString(margin, current_y - 24, "AUTOMOBILE")
    
    # === 2. ANGEBOT ZENTRIERT ===
    canvas.setFont("Helvetica-Bold", 14)
    canvas.setFillColor(colors.black)
    angebot_width = canvas.stringWidth("ANGEBOT", "Helvetica-Bold", 14)
    canvas.drawString((width - angebot_width) / 2, current_y - 20, "ANGEBOT")
    
    # "unverbindlich" zentriert darunter
    canvas.setFont("Helvetica", 8)
    unverb_width = canvas.stringWidth("unverbindlich", "Helvetica", 8)
    canvas.drawString((width - unverb_width) / 2, current_y - 30, "unverbindlich")
    
    current_y -= 50
    
    # === 3. FIRMENADRESSE ===
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.black)
    canvas.drawString(margin, current_y, "Ramsperger Automobile . Postfach 1516 . 73223 Kirchheim u.T.")
    current_y -= 18
    
    # === 4. ORIGINALE KUNDENDATEN-TABELLE EXAKT NACHBAUEN ===
    date_today = datetime.now()
    date_str = date_today.strftime('%d.%m.%Y')
    
    # Kundendaten links zusammenbauen (EXAKT wie im Original)
    left_address_parts = []
    if customer_data and customer_data.get('name'):
        if customer_data.get('anrede') and customer_data.get('name'):
            left_address_parts.append(f"{customer_data['anrede']}")
            left_address_parts.append(f"{customer_data['name']}")
        elif customer_data.get('name'):
            left_address_parts.append(customer_data['name'])
        
        if customer_data.get('strasse'):
            strasse_haus = customer_data['strasse']
            if customer_data.get('hausnummer'):
                strasse_haus += f" {customer_data['hausnummer']}"
            left_address_parts.append(strasse_haus)
        
        if customer_data.get('plz') and customer_data.get('ort'):
            left_address_parts.append(f"{customer_data['plz']} {customer_data['ort']}")
    
    left_address_text = "\n".join(left_address_parts) if left_address_parts else ""
    
    # Rechte Spalte: Geschäftsdaten (EXAKT wie im Original)
    right_data_parts = []
    payment_line = "Bei Zahlungen bitte Rechnungs-Nr. und Kunden-Nr. angeben."
    right_data_parts.append(f"Datum (= Tag der Lieferung): {date_str}")
    
    if customer_data:
        if customer_data.get('kunden_nr'):
            right_data_parts.append(f"Kunden-Nr.: {customer_data['kunden_nr']}")
        if customer_data.get('abnehmer_gruppe'):
            right_data_parts.append(f"Abnehmer-Gruppe: {customer_data['abnehmer_gruppe']}")
        if customer_data.get('auftrags_nr'):
            right_data_parts.append(f"Auftrags-Nr.: {customer_data['auftrags_nr']}")
        if customer_data.get('betriebs_nr'):
            right_data_parts.append(f"Betriebs-Nr.: {customer_data['betriebs_nr']}")
        if customer_data.get('leistungsdatum'):
            leistung_str = format_date_german(customer_data['leistungsdatum'])
            if leistung_str:
                right_data_parts.append(f"Leistungsdatum: {leistung_str}")
    
    right_data_text = "\n".join(right_data_parts) if right_data_parts else ""
    
    # ORIGINALE Adress-Tabelle (EXAKT wie im Original mit first line size=7)
    addr_data = [
        [
            left_address_text,
            "",  # Leerraum
            f'{payment_line}\n{right_data_text}'  # Erste Zeile wird separat behandelt
        ]
    ]
    
    # Adress-Tabelle zeichnen mit originalen Spaltenbreiten
    addr_col_widths = [5*cm, 7*cm, 5*cm]
    addr_table_height = draw_address_table_special(canvas, addr_data, addr_col_widths, margin, current_y - 60, payment_line, right_data_text, left_address_text)
    current_y -= addr_table_height + 20
    
    # === 5. SEITENZAHL ===
    page_num = canvas.getPageNumber()
    canvas.setFont("Helvetica", 9)
    page_text = f"Seite {page_num} von {page_count}"
    page_width = canvas.stringWidth(page_text, "Helvetica", 9)
    canvas.drawString(width - margin - page_width, current_y, page_text)
    current_y -= 20
    
    # === 6. ORIGINALE FAHRZEUGDATEN-TABELLE ===
    serviceberater_name = ""
    if selected_mitarbeiter_info:
        serviceberater_name = selected_mitarbeiter_info.get('name', '')
    
    vehicle_headers = [
        "Amtl. Kennzeichen", "Typ/\nModellschlüssel", "Datum\nErstzulassung",
        "Fahrzeug-Ident.-Nr.", "Fzg.-\nAnnahmedatum", "km-Stand\nFahrzeugannahme", "Serviceberater"
    ]
    
    vehicle_row = [
        customer_data.get('kennzeichen', '') if customer_data else '',
        customer_data.get('typ_modellschluessel', '') if customer_data else '',
        format_date_german(customer_data.get('erstzulassung')) if customer_data else '',
        customer_data.get('fahrgestellnummer', '') if customer_data else '',
        format_date_german(customer_data.get('fahrzeugannahme')) if customer_data else '',
        customer_data.get('km_stand', '') if customer_data else '',
        serviceberater_name
    ]
    
    vehicle_data = [vehicle_headers, vehicle_row]
    
    # ORIGINALE TableStyle nachbauen
    vehicle_style = TableStyle([
        ('BACKGROUND',(0,0),(-1,0), colors.Color(0.95, 0.95, 0.95)),
        ('TEXTCOLOR',(0,0),(-1,0), colors.black),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,0),5),
        ('FONTSIZE',(0,1),(-1,-1),7),
        ('BOTTOMPADDING',(0,0),(-1,-1),2),
        ('TOPPADDING',(0,0),(-1,-1),2),
        ('LINEBELOW',(0,0),(-1,0),0.5,colors.black),
        ('FONTNAME',(0,1),(-1,-1),'Helvetica'),
        ('TEXTCOLOR',(0,1),(-1,-1), colors.black),
    ])
    
    vehicle_col_widths = [2.7*cm, 2.3*cm, 2.2*cm, 3.8*cm, 2.4*cm, 2.8*cm, 3.0*cm]
    vehicle_table_height = draw_table_on_canvas(canvas, vehicle_data, vehicle_style, vehicle_col_widths, margin, current_y - 35)
    current_y -= vehicle_table_height + 15
    
    # === 7. HU/AU UND KOSTENVORANSCHLAG TEXT ===
    canvas.setFont("Helvetica", 9)
    if customer_data and customer_data.get('hu_au_datum'):
        canvas.drawString(margin, current_y, f"Ihre nächste HU/AU ist: {customer_data['hu_au_datum']}")
        current_y -= 12
    
    kostenvoranschlag_text = "Kostenvoranschläge werden im unzerlegten Zustand erstellt. Schäden die erst nach der Demontage sichtbar werden, sind hierbei nicht berücksichtigt!"
    # Text umbrechen wenn zu lang
    max_width = width - 2 * margin
    if canvas.stringWidth(kostenvoranschlag_text, "Helvetica", 9) > max_width:
        # Vereinfachte Textaufteilung
        line1 = "Kostenvoranschläge werden im unzerlegten Zustand erstellt. Schäden die erst nach der"
        line2 = "Demontage sichtbar werden, sind hierbei nicht berücksichtigt!"
        canvas.drawString(margin, current_y, line1)
        current_y -= 12
        canvas.drawString(margin, current_y, line2)
    else:
        canvas.drawString(margin, current_y, kostenvoranschlag_text)
    
    canvas.restoreState()

def draw_address_table_special(canvas, addr_data, col_widths, x, y, payment_line, right_data_text, left_address_text):
    """Spezielle Funktion für Adress-Tabelle mit unterschiedlichen Schriftgrößen"""
    canvas.saveState()
    
    # Kundendaten links (Schriftgröße 8)
    if left_address_text:
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.black)
        lines = left_address_text.split('\n')
        y_pos = y
        for line in lines:
            canvas.drawString(x + 2, y_pos, line)
            y_pos -= 12
    
    # Geschäftsdaten rechts - erste Zeile kleiner (Schriftgröße 7)
    right_x = x + col_widths[0] + col_widths[1]
    y_pos = y
    
    # Erste Zeile (Bei Zahlungen...) mit Schriftgröße 7
    canvas.setFont("Helvetica", 7)
    canvas.drawString(right_x, y_pos, payment_line)
    y_pos -= 10
    
    # Restliche Zeilen mit Schriftgröße 8
    if right_data_text:
        canvas.setFont("Helvetica", 8)
        lines = right_data_text.split('\n')
        for line in lines:
            canvas.drawString(right_x, y_pos, line)
            y_pos -= 12
    
    canvas.restoreState()
    return 60  # Geschätzte Höhe der Adress-Tabelle

# ================================================================================================
# PDF LAYOUT MIT FESTEM HEADER - ORIGINALE TABELLEN ERHALTEN
# ================================================================================================
def create_professional_pdf(customer_data, detected_season, cart_items, cart_quantities, cart_services, selected_filial_info, selected_mitarbeiter_info):
    """Erstellt PDF mit festem Header auf jeder Seite - ALLE ORIGINALEN LAYOUTS ERHALTEN"""
    if not cart_items:
        return None

    buffer = io.BytesIO()
    
    # Seiten zählen für Header-Info
    total_pages = 2  # Standardmäßig 2 Seiten
    
    # Header-Daten global setzen
    set_header_data(customer_data, selected_filial_info, selected_mitarbeiter_info, total_pages)
    
    # VERGRÖSSERTER TOP-MARGIN für erweiterten Header
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=140*mm,  # VERGRÖSSERT für erweiterten Header
        bottomMargin=25*mm
    )

    # Styles mit optimierten Schriftgrößen (UNVERÄNDERT)
    styles = getSampleStyleSheet()
    
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
    
    # === HAUPTTABELLE IM NEUEN STIL (UNVERÄNDERT) ===
    main_headers = [
        "Nr.", "Arbeitsposition/\nTeilenummer", "Bezeichnung", 
        "Mit-\narbeiter", "Einzel-\npreis", "Menge/\nZeit", "Rabatt", "Steuer-\nCode", "Betrag\nEUR"
    ]
    
    main_table_data = [main_headers]
    total_netto, _ = get_cart_total(cart_items, cart_quantities, cart_services)
    position_counter = 1
    
    # ERST ALLE REIFEN
    for item in cart_items:
        quantity = cart_quantities.get(item['id'], 4)
        reifen_kosten_netto = (item['Preis_EUR'] / 1.19) * quantity
        
        main_table_data.append([
            str(position_counter),
            item['Teilenummer'],
            f"{item['Reifengröße']} - {item['Fabrikat']} {item['Profil']}",
            "",
            format_currency_german(item['Preis_EUR'] / 1.19),
            f"{quantity},00 Stück",
            "",
            "#3",
            format_currency_german(reifen_kosten_netto)
        ])
        position_counter += 1
    
    # DANN ALLE SERVICES - JEDES SERVICE ALS EIGENE POSITION
    for item in cart_items:
        selected_packages = cart_services.get(item['id'], [])
        if selected_packages:
            quantity = cart_quantities.get(item['id'], 4)
            
            # Jedes Service-Paket als eigene Position (keine Unterzeilen mehr)
            for package in selected_packages:
                brutto_pkg_price = float(package['preis'])
                netto_pkg_price = brutto_pkg_price / 1.19
                
                main_table_data.append([
                    str(position_counter),
                    package['positionsnummer'],
                    package['bezeichnung'].upper(),
                    "",
                    format_currency_german(netto_pkg_price),
                    "1,00 Stück",  # Service-Pakete sind immer 1x (nicht quantity!)
                    "",
                    "#3",
                    format_currency_german(netto_pkg_price)
                ])
                position_counter += 1

    # Haupttabelle im neuen Stil (UNVERÄNDERT)
    main_table = Table(main_table_data, colWidths=[1.1*cm, 2.6*cm, 5.2*cm, 1.2*cm, 1.8*cm, 1.8*cm, 1.1*cm, 1.1*cm, 1.9*cm])
    main_table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0), colors.Color(0.95, 0.95, 0.95)),
        ('TEXTCOLOR',(0,0),(-1,0), colors.black),
        ('FONTNAME',(0,0),(-1,0),'Helvetica'),
        ('FONTSIZE',(0,0),(-1,0),6),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('FONTNAME',(0,1),(-1,-1),'Helvetica'),
        ('FONTSIZE',(0,1),(-1,-1),8),
        ('LEFTPADDING',(0,0),(-1,-1),2),
        ('RIGHTPADDING',(0,0),(-1,-1),2),
        ('TOPPADDING',(0,0),(-1,-1),2),
        ('BOTTOMPADDING',(0,0),(-1,-1),2),
        ('LINEBELOW',(0,0),(-1,0),0.5,colors.black),
        ('ALIGN',(4,1),(-1,-1),'RIGHT'),
        ('ALIGN',(5,1),(5,-1),'CENTER'),
        ('ALIGN',(-1,1),(-1,-1),'CENTER'),
    ]))
    
    story.append(main_table)
    story.append(Spacer(1, 12))

    # GARANTIE-TEXTE (UNVERÄNDERT)
    radschrauben_text = """Wir weisen darauf hin, dass die Radschrauben nach 50 - 100 km nachgezogen werden müssen. Die max. Einlagerungszeit beträgt 7 Monate, bei Überschreitung erfolgt eine weitere Saisonabrechnung. Die zur Aufbewahrung übergebenen Räder müssen innerhalb von 12 Monate abgeholt werden."""
    story.append(Paragraph(radschrauben_text, small_style))
    story.append(Spacer(1, 8))
    
    garantie_text = """Reifen/Kompletträder in dieser Rechnung sind inklusive kostenloser 36 Monate Reifen Garantie gemäß den Bedingungen im Reifen Garantie Pass (Original Rechnung oder Rechnungskopie bitte als Garantienachweis im Fahrzeug mitführen)"""
    story.append(Paragraph(garantie_text, small_style))
    story.append(Spacer(1, 12))

    # Gesamtbetrag (UNVERÄNDERT)
    story.append(Paragraph(f"Gesamtbetrag (netto): {format_currency_german(total_netto)}", 
                          ParagraphStyle('NettoTotal', parent=normal_style, alignment=TA_RIGHT)))
    story.append(Spacer(1, 15))

    # Zwischensumme (UNVERÄNDERT)
    story.append(Paragraph("Zwischensumme", ParagraphStyle('Zwischensumme', parent=normal_style, alignment=TA_RIGHT)))
    story.append(Paragraph(format_currency_german(total_netto), ParagraphStyle('ZwischensummeWert', parent=normal_style, alignment=TA_RIGHT, fontName='Helvetica-Bold')))

    # Footer Seite 1 (UNVERÄNDERT)
    story.append(Spacer(1, 15))
    footer_text1 = "Die Lieferung auf Rechnung Dritter (z.B. Agenturware) erfolgt im Namen und für Rechnung des Leistungserbringers. Ggf. enthaltene USt. ist den beigefügten Belegen zu entnehmen."
    story.append(Paragraph(footer_text1, small_style))
    story.append(Spacer(1, 8))

    # Firmen-Footer Seite 1 (UNVERÄNDERT)
    if selected_filial_info:
        filial_adresse = selected_filial_info.get('adresse', 'Robert-Bosch-Str. 9-11 | 72622 Nürtingen')
        filial_telefon = selected_filial_info.get('zentrale', '07022/9211-0')
    else:
        filial_adresse = "Robert-Bosch-Str. 9-11 | 72622 Nürtingen"
        filial_telefon = "07022/9211-0"

    footer_data1 = [
        [
            Paragraph(f"Ramsperger Automobile<br/>GmbH &amp; Co.KG<br/>{filial_adresse}<br/>Telefon ({filial_telefon})<br/>Telefax ({filial_telefon.replace('-0', '-613')})<br/>eMail:<br/>info@ramsperger-automobile.de<br/>Internet:<br/>www.ramsperger-automobile.de", small_style),
            Paragraph("Bankverbindung:<br/>Volksbank Mittlerer Neckar eG<br/>IBAN:<br/>DE36 6129 0120 0439 6380 03<br/>BIC: GENODES1NUE", small_style),
            Paragraph("Rechtsform: KG Sitz: Kirchheim u. T.<br/>Amtsgericht Stuttgart<br/>Handelsregister: HRA 231034<br/>USt-Id.Nr. DE 199 195 203<br/>Steuer-Nr.69026/26107", small_style),
            Paragraph("Komplementär:<br/>Ramsperger Automobile<br/>Verwaltungs-GmbH<br/>Sitz Kirchheim u.T.<br/>HRB: 231579<br/>Geschäftsführer:<br/>Frank Eberhart", small_style)
        ]
    ]
    
    footer_table1 = Table(footer_data1, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    footer_table1.setStyle(TableStyle([
        ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
        ('FONTSIZE',(0,0),(-1,-1),6),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),1),
        ('RIGHTPADDING',(0,0),(-1,-1),1),
    ]))
    story.append(footer_table1)

    # === SEITE 2: ÜBERTRAG UND MWST (Header wird automatisch gezeichnet) ===
    story.append(PageBreak())

    # Haupttabelle Header + Übertrag (UNVERÄNDERT)
    main_headers_page2 = [
        "Nr.", "Arbeitsposition/\nTeilenummer", "Bezeichnung", 
        "Mit-\narbeiter", "Einzel-\npreis", "Menge/\nZeit", "Rabatt", "Steuer-\nCode", "Betrag\nEUR"
    ]
    
    uebertrag_data = [
        main_headers_page2,
        ["", "", "Übertrag", "", "", "", "", "", format_currency_german(total_netto)]
    ]
    
    uebertrag_table = Table(uebertrag_data, colWidths=[0.8*cm, 2.2*cm, 4.2*cm, 1.0*cm, 1.4*cm, 1.4*cm, 1.0*cm, 1.0*cm, 1.6*cm])
    uebertrag_table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0), colors.whitesmoke),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,0),7),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('FONTNAME',(0,1),(-1,-1),'Helvetica'),
        ('FONTSIZE',(0,1),(-1,-1),8),
        ('LEFTPADDING',(0,0),(-1,-1),2),
        ('RIGHTPADDING',(0,0),(-1,-1),2),
        ('TOPPADDING',(0,0),(-1,-1),2),
        ('BOTTOMPADDING',(0,0),(-1,-1),2),
        ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ('ALIGN',(-1,1),(-1,-1),'RIGHT'),
        ('FONTNAME',(0,1),(-1,1),'Helvetica-Bold'),
    ]))
    
    story.append(uebertrag_table)
    story.append(Spacer(1, 15))

    # Rest der Seite 2 (UNVERÄNDERT)
    date_today = datetime.now()
    gueltig_bis = date_today + timedelta(days=30)
    gueltig_str = gueltig_bis.strftime('%d-%m-%Y')
    story.append(Paragraph(f"Angebot gültig bis {gueltig_str}", normal_style))

    # Serviceberater Text (UNVERÄNDERT)
    if selected_mitarbeiter_info:
        mitarbeiter_name = selected_mitarbeiter_info.get('name', '')
        mitarbeiter_email = selected_mitarbeiter_info.get('email', '')
        
        if "E-Mail" in selected_mitarbeiter_info.get('position', ''):
            service_text = f"Es bediente Sie Ihr Service-Team. Für Rückfragen stehen wir Ihnen gerne zur Verfügung. e-Mail: {mitarbeiter_email}"
        else:
            service_text = f"Es bediente Sie Ihr Serviceberater Herr {mitarbeiter_name}. Für Rückfragen stehe ich Ihnen gerne persönlich zur Verfügung. e-Mail: {mitarbeiter_email}"
        
        story.append(Paragraph(service_text, normal_style))
    
    story.append(Paragraph('Besuchen Sie uns doch im Internet. Unter www.ramsperger-automobile.de finden Sie alles über uns und "...die Menschen machen den Unterschied!"', normal_style))
    story.append(Spacer(1, 15))

    # === MWST-TABELLE (UNVERÄNDERT) ===
    mwst_betrag = total_netto * 0.19
    brutto_gesamt = total_netto + mwst_betrag

    mwst_headers = ["Steuer-\nCode", "Arbeit", "Material", "Steuerbasis", "%-Mwst", "Mwst", "Steuerbasis\nAltwert", "Mwst auf\nAltwert", "Gesamtbetrag"]
    mwst_data = [
        mwst_headers,
        ["#3", format_currency_german(total_netto), "0,00", format_currency_german(total_netto), "19%", format_currency_german(mwst_betrag), "0,00", "0,00", ""],
        ["Summe", format_currency_german(total_netto), "0,00", format_currency_german(total_netto), "", format_currency_german(mwst_betrag), "0,00", "", format_currency_german(brutto_gesamt)]
    ]

    mwst_table = Table(mwst_data, colWidths=[1*cm, 1.3*cm, 1.3*cm, 1.8*cm, 1*cm, 1.3*cm, 1.3*cm, 1.2*cm, 1.8*cm])
    mwst_table.setStyle(TableStyle([
        ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
        ('FONTSIZE',(0,0),(-1,-1),7),
        ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ('BACKGROUND',(0,0),(-1,0), colors.lightgrey),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('ALIGN',(1,1),(-1,-1),'RIGHT'),
        ('LEFTPADDING',(0,0),(-1,-1),2),
        ('RIGHTPADDING',(0,0),(-1,-1),2),
    ]))

    story.append(mwst_table)
    story.append(Spacer(1, 8))
    story.append(Paragraph("Zahlungsziel: Bar / Kasse bar", normal_style))

    # PDF erstellen mit festem Header auf jeder Seite
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