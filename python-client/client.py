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

server_ip = sys.argv[2]
#server_ip = "192.168.1.115"
server_port = sys.argv[4]
#server_port = 8085

socket_size = sys.argv[6]
#socket_size = 1024
tag = sys.argv[8]
#tag = "#ECE4564T24"

# ----------------------------------functions--------------------------


def hash_build(text):
    hasher = hashlib.md5()
    for i in range(0, len(text), 8192):
        hasher.update(text[i: i + 8192])
    hash_value = hasher.digest()
    return hash_value


def encrypt(text):
    key = Fernet.generate_key()
    encryptor = Fernet(key)
    question_encrypt = encryptor.encrypt(bytes(text, 'utf-8'))
    return (question_encrypt,key)


def check_sum(text, hash):
    check_hasher = hashlib.md5()
    for i in range(0, len(text), 8192):
        check_hasher.update(text[i: i + 8192])
    check_md5 = check_hasher.digest()
    return hash == check_md5


def decrypt(text,key):
    answer_encryptor = Fernet(key)
    answer = answer_encryptor.decrypt(text)
    answer = answer.decode('utf-8')
    return answer


# -------------------override tweepy.StreamListener to add logic to on_status
class MyStreamListener(StreamListener):

    def on_status(self, status):
        question = status.text.replace(tag, "")
        # encrypt
        (question_encrypt, key) = encrypt(question)
        # hash
        hash_value = hash_build(question_encrypt)
        # pickle
        send = (key, question_encrypt, hash_value)
        send_question = pickle.dumps(send)
        print("The question is: " + question)
        print("The key is: " + key)
        print("The encrypted question is: " + question_encrypt)
        print("The MD5 Hash value is:" + hash_value)
        # receive
        # setup server connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server_ip, server_port))
        s.send(send_question)
        while 1:
            data = s.recv(socket_size)
            if data:
                # load data using pickle
                answer_struct = pickle.loads(data)
                answer_key = answer_struct[0]
                answer_encrypt = answer_struct[1]
                answer_md5 = answer_struct[2]
                # check_sum
                noncrop = check_sum(answer_encrypt, answer_md5)
                if noncrop:
                    print("MD5 is correct")
                    answer = decrypt(answer_encrypt, answer_key)
                    print("The answer is: " + answer)
                    # speak it out
                    tts = gTTS(text=answer, lang="en")
                    tts.save("answer.mp3")
                    os.system("mpg321 answer.mp3")
                    s.close()
                    break

                else:
                    print("MD5 is wrong, package lost!")
                    s.close()
                    break


# -------------------main start here----------------------------------
# setup connection
auth = OAuthHandler(keys.API_Key(), keys.API_Secret())
auth.set_access_token(keys.Access_Token(), keys.Access_Secret())
# start a listener
myStream = Stream(auth, MyStreamListener())
# filter out string with tag
myStream.filter(track=[tag])

