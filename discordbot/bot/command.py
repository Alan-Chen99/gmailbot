#import re
from .bot import client
import logging

class command_failed_exception(Exception):
	pass

class invalid_command_exception(command_failed_exception):
	pass

class invalid_permission_exception(command_failed_exception):
	pass


class serial_command_group:
	def __init__(self):
		self.commandlist=[]

	def add(self):
		def internal(command):
			self.commandlist.append(command)
			return command
		return internal

	async def __call__(self,commandtext,context):#TODO: type checking
		for command in self.commandlist:
			try:
				#print(repr(command))
				return await command(commandtext,context)
			except command_failed_exception:
				pass
		raise command_failed_exception()



class contextbase:
	@classmethod
	def classid(cls):  
		return id(cls)

	
class subcontextclass:
	def __init__(self):
		self.x={}
	def add(self,context):
		tmp=context.classid()
		assert(tmp not in self.x)
		self.x[tmp]=context

	def get(self,contexttype):
		assert(issubclass(contexttype,contextbase))
		return self.x[contexttype.classid()]

class contextclass:
	def __init__(self,glob=None,loc=None):
		if loc is None:
			loc=subcontextclass()
		if glob is None:
			glob=subcontextclass()
		self.loc=loc
		self.glob=glob
	def child(self):
		return contextclass(self.glob,None)



class message(contextbase):
	def __init__(self,mes):
		self.message=mes
	def __call__(self):
		return self.message


message_handler=None
def set_message_handler(handler):#should be a async func with (message,context) as arg
	global message_handler
	message_handler=handler


@client.event
async def on_message(messageobj):
	global message_handler
	#if message.author == client.user:#TODO: implement this downstream
	#	return
	if message_handler is not None:
		try:
			context=contextclass()
			context.glob.add(message(messageobj))
			await message_handler(messageobj.content,context)
		except command_failed_exception:
			pass
		except Exception as e:
			logging.exception(e)



'''


regexcommands=serial_command_group()


class regexcommand:
	def __init__(self,func):
		self.func=func

async def matcherhandlernothing(groups,context):
	return groups

def regexmatcher(commandregex,handler=matcherhandlernothing):
	def newcommand_inner(command):
		assert(type(command) is regexcommand)
		
		@regexcommands.add
		def internal(commandtext,context):
			mr=re.search(commandregex,commandtext)
			if mr:
				groups=mr.groupdict()
				groups=await handler(groups,context)
				return await command.func(groups,context)
			else:
				raise invalid_command_exception()

		return command
	return newcommand_inner


def addregexrequirement(func):#func takes (groups,context)
	def addrequirement_inner(command):
		
		
		command[2].append(func)
		return command
	return addrequirement_inner





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

'''