import os
import discord
from dotenv import load_dotenv
import time

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

prefix = 'q'
role_id = 820745228045910026
mention_string = "<@&"+str(role_id)+">"
queue_flag = False
num_games = 0
players = {}
all_players = []

# displays the message with all the people in for queues
def disp_queue(game_num):
	global players
	ret_str = "Game " + str(game_num) + "\n"
	game_list = {}
	for player in players:
		# if the player is down to play that game
		if players.get(player)[0] >= game_num:
			game_list[player] = players.get(player)

	#get a sorted list by time they joined
	sorted_players = sorted(game_list.items(), key = lambda p: p[1])

	if len(sorted_players)  >= 5:
		for i in range(4):
			print(str(i + 1) + ". " + sorted_players[i][0])
			ret_str += str(i + 1) + ". " + sorted_players[i][0] + "\n"
	else:
		for i in range(len(sorted_players)):
			print(str(i + 1) + ". " + sorted_players[i][0])
			ret_str += str(i + 1) + ". " + sorted_players[i][0] + "\n"

	# do substitutes
	if len(sorted_players) >= 5:
		ret_str += "Substitutes:\n"
		for i in range(len(sorted_players) - 5):
			ret_str += str(i + 1) + ". " + sorted_players[i][0] + "\n"

	return ret_str

@client.event
async def on_ready():
	global all_players
	print(f'{client.user} has connected to Discord!')
	guild = client.guilds[0]
	role = guild.get_role(role_id)
	print(role)
	all_players = role.members
	print(all_players)
	

# when someone sends a message
@client.event
async def on_message(message):
	global queue_flag
	global players
	global num_games
	# if the author is the bot, we do nothing
	if message.author == client.user:
		return
	# if the message starts with the prefix
	if message.content.startswith(prefix):
		message_list = message.content.split()
		num_args = len(message_list)
		# if they only said 'q'
		if num_args == 1:
			await message.channel.send("No arguments given")
		# if they passed a command
		else:
			if message_list[1] == 'help':
				await message.channel.send("Send help please.")
				return
			if message_list[1] == 'summon':
				if queue_flag == False:
					if num_args == 3:
						if int(message_list[2]) > 0:
							num_games = int(message_list[2])
							if num_games <= 5:
								await message.channel.send(mention_string + " Summoning for " 
								+ str(num_games) + " games.")
								queue_flag = True
							else:
								await message.channel.send("Too many games, please summon a queue for a smaller number of games.")
					else:
						await message.channel.send("Please input the number of games.")
				else:
					await message.channel.send("Queue has already been summoned, please stop queue before starting a new one.")
				return
			if message_list[1] == 'cancel':
				queue_flag = False
				num_games = 0
				players = {}

				await message.channel.send("Queue has been cancelled.")
				return
			#person decides to join the queue
			if message_list[1] == 'join':
				if queue_flag == True:
					if num_args == 3:
						if int(message_list[2]) > 0:
							players[message.author.name] = [int(message_list[2]), time.time()]
							await message.channel.send("You have been added to the queue for game " + message_list[2] + ".")
							print(players)
					else:
						await message.channel.send("Please input the number of games")
				else:
					await message.channel.send("Queue is not currently summoned.")

				return

			if message_list[1] == 'leave':
				if queue_flag == True:
					if num_args == 2:
						del players[message.author.name]
						await message.channel.send("You have been removed from the queue.")
						print(players)
				else:
					await message.channel.send("Queue is not currently summoned.")

				return

			if message_list[1] == 'disp':
				if queue_flag == True:
					if num_args == 2:
						for i in range(num_games):
							await message.channel.send(disp_queue(i + 1))
				else:
					await message.channel.send("Queue is not currently summoned.")
				return
			else:
				await message.channel.send("Unknown command.")
				return

client.run(TOKEN)