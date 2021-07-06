import discordbot.bot as bot
from discordbot import defaultvars
from  discordbot.tools import standardcommands
import gmail.bot as gmail

from discordbot.tools.requirements import varreq
from discordbot.tools import requirements


gmailcommands=standardcommands.standard_command_group()

@standardcommands.standard('gmail','content',commandexecutor=gmailcommands)
@varreq(defaultvars.admin)
@bot.command(standardcommands.args)
async def commands(content):
	return content['content']

makematcher=gmailcommands.add


@makematcher('url')
@bot.command()
async def getgmail():
	return gmail.auth_url


@makematcher('id')
@requirements.invert(varreq(defaultvars.email_id,None))
@bot.command(bot.contextall)
async def getid(context):
	return await context[bot.getvar](defaultvars.email_id)

@makematcher('raw')
@requirements.invert(varreq(defaultvars.email_id,None))
@bot.command(bot.contextall)
async def getraw(context):
	emailid=await context[bot.getvar](defaultvars.email_id)
	return await gmail.getrawfromid(emailid)

