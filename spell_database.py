"""
Spell Database Builder
Zpracuje dokument s kouzly a vytvoří strukturovanou databázi
"""

import json
import re

# Manuálně vytvoříme databázi klíčových kouzel s realistickými efekty
# (Automatické parsování by bylo složité kvůli struktuře dokumentu)


SPELLS_DATABASE = {
"aberto": {
    "name_cs": "Aberto",
    "name_en": "Aberto",
    "incantation": "Aberto",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Odemyká dveře, je silnější než Alohomora. Použito ve filmu Fantastická zvířata a kde je najít. Z portugalského aberto, což znamená „otevřený“....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"accio": {
    "name_cs": "Accio",
    "name_en": "Accio",
    "incantation": "Accio",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Přivolávací kouzlo, které přivolá předmět ke kouzelníkovi. Většinou se používá v kombinaci s pojmenováním daného předmětu, například accio koště. Formule pochází z latiny a znamená „volám, přivolávám“...",
    "learning_time_hours": 5,
    "legality": "legal",
    "reputation_impact": 0
},

"accio_lumarum": {
    "name_cs": "Accio Lumarum",
    "name_en": "Accio Lumarum",
    "incantation": "Accio Lumarum",
    "type": "defensive",
    "category": "shield",
    "difficulty": 6,
    "cooldown": 15,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Ochranné kouzlo. Přenese člověka na jiné místo, poprvé použito ve filmu Fantastická zvířata a kde je najít....",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"aguamenti": {
    "name_cs": "Aguamenti",
    "name_en": "Aguamenti",
    "incantation": "Aguamenti",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 25,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Vykouzlí z hůlky fontánku vody. V Bradavicích se učí v šestém ročníku, a v šestém díle knihy se objevuje několikrát. Agua znamená španělsky voda, a pochází z latinského aqua. Mentio je latinsky „prohl...",
    "learning_time_hours": 6,
    "legality": "legal",
    "reputation_impact": 0
},

"alerte_ascendere": {
    "name_cs": "Alerte Ascendere",
    "name_en": "Alerte Ascendere",
    "incantation": "Alerte Ascendere",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Jedná se o kouzlo, které svým efektem vymrští cíl vysoko do vzduchu. Zlatoslav Lockhart použil toto kouzlo v dílu Harry Potter a Tajemná komnata (film a kniha) na hada, kterého vyčaroval Draco Malfoy,...",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"alohomora": {
    "name_cs": "Alohomora",
    "name_en": "Alohomora",
    "incantation": "Alohomora",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Zaklínadlo sloužící k odemykání zamčených (dveří, oken atd.). Poprvé ho v knize již v prvním díle použila Hermiona Grangerová. Protikouzlo Colloportus....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": -2
},

"amato_animo_animato_animagus": {
    "name_cs": "Amato Animo Animato Animagus",
    "name_en": "Amato Animo Animato Animagus",
    "incantation": "Amato Animo Animato Animagus",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 10,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo používané zvěromágy k jejich přeměně. Před pronesením formule je třeba přiložit hůlku na srdce sesilatele, který musí vypít lektvar Animagus. Na tento lektvar je třeba kromě jiného taky list ma...",
    "learning_time_hours": 40,
    "legality": "legal",
    "reputation_impact": 0
},

"anapneo": {
    "name_cs": "Anapneo",
    "name_en": "Anapneo",
    "incantation": "Anapneo",
    "type": "healing",
    "category": "healing",
    "difficulty": 5,
    "cooldown": 12,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "healing",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "green",
        "sound": "heal",
        "projectile": False
    },
    "description": "Kouzlo proti dušení. V šestém díle ho použil Horacio Křiklan na Marcuse Belbyho. Řecké slovo anapneo (αναπνεω) znamená „nadechuji se“....",
    "learning_time_hours": 18,
    "legality": "legal",
    "reputation_impact": 0
},

"anteocula": {
    "name_cs": "Anteocula",
    "name_en": "Anteocula",
    "incantation": "Anteocula",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 8,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Kouzlo přeměňující vlasy cíle v parohy....",
    "learning_time_hours": 4,
    "legality": "forbidden",
    "reputation_impact": -30
},

"aparecium": {
    "name_cs": "Aparecium",
    "name_en": "Aparecium",
    "incantation": "Aparecium",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Zobrazí neviditelný inkoust. Z latinského apparere, což znamená „objevit se“....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"aqua_carcerem": {
    "name_cs": "Aqua Carcerem",
    "name_en": "Aqua Carcerem",
    "incantation": "Aqua Carcerem",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Po zasáhnutí soupeře tímto kouzlem se u soupeře objeví koule vody, která ho do sebe uzavře a soupeř po dobu třiceti sekund nemůže nic dělat a jenom nehybně stojí v kouli z bubliny. (Po půl minutě se k...",
    "learning_time_hours": 7,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"aqua_erupto": {
    "name_cs": "Aqua Erupto",
    "name_en": "Aqua Erupto",
    "incantation": "Aqua Erupto",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Vytvoří velký a silný proud vody z konce hůlky....",
    "learning_time_hours": 3,
    "legality": "legal",
    "reputation_impact": 0
},

"arania_exhuma": {
    "name_cs": "Arania Exhuma",
    "name_en": "Arania Exhuma",
    "incantation": "Arania Exhuma",
    "type": "defensive",
    "category": "shield",
    "difficulty": 5,
    "cooldown": 5,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Kouzlo proti pavoukům. V druhém díle ho použil poprvé Tom Rojvol Raddle (pozdější Lord Voldemort) proti Aragogovi, později ho použil i Harry Potter proti pavoukům ze Zapovězeného lesa. Toto kouzlo půs...",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"arania_sortia": {
    "name_cs": "Arania Sortia",
    "name_en": "Arania Sortia",
    "incantation": "Arania Sortia",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 8,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": False
    },
    "description": "Vyvolá z hůlky pavouky....",
    "learning_time_hours": 40,
    "legality": "legal",
    "reputation_impact": -1
},

"aresto_momentum": {
    "name_cs": "Aresto Momentum",
    "name_en": "Aresto Momentum",
    "incantation": "Aresto Momentum",
    "type": "defensive",
    "category": "shield",
    "difficulty": 5,
    "cooldown": 5,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Výrazně zpomalí pád. Použito Hermionou v pátém díle při útěku ze Síně věšteb a v sedmém díle při vloupání se do Gringottovic banky. Známo také jako polštářové kouzlo. Také ho použil Albus Brumbál na H...",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"ascendio": {
    "name_cs": "Ascendio",
    "name_en": "Ascendio",
    "incantation": "Ascendio",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo podobné tryskovému pohonu. Ascendio použil Harry Potter ve čtvrtém díle, když potřeboval vyskočit z jezera. Odvozeno od latinského slovesa ascendo – jít vzhůru, zdvihat se, vystoupat....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"assa_in_tuo_suco": {
    "name_cs": "Assa in tuo suco",
    "name_en": "Assa in tuo suco",
    "incantation": "Assa in tuo suco",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 7,
    "cooldown": 15,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Kletba „usmaž se ve vlastní šťávě“....",
    "learning_time_hours": 40,
    "legality": "forbidden",
    "reputation_impact": -15
},

"avada_kedavra": {
    "name_cs": "Avada Kedavra",
    "name_en": "Avada Kedavra",
    "incantation": "Avada Kedavra",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 10,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Smrtící kletba Patří mezi tři „kletby, které se nepromíjejí“ (mezi ně patří i kouzla: Cruciatus a Imperius – za její použití je kouzelník poslán na doživotí do Azkabanu). Člověk, proti kterému je použ...",
    "learning_time_hours": 40,
    "legality": "unforgivable",
    "reputation_impact": -30
},

"avifors": {
    "name_cs": "Avifors",
    "name_en": "Avifors",
    "incantation": "Avifors",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 10,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Kouzlo Avifors je transformační kouzlo schopné přeměnit cíl v ptáka/ptáky, či netopýra/netopýry....",
    "learning_time_hours": 40,
    "legality": "forbidden",
    "reputation_impact": 0
},

"avis": {
    "name_cs": "Avis",
    "name_en": "Avis",
    "incantation": "Avis",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Kouzlo vytvářející hejno ptáků. Při seslání vydá kouzlo střelbě podobný zvuk a kouř. Ve čtvrtém díle ho použil Ollivander na prověření Krumovy hůlky. V šestém díle Hermiona následně ptáčky kletbou Opp...",
    "learning_time_hours": 16,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"balit": {
    "name_cs": "Balit",
    "name_en": "Balit",
    "incantation": "Balit",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo umožňující bez námahy sbalit vícečetné objekty do kufru, či jiného úložného prostoru. V angličtině zní Pack....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"baubillious": {
    "name_cs": "Baubillious",
    "name_en": "Baubillious",
    "incantation": "Baubillious",
    "type": "control",
    "category": "binding",
    "difficulty": 10,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Kouzlo které udělá přesně to na co uživatel myslí. Jediným známým uživatelem je Filius Kratiknot....",
    "learning_time_hours": 360,
    "legality": "legal",
    "reputation_impact": 0 
},

"bleskove_kouzlo": {
    "name_cs": "(Bleskové kouzlo)",
    "name_en": "(Bleskové kouzlo)",
    "incantation": "(Bleskové kouzlo)",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 10,
    "cooldown": 40,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Mocné kouzlo vyžadující mnoho síly. Ze špičky hůlky vyšlehne mohutný blesk. Kouzlo je tak silné, že pouze jedním použitím rozervalo gigantický štít obklopující Bradavice, na jehož tvorbě se podíleli v...",
    "learning_time_hours": 60,
    "legality": "legal_combat",
    "reputation_impact": 0 
},

"bombarda": {
    "name_cs": "Bombarda",
    "name_en": "Bombarda",
    "incantation": "Bombarda",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Formule vytvoří explozi na místě ukázání hůlky. Variantu Bombarda Maxima použila Dolores Jane Umbridgeová k probourání zdi do Komnaty nejvyšší potřeby (ve filmu se dostala a v knize se do komnaty vůbe...",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"bublinove_kouzlo": {
    "name_cs": "(Bublinové kouzlo)",
    "name_en": "(Bublinové kouzlo)",
    "incantation": "(Bublinové kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Vyčaruje velkou bublinu vzduchu, v níž je například možné dýchat pod vodou. Poprvé ho použili Cedric Diggory a Fleur Delacourová ve čtvrtém díle při plnění druhého úkolu Turnaje tří kouzelnických škol...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"brachium_emendo": {
    "name_cs": "Brachium Emendo",
    "name_en": "Brachium Emendo",
    "incantation": "Brachium Emendo",
    "type": "healing",
    "category": "healing",
    "difficulty": 5,
    "cooldown": 12,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "healing",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "green",
        "sound": "heal",
        "projectile": False
    },
    "description": "Kouzlo na opravu kosti. Brachium znamená paže a emendo spravuji....",
    "learning_time_hours": 4,
    "legality": "legal",
    "reputation_impact": 5
},

"brachaibindo": {
    "name_cs": "Brachaibindo",
    "name_en": "Brachaibindo",
    "incantation": "Brachaibindo",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Formule na spoutání nepřítele. Není tak silné jako pouta na tebe nebo petrificus totalus....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"calvorio": {
    "name_cs": "Calvorio",
    "name_en": "Calvorio",
    "incantation": "Calvorio",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 8,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Kouzlo vyvolávající okamžitou ztrátu vlasů u cíle....",
    "learning_time_hours": 40,
    "legality": "forbidden",
    "reputation_impact": -30
},

"cantis": {
    "name_cs": "Cantis",
    "name_en": "Cantis",
    "incantation": "Cantis",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 8,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Kouzlo, které nutí oběť nekontrolovatelně zpívat. Výraz souvisí s latinským cantō (zpívat) či cantus (zpěv)....",
    "learning_time_hours": 40,
    "legality": "forbidden",
    "reputation_impact": -30
},

"capacious_extremis": {
    "name_cs": "Capacious Extremis",
    "name_en": "Capacious Extremis",
    "incantation": "Capacious Extremis",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Nezjistitelné zvětšovací kouzlo, zvětší vnitřní dimenzi nádoby, či jiného úložného prostoru, zatímco vnější dimenze zůstane zachována. Tím může masivně zvýšit kapacitu i malé tašky, použito Hermionou ...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"carpe_retractum": {
    "name_cs": "Carpe Retractum",
    "name_en": "Carpe Retractum",
    "incantation": "Carpe Retractum",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Přitahovací kouzlo. Z hůlky vytryskne fialový blesk (na rozdíl od kouzla Accio, které je bez efektu) a přitáhne daný předmět. Ve třetím díle hry ho používal Ron. Carpe znamená latinsky trhej. Retract ...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"cave_inimicum": {
    "name_cs": "Cave Inimicum",
    "name_en": "Cave Inimicum",
    "incantation": "Cave Inimicum",
    "type": "defensive",
    "category": "shield",
    "difficulty": 5,
    "cooldown": 5,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Ochranné kouzlo. Pravděpodobně varuje před příchodem nepřátel. Latinsky doslova znamená pozor na nepřátele. Používala ho Hermiona v sedmém dílu na místo, kde stanovali....",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"cistem_aperio": {
    "name_cs": "Cistem Aperio",
    "name_en": "Cistem Aperio",
    "incantation": "Cistem Aperio",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo pro otvírání beden a truhel. Použil ho Tom Rojvol Raddle k otevření Hagridovy bedny s Aragogem....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"colloportus": {
    "name_cs": "Colloportus",
    "name_en": "Colloportus",
    "incantation": "Colloportus",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Formule na kouzelné uzamčení dveří. „Porte“ ve francouzštině znamená dveře, „coller“ zase lepit....",
    "learning_time_hours": 16,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"colloshoo": {
    "name_cs": "Colloshoo",
    "name_en": "Colloshoo",
    "incantation": "Colloshoo",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kouzlo vytvoří pod nohama oběti lepivou ektoplazmickou látku, která způsobí, že boty/nohy oběti se okamžitě přilepí k podlaze....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"colovaria": {
    "name_cs": "Colovaria",
    "name_en": "Colovaria",
    "incantation": "Colovaria",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo přeměňující barvu cíle....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"confringo": {
    "name_cs": "Confringo",
    "name_en": "Confringo",
    "incantation": "Confringo",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Vybuchovací kouzlo, zasažený předmět se rozletí. Použito Harrym v 7. díle při přesunu ze Zobí ulice do domu Teda Tonkse. Také použito v posledním díle na Nagini, když Harry seskočil z náruče Hagrida....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"confundus": {
    "name_cs": "Confundus",
    "name_en": "Confundus",
    "incantation": "Confundus",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 8,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Matoucí kouzlo. Protivník sebou lehce škubne při zásahu tohoto kouzla a tím je zmaten a nevšímá si okolí. Hermiona Grangerová ho v 6. díle použila na Cormaka McLaggena. Dále ho použil Severus Snape na...",
    "learning_time_hours": 40,
    "legality": "legal_combat",
    "reputation_impact": -30
},

"conjunctivitus": {
    "name_cs": "Conjunctivitus",
    "name_en": "Conjunctivitus",
    "incantation": "Conjunctivitus",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kletba zhoršující zrak. Způsobuje i bolest a použil ji Viktor Krum v prvním úkolu Turnaje tří kouzelnických škol proti samici čínského ohniváče (drak č. 3). Conjunctivitis znamená latinsky zánět spoji...",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"cornflakova_kuze": {
    "name_cs": "(Cornflaková kůže)",
    "name_en": "(Cornflaková kůže)",
    "incantation": "(Cornflaková kůže)",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 8,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Kouzlo způsobující, že se kůže na celém těle oběti obalí ovesnými vločkami....",
    "learning_time_hours": 40,
    "legality": "legal_combat",
    "reputation_impact": -30
},

"crinus_muto": {
    "name_cs": "Crinus Muto",
    "name_en": "Crinus Muto",
    "incantation": "Crinus Muto",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo měnící barvu vlasů....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"cruciatus": {
    "name_cs": "Cruciatus",
    "name_en": "Cruciatus",
    "incantation": "Cruciatus",
    "type": "combat",
    "category": "damage",
    "difficulty": 10,
    "cooldown": 30,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Druhá z kleteb, které se nepromíjejí. Způsobuje bolest, která může oběti přivodit i šílenství, jak se to stalo rodičům Nevilla Longbottoma, Frankovi a Alice Longbottomovým. Formule zní crucio a latins...",
    "learning_time_hours": 20,
    "legality": "unforgivable",
    "reputation_impact": -50
},

"defensio": {
    "name_cs": "Defensio",
    "name_en": "Defensio",
    "incantation": "Defensio",
    "type": "defensive",
    "category": "shield",
    "difficulty": 4,
    "cooldown": 5,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Obranné kouzlo....",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"deferzo": {
    "name_cs": "Deferzo",
    "name_en": "Deferzo",
    "incantation": "Deferzo",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kletba způsobí okamžité zmenšení předmětu....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"defodio": {
    "name_cs": "Defodio",
    "name_en": "Defodio",
    "incantation": "Defodio",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Defodio je drtící kouzlo. Působí na cíl vysokým tlakem a tak ho ničí. V minulosti bylo používáno k vyhrabávání truhel. V sedmém díle bylo použito při útěku Harryho, Rona a Hermiony z Gringottovy banky...",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"deletrius": {
    "name_cs": "Deletrius",
    "name_en": "Deletrius",
    "incantation": "Deletrius",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Vyvolává zmizení daného předmětu. Delere znamená latinsky ničit....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"densaugeo": {
    "name_cs": "Densaugeo",
    "name_en": "Densaugeo",
    "incantation": "Densaugeo",
    "type": "healing",
    "category": "healing",
    "difficulty": 5,
    "cooldown": 12,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "healing",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "green",
        "sound": "heal",
        "projectile": False
    },
    "description": "Způsobuje nekontrolovatelný růst zubů. Kouzlo může být použito i na obnovení ztracených zubů. Z latinského dens, což znamená zub, a augeo, což znamená zvětšuji. Použil ho Draco Malfoy na Harryho Potte...",
    "learning_time_hours": 18,
    "legality": "legal",
    "reputation_impact": 5
},

"deprimo": {
    "name_cs": "Deprimo",
    "name_en": "Deprimo",
    "incantation": "Deprimo",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Kouzlo vytvářející obrovský tlak na povrch cíle. V sedmém díle ho použila Hermiona, aby unikli z domu Xenofilia Láskoráda před Smrtijedy....",
    "learning_time_hours": 16,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"depulso": {
    "name_cs": "Depulso",
    "name_en": "Depulso",
    "incantation": "Depulso",
    "type": "defensive",
    "category": "shield",
    "difficulty": 5,
    "cooldown": 5,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Odpuzující kouzlo, stejné kouzlo jako expeliarmus...",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"descendo": {
    "name_cs": "Descendo",
    "name_en": "Descendo",
    "incantation": "Descendo",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Způsobí, že objekt spadne nebo se posune dolů. První použití bylo v 6. díle Harry Potter a Princ dvojí krve Descendo je latinský výraz pro \"sestupuji\"....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"destrukto": {
    "name_cs": "destrukto",
    "name_en": "destrukto",
    "incantation": "destrukto",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kouzlo vyšle záblesk modrého světla, který zasáhne objekt a zdevastuje vše v okolí. Bylo předvedeno Bellatrix Lestrangeovou v šestém díle, kde rozbilo všechna okna ve velké místnosti a zanechalo za se...",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"diffindo": {
    "name_cs": "Diffindo",
    "name_en": "Diffindo",
    "incantation": "Diffindo",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Řezací kouzlo. Bylo vytvořeno za účelem správného sestřižení šatů Delfinou Crimpovou. Jeho efektem může být i trhání a praskání cílového materiálu. Ve čtvrtém díle knihy ho použil Harry Potter k roztr...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"diminuendo": {
    "name_cs": "Diminuendo",
    "name_en": "Diminuendo",
    "incantation": "Diminuendo",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo zmenšující objekty. Použil ho při tréninku Nigel Wolpert v Komnatě nejvyšší potřeby ve filmu Harry Potter a Fénixův řád. Je podobné kouzlu Reducio....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"dissendium": {
    "name_cs": "Dissendium",
    "name_en": "Dissendium",
    "incantation": "Dissendium",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Odhaluje tajné vchody. Bylo použito na otevření hrbu sochy jednooké čarodějnice, který je vchodem do tajné chodby (o té se Harry dozvěděl z Pobertova plánku) z Bradavic do sklepa Medového ráje v Prasi...",
    "learning_time_hours": 16,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"draconifors": {
    "name_cs": "Draconifors",
    "name_en": "Draconifors",
    "incantation": "Draconifors",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Přemění cíl v draka. Pokud je použito studentem s nevelkými schopnostmi magie, většinou přemění cíl pouze v malého dráčka....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"ducklifors": {
    "name_cs": "Ducklifors",
    "name_en": "Ducklifors",
    "incantation": "Ducklifors",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Přemění cíl v kachnu....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"duro": {
    "name_cs": "Duro",
    "name_en": "Duro",
    "incantation": "Duro",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Promění cokoliv kromě přírodních živlů v kámen. V sedmém dílu ho použila Hermiona. Formule znamená v latině ztvrzuji, činím něco tvrdým....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"ebublio": {
    "name_cs": "Ebublio",
    "name_en": "Ebublio",
    "incantation": "Ebublio",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kouzlo uvězní nepřátele ve velké, pevné bublině. Kouzlo může být použito i v útočné formě, kdy cíl vybuchne do stovek barevných bublin. To však vyžaduje zároveň použití zavlažovacího kouzla. Seslání k...",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"ebublio_maxima": {
    "name_cs": "Ebublio Maxima",
    "name_en": "Ebublio Maxima",
    "incantation": "Ebublio Maxima",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kouzlo je velice podobné kouzlu Ebublio, ale bublina má možnost zachytit více cílů najednou....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"enervate": {
    "name_cs": "Enervate",
    "name_en": "Enervate",
    "incantation": "Enervate",
    "type": "healing",
    "category": "healing",
    "difficulty": 5,
    "cooldown": 12,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "healing",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "green",
        "sound": "heal",
        "projectile": False
    },
    "description": "Probudí člověka z bezvědomí. Je to protikouzlo proti Omračujícímu kouzlu Stupefy. Je doprovázeno červeným světlem. Někdy bývá uváděno jako Rennervate....",
    "learning_time_hours": 18,
    "legality": "legal",
    "reputation_impact": 5
},

"engorgio": {
    "name_cs": "Engorgio",
    "name_en": "Engorgio",
    "incantation": "Engorgio",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Zvětšovací kouzlo. Protikouzlem je kouzlo Reducio. Použito Bartym Skrkem mladším (byl převlečen mnoholičným lektvarem za Pošuka Moodyho) při první hodině, když žákům předváděl kletby, které se nepromí...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"engorgio_skullus": {
    "name_cs": "Engorgio Skullus",
    "name_en": "Engorgio Skullus",
    "incantation": "Engorgio Skullus",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo disproporčně zvětší hlavu. Protikouzlem je kouzlo Redactum Skullus....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"entomorphis": {
    "name_cs": "Entomorphis",
    "name_en": "Entomorphis",
    "incantation": "Entomorphis",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo přeměňující cíl v hmyz. Funguje pouze po krátkou dobu....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"epidior": {
    "name_cs": "Epidior",
    "name_en": "Epidior",
    "incantation": "Epidior",
    "type": "healing",
    "category": "healing",
    "difficulty": 5,
    "cooldown": 12,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "healing",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "green",
        "sound": "heal",
        "projectile": False
    },
    "description": "Kouzlo, které kolem vás a ostatních blízko vás vykouzlí kouli žlutých blesků a ty vám zahojí lehká zranění (podobné kouzlu Episkey, ale toto může být použito na více lidí)....",
    "learning_time_hours": 18,
    "legality": "legal",
    "reputation_impact": 5
},

"episkey": {
    "name_cs": "Episkey",
    "name_en": "Episkey",
    "incantation": "Episkey",
    "type": "healing",
    "category": "healing",
    "difficulty": 2,
    "cooldown": 12,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "healing",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "green",
        "sound": "heal",
        "projectile": False
    },
    "description": "Užívá se pro zhojení relativně lehkých zranění. V šestém díle tímto kouzlem (ve filmu Lenka Láskorádová, v knize Nymfadora Tonksová) napravila zlomený nos Harrymu. Řecky episkeui (επισκευή) znamená op...",
    "learning_time_hours": 2,
    "legality": "legal",
    "reputation_impact": 5
},

"epoximise": {
    "name_cs": "Epoximise",
    "name_en": "Epoximise",
    "incantation": "Epoximise",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Transformační kouzlo, které spojí dva cíle dohromady....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"erecto": {
    "name_cs": "Erecto",
    "name_en": "Erecto",
    "incantation": "Erecto",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Z příslušných součástí postaví skoro všechno. Harry, Ron a Hermiona toto kouzlo často používali v Harry Potter a relikvie smrti pro postavení svého stanu, když se často přesouvali z místa na místo a s...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"evanesco": {
    "name_cs": "Evanesco",
    "name_en": "Evanesco",
    "incantation": "Evanesco",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Odstraňovací kouzlo. Z latinského slova evanescere, které znamená zmizet. Poprvé jej použil Bill Weasley v pátém díle, aby odstranil plány, které zbyly po poradě Fénixova řádu. Severus Snape jím běžně...",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"everte_statim_v_angl._everte_statum": {
    "name_cs": "Everte Statim (v angl. Everte Statum)",
    "name_en": "Everte Statim (v angl. Everte Statum)",
    "incantation": "Everte Statim (v angl. Everte Statum)",
    "type": "combat",
    "category": "damage",
    "difficulty": 2,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Latinsky everto = vyvracet, statim = okamžitý, naléhavý, neprodleně neodkladný. Používá se pro odhození protivníka stranou. Řadí se mezi soubojová kouzla. Poprvé ho použil Draco Malfoy ve filmu ve dru...",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"patronovo_zaklinadlo_expecto_patronum": {
    "name_cs": "Patronovo zaklínadlo (Expecto Patronum)",
    "name_en": "Patronovo zaklínadlo (Expecto Patronum)",
    "incantation": "Patronovo zaklínadlo (Expecto Patronum)",
    "type": "defensive",
    "category": "shield",
    "difficulty": 9,
    "cooldown": 10,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Vykouzlí patrona, pozitivní sílu, Ochránce, který má v případě, že je opravdu mocný, podobu zvířete a je velmi účinný proti mozkomorům a dalším nebezpečným magickým tvorům. Podoba Ochránce je charakte...",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 20
},

"expelliarmus": {
    "name_cs": "Expelliarmus",
    "name_en": "Expelliarmus",
    "incantation": "Expelliarmus",
    "type": "defensive",
    "category": "shield",
    "difficulty": 1,
    "cooldown": 5,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Odzbrojovací kouzlo. Člověk, který je touto kletbou zasažen, ztratí hůlku (vyletí mu z ruky), a pokud je kletba dost silná, je schopna ho i udeřit či zvednout do vzduchu a odhodit. Kouzlo při použití ...",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"expertonum": {
    "name_cs": "Expertonum",
    "name_en": "Expertonum",
    "incantation": "Expertonum",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Ovládá oheň....",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"expulso": {
    "name_cs": "Expulso",
    "name_en": "Expulso",
    "incantation": "Expulso",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Rychlé kouzlo. Pokud ho kouzelník nabije, funguje jako automatická puška. Člověka, kterého toto kouzlo zasáhne, čeká velmi nepříjemné pokračování. Toto kouzlo bylo použito v sedmém díle....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"fenesta": {
    "name_cs": "Fenesta",
    "name_en": "Fenesta",
    "incantation": "Fenesta",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Ničí sklo na drobné střepiny. Použito ve filmu Fantastická zvířata a kde je najít....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"ferula": {
    "name_cs": "Ferula",
    "name_en": "Ferula",
    "incantation": "Ferula",
    "type": "healing",
    "category": "healing",
    "difficulty": 5,
    "cooldown": 12,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "healing",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "green",
        "sound": "heal",
        "projectile": False
    },
    "description": "Vykouzlí obvazy a omotá je kolem končetiny či jiné zraněné části těla. Použito ve třetím díle Remusem Lupinem na Rona....",
    "learning_time_hours": 18,
    "legality": "legal",
    "reputation_impact": 5
},

"fianto_duri": {
    "name_cs": "Fianto Duri",
    "name_en": "Fianto Duri",
    "incantation": "Fianto Duri",
    "type": "defensive",
    "category": "shield",
    "difficulty": 5,
    "cooldown": 5,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Ochranné kouzlo, které zpevňuje již existující bariéru. Použili ho v sedmém díle filmu Filius Kratiknot spolu s Molly Weasleyovou a Horáciem Křiklanem při vytváření magické bariéry kolem Bradavic....",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"fiat_lux": {
    "name_cs": "Fiat Lux",
    "name_en": "Fiat Lux",
    "incantation": "Fiat Lux",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Vykouzlí slabé světlo v okolí kouzelníka....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"fideliovo_zaklinadlo": {
    "name_cs": "(Fideliovo zaklínadlo)",
    "name_en": "(Fideliovo zaklínadlo)",
    "incantation": "(Fideliovo zaklínadlo)",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Ukrývací kouzlo. Pro jeho provedení je třeba důvěryhodná osoba, která jediná ví, jak skrytou věc najít. Bylo tak zamaskováno například sídlo Fénixova řádu, dům Fleur a Billa nebo také dům Potterových....",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"fiendfyre[3]": {
    "name_cs": "Fiendfyre[3]",
    "name_en": "Fiendfyre[3]",
    "incantation": "Fiendfyre[3]",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 8,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Kletba vyčaruje zložár, ohnivé duchy, již zničí vše v okolí. Použil ji Vincent Crabbe v sedmém dílu série v Komnatě nejvyšší potřeby proti Harrymu, Hermioně a Ronovi. Kouzlo se však vymklo kontrole, z...",
    "learning_time_hours": 40,
    "legality": "forbidden",
    "reputation_impact": -30
},

"finite": {
    "name_cs": "Finite",
    "name_en": "Finite",
    "incantation": "Finite",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Ruší probíhající děje. Neslouží k odstranění následků proběhlých. Finite incantatem ruší působící kouzla. Finite je latinsky „skončete“ a incantatum je „zaklínadlo, kouzlo“. Ve druhém díle jej použila...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"flagrante": {
    "name_cs": "Flagrante",
    "name_en": "Flagrante",
    "incantation": "Flagrante",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Kletba, která způsobí, že očarovaný objekt popálí kohokoliv, kdo se jej dotkne....",
    "learning_time_hours": 16,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"flagrate": {
    "name_cs": "Flagrate",
    "name_en": "Flagrate",
    "incantation": "Flagrate",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlí ohnivé čáry ve vzduchu, slouží ke psaní do prostoru. Ohnivým X označila v 5. knize Hermiona dveře vedoucí do místností na odboru záhad. Formule znamená latinsky spálenina. Ve druhém díle pomocí...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"flipendo": {
    "name_cs": "Flipendo",
    "name_en": "Flipendo",
    "incantation": "Flipendo",
    "type": "utility",
    "category": "utility",
    "difficulty": 1,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo velmi podobné zaklínadlu Depulso. Také odhazuje předměty, slouží ale spíše pro prvňáky a druháky v Bradavicích. Flip znamená anglicky otočit, odhodit. Toto kouzlo se objevuje pouze v hrách na m...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"fugio": {
    "name_cs": "Fugio",
    "name_en": "Fugio",
    "incantation": "Fugio",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Věc zasažena kouzlem nabude schopnost létat. Používá se hlavně pro košťata nebo koberce....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"geminio": {
    "name_cs": "Geminio",
    "name_en": "Geminio",
    "incantation": "Geminio",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kopírovací kouzlo. V sedmém díle ho použila Hermiona na výrobu duplikátu medailonku Salazara Zmijozela. Také jím byl zaklet obsah trezoru Lestrangeových, a při každém dotyku se vytvořily kopie nerozpo...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"glacius": {
    "name_cs": "Glacius",
    "name_en": "Glacius",
    "incantation": "Glacius",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Zmrazovací kouzlo. Vytváří led ve směru hůlky. Ve třetím díle počítačové hry ho používal Harry a Hermiona. V latině glacies (s e, nikoli u) znamená led. Posílená verze Glacius Duo je použitelná v duel...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"glisseo": {
    "name_cs": "Glisseo",
    "name_en": "Glisseo",
    "incantation": "Glisseo",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Toto kouzlo je možné použít pouze na schodiště, které tím promění ve skluzavku. Účinek se dostaví okamžitě. (Použito Hermionou v 7. díle.) Tímto kouzlem bylo také začarováno schodiště do dívčích ložni...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"harmonia_nectere_passus": {
    "name_cs": "Harmonia Nectere Passus",
    "name_en": "Harmonia Nectere Passus",
    "incantation": "Harmonia Nectere Passus",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Použito v 6. díle, kdy Draco Malfoy využil rozplývavé skříně k průchodu smrtijedů do Bradavic....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"hasici_kouzlo": {
    "name_cs": "(Hasicí kouzlo)",
    "name_en": "(Hasicí kouzlo)",
    "incantation": "(Hasicí kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo způsobuje vyhasnutí ohně, na který je hůlka namířena....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"herbifors": {
    "name_cs": "Herbifors",
    "name_en": "Herbifors",
    "incantation": "Herbifors",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 8,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Kouzlo způsobující růst květin na těle (obzvláště hlavě) cíle....",
    "learning_time_hours": 40,
    "legality": "legal",
    "reputation_impact": -30
},

"herbivicus": {
    "name_cs": "Herbivicus",
    "name_en": "Herbivicus",
    "incantation": "Herbivicus",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo nutící rostliny okamžitě vyrůst....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"hnis_z_nosu": {
    "name_cs": "(Hnis z nosu)",
    "name_en": "(Hnis z nosu)",
    "incantation": "(Hnis z nosu)",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kouzlo způsobí, že oběti začne téct žlutý hnis z nosu....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"hodinove_kouzlo": {
    "name_cs": "(Hodinové kouzlo)",
    "name_en": "(Hodinové kouzlo)",
    "incantation": "(Hodinové kouzlo)",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Nestabilní a nebezpečné kouzlo umožňující kouzelníkovi vrátit se až pět hodin zpět v čase....",
    "learning_time_hours": 16,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"homenum_revelio": {
    "name_cs": "Homenum Revelio",
    "name_en": "Homenum Revelio",
    "incantation": "Homenum Revelio",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Průzkumní kouzlo, které opatří ujištění, není-li v domě či jiném prostoru kouzelník....",
    "learning_time_hours": 16,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"homorphovo_kouzlo": {
    "name_cs": "(Homorphovo kouzlo)",
    "name_en": "(Homorphovo kouzlo)",
    "incantation": "(Homorphovo kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Velmi složité kouzlo určené k přeměně Zvěromága, Vlkodlaka, či transfigurovaného objektu zpět do původního stavu....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"hop/vzhuru": {
    "name_cs": "Hop/Vzhůru",
    "name_en": "Hop/Vzhůru",
    "incantation": "Hop/Vzhůru",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo k zvednutí koštěte. V knize používáno jako zaklínadlo Vzhůru. Ve filmu Hop....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"horkovzdusne_kouzlo": {
    "name_cs": "(Horkovzdušné kouzlo)",
    "name_en": "(Horkovzdušné kouzlo)",
    "incantation": "(Horkovzdušné kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo vytvářející proud horkého vzduchu ze špičky hůlky....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"horton-keitchovo_brzdici_kouzlo": {
    "name_cs": "(Horton-Keitchovo brzdící kouzlo)",
    "name_en": "(Horton-Keitchovo brzdící kouzlo)",
    "incantation": "(Horton-Keitchovo brzdící kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo využívané společností Comet k tomu, aby jejich košťata velmi snadno zastavovala....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"hyacintus": {
    "name_cs": "Hyacintus",
    "name_en": "Hyacintus",
    "incantation": "Hyacintus",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Toto kouzlo je specialita Hermiony Grangerové. Vykouzlí voděodolné, modré plameny, které tepelně ovlivňují pouze objekty přímo nad plamenem. Plameny mohou být přenášeny ve sklenicích, či drženy v ruce...",
    "learning_time_hours": 16,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"illegibilus": {
    "name_cs": "Illegibilus",
    "name_en": "Illegibilus",
    "incantation": "Illegibilus",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo učiní psaný text nečitelným....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"impedimenta": {
    "name_cs": "Impedimenta",
    "name_en": "Impedimenta",
    "incantation": "Impedimenta",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kouzlo, které má zabránit pohybu cíle vůči kouzelníkovi. Může mít mnoho efektů, jako znehybnění, odhození, zpomalení, nebo i levitaci cíle. Formule znamená latinsky překážky....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"imperius": {
    "name_cs": "Imperius",
    "name_en": "Imperius",
    "incantation": "Imperius",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 10,
    "cooldown": 30,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Třetí z kleteb, které se nepromíjejí. Umožňuje absolutní ovládání oběti. Někteří lidé se silnou vůlí, jako například Harry Potter, se jí dokáží vzepřít. Samotná formule zní imperio, což latinský zname...",
    "learning_time_hours": 40,
    "legality": "unforgivable",
    "reputation_impact": -50
},

"infernum": {
    "name_cs": "Infernum",
    "name_en": "Infernum",
    "incantation": "Infernum",
    "type": "defensive",
    "category": "shield",
    "difficulty": 10,
    "cooldown": 5,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Kouzlo vytvářející mohutný kruh ohně kolem sesilatele pohybující se dle směru hůlky. Bylo použito Albusem Brumbálem v šestém díle proti neživým...",
    "learning_time_hours": 35,
    "legality": "legal",
    "reputation_impact": 0
},

"impervius": {
    "name_cs": "Impervius",
    "name_en": "Impervius",
    "incantation": "Impervius",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo učiní cíl odolný vůči kapalinám. Umožňuje tak například kouzelníkovi být v dešti a přesto nezmoknout viz Repellentus....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"inanimatus_conjurus": {
    "name_cs": "Inanimatus Conjurus",
    "name_en": "Inanimatus Conjurus",
    "incantation": "Inanimatus Conjurus",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo, které přeměňuje různé druhy živočichů na jiné....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"incendio": {
    "name_cs": "Incendio",
    "name_en": "Incendio",
    "incantation": "Incendio",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Zapálí nebo nechá vzplanout nějaký předmět. Incendo znamená latinsky zapaluji. Intenzivnější variace Incendio Duo a Incendio Tria umožňují přivolat zelený (Duo), či modrý (Tria) plamen o vyšší teplotě...",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"indicare": {
    "name_cs": "Indicare",
    "name_en": "Indicare",
    "incantation": "Indicare",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Po použití zaklínadla se hůlka začne chovat jako kompas – bude ukazovat sever....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"inflatus": {
    "name_cs": "Inflatus",
    "name_en": "Inflatus",
    "incantation": "Inflatus",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 8,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Nafoukne cíl. Je-li kouzlo použito s dostatečnou silou, cíl se nafoukne, vybuchne a uvolní tucty barevných balónků....",
    "learning_time_hours": 40,
    "legality": "forbidden",
    "reputation_impact": -30
},

"informus": {
    "name_cs": "Informus",
    "name_en": "Informus",
    "incantation": "Informus",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Po seslání na cílového tvora, či rostlinu přidá informace o něm do kouzelníkova Folio Bruti (bestiáře tvorů a rostlin)....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"jecici_kouzlo": {
    "name_cs": "(Ječící kouzlo)",
    "name_en": "(Ječící kouzlo)",
    "incantation": "(Ječící kouzlo)",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Kouzlo používané k ochraně určitého místa. Vstoupí-li na toto místo nepovolaná osoba, kouzlo začne vydávat hlasitý zvuk o vysoké tónině, aby na ni upozornilo....",
    "learning_time_hours": 16,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"jinx": {
    "name_cs": "Jinx",
    "name_en": "Jinx",
    "incantation": "Jinx",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Z hůlky vystřelí modrý paprsek...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"kaskadove_kouzlo": {
    "name_cs": "(Kaskádové kouzlo)",
    "name_en": "(Kaskádové kouzlo)",
    "incantation": "(Kaskádové kouzlo)",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kouzlo vytvoří explozi, která zasáhne mnoho cílů najednou....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"kletba_antonina_dolohova": {
    "name_cs": "(Kletba Antonina Dolohova)",
    "name_en": "(Kletba Antonina Dolohova)",
    "incantation": "(Kletba Antonina Dolohova)",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kletba používaná Antoninem Dolohovem. Svižným pohybem hůlky vyšle k cíli fialové plameny, které po zásahu způsobí vážná vnitřní zranění, či dokonce smrt....",
    "learning_time_hours": 20,
    "legality": "illegal",
    "reputation_impact": 0
},

"kletba_hermiony_grangerove": {
    "name_cs": "(Kletba Hermiony Grangerové)",
    "name_en": "(Kletba Hermiony Grangerové)",
    "incantation": "(Kletba Hermiony Grangerové)",
    "type": "utility",
    "category": "damage",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kouzlo, které Hermiona vytvořila speciálně pro Brumbálovu armádu. Pokud by nějaký člen tajnou skupinu zradil, vyraší mu na tváři boláky, které dohromady vytvoří slovo „práskač“ (SNEAK)....",
    "learning_time_hours": 20,
    "legality": "illegal",
    "reputation_impact": 0
},

"klihando": {
    "name_cs": "Klihando",
    "name_en": "Klihando",
    "incantation": "Klihando",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "po této kletbě se zasaženému přilepí jazyk k patru a postižený nemůže mluvit. Vynalezeno Princem dvojí krve (Severus Snape). Použita pouze v knize na Protivu. Viz Langlock....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"klopytaci_kletba": {
    "name_cs": "(Klopýtací kletba)",
    "name_en": "(Klopýtací kletba)",
    "incantation": "(Klopýtací kletba)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Vyčaruje neviditelnou překážku, o kterou zakopne každý, kdo jde kolem. Poprvé ji použil Draco Malfoy na Harryho, když Brumbálova armáda prchala před Umbridgeovou....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"kotlik_v_cednik": {
    "name_cs": "(Kotlík v cedník)",
    "name_en": "(Kotlík v cedník)",
    "incantation": "(Kotlík v cedník)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Transformační kouzlo, které přemění libovolný kotlík v cedník, čímž způsobí vylití tekutiny v kotlíku obsažené....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"kullomulium": {
    "name_cs": "Kullomulium",
    "name_en": "Kullomulium",
    "incantation": "Kullomulium",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kouzlo v podobě oranžového, či zeleného projektilu, které pronásleduje svůj cíl, dokud nenarazí na překážku, či na cíl samotný. Při nárazu způsobí podobné poškození jako Omračovací kouzlo....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"lacarnum_inflamari": {
    "name_cs": "Lacarnum Inflamari",
    "name_en": "Lacarnum Inflamari",
    "incantation": "Lacarnum Inflamari",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Podpalovací kouzlo. Toto kouzlo bylo použito Hermionou Grangerovou v prvním dílu, když podpálila Snapeovi plášť při Famfrpálu....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"lapifors": {
    "name_cs": "Lapifors",
    "name_en": "Lapifors",
    "incantation": "Lapifors",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo růžové barvy přemění cíl v zajíce, či králíka....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"legilimens": {
    "name_cs": "Legilimens",
    "name_en": "Legilimens",
    "incantation": "Legilimens",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 8,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Umožňuje kouzelníkovi či čarodějce proniknout do mysli druhého člověka (oběti). Poprvé jsme ho mohli vidět v pátém díle, při hodinách nitrobrany, ale ve znění lakerimé. Legere je latinsky číst a mens ...",
    "learning_time_hours": 40,
    "legality": "legal_combat",
    "reputation_impact": -30
},

"levicorpus": {
    "name_cs": "Levicorpus",
    "name_en": "Levicorpus",
    "incantation": "Levicorpus",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kletba, která způsobí, že postižený visí za kotník hlavou dolů ve vzduchu a lze ho přemisťovat, dokud na něj není použita protikletba Liberacorpus. Vynalezl ji Princ dvojí krve jako neverbální zaklína...",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"liberacorpus": {
    "name_cs": "Liberacorpus",
    "name_en": "Liberacorpus",
    "incantation": "Liberacorpus",
    "type": "defensive",
    "category": "shield",
    "difficulty": 5,
    "cooldown": 5,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Protikletba ke kletbě Levicorpus, vynalezl ji též Princ dvojí krve. Liberare je latinsky uvolňovat, osvobozovat a corpus je tělo....",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"locomotor": {
    "name_cs": "Locomotor",
    "name_en": "Locomotor",
    "incantation": "Locomotor",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo o mnoho silnější než Wingardium leviosa, neboť dokáže zvedat a přenášet i živé tvory. Při seslání je nutno říct jméno cíle, například „locomotor kufr“....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"locomotor_mortis": {
    "name_cs": "Locomotor Mortis",
    "name_en": "Locomotor Mortis",
    "incantation": "Locomotor Mortis",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Svěrací kouzlo. V prvním díle si ho zkoušel Malfoy na Nevillovi a ten pak měl spoutané nohy k sobě a mohl jenom snožmo skákat a to samé kouzlo se naučili Ron s Hermionou, aby mohli zneškodnit Snapea, ...",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"locomotor_wibbly": {
    "name_cs": "Locomotor Wibbly",
    "name_en": "Locomotor Wibbly",
    "incantation": "Locomotor Wibbly",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Záblesk červeného světla vyvolá slabost v nohách cíle a způsobí, že spadne. Kouzlo je taky známo jako Kletba želatinových nohou....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"lumos": {
    "name_cs": "Lumos",
    "name_en": "Lumos",
    "incantation": "Lumos",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Rozsvítí světlo na špičce hůlky. Světlo také trochu zahřívá. Použil ho Harry Potter v Tajemné komnatě. Opačné kouzlo je Nox, které světlo zase zhasne. Latinsky lumen je světlo. Vynalezeno Levinou Monk...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"lumos_maxima": {
    "name_cs": "Lumos Maxima",
    "name_en": "Lumos Maxima",
    "incantation": "Lumos Maxima",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo vytvářející oslňující světlo na špičce hůlky, které může být vrženo v podobě létající svítící koule, která osvětluje okolí....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"lumos_solem": {
    "name_cs": "Lumos Solem",
    "name_en": "Lumos Solem",
    "incantation": "Lumos Solem",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo vytvářející oslnivý proud slunečního světla ze špičky hůlky. Použila ho Hermiona v prvním díle, když pomáhala Ronovi z Ďáblova osidla (pouze ve filmu)....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"lumos_duo": {
    "name_cs": "Lumos Duo",
    "name_en": "Lumos Duo",
    "incantation": "Lumos Duo",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Tato modernější verze kouzla Lumos, způsobí, že ze špičky hůlky vyzařuje extrémně jasný a intenzivní paprsek světla, který může být použit pro různé účely. Svítí v bílé barvě, což je rozdíl od ostatní...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"magicus_extremos": {
    "name_cs": "Magicus Extremos",
    "name_en": "Magicus Extremos",
    "incantation": "Magicus Extremos",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo umožní kouzelníkovi po krátkou dobu sesílat mnohem silnější kouzla....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"melofors": {
    "name_cs": "Melofors",
    "name_en": "Melofors",
    "incantation": "Melofors",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Kouzlo zasáhne oranžovým paprskem oběť a uzavře její hlavu v dýni....",
    "learning_time_hours": 16,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"meteolojinx_recanto": {
    "name_cs": "Meteolojinx Recanto",
    "name_en": "Meteolojinx Recanto",
    "incantation": "Meteolojinx Recanto",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Toto kouzlo poradil Arthur Weasley Reginaldu Cattermolovi, zaměstnanci Ministerstva kouzel, na odstranění kletby způsobující déšť v místnosti. Netušil, že to nebyl Reginald, ale jeho syn Ron zamaskova...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"mimblewimble": {
    "name_cs": "Mimblewimble",
    "name_en": "Mimblewimble",
    "incantation": "Mimblewimble",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Kouzlo způsobí, že se jazyk oběti doslova zamotá a zabrání tak například vyzrazení určitého tajemství....",
    "learning_time_hours": 16,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"mdloby_na_tebe": {
    "name_cs": "Mdloby na tebe",
    "name_en": "Mdloby na tebe",
    "incantation": "Mdloby na tebe",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Případně „Mdloby na vás“. Omračovací kouzlo. V anglickém originále používáno jako zaklínadlo Stupefy....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"mobiliarbus": {
    "name_cs": "Mobiliarbus",
    "name_en": "Mobiliarbus",
    "incantation": "Mobiliarbus",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo určené k levitaci rostlin....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"mobilicorpus": {
    "name_cs": "Mobilicorpus",
    "name_en": "Mobilicorpus",
    "incantation": "Mobilicorpus",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo určené k levitaci živých tvorů....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"molliare": {
    "name_cs": "Molliare",
    "name_en": "Molliare",
    "incantation": "Molliare",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Je to změkčovací kouzlo....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"morsmorse": {
    "name_cs": "Morsmorse",
    "name_en": "Morsmorse",
    "incantation": "Morsmorse",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 8,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Vykouzlí znamení zla. Používali jej Smrtijedi na označení místa, kde provedli nějaký zločin, nejčastěji vraždu. Poprvé jsme ji viděli ve 4. díle, kdy viděl Harry Bartyho Skrka Juniora. Mors je latinsk...",
    "learning_time_hours": 40,
    "legality": "forbidden",
    "reputation_impact": -30
},

"mucus_ad_nauseam": {
    "name_cs": "Mucus ad Nauseam",
    "name_en": "Mucus ad Nauseam",
    "incantation": "Mucus ad Nauseam",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 8,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "ceským překladem Hlen až do zhloupnutí, známá též jako Kletba nudlí. Po zásahu zeleného světla způsobí vážné nachlazení, rýmu a extrémní zahlenění nosu....",
    "learning_time_hours": 40,
    "legality": "legal",
    "reputation_impact": -30
},

"multicorfors": {
    "name_cs": "Multicorfors",
    "name_en": "Multicorfors",
    "incantation": "Multicorfors",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo umožňující kouzelníkovi změnit barvu oblečení cíle....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"naplnovaci_kouzlo": {
    "name_cs": "(Naplňovací kouzlo)",
    "name_en": "(Naplňovací kouzlo)",
    "incantation": "(Naplňovací kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Znovu naplní nádobu tekutinou, která v nádobě byla před vyprázdněním....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"nehtove_kouzlo": {
    "name_cs": "(Nehtové kouzlo)",
    "name_en": "(Nehtové kouzlo)",
    "incantation": "(Nehtové kouzlo)",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Způsobí, že nehty na nohou oběti začnou růst vysokou rychlostí....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"nepalivy_ohen": {
    "name_cs": "(Nepálivý oheň)",
    "name_en": "(Nepálivý oheň)",
    "incantation": "(Nepálivý oheň)",
    "type": "defensive",
    "category": "shield",
    "difficulty": 5,
    "cooldown": 5,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Kouzlo očaruje oheň, aby při kontaktu nepálil, ale šimral. Čarodějka Wendelina se tímto kouzlem proslavila, když byla 47krát neúspěšně upálena....",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"neporusitelny_slib": {
    "name_cs": "(Neporušitelný slib)",
    "name_en": "(Neporušitelný slib)",
    "incantation": "(Neporušitelný slib)",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 8,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Kouzlo neznámého zaklínání, které uzavře přísahu mezi dvěma kouzelníky. Je-li slib porušen jedním z nich, ten, jenž ji porušil, zemře. Byl použit v 6. díle na Severuse Snapea, který kvůli němu musel z...",
    "learning_time_hours": 40,
    "legality": "legal",
    "reputation_impact": 0
},

"neproniknutelne_kouzlo": {
    "name_cs": "(Neproniknutelné kouzlo)",
    "name_en": "(Neproniknutelné kouzlo)",
    "incantation": "(Neproniknutelné kouzlo)",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Kouzlo očaruje objekt (například dveře), čímž je učiní neproniknutelné a zvukotěsné....",
    "learning_time_hours": 16,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"nerozbitne_kouzlo": {
    "name_cs": "(Nerozbitné kouzlo)",
    "name_en": "(Nerozbitné kouzlo)",
    "incantation": "(Nerozbitné kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo učiní libovolný objekt nerozbitným....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"nox": {
    "name_cs": "Nox",
    "name_en": "Nox",
    "incantation": "Nox",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Zhasne světlo vyčarované kouzlem Lumos. Nox znamená latinsky noc....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"obracena_kolena": {
    "name_cs": "(Obrácená kolena)",
    "name_en": "(Obrácená kolena)",
    "incantation": "(Obrácená kolena)",
    "type": "defensive",
    "category": "shield",
    "difficulty": 5,
    "cooldown": 5,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Kouzlo způsobující, že se kolena oběti obrátí na opačnou stranu, stejně jako chodidla....",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"obscuro": {
    "name_cs": "Obscuro",
    "name_en": "Obscuro",
    "incantation": "Obscuro",
    "type": "defensive",
    "category": "shield",
    "difficulty": 5,
    "cooldown": 5,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Kouzlo zakryje páskou oči cíle. Hodí se do duelů na rozptýlení....",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"ocullus_reparo": {
    "name_cs": "Ocullus reparo",
    "name_en": "Ocullus reparo",
    "incantation": "Ocullus reparo",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Varianta kouzla Reparo. Kouzlo, které bylo použito na opravu Harryho brýlí....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"oko_norka,_harfy_sum,_promen_vodu_v_dobry_rum": {
    "name_cs": "Oko norka, harfy šum, proměn vodu v dobrý rum",
    "name_en": "Oko norka, harfy šum, proměn vodu v dobrý rum",
    "incantation": "Oko norka, harfy šum, proměn vodu v dobrý rum",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo se v prvním díle pokusil použít Seamus Finnigan, aby proměnil vodu v rum. Místo toho mu kouzlo vybuchlo do obličeje a Ron Harrymu řekl, že se mu to minule podařilo proměnit ve slabý čaj. Anglic...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"opisovaci_kouzlo": {
    "name_cs": "(Opisovací kouzlo)",
    "name_en": "(Opisovací kouzlo)",
    "incantation": "(Opisovací kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo neznámým způsobem pomáhá kouzelníkovi v podvádění při písemných zkouškách....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"oppugno": {
    "name_cs": "Oppugno",
    "name_en": "Oppugno",
    "incantation": "Oppugno",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Použito v šestém díle. Hermiona tak poštvala hejno ptáčků vyčarovaných kouzlem Avis proti Ronu Weasleymu. Formule je z latiny a znamená bojuji....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"orbis": {
    "name_cs": "Orbis",
    "name_en": "Orbis",
    "incantation": "Orbis",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kouzlo použitelné pouze pokud je cíl ve vzduchu. Obklopí jej vírem modrého světla a zaboří jej do země....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"orchideous": {
    "name_cs": "Orchideous",
    "name_en": "Orchideous",
    "incantation": "Orchideous",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo vytvoří květiny na místě, kam ukazuje hůlka. Může být také použito k přeměně cíle v květiny. Použil ho výrobce hůlek Ollivander při kontrole hůlky Fleur Delacour ve 4. díle (pouze v knize). Pot...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"osrstovaci_kouzlo": {
    "name_cs": "(Osrsťovací kouzlo)",
    "name_en": "(Osrsťovací kouzlo)",
    "incantation": "(Osrsťovací kouzlo)",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kouzlo způsobující náhlý růst srsti na těle cíle....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"partis_temporus": {
    "name_cs": "Partis Temporus",
    "name_en": "Partis Temporus",
    "incantation": "Partis Temporus",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo vytvoří mezeru v cíli. Kouzlo pravděpodobně nefunguje na pevné objekty. Je ale použitelné na magické bariéry a (ve všech případech použití) oheň. Použito Brumbálem v šestém díle během úniku z j...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"patentovane_kouzlo_denniho_sneni": {
    "name_cs": "(Patentované kouzlo denního snění)",
    "name_en": "(Patentované kouzlo denního snění)",
    "incantation": "(Patentované kouzlo denního snění)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo umožňuje cíli mít až 30minutový, vysoce realistický sen. Kouzlo bylo pravděpodobně vytvořeno bratry Fredem a Georgem Weasleyovými....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"perfendi": {
    "name_cs": "Perfendi",
    "name_en": "Perfendi",
    "incantation": "Perfendi",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo k uzamčení dveří....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"pede_labetur": {
    "name_cs": "Pede Labetur",
    "name_en": "Pede Labetur",
    "incantation": "Pede Labetur",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Zakopávací formule....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"perrikulus_periculum": {
    "name_cs": "Perrikulus (Periculum)",
    "name_en": "Perrikulus (Periculum)",
    "incantation": "Perrikulus (Periculum)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Při použití vyletí z hůlky červená světlice. Použito ve 4. díle ve třetím úkolu. Latinské Periculum znamená nebezpečí. Zde bráno jako „Jsem v nebezpečí, žádám o pomoc“....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"permanentni_lepici_kouzlo": {
    "name_cs": "Permanentní lepicí kouzlo)",
    "name_en": "Permanentní lepicí kouzlo)",
    "incantation": "Permanentní lepicí kouzlo)",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Silné kouzlo způsobující, že cíl se přilepí k povrchu jiného a je následně prakticky nemožné je oddělit....",
    "learning_time_hours": 16,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"perickove_kouzlo": {
    "name_cs": "(Peříčkové kouzlo)",
    "name_en": "(Peříčkové kouzlo)",
    "incantation": "(Peříčkové kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo zlehčující cílový objekt....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"peskipiksi_pesternomi": {
    "name_cs": "Peskipiksi Pesternomi",
    "name_en": "Peskipiksi Pesternomi",
    "incantation": "Peskipiksi Pesternomi",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "V českém překladu Peskirarach Pesternomi. Ve druhém díle jej použil Zlatoslav Lockhart na cornwallské rarachy, ale nic se nestalo. Není známo, zda má kouzlo vůbec nějaký účinek....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"petardove_kouzlo": {
    "name_cs": "(Petardové kouzlo)",
    "name_en": "(Petardové kouzlo)",
    "incantation": "(Petardové kouzlo)",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Kouzlo, které vyčaruje kouzelnické petardy. Je účinné v duelech, ale může poranit i sesilatele....",
    "learning_time_hours": 16,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"petrificus_totalus": {
    "name_cs": "Petrificus Totalus",
    "name_en": "Petrificus Totalus",
    "incantation": "Petrificus Totalus",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kouzlo úplného spoutání, oběť může hýbat jen očima. Hermiona ho použila proti Nevillu Longbottomovi, který chtěl trojici bránit, když v noci opouštěla kolej. Malfoy ho použil proti Harrymu v šestém dí...",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"piertotum_locomotor": {
    "name_cs": "Piertotum Locomotor",
    "name_en": "Piertotum Locomotor",
    "incantation": "Piertotum Locomotor",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Tímto kouzlem profesorka Minerva McGonagallová v sedmém díle oživí bradavické sochy, aby pomohly s obranou hradu. Latinské slovo petra (z čehož je odvozené italské jméno Pier a české Petr) znamená ská...",
    "learning_time_hours": 16,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"polstrovaci_kouzlo": {
    "name_cs": "(Polstrovací kouzlo)",
    "name_en": "(Polstrovací kouzlo)",
    "incantation": "(Polstrovací kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo neviditelně změkčí cílový povrch. Je často využívané při výrobě košťat....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"porkove_kouzlo": {
    "name_cs": "(Pórkové kouzlo)",
    "name_en": "(Pórkové kouzlo)",
    "incantation": "(Pórkové kouzlo)",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Způsobí, že cíli z uší začnou růst pórky....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"portus": {
    "name_cs": "Portus",
    "name_en": "Portus",
    "incantation": "Portus",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo, které přemění jakýkoliv předmět v přenášedlo. Poprvé ho použil Albus Brumbál v pátém díle v ředitelově pracovně, po vidění napadení Artura Weaslyho hadem Naginim při plnění úkolu pro Fénixův ř...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"pouta_na_tebe": {
    "name_cs": "Pouta na tebe",
    "name_en": "Pouta na tebe",
    "incantation": "Pouta na tebe",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Případně „Pouta na vás“. Poutací kouzlo. V anglickém originále používáno jako zaklínadlo Incarcerous. Protikouzlo na zrušení pout: Diffindo...",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"priori_incantatem": {
    "name_cs": "Priori Incantatem",
    "name_en": "Priori Incantatem",
    "incantation": "Priori Incantatem",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Odhalí předchozí kouzla, která byla hůlkou provedena. V Ohnivém poháru je takto odhaleno, že znamení zla bylo vykouzleno Harryho hůlkou. Prior je v latině „dřívější, předešlý“ a incantatum znamená „za...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"prohazovaci_kouzlo": {
    "name_cs": "(Prohazovací kouzlo)",
    "name_en": "(Prohazovací kouzlo)",
    "incantation": "(Prohazovací kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo prohodí pozice dvou objektů....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"promenlive_spojeni": {
    "name_cs": "(Proměnlivé spojení)",
    "name_en": "(Proměnlivé spojení)",
    "incantation": "(Proměnlivé spojení)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo vytvoří spojení mezi dvěma objekty. Jakkoliv se změní jeden (je do něj něco vyryto, či je přeměněn), změní se přesně tak i ten druhý. Kouzlo bylo využíváno na mince Brumbálovy armády....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"protego": {
    "name_cs": "Protego",
    "name_en": "Protego",
    "incantation": "Protego",
    "type": "defensive",
    "category": "shield",
    "difficulty": 5,
    "cooldown": 5,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Štítové kouzlo. Je-li dost silné, může protivníka i odhodit. V pátém díle jej použije Harry proti Snapeovi, když s ním cvičí nitrobranu. Protego dokáže odvrátit většinu zaklínadel i fyzických útoků, n...",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"protego_diabolica": {
    "name_cs": "Protego Diabolica",
    "name_en": "Protego Diabolica",
    "incantation": "Protego Diabolica",
    "type": "defensive",
    "category": "shield",
    "difficulty": 10,
    "cooldown": 5,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "extrémně mocné, složité a nebezpečné ochranné kouzlo černé magie (poprvé použité Gellertem Grindelwaldem filmu ve Fantastická zvířata: Grindelwaldovy zločiny). Vytváří kolem sesilatele kruh modrého oh...",
    "learning_time_hours": 45,
    "legality": "legal",
    "reputation_impact": 0
},

"protego_maxima": {
    "name_cs": "Protego Maxima",
    "name_en": "Protego Maxima",
    "incantation": "Protego Maxima",
    "type": "defensive",
    "category": "shield",
    "difficulty": 5,
    "cooldown": 5,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Kouzlo vytvoří mnohem větší a časově stálý štít na ochranu velkého území....",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"protego_totalum": {
    "name_cs": "Protego Totalum",
    "name_en": "Protego Totalum",
    "incantation": "Protego Totalum",
    "type": "defensive",
    "category": "shield",
    "difficulty": 8,
    "cooldown": 1,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Silnější varianta Štítového kouzla, která ochrání menší území po delší časový úsek před vetřelci. V sedmém díle Hermiona používá Protego totalum k ochraně jejich tábora....",
    "learning_time_hours": 20,
    "legality": "legal",
    "reputation_impact": 0
},

"protego_horribilis": {
    "name_cs": "Protego Horribilis",
    "name_en": "Protego Horribilis",
    "incantation": "Protego Horribilis",
    "type": "defensive",
    "category": "shield",
    "difficulty": 5,
    "cooldown": 5,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Silnější Štítové kouzlo určené pro obranu velkého území proti černé magii. Profesor Filius Kratiknot během bitvy o Bradavice použil Protego horribilis....",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"protego_inimisium": {
    "name_cs": "Protego Inimisium",
    "name_en": "Protego Inimisium",
    "incantation": "Protego Inimisium",
    "type": "defensive",
    "category": "shield",
    "difficulty": 5,
    "cooldown": 5,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Kouzla užita proti vám, se vsáknou do špičky hůlky. Funguje dokonce na smrtící kletbu. Kouzlo, které bylo užito proti vám, můžete poslat zpět protivníkovi....",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"proti-podvadeci_kouzlo": {
    "name_cs": "(Proti-podváděcí kouzlo)",
    "name_en": "(Proti-podváděcí kouzlo)",
    "incantation": "(Proti-podváděcí kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "začaruje psací potřebu, například brk, aby ten, kdo ho používá, nemohl podvádět. Používalo se během zkoušek v Bradavicích....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"pulirexo": {
    "name_cs": "Pulírexo",
    "name_en": "Pulírexo",
    "incantation": "Pulírexo",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Čisticí kouzlo. Bylo použito v pátém díle knihy Nymfadorou Tonksovou k vyčištění Hedvičiny klece. V anglickém originálu zní Scourgify....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"quietus": {
    "name_cs": "Quietus",
    "name_en": "Quietus",
    "incantation": "Quietus",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo pro ztlumení hlasu na původní sílu (protikouzlo ke kouzlu Sonorus). V latině znamená tichý....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"redactum_skullus": {
    "name_cs": "Redactum Skullus",
    "name_en": "Redactum Skullus",
    "incantation": "Redactum Skullus",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo zmenšující hlavu cíle. Je to také protikouzlo proti Engorgio Skullus....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"reducio": {
    "name_cs": "Reducio",
    "name_en": "Reducio",
    "incantation": "Reducio",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Způsobuje zmenšení předmětu. Pokud je kouzlo použito jako protikouzlo ke kouzlu Engorgio, předmět se zmenší na původní velikost....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"reducto": {
    "name_cs": "Reducto",
    "name_en": "Reducto",
    "incantation": "Reducto",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Ničící kouzlo. Kouzlo ve filmu po dopadnutí na živou bytost vytvoří tlakovou vlnu. Po dopadu na předmět ho rozbije nebo rozpráší. Ve čtvrtém díle bylo použito Harrym v bludišti při záchraně Cedrica ze...",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"relashio": {
    "name_cs": "Relashio",
    "name_en": "Relashio",
    "incantation": "Relashio",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "kouzlo donutí jakýkoliv objekt, či osobu, aby uvolnila sevření jiného objektu, či osoby, nebo od sebe dva cíle silou rozdělí. Pod vodou toto kouzlo vytvoří proud vařící vody. Ve čtvrtém díle jej Harry...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"reparo": {
    "name_cs": "Reparo",
    "name_en": "Reparo",
    "incantation": "Reparo",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Opravovací kouzlo. Reparo znamená latinsky „obnovit“. Ve filmové podobě použila Hermiona variantu Ocullus Reparo, aby Harrymu opravila brýle....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"reparifarge": {
    "name_cs": "Reparifarge",
    "name_en": "Reparifarge",
    "incantation": "Reparifarge",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo určené k navracení transfigurovaných objektů zpět do původního stavu....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"reparifors": {
    "name_cs": "Reparifors",
    "name_en": "Reparifors",
    "incantation": "Reparifors",
    "type": "healing",
    "category": "healing",
    "difficulty": 5,
    "cooldown": 12,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "healing",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "green",
        "sound": "heal",
        "projectile": False
    },
    "description": "Kouzlo zahojí škody způsobené kouzly, jako paralýzu, či otrávení....",
    "learning_time_hours": 18,
    "legality": "legal",
    "reputation_impact": 5
},

"repellentus": {
    "name_cs": "Repellentus",
    "name_en": "Repellentus",
    "incantation": "Repellentus",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo odpuzující vodu a další tekutiny. Použito Hermionou Grangerovou (jen v knize) na brýle Harryho Pottera při famfrpálovém zápasu....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"repello_inimicum": {
    "name_cs": "Repello Inimicum",
    "name_en": "Repello Inimicum",
    "incantation": "Repello Inimicum",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Odpuzuje nepřátele. Často se používá v kombinaci s protego maxima a fianto duri. Bylo použito v sedmém díle při budování magického štítu na ochranu Bradavic....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"repello_mudletum": {
    "name_cs": "Repello mudletum",
    "name_en": "Repello mudletum",
    "incantation": "Repello mudletum",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Udržuje mudly od místa, které bylo tímto kouzlem zabezpečeno. Hermiona ho používala v sedmém díle k zabezpečení místa, kde stanovali, a ve velkém bylo použito na mistrovství světa ve famfrpálu....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"repleo": {
    "name_cs": "Repleo",
    "name_en": "Repleo",
    "incantation": "Repleo",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Prázdná nádoba se naplní tekutinou, která se v ní nacházela původně....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"revelio": {
    "name_cs": "Revelio",
    "name_en": "Revelio",
    "incantation": "Revelio",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Odhalující kouzlo. Revelatio je latinsky odhalení. Varianta Specialis revelio odhaluje, je-li daný předmět kouzelný. V šestém díle ho Hermiona použila na Harryho učebnici Přípravy lektvarů pro pokroči...",
    "learning_time_hours": 16,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"revertis_fortis": {
    "name_cs": "Revertis fortis",
    "name_en": "Revertis fortis",
    "incantation": "Revertis fortis",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Odhodí soupeře do dálky....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"rictusempra": {
    "name_cs": "Rictusempra",
    "name_en": "Rictusempra",
    "incantation": "Rictusempra",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Lechtací kletba. Harry ji použil ve druhém díle v soubojnickém klubu proti Dracu Malfoyovi a ten poté lehl na zem a svíjel se v křečích smíchem. Latinsky rictus znamená ústa a semper je stále....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"riddikulus": {
    "name_cs": "Riddikulus",
    "name_en": "Riddikulus",
    "incantation": "Riddikulus",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Zesměšní cíl kouzla, používá se proto k zahnání bubáka. Bubák je tvor živící se strachem, bere proto na sebe podobu, která podle něj oběť co nejvíce vyděsí a když člověka zastihne nepřipraveného, může...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"salvio_hexia": {
    "name_cs": "Salvio Hexia",
    "name_en": "Salvio Hexia",
    "incantation": "Salvio Hexia",
    "type": "defensive",
    "category": "shield",
    "difficulty": 5,
    "cooldown": 5,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "shield",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "blue",
        "sound": "shield_up",
        "projectile": False
    },
    "description": "Ochranné kouzlo, Hermiona ho v sedmém díle používala k zabezpečení místa, kde stanovali. Patrně je to splývací kouzlo na dané místo....",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 0
},

"sardinkove_kouzlo": {
    "name_cs": "(Sardinkové kouzlo)",
    "name_en": "(Sardinkové kouzlo)",
    "incantation": "(Sardinkové kouzlo)",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Způsobí, že z nosu oběti vypadávají sardinky....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"stupefy": {
    "name_cs": "Stupefy",
    "name_en": "Stupefy",
    "incantation": "Stupefy",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Způsobí omráčení protivníka....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"sectumsempra": {
    "name_cs": "Sectumsempra",
    "name_en": "Sectumsempra",
    "incantation": "Sectumsempra",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Řezací kouzlo. Kletba zasaženého sekne jako neviditelný meč. V šestém díle ji Harry objevil ve staré učebnici lektvarů po Princi dvojí krve (Severus Snape, který ho vynalezl) a pak, nevěda, co kouzlo ...",
    "learning_time_hours": 20,
    "legality": "illegal",
    "reputation_impact": 0
},

"serpensortia": {
    "name_cs": "Serpensortia",
    "name_en": "Serpensortia",
    "incantation": "Serpensortia",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Vykouzlí hada – serpente je z latiny a značí hada. Anglicky sortie znamená let nebo výpad. Na radu Severuse Snapea ho ve druhém díle knihy v soubojnickém klubu použil Draco Malfoy na Harryho Pottera. ...",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"shazovaci_kouzlo": {
    "name_cs": "(Shazovací kouzlo)",
    "name_en": "(Shazovací kouzlo)",
    "incantation": "(Shazovací kouzlo)",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Očaruje koště a způsobí, že koště shodí svého jezdce při nejbližší příležitosti....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"silencio": {
    "name_cs": "Silencio",
    "name_en": "Silencio",
    "incantation": "Silencio",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Tišící kouzlo. Člověk nemůže mluvit, i když otevírá ústa. Formule znamená španělsky ticho....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"skurge": {
    "name_cs": "Skurge",
    "name_en": "Skurge",
    "incantation": "Skurge",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo použité pro vyčištění ektoplazmy, podivného materiálu, který za sebou zanechávají někteří duchové. Kouzlo při seslání vytváří mydliny....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"slugus_eructo": {
    "name_cs": "Slugus Eructo",
    "name_en": "Slugus Eructo",
    "incantation": "Slugus Eructo",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Paprsek zeleného světla zasáhne oběť, která pak následujících deset minut zvrací slimáky. Použil ho Ron Weasley ve druhém díle na Draca Malfoye. Ron měl však zlomenou hůlku a kouzlo se obrátilo proti ...",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"solidatur": {
    "name_cs": "Solidatur",
    "name_en": "Solidatur",
    "incantation": "Solidatur",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 8,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Kletba vytvoří kolem oběti kolo rampouchů a nakonec nechá oběť zamrznout do velkého rampouchu který se oběti vynoří pod nohama. Následně oběti zamrzne celé tělo. Kletba jde zrušit pouze jakýmkoliv drt...",
    "learning_time_hours": 40,
    "legality": "forbidden",
    "reputation_impact": -30
},

"somnium": {
    "name_cs": "Somnium",
    "name_en": "Somnium",
    "incantation": "Somnium",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Osoba zasažena kletbou upadá do půlhodinového spánku, při kterém se mu zdá realisticky působící sen. Má prázdný výraz a může u toho i slintat....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"somnium_duo": {
    "name_cs": "Somnium duo",
    "name_en": "Somnium duo",
    "incantation": "Somnium duo",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kouzelník zasažen kletbou upadá do spánku s tím, kdo vyslal kouzlo. Spánek může ukončit ten, co formuli pronesl. Sdílejí spolu svět, ve kterém se v jejich okolí stane vše, na co pomyslí....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"sonorus": {
    "name_cs": "Sonorus",
    "name_en": "Sonorus",
    "incantation": "Sonorus",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo, po kterém se stává hlas hlasitější. Kouzlo může být také použito k projekci ohlušujícího řevu z hůlky. Formule je z latiny a znamená hlasitý. Používal ho například Ludo Pytloun při komentování...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"spalovaci_kouzlo": {
    "name_cs": "(Spalovací kouzlo)",
    "name_en": "(Spalovací kouzlo)",
    "incantation": "(Spalovací kouzlo)",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kouzlo vytvářející tancující plameny s účelem spálit cíl. Bylo použito v sedmém díle Minervou McGonagallovou....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"spongify": {
    "name_cs": "Spongify",
    "name_en": "Spongify",
    "incantation": "Spongify",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo udělá cíl měkčím a naducanějším....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"steleus": {
    "name_cs": "Steleus",
    "name_en": "Steleus",
    "incantation": "Steleus",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo způsobí, že oběť musí po krátký čas neustále kýchat. Je oblíbené v duelech pro rozptýlení soupeře. Kouzlo je sesláno v podobě střely zelených kruhů....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"supersenzoricke_kouzlo": {
    "name_cs": "(Supersenzorické kouzlo)",
    "name_en": "(Supersenzorické kouzlo)",
    "incantation": "(Supersenzorické kouzlo)",
    "type": "healing",
    "category": "healing",
    "difficulty": 5,
    "cooldown": 12,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "healing",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "green",
        "sound": "heal",
        "projectile": False
    },
    "description": "Kouzlo zlepší smysly sesilatele....",
    "learning_time_hours": 18,
    "legality": "legal",
    "reputation_impact": 5
},

"sevelissimo": {
    "name_cs": "Ševelissimo",
    "name_en": "Ševelissimo",
    "incantation": "Ševelissimo",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Všem nežádoucím osobám v okolí zaplňuje uši nevysledovatelným šumem, takže je možné mluvit bez obav, že budete zaslechnuti. Toto kouzlo bylo vynalezeno Princem dvojí krve (Severusem Snapem) a poprvé s...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"sipove_kouzlo": {
    "name_cs": "(Šípové kouzlo)",
    "name_en": "(Šípové kouzlo)",
    "incantation": "(Šípové kouzlo)",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kouzlo vystřelí z hůlky šíp. Toto kouzlo je oblíbené u Applebyjských Šípů, jeho použití ve famfrpálu bylo však zakázáno Ústředím Britské a Irské Famfrpálové Ligy....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"tabu": {
    "name_cs": "(Tabu)",
    "name_en": "(Tabu)",
    "incantation": "(Tabu)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo seslané na určité slovo. Je-li toto slovo vyřčeno, sesilatel Tabu se okamžitě dozví, kdo slovo vyřkl a kde bylo vyřknuto....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"tarantallegra": {
    "name_cs": "Tarantallegra",
    "name_en": "Tarantallegra",
    "incantation": "Tarantallegra",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kouzlo, které přinutí protivníka stepovat. Tarantella je italský tanec a allegro je v hudbě výraz pro rychle. Použil ho v soubojnickém klubu Draco Malfoy na Harryho Pottera....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"teleportacni_kouzlo": {
    "name_cs": "(Teleportační kouzlo)",
    "name_en": "(Teleportační kouzlo)",
    "incantation": "(Teleportační kouzlo)",
    "type": "control",
    "category": "binding",
    "difficulty": 5,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "binding",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "purple",
        "sound": "bind",
        "projectile": True
    },
    "description": "Přenese objekt na jiné místo....",
    "learning_time_hours": 16,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"tentaclifors": {
    "name_cs": "Tentaclifors",
    "name_en": "Tentaclifors",
    "incantation": "Tentaclifors",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo přemění hlavu cíle v chapadlo. Není známo, zdali v této podobě může cíl dýchat....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"tergeo": {
    "name_cs": "Tergeo",
    "name_en": "Tergeo",
    "incantation": "Tergeo",
    "type": "healing",
    "category": "healing",
    "difficulty": 5,
    "cooldown": 12,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "healing",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "green",
        "sound": "heal",
        "projectile": False
    },
    "description": "Na začátku šestého dílu použila Hermiona toto kouzlo, aby Harrymu smyla krev z obličeje. Formule znamená latinsky čistím....",
    "learning_time_hours": 18,
    "legality": "legal",
    "reputation_impact": 5
},

"titillando": {
    "name_cs": "Titillando",
    "name_en": "Titillando",
    "incantation": "Titillando",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Lechtací kouzlo. Zasažený se svíjí smíchy, dokud někdo kletbu nezruší....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"transmogrificke_muceni": {
    "name_cs": "(Transmogrifické mučení)",
    "name_en": "(Transmogrifické mučení)",
    "incantation": "(Transmogrifické mučení)",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 8,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Kouzlo neznámým způsobem mučí a zabije oběť....",
    "learning_time_hours": 40,
    "legality": "forbidden",
    "reputation_impact": -30
},

"usi_v_kumquat": {
    "name_cs": "Uši v kumquat",
    "name_en": "Uši v kumquat",
    "incantation": "Uši v kumquat",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo, které má údajně přeměnit uši cíle v tropické ovoce kumquat....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"ukaz_mi_cestu": {
    "name_cs": "Ukaž mi cestu",
    "name_en": "Ukaž mi cestu",
    "incantation": "Ukaž mi cestu",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Hůlka se po pronesení těchto slov natočí směrem k severu. Toto kouzlo bylo použito v knize Harry Potter a Ohnivý pohár při třetím úkolu Turnaje tří kouzelníků a je jedním z mála kouzel pojmenovaných v...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"uchopove_kouzlo": {
    "name_cs": "(Úchopové kouzlo)",
    "name_en": "(Úchopové kouzlo)",
    "incantation": "(Úchopové kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo umožňuje, aby byl cíl snadno uchopitelný a držený. Bylo používáno při Famfrpálu. V nynějších dobách je Camrál navržen tak, aby byl snadno udržitelný a není tak tohoto kouzla třeba....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"ventus": {
    "name_cs": "Ventus",
    "name_en": "Ventus",
    "incantation": "Ventus",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Vyvolá silný proud vzduchu ze špičky hůlky. Kouzlo má i svou posílenou verzi – Ventus Duo....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"veslicove_kouzlo": {
    "name_cs": "(Veslicové kouzlo)",
    "name_en": "(Veslicové kouzlo)",
    "incantation": "(Veslicové kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo umožňuje loďce, aby sama plula, bez jakékoliv výpomoci....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"vera_verto": {
    "name_cs": "Vera Verto",
    "name_en": "Vera Verto",
    "incantation": "Vera Verto",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Promění živého tvora v pohár na vodu. Harryho třída se ho učila v přeměňování ve filmovém zpracování druhého ročníku s profesorkou McGonnagallovou. Před pronesením formule je nutno na cíl (tvora) třik...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"verdillious": {
    "name_cs": "Verdillious",
    "name_en": "Verdillious",
    "incantation": "Verdillious",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Při seslání špička hůlky napodobí hořící zelenou prskavku....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"verdimillious": {
    "name_cs": "Verdimillious",
    "name_en": "Verdimillious",
    "incantation": "Verdimillious",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo vystřelí ze špičky hůlky zelené jiskry, které mohou být použity v duelu, ale také k odhalení předmětů skrytých černou magií. Kouzlo má i posílenou verzi Verdimillious Duo, která má však červené...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"vipera_evanesca": {
    "name_cs": "Vipera Evanesca",
    "name_en": "Vipera Evanesca",
    "incantation": "Vipera Evanesca",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 8,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Varianta kouzla Evanesco (vyřčena pouze ve filmu). Je bezpečné a na rozdíl od kletby Avada Kedavra povolené, i když živý cíl rovnou zničí zaživa (bez zabití). Použil jej Severus Snape ve druhém díle v...",
    "learning_time_hours": 60,
    "legality": "legal",
    "reputation_impact": 0
},

"vitaglacius": {
    "name_cs": "Vitaglacius",
    "name_en": "Vitaglacius",
    "incantation": "Vitaglacius",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo, které okamžitě zmrazí vodu...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"vitealova_kletba": {
    "name_cs": "(Viteálová kletba)",
    "name_en": "(Viteálová kletba)",
    "incantation": "(Viteálová kletba)",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 8,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Kletba umožňující čaroději nebo čarodějce uzavřít kus své duše do objektu, čímž z něj udělá Viteál. K tomu, aby mohl člověk tohoto ohavného kouzla použít, musí zabít člověka. Jde tak o jednu z nejhorš...",
    "learning_time_hours": 40,
    "legality": "forbidden",
    "reputation_impact": -30
},

"voateaceterain": {
    "name_cs": "Voateaceterain",
    "name_en": "Voateaceterain",
    "incantation": "Voateaceterain",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Toto kouzlo působí pouze na zvířata a dělá je mnohem hrůzostrašnějšími a silnějšími....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"vulnera_sanentur": {
    "name_cs": "Vulnera Sanentur",
    "name_en": "Vulnera Sanentur",
    "incantation": "Vulnera Sanentur",
    "type": "healing",
    "category": "healing",
    "difficulty": 5,
    "cooldown": 12,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "healing",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "green",
        "sound": "heal",
        "projectile": False
    },
    "description": "Jedná se o léčivé kouzlo, které bylo vytvořeno Severusem Snapem jako protikouzlo ke kletbě Sectumsempra. Jeho formule se podle knihy podobá písni. Formule se vysloví 3x, než dojde k plnému vyléčení ra...",
    "learning_time_hours": 18,
    "legality": "legal",
    "reputation_impact": 5
},

"vyhlazovaci_kouzlo": {
    "name_cs": "(Vyhlazovací kouzlo)",
    "name_en": "(Vyhlazovací kouzlo)",
    "incantation": "(Vyhlazovací kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo nechá zmizet stopy....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"vysusovaci_kouzlo": {
    "name_cs": "(Vysušovací kouzlo)",
    "name_en": "(Vysušovací kouzlo)",
    "incantation": "(Vysušovací kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo způsobující vysušení určitého množství vody. Není však dost silné, aby ovlivnilo jezera, či rybníky. Většinou se užívá k vysušení oblečení....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"vysychani_usi": {
    "name_cs": "(Vysychání uší)",
    "name_en": "(Vysychání uší)",
    "incantation": "(Vysychání uší)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kletba způsobující, že uši cíle vyschnou....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"vyvrzeni_vnitrnosti": {
    "name_cs": "(Vyvržení vnitřností)",
    "name_en": "(Vyvržení vnitřností)",
    "incantation": "(Vyvržení vnitřností)",
    "type": "combat",
    "category": "dark_magic",
    "difficulty": 8,
    "cooldown": 20,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "dark_magic",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "black",
        "sound": "dark_spell",
        "projectile": True
    },
    "description": "Kletba pravděpodobně způsobující vyvržení vnitřností cíle....",
    "learning_time_hours": 40,
    "legality": "forbidden",
    "reputation_impact": -30
},

"vznaseci_kouzlo": {
    "name_cs": "(Vznášecí kouzlo)",
    "name_en": "(Vznášecí kouzlo)",
    "incantation": "(Vznášecí kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo umožňující levitovat určitý objekt. Jedná se nejspíš o jednu z variací kouzla Wingardium Leviosa. Bylo použito například Dobbym v druhém díle....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"waddiwasi": {
    "name_cs": "Waddiwasi",
    "name_en": "Waddiwasi",
    "incantation": "Waddiwasi",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Použil Remus John Lupin ve třetím díle, kdy ji použil proti Protivovi (pouze v knize). Po vyřčení zaklínadla vyletěla z klíčové dírky žvýkačka (kterou tam předtím Protiva nacpal) a vletěla strašidlu d...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"wingardium_leviosa": {
    "name_cs": "Wingardium Leviosa",
    "name_en": "Wingardium Leviosa",
    "incantation": "Wingardium Leviosa",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Způsobuje levitaci předmětů. Ke kouzlu je kromě slov nutný pohyb hůlkou: švihnout a přiklepnout (ve filmu a hře švihnout a mávnout). Jako první z Harryho ročníku se ho naučila Hermiona, za což profeso...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"zahusteni_vlasu": {
    "name_cs": "(Zahuštění vlasů)",
    "name_en": "(Zahuštění vlasů)",
    "incantation": "(Zahuštění vlasů)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo způsobí, že vlasy a obočí oběti jsou velmi husté a začnou rychle růst....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"zakopni_a_spadni": {
    "name_cs": "Zakopni a spadni",
    "name_en": "Zakopni a spadni",
    "incantation": "Zakopni a spadni",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Vytvoří neviditelnou překážku o kterou každý zakopne....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"zapomen": {
    "name_cs": "Zapomeň",
    "name_en": "Zapomeň",
    "incantation": "Zapomeň",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Případně Zapomeňte či Obliviate (v angličtině také Amnesia či Forget). Člověk, na kterého bylo kouzlo sesláno, kompletně zapomene na určitou událost nebo okamžik, který mu druhý kouzelník nebo čaroděj...",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"zastiraci_kouzlo": {
    "name_cs": "(Zastírací kouzlo)",
    "name_en": "(Zastírací kouzlo)",
    "incantation": "(Zastírací kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Způsobí, že člověk nebo věc, na kterou je kouzlo sesláno, splyne s okolím, a tím jej zneviditelní. Toto kouzlo je ovšem poměrně nespolehlivé a stává se, že ve chvíli, kdy je potřeba nejvíc, neviditeln...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"zateplovaci_kouzlo": {
    "name_cs": "(Zateplovací kouzlo)",
    "name_en": "(Zateplovací kouzlo)",
    "incantation": "(Zateplovací kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Zateplí a vysuší daný předmět. Poprvé ho použila Hermiona Grangerová v pátém dílu na sebe, když se vrátila od návštěvy Hagrida, který se, po dlouhé době, uprostřed zimy, vrátil ze své výpravy, kterou ...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"zmrazovaci_kouzlo": {
    "name_cs": "(Zmrazovací kouzlo)",
    "name_en": "(Zmrazovací kouzlo)",
    "incantation": "(Zmrazovací kouzlo)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Zmrazovací kouzlo (v angličtině Freezing Charm) se požívá ke znehybnění. Je možné jej také použít k inaktivaci mudlovských poplašných zařízení, což využíval Horácio Křiklan, když se skrýval v jejich d...",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

"zelatinovy_mozek": {
    "name_cs": "(Želatinový mozek)",
    "name_en": "(Želatinový mozek)",
    "incantation": "(Želatinový mozek)",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kouzlo negativně ovlivňující myšlení cíle....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"zelatinove_prsty": {
    "name_cs": "(Želatinové prsty)",
    "name_en": "(Želatinové prsty)",
    "incantation": "(Želatinové prsty)",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Kletba způsobující změkčení prstů cíle na úroveň želatiny....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"zer_slimaky": {
    "name_cs": "Žer slimáky",
    "name_en": "Žer slimáky",
    "incantation": "Žer slimáky",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Paprsek zeleného světla zasáhne oběť, která pak následujících deset minut zvrací slimáky. Použil ho Ronald Weasley ve druhém díle na Draca Malfoye protože řekl Hermioně že je mudlovská šmejdka. Ron mě...",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"zihadlova_kletba": {
    "name_cs": "(Žihadlová kletba)",
    "name_en": "(Žihadlová kletba)",
    "incantation": "(Žihadlová kletba)",
    "type": "combat",
    "category": "damage",
    "difficulty": 6,
    "cooldown": 8,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "red",
        "sound": "blast",
        "projectile": True
    },
    "description": "Bolestivá kletba způsobí, že zasažená část cíle oteče. Byla použita v sedmém díle Hermionou Grangerovou, aby zamaskovala tvář Harryho Pottera....",
    "learning_time_hours": 20,
    "legality": "legal_combat",
    "reputation_impact": 0
},

"zivy_sat": {
    "name_cs": "(Živý šat)",
    "name_en": "(Živý šat)",
    "incantation": "(Živý šat)",
    "type": "utility",
    "category": "utility",
    "difficulty": 3,
    "cooldown": 3,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "utility",
            "description": "Auto-generated, needs manual review"
        }
    },
    "visual": {
        "color": "white",
        "sound": "spell_cast",
        "projectile": False
    },
    "description": "Kouzlo umožňuje kouzelníkovi oživit a následně ovládat své oblečení, či jeho části....",
    "learning_time_hours": 8,
    "legality": "legal",
    "reputation_impact": 0
},

}


def save_database():
    """Uloží databázi do JSON souboru"""
    with open('/home/claude/hp_duel_bot/data/spells.json', 'w', encoding='utf-8') as f:
        json.dump(SPELLS_DATABASE, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Uloženo {len(SPELLS_DATABASE)} kouzel do databáze")
    
    # Statistiky
    categories = {}
    difficulties = {}
    
    for spell_id, spell in SPELLS_DATABASE.items():
        cat = spell.get('category', 'unknown')
        diff = spell.get('difficulty', 0)
        
        categories[cat] = categories.get(cat, 0) + 1
        difficulties[diff] = difficulties.get(diff, 0) + 1
    
    print("\n📊 Statistiky kouzel:")
    print(f"Celkem kouzel: {len(SPELLS_DATABASE)}")
    print(f"\nKategorie:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    print(f"\nObotížnost:")
    for diff, count in sorted(difficulties.items()):
        print(f"  Level {diff}: {count}")


if __name__ == "__main__":
    import os
    os.makedirs('/home/claude/hp_duel_bot/data', exist_ok=True)
    save_database()
