"""
Potion Brewing System - Systém vaření a správy lektvarů
Realistické vaření s časem, ingrediencemi a efekty
"""

import json
import time
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import asdict

from models.potions import (
    Potion, PotionInventory, BrewingProcess, Ingredient,
    PotionEffect, PotionEffectData, get_ingredient, get_all_ingredients
)
from potion_database import get_potion, get_all_potions, get_brewable_potions
from models.player import Player, StatusEffect, Condition, Injury, InjuryType


class PotionBrewingManager:
    """Manager pro vaření a správu lektvarů"""
    
    def __init__(self, data_file: str = "data/potion_inventories.json"):
        self.data_file = data_file
        self.inventories: Dict[int, PotionInventory] = {}  # {player_id: inventory}
        self.load()
    
    # ========== DATA PERSISTENCE ==========
    
    def save(self):
        """Ulož inventáře do JSON"""
        data = {}
        for player_id, inventory in self.inventories.items():
            data[str(player_id)] = {
                "potions": inventory.potions,
                "ingredients": inventory.ingredients,
                "brewing_skill": inventory.brewing_skill,
                "active_brewing": {
                    "player_id": inventory.active_brewing.player_id,
                    "potion_id": inventory.active_brewing.potion_id,
                    "start_time": inventory.active_brewing.start_time,
                    "end_time": inventory.active_brewing.end_time,
                    "ingredients_used": inventory.active_brewing.ingredients_used
                } if inventory.active_brewing else None
            }
        
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Chyba při ukládání potion inventories: {e}")
    
    def load(self):
        """Načti inventáře z JSON"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for player_id_str, inv_data in data.items():
                player_id = int(player_id_str)
                
                inventory = PotionInventory(
                    potions=inv_data.get("potions", {}),
                    ingredients=inv_data.get("ingredients", {}),
                    brewing_skill=inv_data.get("brewing_skill", 0)
                )
                
                # Načti aktivní vaření
                if inv_data.get("active_brewing"):
                    brew_data = inv_data["active_brewing"]
                    inventory.active_brewing = BrewingProcess(
                        player_id=brew_data["player_id"],
                        potion_id=brew_data["potion_id"],
                        start_time=brew_data["start_time"],
                        end_time=brew_data["end_time"],
                        ingredients_used=brew_data["ingredients_used"]
                    )
                
                self.inventories[player_id] = inventory
        
        except FileNotFoundError:
            print("📦 Vytvářím nový soubor pro potion inventories")
        except Exception as e:
            print(f"❌ Chyba při načítání inventories: {e}")
    
    # ========== INVENTORY MANAGEMENT ==========
    
    def get_inventory(self, player_id: int) -> PotionInventory:
        """Získej nebo vytvoř inventář hráče"""
        if player_id not in self.inventories:
            self.inventories[player_id] = PotionInventory()
        return self.inventories[player_id]
    
    # ========== BREWING ==========
    
    def start_brewing(
        self, 
        player_id: int, 
        potion_id: str
    ) -> Tuple[bool, str]:
        """
        Začni vařit lektvar
        Returns: (success, message)
        """
        inventory = self.get_inventory(player_id)
        potion = get_potion(potion_id)
        
        if not potion:
            return False, "❌ Neznámý lektvar!"
        
        if not potion.recipe:
            return False, "❌ Tento lektvar nelze uvařit!"
        
        # Už něco vaří?
        if inventory.active_brewing:
            return False, "❌ Už vaříš jiný lektvar!"
        
        # Má dostatečný skill?
        if not potion.recipe.can_brew(inventory.brewing_skill):
            return False, (
                f"❌ Potřebuješ brewing skill {potion.recipe.required_skill}! "
                f"(máš {inventory.brewing_skill})"
            )
        
        # Má ingredience?
        if not inventory.has_ingredients(potion.recipe.ingredients):
            missing = self._get_missing_ingredients(inventory, potion.recipe.ingredients)
            return False, (
                f"❌ Chybí ti ingredience:\n" + 
                "\n".join([f"• {get_ingredient(ing_id).name_cs}: {count}x" 
                          for ing_id, count in missing.items()])
            )
        
        # Odeber ingredience
        for ing_id, count in potion.recipe.ingredients.items():
            inventory.remove_ingredient(ing_id, count)
        
        # Započni vaření
        start_time = time.time()
        brewing_hours = potion.recipe.brewing_time
        end_time = start_time + (brewing_hours * 3600)  # Convert to seconds
        
        inventory.active_brewing = BrewingProcess(
            player_id=player_id,
            potion_id=potion_id,
            start_time=start_time,
            end_time=end_time,
            ingredients_used=potion.recipe.ingredients.copy()
        )
        
        self.save()
        
        # Časový popis
        if brewing_hours < 24:
            time_desc = f"{brewing_hours:.0f} hodin"
        else:
            days = brewing_hours / 24
            time_desc = f"{days:.0f} dní"
        
        return True, (
            f"🧪 Začal jsi vařit **{potion.name_cs}**!\n"
            f"⏱️ Čas vaření: {time_desc}\n"
            f"📊 Obtížnost: {potion.recipe.difficulty}/10\n"
            f"⚠️ Šance na selhání: {int(potion.recipe.failure_chance * 100)}%"
        )
    
    def check_brewing_completion(self, player_id: int) -> Tuple[bool, Optional[str], Optional[Potion]]:
        """
        Zkontroluj jestli je vaření hotové
        Returns: (is_complete, message, potion)
        """
        inventory = self.get_inventory(player_id)
        
        if not inventory.active_brewing:
            return False, None, None
        
        if not inventory.active_brewing.is_complete():
            return False, None, None
        
        # Vaření je hotové!
        brewing = inventory.active_brewing
        potion = get_potion(brewing.potion_id)
        
        # Zkontroluj úspěch
        success_roll = random.random()
        
        # Skill bonus: vyšší skill = nižší šance na selhání
        skill_bonus = inventory.brewing_skill / 100.0
        adjusted_failure = potion.recipe.failure_chance * (1.0 - skill_bonus * 0.5)
        
        if success_roll < adjusted_failure:
            # SELHÁNÍ!
            inventory.active_brewing = None
            inventory.brewing_skill += 1  # Malý skill boost i při selhání
            self.save()
            
            return True, (
                f"💥 **SELHÁNÍ!**\n"
                f"Tvůj {potion.name_cs} explodoval!\n"
                f"Všechny ingredience jsou ztraceny.\n"
                f"+1 brewing skill (nyní {inventory.brewing_skill})"
            ), None
        
        # ÚSPĚCH!
        inventory.add_potion(potion.id, 1)
        inventory.active_brewing = None
        
        # Skill boost
        skill_gain = potion.recipe.difficulty // 2
        inventory.brewing_skill += skill_gain
        
        self.save()
        
        return True, (
            f"✅ **ÚSPĚCH!**\n"
            f"Uvařil jsi **{potion.name_cs}**!\n"
            f"🧪 Přidáno do inventáře\n"
            f"+{skill_gain} brewing skill (nyní {inventory.brewing_skill})"
        ), potion
    
    def _get_missing_ingredients(
        self, 
        inventory: PotionInventory, 
        required: Dict[str, int]
    ) -> Dict[str, int]:
        """Vrátí chybějící ingredience"""
        missing = {}
        for ing_id, count in required.items():
            have = inventory.ingredients.get(ing_id, 0)
            if have < count:
                missing[ing_id] = count - have
        return missing
    
    # ========== POTION EFFECTS ==========
    
    def use_potion(
        self, 
        player: Player, 
        potion_id: str,
        target_player: Optional[Player] = None
    ) -> Tuple[bool, str]:
        """
        Použij lektvar
        Returns: (success, message)
        """
        inventory = self.get_inventory(player.discord_id)
        
        if not inventory.remove_potion(potion_id, 1):
            return False, "❌ Nemáš tento lektvar!"
        
        potion = get_potion(potion_id)
        
        # Aplikuj efekty
        messages = [f"🧪 Použil jsi **{potion.name_cs}**!"]
        
        for effect_data in potion.effects:
            success, msg = self._apply_effect(
                effect_data, 
                player, 
                target_player,
                potion.quality
            )
            messages.append(msg)
        
        self.save()
        return True, "\n".join(messages)
    
    def _apply_effect(
        self, 
        effect_data: PotionEffectData, 
        player: Player,
        target: Optional[Player],
        quality: float
    ) -> Tuple[bool, str]:
        """Aplikuj jeden efekt lektvaru"""
        
        # Určení cíle
        if effect_data.target == "other" and not target:
            return False, "❌ Tento lektvar vyžaduje cíl!"
        
        target_player = target if effect_data.target == "other" else player
        
        # Aplikuj podle typu efektu
        if effect_data.effect_type == PotionEffect.HEALING:
            return self._apply_healing(target_player, effect_data, quality)
        
        elif effect_data.effect_type == PotionEffect.ANTIDOTE:
            return self._apply_antidote(target_player, effect_data, quality)
        
        elif effect_data.effect_type == PotionEffect.LUCK:
            return self._apply_luck(target_player, effect_data, quality)
        
        elif effect_data.effect_type == PotionEffect.POLYMORPH:
            return self._apply_polymorph(target_player, effect_data, quality)
        
        elif effect_data.effect_type == PotionEffect.TRUTH_SERUM:
            return self._apply_truth_serum(target_player, effect_data, quality)
        
        elif effect_data.effect_type == PotionEffect.SLEEP:
            return self._apply_sleep(target_player, effect_data, quality)
        
        elif effect_data.effect_type == PotionEffect.LOVE_POTION:
            return self._apply_love_potion(target_player, effect_data, quality)
        
        elif effect_data.effect_type == PotionEffect.WEREWOLF_CONTROL:
            return self._apply_werewolf_control(target_player, effect_data, quality)
        
        elif effect_data.effect_type == PotionEffect.INVISIBILITY:
            return self._apply_invisibility(target_player, effect_data, quality)
        
        else:
            return False, f"⚠️ Neimplementovaný efekt: {effect_data.effect_type.value}"
    
    # ========== EFFECT IMPLEMENTATIONS ==========
    
    def _apply_healing(self, player: Player, effect: PotionEffectData, quality: float) -> Tuple[bool, str]:
        """Léčivý efekt"""
        heal_amount = effect.strength * quality
        
        # Zastaví krvácení
        for body_part in player.body.values():
            for injury in body_part.injuries:
                if injury.bleeding_rate > 0 and not injury.treated:
                    injury.treated = True
                    injury.bleeding_rate = 0
        
        # Částečně vyléčí zranění
        healed = 0
        for body_part in player.body.values():
            for injury in body_part.injuries[:]:
                if injury.severity > 0:
                    reduction = min(injury.severity, heal_amount - healed)
                    injury.severity -= reduction
                    healed += reduction
                    
                    if injury.severity <= 0:
                        body_part.injuries.remove(injury)
        
        # Obnovení krve
        blood_restore = 500 * quality
        player.blood_volume = min(5000, player.blood_volume + blood_restore)
        
        # Obnovení vědomí
        consciousness_restore = 20 * quality
        player.consciousness = min(100, player.consciousness + consciousness_restore)
        
        player._update_conditions()
        
        return True, (
            f"💚 **Léčení:**\n"
            f"• Zastaveno krvácení\n"
            f"• Vyléčeno {int(healed)} bodů zranění\n"
            f"• Obnoveno {int(blood_restore)}ml krve\n"
            f"• Obnoveno {int(consciousness_restore)}% vědomí"
        )
    
    def _apply_antidote(self, player: Player, effect: PotionEffectData, quality: float) -> Tuple[bool, str]:
        """Protijed"""
        cured = []
        
        # Odstraň CURSED injury
        for body_part in player.body.values():
            for injury in body_part.injuries[:]:
                if injury.type == InjuryType.CURSED:
                    body_part.injuries.remove(injury)
                    cured.append("Kletba")
        
        # Odstraň některé negative stavy
        negative_conditions = [
            Condition.CURSED, Condition.CONFUNDED, 
            Condition.CONTROLLED, Condition.PARALYZED
        ]
        
        for condition in negative_conditions:
            if condition in player.conditions:
                player.remove_status_effect(condition)
                cured.append(condition.value)
        
        if cured:
            return True, f"🛡️ **Vyléčeno:** {', '.join(cured)}"
        else:
            return True, "🛡️ Žádný jed nebyl detekován"
    
    def _apply_luck(self, player: Player, effect: PotionEffectData, quality: float) -> Tuple[bool, str]:
        """Felix Felicis - štěstí"""
        duration = effect.duration * quality
        
        effect_obj = StatusEffect(
            effect_type=Condition.INVISIBLE,  # Použijeme jako placeholder pro "lucky"
            duration=duration,
            severity=effect.strength,
            caused_by="Felix Felicis",
            description="Úžasné štěstí - vše se daří!"
        )
        
        player.add_status_effect(effect_obj)
        
        hours = duration / 3600
        return True, (
            f"✨ **Felix Felicis aktivní!**\n"
            f"⏱️ Trvání: {hours:.1f}h\n"
            f"🍀 Vše se ti bude dařit!"
        )
    
    def _apply_polymorph(self, player: Player, effect: PotionEffectData, quality: float) -> Tuple[bool, str]:
        """Mnoholičný lektvar"""
        duration = effect.duration * quality
        
        effect_obj = StatusEffect(
            effect_type=Condition.TRANSFORMED,
            duration=duration,
            severity=effect.strength,
            caused_by="Polyjuice Potion",
            description="Proměněn v jinou osobu"
        )
        
        player.add_status_effect(effect_obj)
        
        minutes = duration / 60
        return True, (
            f"🎭 **Proměna aktivní!**\n"
            f"⏱️ Trvání: {int(minutes)} minut\n"
            f"⚠️ Nezapomeň přidat vlas cílové osoby!"
        )
    
    def _apply_truth_serum(self, player: Player, effect: PotionEffectData, quality: float) -> Tuple[bool, str]:
        """Veritasérum"""
        duration = effect.duration * quality
        
        effect_obj = StatusEffect(
            effect_type=Condition.CONFUNDED,  # Použijeme jako placeholder
            duration=duration,
            severity=effect.strength,
            caused_by="Veritaserum",
            description="Musí mluvit pravdu"
        )
        
        player.add_status_effect(effect_obj)
        
        minutes = duration / 60
        return True, (
            f"🗣️ **Veritasérum aktivní!**\n"
            f"⏱️ Trvání: {int(minutes)} minut\n"
            f"⚠️ Cíl musí mluvit jen pravdu!"
        )
    
    def _apply_sleep(self, player: Player, effect: PotionEffectData, quality: float) -> Tuple[bool, str]:
        """Lektvar živé smrti"""
        duration = effect.duration * quality
        
        effect_obj = StatusEffect(
            effect_type=Condition.UNCONSCIOUS,
            duration=duration,
            severity=effect.strength,
            caused_by="Draught of Living Death",
            description="Hluboký spánek"
        )
        
        player.add_status_effect(effect_obj)
        
        hours = duration / 3600
        return True, (
            f"💤 **Hluboký spánek!**\n"
            f"⏱️ Trvání: {hours:.1f}h\n"
            f"⚠️ Nelze probudit!"
        )
    
    def _apply_love_potion(self, player: Player, effect: PotionEffectData, quality: float) -> Tuple[bool, str]:
        """Amortence"""
        duration = effect.duration * quality
        
        effect_obj = StatusEffect(
            effect_type=Condition.CONFUNDED,
            duration=duration,
            severity=effect.strength,
            caused_by="Amortentia",
            description="Posedlost"
        )
        
        player.add_status_effect(effect_obj)
        
        hours = duration / 3600
        return True, (
            f"💕 **Lektvar lásky aktivní!**\n"
            f"⏱️ Trvání: {hours:.1f}h\n"
            f"⚠️ Cíl je posedlý!"
        )
    
    def _apply_werewolf_control(self, player: Player, effect: PotionEffectData, quality: float) -> Tuple[bool, str]:
        """Vlkodlačí lektvar"""
        duration = effect.duration * quality
        
        effect_obj = StatusEffect(
            effect_type=Condition.CONTROLLED,  # Vlastně self-control
            duration=duration,
            severity=effect.strength,
            caused_by="Wolfsbane Potion",
            description="Kontrola nad vlkodlačí proměnou"
        )
        
        player.add_status_effect(effect_obj)
        
        hours = duration / 3600
        return True, (
            f"🐺 **Vlkodlačí lektvar aktivní!**\n"
            f"⏱️ Trvání: {hours:.1f}h\n"
            f"🧠 Zachováš si lidskou mysl!"
        )
    
    def _apply_invisibility(self, player: Player, effect: PotionEffectData, quality: float) -> Tuple[bool, str]:
        """Neviditelnost"""
        duration = effect.duration * quality
        
        effect_obj = StatusEffect(
            effect_type=Condition.INVISIBLE,
            duration=duration,
            severity=effect.strength,
            caused_by="Invisibility Potion",
            description="Neviditelný"
        )
        
        player.add_status_effect(effect_obj)
        
        minutes = duration / 60
        return True, (
            f"👻 **Neviditelnost aktivní!**\n"
            f"⏱️ Trvání: {int(minutes)} minut\n"
            f"🙈 Ostatní tě nevidí!"
        )
    
    # ========== UTILITIES ==========
    
    def give_ingredient(self, player_id: int, ingredient_id: str, count: int = 1):
        """Dej hráči ingredienci"""
        inventory = self.get_inventory(player_id)
        inventory.add_ingredient(ingredient_id, count)
        self.save()
    
    def give_potion(self, player_id: int, potion_id: str, count: int = 1):
        """Dej hráči lektvar"""
        inventory = self.get_inventory(player_id)
        inventory.add_potion(potion_id, count)
        self.save()
