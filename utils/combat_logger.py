"""
Combat Logger Integration - Propojení combat systému s Discord loggerem
Automaticky loguje všechny bojové akce do Discord kanálu
"""

import asyncio
from typing import Optional, Dict, Any
from discord_logger import DiscordLogger
from models.player import Player


class CombatLogger:
    """
    Wrapper pro Discord logger specificky pro combat systém
    Volá se z CombatManager během souboje
    """
    
    def __init__(self, discord_logger: Optional[DiscordLogger] = None):
        """
        Args:
            discord_logger: Instance DiscordLogger (může být None pro testování)
        """
        self.discord_logger = discord_logger
        self.enabled = discord_logger is not None
    
    
    def _run_async(self, coroutine):
        """
        Helper pro spuštění async funkce
        """
        if not self.enabled:
            return
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(coroutine)
            else:
                loop.run_until_complete(coroutine)
        except Exception as e:
            print(f"⚠️ Chyba při combat loggingu: {e}")
    
    
    def log_duel_start(
        self,
        duel_id: str,
        player1: Player,
        player2: Player,
        location: str = "Neznámá lokace"
    ):
        """
        ⚔️ Loguje začátek souboje
        
        Volá se při startu duelu v CombatManager.start_duel()
        """
        if not self.enabled:
            return
        
        self._run_async(
            self.discord_logger.log_duel_start(
                duel_id=duel_id,
                player1_id=player1.discord_id,
                player1_name=player1.name,
                player2_id=player2.discord_id,
                player2_name=player2.name,
                location=location
            )
        )
    
    
    def log_spell_cast(
        self,
        duel_id: str,
        turn_number: int,
        caster: Player,
        spell_name: str,
        target: Player,
        result: str,
        damage_description: Optional[str] = None
    ):
        """
        🎯 Loguje seslání kouzla
        
        Volá se po každém spell cast v CombatManager.execute_turn()
        
        Args:
            duel_id: ID souboje
            turn_number: Číslo tahu
            caster: Hráč který sesílá
            spell_name: Název kouzla
            target: Cílový hráč
            result: "hit", "miss", "blocked", "dodged" atd.
            damage_description: Popis následků (volitelné)
        """
        if not self.enabled:
            return
        
        self._run_async(
            self.discord_logger.log_combat_action(
                duel_id=duel_id,
                turn_number=turn_number,
                caster_name=caster.name,
                spell_name=spell_name,
                target_name=target.name,
                result=result,
                damage_description=damage_description
            )
        )
    
    
    def log_injury_dealt(
        self,
        player: Player,
        injury_description: str,
        body_part: str,
        severity: int,
        bleeding_rate: float
    ):
        """
        🩹 Loguje způsobené zranění
        
        Volá se když hráč dostane zranění
        """
        if not self.enabled:
            return
        
        self._run_async(
            self.discord_logger.log_injury(
                player_id=player.discord_id,
                player_name=player.name,
                injury_description=injury_description,
                body_part=body_part,
                severity=severity,
                bleeding_rate=bleeding_rate
            )
        )
    
    
    def log_duel_end(
        self,
        duel_id: str,
        winner: Player,
        loser: Player,
        duration_seconds: float,
        total_turns: int
    ):
        """
        🏆 Loguje konec souboje
        
        Volá se při ukončení duelu v CombatManager.end_duel()
        """
        if not self.enabled:
            return
        
        # Spočítej finální statistiky
        winner_injuries = sum(len(bp.injuries) for bp in winner.body.values())
        loser_injuries = sum(len(bp.injuries) for bp in loser.body.values())
        
        final_stats = {
            "winner_blood": winner.blood_volume,
            "loser_blood": loser.blood_volume,
            "winner_injuries": winner_injuries,
            "loser_injuries": loser_injuries
        }
        
        self._run_async(
            self.discord_logger.log_duel_end(
                duel_id=duel_id,
                winner_id=winner.discord_id,
                winner_name=winner.name,
                loser_id=loser.discord_id,
                loser_name=loser.name,
                duration_seconds=duration_seconds,
                total_turns=total_turns,
                final_stats=final_stats
            )
        )
    
    
    def log_death(
        self,
        player: Player,
        cause_of_death: str,
        killer: Optional[Player] = None,
        location: Optional[str] = None
    ):
        """
        💀 Loguje smrt hráče
        
        Volá se když hráč zemře
        """
        if not self.enabled:
            return
        
        killer_name = killer.name if killer else None
        
        self._run_async(
            self.discord_logger.log_death(
                player_id=player.discord_id,
                player_name=player.name,
                cause_of_death=cause_of_death,
                killer_name=killer_name,
                location=location
            )
        )
    
    
    def disable(self):
        """Vypne logování"""
        self.enabled = False
    
    
    def enable(self):
        """Zapne logování (pokud je discord_logger nastaven)"""
        if self.discord_logger:
            self.enabled = True
