import weakref


class node:
	def __init__(self,path,parent):
		self.path=path
		#self.val=None
		self.parent=parent
		self.child=weakref.WeakValueDictionary()
	def __getitem__(self,key:str):
		assert(type(key) is str)#TODO: check if key contains '/'
		obj=self.child.get(key)
		if obj is None:
			obj=node(self.path+key+'/',self)
			self.child[key]=obj
		return obj
	def subtree(self):#from those that exists as node
		yield self
		for key,val in self.child.items():
			yield from val.subtree()
	def children(self):#from those that exists as node
		for key,val in self.child.items():
			yield from val.subtree()
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
		return self.path[len(self.parent.path):-1]
			
def getchildpathunsafe(curpath,key):
	return curpath+key+'/'

root=node('',None)