import sys
import os

# Zajištění importu z models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.player import Player
from models.combat import CombatEngine, Duel, CombatAction
from spell_database import SPELLS_DATABASE

def run_test_duel():
    print("🪄 --- TESTOVACÍ DUEL (FINÁLNÍ OPRAVA) --- 🪄\n")

    spell_db = SPELLS_DATABASE
    harry = Player(discord_id=1, name="Harry Potter")
    voldy = Player(discord_id=2, name="Lord Voldemort")

    # Harry se naučí kouzla
    harry.known_spells = {"sectumsempra", "expelliarmus", "protego"}
    
    engine = CombatEngine(spell_db)
    duel = Duel(duel_id="test-001", player1=harry, player2=voldy)

    print(f"Bojovníci: {harry.name} vs {voldy.name}")
    print(f"Počáteční krev: {voldy.blood_volume} ml")
    print("-" * 30)

    # --- TEST 1: Sectumsempra ---
    print("\n🩸 TEST 1: Harry sesílá Sectumsempra")
    result, msgs, _ = engine.cast_spell(harry, voldy, "sectumsempra")
    
    for msg in msgs:
        print(msg)

    # Zjištění počtu zranění (procházíme části těla v voldy.body)
    total_injuries = 0
    if hasattr(voldy, 'body'):
        for part_name, part in voldy.body.items():
            total_injuries += len(getattr(part, 'injuries', []))

    print(f"Stav Voldemorta: Krev {voldy.blood_volume}ml, Celkem ran: {total_injuries}")

    # --- TEST 2: Update (Krvácení) ---
    print("\n⏳ TEST 2: Průběh času (3 sekundy krvácení)")
    initial_blood = voldy.blood_volume
    
    for _ in range(3):
        voldy.update(1.0)
    
    blood_loss = initial_blood - voldy.blood_volume
    print(f"Stav Voldemorta po 3s: {voldy.blood_volume:.1f}ml (Ztráta: {blood_loss:.1f}ml)")

    if blood_loss > 0:
        print("✅ Krvácení funguje! Krev ubývá.")
    else:
        print("❌ Chyba: Krev neubyla, zkontroluj logiku update() v player.py")

    # --- TEST 3: Soubojové kolo ---
    print("\n⚔️ TEST 3: Tah souboje (Expelliarmus vs Protego)")
    turn_result = engine.execute_turn(
        duel, 
        p1_action=CombatAction.ATTACK, p1_spell="expelliarmus",
        p2_action=CombatAction.DEFEND, p2_spell="protego"
    )
    for res in turn_result.results:
        print(res)

if __name__ == "__main__":
    run_test_duel()