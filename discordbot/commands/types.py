import discordbot.bot as bot
#from discordbot.tools import ratelimit
#from discordbot.tools import context as ctools
from  discordbot.tools import standardcommands
import utils.exceptions

import json

commands=standardcommands.standard_command_group()
makematcher=commands.add
newcommand=standardcommands.standardcommand



@makematcher('file','arg')
@newcommand
async def botfile(content,message):
	await message.reply(file=await bot.filefromstring(content['arg']))
	return None

@makematcher('auto','arg')
@newcommand
async def botauto(content,message):
	tmp=content['arg']
	if tmp==None:
		return 'output is None'
	if isinstance(tmp, Exception):
		tmp=utils.exceptions.excpetiontostring(tmp)
	elif isinstance(tmp, (str,int,float)):
		tmp=str(tmp)
	else:
		try:
			tmp=json.dumps(tmp,indent=2)
		except (TypeError, OverflowError):
			tmp=str(tmp)

	await message.reply(file=await bot.filefromstring(tmp))
	return None
	


#@makematcher('content','arg')
#@newcommand
#async def botcontent(content,message):
#	return content

@makematcher('send','arg')
@newcommand
async def botsend(content,message):
	tmp=content.get('arg')
	await message.channel.send(str(tmp))
	return tmp

@makematcher('str','arg')
@newcommand
async def botstr(content,message):
	tmp=content.get('arg')
	return str(tmp)
	
@makematcher('int','arg')
@newcommand
async def botint(content,message):
	try:
		tmp=int(content['arg'])
		return tmp
	except ValueError:
		return f'{repr(content["arg"])} cannot be converted to int'

@makematcher('bool','arg')
@newcommand
async def botbool(content,message):
	tmp=content['arg']
	if tmp=='True':
		return True
	if tmp=='False':
		return False
	return f'{repr(tmp)} cannot be converted to bool'
	
@makematcher('json','arg')
@newcommand
async def botjson(content,message):
	tmp=content['arg']
	return json.dumps(tmp,indent=2)