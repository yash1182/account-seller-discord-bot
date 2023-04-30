import json
import time
from datetime import datetime
import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
from discord.utils import get
from pymongo import MongoClient

client = MongoClient(
    "")  # mongo db connection string
db = client.accountseller

botprefix = "-"
bot = commands.Bot(command_prefix=botprefix)
bot.remove_command('help')
embedtext = "Made by The Unfortunate Guy#7835 |"
embedurl = None
embedcolor = 0xf05b5b

admins = [499278166347743233]


def checkAdmin(userid):
    if userid in admins:
        return True
    else:
        return False


def checkChannel(ctx):
    if ctx.message.channel.type != discord.ChannelType.private:
        return False
    return True


@bot.event
async def on_ready():
    print("Bot is Online")
    print(discord.__version__)


def get_account(service):
    info = {'Type': service}
    response = db['accounts'].find_one(info)
    if response:
        AccountID = response['_id']
        combo = response['combo']
        db['accounts'].delete_one({'_id': AccountID})
        return combo
    return


def update_services(NewService, cost: int):
    data = {"name": NewService, "cost": cost}
    info = {'configType': 'services'}
    services = db['config'].find_one({'configType': "services"})['services']
    print(services)
    if NewService in [service['name'] for service in services]:
        return {'status': 'already Exist'}
    services.append(data)
    update = {'services': services}
    update = {'$set': update}
    response = db['config'].find_one_and_update(
        info, update=update, upsert=True)
    return {'status': 'updated'}


def get_services():
    services = db['config'].find_one({'configType': "services"})
    print(services)
    services = services['services']
    return services


def add_account(service, combo):
    account_details = {'Type': "Nord VPN", 'combo': "test@test.com:thisistest"}
    db['accounts'].insert_one(account_details)


def stock_check(service):
    counts = db['accounts'].count_documents({'Type': service})
    return counts


@bot.command()
async def stock(ctx):
    services = get_services()
    embed = discord.Embed(title="Account Stock", color=embedcolor)
    embed.set_footer(text=embedtext)
    for service in services:
        name = service['name']
        stock = stock_check(name)
        embed.add_field(name=f"**{name}:**", value=f"{stock}", inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Help Menu", description=f"Bot prefix is ``{botprefix}``.", color=embedcolor)
    embed.add_field(name=f"**{botprefix}nord**",
                    value="generates a nord premium account for you.", inline=False)
    # embed.add_field(name=f"{botprefix}",value="",inline=False)
    embed.set_footer(text=embedtext)
    await ctx.send(embed=embed)


@bot.command()
async def addservice(ctx, cost: int = None, *, service_Name=None):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    if checkAdmin(ctx.author.id) is False:
        return
    if not cost:
        await ctx.send(f"Please enter cost. ``{botprefix}addservice <service name> <cost>``")
        return
    if not service_Name:
        await ctx.send(f"Please enter the service name. ``{botprefix}addservice <service name> <cost>``.")
        return
    response = update_services(service_Name, cost)
    if response['status'] == "already Exist":
        await ctx.send("Service Already exist.")
        return
    await ctx.send(f"{service_Name} added successfully!")


@bot.command()
async def nord(ctx):
    service = "Nord VPN"
    response = get_account(service)
    if not response:
        embed = discord.Embed(title="Nord Account Generator",
                              description="Sorry there is no stock! Try again later.", color=embedcolor)
        embed.set_footer(text=embedtext)
        await ctx.send(embed=embed)
        return
    email, password = response.split(":")
    embed = discord.Embed(title="Nord Account Generator", color=embedcolor)
    embed.add_field(name="Email:", value=email)
    embed.add_field(name="Password:", value=password)
    embed.set_footer(text=embedtext)
    await ctx.author.send(embed=embed)
    if checkChannel(ctx) is False:
        embed = discord.Embed(title="Nord Account Generator",
                              description="Account details are sent to you, Check your DM.", color=embedcolor)
        embed.set_footer(text=embedtext)
        await ctx.send(embed=embed)


@bot.command()
async def test(ctx):
    if checkAdmin(ctx.author.id) is False:
        return
    add_account("1", "1")


@bot.command()
async def prices(ctx):
    services = get_services()
    embed = discord.Embed(title="Prices", color=embedcolor)
    embed.set_footer(text=embedtext)
    for service in services:
        name = service['name']
        price = service['cost']
        embed.add_field(name=f"**{name}:**", value=f"₹{price}", inline=False)
    await ctx.send(embed=embed)

bot.run("")  # discord bot token here
