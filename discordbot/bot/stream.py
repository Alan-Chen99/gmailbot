
import firebase
from .bot import client
from .bot import ondiscordready

import utils.timing

streamroot=firebase.init()['discordstream']


def setstream(name,channel,config):
	streamroot[name]['channel']<<channel.id
	streamroot[name]['config']<<config

async def send(name,text,**kwargs):
	await client.wait_until_ready()
	channelid=await streamroot[name]['channel']()
	if channelid is not None:
		channel=client.get_channel(channelid)
		loggingprefix=await streamroot[name]['config']['prefix']()
		if loggingprefix is not None:
			text=loggingprefix+text
		await channel.send(text,**kwargs)

@ondiscordready
async def sendinit():
	await send('info',f'i am initialized at {utils.timing.timestringnow()}')

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

