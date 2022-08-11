# baidu_d_tts
a tts driver used by [unitts](https://pypi.org/project/unitts)

# Dependent

```
pip install requests
```

## installation
```
pip install baidu_d_tts
```

## Usage

```
from baidu_d_tts.baidu_ai_api import set_app_info
import unitts

set_app_info(appid, appkey, secret_key)
tts = unitts.init('baidu_d_tts')
tts.say('This is a test')
```
