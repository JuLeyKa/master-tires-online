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
# SERVICE-PAKETE LADEN UND VERARBEITEN
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

# ================================================================================================
# SAISON-ERKENNUNG
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
# SERVICE DETECTION FÜR DYNAMISCHE ÜBERSCHRIFT
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
# WARENKORB-BERECHNUNGEN - ANGEPASST FÜR NEUE SERVICE-PAKETE
# ================================================================================================
def calculate_position_total(item, quantity, selected_packages):
    """Berechnet Gesamtkosten für eine Position mit neuen Service-Paketen"""
    reifen_kosten = item['Preis_EUR'] * quantity
    service_kosten = 0.0
    
    # Service-Pakete durchgehen
    for package in selected_packages:
        pkg_price = float(package['preis'])
        
        # Prüfen ob pro Reifen oder pauschal
        # Vereinfachte Logik: wenn "REIFENSERVICE" im Namen, dann pro Reifen
        if 'REIFENSERVICE' in package['bezeichnung'].upper():
            service_kosten += pkg_price * quantity
        else:
            service_kosten += pkg_price
    
    return reifen_kosten, service_kosten, reifen_kosten + service_kosten

def get_cart_total(cart_items, cart_quantities, cart_services):
    """Berechnet Gesamtsumme des Warenkorbs mit neuen Service-Paketen"""
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
# PDF GENERATION - ANGEPASST FÜR NEUE SERVICE-PAKETE
# ================================================================================================
def format_eur(value: float) -> str:
    """Formatiert Euro-Beträge"""
    s = f"{value:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €"

def _header_footer(canvas, doc, selected_filial_info):
    """Header mit Ramsperger Logo + Footer mit Filialinformationen"""
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
    
    # Filialinformationen
    if selected_filial_info:
        filial_text = f"Ramsperger Automobile {selected_filial_info.get('bereich', '')} {selected_filial_info.get('adresse', '')} Telefon: {selected_filial_info.get('zentrale', '')}"
        canvas.drawString(margin, margin - 8, filial_text)

    canvas.restoreState()

def _p(text, style):
    """Hilfsfunktion für Paragraph-Erstellung"""
    return Paragraph(text, style)

def create_professional_pdf(customer_data, offer_scenario, detected_season, cart_items, cart_quantities, cart_services, selected_filial_info, selected_mitarbeiter_info):
    """Erstellt professionelle PDF mit neuen Service-Paketen"""
    if not cart_items:
        return None

    total, breakdown = get_cart_total(cart_items, cart_quantities, cart_services)
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
    dynamic_title = get_dynamic_title(cart_items, cart_services)
    story.append(_p(dynamic_title, h1))

    # Datum rechts oben positionieren
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
        "vergleich": f"Ihr individuelles {dynamic_title.split(' ', 1)[1]}",
        "separate": f"Angebot für Ihre Fahrzeuge",
        "einzelangebot": f"Ihr individuelles {dynamic_title.split(' ', 1)[1]}"
    }.get(offer_scenario, f"Ihr {dynamic_title.split(' ', 1)[1]}")
    story.append(_p(section_title, h2))
    story.append(Spacer(1, 4))

    for i, item in enumerate(cart_items, 1):
        quantity = cart_quantities.get(item['id'], 4)
        selected_packages = cart_services.get(item['id'], [])
        
        reifen_kosten, service_kosten, position_total = calculate_position_total(item, quantity, selected_packages)

        # EU-Label kompakt (falls vorhanden) + Saison
        eu_parts = []
        if item.get('Kraftstoffeffizienz'): 
            eu_parts.append(f"Kraftstoff: {str(item['Kraftstoffeffizienz']).strip()}")
        if item.get('Nasshaftung'): 
            eu_parts.append(f"Nass: {str(item['Nasshaftung']).strip()}")
        if item.get('Geräuschemissionen'): 
            eu_parts.append(f"Geräusch: {str(item['Geräuschemissionen']).strip()}")
        # Saison hinzufügen
        if item.get('Saison'): 
            eu_parts.append(f"Saison: {item.get('Saison')}")
        eu_label = " | ".join(eu_parts) if eu_parts else "EU-Label: –"

        # Service-Aufschlüsselung für linke Spalte - NEUE LOGIK
        service_lines = []
        for package in selected_packages:
            pkg_price = float(package['preis'])
            
            # Service-Kosten berechnen (je nach Paket-Typ)
            if 'REIFENSERVICE' in package['bezeichnung'].upper():
                total_pkg_cost = pkg_price * quantity
                service_lines.append(f"{package['bezeichnung']}: {format_eur(total_pkg_cost)}")
            else:
                service_lines.append(f"{package['bezeichnung']}: {format_eur(pkg_price)}")

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
        if i < len(cart_items):
            story.append(Table([[""]], colWidths=[17.6*cm], rowHeights=[0.2]))
            story[-1].setStyle(TableStyle([
                ('LINEABOVE',(0,0),(-1,-1),0.3,colors.black),
                ('LEFTPADDING',(0,0),(-1,-1),0),
                ('RIGHTPADDING',(0,0),(-1,-1),0),
                ('TOPPADDING',(0,0),(-1,-1),0),
                ('BOTTOMPADDING',(0,0),(-1,-1),0),
            ]))
        story.append(Spacer(1, 3))

    # Kostenaufstellung nur für andere Szenarien (nicht bei Vergleichsangeboten)
    if offer_scenario != "vergleich":
        story.append(_p("Kostenaufstellung", h2))
        cost_rows = [['Reifen-Kosten', format_eur(breakdown['reifen'])]]
        if breakdown['services'] > 0:
            cost_rows.append(['Service-Kosten', format_eur(breakdown['services'])])

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
    if selected_mitarbeiter_info:
        mitarbeiter_name = selected_mitarbeiter_info.get('name', '')
        mitarbeiter_position = selected_mitarbeiter_info.get('position', '')
        mitarbeiter_email = selected_mitarbeiter_info.get('email', '')
        
        # Telefonnummer aufbauen
        zentrale = selected_filial_info.get('zentrale', '') if selected_filial_info else ''
        durchwahl = selected_mitarbeiter_info.get('durchwahl', '')
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

    # PDF bauen mit Header/Footer
    def header_footer_wrapper(canvas, doc):
        _header_footer(canvas, doc, selected_filial_info)
    
    doc.build(story, onFirstPage=header_footer_wrapper, onLaterPages=header_footer_wrapper)
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