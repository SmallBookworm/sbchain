from cgi import print_arguments
from email import message
import myrsa

if __name__ =="__main__":
    private_key=myrsa.load_private_key("E:\sbchain\private_key.pem")
    public_key=myrsa.load_publick_key("E:\sbchain\publick_key.pem")
    message="asdfdsvczxvbcjkl;uorefds"
    enmes=myrsa.encrypt(message,public_key)
    print(enmes)
    demes=myrsa.decrypt(enmes,private_key)
    print(demes)
    print("sign")
    sign=myrsa.sign_msg(message,private_key)
    print(sign)
    res=myrsa.validate_signature(public_key,sign,message)
    print(res)
    print(myrsa.validate_signature(public_key,b'fasdfagfsdgfdgdfgdsg==',message))
