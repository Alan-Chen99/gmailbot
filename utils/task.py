import asyncio

class syncensure():
	def __init__(self):
		self.lock=0
	def __enter__(self):
		if sync_exempt.lock>0:
			raise RuntimeError('trying to ensure sync in an exempted block')
		self.lock=self.lock+1
	def __exit__(self,exc_type, exc_value, exc_traceback):
		self.lock=self.lock-1

class syncexempt():
	def __init__(self):
		self.lock=0
	def __enter__(self):
		self.lock=self.lock+1
	def __exit__(self,exc_type, exc_value, exc_traceback):
		self.lock=self.lock-1

sync_ensure=syncensure()
sync_exempt=syncexempt()

def addtask(coru):
	global sync_ensure,sync_exempt
	tmp=asyncio.get_event_loop()
	if sync_ensure.lock>0 and sync_exempt.lock==0:
		raise RuntimeError('trying to schedual async operations in sync_ensure')
	return tmp.create_task(coru)

def runforever():
	tmp=asyncio.get_event_loop()
	tmp.run_forever()