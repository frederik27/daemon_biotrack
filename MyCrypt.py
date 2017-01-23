###
#   This is an utility uses for crypting
#   Author is Ulug'bek Ro'zimboyev <ulugbekrozimboyev@gmail.com>
#   version 1.0.1
#
#   User guide:
#       - this library generete password themself. password is made by @_getRandomString function
#       -
#
###
import hashlib
import random
import string
import binascii

class MyAuthModel:

    password = None
    salt = None
    key = None

    ###
    #   generete random string
    #   @length is size of created word
    #   @return string
    ###

    def _getRandomString(self, length = 8):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def generateKey(self):
        passwordStr = self._getRandomString()
        passwordByte = str.encode(passwordStr)
        self.password = passwordStr
        #print(passwordStr)

        hash_object = hashlib.sha1(passwordByte)
        hash_dig = str.encode(hash_object.hexdigest())
        #print(hash_dig)

        saltStr = self._getRandomString(7)
        saltByte = str.encode(saltStr)
        self.salt = saltStr
        #print(saltStr)
        # dk = hashlib.pbkdf2_hmac('sha256', hash_dig, salt, 1)
        dk = hashlib.sha256(hash_dig + saltByte)
        key = dk.hexdigest()
        self.key = key

        return key

