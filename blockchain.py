import functools
import hashlib
from hash_utils import hash_string_256, hash_block
import json
import os.path
import pickle

from block import Block
from transaction import Transaction
from verification import Verification

# Initializing blockchain list
blockchain = []  # list of blocks
open_transactions = []  # list of unhandled transactions
owner = 'Dan'
participants = {'Dan'}  # set of participants (only unique values)\

# The reward we give to miners (for creating a new block)
MINING_REWARD = 10


def file_exists(path):
    return os.path.isfile(path)


def load_data():
    global blockchain
    global open_transactions
    try:
        with open('blockchain.txt', mode='rb') as f:
            file_content = pickle.loads(f.read())
            blockchain = file_content['chain']
            open_transactions = file_content['ot']
    except IOError:
        print('File not found')
        # Starting block for the blockchain
        genesis_block = Block(0, '', [], 100, 0)
        blockchain.append(genesis_block)


load_data()


def save_data():
    try:
        # Use pickle lib to store data in a binary format
        with open('blockchain.txt', mode='wb') as file:
            save_data = {
                'chain': blockchain,
                'ot': open_transactions
            }
            file.write(pickle.dumps(save_data))
    except IOError:
        print('Saving failed')


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    ver = Verification()
    while not ver.valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def get_balance(participant):
    # list comprehension
    # get the list with amount of coins sent
    tx_sender = [[tx.amount for tx in block.transactions if participant == tx.sender]
                 for block in blockchain]
    open_tx_sender = [tx.amount
                      for tx in open_transactions if tx.sender == participant]
    tx_sender.append(open_tx_sender)
    # Calc total amount sent with reduce func
    amount_sent = functools.reduce(
        lambda tx_sum, tx_amount: tx_sum + sum(tx_amount) if len(tx_amount) > 0 else tx_sum + 0, tx_sender, 0)
    # get the list with amount of coins recieved
    tx_recipient = [[tx.amount for tx in block.transactions if participant == tx.recipient]
                    for block in blockchain]
    # Calc total amount recieved with reduce func
    amount_recieved = functools.reduce(
        lambda tx_sum, tx_amount: tx_sum + sum(tx_amount) if len(tx_amount) > 0 else tx_sum + 0, tx_recipient, 0)

    balance = amount_recieved - amount_sent
    return (amount_sent, amount_recieved, balance)


def get_last_blockchain_value():
    """ Returns the last value of the current blockchain. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def add_transaction(recipient, amount=1.0, sender=owner):
    """
    Arguments:
        :sender: sender of the coins.
        :recipient: reciever of the coins
        :amount: amount of coins sent with the transaction
    """
    # transaction = {
    #     "sender": sender,
    #     "recipient": recipient,
    #     "amount": amount
    # }
    transaction = Transaction(sender, recipient, amount)

    ver = Verification()

    if ver.verify_tx(transaction, get_balance):
        open_transactions.append(transaction)
        save_data()
        return True
    return False


def mine_block():
    last_block = blockchain[-1]  # get last_block from blockchain list
    # use list comprehention to loop over keys in last_block dict
    # and create a new list w/ values from last_block dict
    # then convert it to string
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    reward_tx = Transaction('MINING', owner, MINING_REWARD)

    # Copy trans. instead of mutating original open_tx.
    copied_open_transactions = open_transactions[:]
    copied_open_transactions.append(reward_tx)

    # Create a block object
    block = Block(len(blockchain),  hashed_block,
                  copied_open_transactions, proof)
    # Add newly created block to blockchain
    blockchain.append(block)
    return True


def get_transaction_value():
    """ Returns a tuple w/ recipient and amount value """
    tx_recipient = input('Enter the recipient: ')
    tx_amount = float(input('Your transaction amount please: '))
    return (tx_recipient, tx_amount)


def get_user_choice():
    user_input = input('Your choice: ')
    return user_input


def print_blockchain_elements():
    # Output the blockchain list to the console
    # for block in blockchain:
    #     print('Outputting Block')
    #     print(block)
    print(blockchain)


while True:
    print('==================================')
    print('Please choose')
    print('1: Add a new transaction')
    print('2: Mine new block')
    print('3: Show blockchain')
    print('5: Show balance')
    print('6: Show open transactions')
    print('7: Check transaction validity')
    print('q: Quit')
    ver = Verification()
    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()  # returns a tuple
        recipient, amount = tx_data
        if add_transaction(recipient, amount=amount):
            print('Added transaction!')
        else:
            print('Transaction failed!')
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '5':
        (amount_sent, amount_recieved, balance) = get_balance(owner)
        print(f'{owner} sent: {amount_sent:.2f}')
        print(f'{owner} recieved: {amount_recieved:.2f}')
        print(f'Balance of {owner}: {balance:.2f}')
    elif user_choice == '6':
        print(open_transactions)
    elif user_choice == '7':
        if ver.check_transaction_validity(open_transactions, get_balance):
            print('All transactions are valid')
        else:
            print('There are invalid transactions!')
    elif user_choice == 'q':
        break
    else:
        print('Input was invalid, please pick a value from the list!')

    if not ver.verify_chain(blockchain):
        print('Invalid blockchain')
        break

print('Done!')
