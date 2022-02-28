import hikari
import lightbulb
import os
import aiohttp
from dotenv import load_dotenv
import logging
import dataset
import miru

# Loading .env values
load_dotenv()

# Create logger
logger = logging.getLogger('wacka.bot')

# Initializing bot instance
bot = lightbulb.BotApp(token=os.getenv('TOKEN'), prefix=os.getenv('PREFIX'), banner=None, intents=hikari.Intents.ALL_UNPRIVILEGED, default_enabled_guilds=(884484987758473217,623015907995811840,))
miru.load(bot)

# Create and close an aiohttp.ClientSession on start and stop of bot, add it to DataStore
# Initialize database and add it to DataStore
@bot.listen()
async def on_starting(event: hikari.StartingEvent) -> None:

    bot.d.aio_session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar())
    logger.info("Created aiohttp.ClientSession")
    bot.d.logger = logger
    logger.info("Added logger to datastore")
    bot.d.db = dataset.connect(os.getenv('DATABASE'), engine_kwargs=dict(connect_args={'check_same_thread': False}))
    logger.info(f"Connected to database {os.getenv('DATABASE')}")

@bot.listen()
async def on_stopping(event: hikari.StoppingEvent) -> None:
    await bot.d.aio_session.close()
    logger.info("Closed aiohttp.ClientSession")

# Update presence on started
@bot.listen()
async def on_started(event: hikari.StartedEvent) -> None:
    await bot.update_presence(activity=hikari.Activity(name="/help | WACCA! 🧤"))
    logger.info("Updated presence")

# Error Handler
@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        await event.context.respond(f"<:no:442206260151189518> An error occurred while running `{event.context.command.name}`. If this persists, please contact Burrito at <https://website.burrito.software/discord>.", flags=hikari.MessageFlag.EPHEMERAL)
        raise event.exception

    # Unwrap the exception to get the original cause
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.NotOwner):
        await event.context.respond("<:no:442206260151189518> You are not the owner of this bot.", flags=hikari.MessageFlag.EPHEMERAL)
    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        await event.context.respond(f":hourglass: This command is on cooldown. Retry in `{exception.retry_after:.2f}` seconds.", flags=hikari.MessageFlag.EPHEMERAL)
    else:
        raise exception

# Loading all extensions
bot.load_extensions_from("./extensions/", must_exist=True)

# uvloop for performance on UNIX systems
if os.name != "nt":
    import uvloop
    uvloop.install()

bot.run()