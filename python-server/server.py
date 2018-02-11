#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: Theo
# @Date:   2018-02-10 14:12:12
# @Last Modified by:   Theo
# @Last Modified time: 2018-02-11 13:02:47

'''packages: 
sudo pip3 install gTTS
pip3 install wolframalpha
pip3 install mpg321
pip3 install cryptography
pip3 install pickle
'''
import socket
import wolframalpha
import hashlib
from cryptography.fernet import Fernet
import pickle
from gtts import gTTS
import os

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
app_id="Q34244-EVW4A8EQRP"
# server_ip = sys.argv[2]
# server_port = sys.argv[4]
# socket_size = sys.argv[6]
host = ''
port = 8085
backlog = 5
size = 1024
#===========================    initialize   ==============================
WAclient = wolframalpha.Client(app_id)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(backlog)


#===========================    main   ==============================



# hasher = hashlib.md5()
# for i in range(0, len(question_encrypt), 8192):
#     hasher.update(question_encrypt[i: i + 8192])
# hash_value = hasher.hexdigest
# send_question = (key,question_encrypt,hash_value)
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




