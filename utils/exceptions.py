import traceback


def exceptiontest():
	return 1/0

def excpetiontostring(ex):
	return "".join(traceback.TracebackException.from_exception(ex).format())
	#return ''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__))