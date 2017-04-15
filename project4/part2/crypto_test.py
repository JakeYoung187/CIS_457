from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key

pub_data = open('RSApub.pem','r').read()
priv_data = open('RSApriv.pem','r').read()
pub_key = load_pem_public_key(pub_data, backend=default_backend())
priv_key = load_pem_private_key(priv_data, password=None, backend=default_backend())

print pub_key, priv_key


message = b"encrypted data"
ciphertext = pub_key.encrypt(
		message,
		padding.OAEP(
			mgf=padding.MGF1(algorithm=hashes.SHA1()),
			algorithm=hashes.SHA1(),
			label=None
		)
	)

plaintext = priv_key.decrypt(
		ciphertext,
		padding.OAEP(
			mgf=padding.MGF1(algorithm=hashes.SHA1()),
			algorithm=hashes.SHA1(),
			label=None
		)
)
print plaintext

from cryptography.fernet import Fernet
key = Fernet.generate_key()
f = Fernet(key)
token = f.encrypt(b"my deep dark secret")
print token
print f.decrypt(token)
#'my deep dark secret'

