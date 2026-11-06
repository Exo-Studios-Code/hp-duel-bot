# Harry Potter Realistický Soubojový Bot - Design Document

## 🎯 Hlavní Koncept
Žádné HP, žádné XP, žádné levely. Pouze **realistické důsledky kouzel** a **znalost magie**.

## 🧙 Systém Postavy

### Tělo (Body System)
```
┌─────────────┐
│    Hlava    │  - Vědomí, zrak, sluch
├─────────────┤
│    Trup     │  - Vitální orgány, dýchání
├──────┬──────┤
│ Levá │ Pravá│  - Držení hůlky, gesta
│ Paže │ Paže │
├──────┴──────┤
│ Levá │ Pravá│  - Pohyb, stabilita
│ Noha │ Noha │
└──────┴──────┘
```

Každá část může být:
- **Zdravá** (100% funkčnost)
- **Zraněná** (snížená funkčnost)
- **Vážně poškozená** (téměř nefunkční)
- **Zničená** (permanentní ztráta)

### Stavy (Conditions)
- **Krvácení** (Bleeding) - postupná ztráta vědomí
- **Bolest** (Pain) - snížená přesnost
- **Ochromení** (Paralysis) - nemožnost pohybu
- **Omráčení** (Stunned) - dočasná neschopnost
- **Slepota** (Blind) - nemůžeš cílit
- **Šok** (Shock) - po vážném zranění

## 📚 Znalostní Systém

### Učení Kouzel
- Každé kouzlo má **obtížnost** (1-10)
- Musíš ho **naučit** před použitím
- Učení vyžaduje **čas** a **praxi**
- Některá kouzla vyžadují **předpoklady**

**Příklad:**
```
Stupefy (Obtížnost: 3)
├── Předpoklad: Základy obrany
└── Čas učení: 1 den

Sectumsempra (Obtížnost: 9)
├── Předpoklad: Pokročilá magie, Černá magie
└── Čas učení: 7 dní
```

## ⚔️ Soubojový Systém

### Real-Time + Tahový Hybrid
1. **Přípravná fáze** (10s)
   - Postav se do pozice
   - Zvol strategii

2. **Akční fáze** (každý má 5s na reakci)
   - Sešli kouzlo NEBO
   - Braň se NEBO
   - Uhni NEBO
   - Kombinuj

3. **Resoluce** (okamžitá)
   - Kouzla se střetnou
   - Vyhodnotí se úspěch/selhání
   - Aplikují se efekty

### Kombinace Kouzel
```
Protego + Expelliarmus = "Štít a protiútok"
Stupefy + Stupefy = "Dvojí omráčení"
Incendio + Aqua Erupto = "Pára" (zastření)
```

## 🎪 Efekty Kouzel (Příklady)

### Avada Kedavra
```yaml
typ: Smrtící
efekt: Okamžitá smrt
obrana: Fyzické krytí (protego nefunguje!)
cooldown: 30s
následky: Žádné (cíl je mrtvý)
```

### Sectumsempra
```yaml
typ: Řezací
efekt: 
  - Hluboké řezné rány
  - Těžké krvácení
  - Bolest (8/10)
obrana: Protego (50% šance)
cooldown: 15s
léčení: Vulnera Sanentur (specifické!)
následky: Jizvy, možná ztráta končetiny
```

### Petrificus Totalus
```yaml
typ: Kontrolní
efekt:
  - Úplné ochromení
  - Pád na zem
  - Bezmocnost
trvání: Dokud není zrušeno
obrana: Protego, Finite
cooldown: 5s
následky: Možný úraz při pádu
```

### Stupefy
```yaml
typ: Omráčení
efekt:
  - Dočasné bezvědomí (5-15s)
  - Pád
obrana: Protego
cooldown: 3s
probuzení: Enervate
následky: Možný otřes mozku při pádu
```

## 🩺 Systém Léčení

### Není jako v hrách!
- **Episkey** - pouze lehká zranění (zlomený nos, drobné řezy)
- **Vulnera Sanentur** - specificky pro Sectumsempru
- **Ferula** - obvazy, stabilizace
- Těžká zranění vyžadují **profesionální léčitele**
- Některá zranění jsou **permanentní** (ztráta končetiny, jizvy)

## 🎲 Mechaniky

### Přesnost Sesílání
```
Základní šance = 80%
- Zranění pravé paže: -30%
- Bolest (vysoká): -20%
- Krvácení: -10%
- Únava: -5% za každý seslaný spell
= Výsledná šance: 15% (téměř nemožné!)
```

### Vykrvácení
```
Stupeň 1: -5% přesnosti/10s
Stupeň 2: -10% přesnosti/10s + mlhavé vidění
Stupeň 3: -25% přesnosti/10s + kolaps za 30s
Stupeň 4: Smrt za 10s
```

### Cooldowny (Realistické)
- **Jednoduché kouzlo** (Lumos): 1s
- **Běžné bojové** (Stupefy): 3s
- **Silné** (Expulso): 10s
- **Zakázané** (Cruciatus): 20s
- **Smrtící** (Avada Kedavra): 30s

## 🎮 Herní Režimy

### 1. Souboj (Duel)
Klasický 1v1 souboj do smrti/vzdání

### 2. Trénink (Training)
Učení kouzel, praktikování kombinací

### 3. Turnaj (Tournament)
Více hráčů, vyřazovací systém

### 4. Přežití (Survival)
Vlny nepřátel (NPC), jak dlouho přežiješ?

## 📊 Databáze Kouzel

Všech **200+ kouzel** z dokumentu, každé s:
- České i anglické jméno
- Kategorie (útok/obrana/podpora/kontrola/léčení)
- Obtížnost
- Efekty
- Cooldown
- Protikouzla
- Předpoklady
- Popis z kanonického zdroje

## 🔐 Permanence a Následky

### Smrt je Trvalá
- Žádné respawny
- Můžeš vytvořit novou postavu
- Tvá reputace a znalosti se NEZACHOVÁVAJÍ

### Vážná Zranění
- Ztráta končetiny = permanentní handicap
- Jizvy = psychologický efekt
- Trauma = PTSD z určitých kouzel

### Reputace
- Použití zakázaných kouzel = Dark Wizard
- Honorabilní souboje = Respekt
- Zabitých soupeřů = Fear Factor

## 🎯 Unikátní Featury

1. **Přátelský Oheň** - Ano! Můžeš zasáhnout spojence
2. **Prostředí** - Využívej terén (krytí, distance)
3. **Taktika** - Kouzla se liší rychlostí, silou, dosahem
4. **Psychologie** - Strach z bolestivých kouzel ovlivňuje chování
5. **Ekonomika** - Léčení stojí peníze, hůlky se mohou zlomit

## 🚀 Budoucí Rozšíření

- **Lektvary** během souboje
- **Artefakty** (neviditelný plášť, kámen vzkříšení...)
- **Patronus** specializace
- **Animagus** transformace
- **House Points** systém pro týmy
- **Quidditch** režim
- **Story Mode** s kampaní

---

**Filozofie designu:** 
"Každé rozhodnutí má váhu. Každé kouzlo má následky. Každý souboj je na život a na smrt."
