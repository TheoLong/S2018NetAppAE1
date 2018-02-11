#!/usr/bin/env python3
import sys
import socket
import keys
from tweepy import StreamListener
from tweepy import Stream
import os
from tweepy import OAuthHandler
import pickle
from cryptography.fernet import Fernet
import hashlib
from gtts import gTTS

#server_ip = sys.argv[2]
server_ip = "192.168.1.115"
#server_port = sys.argv[4]
server_port = 8085

#socket_size = sys.argv[6]
socket_size = 1024
# tag = sys.argv[8]
tag = "#ECE4564T24"


# override tweepy.StreamListener to add logic to on_status
class MyStreamListener(StreamListener):

    def on_status(self, status):
        question = status.text.replace("#ECE4564T24", "")
        # encrypt
        key = Fernet.generate_key()
        encryptor = Fernet(key)
        question_encrypt = encryptor.encrypt(bytes(question, 'utf-8'))
        # hash
        hasher = hashlib.md5()
        for i in range(0, len(question_encrypt), 8192):
            hasher.update(question_encrypt[i: i + 8192])
        hash_value = hasher.digest()
        send = (key,question_encrypt,hash_value)
        send_question = pickle.dumps(send)
        print(question)
        print(key)
        print(question_encrypt)
        print(hash_value)
        # receive
        # setup server connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server_ip, server_port))
        s.send(send_question)
        while 1:
            data = s.recv(socket_size)
            if data:
                answer_struct = pickle.loads(data)
                answer_key = answer_struct[0]
                answer_encrypt = answer_struct[1]
                answer_md5 = answer_struct[2]
                check_hasher = hashlib.md5()
                for i in range(0, len(answer_encrypt), 8192):
                    check_hasher.update(answer_encrypt[i: i + 8192])
                check_md5 = check_hasher.digest()
                if check_md5 == answer_md5:
                    print("md5 is correct")
                    answer_encryptor = Fernet(answer_key)
                    answer = answer_encryptor.decrypt(answer_encrypt)

                    answer = answer.decode('utf-8')

                    print(answer)
                    tts = gTTS(text=answer, lang="en")
                    tts.save("answer.mp3")
                    os.system("mpg321 answer.mp3")
                    s.close()
                    break

                else:
                    print("md5 is wrong, package lost!")
                    s.close()
                    break

# setup connection
auth = OAuthHandler(keys.API_Key(), keys.API_Secret())
auth.set_access_token(keys.Access_Token(), keys.Access_Secret())

# start a listener
myStream = Stream(auth, MyStreamListener())
#
myStream.filter(track=[tag])

