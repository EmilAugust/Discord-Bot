import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import random

intents = discord.Intents.default()
intents.members = True

prefix = "!"
bot = commands.Bot(command_prefix = prefix,case_insensitive=True ,intents=intents)
usersMessages = dict()
usersXP = dict()
usersLevel = dict()
usersBalance = dict()

@bot.event
async def on_ready():
  print("We have logged in as {0.user}".format(bot))

bot.remove_command('help')

@bot.event
async def on_message(message):
    msg = message.content.lower()

    user = message.author
    userID = message.author.id

    if message.author == bot.user:
        return

    if not userID in usersBalance:
        usersBalance[userID] = 0
    if not userID in usersMessages:
        usersMessages[userID] = 0
    usersMessages[userID] += 1

    if not userID in usersXP:
        usersXP[userID] = 0
    usersXP[userID] += 50 + len(msg)

    if usersXP[userID] < 10000 and not userID in usersLevel:
        usersLevel[userID] = 0
    elif usersXP[userID] >= 1000 + usersLevel[userID] * 100 + usersLevel[userID] * 1000:
        usersLevel[userID] += 1
        usersBalance[userID] += 3000
        await message.channel.send(f"{user.mention}, You just reached level {usersLevel[userID]}!")

    await bot.process_commands(message)

@bot.command(aliases = ["commands"])
async def help(ctx):
    helptext = ""
    for command in bot.commands:
        helptext+=f"-{command}\n"
    helpEmbed = discord.Embed(title="Commands", description=helptext, color=0xf7c200)
    helpEmbed.set_footer(text=f"Requested by {ctx.author}")
    await ctx.send(embed=helpEmbed)

@bot.command(aliases = ["me", "stats"])
async def profile(ctx):
    user = ctx.author
    username = ctx.author.name
    userTag = ctx.author.discriminator
    userID = ctx.author.id
    meEmbed = discord.Embed(title = f":bar_chart:{user}", color=0xf7c200)
    meEmbed.set_thumbnail(url=user.avatar_url)
    meEmbed.add_field(name=":moneybag: Balance", value=f"{usersBalance[userID]:,}", inline=True)
    meEmbed.add_field(name=":star: Level", value=f"{usersLevel[userID]:,}", inline=True)
    meEmbed.add_field(name=":sparkles: XP", value=f"{usersXP[userID]:,}", inline=True)
    meEmbed.add_field(name=":incoming_envelope: Messages", value=f"{usersMessages[userID]:,}", inline=False)
    meEmbed.add_field(name="UserID", value=userID, inline=False)
    meEmbed.set_footer(text=f"Requested by {ctx.author}")
    await ctx.send(embed=meEmbed)

@bot.command(aliases = ["xptop", "xpleaderboard", "levelleaderboard"])
async def leveltop(ctx):
    server = ctx.guild
    sortedXP = sorted(usersXP.items(), key=lambda x: x[1], reverse = True)
    formatted_text = ""
    count = 0
    for x in sortedXP:
        count += 1
        key = x[0]
        value = x[1]
        levelValue = usersLevel[key]
        memberObject = await server.fetch_member(key)
        totalXP = sum(usersXP.values())
        formatted_text += f"\n **{count}.** Level: `{levelValue}` XP: `{value:,}` - {memberObject.mention}"
        if count == 15:
            break
    leveltopEmbed = discord.Embed(title = ":sparkles: XP Leaderboard", description=formatted_text, color=0xf7c200)
    leveltopEmbed.set_footer(text=f"Total XP: {totalXP:,}")

    await ctx.send(embed=leveltopEmbed)


@bot.command()
async def coinflip(ctx, outcome, amount:int):
    userID = ctx.author.id
    coins = ["heads", "tails"]
    coin = random.choice(coins)
    if outcome in ("heads","tails") and amount > 0:
        if usersBalance[userID] >= amount:
            if outcome == coin:
                usersBalance[userID] += amount
                coinflipEmbed = discord.Embed(title="Coinflip", description=f"The coin landed on **{coin}**, and you won `{amount:,}` money! \n **New balance:** {usersBalance[userID]:,}", color=0x99EE38)
                if coin == "heads":
                    coinflipEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/637105382631669760/675097745295540244/heads.png")
                else:
                    coinflipEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/637105382631669760/675097748747452431/tails.png")
                coinflipEmbed.set_footer(text=f"Tossed by {ctx.author}")
                await ctx.send(embed=coinflipEmbed)
            elif outcome != coin:
                print(usersBalance[userID])
                usersBalance[userID] -= amount
                coinflipEmbed = discord.Embed(title="Coinflip", description=f"The coin landed on **{coin}**, and you lost `{amount:,}` money! \n **New balance:** {usersBalance[userID]:,}", color=0xDE2424)
                if coin == "heads":
                    coinflipEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/637105382631669760/675097745295540244/heads.png")
                else:
                    coinflipEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/637105382631669760/675097748747452431/tails.png")
                coinflipEmbed.set_footer(text=f"Tossed by {ctx.author}")
                await ctx.send(embed=coinflipEmbed)
        else:
            coinflipErrorEmbed = discord.Embed(title="You don't have enough money!", description=f"**Your balance:** {usersBalance[userID]:,}", color=0xDE2424)
            coinflipErrorEmbed.set_footer(text=f"Requested by {ctx.author}")
            await ctx.send(embed=coinflipErrorEmbed)
    else:
        coinflipErrorEmbed = discord.Embed(title="Invalid", description="Correct usage: `!coinflip [heads/tails] [money]`", color=0xDE2424)
        coinflipErrorEmbed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=coinflipErrorEmbed)

@coinflip.error
async def flip_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        coinflipErrorEmbed = discord.Embed(title="Invalid", description="Correct usage: `!coinflip [heads/tails] [money]`", color=0xDE2424)
        coinflipErrorEmbed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=coinflipErrorEmbed)
    if isinstance(error, commands.BadArgument):
        coinflipErrorEmbed = discord.Embed(title="Invalid", description="Correct usage: `!coinflip [heads/tails] [money]`", color=0xDE2424)
        coinflipErrorEmbed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=coinflipErrorEmbed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        unknownCommandEmbed = discord.Embed(title="Unknown Command", description="Do `!help` for a list of commands", color=0xDE2424)
        unknownCommandEmbed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=unknownCommandEmbed)
        return
    raise error

bot.run("ODQxNTk4MTg3MzQ1MDE4OTQw.YJpFZA.KNZOo2KuFDzzLhCL9ADXkrWzgfM")
