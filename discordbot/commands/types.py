import discordbot.bot as bot
from discordbot.tools import ratelimit
#from discordbot.tools import context as ctools
from  discordbot.tools import standardcommands
import utils.exceptions

import json

commands=standardcommands.standard_command_group()
makematcher=commands.add
newcommand=standardcommands.standardcommand



@makematcher('file','arg')
@ratelimit.usemessage
@newcommand
async def botfile(content,message):
	await message.reply(file=await bot.filefromstring(content['arg']))
	return None

@makematcher('auto','arg')
@ratelimit.usemessage
@newcommand
async def botauto(content,message):
	tmp=content['arg']
	if tmp==None:
		tmp='output is None'
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
	


#@makematcher('content','arg')#same as str
#@newcommand
#async def botcontent(content,message):
#	return content

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

@makematcher('none')#equivalent to pass
@newcommand
async def botnone(content,message):
	return None
	
@makematcher('silence','content')
@newcommand
async def botsilence(content,message):
	pass

@makematcher('json','arg')
@newcommand
async def botjson(content,message):
	tmp=content['arg']
	return json.dumps(tmp,indent=2)

@makematcher('jsonload','arg')
@newcommand
async def botjsonload(content,message):
	tmp=content['arg']
	return json.loads(tmp)

@makematcher('code','content')
@newcommand
async def botcode(content,message):
	arr=str(content['content']).split('```')
	return '```\n'+('\u200b`\u200b`\u200b`').join(arr)+'\n```'
	
@makematcher('repr','content')
@newcommand
async def botrepr(content,message):
	return repr(content['content'])