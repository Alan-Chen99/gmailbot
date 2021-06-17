import discordbot
from discordbot import newcommand
from discordbot import requirevar
from discordbot import addmatcher
from discordbot import makematcher

import utils
import database
import re
import datetime
import asyncio
import json
#TODO: delete
import gmail


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
	await tmp.edit(content=f'latency is {timetake} ms, API latency is {discordbot.client.latency*1000} ms')
	return None
	


#r'^echo(\s+(?P<content>[\s\S]*)$|$)'
@addmatcher(r'^echo$')
@addmatcher(r'^echo\s+(?P<arg>[\s\S]*)$')
@newcommand
async def botecho(content,message):
	tmp=content.get('arg')
	if tmp!=None:
		return str(tmp)
	return 'nothing to echo!'

@makematcher('file','arg')
@newcommand
async def botfile(content,message):
	await message.reply(file=await discordbot.filefromstring(content['arg']))
	return None

@makematcher('auto','arg')
@newcommand
async def botauto(content,message):
	tmp=content['arg']
	if tmp==None:
		return 'output is None'
	if isinstance(tmp, Exception):
		tmp=utils.excpetiontostring(tmp)
	elif isinstance(tmp, (str,int,float)):
		tmp=str(tmp)
	else:
		try:
			tmp=json.dumps(tmp,indent=2)
		except (TypeError, OverflowError):
			tmp=str(tmp)

	await message.reply(file=await discordbot.filefromstring(tmp))
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

@makematcher('sendastest','arg')#TODO
@newcommand
async def botsendastest(content,message):
	tmp=content['arg']
	await discordbot.sendastest(message,message.author,tmp)


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
@newcommand
async def bottime(content,message):
	interval=content['arg']
	if not isinstance(interval, datetime.timedelta):
		return "timer takes a datetime object"
	
	await message.reply(f'setting a timer of {str(interval)}')
	await asyncio.sleep(interval.total_seconds())
	return f'timer of {str(interval)} is up!'

@makematcher('repeatalarm')
@requirevar('admin')
@newcommand
async def botrepeatalarm(content,message):
	while True:
		await message.reply(f'repeat alert')
		await asyncio.sleep(5)


@makematcher('commands')#TODO
@newcommand
async def botcommands(content,message):
	ans=''
	for command in discordbot.alldiscordcommands:
		havereq=True
		for req in command[2]:
			if (await req(message))!=True:
				havereq=False
				break
		if havereq:
			for x in command[1]:
				ans=ans+x[0]+'\n'
	return ans

@makematcher('id')
@newcommand
async def botid(content,message):
	return discordbot.client.user.id

@makematcher('mention')
@newcommand
async def botmention(content,message):
	return discordbot.client.user.mention

#@addmatcher(r'^pingid\s+<@(?P<arg>[\s\S]*)>$')
#@newcommand
#async def botpingid(content,message):
#	return content['arg']

@makematcher('silence','content')
@newcommand
async def botsilence(content,message):
	pass

@makematcher('print','content')
@requirevar('admin')
@newcommand
async def botprint(content,message):
	tmp=content['content']
	print(tmp)
	return tmp

@makematcher('code','content')
@newcommand
async def botcode(content,message):
	arr=str(content['content']).split('```')
	return '```\n'+('\u200b`\u200b`\u200b`').join(arr)+'\n```'
	
@makematcher('repr','content')
@newcommand
async def botrepr(content,message):
	return repr(content['content'])

@makematcher('line')
@requirevar('admin')
@newcommand
async def botline(content,message):
	await message.channel.send(f'{utils.timestringnow()}\n--------------------------------------------------------------------------------------------------------------------')
	return None

@makematcher('get')
@requirevar('admin')
@newcommand
async def botget(content,message):
	rst={}
	for x in discordbot.discord_default_vars:
		rst[x[0]]=await discordbot.getdiscordvar(message,x[0])
	return rst


@makematcher('adminverify','key')
@newcommand
async def botadminverify(content,message):
	key=content['key']
	if utils.verhash(key,utils.discord_user_pwd):
		await discordbot.setdiscordvar(message,'author','admin',True)
		return 'admin permission added'
	else:
		return 'password incorrect'


@makematcher('getdball')
@requirevar('admin')
@newcommand
async def botgetdball(content,message):
	return repr(await database.getwebdb())+'\n'+repr(await database.getlocaldb())


@makematcher('getdb')
@requirevar('admin')
@newcommand
async def botgetdb(content,message):
	return await database.getwebdb()
	

@makematcher('resetdb')
@requirevar('admin')
@newcommand
async def botresetdb(content,message):
	await database.resetdb()
	await discordbot.setdiscordvar(message,'author','admin',True)
	return 'database reseted'

@makematcher('resetdefaults')
@requirevar('admin')
@newcommand
async def botresetdefaults(content,message):
	await discordbot.resetdiscordvarsdefault()
	return 'database default vars reseted'



@addmatcher(r'^eval\s+(?P<arg>[\s\S]*)$')
@addmatcher(r'^eval\s+`(?P<arg>[\s\S]*)`$')
@addmatcher(r'^eval\s+```(?P<arg>[\s\S]*)```$')
@requirevar('admin')
@newcommand
async def boteval(content,message):
	try:
		tmp=eval(content['arg'])
	except Exception as e:
		return utils.excpetiontostring(e)
	return tmp

#https://stackoverflow.com/questions/44859165/async-exec-in-python
async def aexec(code):
	# Make an async function with the code and `exec` it
	try:
		exec(
			f'async def __aexecinternal(): ' +
			''.join(f'\n {l}' for l in code.split('\n'))
		)
		# Get `__aexecinternal` from local variables, call it and return the result
		tmp=await locals()['__aexecinternal']()
	except Exception as e:
		return utils.excpetiontostring(e)
	return tmp


@addmatcher(r'^exec\s+(?P<arg>[\s\S]*)$')
@addmatcher(r'^exec\s+`(?P<arg>[\s\S]*)`$')
@addmatcher(r'^exec\s+```(?P<arg>[\s\S]*)```$')
@requirevar('admin')
@newcommand
async def botexec(content,message):
	loc=locals()
	try:
		exec(content['arg'], globals(), loc)
	except Exception as e:
		return utils.excpetiontostring(e)
	loccopy = dict(loc)
	loccopy.pop('content')
	loccopy.pop('message')
	return loccopy

@addmatcher(r'^aexec\s+(?P<arg>[\s\S]*)$')
@addmatcher(r'^aexec\s+`(?P<arg>[\s\S]*)`$')
@addmatcher(r'^aexec\s+```(?P<arg>[\s\S]*)```$')
@requirevar('admin')
@newcommand
async def botaexec(content,message):
	loc=locals()
	try:
		rst=await aexec(content['arg'])
	except Exception as e:
		return e
	return rst




@makematcher('set','val',['level','var'])
@requirevar('admin')
@newcommand
async def botset(content,message):
	level=content['level']
	tmp=await discordbot.havelevel(level)
	if tmp==False:
		return f'{level} is not a valid level'
	var=content['var']
	val=content['val']
	await discordbot.setdiscordvar(message,level,var,val)
	return 'success!'

@makematcher('setlogging','prefix',['type'])#TODO
@requirevar('admin')
@newcommand
async def botsetlogging(content,message):
	loggers=await discordbot.getdiscordvar(None,'logging')
	loggingtype=content['type']
	#print(repr(loggers))
	if loggingtype not in loggers:
		loggers[loggingtype]={}
	loggers[loggingtype]['channel']=message.channel.id
	loggers[loggingtype]['prefix']=content['prefix']
	await discordbot.setdiscordvar(None,'default','logging',loggers)
	return 'success!'

class testexception(Exception):
	pass

@makematcher('testexception')#TODO
@requirevar('admin')
@newcommand
async def bottestexception(content,message):
	raise testexception('testexception content')

'''
@makematcher('setloggingchannel')
@requirevar('admin')
@newcommand
async def botsetloggingchannel(content,message):
	await discordbot.setdiscordvar(message,'default','loggingchannel',message.channel.id)
	return 'success!'

@makematcher('setloggingprefix','arg')
@requirevar('admin')
@newcommand
async def botsetloggingprefix(content,message):
	await discordbot.setdiscordvar(message,'default','loggingprefix',content['arg'])
	return 'success!'
'''
#TODO

bot=None


@makematcher('messenger','arg')
@requirevar('admin')
@newcommand
async def botmessengertest(content,message):
	messenger_recipient_id_tmp=await discordbot.getdiscordvar(message,'messenger_recipient_id_tmp')
	if messenger_recipient_id_tmp!=None:
		bot.send_text_message(messenger_recipient_id_tmp, str(content['arg']))
		return 'success!'