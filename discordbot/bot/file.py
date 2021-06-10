import io
import discord

async def filefromstring(text,filename="file.txt"):
	f = io.StringIO(str(text))
	return discord.File(fp=f,filename=filename)