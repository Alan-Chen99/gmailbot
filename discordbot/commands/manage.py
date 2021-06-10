from discordbot import bot
from discordbot.tools import requirements
from discordbot.tools import ratelimit

full_commands_list=bot.serial_command_group()


@ratelimit.use(1)
async def commands(commandtext,context):
	return await full_commands_list(commandtext,context)

def addcommand(command):
	full_commands_list.add()(command)

async def runall(commandtext,context):
	message=context.glob.get(bot.message).message
	if message.author==bot.client.user:
		return
	rst=await commands(commandtext,context)
	if rst is not None:
		await message.reply(rst)

#handle rate limits



finalcommands=bot.serial_command_group()

@finalcommands.add()
@requirements.varreq('admin')
@ratelimit.setlimit(float('inf'))
async def runasadmin(commandtext,context):
	return await runall(commandtext,context)

@finalcommands.add()
@requirements.invert(requirements.varreq('admin'))
@ratelimit.setlimit(5)
async def runwithratelimit(commandtext,context):
	return await runall(commandtext,context)



bot.set_message_handler(finalcommands)