import datetime

lasttime=None


def timepoint(name):
	global lasttime
	if lasttime is not None:
		print(datetime.datetime.now()-lasttime)
	lasttime=datetime.datetime.now()
	print(f'timepoint {name}')