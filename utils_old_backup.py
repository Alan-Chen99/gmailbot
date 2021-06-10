"""Utilities"""
import hashlib
import os
from aiohttp import web
import asyncio_throttle
import base64
from passlib import pwd
from passlib.hash import sha512_crypt
#import hmac



adminpwdhash=os.getenv('adminpwdhash')

discord_user_pwd=os.getenv('discord_user_pwd')






def tocode(s):
	return base64.b16encode(s.encode()).decode()
def fromcode(s):
	return base64.b16decode(s.encode()).decode()

def newpwd():
	global webpwd
	webpwd=pwd.genword(entropy=512)

def gethash(key):
	return tocode(sha512_crypt.hash(key,rounds=1000))
def verhash(key,hash):
	return sha512_crypt.verify(key,fromcode(hash))


def adminauth(func):
	"""Decorator to check for an API key"""  
	async def route(req):
		#data=await req.post()
		authstr=req.headers.get("Authorization")
		if not authstr:
			return web.json_response({
				'error': "Missing Authorization header"
			}, status=401)
		if authstr[:6]!="Basic ":
			return web.json_response({
				'error': "The authorization header isn't Basic"
			}, status=401)
		authstr=authstr[6:]
		authstr=base64.b64decode(authstr).decode()
		authlist=authstr.split(':')

		if len(authlist)!=2:
			return web.json_response({
				'error': "Incorrect authorization format"
			}, status=401)

		if authlist[0]!='admin':
			return web.json_response({
				'error': "admin required"
			}, status=401)

		key = authlist[1]
		valid = verhash(key,adminpwdhash)
		if valid:
			return await func(req)
		return web.json_response({
			'error': "Invalid admin key"
		}, status=401)
	return route


def ratelimit(limit, period=1, **kwargs):
    throttler = asyncio_throttle.Throttler(limit, period=period, **kwargs)

    def decorator(func):
        async def handler(req):
            async with throttler:
                return await func(req)
        
        return handler
    
    return decorator


