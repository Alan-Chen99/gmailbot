from replit.database import AsyncDatabase
from replit import db 
import asyncio

repldb=AsyncDatabase(db.db_url)

loop =asyncio.get_event_loop()
alldict = loop.run_until_complete(repldb.to_dict())

async def getwebdb():
	tmp=await repldb.to_dict()
	return tmp

async def getlocaldb():
	global alldict
	return alldict

import logging
import asyncio
class setvarerror(Exception):
	pass
async def setvar(key,val):
	global alldict
	retrynum=0
	while True:
		retrynum=retrynum+1
		try:
			if val==None:
				await repldb.delete(key)
			else:
				alldict[key]=val
				await repldb.set(key,val)
			return None
		except Exception as e:
			try:
				raise setvarerror(f'failed to set {repr(key)} to {repr(val)} in the repl database') from e
			except Exception as e2:
				if retrynum<5:
					logging.exception(e2)
					await asyncio.sleep(1)
				else:
					raise e2



async def getvar(var):
	global alldict
	if var in alldict:
		return alldict[var]
	else:
		await repldb.set(var,None)
		return None
	#return await repldb.get(var)
	

async def havevar(var):
	return var in alldict

resetfunclist=[]

def onreset(func):
	resetfunclist.append(func)
	return func

async def resetdb():
	global alldict
	keys=await repldb.keys()
	for x in keys:
		await repldb.delete(x)
	alldict={}
	for reseter in resetfunclist:
		await reseter()

#async def softresetdb():
#	global alldict
#	for reseter in resetfunclist:
#		await reseter()