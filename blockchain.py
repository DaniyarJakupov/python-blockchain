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
MINIGN_REWARD = 10


def hash_block(block):
    return '-'.join([str(block[key]) for key in block])  # list comprehension


def get_balance(participant):
    # get the list with amount of coins sent
    tx_sender = [[tx['amount'] for tx in block['transactions'] if participant == tx['sender']]
                 for block in blockchain]
    open_tx_sender = [tx['amount']
                      for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = 0
    for tx in tx_sender:
        if len(tx) > 0:
            amount_sent += tx[0]
    # get the list with amount of coins recieved
    tx_recipient = [[tx['amount'] for tx in block['transactions'] if participant == tx['recipient']]
                    for block in blockchain]
    amount_recieved = 0
    for tx in tx_recipient:
        if len(tx) > 0:
            amount_recieved += tx[0]

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
    transaction = {
        "sender": sender,
        "recipient": recipient,
        "amount": amount
    }
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
    reward_tx = {
        'sender': "MINING",
        'recipient': owner,
        'amount': MINIGN_REWARD
    }
    copied_open_transactions = open_transactions[:]
    copied_open_transactions.append(reward_tx)

    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_open_transactions
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
        print('Amount sent: ' + str(amount_sent))
        print('Amount recieved: ' + str(amount_recieved))
        print('Balance: ' + str(balance))
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
