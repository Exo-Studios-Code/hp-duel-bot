# 🗺️ Open World - Status Implementace

## ✅ CO JE HOTOVÉ (v tomto balíčku)

### 1. Dokumentace (100% hotové)
- ✅ `PVP_SYSTEM_EXPLAINED.md` - Kompletní vysvětlení PvP systému
- ✅ `README_OPENWORLD.md` - Quick start guide
- ✅ `OPEN_WORLD_GUIDE.md` - Detailní herní mechaniky
- ✅ Tento soubor - Implementation status

### 2. Core Models (připravené k použití)
- ✅ `models/world.py` - Základní struktury (Location, Camp, PlayerWorldState)
- ✅ PvP zóny (Safe, Consensual, Open)
- ✅ 10 lokací (Prasinky, Zapovězený les, atd.)
- ✅ Tábory s ochranou
- ✅ Party systém

### 3. Existující Bot (už funguje)
- ✅ `bot.py` - Discord bot s combat systémem
- ✅ `models/player.py` - Hráčský model s realistickými zraněními
- ✅ `models/combat.py` - Combat engine
- ✅ `spell_database.py` - 62 funkčních kouzel

---

## 🚧 CO POTŘEBUJE DOIMPLEMENTOVAT

### 1. World Manager (skeleton ready)
**Soubor:** `systems/world_manager.py`

```python
# Potřebné funkce:
class WorldManager:
    def __init__(self):
        self.world_state = WorldState()
        self.load_locations()
    
    def get_player_location(self, player_id: int) -> Location:
        # TODO: Implementovat
        pass
    
    def travel(self, player_id: int, destination: str):
        # TODO: Implementovat
        pass
    
    def create_camp(self, player_id: int, name: str):
        # TODO: Implementovat
        pass
    
    def initiate_pvp(self, attacker_id: int, target_id: int):
        # TODO: Implementovat
        # Kontrola PvP zóny
        # Start combat (použít existující combat.py!)
        pass
```

**Priorita:** HIGH
**Složitost:** MEDIUM
**Čas:** 2-3 hodiny

### 2. Discord Commands (skeleton ready)
**Soubor:** `commands/world_commands.py`

```python
# Potřebné příkazy:

@bot.tree.command(name="map")
async def map_command(interaction):
    # TODO: Zobraz mapu s lokacemi
    pass

@bot.tree.command(name="travel")
async def travel_command(interaction, destination: str):
    # TODO: Zavolej world_manager.travel()
    pass

@bot.tree.command(name="camp_create")
async def camp_create(interaction, name: str):
    # TODO: Zavolej world_manager.create_camp()
    pass

@bot.tree.command(name="pvp_attack")
async def pvp_attack(interaction, target: discord.Member):
    # TODO: Zavolej world_manager.initiate_pvp()
    # Použij existující combat systém!
    pass
```

**Priorita:** HIGH
**Složitost:** MEDIUM
**Čas:** 3-4 hodiny

### 3. Integration s Combat System
**Soubor:** `models/combat.py` (aktualizace)

```python
# V existujícím combat.py přidej:

def check_pvp_rules(attacker_id, target_id, location):
    """
    Kontrola zda může hráč zaútočit
    podle PvP pravidel lokace
    """
    # TODO: Implementovat
    pass
```

**Priorita:** HIGH
**Složitost:** LOW
**Čas:** 1 hodina

---

## 🎯 Implementační Plán (Krok za Krokem)

### Fáze 1: Základní World (2-3 hodiny)
```
1. Implementuj WorldManager.get_player_location()
2. Implementuj WorldManager.travel()
3. Přidej /map a /travel příkazy
4. Test: Hráč může cestovat mezi lokacemi
```

### Fáze 2: PvP Integration (2-3 hodiny)
```
1. Implementuj check_pvp_rules() v combat.py
2. Aktualizuj /duel příkaz aby kontroloval PvP zóny
3. Přidej /pvp_attack příkaz
4. Test: PvP funguje pouze v PvP zónách
```

### Fáze 3: Tábory (3-4 hodiny)
```
1. Implementuj WorldManager.create_camp()
2. Implementuj WorldManager.enter_camp()
3. Přidej /camp_* příkazy
4. Test: Hráči mohou vytvářet a používat tábory
```

### Fáze 4: Economy (2-3 hodiny)
```
1. Implementuj gathering systém
2. Implementuj /gather příkaz
3. Implementuj /inventory příkaz
4. Test: Hráči mohou sbírat zdroje
```

### Fáze 5: Polish (2-3 hodiny)
```
1. Přidej embeds pro lepší UI
2. Přidej error handling
3. Přidej persistence (save/load)
4. Test: Vše funguje smooth
```

**Celkový čas: 12-16 hodin práce**

---

## 🚀 Jak Začít Implementovat

### Rychlý Start (30 minut = minimum viable product):

1. **Otevři `systems/world_manager.py`** (nový soubor)
```python
import json
from models.world import LOCATIONS, PlayerWorldState

class WorldManager:
    def __init__(self):
        self.locations = LOCATIONS
        self.players = {}  # {discord_id: PlayerWorldState}
    
    def get_player(self, player_id):
        if player_id not in self.players:
            self.players[player_id] = PlayerWorldState(player_id=player_id)
        return self.players[player_id]
    
    def get_player_location(self, player_id):
        player = self.get_player(player_id)
        return self.locations[player.current_location]
```

2. **Otevři `commands/world_commands.py`** (nový soubor)
```python
import discord
from discord import app_commands

async def setup(bot):
    @bot.tree.command(name="map")
    async def map_command(interaction: discord.Interaction):
        embed = discord.Embed(title="🗺️ Mapa Světa", color=0x00ff00)
        
        safe_zones = "🛡️ **Bezpečné zóny:**\n- Prasinky\n- Bradavice\n- Šikmá ulička"
        pvp_zones = "⚔️ **PvP zóny:**\n- Zapovězený les\n- Obrtlá ulička"
        
        embed.add_field(name="Safe Zones", value=safe_zones, inline=False)
        embed.add_field(name="PvP Zones", value=pvp_zones, inline=False)
        
        await interaction.response.send_message(embed=embed)
```

3. **Aktualizuj `bot.py`** (přidej na konec __init__)
```python
from systems.world_manager import WorldManager
from commands import world_commands

class DuelBot(commands.Bot):
    def __init__(self):
        # ... existující init ...
        
        # === OPEN WORLD ===
        self.world_manager = WorldManager()
    
    async def setup_hook(self):
        # ... existující setup ...
        
        # Setup world commands
        await world_commands.setup(self)
```

4. **Spusť a test:**
```bash
python bot.py
# V Discordu: /map
# Mělo by fungovat!
```

---

## 📖 Template Files (Začni tady!)

### Template: `systems/world_manager.py`
```python
"""World Manager - Správa světa, lokací, táborů"""

import json
import time
from typing import Optional, List, Dict
from models.world import LOCATIONS, PlayerWorldState, Camp

class WorldManager:
    def __init__(self):
        self.locations = LOCATIONS
        self.players: Dict[int, PlayerWorldState] = {}
        self.camps: Dict[str, Camp] = {}
        
    def get_player(self, player_id: int) -> PlayerWorldState:
        """Získej nebo vytvoř hráče"""
        if player_id not in self.players:
            self.players[player_id] = PlayerWorldState(player_id=player_id)
        return self.players[player_id]
    
    # TODO: Implementuj zbytek funkcí podle plánu výše
```

### Template: `commands/world_commands.py`
```python
"""World Commands - Discord příkazy pro open world"""

import discord
from discord import app_commands

async def setup(bot):
    """Setup all world commands"""
    
    @bot.tree.command(name="map", description="Zobraz mapu světa")
    async def map_command(interaction: discord.Interaction):
        # TODO: Implementuj
        await interaction.response.send_message("🗺️ Mapa - TODO")
    
    # TODO: Přidej zbytek příkazů
```

---

## 💡 Tips Pro Implementaci

### 1. Začni Malé
Naimplementuj jen `/map` a `/travel` nejdřív.
Pak postupně přidávej features.

### 2. Použij Existující Combat
Nepřepisuj combat systém! Jen zavolej existující funkce:
```python
from models.combat import CombatEngine

def initiate_pvp(attacker_id, target_id):
    # Kontrola PvP
    if not can_pvp(...):
        return False
    
    # Použij existující combat!
    combat = CombatEngine(attacker, target)
    combat.start_duel()
```

### 3. Discord Embeds
Používej embeds pro hezčí výstupy:
```python
embed = discord.Embed(title="🗺️ Mapa", color=0x00ff00)
embed.add_field(name="Lokace", value="Prasinky")
await interaction.response.send_message(embed=embed)
```

### 4. Error Handling
```python
try:
    world_manager.travel(player_id, destination)
except Exception as e:
    await interaction.response.send_message(f"❌ Error: {e}")
```

---

## 🎓 Potřebuješ Pomoc?

### Dokumentace:
- `PVP_SYSTEM_EXPLAINED.md` - Jak funguje PvP
- `OPEN_WORLD_GUIDE.md` - Herní mechaniky
- `README_OPENWORLD.md` - Quick start

### Struktura:
Vše je připravené v `models/world.py` - jen potřebuješ napsat manager a příkazy!

### Community:
Pokud něco není jasné, můžeš:
1. Přečíst dokumentaci výše
2. Podívat se na existující `bot.py` jak fungují příkazy
3. Zkusit implementovat podle templates

---

**Good luck! Systém je designově hotový, jen potřebuje implementaci! 🚀**
