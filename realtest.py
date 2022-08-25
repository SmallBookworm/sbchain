import weakref
from flask import Flask, request
import requests
from flask_apscheduler import APScheduler
from app.transaction import Transaction

from filechain import Filechain
import logging

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

finish_trans=0
last_num=0

exp_trans = {
    "from_addr": "-----BEGIN PUBLIC KEY-----\r\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwJvUKqGJLyrckZj3EzhO\r\n1SRdCyM+1hKffkQWBT6vsQ54h1+HS4UuBMhWoWTzqUVgk+l1jEx8S9tKxUhdxNRL\r\nZJr7k8X93mNUKdcBSbi3cRBdKgqWjJFru06GGEQpD4uY8c7p6DQhOwuFZQtsW67w\r\naUUQGXZMNQdZj+yykPMkXIXukGASsSex+8TUvDr9u0Xp4vAo2m0IwMifkmS8YCSN\r\neWrra3T5aq2LwyFoQpr9v6/RXvye9/jBi5coVYD3Zjw2vs6lbBvJFqa5eSEi9XzM\r\njKgRyAMnvswAPz+Nz0O7e8b5j2y3mf7erq5wPnhS3dyt+Qkmm6GaWk1He41LaQmB\r\n6QIDAQAB\r\n-----END PUBLIC KEY-----",
    "to_addr": "-----BEGIN PUBLIC KEY-----\r\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwJvUKqGJLyrckZj3EzhO\r\n1SRdCyM+1hKffkQWBT6vsQ54h1+HS4UuBMhWoWTzqUVgk+l1jEx8S9tKxUhdxNRL\r\nZJr7k8X93mNUKdcBSbi3cRBdKgqWjJFru06GGEQpD4uY8c7p6DQhOwuFZQtsW67w\r\naUUQGXZMNQdZj+yykPMkXIXukGASsSex+8TUvDr9u0Xp4vAo2m0IwMifkmS8YCSN\r\neWrra3T5aq2LwyFoQpr9v6/RXvye9/jBi5coVYD3Zjw2vs6lbBvJFqa5eSEi9XzM\r\njKgRyAMnvswAPz+Nz0O7e8b5j2y3mf7erq5wPnhS3dyt+Qkmm6GaWk1He41LaQmB\r\n6QIDAQAB\r\n-----END PUBLIC KEY-----",
    "type": 1,
    "timestamp": 1660820721.2661037,
    "previous_hash": "0",
    "message": "{\"creater\": \"-----BEGIN PUBLIC KEY-----\\r\\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwJvUKqGJLyrckZj3EzhO\\r\\n1SRdCyM+1hKffkQWBT6vsQ54h1+HS4UuBMhWoWTzqUVgk+l1jEx8S9tKxUhdxNRL\\r\\nZJr7k8X93mNUKdcBSbi3cRBdKgqWjJFru06GGEQpD4uY8c7p6DQhOwuFZQtsW67w\\r\\naUUQGXZMNQdZj+yykPMkXIXukGASsSex+8TUvDr9u0Xp4vAo2m0IwMifkmS8YCSN\\r\\neWrra3T5aq2LwyFoQpr9v6/RXvye9/jBi5coVYD3Zjw2vs6lbBvJFqa5eSEi9XzM\\r\\njKgRyAMnvswAPz+Nz0O7e8b5j2y3mf7erq5wPnhS3dyt+Qkmm6GaWk1He41LaQmB\\r\\n6QIDAQAB\\r\\n-----END PUBLIC KEY-----\", \"filename\": \"a_2.txt\", \"key\": \"hO1DJoRN3JSPUOZSarvH3shcbUB4w9/5GFliQRn5NyaeNU2qAWMH/YqgG+zSXrxo2LRgsFQdaZEDEyxUerqQ+Cv760il4FS5YQwnHEZJxmeXx/TglmY7nz5rhAhWWj1n2yvd4AZanpH49EYv+ljg5ZFODtHm5PyUjkg5E/zg8Tlih7CyBbekxgA9WAQSztbEqtNkI/IADI00vnVYrxMTwnHoQ3SfVMQWo0sP902AAq/RHPDnwiocJrJgDVJ2+W3nluvnQeYcxZYvFqvLo4CFbTTnjvGNGi0EcZYx7zL3ojda2QNdmOa+U4Lj13Yheof/TpUkFbBSLTBysTu2D18svg==\", \"hash\": \"QmfWVbdmvbauvLshw6ZUZZS2nGQQ6dx6r5EBTUJcSGrCzn\"}",
    "signature": "DAIX/7gBqUxe5m/eg62eTuQ4lPC/zR4WUCj+PsPL2pYvAtd3drBrx7apkLVBmO9FjxU0lrB2uhcLdIo0rgy1v5qgiJAr1KUBK2UkONFJaxJer91nvYQ3K43NFUM87DbHbu0kxaTlgulgCu6tX/m+nK6u800KtpIR8UfpJEtce4oWqIOJEyl3emW8AdN8T3zLsyIvpSXCf8qWR9pBcHM3fWhhoabykoUBVgt7ER84dcOnBzDfwU5rP4svriieeAGxQ5Cr91uZcqaCaw4Z5abi71KM24bJsKc80LQwSdhJ3EX8fXFXo2HzQ3MSHIA4n3QCYH+yS8tC00K9gSVYS3izlQ==",
    "hash": "55cbbde51c1ef45eff36f5ea0c4cc4e7ad7b723dbc63737189b5fd5bcc69445e"
}

class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': 'realtest:post_reqeust',
            'trigger': 'interval',
            'max_instances': 10,
            'seconds': 1
        }
    ]
    SCHEDULER_API_ENABLED = True

tps=0
def post_reqeust():
    global tps,finish_trans,last_num
    
    tps+=5
    #should create websocket
    url = "http://localhost:8008/new_transaction"
    headers = {'Content-Type': "application/json"}
    requests.post(url,
                  json=exp_trans,
                  headers=headers)



app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

node=Filechain()
pool = []
hash_group = []

@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    global node,finish_trans,tps,last_num
    print("tps: ",tps," speed: ",finish_trans-last_num)
    last_num=finish_trans
    new_txion = request.get_json()
    for i in range(0,tps):
        # verify
        if Transaction.is_valid(new_txion, new_txion['signature'], new_txion['hash']):
            node.add_trans(new_txion)
            # signature
            new_transaction = Transaction(new_txion["from_addr"],
                                          new_txion["to_addr"],
                                          new_txion["previous_hash"],
                                          new_txion["message"],
                                          new_txion["type"],
                                          new_txion["timestamp"])
    
            signature, hash = new_transaction.compute_signature(
                node.private_key)
            finish_trans+=1
    return "",200