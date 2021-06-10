import datetime
import pytz


lasttime=None


def timepoint(name):
	global lasttime
	if lasttime is not None:
		print(datetime.datetime.now()-lasttime)
	lasttime=datetime.datetime.now()
	print(f'timepoint {name}')




def timestringnow():
	return datetime.datetime.now(tz=pytz.timezone("America/Chicago"))

def loggingtimenow(*args):
	#utc_dt = datetime.utc.localize(datetime.utcnow())
	#my_tz = pytz.timezone("US/Eastern")
	#converted = utc_dt.astimezone(my_tz)
	return timestringnow().timetuple()