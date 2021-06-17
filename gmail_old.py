from webserver import routes
from aiohttp.web import Response
import os
import aiogoogle
#from aiogoogle import Aiogoogle
#from aiogoogle.auth.utils import create_secret
import json
import time
import discordbot

import re
import logging

import asyncio
import aiohttp
# Use the client_secret.json file to identify the application requesting
# authorization. The client ID (from that file) and access scopes are required.

#print('tmp1')


#according to this, must click 'publish' or else refresh token only lives for 7 days.
#https://stackoverflow.com/questions/8953983/do-google-refresh-tokens-expire


client_creds=json.loads(os.getenv('gmail_client_secret'))['web']

client_creds['scopes']=['https://www.googleapis.com/auth/gmail.readonly']
client_creds['redirect_uri']='https://xinyangchen.repl.co/test'

#print(client_creds)

aoig = aiogoogle.Aiogoogle(client_creds=client_creds)

state=aiogoogle.auth.utils.create_secret()

uri = aoig.oauth2.authorization_url(
		client_creds=client_creds,
		state=state,
		access_type="offline",
		include_granted_scopes=True,#example has this as true
		#login_hint=EMAIL,
		prompt="consent",
	)
#print(uri)

import database


@database.onreset
async def resetgmail():
	await database.setvar('email_to_info',{})
	await database.setvar('email_from_info',{})
	#not needed anymore since get defaults to None now
	#await database.setvar('gmail_cred',None)
	#await database.setvar('gmail_historyid',None)
	

async def gethistoryid():
	global aioggl,gmail
	tmp=await database.getvar('gmail_historyid')
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
		await database.setvar('gmail_historyid',tmp)
	return tmp


@routes.get("/test")
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
		full_user_creds = await aoig.oauth2.build_user_creds(
			grant=req.query.get("code"), client_creds=client_creds
		)
		await database.setvar('gmail_cred',full_user_creds)
		return Response(text=json.dumps(full_user_creds))
	else:
		# Should either receive a code or an error
		return Response(text="Something's probably wrong with your callback")


gmail=None

async def getgmail():
	global aioggl,gmail
	if gmail==None:
		aioggl=aiogoogle.Aiogoogle(
			client_creds=client_creds,
			user_creds=(await database.getvar('gmail_cred'))
		)
		gmail=await aioggl.discover('gmail', 'v1')


import base64

class email:
	def __init__(self):
		self.dto=''
		self.rtpath=''
		self.source=''
		self.date=''
		self.subject=''
		self.to=''
		self.cc=''
		self.text=''
		self.gotfor=''
		self.labels=[]
	def getinfo(self):
		return (
			f'labels: {repr(self.labels)}\n'
			f'dto: {self.dto}\n'
			f'rtpath: {self.rtpath}\n'
			f'source: {self.source}\n'
			f'date: {self.date}\n'
			f'subject: {self.subject}\n'
			f'to: {self.to}\n'
			f'cc: {self.cc}\n'
			#bcc?
			f'for: {self.gotfor}\n'
		)
		
def decode64(b64s):
	return base64.urlsafe_b64decode(b64s).decode("utf-8")

async def handlepart(part,mail):
	if part['mimeType']=='multipart/alternative':
		for x in part['parts']:
			await handlepart(x,mail)
	else:
		if part['mimeType']=='text/plain':
			mail.text=mail.text+decode64(part['body']['data'])



async def handlenewemail(messagemeta):
	mssgid=messagemeta['id']
	try:
		mssg=await aioggl.as_user(  # the request is being sent here
			gmail.users.messages.get(
				userId='me',id=mssgid
			)
		)
	except aiogoogle.excs.HTTPError as e:
		#might be message deleted
		#TODO: delete following line after testing
		logging.exception(e)
		return None
	mail=email()
	mail.labels=mssg['labelIds']
	for x in mssg['payload']['headers']:
		if x['name']=='Delivered-To':
			mail.dto=x['value']
		if x['name']=='Return-Path':
			mail.rtpath=x['value']
		if x['name']=='From':
			mail.source=x['value']
		if x['name']=='Date':
			mail.date=x['value']
		if x['name']=='Subject':
			mail.subject=x['value']
		if x['name']=='To':
			mail.to=x['value']
		if x['name']=='Cc':
			mail.cc=x['value']
		if x['name']=='Received':
			rerst=re.findall(r'(?<=for <)[^\s@]+@[^\s@]+\.[^\s@]{2,}(?=>)', x['value'])
			if len(rerst)>1:
				logging.warning(f'{repr(x["value"])} contains more than 1 email')
			else:
				if len(rerst)==1:
					mail.gotfor=rerst[0]
			#not entirely sure if this works
			#get oldest send for
			#supposed to be ordered from newest to oldest

	await handlepart(mssg['payload'],mail)
	#for x in mssg['payload']['parts']:
	#	await handlepart(x,mail)

	
	#mail.toinfo=(await database.getvar('email_to_info'))[mail.gotfor]
	#mail.frominfo=(await database.getvar('email_from_info'))[mail.source]

	await discordbot.sendloggingmessage(
		'email',
		mail.getinfo(),
		file=await discordbot.filefromstring(mail.text)
	)
	
emaildiscordhandlers=[]
def newhandler(handler):
	emaildiscordhandlers.append(handler)
	return handler

class conditionnotmet(Exception):
	pass

async def pushemail(mail):
	for handler in emaildiscordhandlers:
		try:
			handler(mail)
			return None
		except conditionnotmet:
			pass

#def email_to_handletype_only(handletype):
#	def internal(handler):
#		def newhandler(mail):
#
#			if await database.getvar('email_to_info'):
#				pass


async def checkmail():
	global aioggl,gmail
	await getgmail()
	historyall = await aioggl.as_user(
		gmail.users.history.list(
			userId='me',
			startHistoryId=(await gethistoryid()),
			historyTypes='messageAdded'
		)
	)
	if 'history' in historyall:
		for history in historyall['history']:
			if 'messagesAdded' in history:
				for x in history['messagesAdded']:
					await handlenewemail(x['message'])
			await database.setvar('gmail_historyid',history['id'])
	await database.setvar('gmail_historyid',historyall['historyId'])


async def getlastfull():
	global aioggl,gmail
	await getgmail()
	lastlist = await aioggl.as_user(  # the request is being sent here
            gmail.users.messages.list(
                userId='me',includeSpamTrash=True,maxResults=1
            )
        )
	lastid=lastlist['messages'][0]['id']

	return await aioggl.as_user(  # the request is being sent here
		gmail.users.messages.get(
			userId='me',id=lastid
		)
	)

@discordbot.ondiscordready
async def initgmail():
	#print('initing gmail')
	#global aioggl,gmail
	#await getgmail()
	errorwaittime=1
	while True:
		#print('checking gmail')
		try:
			await checkmail()
			await asyncio.sleep(1)
			errorwaittime=1
		except aiohttp.client_exceptions.ClientOSError as e:
			logging.exception(e)
			asyncio.sleep(errorwaittime)
			errorwaittime=errorwaittime*2

#delete this
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

async def synctest():
	credjson=await database.getvar('gmail_cred')
	creds=Credentials(
		token=credjson['access_token'],
		refresh_token=credjson['refresh_token'],
		token_uri=credjson['token_uri'],
		client_id=client_creds['client_id'],
		client_secret=client_creds['client_secret']
	)
	if creds.expired:
		creds.refresh(Request())
	service = build('gmail', 'v1', credentials=creds)
	return service


async def tryrun():
	global aioggl,gmail
	await getgmail()
	lastlist = await aioggl.as_user(  # the request is being sent here
            gmail.users.messages.list(
                userId='me',includeSpamTrash=True,maxResults=1
            )
        )
	await handlenewemail(lastlist['messages'][0])
	return None
	
	#########################
	lastid=lastlist['messages'][0]['id']

	lastmssg=await aioggl.as_user(  # the request is being sent here
		gmail.users.messages.get(
			userId='me',id=lastid
		)
	)
	
	straggr=email()
	for x in lastmssg['payload']['parts']:
		await handlepart(x,straggr)

	return straggr.s

		
	#service = build('gmail', 'v1', credentials=credentials)
	
	#messages=service.users().messages()
	
	#tmp=messages.list(userId='me',includeSpamTrash=True,maxResults=1)

	#return tmp

	
	#results = service.users().labels().list(userId='me').execute()
	#labels = results.get('labels', [])
	#if not labels:
	#	print('No labels found.')
	#else:
	#	print('Labels:')
	#	for label in labels:
	#		print(label['name'])


'''

client_secret=json.loads(os.getenv('gmail_client_secret'))
#print('tmp2')

flow = google_auth_oauthlib.flow.Flow.from_client_config(
	client_secret,
	scopes=['https://www.googleapis.com/auth/gmail.readonly'])
#print('tmp3')
flow.redirect_uri = 'https://xinyangchen.repl.co/test'
#print('tmp4')


def getauthurl():
	url,state=flow.authorization_url(
		access_type='offline', include_granted_scopes='false')#example has this as true
	return url

print(getauthurl())


credentials=None
def authresponse(authorization_response):
	global credentials
	flow.fetch_token(
		authorization_response=authorization_response)
	credentials = flow.credentials
'''

'''
	tmp = {
		'token': credentials.token,
		'refresh_token': credentials.refresh_token,
		'token_uri': credentials.token_uri,
		'client_id': credentials.client_id,
		'client_secret': credentials.client_secret,
		'scopes': credentials.scopes}
'''

'''

def tryrun():
	service = build('gmail', 'v1', credentials=credentials)
	
	messages=service.users().messages()
	
	tmp=messages.list(userId='me',includeSpamTrash=True,maxResults=1)

	return tmp

	
	#results = service.users().labels().list(userId='me').execute()
	#labels = results.get('labels', [])
	#if not labels:
	#	print('No labels found.')
	#else:
	#	print('Labels:')
	#	for label in labels:
	#		print(label['name'])


'''

