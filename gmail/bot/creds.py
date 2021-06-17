from webserver import routes
from aiohttp.web import Response
import os
import aiogoogle

import json
import asyncio

from .vars import gmailvars

import utils.task
#import reseter


#according to this, must click 'publish' or else refresh token only lives for 7 days.
#https://stackoverflow.com/questions/8953983/do-google-refresh-tokens-expire


client_creds=json.loads(os.getenv('gmail_client_secret'))['web']

client_creds['scopes']=['https://www.googleapis.com/auth/gmail.readonly']
client_creds['redirect_uri']='https://xinyangchen.repl.co/googleredirect'

#print(client_creds)

aiog = aiogoogle.Aiogoogle(client_creds=client_creds)

state=aiogoogle.auth.utils.create_secret()

uri = aiog.oauth2.authorization_url(
		client_creds=client_creds,
		state=state,
		access_type="offline",
		include_granted_scopes=True,#example has this as true
		#login_hint=EMAIL,
		prompt="consent",
	)

#@reseter.onfullreset
#async def resetgmail():
#	pass#not needed since everything defaults to None now
	
'''
async def gethistoryid():
	global aioggl,gmail
	tmp=await gmailvars['gmail_historyid']()
	if tmp==None:
		await getgmail()
		lastlist = await aioggl.as_user(
				gmail.users.messages.list(
					userId='me',includeSpamTrash=True,maxResults=1
				)
			)
		lastid=lastlist['messages'][0]['id']

		lastmssg=await aioggl.as_user(
			gmail.users.messages.get(
				userId='me',id=lastid
			)
		)
		tmp=lastmssg['historyId']
		gmailvars['gmail_historyid']<<tmp
	return tmp
'''

gmail_ready_event=asyncio.Event()


@routes.get("/googleredirect")
async def testhandle(req):
	if req.query.get("error"):
		error = {
			"error": req.query.get("error"),
			"error_description": req.query.get("error_description"),
		}
		return Response(text=json.dumps(error))
	elif req.query.get("code"):
		returned_state = req.query["state"]
		# Check state
		if returned_state != state:
			return Response(text='state mismatch')
		# Step D & E (D send grant code, E receive token info)
		full_user_creds = await aiog.oauth2.build_user_creds(
			grant=req.query.get("code"), client_creds=client_creds
		)
		gmailvars['gmail_cred']<<full_user_creds
		gmail_ready_event.set()
		return Response(text=json.dumps(full_user_creds))
	else:
		# Should either receive a code or an error
		return Response(text="Something's probably wrong with your callback")


gmail=None
aioggl=None


async def waitforcred():
	global aioggl,gmail
	assert(aioggl is None)
	assert(gmail is None)
	gmail_cred_var=await gmailvars['gmail_cred']
	gmail_cred=gmail_cred_var()
	if gmail_cred is not None:
		aioggl=aiogoogle.Aiogoogle(
			client_creds=client_creds,
			user_creds=gmail_cred
		)
		gmail=await aioggl.discover('gmail', 'v1')
	else:
		await gmail_ready_event.wait()
		gmail_cred=gmail_cred_var()
		assert(gmail_cred is not None)
		aioggl=aiogoogle.Aiogoogle(
			client_creds=client_creds,
			user_creds=gmail_cred
		)
		gmail=await aioggl.discover('gmail', 'v1')
	

getcredtask=utils.task.addtask(waitforcred())

async def waitforaioggl():
	await getcredtask
	return aioggl

async def waitforgmail():
	await getcredtask
	return gmail

getaioggl=utils.task.addtask(waitforaioggl())
getgmail=utils.task.addtask(waitforgmail())