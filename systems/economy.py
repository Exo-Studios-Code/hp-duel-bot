"""
Economy System - Gathering, obchody, trading
"""

import time
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class ShopItem:
    """Item v obchodě"""
    id: str
    name_cs: str
    name_en: str
    description: str
    price: int
    category: str
    
    consumable: bool = True
    stackable: bool = True
    
    effects: Dict[str, float] = field(default_factory=dict)


@dataclass
class GatherableResource:
    """Zdroj který lze sbírat"""
    id: str
    name_cs: str
    name_en: str
    description: str
    
    base_value: int  # Kolik goldů za kus
    
    locations: List[str] = field(default_factory=list)
    
    spawn_chance: float = 0.3
    
    gather_time: float = 5.0  # sekundy
    difficulty: int = 1  # 1-5


# ========== SHOP DATABASE ==========

SHOP_ITEMS = {
    # Lektvary
    "wiggenweld_potion": ShopItem(
        id="wiggenweld_potion",
        name_cs="Regenerační lektvar",
        name_en="Wiggenweld Potion",
        description="Obnoví 50% vědomí a zastaví lehké krvácení",
        price=50,
        category="healing",
        effects={"consciousness": 0.5, "stop_bleeding": 0.5}
    ),
    
    "blood_replenishing": ShopItem(
        id="blood_replenishing",
        name_cs="Lektvar doplňující krev",
        name_en="Blood-Replenishing Potion",
        description="Obnoví 500ml krve",
        price=100,
        category="healing",
        effects={"blood_volume": 500}
    ),
    
    "invigoration_draught": ShopItem(
        id="invigoration_draught",
        name_cs="Oživující lektvar",
        name_en="Invigoration Draught",
        description="Zvýší energii a bdělost",
        price=30,
        category="buff",
        effects={"energy": 0.3}
    ),
    
    # Ingredience
    "moonstone": ShopItem(
        id="moonstone",
        name_cs="Měsíční kámen",
        name_en="Moonstone",
        description="Vzácná ingredience",
        price=20,
        category="ingredient"
    ),
    
    "unicorn_hair": ShopItem(
        id="unicorn_hair",
        name_cs="Jednorožcův vlas",
        name_en="Unicorn Hair",
        description="Magická ingredience",
        price=15,
        category="ingredient"
    ),
    
    "mandrake_root": ShopItem(
        id="mandrake_root",
        name_cs="Mandragora (kořen)",
        name_en="Mandrake Root",
        description="Léčivá rostlina",
        price=10,
        category="ingredient"
    ),
    
    # Utility
    "portkey": ShopItem(
        id="portkey",
        name_cs="Portklíč",
        name_en="Portkey",
        description="Okamžitá teleportace do Prasinek",
        price=200,
        category="utility",
        consumable=True
    ),
    
    "tent": ShopItem(
        id="tent",
        name_cs="Magický stan",
        name_en="Magical Tent",
        description="Potřebné pro vytvoření tábora",
        price=50,
        category="utility",
        consumable=True
    )
}


# ========== GATHERABLE RESOURCES ==========

GATHERABLE_RESOURCES = {
    "unicorn_hair": GatherableResource(
        id="unicorn_hair",
        name_cs="Jednorožcův vlas",
        name_en="Unicorn Hair",
        description="Vzácný magický vlas",
        base_value=15,
        locations=["forbidden_forest"],
        spawn_chance=0.1,
        gather_time=10.0,
        difficulty=3
    ),
    
    "moonstone": GatherableResource(
        id="moonstone",
        name_cs="Měsíční kámen",
        name_en="Moonstone",
        description="Kámen nabytý měsíční magií",
        base_value=20,
        locations=["forbidden_forest"],
        spawn_chance=0.05,
        gather_time=15.0,
        difficulty=4
    ),
    
    "mandrake_root": GatherableResource(
        id="mandrake_root",
        name_cs="Mandragora",
        name_en="Mandrake Root",
        description="Léčivý kořen",
        base_value=10,
        locations=["hogwarts_grounds", "hogsmeade"],
        spawn_chance=0.3,
        gather_time=5.0,
        difficulty=1
    ),
    
    "dittany": GatherableResource(
        id="dittany",
        name_cs="Třemdava",
        name_en="Dittany",
        description="Silná léčivá rostlina",
        base_value=25,
        locations=["forbidden_forest"],
        spawn_chance=0.08,
        gather_time=12.0,
        difficulty=3
    ),
    
    "wormwood": GatherableResource(
        id="wormwood",
        name_cs="Pelyněk",
        name_en="Wormwood",
        description="Hořká bylina",
        base_value=5,
        locations=["hogsmeade", "hogwarts_grounds"],
        spawn_chance=0.4,
        gather_time=3.0,
        difficulty=1
    )
}


class EconomyManager:
    """Správa ekonomiky"""
    
    def __init__(self):
        self.shop_items = SHOP_ITEMS
        self.gatherable_resources = GATHERABLE_RESOURCES
        
        # Cooldowny na gathering
        self.gather_cooldowns: Dict[int, float] = {}  # {player_id: next_gather_time}
    
    
    # ========== SHOP SYSTEM ==========
    
    def get_shop_inventory(self, category: Optional[str] = None) -> List[ShopItem]:
        """Získej seznam věcí v obchodě"""
        items = list(self.shop_items.values())
        
        if category:
            items = [item for item in items if item.category == category]
        
        return sorted(items, key=lambda x: x.price)
    
    
    def can_buy(
        self, 
        player_gold: int, 
        item_id: str, 
        quantity: int = 1
    ) -> Tuple[bool, str, int]:
        """
        Může hráč koupit item?
        Returns: (success, message, total_cost)
        """
        if item_id not in self.shop_items:
            return False, "Tento item neexistuje!", 0
        
        item = self.shop_items[item_id]
        total_cost = item.price * quantity
        
        if player_gold < total_cost:
            return False, f"Nemáš dost goldů! Potřebuješ {total_cost}g, máš {player_gold}g", total_cost
        
        return True, "OK", total_cost
    
    
    def buy_item(
        self,
        player_inventory: Dict[str, int],
        player_gold: int,
        item_id: str,
        quantity: int = 1
    ) -> Tuple[bool, str, int, Dict[str, int]]:
        """
        Kup item
        Returns: (success, message, new_gold, new_inventory)
        """
        can_buy, reason, total_cost = self.can_buy(player_gold, item_id, quantity)
        
        if not can_buy:
            return False, reason, player_gold, player_inventory
        
        item = self.shop_items[item_id]
        
        # Odečti gold
        new_gold = player_gold - total_cost
        
        # Přidej do inventáře
        new_inventory = player_inventory.copy()
        if item.stackable:
            new_inventory[item_id] = new_inventory.get(item_id, 0) + quantity
        else:
            # Non-stackable items
            for i in range(quantity):
                unique_id = f"{item_id}_{i}"
                new_inventory[unique_id] = 1
        
        return True, f"✅ Koupil jsi {quantity}x **{item.name_cs}** za {total_cost}g!", new_gold, new_inventory
    
    
    def sell_item(
        self,
        player_inventory: Dict[str, int],
        player_gold: int,
        item_id: str,
        quantity: int = 1
    ) -> Tuple[bool, str, int, Dict[str, int]]:
        """
        Prodej item
        Returns: (success, message, new_gold, new_inventory)
        """
        if item_id not in player_inventory or player_inventory[item_id] < quantity:
            return False, "Nemáš dost těchto itemů!", player_gold, player_inventory
        
        # Zjisti cenu
        if item_id in self.shop_items:
            sell_price = int(self.shop_items[item_id].price * 0.5)  # Prodej za 50%
        elif item_id in self.gatherable_resources:
            sell_price = self.gatherable_resources[item_id].base_value
        else:
            sell_price = 1  # Default
        
        total_value = sell_price * quantity
        
        # Odeber z inventáře
        new_inventory = player_inventory.copy()
        new_inventory[item_id] -= quantity
        if new_inventory[item_id] <= 0:
            del new_inventory[item_id]
        
        # Přidej gold
        new_gold = player_gold + total_value
        
        return True, f"✅ Prodal jsi {quantity}x za {total_value}g!", new_gold, new_inventory
    
    
    # ========== GATHERING SYSTEM ==========
    
    def can_gather(self, player_id: int, location_id: str) -> Tuple[bool, str]:
        """Může hráč sbírat?"""
        # Cooldown check
        if player_id in self.gather_cooldowns:
            next_time = self.gather_cooldowns[player_id]
            if time.time() < next_time:
                wait_seconds = int(next_time - time.time())
                return False, f"⏳ Musíš počkat ještě {wait_seconds}s"
        
        # Je něco ke sběru v této lokaci?
        available = [
            res for res in self.gatherable_resources.values()
            if location_id in res.locations
        ]
        
        if not available:
            return False, "V této lokaci není nic ke sběru!"
        
        return True, "OK"
    
    
    def gather(
        self,
        player_id: int,
        location_id: str,
        player_inventory: Dict[str, int]
    ) -> Tuple[bool, str, Optional[str], int, Dict[str, int]]:
        """
        Pokus se sebrat zdroje
        Returns: (success, message, resource_id, value, new_inventory)
        """
        can_gather, reason = self.can_gather(player_id, location_id)
        if not can_gather:
            return False, reason, None, 0, player_inventory
        
        # Najdi dostupné zdroje
        available = [
            res for res in self.gatherable_resources.values()
            if location_id in res.locations
        ]
        
        if not available:
            return False, "Nenašel jsi nic!", None, 0, player_inventory
        
        # Náhodně vyber zdroj
        weights = [res.spawn_chance for res in available]
        resource = random.choices(available, weights=weights)[0]
        
        # Roll jestli to najde
        success_chance = resource.spawn_chance
        
        if random.random() > success_chance:
            # Neúspěch
            cooldown = 60  # 1 minuta
            self.gather_cooldowns[player_id] = time.time() + cooldown
            return False, f"❌ Nenašel jsi nic! Zkus to za {cooldown}s", None, 0, player_inventory
        
        # Úspěch!
        quantity = random.randint(1, 3)  # 1-3 kusy
        total_value = resource.base_value * quantity
        
        # Přidej do inventáře
        new_inventory = player_inventory.copy()
        new_inventory[resource.id] = new_inventory.get(resource.id, 0) + quantity
        
        # Nastav cooldown
        cooldown = int(resource.gather_time * 60)  # Convert to seconds
        self.gather_cooldowns[player_id] = time.time() + cooldown
        
        return True, (
            f"✅ Našel jsi {quantity}x **{resource.name_cs}**! (hodnota: {total_value}g)\n"
            f"⏳ Další gathering za {cooldown}s"
        ), resource.id, total_value, new_inventory
    
    
    # ========== TRADING SYSTEM ==========
    
    def create_trade_offer(
        self,
        from_player_id: int,
        to_player_id: int,
        offered_items: Dict[str, int],
        requested_gold: int
    ) -> Tuple[bool, str, str]:
        """
        Vytvoř nabídku na trade
        Returns: (success, message, trade_id)
        """
        trade_id = f"trade_{from_player_id}_{to_player_id}_{int(time.time())}"
        
        # Zde by šel implementovat pending trades systém
        # Pro teď jen vrátíme trade_id
        
        return True, "✅ Nabídka odeslána!", trade_id
    
    
    def accept_trade(
        self,
        trade_id: str,
        from_inventory: Dict[str, int],
        from_gold: int,
        to_inventory: Dict[str, int],
        to_gold: int,
        offered_items: Dict[str, int],
        requested_gold: int
    ) -> Tuple[bool, str, Dict[str, int], int, Dict[str, int], int]:
        """
        Přijmi trade
        Returns: (success, message, from_new_inv, from_new_gold, to_new_inv, to_new_gold)
        """
        # Kontrola že from hráč má věci
        for item_id, count in offered_items.items():
            if from_inventory.get(item_id, 0) < count:
                return False, "Nabízející nemá dost itemů!", from_inventory, from_gold, to_inventory, to_gold
        
        # Kontrola že to hráč má gold
        if to_gold < requested_gold:
            return False, "Nemáš dost goldů!", from_inventory, from_gold, to_inventory, to_gold
        
        # Proveď trade
        from_new_inv = from_inventory.copy()
        to_new_inv = to_inventory.copy()
        
        # Přesuň itemy
        for item_id, count in offered_items.items():
            from_new_inv[item_id] -= count
            if from_new_inv[item_id] <= 0:
                del from_new_inv[item_id]
            
            to_new_inv[item_id] = to_new_inv.get(item_id, 0) + count
        
        # Přesuň gold
        from_new_gold = from_gold + requested_gold
        to_new_gold = to_gold - requested_gold
        
        return True, "✅ Trade dokončen!", from_new_inv, from_new_gold, to_new_inv, to_new_gold
    
    
    # ========== UTILITY ==========
    
    def get_inventory_value(self, inventory: Dict[str, int]) -> int:
        """Spočítej celkovou hodnotu inventáře"""
        total = 0
        
        for item_id, count in inventory.items():
            if item_id in self.shop_items:
                total += self.shop_items[item_id].price * count
            elif item_id in self.gatherable_resources:
                total += self.gatherable_resources[item_id].base_value * count
        
        return total
    
    
    def format_inventory(self, inventory: Dict[str, int]) -> str:
        """Naformátuj inventář pro zobrazení"""
        if not inventory:
            return "_(prázdný)_"
        
        lines = []
        for item_id, count in sorted(inventory.items()):
            # Zjisti název
            if item_id in self.shop_items:
                name = self.shop_items[item_id].name_cs
                value = self.shop_items[item_id].price
            elif item_id in self.gatherable_resources:
                name = self.gatherable_resources[item_id].name_cs
                value = self.gatherable_resources[item_id].base_value
            else:
                name = item_id
                value = 0
            
            lines.append(f"• **{name}** x{count} _(~{value * count}g)_")
        
        return "\n".join(lines)
    
    
    def format_shop(self, items: List[ShopItem]) -> str:
        """Naformátuj obchod pro zobrazení"""
        lines = []
        
        current_category = None
        for item in items:
            if item.category != current_category:
                current_category = item.category
                category_names = {
                    "healing": "💚 Léčení",
                    "buff": "⚡ Posílení",
                    "ingredient": "🌿 Ingredience",
                    "utility": "🔧 Utility"
                }
                lines.append(f"\n**{category_names.get(item.category, item.category.upper())}**")
            
            lines.append(
                f"• **{item.name_cs}** - {item.price}g\n"
                f"  _{item.description}_"
            )
        
        return "\n".join(lines)
    
    
    def use_item(
        self,
        player_inventory: Dict[str, int],
        item_id: str,
        player_state: dict
    ) -> Tuple[bool, str, Dict[str, int]]:
        """
        Použij item
        Returns: (success, message, new_inventory)
        """
        if item_id not in player_inventory or player_inventory[item_id] <= 0:
            return False, "Nemáš tento item!", player_inventory
        
        if item_id not in self.shop_items:
            return False, "Tento item nelze použít!", player_inventory
        
        item = self.shop_items[item_id]
        
        if not item.consumable:
            return False, "Tento item není spotřební!", player_inventory
        
        # Aplikuj efekty
        effects_applied = []
        for effect, value in item.effects.items():
            if effect == "consciousness":
                # Obnoví vědomí
                effects_applied.append(f"Obnoveno {int(value*100)}% vědomí")
            elif effect == "blood_volume":
                effects_applied.append(f"Obnoveno {int(value)}ml krve")
            elif effect == "stop_bleeding":
                effects_applied.append("Zastaveno krvácení")
            elif effect == "energy":
                effects_applied.append(f"Zvýšena energie o {int(value*100)}%")
        
        # Odeber z inventáře
        new_inventory = player_inventory.copy()
        new_inventory[item_id] -= 1
        if new_inventory[item_id] <= 0:
            del new_inventory[item_id]
        
        effects_text = "\n".join(f"• {eff}" for eff in effects_applied)
        
        return True, (
            f"✅ Použil jsi **{item.name_cs}**!\n\n"
            f"**Efekty:**\n{effects_text}"
        ), new_inventory