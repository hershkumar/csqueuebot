import os
import discord
from dotenv import load_dotenv
import time
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

prefix = "q "
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=prefix, intents=intents)

role_id = 820745228045910026
mention_string = "<@&"+str(role_id)+">"

game_summoned = False

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')

@bot.command()
async def summon(ctx, num_games_summoned: int = 0):
	global game_summoned
	if game_summoned == False:
		if num_games_summoned != 0:
			await ctx.send("Summoning for " + str(num_games_summoned) + " game(s).")
			game_summoned = True
		else:
			await ctx.send("Please give a number of games.")
	else:
		await ctx.send("Game is already summoned.")
@bot.command()
async def join(ctx, game_num: int = 0):
	if game_num != 0:
		await ctx.send("Joined game " + str(game_num) + str("."))
	else:
		await ctx.send("Please pick a game to join.")


bot.run(TOKEN)