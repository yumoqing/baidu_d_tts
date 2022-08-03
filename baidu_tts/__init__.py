
class NoAppRegisterInfo(Exception):
	pass

def buildDriver(proxy):
	return BaiduTTSDriver(proxy)

class BaiduTTSDriver:
	def __init__(self, proxy):
		if self.no_app_info(self):
			raise NoAppRegisterInfo()
		self._proxy = proxy
		self._tts = Baidu
