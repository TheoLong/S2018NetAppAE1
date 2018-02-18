#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: Theo
# @Date:   2018-02-10 14:12:12
# @Last Modified by:   Theo
# @Last Modified time: 2018-02-17 21:21:02

'''packages: 
sudo pip3 install gTTS
pip3 install wolframalpha
pip3 install cryptography
pip3 install pickle
sudo apt-get install mpg321
'''
from cryptography.fernet    import Fernet
from gtts                   import gTTS
from serverKeys             import wolfram_alpha_appid
import socket
import wolframalpha
import hashlib
import pickle
import argparse
import os
#===========================    arguments   ==============================
parser = argparse.ArgumentParser(description='Arguments for server.')
parser.add_argument('-p', dest='server_port',  help="server port", action="store", type=int, default=80)
parser.add_argument('-b', dest="backlog_size", help="backlog size",action="store", type=int, default=1)
parser.add_argument('-z', dest="socket_size",  help="socket size", action="store", type=int, default=1024)
args=parser.parse_args()

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
host = ''
port = args.server_port
backlog = args.backlog_size
size = args.socket_size

#===========================    initialize   ==============================
WAclient = wolframalpha.Client(wolfram_alpha_appid)
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("======= Created socket on port " + str(port))
except socket.error as message:
    if s:
        s.close()
    print ("======= Unable to open socket: " + str(message))    
s.bind((host, port))
s.listen(backlog)

#===========================    main   ==============================
while 1:
    print('======= Waiting for question')
    client, address = s.accept()
    package = client.recv(size)
    if package:
        #ask the question
        question = depackage(package)
        if question == 0:
            question = "!!!!!!! I think I missed the question"
            speak(question)
        else:
            print("======= Question: "+question)
            speak(question)
            res = WAclient.query(question)

            #return question
            try:
                answer = str(next(res.results).text)
            except:
                answer = "I think the answer is too complicate to speak out"
            print ('======= Answer: ' + answer)
            package = pack(answer)
            client.send(package)
            print ('======= Answer sent!')
            client.close()




