from discordbot import bot
from discordbot.tools import regexcommands
#from discordbot.commands.manage import commands as commandsall


class args(bot.contextbase):
	def __init__(self,argsdict):
		self.args=argsdict
	def __call__(self):
		return self.args


commandcall='__makematcher_command'

childcaller=None
def setchildcaller(func):
	global childcaller
	childcaller=func

class standard_command_group(regexcommands.regex_command_group):

	def add(self,prefix,strarg=None,opts=[],commandexecutor=None):
		if commandexecutor is None:
			commandexecutor=childcaller
		optstr=''.join([fr'\.(?P<{x}>\S*?)' for x in opts])
		argstr='$'
		if strarg!=None:
			#r'^echo(\s+(?P<content>[\s\S]*)$|$)'
			argstr=fr'(\.(?P<{commandcall}>[\S\s]*)|(\s+|(?=$))(?P<{strarg}>[\S\s]*))$'
		rs= fr'^{prefix}{optstr}{argstr}'

		def newcommand_inner(command):
			async def internal(commandtext,context):
				matchrst=context.loc.get(regexcommands.matchrst)()
				argsrst=matchrst.copy()
				context.loc.add(args(argsrst))
				if strarg!=None:
					if argsrst[commandcall]!=None:
						argsrst[strarg]=await commandexecutor(argsrst[commandcall],context.child())
					argsrst.pop(commandcall)
				return await command(commandtext,context)

			super(standard_command_group,self).add(rs)(internal)
			return command
		return newcommand_inner

def standardcommand(func):
	def internal(commandtext,context):
		return func(context.loc.get(args)(),context.glob.get(bot.message)())
	return internal