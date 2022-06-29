from fractions import Fraction
import sys
from turtle import pos
from app.transaction import Transaction

from app.utils import fernetfile, myedsa

import datetime
import json
import os

import requests
from flask import flash, render_template, redirect, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from app import app
from app.utils.ipfs import ipfs_add, ipfs_get


# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []


def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["block_index"] = block["index"]
                tx["block_hash"] = block["hash"]
                tx["block_timestamp"] = block["timestamp"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['block_timestamp'],
                       reverse=True)


@app.route('/')
def index():
    fetch_posts()
    return render_template('index.html',
                           title='YourNet: Decentralized '
                                 'content sharing',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/register_with', methods=['GET'])
def register_with():
    """
    Endpoint to register_with.
    """

    post_object = {
        'node_address': "http://127.0.0.1:8001",
    }

    # Submit a transaction
    new_tx_address = "{}/register_with".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')


client_private_key = "4c18327e973d0f2a65bcbd297965faa1f406363c76836af55ed9e2390cd9bc16"
client_address = "so83hSljI5PBSzknTR5ChOixY/9nLKgIF6bdFgpnzmfhWSS5hUHMtqHveq80a7omwKZK2HMjDYnT4GttsZAf+w=="
# For fast debugging REMOVE LATER
private_key = "181f2448fa4636315032e15bb9cbc3053e10ed062ab0b2680a37cd8cb51f53f2"

addr_from = "SD5IZAuFixM3PTmkm5ShvLm1tbDNOmVlG7tg6F5r7VHxPNWkNKbzZfa+JdKmfBAIhWs9UKnQLOOL1U+R3WxcsQ=="


@app.route('/submit', methods=['POST'])
def submit_file():
    """
    Endpoint to create a new transaction via our application.
    """
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
    if file:
        addr = request.form["addr"]
        filename = secure_filename(file.filename)

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        key = fernetfile.get_key()
        fernetfile.encrypt(filepath, key)
        file_hash = ipfs_add(filepath)
        #debug
        #file_hash = filepath

        info = {'creater': addr_from,
                'filename': filename, 'key': key.decode(), 'hash': file_hash}

        # encrypt file by client
        message_password = fernetfile.derive_key(client_private_key)
        ecmessage = fernetfile.encrypt_str(
            json.dumps(info), message_password).decode()

        new_transaction = Transaction(addr_from, addr_from, "0", ecmessage, 1)
        signature, hash = new_transaction.compute_signature(private_key)

        # Submit a transaction
        response = post_transaction(new_transaction, signature, hash)

        return redirect(url_for('uploaded_file', result=response.content,
                                info=info))

    return redirect('/')


def post_transaction(new_transaction, signature, hash):
    post_object = {'from_addr': new_transaction.from_addr,
                   'to_addr': new_transaction.to_addr,
                   'amount': new_transaction.amount,
                   'previous_hash': new_transaction.previous_hash,
                   "message": new_transaction.message,
                   "signature": signature,
                   "hash": hash}
    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    return requests.post(new_tx_address,
                         json=post_object,
                         headers={'Content-type': 'application/json'})


@app.route('/uploads/<result>/<info>')
def uploaded_file(result, info):
    return "{}.<br>File info: {}".format(result, info)


def transaction(trans_data):
    previous_transaction = Transaction(trans_data["from_addr"],
                                       trans_data["to_addr"],
                                       trans_data["previous_hash"],
                                       trans_data["message"],
                                       trans_data["amount"])
    try:
        if Transaction.is_valid(trans_data, trans_data['signature'], trans_data['hash']):
           # 私钥验证交给区块链进行
            if trans_data["private_key"]:
                new_transaction = Transaction(previous_transaction.to_addr,
                                              trans_data["new_addr"],
                                              trans_data["hash"],
                                              previous_transaction.message,
                                              previous_transaction.amount)
                signature, hash = new_transaction.compute_signature(
                    trans_data["private_key"])

                # Submit a transaction
                response = post_transaction(new_transaction, signature, hash)
                if response.status_code == 201:
                    return "Success.Transaction info: {}".format(hash), 201

        return 'The file do not belong to you.', 400
    except:
        return 'The file do not belong to you.', 400


@app.route('/download_file/', methods=['POST'])
def download():
    trans_data = request.get_json()

    try:
        response_text, status_code = transaction(trans_data)
        if status_code == 201:
            message_password = fernetfile.derive_key(client_private_key)
            messagejson = fernetfile.decrypt_str(
                trans_data["message"], message_password).decode()
            post = json.loads(messagejson)
            download_path=app.config['DOWNLOAD_FOLDER']
            ipfs_get(post['hash'],download_path)
            filepath = os.path.join(download_path, post['hash'])
            output_path= os.path.join(download_path, post['filename'])
            fernetfile.decrypt(filepath, post['key'],output_path)
            return "{}<br>File info: {}".format(response_text, post)
        else:
            return response_text, status_code
    except:
        return 'Something error.', 400


@app.route('/transaction_file/', methods=['POST'])
def transaction_file():
    trans_data = request.get_json()
    return transaction(trans_data)


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
