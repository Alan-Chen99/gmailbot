#import re
from .bot import client
from discordbot import vars
import logging

class command_failed_exception(Exception):
	pass

class invalid_command_exception(command_failed_exception):
	pass

class invalid_permission_exception(command_failed_exception):
	pass

class context_not_available_exception(command_failed_exception):
	pass

#class contextbase:
#	@classmethod
#	def classid(cls):  
#		return id(cls)

	
#class subcontextclass:
#	def __init__(self):
#		self.x={}
#	def add(self,context):
#		tmp=context.classid()
#		assert(tmp not in self.x)
#		self.x[tmp]=context
#
#	def get(self,contexttype):
#		assert(issubclass(contexttype,contextbase))
#		return self.x[contexttype.classid()]

#class contextclass:
#	def __init__(self,glob=None,loc=None):
#		if loc is None:
#			loc=subcontextclass()
#		if glob is None:
#			glob=subcontextclass()
#		self.loc=loc
#		self.glob=glob
#	def child(self):
#		return contextclass(self.glob,None)

class Context:
	def __init__(self,glob=None,loc=None):
		if loc is None:
			loc={}
		if glob is None:
			glob={}
		self.loc=loc
		self.glob=glob
	def __getitem__(self,key):
		if key in self.loc:
			assert(key not in self.glob)
			return self.loc[key]
		return self.glob[key]
	def globcreate(self,key,val):
		assert(key not in self.glob)
		assert(key not in self.loc)
		self.glob[key]=val
	def loccreate(self,key,val):
		assert(key not in self.glob)
		assert(key not in self.loc)
		self.loc[key]=val
	def child(self,newloc=None):
		return Context(glob=self.glob,loc=newloc)
	def have(self,key):
		if key in self.loc:
			return True
		if key in self.glob:
			return True
		return False
		
	

class serial_command_group:
	def __init__(self):
		self.commandlist=[]

	def add(self):
		def internal(command):
			self.commandlist.append(command)
			return command
		return internal

	async def __call__(self,context):#TODO: type checking
		assert(type(context) is Context)
		for command in self.commandlist:
			try:
				#print(repr(command))
				return await command(context)
			except command_failed_exception:
				pass
		raise command_failed_exception()

def runbefore(commandprev):#decorator
	def internal(command):
		async def runner(context):
			assert(type(context) is Context)
			await commandprev(context)
			return await command(context)
		return runner
	return internal

def runafter(commandnext):#decorator
	def internal(command):
		async def runner(context):
			assert(type(context) is Context)
			tmp=await command(context)
			await commandnext(context)
			return tmp
		return runner
	return internal

class contextall:
	pass

def command(*args,**kargs):#kargs
	def internal(handler):
		def runner(context):
			argsnew=[]
			for x in args:
				if x is contextall:
					argsnew.append(context)
				elif context.have(x):
					argsnew.append(context[x])
				else:
					raise context_not_available_exception()
			
			kargsnew={}
			for argname,x in kargs.items():
				if x is contextall:
					kargsnew[argname]=context
				elif context.have(x):
					kargsnew[argname]=context[x]
				else:
					raise context_not_available_exception()
			return handler(*argsnew,**kargsnew)
		return runner
	return internal

class commandtext:
	pass

class message:
	pass
	#def __init__(self,mes):
	#	self.message=mes
	#def __call__(self):
	#	return self.message

class getvar:#contains a function that takes str and outputs a coro that returns the var
	pass

message_handler=None
def set_message_handler(handler):#should be a async func with (message,context) as arg
	global message_handler
	message_handler=handler

def run_message_handler(context):
	if message_handler is not None:
		return message_handler(context)


@client.event
async def on_message(messageobj):
	global message_handler
	#if message.author == client.user:#DONE: implement this downstream
	#	return
	if message_handler is not None:
		try:
			context=Context()
			context.globcreate(message,messageobj)
			context.loccreate(commandtext,messageobj.content)
			async def getvarfunc(varname):
				return await vars.getdiscordvar(messageobj,varname)
			context.globcreate(getvar,getvarfunc)
			await message_handler(context)
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