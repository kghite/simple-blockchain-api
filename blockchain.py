"""
Blockchain with ability to create new blocks and transactions
"""

import hashlib
import json
import requests
from time import time
from uuid import uuid4
from urlparse import urlparse

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set() # Use a set to prevent duplicate nodes

        # Create initial block
        self.new_block(previous_hash=1, proof=100)

    """
    Create new block in the blockchain
    Returns: New block as a dictionary
    """
    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
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
    Add a new node to the node list
    """
    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    """
    Check the validity of a given blockchain
    Returns: Boolean validity
    """
    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    """
    Replace chain with longest network chain to keep consensus
    Returns: True if chain was replaced
    """
    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        # Verify all network chains
        for node in neighbours:
            request_string = 'http://' + str(node) + '/chain'
            response = requests.get(request_string)

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check length and validity
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace chain if found longer
        if new_chain:
            self.chain = new_chain
            return True

        return False
    
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
        guess_string = str(last_proof) + str(proof)
        guess = guess_string.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:4] == '0000'

    """
    Return the last block in the blockchain
    """
    @property
    def last_block(self):
        return self.chain[-1]


if __name__ == '__main__':
    # Test the blockchain methods
    b = Blockchain()

    transaction =  b.new_transaction(
        sender = '0',
        recipient = '0',
        amount = 1)
    print transaction

    last_block = b.last_block
    last_proof = last_block['proof']
    proof = b.proof_of_work(last_proof)

    previous_hash = b.hash(last_block)
    block = b.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    print response
