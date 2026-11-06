"""
World Commands - Discord slash příkazy pro open world systém
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import time
import asyncio


async def setup_world_commands(bot: commands.Bot):
    """Registruje všechny world příkazy"""
    
    # Import manažerů (měly by být už v botu)
    if not hasattr(bot, 'world_manager'):
        print("⚠️ WorldManager není inicializován!")
        return
    
    if not hasattr(bot, 'economy_manager'):
        print("⚠️ EconomyManager není inicializován!")
        return
    
    world_manager = bot.world_manager
    economy_manager = bot.economy_manager
    player_db = bot.player_db
    
    
    # ========== NAVIGATION COMMANDS ==========
    
    @bot.tree.command(name="map", description="🗺️ Zobraz mapu světa")
    async def map_command(interaction: discord.Interaction):
        """Zobrazí mapu světa"""
        map_text = world_manager.get_map_overview()
        
        embed = discord.Embed(
            title="🗺️ Mapa Čarodějnického Světa",
            description=map_text,
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📖 Legenda",
            value=(
                "🛡️ Safe Zone - Žádné PvP\n"
                "⚠️ Consensual - PvP se souhlasem\n"
                "⚔️ Open PvP - Kdokoliv může zaútočit!\n"
                "🏪 Obchod | 💚 Léčitel | 🏦 Banka"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    
    @bot.tree.command(name="location", description="📍 Kde jsem?")
    async def location_command(interaction: discord.Interaction):
        """Zobrazí současnou lokaci"""
        player_id = interaction.user.id
        state = world_manager.get_player_state(player_id)
        location = world_manager.get_player_location(player_id)
        
        # Je na cestě?
        if state.traveling:
            destination = world_manager.locations[state.travel_destination]
            time_left = max(0, state.travel_eta - time.time())
            
            embed = discord.Embed(
                title="🚶 Cestuješ...",
                description=(
                    f"Z: **{world_manager.locations[state.last_location].name_cs}**\n"
                    f"Do: **{destination.name_cs}**\n"
                    f"⏱️ Zbývá: {int(time_left/60)}m {int(time_left%60)}s"
                ),
                color=discord.Color.orange()
            )
            
            await interaction.response.send_message(embed=embed)
            return
        
        # Normální lokace
        # PvP zóna
        pvp_text = {
            "safe": "🛡️ **Safe Zone** - Žádné PvP",
            "consensual": "⚠️ **Consensual PvP** - Oba musí mít PvP ON",
            "open": "⚔️ **OPEN PVP** - Kdokoliv může zaútočit!",
            "flagged": "🎯 **Flagged PvP** - Jen na arénách"
        }
        
        embed = discord.Embed(
            title=f"📍 {location.name_cs}",
            description=location.description,
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="⚔️ PvP Pravidla",
            value=pvp_text.get(location.pvp_zone.value, "Neznámé"),
            inline=False
        )
        
        # Hráči v lokaci
        players_here = world_manager.get_players_in_location(location.id)
        if len(players_here) > 1:  # -1 pro sebe
            other_players = [pid for pid in players_here if pid != player_id]
            player_count = len(other_players)
            embed.add_field(
                name=f"👥 Hráči ({player_count})",
                value=f"{player_count} dalších hráčů v lokaci",
                inline=False
            )
        
        # Tábory
        camps = world_manager.get_camps_in_location(location.id)
        if camps:
            camp_list = [f"• {camp.name} ({'veřejný' if camp.public else 'soukromý'})" for camp in camps[:5]]
            embed.add_field(
                name=f"⛺ Tábory ({len(camps)})",
                value="\n".join(camp_list),
                inline=False
            )
        
        # Services
        services = []
        if location.has_shop:
            services.append("🏪 Obchod")
        if location.has_healer:
            services.append("💚 Léčitel")
        if location.has_bank:
            services.append("🏦 Banka")
        
        if services:
            embed.add_field(
                name="🔧 Služby",
                value=" | ".join(services),
                inline=False
            )
        
        # Connections
        connections = list(location.connections.keys())
        if connections:
            conn_names = [world_manager.locations[cid].name_cs for cid in connections[:5]]
            embed.add_field(
                name="🛤️ Můžeš cestovat do",
                value=", ".join(conn_names),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    
    @bot.tree.command(name="travel", description="🚶 Cestuj kamkoliv - i do nových míst!")
    @app_commands.describe(destination="Kam chceš jít? (název místa, 'north', 'south', 'east', 'west')")
    async def travel_command(interaction: discord.Interaction, destination: str):
        """
        🌟 NOVÝ! Podporuje procedurální generování
        Hráč může cestovat kamkoliv - pokud místo neexistuje, vygeneruje se!
        """
        player_id = interaction.user.id
        
        # Zkontroluj jestli už cestuje
        state = world_manager.get_player_state(player_id)
        if state.traveling:
            await interaction.response.send_message(
                "⚠️ Už cestuješ! Počkej než dorazíš.",
                ephemeral=True
            )
            return
        
        # Začni cestování (s procedurálním generováním!)
        success, message, travel_time = world_manager.start_travel(player_id, destination)
        
        if success:
            embed = discord.Embed(
                title="🗺️ Cestování",
                description=message,
                color=discord.Color.green()
            )
            
            # Pokud byla lokace právě vygenerována, přidej info
            dest_id = world_manager.generator.sanitize_location_id(destination)
            if dest_id in world_manager.generated_location_ids:
                embed.set_footer(text="✨ Toto místo bylo právě objeveno!")
            
            await interaction.response.send_message(embed=embed)
            
            # Počkej a notify o příchodu
            await asyncio.sleep(min(travel_time * 60, 5))  # Max 5s wait for demo
            
            # Zkontroluj příchod
            arrived, dest_name = world_manager.check_travel_completion(player_id)
            if arrived:
                try:
                    await interaction.followup.send(
                        f"✅ {interaction.user.mention} Dorazil jsi do **{dest_name}**!"
                    )
                except:
                    pass  # Channel může být deleted
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    
    @bot.tree.command(name="players_nearby", description="👥 Kdo je v lokaci?")
    async def players_nearby_command(interaction: discord.Interaction):
        """Zobrazí hráče v lokaci"""
        player_id = interaction.user.id
        state = world_manager.get_player_state(player_id)
        location = world_manager.get_player_location(player_id)
        
        if state.traveling:
            await interaction.response.send_message(
                "❌ Cestuješ! Nelze vidět hráče.",
                ephemeral=True
            )
            return
        
        # Najdi hráče
        players_here = world_manager.get_players_in_location(location.id)
        other_players = [pid for pid in players_here if pid != player_id]
        
        if not other_players:
            await interaction.response.send_message(
                f"📍 **{location.name_cs}**\n\n"
                "👥 Žádní další hráči v lokaci.",
                ephemeral=True
            )
            return
        
        # Vytvoř seznam
        embed = discord.Embed(
            title=f"👥 Hráči v {location.name_cs}",
            color=discord.Color.blue()
        )
        
        player_lines = []
        for pid in other_players[:20]:  # Max 20
            try:
                user = await bot.fetch_user(pid)
                other_state = world_manager.get_player_state(pid)
                
                pvp_icon = "⚔️" if other_state.pvp_enabled else "🛡️"
                camp_icon = "⛺" if other_state.current_camp else ""
                bounty_icon = "💰" if other_state.bounty > 0 else ""
                
                player_lines.append(
                    f"{pvp_icon} **{user.display_name}** {camp_icon}{bounty_icon}"
                )
            except:
                continue
        
        if player_lines:
            embed.description = "\n".join(player_lines)
            
            embed.set_footer(
                text="⚔️ = PvP ON | ⛺ = V táboře | 💰 = Wanted"
            )
        else:
            embed.description = "Žádní hráči nenalezeni"
        
        await interaction.response.send_message(embed=embed)
    
    
    # ========== CAMP COMMANDS ==========
    
    @bot.tree.command(name="camp_create", description="⛺ Vytvoř tábor")
    @app_commands.describe(name="Název tábora")
    async def camp_create_command(interaction: discord.Interaction, name: str):
        """Vytvoří tábor"""
        player_id = interaction.user.id
        
        success, message, camp = world_manager.create_camp(player_id, name)
        
        if success:
            embed = discord.Embed(
                title="⛺ Tábor vytvořen!",
                description=f"Úspěšně jsi vytvořil tábor **{name}**",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📍 Lokace",
                value=world_manager.locations[camp.location_id].name_cs,
                inline=True
            )
            
            embed.add_field(
                name="⏱️ Vyprší za",
                value="24 hodin",
                inline=True
            )
            
            embed.add_field(
                name="💡 Tip",
                value=(
                    "Použij `/camp_protect` pro ochranu!\n"
                    "Pozvi přátele: `/camp_invite @hráč`"
                ),
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    
    @bot.tree.command(name="camp_enter", description="🚪 Vstup do tábora")
    @app_commands.describe(camp_name="Název tábora")
    async def camp_enter_command(interaction: discord.Interaction, camp_name: str):
        """Vstoupí do tábora"""
        player_id = interaction.user.id
        state = world_manager.get_player_state(player_id)
        
        # Najdi tábor podle jména
        camps_here = world_manager.get_camps_in_location(state.current_location)
        
        camp = None
        for c in camps_here:
            if camp_name.lower() in c.name.lower():
                camp = c
                break
        
        if not camp:
            await interaction.response.send_message(
                f"❌ Tábor '{camp_name}' nebyl nalezen v této lokaci!",
                ephemeral=True
            )
            return
        
        success, message = world_manager.enter_camp(player_id, camp.id)
        
        if success:
            embed = discord.Embed(
                title="⛺ Vstoupil jsi do tábora",
                description=f"**{camp.name}**",
                color=discord.Color.green()
            )
            
            # Členové
            member_count = len(camp.members)
            embed.add_field(
                name="👥 Členové",
                value=f"{member_count} hráčů",
                inline=True
            )
            
            # Ochrana
            if camp.protections:
                active = [spell for spell, expires in camp.protections.items() if expires > time.time()]
                if active:
                    embed.add_field(
                        name="🛡️ Ochrana",
                        value=", ".join(active),
                        inline=True
                    )
            
            embed.add_field(
                name="💡 Příkazy",
                value=(
                    "`/camp_leave` - Opusť tábor\n"
                    "`/camp_rest` - Odpočiň si (2x rychlejší léčení)"
                ),
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    
    @bot.tree.command(name="camp_leave", description="🚪 Opusť tábor")
    async def camp_leave_command(interaction: discord.Interaction):
        """Opustí tábor"""
        player_id = interaction.user.id
        
        success, message = world_manager.leave_camp(player_id)
        
        if success:
            await interaction.response.send_message(message)
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    
    @bot.tree.command(name="camp_protect", description="🛡️ Ochraň tábor kouzlem")
    @app_commands.describe(spell="Ochranné kouzlo (cave_inimicum, protego_totalum)")
    async def camp_protect_command(interaction: discord.Interaction, spell: str):
        """Ochrání tábor"""
        player_id = interaction.user.id
        
        # Mapování kouzel
        protection_spells = {
            "cave_inimicum": ("Cave Inimicum", "Varuje před nepřáteli", 3600),
            "protego_totalum": ("Protego Totalum", "Magická bariéra", 7200),
            "salvio_hexia": ("Salvio Hexia", "Ochrana před kouzly", 3600),
            "repello_inimicum": ("Repello Inimicum", "Odpuzuje nepřátele", 7200)
        }
        
        spell_lower = spell.lower().replace(" ", "_")
        
        if spell_lower not in protection_spells:
            await interaction.response.send_message(
                f"❌ Neznámé ochranné kouzlo! Dostupné:\n" +
                "\n".join(f"• {data[0]}" for data in protection_spells.values()),
                ephemeral=True
            )
            return
        
        spell_name, description, duration = protection_spells[spell_lower]
        
        success, message = world_manager.protect_camp(player_id, spell_name, duration)
        
        if success:
            embed = discord.Embed(
                title="🛡️ Ochrana aktivována!",
                description=f"**{spell_name}**\n_{description}_",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="⏱️ Doba trvání",
                value=f"{duration//3600} hodin",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    
    @bot.tree.command(name="camp_raid", description="⚔️ Napadni tábor")
    @app_commands.describe(camp_name="Název tábora který chceš napadnout")
    async def camp_raid_command(interaction: discord.Interaction, camp_name: str):
        """Napadne tábor"""
        player_id = interaction.user.id
        state = world_manager.get_player_state(player_id)
        
        # Najdi tábor
        camps_here = world_manager.get_camps_in_location(state.current_location)
        
        camp = None
        for c in camps_here:
            if camp_name.lower() in c.name.lower():
                camp = c
                break
        
        if not camp:
            await interaction.response.send_message(
                f"❌ Tábor '{camp_name}' nebyl nalezen!",
                ephemeral=True
            )
            return
        
        # Raid
        success, message, loot = world_manager.raid_camp(player_id, camp.id)
        
        if success:
            embed = discord.Embed(
                title="⚔️ RAID ÚSPĚŠNÝ!",
                description=message,
                color=discord.Color.red()
            )
            
            if loot:
                loot_list = [f"• {item}: {count}x" for item, count in loot.items()]
                embed.add_field(
                    name="💰 Kořist",
                    value="\n".join(loot_list),
                    inline=False
                )
            else:
                embed.add_field(
                    name="💰 Kořist",
                    value="Tábor byl prázdný",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    
    # ========== PVP COMMANDS ==========
    
    @bot.tree.command(name="pvp_toggle", description="⚔️ Zapni/vypni PvP")
    async def pvp_toggle_command(interaction: discord.Interaction):
        """Přepne PvP status"""
        player_id = interaction.user.id
        state = world_manager.get_player_state(player_id)
        
        state.pvp_enabled = not state.pvp_enabled
        world_manager.save()
        
        if state.pvp_enabled:
            embed = discord.Embed(
                title="⚔️ PvP ZAPNUTO",
                description=(
                    "**VAROVÁNÍ:** Nyní mohou ostatní hráči na tebe zaútočit!\n\n"
                    "V Open PvP zónách může kdokoliv zaútočit.\n"
                    "V Consensual zónách jen hráči s PvP ON."
                ),
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="🛡️ PvP VYPNUTO",
                description=(
                    "Jsi v bezpečí před většinou útoků.\n\n"
                    "Poznámka: V Open PvP zónách stále můžeš být napaden!"
                ),
                color=discord.Color.green()
            )
        
        await interaction.response.send_message(embed=embed)
    
    
    @bot.tree.command(name="pvp_attack", description="⚔️ Zaútoč na hráče")
    @app_commands.describe(target="Hráč na kterého chceš zaútočit")
    async def pvp_attack_command(interaction: discord.Interaction, target: discord.Member):
        """Zahájí PvP souboj"""
        attacker_id = interaction.user.id
        target_id = target.id
        
        # Kontroly
        if attacker_id == target_id:
            await interaction.response.send_message(
                "❌ Nemůžeš zaútočit sám na sebe!",
                ephemeral=True
            )
            return
        
        if target.bot:
            await interaction.response.send_message(
                "❌ Nemůžeš zaútočit na bota!",
                ephemeral=True
            )
            return
        
        # Může útočit?
        can_attack, reason = world_manager.can_attack(attacker_id, target_id)
        
        if not can_attack:
            await interaction.response.send_message(
                f"❌ {reason}",
                ephemeral=True
            )
            return
        
        # Zahaj souboj (integruje se s existujícím combat systémem)
        location = world_manager.get_player_location(attacker_id)
        
        embed = discord.Embed(
            title="⚔️ PVP SOUBOJ ZAHÁJEN!",
            description=(
                f"**{interaction.user.display_name}** útočí na **{target.display_name}**!\n\n"
                f"📍 Lokace: {location.name_cs}\n"
                f"⚠️ Smrt je trvalá! Bojuj statečně!\n\n"
                f"Použij `/cast <kouzlo>` pro útok!"
            ),
            color=discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Tady by se integroval existující combat systém z bot.py
        # combat_engine.start_duel(attacker, target, pvp=True)
    
    
    @bot.tree.command(name="bounty_list", description="💰 Seznam wanted hráčů")
    async def bounty_list_command(interaction: discord.Interaction):
        """Zobrazí wanted hráče"""
        wanted = world_manager.get_bounty_list()
        
        if not wanted:
            await interaction.response.send_message(
                "✅ Momentálně nejsou žádní wanted hráči!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="💰 WANTED - Odměny za hlavu",
            description="Zabij tyto hráče a získej odměnu!",
            color=discord.Color.gold()
        )
        
        for player_id, bounty, kills in wanted[:10]:  # Top 10
            try:
                user = await bot.fetch_user(player_id)
                embed.add_field(
                    name=f"⚔️ {user.display_name}",
                    value=(
                        f"💰 Odměna: **{bounty}g**\n"
                        f"🩸 Zabití: {kills}"
                    ),
                    inline=False
                )
            except:
                continue
        
        embed.set_footer(text="Použij /pvp_attack pro útok!")
        
        await interaction.response.send_message(embed=embed)
    
    
    # ========== ECONOMY COMMANDS ==========
    
    @bot.tree.command(name="shop", description="🏪 Otevři obchod")
    @app_commands.describe(category="Kategorie (healing, ingredient, utility)")
    async def shop_command(interaction: discord.Interaction, category: Optional[str] = None):
        """Zobrazí obchod"""
        player_id = interaction.user.id
        location = world_manager.get_player_location(player_id)
        
        if not location.has_shop:
            await interaction.response.send_message(
                f"❌ V {location.name_cs} není obchod!",
                ephemeral=True
            )
            return
        
        items = economy_manager.get_shop_inventory(category)
        
        embed = discord.Embed(
            title="🏪 Obchod",
            description=economy_manager.format_shop(items),
            color=discord.Color.blue()
        )
        
        embed.set_footer(text="Použij /buy <item> <počet> pro nákup")
        
        await interaction.response.send_message(embed=embed)
    
    
    @bot.tree.command(name="buy", description="💰 Kup item z obchodu")
    @app_commands.describe(
        item="Co chceš koupit?",
        quantity="Kolik kusů? (default 1)"
    )
    async def buy_command(
        interaction: discord.Interaction, 
        item: str, 
        quantity: int = 1
    ):
        """Koupí item"""
        player_id = interaction.user.id
        state = world_manager.get_player_state(player_id)
        location = world_manager.get_player_location(player_id)
        
        if not location.has_shop:
            await interaction.response.send_message(
                f"❌ V {location.name_cs} není obchod!",
                ephemeral=True
            )
            return
        
        # Najdi item
        item_id = item.lower().replace(" ", "_")
        
        success, message, new_gold, new_inv = economy_manager.buy_item(
            state.inventory,
            state.gold,
            item_id,
            quantity
        )
        
        if success:
            state.gold = new_gold
            state.inventory = new_inv
            world_manager.save()
            
            await interaction.response.send_message(message)
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    
    @bot.tree.command(name="sell", description="💰 Prodej item")
    @app_commands.describe(
        item="Co chceš prodat?",
        quantity="Kolik kusů? (default 1)"
    )
    async def sell_command(
        interaction: discord.Interaction,
        item: str,
        quantity: int = 1
    ):
        """Prodá item"""
        player_id = interaction.user.id
        state = world_manager.get_player_state(player_id)
        
        item_id = item.lower().replace(" ", "_")
        
        success, message, new_gold, new_inv = economy_manager.sell_item(
            state.inventory,
            state.gold,
            item_id,
            quantity
        )
        
        if success:
            state.gold = new_gold
            state.inventory = new_inv
            world_manager.save()
            
            await interaction.response.send_message(message)
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    
    @bot.tree.command(name="gather", description="🌿 Seber zdroje")
    async def gather_command(interaction: discord.Interaction):
        """Sebere zdroje v lokaci"""
        player_id = interaction.user.id
        state = world_manager.get_player_state(player_id)
        location = world_manager.get_player_location(player_id)
        
        if state.traveling:
            await interaction.response.send_message(
                "❌ Nemůžeš sbírat během cestování!",
                ephemeral=True
            )
            return
        
        success, message, resource_id, value, new_inv = economy_manager.gather(
            player_id,
            location.id,
            state.inventory
        )
        
        if success:
            state.inventory = new_inv
            world_manager.save()
            
            embed = discord.Embed(
                title="🌿 Gathering úspěšný!",
                description=message,
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    
    @bot.tree.command(name="inventory", description="🎒 Tvůj inventář")
    async def inventory_command(interaction: discord.Interaction):
        """Zobrazí inventář"""
        player_id = interaction.user.id
        state = world_manager.get_player_state(player_id)
        
        embed = discord.Embed(
            title="🎒 Inventář",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="💰 Gold",
            value=f"**{state.gold}g**",
            inline=False
        )
        
        embed.add_field(
            name="📦 Itemy",
            value=economy_manager.format_inventory(state.inventory),
            inline=False
        )
        
        total_value = economy_manager.get_inventory_value(state.inventory)
        embed.set_footer(text=f"Celková hodnota inventáře: ~{total_value}g")
        
        await interaction.response.send_message(embed=embed)
    
    
    # ========== PARTY COMMANDS ==========
    
    @bot.tree.command(name="party_create", description="👥 Vytvoř party")
    async def party_create_command(interaction: discord.Interaction):
        """Vytvoří party"""
        player_id = interaction.user.id
        
        success, message, party_id = world_manager.create_party(player_id)
        
        if success:
            embed = discord.Embed(
                title="👥 Party vytvořena!",
                description="Pozvi přátele: `/party_invite @hráč`",
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    
    @bot.tree.command(name="party_invite", description="📨 Pozvi hráče do party")
    @app_commands.describe(player="Hráč kterého chceš pozvat")
    async def party_invite_command(interaction: discord.Interaction, player: discord.Member):
        """Pozve hráče"""
        inviter_id = interaction.user.id
        invitee_id = player.id
        
        success, message, party_id = world_manager.invite_to_party(inviter_id, invitee_id)
        
        if success:
            # Vytvoř accept/decline view
            class PartyInviteView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=300)
                
                @discord.ui.button(label="Přijmout", style=discord.ButtonStyle.green)
                async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id != invitee_id:
                        await interaction.response.send_message("❌ Tohle není pro tebe!", ephemeral=True)
                        return
                    
                    success, msg = world_manager.join_party(invitee_id, party_id)
                    if success:
                        await interaction.response.send_message(f"✅ {msg}")
                    else:
                        await interaction.response.send_message(f"❌ {msg}", ephemeral=True)
                    
                    self.stop()
                
                @discord.ui.button(label="Odmítnout", style=discord.ButtonStyle.red)
                async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id != invitee_id:
                        await interaction.response.send_message("❌ Tohle není pro tebe!", ephemeral=True)
                        return
                    
                    await interaction.response.send_message("❌ Odmítl jsi pozvánku")
                    self.stop()
            
            embed = discord.Embed(
                title="👥 Pozvánka do party",
                description=f"**{interaction.user.display_name}** tě zve do své party!",
                color=discord.Color.blue()
            )
            
            await interaction.response.send_message(
                content=player.mention,
                embed=embed,
                view=PartyInviteView()
            )
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    
    @bot.tree.command(name="party_leave", description="🚪 Opusť party")
    async def party_leave_command(interaction: discord.Interaction):
        """Opustí party"""
        player_id = interaction.user.id
        
        success, message = world_manager.leave_party(player_id)
        
        if success:
            await interaction.response.send_message(message)
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    
    @bot.tree.command(name="party_info", description="ℹ️ Info o party")
    async def party_info_command(interaction: discord.Interaction):
        """Zobrazí info o party"""
        player_id = interaction.user.id
        members = world_manager.get_party_members(player_id)
        
        if not members:
            await interaction.response.send_message(
                "❌ Nejsi v žádné party!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="👥 Tvoje Party",
            color=discord.Color.blue()
        )
        
        member_list = []
        for member_id in members:
            try:
                user = await bot.fetch_user(member_id)
                state = world_manager.get_player_state(member_id)
                location = world_manager.get_player_location(member_id)
                
                member_list.append(
                    f"• **{user.display_name}** - {location.name_cs}"
                )
            except:
                continue
        
        embed.add_field(
            name=f"Členové ({len(members)}/5)",
            value="\n".join(member_list) if member_list else "Žádní členové",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    
    # ========== NOVÉ PŘÍKAZY PRO PROCEDURÁLNÍ GENEROVÁNÍ ==========
    
    @bot.tree.command(name="explore", description="🧭 Prozkoumej náhodný směr!")
    async def explore_command(interaction: discord.Interaction):
        """
        🌟 NOVÝ! Automaticky vygeneruje a prozkoumá náhodný směr
        """
        player_id = interaction.user.id
        
        success, message = world_manager.explore_random_direction(player_id)
        
        if success:
            embed = discord.Embed(
                title="🧭 Průzkum",
                description=message,
                color=discord.Color.blue()
            )
            embed.set_footer(text="Používej /explore pro objevování nových míst!")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    
    @bot.tree.command(name="nearby", description="🗺️ Co je v okolí?")
    async def nearby_command(interaction: discord.Interaction):
        """
        🌟 NOVÝ! Zobrazí prozkoumané i neprozkoumané oblasti
        """
        player_id = interaction.user.id
        summary = world_manager.get_exploration_summary(player_id)
        
        embed = discord.Embed(
            title="🗺️ Okolí",
            description=summary,
            color=discord.Color.blue()
        )
        
        embed.set_footer(text="Použij /travel [směr] pro prozkoumání nových míst")
        await interaction.response.send_message(embed=embed)
    
    
    @bot.tree.command(name="worldstats", description="📊 Statistiky světa")
    @app_commands.default_permissions(administrator=True)  # Jen pro adminy
    async def worldstats_command(interaction: discord.Interaction):
        """
        🌟 NOVÝ! Zobrazí statistiky procedurálního světa
        """
        stats = world_manager.get_world_stats()
        
        embed = discord.Embed(
            title="📊 Statistiky Světa",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="🗺️ Lokace",
            value=(
                f"Celkem: **{stats['total_locations']}**\n"
                f"Přednastavené: {stats['predefined']}\n"
                f"✨ Vygenerované: **{stats['generated']}**"
            ),
            inline=False
        )
        
        # Typy lokací
        types_text = "\n".join([
            f"{loc_type}: {count}" 
            for loc_type, count in stats['types'].items()
        ])
        
        embed.add_field(
            name="🏞️ Typy Lokací",
            value=types_text,
            inline=True
        )
        
        # PvP zóny
        pvp_text = "\n".join([
            f"{pvp_zone}: {count}" 
            for pvp_zone, count in stats['pvp_zones'].items()
        ])
        
        embed.add_field(
            name="⚔️ PvP Zóny",
            value=pvp_text,
            inline=True
        )
        
        embed.add_field(
            name="👥 Hráči & Tábory",
            value=(
                f"Hráči: {stats['total_players']}\n"
                f"Tábory: {stats['total_camps']}"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    
    print("✅ World commands registrovány!")