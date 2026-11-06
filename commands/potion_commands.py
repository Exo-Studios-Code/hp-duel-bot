"""
Potion Commands - Discord slash příkazy pro lektvary
/brew, /potions, /use_potion, /ingredients, atd.
"""

import discord
from discord import app_commands
from discord.ext import commands
import time

from potion_database import get_potion, get_all_potions, get_brewable_potions
from models.potions import get_ingredient, get_all_ingredients, PotionRarity


async def setup_potion_commands(bot: commands.Bot):
    """Registruje všechny potion příkazy"""
    
    if not hasattr(bot, 'potion_manager'):
        print("⚠️ PotionBrewingManager není inicializován!")
        return
    
    potion_manager = bot.potion_manager
    player_db = bot.player_db
    
    
    # ========== BREWING COMMANDS ==========
    
    @bot.tree.command(name="brew", description="🧪 Začni vařit lektvar")
    @app_commands.describe(potion="Který lektvar chceš uvařit?")
    async def brew_command(interaction: discord.Interaction, potion: str):
        """Začne vařit lektvar"""
        player_id = interaction.user.id
        
        # Najdi lektvar
        potion_obj = None
        potion_lower = potion.lower()
        
        for p in get_all_potions():
            if (potion_lower in p.name_cs.lower() or 
                potion_lower in p.name_en.lower() or 
                p.id == potion_lower):
                potion_obj = p
                break
        
        if not potion_obj:
            await interaction.response.send_message(
                f"❌ Lektvar '{potion}' nebyl nalezen! Použij `/potions list`",
                ephemeral=True
            )
            return
        
        # Začni vařit
        success, message = potion_manager.start_brewing(player_id, potion_obj.id)
        
        if success:
            embed = discord.Embed(
                title="🧪 Vaření zahájeno",
                description=message,
                color=discord.Color.purple()
            )
            
            # Přidej info o lektvaru
            embed.add_field(
                name="📖 Popis",
                value=potion_obj.description,
                inline=False
            )
            
            # Receptura
            if potion_obj.recipe:
                ingredients_text = "\n".join([
                    f"• {get_ingredient(ing_id).name_cs}: {count}x"
                    for ing_id, count in potion_obj.recipe.ingredients.items()
                ])
                embed.add_field(
                    name="🌿 Použité ingredience",
                    value=ingredients_text,
                    inline=False
                )
            
            embed.set_footer(text="Použij /brewing status pro kontrolu pokroku")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"{message}", ephemeral=True)
    
    
    @bot.tree.command(name="brewing_status", description="⏱️ Zkontroluj stav vaření")
    async def brewing_status_command(interaction: discord.Interaction):
        """Zkontroluje stav probíhajícího vaření"""
        player_id = interaction.user.id
        inventory = potion_manager.get_inventory(player_id)
        
        if not inventory.active_brewing:
            # Zkontroluj jestli něco nedokončilo
            is_complete, message, potion = potion_manager.check_brewing_completion(player_id)
            
            if is_complete:
                await interaction.response.send_message(message)
            else:
                await interaction.response.send_message(
                    "❌ Momentálně nic nevaříš!\nPoužij `/brew [lektvar]` pro zahájení vaření.",
                    ephemeral=True
                )
            return
        
        brewing = inventory.active_brewing
        potion = get_potion(brewing.potion_id)
        
        # Zkontroluj jestli je hotové
        is_complete, message, completed_potion = potion_manager.check_brewing_completion(player_id)
        
        if is_complete:
            await interaction.response.send_message(message)
            return
        
        # Stále probíhá
        time_remaining = brewing.time_remaining()
        progress = brewing.progress() * 100
        
        # Formátuj zbývající čas
        hours = int(time_remaining / 3600)
        minutes = int((time_remaining % 3600) / 60)
        
        if hours > 24:
            days = hours / 24
            time_str = f"{days:.1f} dní"
        elif hours > 0:
            time_str = f"{hours}h {minutes}m"
        else:
            time_str = f"{minutes}m"
        
        embed = discord.Embed(
            title="🧪 Probíhající vaření",
            description=f"Vaříš: **{potion.name_cs}**",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="⏱️ Zbývá",
            value=time_str,
            inline=True
        )
        
        embed.add_field(
            name="📊 Pokrok",
            value=f"{progress:.1f}%",
            inline=True
        )
        
        # Progress bar
        bar_length = 20
        filled = int(progress / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        embed.add_field(
            name="Progress",
            value=f"`{bar}`",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    
    @bot.tree.command(name="cancel_brewing", description="❌ Zruš probíhající vaření")
    async def cancel_brewing_command(interaction: discord.Interaction):
        """Zruší probíhající vaření (ingredience se ztratí)"""
        player_id = interaction.user.id
        inventory = potion_manager.get_inventory(player_id)
        
        if not inventory.active_brewing:
            await interaction.response.send_message(
                "❌ Momentálně nic nevaříš!",
                ephemeral=True
            )
            return
        
        potion = get_potion(inventory.active_brewing.potion_id)
        
        # Zruš vaření
        inventory.active_brewing = None
        potion_manager.save()
        
        await interaction.response.send_message(
            f"❌ Zrušil jsi vaření **{potion.name_cs}**!\n"
            f"⚠️ Všechny ingredience byly ztraceny."
        )
    
    
    # ========== POTION INVENTORY ==========
    
    @bot.tree.command(name="potions", description="🧪 Tvé lektvary a ingredience")
    @app_commands.describe(view="Co chceš vidět?")
    @app_commands.choices(view=[
        app_commands.Choice(name="Moje lektvary", value="potions"),
        app_commands.Choice(name="Moje ingredience", value="ingredients"),
        app_commands.Choice(name="Seznam všech lektvarů", value="list"),
        app_commands.Choice(name="Seznam ingrediencí", value="ing_list")
    ])
    async def potions_command(interaction: discord.Interaction, view: str = "potions"):
        """Zobrazí lektvary nebo ingredience"""
        player_id = interaction.user.id
        inventory = potion_manager.get_inventory(player_id)
        
        if view == "potions":
            # Moje lektvary
            if not inventory.potions:
                await interaction.response.send_message(
                    "❌ Nemáš žádné lektvary!\nPoužij `/brew` pro uvaření lektvaru.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="🧪 Tvé lektvary",
                color=discord.Color.purple()
            )
            
            for potion_id, count in inventory.potions.items():
                potion = get_potion(potion_id)
                if potion:
                    embed.add_field(
                        name=f"{potion.name_cs} ({count}x)",
                        value=f"_{potion.description}_\n💰 {potion.sell_price}g",
                        inline=False
                    )
            
            embed.set_footer(text="Použij /use_potion pro použití lektvaru")
            await interaction.response.send_message(embed=embed)
        
        elif view == "ingredients":
            # Moje ingredience
            if not inventory.ingredients:
                await interaction.response.send_message(
                    "❌ Nemáš žádné ingredience!\nPoužij `/gather` nebo kup si je.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="🌿 Tvé ingredience",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📊 Brewing Skill",
                value=f"**{inventory.brewing_skill}/100**",
                inline=False
            )
            
            ing_text = ""
            for ing_id, count in inventory.ingredients.items():
                ing = get_ingredient(ing_id)
                if ing:
                    ing_text += f"• **{ing.name_cs}**: {count}x\n"
            
            embed.add_field(
                name="🌿 Ingredience",
                value=ing_text if ing_text else "Žádné",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
        
        elif view == "list":
            # Seznam všech lektvarů
            embed = discord.Embed(
                title="📖 Seznam lektvarů",
                description="Všechny lektvary které lze uvařit",
                color=discord.Color.gold()
            )
            
            brewable = get_brewable_potions(inventory.brewing_skill)
            
            for potion in sorted(get_all_potions(), key=lambda p: p.rarity.value):
                can_brew = potion in brewable
                status = "✅" if can_brew else "🔒"
                
                value = f"_{potion.description}_\n"
                if potion.recipe:
                    value += f"⏱️ {potion.recipe.brewing_time:.0f}h | "
                    value += f"📊 Skill: {potion.recipe.required_skill}\n"
                    value += f"💰 {potion.buy_price}g"
                
                embed.add_field(
                    name=f"{status} {potion.name_cs}",
                    value=value,
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
        
        elif view == "ing_list":
            # Seznam ingrediencí
            embed = discord.Embed(
                title="📖 Seznam ingrediencí",
                color=discord.Color.green()
            )
            
            for ing in sorted(get_all_ingredients(), key=lambda i: i.rarity.value):
                have = inventory.ingredients.get(ing.id, 0)
                status = f"({have}x)" if have > 0 else ""
                
                embed.add_field(
                    name=f"{ing.name_cs} {status}",
                    value=(
                        f"_{ing.description}_\n"
                        f"💰 {ing.buy_price}g | "
                        f"🏷️ {ing.rarity.value}"
                    ),
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
    
    
    @bot.tree.command(name="use_potion", description="🍾 Použij lektvar")
    @app_commands.describe(
        potion="Který lektvar chceš použít?",
        target="Na koho? (pro lektvary vyžadující cíl)"
    )
    async def use_potion_command(
        interaction: discord.Interaction, 
        potion: str,
        target: discord.Member = None
    ):
        """Použije lektvar"""
        player_id = interaction.user.id
        player = player_db.get_player(player_id)
        
        # Najdi lektvar
        inventory = potion_manager.get_inventory(player_id)
        potion_id = None
        potion_lower = potion.lower()
        
        # Hledej v inventáři
        for pot_id in inventory.potions.keys():
            pot = get_potion(pot_id)
            if (potion_lower in pot.name_cs.lower() or 
                potion_lower in pot.name_en.lower() or 
                pot_id == potion_lower):
                potion_id = pot_id
                break
        
        if not potion_id:
            await interaction.response.send_message(
                f"❌ Nemáš lektvar '{potion}'!",
                ephemeral=True
            )
            return
        
        # Cíl (pokud je potřeba)
        target_player = None
        if target:
            target_player = player_db.get_player(target.id)
        
        # Použij lektvar
        success, message = potion_manager.use_potion(player, potion_id, target_player)
        
        if success:
            embed = discord.Embed(
                title="🧪 Lektvar použit",
                description=message,
                color=discord.Color.green()
            )
            
            if target:
                embed.set_footer(text=f"Cíl: {target.display_name}")
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    
    
    # ========== ADMIN COMMANDS ==========
    
    @bot.tree.command(name="give_potion", description="🎁 Dej hráči lektvar (ADMIN)")
    @app_commands.describe(
        player="Komu?",
        potion="Který lektvar?",
        count="Kolik?"
    )
    @app_commands.default_permissions(administrator=True)
    async def give_potion_command(
        interaction: discord.Interaction,
        player: discord.Member,
        potion: str,
        count: int = 1
    ):
        """Dá hráči lektvar"""
        # Najdi lektvar
        potion_obj = None
        potion_lower = potion.lower()
        
        for p in get_all_potions():
            if (potion_lower in p.name_cs.lower() or 
                potion_lower in p.name_en.lower() or 
                p.id == potion_lower):
                potion_obj = p
                break
        
        if not potion_obj:
            await interaction.response.send_message(
                f"❌ Neznámý lektvar: {potion}",
                ephemeral=True
            )
            return
        
        potion_manager.give_potion(player.id, potion_obj.id, count)
        
        await interaction.response.send_message(
            f"✅ Dal jsi {player.mention} {count}x **{potion_obj.name_cs}**!"
        )
    
    
    @bot.tree.command(name="give_ingredient", description="🎁 Dej hráči ingredienci (ADMIN)")
    @app_commands.describe(
        player="Komu?",
        ingredient="Kterou ingredienci?",
        count="Kolik?"
    )
    @app_commands.default_permissions(administrator=True)
    async def give_ingredient_command(
        interaction: discord.Interaction,
        player: discord.Member,
        ingredient: str,
        count: int = 1
    ):
        """Dá hráči ingredienci"""
        # Najdi ingredienci
        ing = get_ingredient(ingredient)
        
        if not ing:
            await interaction.response.send_message(
                f"❌ Neznámá ingredience: {ingredient}",
                ephemeral=True
            )
            return
        
        potion_manager.give_ingredient(player.id, ing.id, count)
        
        await interaction.response.send_message(
            f"✅ Dal jsi {player.mention} {count}x **{ing.name_cs}**!"
        )
    
    
    print("✅ Potion commands registrovány!")
