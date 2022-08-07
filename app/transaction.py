from datetime import MAXYEAR
from hashlib import sha256
import json
import time

from app.utils import myecdsa, myrsa


class Transaction(object):
    def __init__(self, from_addr, to_addr, previous_hash, message, type=0, timestamp=time.time()) -> None:
        """
        Constructor for the `Block` class.
        :param from_addr:         publick key of sender.
        :param to_addr:  publick key of reciver.
        :param type:     type of transaction: 0、1:file;4:mp4;8:vote.
        :param previous_hash: Hash of the previous transaction.                                        
        """

        self.from_addr = from_addr
        self.to_addr = to_addr
        self.previous_hash = previous_hash
        self.message = message
        self.type = type
        self.timestamp = timestamp

    def compute_hash(self):
        """
        A function that return the hash and signature of the transaction contents.

        return
        hash:transaction info hash.
        """
        transaction_string = json.dumps(self.__dict__, sort_keys=True)
        hash = sha256(transaction_string.encode()).hexdigest()

        return hash

    def compute_signature(self, private_key):
        """
        A function that return the hash and signature of the transaction contents.

        return
        signature: base64 (to make it shorter),sign hash.
        hash:transaction info hash.
        """

        hash = self.compute_hash()
        signature = myrsa.sign_msg(hash, private_key).decode()
        return signature, hash

    def compute_ECDSA_signature(self, private_key):
        hash = self.compute_hash()
        signature = myecdsa.sign_ECDSA_msg(private_key, hash).decode()
        return signature, hash

    @staticmethod
    def get_dict(new_transaction, signature, hash):
        return {'from_addr': new_transaction.from_addr,
                'to_addr': new_transaction.to_addr,
                'type': new_transaction.type,
                'timestamp': new_transaction.timestamp,
                'previous_hash': new_transaction.previous_hash,
                "message": new_transaction.message,
                "signature": signature,
                "hash": hash}

    @classmethod
    def create_from_dict(cls, trans_data):
        return cls(trans_data["from_addr"],
                   trans_data["to_addr"],
                   trans_data["previous_hash"],
                   trans_data["message"],
                   trans_data["type"],
                   trans_data["timestamp"])

    @classmethod
    def is_valid(cls,transaction, signature, hash):
        """
        Check if transaction is valid.
        """
        atrans = cls.create_from_dict(transaction)

        publick_key = myrsa.load_str_publick_key(transaction["from_addr"])

        return hash == atrans.compute_hash() and myrsa.validate_signature(publick_key, signature, hash)
