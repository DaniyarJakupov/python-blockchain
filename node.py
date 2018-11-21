from uuid import uuid4
from blockchain import Blockchain
from utils.verification import Verification


class Node:
    def __init__(self):
        # self.id = str(uuid4())
        self.id = 'Dan'
        self.blockchain = Blockchain(self.id)

    def listen_for_input(self):
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
            print('==================================')
            user_choice = self.get_user_choice()
            if user_choice == '1':
                tx_data = self.get_transaction_value()  # returns a tuple
                recipient, amount = tx_data
                if self.blockchain.add_transaction(recipient, self.id, amount=amount):
                    print('Added transaction!')
                else:
                    print('Transaction failed!')
            elif user_choice == '2':
                self.blockchain.mine_block()
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == '5':
                (amount_sent, amount_recieved,
                 balance) = self.blockchain.get_balance()
                print(f'{self.id} sent: {amount_sent:.2f}')
                print(f'{self.id} recieved: {amount_recieved:.2f}')
                print(f'Balance of {self.id}: {balance:.2f}')
            elif user_choice == '6':
                print(self.blockchain.get_open_transactions())
            elif user_choice == '7':
                if Verification.check_transaction_validity(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('All transactions are valid')
                else:
                    print('There are invalid transactions!')
            elif user_choice == 'q':
                break
            else:
                print('Input was invalid, please pick a value from the list!')

            if not Verification.verify_chain(self.blockchain.chain):
                print('Invalid blockchain')
                break
        print('Done!')

    def get_transaction_value(self):
        """ Returns a tuple w/ recipient and amount value """
        tx_recipient = input('Enter the recipient: ')
        tx_amount = float(input('Your transaction amount please: '))
        return (tx_recipient, tx_amount)

    def get_user_choice(self):
        user_input = input('Your choice: ')
        return user_input

    def print_blockchain_elements(self):
        # Output the blockchain list to the console
        # for block in self.blockchain.chain:
        #     print('Outputting Block')
        #     print(block)
        print(self.blockchain.chain)


node = Node()
node.listen_for_input()
