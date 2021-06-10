import firebase
import reseter


discordroot=firebase.init()['discordvars']

discord_default_vars={}

def adddefaultvar(var,defaultvalue):
	assert(var not in discord_default_vars)
	discord_default_vars[var]=defaultvalue

@reseter.onfullreset
async def resetdiscordvars():
	for x,y in discord_default_vars.items():
		discordroot[x]<<{'default':y}

async def resetdiscordvarsdefault():
	for x in discord_default_vars:
		discordroot[x[0]]['default']<<x[1]



alldiscordvarlevels=[]

def newvarlevel(level):
	def newvarlevelinner(func):
		alldiscordvarlevels.append((level,func))
		return func
	return newvarlevelinner

async def getdiscordvar(message,var):
	curlist=discordroot[var]
	for x in alldiscordvarlevels:
		tmp = str(await (x[1])(message))
		rst=await curlist[tmp]()
		if rst is not None:
			return rst
	return None

async def havelevel(level):
	for x in alldiscordvarlevels:
		if x[0]==level:
			return True
	return False

async def setdiscordvar(message,level,var,val):
	for x in alldiscordvarlevels:
		if x[0]==level:
			tmp = str(await (x[1])(message))
			if tmp!=None: #why was this here?
				discordroot[var][tmp]<<val
				return None
	assert(False)