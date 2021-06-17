import logging
import discordbot.bot
import utils.task

async def sendservererror(log_entry):
	#print(log_entry)
	try:
		file=await discordbot.bot.filefromstring(log_entry,'exception.txt')
		await discordbot.bot.send('error','**Server Error**',file=file)
	except Exception as e:
		print(e)
		print('due to the above exception, the following excpetion cannot be logged:')
		print(log_entry)

class discordhandler(logging.Handler):
	def emit(self, record):
		#print('an error occcured')
		log_entry = self.format(record)
		try:
			#raise Exception('testexcpetion')
			#if discordbot.bot.haveinitialized():
			utils.task.addtask(sendservererror(log_entry))
			if not discordbot.bot.haveinitialized():
				print(log_entry)
		except Exception as e:
			print(e)
			print('due to the above exception, the following excpetion cannot be logged:')
			print(log_entry)

havesetup=False
def setup():
	global havesetup
	if havesetup==False:
		havesetup=True
		dh = discordhandler()
		dh.setLevel(logging.WARNING)
		logging.getLogger().addHandler(dh)