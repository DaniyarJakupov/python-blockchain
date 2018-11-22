from utils.hash_utils import hash_string_256, hash_block
from wallet import Wallet


class Verification:
    @classmethod
    def verify_chain(cls, blockchain):
        """ Check if previous_hash value in block dict is equal to hashed version of previous block"""
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work is invalid')
                return False
        return True

    @classmethod
    def check_transaction_validity(cls, open_transactions, get_balance):
        ''' Check if all transactions are valid '''
        return all([cls.verify_tx(tx, get_balance, False) for tx in open_transactions])

    @staticmethod
    def verify_tx(transaction, get_balance, check_funds=True):
        if check_funds:
            (_, _, sender_balance) = get_balance()
            return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)
        else:
            return Wallet.verify_transaction(transaction)

    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        guess = (str([tx.to_ordered_dict() for tx in transactions]) +
                 str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        return guess_hash[0:2] == '00'
