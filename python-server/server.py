#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: Theo
# @Date:   2018-02-10 14:12:12
# @Last Modified by:   Theo
# @Last Modified time: 2018-02-11 15:06:16

'''packages: 
sudo pip3 install gTTS
pip3 install wolframalpha
pip3 install mpg321
pip3 install cryptography
pip3 install pickle
'''
from cryptography.fernet    import Fernet
from gtts                   import gTTS
import socket
import wolframalpha
import hashlib
import pickle
import serverKeys
import argparse
import os
#===========================    arguments   ==============================
parser = argparse.ArgumentParser(description='Arguments for server.')
parser.add_argument("-p", "--server_port",  help="server port", action="store_true", default=8080)
parser.add_argument('-b', "--backlog_size", help="backlog size",action="store_true", default=5)
parser.add_argument('-z', "--socket_size",  help="socket size", action="store_true", default=1024)

#===========================    functions   ==============================
def speak(string):
    tts = gTTS(text=question, lang='en')
    tts.save("ttsCache.mp3")
    os.system("mpg321 ttsCache.mp3")

def depackage(package):
    package = pickle.loads(package)  
    key = package[0]
    question = package[1]
    md5 = package[2]
    if md5 != hash(question):
        print("md5 is wrong, package lost")
        speak("md5 is wrong, package lost")
        return 0

    encryptor = Fernet(key)
    question = encryptor.decrypt(question)
    question = question.decode('utf-8')
    print ('========Question: ' + question)
    return question

def pack(answer):
    key = Fernet.generate_key()
    encryptor = Fernet(key)
    answer_encrypt = encryptor.encrypt(bytes(answer, 'utf-8'))
    # hash
    hasher = hashlib.md5()
    for i in range(0, len(answer_encrypt), 8192):
        hasher.update(answer_encrypt[i: i + 8192])
    md5 = hasher.digest()
    send = (key,answer_encrypt,md5)
    send_answer = pickle.dumps(send)
    return send_answer
    
def hash(data):
    hasher = hashlib.md5()
    for i in range(0, len(data), 8192):
        hasher.update(data[i: i + 8192])
    return hasher.digest()
#===========================    loading data   ==============================
args = parser.parse_args()
host = ''
port = args.server_port
backlog = args.backlog_size
size = args.socket_size
print(port)
print(backlog)
print(size)

#===========================    initialize   ==============================
WAclient = wolframalpha.Client(serverKeys.wolframalpha_appid())
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(backlog)

#===========================    main   ==============================
while 1:
    print('======== Waiting for question')
    client, address = s.accept()
    package = client.recv(size)
    if package:
        #ask the question
        question = depackage(package)
        if question == 0:
            question = "I think I missed the question"
            speak(question)
        else:
            speak(question)
            res = WAclient.query(question)

            #return question
            answer = str(next(res.results).text)
            print ('========Answer: ' + answer)
            package = pack(answer)
            client.send(package)
            client.close()




