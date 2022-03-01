from code import interact
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

    def __init__(self, *, timeout: float = 120, autodefer: bool = True) -> None:
        self._inter: miru.Interaction = None
        super().__init__(timeout=timeout, autodefer=autodefer)

    @miru.button(label="Confirm", style=hikari.ButtonStyle.SUCCESS, emoji=hikari.CustomEmoji(id=459224261136220170, name="yes", is_animated=False))
    async def confirm_button(self, button: miru.Button, ctx: miru.Context) -> None:
        self.answer = True
        await self._inter.edit_initial_response(":hourglass: To finish linking, login to My Page and accept the friend request from Burrito. This must be done within 3 minutes.\nOnce done, this message will edit to confirm the link. To cancel, decline the request.\n\nLink to friend requests: <https://wacca.marv-games.jp/web/friend/request/accepting>", components=None)
        self.stop()

    @miru.button(label="Cancel", style=hikari.ButtonStyle.DANGER, emoji=hikari.CustomEmoji(id=442206260151189518, name="no", is_animated=False))
    async def cancel_button(self, button: miru.Button, ctx: miru.Context) -> None:
        self.answer = False
        await self._inter.edit_initial_response("<:no:442206260151189518> Profile link cancelled.", components=None, embed=None, replace_attachments=True)
        self.stop()

    async def on_timeout(self) -> None:
        self.answer = False
        await self._inter.edit_initial_response(content="<:no:442206260151189518> Profile link timed out.", components=None, embed=None, replace_attachments=True)

@cw_plugin.command
@lightbulb.add_cooldown(length=30, uses=1, bucket=lightbulb.UserBucket)
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
    view._inter = ctx.interaction
    proxy = await ctx.respond(
            ":hourglass: Please confirm that this is the profile you want to link.", embed=embed, components=view.build()
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
                    await ctx.interaction.edit_initial_response("<:yes:459224261136220170> This profile has been linked!")
                    break
                else:
                    await ctx.interaction.edit_initial_response("<:no:442206260151189518> Profile link cancelled.", embed=None, replace_attachments=True)
                    break
            else:
                await asyncio.sleep(10)
        else:
            await pageManager.cancelFriendRequest(ctx.bot, ctx.options.friendcode)
            await ctx.edit_last_response("<:no:442206260151189518> Profile link timed out.", embed=None, replace_attachments=True)

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