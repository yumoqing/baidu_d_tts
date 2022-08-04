import os
import time
from traceback import print_exc
import tempfile
from .baidu_ai_api import BaiduAudioApi
from pyttsx3.voice import Voice
from appPublic.audioplayer import AudioPlayer
from appPublic.background import Background
class NoAppRegisterInfo(Exception):
	pass

def buildDriver(proxy):
	return BaiduTTSDriver(proxy)

Voices = [
	Voice('0', 'duxiaomei', ['zh_CN', 'en_US'], '0', 24),
	Voice('1', 'duxiaoyu', ['zh_CN', 'en_US'], '1', 24),
	Voice('3', 'duxiaoyao', ['zh_CN', 'en_US'], '1', 24),
	Voice('4', 'duyaya', ['zh_CN', 'en_US'], '0', 24),
]

def temp_file(suffix='.txt'):
	x = tempfile.mkstemp(suffix=suffix)
	os.close(x[0])
	return x[1]

def write_tmp_mp3file(raw):
	fn = temp_file(suffix='.mp3')
	with open(fn, 'wb') as f:
		f.write(raw)

	return fn

class BaiduTTSDriver:
	def __init__(self, proxy):
		self._proxy = proxy
		self._tts = BaiduAudioApi()
		self.player = AudioPlayer(on_stop=self.speak_finish)
		self.rate = 5
		self.volume = 1
		self.pitch = 5
		self.language = 'zh'
		self.format = 3
		self.voice = 0
		self.cmds = []
		self._completed = True
		self.running = True
		self.task = None

	def backtask(self):
		print('player back task running ...')
		while self.running:
			self._pump()
			time.sleep(0.01)
		print('player back task end ...')

	
	def speak_finish(self):
		print('callback:speak_finish() called')
		self._proxy.notify('finished-utterance')
		self._proxy.setBusy(False)
		os.unlink(self.player.source)
		# self._pump()

	def _push(self, cmd):
		self.cmds.append(cmd)
		# self._pump()

	def _pump(self):
		if self.player.is_busy():
			# print('player is busy', self.player.loop,
			# 		'state=',self.player.state, 
			# 		'autoplay=', self.player.autoplay)
			return False
		if len(self.cmds) < 1:
			# print('No cmd to do')
			return False

		c, fn = self.cmds.pop(0)
		self.player.set_source(fn)
		self.player.play()
		print('play ...', fn)
		self._proxy.notify('started-utterance')
		return True

	def destroy(self):
		self.player.unload()
	
	def startLoop(self, *args):
		print('startLoop() called')
		self._proxy.setBusy(False)
		self.task = Background(self.backtask)
		self.task.start()

	def endLoop(self):
		print('endLoop() called')
		self.cmds = []
		self._proxy.setBusy(False)
		if self.task:
			self.running = False
			self.task.join()
			self.task = None

	def iterate(self):
		self._proxy.setBusy(False)
		yield
	
	def say(self, text):
		try:
			self._proxy.setBusy(False)
			self._completed = True
			y = self._tts
			y.tts_set_rate(self.rate)
			y.tts_set_pitch(self.pitch)
			y.tts_set_voice(self.voice)
			y.tts_set_language(self.language)
			y.tts_set_format(self.format)
			raw = y.tts(text)
			if raw is None:
				print('baidu api error')
				return
			mp3file = write_tmp_mp3file(raw)
			print('gen mp3 file:', mp3file)
			self._push(('play', mp3file))
		except Exception as e:
			print('error:', e)
			print_exc()

	def stop(self):
		if self._proxy.isBusy():
			self._completed = False
		self.player.stop()

	def getProperty(self, name):
		if name == 'voices':
			return Voices

		if name == 'voice':
			for v in Voices:
				if v.id == self.voice:
					return v
			return None
		if name == 'rate':
			return self.rate
		if name == 'volume':
			return self.volume
		if name == 'pitch':
			return self.pitch
	
	def setProperty(self, name, value):
		if name == 'voice':
			self.voice = value
		if name == 'rate':
			self.rate = value
		if name == 'pitch':
			self.rate = value
		if name == 'language':
			self.language = value
		if name == 'volume':
			self.volume = value

