import discordbot
import gmail



async def defaulthandler(mail):
	await discordbot.sendloggingmessage(
		'email',
		mail.getinfo(),
		file=await discordbot.filefromstring(mail.text)
	)


@gmail.newhandler
