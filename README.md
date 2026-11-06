# 🪄 Harry Potter Realistický Soubojový Bot

Unikátní Discord bot pro **realistické souboje** inspirované světem Harry Pottera. **Žádné HP, žádné XP** - pouze reálné důsledky kouzel a znalost magie!

## ⚡ Unikátní Featury

### 🩸 Realistický Systém Zranění
- **Žádné HP** - místo toho konkrétní zranění (řezy, zlomeniny, popáleniny...)
- **Vykrvácení** - postupná ztráta krve a vědomí
- **Části těla** - každá část může být zraněna samostatně (hlava, trup, ruce, nohy)
- **Permanentní následky** - ztráta končetiny, jizvy, trvalé poškození

### 💀 Smrt je Trvalá
- Když zemřeš, **ztratíš všechna naučená kouzla**
- Můžeš vytvořit novou postavu, ale začínáš od začátku
- Tvá statistika (kolikrát jsi zemřel) zůstává

### 📚 Znalostní Systém
- **Musíš se kouzla naučit** než je můžeš použít
- Každé kouzlo má **obtížnost** a **čas učení**
- Některá kouzla vyžadují **předpoklady** (jiná kouzla, znalost temné magie...)
- **200+ kouzel** z kanonického Harry Potter světa

### ⚔️ Soubojový Systém
- **Přesnost sesílání** závisí na tvém stavu (zranění, bolest, únava...)
- **Kombinace kouzel** - obrana + útok ve stejném tahu
- **Cooldowny** - silnější kouzla mají delší cooldown
- **Protikouzla** - některá kouzla se dají blokovat nebo odrazit

### 🎯 Realistické Efekty Kouzel

#### Avada Kedavra
- ☠️ Okamžitá smrt (nelze blokovat Protegem!)
- Použití = **-50 reputace** (Dark Wizard)

#### Sectumsempra
- 🩸 Hluboké řezné rány
- 💉 Těžké krvácení (smrt za ~60s bez léčení)
- 🏥 Léčitelné pouze **Vulnera Sanentur**
- Jizvy zůstávají navždy

#### Cruciatus
- 😱 Extrémní bolest (10/10)
- 🧠 Může způsobit **šílenství**
- Psychologické trauma

#### Stupefy
- 😵 Dočasné bezvědomí (5-15s)
- 🤕 Možný úraz při pádu
- Probouzení: **Enervate**

## 🚀 Instalace a Spuštění

### 1. Požadavky
- Python 3.10+
- Discord účet a server
- Discord Bot Token

### 2. Získání Discord Bot Tokenu

1. Jdi na [Discord Developer Portal](https://discord.com/developers/applications)
2. Klikni "New Application"
3. Pojmenuj aplikaci (např. "HP Duel Bot")
4. Jdi na "Bot" sekci
5. Klikni "Add Bot"
6. **Zkopíruj Token** (klikni "Reset Token" a pak "Copy")
7. V "Privileged Gateway Intents" aktivuj:
   - ✅ Server Members Intent
   - ✅ Message Content Intent

### 3. Pozvání Bota na Server

1. Jdi na "OAuth2" > "URL Generator"
2. Vyber **scopes**: `bot`, `applications.commands`
3. Vyber **bot permissions**:
   - Send Messages
   - Embed Links
   - Read Message History
   - Use Slash Commands
4. Zkopíruj vygenerovanou URL a otevři ji v prohlížeči
5. Vyber server a potvrď

### 4. Instalace Bota

```bash
# 1. Stáhni nebo naklonuj tento projekt
cd hp_duel_bot

# 2. Nainstaluj závislosti
pip install -r requirements.txt

# 3. Nastav token (Linux/Mac)
export DISCORD_BOT_TOKEN='tvůj_token_zde'

# Nebo (Windows)
set DISCORD_BOT_TOKEN=tvůj_token_zde

# 4. Spusť bota
python bot.py
```

### 5. Alternativně: .env soubor

Vytvoř soubor `.env`:
```
DISCORD_BOT_TOKEN=tvůj_token_zde
GUILD_ID=id_serveru  # Optional, pro rychlejší testování
```

Pak spusť:
```bash
python bot.py
```

## 📋 Příkazy Bota

### Základní Příkazy

| Příkaz | Popis |
|--------|-------|
| `/status` | Zobraz svůj současný stav (zdraví, zranění, vědomí) |
| `/spells` | Seznam všech dostupných kouzel |
| `/spells category:utok` | Filtruj kouzla podle kategorie |
| `/learn <kouzlo>` | Začni se učit kouzlo |
| `/help` | Zobrazí nápovědu |

### Soubojové Příkazy

| Příkaz | Popis |
|--------|-------|
| `/duel @hráč` | Vyzvi hráče k souboji |
| `/cast <kouzlo>` | Sesli kouzlo v souboji |
| `/defend` | Připrav Protego (štít) |
| `/dodge` | Pokus se uhnout |
| `/heal <kouzlo> [@hráč]` | Vyléč zranění |

### Ostatní

| Příkaz | Popis |
|--------|-------|
| `/revive` | Vytvoř novou postavu po smrti |

## 🎮 Jak Hrát

### 1. Začátek

```
/status
```
Podívej se na svůj stav. Na začátku znáš 3 základní kouzla: Lumos, Nox, Alohomora.

### 2. Učení Kouzel

```
/spells category:utok
/learn stupefy
```
Nauč se Stupefy (omráčovací kouzlo). V demo módu se naučíš okamžitě.

### 3. Výzva k Souboji

```
/duel @souper
```
Vyzvi někoho k souboji. Druhý hráč musí přijmout tlačítkem.

### 4. Souboj

```
/cast stupefy      # Útok omráčovacím kouzlem
/cast expelliarmus # Odzbroj soupeře
/defend            # Připrav štít
```

### 5. Léčení

```
/heal episkey      # Vyléč lehká zranění
/heal vulnera_sanentur  # Vyléč zranění od Sectumsempra
```

### 6. Po Smrti

```
/revive
```
Vytvoř novou postavu. **Ztratíš všechna naučená kouzla!**

## ⚠️ Důležité Koncepty

### Přesnost Sesílání

Tvá šance na úspěšné seslání kouzla závisí na:
- ✅ Zdraví dominantní ruky (80% funkčnost = 80% šance)
- 🤕 Bolest (-20% při vysoké bolesti)
- 🩸 Krvácení (-10% při těžkém krvácení)
- 😱 Šok (-60% po vážném zranění)
- 👁️ Slepota (-90%)

**Příklad:**
```
Základní přesnost: 80%
Zraněná pravá ruka: -30% → 50%
Těžká bolest: -20% → 30%
Krvácení: -10% → 20%

Výsledná šance: 20%! (téměř nemožné seslat kouzlo)
```

### Vykrvácení

```
Krvácení stupňů:
1. Lehké (2-5 ml/s)   → -5% přesnost každých 10s
2. Střední (5-10 ml/s) → -10% přesnost každých 10s
3. Těžké (10-20 ml/s)  → -25% přesnost + kolaps za 30s
4. Kritické (20+ ml/s) → Smrt za 10s
```

### Části Těla

| Část | Důsledky Zranění |
|------|------------------|
| **Hlava** | Otřes mozku, ztráta vědomí, smrt |
| **Trup** | Vnitřní krvácení, selhání orgánů |
| **Pravá ruka** | Nemůžeš držet hůlku! |
| **Levá ruka** | Snížená přesnost |
| **Nohy** | Nemůžeš se pohybovat, uhnout |

### Kletby Které Se Nepromíjejí

🚫 **Zakázané použití = Azkaban v reálném světě**

1. **Avada Kedavra** - Smrtící kletba
   - Cooldown: 30s
   - Reputace: -50
   
2. **Crucio** - Mučicí kletba
   - Cooldown: 20s
   - Reputace: -45
   
3. **Imperio** - Ovládací kletba
   - Cooldown: 15s
   - Reputace: -40

## 📊 Kategorie Kouzel

### Útočná Kouzla (category:utok)
- Stupefy, Expelliarmus, Petrificus Totalus
- Sectumsempra, Confringo, Bombarda
- Incendio, Reducto, Diffindo
- Avada Kedavra, Crucio

### Obranná Kouzla (category:obrana)
- Protego, Protego Maxima
- Protego Horribilis, Protego Totalum

### Léčivá Kouzla (category:leceni)
- Episkey (lehká zranění)
- Vulnera Sanentur (Sectumsempra)
- Enervate (probouzení)
- Ferula (obvazy)

### Kontrolní Kouzla (category:kontrola)
- Levicorpus, Impedimenta
- Immobulus, Petrificus Totalus

### Utility (category:utility)
- Lumos, Nox
- Accio, Wingardium Leviosa
- Alohomora, Colloportus
- Aguamenti, Incendio

## 🏆 Reputační Systém

```
+30:  Expecto Patronum master
+10:  Protego Maxima master
+5:   Vítězství v poctivém souboji
0:    Neutrální
-10:  Použití Memory Charm
-25:  Použití Sectumsempra
-40:  Použití Imperio
-45:  Použití Crucio
-50:  Použití Avada Kedavra
```

**Důsledky nízké reputace:**
- Ostatní tě vidí jako Dark Wizard
- (Budoucí update: NPCs tě budou pronásledovat)

## 🔧 Pokročilé Funkce (Připravované)

### V Další Verzi
- [ ] **Lektvary** během souboje
- [ ] **Artefakty** (Neviditelný plášť, Elder Wand...)
- [ ] **Animagus** transformace
- [ ] **Patronus** specializace
- [ ] **NPCs** - trénuj proti AI
- [ ] **Story Mode** - kampaň
- [ ] **Tournaments** - turnaje hráčů
- [ ] **House Points** - týmový systém

### Možná v Budoucnu
- [ ] **Quidditch** mini-hra
- [ ] **Horcrux** systém
- [ ] **Time-Turner** mechaniky
- [ ] **Fidelius Charm** ukrývání
- [ ] **Economy** - koupit lektvary, hůlky

## 📁 Struktura Projektu

```
hp_duel_bot/
├── bot.py                 # Hlavní Discord bot
├── spell_database.py      # Databáze všech kouzel
├── models/
│   ├── player.py         # Systém hráče a těla
│   └── combat.py         # Soubojový engine
├── data/
│   ├── spells.json       # Uložená data kouzel
│   └── players.json      # Uložená data hráčů
├── requirements.txt       # Python závislosti
├── DESIGN.md             # Design dokument
└── README.md             # Tento soubor
```

## 🐛 Známé Problémy

1. **Learning Time** - Momentálně se kouzla učí okamžitě (pro demo)
   - Produkční verze bude mít skutečné časování
   
2. **Simultánní Akce** - Tahový systém může být zjednodušen
   - Real-time režim v budoucnu

3. **Balance** - Některá kouzla mohou být příliš silná/slabá
   - Feedback vítán!

## 💡 Tipy pro Hráče

### Pro Začátečníky
1. ✅ Nauč se **Protego** co nejdřív (obrana)
2. ✅ Nauč se **Episkey** (léčení)
3. ✅ Začni s **Stupefy** a **Expelliarmus**
4. ⚠️ **NEPOUŽÍVEJ** zakázaná kouzla - ztratíš reputaci
5. 🩸 Sleduj své krvácení! Léčení je klíčové.

### Pro Pokročilé
1. 🎯 Kombinuj obranu + útok
2. 🧠 Pamatuj si cooldowny
3. 💡 Využívej prostředí (krytí)
4. 🎭 Psychologická válka - strach z bolestivých kouzel
5. ⚔️ Cílení na specifické části těla

### Pro Experty
1. 🧙 Master Expecto Patronum
2. ⚫ Zvládni temnou magii (pokud si to můžeš dovolit)
3. 🎪 Kombinace kouzel (např. Incendio + Aguamenti = pára)
4. 🏆 Specializuj se na určitý styl boje

## 🤝 Přispívání

Chceš přidat nová kouzla? Opravit bug? Pull requesty vítány!

### Jak Přidat Kouzlo

1. Otevři `spell_database.py`
2. Přidej do `SPELLS_DATABASE`:
```python
"nove_kouzlo": {
    "name_cs": "České Jméno",
    "name_en": "English Name",
    "incantation": "Formule",
    "type": "combat",
    "category": "stunning",
    "difficulty": 5,
    "cooldown": 5.0,
    "effects": {
        "primary": {
            "type": "stun",
            # ...
        }
    },
    "description": "Popis kouzla",
    "learning_time_hours": 12,
}
```
3. Přidej logiku do `combat.py` pokud je potřeba

## 📞 Podpora

- **Issues**: GitHub Issues
- **Discord**: [připojit link]
- **Email**: [připojit email]

## 📜 License

MIT License - Dělej si co chceš!

## 🙏 Poděkování

- J.K. Rowling za vytvoření světa Harry Pottera
- Harry Potter Wiki za detailní informace o kouzlech
- Discord.py community

## ⚡ Bojuj Statečně!

**Remember: Smrt je trvalá. Každé rozhodnutí má váhu. Každé kouzlo má následky.**

*"It does not do to dwell on dreams and forget to live."* - Albus Dumbledore

---

**Version:** 1.0.0  
**Author:** Claude & User  
**Last Updated:** 2026-03-23
