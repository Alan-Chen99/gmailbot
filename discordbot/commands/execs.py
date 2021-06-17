from discordbot.tools import regexcommands
from discordbot.tools.requirements import varreq
#from discordbot.tools import context as ctools
import utils.exceptions






commandgroup=regexcommands.regex_command_group()
addmatcher=commandgroup.add
newcommand=regexcommands.regexcommand

commands=varreq('admin')(commandgroup)

#@requirevar('admin')


@addmatcher(r'^eval\s+(?P<arg>[\s\S]*)$')
@addmatcher(r'^eval\s+`(?P<arg>[\s\S]*)`$')
@addmatcher(r'^eval\s+```(?P<arg>[\s\S]*)```$')
@newcommand
async def boteval(content,message):
	try:
		tmp=eval(content['arg'])
	except Exception as e:
		return utils.exceptions.excpetiontostring(e)
	return tmp

#https://stackoverflow.com/questions/44859165/async-exec-in-python
async def aexec(code,message):
	# Make an async function with the code and `exec` it
	try:
		exec(
			f'async def __aexecinternal(message): ' +
			''.join(f'\n {l}' for l in code.split('\n'))
			#globals()
		)
		# Get `__aexecinternal` from local variables, call it and return the result
		tmp=await locals()['__aexecinternal'](message)
	except Exception as e:
		return utils.exceptions.excpetiontostring(e)
	return tmp


@addmatcher(r'^exec\s+(?P<arg>[\s\S]*)$')
@addmatcher(r'^exec\s+`(?P<arg>[\s\S]*)`$')
@addmatcher(r'^exec\s+```(?P<arg>[\s\S]*)```$')
@newcommand
async def botexec(content,message):
	loc=locals()
	try:
		exec(content['arg'], globals(), loc)
	except Exception as e:
		return utils.exceptions.excpetiontostring(e)
	loccopy = dict(loc)
	loccopy.pop('content')
	loccopy.pop('message')
	return loccopy

@addmatcher(r'^aexec\s+(?P<arg>[\s\S]*)$')
@addmatcher(r'^aexec\s+`(?P<arg>[\s\S]*)`$')
@addmatcher(r'^aexec\s+```(?P<arg>[\s\S]*)```$')
@newcommand
async def botaexec(content,message):
	loc=locals()
	try:
		rst=await aexec(content['arg'],message)
	except Exception as e:
		return e
	return rst


