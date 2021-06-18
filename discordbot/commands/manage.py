from discordbot import bot
from discordbot.tools import requirements
from discordbot.tools import ratelimit
from discordbot.tools import standardcommands
from discordbot.tools import messaging

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


async def runall(context:bot.Context):
	assert(type(context) is bot.Context)
	message=context[bot.message]
	ifnoselfcheck=await context[bot.getvar]('surpress_self_check')
	
	if message.author==bot.client.user and ifnoselfcheck is False:
		raise bot.invalid_permission_exception()
	
	rst=await full_commands_list(context)
	if rst is not None:
		await messaging.reply(context)(rst)

standardcommands.setchildcaller(ratelimit.use(1)(full_commands_list))


#handle rate limits


finalcommands=bot.serial_command_group()

@finalcommands.add()
@requirements.varreq('admin')
@ratelimit.setlimit(float('inf'))
async def runasadmin(context):
	return await runall(context)

@finalcommands.add()
@requirements.invert(requirements.varreq('admin'))
@ratelimit.setlimit(30)
async def runwithratelimit(context):
	return await runall(context)



bot.set_message_handler(finalcommands)
