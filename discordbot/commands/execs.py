from discordbot.tools import regexcommands
from discordbot.tools import context as ctools
import utils.exceptions



commands=regexcommands.regex_command_group()


@commands.add(r'^eval\s+(?P<arg>[\s\S]*)$')
@commands.add(r'^eval\s+`(?P<arg>[\s\S]*)`$')
@commands.add(r'^eval\s+```(?P<arg>[\s\S]*)```$')
async def boteval(commandtext,context):
	group=ctools.getregexgroup(context)
	message=ctools.getmessage(context)
	try:
		tmp=eval(group['arg'])
		await message.reply(tmp)
	except Exception as e:
		await message.reply(utils.exceptions.excpetiontostring(e))


#@requirevar('admin')



'''
async def boteval(content,message):
	try:
		tmp=eval(content['arg'])
	except Exception as e:
		return utils.excpetiontostring(e)
	return tmp

#https://stackoverflow.com/questions/44859165/async-exec-in-python
async def aexec(code):
	# Make an async function with the code and `exec` it
	try:
		exec(
			f'async def __aexecinternal(): ' +
			''.join(f'\n {l}' for l in code.split('\n'))
		)
		# Get `__aexecinternal` from local variables, call it and return the result
		tmp=await locals()['__aexecinternal']()
	except Exception as e:
		return utils.excpetiontostring(e)
	return tmp


@addmatcher(r'^exec\s+(?P<arg>[\s\S]*)$')
@addmatcher(r'^exec\s+`(?P<arg>[\s\S]*)`$')
@addmatcher(r'^exec\s+```(?P<arg>[\s\S]*)```$')
@requirevar('admin')
@newcommand
async def botexec(content,message):
	loc=locals()
	try:
		exec(content['arg'], globals(), loc)
	except Exception as e:
		return utils.excpetiontostring(e)
	loccopy = dict(loc)
	loccopy.pop('content')
	loccopy.pop('message')
	return loccopy

@addmatcher(r'^aexec\s+(?P<arg>[\s\S]*)$')
@addmatcher(r'^aexec\s+`(?P<arg>[\s\S]*)`$')
@addmatcher(r'^aexec\s+```(?P<arg>[\s\S]*)```$')
@requirevar('admin')
@newcommand
async def botaexec(content,message):
	loc=locals()
	try:
		rst=await aexec(content['arg'])
	except Exception as e:
		return e
	return rst


	'''