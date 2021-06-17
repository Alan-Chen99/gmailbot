from aiohttp import web
from aiohttp.web import Response

app = web.Application()
routes = web.RouteTableDef()

@routes.get("/")
async def homepage(req):
	return Response(text="hello world")

async def start():
	app.add_routes(routes)
	runner = web.AppRunner(app)
	await runner.setup()
	site = web.TCPSite(runner, '0.0.0.0', 8080)
	await site.start()