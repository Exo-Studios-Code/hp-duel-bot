"""
Discord Logger - Automatické logování důležitých herních eventů
Odesílá zprávy do Discord kanálů + přidává/odebírá role
"""

import discord
from discord import Embed, Color
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    """Úrovně logování"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    COMBAT = "combat"
    HEALTH = "health"


class DiscordChannels:
    """IDs Discord kanálů pro různé typy logů"""
    
    # Krevní status a kritické stavy
    BLOOD_STATUS = 1487590062895009944  # 🩸┃krevni-status-vitals
    
    # Bojové logy
    COMBAT_LOGS = 1487590052862230682   # 🩸┃zaznamy-boju-logs
    
    # Můžete přidat další kanály:
    GENERAL_LOGS = 1487590063809232959  # Obecné logy
    DEATHS = 1487590045467803804        # Úmrtí hráčů
    ACHIEVEMENTS = 1487590054833422418  # Achievementy


class DiscordRoles:
    """IDs Discord rolí"""
    
    # Kritický zdravotní stav
    CRITICAL_HEALTH = 1487595959922982923  # ⚠️ ┫ CRITICAL ┣ 🩸
    
    # Můžete přidat další role:
    # BLEEDING = 123456789      # Aktivní krvácení
    # UNCONSCIOUS = 123456789   # V bezvědomí
    # IN_COMBAT = 123456789     # V souboji


class DiscordLogger:
    """
    Hlavní logger pro Discord notifikace
    Posílá embedy do různých kanálů a spravuje role
    """
    
    def __init__(self, bot: discord.Client):
        """
        Args:
            bot: Discord bot instance (commands.Bot nebo discord.Client)
        """
        self.bot = bot
        self.enabled = True
        
        # Cache kanálů pro rychlejší přístup
        self._channel_cache: Dict[int, discord.TextChannel] = {}
    
    
    async def _get_channel(self, channel_id: int) -> Optional[discord.TextChannel]:
        """
        Získá kanál z cache nebo z Discord API
        """
        if channel_id in self._channel_cache:
            return self._channel_cache[channel_id]
        
        try:
            channel = await self.bot.fetch_channel(channel_id)
            if isinstance(channel, discord.TextChannel):
                self._channel_cache[channel_id] = channel
                return channel
        except Exception as e:
            print(f"❌ Nepodařilo se načíst kanál {channel_id}: {e}")
        
        return None
    
    
    async def _send_embed(
        self,
        channel_id: int,
        embed: Embed,
        ping_user: Optional[int] = None
    ) -> bool:
        """
        Pošle embed do kanálu
        
        Args:
            channel_id: ID cílového kanálu
            embed: Discord embed k odeslání
            ping_user: Volitelně - Discord user ID k pingu
        
        Returns:
            True pokud se podařilo odeslat
        """
        if not self.enabled:
            return False
        
        channel = await self._get_channel(channel_id)
        if not channel:
            return False
        
        try:
            content = f"<@{ping_user}>" if ping_user else None
            await channel.send(content=content, embed=embed)
            return True
        except Exception as e:
            print(f"❌ Chyba při odesílání do kanálu {channel_id}: {e}")
            return False
    
    
    async def _add_role(self, user_id: int, role_id: int) -> bool:
        """
        Přidá roli uživateli
        """
        if not self.enabled:
            return False
        
        try:
            # Najdi guild (server) kde je role
            for guild in self.bot.guilds:
                role = guild.get_role(role_id)
                if role:
                    member = guild.get_member(user_id)
                    if member and role not in member.roles:
                        await member.add_roles(role)
                        print(f"✅ Přidána role {role.name} uživateli {member.name}")
                        return True
            return False
        except Exception as e:
            print(f"❌ Chyba při přidávání role {role_id} uživateli {user_id}: {e}")
            return False
    
    
    async def _remove_role(self, user_id: int, role_id: int) -> bool:
        """
        Odebere roli uživateli
        """
        if not self.enabled:
            return False
        
        try:
            for guild in self.bot.guilds:
                role = guild.get_role(role_id)
                if role:
                    member = guild.get_member(user_id)
                    if member and role in member.roles:
                        await member.remove_roles(role)
                        print(f"✅ Odebrána role {role.name} uživateli {member.name}")
                        return True
            return False
        except Exception as e:
            print(f"❌ Chyba při odebírání role {role_id} uživateli {user_id}: {e}")
            return False
    
    
    # ========== KREVNÍ STATUS ==========
    
    async def log_critical_blood(
        self,
        player_id: int,
        player_name: str,
        blood_ml: float,
        injuries: List[str],
        consciousness: float
    ):
        """
        🩸 Loguje kritický krevní stav (< 2500ml)
        + Přidá CRITICAL roli
        
        Args:
            player_id: Discord ID hráče
            player_name: Jméno hráče
            blood_ml: Aktuální množství krve v ml
            injuries: Seznam popisů zranění
            consciousness: Úroveň vědomí (0-100)
        """
        # Vytvoř embed
        embed = Embed(
            title="⚠️ KRITICKÝ KREVNÍ STAV",
            description=f"**{player_name}** je v kritickém stavu!",
            color=Color.dark_red(),
            timestamp=datetime.utcnow()
        )
        
        # Výpočet procenta krve
        blood_pct = (blood_ml / 5000.0) * 100
        
        # Barva podle závažnosti
        if blood_ml < 1500:
            status = "💀 EXTRÉMNĚ KRITICKÉ"
            color = Color.from_rgb(139, 0, 0)  # Tmavě červená
        elif blood_ml < 2000:
            status = "🔴 KRITICKÉ"
            color = Color.red()
        else:
            status = "🟠 VÁŽNÉ"
            color = Color.orange()
        
        embed.color = color
        
        embed.add_field(
            name="🩸 Krev",
            value=f"**{blood_ml:.0f} ml** / 5000 ml ({blood_pct:.1f}%)",
            inline=True
        )
        
        embed.add_field(
            name="🧠 Vědomí",
            value=f"**{consciousness:.0f}%**",
            inline=True
        )
        
        embed.add_field(
            name="⚠️ Status",
            value=status,
            inline=True
        )
        
        # Zranění
        if injuries:
            injuries_text = "\n".join([f"• {inj}" for inj in injuries[:5]])
            if len(injuries) > 5:
                injuries_text += f"\n... a {len(injuries) - 5} dalších"
            
            embed.add_field(
                name=f"🩹 Zranění ({len(injuries)})",
                value=injuries_text,
                inline=False
            )
        
        # Doporučení
        if blood_ml < 1500:
            recommendation = "🚨 **OKAMŽITÁ POMOC NUTNÁ!** Vyhledej léčitele nebo použij lektvary!"
        elif blood_ml < 2000:
            recommendation = "⚠️ Potřebuješ léčení. Najdi bezpečné místo."
        else:
            recommendation = "⚠️ Sleduj svůj stav a zvažuje léčení."
        
        embed.add_field(
            name="💊 Doporučení",
            value=recommendation,
            inline=False
        )
        
        embed.set_footer(text=f"Hráč: {player_name}")
        
        # Pošli do kanálu + ping
        await self._send_embed(
            DiscordChannels.BLOOD_STATUS,
            embed,
            ping_user=player_id
        )
        
        # Přidej CRITICAL roli
        await self._add_role(player_id, DiscordRoles.CRITICAL_HEALTH)
    
    
    async def log_blood_recovered(
        self,
        player_id: int,
        player_name: str,
        blood_ml: float
    ):
        """
        ✅ Loguje zotavení z kritického stavu (>= 2500ml)
        + Odebere CRITICAL roli
        """
        embed = Embed(
            title="✅ Krevní Stav Stabilizován",
            description=f"**{player_name}** se zotavil z kritického stavu.",
            color=Color.green(),
            timestamp=datetime.utcnow()
        )
        
        blood_pct = (blood_ml / 5000.0) * 100
        
        embed.add_field(
            name="🩸 Krev",
            value=f"**{blood_ml:.0f} ml** / 5000 ml ({blood_pct:.1f}%)",
            inline=True
        )
        
        embed.add_field(
            name="✅ Status",
            value="Stabilní",
            inline=True
        )
        
        embed.set_footer(text=f"Hráč: {player_name}")
        
        await self._send_embed(DiscordChannels.BLOOD_STATUS, embed)
        
        # Odeber CRITICAL roli
        await self._remove_role(player_id, DiscordRoles.CRITICAL_HEALTH)
    
    
    # ========== BOJOVÉ LOGY ==========
    
    async def log_duel_start(
        self,
        duel_id: str,
        player1_id: int,
        player1_name: str,
        player2_id: int,
        player2_name: str,
        location: str
    ):
        """
        ⚔️ Loguje začátek souboje
        """
        embed = Embed(
            title="⚔️ SOUBOJ ZAHÁJEN",
            description=f"**{player1_name}** vs **{player2_name}**",
            color=Color.gold(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="👤 Bojovník 1",
            value=f"<@{player1_id}>",
            inline=True
        )
        
        embed.add_field(
            name="👤 Bojovník 2",
            value=f"<@{player2_id}>",
            inline=True
        )
        
        embed.add_field(
            name="📍 Lokace",
            value=location,
            inline=True
        )
        
        embed.set_footer(text=f"Duel ID: {duel_id}")
        
        await self._send_embed(DiscordChannels.COMBAT_LOGS, embed)
    
    
    async def log_combat_action(
        self,
        duel_id: str,
        turn_number: int,
        caster_name: str,
        spell_name: str,
        target_name: str,
        result: str,
        damage_description: Optional[str] = None
    ):
        """
        🎯 Loguje bojovou akci (seslání kouzla)
        """
        embed = Embed(
            title=f"⚔️ Tah {turn_number}",
            color=Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        # Ikona podle výsledku
        result_icons = {
            "hit": "💥",
            "miss": "🌀",
            "blocked": "🛡️",
            "dodged": "💨",
            "reflected": "🔄",
            "critical": "💢"
        }
        
        icon = result_icons.get(result.lower(), "⚔️")
        
        embed.add_field(
            name="🪄 Kouzlo",
            value=f"**{caster_name}** sesílá **{spell_name}**",
            inline=False
        )
        
        embed.add_field(
            name=f"{icon} Výsledek",
            value=result.upper(),
            inline=True
        )
        
        if damage_description:
            embed.add_field(
                name="🩸 Následky",
                value=damage_description,
                inline=False
            )
        
        embed.set_footer(text=f"Duel ID: {duel_id}")
        
        await self._send_embed(DiscordChannels.COMBAT_LOGS, embed)
    
    
    async def log_duel_end(
        self,
        duel_id: str,
        winner_id: int,
        winner_name: str,
        loser_id: int,
        loser_name: str,
        duration_seconds: float,
        total_turns: int,
        final_stats: Dict[str, Any]
    ):
        """
        🏆 Loguje konec souboje
        """
        embed = Embed(
            title="🏆 SOUBOJ UKONČEN",
            description=f"**{winner_name}** VYHRÁVÁ!",
            color=Color.gold(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="👑 Vítěz",
            value=f"<@{winner_id}>",
            inline=True
        )
        
        embed.add_field(
            name="💀 Poražený",
            value=f"<@{loser_id}>",
            inline=True
        )
        
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        
        embed.add_field(
            name="⏱️ Délka souboje",
            value=f"{minutes}m {seconds}s ({total_turns} tahů)",
            inline=True
        )
        
        # Finální statistiky
        if final_stats:
            stats_text = ""
            
            if "winner_blood" in final_stats:
                stats_text += f"🩸 Vítěz: {final_stats['winner_blood']:.0f} ml\n"
            
            if "loser_blood" in final_stats:
                stats_text += f"💀 Poražený: {final_stats['loser_blood']:.0f} ml\n"
            
            if "winner_injuries" in final_stats:
                stats_text += f"🩹 Vítěz: {final_stats['winner_injuries']} zranění\n"
            
            if "loser_injuries" in final_stats:
                stats_text += f"🩹 Poražený: {final_stats['loser_injuries']} zranění"
            
            if stats_text:
                embed.add_field(
                    name="📊 Finální Statistiky",
                    value=stats_text,
                    inline=False
                )
        
        embed.set_footer(text=f"Duel ID: {duel_id}")
        
        await self._send_embed(DiscordChannels.COMBAT_LOGS, embed)
    
    
    async def log_injury(
        self,
        player_id: int,
        player_name: str,
        injury_description: str,
        body_part: str,
        severity: int,
        bleeding_rate: float
    ):
        """
        🩹 Loguje nové zranění
        """
        embed = Embed(
            title="🩹 NOVÉ ZRANĚNÍ",
            description=f"**{player_name}** utrpěl zranění!",
            color=Color.red(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📍 Část těla",
            value=body_part.replace("_", " ").title(),
            inline=True
        )
        
        embed.add_field(
            name="⚠️ Závažnost",
            value=f"{severity}/10",
            inline=True
        )
        
        if bleeding_rate > 0:
            embed.add_field(
                name="🩸 Krvácení",
                value=f"{bleeding_rate:.1f} ml/s",
                inline=True
            )
        
        embed.add_field(
            name="📝 Popis",
            value=injury_description,
            inline=False
        )
        
        embed.set_footer(text=f"Hráč: {player_name}")
        
        await self._send_embed(DiscordChannels.COMBAT_LOGS, embed)
    
    
    # ========== DEATH ==========
    
    async def log_death(
        self,
        player_id: int,
        player_name: str,
        cause_of_death: str,
        killer_name: Optional[str] = None,
        location: Optional[str] = None
    ):
        """
        💀 Loguje smrt hráče
        """
        embed = Embed(
            title="💀 SMRT HRÁČE",
            description=f"**{player_name}** zemřel!",
            color=Color.from_rgb(0, 0, 0),  # Černá
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="💀 Oběť",
            value=f"<@{player_id}>",
            inline=True
        )
        
        if killer_name:
            embed.add_field(
                name="⚔️ Zabit/a",
                value=killer_name,
                inline=True
            )
        
        if location:
            embed.add_field(
                name="📍 Místo",
                value=location,
                inline=True
            )
        
        embed.add_field(
            name="☠️ Příčina smrti",
            value=cause_of_death,
            inline=False
        )
        
        embed.set_footer(text=f"R.I.P. {player_name}")
        
        # Pošli do blood status (protože smrt je nejkritičtější stav)
        await self._send_embed(DiscordChannels.BLOOD_STATUS, embed, ping_user=player_id)
    
    
    # ========== UTILITY ==========
    
    def disable(self):
        """Vypne logování (pro testování)"""
        self.enabled = False
        print("⚠️ Discord logger vypnut")
    
    
    def enable(self):
        """Zapne logování"""
        self.enabled = True
        print("✅ Discord logger zapnut")
