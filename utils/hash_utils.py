import hashlib
import json


def hash_string_256(string):
    return hashlib.sha256(string).hexdigest()


def hash_block(block):
    # Convert block object to dictionary for json hashing
    hashable_block = block.__dict__.copy()
    # Convert list of transactions from objects to ordered_dict for json hashing
    hashable_block['transactions'] = [tx.to_ordered_dict()
                                      for tx in hashable_block['transactions']]
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())
