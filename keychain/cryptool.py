import base64
import hashlib
import random

import rsa
from Crypto.Cipher import AES

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]


def encrypt_aes(content, key, salt='', iv=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'):
    content = pad(content)
    if salt != '':
        key = salt + '%' + key
    keybyte = key.encode('utf-8')
    keysha256 = hashlib.sha256(keybyte).digest()

    cipher = AES.new(keysha256, AES.MODE_CBC, iv)
    # cipher = AES.new(keysha256,AES.MODE_ECB)

    contentbyte = content.encode('utf-8')
    cryptbyte = cipher.encrypt(contentbyte)
    cryptbase64byte = base64.encodestring(cryptbyte)
    cryptbase64 = cryptbase64byte.decode('utf-8')
    cryptbase64 = cryptbase64[:cryptbase64.rindex('\n')]
    return cryptbase64


def decrypt_aes(cryptbase64, key, salt='', iv=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'):
    if salt != '':
        key = salt + '%' + key
    keybyte = key.encode('utf-8')
    keysha256 = hashlib.sha256(keybyte).digest()

    cipher = AES.new(keysha256, AES.MODE_CBC, iv)
    # cipher = AES.new(keysha256,AES.MODE_ECB)
    cryptbase64byte = cryptbase64.encode('utf-8')
    cryptbyte = base64.decodestring(cryptbase64byte)
    contentbyte = cipher.decrypt(cryptbyte)
    content = contentbyte.decode('utf-8')
    return unpad(content)


def encrypt_rsa_base64(content, pubkeyfilepath):
    contentbyte = content.encode('utf-8')
    with open(pubkeyfilepath, 'rb') as pubkeyfile:
        pubkeydata = pubkeyfile.read()
        pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(pubkeydata)
        cryptbyte = rsa.encrypt(contentbyte, pubkey)
        cryptbase64byte = base64.encodestring(cryptbyte)
        cryptbase64 = cryptbase64byte.decode("utf-8")
        return cryptbase64


def decrypt_rsa_base64(cryptbase64, prikeyfilepath):
    cryptbase64byte = cryptbase64.encode('utf-8')
    cryptbyte = base64.decodestring(cryptbase64byte)
    with open(prikeyfilepath, 'rb') as prikeyfile:
        prikeydata = prikeyfile.read()
        prikey = rsa.PrivateKey.load_pkcs1(prikeydata)
        contentbyte = rsa.decrypt(cryptbyte, prikey)
        content = contentbyte.decode('utf-8')
        return content


def sign(message, key):
    return digest_sha256(message + key)


def random_salt(length=6):
    salt = ''.join(random.sample(
        ['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g', 'f', 'e',
         'd', 'c', 'b', 'a'], length)).replace(' ', '')
    return salt


def digest_sha256(instr, salt=''):
    if salt == '':
        return hashlib.sha256(instr.encode('utf-8')).hexdigest()
    return hashlib.sha256((salt + '$' + instr).encode('utf-8')).hexdigest()


def otp(otp_key):
    if len(otp_key<50):
        raise Exception('otp key less than 50, may be wrong!')
    