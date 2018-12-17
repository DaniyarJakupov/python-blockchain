import functools
import hashlib
import json
import os.path
import pickle

from block import Block
from transaction import Transaction
from utils.verification import Verification
from utils.hash_utils import hash_string_256, hash_block
from wallet import Wallet

# The reward we give to miners (for creating a new block)
MINING_REWARD = 10


def file_exists(path):
    return os.path.isfile(path)


class Blockchain:
    # Initializing blockchain list
    def __init__(self, public_key, node_id):
        genesis_block = Block(0, '', [], 100, 0)  # Starting block
        self.chain = [genesis_block]  # list of blocks
        self.__open_transactions = []  # list of unhandled transactions
        self.public_key = public_key
        self.__peer_nodes = set()
        self.node_id = node_id
        self.load_data()

    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='rb') as f:
                file_content = pickle.loads(f.read())
                self.chain = file_content['chain']
                self.__open_transactions = file_content['ot']
                self.__peer_nodes = file_content['peer_nodes']
        except IOError:
            print('File not found')

    def save_data(self):
        try:
            # Use pickle lib to store data in a binary format
            with open('blockchain-{}.txt'.format(self.node_id), mode='wb') as file:
                save_data = {
                    'chain': self.__chain,
                    'ot': self.__open_transactions,
                    "peer_nodes": self.__peer_nodes
                }
                file.write(pickle.dumps(save_data))
        except IOError:
            print('Saving failed')

    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self):
        if self.public_key == None:
            return None
        participant = self.public_key
        # list comprehension
        # get the list with amount of coins sent
        tx_sender = [[tx.amount for tx in block.transactions if participant == tx.sender]
                     for block in self.__chain]
        open_tx_sender = [tx.amount
                          for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        # Calc total amount sent with reduce func
        amount_sent = functools.reduce(
            lambda tx_sum, tx_amount: tx_sum + sum(tx_amount) if len(tx_amount) > 0 else tx_sum + 0, tx_sender, 0)
        # get the list with amount of coins recieved
        tx_recipient = [[tx.amount for tx in block.transactions if participant == tx.recipient]
                        for block in self.__chain]
        # Calc total amount recieved with reduce func
        amount_recieved = functools.reduce(
            lambda tx_sum, tx_amount: tx_sum + sum(tx_amount) if len(tx_amount) > 0 else tx_sum + 0, tx_recipient, 0)

        balance = amount_recieved - amount_sent
        return (amount_sent, amount_recieved, balance)

    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchain. """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def add_transaction(self, recipient, sender, signature, amount=1.0):
        if self.public_key == None:
            return False

        transaction = Transaction(sender, recipient, signature, amount)

        if Verification.verify_tx(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        if self.public_key == None:
            return None
        last_block = self.__chain[-1]  # get last_block from blockchain list
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        reward_tx = Transaction(
            'MINING', self.public_key, '',  MINING_REWARD)

        # Copy trans. instead of mutating original open_tx.
        copied_open_transactions = self.__open_transactions[:]

        # Verify each transaction in block
        for tx in copied_open_transactions:
            if not Wallet.verify_transaction(tx):
                return None

        # Add reward transaction
        copied_open_transactions.append(reward_tx)

        # Create a block object
        block = Block(len(self.__chain),  hashed_block,
                      copied_open_transactions, proof)

        # Add newly created block to blockchain
        self.__chain.append(block)

        self.__open_transactions = []
        self.save_data()
        return block

    def add_peer_node(self, node):
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        self.__peer_nodes.discard(node)
        self.save_data()

    def get_peer_nodes(self):
        return list(self.__peer_nodes)
