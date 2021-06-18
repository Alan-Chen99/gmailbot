from discordbot import bot
from discordbot.tools import regexcommands
#from discordbot.commands.manage import commands as commandsall


class args:#(bot.contextbase):
	pass
	#def __init__(self,argsdict):
	#	self.args=argsdict
	#def __call__(self):
	#	return self.args


commandcall='__makematcher_command'

childcaller=None
def setchildcaller(func):
	global childcaller
	childcaller=func

def childcall(context):
	return childcaller(context)

def commandparser_factory(prefix,strarg=None,opts=[],commandexecutor_arg=None):
	commandexecutor=commandexecutor_arg
	if commandexecutor is None:
		commandexecutor=childcall
	
	optstr=''.join([fr'\.(?P<{x}>\S*?)' for x in opts])
	argstr='$'
	if strarg!=None:
		#r'^echo(\s+(?P<content>[\s\S]*)$|$)'
		argstr=fr'(\.(?P<{commandcall}>[\S\s]*)|(\s+|(?=$))(?P<{strarg}>[\S\s]*))$'
	rs= fr'^{prefix}{optstr}{argstr}'

	async def commandparser(context:bot.Context):
		await regexcommands.match_regex_factory(rs)(context)
		matchrst=context[regexcommands.matchrst]
		argsrst=matchrst.copy()
		context.loccreate(args,argsrst)
		if strarg!=None:
			if argsrst[commandcall]!=None:
				argsrst[strarg]=await commandexecutor(
					context.child({bot.commandtext:argsrst[commandcall]})
				)
			argsrst.pop(commandcall)
	
	return commandparser

def standard(prefix,strarg=None,opts=[],commandexecutor=None):#TODO? maybe keep standard command list seperate
	return bot.runbefore(commandparser_factory(prefix,strarg,opts,commandexecutor))



class standard_command_group(bot.serial_command_group):

	def add(self,prefix,strarg=None,opts=[],commandexecutor=None):
		def internal(command):
			super(standard_command_group,self).add()(standard(prefix,strarg,opts,commandexecutor)(command))
			return command
		return internal

#def standardcommand(func):
#	def internal(context):
#		return func(context[args],context[bot.message])
#	return internal