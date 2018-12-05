from flask import Flask, jsonify
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
CORS(app)

wallet = Wallet()
blockchain = Blockchain(wallet.public_key)


@app.route('/', methods=['GET'])
def get_ui():
    return 'Welcome to pycoin!'


@app.route('/balance', methods=['GET'])
def get_balance():
    if blockchain.get_balance() != None:
        (amount_sent, amount_recieved, balance) = blockchain.get_balance()
        response = {
            'sent': f'{amount_sent:.2f}',
            'recieved': f'{amount_recieved: .2f}',
            'total':  f'{balance:.2f}'
        }
        return (jsonify(response), 200)
    else:
        response = {
            'message': 'Cound not get the balance',
            'wallet_setup': wallet.public_key != None
        }
        return (jsonify(response), 500)


@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key
        }
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        return (jsonify(response), 200)
    else:
        response = {
            'message': 'Cound not save the keys'
        }
        return (jsonify(response), 500)


@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        (_, _, balance) = blockchain.get_balance()
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'balance':  balance
        }
        return (jsonify(response), 200)
    else:
        response = {
            'message': 'Wallet loading failed!'
        }
        return (jsonify(response), 500)


@app.route('/chain', methods=['GET'])
def get_chain():
    chain = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain]
    for dict_block in dict_chain:
        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]

    return (jsonify(dict_chain), 200)


@app.route('/mine', methods=['POST'])
def mine():
    block = blockchain.mine_block()
    if block != None:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]
        response = {
            'message': 'Block mined successfully',
            'block': dict_block
        }
        return (jsonify(response), 200)
    else:
        response = {
            'message': 'Failed to mine a block',
            'wallet_setup': wallet.public_key != None
        }
        return (jsonify(response), 500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
