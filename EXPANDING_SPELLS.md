# 📚 Rozšiřování Databáze Kouzel

Tento guide ti ukáže jak přidat všechna zbývající kouzla z dokumentu do bota.

## 📊 Současný Stav

✅ **Implementováno: 32 kouzel**
- Všechny klíčové kouzla z kanonického příběhu
- Pokrývá všechny základní kategorie

⏳ **Zbývá: ~170+ kouzel**
- Většina z nich jsou varianty nebo méně používaná kouzla
- Můžeš je přidat postupně podle potřeby

## 🎯 Jak Přidat Nové Kouzlo

### 1. Najdi Kouzlo v Původním Dokumentu

Příklad z dokumentu:
```
Aresto Momentum

Výrazně zpomalí pád. Použito Hermionou v pátém díle při útěku ze Síně věšteb...
```

### 2. Vytvoř Záznam v `spell_database.py`

```python
"aresto_momentum": {
    # ZÁKLADNÍ INFO
    "name_cs": "Aresto Momentum",
    "name_en": "Aresto Momentum",
    "incantation": "Aresto Momentum",
    
    # KATEGORIZACE
    "type": "utility",           # combat, defensive, healing, utility, advanced
    "category": "motion_control", # Vlastní kategorie
    "difficulty": 6,             # 1-10
    "cooldown": 8.0,             # sekundy
    
    # PŘEDPOKLADY (optional)
    "prerequisites": ["intermediate_magic"],
    
    # EFEKTY
    "effects": {
        "primary": {
            "type": "slow_fall",
            "reduction": 80,      # % snížení rychlosti pádu
            "duration": 5.0       # sekundy
        }
    },
    
    # VIZUÁL
    "visual": {
        "color": "blue",
        "sound": "cushion",
        "projectile": False
    },
    
    # METADATA
    "description": "Výrazně zpomalí pád. Známé také jako polštářové kouzlo.",
    "learning_time_hours": 24,
    "canon_users": ["Hermiona Grangerová", "Albus Brumbál"],
    "legality": "legal",
    "reputation_impact": 0
},
```

### 3. Přidej Logiku do `combat.py` (Pokud Potřeba)

Většina kouzel funguje s existující logikou. Pokud potřebuješ speciální efekt:

```python
# V _apply_spell_effects() přidej:

elif category == 'motion_control':
    # Aresto Momentum
    if spell['incantation'] == 'Aresto Momentum':
        # Sníží poškození z pádu
        target.conditions.add(Condition.FEATHER_FALLING)
```

## 🗂️ Kategorie Kouzel

### Útočné (`category: ...`)
- `death` - Avada Kedavra
- `cutting` - Sectumsempra, Diffindo
- `explosive` - Confringo, Bombarda
- `stunning` - Stupefy
- `torture` - Cruciatus
- `fire` - Incendio
- `destruction` - Reducto

### Obranné
- `shield` - Protego
- `shield_area` - Protego Maxima
- `deflection` - Odražení kouzel

### Léčivé
- `healing` - Obecné léčení
- `minor_healing` - Episkey
- `specific_counter` - Vulnera Sanentur
- `awakening` - Enervate

### Kontrolní
- `control` - Obecná kontrola
- `binding` - Petrificus Totalus
- `suspension` - Levicorpus
- `hindering` - Impedimenta
- `disarming` - Expelliarmus

### Utility
- `summoning` - Accio
- `levitation` - Wingardium Leviosa
- `light` - Lumos
- `darkness` - Nox
- `water` - Aguamenti
- `locking` - Colloportus
- `unlocking` - Alohomora
- `memory_modification` - Obliviate
- `revealing` - Aparecium
- `concealment` - Muffliato

### Speciální
- `protection_light` - Expecto Patronum
- `boggart_specific` - Riddikulus
- `transformation` - Transfigurační kouzla

## 📝 Šablony pro Různé Typy Kouzel

### Šablona: Útočné Kouzlo

```python
"kouzlo_id": {
    "name_cs": "Název",
    "name_en": "Name",
    "incantation": "Formule",
    "type": "combat",
    "category": "kategorie",  # cutting, explosive, fire...
    "difficulty": 5,
    "cooldown": 8.0,
    "prerequisites": [],
    "effects": {
        "primary": {
            "type": "damage_type",  # burn, cut, explosion, stun
            "severity": "moderate",  # light, moderate, severe, critical
            "body_parts": ["torso", "limbs"],  # které části může zasáhnout
            "blockable": True,
            "dodge_chance": 0.4
        },
        "secondary": {
            "type": "bleeding",  # optional sekundární efekt
            "bleeding_rate": 3.0
        }
    },
    "visual": {"color": "red", "sound": "blast", "projectile": True},
    "description": "Popis z dokumentu",
    "counter_spells": ["protego"],
    "learning_time_hours": 16,
    "legality": "legal_combat",
    "reputation_impact": 0
}
```

### Šablona: Obranné Kouzlo

```python
"kouzlo_id": {
    "name_cs": "Název",
    "incantation": "Formule",
    "type": "defensive",
    "category": "shield",
    "difficulty": 5,
    "cooldown": 5.0,
    "effects": {
        "primary": {
            "type": "shield",
            "duration": 3.0,
            "blocks": ["most_spells"],
            "reflects": True,
            "effectiveness": 80  # %
        }
    },
    "visual": {"color": "blue", "sound": "shield_up", "projectile": False},
    "description": "...",
    "learning_time_hours": 20,
    "legality": "legal"
}
```

### Šablona: Léčivé Kouzlo

```python
"kouzlo_id": {
    "name_cs": "Název",
    "incantation": "Formule",
    "type": "healing",
    "category": "minor_healing",
    "difficulty": 4,
    "cooldown": 10.0,
    "effects": {
        "heals": [
            "minor_cuts",
            "bruises",
            "minor_fractures"
        ],
        "cannot_heal": [
            "deep_wounds",
            "severed_limbs"
        ],
        "healing_time": "instant"
    },
    "description": "...",
    "learning_time_hours": 16,
    "legality": "legal",
    "reputation_impact": 5
}
```

### Šablona: Utility Kouzlo

```python
"kouzlo_id": {
    "name_cs": "Název",
    "incantation": "Formule",
    "type": "utility",
    "category": "light",  # nebo summoning, locking...
    "difficulty": 2,
    "cooldown": 1.0,
    "effects": {
        "primary": {
            "type": "light",  # nebo summon, lock...
            "duration": "until_canceled",
            "radius": 5.0
        }
    },
    "combat_use": {
        "blind_chance": 10,  # optional - může být užitečné v boji
    },
    "description": "...",
    "learning_time_hours": 2,
    "legality": "legal"
}
```

## 🚀 Rychlé Přidání Kouzel z Dokumentu

### Prioritní Kouzla k Přidání

1. **Bojová (vysoká priorita)**
   ```
   - Impedimenta
   - Flipendo
   - Rictusempra
   - Tarantallegra
   - Furnunculus
   - Densaugeo
   ```

2. **Obranná**
   ```
   - Fianto Duri
   - Repello Inimicum
   - Cave Inimicum
   - Salvio Hexia
   ```

3. **Utility**
   ```
   - Reparo
   - Evanesco
   - Geminio
   - Aparecium
   - Silencio
   ```

4. **Transformační**
   ```
   - Vera Verto
   - Draconifors
   - Avis
   - Serpensortia
   ```

### Automatické Generování (Pro 100+ kouzel)

Pokud chceš přidat všechna kouzla rychle:

```python
# Vytvoř helper script: bulk_add_spells.py

spells_to_add = {
    "Impedimenta": {
        "category": "hindering",
        "difficulty": 5,
        "cooldown": 6.0,
        "effect_type": "slow_freeze"
    },
    "Flipendo": {
        "category": "knockback",
        "difficulty": 3,
        "cooldown": 3.0,
        "effect_type": "push"
    },
    # ... atd
}

for spell_name, data in spells_to_add.items():
    spell_id = spell_name.lower()
    # Generuj záznam automaticky
    generate_spell_entry(spell_id, data)
```

## ⚠️ Důležité Poznámky

### Balance
- Smrtící kouzla: cooldown 30s+
- Silná bojová: cooldown 10-20s
- Běžná bojová: cooldown 3-8s
- Utility: cooldown 1-5s

### Obtížnost
1-2: Začátečník (Lumos, Alohomora)
3-4: Základní bojové (Stupefy, Expelliarmus)
5-6: Pokročilé (Protego, Impedimenta)
7-8: Expertní (Confringo, Protego Maxima)
9: Temná magie (Sectumsempra, Cruciatus)
10: Master level (Avada Kedavra, Patronus)

### Reputace
- Běžná kouzla: 0
- Pomáhající: +5 až +10
- Temná magie: -10 až -30
- Zakázané kletby: -40 až -50

## 📄 Příklady z Dokumentu

### 1. Glisseo (Skluzavka)
```python
"glisseo": {
    "name_cs": "Glisseo",
    "name_en": "Glisseo",
    "incantation": "Glisseo",
    "type": "utility",
    "category": "transformation",
    "difficulty": 5,
    "cooldown": 10.0,
    "effects": {
        "primary": {
            "type": "transform_stairs",
            "target": "stairs_only",
            "duration": 30.0,
            "result": "slide"
        }
    },
    "visual": {"color": "silver", "sound": "smooth", "projectile": False},
    "description": "Promění schodiště ve skluzavku.",
    "learning_time_hours": 16,
    "legality": "legal",
    "canon_users": ["Hermiona Grangerová"]
}
```

### 2. Ferula (Obvazy)
```python
"ferula": {
    "name_cs": "Ferula",
    "name_en": "Ferula",
    "incantation": "Ferula",
    "type": "healing",
    "category": "stabilization",
    "difficulty": 3,
    "cooldown": 5.0,
    "effects": {
        "heals": ["stabilizes_fractures", "bandages_wounds"],
        "cannot_heal": ["broken_bones_fully", "deep_wounds"],
        "healing_time": "instant",
        "provides": "temporary_support"
    },
    "visual": {"color": "white", "sound": "wrap", "projectile": False},
    "description": "Vykouzlí obvazy a omotá je kolem zraněné části těla.",
    "learning_time_hours": 8,
    "legality": "legal",
    "canon_users": ["Remus Lupin"]
}
```

### 3. Rictusempra (Lechtání)
```python
"rictusempra": {
    "name_cs": "Rictusempra",
    "name_en": "Rictusempra",
    "incantation": "Rictusempra",
    "type": "combat",
    "category": "tickling",
    "difficulty": 4,
    "cooldown": 5.0,
    "effects": {
        "primary": {
            "type": "tickling_curse",
            "duration": 10.0,
            "incapacitates": True,
            "causes": "uncontrollable_laughter"
        }
    },
    "visual": {"color": "silver", "sound": "giggle", "projectile": True},
    "description": "Lechtací kletba. Oběť se svíjí smíchy.",
    "counter_spells": ["finite", "protego"],
    "learning_time_hours": 12,
    "legality": "legal",
    "canon_users": ["Harry Potter"],
    "book_appearance": "Harry Potter a Tajemná komnata"
}
```

## 🎓 Tip: Batch Processing

Pro rychlé přidání mnoha kouzel najednou:

```python
# batch_spells.py
import json

basic_template = {
    "type": "combat",
    "difficulty": 5,
    "cooldown": 5.0,
    "prerequisites": [],
    "legality": "legal",
    "reputation_impact": 0,
    "learning_time_hours": 12
}

spells_from_doc = [
    ("Impedimenta", "hindering", "Zpomalí nebo zastaví cíl"),
    ("Flipendo", "knockback", "Odhodí cíl"),
    # ... more
]

for incant, category, desc in spells_from_doc:
    spell_id = incant.lower()
    spell = {
        **basic_template,
        "name_cs": incant,
        "name_en": incant,
        "incantation": incant,
        "category": category,
        "description": desc,
        # Add specific effects based on category
    }
    print(f'"{spell_id}": {json.dumps(spell, indent=2)},')
```

## ✅ Checklist Po Přidání Kouzla

- [ ] Přidáno do `SPELLS_DATABASE` v `spell_database.py`
- [ ] Spuštěn `python spell_database.py` (vygeneruje spells.json)
- [ ] Pokud speciální efekt: Přidána logika do `combat.py`
- [ ] Testováno v botu: `/learn <kouzlo>` a `/cast <kouzlo>`
- [ ] Zkontrolován balance (cooldown, difficulty)
- [ ] Aktualizován README pokud významné kouzlo

## 📞 Potřebuješ Pomoc?

Pokud máš problémy s přidáním kouzla nebo nejsi si jistý jak ho implementovat, otevři Issue na GitHubu nebo se zeptej v komunitě!

---

**Happy Spell Crafting! 🪄✨**
