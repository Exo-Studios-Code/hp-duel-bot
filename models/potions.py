"""
Potion System - Lektvary a jejich efekty
Realistické vaření s časem, ingrediencemi a účinky
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Callable, Any
from enum import Enum
import time
import json


class PotionRarity(Enum):
    """Vzácnost lektvaru"""
    COMMON = "common"           # Běžný
    UNCOMMON = "uncommon"       # Neobvyklý
    RARE = "rare"               # Vzácný
    VERY_RARE = "very_rare"     # Velmi vzácný
    LEGENDARY = "legendary"     # Legendární


class PotionEffect(Enum):
    """Typy efektů lektvarů"""
    # Léčivé
    HEALING = "healing"
    ANTIDOTE = "antidote"
    
    # Transformace
    POLYMORPH = "polymorph"
    SIZE_CHANGE = "size_change"
    
    # Mentální
    TRUTH_SERUM = "truth_serum"
    LOVE_POTION = "love_potion"
    MEMORY_MODIFICATION = "memory_modification"
    CLARITY = "clarity"
    
    # Combat
    LUCK = "luck"
    INVISIBILITY = "invisibility"
    STRENGTH = "strength"
    SPEED = "speed"
    
    # Speciální
    SLEEP = "sleep"
    WEREWOLF_CONTROL = "werewolf_control"
    PROTECTION = "protection"
    RESISTANCE = "resistance"


class IngredientType(Enum):
    """Typy ingrediencí"""
    PLANT = "plant"
    MINERAL = "mineral"
    ANIMAL = "animal"
    MAGICAL = "magical"
    RARE = "rare"


@dataclass
class Ingredient:
    """Ingredience pro vaření"""
    id: str
    name_cs: str
    name_en: str
    type: IngredientType
    rarity: PotionRarity
    description: str
    gathering_location: Optional[str] = None  # Kde se dá sebrat
    buy_price: int = 100  # Cena v galleonech
    
    def __hash__(self):
        return hash(self.id)


@dataclass
class PotionRecipe:
    """Recept na lektvar"""
    potion_id: str
    ingredients: Dict[str, int]  # {ingredient_id: množství}
    brewing_time: float  # v hodinách
    difficulty: int  # 1-10
    failure_chance: float  # 0.0-1.0
    required_skill: int = 0  # Minimální skill pro vaření
    
    def can_brew(self, player_skill: int) -> bool:
        """Může hráč uvařit tento lektvar?"""
        return player_skill >= self.required_skill


@dataclass
class PotionEffectData:
    """Data o efektu lektvaru"""
    effect_type: PotionEffect
    duration: float  # v sekundách (0 = permanent/instant)
    strength: int  # 1-10
    target: str = "self"  # "self", "other", "area"
    description: str = ""
    
    # Callback funkce pro aplikaci efektu
    apply_callback: Optional[Callable] = None
    remove_callback: Optional[Callable] = None


@dataclass
class Potion:
    """Lektvar"""
    id: str
    name_cs: str
    name_en: str
    description: str
    rarity: PotionRarity
    
    # Vzhled
    color: str = "clear"
    appearance: str = "tekutina"
    
    # Efekty
    effects: List[PotionEffectData] = field(default_factory=list)
    
    # Recipe
    recipe: Optional[PotionRecipe] = None
    
    # Hodnota
    buy_price: int = 1000
    sell_price: int = 500
    
    # Metadata
    created_by: Optional[int] = None  # Discord ID
    created_at: float = field(default_factory=time.time)
    quality: float = 1.0  # 0.0-2.0 (ovlivňuje sílu efektů)


@dataclass
class BrewingProcess:
    """Probíhající proces vaření"""
    player_id: int
    potion_id: str
    start_time: float
    end_time: float
    ingredients_used: Dict[str, int]
    
    def is_complete(self) -> bool:
        """Je vaření hotové?"""
        return time.time() >= self.end_time
    
    def time_remaining(self) -> float:
        """Kolik času zbývá (v sekundách)?"""
        return max(0, self.end_time - time.time())
    
    def progress(self) -> float:
        """Pokrok 0.0-1.0"""
        total_time = self.end_time - self.start_time
        elapsed = time.time() - self.start_time
        return min(1.0, elapsed / total_time)


@dataclass
class PotionInventory:
    """Inventář lektvarů hráče"""
    potions: Dict[str, int] = field(default_factory=dict)  # {potion_id: count}
    ingredients: Dict[str, int] = field(default_factory=dict)  # {ingredient_id: count}
    active_brewing: Optional[BrewingProcess] = None
    brewing_skill: int = 0  # 0-100
    
    def add_potion(self, potion_id: str, count: int = 1):
        """Přidá lektvar"""
        self.potions[potion_id] = self.potions.get(potion_id, 0) + count
    
    def remove_potion(self, potion_id: str, count: int = 1) -> bool:
        """Odebere lektvar, vrací True pokud úspěch"""
        if self.potions.get(potion_id, 0) >= count:
            self.potions[potion_id] -= count
            if self.potions[potion_id] == 0:
                del self.potions[potion_id]
            return True
        return False
    
    def add_ingredient(self, ingredient_id: str, count: int = 1):
        """Přidá ingredienci"""
        self.ingredients[ingredient_id] = self.ingredients.get(ingredient_id, 0) + count
    
    def remove_ingredient(self, ingredient_id: str, count: int = 1) -> bool:
        """Odebere ingredienci"""
        if self.ingredients.get(ingredient_id, 0) >= count:
            self.ingredients[ingredient_id] -= count
            if self.ingredients[ingredient_id] == 0:
                del self.ingredients[ingredient_id]
            return True
        return False
    
    def has_ingredients(self, recipe: Dict[str, int]) -> bool:
        """Má hráč všechny ingredience?"""
        for ingredient_id, count in recipe.items():
            if self.ingredients.get(ingredient_id, 0) < count:
                return False
        return True


# ========== INGREDIENCE DATABASE ==========

INGREDIENTS = {
    # Běžné
    "mandrake_root": Ingredient(
        id="mandrake_root",
        name_cs="Kořen mandragory",
        name_en="Mandrake Root",
        type=IngredientType.PLANT,
        rarity=PotionRarity.COMMON,
        description="Kořen mandragory, křičí když se vytáhne",
        gathering_location="forbidden_forest",
        buy_price=50
    ),
    "wormwood": Ingredient(
        id="wormwood",
        name_cs="Pelyněk",
        name_en="Wormwood",
        type=IngredientType.PLANT,
        rarity=PotionRarity.COMMON,
        description="Hořká bylina",
        buy_price=20
    ),
    "boomslang_skin": Ingredient(
        id="boomslang_skin",
        name_cs="Kůže boomslanga",
        name_en="Boomslang Skin",
        type=IngredientType.ANIMAL,
        rarity=PotionRarity.UNCOMMON,
        description="Svlečená kůže africké jedovaté hada",
        buy_price=150
    ),
    "lacewing_flies": Ingredient(
        id="lacewing_flies",
        name_cs="Síťokřídlé mouchy",
        name_en="Lacewing Flies",
        type=IngredientType.ANIMAL,
        rarity=PotionRarity.UNCOMMON,
        description="Mouchy musí být namáčené 21 dní",
        buy_price=80
    ),
    "bicorn_horn": Ingredient(
        id="bicorn_horn",
        name_cs="Roh bicorna",
        name_en="Bicorn Horn",
        type=IngredientType.MAGICAL,
        rarity=PotionRarity.RARE,
        description="Roh z magického tvora",
        buy_price=500
    ),
    "unicorn_hair": Ingredient(
        id="unicorn_hair",
        name_cs="Vlasy jednorožce",
        name_en="Unicorn Hair",
        type=IngredientType.MAGICAL,
        rarity=PotionRarity.RARE,
        description="Stříbrné vlasy jednorožce",
        buy_price=1000
    ),
    "felix_felicis_essence": Ingredient(
        id="felix_felicis_essence",
        name_cs="Esence štěstí",
        name_en="Felix Felicis Essence",
        type=IngredientType.MAGICAL,
        rarity=PotionRarity.LEGENDARY,
        description="Vzácná magická esence",
        buy_price=5000
    ),
    "moonstone": Ingredient(
        id="moonstone",
        name_cs="Měsíční kámen",
        name_en="Moonstone",
        type=IngredientType.MINERAL,
        rarity=PotionRarity.UNCOMMON,
        description="Kámen nabitý měsíční energií",
        buy_price=200
    ),
    "bezoar": Ingredient(
        id="bezoar",
        name_cs="Bezoár",
        name_en="Bezoar",
        type=IngredientType.ANIMAL,
        rarity=PotionRarity.RARE,
        description="Kámen z žaludku kozy, lék na většinu jedů",
        buy_price=800
    ),
    "valerian_root": Ingredient(
        id="valerian_root",
        name_cs="Kořen kozlíku",
        name_en="Valerian Root",
        type=IngredientType.PLANT,
        rarity=PotionRarity.COMMON,
        description="Uspávací bylina",
        buy_price=30
    ),
    "sopophorous_bean": Ingredient(
        id="sopophorous_bean",
        name_cs="Uspávací bob",
        name_en="Sopophorous Bean",
        type=IngredientType.PLANT,
        rarity=PotionRarity.UNCOMMON,
        description="Bob s uspávacími vlastnostmi",
        buy_price=100
    ),
    "ashwinder_egg": Ingredient(
        id="ashwinder_egg",
        name_cs="Vajíčko popelníka",
        name_en="Ashwinder Egg",
        type=IngredientType.MAGICAL,
        rarity=PotionRarity.RARE,
        description="Horké vajíčko magického hada",
        buy_price=600
    ),
    "rose_thorns": Ingredient(
        id="rose_thorns",
        name_cs="Růžové trny",
        name_en="Rose Thorns",
        type=IngredientType.PLANT,
        rarity=PotionRarity.COMMON,
        description="Trny z růže",
        buy_price=15
    ),
    "peppermint": Ingredient(
        id="peppermint",
        name_cs="Máta peprná",
        name_en="Peppermint",
        type=IngredientType.PLANT,
        rarity=PotionRarity.COMMON,
        description="Osvěžující bylina",
        buy_price=10
    ),
    "wolfsbane": Ingredient(
        id="wolfsbane",
        name_cs="Přílba modrá",
        name_en="Wolfsbane",
        type=IngredientType.PLANT,
        rarity=PotionRarity.RARE,
        description="Jedovatá rostlina používaná proti vlkodlakům",
        buy_price=400
    ),
}


def get_ingredient(ingredient_id: str) -> Optional[Ingredient]:
    """Získá ingredienci podle ID"""
    return INGREDIENTS.get(ingredient_id)


def get_all_ingredients() -> List[Ingredient]:
    """Vrátí všechny ingredience"""
    return list(INGREDIENTS.values())
