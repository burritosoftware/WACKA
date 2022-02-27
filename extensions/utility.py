import lightbulb
import os
from subprocess import Popen
import hikari
import re
import textwrap
from io import StringIO
from contextlib import redirect_stdout
import functions.dataManager as dataManager

async def addOrUpdateCookie(bot, cookieid) -> None:
    table = await dataManager.tableLookup(bot, 'cookie')
    cookie = await dataManager.findKey(table, 'session_id')
    if cookie == None:
        await dataManager.tableInsert(table, dict(key='session_id', value=cookieid))
        return(True)
    else:
        await dataManager.tableUpdate(table, dict(key='session_id', value=cookieid), ['key'])
        return(False)

bot_plugin = lightbulb.Plugin("Bot")

@bot_plugin.command
@lightbulb.command("ping", description="Gets the bot's latency.", ephemeral=True)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def ping(ctx: lightbulb.Context) -> None:
    await ctx.respond(f":ping_pong: **Pong!** Latency: {ctx.bot.heartbeat_latency*1000:.2f}ms")

@bot_plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("update", description="Pulls the latest source from GitHub and updates the bot.", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def update(ctx: lightbulb.Context) -> None:
    output = os.popen('git pull').read()
    if "Already up to date." in output:
        await ctx.respond("<:yes:459224261136220170> Bot already up to date.")
    else:
        ctx.bot.d.logger.info(f"Bot updated!\n\n{output}")
        await ctx.respond(f"<:yes:459224261136220170> **Update complete!** The bot will restart momentarily...\n\n```\n{output}\n```")
        await ctx.bot.update_presence(status=hikari.Status.IDLE, activity=hikari.Activity(name="Updating, please wait..."))
        if os.name != "nt":
            p = Popen(['pm2', 'restart', 'bot'])
            p.poll()

@bot_plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("eval", description="Evaluates Python code.", ephemeral=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def eval(ctx: lightbulb.Context) -> None:
    code = re.findall(r"```(?:[\w]*\n?)([\s\S(^\\`{3})]*?)\n*```", ctx.event.message.content)
    if not code:
        await ctx.respond("<:no:442206260151189518> Expected a Python codeblock.")
        return
    if "import os" in code or "import sys" in code or "token" in code:
        await ctx.respond("<:no:442206260151189518> This code has been blocked from running for security.")
        return
        
    else:
        code = ' '.join(code).strip('` ') 
        env = {'bot': ctx.bot, 'ctx': ctx, 'message': ctx.event.message}
        env.update(globals()) 
        new_forced_async_code = f"async def code():\n{textwrap.indent(code, ' ')}"
        exec(new_forced_async_code, env) 
        code = env['code'] 
        f = StringIO()
        with redirect_stdout(f):
            try: 
                await code()
            except Exception as e:
                await ctx.respond(f"<:no:442206260151189518> **error:**\n```py\n{e}\n```")
                return
        if f.getvalue() != "":
            await ctx.respond(f"<:yes:459224261136220170> **stdout:**\n```py\n{f.getvalue()}\n```")
        else:
            await ctx.event.message.add_reaction(emoji="yes",emoji_id=459224261136220170)

@bot_plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option(
    "cookie", "The cookie to add/update to/in the database", str, required=True
)
@lightbulb.command("setcookie", description="Sets next cookie to be used for My Page.", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def setcookie(ctx: lightbulb.Context) -> None:
    status = await addOrUpdateCookie(bot=ctx.bot, cookieid=ctx.options.cookie)
    if status:
        await ctx.respond("<:yes:459224261136220170> Added the cookie to the database!")
    else:
        await ctx.respond("<:yes:459224261136220170> Updated the cookie in the database!")

# @bot_plugin.command
# @lightbulb.add_checks(lightbulb.owner_only)
# @lightbulb.command("servers", description="Shows what servers this bot is in.", auto_defer=True, ephemeral=True)
# @lightbulb.implements(lightbulb.PrefixCommand)
# async def servers(ctx: lightbulb.Context) -> None:
#     guilds = ctx.bot.cache.get_guilds_view()
#     serverlist = []
#     for id in guilds:
#         name = ctx.bot.cache.get_guild(id).name
#         serverlist.append(f"{name} ({id})")
#     servernames = "`, `".join(serverlist)
#     await ctx.respond(f"<:yes:459224261136220170> Currently in **{len(guilds)}** servers: `{servernames}`")

# @bot_plugin.command
# @lightbulb.add_checks(lightbulb.owner_only)
# @lightbulb.option(
#     "id", "The ID of the server to show the channels for", str, required=True
# )
# @lightbulb.command("channels", description="Shows what channels are in a server.", auto_defer=True, ephemeral=True)
# @lightbulb.implements(lightbulb.PrefixCommand)
# async def servers(ctx: lightbulb.Context) -> None:
#     guild = ctx.bot.cache.get_guild(ctx.options.id)
#     channels = ctx.bot.cache.get_guild_channels_view_for_guild(guild)
#     channellist = []
#     for id in channels:
#         name = ctx.bot.cache.get_guild_channel(id).name
#         channellist.append(f"{name} ({id})")
#     channelnames = "`, `".join(channellist)
#     await ctx.respond(f"<:yes:459224261136220170> **{len(channels)}** channels found: `{channelnames}`")

# @bot_plugin.command
# @lightbulb.add_checks(lightbulb.owner_only)
# @lightbulb.option(
#     "id", "The ID of the channel to create the invite for", str, required=True
# )
# @lightbulb.command("createinvite", description="Creates an invite to a server for support purposes.", auto_defer=True, ephemeral=True)
# @lightbulb.implements(lightbulb.PrefixCommand)
# async def servers(ctx: lightbulb.Context) -> None:
#     invite = await ctx.bot.rest.create_invite(ctx.options.id, max_uses=1, max_age=10, reason="Invite created for support/bot troubleshooting")
#     await ctx.respond(f"<:yes:459224261136220170> **Valid for 10 seconds...** https://discord.gg/{invite.code}")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(bot_plugin)