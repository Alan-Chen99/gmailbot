#TODO: in database requests errors not sent (perhaps b/c it calls logging.error which uses async?)


#TODO:
#https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests


#set up logging first
import logging
import utils.timing
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s [%(levelname)s] %(message)s",
)
logging.Formatter.converter = utils.timing.loggingtimenow
#?^
import sys
#TODO: change discord bot token
import utils.task
#import discordbot.bot.set_message_handler
import discordbot.bot
from discordbot.commands.manage import addcommand as insertdiscoredcommand

import discordbot.commands.simple
insertdiscoredcommand(discordbot.commands.simple.commands)

#import discordbot.commands.types
#insertdiscoredcommand(discordbot.commands.types.commands)

import discordbot.commands.admin
insertdiscoredcommand(discordbot.commands.admin.commands)

#import discordbot.commands.execs
#insertdiscoredcommand(discordbot.commands.execs.commands)

#import discordbot.commands.gmail
#insertdiscoredcommand(discordbot.commands.gmail.commands)


import loggingsetup
loggingsetup.setup()

#import webserver
#utils.task.addtask(discordbot.bot.send('error','hello before init'))

utils.task.addtask(discordbot.bot.runbot())
#utils.task.addtask(webserver.start())

#import gmail.bot
#utils.task.addtask(gmail.bot.initgmail())

print('starting all the tasks')
utils.task.runforever()
sys.exit()


from webserver import routes
from webserver import app
from aiohttp import web




import os


#import uvloop # speed
import utils

import discordbot
import gmail


import discordlevels
import discorddefaultvars
import discordcommands



import asyncio

import logging





async def sendservererror(log_entry):
	#print(log_entry)
	file=await discordbot.filefromstring(log_entry,'exception.txt')
	await discordbot.sendloggingmessage('error','**Server Error**',file=file)


class discordhandler(logging.Handler):
	def emit(self, record):
		log_entry = self.format(record)
		try:
			#raise Exception('testexcpetion')
			if discordbot.haveinitialized:
				discordbot.client.loop.create_task(sendservererror(log_entry))
			else:
				print(log_entry)
		except Exception as e:
			print(e)
			print('due to the above exception, the following excpetion cannot be logged:')
			print(log_entry)

'''
class discordhandler(logging.StreamHandler):
	def emit(self, record):
		try:
			msg = self.format(record)
			stream = self.stream
			stream.write(msg)
			self.flush()
		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			self.handleError(record)
'''
dh = discordhandler()
dh.setLevel(logging.WARNING)
#TODO: also log to stdout

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s [%(levelname)s] %(message)s",
	handlers=[dh]
)
logging.Formatter.converter = utils.loggingtimenow





# show access logs in console (remove this to not show logs)



@routes.get("/")
async def index(request):
  return web.Response(text="hellohello")

'''
@routes.post('/gen_key')
async def gen_key(req):
	data = await req.post()
	# you can also store a separate password in .env just for generating keys
	if data.get('secret') == os.environ["KEY_SECRET"]:
		print("Generating a new API key...")
		key = await utils.gen_key()
		return web.Response(text=key)
	else:
		# use the status kwarg for a custom status
		return web.Response(text="401 Unauthroized", status=401)
'''

# an example api route

# Add the following line between the @routes and the async def
#  to check for an API key before running your code
# this will handle the check for you

# Additionally you can add the following line to ratelimit calls to this endpoint
#  limit is global (affects all users the same) as repl.it does not expose IPs
# This example sets a max of 1 request a second. 
#  To ratelimit by minute set period to 60, or whatever value you want
#@utils.ratelimit(1, period=1)
@routes.post("/logger/api")
@utils.adminauth
async def discordlogger(req):
	data=await req.post()
	#mssg=data.get('message')
	#mssg=repr(data)
	await discordbot.sendloggingmessage('error',
		data.get('type'),file=await discordbot.filefromstring(data.get('message'),'logging.txt'))

	'''#using library http logger
	tb=data.get("exc_text")
	if tb=="None":
		tb=''
	else:
		tb='\n'+tb

	mssg=f'```{data.get("asctime")} [{data.get("levelname")}]\n{data.get("message")}{tb}```'
	#'\n\n \u200b'
	#print(mssg)
	await discordbot.sendloggingmessage(mssg)
	return web.Response(text="success")
	'''

	'''
	print("Calling backend.get_current_weekday()")
	weekday_name = await backend.current_weekday()
	# Most APIs return JSON because it is easy to read and parse
	# to do this return web.json_resonse(data)
	return web.json_response({
		'error': None,
		'weekday': weekday_name
	})
	'''










async def startserver():
	#TODO: delete those
	firebaseroot=firebase.init()
	firebaseroot<<None


	runner = web.AppRunner(app)
	await runner.setup()
	site = web.TCPSite(runner, '0.0.0.0', 8080)
	await site.start()
	while True:
		await asyncio.sleep(3600)

#asyncio.run(startserver())



#web.run_app(app)


#utils.resetdb()


	
	#if message.content.startswith('alanbot.ping'):
	#	await message.channel.send('pong')
	#if message.content.startswith('alanbot.setchannel'):
	#	db['loggingchannels'].append(message.channel.id)
	#	await message.channel.send('success!')


#client.loop.create_task(sender())
app.add_routes(routes)
uvloop.install()



discordbot.client.loop.create_task(startserver())
print('starting bots')

discordbot.client.run(os.getenv('discordtoken'))




#web.run_app(app)

'''
if __name__ == "__main__":	
	uvloop.install()
	web.run_app(app)
'''
