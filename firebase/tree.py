from __future__ import annotations

import weakref
from typing import Tuple, Union
from typing import Generator


from typing import NewType
Path = NewType('Path', str)

class node:
	def __init__(self,path:str,parent:Union[node,None]):
		self.path:Path=Path(path)
		self.parent:Union[node,None]=parent
		self.child:weakref.WeakValueDictionary[str,node]=weakref.WeakValueDictionary()
	def __getitem__(self,key:str):
		assert(type(key) is str)#TODO: check if key contains '/'
		obj=self.child.get(key)
		if obj is None:
			obj=node(self.path+key+'/',self)
			self.child[key]=obj
		return obj
	def subtree(self) -> Generator[node, None, None]:#from those that exists as node
		yield self
		for _,val in self.child.items():
			yield from val.subtree()
	def children(self):#from those that exists as node
		for _,val in self.child.items():
			yield from val.subtree()
	def subtree_and_childset(self) -> Generator[Tuple[node,set[Path]], None, None]:
		childset:set[Path]=set()
		for child in self.child.values():
			yield from child.subtree_and_childset()
			childset.add(child.path)
		yield (self,childset)


	def ancestors(self):#from closest
		x=self.parent
		while x is not None:
			yield x
			x=x.parent
	def ancestorswithself(self):#from closest
		x=self
		while x is not None:
			yield x
			x=x.parent
	def key(self):
		tmp=self.parent
		assert(tmp is not None)
		return self.path[len(tmp.path):-1]
			
def getchildpathunsafe(curpath:Path,key:str)->Path:
	return Path(curpath+key+'/')

root=node('',None)