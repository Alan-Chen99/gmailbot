#from discordbot.tools.context import getmessage
from discordbot.bot import invalid_permission_exception
import discordbot.bot

class req:
	def __init__(self,func):
		#coro takes (commandtext,context) and returns bool
		self.func=func
	def __call__(self,callback):
		async def internal(context):
			tmp=await self.func(context)
			if tmp is True:
				return await callback(context)
			elif tmp is False:
				raise invalid_permission_exception()
			else:
				raise ValueError('requirements must return bool')
		return internal
	#TODO: and, or, etc
def invert(reqobj):
	async def internal(context):
		return not (await reqobj.func(context))
	return req(internal)


def varreq(varname,value=True):
	async def internal(context):
		tmp=await context[discordbot.bot.getvar](varname)
		return tmp==value
	return req(internal)