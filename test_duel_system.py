"""
KOMPLEXNÍ TESTOVACÍ SKRIPT PRO DUELOVÝ SYSTÉM
Postupně testuje všechny komponenty duelu:
1. Player vytvoření a inicializace
2. Spell databáze a cooldowny
3. Combat engine a damage výpočty
4. Duel state management
5. Embed rendering
6. Action view components
7. Kompletní duel simulace
"""

import sys
import time
from typing import List, Dict
from dataclasses import dataclass


# Test configuration
@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    duration: float


class DuelSystemTester:
    """Komplexní tester pro duelový systém"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.total_tests = 0
        self.passed_tests = 0
    
    def log(self, message: str, level: str = "INFO"):
        """Logování s barevným výstupem"""
        colors = {
            "INFO": "\033[94m",     # Modrá
            "SUCCESS": "\033[92m",  # Zelená
            "ERROR": "\033[91m",    # Červená
            "WARNING": "\033[93m",  # Žlutá
        }
        reset = "\033[0m"
        print(f"{colors.get(level, '')}{message}{reset}")
    
    def run_test(self, test_name: str, test_func):
        """Spustí jednotlivý test"""
        self.total_tests += 1
        self.log(f"\n{'='*60}")
        self.log(f"TEST {self.total_tests}: {test_name}", "INFO")
        self.log(f"{'='*60}")
        
        start_time = time.time()
        try:
            test_func()
            duration = time.time() - start_time
            self.passed_tests += 1
            self.results.append(TestResult(test_name, True, "PASS", duration))
            self.log(f"✅ PASSED in {duration:.3f}s", "SUCCESS")
            return True
        except Exception as e:
            duration = time.time() - start_time
            self.results.append(TestResult(test_name, False, str(e), duration))
            self.log(f"❌ FAILED: {e}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")
            return False
    
    def print_summary(self):
        """Vytiskne celkový přehled testů"""
        self.log(f"\n\n{'='*60}")
        self.log("TESTOVACÍ PŘEHLED", "INFO")
        self.log(f"{'='*60}")
        
        for i, result in enumerate(self.results, 1):
            status = "✅ PASS" if result.passed else "❌ FAIL"
            level = "SUCCESS" if result.passed else "ERROR"
            self.log(f"{i}. {result.name}: {status} ({result.duration:.3f}s)", level)
            if not result.passed:
                self.log(f"   Důvod: {result.message}", "ERROR")
        
        self.log(f"\n{'='*60}")
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        self.log(f"CELKEM: {self.passed_tests}/{self.total_tests} testů prošlo ({success_rate:.1f}%)", 
                "SUCCESS" if self.passed_tests == self.total_tests else "WARNING")
        self.log(f"{'='*60}\n")


def test_1_imports():
    """Test 1: Import všech potřebných modulů"""
    print("Importuji models.player...")
    from models.player import Player, PlayerDatabase, BodyPart, Condition
    
    print("Importuji models.combat...")
    from models.combat import CombatEngine, CombatAction, DuelState
    
    print("Importuji spell_database...")
    from spell_database import SPELLS_DATABASE
    
    print("Importuji duel_system_improved...")
    from duel_system_improved import (
        AdvancedDuelManager,
        DuelEmbedBuilder,
        DuelActionView,
        DuelSpellSelect
    )
    
    print(f"✓ Načteno {len(SPELLS_DATABASE)} kouzel ze spell databáze")
    assert len(SPELLS_DATABASE) > 0, "Spell databáze je prázdná!"
    
    # Kontrola typů kouzel
    spell_types = set()
    for spell in SPELLS_DATABASE.values():
        spell_types.add(spell.get('type', 'unknown'))
    
    print(f"✓ Nalezeny typy kouzel: {spell_types}")
    assert 'combat' in spell_types, "Chybí combat kouzla!"
    assert 'defensive' in spell_types, "Chybí defensive kouzla!"
    
    # Kontrola utility a control kouzel (nové!)
    has_utility = 'utility' in spell_types
    has_control = 'control' in spell_types
    
    if has_utility:
        print("✓ Nalezena UTILITY kouzla")
    else:
        print("⚠ VAROVÁNÍ: Žádná utility kouzla v databázi")
    
    if has_control:
        print("✓ Nalezena CONTROL kouzla")
    else:
        print("⚠ VAROVÁNÍ: Žádná control kouzla v databázi")


def test_2_player_creation():
    """Test 2: Vytvoření a inicializace hráčů"""
    from models.player import Player, PlayerDatabase
    
    print("Vytvářím databázi hráčů...")
    db = PlayerDatabase()
    
    print("Vytvářím Player 1...")
    player1 = Player(123456, "TestPlayer1")
    assert player1.discord_id == 123456
    assert player1.name == "TestPlayer1"
    assert player1.consciousness == 100.0
    assert player1.blood_volume == 5000.0
    print(f"✓ Player 1: {player1.name}, HP: {player1.consciousness}%, Krev: {player1.blood_volume}ml")
    
    print("Vytvářím Player 2...")
    player2 = Player(789012, "TestPlayer2")
    assert player2.discord_id == 789012
    assert player2.name == "TestPlayer2"
    print(f"✓ Player 2: {player2.name}, HP: {player2.consciousness}%, Krev: {player2.blood_volume}ml")
    
    # Kontrola body parts
    print("Kontroluji části těla...")
    assert 'head' in player1.body
    assert 'torso' in player1.body
    assert 'left_arm' in player1.body
    assert 'right_arm' in player1.body
    print(f"✓ Player má {len(player1.body)} částí těla")
    
    # Kontrola známých kouzel
    print("Kontroluji známá kouzla...")
    assert len(player1.known_spells) > 0, "Hráč nemá žádná známá kouzla!"
    print(f"✓ Player 1 zná {len(player1.known_spells)} kouzel")
    print(f"  Příklad kouzel: {list(player1.known_spells)[:5]}")


def test_3_spell_database():
    """Test 3: Spell databáze a typy kouzel"""
    from spell_database import SPELLS_DATABASE
    
    # Kontrola struktury kouzel
    print("Analyzuji strukturu kouzel...")
    
    spell_by_type = {
        'combat': [],
        'defensive': [],
        'healing': [],
        'control': [],
        'utility': []
    }
    
    for spell_id, spell in SPELLS_DATABASE.items():
        spell_type = spell.get('type', 'unknown')
        if spell_type in spell_by_type:
            spell_by_type[spell_type].append(spell_id)
    
    for spell_type, spells in spell_by_type.items():
        print(f"✓ {spell_type.upper()}: {len(spells)} kouzel")
        if len(spells) > 0:
            # Ukázka prvního kouzla
            example_spell = SPELLS_DATABASE[spells[0]]
            print(f"  Příklad: {example_spell['name_cs']} ({example_spell['incantation']})")
    
    # Kontrola povinných polí
    print("\nKontroluji povinná pole v kouzlech...")
    required_fields = ['name_cs', 'incantation', 'type', 'cooldown', 'difficulty']
    
    for spell_id, spell in list(SPELLS_DATABASE.items())[:5]:  # Kontrola prvních 5
        for field in required_fields:
            assert field in spell, f"Kouzlo {spell_id} nemá pole {field}!"
        print(f"✓ {spell['name_cs']}: všechna pole OK")


def test_4_combat_engine():
    """Test 4: Combat engine a damage výpočty"""
    from models.player import Player
    from models.combat import CombatEngine, CombatAction
    from spell_database import SPELLS_DATABASE
    
    print("Inicializuji combat engine...")
    engine = CombatEngine(SPELLS_DATABASE)
    
    print("Vytvářím testovací hráče...")
    attacker = Player(111, "Attacker")
    defender = Player(222, "Defender")
    
    # Přidej nějaká kouzla
    if 'expelliarmus' in SPELLS_DATABASE:
        attacker.known_spells.add('expelliarmus')
        print("✓ Útočník zná Expelliarmus")
    
    if 'protego' in SPELLS_DATABASE:
        defender.known_spells.add('protego')
        print("✓ Obránce zná Protego")
    
    # Test útoku
    print("\nTestuji útok...")
    initial_consciousness = defender.consciousness
    
    # Najdi combat spell
    combat_spell = None
    for spell_id, spell in SPELLS_DATABASE.items():
        if spell['type'] == 'combat' and spell_id in attacker.known_spells:
            combat_spell = spell_id
            break
    
    if combat_spell:
        result = engine.execute_action(
            attacker, 
            defender, 
            CombatAction.ATTACK, 
            combat_spell
        )
        print(f"✓ Útok proveden: {result}")
        
        # Kontrola že se něco stalo
        if defender.consciousness < initial_consciousness:
            print(f"✓ Obránce utrpěl damage: {initial_consciousness - defender.consciousness:.1f}%")
    else:
        print("⚠ Není dostupné žádné combat kouzlo pro test")


def test_5_duel_state():
    """Test 5: Duel state management"""
    from models.player import Player
    from models.combat import CombatEngine, DuelState
    from spell_database import SPELLS_DATABASE
    
    print("Vytvářím duel state...")
    player1 = Player(111, "Duelist1")
    player2 = Player(222, "Duelist2")
    
    engine = CombatEngine(SPELLS_DATABASE)
    duel = DuelState(player1, player2, engine)
    
    assert duel.player1 == player1
    assert duel.player2 == player2
    assert duel.current_turn == 1
    assert duel.is_active == True
    
    print(f"✓ Duel vytvořen: {duel.duel_id}")
    print(f"✓ Hráč 1: {duel.player1.name}")
    print(f"✓ Hráč 2: {duel.player2.name}")
    print(f"✓ Tah: {duel.current_turn}")
    print(f"✓ Aktivní: {duel.is_active}")
    
    # Test historie
    duel.add_to_history("Test zápis do historie")
    assert len(duel.history) > 0
    print(f"✓ Historie funguje: {len(duel.history)} záznamů")


def test_6_embed_builder():
    """Test 6: Embed builder komponenty"""
    from models.player import Player
    from duel_system_improved import DuelEmbedBuilder
    from spell_database import SPELLS_DATABASE
    
    print("Vytvářím testovací hráče...")
    player1 = Player(111, "EmbedPlayer1")
    player2 = Player(222, "EmbedPlayer2")
    
    # Přidej kouzla
    available_spells = []
    for spell_id, spell in list(SPELLS_DATABASE.items())[:5]:
        player1.known_spells.add(spell_id)
        available_spells.append((spell_id, spell))
    
    print(f"✓ Player1 má {len(available_spells)} kouzel pro embed")
    
    # Test vytvoření embedu
    print("\nVytvářím embed pro Player 1...")
    embed_data = DuelEmbedBuilder.create_player_embed(
        player=player1,
        opponent=player2,
        is_player1=True,
        turn_number=1,
        is_your_turn=True,
        available_spells=available_spells,
        state_message="Test embed"
    )
    
    # Kontrola embed struktury (simulace Discord Embed)
    assert hasattr(embed_data, 'title')
    assert hasattr(embed_data, 'description')
    assert hasattr(embed_data, 'color')
    
    print(f"✓ Embed vytvořen")
    print(f"  Titulek: {embed_data.title}")
    print(f"  Popis: {embed_data.description[:50]}...")
    print(f"  Barva: {embed_data.color}")
    print(f"  Počet polí: {len(embed_data.fields)}")


def test_7_spell_select():
    """Test 7: Spell select komponenty"""
    from models.player import Player
    from spell_database import SPELLS_DATABASE
    
    # Nemůžeme plně testovat Discord UI komponenty bez Discordu,
    # ale můžeme testovat logiku výběru kouzel
    
    print("Vytvářím testovacího hráče...")
    player = Player(111, "SpellSelectPlayer")
    
    # Přidej různé typy kouzel
    spell_types = {'combat': 0, 'defensive': 0, 'healing': 0, 'control': 0, 'utility': 0}
    
    for spell_id, spell in SPELLS_DATABASE.items():
        spell_type = spell.get('type', 'unknown')
        if spell_type in spell_types and spell_types[spell_type] < 3:
            player.known_spells.add(spell_id)
            spell_types[spell_type] += 1
    
    print("✓ Hráč zná kouzla:")
    for spell_type, count in spell_types.items():
        print(f"  {spell_type}: {count} kouzel")
    
    # Kontrola dostupných kouzel podle typu
    print("\nKontroluji filtrování kouzel...")
    for spell_type in ['combat', 'defensive', 'healing', 'control', 'utility']:
        available = [
            spell_id for spell_id in player.known_spells
            if spell_id in SPELLS_DATABASE and SPELLS_DATABASE[spell_id].get('type') == spell_type
        ]
        print(f"✓ {spell_type}: {len(available)} dostupných")


def test_8_cooldown_system():
    """Test 8: Cooldown systém"""
    from models.player import Player
    from spell_database import SPELLS_DATABASE
    import time
    
    print("Vytvářím testovacího hráče...")
    player = Player(111, "CooldownPlayer")
    
    # Najdi kouzlo s cooldownem
    test_spell = None
    for spell_id, spell in SPELLS_DATABASE.items():
        if spell.get('cooldown', 0) > 0:
            test_spell = spell_id
            player.known_spells.add(spell_id)
            break
    
    if not test_spell:
        print("⚠ Žádné kouzlo s cooldownem nenalezeno")
        return
    
    spell = SPELLS_DATABASE[test_spell]
    print(f"✓ Testovací kouzlo: {spell['name_cs']} (CD: {spell['cooldown']}s)")
    
    # První použití
    can_cast, cooldown = player.can_cast_spell_now(test_spell)
    assert can_cast, "Kouzlo by mělo být použitelné"
    print("✓ Kouzlo je dostupné před prvním použitím")
    
    # Použij kouzlo
    player.use_spell(test_spell)
    print("✓ Kouzlo použito")
    
    # Hned po použití
    can_cast, cooldown = player.can_cast_spell_now(test_spell)
    assert not can_cast, "Kouzlo by nemělo být dostupné hned po použití"
    print(f"✓ Kouzlo je na cooldownu: {cooldown:.1f}s zbývá")
    
    # Simuluj čas
    print("Simuluji běh času...")
    player.last_spell_cast[test_spell] -= (spell['cooldown'] + 1)  # Odečti cooldown
    
    can_cast, cooldown = player.can_cast_spell_now(test_spell)
    assert can_cast, "Kouzlo by mělo být znovu dostupné"
    print("✓ Kouzlo je znovu dostupné po cooldownu")


def test_9_damage_calculation():
    """Test 9: Damage kalkulace a body parts"""
    from models.player import Player
    from models.combat import CombatEngine
    from spell_database import SPELLS_DATABASE
    
    print("Vytvářím testovacího hráče...")
    player = Player(111, "DamagePlayer")
    
    initial_consciousness = player.consciousness
    initial_blood = player.blood_volume
    
    print(f"Počáteční stav: HP={initial_consciousness}%, Krev={initial_blood}ml")
    
    # Simuluj poškození
    print("\nSimuluji poškození hlavy...")
    player.body['head'].take_damage(10.0)
    
    # Update hráče (aplikuj bleeding)
    player.update(1.0)
    
    print(f"✓ Vědomí po zranění: {player.consciousness:.1f}%")
    print(f"✓ Krev po zranění: {player.blood_volume:.1f}ml")
    
    # Kontrola bleeding
    bleeding = player.body['head'].get_total_bleeding()
    if bleeding > 0:
        print(f"✓ Krvácení z hlavy: {bleeding:.2f} ml/s")


def test_10_complete_duel_simulation():
    """Test 10: Kompletní simulace souboje"""
    from models.player import Player
    from models.combat import CombatEngine, CombatAction, DuelState
    from spell_database import SPELLS_DATABASE
    from duel_system_improved import AdvancedDuelManager
    
    print("=== KOMPLETNÍ SIMULACE SOUBOJE ===\n")
    
    # Vytvoř hráče
    print("Vytvářím soubojníky...")
    player1 = Player(111, "Harry Potter")
    player2 = Player(222, "Draco Malfoy")
    
    # Přidej kouzla různých typů
    print("\nPřipravuji kouzla...")
    
    # Player 1 - různá kouzla
    combat_spells = [sid for sid, s in SPELLS_DATABASE.items() if s.get('type') == 'combat']
    defensive_spells = [sid for sid, s in SPELLS_DATABASE.items() if s.get('type') == 'defensive']
    control_spells = [sid for sid, s in SPELLS_DATABASE.items() if s.get('type') == 'control']
    utility_spells = [sid for sid, s in SPELLS_DATABASE.items() if s.get('type') == 'utility']
    
    for spell_list, name in [(combat_spells[:3], 'combat'), 
                              (defensive_spells[:2], 'defensive'),
                              (control_spells[:1], 'control'),
                              (utility_spells[:1], 'utility')]:
        for spell_id in spell_list:
            player1.known_spells.add(spell_id)
            player2.known_spells.add(spell_id)
        print(f"✓ Přidáno {len(spell_list)} {name} kouzel")
    
    print(f"\nHarry zná {len(player1.known_spells)} kouzel")
    print(f"Draco zná {len(player2.known_spells)} kouzel")
    
    # Vytvoř combat engine a duel
    print("\nZahajuji souboj...")
    engine = CombatEngine(SPELLS_DATABASE)
    duel = DuelState(player1, player2, engine)
    
    # Vytvoř duel manager
    manager = AdvancedDuelManager(engine)
    manager.start_duel(12345, duel, None, None)
    
    print(f"✓ Souboj zahájen: {duel.duel_id}")
    
    # Simuluj několik tahů
    print("\n" + "="*60)
    print("SIMULACE SOUBOJE")
    print("="*60)
    
    max_turns = 5
    for turn in range(1, max_turns + 1):
        print(f"\n--- TAH {turn} ---")
        
        # Player 1 útočí
        if combat_spells:
            spell_id = combat_spells[turn % len(combat_spells)]
            result = engine.execute_action(player1, player2, CombatAction.ATTACK, spell_id)
            spell = SPELLS_DATABASE[spell_id]
            print(f"Harry: {spell['name_cs']} → {result}")
        
        # Player 2 se brání
        if defensive_spells:
            spell_id = defensive_spells[0]
            result = engine.execute_action(player2, player1, CombatAction.DEFEND, spell_id)
            spell = SPELLS_DATABASE[spell_id]
            print(f"Draco: {spell['name_cs']} → {result}")
        
        # Update hráčů
        player1.update(1.0)
        player2.update(1.0)
        
        # Statistiky
        print(f"\nStatistiky po tahu {turn}:")
        print(f"  Harry: HP={player1.consciousness:.1f}%, Krev={player1.blood_volume:.0f}ml")
        print(f"  Draco: HP={player2.consciousness:.1f}%, Krev={player2.blood_volume:.0f}ml")
        
        # Kontrola konce
        if not player1.is_alive():
            print("\n🏆 DRACO VYHRÁL! Harry byl poražen!")
            break
        if not player2.is_alive():
            print("\n🏆 HARRY VYHRÁL! Draco byl poražen!")
            break
    
    print("\n" + "="*60)
    print("KONEC SIMULACE")
    print("="*60)
    
    # Ukončení souboje
    winner = player1 if player1.is_alive() else player2
    loser = player2 if player1.is_alive() else player1
    manager.end_duel(12345, winner, loser)
    
    print(f"\n✓ Souboj byl ukončen")
    print(f"✓ Celkem tahů: {duel.current_turn}")
    print(f"✓ Vítěz: {winner.name}")


def main():
    """Hlavní funkce - spustí všechny testy"""
    tester = DuelSystemTester()
    
    tester.log("╔═══════════════════════════════════════════════════════════╗")
    tester.log("║   KOMPLEXNÍ TEST DUELOVÉHO SYSTÉMU - Harry Potter RPG    ║")
    tester.log("╚═══════════════════════════════════════════════════════════╝\n")
    
    # Seznam testů
    tests = [
        ("Import modulů a spell databáze", test_1_imports),
        ("Vytvoření a inicializace hráčů", test_2_player_creation),
        ("Spell databáze a typy kouzel", test_3_spell_database),
        ("Combat engine a damage výpočty", test_4_combat_engine),
        ("Duel state management", test_5_duel_state),
        ("Embed builder komponenty", test_6_embed_builder),
        ("Spell select komponenty", test_7_spell_select),
        ("Cooldown systém", test_8_cooldown_system),
        ("Damage kalkulace a body parts", test_9_damage_calculation),
        ("Kompletní simulace souboje", test_10_complete_duel_simulation),
    ]
    
    # Spusť všechny testy
    for test_name, test_func in tests:
        tester.run_test(test_name, test_func)
    
    # Výsledný přehled
    tester.print_summary()
    
    # Exit code
    sys.exit(0 if tester.passed_tests == tester.total_tests else 1)


if __name__ == "__main__":
    main()
