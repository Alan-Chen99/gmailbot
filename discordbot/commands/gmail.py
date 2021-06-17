#import discordbot.bot as bot
#from discordbot.tools import ratelimit
from  discordbot.tools import standardcommands
import gmail.bot as gmail

commands=standardcommands.standard_command_group()
makematcher=commands.add
newcommand=standardcommands.standardcommand



@makematcher('getgmail')
@newcommand
async def getgmail(content,message):
	return gmail.auth_url


@makematcher('getgmail')
@newcommand
async def botping(content,message):
	return gmail.auth_url
