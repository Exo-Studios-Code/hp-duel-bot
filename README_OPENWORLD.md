# 🗺️ Open World System - README

## 🎯 Co Je Implementováno

### ✅ Core Systems (HOTOVÉ)
1. **Mapa** - 10 lokací s PvP zónami
2. **Cestování** - Real-time travel mezi lokacemi  
3. **Tábory** - Vytváření, ochrana, raid system
4. **PvP Zóny** - Safe, Consensual, Open PvP
5. **Ekonomika** - Gold, gathering, trading
6. **Party System** - Skupiny hráčů
7. **Bounty System** - Wanted hráči

### 🎮 Discord Commands (HOTOVÉ)
```
/map               - Zobraz mapu
/location          - Kde jsem?
/travel <loc>      - Cestuj někam
/players_nearby    - Kdo je v lokaci?

/camp_create       - Vytvoř tábor
/camp_enter        - Vstup do tábora
/camp_raid         - Napadni tábor

/pvp_toggle        - Zapni/vypni PvP
/pvp_attack        - Zaútoč na hráče
/bounty_list       - Wanted hráči

/gather            - Sběr zdrojů
/inventory         - Inventář
```

## 🚀 Jak To Spustit

### 1. Už je to v projektu!
Všechno je připravené v:
- `systems/world_manager.py`
- `commands/world_commands.py`
- `models/world.py`

### 2. Bot.py je aktualizovaný
World manager je už integrovaný.

### 3. Prostě spusť:
```bash
python bot.py
```

## 🎮 První Kroky

### Pro Nové Hráče:
```
1. /map                    # Podívej se na svět
2. /location               # Jsi v Prasinkách (safe zone)
3. /gather                 # Seber nějaké zdroje
4. /camp_create "Můj tábor"  # Vytvoř tábor
5. /pvp_toggle             # Až budeš ready pro PvP!
```

### Pro PvP Hráče:
```
1. /pvp_toggle             # Zapni PvP
2. /travel forbidden_forest  # Jdi do PvP zóny
3. /players_nearby         # Najdi hráče
4. /pvp_attack @hráč       # FIGHT!
```

## 📝 Důležité Poznámky

### Žádné NPC!
- Všechno combat je PvP (hráč vs hráč)
- Tábory patří hráčům
- Žádní AI nepřátelé

### PvP Zóny:
- 🛡️ **Safe** (Prasinky, Bradavice) - Nelze útočit
- ⚠️ **Consensual** (Okolí Bradavic) - Oba musí mít PvP ON
- ⚔️ **Open** (Zapovězený les) - Kdokoliv může zaútočit!

### Economy:
- Start gold: 100
- Gathering: 5-50 gold
- Camp: 50 gold
- Potions: 20-100 gold

## 🔧 Rozšíření

Chceš přidat více lokací?
1. Otevři `models/world.py`
2. Přidej do `LOCATIONS` dictionary
3. Hotovo!

Chceš přidat více příkazů?
1. Otevři `commands/world_commands.py`
2. Přidej nový `@bot.tree.command()`
3. Hotovo!

---

**Enjoy the PvP world! ⚔️**
