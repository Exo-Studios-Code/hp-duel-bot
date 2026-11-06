# HP Duel Bot

A Discord bot for Harry Potter roleplay servers with a **realistic duel system**: no HP bars, only real consequences. Wounds, bleeding, permanent scars and permanent death. Unofficial fan project, not affiliated with or endorsed by Warner Bros. or J.K. Rowling.

## Features

### Duels
- Injury system per body part (cuts, fractures, burns) instead of hit points
- Bleeding, pain, fatigue and unconsciousness affect casting accuracy
- Shield spells, counter-spells, cooldowns and combined defense and attack turns
- Permadeath: dying wipes learned spells, `/revive` starts a new character

### Magic and Potions
- 200+ spells you must learn before you can cast them, with difficulty, learning time and prerequisites
- Potion brewing with ingredients, timers and a potion inventory
- Healing spells and potions to treat injuries

### Open World
- Procedurally generated locations with a world map and `/location`

### Hogwarts Server Tools
- House sorting, house points and the House Cup
- Ollivander's wand shop with 15 wand roles
- Patronus test with roles, RPG character profiles and a pet menagerie
- Daily Prophet articles, welcome letters and rules posting
- Unbreakable Vow between three players

## Tech Stack

- Python 3.10+
- discord.py 2.3+
- JSON file storage, no database needed

## Getting Started

### Prerequisites

- Python 3.10+
- A Discord bot token (create it in the Discord Developer Portal)

### Installation

```bash
git clone https://github.com/Exo-Studios-Code/hp-duel-bot.git
cd hp-duel-bot
pip install -r requirements.txt
mkdir -p data
```

### Configuration

Linux/macOS:

```bash
export DISCORD_BOT_TOKEN=your_bot_token
export GUILD_ID=your_server_id      # optional, instant command sync for testing
```

Windows PowerShell:

```powershell
$env:DISCORD_BOT_TOKEN="your_bot_token"
$env:GUILD_ID="your_server_id"
```

### Run

```bash
python bot.py
```

## Main Commands

| Command | Description |
|---------|-------------|
| `/status`, `/spells`, `/learn` | Character state, spell list, learning spells |
| `/duel`, `/defend`, `/cast_utility`, `/heal`, `/revive` | Duels and recovery |
| `/brew`, `/brewing_status`, `/cancel_brewing`, `/potions`, `/use_potion` | Potions |
| `/map`, `/location` | Open world |
| `/postava`, `/zverinec`, `/patron` | Character, pets, Patronus |
| `/kolej_body`, `/pohar` | House points and the House Cup |
| `/setup_welcome`, `/setup_sorting`, `/setup_ollivander`, `/setup_patron`, `/post_rules`, `/dennik` | Server setup (admin) |
| `/neporusitelny_slib`, `/moje_sliby` | Unbreakable Vow |
| `/help` | Full help |

More design notes are in `DESIGN.md`, `PVP_SYSTEM_EXPLAINED.md` and `OPEN_WORLD_GUIDE.md`.
