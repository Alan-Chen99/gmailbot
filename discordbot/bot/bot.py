import discord
import logging
import os


haveinitialized=False

client = discord.Client()





ondiscordreadylist=[]#list of corutines that needs to run upon discord ready

def ondiscordready(func):
	ondiscordreadylist.append(func)
	return func

@client.event
async def on_ready():
	global haveinitialized
	#await sendloggingmessage('info',f'i am initialized at {utils.timing.timestringnow()}')
	for x in ondiscordreadylist:
		client.loop.create_task(x())
	haveinitialized=True
	print('We have logged in as {0.user}'.format(client))
	

async def runbot():
	await client.start(os.getenv('discordtoken'))