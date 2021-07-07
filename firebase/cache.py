#from __future__ import annotations
import asyncio


from utils.task import addtask


from . import basedb

from .tree import node

from .basedb import nestedtype
from copy import deepcopy
#Valtype=Union[str,int,float,bool,None]
#TypeVar('Valtype')#str,int,float,bool,None


#fulldatatype = Union[dict[Path,'fulldatatype'],Valtype]
fulldata:nestedtype
write:nestedtype


#datatype = Union[dict[Path,'datatype'],Valtype]
#modifytype=dict[Path,tuple[node,Union[set[Path],Valtype]]]

#TODO: it is possible that the program is restarted after a change operation, then the change operation occur after the first read after restart

#TODO: check for global on everything!

#TODO: copy when needed



def init():
	global fulldata
	
	basedb.init()	
	fulldata=basedb.basegetsync('')
	addtask(pushchangesloop())
	


def datachanger_root(change:nestedtype):
	global fulldata
	fulldata=change

def datachanger_child(dictobj,key:str):
	obj_copy=dictobj
	def internal(change:nestedtype):
		obj_copy[key]=change
	return internal

def modifyval_dict(curnode:node,change:nestedtype):

	datachanger=datachanger_root
	
	data:nestedtype=fulldata
	pathlist:list[str]=[]

	for x in curnode.ancestorswithself():
		if x.parent is not None:
			pathlist.append(x.key())

	for x in reversed(pathlist):
		if not isinstance(data,dict):
			data={x:None}
			datachanger(data)
		assert(isinstance(data,dict))
		datachanger=datachanger_child(data,x)
		if x not in data:
			data[x]=None
		data=data[x]
		
	datachanger(change)
	return sync_accesser.createsync(curnode)


#def startload(curnode:node):
#	pass


#async def wait_until_loaded(curnode:node):
#	pass


def loadfromcache(curnode:node)->nestedtype:
	pathlist:list[str]=[]
	data:nestedtype=fulldata

	for x in curnode.ancestorswithself():
		if x.parent is not None:
			pathlist.append(x.key())

	for x in reversed(pathlist):
		if isinstance(data,dict):
			if x in data:
				data=data[x]
			else:
				return None
		else:
			return None
	return data

class sync_accesser():#use this to read
	def __init__(self,curnode:node):
		self.curnode=curnode

	@classmethod
	async def create(cls,curnode:node):
		return sync_accesser(curnode)

	@classmethod
	def createsync(cls,curnode:node):
		return sync_accesser(curnode)

	@classmethod
	def createsyncforce(cls,curnode:node):
		return sync_accesser(curnode)

	def __call__(self):
		return loadfromcache(self.curnode)

	def __del__(self):
		pass

async def sync_access(curnode:node):
	return await sync_accesser.create(curnode)



async def pushchanges():
	global write,fulldata
	#print('new push changes cycle')
	
	write=deepcopy(fulldata)
	
	await basedb.baseupdate({'':write})



async def pushchangesloop():
	while True:
		await pushchanges()
		await asyncio.sleep(1)




