import discordbot.bot as bot
from discordbot.tools import ratelimit
#from discordbot.tools import context as ctools
from  discordbot.tools import standardcommands

import datetime
import asyncio
import utils.timing

commands=standardcommands.standard_command_group()
makematcher=commands.add
newcommand=standardcommands.standardcommand



@makematcher('ping')
@newcommand
async def botping(content,message):
	return 'pong'


@makematcher('pass')
@newcommand
async def botpass(content,message):
	pass

@makematcher('latency')
@newcommand
async def botlatency(content,message):
	tmp=await message.reply('Loading data',mention_author=False)
	timetake=(tmp.created_at - message.created_at).total_seconds()*1000
	await tmp.edit(content=f'latency is {timetake} ms, API latency is {bot.client.latency*1000} ms')
	return None


@makematcher('send','arg')
@ratelimit.usemessage
@newcommand
async def botsend(content,message):
	tmp=content.get('arg')
	await message.channel.send(str(tmp))
	return tmp



@makematcher('second','arg')
@newcommand
async def botsecond(content,message):
	try:
		tmp=float(content['arg'])
		delta = datetime.timedelta(seconds=tmp)
		return delta
	except ValueError:
		return f'{repr(content["arg"])} cannot be converted to seconds'

@makematcher('timer','arg')
@ratelimit.usemessage
@newcommand
async def bottime(content,message):
	interval=content['arg']
	if not isinstance(interval, datetime.timedelta):
		return "timer takes a datetime object"
	
	await message.reply(f'setting a timer of {str(interval)}')
	await asyncio.sleep(interval.total_seconds())
	return f'timer of {str(interval)} is up!'


@makematcher('clientid')
@newcommand
async def botclientid(content,message):
	return bot.client.user.id

@makematcher('clientmention')
@newcommand
async def botclientmention(content,message):
	return bot.client.user.mention


@makematcher('line')
@ratelimit.usemessage
@newcommand
async def botline(content,message):
	await message.channel.send(f'{utils.timing.timestringnow()}\n--------------------------------------------------------------------------------------------------------------------')
	return None