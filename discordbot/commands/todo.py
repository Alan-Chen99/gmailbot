
@makematcher('sendastest','arg')#TODO
@newcommand
async def botsendastest(content,message):
	tmp=content['arg']
	await discordbot.sendastest(message,message.author,tmp)



@makematcher('commands')#TODO
@newcommand
async def botcommands(content,message):
	ans=''
	for command in discordbot.alldiscordcommands:
		havereq=True
		for req in command[2]:
			if (await req(message))!=True:
				havereq=False
				break
		if havereq:
			for x in command[1]:
				ans=ans+x[0]+'\n'
	return ans





@makematcher('setlogging','prefix',['type'])#TODO
@requirevar('admin')
@newcommand
async def botsetlogging(content,message):
	loggers=await discordbot.getdiscordvar(None,'logging')
	loggingtype=content['type']
	#print(repr(loggers))
	if loggingtype not in loggers:
		loggers[loggingtype]={}
	loggers[loggingtype]['channel']=message.channel.id
	loggers[loggingtype]['prefix']=content['prefix']
	await discordbot.setdiscordvar(None,'default','logging',loggers)
	return 'success!'

class testexception(Exception):
	pass

@makematcher('testexception')#TODO
@requirevar('admin')
@newcommand
async def bottestexception(content,message):
	raise testexception('testexception content')

'''
@makematcher('setloggingchannel')
@requirevar('admin')
@newcommand
async def botsetloggingchannel(content,message):
	await discordbot.setdiscordvar(message,'default','loggingchannel',message.channel.id)
	return 'success!'

@makematcher('setloggingprefix','arg')
@requirevar('admin')
@newcommand
async def botsetloggingprefix(content,message):
	await discordbot.setdiscordvar(message,'default','loggingprefix',content['arg'])
	return 'success!'
'''
