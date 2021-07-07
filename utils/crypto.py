import os
import base64
from passlib import pwd
from passlib.hash import sha512_crypt
#import hmac
from dotenv import load_dotenv

load_dotenv()



adminpwdhash=os.getenv('adminpwdhash')

discord_user_pwd_hash=os.getenv('discord_user_pwd_hash')



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

def getenv(name):
	tmp=os.environ[name]
	return fromcode(tmp)