"""
Open World Manager - Správa světa, cestování, PvP, táborů
NYNÍ S PROCEDURÁLNÍM GENEROVÁNÍM! ✨
"""

import json
import time
import random
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import asdict

from models.world import (
    Location, Camp, PlayerWorldState, LocationType, PvPZone, 
    Weather, LOCATIONS
)
from models.procedural_world import ProceduralWorldGenerator, get_directional_location_id


class WorldManager:
    """Hlavní manager pro open world systém s procedurálním generováním"""
    
    def __init__(
        self, 
        data_file: str = "data/world_state.json",
        locations_file: str = "data/generated_locations.json"
    ):
        self.data_file = data_file
        self.locations_file = locations_file
        
        # Lokace (načte se z world.py + vygenerované)
        self.locations: Dict[str, Location] = LOCATIONS.copy()
        
        # Hráči v světě
        self.player_states: Dict[int, PlayerWorldState] = {}
        
        # Tábory
        self.camps: Dict[str, Camp] = {}
        
        # Party systém
        self.parties: Dict[str, Set[int]] = {}  # {party_id: {player_ids}}
        self.player_parties: Dict[int, str] = {}  # {player_id: party_id}
        
        # 🌟 Procedurální generátor
        self.generator = ProceduralWorldGenerator(self.locations)
        
        # 🌟 Tracking vygenerovaných lokací
        self.generated_location_ids: Set[str] = set()
        
        # Načti data
        self.load()
        self.load_generated_locations()
    
    
    # ========== DATA PERSISTENCE ==========
    
    def save(self):
        """Ulož stav do JSON"""
        data = {
            "player_states": {
                str(pid): asdict(state) 
                for pid, state in self.player_states.items()
            },
            "camps": {
                cid: asdict(camp) 
                for cid, camp in self.camps.items()
            },
            "parties": {
                pid: list(members) 
                for pid, members in self.parties.items()
            },
            "player_parties": {
                str(pid): party_id 
                for pid, party_id in self.player_parties.items()
            }
        }
        
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Chyba při ukládání world state: {e}")
    
    
    def save_generated_locations(self):
        """🌟 Ulož vygenerované lokace do JSON"""
        generated_locs = {
            loc_id: {
                "id": loc.id,
                "name_cs": loc.name_cs,
                "name_en": loc.name_en,
                "type": loc.type.value,
                "pvp_zone": loc.pvp_zone.value,
                "description": loc.description,
                "connections": loc.connections,
                "has_shop": loc.has_shop,
                "has_healer": loc.has_healer,
                "has_bank": loc.has_bank,
                "has_trainer": loc.has_trainer,
                "has_quest_board": loc.has_quest_board,
                "has_inn": loc.has_inn,
                "resources": loc.resources,
                "weather": loc.weather.value,
                "visibility": loc.visibility,
                "allows_camping": loc.allows_camping,
                "allows_apparition": loc.allows_apparition,
                "spawn_point": loc.spawn_point
            }
            for loc_id, loc in self.locations.items()
            if loc_id in self.generated_location_ids
        }
        
        try:
            with open(self.locations_file, 'w', encoding='utf-8') as f:
                json.dump(generated_locs, f, indent=2, ensure_ascii=False)
            print(f"💾 Uloženo {len(generated_locs)} vygenerovaných lokací")
        except Exception as e:
            print(f"❌ Chyba při ukládání generated locations: {e}")
    
    
    def load_generated_locations(self):
        """🌟 Načti vygenerované lokace z JSON"""
        try:
            with open(self.locations_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for loc_id, loc_data in data.items():
                # Převeď enum values zpět
                loc = Location(
                    id=loc_data["id"],
                    name_cs=loc_data["name_cs"],
                    name_en=loc_data["name_en"],
                    type=LocationType(loc_data["type"]),
                    pvp_zone=PvPZone(loc_data["pvp_zone"]),
                    description=loc_data["description"],
                    connections=loc_data["connections"],
                    has_shop=loc_data["has_shop"],
                    has_healer=loc_data["has_healer"],
                    has_bank=loc_data["has_bank"],
                    has_trainer=loc_data["has_trainer"],
                    has_quest_board=loc_data["has_quest_board"],
                    has_inn=loc_data["has_inn"],
                    resources=loc_data["resources"],
                    weather=Weather(loc_data["weather"]),
                    visibility=loc_data["visibility"],
                    allows_camping=loc_data["allows_camping"],
                    allows_apparition=loc_data["allows_apparition"],
                    spawn_point=loc_data["spawn_point"]
                )
                
                self.locations[loc_id] = loc
                self.generated_location_ids.add(loc_id)
            
            print(f"✨ Načteno {len(data)} vygenerovaných lokací")
        
        except FileNotFoundError:
            print("📝 Žádné vygenerované lokace zatím neexistují")
        except Exception as e:
            print(f"⚠️ Chyba při načítání generated locations: {e}")
    
    
    def load(self):
        """Načti stav z JSON"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Player states
            for pid_str, state_dict in data.get("player_states", {}).items():
                pid = int(pid_str)
                # Konverze set z list
                if "owned_camps" in state_dict:
                    state_dict["owned_camps"] = state_dict["owned_camps"] or []
                
                self.player_states[pid] = PlayerWorldState(**state_dict)
            
            # Camps
            for cid, camp_dict in data.get("camps", {}).items():
                # Konverze sets z lists
                camp_dict["members"] = set(camp_dict.get("members", []))
                camp_dict["invited"] = set(camp_dict.get("invited", []))
                camp_dict["resting"] = set(camp_dict.get("resting", []))
                
                self.camps[cid] = Camp(**camp_dict)
            
            # Parties
            for pid, members_list in data.get("parties", {}).items():
                self.parties[pid] = set(members_list)
            
            # Player parties
            for pid_str, party_id in data.get("player_parties", {}).items():
                self.player_parties[int(pid_str)] = party_id
            
            print(f"✅ Načteno {len(self.player_states)} hráčů, {len(self.camps)} táborů")
        
        except FileNotFoundError:
            print("📝 Vytvářím nový world state")
        except Exception as e:
            print(f"⚠️ Chyba při načítání world state: {e}")
    
    
    # ========== PLAYER STATE ==========
    
    def get_player_state(self, player_id: int) -> PlayerWorldState:
        """Získej nebo vytvoř stav hráče"""
        if player_id not in self.player_states:
            self.player_states[player_id] = PlayerWorldState(player_id=player_id)
        return self.player_states[player_id]
    
    
    def get_player_location(self, player_id: int) -> Location:
        """Získej lokaci kde je hráč"""
        state = self.get_player_state(player_id)
        return self.locations.get(state.current_location, self.locations["hogsmeade"])
    
    
    # ========== TRAVEL SYSTEM ==========
    
    def can_travel(self, player_id: int) -> Tuple[bool, str]:
        """Může hráč cestovat?"""
        state = self.get_player_state(player_id)
        
        if state.traveling:
            return False, "Už cestuješ!"
        
        if state.current_camp:
            return False, "Nejdřív opusť tábor pomocí `/camp leave`"
        
        return True, "OK"
    
    
    def generate_or_get_location(
        self,
        location_id: str,
        source_location_id: Optional[str] = None
    ) -> Location:
        """
        🌟 PROCEDURÁLNÍ GENEROVÁNÍ!
        Pokud lokace existuje, vrátí ji. Pokud ne, vygeneruje novou.
        
        Args:
            location_id: ID lokace (může být cokoliv, např. "temny_les", "north")
            source_location_id: ID lokace odkud hráč přichází
        
        Returns:
            Location (buď existující nebo nově vygenerovaná)
        """
        # Sanitizuj ID
        clean_id = self.generator.sanitize_location_id(location_id)
        
        # Už existuje?
        if clean_id in self.locations:
            return self.locations[clean_id]
        
        # Vygeneruj novou! ✨
        print(f"🌟 Generuji novou lokaci: {clean_id}")
        
        new_location = self.generator.generate_location(
            location_id=clean_id,
            source_location_id=source_location_id
        )
        
        # Přidej do světa
        self.locations[clean_id] = new_location
        self.generated_location_ids.add(clean_id)
        
        # Vytvoř obousměrné spojení
        if source_location_id and source_location_id in self.locations:
            self.generator.connect_locations(
                source_location_id,
                clean_id,
                self.locations
            )
        
        # Ulož
        self.save_generated_locations()
        
        # Aktualizuj generátor s novou lokací
        self.generator.existing_locations = self.locations
        
        return new_location
    
    
    def start_travel(
        self, 
        player_id: int, 
        destination_input: str  # Nyní může být cokoliv!
    ) -> Tuple[bool, str, float]:
        """
        🌟 VYLEPŠENO! Začni cestování - nyní s procedurálním generováním!
        
        Args:
            player_id: ID hráče
            destination_input: Kam chce jít - může být:
                - ID existující lokace ("hogsmeade")
                - Název nového místa ("temný les")
                - Směr ("north", "south", "east", "west")
        
        Returns: (success, message, travel_time)
        """
        state = self.get_player_state(player_id)
        current_loc = self.get_player_location(player_id)
        
        # Kontroly
        can_travel, reason = self.can_travel(player_id)
        if not can_travel:
            return False, reason, 0.0
        
        # 🌟 Detekce směrového cestování
        direction_keywords = ["north", "n", "south", "s", "east", "e", "west", "w", 
                             "sever", "jih", "vychod", "zapad"]
        
        is_direction = destination_input.lower() in direction_keywords
        
        if is_direction:
            # Směrové cestování -> vygeneruj ID
            destination_id = get_directional_location_id(
                current_loc.id, 
                destination_input.lower()
            )
            
            # Vygeneruj nebo získej lokaci ve směru
            destination = self.generate_or_get_location(
                destination_id,
                source_location_id=current_loc.id
            )
            
        else:
            # Normální cestování
            # Zkus najít existující lokaci
            if destination_input in self.locations:
                destination = self.locations[destination_input]
                destination_id = destination_input
            else:
                # Neexistuje -> vygeneruj! ✨
                destination = self.generate_or_get_location(
                    destination_input,
                    source_location_id=current_loc.id
                )
                destination_id = destination.id
        
        # Už tam je?
        if state.current_location == destination_id:
            return False, "Už jsi v této lokaci!", 0.0
        
        # 🌟 Automatické vytvoření spojení pokud neexistuje
        if destination_id not in current_loc.connections:
            # Přidej spojení (procedurálně vygenerované spojení)
            self.generator.connect_locations(
                current_loc.id,
                destination_id,
                self.locations
            )
            self.save_generated_locations()  # Ulož změny
        
        # Spočítej čas (v minutách)
        base_time = current_loc.connections.get(destination_id, 15.0)  # Default 15 min
        
        # Weather může ovlivnit
        weather_modifiers = {
            Weather.CLEAR: 1.0,
            Weather.RAIN: 1.2,
            Weather.STORM: 1.5,
            Weather.FOG: 1.3,
            Weather.SNOW: 1.4,
            Weather.NIGHT: 1.1
        }
        
        time_modifier = weather_modifiers.get(current_loc.weather, 1.0)
        travel_time = base_time * time_modifier
        
        # Nastav cestování
        state.traveling = True
        state.travel_destination = destination_id
        state.travel_eta = time.time() + (travel_time * 60)  # Convert to seconds
        state.last_location = state.current_location
        
        self.save()
        
        weather_note = ""
        if current_loc.weather != Weather.CLEAR:
            weather_note = f"\n🌦️ Počasí ({current_loc.weather.value}) zpomaluje cestu o {int((time_modifier-1)*100)}%"
        
        # 🌟 Oznámení o objevení nové lokace
        discovery_note = ""
        if destination_id in self.generated_location_ids:
            discovery_note = "\n✨ **Objevuješ nové místo!**"
        
        return True, (
            f"🗺️ Cestuješ z **{current_loc.name_cs}** do **{destination.name_cs}**\n"
            f"⏱️ Čas: ~{travel_time:.0f} minut{weather_note}{discovery_note}"
        ), travel_time
    
    
    def check_travel_completion(self, player_id: int) -> Tuple[bool, Optional[str]]:
        """
        Zkontroluj jestli hráč dorazil
        Returns: (arrived, destination_name)
        """
        state = self.get_player_state(player_id)
        
        if not state.traveling:
            return False, None
        
        if time.time() >= state.travel_eta:
            # Dorazil!
            destination = self.locations[state.travel_destination]
            
            # Přesuň hráče
            old_loc = self.locations.get(state.current_location)
            if old_loc and player_id in old_loc.players_present:
                old_loc.players_present.remove(player_id)
            
            state.current_location = state.travel_destination
            state.traveling = False
            state.travel_destination = None
            state.travel_eta = 0.0
            
            # Přidej do nové lokace
            destination.players_present.add(player_id)
            
            self.save()
            return True, destination.name_cs
        
        return False, None
    
    
    # ========== PVP SYSTEM ==========
    
    def can_attack(
        self, 
        attacker_id: int, 
        target_id: int
    ) -> Tuple[bool, str]:
        """Může útočník zaútočit na cíl?"""
        attacker_state = self.get_player_state(attacker_id)
        target_state = self.get_player_state(target_id)
        
        # Kontrola lokace
        if attacker_state.current_location != target_state.current_location:
            return False, "Cíl není v této lokaci!"
        
        location = self.get_player_location(attacker_id)
        
        # PvP zóna kontrola
        if location.pvp_zone == PvPZone.SAFE:
            return False, f"🛡️ {location.name_cs} je bezpečná zóna! PvP není povoleno."
        
        if location.pvp_zone == PvPZone.CONSENSUAL:
            if not attacker_state.pvp_enabled or not target_state.pvp_enabled:
                return False, "⚠️ Oba hráči musí mít PvP zapnuté! Použij `/pvp toggle`"
        
        # V táboře?
        if target_state.current_camp:
            camp = self.camps.get(target_state.current_camp)
            if camp and camp.protections:
                return False, "🛡️ Cíl je chráněn táborovými kouzly!"
        
        # Cestuje?
        if attacker_state.traveling:
            return False, "Nemůžeš útočit během cestování!"
        
        if target_state.traveling:
            return False, "Cíl právě cestuje!"
        
        return True, "OK"
    
    
    def register_pvp_kill(self, killer_id: int, victim_id: int):
        """Zaznamenej PvP zabití"""
        killer_state = self.get_player_state(killer_id)
        victim_state = self.get_player_state(victim_id)
        
        killer_state.pvp_kills += 1
        victim_state.pvp_deaths += 1
        
        # Bounty systém
        # Pokud zabije 3+ hráčů za poslední 24h = wanted
        if killer_state.pvp_kills >= 3:
            killer_state.bounty = min(killer_state.bounty + 100, 1000)
        
        self.save()
    
    
    def get_bounty_list(self) -> List[Tuple[int, int, int]]:
        """
        Vrať seznam wanted hráčů
        Returns: [(player_id, bounty, kills)]
        """
        wanted = []
        for player_id, state in self.player_states.items():
            if state.bounty > 0:
                wanted.append((player_id, state.bounty, state.pvp_kills))
        
        return sorted(wanted, key=lambda x: x[1], reverse=True)
    
    
    def claim_bounty(self, hunter_id: int, target_id: int) -> Tuple[bool, int]:
        """
        Zaznamenej že hunter zabil wanted hráče
        Returns: (success, bounty_amount)
        """
        target_state = self.get_player_state(target_id)
        hunter_state = self.get_player_state(hunter_id)
        
        if target_state.bounty <= 0:
            return False, 0
        
        bounty = target_state.bounty
        target_state.bounty = 0
        hunter_state.gold += bounty
        
        self.save()
        return True, bounty
    
    
    # ========== CAMP SYSTEM ==========
    
    def can_create_camp(self, player_id: int) -> Tuple[bool, str]:
        """Může hráč vytvořit tábor?"""
        state = self.get_player_state(player_id)
        location = self.get_player_location(player_id)
        
        if not location.allows_camping:
            return False, f"{location.name_cs} neumožňuje tábory!"
        
        if state.traveling:
            return False, "Nemůžeš vytvořit tábor během cestování!"
        
        if len(state.owned_camps) >= 3:
            return False, "Můžeš mít max 3 aktivní tábory!"
        
        return True, "OK"
    
    
    def create_camp(
        self, 
        player_id: int, 
        camp_name: str
    ) -> Tuple[bool, str, Optional[Camp]]:
        """
        Vytvoř nový tábor
        Returns: (success, message, camp)
        """
        can_create, reason = self.can_create_camp(player_id)
        if not can_create:
            return False, reason, None
        
        state = self.get_player_state(player_id)
        
        # Generuj ID
        camp_id = f"camp_{player_id}_{int(time.time())}"
        
        # Vytvoř tábor
        camp = Camp(
            id=camp_id,
            owner_id=player_id,
            location_id=state.current_location,
            name=camp_name,
            created_at=time.time(),
            expires_at=time.time() + (24 * 3600)  # 24 hodin
        )
        
        # Přidej majitele do členů
        camp.members.add(player_id)
        
        # Ulož
        self.camps[camp_id] = camp
        state.owned_camps.append(camp_id)
        state.current_camp = camp_id
        
        # Přidej do lokace
        location = self.get_player_location(player_id)
        location.camps[camp_id] = camp
        
        self.save()
        
        return True, f"✅ Tábor **{camp_name}** vytvořen!", camp
    
    
    def enter_camp(self, player_id: int, camp_id: str) -> Tuple[bool, str]:
        """Vstup do tábora"""
        state = self.get_player_state(player_id)
        
        if camp_id not in self.camps:
            return False, "Tento tábor neexistuje!"
        
        camp = self.camps[camp_id]
        
        # Kontrola lokace
        if state.current_location != camp.location_id:
            return False, "Tábor není v této lokaci!"
        
        # Má přístup?
        if not camp.public and player_id not in camp.members and player_id not in camp.invited:
            return False, "Nemáš přístup do tohoto tábora!"
        
        # Vstup
        state.current_camp = camp_id
        camp.members.add(player_id)
        
        self.save()
        return True, f"✅ Vstoupil jsi do tábora **{camp.name}**"
    
    
    def leave_camp(self, player_id: int) -> Tuple[bool, str]:
        """Opusť tábor"""
        state = self.get_player_state(player_id)
        
        if not state.current_camp:
            return False, "Nejsi v žádném táboře!"
        
        camp = self.camps.get(state.current_camp)
        if camp:
            if player_id in camp.resting:
                camp.resting.remove(player_id)
        
        state.current_camp = None
        self.save()
        
        return True, "✅ Opustil jsi tábor"
    
    
    def protect_camp(
        self, 
        player_id: int, 
        spell_name: str, 
        duration: float = 3600
    ) -> Tuple[bool, str]:
        """Ochraň tábor kouzlem"""
        state = self.get_player_state(player_id)
        
        if not state.current_camp:
            return False, "Nejsi v žádném táboře!"
        
        camp = self.camps.get(state.current_camp)
        if not camp:
            return False, "Tábor neexistuje!"
        
        if camp.owner_id != player_id:
            return False, "Nejsi majitel tohoto tábora!"
        
        # Přidej ochranu
        camp.protections[spell_name] = time.time() + duration
        self.save()
        
        return True, f"🛡️ Tábor chráněn kouzlem **{spell_name}** na {duration/3600:.1f}h"
    
    
    def can_raid_camp(self, raider_id: int, camp_id: str) -> Tuple[bool, str]:
        """Může hráč napadnout tábor?"""
        raider_state = self.get_player_state(raider_id)
        
        if camp_id not in self.camps:
            return False, "Tábor neexistuje!"
        
        camp = self.camps[camp_id]
        
        # Je v lokaci?
        if raider_state.current_location != camp.location_id:
            return False, "Tábor není v této lokaci!"
        
        # Je vlastník?
        if camp.owner_id == raider_id:
            return False, "Nemůžeš napadnout vlastní tábor!"
        
        # Je člen?
        if raider_id in camp.members:
            return False, "Jsi člen tohoto tábora!"
        
        # Má ochranu?
        active_protections = []
        current_time = time.time()
        
        for spell, expires_at in list(camp.protections.items()):
            if expires_at > current_time:
                active_protections.append(spell)
            else:
                del camp.protections[spell]
        
        if active_protections:
            return False, f"🛡️ Tábor je chráněn: {', '.join(active_protections)}"
        
        return True, "OK"
    
    
    def raid_camp(
        self, 
        raider_id: int, 
        camp_id: str
    ) -> Tuple[bool, str, Dict[str, int]]:
        """
        Napadni tábor
        Returns: (success, message, loot)
        """
        can_raid, reason = self.can_raid_camp(raider_id, camp_id)
        if not can_raid:
            return False, reason, {}
        
        camp = self.camps[camp_id]
        
        # Loot 30% věcí ze skladu
        loot = {}
        for item, count in list(camp.storage.items()):
            stolen = max(1, int(count * 0.3))
            loot[item] = stolen
            camp.storage[item] -= stolen
            if camp.storage[item] <= 0:
                del camp.storage[item]
        
        self.save()
        return True, f"⚔️ Úspěšně jsi přepadl tábor **{camp.name}**!", loot
    
    
    # ========== PARTY SYSTEM ==========
    
    def create_party(self, leader_id: int) -> Tuple[bool, str, Optional[str]]:
        """Vytvoř party"""
        if leader_id in self.player_parties:
            return False, "Už jsi v party!", None
        
        party_id = f"party_{leader_id}_{int(time.time())}"
        self.parties[party_id] = {leader_id}
        self.player_parties[leader_id] = party_id
        
        self.save()
        return True, "✅ Party vytvořena!", party_id
    
    
    def invite_to_party(
        self, 
        inviter_id: int, 
        invitee_id: int
    ) -> Tuple[bool, str, Optional[str]]:
        """Pozvi hráče do party"""
        if inviter_id not in self.player_parties:
            return False, "Nejsi v žádné party!", None
        
        if invitee_id in self.player_parties:
            return False, "Hráč už je v party!", None
        
        party_id = self.player_parties[inviter_id]
        party = self.parties[party_id]
        
        if len(party) >= 5:
            return False, "Party je plná! (max 5 hráčů)", None
        
        return True, "✅ Pozvánka odeslána", party_id
    
    
    def join_party(self, player_id: int, party_id: str) -> Tuple[bool, str]:
        """Přidej se do party"""
        if player_id in self.player_parties:
            return False, "Už jsi v party!"
        
        if party_id not in self.parties:
            return False, "Party neexistuje!"
        
        party = self.parties[party_id]
        if len(party) >= 5:
            return False, "Party je plná!"
        
        party.add(player_id)
        self.player_parties[player_id] = party_id
        
        self.save()
        return True, "✅ Připojil ses do party!"
    
    
    def leave_party(self, player_id: int) -> Tuple[bool, str]:
        """Opusť party"""
        if player_id not in self.player_parties:
            return False, "Nejsi v žádné party!"
        
        party_id = self.player_parties[player_id]
        party = self.parties[party_id]
        
        party.remove(player_id)
        del self.player_parties[player_id]
        
        # Pokud je party prázdná, smaž ji
        if not party:
            del self.parties[party_id]
        
        self.save()
        return True, "✅ Opustil jsi party"
    
    
    def get_party_members(self, player_id: int) -> Optional[Set[int]]:
        """Získej členy party"""
        if player_id not in self.player_parties:
            return None
        
        party_id = self.player_parties[player_id]
        return self.parties.get(party_id)
    
    
    # ========== LOCATION QUERIES ==========
    
    def get_players_in_location(self, location_id: str) -> Set[int]:
        """Získej všechny hráče v lokaci"""
        players = set()
        for player_id, state in self.player_states.items():
            if state.current_location == location_id and not state.traveling:
                players.add(player_id)
        return players
    
    
    def get_camps_in_location(self, location_id: str) -> List[Camp]:
        """Získej všechny tábory v lokaci"""
        camps = []
        for camp in self.camps.values():
            if camp.location_id == location_id:
                # Zkontroluj expiraci
                if camp.expires_at > time.time():
                    camps.append(camp)
        return camps
    
    
    # ========== UTILITIES ==========
    
    def get_map_overview(self) -> str:
        """Vytvoř ASCII mapu"""
        lines = ["🗺️ **MAPA SVĚTA**\n"]
        
        for loc_id, loc in self.locations.items():
            # PvP ikona
            pvp_icons = {
                PvPZone.SAFE: "🛡️",
                PvPZone.CONSENSUAL: "⚠️",
                PvPZone.OPEN: "⚔️",
                PvPZone.FLAGGED: "🎯"
            }
            
            icon = pvp_icons.get(loc.pvp_zone, "")
            
            # Počet hráčů
            player_count = len(self.get_players_in_location(loc_id))
            player_text = f"👥 {player_count}" if player_count > 0 else ""
            
            # Services
            services = []
            if loc.has_shop:
                services.append("🏪")
            if loc.has_healer:
                services.append("💚")
            if loc.has_bank:
                services.append("🏦")
            
            services_text = "".join(services)
            
            lines.append(
                f"{icon} **{loc.name_cs}** {services_text} {player_text}\n"
                f"   _{loc.description}_"
            )
        
        return "\n".join(lines)
    
    
    def cleanup_expired_camps(self):
        """Vyčisti expirované tábory"""
        current_time = time.time()
        expired = []
        
        for camp_id, camp in self.camps.items():
            if camp.expires_at < current_time:
                expired.append(camp_id)
        
        for camp_id in expired:
            camp = self.camps[camp_id]
            
            # Odeber z player states
            for player_id, state in self.player_states.items():
                if camp_id in state.owned_camps:
                    state.owned_camps.remove(camp_id)
                if state.current_camp == camp_id:
                    state.current_camp = None
            
            # Odeber z lokace
            location = self.locations.get(camp.location_id)
            if location and camp_id in location.camps:
                del location.camps[camp_id]
            
            del self.camps[camp_id]
        
        if expired:
            print(f"🗑️ Vyčištěno {len(expired)} expirovaných táborů")
            self.save()
    
    
    # ========== PROCEDURÁLNÍ WORLD UTILITIES ==========
    
    def explore_random_direction(self, player_id: int) -> Tuple[bool, str]:
        """
        🌟 Prozkoumej náhodný směr - automatické generování!
        """
        directions = ["north", "south", "east", "west"]
        direction = random.choice(directions)
        
        success, message, travel_time = self.start_travel(player_id, direction)
        
        if success:
            return True, f"🧭 Vydáváš se na {direction}!\n{message}"
        else:
            return False, message
    
    
    def get_world_stats(self) -> Dict:
        """
        Získej statistiky světa
        """
        total_locations = len(self.locations)
        generated_locations = len(self.generated_location_ids)
        predefined_locations = total_locations - generated_locations
        
        # Typy lokací
        type_counts = {}
        for loc in self.locations.values():
            type_name = loc.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        # PvP zóny
        pvp_counts = {}
        for loc in self.locations.values():
            pvp_name = loc.pvp_zone.value
            pvp_counts[pvp_name] = pvp_counts.get(pvp_name, 0) + 1
        
        return {
            "total_locations": total_locations,
            "predefined": predefined_locations,
            "generated": generated_locations,
            "types": type_counts,
            "pvp_zones": pvp_counts,
            "total_players": len(self.player_states),
            "total_camps": len(self.camps)
        }
    
    
    def get_nearby_unexplored(self, player_id: int, radius: int = 1) -> List[str]:
        """
        🌟 Získej seznam neprozkoumaných směrů
        
        Args:
            radius: Jak daleko hledat (default 1 = přímí sousedé)
        
        Returns:
            Seznam směrů které ještě nejsou vygenerované
        """
        state = self.get_player_state(player_id)
        current_loc = self.locations[state.current_location]
        
        # Kontroluj všechny směry
        directions = ["north", "south", "east", "west"]
        unexplored = []
        
        for direction in directions:
            direction_id = get_directional_location_id(current_loc.id, direction)
            
            # Pokud neexistuje = neprozkoumaný
            if direction_id not in self.locations:
                unexplored.append(direction)
        
        return unexplored
    
    
    def get_exploration_summary(self, player_id: int) -> str:
        """
        Vytvoř přehled průzkumu pro hráče
        """
        state = self.get_player_state(player_id)
        current_loc = self.locations[state.current_location]
        
        lines = [f"🗺️ **Průzkum z: {current_loc.name_cs}**\n"]
        
        # Existující spojení
        if current_loc.connections:
            lines.append("**Známá místa:**")
            for conn_id in current_loc.connections.keys():
                conn_loc = self.locations.get(conn_id)
                if conn_loc:
                    is_generated = "✨" if conn_id in self.generated_location_ids else "📍"
                    lines.append(f"{is_generated} {conn_loc.name_cs}")
        
        # Neprozkoumaná místa
        unexplored = self.get_nearby_unexplored(player_id)
        if unexplored:
            lines.append("\n**Neprozkoumaná území:**")
            direction_cs = {
                "north": "🧭 Sever",
                "south": "🧭 Jih",
                "east": "🧭 Východ",
                "west": "🧭 Západ"
            }
            for direction in unexplored:
                lines.append(direction_cs.get(direction, direction))
        
        return "\n".join(lines)