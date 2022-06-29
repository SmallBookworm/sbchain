from hashlib import sha256
import json
from time import time

from app.utils import myedsa


class Transaction(object):
    def __init__(self, from_addr, to_addr, previous_hash, message, amount=0) -> None:
        """
        Constructor for the `Block` class.
        :param from_addr:         publick key of sender.
        :param to_addr:  publick key of reciver.
        :param amount:     amount of money(file).
        :param previous_hash: Hash of the previous transaction.                                        
        """

        self.from_addr = from_addr
        self.to_addr = to_addr
        self.previous_hash = previous_hash
        self.message = message
        self.amount = amount

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
        signature = myedsa.sign_ECDSA_msg(private_key, hash).decode()
        return signature, hash

    @staticmethod
    def is_valid(transaction, signature, hash):
        """
        Check if transaction is valid.
        """
        atrans = Transaction(transaction["from_addr"],
                             transaction["to_addr"],
                             transaction["previous_hash"],
                             transaction["message"],
                             transaction["amount"])

        return hash == atrans.compute_hash() and myedsa.validate_signature(transaction["from_addr"], signature, hash)
