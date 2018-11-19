from hash_utils import hash_string_256, hash_block


class Verification:
    def verify_chain(self, blockchain):
        """ Check if previous_hash value in block dict is equal to hashed version of previous block"""
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            if not self.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work is invalid')
                return False
        return True

    def check_transaction_validity(self, open_transactions, get_balance):
        ''' Check if all transactions are valid '''
        return all([self.verify_tx(tx, get_balance) for tx in open_transactions])

    def verify_tx(self, transaction, get_balance):
        (_, _, sender_balance) = get_balance(transaction.sender)
        return sender_balance >= transaction.amount

    def valid_proof(self, transactions, last_hash, proof):
        guess = (str([tx.to_ordered_dict() for tx in transactions]) +
                 str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        return guess_hash[0:2] == '00'
