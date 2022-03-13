from . import creds
from .vars import gmailvars
from discordbot import bot as discord
from discordbot import vars as discordvars
from discordbot import defaultvars as discorddefaultvars

import aiogoogle
import aiohttp

import logging
import asyncio
import re

gmail_historyid_async=gmailvars['gmail_historyid']

async def gethistoryid():
	aioggl=await creds.getaioggl
	gmail=await creds.getgmail
	
	gmail_historyid_var=await gmail_historyid_async

	tmp=gmail_historyid_var()
	if tmp==None:
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
		gmail_historyid_var<<tmp
	return tmp



import base64

class email:
	def __init__(self):
		self.id=''
		self.dto=''
		self.rtpath=''
		self.source=''
		self.date=''
		self.subject=''
		self.to=''
		self.cc=''
		self.text=''
		self.gotfor=''
		self.listid=''
		self.labels=[]
	def getinfo(self):
		return (
			f'id: {self.id}\n'
			f'labels: {repr(self.labels)}\n'
			f'dto: {self.dto}\n'
			f'rtpath: {self.rtpath}\n'
			f'source: {self.source}\n'
			f'date: {self.date}\n'
			f'subject: {self.subject}\n'
			f'to: {self.to}\n'
			f'cc: {self.cc}\n'
			f'listid: {self.listid}\n'
			#bcc?
			f'for: {self.gotfor}\n'
		)
		
def decode64(b64s):
	return base64.urlsafe_b64decode(b64s).decode("utf-8")

async def handlepart(part,mail):#TODO: some email might only have html in which this will return empty
	if part['mimeType']=='multipart/alternative':
		for x in part['parts']:
			await handlepart(x,mail)
	else:
		if part['mimeType']=='text/plain':
			mail.text=mail.text+decode64(part['body']['data'])



async def handlenewemail(messagemeta):
	aioggl=await creds.getaioggl
	gmail=await creds.getgmail
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
	mail.id=mssgid
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
		if x['name']=='List-ID':
			mail.listid=x['value']
		if x['name']=='Received':
			rerst=re.findall(r'(?<=for <)[^\s@]+@[^\s@]+\.[^\s@]{2,}(?=>)', x['value'])
			if len(rerst)>1:
				logging.warning(f'{repr(x["value"])} contains more than 1 email')
			else:
				if len(rerst)==1:
					mail.gotfor=rerst[0].lower()
			#not entirely sure if this works
			#get oldest send for
			#supposed to be ordered from newest to oldest

	await handlepart(mssg['payload'],mail)
	#for x in mssg['payload']['parts']:
	#	await handlepart(x,mail)

	
	#mail.toinfo=(await database.getvar('email_to_info'))[mail.gotfor]
	#mail.frominfo=(await database.getvar('email_from_info'))[mail.source]

	#discordmsg=await discord.send(
	#	'email',
	#	mail.getinfo(),
	#	file=await discord.filefromstring(mail.text)
	#)
	#print(f'listid{mail.listid}')
	#print(mail.getinfo())
	if mail.listid:
		discordmsg=await discord.send_cat(
			'email_lists',
			mail.listid,
			'info:',
			file=await discord.filefromstring(mail.getinfo())
		)
		discordmsg=await discord.send_cat(
			'email_lists',
			mail.listid,
			'content:',
			file=await discord.filefromstring(mail.text)
		)
	else:
		if not mail.gotfor:
			mail.gotfor='empty_for'
		discordmsg=await discord.send_cat(
			'email',
			mail.gotfor,
			'info:',
			file=await discord.filefromstring(mail.getinfo())
		)
		discordmsg=await discord.send_cat(
			'email',
			mail.gotfor,
			'content:',
			file=await discord.filefromstring(mail.text)
		)
	await discordvars.setdiscordvar(discordmsg,discordvars.levels.message,discorddefaultvars.email_id,mssgid)
	return mail
	
#emaildiscordhandlers=[]
#def newhandler(handler):
#	emaildiscordhandlers.append(handler)
#	return handler

#class conditionnotmet(Exception):
#	pass

#async def pushemail(mail):
#	for handler in emaildiscordhandlers:
#		try:
#			handler(mail)
#			return None
#		except conditionnotmet:
#			pass

#def email_to_handletype_only(handletype):
#	def internal(handler):
#		def newhandler(mail):
#
#			if await database.getvar('email_to_info'):
#				pass


async def checkmail():
	aioggl=await creds.getaioggl
	gmail=await creds.getgmail
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
			gmail_historyid_async<<history['id']
	gmail_historyid_async<<historyall['historyId']


async def getlastfull():
	aioggl=await creds.getaioggl
	gmail=await creds.getgmail
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

async def getrawfromid(emailid):
	aioggl=await creds.getaioggl
	gmail=await creds.getgmail
	return await aioggl.as_user(  # the request is being sent here
		gmail.users.messages.get(
			userId='me',id=emailid
		)
	)

#@discord.ondiscordready
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