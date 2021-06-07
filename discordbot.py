import discord
import re
import database
import utils
import logging
import io

haveinitialized=False

discord_default_vars=[]
discord_vars_prefix='discord_'

def adddefaultvar(var,default):
	discord_default_vars.append((var,default))

@database.onreset
async def resetdiscordvars():
	for x in discord_default_vars:
		await database.setvar(discord_vars_prefix+x[0],{'default':x[1]})

async def changevar(var,key,val):
	var=discord_vars_prefix+var
	havevar=await database.havevar(var)
	if havevar:
		curdict=await database.getvar(var)
		curdict[str(key)]=val
		await database.setvar(var,curdict)
	else:
		await database.setvar(var,{str(key):val})

async def resetdiscordvarsdefault():
	for x in discord_default_vars:
		await changevar(x[0],'default',x[1])

alldiscordcommands=[]

client = discord.Client()

alldiscordvarlevels=[]

def newvarlevel(level):
	def newvarlevelinner(func):
		alldiscordvarlevels.append((level,func))
		return None
	return newvarlevelinner

async def getdiscordvar(message,var):
	var=discord_vars_prefix+var
	curlist=await database.getvar(var)
	for x in alldiscordvarlevels:
		tmp = str(await (x[1])(message))
		if tmp in curlist:
			return curlist[tmp]
	assert(False)

async def havelevel(level):
	for x in alldiscordvarlevels:
		if x[0]==level:
			return True
	return False

async def setdiscordvar(message,level,var,val):
	for x in alldiscordvarlevels:
		if x[0]==level:
			tmp = str(await (x[1])(message))
			if tmp!=None:
				await changevar(var,tmp,val)

async def filefromstring(text,filename=None):
	f = io.StringIO(str(text))
	if filename==None:
		filename="file.txt"
	return discord.File(fp=f,filename=filename)

async def sendloggingmessage(target,text,**kwargs):
	loggers=await getdiscordvar(None,'logging')
	#print(loggers)
	logger=loggers.get(target)
	if logger!=None:
		loggingprefix=logger.get('prefix')
		#if loggingprefix is not None:
		text=loggingprefix+text
		channelid=logger.get('channel')
		#if channelid is not None:
		await client.get_channel(channelid).send(text,**kwargs)


def newcommand(func):#func, matches, requirements
	tmp=(func,[],[])
	alldiscordcommands.append(tmp)
	return tmp

async def matcherhandlernothing(groups,message):
	return groups

def addmatcher(commandregex,handler=matcherhandlernothing):
	def newcommand_inner(command):
		command[1].append((commandregex,handler))
		return command
	return newcommand_inner


commandcall='__makematcher_command'
#directstr='__makematcher_str'

def makematcher(prefix,strarg=None,opts=[]):
	async def matchercommandhandler(groups,message):
		if strarg==None:
			return groups
		if groups[commandcall]!=None:
			tryrunrst=await tryrun(groups[commandcall],message,False)
			if tryrunrst[0]:
				groups[strarg]=tryrunrst[1]
			else:
				pass #reply error?
		groups.pop(commandcall)
		return groups

	optstr=''.join([fr'\.(?P<{x}>\S*?)' for x in opts])
	argstr='$'
	if strarg!=None:
		#r'^echo(\s+(?P<content>[\s\S]*)$|$)'
		argstr=fr'(\.(?P<{commandcall}>[\S\s]*)|(\s+|(?=$))(?P<{strarg}>[\S\s]*))$'
	rs= fr'^{prefix}{optstr}{argstr}'
	#print(rs)
	return addmatcher(rs,matchercommandhandler)


def addrequirement(func):
	def addrequirement_inner(command):
		command[2].append(func)
		return command
	return addrequirement_inner

def varrequirement(var,val=True):
	async def withvar(message):
		tmp = await getdiscordvar(message,var)
		return tmp==val
	return withvar

def requirevar(var,val=True):
	return addrequirement(varrequirement(var,val))


#https://stackoverflow.com/questions/65894198/discord-py-send-message-under-different-name-or-user
async def sendastest(message,member: discord.Member, content):
	webhook = await message.channel.create_webhook(name=member.name)
	await webhook.send(
		str(content), username=member.name, avatar_url=member.avatar_url)
	webhooks = await message.channel.webhooks()
	for webhook in webhooks:
		await webhook.delete()


async def tryrun(content,message,reply=True):
	for command in alldiscordcommands:
		havereq=True
		for req in command[2]:
			if (await req(message))!=True:
				havereq=False
				break
		if havereq:
			for rg in command[1]:
				#print(rg)
				#print(content)
				mr=re.search(rg[0],content)
				if mr:
					groups=mr.groupdict()
					groups=await rg[1](groups,message)
					rst=await command[0](groups,message)
					if reply and (rst is not None):
						if rst=='':
							await message.reply('the command succeeded, but it returned an empty string')
						else: await message.reply(rst)
					return (True,rst)
	return (False,None)


async def handlemessage(message):
	messagecontent=message.content
	
	#TODO: regex as prefix?
	curprefix=await getdiscordvar(message,'prefix')
	if messagecontent.startswith(curprefix):	
		content=messagecontent[len(curprefix):]#TODO: do this create new copy?
		if (await tryrun(content,message))[0]:
			return

	pingstr=f'<@!{str(client.user.id)}>.'#direct ping have !, and role ping have &
	#print(pingstr)
	#print(messagecontent)
	if messagecontent.startswith(pingstr):
		content=messagecontent[len(pingstr):]#TODO: do this create new copy?
		if (await tryrun(content,message))[0]:
			return


	#print(messagecontent)
	#restr=r'^<@\&'+str(client.user.id)+r'>\s*(?P<content>[\s\S]*)$'
	#print(restr)
	#rerst=re.search(restr,messagecontent)
	#if rerst:
	#	print('success!')
	#	messagecontent=rerst.groups()['content']
	#	await tryrun(messagecontent,message)
		
		

'''
	if messagecontent.startswith(universalprefix):
		messagecontent=messagecontent[len(universalprefix):]
		
		res = re.search(r'\s', messagecontent)

		if res is None:
			messageprefix=messagecontent
			messagecontent=''
		else:
			messageprefix=messagecontent[:res.start()]
			messagecontent=messagecontent[res.start()+1:]

		if messageprefix in alldiscordcommands:
			rst=await alldiscordcommands[messageprefix](messagecontent,message)
		else:
			rst=f'command {universalprefix+messageprefix} does not exist'
		if rst is not None:
			await message.reply(rst)
		
		#print(repr(messageprefix))
		#print(repr(messagecontent))
'''		


ondiscordreadylist=[]#list of corutines that needs to run upon discord ready

def ondiscordready(func):
	ondiscordreadylist.append(func())
	return func

@client.event
async def on_ready():
	global haveinitialized
	await sendloggingmessage('info',f'i am initialized at {utils.timestringnow()}')
	for x in ondiscordreadylist:
		client.loop.create_task(x)
	haveinitialized=True
	print('We have logged in as {0.user}'.format(client))
	

@client.event
async def on_message(message):
	global targetchannel
	if message.author == client.user:
		return
	try:
		await handlemessage(message)
	except Exception as e:
		logging.exception(e)