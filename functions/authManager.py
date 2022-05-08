import aiohttp
import functions.dataManager as dataManager
import os
import datetime

baseurl = "https://wacca.marv-games.jp"
headers = {'Connection': 'keep-alive', 'Host': 'wacca.marv-games.jp', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.39', 'Referer': baseurl}

async def addOrUpdateCookie(bot, res):
    cookie = res.cookies.get('WSID').value
    expiry = datetime.datetime.strptime(res.cookies.get('WUID')['expires'], "%a, %d-%b-%Y %H:%M:%S GMT").timestamp()
    table = await dataManager.tableLookup(bot, 'cookie')
    session = await dataManager.findKey(table, 'session_id')

    if session == None:
        await dataManager.tableInsert(table, dict(key='session_id', value=cookie))
        await dataManager.tableInsert(table, dict(key='expiry', value=expiry))
    else:
        await dataManager.tableUpdate(table, dict(key='session_id', value=cookie, expiry=expiry), ['key'])
        await dataManager.tableUpdate(table, dict(key='expiry', value=expiry), ['key'])

async def loginWithAimeID(bot):
    data = aiohttp.FormData({'aimeId': os.getenv('AIMEID')}, quote_fields=False, charset='utf-8')
    async with bot.d.aio_session.post(
        baseurl + "/web/login/exec",
        data=data,
        headers=headers,

    ) as response:
        if response.status == 200:
            await addOrUpdateCookie(bot, response)
            return(True)
        else:
            return(False)

async def getCookies(bot):
    table = await dataManager.tableLookup(bot, 'cookie')
    expiry = await dataManager.findKey(table, 'expiry')
    currentTimestamp = datetime.datetime.now().timestamp()
    if currentTimestamp >= float(expiry['value']):
        await loginWithAimeID(bot)
    cookie = await dataManager.findKey(table, 'session_id')
    cookies = {'WSID': cookie['value'], 'WUID': cookie['value']}
    return(cookies)

async def updateCookies(bot, res):
    table = await dataManager.tableLookup(bot, 'cookie')
    cookie = res.cookies.get('WSID').value
    await dataManager.tableUpdate(table, dict(key='session_id', value=cookie), ['key'])
    
async def logout(bot):
    cookies = await getCookies(bot)
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
    cookies = await getCookies(bot)
    async with bot.d.aio_session.get(
        baseurl + suffix,
        headers=headers,
        cookies=cookies

    ) as response:
        if response.status == 200:
            await addOrUpdateCookie(bot, response)
            return(await response.text())
        else:
            return(False)

async def getRequestData(bot, suffix):
    cookies = await getCookies(bot)
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
    cookies = await getCookies(bot)
    async with bot.d.aio_session.post(
        baseurl + suffix,
        data=data,
        headers=headers,
        cookies=cookies

    ) as response:
        if response.status == 200:
            await addOrUpdateCookie(bot, response)
            return(await response.text())
        else:
            return(False)

async def postRequestStatus(bot, suffix, data):
    cookies = await getCookies(bot)
    async with bot.d.aio_session.post(
        baseurl + suffix,
        data=data,
        headers=headers,
        cookies=cookies

    ) as response:
        if response.status == 200:
            await addOrUpdateCookie(bot, response)
            return(True)
        else:
            return(False)