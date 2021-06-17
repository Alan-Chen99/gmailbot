import asyncio

import time
import collections
import logging

from utils.task import addtask
from utils.task import sync_ensure


from . import basedb

from .tree import node
from .tree import getchildpathunsafe

#TODO: it is possible that the program is restarted after a change operation, then the change operation occur after the first read after restart

#TODO: check for global on everything!

#TODO: copy when needed

#TODO: better priority system

#DONE: handle modifies when loading


cacheclean_threshold=1000



def init():
	global nodeholder,loading,cache,pending,writing,inuse,cachequeue
	
	basedb.init()
	nodeholder={}

	loading={} #{key: (task,event)}, mark as once in use
	cache={} #newest if possible, else None; stores (time, the object)
	#object should be a set of keys or a string (for a leaf)

	inuse={} #{key: num marked as inuse}
	
	#{key: value if read, else func if loading}, mark as once in use if pending, and once if writing 
	pending={}#new changes
	writing={}#changes that are currently being pushed to basedb

	cachequeue=collections.deque()#only case to push to this should be unmark_inuse

	'''
	*either in cache or loading 

	#TODO: this list is old, might be different
	1) none of everything

	2) task in loading, func in pending and/or writing
	#val=pending(writing(loadrst))

	3) func in writing, value in pending, value in cache, task in loading

	4) value in pending and/or writing, task in/not loading

	5) value in cache

	'''

	addtask(pushchangesloop())

	#root=parsefingerprint(meta['root'])
	#return root['database']


#for debugging
###########################################

import json
async def printdebug():
	tmp={}
	for x,y in cache.items():
		tmp['/'+x+f' [cache {inuse.get(x,0)}]']=y[1]
	for x,y in pending.items():
		if callable(y):
			tmp['/'+x+f' [pending func {inuse.get(x,0)}]']=y(await basedb.baseget(x))
		else:
			tmp['/'+x+f' [pending val {inuse.get(x,0)}]']=y
	for x,y in writing.items():
		if callable(y):
			tmp['/'+x+f' [writing func {inuse.get(x,0)}]']=y(await basedb.baseget(x))
		else:
			tmp['/'+x+f' [writing val {inuse.get(x,0)}]']=y
	for x in loading:
		tmp['/'+x+f' [loading {inuse.get(x,0)}]']=None
	for x in tmp:
		if type(tmp[x]) is set:
			tmp[x]=list(tmp[x])
	print(json.dumps(tmp,indent=4))

###########################################

def mark_inuse(key):
	inuse[key]=inuse.get(key,0)+1

def unmark_inuse(key):
	assert((key in inuse) and (inuse[key]>0))
	tmp=inuse[key]
	pathsettodel=None
	settodel=None
	if tmp==1:
		assert(key not in pending)
		assert(key not in writing)
		assert(key not in loading)
		del inuse[key]
		curtime=time.time()
		cache[key]=(curtime,cache[key][1])
		cachequeue.appendleft((curtime,key))
		if len(cachequeue)>cacheclean_threshold:
			todel=cachequeue.pop()#(prioority,key)
			if todel[1] not in inuse:
				cacheobj=cache[todel[1]]
				if cacheobj[0] is todel[0]:
					if type(cacheobj[1]) is set:
						pathsettodel=todel[1]
						settodel=cacheobj[1]
					del cache[todel[1]]
					del nodeholder[todel[1]]
		if settodel is not None:
			assert(pathsettodel is not None)
			for x in settodel:
				unmark_inuse(getchildpathunsafe(pathsettodel,x))
	else:
		inuse[key]=tmp-1

class usepath:
	def __init__(self,path):
		self.path=path
	def __enter__(self):
		mark_inuse(self.path)
	def __exit__(self,exc_type, exc_value, exc_tb):
		unmark_inuse(self.path)

#def objtostr(val):#json-like obj to string
#	if val is nokey:
#		return None
#	return json.dumps(val)

#def strtoobj(val):#string to json-like obj
#	if val==None:
#		return nokey
#	return json.loads(val)

'''
The tree is needed b/c, suppose that an node in in cache, then its parent is set, then parent is out of cache, then noway to tell if it is changed.
'''

'''
conditions need to be maintained through a sequence of sync operations

~~objects are invalidated if a parent of it is in cache?

cache has object iff object is fully available locally

pending has object or function iff ~~object has been changed since
the last start of call to pushchanges
--> a node or its parent has been changed directly. A node is allowed to be not in pending if only change to it is insertion of child.
pending can only have a function if object cannot yet be obtained
function represents changes after the last pushchanges call

writing has object or function iff it has changes in the current writing cycle
writing can only have a function if object cannot yet be obtained

loading stores (task,event).
loading task deletes itself after loaded. it should not be externally removed
(loading task persist after a val is written to pending and load is no longer needed)
event is set if object is set to during load

1 time inuse for each of key in loading, pending, writing
1 time inuse if the immediate parent of a key is in cache

if a node is pending but not in cache, then its pending status is ignored for its children since func changes are only allowed on leaves

if a node is in pending and cache, then all child of it is in pending and cache

if a node is in cache but not in pending, then all child of it is in cache (and can be in pending)

should be in nodeholder if in any other var, 
'''

def changesfromdict(curnode:node,nd):#from nested dict, returns a pair
	assert(type(curnode) is node)
	if type(nd) is not dict:
		yield (curnode,nd)
	else:
		#assert(type(nd) is dict)
		curset=set()
		for key,val in nd.items():
			assert(type(key) is str)
			curset.add(key)
			yield from changesfromdict(curnode[key],val)
		yield (curnode,curset)


def modifyval(curnode,newval):
	with sync_ensure:
		modifynode=curnode
		modifydepth=0
		depth=0
		for x in curnode.ancestors():
			depth+=1
			parentpath=x.path
			if parentpath in cache:# or (parentpath in pending):#not needed
				modifydepth=depth
				modifynode=x
				if cache[parentpath][1] is not None:
					break
				#else: if x in a hidden cached child of a cached node with value None

		depth=0
		if modifydepth>0:
			for x in curnode.ancestorswithself():
				if depth>=modifydepth-1:
					childmodify=x
					break
				if x.path in cache:
					assert(cache[x.path][1] is None)
				newval={x.key():newval}
				depth+=1
			assert(childmodify.parent is modifynode)
		else:
			childmodify=curnode

		for x in childmodify.subtree():
			childpath=x.path
			if childpath in nodeholder:
				assert(nodeholder[childpath] is x)
				with usepath(childpath):
					#TODO: is inuse handled correctly here?
					#TODO: change this so that priority does not refresh
					if (childpath in cache) and type(cache[childpath][1]) is set:
						for setchild in cache[childpath][1]:
							unmark_inuse(getchildpathunsafe(childpath,setchild))
					cache[childpath]=(None,None)
					if childpath in pending:
						del pending[childpath]
						unmark_inuse(childpath)
					if childpath in loading:
						loading[childpath][1].set()

		for childnode,childval in changesfromdict(childmodify,newval):
			childpath=childnode.path
			mark_inuse(childpath)#needs to do this for all nodes other than childmodify since direct parent changed
			nodeholder[childpath]=childnode
			if childpath in cache:
				assert(cache[childpath][1] is None)
			cache[childpath]=(None,childval)
			if childpath not in pending:
				mark_inuse(childpath)
			if type(childval) is set:
				pending[childpath]=childval.copy()
			else:
				pending[childpath]=childval
			if childpath in loading:#modifynode? can still previously in pending as a func
				loading[childpath][1].set()

		unmark_inuse(childmodify.path)#childmodify is marked once extra inuse as said above
		assert(childmodify.path in pending)
		assert(childmodify.path in inuse)#since in pending

		if modifydepth>0:
			assert(modifynode.path!=curnode.path)
			modifynode_path=modifynode.path
			mark_inuse(childmodify.path)
			if (modifynode_path in cache) and (type(cache[modifynode_path][1]) is set):
				cache[modifynode_path][1].add(childmodify.key())
				if modifynode_path in pending:
					pending[modifynode_path].add(childmodify.key())
				#else:
				#	mark_inuse(modifynode_path)
				#	pending[modifynode_path]=cache[modifynode_path][1].copy()
			else:
				cache[modifynode_path]=(None,{childmodify.key()})
				if modifynode_path not in pending:
					mark_inuse(modifynode_path)
				pending[modifynode_path]={childmodify.key()}

		assert(curnode.path in pending)
		assert(curnode.path in inuse)
		return sync_accesser.createsync(curnode)



def changeafterload(curnode,loaded)->None:
	curpath=curnode.path
	mark_inuse(curpath)#marks inuse for nodes up to and including the roots of cached subtrees
	if curpath in writing:
		tmp=writing[curpath]
		if callable(tmp):
			if type(loaded) is dict:
				logging.error('cannot use a function to change a dict')
				writing[curpath]=loaded
			else:
				tmprst=tmp(loaded)
				if type(tmprst) is dict:
					logging.error('changing by function that returns a dict is not implemented')
				else:
					loaded=tmprst
				writing[curpath]=loaded
		else: #if obj is assigned and then written to writing after load start
			assert(curpath in cache)
	
	if curpath in pending:
		tmp=pending[curpath]
		if callable(tmp):
			if type(loaded) is dict:
				logging.error('cannot use a function to change a dict')
			else:
				tmprst=tmp(loaded)
				if type(tmprst) is dict:
					logging.error('changing by function that returns a dict is not implemented')#for consistency since it not implemented in writing
				else:
					loaded=tmprst
			loaded=tmp(loaded)
		else:
			assert(curpath in cache)
			loaded=tmp
		pending[curpath]=loaded
	
	if curpath in cache:
		return None
	else:
		nodeholder[curpath]=curnode
		#curpath marked inuse at the start of this function as it is a child of a cached obj
		if type(loaded) is dict:
			keyset=set()
			for x in loaded:
				keyset.add(x)
			cache[curpath]=(None,keyset)
			for x,y in loaded.items():
				changeafterload(curnode[x],y)
		else:
			cache[curpath]=(None,loaded)


def startload(curnode):
	curpath=curnode.path
	if curpath in cache:
		if curpath not in writing:
			return None #pending==cache so have full access already
		elif not callable(writing[curpath]):
			return None

	#assert(not (key in cache)) #not neccessarily as could be in writing as a func and need to read before updating

	if curpath in writing:
		tmp=writing[curpath]
		assert(callable(tmp))
	elif curpath in pending:
		#if not in writing, then must be a func
		tmp=pending[curpath]
		assert(callable(tmp))

	
	async def loadvar(curnode):
		assert(type(curnode) is node)
		curpath=curnode.path
		assert(curpath in loading)
		assert(curpath in inuse)
		rst=await basedb.baseget(curpath)

		changeafterload(curnode,rst)
		unmark_inuse(curpath)#since inuse b/c loading
		unmark_inuse(curpath)#marked once extra inuse in changeafterload

		loading[curpath][1].set()#if not this, the throw warning on garbage collection for "Task was destroyed but it is pending!"
		del loading[curpath]
		return None

	if curpath in loading:
		return None
	else:
		mark_inuse(curpath)#will unmark in the end of loadvar
		loading[curpath]=(addtask(loadvar(curnode)),asyncio.Event())
		#assert(curpath in loading)


async def wait_until_loaded(curnode):#must always be run with inuse
	assert(type(curnode) is node)
	curpath=curnode.path
	assert(curpath in inuse)
	startload(curnode)
	if curpath in loading:
		tmp=loading[curpath]
		wait_until_set=addtask(tmp[1].wait())
		await asyncio.wait({tmp[0],wait_until_set},return_when=asyncio.FIRST_COMPLETED)
		if tmp[0].done():
			await tmp[0]
		#DONE?: haddle exception in tmp[0] accordingly by awaiting
	if curpath not in cache:
		logging.error('object still not in cache after it should have been')
		#print(loading)
		#print(cache)
	assert(curpath in cache)
	assert(curpath in inuse)

def loadfromcache(curnode):
	curpath=curnode.path
	assert(curpath in cache)
	assert(curpath in inuse)
	if type(cache[curpath][1]) is set:
		ans={}
		for x in cache[curpath][1]:
			assert(type(x) is str)
			ans[x]=loadfromcache(curnode[x])
		return ans
	else:
		return cache[curpath][1]

class sync_accesser():#use this to read
	def __init__(self,curnode):
		self.curnode=curnode

	async def create(curnode):
		assert(type(curnode) is node)
		#print(f'sync_access for {key} created')
		curpath=curnode.path
		mark_inuse(curpath)
		await wait_until_loaded(curnode)
		assert((curpath in inuse) and (curpath in cache))
		return sync_accesser(curnode)

	def createsync(curnode):
		assert(type(curnode) is node)
		curpath=curnode.path
		mark_inuse(curpath)
		assert((curpath in inuse) and (curpath in cache))
		return sync_accesser(curnode)

	def createsyncforce(curnode):
		assert(type(curnode) is node)
		curpath=curnode.path
		mark_inuse(curpath)
		if curpath not in cache:
			cache[curpath]=(None,None)
		assert((curpath in inuse) and (curpath in cache))
		return sync_accesser(curnode)

	def __call__(self):
		return loadfromcache(self.curnode)

	def __del__(self):
		#print(f'sync_access for {self.key} destroyed')
		curpath=self.curnode.path
		assert((curpath in inuse) and (curpath in cache))
		unmark_inuse(curpath)

async def sync_access(curnode):
	assert(type(curnode) is node)
	return await sync_accesser.create(curnode)

#def random_sync_access():
#	return sync_accesser.create_random()


'''
#func should not return an external refrence!
def modifyfunc(key,func):
	global cache, pending

	assert(callable(func))
	if key in cache:
		newval=func(cache[key][1])
		cache[key]=(time.time(),newval)#awlays inuse
		if key not in pending:
			mark_inuse(key)
		pending[key]=newval
	else:
		if key in pending:
			curfunc=pending[key]
			def newfunc(val):
				return func(curfunc(val))	
			pending[key]=newfunc
		else:
			pending[key]=func
			mark_inuse(key)
		#startload(key)#can both have or not have
'''


#default: get from list
#writing to list: have len already

#1) chnage to write to list with length
#2) push all changes to list
#3) change statee to get from list
#4) push changes and delete from change list

def getfromwriting(path,known,final):
	if path in known:
		return known[path]
	val=writing[path]
	if type(val) is set:
		ans={}
		for key in val:
			childpath=getchildpathunsafe(path,key)
			ans[key]=getfromwriting(childpath,known,final)
			del final[childpath]
		known[path]=ans
		final[path]=ans
		return ans
	else:
		known[path]=val
		final[path]=val
		return val

async def pushchanges():
	global writing,pending
	#print('new push changes cycle')
	
	if writing:#another push changes is in progress
		return None#change return?

	if not pending:
		return None#no changes to push

	with sync_ensure:
		writing=pending
		pending={}

	for x in writing:
		assert(x in inuse)
		if callable(writing[x]):
			assert(x in loading)
			await loading[x][0]
	for x,y in writing.items():
		assert(not callable(y))

	known={}
	final={}
	for x in writing:
		getfromwriting(x,known,final)
	#print('updating, final is:')
	#print(final)
	await basedb.baseupdate(final)

	tmp_todel=writing
	writing={}
	#await printdebug()
	for x in tmp_todel:
		unmark_inuse(x)



async def pushchangesloop():
	while True:
		await pushchanges()
		if not pending:
			await asyncio.sleep(0.1)#change?




