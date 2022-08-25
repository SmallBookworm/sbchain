import json
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


class Fileblock:
    def __init__(self, trans_data):
        self.file = trans_data["message"]
        self.users = []
        user = self.new_user(trans_data)
        self.users.append(user)

    def new_user(self, trans_data):
        # someone create file
        if len(self.users) == 0 and trans_data["to_addr"] == trans_data["from_addr"]:
            return {"addr": trans_data["to_addr"],
                    "from_user": trans_data["from_addr"],
                    "transactions": [trans_data]}
        else:
            for user in self.users:
                if user["addr"] == trans_data["from_addr"]:
                    return {"addr": trans_data["to_addr"],
                            "from_user": user,
                            "transactions": [trans_data]}
        raise Exception("Error transaction")

    def add_trans(self, trans_data):
        user_added=False
        for user in self.users:
            if user['addr'] == trans_data["to_addr"] or \
            user['addr'] == trans_data["from_addr"]:
                user['transactions'].append(trans_data)
                user_added=True
        
        if not user_added:
            self.users.append(self.new_user(trans_data))


class Filechain:
    def __init__(self):
        self.users = set()
        self.files = []
        self.chain = []
        self.private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        )
        self.publick_key = self.private_key.public_key()
        

    def add_trans(self, trans_data):
        self.users.add(trans_data["to_addr"])
        messagejson = trans_data["message"]
        post = json.loads(messagejson)
        file_hash = post['hash']
        try:
            index = self.files.index(file_hash)
            self.chain[index].add_trans(trans_data)
        except Exception as e:
            # files is not include file_hash
            self.files.append(file_hash)
            self.chain.append(Fileblock(trans_data))
