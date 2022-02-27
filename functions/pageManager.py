import hikari
import aiohttp
import aiofiles
import functions.dataManager as dataManager
from bs4 import BeautifulSoup

baseurl = "https://wacca.marv-games.jp"
headers = {'Connection': 'keep-alive', 'Host': 'wacca.marv-games.jp', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.62', 'Referer': baseurl}

async def getFriendInformation(bot, friendCode):
    table = await dataManager.tableLookup(bot, 'cookie')
    cookie = await dataManager.findKey(table, 'session_id')
    cookies = {'WSID': cookie['value'], 'WUID': cookie['value']}
    cookieValue = cookie['value']
    data = aiohttp.FormData({'friendCode': friendCode}, quote_fields=True, charset=None)
    async with bot.d.aio_session.post(
        baseurl + "/web/friend/find/result",
        data=data,
        headers=headers,
        cookies=cookies

    ) as response:
        res = await response.text()

        # Writing new cookie's value to the db
        jar = bot.d.aio_session.cookie_jar.filter_cookies(baseurl)
        for key, cookie in jar.items():
            if cookie.key == 'WSID':
                await dataManager.tableUpdate(table, dict(key='session_id', value=cookie.value), ['key'])

        if "プレイヤーが見つかりません" in res:
            return(None)
        else:
            return(res, cookieValue)

async def downloadFile(bot, path, cookie):
    cookies = {'WSID': cookie, 'WUID': cookie}
    async with bot.d.aio_session.get(
        baseurl + path,
        headers=headers,
        cookies=cookies
    ) as response:
        return(await response.read())

async def createFriendEmbed(bot, res, cookie, friendcode):
    soup = BeautifulSoup(res, "html.parser")
    friendname = soup.find_all("div", class_="user-info__detail__name")[0].text
    friendtitle = soup.find_all("div", class_="user-info__detail__title")[0].text
    friendlevel = soup.find_all("div", class_="user-info__detail__lv")[0].find("span").text.removeprefix('Lv.')
    friendicon = hikari.Bytes(await downloadFile(bot, soup.find_all("div", class_="icon__image")[0].find("img")['src'], cookie), 'icon.png')
    friendcolor = hikari.Bytes(await downloadFile(bot, soup.find_all("div", class_="symbol__color__base")[0].find("img")['src'], cookie), 'color.png')
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