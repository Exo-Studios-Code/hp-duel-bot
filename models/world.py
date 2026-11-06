"""
Open World System - PvP Zaměřený Svět
Hráči proti hráčům, tábory, cestování, ekonomika
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import time
import random
import json
import os

class LocationType(Enum):
    """Typy lokací"""
    SAFE_ZONE = "safe_zone"
    CITY = "city"
    VILLAGE = "village"
    WILDERNESS = "wilderness"
    FOREST = "forest"
    DUNGEON = "dungeon"
    RUINS = "ruins"
    MINISTRY = "ministry"
    SCHOOL = "school"


class PvPZone(Enum):
    """PvP pravidla"""
    SAFE = "safe"              # Žádné PvP
    CONSENSUAL = "consensual"  # Pouze se souhlasem
    OPEN = "open"              # Free for all
    FLAGGED = "flagged"        # Pouze s PvP flagem


class Weather(Enum):
    """Počasí"""
    CLEAR = "clear"
    RAIN = "rain"
    STORM = "storm"
    FOG = "fog"
    SNOW = "snow"
    NIGHT = "night"


@dataclass
class Location:
    """Lokace ve světě"""
    id: str
    name_cs: str
    name_en: str
    type: LocationType
    pvp_zone: PvPZone
    description: str
    
    connections: Dict[str, float] = field(default_factory=dict)
    
    has_shop: bool = False
    has_healer: bool = False
    has_bank: bool = False
    has_trainer: bool = False
    has_quest_board: bool = False
    has_inn: bool = False 
    resources: Dict[str, float] = field(default_factory=dict)
    
    weather: Weather = Weather.CLEAR
    visibility: float = 1.0
    
    players_present: Set[int] = field(default_factory=set)
    camps: Dict[str, 'Camp'] = field(default_factory=dict)
    
    allows_camping: bool = True
    allows_apparition: bool = True
    spawn_point: bool = False


@dataclass
class Camp:
    """Tábor hráče"""
    id: str
    owner_id: int
    location_id: str
    name: str
    
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    
    protections: Dict[str, float] = field(default_factory=dict)
    
    members: Set[int] = field(default_factory=set)
    invited: Set[int] = field(default_factory=set)
    public: bool = False
    
    storage: Dict[str, int] = field(default_factory=dict)
    
    healing_rate: float = 2.0
    resting: Set[int] = field(default_factory=set)
    
    hidden: bool = False


@dataclass
class PlayerWorldState:
    """Stav hráče"""
    player_id: int
    
    current_location: str = "hogsmeade"
    last_location: str = "hogsmeade"
    
    traveling: bool = False
    travel_destination: Optional[str] = None
    travel_eta: float = 0.0
    
    pvp_enabled: bool = False
    pvp_kills: int = 0
    pvp_deaths: int = 0
    bounty: int = 0
    
    current_camp: Optional[str] = None
    owned_camps: List[str] = field(default_factory=list)
    
    inventory: Dict[str, int] = field(default_factory=dict)
    gold: int = 100
    
    hidden: bool = False


# Konkrétní lokace (22 lokací pro volný pohyb)
LOCATIONS = {
    # ================= BRADAVICE A OKOLÍ =================
    
    "hogsmeade": Location(
        id="hogsmeade",
        name_cs="Prasinky",
        name_en="Hogsmeade",
        type=LocationType.VILLAGE,
        pvp_zone=PvPZone.SAFE,
        description="Jediná čistě kouzelnická vesnice v Británii. Skvělé místo pro odpočinek.",
        has_shop=True,
        has_healer=True,
        has_inn=True,
        resources={"mandrake_root": 0.3, "wormwood": 0.4},
        connections={"hogwarts_grounds": 15.0, "hogsmeade_station": 5.0, "shrieking_shack": 10.0, "forbidden_forest": 15.0},
        spawn_point=True
    ),
    
    "hogsmeade_station": Location(
        id="hogsmeade_station",
        name_cs="Nádraží v Prasinkách",
        name_en="Hogsmeade Station",
        type=LocationType.VILLAGE,
        pvp_zone=PvPZone.SAFE,
        description="Stanice Spěšného vlaku do Bradavic. Zajišťuje spojení s Londýnem.",
        connections={"hogsmeade": 5.0, "black_lake": 10.0, "kings_cross": 120.0}, # Vlak trvá dlouho
        allows_camping=False
    ),

    "hogwarts_grounds": Location(
        id="hogwarts_grounds",
        name_cs="Školní pozemky",
        name_en="Hogwarts Grounds",
        type=LocationType.WILDERNESS,
        pvp_zone=PvPZone.CONSENSUAL,
        description="Rozlehlé pozemky obklopující hrad. Hagridova bouda leží nedaleko.",
        resources={"mandrake_root": 0.4, "wormwood": 0.5},
        connections={"hogwarts": 5.0, "hogsmeade": 15.0, "black_lake": 10.0, "quidditch_pitch": 5.0, "forbidden_forest": 10.0},
        allows_apparition=False # Ochrany sahají až sem
    ),

    "hogwarts": Location(
        id="hogwarts",
        name_cs="Bradavice",
        name_en="Hogwarts",
        type=LocationType.SCHOOL,
        pvp_zone=PvPZone.CONSENSUAL,
        description="Škola čar a kouzel. Na chodbách se bojuje jen v rámci tréninku.",
        has_healer=True,
        has_quest_board=True,
        has_trainer=True,
        connections={"hogwarts_grounds": 5.0},
        allows_apparition=False,  # V Bradavicích se nedá přemisťovat!
        allows_camping=False
    ),

    "black_lake": Location(
        id="black_lake",
        name_cs="Černé jezero",
        name_en="Black Lake",
        type=LocationType.WILDERNESS,
        pvp_zone=PvPZone.CONSENSUAL,
        description="Temné, hluboké jezero plné tajemných stvoření.",
        weather=Weather.FOG,
        visibility=0.8,
        connections={"hogwarts_grounds": 10.0, "hogsmeade_station": 10.0}
    ),

    "quidditch_pitch": Location(
        id="quidditch_pitch",
        name_cs="Famfrpálové hřiště",
        name_en="Quidditch Pitch",
        type=LocationType.WILDERNESS,
        pvp_zone=PvPZone.CONSENSUAL,
        description="Tribuny a obruče. Často tu probíhají tréninky.",
        connections={"hogwarts_grounds": 5.0},
        allows_apparition=False,
        allows_camping=False
    ),

    "forbidden_forest": Location(
        id="forbidden_forest",
        name_cs="Zapovězený les",
        name_en="Forbidden Forest",
        type=LocationType.FOREST,
        pvp_zone=PvPZone.OPEN,
        description="⚔️ NEBEZPEČNO! Temný les plný nestvůr. Open PvP zóna!",
        weather=Weather.FOG,
        visibility=0.6,
        resources={"unicorn_hair": 0.1, "moonstone": 0.05, "dittany": 0.15},
        connections={"hogwarts_grounds": 10.0, "hogsmeade": 15.0, "forbidden_forest_deep": 20.0}
    ),

    "forbidden_forest_deep": Location(
        id="forbidden_forest_deep",
        name_cs="Hlubiny Zapovězeného lesa",
        name_en="Deep Forbidden Forest",
        type=LocationType.FOREST,
        pvp_zone=PvPZone.OPEN,
        description="💀 EXTRÉMNÍ NEBEZPEČÍ! Tady slunce nesvítí. Hnízda akromantulí.",
        weather=Weather.NIGHT,
        visibility=0.3,
        resources={"unicorn_hair": 0.3, "moonstone": 0.15, "dittany": 0.3},
        connections={"forbidden_forest": 20.0}
    ),

    "shrieking_shack": Location(
        id="shrieking_shack",
        name_cs="Chroptící chýše",
        name_en="Shrieking Shack",
        type=LocationType.RUINS,
        pvp_zone=PvPZone.OPEN,
        description="⚔️ Opuštěná, polorozpadlá chata. Říká se, že tu straší.",
        connections={"hogsmeade": 10.0}
    ),

    # ================= LONDÝN A OKOLÍ =================

    "kings_cross": Location(
        id="kings_cross",
        name_cs="Nádraží King's Cross",
        name_en="King's Cross Station",
        type=LocationType.CITY,
        pvp_zone=PvPZone.SAFE,
        description="Mudlovské nádraží s tajným Nástupištěm 9 a 3/4.",
        connections={"hogsmeade_station": 120.0, "leaky_cauldron": 15.0},
        allows_camping=False
    ),

    "leaky_cauldron": Location(
        id="leaky_cauldron",
        name_cs="Děravý kotlík",
        name_en="The Leaky Cauldron",
        type=LocationType.CITY,
        pvp_zone=PvPZone.SAFE,
        description="Hospoda spojující mudlovský a kouzelnický svět. Skvělý výchozí bod.",
        has_inn=True,
        has_shop=True,
        connections={"kings_cross": 15.0, "diagon_alley": 2.0},
        allows_camping=False,
        spawn_point=True
    ),

    "diagon_alley": Location(
        id="diagon_alley",
        name_cs="Příčná ulice",
        name_en="Diagon Alley",
        type=LocationType.CITY,
        pvp_zone=PvPZone.SAFE,
        description="Hlavní obchodní čtvrť pro kouzelníky. Vždy plno lidí.",
        has_shop=True,
        has_bank=True,
        has_inn=True,
        has_quest_board=True,
        connections={"leaky_cauldron": 2.0, "knockturn_alley": 5.0, "ministry": 20.0, "st_mungos": 15.0},
        allows_camping=False
    ),

    "knockturn_alley": Location(
        id="knockturn_alley",
        name_cs="Obrtlá ulice",
        name_en="Knockturn Alley",
        type=LocationType.CITY,
        pvp_zone=PvPZone.OPEN,
        description="⚔️ Temná ulička plná černokněžníků a nelegálního zboží. Open PvP!",
        has_shop=True, # Černý trh
        visibility=0.7,
        connections={"diagon_alley": 5.0},
        allows_camping=False
    ),

    "st_mungos": Location(
        id="st_mungos",
        name_cs="Nemocnice sv. Munga",
        name_en="St Mungo's Hospital",
        type=LocationType.CITY,
        pvp_zone=PvPZone.SAFE,
        description="Kouzelnická nemocnice pro léčbu magických zranění a nemocí.",
        has_healer=True,
        connections={"diagon_alley": 15.0, "ministry": 10.0},
        allows_camping=False
    ),

    "ministry": Location(
        id="ministry",
        name_cs="Ministerstvo kouzel",
        name_en="Ministry of Magic",
        type=LocationType.MINISTRY,
        pvp_zone=PvPZone.SAFE,
        description="Sídlo vlády britského kouzelnického společenství. Přísná kontrola.",
        has_quest_board=True,
        has_trainer=True,
        connections={"diagon_alley": 20.0, "st_mungos": 10.0},
        allows_camping=False,
        allows_apparition=False # Lze jen letaxem / vchodem
    ),

    "grimmauld_place": Location(
        id="grimmauld_place",
        name_cs="Grimmauldovo náměstí 12",
        name_en="Grimmauld Place",
        type=LocationType.CITY,
        pvp_zone=PvPZone.SAFE,
        description="Starobylé sídlo rodiny Blacků, skryté před mudly. Bezpečný úkryt.",
        has_inn=True,
        connections={"leaky_cauldron": 25.0},
        allows_camping=False
    ),

    # ================= OSTATNÍ A VENKOV =================

    "the_burrow": Location(
        id="the_burrow",
        name_cs="Doupě",
        name_en="The Burrow",
        type=LocationType.VILLAGE,
        pvp_zone=PvPZone.SAFE,
        description="Domov rodiny Weasleyových. Chaos, ale útulno.",
        has_healer=True,
        connections={"ottery_st_catchpole": 15.0}
    ),

    "ottery_st_catchpole": Location(
        id="ottery_st_catchpole",
        name_cs="Vydrník sv. Drába",
        name_en="Ottery St Catchpole",
        type=LocationType.VILLAGE,
        pvp_zone=PvPZone.CONSENSUAL,
        description="Malá mudlovská vesnice s utajenou kouzelnickou komunitou.",
        resources={"wormwood": 0.2, "dittany": 0.05},
        connections={"the_burrow": 15.0, "leaky_cauldron": 60.0} # Dlouhá cesta pěšky, ideální na přemístění
    ),

    "godrics_hollow": Location(
        id="godrics_hollow",
        name_cs="Godrikův důl",
        name_en="Godric's Hollow",
        type=LocationType.VILLAGE,
        pvp_zone=PvPZone.SAFE,
        description="Historická vesnice s památníkem Potterových. Klidné místo.",
        has_inn=True,
        has_shop=True,
        connections={"godrics_graveyard": 5.0, "leaky_cauldron": 80.0}
    ),

    "godrics_graveyard": Location(
        id="godrics_graveyard",
        name_cs="Hřbitov v Godrikově dole",
        name_en="Godric's Hollow Graveyard",
        type=LocationType.RUINS,
        pvp_zone=PvPZone.OPEN,
        description="⚔️ Strašidelný starý hřbitov. V noci sem nikdo nechodí.",
        weather=Weather.NIGHT,
        resources={"moonstone": 0.2},
        connections={"godrics_hollow": 5.0}
    ),

    "malfoy_manor": Location(
        id="malfoy_manor",
        name_cs="Sídlo Malfoyů",
        name_en="Malfoy Manor",
        type=LocationType.WILDERNESS,
        pvp_zone=PvPZone.OPEN,
        description="⚔️ Temné a elegantní sídlo. Často se zde schází pochybné existence.",
        weather=Weather.STORM,
        connections={"knockturn_alley": 40.0}
    ),

    "azkaban": Location(
        id="azkaban",
        name_cs="Azkaban",
        name_en="Azkaban",
        type=LocationType.DUNGEON,
        pvp_zone=PvPZone.OPEN,
        description="💀 NEJVYŠŠÍ NEBEZPEČÍ! Temná věznice strážená mozkomory.",
        weather=Weather.STORM,
        visibility=0.1,
        connections={"ministry": 120.0}, # Pouze lodí/speciálním transportem z ministerstva
        allows_apparition=False,
        allows_camping=False
    ),
# ================= DETAIL BRADAVIC =================
    
    "great_hall": Location(
        id="great_hall",
        name_cs="Velká síň",
        name_en="Great Hall",
        type=LocationType.SCHOOL,
        pvp_zone=PvPZone.SAFE,
        description="Srdce Bradavic s kouzelným stropem. Ideální místo pro setkávání hráčů.",
        has_inn=True,
        connections={"hogwarts": 2.0, "hogwarts_dungeons": 5.0},
        allows_apparition=False,
        allows_camping=False
    ),

    "hogwarts_greenhouses": Location(
        id="hogwarts_greenhouses",
        name_cs="Bradavické skleníky",
        name_en="Hogwarts Greenhouses",
        type=LocationType.SCHOOL,
        pvp_zone=PvPZone.CONSENSUAL,
        description="Zde se vyučuje bylinkářství. Plno vzácných a nebezpečných rostlin.",
        resources={"mandrake_root": 0.6, "wormwood": 0.4, "dittany": 0.2},
        connections={"hogwarts_grounds": 3.0, "hogwarts": 5.0},
        allows_apparition=False,
        allows_camping=False
    ),

    "astronomy_tower": Location(
        id="astronomy_tower",
        name_cs="Astronomická věž",
        name_en="Astronomy Tower",
        type=LocationType.SCHOOL,
        pvp_zone=PvPZone.CONSENSUAL,
        description="Nejvyšší bod hradu s nádherným výhledem. V noci se tu dobře sbírají suroviny.",
        resources={"moonstone": 0.4},
        connections={"hogwarts": 8.0},
        allows_apparition=False,
        allows_camping=False
    ),

    "room_of_requirement": Location(
        id="room_of_requirement",
        name_cs="Komnata nejvyšší potřeby",
        name_en="Room of Requirement",
        type=LocationType.SCHOOL,
        pvp_zone=PvPZone.SAFE,
        description="Zjeví se jen tomu, kdo ji opravdu potřebuje. Tajný úkryt.",
        has_bank=True, # Simulace schovaných věcí
        connections={"hogwarts": 5.0},
        allows_apparition=False,
        allows_camping=True # Výjimka v hradu!
    ),

    "chamber_of_secrets": Location(
        id="chamber_of_secrets",
        name_cs="Tajemná komnata",
        name_en="Chamber of Secrets",
        type=LocationType.DUNGEON,
        pvp_zone=PvPZone.OPEN,
        description="💀 Hluboko pod hradem. Zde neplatí žádná školní pravidla. Open PvP!",
        weather=Weather.FOG,
        visibility=0.2,
        connections={"hogwarts_dungeons": 15.0},
        allows_apparition=False,
        allows_camping=False
    ),

    "hogwarts_dungeons": Location(
        id="hogwarts_dungeons",
        name_cs="Hradní sklepení",
        name_en="Hogwarts Dungeons",
        type=LocationType.SCHOOL,
        pvp_zone=PvPZone.CONSENSUAL,
        description="Chladné a vlhké chodby. Nachází se zde učebna lektvarů.",
        connections={"great_hall": 5.0, "chamber_of_secrets": 15.0},
        allows_apparition=False,
        allows_camping=False
    ),

    # ================= DETAIL PRASINEK A PŘÍČNÉ =================

    "three_broomsticks": Location(
        id="three_broomsticks",
        name_cs="U Tří košťat",
        name_en="The Three Broomsticks",
        type=LocationType.VILLAGE,
        pvp_zone=PvPZone.SAFE,
        description="Teplá, hlučná a přátelská hospoda. Voní tu máslový ležák.",
        has_inn=True,
        has_quest_board=True,
        connections={"hogsmeade": 1.0},
        allows_camping=False
    ),

    "hogs_head": Location(
        id="hogs_head",
        name_cs="U Prasečí hlavy",
        name_en="The Hog's Head",
        type=LocationType.VILLAGE,
        pvp_zone=PvPZone.CONSENSUAL,
        description="Zapadlá a špinavá hospoda. Ideální místo pro temné obchody.",
        has_shop=True, # Pochybné zboží
        visibility=0.8,
        connections={"hogsmeade": 2.0},
        allows_camping=False
    ),

    "gringotts": Location(
        id="gringotts",
        name_cs="Gringottova banka",
        name_en="Gringotts Wizarding Bank",
        type=LocationType.CITY,
        pvp_zone=PvPZone.SAFE,
        description="Nejbezpečnější místo na světě, hned po Bradavicích.",
        has_bank=True,
        connections={"diagon_alley": 1.0, "gringotts_vaults": 10.0},
        allows_camping=False
    ),

    "gringotts_vaults": Location(
        id="gringotts_vaults",
        name_cs="Trezory u Gringottů",
        name_en="Gringotts Vaults",
        type=LocationType.DUNGEON,
        pvp_zone=PvPZone.SAFE, # Nebo OPEN, pokud chceš povolit bankovní loupeže!
        description="Hluboké podzemí hlídané draky a skřety.",
        connections={"gringotts": 10.0},
        allows_apparition=False,
        allows_camping=False
    ),

    "borgin_and_burkes": Location(
        id="borgin_and_burkes",
        name_cs="Borgin a Burkes",
        name_en="Borgin and Burkes",
        type=LocationType.CITY,
        pvp_zone=PvPZone.OPEN,
        description="⚔️ Obchod s černou magií. Raději se tu k nikomu neotáčej zády.",
        has_shop=True,
        connections={"knockturn_alley": 1.0},
        allows_camping=False
    ),

    "department_of_mysteries": Location(
        id="department_of_mysteries",
        name_cs="Odbor záhad",
        name_en="Department of Mysteries",
        type=LocationType.MINISTRY,
        pvp_zone=PvPZone.OPEN,
        description="💀 Přísně tajné podlaží Ministerstva. Extrémně nebezpečná zóna.",
        visibility=0.5,
        connections={"ministry": 5.0},
        allows_apparition=False,
        allows_camping=False
    ),

    # ================= DIVOČINA A DALŠÍ MÍSTA =================

    "forest_of_dean": Location(
        id="forest_of_dean",
        name_cs="Lesy v Deanu",
        name_en="Forest of Dean",
        type=LocationType.WILDERNESS,
        pvp_zone=PvPZone.CONSENSUAL,
        description="Rozlehlé mudlovské lesy. Výborné místo pro skrytý kemp a sběr surovin.",
        resources={"wormwood": 0.5, "dittany": 0.3, "moonstone": 0.1},
        connections={"leaky_cauldron": 180.0, "godrics_hollow": 60.0}, # Daleko!
        allows_camping=True
    ),

    "shell_cottage": Location(
        id="shell_cottage",
        name_cs="Lasturová vila",
        name_en="Shell Cottage",
        type=LocationType.WILDERNESS,
        pvp_zone=PvPZone.SAFE,
        description="Osamělý domek na útesu u moře. Chráněn Fideliovým zaklínadlem.",
        has_healer=True,
        has_inn=True,
        weather=Weather.RAIN,
        connections={"forest_of_dean": 120.0},
        allows_camping=False
    ),

    "spinners_end": Location(
        id="spinners_end",
        name_cs="Tkalcovská ulička",
        name_en="Spinner's End",
        type=LocationType.CITY,
        pvp_zone=PvPZone.OPEN,
        description="⚔️ Zchátralá průmyslová čtvrť. Domov některých Smrtijedů.",
        weather=Weather.FOG,
        connections={"leaky_cauldron": 90.0, "malfoy_manor": 45.0}
    ),

    "little_hangleton": Location(
        id="little_hangleton",
        name_cs="Malý Visánek",
        name_en="Little Hangleton",
        type=LocationType.VILLAGE,
        pvp_zone=PvPZone.CONSENSUAL,
        description="Zapadlá vesnice s temnou minulostí.",
        connections={"riddle_house": 10.0, "little_hangleton_graveyard": 5.0, "leaky_cauldron": 150.0}
    ),

    "riddle_house": Location(
        id="riddle_house",
        name_cs="Raddleův statek",
        name_en="Riddle House",
        type=LocationType.RUINS,
        pvp_zone=PvPZone.OPEN,
        description="⚔️ Opuštěné, chátrající sídlo na kopci nad vesnicí.",
        weather=Weather.STORM,
        connections={"little_hangleton": 10.0}
    ),

    "little_hangleton_graveyard": Location(
        id="little_hangleton_graveyard",
        name_cs="Hřbitov v Malém Visánku",
        name_en="Little Hangleton Graveyard",
        type=LocationType.DUNGEON,
        pvp_zone=PvPZone.OPEN,
        description="💀 Místo, kde se zrodila noční můra. Zde buďte velmi opatrní.",
        weather=Weather.FOG,
        visibility=0.4,
        resources={"moonstone": 0.5, "unicorn_hair": 0.1},
        connections={"little_hangleton": 5.0}
    ),

    "lovegood_house": Location(
        id="lovegood_house",
        name_cs="Dům Láskorádových",
        name_en="Lovegood House",
        type=LocationType.WILDERNESS,
        pvp_zone=PvPZone.CONSENSUAL,
        description="Podivná věžovitá stavba nedaleko Vydrníku sv. Drába.",
        connections={"ottery_st_catchpole": 10.0}
    ),

    "azkaban_cells": Location(
        id="azkaban_cells",
        name_cs="Cely Azkabanu",
        name_en="Azkaban Cells",
        type=LocationType.DUNGEON,
        pvp_zone=PvPZone.OPEN,
        description="💀 Mrazivé cely obklopené beznadějí. Útěk je téměř nemožný.",
        weather=Weather.STORM,
        visibility=0.0,
        connections={"azkaban": 5.0},
        allows_apparition=False,
        allows_camping=False
    ),

    "nurmengard": Location(
        id="nurmengard",
        name_cs="Nurmengard",
        name_en="Nurmengard",
        type=LocationType.DUNGEON,
        pvp_zone=PvPZone.OPEN,
        description="💀 Grindelwaldovo temné vězení vysoko v horách.",
        weather=Weather.SNOW,
        connections={"ministry": 240.0}, # Mezinárodní letax/přenášedlo
        allows_apparition=False,
        allows_camping=False
    ),
    
    "weasleys_wizard_wheezes": Location(
        id="weasleys_wizard_wheezes",
        name_cs="Kratochvilné kouzelnické kejkle",
        name_en="Weasleys' Wizard Wheezes",
        type=LocationType.CITY,
        pvp_zone=PvPZone.SAFE,
        description="Hlučný, zářivě barevný obchod plný kanadských žertíků.",
        has_shop=True,
        connections={"diagon_alley": 1.0},
        allows_camping=False
    )
}


class WorldSystem:
    """Hlavní správce herního světa"""
    
    def __init__(self):
        self.locations: Dict[str, Location] = LOCATIONS
        self.players: Dict[int, PlayerWorldState] = {}
        self.active_camps: Dict[str, Camp] = {}

    def get_player(self, player_id: int) -> PlayerWorldState:
        """Získá nebo vytvoří stav hráče"""
        if player_id not in self.players:
            # Nový hráč začíná v Prasinkách (spawn point)
            self.players[player_id] = PlayerWorldState(player_id=player_id)
            self.locations["hogsmeade"].players_present.add(player_id)
        return self.players[player_id]

    def start_travel(self, player_id: int, destination_id: str) -> Tuple[bool, str]:
        """Zahájí cestování hráče do jiné lokace"""
        player = self.get_player(player_id)
        
        if player.traveling:
            return False, "Již cestuješ."
            
        if destination_id not in self.locations:
            return False, "Tato lokace neexistuje."
            
        current_loc = self.locations[player.current_location]
        
        if destination_id not in current_loc.connections:
            # Kontrola přemisťování (Apparition)
            dest_loc = self.locations[destination_id]
            if not current_loc.allows_apparition or not dest_loc.allows_apparition:
                return False, f"Do lokace {dest_loc.name_cs} nelze cestovat přímo a přemisťování je zde blokováno."
            travel_time = 5.0 # Přemístění je rychlé, ale stojí víc many (řešeno jinde)
        else:
            travel_time = current_loc.connections[destination_id]
            
        # Odebrání z aktuální lokace
        if player_id in current_loc.players_present:
            current_loc.players_present.remove(player_id)
            
        if player.current_camp:
            self.leave_camp(player_id)

        player.traveling = True
        player.travel_destination = destination_id
        player.travel_eta = time.time() + travel_time
        player.last_location = player.current_location
        
        return True, f"Vydal ses na cestu do {self.locations[destination_id].name_cs}. Cesta potrvá {travel_time} vteřin."

    def update(self):
        """Pravidelný update světa (voláno např. v hlavní smyčce hry)"""
        current_time = time.time()
        
        # 1. Zpracování cestování
        for player in self.players.values():
            if player.traveling and player.travel_destination:
                if current_time >= player.travel_eta:
                    self._finish_travel(player)
                    
        # 2. Expirace kempů
        camps_to_remove = []
        for camp_id, camp in self.active_camps.items():
            if camp.expires_at > 0 and current_time >= camp.expires_at:
                camps_to_remove.append(camp_id)
                
        for camp_id in camps_to_remove:
            self.destroy_camp(camp_id)

    def _finish_travel(self, player: PlayerWorldState):
        """Dokončí cestování hráče"""
        dest_id = player.travel_destination
        player.current_location = dest_id
        player.traveling = False
        player.travel_destination = None
        player.travel_eta = 0.0
        
        dest_loc = self.locations[dest_id]
        dest_loc.players_present.add(player.player_id)
        
        # Pokud hráč vstoupí do Open PvP zóny, automaticky se mu zapne PvP
        if dest_loc.pvp_zone == PvPZone.OPEN:
            player.pvp_enabled = True

    def create_camp(self, player_id: int, camp_name: str) -> Tuple[bool, str]:
        """Vytvoří tábor v aktuální lokaci"""
        player = self.get_player(player_id)
        location = self.locations[player.current_location]
        
        if not location.allows_camping:
            return False, "V této lokaci není možné tábořit."
            
        if player.current_camp:
            return False, "Už jsi v jiném táboře."
            
        camp_id = f"camp_{player_id}_{int(time.time())}"
        
        new_camp = Camp(
            id=camp_id,
            owner_id=player_id,
            location_id=player.current_location,
            name=camp_name,
            expires_at=time.time() + (60 * 60 * 24) # Expirace za 24 hodin
        )
        
        new_camp.members.add(player_id)
        self.active_camps[camp_id] = new_camp
        location.camps[camp_id] = new_camp
        
        player.current_camp = camp_id
        player.owned_camps.append(camp_id)
        
        return True, f"Tábor '{camp_name}' byl úspěšně založen."

    def leave_camp(self, player_id: int) -> bool:
        """Hráč opustí aktuální tábor"""
        player = self.get_player(player_id)
        if not player.current_camp:
            return False
            
        camp = self.active_camps.get(player.current_camp)
        if camp and player_id in camp.members:
            camp.members.remove(player_id)
            if player_id in camp.resting:
                camp.resting.remove(player_id)
                
        player.current_camp = None
        return True

    def destroy_camp(self, camp_id: str):
        """Zničí tábor"""
        if camp_id not in self.active_camps:
            return
            
        camp = self.active_camps[camp_id]
        location = self.locations.get(camp.location_id)
        
        if location and camp_id in location.camps:
            del location.camps[camp_id]
            
        # Vyhodit všechny hráče
        for member_id in list(camp.members):
            self.leave_camp(member_id)
            
        del self.active_camps[camp_id]

    def toggle_pvp(self, player_id: int) -> Tuple[bool, str]:
        """Přepne PvP mód hráče"""
        player = self.get_player(player_id)
        location = self.locations[player.current_location]
        
        if location.pvp_zone == PvPZone.SAFE:
            player.pvp_enabled = False
            return False, "V bezpečné zóně nemůžeš zapnout PvP."
            
        if location.pvp_zone == PvPZone.OPEN:
            player.pvp_enabled = True
            return False, "V této zóně je PvP trvale zapnuto!"
            
        player.pvp_enabled = not player.pvp_enabled
        status = "zapnuto" if player.pvp_enabled else "vypnuto"
        return True, f"PvP bylo {status}."

    def get_local_players(self, player_id: int, include_hidden: bool = False) -> List[int]:
        """Vrátí seznam hráčů ve stejné lokaci"""
        player = self.get_player(player_id)
        location = self.locations[player.current_location]
        
        visible_players = []
        for other_id in location.players_present:
            if other_id == player_id:
                continue
            other_player = self.get_player(other_id)
            if not other_player.hidden or include_hidden:
                visible_players.append(other_id)
                
        return visible_players