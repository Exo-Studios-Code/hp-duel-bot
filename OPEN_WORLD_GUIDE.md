# 🗺️ Open World System - Návod na Integraci

## 🎯 Co Přidává Open World Systém

### ✨ Hlavní Featury
1. **Mapa s lokacemi** - 15+ lokací (města, lesy, dungeons...)
2. **PvP zóny** - Bezpečné, Consensual, Open PvP
3. **Tábory** - Vlastní tábory s ochranou
4. **Cestování** - Realistické cestování mezi lokacemi
5. **Ekonomika** - Obchody, zdroje, gold
6. **Počasí** - Ovlivňuje viditelnost a boj
7. **Party system** - Skupiny hráčů
8. **Bounty system** - Odměny za PvP

---

## 📁 Struktura Souborů

```
hp_duel_bot/
├── models/
│   ├── player.py (existující)
│   ├── combat.py (existující)
│   └── world.py (✨ NOVÝ)
│
├── systems/
│   ├── world_manager.py (✨ NOVÝ)
│   └── economy.py (✨ NOVÝ)
│
├── commands/
│   └── world_commands.py (✨ NOVÝ)
│
├── bot.py (AKTUALIZOVANÝ)
└── data/
    ├── locations.json (auto-generován)
    └── world_state.json (auto-generován)
```

---

## 🎮 Nové Discord Příkazy

### Pohyb a Navigace
```
/map                    - Zobraz mapu světa
/location               - Kde jsem?
/travel <lokace>        - Cestuj někam
/players_nearby         - Kdo je poblíž?
```

### Tábory
```
/camp create <název>    - Vytvoř tábor
/camp enter <id>        - Vstup do tábora
/camp leave             - Opusť tábor
/camp protect <spell>   - Ochraň tábor kouzlem
/camp invite @hráč      - Pozvi hráče
/camp storage           - Zobraz sklad
```

### PvP
```
/pvp toggle             - Zapni/vypni PvP
/pvp attack @hráč       - Zaútoč na hráče
/bounty list            - Seznam wanted hráčů
/bounty claim @hráč     - Zabij wanted hráče
```

### Ekonomika
```
/shop                   - Otevři obchod
/gather                 - Seber zdroje
/inventory              - Tvůj inventář
/trade @hráč            - Vyměň si věci
```

### Party
```
/party create           - Vytvoř party
/party invite @hráč     - Pozvi do party
/party leave            - Opusť party
/party chat <zpráva>    - Party chat
```

---

## 🗺️ Mapa Světa

### 🛡️ Bezpečné Zóny (Safe - Žádné PvP)
- **Prasinky** (Hogsmeade) - Spawn point
- **Bradavice** (Hogwarts) - Škola
- **Šikmá ulička** (Diagon Alley) - Obchody
- **Ministerstvo** - Questy

### ⚠️ Částečně Bezpečné (Consensual PvP)
- **Okolí Bradavic** - Souboje jen se souhlasem
- **Děravý kotel** - Hospoda

### ⚔️ Nebezpečné Zóny (Open PvP!)
- **Zapovězený les** - Mlha, zdroje, vysoké riziko
- **Obrtlá ulička** - Temná magie
- **Vyjící bouda** - Opuštěné místo
- **Godrikův důl** - Bounty hunters
- **Tajemná komnata** - Extreme danger!

---

## 💡 Herní Mechaniky

### Cestování
```
Každá cesta trvá X minut (real-time)
Během cestování:
- Nemůžeš bojovat
- Nemůžeš obchodovat
- Můžeš být napaden (v nebezpečných zónách!)
```

### Tábory
```
Vytvoření: 5 minut práce + 50 gold
Životnost: 24 hodin (pak vyprší)
Ochrana: Cave Inimicum, Salvio Hexia, Repello Inimicum

V táboře:
✅ 2x rychlejší léčení
✅ Bezpečný odpočinek
✅ Sklad na věci
❌ Může být napaden (pokud není chráněný)
```

### PvP Systém
```
Bezpečné zóny: Žádné PvP
Consensual: Oba musí mít /pvp toggle ON
Open: Kdokoliv může zaútočit!
Flagged: Jen na arénách

Za zabití hráče:
+1 Kill
Možná získáš jeho věci (% šance)
Pokud zabíješ moc: BOUNTY (wanted)
```

### Bounty (Wanted) System
```
Zabiješ 3+ hráčů za den = WANTED
Bounty: 100-1000 gold (podle kills)

Každý tě může zabít pro odměnu!
Wanted hráči se ukazují na /bounty list
Bounty mizí po 24h bez PvP
```

### Ekonomika
```
Gold získáváš:
- Gathering zdrojů
- Zabíjení wanted hráčů
- Prodej věcí v obchodě
- Questy

Gold utrácíš za:
- Lektvary
- Ingredience
- Opravy
- Tábory
```

### Počasí Efekty
```
☀️ Clear: Normální podmínky
🌧️ Rain: -10% přesnost
⛈️ Storm: -25% přesnost, -20% viditelnost
🌫️ Fog: -40% viditelnost (těžší najít hráče)
❄️ Snow: -15% přesnost, stopy
🌙 Night: -30% viditelnost (Lumos pomůže)
```

---

## 🎯 Herní Strategie

### Pro Začátečníky
1. Zůstaň v bezpečných zónách
2. Nauč se základní kouzla
3. Gathering v Okolí Bradavic (consensual PvP)
4. Vytvoř si malý tábor

### Pro Pokročilé
1. Zapni PvP v bezpečné době
2. Průzkum Zapovězeného lesa
3. Vytvoř chráněný tábor
4. Join party pro bezpečnost

### Pro PvP Hráče
1. Lovci odměn (Bounty hunters)
2. Ambush v mlze
3. Camp raids
4. Kontrola dungeon vstupů

### Pro Peacemakery
1. Healer build
2. Pomáhej v táborech
3. Trading
4. Quest runner

---

## 🔧 Integrace do Existujícího Bota

### Krok 1: Přidej Soubory
Zkopíruj nové soubory do projektu

### Krok 2: Aktualizuj bot.py
```python
# Přidej import
from systems.world_manager import WorldManager
from commands.world_commands import setup_world_commands

# V __init__
self.world_manager = WorldManager()

# V setup_hook
await setup_world_commands(self)
```

### Krok 3: Aktualizuj combat.py
```python
# Kontrola PvP zóny před bojem
location = world_manager.get_player_location(player_id)
if not location.can_pvp(...):
    return False, "Nelze útočit v této zóně!"
```

### Krok 4: Spusť Bota
```bash
python bot.py
```

---

## 📊 Příklad Herního Session

```
Nový hráč spawne v Prasinkách

[10:00] /map
        → Vidí mapu, bezpečné/nebezpečné zóny

[10:02] /shop
        → Koupí základní lektvar (50g)

[10:05] /travel hogwarts_grounds
        → Cestuje 5 minut

[10:10] /gather
        → Najde Mandrake Root

[10:15] /camp create "Můj tábor"
        → Vytvoří tábor (stojí 50g)

[10:20] /camp protect cave_inimicum
        → Aktivuje ochranné kouzlo

[10:25] /pvp toggle
        → Zapne PvP (riskantní!)

[10:30] Druhý hráč ho napadne!
        → PvP souboj začíná

[10:35] Vyhrál! +100g bounty od wanted hráče

[10:40] /camp enter
        → Ukryje se do tábora na léčení
```

---

## 🎮 Herní Scénáře

### Scénář 1: Tábor Raid
```
Party 3 hráčů:
1. Scout najde nepřátelský tábor (Confundus scout)
2. Disable protection (Finite Incantatem)
3. Attack! (Stupefy, Expelliarmus)
4. Loot storage
5. Escape před reinforcements
```

### Scénář 2: Bounty Hunt
```
Bounty hunter:
1. /bounty list → Najde wanted hráče
2. /travel forbidden_forest → Cestuje do PvP zóny
3. Hidden (Zastírací kouzlo) → Stealth
4. Wait in fog → Čeká v mlze
5. Ambush! → Sectumsempra
6. Claim bounty → +500 gold
```

### Scénář 3: Gathering Party
```
Party 5 hráčů (consensual PvP):
1. Travel together → Zapovězený les
2. One defender → Protego watch
3. Others gather → Unicorn hair
4. Share loot equally
5. Return to camp safely
```

### Scénář 4: Safe Zone Trader
```
Peaceful player:
1. Gather resources in safe zones
2. /shop sell → Prodej v Prasinkách
3. Buy potions
4. /trade s jinými hráči
5. Never leave safe zones
```

---

## ⚙️ Nastavení a Balance

### Travel Times (minuty)
```
Krátké cesty:     2-5 min
Střední cesty:    10-20 min
Dlouhé cesty:     30-45 min
```

### Camp Costs
```
Vytvoření:        50 gold
Ochrana kouzlem:  20 gold / spell
Prodloužení:      25 gold / 24h
```

### Gathering
```
Cooldown:         5 minut
Success rate:     30-80% (podle lokace)
Value:            5-50 gold / item
```

### PvP Rewards
```
Kill:             10-50 gold (z oběti)
Bounty:           100-1000 gold
Loot chance:      30% (náhodná věc)
```

---

## 🐛 Anti-Grief Mechaniky

### Spawn Protection
- Nový hráč má 1 hodinu imunitu
- Nemůže být napaden
- Nemůže útočit

### Safe Logout
- /camp enter a logout = bezpečné
- Logout v PvP zóně = zůstaneš 30s in-game

### Bounty System
- PvP killeri jsou wanted
- Každý je může zabít
- Omezuje griefing

### Camp Raid Cooldown
- Tábor lze napadnout max 1x za 6h
- Dává čas na obranu

---

## 📞 Commands Cheat Sheet

| Příkaz | Popis | Zóna |
|--------|-------|------|
| `/map` | Mapa světa | Všude |
| `/travel <loc>` | Cestuj | Mimo tábor |
| `/camp create` | Nový tábor | Camping zóny |
| `/camp protect` | Ochrana | Vlastní tábor |
| `/pvp toggle` | Zapni PvP | Všude |
| `/pvp attack` | Útok na hráče | PvP zóny |
| `/gather` | Seber zdroje | Mimo město |
| `/shop` | Obchod | Města |
| `/party create` | Nová party | Všude |

---

**Užij si open-world Harry Potter svět! ⚡🗺️✨**

*"It is our choices that show what we truly are, far more than our abilities."*
