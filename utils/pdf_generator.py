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
# NEUE MWST-KORREKTE BERECHNUNGEN - WICHTIGSTE ÄNDERUNG!
# ================================================================================================
def calculate_netto_from_brutto(brutto_price):
    """Rechnet Brutto-Preis (inkl. 19% MwSt) zu Netto-Preis um"""
    return brutto_price / 1.19

def calculate_mwst_from_netto(netto_price):
    """Berechnet 19% MwSt von Netto-Preis"""
    return netto_price * 0.19

def calculate_position_total(item, quantity, selected_packages):
    """Berechnet Gesamtkosten für eine Position mit KORREKTER MwSt-Berechnung"""
    # Reifen: CSV-Preis ist BRUTTO → zu NETTO umrechnen
    reifen_preis_brutto = item['Preis_EUR']
    reifen_preis_netto = calculate_netto_from_brutto(reifen_preis_brutto)
    reifen_kosten_netto = reifen_preis_netto * quantity
    
    # Service-Pakete: CSV-Preis ist auch BRUTTO → zu NETTO umrechnen
    service_kosten_netto = 0.0
    for package in selected_packages:
        pkg_price_brutto = float(package['preis'])
        pkg_price_netto = calculate_netto_from_brutto(pkg_price_brutto)
        service_kosten_netto += pkg_price_netto
    
    # Gesamt NETTO
    position_netto = reifen_kosten_netto + service_kosten_netto
    
    # MwSt berechnen (19%)
    position_mwst = calculate_mwst_from_netto(position_netto)
    
    # Gesamt BRUTTO
    position_brutto = position_netto + position_mwst
    
    return {
        'reifen_netto': reifen_kosten_netto,
        'service_netto': service_kosten_netto,
        'gesamt_netto': position_netto,
        'mwst': position_mwst,
        'gesamt_brutto': position_brutto,
        'reifen_einzelpreis_netto': reifen_preis_netto
    }

def get_cart_total(cart_items, cart_quantities, cart_services):
    """Berechnet Gesamtsumme des Warenkorbs mit KORREKTER MwSt"""
    totals = {
        'reifen_netto': 0.0,
        'service_netto': 0.0,
        'gesamt_netto': 0.0,
        'mwst': 0.0,
        'gesamt_brutto': 0.0
    }
    
    for item in cart_items:
        quantity = cart_quantities.get(item['id'], 4)
        selected_packages = cart_services.get(item['id'], [])
        
        position_calc = calculate_position_total(item, quantity, selected_packages)
        
        totals['reifen_netto'] += position_calc['reifen_netto']
        totals['service_netto'] += position_calc['service_netto']
        totals['gesamt_netto'] += position_calc['gesamt_netto']
        totals['mwst'] += position_calc['mwst']
        totals['gesamt_brutto'] += position_calc['gesamt_brutto']
    
    return totals['gesamt_brutto'], {
        'reifen': totals['reifen_netto'],
        'services': totals['service_netto'],
        'netto': totals['gesamt_netto'],
        'mwst': totals['mwst'],
        'brutto': totals['gesamt_brutto']
    }

# ================================================================================================
# HILFSFUNKTIONEN FÜR PDF
# ================================================================================================
def format_eur(value: float) -> str:
    """Formatiert Euro-Beträge"""
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

def _p(text, style):
    """Hilfsfunktion für Paragraph-Erstellung"""
    return Paragraph(text, style)

# ================================================================================================
# NEUER HEADER/FOOTER NACH VORLAGE
# ================================================================================================
def _new_header_footer(canvas, doc, selected_filial_info):
    """NEUER Header nach Vorlage + Footer mit Betriebsdaten"""
    canvas.saveState()
    width, height = A4
    margin = 20 * mm

    # === HEADER ===
    # Logo/Firmenname links
    try:
        logo_path = Path("data/Logo.png")
        if logo_path.exists():
            logo = ImageReader(str(logo_path))
            logo_width = 70 * mm
            logo_height = 21 * mm
            canvas.drawImage(logo, margin, height - margin - 5, 
                           width=logo_width, height=logo_height, 
                           mask='auto', preserveAspectRatio=True)
        else:
            # Fallback Text
            canvas.setFont("Helvetica-Bold", 14)
            canvas.setFillColor(colors.black)
            canvas.drawString(margin, height - margin + 2, "RAMSPERGER")
            canvas.drawString(margin, height - margin - 12, "AUTOMOBILE")
    except Exception:
        # Fallback bei Fehlern
        canvas.setFont("Helvetica-Bold", 14)
        canvas.setFillColor(colors.black)
        canvas.drawString(margin, height - margin + 2, "RAMSPERGER")
        canvas.drawString(margin, height - margin - 12, "AUTOMOBILE")

    # ANGEBOT zentriert
    canvas.setFont("Helvetica-Bold", 18)
    canvas.setFillColor(colors.black)
    text_width = canvas.stringWidth("ANGEBOT", "Helvetica-Bold", 18)
    canvas.drawString((width - text_width) / 2, height - margin - 5, "ANGEBOT")
    
    # "unverbindlich" zentriert darunter
    canvas.setFont("Helvetica", 10)
    text_width_unverb = canvas.stringWidth("unverbindlich", "Helvetica", 10)
    canvas.drawString((width - text_width_unverb) / 2, height - margin - 20, "unverbindlich")

    # Feste Firmenadresse unter Header
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.black)
    company_address = "Ramsperger Automobile . Postfach 1516 . 73223 Kirchheim u.T."
    canvas.drawString(margin, height - margin - 45, company_address)

    # Linie unter Header
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(0.5)
    canvas.line(margin, height - margin - 50, width - margin, height - margin - 50)

    # === FOOTER MIT BETRIEBSDATEN ===
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.black)
    
    # Footer-Informationen basierend auf gewählter Filiale
    if selected_filial_info:
        # Zeile 1: Firmenname und Adresse
        footer_line1 = f"Ramsperger Automobile GmbH & Co.KG {selected_filial_info.get('adresse', '')}"
        
        # Zeile 2: Telefon/Fax
        zentrale = selected_filial_info.get('zentrale', '')
        footer_line2 = f"Telefon {zentrale}"
        
        # Zeile 3: Standard-Firmendaten
        footer_line3 = "Rechtsform: KG Sitz: Kirchheim u. T. Amtsgericht Stuttgart Handelsregister: HRA 231034 USt-Id.Nr. DE 199 195 203"
        
        canvas.drawString(margin, margin - 15, footer_line1)
        canvas.drawString(margin, margin - 25, footer_line2)
        canvas.drawString(margin, margin - 35, footer_line3)
    
    canvas.restoreState()

# ================================================================================================
# NEUE PDF GENERATION - VOLLSTÄNDIG NACH VORLAGE
# ================================================================================================
def create_professional_pdf(customer_data, offer_scenario, detected_season, cart_items, cart_quantities, cart_services, selected_filial_info, selected_mitarbeiter_info):
    """Erstellt professionelle PDF mit NEUER STRUKTUR NACH VORLAGE"""
    if not cart_items:
        return None

    # Nur eine Position erwarten (da jetzt ein PDF pro Position)
    if len(cart_items) != 1:
        return None
    
    item = cart_items[0]
    quantity = cart_quantities.get(item['id'], 4)
    selected_packages = cart_services.get(item['id'], [])
    
    # Berechnungen mit korrekter MwSt
    position_calc = calculate_position_total(item, quantity, selected_packages)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=40*mm,
        bottomMargin=40*mm  # Mehr Platz für Footer
    )

    # Styles
    styles = getSampleStyleSheet()
    normal = ParagraphStyle('NormalPlus', parent=styles['Normal'], fontName="Helvetica",
                            fontSize=9, leading=11, textColor=colors.black)
    small = ParagraphStyle('Small', parent=styles['Normal'], fontName="Helvetica",
                           fontSize=8, leading=10, textColor=colors.black)

    story = []

    # === KUNDENDATEN UND GESCHÄFTSDATEN (wie auf Vorlage) ===
    story.append(Spacer(1, 15))
    
    date_str = datetime.now().strftime('%d.%m.%Y')
    
    # LINKS: Kundenadresse
    left_address = []
    if customer_data and customer_data.get('name'):
        if customer_data.get('anrede') and customer_data.get('name'):
            left_address.append(f"{customer_data['anrede']} {customer_data['name']}")
        else:
            left_address.append(customer_data.get('name', ''))
        
        # Straße + Hausnummer
        strasse_haus = ""
        if customer_data.get('strasse'):
            strasse_haus = customer_data['strasse']
            if customer_data.get('hausnummer'):
                strasse_haus += f" {customer_data['hausnummer']}"
        if strasse_haus:
            left_address.append(strasse_haus)
        
        # PLZ + Ort
        plz_ort = ""
        if customer_data.get('plz') and customer_data.get('ort'):
            plz_ort = f"{customer_data['plz']} {customer_data['ort']}"
        elif customer_data.get('plz'):
            plz_ort = customer_data['plz']
        elif customer_data.get('ort'):
            plz_ort = customer_data['ort']
        if plz_ort:
            left_address.append(plz_ort)

    # RECHTS: Geschäftsdaten
    right_data = []
    right_data.append(f"Datum (= Tag der Lieferung): {date_str}")
    if customer_data and customer_data.get('kunden_nr'):
        right_data.append(f"Kunden-Nr.: {customer_data['kunden_nr']}")
    if customer_data and customer_data.get('abnehmer_gruppe'):
        right_data.append(f"Abnehmer-Gruppe: {customer_data['abnehmer_gruppe']}")
    if customer_data and customer_data.get('auftrags_nr'):
        right_data.append(f"Auftrags-Nr.: {customer_data['auftrags_nr']}")
    if customer_data and customer_data.get('betriebs_nr'):
        right_data.append(f"Betriebs-Nr.: {customer_data['betriebs_nr']}")
    if customer_data and customer_data.get('leistungsdatum'):
        leistung_str = format_date_german(customer_data['leistungsdatum'])
        if leistung_str:
            right_data.append(f"Leistungsdatum: {leistung_str}")

    # Zwei-Spalten-Layout
    if left_address or right_data:
        max_rows = max(len(left_address), len(right_data))
        combined_data = []
        for i in range(max_rows):
            left_cell = _p(left_address[i] if i < len(left_address) else "", normal)
            right_cell = _p(right_data[i] if i < len(right_data) else "", normal)
            combined_data.append([left_cell, right_cell])

        addr_table = Table(combined_data, colWidths=[9*cm, 8*cm])
        addr_table.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('LEFTPADDING',(0,0),(-1,-1),0),
            ('RIGHTPADDING',(0,0),(-1,-1),0),
            ('TOPPADDING',(0,0),(-1,-1),2),
            ('BOTTOMPADDING',(0,0),(-1,-1),2),
        ]))
        story.append(addr_table)

    story.append(Spacer(1, 15))

    # === FAHRZEUGDATEN TABELLE (wie auf Vorlage) ===
    if customer_data:
        story.append(_p("Seite 1 von 2", ParagraphStyle('PageInfo', parent=normal, alignment=TA_RIGHT)))
        story.append(Spacer(1, 10))

        # Fahrzeugdaten-Tabelle
        vehicle_headers = [
            "Amtl. Kennzeichen",
            "Typ/\nModellschlüssel", 
            "Datum\nErstzulassung",
            "Fahrzeug-Ident.-Nr.",
            "Fzg.-\nAnnahmedatum",
            "km-Stand\nFahrzeugannahme",
            "Serviceberater"
        ]
        
        vehicle_row = [
            customer_data.get('kennzeichen', ''),
            customer_data.get('typ_modellschluessel', ''),
            format_date_german(customer_data.get('erstzulassung')),
            customer_data.get('fahrgestellnummer', ''),
            format_date_german(customer_data.get('fahrzeugannahme')),
            customer_data.get('km_stand', ''),
            selected_mitarbeiter_info.get('name', '') if selected_mitarbeiter_info else ''
        ]
        
        vehicle_data = [vehicle_headers, vehicle_row]

        vehicle_table = Table(vehicle_data, colWidths=[2.5*cm, 2*cm, 2*cm, 3.5*cm, 2.2*cm, 2.3*cm, 3*cm])
        vehicle_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND',(0,0),(-1,0), colors.grey),
            ('TEXTCOLOR',(0,0),(-1,0), colors.whitesmoke),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('FONTSIZE',(0,0),(-1,-1),8),
            ('BOTTOMPADDING',(0,0),(-1,-1),6),
            ('TOPPADDING',(0,0),(-1,-1),6),
            ('GRID',(0,0),(-1,-1),0.5,colors.black),
            # Datenzeilen
            ('FONTNAME',(0,1),(-1,-1),'Helvetica'),
            ('TEXTCOLOR',(0,1),(-1,-1), colors.black),
        ]))
        story.append(vehicle_table)
        story.append(Spacer(1, 15))

        # HU/AU Info
        if customer_data and customer_data.get('hu_au_datum'):
            story.append(_p(f"Ihre nächste HU/AU ist: {customer_data['hu_au_datum']}", normal))
        
        story.append(_p("Kostenvoranschläge werden im unzerlegten Zustand erstellt. Schäden die erst nach der Demontage sichtbar werden, sind hierbei nicht berücksichtigt!", normal))
        story.append(Spacer(1, 20))

    # === HAUPT-ARBEITSTABELLE (wie auf Vorlage) ===
    # Header der Haupttabelle
    table_headers = [
        "Nr.",
        "Arbeitsposition/\nTeilenummer", 
        "Bezeichnung",
        "Mit-\narbeiter",
        "Einzel-\npreis",
        "Menge/\nZeit",
        "Rabatt",
        "Steuer-\nCode",
        "Betrag\nEUR"
    ]
    
    table_data = [table_headers]
    
    # Positions-Nummer
    pos_nr = 1
    
    # REIFEN-ZEILE
    reifen_bezeichnung = f"{item['Reifengröße']} {item['Fabrikat']} {item['Profil']}"
    reifen_einzelpreis_netto = position_calc['reifen_einzelpreis_netto']
    reifen_betrag_netto = position_calc['reifen_netto']
    
    reifen_row = [
        str(pos_nr),
        item['Teilenummer'],
        reifen_bezeichnung,
        "",  # Mitarbeiter
        format_eur(reifen_einzelpreis_netto),
        f"{quantity},00 Stück",
        "",  # Rabatt
        "#3",  # Steuer-Code
        format_eur(reifen_betrag_netto)
    ]
    table_data.append(reifen_row)
    
    # SERVICE-ZEILEN
    for package in selected_packages:
        pos_nr += 1
        pkg_price_brutto = float(package['preis'])
        pkg_price_netto = calculate_netto_from_brutto(pkg_price_brutto)
        
        service_row = [
            str(pos_nr),
            package.get('positionsnummer', ''),
            package['bezeichnung'],
            "",  # Mitarbeiter
            format_eur(pkg_price_netto),
            "1,00 Stück",
            "",  # Rabatt
            "#3",  # Steuer-Code
            format_eur(pkg_price_netto)
        ]
        table_data.append(service_row)
    
    # Haupttabelle erstellen
    main_table = Table(table_data, colWidths=[1*cm, 2.5*cm, 4*cm, 1.5*cm, 1.8*cm, 1.5*cm, 1.2*cm, 1.2*cm, 2.3*cm])
    main_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND',(0,0),(-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0), colors.whitesmoke),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,0),8),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        
        # Datenzeilen
        ('FONTNAME',(0,1),(-1,-1),'Helvetica'),
        ('FONTSIZE',(0,1),(-1,-1),8),
        ('TEXTCOLOR',(0,1),(-1,-1), colors.black),
        ('ALIGN',(0,1),(0,-1),'CENTER'),  # Nr.
        ('ALIGN',(4,1),(4,-1),'RIGHT'),   # Einzelpreis
        ('ALIGN',(5,1),(5,-1),'CENTER'),  # Menge
        ('ALIGN',(7,1),(7,-1),'CENTER'),  # Steuer-Code
        ('ALIGN',(8,1),(8,-1),'RIGHT'),   # Betrag
        
        # Grid
        ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('TOPPADDING',(0,0),(-1,-1),4),
    ]))
    
    story.append(main_table)
    story.append(Spacer(1, 15))

    # === STANDARD-TEXTE (wie auf Vorlage) ===
    standard_text = (
        "Reifen/Kompletträder in dieser Rechnung sind inklusive kostenloser 36 Monate Reifen "
        "Garantie gemäß den Bedingungen im Reifen Garantie Pass (Original Rechnung "
        "oder Rechnungskopie bitte als Garantienachweis im Fahrzeug mitführen)"
    )
    story.append(_p(standard_text, small))
    story.append(Spacer(1, 10))

    # NETTO-Summe
    story.append(_p(f"Gesamtbetrag (netto): {format_eur(position_calc['gesamt_netto'])}", normal))
    story.append(Spacer(1, 25))

    # Zwischensumme
    story.append(_p(f"Zwischensumme {format_eur(position_calc['gesamt_netto'])}", normal))
    story.append(Spacer(1, 15))

    # === MWST-AUFSCHLÜSSELUNG (wie auf Vorlage) ===
    mwst_headers = [
        "Steuer-\nCode",
        "Arbeit",
        "Material", 
        "Steuerbasis",
        "%-Mwst",
        "Mwst",
        "Steuerbasis\nAltwert",
        "Mwst auf\nAltwert",
        "Gesamtbetrag"
    ]
    
    mwst_row = [
        "#3",
        format_eur(position_calc['gesamt_netto']),
        "0,00",
        format_eur(position_calc['gesamt_netto']),
        "19%",
        format_eur(position_calc['mwst']),
        "0,00",
        "0,00",
        ""
    ]
    
    mwst_summe_row = [
        "Summe",
        format_eur(position_calc['gesamt_netto']),
        "0,00",
        format_eur(position_calc['gesamt_netto']),
        "",
        format_eur(position_calc['mwst']),
        "0,00",
        "0,00",
        format_eur(position_calc['gesamt_brutto'])
    ]
    
    mwst_data = [mwst_headers, mwst_row, mwst_summe_row]
    
    mwst_table = Table(mwst_data, colWidths=[1.2*cm, 1.8*cm, 1.5*cm, 1.8*cm, 1.2*cm, 1.8*cm, 1.5*cm, 1.5*cm, 2*cm])
    mwst_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND',(0,0),(-1,0), colors.lightgrey),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,0),7),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        
        # Datenzeilen
        ('FONTNAME',(0,1),(-1,-1),'Helvetica'),
        ('FONTSIZE',(0,1),(-1,-1),8),
        ('ALIGN',(1,1),(-1,-1),'RIGHT'),
        
        # Summenzeile hervorheben
        ('FONTNAME',(0,2),(-1,2),'Helvetica-Bold'),
        
        # Grid
        ('GRID',(0,0),(-1,-1),0.3,colors.black),
        ('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('TOPPADDING',(0,0),(-1,-1),3),
    ]))
    
    story.append(mwst_table)
    story.append(Spacer(1, 10))

    # Angebot gültig bis
    gueltigkeit = (datetime.now().replace(day=datetime.now().day + 14)).strftime('%d-%m-%Y')
    story.append(_p(f"Angebot gültig bis {gueltigkeit}", normal))
    
    # Serviceberater-Info
    if selected_mitarbeiter_info:
        mitarbeiter_name = selected_mitarbeiter_info.get('name', '')
        mitarbeiter_email = selected_mitarbeiter_info.get('email', '')
        story.append(_p(f"Es bediente Sie Ihr Serviceberater Herr {mitarbeiter_name}. Für Rückfragen stehe ich Ihnen gerne persönlich zur Verfügung. e-Mail: {mitarbeiter_email}", small))

    # PDF bauen
    def header_footer_wrapper(canvas, doc):
        _new_header_footer(canvas, doc, selected_filial_info)
    
    doc.build(story, onFirstPage=header_footer_wrapper, onLaterPages=header_footer_wrapper)
    buffer.seek(0)
    return buffer.getvalue()

# ================================================================================================
# E-MAIL TEXT & MAILTO (direkter Flow, Regex FIX) - UNVERÄNDERT
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