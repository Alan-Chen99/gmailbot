'''
import uuid

def getuuid():#128 bit uuid
	return uuid.UUID(int=uuid.uuid1().int^uuid.uuid4().int).hex

import hashlib

def hash(string):#128 bit hash
	return hashlib.sha256(string.encode('utf-8')).hexdigest()[:32]

#TODO: make those better

def hashmerge(uuid128,hash128):
	return hash(uuid128+hash128)
	#return hex(int(uuid128,16)^int(hash128,16))[2:]

rdstr=hash('rdstr')
def hashmergeint(uuid128,index):
	return hash(uuid128+str(index)+rdstr)
	#return hex(int(uuid128,16)^index)[2:]#does not work since collsion for index==0
'''