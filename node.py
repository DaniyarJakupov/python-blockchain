from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def get_ui():
    return send_from_directory('frontend', 'node.html')


@app.route('/network', methods=['GET'])
def get_network():
    return send_from_directory('frontend', 'network.html')


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
        blockchain = Blockchain(wallet.public_key, port)
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
        blockchain = Blockchain(wallet.public_key, port)
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


@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key == None:
        response = {
            'message': 'No wallet found!'
        }
        return (jsonify(response), 400)

    params = request.get_json()
    if not params:
        response = {
            'message': 'You have to provide params!'
        }
        return (jsonify(response), 400)

    required_fields = ['recipient', 'amount']
    if not all(field in params for field in required_fields):
        response = {
            'message': 'Required data is missing!'
        }
        return (jsonify(response), 400)

    recipient = params['recipient']
    amount = params['amount']
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    success = blockchain.add_transaction(
        recipient, wallet.public_key, signature, amount)

    if success:
        (_, _, balance) = blockchain.get_balance()
        response = {
            'message': 'Tx was added to open_transactions',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount
            },
            'balance': balance
        }
        return (jsonify(response), 201)
    else:
        response = {
            'message': 'Tx creation failed :('
        }
        return (jsonify(response), 500)


@app.route('/transactions', methods=['GET'])
def get_open_transactions():
    if wallet.public_key == None:
        response = {
            'message': 'No wallet found!'
        }
        return (jsonify(response), 400)
    else:
        response = {
            'open_transactions': [tx.__dict__ for tx in blockchain.get_open_transactions()]
        }
        return (jsonify(response), 200)


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
    (_, _, balance) = blockchain.get_balance()
    if block != None:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]
        response = {
            'message': 'Block mined successfully',
            'block': dict_block,
            'balance': balance
        }
        return (jsonify(response), 200)
    else:
        response = {
            'message': 'Failed to mine a block',
            'wallet_setup': wallet.public_key != None
        }
        return (jsonify(response), 500)


@app.route('/node', methods=["POST"])
def add_node():
    params = request.get_json()
    if not params:
        response = {
            'message': 'Node has to be provided'
        }
        return (jsonify(response), 400)
    if 'node' not in params:
        response = {
            'message': 'Node has to be provided'
        }
        return (jsonify(response), 400)

    node = params['node']
    blockchain.add_peer_node(node)
    response = {
        'message': 'Successfully added a node',
        "all_nodes": blockchain.get_peer_nodes()
    }
    return (jsonify(response), 200)


@app.route('/node/<node_url>', methods=["DELETE"])
def remove_node(node_url):
    if node_url == '' or node_url == None:
        response = {
            'message': 'Node has to be provided'
        }
        return (jsonify(response), 400)

    blockchain.remove_peer_node(node_url)
    response = {
        'message': 'Successfully removed a node',
        "all_nodes": blockchain.get_peer_nodes()
    }
    return (jsonify(response), 200)


@app.route('/nodes', methods=['GET'])
def get_nodes():
    response = {
        "all_nodes": blockchain.get_peer_nodes()
    }
    return (jsonify(response), 200)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key, port)
    app.run(host='0.0.0.0', port=port)
