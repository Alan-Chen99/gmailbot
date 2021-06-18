#import discordbot.bot
#import discordbot.vars
#def getmessage(context:discordbot.bot.Context):
#	return context[discordbot.bot.message]

#async def getvar(context:discordbot.bot.Context,varname:str):
#	return await discordbot.vars.getdiscordvar(getmessage(context),varname)


#import discordbot.tools.regexcommands
#def getregexgroup(context):
#	return context.loc.get(discordbot.tools.regexcommands.matchrst)()

