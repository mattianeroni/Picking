from __future__ import annotations

"""
This is a web server which emulates a node of the blockchain.

"""


from typing import Dict, List, Optional, Union

import uuid
import json

import flask
from flask import session
from flask_session import Session

from blockchain import Blockchain



# Instantiate our Node
app = flask.Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

# Generate a globally unique address for this node
node_identifier : str = str(uuid.uuid4()).replace('-', '')





@app.route('/init', methods=['GET'])
def init ():
	"""
	Initialize the functioning of the node.
	"""
	session['blockchain'] = Blockchain()
	return flask.jsonify({
            	'message': 'The current chain of this node',
            	'chain': session['blockchain'].chain
        	}), 200





@app.route('/mine', methods=['GET'])
def mine():
	"""
	Forge a new block:
		- The Proof of Work is used to calculate the next proof
		- The last block is hashed
		- The new block is added and returned to the client
	"""

	last_block = session['blockchain'].chain[-1]
	proof : int = session['blockchain'].proof_of_work(last_proof=last_block.get('proof'))
	response = session['blockchain'].new_block(proof)

	return flask.jsonify(response), 200



  
@app.route('/transaction', methods=['POST'])
def transaction():
	"""
	Forge a new transaction:
	:receive the transaction request in json format
	:check that sender, receiver and amount are all given
	:forge the transaction and return a message
	"""

	values : Dict[str, Union[str,int]] = flask.request.get_json() # receive the request in Json format
	print(values)
	# Check that the required fields are in the POSTed data
	if not all(k in values for k in ('sender', 'receiver', 'amount')):
		return 'Missing values', 400

	error, index = session['blockchain'].new_transaction(values['sender'], values['receiver'], values['amount']) # create a new transaction

	if error:
		return 'Sender or Receiver NOT correct', 400

	return flask.jsonify({'message': f'Transaction will be added to Block {index}'}), 201




@app.route('/chain', methods=['GET'])
def chain():
	"""
	Return to the node user a representation of the full blockchain
	"""

	return flask.jsonify({
        	'chain': session['blockchain'].chain,
        	'length': len(session['blockchain'].chain),
        	'total_nodes' : list(session['blockchain'].nodes),
        	'pending_transactions' : session['blockchain'].current_transactions
    	}), 200




@app.route('/node', methods=['POST'])
def register_nodes():
    values = flask.request.get_json()

    if not values.get('nodes'):
        return "Error: Please supply a valid list of nodes", 400

    for node in values.get('nodes'):
        session['blockchain'].register_node(node)

    return flask.jsonify({
        	'message': 'New nodes have been added',
        	'total_nodes': list(session['blockchain'].nodes),
    	}), 201





@app.route('/resolve', methods=['GET'])
def consensus():
    replaced = session['blockchain'].solve_conflicts()

    if replaced:
        return flask.jsonify({
            	'message': 'The chain was replaced',
            	'new_chain': session['blockchain'].chain
        	}), 200
    else:
        return flask.jsonify({
            	'message': 'The chain is authoritative',
            	'chain': session['blockchain'].chain
        	}), 200





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
