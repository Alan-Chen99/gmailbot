from . import cache
from .tree import root as rootraw
from .tree import node


class asyncnode:
	def __init__(self,obj:node):
		assert(type(obj) is node)
		self.obj=obj
	def __getitem__(self,key):
		return asyncnode(self.obj[key])
	def __lshift__(self,val):
		tmp=cache.modifyval(self.obj,val)
		return syncnode(self.obj,tmp)
	async def create_syncnode(self):
		return syncnode(self.obj,await cache.sync_access(self.obj))

	def __await__(self):
		return self.create_syncnode().__await__()


class syncnode:
	def __init__(self,obj:node,access:cache.sync_accesser):
		assert(type(obj) is node)
		assert(type(access) is cache.sync_accesser)
		self.obj=obj
		self.access=access
	def __getitem__(self,key):
		tmp=self.obj[key]
		return syncnode(tmp,cache.sync_accesser.createsyncforce(tmp))
	def __lshift__(self,val):
		cache.modifyval(self.obj,val)
		return self
	def __call__(self):
		return self.access()

root=None

def init():
	global root
	if root is not None:
		return root
	cache.init()
	root=asyncnode(rootraw)
	return root