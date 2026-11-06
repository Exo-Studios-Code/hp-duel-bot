"""
Player Model - Realistické tělo a stav kouzelníka
Žádné HP, pouze reálná zranění a následky
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum
import time
import json
import os
from typing import Tuple
from typing import Any
class BodyPart(Enum):
    """Části těla které mohou být zraněny"""
    HEAD = "head"
    TORSO = "torso"
    LEFT_ARM = "left_arm"
    RIGHT_ARM = "right_arm"
    LEFT_LEG = "left_leg"
    RIGHT_LEG = "right_leg"


class BodyPartState(Enum):
    """Stav části těla"""
    HEALTHY = "healthy"           # 100% funkčnost
    INJURED = "injured"           # 50-90% funkčnost
    SEVERELY_DAMAGED = "severe"   # 10-50% funkčnost
    DESTROYED = "destroyed"       # 0% funkčnost, ztraceno


class InjuryType(Enum):
    """Typy zranění"""
    CUT = "cut"
    DEEP_WOUND = "deep_wound"
    BURN = "burn"
    FRACTURE = "fracture"
    BROKEN_BONE = "broken_bone"
    INTERNAL_BLEEDING = "internal_bleeding"
    CONCUSSION = "concussion"
    SEVERED = "severed"
    CURSED = "cursed"  # Magické zranění
    PARALYSIS = "paralysis"


class Condition(Enum):
    """Celkové stavy postavy"""
    BLEEDING = "bleeding"
    HEAVY_BLEEDING = "heavy_bleeding"
    PAIN = "pain"
    SEVERE_PAIN = "severe_pain"
    STUNNED = "stunned"
    PARALYZED = "paralyzed"
    UNCONSCIOUS = "unconscious"
    BLIND = "blind"
    DEAF = "deaf"
    DISARMED = "disarmed"
    SHOCKED = "shocked"
    DYING = "dying"
    DEAD = "dead"
    
    # Nové stavy pro magické efekty
    FROZEN = "frozen"              # Zmrazen (Glacius, Zmrazovací kouzlo)
    IMMOBILIZED = "immobilized"    # Znehybněn (Immobulus, Petrificus Totalus)
    PETRIFIED = "petrified"        # Zkamenělý (Petrificus Totalus)
    CONFUNDED = "confunded"        # Zmaten (Confundo)
    SILENCED = "silenced"          # Umlčen (Silencio)
    INVISIBLE = "invisible"        # Neviditelný
    LEVITATING = "levitating"      # Levituje
    TRANSFORMED = "transformed"    # Transformován
    CURSED = "cursed"             # Pod kletbou
    CONTROLLED = "controlled"      # Kontrolován (Imperius)
    MEMORY_WIPED = "memory_wiped"  # Paměť smazána (Obliviate)


@dataclass
class StatusEffect:
    """Dočasný magický efekt"""
    effect_type: Condition
    duration: float  # sekund zbývajících
    severity: int  # 1-10
    caused_by: str  # které kouzlo
    description: str
    timestamp: float = field(default_factory=time.time)
    
    def update(self, delta_time: float) -> bool:
        """
        Aktualizuje efekt v čase
        Returns: True pokud efekt stále trvá, False pokud vypršel
        """
        self.duration -= delta_time
        return self.duration > 0


@dataclass
class Injury:
    """Konkrétní zranění"""
    type: InjuryType
    body_part: BodyPart
    severity: int  # 1-10
    bleeding_rate: float = 0.0  # ml krve/s (pokud krvácí)
    pain_level: int = 0  # 1-10
    timestamp: float = field(default_factory=time.time)
    treatable: bool = True
    treated: bool = False
    description: str = ""
    caused_by: str = ""  # Které kouzlo to způsobilo
    
    def get_functional_penalty(self) -> float:
        """Vrací % snížení funkčnosti (0.0 = žádné, 1.0 = úplné)"""
        base_penalty = self.severity / 10.0
        
        if self.type == InjuryType.SEVERED:
            return 1.0
        elif self.type == InjuryType.BROKEN_BONE:
            return 0.8
        elif self.type == InjuryType.FRACTURE:
            return 0.5
        elif self.type == InjuryType.DEEP_WOUND:
            return 0.4
        
        return base_penalty


@dataclass
class BodyPartStatus:
    """Stav konkrétní části těla"""
    part: BodyPart
    state: BodyPartState = BodyPartState.HEALTHY
    injuries: List[Injury] = field(default_factory=list)
    functionality: float = 1.0  # 0.0 - 1.0
    
    def add_injury(self, injury: Injury):
        """Přidá zranění a aktualizuje stav"""
        self.injuries.append(injury)
        self._update_state()
    
    def _update_state(self):
        """Aktualizuje stav na základě zranění"""
        total_penalty = sum(inj.get_functional_penalty() for inj in self.injuries)
        self.functionality = max(0.0, 1.0 - total_penalty)
        
        if self.functionality == 0:
            self.state = BodyPartState.DESTROYED
        elif self.functionality < 0.1:
            self.state = BodyPartState.SEVERELY_DAMAGED
        elif self.functionality < 0.9:
            self.state = BodyPartState.INJURED
        else:
            self.state = BodyPartState.HEALTHY
    
    def get_total_bleeding(self) -> float:
        """Celková rychlost krvácení z této části"""
        return sum(inj.bleeding_rate for inj in self.injuries if not inj.treated)
    
    def get_total_pain(self) -> int:
        """Celková bolest z této části"""
        return min(10, sum(inj.pain_level for inj in self.injuries))


@dataclass
class Player:
    """Hráč - kouzelník ve hře"""
    
    # Základní info
    discord_id: int
    name: str
    
    # Fyzické vlastnosti
    hair_color: str = "brown"  # barva vlasů
    hair_length: float = 10.0  # délka vlasů v cm
    eye_color: str = "brown"  # barva očí
    height: float = 170.0  # výška v cm
    has_antlers: bool = False  # má parohy?
    has_tail: bool = False  # má ocas?
    has_wings: bool = False  # má křídla?
    size_multiplier: float = 1.0  # modifikátor velikosti (Engorgio/Reducio)
    
    # Tělo
    body: Dict[BodyPart, BodyPartStatus] = field(default_factory=dict)
    
    # Celkový stav
    conditions: Set[Condition] = field(default_factory=set)
    status_effects: List[StatusEffect] = field(default_factory=list)  # Nové!
    consciousness: float = 100.0  # 0 = mrtvý, 100 = plně při vědomí
    blood_volume: float = 5000.0  # ml (normál: 5000ml)
    
    # Kouzla
    known_spells: Set[str] = field(default_factory=set)  # spell_id
    learning_spells: Dict[str, float] = field(default_factory=dict)  # spell_id: time_remaining
    spell_cooldowns: Dict[str, float] = field(default_factory=dict)  # spell_id: end_time
    
    # Bojový stav
    wand_hand: BodyPart = BodyPart.RIGHT_ARM
    has_wand: bool = True
    in_combat: bool = False
    last_spell_time: float = 0.0
    
    # Statistiky
    total_duels: int = 0
    duels_won: int = 0
    enemies_killed: int = 0
    times_died: int = 0
    reputation: int = 0
    dark_magic_uses: int = 0
    
    # Utility tracking
    utility_uses: Dict[str, int] = field(default_factory=dict)  # spell_id: počet použití
    
    # 🩸 Discord logging
    _was_critical_blood: bool = False  # Tracking pro log kritického stavu
    _discord_logger: Optional[Any] = None  # Discord logger instance (Optional pro avoid circular import)
    
    def __post_init__(self):
        """Inicializace těla"""
        if not self.body:
            for part in BodyPart:
                self.body[part] = BodyPartStatus(part=part)
    
    def set_discord_logger(self, logger):
        """
        Nastaví Discord logger pro automatické logování
        
        Args:
            logger: Instance DiscordLogger
        """
        self._discord_logger = logger
    
    # ========== ZRANĚNÍ A STAV ==========
    
    def take_damage(self, injury: Injury):
        """Přidá zranění k části těla"""
        body_part_status = self.body[injury.body_part]
        body_part_status.add_injury(injury)
        
        # Aktualizuj celkový stav
        self._update_conditions()
        
        # Speciální efekty podle typu
        if injury.type == InjuryType.SEVERED:
            if injury.body_part == self.wand_hand:
                self.has_wand = False
        
        # Bolest může způsobit šok
        if injury.pain_level >= 8:
            self.conditions.add(Condition.SHOCKED)
    
    def add_status_effect(self, effect: StatusEffect):
        """Přidá dočasný magický efekt"""
        self.status_effects.append(effect)
        self.conditions.add(effect.effect_type)
    
    def remove_status_effect(self, effect_type: Condition):
        """Odstraní všechny efekty daného typu"""
        self.status_effects = [e for e in self.status_effects if e.effect_type != effect_type]
        
        # Pokud už žádný takový efekt není, odstraň condition
        if not any(e.effect_type == effect_type for e in self.status_effects):
            self.conditions.discard(effect_type)
    
    def _update_conditions(self):
        """Aktualizuje celkové stavy na základě zranění"""
        # Krvácení
        total_bleeding = sum(bp.get_total_bleeding() for bp in self.body.values())
        if total_bleeding > 10:
            self.conditions.add(Condition.HEAVY_BLEEDING)
        elif total_bleeding > 2:
            self.conditions.add(Condition.BLEEDING)
        else:
            self.conditions.discard(Condition.BLEEDING)
            self.conditions.discard(Condition.HEAVY_BLEEDING)
        
        # Bolest
        total_pain = sum(bp.get_total_pain() for bp in self.body.values())
        if total_pain >= 20:
            self.conditions.add(Condition.SEVERE_PAIN)
        elif total_pain >= 10:
            self.conditions.add(Condition.PAIN)
        else:
            self.conditions.discard(Condition.PAIN)
            self.conditions.discard(Condition.SEVERE_PAIN)
        
        # Vědomí
        if self.consciousness <= 0:
            self.conditions.add(Condition.UNCONSCIOUS)
            self.conditions.add(Condition.DEAD)
        elif self.consciousness < 30:
            self.conditions.add(Condition.DYING)
        elif self.consciousness < 50:
            self.conditions.add(Condition.UNCONSCIOUS)
        
        # Hlava
        head = self.body[BodyPart.HEAD]
        if head.state == BodyPartState.DESTROYED:
            self.conditions.add(Condition.DEAD)
        
        # Trup
        torso = self.body[BodyPart.TORSO]
        if torso.state == BodyPartState.DESTROYED:
            self.conditions.add(Condition.DEAD)
    
    def update(self, delta_time: float):
        """
        Aktualizuje stav hráče v čase
        delta_time v sekundách
        """
        # Krvácení
        if Condition.BLEEDING in self.conditions or Condition.HEAVY_BLEEDING in self.conditions:
            bleeding_rate = sum(bp.get_total_bleeding() for bp in self.body.values())
            blood_loss = bleeding_rate * delta_time * 5.0  # 5x rychlejší krvácení pro realističtější combat
            self.blood_volume -= blood_loss
            
            # Ztráta krve ovlivňuje vědomí
            blood_pct = self.blood_volume / 5000.0
            if blood_pct < 0.7:
                consciousness_loss = (0.7 - blood_pct) * 20 * delta_time
                self.consciousness -= consciousness_loss
        
        # Aktualizace statusových efektů
        expired_effects = []
        for effect in self.status_effects:
            if not effect.update(delta_time):
                expired_effects.append(effect)
        
        # Odstraň vypršelé efekty
        for effect in expired_effects:
            self.remove_status_effect(effect.effect_type)
        
        self._update_conditions()
        
        # 🩸 Kontrola kritického krevního stavu pro Discord logging
        self._check_blood_status_async()
    
    def _check_blood_status_async(self):
        """
        🩸 Kontrola krevního stavu a volání Discord loggeru
        Volá se v update() - neblokující (spustí async task)
        """
        if not self._discord_logger:
            return  # Žádný logger = skip
        
        CRITICAL_THRESHOLD = 2500.0  # ml
        is_critical_now = self.blood_volume < CRITICAL_THRESHOLD
        
        # Změnil se stav na kritický?
        if is_critical_now and not self._was_critical_blood:
            # Nově kritický stav!
            self._was_critical_blood = True
            
            # Získej seznam zranění
            injuries = []
            for part_status in self.body.values():
                for injury in part_status.injuries:
                    injuries.append(
                        f"{injury.description} ({part_status.part.value}, {injury.severity}/10)"
                    )
            
            # Spusť async log (bez čekání)
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # V běžícím event loopu - schedule coroutine
                    asyncio.create_task(
                        self._discord_logger.log_critical_blood(
                            player_id=self.discord_id,
                            player_name=self.name,
                            blood_ml=self.blood_volume,
                            injuries=injuries,
                            consciousness=self.consciousness
                        )
                    )
                else:
                    # Není event loop - spustíme nový
                    loop.run_until_complete(
                        self._discord_logger.log_critical_blood(
                            player_id=self.discord_id,
                            player_name=self.name,
                            blood_ml=self.blood_volume,
                            injuries=injuries,
                            consciousness=self.consciousness
                        )
                    )
            except Exception as e:
                print(f"⚠️ Chyba při logování critical blood: {e}")
        
        # Změnil se stav zpět na normální?
        elif not is_critical_now and self._was_critical_blood:
            # Zotavil se!
            self._was_critical_blood = False
            
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(
                        self._discord_logger.log_blood_recovered(
                            player_id=self.discord_id,
                            player_name=self.name,
                            blood_ml=self.blood_volume
                        )
                    )
                else:
                    loop.run_until_complete(
                        self._discord_logger.log_blood_recovered(
                            player_id=self.discord_id,
                            player_name=self.name,
                            blood_ml=self.blood_volume
                        )
                    )
            except Exception as e:
                print(f"⚠️ Chyba při logování blood recovery: {e}")
    
    # ========== SESÍLÁNÍ KOUZEL ==========
    
    def can_cast_spell(self) -> Tuple[bool, str]:
        """Může hráč obecně sesílat kouzla?"""
        if not self.has_wand:
            return False, "Nemáte hůlku!"
        
        if Condition.DISARMED in self.conditions:
            return False, "Jste odzbrojeni - nemáte hůlku!"
        
        wand_arm = self.body[self.wand_hand]
        if wand_arm.functionality < 0.3:
            return False, f"Vaše {self.wand_hand.value} je příliš poškozená!"
        
        if Condition.UNCONSCIOUS in self.conditions:
            return False, "Jste v bezvědomí!"
        
        if Condition.DEAD in self.conditions:
            return False, "Jste mrtví!"
        
        if Condition.FROZEN in self.conditions:
            return False, "Jste zmrazeni!"
        
        if Condition.PETRIFIED in self.conditions:
            return False, "Jste zkamenělí!"
        
        if Condition.PARALYZED in self.conditions:
            return False, "Jste paralyzováni!"
        
        if Condition.SILENCED in self.conditions:
            return False, "Jste umlčeni - nemůžete vyslovit zaklínadlo!"
        
        return True, ""
    
    def can_cast_spell_now(self, spell_id: str) -> Tuple[bool, str]:
        """Může hráč teď seslat konkrétní kouzlo?"""
        # Základní kontrola
        can_cast, reason = self.can_cast_spell()
        if not can_cast:
            return False, reason
        
        # Zná kouzlo?
        if spell_id not in self.known_spells:
            return False, f"Neznáte kouzlo {spell_id}!"
        
        # Cooldown
        if spell_id in self.spell_cooldowns:
            cooldown_end = self.spell_cooldowns[spell_id]
            if time.time() < cooldown_end:
                remaining = cooldown_end - time.time()
                return False, f"Kouzlo má cooldown ještě {remaining:.1f}s"
        
        return True, ""
    
    def cast_spell(self, spell_id: str, cooldown: int):
        """Zaznamená seslání kouzla"""
        self.last_spell_time = time.time()
        
        if cooldown > 0:
            self.spell_cooldowns[spell_id] = time.time() + cooldown
    
    def use_utility_spell(self, spell_id: str):
        """Zaznamená použití utility kouzla"""
        if spell_id not in self.utility_uses:
            self.utility_uses[spell_id] = 0
        self.utility_uses[spell_id] += 1
    
    def get_spell_accuracy_modifier(self) -> float:
        """
        Vrací modifikátor přesnosti 0.0-1.0
        Ovlivněno zraněními a stavy
        """
        modifier = 1.0
        
        # Ruka s hůlkou
        wand_arm = self.body[self.wand_hand]
        modifier *= wand_arm.functionality
        
        # Bolest
        if Condition.SEVERE_PAIN in self.conditions:
            modifier *= 0.5
        elif Condition.PAIN in self.conditions:
            modifier *= 0.7
        
        # Šok
        if Condition.SHOCKED in self.conditions:
            modifier *= 0.6
        
        # Zmatení
        if Condition.CONFUNDED in self.conditions:
            modifier *= 0.4
        
        # Vědomí
        consciousness_factor = self.consciousness / 100.0
        modifier *= consciousness_factor
        
        return max(0.0, min(1.0, modifier))
    
    def get_movement_ability(self) -> float:
        """
        Vrací schopnost pohybu 0.0-1.0
        Ovlivněno zraněními nohou a stavů
        """
        if Condition.FROZEN in self.conditions:
            return 0.0
        
        if Condition.PETRIFIED in self.conditions:
            return 0.0
        
        if Condition.IMMOBILIZED in self.conditions:
            return 0.0
        
        left_leg = self.body[BodyPart.LEFT_LEG]
        right_leg = self.body[BodyPart.RIGHT_LEG]
        
        avg_leg_function = (left_leg.functionality + right_leg.functionality) / 2
        
        return avg_leg_function
    
    # ========== UČENÍ KOUZEL ==========
    
    def start_learning_spell(self, spell_id: str, learning_time_hours: float):
        """Začne se učit kouzlo"""
        self.learning_spells[spell_id] = learning_time_hours * 3600  # převod na sekundy
    
    def update_learning(self, delta_time: float):
        """Aktualizuje učení kouzel"""
        learned = []
        
        for spell_id, time_remaining in list(self.learning_spells.items()):
            time_remaining -= delta_time
            
            if time_remaining <= 0:
                self.known_spells.add(spell_id)
                learned.append(spell_id)
            else:
                self.learning_spells[spell_id] = time_remaining
        
        for spell_id in learned:
            del self.learning_spells[spell_id]
        
        return learned
    
    def knows_spell(self, spell_id: str) -> bool:
        """Zná hráč dané kouzlo?"""
        return spell_id in self.known_spells
    
    # ========== SMRT A OŽIVENÍ ==========
    
    def is_alive(self) -> bool:
        """Je hráč naživu?"""
        return Condition.DEAD not in self.conditions
    
    def die(self, cause: str = ""):
        """Smrt hráče"""
        self.conditions.add(Condition.DEAD)
        self.consciousness = 0
        self.times_died += 1
    
    def revive(self):
        """Oživení - plný reset"""
        # Reset těla
        for part in BodyPart:
            self.body[part] = BodyPartStatus(part=part)
        
        # Reset stavů
        self.conditions.clear()
        self.status_effects.clear()
        self.consciousness = 100.0
        self.blood_volume = 5000.0
        
        # Kouzla se NEOBNOVUJÍ!
        self.known_spells.clear()
        self.learning_spells.clear()
        
        # Statistiky zůstávají
        # Reputace se NEZACHOVÁVÁ
        self.reputation = 0
    
    # ========== STATUS A INFO ==========
    
    def get_status_summary(self) -> str:
        """Textový přehled stavu hráče"""
        lines = [
            f"👤 **{self.name}**",
            f"🧠 Vědomí: {self.consciousness:.1f}%",
            f"🩸 Krev: {self.blood_volume:.0f}ml / 5000ml ({self.blood_volume/50:.1f}%)",
        ]
        
        # Stavy
        if self.conditions:
            conditions_text = ", ".join([c.value for c in self.conditions])
            lines.append(f"⚠️ Stavy: {conditions_text}")
        
        # Aktivní efekty
        if self.status_effects:
            lines.append("\n**Aktivní efekty:**")
            for effect in self.status_effects:
                lines.append(f"  • {effect.description} ({effect.duration:.1f}s)")
        
        # Části těla
        lines.append("\n**Tělo:**")
        for part, status in self.body.items():
            emoji = self._get_body_part_emoji(part)
            state_emoji = self._get_state_emoji(status.state)
            functionality_pct = status.functionality * 100
            
            line = f"{emoji} {part.value}: {state_emoji} {functionality_pct:.0f}%"
            
            if status.injuries:
                injury_count = len(status.injuries)
                line += f" ({injury_count} zranění)"
            
            lines.append(line)
        
        # Hůlka
        wand_status = "✅" if self.has_wand else "❌"
        lines.append(f"\n🪄 Hůlka: {wand_status}")
        
        # Přesnost
        accuracy = self.get_spell_accuracy_modifier() * 100
        lines.append(f"🎯 Přesnost sesílání: {accuracy:.0f}%")
        
        return "\n".join(lines)
    
    def _get_body_part_emoji(self, part: BodyPart) -> str:
        emojis = {
            BodyPart.HEAD: "🧠",
            BodyPart.TORSO: "🫁",
            BodyPart.LEFT_ARM: "💪",
            BodyPart.RIGHT_ARM: "💪",
            BodyPart.LEFT_LEG: "🦵",
            BodyPart.RIGHT_LEG: "🦵",
        }
        return emojis.get(part, "❓")
    
    def _get_state_emoji(self, state: BodyPartState) -> str:
        emojis = {
            BodyPartState.HEALTHY: "✅",
            BodyPartState.INJURED: "🟡",
            BodyPartState.SEVERELY_DAMAGED: "🔴",
            BodyPartState.DESTROYED: "💀",
        }
        return emojis.get(state, "❓")
    
    # ========== PERSISTENCE ==========
    
    def to_dict(self) -> dict:
        """Serializace do dict pro uložení"""
        return {
            "discord_id": self.discord_id,
            "name": self.name,
            "body": {
                part.value: {
                    "state": status.state.value,
                    "functionality": status.functionality,
                    "injuries": [
                        {
                            "type": inj.type.value,
                            "body_part": inj.body_part.value,
                            "severity": inj.severity,
                            "bleeding_rate": inj.bleeding_rate,
                            "pain_level": inj.pain_level,
                            "treated": inj.treated,
                            "description": inj.description,
                            "caused_by": inj.caused_by,
                        }
                        for inj in status.injuries
                    ]
                }
                for part, status in self.body.items()
            },
            "conditions": [c.value for c in self.conditions],
            "status_effects": [
                {
                    "effect_type": e.effect_type.value,
                    "duration": e.duration,
                    "severity": e.severity,
                    "caused_by": e.caused_by,
                    "description": e.description,
                }
                for e in self.status_effects
            ],
            "consciousness": self.consciousness,
            "blood_volume": self.blood_volume,
            "known_spells": list(self.known_spells),
            "learning_spells": self.learning_spells,
            "wand_hand": self.wand_hand.value,
            "has_wand": self.has_wand,
            "stats": {
                "total_duels": self.total_duels,
                "duels_won": self.duels_won,
                "enemies_killed": self.enemies_killed,
                "times_died": self.times_died,
                "reputation": self.reputation,
                "dark_magic_uses": self.dark_magic_uses,
            },
            "utility_uses": self.utility_uses,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Player':
        """Deserializace z dict"""
        player = cls(
            discord_id=data["discord_id"],
            name=data["name"],
        )
        
        # Obnovit tělo
        for part_str, part_data in data["body"].items():
            part = BodyPart(part_str)
            status = BodyPartStatus(
                part=part,
                state=BodyPartState(part_data["state"]),
                functionality=part_data["functionality"]
            )
            
            for inj_data in part_data["injuries"]:
                injury = Injury(
                    type=InjuryType(inj_data["type"]),
                    body_part=BodyPart(inj_data["body_part"]),
                    severity=inj_data["severity"],
                    bleeding_rate=inj_data["bleeding_rate"],
                    pain_level=inj_data["pain_level"],
                    treated=inj_data["treated"],
                    description=inj_data["description"],
                    caused_by=inj_data["caused_by"],
                )
                status.injuries.append(injury)
            
            player.body[part] = status
        
        # Obnovit stavy
        player.conditions = {Condition(c) for c in data["conditions"]}
        
        # Obnovit statusové efekty
        if "status_effects" in data:
            for effect_data in data["status_effects"]:
                effect = StatusEffect(
                    effect_type=Condition(effect_data["effect_type"]),
                    duration=effect_data["duration"],
                    severity=effect_data["severity"],
                    caused_by=effect_data["caused_by"],
                    description=effect_data["description"],
                )
                player.status_effects.append(effect)
        
        player.consciousness = data["consciousness"]
        player.blood_volume = data["blood_volume"]
        player.known_spells = set(data["known_spells"])
        player.learning_spells = data["learning_spells"]
        player.wand_hand = BodyPart(data["wand_hand"])
        player.has_wand = data["has_wand"]
        
        # Statistiky
        stats = data["stats"]
        player.total_duels = stats["total_duels"]
        player.duels_won = stats["duels_won"]
        player.enemies_killed = stats["enemies_killed"]
        player.times_died = stats["times_died"]
        player.reputation = stats["reputation"]
        player.dark_magic_uses = stats["dark_magic_uses"]
        
        # Utility uses
        if "utility_uses" in data:
            player.utility_uses = data["utility_uses"]
        
        return player


# ========== DATABÁZE HRÁČŮ ==========


class PlayerDatabase:
    """Správa hráčských dat"""
    
    def __init__(self, filepath: str = None):
        # 🔧 Automatická správná cesta (Windows/Linux kompatibilní)
        if filepath is None:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(BASE_DIR, "data", "players.json")
        
        self.filepath = filepath
        self.players: Dict[int, Player] = {}
        self.load()
    
    def load(self):
        """Načte hráče ze souboru"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for player_data in data:
                    player = Player.from_dict(player_data)
                    self.players[player.discord_id] = player
            print(f"✅ Načteno {len(self.players)} hráčů")
        
        except FileNotFoundError:
            print("ℹ️ Soubor hráčů neexistuje, vytváří se nový")
            self.players = {}
        
        except Exception as e:
            print(f"❌ Chyba při načítání hráčů: {e}")
            self.players = {}
    
    def save(self):
        """Uloží hráče do souboru"""
        try:
            # 🔧 vytvoří složku automaticky
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

            data = [player.to_dict() for player in self.players.values()]
            
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"❌ Chyba při ukládání: {e}")
    
    def get_or_create_player(self, discord_id: int, name: str) -> Player:
        """Získá nebo vytvoří hráče"""
        if discord_id not in self.players:
            player = Player(discord_id=discord_id, name=name)
            
            # 🔥 základní kouzla
            player.known_spells = {"lumos", "nox", "alohomora"}
            
            self.players[discord_id] = player
            self.save()
        
        return self.players[discord_id]
    
    def get_player(self, discord_id: int) -> Optional[Player]:
        """Získá hráče pokud existuje"""
        return self.players.get(discord_id)