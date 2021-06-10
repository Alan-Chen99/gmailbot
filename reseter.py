


import firebase

resetfunclist=[]


def onfullreset(func):
	resetfunclist.append(func)
	return func

async def fullreset():
	firebase.init()<<None
	for reseter in resetfunclist:
		await reseter()

#async def softresetdb():
#	global alldict
#	for reseter in resetfunclist:
#		await reseter()
