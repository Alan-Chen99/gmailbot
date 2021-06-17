from discordbot import newvarlevel

#TODO: check if pm for some levels

@newvarlevel('message')
async def levelmessage(message):
	if message:
		return message.id

@newvarlevel('channel')
async def levelchannel(message):
	if message:
		return message.channel.id

@newvarlevel('category')
async def levelcategory(message):
	if message:
		return message.channel.category_id

@newvarlevel('guild')
async def levelguild(message):
	if message:
		return message.guild.id

@newvarlevel('author')
async def levelauthor(message):
	if message:
		return message.author.id

@newvarlevel('default')
async def leveldefault(message):
	return 'default'
