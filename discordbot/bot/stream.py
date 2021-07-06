
import firebase
from .bot import client
from .bot import ondiscordready
from discordbot import defaultstreams

import utils.timing

streamroot=firebase.init()['discordstream']
catstreamroot=firebase.init()['discordstream_cat']


def setstream(name,channel,config):
	streamroot[name]['channel']<<channel.id
	streamroot[name]['config']<<config

async def send(name,text,**kwargs):
	await client.wait_until_ready()
	stream=streamroot[name]
	channelid=await stream['channel']()
	if channelid is not None:
		channel=client.get_channel(channelid)
		loggingprefix=await stream['config']['prefix']()
		if loggingprefix is not None:
			text=loggingprefix+text
		return await channel.send(text,**kwargs)
	

def setstream_cat(name,category,config):
	catstreamroot[name]['category']<<category.id
	catstreamroot[name]['config']<<config

async def send_cat(name,channel,text,**kwargs):
	await client.wait_until_ready()
	stream=catstreamroot[name]
	catid=await stream['category']()
	if catid is not None:
		channelname=channel
		channelidvar=await stream['config']['channel'][channelname]
		if channelidvar() is None:
			category=client.get_channel(catid)
			channel=await category.create_text_channel(channelname)
			channelidvar<<channel.id
		else:
			channel=client.get_channel(channelidvar())
		loggingprefix=await stream['config']['prefix']()
		if loggingprefix is not None:
			text=loggingprefix+text
		return await channel.send(text,**kwargs)



@ondiscordready
async def sendinit():#should this be in the file?
	await send(defaultstreams.info,f'i am initialized at {utils.timing.timestringnow()}')

#	loggers=await getdiscordvar(None,'logging')
#	#print(loggers)
#	logger=loggers.get(target)
#	if logger!=None:
#		loggingprefix=logger.get('prefix')
#		#if loggingprefix is not None:
#		text=loggingprefix+text
#		channelid=logger.get('channel')
#		#if channelid is not None:
#		await client.get_channel(channelid).send(text,**kwargs)

