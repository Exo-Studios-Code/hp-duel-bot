"""
Combat System - Kompletní realistické implementace VŠECH kouzel
Podporuje všechny kategorie kouzel s detailními efekty
"""

import random
import time
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum

from models.player import (
    Player, Injury, InjuryType, BodyPart, Condition,
    BodyPartState, StatusEffect
)


class SpellResult(Enum):
    """Výsledek sesílání kouzla"""
    HIT = "hit"
    MISS = "miss"
    BLOCKED = "blocked"
    DODGED = "dodged"
    REFLECTED = "reflected"
    FAILED = "failed"
    SUCCESS = "success"


class CombatAction(Enum):
    """Akce v souboji"""
    ATTACK = "attack"
    DEFEND = "defend"
    DODGE = "dodge"
    WAIT = "wait"
    COMBO = "combo"
    HEAL = "heal"  # Pro léčení během souboje


@dataclass
class SpellCast:
    """Seslané kouzlo"""
    caster: Player
    spell_id: str
    spell_data: dict
    target: Player
    timestamp: float = field(default_factory=time.time)
    action_type: CombatAction = CombatAction.ATTACK


@dataclass
class UnbreakableVow:
    """
    Neporušitelný Slib - magická přísaha s povinností smrti při porušení
    
    Vyžaduje tři osoby:
    - vow_maker: Osoba, která přísahá (a zemře při porušení)
    - vow_recipient: Osoba, které se přísahá
    - binder: Svědek, který magicky spojuje slib
    """
    vow_id: str
    vow_maker: Player  # Kdo přísahá (zemře při porušení)
    vow_recipient: Player  # Komu se přísahá
    binder: Player  # Svědek provádějící rituál
    
    # Konkrétní podmínky slibu
    vow_text: str  # Přesný text slibu
    conditions: List[str] = field(default_factory=list)  # Seznam podmínek
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    is_active: bool = True
    violation_detected: bool = False
    violation_reason: Optional[str] = None
    
    def check_violation(self, action: str, context: dict) -> bool:
        """
        Kontrola, zda akce porušuje slib
        
        Args:
            action: Popis akce (např. "attacked_player", "used_spell", "refused_order")
            context: Kontext akce (kdo, co, kde, proč)
        
        Returns:
            True pokud akce porušuje slib
        """
        if not self.is_active:
            return False
        
        # Kontroluj každou podmínku
        for condition in self.conditions:
            if self._check_condition_violation(condition, action, context):
                self.violation_detected = True
                self.violation_reason = f"Porušení podmínky: {condition} (akce: {action})"
                return True
        
        return False
    
    def _check_condition_violation(self, condition: str, action: str, context: dict) -> bool:
        """Kontrola jedné podmínky slibu"""
        condition_lower = condition.lower()
        action_lower = action.lower()
        
        # Příklady podmínek:
        # "never_harm:player_name" - Nikdy neublížit konkrétnímu hráči
        if condition_lower.startswith("never_harm:"):
            target_name = condition.split(":")[1]
            if action_lower == "attacked_player" and context.get("target_name") == target_name:
                return True
        
        # "always_protect:player_name" - Vždy chránit konkrétního hráče
        elif condition_lower.startswith("always_protect:"):
            target_name = condition.split(":")[1]
            if action_lower == "refused_protection" and context.get("target_name") == target_name:
                return True
        
        # "never_reveal:secret" - Nikdy neprozradit tajemství
        elif condition_lower.startswith("never_reveal:"):
            secret = condition.split(":")[1]
            if action_lower == "revealed_secret" and context.get("secret") == secret:
                return True
        
        # "complete_task:task_name" - Dokončit konkrétní úkol
        elif condition_lower.startswith("complete_task:"):
            task = condition.split(":")[1]
            if action_lower == "failed_task" and context.get("task") == task:
                return True
        
        # "never_use_spell:spell_id" - Nikdy nepoužít konkrétní kouzlo
        elif condition_lower.startswith("never_use_spell:"):
            spell_id = condition.split(":")[1]
            if action_lower == "used_spell" and context.get("spell_id") == spell_id:
                return True
        
        return False
    
    def execute_death_penalty(self) -> str:
        """Zabije osobu, která porušila slib"""
        if self.violation_detected and self.is_active:
            self.vow_maker.die(f"Porušení Neporušitelného Slibu: {self.violation_reason}")
            self.is_active = False
            return f"💀 {self.vow_maker.name} zemřel za porušení Neporušitelného Slibu! Důvod: {self.violation_reason}"
        return ""


@dataclass
class CombatTurn:
    """Jeden tah souboje"""
    turn_number: int
    player1_action: Optional[SpellCast] = None
    player2_action: Optional[SpellCast] = None
    results: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


class DuelState(Enum):
    """Stav souboje"""
    WAITING = "waiting"
    PREPARING = "preparing"
    ACTIVE = "active"
    FINISHED = "finished"


@dataclass
class Duel:
    """Souboj mezi dvěma hráči"""
    duel_id: str
    player1: Player
    player2: Player
    state: DuelState = DuelState.WAITING
    turns: List[CombatTurn] = field(default_factory=list)
    current_turn: int = 0
    winner: Optional[Player] = None
    start_time: float = 0.0
    end_time: float = 0.0
    
    def start(self):
        """Začátek souboje"""
        self.state = DuelState.ACTIVE
        self.start_time = time.time()
        self.player1.in_combat = True
        self.player2.in_combat = True
    
    def end(self, winner: Player):
        """Konec souboje"""
        self.state = DuelState.FINISHED
        self.end_time = time.time()
        self.winner = winner
        self.player1.in_combat = False
        self.player2.in_combat = False
        
        winner.duels_won += 1
        winner.total_duels += 1
        
        loser = self.player2 if winner == self.player1 else self.player1
        loser.total_duels += 1
        
        if not loser.is_alive():
            winner.enemies_killed += 1


class CombatEngine:
    """Jádro soubojového systému s kompletními implementacemi VŠECH kouzel"""
    
    def __init__(self, spell_database: dict):
        self.spells = spell_database
        self.active_duels: Dict[str, Duel] = {}
        self.active_vows: Dict[str, UnbreakableVow] = {}  # Správa Neporušitelných slibů
    
    # ========== HLAVNÍ SESÍLÁNÍ ==========
    
    def cast_spell(
        self, 
        caster: Player, 
        target: Player, 
        spell_id: str,
        defend_action: Optional[str] = None
    ) -> Tuple[SpellResult, List[str], List[Injury]]:
        """Seslání kouzla s kompletním vyhodnocením"""
        messages = []
        injuries = []
        
        if spell_id not in self.spells:
            return SpellResult.FAILED, [f"❌ Kouzlo {spell_id} neexistuje!"], []
        
        spell = self.spells[spell_id]
        
        can_cast, reason = caster.can_cast_spell_now(spell_id)
        if not can_cast:
            return SpellResult.FAILED, [f"❌ {caster.name}: {reason}"], []
        
        base_accuracy = caster.get_spell_accuracy_modifier()
        accuracy = base_accuracy * 100
        
        messages.append(f"🎯 {caster.name} sesílá **{spell['name_cs']}** (přesnost: {accuracy:.0f}%)")
        
        roll = random.random()
        if roll > base_accuracy:
            messages.append(f"❌ Kouzlo selhalo! ({roll*100:.0f}% vs {accuracy:.0f}%)")
            return SpellResult.FAILED, messages, []
        
        caster.cast_spell(spell_id, spell['cooldown'])
        
        # Obrana
        if defend_action:
            result = self._resolve_defense(caster, target, spell, defend_action)
            messages.append(f"🛡️ {target.name} brání: {defend_action}")
            
            if result == SpellResult.BLOCKED:
                messages.append(f"✋ Kouzlo bylo zablokováno!")
                return result, messages, []
            elif result == SpellResult.REFLECTED:
                messages.append(f"↩️ Kouzlo se odrazilo zpět!")
                injuries = self._apply_spell_effects(spell, caster, caster)
                return result, messages, injuries
            elif result == SpellResult.DODGED:
                messages.append(f"💨 {target.name} uhnul!")
                return result, messages, []
        
        messages.append(f"💥 Zásah!")
        injuries = self._apply_spell_effects(spell, target, caster)
        
        for injury in injuries:
            messages.append(
                f"🩸 {target.name}: {injury.description} "
                f"({injury.body_part.value}, bolest: {injury.pain_level}/10)"
            )
        
        # Speciální efekty
        category = spell.get('category', '')
        
        if category == 'death':
            messages.append(f"💀 {target.name} byl zabit kletbou Avada Kedavra!")
            target.die(f"Avada Kedavra from {caster.name}")
        
        # Reputace
        legality = spell.get('legality', 'legal')
        if legality in ['unforgivable', 'forbidden']:
            caster.reputation += spell.get('reputation_impact', 0)
            caster.dark_magic_uses += 1
            messages.append(f"⚫ {caster.name} použil zakázané kouzlo! (reputace: {caster.reputation})")
        
        # ===== KONTROLA NEPORUŠITELNÝCH SLIBŮ =====
        # Kontrola, zda útok na target neporušuje nějaký slib
        vow_violations = self.check_vow_violations(
            caster,
            "attacked_player",
            {"target_name": target.name, "spell_id": spell_id}
        )
        messages.extend(vow_violations)
        
        # Kontrola použití zakázaného kouzla
        spell_vow_violations = self.check_vow_violations(
            caster,
            "used_spell",
            {"spell_id": spell_id}
        )
        messages.extend(spell_vow_violations)
        
        return SpellResult.HIT, messages, injuries
    
    def cast_utility_spell(
        self,
        caster: Player,
        spell_id: str,
        context: str = "",
        target: Optional[Player] = None
    ) -> Tuple[bool, str]:
        """
        Seslání utility kouzla s realistickými efekty
        
        Args:
            caster: Kdo sesílá
            spell_id: ID kouzla
            context: Popis situace
            target: Cíl (pro některá utility kouzla)
        """
        if spell_id not in self.spells:
            return False, f"❌ Kouzlo {spell_id} neexistuje!"
        
        spell = self.spells[spell_id]
        
        if spell['type'] != 'utility':
            return False, f"❌ {spell['name_cs']} není utility kouzlo!"
        
        can_cast, reason = caster.can_cast_spell_now(spell_id)
        if not can_cast:
            return False, f"❌ {reason}"
        
        accuracy = caster.get_spell_accuracy_modifier()
        roll = random.random()
        
        if roll > accuracy:
            return False, f"❌ Kouzlo selhalo! ({roll*100:.0f}% vs {accuracy*100:.0f}%)"
        
        caster.cast_spell(spell_id, spell['cooldown'])
        caster.use_utility_spell(spell_id)
        
        # Specifické efekty podle spell_id
        success_msg = self._apply_utility_spell_effects(spell, spell_id, caster, context, target)
        
        return True, f"✅ {success_msg}"
    
    # ========== UTILITY KOUZLA - KOMPLETNÍ IMPLEMENTACE ==========
    
    def _apply_utility_spell_effects(
        self, 
        spell: dict, 
        spell_id: str, 
        caster: Player, 
        context: str,
        target: Optional[Player]
    ) -> str:
        """
        Kompletní implementace všech utility kouzel s realistickými efekty
        """
        spell_lower = spell_id.lower()
        
        # ===== SVĚTELNÁ KOUZLA =====
        if spell_lower in ['lumos', 'lumos_maxima', 'lumos_solem']:
            return f"💡 {spell['name_cs']}: Váš hůlka rozsvítila okolí jasným světlem!"
        
        if spell_lower == 'nox':
            return f"🌑 {spell['name_cs']}: Světlo z hůlky zhaslo."
        
        # ===== ODEMYKÁNÍ / ZAMYKÁNÍ =====
        if spell_lower in ['alohomora', 'aberto']:
            if 'dveře' in context.lower() or 'zámek' in context.lower():
                return f"🔓 {spell['name_cs']}: {context} se odemkly!"
            return f"🔓 {spell['name_cs']}: Zámek se odemkl!"
        
        if spell_lower == 'colloportus':
            return f"🔒 {spell['name_cs']}: Dveře byly zapečetěny!"
        
        if spell_lower == 'dissendium':
            return f"🚪 {spell['name_cs']}: Tajný vchod se odhalil!"
        
        # ===== OPRAVY =====
        if spell_lower == 'reparo':
            if context:
                return f"🔧 {spell['name_cs']}: {context} bylo opraveno!"
            return f"🔧 {spell['name_cs']}: Předmět byl opraven!"
        
        # ===== ČIŠTĚNÍ =====
        if spell_lower in ['scourgify', 'tergeo']:
            return f"✨ {spell['name_cs']}: Vše je dokonale čisté!"
        
        # ===== VODA =====
        if spell_lower == 'aguamenti':
            return f"💧 {spell['name_cs']}: Z hůlky tryská čistá voda!"
        
        if spell_lower == 'aqua_erupto':
            return f"💦 {spell['name_cs']}: Mohutný proud vody vyšlehl z hůlky!"
        
        # ===== OHEŇ =====
        if spell_lower in ['incendio', 'flagrate']:
            return f"🔥 {spell['name_cs']}: Vzplanul oheň!"
        
        if spell_lower == 'expertonum':
            return f"🔥 {spell['name_cs']}: Ovládáte plamen!"
        
        # ===== LEVITACE A POHYB =====
        if spell_lower == 'wingardium_leviosa':
            if context:
                return f"🪶 {spell['name_cs']}: {context} vzlétlo do vzduchu!"
            return f"🪶 {spell['name_cs']}: Předmět levituje!"
        
        if spell_lower == 'ascendio':
            return f"⬆️ {spell['name_cs']}: Vystřelili jste vysoko do vzduchu!"
        
        # ===== PŘIVOLÁNÍ =====
        if spell_lower == 'accio':
            if context:
                return f"🧲 {spell['name_cs']}: {context} letí k vám!"
            return f"🧲 {spell['name_cs']}: Předmět byl přivolán!"
        
        # ===== VYTVOŘENÍ OBJEKTŮ =====
        if spell_lower == 'avis':
            return f"🕊️ {spell['name_cs']}: Vyčarovali jste hejno ptáků!"
        
        if spell_lower == 'arania_sortia':
            return f"🕷️ {spell['name_cs']}: Z hůlky vylétli pavouci!"
        
        if spell_lower in ['orchideous', 'orchideus']:
            return f"🌺 {spell['name_cs']}: Z hůlky vyrostla kytice květin!"
        
        if spell_lower == 'periculum':
            return f"🎆 {spell['name_cs']}: Rudé jiskry vystřelily do vzduchu jako signál!"
        
        if spell_lower == 'verdimilious':
            return f"✨ {spell['name_cs']}: Zelené jiskry osvětlily okolí!"
        
        # ===== TRANSFORMACE OBJEKTŮ =====
        if spell_lower == 'piertotum_locomotor':
            return f"🗿 {spell['name_cs']}: Sochy ožily a chystají se k obraně!"
        
        if spell_lower == 'repello_inimigotum':
            return f"🛡️ {spell['name_cs']}: Nepřátelé jsou odpuzováni od této oblasti!"
        
        # ===== MIZENÍ A OBJEVOVÁNÍ =====
        if spell_lower == 'evanesco':
            if context:
                return f"👻 {spell['name_cs']}: {context} zmizelo!"
            return f"👻 {spell['name_cs']}: Předmět zmizel!"
        
        if spell_lower == 'aparecium':
            return f"📜 {spell['name_cs']}: Neviditelný inkoust se zviditelnil!"
        
        # ===== BALENÍ A ORGANIZACE =====
        if spell_lower == 'balit':
            return f"📦 {spell['name_cs']}: Všechno je rychle sbalené!"
        
        if spell_lower == 'portus':
            if context:
                return f"🌀 {spell['name_cs']}: {context} se stalo klíčem k přenesení!"
            return f"🌀 {spell['name_cs']}: Vytvořili jste klíč k přenesení!"
        
        # ===== OCHRANA A BUBLINY =====
        if spell_lower == 'bublinove_kouzlo':
            return f"🫧 {spell['name_cs']}: Velká vzdušná bublina vás obklopila - můžete dýchat pod vodou!"
        
        if spell_lower == 'impervius':
            return f"☔ {spell['name_cs']}: Předmět je nyní nepromokavý!"
        
        # ===== TEPLO A CHLAD =====
        if spell_lower == 'zateplovaci_kouzlo':
            return f"🔥 {spell['name_cs']}: Je vám příjemně teplo a sucho!"
        
        if spell_lower == 'zmrazovaci_kouzlo':
            return f"❄️ {spell['name_cs']}: Předmět zamrzl!"
        
        # ===== KOMUNIKACE =====
        if spell_lower == 'muffliato':
            return f"🤫 {spell['name_cs']}: Kolem vás vznikl bublina soukromí - nikdo vás neslyší!"
        
        if spell_lower == 'sonorus':
            return f"📢 {spell['name_cs']}: Váš hlas je nyní magicky zesílen!"
        
        if spell_lower == 'quietus':
            return f"🔇 {spell['name_cs']}: Váš hlas se vrátil k normálu."
        
        # ===== ODHALENÍ =====
        if spell_lower == 'revelio':
            return f"🔍 {spell['name_cs']}: Skryté objekty a lidi byly odhaleny!"
        
        if spell_lower == 'homenum_revelio':
            return f"👥 {spell['name_cs']}: Detekovali jste přítomnost {random.randint(0, 5)} lidí v okolí!"
        
        if spell_lower == 'specialis_revelio':
            return f"✨ {spell['name_cs']}: Magické vlastnosti byly odhaleny!"
        
        # ===== SPECIÁLNÍ EFEKTY =====
        if spell_lower == 'pack':
            return f"🎒 {spell['name_cs']}: Zavazadla se sama sbalila!"
        
        if spell_lower == 'scouring_charm':
            return f"🧹 {spell['name_cs']}: Všechna špína zmizela!"
        
        if spell_lower == 'geminio':
            if context:
                return f"👯 {spell['name_cs']}: Vytvořili jste duplikát {context}!"
            return f"👯 {spell['name_cs']}: Vytvořili jste duplikát předmětu!"
        
        if spell_lower == 'prior_incanto':
            return f"🔮 {spell['name_cs']}: Odhalili jste poslední seslaná kouzla z hůlky!"
        
        if spell_lower == 'protean_charm':
            return f"🔗 {spell['name_cs']}: Předměty jsou nyní magicky propojeny!"
        
        if spell_lower == 'specialis_revelio':
            return f"🔍 {spell['name_cs']}: Odhalili jste skryté vlastnosti předmětu!"
        
        # Default
        return f"{spell['name_cs']} bylo úspěšně sesláno!"
    
    # ========== APLIKACE EFEKTŮ KOUZEL ==========
    
    def _apply_spell_effects(
        self,
        spell: dict,
        target: Player,
        caster: Player
    ) -> List[Injury]:
        """Aplikuje efekty kouzla podle kategorie a specifického ID"""
        category = spell.get('category', 'damage')
        spell_id = spell.get('incantation', '').lower().replace(' ', '_')
        injuries = []
        
        # DAMAGE - poškozující kouzla
        if category == 'damage':
            injuries = self._apply_damage_spells(spell, spell_id, target)
        
        # DARK MAGIC - temná magie
        elif category == 'dark_magic':
            injuries = self._apply_dark_magic_spells(spell, spell_id, target, caster)
        
        # BINDING - svazující/kontrolní kouzla
        elif category == 'binding':
            self._apply_binding_spells(spell, spell_id, target, caster)
        
        # SHIELD - ochranná kouzla
        elif category == 'shield':
            self._apply_shield_spells(spell, spell_id, target)
        
        # HEALING - léčivá kouzla (v heal_injury metodě)
        # UTILITY - v cast_utility_spell
        
        # Aplikuj zranění
        for injury in injuries:
            target.take_damage(injury)
        
        return injuries
    
    # ========== DAMAGE KOUZLA ==========
    
    def _apply_damage_spells(self, spell: dict, spell_id: str, target: Player) -> List[Injury]:
        """Implementace všech damage kouzel"""
        injuries = []
        
        # ===== VÝBUŠNÁ KOUZLA =====
        if spell_id in ['bombarda', 'bombarda_maxima', 'confringo', 'destrükto', 'destrukto']:
            # Výbuch - popáleniny, zlomeniny, otřes mozku
            burn_parts = random.sample(list(BodyPart), random.randint(2, 4))
            for part in burn_parts:
                injuries.append(Injury(
                    type=InjuryType.BURN,
                    body_part=part,
                    severity=random.randint(6, 9),
                    pain_level=random.randint(7, 10),
                    description=f"Popáleniny od výbuchu {spell['name_cs']}",
                    caused_by=spell['incantation']
                ))
            
            # Zlomeniny
            if random.random() < 0.4:
                part = random.choice([BodyPart.LEFT_ARM, BodyPart.RIGHT_ARM, BodyPart.LEFT_LEG, BodyPart.RIGHT_LEG])
                injuries.append(Injury(
                    type=InjuryType.FRACTURE,
                    body_part=part,
                    severity=random.randint(5, 8),
                    pain_level=random.randint(7, 9),
                    description=f"Zlomenina od explozivní síly",
                    caused_by=spell['incantation']
                ))
            
            # Otřes mozku
            if random.random() < 0.6:
                injuries.append(Injury(
                    type=InjuryType.CONCUSSION,
                    body_part=BodyPart.HEAD,
                    severity=random.randint(5, 8),
                    pain_level=random.randint(6, 9),
                    description="Otřes mozku od výbuchu",
                    caused_by=spell['incantation']
                ))
                target.conditions.add(Condition.STUNNED)
        
        # ===== ŘEZNÁ KOUZLA =====
        elif spell_id in ['sectumsempra', 'diffindo']:
            num_cuts = random.randint(3, 5) if spell_id == 'sectumsempra' else random.randint(1, 3)
            parts = random.sample(list(BodyPart), min(num_cuts, len(BodyPart)))
            
            for part in parts:
                if spell_id == 'sectumsempra':
                    injuries.append(Injury(
                        type=InjuryType.DEEP_WOUND,
                        body_part=part,
                        severity=random.randint(8, 10),
                        bleeding_rate=random.uniform(8, 15),
                        pain_level=random.randint(9, 10),
                        description=f"Hluboké řezné rány od Sectumsempra",
                        caused_by=spell['incantation']
                    ))
                else:
                    injuries.append(Injury(
                        type=InjuryType.CUT,
                        body_part=part,
                        severity=random.randint(4, 7),
                        bleeding_rate=random.uniform(2, 5),
                        pain_level=random.randint(5, 8),
                        description=f"Řezná rána od {spell['name_cs']}",
                        caused_by=spell['incantation']
                    ))
        
        # ===== OMRAČUJÍCÍ KOUZLA =====
        elif spell_id in ['stupefy', 'stupef']:
            target.conditions.add(Condition.UNCONSCIOUS)
            target.consciousness -= random.uniform(40, 60)
            
            # Pád
            injuries.append(self._create_fall_injury(target))
        
        # ===== MUČÍCÍ KOUZLA =====
        elif spell_id == 'cruciatus':
            target.conditions.add(Condition.SEVERE_PAIN)
            
            injuries.append(Injury(
                type=InjuryType.CURSED,
                body_part=BodyPart.HEAD,
                severity=random.randint(9, 10),
                pain_level=10,
                description="Nesnesitelná bolest od Cruciatus",
                caused_by="Cruciatus",
                treatable=False
            ))
            
            if random.random() < 0.15:  # 15% šance na trvalé poškození
                target.consciousness -= 50
                target.conditions.add(Condition.SHOCKED)
        
        # ===== VRHAJÍCÍ KOUZLA =====
        elif spell_id in ['alerte_ascendere', 'flipendo', 'depulso']:
            # Vrhne cíl do vzduchu nebo stranou
            injuries.append(self._create_fall_injury(target))
            
            if random.random() < 0.3:
                injuries.append(Injury(
                    type=InjuryType.FRACTURE,
                    body_part=random.choice([BodyPart.LEFT_LEG, BodyPart.RIGHT_LEG]),
                    severity=random.randint(4, 6),
                    pain_level=random.randint(6, 8),
                    description="Zlomenina z prudkého pádu",
                    caused_by=spell['incantation']
                ))
        
        # ===== LEPÍCÍ/BRÁNÍCÍ KOUZLA =====
        elif spell_id == 'colloshoo':
            # Boty přilepeny k zemi
            effect = StatusEffect(
                effect_type=Condition.IMMOBILIZED,
                duration=random.uniform(10, 20),
                severity=6,
                caused_by=spell['incantation'],
                description="Nohy přilepené k zemi"
            )
            target.add_status_effect(effect)
        
        elif spell_id in ['incarcerous', 'incarcifors', 'brachiabindo']:
            # Svázání lan
            effect = StatusEffect(
                effect_type=Condition.IMMOBILIZED,
                duration=random.uniform(15, 30),
                severity=8,
                caused_by=spell['incantation'],
                description="Svázán magickými lany"
            )
            target.add_status_effect(effect)
        
        # ===== BUBLINY A UVĚZNĚNÍ =====
        elif spell_id == 'ebublio':
            effect = StatusEffect(
                effect_type=Condition.IMMOBILIZED,
                duration=random.uniform(20, 40),
                severity=7,
                caused_by=spell['incantation'],
                description="Uvězněn v magické bublině"
            )
            target.add_status_effect(effect)
        
        # ===== MRZNUTÍ =====
        elif spell_id in ['glacius', 'inmobilus', 'immobulus']:
            effect = StatusEffect(
                effect_type=Condition.FROZEN,
                duration=random.uniform(10, 25),
                severity=random.randint(6, 9),
                caused_by=spell['incantation'],
                description="Zmrazen"
            )
            target.add_status_effect(effect)
        
        # ===== ZKAMENĚNÍ =====
        elif spell_id in ['petrificus_totalus', 'petrificus']:
            effect = StatusEffect(
                effect_type=Condition.PETRIFIED,
                duration=random.uniform(20, 40),
                severity=10,
                caused_by=spell['incantation'],
                description="Zcela zkamenělý"
            )
            target.add_status_effect(effect)
        
        # ===== ZRAK A SLUCH =====
        elif spell_id in ['conjunctivitus', 'conjunctivitis']:
            # Poškození očí
            injuries.append(Injury(
                type=InjuryType.CURSED,
                body_part=BodyPart.HEAD,
                severity=random.randint(5, 7),
                pain_level=random.randint(7, 9),
                description="Poškozené oči od Conjunctivitus",
                caused_by=spell['incantation']
            ))
            
            effect = StatusEffect(
                effect_type=Condition.BLIND,
                duration=random.uniform(30, 60),
                severity=8,
                caused_by=spell['incantation'],
                description="Dočasně oslepený"
            )
            target.add_status_effect(effect)
        
        # ===== ŽLUČOVÁNÍ / ZVRÁCENÍ =====
        elif spell_id == 'zer_slimaky':
            effect = StatusEffect(
                effect_type=Condition.SEVERE_PAIN,
                duration=random.uniform(300, 600),  # 5-10 minut
                severity=7,
                caused_by=spell['incantation'],
                description="Zvrací slimáky"
            )
            target.add_status_effect(effect)
        
        # ===== TLAK A DRCENÍ =====
        elif spell_id in ['defodio', 'deprimo']:
            # Drtivý tlak
            parts = random.sample(list(BodyPart), random.randint(1, 2))
            for part in parts:
                injuries.append(Injury(
                    type=InjuryType.FRACTURE,
                    body_part=part,
                    severity=random.randint(6, 9),
                    pain_level=random.randint(7, 10),
                    description=f"Drcení od vysokého tlaku",
                    caused_by=spell['incantation']
                ))
        
        # ===== OBECNÉ POŠKOZENÍ =====
        else:
            # Generické poškození pro nespecifikovaná kouzla
            parts = random.sample(list(BodyPart), random.randint(1, 2))
            for part in parts:
                injuries.append(Injury(
                    type=InjuryType.CUT,
                    body_part=part,
                    severity=random.randint(3, 6),
                    pain_level=random.randint(4, 7),
                    description=f"Zranění od {spell['name_cs']}",
                    caused_by=spell['incantation']
                ))
        
        return injuries
    
    # ========== DARK MAGIC KOUZLA ==========
    
    def _apply_dark_magic_spells(self, spell: dict, spell_id: str, target: Player, caster: Player) -> List[Injury]:
        """Implementace všech dark magic kouzel"""
        injuries = []
        
        # ===== AVADA KEDAVRA - SMRTÍCÍ KLETBA =====
        if spell_id in ['avada_kedavra', 'avada']:
            target.die(f"Killed by Avada Kedavra from {caster.name}")
            return []
        
        # ===== IMPERIUS - KONTROLA MYSLI =====
        elif spell_id == 'imperius':
            effect = StatusEffect(
                effect_type=Condition.CONTROLLED,
                duration=random.uniform(30, 120),
                severity=10,
                caused_by=spell['incantation'],
                description="Pod úplnou kontrolou Imperius kletby"
            )
            target.add_status_effect(effect)
        
        # ===== FIENDFYRE - PROKLETÉ PLAMENY =====
        elif spell_id == 'fiendfyre':
            # Extrémní popáleniny všude
            for part in BodyPart:
                injuries.append(Injury(
                    type=InjuryType.BURN,
                    body_part=part,
                    severity=random.randint(9, 10),
                    pain_level=10,
                    description="Prokleté popáleniny od Fiendfyre",
                    caused_by=spell['incantation'],
                    treatable=False
                ))
        
        # ===== TRANSFORMACE VLASŮ =====
        elif spell_id == 'anteocula':
            # Vlasy se mění v parohy!
            target.has_antlers = True
            effect = StatusEffect(
                effect_type=Condition.TRANSFORMED,
                duration=random.uniform(120, 300),
                severity=5,
                caused_by=spell['incantation'],
                description="Vlasy přeměněny v parohy"
            )
            target.add_status_effect(effect)
        
        elif spell_id == 'crinus_muto':
            # Mění barvu vlasů
            colors = ['červená', 'modrá', 'zelená', 'fialová', 'oranžová', 'růžová']
            target.hair_color = random.choice(colors)
            effect = StatusEffect(
                effect_type=Condition.TRANSFORMED,
                duration=random.uniform(300, 600),
                severity=2,
                caused_by=spell['incantation'],
                description=f"Vlasy změněny na {target.hair_color}"
            )
            target.add_status_effect(effect)
        
        elif spell_id == 'calvorio':
            # Okamžitá ztráta vlasů
            target.hair_length = 0
            effect = StatusEffect(
                effect_type=Condition.TRANSFORMED,
                duration=random.uniform(600, 1200),
                severity=3,
                caused_by=spell['incantation'],
                description="Úplná ztráta vlasů"
            )
            target.add_status_effect(effect)
        
        elif spell_id in ['dlouhe_vlasy_oboci', 'dlouhovlase_kouzlo']:
            # Rychlý růst vlasů
            target.hair_length += random.uniform(30, 100)
            effect = StatusEffect(
                effect_type=Condition.TRANSFORMED,
                duration=random.uniform(300, 600),
                severity=4,
                caused_by=spell['incantation'],
                description="Extrémní růst vlasů a obočí"
            )
            target.add_status_effect(effect)
        
        # ===== VELIKOSTNÍ ZMĚNY =====
        elif spell_id in ['engorgio', 'enbervio']:
            # Zvětšení
            target.size_multiplier *= random.uniform(1.5, 3.0)
            effect = StatusEffect(
                effect_type=Condition.TRANSFORMED,
                duration=random.uniform(60, 180),
                severity=6,
                caused_by=spell['incantation'],
                description=f"Zvětšen na {target.size_multiplier:.1f}x normální velikosti"
            )
            target.add_status_effect(effect)
        
        elif spell_id == 'reducio':
            # Zmenšení
            target.size_multiplier *= random.uniform(0.3, 0.7)
            effect = StatusEffect(
                effect_type=Condition.TRANSFORMED,
                duration=random.uniform(60, 180),
                severity=6,
                caused_by=spell['incantation'],
                description=f"Zmenšen na {target.size_multiplier:.1f}x normální velikosti"
            )
            target.add_status_effect(effect)
        
        # ===== ZVÍŘECÍ TRANSFORMACE =====
        elif spell_id == 'avifors':
            # Přeměna v ptáka
            effect = StatusEffect(
                effect_type=Condition.TRANSFORMED,
                duration=random.uniform(120, 300),
                severity=9,
                caused_by=spell['incantation'],
                description="Přeměněn v ptáka"
            )
            target.add_status_effect(effect)
        
        elif spell_id in ['ducklifors', 'entomorphis']:
            # Různé zvířecí transformace
            animal = "kachnu" if spell_id == 'ducklifors' else "hmyz"
            effect = StatusEffect(
                effect_type=Condition.TRANSFORMED,
                duration=random.uniform(120, 300),
                severity=9,
                caused_by=spell['incantation'],
                description=f"Přeměněn v {animal}"
            )
            target.add_status_effect(effect)
        
        # ===== TĚLESNÉ DEFORMACE =====
        elif spell_id == 'densaugeo':
            # Zvětšení zubů
            injuries.append(Injury(
                type=InjuryType.CURSED,
                body_part=BodyPart.HEAD,
                severity=4,
                pain_level=3,
                description="Abnormálně zvětšené zuby",
                caused_by=spell['incantation']
            ))
        
        elif spell_id == 'furnunculus':
            # Vředy
            parts = random.sample(list(BodyPart), random.randint(2, 4))
            for part in parts:
                injuries.append(Injury(
                    type=InjuryType.CURSED,
                    body_part=part,
                    severity=random.randint(3, 5),
                    pain_level=random.randint(4, 6),
                    description="Bolestivé vředy",
                    caused_by=spell['incantation']
                ))
        
        elif spell_id == 'zelatinove_prsty':
            # Prsty změkly
            arms = [BodyPart.LEFT_ARM, BodyPart.RIGHT_ARM]
            for arm in arms:
                injuries.append(Injury(
                    type=InjuryType.CURSED,
                    body_part=arm,
                    severity=6,
                    pain_level=3,
                    description="Prsty změkly na úroveň želatiny",
                    caused_by=spell['incantation'],
                    treatable=False
                ))
        
        elif spell_id == 'zelatinovy_mozek':
            # Poškození myšlení
            injuries.append(Injury(
                type=InjuryType.CURSED,
                body_part=BodyPart.HEAD,
                severity=random.randint(7, 9),
                pain_level=5,
                description="Poškozené myšlení - mozek změkl",
                caused_by=spell['incantation'],
                treatable=False
            ))
            target.consciousness -= random.uniform(20, 40)
        
        elif spell_id == 'zihadlova_kletba':
            # Oteklina
            part = random.choice(list(BodyPart))
            injuries.append(Injury(
                type=InjuryType.CURSED,
                body_part=part,
                severity=random.randint(5, 7),
                pain_level=random.randint(6, 8),
                description=f"Oteklina od žihadlové kletby",
                caused_by=spell['incantation']
            ))
        
        # ===== KŮŽE A POVRCH TĚLA =====
        elif spell_id == 'cornflakova_kuze':
            # Kůže pokrytá vločkami
            effect = StatusEffect(
                effect_type=Condition.CURSED,
                duration=random.uniform(180, 360),
                severity=5,
                caused_by=spell['incantation'],
                description="Kůže obalená ovesnými vločkami"
            )
            target.add_status_effect(effect)
        
        # ===== ZPÍVÁNÍ A ZVUKY =====
        elif spell_id == 'cantis':
            # Nucené zpívání
            effect = StatusEffect(
                effect_type=Condition.CURSED,
                duration=random.uniform(60, 180),
                severity=4,
                caused_by=spell['incantation'],
                description="Nucené nekontrolované zpívání"
            )
            target.add_status_effect(effect)
        
        # ===== MENTÁLNÍ EFEKTY =====
        elif spell_id in ['zapomen', 'obliviate']:
            # Ztráta paměti
            effect = StatusEffect(
                effect_type=Condition.MEMORY_WIPED,
                duration=random.uniform(300, 1800),  # 5-30 minut  
                severity=random.randint(6, 10),
                caused_by=spell['incantation'],
                description="Paměť smazána"
            )
            target.add_status_effect(effect)
            target.consciousness -= random.uniform(10, 30)
        
        elif spell_id == 'legilimens':
            # Čtení myšlenek - čteme myšlenky cíle
            # Cíl dostane mentální poškození
            injuries.append(Injury(
                type=InjuryType.CURSED,
                body_part=BodyPart.HEAD,
                severity=random.randint(5, 7),
                pain_level=random.randint(6, 8),
                description="Mentální invaze od Legilimens - myšlenky byly prověřeny",
                caused_by=spell['incantation'],
                treatable=False
            ))
            
            # Dočasné zmatení
            effect = StatusEffect(
                effect_type=Condition.CONFUNDED,
                duration=random.uniform(20, 60),
                severity=6,
                caused_by=spell['incantation'],
                description="Zmatený po mentální invazi"
            )
            target.add_status_effect(effect)
            target.consciousness -= random.uniform(10, 20)
        
        elif spell_id == 'confundus':
            # Zmatek
            effect = StatusEffect(
                effect_type=Condition.CONFUNDED,
                duration=random.uniform(30, 120),
                severity=random.randint(6, 9),
                caused_by=spell['incantation'],
                description="Zmaten - snížená orientace a přesnost"
            )
            target.add_status_effect(effect)
        
        # ===== TEMNÁ ZNAČKA A SLIBY =====
        elif spell_id == 'morsmorse':
            # Temná značka - způsobuje strach a bolest
            injuries.append(Injury(
                type=InjuryType.CURSED,
                body_part=BodyPart.LEFT_ARM,
                severity=random.randint(8, 10),
                pain_level=random.randint(9, 10),
                description="Vypalování Temné značky - nesnesitelná bolest",
                caused_by=spell['incantation'],
                treatable=False
            ))
            
            # Permanentní značka a mentální trauma
            effect = StatusEffect(
                effect_type=Condition.CURSED,
                duration=random.uniform(3600, 7200),  # 1-2 hodiny mentální trauma
                severity=10,
                caused_by=spell['incantation'],
                description="Temná značka vypalena - permanentní prokletí"
            )
            target.add_status_effect(effect)
            target.consciousness -= random.uniform(30, 50)
        
        # POZNÁMKA: Neporušitelný Slib není normální kouzlo!
        # Používá se speciální funkce create_unbreakable_vow() vyžadující 3 osoby
        
        # ===== NEVOLNOST A MUČENÍ =====
        elif spell_id in ['mucus_ad_nauseam', 'mucus']:
            # Nevolnost a zvracení
            effect = StatusEffect(
                effect_type=Condition.SEVERE_PAIN,
                duration=random.uniform(180, 360),
                severity=7,
                caused_by=spell['incantation'],
                description="Extrémní nevolnost a zvracení"
            )
            target.add_status_effect(effect)
            target.consciousness -= random.uniform(15, 30)
        
        elif spell_id == 'transmogrificke_muceni':
            # Mučení transformací - extrémně bolestivé
            injuries.append(Injury(
                type=InjuryType.CURSED,
                body_part=random.choice(list(BodyPart)),
                severity=random.randint(9, 10),
                pain_level=10,
                description="Nesnesitelná bolest od transmogrifikačního mučení",
                caused_by=spell['incantation'],
                treatable=False
            ))
            
            effect = StatusEffect(
                effect_type=Condition.SEVERE_PAIN,
                duration=random.uniform(60, 180),
                severity=10,
                caused_by=spell['incantation'],
                description="Mučen transformačními změnami"
            )
            target.add_status_effect(effect)
        
        # ===== TRANSFORMACE NA ROSTLINY/OBJEKTY =====
        elif spell_id == 'herbifors':
            # Transformace na květiny
            effect = StatusEffect(
                effect_type=Condition.TRANSFORMED,
                duration=random.uniform(180, 360),
                severity=8,
                caused_by=spell['incantation'],
                description="Částečně přeměněn na květiny"
            )
            target.add_status_effect(effect)
        
        elif spell_id == 'inflatus':
            # Nafouknutí jako balón
            target.size_multiplier *= random.uniform(2.0, 4.0)
            effect = StatusEffect(
                effect_type=Condition.TRANSFORMED,
                duration=random.uniform(120, 300),
                severity=7,
                caused_by=spell['incantation'],
                description=f"Nafouknut jako balón na {target.size_multiplier:.1f}x velikost"
            )
            target.add_status_effect(effect)
        
        elif spell_id == 'solidatur':
            # Ztuhnutí těla
            effect = StatusEffect(
                effect_type=Condition.PETRIFIED,
                duration=random.uniform(60, 180),
                severity=9,
                caused_by=spell['incantation'],
                description="Tělo ztuhlo jako kámen"
            )
            target.add_status_effect(effect)
        
        # ===== KOUZLA S HADY A VNITŘNOSTMI =====
        elif spell_id == 'vipera_evanesca':
            # Mizení hadů - pokud má target hady na sobě
            # Odstraní hadí prokletí, pokud existuje
            had_effects = [e for e in target.status_effects if 'had' in e.description.lower()]
            if had_effects:
                for effect in had_effects:
                    target.remove_status_effect(effect.effect_type)
        
        elif spell_id == 'vyvrzeni_vnitrnosti':
            # Vyvržení vnitřností - extrémně brutální
            injuries.append(Injury(
                type=InjuryType.CURSED,
                body_part=BodyPart.TORSO,
                severity=10,
                pain_level=10,
                description="Kritické poškození vnitřních orgánů",
                caused_by=spell['incantation'],
                bleeding_rate=random.uniform(15, 25),
                treatable=False
            ))
            target.consciousness -= random.uniform(50, 80)
        
        elif spell_id == 'vitealova_kletba':
            # Prokletí života - postupné umírání
            injuries.append(Injury(
                type=InjuryType.CURSED,
                body_part=BodyPart.TORSO,
                severity=random.randint(8, 10),
                pain_level=random.randint(8, 10),
                description="Vitealova kletba - postupné vysávání života",
                caused_by=spell['incantation'],
                treatable=False
            ))
            
            effect = StatusEffect(
                effect_type=Condition.CURSED,
                duration=random.uniform(600, 1800),
                severity=10,
                caused_by=spell['incantation'],
                description="Prokletí postupného umírání"
            )
            target.add_status_effect(effect)
        
        elif spell_id == 'assa_in_tuo_suco':
            # Vaření v vlastním džusu - popáleniny zevnitř
            injuries.append(Injury(
                type=InjuryType.BURN,
                body_part=BodyPart.TORSO,
                severity=random.randint(9, 10),
                pain_level=10,
                description="Popálení zevnitř - vaření v džusu",
                caused_by=spell['incantation'],
                treatable=False
            ))
            
            effect = StatusEffect(
                effect_type=Condition.SEVERE_PAIN,
                duration=random.uniform(120, 300),
                severity=10,
                caused_by=spell['incantation'],
                description="Vaří zevnitř"
            )
            target.add_status_effect(effect)
        
        # ===== BLESKOVÉ KOUZLO =====
        elif spell_id == 'bleskove_kouzlo':
            # Mocný blesk
            injuries.append(Injury(
                type=InjuryType.BURN,
                body_part=BodyPart.TORSO,
                severity=random.randint(8, 10),
                pain_level=random.randint(9, 10),
                description="Masivní poškození bleskem",
                caused_by=spell['incantation']
            ))
            
            # Paralýza
            effect = StatusEffect(
                effect_type=Condition.PARALYZED,
                duration=random.uniform(10, 30),
                severity=8,
                caused_by=spell['incantation'],
                description="Paralyzován elektrickým šokem"
            )
            target.add_status_effect(effect)
        
        # ===== GENERIC DARK MAGIC =====
        else:
            # Obecná temná kletba
            injuries.append(Injury(
                type=InjuryType.CURSED,
                body_part=random.choice(list(BodyPart)),
                severity=random.randint(6, 9),
                pain_level=random.randint(7, 10),
                description=f"Kletba od {spell['name_cs']}",
                caused_by=spell['incantation'],
                treatable=False
            ))
        
        return injuries
    
    # ========== BINDING KOUZLA ==========
    
    def _apply_binding_spells(self, spell: dict, spell_id: str, target: Player, caster: Player):
        """Implementace svazujících a kontrolních kouzel"""
        
        # ===== VODNÍ VĚZENÍ =====
        if spell_id == 'aqua_carcerem':
            effect = StatusEffect(
                effect_type=Condition.IMMOBILIZED,
                duration=random.uniform(20, 40),
                severity=8,
                caused_by=spell['incantation'],
                description="Uvězněn ve vodní kouli"
            )
            target.add_status_effect(effect)
        
        # ===== ODHALENÍ A DETEKCE =====
        elif spell_id == 'revelio':
            # Odhalí skryté objekty a lidi
            # Odstraní neviditelnost a skrytí
            if Condition.INVISIBLE in target.conditions:
                target.conditions.remove(Condition.INVISIBLE)
            
            effect = StatusEffect(
                effect_type=Condition.CURSED,  # Placeholder
                duration=random.uniform(30, 60),
                severity=0,  # Pozitivní pro castera
                caused_by=spell['incantation'],
                description="Odhalen - nemůže se skrýt"
            )
            target.add_status_effect(effect)
        
        elif spell_id == 'homenum_revelio':
            # Odhalí přítomnost lidí v okolí
            # Pro cíl to znamená, že nemůže být skrytý
            if Condition.INVISIBLE in target.conditions:
                target.conditions.remove(Condition.INVISIBLE)
            
            effect = StatusEffect(
                effect_type=Condition.CURSED,
                duration=random.uniform(60, 120),
                severity=0,
                caused_by=spell['incantation'],
                description="Detekován - přítomnost odhalena"
            )
            target.add_status_effect(effect)
        
        elif spell_id == 'specialis_revelio':
            # Odhalí magické vlastnosti a kouzla
            # Podobné revelio, ale na magii
            effect = StatusEffect(
                effect_type=Condition.CURSED,
                duration=random.uniform(30, 90),
                severity=0,
                caused_by=spell['incantation'],
                description="Magické vlastnosti odhaleny"
            )
            target.add_status_effect(effect)
        
        # ===== ZAMOTÁNÍ JAZYKA A KOMUNIKACE =====
        elif spell_id == 'mimblewimble':
            # Zamotání jazyka - cíl nemůže mluvit správně
            effect = StatusEffect(
                effect_type=Condition.SILENCED,
                duration=random.uniform(60, 180),
                severity=7,
                caused_by=spell['incantation'],
                description="Jazyk zamotan - nemůže vyslovit kouzla správně"
            )
            target.add_status_effect(effect)
            
            # Navíc zhoršuje přesnost sesílání
            target.spell_accuracy_penalty = random.uniform(0.3, 0.5)
        
        elif spell_id == 'langlock':
            # Přilepí jazyk k patru - podobné mimblewimble ale silnější
            effect = StatusEffect(
                effect_type=Condition.SILENCED,
                duration=random.uniform(90, 240),
                severity=8,
                caused_by=spell['incantation'],
                description="Jazyk přilepen k patru - úplné mlčení"
            )
            target.add_status_effect(effect)
        
        # ===== BÍLÝ PAPRSEK A ZÁŘENÍ =====
        elif spell_id == 'baubillious':
            # Bílý paprsek - zaslepení a omráčení
            effect = StatusEffect(
                effect_type=Condition.BLIND,
                duration=random.uniform(20, 40),
                severity=7,
                caused_by=spell['incantation'],
                description="Oslepený bílým paprskem"
            )
            target.add_status_effect(effect)
            
            # Navíc mírné omráčení
            target.consciousness -= random.uniform(10, 20)
        
        # ===== OCHRANNÁ KOUZLA =====
        elif spell_id == 'fideliovo_zaklinadlo':
            # Fideliovo zaklinadlo - ochrana tajemství
            # Pro target to znamená, že nemůže prozradit tajemství
            effect = StatusEffect(
                effect_type=Condition.CURSED,
                duration=random.uniform(3600, 86400),  # 1 hodina až den
                severity=9,
                caused_by=spell['incantation'],
                description="Magicky svázán tajemstvím - nemůže ho prozradit"
            )
            target.add_status_effect(effect)
        
        elif spell_id == 'neproniknutelne_kouzlo':
            # Neproniknutelná bariéra
            effect = StatusEffect(
                effect_type=Condition.IMMOBILIZED,
                duration=random.uniform(60, 180),
                severity=10,
                caused_by=spell['incantation'],
                description="Uvězněn neproniknutelnou bariérou"
            )
            target.add_status_effect(effect)
        
        # ===== ODZBROJENÍ =====
        elif spell_id in ['expelliarmus', 'expeliarmus']:
            if target.has_wand:
                target.has_wand = False
                target.conditions.add(Condition.DISARMED)
        
        # ===== ZMRAZENÍ A ZNEHYBNĚNÍ =====
        elif spell_id in ['glacius', 'immobulus', 'inmobilus']:
            effect = StatusEffect(
                effect_type=Condition.FROZEN,
                duration=random.uniform(15, 30),
                severity=random.randint(7, 9),
                caused_by=spell['incantation'],
                description="Zmrazen"
            )
            target.add_status_effect(effect)
        
        elif spell_id in ['petrificus_totalus', 'petrificus']:
            effect = StatusEffect(
                effect_type=Condition.PETRIFIED,
                duration=random.uniform(25, 50),
                severity=10,
                caused_by=spell['incantation'],
                description="Zcela zkamenělý"
            )
            target.add_status_effect(effect)
        
        # ===== UMLČENÍ =====
        elif spell_id == 'silencio':
            effect = StatusEffect(
                effect_type=Condition.SILENCED,
                duration=random.uniform(30, 90),
                severity=random.randint(6, 8),
                caused_by=spell['incantation'],
                description="Umlčen - nemůže mluvit ani sesílat"
            )
            target.add_status_effect(effect)
        
        # ===== LEVITACE =====
        elif spell_id in ['levicorpus', 'wingardium_leviosa']:
            effect = StatusEffect(
                effect_type=Condition.LEVITATING,
                duration=random.uniform(15, 30),
                severity=random.randint(5, 7),
                caused_by=spell['incantation'],
                description="Levituje ve vzduchu"
            )
            target.add_status_effect(effect)
        
        # ===== TANCOVÁNÍ =====
        elif spell_id == 'tarantallegra':
            effect = StatusEffect(
                effect_type=Condition.IMMOBILIZED,
                duration=random.uniform(20, 40),
                severity=6,
                caused_by=spell['incantation'],
                description="Nohy tančí nekontrolovatelně"
            )
            target.add_status_effect(effect)
        
        # ===== OSLEPENÍ =====
        elif spell_id == 'obscuro':
            effect = StatusEffect(
                effect_type=Condition.BLIND,
                duration=random.uniform(30, 60),
                severity=random.randint(7, 9),
                caused_by=spell['incantation'],
                description="Oslepený - oči zakryté"
            )
            target.add_status_effect(effect)
        
        # ===== HOŘENÍ =====
        elif spell_id == 'flagrante':
            # Předmět/člověk bude pálit každého, kdo se dotkne
            effect = StatusEffect(
                effect_type=Condition.CURSED,
                duration=random.uniform(120, 300),
                severity=7,
                caused_by=spell['incantation'],
                description="Pálivé prokletí - popálí každého, kdo se dotkne"
            )
            target.add_status_effect(effect)
    
    # ========== SHIELD KOUZLA ==========
    
    def _apply_shield_spells(self, spell: dict, spell_id: str, target: Player):
        """Implementace ochranných kouzel"""
        
        # Přidání dočasného obranného buffuu
        if spell_id in ['protego', 'protego_maxima', 'protego_totalum']:
            duration = random.uniform(10, 30) if 'maxima' in spell_id or 'totalum' in spell_id else random.uniform(5, 15)
            effect = StatusEffect(
                effect_type=Condition.CURSED,  # Použijeme jako placeholder pro shield
                duration=duration,
                severity=0,  # 0 = pozitivní efekt
                caused_by=spell['incantation'],
                description=f"Ochráněn štítem {spell['name_cs']}"
            )
            target.add_status_effect(effect)
        
        # Teleportace/únik
        elif spell_id in ['accio_lumarum', 'aparecka', 'zmizik']:
            # Okamžitě přenese hráče pryč (v reálné hře by to změnilo pozici)
            effect = StatusEffect(
                effect_type=Condition.CURSED,
                duration=0,  # Okamžitý efekt
                severity=0,
                caused_by=spell['incantation'],
                description=f"Teleportován pryč"
            )
            target.add_status_effect(effect)
    
    # ========== POMOCNÉ METODY ==========
    
    def _create_fall_injury(self, target: Player) -> Injury:
        """Zranění z pádu"""
        possibilities = [
            (BodyPart.HEAD, InjuryType.CONCUSSION, "Otřes mozku z pádu"),
            (BodyPart.LEFT_ARM, InjuryType.FRACTURE, "Zlomená ruka z pádu"),
            (BodyPart.RIGHT_ARM, InjuryType.FRACTURE, "Zlomená ruka z pádu"),
            (BodyPart.LEFT_LEG, InjuryType.FRACTURE, "Zlomená noha z pádu"),
            (BodyPart.RIGHT_LEG, InjuryType.FRACTURE, "Zlomená noha z pádu"),
        ]
        
        part, inj_type, desc = random.choice(possibilities)
        
        return Injury(
            type=inj_type,
            body_part=part,
            severity=random.randint(3, 6),
            pain_level=random.randint(5, 7),
            description=desc,
            caused_by="fall"
        )
    
    def _resolve_defense(
        self,
        attacker: Player,
        defender: Player,
        spell: dict,
        defense_spell_id: str
    ) -> SpellResult:
        """
        Vyhodnotí obranu proti kouzlu s podporou VŠECH defensive spells
        
        Args:
            defense_spell_id: ID defensive spell (protego, protego_maxima, expecto_patronum, atd.)
                             nebo "dodge" pro uhnutí
        """
        if not defense_spell_id:
            return SpellResult.HIT
        
        # Speciální případ: dodge není kouzlo
        if defense_spell_id == "dodge":
            movement = defender.get_movement_ability()
            dodge_chance = movement * 0.6
            if random.random() < dodge_chance:
                return SpellResult.DODGED
            return SpellResult.HIT
        
        # Získej defensive spell data
        defense_spell = self.spells.get(defense_spell_id)
        if not defense_spell or defense_spell.get('type') != 'defensive':
            return SpellResult.HIT
        
        # Kontrola, zda obránce umí kouzlo a nemá ho na cooldownu
        can_defend, _ = defender.can_cast_spell_now(defense_spell_id)
        if not can_defend:
            return SpellResult.HIT
        
        # Spotřebuj cooldown
        defender.cast_spell(defense_spell_id, defense_spell['cooldown'])
        
        # Rozhodnutí podle typu defensive spell
        if defense_spell_id in ['protego', 'defensio']:
            return self._resolve_basic_shield(spell, defender)
        
        elif defense_spell_id in ['protego_maxima', 'protego_totalum', 'protego_horribilis', 
                                   'fianto_duri', 'cave_inimicum', 'salvio_hexia']:
            return self._resolve_strong_shield(spell, defender)
        
        elif defense_spell_id in ['expecto_patronum', 'patronovo_zaklinadlo_expecto_patronum']:
            return self._resolve_patronus(spell, defender)
        
        elif defense_spell_id in ['protego_diabolica', 'infernum']:
            return self._resolve_ultimate_shield(spell, defender)
        
        elif defense_spell_id in ['accio_lumarum', 'aparecka', 'zmizik']:
            return SpellResult.DODGED  # Teleportace = auto-dodge
        
        elif defense_spell_id == 'expelliarmus':
            return self._resolve_expelliarmus(spell, defender, attacker)
        
        else:
            # Ostatní defensive spells = základní štít
            return self._resolve_basic_shield(spell, defender)
    
    def _resolve_basic_shield(self, spell: dict, defender: Player) -> SpellResult:
        """Základní štít (Protego, Defensio)"""
        # Avada Kedavra nelze zablokovat
        if spell.get('incantation', '').lower() in ['avada_kedavra', 'avada']:
            return SpellResult.HIT
        
        # Částečná blokace výbušných kouzel
        if spell.get('incantation', '').lower() in ['bombarda', 'confringo', 'sectumsempra']:
            if random.random() < 0.5:
                return SpellResult.BLOCKED
            return SpellResult.HIT
        
        # Plná blokace
        defender_skill = defender.get_spell_accuracy_modifier()
        if random.random() < defender_skill * 0.9:
            if random.random() < 0.3:
                return SpellResult.REFLECTED
            return SpellResult.BLOCKED
        
        return SpellResult.HIT
    
    def _resolve_strong_shield(self, spell: dict, defender: Player) -> SpellResult:
        """Silný štít (Protego Maxima, Protego Totalum, Fianto Duri)"""
        # Avada Kedavra stále nelze zablokovat
        if spell.get('incantation', '').lower() in ['avada_kedavra', 'avada']:
            return SpellResult.HIT
        
        # Lepší šance blokovat výbušná kouzla (80% vs 50%)
        if spell.get('incantation', '').lower() in ['bombarda', 'confringo', 'sectumsempra']:
            if random.random() < 0.8:
                return SpellResult.BLOCKED
            return SpellResult.HIT
        
        # Vyšší šance na blokaci (95% vs 90%)
        defender_skill = defender.get_spell_accuracy_modifier()
        if random.random() < defender_skill * 0.95:
            if random.random() < 0.5:  # 50% vs 30% na odražení
                return SpellResult.REFLECTED
            return SpellResult.BLOCKED
        
        return SpellResult.HIT
    
    def _resolve_patronus(self, spell: dict, defender: Player) -> SpellResult:
        """Expecto Patronum - speciální obrana proti dark magic"""
        # Patronus je NEPRONIKNUTELNÝ proti dark magic
        if spell.get('legality') in ['unforgivable', 'forbidden']:
            return SpellResult.BLOCKED
        
        # Pro temná kouzla (dark_magic kategorie)
        if spell.get('category') == 'dark_magic':
            return SpellResult.BLOCKED
        
        # Jinak funguje jako silný štít
        return self._resolve_strong_shield(spell, defender)
    
    def _resolve_ultimate_shield(self, spell: dict, defender: Player) -> SpellResult:
        """Protego Diabolica / Infernum - absolutní obrana"""
        # Dokonce i Avada Kedavra má jen 50% šanci prorazit!
        if spell.get('incantation', '').lower() in ['avada_kedavra', 'avada']:
            if random.random() < 0.5:
                return SpellResult.BLOCKED
            return SpellResult.HIT
        
        # Vše ostatní je téměř jistě zablokováno
        if random.random() < 0.8:  # 80% šance na odražení
            return SpellResult.REFLECTED
        return SpellResult.BLOCKED
    
    def _resolve_expelliarmus(self, spell: dict, defender: Player, attacker: Player) -> SpellResult:
        """Expelliarmus - odzbrojuje útočníka místo blokace"""
        # Expelliarmus nezastavuje kouzlo, ale odzbrojuje útočníka
        # Kouzlo proletí, ale útočník ztratí hůlku
        if attacker.has_wand:
            attacker.has_wand = False
            attacker.conditions.add(Condition.DISARMED)
        
        # Kouzlo však stále zasáhne
        return SpellResult.HIT
    
    # ========== LÉČENÍ ==========
    
    def heal_injury(
        self,
        healer: Player,
        target: Player,
        spell_id: str,
        injury_index: Optional[int] = None
    ) -> Tuple[bool, str]:
        """Pokus o vyléčení zranění"""
        if spell_id not in self.spells:
            return False, f"Kouzlo {spell_id} neexistuje"
        
        spell = self.spells[spell_id]
        
        if spell['type'] != 'healing':
            return False, f"{spell['name_cs']} není léčivé kouzlo"
        
        can_cast, reason = healer.can_cast_spell_now(spell_id)
        if not can_cast:
            return False, reason
        
        # Najdi zranění
        all_injuries = []
        for body_part, status in target.body.items():
            for i, injury in enumerate(status.injuries):
                if not injury.treated:
                    all_injuries.append((body_part, i, injury))
        
        if not all_injuries:
            return False, f"{target.name} nemá žádná neléčená zranění"
        
        if injury_index is not None and injury_index < len(all_injuries):
            body_part, idx, injury = all_injuries[injury_index]
        else:
            all_injuries.sort(key=lambda x: x[2].severity, reverse=True)
            body_part, idx, injury = all_injuries[0]
        
        # Specifická léčení
        spell_lower = spell_id.lower()
        
        if spell_lower == 'vulnera_sanentur':
            if injury.caused_by.lower() != 'sectumsempra':
                return False, "Vulnera Sanentur funguje pouze na zranění od Sectumsempra"
        
        elif spell_lower == 'anapneo':
            # Léčí dušení
            if Condition.UNCONSCIOUS not in target.conditions:
                return False, "Anapneo se používá proti dušení"
        
        elif spell_lower == 'enervate':
            # Probouzí z bezvědomí
            if Condition.UNCONSCIOUS in target.conditions:
                target.conditions.remove(Condition.UNCONSCIOUS)
                target.consciousness = min(100, target.consciousness + 30)
                healer.cast_spell(spell_id, spell['cooldown'])
                return True, f"✅ {healer.name} probudil {target.name} z bezvědomí!"
            else:
                return False, "Enervate probouzí pouze z bezvědomí"
        
        elif spell_lower == 'epidior':
            # Léčí rány (řezné rány a popáleniny)
            if injury.type not in [InjuryType.CUT, InjuryType.DEEP_WOUND, InjuryType.BURN]:
                return False, "Epidior léčí pouze rány a popáleniny"
            
            # Velmi efektivní léčení ran
            injury.severity = max(0, injury.severity - 5)
            injury.bleeding_rate = max(0, injury.bleeding_rate - 8)
            injury.pain_level = max(0, injury.pain_level - 6)
        
        elif spell_lower == 'reparifors':
            # Ruší transformace a kletby
            # Odstraní všechny transformační efekty
            effects_removed = []
            for effect in list(target.status_effects):
                if effect.effect_type in [Condition.TRANSFORMED, Condition.CURSED]:
                    target.remove_status_effect(effect.effect_type)
                    effects_removed.append(effect.description)
            
            if effects_removed:
                healer.cast_spell(spell_id, spell['cooldown'])
                return True, f"✅ {healer.name} zrušil transformace: {', '.join(effects_removed)}"
            else:
                return False, "Reparifors ruší transformace - ale žádné nebyly nalezeny"
        
        elif spell_lower == 'supersenzoricke_kouzlo':
            # Zvyšuje smysly - odstraňuje oslepení a zlepšuje vnímání
            if Condition.BLIND in target.conditions:
                target.conditions.remove(Condition.BLIND)
            
            # Přidá pozitivní efekt zvýšených smyslů
            effect = StatusEffect(
                effect_type=Condition.CURSED,  # Placeholder
                duration=random.uniform(300, 600),
                severity=0,  # 0 = pozitivní
                caused_by=spell['incantation'],
                description="Zvýšené smysly - lepší přesnost a vnímání"
            )
            target.add_status_effect(effect)
            healer.cast_spell(spell_id, spell['cooldown'])
            return True, f"✅ {healer.name} zvýšil smysly {target.name}!"
        
        elif spell_lower == 'episkey':
            # Léčí menší zlomeniny
            if injury.type not in [InjuryType.FRACTURE, InjuryType.CUT]:
                return False, "Episkey léčí pouze menší zlomeniny a řezné rány"
        
        elif spell_lower in ['brackium_emendo', 'brachium_emendo']:
            # Léčí kosti (ale může je i odstranit!)
            if injury.type not in [InjuryType.FRACTURE, InjuryType.BROKEN_BONE]:
                return False, "Brackium Emendo funguje pouze na kosti"
            
            # 30% šance, že to pokazí
            if random.random() < 0.3:
                injury.severity = 10
                injury.description = "Kosti úplně odstraněny Brackium Emendo"
                return False, "⚠️ Brackium Emendo selhalo - kosti byly odstraněny místo vyléčení!"
        
        elif spell_lower == 'ferula':
            # Vytvoří dlahu
            if injury.type not in [InjuryType.FRACTURE, InjuryType.BROKEN_BONE]:
                return False, "Ferula vytváří dlahy pro zlomeniny"
            
            injury.severity = max(1, injury.severity - 3)
            injury.pain_level = max(0, injury.pain_level - 4)
        
        # Vyléčit
        injury.treated = True
        injury.bleeding_rate = 0
        injury.pain_level = max(0, injury.pain_level - 5)
        
        healer.cast_spell(spell_id, spell['cooldown'])
        
        return True, f"✅ {healer.name} vyléčil {injury.description} u {target.name}"
    
    # ========== SPRÁVA NEPORUŠITELNÝCH SLIBŮ ==========
    
    def create_unbreakable_vow(
        self,
        vow_maker: Player,
        vow_recipient: Player,
        binder: Player,
        vow_text: str,
        conditions: List[str]
    ) -> Tuple[bool, str, Optional[UnbreakableVow]]:
        """
        Vytvoří Neporušitelný Slib mezi třemi osobami
        
        Args:
            vow_maker: Osoba, která přísahá (zemře při porušení)
            vow_recipient: Osoba, které se přísahá
            binder: Svědek provádějící rituál
            vow_text: Přesný text slibu
            conditions: Seznam podmínek (např. ["never_harm:Harry", "always_protect:Draco"])
        
        Returns:
            (success, message, vow_object)
        
        Příklady podmínek:
            - "never_harm:player_name" - Nikdy neublížit hráči
            - "always_protect:player_name" - Vždy chránit hráče
            - "never_reveal:secret_name" - Nikdy neprozradit tajemství
            - "complete_task:task_name" - Dokončit úkol
            - "never_use_spell:spell_id" - Nikdy nepoužít kouzlo
        """
        # Ověření, že všichni jsou naživu
        if not vow_maker.is_alive():
            return False, f"❌ {vow_maker.name} není naživu!", None
        if not vow_recipient.is_alive():
            return False, f"❌ {vow_recipient.name} není naživu!", None
        if not binder.is_alive():
            return False, f"❌ {binder.name} není naživu!", None
        
        # Ověření, že binder má hůlku
        if not binder.has_wand:
            return False, f"❌ {binder.name} nemá hůlku pro provedení rituálu!", None
        
        # Kontrola, že má alespoň jednu podmínku
        if not conditions:
            return False, "❌ Slib musí mít alespoň jednu podmínku!", None
        
        # Vytvoření slibu
        vow_id = f"vow_{vow_maker.discord_id}_{int(time.time())}"
        vow = UnbreakableVow(
            vow_id=vow_id,
            vow_maker=vow_maker,
            vow_recipient=vow_recipient,
            binder=binder,
            vow_text=vow_text,
            conditions=conditions
        )
        
        # Uložení do aktivních slibů
        self.active_vows[vow_id] = vow
        
        # Přidání status effectu osobě, která přísahá
        effect = StatusEffect(
            effect_type=Condition.CURSED,
            duration=float('inf'),  # Navždy, dokud není porušen
            severity=10,
            caused_by="Neporušitelný Slib",
            description=f"Vázán Neporušitelným slibem - smrt při porušení"
        )
        vow_maker.add_status_effect(effect)
        
        # Vytvoření viditelného zranění (magické řetězy)
        injury = Injury(
            type=InjuryType.CURSED,
            body_part=BodyPart.TORSO,
            severity=8,
            pain_level=7,
            description=f"Magické řetězy Neporušitelného slibu (ID: {vow_id})",
            caused_by="Neporušitelný Slib",
            treatable=False
        )
        vow_maker.take_damage(injury)
        
        message = (
            f"✨🔗 **NEPORUŠITELNÝ SLIB UZAVŘEN** 🔗✨\n\n"
            f"**Přísahající:** {vow_maker.name}\n"
            f"**Příjemce slibu:** {vow_recipient.name}\n"
            f"**Svědek (Binder):** {binder.name}\n\n"
            f"**Text slibu:**\n> {vow_text}\n\n"
            f"**Podmínky:**\n"
        )
        for i, condition in enumerate(conditions, 1):
            message += f"{i}. {self._format_condition(condition)}\n"
        
        message += f"\n⚠️ **VAROVÁNÍ:** Porušení jakékoliv podmínky způsobí okamžitou smrt {vow_maker.name}!"
        
        return True, message, vow
    
    def _format_condition(self, condition: str) -> str:
        """Formátuje podmínku pro čitelné zobrazení"""
        if condition.startswith("never_harm:"):
            target = condition.split(":")[1]
            return f"Nikdy neublížit: **{target}**"
        elif condition.startswith("always_protect:"):
            target = condition.split(":")[1]
            return f"Vždy chránit: **{target}**"
        elif condition.startswith("never_reveal:"):
            secret = condition.split(":")[1]
            return f"Nikdy neprozradit: **{secret}**"
        elif condition.startswith("complete_task:"):
            task = condition.split(":")[1]
            return f"Dokončit úkol: **{task}**"
        elif condition.startswith("never_use_spell:"):
            spell = condition.split(":")[1]
            return f"Nikdy nepoužít kouzlo: **{spell}**"
        else:
            return condition
    
    def check_vow_violations(self, player: Player, action: str, context: dict) -> List[str]:
        """
        Kontroluje všechny aktivní sliby pro daného hráče
        
        Args:
            player: Hráč provádějící akci
            action: Typ akce (attacked_player, used_spell, revealed_secret, atd.)
            context: Kontext akce
        
        Returns:
            Seznam zpráv o porušených slibech (prázdný pokud žádné)
        """
        messages = []
        
        for vow_id, vow in list(self.active_vows.items()):
            # Kontroluj pouze sliby, kde je tento hráč tím, kdo přísahá
            if vow.vow_maker != player:
                continue
            
            # Kontroluj porušení
            if vow.check_violation(action, context):
                death_msg = vow.execute_death_penalty()
                if death_msg:
                    messages.append(death_msg)
                    # Odstraň slib z aktivních
                    del self.active_vows[vow_id]
        
        return messages
    
    def get_player_vows(self, player: Player) -> List[UnbreakableVow]:
        """Vrátí všechny aktivní sliby pro daného hráče"""
        vows = []
        for vow in self.active_vows.values():
            if vow.vow_maker == player or vow.vow_recipient == player:
                vows.append(vow)
        return vows
    
    # ========== SPRÁVA SOUBOJŮ ==========
    
    def create_duel(self, player1: Player, player2: Player) -> Duel:
        """Vytvoří nový souboj"""
        duel_id = f"{player1.discord_id}_vs_{player2.discord_id}_{int(time.time())}"
        duel = Duel(
            duel_id=duel_id,
            player1=player1,
            player2=player2
        )
        self.active_duels[duel_id] = duel
        return duel
    
    def execute_turn(
        self,
        duel: Duel,
        p1_spell: Optional[str],
        p1_action: CombatAction,
        p2_spell: Optional[str],
        p2_action: CombatAction
    ) -> CombatTurn:
        """Provede jeden tah souboje"""
        turn = CombatTurn(turn_number=duel.current_turn)
        duel.current_turn += 1
        
        messages = []
        messages.append(f"\n🎭 **Tah {turn.turn_number}**\n")
        
        # Update hráčů (krvácení, stavy)
        duel.player1.update(1.0)
        duel.player2.update(1.0)
        
        # OPRAVA 4: Update status effects každý tah
        for effect in list(duel.player1.status_effects):
            if not effect.update(1.0):  # Vrací False když vypršel
                duel.player1.remove_status_effect(effect.effect_type)
                messages.append(f"⏱️ {duel.player1.name}: Efekt {effect.description} vypršel")
        
        for effect in list(duel.player2.status_effects):
            if not effect.update(1.0):
                duel.player2.remove_status_effect(effect.effect_type)
                messages.append(f"⏱️ {duel.player2.name}: Efekt {effect.description} vypršel")
        
        # Kontrola smrti před akcemi
        if not duel.player1.is_alive():
            messages.append(f"💀 {duel.player1.name} zemřel!")
            duel.end(duel.player2)
            turn.results = messages
            return turn
        
        if not duel.player2.is_alive():
            messages.append(f"💀 {duel.player2.name} zemřel!")
            duel.end(duel.player1)
            turn.results = messages
            return turn
        
        # Simultánní útoky
        if p1_action == CombatAction.ATTACK and p1_spell:
            # P2 může bránit pomocí LIBOVOLNÉHO defensive spell (nebo dodge)
            defend_spell = None
            if p2_action == CombatAction.DEFEND and p2_spell:
                # P2 vybral konkrétní defensive spell
                defend_spell = p2_spell
            elif p2_action == CombatAction.DEFEND:
                # P2 vybral DEFEND bez kouzla = použije Protego jako default
                defend_spell = "protego"
            elif p2_action == CombatAction.DODGE:
                # P2 se snaží uhnout
                defend_spell = "dodge"
            
            result, spell_msgs, injuries = self.cast_spell(
                duel.player1, duel.player2, p1_spell, defend_spell
            )
            messages.extend(spell_msgs)
        
        if p2_action == CombatAction.ATTACK and p2_spell:
            # P1 může bránit pomocí LIBOVOLNÉHO defensive spell (nebo dodge)
            defend_spell = None
            if p1_action == CombatAction.DEFEND and p1_spell:
                # P1 vybral konkrétní defensive spell
                defend_spell = p1_spell
            elif p1_action == CombatAction.DEFEND:
                # P1 vybral DEFEND bez kouzla = použije Protego jako default
                defend_spell = "protego"
            elif p1_action == CombatAction.DODGE:
                # P1 se snaží uhnout
                defend_spell = "dodge"
            
            result, spell_msgs, injuries = self.cast_spell(
                duel.player2, duel.player1, p2_spell, defend_spell
            )
            messages.extend(spell_msgs)
        
        # OPRAVA 3: Léčení během souboje
        if p1_action == CombatAction.HEAL and p1_spell:
            spell1 = self.spells.get(p1_spell)
            if spell1 and spell1.get('type') == 'healing':
                success, msg = self.heal_injury(
                    duel.player1,  # healer
                    duel.player1,  # target (self-heal)
                    p1_spell
                )
                messages.append(msg)
            else:
                messages.append(f"❌ {p1_spell} není léčivé kouzlo!")
        
        if p2_action == CombatAction.HEAL and p2_spell:
            spell2 = self.spells.get(p2_spell)
            if spell2 and spell2.get('type') == 'healing':
                success, msg = self.heal_injury(
                    duel.player2,  # healer
                    duel.player2,  # target (self-heal)
                    p2_spell
                )
                messages.append(msg)
            else:
                messages.append(f"❌ {p2_spell} není léčivé kouzlo!")
        
        # OPRAVA 6: Kontrola consciousness (ztráta vědomí kvůli krvácení)
        if duel.player1.consciousness <= 0 and duel.state == DuelState.ACTIVE:
            messages.append(f"💀 {duel.player1.name} ztratil vědomí a prohrál!")
            duel.end(duel.player2)
        
        if duel.player2.consciousness <= 0 and duel.state == DuelState.ACTIVE:
            messages.append(f"💀 {duel.player2.name} ztratil vědomí a prohrál!")
            duel.end(duel.player1)
        
        turn.results = messages
        duel.turns.append(turn)
        
        return turn