import discordbot.bot as bot

class ratelimiter:
	def __init__(self,limit):
		self.used=0
		self.limit=limit
		self.havesenderror=False

class ratelimitexceeded(bot.command_failed_exception):
	pass

def setlimit_factory(limit):
	async def setlimit_command(context:bot.Context):
		assert(type(context) is bot.Context)
		context.globcreate(ratelimiter,ratelimiter(limit))
	return setlimit_command

def setlimit(limit):
	return bot.runbefore(setlimit_factory(limit))

def uselimit_factory(usage):
	async def uselimit_command(context:bot.Context):
		assert(type(context) is bot.Context)
		limiter=context[ratelimiter]
		limiter.used+=usage
		if limiter.used>limiter.limit:
			raise ratelimitexceeded()
	return uselimit_command

def use(usage):
	return bot.runbefore(uselimit_factory(usage))

usemessage=use(10)