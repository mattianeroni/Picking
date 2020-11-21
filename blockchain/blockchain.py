from __future__ import annotations
"""
Example of a block used in this Blockchain:

block = {
    'index': 1,
    'timestamp': 1506057125.900785,
    'transactions': [
        {
            'sender': "8527147fe1f5426f9dd545de4b27ee00",
            'recipient': "a77f5cdfa2934df3954a5c7c7da5df1f",
            'amount': 5,
        }
    ],
    'proof': 324984774000,
    'previous_hash': "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
}
"""


from typing import List, Dict, Tuple, Optional, Any, Set, cast

import time

import hashlib
import json
import uuid
import requests

import urllib.parse as parse





class Blockchain(object):
    def __init__(self):
        self.chain : List[Dict[str, Any]] = []
        self.current_transactions : List[Dict[str, Union[str, int]]] = []
        self.nodes : Set[str] = set()

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)




    def register_node(self, address : str) -> None:
        """
        Add a new node after correctly formatting the address string.
        :param address: Address of node (e.g. 'http://192.168.0.5:5000')
        """

        self.nodes.add(parse.urlparse(address).netloc)




    def valid_chain(self, chain : List[Dict[str, Any]]) -> bool:
        """
        Determine if a blockchain is valid or not.
        Block after block controls the hashing and the proof by using the PoW algorithm.

        :param chain: the chain list of a blockchain
        :return: True if the chain is valid and Flase otherwise
        """


        for cindex in range(1, len(chain)):
            last_block = chain[cindex - 1]
            block = chain[cindex]

            if block.get('previous_hash') != self.hash(last_block) or not self.valid_proof(cast(int, last_block.get('proof')), cast(int, block.get('proof'))):
                return False


        return True




    def solve_conflicts(self) -> bool:
        """
        This is the Consensus Algorithm.

        It checks all neighbourhood of nodes working as a client for other nodes,
        if it finds a chain longer or equally long with more pending transactions, it updates the current 
        chain and pending transactions.

        :return: True if our chain was replaced, False if not.
        """


        updated : bool = False
        neighbours : Set[str] = self.nodes

        clength : int = len(self.chain)
        ctransactions : int = len(self.current_transactions)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                chain, length, transactions = response.json()['chain'], response.json()['length'], len(response.json()['pending_transactions'])

                if (length > clength and self.valid_chain(chain)) or (length == clength and transactions > ctransactions and self.valid_chain(chain)):
                    clength, ctransactions = length, transactions
                    self.chain, self.current_transactions = chain, response.json()['pending_transactions']
                    updated = True

        return updated


        
    def new_block(self, proof : int, previous_hash : Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new Block in the Blockchain
        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """

        block = {
            'index': len(self.chain),
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transactions = []
        self.chain.append(block)
        return block
    


    def new_transaction(self, sender : str, receiver : str, amount : int) -> Tuple[bool, Optional[int]]:
        """
        Creates a new transaction to go into the next mined Block.
        If sender or receiver are note registered nodes it returns an Error, 
        otherwise it returns a false error and the index of the block that will hold the transaction.

        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount

        :return: (Error, BlockIndex)
        """
        if parse.urlparse(sender).netloc in self.nodes and parse.urlparse(receiver).netloc in self.nodes:

            self.current_transactions.append({
                'sender': sender,
                'receiver': receiver,
                'amount': amount,
            })

            return False, self.chain[-1]['index'] + 1
        
        return True, None




    @staticmethod
    def hash(block : Dict[str, Any]) -> str:
        """
        Creates a SHA-256 hash of a Block.
        It uses a crypting algorithm proposed by the National Security Agency
        also used as federal standard by the USA.

        To make this, we firstly make sure the Block dictionary is ordered, or we would have inconsistent hashes

        :param block: Block
        :return: The SHA-256 string
        """

        block_string : bytes = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()






    def proof_of_work(self, last_proof : int) -> int:
        """
        Simple Proof of Work Algorithm for hashing:
            It must be fast and easy to implement, but difficult to decrypt.
            It basically increases the proof until the hashing of f'{last_proof}{proof}' ends with some specified numbers.

        :param last_proof: the proof of the last block
        :return: the proof of the current block
        """

        proof : int = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof



    @staticmethod
    def valid_proof (last_proof : int, proof : int) -> bool:
        """
        This defines the difficulty of our PoW algorithm. Here we define how to crypt with hashing.
        """
        return hashlib.sha256(f'{last_proof}{proof}'.encode()).hexdigest()[-1] == "4"


