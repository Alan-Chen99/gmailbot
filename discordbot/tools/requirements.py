from discordbot.tools.context import getmessage
from discordbot.vars import getdiscordvar
from discordbot.bot import invalid_permission_exception

class req:
	def __init__(self,func):
		#coro takes (commandtext,context) and returns bool
		self.func=func
	def __call__(self,callback):
		async def internal(commandtext,context):
			tmp=await self.func(commandtext,context)
			if tmp is True:
				return await callback(commandtext,context)
			elif tmp is False:
				raise invalid_permission_exception()
			else:
				raise ValueError('requirements must return bool')
		return internal
	#TODO: and, or, etc
def invert(reqobj):
	async def internal(commandtext,context):
		return not (await reqobj.func(commandtext,context))
	return req(internal)


def varreq(varname,value=True):
	async def internal(commandtext,context):
		message=getmessage(context)
		tmp=await getdiscordvar(message,varname)
		return tmp==value
	return req(internal)