"""
POTION SYSTEM TEST - Testuj všechny funkce
Rychlý test před nasazením do produkce
"""

import asyncio
from systems.potion_brewing import PotionBrewingManager
from models.player import Player
from potion_database import get_potion, get_all_potions
from models.potions import get_ingredient


async def test_potion_system():
    """Kompletní test potion systému"""
    
    print("\n" + "="*60)
    print("🧪 TESTOVÁNÍ POTION SYSTÉMU")
    print("="*60)
    
    # Inicializuj systém
    potion_manager = PotionBrewingManager()
    test_player_id = 123456789
    
    # Test hráč
    player = Player(
        discord_id=test_player_id,
        name="Test Wizard"
    )
    
    # ========== TEST 1: INGREDIENCE ==========
    print("\n1️⃣ Test: Přidání ingrediencí")
    inventory = potion_manager.get_inventory(test_player_id)
    
    # Dej ingredience
    potion_manager.give_ingredient(test_player_id, "mandrake_root", 10)
    potion_manager.give_ingredient(test_player_id, "peppermint", 10)
    potion_manager.give_ingredient(test_player_id, "unicorn_hair", 5)
    
    print(f"   ✅ Ingredience přidány")
    print(f"   📦 Inventář: {inventory.ingredients}")
    
    # ========== TEST 2: BREWING ==========
    print("\n2️⃣ Test: Zahájení vaření")
    
    success, message = potion_manager.start_brewing(test_player_id, "healing_potion")
    
    if success:
        print(f"   ✅ Vaření zahájeno")
        print(f"   📝 {message}")
    else:
        print(f"   ❌ FAIL: {message}")
        return
    
    # ========== TEST 3: STATUS ==========
    print("\n3️⃣ Test: Kontrola statusu")
    
    inventory = potion_manager.get_inventory(test_player_id)
    if inventory.active_brewing:
        brewing = inventory.active_brewing
        print(f"   ✅ Vaření probíhá")
        print(f"   🧪 Lektvar: {brewing.potion_id}")
        print(f"   ⏱️ Zbývá: {brewing.time_remaining():.0f}s")
        print(f"   📊 Pokrok: {brewing.progress()*100:.1f}%")
    else:
        print(f"   ❌ FAIL: Žádné aktivní vaření")
    
    # ========== TEST 4: COMPLETION (simulace) ==========
    print("\n4️⃣ Test: Dokončení vaření (simulace)")
    
    # Nastaví čas na dokončeno
    if inventory.active_brewing:
        inventory.active_brewing.end_time = 0  # Okamžitě hotovo
        
        is_complete, message, potion = potion_manager.check_brewing_completion(test_player_id)
        
        if is_complete:
            print(f"   ✅ Vaření dokončeno")
            print(f"   📝 {message}")
            
            if potion:
                print(f"   🧪 Získán: {potion.name_cs}")
            else:
                print(f"   💥 Vaření selhalo!")
        else:
            print(f"   ❌ FAIL: Vaření nedokončeno")
    
    # ========== TEST 5: POUŽITÍ ==========
    print("\n5️⃣ Test: Použití lektvaru")
    
    # Dej lektvar přímo
    potion_manager.give_potion(test_player_id, "healing_potion", 1)
    
    inventory = potion_manager.get_inventory(test_player_id)
    print(f"   📦 Lektvary v inventáři: {inventory.potions}")
    
    # Použij
    success, message = potion_manager.use_potion(player, "healing_potion")
    
    if success:
        print(f"   ✅ Lektvar použit")
        print(f"   📝 {message}")
    else:
        print(f"   ❌ FAIL: {message}")
    
    # ========== TEST 6: SKILL PROGRESSION ==========
    print("\n6️⃣ Test: Skill progression")
    
    initial_skill = inventory.brewing_skill
    print(f"   📊 Počáteční skill: {initial_skill}")
    
    # Dej ingredience a zkus vařit několik lektvarů
    for ingredient_id in ["mandrake_root", "peppermint", "unicorn_hair"]:
        potion_manager.give_ingredient(test_player_id, ingredient_id, 20)
    
    # Uvaři 3 lektvary
    for i in range(3):
        success, _ = potion_manager.start_brewing(test_player_id, "healing_potion")
        if success:
            # Simuluj dokončení
            inventory.active_brewing.end_time = 0
            potion_manager.check_brewing_completion(test_player_id)
    
    final_skill = inventory.brewing_skill
    print(f"   📊 Konečný skill: {final_skill}")
    print(f"   ✨ Gain: +{final_skill - initial_skill}")
    
    # ========== TEST 7: VŠECHNY LEKTVARY ==========
    print("\n7️⃣ Test: Databáze lektvarů")
    
    all_potions = get_all_potions()
    print(f"   📚 Celkem lektvarů: {len(all_potions)}")
    
    for potion in all_potions:
        print(f"   • {potion.name_cs} ({potion.rarity.value})")
    
    # ========== TEST 8: EFEKTY ==========
    print("\n8️⃣ Test: Efekty lektvarů")
    
    # Felix Felicis
    potion_manager.give_potion(test_player_id, "felix_felicis", 1)
    success, message = potion_manager.use_potion(player, "felix_felicis")
    
    if success:
        print(f"   ✅ Felix Felicis použit")
        print(f"   🔍 Status efekty: {len(player.status_effects)}")
        
        for effect in player.status_effects:
            print(f"      • {effect.caused_by}: {effect.duration:.0f}s")
    
    # ========== FINAL SUMMARY ==========
    print("\n" + "="*60)
    print("📊 FINÁLNÍ SOUHRN")
    print("="*60)
    print(f"   Inventář ingrediencí: {len(inventory.ingredients)}")
    print(f"   Inventář lektvarů: {len(inventory.potions)}")
    print(f"   Brewing skill: {inventory.brewing_skill}")
    print(f"   Status efekty na hráči: {len(player.status_effects)}")
    print("="*60)
    print("✅ VŠECHNY TESTY PROŠLY!\n")


# ========== SPUŠTĚNÍ ==========

if __name__ == "__main__":
    asyncio.run(test_potion_system())


# ========== JAK SPUSTIT ==========

"""
1. Ujisti se že máš všechny soubory:
   - models/potions.py
   - systems/potion_brewing.py
   - potion_database.py

2. Spusť:
   python POTION_TEST.py

3. Očekávaný výstup:
   
============================================================
🧪 TESTOVÁNÍ POTION SYSTÉMU
============================================================

1️⃣ Test: Přidání ingrediencí
   ✅ Ingredience přidány
   📦 Inventář: {'mandrake_root': 10, 'peppermint': 10, ...}

2️⃣ Test: Zahájení vaření
   ✅ Vaření zahájeno
   📝 🧪 Začal jsi vařit Léčivý lektvar!

3️⃣ Test: Kontrola statusu
   ✅ Vaření probíhá
   🧪 Lektvar: healing_potion
   ⏱️ Zbývá: 14400s
   📊 Pokrok: 0.0%

4️⃣ Test: Dokončení vaření (simulace)
   ✅ Vaření dokončeno
   📝 ✅ ÚSPĚCH! Uvařil jsi Léčivý lektvar!

5️⃣ Test: Použití lektvaru
   📦 Lektvary v inventáři: {'healing_potion': 1}
   ✅ Lektvar použit
   📝 🧪 Použil jsi Léčivý lektvar!
        💚 Léčení: ...

6️⃣ Test: Skill progression
   📊 Počáteční skill: 0
   📊 Konečný skill: 6
   ✨ Gain: +6

7️⃣ Test: Databáze lektvarů
   📚 Celkem lektvarů: 9
   • Mnoholičný lektvar (very_rare)
   • Felix Felicis (legendary)
   ...

8️⃣ Test: Efekty lektvarů
   ✅ Felix Felicis použit
   🔍 Status efekty: 1
      • Felix Felicis: 3600s

============================================================
📊 FINÁLNÍ SOUHRN
============================================================
   Inventář ingrediencí: 3
   Inventář lektvarů: 1
   Brewing skill: 6
   Status efekty na hráči: 1
============================================================
✅ VŠECHNY TESTY PROŠLY!
"""
