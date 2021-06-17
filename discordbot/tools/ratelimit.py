import discordbot.bot as bot

class ratelimiter(bot.contextbase):
	def __init__(self,limit):
		self.used=0
		self.limit=limit

class ratelimitexceeded(bot.command_failed_exception):
	pass

def setlimit(limit):
	def internal(func):
		def rstfunc(commandtext,context):
			tmp=context.glob
			assert(type(tmp) is bot.subcontextclass)
			tmp.add(ratelimiter(limit))
			return func(commandtext,context)
		return rstfunc
	return internal

def use(usage):
	def internal(func):
		def rstfunc(commandtext,context):
			tmp=context.glob
			assert(type(tmp) is bot.subcontextclass)
			limiter=tmp.get(ratelimiter)
			limiter.used+=usage
			if limiter.used>limiter.limit:
				raise ratelimitexceeded()
			return func(commandtext,context)
		return rstfunc
	return internal


usemessage=use(10)