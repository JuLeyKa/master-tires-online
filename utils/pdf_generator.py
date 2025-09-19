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
# WARENKORB-BERECHNUNGEN - ANGEPASST FÜR NEUE SERVICE-PAKETE - UNVERÄNDERT
# ================================================================================================
def calculate_position_total(item, quantity, selected_packages):
    """Berechnet Gesamtkosten für eine Position mit neuen Service-Paketen"""
    reifen_kosten = item['Preis_EUR'] * quantity
    service_kosten = 0.0
    
    # Service-Pakete durchgehen - alle sind Pauschalpreise
    for package in selected_packages:
        pkg_price = float(package['preis'])
        # Alle Service-Pakete sind Pauschalpreise
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
# NEUE PDF GENERATION - KOMPLETT NEUES LAYOUT NACH VORLAGE
# ================================================================================================
def format_eur(value: float) -> str:
    """Formatiert Euro-Beträge"""
    s = f"{value:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €"

def format_date_german(date_obj):
    """Formatiert Datum als deutschen String (DD.MM.YYYY)"""
    if not date_obj:
        return ""
    if hasattr(date_obj, 'strftime'):
        return date_obj.strftime('%d.%m.%Y')
    return str(date_obj)

def _new_header_footer(canvas, doc):
    """NEUER Header nach Vorlage: RAMSPERGER AUTOMOBILE links, ANGEBOT zentral, feste Firmenadresse"""
    canvas.saveState()
    width, height = A4
    margin = 20 * mm

    # === NEUER HEADER NACH VORLAGE ===
    # Logo/Firmenname links
    try:
        logo_path = Path("data/Logo.png")
        if logo_path.exists():
            logo = ImageReader(str(logo_path))
            # Logo links positionieren - größer
            logo_width = 70 * mm
            logo_height = 21 * mm
            canvas.drawImage(logo, margin, height - margin - 5, 
                           width=logo_width, height=logo_height, 
                           mask='auto', preserveAspectRatio=True)
        else:
            # Fallback Text falls Logo nicht gefunden - SCHWARZ, GROSS
            canvas.setFont("Helvetica-Bold", 14)
            canvas.setFillColor(colors.black)
            canvas.drawString(margin, height - margin + 2, "RAMSPERGER")
            canvas.drawString(margin, height - margin - 12, "AUTOMOBILE")
    except Exception:
        # Fallback bei Fehlern - SCHWARZ, GROSS
        canvas.setFont("Helvetica-Bold", 14)
        canvas.setFillColor(colors.black)
        canvas.drawString(margin, height - margin + 2, "RAMSPERGER")
        canvas.drawString(margin, height - margin - 12, "AUTOMOBILE")

    # ANGEBOT zentriert (größer, fett)
    canvas.setFont("Helvetica-Bold", 18)
    canvas.setFillColor(colors.black)
    text_width = canvas.stringWidth("ANGEBOT", "Helvetica-Bold", 18)
    canvas.drawString((width - text_width) / 2, height - margin - 5, "ANGEBOT")
    
    # "unverbindlich" zentriert darunter (kleiner)
    canvas.setFont("Helvetica", 10)
    text_width_unverb = canvas.stringWidth("unverbindlich", "Helvetica", 10)
    canvas.drawString((width - text_width_unverb) / 2, height - margin - 20, "unverbindlich")

    # === FESTE FIRMENADRESSE unter Header ===
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.black)
    company_address = "Ramsperger Automobile . Postfach 1516 . 73223 Kirchheim u.T."
    canvas.drawString(margin, height - margin - 45, company_address)

    # Dünne Linie unter gesamtem Header
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(0.5)
    canvas.line(margin, height - margin - 50, width - margin, height - margin - 50)

    # === FOOTER LEER (Informationen kommen in den Haupttext) ===
    canvas.restoreState()

def _p(text, style):
    """Hilfsfunktion für Paragraph-Erstellung"""
    return Paragraph(text, style)

def create_professional_pdf(customer_data, offer_scenario, detected_season, cart_items, cart_quantities, cart_services, selected_filial_info, selected_mitarbeiter_info):
    """Erstellt professionelle PDF mit NEUEM LAYOUT NACH VORLAGE"""
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
        topMargin=40*mm,  # Mehr Platz für neuen Header
        bottomMargin=25*mm
    )

    # Styles
    styles = getSampleStyleSheet()
    normal = ParagraphStyle('NormalPlus', parent=styles['Normal'], fontName="Helvetica",
                            fontSize=9, leading=11, textColor=colors.black)
    small = ParagraphStyle('Small', parent=styles['Normal'], fontName="Helvetica",
                           fontSize=8, leading=10, textColor=colors.black)

    story = []

    # === NACH HEADER: Platz für Kundendaten-Layout wie auf Vorlage ===
    story.append(Spacer(1, 15))  # Abstand nach Header

    # === KUNDENDATEN LINKS + GESCHÄFTSDATEN RECHTS (wie auf Vorlage) ===
    date_str = datetime.now().strftime('%d.%m.%Y')
    
    # LINKS: Kundenadresse (wie auf Vorlage)
    left_address = []
    if customer_data and customer_data.get('name'):
        # Namen mit Anrede zusammenfassen
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

    # RECHTS: Geschäftsdaten (wie auf Vorlage)
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

    # Zwei-Spalten-Layout für Adresse + Geschäftsdaten
    if left_address or right_data:
        # Left column content
        left_content = []
        for addr_line in left_address:
            left_content.append([_p(addr_line, normal)])
        # Auffüllen falls rechte Spalte länger
        while len(left_content) < len(right_data):
            left_content.append([_p("", normal)])

        # Right column content  
        right_content = []
        for data_line in right_data:
            right_content.append([_p(data_line, normal)])
        # Auffüllen falls linke Spalte länger
        while len(right_content) < len(left_address):
            right_content.append([_p("", normal)])

        # Tabelle für Links/Rechts Layout
        if left_content or right_content:
            max_rows = max(len(left_content), len(right_content))
            combined_data = []
            for i in range(max_rows):
                left_cell = left_content[i][0] if i < len(left_content) else _p("", normal)
                right_cell = right_content[i][0] if i < len(right_content) else _p("", normal)
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
    # Sammlung aller Fahrzeuge basierend auf Szenario
    vehicles = []
    
    if offer_scenario == "separate" and len(cart_items) >= 2:
        # Separate Fahrzeuge: Jedem Reifen ein Fahrzeug zuordnen
        for i, item in enumerate(cart_items):
            if i == 0:
                # Erstes Fahrzeug
                vehicle = {
                    'kennzeichen': customer_data.get('kennzeichen', ''),
                    'typ': customer_data.get('typ_modellschluessel', ''),
                    'erstzulassung': customer_data.get('erstzulassung'),
                    'fahrzeug_ident': customer_data.get('fahrgestellnummer', ''),
                    'fahrzeugannahme': customer_data.get('fahrzeugannahme'),
                    'km_stand': customer_data.get('km_stand', ''),
                    'serviceberater': selected_mitarbeiter_info.get('name', '') if selected_mitarbeiter_info else ''
                }
            elif i == 1 and customer_data.get('kennzeichen_2'):
                # Zweites Fahrzeug
                vehicle = {
                    'kennzeichen': customer_data.get('kennzeichen_2', ''),
                    'typ': customer_data.get('typ_modellschluessel_2', ''),
                    'erstzulassung': customer_data.get('erstzulassung_2'),
                    'fahrzeug_ident': customer_data.get('fahrgestellnummer_2', ''),
                    'fahrzeugannahme': customer_data.get('fahrzeugannahme_2'),
                    'km_stand': customer_data.get('km_stand_2', ''),
                    'serviceberater': selected_mitarbeiter_info.get('name', '') if selected_mitarbeiter_info else ''
                }
            else:
                # Weitere Fahrzeuge - leer oder aus erstem ableiten
                vehicle = {
                    'kennzeichen': '',
                    'typ': '',
                    'erstzulassung': None,
                    'fahrzeug_ident': '',
                    'fahrzeugannahme': None,
                    'km_stand': '',
                    'serviceberater': selected_mitarbeiter_info.get('name', '') if selected_mitarbeiter_info else ''
                }
            vehicles.append(vehicle)
    else:
        # Alle anderen Szenarien: Ein Fahrzeug für alle Reifen
        if customer_data:
            vehicle = {
                'kennzeichen': customer_data.get('kennzeichen', ''),
                'typ': customer_data.get('typ_modellschluessel', ''),
                'erstzulassung': customer_data.get('erstzulassung'),
                'fahrzeug_ident': customer_data.get('fahrgestellnummer', ''),
                'fahrzeugannahme': customer_data.get('fahrzeugannahme'),
                'km_stand': customer_data.get('km_stand', ''),
                'serviceberater': selected_mitarbeiter_info.get('name', '') if selected_mitarbeiter_info else ''
            }
            vehicles.append(vehicle)

    # Fahrzeugdaten-Tabelle erstellen (wenn Fahrzeugdaten vorhanden)
    if vehicles and any(v.get('kennzeichen') or v.get('typ') or v.get('fahrzeug_ident') for v in vehicles):
        story.append(_p("Seite 1 von 2", ParagraphStyle('PageInfo', parent=normal, alignment=TA_RIGHT)))
        story.append(Spacer(1, 10))

        # Tabellen-Header (wie auf Vorlage)
        vehicle_headers = [
            "Amtl. Kennzeichen",
            "Typ/\nModellschlüssel", 
            "Datum\nErstzulassung",
            "Fahrzeug-Ident.-Nr.",
            "Fzg.-\nAnnahmedatum",
            "km-Stand\nFahrzeugannahme",
            "Serviceberater"
        ]
        
        # Datenzeilen
        vehicle_data = [vehicle_headers]
        for vehicle in vehicles:
            row = [
                vehicle.get('kennzeichen', ''),
                vehicle.get('typ', ''),
                format_date_german(vehicle.get('erstzulassung')),
                vehicle.get('fahrzeug_ident', ''),
                format_date_german(vehicle.get('fahrzeugannahme')),
                vehicle.get('km_stand', ''),
                vehicle.get('serviceberater', '')
            ]
            vehicle_data.append(row)

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

        # Zusatzinformationen (wie auf Vorlage)
        if customer_data and customer_data.get('hu_au_datum'):
            story.append(_p(f"Ihre nächste HU/AU ist: {customer_data['hu_au_datum']}", normal))
        # Zusatztext wie auf Vorlage (aber ohne den letzten Satz)
        story.append(_p("Kostenvoranschläge werden im unzerlegten Zustand erstellt. Schäden die erst nach der Demontage sichtbar werden, sind hierbei nicht berücksichtigt!", normal))
        story.append(Spacer(1, 20))

    # === REIFEN-ANGEBOT BEREICH (bestehende Logik beibehalten) ===
    # Dynamische Überschrift basierend auf Warenkorb-Inhalt
    dynamic_title = get_dynamic_title(cart_items, cart_services)
    story.append(_p(dynamic_title, ParagraphStyle('H2', parent=styles['Heading2'], 
                                                  fontName="Helvetica-Bold", fontSize=12, 
                                                  leading=14, spaceAfter=8, textColor=colors.black)))

    # Positionsdarstellung (bestehende Logik)
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

        # Service-Aufschlüsselung für linke Spalte
        service_lines = []
        for package in selected_packages:
            pkg_price = float(package['preis'])
            service_lines.append(f"{package['bezeichnung']}: {format_eur(pkg_price)}")

        # Linke Spalte (Info + Services)
        cell_style = ParagraphStyle('cell', parent=normal, fontSize=9, leading=11)
        left_rows = [
            [_p(f"<b>{item['Reifengröße']}</b> – <b>{item['Fabrikat']} {item['Profil']}</b>", cell_style)],
            [_p(f"Teilenummer: {item['Teilenummer']} · Einzelpreis: <b>{format_eur(item['Preis_EUR'])}</b>", cell_style)],
            [_p(f"{eu_label}", cell_style)]
        ]
        
        # Service-Zeilen hinzufügen
        for service_line in service_lines:
            left_rows.append([_p(service_line, cell_style)])

        left_tbl = Table(left_rows, colWidths=[12*cm])
        left_tbl.setStyle(TableStyle([
            ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
            ('FONTSIZE',(0,0),(-1,-1),9),
            ('TEXTCOLOR',(0,0),(-1,-1),colors.black),
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('BOTTOMPADDING',(0,0),(-1,-1),2),
            ('TOPPADDING',(0,0),(-1,-1),1),
        ]))

        # Rechte Spalte
        cell_c_style = ParagraphStyle('cellc', parent=cell_style, alignment=TA_CENTER)
        cell_r_style = ParagraphStyle('cellr', parent=cell_style, alignment=TA_RIGHT)
        
        if offer_scenario == "vergleich":
            # Grüne Box für Vergleichsangebote
            right_rows = [
                [_p(f"<b>{quantity}×</b>", cell_c_style)],  # Stückzahl
                [_p(" ", cell_c_style)],  # Spacer
                [_p(f"Reifen: {format_eur(reifen_kosten)}", cell_r_style)],
                [_p(f"Services: {format_eur(service_kosten)}", cell_r_style)],
                [_p(f"<b>GESAMT</b><br/><b>{format_eur(position_total)}</b>", cell_c_style)],
            ]

            right_tbl = Table(right_rows, colWidths=[5.6*cm])
            right_tbl.setStyle(TableStyle([
                ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
                ('FONTSIZE',(0,0),(-1,-1),9),
                ('TEXTCOLOR',(0,0),(-1,-1),colors.black),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('BOTTOMPADDING',(0,0),(-1,-1),2),
                ('TOPPADDING',(0,0),(-1,-1),1),
                
                # Grüne Box für Gesamtpreis
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
                [_p(f"<b>{quantity}×</b>", cell_c_style)],
                [_p(" ", cell_c_style)],
                [_p(f"Reifen: {format_eur(reifen_kosten)}", cell_r_style)],
                [_p(f"Services: {format_eur(service_kosten)}", cell_r_style)],
                [_p(f"<b>Gesamt: {format_eur(position_total)}</b>", cell_r_style)],
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

        story.append(KeepTogether(card))

        # Trennlinie zwischen Positionen
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

    # Kostenaufstellung (für nicht-Vergleichsangebote)
    if offer_scenario != "vergleich":
        h2_style = ParagraphStyle('H2', parent=styles['Heading2'], 
                                 fontName="Helvetica-Bold", fontSize=12, 
                                 leading=14, spaceAfter=6, textColor=colors.black)
        story.append(_p("Kostenaufstellung", h2_style))
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

            # Gesamtsumme
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
        story.append(Spacer(1, 10))

    # Abschließende Informationen (bestehende Logik)
    story.append(Spacer(1, 10))
    bullets = [
        "Angebot gültig 14 Tage",
        "Inklusive Reifengarantie 36 Monate", 
        "Inklusive Entsorgung Altreifen"
    ]
    
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
    story.append(Spacer(1, 8))

    # Schluss und Kontaktdaten
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], 
                             fontName="Helvetica-Bold", fontSize=12, 
                             leading=14, spaceAfter=6, textColor=colors.black)
    story.append(_p("Vielen Dank für Ihr Vertrauen!", h2_style))
    story.append(_p("Ihr Team von Ramsperger Automobile", normal))
    story.append(Spacer(1, 8))
    
    story.append(_p("Für Rückfragen stehen wir Ihnen gerne zur Verfügung.", small))
    story.append(Spacer(1, 8))

    # Mitarbeiterinformationen
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

    # Filialadresse als Footer-Alternative
    if selected_filial_info:
        story.append(Spacer(1, 10))
        filial_text = f"{selected_filial_info.get('bereich', '')} {selected_filial_info.get('adresse', '')} Telefon: {selected_filial_info.get('zentrale', '')}"
        story.append(_p(filial_text, small))

    # PDF bauen
    doc.build(story, onFirstPage=_new_header_footer, onLaterPages=_new_header_footer)
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