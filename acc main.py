import json
import time
import datetime
from dhooks.utils import alias
import discord
from discord import user
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import requests
from discord.utils import get
from pymongo import MongoClient
from dhooks import Embed, Webhook

client = MongoClient("")  # account seller mongo connection string
db = client.accountseller

client = MongoClient("")  # payment verification mongo connection string
tb = client.karmabot


# =============================================
try:
    error_hook = Webhook(
        "https://discordapp.com/api/webhooks/732260568819302437/pe6axlXaWot5UetnofDFYD78u4bagX_jsm8xrvzhBeqOsOyFPLhsFFFkfjLV3rYUsvK_")
    dm_hook = Webhook(
        "https://discordapp.com/api/webhooks/733811550166581298/XzHHZaUA55XyWWIKuyW5VavW5H_KB2OVMLd6bIolMld2Tt5iWMjjg9OSZhqcO5esQpad")
    numberlogshook = Webhook(
        "https://discordapp.com/api/webhooks/738702685313695774/Tj1sYObjvsMPbElEO1BaGRoieNGEp_FyzHXQ3SGzI-0pgDXdrsqZd1CA4_rFiDZQduna")
    transactionlogshook = Webhook(
        "https://discordapp.com/api/webhooks/738702947051110461/o-WfdLgGJ5plfk2yG6fUGyMubbqAuVCYJnyeOqmd8mKKX5195FJfNmpE5jpnHxFVlHuN")
    commandslogshook = Webhook(
        "https://discordapp.com/api/webhooks/738747911143424010/x5aT25Oz8Q96CnFtCWAaPkAqStet03buK7pnIH_cQh8jTfJRVq_Pv8Za9E4ZQJqSJvh-")
except Exception:
    error_hook = Webhook(
        "https://discord.com/api/webhooks/732260568819302437/pe6axlXaWot5UetnofDFYD78u4bagX_jsm8xrvzhBeqOsOyFPLhsFFFkfjLV3rYUsvK_")
    dm_hook = Webhook(
        "https://discord.com/api/webhooks/733811550166581298/XzHHZaUA55XyWWIKuyW5VavW5H_KB2OVMLd6bIolMld2Tt5iWMjjg9OSZhqcO5esQpad")
    numberlogshook = Webhook(
        "https://discord.com/api/webhooks/738702685313695774/Tj1sYObjvsMPbElEO1BaGRoieNGEp_FyzHXQ3SGzI-0pgDXdrsqZd1CA4_rFiDZQduna")
    transactionlogshook = Webhook(
        "https://discord.com/api/webhooks/738702947051110461/o-WfdLgGJ5plfk2yG6fUGyMubbqAuVCYJnyeOqmd8mKKX5195FJfNmpE5jpnHxFVlHuN")
    commandslogshook = Webhook(
        "https://discord.com/api/webhooks/738747911143424010/x5aT25Oz8Q96CnFtCWAaPkAqStet03buK7pnIH_cQh8jTfJRVq_Pv8Za9E4ZQJqSJvh-")


# =============================================
botprefix = "--"
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=botprefix, intents=intents)
bot.remove_command('help')
embedtext = "Made by The Unfortunate Guy#7835 |"
embedurl = None
embedcolor = 0xf05b5b

admins = [499278166347743233, 436513875744129025]
sellers = [663057571476930569, 499278166347743233, 436513875744129025]
blockedUsers = []
user_active = []

#priceList = {"Amazon Prime":30,"Vyper VPN":25,"Zee5 Premium 6 Month":90}
#sellerPriceList = {"Amazon Prime":7,"Vyper VPN":6,"Zee5 Premium 6 Month":60}
commandValues = {"give": True, "buy": True, "purchase": True}

# =============================================

transactionLogChannelId = 775626318888304642
orderLogChannelId = 775626292544405557
commandLogChannelId = 775802028898779146
deliveryLogChannelId = 775626386555142165
refundLogChannelId = 775626191649898517
# =============================================


def addToActive(userid):
    global user_active
    if userid not in user_active:
        user_active.append(userid)
    return


def removeFromActive(userId):
    global user_active
    if userId in user_active:
        user_active.remove(userId)
    return


def update_points(user_id, points):
    data = {"$set": {"points": int(points)}}
    response = db['user_database'].find_one_and_update(
        {'user_id': str(user_id)}, update=data, upsert=True)
    return response


def get_last_request():
    data = {'query': "lastRequestNumber"}
    lastNumber = tb['config'].find_one(data)["Number"]
    return lastNumber


def getTime():
    currenttime = datetime.datetime.utcnow()
    currentdate = currenttime + datetime.timedelta(hours=5.5)
    return currentdate


def addTransactionLogs(user_id, transactionId, points):
    lastNumber = get_last_request()
    newNumber = lastNumber+1
    currenttime = getTime()
    data = {"LogType": "transaction", "requestNumber": newNumber, "transactionId": str(
        transactionId), "points": str(points), "userid": str(user_id), "time": currenttime}
    response = tb['numberLogs'].insert_one(data)
    update = {"$set": {"Number": newNumber}}
    tb['config'].find_one_and_update(
        {'query': "lastRequestNumber"}, update=update, upsert=True)
    return newNumber


def addToPendings(amount, sellerAmount):
    data = {"configType": "pendingAmount"}
    response = db['config'].find_one(data)
    pendingRetails = response['pendingRetails']
    pendingSeller = response['pendingSeller']
    update = {"$set": {"pendingRetails": pendingRetails +
                       amount, "pendingSeller": pendingSeller+sellerAmount}}
    db['config'].find_one_and_update(data, update=update, upsert=True)


def update_counts():
    data = {'method': 'counts'}
    countData = db['config'].find_one(data)
    data = {"$set": {"soldCounts": countData['soldCounts']+1}}
    response = db['config'].find_one_and_update(
        {'method': 'counts'}, update=data, upsert=True)

    db['configs']


def checkAdmin(userid):
    if userid in admins:
        return True
    else:
        return False


def checkChannel(ctx):
    if ctx.message.channel.type != discord.ChannelType.private:
        return False
    return True


def check_profile(userId):
    data = {'user_id': str(userId)}
    response = db['user_database'].find_one(data)
    if not response:
        new_profile = {'user_id': str(userId), 'points': 0}
        db['user_database'].insert_one(new_profile)
        response = db['user_database'].find_one(data)
    return response


def checkPayment(transactiondId, number, amount):
    date = datetime.datetime.utcnow()+datetime.timedelta(hours=5.5)
    number = str(number)
    url = "https://dashboard.paytm.com/api/v2/order/list"
    headers = {}  # paytm merchant headers
    payload = {"bizTypeList": ["ACQUIRING", "SPLIT_PAYMENT"], "pageSize": 10,
               "pageNum": 1, "merchantTransId": str(transactiondId), "isSort": True}
    try:
        data = {"transactionId": str(transactiondId)}
        trandata = tb['transactions'].find_one(data)
        if trandata:
            return {"error": "not match"}
    except Exception as e:
        print(e)
        return {"error": "There was an error while processing your request, please contact the developer!"}
    response = requests.post(url, headers=headers, json=payload).json()
    orders = response.get('orderList')
    if not orders:
        print(response)
        return {"error": "not match"}
        #print(f"[Line 131] There was an error while processing your request, please contact the developer!")
        # return {"error":"There was an error while processing your request, please contact the developer!"}
    for order in orders:
        tid = order['merchantTransId']
        tnum = order.get('oppositePhone')
        fraudNum = ["9173346419", "9537599185"]
        if tnum is not None:
            for num in fraudNum:
                if tnum[:2] == num[:2] and tnum[6:] == num[6:]:
                    return {"error": "fruad"}
        tamount = int(order['payMoneyAmount']['value'])//100
        if tid == str(transactiondId) and tamount == int(amount):
            print("Payment is verified successfully")
            return {"error": None, "tamount": tamount}
    return {"error": "not match"}


def addLogs(logType=None, logData=None):
    lastNumber = get_last_request()
    newNumber = lastNumber+1
    currenttime = getTime()
    data = {}
    if logType == "purchaseAccount":
        data = {"logType": "purchaseAccount", "productType": logData['productType'], "time": currenttime, "isRefunded": False, "refundedTime": None, "lastUpdated": currenttime,
                "soldAtPrice": logData['soldAtPrice'],
                "soldAtSellerPrice": logData['soldAtSellerPrice'], "userId": logData['userId'],
                "orderNumber": newNumber,
                "isDelivered": False,
                "deliveredTime": None,
                }
    db['logs'].insert_one(data)
    update = {"$set": {"Number": newNumber}}
    tb['config'].find_one_and_update(
        {'query': "lastRequestNumber"}, update=update, upsert=True)

    return newNumber


async def addCommandLog(ctx, logType, data=None):
    channel = bot.get_channel(commandLogChannelId)
    if ctx.message.channel.type == discord.ChannelType.private:
        await channel.send(f"**{ctx.message.author} ({ctx.message.author.id})** used ``{logType}`` command at DM.")
    else:
        await channel.send(f"**{ctx.message.author} ({ctx.message.author.id})** used ``{logType}`` command at {ctx.message.channel.mention}.")


def getProducts():
    data = {"configType": "priceList"}
    products = db["config"].find_one(data)['priceList']
    return products


def updateProducts(productList):
    data = {"configType": "priceList"}
    update = {"$set": {"priceList": productList}}
    db['config'].find_one_and_update(data, update=update, upsert=True)


@bot.event
async def on_ready():
    print("Bot is Online")
    print(discord.__version__)


@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Help Menu", description=f"Bot prefix is ``{botprefix}``.", color=embedcolor)
    embed.add_field(name=f"{botprefix}buy",
                    value="Load Points to your profile.", inline=False)
    embed.add_field(name=f"{botprefix}give <user> <points>",
                    value="Give points to a discord User.", inline=False)
    embed.add_field(name=f"{botprefix}prices",
                    value="Displays a list of all available product and their prices.", inline=False)
    embed.add_field(name=f"{botprefix}purchase",
                    value="Purchase a product.", inline=False)
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
    embed.add_field(name=f"{botprefix}partners",
                    value="Get link to our Partner Servers.", inline=False)

    await ctx.send(embed=embed)


@bot.command(aliases=['Partners', "partner", "Partner"])
async def partners(ctx):
    description = '''**Inferno**: [Join Now](https://discord.gg/kYyh2zC)

    **Inferno Accounts:** [Join Now](https://discord.gg/DFEUUCgr8X)

    **Inferno Lives:** [Join Now](https://discord.gg/dRH864UX5c)

    **Exclusive Number Bot:** [Join Now](https://discord.gg/7DpXZJSMsQ)
    '''
    embed = discord.Embed(title="Inferno Partners",
                          description=description, color=embedcolor)
    embed.set_thumbnail(url=f"{bot.user.avatar_url}")
    embed.set_footer(text=embedtext, icon_url=f"{bot.user.avatar_url}")
    await ctx.send(embed=embed)


@bot.command()
async def uprice(ctx, pid=None, sprice=None, rprice=None):
    if checkAdmin(ctx.author.id) is False:
        return
    try:
        await ctx.message.delete()
    except Exception:
        pass
    if not sprice or not rprice or not pid:
        await ctx.send(f"**Correct Use:** ``{botprefix}uprice <product id> <seller price> <retail price>``")
        return
    try:
        sprice = int(sprice)
        rprice = int(rprice)
        pid = int(pid)
    except Exception:
        await ctx.send(f"**Correct Use:** ``{botprefix}uprice <product id> <seller price> <retail price>``")
        return
    data = {"configType": "priceList"}
    products = getProducts()
    newProducts = products.copy()
    found = False
    foundProduct = None
    for product in products:
        if product['id'] != pid:
            continue
        found = True
        foundProduct = product
        break
    if found is False:
        await ctx.send(f"Invalid Product ID: {pid}")
        return
    newProducts.remove(foundProduct)
    foundProduct['sprice'] = sprice
    foundProduct['rprice'] = rprice
    newProducts.append(foundProduct)
    updateProducts(newProducts)
    await ctx.send(f"**Successfully Updated {foundProduct['name']}!**")


@bot.command()
async def ustock(ctx, pid=None, instock: bool = None):
    print(instock)
    if checkAdmin(ctx.author.id) is False:
        return
    try:
        await ctx.message.delete()
    except Exception:
        pass
    if not pid or instock is None:
        await ctx.send(f"**Correct Use:** ``{botprefix}ustock <product id> <true/false>``")
        return
    try:
        pid = int(pid)
    except Exception:
        await ctx.send(f"**Correct Use:** ``{botprefix}ustock <product id> <true/false>``")
    data = {"configType": "priceList"}
    products = getProducts()
    newProducts = products.copy()
    found = False
    foundProduct = None
    if instock is True:
        value = "in Stock!"
    else:
        value = "out of stock!"
    for product in products:
        if product['id'] != pid:
            continue
        found = True
        if product['isInStock'] == instock:
            await ctx.send(f"**{product['name']} is already {value}**")
            return
        foundProduct = product
        break
    if found is False:
        await ctx.send(f"**Invalid Product ID:** ``{pid}``")
        return
    newProducts.remove(foundProduct)
    foundProduct['isInStock'] = instock
    newProducts.append(foundProduct)
    updateProducts(newProducts)
    await ctx.send(f"**{foundProduct['name']} is now {value}**")


@ustock.error
async def ustock_error(ctx, error):
    if isinstance(error, commands.BadBoolArgument):
        await ctx.message.delete()
        await ctx.send(f"**Invalid Value: It must be true/false.**")


@bot.command()
async def plist(ctx):
    if checkAdmin(ctx.author.id) is False:
        return
    try:
        await ctx.message.delete()
    except Exception:
        pass
    products = getProducts()
    description = ""
    for product in products:
        description += f"\n\n**{product['name']}:** {product['id']}"
    embed = discord.Embed(title="Product List",
                          description=description, color=embedcolor)
    embed.set_thumbnail(url=ctx.author.avatar_url)
    embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
    await ctx.send(embed=embed)


@bot.command(aliases=['stock'])
async def prices(ctx):
    priceList = getProducts()
    description = ""
    for product in priceList:
        isAvailable = ""
        isInStock = product['isInStock']
        if isInStock is False:
            isAvailable = "[Out of Stock]"
        description += f"\n\n**{product['name']}:** ₹{product['rprice']} {isAvailable}"
    embed = discord.Embed(
        title="Prices", description=description, color=embedcolor)
    embed.set_thumbnail(url=ctx.author.avatar_url)
    embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
    await ctx.send(embed=embed)


@bot.command(aliases=['point', 'Points', 'Point'])
async def points(ctx, user: discord.Member = None):
    if not user:
        user = ctx.message.author
    user_id = user.id
    profile = check_profile(user_id)
    user_points = profile['points']
    embed = discord.Embed(title=f"{user.name}'s Profile", color=embedcolor)
    embed.add_field(name="Points:", value=user_points)
    embed.set_footer(text=embedtext, icon_url=user.avatar_url)
    embed.set_thumbnail(url=user.avatar_url)
    await ctx.send(embed=embed)


@points.error
async def point_error(ctx, error):
    if isinstance(error, commands.errors.MemberNotFound):
        await ctx.send("**Member not found!**")


@bot.command()
async def aetgrgewyg(ctx):
    if checkAdmin is False:
        return
    description = '''**Q. What is <@775793137976344601> ?**
    Inferno Accounts is a Accounts selling bot, with which you can purchase multiple accounts like VPN and OTT platform accounts.
    
    **Q. How can i load points?**
    Use command ``-buy`` to load points.

    **Q. How long purchased accounts are valid?**
    We take process accounts when we receive order, so you can expect a month validity (or whatever the service offers).
    
    **Q. What if my Account is expired before the expiry?**
    We offer 20 days refund policy only if- Account is expired and cannot be fixed. Keep in mind we only do refunds in bot points.

    **Q. Are purchases instant?**
    No they are not! We offer validity as per the subscription plans, so there will be some hours delay to process your orders.

    **Q. Are accounts password changeable?**
    Absolutely YES. Accounts are made for private use so you can change password as well.

    **Q. How can i purchase my desired account?**
    Hover to <#775798955714936872> channel , i had explained it!

    **Q. How can i get help?**
    You can open a instant ticket from <#775627382601547776>. Our support team will be happy to answer your questions.
    '''
    embed = discord.Embed(title="Frequently Asked Questions",
                          description=description, color=embedcolor)
    embed.set_footer(text="© Inferno Accounts 2020",
                     icon_url=bot.user.avatar_url)
    await ctx.send(embed=embed)


@bot.command()
async def purchase(ctx):
    if ctx.message.channel.type != discord.ChannelType.private:
        await ctx.send("**Sorry, this command can only be used in DMs!**")
        return
    if ctx.author.id in user_active:
        await ctx.send("Sorry, you are on a cooldown!")
        return
    await addCommandLog(ctx, "purchase")
    userId = ctx.author.id
    addToActive(userId)
    profile = check_profile(userId)
    userPoints = profile['points']
    priceList = getProducts()
    print(priceList)
    description = ""
    while True:
        for product in priceList:
            isAvailable = ""
            isInStock = product['isInStock']
            if isInStock is False:
                isAvailable = "[Out of Stock]"
            description += f"\n\n**{product['name']}:** ₹{product['rprice']} {isAvailable}"
        description += "\n\n_**Please write below the full name of the product you wants to purchase**\n(You can cancel anytime write ``cancel`` to cancel the request)_"
        embed = discord.Embed(
            title="Purchase", description=description, color=embedcolor)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
        msg = await ctx.send(embed=embed)

        def check(message):
            return message.author == ctx.author
            if message.author == ctx.author:
                return message.channel.type == discord.ChannelType.private
        try:
            uProduct = await bot.wait_for("message", timeout=60, check=check)
            uProduct = uProduct.content
            if uProduct.lower().startswith("cancel"):
                embed = discord.Embed(
                    title="Purchase", description="**Your request has been cancelled Successfully!**", color=embedcolor)
                embed.set_thumbnail(url=ctx.author.avatar_url)
                embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
                await msg.edit(embed=embed)
                removeFromActive(userId)
                return
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="Purchase", description="**You failed to respond within time.**", color=embedcolor)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
            await msg.edit(embed=embed)
            removeFromActive(userId)
            return
        found = None
        for product in priceList:
            if product['name'].lower() == uProduct.lower():
                if product['isInStock'] is False:
                    embed = discord.Embed(
                        title="Purchase", description=f"**Sorry, The product you are trying to purchase is currently out of stock!**", color=embedcolor)
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    embed.set_footer(
                        text=embedtext, icon_url=bot.user.avatar_url)
                    await ctx.send(embed=embed)
                    removeFromActive(userId)
                    return
                found = product
                break
        if not found:
            embed = discord.Embed(
                title="Purchase", description=f"**Sorry, theres no product named ``{uProduct}``. Please try again!**", color=embedcolor)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
            await ctx.send(embed=embed)
            removeFromActive(userId)
            return
        break
    if found['rprice'] > userPoints:
        embed = discord.Embed(
            title="Purchase", description=f"**Sorry, You dont have enough points to purchase {found['name']}.**", color=embedcolor)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
        await ctx.send(embed=embed)
        removeFromActive(userId)
        return
    isInstant = found['isInstant']
    newPoints = userPoints - found['rprice']
    update_points(userId, newPoints)
    logData = {"productType": found['name'], "soldAtPrice": found['rprice'],
               "soldAtSellerPrice": found['sprice'], "userId": str(userId)}
    response = addLogs(logType="purchaseAccount", logData=logData)
    channel = bot.get_channel(orderLogChannelId)
    embed = discord.Embed(
        title="Purchase Log", description=f"_A new order has been placed by {ctx.author.name}._", color=0x62FF33)
    embed.add_field(name="Order ID:", value=f"{response}", inline=False)
    embed.add_field(name="Product Name:",
                    value=f"{found['name']}", inline=False)
    embed.add_field(name="User ID:", value=f"{userId}", inline=False)
    embed.set_thumbnail(url=ctx.author.avatar_url)
    embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
    await channel.send(embed=embed)
    embed = discord.Embed(title="Order Placed Successfully!",
                          description=f"**Hello {ctx.author.name},\nThis is to confirm that your order of ``{found['name']}`` with order id ``{response}`` has been placed Successfully!** \n_You will receive a DM shortly right after we process your order._", color=0x62FF33)
    embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
    await ctx.send(embed=embed)
    removeFromActive(userId)


@bot.command()  # checking
async def give(ctx, user: discord.Member = None, amount=None):
    command_logs = bot.get_channel(commandLogChannelId)
    if commandValues["give"] is False:
        await ctx.send("**Sorry, this command is disabled!**")
        return
    await addCommandLog(ctx, "give")
    global user_active
    if ctx.message.author.id in blockedUsers:
        await ctx.send("**Sorry, you have been blocked from using this command!**")
        return
    if ctx.message.author.id in user_active:
        await ctx.send("You are on cooldown, please wait till the last command get completed. If you think this is a mistake please open a ticket at our support server.")
        return

    addToActive(ctx.message.author.id)
    if not user:
        await ctx.send(f"Correct use: ``{botprefix}give <user> <points>``")
        removeFromActive(ctx.message.author.id)
        return
    try:
        amount = int(amount)
    except Exception:
        await ctx.send("Invalid Amount Entered!")
        removeFromActive(ctx.message.author.id)
        return
    giver_user = ctx.message.author
    giver_id = giver_user.id
    taker_id = user.id
    if not giver_id in admins:
        giver_profile = check_profile(giver_id)
        if giver_profile['points'] < amount:
            try:
                await ctx.send("Sorry, you don't enough points.")
            except discord.errors.Forbidden:
                if ctx.message.channel.type != discord.ChannelType.private:
                    await ctx.author.send("I can't send message at <#{ctx.message.channel.id}>")
            removeFromActive(ctx.message.author.id)
            return
        if amount < 0:
            await ctx.send("Invalid Amount Entered!")
            removeFromActive(ctx.message.author.id)
            return
        old_points = giver_profile['points']
        new_points = int(old_points) - amount
        update_points(giver_id, new_points)
    taker_profile = check_profile(taker_id)
    taker_points = taker_profile['points']
    new_points = taker_points + amount
    update_points(taker_id, new_points)
    await ctx.send(f"**{giver_user.name}** gave **{amount} points** to **{user.name}**.")
    channel = bot.get_channel(commandLogChannelId)
    await channel.send(f"**{giver_user}** gave ``{amount} points`` to **{user}**.")
    removeFromActive(ctx.message.author.id)


@give.error
async def give_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("**Member not found!**")
    else:
        await error_hook.send(str(error))


@bot.command()
async def take(ctx, user: discord.Member = None, amount=None):
    command_logs = bot.get_channel(commandLogChannelId)
    giver_id = ctx.message.author.id
    if not giver_id in admins:
        await ctx.send("Sorry, you do not have permission to use this command!")
        return

    await addCommandLog(ctx, "take")
    if not user:
        await ctx.send(f"Correct use: ``{botprefix}take <user> <points>``")
        return
    try:
        amount = int(amount)
    except Exception:
        await ctx.send("Invalid Amount Entered!")
        return
    giver_user = ctx.message.author
    giver_id = giver_user.id
    taker_id = user.id

    taker_profile = check_profile(taker_id)
    taker_points = taker_profile['points']
    new_points = taker_points - amount
    update_points(taker_id, new_points)
    await ctx.send(f"**{giver_user.name}** took ``{amount} points`` from **{user.name}**.")
    command_logs.send(
        f"**{giver_user}** took ``{amount} points`` from **{user}**.")


@take.error
async def take_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("**Member not found!**")
    else:
        await error_hook.send(str(error))


@bot.command()
async def stats(ctx):
    totalOrders = db['logs'].count_documents(filter={})
    totalDeliveredOrders = db['logs'].count_documents(
        filter={"isDelivered": True})
    totalRefundedOrders = db['logs'].count_documents(
        filter={"isRefunded": True})
    ordersProcessing = db['logs'].count_documents(
        filter={"isDelivered": False, "isRefunded": False})
    totalRetailEarnedCollection = db['logs'].find(
        filter={"isDelivered": True, "isRefunded": False})
    totalRetailsEarned = 0
    totalSellerEarned = 0
    totalRetailEarnedCollection = list(totalRetailEarnedCollection)
    for i in totalRetailEarnedCollection:
        totalSellerEarned += i['soldAtSellerPrice']
        totalRetailsEarned += i['soldAtPrice']
    embed = discord.Embed(title="Stats", color=embedcolor)
    embed.add_field(name="Total Orders:", value=f"{totalOrders}", inline=False)
    embed.add_field(name="Orders Delivered:",
                    value=f"{totalDeliveredOrders}", inline=False)
    embed.add_field(name="Orders Refunded:",
                    value=f"{totalRefundedOrders}", inline=False)
    embed.add_field(name="Orders Processing:",
                    value=f"{ordersProcessing}", inline=False)
    embed.add_field(name="Retail Earned:",
                    value=f"₹{totalRetailsEarned}", inline=False)
    embed.add_field(name="Seller Earned:",
                    value=f"₹{totalSellerEarned}", inline=False)
    embed.add_field(
        name="Profit:", value=f"₹{totalRetailsEarned-totalSellerEarned}", inline=False)
    embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
    embed.set_thumbnail(url=bot.user.avatar_url)
    await ctx.send(embed=embed)


@bot.command(aliases=['loadp'])
async def buy(ctx):
    user = ctx.author
    if user.id in user_active:
        await ctx.send("_You are on cooldown, please wait till the last command get completed. If you think this is a mistake please open a ticket at our support server._")
        return
    addToActive(user.id)
    await addCommandLog(ctx, "buy")
    if checkChannel(ctx) is False:
        await ctx.send("**Alright, check your DM.**")

    def check(message):
        if message.author == ctx.author:
            return message.channel.type == discord.ChannelType.private
    while True:
        try:
            description = f"Hey {user.name}!\n\n1 Points: ₹1\n\nHow many points do you want to buy?\n_You can also type ``cancel`` to cancel this purchase!_"
            embed = discord.Embed(title="Purchase Points",
                                  description=description, color=embedcolor)
            embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
            embed.set_thumbnail(url=bot.user.avatar_url)
            msg = await user.send(embed=embed)
        except Exception:
            if checkChannel(ctx) is False:
                await ctx.send(f"Sorry {user.mention}, I am unable to DM you!")
                removeFromActive(user.id)
                return
            return
        try:
            userpoints = await bot.wait_for("message", timeout=60, check=check)
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="Purchase Points", description=f"Sorry, you failed to reply within time. You can again start with ``{botprefix}buy``.", color=embedcolor)
            embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
            embed.set_thumbnail(url=bot.user.avatar_url)
            await msg.edit(embed=embed)
            removeFromActive(user.id)
            return
        if userpoints.content.lower() == "cancel":
            embed = discord.Embed(
                title="Purchase Points", description=f"Your request is cancelled!", color=0xff073a)
            embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
            embed.set_thumbnail(url=bot.user.avatar_url)
            await msg.edit(embed=embed)
            removeFromActive(user.id)
            return
        try:
            amount = int(userpoints.content)
            break
        except Exception:
            embed = discord.Embed(
                title="Purchase Points", description="The amount you entered is invalid! Please try again.", color=0xff073a)
            embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
            embed.set_thumbnail(url=bot.user.avatar_url)
            await msg.edit(embed=embed)
            continue
    while True:
        description = "Please enter your mobile number ``98xxxxx207`` (we do care about your privacy your number is only stored to the bot till the end of the transaction)."
        embed = discord.Embed(title="Points Purchase",
                              description=description, color=embedcolor)
        embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
        embed.set_thumbnail(url=bot.user.avatar_url)
        msg = await user.send(embed=embed)
        try:
            number = await bot.wait_for("message", timeout=60, check=check)
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="Purchase Points", description=f"Sorry, you failed to reply within time. You can again start with ``{botprefix}buy``.", color=embedcolor)
            embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
            embed.set_thumbnail(url=bot.user.avatar_url)
            await msg.edit(embed=embed)
            removeFromActive(user.id)
            return
        if number.content.lower() == "cancel":
            embed = discord.Embed(
                title="Purchase Points", description=f"Your request is cancelled!", color=0xff073a)
            embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
            embed.set_thumbnail(url=bot.user.avatar_url)
            await msg.edit(embed=embed)
            removeFromActive(user.id)
            return
        try:
            if len(number.content) != 10:
                raise Exception
            number = int(number.content)
            break
        except Exception as e:
            embed = discord.Embed(
                title="Purchase Points", description="The number you entered is invalid! Please try again.", color=0xff073a)
            embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
            embed.set_thumbnail(url=bot.user.avatar_url)
            await msg.edit(embed=embed)
            continue
    description = f"Please pay ‎**₹{amount}** to the below QR Code. You have 5 minutes to enter the Order ID, Example: ``202006051709231138``. (If you don't wanna continue right now you can cancel the request with ``cancel``.)"
    embed = discord.Embed(title="Purchase Points",
                          description=description, color=embedcolor)
    embed.set_image(
        url="https://cdn.discordapp.com/attachments/521686905067274240/696430757291360357/1586112417055.jpg")
    embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
    embed.set_thumbnail(url=bot.user.avatar_url)
    msg = await user.send(embed=embed)
    while True:
        try:
            transactiondId = await bot.wait_for("message", timeout=300, check=check)
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="Purchase Points", description=f"Sorry, you failed to reply within time. You can again start with ``{botprefix}buy``.", color=embedcolor)
            embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
            embed.set_thumbnail(url=bot.user.avatar_url)
            await msg.edit(embed=embed)
            removeFromActive(user.id)
            return
        if transactiondId.content.lower() == "cancel":
            embed = discord.Embed(
                title="Purchase Points", description=f"Your request is cancelled!", color=0xff073a)
            embed.set_footer(text=embedtext, icon_url=bot.user.avatar_url)
            embed.set_thumbnail(url=bot.user.avatar_url)
            await msg.edit(embed=embed)
            removeFromActive(user.id)
            return
        try:
            transactiondId = transactiondId.content
            response = checkPayment(transactiondId, number, amount)
        except Exception as e:
            response = {
                "error": "Something Went Wrong! Please try to contact Developer"}
            print(e)
            return
        if response.get("error") == "not match":
            await user.send("**Failed to verify your payment. Make sure you are entering Order ID ``202006051709231138``, if you do Please check once if you had enter the correct order ID and number or have paid the correct amount and enter again. (You can cancel this request with ``cancel``)**")
            continue
        elif response.get("error") == "fraud":
            data = {"transactionId": str(transactiondId)}
            tb['transactions'].insert_one(data)
            await ctx.send("Your order has been flagged as a fraudrant Activity. If you believe this is a mistake open a ticket at our support server!")
            return
        elif response.get("tamount"):
            break
        else:
            await user.send(response['error'])
            continue
    takerId = user.id
    takerProfile = check_profile(takerId)
    takerPoints = takerProfile['points']
    newPoints = takerPoints + int(amount)
    my_amount = response["tamount"]
    update_points(takerId, newPoints)
    data = {"transactionId": str(transactiondId)}
    tb['transactions'].insert_one(data)
    orderId = addTransactionLogs(takerId, str(transactiondId), int(my_amount))
    description = f"Successfully added {my_amount} Points to your account.\n\n**Order ID: ``#{orderId}``**.\n\n_If you have any queries with your order please open a ticket at our support server._"
    embed = discord.Embed(title="Purchase Points",
                          description=description, color=0x62FF33)
    embed.set_thumbnail(url=f"{bot.user.avatar_url}")
    embed.set_footer(text=embedtext, icon_url=f"{bot.user.avatar_url}")
    await user.send(embed=embed)
    embed = Embed(title="Transaction Details", color=0x62FF33)
    embed.add_field(name="Order ID:", value=f"{orderId}", inline=False)
    embed.add_field(name="Payee:", value=f"{user}", inline=False)
    embed.add_field(name="User ID:", value=f"{user.id}", inline=False)
    embed.add_field(name="Amount:", value=f"₹{my_amount}", inline=False)
    embed.add_field(name="Total Points:", value=f"{my_amount}", inline=False)
    embed.add_field(name="Old Points:", value=f"{takerPoints}", inline=False)
    embed.add_field(name="New Points:", value=f"{newPoints}", inline=False)
    embed.add_field(name="Transaction ID:",
                    value=f"{transactiondId}", inline=False)
    embed.set_thumbnail(url=f"{bot.user.avatar_url}")
    embed.set_footer(text=embedtext, icon_url=f"{bot.user.avatar_url}")
    channel = bot.get_channel(transactionLogChannelId)
    await channel.send(embed=embed)
    removeFromActive(user.id)
    return


@bot.command(aliases=['rl', "Rl"])
async def requestlogs(ctx, requestId: int = None, isAdmin=False):
    if checkAdmin(ctx.author.id) is False:
        return
    await ctx.message.delete()
    if not requestId:
        await ctx.send(f"**Correct Use:** ``{botprefix}rl <request id>``")
        return
    response = db['logs'].find_one({"orderNumber": requestId})
    if not response:
        await ctx.send(f"Request ID: ``{requestId}`` not found!")
        return
    userId = response['userId']
    user = get(bot.get_all_members(), id=int(userId))
    productName = response['productType']
    price = response['soldAtPrice']
    isRefunded = response['isRefunded']
    purchasedOn = response['time']
    isDelivered = response['isDelivered']
    embed = Embed(title=f"Purchase Details | #{requestId}", color=0x62FF33)
    embed.add_field(name="User:", value=f"{user}", inline=False)
    embed.add_field(name="User ID:", value=f"{user.id}", inline=False)
    embed.add_field(name="Product Name:", value=f"{productName}", inline=False)
    embed.add_field(name="Price:", value=f"₹{price}", inline=False)
    embed.add_field(name="Purchase on:",
                    value=f"{purchasedOn.day}/{purchasedOn.month}/{purchasedOn.year} at {purchasedOn.hour}:{purchasedOn.minute}", inline=False)
    embed.add_field(name="Refunded:", value=f"{isRefunded}", inline=False)
    embed.add_field(name="Delivered:", value=f"{isDelivered}", inline=False)
    if isRefunded is True:
        refundedOn = response['refundedTime']
        embed.add_field(
            name="Refunded On:", value=f"{refundedOn.day}/{refundedOn.month}/{refundedOn.year} at {refundedOn.hour}:{refundedOn.minute}", inline=False)
    if isDelivered is True:
        deliveredOn = response['deliveredTime']
        embed.add_field(name="Delivered On:",
                        value=f"{deliveredOn.day}/{deliveredOn.month}/{deliveredOn.year} at {deliveredOn.hour}:{deliveredOn.minute}", inline=False)
    if isAdmin is True:
        embed.add_field(name="Seller Price:",
                        value=f"₹{response['soldAtSellerPrice']}", inline=False)

    embed.set_thumbnail(url=f"{bot.user.avatar_url}")

    embed.set_footer(text=embedtext, icon_url=f"{bot.user.avatar_url}")
    await ctx.send(embed=embed)


@requestlogs.error
async def requestlogs_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.message.delete()
        await ctx.send(f"**Invalid Request ID.**")
        return
    if isinstance(error, commands.BadBoolArgument):
        await ctx.message.delete()
        await ctx.send(f"**It must be either true or false.**")


@bot.command()
async def deliver(ctx, orderId=None, product=None, productType=None):
    if ctx.author.id not in sellers:
        return
    await ctx.message.delete()
    if not orderId or not product or not productType:
        await ctx.send(f"**Correct Use:** ``{botprefix}deliver <orderid> <product> <product type>``")
        return
    productTypes = ["account", "promo"]
    if productType.lower() not in productTypes:
        await ctx.send(f"Invalid Product Type: ``{productType}``.")
        return
    try:
        orderId = int(orderId)
    except Exception:
        await ctx.send("Order ID is invalid!")
        return
    data = {"orderNumber": int(orderId)}
    response = db['logs'].find_one(data)
    if not response:
        await ctx.send(f"Order ID: {orderId} doesn't exists!")
        return
    if response['isDelivered'] is True:
        await ctx.send("This order has already been delivered!")
        return
    userId = response['userId']
    user = get(bot.get_all_members(), id=int(userId))
    embed = discord.Embed(
        title="Your Order has been processed!", color=embedcolor)
    embed.add_field(name="Order ID", value=f"{orderId}", inline=False)
    embed.add_field(name="Product Name:",
                    value=f"{response['productType']}", inline=False)
    if productType == "account":
        try:
            email, password = product.split(":")
        except Exception:
            await ctx.send("**Account Type products must be a combo!**")
            return
        embed.add_field(name="Email:", value=f"{email}", inline=False)
        embed.add_field(name="Password:", value=f"{password}", inline=False)
    if productType == "promo":
        embed.add_field(name="Promo Code:", value=f"{product}", inline=False)
    embed.set_thumbnail(url=f"{bot.user.avatar_url}")
    embed.set_footer(text=embedtext, icon_url=f"{bot.user.avatar_url}")
    await user.send(embed=embed)
    currentTime = getTime()
    update = {"$set": {"lastUpdates": currentTime,
                       "isDelivered": True, "deliveredTime": currentTime}}
    db['logs'].find_one_and_update(data, update=update, upsert=True)
    channel = bot.get_channel(deliveryLogChannelId)
    embed = discord.Embed(title="Order Delivered!", color=embedcolor)
    embed.add_field(name="Order ID", value=f"{orderId}", inline=False)
    embed.add_field(name="User ID:", value=f"{userId}", inline=False)
    embed.add_field(name="Product Name:",
                    value=f"{response['productType']}", inline=False)
    if productType == "account":
        embed.add_field(name="Combo:", value=f"{product}", inline=False)
    if productType == "promocode":
        embed.add_field(name="Promo Code:", value=f"{product}", inline=False)
    embed.set_thumbnail(url=f"{bot.user.avatar_url}")
    embed.set_footer(text=embedtext, icon_url=f"{bot.user.avatar_url}")
    await channel.send(embed=embed)
    soldAtPrice = response['soldAtPrice']
    soldAtSellerPrice = response['soldAtSellerPrice']
    amount = soldAtSellerPrice + ((soldAtPrice - soldAtSellerPrice)/2)
    addToPendings(amount, soldAtSellerPrice)
    await ctx.send("**Your order is successfully delivered!**")


@bot.command()
async def refund(ctx, orderId=None):
    if checkAdmin(ctx.author.id) is False:
        return
    await ctx.message.delete()
    if not orderId:
        await ctx.send(f"**Correct Use:** ``{botprefix}refund <orderId>``")
        return
    try:
        orderId = int(orderId)
    except Exception:
        await ctx.send("Order ID is invalid!")
        return
    data = {"orderNumber": int(orderId)}
    response = db['logs'].find_one(data)
    if not response:
        await ctx.send(f"Order ID: {orderId} doesn't exists!")
        return
    userId = response['userId']
    user = get(bot.get_all_members(), id=int(userId))
    productName = response['productType']
    currentTime = getTime()
    update = {"$set": {"lastUpdates": currentTime,
                       "isRefunded": True, "refundedTime": currentTime}}
    db['logs'].find_one_and_update(data, update=update, upsert=True)
    profile = check_profile(userId)
    userPoints = profile['points']
    newPoints = userPoints + response['soldAtPrice']
    update_points(userId, newPoints)
    description = f"Hey {user.name},\n\nYour refund request for order ``{orderId}`` with order ``{productName}`` has been processed and your points are sent back to your profile. We appoligies if any inconvenience caused to you!"
    embed = discord.Embed(title="Your refund request has been processed!",
                          description=description, color=0xDF00FE)
    embed.set_thumbnail(url=f"{bot.user.avatar_url}")
    embed.set_footer(text=embedtext, icon_url=f"{bot.user.avatar_url}")
    await user.send(embed=embed)
    channel = bot.get_channel(refundLogChannelId)
    embed = discord.Embed(title="Order Refunded!", color=0xDF00FE)
    embed.add_field(name="Order ID", value=f"{orderId}", inline=False)
    embed.add_field(name="User ID:", value=f"{userId}", inline=False)
    embed.add_field(name="Product Name:", value=f"{productName}", inline=False)
    embed.set_thumbnail(url=f"{bot.user.avatar_url}")
    embed.set_footer(text=embedtext, icon_url=f"{bot.user.avatar_url}")
    await channel.send(embed=embed)


@bot.command(aliases=['deleteorder', 'removeorder', 'ro'])
async def do(ctx, orderId=None):
    if checkAdmin(ctx.author.id) is False:
        return
    await ctx.message.delete()
    if not orderId:
        await ctx.send(f"**Correct Use:** ``{botprefix}deleteorder <order id>``")
        return
    try:
        orderId = int(orderId)
    except Exception:
        await ctx.send("Order ID is invalid!")
        return
    data = {"orderNumber": int(orderId)}
    response = db['logs'].find_one(data)
    if not response:
        await ctx.send(f"Order ID: {orderId} doesn't exists!")
        return
    db['logs'].delete_one(data)
    await ctx.send(f"Successfully deleted order with order Id ``{orderId}``")


@bot.command()
async def test(ctx, orderId):
    if checkAdmin is False:
        return
    data = {"orderNumber": int(orderId)}
    response = db['logs'].find_one(data)
    soldAtPrice = response['soldAtPrice']
    soldAtSellerPrice = response['soldAtSellerPrice']
    amount = soldAtSellerPrice + ((soldAtPrice - soldAtSellerPrice)/2)
    addToPendings(amount, soldAtSellerPrice)
    await ctx.send("Successfully updated!")


@bot.command()
async def cp(ctx):
    if checkAdmin is False:
        return
    data = {"configType": "pendingAmount"}
    response = db['config'].find_one(data)
    retailsPendings = response['pendingRetails']
    sellerPendings = response['pendingSeller']
    embed = discord.Embed(title="Pendings", color=embedcolor)
    embed.add_field(name="Retail Pendings:",
                    value=f"{retailsPendings}", inline=False)
    embed.add_field(name="Seller Pendings:",
                    value=f"{sellerPendings}", inline=False)
    embed.set_thumbnail(url=f"{bot.user.avatar_url}")
    embed.set_footer(text=embedtext, icon_url=f"{bot.user.avatar_url}")
    await ctx.send(embed=embed)


@bot.command()
async def rp(ctx):
    if checkAdmin is False:
        return
    data = {"configType": "pendingAmount"}
    response = db['config'].find_one(data)
    retailsPendings = response['pendingRetails']
    sellerPendings = response['pendingSeller']
    update = {"$set": {"pendingRetails": 0, "pendingSeller": 0}}
    response = db['config'].find_one_and_update(
        data, update=update, upsert=True)
    await ctx.send(f"Retail Pendings: **₹{retailsPendings}** and Seller Pendings: **{sellerPendings}** is now erased!")


# bot.run("NzU3Mjc1OTg4NjY4NDQ4ODg4.X2eCOQ.Qx7GRw1XAcJl3CstzWV8uaz_ihk") #testbot token
bot.run("Nzc1NzkzMTM3OTc2MzQ0NjAx.X6rfqQ._xyx5dKGJcLzSeLbGSp-e60UcvE")
