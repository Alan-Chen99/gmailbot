import firebase
import reseter


discordroot=firebase.init()['discordvars']

discord_default_vars={}

def adddefaultvar(var,defaultvalue):
	assert(var not in discord_default_vars)
	discord_default_vars[var]=defaultvalue

@reseter.onfullreset
async def resetdiscordvars():
	discordroot['default']<<discord_default_vars

async def resetdiscordvarsdefault():
	discordroot['default']<<discord_default_vars



alldiscordvarlevels=[]

def newvarlevel(level):
	def newvarlevelinner(func):
		alldiscordvarlevels.append((level,func))
		return func
	return newvarlevelinner

async def getdiscordvar(message,var):
	for x in alldiscordvarlevels:
		tmp = str(await (x[1])(message))
		rst=await discordroot[tmp][var]()
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
			if tmp!=None: #why was this here?#bc None == message does not actually have that level
				discordroot[tmp][var]<<val
				return None
	assert(False)