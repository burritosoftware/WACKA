import hikari
import aiohttp
import functions.authManager as authManager
from bs4 import BeautifulSoup
import aiofiles
from aiofiles import os as aiofiles_os
from aiofiles import ospath as aiofiles_ospath
import os

async def getFriendInformation(bot, friendCode):
    data = aiohttp.FormData({'friendCode': friendCode}, quote_fields=False, charset='utf-8')
    response = await authManager.postRequestText(bot, '/web/friend/find/result', data)
    if "プレイヤーが見つかりません" in response:
        return(None)
    else:
        return(response)

async def getRequestStatus(bot, friendCode):
    response = await authManager.getRequestText(bot, '/web/friend/request/applying')
    soup = BeautifulSoup(response, "html.parser")
    requests = soup.find_all("div", class_="user-info__detail__req-cancel")
    if requests == []:
        return(False)

    for friend in requests:
        if friend['data-friend-code'] == friendCode:
            return(True)
    else:
        return(False)

async def getFriendedStatus(bot, friendCode):
    response = await authManager.getRequestText(bot, '/web/friend/list')
    soup = BeautifulSoup(response, "html.parser")
    friends = soup.find_all("div", class_="friend__playerdata")
    if friends == []:
        return(False)

    for friend in friends:
        if friend.find("form").find("input")['value'] == friendCode:
            return(True)
    else:
        return(False)

async def sendFriendRequest(bot, friendCode):
    data = aiohttp.FormData({'friendCode': friendCode}, quote_fields=False, charset='utf-8')
    response = await authManager.postRequestStatus(bot, '/web/friend/find/request', data)
    return(response)

async def cancelFriendRequest(bot, friendCode):
    data = aiohttp.FormData({'friendCode': friendCode}, quote_fields=False, charset='utf-8')
    response = await authManager.postRequestStatus(bot, '/web/friend/request/cancelApply', data)
    return(response)

async def unfriend(bot, friendCode):
    data = aiohttp.FormData({'friendCode': friendCode}, quote_fields=False, charset='utf-8')
    response = await authManager.postRequestStatus(bot, '/web/friend/player/cancel', data)
    return(response)

async def downloadFile(bot, path):
    if os.name != "nt":
        workingDir = os.getcwd() + '/cache'
        localCache = workingDir + path
    else:
        workingDir = os.getcwd() + '\\cache'
        localCache = workingDir + path.replace('/', '\\')
    localCacheDir = os.path.dirname(localCache)
    if not await aiofiles_ospath.exists(localCacheDir):
        await aiofiles_os.makedirs(localCacheDir)
    if not await aiofiles_ospath.exists(localCache):
        file = await authManager.getRequestData(bot, path)
        localCachedFile = await aiofiles.open(localCache, mode='wb')
        await localCachedFile.write(file)
        await localCachedFile.close()
        return(file)
    else:
        file = await aiofiles.open(localCache, mode='rb')
        bytes = await file.read()
        await file.close()
        return(bytes)

async def createFriendEmbed(bot, res, friendcode):
    soup = BeautifulSoup(res, "html.parser")
    friendname = soup.find_all("div", class_="user-info__detail__name")[0].text
    friendtitle = soup.find_all("div", class_="user-info__detail__title")[0].text
    friendlevel = soup.find_all("div", class_="user-info__detail__lv")[0].find("span").text.removeprefix('Lv.')
    friendicon = hikari.Bytes(await downloadFile(bot, soup.find_all("div", class_="icon__image")[0].find("img")['src']), 'icon.png')
    friendcolor = hikari.Bytes(await downloadFile(bot, soup.find_all("div", class_="symbol__color__base")[0].find("img")['src']), 'color.png')
    embed = (
        hikari.Embed(
            title=friendname,
            description=friendtitle,
            colour=0x5822B9
        )
        .set_thumbnail(friendicon)
        .set_author(name=friendcode, icon=friendcolor)
        .add_field("Level", friendlevel, inline=True)
        
        
    )
    return(embed)