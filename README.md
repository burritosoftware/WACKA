# WACKA
An open-source Discord bot for the arcade rhythm game WACCA.

## Setup

### Requirements
- Python 3
- Aime Account with a WACCA Profile (it is recommended to have a dedicated account for this bot)

### Installation
1. Install dependencies.
```
python -m pip install -r requirements.txt
```

2. Create a copy of the `.env-example` file to `.env` and fill in your bot token and Aime ID
- To get the Aime ID, login on WACCA My Page, and before selecting profile, run this in the console: `document.getElementById('aimeId').value`
```
cp .env-example .env
nano .env
```

3. Start the bot.
```
python bot.py
```

Done!