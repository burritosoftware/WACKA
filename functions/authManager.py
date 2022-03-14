import aiohttp
import functions.dataManager as dataManager

baseurl = "https://wacca.marv-games.jp"
headers = {'Connection': 'keep-alive', 'Host': 'wacca.marv-games.jp', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.39', 'Referer': baseurl}

async def loginWithAimeID(bot, aimeID):
    table = await dataManager.tableLookup(bot, 'cookie')
    data = aiohttp.FormData({'aimeId': aimeID}, quote_fields=False, charset='utf-8')
    async with bot.d.aio_session.post(
        baseurl + "/web/login/exec",
        data=data,
        headers=headers,

    ) as response:
        if response.status == 200:
            cookie = response.cookies.get('WSID').value
            await dataManager.tableUpdate(table, dict(key='session_id', value=cookie), ['key'])
            return(True)
        else:
            return(False)

async def logout(bot):
    table = await dataManager.tableLookup(bot, 'cookie')
    cookie = await dataManager.findKey(table, 'session_id')
    cookies = {'WSID': cookie['value'], 'WUID': cookie['value']}
    async with bot.d.aio_session.post(
        baseurl + "/web/logout",
        headers=headers,
        cookies=cookies

    ) as response:
        if response.status == 200:
            return(True)
        else:
            return(False)

async def getRequestText(bot, suffix):
    table = await dataManager.tableLookup(bot, 'cookie')
    cookie = await dataManager.findKey(table, 'session_id')
    cookies = {'WSID': cookie['value'], 'WUID': cookie['value']}
    async with bot.d.aio_session.get(
        baseurl + suffix,
        headers=headers,
        cookies=cookies

    ) as response:
        if response.status == 200:
            cookie = response.cookies.get('WSID').value
            await dataManager.tableUpdate(table, dict(key='session_id', value=cookie), ['key'])
            return(await response.text())
        else:
            return(False)

async def getRequestData(bot, suffix):
    table = await dataManager.tableLookup(bot, 'cookie')
    cookie = await dataManager.findKey(table, 'session_id')
    cookies = {'WSID': cookie['value'], 'WUID': cookie['value']}
    async with bot.d.aio_session.get(
        baseurl + suffix,
        headers=headers,
        cookies=cookies

    ) as response:
        if response.status == 200:
            return(await response.read())
        else:
            return(False)

async def postRequestText(bot, suffix, data):
    table = await dataManager.tableLookup(bot, 'cookie')
    cookie = await dataManager.findKey(table, 'session_id')
    cookies = {'WSID': cookie['value'], 'WUID': cookie['value']}
    async with bot.d.aio_session.post(
        baseurl + suffix,
        data=data,
        headers=headers,
        cookies=cookies

    ) as response:
        if response.status == 200:
            cookie = response.cookies.get('WSID').value
            await dataManager.tableUpdate(table, dict(key='session_id', value=cookie), ['key'])
            return(await response.text())
        else:
            return(False)

async def postRequestStatus(bot, suffix, data):
    table = await dataManager.tableLookup(bot, 'cookie')
    cookie = await dataManager.findKey(table, 'session_id')
    cookies = {'WSID': cookie['value'], 'WUID': cookie['value']}
    async with bot.d.aio_session.post(
        baseurl + suffix,
        data=data,
        headers=headers,
        cookies=cookies

    ) as response:
        if response.status == 200:
            cookie = response.cookies.get('WSID').value
            await dataManager.tableUpdate(table, dict(key='session_id', value=cookie), ['key'])
            return(True)
        else:
            return(False)