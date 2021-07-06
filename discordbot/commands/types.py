import discordbot.bot as bot
#from discordbot.tools import ratelimit
#from discordbot.tools import context as ctools
from  discordbot.tools import standardcommands
from  discordbot.tools import messaging
import utils.exceptions

import json
import pprint
import datetime

commands=standardcommands.standard_command_group()
makematcher=commands.add
#newcommand=standardcommands.standardcommand



@makematcher('file','arg')
@bot.command(standardcommands.args,bot.contextall)
async def botfile(content,context):
	await messaging.reply(context)(file=await bot.filefromstring(content['arg']))
	return None

@makematcher('auto','arg')
@bot.command(standardcommands.args,bot.contextall)
async def botauto(content,context):
	tmp=content['arg']
	if tmp==None:
		tmp='output is None'
	elif isinstance(tmp, Exception):
		tmp=utils.exceptions.excpetiontostring(tmp)
	elif type(tmp) is not str:
		try:
			tmp=json.dumps(tmp,indent=2)
		except (TypeError, OverflowError):
			tmp=pprint.pformat(tmp)
	
	assert(type(tmp) is str)
	await messaging.reply(context)(file=await bot.filefromstring(tmp))
	return None


'''
@makematcher('autoold','arg')
@bot.command(standardcommands.args,bot.contextall)
async def botautoold(content,context):
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

	await messaging.reply(context)(file=await bot.filefromstring(tmp))
	return None
'''


#@makematcher('content','arg')#same as str
#@newcommand
#async def botcontent(content,message):
#	return content

@makematcher('str','arg')
@bot.command(standardcommands.args)
async def botstr(content):
	tmp=content.get('arg')
	return str(tmp)
	
@makematcher('int','arg')
@bot.command(standardcommands.args)
async def botint(content):
	try:
		tmp=int(content['arg'])
		return tmp
	except ValueError:
		return f'{repr(content["arg"])} cannot be converted to int'

@makematcher('bool','arg')
@bot.command(standardcommands.args)
async def botbool(content):
	tmp=content['arg']
	if tmp=='True':
		return True
	if tmp=='False':
		return False
	return f'{repr(tmp)} cannot be converted to bool'

@makematcher('second','arg')
@bot.command(standardcommands.args)
async def botsecond(content):
	try:
		tmp=float(content['arg'])
		delta = datetime.timedelta(seconds=tmp)
		return delta
	except ValueError:
		return f'{repr(content["arg"])} cannot be converted to seconds'

@makematcher('none')#equivalent to pass
@bot.command()
async def botnone():
	return None
	
@makematcher('silence','content')
@bot.command()
async def botsilence():
	pass

@makematcher('json','arg')
@bot.command(standardcommands.args)
async def botjson(content):
	tmp=content['arg']
	try:
		return json.dumps(tmp,indent=2)
	except (TypeError, OverflowError):
		return f'{repr(tmp)} is not json serializable'	

@makematcher('jsonload','arg')
@bot.command(standardcommands.args)
async def botjsonload(content):
	tmp=content['arg']
	try:
		return json.loads(tmp)
	except:
		return f'{repr(tmp)} is not valid json'

@makematcher('code','content')
@bot.command(standardcommands.args)
async def botcode(content):
	arr=str(content['content']).split('```')
	return '```\n'+('\u200b`\u200b`\u200b`').join(arr)+'\n```'
	
@makematcher('repr','content')
@bot.command(standardcommands.args)
async def botrepr(content):
	return repr(content['content'])

@makematcher('type','content')
@bot.command(standardcommands.args)
async def bottype(content):
	return type(content['content'])