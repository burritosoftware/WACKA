import hikari
import lightbulb
import functions.pageManager as pageManager
import functions.dataManager as dataManager

async def addOrUpdateUser(bot, id, friendcode) -> None:
    table = await dataManager.tableLookup(bot, 'user')
    user = await dataManager.findUser(table, id)
    if user == None:
        await dataManager.tableInsert(table, dict(id=id, friendcode=friendcode))
        return(True)
    else:
        await dataManager.tableUpdate(table, dict(id=id, friendcode=friendcode), ['id'])
        return(False)

cw_plugin = lightbulb.Plugin("My Page")
@cw_plugin.command
@lightbulb.add_cooldown(length=20, uses=1, bucket=lightbulb.UserBucket)
@lightbulb.option(
    "friendcode", "The friend code to add to the database", str, required=True
)
@lightbulb.command("setfriendcode", description="Sets your friend code to allow others to look up your profile.", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def setfriendcode(ctx: lightbulb.Context) -> None:
    status = await addOrUpdateUser(bot=ctx.bot, id=ctx.author.id, friendcode=ctx.options.friendcode)
    if status:
        await ctx.respond("<:yes:459224261136220170> Added your code to the database!")
    else:
        await ctx.respond("<:yes:459224261136220170> Updated your code in the database!")

@cw_plugin.command
@lightbulb.add_cooldown(length=2, uses=1, bucket=lightbulb.UserBucket)
@lightbulb.option(
    "user", "The user to lookup their WACCA profile", hikari.User, required=True
)
@lightbulb.command("lookup", description="Looks up a user's WACCA profile.", auto_defer=False)
@lightbulb.implements(lightbulb.SlashCommand)
async def lookup(ctx: lightbulb.Context) -> None:
    table = await dataManager.tableLookup(ctx.bot, 'user')
    user = await dataManager.findUser(table, ctx.options.user.id)
    if user != None:
        await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        res = await pageManager.getFriendInformation(ctx.bot, user['friendcode'])
        if res == None:
            await ctx.respond("<:no:442206260151189518> This user's friend code is invalid.")
        else:
            embed = await pageManager.createFriendEmbed(ctx.bot, res[0], res[1], user['friendcode'])
            await ctx.respond(embed)
    else:
        await ctx.respond("<:no:442206260151189518> This user does not have their friend code set.", flags=hikari.MessageFlag.EPHEMERAL)

@cw_plugin.command
@lightbulb.add_cooldown(length=2, uses=1, bucket=lightbulb.UserBucket)
@lightbulb.option(
    "friendcode", "The friend code to search for", str, required=True
)
@lightbulb.command("search", description="Looks up a user's WACCA profile through a friend code.", auto_defer=False)
@lightbulb.implements(lightbulb.SlashCommand)
async def search(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    res = await pageManager.getFriendInformation(ctx.bot, ctx.options.friendcode)
    if res == None:
        await ctx.respond("<:no:442206260151189518> This friend code is invalid.")
    else:
        embed = await pageManager.createFriendEmbed(ctx.bot, res[0], res[1], ctx.options.friendcode)
        await ctx.respond(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(cw_plugin)