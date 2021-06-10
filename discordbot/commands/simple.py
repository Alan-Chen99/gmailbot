import discordbot.bot as bot
#from discordbot.tools import ratelimit
#from discordbot.tools import context as ctools
from  discordbot.tools import standardcommands


commands=standardcommands.standard_command_group()
makematcher=commands.add
newcommand=standardcommands.standardcommand



@makematcher('ping')
@newcommand
async def botping(content,message):
	return 'pong'


@makematcher('pass')
@newcommand
async def botpass(content,message):
	pass

@makematcher('latency')
@newcommand
async def botlatency(content,message):
	tmp=await message.reply('Loading data',mention_author=False)
	timetake=(tmp.created_at - message.created_at).total_seconds()*1000
	await tmp.edit(content=f'latency is {timetake} ms, API latency is {bot.client.latency*1000} ms')
	return None

