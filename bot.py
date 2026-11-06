"""
Harry Potter Realistický Soubojový Discord Bot
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import asyncio
import os
import time
import math
from typing import Optional
from systems.potion_brewing import PotionBrewingManager
from commands.potion_commands import setup_potion_commands
from models.player import PlayerDatabase, Player, BodyPart, Condition
from models.combat import CombatEngine, CombatAction, DuelState
from spell_database import SPELLS_DATABASE
import discord
from duel_system_advanced import (
    AdvancedDuelManager,
    DuelEmbedBuilder,
    AttackerActionView,
    DefenderActionView,
    TurnPhase,
    get_available_spells,
)
# Open World systémy
from systems.world_manager import WorldManager
from systems.economy import EconomyManager
from commands.world_commands import setup_world_commands

# Import combat loggeru (pokud existuje)
try:
    from combat_logger import CombatLogger
    COMBAT_LOGGER_AVAILABLE = True
except ImportError:
    COMBAT_LOGGER_AVAILABLE = False
    print("⚠️ Combat logger není dostupný")

try:
    from discord_logger import DiscordLogger
except ImportError:
    print("⚠️ Discord logger není dostupný")
# Config
TOKEN = os.getenv('DISCORD_BOT_TOKEN', 'YOUR_TOKEN_HERE')
GUILD_ID = os.getenv('GUILD_ID')

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Bot
bot = commands.Bot(command_prefix='!hp ', intents=intents)

# Databáze
player_db = PlayerDatabase()
combat_engine = CombatEngine(SPELLS_DATABASE)

# Open World systémy
world_manager = WorldManager()
economy_manager = EconomyManager()

# Přiřaď k botu pro přístup z commands
bot.player_db = player_db
bot.world_manager = world_manager
bot.economy_manager = economy_manager

# Globální proměnné pro pending souboje
pending_duels = {}  # {challenger_id: (target_id, timestamp)}
active_duel_channels = {}  # {channel_id: duel_id}
SORTING_HAT_IMG = "https://cdn.discordapp.com/attachments/1487590069471674480/1487814889488519178/Gemini_Generated_Image_vk42cevk42cevk42.png?ex=69ca8317&is=69c93197&hm=ef06ce3292bcab8149001ffba757ddbd579be92abf6756087e47ed103134a397&" 
IMG_POHAR = "https://cdn.discordapp.com/attachments/1487590069471674480/1487826819947303114/Gemini_Generated_Image_t1w0nut1w0nut1w0.png?ex=69ca8e34&is=69c93cb4&hm=a0f8126317c1dd3d78afc01b7598ba47ee6c903086854482277b1a0b75e6cc41&"
IMG_URL = "https://cdn.discordapp.com/attachments/1487590069471674480/1487599149368086732/Gemini_Generated_Image_wk1rawk1rawk1raw.png?ex=69c9ba2b&is=69c868ab&hm=286245eb2018a4d422c858cc6a0ebe9cf4c0bed8df7fc874fced71a7a2867cc2&"
ROLE_CITIZEN_ID = 1487595968630358067
ROLE_NOVICE_ID = 1487595967732519133
# --- NOVÁ KONFIGURACE INTERIÉRŮ 
IMG_ROOM_GRYFFINDOR = "https://cdn.discordapp.com/attachments/1487590069471674480/1487834336366559467/Gemini_Generated_Image_tyg4evtyg4evtyg4.png?ex=69ca9534&is=69c943b4&hm=97f663f883353613ea4422d630121381e9de4e705628f05a1c391d12d586ea9f&" # URL obrázku image_20.png
IMG_ROOM_SLYTHERIN = "https://cdn.discordapp.com/attachments/1487590069471674480/1487834335527833741/Gemini_Generated_Image_tyg4evtyg4evtyg41.png?ex=69ca9534&is=69c943b4&hm=798a5ca26ba59aa6a58428160a1de928e7c016e038e11c2fdc05b019ae1d8b9b&"   # URL obrázku image_21.png
IMG_ROOM_RAVENCLAW = "https://cdn.discordapp.com/attachments/1487590069471674480/1487834337700352160/Gemini_Generated_Image_tyg4evtyg4evtyg42.png?ex=69ca9534&is=69c943b4&hm=fddbcc0a5b478690ff609965d5a8590a1c41d257f12f754c73e836230d81bf39&"    # URL obrázku image_22.png
IMG_ROOM_HUFFLEPUFF = "https://cdn.discordapp.com/attachments/1487590069471674480/1487834337045909575/Gemini_Generated_Image_tyg4evtyg4evtyg43.png?ex=69ca9534&is=69c943b4&hm=4a413f1026b68edc839bb56d2cff797d1511c46284cb9dadca503626d3719983&"   # URL obrázku image_23.png

# ========== KONFIGURACE MAZLÍČKŮ ZADRAMA (s obrázky) ==========

# Data mazlíčků (Ponechány tvé URL z generace)
PET_ADOPTION_DATA = [
    {
        "id": "pet_owl",
        "name": "Sova",
        "emoji": "🦉",
        "role": "Majitel Sovy",
        "desc": "Tradiční bradavický společník. Noste zprávy s elegancí.",
        "img": "https://cdn.discordapp.com/attachments/1487590069471674480/1489325925748314213/Gemini_Generated_Image_h2qmrkh2qmrkh2qm.png?ex=69d0025b&is=69ceb0db&hm=3acf33a822f1bd42f524d10393094b99b9de48df3e5c1fcb0237aff239285278&"
    },
    {
        "id": "pet_cat",
        "name": "Kočka",
        "emoji": "🐈",
        "role": "Majitel Kočky",
        "desc": "Nezávislá, mazaná a hrdá. Vidí, co jiní ne.",
        "img": "https://cdn.discordapp.com/attachments/1487590069471674480/1489325924909580418/Gemini_Generated_Image_h2qmrkh2qmrkh2qm1.png?ex=69d0025a&is=69ceb0da&hm=0f252f6a00176012936cc69adfb5fbc3a4976e25bfb33ef0dbb908d595df8935&"
    },
    {
        "id": "pet_toad",
        "name": "Ropucha",
        "emoji": "🐸",
        "role": "Majitel Ropuchy",
        "desc": "Klidná a skromná. Ideální pro vážné studenty magie.",
        "img": "https://cdn.discordapp.com/attachments/1487590069471674480/1489325924150153406/Gemini_Generated_Image_h2qmrkh2qmrkh2qm2.png?ex=69d0025a&is=69ceb0da&hm=0a8942bfd5ace3b7a3f37cdbb87c9a6b278dedfc79b64617c3019ade0e248ff4&"
    },
    {
        "id": "pet_rat",
        "name": "Krysa",
        "emoji": "🐀",
        "role": "Majitel Krysy",
        "desc": "Nenápadná, ale chytrá. Vždy ví, kde se co šustne.",
        "img": "https://cdn.discordapp.com/attachments/1487590069471674480/1489325926838960209/Gemini_Generated_Image_h2qmrkh2qmrkh2qm3.png?ex=69d0025b&is=69ceb0db&hm=22cc1aad81600aab122726305b99a0fcf07b60426091097a1f4b91e64144fde8&"
    },
    {
        "id": "pet_puff",
        "name": "Kluběnko",
        "emoji": "🧶",
        "role": "Majitel Kluběnka",
        "desc": "Nejroztomilejší růžová koule. Zpívá, když je šťastná.",
        "img": "https://cdn.discordapp.com/attachments/1487590069471674480/1489325926310481992/Gemini_Generated_Image_h2qmrkh2qmrkh2qm4.png?ex=69d0025b&is=69ceb0db&hm=6b6a089a2758f1f806a7ea5983120b48d54802b659534333890179046a046c02&"
    }
]



# ========== EVENTS ==========

potion_manager = PotionBrewingManager()
bot.potion_manager = potion_manager
@bot.event
async def on_ready():
    print(f'🪄 {bot.user} je připraven k soubojům!')
    print(f'📚 Načteno {len(SPELLS_DATABASE)} kouzel')
    print(f'👥 Načteno {len(player_db.players)} hráčů')
    bot.add_view(SortingHatView()) 
    print('✅ Zařazovací systém aktivován')
    # Registruj world commands
    await setup_world_commands(bot)
    await setup_potion_commands(bot)
    if hasattr(bot, 'discord_logger'):
        bot.combat_logger = CombatLogger(bot.discord_logger)    
    bot.add_view(WandView())
    print('✅ Potion systém aktivován')
    # Sync commands
    bot.add_view(PetGalleryView()) # Tímto se View stane perzistentním
    print("✅ Perzistentní galerie mazlíčků zaregistrována.")    
    try:
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
        else:
            await bot.tree.sync()
        print('✅ Příkazy synchronizovány')
    except Exception as e:
        print(f'❌ Chyba při synchronizaci příkazů: {e}')
    
    # Start background tasks
    update_players_loop.start()
    cleanup_world_loop.start()
    

@tasks.loop(seconds=1.0)
async def update_players_loop():
    """Aktualizuje všechny hráče v souboji (krvácení atd.) - RYCHLÁ AKTUALIZACE"""
    for player in player_db.players.values():
        if player.in_combat:
            player.update(1.0)
            
            # Kontrola smrti
            if not player.is_alive():
                # Notify
                pass
    
    # Ulož změny
    player_db.save()


@tasks.loop(minutes=5.0)
async def cleanup_world_loop():
    """Čistí expirované tábory a kontroluje cestování"""
    # Vyčisti expirované tábory
    world_manager.cleanup_expired_camps()
    
    # Zkontroluj cestování všech hráčů
    for player_id in list(world_manager.player_states.keys()):
        arrived, dest_name = world_manager.check_travel_completion(player_id)
        # Notification by bylo možné poslat přes DM, ale to je optional
    
    # Ulož změny
    world_manager.save()


# ========== HELPER FUNCTIONS ==========

def get_player(interaction: discord.Interaction) -> Player:
    """Získá nebo vytvoří hráče a rovnou zkontroluje, jestli se nedoučil kouzla"""
    player = player_db.get_or_create_player(
        interaction.user.id,
        interaction.user.display_name
    )
    
    # KONTROLA DOUČENÝCH KOUZEL
    now = time.time()
    finished = []
    
    for spell_id, finish_time in list(player.learning_spells.items()):
        # Fix pro stará data, kdyby tam zbyly vteřiny místo timestampu
        if finish_time < 31536000:  
            finish_time = now + finish_time
            player.learning_spells[spell_id] = finish_time
            
        # Kouzlo se doučilo
        if now >= finish_time:
            player.known_spells.add(spell_id)
            finished.append(spell_id)
            
    # Odstraníme je z probíhajícího studia
    for spell_id in finished:
        del player.learning_spells[spell_id]
        
    if finished:
        player_db.save()
        
    return player


def format_spell_list(spells: list, known_spells: set, learning_spells: dict) -> str:
    """Naformátuje seznam kouzel"""
    lines = []
    for spell_id in spells:
        if spell_id not in SPELLS_DATABASE:
            continue
        spell = SPELLS_DATABASE[spell_id]
        
        if spell_id in known_spells:
            status_icon = "✅"
        elif spell_id in learning_spells:
            status_icon = "⏳"
        else:
            status_icon = "❌"
            
        difficulty = "⭐" * spell['difficulty']
        
        lines.append(
            f"{status_icon} **{spell['name_cs']}** ({spell['incantation']}) "
            f"- {difficulty} - {spell['cooldown']}s cooldown"
        )
    
    return "\n".join(lines)


# ========== VIEW CLASSES ==========

class SpellListView(discord.ui.View):
    def __init__(self, pages, player, category_name):
        super().__init__(timeout=120)
        self.pages = pages
        self.current_page = 0
        self.player = player
        self.category_name = category_name

    def create_embed(self):
        page_ids = self.pages[self.current_page]
        description = format_spell_list(page_ids, self.player.known_spells, self.player.learning_spells)
        
        embed = discord.Embed(
            title="📚 Seznam kouzel",
            description=description,
            color=discord.Color.purple()
        )
        embed.set_footer(text=f"Stránka {self.current_page + 1}/{len(self.pages)} | Kategorie: {self.category_name}")
        return embed

    @discord.ui.button(label="◀ Předchozí", style=discord.ButtonStyle.gray)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Další ▶", style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.defer()


# ========== SLASH COMMANDS ==========

@bot.tree.command(name="status", description="Zobraz svůj současný stav")
async def status(interaction: discord.Interaction):
    """Zobrazí stav hráče"""
    player = get_player(interaction)
    
    embed = discord.Embed(
        title=f"⚡ Status: {player.name}",
        description=player.get_status_summary(),
        color=discord.Color.blue()
    )
    
    # Přidat statistiky
    embed.add_field(
        name="📊 Statistiky",
        value=(
            f"🎯 Soubojů: {player.total_duels} (vyhráno: {player.duels_won})\n"
            f"💀 Zabito: {player.enemies_killed}\n"
            f"☠️ Zemřel: {player.times_died}krát\n"
            f"🌟 Reputace: {player.reputation}\n"
            f"⚫ Temná magie: {player.dark_magic_uses}krát"
        ),
        inline=False
    )
    
    # Známá kouzla
    known_count = len(player.known_spells)
    total_count = len(SPELLS_DATABASE)
    embed.add_field(
        name="📚 Kouzla",
        value=f"Znáš {known_count}/{total_count} kouzel",
        inline=True
    )

    # Právě studovaná kouzla
    if player.learning_spells:
        now = time.time()
        learning_text = ""
        for sid, ftime in player.learning_spells.items():
            s_data = SPELLS_DATABASE.get(sid, {})
            name = s_data.get('name_cs', sid)
            rem = max(0, int((ftime - now) / 60))
            if rem > 60:
                learning_text += f"• **{name}** (zbývá {rem//60}h {rem%60}m)\n"
            else:
                learning_text += f"• **{name}** (zbývá {rem}m)\n"
                
        embed.add_field(name="⏳ Právě studuješ", value=learning_text, inline=False)
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="spells", description="Seznam všech kouzel")
@app_commands.choices(category=[
    app_commands.Choice(name="Útok", value="utok"),
    app_commands.Choice(name="Obrana", value="obrana"),
    app_commands.Choice(name="Léčení", value="leceni"),
    app_commands.Choice(name="Kontrola", value="kontrola"),
    app_commands.Choice(name="Utility", value="utility")
])
async def spells_list(
    interaction: discord.Interaction,
    category: Optional[app_commands.Choice[str]] = None
):
    """Zobrazí seznam kouzel s funkčním listováním"""
    player = get_player(interaction)
    
    # Filtr kategorií mapovaný na tvou SPELLS_DATABASE
    categories_map = {
        "utok": ["damage", "cutting", "explosive", "stunning", "torture", "unforgivable_curse"],
        "obrana": ["shield", "shield_area", "defensive"],
        "leceni": ["healing", "minor_healing", "awakening"],
        "kontrola": ["control", "binding", "hindering", "mental", "tickling", "dancing_curse", "freezing", "adhesive"],
        "utility": ["utility", "summoning", "light", "water", "cutting", "levitation", "unlocking", "locking", "revealing", "concealment", "cleaning", "repair", "silencing", "vanishing", "duplication", "motion_control", "propulsion", "conjuration", "transformation", "wind"]
    }
    
    cat_value = category.value if category else None
    
    if cat_value and cat_value in categories_map:
        filter_cats = categories_map[cat_value]
        spell_ids = [
            sid for sid, spell in SPELLS_DATABASE.items()
            if spell.get('category') in filter_cats or spell.get('type') in filter_cats
        ]
    else:
        spell_ids = list(SPELLS_DATABASE.keys())
    
    if not spell_ids:
        await interaction.response.send_message("❌ Žádná kouzla v této kategorii nenalezena!", ephemeral=True)
        return

    # Rozdělení na stránky po 10 kusech
    per_page = 10
    pages = [spell_ids[i:i+per_page] for i in range(0, len(spell_ids), per_page)]
    
    # Vytvoření interaktivního zobrazení
    view = SpellListView(pages, player, cat_value or "Všechny")
    await interaction.response.send_message(embed=view.create_embed(), view=view)


@bot.tree.command(name="debug_reset_me", description="Úplně vymaže můj profil a kouzla")
async def debug_reset_me(interaction: discord.Interaction):
    if interaction.user.id in player_db.players:
        del player_db.players[interaction.user.id]
        player_db.save()
        await interaction.response.send_message("✅ Tvůj profil byl vymazán. Při příštím příkazu se vytvoří čistý.")
    else:
        await interaction.response.send_message("Nemáš žádný profil k smazání.")


@bot.tree.command(name="learn", description="Začni se učit nové kouzlo")
@app_commands.describe(spell="Název kouzla (např. stupefy)")
async def learn_spell(interaction: discord.Interaction, spell: str):
    """Začne učení kouzla"""
    player = get_player(interaction)
    
    # Najdi kouzlo
    spell_id = spell.lower().replace(" ", "_")
    
    if spell_id not in SPELLS_DATABASE:
        await interaction.response.send_message(
            f"❌ Kouzlo '{spell}' neexistuje! Použij `/spells` pro seznam.",
            ephemeral=True
        )
        return
    
    spell_data = SPELLS_DATABASE[spell_id]
    
    # Již známé?
    if spell_id in player.known_spells:
        await interaction.response.send_message(
            f"✅ Už dávno znáš kouzlo **{spell_data['name_cs']}**!",
            ephemeral=True
        )
        return
        
    # Už se ho učí?
    if spell_id in player.learning_spells:
        finish_time = player.learning_spells[spell_id]
        remaining = max(0, int((finish_time - time.time()) / 60))
        if remaining > 60:
            time_str = f"{remaining // 60}h {remaining % 60}m"
        else:
            time_str = f"{remaining} minut"
            
        await interaction.response.send_message(
            f"⏳ Toto kouzlo se už učíš! Zbývá ještě {time_str}.",
            ephemeral=True
        )
        return
        
    # Limit max 3 kouzla najednou
    if len(player.learning_spells) >= 3:
        await interaction.response.send_message(
            "❌ Tvoje mysl je přetížená! Nemůžeš se učit více než **3 kouzla najednou**.\n"
            "Počkej, až se doučíš ta stávající.",
            ephemeral=True
        )
        return
    
    # Předpoklady (Zatím jen placeholder z původního kódu)
    prereqs = spell_data.get('prerequisites', [])
    if prereqs:
        pass
    
    # Nastavení času dokončení
    hours_needed = spell_data.get('learning_time_hours', 1)
    finish_timestamp = time.time() + (hours_needed * 3600)
    
    player.learning_spells[spell_id] = finish_timestamp
    player_db.save()
    
    embed = discord.Embed(
        title="📖 Studium započalo",
        description=(
            f"Otevřel jsi staré svazky a začínáš studovat **{spell_data['name_cs']}**.\n\n"
            f"⏱️ **Čas studia:** {hours_needed} hodin\n"
            f"🎓 **Obtížnost:** {'⭐' * spell_data['difficulty']}\n"
            f"✨ **Formule:** `{spell_data['incantation']}`\n"
            f"❄️ **Cooldown:** {spell_data['cooldown']}s\n\n"
            f"📝 {spell_data['description']}"
        ),
        color=discord.Color.green()
    )
    embed.set_footer(text="Až čas uplyne, kouzlo se ti automaticky zpřístupní")
    
    await interaction.response.send_message(embed=embed)


# ========== POMOCNÉ FUNKCE SOUBOJE ==========
# Poznámka: get_available_spells se importuje z duel_system_advanced na začátku souboru
 
def get_available_spells_OLD_BACKUP(player: Player, spell_type: str = "all"):
    """DEPRECATED - Vrátí seznam dostupných kouzel pro hráče - Tato funkce je nahrazena importem z duel_system_advanced"""
    available = []
    
    for spell_id in player.known_spells:
        if spell_id not in SPELLS_DATABASE:
            continue
        
        spell = SPELLS_DATABASE[spell_id]
        
        # Filter podle typu
        if spell_type != "all" and spell['type'] != spell_type:
            continue
        
        # Kontrola cooldownu
        can_cast, _ = player.can_cast_spell_now(spell_id)
        if can_cast:
            available.append((spell_id, spell))
    
    return available
 
 
# ========== /DUEL PŘÍKAZ ==========
 
@bot.tree.command(name="duel", description="Vyzvi někoho k souboji (NOVÝ SYSTÉM)")
@app_commands.describe(opponent="Soupeř kterého chceš vyzvat")
async def challenge_duel(interaction: discord.Interaction, opponent: discord.Member):
    """
    Vyzve hráče k souboji s POKROČILÝM UI:
    - Separátní embedy pro každého hráče
    - Real-time statistiky
    - Dropdown pro útok i obranu
    - Combat logging
    - Proper death handling
    """
    
    # Získej challenger
    challenger = get_player(interaction)
    
    # Základní kontroly
    if opponent.id == interaction.user.id:
        await interaction.response.send_message(
            "❌ Nemůžeš vyzvat sám sebe!",
            ephemeral=True
        )
        return
    
    if opponent.bot:
        await interaction.response.send_message(
            "❌ Nemůžeš vyzvat bota!",
            ephemeral=True
        )
        return
    
    if not challenger.is_alive():
        await interaction.response.send_message(
            "❌ Jsi mrtvý! Použij `/revive` pro novou postavu.",
            ephemeral=True
        )
        return
    
    if challenger.in_combat:
        await interaction.response.send_message(
            "❌ Už jsi v souboji!",
            ephemeral=True
        )
        return
    
    # View pro přijetí/odmítnutí
    class DuelAcceptView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60.0)
        
        @discord.ui.button(label="✅ Přijmout", style=discord.ButtonStyle.green)
        async def accept(self, button_interaction: discord.Interaction, button: discord.ui.Button):
            if button_interaction.user.id != opponent.id:
                await button_interaction.response.send_message(
                    "❌ Tohle není pro tebe!",
                    ephemeral=True
                )
                return
            
            # Získej target
            target = player_db.get_or_create_player(opponent.id, opponent.display_name)
            
            if not target.is_alive():
                await button_interaction.response.send_message(
                    "❌ Jsi mrtvý! Použij `/revive`.",
                    ephemeral=True
                )
                return
            
            if target.in_combat:
                await button_interaction.response.send_message(
                    "❌ Už jsi v souboji!",
                    ephemeral=True
                )
                return
            
            # Vytvoř souboj
            duel = combat_engine.create_duel(challenger, target)
            duel.start()
            
            # Vytvoř advanced manager (s combat loggerem pokud je dostupný)
            if COMBAT_LOGGER_AVAILABLE and hasattr(bot, 'combat_logger'):
                duel_manager_instance = AdvancedDuelManager(combat_engine, bot.combat_logger)
            else:
                duel_manager_instance = AdvancedDuelManager(combat_engine)
            
            # Ulož do globální paměti
            if not hasattr(bot, 'active_duel_managers'):
                bot.active_duel_managers = {}
            bot.active_duel_managers[interaction.channel_id] = duel_manager_instance
            
            # Start duel
            duel_manager_instance.start_duel(
                interaction.channel_id,
                duel,
                interaction.user,
                opponent
            )
            
            # Notifikace
            await button_interaction.response.send_message(
                f"⚔️ **SOUBOJ ZAČÍNÁ!**\n"
                f"**{challenger.name}** vs **{target.name}**\n\n"
                f"🎮 Každý hráč dostane vlastní panel s akcemi.\n"
                f"📊 Statistiky se aktualizují real-time.\n"
                f"⚠️ Smrt je trvalá!"
            )
            
            # Spusť první tah
            await start_duel_turn(interaction.channel, interaction.channel_id, duel_manager_instance)
            
            self.stop()
        
        @discord.ui.button(label="❌ Odmítnout", style=discord.ButtonStyle.red)
        async def decline(self, button_interaction: discord.Interaction, button: discord.ui.Button):
            if button_interaction.user.id != opponent.id:
                await button_interaction.response.send_message(
                    "❌ Tohle není pro tebe!",
                    ephemeral=True
                )
                return
            
            await button_interaction.response.send_message(
                f"❌ {opponent.display_name} odmítl souboj!"
            )
            self.stop()
    
    # Výzva
    embed = discord.Embed(
        title="⚔️ Výzva k souboji!",
        description=(
            f"**{interaction.user.display_name}** vyzývá **{opponent.display_name}** k souboji!\n\n"
            f"⚠️ **VAROVÁNÍ:** Souboj je na život a na smrt!\n"
            f"🩸 Zranění jsou realistická - můžeš vykrvácet nebo zemřít.\n"
            f"💀 Smrt je trvalá!\n\n"
            f"🎮 **NOVÝ SYSTÉM:**\n"
            f"• Každý hráč má vlastní panel s akcemi\n"
            f"• Real-time statistiky (vědomí, krev, zranění)\n"
            f"• Dropdown menu pro výběr kouzel\n"
            f"• Jedním klikem použít kouzlo\n"
            f"• Combat logging pro komentátora\n\n"
            f"{opponent.mention}, přijmeš výzvu?"
        ),
        color=discord.Color.orange()
    )
    
    await interaction.response.send_message(
        embed=embed,
        view=DuelAcceptView()
    )
 
 
async def start_duel_turn(channel, channel_id: int, manager: AdvancedDuelManager):
    """
    Začne nový tah - nejdřív útočník, pak obránce.
    """
    state = manager.get_state(channel_id)
    if not state:
        return
    
    duel = state['duel']
    
    # === Kontrola smrti ===
    if not duel.player1.is_alive() or duel.player1.consciousness <= 0:
        await handle_duel_death(channel, channel_id, manager, duel.player2, duel.player1, 
                                "Zemřel" if not duel.player1.is_alive() else "Ztratil vědomí")
        return
    
    if not duel.player2.is_alive() or duel.player2.consciousness <= 0:
        await handle_duel_death(channel, channel_id, manager, duel.player1, duel.player2,
                                "Zemřel" if not duel.player2.is_alive() else "Ztratil vědomí")
        return
    
    # === Kdo útočí/brání se ===
    attacker, attacker_user = manager.get_current_attacker(channel_id)
    defender, defender_user = manager.get_current_defender(channel_id)
    turn_num = state['current_turn']
    
    # === Oznámení ===
    await channel.send(
        f"⚔️ **TAH {turn_num}** | {attacker_user.mention} útočí → {defender_user.mention} se brání"
    )
    
    # === EMBED PRO ÚTOČNÍKA ===
    attacker_spells = get_available_spells(attacker)
    attacker_embed = DuelEmbedBuilder.create_attacker_embed(attacker, defender, turn_num, attacker_spells)
    
    async def attacker_callback(action, spell_id):
        await handle_attacker_action(channel, channel_id, manager, action, spell_id)
    
    attacker_view = AttackerActionView(manager, channel_id, attacker, attacker_callback)
    
    attacker_msg = await channel.send(
        content=f"**{attacker_user.mention} - TVŮJ TAH (útočíš)**",
        embed=attacker_embed,
        view=attacker_view
    )
    state['attacker_message'] = attacker_msg
    
    # === ČEKACÍ EMBED PRO OBRÁNCE ===
    waiting_embed = DuelEmbedBuilder.create_waiting_embed(defender, attacker, turn_num, is_attacker=False)
    
    defender_msg = await channel.send(
        content=f"**{defender_user.mention} - Čekáš na útok soupeře...**",
        embed=waiting_embed
    )
    state['defender_message'] = defender_msg


# ========== NOVÁ FUNKCE ==========

async def handle_attacker_action(channel, channel_id: int, manager: AdvancedDuelManager, action, spell_id):
    """
    Zpracuje akci útočníka.
    """
    state = manager.get_state(channel_id)
    if not state:
        return
    
    manager.set_attack(channel_id, action, spell_id)
    
    duel = state['duel']
    attacker, attacker_user = manager.get_current_attacker(channel_id)
    defender, defender_user = manager.get_current_defender(channel_id)
    turn_num = state['current_turn']
    
    # === LÉČENÍ/UTILITY - obránce nic nedělá ===
    if action == CombatAction.HEAL:
        spell = SPELLS_DATABASE.get(spell_id, {})
        spell_name = spell.get('name_cs', 'Neznámé kouzlo')
        spell_desc = spell.get('description', 'Kouzlo bylo aktivováno.')
        spell_type = spell.get('type', 'utility')
        
        # Truncate description if too long
        if len(spell_desc) > 300:
            spell_desc = spell_desc[:297] + "..."
        
        # If it's actually a healing spell, try to heal
        if spell_type in ['healing', 'minor_healing', 'awakening']:
            success, msg = manager.combat_engine.heal_injury(attacker, attacker, spell_id)
            await channel.send(f"💚 **{attacker.name}** používá **{spell_name}**!\n{msg}")
        else:
            # For other utility spells, just show the description
            await channel.send(f"✨ **{attacker.name}** používá **{spell_name}**!\n📖 {spell_desc}")
        
        # Update players to show blood/consciousness changes
        attacker.update(1.0)
        defender.update(1.0)
        
        manager.advance_turn(channel_id)
        await asyncio.sleep(2)
        await start_duel_turn(channel, channel_id, manager)
        return
    
    # === DEFENZIVA - obránce nic nedělá ===
    if action == CombatAction.DEFEND:
        spell = SPELLS_DATABASE.get(spell_id, {})
        await channel.send(f"🛡️ **{attacker.name}** se připravuje na obranu...")
        
        # Update players to show blood/consciousness changes
        attacker.update(1.0)
        defender.update(1.0)
        
        manager.advance_turn(channel_id)
        await asyncio.sleep(2)
        await start_duel_turn(channel, channel_id, manager)
        return
    
    # === ÚTOK - obránce musí reagovat ===
    
    # Update útočníkovy zprávy
    if state.get('attacker_message'):
        try:
            waiting_embed = DuelEmbedBuilder.create_waiting_embed(attacker, defender, turn_num, is_attacker=True)
            await state['attacker_message'].edit(
                content=f"**{attacker_user.mention} - Útok vyslán! Čekáš...**",
                embed=waiting_embed,
                view=None
            )
        except:
            pass
    
    # === POŠLI OBRÁNCI JEHO PANEL ===
    defensive_spells = get_available_spells(defender, "defensive")
    defender_embed = DuelEmbedBuilder.create_defender_embed(defender, attacker, turn_num, spell_id, defensive_spells)
    
    async def defender_callback(def_action, def_spell_id):
        await handle_defender_action(channel, channel_id, manager, def_action, def_spell_id)
    
    defender_view = DefenderActionView(manager, channel_id, defender, defender_callback)
    
    if state.get('defender_message'):
        try:
            await state['defender_message'].edit(
                content=f"**{defender_user.mention} - BRAŇ SE!**",
                embed=defender_embed,
                view=defender_view
            )
        except:
            defender_msg = await channel.send(
                content=f"**{defender_user.mention} - BRAŇ SE!**",
                embed=defender_embed,
                view=defender_view
            )
            state['defender_message'] = defender_msg


# ========== NOVÁ FUNKCE ==========

async def handle_defender_action(channel, channel_id: int, manager: AdvancedDuelManager, action, spell_id):
    """
    Zpracuje reakci obránce a vyhodnotí tah.
    """
    state = manager.get_state(channel_id)
    if not state:
        return
    
    manager.set_defense(channel_id, action, spell_id)
    await resolve_turn(channel, channel_id, manager)


# ========== NOVÁ FUNKCE ==========

async def resolve_turn(channel, channel_id: int, manager: AdvancedDuelManager):
    """
    Vyhodnotí tah.
    """
    state = manager.get_state(channel_id)
    if not state:
        return
    
    duel = state['duel']
    attacker, attacker_user = manager.get_current_attacker(channel_id)
    defender, defender_user = manager.get_current_defender(channel_id)
    turn_num = state['current_turn']
    
    attack_action = state['pending_attack_action']
    attack_spell = state['pending_attack_spell']
    defend_action = state['pending_defend_action']
    defend_spell = state['pending_defend_spell']
    
    messages = [f"\n🎭 **VYHODNOCENÍ TAHU {turn_num}**\n"]
    
    # Update hráčů
    attacker.update(1.0)
    defender.update(1.0)
    
    # === ÚTOK ===
    if attack_action == CombatAction.ATTACK and attack_spell:
        defense = None
        if defend_action == CombatAction.DEFEND and defend_spell:
            defense = defend_spell
            # Add description for defensive spell used
            def_spell_data = SPELLS_DATABASE.get(defend_spell, {})
            def_spell_name = def_spell_data.get('name_cs', 'Neznámé kouzlo')
            def_spell_desc = def_spell_data.get('description', '')
            if len(def_spell_desc) > 200:
                def_spell_desc = def_spell_desc[:197] + "..."
            messages.append(f"🛡️ **{defender.name}** aktivuje **{def_spell_name}**!\n✨ {def_spell_desc}\n")
        elif defend_action == CombatAction.DODGE:
            if defend_spell:  # Pokud má spell, jde o skutečný dodge
                defense = "dodge"
                messages.append(f"⏭️ **{defender.name}** se pokouší uhýbat!\n")
            else:  # Pokud je spell None, znamená to "přijmout ránu bez obrany"
                defense = None
                messages.append(f"⏭️ **{defender.name}** přijímá útok bez obrany!\n")
        
        result, spell_msgs, injuries = manager.combat_engine.cast_spell(
            attacker, defender, attack_spell, defense
        )
        messages.extend(spell_msgs)
        
        if manager.combat_logger:
            spell = SPELLS_DATABASE.get(attack_spell, {})
            manager.combat_logger.log_spell_cast(
                duel.duel_id, turn_num, attacker, spell.get('name_cs', attack_spell),
                defender, result.value,
                "\n".join([i.description for i in injuries]) if injuries else None
            )
    
    # === PROTIÚTOK ===
    if defend_action == CombatAction.ATTACK and defend_spell:
        messages.append(f"\n⚔️ **{defender.name} PROTIÚTOČÍ!**\n")
        
        result, spell_msgs, injuries = manager.combat_engine.cast_spell(
            defender, attacker, defend_spell, None
        )
        messages.extend(spell_msgs)
        
        if manager.combat_logger:
            spell = SPELLS_DATABASE.get(defend_spell, {})
            manager.combat_logger.log_spell_cast(
                duel.duel_id, turn_num, defender, spell.get('name_cs', defend_spell),
                attacker, result.value,
                "\n".join([i.description for i in injuries]) if injuries else None
            )
    
    # === KONTROLA SMRTI ===
    if not attacker.is_alive() or attacker.consciousness <= 0:
        messages.append(f"\n💀 **{attacker.name} {'ZEMŘEL' if not attacker.is_alive() else 'ZTRATIL VĚDOMÍ'}!**")
        await channel.send("\n".join(messages))
        await handle_duel_death(channel, channel_id, manager, defender, attacker, "Zemřel v souboji")
        return
    
    if not defender.is_alive() or defender.consciousness <= 0:
        messages.append(f"\n💀 **{defender.name} {'ZEMŘEL' if not defender.is_alive() else 'ZTRATIL VĚDOMÍ'}!**")
        await channel.send("\n".join(messages))
        await handle_duel_death(channel, channel_id, manager, attacker, defender, "Zemřel v souboji")
        return
    
    # === VÝSLEDKY ===
    result_embed = DuelEmbedBuilder.create_result_embed(attacker, defender, turn_num, messages)
    await channel.send(embed=result_embed)
    
    player_db.save()
    
    # === DALŠÍ TAH ===
    manager.advance_turn(channel_id)
    
    await asyncio.sleep(3)
    await start_duel_turn(channel, channel_id, manager)
 
async def handle_duel_death(
    channel,
    channel_id: int,
    manager: AdvancedDuelManager,
    winner: Player,
    loser: Player,
    cause: str
):
    """Zpracuje smrt v souboji"""
    
    # Oznámení
    embed = discord.Embed(
        title="💀 SOUBOJ UKONČEN!",
        description=(
            f"**🏆 VÍTĚZ: {winner.name}**\n"
            f"**💀 PORAŽENÝ: {loser.name}**\n\n"
            f"**Příčina smrti:** {cause}\n\n"
            f"📊 **FINÁLNÍ STATISTIKY:**\n\n"
            f"**{winner.name}:**\n"
            f"💚 Vědomí: {winner.consciousness:.0f}%\n"
            f"🩸 Krev: {winner.blood_volume:.0f} ml\n"
            f"🤕 Zranění: {sum(len(bp.injuries) for bp in winner.body.values())}x\n\n"
            f"**{loser.name}:**\n"
            f"💀 Mrtvý\n"
            f"🩸 Krev: {loser.blood_volume:.0f} ml\n"
            f"🤕 Zranění: {sum(len(bp.injuries) for bp in loser.body.values())}x\n"
        ),
        color=discord.Color.gold()
    )
    
    await channel.send(embed=embed)
    
    # Aktualizuj statistiky
    state = manager.get_state(channel_id)
    if state:
        duel = state['duel']
        duel.end(winner)
    
    # Log death
    if manager.combat_logger:
        manager.combat_logger.log_death(
            loser,
            cause,
            killer=winner,
            location="Discord Arena"
        )
    
    # Ukončí souboj
    manager.end_duel(channel_id, winner, loser)
    
    # Cleanup
    if hasattr(bot, 'active_duel_managers') and channel_id in bot.active_duel_managers:
        del bot.active_duel_managers[channel_id]
    
    # Ulož
    player_db.save()




# ========== STARŠÍ PŘÍKAZY PRO BACKWARD COMPATIBILITY ==========
# /cast a /defend jsou nyní nahrazeny UI tlačítky v souboji
# Ponecháno pouze pro zpětnou kompatibilitu mimo souboj

@bot.tree.command(name="cast_utility", description="Sesli utility kouzlo mimo souboj")
@app_commands.describe(spell="Utility kouzlo (lumos, alohomora...)")
async def cast_utility_command(interaction: discord.Interaction, spell: str):
    """Sesílá utility kouzla mimo souboj"""
    player = get_player(interaction)
    
    spell_id = spell.lower().replace(" ", "_")
    
    if spell_id not in SPELLS_DATABASE:
        await interaction.response.send_message(
            f"❌ Kouzlo '{spell}' neexistuje!",
            ephemeral=True
        )
        return
    
    spell_data = SPELLS_DATABASE[spell_id]
    
    if spell_data['type'] == 'combat':
        await interaction.response.send_message(
            "❌ Útočná kouzla lze používat pouze v souboji! Použij `/duel` nejdřív.",
            ephemeral=True
        )
        return
    
    # Utility kouzlo
    success, message = combat_engine.cast_utility_spell(
        player,
        spell_id,
        context="Discord command"
    )
    
    if success:
        embed = discord.Embed(
            title=f"✨ {spell_data['name_cs']}",
            description=message,
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    player_db.save()


@bot.tree.command(name="defend", description="Braň se štítovým kouzlem")
async def defend_command(interaction: discord.Interaction):
    """Obrana v souboji - zastaralý příkaz, používej UI tlačítka"""
    await interaction.response.send_message(
        "ℹ️ **Nový systém soubojů!**\n"
        "Obrana se nyní provádí pomocí tlačítek přímo v souboji.\n"
        "Když tě někdo napadne, objeví se tlačítka:\n"
        "🛡️ BRÁNIT | 💨 UHNOUT | 💚 LÉČIT",
        ephemeral=True
    )


@bot.tree.command(name="heal", description="Pokus se vyléčit zranění")
@app_commands.describe(
    spell="Léčivé kouzlo (episkey, vulnera_sanentur)",
    target="Koho chceš léčit (prázdné = sebe)"
)
async def heal_command(
    interaction: discord.Interaction,
    spell: str,
    target: Optional[discord.Member] = None
):
    """Léčí zranění"""
    healer = get_player(interaction)
    
    if target:
        target_player = player_db.get_or_create_player(target.id, target.display_name)
    else:
        target_player = healer
    
    spell_id = spell.lower().replace(" ", "_")
    
    success, message = combat_engine.heal_injury(
        healer, target_player, spell_id
    )
    
    if success:
        embed = discord.Embed(
            title="💚 Léčení",
            description=message,
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    player_db.save()


@bot.tree.command(name="revive", description="Vytvoř novou postavu po smrti")
async def revive_command(interaction: discord.Interaction):
    """Oživení = nová postava"""
    player = get_player(interaction)
    
    if player.is_alive():
        await interaction.response.send_message(
            "❌ Jsi naživu! Oživení není potřeba.",
            ephemeral=True
        )
        return
    
    # Vytvoř novou postavu
    player.revive()
    player_db.save()
    
    embed = discord.Embed(
        title="✨ Nová postava",
        description=(
            f"**{player.name}** byl obnoven!\n\n"
            f"⚠️ Všechna kouzla byla zapomenuta!\n"
            f"📚 Musíš se je naučit znovu.\n"
            f"🌟 Reputace byla resetována.\n\n"
            f"📊 Celkové statistiky:\n"
            f"💀 Celkem zemřel: {player.times_died}krát\n"
            f"🎯 Celkových soubojů: {player.total_duels}"
        ),
        color=discord.Color.blue()
    )
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="help", description="Nápověda k botovi")
async def help_command(interaction: discord.Interaction):
    """Zobrazí nápovědu"""
    embed = discord.Embed(
        title="🪄 Harry Potter Soubojový Bot - Nápověda",
        description="Realistické souboje bez HP! Každé zranění má následky.",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="📊 Základní příkazy",
        value=(
            "`/status` - Tvůj současný stav\n"
            "`/spells` - Seznam všech kouzel\n"
            "`/learn <kouzlo>` - Nauč se kouzlo\n"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚔️ Nový reaktivní soubojový systém",
        value=(
            "`/duel @hráč` - Vyzvi k souboji\n\n"
            "**🎮 Jak to funguje:**\n"
            "1️⃣ Útočník vybere kouzlo z **dropdown menu**\n"
            "2️⃣ Klikne na **⚔️ ÚTOK**\n"
            "3️⃣ Obránce má **5 sekund** reagovat:\n"
            "   • 🛡️ **BRÁNIT** - Protego štít\n"
            "   • 💨 **UHNOUT** - Pokus uhnout\n"
            "   • 💚 **LÉČIT** - Vyléčit se\n"
            "4️⃣ Tahy se střídají\n\n"
            "✨ **Zobrazení cooldownů v real-time**\n"
            "📊 **Živý status obou hráčů**\n"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🔧 Další příkazy",
        value=(
            "`/cast_utility <kouzlo>` - Utility kouzla mimo souboj\n"
            "`/heal <kouzlo>` - Vyléč zranění mimo souboj\n"
            "`/revive` - Vytvoř novou postavu po smrti\n"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚠️ DŮLEŽITÉ",
        value=(
            "• Smrt je **trvalá**! Ztratíš všechna naučená kouzla.\n"
            "• Zranění jsou **realistická** - můžeš ztratit končetiny.\n"
            "• Vykrvácení je **postupné** - léčení je důležité.\n"
            "• Zakázaná kouzla sníží tvou **reputaci**.\n"
            "• Máš **5 sekund** reagovat na útok!\n"
        ),
        inline=False
    )
    
    embed.set_footer(text="Bojuj statečně! ⚡")
    
    await interaction.response.send_message(embed=embed)

import discord
from discord import app_commands
from discord.ext import commands
import json
import os

# --- KONFIGURACE ---
# Název souboru pro uložení ID kanálu
CONFIG_FILE = "server_config.json"
# Barva Embed zprávy (Temně fialová)
EMBED_COLOR = 0x4b0082 

# --- POMOCNÉ FUNKCE PRO UKLÁDÁNÍ KONFIGURACE ---
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# --- TVŮJ UPRAVENÝ TEXT (Vytvořený jako Embed) ---
def create_welcome_embed():
    # Vytvoření Embed objektu
    embed = discord.Embed(
        title="✨ VITEJ V HOGWARTS ┃ VITALIS ✨",
        description="Vazeny kouzelniku,\n\nbyl jsi prijat do studia na nasi akademii. Upozornujeme vsak, ze v techto prostorach magie neni jen hrou cisel – je to zivy organismus, ktery reaguje na kazdy tvuj pohyb.",
        color=EMBED_COLOR
    )

    # Přidání polí (Fields) pro inicializaci stavu
    embed.add_field(name="🩸 ┃ BLOOD_VOLUME", value="5000.0 ml (Stable)", inline=False)
    embed.add_field(name="🪄 ┃ STATUS", value="NOVICE", inline=False)
    embed.add_field(name="🛡️ ┃ DIRECTIVE", value="Dodrzuj pokyny Ministerstva a v Zapovezenem lese bud obezretny.", inline=False)

    # Přidání hlavního pravidla a kroků
    embed.add_field(name="\n══════════════════════════", value="**Kazda rana zanecha stopu.** Neze se vydas do Areny nebo Zapovezeneho lesa, ujisti se, ze mas v poradku sve zaklinadlo *Protego* a znas zaklady magie leceni.", inline=False)
    
    steps = (
        "1. 🏰 ┃ **Zvol si svou kolej** v kanale #zařazování\n"
        "2. 📖 ┃ **Prostuduj zakony** v kanale #pravidla-a-zakony\n"
        "3. 🧪 ┃ **Ohlas se v osetrovne**, pokud pocitis nahlou ztratu energie."
    )
    embed.add_field(name="Prvni kroky pro novacka:", value=steps, inline=False)

    # Přidání citátu a patičky
    embed.set_footer(text="„Magie je mocna, ale krev je cenou, kterou nelze splatit nicim jinym nez zivotem.“\n\nPROTOKOL VITALIS BYL SPUSTEN.")
    
    return embed

# --- NASTAVENÍ BOTA (Předpokládá se, že už máš základní setup) ---
# Pokud ne, použij tohle:
# intents = discord.Intents.default()
# intents.members = True # Nutné pro on_member_join
# bot = commands.Bot(command_prefix="!", intents=intents)

import discord
from discord import app_commands
from discord.ext import commands
import json
import os

# --- KONFIGURACE ---
CONFIG_FILE = "server_config.json"
EMBED_COLOR = 0x4b0082 


# --- POMOCNÉ FUNKCE ---
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def create_welcome_embed():
    embed = discord.Embed(
        title="✨ VITEJTE V HOGWARTS ┃ VITALIS ✨",
        description=(
            "SKOLA CAR A KOUZEL V BRADAVICICH\n"
            "------------------------------------------\n\n"
            "Vazeny kouzelniku,\n\n"
            "s velkou radosti Ti oznamujeme, ze jsi byl prijat do nasi akademie. "
            "Vitame Te v komunite, kde se magie setkava s pratelstvim a kde kazdy z nas pise svuj vlastni pribeh.\n\n"
            "Bradavice nejsou jen mistem pro studium – jsou domovem, kde si muzes pokecat s ostatnimi, "
            "najit si nove pratele v nasi Velke sini a prozit magicke chvile. Pokud mas odvahu, "
            "muzes vyzkouset i nas unikatni system Vitalis, ktery vnasi do tvych RP pribehu kapku adrenalinu."
        ),
        color=EMBED_COLOR
    )

    embed.add_field(
        name="🏰 ┃ Zivot v nasi komunite", 
        value="V nasi Velke sini na Tebe ceka parta fajn lidi. Prijd se jen tak pozdravit a uzij si magickou atmosferu.", 
        inline=False
    )
    
    embed.add_field(
        name="🛡️ ┃ Magicky system Vitalis", 
        value="Pro nase pribehy jsme si pripravili unikatni system zivotni sily. Je to jen bonus, ktery dela nase dobrodruzstvi autentictejsi.", 
        inline=False
    )

    steps = (
        "1. 🏛️ ┃ **Zvol si svou kolej** v kanale #zařazování\n"
        "2. 🕯️ ┃ **Pozdrav ostatni** v kanale #velká-síň\n"
        "3. 📖 ┃ **Prostuduj tradice** v kanale #pravidla-a-zakony"
    )
    embed.add_field(name="Tvuj prvni den v Bradavicich:", value=steps, inline=False)
    
    embed.set_footer(
        text="„Hogwarts bude vzdycky tvym domovem, at uz se vratis jakoukoliv cestou.“\n\nVAS DOPIS BYL DORUCEN."
    )
    return embed
# --- UDÁLOST: PŘIPOJENÍ NOVÉHO ČLENA ---
@bot.event
async def on_member_join(member):
    # --- AUTOMATICKÉ PŘIDĚLENÍ ROLE CITIZEN ---
    role_citizen = member.guild.get_role(ROLE_CITIZEN_ID)
    if role_citizen:
        try:
            await member.add_roles(role_citizen)
            print(f"✅ Role {role_citizen.name} přidělena uživateli {member.name}.")
        except Exception as e:
            print(f"❌ Chyba při přidělování role: {e}")

    # --- UVÍTACÍ ZPRÁVA ---
    config = load_config()
    guild_id = str(member.guild.id)
    
    if guild_id in config and "welcome_channel_id" in config[guild_id]:
        channel_id = config[guild_id]["welcome_channel_id"]
        channel = member.guild.get_channel(channel_id)
        
        if channel:
            embed = create_welcome_embed()
            embed.set_image(url=IMG_URL)
            await channel.send(f"Vítej v našem kouzelnickém světě, {member.mention}!", embed=embed)
            print(f"✅ Uvitaci zprava poslana pro {member.name}.")

# --- SLASH PŘÍKAZY ---
@bot.tree.command(name="setup_welcome", description="Nastavi kanal pro uvitaci dopis.")
@app_commands.describe(channel="Kanal pro uvitani novych clenu.")
@app_commands.default_permissions(administrator=True)
async def setup_welcome(interaction: discord.Interaction, channel: discord.TextChannel):
    config = load_config()
    guild_id = str(interaction.guild.id)
    
    if guild_id not in config:
        config[guild_id] = {}
    config[guild_id]["welcome_channel_id"] = channel.id
    save_config(config)
    
    await interaction.response.send_message(f"✅ Uvitaci kanal nastaven na: {channel.mention}.", ephemeral=True)

@bot.tree.command(name="test_welcome", description="Posle testovaci uvitaci dopis.")
@app_commands.default_permissions(administrator=True)
async def test_welcome(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = create_welcome_embed()
    embed.set_image(url=IMG_URL)
    await interaction.channel.send(f"Testovaci uvitani (spustil {interaction.user.mention}):", embed=embed)
    await interaction.followup.send("✅ Testovaci dopis byl odeslan.", ephemeral=True)
    
    
    
# --- KONFIGURACE KOLEJÍ ---
ROLES_HOUSES = {
    "Gryffindor": 1487595962217267231,
    "Slytherin": 1487595963433357323,
    "Ravenclaw": 1487595964242853908,
    "Hufflepuff": 1487595965014872276
}


# --- DOTAZNÍK MOUDRÉHO KLOBOUKU ---
class SortingHatModal(discord.ui.Modal, title='Moudrý klobouk: Zkouška povahy'):
    q1 = discord.ui.TextInput(
        label="V lese uvidíš raněné zvíře. Co uděláš?",
        placeholder="Pomůžu mu / Využiji ho / Budu ho studovat / Nechám ho být...",
        style=discord.TextStyle.short,
        required=True
    )
    q2 = discord.ui.TextInput(
        label="Jaká vlastnost je pro tebe nejdůležitější?",
        placeholder="Odvaha, věrnost, moc, nebo snad moudrost?",
        style=discord.TextStyle.short,
        required=True
    )
    q3 = discord.ui.TextInput(
        label="Co vidíš v zrcadle z Erisedu?",
        placeholder="Popiš své nejhlubší přání...",
        style=discord.TextStyle.paragraph,
        required=True,
        min_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Inicializace bodů
        scores = {"Gryffindor": 0, "Slytherin": 0, "Ravenclaw": 0, "Hufflepuff": 0}
        ans = (self.q1.value + " " + self.q2.value + " " + self.q3.value).lower()

        # --- ROZŠÍŘENÁ LOGIKA BODOVÁNÍ ---
        if any(w in ans for w in ["pomo", "zachrán", "přím", "nebezpeč", "hrdin", "odvah", "boj", "lev", "meč", "přítel", "čest"]):
            scores["Gryffindor"] += 5
        if any(w in ans for w in ["využ", "moc", "sláv", "peníz", "vlastní", "skryt", "ambic", "had", "vůdce", "vítěz", "pýcha"]):
            scores["Slytherin"] += 5
        if any(w in ans for w in ["stud", "věd", "chyt", "rozum", "knih", "pravd", "orel", "hádank", "učit", "logik", "plán"]):
            scores["Ravenclaw"] += 5
        if any(w in ans for w in ["klid", "domov", "přát", "věrn", "všich", "pomáh", "jezev", "lásk", "rodin", "spraved", "práce"]):
            scores["Hufflepuff"] += 5

        # Výběr koleje (nebo náhoda, pokud není shoda)
        if all(v == 0 for v in scores.values()):
            import random
            sorted_house = random.choice(list(ROLES_HOUSES.keys()))
        else:
            sorted_house = max(scores, key=scores.get)

        role_house = interaction.guild.get_role(ROLES_HOUSES[sorted_house])
        role_citizen = interaction.guild.get_role(ROLE_CITIZEN_ID)
        role_novice = interaction.guild.get_role(ROLE_NOVICE_ID)
        
        if role_house:
            try:
                # 1. Vyčištění starých kolejí (pokud by někdo zkoušel klobouk znovu)
                all_house_roles = [interaction.guild.get_role(rid) for rid in ROLES_HOUSES.values() if rid]
                roles_to_remove = [r for r in all_house_roles if r and r in interaction.user.roles]
                
                # 2. Přidáme do seznamu k odebrání i roli CITIZEN
                if role_citizen and role_citizen in interaction.user.roles:
                    roles_to_remove.append(role_citizen)
                
                if roles_to_remove:
                    await interaction.user.remove_roles(*roles_to_remove)
                
                # 3. Přidání nové KOLEJE a role NOVICE
                roles_to_add = [role_house]
                if role_novice:
                    roles_to_add.append(role_novice)
                
                await interaction.user.add_roles(*roles_to_add)

                # Speciální popisy
                descriptions = {
                    "Gryffindor": "Cítím v tobě oheň, který nehasne! Tvá odvaha a rytířskost tě předurčují k velkým činům.",
                    "Slytherin": "Hm... vidím ambice a mazanost. Máš v sobě sílu dosáhnout všeho, co si umaneš.",
                    "Ravenclaw": "Tvá mysl je ostrá jako břitva. Najdeš domov mezi těmi, kteří si váží vědění nade vše.",
                    "Hufflepuff": "Tvé srdce je čisté a věrné. Jsi pilný a čestný – to je pravá síla Mrzimoru."
                }

                embed = discord.Embed(
                    title="🎩 MOUDRÝ KLOBOUK PROMLUVIL!",
                    description=(
                        f"Klobouk se ti na hlavě zakroutil, zamumlal pár slov a pak vykřikl do celé síně:\n\n"
                        f"# **{sorted_house.upper()}**\n\n"
                        f"*{descriptions[sorted_house]}*\n\n"
                        f"🛡️ *Nyní jsi oficiálně studentem (**Novice**).*"
                    ),
                    color=role_house.color
                )
                embed.set_thumbnail(url=SORTING_HAT_IMG)
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
            except Exception as e:
                await interaction.response.send_message(f"❌ Chyba při magických procesech: {e}", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Kolej nebyla nalezena. Kontaktuj Ministra kouzel.", ephemeral=True)

class SortingHatView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Předstoupit před klobouk", 
        style=discord.ButtonStyle.primary, 
        emoji="🎩", 
        custom_id="sorting_hat_button"
    )
    async def start_sorting(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SortingHatModal())

@bot.tree.command(name="setup_sorting", description="Vytvoří trvalou zprávu pro zařazování.")
@app_commands.default_permissions(administrator=True)
async def setup_sorting(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏰 Velká síň: Obřad zařazování",
        description=(
            "Tiše se posaďte na stoličku a nasaďte si Moudrý klobouk.\n\n"
            "On prozkoumá vaše nejniternější touhy, vaše silné stránky i vaše slabiny. "
            "Nebojte se, klobouk se málokdy mýlí... i když občas vidí věci, které vy sami ne."
        ),
        color=0x4b0082
    )
    # Zde v hlavní zprávě použijeme tvou pečeť (IMG_URL z tvého bot.py)
    embed.set_image(url=SORTING_HAT_IMG) 
    await interaction.channel.send(embed=embed, view=SortingHatView())
    await interaction.response.send_message("✅ Zařazovací systém byl spuštěn.", ephemeral=True) 
    
import os
import json

# --- SOUBOR PRO BODY ---
POINTS_FILE = "house_points.json"

def load_points():
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, 'r') as f:
            return json.load(f)
    return {"Gryffindor": 0, "Slytherin": 0, "Ravenclaw": 0, "Hufflepuff": 0}

def save_points(data):
    with open(POINTS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- PŘÍKAZY PRO MINISTRA ---

@bot.tree.command(name="kolej_body", description="Přidá nebo strhne body koleji.")
@app_commands.describe(
    kolej="Vyber kolej", 
    akce="Přidat nebo Strhnout", 
    mnozstvi="Počet bodů", 
    duvod="Proč body upravuješ?"
)
@app_commands.choices(
    kolej=[
        app_commands.Choice(name="Nebelvír", value="Gryffindor"),
        app_commands.Choice(name="Zmijozel", value="Slytherin"),
        app_commands.Choice(name="Havraspár", value="Ravenclaw"),
        app_commands.Choice(name="Mrzimor", value="Hufflepuff"),
    ],
    akce=[
        app_commands.Choice(name="➕ Přidat", value="add"),
        app_commands.Choice(name="➖ Strhnout", value="remove"),
    ]
)
# TENTO ŘÁDEK JE KLÍČOVÝ PRO SLASH PŘÍKAZY:
@app_commands.default_permissions(administrator=True) 
async def kolej_body(interaction: discord.Interaction, kolej: app_commands.Choice[str], akce: app_commands.Choice[str], mnozstvi: int, duvod: str):
    # Pro jistotu můžeme nechat i vnitřní kontrolu
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Pouze Ministr (Admin) může upravovat body kolejí!", ephemeral=True)
        return

    data = load_points()
    
    if akce.value == "add":
        data[kolej.value] += mnozstvi
        slovo = "přidal"
        barva = discord.Color.green()
    else:
        data[kolej.value] -= mnozstvi
        slovo = "strhl"
        barva = discord.Color.red()
        
    save_points(data)
    
    # Ikony kolejí pro embed
    icons = {
        "Gryffindor": "🦁",
        "Slytherin": "🐍",
        "Ravenclaw": "🦅",
        "Hufflepuff": "🦡"
    }
    
    embed = discord.Embed(
        title=f"{icons[kolej.value]} Změna bodů pro {kolej.name}",
        description=f"Ministr **{slovo}** koleji **{mnozstvi}** bodů.",
        color=barva
    )
    embed.add_field(name="📜 Důvod", value=duvod)
    embed.add_field(name="🏆 Nový stav", value=f"**{data[kolej.value]}** bodů", inline=False)
    embed.set_footer(text="Moudrý klobouk vše vidí...")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="pohar", description="Zobrazí aktuální stav školního poháru.")
async def pohar(interaction: discord.Interaction):
    data = load_points()
    # Seřazení kolejí podle bodů
    sorted_points = sorted(data.items(), key=lambda x: x[1], reverse=True)
    
    description = ""
    medals = ["🥇", "🥈", "🥉", "🏅"]
    
    for i, (kolej, body) in enumerate(sorted_points):
        name_cz = kolej.replace("Gryffindor", "Nebelvír").replace("Slytherin", "Zmijozel").replace("Ravenclaw", "Havraspár").replace("Hufflepuff", "Mrzimor")
        description += f"{medals[i]} **{name_cz}**: {body} bodů\n"

    embed = discord.Embed(
        title="🏆 Školní pohár - Aktuální pořadí",
        description=description,
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=SORTING_HAT_IMG)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="post_rules", description="Vystaví majestátní zákoník do kanálu pravidel.")
@app_commands.default_permissions(administrator=True)
async def post_rules(interaction: discord.Interaction):
    # První část: Úvod a Discord pravidla
    embed1 = discord.Embed(
        title="📜 KODEX KOUZELNICKÉHO PRÁVA A ETIKY",
        description=(
            "**Vítejte v oficiálním věstníku Ministerstva kouzel.**\n"
            "Následující řádky definují hranice mezi civilizovaným čarodějem a vyhnancem z Azkabanu. "
            "Neznalost zákona neomlouvá a každé porušení bude trestáno stržením bodů či vyhoštěním.\n\n"
            "### ⚖️ I. MEZINÁRODNÍ ZÁKONY (Discord Pravidla)\n"
            "* **Slušnost:** Respektujte ostatní kouzelníky. Urážky, šikana a nenávistné projevy jsou trestány kletbou 'Ban'.\n"
            "* **Spam:** Nepřehlcujte soví poštu (kanály) zbytečnými zprávami.\n"
            "* **Obsah:** Je přísně zakázáno šířit mudlovský nevhodný obsah (NSFW).\n"
            "* **Reklama:** Propagace jiných škol či spolků bez souhlasu Ministerstva je zapovězena."
        ),
        color=0x4b0082 # Temně fialová
    )
    embed1.set_image(url="https://cdn.discordapp.com/attachments/1487590069471674480/1487599149368086732/Gemini_Generated_Image_wk1rawk1rawk1raw.png?ex=69ca62eb&is=69c9116b&hm=460e2d74bd3c423567281b48513b4ba3833cee447741a409c0d70330ba89bbf6&") # Symbol spravedlnosti nebo pečeť

    # Druhá část: Kouzelnický svět a RP
    embed2 = discord.Embed(
        title="🪄 II. DEKRET O KOUZELNICKÉM ŽIVOTĚ (RP Pravidla)",
        description=(
            "### 🏆 ŠKOLNÍ POHÁR A BODY\n"
            "Vaše chování přímo ovlivňuje slávu vaší koleje. Body jsou udělovány za duely, aktivitu a pomoc ostatním. "
            "**Ministr a Prefekti** mají právo body strhávat za nevhodné chování.\n\n"
            "### ⚔️ SOUBOJE A MAGIE\n"
            "* **Úcta k soupeři:** Duel končí v momentě, kdy jeden z kouzelníků není schopen pokračovat.\n"
            "* **Zakázaná kouzla:** Použití Kleteb, které se nepromíjejí, mimo tréninkové arény může vést k okamžitému trestu.\n"
            "* **Roleplay:** V RP kanálech se chovejte jako vaše postava. Respektujte lore světa Harryho Pottera.\n\n"
            "### 🏛️ AUTORITA\n"
            "Slovo Ministra kouzel a Adminů je zákonem. Pokud máte pocit nespravedlnosti, podejte oficiální žádost v kanceláři Ministerstva."
        ),
        color=0x4b0082
    )
    
    # Použijeme tvůj nový obrázek se Školním pohárem na konec
    embed2.set_image(url=IMG_POHAR) 
    embed2.set_footer(text="Vydáno pod dohledem Moudrého klobouku.", icon_url=SORTING_HAT_IMG)

    await interaction.channel.send(embed=embed1)
    await interaction.channel.send(embed=embed2)
    await interaction.response.send_message("✅ Zákoník byl úspěšně vyvěšen.", ephemeral=True)    
    



# --- PŘÍKAZY PRO UVÍTÁNÍ V MÍSTNOSTECH ---

@bot.tree.command(name="welcome_gryffindor", description="Odešle majestátní uvítání do Nebelvírské věže.")
@app_commands.default_permissions(administrator=True)
async def welcome_gryffindor(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🦁 VÍTEJTE V NEBELVÍRSKÉ VĚŽI!",
        description=(
            "Před vámi praská krb a vzduch voní odvahou. Zde, pod ochranou lva, "
            "najdete domov plný rytířskosti a hrdinských činů.\n\n"
            "**„Kde odvaha a udatnost jsou doma, tam Nebelvír své věrné k sobě volá.“**\n\n"
            "Buďte hrdí na své barvy, studenti!"
        ),
        color=0x740001 # Nebelvírská červená
    )
    # Zde vložíme ten krásný interiér (image_20.png)
    embed.set_image(url=IMG_ROOM_GRYFFINDOR)
    embed.set_footer(text="Společenská místnost Nebelvíru", icon_url=SORTING_HAT_IMG)
    
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ Uvítání posláno.", ephemeral=True)

@bot.tree.command(name="welcome_slytherin", description="Odešle majestátní uvítání do Zmijozelského sklepení.")
@app_commands.default_permissions(administrator=True)
async def welcome_slytherin(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🐍 VÍTEJTE VE ZMIJOZELSKÉM SKLEPENÍ!",
        description=(
            "Voda jezera nad námi tiše šumí a nazelenalé světlo odhaluje tvou sílu. "
            "Zde, v hlubinách, kujeme plány na velikost.\n\n"
            "**„Zmijozel je pro ty, co ambice mají, a k moci a slávě cestu si najdou.“**\n\n"
            "Buďte mazaní a hrdí, studenti!"
        ),
        color=0x1A472A # Zmijozelská zelená
    )
    # Zde vložíme ten krásný interiér (image_21.png)
    embed.set_image(url=IMG_ROOM_SLYTHERIN)
    embed.set_footer(text="Společenská místnost Zmijozelu", icon_url=SORTING_HAT_IMG)
    
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ Uvítání posláno.", ephemeral=True)

@bot.tree.command(name="welcome_ravenclaw", description="Odešle majestátní uvítání do Havraspárské věže.")
@app_commands.default_permissions(administrator=True)
async def welcome_ravenclaw(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🦅 VÍTEJTE V HAVRASPÁRSKÉ VĚŽI!",
        description=(
            "Hvězdy jsou na dosah ruky a tisíce knih čekají na tvou mysl. "
            "Zde, vysoko nad hradem, ceníme moudrost nade vše.\n\n"
            "**„Havraspár je pro ty, co bystrou mysl mají, a učení a vědění si váží.“**\n\n"
            "Buďte zvídaví a originální, studenti!"
        ),
        color=0x0E1A40 # Havraspárská modrá
    )
    # Zde vložíme ten krásný interiér (image_22.png)
    embed.set_image(url=IMG_ROOM_RAVENCLAW)
    embed.set_footer(text="Společenská místnost Havraspáru", icon_url=SORTING_HAT_IMG)
    
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ Uvítání posláno.", ephemeral=True)

@bot.tree.command(name="welcome_hufflepuff", description="Odešle majestátní uvítání do Mrzimorského přístěnku.")
@app_commands.default_permissions(administrator=True)
async def welcome_hufflepuff(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🦡 VÍTEJTE V MRZIMORSKÉM PŘÍSTĚNKU!",
        description=(
            "Vůně bylin a teplo domova vás objímá. Zde, v bezpečí a klidu, "
            "si vážíme poctivé práce a věrnosti.\n\n"
            "**„Mrzimor je pro ty, co spravedliví jsou, a věrnost a přátelství ctí.“**\n\n"
            "Buďte dobří a loajální, studenti!"
        ),
        color=0xECB939 # Mrzimorská žlutá
    )
    # Zde vložíme ten krásný interiér (image_23.png)
    embed.set_image(url=IMG_ROOM_HUFFLEPUFF)
    embed.set_footer(text="Společenská místnost Mrzimoru", icon_url=SORTING_HAT_IMG)
    
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ Uvítání posláno.", ephemeral=True)


import discord
from discord import app_commands
from discord.ext import commands

# --- KONFIGURACE OBRÁZKŮ HŮLEK (⚠️ Doplň URL adresy z Discordu) ---
IMG_WAND_ELDER = "https://cdn.discordapp.com/attachments/1487590069471674480/1487866284904284260/Gemini_Generated_Image_ivvfxivvfxivvfxi.png?ex=69cab2f5&is=69c96175&hm=d998f12f0297f33ddbbcd5b9c93469e4d881719a139071617cdc1b6b4bc98a9c&"     # image_25.png
IMG_WAND_HARRY = "https://cdn.discordapp.com/attachments/1487590069471674480/1487866284413681664/Gemini_Generated_Image_ivvfxivvfxivvfxi1.png?ex=69cab2f5&is=69c96175&hm=8d23ef5d2961f5b259923a8f88901dd687b823d92bad7845c49d775d496f6600&"     # image_26.png
IMG_WAND_SNAPE = "https://cdn.discordapp.com/attachments/1487590069471674480/1487866286342930512/Gemini_Generated_Image_ivvfxivvfxivvfxi2.png?ex=69cab2f5&is=69c96175&hm=c1e36f3f42c5f16d7a67b9ce911eeaeda6c472d0dc01c1226e1da3306a5eee2e&"     # image_27.png
IMG_WAND_SCAMANDER = "https://cdn.discordapp.com/attachments/1487590069471674480/1487866285835550912/Gemini_Generated_Image_ivvfxivvfxivvfxi3.png?ex=69cab2f5&is=69c96175&hm=9327371e8bbe3e8c93b4437a58e130ad145ae66301db5316693b0d4aa7f6c826&" # image_28.png
IMG_WAND_GROUP = "https://cdn.discordapp.com/attachments/1487590069471674480/1487866285328044183/Gemini_Generated_Image_ivvfxivvfxivvfxi4.png?ex=69cab2f5&is=69c96175&hm=91eb6a8acf978b6a8fb96bf14169a08d80ac553a7129459c4040c71936052384&"     # image_29.png (Skupinový)
IMG_WAND_VOLDEMORT = "https://cdn.discordapp.com/attachments/1487590069471674480/1487867332905799857/Gemini_Generated_Image_2j8kgb2j8kgb2j8k.png?ex=69cab3ef&is=69c9626f&hm=e46629dad66ba858c91c07f430e998887aa2eeb20082aba67f754e4c898056f7&" # image_31.png
IMG_WAND_DUMBLEDORE = "https://cdn.discordapp.com/attachments/1487590069471674480/1487867332372987974/Gemini_Generated_Image_2j8kgb2j8kgb2j8k1.png?ex=69cab3ef&is=69c9626f&hm=f769cc6eb1cf15c4584d2fb4c5b51b5326ba680eb3eb6074f579dfcaca5c1437&" # image_32.png
IMG_WAND_HERMIONE = "https://cdn.discordapp.com/attachments/1487590069471674480/1487867331920269473/Gemini_Generated_Image_2j8kgb2j8kgb2j8k2.png?ex=69cab3ef&is=69c9626f&hm=4979fdfc257b6f51212e5070ba2f09a075d85565e71e5a038a32c62b02632e6f&"  # image_33.png
IMG_WAND_RON = "https://cdn.discordapp.com/attachments/1487590069471674480/1487867336622080071/Gemini_Generated_Image_2j8kgb2j8kgb2j8k3.png?ex=69cab3f0&is=69c96270&hm=578e5b6987de9ebe665eb6230060534d774f0000eb8c9eebb71ea0537d09c1d4&"       # image_34.png
IMG_WAND_DRACO = "https://cdn.discordapp.com/attachments/1487590069471674480/1487867335971832039/Gemini_Generated_Image_2j8kgb2j8kgb2j8k4.png?ex=69cab3f0&is=69c96270&hm=94749a5dfdc0d05387d12c4b08733becab5c302754c5e85cf782e875e1844d9e&"     # image_35.png
IMG_WAND_BELLATRIX = "https://cdn.discordapp.com/attachments/1487590069471674480/1487867335443480737/Gemini_Generated_Image_2j8kgb2j8kgb2j8k5.png?ex=69cab3f0&is=69c96270&hm=3765690811dc3364c206563340b28d2de1d511d0835f2db61671eefe531d2d52&" # image_36.png
IMG_WAND_MCGONAGALL = "https://cdn.discordapp.com/attachments/1487590069471674480/1487867334797299783/Gemini_Generated_Image_2j8kgb2j8kgb2j8k6.png?ex=69cab3ef&is=69c9626f&hm=251902b5795850421430493a3af06f292b7f87e921f24f16de9e35d3de937d0b&" # image_37.png
IMG_WAND_LUNA = "https://cdn.discordapp.com/attachments/1487590069471674480/1487867334352834650/Gemini_Generated_Image_2j8kgb2j8kgb2j8k7.png?ex=69cab3ef&is=69c9626f&hm=9d60e6810c44163658913cbf68e5a5043b49e045e31794141c4c48025b5ee7c0&"      # image_38.png
IMG_WAND_GRINDELWALD = "https://cdn.discordapp.com/attachments/1487590069471674480/1487867333874810980/Gemini_Generated_Image_2j8kgb2j8kgb2j8k8.png?ex=69cab3ef&is=69c9626f&hm=c64a5f32f58c4ac222a4eef2006c94cbf08397d3ffbfd36ad7250dab08e91178&" # image_39.png
IMG_WAND_DARK_EBONY = "https://cdn.discordapp.com/attachments/1487590069471674480/1487867333505454130/Gemini_Generated_Image_2j8kgb2j8kgb2j8k9.png?ex=69cab3ef&is=69c9626f&hm=7e7faeb1d3e8866b8653ac1b5cd63e72f61319e5f129c7d0133cdea824ddb513&" # image_40.png

# --- DATABÁZE HŮLEK ---
WANDS_DATA = {
    "wand_01": {"name": "Bezová hůlka", "wood": "Bez", "core": "Žíně testrála", "length": "15 palců", "desc": "Legendární hůlka smrti. Neporazitelná.", "img": IMG_WAND_ELDER},
    "wand_02": {"name": "Hůlka Harryho Pottera", "wood": "Cesmína", "core": "Pírko fénixe", "length": "11 palců", "desc": "Věrná a silná v obraně.", "img": IMG_WAND_HARRY},
    "wand_03": {"name": "Hůlka Lorda Voldemorta", "wood": "Tis", "core": "Pírko fénixe", "length": "13.5 palců", "desc": "Zlověstná a mocná.", "img": IMG_WAND_VOLDEMORT},
    "wand_04": {"name": "Hůlka Albuse Brumbála (pův.)", "wood": "Jabloň", "core": "Blána z dračího srdce", "length": "12.2 palců", "desc": "Ušlechtilá a moudrá.", "img": IMG_WAND_DUMBLEDORE},
    "wand_05": {"name": "Hůlka Hermiony Grangerové", "wood": "Vinná réva", "core": "Blána z dračího srdce", "length": "10.7 palců", "desc": "Líbí se ambiciózním.", "img": IMG_WAND_HERMIONE},
    "wand_06": {"name": "Hůlka Rona Weasleyho (dr.)", "wood": "Vrba", "core": "Žíně jednorožce", "length": "14 palců", "desc": "Věrná svému majiteli.", "img": IMG_WAND_RON},
    "wand_07": {"name": "Hůlka Draca Malfoye", "wood": "Hloh", "core": "Žíně jednorožce", "length": "10 palců", "desc": "Pro složité povahy.", "img": IMG_WAND_DRACO},
    "wand_08": {"name": "Hůlka Bellatrix Lestrangeové", "wood": "Vlašský ořech", "core": "Blána z dračího srdce", "length": "12.7 palců", "desc": "Smrtící nástroj.", "img": IMG_WAND_BELLATRIX},
    "wand_09": {"name": "Hůlka Minervy McGonagallové", "wood": "Jedle", "core": "Blána z dračího srdce", "length": "9.5 palců", "desc": "Elegantní a přesná.", "img": IMG_WAND_MCGONAGALL},
    "wand_10": {"name": "Hůlka Severuse Snapea", "wood": "Eben", "core": "Blána z dračího srdce", "length": "13 palců", "desc": "Pro mistry lektvarů.", "img": IMG_WAND_SNAPE},
    "wand_11": {"name": "Hůlka Luny Lovegoodové (dr.)", "wood": "Javor", "core": "Žíně jednorožce", "length": "11.5 palců", "desc": "Pro snílky a objevitele.", "img": IMG_WAND_LUNA},
    "wand_12": {"name": "Hůlka Mlokka Scamadera", "wood": "Jasan", "core": "Žíně testrála", "length": "13.2 palců", "desc": "Pro milovníky tvorů.", "img": IMG_WAND_SCAMANDER},
    "wand_13": {"name": "Hůlka Cedrica Diggoryho", "wood": "Jasan", "core": "Žíně jednorožce (hřebec)", "length": "12.2 palců", "desc": "Přímočará a čestná.", "img": IMG_WAND_GROUP}, # Použijeme skupinový
    "wand_14": {"name": "Hůlka Gellerta Grindelwalda", "wood": "Akácie", "core": "Blána z dračího srdce", "length": "12 palců", "desc": "Mocná a nepředvídatelná.", "img": IMG_WAND_GRINDELWALD},
    "wand_15": {"name": "Hůlka \"Temný Eben\"", "wood": "Černý eben", "core": "Pero fénixe (černé)", "length": "14 palců", "desc": "Pro skrytý potenciál.", "img": IMG_WAND_DARK_EBONY}
}

# --- KONFIGURACE ROLÍ HŮLEK (⚠️ Názvy rolí na serveru) ---
WAND_ROLES = {
    "wand_01": "Bezová hůlka", "wand_02": "Hůlka Harryho Pottera", "wand_03": "Hůlka Lorda Voldemorta",
    "wand_04": "Hůlka Albuse Brumbála (původní)", "wand_05": "Hůlka Hermiony Grangerové", "wand_06": "Hůlka Rona Weasleyho (druhá)",
    "wand_07": "Hůlka Draca Malfoye", "wand_08": "Hůlka Bellatrix Lestrangeové", "wand_09": "Hůlka Minervy McGonagallové",
    "wand_10": "Hůlka Severuse Snapea", "wand_11": "Hůlka Luny Lovegoodové (druhá)", "wand_12": "Hůlka Mlokka Scamadera",
    "wand_13": "Hůlka Cedrica Diggoryho", "wand_14": "Hůlka Gellerta Grindelwalda (mladého)", "wand_15": "Hůlka \"Temný Eben\""
}

# --- VIEW A SELECT MENU PRO VÝBĚR HŮLKY ---
# --- VIEW A SELECT MENU PRO VÝBĚR HŮLKY ---
class WandSelect(discord.ui.Select):
    def __init__(self):
        options = []
        # Discord Select Menu má limit 25 možností, takže 15 hůlek se vejde do jednoho.
        for wand_id, wand in WANDS_DATA.items():
            options.append(discord.SelectOption(
                label=wand["name"],
                value=wand_id,
                description=f"{wand['wood']}, {wand['core']}, {wand['length']}",
                emoji="🪄"
            ))
        
        # PŘIDÁNO custom_id: Klíčové pro persistentní (trvalé) fungování po restartu
        super().__init__(
            placeholder='Vyber si svou hůlku...', 
            min_values=1, 
            max_values=1, 
            options=options,
            custom_id="persistent_wand_select" 
        )

    async def callback(self, interaction: discord.Interaction):
        wand_id = self.values[0]
        wand = WANDS_DATA[wand_id]
        role_name = WAND_ROLES[wand_id]
        
        # 1. Soukromá zpráva s detailem hůlky (Embed)
        embed_dm = discord.Embed(
            title=f"🪄 HŮLKA SI TĚ VYBRALA!",
            description=(
                f"Když jsi hůlku uchopil, pocítil jsi teplé mravenčení. Pan Ollivander se usmál a přikývl.\n\n"
                f"**Název:** {wand['name']}\n"
                f"**Dřevo:** {wand['wood']}\n"
                f"**Jádro:** {wand['core']}\n"
                f"**Délka:** {wand['length']}\n\n"
                f"*{wand['desc']}*"
            ),
            color=0xFFD700 # Zlatá
        )
        embed_dm.set_image(url=wand['img'])
        embed_dm.set_footer(text="Ollivanderovy hůlky - Příčná ulice")
        
        # 2. Přidělení role
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role:
            try:
                # Odebrání starých rolí hůlek (pokud nějaké má)
                all_wand_role_names = list(WAND_ROLES.values())
                roles_to_remove = [r for r in interaction.user.roles if r.name in all_wand_role_names]
                
                if roles_to_remove:
                    await interaction.user.remove_roles(*roles_to_remove)
                
                # Přidání nové role
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"✅ Hůlka **{wand['name']}** se stala tvým nástrojem! (Detaily máš v SZ)", ephemeral=True)
                
                # Pokus o zaslání SZ (může selhat, pokud má uživatel zavřené SZ)
                try:
                    await interaction.user.send(embed=embed_dm)
                except discord.Forbidden:
                    pass 
            except discord.Forbidden:
                await interaction.response.send_message("❌ Nemám oprávnění spravovat role. Moje role musí být v seznamu výše než role hůlek!", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Role `{role_name}` nebyla na serveru nalezena. Vytvoř ji prosím se stejným názvem.", ephemeral=True)

class WandView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Timeout=None je nutný pro trvalá menu
        self.add_item(WandSelect())

# --- PŘÍKAZ PRO SETUP OBCHODU ---
@bot.tree.command(name="setup_ollivander", description="Vytvoří majestátní obchod s hůlkami (Pouze Admin).")
@app_commands.default_permissions(administrator=True)
async def setup_ollivander(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🪄 OLLIVANDEROVY HŮLKY - PŘÍČNÁ ULICE",
        description=(
            "Vítejte, mladý kouzelníku. Vstupte do tichého obchodu, kde tisíce krabic "
            "čekají na své majitele. Jak pravil pan Ollivander: *„Hůlka si vybírá kouzelníka.“*\n\n"
            "Zde je výběr těch nejvzácnějších kousků, které jsou momentálně k dispozici. "
            "Uchopte tu, která k vám promlouvá, a staňte se jejím mistrem."
        ),
        color=0x4b0082 # Temně fialová
    )
    embed.set_image(url=IMG_WAND_GROUP)
    embed.set_footer(text="Garrick Ollivander, Výrobce hůlek od roku 382 př. n. l.")
    
    # Používáme persistentní view
    await interaction.channel.send(embed=embed, view=WandView())
    await interaction.response.send_message("✅ Obchod byl úspěšně nastaven.", ephemeral=True)

@bot.tree.command(name="vytvor_role_hulek", description="Automaticky vytvoří všech 15 rolí pro hůlky (Pouze Admin).")
@app_commands.default_permissions(administrator=True)
async def vytvor_role_hulek(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True) # Botovi to chvíli potrvá
    
    vytvoreno = 0
    existuje = 0
    
    # Projdeme seznam rolí z tvé konfigurace WAND_ROLES
    for wand_id, role_name in WAND_ROLES.items():
        # Zkontrolujeme, zda už role neexistuje
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        
        if role is None:
            # Vytvoříme novou roli
            # Nastavujeme barvu na šedou a vypínáme oddělené zobrazení v seznamu členů
            await interaction.guild.create_role(
                name=role_name, 
                colour=discord.Colour.light_gray(),
                mentionable=False,
                reason="Automatické vytvoření rolí pro Ollivanderův obchod"
            )
            vytvoreno += 1
        else:
            existuje += 1
            
    await interaction.followup.send(
        f"✅ Hotovo! Vytvořeno nových rolí: **{vytvoreno}**. Již existovalo: **{existuje}**.\n\n"
        f"⚠️ **DŮLEŽITÉ:** Jdi do nastavení serveru a posuň roli mého bota (Wizard Bot) **NAD** tyto nově vytvořené role, jinak je nebudu moci přidělovat!"
    )

@bot.tree.command(name="dennik", description="Publikuje článek do Denního Věštce.")
@app_commands.default_permissions(administrator=True)
@discord.app_commands.describe(text="Obsah článku, který chceš publikovat")
async def dennik(interaction: discord.Interaction, text: str):
    # Formátování textu - nahradíme zástupný text tvým skutečným textem
    # Používáme f-string pro vložení proměnné 'text'
    popis_clanku = (
        "*„Pouze pravda, která je schválena Ministerstvem.“*\n"
        "### ⚡ NEJNOVĚJŠÍ UDÁLOSTI Z HOGWARTS VITALIS\n\n"
        f"> {text}"
    )

    embed = discord.Embed(
        title="🗞️ DENNÍ VĚŠTEC | MIMOŘÁDNÉ VYDÁNÍ",
        description=popis_clanku,
        color=0xf5f5dc # Barva pergamenu
    )
    
    embed.set_author(name="Gwenog Jonesová, šéfredaktorka")
    
    # Tvé vygenerované logo pro Hogwarts Vitalis
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1487590069471674480/1487901051733545102/Gemini_Generated_Image_7e5y987e5y987e5y.png?ex=69cad356&is=69c981d6&hm=9cebb966eb612119677e8fea1d118a74c6bd0333de5e70300bb46b5199577264&")
    
    embed.set_footer(text="Hogwarts Vitalis - Ministerstvo kouzel varuje.")

    # Odeslání do kanálu, kde byl příkaz použit
    await interaction.channel.send(embed=embed)
    
    # Potvrzení pro tebe (uvidíš ho jen ty, aby to nerušilo noviny)
    await interaction.response.send_message("✅ Článek byl úspěšně publikován v Denním Věštci.", ephemeral=True)

import discord
from discord.ext import commands
import random  # <--- OPRAVA 1: Přidán import pro náhodný výběr při remíze

# --- KONFIGURACE OBRÁZKŮ (Ponechány tvé URL) ---
IMG_PATRON_STAG = "https://cdn.discordapp.com/attachments/1487590069471674480/1487904048580399306/Gemini_Generated_Image_hlczguhlczguhlcz.png?ex=69cad621&is=69c984a1&hm=92c99e79247ceeea1ee950729366902261df76d16abcf23c8c04e4491a73129d&"
IMG_PATRON_DOE = "https://cdn.discordapp.com/attachments/1487590069471674480/1487904047728951327/Gemini_Generated_Image_hlczguhlczguhlcz1.png?ex=69cad620&is=69c984a0&hm=d042839292dd303e87db0b33b9de725cdd9f7c8d271f12678049776ac182ef4f&"
IMG_PATRON_OTTER = "https://cdn.discordapp.com/attachments/1487590069471674480/1487904046860992763/Gemini_Generated_Image_hlczguhlczguhlcz2.png?ex=69cad620&is=69c984a0&hm=ea33767eefba7258e6a562da73cf228fdae5b4682264868a108bdd4e6c01a5b0&"
IMG_PATRON_TERRIER = "https://cdn.discordapp.com/attachments/1487590069471674480/1487904051428458766/Gemini_Generated_Image_hlczguhlczguhlcz3.png?ex=69cad621&is=69c984a1&hm=0781c9b9643fa9516986211a9e3d17b4ecabf226ea39c232ea2c8be7e6fd78ba&"
IMG_PATRON_WOLF = "https://cdn.discordapp.com/attachments/1487590069471674480/1487904050744918220/Gemini_Generated_Image_hlczguhlczguhlcz4.png?ex=69cad621&is=69c984a1&hm=28940dcdb2bf2a5283ebd48584e05cca7ebd7e42b2cfef854dd81fdbdbc29db8&"
IMG_PATRON_PHOENIX = "https://cdn.discordapp.com/attachments/1487590069471674480/1487904050015113226/Gemini_Generated_Image_hlczguhlczguhlcz5.png?ex=69cad621&is=69c984a1&hm=6f6afa760944c070754cc10ef193cf0aa7541707152aa37e2d6f900bb2769539&"
IMG_PATRON_GROUP = "https://cdn.discordapp.com/attachments/1487590069471674480/1487904049322786917/Gemini_Generated_Image_hlczguhlczguhlcz6.png?ex=69cad621&is=69c984a1&hm=5982ee919a7005b77ebf115c7826b2c4a9581c0ff22c7ab003847ded6128cef5&"

PATRON_DATA = {
    "patron_01": {"name": "Jelen", "desc": "Znak rozeného vůdce, odvahy a hrdosti. Majitelé tohoto patrona chrání ostatní i za cenu vlastního bezpečí.", "img": IMG_PATRON_STAG},
    "patron_02": {"name": "Laň", "desc": "Symbol něhy, hluboké lásky a oddanosti. Majitel je empatický, klidný a nesmírně pečující.", "img": IMG_PATRON_DOE},
    "patron_03": {"name": "Vydra", "desc": "Chytrá, hravá a zvědavá. Lidé s tímto patronem jsou nezávislí, inteligentní a nenechají se jen tak spoutat.", "img": IMG_PATRON_OTTER},
    "patron_04": {"name": "Jack Russell teriér", "desc": "Tvrdohlavý, věrný a neústupný. Chrání své přátele do posledního dechu a necouvne před žádnou výzvou.", "img": IMG_PATRON_TERRIER},
    "patron_05": {"name": "Vlk", "desc": "Silně rodinně založený, ochranářský a divoký. Spoléhá na svou smečku, ale má i svou tajemnou stránku.", "img": IMG_PATRON_WOLF},
    "patron_06": {"name": "Fénix", "desc": "Mimořádně vzácný patron. Značí obrovskou vnitřní sílu, moudrost a schopnost povstat z popela po těžkých ranách.", "img": IMG_PATRON_PHOENIX}
}

PATRON_ROLES = {
    "patron_01": "Patron: Jelen", "patron_02": "Patron: Laň", "patron_03": "Patron: Vydra",
    "patron_04": "Patron: Teriér", "patron_05": "Patron: Vlk", "patron_06": "Patron: Fénix"
}

QUIZ_QUESTIONS = [
    {
        "text": "1. K tobě a tvým přátelům se blíží Mozkomor. Tvá první reakce?",
        "options": [
            {"label": "Postavím se do čela a odlákám pozornost.", "value": "A", "boosts": ["patron_01"]}, 
            {"label": "Zůstanu klidný a soustředím se na lásku k nim.", "value": "B", "boosts": ["patron_06", "patron_02"]}, 
            {"label": "Bleskově analyzuji únikovou cestu.", "value": "C", "boosts": ["patron_03"]}, 
            {"label": "S divokým odhodláním zaútočím.", "value": "D", "boosts": ["patron_05", "patron_04"]} 
        ]
    },
    {
        "text": "2. Co bys viděl v Zrcadle z Erisedu?",
        "options": [
            {"label": "Svou rodinu a přátele v naprostém bezpečí.", "value": "A", "boosts": ["patron_05", "patron_02"]}, 
            {"label": "Sebe, jak vedu ostatní k lepším zítřkům.", "value": "B", "boosts": ["patron_01"]}, 
            {"label": "Nekonečnou svobodu a objevování neznámého.", "value": "C", "boosts": ["patron_03"]}, 
            {"label": "Světlo prolomené skrze nejhlubší temnotu.", "value": "D", "boosts": ["patron_06"]} 
        ]
    },
    {
        "text": "3. Kouzlo Expecto Patronum vyžaduje vzpomínku. Kterou zvolíš?",
        "options": [
            {"label": "Chvíli, kdy jsem překonal svůj největší strach.", "value": "A", "boosts": ["patron_06", "patron_04"]}, 
            {"label": "Tichý, obyčejný večer s těmi, které miluji.", "value": "B", "boosts": ["patron_02", "patron_05"]}, 
            {"label": "Okamžik absolutního triumfu a uznání.", "value": "C", "boosts": ["patron_01"]}, 
            {"label": "Moment, kdy jsem se cítil naprosto svobodný.", "value": "D", "boosts": ["patron_03"]} 
        ]
    },
    {
        "text": "4. Zjistíš, že tě zradil někdo blízký. Jak se zachováš?",
        "options": [
            {"label": "Okamžitě ho konfrontuji, zrada se neodpouští.", "value": "A", "boosts": ["patron_04", "patron_01"]}, 
            {"label": "Stáhnu se do sebe a řeším to se svou 'smečkou'.", "value": "B", "boosts": ["patron_05"]}, 
            {"label": "Zkusím pochopit důvody a najít cestu k odpuštění.", "value": "C", "boosts": ["patron_06", "patron_02"]}, 
            {"label": "Smažu ho ze svého života a jdu dál.", "value": "D", "boosts": ["patron_03"]} 
        ]
    },
    {
        "text": "5. Co je podle tebe skutečnou podstatou magie?",
        "options": [
            {"label": "Síla ochránit ty, kteří to sami nedokážou.", "value": "A", "boosts": ["patron_01", "patron_04"]}, 
            {"label": "Pouto, které spojuje všechno živé.", "value": "B", "boosts": ["patron_02", "patron_05"]}, 
            {"label": "Nástroj k překonávání limitů a pravidel.", "value": "C", "boosts": ["patron_03"]}, 
            {"label": "Koloběh zániku a znovuzrození duše.", "value": "D", "boosts": ["patron_06"]} 
        ]
    }
]

class QuizView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=300)
        self.user = user
        self.current_q = 0
        self.scores = {p_id: 0 for p_id in PATRON_DATA.keys()}
        self.update_select()

    def update_select(self):
        self.clear_items()
        if self.current_q >= len(QUIZ_QUESTIONS):
            return

        question = QUIZ_QUESTIONS[self.current_q]
        options = [discord.SelectOption(label=opt["label"], value=opt["value"]) for opt in question["options"]]
        select = discord.ui.Select(placeholder=f"Otázka {self.current_q + 1} z 5...", options=options)
        
        async def select_callback(interaction: discord.Interaction):
            if interaction.user != self.user:
                return await interaction.response.send_message("Tohle není tvůj test!", ephemeral=True)
            
            # OPRAVA 2: Uložení odpovědi dříve, než se inkrementuje index
            selected_val = select.values[0]
            current_question_data = QUIZ_QUESTIONS[self.current_q]
            
            for opt in current_question_data["options"]:
                if opt["value"] == selected_val:
                    for boost in opt["boosts"]:
                        self.scores[boost] += 1
            
            self.current_q += 1
            
            if self.current_q < len(QUIZ_QUESTIONS):
                self.update_select()
                embed = discord.Embed(
                    title="✨ Testování tvé podstaty", 
                    description=f"### {QUIZ_QUESTIONS[self.current_q]['text']}", 
                    color=0xADD8E6
                )
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                await self.finish_quiz(interaction)
                
        select.callback = select_callback
        self.add_item(select)

    async def finish_quiz(self, interaction: discord.Interaction):
        # Fénixova bariéra (potřeba 4 body pro patron_06)
        if self.scores["patron_06"] >= 4:
            winner_id = "patron_06"
        else:
            temp_scores = self.scores.copy()
            temp_scores["patron_06"] = 0 
            max_val = max(temp_scores.values())
            winners = [p_id for p_id, s in temp_scores.items() if s == max_val]
            winner_id = random.choice(winners) # Teď už random funguje

        patron = PATRON_DATA[winner_id]
        role_name = PATRON_ROLES[winner_id]
        
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role:
            all_patron_roles = [discord.utils.get(interaction.guild.roles, name=r) for r in PATRON_ROLES.values()]
            await interaction.user.remove_roles(*[r for r in all_patron_roles if r and r in interaction.user.roles])
            await interaction.user.add_roles(role)

        embed_res = discord.Embed(
            title="✨ EXPECTO PATRONUM!",
            description=f"Hůlka se zachvěla a z jejího konce vytryskl jasný stříbrný proud...\n\nTvým ochráncem se stává: **{patron['name']}**\n\n*{patron['desc']}*",
            color=0xADD8E6
        )
        embed_res.set_image(url=patron['img'])
        await interaction.response.edit_message(embed=embed_res, view=None)

class StartQuizView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Vyvolat svého Patrona", style=discord.ButtonStyle.secondary, emoji="🪄")
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = QuizView(interaction.user)
        embed = discord.Embed(title="✨ Testování tvé podstaty", description=f"### {QUIZ_QUESTIONS[0]['text']}", color=0xADD8E6)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="setup_patron", description="Vytvoří startovací zprávu pro test Patrona.")
@app_commands.default_permissions(administrator=True)
async def setup_patron(interaction: discord.Interaction):
    embed = discord.Embed(
        title="✨ ODBOR ZÁHAD: SÍŇ PATRONŮ",
        description="Soustřeď se na svou nejsilnější vzpomínku a prokaž svou čistou podstatu v testu pěti otázek.",
        color=0xADD8E6
    )
    embed.set_image(url=IMG_PATRON_GROUP)
    await interaction.channel.send(embed=embed, view=StartQuizView())
    await interaction.response.send_message("✅ Síň Patronů připravena.", ephemeral=True)

@bot.tree.command(name="vytvor_role_patronu", description="Automaticky vytvoří role pro Patrony.")
@app_commands.default_permissions(administrator=True)
async def vytvor_role_patronu(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    for role_name in PATRON_ROLES.values():
        if not discord.utils.get(interaction.guild.roles, name=role_name):
            await interaction.guild.create_role(name=role_name, colour=discord.Colour.from_rgb(173, 216, 230))
    await interaction.followup.send("✅ Role byly vytvořeny.")

@bot.tree.command(name="patron", description="Ukaž svého Patrona ostatním.")
async def patron_cmd(interaction: discord.Interaction):
    user_p_id = None
    for p_id, r_name in PATRON_ROLES.items():
        if discord.utils.get(interaction.user.roles, name=r_name):
            user_p_id = p_id
            break
    if not user_p_id:
        return await interaction.response.send_message("❌ Ještě nemáš Patrona!", ephemeral=True)
    
    p = PATRON_DATA[user_p_id]
    embed = discord.Embed(title=f"✨ Patron čaroděje {interaction.user.display_name}", description=f"***„Expecto Patronum!“***\n\nZ hůlky vyběhl: **{p['name']}**.\n\n*{p['desc']}*", color=0xADD8E6)
    embed.set_image(url=p['img'])
    await interaction.response.send_message(embed=embed)

# ========== SYSTÉM CUSTOMIZACE POSTAVY ==========

class NameModal(discord.ui.Modal, title='Základní info o postavě'):
    char_name = discord.ui.TextInput(
        label='Jméno a příjmení postavy',
        style=discord.TextStyle.short,
        placeholder='Např. Cedric Diggory',
        required=True,
        max_length=50
    )
    age = discord.ui.TextInput(
        label='Věk postavy',
        style=discord.TextStyle.short,
        placeholder='Např. 15',
        required=True,
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):
        player = get_player(interaction)
        # Uložení do tvého Player objektu
        player.name = self.char_name.value
        player.age = self.age.value
        player_db.save() # Uložení do tvé DB
        await interaction.response.send_message(f"✅ Identita uložena: **{player.name}** (Věk: {player.age}). Zkus znovu `/postava` pro zobrazení.", ephemeral=True)

class BioModal(discord.ui.Modal, title='Příběh a Vlastnosti'):
    bio = discord.ui.TextInput(
        label='Krátký popisek (Lore)',
        style=discord.TextStyle.paragraph,
        placeholder='Odkud postava pochází? Jaká je její historie?',
        required=False,
        max_length=1000
    )
    traits = discord.ui.TextInput(
        label='Vlastnosti a zájmy',
        style=discord.TextStyle.paragraph,
        placeholder='Např. Odvážný, miluje famfrpál, bojí se pavouků...',
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        player = get_player(interaction)
        player.bio = self.bio.value
        player.traits = self.traits.value
        player_db.save()
        await interaction.response.send_message("✅ Příběh a vlastnosti byly uloženy do kanálů Ministerstva. Zkus znovu `/postava`.", ephemeral=True)

class PhotoModal(discord.ui.Modal, title='Vzhled postavy'):
    photo_url = discord.ui.TextInput(
        label='URL odkaz na obrázek',
        style=discord.TextStyle.short,
        placeholder='https://cdn.discordapp.com/avatars/1224452995442540647/9c1ca1ed3858644f0dcf0ef17251fc4b.jpg?size=1024',
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        player = get_player(interaction)
        if not self.photo_url.value.startswith(("http://", "https://")):
            await interaction.response.send_message("❌ Neplatný odkaz! Musí začínat na http:// nebo https://", ephemeral=True)
            return
        
        player.photo_url = self.photo_url.value
        player_db.save()
        await interaction.response.send_message("✅ Vizuální podoba aktualizována! Zkus znovu `/postava`.", ephemeral=True)


class CharacterSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Tlačítka nevyprší

    @discord.ui.button(label="Jméno a Věk", style=discord.ButtonStyle.primary, emoji="📝", custom_id="char_name_btn")
    async def btn_name(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NameModal())

    @discord.ui.button(label="Příběh (Lore)", style=discord.ButtonStyle.secondary, emoji="📖", custom_id="char_bio_btn")
    async def btn_bio(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BioModal())

    @discord.ui.button(label="Změnit Fotku", style=discord.ButtonStyle.success, emoji="🖼️", custom_id="char_photo_btn")
    async def btn_photo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PhotoModal())

# --- HLAVNÍ SLASH PŘÍKAZ PRO POSTAVU ---

@bot.tree.command(name="postava", description="Prohlédni si nebo si nastav svou RPG postavu")
async def character_profile(interaction: discord.Interaction):
    """Zobrazí a umožní editaci postavy hráče"""
    player = get_player(interaction)
    
    # Bezpečné načtení dat (pokud si hráč ještě něco nenastavil, použijeme zástupné texty)
    p_name = getattr(player, 'name', interaction.user.display_name)
    p_age = getattr(player, 'age', '??')
    p_bio = getattr(player, 'bio', '*Tento kouzelník je zahalen tajemstvím... Klikni na tlačítko a napiš svůj příběh!*')
    p_traits = getattr(player, 'traits', '*Nenastaveno*')
    p_photo = getattr(player, 'photo_url', None)

    # Vytvoření nádherného Embedu
    embed = discord.Embed(
        title=f"🧙‍♂️ Osobní složka: {p_name}",
        color=0xFFD700 # Zlatá barva
    )
    
    embed.add_field(name="Věk", value=p_age, inline=True)
    embed.add_field(name="Reputace", value=f"{player.reputation}", inline=True)
    embed.add_field(name="Souboje", value=f"Vyhráno: {player.duels_won} / Celkem: {player.total_duels}", inline=True)
    
    # Pouze pokud není bio prázdné
    if not p_bio: p_bio = "*Tajemný kouzelník...*"
    embed.add_field(name="📖 Příběh (Lore)", value=p_bio, inline=False)
    
    if not p_traits: p_traits = "*Nenastaveno*"
    embed.add_field(name="🎭 Vlastnosti a Zájmy", value=p_traits, inline=False)
    
    # Miniatura a fotka
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    if p_photo:
        embed.set_image(url=p_photo)
    else:
        # Defaultní pečeť, pokud nemá fotku
        embed.set_image(url=IMG_URL)
        
    embed.set_footer(text="Ministerstvo Kouzel | Hogwarts Vitalis RPG")

    # Poslání jako ephemeral = uvidí to jen ten hráč
    await interaction.response.send_message(embed=embed, view=CharacterSetupView(), ephemeral=True)







# --- VIEW PRO LISTOVÁNÍ MAZLÍČKY (GALLERY) ---

class PetGalleryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Timeout None pro perzistenci
        self.current_pet = 0 

    def create_embed(self):
        pet = PET_ADOPTION_DATA[self.current_pet]
        embed = discord.Embed(
            title=f"🐈 Mžouralův zvěřinec: {pet['name']}",
            description=f"{pet['emoji']} *{pet['desc']}*",
            color=0xADD8E6
        )
        embed.set_image(url=pet['img'])
        embed.set_footer(text=f"Zvíře {self.current_pet + 1} z {len(PET_ADOPTION_DATA)} | Prohlédni si nabídku a zvol srdcem")
        return embed

    @discord.ui.button(label="◀ Předchozí", style=discord.ButtonStyle.gray, custom_id="pet_gallery_prev")
    async def previous_pet(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_pet = (self.current_pet - 1) % len(PET_ADOPTION_DATA)
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Zvolit tohoto mazlíčka", style=discord.ButtonStyle.success, emoji="💖", custom_id="pet_gallery_choose")
    async def choose_pet(self, interaction: discord.Interaction, button: discord.ui.Button):
        pet = PET_ADOPTION_DATA[self.current_pet]
        guild = interaction.guild
        role_name = pet['role']
        
        # Získání/Vytvoření role
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            role = await guild.create_role(name=role_name, colour=discord.Colour.orange())

        # Odebrání ostatních rolí mazlíčků
        all_pet_role_names = [p['role'] for p in PET_ADOPTION_DATA]
        roles_to_remove = [r for r in interaction.user.roles if r.name in all_pet_role_names]
        if roles_to_remove:
            await interaction.user.remove_roles(*roles_to_remove)

        await interaction.user.add_roles(role)
        
        # Uložení do DB
        player = get_player(interaction)
        player.pet = pet['id']
        player_db.save()

        await interaction.response.send_message(f"💖 Gratuluji! Tvým mazlíčkem je nyní **{pet['name']}** a získal/a jsi roli `{role_name}`.", ephemeral=True)

    @discord.ui.button(label="Další ▶", style=discord.ButtonStyle.secondary, custom_id="pet_gallery_next")
    async def next_pet(self, interaction: discord.Interaction, button: discord.ui.Button):
        # OPRAVA: Tady už není 'embed', ale volání funkce
        self.current_pet = (self.current_pet + 1) % len(PET_ADOPTION_DATA)
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

# --- HLAVNÍ SLASH PŘÍKAZ PRO ZVĚŘINEC ---

@bot.tree.command(name="zverinec", description="Otevře galerii pro výběr mazlíčka.")
async def pet_adoption(interaction: discord.Interaction):
    view = PetGalleryView()
    # Posíláme veřejně (ephemeral=False), aby to v kanálu zůstalo pro všechny
    await interaction.response.send_message(embed=view.create_embed(), view=view)


@bot.tree.command(name="uvitat", description="Slavnostní uvítání studenta do koleje (Brumbál)")
@app_commands.describe(
    student="Student, kterého vítáme",
    kolej="Do které koleje se dostal?"
)
@app_commands.choices(kolej=[
    app_commands.Choice(name="Nebelvír 🦁", value="Nebelvíru"),
    app_commands.Choice(name="Zmijozel 🐍", value="Zmijozelu"),
    app_commands.Choice(name="Havraspár 🦅", value="Havraspáru"),
    app_commands.Choice(name="Mrzimor 🦡", value="Mrzimoru"),
])
async def welcome_student(interaction: discord.Interaction, student: discord.Member, kolej: app_commands.Choice[str]):
    """Pošle RP zprávu od Brumbála do Velké síně"""
    
    # Nastavení barev a ikon podle koleje
    kolej_data = {
        "Nebelvíru": {"color": discord.Color.red(), "emoji": "🦁"},
        "Zmijozelu": {"color": discord.Color.green(), "emoji": "🐍"},
        "Havraspáru": {"color": discord.Color.blue(), "emoji": "🦅"},
        "Mrzimoru": {"color": discord.Color.gold(), "emoji": "🦡"},
    }
    
    data = kolej_data.get(kolej.value)
    
    embed = discord.Embed(
        title="✨ PROHLÁŠENÍ ŘEDITELE ŠKOLY ✨",
        description=(
            f"**„Věnujte mi pozornost!“**\n\n"
            f"S velkou radostí oznamuji, že Moudrý klobouk právě rozhodl! "
            f"Náš nový student, {student.mention}, prokázal přesně ty vlastnosti, "
            f"které zdobí zakladatele jedné z našich slavných kolejí.\n\n"
            f"Nechť se celá Velká síň otřese potleskem, neboť vítáme nového člena v...\n"
            f"## {data['emoji']} **{kolej.name.upper()}** {data['emoji']}\n\n"
            f"*{student.display_name}, věřím, že tvá cesta v {kolej.value} bude plná úspěchů a tvá kolej na tebe bude hrdá. "
            f"Nyní se připoj ke svým spolužákům u stolu a hodujme!* 🥂"
        ),
        color=data['color']
    )
    
    # Přidáme obrázek Brumbála nebo Bradavic pro atmosféru
    embed.set_thumbnail(url="https://i.imgur.com/K1LAn1U.png") # Můžeš nahradit vlastním linkem na Brumbála
    embed.set_footer(text="Albus Persival Wulfric Brian Brumbál, Ředitel školy")
    
    # Pošleme zprávu všem (ne jen studentovi)
    await interaction.response.send_message(content=f"🔔 {student.mention} právě dorazil do Bradavic!", embed=embed)


# ========== NEPORUŠITELNÝ SLIB ==========

@bot.tree.command(name="neporusitelny_slib", description="Vytvořit Neporušitelný Slib (vyžaduje 3 hráče)")
@app_commands.describe(
    prisahajici="Hráč, který přísahá (ZEMŘE při porušení)",
    prijemce="Hráč, kterému se přísahá",
    svedek="Hráč provádějící rituál (musí mít hůlku)",
    text_slibu="Přesný text slibu (např: 'Přísahám, že ochráním Draca')",
    podminky="Podmínky oddělené čárkami (např: never_harm:Draco,always_protect:Harry)"
)
async def create_unbreakable_vow(
    interaction: discord.Interaction,
    prisahajici: discord.Member,
    prijemce: discord.Member,
    svedek: discord.Member,
    text_slibu: str,
    podminky: str
):
    """
    Vytvoří Neporušitelný Slib mezi třemi hráči
    
    DŮLEŽITÉ: Toto není bojové kouzlo! Je to magický rituál.
    
    Typy podmínek:
    - never_harm:jméno - Nikdy neublížit
    - always_protect:jméno - Vždy chránit
    - never_reveal:tajemství - Nikdy neprozradit
    - complete_task:úkol - Dokončit úkol
    - never_use_spell:spell_id - Nikdy nepoužít kouzlo
    """
    
    # Získat hráče z databáze
    vow_maker_data = player_db.get_player(prisahajici.id)
    vow_recipient_data = player_db.get_player(prijemce.id)
    binder_data = player_db.get_player(svedek.id)
    
    if not vow_maker_data:
        return await interaction.response.send_message(
            f"❌ {prisahajici.mention} neexistuje v databázi! Musí se nejdřív zaregistrovat.",
            ephemeral=True
        )
    
    if not vow_recipient_data:
        return await interaction.response.send_message(
            f"❌ {prijemce.mention} neexistuje v databázi! Musí se nejdřív zaregistrovat.",
            ephemeral=True
        )
    
    if not binder_data:
        return await interaction.response.send_message(
            f"❌ {svedek.mention} neexistuje v databázi! Musí se nejdřív zaregistrovat.",
            ephemeral=True
        )
    
    # Vytvořit Player objekty - handle both Player objects and dicts
    vow_maker = vow_maker_data if isinstance(vow_maker_data, Player) else Player.from_dict(vow_maker_data)
    vow_recipient = vow_recipient_data if isinstance(vow_recipient_data, Player) else Player.from_dict(vow_recipient_data)
    binder = binder_data if isinstance(binder_data, Player) else Player.from_dict(binder_data)
    
    # Rozdělit podmínky
    conditions_list = [c.strip() for c in podminky.split(',') if c.strip()]
    
    if not conditions_list:
        return await interaction.response.send_message(
            "❌ Musíš zadat alespoň jednu podmínku!",
            ephemeral=True
        )
    
    # Vytvořit slib
    success, message, vow = combat_engine.create_unbreakable_vow(
        vow_maker=vow_maker,
        vow_recipient=vow_recipient,
        binder=binder,
        vow_text=text_slibu,
        conditions=conditions_list
    )
    
    if success:
        # Vytvoř embed
        embed = discord.Embed(
            title="✨🔗 NEPORUŠITELNÝ SLIB UZAVŘEN 🔗✨",
            description=message,
            color=discord.Color.dark_red()
        )
        
        embed.add_field(
            name="⚠️ VAROVÁNÍ",
            value=(
                f"**{prisahajici.mention} je nyní vázán Neporušitelným slibem!**\n\n"
                f"Porušení **jakékoliv** podmínky způsobí **okamžitou smrt**!\n"
                f"Slib **nelze zrušit** - pouze smrt může ukončit závazek."
            ),
            inline=False
        )
        
        embed.set_footer(text="💀 Neporušitelný Slib je permanentní a nezrušitelný!")
        
        await interaction.response.send_message(embed=embed)
        
        # Ulož změny do databáze
        player_db.save_player(prisahajici.id, vow_maker.to_dict())
        player_db.save_player(prijemce.id, vow_recipient.to_dict())
        player_db.save_player(svedek.id, binder.to_dict())
        
        # Log
        if combat_logger:
            combat_logger.log_event(
                event_type="unbreakable_vow_created",
                data={
                    "vow_id": vow.vow_id,
                    "vow_maker": vow_maker.name,
                    "vow_recipient": vow_recipient.name,
                    "binder": binder.name,
                    "conditions": conditions_list
                }
            )
    else:
        await interaction.response.send_message(
            f"❌ **Selhání rituálu:**\n{message}",
            ephemeral=True
        )


@bot.tree.command(name="moje_sliby", description="Zobrazí všechny tvoje aktivní Neporušitelné sliby")
async def show_my_vows(interaction: discord.Interaction):
    """Zobrazí všechny aktivní Neporušitelné sliby pro hráče"""
    
    player_data = player_db.get_player(interaction.user.id)
    if not player_data:
        return await interaction.response.send_message(
            "❌ Nejsi zaregistrován v databázi!",
            ephemeral=True
        )
    
    # Handle both Player objects and dicts
    if isinstance(player_data, Player):
        player = player_data
    else:
        player = Player.from_dict(player_data)
    
    # Získat sliby
    vows = combat_engine.get_player_vows(player)
    
    if not vows:
        embed = discord.Embed(
            title="📜 Tvoje Neporušitelné sliby",
            description="Nemáš žádné aktivní Neporušitelné sliby.",
            color=discord.Color.green()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Vytvoř embed
    embed = discord.Embed(
        title=f"📜 Tvoje Neporušitelné sliby ({len(vows)})",
        description=f"**{interaction.user.display_name}**, zde jsou tvoje aktivní sliby:",
        color=discord.Color.dark_red()
    )
    
    for i, vow in enumerate(vows, 1):
        role = ""
        if vow.vow_maker == player:
            role = "🔴 **PŘÍSAHAJÍCÍ** (ty zemřeš při porušení!)"
        elif vow.vow_recipient == player:
            role = "🟢 **PŘÍJEMCE** (někdo ti přísahá)"
        elif vow.binder == player:
            role = "🟡 **SVĚDEK** (ty jsi slib spojil/a)"
        
        conditions_text = "\n".join([f"• {combat_engine._format_condition(c)}" for c in vow.conditions])
        
        embed.add_field(
            name=f"📜 Slib #{i} {role}",
            value=(
                f"**Text:** {vow.vow_text}\n"
                f"**Přísahající:** {vow.vow_maker.name}\n"
                f"**Příjemce:** {vow.vow_recipient.name}\n"
                f"**Svědek:** {vow.binder.name}\n"
                f"**Podmínky:**\n{conditions_text}\n"
                f"**Aktivní:** {'✅ Ano' if vow.is_active else '❌ Ne'}"
            ),
            inline=False
        )
    
    embed.set_footer(text="💀 Neporušitelné sliby jsou permanentní!")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ========== RUN BOT ==========

if __name__ == "__main__":
    print("🚀 Spouštím bota...")
    print(f"📋 Token nastaven: {'✅' if TOKEN != 'YOUR_TOKEN_HERE' else '❌'}")
    
    if TOKEN == 'YOUR_TOKEN_HERE':
        print("\n⚠️  CHYBA: Nastavte DISCORD_BOT_TOKEN v environment variables!")
        print("Příklad:")
        print("  export DISCORD_BOT_TOKEN='your_token_here'")
        print("  python bot.py")
        exit(1)
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("\n❌ CHYBA: Neplatný Discord token!")
    except Exception as e:
        print(f"\n❌ CHYBA: {e}")