from discordbot import bot
import re


class matchrst:
	pass
	#def __init__(self,group):
	#	self.group=group
	#def __call__(self):
	#	return self.group

def match_regex_factory(commandregex):
	async def match_regex(context:bot.Context):
		mr=re.search(commandregex,context[bot.commandtext])
		if mr:
			groups=mr.groupdict()
			context.loccreate(matchrst,groups)
		else:
			raise bot.invalid_command_exception()
	return match_regex

def regex(commandregex,hidden=False):#TODO: keep list of regexes
	return bot.runbefore(match_regex_factory(commandregex))


class regex_command_group(bot.serial_command_group):
	def add(self,commandregex,hidden=False):
		def newcommand_inner(command):
			super(regex_command_group,self).add()(regex(commandregex,hidden)(command))
			return command
		return newcommand_inner


#def regexcommand(func):
#	def internal(context):
#		return func(context[matchrst],context[bot.message])
#	return internal

'''

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

'''


'''
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

'''