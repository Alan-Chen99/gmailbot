from discordbot import bot
from discordbot.tools import requirements
from discordbot.tools import ratelimit
from discordbot.tools import standardcommands
from discordbot.tools import messaging

import logging
#TODO: change?
import discordbot.defaultvars

full_commands_list=bot.serial_command_group()


#@ratelimit.use(1)
#async def commands(commandtext,context):
#	return await full_commands_list(commandtext,context)

def addcommand(command):
	full_commands_list.add()(command)

#@ratelimit.usemessage
#def use_message_ratelimit(commandtext,context):
#	pass
standardcommands.setchildcaller(ratelimit.use(1)(full_commands_list))


async def runall(context:bot.Context):
	assert(type(context) is bot.Context)
	
	rst=await full_commands_list(context)
	if rst is not None:
		await messaging.reply(context)(rst)



#handle rate limits


withratelimit=bot.serial_command_group()

@withratelimit.add()
@requirements.varreq('admin')
@ratelimit.setlimit(float('inf'))
async def runasadmin(context):
	return await runall(context)

@withratelimit.add()
@requirements.invert(requirements.varreq('admin'))
@ratelimit.setlimit(30)
async def runwithratelimit(context):
	return await runall(context)


async def runwithselfcheck(context:bot.Context):
	assert(type(context) is bot.Context)
	message=context[bot.message]

	if message.author==bot.client.user:
		ifnoselfcheck=await context[bot.getvar]('surpress_self_check')
		if not ifnoselfcheck:
			raise bot.invalid_permission_exception()
	prefix=await context[bot.getvar]('prefix')
	if not context[bot.commandtext].startswith(prefix):
		raise bot.command_failed_exception()
	newchild=context.child({bot.commandtext: context[bot.commandtext][len(prefix):]})
	await withratelimit(newchild)
	#await withratelimit(context)


bot.set_message_handler(runwithselfcheck)
