import discordbot.bot as bot
from discordbot import vars
#from discordbot.tools import ratelimit
#from discordbot.tools import context as ctools
import utils.crypto
import utils.exceptions
from discordbot.tools import standardcommands
from discordbot.tools.requirements import varreq
import firebase
#from firebase.cache import printdebug
import reseter

import sys
from discordbot import defaultvars

commands=bot.serial_command_group()

admincommands=standardcommands.standard_command_group()
commands.add()(varreq(defaultvars.admin)(admincommands))

nonadmincommands=standardcommands.standard_command_group()
commands.add()(nonadmincommands)

makematcher=admincommands.add
#newcommand=bot.command(standardcommands.args,bot.message)


@nonadmincommands.add('adminverify','key')
@bot.command(standardcommands.args,bot.message)
async def botadminverify(content,message):
	key=content['key']
	if utils.crypto.verhash(key,utils.crypto.getenv('discord_user_pwd_hash')):
		await vars.setdiscordvar(message,vars.levels.author,defaultvars.admin,True)
		return 'admin permission added'
	else:
		return 'password incorrect'


@makematcher('abort')
@bot.command()
async def botabort():
	sys.exit(0)


@makematcher('set','val',['level','var'])
@bot.command(standardcommands.args,bot.message)
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
@bot.command()
async def botgetdb():
	return await firebase.init()()


#@makematcher('debug')
#@bot.command()
#async def botdebug():
#	await printdebug()

@makematcher('print','content')
@bot.command(standardcommands.args)
async def botprint(content):
	tmp=content['content']
	print(tmp)
	return tmp

@makematcher('get')
@bot.command(bot.message)
async def botget(message):
	rst={}
	for x in vars.discord_default_vars:
		rst[x]=await vars.getdiscordvar(message,x)
	return rst

#@makematcher('resetdb')#TODO: warn
#@bot.command(bot.message)
#async def botresetdb(message):
#	await reseter.fullreset()
#	await vars.setdiscordvar(message,vars.levels.author,defaultvars.admin,True)
#	return 'database reseted'

@makematcher('resetdefaults')
@bot.command()
async def botresetdefaults():
	await vars.resetdiscordvarsdefault()
	return 'database default vars reseted'


def execfromref_factory(giveadmin,skipselfcheck):
	async def execfromref(context):
		message=context[bot.message]
		
		#https://stackoverflow.com/questions/66016979/discord-py-send-a-different-message-if-a-user-replies-to-my-bot
		if message.reference is not None:
			if message.reference.cached_message is None:
				# Fetching the message
				channel = bot.client.get_channel(message.reference.channel_id)
				refmsg = await channel.fetch_message(message.reference.message_id)

			else:
				refmsg = message.reference.cached_message

			try:
				newcontext=bot.Context()
				newcontext.globcreate(bot.message,refmsg)
				newcontext.loccreate(bot.commandtext,context[bot.commandtext])
				async def getvarfunc(varname):
					if giveadmin and varname==defaultvars.admin:
						return True
					if skipselfcheck and varname==defaultvars.surpress_self_check:
						return True
					return await vars.getdiscordvar(refmsg,varname)
				newcontext.globcreate(bot.getvar,getvarfunc)

				return await bot.run_message_handler(newcontext)
			except bot.command_failed_exception:
				return 'command failed'
			except Exception as e:
				return utils.exceptions.excpetiontostring(e)
		else:
			return 'no messeage is referenced'
	
	return execfromref


@makematcher('ref','content',commandexecutor=execfromref_factory(False,False))
@bot.command(standardcommands.args)
async def botref(content):
	return content['content']


@makematcher('refadmin','content',commandexecutor=execfromref_factory(True,True))
@bot.command(standardcommands.args)
async def botrefadmin(content):
	return content['content']


@makematcher('setlogging','prefix',['type'])
@bot.command(standardcommands.args,bot.message)
async def botsetlogging(content,message):
	bot.setstream(content['type'],message.channel,{'prefix':content['prefix']})
	return 'success!'

@makematcher('setlogging_cat','prefix',['type'])
@bot.command(standardcommands.args,bot.message)
async def botsetlogging_cat(content,message):
	bot.setstream_cat(content['type'],message.channel.category,{'prefix':content['prefix']})
	return 'success!'
	




@makematcher('testexception')
@bot.command()
async def testexception():
	return 1/0