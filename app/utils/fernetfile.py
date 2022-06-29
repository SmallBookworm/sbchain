import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


def get_key():
    """
    Generates a key and save it into a file
    """
    return Fernet.generate_key()


def write_key():
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)


def load_key():
    """
    Loads the key from the current directory named `key.key`
    """
    return open("key.key", "rb").read()


def encrypt(filename, key):
    """
    Given a filename (str) and key (bytes), it decrypts the file and write it
    """
    f = Fernet(key)
    with open(filename, "rb") as file:
        # read all file data
        file_data = file.read()
    # encrypt data
    encrypted_data = f.encrypt(file_data)
    # write the encrypted file
    with open(filename, "wb") as file:
        file.write(encrypted_data)


def decrypt(filename, key,output_name=''):
    """
    Given a filename (str) and key (bytes), it decrypts the file and write it
    """
    f = Fernet(key)
    with open(filename, "rb") as file:
        # read the encrypted data
        encrypted_data = file.read()
    # decrypt data
    decrypted_data = f.decrypt(encrypted_data)

    if output_name=='':
        output_name=filename
    # write the original file
    with open(output_name, "wb") as file:
        file.write(decrypted_data)
        os.remove(filename)


def derive_key(password):
    salt = b'\xa78\xaa\xc9\xceg:\xe1\x98\xb5)\x8c\xf5O\x8a\xc8\n\x93\x8e\x83\x00\x8c7\xea\x8d\x83\x1fN\r\x8bs\xfc\xd4\xcc\xa7\xe1l\x91\xe6:\xb0$gn\xc6\xd2\xd0\xb0\xbain\x15"\x01\x17\\\x97\x97Je\x0c(V%Xz\xbf\x88\x12\xae\x83\xe8d\xb25\x12\x92\xd8fk\xf7>\n.o\xad\xeb!\xf5@ (\x13\xa2!NT\x95*W\xa1\xba}`\xaf\x1ckq\xc6}\xfc\x91]\xbf\x04\x95]:\x9d|?[nU/\xf4\x18\xac\xd5\x0c#2ye\xdc7\x9c\n\xfb\xddey\t\xb5j\x1b\xe8];\xbb\x9f\xb6\xd4\xee\x1dP:\xe2\x0e\xad\t\xe0\xa6w\x05\x8av\xcf\xe8\x81\xe2X\xbd\xbfTw\x16!\x82\x02\x16\x8b\xd7@\xdeW-\r\n\xac+\x0cR\xf1\xaa]\x87\xd2\x1cfg\xcag\xeb\x12\xd9\x86\xef\x82\x13\'\x1e\xe7\x94\x14\xd4K\xfb\xe7\x02\x80\x8f]0\xf5\xf1\xca\xa2\t\x1d\x94\x04\xc1cUy\x03u\xeeE\xf84}Emm,\xbd`\x07\toE-\xa3s'
    """Derive the key from the `password` using the passed `salt`"""
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    derived_key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(derived_key)


def encrypt_str(message, key):
    f = Fernet(key)
    return f.encrypt(message.encode())


def decrypt_str(message, key):
    f = Fernet(key)
    return f.decrypt(message.encode())
