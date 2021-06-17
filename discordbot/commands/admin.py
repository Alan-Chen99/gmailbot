import discordbot.bot as bot
from discordbot import vars
#from discordbot.tools import ratelimit
from discordbot.tools import context as ctools
import utils.crypto
import utils.exceptions
from discordbot.tools import standardcommands
from discordbot.tools.requirements import varreq
import firebase
from firebase.cache import printdebug
import reseter

commands=bot.serial_command_group()

admincommands=standardcommands.standard_command_group()
commands.add()(varreq('admin')(admincommands))

nonadmincommands=standardcommands.standard_command_group()
commands.add()(nonadmincommands)

makematcher=admincommands.add
newcommand=standardcommands.standardcommand


@nonadmincommands.add('adminverify','key')
@newcommand
async def botadminverify(content,message):
	key=content['key']
	if utils.crypto.verhash(key,utils.crypto.discord_user_pwd_hash):
		await vars.setdiscordvar(message,'author','admin',True)
		return 'admin permission added'
	else:
		return 'password incorrect'


@makematcher('set','val',['level','var'])
@newcommand
async def botset(content,message):
	level=content['level']
	tmp=await vars.havelevel(level)
	if tmp==False:
		return f'{level} is not a valid level'
	var=content['var']
	val=content['val']
	await vars.setdiscordvar(message,level,var,val)
	return 'success!'


@makematcher('getdb')
@newcommand
async def botgetdb(content,message):
	#print('getting db')
	return await firebase.init()()

@makematcher('debug')
@newcommand
async def botdebug(content,message):
	await printdebug()

@makematcher('print','content')
@newcommand
async def botprint(content,message):
	tmp=content['content']
	print(tmp)
	return tmp

@makematcher('get')
@newcommand
async def botget(content,message):
	rst={}
	for x in vars.discord_default_vars:
		rst[x]=await vars.getdiscordvar(message,x)
	return rst

@makematcher('resetdb')
@newcommand
async def botresetdb(content,message):
	await reseter.fullreset()
	await vars.setdiscordvar(message,'author','admin',True)
	return 'database reseted'

@makematcher('resetdefaults')
@newcommand
async def botresetdefaults(content,message):
	await vars.resetdiscordvarsdefault()
	return 'database default vars reseted'


async def execfromref(commandtext,context):
	message=ctools.getmessage(context)
	
	#https://stackoverflow.com/questions/66016979/discord-py-send-a-different-message-if-a-user-replies-to-my-bot
	if message.reference is not None:
		if message.reference.cached_message is None:
			# Fetching the message
			channel = bot.client.get_channel(message.reference.channel_id)
			refmsg = await channel.fetch_message(message.reference.message_id)

		else:
			refmsg = message.reference.cached_message

		try:
			newcontext=bot.contextclass()
			newcontext.glob.add(bot.message(refmsg))
			return await bot.run_message_handler(commandtext,newcontext)
		except bot.command_failed_exception:
			return 'command failed'
		except Exception as e:
			return utils.exceptions.excpetiontostring(e)
	else:
		return 'no messeage is referenced'


@makematcher('ref','content',commandexecutor=execfromref)
@newcommand
async def botref(content,message):
	return content['content']

async def execfromrefadmin(commandtext,context):
	message=ctools.getmessage(context)
	
	#https://stackoverflow.com/questions/66016979/discord-py-send-a-different-message-if-a-user-replies-to-my-bot
	if message.reference is not None:
		if message.reference.cached_message is None:
			# Fetching the message
			channel = bot.client.get_channel(message.reference.channel_id)
			refmsg = await channel.fetch_message(message.reference.message_id)

		else:
			refmsg = message.reference.cached_message

		#pastvar=await vars.getdiscordvar(refmsg,'admin')
		#TODO: maybe return to past?
		await vars.setdiscordvar(refmsg,vars.levels.message,'admin',True)

		try:
			newcontext=bot.contextclass()
			newcontext.glob.add(bot.message(refmsg))
			return await bot.run_message_handler(commandtext,newcontext)
		except bot.command_failed_exception:
			return 'command failed'
		except Exception as e:
			return utils.exceptions.excpetiontostring(e)
		finally:
			await vars.setdiscordvar(refmsg,vars.levels.message,'admin',None)
	else:
		return 'no messeage is referenced'


@makematcher('refadmin','content',commandexecutor=execfromrefadmin)
@newcommand
async def botrefadmin(content,message):
	return content['content']


@makematcher('setlogging','prefix',['type'])#TODO
@newcommand
async def botsetlogging(content,message):
	bot.setstream(content['type'],message.channel,{'prefix':content['prefix']})
	return 'success!'