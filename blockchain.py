import functools
import hashlib
from hash_utils import hash_string_256, hash_block
import json
import os.path
import pickle

from block import Block
from transaction import Transaction
from verification import Verification

# The reward we give to miners (for creating a new block)
MINING_REWARD = 10


def file_exists(path):
    return os.path.isfile(path)


class Blockchain:
    # Initializing blockchain list
    def __init__(self, hosting_node_id):
        genesis_block = Block(0, '', [], 100, 0)  # Starting block
        self.chain = [genesis_block]  # list of blocks
        self.open_transactions = []  # list of unhandled transactions
        self.hosting_node = hosting_node_id
        self.load_data()

    def load_data(self):
        try:
            with open('blockchain.txt', mode='rb') as f:
                file_content = pickle.loads(f.read())
                self.chain = file_content['chain']
                self.open_transactions = file_content['ot']
        except IOError:
            print('File not found')

    def save_data(self):
        try:
            # Use pickle lib to store data in a binary format
            with open('blockchain.txt', mode='wb') as file:
                save_data = {
                    'chain': self.chain,
                    'ot': self.open_transactions
                }
                file.write(pickle.dumps(save_data))
        except IOError:
            print('Saving failed')

    def proof_of_work(self):
        last_block = self.chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self):
        participant = self.hosting_node
        # list comprehension
        # get the list with amount of coins sent
        tx_sender = [[tx.amount for tx in block.transactions if participant == tx.sender]
                     for block in self.chain]
        open_tx_sender = [tx.amount
                          for tx in self.open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        # Calc total amount sent with reduce func
        amount_sent = functools.reduce(
            lambda tx_sum, tx_amount: tx_sum + sum(tx_amount) if len(tx_amount) > 0 else tx_sum + 0, tx_sender, 0)
        # get the list with amount of coins recieved
        tx_recipient = [[tx.amount for tx in block.transactions if participant == tx.recipient]
                        for block in self.chain]
        # Calc total amount recieved with reduce func
        amount_recieved = functools.reduce(
            lambda tx_sum, tx_amount: tx_sum + sum(tx_amount) if len(tx_amount) > 0 else tx_sum + 0, tx_recipient, 0)

        balance = amount_recieved - amount_sent
        return (amount_sent, amount_recieved, balance)

    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchain. """
        if len(self.chain) < 1:
            return None
        return self.chain[-1]

    def add_transaction(self, recipient, sender, amount=1.0):
        # transaction = {
        #     "sender": sender,
        #     "recipient": recipient,
        #     "amount": amount
        # }
        transaction = Transaction(sender, recipient, amount)
        if Verification.verify_tx(transaction, self.get_balance):
            self.open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        last_block = self.chain[-1]  # get last_block from blockchain list
        # use list comprehention to loop over keys in last_block dict
        # and create a new list w/ values from last_block dict
        # then convert it to string
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        reward_tx = Transaction('MINING', self.hosting_node, MINING_REWARD)

        # Copy trans. instead of mutating original open_tx.
        copied_open_transactions = self.open_transactions[:]
        copied_open_transactions.append(reward_tx)

        # Create a block object
        block = Block(len(self.chain),  hashed_block,
                      copied_open_transactions, proof)
        # Add newly created block to blockchain
        self.chain.append(block)

        self.open_transactions = []
        self.save_data()
        return True
