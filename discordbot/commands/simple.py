import discordbot.bot as bot
from discordbot.bot import command
from discordbot.tools import ratelimit
#from discordbot.tools import context as ctools
from  discordbot.tools import standardcommands
from  discordbot.tools import messaging

import datetime
import asyncio
import utils.timing

commands=standardcommands.standard_command_group()
makematcher=commands.add
#newcommand=command(standardcommands.args,bot.message)
#standardcommands.standardcommand



@makematcher('ping')
@command()
async def botping():
	return 'pong'


@makematcher('pass')
@command()
async def botpass():
	pass

@makematcher('latency')
@ratelimit.usemessage
@command(bot.message)
async def botlatency(message):
	tmp=await message.reply('Loading data',mention_author=False)
	timetake=(tmp.created_at - message.created_at).total_seconds()*1000
	await tmp.edit(content=f'latency is {timetake} ms, API latency is {bot.client.latency*1000} ms')
	return None


@makematcher('send','arg')#TODO: what if arg is none
@bot.command(content=standardcommands.args,context=bot.contextall)
async def botsend(content,context):
	tmp=content.get('arg')
	await messaging.sendchannel(context)(tmp)
	return tmp


'''#move to types
@makematcher('second','arg')
@newcommand
async def botsecond(content,message):
	try:
		tmp=float(content['arg'])
		delta = datetime.timedelta(seconds=tmp)
		return delta
	except ValueError:
		return f'{repr(content["arg"])} cannot be converted to seconds'
'''

@makematcher('timer','arg')
@ratelimit.usemessage
@ratelimit.usemessage
@bot.command(standardcommands.args,bot.message)
async def bottime(content,message):
	interval=content['arg']
	if not isinstance(interval, datetime.timedelta):
		return "timer takes a datetime object"
	
	await message.reply(f'setting a timer of {str(interval)}')
	await asyncio.sleep(interval.total_seconds())
	await message.reply(f'timer of {str(interval)} is up!')
	return None


@makematcher('clientid')
@bot.command()
async def botclientid():
	return bot.client.user.id

@makematcher('clientmention')
@bot.command()
async def botclientmention():
	return bot.client.user.mention


@makematcher('line')
@bot.command(bot.contextall)
async def botline(context):
	await messaging.sendchannel(context)(f'{utils.timing.timestringnow()}\n--------------------------------------------------------------------------------------------------------------------')
	return None