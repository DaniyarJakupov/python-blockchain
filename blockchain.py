import functools
import hashlib
import json
from collections import OrderedDict
# Initializing blockchain list
blockchain = []  # list of blocks
genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions': [],
    'proof': 100
}
blockchain.append(genesis_block)
open_transactions = []  # list of open transactions
owner = 'Dan'
participants = {'Dan'}  # set of participants (only unique values)
MINING_REWARD = 10


def hash_block(block):
    return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()


def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[0:2] == '00'


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def get_balance(participant):
    # list comprehension
    # get the list with amount of coins sent
    tx_sender = [[tx['amount'] for tx in block['transactions'] if participant == tx['sender']]
                 for block in blockchain]
    open_tx_sender = [tx['amount']
                      for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    # Calc total amount sent with reduce func
    amount_sent = functools.reduce(
        lambda tx_sum, tx_amount: tx_sum + sum(tx_amount) if len(tx_amount) > 0 else tx_sum + 0, tx_sender, 0)
    # get the list with amount of coins recieved
    tx_recipient = [[tx['amount'] for tx in block['transactions'] if participant == tx['recipient']]
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
    transaction = OrderedDict([
        ("sender", sender), ("recipient", recipient), ("amount", amount)
    ])
    if verify_tx(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        return True
    return False


def verify_tx(transaction):
    (_, _, sender_balance) = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def mine_block():
    last_block = blockchain[-1]  # get last_block from blockchain list
    # use list comprehention to loop over keys in last_block dict
    # and create a new list w/ values from lsat_block dict
    # then convert it to string
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    reward_tx = OrderedDict([
        ("sender", "MINING"), ("recipient", owner), ("amount", MINING_REWARD)
    ])
    # Copy trans. instead of mutating original open_tx.
    copied_open_transactions = open_transactions[:]
    copied_open_transactions.append(reward_tx)

    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_open_transactions,
        'proof': proof
    }
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


def verify_chain():
    """ Check if previous_hash value in block dict is equal to hashed version of previous block"""
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print('Proof of work is invalid')
            return False
    return True


def check_transaction_validity():
    ''' Check if all transactions are valid '''
    return all([verify_tx(tx) for tx in open_transactions])


while True:
    print('==================================')
    print('Please choose')
    print('1: Add a new transaction')
    print('2: Mine new block')
    print('3: Show blockchain')
    print('4: Show participants')
    print('5: Show balance')
    print('6: Show open transactions')
    print('7: Check transaction validity')
    print('h: Manipulate the chain')
    print('q: Quit')

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
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        (amount_sent, amount_recieved, balance) = get_balance(owner)
        print(f'{owner} sent: {amount_sent:.2f}')
        print(f'{owner} recieved: {amount_recieved:.2f}')
        print(f'Balance of {owner}: {balance:.2f}')
    elif user_choice == '6':
        print(open_transactions)
    elif user_choice == '7':
        if check_transaction_validity():
            print('All transactions are valid')
        else:
            print('There are invalid transactions!')
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{'sender': 'Max', 'recipient': owner, 'amount': 1000}]
            }
    elif user_choice == 'q':
        break
    else:
        print('Input was invalid, please pick a value from the list!')

    if not verify_chain():
        print('Invalid blockchain')
        break

print('Done!')
