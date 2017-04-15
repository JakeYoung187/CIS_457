from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import dsa, rsa
from cryptography.hazmat.primitives.serialization import *

#der_data = 'RSApriv.der'

#key = load_der_private_key(der_data, password=None, backend=default_backend())
#print isinstance(key, rsa.RSAPrivateKey)

#pem_data = 'RSApriv.pem'


'''
key = load_pem_private_key(pem_data, password=None, backend=default_backend())
if isinstance(key, rsa.RSAPrivateKey):
	signature = sign_with_rsa_key(key, message)
elif isinstance(key, dsa.DSAPrivateKey):
	signature = sign_with_dsa_key(key, message)
else:
	raise TypeError
'''
