#import discordbot.bot as bot
from discordbot import vars
#from discordbot.tools import ratelimit
#from discordbot.tools import context as ctools
import utils.crypto
from discordbot.tools import standardcommands
from discordbot.tools.requirements import varreq
import firebase
from firebase.cache import printdebug

commands=standardcommands.standard_command_group()
makematcher=commands.add
newcommand=standardcommands.standardcommand


@makematcher('adminverify','key')
@newcommand
async def botadminverify(content,message):
	key=content['key']
	if utils.crypto.verhash(key,utils.crypto.discord_user_pwd_hash):
		await vars.setdiscordvar(message,'author','admin',True)
		return 'admin permission added'
	else:
		return 'password incorrect'


'''
@makematcher('set','val',['level','var'])
@varreq('admin')
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
@varreq('admin')
@newcommand
async def botgetdb(content,message):
	#print('getting db')
	return repr(await firebase.init()())

@makematcher('debug')
@varreq('admin')
@newcommand
async def botdebug(content,message):
	await printdebug()
'''
@makematcher('reqtest')
@varreq('admin')
@newcommand
async def botdebug(content,message):
	return 'success'