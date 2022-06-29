from hashlib import sha256
import json
from time import time


class Block(object):
    def __init__(self,index,transactions,timestamp,previous_hash, nonce=0) -> None:
        """
        Constructor for the `Block` class.
        :param index:         Unique ID of the block.
        :param transactions:  List of transactions.
        :param timestamp:     Time of generation of the block.
        :param previous_hash: Hash of the previous block in the chain which this block is part of.                                        
        """
        self.nonce=nonce
        self.index=index
        self.transactions=transactions
        self.timestamp=timestamp
        self.previous_hash=previous_hash

    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()
