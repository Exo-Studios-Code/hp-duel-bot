#!/usr/bin/env python3
"""
Setup Script pro HP Duel Bot
Vytvoří potřebné adresáře a ověří instalaci
"""

import os
import sys
import json

def create_directories():
    """Vytvoří potřebné adresáře"""
    dirs = [
        'data',
        'models'
    ]
    
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✅ Adresář '{dir_name}' vytvořen/ověřen")

def initialize_data_files():
    """Inicializuje prázdné datové soubory pokud neexistují"""
    
    # players.json
    if not os.path.exists('data/players.json'):
        with open('data/players.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
        print("✅ data/players.json vytvořen")
    else:
        print("ℹ️  data/players.json již existuje")
    
    # spells.json - vygeneruj z databáze
    if not os.path.exists('data/spells.json'):
        print("🔄 Generuji data/spells.json...")
        try:
            from spell_database import save_database
            save_database()
            print("✅ data/spells.json vygenerován")
        except Exception as e:
            print(f"⚠️  Nepodařilo se vygenerovat spells.json: {e}")
            print("   Spusť: python spell_database.py")
    else:
        print("ℹ️  data/spells.json již existuje")

def check_dependencies():
    """Zkontroluje nainstalované závislosti"""
    print("\n📦 Kontrola závislostí...")
    
    dependencies = {
        'discord': 'discord.py',
        'dotenv': 'python-dotenv',
    }
    
    missing = []
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {package} nainstalován")
        except ImportError:
            print(f"❌ {package} NENÍ nainstalován")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Chybějící závislosti: {', '.join(missing)}")
        print("   Nainstaluj je pomocí: pip install -r requirements.txt")
        return False
    
    return True

def check_token():
    """Zkontroluje zda je nastaven Discord token"""
    print("\n🔑 Kontrola Discord tokenu...")
    
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if token and token != 'YOUR_TOKEN_HERE':
        print("✅ DISCORD_BOT_TOKEN je nastaven")
        return True
    else:
        print("⚠️  DISCORD_BOT_TOKEN NENÍ nastaven")
        print("   Nastav jej pomocí:")
        print("   export DISCORD_BOT_TOKEN='your_token_here'")
        print("   nebo vytvoř .env soubor")
        return False

def create_env_template():
    """Vytvoří .env.example template"""
    env_content = """# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
GUILD_ID=your_guild_id_for_testing  # Optional
"""
    
    if not os.path.exists('.env.example'):
        with open('.env.example', 'w') as f:
            f.write(env_content)
        print("✅ .env.example vytvořen")
    else:
        print("ℹ️  .env.example již existuje")

def main():
    """Hlavní setup funkce"""
    print("🪄 ===== HP Duel Bot Setup =====\n")
    
    # Vytvoř adresáře
    print("📁 Vytváření adresářů...")
    create_directories()
    
    # Inicializuj data soubory
    print("\n📊 Inicializace datových souborů...")
    initialize_data_files()
    
    # Vytvoř .env template
    print("\n⚙️  Vytváření konfiguračních souborů...")
    create_env_template()
    
    # Zkontroluj závislosti
    deps_ok = check_dependencies()
    
    # Zkontroluj token
    token_ok = check_token()
    
    # Shrnutí
    print("\n" + "="*50)
    print("📋 SHRNUTÍ SETUP")
    print("="*50)
    
    if deps_ok and token_ok:
        print("✅ Vše je připraveno!")
        print("\n🚀 Spusť bota pomocí: python bot.py")
    else:
        print("⚠️  Setup není kompletní. Prosím dokončte následující:")
        if not deps_ok:
            print("   • Nainstaluj závislosti: pip install -r requirements.txt")
        if not token_ok:
            print("   • Nastav DISCORD_BOT_TOKEN (viz README.md)")
        print("\n📖 Pro podrobné instrukce viz README.md")
    
    print("="*50)

if __name__ == "__main__":
    main()
