import discordbot.bot
def getmessage(context):
	return context.glob.get(discordbot.bot.message)()


import discordbot.tools.regexcommands
def getregexgroup(context):
	return context.loc.get(discordbot.tools.regexcommands.matchrst)()
