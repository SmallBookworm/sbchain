import ipfshttpclient


def ipfs_add(filepath):
    # Share TCP connections using a context manager
    with ipfshttpclient.connect() as client:
        ipfsfile = client.add(filepath)
        return ipfsfile['Hash']

def ipfs_get(cid,filepath):
    # Share TCP connections using a context manager
    with ipfshttpclient.connect() as client:
        ipfsfile = client.get(cid,filepath)
        return ipfsfile