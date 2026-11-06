"""
Potion Database - Všechny lektvary v HP světě
S realistickými efekty a recepty
"""

from models.potions import (
    Potion, PotionRecipe, PotionEffectData, PotionEffect, 
    PotionRarity, INGREDIENTS
)


# ========== POTION DEFINITIONS ==========

POTIONS_DATABASE = {}


def register_potion(potion: Potion):
    """Registruje lektvar do databáze"""
    POTIONS_DATABASE[potion.id] = potion
    return potion


# ========== MNOHOLIČNÝ LEKTVAR (POLYJUICE POTION) ==========

POLYJUICE_POTION = register_potion(Potion(
    id="polyjuice_potion",
    name_cs="Mnoholičný lektvar",
    name_en="Polyjuice Potion",
    description="Umožňuje proměnu v jinou osobu na jednu hodinu. Příprava trvá měsíc.",
    rarity=PotionRarity.VERY_RARE,
    color="muddy_brown",
    appearance="hustá hnědá tekutina s bublinami",
    effects=[
        PotionEffectData(
            effect_type=PotionEffect.POLYMORPH,
            duration=3600.0,  # 1 hodina
            strength=10,
            target="self",
            description="Proměna v cílovou osobu (vyžaduje vlas/součást)"
        )
    ],
    recipe=PotionRecipe(
        potion_id="polyjuice_potion",
        ingredients={
            "lacewing_flies": 10,      # Síťokřídlé mouchy
            "boomslang_skin": 5,       # Kůže boomslanga
            "bicorn_horn": 2,          # Roh bicorna
            "mandrake_root": 3,        # Kořen mandragory
            "wormwood": 5              # Pelyněk
        },
        brewing_time=720.0,  # 30 dní (v hodinách)
        difficulty=9,
        failure_chance=0.3,
        required_skill=70
    ),
    buy_price=5000,
    sell_price=2500
))


# ========== FELIX FELICIS ==========

FELIX_FELICIS = register_potion(Potion(
    id="felix_felicis",
    name_cs="Felix Felicis",
    name_en="Felix Felicis",
    description="Zajišťuje pijákovi štěstí po omezenou dobu. Zlatavá barva.",
    rarity=PotionRarity.LEGENDARY,
    color="golden",
    appearance="tekoucí zlato, třpytivé",
    effects=[
        PotionEffectData(
            effect_type=PotionEffect.LUCK,
            duration=3600.0,  # 1 hodina
            strength=10,
            target="self",
            description="+50% šance na kritický hit, +30% úhyb, automatický úspěch v náročných akcích"
        )
    ],
    recipe=PotionRecipe(
        potion_id="felix_felicis",
        ingredients={
            "felix_felicis_essence": 1,
            "unicorn_hair": 3,
            "moonstone": 5,
            "ashwinder_egg": 2
        },
        brewing_time=168.0,  # 7 dní
        difficulty=10,
        failure_chance=0.5,
        required_skill=90
    ),
    buy_price=10000,
    sell_price=5000
))


# ========== VERITASÉRUM ==========

VERITASERUM = register_potion(Potion(
    id="veritaserum",
    name_cs="Veritasérum",
    name_en="Veritaserum",
    description="Extrémně silný lektvar pravdy. Tři kapky donutí kohokoliv prozradit vše.",
    rarity=PotionRarity.VERY_RARE,
    color="clear",
    appearance="průhledná jako voda, bez chuti i zápachu",
    effects=[
        PotionEffectData(
            effect_type=PotionEffect.TRUTH_SERUM,
            duration=600.0,  # 10 minut
            strength=10,
            target="other",  # Musí se aplikovat na někoho jiného
            description="Oběť musí mluvit pravdu a odpovídat na všechny otázky"
        )
    ],
    recipe=PotionRecipe(
        potion_id="veritaserum",
        ingredients={
            "moonstone": 10,
            "wormwood": 15,
            "unicorn_hair": 1
        },
        brewing_time=672.0,  # 28 dní (měsíční cyklus)
        difficulty=8,
        failure_chance=0.2,
        required_skill=60
    ),
    buy_price=3000,
    sell_price=1500
))


# ========== VŠELÉK (BEZOÁR) ==========

UNIVERSAL_ANTIDOTE = register_potion(Potion(
    id="universal_antidote",
    name_cs="Všelék",
    name_en="Universal Antidote",
    description="Léčí většinu jedů. Bezoár z žaludku kozy.",
    rarity=PotionRarity.RARE,
    color="grey",
    appearance="šedý kámen rozpuštěný ve vodě",
    effects=[
        PotionEffectData(
            effect_type=PotionEffect.ANTIDOTE,
            duration=0,  # Okamžitý efekt
            strength=9,
            target="self",
            description="Vyléčí většinu jedů a toxinů"
        ),
        PotionEffectData(
            effect_type=PotionEffect.HEALING,
            duration=0,
            strength=5,
            target="self",
            description="Částečně obnoví zdraví"
        )
    ],
    recipe=PotionRecipe(
        potion_id="universal_antidote",
        ingredients={
            "bezoar": 1,
            "mandrake_root": 2,
            "peppermint": 3
        },
        brewing_time=2.0,  # 2 hodiny
        difficulty=4,
        failure_chance=0.1,
        required_skill=20
    ),
    buy_price=800,
    sell_price=400
))


# ========== LEKTVAR ŽIVÉ SMRTI ==========

DRAUGHT_OF_LIVING_DEATH = register_potion(Potion(
    id="living_death",
    name_cs="Lektvar živé smrti",
    name_en="Draught of Living Death",
    description="Způsobuje hluboký spánek podobný smrti.",
    rarity=PotionRarity.RARE,
    color="purple_black",
    appearance="temná fialovo-černá tekutina, kouřící",
    effects=[
        PotionEffectData(
            effect_type=PotionEffect.SLEEP,
            duration=28800.0,  # 8 hodin
            strength=10,
            target="self",
            description="Hluboký spánek - nelze probudit kromě protiléku"
        )
    ],
    recipe=PotionRecipe(
        potion_id="living_death",
        ingredients={
            "sopophorous_bean": 5,
            "valerian_root": 10,
            "wormwood": 7
        },
        brewing_time=12.0,  # 12 hodin
        difficulty=7,
        failure_chance=0.25,
        required_skill=50
    ),
    buy_price=1200,
    sell_price=600
))


# ========== AMORTENCE ==========

AMORTENTIA = register_potion(Potion(
    id="amortentia",
    name_cs="Amortence",
    name_en="Amortentia",
    description="Nejsilnější lektvar lásky. Voní každému po tom, co ho přitahuje.",
    rarity=PotionRarity.VERY_RARE,
    color="pearl_pink",
    appearance="perleťově růžová, kouřící spirály",
    effects=[
        PotionEffectData(
            effect_type=PotionEffect.LOVE_POTION,
            duration=86400.0,  # 24 hodin
            strength=10,
            target="other",
            description="Způsobí silnou posedlost cílovou osobou"
        )
    ],
    recipe=PotionRecipe(
        potion_id="amortentia",
        ingredients={
            "rose_thorns": 20,
            "ashwinder_egg": 3,
            "moonstone": 7,
            "peppermint": 10,
            "unicorn_hair": 2
        },
        brewing_time=168.0,  # 7 dní
        difficulty=8,
        failure_chance=0.3,
        required_skill=65
    ),
    buy_price=4000,
    sell_price=2000
))


# ========== VLKODLAČÍ LEKTVAR ==========

WOLFSBANE_POTION = register_potion(Potion(
    id="wolfsbane_potion",
    name_cs="Vlkodlačí lektvar",
    name_en="Wolfsbane Potion",
    description="Umožňuje vlkodlakům zachovat si při proměně lidskou mysl.",
    rarity=PotionRarity.VERY_RARE,
    color="smoke_blue",
    appearance="kouřově modrá, chutná odporně",
    effects=[
        PotionEffectData(
            effect_type=PotionEffect.WEREWOLF_CONTROL,
            duration=28800.0,  # 8 hodin (přes úplněk)
            strength=10,
            target="self",
            description="Vlkodlak si zachová lidskou mysl během proměny"
        )
    ],
    recipe=PotionRecipe(
        potion_id="wolfsbane_potion",
        ingredients={
            "wolfsbane": 10,
            "moonstone": 5,
            "mandrake_root": 3,
            "wormwood": 8
        },
        brewing_time=168.0,  # 7 dní (týdenní příprava před úplňkem)
        difficulty=9,
        failure_chance=0.4,
        required_skill=75
    ),
    buy_price=6000,
    sell_price=3000
))


# ========== BONUS LEKTVARY ==========

# Léčivý lektvar
HEALING_POTION = register_potion(Potion(
    id="healing_potion",
    name_cs="Léčivý lektvar",
    name_en="Healing Potion",
    description="Základní léčivý lektvar. Hojí lehká zranění.",
    rarity=PotionRarity.COMMON,
    color="red",
    appearance="jasně červená tekutina",
    effects=[
        PotionEffectData(
            effect_type=PotionEffect.HEALING,
            duration=0,
            strength=5,
            target="self",
            description="Vyléčí lehká zranění, zastaví krvácení"
        )
    ],
    recipe=PotionRecipe(
        potion_id="healing_potion",
        ingredients={
            "mandrake_root": 2,
            "peppermint": 3,
            "unicorn_hair": 1
        },
        brewing_time=4.0,  # 4 hodiny
        difficulty=3,
        failure_chance=0.1,
        required_skill=0
    ),
    buy_price=200,
    sell_price=100
))


# Lektvar neviditelnosti
INVISIBILITY_POTION = register_potion(Potion(
    id="invisibility_potion",
    name_cs="Lektvar neviditelnosti",
    name_en="Invisibility Potion",
    description="Dočasně tě učiní neviditelným.",
    rarity=PotionRarity.RARE,
    color="transparent",
    appearance="průhledná, třpytivá",
    effects=[
        PotionEffectData(
            effect_type=PotionEffect.INVISIBILITY,
            duration=3600.0,  # 1 hodina
            strength=8,
            target="self",
            description="Neviditelnost - ostatní tě nevidí"
        )
    ],
    recipe=PotionRecipe(
        potion_id="invisibility_potion",
        ingredients={
            "moonstone": 3,
            "lacewing_flies": 5,
            "unicorn_hair": 2
        },
        brewing_time=24.0,  # 24 hodin
        difficulty=6,
        failure_chance=0.2,
        required_skill=40
    ),
    buy_price=1500,
    sell_price=750
))


# ========== HELPER FUNCTIONS ==========

def get_potion(potion_id: str) -> Potion:
    """Získá lektvar podle ID"""
    return POTIONS_DATABASE.get(potion_id)


def get_all_potions() -> list:
    """Vrátí všechny lektvary"""
    return list(POTIONS_DATABASE.values())


def get_potions_by_rarity(rarity: PotionRarity) -> list:
    """Vrátí lektvary podle vzácnosti"""
    return [p for p in POTIONS_DATABASE.values() if p.rarity == rarity]


def get_brewable_potions(player_skill: int) -> list:
    """Vrátí lektvary které může hráč uvařit"""
    return [
        p for p in POTIONS_DATABASE.values() 
        if p.recipe and p.recipe.can_brew(player_skill)
    ]
