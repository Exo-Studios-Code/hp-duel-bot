"""
Procedural World Generator - Generování nekonečného open worldu
Když hráč jde někam co neexistuje, automaticky se to vytvoří
"""

import random
import hashlib
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from models.world import Location, LocationType, PvPZone, Weather


@dataclass
class BiomeDefinition:
    """Definice biomu pro generování"""
    name: str
    location_types: List[LocationType]  # Jaké typy lokací se mohou vyskytnout
    weather_weights: Dict[Weather, float]  # Pravděpodobnost počasí
    resource_pool: Dict[str, float]  # Možné zdroje a jejich šance
    danger_modifier: float  # 1.0 = normální, 2.0 = dvojnásobně nebezpečné
    next_biomes: Dict[str, float]  # Jaké biomy mohou navazovat {biome_name: weight}


# Biomy pro generování
BIOMES = {
    "forest": BiomeDefinition(
        name="forest",
        location_types=[LocationType.FOREST, LocationType.WILDERNESS, LocationType.RUINS],
        weather_weights={
            Weather.CLEAR: 0.4,
            Weather.RAIN: 0.3,
            Weather.FOG: 0.2,
            Weather.NIGHT: 0.1
        },
        resource_pool={
            "mandrake_root": 0.3,
            "wormwood": 0.4,
            "dittany": 0.2,
            "unicorn_hair": 0.05
        },
        danger_modifier=1.5,
        next_biomes={
            "forest": 0.4,
            "wilderness": 0.3,
            "village": 0.2,
            "ruins": 0.1
        }
    ),
    
    "wilderness": BiomeDefinition(
        name="wilderness",
        location_types=[LocationType.WILDERNESS, LocationType.RUINS],
        weather_weights={
            Weather.CLEAR: 0.5,
            Weather.RAIN: 0.2,
            Weather.NIGHT: 0.2,
            Weather.FOG: 0.1
        },
        resource_pool={
            "mandrake_root": 0.2,
            "wormwood": 0.3,
            "moonstone": 0.1
        },
        danger_modifier=1.2,
        next_biomes={
            "wilderness": 0.3,
            "forest": 0.3,
            "village": 0.25,
            "city": 0.15
        }
    ),
    
    "village": BiomeDefinition(
        name="village",
        location_types=[LocationType.VILLAGE, LocationType.CITY],
        weather_weights={
            Weather.CLEAR: 0.6,
            Weather.RAIN: 0.25,
            Weather.NIGHT: 0.15
        },
        resource_pool={},
        danger_modifier=0.5,
        next_biomes={
            "village": 0.2,
            "city": 0.3,
            "wilderness": 0.3,
            "forest": 0.2
        }
    ),
    
    "city": BiomeDefinition(
        name="city",
        location_types=[LocationType.CITY, LocationType.VILLAGE],
        weather_weights={
            Weather.CLEAR: 0.7,
            Weather.RAIN: 0.2,
            Weather.NIGHT: 0.1
        },
        resource_pool={},
        danger_modifier=0.3,
        next_biomes={
            "city": 0.3,
            "village": 0.4,
            "wilderness": 0.3
        }
    ),
    
    "ruins": BiomeDefinition(
        name="ruins",
        location_types=[LocationType.RUINS, LocationType.DUNGEON],
        weather_weights={
            Weather.FOG: 0.4,
            Weather.NIGHT: 0.3,
            Weather.CLEAR: 0.2,
            Weather.STORM: 0.1
        },
        resource_pool={
            "moonstone": 0.3,
            "unicorn_hair": 0.15,
            "dittany": 0.2
        },
        danger_modifier=2.0,
        next_biomes={
            "ruins": 0.3,
            "forest": 0.3,
            "wilderness": 0.4
        }
    )
}


class ProceduralWorldGenerator:
    """Generátor procedurálního světa"""
    
    def __init__(self, existing_locations: Dict[str, Location]):
        self.existing_locations = existing_locations
        
        # Slovníky pro generování názvů
        self.name_prefixes = {
            LocationType.FOREST: ["Temný", "Starý", "Zapovězený", "Kouzelný", "Mlhavý", "Tichý"],
            LocationType.WILDERNESS: ["Širá", "Pustá", "Divočina", "Pustina", "Planina"],
            LocationType.VILLAGE: ["Malá", "Stará", "Nová", "Horní", "Dolní", "Klidná"],
            LocationType.CITY: ["Velké", "Královské", "Staré", "Nové"],
            LocationType.RUINS: ["Zřícenina", "Trosky", "Pozůstatky", "Ruiny"],
            LocationType.DUNGEON: ["Jeskyně", "Katakómby", "Podzemí", "Sklepy"]
        }
        
        self.name_suffixes = {
            LocationType.FOREST: ["les", "háj", "bor", "doubravy", "houští"],
            LocationType.WILDERNESS: ["pláně", "step", "mokřad", "pastviny", "pole"],
            LocationType.VILLAGE: ["ves", "víska", "osada", "dvorec", "statek"],
            LocationType.CITY: ["město", "hradisko", "bašta", "sídelní"],
            LocationType.RUINS: ["hradu", "kláštera", "tvrze", "paláce", "dómu"],
            LocationType.DUNGEON: ["prokletých", "zapomenutých", "temných", "ztracených"]
        }
    
    def _seed_from_location_id(self, location_id: str) -> int:
        """Vytvoří deterministický seed z ID lokace"""
        return int(hashlib.md5(location_id.encode()).hexdigest(), 16) % (10 ** 8)
    
    def _generate_location_name(self, location_type: LocationType, seed: int) -> Tuple[str, str]:
        """
        Vygeneruje název lokace
        Returns: (czech_name, english_name)
        """
        rng = random.Random(seed)
        
        prefixes = self.name_prefixes.get(location_type, [""])
        suffixes = self.name_suffixes.get(location_type, ["místo"])
        
        prefix = rng.choice(prefixes)
        suffix = rng.choice(suffixes)
        
        czech_name = f"{prefix} {suffix}"
        
        # Jednoduchý anglický překlad (placeholder)
        english_name = f"{prefix} {suffix}".replace("ý", "y").replace("á", "a")
        
        return czech_name, english_name
    
    def _determine_biome(self, neighboring_locations: List[Location], seed: int) -> str:
        """Určí biome pro novou lokaci na základě sousedů"""
        rng = random.Random(seed)
        
        if not neighboring_locations:
            # Žádní sousedé -> random biome
            return rng.choice(list(BIOMES.keys()))
        
        # Vezmi nejbližšího souseda a vyber biome podle jeho next_biomes
        neighbor = neighboring_locations[0]
        
        # Detekce biomu souseda
        neighbor_biome_name = "wilderness"  # default
        for biome_name, biome in BIOMES.items():
            if neighbor.type in biome.location_types:
                neighbor_biome_name = biome_name
                break
        
        # Vyber další biome podle pravděpodobností
        biome_def = BIOMES[neighbor_biome_name]
        choices = list(biome_def.next_biomes.keys())
        weights = list(biome_def.next_biomes.values())
        
        return rng.choices(choices, weights=weights)[0]
    
    def _determine_pvp_zone(self, distance_from_spawn: int, biome: BiomeDefinition, seed: int) -> PvPZone:
        """
        Určí PvP zónu podle vzdálenosti od spawnu a nebezpečnosti biomu
        """
        rng = random.Random(seed)
        
        # Vzdálenost ovlivňuje nebezpečnost
        danger_score = distance_from_spawn * biome.danger_modifier
        
        if danger_score < 2:
            return PvPZone.SAFE
        elif danger_score < 5:
            return PvPZone.CONSENSUAL if rng.random() > 0.3 else PvPZone.SAFE
        elif danger_score < 10:
            return PvPZone.CONSENSUAL if rng.random() > 0.5 else PvPZone.OPEN
        else:
            # Velmi daleko = pravděpodobně Open PvP
            return PvPZone.OPEN if rng.random() > 0.2 else PvPZone.CONSENSUAL
    
    def _generate_services(self, location_type: LocationType, pvp_zone: PvPZone, seed: int) -> Dict:
        """Vygeneruje služby v lokaci"""
        rng = random.Random(seed)
        
        services = {
            "has_shop": False,
            "has_healer": False,
            "has_bank": False,
            "has_trainer": False,
            "has_quest_board": False,
            "has_inn": False
        }
        
        # Města a vesnice mají více služeb
        if location_type in [LocationType.CITY, LocationType.VILLAGE]:
            services["has_shop"] = rng.random() > 0.3
            services["has_healer"] = rng.random() > 0.4
            services["has_inn"] = rng.random() > 0.5
            
            if location_type == LocationType.CITY:
                services["has_bank"] = rng.random() > 0.4
                services["has_trainer"] = rng.random() > 0.5
                services["has_quest_board"] = rng.random() > 0.6
        
        # Bezpečné zóny mají vyšší šanci na služby
        if pvp_zone == PvPZone.SAFE:
            if rng.random() > 0.5:
                services["has_healer"] = True
        
        return services
    
    def _generate_resources(self, biome: BiomeDefinition, seed: int) -> Dict[str, float]:
        """Vygeneruje zdroje v lokaci"""
        rng = random.Random(seed)
        
        resources = {}
        for resource, base_chance in biome.resource_pool.items():
            if rng.random() < base_chance:
                # Množství zdroje (0.1 - 0.5)
                amount = rng.uniform(0.1, 0.5)
                resources[resource] = amount
        
        return resources
    
    def _calculate_distance_from_spawn(self, location_id: str, source_location: Optional[Location]) -> int:
        """
        Vypočítá vzdálenost od spawn pointu
        Pro jednoduchost použijeme chain distance (kolik kroků)
        """
        if not source_location:
            return 0
        
        # Pokud je source spawn point, distance = 1
        if source_location.spawn_point:
            return 1
        
        # Jinak heuristika: lokace s více službami = blíž spawnu
        service_count = sum([
            source_location.has_shop,
            source_location.has_healer,
            source_location.has_bank,
            source_location.has_trainer
        ])
        
        # Méně služeb = dál od spawnu
        base_distance = 5 - service_count
        return max(1, base_distance)
    
    def generate_location(
        self,
        location_id: str,
        source_location_id: Optional[str] = None,
        direction: Optional[str] = None
    ) -> Location:
        """
        Vygeneruje novou lokaci
        
        Args:
            location_id: ID nové lokace (použije se jako seed)
            source_location_id: ID lokace, odkud hráč přichází (pro určení biomu)
            direction: Směr cestování (north, south, east, west) - volitelné
        
        Returns:
            Nová procedurálně vygenerovaná lokace
        """
        seed = self._seed_from_location_id(location_id)
        rng = random.Random(seed)
        
        # Získej source lokaci pokud existuje
        source_location = None
        if source_location_id and source_location_id in self.existing_locations:
            source_location = self.existing_locations[source_location_id]
        
        # Urči biome
        neighboring_locations = [source_location] if source_location else []
        biome_name = self._determine_biome(neighboring_locations, seed)
        biome = BIOMES[biome_name]
        
        # Vyber typ lokace z biomu
        location_type = rng.choice(biome.location_types)
        
        # Vygeneruj jméno
        name_cs, name_en = self._generate_location_name(location_type, seed + 1)
        
        # Urči vzdálenost od spawnu
        distance_from_spawn = self._calculate_distance_from_spawn(location_id, source_location)
        
        # Urči PvP zónu
        pvp_zone = self._determine_pvp_zone(distance_from_spawn, biome, seed + 2)
        
        # Vygeneruj popis
        descriptions = self._generate_description(location_type, biome, pvp_zone, seed + 3)
        
        # Vygeneruj počasí
        weather_choices = list(biome.weather_weights.keys())
        weather_weights = list(biome.weather_weights.values())
        weather = rng.choices(weather_choices, weights=weather_weights)[0]
        
        # Vygeneruj služby
        services = self._generate_services(location_type, pvp_zone, seed + 4)
        
        # Vygeneruj zdroje
        resources = self._generate_resources(biome, seed + 5)
        
        # Viditelnost podle počasí
        visibility_map = {
            Weather.CLEAR: 1.0,
            Weather.RAIN: 0.8,
            Weather.STORM: 0.6,
            Weather.FOG: 0.5,
            Weather.SNOW: 0.7,
            Weather.NIGHT: 0.6
        }
        visibility = visibility_map.get(weather, 1.0)
        
        # Vytvoř spojení zpět na source
        connections = {}
        if source_location:
            # Vzdálenost cestování (10-30 minut)
            travel_time = rng.uniform(10, 30)
            connections[source_location_id] = travel_time
        
        # Vytvoř lokaci
        new_location = Location(
            id=location_id,
            name_cs=name_cs,
            name_en=name_en,
            type=location_type,
            pvp_zone=pvp_zone,
            description=descriptions,
            connections=connections,
            **services,
            resources=resources,
            weather=weather,
            visibility=visibility,
            allows_camping=True,  # Většina míst povoluje kempování
            allows_apparition=pvp_zone != PvPZone.OPEN,  # Open PvP = může blokovat apparition
            spawn_point=False
        )
        
        return new_location
    
    def _generate_description(
        self,
        location_type: LocationType,
        biome: BiomeDefinition,
        pvp_zone: PvPZone,
        seed: int
    ) -> str:
        """Vygeneruje popis lokace"""
        rng = random.Random(seed)
        
        # Základní popisy podle typu
        type_descriptions = {
            LocationType.FOREST: [
                "Hustý les plný starých stromů a tajemství.",
                "Temný lesní porost, kde se snadno ztratíte.",
                "Kouzelný les s podivnými zvuky a světly."
            ],
            LocationType.WILDERNESS: [
                "Pustá krajina s rozptýlenými stromy.",
                "Divoká příroda, kam málokdo zavítá.",
                "Otevřená pláň s vysokou trávou a vzácnými stezkami."
            ],
            LocationType.VILLAGE: [
                "Malá vesnice s několika domy a klidem.",
                "Osada obklopená poli a pastvinami.",
                "Poklidné místo, kde se všichni znají."
            ],
            LocationType.CITY: [
                "Rušné město plné kouzelníků a obchodů.",
                "Velké město s kamennými budovami a kouzelnou atmosférou.",
                "Městské náměstí, kde se křižují cesty mnoha cestovatělů."
            ],
            LocationType.RUINS: [
                "Zřícenina starého hradu, zarostlá břečťanem.",
                "Zbytky kdysi slavného místa, nyní opuštěné.",
                "Tajemné trosky, o kterých se vypráví legendy."
            ],
            LocationType.DUNGEON: [
                "Temné podzemí, odkud vane chlad a stín.",
                "Jeskyně plná tajemství a nebezpečí.",
                "Katakomby, které si pamatují staré časy."
            ]
        }
        
        base_desc = rng.choice(type_descriptions.get(location_type, ["Neznámé místo."]))
        
        # Přidej PvP varování
        if pvp_zone == PvPZone.OPEN:
            base_desc += " ⚔️ NEBEZPEČÍ! Open PvP zóna!"
        elif pvp_zone == PvPZone.CONSENSUAL:
            base_desc += " ⚠️ Zde je možné bojovat se souhlasem."
        
        return base_desc
    
    def connect_locations(
        self,
        location_a_id: str,
        location_b_id: str,
        locations_dict: Dict[str, Location]
    ):
        """
        Vytvoří obousměrné spojení mezi dvěma lokacemi
        """
        if location_a_id not in locations_dict or location_b_id not in locations_dict:
            return
        
        loc_a = locations_dict[location_a_id]
        loc_b = locations_dict[location_b_id]
        
        # Pokud už spojení existuje, neměň ho
        if location_b_id in loc_a.connections and location_a_id in loc_b.connections:
            return
        
        # Vygeneruj čas cestování (10-30 minut)
        seed = self._seed_from_location_id(f"{location_a_id}_{location_b_id}")
        rng = random.Random(seed)
        travel_time = rng.uniform(10, 30)
        
        # Přidej spojení
        loc_a.connections[location_b_id] = travel_time
        loc_b.connections[location_a_id] = travel_time
    
    def sanitize_location_id(self, raw_input: str) -> str:
        """
        Převede libovolný vstup uživatele na validní location_id
        
        Například:
        - "Severní les" -> "severni_les"
        - "old castle" -> "old_castle"
        - "темный лес" -> "temny_les" (transliterace)
        """
        # Převeď na lowercase
        normalized = raw_input.lower().strip()
        
        # Nahraď mezery podtržítky
        normalized = normalized.replace(" ", "_")
        
        # Odstraň speciální znaky (ponechej jen a-z, 0-9, _)
        import re
        normalized = re.sub(r'[^a-z0-9_]', '', normalized)
        
        # Pokud je prázdné, vygeneruj náhodné ID
        if not normalized:
            normalized = f"location_{random.randint(1000, 9999)}"
        
        return normalized


# ========== HELPER FUNKCE PRO SMĚROVÉ CESTOVÁNÍ ==========

def get_directional_location_id(source_id: str, direction: str) -> str:
    """
    Vygeneruje ID pro lokaci ve směru od zdroje
    
    Args:
        source_id: ID současné lokace
        direction: 'north', 'south', 'east', 'west'
    
    Returns:
        ID nové lokace ve tvaru "source_north", "source_south" atd.
    """
    direction_map = {
        "north": "sever",
        "n": "sever",
        "south": "jih",
        "s": "jih",
        "east": "vychod",
        "e": "vychod",
        "west": "zapad",
        "w": "zapad"
    }
    
    direction_suffix = direction_map.get(direction.lower(), direction.lower())
    return f"{source_id}_{direction_suffix}"