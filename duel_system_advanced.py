"""
================================================================================
KOMPLETNÍ SOUBOJOVÝ SYSTÉM - STŘÍDÁNÍ TAHŮ + UTILITY + PAGINATION
================================================================================

NOVINKY V2:
✨ Utility kouzla použitelná v souboji
📜 Stránkování kouzel (podpora pro 256+ kouzel)
🛡️ Fix: Když obránce nemá obranu, dostane ránu a pokračuje

INSTALACE:
1. Nahraď celý obsah souboru duel_system_advanced.py tímto kódem
2. V bot.py nahraď funkce start_duel_turn

JAK TO FUNGUJE:
- Tah 1: Hráč1 útočí → Hráč2 se brání → Vyhodnocení
- Tah 2: Hráč2 útočí → Hráč1 se brání → Vyhodnocení  
- Utility kouzla: Použitelná kdykoliv (léčení, buff, debuff, atd.)
- Pagination: Šipky "◀️ Předchozí" a "▶️ Další" pro listování kouzly

================================================================================
"""

import discord
from discord import app_commands
import asyncio
import time
from typing import Optional, Dict, List, Tuple
from enum import Enum
from models.player import Player, Condition
from models.combat import CombatEngine, CombatAction, DuelState
from spell_database import SPELLS_DATABASE


# ================================================================================
# MANAGER
# ================================================================================

class TurnPhase(Enum):
    ATTACKER_CHOOSING = "attacker"
    DEFENDER_REACTING = "defender"
    RESOLVING = "resolving"


class AdvancedDuelManager:
    def __init__(self, combat_engine: CombatEngine, combat_logger=None):
        self.combat_engine = combat_engine
        self.combat_logger = combat_logger
        self.active_duels: Dict[int, Dict] = {}
    
    def start_duel(self, channel_id: int, duel, p1_user, p2_user):
        self.active_duels[channel_id] = {
            'duel': duel,
            'player1_user': p1_user,
            'player2_user': p2_user,
            'current_turn': 1,
            'phase': TurnPhase.ATTACKER_CHOOSING,
            'attacker_is_p1': True,
            'pending_attack_spell': None,
            'pending_attack_action': None,
            'pending_defend_spell': None,
            'pending_defend_action': None,
            'attacker_message': None,
            'defender_message': None,
        }
        
        if self.combat_logger:
            self.combat_logger.log_duel_start(
                duel.duel_id, duel.player1, duel.player2, location="Discord Arena"
            )
    
    def get_state(self, channel_id: int) -> Optional[Dict]:
        return self.active_duels.get(channel_id)
    
    def get_current_attacker(self, channel_id: int) -> Tuple[Player, discord.User]:
        state = self.get_state(channel_id)
        if not state:
            return None, None
        duel = state['duel']
        if state['attacker_is_p1']:
            return duel.player1, state['player1_user']
        else:
            return duel.player2, state['player2_user']
    
    def get_current_defender(self, channel_id: int) -> Tuple[Player, discord.User]:
        state = self.get_state(channel_id)
        if not state:
            return None, None
        duel = state['duel']
        if state['attacker_is_p1']:
            return duel.player2, state['player2_user']
        else:
            return duel.player1, state['player1_user']
    
    def set_attack(self, channel_id: int, action: CombatAction, spell_id: str):
        state = self.get_state(channel_id)
        if state:
            state['pending_attack_action'] = action
            state['pending_attack_spell'] = spell_id
            state['phase'] = TurnPhase.DEFENDER_REACTING
    
    def set_defense(self, channel_id: int, action: CombatAction, spell_id: str):
        state = self.get_state(channel_id)
        if state:
            state['pending_defend_action'] = action
            state['pending_defend_spell'] = spell_id
            state['phase'] = TurnPhase.RESOLVING
    
    def advance_turn(self, channel_id: int):
        state = self.get_state(channel_id)
        if state:
            state['current_turn'] += 1
            state['attacker_is_p1'] = not state['attacker_is_p1']
            state['phase'] = TurnPhase.ATTACKER_CHOOSING
            state['pending_attack_spell'] = None
            state['pending_attack_action'] = None
            state['pending_defend_spell'] = None
            state['pending_defend_action'] = None
    
    def end_duel(self, channel_id: int, winner: Player, loser: Player):
        if channel_id in self.active_duels:
            state = self.active_duels[channel_id]
            duel = state['duel']
            if self.combat_logger:
                duration = time.time() - duel.start_time
                self.combat_logger.log_duel_end(duel.duel_id, winner, loser, duration, state['current_turn'])
            del self.active_duels[channel_id]


# ================================================================================
# EMBED BUILDER
# ================================================================================

class DuelEmbedBuilder:
    
    @staticmethod
    def create_attacker_embed(attacker: Player, defender: Player, turn_number: int, 
                               available_spells: List[Tuple[str, dict]], current_page: int = 0, 
                               total_pages: int = 1) -> discord.Embed:
        embed = discord.Embed(
            title=f"⚔️ TAH {turn_number} | TY ÚTOČÍŠ!",
            description=f"**TY:** {attacker.name}\n**SOUPEŘ:** {defender.name}\n\n🎯 **Vyber kouzlo a zaútoč!**",
            color=discord.Color.red()
        )
        
        stats = f"💚 Vědomí: {attacker.consciousness:.0f}%\n🩸 Krev: {attacker.blood_volume:.0f} ml"
        bleeding = sum(bp.get_total_bleeding() for bp in attacker.body.values())
        if bleeding > 0:
            stats += f"\n🩸 Krvácení: {bleeding:.1f} ml/s"
        embed.add_field(name="📊 Tvoje Statistiky", value=stats, inline=True)
        
        def_stats = f"💚 Vědomí: {defender.consciousness:.0f}%\n🩸 Krev: {defender.blood_volume:.0f} ml"
        embed.add_field(name=f"📊 Soupeř", value=def_stats, inline=True)
        
        if available_spells:
            spells_text = ""
            for spell_id, spell in available_spells[:8]:
                emoji_map = {
                    'combat': '⚔️',
                    'defensive': '🛡️',
                    'utility': '🎭',
                    'healing': '💚',
                    'control': '🧠'
                }
                emoji = emoji_map.get(spell.get('type', 'all'), '✨')
                spells_text += f"{emoji} {spell['name_cs']}\n"
            embed.add_field(name="✨ Dostupná Kouzla", value=spells_text or "Žádná", inline=False)
        
        if total_pages > 1:
            embed.set_footer(text=f"Stránka {current_page + 1}/{total_pages} • Použij šipky pro listování")
        else:
            embed.set_footer(text="Vyber kouzlo a klikni na ÚTOK nebo UTILITY!")
        return embed
    
    @staticmethod
    def create_waiting_embed(player: Player, opponent: Player, turn_number: int, 
                            is_attacker: bool = False) -> discord.Embed:
        """Create a waiting embed while the other player makes their choice"""
        if is_attacker:
            title = f"⏳ TAH {turn_number} | Čekáš na reakci soupeře..."
            description = f"**TY:** {player.name}\n**SOUPEŘ:** {opponent.name}\n\n🎯 Tvůj útok byl odeslán!\n⏳ Čekej na reakci soupeře..."
            color = discord.Color.orange()
        else:
            title = f"⏳ TAH {turn_number} | Čekáš na útok soupeře..."
            description = f"**TY:** {player.name}\n**SOUPEŘ:** {opponent.name}\n\n🛡️ Připrav se na obranu!\n⏳ Soupeř vybírá své kouzlo..."
            color = discord.Color.greyple()
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        
        stats = f"💚 Vědomí: {player.consciousness:.0f}%\n🩸 Krev: {player.blood_volume:.0f} ml"
        bleeding = sum(bp.get_total_bleeding() for bp in player.body.values())
        if bleeding > 0:
            stats += f"\n🩸 Krvácení: {bleeding:.1f} ml/s"
        embed.add_field(name="📊 Tvoje Statistiky", value=stats, inline=True)
        
        opp_stats = f"💚 Vědomí: {opponent.consciousness:.0f}%\n🩸 Krev: {opponent.blood_volume:.0f} ml"
        embed.add_field(name=f"📊 Soupeř", value=opp_stats, inline=True)
        
        embed.set_footer(text="Počkej na druhou stranu...")
        return embed
    
    @staticmethod
    def create_defender_embed(defender: Player, attacker: Player, turn_number: int,
                               incoming_spell: str, available_defensive: List[Tuple[str, dict]],
                               current_page: int = 0, total_pages: int = 1) -> discord.Embed:
        spell_name = SPELLS_DATABASE.get(incoming_spell, {}).get('name_cs', 'Neznámé kouzlo') if incoming_spell else "???"
        
        embed = discord.Embed(
            title=f"🛡️ TAH {turn_number} | BRAŇ SE!",
            description=(
                f"**TY:** {defender.name}\n**SOUPEŘ:** {attacker.name}\n\n"
                f"⚠️ **{attacker.name} útočí: {spell_name}!**\n"
                f"🛡️ Jak budeš reagovat?"
            ),
            color=discord.Color.blue()
        )
        
        stats = f"💚 Vědomí: {defender.consciousness:.0f}%\n🩸 Krev: {defender.blood_volume:.0f} ml"
        embed.add_field(name="📊 Tvoje Statistiky", value=stats, inline=True)
        
        att_stats = f"💚 Vědomí: {attacker.consciousness:.0f}%\n🩸 Krev: {attacker.blood_volume:.0f} ml"
        embed.add_field(name=f"📊 Soupeř", value=att_stats, inline=True)
        
        # Check if defender has any defensive spells
        has_defense = any(spell['type'] in ['defensive', 'utility'] for _, spell in available_defensive)
        
        if has_defense:
            embed.add_field(
                name="💡 Tvoje možnosti obrany",
                value=(
                    "🛡️ **BRÁNIT** - Použij obranné kouzlo proti útoku\n"
                    "💚 **VYLÉČIT** - Vyleč se a pak přijmi útok\n"
                    "⚔️ **PROTIÚTOK** - Zaútoč zpět bez obrany!\n"
                    "🎭 **UTILITY** - Použij utility kouzlo a pak přijmi útok\n"
                    "⏭️ **PŘIJMOUT ZÁSAH** - Vezmi ránu bez obrany"
                ),
                inline=False
            )
        else:
            embed.add_field(
                name="⚠️ Varování",
                value="❌ Nemáš žádná obranná kouzla!\n⏭️ Klikni **PŘIJMOUT ZÁSAH** pro pokračování.",
                inline=False
            )
        
        if total_pages > 1:
            embed.set_footer(text=f"Stránka {current_page + 1}/{total_pages} • Použij šipky pro listování")
        else:
            embed.set_footer(text="Rychle reaguj!")
        return embed
    
    @staticmethod
    def create_waiting_embed(player: Player, opponent: Player, turn_number: int, is_attacker: bool) -> discord.Embed:
        if is_attacker:
            title = f"⏳ TAH {turn_number} | Čekáš na reakci..."
            desc = f"Útok vyslán! **{opponent.name}** reaguje..."
        else:
            title = f"⏳ TAH {turn_number} | Čekáš na soupeře..."
            desc = f"**{opponent.name}** vybírá útok..."
        
        embed = discord.Embed(title=title, description=desc, color=discord.Color.greyple())
        embed.add_field(name=f"📊 {player.name}", value=f"💚 {player.consciousness:.0f}% | 🩸 {player.blood_volume:.0f} ml", inline=True)
        embed.add_field(name=f"📊 {opponent.name}", value=f"💚 {opponent.consciousness:.0f}% | 🩸 {opponent.blood_volume:.0f} ml", inline=True)
        return embed
    
    @staticmethod
    def create_result_embed(attacker: Player, defender: Player, turn_number: int, messages: List[str]) -> discord.Embed:
        embed = discord.Embed(
            title=f"⚔️ VÝSLEDEK TAHU {turn_number}",
            description="\n".join(messages),
            color=discord.Color.gold()
        )
        embed.add_field(
            name=f"📊 {attacker.name}",
            value=f"💚 {attacker.consciousness:.0f}% | 🩸 {attacker.blood_volume:.0f} ml",
            inline=True
        )
        embed.add_field(
            name=f"📊 {defender.name}",
            value=f"💚 {defender.consciousness:.0f}% | 🩸 {defender.blood_volume:.0f} ml",
            inline=True
        )
        return embed


# ================================================================================
# PAGINATION HELPER
# ================================================================================

def paginate_spells(spells: List[Tuple[str, dict]], page_size: int = 20) -> List[List[Tuple[str, dict]]]:
    """Split spells into pages for pagination"""
    if not spells:
        return [[]]
    return [spells[i:i + page_size] for i in range(0, len(spells), page_size)]


# ================================================================================
# SPELL SELECT DROPDOWNS WITH PAGINATION
# ================================================================================

class AttackerSpellSelect(discord.ui.Select):
    def __init__(self, player: Player, view_ref, current_page: int = 0):
        self.player = player
        self.view_ref = view_ref
        self.current_page = current_page
        
        # Get all available offensive and utility spells
        all_spells = [
            (spell_id, spell)
            for spell_id in player.known_spells
            if (spell := SPELLS_DATABASE.get(spell_id))
            and spell['type'] in ['combat', 'utility', 'control']
            and player.can_cast_spell_now(spell_id)[0]
        ]
        
        # Paginate
        pages = paginate_spells(all_spells, page_size=20)
        self.total_pages = len(pages) if pages else 1
        self.view_ref.total_pages = self.total_pages
        
        current_spells = pages[current_page] if pages and current_page < len(pages) else []
        
        options = []
        for spell_id, spell in current_spells[:25]:  # Discord limit
            emoji_map = {
                'all': '⚡',
                'offensive': '⚔️',
                'utility': '🎭'
            }
            emoji = emoji_map.get(spell.get('type', 'all'), '✨')
            options.append(discord.SelectOption(
                label=spell['name_cs'][:100],
                value=spell_id,
                description=f"{spell.get('type', 'offensive')} | {spell.get('damage_type', 'N/A')}"[:100],
                emoji=emoji
            ))
        
        if not options:
            options.append(discord.SelectOption(label="Žádná kouzla", value="none", emoji="❌"))
        
        super().__init__(
            placeholder=f"⚔️ Vyber útočné/utility kouzlo (Stránka {current_page + 1}/{self.total_pages})",
            options=options,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.player.discord_id:
            return await interaction.response.send_message("❌ Tohle není pro tebe!", ephemeral=True)
        
        if self.values[0] == "none":
            return await interaction.response.send_message("❌ Nemáš žádná kouzla!", ephemeral=True)
        
        self.view_ref.selected_spell = self.values[0]
        spell = SPELLS_DATABASE[self.values[0]]

        self.placeholder = f"✅ {spell['name_cs']}"
        await interaction.response.edit_message(
            content=f"⚔️ Vybráno: **{spell['name_cs']}**\n👉 Klikni **ÚTOK** nebo **UTILITY**.",
            view=self.view_ref
        )


class DefenderSpellSelect(discord.ui.Select):
    def __init__(self, player: Player, view_ref, current_page: int = 0):
        self.player = player
        self.view_ref = view_ref
        self.current_page = current_page
        
        # Get all defensive and utility spells
        all_spells = [
            (spell_id, spell)
            for spell_id in player.known_spells
            if (spell := SPELLS_DATABASE.get(spell_id))
            and spell['type'] in ['defensive', 'utility']
            and player.can_cast_spell_now(spell_id)[0]
        ]
        
        # Paginate
        pages = paginate_spells(all_spells, page_size=20)
        self.total_pages = len(pages) if pages else 1
        self.view_ref.total_pages = self.total_pages
        
        current_spells = pages[current_page] if pages and current_page < len(pages) else []
        
        options = []
        for spell_id, spell in current_spells[:25]:
            emoji = '🛡️' if spell['type'] == 'defensive' else '🎭'
            options.append(discord.SelectOption(
                label=spell['name_cs'][:100],
                value=spell_id,
                description=f"{spell.get('type', 'defensive')}"[:100],
                emoji=emoji
            ))
        
        if not options:
            options.append(discord.SelectOption(label="Žádná obrana", value="none", emoji="❌"))
        
        super().__init__(
            placeholder=f"🛡️ Obranné kouzlo (Stránka {current_page + 1}/{self.total_pages})",
            options=options,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.player.discord_id:
            return await interaction.response.send_message("❌ Tohle není pro tebe!", ephemeral=True)
        
        if self.values[0] == "none":
            return await interaction.response.send_message("❌ Nemáš obranná kouzla!", ephemeral=True)
        
        self.view_ref.selected_spell = self.values[0]
        spell = SPELLS_DATABASE[self.values[0]]

        self.placeholder = f"✅ {spell['name_cs']}"
        await interaction.response.edit_message(
            content=f"🛡️ Obrana: **{spell['name_cs']}**\n👉 Klikni **BRÁNIT** nebo **UTILITY**.",
            view=self.view_ref
        )


class HealingSpellSelect(discord.ui.Select):
    def __init__(self, player: Player, view_ref, current_page: int = 0):
        self.player = player
        self.view_ref = view_ref
        self.current_page = current_page
        
        # Get all healing spells
        all_spells = [
            (spell_id, spell)
            for spell_id in player.known_spells
            if (spell := SPELLS_DATABASE.get(spell_id))
            and spell['type'] == 'healing'
            and player.can_cast_spell_now(spell_id)[0]
        ]
        
        # Paginate
        pages = paginate_spells(all_spells, page_size=20)
        self.total_pages = len(pages) if pages else 1
        self.view_ref.total_pages = self.total_pages
        
        current_spells = pages[current_page] if pages and current_page < len(pages) else []
        
        options = []
        for spell_id, spell in current_spells[:25]:
            options.append(discord.SelectOption(
                label=spell['name_cs'][:100],
                value=spell_id,
                description=f"Léčení | {spell.get('description', '')[:80]}"[:100],
                emoji='💚'
            ))
        
        if not options:
            options.append(discord.SelectOption(label="Žádné léčení", value="none", emoji="❌"))
        
        super().__init__(
            placeholder=f"💚 Léčivé kouzlo (Stránka {current_page + 1}/{self.total_pages})",
            options=options,
            row=1
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.player.discord_id:
            return await interaction.response.send_message("❌ Tohle není pro tebe!", ephemeral=True)
        
        if self.values[0] == "none":
            return await interaction.response.send_message("❌ Nemáš léčivá kouzla!", ephemeral=True)
        
        self.view_ref.healing_spell = self.values[0]
        spell = SPELLS_DATABASE[self.values[0]]

        self.placeholder = f"✅ {spell['name_cs']}"
        await interaction.response.edit_message(
            content=f"💚 Léčení: **{spell['name_cs']}**\n👉 Klikni **VYLÉČIT**.",
            view=self.view_ref
        )


class CounterSpellSelect(discord.ui.Select):
    def __init__(self, player: Player, view_ref, current_page: int = 0):
        self.player = player
        self.view_ref = view_ref
        self.current_page = current_page
        
        # Get all offensive spells for counter
        all_spells = [
            (spell_id, spell)
            for spell_id in player.known_spells
            if (spell := SPELLS_DATABASE.get(spell_id))
            and spell['type'] in ['combat', 'utility']
            and player.can_cast_spell_now(spell_id)[0]
        ]
        
        # Paginate
        pages = paginate_spells(all_spells, page_size=20)
        self.total_pages = len(pages) if pages else 1
        
        current_spells = pages[current_page] if pages and current_page < len(pages) else []
        
        options = []
        for spell_id, spell in current_spells[:25]:
            emoji = '⚡' if spell['type'] == 'all' else '⚔️'
            options.append(discord.SelectOption(
                label=spell['name_cs'][:100],
                value=spell_id,
                description=f"{spell.get('damage_type', 'N/A')}"[:100],
                emoji=emoji
            ))
        
        if not options:
            options.append(discord.SelectOption(label="Žádná kouzla", value="none", emoji="❌"))
        
        super().__init__(
            placeholder=f"⚔️ Protiútok (Stránka {current_page + 1}/{self.total_pages})",
            options=options,
            row=2
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.player.discord_id:
            return await interaction.response.send_message("❌ Tohle není pro tebe!", ephemeral=True)
        
        if self.values[0] == "none":
            return await interaction.response.send_message("❌ Nemáš útočná kouzla!", ephemeral=True)
        
        self.view_ref.counter_spell = self.values[0]
        spell = SPELLS_DATABASE[self.values[0]]

        self.placeholder = f"✅ {spell['name_cs']}"
        await interaction.response.edit_message(
            content=f"⚔️ Protiútok: **{spell['name_cs']}**\n👉 Klikni **PROTIÚTOK**.",
            view=self.view_ref
        )


# ================================================================================
# ACTION VIEWS
# ================================================================================

class AttackerActionView(discord.ui.View):
    def __init__(self, manager, channel_id, player, callback_func):
        super().__init__(timeout=120.0)
        self.manager = manager
        self.channel_id = channel_id
        self.player = player
        self.callback_func = callback_func
        self.selected_spell = None
        self.current_page = 0
        self.total_pages = 1

        self.add_item(AttackerSpellSelect(player, self, self.current_page))
        self._add_pagination_buttons()

    def _add_pagination_buttons(self):
        """Add previous/next buttons for spell pagination"""
        # Remove old pagination buttons if any
        buttons_to_remove = [c for c in self.children if isinstance(c, discord.ui.Button) and c.label in ["◀️ Předchozí", "▶️ Další"]]
        for btn in buttons_to_remove:
            self.remove_item(btn)
        
        if self.total_pages > 1:
            prev_btn = discord.ui.Button(label="◀️ Předchozí", style=discord.ButtonStyle.secondary, row=3, disabled=self.current_page == 0)
            next_btn = discord.ui.Button(label="▶️ Další", style=discord.ButtonStyle.secondary, row=3, disabled=self.current_page >= self.total_pages - 1)
            
            async def prev_callback(interaction: discord.Interaction):
                if interaction.user.id != self.player.discord_id:
                    return await interaction.response.send_message("❌ Tohle není pro tebe!", ephemeral=True)
                self.current_page = max(0, self.current_page - 1)
                await self._refresh_view(interaction)
            
            async def next_callback(interaction: discord.Interaction):
                if interaction.user.id != self.player.discord_id:
                    return await interaction.response.send_message("❌ Tohle není pro tebe!", ephemeral=True)
                self.current_page = min(self.total_pages - 1, self.current_page + 1)
                await self._refresh_view(interaction)
            
            prev_btn.callback = prev_callback
            next_btn.callback = next_callback
            
            self.add_item(prev_btn)
            self.add_item(next_btn)

    async def _refresh_view(self, interaction: discord.Interaction):
        """Refresh the view with new page"""
        # Remove old select
        selects_to_remove = [c for c in self.children if isinstance(c, AttackerSpellSelect)]
        for select in selects_to_remove:
            self.remove_item(select)
        # Add new select with current page
        self.add_item(AttackerSpellSelect(self.player, self, self.current_page))
        # Update pagination buttons
        self._add_pagination_buttons()
        await interaction.response.edit_message(view=self)

    def _disable_all(self):
        for item in self.children:
            item.disabled = True

    def _is_wrong_user(self, interaction):
        return interaction.user.id != self.player.discord_id

    async def _reject(self, interaction, msg):
        await interaction.response.send_message(msg, ephemeral=True)

    @discord.ui.button(label="⚔️ ÚTOK", style=discord.ButtonStyle.danger, row=1)
    async def attack_btn(self, interaction: discord.Interaction, button):
        if self._is_wrong_user(interaction):
            return await self._reject(interaction, "❌ Tohle není pro tebe!")

        if not self.selected_spell:
            return await self._reject(interaction, "❌ Nejdřív vyber kouzlo!")

        spell = SPELLS_DATABASE.get(self.selected_spell, {})
        
        # Check if spell is offensive
        if spell.get('type') != 'combat':
            return await self._reject(interaction, "❌ Toto není útočné kouzlo! Použij UTILITY.")

        self._disable_all()
        await interaction.response.edit_message(
            content=f"⚔️ Sesíláš **{spell.get('name_cs')}**!\n⏳ Čekáme na tah soupeře...",
            view=self
        )

        await self.callback_func(CombatAction.ATTACK, self.selected_spell)
        self.stop()

    @discord.ui.button(label="🎭 UTILITY", style=discord.ButtonStyle.success, row=1)
    async def utility_btn(self, interaction: discord.Interaction, button):
        if self._is_wrong_user(interaction):
            return await self._reject(interaction, "❌ Tohle není pro tebe!")

        if not self.selected_spell:
            return await self._reject(interaction, "❌ Nejdřív vyber kouzlo!")

        spell = SPELLS_DATABASE.get(self.selected_spell, {})
        
        # Allow utility, healing, or defensive spells
        if spell.get('type') not in ['utility', 'healing', 'defensive']:
            return await self._reject(interaction, "❌ Toto není utility kouzlo! Použij ÚTOK.")

        self._disable_all()
        await interaction.response.edit_message(
            content=f"🎭 Používáš **{spell.get('name_cs')}**!\n✨ Kouzlo aktivováno!",
            view=self
        )

        # Use HEAL action for utility spells (they don't end the turn waiting for defender)
        await self.callback_func(CombatAction.HEAL, self.selected_spell)
        self.stop()

    @discord.ui.button(label="🛡️ DEFENZIVA", style=discord.ButtonStyle.secondary, row=1)
    async def defend_btn(self, interaction: discord.Interaction, button):
        if self._is_wrong_user(interaction):
            return await self._reject(interaction, "❌ Tohle není pro tebe!")

        def_spell = next((
            spell_id for spell_id in self.player.known_spells
            if spell_id in SPELLS_DATABASE
            and SPELLS_DATABASE[spell_id]['type'] in ['defensive', 'utility']
            and self.player.can_cast_spell_now(spell_id)[0]
        ), None)

        if not def_spell:
            return await self._reject(interaction, "❌ Nemáš obranná kouzla!")

        self._disable_all()
        await interaction.response.edit_message(
            content="🛡️ Připravuješ obranu...\n⏳ Čekáš na útok soupeře.",
            view=self
        )

        await self.callback_func(CombatAction.DEFEND, def_spell)
        self.stop()

    async def on_timeout(self):
        self._disable_all()
        await self.callback_func(CombatAction.DODGE, None)


class DefenderActionView(discord.ui.View):
    def __init__(self, manager, channel_id, player, callback_func):
        super().__init__(timeout=120.0)
        self.manager = manager
        self.channel_id = channel_id
        self.player = player
        self.callback_func = callback_func
        self.selected_spell = None  # For defensive spells
        self.counter_spell = None  # For counter-attack spells
        self.healing_spell = None  # For healing spells
        self.current_page = 0
        self.total_pages = 1

        self.add_item(DefenderSpellSelect(player, self, self.current_page))
        self.add_item(HealingSpellSelect(player, self, self.current_page))
        self.add_item(CounterSpellSelect(player, self, self.current_page))
        self._add_pagination_buttons()

    def _add_pagination_buttons(self):
        """Add previous/next buttons for spell pagination"""
        # Remove old pagination buttons if any
        buttons_to_remove = [c for c in self.children if isinstance(c, discord.ui.Button) and c.label in ["◀️ Předchozí", "▶️ Další"]]
        for btn in buttons_to_remove:
            self.remove_item(btn)
        
        if self.total_pages > 1:
            prev_btn = discord.ui.Button(label="◀️ Předchozí", style=discord.ButtonStyle.secondary, row=4, disabled=self.current_page == 0)
            next_btn = discord.ui.Button(label="▶️ Další", style=discord.ButtonStyle.secondary, row=4, disabled=self.current_page >= self.total_pages - 1)
            
            async def prev_callback(interaction: discord.Interaction):
                if interaction.user.id != self.player.discord_id:
                    return await interaction.response.send_message("❌ Tohle není pro tebe!", ephemeral=True)
                self.current_page = max(0, self.current_page - 1)
                await self._refresh_view(interaction)
            
            async def next_callback(interaction: discord.Interaction):
                if interaction.user.id != self.player.discord_id:
                    return await interaction.response.send_message("❌ Tohle není pro tebe!", ephemeral=True)
                self.current_page = min(self.total_pages - 1, self.current_page + 1)
                await self._refresh_view(interaction)
            
            prev_btn.callback = prev_callback
            next_btn.callback = next_callback
            
            self.add_item(prev_btn)
            self.add_item(next_btn)

    async def _refresh_view(self, interaction: discord.Interaction):
        """Refresh the view with new page"""
        # Remove old selects
        selects_to_remove = [c for c in self.children if isinstance(c, (DefenderSpellSelect, CounterSpellSelect))]
        for select in selects_to_remove:
            self.remove_item(select)
        # Add new selects with current page
        self.add_item(DefenderSpellSelect(self.player, self, self.current_page))
        self.add_item(CounterSpellSelect(self.player, self, self.current_page))
        # Update pagination buttons
        self._add_pagination_buttons()
        await interaction.response.edit_message(view=self)

    def _disable_all(self):
        for item in self.children:
            item.disabled = True

    def _is_wrong_user(self, interaction):
        return interaction.user.id != self.player.discord_id

    async def _reject(self, interaction, msg):
        await interaction.response.send_message(msg, ephemeral=True)

    @discord.ui.button(label="🛡️ BRÁNIT", style=discord.ButtonStyle.primary, row=3)
    async def defend_btn(self, interaction: discord.Interaction, button):
        if self._is_wrong_user(interaction):
            return await self._reject(interaction, "❌ Tohle není pro tebe!")

        if not self.selected_spell:
            return await self._reject(interaction, "❌ Vyber obranné kouzlo!")

        spell = SPELLS_DATABASE.get(self.selected_spell, {})

        self._disable_all()
        await interaction.response.edit_message(
            content=f"🛡️ Aktivuješ **{spell.get('name_cs')}**!",
            view=self
        )

        await self.callback_func(CombatAction.DEFEND, self.selected_spell)
        self.stop()

    @discord.ui.button(label="💚 VYLÉČIT", style=discord.ButtonStyle.success, row=3)
    async def heal_btn(self, interaction: discord.Interaction, button):
        if self._is_wrong_user(interaction):
            return await self._reject(interaction, "❌ Tohle není pro tebe!")

        if not self.healing_spell:
            return await self._reject(interaction, "❌ Vyber léčivé kouzlo!")

        spell = SPELLS_DATABASE.get(self.healing_spell, {})

        self._disable_all()
        await interaction.response.edit_message(
            content=f"💚 Léčíš sebe pomocí **{spell.get('name_cs')}** a pak přijímáš útok!",
            view=self
        )

        # Use HEAL action - this will cast healing then take the hit
        await self.callback_func(CombatAction.HEAL, self.healing_spell)
        self.stop()

    @discord.ui.button(label="⚔️ PROTIÚTOK", style=discord.ButtonStyle.danger, row=3)
    async def counter_btn(self, interaction: discord.Interaction, button):
        if self._is_wrong_user(interaction):
            return await self._reject(interaction, "❌ Tohle není pro tebe!")

        if not self.counter_spell:
            return await self._reject(interaction, "❌ Vyber kouzlo pro protiútok!")

        spell = SPELLS_DATABASE.get(self.counter_spell, {})

        self._disable_all()
        await interaction.response.edit_message(
            content=f"⚔️ Okamžitý protiútok: **{spell.get('name_cs')}**!",
            view=self
        )

        await self.callback_func(CombatAction.ATTACK, self.counter_spell)
        self.stop()

    @discord.ui.button(label="🎭 UTILITY", style=discord.ButtonStyle.secondary, row=4)
    async def utility_btn(self, interaction: discord.Interaction, button):
        if self._is_wrong_user(interaction):
            return await self._reject(interaction, "❌ Tohle není pro tebe!")

        if not self.selected_spell:
            return await self._reject(interaction, "❌ Vyber utility kouzlo z obranných kouzel!")

        spell = SPELLS_DATABASE.get(self.selected_spell, {})
        
        # Check if it's actually utility (not healing, not pure defensive)
        if spell.get('type') not in ['utility']:
            return await self._reject(interaction, "❌ Toto není utility kouzlo! Použij BRÁNIT nebo VYLÉČIT.")

        self._disable_all()
        await interaction.response.edit_message(
            content=f"🎭 Používáš **{spell.get('name_cs')}** a následně přijímáš útok!",
            view=self
        )

        # Use HEAL action - this will cast utility then take the hit
        await self.callback_func(CombatAction.HEAL, self.selected_spell)
        self.stop()

    @discord.ui.button(label="⏭️ PŘIJMOUT ZÁSAH", style=discord.ButtonStyle.secondary, row=4)
    async def take_hit_btn(self, interaction: discord.Interaction, button):
        """New button: Take the hit without defense - fixes stuck defenders"""
        if self._is_wrong_user(interaction):
            return await self._reject(interaction, "❌ Tohle není pro tebe!")

        self._disable_all()
        await interaction.response.edit_message(
            content="⏭️ Přijímáš útok bez obrany...\n💥 Připrav se!",
            view=self
        )

        # Use DODGE action with None spell - means "take hit without defense"
        await self.callback_func(CombatAction.DODGE, None)
        self.stop()

    async def on_timeout(self):
        """On timeout, automatically take the hit"""
        self._disable_all()
        await self.callback_func(CombatAction.DODGE, None)


# ================================================================================
# HELPER
# ================================================================================

def get_available_spells(player: Player, spell_type: str = "all") -> List[Tuple[str, dict]]:
    type_mappings = {
        "combat": ["combat"],
        "defensive": ["defensive"],
        "utility": ["utility"],
        "healing": ["healing"],
        "control": ["control"]
    }

    if spell_type == "all":
        valid_values = set(type_mappings.keys())

    elif spell_type == "combat":
        # všechno použitelné v boji
        valid_values = {"combat", "defensive", "utility", "healing", "control"}

    elif spell_type in type_mappings:
        valid_values = set(type_mappings[spell_type])

    else:
        valid_values = {spell_type}

    result = []

    for spell_id in player.known_spells:
        spell = SPELLS_DATABASE.get(spell_id)
        if not spell:
            continue

        can_cast, _ = player.can_cast_spell_now(spell_id)
        if not can_cast:
            continue

        spell_type_value = spell.get("type", "")

        if spell_type_value in valid_values:
            result.append((spell_id, spell))

    return result


# ================================================================================
# EXPORT
# ================================================================================

__all__ = [
    'AdvancedDuelManager',
    'DuelEmbedBuilder',
    'AttackerActionView',
    'DefenderActionView',
    'TurnPhase',
    'get_available_spells',
    'paginate_spells',
    # Zpětná kompatibilita
    'DuelActionView',
    'DuelSpellSelect',
]

DuelActionView = AttackerActionView
DuelSpellSelect = AttackerSpellSelect
