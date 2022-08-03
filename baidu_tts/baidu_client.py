from aip import AipSpeech
from appPublic.uniqueID import getId
from .appkey import APPID, APPKEY, SECRET_KEY

class BaiduClient(AipSpeech):
	def __init__(self, APPID, APPKEY, SECRET_KEY):
		AipSpeech(self, APPID, APPKEY, SECRET_KEY)
		self.cuid = getId()

