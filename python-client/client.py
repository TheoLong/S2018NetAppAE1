#!/usr/bin/env python3
import sys
import socket
import keys
from tweepy import StreamListener
from tweepy import Stream
from tweepy import OAuthHandler
import pickle
from cryptography.fernet import Fernet
import hashlib

server_ip = sys.argv[2]
server_port = sys.argv[4]
socket_size = sys.argv[6]
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
        hash_value = hasher.hexdigest
        send_question = (key,question_encrypt,hash_value)
        print(question)
        print(key)
        print(question_encrypt)
        print(hash_value)

# setup connection
auth = OAuthHandler(keys.API_Key(), keys.API_Secret())
auth.set_access_token(keys.Access_Token(), keys.Access_Secret())
# start a listener
myStream = Stream(auth, MyStreamListener())
#
myStream.filter(track=[tag])

# -------------------------------
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((server_ip, server_port))
