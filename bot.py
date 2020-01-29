import discord
from discord.ext import commands
from discord.utils import get
import logging
import os
import asyncio
from itertools import cycle
import youtube_dl
import shutil
players={}

#Add token.txt to the working directory with your Bot Token
#Add youtube_api.txt with your API key

f = open('token.txt', 'r')
TOKEN = f.read().replace('\n', '')
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
client = commands.Bot(command_prefix="!")
client.remove_command('help')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
@client.event
async def on_member_join(member):
	role=discord.utils.get(member.guild.roles,name="Hero")
	await member.add_roles(role)
@client.command()
async def ping(message):
	await message.channel.send("Pong!")
@client.command()
async def clean(ctx,amount=100):
	messages=[]
	channel=ctx.channel
	async for message in channel.history(limit=int(amount)):
		messages.append(message)
	await channel.delete_messages(messages)
	await channel.send('Messages Deleted!')
@client.command()
async def help(ctx):
	author=ctx.author
	embed=discord.Embed(
	description="Here' some Help",
	colour=discord.Colour.blue()
	)
	embed.set_author(name='help')
	embed.add_field(name="!ping ",value="Returns pong",inline=False)
	embed.add_field(name="!clean ",value="Clean messages Usage:!clean no._of_messages,default-100",inline=False)
	embed.add_field(name="!play",value="Play with !play songname ",inline=False)
	embed.add_field(name="!pause",value="pauses the music",inline=False)
	embed.add_field(name="!resume",value="resumes the music",inline=False)
	embed.add_field(name="!stop",value="stops the music",inline=False)
	embed.add_field(name="!next",value="Plays next song in queue.",inline=False)
	embed.add_field(name="!queue",value="Queues a song. Use !queue Song_name",inline=False)
	embed.add_field(name="!kick",value="Kicks a member. Use !kick member_name",inline=False)
	embed.add_field(name="!ban",value="Bans a member. Use !ban member_name",inline=False)
	embed.add_field(name="!unban",value="Unbans a member. Use !unban member_name(with discriminator) Eg:Nishant#4324",inline=False)

	await ctx.channel.send(author,embed=embed)
@client.event
async def on_reaction_add(reaction,user):
	channel=reaction.message.channel
	await channel.send('{} has added {} to the message {}'.format(user.name,reaction.emoji,reaction.message.content))
@client.command()
@commands.has_role('admin')
async def kick(ctx,member: discord.Member,*,reason="none"):
	await member.kick(reason=reason)
	await ctx.send(f"Kicked!{user.mention}")
@client.command()
@commands.has_role('admin')
async def ban(ctx,member : discord.Member,*,reason="none"):
	await member.ban(reason=reason)
	await ctx.send(f"Banned! {user.mention}")
@client.command()
@commands.has_role('admin')
#we need user#123 member format as they are not in server
async def unban(ctx,*,member): 						
	banned_users= await ctx.guild.bans()
	member_name,member_discriminator=member.split('#')
	for ban_entry in banned_users:
		user=ban_entry.user
		if(user.name,user.discriminator)==(member_name,member_discriminator):
			await ctx.guild.unban(user)
			await ctx.send(f"Unbanned {user.mention}")
			return
#load the cogs in the working directory
for filename in os.listdir("./"):
	if filename.endswith(".py") and filename!="bot.py":
		client.load_extension(f"{filename[:-3]}")
client.run(TOKEN)