from discordbot import bot
from discordbot.tools import ratelimit

@ratelimit.usemessage
async def usemessagedummy(context):
	pass


def reply(context:bot.Context):
	assert(type(context) is bot.Context)
	async def internal(content=None,**kargs):
		if not content and not kargs:
			return
		await usemessagedummy(context)
		await context[bot.message].reply(content,**kargs)
	return internal

def sendchannel(context:bot.Context):
	assert(type(context) is bot.Context)
	async def internal(content=None,**kargs):
		if not content and not kargs:
			return
		await usemessagedummy(context)
		await context[bot.message].channel.send(content,**kargs)
	return internal