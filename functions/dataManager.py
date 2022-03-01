import functools
import asyncio

# Running stuff asynchronously https://github.com/balkierode/assortedscripts/blob/master/python/blockex.py
def run_in_executor(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, lambda: f(*args, **kwargs))
    return inner

# Provide bot from an extension and the table name you want to lookup, and this will look it up and return it
def blockingTableLookup(bot, tablename):
    table = bot.d.db[f'{tablename}']
    return table

# Provide a table, and a dictionary entry to insert, and this will return the inserted table
def blockingTableInsert(table, dict):
    record = table.insert(dict)
    return record

# Provide a table, and a dictionary entry to update, and a filter, and this will return the updated table
def blockingTableUpdate(table, dict, filter):
    record = table.update(dict, filter)
    return record

# Provide a table and a userid, and this will return their object from the db
def blockingFindUser(table, id):
    record = table.find_one(id=id)
    return record

# Provide a table and a userid, and this will delete their object from the db
def blockingDeleteUser(table, id):
    record = table.delete(id=id)
    return record

# Provide a table and a key, and this will return the cookie's object from the db
def blockingFindKey(table, key):
    record = table.find_one(key=key)
    return record

@run_in_executor
def tableLookup(bot, tablename):
    resp = blockingTableLookup(bot, tablename)
    return resp

@run_in_executor
def tableInsert(table, dict):
    resp = blockingTableInsert(table, dict)
    return resp

@run_in_executor
def tableUpdate(table, dict, filter):
    resp = blockingTableUpdate(table, dict, filter)
    return resp

@run_in_executor
def findUser(table, id):
    resp = blockingFindUser(table, id)
    return resp

@run_in_executor
def deleteUser(table, id):
    resp = blockingDeleteUser(table, id)
    return resp

@run_in_executor
def findKey(table, id):
    resp = blockingFindKey(table, id)
    return resp