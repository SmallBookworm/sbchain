import base64
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.types import (
    PRIVATE_KEY_TYPES,
    PUBLIC_KEY_TYPES,
)
from cryptography.exceptions import InvalidSignature


def generate_RSA_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    private_key.public_key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key = private_key.public_key()
    publick_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open("private_key.pem", "wb") as f:
        f.write(private_pem)
    with open("publick_key.pem", "wb") as f:
        f.write(publick_pem)

def load_str_private_key(key:str):
        return serialization.load_pem_private_key(
            key.encode(),
            password=None,
        )

def load_str_publick_key(key:str):
        return serialization.load_pem_public_key(
            key.encode()
        )

def load_private_key(path="private_key.pem"):
    with open(path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )
        return private_key


def load_publick_key(path="publick_key.pem"):
    with open(path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
        )
        return public_key


def encrypt(message: str, public_key: PUBLIC_KEY_TYPES):
    """message: str

    return
    ciphertext: base64 (to make it shorter)
    """

    # message is a string and encode it to bytes(utf-8)
    bmessage = message.encode()

    ciphertext = public_key.encrypt(
        bmessage,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(ciphertext)


def decrypt(message: str, private_key: PRIVATE_KEY_TYPES):
    """message: str

    return
    plaintext: str(utf-8)

    """
    try:
        plaintext = private_key.decrypt(
            base64.b64decode(message),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext.decode()
    except Exception as e:
        return False


def sign_msg(message: str, private_key: PRIVATE_KEY_TYPES):
    signature = private_key.sign(
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature)


def validate_signature(public_key: PUBLIC_KEY_TYPES, signature: str, message: str):

    # convert it into bytes (utf-8)
    signature = base64.b64decode(signature)
    try:
        public_key.verify(
            signature,
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except InvalidSignature:
        return False
    return True
