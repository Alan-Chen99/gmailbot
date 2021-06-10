from .lib import newvarlevel

#TODO: check if pm for some levels
message='message'
@newvarlevel(message)
async def levelmessage(message):
	if message:
		return message.id

channel='channel'
@newvarlevel(channel)
async def levelchannel(message):
	if message:
		return message.channel.id

category='category'
@newvarlevel('category')
async def levelcategory(message):
	if message:
		return message.channel.category_id

guild='guild'
@newvarlevel(guild)
async def levelguild(message):
	if message:
		return message.guild.id

author='author'
@newvarlevel(author)
async def levelauthor(message):
	if message:
		return message.author.id

default='default'
@newvarlevel(default)
async def leveldefault(message):
	return 'default'
