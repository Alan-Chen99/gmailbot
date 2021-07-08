#from __future__ import annotations
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

from utils import crypto

import firebase_admin
from firebase_admin import db

from typing import Union


#Valtype=Union[str,int,float,bool,None]

Valtype=None
nestedtype=None
#nestedtype = Union[dict[str,'nestedtype'],Valtype]


def init():
	global root,read_executor,write_executor
	cred=firebase_admin.credentials.Certificate(json.loads(
		crypto.getenv('GOOGLE_APPLICATION_CREDENTIALS')
	))
	firebase_admin.initialize_app(cred,
		options=json.loads(crypto.getenv('FIREBASE_CONFIG'))
	)

	root =db.reference('athena_db')

	read_executor=ThreadPoolExecutor(max_workers=5)#do i need to call .shutdown?
	write_executor=ThreadPoolExecutor(max_workers=1)


def basegetsync(path:str)->nestedtype:
	if path=='':
		return root.get()
	else:
		return root.child(path).get()


async def baseget(path:str):
	loop = asyncio.get_event_loop()
	return await loop.run_in_executor(read_executor,basegetsync,path)
	

#async def baseset(path,val):
#	return root.child(path).set(val)

#async def basehave(path):
#	return await baseget(path) is not None

def baseupdatesync(dictobj):
	if '' in dictobj:
		assert(len(dictobj)==1)
		tmp=dictobj['']
		if tmp is None:
			root.delete()
		else:
			root.set(tmp)
	else:
		root.update(dictobj)

async def baseupdate(dictobj):
	loop = asyncio.get_event_loop()
	return await loop.run_in_executor(write_executor,baseupdatesync,dictobj)


