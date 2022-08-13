import copy
import math
from operator import truediv
import random
import re
import time
from unittest import result
from block import Block


class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 2

    def __init__(self):
        self.unconfirmed_transactions = []
        self.unconfirmed_timestamp = []
        self.chain = []
        self.votes = {}

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(0, [], 0, "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def vote(self, peers, localhost_url):
        self.votes[localhost_url] = []
        total = math.ceil(len(peers)/2)
        for peer in peers:
            vote = random.randint(0, total)
            self.votes[localhost_url].append({'address': peer, 'votes': vote})
            total -= vote

    def add_block(self, block:Block, proof):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        #remove transactions in block
        for trans in block.transactions:
            if trans['timestamp'] in self.unconfirmed_timestamp:
                index = self.unconfirmed_timestamp.index(trans['timestamp'])
                del self.unconfirmed_timestamp[index]
                del self.unconfirmed_transactions[index]

        block.hash = proof
        self.chain.append(block)
        return True

    @staticmethod
    def proof_of_work(block):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_new_transaction(self, transaction):
        if transaction['timestamp'] in self.unconfirmed_timestamp:
            return False
        else:
            self.unconfirmed_transactions.append(transaction)
            self.unconfirmed_timestamp.append(transaction['timestamp'])
            return True

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=copy.deepcopy(self.unconfirmed_transactions),
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        if self.add_block(new_block, proof):
            return True
        else:
            return False
