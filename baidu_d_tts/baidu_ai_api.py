
import base64
from urllib.parse import quote_plus
from appPublic.uniqueID import getID
from appPublic.http_client import Http_Client

import shutil
import io

class NoAppRegisterInfo(Exception):
	pass

app_info = {
}

def set_app_info(appid, appkey, secret_key):
	app_info.update({
		'appkey':appkey,
		'appid':appid,
		'secret_key':secret_key
	})

SUPPORT_LANG={
	'zh_CN':'1537',
	'en_US':'1737',
	'zh_GD':'1637',
	'zh_SC':'1837',
	'zh_CNF':'1936'
}

PERS={
	'duxiaomei':0,
	'duxiaoyu':1,
	'duxiaoyao':3,
	'duyaya':4
}

class BaiduAudioApi:
	def __init__(self, lang='zh_CN',
				rate=5, volume=5, pitch=5):
		self.access_token = None
		self._auth_()
		self.cuid = getID()
		self.asr_params = {
			'dev_pid':SUPPORT_LANG.get('zh_CN'),
			'format':'wav',
			'rate':'16000',
			'token':self.access_token,
			'cuid':self.cuid,
			'channel':'1',
		}
		self.headers = {
			"Content-type":"application/json"
		}
		self.tts_params = {
			# 发音人选择, 基础音库：0为度小美，1为度小宇，3为度逍遥，4为度丫丫，
			# 精品音库：5为度小娇，103为度米朵，106为度博文，110为度小童，111为度小萌，默认>为度小美
			# 语速，取值0-15，默认为5中语速
			# 音调，取值0-15，默认为5中语调
			# 音量，取值0-9，默认为5中音量
			# 下载的文件格式, 3：mp3(default) 4： pcm-16k 5： pcm-8k 6. wav

			'tok':self.access_token,
			'per':PERS.get(0),
			'spd':5,
			'pit':5,
			'vol':5,
			'aue':4,
			'cuid':self.cuid,
			'lan':'zh',
			'ctp':1
		}
		self.lang = lang
		self.rate = rate
		self.pitch = pitch
		self.volume = volume
		self.asr_url = 'http://vop.baidu.com/server_api'
		self.tts_url = 'http://tsn.baidu.com/text2audio'

	def _auth_(self):
		if app_info == {}:
			raise NoAppRegisterInfo()

		url = "https://aip.baidubce.com/oauth/2.0/token"
		params = {
			"grant_type":"client_credentials",
			"client_id":app_info.get('appkey'),
			"client_secret":app_info.get('secret_key')  #SECRET_KEY
		}
		hc = Http_Client()
		x = hc.post(url, params=params)

		if isinstance(x, dict):
			self.scopes = x.get('scopes', '').split(' ')
			self.access_token = x.get('access_token')
			if self.access_token is None:
				print('error', x)

	def asr(self, audio_buffer):
		length = len(audio_buffer)
		speech = base64.b64encode(audio_buffer)
		params = self.asr_params.copy()
		params['len'] = length
		print('params=',params)
		params['speech'] = speech.decode('utf-8')
		hc = Http_Client()
		x = hc.post(self.asr_url, 
				params=params,
				headers=self.headers
		)
		print('x=', x)
		return x

	def tts_get_rate(self):	
		return self.tts_params.get('spd')

	def tts_get_pitch(self):
		return self.tts_params.get('pit')

	def tts_get_voice(self):
		return self.tts_params.get('per')

	def tts_get_format(self):
		return self.tts_params.get('aue')

	def tts_get_volume(self):
		return self.tts_params.get('vol')

	def tts_get_language(self):
		return self.tts_params.get('lan')

	def tts_set_language(self, lang):
		self.tts_params['lan'] = lang

	def tts_set_rate(self, rate):
		if rate < 0 or rate > 15:
			return 

		self.tts_params['spd'] = rate

	def tts_set_pitch(self, pitch):
		if pitch < 0 or pitch > 15:
			return

		self.tts_params['pit'] = pitch

	def tts_set_voice(self, voice):
		self.tts_params['per'] = voice

	def tts_set_volume(self, vol=5):
		if vol < 0 or vol > 9:
			return

		self.tts_params['vol'] = vol

	def tts_set_format(self, fmt=3):
		if fmt not in [3, 4, 5, 6]:
			return
		self.tts_params['aue'] = fmt

	def tts(self, text):
		tex = quote_plus(text)
		params = self.tts_params.copy()
		params.update({'tex':tex})
		hc = Http_Client()
		x = hc.post(self.tts_url, params=params, stream=True)
		ct = x.headers.get('Content-Type')
		if ct == 'application/json':
			err = x.json()
			print(params, err)
			return None
		# 'Content-Type': 'audio/basic;codec=pcm;rate=16000;channel=1'
		ct_parts = ct.split(';')
		
		print('tts resp headers=', x.headers)
		buf = x.content
		return buf

if __name__ == '__main__':
	from kivycv.audio import Audio
	api = BaiduAudioApi()
	a = Audio()
	text1 = '余模清正在做百度智能接口测试'
	buf = api.tts(text1)
	fn = a.tmpfile()
	a.write_audiofile(fn, buf, channels=1, rate=16000)
	a.replay(fn)
	with open(fn, 'rb') as f:
		buf = f.read()
		api1 = BaiduAudioApi()
		text2 = api1.asr(buf)
		print(text2)
