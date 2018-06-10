"""
Blockchain with ability to create new blocks and transactions
"""

import hashlib
import json
from time import time
from uuid import uuid4

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        
        # Create initial block
        self.new_block(previous_hash=1, proof=100)

    """
    Create new block in the blockchain
    Returns: New block as a dictionary
    """
    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain + 1),
            'timestamp': time,
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        # Reset the transaction list
        self.current_transactions = []
        # Add the new block to the blockchain
        self.chain.append(block) 
        
        return block

    """
    Create new transaction for the next mined block
    Returns: Index of the transaction block
    """
    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.last_block['index'] + 1

    """
    Proof of Work implementation to mine new blocks
    Returns: Proof integer
    Algorithm: Find p' such that hash(pp') contains 4 leading zeros,
                where p is the previous proof
    """
    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        
        return proof
    
    """
    Create a SHA-256 hash of a Block
    """
    @staticmethod
    def hash(block):
        # Ensure the dictionary is ordered
        block_string = json.dumps(block, sort_keys=True).encode()
        # Create the new hash
        return hashlib.sha256(block_string).hexdigest()

    """
    Validate a proof if the hash contains 4 leading zeros
    Return: Boolean validation
    """
    @staticmethod
    def valid_proof(last_proof, proof):
        guess_string = last_proof + proof
        guess = guess_string.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return gues_hash[:4] == '0000'

    """
    Return the last block in the blockchain
    """
    @property
    def last_block(self):
        return self.chain[-1]
