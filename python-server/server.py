# -*- coding: utf-8 -*-
# @Author: Theo
# @Date:   2018-02-10 14:12:12
# @Last Modified by:   Theo
# @Last Modified time: 2018-02-10 14:42:12

'''packages: 
sudo pip install gTTS
pip install wolframalpha
'''
import wolframalpha
from gtts import gTTS
import os
app_id="Q34244-EVW4A8EQRP"
client = wolframalpha.Client(app_id)

question = "Who killed the radio star"
res = client.query(question)

tts = gTTS(text=question, lang='en')
tts.save("tts.mp3")
os.system("mpg321 tts.mp3")
# for pod in res.pods:
#     print(pod)
print(next(res.results).text)
tts = gTTS(text=next(res.results).text, lang='en')
tts.save("tts.mp3")
os.system("mpg321 tts.mp3")