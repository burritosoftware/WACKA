import hikari
import lightbulb
import miru
import aiohttp
import os
import sys
from dotenv import load_dotenv
import logging
import dataset
import functions.authManager as authManager

# Load .env values
load_dotenv()

# Create logger
logger = logging.getLogger('wacka.bot')

# Initialize bot instance
bot = lightbulb.BotApp(token=os.getenv('TOKEN'), prefix=os.getenv('PREFIX'), banner=None, intents=hikari.Intents.ALL_UNPRIVILEGED, default_enabled_guilds=(884484987758473217,623015907995811840,))
miru.load(bot)

@bot.listen()
async def on_starting(event: hikari.StartingEvent) -> None:

    # Create a ClientSession to be used for the entire uptime of the bot
    bot.d.aio_session = aiohttp.ClientSession()
    logger.info("Created aiohttp.ClientSession")
    bot.d.logger = logger
    logger.info("Added logger to datastore")
    bot.d.db = dataset.connect(os.getenv('DATABASE'), engine_kwargs=dict(connect_args={'check_same_thread': False}))
    logger.info(f"Connected to database {os.getenv('DATABASE')}")
    # Login to Aime and get a fresh new session cookie
    loginStatus = await authManager.loginWithAimeID(bot)
    if loginStatus == True:
        logger.info("Logged in with Aime")
    else:
        logger.error("Failed to login with Aime, likely due to maintenance")

@bot.listen()
async def on_stopping(event: hikari.StoppingEvent) -> None:
    # Log out of Aime
    logoutStatus = await authManager.logout(bot)
    if logoutStatus == True:
        logger.info("Logged out of Aime")
    else:
        logger.error("Failed to logout of Aime, likely due to maintenance")
    # Close the ClientSession
    await bot.d.aio_session.close()
    logger.info("Closed aiohttp.ClientSession")

# Update presence on start
@bot.listen()
async def on_started(event: hikari.StartedEvent) -> None:
    await bot.update_presence(activity=hikari.Activity(name="/help | WACCA! 🧤"))
    logger.info("Updated presence")

# Error handling
@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        await event.context.respond(f"<:no:442206260151189518> An error occurred while running `{event.context.command.name}`. Try again in a minute. If this persists, please contact Burrito at <https://website.burrito.software/discord>.", flags=hikari.MessageFlag.EPHEMERAL)
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