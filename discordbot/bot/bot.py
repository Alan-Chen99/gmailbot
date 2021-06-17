import discord
import logging
import os

from utils.task import addtask

haveinitialized_var=False

client = discord.Client()


def haveinitialized():
	return haveinitialized_var


ondiscordreadylist=[]#list of corutines that needs to run upon discord ready

def ondiscordready(func):
	ondiscordreadylist.append(func())
	return func

@client.event
async def on_ready():
	global haveinitialized_var
	for x in ondiscordreadylist:
		addtask(x)
	haveinitialized_var=True
	print('We have logged in as {0.user}'.format(client))
	

async def runbot():
	await client.start(os.getenv('discordtoken'))