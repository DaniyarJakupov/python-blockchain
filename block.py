from time import time


class Block():
    def __init__(self, index, previous_hash, transactions, proof, time=time()):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.proof = proof
        self.timestamp = time

    def __repr__(self):
        return f'Index: {self.index}, Transactions: {self.transactions}, Previous Hash: {self.previous_hash}, Proof: {self.proof} \n'
