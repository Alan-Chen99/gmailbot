#from __future__ import annotations
from . import cache
from .tree import root as rootraw
from .tree import node

from .basedb import nestedtype
from .basedb import Valtype
from typing import Union

from utils import crypto


datatype=None

def encode_obj(obj:datatype)->nestedtype:
	if isinstance(obj,dict):
		return {crypto.tocode(x):encode_obj(y) for x,y in obj.items()}
	elif isinstance(obj,list):
		tmp={crypto.tocode(str(x)):encode_obj(y) for x,y in enumerate(obj)}
		tmp['_meta']='list'
		return tmp
	else:
		return obj

def decode_obj(obj:nestedtype)->datatype:
	if isinstance(obj,dict):
		if '_meta' in obj and obj['_meta']=='list':
			listsize=0
			islist=True
			for x,y in obj.items():
				if x!='_meta' and y is not None:
					tmp=crypto.fromcode(x)
					try:
						tmp_int=int(tmp)
						if tmp_int<0:
							islist=False
						else:
							if tmp_int>listsize:
								listsize=tmp_int
					except ValueError:
						islist=False
			if islist:
				ans:list[datatype]=[None]*(listsize+1)
				for x,y in obj.items():
					if x!='_meta' and y is not None:
						ans[int(crypto.fromcode(x))]=decode_obj(y)
				return ans
			else:
				pass #TODO?: should i do obj['_meta']<<None here?
		ans_dict={crypto.fromcode(x):decode_obj(y) for x,y in obj.items() if x!='_meta' and y is not None}
		if ans_dict:
			return ans_dict
		else:
			return None
	else:
		return obj


class asyncnode:
	def __init__(self,obj:node):
		self.obj=obj
	def __getitem__(self,key:str):
		key=crypto.tocode(key)
		return asyncnode(self.obj[key])
	def __lshift__(self,val:datatype):
		tmp=cache.modifyval_dict(self.obj,encode_obj(val))
		return syncnode(self.obj,tmp)
	async def create_syncnode(self):
		return syncnode(self.obj,await cache.sync_access(self.obj))
	def __await__(self):
		return self.create_syncnode().__await__()
	async def __call__(self):
		return (await self.create_syncnode())()

class syncnode:
	def __init__(self,obj:node,access:cache.sync_accesser):
		self.obj=obj
		self.access=access
	def __getitem__(self,key:str):
		key=crypto.tocode(key)
		tmp=self.obj[key]
		return syncnode(tmp,cache.sync_accesser.createsyncforce(tmp))
	def __lshift__(self,val:datatype):
		cache.modifyval_dict(self.obj,encode_obj(val))
		return self
	def __call__(self):
		return decode_obj(self.access())

root=None

def init():
	global root
	if root is not None:
		return root
	cache.init()
	root=asyncnode(rootraw)
	return root