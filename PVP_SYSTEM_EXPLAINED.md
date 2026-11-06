# 🗺️ Harry Potter Open World - PvP Systém

## ⚡ KLÍČOVÉ: Žádné NPC!

Tento systém je **čistě PvP zaměřený**:
- ❌ Žádní AI nepřátelé
- ❌ Žádné NPC bossové
- ❌ Žádní automatičtí soupeři
- ✅ Pouze hráči vs. hráči
- ✅ Player-driven economy
- ✅ Player-driven combat

---

## 🎮 Co Systém Obsahuje

### 1. **Mapa Světa** (15+ lokací)
```
Bezpečné zóny:
└─ Prasinky (spawn)
└─ Bradavice (škola)
└─ Šikmá ulička (obchody)
└─ Ministerstvo (questy)

PvP zóny:
└─ Zapovězený les (open PvP)
└─ Obrtlá ulička (open PvP)
└─ Godrikův důl (open PvP)
└─ Tajemná komnata (extreme PvP)
```

### 2. **Tábory (Player Camps)**
```python
# Hráč vytvoří tábor
/camp create "Můj tábor"

# Ochrana proti JINÝM HRÁČŮM
/camp protect cave_inimicum

# Jiný hráč může napadnout tábor!
/camp raid @opponent_camp

# Společný tábor
/camp invite @friend
```

### 3. **PvP Systém**
```python
# Zapni PvP (opt-in)
/pvp toggle

# Zaútoč na HRÁČE (ne NPC!)
/pvp attack @player

# Bounty na HRÁČE (ne NPC!)
/bounty claim @wanted_player

# Všechno combat je proti hráčům!
```

### 4. **Cestování**
```python
# Cestuj mezi lokacemi
/travel forbidden_forest

# Během cesty můžeš být napaden HRÁČEM
# Žádní random NPC encounters!
```

### 5. **Ekonomika (Player-Driven)**
```python
# Gathering zdrojů
/gather  # Sběr ingrediencí

# Trading s HRÁČI
/trade @player

# Prodej do NPC obchodu (ale to je jen ekonomický sink)
/shop sell moonstone
```

### 6. **Party Systém**
```python
# Skupina HRÁČŮ
/party create
/party invite @player

# Bojujte PROTI JINÝM HRÁČŮM
# Ne proti NPC!
```

---

## 🎯 Příklady PvP Scénářů

### Scénář 1: Ambush v Lese
```
Hráč A: Gathering v Zapovězeném lese
Hráč B: Číhá v mlze (zastírací kouzlo)
Hráč B: /pvp attack @HráčA
→ PvP souboj začíná!
→ Žádné NPC! Jen hráč proti hráči!
```

### Scénář 2: Camp Raid
```
Party 3 hráčů napadne tábor jiného hráče
/camp raid @victim_camp
→ Majitel tábora je notifikován
→ PvP obrana! (hráči vs hráči)
→ Žádné NPC guards!
```

### Scénář 3: Bounty Hunt
```
Hráč má bounty (wanted za PvP kills)
Bounty hunter: /bounty list
Bounty hunter: Cestuje do PvP zóny
Bounty hunter: /pvp attack @wanted_player
→ Souboj hráč vs hráč!
→ Winner dostane gold bounty
```

### Scénář 4: Resource War
```
Dva hráči chtějí stejný Unicorn Hair spot
Oba /gather ve stejný čas
Conflict vzniká
/pvp attack @competitor
→ PvP o resources! Žádné NPC!
```

---

## 🔧 Technická Implementace

### Core Principles
```python
# ✅ CORRECT: Player vs Player
if attacker.is_player() and target.is_player():
    initiate_pvp_combat()

# ❌ WRONG: Player vs NPC (NEIMPLEMENTOVÁNO!)
# if attacker.is_player() and target.is_npc():
#     # TENTO KÓD NEEXISTUJE!
```

### Combat Flow
```python
def initiate_combat(attacker_id: int, target_id: int):
    # Kontrola: jsou oba hráči?
    if not is_player(attacker_id) or not is_player(target_id):
        return False, "Combat pouze mezi hráči!"
    
    # Kontrola PvP zóny
    location = get_location(attacker_id)
    if not location.allows_pvp():
        return False, "Bezpečná zóna!"
    
    # START PvP (hráč vs hráč)
    start_pvp_duel(attacker_id, target_id)
```

### World State
```python
class WorldState:
    players: Dict[int, PlayerState]  # Jen hráči
    camps: Dict[str, Camp]           # Player-owned camps
    parties: Dict[str, Party]        # Player parties
    
    # ❌ Žádné NPC:
    # npcs: Dict[str, NPC]  # NEEXISTUJE!
    # enemies: List[Enemy]  # NEEXISTUJE!
```

---

## 🎮 Discord Commands (Finální Seznam)

### Svět & Navigace
```
/map                        - Mapa světa (bez NPC!)
/location                   - Kde jsem?
/travel <destination>       - Cestuj (můžeš být napaden hráčem)
/players_nearby             - Seznam hráčů v lokaci
```

### Tábory (Player vs Player)
```
/camp create <name>         - Vytvoř tábor
/camp protect <spell>       - Ochrana proti HRÁČŮM
/camp raid @camp            - Napadni tábor HRÁČE
/camp enter                 - Vstup do tábora
/camp leave                 - Opusť tábor
/camp invite @player        - Pozvi HRÁČE
```

### PvP (Player vs Player!)
```
/pvp toggle                 - Zapni/vypni PvP
/pvp attack @player         - Zaútoč na HRÁČE
/pvp stats                  - Tvoje PvP statistiky
/bounty list                - Wanted HRÁČI (ne NPC!)
/bounty claim @player       - Zabij wanted HRÁČE
```

### Economy (Player-Driven)
```
/gather                     - Sběr zdrojů
/trade @player              - Trading s HRÁČEM
/shop                       - NPC obchod (ekonomický sink)
/inventory                  - Tvůj inventář
```

### Party (Player Groups)
```
/party create               - Vytvoř skupinu HRÁČŮ
/party invite @player       - Pozvi HRÁČE
/party chat <msg>           - Chat pro HRÁČE
/party leave                - Opusť party
```

---

## 📊 Herní Statistiky (PvP Focus)

### Player Stats
```python
class PlayerStats:
    pvp_kills: int           # Kolik HRÁČŮ zabil
    pvp_deaths: int          # Kolikrát zemřel od HRÁČŮ
    bounty: int              # Wanted level (za PvP)
    camps_raided: int        # Kolik táborů HRÁČŮ napadl
    camps_defended: int      # Kolikrát obránil tábor
    
    # ❌ Žádné NPC stats:
    # npc_kills: int         # NEEXISTUJE!
    # bosses_defeated: int   # NEEXISTUJE!
```

### Leaderboard
```
Top PvP Hráči:
1. xXDarkLordXx - 47 kills
2. HermioneGranger - 32 kills
3. SnapeRules - 28 kills

Žádné "Top NPC Killers" - NPC neexistují!
```

---

## 🚀 Quick Start (Pro Hráče)

### 1. Spawn v Prasinkách (Safe Zone)
```
Spawneš jako nový hráč
/map - Podívej se na svět
Jsi v bezpečí - nelze tě napadnout
```

### 2. Nauč Se Základy
```
/shop - Kup si lektvar
/learn stupefy - Nauč se kouzlo
/gather - Sběr zdrojů
```

### 3. První PvP Experience
```
/travel hogwarts_grounds (consensual PvP)
/pvp toggle - Zapni PvP
Najdi jiného hráče s PvP ON
/pvp attack @player - Tvůj první souboj!
```

### 4. Open World PvP
```
/travel forbidden_forest (OPEN PvP!)
Kdokoliv tě může napadnout!
Žádné NPC - jen HRÁČI jsou nebezpeční!
```

---

## ⚠️ Co NENÍ ve Hře

❌ **NPC nepřátelé** - Neexistují
❌ **NPC bossové** - Neexistují  
❌ **PvE dungeons** - Neexistují
❌ **AI companions** - Neexistují
❌ **Questové NPC** - Quest board je automatický
❌ **NPC guards** - Bezpečnost = PvP pravidla

✅ **Pouze hráči proti hráčům!**

---

## 🎯 Design Philosophy

```
"Každé nebezpečí pochází od jiných hráčů"

- Vidíš hráče v lese? Může tě napadnout!
- Najdeš tábor? Je to tábor HRÁČE!
- Wanted list? Jsou to HRÁČI!
- Raid? Je to proti HRÁČŮM!

Žádné scripted encounters.
Žádné predictable spawns.
Pouze nepředvídatelnost LIDSKÝCH hráčů!
```

---

## 🔮 Budoucí Rozšíření (Stále PvP!)

### Možné Additions (Všechno PvP):
- **Guild Wars** - Guildy HRÁČŮ bojují
- **Territory Control** - HRÁČI kontrolují území
- **Siege Warfare** - HRÁČI útočí na pevnosti HRÁČŮ
- **Dueling Tournaments** - Turnaje HRÁČŮ
- **Bounty Contracts** - HRÁČI si dávají kontrakty na HRÁČE

### Co NEBUDE:
- ❌ Dungeon raids s NPC bossy
- ❌ NPC quest chains
- ❌ PvE content

---

**Užij si čistý PvP svět! ⚔️👥**

*"The world is shaped by those who dare to fight." - Player-driven world*
