# Initializing blockchain list
blockchain = []  # list of blocks
genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions': []
}
blockchain.append(genesis_block)
open_transactions = []  # list of open transactions
owner = 'Dan'
participants = {'Dan'}  # set of participants (only unique values)


def hash_block(block):
    return '-'.join([str(block[key]) for key in block])


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
    transaction = {
        "sender": sender,
        "recipient": recipient,
        "amount": amount
    }
    open_transactions.append(transaction)
    participants.add(sender)
    participants.add(recipient)


def mine_block():
    last_block = blockchain[-1]  # get last_block from blockchain list
    # use list comprehention to loop over keys in last_block dict
    # and create a new list w/ values from lsat_block dict
    # then convert it to string
    hashed_block = hash_block(last_block)
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': open_transactions
    }
    blockchain.append(block)


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
    return True


while True:
    print('Please choose')
    print('1: Add a new transaction')
    print('2: Mine new block')
    print('3: Show blockchain')
    print('4: Show participants')
    print('h: Manipulate the chain')
    print('q: Quit')
    print('==================================')
    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()  # returns a tuple
        recipient, amount = tx_data
        add_transaction(recipient, amount=amount)
        print(open_transactions)
    elif user_choice == '2':
        mine_block()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
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
