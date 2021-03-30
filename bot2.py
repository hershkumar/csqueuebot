import os
import discord
from dotenv import load_dotenv
import time as t
from discord.ext import commands, tasks

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

prefix = "q "
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=prefix, intents=intents)

role_id = 820745228045910026
mention_string = "<@&"+str(role_id)+">"
#mention_string = ""
game_summoned = False
time_summoned = 0
# summons should be auto-cancelled after this many hours
cancel_timer = 3

# players are stored in a list of lists, top level is game number and second level is player names (sorted by join time)
games = []

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')
	await bot.change_presence(activity=discord.Game(name="q summon"))



@bot.command(help="Summons a queue of gamers.")
async def summon(ctx, num_games_summoned: int = 1, time: str = ""):
	global game_summoned
	global games
	global time_summoned

	if game_summoned == False:
		if num_games_summoned != 0:
			await ctx.send(mention_string + " Summoning for " + str(num_games_summoned) + " game(s), with the first game at " + time + ".")
			game_summoned = True
			# add that number of games to the games list, all empty
			games = [[] for i in range(num_games_summoned)]
			
			await bot.change_presence(activity=discord.Game(name="0/5 slots filled"))
			# set the time summoned
			time_summoned = t.time()
			check_timer.start(ctx)
			# Should auto-join the summoner into the first game
			await ctx.invoke(bot.get_command('join'), game_num=1)
		else:
			await ctx.send("Please give a number of games.")
	else:
		await ctx.send("Game is already summoned.")


@bot.command(help="Adds you to the current queue.")
async def join(ctx, game_num: int = 0):
	global games
	global game_summoned

	if game_summoned:
		if game_num != 0 and game_num > 0:
			# if they're joing a game that already exists
			if game_num <= len(games):
				# only add them if they're not already in the game
				if not (ctx.message.author in games[game_num - 1]):
					games[game_num - 1].append(ctx.message.author)
					await bot.change_presence(activity=discord.Game(name=str(len(games[0])) + "/5 slots filled"))
					await ctx.send("Joined game " + str(game_num) + ".")
				else:
					await ctx.send("You are already in that game.")
			# otherwise we need to add a new list to games
			# need to add game_num - len(games) new lists
			else:
				for i in range(game_num - len(games)):
					games.append([])
				# add the player to the next game
				games[game_num - 1].append(ctx.message.author)
				print(str(len(games[0])))
				await bot.change_presence(activity=discord.Game(name=str(len(games[0])) + "/5 slots filled"))
				await ctx.send("Joined new game " + str(game_num) + ".")
		else:
			await ctx.send("Please pick a game to join.")
	else:
		await ctx.send("No currently running queue.")

@bot.command(help="Removes you from chosen game.")
async def leave(ctx, game_num: int = 0):
	global games
	global game_summoned

	if game_summoned:
		if game_num != 0 and game_num > 0:
			# if the person is in the game
			if ctx.message.author in games[game_num - 1]:
				index = games[game_num - 1].index(ctx.message.author)
				# if the players was one of the first 5
				if index < 5:
					if len(games[game_num - 1]) > 5:
						# ping the person in slot 5
						await ctx.send("{}, you are no longer a substitute for game ".format(games[game_num - 1][5].mention) + str(game_num)) 
				games[game_num - 1].remove(ctx.message.author)
				await bot.change_presence(activity=discord.Game(name=str(len(games[0])) + "/5 slots filled"))
				await ctx.send("You have been removed from game " + str(game_num))
			else:
				await ctx.send("You are not in that game.")
		else:
			await ctx.send("Please pick a game to leave.")
	else:
		await ctx.send("No currently running queue.")

@bot.command(help="Cancels the current queue.")
async def cancel(ctx):
	global game_summoned
	global games

	if game_summoned:
		await ctx.send("Summon has been cancelled.")
		game_summoned = False
		games.clear()
		
		await bot.change_presence(activity=discord.Game(name="q summon"))
	else:
		await ctx.send("There is no queue running currently.")

# displays all the nonempty games
@bot.command(help="Displays the status of the current queue.")
async def disp(ctx):
	global games
	msg = ""
	for i in range(len(games)):
		# if the game is not empty, we want to print the queue for it
		if games[i]:
			# print the game label
			msg += "__Game " + str(i + 1) + "__\n"
			# loop through and print all the players in the game
			for j in range(len(games[i])):
				if j < 5:
					msg += "**"+str(j + 1)+". " + games[i][j].name + "**\n"
				else:
					msg += str(j + 1)+". " + games[i][j].name + "\n"

	# if all the games are empty
	if msg == "":
		await ctx.send("All games are currently empty.")
	else:
		await ctx.send(msg)

# removes the first game from the games list (when the game has been played)
@bot.command(help="Removes the first game from the queue.")
async def played(ctx):
	global games
	global game_summoned
	if game_summoned:
		if games:
			# remove the first one
			games.pop(0)
			await ctx.send("First game has been played.")
		else:
			await ctx.send("There are no games in queue.")
	else:
		await ctx.send("Game is not summoned.")

@tasks.loop(seconds=5.0)
async def check_timer(ctx):
	global game_summoned
	global time_summoned

	if game_summoned:
		# check the current time against the time_summoned
		time_since_summoned = t.time() - time_summoned
		# if cancel_timer hours have passed since the summon
		if time_since_summoned >= (3600 * cancel_timer):
			# cancel the summon
			await ctx.invoke(bot.get_command('cancel'))


bot.run(TOKEN)