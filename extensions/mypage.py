import hikari
import lightbulb
import miru
import asyncio
import functions.pageManager as pageManager
import functions.dataManager as dataManager

cw_plugin = lightbulb.Plugin("My Page")

async def addOrUpdateUser(bot, id, friendcode) -> None:
    table = await dataManager.tableLookup(bot, 'user')
    user = await dataManager.findUser(table, id)
    if user == None:
        await dataManager.tableInsert(table, dict(id=id, friendcode=friendcode))
        return(True)
    else:
        await dataManager.tableUpdate(table, dict(id=id, friendcode=friendcode), ['id'])
        return(False)

class ConfirmView(miru.View):

    @miru.button(label="Confirm", style=hikari.ButtonStyle.SUCCESS, emoji=hikari.CustomEmoji(id=459224261136220170, name="yes", is_animated=False))
    async def basic_button(self, button: miru.Button, ctx: miru.Context) -> None:
        self.answer = True
        for c in self.children:
            c.disabled = True
        await ctx.edit_response(components=self.build())
        await ctx.respond("To finish linking, go to My Page and accept the request from Burrito. This must be done within 3 minutes.\nOnce done, you'll receive a confirmation message within a couple seconds. To cancel, decline the request.\n\nLink to Friend Requests: <https://wacca.marv-games.jp/web/friend/request/accepting>", flags=hikari.MessageFlag.EPHEMERAL)
        self.stop()

    @miru.button(label="Cancel", style=hikari.ButtonStyle.DANGER, emoji=hikari.CustomEmoji(id=442206260151189518, name="no", is_animated=False))
    async def stop_button(self, button: miru.Button, ctx: miru.Context) -> None:
        self.answer = False
        for c in self.children:
            c.disabled = True
        await ctx.edit_response(components=self.build())
        await ctx.respond("<:no:442206260151189518> Account link cancelled.", flags=hikari.MessageFlag.EPHEMERAL)
        self.stop()

    async def on_timeout(self) -> None:
        self.answer = False
        for c in self.children:
            c.disabled = True
        # await self.message.edit(components=self.build())

@cw_plugin.command
@lightbulb.add_cooldown(length=20, uses=1, bucket=lightbulb.UserBucket)
@lightbulb.option(
    "friendcode", "The friend code of the profile to link", str, required=True
)
@lightbulb.command("linkprofile", description="Links a WACCA profile to your Discord account.", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def linkprofile(ctx: lightbulb.Context) -> None:
    res = await pageManager.getFriendInformation(ctx.bot, ctx.options.friendcode)
    if res == None:
        await ctx.respond("<:no:442206260151189518> This friend code is invalid.")
    else:
        embed = await pageManager.createFriendEmbed(ctx.bot, res[0], res[1], ctx.options.friendcode)
    view = ConfirmView(timeout=20.0)
    proxy = await ctx.respond(
            "Please confirm that this is the account you want to link.", embed=embed, components=view.build()
        )
    
    view.start(await proxy.message())  # Start listening for interactions
    await view.wait()
    if view.answer == True:
        await pageManager.sendFriendRequest(ctx.bot, ctx.options.friendcode)
        for i in range(18):
            if await pageManager.getRequestStatus(ctx.bot, ctx.options.friendcode) == False:
                if await pageManager.getFriendedStatus(ctx.bot, ctx.options.friendcode) == True:
                    await pageManager.unfriend(ctx.bot, ctx.options.friendcode)
                    await addOrUpdateUser(ctx.bot, ctx.author.id, ctx.options.friendcode)
                    await ctx.respond("<:yes:459224261136220170> Your account has been linked!")
                    break
                else:
                    await ctx.respond("<:no:442206260151189518> Account link cancelled.")
                    break
            else:
                await asyncio.sleep(10)
        else:
            await pageManager.cancelFriendRequest(ctx.bot, ctx.options.friendcode)
            await ctx.respond("<:no:442206260151189518> Account link timed out.")

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